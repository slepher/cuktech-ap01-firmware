import json
from datetime import datetime, timezone
from pathlib import Path
from hashlib import sha256

OUT = Path(__file__).resolve().parent
ROOT = OUT.parents[2]
rom = ROOT / 'roms/0041/ap01-1.0.2_0041.bin'
metadata = json.loads((OUT / 'metadata-selection.json').read_text(encoding='utf-8'))
checks = []
with rom.open('rb') as stream:
    for path in sorted(OUT.glob('*.raw.json')):
        item = json.loads(path.read_text(encoding='utf-8'))
        stream.seek(item['file_offset'])
        actual = stream.read(item['length'])
        assert actual.hex() == item['bytes_hex'], path
        assert item['file_offset'] == int(item['address'],16)-0x9ffff000
        checks.append({'path': path.name, 'bytes': len(actual), 'window_sha256': sha256(actual).hexdigest(), 'matches_rom': True})
    strings = []
    for address, expected in [(0xa06276e4,b'mible_gatts_notify_or_indicate'),(0xa0561acc,b'mible_gattc_write_without_response'),(0xa0567d48,b'subsys/bluetooth/host/gatt.c')]:
        stream.seek(address-0x9ffff000)
        text = stream.read(128).split(b'\0')[0]
        assert text == expected
        strings.append({'address': hex(address), 'ascii': text.decode('ascii')})
for item in metadata:
    selected = json.loads((OUT/(item['address']+'.selected.json')).read_text(encoding='utf-8'))
    assert selected['evidence_id'] == item['evidence_id']
    assert selected['analysis_profile']['digest'] == item['profile']
    assert selected['normalized_result']['procedure']['address'] == item['address']
assert rom.stat().st_size == 6769704
end = datetime.now(timezone.utc)
start = datetime(2026,10,24,16,6,31,tzinfo=timezone.utc)
result = {'status': 'author static checks only; independent review pending', 'rom_size': rom.stat().st_size, 'whole_rom_digest': 'inherited; not recomputed', 'selected_records': len(metadata), 'raw_windows': checks, 'strings': strings, 'utc_start': start.isoformat(), 'utc_end': end.isoformat(), 'wall_seconds': (end-start).total_seconds(), 'tool_wait': {'separately_instrumented': False, 'visible_shell_command_wall_seconds_approx_before_validation': 34.6, 'session_check_seconds_approx': 4.8, 'note': 'Observed tool reply elapsed values only; not a complete wait trace and not active compute time. No queue/sleep interruption.'}, 'tokens': {'availability': 'parent collects actual usage; author does not estimate', 'input': None, 'cached': None, 'output': None}}
(OUT/'validation.json').write_text(json.dumps(result,ensure_ascii=False,indent=2),encoding='utf-8')
print(json.dumps({k:result[k] for k in ['status','selected_records','utc_start','utc_end','wall_seconds']},ensure_ascii=False))
