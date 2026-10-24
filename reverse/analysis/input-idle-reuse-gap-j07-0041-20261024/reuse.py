"""J07 existing text/JSON evidence only. Does not read ROM or run a target."""
from pathlib import Path
import json

OUT=Path(__file__).resolve().parent
TREE=OUT.parents[2]
MAIN=Path('D:/Documents/PlatformIO/Projects/cuktech-ap01-firmware')
R=MAIN/'reverse/rehost'
checks=[]

def check(label,condition):
    assert condition,label
    checks.append(label)

def load(p):
    return json.loads(p.read_text(encoding='utf8'))

screen=load(TREE/'reverse/analysis/screen-host-append-20261020.json')
tick=screen['functions'][4]
check('retained tick function identity',tick['procedure']=='0xa00af262')
asm=tick['assembly']
expected={
    '0xa00af280':'c.lw s1, 0xc, a0',
    '0xa00af78a':'lui s2, 0x62fc4',
    '0xa00af79a':'addi s2, s2, 0x2c',
    '0xa00afa78':'lbu a5, 0xe, s2',
    '0xa00afa7c':'lui s1, 0x62fcc',
    '0xa00afa80':'addi s1, s1, -0x33c',
    '0xa00afa8c':'c.beqz a5, 0xa00afb42',
    '0xa00afaa8':'sw zero, 0x0, s1',
    '0xa00afab0':'lbu a5, 0xe, s2',
    '0xa00afab4':'lui s1, 0x62fcc',
    '0xa00afab8':'addi s1, s1, -0x338',
    '0xa00afabc':'beq a5, zero, 0xa00afbec',
    '0xa00afac0':'sw zero, 0x0, s1',
    '0xa00afac4':'sb zero, 0xe, s2',
    '0xa00afac8':'j 0xa00af2a8',
}
for pc,text in expected.items():
    check('old tick anchor '+pc,pc+': '+text in asm)

main=load(R/'main-knob-0041-round2.json')['records'][1]
ma=main['normalized_result']['assembly']
for pc,text in {
    '0xa00afd52':'lui s6, 0x62fc4',
    '0xa00afd56':'addi s11, s6, 0x2c',
    '0xa00afd5a':'c.li a5, 0x1',
    '0xa00afd5c':'sb a5, 0xe, s11',
    '0xa00afd60':'jal ra, 0xa00a769a',
}.items(): check('old main producer '+pc,pc+': '+text in ma)

guide=load(R/'guide-complete-0041.json')
check('parent already explains wake consumption','consumeinput' in str(guide['hooks']['saver']))
check('parent already explains idle thresholds','a00afbec' in guide['saver']['idle'] and 'a00afb42' in guide['saver']['idle'])
check('parent has raw idle-consume fragment','a00afac4:' in guide['bounded_local_disassembly']['saver_idle_gates_asm'])
system=load(R/'system-complete-0041.json')
check('system caches same main producer','62fc403a' in system['cached_evidence']['main_a00afc88'])
final=(TREE/'reverse/reports/ap01/application-rehost-complete-0041-20261017.md').read_text(encoding='utf8')
check('final already covers wake and longpress','首个唤醒事件消费' in final and '3秒长按返回' in final)
e05=(TREE/'reverse/reports/ap01/ctk-app-close-e05-0041-20261023.md').read_text(encoding='utf8')
e06=(TREE/'reverse/reports/ap01/ctk-app-close-review-e06-0041-20261023.md').read_text(encoding='utf8')
check('timer registration already independently accepted','a008bc64(a00af262,1000,app)' in e05 and 'a00af262, 1000 ms, borrowed app' in e06)
pass3=(TREE/'reverse/analysis/0041-20261013/0041-ghidra-pass3.txt').read_text(encoding='utf8').splitlines()
line=next(i+1 for i,s in enumerate(pass3) if 'a008bc64(&LAB_ram_a00af262,1000,iVar6)' in s)
check('pass3 already retains real timer registration',line==2831)

idx=load(TREE/'reverse/analysis/whole-rom-coverage-0041-20261023-round1.json')
j,f=next((i,f) for i,f in enumerate(idx['functions']) if f['address']=='0xa00af262')
check('whole-ROM exact entry matches owner',any(int(x['start'],16)<=0xa00afab0<=int(x['end'],16) for x in f['extent']['body']['ranges']))

later=['display-event-flow-g05-0041-20261023.md','display-event-review-g06-0041-20261023.md',
       'saver-time2-lifetime-i03-0041-20261024.md','saver-time2-lifetime-review-i04-0041-20261024.md']
hits=[]
for name in later:
    text=(TREE/'reverse/reports/ap01'/name).read_text(encoding='utf8').lower()
    hits.append(dict(file=name,exact_hits=[t for t in ['a00afa78','a00afab0','62fcbcc4','62fcbcc8'] if t in text]))

candidate=dict(id='idle-activity-consumption',scope='independent sparse field/ordering review only; new functionality0',
    producer=dict(file='main-knob-0041-round2.json',pointer='/records/1/normalized_result/assembly',
        evidence_id=main['evidence_id'],call='a00afd60 -> a00a769a',store='a00afd5c:62fc403a=1'),
    consumer=dict(file='reverse/analysis/screen-host-append-20261020.json',pointer='/functions/4',
        evidence_id=tick['evidence_id'],entry='a00af262',anchors=list(expected),
        fields=['global base62fc402c','activity62fc403a','screen-close counter62fcbcc4','saver counter62fcbcc8']),
    parent=dict(file='guide-complete-0041.json',pointers=['/saver/idle','/hooks/saver',
        '/bounded_local_disassembly/saver_idle_gates_asm','/bounded_local_disassembly/saver_idle_branch_asm']),
    inventory=dict(pointer=f'/functions/{j}',extent_evidence_id=f['extent']['evidence_id']),
    already_accepted=['timer1000ms/app userdata E05/E06','thresholds/wake semantics guide complete',
        'longpress finalSIM','same old main producer in system parent'],
    unclosed='necessary raw width/base/branch and double-counter-clear then activity-clear ordering has no targeted independent acceptance in checked reports',
    exclude=['all thresholds/menu','whole periodic callback','callback OTA/security branches','all input writers/GPIO','timer lifecycle/registration','L/K/D accepted batches'])
out=dict(status='PASS',baseline='a462ff5',new_functions=0,new_ROM_reads=0,new_decompilation=0,
    checks=checks,pass3_registration_line=line,candidate=candidate,later_targeted_overlap=hits,
    correction='s2 in idle tail is global62fc402c, not app userdata; E05/E06 already accept app timer registration',
    limits=['Old text query does not independently verify ROM or execution','No absence claim for whole history',
        'Candidate is precision review of old behavior, not first recovery','No source/resource/body export or external service'])
(OUT/'reuse-result.json').write_text(json.dumps(out,ensure_ascii=False,indent=2)+'\n',encoding='utf8')
print(json.dumps(dict(status='PASS',checks=len(checks),candidates=1,new_functions=0,new_ROM_reads=0)))
