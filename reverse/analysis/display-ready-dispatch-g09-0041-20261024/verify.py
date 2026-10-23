"""G09 bounded static checks; no target execution or whole-function export."""
from pathlib import Path
import sys,json,zipfile
OUT=Path(__file__).resolve().parent
ROOT=OUT.parents[2]
MAIN=Path('D:/Documents/PlatformIO/Projects/cuktech-ap01-firmware')
sys.path.insert(0,str(ROOT/'reverse/analysis/display-event-flow-g05-0041-20261023'))
import read_rom as rr
f=json.loads((ROOT/'reverse/analysis/factory-test-0041-20261023/retained-initializer.json').read_text())['function']
rg=f['raw_ranges'][0]; base=int(rg['start'],16); old=bytes.fromhex(rg['hex'])
spans=[('ready_record_output',0xa005c334,0xa005c34a),('record_loop_identity',0xa005c424,0xa005c456),('record_fd',0xa005c4da,0xa005c4ee),('record_stride',0xa005c59e,0xa005c5b4),('ready_dispatch',0xa005c6ea,0xa005c79e)]
rechecks=[];D={}
for n,a,z in spans:
 assert rr.rom[a-rr.BASE:z-rr.BASE]==old[a-base:z-base]
 rows=list(rr.rows(a,z));D.update({int(x['pc'],16):x for x in rows})
 rechecks.append(dict(name=n,start=hex(a),end_exclusive=hex(z),source=f['evidence_id'],status='old conclusion raw-byte recheck; original raw/assembly not duplicated'))
new=[]
for n,a,z in [('register_identity_and_desired_mask',0xa009ecc4,0xa009ecf0),('register_bucket_link',0xa009ed70,0xa009edce),('existing_bucket_node_identity',0xa009ee0a,0xa009ee16)]:
 rows=list(rr.rows(a,z));new.append(dict(name=n,start=hex(a),end_exclusive=hex(z),rows=rows));D.update({int(x['pc'],16):x for x in rows})
checks=[]
def ck(a,s):
 assert D[a]['asm']==s,(hex(a),D[a]['asm'],s)
 checks.append(dict(pc=hex(a),asm=s))
for a,s in {0xa009ecc4:'c.lw s1, 0x24(a1)',0xa009ecc6:'c.mv s2, a1',0xa009ece8:'c.lw a5, 0x1c(a1)',0xa009ecea:'c.mv s3, a0',0xa009ecec:'c.or a5, a2',0xa009ecee:'c.sw a5, 0x1c(a1)',0xa009ee0a:'addi a3, a4, -0x14',0xa009ee12:'c.lw a4, 0(a4)',0xa009ed70:'lw a4, 0x20(s2)',0xa009ed74:'lw a5, 0x1c(s2)',0xa009ed9e:'lw a3, 0x24(s2)',0xa009eda2:'lw a4, 0x34(s3)',0xa009edb2:'sw a5, 0x14(s2)',0xa009edb8:'addi a4, s2, 0x14',0xa009edbc:'sw a3, 0x18(s2)',0xa009edc0:'c.sw a4, 0(a3)',0xa009edc2:'c.sw a4, 4(a5)',0xa005c338:'c.li a2, 8',0xa005c33a:'addi a1, s0, -0xc0',0xa005c42c:'addi a5, s0, -0xc0',0xa005c430:'sw a5, -0x12c(s0)',0xa005c4de:'c.lw a4, 8(a5)',0xa005c5ac:'c.addi a5, 0x10',0xa005c704:'c.lw a5, 0x34(s1)',0xa005c72a:'c.lw a4, 0(a5)',0xa005c730:'c.lw a1, 0(a3)',0xa005c732:'c.lw a3, 8(a5)',0xa005c734:'ori a2, a3, 0x18',0xa005c738:'c.and a2, a1',0xa005c73a:'addi a1, a2, -8',0xa005c73e:'c.andi a1, -9',0xa005c742:'c.andi a3, 0x17',0xa005c74c:'addi a1, a5, -0x14',0xa005c77a:'lw a5, -0x14(a5)',0xa005c77e:'c.mv a0, s1',0xa005c780:'c.jalr a5'}.items():ck(a,s)
assert D[0xa005c33e]['target']=='0xa010d7da'
checks.append(dict(pc='0xa005c33e',target='0xa010d7da'))
vendor=[]
for a,want in [(0xa009eda6,[1,0,15,14,13,3]),(0xa009edaa,[4,8,14,14,13,3]),(0xa005c706,[1,0,16,15,14,3]),(0xa005c70a,[4,8,15,15,14,3])]:
 w=int.from_bytes(rr.rom[a-rr.BASE:a-rr.BASE+4],'little')
 got=[(w>>12)&7,w>>27,(w>>7)&31,(w>>15)&31,(w>>20)&31,(w>>25)&3];assert got==want,(hex(a),got,want)
 vendor.append(dict(pc=hex(a),raw=w.to_bytes(4,'little').hex(),fields=got,semantics='base+(index<<3)' if got[0]==1 else 'u32 load at base+(index<<3)'))
model=MAIN/'evidence/rea-0041-20261017/ghidra/Ghidra/Processors/RISCV/data/languages/ap01thead2.sinc'
s=model.read_text();rules=[]
for key in [':th.addsl ',':th.lrw ']:
 i=s.index(key);rules.append(s[i:s.index('\n}',i)+2])
# Only classify old artifacts relevant to this exact dispatch question.
paths=[MAIN/'reverse/reports/ap01'/n for n in ['application-rehost-complete-0041-20261017.md','application-function-matrix-0041.json','factory-reference-map-0041-20261020.md']]
for pattern in ['*-complete-0041.json','*round3*.json','page-logic*.json']:
 paths.extend((MAIN/'reverse/rehost').glob(pattern))
paths.append(MAIN/'reverse/analysis/0041-20261013/0041-ghidra-pass3.txt')
seeds=['a009ec98','a009f8ea','a005c704','a005c780','a010d7da'];reuse=[]
for p in sorted(set(paths)):
 t=p.read_text(encoding='utf-8-sig').lower();reuse.append(dict(path=str(p.relative_to(MAIN)),hits=[v for v in seeds if v in t]))
zipped=[]
with zipfile.ZipFile(MAIN/'reverse/rehost/ap01-ui-0041-complete-source.zip') as z:
 for n in z.namelist():
  try:t=z.read(n).decode('utf-8').lower()
  except UnicodeDecodeError:continue
  zipped.append(dict(member=n,hits=[v for v in seeds if v in t]))
result=dict(status='PASS',baseline='bccdd65',scope='conditional backend-record-to-existing-display-watcher connection; no actual-ready or source-version proof',old_rechecks=rechecks,new_windows=new,asm_checks=checks,vendor_checks=vendor,model_path=str(model),model_rules=rules,reuse=dict(files=reuse,zip_members=zipped,note='bounded textual absence is not previous-analysis absence; retained initializer includes full ready consumer'),counts=dict(old_recheck_bytes=sum(z-a for _,a,z in spans),new_window_bytes=150,asm_checks=len(checks),vendor_checks=len(vendor)))
(OUT/'evidence.json').write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
print(json.dumps(result['counts']), 'PASS')
