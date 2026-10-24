"""G24 independent sparse RISC-V bit-field review; no target execution."""
from pathlib import Path
import json

MAIN=Path('D:/Documents/PlatformIO/Projects/cuktech-ap01-firmware')
OUT=Path(__file__).resolve().parent
ROM=MAIN/'roms/0041/ap01-1.0.2_0041.bin'
BASE=0x9ffff000
assert ROM.stat().st_size==6769704
saved={}
checks=[]

def sx(x,n): return x-(1<<n) if x&(1<<(n-1)) else x
def bits(x,a,n): return (x>>a)&((1<<n)-1)
def raw(pc):
    assert 0xa009dfcc<=pc<0xa009e0e6
    if pc not in saved:
        with ROM.open('rb') as f:
            f.seek(pc-BASE)
            b=f.read(2)
            if b[0]&3==3: b+=f.read(2)
        saved[pc]=b
    return int.from_bytes(saved[pc],'little')
def eq(pc,label,got,want):
    assert got==want,(hex(pc),label,got,want)
    checks.append(dict(address=hex(pc),label=label,decoded=got))
def clw(pc,rd,base,off,store=False):
    v=raw(pc)
    got=[v&3,v>>13,8+bits(v,2,3),8+bits(v,7,3),
         (bits(v,10,3)<<3)|(bits(v,6,1)<<2)|(bits(v,5,1)<<6)]
    eq(pc,'compressed word store' if store else 'compressed word load',got,
       [0,6 if store else 2,rd,base,off])
def mv(pc,rd,src):
    v=raw(pc);eq(pc,'compressed move',[v&3,v>>12,bits(v,7,5),bits(v,2,5)],[2,8,rd,src])
def li(pc,rd,imm):
    v=raw(pc);eq(pc,'compressed immediate',[v&3,v>>13,bits(v,7,5),
        sx((bits(v,12,1)<<5)|bits(v,2,5),6)],[1,2,rd,imm])
def it(pc,op,rd,f3,rs1,imm):
    v=raw(pc);eq(pc,'I-type',[v&127,bits(v,7,5),bits(v,12,3),bits(v,15,5),sx(v>>20,12)],
                 [op,rd,f3,rs1,imm])
def b(pc,f3,r1,r2,target):
    v=raw(pc)
    imm=(bits(v,31,1)<<12)|(bits(v,7,1)<<11)|(bits(v,25,6)<<5)|(bits(v,8,4)<<1)
    eq(pc,'B-type branch',[v&127,bits(v,12,3),bits(v,15,5),bits(v,20,5),pc+sx(imm,13)],
       [99,f3,r1,r2,target])
def j(pc,target,compressed=False,link=False):
    v=raw(pc)
    if not compressed:
        imm=(bits(v,31,1)<<20)|(bits(v,12,8)<<12)|(bits(v,20,1)<<11)|(bits(v,21,10)<<1)
        got=[v&127,bits(v,7,5),pc+sx(imm,21)]
        want=[111,1 if link else 0,target]
    else:
        imm=(bits(v,12,1)<<11)|(bits(v,11,1)<<4)|(bits(v,9,2)<<8)|(bits(v,8,1)<<10)
        imm|=(bits(v,7,1)<<6)|(bits(v,6,1)<<7)|(bits(v,3,3)<<1)|(bits(v,2,1)<<5)
        got=[v&3,v>>13,pc+sx(imm,12)];want=[1,1 if link else 5,target]
    eq(pc,'direct jump/call',got,want)

clw(0xa009dfe0,14,11,0x3c);li(0xa009dfe2,15,-1)
b(0xa009dfe4,1,14,15,0xa009dffa)
for pc,rd,base,off in [(0xa009dffa,15,11,0),(0xa009dffe,14,15,0),
                       (0xa009e000,15,11,4),(0xa009e002,15,15,0),
                       (0xa009e04a,14,9,0),(0xa009e04c,15,9,4),
                       (0xa009e04e,14,14,0),(0xa009e050,15,15,0),
                       (0xa009e070,14,9,0x14),(0xa009e072,13,9,0x18),
                       (0xa009e074,15,14,0),(0xa009e076,13,13,0),
                       (0xa009e096,13,9,0x1c),(0xa009e098,14,9,0x24),
                       (0xa009e0a0,14,15,8),(0xa009e0a4,12,15,0),
                       (0xa009e0a6,13,15,4)]: clw(pc,rd,base,off)
mv(0xa009dffc,9,11);mv(0xa009e00c,19,10);mv(0xa009e00e,18,12)
v=raw(0xa009e004)
eq(0xa009e004,'word subtraction tail-head',[v&127,bits(v,7,5),bits(v,12,3),bits(v,15,5),bits(v,20,5),v>>25],
   [51,20,0,15,14,32])
b(0xa009e008,0,14,15,0xa009e042)
it(0xa009e010,19,22,0,0,0x26);li(0xa009e014,21,4)
j(0xa009e016,0xa00267c0,link=True)
v=raw(0xa009e01a)
eq(0xa009e01a,'word store constant to returned address',
   [v&127,bits(v,12,3),bits(v,15,5),bits(v,20,5),sx((bits(v,25,7)<<5)|bits(v,7,5),12)],
   [35,2,10,22,0])
j(0xa009e01e,0xa00267c0,link=True);clw(0xa009e022,15,10,0)
b(0xa009e024,0,15,21,0xa009e016)
j(0xa009e030,0xa0134716,link=True);li(0xa009e034,15,-1)
b(0xa009e036,0,20,15,0xa009e04a)
for pc,val in [(0xa009e03c,0x500),(0xa009e044,0x4f5),
               (0xa009e058,0x502),(0xa009e0be,0x51c),(0xa009e0ca,0x51f)]:
    it(pc,19,11,0,0,val)
for pc in (0xa009e040,0xa009e048,0xa009e05c,0xa009e0c2,0xa009e0ce):
    j(pc,0xa009dfee,compressed=True)
j(0xa009dff6,0xa0019672,link=True)
b(0xa009e052,0,14,15,0xa009e05e)
li(0xa009e05e,12,16);mv(0xa009e060,11,18);it(0xa009e062,19,10,0,8,-0x30)
j(0xa009e066,0xa000589c,link=True)
li(0xa009e06a,20,2);li(0xa009e06c,21,1);li(0xa009e06e,22,-17)
b(0xa009e078,1,15,13,0xa009e090)
it(0xa009e090,19,13,0,15,1);clw(0xa009e094,13,14,0,store=True)
v=raw(0xa009e09a)
eq(0xa009e09a,'compressed and mask',[v&3,v>>10,bits(v,5,2),8+bits(v,7,3),8+bits(v,2,3)],
   [1,35,3,15,13])
for pc in (0xa009e09c,0xa009e0d4):
    v=raw(pc);eq(pc,'compressed index shift4',[v&3,v>>13,bits(v,7,5),bits(v,2,5),bits(v,12,1)],
                [2,0,15,4,0])
for pc in (0xa009e09e,0xa009e0d6):
    v=raw(pc);eq(pc,'compressed address add',[v&3,v>>12,bits(v,7,5),bits(v,2,5)],[2,9,15,14])
v=raw(0xa009e0a2)
imm=(bits(v,12,1)<<8)|(bits(v,10,2)<<3)|(bits(v,5,2)<<6)|(bits(v,3,2)<<1)|(bits(v,2,1)<<5)
eq(0xa009e0a2,'compressed result zero branch',[v&3,v>>13,8+bits(v,7,3),0xa009e0a2+sx(imm,9)],
   [1,6,14,0xa009e070])
it(0xa009e0a8,19,11,7,12,3);it(0xa009e0b0,19,15,7,15,255)
v=raw(0xa009e0ac)
eq(0xa009e0ac,'wexti pair fields',[v&127,bits(v,7,5),bits(v,12,3),bits(v,15,5),bits(v,20,5),v>>25],
   [119,15,0,12,2,111])
b(0xa009e0b4,0,11,20,0xa009e070);b(0xa009e0b8,0,11,21,0xa009e0c4)
b(0xa009e0c4,0,14,22,0xa009e0d0)
it(0xa009e0d0,19,14,0,8,-0x30)
for pc,rd,src in [(0xa009e0d8,12,18),(0xa009e0da,14,13),(0xa009e0dc,11,9),(0xa009e0e0,10,19)]:
    mv(pc,rd,src)
li(0xa009e0de,13,3);j(0xa009e0e2,0xa009e0e6,compressed=True,link=True)
j(0xa009e0e4,0xa009e070,compressed=True)

# Check every instruction of the bounded epilogue by architectural fields.
for pc,rd,off in [(0xa009e07c,1,0x2c),(0xa009e07e,8,0x28),(0xa009e080,9,0x24),
                  (0xa009e082,18,0x20),(0xa009e084,19,0x1c),(0xa009e086,20,0x18),
                  (0xa009e088,21,0x14),(0xa009e08a,22,0x10)]:
    v=raw(pc)
    imm=(bits(v,12,1)<<5)|(bits(v,4,3)<<2)|(bits(v,2,2)<<6)
    eq(pc,'epilogue LWSP; no a0 write',[v&3,v>>13,bits(v,7,5),imm],[2,2,rd,off])
eq(0xa009e08c,'restore sp',raw(0xa009e08c),0x6145)
eq(0xa009e08e,'return ra without a0 write',raw(0xa009e08e),0x8082)
# Only frame-size anchors, not a whole-function dump.
eq(0xa009dfcc,'entry frame allocation',raw(0xa009dfcc),0x7179)
eq(0xa009dfde,'frame pointer sp+0x30',raw(0xa009dfde),0x1800)

model_path=MAIN/'evidence/rea-0041-20261017/ghidra/Ghidra/Processors/RISCV/data/languages/ap01thead2.sinc'
t=model_path.read_text(encoding='utf8');p=t.index(':wexti rd,rs1,op2024');rule=t[p:t.index('\n}',p)+2]
eq(0xa009e0ac,'existing pair model clauses',
   all(x in rule for x in ('local src:8 = (high << 32) | low;', 'src >> op2024', 'rd = shifted:4;')),True)
out=dict(status='PASS',task='G24',claim='G19/4',reviewer='/root/a56',author='G23 /root/g23',baseline='32f9c9e',
         static_only=True,identity=dict(path=str(ROM),length=6769704,mapping='VA - 0x9ffff000',
         sha256_inherited='972db4c136c7ed9e24a83c07c1a7fd62040ca018b08ca285216d26b1fee3c6b9',hash_recomputed=False),
         method='Independent RV32/RVC bit fields, sparse seeks; author script not run; no Capstone needed',
         checks=checks,raw=[dict(address=hex(a),file_offset=hex(a-BASE),raw=b.hex()) for a,b in sorted(saved.items())],
         model=dict(path=str(model_path),rule=rule,limit='Existing local profile only; no independent ISA authentication'),
         conclusion='Limited acceptance; new business functionality 0; post-diagnostic reachability remains unclosed',
         limits=['No callee body or op3 body expansion','No target/model/instruction execution or input experiment',
                 'No OS submission/success/lifetime certification','Diagnostic return and caller-saved registers unknown'])
(OUT/'review-evidence.json').write_text(json.dumps(out,ensure_ascii=False,indent=2)+'\n',encoding='utf8')
print(json.dumps(dict(status='PASS',checks=len(checks),instructions=len(saved),bytes=sum(map(len,saved.values())))))
