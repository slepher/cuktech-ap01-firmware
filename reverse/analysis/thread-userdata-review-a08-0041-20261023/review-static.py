"""A08 static review: independent ROM read; never execute firmware."""
import json
from pathlib import Path
from capstone import Cs, CS_ARCH_RISCV, CS_MODE_RISCV32, CS_MODE_RISCVC, __version__
here=Path(__file__).resolve().parent
root=here.parents[2]
rom=Path('D:/Documents/PlatformIO/Projects/cuktech-ap01-firmware/roms/0041/ap01-1.0.2_0041.bin').read_bytes()
base=0x9ffff000
prior=json.loads((root/'reverse/analysis/thread-userdata-a07-0041-20261023/instruction-evidence.json').read_text(encoding='utf8'))
md=Cs(CS_ARCH_RISCV, CS_MODE_RISCV32|CS_MODE_RISCVC)
by_pc={}; slots=0; ordinary=0; unknown=[]
for w in prior['windows']:
 cursor=int(w['start'],16)
 for i in w['instructions']:
  pc=int(i['pc'],16); b=bytes.fromhex(i['bytes'])
  assert cursor==pc and rom[pc-base:pc-base+len(b)]==b
  fresh=next(md.disasm(b,pc,1),None)
  if fresh:
   asm=fresh.mnemonic+' '+fresh.op_str
   assert fresh.size==len(b) and asm==i['asm']
   ordinary+=1
  else:
   assert len(b)==4 and int.from_bytes(b,'little')&0x7f==0x0b
   unknown.append(dict(pc=hex(pc),bytes=b.hex(),status='custom opcode; semantics unassigned'))
  by_pc[pc]=i; slots+=1; cursor+=len(b)
 assert cursor==int(w['end_exclusive'],16)
# Separate selected instruction assertions, not executing/reusing A07 checker.
expected={
0xa0197f12:'c.mv s3, a1',0xa0197f18:'c.mv s4, a0',0xa0197f1a:'c.mv s2, a2',
0xa0197f26:'sw a3, -0x38(s0)',0xa0197f2a:'sw a4, -0x34(s0)',
0xa0197f36:'lw a3, -0x38(s0)',0xa0197f3e:'sw a3, -0x24(s0)',0xa0197f42:'sb a5, -0x29(s0)',
0xa0197f50:'lw a4, -0x34(s0)',0xa0197f54:'c.mv a2, s2',0xa0197f56:'addi a1, s0, -0x2c',
0xa0197f5a:'c.mv a3, a4',0xa0197f5c:'c.mv s1, a0',0xa0197f66:'c.mv s2, a0',
0xa0197f98:'sw s1, 0(s4)',0xa0197f9c:'c.mv a1, s3',0xa0197f8e:'c.mv a0, s2',
0xa005300a:'c.mv s2, a1',0xa0053010:'c.mv s6, a0',0xa0053012:'c.mv s9, a2',0xa0053022:'c.mv s7, a3',
0xa005305e:'addi a0, zero, 0x140',0xa0053066:'c.mv s1, a0',
0xa0053100:'lui a2, 0xa0130',0xa0053104:'c.li a4, 1',0xa0053106:'c.mv a3, s9',
0xa0053108:'addi a2, a2, -0x6ba',0xa005310c:'c.mv a0, s1',0xa0053112:'c.mv s4, a0',
0xa0053126:'lui a5, 0xa0052',0xa005312e:'addi a5, a5, -0x254',
0xa0053132:'sw a5, 0x130(s1)',0xa0053136:'sw s7, 0x134(s1)',
0xa00531f4:'lw s2, 0xc(s1)',0xa005320a:'sw s2, 0(s6)',0xa005322c:'c.mv a0, s4'}
for pc,asm in expected.items(): assert by_pc[pc]['asm']==asm
checks=[]
def sx(v,n): return (v^(1<<(n-1)))-(1<<(n-1))
def word(pc): return int.from_bytes(rom[pc-base:pc-base+4],'little')
for pc,target in [(0xa0197f5e,0xa0052fee),(0xa0197f46,0xa002fcc8),(0xa0197f6c,0xa002e14e)]:
 a=word(pc); b=word(pc+4)
 assert a&0xfff==0x97 and b&0xfffff==0x80e7
 actual=(pc+sx(a&0xfffff000,32)+sx(b>>20,12))&0xfffffffe
 assert actual==target
 checks.append(dict(pc=hex(pc),kind='independent AUIPC/JALR target',target=hex(actual)))
for pc,target in [(0xa0053062,0xa0030eb8),(0xa005310e,0xa0030ef8),(0xa0197f9e,0xa01a9038)]:
 v=word(pc); assert v&0xfff==0xef
 disp=(v>>31<<20)|((v>>12&255)<<12)|((v>>20&1)<<11)|((v>>21&1023)<<1)
 actual=(pc+sx(disp,21))&0xffffffff; assert actual==target
 checks.append(dict(pc=hex(pc),kind='independent JAL target',target=hex(actual)))
for pc,reg,off in [(0xa0053132,15,0x130),(0xa0053136,23,0x134)]:
 v=word(pc); actual=[v&127,v>>12&7,v>>15&31,v>>20&31,sx((v>>25<<5)|(v>>7&31),12)]
 assert actual==[35,2,9,reg,off]
 checks.append(dict(pc=hex(pc),kind='independent store fields',fields=actual))
result=dict(task='A08',status='accepted_bounded_no_correction',capstone=__version__,
 windows=[{k:w[k] for k in ['start','end_exclusive']} for w in prior['windows']],
 checked_bytes=778,slots=slots,ordinary=ordinary,unknown=unknown,
 selected_instruction_assertions=[dict(pc=hex(pc),asm=asm) for pc,asm in expected.items()],encoding_checks=checks,
 limits=['No firmware execution','No new API/source attribution','No final consumer a0, runtime launch, adapter body or scheduler proof','Custom opcodes do not establish value preservation'])
(here/'review-index.json').write_text(json.dumps(result,indent=2)+'\n',encoding='utf8')
print('PASS',slots,ordinary,len(expected),len(checks),len(unknown))
