"""D09: bounded new allocator/close windows. Static original bytes only."""
from pathlib import Path
import json
from capstone import Cs,CS_ARCH_RISCV,CS_MODE_RISCV32,CS_MODE_RISCVC
ROOT=Path('D:/Documents/PlatformIO/Projects/cuktech-ap01-firmware')
OUT=Path(__file__).resolve().parent
BASE=0x9ffff000
blob=(ROOT/'roms/0041/ap01-1.0.2_0041.bin').read_bytes()
mp=ROOT/'evidence/rea-0041-20261017/ghidra/Ghidra/Processors/RISCV/data/languages/ap01thead2.sinc'
model=mp.read_text().splitlines()
regs='zero ra sp gp tp t0 t1 t2 s0 s1 a0 a1 a2 a3 a4 a5 a6 a7 s2 s3 s4 s5 s6 s7 s8 s9 s10 s11 t3 t4 t5 t6'.split()
sx=lambda v,n:v-(1<<n) if v>>(n-1) else v
raw=lambda a,n:blob[a-BASE:a-BASE+n]
word=lambda a,n=4:int.from_bytes(raw(a,n),'little')
cs=Cs(CS_ARCH_RISCV,CS_MODE_RISCV32|CS_MODE_RISCVC)
clauses={}
def vendor(w):
 f=w>>12&7;rd=w>>7&31;r1=w>>15&31;r2=w>>20&31
 if f in (2,3):
  name=('ext','extu')[f-2];hi=w>>26&31;key=f':th.{name} rd,rs1,{hi},{r2} ';args=f'{regs[rd]}, {regs[r1]}, {hi}, {r2}'
 else:
  name={(4,16):'lrbu',(5,0):'srb'}[(f,w>>27)];key=f':th.{name} ';args=f'{regs[rd]}, {regs[r1]}, {regs[r2]}, {w>>25&3}'
 ids=[i for i,l in enumerate(model) if l.startswith(key)];assert len(ids)==1,key
 a=ids[0];b=next(i for i in range(a+1,len(model)) if model[i]=='}')
 clauses[key]={'line':a+1,'text':'\n'.join(model[a:b+1])}
 return f'th.{name} {args}'
windows=[('allocator_wait_retry',0xa00288c4,0xa00288d2),('allocator',0xa00288de,0xa002897c),('release_busy',0xa01b5c48,0xa01b5c9c),('final_file_dispatch',0xa0027d16,0xa0027d2a),('uart_close_to_lower',0xa002c68e,0xa002c700),('uart_close_late_optional',0xa002c744,0xa002c77a),('shutdown_TX',0xa00198c8,0xa001994c)]
rows={};out=[]
for name,a,b in windows:
 pc=a;rr=[]
 while pc<b:
  w=word(pc);n=4 if w&3==3 else 2;assert pc+n<=b
  if n==4 and w&127==11:text=vendor(w)
  else:
   ins=list(cs.disasm(raw(pc,n),pc));assert len(ins)==1 and ins[0].size==n,(hex(pc),raw(pc,n).hex())
   text=ins[0].mnemonic+' '+ins[0].op_str
  r={'va':hex(pc),'offset':hex(pc-BASE),'bytes':raw(pc,n).hex(),'asm':text};rr.append(r);rows[pc]=r;pc+=n
 out.append({'name':name,'start':hex(a),'end_exclusive':hex(b),'instructions':rr})
def jal(pc):
 w=word(pc);assert w&127==0x6f
 v=((w>>31)<<20)|((w>>12&255)<<12)|((w>>20&1)<<11)|((w>>21&1023)<<1)
 return (pc+sx(v,21))&0xffffffff
def pair(pc):
 w=word(pc);n=word(pc+4);assert w&127==0x17 and n&127==0x67 and w>>7&31==n>>15&31
 return (pc+(w&0xfffff000)+sx(n>>20,12))&0xffffffff
checks=[]
for pc,t in [(0xa001a8ee,0xa00288de),(0xa001992a,0xa0024bb6),(0xa00288f4,0xa00288b8),(0xa00288ca,0xa002786c),(0xa0028900,0xa0027968),(0xa002890a,0xa00273cc),(0xa002894e,0xa00274b2)]:
 assert jal(pc)==t;checks.append([hex(pc),'JAL',hex(t)])
for pc,t in [(0xa001993a,0xa01b5c48),(0xa01b5c5a,0xa0027968),(0xa01b5c7c,0xa00273cc),(0xa01b5c88,0xa00274b2)]:
 assert pair(pc)==t;checks.append([hex(pc),'AUIPC/JALR',hex(t)])
def branch(pc):
 w=word(pc);assert w&127==0x63
 v=((w>>31)<<12)|((w>>7&1)<<11)|((w>>25&63)<<5)|((w>>8&15)<<1)
 return (pc+sx(v,13))&0xffffffff
def cb(pc):
 w=word(pc,2);assert w&3==1 and w>>13 in (6,7)
 v=((w>>12&1)<<8)|((w>>10&3)<<3)|((w>>5&3)<<6)|((w>>3&3)<<1)|((w>>2&1)<<5)
 return (pc+sx(v,9))&0xffffffff
for pc,t in [(0xa00288ce,0xa00288c8),(0xa00288f8,0xa002890e),(0xa0028904,0xa002891e),(0xa0028956,0xa0028910),(0xa01b5c62,0xa01b5c90),(0xa002c6a4,0xa002c6b6),(0xa0019912,0xa001994c),(0xa001991e,0xa001994c)]:
 assert branch(pc)==t;checks.append([hex(pc),'B',hex(t)])
for pc,t in [(0xa002892c,0xa002896c),(0xa0028932,0xa0028974),(0xa002893c,0xa002894a),(0xa01b5c72,0xa01b5c84),(0xa00198fe,0xa001994c),(0xa002c6f4,0xa002c700),(0xa002c74a,0xa002c6b0)]:
 assert cb(pc)==t,(hex(pc),hex(cb(pc)),hex(t));checks.append([hex(pc),'CB',hex(t)])
expected={0xa002c6ba:'sb zero, 0(s1)',0xa002c6c0:'c.lw a5, 0x18(a5)',0xa002c6ec:'c.lw a5, 0xc(a5)',0xa002c6fc:'c.lw a5, 4(a5)',0xa002c6fe:'c.jalr a5',0xa00198fa:'lbu a5, 0xe(s1)',0xa0019904:'addi s2, gp, 0x3dc',0xa0019946:'c.li a4, 0xf',0xa0019948:'th.srb a4, s2, a5, 0',0xa01b5c74:'th.srb zero, s2, a5, 0',0xa0028946:'th.srb a4, a5, s1, 0',0xa0028952:'th.ext a0, s1, 7, 0'}
for pc,t in expected.items():assert rows[pc]['asm']==t,(hex(pc),rows[pc]);checks.append([hex(pc),'field/width',t])
# Pointer identities already D03-proven; re-read only close slots, explicitly old-contract review.
constants={'old_contract_review':{'inode_close_slot':hex(word(0xa066d7cc)),'lower_shutdown_slot':hex(word(0xa01bcb1c)),'device_initial_4bytes':raw(0xa00031e4,4).hex()}}
assert word(0xa066d7cc)==0xa002c678 and word(0xa01bcb1c)==0xa00198bc
result={'method':'Original ROM; new bounded allocator/close windows, inherited descriptor/IRQ contracts not reexported; no execution','rom':str(ROOT/'roms/0041/ap01-1.0.2_0041.bin'),'windows':out,'vendor_clauses':clauses,'checks':checks,'constants':constants}
(OUT/'instructions.json').write_text(json.dumps(result,indent=2,ensure_ascii=False)+'\n',encoding='utf-8')
print('windows',len(out),'bytes',sum(b-a for _,a,b in windows),'instructions',len(rows),'checks',len(checks),'vendor clauses',len(clauses));print(constants)
