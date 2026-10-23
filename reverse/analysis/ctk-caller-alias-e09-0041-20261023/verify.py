"""E09 reuse check: read retained round3 dossier and necessary original words only."""
from pathlib import Path
import json,re
HERE=Path(__file__).resolve().parent
ROOT=Path('D:/Documents/PlatformIO/Projects/cuktech-ap01-firmware')
SOURCE=ROOT/'evidence/rea-0041-20261017/round3/evidence/whole-rom-round3-open-20261023-002.json'
e=json.loads(SOURCE.read_text())['structuredContent'];n=e['normalized_result'];a=n['assembly'];body=n['procedure']['body']
assert e['evidence_id']=='ev_dac9ee80a05e233e383bc1f10b5d225121efdc2db62ab51519958d8f220d15c3'
assert body['ranges']==[{'start':'0xa00a12d0','end':'0xa00a24a5'}]
by={int(s.split(':',1)[0],16):s for s in a}
checks={0xa00a12d0:'c.addi16sp sp, -0x110',0xa00a12da:'c.addi4spn s0, sp, 0x110',0xa00a1450:'sub64 a0, a2, a4',0xa00a1aa4:'andi a0, s10, 0xff',0xa00a1aa8:'jal ra, 0xa00a53c0',0xa00a1acc:'sw a0, -0xe4, s0',0xa00a1b20:'lhu a6, 0xa, a0',0xa00a1b24:'c.li a0, 0x4',0xa00a1cd0:'lw a5, -0xe4, s0',0xa00a1cd8:'lbu a2, 0x12, a5',0xa00a1ce2:'th.srb a2, a3, s10, 0x0'}
for pc,s in checks.items():assert by[pc].split(': ',1)[1]==s,(hex(pc),by[pc])
slot=[s for s in a if '-0xe4, s0' in s];assert len(slot)==2
rom=(ROOT/'roms/0041/ap01-1.0.2_0041.bin').read_bytes();base=0x9ffff000
raw={0xa00a1450:'7715e6c2',0xa00a1aa4:'1375fd0f',0xa00a1aa8:'ef309011',0xa00a1acc:'232ea4f0',0xa00a1b20:'0358a500',0xa00a1b24:'1145',0xa00a1cd0:'8327c4f1',0xa00a1cd8:'03c62701',0xa00a1ce2:'0bd6a601'}
for pc,h in raw.items():assert rom[pc-base:pc-base+len(bytes.fromhex(h))].hex()==h
# Independent raw load/store width, registers, offset and special word fields.
w=int.from_bytes(bytes.fromhex(raw[0xa00a1cd8]),'little');assert [w&127,w>>12&7,w>>7&31,w>>15&31,w>>20]==[3,4,12,15,0x12]
w=int.from_bytes(bytes.fromhex(raw[0xa00a1450]),'little');assert [w&127,w>>12&7,w>>25,w>>7&31,w>>15&31,w>>20&31]==[0x77,1,0x61,10,12,14]
model=ROOT/'evidence/rea-0041-20261017/round3/scripts/ap01thead3.sinc';assert ':sub64 rd,rs1,rs2 is op0006=0x77 & op1214=1 & op2531=0x61' in model.read_text()
assert 'halt_baddata' not in n['pseudocode'];assert 'Bad instruction' not in n['pseudocode']
summary=json.loads((ROOT/'reverse/analysis/uart-retry-receive-0041-20261023.json').read_text())
out={'status':'covered-in-prior-round3; no new functionality or function export','source':str(SOURCE),'evidence_id':e['evidence_id'],'profile_digest':e['analysis_profile']['digest'],'body':body,'inherited_assembly_anchors':[by[pc] for pc in checks],'slot_references':slot,'original_byte_recheck':{hex(pc):h for pc,h in raw.items()},'model_clause_source':str(model),'limits':['Raw rereads are old-conclusion verification, not new ROM behavior recovery.','Round3 decompiler still warns unreachable blocks at a00a1abc/a00a1adc/a00a23f0; use retained assembly for local pointer identity.','Only direct returned-item/slot chain; not all CTK aliases or no-consumer proof.','No model/replay execution, no whole-function export.']}
(HERE/'reuse-result.json').write_text(json.dumps(out,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
print('PASS: inherited round3 body, 11 assembly anchors, unique slot store/read, 9 old-byte rechecks, SUB64 fields; new recovery 0')
