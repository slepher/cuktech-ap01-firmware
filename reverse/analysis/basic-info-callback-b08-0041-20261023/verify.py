"""B08 static ROM extraction/encoding checks; does not execute firmware."""
from pathlib import Path
import json, sys
from capstone import Cs, CS_ARCH_RISCV, CS_MODE_RISCV32, CS_MODE_RISCVC
HERE=Path(__file__).resolve().parent
ROOT=HERE.parents[2]
SOURCE=Path(sys.argv[1])
ROM=SOURCE/'roms/0041/ap01-1.0.2_0041.bin'
r=ROM.read_bytes(); BASE=0x9ffff000
md=Cs(CS_ARCH_RISCV,CS_MODE_RISCV32|CS_MODE_RISCVC)
specs=[('dispatch',0xa00a389c,0xa00a3904),('callback',0xa00a3c8a,0xa00a3ce0)]
records=[]; ins={}; raw={}; vendors=[]
for name,start,end in specs:
 p=start; rows=[]
 while p<end:
  n=4 if r[p-BASE]&3==3 else 2; b=r[p-BASE:p-BASE+n]; raw[p]=int.from_bytes(b,'little')
  i=next(md.disasm(b,p),None)
  if i:
   assert i.size==n
   asm=i.mnemonic+' '+i.op_str; ins[p]=(i.mnemonic,i.op_str)
  else:
   w=raw[p]; fields=dict(op=w&127,rd=w>>7&31,funct3=w>>12&7,rs1=w>>15&31,rs2=w>>20&31,shift=w>>25&3,funct5=w>>27)
   if p==0xa00a38d8:
    assert fields==dict(op=11,rd=0,funct3=5,rs1=20,rs2=18,shift=0,funct5=8)
    asm='th.srw zero,s4,s2,0 (existing local model)'
   else:
    assert p==0xa00a3c9e
    fields=dict(op=w&127,rd=w>>7&31,funct3=w>>12&7,rs1=w>>15&31,lsb=w>>20&63,msb=w>>26&63)
    assert fields==dict(op=11,rd=14,funct3=3,rs1=14,lsb=4,msb=5)
    asm='th.extu a4,a4,5,4 (existing local model)'
   vendors.append(dict(address=hex(p),fields=fields));
  rows.append(dict(address=hex(p),file_offset=p-BASE,hex=b.hex(),decode=asm)); p+=n
 assert p==end
 records.append(dict(name=name,start=hex(start),end_exclusive=hex(end),instructions=rows))
expected={0xa00a38a0:('lw','a5, 0x2cc(a5)'),0xa00a38ae:('mul','s2, a0, s2'),0xa00a38c0:('lw','s4, 0(a5)'),0xa00a38ce:('add','s5, s4, s2'),0xa00a38ee:('c.lw','a5, 0(s1)'),0xa00a38f2:('c.lw','a0, 4(s1)'),0xa00a38f4:('c.mv','a1, s5'),0xa00a38f6:('c.jalr','a5'),0xa00a38f8:('lw','a5, 0(s3)'),0xa00a38fe:('c.lw','s1, 4(s1)'),0xa00a3c92:('c.lw','a4, 0x24(a1)'),0xa00a3c94:('c.mv','a5, a0'),0xa00a3c9a:('andi','a3, a4, 0xf'),0xa00a3ca6:('lbu','a4, 0xe(a1)'),0xa00a3cb4:('lbu','a4, 0xd(a1)'),0xa00a3cbc:('lhu','a7, 6(a1)'),0xa00a3cc0:('lhu','a6, 4(a1)'),0xa00a3cde:('c.jr','ra')}
for p,e in expected.items(): assert ins[p]==e,(hex(p),ins[p])
# Independent bitfields for ABI compressed loads, MV and indirect call, and standard loads.
encoding=[]
def check(p,condition,label):
 assert condition,(hex(p),label)
 encoding.append(dict(address=hex(p),check=label))
for p,rd,rs,imm in [(0xa00a38ee,15,9,0),(0xa00a38f2,10,9,4),(0xa00a3c92,14,11,36)]:
 w=raw[p]; off=((w>>10&7)<<3)|((w>>6&1)<<2)|((w>>5&1)<<6)
 check(p,w&3==0 and w>>13==2 and (w>>2&7)+8==rd and (w>>7&7)+8==rs and off==imm,'C.LW register/offset')
for p,rd,rs in [(0xa00a38f4,11,21),(0xa00a3c94,15,10)]:
 w=raw[p]; check(p,w>>12==8 and w&3==2 and w>>7&31==rd and w>>2&31==rs,'C.MV registers')
w=raw[0xa00a38f6]; check(0xa00a38f6,w==0x9782,'C.JALR a5 exact encoding')
for p,rd,imm,f3 in [(0xa00a3ca6,14,14,4),(0xa00a3cb4,14,13,4),(0xa00a3cbc,17,6,5),(0xa00a3cc0,16,4,5)]:
 w=raw[p]; check(p,w&127==3 and w>>7&31==rd and w>>15&31==11 and w>>20==imm and w>>12&7==f3,'load unsigned width/register/offset')
for p,base,dest in [(0xa00a38a4,0,0xa00a3902),(0xa00a38d6,0,0xa00a38ee),(0xa00a38f0,0,0xa00a38f8),(0xa00a3900,0,0xa00a38d6),(0xa00a3cd4,0,0xa008b51a)]:
 check(p,p+int(ins[p][1].split(',')[-1].strip(),0)==dest,'decoded relative control target')
# JAL target from raw immediate, independent of text.
w=raw[0xa00a3cd4]; imm=((w>>31)<<20)|((w>>12&255)<<12)|((w>>20&1)<<11)|((w>>21&1023)<<1); imm=imm-(1<<21) if imm&(1<<20) else imm
check(0xa00a3cd4,0xa00a3cd4+imm==0xa008b51a,'raw JAL target')
strings=[]
for p in [0xa0268540,0xa026a5d0,0xa02684f0]:
 b=r[p-BASE:].split(b'\0',1)[0]; strings.append(dict(address=hex(p),file_offset=p-BASE,text=b.decode('ascii')))
model=SOURCE/'evidence/rea-0041-20261017/ghidra/Ghidra/Processors/RISCV/data/languages/ap01thead2.sinc'
lines=model.read_text().splitlines(); excerpts=[]
for prefix in [':th.extu rd,rs1,5,4 ',':th.srw ']:
 i=next(i for i,l in enumerate(lines) if l.startswith(prefix)); e=next(j for j in range(i+1,len(lines)) if lines[j]=='}')+1
 excerpts.append(dict(path=str(model),line=i+1,text='\n'.join(lines[i:e])))
d=json.loads((ROOT/'reverse/analysis/whole-rom-coverage-0041-20261023-round1.json').read_text())
functions=[dict(address=f['address'],extent=f['extent'],dossiers=f['dossiers'],scope=f['scope'],excluded_as_verified_open_source=f['excluded_as_verified_open_source']) for f in d['functions'] if f['address'] in ['0xa00a389c','0xa00a3c8a']]
checks=dict(result='passed',windows=2,bytes=sum(e-s for _,s,e in specs),ordinary_instructions=len(ins),vendor_words=len(vendors),semantic_decode_assertions=len(expected),encoding_checks=len(encoding))
(HERE/'instruction-evidence.json').write_text(json.dumps(dict(task='B08',source=str(ROM),mapping='offset=VA-0x9ffff000',checks=checks,windows=records,vendor_words=vendors,encoding_checks=encoding,strings=strings,model_excerpts=excerpts,retained_inventory=functions,limits=['Static ROM reading only; no target execution.','Indirect ABI conditional on node target and runtime list contents.','Vendor meanings rely on existing local model; no fresh upstream ISA certification.']),indent=2)+'\n')
print(json.dumps(checks))
