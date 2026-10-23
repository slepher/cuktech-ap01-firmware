"""B17 selected static review. Does not rerun the B16 ROM localization."""
from pathlib import Path
import ast
import json

HERE = Path(__file__).resolve().parent
TREE = HERE.parents[2]
SOURCE = Path('D:/Documents/PlatformIO/Projects/cuktech-ap01-firmware')
B16 = TREE / 'reverse/analysis/factory-active-reader-b16-0041-20261023'
BASE = 0x9ffff000
rom = (SOURCE / 'roms/0041/ap01-1.0.2_0041.bin').read_bytes()
rows = []

def raw(address, size, expected):
    data = rom[address-BASE:address-BASE+size]
    assert data.hex() == expected
    rows.append({'address': hex(address), 'offset': hex(address-BASE), 'hex': expected})
    return int.from_bytes(data, 'little')

for address in (0xa005b7b4, 0xa009f178):
    w = raw(address, 4, 'b797fc62')
    assert (w & 127, w >> 7 & 31, w & 0xfffff000) == (0x37, 15, 0x62fc9000)
w = raw(0xa005b7b8, 2, '0547')
assert (w & 3, w >> 13, w >> 7 & 31, (w >> 2 & 31) | (w >> 12 & 1) << 5) == (1, 2, 14, 1)
w = raw(0xa005b7ba, 4, '238ce72a')
assert (w & 127, w >> 12 & 7, w >> 15 & 31, w >> 20 & 31) == (0x23, 0, 15, 14)
assert ((w >> 25) << 5 | (w >> 7 & 31)) == 0x2b8
w = raw(0xa009f17c, 4, '83c7872b')
assert (w & 127, w >> 12 & 7, w >> 7 & 31, w >> 15 & 31, w >> 20) == (3, 4, 15, 15, 0x2b8)
w = raw(0xa009f180, 4, '6383071c')
imm = (w >> 31) << 12 | (w >> 7 & 1) << 11 | (w >> 25 & 63) << 5 | (w >> 8 & 15) << 1
if imm & 0x1000:
    imm -= 0x2000
assert (w & 127, w >> 12 & 7, w >> 15 & 31, w >> 20 & 31, 0xa009f180 + imm) == (0x63, 0, 15, 0, 0xa009f346)
assert raw(0xa009f346, 2, '8280') == 0x8082
old = json.loads((TREE / 'reverse/analysis/factory-test-0041-20261023/instruction-windows.json').read_text())['windows'][0]
start, end = int(old['start'], 16), int(old['end_exclusive'], 16)
assert bytes.fromhex(old['hex']) == rom[start-BASE:end-BASE]
assert end-start == 464
assert rom[0x1bee24:0x1bee2c] == b'-rom1fs-'

# Inspect the producer's AST without executing its global scan or output writes.
tree = ast.parse((B16 / 'locate.py').read_text())
outer = next(n for n in tree.body if isinstance(n, ast.For))
assert ast.unparse(outer.iter) == 'range(0, 1830436, 2)'
inner = next(n for n in outer.body if isinstance(n, ast.For))
assert ast.unparse(inner.iter) == 'range(off + 4, min(off + 68, 1830436), 2)'
tests = [ast.unparse(n.test) for n in inner.body if isinstance(n, ast.If)]
assert tests == ['op in (3, 19) and v >> 15 & 31 == rd and (v >> 20 == 696)', 'op == 35 and v >> 15 & 31 == rd and (v >> 25 << 5 | v >> 7 & 31 == 696)']
loc = json.loads((B16 / 'localization.json').read_text())
assert [(r['lui'], r['candidate'], r['hex'], r['kind']) for r in loc['candidates']] == [('0xa005b7b4', '0xa005b7ba', '238ce72a', 'store'), ('0xa009f178', '0xa009f17c', '83c7872b', 'load')]

def pointer(obj, path):
    for part in path.split('/')[1:]:
        part = part.replace('~1', '/').replace('~0', '~')
        obj = obj[int(part)] if isinstance(obj, list) else obj[part]
    return obj

groups = json.loads((B16 / 'retained-reference-hits.json').read_text())['groups']
backrefs = []
selected = 0
for group in groups:
    original = json.loads((SOURCE / 'evidence/rea-0041-20261017' / group['source']).read_text(encoding='utf-8'))
    for hit in group['selected_hits']:
        text = pointer(original, hit['json_pointer'])
        assert isinstance(text, str) and hit['excerpt'] in text and '62fc92b8' in text
        selected += 1
        if '/outgoing_references/' in hit['json_pointer']:
            parent = pointer(original, hit['json_pointer'].rsplit('/', 1)[0])
            assert parent['source_address'] == '0xa005b7ba' and parent['target_address'] == '0x62fc92b8'
            assert parent['kind']['type'] == 'WRITE' and parent['kind']['write'] is True and parent['kind']['read'] is False
            backrefs.append({'source': group['source'], 'pointer': hit['json_pointer'], 'edge': '0xa005b7ba -> 0x62fc92b8 WRITE'})
        # Verify the enclosing retained procedure instead of trusting B16's label.
        if hit['json_pointer'].startswith('/records/'):
            record = pointer(original, '/'.join(hit['json_pointer'].split('/')[:3]))
            assert '0xa005a736' in json.dumps(record.get('input', record.get('arguments', {}))) or '0xa005a736' in json.dumps(record.get('normalized_result', {}))
    assert group['procedure'] == '0xa005a736'
out = {'status': 'passed', 'method': 'selected raw instruction bitfields, AST-only producer inspection, saved JSON-pointer backreferences; no localization rerun or broader scan', 'raw_instruction_count': len(rows), 'raw_byte_count': sum(len(r['hex'])//2 for r in rows), 'instructions': rows, 'retained_callback_bytes': 464, 'selected_pointer_count': selected, 'exact_target_backrefs': backrefs, 'detector_tests': tests, 'romfs_magic_offset': '0x1bee24', 'external_reader': 'unknown', 'unverified': ['global absence/completeness of retained literal hits', 'aliases/indirect/wide reads and constructions outside B16 detector', 'external reader ABI and business contract', 'source version/vendor modification']}
(HERE / 'review-index.json').write_text(json.dumps(out, indent=2) + '\n')
print(f'PASS: {len(rows)} instructions / 24B, 464B retained callback, {selected} saved pointers / {len(backrefs)} WRITE backreferences; AST inspected, no scan rerun')
