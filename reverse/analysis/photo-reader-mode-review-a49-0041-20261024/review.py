"""A49 independent bounded static ABI/field review; no firmware execution."""
from pathlib import Path
import json

OUT=Path(__file__).resolve().parent
ROOT=OUT.parents[2]
ROM=Path('D:/Documents/PlatformIO/Projects/cuktech-ap01-firmware/roms/0041/ap01-1.0.2_0041.bin').read_bytes()
BASE=0x9ffff000
prior=json.loads((ROOT/'reverse/analysis/photo-reader-mode-a47-0041-20261024/evidence.json').read_text())
checks=[]
def raw(pc,n): return ROM[pc-BASE:pc-BASE+n]
def w(pc,n=4): return int.from_bytes(raw(pc,n),'little')
def sx(v,n): return v-(1<<n) if v&(1<<(n-1)) else v
def eq(label,got,expected):
    assert got==expected,(label,got,expected)
    checks.append(label)
def imm(pc,op,f3,rd,base,offset):
    v=w(pc)
    eq(hex(pc)+' I fields',(v&127,(v>>12)&7,(v>>7)&31,(v>>15)&31,sx(v>>20,12)),(op,f3,rd,base,offset))
def store(pc,f3,src,base,offset):
    v=w(pc)
    eq(hex(pc)+' store fields',(v&127,(v>>12)&7,(v>>20)&31,(v>>15)&31,sx(((v>>25)<<5)|((v>>7)&31),12)),(35,f3,src,base,offset))
def clw(pc,rd,base,offset):
    v=w(pc,2)
    eq(hex(pc)+' C.LW',(v&3,v>>13,8+((v>>2)&7),8+((v>>7)&7),((v>>10)&7)*8+((v>>6)&1)*4+((v>>5)&1)*64),(0,2,rd,base,offset))
def mv(pc,rd,src):
    v=w(pc,2)
    eq(hex(pc)+' C.MV',(v&3,v>>12,(v>>7)&31,(v>>2)&31),(2,8,rd,src))
def cli(pc,rd,value):
    v=w(pc,2)
    eq(hex(pc)+' C.LI',(v&3,v>>13,(v>>7)&31,sx(((v>>12)&1)*32+((v>>2)&31),6)),(1,2,rd,value))
def cb(pc,nonzero,reg,target):
    v=w(pc,2)
    off=(((v>>12)&1)<<8)|(((v>>10)&3)<<3)|(((v>>5)&3)<<6)|(((v>>3)&3)<<1)|(((v>>2)&1)<<5)
    eq(hex(pc)+' compressed branch',(v&3,v>>13,8+((v>>7)&7),pc+sx(off,9)),(1,7 if nonzero else 6,reg,target))
def branch(pc,f3,r1,r2,target):
    v=w(pc)
    off=((v>>31)<<12)|(((v>>7)&1)<<11)|(((v>>25)&63)<<5)|(((v>>8)&15)<<1)
    eq(hex(pc)+' branch',(v&127,(v>>12)&7,(v>>15)&31,(v>>20)&31,pc+sx(off,13)),(99,f3,r1,r2,target))
def call(pc,target):
    v=w(pc)
    if v&127==111:
        eq(hex(pc)+' JAL ABI',(v>>7)&31,1)
        off=((v>>31)<<20)|(((v>>12)&255)<<12)|(((v>>20)&1)<<11)|(((v>>21)&1023)<<1)
        got=pc+sx(off,21)
    else:
        n=w(pc+4)
        eq(hex(pc)+' AUIPC/JALR ABI',(v&127,(v>>7)&31,n&127,(n>>7)&31,(n>>15)&31),(23,1,103,1,1))
        got=(pc+sx(v&0xfffff000,32)+sx(n>>20,12))&0xffffffff
    eq(hex(pc)+' call target',got,target)

for r in prior['rows']: eq(r['pc']+' retained raw',raw(int(r['pc'],16),len(bytes.fromhex(r['raw']))).hex(),r['raw'])
branch(0xa00ed878,1,10,15,0xa00ed842)
cli(0xa00ed876,15,1)
mv(0xa00ed87c,10,19)
mv(0xa0107da2,9,10)
cli(0xa0107da4,11,0)
imm(0xa0107da6,19,0,12,0,0x664)
for pc in [0xa0107daa,0xa0107db6,0xa0107dcc]: imm(pc,19,0,10,8,-0x674)
cli(0xa0107db2,15,1)
mv(0xa0107db4,11,9)
store(0xa0107dba,2,0,8,-0x660)
store(0xa0107dbe,2,0,8,-0x668)
store(0xa0107dc2,0,15,8,-0x664)
cb(0xa0107dca,True,10,0xa0107de6)
for a,t in [(0xa00ed87e,0xa0107d8e),(0xa0107dae,0xa0024906),(0xa0107dc6,0xa019d6a4),(0xa0107dd0,0xa010a65a),(0xa019d7b4,0xa008e362),(0xa01b2e66,0xa008ab8a),(0xa01b2e70,0xa008ab8a)]: call(a,t)
store(0xa019d798,2,9,18,4)
clw(0xa019d7a8,14,9,4)
cb(0xa019d7ac,False,14,0xa019d6dc)
cli(0xa019d7ae,10,16)
store(0xa019d7bc,2,10,18,8)
store(0xa019d828,2,10,18,0)
clw(0xa019d80e,14,9,12)
cli(0xa019d810,12,2)
mv(0xa019d812,10,9)
eq('open callback C.JALR a4',w(0xa019d818,2),0x9702)
mv(0xa01b2e44,9,10)
for args in [(0xa01b2e46,10,10,4),(0xa01b2e4a,15,10,16),(0xa01b2e4e,11,9,0),(0xa01b2e52,15,9,4),(0xa01b2e54,14,15,4),(0xa01b2e58,15,9,8),(0xa01b2e62,10,15,12),(0xa01b2e6e,10,9,8)]: clw(*args)
eq('close callback C.JALR a5',w(0xa01b2e50,2),0x9782)
for args in [(0xa01b2e48,False,10,0xa01b2e84),(0xa01b2e4c,False,15,0xa01b2e84),(0xa01b2e56,False,14,0xa01b2e78),(0xa01b2e5a,False,15,0xa01b2e78),(0xa01b2e64,False,10,0xa01b2e6e)]: cb(*args)
cli(0xa01b2e5c,13,-1)
branch(0xa01b2e5e,0,14,13,0xa01b2e6e)
for pc,offset in [(0xa01b2e78,0),(0xa01b2e7c,4),(0xa01b2e80,8)]: store(pc,2,0,9,offset)
extra=[(0xa0107dd4,'8320c16703248167832441671301016882800145f5b7'),(0xa019d75c,'232eb4fc02978325c4fd'),(0xa01b2e84,'b2402244924441018280')]
for pc,h in extra: eq(hex(pc)+' supplemental raw',raw(pc,len(bytes.fromhex(h))).hex(),h)
cli(0xa0107de6,10,0)
store(0xa019d75c,2,11,8,-0x24)
imm(0xa019d762,3,2,11,8,-0x24)
result={'status':'PASS','static_only':True,'retained_rows_compared':len(prior['rows']),'checks':checks,'supplemental_bytes':[{'pc':hex(pc),'raw':h} for pc,h in extra],'supplemental_byte_count':sum(len(bytes.fromhex(h)) for _,h in extra),'new_functionality':0,'limits':['No concrete D or callback target identity; no actual default-photo mode1 observation.','Normal branch ABI and cleanup reviewed; all failures and filesystem internals not reviewed.','A37/A39 copy and A41/A42 outer destructor contracts inherited.']}
(OUT/'review-result.json').write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n',encoding='utf8')
print(json.dumps({'status':result['status'],'checks':len(checks),'retained_rows':result['retained_rows_compared'],'supplemental_bytes':result['supplemental_byte_count']}))
