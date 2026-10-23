"""F08 independent local-file review. No target code is imported or executed."""
import json
from pathlib import Path
import subprocess

HERE = Path(__file__).resolve().parent
REMOTE = r'''
import json, re, zipfile, subprocess
from pathlib import Path
base=Path('/home/slepher/nuttx-ap01-sim/apps/graphics/lvgl/lvgl')
selections={
 'lv_version.h':[(1,16)],
 'src/display/lv_display.c':[(62,90),(158,212),(734,739),(780,797),(912,933)],
 'src/display/lv_display_private.h':[(36,167)],
 'src/misc/lv_ll.c':[(16,18),(57,78)],
 'src/misc/lv_ll.h':[(29,35)],
 'src/misc/lv_event.c':[(63,105)],
 'src/misc/lv_event_private.h':[(23,45)],
 'src/misc/lv_event.h':[(26,120)],
 'src/misc/lv_array.h':[(26,44)],
 'src/misc/lv_types.h':[(48,61)],
 'src/drivers/nuttx/lv_nuttx_entry.c':[(96,110),(134,175)],
 'src/drivers/nuttx/lv_nuttx_fbdev.c':[(34,47),(75,107),(383,405)],
 'src/draw/lv_draw.h':[(70,108)],
}
out={'root':str(base),'archive':str(base.parent/'v9.2.1.zip'),'members':[]}
with zipfile.ZipFile(base.parent/'v9.2.1.zip') as z:
 for rel,ranges in selections.items():
  raw=(base/rel).read_bytes(); lines=raw.decode().splitlines(); name='lvgl-9.2.1/'+rel
  info=z.getinfo(name)
  out['members'].append({'path':str(base/rel),'member':name,'equal':raw==z.read(name),
   'zip_size':info.file_size,'zip_timestamp':info.date_time,
   'excerpts':[[f'{i+1}: {lines[i]}' for i in range(a-1,min(b,len(lines)))] for a,b in ranges]})
# Enumerate each ordinary event token independently, preserving explicit assignments.
header=(base/'src/misc/lv_event.h').read_text()
body=header[header.index('typedef enum {')+len('typedef enum {'):header.index('} lv_event_code_t;')]
body=re.sub(r'/\*.*?\*/','',body,flags=re.S)
out['enum_directives']=[s.strip() for s in body.splitlines() if s.lstrip().startswith('#')]
body=re.sub(r'//[^\n]*','',body)
value=-1; out['enum']=[]
for token in body.split(','):
 token=token.strip()
 if not token: continue
 match=re.fullmatch(r'(LV_EVENT_\w+)(?:\s*=\s*(0x[0-9A-Fa-f]+|[0-9]+))?',token)
 if not match: raise ValueError(token)
 value=int(match.group(2),0) if match.group(2) else value+1
 out['enum'].append({'name':match.group(1),'value':value})
out['candidate_has_git']=(base/'.git').exists()
out['git']={}
apps=base.parents[2]
for key,args in {'head':['rev-parse','HEAD'], 'ignore':['check-ignore','-v','graphics/lvgl/lvgl/src/display/lv_display.c'], 'tracked':['ls-files','graphics/lvgl']}.items():
 p=subprocess.run(['git','-C',str(apps),*args],capture_output=True,text=True)
 out['git'][key]={'returncode':p.returncode,'stdout':p.stdout,'stderr':p.stderr}
out['integration']={}
for rel in ['Makefile','.gitignore']:
 lines=(base.parent/rel).read_text().splitlines()
 out['integration'][rel]=[f'{i+1}: {s}' for i,s in enumerate(lines) if rel=='.gitignore' or 54<=i+1<=80]
out['configuration_support']=[]
for rel,ranges in {'src/stdlib/lv_mem.c':[(1,26),(92,117)],'src/lv_conf_internal.h':[(17,26),(96,114),(314,325),(1007,1021)]}.items():
 lines=(base/rel).read_text().splitlines()
 out['configuration_support'].append({'path':str(base/rel),'excerpts':[[f'{i+1}: {lines[i]}' for i in range(a-1,b)] for a,b in ranges]})
print(json.dumps(out,ensure_ascii=False,indent=2))
'''
if __name__ == '__main__':
    p=subprocess.run(['wsl.exe','-d','Ubuntu-24.04','--exec','python3','-c',REMOTE],capture_output=True)
    if p.returncode:
        raise SystemExit(p.stderr.decode(errors='replace') or p.stdout.decode(errors='replace'))
    data=json.loads(p.stdout.decode())
    assert len(data['members'])==13 and all(m['equal'] for m in data['members'])
    (HERE/'candidate-review.json').write_text(json.dumps(data,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
    print('Independent local comparison: 13/13 equal; enum entries:',len(data['enum']))
    print('Event enum directives:',data['enum_directives'])
    print('Apps HEAD:',data['git']['head'])
