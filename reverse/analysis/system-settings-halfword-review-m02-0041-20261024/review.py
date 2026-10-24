"""Independent M02 static wrapper/return checks; no CRC evaluation or target execution."""
from pathlib import Path
import json

ROOT = Path('D:/Documents/PlatformIO/Projects/cuktech-ap01-firmware')
OUT = Path(__file__).resolve().parent
ROM = (ROOT / 'roms/0041/ap01-1.0.2_0041.bin').read_bytes()
BASE = 0x9ffff000
checks = []


def read(address, size=4):
    return int.from_bytes(ROM[address - BASE:address - BASE + size], 'little')


def sign(n, bits):
    return n - (1 << bits) if n & (1 << (bits - 1)) else n


def check(address, meaning, actual, expected, size=4):
    assert actual == expected, (hex(address), meaning, actual, expected)
    checks.append({'address': hex(address), 'raw': read(address, size).to_bytes(size, 'little').hex(),
                   'meaning': meaning, 'decoded': actual})


def lui(address, destination, high):
    w = read(address)
    check(address, 'LUI opcode/rd/upper', [w & 127, w >> 7 & 31, w & 0xfffff000],
          [0x37, destination, high])


def addi(address, destination, source, immediate):
    w = read(address)
    check(address, 'ADDI opcode/rd/funct3/rs1/immediate',
          [w & 127, w >> 7 & 31, w >> 12 & 7, w >> 15 & 31, sign(w >> 20, 12)],
          [0x13, destination, 0, source, immediate])


def c_li(address, destination, value):
    h = read(address, 2)
    check(address, 'C.LI quadrant/funct3/rd/signed immediate',
          [h & 3, h >> 13, h >> 7 & 31, sign(((h >> 12 & 1) << 5) | (h >> 2 & 31), 6)],
          [1, 2, destination, value], 2)


def jal(address, target):
    w = read(address)
    delta = sign(((w >> 31) << 20) | (((w >> 12) & 255) << 12) |
                 (((w >> 20) & 1) << 11) | (((w >> 21) & 1023) << 1), 21)
    check(address, 'JAL opcode/rd/target', [w & 127, w >> 7 & 31, address + delta], [0x6f, 1, target])


def c_lwsp(address, destination, offset):
    h = read(address, 2)
    immediate = ((h >> 12 & 1) << 5) | ((h >> 4 & 7) << 2) | ((h >> 2 & 3) << 6)
    check(address, 'C.LWSP quadrant/funct3/rd/offset',
          [h & 3, h >> 13, h >> 7 & 31, immediate], [2, 2, destination, offset], 2)


def c_stack_return(add_address, ret_address):
    h = read(add_address, 2)
    check(add_address, 'C.ADDI sp,16',
          [h & 3, h >> 13, h >> 7 & 31, sign(((h >> 12 & 1) << 5) | (h >> 2 & 31), 6)],
          [1, 0, 2, 16], 2)
    h = read(ret_address, 2)
    check(ret_address, 'C.JR ra, no a0 destination', h, 0x8082, 2)


lui(0xa00a46f0, 11, 0x62fc9000)
c_li(0xa00a46f4, 12, 6)
addi(0xa00a46f6, 11, 11, 0x98)
c_li(0xa00a46fa, 10, 0)
jal(0xa00a46fc, 0xa00ee8fc)
c_lwsp(0xa00a4700, 1, 12)
c_lwsp(0xa00a4702, 8, 8)
c_stack_return(0xa00a4704, 0xa00a4706)

# Sparse stitch to the existing L04 SH consumer; no file service re-analysis.
jal(0xa00ab2c2, 0xa00a46e8)
lui(0xa00ab2c6, 15, 0x62fc9000)
addi(0xa00ab2ca, 14, 15, 0x98)
w = read(0xa00ab2ce)
offset = sign(((w >> 25) << 5) | (w >> 7 & 31), 12)
check(0xa00ab2ce, 'SH opcode/funct3/base/value/offset',
      [w & 127, w >> 12 & 7, w >> 15 & 31, w >> 20 & 31, offset], [0x23, 1, 14, 10, 6])

# Width-only support for inherited positive-length result, not recurrence/table re-analysis.
w = read(0xa00ee926)
check(0xa00ee926, 'EXTU opcode/rd/funct3/rs1/msb/lsb',
      [w & 127, w >> 7 & 31, w >> 12 & 7, w >> 15 & 31, w >> 26 & 63, w >> 20 & 63],
      [0x0b, 10, 3, 10, 15, 0])
w = read(0xa00ee92a)
delta = sign(((w >> 31) << 12) | ((w >> 7 & 1) << 11) | ((w >> 25 & 63) << 5) |
             ((w >> 8 & 15) << 1), 13)
check(0xa00ee92a, 'BLT loop edge leaves a0 untouched; untaken path to tail',
      [w & 127, w >> 12 & 7, w >> 15 & 31, w >> 20 & 31, 0xa00ee92a + delta],
      [0x63, 4, 13, 12, 0xa00ee90c])
c_lwsp(0xa00ee92e, 8, 12)
c_stack_return(0xa00ee930, 0xa00ee932)

old_report = (ROOT / 'reverse/reports/ap01/usb-interface-ota-0041-20261023.md').read_text(encoding='utf-8')
assert 'a00ee8fc' in old_report and '0x1021' in old_report and '& 0xffff' in old_report
retained = json.loads((ROOT / 'reverse/analysis/usb-interface-ota-0041-20261023.json').read_text(encoding='utf-8'))
old = next(f for f in retained['functions'] if f['address'] == '0xa00ee8fc')
assert old['evidence_id'] == 'ev_98903ff50cb2f96b342e6df43357e470de464e58dd13257922d9d3e9efaad342'
assert '0xa00ee926: th.extu a0, a0' in old['assembly']

languages = ROOT / 'evidence/rea-0041-20261017/ghidra/Ghidra/Processors/RISCV/data/languages'
registers = (languages / 'ap01thead2.reg.sinc').read_text().splitlines()
rules = (languages / 'ap01thead2.sinc').read_text().splitlines()
assert 'thlsb=(20,25)' in registers[1163]
assert 'thmsb=(26,31)' in registers[1164]
assert ':th.extu rd,rs1,15,0 ' in rules[3929]
assert 'local value:4 = rs1 << 16;' in rules[3931]
assert 'rd = value >> 16;' in rules[3932]

result = {'baseline': '6fef66e', 'static_only': True, 'status': 'PASS',
          'check_count': len(checks), 'checks': checks,
          'inherited_crc_evidence': old['evidence_id'],
          'width_rule': {'register_lines': [1164, 1165], 'semantic_lines': [3930, 3934]},
          'coverage': {'input': ['0x62fc9098', '0x62fc909d'], 'byte_count': 6,
                       'excluded_output': ['0x62fc909e', '0x62fc909f']},
          'limits': ['CRC recurrence, polynomial/table and test vectors inherited, not recomputed.',
                     'No algorithm evaluation, input enumeration or target/model execution.',
                     'Private local EXTU rule is not independent vendor specification.',
                     'No full structure, atomic snapshot, source version or persistence claim.']}
(OUT / 'review-result.json').write_text(json.dumps(result, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
print(f'PASS: {len(checks)} independent wrapper/consumer/return checks; CRC evaluations=0')
