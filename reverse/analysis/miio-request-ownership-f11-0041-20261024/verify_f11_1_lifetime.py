"""F11/1 extension2e203cc: only the registered early-message-return gates."""
import json
from pathlib import Path

HERE=Path(__file__).resolve().parent
MAIN=Path('D:/Documents/PlatformIO/Projects/cuktech-ap01-firmware')
BASE=0x9ffff000
ranges=[(0xa011f79a,0xa011f79c),(0xa011f818,0xa011f832)]
chunks={}
with (MAIN/'roms/0041/ap01-1.0.2_0041.bin').open('rb') as stream:
    for a,b in ranges:
        stream.seek(a-BASE); chunks[a]=stream.read(b-a); assert len(chunks[a])==b-a
def raw(pc,n):
    for a,b in chunks.items():
        if a<=pc and pc+n<=a+len(b): return b[pc-a:pc-a+n]
    raise AssertionError('outside2e203cc extension')
def sx(v,n): return v-(1<<n) if v&(1<<(n-1)) else v
checks=[]
def need(pc,test,meaning):
    assert test,(hex(pc),meaning)
    checks.append({'pc':hex(pc),'raw':raw(pc,2 if int.from_bytes(raw(pc,2),'little')&3!=3 else 4).hex(),'meaning':meaning})
def clw(pc,rd,rs,off):
    h=int.from_bytes(raw(pc,2),'little')
    imm=(((h>>10)&7)<<3)|(((h>>6)&1)<<2)|(((h>>5)&1)<<6)
    need(pc,(h&3,h>>13,8+((h>>2)&7),8+((h>>7)&7),imm)==(0,2,rd,rs,off),'C.LW exact object/offset')
def cb(pc,target,f3,rs):
    h=int.from_bytes(raw(pc,2),'little')
    off=(((h>>12)&1)<<8)|(((h>>10)&3)<<3)|(((h>>5)&3)<<6)|(((h>>3)&3)<<1)|(((h>>2)&1)<<5)
    need(pc,(h&3,h>>13,8+((h>>7)&7),pc+sx(off,9))==(1,f3,rs,target),'compressed condition and target')
cb(0xa011f79a,0xa011f818,7,10)
clw(0xa011f818,15,9,4)
clw(0xa011f81a,14,15,0x34)
cb(0xa011f81c,0xa011f832,7,14)
clw(0xa011f81e,10,15,0x24)
cb(0xa011f820,0xa011f832,6,10)
w=int.from_bytes(raw(0xa011f822,4),'little')
d=((w>>31)<<20)|(((w>>12)&255)<<12)|(((w>>20)&1)<<11)|(((w>>21)&1023)<<1)
need(0xa011f822,w&127==0x6f and (w>>7)&31==1 and 0xa011f822+sx(d,21)==0xa002e14e,'message pointer in a0 passed to inherited return service')
clw(0xa011f826,15,9,4)
clw(0xa011f82c,15,9,4)
for pc in [0xa011f828,0xa011f82e]:
    w=int.from_bytes(raw(pc,4),'little'); off=sx(((w>>25)<<5)|((w>>7)&31),12)
    need(pc,(w&127,(w>>12)&7,(w>>20)&31,(w>>15)&31,off)==(35,2,0,15,0x24),'SW zero to same R+24; not length+20')
out={'claim':'F11/1','management_extension':'2e203cc','research_baseline':'ee220d8','static_only':True,
     'ranges':[{'start':hex(a),'end_exclusive':hex(b)} for a,b in ranges],'checks':checks,
     'contract':'If prior service return is nonzero, loaded R+34 is zero and loaded R+24 is nonzero, hand that message to return service; reload R and clear R+24 twice. R object remains held by session.',
     'limits':['No assumed initializer default for R+34 when constructor skips assignment.',
               'No backend/timer/allocator-body expansion or target execution.']}
(HERE/'evidence-f11-1-lifetime.json').write_text(json.dumps(out,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
print(json.dumps({'passed':True,'claim':'F11/1','checks':len(checks),'bytes':sum(b-a for a,b in ranges)}))
