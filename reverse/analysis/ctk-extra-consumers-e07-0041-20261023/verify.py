"""E07 bounded static call/reference checks; never execute firmware or open REA state."""
import importlib.util,json
from pathlib import Path
from bisect import bisect_right
HERE=Path(__file__).resolve().parent
ROOT=Path('D:/Documents/PlatformIO/Projects/cuktech-ap01-firmware')
EV=ROOT/'evidence/rea-0041-20261017'
BUNDLE=EV/'evidence/whole-rom-private-20261023.evidence.json'
s=importlib.util.spec_from_file_location('e05decode',HERE.parent/'ctk-app-close-e05-0041-20261023/decode.py')
d=importlib.util.module_from_spec(s);s.loader.exec_module(d)
old_custom=d.custom
def custom(w):
 if w&127==11 and (w>>12)&7==1 and w>>25==16:
  return 'th.mula '+','.join(d.regs[(w>>k)&31] for k in (7,15,20))
 return old_custom(w)
d.custom=custom
bundle=json.loads(BUNDLE.read_text()); records=bundle['records']
procs=next(r['normalized_result'] for r in records if r['operation']=='list_procedures')
ps=sorted((int(p['address'],16),p['value']) for p in procs if p['address'].startswith('0x'))
starts=[p[0] for p in ps]
queue=json.loads((EV/'whole-rom-graph-queue-20261023.json').read_text())['commands']
infos={c['arguments']['procedure']:i for i,c in enumerate(queue) if c['name']=='procedure_info'}
def save(name,o): (HERE/name).write_text(json.dumps(o,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
def graph(entry):
 i=infos[entry];path=EV/f'evidence/whole-rom-graph-20261023-{i:03}.json'
 e=json.loads(path.read_text())['structuredContent']
 return dict(source=str(path),evidence_id=e['evidence_id'],body=e['normalized_result']['body'])
call_candidates=[]
for off in range(0x1000,0x1ba800,2):
 w=int.from_bytes(d.rom[off:off+4],'little');pc=off+d.BASE;t=None;kind=None
 if w&127==111:
  imm=((w>>31)<<20)|(((w>>12)&255)<<12)|(((w>>20)&1)<<11)|(((w>>21)&1023)<<1)
  t=pc+d.signed(imm,21);kind='JAL'
 elif w&127==0x17:
  v=int.from_bytes(d.rom[off+4:off+8],'little')
  if v&0x707f==0x67 and (v>>15)&31==(w>>7)&31:
   t=(pc+d.signed(w&0xfffff000,32)+d.signed(v>>20,12))&0xffffffff;kind='AUIPC/JALR'
 if t not in (0xa00a53c0,0xa01b28ce):continue
 owner=ps[bisect_right(starts,pc)-1][0];g=graph(hex(owner))
 in_body=any(int(r['start'],16)<=pc<=int(r['end'],16) for r in g['body']['ranges'])
 row=dict(address=hex(pc),target=hex(t),kind=kind,owner=hex(owner) if in_body else None,preceding_entry=hex(owner),inside_retained_body=in_body,owner_body_source=g,
          instructions=d.decode(pc,pc+(8 if kind=='AUIPC/JALR' else 4)))
 call_candidates.append(row)
assert len([r for r in call_candidates if r['target']=='0xa00a53c0'])==14
assert len([r for r in call_candidates if r['target']=='0xa01b28ce'])==3
save('focused-call-index.json',dict(rom=str(d.ROM),base=hex(d.BASE),scan_start='0xa0000000',scan_end_exclusive='0xa01b9800',
 method='Halfword aligned exact-target RV32 JAL and adjacent AUIPC/JALR encoding candidates, each compared with retained preceding-entry body; an out-of-body candidate has owner=null. Does not discover indirect, non-adjacent address materialization, alternative encodings or pointer aliases; is not a complete xref census.',matches=call_candidates))
# Only named question-facing windows: no entire large response/callback dump.
spans=[('subtype6_copy_log_and_mask',0xa00a9ac8,0xa00a9b3e),('subtype2_copy_log_and_mask',0xa00a9bae,0xa00a9c20),
 ('common_notify_tail',0xa00a8730,0xa00a873e),('item_lookup',0xa00a53c0,0xa00a53ee),
 ('item_notification_abi',0xa00a389c,0xa00a3904),('item_register',0xa01b28ce,0xa01b291a),
 ('diagnostic_callback',0xa00a3c8a,0xa00a3ce0),('internal_callback_registration',0xa00a8a82,0xa00a8a8c),
 ('internal_registration_call',0xa00a8b50,0xa00a8b5e),('details_registration',0xa00b0774,0xa00b0786),
 ('details_item_identity',0xa00f52b4,0xa00f52b8),('details_false_positive',0xa00f58a4,0xa00f58c8),
 ('orphan_getter_call',0xa00a1aa4,0xa00a1aac),('orphan_saved_item_pointer',0xa00a1acc,0xa00a1ad0),('orphan_scalar_load',0xa00a1b1c,0xa00a1b26),('command63_scalar_gate',0xa01917d0,0xa0191834),('item_extra_cleanup',0xa00a3dd2,0xa00a3dea)]
windows=[]
for name,a,b in spans:
 rows=d.decode(a,b);assert int(rows[-1]['address'],16)+len(bytes.fromhex(rows[-1]['hex']))==b,name
 windows.append(dict(name=name,start=hex(a),end_exclusive=hex(b),instructions=rows))
idx={int(r['address'],16):r for w in windows for r in w['instructions']}
for pc,raw in [(0xa00a9ac8,'03a98a03'),(0xa00a9bae,'03a94a03'),(0xa00a9b0e,'8bb7471c'),(0xa00f52b6,'ae84'),(0xa01917fc,'83474502')]:assert idx[pc]['hex']==raw,(hex(pc),idx[pc]['hex'])
assert idx[0xa00a9ad8]['target']=='0xa00501be'
assert idx[0xa00a9aea]['target']=='0xa000589c'
assert idx[0xa00a9bd2]['target']=='0xa000589c'
assert idx[0xa00a9b32]['target']=='0xa008b51a'
assert idx[0xa00a9c16]['target']=='0xa008b51a'
strings=[]
for va in [0xa0269934,0xa02698a8,0xa0268540]:
 off=va-d.BASE;end=d.rom.index(0,off);strings.append(dict(address=hex(va),file_offset=off,hex=d.rom[off:end+1].hex(),text=d.rom[off:end].decode('utf-8',errors='replace')))
save('instruction-evidence.json',dict(rom=str(d.ROM),base=hex(d.BASE),windows=windows,strings=strings,
 vendor_model_source=str(EV/'processor/data/languages/ap01thead2.sinc'),limits=['Static byte decoding, not execution. Shared model is not independently authenticated upstream ISA evidence.','Only retained boundaries and selected instruction windows; large callback bodies are not newly restored.']))
# Compact provenance and bounded offset candidates; full dossiers remain read-only at origin.
rs=[r for r in records if r['operation']=='analyze_function']
for f in (EV/'evidence').glob('whole-rom-retained-private-20261023-*.json'):
 e=json.loads(f.read_text())['structuredContent'];e['_source']=str(f);rs.append(e)
chosen={r['owner'] for r in call_candidates if r['owner']}|{'0xa00adabc','0xa00f5288','0xa00a3c8a'}
selected=[];seen=set()
for r in rs:
 n=r['normalized_result'];a=n['procedure']['address']
 if a not in chosen or a in seen:continue
 # Prefer full retained record for theme callback; same entry duplicates omitted.
 seen.add(a)
 offset_lines=[t for t in n['assembly'] if any(k in t for k in [' 0x34,',' 0x38,']) and ('lw ' in t or 'sw ' in t) and not t.endswith(', sp')]
 selected.append(dict(procedure=a,evidence_id=r['evidence_id'],source=r.get('_source',str(BUNDLE)),
  profile_digest=r['analysis_profile']['digest'],body=n['procedure']['body'],offset_34_38_literal_candidates=offset_lines,
  incoming_references=n['incoming_references'] if a in ('0xa00adabc','0xa00f5288','0xa00a3c8a') else [],
  limitations=n['limitations']))
save('retained-search-boundary.json',dict(source=str(BUNDLE),selected_dossiers=selected,
 selection='Only exact-target getter caller owners plus three known item callback identities. Literal offset candidate extraction is not pointer alias analysis; a +34 in an app/panel is not item+34.',
 missing_dossiers=sorted(chosen-seen)))
print(f'{len(call_candidates)} exact-target candidates (14 getter, 3 registry); {len(windows)} windows, {sum(len(w["instructions"]) for w in windows)} instructions; {len(selected)} selected dossiers; missing={sorted(chosen-seen)}')
