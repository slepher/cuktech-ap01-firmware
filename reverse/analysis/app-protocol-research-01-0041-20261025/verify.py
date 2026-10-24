"""Q11: bounded ROM/retained-evidence checks; never execute target code."""
import hashlib
import json
from pathlib import Path

ROOT = Path('D:/Documents/PlatformIO/Projects/cuktech-ap01-firmware')
HERE = Path(__file__).resolve().parent
BASE = 0x9ffff000
ROM = ROOT / 'roms/0041/ap01-1.0.2_0041.bin'
rom = ROM.read_bytes()
assert len(rom) == 6769704
assert hashlib.sha256(rom).hexdigest() == '972db4c136c7ed9e24a83c07c1a7fd62040ca018b08ca285216d26b1fee3c6b9'

def read(relative):
    return json.loads((ROOT / relative).read_text(encoding='utf-8-sig'))

def retained(number):
    path = f'evidence/rea-0041-20261017/evidence/whole-rom-private-20261023-{number}.json'
    record = read(path)['structuredContent']
    return path, record['evidence_id'], record['analysis_profile']['digest'], record['normalized_result']

sources = [retained('008'), retained('006')]
caller = read('reverse/analysis/miio-deferred-settings-0041-20261023/retained-functions.json')['functions'][1]
sources.append((caller['source']['path'], caller['evidence_id'], caller['profile']['digest'], caller['normalized_result']))
submit = read('reverse/rehost/charge-complete-0041.json')['records'][22]
sources.append(('reverse/rehost/charge-complete-0041.json#/records/22', submit['evidence_id'], None, submit))
windows = []
for path, eid, profile, result in sources:
    address = result['procedure']['address']
    rows = []
    for line in result['assembly']:
        pc = int(line.split(':')[0], 16)
        if address == '0xa009d8bc' and not 0xa009dd94 <= pc < 0xa009de14:
            continue
        off = pc - BASE
        size = 4 if rom[off] & 3 == 3 else 2
        raw = rom[off:off + size]
        row = dict(address=hex(pc), file_offset=off, hex=raw.hex(), retained_assembly=line.split(': ', 1)[1])
        w = int.from_bytes(raw, 'little')
        if size == 4 and w & 127 == 11 and (w >> 12) & 7 in (2, 3):
            row['vendor_extract'] = dict(signed=((w >> 12) & 7) == 2, msb=w >> 26, lsb=(w >> 20) & 63)
        rows.append(row)
    windows.append(dict(procedure=address, source=path, evidence_id=eid, profile_digest=profile,
                        body=result['procedure']['body'], instructions=rows))

idx = {int(r['address'], 16): r for w in windows for r in w['instructions']}
for pc, bit in [(0xa009c92a, 1), (0xa009c96a, 2), (0xa009c9aa, 3),
                (0xa009ca5a, 8), (0xa009ca9c, 9), (0xa009cadc, 10), (0xa009cb1c, 11),
                (0xa009c6c0, 3), (0xa009c6ec, 4), (0xa009c718, 5), (0xa009c744, 7)]:
    assert idx[pc]['vendor_extract'] == dict(signed=False, msb=bit, lsb=bit)
for pc, expected in [(0xa009c90c, 'sb '), (0xa009c946, 'sb '), (0xa009c986, 'sb '),
                     (0xa009c9c6, 'sb '), (0xa009ca82, 'sb '), (0xa009cab8, 'sb '),
                     (0xa009caf8, 'sb '), (0xa009cb38, 'sb '), (0xa009c784, 'sb ')]:
    assert idx[pc]['retained_assembly'].startswith(expected)
    w = int.from_bytes(bytes.fromhex(idx[pc]['hex']), 'little')
    assert w & 0x707f == 0x23  # SB rather than halfword/word store
for pc in [0xa009ddaa, 0xa009ddea]:
    w = int.from_bytes(bytes.fromhex(idx[pc]['hex']), 'little')
    imm = (w >> 31 << 20) | (((w >> 12) & 255) << 12) | (((w >> 20) & 1) << 11) | (((w >> 21) & 1023) << 1)
    if imm & (1 << 20):
        imm -= 1 << 21
    assert w & 127 == 0x6f and pc + imm == 0xa009c8a4
for pc in [0xa009ca14, 0xa009cb86]:
    hi = int.from_bytes(rom[pc-BASE:pc-BASE+4], 'little')
    lo = int.from_bytes(rom[pc-BASE+4:pc-BASE+8], 'little')
    upper = hi & 0xfffff000
    if upper & 0x80000000:
        upper -= 1 << 32
    lower = lo >> 20
    if lower & 0x800:
        lower -= 1 << 12
    assert hi & 127 == 0x17 and lo & 0x707f == 0x67
    assert (pc + upper + lower) & 0xffffffff == 0xa01b272c
for pc in [0xa009ddcc, 0xa009de0c]:
    w = int.from_bytes(bytes.fromhex(idx[pc]['hex']), 'little')
    assert w & 0x707f == 0x7013 and w >> 20 == 255
for window, size in zip(windows[:2], [824, 364]):
    rows = window['instructions']
    assert sum(len(bytes.fromhex(r['hex'])) for r in rows) == size
    for a, b in zip(rows, rows[1:]):
        assert int(a['address'], 16) + len(bytes.fromhex(a['hex'])) == int(b['address'], 16)

out = dict(rom=str(ROM), sha256=hashlib.sha256(rom).hexdigest(), base=hex(BASE), windows=windows,
           limits=['Static original bytes and retained Ghidra text only; no execution or model replay.',
                   'Vendor bit fields decoded from word encoding under retained ap01thead2 model; no new ISA provenance claim.',
                   'Only two full local bodies, selected caller branch and inherited submit; no global dispatcher coverage.'])
(HERE / 'instruction-evidence.json').write_text(json.dumps(out, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
print('PASS: ROM identity; 824/364 contiguous body byte coverage; 11 vendor extract fields; 9 SB widths; 2 caller JAL and 2 submit AUIPC/JALR targets; 2 notification ANDI255.')
