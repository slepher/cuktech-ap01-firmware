"""A33 static bounded source-argument checks. Never executes target code."""
from pathlib import Path
import json, sys, zipfile
OUT=Path(__file__).resolve().parent
TREE=OUT.parents[2]
MAIN=Path('D:/Documents/PlatformIO/Projects/cuktech-ap01-firmware')
sys.path.insert(0,str(TREE/'reverse/analysis/display-event-flow-g05-0041-20261023'))
import read_rom as rr
def u32(a): return int.from_bytes(rr.rom[a-rr.BASE:a-rr.BASE+4],'little')
windows=[('existing photo branch ABI',0xa00b17ea,0xa00b1828),('setter preserves source',0xa00ed802,0xa00ed80a),('class0 data handoff',0xa00ed830,0xa00ed846),('memory input preserves pointer',0xa0107dfe,0xa0107e22)]
rows=[dict(window=n,**r) for n,a,z in windows for r in rr.rows(a,z)]
D={int(x['pc'],16):x for x in rows};checks=[]
def ck(a,s):
 assert D[a]['asm']==s,(hex(a),D[a],s)
 checks.append(dict(address=hex(a),asm=s))
for a,s in {0xa00b17ec:'c.li a1, 7',0xa00b17f2:'c.lw a5, 0x10(a0)',0xa00b17f4:'c.lw s1, 4(a5)',0xa00b17f8:'lw a6, 0xc(s1)',0xa00b17fc:'c.addi a6, 1',0xa00b1802:'c.li a6, 0',0xa00b1804:'lui a5, 0xa0560',0xa00b1808:'addi a5, a5, -0x1bc',0xa00b1810:'c.lw a0, 0(s1)',0xa00b1812:'sw a6, -0x144(s0)',0xa00b181a:'lw a6, -0x144(s0)',0xa00b1824:'sw a6, 0xc(s1)',0xa00ed808:'c.mv s3, a1',0xa00ed830:'c.mv a0, s3',0xa00ed838:'lw a0, 0x10(s3)',0xa0107dfe:'c.mv s1, a0',0xa0107e12:'sw s1, -0x668(s0)',0xa0107e16:'sw zero, -0x660(s0)',0xa0107e1a:'sb zero, -0x664(s0)'}.items():ck(a,s)
for a,t in [(0xa00b17ee,0xa00dcee4),(0xa00b1816,0xa00ed7f4),(0xa00ed832,0xa00dd454),(0xa00ed83c,0xa0107dea),(0xa0107e0a,0xa0024906),(0xa0107e1e,0xa010a65a)]:
 assert D[a]['target']==hex(t)
 checks.append(dict(address=hex(a),target=hex(t)))
w=u32(0xa00b180c)
fields=[w&127,(w>>12)&7,w>>27,(w>>7)&31,(w>>15)&31,(w>>20)&31,(w>>25)&3]
assert fields==[11,4,8,11,15,16,2]
# Independent B-immediate reconstruction: unsigned 4 >= next goes directly to table load.
wbranch=u32(0xa00b17fe)
imm=((wbranch>>31)<<12)|(((wbranch>>7)&1)<<11)|(((wbranch>>25)&63)<<5)|(((wbranch>>8)&15)<<1)
assert wbranch&127==99 and (wbranch>>12)&7==7 and 0xa00b17fe+imm==0xa00b1804
model=MAIN/'evidence/rea-0041-20261017/ghidra/Ghidra/Processors/RISCV/data/languages/ap01thead2.sinc'
s=model.read_text();i=s.index(':th.lrw ');rule=s[i:s.index('\n}',i)+2]
assert 'local delta:4 = rs2 << thshift;' in rule and 'local value:4 = *[ram]:4 ea;' in rule
table=[]
for i,p in enumerate([0xa01c4a50,0xa03f3b08,0xa046a894,0xa04a09b8,0xa037c064]):
 assert u32(0xa055fe44+4*i)==p
 assert u32(p+16)==p+28
 table.append(dict(index=i,slot=hex(0xa055fe44+4*i),source=hex(p),data=hex(u32(p+16)),data_size=u32(p+12)))
r=MAIN/'reverse/rehost';reuse=[]
for fn,path in [('photo-evidence-round3.json',['rea_records',3,'normalized_result']),('main-knob-0041-round2.json',['records',1,'normalized_result','pseudocode']),('system-complete-0041.json',['cached_evidence','main_a00afc88'])]:
 p=json.loads((r/fn).read_text(encoding='utf8'));v=p
 for k in path:v=v[k]
 assert 'uVar7 = custom0.rd();' in v and 'FUN_ram_a00ed7f4(*puVar17,uVar7);' in v
 reuse.append(dict(file=fn,path=path,status='existing complete photo branch retains custom0 source limitation'))
with zipfile.ZipFile(r/'ap01-ui-0041-complete-source.zip') as z:
 s=z.read('tools/ap01/ap01-ui-pages.h').decode();assert 'lv_gif_set_src(pet, &ap01_pets[g_ap01_ui_pet_index]);' in s
# Bounded late-round3 lookup only; do not confuse semantic-free text absence with missing analysis.
late=[]
for p in sorted(r.glob('*round3*.json')):
 s=p.read_text(encoding='utf8',errors='replace')
 if any(t in s.lower() for t in ['a00ed7f4','a055fe44','a00b180c']):
  late.append(dict(file=p.name,terms=[t for t in ['a00ed7f4','a055fe44','a00b180c'] if t in s.lower()]))
result=dict(status='PASS',static_only=True,baseline='b673714',named_abi_checks=len(checks),windows=windows,rows=rows,vendor=dict(address='0xa00b180c',raw='8bc50745',fields=fields,semantics='a1 = load32(a5 + (a6 << 2))',model_path=str(model),rule=rule),table=table,reuse=reuse,late_round3_hits=late,zip_member='tools/ap01/ap01-ui-pages.h',limits='No execution; GIF constructor internal persistence/copy and deeper decode/cleanup not audited. No full-function export.')
(OUT/'evidence.json').write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n',encoding='utf8')
print(json.dumps(dict(status=result['status'],windows=len(windows),named_abi_checks=result['named_abi_checks'],table_entries=len(table))))
