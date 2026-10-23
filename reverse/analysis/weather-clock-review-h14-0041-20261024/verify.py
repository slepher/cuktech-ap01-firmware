"""Independent sparse static checks only; no target/model execution or time replay."""
import json
from pathlib import Path

HERE = Path(__file__).resolve().parent
REVERSE = HERE.parents[1]
ROOT = REVERSE.parent
MAIN = Path('D:/Documents/PlatformIO/Projects/cuktech-ap01-firmware')
ROM = (MAIN / 'roms/0041/ap01-1.0.2_0041.bin').read_bytes()
BASE = 0x9ffff000

def raw(address, size):
    return ROM[address - BASE:address - BASE + size]

def word(address):
    return int.from_bytes(raw(address, 4), 'little')

def fields(value):
    return dict(opcode=value & 127, rd=value >> 7 & 31, funct3=value >> 12 & 7,
                rs1=value >> 15 & 31, rs2=value >> 20 & 31, funct7=value >> 25)

def jal(address):
    value = word(address)
    assert value & 127 == 0x6f
    delta = ((value >> 31) << 20 | (value >> 21 & 1023) << 1 |
             (value >> 20 & 1) << 11 | (value >> 12 & 255) << 12)
    if delta & 0x100000:
        delta -= 0x200000
    return (address + delta) & 0xffffffff

# Compare existing evidence without re-exporting either complete helper or URL body.
h13 = json.loads((REVERSE / 'analysis/weather-clock-abi-h13-0041-20261024/static-result.json').read_text())
for window in h13['source_windows']:
    saved = bytes.fromhex(window['hex'])
    assert raw(int(window['start'], 16), len(saved)) == saved
old = json.loads((REVERSE / 'analysis/weather-dataflow-0041-20261023/instruction-windows.json').read_text())
clock = next(w for w in old['windows'] if w['name'] == 'clock_ms')
assert raw(0xa00a9d1e, len(bytes.fromhex(clock['hex']))).hex() == clock['hex']

calls = {0xa00a9d30: 0xa002696a, 0xa00269a6: 0xa002645a,
         0xa00aaca0: 0xa00a9d1e, 0xa00aae98: 0xa00a9d1e}
for address, target in calls.items():
    assert jal(address) == target
for address, rd, rs1, rs2 in [(0xa00a9d42, 9, 15, 9), (0xa00a9d4e, 15, 9, 14)]:
    assert fields(word(address)) == dict(opcode=0x33, rd=rd, funct3=4, rs1=rs1, rs2=rs2, funct7=1)
vendor = fields(word(0xa00a9d5a))
assert vendor == dict(opcode=0x77, rd=10, funct3=1, rs1=18, rs2=14, funct7=0x52)

# Source text is inherited ISA evidence, read only; never import/execute model/test.
patch = (ROOT / 'tooling/scripts/qemu-ap01-cpu.patch').read_text()
body = patch.split('+static bool trans_ap01_umar64(', 1)[1].split('+}', 1)[0]
for clause in ['int rd = a->rd & ~1;', 'get_gpr(ctx, a->rs1, EXT_ZERO)',
               'get_gpr(ctx, a->rs2, EXT_ZERO)', 'tcg_gen_mulu2_i32(pl, ph, left, right);',
               'tcg_gen_add2_i32(low, high, al, ah, pl, ph);',
               'gen_set_gpr(ctx, rd, result);', 'gen_set_gpr(ctx, rd + 1, result);']:
    assert clause in body
assert 'ap01_umar64 1010010 ..... ..... 001 ..... 1110111 @r' in patch

anchors = {
    0xa00a9d2a: '930584fe0145',        # output local; selector zero
    0xa00a9d54: '3e8593d5f741',        # low and arithmetic high
    0xa00a9d5a: '7715e9a4424905618280', # vendor word; restore; return
    0xa00269d0: '37d69a3b1306f69f6358f600', # +999999999; signed BGE
    0xa00269dc: '373665c413060660b297050798c1dcc1', # -1e9; one carry; stores
    0xa00269f4: '2685',                # normal return status s1 -> a0
}
for address, expected in anchors.items():
    assert raw(address, len(bytes.fromhex(expected))).hex() == expected
result = dict(passed=True, inherited_byte_windows_match=True,
              direct_calls={hex(k): hex(v) for k, v in calls.items()},
              div_encoding='OP/M funct3=4, funct7=1: signed RV32 DIV, twice',
              vendor_word=hex(word(0xa00a9d5a)), vendor_fields=vendor,
              inherited_semantics='unsigned single-register product + a1:a0 accumulator modulo 2^64',
              sparse_anchors={hex(k): v for k, v in anchors.items()},
              normalization_limit='signed upper-bound test and one carry only; no general range guarantee',
              new_features=0, model_runs=0, replay_runs=0)
(HERE / 'static-review.json').write_text(json.dumps(result, ensure_ascii=False, indent=2) + '\n')
print(json.dumps(dict(passed=True, new_features=0, model_runs=0, replay_runs=0)))
