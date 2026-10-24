"""Confirmed claim F11/1 only: sparse static bytes/fields; never run target."""
import json
from pathlib import Path
from capstone import Cs, CS_ARCH_RISCV, CS_MODE_RISCV32, CS_MODE_RISCVC

HERE = Path(__file__).resolve().parent
MAIN = Path('D:/Documents/PlatformIO/Projects/cuktech-ap01-firmware')
BASE = 0x9ffff000
# Explicit range fence: pending F11/2 response/session functions are not read.
ranges = [(0xa01b62fc,0xa01b6332),(0xa0112038,0xa0112066),(0xa0112072,0xa0112092),
          (0xa011f9ea,0xa011fa1e),(0xa011f886,0xa011f892),(0xa011f89c,0xa011f8a8),
          (0xa011f8f2,0xa011f956),(0xa011f956,0xa011f96c),(0xa011f992,0xa011f9a8),
          (0xa011f8d2,0xa011f8da),(0xa011f8ea,0xa011f8f2),(0xa011f9d2,0xa011f9da),
          (0xa011f622,0xa011f65c),(0xa011f674,0xa011f678),
          (0xa011f850,0xa011f858),(0xa011f862,0xa011f864),
          (0xa011e306,0xa011e31e),(0xa011e31e,0xa011e344),
          (0xa011e37a,0xa011e382),(0xa011e382,0xa011e390),(0xa011e3b8,0xa011e3d6)]
chunks = {}
with (MAIN/'roms/0041/ap01-1.0.2_0041.bin').open('rb') as stream:
    for start,end in ranges:
        stream.seek(start-BASE)
        chunks[start] = stream.read(end-start)
        assert len(chunks[start]) == end-start
def raw(pc,n):
    for start,data in chunks.items():
        if start <= pc and pc+n <= start+len(data): return data[pc-start:pc-start+n]
    raise AssertionError(('outside confirmed sparse ranges',hex(pc),n))
def u32(pc): return int.from_bytes(raw(pc,4),'little')
def sx(v,n): return v-(1<<n) if v & (1<<(n-1)) else v
checks = []
def require(pc,test,label):
    assert test,(hex(pc),label)
    checks.append({'pc':hex(pc),'check':label})
def load(pc,f3,rd,rs1,imm):
    w = u32(pc)
    require(pc,(w&127,(w>>12)&7,(w>>7)&31,(w>>15)&31,sx(w>>20,12))==(3,f3,rd,rs1,imm),'load width/register/offset')
def store(pc,f3,rs2,rs1,imm):
    w = u32(pc); off=sx(((w>>25)<<5)|((w>>7)&31),12)
    require(pc,(w&127,(w>>12)&7,(w>>20)&31,(w>>15)&31,off)==(35,f3,rs2,rs1,imm),'store width/register/offset')
def addi(pc,rd,rs1,imm):
    w = u32(pc)
    require(pc,(w&127,(w>>12)&7,(w>>7)&31,(w>>15)&31,sx(w>>20,12))==(19,0,rd,rs1,imm),'ADDI registers/immediate')
def call(pc,target):
    w = u32(pc)
    if w&127 == 0x6f:
        d=((w>>31)<<20)|(((w>>12)&255)<<12)|(((w>>20)&1)<<11)|(((w>>21)&1023)<<1)
        require(pc,(w>>7)&31==1 and pc+sx(d,21)==target,'independent JAL target')
    else:
        v=u32(pc+4)
        require(pc,w&127==0x17 and v&127==0x67 and (w>>7)&31==(v>>15)&31==1 and (v>>7)&31==1 and pc+sx(w&0xfffff000,32)+sx(v>>20,12)==target,'independent AUIPC/JALR target')
def exact(pc,code,label): require(pc,raw(pc,len(bytes.fromhex(code))).hex()==code,label)
def cbranch(pc,target,funct3,rs):
    h=int.from_bytes(raw(pc,2),'little')
    d=(((h>>12)&1)<<8)|(((h>>10)&3)<<3)|(((h>>5)&3)<<6)|(((h>>3)&3)<<1)|(((h>>2)&1)<<5)
    require(pc,(h&3,h>>13,8+((h>>7)&7),pc+sx(d,9))==(1,funct3,rs,target),'independent compressed condition/target')
def bbranch(pc,target,funct3,rs1,rs2):
    w=u32(pc)
    d=((w>>31)<<12)|(((w>>7)&1)<<11)|(((w>>25)&63)<<5)|(((w>>8)&15)<<1)
    require(pc,(w&127,(w>>12)&7,(w>>15)&31,(w>>20)&31,pc+sx(d,13))==(0x63,funct3,rs1,rs2,target),'independent branch fields/target')

# Caller D offsets and callback/user publication.
addi(0xa01b62fc,10,8,-0x54)
call(0xa01b6300,0xa01ac1c4)
addi(0xa01b6308,15,15,0x222)
store(0xa01b630c,2,18,8,-0x50)
store(0xa01b6310,0,0,8,-0x44)
store(0xa01b6314,2,20,8,-0x30)
store(0xa01b6318,2,19,8,-0x34)
store(0xa01b631c,2,15,8,-0x28)
store(0xa01b6320,2,9,8,-0x24)
addi(0xa01b6326,11,8,-0x54)
call(0xa01b632a,0xa0111ff6)
bbranch(0xa01b632e,0xa01b61d0,0,10,0)

# Send adapter chooses context and passes D+4, callback, user.
load(0xa0112040,4,15,15,0x136)
addi(0xa0112038,14,18,0x7ff)
addi(0xa011203c,15,14,0x7ff)
load(0xa011204e,2,14,14,0x26d)
addi(0xa0112056,10,10,-0x698)
addi(0xa011205c,11,9,4)
call(0xa0112062,0xa011f9da)
load(0xa0112072,4,15,18,0x1c8)
load(0xa011207e,2,14,14,0xe1)
addi(0xa0112088,11,9,4)
addi(0xa011208c,10,18,0x174)
for pc,code in [(0xa0112052,'9458'),(0xa0112054,'d054'),
                (0xa0112082,'9458'),(0xa0112084,'d054')]: exact(pc,code,'callback/user compressed loads')

# Q=D+4: clear metadata before copying the selected fields into R.
exact(0xa011f9f0,'2146','C.LI a2,8')
exact(0xa011f9f2,'8145','C.LI a1,0')
addi(0xa011f9f4,10,9,0x10)
call(0xa011fa04,0xa0024906)
call(0xa011fa1a,0xa011f86c)
addi(0xa011f89c,10,0,0x3c)
call(0xa011f8a0,0xa002fcc8)
cbranch(0xa011f8a6,0xa011f8f2,7,10)
call(0xa011f8f2,0xa01ac1f0)
load(0xa011f8f6,2,15,18,0)
load(0xa011f902,4,15,18,0xc)
store(0xa011f90a,0,15,9,0x10)
addi(0xa011f8fc,11,18,0x10)
addi(0xa011f906,10,9,0x14)
call(0xa011f90e,0xa000589c)
load(0xa011f916,2,10,18,0x1c)
call(0xa011f920,0xa002fcc8)
cbranch(0xa011f91c,0xa011f93e,6,10)
cbranch(0xa011f926,0xa011f8a8,6,10)
load(0xa011f92a,2,11,18,0x20)
call(0xa011f92e,0xa000589c)
store(0xa011f93e,2,19,9,0x2c)
store(0xa011f942,2,23,9,0x30)
store(0xa011f94a,2,22,9,0)
store(0xa011f952,2,21,9,0x34)
w=u32(0xa011f93a)
require(0xa011f93a,(w&127,(w>>12)&7,(w>>7)&31,(w>>15)&31,(w>>20)&31,(w>>27)&31,(w>>25)&3)==(11,5,0,14,15,0,0),'indexed byte zero store at allocated_message+length')

# Invocation I is a separate allocation, payload holds {ctx,R}.
load(0xa011f956,2,10,20,4)
addi(0xa011f960,11,11,0x718)
call(0xa011f964,0xa011f610)
call(0xa011f992,0xa011f66c)
store(0xa011f996,2,20,10,0)
exact(0xa011f99a,'44c1','C.SW R,4(payload)')
call(0xa011f9a0,0xa011f84a)
cbranch(0xa011f9a6,0xa011f8da,6,10)
call(0xa011f8d6,0xa0119720)
call(0xa011f9d4,0xa002e14e)
exact(0xa011f622,'0d06','payload length plus3')
exact(0xa011f624,'719a','align length down to4')
exact(0xa011f626,'6106','add invocation header18')
call(0xa011f632,0xa002fcc8)
call(0xa011f640,0xa0024906)
addi(0xa011f648,15,15,0x2f0)
store(0xa011f650,0,15,9,8)
store(0xa011f654,2,18,9,0xc)
store(0xa011f658,2,19,9,0x10)
exact(0xa011f674,'6d05','payload pointer plus1b')
exact(0xa011f676,'7199','payload pointer align down4')
exact(0xa011f852,'4cc9','store queue argument at I+14')
exact(0xa011f854,'dc43','load dispatch callback from I+4')
exact(0xa011f856,'1105','pass I+4')
exact(0xa011f862,'8297','indirect invoke installed dispatch')
exact(0xa011f8ea,'4a85','restore saved construction status to a0')

# type1 I enters the loop-owned queue; lower queue service is a boundary.
load(0xa011e306,4,15,10,4)
addi(0xa011e30a,18,10,-4)
load(0xa011e38a,2,19,18,0xc)
load(0xa011e324,2,15,19,0xc)
load(0xa011e32c,2,10,19,0x18)
store(0xa011e330,2,18,8,-0x24)
addi(0xa011e33a,11,8,-0x24)
call(0xa011e33e,0xa005f464)
load(0xa011e3b8,2,15,19,0x2c)
store(0xa011e3be,2,18,19,0x2c)
store(0xa011e3cc,2,0,9,-4)
store(0xa011e3d0,2,18,14,0)
exact(0xa011e3c2,'8144','same-loop append returns status0 in s1')
exact(0xa011e37a,'2685','return saved dispatch status in a0')

cs=Cs(CS_ARCH_RISCV,CS_MODE_RISCV32|CS_MODE_RISCVC)
rows=[]
for start,end in ranges:
    pc=start
    while pc<end:
        h=int.from_bytes(raw(pc,2),'little'); n=2 if h&3!=3 else 4
        assert pc+n<=end
        code=raw(pc,n); ins=next(cs.disasm(code,pc),None)
        assert ins is not None or pc==0xa011f93a
        rows.append({'pc':hex(pc),'raw':code.hex(),'asm':ins.mnemonic+' '+ins.op_str if ins else 'vendor indexed byte zero store; independently field-checked'})
        pc+=n
model_path=MAIN/'evidence/rea-0041-20261017/ghidra/Ghidra/Processors/RISCV/data/languages/ap01thead2.sinc'
model=model_path.read_text(); at=model.index(':th.srb ')
rule=model[at:model.index('\n}',at)+2]
assert '*[ram]:1 ea = rd:1' in rule
result={'claim_id':'F11/1','management_registration':'02afb05','research_baseline':'ee220d8',
        'static_only':True,'ranges':[{'start':hex(a),'end_exclusive':hex(b)} for a,b in ranges],
        'instructions':rows,'checks':checks,'vendor_rule_source':str(model_path),'inherited_vendor_rule':rule,
        'limits':['F11/2 remains pending disambiguation; no response/session ROM bytes read by this script.',
                  'No target/model/instruction execution or input experiments.',
                  'Generic event-loop type1 dispatch/return1 transfer is inherited from upper-miio-b, not reimplemented.',
                  'Native a005f464 pointer-copy and full session/response ownership are not claimed here.']}
(HERE/'evidence-f11-1.json').write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
print(json.dumps({'passed':True,'claim':'F11/1','checks':len(checks),'instructions':len(rows),'bytes':sum(b-a for a,b in ranges)}))
