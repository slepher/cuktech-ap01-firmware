"""Read only selected local WSL candidate sources; never build or run target code."""
import json
import pathlib
import subprocess

OUT = pathlib.Path(__file__).resolve().parent
REMOTE = r'''
import json, pathlib, subprocess, zipfile, re
root = pathlib.Path('/home/slepher/nuttx-ap01-sim')
base = root/'apps/graphics/lvgl/lvgl'
selections = {
 'lv_version.h': [(1,30)],
 'src/display/lv_display.c': [(62,212),(734,739),(780,797),(912,933)],
 'src/display/lv_display_private.h': [(36,167)],
 'src/misc/lv_ll.c': [(16,18),(57,78)],
 'src/misc/lv_ll.h': [(29,35)],
 'src/misc/lv_event.c': [(63,105)],
 'src/misc/lv_event_private.h': [(27,43)],
 'src/misc/lv_event.h': [(30,116)],
 'src/misc/lv_array.h': [(35,40)],
 'src/misc/lv_types.h': [(53,58)],
 'src/drivers/nuttx/lv_nuttx_entry.c': [(96,175)],
 'src/drivers/nuttx/lv_nuttx_fbdev.c': [(34,47),(75,107),(383,405)],
 'src/draw/lv_draw.h': [(70,108)],
}
def git(tree, *args):
 p=subprocess.run(['git','-C',str(root/tree),*args],text=True,capture_output=True)
 return {'returncode':p.returncode,'stdout':p.stdout,'stderr':p.stderr}
result={'root':str(root), 'git':{
 'apps_head':git('apps','rev-parse','HEAD'),
 'nuttx_head':git('nuttx','rev-parse','HEAD'),
 'candidate_ignore':git('apps','check-ignore','-v','graphics/lvgl/lvgl/src/display/lv_display.c'),
 'package_diff':git('apps','diff','--','graphics/lvgl/Makefile','graphics/lvgl/.gitignore'),
 'package_files':git('apps','ls-files','graphics/lvgl'),
},'candidate_has_git':(base/'.git').exists(),'sources':[]}
archive=root/'apps/graphics/lvgl/v9.2.1.zip'
result['archive']={'path':str(archive),'present':archive.is_file()}
with zipfile.ZipFile(archive) as z:
 for rel,ranges in selections.items():
  path=base/rel
  raw=path.read_bytes()
  member='lvgl-9.2.1/'+rel
  lines=raw.decode().splitlines()
  result['sources'].append({'path':str(path),'archive_member':member,
    'equals_local_archive_member':raw==z.read(member),
    'excerpts':[{'start_line':a,'end_line':min(b,len(lines)),
                 'lines':[f'{i+1}: {lines[i]}' for i in range(a-1,min(b,len(lines)))]} for a,b in ranges]})
event=(base/'src/misc/lv_event.h').read_text()
part=event[event.index('LV_EVENT_ALL = 0'):event.index('LV_EVENT_PREPROCESS =')]
names=re.findall(r'^\s*(LV_EVENT_\w+)(?:\s*=\s*0)?\s*,',part,re.M)
result['candidate_event_enum']={name:i for i,name in enumerate(names) if name in ['LV_EVENT_ALL','LV_EVENT_DELETE','LV_EVENT_REFR_REQUEST']}
for rel in ['Makefile','.gitignore']:
 p=root/'apps/graphics/lvgl'/rel
 result[rel]={'path':str(p),'text':p.read_text()}
print(json.dumps(result,ensure_ascii=False,indent=2))
'''

if __name__ == '__main__':
    proc = subprocess.run(['wsl.exe', '-d', 'Ubuntu-24.04', '--exec', 'python3', '-c', REMOTE], capture_output=True)
    if proc.returncode:
        raise SystemExit(proc.stderr.decode(errors='replace') or proc.stdout.decode(errors='replace'))
    obj = json.loads(proc.stdout.decode('utf-8'))
    (OUT/'source-evidence.json').write_text(json.dumps(obj, ensure_ascii=False, indent=2)+'\n', encoding='utf-8')
    print('Read-only candidate capture:',len(obj['sources']),'selected files')
    print('Local archive equal:',sum(s['equals_local_archive_member'] for s in obj['sources']))
    print('Candidate enums:',obj['candidate_event_enum'])
