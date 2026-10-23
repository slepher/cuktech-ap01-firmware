"""Independent H18 bounded retained-evidence review. No directory/ROM sweep."""
from pathlib import Path
import json
import subprocess

OUT=Path(__file__).resolve().parent
TREE=OUT.parents[2]
PRIOR=TREE/'reverse/analysis/clock-counter-writer-h17-0041-20261024'
MAIN=Path('D:/Documents/PlatformIO/Projects/cuktech-ap01-firmware')
old=json.loads((PRIOR/'review-result.json').read_text(encoding='utf8'))
script=(PRIOR/'collect.py').read_text(encoding='utf8')
assert old['writer_seed_found'] is False and old['new_business_functions']==0
assert len(old['surveys'])==3 and all(s['query']=='62fc6c64|g_system_ticks|clock_timer|clock_systimer|clock_initialize' for s in old['surveys'])
assert old['surveys'][1]['exit_code']==old['surveys'][2]['exit_code']==1
assert all('*.evidence.json' in s['excluded'] for s in old['surveys'])
assert "'-g', '!*.evidence.json'" in script
assert "['source-xref', 'global-ref', 'globalref']" in script
assert old['named_ref_inventory']['matching_artifacts']==[]
root=MAIN/'evidence/rea-0041-20261017/evidence'
bundle=json.loads((root/'upper-complete.evidence.json').read_text(encoding='utf8'))
assert len(bundle['records'])==317==old['selected_complete_bundle']['records']
terms=['62fc6c64','g_system_ticks','clock_timer','clock_systimer','clock_initialize']
hit_indices=[i for i,r in enumerate(bundle['records']) if any(t in json.dumps(r.get('normalized_result',{})).lower() for t in terms)]
assert hit_indices==[108]
r=bundle['records'][108]
assert r['evidence_id']=='ev_4d6c9f986061ce8306d891bf4fe062d0411c134c2aeb388cd1253c071e04a722'
assert r['parameters']=={'procedure':'0xa00992d2'}
z=r['normalized_result']
refs=[x for x in z['outgoing_references'] if x.get('target_address')=='0x62fc6c64']
assert [x['source_address'] for x in refs]==['0xa00993a2','0xa00993ca','0xa0099412','0xa009948a']
assert all(x['kind']['type']=='READ' and x['kind']['read'] is True and x['kind']['write'] is False for x in refs)
assert old['selected_complete_bundle']['hits'][0]['references']==[{k:x.get(k) for k in ['source_address','target_address','kind']} for x in refs]
known_files=[]
for name in ['final-seeded-roots-135.json','root-collection-044.json','upper-final-collection-020.json','v2-all-roots-240.json']:
 d=json.loads((root/name).read_text(encoding='utf8'))['structuredContent']
 assert d['parameters']=={'procedure':'0xa00992d2'}
 known_files.append(dict(file=name,evidence_id=d['evidence_id'],procedure=d['parameters']['procedure']))
assert {Path(p).name for p in old['surveys'][0]['matching_files']}=={x['file'] for x in known_files}
# A very small independent opcode check corroborates READ without exporting the function.
raw_checks=[]
with (MAIN/'roms/0041/ap01-1.0.2_0041.bin').open('rb') as f:
 for ref in refs:
  pc=int(ref['source_address'],16);f.seek(pc-0x9ffff000);b=f.read(4);w=int.from_bytes(b,'little')
  assert (w&127,(w>>12)&7,(w>>15)&31,w>>20)==(3,2,19,0xc64)
  raw_checks.append(dict(pc=hex(pc),raw=b.hex(),opcode='LW',base='s3',displacement=-0x39c,rd=(w>>7)&31))
ops=z['native_value_flow']['operations']
examples=[]
for i in [1,11]:
 op=ops[i]
 assert op['opcode']=='INDIRECT' and op['is_dead'] is True and op['output']['location']=='0x62fc6c64'
 examples.append({k:op[k] for k in ['address','opcode','is_dead','output']})
candidate=json.loads((PRIOR/'candidate-excerpts.json').read_text(encoding='utf8'))
requested={Path(x['path']).name:[line['line'] for line in x.get('lines',[])] for x in candidate}
remote='''from pathlib import Path
import json
r=Path('/home/slepher/nuttx-ap01-sim/nuttx')
paths=['sched/clock/clock_timer.c','sched/clock/clock_systimer.c','sched/clock/clock_initialize.c']
out=[]
for p in paths:
 f=r/p
 ls=f.read_text().splitlines() if f.exists() else []
 out.append(dict(path=str(f),exists=f.exists(),lines={str(i):ls[i-1] for i in requested[f.name]}))
print(json.dumps(out))
'''
remote='requested='+repr(requested)+'\n'+remote
# Returned lines stay in memory; save equality/index results, not a second source copy.
p=subprocess.run(['wsl','-d','Ubuntu-24.04','--','python3','-c',remote],text=True,capture_output=True,encoding='utf8')
assert p.returncode==0,p.stderr
fresh=json.loads(p.stdout)
source_checks=[]
for oldc,newc in zip(candidate,fresh):
 assert oldc['path']==newc['path'] and oldc['exists']==newc['exists']
 for line in oldc.get('lines',[]):assert newc['lines'][str(line['line'])]==line['text']
 source_checks.append(dict(path=oldc['path'],exists=oldc['exists'],retained_lines_equal=len(oldc.get('lines',[]))))
result=dict(status='PASS',baseline='ed4735b',survey_audit='H17 script/result boundary audited; root inventories/text surveys not repeated',
 complete_bundle=dict(records=317,hits=hit_indices,evidence_id=r['evidence_id']),
 known_matching_files=known_files,read_reference_checks=[dict(pc=x['source_address'],type=x['kind']['type'],read=True,write=False) for x in refs],
 raw_checks=raw_checks,value_flow_examples=examples,candidate_checks=source_checks,
 decision='Accept bounded no-writer-seed conclusion; no claim writer does not exist',
 new_functions=0,limits=['No full-ROM/IRQ/offset search','H15/H16 reader inherited','No candidate-to-ROM binding','Writer/update cadence/start/epoch remain unknown'])
(OUT/'review-result.json').write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n',encoding='utf8')
print(json.dumps(dict(status='PASS',records=317,hits=1,read_refs=4,rom_bytes=16,candidate_paths=3)))
