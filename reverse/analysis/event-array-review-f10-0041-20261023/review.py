"""F10 old-conclusion review: bounded ROM fields, no target execution/export."""
import json
from pathlib import Path
ROOT = Path("D:/Documents/PlatformIO/Projects/cuktech-ap01-firmware")
OUT = Path(__file__).resolve().parent
ROM = (ROOT / "roms/0041/ap01-1.0.2_0041.bin").read_bytes()
BASE = 0x9ffff000
checks = []
def read(pc, n):
    return int.from_bytes(ROM[pc-BASE:pc-BASE+n], "little")
def signed(v, bits):
    return v - (1 << bits) if v & (1 << (bits-1)) else v
def verify(pc, label, got, expected):
    assert got == expected, (hex(pc), label, got, expected)
    checks.append({"pc": hex(pc), "claim": label, "decoded": got})
def std(pc):
    w = read(pc, 4)
    assert w & 3 == 3
    return w
# Standard encodings: independent opcode/register/immediate interpretation.
w = std(0xa00ecc76)
verify(0xa00ecc76, "owned unsigned byte load into s3", [w&127,(w>>12)&7,(w>>7)&31,(w>>15)&31,signed(w>>20,12)], [3,4,19,10,16])
w = std(0xa00ecc7a)
imm=((w>>31)<<12)|(((w>>7)&1)<<11)|(((w>>25)&63)<<5)|(((w>>8)&15)<<1)
verify(0xa00ecc7a,"nonzero owned branch",[w&127,(w>>12)&7,(w>>15)&31,(w>>20)&31,0xa00ecc7a+signed(imm,13)],[99,1,19,0,0xa00eccb0])
def clw(pc, dest, base, offset):
    h=read(pc,2)
    verify(pc,"compressed word load",[h&3,h>>13,8+((h>>2)&7),8+((h>>7)&7),((h>>10)&7)*8+((h>>6)&1)*4+((h>>5)&1)*64],[0,2,dest,base,offset])
def cmv(pc, dest, source):
    h=read(pc,2)
    verify(pc,"compressed register move",[h&3,h>>12,(h>>7)&31,(h>>2)&31],[2,8,dest,source])
cmv(0xa00eccb0,18,11)
clw(0xa00eccb2,11,10,12)
cmv(0xa00eccb4,9,10)
clw(0xa00eccb6,10,10,0)
w=std(0xa00eccb8)
verify(0xa00eccb8,"RV32 low word multiply",[w&127,(w>>25)&127,(w>>12)&7,(w>>7)&31,(w>>15)&31,(w>>20)&31],[51,1,0,11,18,11])
def jal(pc, target):
    w=std(pc)
    imm=((w>>31)<<20)|(((w>>12)&255)<<12)|(((w>>20)&1)<<11)|(((w>>21)&1023)<<1)
    verify(pc,"JAL ra target",[w&127,(w>>7)&31,pc+signed(imm,21)],[111,1,target])
jal(0xa00eccbc,0xa008c332)
def cb(pc, reg, target):
    h=read(pc,2)
    imm=(((h>>12)&1)<<8)|(((h>>10)&3)<<3)|(((h>>5)&3)<<6)|(((h>>3)&3)<<1)|(((h>>2)&1)<<5)
    verify(pc,"compressed nonzero branch",[h&3,h>>13,8+((h>>7)&7),pc+signed(imm,9)],[1,7,reg,target])
cb(0xa00eccc0,10,0xa00ecd02)
clw(0xa00ecd02,15,9,4)
h=read(0xa00ecd04,2)
verify(0xa00ecd04,"first publish data word",[h&3,h>>13,8+((h>>2)&7),8+((h>>7)&7),((h>>10)&7)*8+((h>>6)&1)*4+((h>>5)&1)*64],[0,6,10,9,0])
def sw(pc, offset):
    w=std(pc)
    imm=((w>>25)<<5)|((w>>7)&31)
    verify(pc,"publish capacity/count word",[w&127,(w>>12)&7,(w>>15)&31,(w>>20)&31,signed(imm,12)],[35,2,9,18,offset])
sw(0xa00ecd06,8)
w=std(0xa00ecd0a)
imm=((w>>31)<<12)|(((w>>7)&1)<<11)|(((w>>25)&63)<<5)|(((w>>8)&15)<<1)
verify(0xa00ecd0a,"unsigned new capacity >= old count",[w&127,(w>>12)&7,(w>>15)&31,(w>>20)&31,0xa00ecd0a+signed(imm,13)],[99,7,18,15,0xa00ecca0])
sw(0xa00ecd0e,4)
def cj(pc, target):
    h=read(pc,2)
    imm=(((h>>12)&1)<<11)|(((h>>11)&1)<<4)|(((h>>9)&3)<<8)|(((h>>8)&1)<<10)|(((h>>7)&1)<<6)|(((h>>6)&1)<<7)|(((h>>3)&7)<<1)|(((h>>2)&1)<<5)
    verify(pc,"compressed unconditional jump",[h&3,h>>13,pc+signed(imm,12)],[1,5,target])
cj(0xa00ecd12,0xa00ecca0)
cmv(0xa00ecca8,10,19)
verify(0xa00eccaa,"restore saved s3 only after move to return register",read(0xa00eccaa,2),0x49b2)
verify(0xa00eccae,"return through ra",read(0xa00eccae,2),0x8082)
h=read(0xa01b9510,2)
verify(0xa01b9510,"caller add capacity 4",[h&3,h>>13,(h>>7)&31,signed((((h>>12)&1)<<5)|((h>>2)&31),6)],[1,0,11,4])
cmv(0xa01b9512,10,9)
jal(0xa01b9514,0xa00ecc68)
cb(0xa01b9518,10,0xa01b94e8)
cj(0xa01b951a,0xa01b9504)
result={"classification":"independent review of old conclusions; new functionality 0","checks":checks,"limits":"No full function export; diagnostic/assert/realloc internals and inherited G03-G06 paths not reopened."}
(OUT / "review.json").write_text(json.dumps(result,ensure_ascii=False,indent=2)+"\n",encoding="utf-8")
print(json.dumps({"checks":len(checks),"new_functionality":0}))
