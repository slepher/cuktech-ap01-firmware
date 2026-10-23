"""G16 independent bounded static review; never executes firmware."""
from pathlib import Path
import json

OUT = Path(__file__).resolve().parent
ROOT = OUT.parents[2]
ROM = Path('D:/Documents/PlatformIO/Projects/cuktech-ap01-firmware/roms/0041/ap01-1.0.2_0041.bin').read_bytes()
BASE = 0x9ffff000
prior = json.loads((ROOT/'reverse/analysis/fb-file-lifecycle-g15-0041-20261024/evidence.json').read_text())
checks = []
def raw(pc, n): return ROM[pc-BASE:pc-BASE+n]
def word(pc, n=4): return int.from_bytes(raw(pc, n), 'little')
def eq(label, got, expected):
    assert got == expected, (label, got, expected)
    checks.append(label)
def sx(v, n): return v-(1<<n) if v & (1<<(n-1)) else v
def lw(pc, rd, base, offset):
    w=word(pc)
    eq(hex(pc)+' lw', (w&127,(w>>12)&7,(w>>7)&31,(w>>15)&31,sx(w>>20,12)), (3,2,rd,base,offset))
def sw(pc, src, base, offset):
    w=word(pc)
    eq(hex(pc)+' sw', (w&127,(w>>12)&7,(w>>20)&31,(w>>15)&31,sx(((w>>25)<<5)|((w>>7)&31),12)), (35,2,src,base,offset))
def cls(pc, store, reg, base, offset):
    w=word(pc,2)
    eq(hex(pc)+' compressed word', (w&3,w>>13,8+((w>>2)&7),8+((w>>7)&7),((w>>10)&7)*8+((w>>6)&1)*4+((w>>5)&1)*64), (0,6 if store else 2,reg,base,offset))
def branch(pc, cond, r1, r2, target):
    w=word(pc)
    imm=((w>>31)<<12)|(((w>>7)&1)<<11)|(((w>>25)&63)<<5)|(((w>>8)&15)<<1)
    eq(hex(pc)+' branch',(w&127,(w>>12)&7,(w>>15)&31,(w>>20)&31,pc+sx(imm,13)),(99,cond,r1,r2,target))
def call(pc, target):
    w=word(pc)
    if w&127==111:
        imm=((w>>31)<<20)|(((w>>12)&255)<<12)|(((w>>20)&1)<<11)|(((w>>21)&1023)<<1)
        got=pc+sx(imm,21)
    else:
        v=word(pc+4)
        eq(hex(pc)+' auipc/jalr ABI',(w&127,(w>>7)&31,v&127,(v>>7)&31,(v>>15)&31),(23,1,103,1,1))
        got=(pc+sx(w&0xfffff000,32)+sx(v>>20,12))&0xffffffff
    eq(hex(pc)+' direct call',got,target)

retained=0
for window in prior['windows']:
    for row in window['rows']:
        eq(row['pc']+' retained raw',raw(int(row['pc'],16),len(bytes.fromhex(row['raw']))).hex(),row['raw'])
        retained+=1
for pc,value in [(0xa01c1368,0xa012fabc),(0xa01c136c,0xa012f3e0),(0xa01c1388,0xa0132116)]: eq(hex(pc)+' ops',word(pc),value)
for args in [(0xa012face,False,15,10,12),(0xa012fb0e,False,15,10,8),(0xa012fb3e,True,15,9,4),(0xa012fb44,True,15,9,0),(0xa012f3ee,False,15,10,12),(0xa012f3f4,False,9,15,24),(0xa012f426,False,15,15,0),(0xa012f42c,False,15,10,12),(0xa012f448,False,15,9,12),(0xa012f458,True,15,9,12),(0xa012f462,True,15,14,0)]: cls(*args)
for args in [(0xa012fad0,18,15,24),(0xa012fb04,15,18,12),(0xa012fb0a,10,18,0),(0xa012fb40,15,18,12),(0xa012f3f0,18,10,16),(0xa012f452,15,18,0),(0xa0030ed8,12,8,-20)]: lw(*args)
sw(0xa012fb46,9,18,12)
sw(0xa012fb4a,9,21,16)
sw(0xa0030ec8,10,8,-20)
branch(0xa012fb16,5,10,0,0xa012fb3c)
branch(0xa012f432,5,10,0,0xa012f448)
branch(0xa012f44e,1,15,18,0xa012f45c)
for args in [(0xa012faf4,0xa0030eb8),(0xa012fb20,0xa002e14e),(0xa012f46a,0xa002e14e),(0xa0030ed0,0xa002ed8e),(0xa0030ede,0xa0024906)]: call(*args)
for pc,h in [(0xa012faf2,'4145'),(0xa012fb3c,'fd57'),(0xa0030edc,'8145'),(0xa012fb1a,'73100a30'),(0xa012fb4e,'73100a30'),(0xa012f436,'73900930'),(0xa012f464,'73900930'),(0xa012f468,'4a85'),(0xa012f472,'0145')]: eq(hex(pc)+' ABI/order anchor',raw(pc,len(bytes.fromhex(h))).hex(),h)
# Sparse omitted return anchors: wrapper restores saved F; open returns saved s3.
extra=[(0xa0030ee6,'2685'),(0xa012fb34,'4e85'),(0xa012f43a,'f2406244d2444249b24905618280')]
for pc,h in extra: eq(hex(pc)+' extra raw',raw(pc,len(bytes.fromhex(h))).hex(),h)
result={'status':'passed','static_only':True,'retained_rows_compared':retained,'checks':checks,'extra_bytes':[{'pc':hex(pc),'raw':h} for pc,h in extra],'extra_byte_count':sum(len(bytes.fromhex(h)) for _,h in extra),'limits':['No executed open/close or fd/inode identity proof.','Lower callback internals and poll teardown to close ordering remain unknown.','Close-body bounded absence is not a system-wide cleanup or defect claim.']}
(OUT/'review-result.json').write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n')
print(json.dumps({k:result[k] for k in ['status','retained_rows_compared','extra_byte_count']} | {'checks':len(checks)}))
