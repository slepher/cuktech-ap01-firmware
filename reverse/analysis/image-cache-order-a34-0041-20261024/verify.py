"""A34 bounded ROM ordering windows; no execution of target or shared REA state."""
from pathlib import Path
import json, zipfile, capstone

HERE = Path(__file__).resolve().parent
ROOT = Path('D:/Documents/PlatformIO/Projects/cuktech-ap01-firmware')
ROM = ROOT / 'roms/0041/ap01-1.0.2_0041.bin'
data = ROM.read_bytes()
def read(a,n):
    o=a-0x9ffff000
    assert 0 <= o <= len(data)-n
    return data[o:o+n]
checks=[]
def raw(a,h,meaning):
    assert read(a,len(bytes.fromhex(h))).hex()==h
    checks.append(dict(address=hex(a),bytes=h,meaning=meaning))
for a,h,m in [
 (0xa0263b08,'c0b90ea0','actual backend+0c lookup target'),
 (0xa00f0dec,'91479cd8','offset=4 at cache+30'),
 (0xa00f0df8,'23aa040223ac0402','both endpoints initially NULL'),
 (0xa00eba54,'5c59','fast candidate = cache+34'),
 (0xa00eba58,'9de3','nonempty list checks front candidate first'),
 (0xa00eba64,'aa84','save tree search result'),
 (0xa00eba66,'0de9','non-NULL enters ordering path; NULL returns'),
 (0xa00eba94,'79f1','front comparator nonzero falls back to tree'),
 (0xa00ebaa4,'83a9c7ff','backlink from payload+cache+2c-4'),
 (0xa00ebaa8,'638c5905','already-front hit bypasses rewiring'),
 (0xa00ebaf4,'232c3903','empty tail repaired to hit node'),
 (0xa00ebafc,'232a3903','new head is hit node when predecessor NULL'),
 (0xa00ebdf8,'13050903','insertion list descriptor cache+30'),
 (0xa00ebe5c,'1146','copy one RV32 word'),
 (0xa00ebe70,'084b','destination backlink base is payload'),
 (0xa00ebe72,'f117','backlink at allocation length minus four'),
 (0xa00ebe74,'9305c4fc','copy new list-node pointer into backlink'),
 (0xa00ebf48,'83a9c7ff','removal loads same backlink'),
 (0xa00ec252,'83270900','victim list node word0 is tree-node pointer'),
 (0xa00ec236,'03298503','victim starts cache+38'),
 (0xa0089cfa,'d0c1','next setter writes node+offset+4'),
 (0xa008aefc,'23a22401','prepend writes descriptor head'),
 (0xa008af02,'23a42401','empty list also writes tail'),
]: raw(a,h,m)
def jal(a,t):
    w=int.from_bytes(read(a,4),'little')
    i=((w>>31)<<20)|(((w>>12)&255)<<12)|(((w>>20)&1)<<11)|(((w>>21)&1023)<<1)
    i=(i^(1<<20))-(1<<20)
    assert w&127==111 and (w>>7)&31==1 and (a+i)&0xffffffff==t
    checks.append(dict(address=hex(a),target=hex(t)))
for a,t in [(0xa00eba60,0xa00ea832),(0xa00ebc34,0xa00ea832),
 (0xa00ebac4,0xa0089d02),(0xa00ebace,0xa0089cee),
 (0xa00ebad8,0xa0089cda),(0xa00ebae2,0xa0089cda),(0xa00ebaec,0xa0089cee),
 (0xa00ebdfc,0xa008aec0),(0xa00ebe62,0xa008ab76),(0xa00ebe7a,0xa008ab76),
 (0xa00ebf56,0xa0089d02),(0xa00ebf5c,0xa008ab8a),
 (0xa008aee0,0xa0089cda),(0xa008aeea,0xa0089cee),(0xa008aef6,0xa0089cda)]: jal(a,t)
vendors={0xa00ebab4:[11,4,8,22,21,15,0],0xa0089ce4:[11,5,8,12,11,15,0],
 0xa0089d3a:[11,4,8,11,11,14,0],0xa00ebe86:[11,5,8,18,9,20,0],
 0xa00ec270:[11,4,8,18,18,15,0]}
model=ROOT/'evidence/rea-0041-20261017/ghidra/Ghidra/Processors/RISCV/data/languages/ap01thead2.sinc'
s=model.read_text(); rules={}
for name in ['th.lrw','th.srw']:
    p=s.index(':'+name+' ');rules[name]=s[p:s.index('\n}',p)+2]
for a,expected in vendors.items():
    w=int.from_bytes(read(a,4),'little')
    fields=[w&127,(w>>12)&7,w>>27,(w>>7)&31,(w>>15)&31,(w>>20)&31,(w>>25)&3]
    assert fields==expected
    checks.append(dict(address=hex(a),bytes=read(a,4).hex(),vendor_fields=fields))
windows=[('init endpoints',0xa00f0dec,0xa00f0e02),
 ('lookup head fast path and promotion',0xa00eba54,0xa00ebb12),
 ('insertion list allocation gate',0xa00ebdf8,0xa00ebe06),
 ('insertion associations',0xa00ebe5c,0xa00ebe98),
 ('removal joins inherited tree removal',0xa00ebf40,0xa00ebf60),
 ('inherited victim traversal',0xa00ec252,0xa00ec276),
 ('list setters only',0xa0089cda,0xa0089d02),
 ('unlink normal endpoint and neighbour operations',0xa0089d10,0xa0089d74),
 ('prepend pointer operations',0xa008aed8,0xa008af06)]
cs=capstone.Cs(capstone.CS_ARCH_RISCV,capstone.CS_MODE_RISCV32|capstone.CS_MODE_RISCVC)
rows=[]
for scope,a,e in windows:
    while a<e:
        n=2 if read(a,2)[0]&3!=3 else 4
        assert a+n<=e
        b=read(a,n);ins=next(cs.disasm(b,a),None)
        assert ins is not None or a in vendors
        rows.append(dict(scope=scope,address=hex(a),bytes=b.hex(),asm=ins.mnemonic+' '+ins.op_str if ins else 'vendor: see decoded fields and retained model rule'))
        a+=n
summary=dict(result='passed',static_only=True,windows=len(windows),bytes=sum(e-a for _,a,e in windows),instructions=len(rows),assertions=len(checks),vendor_words=len(vendors))
(HERE/'evidence.json').write_text(json.dumps(dict(summary=summary,rom=str(ROM),mapping='offset=VA-0x9ffff000',checks=checks,instructions=rows,vendor_model=str(model),vendor_rules=rules),ensure_ascii=False,indent=2)+'\n',encoding='utf8')
terms=['a00eb9c0','a00ebb90','a00ebe98','a00ec1e6','a0089d02','a008aec0','cache+38','cache+30']
files=[]
for pat in ['*-complete-0041.json','page-logic*.json','*round4.json','*knob*round2.json','photo-evidence-round3.json','settings-0041-round2*.json']:
    files.extend((ROOT/'reverse/rehost').glob(pat))
files.append(ROOT/'reverse/analysis/0041-20261013/0041-ghidra-pass3.txt')
files.extend((ROOT/'evidence/rea-0041-20261017/round3/evidence').glob('*.json'))
hits=[]
for p in dict.fromkeys(files):
    text=p.read_text(encoding='utf8',errors='replace').lower()
    found=[t for t in terms if t in text]
    if found:hits.append(dict(path=str(p),terms=found))
zh=[]
with zipfile.ZipFile(ROOT/'reverse/rehost/ap01-ui-0041-complete-source.zip') as z:
    members=[n for n in z.namelist() if n.endswith(('.c','.h','.md','.py','.json','.txt'))]
    for n in members:
        text=z.read(n).decode('utf8',errors='replace').lower();found=[t for t in terms if t in text]
        if found:zh.append(dict(member=n,terms=found))
(HERE/'reuse.json').write_text(json.dumps(dict(terms=terms,files_searched=[str(p) for p in dict.fromkeys(files)],hits=hits,zip_text_members=len(members),zip_hits=zh,limitations='Exact token bounded search, not proof of absent prior analysis; round3 metadata is not function semantics; no full-function export.',inherited=['A23/A24','A27/A28','A30/A32']),ensure_ascii=False,indent=2)+'\n',encoding='utf8')
print(json.dumps(summary))
