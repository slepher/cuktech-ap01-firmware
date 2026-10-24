"""P-19 bounded offline ROM checks. Does not execute target code or an ISA model."""
import sys
sys.dont_write_bytecode = True
import importlib.util
import json
from pathlib import Path
from datetime import datetime, timezone

ROOT = Path('D:/Documents/PlatformIO/Projects/cuktech-ap01-firmware')
HERE = Path(__file__).resolve().parent
spec = importlib.util.spec_from_file_location('e05', ROOT/'reverse/analysis/ctk-app-close-e05-0041-20261023/decode.py')
d = importlib.util.module_from_spec(spec)
spec.loader.exec_module(d)
original = d.custom
def render(word):
    try:
        return original(word)
    except AssertionError:
        # Preserve unresolved instructions instead of inventing semantics.
        return 'opaque_custom ' + hex(word)
d.custom = render
spans = [
    ('allocator_zero_contract', 0xa008e362, 0xa008e38c),
    ('zero_adapter', 0xa0080d8e, 0xa0080da6),
    ('creator_allocation_failure', 0xa01afda6, 0xa01afe2a),
    ('chart_series_setup', 0xa01b01c4, 0xa01b021c),
    ('marker_cache_timer', 0xa01b021c, 0xa01b0280),
    ('page_install', 0xa01b0612, 0xa01b0638),
    ('timer_pause_nonnull', 0xa008bd62, 0xa008bd70),
    ('port1_snapshot_context', 0xa00f6e44, 0xa00f6e7c),
    ('port1_creator_call', 0xa00f6eb8, 0xa00f6ed4),
    ('port2_creator_call', 0xa00f6f78, 0xa00f6f7c),
    ('port3_creator_call', 0xa00f7024, 0xa00f7028),
    ('port4_creator_call', 0xa00f70d0, 0xa00f70d4),
    ('return_enumeration_identity', 0xa00f7112, 0xa00f7194),
    ('normal_return_to_list', 0xa00f719e, 0xa00f71b6),
    ('page_delete_callback', 0xa00f1b8e, 0xa00f1c28),
]
windows = [dict(name=n,start=hex(a),end_exclusive=hex(b),instructions=d.decode(a,b)) for n,a,b in spans]
idx = {int(r['address'],16):r for w in windows for r in w['instructions']}
checks=[]
def check(label, condition):
    assert condition, label
    checks.append(label)
for w in windows:
    rows=w['instructions']
    check(w['name']+' exact end',int(rows[-1]['address'],16)+len(bytes.fromhex(rows[-1]['hex']))==int(w['end_exclusive'],16))
for pc,target in [(0xa008e370,0xa002fcc8),(0xa008e37c,0xa0080d8e),(0xa0080d9a,0xa0024906),(0xa00f6e4a,0xa00f3b36),(0xa00f6ecc,0xa01afd56),(0xa00f6f78,0xa01afd56),(0xa00f7024,0xa01afd56),(0xa00f70d0,0xa01afd56),(0xa00f71ae,0xa00ded6c),(0xa00f1bea,0xa008ae58),(0xa00f1c10,0xa008ab8a)]:
    check(hex(pc)+' target',idx[pc]['target']==hex(target))
for pc,raw in [(0xa01afde0,'1305c006'),(0xa01afdec,'aa84'),(0xa01b020c,'a8c0'),(0xa01b0266,'23a60404'),(0xa01b0618,'23a29b00'),(0xa008bd66,'93e71700')]:
    check(hex(pc)+' bytes',idx[pc]['hex']==raw)
parent=json.loads((ROOT/'reverse/rehost/charge-complete-0041.json').read_text(encoding='utf8'))
retained={int(r['address'],16):r for r in parent['creator_continuations'][2]['instructions']}
for w in windows:
    if w['name'] in ('chart_series_setup','marker_cache_timer','page_install'):
        for r in w['instructions']:
            old=retained[int(r['address'],16)]
            check(r['address']+' original continuation bytes',old['bytes']==r['hex'])
def pair(pc):
    a=int.from_bytes(bytes.fromhex(idx[pc]['hex']),'little')
    b=int.from_bytes(bytes.fromhex(idx[pc+4]['hex']),'little')
    imm=(b>>20); imm=imm-4096 if imm&2048 else imm
    return (pc+(a&0xfffff000)+imm)&0xffffffff
check('timer create target',pair(0xa01b026e)==0xa008bc64)
check('timer pause target',pair(0xa01b0278)==0xa008bd16)
check('ctor zero allocator target',pair(0xa01afde4)==0xa008e362)
sources=[]
for n in (4872,4873):
    path=ROOT/f'evidence/rea-0041-20261017/evidence/whole-rom-graph-20261023-{n}.json'
    p=json.loads(path.read_text(encoding='utf8'))['structuredContent']
    sources.append(dict(path=str(path),evidence_id=p['evidence_id'],operation=p['operation'],parameters=p['parameters'],analysis_profile_digest=p['analysis_profile']['digest'],provider=p['provider']))
out=dict(observed_at_utc=datetime.now(timezone.utc).isoformat(),rom=str(d.ROM),mapping_base=hex(d.BASE),sources=sources,legacy_creator=dict(path=str(ROOT/'reverse/rehost/charge-0041-round4.json'),pointer='/records/2',evidence_id='ev_e30acc99f01e5e79a06965e472ec0c1aee39a56a7c3e8ae8ad7fdef09673d74e',profile='Carrier omits profile; generic/custom/no-return limitations retained.'),decoder=dict(source=str(ROOT/'reverse/analysis/ctk-app-close-e05-0041-20261023/decode.py'),mode='Capstone RV32+C plus inherited local rendering; unresolved custom kept opaque; no model changes'),windows=windows,checks=checks)
(HERE/'static-evidence.json').write_text(json.dumps(out,ensure_ascii=False,indent=2)+'\n',encoding='utf8')
print(len(checks),'PASS;',sum(len(w['instructions']) for w in windows),'instructions;',sum(int(w['end_exclusive'],16)-int(w['start'],16) for w in windows),'bytes')
