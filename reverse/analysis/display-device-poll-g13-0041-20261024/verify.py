"""Bounded static framebuffer poll connection; never runs the target."""
from pathlib import Path
import json, sys
sys.dont_write_bytecode = True
OUT = Path(__file__).resolve().parent
ROOT = OUT.parents[2]
MAIN = Path('D:/Documents/PlatformIO/Projects/cuktech-ap01-firmware')
sys.path.insert(0, str(ROOT/'reverse/analysis/display-event-flow-g05-0041-20261023'))
import read_rom as rr
checks=[]
def eq(label,actual,expected):
    assert actual==expected,(label,actual,expected)
    checks.append(label)
def word(a): return int.from_bytes(rr.rom[a-rr.BASE:a-rr.BASE+4],'little')
def raw(a,h): eq(hex(a),rr.rom[a-rr.BASE:a-rr.BASE+len(bytes.fromhex(h))].hex(),h)
def call(a,t): eq(hex(a)+' call',next(rr.rows(a,a+4))['target'],hex(t))
def vendor(a, f3, top, rd, base, index, shift):
    x=word(a)
    eq(hex(a)+' vendor',(x&127,x>>12&7,x>>27,x>>7&31,x>>15&31,x>>20&31,x>>25&3),(11,f3,top,rd,base,index,shift))
eq('fb ops poll slot',word(0xa01c1368+0x20),0xa0132116)
eq('path format',rr.rom[0xa01c0bc4-rr.BASE:0xa01c0bcd-rr.BASE],b'/dev/fb%d')
raw(0xa0056a1e,'8146'); raw(0xa0056a20,'130646bc')
raw(0xa0056a2e,'b7151ca0'); raw(0xa0056a34,'93858536')
call(0xa0056a3c,0xa01b5a12)
raw(0xa01b5a4a,'04cb'); raw(0xa01b5a4c,'10cf'); raw(0xa01b5a54,'2317f700')
raw(0xa003e388,'0c4b'); raw(0xa003e38c,'03a80502'); raw(0xa003e398,'0298')
raw(0xa0132122,'5c45'); raw(0xa0132124,'944f'); raw(0xa0132126,'1c49')
vendor(0xa0132170,1,0,14,15,14,2)
vendor(0xa0132176,1,0,9,15,9,2)
raw(0xa0132174,'0cc7'); raw(0xa013217a,'c4c9')
call(0xa0132180,0xa01320e0); call(0xa0132184,0xa0059678)
raw(0xa013218e,'1146'); raw(0xa0132190,'8545'); raw(0xa0132192,'2685')
call(0xa0132194,0xa003e2a0)
vendor(0xa003e2cc,4,8,10,18,9,2)
raw(0xa003e2e4,'1cc5'); raw(0xa003e2f0,'1c49'); raw(0xa003e2fc,'8297')
raw(0xa013219e,'23a00700'); raw(0xa01321a2,'23aa0500')
model=(MAIN/'evidence/rea-0041-20261017/ghidra/Ghidra/Processors/RISCV/data/languages/ap01thead2.sinc').read_text()
eq('addsl semantic','rd = rs1 + (rs2 << thshift);' in model,True)
spans=[('fb0_registration',0xa0056a14,0xa0056a48),('inode_ops_install',0xa01b5a3e,0xa01b5a58),('poll_ops_call',0xa003e388,0xa003e39a),('fb_poll_identity',0xa0132122,0xa0132130),('fb_poll_slots_and_notify',0xa0132146,0xa01321a8),('notify_field_write_and_callback',0xa003e2cc,0xa003e310)]
idx=json.loads((ROOT/'reverse/analysis/whole-rom-coverage-0041-20261023-round1.json').read_text())
selected=['0xa003e2a0','0xa0055a14','0xa0132116','0xa01b5a12']
inherited=[{'address':f['address'],'extent':f['extent'],'direct_calls':f['direct_calls']} for f in idx['functions'] if f['address'] in selected]
later=json.loads((MAIN/'evidence/rea-0041-20261017/round3/evidence/whole-rom-round3-initial.evidence.json').read_text())['records']
reuse={a:[{'operation':r['operation'],'evidence_id':r['evidence_id'],'parameters':r.get('parameters')} for r in later if a[2:] in json.dumps(r)] for a in selected}
result={'static_only':True,'checks':checks,'windows':[{'name':n,'start':hex(a),'end_exclusive':hex(z),'rows':list(rr.rows(a,z))} for n,a,z in spans],'ops_table':{'address':'0xa01c1368','poll_offset':'0x20','poll':hex(word(0xa01c1388))},'existing_index':inherited,'later_round3_exact_reuse':reuse,'limitations':['Conditional normal fb0 registration/open identity; no runtime fd/inode observation.','No async hardware producer, IRQ or all-VFS search; only selected device poll immediate readiness branch.','No firmware, SIM, build, replay, device, network, shared REA target or source/model modification.']}
(OUT/'evidence.json').write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n')
print(json.dumps({'status':'passed','checks':len(checks),'window_bytes':sum(z-a for _,a,z in spans)}))
