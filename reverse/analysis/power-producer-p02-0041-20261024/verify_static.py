"""P-02: bounded static ROM/retained checks. No firmware/model execution."""
import hashlib
import json
from pathlib import Path
from capstone import Cs, CS_ARCH_RISCV, CS_MODE_RISCV32, CS_MODE_RISCVC, cs_version
MAIN=Path('D:/Documents/PlatformIO/Projects/cuktech-ap01-firmware')
OUT=Path(__file__).resolve().parent
BASE=0x9ffff000
SOURCE='reverse/analysis/buzzer-backlight-0041-20261023.json'
doc=json.loads((MAIN/SOURCE).read_text(encoding='utf-8'))
assert doc['rom_sha256']=='972db4c136c7ed9e24a83c07c1a7fd62040ca018b08ca285216d26b1fee3c6b9'
f=next(x for x in doc['functions'] if x['address']=='0xa00a8582')
assert f['profile']['parameters']['language_id']=='RISCV:LE:32:ap01thead3'
r=(MAIN/'roms/0041/ap01-1.0.2_0041.bin').read_bytes()
rr=f['raw_ranges'][0];old=bytes.fromhex(rr['hex']);origin=int(rr['start'],16)
asm={int(s.split(':',1)[0],16):s.split(':',1)[1].strip() for s in f['assembly']}
checks=[]
def check(label,actual,expected):
 assert actual==expected,(label,actual,expected)
 checks.append(dict(label=label,actual=actual,expected=expected))
def raw(pc,n=4):return r[pc-BASE:pc-BASE+n]
def w(pc):return int.from_bytes(raw(pc),'little')
def sx(n,b):return n-(1<<b) if n&(1<<(b-1)) else n
def load(pc,rd,rs,imm,f3):
 q=w(pc);check(hex(pc)+' load',[q&127,(q>>7)&31,(q>>12)&7,(q>>15)&31,sx(q>>20,12)],[3,rd,f3,rs,imm])
def store(pc,rs2,rs1,imm,f3):
 q=w(pc);v=((q>>25)<<5)|((q>>7)&31)
 check(hex(pc)+' store',[q&127,(q>>12)&7,(q>>15)&31,(q>>20)&31,sx(v,12)],[35,f3,rs1,rs2,imm])
def imm(pc,rd,rs,value,f3=0):
 q=w(pc);check(hex(pc)+' immediate',[q&127,(q>>7)&31,(q>>12)&7,(q>>15)&31,sx(q>>20,12)],[19,rd,f3,rs,value])
def jal(pc,target):
 q=w(pc);v=((q>>31)<<20)|(((q>>12)&255)<<12)|(((q>>20)&1)<<11)|(((q>>21)&1023)<<1)
 check(hex(pc)+' call',[q&127,(q>>7)&31,pc+sx(v,21)],[111,1,target])
def vendor(pc,kind,rd,rs1,third,msb=None):
 q=w(pc)
 if kind in ('ext','extu'):
  check(hex(pc)+' '+kind,[q&127,(q>>12)&7,(q>>7)&31,(q>>15)&31,(q>>20)&63,(q>>26)&63],[11,2 if kind=='ext' else 3,rd,rs1,third,msb])
 elif kind=='mula':check(hex(pc)+' mula',[q&127,(q>>12)&7,q>>25,(q>>7)&31,(q>>15)&31,(q>>20)&31],[11,1,16,rd,rs1,third])
 else:check(hex(pc)+' srw',[q&127,(q>>12)&7,q>>27,(q>>25)&3,(q>>7)&31,(q>>15)&31,(q>>20)&31],[11,5,8,0,rd,rs1,third])
md=Cs(CS_ARCH_RISCV,CS_MODE_RISCV32|CS_MODE_RISCVC)
windows=[]
for name,a,b,inherited in [('descriptor',0xa00a85a0,0xa00a85ac,True),('cmd50_dispatch',0xa00a85d4,0xa00a85dc,True),('raw_update',0xa00a8b72,0xa00a8b90,True),('total',0xa00a8bac,0xa00a8c58,True),('item_loop',0xa00a91c6,0xa00a93a4,True),('ordinary_values',0xa00a3904,0xa00a398c,False),('status_code_conversion',0xa00a36ca,0xa00a385a,False)]:
 if inherited:check(name+' retained bytes',raw(a,b-a).hex(),old[a-origin:b-origin].hex())
 ins=[];pc=a
 while pc<b:
  size=4 if raw(pc,2)[0]&3==3 else 2
  assert pc+size<=b
  i=next(md.disasm(raw(pc,size),pc),None)
  ins.append(dict(pc=hex(pc),file_offset=pc-BASE,hex=raw(pc,size).hex(),standard_decode=i.mnemonic+' '+i.op_str if i else None,retained_decode=asm.get(pc)))
  pc+=size
 check(name+' boundary',pc,b)
 windows.append(dict(name=name,start=hex(a),end_exclusive=hex(b),hex=raw(a,b-a).hex(),retained_byte_match=inherited,instructions=ins))
# raw record/value production and two-stage status conversion.
for pc,rd,rs,off,f3 in [(0xa00a392a,14,11,0,5),(0xa00a3938,13,15,4,5),(0xa00a394a,14,11,2,5),(0xa00a395a,13,15,6,5),(0xa00a396e,13,15,6,5),(0xa00a3972,14,15,4,5),(0xa00a91d2,17,9,4,5),(0xa00a91e0,16,26,12,4),(0xa00a9238,13,26,13,4),(0xa00a9260,14,9,7,4),(0xa00a9280,14,26,10,5),(0xa00a9298,11,26,8,5),(0xa00a8c14,11,10,4,5),(0xa00a938e,12,12,8,5)]:load(pc,rd,rs,off,f3)
for pc,rs2,rs1,off,f3 in [(0xa00a3944,14,15,4,1),(0xa00a3966,14,15,6,1),(0xa00a3982,14,15,8,1),(0xa00a920e,15,26,12,0),(0xa00a924a,14,26,13,0),(0xa00a9288,10,26,10,1),(0xa00a9330,14,26,13,0),(0xa00a8bdc,0,14,4,1),(0xa00a9394,15,14,4,1),(0xa00a8c36,19,15,12,1)]:store(pc,rs2,rs1,off,f3)
for pc,rd,rs,value,f3 in [(0xa00a3930,14,14,50,0),(0xa00a3952,14,14,50,0),(0xa00a396a,10,10,6,6),(0xa00a925c,25,15,32,6),(0xa00a928c,25,25,8,6),(0xa00a92a6,25,25,1024,6),(0xa00a931a,25,25,1,6),(0xa00a8c22,19,19,1024,6),(0xa00a9380,9,9,8,0)]:
 if pc==0xa00a9380:check('record stride c.addi',raw(pc,2).hex(),'a104')
 else:imm(pc,rd,rs,value,f3)
for pc,target in [(0xa00a8b8c,0xa0191652),(0xa00a9254,0xa00a3904),(0xa00a9370,0xa00a3904),(0xa00a926e,0xa00a36ca),(0xa00a927c,0xa00a36ca),(0xa00a92a0,0xa00a398c),(0xa00a92e2,0xa00a389c),(0xa00a8c1a,0xa00a398c),(0xa00a8c52,0xa00a536c)]:jal(pc,target)
vendor(0xa00a3926,'mula',15,10,14)
for pc,rd,rs in [(0xa00a393c,14,14),(0xa00a395e,14,14),(0xa00a930e,14,14),(0xa00a379a,10,12),(0xa00a37a2,10,14)]:vendor(pc,'extu',rd,rs,0,15)
for pc,rd,rs in [(0xa00a91d8,17,17),(0xa00a920a,15,15),(0xa00a9356,15,15)]:vendor(pc,'extu',rd,rs,10,10)
vendor(0xa00a9326,'ext',14,14,0,15)
vendor(0xa00a92aa,'srw',25,24,23)
# Model excerpts are read/hash-bound references, never loaded into an engine.
model=MAIN/'evidence/rea-0041-20261017/ghidra/Ghidra/Processors/RISCV/data/languages/ap01thead2.sinc'
data=model.read_bytes();expected=next(x['sha256'] for x in f['profile']['parameters']['private_model_inputs'] if Path(x['path']).name=='ap01thead2.sinc')
check('local vendor source hash',hashlib.sha256(data).hexdigest(),expected)
lines=data.decode().splitlines();excerpts=[]
for stem in [':th.mula ',':th.ext rd,rs1,15,0 ',':th.extu rd,rs1,10,10 ',':th.extu rd,rs1,15,0 ',':th.srw ']:
 i=next(i for i,s in enumerate(lines) if s.startswith(stem));excerpts.append(dict(line=i+1,text='\n'.join(lines[i:i+8])))
result=dict(claim='P-02',rom_sha256=doc['rom_sha256'],source=SOURCE,evidence_id=f['evidence_id'],profile_digest=f['profile']['digest'],language=f['profile']['parameters']['language_id'],provider=f['profile']['provider'],source_record=f['source'],base=hex(BASE),capstone=cs_version(),checks=checks,windows=windows,vendor_reference=dict(path=str(model),sha256=expected,excerpts=excerpts),limits=['Static decoding/encoding only; no target or instruction-model execution','Compressed branch immediates in standard_decode are relative offsets','Custom semantic authority is existing private source, not independent ISA certification','Full ROM digest inherited, bounded ROM bytes read only'])
(OUT/'static-checks.json').write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
print(json.dumps(dict(checks=len(checks),windows=len(windows),bytes=sum(len(x['hex'])//2 for x in windows),instructions=sum(len(x['instructions']) for x in windows))))
