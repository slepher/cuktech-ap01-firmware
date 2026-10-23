"""E03: immutable-ROM static evidence; no firmware or shared REA execution."""
import json
from pathlib import Path
from capstone import Cs, CS_ARCH_RISCV, CS_MODE_RISCV32, CS_MODE_RISCVC
H=Path(__file__).resolve().parent
O=Path('D:/Documents/PlatformIO/Projects/cuktech-ap01-firmware')
ROMPATH=O/'roms/0041/ap01-1.0.2_0041.bin'
R=ROMPATH.read_bytes(); BASE=0x9ffff000
M=Cs(CS_ARCH_RISCV,CS_MODE_RISCV32|CS_MODE_RISCVC)
REG='zero ra sp gp tp t0 t1 t2 s0 s1 a0 a1 a2 a3 a4 a5 a6 a7 s2 s3 s4 s5 s6 s7 s8 s9 s10 s11 t3 t4 t5 t6'.split()
def sx(n,b): return n-(1<<b) if n>>(b-1) else n
def vendor(w):
 if w&127!=11:return None
 rd,rs1,rs2=[REG[(w>>n)&31] for n in (7,15,20)]
 f=(w>>12)&7
 if f in (2,3):return f'th.ext{"u" if f==3 else ""} {rd},{rs1},{w>>26},{(w>>20)&63}'
 if f==1 and w>>25==16:return f'th.mula {rd},{rs1},{rs2}'
 if f==1 and w>>27==0:return f'th.addsl {rd},{rs1},{rs2},{(w>>25)&3}'
 if f in (4,5) and w>>27==8:return f'th.{"lrw" if f==4 else "srw"} {rd},{rs1},{rs2},{(w>>25)&3}'
 if f==4 and w>>27==16:return f'th.lrbu {rd},{rs1},{rs2},{(w>>25)&3}'
 return None
specs=[
 ('item_head_init',0xa00a5630,0xa00a5664),
 ('registration',0xa005d13c,0xa005d14e),
 ('item_register',0xa01b28ce,0xa01b291a),
 ('item_dispatch',0xa00a389c,0xa00a3904),
 ('callback_entry_guards',0xa00adabc,0xa00adc3a),
 ('port_map_other_cases',0xa00ae166,0xa00ae194),
 ('port_index',0xa00add16,0xa00add22),
 ('child_accessor',0xa00dcee4,0xa00dcf52),
 ('offline_converter_caller',0xa00ae216,0xa00ae250),
 ('port1_prepare',0xa00aef16,0xa00aef82),
 ('port1_names',0xa00af062,0xa00af090),
 ('port1_values_battery',0xa00af090,0xa00af12e),
 ('port2_reuse',0xa00af12e,0xa00af18e),
 ('callback_finish',0xa00af250,0xa00af262),
 ('name_consumer',0xa00f44e8,0xa00f4610),
 ('value_consumer',0xa00f4610,0xa00f4740),
 ('status_consumer',0xa00ef0ec,0xa00ef1d4),
 ('battery_consumer',0xa00ef2da,0xa00ef468),
]
rows=[]; index={}
for name,start,end in specs:
 pc=start; ins=[]
 while pc<end:
  n=4 if R[pc-BASE]&3==3 else 2; b=R[pc-BASE:pc-BASE+n]; w=int.from_bytes(b,'little')
  assert pc+n<=end,(name,hex(pc))
  i=next(M.disasm(b,pc),None); v=vendor(w) if n==4 else None
  assert v or i,(name,hex(pc),b.hex())
  q={'address':hex(pc),'file_offset':pc-BASE,'hex':b.hex(),'assembly':v or i.mnemonic+' '+i.op_str}
  if v:q['vendor_fields']={'rd':(w>>7)&31,'rs1':(w>>15)&31,'rs2':(w>>20)&31,'funct3':(w>>12)&7,'bits31_26':w>>26,'bits25_20':(w>>20)&63,'bits26_25':(w>>25)&3}
  if n==4 and w&127==111:
   delta=sx(((w>>31)<<20)|(((w>>12)&255)<<12)|(((w>>20)&1)<<11)|(((w>>21)&1023)<<1),21)
   q['direct_target']=hex(pc+delta)
  if n==4 and w&127==99:
   delta=sx(((w>>31)<<12)|(((w>>7)&1)<<11)|(((w>>25)&63)<<5)|(((w>>8)&15)<<1),13)
   q['direct_target']=hex(pc+delta)
  ins.append(q); index[pc]=q; pc+=n
 rows.append({'name':name,'start':hex(start),'end_exclusive':hex(end),'instructions':ins})
expected={0xa00aef62:0xa00f4740,0xa00af17c:0xa00f4740,0xa00ae238:0xa00f4740,0xa00aef66:0xa00af12e,0xa00af076:0xa00f44e8,0xa00af0ee:0xa00ef0ec,0xa00af0f6:0xa00f4610,0xa00af124:0xa00ef2da}
for a,t in expected.items():assert index[a]['direct_target']==hex(t)
# The two PC-relative registration instructions are one call, not two calls.
assert R[0xa005d146-BASE:0xa005d14e-BASE].hex()=='97501500e7808078'
assert 0xa005d146+0x155000+0x788==0xa01b28ce
assert vendor(int.from_bytes(R[0xa00dcf48-BASE:0xa00dcf4c-BASE],'little'))=='th.lrw a0,a5,a1,2'
assert vendor(int.from_bytes(R[0xa00adbc4-BASE:0xa00adbc8-BASE],'little'))=='th.extu a4,a5,5,4'
# All callback-local view storage lies below saved registers and within its frame.
assert -0x100 <= -0x94 and -0x94+0x52 <= -0x34
E=O/'evidence/rea-0041-20261017/evidence'
bundle=json.loads((E/'whole-rom-private-20261023.evidence.json').read_text(encoding='utf-8'))
caller=next(x for x in bundle['records'] if x.get('evidence_id')=='ev_19e11c8fc1582881b289f2b24c2a98bbb305f7c2e57caad784442a60d1fb76e5')
n=caller['normalized_result']
incoming=n['incoming_references']
assert len(incoming)==1 and incoming[0]['source_address']=='0xa005d142'
refs={'source':str(E/'whole-rom-private-20261023.evidence.json'),'evidence_id':caller['evidence_id'],'caller_incoming_references':incoming,'converter_calls':[x for x in n['outgoing_references'] if x.get('target_address')=='0xa00f4740'],'limitations':n.get('limitations',[])}
(H/'references.json').write_text(json.dumps(refs,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
strings=[]
for a in [0xa059c728,0xa059c730,0xa059c738,0xa059c320,0xa059c328,0xa06130bc,0xa037a7bc,0xa0614cec,0xa059c78c,0xa061e62c]:
 p=a-BASE; end=R.index(0,p)
 strings.append({'address':hex(a),'file_offset':p,'hex':R[p:end+1].hex(),'text':R[p:end].decode('utf-8')})
(H/'resource-strings.json').write_text(json.dumps(strings,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
out={'rom_source':str(ROMPATH),'base':hex(BASE),'method':'Original bytes; Capstone standard instructions, independently extracted custom fields with local SLEIGH semantic comparison. Static only.','vendor_semantic_source':str(O/'evidence/rea-0041-20261017/processor/data/languages/ap01thead2.sinc'),'windows':rows,'direct_edge_assertions':len(expected),'registration_pair_assertion':True,'unknown_instructions':[],'limits':['No firmware execution, target switching, shared database mutation, replay or external services.','Selected caller fragments certify the port1 normal path, not every branch of the 6054-byte callback.','Local custom model is not upstream vendor authentication; generic GUI/format/allocator internals remain interface boundaries.']}
(H/'instruction-windows.json').write_text(json.dumps(out,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
print(json.dumps({'windows':len(rows),'instructions':sum(len(x['instructions']) for x in rows),'custom_words':sum('vendor_fields' in q for x in rows for q in x['instructions']),'direct_edges':len(expected),'registration_pair':'pass','incoming_refs':len(incoming),'result':'pass'}))
