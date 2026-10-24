"""Read-only checks of retained OTA assembly and bounded original bytes; no target execution."""
import argparse
import hashlib
import json
from pathlib import Path

p = argparse.ArgumentParser()
p.add_argument('--source-root', type=Path, required=True)
args = p.parse_args()
rom = (args.source_root / 'roms/0041/ap01-1.0.2_0041.bin').read_bytes()
assert len(rom) == 6769704
assert hashlib.sha256(rom).hexdigest() == '972db4c136c7ed9e24a83c07c1a7fd62040ca018b08ca285216d26b1fee3c6b9'
records = json.loads((args.source_root / 'evidence/rea-0041-20261017/evidence/upper-complete.evidence.json').read_text(encoding='utf-8'))['records']
identities = {
    205: ('0xa01158f6', 'ev_a19c9b52372ecb98fa3751f092a2269b416466b6fc4a07098a49b6a982fab463'),
    185: ('0xa01148c4', 'ev_940624df09f090be66676c31a0efe6ef3e40b3e6f0380cb01487b1cf832b0db1'),
    271: ('0xa010f7e8', 'ev_d6be6dc0f8564f7784fce8fcf5e96cca1c44d0822ce88f84e70cc6b2e74a2c1d'),
    313: ('0xa0115b84', 'ev_fd8948808aaf2ff89b3ead54915929647356606d6f906795f366c1acd9570ecd'),
}
for n, (address, eid) in identities.items():
    r = records[n]
    assert r['evidence_id'] == eid
    assert r['normalized_result']['procedure']['address'] == address
    assert r['analysis_profile']['digest'] == '4825fb58a33a3e7d618557975b153b8318cf7e833d190ad16bcbf8bd441ae621'
for n, lines in {
    205: ['0xa0115a98: jal ra, 0xa010f7e8', '0xa0115b0a: jal ra, 0xa01148c4'],
    185: ['0xa01148f4: jal ra, 0xa0114790', '0xa011492e: sb zero, 0x50, s1', '0xa0114938: c.jalr a5', '0xa011490e: sw a0, 0x2b4, s1'],
    313: ['0xa0115c20: sw s8, 0x4c, s1', '0xa0115c24: sw s4, 0x8, s1'],
}.items():
    assert all(line in records[n]['normalized_result']['assembly'] for line in lines)
raw = json.loads(Path(__file__).with_name('raw-windows.json').read_text(encoding='utf-8'))
for window in raw['windows']:
    offset = int(window['address'], 16) - 0x9ffff000
    assert rom[offset:offset + window['length']].hex() == window['hex']
    if window['instructions']:
        assert ''.join(i['hex'] for i in window['instructions']) == window['hex']
for address, expected in {
    0xa011481c: '2388f404',  # state=2 before submit
    0xa0114846: '232024ed',  # URL pointer in stack descriptor
    0xa01148aa: '0325ca00',  # service from L+0xc
    0xa01148bc: 'efd00008',  # jal a012193c
}.items():
    offset = address - 0x9ffff000
    assert rom[offset:offset + 4].hex() == expected
assert rom[0xa056ba48 - 0x9ffff000:0xa056ba48 - 0x9ffff000 + 6] == b'https\0'
print('PASS: ROM identity; four retained record identities/profile; ABI/state/callback lines; 448 bounded original bytes and key submit words.')
