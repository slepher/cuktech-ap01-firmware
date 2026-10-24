"""P-R12 independent stdlib-only bounded ROM field audit. No imported decoder or execution."""
import json
from pathlib import Path
from datetime import datetime, timezone
ROOT=Path('D:/Documents/PlatformIO/Projects/cuktech-ap01-firmware')
HERE=Path(__file__).resolve().parent
BASE=0x9ffff000
rom=(ROOT/'roms/0041/ap01-1.0.2_0041.bin').read_bytes()
author=json.loads((ROOT/'reverse/analysis/history-reader-p12-0041-20261024/static-evidence.json').read_text(encoding='utf8'))
checks=[]
def ck(label,actual,expected):
    assert actual==expected,(label,actual,expected)
    checks.append({'label':label,'actual':actual})
def word(pc,n=4):return int.from_bytes(rom[pc-BASE:pc-BASE+n],'little')
def sx(x,n):return x-(1<<n) if x>>(n-1) else x
def fields(pc):
    w=word(pc)
    return (w&127,(w>>7)&31,(w>>12)&7,(w>>15)&31,(w>>20)&31,w>>27,(w>>25)&3)
def itype(pc):
    w=word(pc);return (w&127,(w>>7)&31,(w>>12)&7,(w>>15)&31,sx(w>>20,12))
def store(pc):
    w=word(pc);return (w&127,(w>>12)&7,(w>>15)&31,(w>>20)&31,sx(((w>>25)<<5)|((w>>7)&31),12))
def jal(pc):
    w=word(pc);assert w&127==111
    imm=((w>>31)<<20)|(((w>>12)&255)<<12)|(((w>>20)&1)<<11)|(((w>>21)&1023)<<1)
    return pc+sx(imm,21)
def branch(pc):
    w=word(pc);assert w&127==99
    imm=((w>>31)<<12)|(((w>>7)&1)<<11)|(((w>>25)&63)<<5)|(((w>>8)&15)<<1)
    return ((w>>12)&7,(w>>15)&31,(w>>20)&31,pc+sx(imm,13))
def cmv(pc):
    w=word(pc,2);return (w&3,w>>12,(w>>7)&31,(w>>2)&31)
def clw(pc):
    w=word(pc,2);return (w&3,w>>13,8+((w>>2)&7),8+((w>>7)&7),(((w>>10)&7)<<3)|(((w>>6)&1)<<2)|(((w>>5)&1)<<6))
# All seven author spans are carriers to compare, not semantic oracles.
rows=0;bytecount=0
parent=json.loads((ROOT/'reverse/rehost/charge-complete-0041.json').read_text(encoding='utf8'))['records'][19]
old={int(line.split(':')[0],16) for line in parent['assembly']}
for win in author['windows']:
    pc=int(win['start'],16)
    for row in win['instructions']:
        raw=bytes.fromhex(row['hex']);n=4 if word(pc,2)&3==3 else 2
        assert pc==int(row['address'],16) and n==len(raw)
        assert rom[pc-BASE:pc-BASE+n]==raw
        if win['name']!='chart_glue':assert pc in old
        pc+=n;rows+=1;bytecount+=n
    assert pc==int(win['end_exclusive'],16)
ck('span byte agreement',bytecount,458)
ck('span instruction boundary agreement',rows,146)
for pc,v in [(0xa00f52b4,(2,8,23,10)),(0xa00f52b6,(2,8,9,11)),(0xa00a64f2,(2,8,9,11)),(0xa00a650a,(2,8,13,9))]:ck(hex(pc)+' c.mv',cmv(pc),v)
for pc,v in [(0xa00f575c,(11,15,1,9,15,0,1)),(0xa00f5a10,(11,15,1,9,15,0,1)),(0xa00f5a44,(11,10,4,25,21,20,1)),(0xa00a650c,(11,10,4,13,10,11,1)),(0xa00a39b6,(11,11,5,15,13,4,1))]:ck(hex(pc)+' private fields',fields(pc),v)
for pc,v in [(0xa00f5704,(19,15,7,15,1024)),(0xa00f570a,(3,14,5,9,420)),(0xa00f571a,(3,24,4,9,422)),(0xa00f5740,(3,22,4,15,96)),(0xa00f5760,(3,10,5,15,60)),(0xa00f5a14,(3,10,5,15,60)),(0xa00f5a34,(19,25,0,9,60)),(0xa00f5764,(19,11,0,25,60)),(0xa00f5a18,(19,11,0,26,60)),(0xa00f5a48,(19,11,0,22,60)),(0xa00a6522,(19,12,0,0,179)),(0xa00a651a,(3,13,2,8,-20))]:ck(hex(pc)+' I fields',itype(pc),v)
for pc,v in [(0xa00f5782,(35,0,15,24,96)),(0xa00f576e,(35,2,25,10,76)),(0xa00f5a22,(35,2,26,10,76)),(0xa00f5a52,(35,2,22,10,76)),(0xa00f5a76,(35,2,15,0,76)),(0xa00a6512,(35,2,8,13,-20)),(0xa00a39b2,(35,0,15,14,362)),(0xa00a39c2,(35,0,15,0,362))]:ck(hex(pc)+' S fields',store(pc),v)
for pc,v in [(0xa00f5744,(6,22,24,0xa00f5a04)),(0xa00f5748,(7,24,22,0xa00f577e)),(0xa00f577a,(4,21,26,0xa00f5758)),(0xa00f5a2e,(4,21,25,0xa00f5a0c)),(0xa00f5a40,(7,15,24,0xa00f577e)),(0xa00a64f4,(7,15,10,0xa00a650a))]:ck(hex(pc)+' branch fields',branch(pc),v)
for pc,target in [(0xa00f576a,0xa00a64e4),(0xa00f5a1e,0xa00a64e4),(0xa00f5a4e,0xa00a64e4),(0xa00a6502,0xa019c5d0),(0xa00a6516,0xa00925e0),(0xa00a6526,0xa0093a7c),(0xa00a6538,0xa00dbb68),(0xa00f53ce,0xa00a72ae)]:ck(hex(pc)+' J target',jal(pc),target)
ck('0xa00a64ee C cached maximum',clw(0xa00a64ee),(0,2,15,11,16))
for pc,v in [(0xa00a6510,(0,2,11,9,4)),(0xa00a651e,(0,2,11,9,4)),(0xa00a6520,(0,2,10,9,0)),(0xa00a652a,(0,2,14,9,24)),(0xa00a652c,(0,2,13,9,20)),(0xa00a652e,(0,2,10,9,8)),(0xa00a6530,(0,2,11,9,0)),(0xa00a6540,(0,2,10,9,16))]:ck(hex(pc)+' C load',clw(pc),v)
graph=json.loads((ROOT/'evidence/rea-0041-20261017/evidence/whole-rom-graph-20261023-4942.json').read_text(encoding='utf8'))['structuredContent']
ck('glue body',graph['normalized_result']['body']['ranges'],[{'start':'0xa00a64e4','end':'0xa00a6547'}])
ck('glue digest',graph['analysis_profile']['digest'],'b6368dd18431e8113aa5026c713d41e648ab0f6ddd9421ff6c4a49e23b3cd2f3')
model=(ROOT/'evidence/rea-0041-20261017/processor/data/languages/ap01thead2.sinc').read_text(encoding='utf8')
# Text provenance only; never execute or compile this model.
for name in ('addsl','lrhu','lwia','srh'):
    body=model.split(':th.'+name+' ',1)[1].split('}',1)[0]
    checks.append({'label':'read existing model '+name,'body':body.strip()})
out={'observed_utc':datetime.now(timezone.utc).isoformat(),'method':'independent stdlib byte and field extraction; no author imports, Capstone, REA session, target or model execution','author_spans_bytes':bytecount,'author_spans_instructions':rows,'extra_writer_bytes':12,'checks':checks,'correction':{'address_order':['0xa00a39b2','0xa00a39b6','0xa00a39c2'],'finding':'cursor next store precedes old-slot sample store; conditional cursor wrap follows. Reader sequence applies after producer completion; no atomic publication claim.'},'limits':['private opcode meaning conditional on existing bound model','no chart library internals','no T reader, creator/reset or final release closure']}
(HERE/'independent-checks.json').write_text(json.dumps(out,ensure_ascii=False,indent=2)+'\n',encoding='utf8')
print(len(checks),'independent checks PASS;',bytecount,'author bytes;',rows,'boundaries; 12 necessary writer bytes')
