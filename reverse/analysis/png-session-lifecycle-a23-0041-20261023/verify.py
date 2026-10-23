"""A23 read-only static ROM evidence; no execution/emulation of firmware."""
from pathlib import Path
import json,capstone
HERE=Path(__file__).resolve().parent
ROOT=Path('D:/Documents/PlatformIO/Projects/cuktech-ap01-firmware')
ROM=ROOT/'roms/0041/ap01-1.0.2_0041.bin'
data=ROM.read_bytes()
def read(a,n):
 o=a-0xa0000000+0x1000
 assert 0<=o<=len(data)-n
 return data[o:o+n]
def u(a,n=4): return int.from_bytes(read(a,n),'little')
def sx(x,n): return (x^(1<<(n-1)))-(1<<(n-1))
checks=[]
def eq(label,a,b,va):
 assert a==b,(label,hex(va),a,b)
 checks.append(dict(label=label,address=hex(va),actual=a,expected=b))
def raw(a,s): eq('original encoding',read(a,len(bytes.fromhex(s))).hex(),s,a)
def jal(a,t):
 w=u(a); imm=((w>>31)<<20)|(((w>>12)&255)<<12)|(((w>>20)&1)<<11)|(((w>>21)&1023)<<1)
 eq('JAL rd/target',[w&127,(w>>7)&31,(a+sx(imm,21))&0xffffffff],[111,1,t],a)
def pair(a,t):
 w=u(a); v=u(a+4)
 eq('AUIPC/JALR opcode and registers',[w&127,(w>>7)&31,v&127,(v>>7)&31,(v>>15)&31],[23,1,103,1,1],a)
 eq('AUIPC/JALR target',(a+(w&0xfffff000)+sx(v>>20,12))&0xfffffffe,t,a)
def mem(a,op,f3,r,b,imm):
 w=u(a); ii=w>>20 if op!=35 else ((w>>25)<<5)|((w>>7)&31)
 rr=(w>>7)&31 if op!=35 else (w>>20)&31
 eq('I/S width/reg/displacement',[w&127,(w>>12)&7,rr,(w>>15)&31,sx(ii,12)],[op,f3,r,b,imm],a)
def branch(a,f3,r1,r2,t):
 w=u(a); i=((w>>31)<<12)|(((w>>7)&1)<<11)|(((w>>25)&63)<<5)|(((w>>8)&15)<<1)
 eq('B condition/register/target',[w&127,(w>>12)&7,(w>>15)&31,(w>>20)&31,a+sx(i,13)],[99,f3,r1,r2,t],a)
windows=[
 ('owner normal open/consume/close slice',0xa00e5d1a,0xa00e5d92),
 ('owner alternate open slice',0xa00e5d92,0xa00e5db8),
 ('session open',0xa019b168,0xa019b270),
 ('PNG open complete',0xa00eb7b6,0xa00eb9c0),
 ('PNG close complete',0xa00eab9a,0xa00eabc4),
 ('session close complete',0xa00828d6,0xa0082914),
 ('pixel destroy complete',0xa0081f26,0xa0081ff6),
 ('pixel allocator constructor complete',0xa0081d90,0xa0081eba),
 ('postprocess entry normal option gate',0xa00829e4,0xa0082a16),
 ('postprocess normal return gates',0xa0082b80,0xa0082bdc),
 ('cache insertion wrapper',0xa0082980,0xa00829e4),
 ('cache eviction payload cleanup',0xa008abb0,0xa008abe4),
 ('cache normal setup',0xa008e642,0xa008e694),
 ('PNG registered callbacks',0xa008e82c,0xa008e858),
 ('decode ABI entry',0xa019262e,0xa0192682),
 ('decode output pixel constructor slice1',0xa01928f2,0xa0192948),
 ('decode output pixel constructor slice2',0xa0192ac6,0xa0192af6),
 ('decode scratch destruction slice',0xa0193bd6,0xa0193bea),
 ('allocator adapter',0xa008aea0,0xa008aec0),
 ('free adapter',0xa008ab8a,0xa008abb0),
 ('cache entry payload adapter',0xa008b654,0xa008b6a6),
]
# Fresh original encodings rather than execution results.
for a,s in [(0xa019b176,'9305c004'),(0xa019b198,'23a62401'),(0xa019b1a2,'2388a400'),(0xa019b1fc,'5c41'),(0xa019b1fe,'a685'),(0xa019b200,'8297'),(0xa019b20a,'c854'),(0xa019b20e,'5c49'),(0xa019b212,'1c4d'),(0xa00828e2,'0841'),(0xa00828e6,'5c45'),(0xa00828ea,'a685'),(0xa00828ec,'8297'),(0xa00eabb4,'c855'),(0xa0081fba,'dc43'),(0xa0081fbe,'4849'),(0xa0081fc0,'8297'),(0xa00eb91c,'dc45'),(0xa00eb922,'c447'),(0xa00eb930,'b387d702'),(0xa00eb934,'93062700'),(0xa00eb97c,'83476900'),(0xa0082a02,'83474500'),(0xa0082b80,'83c75b00'),(0xa0082bd4,'2685'),(0xa008e674,'b7150e00')]: raw(a,s)
for args in [(0xa00eb91e,3,2,19,15,16),(0xa00eb980,35,2,12,18,44),(0xa00eb9ba,35,2,10,18,68),(0xa0081f72,3,5,15,10,2),(0xa0081eac,35,2,24,9,20),(0xa0081eb4,35,2,21,9,24),(0xa00829b4,35,2,21,10,12),(0xa00829c8,35,2,20,9,20),(0xa00829cc,35,2,19,9,16)]: mem(*args)
for args in [(0xa019b206,1,10,15,0xa019b18a),(0xa00eb938,1,15,10,0xa00eb942),(0xa00eb7d2,1,15,14,0xa00eb918),(0xa00eb8be,0,9,0,0xa00eb8ca)]: branch(*args)
for a,t in [(0xa00e5d32,0xa019b168),(0xa00e5d84,0xa018f9e8),(0xa00e5d8c,0xa00828d6),(0xa00e5d98,0xa019b168),(0xa00eb8b4,0xa019262e),(0xa00eb8c4,0xa0081f26),(0xa00eb95a,0xa00829e4),(0xa00eb964,0xa0081f26),(0xa00eb974,0xa0081f26),(0xa00eb9b2,0xa0082980),(0xa00eabb6,0xa0081f26),(0xa0081fc4,0xa008ab8a),(0xa008abc6,0xa0081f26),(0xa00829ac,0xa008b654)]: jal(a,t)
for a,t in [(0xa019b17c,0xa0080d8e),(0xa019b1e8,0xa0082c8c),(0xa0082902,0xa019d9f6),(0xa00829a0,0xa019d914),(0xa0192914,0xa0081d90),(0xa019293c,0xa0081f26),(0xa0192ade,0xa0081d90),(0xa0193bda,0xa0081f26)]: pair(a,t)
vendor={0xa00eb7f2:'th.lrw a6,a4,a5,2',0xa00eb942:'th.lrbu a1,a3,a0,2',0xa00eb946:'th.lrbu a2,a4,a0,2',0xa00eb94a:'th.srb a1,a4,a0,2',0xa00eb94e:'th.srb a2,a3,a0,2'}
for a,expected in [(0xa00eb7f2,[4,8,16,14,15,2]),(0xa00eb942,[4,16,11,13,10,2]),(0xa00eb946,[4,16,12,14,10,2]),(0xa00eb94a,[5,0,11,14,10,2]),(0xa00eb94e,[5,0,12,13,10,2])]:
 w=u(a); eq('indexed byte vendor fields',[(w>>12)&7,w>>27,(w>>7)&31,(w>>15)&31,(w>>20)&31,(w>>25)&3],expected,a)
cs=capstone.Cs(capstone.CS_ARCH_RISCV,capstone.CS_MODE_RISCV32|capstone.CS_MODE_RISCVC)
rows=[]
for name,start,end in windows:
 a=start
 while a<end:
  n=2 if u(a,2)&3!=3 else 4
  assert a+n<=end,(hex(a),name)
  rawbytes=read(a,n); i=next(cs.disasm(rawbytes,a),None)
  asm=i.mnemonic+' '+i.op_str if i else vendor.get(a)
  assert asm is not None,('unresolved instruction',hex(a),rawbytes.hex())
  rows.append(dict(scope=name,address=hex(a),file_offset=hex(a-0xa0000000+0x1000),bytes=rawbytes.hex(),asm=asm.strip()))
  a+=n
model=ROOT/'evidence/rea-0041-20261017/ghidra/Ghidra/Processors/RISCV/data/languages/ap01thead2.sinc'
s=model.read_text(); rules=[]
for p in [':th.lrbu ',':th.srb ',':th.lrw ']:
 a=s.index(p); b=s.index('\n}',a)+2; rules.append(s[a:b])
idx=json.loads((HERE.parent/'whole-rom-coverage-0041-20261023-round1.json').read_text())
seeds=['0xa019b168','0xa00828d6','0xa0081f26']
refs={a:[dict(caller=f['address'],evidence=f['direct_calls']['evidence_id']) for f in idx['functions'] if a in f['direct_calls']['callees']] for a in seeds}
summary=dict(result='passed',static_only=True,core_items=10,windows=len(windows),bytes=sum(b-a for _,a,b in windows),instructions=len(rows),assertions=len(checks),vendor_words=len(vendor),unknown_instructions=0)
result=dict(summary=summary,rom=str(ROM),mapping='offset=VA-a0000000+1000',windows=[dict(name=n,start=hex(a),end_exclusive=hex(b)) for n,a,b in windows],instructions=rows,assertions=checks,model=dict(path=str(model),rules=rules),bounded_direct_call_inventory=dict(scope='6487 Ghidra procedure direct calls; not exhaustive indirect references',refs=refs),limits=['No firmware execution, emulation, abnormal input, device/network access or historical replay.','Generic PNG decoder is an explicit ABI/output contract and slices, not a recovered or source-certified algorithm.','Cache backend acquisition/release/eviction timing is an explicit unresolved ownership boundary.','Owner is one real synchronous draw caller; no claim all rendering consumers return synchronously.'])
(HERE/'instruction-evidence.json').write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n',encoding='utf8')
(HERE/'instructions.txt').write_text('\n'.join(r['scope']+' '+r['address']+' '+r['bytes']+' '+r['asm'] for r in rows)+'\n',encoding='utf8')
(HERE/'review-index.json').write_text(json.dumps(summary,indent=2)+'\n',encoding='utf8')
print(json.dumps(summary))
