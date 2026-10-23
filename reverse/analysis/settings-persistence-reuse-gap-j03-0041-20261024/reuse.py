"""J03 evidence lookup only. No ROM reads, decompilation, replay, or build."""
from pathlib import Path
import json
import zipfile

HERE=Path(__file__).resolve().parent
TREE=HERE.parents[2]
MAIN=Path('D:/Documents/PlatformIO/Projects/cuktech-ap01-firmware')
R=MAIN/'reverse/rehost'
def read_json(p):return json.loads(p.read_text(encoding='utf8'))
checks=[]
def check(label,value):
    assert value,label
    checks.append(label)
settings=[]
for p in sorted(R.glob('settings-0041-round2*.json')):
    x=read_json(p)
    settings.append(dict(file=p.name,records=len(x['records']),unknowns=x.get('unknowns'),role='Old UI/asset evidence; empty unknown list is not full storage ABI proof'))
source=read_json(R/'settings-0041-round2b.json')['records'][10]
nr=source['normalized_result']
expected={'0xa00fe9f2':'0xa00ab4a8','0xa00fea0a':'0xa00ab4a8','0xa00feac8':'0xa00ab478','0xa00feade':'0xa00ab478'}
refs=[]
for a,t in expected.items():
    hit=next(z for z in nr['outgoing_references'] if z.get('source_address')==a and z.get('target_address')==t)
    check('old caller '+a+' -> '+t,hit is not None)
    refs.append(dict(call=a,target=t,source='settings-0041-round2b.json#/records/10',evidence_id=source['evidence_id']))
parent=read_json(R/'system-complete-0041.json')['cached_evidence']['settings_a00fd1ac']
for t in ['a00ab478','a00ab4a8']:check('parent cached settings still contains '+t,t in parent)
constructor=read_json(R/'settings-0041-round2d.json')['records'][3]
for token in ['DAT_ram_62fc909b','DAT_ram_62fc909a',"uVar4 = 0x1b","uVar4 = 0x1c"]:check('old constructor '+token,token in constructor['normalized_result']['pseudocode'])
inventory=read_json(TREE/'reverse/analysis/whole-rom-coverage-0041-20261023-round1.json')
targets=['0xa00ab478','0xa00ab4a8']
seeds=[]
for t in targets:
    f=next(f for f in inventory['functions'] if f['address']==t)
    seeds.append({k:f.get(k) for k in ['address','extent','direct_calls','historical_dossier','historical_contracts']})
matrix=read_json(TREE/'reverse/reports/ap01/application-function-matrix-0041.json')
services=[{k:s[k] for k in ['id','name','status','implementation']} for s in matrix['service_contracts'] if s['name'] in ['ap01_sim_save','ap01_sim_apply_settings']]
check('two SIM save services passed',len(services)==2 and all(s['status']=='passed-in-sim' for s in services))
check('parent global acceptance only SIM',matrix['global_acceptance']['status']=='passed-in-sim')
zip_checks=[]
with zipfile.ZipFile(R/'ap01-ui-0041-complete-source.zip') as z:
    members={n:z.read(n).decode('utf8').splitlines() for n in ['tools/ap01/ap01-sim-service-impl.h','tools/ap01/ap01-ui.h']}
    for member,line,token in [('tools/ap01/ap01-sim-service-impl.h',149,'AP01SCF1'),('tools/ap01/ap01-sim-service-impl.h',211,'AP01_SIM_STATE_PATH'),('tools/ap01/ap01-sim-service-impl.h',215,'fsync'),('tools/ap01/ap01-sim-service-impl.h',219,'memcmp(data, check, length)'),('tools/ap01/ap01-sim-service-impl.h',222,'rename(temporary, AP01_SIM_STATE_PATH)'),('tools/ap01/ap01-sim-service-impl.h',290,'previous = g_ap01_sim.settings'),('tools/ap01/ap01-sim-service-impl.h',291,'g_ap01_sim.settings = previous'),('tools/ap01/ap01-ui.h',238,'ap01_sim_apply_settings(candidate)')]:
        check('ZIP '+member+':'+str(line),token in members[member][line-1])
        zip_checks.append(dict(member=member,line=line,contains=token,role='SIM service implementation, not original storage ABI'))
report_hits=[]
for p in sorted((TREE/'reverse/reports/ap01').rglob('*.md')):
    if p.name.startswith(('rolling-','settings-persistence-reuse-gap-j03')):continue
    text=p.read_text(encoding='utf8',errors='replace').lower()
    hits=[t for t in targets if t.removeprefix('0x') in text]
    if hits:report_hits.append(dict(file=p.name,tokens=hits))
out=dict(status='PASS',baseline='09e11d0',new_functions=0,new_ROM_bytes=0,execution=False,checks=checks,settings_batches=settings,old_calls=refs,parent_settings_cache_has_same_targets=True,constructor=dict(source='settings-0041-round2d.json#/records/3',evidence_id=constructor['evidence_id'],role='Old constructor reads 909a/909b for selection; not proof of setter writes'),seeds=seeds,sim_services=services,sim_source_checks=zip_checks,recent_report_exact_hits=report_hits,limits=['Bounded exact-token and parent checks, not proof never analyzed.', 'No all-settings matrix, source copy, ROM extraction or decompiler invoked.', 'D19/D22 animation, I01/I02 boot and I05 wifi-cache updates excluded.'])
(HERE/'reuse-result.json').write_text(json.dumps(out,ensure_ascii=False,indent=2)+'\n',encoding='utf8')
print(json.dumps(dict(status=out['status'],checks=len(checks),settings_batches=len(settings),old_calls=len(refs),SIM_services=len(services),candidate_seeds=len(seeds),new_functions=0,new_ROM_bytes=0)))
