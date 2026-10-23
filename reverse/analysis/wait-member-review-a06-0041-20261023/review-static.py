"""A06 independent bounded ROM review; never executes target instructions."""
import json
from pathlib import Path
from capstone import Cs, CS_ARCH_RISCV, CS_MODE_RISCV32, CS_MODE_RISCVC, __version__
HERE = Path(__file__).resolve().parent
ROM = Path('D:/Documents/PlatformIO/Projects/cuktech-ap01-firmware/roms/0041/ap01-1.0.2_0041.bin')
BASE = 0x9ffff000
raw = ROM.read_bytes()
old = json.loads((HERE.parent/'wait-member-writer-a05-0041-20261023/instruction-evidence.json').read_text())
md = Cs(CS_ARCH_RISCV, CS_MODE_RISCV32 | CS_MODE_RISCVC)
checks = []
def sign(x, n): return x - (1 << n) if x >> (n-1) else x
def word(pc, n=4): return int.from_bytes(raw[pc-BASE:pc-BASE+n], 'little')
def check(pc, label, actual, expected):
    assert actual == expected, (hex(pc), label, actual, expected)
    checks.append(dict(pc=hex(pc), check=label, actual=actual))
def store(pc, rs1, rs2, imm):
    w = word(pc)
    check(pc, 'RV32 word-store fields', [w&127,(w>>12)&7,(w>>15)&31,(w>>20)&31,sign(((w>>25)<<5)|((w>>7)&31),12)], [35,2,rs1,rs2,imm])
def addi(pc, rd, rs1, imm):
    w = word(pc)
    check(pc, 'RV32 ADDI fields', [w&127,(w>>12)&7,(w>>7)&31,(w>>15)&31,sign(w>>20,12)], [19,0,rd,rs1,imm])
def cb(pc, neq, rs1, target):
    w = word(pc,2)
    off = ((w>>12&1)<<8)|((w>>10&3)<<3)|((w>>5&3)<<6)|((w>>3&3)<<1)|((w>>2&1)<<5)
    check(pc, 'compressed zero branch fields/target', [w&3,w>>13,8+(w>>7&7),pc+sign(off,9)], [1,7 if neq else 6,rs1,target])
def cj(pc, target):
    w = word(pc,2)
    off = ((w>>12&1)<<11)|((w>>11&1)<<4)|((w>>9&3)<<8)|((w>>8&1)<<10)|((w>>7&1)<<6)|((w>>6&1)<<7)|((w>>3&7)<<1)|((w>>2&1)<<5)
    check(pc, 'compressed jump fields/target', [w&3,w>>13,pc+sign(off,12)], [1,5,target])
def call(pc, target, pair=False):
    w = word(pc)
    if pair:
        v=word(pc+4)
        check(pc, 'AUIPC/JALR opcodes and ra registers', [w&127,w>>7&31,v&0x707f,v>>7&31,v>>15&31], [23,1,103,1,1])
        dst=(pc+sign(w&0xfffff000,32)+sign(v>>20,12))&0xfffffffe
    else:
        check(pc, 'JAL opcode/rd', [w&127,w>>7&31], [111,1])
        off=((w>>31)<<20)|((w>>12&255)<<12)|((w>>20&1)<<11)|((w>>21&1023)<<1)
        dst=(pc+sign(off,21))&0xffffffff
    check(pc, 'call target', hex(dst), hex(target))
windows=[]
for win in old['windows']:
    inst=[]
    for item in win['instructions']:
        pc=int(item['pc'],16); b=bytes.fromhex(item['bytes'])
        check(pc,'A05 bytes equal original ROM',raw[pc-BASE:pc-BASE+len(b)].hex(),b.hex())
        i=next(md.disasm(b,pc,1))
        check(pc,'instruction extent',i.size,len(b))
        inst.append(dict(pc=hex(pc),bytes=b.hex(),asm=i.mnemonic+' '+i.op_str))
    windows.append(dict(start=win['start'],end_exclusive=win['end_exclusive'],instructions=inst))
for pc,target in [(0xa00632ae,0xa0058386),(0xa00632ba,0xa002fcc8),(0xa00632cc,0xa0024906),(0xa00632e4,0xa0058386),(0xa0063318,0xa00b7bc0),(0xa0197eda,0xa01a8d2e),(0xa01a8d50,0xa01a4468)]: call(pc,target)
for pc,target in [(0xa0063306,0xa0197ebc),(0xa0063342,0xa0197f02),(0xa0197ecc,0xa002fcc8),(0xa0197ee2,0xa002e14e),(0xa01a8d3a,0xa0026844),(0xa01a8d5e,0xa00267c0)]: call(pc,target,True)
for args in [(0xa00632d2,26,15,8),(0xa00632da,26,15,4),(0xa00632e8,26,10,0),(0xa00632f6,26,0,12),(0xa00632fa,26,0,16),(0xa00632fe,26,15,20),(0xa006332c,23,26,8),(0xa0197ef8,18,9,0)]: store(*args)
for args in [(0xa00632b6,10,0,32),(0xa00632c6,12,0,32),(0xa00632de,11,0,33),(0xa0063302,10,26,24),(0xa0063314,10,26,28),(0xa0063332,13,13,-768),(0xa0063336,12,12,-1722),(0xa006333a,11,11,1732),(0xa006333e,10,23,4)]: addi(*args)
for args in [(0xa00632a8,True,15,0xa0063386),(0xa00632b4,False,10,0xa0063382),(0xa00632c0,True,10,0xa00632c6),(0xa00632ec,True,10,0xa00632f2),(0xa006330e,False,10,0xa0063314),(0xa006331c,False,10,0xa0063322),(0xa006334a,False,10,0xa006337e),(0xa0197ed4,False,10,0xa0197efe),(0xa0197ede,False,10,0xa0197ef8),(0xa01a8d38,True,10,0xa01a8d50)]: cb(*args)
for args in [(0xa0197efc,0xa0197eec),(0xa0197f00,0xa0197eec),(0xa01a8d6a,0xa01a8d44)]: cj(*args)
w=word(0xa01a8d56)
off=((w>>31)<<12)|((w>>7&1)<<11)|((w>>25&63)<<5)|((w>>8&15)<<1)
check(0xa01a8d56,'BGE a0,zero target', [w&127,w>>12&7,w>>15&31,w>>20&31,0xa01a8d56+sign(off,13)], [99,5,10,0,0xa01a8d44])
check(0xa01a8d5a,'SUB s1,zero,s1 fields',[word(0xa01a8d5a)&127,word(0xa01a8d5a)>>7&31,word(0xa01a8d5a)>>15&31,word(0xa01a8d5a)>>20&31,word(0xa01a8d5a)>>25],[51,9,0,9,32])
# Exact compressed register moves/constants and errno word-store encoding.
for pc,expected in [(0xa00632b2,'aa8b'),(0xa00632be,'2a8d'),(0xa0063330,'5e87'),(0xa0063322,'8566'),(0xa0197ec8,'2a89'),(0xa0197eca,'3145'),(0xa0197ed6,'8145'),(0xa0197ed8,'aa84'),(0xa0197ee0,'2685'),(0xa0197eea,'7955'),(0xa0197efe,'7d55'),(0xa01a8d48,'2685'),(0xa01a8d66,'04c1'),(0xa01a8d68,'fd54')]: check(pc,'decisive compressed encoding',raw[pc-BASE:pc-BASE+2].hex(),expected)
result=dict(task='A06',method='independent original-ROM bounded review; no execution',capstone=__version__,windows=windows,checks=checks,decision='accepted within scope; no A05 semantic correction',limits=['No a0197f02 ABI/body review','No new whole-ROM scan','No lower initialization or allocation semantics certified','No buzzer exited_sem connection'])
(HERE/'review-evidence.json').write_text(json.dumps(result,indent=2)+'\n',encoding='utf-8')
print('PASS',len(checks),'checks;',sum(len(w['instructions']) for w in windows),'instructions; 308 bytes')
