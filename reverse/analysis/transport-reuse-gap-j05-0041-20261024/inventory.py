"""Existing-text/JSON inventory only. Does not open a ROM or analysis session."""
import json
from pathlib import Path

ROOT=Path('D:/Documents/PlatformIO/Projects/cuktech-ap01-firmware')
terms=['a009f442','a009e212','a009f972','uv__io_stop','uv__platform_invalidate_fd']
parents=[]
for name in ['system-complete-0041.json','charge-complete-0041.json','guide-complete-0041.json','weather-calendar-complete-0041.json']:
    p=ROOT/'reverse/rehost'/name
    text=p.read_text(encoding='utf-8').lower()
    parents.append(dict(path=str(p),exact_token_counts={term:text.count(term) for term in terms}))

g07=ROOT/'reverse/analysis/display-alternate-work-g07-0041-20261023/evidence.json'
d=json.loads(g07.read_text(encoding='utf-8'))
window=d['windows'][5]
assert window['name']=='poll_stop' and window['start']=='0xa009f972'
rows=window['rows']
assert rows[6]['pc']=='0xa009f97e' and '0x34' in rows[6]['asm']
assert rows[8]['pc']=='0xa009f984' and '0x17' in rows[8]['asm']
assert rows[9]['pc']=='0xa009f986' and rows[9]['target']=='0xa009f442'
assert rows[21]['pc']=='0xa009f9a4' and '0x58' in rows[21]['asm']
assert rows[23]['pc']=='0xa009f9a8' and rows[23]['target']=='0xa009e212'
seeds=[dict(path=str(g07),pointer=f'#/windows/5/rows/{i}',address=rows[i]['pc'],role=role) for i,role in [(6,'same poll watcher offset34'),(8,'cancel mask17'),(9,'cancel call'),(21,'same poll fd word58'),(23,'fd backend synchronizer call')]]

index=ROOT/'reverse/analysis/whole-rom-coverage-0041-20261023-round1.json'
inventory=json.loads(index.read_text(encoding='utf-8'))
targets=[]
for i,address in [(2358,'0xa009e212'),(2374,'0xa009f442'),(2377,'0xa009f972')]:
    f=inventory['functions'][i]
    assert f['address']==address
    targets.append(dict(path=str(index),pointer=f'#/functions/{i}',address=address,extent_evidence=f['extent']['evidence_id'],range=f['extent']['body']['ranges'],bytes=f['extent']['body']['total_bytes'],calls_evidence=f['direct_calls']['evidence_id'],callees=f['direct_calls']['callees'],status='extent/direct-call metadata only; not a recovered body contract'))

page=ROOT/'reverse/rehost/page-logic-0041.json'
pd=json.loads(page.read_text(encoding='utf-8'))
r=pd['records'][15]
assert r['parameters']['procedure']=='0xa0024906'
assert r['normalized_result']['callers'][195]['address']=='0xa009e212'
page_match=dict(path=str(page),pointer='#/records/15/normalized_result/callers/195',evidence_id=r['evidence_id'],meaning='a009e212 is caller metadata for a0024906, not an e212 body/behavior recovery')

reports=ROOT/'reverse/reports/ap01'
semantic_proofs={
 'pogo-close-dispatch-review-c06-0041-20261023.md':['ffbe','a009f972'],
 'display-alternate-work-g07-0041-20261023.md':['a009f442','a009e212','内部backend取消'],
 'display-ready-review-g10-0041-20261024.md':['watcher+14','loop+34'],
 'uart-dma-channel-review-d10-0041-20261023.md':['channel读共4次','0x0f'],
 'dock-presence-polling-0041-20261023.md':['相位匹配但 sent>=limit','不重写 sent'],
}
for name,needles in semantic_proofs.items():
    text=(reports/name).read_text(encoding='utf-8')
    for needle in needles: assert needle in text,(name,needle)

result=dict(status='PASS-existing-evidence-inventory-only',baseline='a462ff5',parent_queries=parents,seeds=seeds,target_metadata=targets,page_logic_match=page_match,candidate='Pogo type8 close: existing stop -> watcher cancel and same-fd backend synchronization',new_rom_functionality=0,limitations=['No new ROM reads/decompilation/runtime/network/model operations','Exact token negatives limited to named files; inherited G09/J04 final ZIP/SIM boundary retained','No claim that close drains pending, stops the Pogo timer, closes the OS fd or releases owner context','Not a technical acceptance of f442/e212 bodies'])
Path(__file__).with_name('reuse.json').write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
print('PASS: existing stop rows, 3 inventory targets, 4 parent text queries, bounded caller-metadata match')
