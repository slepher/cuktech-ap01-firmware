"""Independent byte checks only; never imports or executes the author verifier."""
import hashlib
import json
from pathlib import Path
import sys

project, evidence = map(Path, sys.argv[1:3])
rom = (project / 'roms/0041/ap01-1.0.2_0041.bin').read_bytes()
assert len(rom) == 6769704
assert hashlib.sha256(rom).hexdigest() == '972db4c136c7ed9e24a83c07c1a7fd62040ca018b08ca285216d26b1fee3c6b9'
base = 0x9ffff000
source = json.loads((evidence / 'windows.json').read_text())
expected = [(0xa0116900, 0xa0116a3a), (0xa0116a3a, 0xa0116ad0), (0xa011c3b0, 0xa011c514)]
assert len(source['windows']) == 3
count = total = 0
for w, (start, stop) in zip(source['windows'], expected):
    assert int(w['start'], 16) == start and int(w['end_exclusive'], 16) == stop
    actual = rom[start-base:stop-base]
    assert actual == bytes.fromhex(w['hex'])
    assert hashlib.sha256(actual).hexdigest() == w['sha256']
    cursor = start
    for instruction in w['instructions']:
        assert int(instruction['address'], 16) == cursor
        raw = bytes.fromhex(instruction['bytes'])
        width = 4 if rom[cursor-base] & 3 == 3 else 2
        assert len(raw) == width and raw == rom[cursor-base:cursor-base+width]
        cursor += width
        count += 1
    assert cursor == stop
    total += len(actual)
assert (total, count) == (820, 281)

# Build the signed J immediate in bit order independently of mnemonic strings.
edges = [(0xa0116a9a, 0xa011c3b0), (0xa0116aa4, 0xa005f3d8),
         (0xa0116ab0, 0xa0116900), (0xa0116aba, 0xa01b3c8c),
         (0xa011c3c8, 0xa0110984), (0xa011c4cc, 0xa011c0da)]
for pc, target in edges:
    word = int.from_bytes(rom[pc-base:pc-base+4], 'little')
    assert word & 0x7f == 0x6f and (word >> 7) & 31 == 1
    bits = f'{word:032b}'
    immediate = int(bits[0] + bits[12:20] + bits[11] + bits[1:11] + '0', 2)
    if bits[0] == '1':
        immediate -= 1 << 21
    assert pc + immediate == target
word = int.from_bytes(rom[0xa0116a0c-base:0xa0116a10-base], 'little')
assert word == 0x00a7d00b
assert [word & 127, word >> 7 & 31, word >> 12 & 7, word >> 15 & 31,
        word >> 20 & 31, word >> 25 & 3, word >> 27] == [11, 0, 5, 15, 10, 0, 0]
for address, value in [(0xa0565828, b'props\0'), (0xa056c058, b'method\0')]:
    assert rom[address-base:address-base+len(value)] == value
record = json.loads((evidence / 'root-record-256.json').read_text())
profile = json.loads((evidence / 'root-profile.json').read_text())
assert record['evidence_id'] == profile['evidence_id'] == 'ev_cae45a84ae40a1571e17792b4854ee16d8f5d44a3f6fe046f24ad031b85410da'
assert record['analysis_profile']['digest'] == profile['analysis_profile']['digest'] == '4825fb58a33a3e7d618557975b153b8318cf7e833d190ad16bcbf8bd441ae621'
result = dict(body_bytes=total, instructions=count, jal_edges=6, vendor_words=1,
              strings=2, result='PASS', firmware_executed=False,
              limits='Byte verification plus manual semantic review; no downstream ownership proof.')
(Path(__file__).parent / 'checks.json').write_text(json.dumps(result, indent=2)+'\n')
print(json.dumps(result))
