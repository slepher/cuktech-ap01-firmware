"""A41: bounded static replacement checks; does not execute firmware."""
from pathlib import Path
import json
import sys

OUT = Path(__file__).resolve().parent
TREE = OUT.parents[2]
MAIN = Path('D:/Documents/PlatformIO/Projects/cuktech-ap01-firmware')
sys.path.insert(0, str(TREE/'reverse/analysis/display-event-flow-g05-0041-20261023'))
import read_rom as rr

rows = list(rr.rows(0xa00ed802, 0xa00ed830))
D = {int(r['pc'], 16): r for r in rows}
checks = []
for pc, asm in {
    0xa00ed802: 'lw s2, 0x5c(a0)',
    0xa00ed806: 'c.mv s1, a0',
    0xa00ed808: 'c.mv s3, a1',
    0xa00ed816: 'lbu a5, 0x10(s2)',
    0xa00ed81a: 'c.beqz a5, 8',
    0xa00ed81c: 'c.mv a0, s2',
    0xa00ed822: 'c.mv a0, s2',
    0xa00ed828: 'sw zero, 0x5c(s1)',
    0xa00ed82c: 'sw zero, 0x74(s1)',
}.items():
    assert D[pc]['asm'] == asm, (hex(pc), D[pc])
    checks.append(dict(pc=hex(pc), asm=asm))

def sx(v, bits):
    return v-(1 << bits) if v & (1 << (bits-1)) else v

def word(pc):
    return int.from_bytes(rr.rom[pc-rr.BASE:pc-rr.BASE+4], 'little')

# Decode the direct call targets independently of the display helper.
for pc, target in [(0xa00ed80e, 0xa00eaa50), (0xa00ed812, 0xa00890e8),
                   (0xa00ed81e, 0xa01b2e3a), (0xa00ed824, 0xa008ab8a)]:
    w = word(pc)
    imm = ((w >> 31) << 20) | (((w >> 12) & 255) << 12) | (((w >> 20) & 1) << 11) | (((w >> 21) & 1023) << 1)
    assert w & 127 == 0x6f and (w >> 7) & 31 == 1
    assert pc + sx(imm, 21) == target
    checks.append(dict(pc=hex(pc), target=hex(target)))

w = word(0xa00ed80a)
bimm = ((w >> 31) << 12) | (((w >> 7) & 1) << 11) | (((w >> 25) & 63) << 5) | (((w >> 8) & 15) << 1)
assert (w & 127, (w >> 12) & 7, (w >> 15) & 31, (w >> 20) & 31) == (99, 0, 18, 0)
assert 0xa00ed80a + sx(bimm, 13) == 0xa00ed830
checks.append(dict(pc='0xa00ed80a', semantics='old O == 0 skips teardown and both clears to a00ed830'))

c = word(0xa00ed81a) & 65535
cimm = (((c >> 12) & 1) << 8) | (((c >> 10) & 3) << 3) | (((c >> 5) & 3) << 6) | (((c >> 3) & 3) << 1) | (((c >> 2) & 1) << 5)
assert c & 3 == 1 and c >> 13 == 6 and ((c >> 7) & 7)+8 == 15
assert 0xa00ed81a + sx(cimm, 9) == 0xa00ed822
checks.append(dict(pc='0xa00ed81a', semantics='mode byte == 0 skips a01b2e3a and reaches free(O)'))

# Independent I/S field checks preserve byte read and word stores/order.
w = word(0xa00ed816)
assert (w & 127, (w >> 12) & 7, (w >> 7) & 31, (w >> 15) & 31, w >> 20) == (3, 4, 15, 18, 16)
for pc, offset in [(0xa00ed828, 0x5c), (0xa00ed82c, 0x74)]:
    w = word(pc)
    assert (w & 127, (w >> 12) & 7, (w >> 15) & 31, (w >> 20) & 31) == (35, 2, 9, 0)
    assert ((w >> 25) << 5) | ((w >> 7) & 31) == offset

reuse = []
for p in sorted((MAIN/'reverse/rehost').glob('*.json')):
    text = p.read_text(encoding='utf8', errors='replace').lower()
    hits = [term for term in ['a00ed7f4', 'a00ed816', 'a01b2e3a'] if term in text]
    if hits:
        reuse.append(dict(file=p.name, terms=hits))
result = dict(status='PASS', static_only=True, baseline='2844cc4', rows=rows,
              checks=checks, reuse_search=dict(boundary='main reverse/rehost/*.json including complete and late round3; address text search only', hits=reuse),
              inherited=['A29/A31 old-source cache invalidation', 'A33/A35 memory reader mode0', 'A37/A39 O single allocation and derived +658', 'C03/C04 a008ab8a free wrapper'],
              limits='Only old nonnull ROM-memory O normal replacement. No mode1 close internals, allocator internals, object DELETE caller, runtime or resource decode.')
(OUT/'evidence.json').write_text(json.dumps(result, ensure_ascii=False, indent=2)+'\n', encoding='utf8')
print(json.dumps(dict(status='PASS', checks=len(checks), sparse_window='a00ed802..a00ed82f', new_functionality='normal old-O teardown/clear connection')))
