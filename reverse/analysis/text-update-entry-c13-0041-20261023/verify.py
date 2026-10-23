"""C13 read-only static ROM decoding; never executes firmware or business models."""
import json
from pathlib import Path
from capstone import Cs, CS_ARCH_RISCV, CS_MODE_RISCV32, CS_MODE_RISCVC
HERE=Path(__file__).resolve().parent
TREE=HERE.parents[2]
SOURCE=Path('D:/Documents/PlatformIO/Projects/cuktech-ap01-firmware')
ROM=SOURCE/'roms/0041/ap01-1.0.2_0041.bin'
BASE=0x9ffff000
rom=ROM.read_bytes()
md=Cs(CS_ARCH_RISCV,CS_MODE_RISCV32|CS_MODE_RISCVC)
def raw(pc,n):return rom[pc-BASE:pc-BASE+n]
def sext(v,n):return v-(1<<n) if v&(1<<(n-1)) else v
def target(pc):
 h=int.from_bytes(raw(pc,2),'little')
 if h&3!=3:
  f=h>>13
  if f in (6,7):
   v=((h>>12&1)<<8)|((h>>10&3)<<3)|((h>>5&3)<<6)|((h>>3&3)<<1)|((h>>2&1)<<5)
   return pc+sext(v,9)
  assert f==5
  v=((h>>12&1)<<11)|((h>>11&1)<<4)|((h>>9&3)<<8)|((h>>8&1)<<10)|((h>>7&1)<<6)|((h>>6&1)<<7)|((h>>3&7)<<1)|((h>>2&1)<<5)
  return pc+sext(v,12)
 w=int.from_bytes(raw(pc,4),'little')
 if w&127==0x6f:
  v=((w>>31)<<20)|((w>>21&1023)<<1)|((w>>20&1)<<11)|((w>>12&255)<<12)
  return pc+sext(v,21)
 assert w&127==0x63
 v=((w>>31)<<12)|((w>>25&63)<<5)|((w>>8&15)<<1)|((w>>7&1)<<11)
 return pc+sext(v,13)
inv=json.loads((TREE/'reverse/analysis/whole-rom-coverage-0041-20261023-round1.json').read_text())
selected=[f for f in inv['functions'] if f['address'] in ('0xa0091ee4','0xa008bbd8')]
assert len(selected)==2
windows=[];decoded={}
for f in selected:
 ranges=f['extent']['body']['ranges'];assert len(ranges)==1
 start=int(ranges[0]['start'],16);end=int(ranges[0]['end'],16)+1
 pc=start;rows=[]
 while pc<end:
  n=4 if raw(pc,1)[0]&3==3 else 2;r=raw(pc,n)
  i=next(md.disasm(r,pc),None);assert i and i.size==n
  decoded[pc]=i
  rows.append(dict(address=hex(pc),hex=r.hex(),assembly=i.mnemonic+' '+i.op_str));pc+=n
 assert pc==end and i.mnemonic=='c.jr' and i.op_str=='ra'
 windows.append(dict(name=f['name'],start=hex(start),end_exclusive=hex(end),instructions=rows,extent_evidence=f['extent']['evidence_id'],calls_evidence=f['direct_calls']['evidence_id']))
expected={0xa0091f00:0xa0091f42,0xa0091f30:0xa008b51a,0xa0091f3e:0xa0019672,0xa0091f46:0xa00dddf4,0xa0091f4c:0xa0091f5e,0xa0091f54:0xa0091f5e,0xa0091f56:0xa008ab8a,0xa0091f68:0xa008bbd8,0xa0091f7a:0xa009166e,0xa008bbf2:0xa0053252,0xa008bc00:0xa008aea0,0xa008bc10:0xa008bc52,0xa008bc40:0xa008b51a,0xa008bc4e:0xa0019672,0xa008bc54:0xa0053252}
branches=[]
for pc,dst in expected.items():
 actual=target(pc);assert actual==dst
 branches.append(dict(address=hex(pc),hex=raw(pc,decoded[pc].size).hex(),target=hex(actual)))
# Ensure every direct control transfer in these complete windows is checked.
control={pc for pc,i in decoded.items() if i.mnemonic in ('jal','beq','bne','beqz','bnez','blt','bge','bltu','bgeu','c.j','c.beqz','c.bnez')}
assert control==set(expected)
ops={0xa0091ee4:('c.addi16sp','sp, -0x40'),0xa0091eea:('c.addi4spn','s0, sp, 0x20'),0xa0091ef0:('c.sw','a2, 8(s0)'),0xa0091ef2:('c.sw','a3, 0xc(s0)'),0xa0091ef4:('c.sw','a4, 0x10(s0)'),0xa0091ef6:('c.sw','a5, 0x14(s0)'),0xa0091ef8:('sw','a6, 0x18(s0)'),0xa0091efc:('sw','a7, 0x1c(s0)'),0xa0091f42:('c.mv','s1, a0'),0xa0091f44:('c.mv','s2, a1'),0xa0091f4a:('c.lw','a0, 0x2c(s1)'),0xa0091f4e:('lbu','a5, 0x5c(s1)'),0xa0091f52:('c.andi','a5, 0x10'),0xa0091f5a:('sw','zero, 0x2c(s1)'),0xa0091f5e:('addi','a1, s0, 8'),0xa0091f62:('c.mv','a0, s2'),0xa0091f64:('sw','a1, -0x14(s0)'),0xa0091f6c:('lbu','a5, 0x5c(s1)'),0xa0091f70:('c.sw','a0, 0x2c(s1)'),0xa0091f72:('c.mv','a0, s1'),0xa0091f74:('c.andi','a5, -0x11'),0xa0091f76:('sb','a5, 0x5c(s1)'),0xa008bbe2:('c.mv','a2, a0'),0xa008bbe4:('c.mv','a3, a1'),0xa008bbe6:('sw','a1, -0x1c(s0)'),0xa008bbea:('sw','a0, -0x18(s0)'),0xa008bbee:('c.li','a1, 0'),0xa008bbf0:('c.li','a0, 0'),0xa008bbf6:('addi','a1, a0, 1'),0xa008bbfa:('c.mv','a0, a1'),0xa008bbfc:('sw','a1, -0x14(s0)'),0xa008bc04:('lw','a1, -0x14(s0)'),0xa008bc08:('lw','a2, -0x18(s0)'),0xa008bc0c:('lw','a3, -0x1c(s0)'),0xa008bc52:('c.mv','s1, a0'),0xa008bc5c:('c.mv','a0, s1')}
for pc,(mn,op) in ops.items():assert (decoded[pc].mnemonic,decoded[pc].op_str)==(mn,op)
strings=[]
for a in [0xa02641a0,0xa0263224,0xa0263794,0xa02647f4,0xa01c38d4,0xa01c296c,0xa01c2994,0xa0263274,0xa0263318]:
 end=rom.index(0,a-BASE);r=rom[a-BASE:end+1]
 strings.append(dict(address=hex(a),hex=r.hex(),text=r[:-1].decode()))
assert next(s['text'] for s in strings if s['address']=='0xa0263794')=='lv_text_set_text_vfmt'
assert next(s['text'] for s in strings if s['address']=='0xa02647f4')=='lv_label_set_text_fmt'
# Bounded local source inventory only; no online lookup or version attribution.
source_matches=[]
for root in [SOURCE/'reverse/sdk',SOURCE/'tooling']:
 for p in root.rglob('*'):
  if p.is_file() and p.name.lower() in ('lv_label.c','lv_text.c','lv_version.h','lvgl.h','lv_mem.c'):
   source_matches.append(str(p))
checks=dict(result='passed',windows=len(windows),bytes=sum(int(w['end_exclusive'],16)-int(w['start'],16) for w in windows),ordinary_instructions=len(decoded),vendor_words=0,all_direct_control_targets=len(branches),operand_checks=len(ops),strings=len(strings),inventory_extents_match=True)
out=dict(task='C13',baseline='8b82f93',rom=str(ROM),mapping_base=hex(BASE),checks=checks,windows=windows,raw_control_targets=branches,operand_checks=[dict(address=hex(pc),mnemonic=mn,operands=op) for pc,(mn,op) in ops.items()],strings=strings,retained_inventory=str(TREE/'reverse/analysis/whole-rom-coverage-0041-20261023-round1.json'),source_search=dict(roots=[str(SOURCE/'reverse/sdk'),str(SOURCE/'tooling')],filenames=['lv_label.c','lv_text.c','lv_version.h','lvgl.h','lv_mem.c'],matches=source_matches,conclusion='No exact upstream version authenticated; vendor modifications remain unknown.'),limits=['Static byte reading/decoding only; no firmware execution or model simulation.','a0053252 formatting, a008aea0 allocator, a009166e refresh internals not expanded.','Formatting result length/termination convention inferred from two-pass pattern, not independently certified.','No shared writable REA database opened; existing REA extent/call provenance reused.'])
(HERE/'instruction-evidence.json').write_text(json.dumps(out,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
print(json.dumps(checks));print('local_source_matches='+str(len(source_matches)))
