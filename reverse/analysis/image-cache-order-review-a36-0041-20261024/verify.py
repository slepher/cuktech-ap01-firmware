"""A36 independent sparse static review; reads ROM, never executes target."""
from pathlib import Path
import json
import capstone

HERE = Path(__file__).resolve().parent
ROM = Path('D:/Documents/PlatformIO/Projects/cuktech-ap01-firmware/roms/0041/ap01-1.0.2_0041.bin')
data = ROM.read_bytes()
cs = capstone.Cs(capstone.CS_ARCH_RISCV, capstone.CS_MODE_RISCV32 | capstone.CS_MODE_RISCVC)
rows = []

def read(a, n):
    off = a - 0x9ffff000
    assert 0 <= off <= len(data) - n
    return data[off:off+n]

def anchor(a, expected, why):
    raw = bytes.fromhex(expected)
    assert read(a, len(raw)) == raw, hex(a)
    ins = list(cs.disasm(raw, a))
    rows.append(dict(address=hex(a), bytes=expected, meaning=why,
                     decoded=[i.mnemonic + ' ' + i.op_str for i in ins]))

for a, b, why in [
    (0xa0263b08, 'c0b90ea0', 'default backend+0c lookup'),
    (0xa00f0dec, '91479cd8', 'link offset is four'),
    (0xa00f0df8, '23aa040223ac0402', 'head and tail initially zero'),
    (0xa0089ce0, '81c51c41', 'prev setter null gate then reread descriptor offset'),
    (0xa0089cf4, '81c51c41be95d0c1', 'next setter null gate and offset+4 store'),
    (0xa008aecc, 'aa8408412105', 'save descriptor and allocate offset+8'),
    (0xa008aed6, '2a891dc5', 'save allocated node then null gate'),
    (0xa008aeda, 'aa8501462685', 'set prev(new) to zero'),
    (0xa008aee4, 'd040ca852685', 'read head for next(new)'),
    (0xa008aeee, 'cc4089c54a862685', 'reread head after setter for prev(old head)'),
    (0xa008aefa, '9c4423a2240199e323a42401', 'read tail then write head and conditional tail'),
    (0xa00ebdf8, '13050903', 'list argument is cache+30'),
    (0xa00ebe00, '2326a4fc21ed', 'save new node and successful nonnull gate'),
    (0xa00ebe5c, '1146930584fc', 'copy four bytes from saved tree node'),
    (0xa00ebe66, '032784fc8327c9021146084bf1179305c4fc3e95', 'reload tree, allocation length and payload; backlink source saved new node'),
    (0xa00eba54, '5c592a899de3', 'read head and save cache; nonempty fast path'),
    (0xa00eba7e, '9c43032a4500844b', 'head to tree to payload, cache header offset'),
    (0xa00eba8c, '1c492685d294829779f1', 'comparator call; nonzero falls back to search'),
    (0xa00eba64, 'aa840de9', 'save search result and test nonnull'),
    (0xa00eba98, '1c490327c902832a4903ba9783a9c7ff', 'tree payload, current head and payload tail backlink'),
    (0xa00ebaa8, '638c590563800a0683270903', 'already head bypass; otherwise load link offset'),
    (0xa00ebab8, '63846905130a0903', 'hit equals predecessor bypass; descriptor cache+30'),
    (0xa00ebac8, '4e86da855285', 'set next(saved predecessor,hit)'),
    (0xa00ebad2, '5a86ce855285', 'set prev(hit,saved predecessor)'),
    (0xa00ebadc, '4e86d6855285', 'set prev(saved head,hit)'),
    (0xa00ebae6, '5686ce855285', 'set next(hit,saved head)'),
    (0xa00ebaf0, '63940a00232c390363140b00232a3903', 'conditional endpoint stores'),
    (0xa00ebb00, '844883274900c9d0be94', 'reread tree payload and cache header offset before return'),
    (0xa0089d10, '54411841aa84ae876390d502', 'unlink loads descriptor head and offset; compares node'),
    (0xa0089d1c, 'b387e500cc4301464cc1a1e523240500', 'unlink head advances to next; empty clears tail'),
    (0xa0089d38, '1445', 'unlink reads tail before indexed prev load'),
    (0xa0089d3e, '639bd7000cc581e523220500', 'unlink tail writes prev and handles empty'),
    (0xa0089d54, 'ba9703a947002326b4fe4a86', 'middle unlink reads next, saves prev'),
    (0xa0089d64, '8325c4fe26852e86ca85', 'reload saved prev before set_prev(next,prev)'),
    (0xa00ebf40, 'd8541c495285ba9783a9c7ff', 'removal uses same payload tail backlink'),
    (0xa00ebf50, '13850403ce85', 'removal unlink(cache+30,node)'),
    (0xa00ebf5a, '4e85', 'node free caller argument'),
    (0xa00ec236, '03298503aa89631b0900', 'victim begins tail and tests node'),
    (0xa00ec252, '83270900844b83a74900', 'victim node to tree to payload, then cache offset'),
    (0xa00ec26a, '61dd83a70903', 'zero ref returns entry; nonzero reloads offset'),
]:
    anchor(a, b, why)

targets = []
for a, target in [
    (0xa008aee0,0xa0089cda),(0xa008aeea,0xa0089cee),(0xa008aef6,0xa0089cda),
    (0xa00ebdfc,0xa008aec0),(0xa00ebe62,0xa008ab76),(0xa00ebe7a,0xa008ab76),
    (0xa00eba60,0xa00ea832),(0xa00ebac4,0xa0089d02),(0xa00ebace,0xa0089cee),
    (0xa00ebad8,0xa0089cda),(0xa00ebae2,0xa0089cda),(0xa00ebaec,0xa0089cee),
    (0xa0089d60,0xa0089cee),(0xa0089d6e,0xa0089cda),
    (0xa00ebf56,0xa0089d02),(0xa00ebf5c,0xa008ab8a),(0xa00ec266,0xa008b604),
]:
    w = int.from_bytes(read(a,4),'little')
    delta = ((w >> 31) << 20) | (((w >> 12) & 255) << 12) | (((w >> 20) & 1) << 11) | (((w >> 21) & 1023) << 1)
    if delta & 0x100000: delta -= 0x200000
    assert w & 127 == 0x6f and (w >> 7) & 31 == 1
    assert (a + delta) & 0xffffffff == target
    targets.append(dict(address=hex(a),bytes=read(a,4).hex(),target=hex(target)))

vendors = []
for a, expected in [
    (0xa0089ce4,[11,5,8,12,11,15,0]),
    (0xa0089d3a,[11,4,8,11,11,14,0]),
    (0xa00ebab4,[11,4,8,22,21,15,0]),
    (0xa00ec270,[11,4,8,18,18,15,0]),
]:
    w = int.from_bytes(read(a,4),'little')
    fields = [w & 127,(w >> 12) & 7,w >> 27,(w >> 7) & 31,(w >> 15) & 31,(w >> 20) & 31,(w >> 25) & 3]
    assert fields == expected
    vendors.append(dict(address=hex(a),bytes=read(a,4).hex(),fields=fields))

summary = dict(result='passed',static_only=True,anchors=len(rows),direct_calls=len(targets),vendor_words=len(vendors),anchor_bytes=sum(len(bytes.fromhex(r['bytes'])) for r in rows))
(HERE/'review-evidence.json').write_text(json.dumps(dict(summary=summary,rom=str(ROM),mapping='offset=VA-0x9ffff000',anchors=rows,direct_calls=targets,vendor_words=vendors,limitations='Vendor effective-address semantics inherited from previously reviewed local model; fields independently checked. No shared REA session, target execution or full-function export.'),ensure_ascii=False,indent=2)+'\n',encoding='utf8')
print(json.dumps(summary))
