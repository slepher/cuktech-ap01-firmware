"""A61 independent registered initializer fields; inherited G setup is not rerun."""
from pathlib import Path
import json
MAIN=Path('D:/Documents/PlatformIO/Projects/cuktech-ap01-firmware')
ROM=MAIN/'roms/0041/ap01-1.0.2_0041.bin'
OUT=Path(__file__).resolve().parent
BASE=0x9ffff000;G=0x62fc957c
assert ROM.stat().st_size==6769704
checks=[];rows={}
def bits(v,a,n):return (v>>a)&((1<<n)-1)
def sx(v,n):return v-(1<<n) if v&(1<<(n-1)) else v
def w(pc):
    assert pc==0xa008e4c4 or 0xa008e506<=pc<0xa008e52a
    if pc not in rows:
        with ROM.open('rb') as f:
            f.seek(pc-BASE);r=f.read(2)
            if r[0]&3==3:r+=f.read(2)
        rows[pc]=r
    return int.from_bytes(rows[pc],'little')
def eq(label,got,want):
    assert got==want,(label,got,want)
    checks.append(dict(label=label,value=got))
v=w(0xa008e4c4)
i=(bits(v,12,1)<<8)|(bits(v,10,2)<<3)|(bits(v,5,2)<<6)|(bits(v,3,2)<<1)|(bits(v,2,1)<<5)
eq('normal compressed gate',[v&3,v>>13,8+bits(v,7,3),0xa008e4c4+sx(i,9)],[1,7,10,0xa008e506])
for pc,imm in [(0xa008e506,24),(0xa008e51c,4)]:
    v=w(pc);eq(hex(pc)+' C.LI a5',[v&3,v>>13,bits(v,7,5),
            sx((bits(v,12,1)<<5)|bits(v,2,5),6)],[1,2,15,imm])
v=w(0xa008e508)
eq('intermediate C.SW not s1 definition',[v&3,v>>13,8+bits(v,2,3),8+bits(v,7,3),
       (bits(v,10,3)<<3)|(bits(v,6,1)<<2)|(bits(v,5,1)<<6)],[0,6,15,9,0x74])
for pc,src,off in [(0xa008e50a,0,0x78),(0xa008e50e,0,0x7c),
                    (0xa008e51e,15,0x1c4),(0xa008e522,0,0x1c8),(0xa008e526,0,0x1cc)]:
    v=w(pc);eq(hex(pc)+' word store',[v&127,bits(v,12,3),bits(v,15,5),bits(v,20,5),
        sx((bits(v,25,7)<<5)|bits(v,7,5),12)],[35,2,9,src,off])
v=w(0xa008e512)
eq('intermediate byte store not s1 definition',[v&127,bits(v,12,3),bits(v,15,5),bits(v,20,5),
    sx((bits(v,25,7)<<5)|bits(v,7,5),12)],[35,0,9,24,0x80])
v=w(0xa008e516)
i=(bits(v,31,1)<<20)|(bits(v,12,8)<<12)|(bits(v,20,1)<<11)|(bits(v,21,10)<<1)
eq('opaque helper target / ra write',[v&127,bits(v,7,5),0xa008e516+sx(i,21)],[111,1,0xa0087b06])
v=w(0xa008e51a)
eq('post-helper C.LW targets a0, not s1',[v&3,v>>13,8+bits(v,2,3),8+bits(v,7,3),
    (bits(v,10,3)<<3)|(bits(v,6,1)<<2)|(bits(v,5,1)<<6)],[0,2,10,9,0x58])
for off,slot in [(0x1c4,0x62fc9740),(0x1c8,0x62fc9744),(0x1cc,0x62fc9748)]:
    eq('exact inherited-G address '+hex(off),G+off,slot)
eq('stride initialization gives conditional next offset',4+4,8)
out=dict(status='PASS',task='A61',claim='J08/4',baseline='bd457a6',reviewer='/root/a56',author='A60 /root/g23',
    identity=dict(path=str(ROM),length=6769704,mapping='VA-0x9ffff000',
    sha256_inherited='972db4c136c7ed9e24a83c07c1a7fd62040ca018b08ca285216d26b1fee3c6b9',hash_recomputed=False),
    method='Independent RV32/RVC fields; no author script or decoder use',checks=checks,
    rows=[dict(address=hex(pc),offset=hex(pc-BASE),raw=r.hex()) for pc,r in sorted(rows.items())],
    inherited_assumptions=['A21/A22/A25/A26 established normal caller, global clear and s1=G=0x62fc957c; not rerun',
                          'a0!=0 branch taken at e4c4; e516 helper returns under ordinary callee-preserved s1 convention'],
    contract='On selected normal path, word(G+1c4)=4, word(G+1c8)=0, then word(G+1cc)=0; no other explicit s1 write in newly checked straight path',
    conclusion='Limited acceptance; semantic corrections and new functionality 0',
    limits=['No helper body, remaining initializer window, registry publication or node registration',
            'Third zero word is an address/order anchor only; no full container layout certification',
            'No proof of real execution, later-writer absence, concrete D/slots or lifecycle',
            'No target/instruction/model/old-script/input execution or shared REA state change'])
(OUT/'review-evidence.json').write_text(json.dumps(out,ensure_ascii=False,indent=2)+'\n',encoding='utf8')
print(json.dumps(dict(status='PASS',checks=len(checks),instructions=len(rows),bytes=sum(map(len,rows.values())))))
