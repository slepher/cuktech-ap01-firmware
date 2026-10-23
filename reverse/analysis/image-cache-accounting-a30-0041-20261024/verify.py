"""A30: static accounting join only; retained contracts are not new recovery."""
from pathlib import Path
import json
import zipfile
import capstone

HERE = Path(__file__).resolve().parent
ROOT = Path('D:/Documents/PlatformIO/Projects/cuktech-ap01-firmware')
ROM = ROOT / 'roms/0041/ap01-1.0.2_0041.bin'
data = ROM.read_bytes()
def read(a, n):
    o = a - 0x9ffff000
    assert 0 <= o <= len(data)-n
    return data[o:o+n]
checks = []
def raw(a, h, meaning):
    assert read(a, len(bytes.fromhex(h))).hex() == h
    checks.append(dict(address=hex(a), bytes=h, meaning=meaning))
for a,h,m in [
    (0xa00f0d6c,'aa84','s1=cache retained to installation'),
    (0xa00f0df0,'b7a70ea0','callback high part'),
    (0xa00f0df4,'9387e75b','callback = a00ea5be'),
    (0xa00f0e00,'dcdc','SW callback to cache+3c'),
    (0xa00ea5c6,'0841','LW a0,0(a0): word return without conversion'),
    (0xa00ea5ca,'8280','callback returns'),
    (0xa00ebbee,'2e8c','s8=insertion key a1'),
    (0xa00ebdea,'032a4900','copy length = cache+4'),
    (0xa00ebdee,'e285','copy source = original key'),
    (0xa00ebdf0,'2685','copy destination = payload allocation'),
    (0xa00ebdf2,'5286','copy a2 = cache+4'),
    (0xa00ebe20,'8448','successful node -> payload'),
    (0xa00ebe2a,'be94','entry returned = payload+cache header offset'),
    (0xa00ebe2c,'8327c903','LW fn,cache+3c'),
    (0xa00ebe30,'6285','a0=original insertion key'),
    (0xa00ebe32,'8297','indirect call'),
    (0xa00ebe34,'8327c900','reload used word after callback'),
    (0xa00ebe38,'aa97','RV32 used+charge'),
    (0xa00ebe3a,'2326f900','SW used'),
    (0xa00ebf60,'dc5c','old conclusion review: same callback for removal'),
    (0xa00ebf62,'4a85','old conclusion review: argument payload'),
    (0xa00ebf68,'898f','old conclusion review: used-charge'),
    (0xa00ebf6a,'dcc4','old conclusion review: store used'),
]: raw(a,h,m)
def jal(a,target):
    w=int.from_bytes(read(a,4),'little')
    i=((w>>31)<<20)|(((w>>12)&255)<<12)|(((w>>20)&1)<<11)|(((w>>21)&1023)<<1)
    i=(i^(1<<20))-(1<<20)
    assert w&127==111 and (w>>7)&31==1 and (a+i)&0xffffffff==target
    checks.append(dict(address=hex(a), target=hex(target), meaning='direct call encoding'))
jal(0xa00ebdf4,0xa008ab76)
jal(0xa008ab7e,0xa000589c)
windows=[
    ('init cache identity',0xa00f0d6a,0xa00f0d70),
    ('init successful callback install',0xa00f0dea,0xa00f0e02),
    ('measurement callback only',0xa00ea5be,0xa00ea5cc),
    ('insertion key alias',0xa00ebbee,0xa00ebbf2),
    ('key to payload copy',0xa00ebdea,0xa00ebdf8),
    ('successful insertion accounting',0xa00ebe1a,0xa00ebe3e),
    ('old conclusion review: removal accounting',0xa00ebf60,0xa00ebf6c),
    ('copy adapter target',0xa008ab7e,0xa008ab82),
]
cs=capstone.Cs(capstone.CS_ARCH_RISCV,capstone.CS_MODE_RISCV32|capstone.CS_MODE_RISCVC)
rows=[]
for name,a,end in windows:
    while a<end:
        n=2 if int.from_bytes(read(a,2),'little')&3!=3 else 4
        assert a+n<=end
        b=read(a,n);ins=next(cs.disasm(b,a),None);assert ins is not None
        rows.append(dict(scope=name,address=hex(a),offset=hex(a-0x9ffff000),bytes=b.hex(),asm=(ins.mnemonic+' '+ins.op_str).strip()))
        a+=n
summary=dict(static_only=True,result='passed',windows=len(windows),bytes=sum(e-a for _,a,e in windows),instructions=len(rows),assertions=len(checks),vendor_words=0)
(HERE/'evidence.json').write_text(json.dumps(dict(summary=summary,rom=str(ROM),mapping='file offset = VA-0x9ffff000',checks=checks,instructions=rows,inherited='A23 key producer and Pixel size; A25/A26 allocation units; A27/A28 budget/removal/cleanup; no re-export'),ensure_ascii=False,indent=2)+'\n',encoding='utf8')

terms=['a00f0d1c','a00ea5be','a00ebb90','a00ebe2c','a00ebf60','cache+3c','cache + 0x3c','lv_cache','cache_entry']
files=[ROOT/'reverse/reports/ap01'/n for n in ['application-rehost-complete-0041-20261017.md','application-function-matrix-0041.json','factory-reference-map-0041-20261020.md']]
rehost=ROOT/'reverse/rehost'
for pat in ['*-complete-0041.json','page-logic*.json','details-0041-round4.json','charge-0041-round4.json','main-knob-0041-round2.json','detail-knob-0041-round2.json','photo-evidence-round3.json','settings-0041-round2*.json']:
    files.extend(rehost.glob(pat))
files.append(ROOT/'reverse/analysis/0041-20261013/0041-ghidra-pass3.txt')
def hits(s):
    return [dict(line=i+1,terms=[t for t in terms if t in line.lower()]) for i,line in enumerate(s.splitlines()) if any(t in line.lower() for t in terms)]
old=[]
for p in dict.fromkeys(files):
    old.append(dict(path=str(p),hits=hits(p.read_text(encoding='utf8',errors='replace')) if p.exists() else None))
zh=[]
with zipfile.ZipFile(rehost/'ap01-ui-0041-complete-source.zip') as z:
    members=[n for n in z.namelist() if n.endswith(('.c','.h','.md','.py','.json','.txt'))]
    for n in members:
        h=hits(z.read(n).decode('utf8',errors='replace'))
        if h:zh.append(dict(member=n,hits=h))
round3=[]
for p in (ROOT/'evidence/rea-0041-20261017/round3/evidence').glob('*.json'):
    s=p.read_text(encoding='utf8',errors='replace');h=[t for t in terms if t in s.lower()]
    if h:round3.append(dict(path=str(p),matched_terms=h))
(HERE/'reuse.json').write_text(json.dumps(dict(terms=terms,old_files=old,zip_text_members=len(members),zip_hits=zh,round3_hits=round3,round3_scope='sub64-no-return repair_events[642]/[662] only body/refit metadata, not full accounting behavior',recent_inheritance=['A23','A25','A26','A27','A28'],limit='bounded exact token search; not proof never analyzed; no scripts from ZIP executed'),ensure_ascii=False,indent=2)+'\n',encoding='utf8')
print(json.dumps(summary))
