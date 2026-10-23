"""Independent retained-evidence review; never opens a target or runs a model."""
import hashlib
import json
from pathlib import Path

ROOT = Path('D:/Documents/PlatformIO/Projects/cuktech-ap01-firmware')
HERE = Path(__file__).resolve().parent
EVIDENCE = ROOT / 'evidence/rea-0041-20261017'

def load(relative):
    return json.loads((EVIDENCE / relative).read_text())['structuredContent']

new = load('round3/evidence/whole-rom-round3-open-20261023-002.json')
old = load('evidence/whole-rom-graph-20261023-4778.json')
assert new['evidence_id'] == 'ev_dac9ee80a05e233e383bc1f10b5d225121efdc2db62ab51519958d8f220d15c3'
assert old['evidence_id'] == 'ev_2ecf5b8ded9c350a2da4c8206066d7cc73f0e3f9f2e80eb4fc229f111a5aeceb'
rom = (ROOT / 'roms/0041/ap01-1.0.2_0041.bin').read_bytes()
# Compare the existing subject commitment; do not create a new hash inventory.
assert new['subject'] == old['subject']
assert hashlib.sha256(rom).hexdigest() == new['subject']['digest']['sha256']
assert new['analysis_profile']['digest'] == 'bcefdee5092076e55636e077b45523e203f4b870ae7b7ab547945ed1b8162279'
assert old['analysis_profile']['digest'] == 'b6368dd18431e8113aa5026c713d41e648ab0f6ddd9421ff6c4a49e23b3cd2f3'
for record, language in [(new, 'ap01thead3'), (old, 'ap01thead2')]:
    p = record['analysis_profile']['parameters']
    assert p['language_id'] == 'RISCV:LE:32:' + language
    assert p['base_address'] == '0x9ffff000' and p['bit_width'] == 32
    assert record['parameters'] == {'procedure': '0xa00a12d0'}
n = new['normalized_result']
body = n['procedure']['body']
assert body['ranges'] == [{'start': '0xa00a12d0', 'end': '0xa00a24a5'}]
assert body['total_bytes'] == body['span_bytes'] == 4566
assert body['contains_entry'] and not body['non_contiguous']
assert old['normalized_result']['body']['ranges'] == [{'start': '0xa00a12d0', 'end': '0xa00a144f'}]
assembly = n['assembly']
by = {int(s.split(':')[0], 16): s.split(': ', 1)[1] for s in assembly}
anchors = {
    0xa00a12d0: 'c.addi16sp sp, -0x110',
    0xa00a12da: 'c.addi4spn s0, sp, 0x110',
    0xa00a13a8: 'c.addi16sp sp, 0x110', 0xa00a13aa: 'ret',
    0xa00a1450: 'sub64 a0, a2, a4',
    0xa00a1aa4: 'andi a0, s10, 0xff', 0xa00a1aa8: 'jal ra, 0xa00a53c0',
    0xa00a1aac: 'th.lrhu a3, s11, s10, 0x3',
    0xa00a1acc: 'sw a0, -0xe4, s0', 0xa00a1b20: 'lhu a6, 0xa, a0',
    0xa00a1b24: 'c.li a0, 0x4', 0xa00a1cd0: 'lw a5, -0xe4, s0',
    0xa00a1cd4: 'addi a3, s0, -0xa8', 0xa00a1cd8: 'lbu a2, 0x12, a5',
    0xa00a1cdc: 'slli a5, s10, 0x3', 0xa00a1ce2: 'th.srb a2, a3, s10, 0x0',
}
for pc, text in anchors.items():
    assert by[pc] == text, (hex(pc), by[pc])
assert assembly[-1] == '0xa00a24a4: c.j 0xa00a2394'
slots = [s for s in assembly if '-0xe4, s0' in s]
assert slots == ['0xa00a1acc: sw a0, -0xe4, s0', '0xa00a1cd0: lw a5, -0xe4, s0']

def word(pc):
    offset = pc - 0x9ffff000
    return int.from_bytes(rom[offset:offset + 4], 'little')

def sign(value, bits):
    return value - (1 << bits) if value >> (bits - 1) else value

w = word(0xa00a1aa8)
imm = ((w >> 31) << 20) | (((w >> 12) & 255) << 12) | (((w >> 20) & 1) << 11) | (((w >> 21) & 1023) << 1)
assert w & 127 == 0x6f and (w >> 7) & 31 == 1
assert 0xa00a1aa8 + sign(imm, 21) == 0xa00a53c0
# I-type loads: opcode/funct3/rd/base/signed offset, independently of pseudocode.
for pc, fields in {
    0xa00a1b20: (3, 5, 16, 10, 10),
    0xa00a1cd0: (3, 2, 15, 8, -228),
    0xa00a1cd8: (3, 4, 12, 15, 18),
}.items():
    w = word(pc)
    assert (w & 127, (w >> 12) & 7, (w >> 7) & 31, (w >> 15) & 31, sign(w >> 20, 12)) == fields
w = word(0xa00a1acc)
assert (w & 127, (w >> 12) & 7, (w >> 15) & 31, (w >> 20) & 31,
        sign(((w >> 25) << 5) | ((w >> 7) & 31), 12)) == (0x23, 2, 8, 10, -228)
w = word(0xa00a1450)
assert w == 0xc2e61577
assert (w & 127, (w >> 12) & 7, w >> 25, (w >> 7) & 31, (w >> 15) & 31, (w >> 20) & 31) == (0x77, 1, 0x61, 10, 12, 14)
model = (EVIDENCE / 'round3/scripts/ap01thead3.sinc').read_text()
assert ':sub64 rd,rs1,rs2 is op0006=0x77 & op1214=1 & op2531=0x61' in model
assert 'halt_baddata' not in n['pseudocode']
for pc in ['a00a1abc', 'a00a1adc', 'a00a23f0']:
    assert 'Removing unreachable block (ram,0x' + pc + ')' in n['pseudocode']
out = {
    'status': 'PASS', 'new_functionality': 0,
    'identity': 'Original ROM matches the existing subject commitment in both retained records; profiles remain distinct.',
    'coverage': 'round3 retained AddressSet a00a12d0..a00a24a5 includes the call and slot chain; round2 ends a00a144f.',
    'checks': ['16 retained assembly anchors', '2 direct s0-e4 references',
               '6 independent ROM instruction decodes: JAL, SW, LW, LHU, LBU, SUB64',
               'existing SUB64 clause only read, never run', '3 preserved decompiler unreachable-block warnings'],
    'limits': ['No full CFG/business/ABI certification', 'No indirect alias or +34/+38 reader exclusion',
               'No model execution, replay, target opening, whole-function export or CTK scan'],
}
(HERE / 'review-result.json').write_text(json.dumps(out, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
print('PASS: identity, distinct profiles, retained ranges, local ABI/width and SUB64; new functionality 0')
