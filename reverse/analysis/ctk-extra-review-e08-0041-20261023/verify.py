"""E08 independent checks of fixed E07 candidates; no discovery or function export."""
import json
from collections import Counter
from pathlib import Path
HERE=Path(__file__).resolve().parent
OLD=HERE.parent/'ctk-extra-consumers-e07-0041-20261023'
ROOT=Path('D:/Documents/PlatformIO/Projects/cuktech-ap01-firmware')
BASE=0x9ffff000
index=json.loads((OLD/'focused-call-index.json').read_text())
rom=(ROOT/'roms/0041/ap01-1.0.2_0041.bin').read_bytes()
def sx(v,n): return v-(1<<n) if v&(1<<(n-1)) else v
rows=[]
for r in index['matches']:
 pc=int(r['address'],16); instructions=r['instructions']
 for i in instructions:
  off=int(i['address'],16)-BASE; raw=bytes.fromhex(i['hex'])
  assert rom[off:off+len(raw)]==raw
 w=int.from_bytes(bytes.fromhex(instructions[0]['hex']),'little')
 if r['kind']=='JAL':
  assert w&127==0x6f
  imm=((w>>31)<<20)|(((w>>12)&255)<<12)|(((w>>20)&1)<<11)|(((w>>21)&1023)<<1)
  target=(pc+sx(imm,21))&0xffffffff; link=(w>>7)&31
 else:
  v=int.from_bytes(bytes.fromhex(instructions[1]['hex']),'little')
  assert w&127==0x17 and v&0x707f==0x67
  assert (w>>7)&31==(v>>15)&31
  target=(pc+sx(w&0xfffff000,32)+sx(v>>20,12))&0xfffffffe
  link=(v>>7)&31
 assert target==int(r['target'],16) and link==1
 src=Path(r['owner_body_source']['source'])
 e=json.loads(src.read_text())['structuredContent']
 assert e['evidence_id']==r['owner_body_source']['evidence_id']
 body=e['normalized_result']['body'];assert body==r['owner_body_source']['body']
 inside=any(int(b['start'],16)<=pc<=int(b['end'],16) for b in body['ranges'])
 assert inside==r['inside_retained_body']
 rows.append(dict(address=r['address'],target=hex(target),link_register='ra',inside_recorded_preceding_body=inside))
counts=Counter(r['target'] for r in rows)
assert counts=={'0xa00a53c0':14,'0xa01b28ce':3}
orphan=next(r for r in index['matches'] if r['address']=='0xa00a1aa8')
assert orphan['owner'] is None and orphan['preceding_entry']=='0xa00a12d0'
assert orphan['owner_body_source']['body']['ranges']==[{'start':'0xa00a12d0','end':'0xa00a144f'}]
complete=json.loads((ROOT/'reverse/rehost/charge-complete-0041.json').read_text())
inherited=[]
for n,addr in [(8,'0xa00f4610'),(9,'0xa00f44e8'),(19,'0xa00f5288')]:
 r=complete['records'][n];assert r['parameters']['procedure']==addr
 inherited.append(dict(record=n,procedure=addr,evidence_id=r['evidence_id']))
# This fixed-list check deliberately makes no new search-completeness assertion.
result=dict(scope='Old-conclusion review only; fixed E07 candidate list, no rescan or function dump',
 checked_candidates=rows, inherited_records=inherited,
 boundary='a00a1aa8 is outside the recorded a00a12d0..a00a144f body; real owner/entry/CFG remain unknown',
 limits=['14/3 are inherited exact-encoding candidates, not a complete xref census',
 'Recorded body membership does not authenticate real function boundaries',
 'No item+34/+38 consumer, conversion or borrowing lifetime newly recovered'],
 new_functionality=0)
(HERE/'review-result.json').write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
print('PASS: 17 fixed candidates, original bytes/targets/ra and recorded bodies; 3 inherited records; new functionality 0')
