"""G14 independent sparse encoding review. Reads ROM, never executes it."""
from pathlib import Path
import json

OUT = Path(__file__).resolve().parent
ROOT = OUT.parents[2]
MAIN = Path('D:/Documents/PlatformIO/Projects/cuktech-ap01-firmware')
ROM = (MAIN/'roms/0041/ap01-1.0.2_0041.bin').read_bytes()
BASE = 0x9ffff000
checks = []
def w(a,n=4): return int.from_bytes(ROM[a-BASE:a-BASE+n],'little')
def sx(v,n): return v-(1<<n) if v&(1<<(n-1)) else v
def eq(label,got,want):
    assert got==want,(label,got,want)
    checks.append(label)
def I(a,op,rd,rs,imm,f3=0):
    x=w(a); eq(hex(a)+' I',(x&127,x>>7&31,x>>15&31,sx(x>>20,12),x>>12&7),(op,rd,rs,imm,f3))
def C(a,store,reg,base,off):
    x=w(a,2); eq(hex(a)+' Cmem',(x&3,x>>13,(x>>2&7)+8,(x>>7&7)+8,(x>>10&7)*8+(x>>6&1)*4+(x>>5&1)*64),(0,6 if store else 2,reg,base,off))
def S(a,rs,reg,off,f3=2):
    x=w(a); eq(hex(a)+' S',(x&127,x>>15&31,x>>20&31,sx((x>>25<<5)|(x>>7&31),12),x>>12&7),(35,rs,reg,off,f3))
def V(a,f3,top,rd,rs,index,shift):
    x=w(a); eq(hex(a)+' vendor',(x&127,x>>12&7,x>>27,x>>7&31,x>>15&31,x>>20&31,x>>25&3),(11,f3,top,rd,rs,index,shift))
def M(a,rd,rs):
    x=w(a,2); eq(hex(a)+' mv',(x&3,x>>12,x>>7&31,x>>2&31),(2,8,rd,rs))
def J(a,t):
    x=w(a); d=sx((x>>31<<20)|(x>>12&255)<<12|(x>>20&1)<<11|(x>>21&1023)<<1,21)
    eq(hex(a)+' jal',(x&127,x>>7&31,a+d),(111,1,t))

old=json.loads((ROOT/'reverse/analysis/display-device-poll-g13-0041-20261024/evidence.json').read_text())
rows=0
for block in old['windows']:
    for r in block['rows']:
        a=int(r['pc'],16); b=bytes.fromhex(r['raw'])
        assert ROM[a-BASE:a-BASE+len(b)]==b
        rows+=1
eq('ops+20',w(0xa01c1388),0xa0132116)
eq('fb format',ROM[0xa01c0bc4-BASE:0xa01c0bce-BASE],b'/dev/fb%d\0')
eq('plane count1 compare constant',w(0xa0056a14,2),0x4785)
eq('format arg0',w(0xa0056a1e,2),0x4681)
I(0xa0056a20,19,12,12,-0x43c)
I(0xa0056a34,19,11,11,0x368)
M(0xa0056a32,12,19)
M(0xa01b5a20,9,11); S(0xa01b5a22,8,12,-0x24)
C(0xa01b5a4a,True,9,14,0x10); C(0xa01b5a4c,True,12,14,0x18)
C(0xa003e388,False,11,14,0x10); I(0xa003e38c,3,16,11,0x20,2)
eq('dispatch indirect a6',w(0xa003e398,2),0x9802)
C(0xa0132122,False,15,10,12); C(0xa0132124,False,13,15,0x18); C(0xa0132126,False,15,10,0x10)
C(0xa013214e,False,14,15,8); C(0xa0132152,False,12,15,12)
I(0xa013216c,19,9,14,2)
V(0xa0132170,1,0,14,15,14,2); C(0xa0132174,True,11,14,8)
V(0xa0132176,1,0,9,15,9,2); C(0xa013217a,True,9,11,0x14)
J(0xa0132180,0xa01320e0); J(0xa0132184,0xa0059678)
eq('nonzero condition',w(0xa0132188,2),0xe119)
eq('mask4/count1',[w(a,2) for a in (0xa013218e,0xa0132190)],[0x4611,0x4585])
M(0xa0132192,10,9); J(0xa0132194,0xa003e2a0)
C(0xa013219a,False,15,11,0x14); S(0xa013219e,15,0,0); S(0xa01321a2,11,0,0x14)
V(0xa003e2cc,4,8,10,18,9,2)
C(0xa003e2d2,False,14,10,4); C(0xa003e2d4,False,13,10,8)
I(0xa003e2d6,19,15,14,0x18,6); I(0xa003e2de,19,13,15,0x18,7)
eq('and/or/reload condition',[w(a,2) for a in (0xa003e2da,0xa003e2dc,0xa003e2ec)],[0x8ff1,0x8fd5,0x8f5d])
C(0xa003e2e4,True,15,10,8); C(0xa003e2e6,False,15,10,8)
eq('s3=0x10000',w(0xa003e2b4,2),0x69c1)
eq('requested AND s3',w(0xa003e2e8),0x01377733)
C(0xa003e2f0,False,15,10,0x10); eq('callback a5 with same a0',w(0xa003e2fc,2),0x9782)
eq('clear bit4 and jump back',[w(a,2) for a in (0xa003e31e,0xa003e320)],[0x9bed,0xb7d1])
# P=node+14, so P+8=node+1c; installed callback/arg are inherited G11/G12.
eq('P offset aliases',(0x14+8,0x14+12,0x14+16,0x14+20),(0x1c,0x20,0x24,0x28))
model=(MAIN/'evidence/rea-0041-20261017/ghidra/Ghidra/Processors/RISCV/data/languages/ap01thead2.sinc').read_text()
eq('existing addsl rule','rd = rs1 + (rs2 << thshift);' in model,True)
p=model.index(':th.lrw '); rule=model[p:model.index('\n}',p)+2]
eq('existing lrw rule 32bit load','local value:4 = *[ram]:4 ea;' in rule and 'rd = value;' in rule and 'thbase = updated;' not in rule,True)
result={'status':'PASS','baseline':'72c84b7','g13_retained_rows_matched':rows,'checks':checks,'new_functionality':0,'new_sparse_raw':[{'pc':hex(a),'raw':ROM[a-BASE:z-BASE].hex()} for a,z in [(0xa003e2b4,0xa003e2b6),(0xa003e31e,0xa003e322)]],'limits':['Static conditional registration and callback chain only','No observed open inode identity, asynchronous hardware event or actual mask4','No target, firmware, SIM, build, replay, device, network or model changes']}
(OUT/'review-result.json').write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
print('PASS',rows,'retained rows;',len(checks),'independent checks; new functionality 0')
