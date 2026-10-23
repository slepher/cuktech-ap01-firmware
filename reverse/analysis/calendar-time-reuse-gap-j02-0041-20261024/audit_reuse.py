"""J02 existing-evidence inventory only; no ROM, disassembly, replay or execution."""
from pathlib import Path
import json

OUT=Path(__file__).resolve().parent
TREE=OUT.parents[2]
MAIN=Path('D:/Documents/PlatformIO/Projects/cuktech-ap01-firmware')
RH=MAIN/'reverse/rehost'
def read(p):return json.loads(p.read_text(encoding='utf8'))
w=read(RH/'weather-calendar-complete-0041.json')
s=read(RH/'system-complete-0041.json')
m=read(TREE/'reverse/reports/ap01/application-function-matrix-0041.json')
cal=read(RH/'calendar-complete-verification.json')
assert w['parent_runtime_verification']['status']=='passed-in-sim'
names=['lv_page_ui_date1_create','lv_page_ui_date1_dtl1_create','lv_page_ui_time1_create','lv_page_ui_time1_dtl1_create']
features=[]
for name in names:
 x=next(e for e in m['features'] if e['native_creator']==name)
 assert x['status']=='passed-in-sim' and x['remaining']==[]
 features.append({k:x[k] for k in ['id','native_creator','status','remaining','coverage_granularity']})
parents=[]
for name,count,shots in [('complete-nuttx-sim-verification.json',502,99),('complete-live-verification.json',30,15)]:
 d=read(RH/name)
 assert d['passed'] is True and d['step_count']==count and len(d['screenshots'])==shots
 selected=[dict(index=i,step=x) for i,x in enumerate(d['steps']) if any(t in str(x).lower() for t in ['12-hour format saved','24-hour format saved','actual c calendar subtitle'])]
 parents.append(dict(path=name,passed=True,step_count=count,screenshots=shots,selected_assertions=selected))
assert cal['status']=='passed' and cal['supported_days']==81772
handler=s['callback_branch_audit']['time_a00b3252']
assert handler['current_screen']==23 and handler['selection_modes']==[42,43,44]
oldrows=s['local_disassembly']['0xa00b3252']
assert len(oldrows)==296 and oldrows[0]['address']=='0xa00b3252' and oldrows[-1]['address']=='0xa00b35ec'
idx=read(TREE/'reverse/analysis/whole-rom-coverage-0041-20261023-round1.json')
f=next(x for x in idx['functions'] if x['address']=='0xa00b3252')
assert f['extent']['body']['total_bytes']==924 and f['dossiers']
old_windows=[]
for i in [0,1,2,3,4,8,20,31,32]:
 e=w['evidence'][i]
 assert e.get('stdout')
 old_windows.append(dict(pointer=f'weather-calendar-complete-0041.json#/evidence/{i}',address=e['address'],
                         provenance=e['tool'],classification='previous local ROM disassembly, not newly verified/exported'))
p=read(RH/'photo-evidence-round3.json')
assert p['time_options']['inline_creator_address']=='0xa00b0dd6'
result=dict(status='PASS',baseline='34ff6ba',new_functions=0,scope='calendar/time reuse inventory only',
 legacy_pending=w['remaining'],parent_acceptance=parents,matrix_features=features,
 calendar_summary={k:w['calendar'][k] for k in ['entry','converter','solar_festival','lunar_festival','solar_term','day_number','bounds','priority','timezone','rtc_boundary']},
 old_rom_evidence_index=old_windows,
 time_handler=dict(parent='system-complete-0041.json',audit_pointer='#/callback_branch_audit/time_a00b3252',
                   audit=handler,retained_instruction_rows=len(oldrows),extent=f['extent'],dossier_id=f['dossiers'][0]['evidence_id'],
                   status='existing raw/dossier and branch audit; not new function or new machine-level verification'),
 time_options=dict(source='photo-evidence-round3.json#/time_options',inline_creator='0xa00b0dd6',list_creator=p['time_options']['list_creator']),
 boundaries=['SIM pass does not prove native runtime ABI/hardware/cloud behavior',
             'Safe lunar bounds are SIM guards, defaultUTC0 and low32 wrap already have old ROM evidence',
             'No restart of H13-H18/E16-E19 counter/offset or H10 no-seed timer route',
             'Factory source-path mapping gaps do not establish missing conversion behavior'],
 recommendations=[],decision='Main requested behaviors already covered; no necessary new seeded behavior proposed',
 no_rom_read=True,no_zip_read=True,no_new_disassembly=True)
(OUT/'reuse-index.json').write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n',encoding='utf8')
print(json.dumps(dict(status='PASS',matrix_creators=4,parent_reports=2,old_time_handler_rows=296,new_functions=0,recommendations=0)))
