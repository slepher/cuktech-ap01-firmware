"""P-16: bounded ROM/retained evidence comparison, no model or target execution."""
import json
from pathlib import Path
from capstone import Cs, CS_ARCH_RISCV, CS_MODE_RISCV32, CS_MODE_RISCVC

ROOT = Path('D:/Documents/PlatformIO/Projects/cuktech-ap01-firmware')
OUT = Path(__file__).resolve().parent
BASE = 0x9ffff000
rom = (ROOT/'roms/0041/ap01-1.0.2_0041.bin').read_bytes()
old = json.loads((ROOT/'reverse/rehost/charge-complete-0041.json').read_text('utf-8'))
bundle = json.loads((ROOT/'evidence/rea-0041-20261017/evidence/whole-rom-private-20261023.evidence.json').read_text('utf-8'))
handler = next(e for e in bundle['records'] if e['evidence_id']=='ev_6044e70f4a6f785a665e891cedb82fc897de52716642b9e9bbe0538f9b9d4c40')
init = json.loads((ROOT/'reverse/analysis/uiiface-lifecycle-0041-20261023/retained-initializer.json').read_text('utf-8'))['function']
model_path = ROOT/'evidence/rea-0041-20261017/processor/data/languages/ap01thead2.sinc'
model = model_path.read_text('utf-8')
start = model.index(':th.extu rd,rs1,5,4 ')
model_snippet = model[start:model.index('\n}',start)+2]
assert 'local value:4 = rs1 << 26;' in model_snippet
assert 'rd = value >> 30;' in model_snippet
sources = {
 'handler': {'path':'evidence/rea-0041-20261017/evidence/whole-rom-private-20261023.evidence.json', 'evidence_id':handler['evidence_id'], 'analysis_profile':handler['analysis_profile']},
 'callback': {'path':'reverse/rehost/charge-complete-0041.json#/records/19','evidence_id':old['records'][19]['evidence_id'],'analysis_profile':None,'profile_note':'Historical record supplies no profile; custom0/extraout remains historical output.'},
 'getter_view': {'path':'reverse/rehost/charge-complete-0041.json#/records/7','evidence_id':old['records'][7]['evidence_id'],'analysis_profile':None},
 'initializer': {'path':'reverse/analysis/uiiface-lifecycle-0041-20261023/retained-initializer.json#/function','evidence_id':init['evidence_id'],'analysis_profile':init['profile']},
}
assemblies = {'handler':handler['normalized_result']['assembly'],'callback':old['records'][19]['assembly'],'getter_view':old['records'][7]['assembly'],'initializer':init['assembly']}
specs = [
 ('handler_object',0xa00f61e6,0xa00f6200,'handler'),
 ('root_dispatch',0xa00f6bf8,0xa00f6c40,'handler'),
 ('root_dispatch_A',0xa00f6cc4,0xa00f6cca,'handler'),
 ('select_1',0xa00f6e44,0xa00f6e66,'handler'),
 ('select_2',0xa00f6ef0,0xa00f6f12,'handler'),
 ('select_3',0xa00f6f9c,0xa00f6fbe,'handler'),
 ('select_4',0xa00f7048,0xa00f706a,'handler'),
 ('safe_enter',0xa00f7126,0xa00f715c,'handler'),
 ('switch_enter',0xa00f79d4,0xa00f7a00,'handler'),
 ('safe_request_index',0xa00f7daa,0xa00f7dda,'handler'),
 ('safe_request_index_off',0xa00f7fca,0xa00f8004,'handler'),
 ('item_getter_index',0xa00f3b42,0xa00f3b5a,'getter_view'),
 ('callback_object_type_selector',0xa00f531e,0xa00f5374,'callback'),
 ('safe_filter',0xa00f5b0a,0xa00f5b16,'callback'),
 ('switch_filter',0xa00f5b6c,0xa00f5b78,'callback'),
 ('item_descriptor',0xa00a8aca,0xa00a8b2a,'initializer'),
]
md = Cs(CS_ARCH_RISCV, CS_MODE_RISCV32|CS_MODE_RISCVC)
windows=[]
for name,a,b,source in specs:
 retained=[s for s in assemblies[source] if a<=int(s.split(':')[0],16)<b]
 ins=[]; pc=a
 while pc<b:
  raw=rom[pc-BASE:pc-BASE+4]; n=4 if raw[0]&3==3 else 2
  assert pc+n<=b,(name,hex(pc))
  d=next(md.disasm(raw[:n],pc),None)
  ins.append({'address':hex(pc),'hex':raw[:n].hex(),'standard_decode':d.mnemonic+' '+d.op_str if d else 'unknown-preserved'})
  pc+=n
 assert [int(s.split(':')[0],16) for s in retained]==[int(s['address'],16) for s in ins],name
 windows.append({'name':name,'start':hex(a),'end_exclusive':hex(b),'source':source,'hex':rom[a-BASE:b-BASE].hex(),'instructions':ins,'retained_assembly':retained})
extractions=[]
for a,rd in [(0xa00f5340,15),(0xa00f5350,14)]:
 w=int.from_bytes(rom[a-BASE:a-BASE+4],'little')
 fields={'opcode':w&127,'funct3':(w>>12)&7,'rd':(w>>7)&31,'rs1':(w>>15)&31,'msb':w>>26,'lsb':(w>>20)&63}
 assert fields=={'opcode':11,'funct3':3,'rd':rd,'rs1':15,'msb':5,'lsb':4}
 extractions.append({'address':hex(a),'word':hex(w),'fields':fields,'interpretation':'unsigned bits[5:4] of a5; destination a5 for log / a4 for selector','source':'independent raw field check against saved model snippet, not historical profile repair'})
result={'status':'PASS','rom_sha256_inherited':old['source_sha256'],'mapping':'offset=VA-0x9ffff000','sources':sources,'windows':windows,'independent_model_reference':{'path':str(model_path),'snippet':model_snippet,'upstream_original_provenance':'unknown; saved local model only; no model executed or changed'},'extractions':extractions,'checks':{'windows':len(windows),'bytes':sum(b-a for _,a,b,_ in specs),'retained_address_alignment':True,'raw_type_fields':True},'limits':['No universal descriptor-to-array-index invariant established','No request acknowledgement established','No fifth selector constructor established in this bounded handler']}
(OUT/'static-evidence.json').write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n','utf-8')
print(json.dumps(result['checks']))
