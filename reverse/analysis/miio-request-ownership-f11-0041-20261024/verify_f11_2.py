"""F11/2 registered identity/normal lifetime bridges only; static fields."""
import json
from pathlib import Path
from capstone import Cs, CS_ARCH_RISCV, CS_MODE_RISCV32, CS_MODE_RISCVC

HERE=Path(__file__).resolve().parent
MAIN=Path('D:/Documents/PlatformIO/Projects/cuktech-ap01-firmware')
BASE=0x9ffff000
# No native queue, transport, parser, cipher, timeout or cancellation body reads.
ranges=[(0xa011f73a,0xa011f74e),(0xa0119ca2,0xa0119ca8),
        (0xa0119cbe,0xa0119cc8),(0xa0119d02,0xa0119d2c),(0xa0119d2c,0xa0119d3e),
        (0xa0119756,0xa011978a),(0xa0119b7e,0xa0119b9c),(0xa0119ba6,0xa0119bb6),
        (0xa011972a,0xa011973c),
        (0xa01ac234,0xa01ac248),(0xa01ac28e,0xa01ac2c2),(0xa01ac2c2,0xa01ac2ec),
        (0xa011f68c,0xa011f6d8),(0xa005f22a,0xa005f238),
        (0xa0116cf0,0xa0116d18),(0xa01ab838,0xa01ab844),(0xa01ab850,0xa01ab862)]
chunks={}
with (MAIN/'roms/0041/ap01-1.0.2_0041.bin').open('rb') as f:
    for a,b in ranges:
        f.seek(a-BASE); chunks[a]=f.read(b-a); assert len(chunks[a])==b-a
def raw(pc,n):
    for a,b in chunks.items():
        if a<=pc and pc+n<=a+len(b): return b[pc-a:pc-a+n]
    raise AssertionError(('outside F11/2 registered windows',hex(pc)))
def u32(pc): return int.from_bytes(raw(pc,4),'little')
def sx(v,n): return v-(1<<n) if v&(1<<(n-1)) else v
checks=[]
def require(pc,test,label):
    assert test,(hex(pc),label)
    checks.append({'pc':hex(pc),'check':label})
def exact(pc,code,label): require(pc,raw(pc,len(bytes.fromhex(code))).hex()==code,label+' actual='+raw(pc,len(bytes.fromhex(code))).hex())
def cmv(pc,rd,rs2):
    h=int.from_bytes(raw(pc,2),'little')
    require(pc,(h&3,h>>12,(h>>7)&31,(h>>2)&31)==(2,8,rd,rs2),'C.MV fields')
def load(pc,rd,rs,imm,f3=2):
    w=u32(pc)
    require(pc,(w&127,(w>>12)&7,(w>>7)&31,(w>>15)&31,sx(w>>20,12))==(3,f3,rd,rs,imm),'load width/field/register')
def store(pc,value,rs,imm,f3=2):
    w=u32(pc); off=sx(((w>>25)<<5)|((w>>7)&31),12)
    require(pc,(w&127,(w>>12)&7,(w>>20)&31,(w>>15)&31,off)==(35,f3,value,rs,imm),'store width/field/register')
def addi(pc,rd,rs,imm):
    w=u32(pc)
    require(pc,(w&127,(w>>12)&7,(w>>7)&31,(w>>15)&31,sx(w>>20,12))==(19,0,rd,rs,imm),'ADDI registers/immediate')
def call(pc,target):
    w=u32(pc)
    if w&127==0x6f:
        d=((w>>31)<<20)|(((w>>12)&255)<<12)|(((w>>20)&1)<<11)|(((w>>21)&1023)<<1)
        require(pc,(w>>7)&31==1 and pc+sx(d,21)==target,'independent JAL target')
    else:
        v=u32(pc+4)
        require(pc,w&127==0x17 and v&127==0x67 and (w>>7)&31==(v>>15)&31==1 and (v>>7)&31==1 and pc+sx(w&0xfffff000,32)+sx(v>>20,12)==target,'independent paired call target')
def branch(pc,target,f3,rs1,rs2):
    w=u32(pc)
    off=((w>>31)<<12)|(((w>>7)&1)<<11)|(((w>>25)&63)<<5)|(((w>>8)&15)<<1)
    require(pc,(w&127,(w>>12)&7,(w>>15)&31,(w>>20)&31,pc+sx(off,13))==(0x63,f3,rs1,rs2,target),'independent branch kind/register/target')

# f718 invocation payload supplies (ctx,0,R), saved as normal session fields.
for pc,code in [(0xa011f73a,'d040'),(0xa011f73c,'8840'),(0xa011f73e,'8145')]: exact(pc,code,'payload ctx/R and kind0 parameters')
call(0xa011f740,0xa0119c8e)
exact(0xa0119ca2,'2a89','save ctx in s2')
exact(0xa0119ca4,'ae89','save kind in s3')
exact(0xa0119ca6,'b28a','save R in s5')
exact(0xa0119cbe,'5145','allocate session14h bytes')
call(0xa0119cc0,0xa002fcc8)
call(0xa0119d06,0xa0024906)
load(0xa0119d0a,15,18,0x20)
store(0xa0119d10,18,9,4)
store(0xa0119d14,0,9,0)
store(0xa0119d18,9,18,0x20)
store(0xa0119d1c,19,9,8,0)
store(0xa0119d26,21,9,0x10)
store(0xa0119d32,18,9,4)
exact(0xa0119d38,'9cc0','append P.next from old tail.next')
exact(0xa0119d3a,'04c3','append old tail.next=P')

# Current lookup bridge builds kind/id/out criterion and returns its out slot.
exact(0xa0119756,'aa84','save lookup ctx')
exact(0xa0119758,'2e89','save lookup kind')
exact(0xa011975a,'b289','save lookup id')
exact(0xa0119768,'8850','load ctx+20 session head')
addi(0xa0119772,11,11,-0x316)
store(0xa0119776,19,8,-0x2c)
store(0xa011977a,18,8,-0x30,0)
store(0xa011977e,0,8,-0x28)
call(0xa0119782,0xa01ab82c)
load(0xa0119786,10,8,-0x28)
load(0xa0116cf0,14,10,8,4)
load(0xa0116cf4,15,11,0,4)
branch(0xa0116cf8,0xa0116d14,1,14,15)
exact(0xa0116cfc,'1c49','predicate loads P.R')
exact(0xa0116cfe,'d841','predicate loads requested id')
exact(0xa0116d00,'d443','predicate loads R.id')
branch(0xa0116d04,0xa0116d0c,1,13,14)
exact(0xa0116d08,'88c5','matching predicate stores P in criterion.out')
exact(0xa0116d0a,'fd57','matching predicate status=-1')
exact(0xa0116d0e,'3e85','return predicate status via a0')
exact(0xa0116d14,'8147','kind mismatch status0')
exact(0xa01ab838,'aa84','iterator saves node')
exact(0xa01ab83a,'2e89','iterator saves callback')
branch(0xa01ab840,0xa01ab850,0,10,0)
exact(0xa01ab850,'b285','predicate a1=criterion')
cmv(0xa01ab856,10,9)
exact(0xa01ab858,'0299','predicate call through s2')
exact(0xa01ab85e,'8440','after callback read node.next')

# Normal cleanup unlinks P from ctx+20 then cleans P.R and P itself.
exact(0xa0119b7e,'5841','load P.ctx')
exact(0xa0119b80,'1c53','load ctx.session_head')
exact(0xa0119b86,'1c41','load P.next')
exact(0xa0119b88,'1cd3','replace head with P.next')
store(0xa0119b8a,0,10,0)
exact(0xa0119b90,'0849','load P+10 request into a0')
call(0xa0119b92,0xa0119720)
exact(0xa0119b96,'2685','restore P as free argument')
call(0xa0119b98,0xa002e14e)
exact(0xa0119bb0,'1841','nonhead unlink reads P.next')
exact(0xa0119bb2,'98c3','nonhead unlink stores previous.next')
exact(0xa011972e,'4851','request cleanup loads owned message+24')
call(0xa0119732,0xa002e14e)
exact(0xa0119736,'2685','then free original object')
call(0xa0119738,0xa002e14e)

# S is a distinct reply allocation, not the original R or the pending-ID node.
cmv(0xa01ac234,19,10)
addi(0xa01ac236,10,0,0x3c)
cmv(0xa01ac23a,18,11)
call(0xa01ac23c,0xa002fcc8)
call(0xa01ac28e,0xa01ac1f0)
load(0xa01ac292,15,18,0)
load(0xa01ac296,10,18,0x1c)
exact(0xa01ac29a,'dcc0','S+4=response id')
load(0xa01ac29c,15,18,0xc,4)
exact(0xa01ac2a0,'88d0','S+20=response length')
store(0xa01ac2a2,15,9,0x10,0)
call(0xa01ac2a8,0xa002fcc8)
exact(0xa01ac2b0,'c8d0','S+24=allocated response message')
load(0xa01ac2b6,11,18,0x20)
call(0xa01ac2ba,0xa000589c)
load(0xa01ac2c2,10,19,4)
addi(0xa01ac2cc,11,11,0x67e)
call(0xa01ac2d0,0xa011f610)
call(0xa01ac2d8,0xa011f66c)
store(0xa01ac2dc,19,10,0)
exact(0xa01ac2e0,'44c1','payload holds S')
call(0xa01ac2e6,0xa011f84a)

# matched P yields R; actual callback receives S+4, then cleanup follows.
call(0xa011f690,0xa011f66c)
exact(0xa011f6a0,'dc40','load S from invocation payload')
exact(0xa011f6a2,'8840','lookup uses same response ctx')
exact(0xa011f6a4,'8145','lookup kind0')
exact(0xa011f6a6,'d043','lookup id from S+4')
call(0xa011f6a8,0xa0119748)
exact(0xa011f6ae,'1c49','load P+10 R')
exact(0xa011f6b4,'8c5b','user from R+30')
exact(0xa011f6b6,'d857','callback from R+2c')
exact(0xa011f6b8,'1105','callback view=S+4')
exact(0xa011f6ba,'0297','indirect callback a4')
call(0xa011f6c0,0xa01ab40c)
call(0xa011f6c6,0xa0119b72)
call(0xa011f6ce,0xa01b3c8c)
call(0xa011f6d4,0xa0119720)
exact(0xa005f22a,'4c4d','f222 length from view+1c')
exact(0xa005f22c,'0851','f222 message from view+20')
call(0xa005f22e,0xa01b38dc)

cs=Cs(CS_ARCH_RISCV,CS_MODE_RISCV32|CS_MODE_RISCVC)
rows=[]
for a,b in ranges:
    pc=a
    while pc<b:
        h=int.from_bytes(raw(pc,2),'little'); size=2 if h&3!=3 else 4
        assert pc+size<=b
        code=raw(pc,size); ins=next(cs.disasm(code,pc),None); assert ins is not None
        rows.append({'pc':hex(pc),'raw':code.hex(),'asm':ins.mnemonic+' '+ins.op_str}); pc+=size
result={'claim_id':'F11/2','management_registration':'608da2b (extends cb4abfd)','research_baseline':'ee220d8',
        'static_only':True,'ranges':[{'start':hex(a),'end_exclusive':hex(b)} for a,b in ranges],
        'instructions':rows,'checks':checks,
        'matching_scope':'first traversed P with byte kind0 and P.R.id equal S.id; uniqueness across same IDs is not established',
        'limits':['Only normal live session/list paths; no trap/null/other merged extent branches analyzed.',
                  'Same-ID uniqueness and concrete incoming transport producer not established.',
                  'Timer-control/locks are call boundaries, not expanded.',
                  'No actual target execution or native queue/parser/cipher/network/timeout/cancellation expansion.']}
(HERE/'evidence-f11-2.json').write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
print(json.dumps({'passed':True,'claim':'F11/2','checks':len(checks),'instructions':len(rows),'bytes':sum(b-a for a,b in ranges)}))
