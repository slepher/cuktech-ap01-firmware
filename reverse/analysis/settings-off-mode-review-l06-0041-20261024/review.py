"""L06 independent sparse field review; no target or author's script execution."""
from pathlib import Path
import json

BASE=0x9ffff000
ROOT=Path('D:/Documents/PlatformIO/Projects/cuktech-ap01-firmware')
ROM=(ROOT/'roms/0041/ap01-1.0.2_0041.bin').read_bytes()
OUT=Path(__file__).resolve().parent
records=[]

def sx(n,bits):
    return n-(1<<bits) if n&(1<<(bits-1)) else n

def word(pc,n=4):
    return int.from_bytes(ROM[pc-BASE:pc-BASE+n],'little')

def check(pc,n,actual,expected,meaning):
    assert actual==expected,(hex(pc),actual,expected)
    records.append({'pc':hex(pc),'raw':ROM[pc-BASE:pc-BASE+n].hex(),'fields':actual,'meaning':meaning})

def itype(pc,op,f3,rd,rs1,imm,meaning):
    w=word(pc)
    check(pc,4,[w&127,w>>12&7,w>>7&31,w>>15&31,sx(w>>20,12)],[op,f3,rd,rs1,imm],meaning)

def cli(pc,rd,imm,meaning):
    w=word(pc,2)
    check(pc,2,[w&3,w>>13,w>>7&31,sx(((w>>12&1)<<5)|(w>>2&31),6)],[1,2,rd,imm],meaning)

def clw(pc,rd,rs1,imm,meaning):
    w=word(pc,2)
    offset=((w>>5&1)<<6)|((w>>10&7)<<3)|((w>>6&1)<<2)
    check(pc,2,[w&3,w>>13,8+(w>>2&7),8+(w>>7&7),offset],[0,2,rd,rs1,imm],meaning)

def jal(pc,target,meaning):
    w=word(pc)
    offset=((w>>31)<<20)|((w>>12&255)<<12)|((w>>20&1)<<11)|((w>>21&1023)<<1)
    check(pc,4,[w&127,w>>7&31,pc+sx(offset,21)],[0x6f,1,target],meaning)

cli(0xa00fe9f0,10,3,'first caller value=3')
itype(0xa00fea06,3,4,10,20,3,'second caller LBU a0,3(s4); shared s4 base inherited L04')
for pc,flag in [(0xa00fe9f6,0),(0xa00fea0e,1)]:
    itype(pc,3,2,15,8,-0x58,'load existing UI object pointer after setter; no return test')
    cli(pc+4,11,flag,'display flag paired to caller')
    clw(pc+6,10,15,8,'overwrite a0 before display call')

w=word(0xa00ab4a8)
check(0xa00ab4a8,4,[w&127,w>>7&31,w&0xfffff000],[0x37,15,0x62fc9000],'G high base')
itype(0xa00ab4ac,0x13,0,15,15,0x98,'G=62fc9098')
itype(0xa00ab4b0,3,4,14,15,3,'old G+3 read unsigned byte')
w=word(0xa00ab4b4)
offset=((w>>31)<<12)|((w>>7&1)<<11)|((w>>25&63)<<5)|((w>>8&15)<<1)
check(0xa00ab4b4,4,[w&127,w>>12&7,w>>15&31,w>>20&31,0xa00ab4b4+sx(offset,13)],[0x63,0,14,10,0xa00ab4d6],'BEQ old U8 vs full incoming a0; equal bypasses publication')
w=word(0xa00ab4c0)
offset=sx(((w>>25)<<5)|(w>>7&31),12)
check(0xa00ab4c0,4,[w&127,w>>12&7,w>>15&31,w>>20&31,offset],[0x23,0,15,10,3],'SB incoming low byte to G+3')
cli(0xa00ab4c4,10,4,'notification reason=4')
for pc,target,meaning in [(0xa00fe9f2,0xa00ab4a8,'constant caller to helper'),(0xa00fea0a,0xa00ab4a8,'byte caller to helper'),(0xa00fe9fe,0xa018f232,'constant caller display target'),(0xa00fea16,0xa018f232,'byte caller display target'),(0xa00ab4c6,0xa00a5bbe,'known notification follows SB'),(0xa00ab4ca,0xa00ab274,'known writer follows notification')]:
    jal(pc,target,meaning)

# Restore-only difference arm and direct equality return; no stable status assignment.
for pc,rd,offset in [(0xa00ab4ce,1,12),(0xa00ab4d0,8,8)]:
    w=word(pc,2)
    immediate=((w>>12&1)<<5)|((w>>4&7)<<2)|((w>>2&3)<<6)
    check(pc,2,[w&3,w>>13,w>>7&31,immediate],[2,2,rd,offset],'C.LWSP restore')
w=word(0xa00ab4d2,2)
check(0xa00ab4d2,2,[w&3,w>>13,w>>7&31,sx(((w>>12&1)<<5)|(w>>2&31),6)],[1,0,2,16],'C.ADDI sp restore')
for pc in (0xa00ab4d4,0xa00ab4d6):
    w=word(pc,2)
    check(pc,2,[w&3,w>>12,w>>7&31,w>>2&31],[2,8,1,0],'C.JR ra; no return-status assignment')

result={'status':'PASS','baseline':'b0b1df1','reviewed':'L05','records':records,'sparse_records':len(records),'limits':['No L05 verifier execution/import','L03/L04 notification/writer internals inherited, not rechecked','No target/SIM/model/build/replay/device/service execution','No persistent-success or complete settings claim','New recovered functionality=0']}
(OUT/'review-result.json').write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
print(json.dumps({'status':'PASS','sparse_records':len(records),'call_targets':6,'branches':1}))
