"""Independent A39 sparse static field checks; no target execution."""
from pathlib import Path
import json

HERE = Path(__file__).resolve().parent
MAIN = Path('D:/Documents/PlatformIO/Projects/cuktech-ap01-firmware')
ROM = MAIN / 'roms/0041/ap01-1.0.2_0041.bin'
checks = []


def read(a, n=4):
    with ROM.open('rb') as f:
        f.seek(a - 0x9ffff000)
        b = f.read(n)
    assert len(b) == n
    return int.from_bytes(b, 'little')


def sx(v, n):
    return (v ^ (1 << (n - 1))) - (1 << (n - 1))


def check(a, claim, actual, expected, n=4):
    assert actual == expected, (hex(a), claim, actual, expected)
    checks.append(dict(pc=hex(a), raw=read(a, n).to_bytes(n, 'little').hex(),
                       claim=claim, decoded=actual))


def iop(a, op, f3, rd, rs1, imm):
    w = read(a)
    check(a, 'I opcode/f3/rd/rs1/signed immediate',
          [w & 127, (w >> 12) & 7, (w >> 7) & 31, (w >> 15) & 31, sx(w >> 20, 12)],
          [op, f3, rd, rs1, imm])


def store(a, f3, rs2, rs1, imm):
    w = read(a)
    check(a, 'S opcode/width/source/base/signed offset',
          [w & 127, (w >> 12) & 7, (w >> 20) & 31, (w >> 15) & 31,
           sx(((w >> 25) << 5) | ((w >> 7) & 31), 12)], [35, f3, rs2, rs1, imm])


def compact(a, raw, claim):
    check(a, claim, read(a, 2), raw, 2)


def csw(a, rs2, rs1, off):
    w = read(a, 2)
    check(a, 'C.SW width32/source/base/offset',
          [w & 3, w >> 13, 8 + ((w >> 2) & 7), 8 + ((w >> 7) & 7),
           ((w >> 5) & 1) * 64 + ((w >> 10) & 7) * 8 + ((w >> 6) & 1) * 4],
          [0, 6, rs2, rs1, off], 2)


def jal(a, target):
    w = read(a)
    imm = ((w >> 31) << 20) | (((w >> 12) & 255) << 12) | (((w >> 20) & 1) << 11) | (((w >> 21) & 1023) << 1)
    check(a, 'JAL ra absolute target', [w & 127, (w >> 7) & 31, (a + sx(imm, 21)) & 0xffffffff],
          [111, 1, target])


def branch(a, f3, rs1, rs2, target):
    w = read(a)
    imm = ((w >> 31) << 12) | (((w >> 7) & 1) << 11) | (((w >> 25) & 63) << 5) | (((w >> 8) & 15) << 1)
    check(a, 'branch opcode/f3/rs1/rs2/target',
          [w & 127, (w >> 12) & 7, (w >> 15) & 31, (w >> 20) & 31, a + sx(imm, 13)],
          [99, f3, rs1, rs2, target])


compact(0xa010a678, 0x892a, 'C.MV s2,a0: preserve W')
check(0xa010a79e, 'RV32 MUL rd/rs1/rs2/f7/f3/opcode',
      [(read(0xa010a79e) >> 7) & 31, (read(0xa010a79e) >> 15) & 31,
       (read(0xa010a79e) >> 20) & 31, read(0xa010a79e) >> 25,
       (read(0xa010a79e) >> 12) & 7, read(0xa010a79e) & 127], [21, 23, 22, 1, 0, 51])
compact(0xa010a7a2, 0x6511, 'C.LUI a0,4: 0x4000')
compact(0xa010a7a4, 0x4795, 'C.LI a5,5')
iop(0xa010a7a6, 19, 0, 10, 10, 0x664)
for a, expected in [(0xa010a7aa, [11, 1, 16, 10, 21, 15]),
                    (0xa010a814, [11, 1, 2, 10, 10, 21])]:
    w = read(a)
    check(a, 'vendor opcode/f3/f7/rd/rs1/rs2',
          [w & 127, (w >> 12) & 7, w >> 25, (w >> 7) & 31, (w >> 15) & 31, (w >> 20) & 31], expected)
check(0xa010a814, 'ADDsl shift bits26:25', (read(0xa010a814) >> 25) & 3, 2)
model = MAIN / 'evidence/rea-0041-20261017/ghidra/Ghidra/Processors/RISCV/data/languages/ap01thead2.sinc'
text = model.read_text()
rules = []
for name, semantic in [(':th.mula ', 'rd = rd + (rs1 * rs2);'),
                       (':th.addsl ', 'rd = rs1 + (rs2 << thshift);')]:
    start = text.index(name)
    rule = text[start:text.index('\n}', start) + 2]
    assert semantic in rule
    rules.append(rule)
jal(0xa010a7ae, 0xa008aea0)
compact(0xa010a7b2, 0x84aa, 'C.MV s1,a0: O')
branch(0xa010a7b4, 0, 10, 0, 0xa010a6b4)
iop(0xa010a7b8, 19, 0, 12, 0, 0x664)
compact(0xa010a7bc, 0x85ca, 'C.MV a1,s2: W')
w, v = read(0xa010a7be), read(0xa010a7c2)
check(0xa010a7be, 'AUIPC ra + JALR ra,ra: copy target',
      [w & 127, (w >> 7) & 31, v & 127, (v >> 7) & 31, (v >> 15) & 31,
       (0xa010a7be + sx(w & 0xfffff000, 32) + sx(v >> 20, 12)) & 0xfffffffe],
      [23, 1, 103, 1, 1, 0xa000589c])
store(0xa00059ec, 2, 17, 15, 12)
iop(0xa00059e8, 3, 2, 17, 11, 12)
store(0xa010a7e8, 1, 23, 9, 0x1c)
store(0xa010a7ec, 1, 22, 9, 0x1e)
iop(0xa010a80a, 19, 0, 10, 9, 0x664)
iop(0xa010a80e, 19, 0, 15, 9, 0x600)
csw(0xa010a812, 10, 15, 0x58)
csw(0xa010a818, 10, 15, 0x5c)
iop(0xa010a838, 3, 2, 15, 9, 0x65c)
compact(0xa010a83e, 0x9abe, 'C.ADD s5,a5: N+region65c')
store(0xa010a840, 2, 21, 9, 0x660)
compact(0xa010a880, 0x8526, 'C.MV a0,s1: return O before s1 restore')
compact(0xa010a882, 0x54d2, 'C.LWSP s1,0x34(sp)')
compact(0xa010a886, 0x8082, 'C.JR ra constructor return')
jal(0xa0107e1e, 0xa010a65a)
for a, rd, off in [(0xa0107e22, 1, 0x67c), (0xa0107e26, 8, 0x678), (0xa0107e2a, 9, 0x674)]:
    iop(a, 3, 2, rd, 2, off)
iop(0xa0107e2e, 19, 0, 2, 2, 0x680)
compact(0xa0107e32, 0x8082, 'C.JR ra: no a0 clobber in wrapper epilogue')
jal(0xa00ed83c, 0xa0107dea)
compact(0xa00ed840, 0x892a, 'C.MV s2,a0: returned O')
branch(0xa00ed842, 1, 18, 0, 0xa00ed884)
store(0xa00ed884, 2, 18, 9, 0x5c)
iop(0xa00ed888, 3, 2, 15, 18, 0x658)
csw(0xa00ed88c, 15, 9, 0x74)
result = dict(status='PASS', static_only=True, baseline='db28e9987da77c12ae83b1167d69a537215edf50',
              checks=checks, local_vendor_rules=rules, new_functionality=0,
              limits='Sparse independent review; source ABI/copy interface inherited. No full decoder export, resource execution, teardown or format/version certification.')
(HERE / 'review-evidence.json').write_text(json.dumps(result, ensure_ascii=False, indent=2) + '\n', encoding='utf8')
print(json.dumps(dict(status='PASS', checks=len(checks), vendor_rules=len(rules))))
