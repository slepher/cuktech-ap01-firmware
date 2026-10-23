"""Read selected local candidate lines only; no import/build/target execution."""
import json
from pathlib import Path
import subprocess

HERE = Path(__file__).resolve().parent
REMOTE = r'''
import json
from pathlib import Path
p=Path('/home/slepher/nuttx-ap01-sim/apps/graphics/lvgl/lvgl/src/misc/cache/lv_cache_lru_rb.c')
selected=[]
with p.open() as stream:
    for number,text in enumerate(stream,1):
        if 343 <= number <= 406:
            selected.append({'line':number,'text':text.rstrip('\n')})
        if number == 406:
            break
assert len(selected)==64
root=p.parents[3]
neighbors=[]
for rel,starts in [('src/misc/lv_rb.c',[257]),('src/misc/lv_ll.c',[160,294])]:
    neighbor=root/rel
    snippets=[]
    current=None
    depth=0
    opened=False
    with neighbor.open() as stream:
        for number,text in enumerate(stream,1):
            if number in starts:
                current={'start':number,'lines':[]}
                depth=0
                opened=False
            if current is not None:
                current['lines'].append({'line':number,'text':text.rstrip('\n')})
                depth += text.count('{')-text.count('}')
                opened = opened or '{' in text
                if opened and depth==0:
                    current['end']=number
                    snippets.append(current)
                    current=None
                    if number > max(starts):
                        break
    assert len(snippets)==len(starts),(rel,snippets)
    neighbors.append({'path':str(neighbor),'snippets':snippets})
print(json.dumps({'path':str(p),'range':[343,406],'lines':selected,'neighbors':neighbors},ensure_ascii=False))
'''
process = subprocess.run(['wsl.exe','-d','Ubuntu-24.04','--','python3','-c',REMOTE],capture_output=True,check=True)
evidence = json.loads(process.stdout.decode('utf-8'))
(HERE/'candidate-excerpts.json').write_text(json.dumps(evidence,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
for item in evidence['lines']:
    print(f"{item['line']}: {item['text']}")
for item in evidence['neighbors']:
    print(item['path'])
    for snippet in item['snippets']:
        for line in snippet['lines']:
            print(f"{line['line']}: {line['text']}")
