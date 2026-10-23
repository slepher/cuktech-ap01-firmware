"""G07: bounded static ROM checks; imports only the retained passive decoder."""
from pathlib import Path
import sys,json,zipfile
ROOT=Path(__file__).resolve().parents[3]
OUT=Path(__file__).resolve().parent
sys.path.insert(0,str(ROOT/'reverse/analysis/display-event-flow-g05-0041-20261023'))
import read_rom as rr
MAIN=Path('D:/Documents/PlatformIO/Projects/cuktech-ap01-firmware')
# Old conclusions are compared in place, never re-exported or counted as new recovery.
g=json.loads((ROOT/'reverse/analysis/display-event-flow-g05-0041-20261023/evidence.json').read_text())
f=json.loads((ROOT/'reverse/analysis/factory-test-0041-20261023/retained-initializer.json').read_text())['function']
old=[]
for w in g['windows']:
 if w['name'] in ('alternative_install','alternative_callback'):
  for row in w['rows']:
   a=int(row['pc'],16);b=bytes.fromhex(row['raw']);assert rr.rom[a-rr.BASE:a-rr.BASE+len(b)]==b
  old.append(dict(source='G05/evidence.json',window=w['name'],check='old conclusion raw-byte recheck; no new behavior'))
range0=f['raw_ranges'][0];rb=bytes.fromhex(range0['hex']);ra=int(range0['start'],16)
for a,z,label in [(0xa005b100,0xa005b10e,'state allocation'),(0xa005be08,0xa005be62,'timer/notifier/fb caller'),(0xa005c83e,0xa005c8c4,'normal deinit registration')]:
 assert rr.rom[a-rr.BASE:z-rr.BASE]==rb[a-ra:z-ra]
 old.append(dict(source=f['evidence_id'],start=hex(a),end=hex(z),purpose=label,check='old retained raw-byte recheck'))
# Only new identity and missing dependency windows are retained here.
spans=[('fb_entry_identity',0xa0083376,0xa008337e),('fd_identity',0xa008342c,0xa008343c),('poll_init_type_and_watcher',0xa009e5f6,0xa009e638),('watcher_callback_store',0xa009cd6e,0xa009cd94),('poll_start',0xa009f9b6,0xa009fa38),('poll_stop',0xa009f972,0xa009f9b6),('stop_wrapper',0xa01b2cb0,0xa01b2ce4),('poll_callback_adapter',0xa009f8ea,0xa009f972),('owner_close_callback',0xa007ff54,0xa007ffa0)]
windows=[];D={}
for name,a,z in spans:
 rows=list(rr.rows(a,z));assert sum(len(bytes.fromhex(v['raw'])) for v in rows)==z-a
 assert all(not v['asm'].startswith('THEAD') for v in rows),(name,'vendor word requires separate model verification')
 windows.append(dict(name=name,start=hex(a),end=hex(z),rows=rows));D.update({int(x['pc'],16):x for x in rows})
checks=[]
def asm(a,s):
 assert D[a]['asm']==s,(hex(a),D[a]['asm'],s)
 checks.append(dict(pc=hex(a),asm=s))
def edge(a,t):
 assert D[a]['target']==hex(t),(hex(a),D[a],hex(t))
 checks.append(dict(pc=hex(a),target=hex(t)))
for a,t in {0xa0083430:0xa007fe32,0xa009e62e:0xa009cd4e,0xa009f9e2:0xa009f972,0xa009f9fe:0xa009ec98,0xa009f986:0xa009f442,0xa009f9a8:0xa009e212,0xa01b2cd4:0xa009f972,0xa009f908:0xa009f442,0xa007ff92:0xa008ab8a}.items():edge(a,t)
for a,s in {0xa0083376:'lw s6, 0(a0)',0xa008337a:'lw s3, 4(a0)',0xa0083436:'c.sw a5, 0x58(s1)',0xa009e5fc:'sb a5, 8(s5)',0xa009e600:'sw a5, 0x2c(s5)',0xa009e604:'sw s3, 4(s5)',0xa009e628:'addi a1, a1, -0x716',0xa009e634:'sw zero, 0x30(s5)',0xa009cd86:'c.sw a1, 0(a0)',0xa009cd88:'c.sw a2, 0x24(a0)',0xa009f9da:'c.mv s2, a2',0xa009f9ea:'andi a5, a1, 8',0xa009f9ee:'andi a2, a1, 1',0xa009f9f8:'c.lw a0, 4(s1)',0xa009f9fa:'addi a1, s1, 0x34',0xa009fa1c:'sw s2, 0x30(s1)',0xa009fa28:'c.li a0, 0',0xa009fa2e:'c.andi a1, 2',0xa009fa32:'ori a2, a2, 4',0xa009f992:'andi a4, a5, -5',0xa009f9a4:'c.lw a1, 0x58(s1)',0xa009f8fe:'addi s2, a1, -0x34',0xa009f92c:'lw a5, -4(s1)',0xa009f934:'c.mv a0, s2',0xa009f936:'c.jalr a5',0xa009f944:'andi a4, a2, 2',0xa009f958:'ori a5, a5, 2',0xa009f964:'lw a4, -4(s1)',0xa009f96a:'c.li a1, 0',0xa009f96c:'c.mv a0, s2',0xa009f96e:'c.jalr a4',0xa007ff5e:'c.lw s1, 0(a0)',0xa007ff60:'lw a5, 0x180(s1)',0xa007ff66:'sw a5, 0x180(s1)',0xa007ff6a:'bgtz a5, 0x2c'}.items():asm(a,s)
# Bounded provenance lookup: records rather than dumping megabyte single-line JSON.
need=['a008335e','a00806f8','a009f9b6','a00806d0','a009f8ea','a009f972','a01b2cb0','a007ff54','state+58','work_queue','work_cancel']
rev=MAIN/'reverse';names=['application-rehost-complete-0041-20261017.md','application-function-matrix-0041.json','factory-reference-map-0041-20261020.md']
fs=[rev/'reports/ap01'/n for n in names]
for pat in ['*-complete-0041.json','page-logic*.json','details-0041-round4.json','charge-0041-round4.json','main-knob-0041-round2.json','detail-knob-0041-round2.json','settings-0041-round2*.json']:
 fs.extend((rev/'rehost').glob(pat))
fs.append(rev/'analysis/0041-20261013/0041-ghidra-pass3.txt');look=[]
for p in sorted(set(fs)):
 s=p.read_text(encoding='utf-8-sig').lower();look.append(dict(path=str(p.relative_to(MAIN)),hits=[a for a in need if a in s]))
zh=[]
with zipfile.ZipFile(rev/'rehost/ap01-ui-0041-complete-source.zip') as z:
 for n in z.namelist():
  try:s=z.read(n).decode('utf-8').lower()
  except UnicodeDecodeError:continue
  zh.append(dict(member=n,hits=[a for a in need if a in s]))
reuse=dict(seeds=need,files=look,zip_text_members=zh,recent_inheritance=['G05','G06','C03/C04','C05/C06','F03/F04','factory-test retained initializer ev_dc0e38b0f382799ea2a8e8ad7f21cefc5998b0767ecf38a58cfdebe8add167c3'],meaning='No hit is bounded textual absence, not proof of no previous analysis; old initializer contains actual caller, notifier and close registration.')
(OUT/'reuse-crosscheck.json').write_text(json.dumps(reuse,ensure_ascii=False,indent=2),encoding='utf-8')
(OUT/'evidence.json').write_text(json.dumps(dict(mapping='VA - 0x9ffff000',old_conclusion_rechecks=old,windows=windows,checks=checks,scope='static ordinary RV32/RVC windows; no backend execution or whole function export'),ensure_ascii=False,indent=2),encoding='utf-8')
print('PASS',len(windows),'new dependency/identity windows',sum(len(x['rows']) for x in windows),'instructions',sum(int(w['end'],16)-int(w['start'],16) for w in windows),'bytes',len(checks),'checks;',len(old),'old conclusion rechecks;',len(look),'old files,',len(zh),'ZIP text members')
