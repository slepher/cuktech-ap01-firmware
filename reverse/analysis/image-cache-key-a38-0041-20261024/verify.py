from pathlib import Path
import json,zipfile,capstone
H=Path(__file__).resolve().parent
R=Path('D:/Documents/PlatformIO/Projects/cuktech-ap01-firmware');p=(R/'roms/0041/ap01-1.0.2_0041.bin').read_bytes()
def read(a,n): return p[a-0x9ffff000:a-0x9ffff000+n]
cs=capstone.Cs(capstone.CS_ARCH_RISCV,capstone.CS_MODE_RISCV32|capstone.CS_MODE_RISCVC)
windows=[('callback producer inherited A23',0xa008e642,0xa008e64e),('table install',0xa01985d6,0xa01985ec),('tree init arguments',0xa00f0de0,0xa00f0dea),('tree comparator save',0xa00f0c02,0xa00f0c1e),('record adapter fields',0xa0087bce,0xa0087bde),('class and source compare core',0xa0087b5c,0xa0087ba6),('head lookup inherited A34',0xa00eba7e,0xa00eba98),('tree lookup call and sign branches',0xa00ea858,0xa00ea870),('byte compare path and alignment gate',0xa002db1a,0xa002db52),('equal word zero detector',0xa002db58,0xa002db70)]
rows=[]
vendors={0xa002db3e:[11,4,16,15,10,14,0],0xa002db42:[11,4,16,13,11,14,0]}
for scope,a,e in windows:
 while a<e:
  n=2 if read(a,1)[0]&3!=3 else 4;b=read(a,n);i=next(cs.disasm(b,a),None)
  assert a+n<=e and (i is not None or a in vendors)
  rows.append(dict(scope=scope,address=hex(a),file_offset=hex(a-0x9ffff000),bytes=b.hex(),asm=i.mnemonic+' '+i.op_str if i else 'th.lrbu (see independently decoded fields)'));a+=n
checks=[]
for a,h,m in [(0xa008e642,'b78708a0938767bc2322f4fc','callback address a0087bc6 producer'),(0xa01985d6,'3146ce854105','copy 12 bytes from callbacks into cache+10'),(0xa00f0d26,'0c49','a1=cache+10 comparator'),(0xa00f0de2,'13054502','tree argument cache+24'),(0xa00f0c18,'23a22401','tree+4=original comparator'),(0xa0087bce,'83c68500d041834585004841','LBU right+8 LW right+4 LBU left+8 LW left+4'),(0xa0087b8c,'99e9','same nonzero non1 class returns zero'),(0xa0087b94,'6377a600','class0 unsigned source ordering'),(0xa0087b9e,'e3edb6fe','different class unsigned ordering'),(0xa00ea862,'7dd163540500','zero hit then signed direction'),(0xa002db4e,'3385d740','return difference of unsigned bytes')]:
 assert read(a,len(bytes.fromhex(h))).hex()==h;checks.append(dict(address=hex(a),bytes=h,meaning=m))
def jal(a,t):
 w=int.from_bytes(read(a,4),'little');imm=((w>>31)<<20)|(((w>>12)&255)<<12)|(((w>>20)&1)<<11)|(((w>>21)&1023)<<1);imm=(imm^(1<<20))-(1<<20)
 assert w&127==111 and (a+imm)&0xffffffff==t;checks.append(dict(address=hex(a),target=hex(t)))
for a,t in [(0xa0087bda,0xa0087b5c),(0xa0087b70,0xa002db16),(0xa00f0de6,0xa00f0b80)]:jal(a,t)
for a,v in vendors.items():
 w=int.from_bytes(read(a,4),'little');f=[w&127,(w>>12)&7,w>>27,(w>>7)&31,(w>>15)&31,(w>>20)&31,(w>>25)&3];assert f==v;checks.append(dict(address=hex(a),bytes=read(a,4).hex(),fields=f))
model=R/'evidence/rea-0041-20261017/ghidra/Ghidra/Processors/RISCV/data/languages/ap01thead2.sinc';s=model.read_text();i=s.index(':th.lrbu ');rule=s[i:s.index('\n}',i)+2]
terms=['a0087bc6','a0087b5c','a002db16','a00ea832']
files=[]
for pat in ['*-complete-0041.json','*round4.json','photo-evidence-round3.json','settings-0041-round2*.json'] :files.extend((R/'reverse/rehost').glob(pat))
files.append(R/'reverse/analysis/0041-20261013/0041-ghidra-pass3.txt');files.extend((R/'evidence/rea-0041-20261017/round3/evidence').glob('*.json'))
hits=[]
for f in dict.fromkeys(files):
 s=f.read_text(encoding='utf8',errors='replace').lower();found=[t for t in terms if t in s]
 if found:hits.append(dict(path=str(f),terms=found))
zh=[]
with zipfile.ZipFile(R/'reverse/rehost/ap01-ui-0041-complete-source.zip') as z:
 names=[n for n in z.namelist() if n.endswith(('.c','.h','.md','.py','.json','.txt'))]
 for n in names:
  s=z.read(n).decode('utf8',errors='replace').lower();found=[t for t in terms if t in s]
  if found:zh.append(dict(member=n,terms=found))
summary=dict(result='passed',windows=len(windows),bytes=sum(e-a for _,a,e in windows),instructions=len(rows),assertions=len(checks),vendor_words=len(vendors),static_only=True)
(H/'evidence.json').write_text(json.dumps(dict(summary=summary,checks=checks,instructions=rows,model=str(model),rule=rule),ensure_ascii=False,indent=2)+'\n',encoding='utf8')
(H/'reuse.json').write_text(json.dumps(dict(terms=terms,files=[str(f) for f in dict.fromkeys(files)],hits=hits,zip_members=len(names),zip_hits=zh,limitations='Bounded exact-token search only; absence is not absence of historical analysis. Hits for a002db16 outside comparator callers are reused location context, not a recovered image-cache matching contract.'),ensure_ascii=False,indent=2)+'\n',encoding='utf8')
print(json.dumps(summary));print(json.dumps(hits,ensure_ascii=False))
