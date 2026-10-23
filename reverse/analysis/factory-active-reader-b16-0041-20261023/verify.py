"""B16 retained-evidence and selected raw instruction verification; no localization rescan."""
from pathlib import Path
import json
from capstone import Cs,CS_ARCH_RISCV,CS_MODE_RISCV32,CS_MODE_RISCVC
HERE=Path(__file__).resolve().parent
TREE=HERE.parents[2]
SOURCE=Path('D:/Documents/PlatformIO/Projects/cuktech-ap01-firmware')
BASE=0x9ffff000
rom=(SOURCE/'roms/0041/ap01-1.0.2_0041.bin').read_bytes()
md=Cs(CS_ARCH_RISCV,CS_MODE_RISCV32|CS_MODE_RISCVC)
expected=[('0xa005b7b4','0xa005b7ba','238ce72a','store'),('0xa009f178','0xa009f17c','83c7872b','load')]
loc=json.loads((HERE/'localization.json').read_text())
assert [(r['lui'],r['candidate'],r['hex'],r['kind']) for r in loc['candidates']]==expected
rows=[]
for name,start,end in [('known_initializer_write',0xa005b7b4,0xa005b7be),('known_callback_gate',0xa009f178,0xa009f184),('known_callback_return',0xa009f346,0xa009f348)]:
 seq=list(md.disasm(rom[start-BASE:end-BASE],start));assert sum(i.size for i in seq)==end-start
 rows.append({'name':name,'start':hex(start),'end_exclusive':hex(end),'instructions':[{'address':hex(i.address),'file_offset':i.address-BASE,'hex':i.bytes.hex(),'decode':i.mnemonic+' '+i.op_str} for i in seq]})
def word(a,n=4):return int.from_bytes(rom[a-BASE:a-BASE+n],'little')
assert word(0xa005b7b4)==0x62fc97b7
assert word(0xa005b7b8,2)==0x4705
w=word(0xa005b7ba)
assert (w&127,w>>12&7,w>>15&31,w>>20&31,((w>>25)<<5)|(w>>7&31))==(35,0,15,14,0x2b8)
assert word(0xa009f178)==0x62fc97b7
w=word(0xa009f17c)
assert (w&127,w>>12&7,w>>7&31,w>>15&31,w>>20)==(3,4,15,15,0x2b8)
w=word(0xa009f180)
imm=((w>>31)<<12)|((w>>7&1)<<11)|((w>>25&63)<<5)|((w>>8&15)<<1)
assert (w&127,w>>12&7,w>>15&31,w>>20&31,0xa009f180+imm)==(99,0,15,0,0xa009f346)
assert word(0xa009f346,2)==0x8082
# Check selected bytes against the already retained callback window, not just Capstone.
old=json.loads((TREE/'reverse/analysis/factory-test-0041-20261023/instruction-windows.json').read_text())['windows'][0]
a=int(old['start'],16);b=int(old['end_exclusive'],16)
assert bytes.fromhex(old['hex'])==rom[a-BASE:b-BASE]
ret=json.loads((HERE/'retained-reference-hits.json').read_text())
assert {g['procedure'] for g in ret['groups']}=={'0xa005a736'}
# Follow each saved JSON pointer back to immutable retained evidence; no new global search.
refs=[]
for g in ret['groups']:
 d=json.loads((SOURCE/'evidence/rea-0041-20261017'/g['source']).read_text(encoding='utf-8'))
 for h in g['selected_hits']:
  v=d
  for part in h['json_pointer'].split('/')[1:]:v=v[int(part)] if isinstance(v,list) else v[part]
  assert '62fc92b8' in v and h['excerpt'] in v
  if '/outgoing_references/' in h['json_pointer']:
   v=d
   for part in h['json_pointer'].rsplit('/',1)[0].split('/')[1:]:v=v[int(part)] if isinstance(v,list) else v[part]
   assert v['source_address']=='0xa005b7ba' and v['kind']['write'] and not v['kind']['read']
   refs.append({'source':g['source'],'pointer':h['json_pointer'].rsplit('/',1)[0],'source_address':v['source_address'],'type':v['kind']['type']})
out={'status':'passed','method':'Selected raw bitfields plus Capstone and retained bytes/pointers; static only; no new hash; no second localization run','windows':rows,'retained_exact_target_references':refs,'retained_literal_hit_groups':[{'source':g['source'],'procedure':g['procedure'],'literal_hit_count':g['literal_hit_count'],'native_value_flow_hit_count':g['native_value_flow_hit_count']} for g in ret['groups']],'external_reader':'unresolved within stated search boundary'}
(HERE/'instruction-evidence.json').write_text(json.dumps(out,indent=2)+'\n')
print('PASS: 24 selected ROM bytes, raw LUI/SB/LBU/BEQ/return fields, retained callback bytes and saved source pointers; external reader unresolved')
