"""J06 existing-evidence inventory only: no ROM reads, decoding or execution."""
import json
from pathlib import Path

HERE = Path(__file__).resolve().parent
MAIN = Path('D:/Documents/PlatformIO/Projects/cuktech-ap01-firmware')
reports = MAIN/'reverse/reports/ap01'
old = MAIN/'evidence/rea-0041-20261017/evidence'
bundle_path = old/'upper-complete.evidence.json'
records = json.loads(bundle_path.read_text(encoding='utf-8'))['records']
selected = []
selectors = [(197,'0xa0111ff6'),(91,'0xa011f9da'),(13,'0xa011f86c'),
             (163,'0xa005f222'),(278,'0xa01b38dc'),(18,'0xa01977cc'),
             (282,'0xa01b6146')]
for idx, address in selectors:
    rec = records[idx]
    proc = rec['normalized_result']['procedure']
    assert proc['address'] == address
    selected.append({'carrier':str(bundle_path),'json_pointer':f'/records/{idx}/normalized_result',
                     'address':address,'evidence_id':rec['evidence_id'],'body':proc['body'],
                     'evidence_level':'existing retained provider body/assembly; not newly verified against ROM'})
by_address = {r['normalized_result']['procedure']['address']:r for r in records if r.get('normalized_result',{}).get('procedure')}
anchors = {
    '0xa01b6146':['0xa01b632a: jal ra, 0xa0111ff6'],
    '0xa0111ff6':['0xa0112062: jal ra, 0xa011f9da'],
    '0xa011f9da':['0xa011fa1a: jal ra, 0xa011f86c'],
    '0xa011f86c':['0xa011f964: jal ra, 0xa011f610','0xa011f992: jal ra, 0xa011f66c'],
    '0xa005f222':['0xa005f22a: c.lw a1, 0x1c, a0','0xa005f22c: c.lw a0, 0x20, a0'],
    '0xa01b38dc':['0xa01b3aea: lw a0, -0x84, s0','0xa01b3aee: c.mv a2, s1',
                    '0xa01b3af0: c.mv a1, s3','0xa01b3af2: jal ra, 0xa01977cc']}
for address, lines in anchors.items():
    asm = by_address[address]['normalized_result']['assembly']
    assert all(line in asm for line in lines), address
rpc_path = MAIN/'reverse/rehost/miio-rpc-rea-0041.json'
rpc = json.loads(rpc_path.read_text(encoding='utf-8'))['native_rpc']
assert 'message/length remain ina1/a2' in rpc['reply_matching']['behavior']
assert rpc['upward_rpc']['pending_node']['head'] == '0x62fca4c8'
assert rpc['report_callback']['procedure'] == '0xa00626ea'
assert 'not timeout policy' in rpc['reply_matching']['behavior']
cards = (old/'upper-miio-b.md').read_text(encoding='utf-8')
assert '0xa0111ff6 copy-versus-retain semantics not closed' in cards
assert 'Cannot claim request buffer retention safe without 0xa0111ff6' in cards
f06 = (reports/'display-exit-review-f06-0041-20261023.md').read_text(encoding='utf-8')
assert '0xffff7fff' in f06 and '并非 F05 所写“低15位”' in f06
complete = (reports/'application-rehost-complete-0041-20261017.md').read_text(encoding='utf-8')
assert '所有模拟成功都只表示SIM服务结果' in complete
queries = []
terms = ['a0111ff6','a005f222','a01b38dc','a00626ea','62fca4c8']
for name in ['system-complete-0041.json','guide-complete-0041.json','page-logic-0041.json']:
    p = MAIN/'reverse/rehost'/name
    text = p.read_text(encoding='utf-8').lower()
    queries.append({'carrier':str(p),'query_terms':terms,'matches':[t for t in terms if t in text]})
result = {
    'baseline':'a462ff5','inventory_only':True,'rom_reads':0,'new_function_exports':0,'new_functionality':0,
    'inherited_contracts':[
        {'carrier':str(rpc_path),'json_pointer':'/native_rpc/reply_matching','scope':'id match, unlink, callback(fd,message,length), node free; already explained'},
        {'carrier':str(rpc_path),'json_pointer':'/native_rpc/send_failure_helper','scope':'a0062afa common failure-to-correlation helper, not a proven timeout policy'},
        {'carrier':str(reports/'display-exit-review-f06-0041-20261023.md'),'scope':'preserve filter & ffff7fff correction, display/DELETE separate from MiIO close'}],
    'candidate':{'question':'normal stack descriptor to owned/borrowed publish request, message copy/hold and callback lifetime',
                 'seed_caller':'0xa01b6146 @0xa01b62fc..0xa01b632a',
                 'first_callee':'0xa0111ff6','minimal_existing_dependency_chain':['0xa011f9da','0xa011f86c'],
                 'queue_edges_to_resolve_only_if_needed':['0xa011f610','0xa011f66c'],
                 'callback':'0xa005f222 -> 0xa01b38dc',
                 'not_yet_proven':['copy versus retain contract and exact field shift through descriptor adapters',
                                   'queued request identity at callback and response message borrowing/free order'],
                 'limits':'normal construction/queue/callback only; no complete parser, transport, cipher, credentials, timeout or external execution'},
    'retained_selectors':selected,'necessary_existing_anchors':anchors,'bounded_parent_queries':queries,
    'rejected_or_inherited_candidates':[
        'F01/F02 kinds0..6 and normal request cleanup already covered; no new producer/walker seed from this pass',
        'F03/F04 type13 conditional close covered; actual9428 close/pending opportunity still unknown without new caller',
        'F05/F06 optional display+2b8 known initialNULL; no new nonNULL install seed; do not repeat whole-ROM SW search',
        'reply_matching a1/a2 is already explicit in prior native_rpc contract; not a new ABI discovery',
        'a0062afa noack helper is known send-failure correlation, not new expiration trigger'],
    'limits':['Existing metadata/assembly and pseudocode inspected only; no new technical semantic certification.',
              'Exact-term absence in bounded reports/parent files is not historical absence.',
              'No SIM/build/replay/firmware/model/device/network/service activity; no production/ROM/config/model changes.']}
(HERE/'reuse-result.json').write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
print(json.dumps({'passed':True,'retained_selectors':len(selected),'existing_anchors':sum(map(len,anchors.values())),
                  'rom_reads':0,'new_functionality':0}))
