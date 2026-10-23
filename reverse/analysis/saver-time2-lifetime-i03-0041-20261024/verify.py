"""I03 retained-evidence coverage and sparse original-byte checks only."""
from pathlib import Path
import json
import re
import zipfile

OUT=Path(__file__).resolve().parent
TREE=OUT.parents[2]
MAIN=Path('D:/Documents/PlatformIO/Projects/cuktech-ap01-firmware')
ROOT=MAIN/'reverse/rehost'
guide=json.loads((ROOT/'guide-complete-0041.json').read_text(encoding='utf8'))
weather=json.loads((ROOT/'weather-calendar-complete-0041.json').read_text(encoding='utf8'))
rom=(MAIN/'roms/0041/ap01-1.0.2_0041.bin').read_bytes()
base=0x9ffff000
texts={
 'guide#/bounded_local_disassembly/saver_window_asm':guide['bounded_local_disassembly']['saver_window_asm'],
 'guide#/bounded_local_disassembly/saver_time_creator_asm':guide['bounded_local_disassembly']['saver_time_creator_asm'],
 'weather-calendar#/evidence/22/stdout':weather['evidence'][22]['stdout']}
rows={}
for origin,text in texts.items():
 for line in text.splitlines():
  m=re.match(r'^(a[0-9a-f]+):\s+([0-9a-f]{8}|[0-9a-f]{4})\s',line)
  if m:
   pc=int(m[1],16); h=m[2]
   rows[pc]=(int(h,16).to_bytes(len(h)//2,'little'),origin)
checks=[]
def eq(label,actual,expected):
 assert actual==expected,(label,actual,expected)
 checks.append(label)
def w(pc,n=4): return int.from_bytes(rom[pc-base:pc-base+n],'little')
def sx(v,n): return v-(1<<n) if v&(1<<(n-1)) else v
anchors=[0xa00a78d8,0xa00a78de,0xa00a78e0,0xa00a79c4,0xa00a79c8,0xa00a79ce,0xa00a79d2,0xa00a79ee,0xa00a7a08,0xa00a7a0a,0xa00a7a0e,0xa00a7a14,0xa00a7a18,0xa00a7d44,0xa00a7d4a,0xa00a7d4e,0xa00a7d52,0xa00a7d54,0xa00a7d58,0xa00a7d70,0xa00a7d74,0xa00a7d78,0xa00a7fbc,0xa00a7fbe,0xa00a7fc2,0xa00a7fca,0xa00a7fce,0xa00a7fd4,0xa00a7fd8,0xa00a7fdc,0xa00a7fde,0xa00a7fe2,0xa00a7fe6,0xa00a4f82,0xa00a4f88,0xa00a4f8a,0xa00a4f8e,0xa00a4f9e,0xa00a4fa0,0xa00a4fa4,0xa00a4fa8,0xa00a4fb0,0xa00a4fd6,0xa00a4fda,0xa00a4fde,0xa00a4fe0,0xa00a4fe4,0xa00a4f50,0xa00a4f54,0xa00a4f58,0xa00a4f5c,0xa00a4f60,0xa00a4f64,0xa00a4f66,0xa00a4f6e,0xa00a7660,0xa00a7668,0xa00a7694]
clear=[(0xa00a4fb2,0),(0xa00a4fb6,4),(0xa00a4fba,8),(0xa00a4fbe,24),(0xa00a4fc2,12),(0xa00a4fc6,16),(0xa00a4fca,20),(0xa00a4fce,28),(0xa00a4fd2,32)]
for pc in anchors+[pc for pc,_ in clear]:
 raw,origin=rows[pc]
 eq(hex(pc)+' retained bytes',rom[pc-base:pc-base+len(raw)],raw)
for pc,offset in clear:
 v=w(pc)
 eq(hex(pc)+' clear ctx word',(v&127,(v>>12)&7,(v>>15)&31,(v>>20)&31,sx(((v>>25)<<5)|((v>>7)&31),12)),(35,2,15,0,offset))
for pc,src,reg,offset in [(0xa00a7fca,18,25,4),(0xa00a7fce,24,25,0),(0xa00a7fde,25,9,16),(0xa00a4fe4,0,9,16)]:
 v=w(pc)
 eq(hex(pc)+' held pointer store',(v&127,(v>>12)&7,(v>>15)&31,(v>>20)&31,sx(((v>>25)<<5)|((v>>7)&31),12)),(35,2,reg,src,offset))
for pc,target in [(0xa00a78e0,0xa008e362),(0xa00a7d54,0xa008e362),(0xa00a7d74,0xa008e362),(0xa00a7fc2,0xa00b3a68),(0xa00a4fda,0xa00b3abe),(0xa00a4fe0,0xa008ab8a),(0xa00a4f50,0xa008ae58),(0xa00a4f66,0xa008ab8a),(0xa00a7694,0xa00ded6c)]:
 v=w(pc); off=((v>>31)<<20)|(((v>>12)&255)<<12)|(((v>>20)&1)<<11)|(((v>>21)&1023)<<1)
 eq(hex(pc)+' JAL target',(v&127,(v>>7)&31,pc+sx(off,21)),(111,1,target))
eq('Time2 ctx request40 I immediate',sx(w(0xa00a7d70)>>20,12),40)
eq('wrapper free C.MV a0,s2',w(0xa00a4fde,2),0x854a)
eq('unregister userdata C.MV a1,s1',w(0xa00a4fb0,2),0x85a6)
eq('callback address ADDI',sx(w(0xa00a4fd6)>>20,12),0x6b0)
# Bounded reuse inventory: pointers and counts only, no copied function bodies.
terms=['a00a4f82','a00ab6b0','a00a7766']
reuse=[]
for p in sorted(ROOT.glob('*.json')):
 text=p.read_text(encoding='utf8',errors='replace').lower()
 hits=[t for t in terms if t in text]
 if hits: reuse.append({'file':p.name,'terms':hits})
late=MAIN/'evidence/rea-0041-20261017/round3/evidence/whole-rom-round3-initial.evidence.json'
late_records=json.loads(late.read_text(encoding='utf8'))['records']
late_hits=[{'index':i,'operation':r.get('operation'),'evidence_id':r.get('evidence_id')} for i,r in enumerate(late_records) if any(t in str(r).lower() for t in terms)]
pass3=MAIN/'reverse/analysis/0041-20261013/0041-ghidra-pass3.txt'
pass_hits=[i+1 for i,line in enumerate(pass3.read_text(encoding='utf8',errors='replace').splitlines()) if any(t in line.lower() for t in terms)]
with zipfile.ZipFile(ROOT/'ap01-ui-0041-complete-source.zip') as z:
 member='tools/ap01/ap01-ui-guide.h'; lines=z.read(member).decode('utf8').splitlines()
 zip_hits=[i+1 for i,line in enumerate(lines) if any(t in line.lower() for t in terms)]
 eq('guide ZIP is replacement saver source',any('g_ap01_ui_saver_kind' in line for line in lines),True)
result={'status':'PASS','static_only':True,'checks':checks,'retained_anchor_count':len(anchors)+len(clear),'retained_origins':list(texts),'new_rom_functionality':0,'new_rom_windows_exported':0,'reuse':{'top_level_main_rehost_json':reuse,'late_round3_exact_address_hits':late_hits,'pass3_exact_address_hit_lines':pass_hits,'zip':{'member':member,'exact_address_hit_lines':zip_hits,'role':'SIM replacement source, not ROM ownership evidence'}},'limits':['Old guide creator plus old weather-calendar DELETE already cover the local lifecycle body.','Only wrapper20 is directly freed by the Time2 DELETE body; ctx40 final free is not established.','No new root destructor scan, runtime lifecycle, or cross-type cleanup inference.']}
(OUT/'verification.json').write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n',encoding='utf8')
print(json.dumps({'status':'PASS','checks':len(checks),'retained_anchors':result['retained_anchor_count'],'new_rom_functionality':0}))
