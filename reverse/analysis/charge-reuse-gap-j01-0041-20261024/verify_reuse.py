"""Existing-evidence triage only. Never reads ROM or runs old verifiers."""
import json
from pathlib import Path

HERE=Path(__file__).resolve().parent
TREE=HERE.parents[2]
MAIN=Path('D:/Documents/PlatformIO/Projects/cuktech-ap01-firmware')
REHOST=MAIN/'reverse/rehost'

def read_json(path):
    return json.loads(path.read_text(encoding='utf-8'))

matrix=read_json(TREE/'reverse/reports/ap01/application-function-matrix-0041.json')
reference=read_json(TREE/'reverse/analysis/factory-reference-map-0041.json')
assert 'functions' in reference and 'open_gaps' in reference
charge=read_json(REHOST/'charge-complete-0041.json')
round4=read_json(REHOST/'charge-0041-round4.json')
details=read_json(REHOST/'details-0041-round4.json')
page=read_json(REHOST/'page-logic-0041.json')
sim=read_json(REHOST/'complete-nuttx-sim-verification.json')
live=read_json(REHOST/'complete-live-verification.json')
assert charge['previous_evidence']=='charge-0041-round4.json'
assert 'local' in charge['scope'].lower() and 'replaced' in charge['scope'].lower()
assert 'Date and Weather' in details['scope']
assert page['records']
assert sim['passed'] and live['passed']
assert (sim['step_count'],len(sim['screenshots']),live['step_count'],len(live['screenshots']))==(502,99,30,15)
assert sim['binary_sha256']==live['binary_sha256']==matrix['global_acceptance']['binary_sha256']
features=[item for item in matrix['features'] if item.get('family')=='charge']
assert len(features)==12 and all(item['status']=='passed-in-sim' for item in features)
service_names=[item['name'] for item in matrix['service_contracts'] if any(token in item['name'] for token in ['set_mode','set_port','set_safe','protocol_'])]
assert len(service_names)==6

# Pointer-only references: keep just the three already established old records.
record_refs=[]
for index,address in [(8,'0xa00f4610'),(9,'0xa00f44e8'),(19,'0xa00f5288')]:
    record=charge['records'][index]
    assert record['parameters']['procedure']==address
    record_refs.append({'index':index,'procedure':address,'evidence_id':record['evidence_id']})

report_tokens={
 'ctk-round3-coverage-review-e11-0041-20261024.md':['E09','a00a1aa8','0xe4'],
 'ctk-snapshot-consumer-e12-0041-20261024.md':['E03','E04','新增业务恢复0','互斥'],
 'ctk-offline-transition-e13-0041-20261024.md':['旧非零、新零','a00ef1d4','不再另立研究题'],
 'uiiface-item-ownership-e01-0041-20261023.md':['a00a93a4','a00a9454','a00a9504','类型分类完整决策树不在本轮认证'],
 'uiiface-ownership-review-e02-0041-20261023.md':['完整分类树未核','完整类型分类'],
 'text-update-entry-review-c14-0041-20261023.md':['a0091ee4','限定接受'],
 'text-entry-source-c23-0041-20261024.md':['lv_label_set_text_fmt','完整formatter/allocator仍未认证'],
 'queued-command-review-b21-0041-20261023.md':['同步复制','不保存descriptor或payload指针'],
 'main-app-root-exit-e10-0041-20261024.md':['没有这个种子时不应重复派 root 退出搜索'],
}
for name,tokens in report_tokens.items():
    text=(TREE/'reverse/reports/ap01'/name).read_text(encoding='utf-8')
    for token in tokens:
        assert token in text,(name,token)

retained=read_json(TREE/'reverse/analysis/buzzer-backlight-0041-20261023.json')
function=next(item for item in retained['functions'] if item['address']=='0xa00a8582')
assert function['evidence_id']=='ev_6f9f82e5daf0540a1c24a0b85daa2e394785391692765e5e3e100eb7b37ed94c'
body=function['procedure']['body']
assert body['ranges']==[{'end':'0xa00a9d1d','start':'0xa00a8582'}]
anchors=['0xa00a93a4','0xa00a9454','0xa00a9504']
assert all(any(address in line.lower() for line in function['assembly']) for address in anchors)
result={
 'task':'J01','result':'PASS','kind':'existing evidence index checks; no semantic adjudication',
 'sim_boundary':{'charge_features':12,'status':'passed-in-sim','local_mutations':service_names,
                 'sim_steps':502,'sim_screenshots':99,'live_steps':30,'live_screenshots':15},
 'old_record_references':record_refs,
 'supersession_checks':list(report_tokens),
 'one_candidate_seed':{'procedure':function['address'],'extent':body['ranges'],
    'evidence_id':function['evidence_id'],'source':function['source']['path'],
    'retained_anchor_presence':anchors,
    'question':'Normal cmd51 classification leading to item+0e; reuse existing body before any sparse follow-up.'},
 'limits':['No ROM read, new decompilation, instruction decoding or old verifier execution.',
           'Metadata/anchor presence is not independent proof of function semantics.',
           'No broad search for item+34/+38 consumers or main app exit without a new alias/caller seed.']}
(HERE/'reuse-result.json').write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
print('PASS: complete/matrix/final SIM boundaries, old record references, 9 supersession checks, one retained classifier seed.')
