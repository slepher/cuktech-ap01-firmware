"""T01 old-contract reuse; no ROM reads or scheduler/delete exports."""
from pathlib import Path
import json
import subprocess

OUT=Path(__file__).resolve().parent
TREE=OUT.parents[2]
old=json.loads((TREE/'reverse/analysis/display-event-flow-g05-0041-20261023/evidence.json').read_text(encoding='utf8'))
rows={int(r['pc'],16):r for w in old['windows'] for r in w['rows']}
checks=[]
for pc,asm in {0xa00805c4:'c.mv a0, s2',0xa00805c6:'c.jalr a5',
 0xa00805c8:'lbu a5, 0x82(s1)',0xa00805ce:'lw a5, 0x10(s2)',
 0xa00805d4:'lbu a5, 0x14(s2)',0xa00805d8:'c.mv a0, s2',
 0xa00805da:'c.andi a5, 2'}.items():
 assert rows[pc]['asm']==asm
 checks.append(dict(pc=hex(pc),inherited_asm=asm))
assert rows[0xa00805de]['target']=='0xa008ae58'
assert rows[0xa00805f4]['target']=='0xa008bd16'
g06=(TREE/'reverse/reports/ap01/display-event-review-g06-0041-20261023.md').read_text(encoding='utf8')
assert '05c8' in g06 and '05ce' in g06 and 'auto-delete' in g06
i02=(TREE/'reverse/reports/ap01/boot-ready-review-i02-0041-20261024.md').read_text(encoding='utf8')
assert '7546' in i02 and '754c' in i02 and '没有直接free(timer)' in i02
remote=r'''
from pathlib import Path
import json
r=Path('/home/slepher/nuttx-ap01-sim/apps/graphics/lvgl/lvgl')
spans={'src/misc/lv_timer.c':[(175,180),(228,231),(339,350)],'src/misc/lv_timer_private.h':[(35,37)]}
out=[]
for rel,rs in spans.items():
 lines=[]
 with (r/rel).open() as f:
  for n,t in enumerate(f,1):
   if any(a<=n<=b for a,b in rs):lines.append(dict(line=n,text=t.rstrip('\n')))
   if n==max(b for a,b in rs):break
 out.append(dict(path=str(r/rel),lines=lines))
print(json.dumps(out))
'''
p=subprocess.run(['wsl','-d','Ubuntu-24.04','--','python3','-c',remote],text=True,capture_output=True,encoding='utf8')
assert p.returncode==0,p.stderr
sources=json.loads(p.stdout)
assert sum(len(s['lines']) for s in sources)==25
t={x['line']:x['text'] for x in sources[0]['lines']}
assert 'auto_delete = true' in t[180] and 'timer->repeat_count = repeat_count' in t[231]
assert 'state.timer_deleted == false' in t[339] and 'repeat_count == 0' in t[340]
assert 'timer->auto_delete' in t[341] and 'lv_timer_delete(timer)' in t[343] and 'lv_timer_pause(timer)' in t[347]
result=dict(status='PASS',baseline='09e11d0',new_functions=0,new_rom_windows=0,
 inherited_checks=checks,inherited_edges=[dict(pc='0xa00805de',target='0xa008ae58'),dict(pc='0xa00805f4',target='0xa008bd16')],
 candidate_naming_only=sources,
 conclusion='Already covered by G05/G06; I01/I02 timer constructor/repeat setter join existing post-callback gate',
 conditions=['Post-callback global deleted flag must remain zero before current timer repeat/flags reads',
             'repeat==0 and current auto-delete bit1 set choose delete; clear choose pause',
             'Boot constructor initializes auto-delete, but runtime state is not observed'],
 limits=['No original bytes reread or new technical verification of G05/G06',
         'No private boot callback or timer delete helper repeated',
         'Candidate only supports names, no exact version/layout authentication',
         'Userdata freed by boot callback; timer object freed by scheduler delete path'])
(OUT/'reuse-evidence.json').write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n',encoding='utf8')
print(json.dumps(dict(status='PASS',old_anchors=len(checks),old_edges=2,candidate_lines=25,new_functions=0,new_rom_windows=0)))
