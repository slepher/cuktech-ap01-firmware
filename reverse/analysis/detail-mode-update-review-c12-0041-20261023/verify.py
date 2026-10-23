"""Independent C12 static ROM review; no firmware or model execution."""
import json
from pathlib import Path
from capstone import Cs, CS_ARCH_RISCV, CS_MODE_RISCV32, CS_MODE_RISCVC
HERE = Path(__file__).resolve().parent
TREE = HERE.parents[2]
SOURCE = Path('D:/Documents/PlatformIO/Projects/cuktech-ap01-firmware')
ROM = SOURCE/'roms/0041/ap01-1.0.2_0041.bin'
BASE = 0x9ffff000
rom = ROM.read_bytes()
prior = json.loads((HERE.parent/'detail-mode-update-c11-0041-20261023/instruction-evidence.json').read_text())
md = Cs(CS_ARCH_RISCV, CS_MODE_RISCV32 | CS_MODE_RISCVC)
def raw(pc,n): return rom[pc-BASE:pc-BASE+n]
def word(pc): return int.from_bytes(raw(pc,4),'little')
def sext(v,n): return v-(1<<n) if v&(1<<(n-1)) else v
# Decode direct-control immediates from original instruction bits, independently
# of Capstone's formatted operands and of C11's target table.
def target(pc):
 h=int.from_bytes(raw(pc,2),'little')
 if h&3 != 3:
  f=h>>13
  if f in (6,7):
   imm=((h>>12&1)<<8)|((h>>10&3)<<3)|((h>>5&3)<<6)|((h>>3&3)<<1)|((h>>2&1)<<5)
   return pc+sext(imm,9)
  assert f==5
  imm=((h>>12&1)<<11)|((h>>11&1)<<4)|((h>>9&3)<<8)|((h>>8&1)<<10)|((h>>7&1)<<6)|((h>>6&1)<<7)|((h>>3&7)<<1)|((h>>2&1)<<5)
  return pc+sext(imm,12)
 w=word(pc)
 if w&127==0x6f:
  imm=((w>>31)<<20)|((w>>21&1023)<<1)|((w>>20&1)<<11)|((w>>12&255)<<12)
  return pc+sext(imm,21)
 assert w&127==0x63
 imm=((w>>31)<<12)|((w>>25&63)<<5)|((w>>8&15)<<1)|((w>>7&1)<<11)
 return pc+sext(imm,13)
windows=[]; decoded={}; count=0
for p in prior['windows']:
 start,end=int(p['start'],16),int(p['end_exclusive'],16)
 pc=start; entries=[]
 while pc<end:
  n=4 if raw(pc,1)[0]&3==3 else 2
  r=raw(pc,n); ins=next(md.disasm(r,pc),None)
  if pc==0xa00f389e:
   assert ins is None and r.hex()=='8b34063c'
   asm='vendor word: see independently extracted fields'
  else:
   assert ins is not None and ins.size==n
   asm=ins.mnemonic+' '+ins.op_str; decoded[pc]=ins; count+=1
  old=next(x for x in p['instructions'] if int(x['address'],16)==pc)
  assert old['hex']==r.hex()
  if ins: assert old['assembly']==asm
  entries.append(dict(address=hex(pc),hex=r.hex(),assembly=asm));pc+=n
 assert pc==end
 windows.append(dict(name=p['name'],start=hex(start),end_exclusive=hex(end),instructions=entries))
expected={0xa00f38a2:0xa00f38aa,0xa00f38a4:0xa00a5c50,
 **{p:0xa00dcee4 for p in (0xa00f38b2,0xa00f38bc,0xa00f38c6,0xa00f38d0,0xa00f38da,0xa00f38e4)},
 0xa00f38ea:0xa00f38fe,0xa00f38f0:0xa00d9044,0xa00f38f8:0xa00d8f7c,
 0xa00f38fc:0xa00f3914,0xa00f3900:0xa00f391e,0xa00f3908:0xa00d8f7c,
 0xa00f3910:0xa00d9044,0xa00f3918:0xa00d8f7c,0xa00f391c:0xa00f393c,
 0xa00f3924:0xa00f394c,0xa00f3928:0xa00d8f7c,0xa00f3930:0xa00d8f7c,
 0xa00f3938:0xa00d9044,0xa00f394c:0xa00d8f7c,0xa00f3950:0xa00f38f4,
 0xa00d8f8c:0xa00d8fce,0xa00d8fd2:0xa00d7446,0xa00d8fd6:0xa00d9034,
 0xa00d9052:0xa00d9094,0xa00d9098:0xa00d749e,0xa00d909c:0xa00d9102,
 0xa00f3b18:0xa00f388c}
branches=[]
for pc,dest in expected.items():
 actual=target(pc);assert actual==dest
 branches.append(dict(address=hex(pc),hex=raw(pc,decoded[pc].size).hex(),target=hex(actual)))
w=word(0xa00f389e)
fields=dict(op=w&127,rd=w>>7&31,funct3=w>>12&7,rs1=w>>15&31,lsb=w>>20&63,msb=w>>26&63)
assert fields==dict(op=11,rd=9,funct3=3,rs1=12,lsb=0,msb=15)
ops={0xa00f389c:'s2, a0',0xa00f38a8:'s1, a0',0xa00f38aa:'s2, 4(s2)',
 0xa00f38ae:'a1, 0',0xa00f38b8:'a1, 1',0xa00f38c2:'a1, 2',
 **{p:'a1, 1' for p in (0xa00f38cc,0xa00f38d4,0xa00f38e0,0xa00f38ec,0xa00f38f4,0xa00f3904,0xa00f390c,0xa00f3914,0xa00f3920,0xa00f392c,0xa00f3934)},
 0xa00d8fd6:'a0, 0x5e',0xa00d909c:'a0, 0x66',
 0xa00d8fee:'a1, 0x24(s1)',0xa00d8ff0:'a1, a1, s3',0xa00d8ff4:'a1, 0x24(s1)',
 0xa00d90ce:'a5, 0x24(s1)',0xa00d90d0:'a4, s2',0xa00d90d8:'a5, a4',0xa00d90da:'a5, 0x24(s1)',
 0xa00f3b12:'a2, 8(s1)',0xa00f3b16:'a1, 0'}
for pc,op in ops.items(): assert decoded[pc].op_str==op
assert decoded[0xa00d8fd6].mnemonic=='c.bnez'
assert decoded[0xa00d909c].mnemonic=='c.beqz'
assert decoded[0xa00f38a2].mnemonic=='c.beqz'
assert decoded[0xa00f394a].mnemonic=='c.jr'
model=SOURCE/'evidence/rea-0041-20261017/ghidra/Ghidra/Processors/RISCV/data/languages'
reg=(model/'ap01thead2.reg.sinc').read_text().splitlines()
sleigh=(model/'ap01thead2.sinc').read_text().splitlines()
assert reg[1163:1165]==['  thlsb=(20,25)','  thmsb=(26,31)']
assert sleigh[3929:3934]==[':th.extu rd,rs1,15,0 is op0006=0xb & op1214=3 & thmsb=15 & thlsb=0 & rd & rs1','{','  local value:4 = rs1 << 16;','  rd = value >> 16;','}']
checks=dict(result='passed',windows=len(windows),bytes=sum(int(x['end_exclusive'],16)-int(x['start'],16) for x in windows),ordinary_instructions=count,vendor_words=1,raw_control_targets=len(branches),operand_checks=len(ops),c11_instruction_equality=True,local_model_excerpt_equal=True)
out=dict(task='C12',baseline='cb16c11',source_report='detail-mode-update-c11-0041-20261023.md',rom=str(ROM),mapping_base=hex(BASE),checks=checks,windows=windows,raw_control_targets=branches,vendor_fields=fields,model=dict(path=str(model),register_lines=[1164,1165],semantic_lines=[3930,3934]),limits=['Static decoding only; no target execution or control-flow simulation.','U16 semantics depend on existing local SLEIGH; no upstream ISA/version authentication.','Query and nested side effects are not expanded.'])
(HERE/'review-evidence.json').write_text(json.dumps(out,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
print(json.dumps(checks))
