"""H16: static byte/field and selected local source review; no target execution."""
import json
import subprocess
from pathlib import Path

from capstone import Cs, CS_ARCH_RISCV, CS_MODE_RISCV32, CS_MODE_RISCVC

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
MAIN = Path('D:/Documents/PlatformIO/Projects/cuktech-ap01-firmware')
BASE = 0x9ffff000
rom = (MAIN / 'roms/0041/ap01-1.0.2_0041.bin').read_bytes()
prior = json.loads((ROOT / 'analysis/clock-source-offset-h15-0041-20261024/static-result.json').read_text())
start = int(prior['window']['start'], 16)
end = int(prior['window']['end_exclusive'], 16)
assert rom[start-BASE:end-BASE].hex() == prior['window']['hex']

def word(pc):
    return int.from_bytes(rom[pc-BASE:pc-BASE+4], 'little')

def regs(w):
    return ((w >> 7) & 31, (w >> 15) & 31, (w >> 20) & 31)

# Independent ordinary instruction fields: one LW, same loaded rs1 for DIVU/REMU.
w = word(0xa0026464)
imm = w >> 20
imm = imm - 4096 if imm & 2048 else imm
assert w & 127 == 3 and (w >> 12) & 7 == 2
assert regs(w)[:2] == (15, 15)
assert (word(0xa0026460) & 0xfffff000) + imm == 0x62fc6c64
assert word(0xa0026468) == 0x3e800713
for pc, f3, expected_regs in [(0xa002646c, 5, (13, 15, 14)),
                              (0xa0026470, 7, (15, 15, 14)),
                              (0xa002647e, 0, (15, 15, 14))]:
    w = word(pc)
    assert w & 127 == 0x33 and w >> 25 == 1 and (w >> 12) & 7 == f3
    assert regs(w) == expected_regs
assert word(0xa0026474) == 0x000f4737
assert word(0xa0026478) == 0x24070713
assert 0xf4000 + 0x240 == 1000000

# Sparse ABI/store/return anchors, rather than another full-function export.
decoder = Cs(CS_ARCH_RISCV, CS_MODE_RISCV32 | CS_MODE_RISCVC)
anchors = []
for pc, size in [(0xa002645a, 6), (0xa002647c, 2), (0xa0026482, 10)]:
    raw = rom[pc-BASE:pc-BASE+size]
    ins = list(decoder.disasm(raw, pc))
    assert sum(i.size for i in ins) == size
    anchors.extend({'address': hex(i.address), 'hex': i.bytes.hex(),
                    'instruction': i.mnemonic + ' ' + i.op_str} for i in ins)
assert rom[0xa002647c-BASE:0xa002647e-BASE].hex() == '14c1'
assert rom[0xa0026482-BASE:0xa002648c-BASE].hex() == '5cc13244014541018280'

# Re-read only two candidate ranges; compare to retained H15 excerpts.
retained = json.loads((ROOT / 'analysis/clock-source-offset-h15-0041-20261024/candidate-excerpts.json').read_text())
selected = [(retained[0], 62, 87), (retained[3], 343, 351)]
source_checks = []
for item, first, last in selected:
    code = 'from pathlib import Path; import json; lines=Path(' + repr(item['path']) + ').read_text().splitlines(); print(json.dumps(lines[' + str(first-1) + ':' + str(last) + ']))'
    p = subprocess.run(['wsl.exe', '-d', 'Ubuntu-24.04', '--exec', 'python3', '-c', code], capture_output=True)
    assert p.returncode == 0, p.stderr.decode(errors='replace')
    current = json.loads(p.stdout)
    old = {}
    for excerpt in item['excerpts']:
        for line in excerpt['lines']:
            number, content = line.split(': ', 1)
            old[int(number)] = content
    assert current == [old[i] for i in range(first, last+1)]
    source_checks.append({'path': item['path'], 'first': first, 'last': last,
                          'matches_retained_h15': True})

result = {'passed': True, 'h15_window_matches_original': True,
          'independent_fields': ['LW32 address/rd/rs1', 'DIVU and REMU share saved load',
                                 '1000 divisor', '1000000 multiplier', 'MUL32'],
          'sparse_anchors': anchors, 'candidate_source_checks': source_checks,
          'accepted': 'caller-owned out+0/out+4; one U32 load; unsigned split; return 0',
          'units_status': 'seconds/nanoseconds shape only; milliseconds per input unit conditional',
          'unknown': ['counter writer/cadence/origin/epoch', 'offset writer', 'exact ROM source/version'],
          'new_functionality': 0, 'shared_rea_target_opened': False}
(HERE / 'static-review.json').write_text(json.dumps(result, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
print(json.dumps({'passed': True, 'sparse_anchors': len(anchors), 'source_ranges': len(source_checks), 'new_functionality': 0}))
