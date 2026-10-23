"""E15 sparse static checks; no firmware, analyzer/model, or replay execution."""
import json
from pathlib import Path

HERE = Path(__file__).resolve().parent
MAIN = Path('D:/Documents/PlatformIO/Projects/cuktech-ap01-firmware')
ROM = MAIN / 'roms/0041/ap01-1.0.2_0041.bin'
LANG = MAIN / 'evidence/rea-0041-20261017/ghidra/Ghidra/Processors/RISCV/data/languages'
BASE = 0x9ffff000
raw = ROM.read_bytes()
rows = []


def word(pc, hexbytes):
    blob = raw[pc - BASE:pc - BASE + len(hexbytes) // 2]
    assert blob.hex() == hexbytes, hex(pc)
    return int.from_bytes(blob, 'little')


def signed(value, width):
    return value - (1 << width) if value & (1 << (width - 1)) else value


for pc, blob, expected in [
    (0xa009d18c, '7715aac0', [10, 20, 10]),
    (0xa009d1bc, '7716c5c0', [12, 10, 12]),
]:
    w = word(pc, blob)
    signature = [w & 127, (w >> 12) & 7, w >> 25]
    selectors = [(w >> bit) & 15 for bit in (8, 16, 21)]
    encoded = [(w >> bit) & 31 for bit in (7, 15, 20)]
    assert signature == [0x77, 1, 0x60]
    assert encoded == expected == [2 * i for i in selectors]
    rows.append(dict(pc=hex(pc), bytes=blob, signature=signature,
                     pair_selectors=selectors, destination_source1_source2_low_regs=expected))

# Decode B-immediates directly, independent of E14/Capstone output.
for pc, blob, expected in [
    (0xa009d190, '63e65501', [6, 11, 21, 0xa009d19c]),
    (0xa009d194, '6396ba00', [1, 21, 11, 0xa009d1a0]),
    (0xa009d198, '63744501', [7, 10, 20, 0xa009d1a0]),
    (0xa009d324, '63e8e704', [6, 15, 14, 0xa009d374]),
    (0xa009d328, '6317f700', [1, 14, 15, 0xa009d336]),
    (0xa009d332, '63e1e704', [6, 15, 14, 0xa009d374]),
]:
    w = word(pc, blob)
    imm = ((w >> 31) << 12) | (((w >> 7) & 1) << 11)
    imm |= (((w >> 25) & 63) << 5) | (((w >> 8) & 15) << 1)
    fields = [(w >> 12) & 7, (w >> 15) & 31, (w >> 20) & 31, pc + signed(imm, 13)]
    assert w & 127 == 0x63 and fields == expected
    rows.append(dict(pc=hex(pc), bytes=blob, branch_funct3_rs1_rs2_target=fields))

for pc, blob, expected in [
    (0xa009d184, '03a50714', ['load', 10, 15, 0x140]),
    (0xa009d188, '83a54714', ['load', 11, 15, 0x144]),
    (0xa009d1b0, '03a58713', ['load', 10, 15, 0x138]),
    (0xa009d1b4, '83a5c713', ['load', 11, 15, 0x13c]),
    (0xa009d1c0, '23acc712', ['store', 12, 15, 0x138]),
    (0xa009d1c4, '23aed712', ['store', 13, 15, 0x13c]),
    (0xa009d31c, '83a74914', ['load', 15, 19, 0x144]),
    (0xa009d32e, '83a70914', ['load', 15, 19, 0x140]),
]:
    w = word(pc, blob)
    opcode = w & 127
    assert opcode in (3, 0x23) and (w >> 12) & 7 == 2
    store = opcode == 0x23
    register = (w >> (20 if store else 7)) & 31
    imm = (((w >> 25) << 5) | ((w >> 7) & 31)) if store else w >> 20
    fields = ['store' if store else 'load', register, (w >> 15) & 31, signed(imm, 12)]
    assert fields == expected
    rows.append(dict(pc=hex(pc), bytes=blob, word_memory_operation_reg_base_offset=fields))

for pc, blob, expected in [
    (0xa009d1a4, 'a8c0', ['store', 10, 9, 0x40]),
    (0xa009d1a6, 'ecc0', ['store', 11, 9, 0x44]),
    (0xa009d1ca, 'a8c8', ['store', 10, 9, 0x50]),
    (0xa009d1cc, 'ecc8', ['store', 11, 9, 0x54]),
    (0xa009d31a, '9848', ['load', 14, 9, 0x10]),
    (0xa009d32c, 'd844', ['load', 14, 9, 0x0c]),
]:
    w = word(pc, blob)
    function = w >> 13
    assert w & 3 == 0 and function in (2, 6)
    offset = (((w >> 10) & 7) << 3) | (((w >> 6) & 1) << 2) | (((w >> 5) & 1) << 6)
    fields = ['store' if function == 6 else 'load', ((w >> 2) & 7) + 8, ((w >> 7) & 7) + 8, offset]
    assert fields == expected
    rows.append(dict(pc=hex(pc), bytes=blob, compressed_word_operation_reg_base_offset=fields))

model = (LANG / 'ap01thead2.sinc').read_text()
regs = (LANG / 'ap01thead2.reg.sinc').read_text()
profile = (LANG / 'ap01thead3.slaspec').read_text()
required = [
    ':add64 rd,rs1,rs2 is op0006=0x77 & op1214=1 & op2531=0x60',
    '[ zero sp tp t1 s0 a0 a2 a4 a6 s2 s4 s6 s8 s10 t3 t5 ];',
    '[ ra gp t0 t2 s1 a1 a3 a5 a7 s3 s5 s7 s9 s11 t4 t6 ];',
    'local low1:8 = zext(th2s1lo);', 'local high1:8 = zext(th2p1hi);',
    'local low2:8 = zext(th2s2lo);', 'local high2:8 = zext(th2p2hi);',
    'local src1:8 = (high1 << 32) | low1;', 'local src2:8 = (high2 << 32) | low2;',
    'local result:8 = src1 + src2;', 'th2dlo = result:4;', 'th2pdhi = result(4);',
]
assert all(fragment in model for fragment in required)
assert all(fragment in regs for fragment in ['th2p1lo=(16,19)', 'th2p2lo=(21,24)', 'th2pdlo=(8,11)'])
assert '@include "ap01thead2.sinc"' in profile
output = dict(task='E15', result='PASS', method='sparse raw bytes, direct field extraction, retained clause text only',
              rom=str(ROM), mapping='file_offset = VA - 0x9ffff000', instruction_count=len(rows), rows=rows,
              clause='ap01thead2.sinc:6638-6677; ap01thead2.reg.sinc:1148-1153; ap01thead3.slaspec:17',
              limits=['Not model execution or vendor ISA authentication.',
                      'F01/F02 lifecycle and complete heap not re-reviewed.',
                      'No time producer/unit/source, wall-clock or weather-clock conclusion.'])
(HERE / 'review.json').write_text(json.dumps(output, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
print(f'PASS: {len(rows)} sparse raw instructions; existing clause text matched; no model execution')
