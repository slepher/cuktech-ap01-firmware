"""N02: bounded byte/encoding checks only; never executes target instructions.

Inputs remain in the main repository. Outputs are confined to this directory.
Inherited contracts are referenced, not revalidated by running their scripts.
"""
import json
from pathlib import Path

MAIN = Path('D:/Documents/PlatformIO/Projects/cuktech-ap01-firmware')
OUT = Path(__file__).resolve().parent
BASE = 0x9ffff000
SOURCE = 'reverse/analysis/buzzer-backlight-0041-20261023.json'
rom = (MAIN / 'roms/0041/ap01-1.0.2_0041.bin').read_bytes()
doc = json.loads((MAIN / SOURCE).read_text(encoding='utf-8'))
fn = next(x for x in doc['functions'] if x['address'] == '0xa00a8582')
original = fn['raw_ranges'][0]
retained = bytes.fromhex(original['hex'])
origin = int(original['start'], 16)
assembly = {int(s.split(':', 1)[0], 16): s.split(':', 1)[1].strip()
            for s in fn['assembly']}
checks = []


def check(label, actual, expected):
    assert actual == expected, (label, actual, expected)
    checks.append({'label': label, 'actual': actual, 'expected': expected})


def raw(pc, n=4):
    return rom[pc - BASE:pc - BASE + n]


def word(pc):
    return int.from_bytes(raw(pc), 'little')


def sx(value, width):
    return value - (1 << width) if value & (1 << (width - 1)) else value


def load(pc, rd, rs1, imm, f3):
    w = word(pc)
    check(hex(pc) + ' I-load',
          [w & 127, (w >> 7) & 31, (w >> 12) & 7,
           (w >> 15) & 31, sx(w >> 20, 12)], [3, rd, f3, rs1, imm])


def store(pc, rs2, rs1, imm, f3):
    w = word(pc)
    value = ((w >> 25) << 5) | ((w >> 7) & 31)
    check(hex(pc) + ' S-store',
          [w & 127, (w >> 12) & 7, (w >> 15) & 31,
           (w >> 20) & 31, sx(value, 12)], [35, f3, rs1, rs2, imm])


def branch(pc, rs1, rs2, f3, target):
    w = word(pc)
    imm = ((w >> 31) << 12) | (((w >> 7) & 1) << 11)
    imm |= (((w >> 25) & 63) << 5) | (((w >> 8) & 15) << 1)
    check(hex(pc) + ' B-fields/target',
          [w & 127, (w >> 15) & 31, (w >> 20) & 31,
           (w >> 12) & 7, pc + sx(imm, 13)], [99, rs1, rs2, f3, target])


def immediate(pc, rd, rs1, imm, f3):
    w = word(pc)
    check(hex(pc) + ' I-immediate',
          [w & 127, (w >> 7) & 31, (w >> 12) & 7,
           (w >> 15) & 31, sx(w >> 20, 12)], [19, rd, f3, rs1, imm])


def jal(pc, target):
    w = word(pc)
    imm = ((w >> 31) << 20) | (((w >> 12) & 255) << 12)
    imm |= (((w >> 20) & 1) << 11) | (((w >> 21) & 1023) << 1)
    check(hex(pc) + ' JAL', [w & 127, (w >> 7) & 31, pc + sx(imm, 21)],
          [111, 1, target])


windows = [(0xa00a93a4, 0xa00a93c2), (0xa00a9598, 0xa00a960a),
           (0xa00a972a, 0xa00a973e)]
selected = []
for start, end in windows:
    check(hex(start) + ' retained bytes', raw(start, end - start).hex(),
          retained[start - origin:end - origin].hex())
    pc = start
    while pc < end:
        size = 4 if int.from_bytes(raw(pc, 2), 'little') & 3 == 3 else 2
        assert pc + size <= end and pc in assembly, hex(pc)
        selected.append({'pc': hex(pc), 'file_offset': pc - BASE,
                         'raw': raw(pc, size).hex(), 'retained_decode': assembly[pc]})
        pc += size
    check(hex(start) + ' instruction boundary', pc, end)

# cmd51 scalar mapping. RISC-V register numbers are independent of old text.
load(0xa00a9598, 15, 18, 2, 5)   # u16 record+2
load(0xa00a959c, 14, 27, 0x10, 5)
branch(0xa00a95a0, 14, 15, 0, 0xa00a95ac)
store(0xa00a95a4, 15, 27, 0x10, 1)
immediate(0xa00a95a8, 16, 16, 0x100, 6)
load(0xa00a95ac, 15, 18, 0, 4)   # u8 record+0
load(0xa00a95b0, 14, 27, 0x12, 4)
branch(0xa00a95b4, 14, 15, 0, 0xa00a95c0)
store(0xa00a95b8, 15, 27, 0x12, 0)
immediate(0xa00a95bc, 16, 16, 0x200, 6)
load(0xa00a95c0, 17, 27, 0x0e, 4)
branch(0xa00a95c4, 17, 0, 0, 0xa00a9734)  # new/current type gate
load(0xa00a95c8, 15, 18, 1, 4)
load(0xa00a95cc, 14, 27, 0x0f, 4)
branch(0xa00a95d0, 14, 15, 0, 0xa00a9734)
store(0xa00a95d4, 15, 27, 0x0f, 0)
immediate(0xa00a95d8, 16, 16, 0x80, 6)
branch(0xa00a9734, 16, 0, 1, 0xa00a95dc)
# th.srw a6,s9,s4,0: current-event assignment, NOT OR with old mask.
w = word(0xa00a95e4)
check('0xa00a95e4 custom indexed word-store fields',
      [w & 127, w >> 7 & 31, w >> 12 & 7, w >> 15 & 31,
       w >> 20 & 31, w >> 25], [11, 16, 5, 25, 20, 32])
immediate(0xa00a9600, 10, 9, 255, 7)
jal(0xa00a9604, 0xa00a389c)
jal(0xa00a93be, 0xa0191652)
immediate(0xa00a93ba, 11, 11, 0xf8, 7)
load(0xa00a93a8, 11, 19, 0x1c, 4)
load(0xa00a93b0, 10, 9, 0x2d4, 2)

resource = 0xa02696f0
text = rom[resource - BASE:rom.index(b'\0', resource - BASE)].decode('utf-8')
check('cmd51 log', text, 'IFace %d:Update = 0x%08x, chgDevType = %d')

evidence = {
    'static_only': True, 'target_execution': False, 'baseline': '5bbc331',
    'main_root_readonly': str(MAIN), 'source': SOURCE,
    'evidence_id': fn['evidence_id'],
    'profile': {'provider': fn['profile']['provider'],
                'language': fn['profile']['parameters']['language_id']},
    'rom_identity_inherited': doc['rom_sha256'], 'mapping': 'offset = VA - 0x9ffff000',
    'scope': 'cmd51 scalar-field provenance and exact update gates only; old contracts inherited',
    'windows': [{'start': hex(a), 'end_exclusive': hex(b)} for a, b in windows],
    'byte_count': sum(b-a for a, b in windows), 'instruction_count': len(selected),
    'instructions': selected, 'checks': checks, 'check_count': len(checks),
    'status': 'PASS',
    'limitations': ['No target/model/input execution; checks do not prove all dataflow.',
                    'Custom store semantics inherit the E02 private SLEIGH rule, not vendor specification.',
                    'No cmd50 producer expansion, no cmd51 full classification repeat, no full dispatcher export.']}
(OUT / 'static-checks.json').write_text(json.dumps(evidence, ensure_ascii=False, indent=2)+'\n', encoding='utf-8')
print(f'N02_STATIC_PASS checks={len(checks)} bytes={evidence["byte_count"]} instructions={len(selected)}')
