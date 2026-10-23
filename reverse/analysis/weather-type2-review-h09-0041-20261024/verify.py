"""H09 independent bounded RV32/RVC encoding review; ROM is data only."""
import json
from pathlib import Path

HERE = Path(__file__).resolve().parent
MAIN = Path('D:/Documents/PlatformIO/Projects/cuktech-ap01-firmware')
ROM = MAIN / 'roms/0041/ap01-1.0.2_0041.bin'
BASE = 0x9ffff000
rom = ROM.read_bytes()
checks = []

def sx(v, n):
    return (v ^ (1 << (n-1))) - (1 << (n-1))

def raw(a, n=4):
    return rom[a-BASE:a-BASE+n]

def word(a):
    return int.from_bytes(raw(a), 'little')

def ck(label, actual, expected, address=None, size=4):
    assert actual == expected, (label, actual, expected)
    row = dict(label=label, actual=actual, expected=expected)
    if address is not None:
        row.update(address=hex(address), offset=hex(address-BASE), bytes=raw(address,size).hex())
    checks.append(row)

def mem(a, store, reg, base, offset):
    w = word(a)
    imm = sx(((w >> 25) << 5 | ((w >> 7) & 31)) if store else w >> 20, 12)
    ck('SW' if store else 'LW', [w&127,(w>>12)&7,((w>>20)&31) if store else ((w>>7)&31),(w>>15)&31,imm],
       [35 if store else 3,2,reg,base,offset],a)

def jal(a, target):
    w=word(a)
    imm=((w>>31)<<20)|(((w>>12)&255)<<12)|(((w>>20)&1)<<11)|(((w>>21)&1023)<<1)
    ck('JAL ra,target',[w&127,(w>>7)&31,a+sx(imm,21)],[111,1,target],a)

def mv(a, dst, src):
    h=int.from_bytes(raw(a,2),'little')
    ck('C.MV',[h&3,h>>12,(h>>7)&31,(h>>2)&31],[2,8,dst,src],a,2)

def li(a, dst, value):
    h=int.from_bytes(raw(a,2),'little')
    ck('C.LI',[h&3,h>>13,(h>>7)&31,sx(((h>>2)&31)|(((h>>12)&1)<<5),6)],[1,2,dst,value],a,2)

def addi(a, dst, src, value):
    w=word(a)
    ck('ADDI',[w&127,(w>>12)&7,(w>>7)&31,(w>>15)&31,sx(w>>20,12)], [19,0,dst,src,value],a)

def branch(a, funct3, rs1, rs2, target):
    w=word(a)
    imm=((w>>31)<<12)|(((w>>7)&1)<<11)|(((w>>25)&63)<<5)|(((w>>8)&15)<<1)
    ck('branch',[w&127,(w>>12)&7,(w>>15)&31,(w>>20)&31,a+sx(imm,13)],[99,funct3,rs1,rs2,target],a)

li(0xa005cfa4,10,20); jal(0xa005cfa6,0xa008e362); mv(0xa005cfaa,23,10)
addi(0xa005da90,10,0,136); jal(0xa005da94,0xa008e362)
# Retained context-save anchor, decoded independently below as C.MV s2,a0.
mv(0xa005da98,18,10)
li(0xa005e182,21,2)
for a,r,b,o in [(0xa005e204,21,23,0),(0xa005e208,18,23,4),(0xa005e20c,23,19,16)]: mem(a,True,r,b,o)
mem(0xa00ababa,False,18,10,4); mem(0xa00ababe,False,19,18,16)
branch(0xa00abac2,0,19,0,0xa00abb52); mem(0xa00abac6,False,9,19,4)
# C.LW: uimm[6]=h[5], [5:3]=h[12:10], [2]=h[6].
h=int.from_bytes(raw(0xa00abaca,2),'little')
off=(((h>>5)&1)<<6)|(((h>>10)&7)<<3)|(((h>>6)&1)<<2)
ck('C.LW timer before stores',[h&3,h>>13,8+((h>>2)&7),8+((h>>7)&7),off],[0,2,10,9,0x78],0xa00abaca,2)
clear=[0x24,0x1c,0,0xc,8,0x48,0x34,0x18,0x14,0x30,0x44,0x2c,0x4c,0x50,0x54,0x58,0x38,0x3c,0x40,4,0x10,0x5c,0x60,0x64,0x84]
for index, offset in enumerate(clear): mem(0xa00abacc+4*index,True,0,9,offset)
jal(0xa00abb30,0xa008ae58); mv(0xa00abb34,10,9); jal(0xa00abb36,0xa008ab8a)
ck('unregister LUI a0',word(0xa00abb3a),0xa00ab537,0xa00abb3a)
mv(0xa00abb3e,11,18); addi(0xa00abb40,10,10,0x754); jal(0xa00abb44,0xa00b3abe)
mv(0xa00abb48,10,19); jal(0xa00abb4a,0xa008ab8a); mem(0xa00abb4e,True,0,18,16)
# Entry mask, comparison and no-code early return are bounded ABI anchors.
ck('C.LW a5,event+8',raw(0xa00aba9c,2).hex(),'1c45',0xa00aba9c,2)
ck('mask construction and AND',raw(0xa00aba9e,6).hex(),'61777d17f98f',0xa00aba9e,6)
addi(0xa00abaa4,14,0,0x29); branch(0xa00abaa8,1,15,14,0xa00abb60)
ck('other-event return',raw(0xa00abb60,2).hex(),'8280',0xa00abb60,2)
result=dict(status='passed',source=str(ROM),mapping_base=hex(BASE),checks=checks,clear_offsets=clear,
            inherited_only=['pass3 registration/hookup','weather-complete evidence[18] callback/classification/display','H02 registry ABI','E06 timer/free ABI'],
            counts=dict(checks=len(checks),clear_words=len(clear),new_functionality=0),
            limits=['No target execution or REA session','No callback re-export or 78-instruction recheck','Timer initialization and upper DELETE trigger remain unknown'])
(HERE/'review-evidence.json').write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
print(json.dumps(result['counts']))
