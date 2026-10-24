"""Independent, bounded Q05 evidence and original-byte checks; no author imports."""
import json
from pathlib import Path
from datetime import datetime, timezone
import capstone

ROOT = Path(__file__).resolve().parents[3]
AUTHOR = ROOT / 'reverse/analysis/app-ble-research-01-0041-20261025'
OUT = Path(__file__).resolve().parent
def read(path):
    return json.loads(path.read_text(encoding='utf-8'))

index = read(AUTHOR / 'metadata-selection.json')
records = read(ROOT / index[0]['bundle'])['records']
checks = []
for item in index:
    original = records[item['ordinal']]
    selected = read(AUTHOR / (item['address'] + '.selected.json'))
    assert original['evidence_id'] == selected['evidence_id'] == item['evidence_id']
    assert original['analysis_profile']['digest'] == selected['analysis_profile']['digest'] == item['profile']
    assert original['subject']['digest']['sha256'] == '972db4c136c7ed9e24a83c07c1a7fd62040ca018b08ca285216d26b1fee3c6b9'
    for key, value in selected['normalized_result'].items():
        assert original['normalized_result'][key] == value, (item['address'], key)
    assert original['parameters']['procedure'] == item['address']
    checks.append(dict(item, original_selected_fields_equal=True))

rom = ROOT / 'roms/0041/ap01-1.0.2_0041.bin'
assert rom.stat().st_size == 6769704
raw_checks = []
with rom.open('rb') as f:
    for path in sorted(AUTHOR.glob('*.raw.json')):
        j = read(path)
        offset = int(j['address'], 16) - 0x9ffff000
        assert offset == j['file_offset']
        f.seek(offset)
        data = f.read(j['length'])
        assert data.hex() == j['bytes_hex'], path.name
        raw_checks.append({'path': path.name, 'va': j['address'], 'length': len(data), 'matches_original': True})
    strings = []
    for va in (0xa06276e4, 0xa0561acc, 0xa0567d48):
        f.seek(va - 0x9ffff000)
        strings.append({'va': hex(va), 'value': f.read(96).split(b'\0')[0].decode('ascii')})
    # Sparse, ordinary-instruction windows only. No whole-ROM scans or model execution.
    decoder = capstone.Cs(capstone.CS_ARCH_RISCV, capstone.CS_MODE_RISCV32 | capstone.CS_MODE_RISCVC)
    windows = []
    for va, size in [(0xa012518e, 62), (0xa0125214, 40), (0xa0125268, 24),
                     (0xa012b62a, 12), (0xa012800a, 4), (0xa012802a, 4),
                     (0xa0128076, 18), (0xa01280e0, 16), (0xa0128100, 16),
                     (0xa0128124, 16), (0xa0128148, 16), (0xa0128174, 16)]:
        f.seek(va - 0x9ffff000)
        data = f.read(size)
        windows.append({'va': hex(va), 'bytes': data.hex(), 'listing': [f'{i.address:08x}: {i.bytes.hex()} {i.mnemonic} {i.op_str}' for i in decoder.disasm(data, va)]})

old = read(ROOT / 'evidence/rea-0041-20261017/evidence/mible-recovered.json')
legacy_records = read(ROOT / 'evidence/rea-0041-20261017/evidence/roots-0041.evidence.json')['records']
legacy_gateway = next(r for r in legacy_records if r.get('parameters', {}).get('procedure') == '0xa012b0a2')
assert legacy_gateway['evidence_id'] == 'ev_2b42593ea4fc9f44bd2b1b7210a9e1582b4d8c37da351bd3ac129b3ffc2c78bf'
assert legacy_gateway['subject']['digest']['sha256'] == '972db4c136c7ed9e24a83c07c1a7fd62040ca018b08ca285216d26b1fee3c6b9'
result = {'scope': 'Q05 independent local evidence/ROM verification only',
          'utc_start': '2026-10-24T16:16:14Z', 'utc_check_end': datetime.now(timezone.utc).isoformat(),
          'rom_size': rom.stat().st_size, 'whole_rom_hash': 'inherited, not recomputed',
          'selected_original_checks': checks, 'raw_original_checks': raw_checks,
          'source_strings': strings, 'independent_sparse_windows': windows,
          'old_sources': old['sources'], 'old_validation_flags_inherited_only': old['validation'],
          'legacy_gateway': {k: legacy_gateway[k] for k in ('evidence_id', 'analysis_profile', 'subject', 'confidence')},
          'legacy_gateway_assembly_anchor': [s for s in legacy_gateway['normalized_result']['assembly'] if '0xa012b62' in s],
          'legacy_gateway_unresolved_calls': legacy_gateway['normalized_result']['unresolved_calls'],
          'old_boundary_exclusions_preserved': old['decompiler_boundary_exclusions'],
          'tokens': 'parent measures actual usage; no local estimate',
          'waits': 'No queue/sleep interruption; tool response wall times are not active compute time.'}
(OUT / 'checks.json').write_text(json.dumps(result, indent=2, ensure_ascii=False) + '\n', encoding='utf-8')
print(json.dumps({'selected_records': len(checks), 'raw_windows': len(raw_checks), 'sparse_windows': len(windows), 'end': result['utc_check_end']}))
