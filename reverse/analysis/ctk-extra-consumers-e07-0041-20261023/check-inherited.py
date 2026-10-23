"""Read old SIM/ROM research without extracting or executing its source."""
import json,re,zipfile
from pathlib import Path
ROOT=Path('D:/Documents/PlatformIO/Projects/cuktech-ap01-firmware')
HERE=Path(__file__).resolve().parent
names=['charge-complete-0041.json','details-0041-round4.json','charge-0041-round4.json','main-knob-0041-round2.json','detail-knob-0041-round2.json','page-logic-0041.json','page-logic-evidence.json','page-logic-evidence2.json']
terms=['a00a53c0','a00a1aa8','a00a12d0','a00f4740','a00adabc','a00f5288','a00a3c8a','a01917d0','a01b28ce','pRemote','0x10000','0x40000',' + 0x34',' + 0x38','[0xd]','[0xe]']
results=[]
def walk(o,path='$'):
 if isinstance(o,dict):
  for k,v in o.items():yield from walk(v,path+'.'+k)
 elif isinstance(o,list):
  for i,v in enumerate(o):yield from walk(v,path+f'[{i}]')
 elif isinstance(o,str):yield path,o
for name in names:
 p=ROOT/'reverse/rehost'/name;o=json.loads(p.read_text(encoding='utf-8-sig'))
 paths={t:[path for path,s in walk(o) if t.lower() in s.lower()] for t in terms}
 results.append(dict(source=str(p),top_level_keys=list(o),term_paths={t:(dict(count=len(v),sample_paths=v[:4]) if len(v)>12 else v) for t,v in paths.items() if v}))
 print(name,{t:len(v) for t,v in paths.items() if v})
# References/maps are inventories, not independent runtime evidence.
for rel in ['reverse/reports/ap01/application-function-matrix-0041.json','reverse/reports/ap01/factory-reference-map-0041-20261020.md','reverse/analysis/0041-20261013/0041-ghidra-pass3.txt']:
 p=ROOT/rel;text=p.read_text(encoding='utf-8-sig');lines=text.splitlines()
 hits={t:[i+1 for i,l in enumerate(lines) if t.lower() in l.lower()] for t in terms}
 results.append(dict(source=str(p),term_lines={t:(dict(count=len(v),sample_lines=v[:4]) if len(v)>12 else v) for t,v in hits.items() if v}))
 print(p.name,{t:len(v) for t,v in hits.items() if v})
zpath=ROOT/'reverse/rehost/ap01-ui-0041-complete-source.zip'
z=zipfile.ZipFile(zpath);members=[]
for name in ['tools/ap01/ap01-ui-charge.h','tools/ap01/ap01-ui-details.h']:
 text=z.read(name).decode('utf-8-sig');lines=text.splitlines()
 keys=['a00f4740','a00f5288','a00adabc','pRemote','0x34','0x38','bank->','remaining','ap01_sim_get_port']
 hits={t:[dict(line=i+1,text=l.strip()[:200]) for i,l in enumerate(lines) if t.lower() in l.lower()] for t in keys}
 members.append(dict(member=name,bytes=z.getinfo(name).file_size,term_lines={t:(dict(count=len(v),sample_lines=v[:4]) if len(v)>12 else v) for t,v in hits.items() if v}))
 print(name,{t:len(v) for t,v in hits.items() if v})
(HERE/'inherited-source-crosswalk.json').write_text(json.dumps(dict(inputs=results,zip_source=str(zpath),zip_members=members,limits='Read-only inventories and text/address cross-checks. Existing ROM instruction records are inherited evidence. SIM services/render reconstruction do not prove native wire-field consumers. No source extraction, build or replay.'),ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
