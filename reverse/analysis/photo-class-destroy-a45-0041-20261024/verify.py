"""A45: read-only reuse and sparse object-identity checks, never runs ROM."""
from pathlib import Path
import json, sys, zipfile
OUT=Path(__file__).resolve().parent
TREE=OUT.parents[2]
MAIN=Path('D:/Documents/PlatformIO/Projects/cuktech-ap01-firmware')
sys.path.insert(0,str(TREE/'reverse/analysis/display-event-flow-g05-0041-20261023'))
import read_rom as rr
r=MAIN/'reverse/rehost'
checks=[]
rows=list(rr.rows(0xa00b17ec,0xa00b17f8))+list(rr.rows(0xa00b1810,0xa00b181a))
D={int(x['pc'],16):x for x in rows}
for pc,asm in {0xa00b17ec:'c.li a1, 7',0xa00b17f2:'c.lw a5, 0x10(a0)',0xa00b17f4:'c.lw s1, 4(a5)',0xa00b1810:'c.lw a0, 0(s1)'}.items():
 assert D[pc]['asm']==asm
 checks.append(dict(pc=hex(pc),asm=asm))
for pc,target in [(0xa00b17ee,0xa00dcee4),(0xa00b1816,0xa00ed7f4)]:
 assert D[pc]['target']==hex(target)
 checks.append(dict(pc=hex(pc),target=hex(target)))
p=json.loads((r/'photo-evidence-round3.json').read_text(encoding='utf8'))
s=p['rea_records'][3]['normalized_result']
assert 'FUN_ram_a00ed7f4(*puVar17,uVar7);' in s
reuse=[dict(file='photo-evidence-round3.json',pointer='/rea_records/3',evidence=p['rea_records'][3].get('evidence_id'),scope='ctx[0] setter consumer; no creator identity from this call')]
for name,path in [('main-knob-0041-round2.json',['records',1,'normalized_result','pseudocode']),('system-complete-0041.json',['cached_evidence','main_a00afc88'])]:
 x=json.loads((r/name).read_text(encoding='utf8'))
 for k in path:x=x[k]
 assert 'FUN_ram_a00ed7f4(*puVar17,uVar7);' in x
 reuse.append(dict(file=name,pointer=path,scope='same consumer; not class installation proof'))
with zipfile.ZipFile(r/'ap01-ui-0041-complete-source.zip') as z:
 s=z.read('tools/ap01/ap01-ui-pages.h').decode()
 assert 'lv_obj_t *pet = lv_gif_create(g_ap01_ui_root);' in s
 assert 'lv_gif_set_src(pet, &ap01_pets[g_ap01_ui_pet_index]);' in s
 reuse.append(dict(file='ap01-ui-0041-complete-source.zip',member='tools/ap01/ap01-ui-pages.h',scope='SIM replacement creator only; not ROM creator evidence'))
late=[]
for f in sorted(r.glob('*round3*.json')):
 s=f.read_text(encoding='utf8',errors='replace').lower()
 hits=[t for t in ['a00ed7f4','a00b1816','a055fe44'] if t in s]
 if hits:late.append(dict(file=f.name,terms=hits))
# Existing retained bundle only: index selected by setter text; do not open or mutate REA session.
p=json.loads((MAIN/'evidence/rea-0041-20261017/evidence/whole-rom-private-20261023.evidence.json').read_text(encoding='utf8'))
hits=[]
for i,x in enumerate(p['records']):
 if 'a00ed7f4' in json.dumps(x).lower():
  hits.append(dict(index=i,evidence=x['evidence_id'],operation=x['operation'],parameters=x['parameters']))
result=dict(status='PASS',baseline='82be763',static_only=True,rows=rows,checks=checks,reuse=reuse,late_round3_hits=late,retained_setter_text_hits=hits,
 inherited=['A33/A35 consumer/source ABI','A37/A39 O/derived-region ownership','A41/A42 setter teardown','H03 a00d7806 class+8 dtor(class,obj) walker'],
 new_functionality=0,unknown='actual photo ctx[0] creator and installed class pointer, therefore concrete destructor/free(O)/derived-slot DELETE connection',
 boundary='selected prior photo/knob/system complete and ZIP member, late *round3*.json exact consumer terms, retained whole-rom bundle exact setter text; no global ROM/reference scan; absence is not proof of no previous analysis')
(OUT/'evidence.json').write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n',encoding='utf8')
print(json.dumps(dict(status='PASS',checks=len(checks),retained_hits=len(hits),new_functionality=0)))
