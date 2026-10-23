"""T02 independent reuse-join review: no ROM, WSL or candidate execution."""
import json
from pathlib import Path

HERE=Path(__file__).resolve().parent
TREE=HERE.parents[2]
def load(relative):
    return json.loads((TREE/relative).read_text(encoding='utf-8'))
g05=load('reverse/analysis/display-event-flow-g05-0041-20261023/evidence.json')
g06=load('reverse/analysis/display-event-review-g06-0041-20261023/evidence.json')
i02=load('reverse/analysis/boot-ready-review-i02-0041-20261024/review-result.json')
t01=load('reverse/analysis/timer-repeat-release-t01-0041-20261024/reuse-evidence.json')
old={row['pc']:row for window in g05['windows'] for row in window['rows']}
accepted={row['address']:row for window in g06['windows'] for row in window['rows']}
join=[]
expectations={
 '0xa00805c4':'c.mv a0, s2','0xa00805c6':'c.jalr a5',
 '0xa00805c8':'lbu a5, 0x82(s1)','0xa00805ce':'lw a5, 0x10(s2)',
 '0xa00805d4':'lbu a5, 0x14(s2)','0xa00805d8':'c.mv a0, s2',
 '0xa00805da':'c.andi a5, 2'}
reported={row['pc']:row['inherited_asm'] for row in t01['inherited_checks']}
assert reported==expectations
for pc,asm in expectations.items():
    assert old[pc]['asm']==accepted[pc]['instruction']==asm
    assert old[pc]['raw']==accepted[pc]['bytes']
    join.append({'pc':pc,'T01_G05_G06_same':True})

edges=[]
for pc,target in [('0xa00805cc','0xa00805e2'),('0xa00805d2','0xa00805e2'),
                  ('0xa00805dc','0xa00805f4'),('0xa00805de','0xa008ae58'),
                  ('0xa00805f4','0xa008bd16')]:
    assert old[pc]['raw']==accepted[pc]['bytes']
    assert accepted[pc]['target']==target
    if old[pc]['target'] is not None:
        assert old[pc]['target']==target
    edges.append({'pc':pc,'accepted_target':target})
assert t01['inherited_edges']==[{'pc':'0xa00805de','target':'0xa008ae58'},
                                {'pc':'0xa00805f4','target':'0xa008bd16'}]

assert i02['status']=='PASS'
checks={item['check']:item for item in i02['checks']}
for label,want in [('JAL 0xa005ce98',[111,1,0xa008bc64]),
                   ('JAL 0xa00a7546',[111,1,0xa008c280]),
                   ('JAL 0xa00a754c',[111,1,0xa008ab8a]),
                   ('load width/regs 0xa00a7488',[3,19,2,10,12])]:
    assert checks[label]['actual']==checks[label]['expected']==want

reports={name:(TREE/'reverse/reports/ap01'/name).read_text(encoding='utf-8') for name in [
 'timer-repeat-release-t01-0041-20261024.md','display-event-review-g06-0041-20261023.md',
 'display-event-flow-g05-0041-20261023.md','boot-ready-review-i02-0041-20261024.md']}
text=reports['timer-repeat-release-t01-0041-20261024.md']
for token in ['没有运行时证据证明任何实际实例在此刻必保持默认位','先检查全局删除标志',
              'P已在callback内归还','timer节点随后由scheduler归还','bit1为0时调用',
              '没有读ROM','只支持命名及分支意图相容']:
    assert token in text,token
assert 'now()返回 → 取 callback 快照 → 写 last_tick' in reports['display-event-review-g06-0041-20261023.md']
assert '没有直接free(timer)' in reports['boot-ready-review-i02-0041-20261024.md']
assert 'list header=`62fc95f0`' in reports['display-event-flow-g05-0041-20261023.md']
assert t01['new_functions']==0 and t01['new_rom_windows']==0
result={'task':'T02','result':'PASS','kind':'independent existing-contract join review',
        'three_way_anchor_checks':join,'G06_accepted_control_edges':edges,
        'I02_accepted_identity_checks':['boot create uses a008bc64','callback loads P from timer+c',
                                       'repeat setter receives timer before free(P)'],
        'decision':'Accept T01 with its runtime conditions; no semantic correction or new functionality.',
        'limits':['No ROM read, disassembly, WSL/candidate read, model/target execution or old verifier execution.',
                  'G05/G06 scheduler and timer deletion remain inherited independent technical contracts.',
                  'Constructor bit1 default is not an all-time or actual-run guarantee.',
                  'Userdata P and timer are distinct allocation roots with different release owners.']}
(HERE/'review-result.json').write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
print('PASS: 7 three-way anchors, 5 accepted control edges, 4 I02 identity checks; T01 runtime limits retained.')
