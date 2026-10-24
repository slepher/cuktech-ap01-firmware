"""G28: sparse independent RV32/RVC fields for the three normal getter layers."""
from pathlib import Path
import json
MAIN=Path('D:/Documents/PlatformIO/Projects/cuktech-ap01-firmware')
ROM=MAIN/'roms/0041/ap01-1.0.2_0041.bin'
OUT=Path(__file__).resolve().parent
BASE=0x9ffff000
assert ROM.stat().st_size==6769704
checks=[];rows={}
def bits(x,a,n):return (x>>a)&((1<<n)-1)
def sx(x,n):return x-(1<<n) if x&(1<<(n-1)) else x
def w(pc):
    assert (0xa002671a<=pc<0xa002672e or 0xa0026740<=pc<0xa0026744 or
            0xa002676c<=pc<0xa00267aa or 0xa00267c0<=pc<0xa00267e2)
    if pc not in rows:
        with ROM.open('rb') as f:
            f.seek(pc-BASE);r=f.read(2)
            if r[0]&3==3:r+=f.read(2)
        rows[pc]=r
    return int.from_bytes(rows[pc],'little')
def eq(pc,label,got,want):
    assert got==want,(hex(pc),label,got,want)
    checks.append(dict(address=hex(pc),label=label,value=got))
def ci(pc,f3,rd,imm):
    v=w(pc);eq(pc,'compressed immediate',[v&3,v>>13,bits(v,7,5),sx((bits(v,12,1)<<5)|bits(v,2,5),6)],
               [1,f3,rd,imm])
def frame(pc,imm):
    v=w(pc);i=(bits(v,11,2)<<4)|(bits(v,7,4)<<6)|(bits(v,6,1)<<2)|(bits(v,5,1)<<3)
    eq(pc,'frame s0=sp+immediate',[v&3,v>>13,8+bits(v,2,3),i],[0,0,8,imm])
def cstack(pc,reg,off,store=False):
    v=w(pc)
    if store:i=(bits(v,7,2)<<6)|(bits(v,9,4)<<2);r=bits(v,2,5)
    else:i=(bits(v,12,1)<<5)|(bits(v,4,3)<<2)|(bits(v,2,2)<<6);r=bits(v,7,5)
    eq(pc,'stack word store' if store else 'stack word restore',[v&3,v>>13,r,i],[2,6 if store else 2,reg,off])
def cl(pc,reg,base,off,store=False):
    v=w(pc);i=(bits(v,10,3)<<3)|(bits(v,6,1)<<2)|(bits(v,5,1)<<6)
    eq(pc,'compressed word store' if store else 'compressed word load',
       [v&3,v>>13,8+bits(v,2,3),8+bits(v,7,3),i],[0,6 if store else 2,reg,base,off])
def mv(pc,rd,src):
    v=w(pc);eq(pc,'compressed move',[v&3,v>>12,bits(v,7,5),bits(v,2,5)],[2,8,rd,src])
def it(pc,op,rd,f3,base,imm):
    v=w(pc);eq(pc,'I-format',[v&127,bits(v,7,5),bits(v,12,3),bits(v,15,5),sx(v>>20,12)],
               [op,rd,f3,base,imm])
def cb(pc,f3,reg,target):
    v=w(pc);i=(bits(v,12,1)<<8)|(bits(v,10,2)<<3)|(bits(v,5,2)<<6)|(bits(v,3,2)<<1)|(bits(v,2,1)<<5)
    eq(pc,'compressed zero gate',[v&3,v>>13,8+bits(v,7,3),pc+sx(i,9)],[1,f3,reg,target])
def jal(pc,target):
    v=w(pc);i=(bits(v,31,1)<<20)|(bits(v,12,8)<<12)|(bits(v,20,1)<<11)|(bits(v,21,10)<<1)
    eq(pc,'direct call',[v&127,bits(v,7,5),pc+sx(i,21)],[111,1,target])
def ret(pc):eq(pc,'return ra',w(pc),0x8082)
def sp16(pc,imm):
    v=w(pc);i=(bits(v,12,1)<<9)|(bits(v,6,1)<<4)|(bits(v,5,1)<<6)|(bits(v,3,2)<<7)|(bits(v,2,1)<<5)
    eq(pc,'stack restore addi16sp',[v&3,v>>13,bits(v,7,5),sx(i,10)],[1,3,2,imm])

# Complete selected normal routes, excluding diagnostics and pid-nonzero body.
ci(0xa002671a,0,2,-32)
cstack(0xa002671c,8,24,True);cstack(0xa002671e,9,20,True);cstack(0xa0026720,1,28,True)
frame(0xa0026722,32)
v=w(0xa0026724);eq(0xa0026724,'global high LUI',[v&127,bits(v,7,5),v&0xfffff000],[55,15,0x62fc7000])
it(0xa0026728,3,9,2,15,-0x3e8)
eq(0xa0026728,'global derived address',0x62fc7000-0x3e8,0x62fc6c18)
cb(0xa002672c,7,9,0xa0026740);mv(0xa0026740,15,9);cb(0xa0026742,6,10,0xa002676c)
cl(0xa002676c,14,15,0x38);ci(0xa002676e,2,10,0);cl(0xa0026770,14,11,0,True)
cl(0xa0026772,14,15,0x3c);cl(0xa0026774,14,11,4,True)
cl(0xa0026776,15,15,0x40);cl(0xa0026778,15,11,8,True)
cstack(0xa002677a,1,28);cstack(0xa002677c,8,24);cstack(0xa002677e,9,20)
sp16(0xa0026780,32);ret(0xa0026782)

ci(0xa0026784,0,2,-32);cstack(0xa0026786,8,24,True);cstack(0xa0026788,1,28,True)
frame(0xa002678a,32);it(0xa002678c,19,11,0,8,-28);ci(0xa0026790,2,10,0)
jal(0xa0026792,0xa002671a);ci(0xa0026796,2,15,0)
v=w(0xa0026798);i=(bits(v,31,1)<<12)|(bits(v,7,1)<<11)|(bits(v,25,6)<<5)|(bits(v,8,4)<<1)
eq(0xa0026798,'signed negative gate',[v&127,bits(v,12,3),bits(v,15,5),bits(v,20,5),0xa0026798+sx(i,13)],
   [99,4,10,0,0xa00267a0])
it(0xa002679c,3,15,2,8,-24)
cstack(0xa00267a0,1,28);cstack(0xa00267a2,8,24);mv(0xa00267a4,10,15)
sp16(0xa00267a6,32);ret(0xa00267a8)

ci(0xa00267c0,0,2,-16);cstack(0xa00267c2,8,8,True);cstack(0xa00267c4,1,12,True)
frame(0xa00267c6,16);jal(0xa00267c8,0xa0026784);cb(0xa00267cc,6,10,0xa00267d8)
ci(0xa00267ce,0,10,4);cstack(0xa00267d0,1,12);cstack(0xa00267d2,8,8)
ci(0xa00267d4,0,2,16);ret(0xa00267d6)
v=w(0xa00267d8);eq(0xa00267d8,'fallback high LUI',[v&127,bits(v,7,5),v&0xfffff000],[55,10,0x62fc6000])
it(0xa00267dc,19,10,0,10,0x4c)
eq(0xa00267dc,'fallback derived address',0x62fc6000+0x4c,0x62fc604c)
v=w(0xa00267e0)
i=(bits(v,12,1)<<11)|(bits(v,11,1)<<4)|(bits(v,9,2)<<8)|(bits(v,8,1)<<10)
i|=(bits(v,7,1)<<6)|(bits(v,6,1)<<7)|(bits(v,3,3)<<1)|(bits(v,2,1)<<5)
eq(0xa00267e0,'fallback return join',[v&3,v>>13,0xa00267e0+sx(i,12)],[1,5,0xa00267d0])

out=dict(status='PASS',task='G28',claim='G19/6',baseline='bd457a6',reviewer='/root/a56',author='G27 /root/g23',
         identity=dict(path=str(ROM),length=6769704,mapping='VA-0x9ffff000',
         sha256_inherited='972db4c136c7ed9e24a83c07c1a7fd62040ca018b08ca285216d26b1fee3c6b9',hash_recomputed=False),
         method='Independent RV32/RVC instruction fields; author script not run; no Capstone needed',
         checks=checks,rows=[dict(address=hex(p),offset=hex(p-BASE),raw=r.hex()) for p,r in sorted(rows.items())],
         normal_contract='T=word(0x62fc6c18)!=0 and a0=0 -> out[1]=word(T+0x3c)=B; wrapper returns B, outer returns B?low32(B+4):0x62fc604c',
         conclusion='Limited acceptance, semantic corrections and new functionality 0',
         limits=['No T/B or fixed-slot type/lifetime/source writer certification',
                 'Normal stores are saved frames and caller local out only; no full-program side-effect claim',
                 'No guarantee of same T/B across calls, no alias/asynchronous-change exclusion',
                 'No diagnostic/pid-nonzero/scheduler/a002661e expansion or target execution'])
(OUT/'review-evidence.json').write_text(json.dumps(out,ensure_ascii=False,indent=2)+'\n',encoding='utf8')
print(json.dumps(dict(status='PASS',checks=len(checks),instructions=len(rows),bytes=sum(map(len,rows.values())))))
