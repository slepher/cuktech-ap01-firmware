"""Independent Q11 static word checks. Does not import author code or run ROM."""
import hashlib
import json
from pathlib import Path

ROOT = Path('D:/Documents/PlatformIO/Projects/cuktech-ap01-firmware')
OUT = Path(__file__).resolve().parent
BASE = 0x9ffff000
rom = (ROOT / 'roms/0041/ap01-1.0.2_0041.bin').read_bytes()
assert len(rom) == 6769704
assert hashlib.sha256(rom).hexdigest() == '972db4c136c7ed9e24a83c07c1a7fd62040ca018b08ca285216d26b1fee3c6b9'
rows = []
def word(pc):
    b = rom[pc-BASE:pc-BASE+4]
    rows.append({'va': hex(pc), 'offset': pc-BASE, 'bytes': b.hex()})
    return int.from_bytes(b, 'little')

def signed(n, bits):
    return n - (1 << bits) if n & (1 << (bits-1)) else n

def jal(pc, target):
    w = word(pc)
    imm = ((w >> 31) << 20) | (((w >> 12) & 255) << 12) | (((w >> 20) & 1) << 11) | (((w >> 21) & 1023) << 1)
    assert w & 127 == 0x6f and pc + signed(imm, 21) == target

def pair(pc, target):
    a, b = word(pc), word(pc+4)
    assert a & 127 == 0x17 and b & 0x707f == 0x67
    assert ((pc + signed(a & 0xfffff000, 32) + signed(b >> 20, 12)) & 0xffffffff) == target

sources = []
for suffix, expected in [('008', 824), ('006', 364)]:
    p = ROOT / f'evidence/rea-0041-20261017/evidence/whole-rom-private-20261023-{suffix}.json'
    d = json.loads(p.read_text(encoding='utf-8-sig'))['structuredContent']
    assert d['analysis_profile']['digest'] == 'b6368dd18431e8113aa5026c713d41e648ab0f6ddd9421ff6c4a49e23b3cd2f3'
    f = d['normalized_result']
    pcs = [int(x.split(':')[0],16) for x in f['assembly']]
    ends = [pc + (4 if rom[pc-BASE] & 3 == 3 else 2) for pc in pcs]
    assert ends[:-1] == pcs[1:] and ends[-1] - pcs[0] == expected
    assert f['procedure']['body']['total_bytes'] == expected
    sources.append({'path': str(p), 'evidence_id': d['evidence_id'], 'bytes': expected})

# Fields omitted by retained assembly text: check all compared cache bits as well.
for pc, bit in [(0xa009c8f0,7),(0xa009c92a,1),(0xa009c92e,6),(0xa009c96a,2),(0xa009c96e,5),(0xa009c9aa,3),(0xa009c9ae,4),(0xa009ca5a,8),(0xa009ca62,7),(0xa009ca9c,9),(0xa009caa0,6),(0xa009cadc,10),(0xa009cae0,5),(0xa009cb1c,11),(0xa009cb20,4),(0xa009c6c0,3),(0xa009c6c4,7),(0xa009c6ec,4),(0xa009c6f0,6),(0xa009c718,5),(0xa009c71c,5),(0xa009c744,7),(0xa009c748,4)]:
    w = word(pc)
    assert w & 0x707f == 0x300b and w >> 26 == bit and (w >> 20) & 63 == bit
for pc in [0xa009c9e6,0xa009cb58]:
    w = word(pc)
    assert w & 0x707f == 0x200b and w >> 26 == 7 and (w >> 20) & 63 == 0
for pc, offset in [(0xa009c90c,0),(0xa009c946,0),(0xa009c986,0),(0xa009c9c6,0),(0xa009ca82,4),(0xa009cab8,4),(0xa009caf8,4),(0xa009cb38,4),(0xa009c784,2)]:
    w = word(pc)
    assert w & 0x707f == 0x23 and (((w >> 25) << 5) | ((w >> 7) & 31)) == offset
for pc in [0xa009ddcc,0xa009de0c]:
    w = word(pc)
    assert w & 0x707f == 0x7013 and w >> 20 == 255
for pc, offset in [(0xa009dda6,-24),(0xa009dde6,-20)]:
    w = word(pc)
    assert w & 0x707f == 0x2023
    assert signed(((w >> 25) << 5) | ((w >> 7) & 31),12) == offset
for pc in [0xa009ddaa,0xa009ddea]:
    jal(pc,0xa009c8a4)
jal(0xa009c8b8,0xa009c662)
jal(0xa009ddd4,0xa0195144)
pair(0xa009ca14,0xa01b272c)
pair(0xa009cb86,0xa01b272c)
pair(0xa01b273c,0xa00a53c0)
pair(0xa01b27aa,0xa00a533a)
jal(0xa01b27d0,0xa01951e2)
(OUT / 'checked-words.json').write_text(json.dumps({'sources':sources,'checks':rows,'limit':'Static original words; retained vendor profile semantics inherited, no firmware execution.'},indent=2)+'\n',encoding='utf-8')
print('PASS: body coverage 824/364; 23 unsigned/2 signed extraction fields; 9 SB offsets; 2 full-word mirrors; low-byte notifications; 9 direct call targets.')
