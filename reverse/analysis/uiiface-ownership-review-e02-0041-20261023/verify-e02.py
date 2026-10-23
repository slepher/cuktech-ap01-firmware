"""E02 independent static byte/encoding checks. No firmware execution or REA target."""
import json
from pathlib import Path
from capstone import Cs, CS_ARCH_RISCV, CS_MODE_RISCV32, CS_MODE_RISCVC
HERE=Path(__file__).resolve().parent
ROOT=HERE.parents[2]
ORIG=Path('D:/Documents/PlatformIO/Projects/cuktech-ap01-firmware')
ROMPATH=ORIG/'roms/0041/ap01-1.0.2_0041.bin'
ROM=ROMPATH.read_bytes(); BASE=0x9ffff000
MD=Cs(CS_ARCH_RISCV,CS_MODE_RISCV32|CS_MODE_RISCVC)
source=ROOT/'reverse/analysis/uiiface-item-ownership-e01-0041-20261023/instruction-windows.json'
old=json.loads(source.read_text(encoding='utf-8'))
checks=[]
for w in old['windows']:
 start,end=int(w['start'],16),int(w['end_exclusive'],16)
 assert ROM[start-BASE:end-BASE].hex()==w['hex']
 pc=start; count=0; custom=0
 for r in w['instructions']:
  assert pc==int(r['address'],16)
  size=4 if ROM[pc-BASE]&3==3 else 2
  raw=ROM[pc-BASE:pc-BASE+size]
  assert raw.hex()==r['hex']
  if size==4 and int.from_bytes(raw,'little')&127==11: custom+=1
  else:
   inst=next(MD.disasm(raw,pc),None)
   assert inst and inst.size==size
   assert inst.mnemonic+' '+inst.op_str==r['assembly']
  pc+=size; count+=1
 assert pc==end
 checks.append({'window':w['name'],'start':hex(start),'end':hex(end),'raw_bytes_match':True,'standard_decode_match':True,'instructions':count,'custom_words':custom})
# Small critical slices selected by reviewer. Existing broad windows remain at E01.
ranges=[('dispatch50',0xa00a85cc,0xa00a85dc),('fallback_origin',0xa00a9410,0xa00a941a),
 ('ctk_allocations',0xa00a953c,0xa00a9598),('cleanup',0xa00a3dae,0xa00a3dea),
 ('cmd50_clear',0xa00a9340,0xa00a936a),('mask_notify_tail',0xa00a92aa,0xa00a92ae),
 ('callback',0xa00a38ee,0xa00a3902),('mask_clear',0xa00a38d6,0xa00a38dc),
 ('compare_bytes',0xa00501ee,0xa0050202),('consumer_guard',0xa00f47b4,0xa00f47f8),
 ('consumer_counts',0xa00f48a0,0xa00f4906),('consumer_soc',0xa00f4938,0xa00f499a),
 ('consumer_soc_fraction',0xa00f49f0,0xa00f4a12),('consumer_port',0xa00f4ade,0xa00f4b70),
 ('consumer_values',0xa00f4b7c,0xa00f4bc4),('consumer_loop_end',0xa00f4be0,0xa00f4bf8)]
def sx(n,bits): return n-(1<<bits) if n>>(bits-1) else n
rows=[]
for name,start,end in ranges:
 pc=start; instructions=[]
 while pc<end:
  size=4 if ROM[pc-BASE]&3==3 else 2; raw=ROM[pc-BASE:pc-BASE+size]; word=int.from_bytes(raw,'little')
  i=next(MD.disasm(raw,pc),None)
  r={'address':hex(pc),'file_offset':pc-BASE,'hex':raw.hex(),'standard_disassembly':i.mnemonic+' '+i.op_str if i else None}
  if size==4 and word&127==11:
   r['custom_encoding']={'opcode':word&127,'rd':(word>>7)&31,'funct3':(word>>12)&7,'rs1':(word>>15)&31,'rs2':(word>>20)&31,'bits31_26':word>>26,'bits25_20':(word>>20)&63,'bits31_27':word>>27,'bits26_25':(word>>25)&3}
  if size==4 and word&127==111:
   off=sx(((word>>31)<<20)|(((word>>12)&255)<<12)|(((word>>20)&1)<<11)|(((word>>21)&1023)<<1),21)
   r['direct_jump_target']=hex(pc+off)
  if size==4 and word&127==99:
   off=sx(((word>>31)<<12)|(((word>>7)&1)<<11)|(((word>>25)&63)<<5)|(((word>>8)&15)<<1),13)
   r['direct_branch_target']=hex(pc+off)
  instructions.append(r); pc+=size
 assert pc==end
 rows.append({'name':name,'instructions':instructions})
# Reviewer-selected exact call and mask assertions, independent of old assembler text.
expected={0xa00a9544:'ef40fee1',0xa00a9554:'ef40fee0',0xa00a9564:'ef40fedf',0xa00a9574:'ef40fede',0xa00a958c:'ef407edd',0xa00a38f6:'8297',0xa00a38d8:'0b502a41',0xa00f4af0:'8b3a4b1c',0xa00f4b4e:'0b37872c',0xa00501ee:'8b47e580',0xa00501f4:'8bc6e580'}
for addr,raw in expected.items(): assert ROM[addr-BASE:addr-BASE+len(raw)//2].hex()==raw
out={'rom_source':str(ROMPATH),'base':hex(BASE),'review_method':'Direct immutable ROM read; independent Capstone standard decode, independent instruction-length and operand bit extraction. Custom semantics checked against saved local SLEIGH only; no upstream authentication.', 'existing_evidence':str(source),'window_checks':checks,'critical_slices':rows,'selected_exact_encoding_checks':len(expected),'limits':['No execution, replay, firmware modification, global REA target or writable database.','Static normal-path review only; allocator/memcpy/log source versions remain unauthenticated.','Full response classification, page caller/dst consumption, +34/+38 UI consumers and global-deinit coupling remain outside certification.']}
(HERE/'independent-checks.json').write_text(json.dumps(out,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
print(json.dumps({'windows':len(checks),'instructions_checked':sum(x['instructions'] for x in checks),'custom_words':sum(x['custom_words'] for x in checks),'critical_slices':len(rows),'critical_instructions':sum(len(x['instructions']) for x in rows),'exact_checks':len(expected),'result':'pass'}))
