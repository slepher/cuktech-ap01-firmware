"""Independent Q10 review: reads ROM and retained evidence, never runs firmware."""
import hashlib
import json
from pathlib import Path

ROOT = Path('D:/Documents/PlatformIO/Projects/cuktech-ap01-firmware')
BASE = 0x9ffff000
rom = (ROOT / 'roms/0041/ap01-1.0.2_0041.bin').read_bytes()
assert len(rom) == 6769704
assert hashlib.sha256(rom).hexdigest() == '972db4c136c7ed9e24a83c07c1a7fd62040ca018b08ca285216d26b1fee3c6b9'
startup = json.loads((ROOT / 'reverse/analysis/buzzer-backlight-0041-20261023.json').read_text())['functions'][6]
inherited = json.loads((ROOT / 'reverse/analysis/weather-location-request-0041-20261023/retained-functions.json').read_text())['functions']
windows = []
for f, spans in [(startup, [(0xa005ac8c, 0xa005ac94), (0xa005acde, 0xa005ace2), (0xa005ad02, 0xa005ad06), (0xa005ae7c, 0xa005aec8), (0xa005b8a4, 0xa005b9ae)]),
                 (inherited[0], [(0xa00a0906, 0xa00a0ac2)]),
                 (inherited[2], [(0xa00aac5e, 0xa00aac8a), (0xa00aae04, 0xa00aae2c)])]:
    for start, end in spans:
        block = rom[start-BASE:end-BASE]
        retained = next(bytes.fromhex(r['hex'])[start-int(r['start'],16):end-int(r['start'],16)] for r in f['raw_ranges'] if int(r['start'],16) <= start and end <= int(r['start'],16)+len(bytes.fromhex(r['hex'])))
        assert block == retained
        windows.append({'start': hex(start), 'end_exclusive': hex(end), 'length': len(block), 'sha256': hashlib.sha256(block).hexdigest(), 'evidence_id': f['evidence_id'], 'assembly': [line for line in f['assembly'] if start <= int(line.split(':')[0],16) < end]})

def word(address):
    return int.from_bytes(rom[address-BASE:address-BASE+4], 'little')

def signed(value, bits):
    return value - ((value >> (bits-1)) << bits)

decoded = []
for address, target, kind in [(0xa005ae90, 0xa0060946, 'jal'), (0xa005aec4, 0xa0061848, 'jal'), (0xa005b8be, 0xa0060946, 'jal'), (0xa005b8d6, 0xa0060946, 'jal'), (0xa005b8ee, 0xa0060946, 'jal'), (0xa005b906, 0xa0060946, 'jal'), (0xa005b944, 0xa0061848, 'jal'), (0xa005ae96, 0xa005b8a4, 'beq'), (0xa005b90c, 0xa005b990, 'beq')]:
    w = word(address)
    if kind == 'jal':
        assert w & 0x7f == 0x6f and (w >> 7) & 31 == 1
        immediate = ((w >> 31) << 20) | (((w >> 12) & 255) << 12) | (((w >> 20) & 1) << 11) | (((w >> 21) & 1023) << 1)
        actual = address + signed(immediate, 21)
    else:
        assert w & 0x7f == 0x63 and (w >> 12) & 7 == 0
        assert (w >> 15) & 31 == 10 and (w >> 20) & 31 == 15
        immediate = ((w >> 31) << 12) | (((w >> 7) & 1) << 11) | (((w >> 25) & 63) << 5) | (((w >> 8) & 15) << 1)
        actual = address + signed(immediate, 13)
    assert actual == target
    decoded.append({'address': hex(address), 'word': hex(w), 'kind': kind, 'target': hex(actual)})
keys = {}
for address, expected in [(0xa01c3068, 'ck_config'), (0xa01c322c, 'bind_flag'), (0xa01c3250, 'loc_province'), (0xa01c3260, 'loc_city'), (0xa01c326c, 'loc_district'), (0xa01c327c, 'loc_id'), (0xa0265898, 'location_id')]:
    actual = rom[address-BASE:].split(b'\0',1)[0].decode('ascii')
    assert actual == expected
    keys[hex(address)] = actual
assert word(0xa005b930) == 0x0cfa2023
assert word(0xa005b988) == 0xfee78623
# URL rejection is BGEU(100000, legacy_id), hence acceptance is unsigned >.
assert word(0xa00aae16) & 0x707f == 0x7063
result = {'review': 'Q10 non-author static review', 'rom_sha256': hashlib.sha256(rom).hexdigest(), 'startup_bytes': sum(w['length'] for w in windows[:5]), 'windows': windows, 'decoded_direct_edges': decoded, 'keys': keys, 'result': 'PASS', 'limits': ['Configuration backend and object return semantics unverified', 'No text NUL or global scheduling guarantee', 'Getter rejected-fast-path a0 ABI unknown']}
Path(__file__).with_name('evidence.json').write_text(json.dumps(result, ensure_ascii=False, indent=2)+'\n', encoding='utf-8')
print('PASS: 358 startup bytes, inherited windows, 7 JAL, 2 BEQ, 7 strings')
