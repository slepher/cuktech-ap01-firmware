"""F23 registered caller-gap and normal state/return increment, no callees run."""
from pathlib import Path
import json
MAIN=Path('D:/Documents/PlatformIO/Projects/cuktech-ap01-firmware')
ROM=MAIN/'roms/0041/ap01-1.0.2_0041.bin';BASE=0x9ffff000
OUT=Path(__file__).resolve().parent
assert ROM.stat().st_size==6769704
checks=[];rows={}
def b(v,a,n):return (v>>a)&((1<<n)-1)
def sx(v,n):return v-(1<<n) if v&(1<<(n-1)) else v
def w(pc):
    assert 0xa0197ad2<=pc<0xa0197ae8 or 0xa0131920<=pc<0xa01319e8
    if pc not in rows:
        with ROM.open('rb') as f:
            f.seek(pc-BASE);r=f.read(2)
            if r[0]&3==3:r+=f.read(2)
        rows[pc]=r
    return int.from_bytes(rows[pc],'little')
def eq(label,got,want):
    assert got==want,(label,got,want)
    checks.append(dict(label=label,value=got))
def ci(pc,f3,rd,imm):
    v=w(pc);eq(hex(pc)+' CI',[v&3,v>>13,b(v,7,5),sx((b(v,12,1)<<5)|b(v,2,5),6)],[1,f3,rd,imm])
def mv(pc,rd,src):
    v=w(pc);eq(hex(pc)+' MV',[v&3,v>>12,b(v,7,5),b(v,2,5)],[2,8,rd,src])
def it(pc,op,rd,f3,base,imm):
    v=w(pc);eq(hex(pc)+' I-format',[v&127,b(v,7,5),b(v,12,3),b(v,15,5),sx(v>>20,12)],
               [op,rd,f3,base,imm])
def st(pc,f3,src,base,off):
    v=w(pc);eq(hex(pc)+' S-format',[v&127,b(v,12,3),b(v,15,5),b(v,20,5),
        sx((b(v,25,7)<<5)|b(v,7,5),12)],[35,f3,base,src,off])
def branch(pc,f3,r1,r2,target):
    v=w(pc);i=(b(v,31,1)<<12)|(b(v,7,1)<<11)|(b(v,25,6)<<5)|(b(v,8,4)<<1)
    eq(hex(pc)+' branch',[v&127,b(v,12,3),b(v,15,5),b(v,20,5),pc+sx(i,13)],
       [99,f3,r1,r2,target])
def cb(pc,f3,reg,target):
    v=w(pc);i=(b(v,12,1)<<8)|(b(v,10,2)<<3)|(b(v,5,2)<<6)|(b(v,3,2)<<1)|(b(v,2,1)<<5)
    eq(hex(pc)+' compressed branch',[v&3,v>>13,8+b(v,7,3),pc+sx(i,9)],[1,f3,reg,target])
def cj(pc,target):
    v=w(pc);i=(b(v,12,1)<<11)|(b(v,11,1)<<4)|(b(v,9,2)<<8)|(b(v,8,1)<<10)
    i|=(b(v,7,1)<<6)|(b(v,6,1)<<7)|(b(v,3,3)<<1)|(b(v,2,1)<<5)
    eq(hex(pc)+' compressed jump',[v&3,v>>13,pc+sx(i,12)],[1,5,target])
def pair(pc,target):
    u=w(pc);v=w(pc+4)
    eq(hex(pc)+' AUIPC/JALR',[u&127,b(u,7,5),v&127,b(v,7,5),b(v,15,5),
             (pc+sx(u&0xfffff000,32)+sx(v>>20,12))&0xfffffffe],[23,1,103,1,1,target])
v=w(0xa0197ad2);eq('gap diagnostic string high',[v&127,b(v,7,5),v&0xfffff000],[55,10,0xa062d000])
ci(0xa0197ad6,2,12,0);it(0xa0197ad8,19,11,0,0,0x79);it(0xa0197adc,19,10,0,10,-0x78c)
pair(0xa0197ae0,0xa0019672)
mv(0xa0131938,18,10);it(0xa013193a,19,19,7,11,0x40)
v=w(0xa013193e);eq('T global high',[v&127,b(v,7,5),v&0xfffff000],[55,21,0x62fc7000])
ci(0xa0131942,2,22,8);it(0xa0131944,19,23,0,10,8)
it(0xa0131948,3,14,1,18,0x22);it(0xa013194c,3,15,1,18,0x20)
branch(0xa0131950,5,14,15,0xa0131958);ci(0xa0131954,2,10,0);cj(0xa0131956,0xa01319cc)
branch(0xa0131958,1,19,0,0xa01319e4);it(0xa013195c,19,20,0,21,-0x3e8)
eq('T global exact address',0x62fc7000-0x3e8,0x62fc6c18)
it(0xa0131960,3,9,2,20,0);st(0xa0131964,2,18,9,0x44)
it(0xa0131968,3,15,5,18,0x10);ci(0xa013196c,0,15,1);st(0xa013196e,1,15,18,0x10)
v=w(0xa0131972)
eq('T+0xc word',[v&3,v>>13,8+b(v,2,3),8+b(v,7,3),
              (b(v,10,3)<<3)|(b(v,6,1)<<2)|(b(v,5,1)<<6)],[0,2,15,9,12])
st(0xa0131974,1,0,9,0x22);branch(0xa0131978,4,0,15,0xa0131992)
pair(0xa013198a,0xa0019672)
ci(0xa0131992,2,11,1);mv(0xa0131994,10,9);pair(0xa0131996,0xa002772e)
mv(0xa013199e,24,10);st(0xa01319a0,0,22,9,0x1c)
mv(0xa01319a4,11,23);mv(0xa01319a6,10,9);pair(0xa01319a8,0xa00272d4)
branch(0xa01319b0,0,24,0,0xa01319c2)
it(0xa01319b4,3,10,2,20,0);mv(0xa01319b8,11,9);pair(0xa01319ba,0xa001ad30)
it(0xa01319c2,3,10,1,9,0x22);cb(0xa01319c6,6,10,0xa0131948)
v=w(0xa01319c8)
eq('return negated signed halfword',[v&127,b(v,7,5),b(v,12,3),b(v,15,5),b(v,20,5),v>>25],
   [51,10,0,0,10,32])
ci(0xa01319e4,2,10,-11);cj(0xa01319e6,0xa01319cc)

# The service saves/restores its incoming s3/s4, which hold source/n in the caller.
for pc,reg,off,store in [(0xa0131926,19,28,True),(0xa0131932,20,24,True),
                       (0xa01319d4,19,28,False),(0xa01319d6,20,24,False)]:
    v=w(pc)
    if store:i=(b(v,7,2)<<6)|(b(v,9,4)<<2);r=b(v,2,5)
    else:i=(b(v,12,1)<<5)|(b(v,4,3)<<2)|(b(v,2,2)<<6);r=b(v,7,5)
    eq(hex(pc)+' preserve caller source/length registers',[v&3,v>>13,r,i],[2,6 if store else 2,reg,off])
eq('service return ra',w(0xa01319e2),0x8082)
out=dict(status='PASS-registered-increment',task='F23',claim='F11/8',baseline='bd457a6',
    identity=dict(path=str(ROM),length=6769704,mapping='VA-0x9ffff000',
    sha256_inherited='972db4c136c7ed9e24a83c07c1a7fd62040ca018b08ca285216d26b1fee3c6b9',hash_recomputed=False),
    checks=checks,rows=[dict(address=hex(p),offset=hex(p-BASE),raw=r.hex()) for p,r in sorted(rows.items())],
    exploration='Registered 22B caller gap and 200B service read in bounded windows; a window landing inside an instruction was discarded and re-aligned from entry, no semantic claim from it',
    contract='Service returns0 if signed K+22 < signed K+20; else flag40 returns-11. Other normal route records K in T+44, increments U16 K+10, clears T+22, calls opaque boundaries, then T+22 zero repeats own checks or nonzero returns its negation; caller zero retries M getter, not direct outM.',
    opaque_calls=[dict(pc='0xa0131996/0xa013199a',target='0xa002772e',a0='T',a1=1),
                  dict(pc='0xa01319a8/0xa01319ac',target='0xa00272d4',a0='T',a1='K+8'),
                  dict(pc='0xa01319ba/0xa01319be',target='0xa001ad30',a0='reload word(0x62fc6c18)',a1='saved T')],
    limits=['No body of new lower calls, scheduler, diagnostics or timed send',
            'T validity/lifetime, callback/source memory retention and actual mode/thread state unknown',
            'Nonzero return is negated signed LH; do not assume all nonzero returns negative',
            'Caller source/n saved values are preserved under normal service ABI/return; not source-region lifetime proof',
            'No target/instruction/model/old-script/input execution'])
(OUT/'increment-evidence.json').write_text(json.dumps(out,ensure_ascii=False,indent=2)+'\n',encoding='utf8')
print(json.dumps(dict(status=out['status'],checks=len(checks),sample_instructions=len(rows),sample_bytes=sum(map(len,rows.values())))))
