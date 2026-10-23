"""J04 bounded retained-evidence inventory. Does not open/read the ROM."""
import json
import re
import subprocess
from pathlib import Path

HERE=Path(__file__).resolve().parent
TREE=HERE.parents[2]
MAIN=Path('D:/Documents/PlatformIO/Projects/cuktech-ap01-firmware')
index_path=MAIN/'reverse/analysis/whole-rom-coverage-0041-20261023-round1.json'
index=json.loads(index_path.read_text(encoding='utf-8'))
functions={f['address']:f for f in index['functions']}
seed=functions['0xa00a4cac']
expected=['0xa00a4116','0xa00a491c','0xa00a4aa0']
assert seed['extent']['body']['ranges']==[{'start':'0xa00a4cac','end':'0xa00a4d71'}]
assert seed['extent']['body']['total_bytes']==198
assert all(c in seed['direct_calls']['callees'] for c in expected)
source=next(p for p in index['source_paths'] if p['text']=='factory_ui/lv_window_slider.c')
owners={r['owner']['procedure'] for r in source['references']}
assert all(c in owners for c in expected)
support=[]
for suffix,address in [('036','0xa00a4116'),('043','0xa00a491c'),('047','0xa00a4aa0')]:
    path=MAIN/f'evidence/rea-0041-20261017/evidence/whole-rom-private-20261023-{suffix}.json'
    r=json.loads(path.read_text(encoding='utf-8'))['structuredContent']
    z=r['normalized_result']
    assert z['procedure']['address']==address
    assert any(c['address']=='0xa00a4cac' for c in z['callers'])
    assert any(s.get('value')=='factory_ui/lv_window_slider.c' for s in z['referenced_strings'])
    support.append({'path':str(path),'selector':'structuredContent.normalized_result',
                    'procedure':address,'evidence_id':r['evidence_id'],
                    'existing_body_ranges':z['procedure']['body']['ranges'],
                    'caller_confirmed':'0xa00a4cac'})

query='a00a4cac|a00a4116|a00a491c|a00a4aa0|factory_ui/lv_window_slider.c|lv_window_slider_get_active_win_idx|lv_window_slider_get_window_count|lv_window_slider_set_active_by_idx'
surveys=[]
for root,glob in [(TREE/'reverse/reports/ap01','*.md'),(MAIN/'reverse/rehost','*.json')]:
    p=subprocess.run(['rg','-l','-i',query,str(root),'-g',glob,
                       '-g','!factory-reuse-gap-j04-0041-20261024.md'],capture_output=True)
    assert p.returncode in [0,1],p.stderr
    surveys.append({'root':str(root),'query':query,'glob':glob,
                    'matching_files':p.stdout.decode().splitlines(),'exit_code':p.returncode})
assert surveys[1]['exit_code']==1
selected_complete=[]
complete_terms='factory_ui|FactoryTestMode|a00a4116|a00a4aa0|a009f178|62fc92b8'
for path in [MAIN/'reverse/rehost/system-complete-0041.json',
             *sorted((MAIN/'reverse/rehost').glob('settings-0041*.json'))]:
    count=len(re.findall(complete_terms,path.read_text(encoding='utf-8'),re.I))
    selected_complete.append({'path':str(path),'query':complete_terms,'literal_matches':count})
assert all(x['literal_matches']==0 for x in selected_complete)
factory_terms=['a00a4116','a00a491c','a00a4aa0','a00a4cac',
               'lv_window_slider_get_active_win_idx','lv_window_slider_get_window_count','lv_window_slider_set_active_by_idx']
daily_terms=['a00b3106','a00b2ff4','a00ab628']
cross=[]
rehost=MAIN/'reverse/rehost'
for path in sorted({rehost/'guide-complete-0041.json',*rehost.glob('guide-*.json'),
                    *rehost.glob('page-logic*.json')}):
    s=path.read_text(encoding='utf-8').lower()
    cross.append({'path':str(path),'factory_term_counts':{t:s.count(t) for t in factory_terms},
                  'daily_term_counts':{t:s.count(t) for t in daily_terms}})
assert all(sum(x['factory_term_counts'].values())==0 for x in cross)
append_path=TREE/'reverse/analysis/screen-host-append-20261020.json'
append=json.loads(append_path.read_text(encoding='utf-8'))
host_functions=[x['procedure'] for x in append['functions']]
assert '0xa00b3106' in host_functions
assert not any(c in host_functions for c in expected)
slide=json.loads((TREE/'reverse/analysis/screen-host-slider-20261020.json').read_text(encoding='utf-8'))
assert not slide['full_ui_executed'] and not slide['hardware_verified']
h07=TREE/'reverse/reports/ap01/weather1-navigation-h07-0041-20261023.md'
assert 'a00b3106' in h07.read_text(encoding='utf-8')

matrix=json.loads((TREE/'reverse/reports/ap01/application-function-matrix-0041.json').read_text(encoding='utf-8'))
assert len(matrix['native_creators'])==33
assert not any('factory_ui' in m for m in matrix['native_modules'])
factory_services=[s.get('name') for s in matrix['service_contracts'] if 'factory' in str(s).lower()]
assert factory_services==['ap01_sim_factory_reset']
old_map_path=MAIN/'reverse/analysis/factory-reference-map-0041.json'
old_map=json.loads(old_map_path.read_text(encoding='utf-8'))
old_scopes=[]
for name in ['PogoPinMng/FactoryTestMode.c','factory_ui/lv_window_slider.c']:
    entry=old_map['files'][name]
    old_scopes.append({'path':name,'in_ui_matrix':entry['in_ui_matrix'],
                       'old_function_links':entry['functions'],
                       'full_file_reverse_complete':entry['full_file_reverse_complete'],
                       'limit':'Old source association count is not semantic coverage and was superseded locally by later reports/index.'})
    assert entry['in_ui_matrix'] is False and entry['full_file_reverse_complete'] is False
result={'status':'PASS','baseline':'09e11d0','scope':'Retained-evidence scope inventory, no new ROM bytes/decompilation',
        'application':{'matrix_path':str(TREE/'reverse/reports/ap01/application-function-matrix-0041.json'),
                        'SIM_creators':33,'factory_ui_module_in_matrix':False,'factory_named_services':factory_services,
                        'limit':'Settings factory reset service is not production-test UI or hardware testing.'},
        'old_reference_map':{'path':str(old_map_path),'selected_scope':old_scopes},
        'selected_seed':{'address':seed['address'],'index_path':str(index_path),
                         'extent':seed['extent'],'direct_calls':seed['direct_calls'],
                         'dossiers_count':len(seed['dossiers']),
                         'historical_contracts_count':len(seed['historical_contracts']),
                         'support':support,
                         'source_path_binding':{'text':source['text'],'source_address':source['address'],
                             'xref_evidence':sorted({r['xref_evidence'] for r in source['references']}),
                             'selected_callee_owners':expected},
                         'proposal':'Only entry-to-slider argument/index/state contract; no root destruction, GPIO stop/close, driver sweep or hardware effect.',
                         'limit':'Metadata confirms extent/call edges, not normal event/ABI or runtime reachability.'},
        'bounded_reuse':surveys,
        'selected_system_settings_reuse':selected_complete,
        'cross_component_reuse':{'guide_page_queries':cross,'host_append_path':str(append_path),
          'host_append_procedures':host_functions,'host_slider_scope':slide['scope'],
          'host_slider_full_ui_executed':slide['full_ui_executed'],
          'host_slider_hardware_verified':slide['hardware_verified'],'H07':str(h07),
          'limit':'Daily W navigation coverage does not certify factory_ui component or FactoryTestMode/GPIO association.'},
        'inherited_results':['factory initializer/sample/fd failure cleanup','GPIO three cycles/constant digit write',
                            'factory long buzzer local block','B16/B17 external-active-reader bounded unknown'],
        'not_proposed':['repeat active scan','success-path stop/close without seed','root destructor without target seed',
                        'all factory resources/driver classification'],
        'new_function_recovery':0,'new_ROM_bytes':0,'new_decompilations':0,'full_library_exclusions':0}
(HERE/'reuse-result.json').write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
print(json.dumps({'status':'PASS','seed':'0xa00a4cac','extent_bytes':198,
                  'crosschecked_callers':len(support),'new_ROM_bytes':0}))
