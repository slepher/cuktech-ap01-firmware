"""A01: bounded static call-site evidence, no execution of ROM instructions.

Usage: python collect-static.py ABSOLUTE_ROM_PATH
Writes only alongside this script. Capstone is used for decoding, never emulation.
"""
import json
import sys
from collections import Counter
from pathlib import Path
from capstone import Cs, CS_ARCH_RISCV, CS_MODE_RISCV32, CS_MODE_RISCVC

HERE = Path(__file__).resolve().parent
TREE = HERE.parents[1]
BASE = 0x9ffff000
ROM = Path(sys.argv[1])
raw = ROM.read_bytes()
md = Cs(CS_ARCH_RISCV, CS_MODE_RISCV32 | CS_MODE_RISCVC)
md.detail = True
targets = {0xa0028b0a: 'sem_wait wrapper', 0xa002786c: 'wait wrapper direct delegate',
           0xa002747c: 'sem_post', 0xa0026a32: 'sem_destroy',
           0xa009ef48: 'buzzer worker', 0xa0052fee: 'thread creation wrapper'}

def signed(n, bits):
    return n - (1 << bits) if n & (1 << (bits - 1)) else n

def record(pc):
    i = next(md.disasm(raw[pc-BASE:pc-BASE+4], pc, count=1), None)
    if i is None:
        h = int.from_bytes(raw[pc-BASE:pc-BASE+2], 'little')
        width = 4 if h & 3 == 3 else 2
        return {'address': hex(pc), 'bytes': raw[pc-BASE:pc-BASE+width].hex(), 'decode': 'unknown'}
    return {'address': hex(pc), 'bytes': bytes(i.bytes).hex(),
            'decode': i.mnemonic+' '+i.op_str}

calls = []
for off in range(0, len(raw)-1, 2):
    pc = BASE+off
    h = int.from_bytes(raw[off:off+2], 'little')
    w = int.from_bytes(raw[off:off+4], 'little')
    dest = None
    form = None
    if off+4 <= len(raw) and w & 0x7f == 0x6f and (w >> 7) & 31 == 1:
        imm = ((w >> 31) << 20) | (((w >> 12) & 255) << 12) | (((w >> 20) & 1) << 11) | (((w >> 21) & 1023) << 1)
        dest = (pc + signed(imm, 21)) & 0xffffffff
        form = 'JAL ra'
    elif h & 0xe003 == 0x2001:  # RV32 compressed JAL
        imm = (((h >> 12)&1)<<11) | (((h >> 11)&1)<<4) | (((h >> 9)&3)<<8) | (((h >> 8)&1)<<10) | (((h >> 7)&1)<<6) | (((h >> 6)&1)<<7) | (((h >> 3)&7)<<1) | (((h >> 2)&1)<<5)
        dest = (pc + signed(imm, 12)) & 0xffffffff
        form = 'C.JAL'
    elif off+8 <= len(raw) and w & 0x7f == 0x17:
        w2 = int.from_bytes(raw[off+4:off+8], 'little')
        rd = (w >> 7) & 31
        if w2 & 0x707f == 0x67 and ((w2 >> 7)&31) == 1 and ((w2 >> 15)&31) == rd:
            dest = (pc + (w & 0xfffff000) + signed(w2 >> 20, 12)) & 0xfffffffe
            form = 'AUIPC/JALR ra'
    if dest not in targets:
        continue
    call_pc = pc+4 if form == 'AUIPC/JALR ra' else pc
    decoded_call = next(md.disasm(raw[call_pc-BASE:call_pc-BASE+4], call_pc, count=1))
    if form == 'AUIPC/JALR ra':
        decoded_upper = next(md.disasm(raw[off:off+4], pc, count=1))
        checked_dest = (pc + (decoded_upper.operands[-1].imm << 12) + decoded_call.operands[-1].imm) & 0xfffffffe
    else:
        checked_dest = (call_pc + decoded_call.operands[-1].imm) & 0xffffffff
    assert checked_dest == dest, hex(call_pc)
    # Arbitrary even window starts are navigation aids, not a trusted CFG.
    # Retain every instruction, with unknown 16/32-bit words explicit.
    window = []
    q = max(BASE, pc-128)
    while q <= call_pc:
        r = record(q)
        window.append(r)
        q += len(bytes.fromhex(r['bytes']))
    calls.append({'start': hex(pc), 'call_address': hex(call_pc), 'target': hex(dest),
                  'target_role': targets[dest], 'form': form, 'window': window})

out = {'scope': 'All even ROM offsets; direct JAL ra/C.JAL and contiguous AUIPC/JALR ra pairs only',
       'limitations': ['Includes non-code and overlapping-instruction candidates; code boundaries require existing evidence',
                       'Does not cover noncontiguous AUIPC/JALR, register-indirect calls, tail calls, RAM code, memory aliases, or arbitrary wait APIs',
                       '128-byte windows are navigation aids; no inferred argument-value or whole-ROM absence proof'],
       'counts': dict(Counter(x['target'] for x in calls)), 'calls': calls}
(HERE/'direct-call-candidates.json').write_text(json.dumps(out, indent=2)+'\n', encoding='utf8')

# Core evidence is taken from the retained repaired profile, checked byte-for-byte.
prior = json.loads((TREE/'analysis/buzzer-backlight-0041-20261023.json').read_text(encoding='utf8'))
windows = []
for addr, lo, hi, title in [('0xa009ef48', 0xa009ef48, 0xa009f177, 'worker full body'),
                           ('0xa005a736', 0xa005bc6c, 0xa005bdc9, 'init success/failure window'),
                           ('0xa005a736', 0xa005c27c, 0xa005c3af, 'same container stack-loaded wait argument')]:
    f = next(x for x in prior['functions'] if x['address'] == addr)
    containing = next(r for r in f['raw_ranges'] if int(r['start'],16)<=lo and int(r['end'],16)>=hi)
    saved = bytes.fromhex(containing['hex'])
    piece = saved[lo-int(containing['start'],16):hi-int(containing['start'],16)+1]
    assert piece == raw[lo-BASE:hi-BASE+1], title
    windows.append({'title': title, 'function_entry': addr, 'start': hex(lo), 'end': hex(hi),
                    'evidence_id': f['evidence_id'], 'source': f['source'], 'raw_bytes_match_rom': True,
                    'bytes': piece.hex(), 'assembly': [s for s in f['assembly'] if lo<=int(s.split(':')[0],16)<=hi]})
lo, hi = 0xa0028b0a, 0xa0028b3d
instructions = list(md.disasm(raw[lo-BASE:hi-BASE+1], lo))
assert instructions and instructions[-1].address+instructions[-1].size == hi+1
windows.append({'title': 'sem_wait wrapper complete return-delimited window', 'function_entry': hex(lo),
                'start': hex(lo), 'end': hex(hi), 'bytes': raw[lo-BASE:hi-BASE+1].hex(),
                'assembly': [record(i.address) for i in instructions]})
(HERE/'core-windows.json').write_text(json.dumps({'windows': windows}, indent=2)+'\n', encoding='utf8')
print(json.dumps({'candidate_counts':out['counts'], 'core_windows':len(windows), 'retained_raw_windows_match':True}))
