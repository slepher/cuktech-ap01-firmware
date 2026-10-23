"""Fixed selected-source reader; never imports or runs candidate code."""
import json
from pathlib import Path
import subprocess

HERE=Path(__file__).resolve().parent
REMOTE=r'''
import json
from pathlib import Path
root=Path('/home/slepher/nuttx-ap01-sim/apps/graphics/lvgl/lvgl')
spans={'src/core/lv_obj_pos.c':[(777,811),(1151,1183)],'src/core/lv_obj_pos.h':[(26,38)],
       'src/misc/lv_style.h':[(47,48),(305,309)],
       'src/misc/lv_area.h':[(31,47),(206,234)],
       'src/misc/lv_area.c':[(441,441),(449,510),(512,520)],
       'src/core/lv_obj_style.h':[(290,300)],
       'src/core/lv_obj_style_gen.h':[(106,134)],
       'src/misc/lv_style.c':[(357,361)],'src/core/lv_obj_draw.h':[(30,36)],
       'src/misc/lv_math.h':[(23,23),(159,165)],'src/misc/lv_types.h':[(78,82)]}
excerpts=[]
for rel,ranges in spans.items():
    selected=[]
    with (root/rel).open() as stream:
        for number,text in enumerate(stream,1):
            if any(a<=number<=b for a,b in ranges):
                selected.append({'line':number,'text':text.rstrip('\n')})
            if number==max(b for a,b in ranges):break
    excerpts.append({'path':str(root/rel),'ranges':ranges,'lines':selected})
print(json.dumps({'root':str(root),'excerpts':excerpts},ensure_ascii=False))
'''
result=subprocess.run(['wsl.exe','-d','Ubuntu-24.04','--','python3','-c',REMOTE],capture_output=True,check=True)
evidence=json.loads(result.stdout.decode('utf-8'))
(HERE/'candidate-excerpts.json').write_text(json.dumps(evidence,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
print('PASS: selected local source files',len(evidence['excerpts']),'; selected lines',sum(len(item['lines']) for item in evidence['excerpts']))
