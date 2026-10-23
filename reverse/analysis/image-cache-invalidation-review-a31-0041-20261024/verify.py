"""A31 independent sparse, static review; reads the original ROM only."""
import json
from pathlib import Path

ROM = Path('D:/Documents/PlatformIO/Projects/cuktech-ap01-firmware/roms/0041/ap01-1.0.2_0041.bin')
HERE = Path(__file__).resolve().parent
BASE = 0x9ffff000
checks = []

def sx(value, bits):
    return (value ^ (1 << (bits - 1))) - (1 << (bits - 1))

def word(address, size=4):
    with ROM.open('rb') as stream:
        stream.seek(address - BASE)
        data = stream.read(size)
    assert len(data) == size
    return int.from_bytes(data, 'little')

def accept(address, claim, actual, expected):
    assert actual == expected, (hex(address), claim, actual, expected)
    checks.append(dict(address=hex(address), claim=claim, value=actual))

def load(address, rd, rs, offset):
    w = word(address)
    accept(address, 'LW destination/base/signed-offset',
           [w & 127, (w >> 12) & 7, (w >> 7) & 31, (w >> 15) & 31, sx(w >> 20, 12)],
           [3, 2, rd, rs, offset])

def store(address, rs, base, offset, width):
    w = word(address)
    imm = ((w >> 25) << 5) | ((w >> 7) & 31)
    accept(address, 'store width/source/base/signed-offset',
           [w & 127, (w >> 12) & 7, (w >> 20) & 31, (w >> 15) & 31, sx(imm, 12)],
           [35, width, rs, base, offset])

def addi(address, rd, rs, offset):
    w = word(address)
    accept(address, 'ADDI destination/base/signed-offset',
           [w & 127, (w >> 12) & 7, (w >> 7) & 31, (w >> 15) & 31, sx(w >> 20, 12)],
           [19, 0, rd, rs, offset])

def jal(address, target):
    w = word(address)
    imm = ((w >> 31) << 20) | (((w >> 12) & 255) << 12) | (((w >> 20) & 1) << 11) | (((w >> 21) & 1023) << 1)
    accept(address, 'JAL ra target', [w & 127, (w >> 7) & 31, (address + sx(imm, 21)) & 0xffffffff], [111, 1, target])

def pair(address, target):
    a, b = word(address), word(address + 4)
    actual = (address + sx(a & 0xfffff000, 32) + sx(b >> 20, 12)) & 0xfffffffe
    accept(address, 'AUIPC/JALR ra target', [a & 127, (a >> 7) & 31, b & 127, (b >> 7) & 31, (b >> 12) & 7, (b >> 15) & 31, actual], [23, 1, 103, 1, 0, 1, target])

def cbnez(address, reg, target):
    w = word(address, 2)
    imm = (((w >> 12) & 1) << 8) | (((w >> 10) & 3) << 3) | (((w >> 5) & 3) << 6) | (((w >> 3) & 3) << 1) | (((w >> 2) & 1) << 5)
    accept(address, 'C.BNEZ register/target', [w & 3, w >> 13, 8 + ((w >> 7) & 7), address + sx(imm, 9)], [1, 7, reg, target])

load(0xa00ed802, 18, 10, 0x5c)
accept(0xa00ed806, 'C.MV s1,a0; C.MV s3,a1', word(0xa00ed806), 0x89ae84aa)
w = word(0xa00ed80a)
imm = ((w >> 31) << 12) | (((w >> 7) & 1) << 11) | (((w >> 25) & 63) << 5) | (((w >> 8) & 15) << 1)
accept(0xa00ed80a, 'BEQ s2,zero skip-invalidation', [w & 127, (w >> 12) & 7, (w >> 15) & 31, (w >> 20) & 31, 0xa00ed80a + sx(imm, 13)], [99, 0, 18, 0, 0xa00ed830])
jal(0xa00ed80e, 0xa00eaa50)
jal(0xa00ed812, 0xa00890e8)
cbnez(0xa00eaa50, 10, 0xa00eaa9c)
w = word(0xa00eaa9c, 2)
offset = (((w >> 10) & 7) << 3) | (((w >> 6) & 1) << 2) | (((w >> 5) & 1) << 6)
accept(0xa00eaa9c, 'C.LW destination/base/offset', [w & 3, w >> 13, 8 + ((w >> 2) & 7), 8 + ((w >> 7) & 7), offset], [0, 2, 10, 10, 0x2c])
accept(0xa00eaa9e, 'RET without a0 rewrite', word(0xa00eaa9e, 2), 0x8082)
w = word(0xa00890f6)
accept(0xa00890f6, 'LUI s1 global high', [w & 127, (w >> 7) & 31, w & 0xfffff000], [55, 9, 0x62fc9000])
addi(0xa00890fa, 9, 9, 0x57c)
load(0xa00890fe, 19, 9, 0x120)
cbnez(0xa0089102, 10, 0xa0089128)
accept(0xa0089128, 'C.MV s2,a0 preserves non-NULL source', word(0xa0089128, 2), 0x892a)
for address, offset in [(0xa008912a, -0x34), (0xa008912e, -0x30), (0xa0089132, -0x2c), (0xa0089136, -0x28), (0xa008913a, -0x24)]:
    store(address, 0, 8, offset, 2)
store(0xa008913e, 10, 8, -0x38, 2)
jal(0xa0089142, 0xa00dd454)
store(0xa0089146, 10, 8, -0x34, 0)
addi(0xa008914a, 11, 8, -0x38)
accept(0xa008914e, 'C.MV a0,s3 selects G+120', word(0xa008914e, 2), 0x854e)
pair(0xa0089150, 0xa019cfbe)
accept(0xa0089158, 'C.LI a2,24; C.LI a1,0', word(0xa0089158), 0x45814661)
addi(0xa008915c, 10, 8, -0x38)
jal(0xa0089160, 0xa0024906)
accept(0xa0089164, 'C.MV a0,s2 restores source for classifier', word(0xa0089164, 2), 0x854a)
store(0xa0089166, 18, 8, -0x34, 2)
jal(0xa008916a, 0xa00dd454)
store(0xa008916e, 10, 8, -0x30, 0)
load(0xa0089172, 10, 9, 0x11c)
addi(0xa0089176, 11, 8, -0x38)
pair(0xa008917a, 0xa019cfbe)
result = dict(kind='independent review of existing conclusions; new functionality=0', result='passed', checks=len(checks), mapping='offset=VA-0x9ffff000', inherited='A23 memset/classifier/cache identity and A27/A28 invalidation internals', findings=checks)
(HERE / 'review-evidence.json').write_text(json.dumps(result, ensure_ascii=False, indent=2) + '\n', encoding='utf8')
print(json.dumps({key: result[key] for key in ['kind', 'result', 'checks']}))
