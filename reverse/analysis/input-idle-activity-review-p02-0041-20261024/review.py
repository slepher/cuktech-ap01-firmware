"""P02: independent original-ROM fields only; no P01 verifier or target execution."""
from pathlib import Path
import json

ROOT=Path('D:/Documents/PlatformIO/Projects/cuktech-ap01-firmware')
ROM=(ROOT/'roms/0041/ap01-1.0.2_0041.bin').read_bytes()
BASE=0x9ffff000
OUT=Path(__file__).resolve().parent
records=[]

def sign(v,n):
    return v-(1<<n) if v&(1<<(n-1)) else v

def u(pc,n=4):
    return int.from_bytes(ROM[pc-BASE:pc-BASE+n],'little')

def accept(pc,n,actual,expected,meaning):
    assert actual==expected,(hex(pc),actual,expected)
    records.append({'pc':hex(pc),'raw':ROM[pc-BASE:pc-BASE+n].hex(),'fields':actual,'meaning':meaning})

def upper(pc,rd,base,meaning):
    w=u(pc)
    accept(pc,4,[w&127,(w>>7)&31,w&0xfffff000],[0x37,rd,base],meaning)

def itype(pc,op,f3,rd,rs1,imm,meaning):
    w=u(pc)
    accept(pc,4,[w&127,(w>>12)&7,(w>>7)&31,(w>>15)&31,sign(w>>20,12)],[op,f3,rd,rs1,imm],meaning)

def stype(pc,f3,rs1,rs2,imm,meaning):
    w=u(pc)
    d=sign(((w>>25)<<5)|((w>>7)&31),12)
    accept(pc,4,[w&127,(w>>12)&7,(w>>15)&31,(w>>20)&31,d],[0x23,f3,rs1,rs2,imm],meaning)

def direct(pc,rd,target,meaning):
    w=u(pc)
    d=((w>>31)<<20)|(((w>>12)&255)<<12)|(((w>>20)&1)<<11)|(((w>>21)&1023)<<1)
    accept(pc,4,[w&127,(w>>7)&31,pc+sign(d,21)],[0x6f,rd,target],meaning)

upper(0xa00afd52,22,0x62fc4000,'producer s6 global high base')
itype(0xa00afd56,0x13,0,27,22,0x2c,'s11=62fc402c')
w=u(0xa00afd5a,2)
accept(0xa00afd5a,2,[w&3,w>>13,(w>>7)&31,sign((((w>>12)&1)<<5)|((w>>2)&31),6)],[1,2,15,1],'C.LI a5,1')
stype(0xa00afd5c,0,27,15,14,'SB a5 to s11+0e = activity byte62fc403a')
direct(0xa00afd60,1,0xa00a769a,'inherited wake wrapper target')

upper(0xa00af78a,18,0x62fc4000,'consumer s2 global high base, distinct from borrowed app')
itype(0xa00af79a,0x13,0,18,18,0x2c,'s2=62fc402c')
itype(0xa00afa78,3,4,15,18,14,'first activity LBU')
upper(0xa00afa7c,9,0x62fcc000,'first counter high base')
itype(0xa00afa80,0x13,0,9,9,-0x33c,'s1=62fcbcc4')
w=u(0xa00afa8c,2)
d=(((w>>12)&1)<<8)|(((w>>10)&3)<<3)|(((w>>5)&3)<<6)|(((w>>3)&3)<<1)|(((w>>2)&1)<<5)
accept(0xa00afa8c,2,[w&3,w>>13,8+((w>>7)&7),0xa00afa8c+sign(d,9)],[1,6,15,0xa00afb42],'C.BEQZ first read to old ScreenOff path')
stype(0xa00afaa8,2,9,0,0,'first nonzero arm SW zero at62fcbcc4')
direct(0xa00afaac,1,0xa008b51a,'existing diagnostic call before second read')
itype(0xa00afab0,3,4,15,18,14,'second independent LBU of same activity byte')
upper(0xa00afab4,9,0x62fcc000,'second counter high base')
itype(0xa00afab8,0x13,0,9,9,-0x338,'s1=62fcbcc8')
w=u(0xa00afabc)
d=((w>>31)<<12)|(((w>>7)&1)<<11)|(((w>>25)&63)<<5)|(((w>>8)&15)<<1)
accept(0xa00afabc,4,[w&127,(w>>12)&7,(w>>15)&31,(w>>20)&31,0xa00afabc+sign(d,13)],[0x63,0,15,0,0xa00afbec],'BEQ second read zero to old ScreenSave path')
stype(0xa00afac0,2,9,0,0,'second nonzero arm SW zero at62fcbcc8')
stype(0xa00afac4,0,18,0,14,'then SB zero activity, not before second counter')
direct(0xa00afac8,0,0xa00af2a8,'JAL x0 common tail; not a call')

identities={'producer_activity':hex(0x62fc4000+0x2c+14),'consumer_activity':hex(0x62fc4000+0x2c+14),'counter_first':hex(0x62fcc000-0x33c),'counter_second':hex(0x62fcc000-0x338)}
assert identities=={'producer_activity':'0x62fc403a','consumer_activity':'0x62fc403a','counter_first':'0x62fcbcc4','counter_second':'0x62fcbcc8'}
assert u(0xa00afa78)==u(0xa00afab0)
assert 0xa00afaa8<0xa00afaac<0xa00afab0<0xa00afabc<0xa00afac0<0xa00afac4
result={'status':'PASS','baseline':'a09959e','reviewed':'P01','sparse_records':len(records),'records':records,'identities':identities,'limits':['Original ROM field decode; no P01 script or JSON used as producer evidence','No target, SIM, build, replay, input, model, device or external service execution','Timer registration, thresholds, wake and long press inherited, not re-reviewed','Two LBU instructions separated by a call; no cross-call flag stability assumed','No all-writer, full callback, actual cadence or complete ROM claim; new functionality=0']}
(OUT/'review-result.json').write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
print(json.dumps({'status':'PASS','sparse_records':len(records),'JAL_targets':3,'B_and_CB_targets':2}))
