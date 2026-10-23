"""A10 independent bounded ROM review; never executes target instructions."""
import json
from pathlib import Path
import capstone

HERE = Path(__file__).resolve().parent
TREE = HERE.parents[2]
ROOT = Path('D:/Documents/PlatformIO/Projects/cuktech-ap01-firmware')
ROM = ROOT / 'roms/0041/ap01-1.0.2_0041.bin'
BASE = 0x9ffff000
raw = ROM.read_bytes()
prior = json.loads((TREE / 'reverse/analysis/thread-adapter-a09-0041-20261023/instruction-evidence.json').read_text(encoding='utf8'))
checks = []

def read(pc, size=4):
    return int.from_bytes(raw[pc-BASE:pc-BASE+size], 'little')

def sx(value, bits):
    return value - (1 << bits) if value & (1 << (bits-1)) else value

def check(pc, label, actual, expected):
    assert actual == expected, (hex(pc), label, actual, expected)
    checks.append(dict(pc=hex(pc), label=label, actual=actual, expected=expected))

def load(pc, rd, rs, imm, funct3=2):
    w = read(pc)
    check(pc, 'I-load opcode/width/base/destination/offset',
          [w & 127, (w >> 12) & 7, (w >> 15) & 31, (w >> 7) & 31, sx(w >> 20, 12)],
          [3, funct3, rs, rd, imm])

def store(pc, rs, base, imm):
    w = read(pc)
    check(pc, 'S-store opcode/width/base/source/offset',
          [w & 127, (w >> 12) & 7, (w >> 15) & 31, (w >> 20) & 31,
           sx(((w >> 25) << 5) | ((w >> 7) & 31), 12)], [35, 2, base, rs, imm])

def branch(pc, rs1, rs2, fn, target):
    w = read(pc)
    delta = ((w >> 31) << 12) | (((w >> 7) & 1) << 11) | (((w >> 25) & 63) << 5) | (((w >> 8) & 15) << 1)
    check(pc, 'B-opcode/condition/registers/target',
          [w & 127, (w >> 12) & 7, (w >> 15) & 31, (w >> 20) & 31, hex(pc + sx(delta, 13))],
          [99, fn, rs1, rs2, hex(target)])

def cbranch(pc, reg, nonzero, target):
    w = read(pc, 2)
    delta = (((w >> 12) & 1) << 8) | (((w >> 10) & 3) << 3) | (((w >> 5) & 3) << 6) | (((w >> 3) & 3) << 1) | (((w >> 2) & 1) << 5)
    check(pc, 'CB-opcode/register/target',
          [w & 0xe003, ((w >> 7) & 7) + 8, hex(pc + sx(delta, 9))],
          [0xe001 if nonzero else 0xc001, reg, hex(target)])

def cjump(pc, target):
    w = read(pc, 2)
    delta = (((w >> 12) & 1) << 11) | (((w >> 11) & 1) << 4) | (((w >> 9) & 3) << 8) | (((w >> 8) & 1) << 10) | (((w >> 7) & 1) << 6) | (((w >> 6) & 1) << 7) | (((w >> 3) & 7) << 1) | (((w >> 2) & 1) << 5)
    check(pc, 'CJ-opcode/target', [w & 0xe003, hex(pc + sx(delta, 12))], [0xa001, hex(target)])

def cmove(pc, dst, src):
    w = read(pc, 2)
    check(pc, 'CR-move opcode/registers', [w & 0xf003, (w >> 7) & 31, (w >> 2) & 31], [0x8002, dst, src])

def addi(pc, dst, src, imm):
    w = read(pc)
    check(pc, 'ADDI fields', [w & 127, (w >> 12) & 7, (w >> 7) & 31, (w >> 15) & 31, sx(w >> 20, 12)], [19, 0, dst, src, imm])

def direct(pc, target, pair=False):
    w = read(pc)
    if pair:
        v = read(pc+4)
        check(pc, 'AUIPC ra / JALR ra,ra', [w & 0xfff, v & 0xfffff], [0x97, 0x80e7])
        actual = pc + sx(w & 0xfffff000, 32) + sx(v >> 20, 12)
    else:
        check(pc, 'JAL destination ra', w & 0xfff, 0xef)
        delta = ((w >> 31) << 20) | (((w >> 12) & 255) << 12) | (((w >> 20) & 1) << 11) | (((w >> 21) & 1023) << 1)
        actual = pc + sx(delta, 21)
    check(pc, 'direct target', hex(actual & 0xffffffff), hex(target))

md = capstone.Cs(capstone.CS_ARCH_RISCV, capstone.CS_MODE_RISCV32 | capstone.CS_MODE_RISCVC)
windows = []
for lo, hi in [(0xa012f946, 0xa012f9b0), (0xa0051dac, 0xa0051dd2), (0xa0030ef8, 0xa0031108)]:
    instructions = []
    pc = lo
    old = next(w for w in prior['windows'] if int(w['start'], 16) == lo)
    for previous in old['instructions']:
        assert int(previous['pc'], 16) == pc
        length = 4 if read(pc, 2) & 3 == 3 else 2
        b = raw[pc-BASE:pc-BASE+length]
        assert b.hex() == previous['bytes'], hex(pc)
        ins = next(md.disasm(b, pc, 1), None)
        instructions.append(dict(pc=hex(pc), bytes=b.hex(), asm=(ins.mnemonic+' '+ins.op_str) if ins else None))
        pc += length
    assert pc == hi
    windows.append(dict(start=hex(lo), end_exclusive=hex(hi), a09_bytes_equal=True, instructions=instructions))

check(0xa012f952, 'global LUI a5', read(0xa012f952), 0x62fc77b7)
load(0xa012f956, 9, 15, -1000)
check(0xa012f956, 'computed global address', hex((0x62fc7000-1000) & 0xffffffff), '0x62fc6c18')
load(0xa012f95e, 11, 9, 17, 4)
load(0xa012f962, 15, 9, 16, 4)
branch(0xa012f966, 11, 15, 7, 0xa012f98a)
cmove(0xa012f96a, 10, 9)
direct(0xa012f96c, 0xa0028d1c, True)
branch(0xa012f974, 10, 0, 5, 0xa012f98a)
load(0xa012f98a, 15, 9, 0x130)
cbranch(0xa012f98e, 15, False, 0xa012f994)
w = read(0xa012f990, 2)
check(0xa012f990, 'C.LW width/dest/base/offset', [w & 0xe003, ((w >> 2) & 7)+8, ((w >> 7) & 7)+8, (((w >> 5) & 1) << 6) | (((w >> 10) & 7) << 3) | (((w >> 6) & 1) << 2)], [0x4000, 10, 9, 24])
cbranch(0xa012f992, 10, True, 0xa012f99c)
load(0xa012f99c, 11, 9, 0x134)
for pc in [0xa012f9a0, 0xa0051dcc]:
    check(pc, 'C.JALR a5 encoding (link ra)', read(pc, 2), 0x9782)
for pc, imm in [(0xa012f97a, 128), (0xa012f996, 136), (0xa012f9aa, 146), (0xa0051dbc, 55)]:
    addi(pc, 11, 0, imm)
for pc in [0xa012f978, 0xa012f994, 0xa0051dba]:
    check(pc, 'C.LI a2,0', read(pc, 2), 0x4601)
check(0xa012f95a, 'LUI s2 path base', read(0xa012f95a), 0xa01c0937)
addi(0xa012f97e, 10, 18, 0x598)
direct(0xa012f982, 0xa0019672, True)
cjump(0xa012f99a, 0xa012f97e)
cjump(0xa012f9ae, 0xa012f97e)
check(0xa012f9a2, 'LUI a2 panic base', read(0xa012f9a2), 0xa01bc637)
addi(0xa012f9a6, 12, 12, -0x5d4)
cbranch(0xa0051db4, 10, True, 0xa0051dc8)
check(0xa0051db6, 'LUI a0 path base', read(0xa0051db6), 0xa01c0537)
addi(0xa0051dc0, 10, 10, 0x598)
direct(0xa0051dc4, 0xa0019672)
cmove(0xa0051dc8, 15, 10)
cmove(0xa0051dca, 10, 11)
direct(0xa0051dce, 0xa00306b4)
cmove(0xa0030f1a, 23, 10)
store(0xa0030f1e, 12, 8, -68)
store(0xa0030f22, 13, 8, -72)
load(0xa0030fc0, 15, 8, -68)
store(0xa0030fd2, 15, 23, 20)
load(0xa0030fda, 15, 8, -72)
store(0xa0030ff4, 15, 23, 24)
vendor = [(0xa0030fa2, 0x04c5980b), (0xa0030fa6, 0x44c5c60b), (0xa0030fce, 0x3c0cbc8b), (0xa003103a, 0x44a8c80b), (0xa0031050, 0x44e6430b), (0xa003106a, 0x44e6580b)]
for pc, word in vendor:
    check(pc, 'opaque vendor raw word; no semantic interpretation', hex(read(pc)), hex(word))
strings = []
for pc, expected in [(0xa01c0598, 'pthread/pthread_create.c'), (0xa01bd0e4, 'task/task_setup.c'), (0xa01bba2c, 'panic')]:
    actual = raw[pc-BASE:pc-BASE+150].split(b'\0')[0].decode('ascii')
    check(pc, 'source/diagnostic string', actual, expected)
    strings.append(dict(address=hex(pc), text=actual))
inventory = json.loads((ROOT/'evidence/rea-0041-20261017/evidence/whole-rom-coverage-0041-20261023-initial.json').read_text(encoding='utf8'))
for inherited in prior['inventory']:
    original = next(f for f in inventory['functions'] if f['address'] == inherited['address'])
    check(int(original['address'], 16), 'primary inventory fields equal A09 retained subset',
          {k: original[k] for k in inherited}, inherited)
result = dict(task='A10', base=hex(BASE), rom=str(ROM), capstone=capstone.__version__,
              windows=windows, independent_field_checks=checks, strings=strings,
              inherited_inventory=prior['inventory'],
              verdict='accepted_with_scope_limits',
              limits=['No new function-boundary analysis; inherited Ghidra address-set extents only',
                      'Six vendor words remain uninterpreted; standard encoding fields are not vendor semantics',
                      'No global-object identity or original entry/userdata provenance across unknown words proven',
                      'No target execution, scheduling, diagnostics noreturn or cleanup semantics established'])
(HERE/'review-evidence.json').write_text(json.dumps(result, indent=2)+'\n', encoding='utf8')
print('PASS', len(checks), 'independent field checks; 672 ROM bytes /', sum(len(w['instructions']) for w in windows), 'instruction slots match A09')
