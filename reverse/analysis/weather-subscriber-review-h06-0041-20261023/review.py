"""H06 independent static ROM review. No target execution or imported H05 verifier."""
from pathlib import Path
import json
from capstone import Cs, CS_ARCH_RISCV, CS_MODE_RISCV32, CS_MODE_RISCVC

OUT = Path(__file__).resolve().parent
ROM = Path('D:/Documents/PlatformIO/Projects/cuktech-ap01-firmware/roms/0041/ap01-1.0.2_0041.bin')
BASE = 0x9ffff000
data = ROM.read_bytes()
decoder = Cs(CS_ARCH_RISCV, CS_MODE_RISCV32 | CS_MODE_RISCVC)
spans = [(0xa005cc1e,0xa005cc5a), (0xa005cfd8,0xa005cff8),
         (0xa005e4e6,0xa005e524), (0xa005e8d2,0xa005e90a),
         (0xa00abed2,0xa00abfe6), (0xa00abb62,0xa00abbf6),
         (0xa019cbc0,0xa019cd14), (0xa008e362,0xa008e38c),
         (0xa0080d8e,0xa0080da6), (0xa00b3c14,0xa00b3c26)]
decoded = {}
for first,end in spans:
    at = first
    for i in decoder.disasm(data[first-BASE:end-BASE],first):
        assert i.address == at
        decoded[at] = i
        at += i.size
    assert at == end, ('decode gap',hex(at),hex(end))

def raw(at,n=4):
    return int.from_bytes(data[at-BASE:at-BASE+n], 'little')
def signed(n,bits):
    return n - (1<<bits) if n & (1<<(bits-1)) else n
checks=[]
def check(at,kind,got,want):
    assert got == want,(hex(at),kind,got,want)
    checks.append(dict(va=hex(at),kind=kind,result=got))
def load(at,rd,rs,offset,width):
    w=raw(at)
    check(at,'RV32 load [opcode,rd,rs1,offset,funct3]',
          [w&127,w>>7&31,w>>15&31,signed(w>>20,12),w>>12&7],
          [3,rd,rs,offset,width])
def store(at,rs2,rs1,offset):
    w=raw(at)
    check(at,'RV32 store [opcode,rs2,rs1,offset,funct3]',
          [w&127,w>>20&31,w>>15&31,signed((w>>25<<5)|(w>>7&31),12),w>>12&7],
          [35,rs2,rs1,offset,2])
def clw(at,rd,rs,off):
    h=raw(at,2)
    check(at,'RVC LW [quadrant,funct3,rd,rs1,offset]',
          [h&3,h>>13,8+(h>>2&7),8+(h>>7&7),((h>>5&1)<<6)|((h>>10&7)<<3)|((h>>6&1)<<2)],
          [0,2,rd,rs,off])
def cmv(at,rd,rs):
    h=raw(at,2)
    check(at,'RVC MV [quadrant,funct4,rd,rs2]',[h&3,h>>12,h>>7&31,h>>2&31],[2,8,rd,rs])
def cli(at,rd,imm):
    h=raw(at,2)
    check(at,'RVC LI [quadrant,funct3,rd,imm]',
          [h&3,h>>13,h>>7&31,signed(((h>>12&1)<<5)|(h>>2&31),6)],[1,2,rd,imm])
def direct(at,target,rd=1):
    w=raw(at)
    delta=((w>>31)<<20)|((w>>12&255)<<12)|((w>>20&1)<<11)|((w>>21&1023)<<1)
    check(at,'JAL [opcode,rd,target]',[w&127,w>>7&31,hex(at+signed(delta,21))],[111,rd,hex(target)])
def cj(at,target):
    h=raw(at,2)
    delta=((h>>12&1)<<11)|((h>>11&1)<<4)|((h>>9&3)<<8)|((h>>8&1)<<10)|((h>>7&1)<<6)|((h>>6&1)<<7)|((h>>3&7)<<1)|((h>>2&1)<<5)
    check(at,'RVC J [quadrant,funct3,target]',[h&3,h>>13,hex(at+signed(delta,12))],[1,5,hex(target)])
def cb(at,nonzero,rs,target):
    h=raw(at,2)
    delta=((h>>12&1)<<8)|((h>>10&3)<<3)|((h>>5&3)<<6)|((h>>3&3)<<1)|((h>>2&1)<<5)
    check(at,'RVC branch [quadrant,funct3,rs1,target]',[h&3,h>>13,8+(h>>7&7),hex(at+signed(delta,9))],[1,7 if nonzero else 6,rs,hex(target)])
def branch(at,kind,r1,r2,target):
    w=raw(at)
    delta=((w>>31)<<12)|((w>>7&1)<<11)|((w>>25&63)<<5)|((w>>8&15)<<1)
    check(at,'branch [opcode,funct3,rs1,rs2,target]',
          [w&127,w>>12&7,w>>15&31,w>>20&31,hex(at+signed(delta,13))],
          [99,kind,r1,r2,hex(target)])
def const(hi,lo,reg,want):
    a,b=raw(hi),raw(lo)
    check(hi,'LUI/ADDI register and address',
          [a&127,a>>7&31,b&127,b>>7&31,b>>15&31,b>>12&7,hex(((a&0xfffff000)+signed(b>>20,12))&0xffffffff)],
          [55,reg,19,reg,reg,0,hex(want)])

# Constructor ownership and true event callback constants.
cmv(0xa005cfd8,10,20); direct(0xa005cfda,0xa00d91c6)
cmv(0xa005cfde,21,10); cli(0xa005cfe2,10,20)
cb(0xa005cfe0,False,10,0xa005cff8)
direct(0xa005cfe4,0xa008e362); cmv(0xa005cfe8,24,10)
cb(0xa005cfea,False,10,0xa005cff0); direct(0xa005cfec,0xa005e4e6,0)
cmv(0xa005cff0,10,21); direct(0xa005cff2,0xa00d7806); cli(0xa005cff6,21,0)
check(0xa005e4e6,'ctx allocation LI raw instruction',hex(raw(0xa005e4e6)),'0x4400513')
direct(0xa005e4ea,0xa008e362); cmv(0xa005e4ee,18,10)
cb(0xa005e4f0,True,10,0xa005e524)
cmv(0xa005e514,10,21); direct(0xa005e516,0xa00d7806)
cmv(0xa005e51a,10,24); direct(0xa005e51c,0xa008ab8a)
direct(0xa005e520,0xa005cff6,0)
const(0xa005e8d2,0xa005e8d8,10,0xa00abed2); cmv(0xa005e8d6,11,21)
direct(0xa005e8dc,0xa00b3a68); cli(0xa005e8e0,15,4)
store(0xa005e8e2,15,24,0); store(0xa005e8e6,18,24,4); store(0xa005e8ee,24,21,16)
const(0xa005e8ea,0xa005e8f8,11,0xa00abb62); cli(0xa005e8f2,13,0)
check(0xa005e8f4,'DELETE filter raw',hex(raw(0xa005e8f4)),'0x2900613')
cmv(0xa005e8fc,10,21)
check(0xa005e8fe,'AUIPC/JALR installer',hex((0xa005e8fe+(raw(0xa005e8fe)&0xfffff000)+signed(raw(0xa005e902)>>20,12))&0xffffffff),'0xa01ad654')
check(0xa005e8fe,'AUIPC/JALR uses ra for base and link',
      [raw(0xa005e8fe)&127,raw(0xa005e8fe)>>7&31,raw(0xa005e902)&127,raw(0xa005e902)>>7&31,raw(0xa005e902)>>15&31],
      [23,1,103,1,1])

# Callback ABI, signed temperatures, unsigned clock words, repeated ctx reads.
branch(0xa00abed2,0,11,0,0xa00abfe4)
clw(0xa00abef0,15,11,16); clw(0xa00abefa,9,15,4)
for at,rd,off,f3 in [(0xa00abef2,18,28,2),(0xa00abef6,23,6,1),(0xa00abefc,24,8,1),
                     (0xa00abf00,25,10,1),(0xa00abf04,21,14,5),(0xa00abf08,22,16,5),
                     (0xa00abf0c,19,18,5),(0xa00abf10,20,20,5),(0xa00abf14,12,12,1)]:
    load(at,rd,10,off,f3)
for at,rd,off in [(0xa00abf18,10,12),(0xa00abf26,11,0),(0xa00abf28,10,12),
                  (0xa00abf36,11,12),(0xa00abf38,10,16),(0xa00abf44,11,12),
                  (0xa00abf46,10,20),(0xa00abf54,10,24),(0xa00abf66,10,28),
                  (0xa00abf76,10,32),(0xa00abf7e,10,36),(0xa00abf8a,10,40),(0xa00abf98,10,44)]:
    clw(at,rd,9,off)
for at,rd,rs in [(0xa00abf5a,13,25),(0xa00abf5c,12,24),(0xa00abf6c,12,23),
                 (0xa00abf78,11,18),(0xa00abf80,11,18),(0xa00abf8c,13,22),
                 (0xa00abf8e,12,21),(0xa00abf9a,13,20),(0xa00abf9c,12,19)]: cmv(at,rd,rs)
for at,target in [(0xa00abf22,0xa0091ee4),(0xa00abf32,0xa00dbb68),(0xa00abf40,0xa00dbb68),
                  (0xa00abf50,0xa00dbb68),(0xa00abf62,0xa0091ee4),(0xa00abf72,0xa0091ee4),
                  (0xa00abf7a,0xa019cbc0),(0xa00abf86,0xa00a6d34),(0xa00abf94,0xa0091ee4),
                  (0xa00abfa2,0xa0091ee4)]: direct(at,target)
const(0xa00abf1a,0xa00abf1e,11,0xa06130bc)
const(0xa00abf56,0xa00abf5e,11,0xa01c3cb4)
const(0xa00abf68,0xa00abf6e,11,0xa01c3ccc)

# DELETE gate and untouched a0 between ctx load, sixteen stores, and free.
clw(0xa00abb62,15,10,8)
check(0xa00abb64,'mask LUI,ADDI,AND raw',data[0xa00abb64-BASE:0xa00abb6a-BASE].hex(),'61777d17f98f')
branch(0xa00abb6e,1,15,14,0xa00abbf4)
clw(0xa00abb7e,9,10,4); load(0xa00abb80,18,9,16,2)
branch(0xa00abb84,0,18,0,0xa00abbe8); load(0xa00abb88,10,18,4,2)
order=[28,52,8,16,20,0,12,48,40,44,4,36,32,24,56,60]
for index,off in enumerate(order): store(0xa00abb8c+4*index,0,10,off)
check(0xa00abb8c,'clear set is exactly first sixteen words',sorted(order),list(range(0,64,4)))
direct(0xa00abbcc,0xa008ab8a)
const(0xa00abbd0,0xa00abbd6,10,0xa00abed2); cmv(0xa00abbd4,11,9)
direct(0xa00abbda,0xa00b3abe); cmv(0xa00abbde,10,18)
direct(0xa00abbe0,0xa008ab8a); store(0xa00abbe4,0,9,16)

# Setter category decision tree: original RV32 branch destinations plus literals.
cmv(0xa019cbcc,18,10); cmv(0xa019cbce,10,11); direct(0xa019cbd0,0xa00a6998)
cmv(0xa019cbd4,9,10); cli(0xa019cbd6,11,1); cmv(0xa019cbd8,10,18); direct(0xa019cbda,0xa00d9044)
for at,f3,r1,r2,target in [
 (0xa019cbe0,0,9,15,0xa019ccba),(0xa019cbe4,6,15,9,0xa019cc46),
 (0xa019cbea,0,9,15,0xa019cc9c),(0xa019cbee,6,15,9,0xa019cc24),
 (0xa019cbf4,0,9,15,0xa019ccec),(0xa019cbf8,6,15,9,0xa019cc14),
 (0xa019cbfe,0,9,15,0xa019ccd8),(0xa019cc04,0,9,15,0xa019cce2),
 (0xa019cc16,1,9,15,0xa019cc08),(0xa019cc26,0,9,15,0xa019ccc4),
 (0xa019cc2c,0,9,15,0xa019ccb0),(0xa019cc32,1,9,15,0xa019cc08),
 (0xa019cc48,0,9,15,0xa019cca6),(0xa019cc4c,6,15,9,0xa019cc80),
 (0xa019cc52,0,9,15,0xa019ccce),(0xa019cc56,6,15,9,0xa019cc70),
 (0xa019cc5c,0,9,15,0xa019cd0a),(0xa019cc62,1,9,15,0xa019cc08),
 (0xa019cc72,1,9,15,0xa019cc08),(0xa019cc82,0,9,15,0xa019ccf6),
 (0xa019cc88,0,9,15,0xa019cd00),(0xa019cc8e,1,9,15,0xa019cc08)]: branch(at,f3,r1,r2,target)
for at,n in [(0xa019cbde,9),(0xa019cbe8,5),(0xa019cbf2,3),(0xa019cbfc,1),
             (0xa019cc02,2),(0xa019cc14,4),(0xa019cc24,7),(0xa019cc2a,8),
             (0xa019cc30,6),(0xa019cc46,14),(0xa019cc50,12),(0xa019cc5a,10),
             (0xa019cc60,11),(0xa019cc70,13),(0xa019cc80,22),(0xa019cc86,23),(0xa019cc8c,15)]: cli(at,15,n)
resources=[(1,0xa019ccd8,0xa0251fd4),(2,0xa019cce2,0xa063461c),(3,0xa019ccec,0xa0633960),
 (4,0xa019cc1a,0xa0633f50),(5,0xa019cc9c,0xa06318b0),(6,0xa019cc36,0xa06315bc),
 (7,0xa019ccc4,0xa0631f78),(8,0xa019ccb0,0xa0632308),(9,0xa019ccba,0xa0632968),
 (10,0xa019cd0a,0xa0636644),(11,0xa019cc66,0xa0636130),(12,0xa019ccce,0xa06334ec),
 (13,0xa019cc76,0xa06330b8),(14,0xa019cca6,0xa0631c68),(22,0xa019ccf6,0xa0634fe4),(23,0xa019cd00,0xa0635878)]
for cat,at,src in resources: const(at,at+4,11,src)
for at in [0xa019cc22,0xa019cc6e,0xa019cc7e,0xa019cca4,0xa019ccae,0xa019ccb8,
           0xa019ccc2,0xa019cccc,0xa019ccd6,0xa019cce0,0xa019ccea,0xa019ccf4,
           0xa019ccfe,0xa019cd08,0xa019cd12]: cj(at,0xa019cc3e)
cj(0xa019cc44,0xa019cc08); cj(0xa019cc9a,0xa019cc08)
check(0xa019cc12,'default return raw',hex(raw(0xa019cc12,2)),'0x8082')
cmv(0xa019cc3e,10,18); direct(0xa019cc40,0xa00ed560)
cli(0xa019cc92,11,1); cmv(0xa019cc94,10,18); direct(0xa019cc96,0xa00d8f7c)

# Zero allocator and synchronous callback dispatch boundary, not full lower libraries.
direct(0xa008e370,0xa002fcc8); cmv(0xa008e374,9,10)
cb(0xa008e376,False,10,0xa008e380)
load(0xa008e378,11,8,-20,2); direct(0xa008e37c,0xa0080d8e); cmv(0xa008e384,10,9)
cmv(0xa0080d96,12,11); cli(0xa0080d98,11,0); direct(0xa0080d9a,0xa0024906)
clw(0xa00b3c14,15,9,0); clw(0xa00b3c18,11,9,4); cmv(0xa00b3c1c,10,19)
check(0xa00b3c1e,'RVC JALR a5 raw',hex(raw(0xa00b3c1e,2)),'0x9782')

# Keep independently selected review anchors only; no duplicate full H05 listing.
anchors=[]
for at in sorted(set(int(c['va'],16) for c in checks)):
    i=decoded[at]
    anchors.append(dict(va=hex(at),file_offset=hex(at-BASE),bytes=bytes(i.bytes).hex(),asm=i.mnemonic+' '+i.op_str))
result=dict(status='passed',source=str(ROM),mapping='file_offset = VA - 0x9ffff000',
    static_only=True,decoded_windows=len(spans),decoded_instructions=len(decoded),
    decoded_bytes=sum(e-s for s,e in spans),raw_checks=len(checks),checks=checks,anchors=anchors,
    limitations=['No shared REA target/database opened or changed','No new REA Evidence ID',
                 'No firmware execution, emulation, build, network or historical replay',
                 'Constructor remainder and normal navigation delivery of DELETE not recovered'])
texts={}
for at in [0xa01c42a0,0xa037bce8,0xa01c3b98,0xa06130bc,0xa01c3cb4,0xa01c3ccc,0xa0564a9c]:
    start=at-BASE
    content=data[start:data.index(0,start)]
    texts[hex(at)]={'file_offset':hex(start),'hex':content.hex(),'utf8':content.decode('utf-8')}
result['independently_read_strings']=texts
(OUT/'review-evidence.json').write_text(json.dumps(result,ensure_ascii=False,indent=2),encoding='utf-8')
(OUT/'anchors.txt').write_text('\n'.join(f"{r['va']} file+{r['file_offset']} {r['bytes']} {r['asm']}" for r in anchors)+'\n',encoding='utf-8')
print(json.dumps({k:result[k] for k in ['status','decoded_windows','decoded_instructions','decoded_bytes','raw_checks']}))
