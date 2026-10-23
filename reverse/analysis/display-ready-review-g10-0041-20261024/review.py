"""G10 passive independent field checks; no target or shared REA session."""
from pathlib import Path
import json

ROOT = Path(__file__).resolve().parents[3]
OUT = Path(__file__).resolve().parent
MAIN = Path('D:/Documents/PlatformIO/Projects/cuktech-ap01-firmware')
ROM = (MAIN/'roms/0041/ap01-1.0.2_0041.bin').read_bytes()
BASE = 0x9ffff000
prior = json.loads((ROOT/'reverse/analysis/display-ready-dispatch-g09-0041-20261024/evidence.json').read_text())
old = json.loads((ROOT/'reverse/analysis/factory-test-0041-20261023/retained-initializer.json').read_text())['function']
checks = []
def w(a, n=4): return int.from_bytes(ROM[a-BASE:a-BASE+n], 'little')
def sx(v,n): return v-(1<<n) if v&(1<<(n-1)) else v
def eq(label,got,want):
    assert got == want, (label,got,want)
    checks.append(label)
def I(a,op,rd,rs1,imm,f3=0):
    x=w(a); eq(hex(a)+' I',(x&127,(x>>7)&31,(x>>15)&31,sx(x>>20,12),(x>>12)&7),(op,rd,rs1,imm,f3))
def S(a,rs1,rs2,imm):
    x=w(a); eq(hex(a)+' SW',(x&127,(x>>15)&31,(x>>20)&31,sx(((x>>25)<<5)|((x>>7)&31),12),(x>>12)&7),(35,rs1,rs2,imm,2))
def Cmem(a,store,reg,base,off):
    x=w(a,2)
    eq(hex(a)+' C.LW/SW',(x&3,x>>13,((x>>2)&7)+8,((x>>7)&7)+8,((x>>10)&7)*8+((x>>6)&1)*4+((x>>5)&1)*64),(0,6 if store else 2,reg,base,off))
def MV(a,rd,rs):
    x=w(a,2); eq(hex(a)+' C.MV',(x&3,x>>12,(x>>7)&31,(x>>2)&31),(2,8,rd,rs))
def B(a,f3,rs1,rs2,target):
    x=w(a); off=sx(((x>>31)<<12)|(((x>>7)&1)<<11)|(((x>>25)&63)<<5)|(((x>>8)&15)<<1),13)
    eq(hex(a)+' B',(x&127,(x>>12)&7,(x>>15)&31,(x>>20)&31,a+off),(99,f3,rs1,rs2,target))

# No second raw/assembly export: compare all G09 registration rows in place.
count=0
for block in prior['new_windows']:
    for r in block['rows']:
        a=int(r['pc'],16); b=bytes.fromhex(r['raw'])
        assert ROM[a-BASE:a-BASE+len(b)] == b
        count+=1
raw=old['raw_ranges'][0]; ob=int(raw['start'],16); data=bytes.fromhex(raw['hex'])
spans=[(0xa005c704,0xa005c79e),(0xa005c434,0xa005c44e)]
for a,z in spans:
    assert ROM[a-BASE:z-BASE] == data[a-ob:z-ob]

# Register: same saved watcher and loop, signed fd/desired masks are words.
Cmem(0xa009ecc4,False,9,11,0x24)
MV(0xa009ecc6,18,11); MV(0xa009ecea,19,10)
Cmem(0xa009ece8,False,15,11,0x1c); Cmem(0xa009ecee,True,15,11,0x1c)
I(0xa009ed70,3,14,18,0x20,2); I(0xa009ed74,3,15,18,0x1c,2)
B(0xa009ed78,0,14,15,0xa009edce)
I(0xa009ed9e,3,13,18,0x24,2); I(0xa009eda2,3,14,19,0x34,2)
B(0xa009edae,1,15,14,0xa009ee0a)
S(0xa009edb2,18,15,0x14); Cmem(0xa009edb6,False,13,15,4)
I(0xa009edb8,19,14,18,0x14); S(0xa009edbc,18,13,0x18)
Cmem(0xa009edc0,True,14,13,0); Cmem(0xa009edc2,True,14,15,4)
I(0xa009ee0a,19,13,14,-0x14); B(0xa009ee0e,0,18,13,0xa009edce)
Cmem(0xa009ee12,False,14,14,0)

# Explicit opcode, funct, registers and 2-bit shift, independently from asm text.
vendor=[]
for a,want in [(0xa009eda6,(11,1,0,15,14,13,3)),(0xa009edaa,(11,4,8,14,14,13,3)),(0xa005c706,(11,1,0,16,15,14,3)),(0xa005c70a,(11,4,8,15,15,14,3))]:
    x=w(a); got=(x&127,(x>>12)&7,x>>27,(x>>7)&31,(x>>15)&31,(x>>20)&31,(x>>25)&3)
    eq(hex(a)+' THead',got,want); vendor.append({'pc':hex(a),'fields':got})
model=(MAIN/'evidence/rea-0041-20261017/ghidra/Ghidra/Processors/RISCV/data/languages/ap01thead2.sinc').read_text()
for key,body in [(':th.addsl ','rd = rs1 + (rs2 << thshift);'),(':th.lrw ','local value:4 = *[ram]:4 ea;')]:
    p=model.index(key); rule=model[p:model.index('\n}',p)+2]
    assert body in rule
    if key==':th.lrw ': assert 'thbase = updated' not in rule

# Old consumer: next is captured before mask/special check and call.
Cmem(0xa005c704,False,15,9,0x34)
Cmem(0xa005c72a,False,14,15,0)
Cmem(0xa005c730,False,11,13,0); Cmem(0xa005c732,False,13,15,8)
I(0xa005c734,19,12,13,0x18,6); I(0xa005c73a,19,11,12,-8)
eq('mask compressed AND/ANDI/OR',[w(a,2) for a in (0xa005c738,0xa005c73e,0xa005c742,0xa005c744)],[0x8e6d,0x99dd,0x8add,0x8e55])
I(0xa005c74c,19,11,15,-0x14)
S(0xa005c746,8,12,-0x17c); S(0xa005c750,8,15,-0x170); S(0xa005c758,8,11,-0x16c)
S(0xa005c762,8,14,-0x158); S(0xa005c766,8,16,-0x154)
x=w(0xa005c76a); off=sx(((x>>31)<<20)|(((x>>12)&255)<<12)|(((x>>20)&1)<<11)|(((x>>21)&1023)<<1),21)
eq('callback pre-call target',(x&127,(x>>7)&31,0xa005c76a+off),(111,1,0xa009d382))
I(0xa005c76e,3,15,8,-0x170,2); I(0xa005c772,3,12,8,-0x17c,2)
I(0xa005c776,3,11,8,-0x16c,2); I(0xa005c77a,3,15,15,-0x14,2)
MV(0xa005c77e,10,9)
eq('indirect C.JALR callback',w(0xa005c780,2),0x9782)
I(0xa005c782,3,16,8,-0x154,2); I(0xa005c786,3,14,8,-0x158,2)
MV(0xa005c798,15,14); Cmem(0xa005c79a,False,14,14,0)
I(0xa005c434,19,15,9,0x150); S(0xa005c44a,8,15,-0x178)
I(0xa005c754,3,15,8,-0x178,2); B(0xa005c75c,0,11,15,0xa005c79e)

result={'status':'PASS','classification':'independent review; new ROM functionality 0','baseline':'3ba6b96','registration_rows_matched':count,'old_consumer_bytes_matched':sum(z-a for a,z in spans),'checks':checks,'vendor_fields':vendor,'inherited_evidence':old['evidence_id'],'profile_digest':old['profile']['digest'],'limits':['No new REA active target or shared database','No backend producer or runtime proof','No whole-function export; existing instructions reused']}
(OUT/'review-result.json').write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
print('PASS:',count,'G09 rows;',result['old_consumer_bytes_matched'],'old bytes;',len(checks),'field/ABI checks; new functionality 0')
