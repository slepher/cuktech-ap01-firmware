"""Read existing reports/selected ZIP members; no extraction or execution."""
import json
from pathlib import Path
import re
import zipfile

HERE=Path(__file__).resolve().parent
TREE=HERE.parents[2]
MAIN=Path('D:/Documents/PlatformIO/Projects/cuktech-ap01-firmware')
pattern=re.compile(r'a0081554|a008acfa|a0084b96|a007ffa0|a00814f4|a00800b4|lv_display\.c|lv_nuttx_entry\.c|lv_event\.c',re.I)
metadata=re.compile(r'LVGL|9\.2\.1|8ff533|6fc5b3|NUTTX_ROOT|apps/graphics/lvgl|SIM|native|reconstruct',re.I)
out={'mode':'read only metadata and selected textual members, no extraction/execution','reports':[],'zip':{}}
for rel in ['reverse/reports/ap01/application-rehost-complete-0041-20261017.md','reverse/reports/ap01/application-function-matrix-0041.json','reverse/reports/ap01/factory-reference-map-0041-20261020.md','reverse/analysis/factory-reference-map-0041.json']:
 path=TREE/rel
 lines=path.read_text(encoding='utf-8').splitlines()
 out['reports'].append({'path':str(path),'exact_scope_matches':[{'line':i+1,'text':s} for i,s in enumerate(lines) if pattern.search(s)]})
system_path=MAIN/'reverse/rehost/system-complete-0041.json'
d=json.loads(system_path.read_text(encoding='utf-8'))
matches=[]
def visit(value,key='$'):
 if isinstance(value,dict):
  for k,v in value.items(): visit(v,key+'.'+k)
 elif isinstance(value,list):
  for i,v in enumerate(value): visit(v,key+f'[{i}]')
 elif isinstance(value,str):
  for line in value.splitlines():
   if pattern.search(line): matches.append({'key':key,'line':line})
visit(d)
out['system']={'path':str(system_path),'scope':d['scope'],'cached_evidence_keys':list(d['cached_evidence']), 'exact_scope_matches':matches,'boundaries':d['reconstruction_boundaries']}
archive=MAIN/'reverse/rehost/ap01-ui-0041-complete-source.zip'
with zipfile.ZipFile(archive) as z:
 names=z.namelist()
 out['zip']={'path':str(archive),'member_count':len(names),'scope_basename_matches':[n for n in names if re.search(r'lv_display|lv_event|lv_nuttx',n,re.I)],'selected_members':[]}
 for name in ['tools/ap01/README.md','tools/ap01/nuttx-sim.sh','tools/ap01/nuttx-sim.c','tools/ap01/ap01-ui.h']:
  lines=z.read(name).decode('utf-8').splitlines()
  # Preserve only source/version markers and exact ROM-scope hits, not source copies.
  out['zip']['selected_members'].append({'name':name,'scope_matches':[{'line':i+1,'text':s} for i,s in enumerate(lines) if pattern.search(s)],'source_markers':[{'line':i+1,'text':s[:500]} for i,s in enumerate(lines) if metadata.search(s)][:18]})
out['current_relocation']=[{'old':'tools/ap01/'+n,'current':str(TREE/'tooling/scripts'/n),'present':(TREE/'tooling/scripts'/n).is_file()} for n in ['README.md','nuttx-sim.sh','nuttx-sim.c','ap01-ui.h']]
(HERE/'reuse-review.json').write_text(json.dumps(out,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
print('reports exact matches:',sum(len(x['exact_scope_matches']) for x in out['reports']))
print('system exact matches:',len(matches),'zip basename matches:',out['zip']['scope_basename_matches'])
for m in out['zip']['selected_members']:
 print(m['name'],'scope hits',len(m['scope_matches']))
 for line in m['source_markers']:
  if re.search(r'9\.2\.1|8ff533|6fc5b3|apps/graphics/lvgl',line['text']): print(line)
