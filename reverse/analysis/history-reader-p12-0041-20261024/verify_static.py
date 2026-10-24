"""P-12: read-only original-byte checks; no target execution or REA session."""
import sys
sys.dont_write_bytecode = True
import importlib.util
import json
from pathlib import Path
from datetime import datetime, timezone

ROOT = Path('D:/Documents/PlatformIO/Projects/cuktech-ap01-firmware')
HERE = Path(__file__).resolve().parent
s = importlib.util.spec_from_file_location('e05', ROOT/'reverse/analysis/ctk-app-close-e05-0041-20261023/decode.py')
d = importlib.util.module_from_spec(s)
s.loader.exec_module(d)
original = d.custom

def custom(word):
    # Local rendering of two existing private-model families. Never edits model.
    f3, high = (word >> 12) & 7, word >> 27
    names = [d.regs[(word >> k) & 31] for k in (7, 15, 20)]
    if word & 127 == 11 and f3 == 4 and high == 20:
        return 'th.lrhu ' + ','.join(names) + ',' + str((word >> 25) & 3)
    if word & 127 == 11 and f3 == 4 and high == 11:
        return 'th.lwia ' + ','.join(names[:2]) + ',' + str(d.signed((word >> 20) & 31, 5)) + ',' + str((word >> 25) & 3)
    return original(word)

d.custom = custom
spans = [
    ('callback_item_identity',0xa00f52b4,0xa00f52b8),
    ('selected_page_lookup',0xa00f53ba,0xa00f53f4),
    ('selected_port_gate',0xa00f56ba,0xa00f56e4),
    ('history_gate_and_cursor',0xa00f5702,0xa00f574c),
    ('first_or_wrapped_tail',0xa00f574c,0xa00f5786),
    ('forward_wrap_zero',0xa00f5a04,0xa00f5a7e),
    ('chart_glue',0xa00a64e4,0xa00a6548),
]
windows = []
for name, a, b in spans:
    rows = d.decode(a,b)
    assert int(rows[-1]['address'],16)+len(bytes.fromhex(rows[-1]['hex'])) == b
    windows.append(dict(name=name,start=hex(a),end_exclusive=hex(b),instructions=rows))
idx = {int(r['address'],16):r for w in windows for r in w['instructions']}
checks = []
def check(label, result):
    assert result, label
    checks.append(label)
for pc, raw in [(0xa00f52b6,'ae84'),(0xa00f575c,'8b97f402'),(0xa00f5a10,'8b97f402'),(0xa00f5a44,'0bc55ca3'),(0xa00a650c,'0bc5a65a')]:
    check(hex(pc)+' bytes',idx[pc]['hex']==raw)
check('scaled address is item + slot*2', idx[0xa00f575c]['assembly']=='th.addsl a5,s1,a5,1')
check('wrapped load is unsigned halfword',idx[0xa00f5a44]['assembly']=='th.lrhu a0,s9,s5,1')
check('chart postincrement is local output point',idx[0xa00a650c]['assembly']=='th.lwia a0,a3,10,1')
for pc,target in [(0xa00f576a,0xa00a64e4),(0xa00f5a1e,0xa00a64e4),(0xa00f5a4e,0xa00a64e4),(0xa00a6516,0xa00925e0),(0xa00a6526,0xa0093a7c),(0xa00a6502,0xa019c5d0),(0xa00a6538,0xa00dbb68)]:
    check(hex(pc)+' target',idx[pc]['target']==hex(target))
parent = json.loads((ROOT/'reverse/rehost/charge-complete-0041.json').read_text(encoding='utf8'))
old = {int(line.split(':')[0],16):line for line in parent['records'][19]['assembly']}
for w in windows[:-1]:
    for r in w['instructions']:
        check(r['address']+' retained boundary',int(r['address'],16) in old)
g = json.loads((ROOT/'evidence/rea-0041-20261017/evidence/whole-rom-graph-20261023-4942.json').read_text())['structuredContent']
check('glue retained body',g['normalized_result']['body']['ranges']==[{'start':'0xa00a64e4','end':'0xa00a6547'}])
out = dict(observed_at_utc=datetime.now(timezone.utc).isoformat(),rom=str(d.ROM),mapping_base=hex(d.BASE),
           old_callback=dict(path=str(ROOT/'reverse/rehost/charge-complete-0041.json'),pointer='/records/19',evidence_id=parent['records'][19]['evidence_id'],profile='Original carrier omits analysis_profile; do not assign later thead2 profile. Generic RISCV limitations explicitly retained.'),
           glue_boundary=dict(path=str(ROOT/'evidence/rea-0041-20261017/evidence/whole-rom-graph-20261023-4942.json'),evidence_id=g['evidence_id'],analysis_profile_digest=g['analysis_profile']['digest'],language=g['analysis_profile']['parameters']['language_id']),
           decoder=dict(source=str(ROOT/'reverse/analysis/ctk-app-close-e05-0041-20261023/decode.py'),capstone_version=list(d.cs.version()) if hasattr(d.cs,'version') else 'installed Capstone Python binding',vendor_semantics=str(ROOT/'evidence/rea-0041-20261017/processor/data/languages/ap01thead2.sinc'),local_extensions=['th.lrhu','th.lwia'],limits='Offline static rendering against existing private model, not execution or independent upstream ISA authentication.'),windows=windows,checks=checks)
(HERE/'static-evidence.json').write_text(json.dumps(out,ensure_ascii=False,indent=2)+'\n',encoding='utf8')
print(len(checks),'checks PASS;',sum(len(w['instructions']) for w in windows),'instructions;',sum(int(w['end_exclusive'],16)-int(w['start'],16) for w in windows),'bytes')
