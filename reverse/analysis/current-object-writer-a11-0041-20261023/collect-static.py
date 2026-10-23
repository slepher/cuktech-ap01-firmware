"""A11 bounded static reads; no firmware execution or writable REA session."""
import json
from pathlib import Path
import capstone

HERE = Path(__file__).resolve().parent
ROOT = Path('D:/Documents/PlatformIO/Projects/cuktech-ap01-firmware')
ROM = ROOT / 'roms/0041/ap01-1.0.2_0041.bin'
INV = ROOT / 'evidence/rea-0041-20261017/evidence/whole-rom-coverage-0041-20261023-initial.json'
BASE = 0x9ffff000
raw = ROM.read_bytes()
inventory = json.loads(INV.read_text(encoding='utf8'))
md = capstone.Cs(capstone.CS_ARCH_RISCV, capstone.CS_MODE_RISCV32 | capstone.CS_MODE_RISCVC)
checks = []

def u(pc, size=4):
    return int.from_bytes(raw[pc-BASE:pc-BASE+size], 'little')

def sx(v, n):
    return v - (1 << n) if v & (1 << (n-1)) else v

def ck(pc, label, actual, expected):
    assert actual == expected, (hex(pc), label, actual, expected)
    checks.append(dict(pc=hex(pc), label=label, actual=actual, expected=expected))

def mem(pc, opcode, rd_rs, base, offset, width):
    w = u(pc)
    imm = sx(((w >> 25) << 5) | ((w >> 7) & 31), 12) if opcode == 35 else sx(w >> 20, 12)
    ck(pc, 'memory raw fields', [w & 127, (w >> 12) & 7, (w >> (20 if opcode == 35 else 7)) & 31, (w >> 15) & 31, imm], [opcode, width, rd_rs, base, offset])

def compact_mem(pc, store, reg, base, offset):
    w = u(pc, 2)
    imm = (((w >> 5) & 1) << 6) | (((w >> 10) & 7) << 3) | (((w >> 6) & 1) << 2)
    ck(pc, 'C.SW/C.LW word fields', [w & 0xe003, ((w >> 2) & 7)+8, ((w >> 7) & 7)+8, imm], [0xc000 if store else 0x4000, reg, base, offset])

def branch(pc, r1, r2, fn, target):
    w = u(pc)
    imm = ((w >> 31) << 12) | (((w >> 7) & 1) << 11) | (((w >> 25) & 63) << 5) | (((w >> 8) & 15) << 1)
    ck(pc, 'B raw condition/target', [w & 127, (w >> 12) & 7, (w >> 15) & 31, (w >> 20) & 31, hex(pc+sx(imm, 13))], [99, fn, r1, r2, hex(target)])

def cb(pc, reg, nz, target):
    w = u(pc, 2)
    imm = (((w >> 12) & 1) << 8) | (((w >> 10) & 3) << 3) | (((w >> 5) & 3) << 6) | (((w >> 3) & 3) << 1) | (((w >> 2) & 1) << 5)
    ck(pc, 'CB raw condition/target', [w & 0xe003, ((w >> 7) & 7)+8, hex(pc+sx(imm, 9))], [0xe001 if nz else 0xc001, reg, hex(target)])

def jal(pc, target):
    w = u(pc)
    imm = ((w >> 31) << 20) | (((w >> 12) & 255) << 12) | (((w >> 20) & 1) << 11) | (((w >> 21) & 1023) << 1)
    ck(pc, 'JAL raw rd/target', [w & 0xfff, hex(pc+sx(imm, 21))], [0xef, hex(target)])

windows, selected = [], []
for address in ['0xa00272d4', '0xa0027340']:
    f = next(f for f in inventory['functions'] if f['address'] == address)
    selected.append({k: f[k] for k in ['address', 'inventory_evidence', 'extent', 'direct_calls', 'source_paths', 'families', 'excluded_as_verified_open_source']})
    for rng in f['extent']['body']['ranges']:
        pc, hi = int(rng['start'], 16), int(rng['end'], 16)+1
        rows = []
        while pc < hi:
            n = 4 if u(pc, 2) & 3 == 3 else 2
            b = raw[pc-BASE:pc-BASE+n]
            ins = next(md.disasm(b, pc, 1), None)
            assert ins and ins.size == n, hex(pc)
            rows.append(dict(pc=hex(pc), bytes=b.hex(), asm=ins.mnemonic+' '+ins.op_str))
            pc += n
        assert pc == hi
        windows.append(dict(start=rng['start'], end_exclusive=hex(hi), instructions=rows))

ck(0xa002734c, 'LUI a1 global base', u(0xa002734c), 0x62fc75b7)
mem(0xa0027350, 3, 18, 11, -1000, 2)
ck(0xa0027350, 'computed global slot', hex(0x62fc7000-1000), '0x62fc6c18')
ck(0xa0027354, 'C.MV s1,a0 incoming node', u(0xa0027354, 2), 0x84aa)
mem(0xa0027356, 3, 15, 18, 32, 1)
branch(0xa002735a, 0, 15, 5, 0xa002738a)
mem(0xa002735e, 3, 14, 18, 16, 4)
mem(0xa0027362, 3, 15, 10, 16, 4)
branch(0xa0027366, 14, 15, 7, 0xa002738a)
ck(0xa002738a, 'ADDI a1,a1,-1000', u(0xa002738a), 0xc1858593)
ck(0xa002738e, 'C.MV a0,s1', u(0xa002738e, 2), 0x8526)
jal(0xa0027390, 0xa00272d4)
ck(0xa002736a, 'alternate LUI a1', u(0xa002736a), 0x62fc75b7)
ck(0xa002736e, 'alternate ADDI a1,-1012 (different slot)', u(0xa002736e), 0xc0c58593)
jal(0xa0027372, 0xa00272d4)
mem(0xa00272d4, 3, 14, 10, 16, 4)
cb(0xa00272d8, 14, True, 0xa00272f4)
compact_mem(0xa00272f4, False, 15, 11, 0)
cb(0xa00272f6, 15, False, 0xa002732c)
mem(0xa00272f8, 3, 13, 15, 16, 4)
branch(0xa00272fc, 13, 14, 7, 0xa0027310)
compact_mem(0xa0027300, False, 14, 15, 4)
cb(0xa0027302, 14, True, 0xa0027322)
compact_mem(0xa0027304, True, 15, 10, 0)
mem(0xa0027306, 35, 0, 10, 4, 2)
compact_mem(0xa002730a, True, 10, 15, 4)
compact_mem(0xa002730c, True, 10, 11, 0)
compact_mem(0xa0027310, False, 15, 15, 0)
compact_mem(0xa002732c, False, 15, 11, 4)
cb(0xa002732e, 15, True, 0xa0027314)
mem(0xa0027330, 35, 0, 10, 0, 2)
mem(0xa0027334, 35, 0, 10, 4, 2)
compact_mem(0xa0027338, True, 10, 11, 0)
compact_mem(0xa002733a, True, 10, 11, 4)
for pc, word in [(0xa002731e, 0x4501), (0xa002733c, 0x4505), (0xa0027320, 0x8082), (0xa002733e, 0x8082), (0xa002737c, 0x4501)]:
    ck(pc, 'return value or return encoding', u(pc, 2), word)
sources = [s for s in inventory['source_paths'] if s['text'] in ['sched/sched_addreadytorun.c', 'sched/sched_addprioritized.c']]
out = dict(task='A11', baseline='f712c40483ced6c44df786822dc9c512042f5e3a', rom=str(ROM), inventory_path=str(INV), base=hex(BASE), capstone=capstone.__version__, windows=windows, checks=checks, inventory=selected, source_path_records=sources, limits=['Only two bounded functions; no scheduler execution or global-object identity proven', 'Nonzero entry byte_10 path only; diagnostic returning path does not preserve proven arguments', 'Generic head slot parameter is 62fc6c18 only on identified caller arm', 'No all-ROM writer enumeration; Ghidra function extents inherited'])
(HERE/'instruction-evidence.json').write_text(json.dumps(out, indent=2)+'\n', encoding='utf8')
print('PASS', len(checks), 'raw encoding checks;', sum(len(w['instructions']) for w in windows), 'instructions; 248 bytes; no opaque words')
