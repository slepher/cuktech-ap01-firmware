"""Read raw ROM anchors independently; neither F06 nor F07 scripts are inputs."""
import json
from pathlib import Path
from capstone import Cs, CS_ARCH_RISCV, CS_MODE_RISCV32, CS_MODE_RISCVC

HERE=Path(__file__).resolve().parent
ROM_PATH=Path('D:/Documents/PlatformIO/Projects/cuktech-ap01-firmware/roms/0041/ap01-1.0.2_0041.bin')
rom=ROM_PATH.read_bytes()
md=Cs(CS_ARCH_RISCV,CS_MODE_RISCV32|CS_MODE_RISCVC)
groups={
 'config/caller':[0xa005ccae,0xa005ccc2,0xa005ccba,0xa005ccbe,0xa005ccc6],
 'create/init':[0xa0084de8,0xa0084e26,0xa0084e2e,0xa0084e6e,0xa0084e72,0xa0084e78,0xa0084e7e,0xa0081a1c,0xa0081a22,0xa0081a28,0xa00819c4,0xa00819c8,0xa00819ca],
 'list insertion':[0xa008aece,0xa008aed0,0xa008aed8,0xa008aefc,0xa008af02],
 'publish':[0xa00873ea],
 'registration wrapper':[0xa007ffec,0xa007fff0,0xa007fff4],
 'descriptor/array':[0xa01b93c2,0xa01b9432,0xa01b9438,0xa01b943a,0xa01b9444,0xa01b9448,0xa01b9456],
 'sender':[0xa0081508,0xa0081516,0xa008151a,0xa0081522,0xa008152a,0xa008152e,0xa0081538,0xa008153c],
 'dispatch differences':[0xa008ad16,0xa008ad1c,0xa008ad1e,0xa008ad26,0xa008ad32,0xa008ad36,0xa008ad48,0xa008ad4e,0xa008ad56,0xa008ad5a,0xa008ad5c,0xa008ad72,0xa008ad76,0xa008ad78,0xa008ad80,0xa008ad92,0xa008ad96,0xa008ad98,0xa008ade0,0xa008ade8],
 'driver getter':[0xa007fe38,0xa007fe3e,0xa007fe42,0xa007fe44],
 'backend installation/cleanup':[0xa0086cc6,0xa0086cca,0xa00800c0,0xa00800de,0xa00800e2,0xa00800e8,0xa00800f2,0xa00800f4,0xa00800fc],
 'delete':[0xa0081570,0xa008157e,0xa0081582,0xa00815de,0xa00815e8,0xa00815ee,0xa00815f2,0xa00815f4,0xa00815f6,0xa00815fa,0xa0081600],
}
rows={}
for name,pcs in groups.items():
 for pc in pcs:
  raw=rom[pc-0x9ffff000:pc-0x9ffff000+4]
  size=4 if raw[0]&3==3 else 2
  inst=next(md.disasm(raw[:size],pc),None)
  if pc==0xa008ad78:
   w=int.from_bytes(raw,'little')
   assert w&127==11 and (w>>7)&31==13 and (w>>15)&31==15
   assert (w>>20)&63==15 and w>>26==15 and (w>>12)&7==3
   asm='vendor extu fields: rd=a3 rs1=a5 lsb=15 msb=15 (semantics inherited from F06 local model)'
  else:
   assert inst is not None,hex(pc)
   asm=inst.mnemonic+' '+inst.op_str
  rows[pc]={'pc':hex(pc),'group':name,'raw':raw[:size].hex(),'asm':asm}
expected={
 0xa0081570:'addi a1, zero, 0x29',0xa0086cca:'addi a2, zero, 0x29',
 0xa008ad26:'c.li a2, 0x14',0xa008ad32:'lbu a5, 0x14(s2)',
 0xa008ad36:'lw s4, 0x14(s2)',0xa008ad48:'sb a5, 0x14(s2)',
 0xa01b9456:'sb s2, 0x10(s1)',0xa008ad4e:'c.lui s8, 0x10',
 0xa008ad72:'and a3, a5, s8',0xa008ad76:'c.bnez a3, -0xa',
 0xa008ad16:'lbu a5, 0x18(a1)',0xa008ad56:'lbu s1, 0x18(s3)',
 0xa00819c4:'addi a5, zero, 0xff',0xa00819c8:'c.sw a5, 0x38(a0)',
 0xa00800e2:'sw zero, 0x2c(s2)',0xa00815e8:'lw a5, 0x2b8(s1)',
 0xa00815f6:'lw a0, 0x2b0(s1)',0xa0081538:'bne a0, a5, 0x10',
}
for pc,asm in expected.items(): assert rows[pc]['asm']==asm,(hex(pc),rows[pc],asm)
def target(pc):
 w=int.from_bytes(rom[pc-0x9ffff000:pc-0x9ffff000+4],'little')
 assert w&127==111
 imm=(w>>31)<<20|((w>>12)&255)<<12|((w>>20)&1)<<11|((w>>21)&1023)<<1
 return (pc+(imm-(1<<21) if imm&(1<<20) else imm))&0xffffffff
edges={0xa0084e6e:0xa00819d0,0xa0081a22:0xa0080d8e,0xa0081a28:0xa0081978,0xa008157e:0xa00814f4}
for pc,dst in edges.items(): assert target(pc)==dst,(hex(pc),hex(target(pc)))
src=json.loads((HERE/'candidate-review.json').read_text(encoding='utf-8'))
enums={v['name']:v['value'] for v in src['enum']}
assert enums['LV_EVENT_DELETE']==0x26 and enums['LV_EVENT_REFR_REQUEST']==0x35 and not src['enum_directives']
result={'mode':'static local reads only; no target execution/build/network','rom':str(ROM_PATH),'mapping':'VA - 0x9ffff000','anchors':list(rows.values()),'direct_edges':[{'pc':hex(p),'target':hex(t)} for p,t in edges.items()], 'enum_checks':{'DELETE':enums['LV_EVENT_DELETE'],'REFR_REQUEST':enums['LV_EVENT_REFR_REQUEST'],'directives_within_enum':src['enum_directives']},'boundary':'11 mapping groups are focused contract checks, not full-function byte identity or ISA certification.'}
(HERE/'rom-review.json').write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
print('PASS:',len(rows),'focused ROM anchors;',len(edges),'direct JAL edges; 65 enum entries parsed, no enum conditionals.')
