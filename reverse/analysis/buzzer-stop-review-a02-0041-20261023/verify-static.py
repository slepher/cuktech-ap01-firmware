"""A02 independent static review; reads ROM, writes only this task directory."""
import json
import struct
from pathlib import Path
from collections import Counter
from capstone import Cs, CS_ARCH_RISCV, CS_MODE_RISCV32, CS_MODE_RISCVC

HERE = Path(__file__).resolve().parent
OLD = HERE.parent / 'buzzer-stop-a01-0041-20261023'
ROM = Path('D:/Documents/PlatformIO/Projects/cuktech-ap01-firmware/roms/0041/ap01-1.0.2_0041.bin')
raw = ROM.read_bytes()
BASE = 0x9ffff000
md = Cs(CS_ARCH_RISCV, CS_MODE_RISCV32 | CS_MODE_RISCVC)
md.detail = True
def sext(n, bits):
    return (n ^ (1 << (bits-1))) - (1 << (bits-1))
def decode(lo, hi):
    result = []
    while lo < hi:
        b = raw[lo-BASE:lo-BASE+4]
        i = next(md.disasm(b, lo, 1), None)
        size = i.size if i else (4 if b[0] & 3 == 3 else 2)
        result.append({'pc': hex(lo), 'bytes': b[:size].hex(),
                       'asm': i.mnemonic+' '+i.op_str if i else 'unknown; no semantics assigned'})
        lo += size
    assert lo == hi
    return result

core = json.loads((OLD/'core-windows.json').read_text())
checks = []
for w in core['windows']:
    lo, hi = int(w['start'],16), int(w['end'],16)+1
    assert bytes.fromhex(w['bytes']) == raw[lo-BASE:hi-BASE]
    checks.append({'title':w['title'], 'start':w['start'], 'end':w['end'], 'bytes_equal_rom':True,
                   'independent_decode':decode(lo,hi)})

prior = json.loads((OLD/'direct-call-candidates.json').read_text())
targets = {int(c['target'],16) for c in prior['calls']} | {0xa009ef48}
found = []
for off in range(0,len(raw)-1,2):
    pc = BASE+off
    h = struct.unpack_from('<H',raw,off)[0]
    w = int.from_bytes(raw[off:off+4], 'little')
    w2 = int.from_bytes(raw[off+4:off+8], 'little')
    dest = None
    if off+4 <= len(raw) and w & 0xfff == 0xef:
        imm = ((w>>21 & 1023)<<1) + ((w>>20 & 1)<<11) + ((w>>12 & 255)<<12) + ((w>>31)<<20)
        dest, form, call = (pc+sext(imm,21))&0xffffffff, 'JAL ra', pc
    elif h & 0xe003 == 0x2001:
        # Destination-bit -> source-bit mapping from the C.J immediate layout.
        pairs = [(1,3),(2,4),(3,5),(4,11),(5,2),(6,7),(7,6),(8,9),(9,10),(10,8),(11,12)]
        imm = sum(((h>>source)&1)<<bit for bit,source in pairs)
        dest, form, call = (pc+sext(imm,12))&0xffffffff, 'C.JAL', pc
    elif off+8 <= len(raw) and w & 127 == 23 and w2 & 0x707f == 0x67 and (w2>>7)&31 == 1 and (w2>>15)&31 == (w>>7)&31:
        dest, form, call = (pc+sext(w&0xfffff000,32)+sext(w2>>20,12))&0xfffffffe, 'AUIPC/JALR ra', pc+4
    if dest in targets:
        if form == 'AUIPC/JALR ra':
            assert (w >> 7) & 31 != 0
        found.append((hex(pc),hex(call),hex(dest),form))
expected = [(c['start'],c['call_address'],c['target'],c['form']) for c in prior['calls']]
assert found == expected
review_ranges = [(0xa00b8bfc,0xa00b8c3a),(0xa01361f8,0xa013620c),
                 (0xa019919e,0xa01991ce),(0xa01991ce,0xa0199238),
                 (0xa01b3244,0xa01b3256),(0xa01b7d66,0xa01b7d78),
                 (0xa0028b3e,0xa0028b46)]
out = {'task':'A02', 'method':'Static byte comparison and independent immediate extraction; Capstone ordinary-instruction decode; no target execution',
       'core_windows':checks,'candidate_count':len(found),'counts':dict(Counter(c[2] for c in found)),
       'candidate_tuple_match':True,'candidates':[{'start':a,'call':b,'target':c,'form':d} for a,b,c,d in found],
       'parameter_windows':[{'start':hex(lo),'end_exclusive':hex(hi),'instructions':decode(lo,hi)} for lo,hi in review_ranges],
       'limits':['Even-offset encoding candidates do not certify code boundaries or CFG edges.',
                 'No memory alias, register-indirect, tail-call, noncontiguous pair, other API or RAM-code exclusion.',
                 'Unknown vendor instructions are retained without assigning semantics.']}
(HERE/'verification.json').write_text(json.dumps(out,indent=2)+'\n',encoding='utf8')
print(json.dumps({'core_windows_bytes_equal_rom':len(checks),'candidate_tuple_match':True,'counts':out['counts']}))
