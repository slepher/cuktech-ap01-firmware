"""Independent E19 static bytes/fields and constant bounds, no input execution."""
from pathlib import Path
import json

OUT=Path(__file__).resolve().parent
ROOT=OUT.parents[2]
BASE=0x9ffff000
ROM=Path('D:/Documents/PlatformIO/Projects/cuktech-ap01-firmware/roms/0041/ap01-1.0.2_0041.bin').read_bytes()
PRIOR=json.loads((ROOT/'reverse/analysis/uv-time-division-e18-0041-20261024/evidence.json').read_text())
checks=[]
def raw(pc,n): return ROM[pc-BASE:pc-BASE+n]
def w(pc,n=4): return int.from_bytes(raw(pc,n),'little')
def sx(v,n): return v-(1<<n) if v&(1<<(n-1)) else v
def eq(label,got,expected):
    assert got==expected,(label,got,expected)
    checks.append(label)
def reg(pc,f7,f3,rd,r1,r2):
    v=w(pc)
    eq(hex(pc)+' register fields',(v&127,v>>25,(v>>12)&7,(v>>7)&31,(v>>15)&31,(v>>20)&31),(51,f7,f3,rd,r1,r2))
def imm(pc,op,f3,rd,r1,value):
    v=w(pc)
    eq(hex(pc)+' immediate fields',(v&127,(v>>12)&7,(v>>7)&31,(v>>15)&31,sx(v>>20,12)),(op,f3,rd,r1,value))
def mv(pc,rd,r2):
    v=w(pc,2)
    eq(hex(pc)+' C.MV',(v&3,v>>12,(v>>7)&31,(v>>2)&31),(2,8,rd,r2))
def cli(pc,rd,value):
    v=w(pc,2)
    eq(hex(pc)+' C.LI',(v&3,v>>13,(v>>7)&31,sx((((v>>12)&1)<<5)|((v>>2)&31),6)),(1,2,rd,value))
def cadd(pc,rd,r2):
    v=w(pc,2)
    eq(hex(pc)+' C.ADD',(v&3,v>>12,(v>>7)&31,(v>>2)&31),(2,9,rd,r2))
def calu(pc,kind,rd,r2):
    v=w(pc,2)
    eq(hex(pc)+' compressed ALU',(v&3,v>>13,(v>>12)&1,(v>>10)&3,(v>>5)&3,8+((v>>7)&7),8+((v>>2)&7)),(1,4,0,3,kind,rd,r2))
def cslli(pc,rd,shift):
    v=w(pc,2)
    eq(hex(pc)+' C.SLLI',(v&3,v>>13,(v>>7)&31,(((v>>12)&1)<<5)|((v>>2)&31)),(2,0,rd,shift))
def branch(pc,f3,r1,r2,target):
    v=w(pc)
    off=((v>>31)<<12)|(((v>>7)&1)<<11)|(((v>>25)&63)<<5)|(((v>>8)&15)<<1)
    eq(hex(pc)+' branch fields',(v&127,(v>>12)&7,(v>>15)&31,(v>>20)&31,pc+sx(off,13)),(99,f3,r1,r2,target))

for r in PRIOR['instructions']:
    eq(r['address']+' retained raw',raw(int(r['address'],16),len(bytes.fromhex(r['bytes']))).hex(),r['bytes'])
for pc,rd,r2 in [(0xa001b302,17,10),(0xa001b304,15,11),(0xa001b306,16,12),(0xa001b308,10,13),(0xa001b30a,6,17),(0xa001b36c,10,13),(0xa001b3a8,12,15)]: mv(pc,rd,r2)
for args in [(0xa001b30c,1,13,0,0xa001b518),(0xa001b318,7,11,12,0xa001b3d6),(0xa001b31e,7,12,14,0xa001b3c8),(0xa001b3ce,6,12,10,0xa001b32c),(0xa001b340,0,10,14,0xa001b356),(0xa001b376,7,15,11,0xa001b38e),(0xa001b3aa,7,6,13,0xa001b3c0)]: branch(*args)
# Resolve existing table address; only one used table byte is read.
x,y=w(0xa001b310),w(0xa001b314)
eq('table base register ABI',(x&127,(x>>7)&31,y&127,(y>>7)&31,(y>>15)&31),(23,13,19,13,13))
table=(0xa001b310+sx(x&0xfffff000,32)+sx(y>>20,12))&0xffffffff
eq('table address',table,0xa01bb7f0)
eq('table used byte',raw(table+15,1)[0],4)
v=w(0xa001b31c,2)
eq('first normalization threshold C.LUI',(v&3,v>>13,(v>>7)&31,sx((((v>>12)&1)<<5)|((v>>2)&31),6)<<12),(1,3,14,65536))
v=w(0xa001b3c8)
eq('second normalization threshold LUI',(v&127,(v>>7)&31,v&0xfffff000),(55,10,0x1000000))
cli(0xa001b3cc,14,16)
reg(0xa001b32c,0,5,10,12,14)
cadd(0xa001b330,13,10)
imm(0xa001b332,3,4,13,13,0)
imm(0xa001b336,19,0,10,0,32)
cadd(0xa001b33a,14,13)
reg(0xa001b33c,32,0,13,10,14)
reg(0xa001b344,0,1,11,15,13)
reg(0xa001b348,0,5,14,17,14)
reg(0xa001b34c,0,1,16,12,13)
calu(0xa001b350,2,11,14)
reg(0xa001b352,0,1,6,17,13)
imm(0xa001b356,19,5,17,16,16)
imm(0xa001b35e,19,1,12,16,16)
v=w(0xa001b362,2)
eq('low divisor digit C.SRLI',(v&3,v>>13,(v>>10)&3,8+((v>>7)&7),(((v>>12)&1)<<5)|((v>>2)&31)),(1,4,0,12,16))
imm(0xa001b364,19,5,15,6,16)
for args in [(0xa001b35a,1,5,13,11,17),(0xa001b368,1,7,14,11,17),(0xa001b36e,1,0,11,12,13),(0xa001b390,1,7,14,15,17),(0xa001b39a,1,5,15,15,17),(0xa001b3a4,1,0,13,12,15)]: reg(*args)
cslli(0xa001b372,14,16)
calu(0xa001b374,2,15,14)
calu(0xa001b38e,0,15,11)
cslli(0xa001b394,6,16)
imm(0xa001b396,19,5,6,6,16)
cslli(0xa001b39e,14,16)
reg(0xa001b3a0,0,6,6,14,6)
cslli(0xa001b3c0,10,16)
calu(0xa001b3c2,2,10,12)
cli(0xa001b3c4,11,0)
v=w(0xa001b3c6,2)
off=(((v>>12)&1)<<11)|(((v>>11)&1)<<4)|(((v>>9)&3)<<8)|(((v>>8)&1)<<10)|(((v>>7)&1)<<6)|(((v>>6)&1)<<7)|(((v>>3)&7)<<1)|(((v>>2)&1)<<5)
eq('return jump ABI/target',(v&3,v>>13,0xa001b3c6+sx(off,12)),(1,5,0xa001b47c))
eq('return preserves pair',w(0xa001b47c,2),0x8082)
# Constant bounds only: no algorithm model, sample inputs, or input enumeration.
D=1000000
bound=(2**32-1)*D
eq('max numerator',bound,4294967295000000)
eq('fine word cannot be negative',999*D<2**31,True)
eq('max H below divisor',bound//2**32,999999)
eq('N shift fits uint64',bound*2**12<2**64,True)
eq('D first threshold',D>=65536,True)
eq('D second threshold',D<2**24,True)
eq('table index',D>>16,15)
eq('normalization shift',32-(16+4),12)
eq('normalized divisor',D<<12,0xf4240000)
eq('high divisor digit',(D<<12)>>16,62500)
eq('low divisor digit',(D<<12)&65535,0)
result={'status':'PASS','static_only':True,'retained_rows_compared':len(PRIOR['instructions']),'checks':checks,'new_functionality':0,'additional_rom_bytes_saved':0,'proof_scope':'D=1000000, divisor high word=0, N=t*D for inherited single U32 t. Symbolic proof in report; checks only bytes, fields, constants and bounds.','limits':['No arithmetic input execution, emulation, replay or runtime observation.','No arbitrary divisor/quotient path or compiler-library provenance certification.','Clock/source/writer/timer contracts inherited without revalidation.']}
(OUT/'review-result.json').write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n',encoding='utf8')
print(json.dumps({'status':result['status'],'retained_rows':result['retained_rows_compared'],'checks':len(checks),'additional_rom_bytes_saved':0}))
