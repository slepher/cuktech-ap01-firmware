"""A37 bounded static ROM checks; no firmware execution or resource decoding."""
from pathlib import Path
import json
import sys
import zipfile

OUT = Path(__file__).resolve().parent
TREE = OUT.parents[2]
MAIN = Path('D:/Documents/PlatformIO/Projects/cuktech-ap01-firmware')
sys.path.insert(0, str(TREE / 'reverse/analysis/display-event-flow-g05-0041-20261023'))
import read_rom as rr

windows = [
    ('reader memory arm', 0xa010a5fa, 0xa010a616),
    ('reader source identity', 0xa010a678, 0xa010a67e),
    ('allocation and reader copy', 0xa010a79e, 0xa010a7c6),
    ('owned header and table', 0xa010a7dc, 0xa010a81a),
    ('saved position and return', 0xa010a85e, 0xa010a888),
    ('wrapper unchanged return', 0xa0107e22, 0xa0107e34),
    ('owner holds decoder and output', 0xa00ed884, 0xa00ed88e),
    ('word copy selected tail', 0xa0005992, 0xa00059b8),
    ('word copy bulk pointer slot', 0xa00059d0, 0xa00059f0),
]
rows = [dict(window=n, **x) for n, a, z in windows for x in rr.rows(a, z)]
D = {int(x['pc'], 16): x for x in rows}
checks = []
def check(a, asm):
    assert D[a]['asm'] == asm, (hex(a), D[a], asm)
    checks.append({'pc': hex(a), 'asm': asm})
for a, asm in {
    0xa010a5fa:'c.lw a4, 0x14(a0)', 0xa010a5fe:'c.lw a1, 0xc(a0)',
    0xa010a600:'c.mv s1, a0', 0xa010a602:'c.mv a0, a5',
    0xa010a604:'c.add a1, a4', 0xa010a606:'c.mv s2, a2',
    0xa010a610:'c.lw a2, 0x14(s1)', 0xa010a612:'c.add a2, s2',
    0xa010a614:'c.sw a2, 0x14(s1)', 0xa010a678:'c.mv s2, a0',
    0xa010a79e:'mul s5, s7, s6', 0xa010a7a2:'c.lui a0, 4',
    0xa010a7a4:'c.li a5, 5', 0xa010a7a6:'addi a0, a0, 0x664',
    0xa010a7b2:'c.mv s1, a0', 0xa010a7b8:'addi a2, zero, 0x664',
    0xa010a7bc:'c.mv a1, s2', 0xa010a7e8:'sh s7, 0x1c(s1)',
    0xa010a7ec:'sh s6, 0x1e(s1)', 0xa010a804:'c.sw a5, 0x34(s1)',
    0xa010a80a:'addi a0, s1, 0x664', 0xa010a812:'c.sw a0, 0x58(a5)',
    0xa010a818:'c.sw a0, 0x5c(a5)', 0xa010a85e:'c.li a2, 1',
    0xa010a860:'c.li a1, 0', 0xa010a862:'c.mv a0, s1',
    0xa010a86a:'c.sw a0, 0x18(s1)', 0xa010a86c:'c.sw a5, 0x24(s1)',
    0xa010a880:'c.mv a0, s1', 0xa010a882:'c.lwsp s1, 0x34(sp)',
    0xa0107e32:'c.jr ra', 0xa00ed884:'sw s2, 0x5c(s1)',
    0xa00ed888:'lw a5, 0x658(s2)', 0xa00ed88c:'c.sw a5, 0x74(s1)',
    0xa00059e8:'lw a7, 0xc(a1)', 0xa00059ec:'sw a7, 0xc(a5)',
}.items(): check(a, asm)
for a, target in [(0xa010a608,0xa000589c),(0xa010a67a,0xa010a5d6),
                  (0xa010a7ae,0xa008aea0),(0xa010a7be,0xa000589c),
                  (0xa010a7f8,0xa010a5d6),(0xa010a864,0xa010a618)]:
    assert D[a]['target'] == hex(target)
    checks.append({'pc':hex(a),'target':hex(target)})

model = MAIN/'evidence/rea-0041-20261017/ghidra/Ghidra/Processors/RISCV/data/languages/ap01thead2.sinc'
s = model.read_text()
vendor = []
for a, expected, name, text in [
    (0xa010a7aa,[11,1,16,10,21,15],':th.mula ','rd = rd + (rs1 * rs2);'),
    (0xa010a814,[11,1,2,10,10,21],':th.addsl ','rd = rs1 + (rs2 << thshift);'),
]:
    w = int.from_bytes(rr.rom[a-rr.BASE:a-rr.BASE+4], 'little')
    fields = [w&127,(w>>12)&7,w>>25,(w>>7)&31,(w>>15)&31,(w>>20)&31]
    assert fields == expected
    i=s.index(name); rule=s[i:s.index('\n}',i)+2]; assert text in rule
    vendor.append({'pc':hex(a),'raw':w.to_bytes(4,'little').hex(),'fields':fields,'rule':rule})
# ADDsl's shift is bits26:25: two => O+0x664+4*N.
assert (int.from_bytes(bytes.fromhex(D[0xa010a814]['raw']), 'little') >> 25) & 3 == 2
# No a0 overwrite between constructor call and wrapper return.
assert all('a0' not in r['asm'] for r in rr.rows(0xa0107e22,0xa0107e32))

rehost=MAIN/'reverse/rehost'
reuse=[]
for p in sorted(rehost.glob('*.json')):
    t=p.read_text(encoding='utf8',errors='replace').lower()
    hits=[x for x in ['a010a65a','a010a7be','a0107dea'] if x in t]
    if hits: reuse.append({'file':p.name,'terms':hits})
j=json.loads((rehost/'weather-calendar-complete-0041.json').read_text(encoding='utf8'))
assert 'truncated output' in j['evidence'][30]['stdout']
j=json.loads((rehost/'page-logic-0041.json').read_text(encoding='utf8'))
assert j['records'][15]['parameters']['procedure']=='0xa0024906'
with zipfile.ZipFile(rehost/'ap01-ui-0041-complete-source.zip') as z:
    members=[n for n in z.namelist() if any(t in n.lower() for t in ['gif','photo','pages.h'])]
result=dict(status='PASS',static_only=True,baseline='f17c7d7',checks=checks,rows=rows,
            vendor=vendor,reuse=reuse,zip_scoped_members=members,
            coverage='Constructor normal success path inspected as raw instructions; retained only required windows. No decoder/resource execution.',
            limits='No all-failure-arm recovery, teardown, runtime timing, source-version certification or heap implementation.')
(OUT/'evidence.json').write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n',encoding='utf8')
print(json.dumps({'status':'PASS','checks':len(checks),'windows':len(windows),'vendor':len(vendor)}))
