"""A35 independent sparse raw-field review. Does not execute firmware."""
import json
from pathlib import Path

HERE = Path(__file__).resolve().parent
MAIN = Path('D:/Documents/PlatformIO/Projects/cuktech-ap01-firmware')
ROM = MAIN / 'roms/0041/ap01-1.0.2_0041.bin'
BASE = 0x9ffff000
checks = []


def sx(v, n):
    return (v ^ (1 << (n - 1))) - (1 << (n - 1))


def word(a, n=4):
    with ROM.open('rb') as f:
        f.seek(a - BASE)
        b = f.read(n)
    assert len(b) == n
    return int.from_bytes(b, 'little')


def check(a, claim, actual, expected, n=4):
    assert actual == expected, (hex(a), claim, actual, expected)
    checks.append(dict(address=hex(a), raw=word(a, n).to_bytes(n, 'little').hex(),
                       claim=claim, decoded=actual))


def iop(a, op, width, rd, rs, offset):
    w = word(a)
    check(a, 'I opcode/width/dest/base/signed-offset',
          [w & 127, (w >> 12) & 7, (w >> 7) & 31, (w >> 15) & 31, sx(w >> 20, 12)],
          [op, width, rd, rs, offset])


def store(a, width, rs, base, offset):
    w = word(a)
    check(a, 'store opcode/width/source/base/signed-offset',
          [w & 127, (w >> 12) & 7, (w >> 20) & 31, (w >> 15) & 31,
           sx(((w >> 25) << 5) | ((w >> 7) & 31), 12)],
          [35, width, rs, base, offset])


def clw(a, rd, base, offset):
    w = word(a, 2)
    check(a, 'C.LW dest/base/unsigned-offset',
          [w & 3, w >> 13, 8 + ((w >> 2) & 7), 8 + ((w >> 7) & 7),
           (((w >> 5) & 1) << 6) | (((w >> 10) & 7) << 3) | (((w >> 6) & 1) << 2)],
          [0, 2, rd, base, offset], 2)


def cmv(a, rd, rs):
    w = word(a, 2)
    check(a, 'C.MV dest/source', [w & 3, w >> 12, (w >> 7) & 31, (w >> 2) & 31],
          [2, 8, rd, rs], 2)


def branch(a, f3, rs1, rs2, target):
    w = word(a)
    imm = ((w >> 31) << 12) | (((w >> 7) & 1) << 11) | (((w >> 25) & 63) << 5) | (((w >> 8) & 15) << 1)
    check(a, 'branch comparison/registers/target',
          [w & 127, (w >> 12) & 7, (w >> 15) & 31, (w >> 20) & 31, a + sx(imm, 13)],
          [99, f3, rs1, rs2, target])


def jal(a, target):
    w = word(a)
    imm = ((w >> 31) << 20) | (((w >> 12) & 255) << 12) | (((w >> 20) & 1) << 11) | (((w >> 21) & 1023) << 1)
    check(a, 'JAL ra target', [w & 127, (w >> 7) & 31, (a + sx(imm, 21)) & 0xffffffff], [111, 1, target])


clw(0xa00b17f2, 15, 10, 0x10)
clw(0xa00b17f4, 9, 15, 4)
iop(0xa00b17f8, 3, 2, 16, 9, 12)
check(0xa00b17f6, 'C.LI a5,4', word(0xa00b17f6, 2), 0x4791, 2)
check(0xa00b17fc, 'C.ADDI a6,1 (RV32 wrap)', word(0xa00b17fc, 2), 0x0805, 2)
branch(0xa00b17fe, 7, 15, 16, 0xa00b1804)
check(0xa00b1802, 'C.LI a6,0', word(0xa00b1802, 2), 0x4801, 2)
w = word(0xa00b1804)
check(0xa00b1804, 'LUI a5 upper table base', [w & 127, (w >> 7) & 31, w & 0xfffff000], [55, 15, 0xa0560000])
iop(0xa00b1808, 19, 0, 15, 15, -0x1bc)
assert (word(0xa00b1804) & 0xfffff000) - 0x1bc == 0xa055fe44
w = word(0xa00b180c)
check(0xa00b180c, 'th.lrw opcode/f3/op2731/rd/rs1/rs2/shift',
      [w & 127, (w >> 12) & 7, w >> 27, (w >> 7) & 31, (w >> 15) & 31, (w >> 20) & 31, (w >> 25) & 3],
      [11, 4, 8, 11, 15, 16, 2])
clw(0xa00b1810, 10, 9, 0)
store(0xa00b1812, 2, 16, 8, -0x144)
jal(0xa00b1816, 0xa00ed7f4)
iop(0xa00b181a, 3, 2, 16, 8, -0x144)
store(0xa00b1824, 2, 16, 9, 12)
cmv(0xa00ed808, 19, 11)
cmv(0xa00ed830, 10, 19)
jal(0xa00ed832, 0xa00dd454)
check(0xa00ed836, 'C.BNEZ a0,+0x40 skips class0 handoff', word(0xa00ed836, 2), 0xe121, 2)
iop(0xa00ed838, 3, 2, 10, 19, 0x10)
jal(0xa00ed83c, 0xa0107dea)
cmv(0xa00ed840, 18, 10)
branch(0xa00ed842, 1, 18, 0, 0xa00ed884)
cmv(0xa0107dfe, 9, 10)
iop(0xa0107e00, 19, 0, 12, 0, 0x664)
check(0xa0107e04, 'C.LI a1,0', word(0xa0107e04, 2), 0x4581, 2)
iop(0xa0107e06, 19, 0, 10, 8, -0x674)
jal(0xa0107e0a, 0xa0024906)
iop(0xa0107e0e, 19, 0, 10, 8, -0x674)
store(0xa0107e12, 2, 9, 8, -0x668)
store(0xa0107e16, 2, 0, 8, -0x660)
store(0xa0107e1a, 0, 0, 8, -0x664)
jal(0xa0107e1e, 0xa010a65a)
assert -0x668 - (-0x674) == 12

model = MAIN / 'evidence/rea-0041-20261017/ghidra/Ghidra/Processors/RISCV/data/languages/ap01thead2.sinc'
text = model.read_text()
start = text.index(':th.lrw ')
rule = text[start:text.index('\n}', start) + 2]
assert 'op2731=8' in rule and 'rs2 << thshift' in rule and '*[ram]:4 ea' in rule
assert 'rd = value;' in rule and 'thbase = updated' not in rule

result = dict(status='PASS', baseline='f2c1458', static_only=True, checks=checks,
              vendor_rule_path=str(model), vendor_rule=rule,
              conclusion='Accept A33 bounded new-source ABI and borrowed-pointer handoff; new functionality 0.',
              unreviewed='No resource table re-extraction, no a010a65a internal copy/persistence or runtime page timing.')
(HERE / 'review-evidence.json').write_text(json.dumps(result, ensure_ascii=False, indent=2) + '\n', encoding='utf8')
print(json.dumps(dict(status='PASS', sparse_checks=len(checks), new_functionality=0)))
