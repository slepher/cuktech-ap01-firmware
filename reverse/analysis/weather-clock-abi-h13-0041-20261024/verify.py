"""Read-only ROM/retained-evidence checks. No model, firmware, or replay execution."""
import json
from pathlib import Path
from capstone import Cs, CS_ARCH_RISCV, CS_MODE_RISCV32, CS_MODE_RISCVC

HERE = Path(__file__).resolve().parent
REPO = HERE.parents[1]
MAIN = Path('D:/Documents/PlatformIO/Projects/cuktech-ap01-firmware')
BASE = 0x9ffff000
rom = (MAIN / 'roms/0041/ap01-1.0.2_0041.bin').read_bytes()
decoder = Cs(CS_ARCH_RISCV, CS_MODE_RISCV32 | CS_MODE_RISCVC)

def raw(start, end):
    return rom[start - BASE:end - BASE]

def window(start, end):
    data = raw(start, end)
    insns = list(decoder.disasm(data, start))
    assert sum(i.size for i in insns) == len(data)
    return {'start': hex(start), 'end_exclusive': hex(end), 'hex': data.hex(),
            'instructions': [f'{i.address:08x}: {i.bytes.hex()} {i.mnemonic} {i.op_str}' for i in insns]}

old = json.loads((REPO / 'analysis/weather-dataflow-0041-20261023/instruction-windows.json').read_text())
clock = next(w for w in old['windows'] if w['name'] == 'clock_ms')
assert raw(0xa00a9d1e, 0xa00a9d64).hex() == clock['hex']

word = int.from_bytes(raw(0xa00a9d5a, 0xa00a9d5e), 'little')
fields = {'opcode': word & 127, 'rd': (word >> 7) & 31,
          'funct3': (word >> 12) & 7, 'rs1': (word >> 15) & 31,
          'rs2': (word >> 20) & 31, 'funct7': word >> 25}
assert fields == {'opcode': 0x77, 'rd': 10, 'funct3': 1, 'rs1': 18, 'rs2': 14, 'funct7': 0x52}
patch = (REPO.parent / 'tooling/scripts/qemu-ap01-cpu.patch').read_text()
assert 'ap01_umar64 1010010 ..... ..... 001 ..... 1110111 @r' in patch
assert 'int rd = a->rd & ~1;' in patch
assert 'tcg_gen_mulu2_i32(pl, ph, left, right);' in patch
assert 'tcg_gen_add2_i32(low, high, al, ah, pl, ph);' in patch

def jal_target(pc):
    w = int.from_bytes(raw(pc, pc + 4), 'little')
    assert w & 127 == 0x6f
    imm = ((w >> 31) << 20) | (((w >> 21) & 1023) << 1) | (((w >> 20) & 1) << 11) | (((w >> 12) & 255) << 12)
    if imm & (1 << 20): imm -= 1 << 21
    return hex((pc + imm) & 0xffffffff)

calls = {hex(pc): jal_target(pc) for pc in [0xa00a9d30, 0xa00269a6, 0xa00aaca0, 0xa00aae98]}
assert calls == {'0xa00a9d30': '0xa002696a', '0xa00269a6': '0xa002645a',
                 '0xa00aaca0': '0xa00a9d1e', '0xa00aae98': '0xa00a9d1e'}

root = MAIN / 'evidence/rea-0041-20261017'
def matched_bodies(value):
    out = []
    if isinstance(value, dict):
        if value.get('address') == '0xa00a9d1e' and 'body' in value:
            out.append(value['body'])
        for child in value.values(): out.extend(matched_bodies(child))
    elif isinstance(value, list):
        for child in value: out.extend(matched_bodies(child))
    return out

reuse = []
for name in ['whole-rom-round3-open-20261023-002.json', 'whole-rom-round3-open-20261023-004.json']:
    source = root / 'round3/evidence' / name
    outer = json.loads(source.read_text(encoding='utf-8-sig'))
    evidence = json.loads(outer['content'][0]['text'])
    bodies = matched_bodies(evidence['raw_result'])
    assert bodies and all(b['ranges'] == [{'start':'0xa00a9d1e','end':'0xa00a9d59'}] for b in bodies)
    reuse.append({'source': str(source), 'evidence_id': evidence['evidence_id'], 'body': bodies[0]})

model3 = (root / 'round3/scripts/ap01thead3.sinc').read_text()
assert ':sub64 ' in model3 and ':umar64 ' not in model3
complete = MAIN / 'reverse/rehost/weather-calendar-complete-0041.json'
assert 'a00a9d1e' not in complete.read_text(encoding='utf-8-sig').lower()
result = {'scope': 'static normal-call ABI; no model execution',
          'inherited_clock_bytes_match_ROM': True,
          'vendor_word': hex(word), 'vendor_fields': fields,
          'semantic_source': 'existing tooling/scripts/qemu-ap01-cpu.patch UMAR64; inherited, not a new ISA rule',
          'direct_calls': calls, 'later_round3': reuse,
          'complete_has_no_helper_address': True,
          'source_windows': [window(0xa0026974, 0xa0026982), window(0xa002699c, 0xa00269f0)],
          'new_function_exports': 0, 'model_runs': 0,
          'unknown': ['epoch', 'upstream source/version', 'source calibration and lower clock implementation']}
(HERE / 'static-result.json').write_text(json.dumps(result, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
print(json.dumps({'passed': True, 'clock_bytes': 'match', 'vendor_fields': fields, 'direct_calls': calls,
                  'later_round3_body_ends': 'a00a9d59', 'new_function_exports': 0}))
