"""G11 bounded ROM field verification. Does not execute firmware or use REA state."""
from pathlib import Path
import json, sys

OUT = Path(__file__).resolve().parent
ROOT = OUT.parents[2]
MAIN = Path('D:/Documents/PlatformIO/Projects/cuktech-ap01-firmware')
sys.dont_write_bytecode = True
sys.path.insert(0, str(ROOT/'reverse/analysis/display-event-flow-g05-0041-20261023'))
import read_rom as rr

checks = []
def eq(label, actual, expected):
    assert actual == expected, (label, actual, expected)
    checks.append(label)
def w(a, n=4): return int.from_bytes(rr.rom[a-rr.BASE:a-rr.BASE+n], 'little')
def I(a, op, rd, rs1, imm, f3=0):
    x=w(a); eq(hex(a)+' I', (x&127,x>>7&31,x>>15&31,rr.sx(x>>20,12),x>>12&7),(op,rd,rs1,imm,f3))
def S(a, base, reg, imm, f3=2):
    x=w(a); eq(hex(a)+' S',(x&127,x>>15&31,x>>20&31,rr.sx((x>>25<<5)|(x>>7&31),12),x>>12&7),(35,base,reg,imm,f3))
def CM(a, store, reg, base, off):
    x=w(a,2); eq(hex(a)+' CM',(x&3,x>>13,(x>>2&7)+8,(x>>7&7)+8,(x>>10&7)*8+(x>>6&1)*4+(x>>5&1)*64),(0,6 if store else 2,reg,base,off))
def MV(a,rd,rs):
    x=w(a,2); eq(hex(a)+' MV',(x&3,x>>12,x>>7&31,x>>2&31),(2,8,rd,rs))
def B(a,f3,rs1,rs2,target):
    x=w(a); off=rr.sx((x>>31<<12)|(x>>7&1)<<11|(x>>25&63)<<5|(x>>8&15)<<1,13)
    eq(hex(a)+' B',(x&127,x>>12&7,x>>15&31,x>>20&31,a+off),(99,f3,rs1,rs2,target))
def call(a,target): eq(hex(a)+' call', next(rr.rows(a,a+4))['target'],hex(target))

# Same older initializer, not a new export. Original raw remains in retained file.
old=json.loads((ROOT/'reverse/analysis/factory-test-0041-20261023/retained-initializer.json').read_text())['function']
raw=old['raw_ranges'][0]; ob=int(raw['start'],16); data=bytes.fromhex(raw['hex'])
old_spans=[(0xa005c08c,0xa005c098),(0xa005c0da,0xa005c0e8),(0xa005c202,0xa005c27c),(0xa005c2c4,0xa005c2ee),(0xa005c334,0xa005c344)]
for a,z in old_spans: eq(hex(a)+' retained bytes',rr.rom[a-rr.BASE:z-rr.BASE],data[a-ob:z-ob])

# Producer parameter persistence, list/sentinel and returned count.
MV(0xa010d7fc,18,10); MV(0xa010d800,22,11); MV(0xa010d802,24,12)
I(0xa010d808,3,9,18,0x28,2); I(0xa010d80e,19,25,18,0x24)
B(0xa010d822,1,9,25,0xa010d84c); MV(0xa010d844,10,19)
I(0xa010d84c,3,15,9,0x10,4)
CM(0xa010d852,False,10,9,0x14); I(0xa010d856,19,11,9,0x14); call(0xa010d85a,0xa003e674)
CM(0xa010d85e,False,14,9,4); CM(0xa010d860,False,15,9,0)
CM(0xa010d862,True,15,14,0); CM(0xa010d866,True,14,15,4)
CM(0xa010d868,False,15,9,0x1c); B(0xa010d874,5,19,24,0xa010d8b4)
CM(0xa010d878,False,15,9,0xc); CM(0xa010d87a,False,14,9,8)
I(0xa010d87c,19,13,19,4,1)
CM(0xa010d884,True,14,12,8); CM(0xa010d886,True,15,12,0xc)
CM(0xa010d888,False,15,9,0x1c)
x=w(0xa010d88c)
vendor=(x&127,x>>12&7,x>>27,x>>7&31,x>>15&31,x>>20&31,x>>25&3)
eq('d88c th.srw fields',vendor,(11,5,8,15,22,13,0))
model=(MAIN/'evidence/rea-0041-20261017/ghidra/Ghidra/Processors/RISCV/data/languages/ap01thead2.sinc').read_text()
p=model.index(':th.srw '); rule=model[p:model.index('\n}',p)+2]
assert 'local delta:4 = rs2 << thshift;' in rule and '*[ram]:4 ea = rd:4;' in rule
CM(0xa010d890,False,15,9,0x18)
I(0xa010d898,3,15,18,0x34,2); I(0xa010d8b4,3,15,18,0x2c,2)

# One actual fallback ADD route; no io_uring arm is reconstructed here.
MV(0xa009e104,20,14); MV(0xa009e108,18,15)
CM(0xa009e106,False,14,11,0x3c)
MV(0xa009e10c,21,10); MV(0xa009e10e,22,13)
B(0xa009e110,1,14,15,0xa009e168); call(0xa009e11a,0xa010e722)
MV(0xa010e73a,18,11); MV(0xa010e740,20,12); MV(0xa010e742,22,13)
call(0xa010e744,0xa010e6cc)
I(0xa010e7d4,3,14,22,8,2); I(0xa010e7d8,3,15,22,12,2)
CM(0xa010e7e0,True,14,10,8); CM(0xa010e7e2,True,15,10,12)
S(0xa010e7ea,10,20,0x14); CM(0xa010e7f0,True,15,10,0x18)
CM(0xa010e7fa,True,10,10,0x20); CM(0xa010e7fc,True,15,10,0x24)
S(0xa010e7fe,10,0,0x1c); call(0xa010e80c,0xa003e674)
B(0xa010e812,5,10,0,0xa010e87c)
CM(0xa010e87c,False,15,9,0x24); S(0xa010e88c,9,18,0x24)
CM(0xa0109b8e,False,15,10,12); S(0xa0109b92,15,14,0x10,0)

# Retained exact searches in later round3: only record identities, not payload copies.
bundle=MAIN/'evidence/rea-0041-20261017/round3/evidence/whole-rom-round3-initial.evidence.json'
records=json.loads(bundle.read_text())['records']
reuse=[]
for needle in ['a010d7da','a010e722','a009e0e6']:
    hits=[{'operation':r['operation'],'evidence_id':r['evidence_id'],'parameters':r.get('parameters')} for r in records if needle in json.dumps(r)]
    reuse.append({'needle':needle,'hits':hits})

# Newly needed windows only; do not duplicate initializer or full producer prologue.
spans=[('producer_inputs_count',0xa010d7f8,0xa010d82c),('producer_output_and_requeue',0xa010d84c,0xa010d8ca),('fallback_submit',0xa009e104,0xa009e11e),('add_node_setup',0xa010e7cc,0xa010e816),('add_success_link',0xa010e87c,0xa010e892),('notification_flag',0xa0109b8e,0xa0109b98),('rearm_setup',0xa010d792,0xa010d7aa)]
windows=[{'name':n,'start':hex(a),'end_exclusive':hex(z),'rows':list(rr.rows(a,z))} for n,a,z in spans]
result={'static_only':True,'checks':checks,'old_rechecks':[{'start':hex(a),'end_exclusive':hex(z),'evidence_id':old['evidence_id']} for a,z in old_spans],'new_windows':windows,'vendor_srw_fields':vendor,'later_round3_reuse':reuse,'limitations':['No target execution, shared REA target, driver timing, exact source version or actual ready observation.','Only fallback ADD and necessary rearm; other backend branch and full MOD/DELETE are outside scope.']}
(OUT/'evidence.json').write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n')
print(json.dumps({'checks':len(checks),'new_window_bytes':sum(z-a for _,a,z in spans),'retained_recheck_bytes':sum(z-a for a,z in old_spans),'status':'passed'}))
