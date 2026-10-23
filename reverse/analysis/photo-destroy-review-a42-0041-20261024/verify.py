"""Independent sparse RV32/RVC review; reads ROM, never executes target."""
from pathlib import Path
import json

OUT = Path(__file__).resolve().parent
TREE = OUT.parents[2]
ROM = Path('D:/Documents/PlatformIO/Projects/cuktech-ap01-firmware/roms/0041/ap01-1.0.2_0041.bin')
BASE = 0x9ffff000
checks = []

def sx(n, bits):
    return n - (1 << bits) if n & (1 << (bits - 1)) else n

def read(pc, size=4):
    with ROM.open('rb') as f:
        f.seek(pc - BASE)
        raw = f.read(size)
    assert len(raw) == size
    return int.from_bytes(raw, 'little'), raw.hex()

def check(pc, kind, actual, expected, size=4):
    assert actual == expected, (hex(pc), kind, actual, expected)
    checks.append(dict(pc=hex(pc), raw=read(pc, size)[1], kind=kind, decoded=actual))

def load(pc, rd, base, offset, funct3):
    w, _ = read(pc)
    check(pc, 'I load [opcode, width, rd, rs1, signed_offset]',
          [w & 127, w >> 12 & 7, w >> 7 & 31, w >> 15 & 31, sx(w >> 20, 12)],
          [3, funct3, rd, base, offset])

def mv(pc, rd, rs):
    c, _ = read(pc, 2)
    check(pc, 'C.MV [quadrant, funct4, rd, rs2]',
          [c & 3, c >> 12, c >> 7 & 31, c >> 2 & 31], [2, 8, rd, rs], 2)

def jal(pc, target):
    w, _ = read(pc)
    imm = ((w >> 31) << 20) | ((w >> 12 & 255) << 12) | ((w >> 20 & 1) << 11) | ((w >> 21 & 1023) << 1)
    check(pc, 'JAL [opcode, rd, target]', [w & 127, w >> 7 & 31, pc + sx(imm, 21)], [111, 1, target])

load(0xa00ed802, 18, 10, 0x5c, 2)  # old O saved before calls
mv(0xa00ed806, 9, 10)             # owner -> s1
mv(0xa00ed808, 19, 11)            # new source -> s3
w, _ = read(0xa00ed80a)
imm = ((w >> 31) << 12) | ((w >> 7 & 1) << 11) | ((w >> 25 & 63) << 5) | ((w >> 8 & 15) << 1)
check(0xa00ed80a, 'BEQ [opcode, funct3, rs1, rs2, target]',
      [w & 127, w >> 12 & 7, w >> 15 & 31, w >> 20 & 31, 0xa00ed80a + sx(imm, 13)],
      [99, 0, 18, 0, 0xa00ed830])
jal(0xa00ed80e, 0xa00eaa50)
jal(0xa00ed812, 0xa00890e8)
load(0xa00ed816, 15, 18, 0x10, 4)  # LBU, not bit test
c, _ = read(0xa00ed81a, 2)
imm = ((c >> 12 & 1) << 8) | ((c >> 10 & 3) << 3) | ((c >> 5 & 3) << 6) | ((c >> 3 & 3) << 1) | ((c >> 2 & 1) << 5)
check(0xa00ed81a, 'C.BEQZ [quadrant, funct3, rs1, target]',
      [c & 3, c >> 13, (c >> 7 & 7) + 8, 0xa00ed81a + sx(imm, 9)], [1, 6, 15, 0xa00ed822], 2)
mv(0xa00ed81c, 10, 18)
jal(0xa00ed81e, 0xa01b2e3a)       # excluded callee, target only
mv(0xa00ed822, 10, 18)            # free arg is saved O
jal(0xa00ed824, 0xa008ab8a)
for pc, offset in [(0xa00ed828, 0x5c), (0xa00ed82c, 0x74)]:
    w, _ = read(pc)
    check(pc, 'SW [opcode, width, rs1, rs2, signed_offset]',
          [w & 127, w >> 12 & 7, w >> 15 & 31, w >> 20 & 31, sx((w >> 25 << 5) | (w >> 7 & 31), 12)],
          [35, 2, 9, 0, offset])
mv(0xa00ed830, 10, 19)
jal(0xa00ed832, 0xa00dd454)       # new source classification after clears

# Compare only retained A41 instruction anchors, without running/importing its script.
old = json.loads((TREE/'reverse/analysis/photo-decoder-destroy-a41-0041-20261024/evidence.json').read_text(encoding='utf8'))
by_pc = {r['pc']: r['raw'] for r in old['rows']}
matches = sum(1 for item in checks if item['pc'] in by_pc and item['raw'] == by_pc[item['pc']])
assert matches == 14
result = dict(status='PASS', baseline='d493236', static_only=True, checks=checks,
              a41_anchor_matches=matches, new_functionality=0,
              inherited='A33/A35 source ABI; A37/A39 allocation and borrowed input; A29/A31 invalidation; C03/C04 free wrapper',
              unknown='nonzero mode callee internals, page DELETE trigger, heap internals/runtime outcome')
(OUT/'review-evidence.json').write_text(json.dumps(result, ensure_ascii=False, indent=2)+'\n', encoding='utf8')
print(json.dumps(dict(status='PASS', checks=len(checks), a41_anchor_matches=matches, new_functionality=0)))
