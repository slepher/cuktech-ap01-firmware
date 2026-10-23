"""A04 independent bounded static decoding. Does not execute ROM instructions."""
import json
from pathlib import Path
import capstone
from capstone import Cs, CS_ARCH_RISCV, CS_MODE_RISCV32, CS_MODE_RISCVC
HERE = Path(__file__).resolve().parent
ROM = Path('D:/Documents/PlatformIO/Projects/cuktech-ap01-firmware/roms/0041/ap01-1.0.2_0041.bin')
BASE = 0x9ffff000
raw = ROM.read_bytes()
md = Cs(CS_ARCH_RISCV, CS_MODE_RISCV32 | CS_MODE_RISCVC)
a03 = json.loads((HERE.parent/'wait-wrapper-a03-0041-20261023/instruction-evidence.json').read_text())
def word(pc, n=4):
    return int.from_bytes(raw[pc-BASE:pc-BASE+n], 'little')
def signed(n, bits):
    return n - (1 << bits) if n & (1 << (bits-1)) else n
def target(pc, kind):
    w = word(pc, 2 if kind in ('cb', 'cj') else 4)
    if kind == 'jal':
        assert w & 0x7f == 0x6f
        imm = ((w>>31&1)<<20)|((w>>12&255)<<12)|((w>>20&1)<<11)|((w>>21&1023)<<1)
        bits = 21
    elif kind == 'b':
        assert w & 0x7f == 0x63
        imm = ((w>>31&1)<<12)|((w>>7&1)<<11)|((w>>25&63)<<5)|((w>>8&15)<<1)
        bits = 13
    elif kind == 'cb':
        assert w & 3 == 1 and w>>13 in (6, 7)
        imm = ((w>>12&1)<<8)|((w>>10&3)<<3)|((w>>5&3)<<6)|((w>>3&3)<<1)|((w>>2&1)<<5)
        bits = 9
    else:
        assert w & 3 == 1 and w>>13 == 5
        imm = ((w>>12&1)<<11)|((w>>11&1)<<4)|((w>>9&3)<<8)|((w>>8&1)<<10)|((w>>7&1)<<6)|((w>>6&1)<<7)|((w>>3&7)<<1)|((w>>2&1)<<5)
        bits = 12
    return (pc + signed(imm, bits)) & 0xffffffff
windows = []
for old in a03['windows']:
    lo, hi = int(old['start'], 16), int(old['end_exclusive'], 16)
    rows = []
    while lo < hi:
        chunk = raw[lo-BASE:lo-BASE+4]
        ins = next(md.disasm(chunk, lo, 1), None)
        size = ins.size if ins else (4 if chunk[0]&3 == 3 else 2)
        rows.append(dict(pc=hex(lo), bytes=chunk[:size].hex(), asm=ins.mnemonic+' '+ins.op_str if ins else 'unknown; no semantics assigned'))
        lo += size
    assert lo == hi and rows == old['instructions']
    windows.append(dict(start=old['start'], end_exclusive=old['end_exclusive'], instructions=rows))
checks = [
    (0xa00b8c08,'cb',0xa00b8c2e), (0xa00b8c32,'b',0xa00b8c4a),
    (0xa00b8c36,'jal',0xa0028b0a), (0xa00b8c52,'jal',0xa002696a),
    (0xa00b8c88,'b',0xa00b8ca0), (0xa00b8ca8,'jal',0xa0028bfc),
    (0xa00b8cae,'b',0xa00b8c3c), (0xa00b8cb6,'jal',0xa00267c0),
    (0xa00b8cbe,'cj',0xa00b8c3c), (0xa0126990,'cb',0xa01269ea),
    (0xa01269f6,'jal',0xa00b8bfc), (0xa01269fc,'b',0xa0126b10),
    (0xa0126b10,'jal',0xa00b4196), (0xa0126b16,'b',0xa012698c),
    (0xa0126bb2,'cj',0xa0126980),
]
edges=[]
for pc, kind, expected in checks:
    actual = target(pc, kind)
    assert actual == expected, (hex(pc), hex(actual), hex(expected))
    edges.append(dict(pc=hex(pc), encoding=kind, target=hex(actual)))
strings=[]
for s in a03['strings']:
    p=int(s['address'],16)-BASE
    b=raw[p:p+128].split(b'\0',1)[0]
    assert b.hex()==s['bytes'] and b.decode('ascii')==s['text']
    strings.append(s)
unknown=[i for w in windows for i in w['instructions'] if i['asm'].startswith('unknown')]
assert any(i['pc']=='0xa00b8c78' and i['bytes']=='8b97d420' for i in unknown)
out=dict(task='A04', method='independent ROM decode and encoded immediate reconstruction; no target execution', decoder='Capstone '+capstone.__version__, mapping_base=hex(BASE), windows=windows, checks=dict(A03_rows_equal=True, verified_edges=edges, string_bytes_equal=True), strings=strings, unknown_words=unknown, limits=['Only A03 two inventory-selected windows; no whole-ROM search.', 'No proof of caller member non-nullness or identity with buzzer exit slot.', 'Vendor words retained without semantics; timeout arithmetic not reconstructed.', 'Caller body coverage only supports selected local path, not complete RPC recovery.'])
(HERE/'verification.json').write_text(json.dumps(out,indent=2)+'\n',encoding='utf8')
print(json.dumps(dict(bytes=sum(int(w['end_exclusive'],16)-int(w['start'],16) for w in windows), instructions=sum(len(w['instructions']) for w in windows), edges=len(edges), unknown=unknown, A03_rows_equal=True)))
