"""G15 bounded static file lifecycle checks; does not execute firmware."""
from pathlib import Path
import json, sys
sys.dont_write_bytecode = True
OUT = Path(__file__).resolve().parent
ROOT = OUT.parents[2]
MAIN = Path('D:/Documents/PlatformIO/Projects/cuktech-ap01-firmware')
sys.path.insert(0, str(ROOT/'reverse/analysis/display-event-flow-g05-0041-20261023'))
import read_rom as rr
checks=[]
def eq(label,a,b):
    assert a==b,(label,a,b)
    checks.append(label)
def raw(a,h): eq(hex(a),rr.rom[a-rr.BASE:a-rr.BASE+len(bytes.fromhex(h))].hex(),h)
def word(a): return int.from_bytes(rr.rom[a-rr.BASE:a-rr.BASE+4],'little')
def call(a,t): eq(hex(a)+' target',next(rr.rows(a,a+4))['target'],hex(t))
eq('ops open',word(0xa01c1368),0xa012fabc)
eq('ops close',word(0xa01c136c),0xa012f3e0)
eq('same ops poll',word(0xa01c1388),0xa0132116)
for a,h in [(0xa003ead8,'83270901'),(0xa003eadc,'9c43'),(0xa003eae0,'5285'),(0xa003eae2,'8297'),(0xa0027d16,'83a70a01'),(0xa0027d1c,'dc43'),(0xa0027d20,'2685'),(0xa0027d22,'8297'),(0xa012face,'5c45'),(0xa012fad0,'03a98701'),(0xa012faf0,'aa8a'),(0xa012faf2,'4145'),(0xa012fafa,'d159'),(0xa012fafc,'15c5'),(0xa012fb04,'8327c900'),(0xa012fb0a,'03250900'),(0xa012fb0e,'1c45'),(0xa012fb12,'8297'),(0xa012fb16,'63530502'),(0xa012fb3c,'fd57'),(0xa012fb3e,'dcc0'),(0xa012fb40,'8327c900'),(0xa012fb44,'9cc0'),(0xa012fb46,'23269900'),(0xa012fb4a,'23a89a00'),(0xa012f3f0,'03290501'),(0xa012f3f4,'844f'),(0xa012f426,'9c43'),(0xa012f42c,'5c45'),(0xa012f430,'8297'),(0xa012f432,'635b0500'),(0xa012f448,'dc44'),(0xa012f44a,'0147'),(0xa012f44e,'63972701'),(0xa012f452,'83270900'),(0xa012f458,'dcc4'),(0xa012f462,'1cc3'),(0xa012f468,'4a85'),(0xa012f472,'0145'),(0xa0030ec6,'aa85'),(0xa0030ed8,'0326c4fe'),(0xa0030edc,'8145')]: raw(a,h)
for a,t in [(0xa012faf4,0xa0030eb8),(0xa012fb20,0xa002e14e),(0xa012f46a,0xa002e14e),(0xa0030ed0,0xa002ed8e),(0xa0030ede,0xa0024906)]: call(a,t)
spans=[('open_file_abi',0xa003ead8,0xa003eae6),('close_file_abi',0xa0027d16,0xa0027d2a),('open_identity_allocate',0xa012face,0xa012fada),('open_allocate_and_lower',0xa012faf0,0xa012fb28),('open_link_publish',0xa012fb3c,0xa012fb56),('zero_allocate',0xa0030ec2,0xa0030ee2),('close_identity',0xa012f3ee,0xa012f3fe),('close_lower_and_error',0xa012f414,0xa012f43a),('close_unlink_free',0xa012f448,0xa012f47e)]
idx=json.loads((ROOT/'reverse/analysis/whole-rom-coverage-0041-20261023-round1.json').read_text())
selected=['0xa012fabc','0xa012f3e0','0xa0030eb8']
prior=[{k:f[k] for k in ['address','extent','direct_calls','historical_contracts','dossiers']} for f in idx['functions'] if f['address'] in selected]
later=json.loads((MAIN/'evidence/rea-0041-20261017/round3/evidence/whole-rom-round3-initial.evidence.json').read_text())['records']
reuse={a:[{'operation':r['operation'],'evidence_id':r['evidence_id']} for r in later if a[2:] in json.dumps(r)] for a in selected[:2]}
result={'static_only':True,'checks':checks,'ops':{'address':'0xa01c1368','open':hex(word(0xa01c1368)),'close':hex(word(0xa01c136c))},'windows':[{'name':n,'start':hex(a),'end_exclusive':hex(z),'rows':list(rr.rows(a,z))} for n,a,z in spans],'inherited_index':prior,'later_round3_exact_reuse':reuse,'limitations':['Normal register/open identity is conditional, not runtime fd proof.','No generic VFS, heap, lower-device callback or IRQ expansion.','Close body has no direct poll-slot walk or P+14 clearing; indirect lower callback effects remain unknown.','No target execution or new shared REA target.']}
(OUT/'evidence.json').write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n')
print(json.dumps({'status':'passed','checks':len(checks),'window_bytes':sum(z-a for _,a,z in spans)}))
