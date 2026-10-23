from pathlib import Path
import json,zipfile,capstone
HERE=Path(__file__).resolve().parent
ROOT=Path('D:/Documents/PlatformIO/Projects/cuktech-ap01-firmware')
ROM=ROOT/'roms/0041/ap01-1.0.2_0041.bin'
r=ROM.read_bytes();base=0x9ffff000
checks=[]
def raw(a,h):
 b=r[a-base:a-base+len(bytes.fromhex(h))].hex();assert b==h,(hex(a),b,h)
 checks.append(dict(address=hex(a),bytes=b,expected=h))
def sx(x,b):return (x^(1<<(b-1)))-(1<<(b-1))
def pair(a,target):
 x=int.from_bytes(r[a-base:a-base+4],'little'); y=int.from_bytes(r[a-base+4:a-base+8],'little')
 assert [x&127,(x>>7)&31,y&127,(y>>7)&31,(y>>15)&31]==[23,1,103,1,1]
 actual=(a+(x&0xfffff000)+sx(y>>20,12))&0xfffffffe
 assert actual==target,(hex(a),hex(actual));checks.append(dict(address=hex(a),call_target=hex(actual)))
def jal(a,target):
 w=int.from_bytes(r[a-base:a-base+4],'little');i=((w>>31)<<20)|(((w>>12)&255)<<12)|(((w>>20)&1)<<11)|(((w>>21)&1023)<<1)
 actual=(a+sx(i,21))&0xffffffff;assert w&127==111 and (w>>7)&31==1 and actual==target
 checks.append(dict(address=hex(a),call_target=hex(actual)))
for a,h in [(0xa00890f6,'b794fc629384c457'),(0xa00890fe,'83a90412'),(0xa0089128,'2a89'),(0xa008912a,'232604fc232804fc232a04fc232c04fc232e04fc'),(0xa008913e,'2324a4fc'),(0xa0089146,'2306a4fc'),(0xa008914a,'930584fc4e85'),(0xa0089158,'61468145130584fc'),(0xa0089164,'4a85232624fd'),(0xa008916e,'2308a4fc'),(0xa0089172,'03a5c411930584fc'),(0xa00eaa9c,'48558280'),(0xa00ed802,'0329c505aa84ae89'),(0xa00ed80a,'63030902')]:raw(a,h)
for a,t in [(0xa0089150,0xa019cfbe),(0xa008917a,0xa019cfbe)]:pair(a,t)
for a,t in [(0xa0089142,0xa00dd454),(0xa008916a,0xa00dd454),(0xa0089160,0xa0024906),(0xa00ed80e,0xa00eaa50),(0xa00ed812,0xa00890e8)]:jal(a,t)
windows=[('old-source getter',0xa00eaa9c,0xa00eaaa0),('normal old-source invalidation caller',0xa00ed802,0xa00ed816),('global identity',0xa00890f6,0xa0089104),('first cache key',0xa0089128,0xa0089158),('key clear',0xa0089158,0xa0089164),('image cache key and call',0xa0089164,0xa0089182)]
c=capstone.Cs(capstone.CS_ARCH_RISCV,capstone.CS_MODE_RISCV32|capstone.CS_MODE_RISCVC);rows=[]
for label,s,e in windows:
 ins=list(c.disasm(r[s-base:e-base],s));assert sum(i.size for i in ins)==e-s
 rows.extend(dict(window=label,address=hex(i.address),bytes=i.bytes.hex(),asm=i.mnemonic+' '+i.op_str) for i in ins)
summary=dict(static_only=True,windows=len(windows),bytes=sum(e-s for _,s,e in windows),instructions=len(rows),checks=len(checks),result='passed',new_scope='old-source normal API to image-cache instance/key only; inherited cache cleanup not re-exported')
(HERE/'evidence.json').write_text(json.dumps(dict(summary=summary,instructions=rows,checks=checks),ensure_ascii=False,indent=2)+'\n',encoding='utf8')
terms=['a019cfbe','a00890e8','a00ed7f4','a00eaa50','62fc9698','cache_drop','cache_invalidate','image_cache_drop']
rev=ROOT/'reverse';files=[rev/'reports/ap01'/n for n in ['application-rehost-complete-0041-20261017.md','application-function-matrix-0041.json','factory-reference-map-0041-20261020.md','application-rehost-0041-round3-20261016.md']]
files+=list((rev/'rehost').glob('*.json'));files+=[rev/'analysis/0041-20261013/0041-ghidra-pass3.txt']
reuse=[]
for p in files:
 s=p.read_text(encoding='utf8',errors='replace').lower();hits=[t for t in terms if t in s]
 reuse.append(dict(path=str(p),matched_terms=hits))
zh=[];count=0
with zipfile.ZipFile(rev/'rehost/ap01-ui-0041-complete-source.zip') as z:
 for n in z.namelist():
  if not n.endswith(('.h','.c','.py','.md','.txt','.json')):continue
  count+=1;s=z.read(n).decode('utf8',errors='replace').lower();hits=[t for t in terms if t in s]
  if hits:zh.append(dict(member=n,matched_terms=hits))
(HERE/'reuse.json').write_text(json.dumps(dict(terms=terms,files=reuse,zip=dict(text_members=count,hits=zh),limits='Token matches only; no-hit does not prove absent prior analysis. Whole-ROM retained direct-call relations are cited in report, not regenerated.'),ensure_ascii=False,indent=2)+'\n',encoding='utf8')
print(json.dumps(summary));print('reuse_hits',[(Path(x['path']).name,x['matched_terms']) for x in reuse if x['matched_terms']])
