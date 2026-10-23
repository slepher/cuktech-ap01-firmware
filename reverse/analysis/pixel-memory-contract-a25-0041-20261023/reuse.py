from pathlib import Path
import zipfile,json,re
root=Path('D:/Documents/PlatformIO/Projects/cuktech-ap01-firmware/reverse');out=Path('reverse/analysis/pixel-memory-contract-a25-0041-20261023')
keys=['a008e3ac','a007fe60','a007fe4e','a007ff40','a0081d90','a0081f26','62fc9674','62fc964c','lv_draw_buf','draw_buf_handlers']
files=[root/'reports/ap01/application-function-matrix-0041.json',root/'reports/ap01/factory-reference-map-0041-20261020.md']+[root/'rehost'/n for n in ['system-complete-0041.json','charge-complete-0041.json','page-logic-0041.json','details-0041-round4.json','charge-0041-round4.json']]+[root/'analysis/0041-20261013/0041-ghidra-pass3.txt']
records=[]
for p in files:
 lines=p.read_text(encoding='utf8',errors='replace').splitlines();hits=[dict(line=i+1,text=l[:600]) for i,l in enumerate(lines) if any(k in l.lower() for k in keys)]
 records.append(dict(path=str(p),hits=hits))
p=root/'rehost/ap01-ui-0041-complete-source.zip'
with zipfile.ZipFile(p) as z:
 members=z.namelist();texts=[n for n in members if n.lower().endswith(('.c','.h','.md','.json','.txt','.py'))]
 zh=[]
 for n in texts:
  t=z.read(n).decode('utf8',errors='replace');hits=[dict(line=i+1,text=l[:400]) for i,l in enumerate(t.splitlines()) if any(k in l.lower() for k in keys)]
  if hits:zh.append(dict(member=n,hits=hits[:30],hit_count=len(hits)))
 zinfo=dict(path=str(p),member_count=len(members),searched_text_members=len(texts),matching_members=zh,representative_members=members[:20])
res=dict(query_terms=keys,files=records,source_zip=zinfo,interpretation='No match means only bounded exact-term search; SIM source is not original allocator proof.')
(out/'reuse-crosscheck.json').write_text(json.dumps(res,indent=2,ensure_ascii=False),encoding='utf8')
print(json.dumps(res,ensure_ascii=False))
