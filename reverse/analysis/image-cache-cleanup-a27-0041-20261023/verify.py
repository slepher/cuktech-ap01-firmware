"""A27: bounded static normal-path cache evidence, no target execution."""
from pathlib import Path
import json, zipfile, capstone

HERE = Path(__file__).resolve().parent
ROOT = Path('D:/Documents/PlatformIO/Projects/cuktech-ap01-firmware')
ROM = ROOT / 'roms/0041/ap01-1.0.2_0041.bin'
data = ROM.read_bytes()
def read(a, n):
    o = a - 0x9ffff000
    assert 0 <= o <= len(data)-n
    return data[o:o+n]
def word(a): return int.from_bytes(read(a, 4), 'little')
def sx(v, n): return (v ^ (1 << (n-1))) - (1 << (n-1))
checks = []
def eq(label, a, actual, expected):
    assert actual == expected, (label, hex(a), actual, expected)
    checks.append(dict(label=label, address=hex(a), actual=actual, expected=expected))
def raw(a, value): eq('encoding', a, read(a, len(bytes.fromhex(value))).hex(), value)
def pair(a, target):
    x,y=word(a),word(a+4)
    eq('AUIPC/JALR ABI',a,[x&127,(x>>7)&31,y&127,(y>>7)&31,(y>>15)&31],[23,1,103,1,1])
    eq('AUIPC/JALR target',a,(a+(x&0xfffff000)+sx(y>>20,12))&0xfffffffe,target)
def mem(a, op, f3, reg, base, imm):
    w=word(a); i=w>>20 if op==3 else ((w>>25)<<5)|((w>>7)&31)
    rr=(w>>7)&31 if op==3 else (w>>20)&31
    eq('memory width/register/offset',a,[w&127,(w>>12)&7,rr,(w>>15)&31,sx(i,12)],[op,f3,reg,base,imm])
def jal(a, target):
    w=word(a);i=((w>>31)<<20)|(((w>>12)&255)<<12)|(((w>>20)&1)<<11)|(((w>>21)&1023)<<1)
    eq('JAL target/register',a,[w&127,(w>>7)&31,(a+sx(i,21))&0xffffffff],[111,1,target])

# Only these inherited anchors are rechecked; they are not new recovery.
for a,b in [(0xa008e64e,'b7b708a0'),(0xa008e652,'938707bb'),(0xa008e660,'2326f4fc'),(0xa008b6a0,'1c45'),(0xa008b6a2,'1d8d')]: raw(a,b)
pair(0xa008e67c,0xa019855e)
for a,t in [(0xa019da52,0xa008b604),(0xa019da86,0xa008b604),(0xa019da98,0xa008b654),(0xa019daaa,0xa008b6a6),(0xa019d8f6,0xa008b654),(0xa019d908,0xa008b6a6),(0xa019d022,0xa008b604),(0xa019d03a,0xa008b654),(0xa019d04a,0xa008b6a6),(0xa01985dc,0xa000589c)]: pair(a,t)
for a,t in [(0xa019d9c8,0xa019d898),(0xa019d9f0,0xa01b2fbe),(0xa00ec266,0xa008b604),(0xa008b6f2,0xa008b654),(0xa008b6f6,0xa008ab8a)]: jal(a,t)
for a,b in [(0xa019da5a,'dc40'),(0xa019da8e,'15e1'),(0xa019da94,'99cf')]: raw(a,b)
for a,b in [(0xa019dabe,'fd17'),(0xa019dac0,'dcc0'),(0xa019dac2,'e3d107fc'),(0xa019daa4,'8145'),(0xa019daa6,'8297'),(0xa019d902,'8145'),(0xa019d904,'8297'),(0xa00ec26a,'61dd'),(0xa00ec274,'e1b7'),(0xa019d9dc,'e30535ff')]: raw(a,b)
for args in [(0xa019da90,3,4,15,9,12),(0xa019daa0,3,2,15,18,24),(0xa019d060,35,0,15,18,12),(0xa01985ce,35,2,18,10,0),(0xa01985d2,35,2,0,10,12),(0xa00ec236,3,2,18,10,56),(0xa00ec26c,3,2,15,19,48)]: mem(*args)
table=[word(a) for a in range(0xa0263afc,0xa0263b24,4)]
eq('installed backend table',0xa0263afc,table,[0xa00f0b16,0xa00f0d1c,0xa00ea730,0xa00eb9c0,0xa00ebb90,0xa00ebe98,0xa00ebf7c,0xa00ec084,0xa00ec1e6,0xa00ea78c])
w=word(0xa00ec270)
eq('vendor indexed word fields',0xa00ec270,[w&127,(w>>12)&7,w>>27,(w>>7)&31,(w>>15)&31,(w>>20)&31,(w>>25)&3],[11,4,8,18,18,15,0])
model=ROOT/'evidence/rea-0041-20261017/ghidra/Ghidra/Processors/RISCV/data/languages/ap01thead2.sinc'
s=model.read_text();p=s.index(':th.lrw ');rule=s[p:s.index('\n}',p)+2]
windows=[
 ('release normal entry',0xa019da4c,0xa019da5e),('release decision and cleanup',0xa019da84,0xa019dabe),('release decrement',0xa019dabe,0xa019dac6),
 ('creation binds backend',0xa019856c,0xa019857e),('creation binds callbacks',0xa01985c6,0xa01985ec),
 ('specific-entry invalidation',0xa019d014,0xa019d072),('eviction victim query',0xa019d8a4,0xa019d8ae),('eviction cleanup',0xa019d8e4,0xa019d914),
 ('insert capacity query',0xa019d984,0xa019d998),('insert eviction loop',0xa019d9c6,0xa019d9f4),
 ('capacity accounting',0xa00ea7d8,0xa00ea7f6),('capacity result',0xa00ea818,0xa00ea832),
 ('zero-reference victim selection',0xa00ec236,0xa00ec276),('backend unlinks and accounts',0xa00ebf26,0xa00ebf6c),
 ('allocation-base release',0xa008b6f2,0xa008b704),('reference increment',0xa01b3012,0xa01b3018)]
cs=capstone.Cs(capstone.CS_ARCH_RISCV,capstone.CS_MODE_RISCV32|capstone.CS_MODE_RISCVC)
rows=[]
for name,start,end in windows:
    a=start
    while a<end:
        n=2 if int.from_bytes(read(a,2),'little')&3!=3 else 4
        assert a+n<=end
        b=read(a,n);i=next(cs.disasm(b,a),None)
        asm=(i.mnemonic+' '+i.op_str).strip() if i else ('th.lrw s2,s2,a5,0' if a==0xa00ec270 else None)
        assert asm is not None,(hex(a),b.hex())
        rows.append(dict(window=name,address=hex(a),offset=hex(a-0x9ffff000),bytes=b.hex(),asm=asm));a+=n
summary=dict(result='passed',static_only=True,windows=len(windows),bytes=sum(e-s for _,s,e in windows),instructions=len(rows),assertions=len(checks),vendor_words=1,new_scope='normal cache ref/mark/evict to existing cleanup; no new PNG/heap recovery')
(HERE/'evidence.json').write_text(json.dumps(dict(summary=summary,rom=str(ROM),mapping='offset=VA-0x9ffff000',windows=[dict(name=n,start=hex(s),end_exclusive=hex(e)) for n,s,e in windows],instructions=rows,checks=checks,backend_table=[hex(v) for v in table],vendor_rule=dict(path=str(model),text=rule),inherited_rechecks=['A23 callback install and entry-to-payload subtraction only; not new business recovery']),ensure_ascii=False,indent=2)+'\n',encoding='utf8')

root=ROOT/'reverse';terms=['a019d9f6','a008abb0','a019d914','cache_entry','lv_cache','cache_release','cache release','cache+','cache +']
files=[root/'reports/ap01'/n for n in ['application-rehost-complete-0041-20261017.md','application-function-matrix-0041.json','factory-reference-map-0041-20261020.md']]+[root/'rehost'/n for n in ['weather-calendar-complete-0041.json','charge-complete-0041.json','guide-complete-0041.json','system-complete-0041.json','page-logic-0041.json','details-0041-round4.json','charge-0041-round4.json']]+[root/'analysis/0041-20261013/0041-ghidra-pass3.txt']
reuse=[]
for p in files:
    hits=[dict(line=i+1,text=l[:400]) for i,l in enumerate(p.read_text(encoding='utf8',errors='replace').splitlines()) if any(t in l.lower() for t in terms)]
    reuse.append(dict(path=str(p),hits=hits))
zh=[]
with zipfile.ZipFile(root/'rehost/ap01-ui-0041-complete-source.zip') as z:
    members=[n for n in z.namelist() if n.endswith(('.c','.h','.md','.py','.json','.txt'))]
    for n in members:
        hits=[dict(line=i+1,text=l[:300]) for i,l in enumerate(z.read(n).decode('utf8',errors='replace').splitlines()) if any(t in l.lower() for t in terms)]
        if hits: zh.append(dict(member=n,hits=hits))
(HERE/'reuse.json').write_text(json.dumps(dict(terms=terms,files=reuse,zip=dict(path=str(root/'rehost/ap01-ui-0041-complete-source.zip'),searched_text_members=len(members),hits=zh),limit='Bounded token search, not proof never analyzed; A23-A26 contracts are inherited directly.'),ensure_ascii=False,indent=2)+'\n',encoding='utf8')
print(json.dumps(summary))
