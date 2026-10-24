"""B26 independent static ROM field checks; never executes target instructions."""
import json
from pathlib import Path

ROOT = Path('D:/Documents/PlatformIO/Projects/cuktech-ap01-firmware')
OUT = Path(__file__).resolve().parent
ROM = (ROOT / 'roms/0041/ap01-1.0.2_0041.bin').read_bytes()
BASE = 0x9ffff000
checks = []


def raw(address, size=4):
    return ROM[address - BASE:address - BASE + size]


def word(address):
    return int.from_bytes(raw(address), 'little')


def signed(value, bits):
    return value - (1 << bits) if value & (1 << (bits - 1)) else value


def check(address, claim, actual, expected, size=4):
    assert actual == expected, (hex(address), claim, actual, expected)
    checks.append({'address': hex(address), 'raw': raw(address, size).hex(),
                   'claim': claim, 'decoded': actual})


def fields(address):
    w = word(address)
    return [w & 127, (w >> 7) & 31, (w >> 12) & 7,
            (w >> 15) & 31, (w >> 20) & 31]


def load(address, destination, width, source, offset):
    w = word(address)
    check(address, 'load opcode/rd/funct3/rs1/signed immediate',
          fields(address)[:4] + [signed(w >> 20, 12)],
          [3, destination, width, source, offset])


def branch(address, funct3, left, right, target):
    w = word(address)
    displacement = signed(((w >> 31) << 12) | (((w >> 7) & 1) << 11) |
                          (((w >> 25) & 63) << 5) | (((w >> 8) & 15) << 1), 13)
    check(address, 'branch opcode/funct3/rs1/rs2/target',
          [w & 127, (w >> 12) & 7, (w >> 15) & 31, (w >> 20) & 31,
           address + displacement], [0x63, funct3, left, right, target])


def jal(address, destination, target):
    w = word(address)
    displacement = signed(((w >> 31) << 20) | (((w >> 12) & 255) << 12) |
                          (((w >> 20) & 1) << 11) | (((w >> 21) & 1023) << 1), 21)
    check(address, 'JAL opcode/rd/target', [w & 127, (w >> 7) & 31, address + displacement],
          [0x6f, destination, target])


def immediate(address, destination, source, value):
    w = word(address)
    check(address, 'ADDI opcode/rd/funct3/rs1/immediate',
          fields(address)[:4] + [signed(w >> 20, 12)],
          [0x13, destination, 0, source, value])


def half(address, value, claim):
    check(address, claim, int.from_bytes(raw(address, 2), 'little'), value, 2)


# Only caller ABI setup needed by the contract; dispatcher ABI is inherited E01/E02.
half(0xa00a85ba, 0x84b2, 'C.MV s1,a2 saves payload')
immediate(0xa00a860a, 15, 0, 0x56)
branch(0xa00a860e, 1, 10, 15, 0xa00a8616)
jal(0xa00a8612, 0, 0xa00a98d0)

# cmd51 object identity anchors, not its already accepted classification.
check(0xa00a93c2, 'LUI a5 establishes global base', word(0xa00a93c2), 0x62fcb7b7)
load(0xa00a93c6, 14, 2, 15, 0x2cc)
check(0xa00a93ca, 'SW a5,-0x64(s0) retains global base', word(0xa00a93ca), 0xf8f42e23)
load(0xa00a93e8, 15, 2, 8, -0x64)
load(0xa00a93ec, 15, 2, 15, 0x2cc)
load(0xa00a93f0, 14, 4, 15, 6)
immediate(0xa00a93f8, 20, 0, 0x1a8)
check(0xa00a93fc, 'MUL s4,s1,s4', fields(0xa00a93fc) + [word(0xa00a93fc) >> 25],
      [0x33, 20, 0, 9, 20, 1])
load(0xa00a9400, 25, 2, 15, 0)
check(0xa00a9404, 'ADD s11,s9,s4', fields(0xa00a9404) + [word(0xa00a9404) >> 25],
      [0x33, 27, 0, 25, 20, 0])

check(0xa00a98d0, 'LUI a5 global base', word(0xa00a98d0), 0x62fcb7b7)
w = word(0xa00a98d4)
check(0xa00a98d4, 'SB zero,0x2f0(a5) before length branch',
      [w & 127, (w >> 12) & 7, (w >> 15) & 31, (w >> 20) & 31,
       signed(((w >> 25) << 5) | ((w >> 7) & 31), 12)], [0x23, 0, 15, 0, 0x2f0])
half(0xa00a98d8, 0x47b5, 'C.LI a5,13')
branch(0xa00a98da, 1, 11, 15, 0xa00a9ab6)
check(0xa00a98de, 'LUI a5 global base repeated', word(0xa00a98de), 0x62fcb7b7)
load(0xa00a98e2, 18, 2, 15, 0x2cc)
load(0xa00a98e6, 19, 4, 12, 0)
half(0xa00a98ea, 0x8a3e, 'C.MV s4,a5 retains global base')
branch(0xa00a98ec, 0, 18, 0, 0xa00a9906)
load(0xa00a98f0, 15, 4, 18, 6)
branch(0xa00a98f4, 7, 19, 15, 0xa00a9988)
load(0xa00a98f8, 18, 2, 18, 0)
immediate(0xa00a98fc, 15, 0, 0x1a8)
w = word(0xa00a9900)
check(0xa00a9900, 'custom MULA opcode/rd/f3/rs1/rs2/f7',
      fields(0xa00a9900) + [w >> 25], [0x0b, 18, 1, 19, 15, 16])
half(0xa00a9904, 0x0961, 'C.ADDI s2,0x18 gives destination')
half(0xa00a9906, 0x0485, 'C.ADDI s1,1 gives source')
for a, v, claim in [(0xa00a9908, 0x4631, 'C.LI a2,12 comparison size'),
                    (0xa00a990a, 0x85ca, 'C.MV a1,s2 comparison destination'),
                    (0xa00a990c, 0x8526, 'C.MV a0,s1 comparison source'),
                    (0xa00a9916, 0x4631, 'C.LI a2,12 copy size'),
                    (0xa00a9918, 0x85a6, 'C.MV a1,s1 copy source'),
                    (0xa00a991a, 0x854a, 'C.MV a0,s2 copy destination')]:
    half(a, v, claim)
jal(0xa00a990e, 1, 0xa00501be)
branch(0xa00a9912, 0, 10, 0, 0xa00a9ab6)
jal(0xa00a991c, 1, 0xa000589c)

# Re-derive current item after copy; do not assume the cached destination survived as current.
load(0xa00a9920, 15, 2, 20, 0x2cc)
immediate(0xa00a9924, 14, 0, 0x1a8)
check(0xa00a9928, 'MUL a4,s3,a4', fields(0xa00a9928) + [word(0xa00a9928) >> 25],
      [0x33, 14, 0, 19, 14, 1])
branch(0xa00a992c, 0, 15, 0, 0xa00a9d06)
load(0xa00a9930, 13, 4, 15, 6)
branch(0xa00a9934, 7, 19, 13, 0xa00a9d06)
half(0xa00a9938, 0x4394, 'C.LW a3,0(a5) reloads current array')
half(0xa00a993a, 0x6585, 'C.LUI a1,1')
immediate(0xa00a993c, 11, 11, -0x800)
for a, f3 in [(0xa00a9940, 4), (0xa00a994c, 5)]:
    w = word(a)
    check(a, 'indexed word opcode/rd/f3/rs1/rs2/upper5/shift',
          fields(a) + [w >> 27, (w >> 25) & 3], [0x0b, 12, f3, 13, 14, 8, 0])
check(0xa00a9944, 'ADD a5,a3,a4 current item address',
      fields(0xa00a9944) + [word(0xa00a9944) >> 25], [0x33, 15, 0, 13, 14, 0])
half(0xa00a994a, 0x8e4d, 'C.OR a2,a1 preserves mask and adds 0x800')
load(0xa00a9950, 17, 5, 15, 0x1a)
load(0xa00a9954, 16, 5, 15, 0x18)
load(0xa00a9958, 15, 5, 15, 0x1c)
half(0xa00a9968, 0xc03e, 'C.SWSP a5,0(sp) supplies next log argument')
for a, expected in [(0xa00a995c, 0xa0269737), (0xa00a9960, 0xa026a6b7)]:
    check(a, 'log string LUI', word(a), expected)
immediate(0xa00a996a, 14, 14, 0x760)
half(0xa00a996e, 0x87ce, 'C.MV a5,s3 gives index to log')
immediate(0xa00a9970, 13, 13, 0x3b8)
jal(0xa00a997c, 1, 0xa008b51a)
half(0xa00a9980, 0x854e, 'C.MV a0,s3 gives index to notification')
jal(0xa00a9982, 1, 0xa00a389c)

strings = {}
for address, expected in [(0xa0269760, b'UiIFaceMngBmsChange = %d, DCap=%d,FCap=%d,RCap=%d'),
                          (0xa026a3b8, b'UiIFaceMngBmsChange')]:
    actual = ROM[address - BASE:ROM.index(b'\0', address - BASE)]
    assert actual == expected
    strings[hex(address)] = actual.decode('ascii')

rule_path = ROOT / 'evidence/rea-0041-20261017/ghidra/Ghidra/Processors/RISCV/data/languages/ap01thead2.sinc'
rule_lines = rule_path.read_text().splitlines()
assert 'rd = rd + (rs1 * rs2);' in rule_lines[26]
assert 'local delta:4 = rs2 << thshift;' in rule_lines[6565]
assert 'local value:4 = *[ram]:4 ea;' in rule_lines[6568]
assert '*[ram]:4 ea = rd:4;' in rule_lines[6600]

result = {'static_only': True, 'baseline': 'dbd788a', 'status': 'PASS',
          'check_count': len(checks), 'checks': checks, 'strings': strings,
          'rule_source': str(rule_path), 'rule_lines': [[25, 28], [6564, 6572], [6596, 6603]],
          'limits': ['No target execution or input enumeration.',
                     'Private local ISA rules are inherited, not independent vendor certification.',
                     'Same object family/field formula is conditional on same total/array/index instance.',
                     'Physical units and cross-command scheduling are unverified.']}
(OUT / 'review-result.json').write_text(json.dumps(result, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
print(f'PASS: {len(checks)} independent original-word field/target checks and 2 strings')
