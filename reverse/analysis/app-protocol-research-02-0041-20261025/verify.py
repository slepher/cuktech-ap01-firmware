"""Read-only byte/encoding checks; does not execute firmware or a behavior model."""
from pathlib import Path
import hashlib
import json

ROOT = Path('D:/Documents/PlatformIO/Projects/cuktech-ap01-firmware')
OUT = Path(__file__).parent
BASE = 0x9ffff000
rom = (ROOT / 'roms/0041/ap01-1.0.2_0041.bin').read_bytes()
assert len(rom) == 6769704
assert hashlib.sha256(rom).hexdigest() == '972db4c136c7ed9e24a83c07c1a7fd62040ca018b08ca285216d26b1fee3c6b9'
src = ROOT / 'reverse/analysis/uart-response-0041-20261023.json'
f = json.loads(src.read_text(encoding='utf-8'))['functions'][0]
assert f['evidence_id'] == 'ev_6f9f82e5daf0540a1c24a0b85daa2e394785391692765e5e3e100eb7b37ed94c'
assert f['profile_digest'] == 'bcefdee5092076e55636e077b45523e203f4b870ae7b7ab547945ed1b8162279'
r = f['raw_ranges'][0]
raw = bytes.fromhex(r['hex'])
off = int(r['start'], 16) - BASE
assert rom[off:off+len(raw)] == raw
assert hashlib.sha256(raw).hexdigest() == r['sha256']
assembly = f['normalized_result']['assembly']
rows = []
for i, line in enumerate(assembly):
    va = int(line.split(':')[0], 16)
    if 0xa00a874e <= va < 0xa00a875a or 0xa00a973e <= va < 0xa00a983e:
        end = int(assembly[i+1].split(':')[0], 16)
        b = rom[va-BASE:end-BASE]
        assert len(b) == (4 if int.from_bytes(b[:2], 'little') & 3 == 3 else 2)
        rows.append(dict(va=hex(va), offset=va-BASE, hex=b.hex(), assembly=line))
def word(va):
    return int.from_bytes(rom[va-BASE:va-BASE+4], 'little')
custom = []
for va, funct3, top, rd, rs1, rs2 in [
    (0xa00a97bc, 4, 16, 16, 18, 23),
    (0xa00a97f4, 4, 16, 16, 25, 23),
    (0xa00a9828, 5, 8, 17, 22, 21),
]:
    w = word(va)
    fields = [w & 127, (w>>12)&7, w>>27, (w>>7)&31, (w>>15)&31, (w>>20)&31]
    assert fields == [11, funct3, top, rd, rs1, rs2], (hex(va), fields)
    custom.append(dict(va=hex(va), word=hex(w), fields=fields, shift=(w>>25)&3))
assert [x['shift'] for x in custom] == [3, 3, 0]
for va, offset in [(0xa00a97ce, 0x14), (0xa00a9800, 0x15)]:
    w = word(va)
    imm = ((w>>25)<<5) | ((w>>7)&31)
    assert (w&127, (w>>12)&7, (w>>15)&31, (w>>20)&31, imm) == (35, 0, 6, 16, offset)
for va, target in [(0xa00a975c, 0xa0191652), (0xa00a9792, 0xa0191746), (0xa00a9830, 0xa00a389c)]:
    w = word(va)
    imm = ((w>>31)<<20) | (((w>>12)&255)<<12) | (((w>>20)&1)<<11) | (((w>>21)&1023)<<1)
    if imm & (1<<20): imm -= 1<<21
    assert w&127 == 111 and va+imm == target
result = dict(source=str(src), pointer='/functions/0/normalized_result', evidence_id=f['evidence_id'], profile_digest=f['profile_digest'], full_body_raw_match=True, instructions=rows, custom_fields=custom)
(OUT / 'instruction-evidence.json').write_text(json.dumps(result, ensure_ascii=False, indent=2)+'\n', encoding='utf-8')
print(f'PASS ROM identity, full retained raw body, {len(rows)} instruction boundaries, 3 indexed encodings, 2 SB fields, 3 JAL targets')
