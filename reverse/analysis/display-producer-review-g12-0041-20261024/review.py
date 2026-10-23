"""Independent G12 sparse static checks; never executes the target."""
from pathlib import Path
import json

ROOT = Path(__file__).resolve().parents[3]
OUT = Path(__file__).resolve().parent
MAIN = Path('D:/Documents/PlatformIO/Projects/cuktech-ap01-firmware')
ROM = (MAIN/'roms/0041/ap01-1.0.2_0041.bin').read_bytes()
BASE = 0x9ffff000
prior = json.loads((ROOT/'reverse/analysis/display-ready-producer-g11-0041-20261024/evidence.json').read_text())
old = json.loads((ROOT/'reverse/analysis/factory-test-0041-20261023/retained-initializer.json').read_text())['function']
checks = []

def w(a,n=4): return int.from_bytes(ROM[a-BASE:a-BASE+n], 'little')
def sx(v,n): return v-(1<<n) if v & (1<<(n-1)) else v
def eq(label,got,want):
    assert got == want, (label,got,want)
    checks.append(label)
def I(a,op,rd,rs1,imm,f3=0):
    x=w(a); eq(hex(a)+' I',(x&127,x>>7&31,x>>15&31,sx(x>>20,12),x>>12&7),(op,rd,rs1,imm,f3))
def S(a,base,reg,off,f3=2):
    x=w(a); eq(hex(a)+' S',(x&127,x>>15&31,x>>20&31,sx((x>>25<<5)|(x>>7&31),12),x>>12&7),(35,base,reg,off,f3))
def C(a,store,reg,base,off):
    x=w(a,2); eq(hex(a)+' Cmem',(x&3,x>>13,(x>>2&7)+8,(x>>7&7)+8,(x>>10&7)*8+(x>>6&1)*4+(x>>5&1)*64),(0,6 if store else 2,reg,base,off))
def M(a,rd,rs):
    x=w(a,2); eq(hex(a)+' Cmv',(x&3,x>>12,x>>7&31,x>>2&31),(2,8,rd,rs))
def B(a,f3,r1,r2,target):
    x=w(a); d=sx((x>>31<<12)|(x>>7&1)<<11|(x>>25&63)<<5|(x>>8&15)<<1,13)
    eq(hex(a)+' B',(x&127,x>>12&7,x>>15&31,x>>20&31,a+d),(99,f3,r1,r2,target))
def J(a,target):
    x=w(a); d=sx((x>>31<<20)|(x>>12&255)<<12|(x>>20&1)<<11|(x>>21&1023)<<1,21)
    eq(hex(a)+' J',(x&127,x>>7&31,a+d),(111,1,target))

# Compare retained rows in place; no second instruction/raw export.
rows=0
for block in prior['new_windows']:
    for r in block['rows']:
        a=int(r['pc'],16); raw=bytes.fromhex(r['raw'])
        assert ROM[a-BASE:a-BASE+len(raw)] == raw
        rows+=1
raw=old['raw_ranges'][0]; start=int(raw['start'],16); retained=bytes.fromhex(raw['hex'])
spans=[(0xa005c0da,0xa005c0f0),(0xa005c220,0xa005c25c),(0xa005c2c4,0xa005c2ee),(0xa005c334,0xa005c34e)]
for a,z in spans:
    eq(hex(a)+' retained bytes',ROM[a-BASE:z-BASE],retained[a-start:z-start])

# Actual caller data, same backend descriptor and object, output arguments.
I(0xa005c0e0,19,10,8,-0xd0); J(0xa005c0ec,0xa0024906)
S(0xa005c22c,8,12,-0xd0); S(0xa005c248,27,12,0x14)
S(0xa005c254,8,14,-0xc8); J(0xa005c258,0xa009e0e6)
I(0xa005c244,3,10,8,-0x11c,2); I(0xa005c2c4,3,10,8,-0x11c,2)
J(0xa005c2d0,0xa010e6cc); S(0xa005c2d4,8,10,-0x128)
I(0xa005c2e4,3,10,8,-0x128,2); J(0xa005c2e8,0xa010d738)
I(0xa005c334,3,10,8,-0x128,2); I(0xa005c33a,19,11,8,-0xc0)
eq('caller capacity8',w(0xa005c338,2),0x4621); J(0xa005c33e,0xa010d7da)

# Fallback and installation node aliases, including callback constant.
C(0xa009e106,False,14,11,0x3c); eq('fallback minus1',w(0xa009e10a,2),0x57fd)
B(0xa009e110,1,14,15,0xa009e168)
M(0xa009e114,13,18); M(0xa009e116,12,20); M(0xa009e118,11,22); J(0xa009e11a,0xa010e722)
M(0xa010e73a,18,11); M(0xa010e740,20,12); M(0xa010e742,22,13)
M(0xa010e750,9,10); B(0xa010e76e,1,18,15,0xa010e82a)
I(0xa010e792,19,23,9,0x3c); M(0xa010e7cc,10,23); J(0xa010e7ce,0xa010d70e)
C(0xa010e7d2,True,9,10,0x2c); S(0xa010e7dc,10,0,0x10,0)
I(0xa010e7d4,3,14,22,8,2); I(0xa010e7d8,3,15,22,12,2)
C(0xa010e7e0,True,14,10,8); C(0xa010e7e2,True,15,10,12)
I(0xa010e7e4,3,15,22,0,2); eq('events OR 0x10000',[w(a,2) for a in (0xa010e7e8,0xa010e7ee)],[0x6741,0x8fd9])
S(0xa010e7ea,10,20,0x14); C(0xa010e7f0,True,15,10,0x18)
eq('callback LUI',w(0xa010e7f2),0xa010a7b7); I(0xa010e7f6,19,15,15,-0x472)
C(0xa010e7fa,True,10,10,0x20); C(0xa010e7fc,True,15,10,0x24); S(0xa010e7fe,10,0,0x1c)
I(0xa010e802,19,11,10,0x14); M(0xa010e806,18,10); J(0xa010e80c,0xa003e674)
B(0xa010e812,5,10,0,0xa010e87c); S(0xa010e88c,9,18,0x24)
C(0xa0109b8e,False,15,10,0xc); eq('notify value1',w(0xa0109b90,2),0x4705); S(0xa0109b92,15,14,0x10,0)

# Collector parameter/count, signed bound, data-before-revents reread.
M(0xa010d7fc,18,10); M(0xa010d800,22,11); M(0xa010d802,24,12)
eq('count starts0',w(0xa010d80c,2),0x4981); M(0xa010d844,10,19)
C(0xa010d868,False,15,9,0x1c)
S(0xa010d86a,9,0,4); S(0xa010d86e,9,0,0)
eq('first revents zero test after links clear',w(0xa010d872,2),0xc3a9)
B(0xa010d874,5,19,24,0xa010d8b4)
C(0xa010d878,False,15,9,0xc); C(0xa010d87a,False,14,9,8)
I(0xa010d87c,19,13,19,4,1); eq('slot base ADD',w(0xa010d880),0x00db0633)
C(0xa010d884,True,14,12,8); C(0xa010d886,True,15,12,12)
C(0xa010d888,False,15,9,0x1c); eq('count increment',w(0xa010d88a,2),0x0985)
x=w(0xa010d88c)
eq('THead srw fields',(x&127,x>>12&7,x>>27,x>>7&31,x>>15&31,x>>20&31,x>>25&3),(11,5,8,15,22,13,0))
model=(MAIN/'evidence/rea-0041-20261017/ghidra/Ghidra/Processors/RISCV/data/languages/ap01thead2.sinc').read_text()
p=model.index(':th.srw '); rule=model[p:model.index('\n}',p)+2]
assert 'local delta:4 = rs2 << thshift;' in rule and '*[ram]:4 ea = rd:4;' in rule and 'thbase = updated' not in rule
checks.append('existing read-only srw rule: 32bit indexed store, no writeback')
I(0xa010d898,3,15,18,0x34,2); S(0xa010d89c,9,27,4); S(0xa010d8a8,18,9,0x34)
I(0xa010d8b4,3,15,18,0x2c,2); S(0xa010d8b8,9,23,4)
C(0xa010d8bc,True,15,9,0); C(0xa010d8c2,True,9,15,4); S(0xa010d8c4,18,9,0x2c)
M(0xa010d8ac,9,20); I(0xa010d8ae,3,20,20,4,2)
eq('requeue continues loop',w(0xa010d8c8,2),0xb7d5)

# Same rearm list; clear first, call, branch before unlink/relink.
I(0xa010d760,3,9,18,0x30,2); I(0xa010d764,19,22,18,0x2c)
I(0xa010d768,19,23,18,0x24); S(0xa010d794,9,0,0x10,0); S(0xa010d798,9,0,0x1c)
I(0xa010d79e,19,11,9,0x14); J(0xa010d7a2,0xa003e674); B(0xa010d7a8,4,10,0,0xa010d774)
I(0xa010d7be,3,15,18,0x24,2); S(0xa010d7c2,9,23,4); S(0xa010d7ce,18,9,0x24)

result={'status':'PASS','baseline':'f312a1a','new_functionality':0,'g11_rows_matched':rows,'retained_bytes_matched':sum(z-a for a,z in spans),'checks':checks,'evidence_id':old['evidence_id'],'limits':['No shared REA target or database','No firmware, simulation, build, replay, device or network execution','No device revents writer or actual ready proof','Fallback first ADD only; other backend and full MOD/DELETE inherited unknown']}
(OUT/'review-result.json').write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
print('PASS',rows,'G11 retained rows;',len(checks),'independent checks; new functionality 0')
