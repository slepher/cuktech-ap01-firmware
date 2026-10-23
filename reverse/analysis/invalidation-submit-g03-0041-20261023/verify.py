"""Static ROM extraction/contract assertions; never executes firmware or model."""
from pathlib import Path
import json,re
from explore import rows,ROM,BASE
OUT=Path(__file__).resolve().parent
SOURCE=Path('D:/Documents/PlatformIO/Projects/cuktech-ap01-firmware')
spans=[
 ('submit',0xa00ddbf6,0xa00dddf4),
 ('width',0xa0080e3e,0xa0080e6c),('height',0xa0080e6c,0xa0080e9a),
 ('copy4',0xa008b43a,0xa008b456),('contains',0xa00894aa,0xa008954c),
 ('event',0xa00814f4,0xa0081554),('dispatch',0xa008acfa,0xa008adf4),
 ('overlap',0xa0089472,0xa00894aa),('area-size',0xa008928c,0xa00892ac),
 ('consumer-record-flow',0xa00e0ac8,0xa00e1294),
 ('zero-wrapper',0xa0080d8e,0xa0080da6),
 ('dispatch-cleanup',0xa008ac38,0xa008acfa),
 ('vector-slot-normal',0xa00ecd68,0xa00ecd76),
 ('copy16-entry',0xa000589c,0xa00058aa),('copy16-alignment',0xa000592c,0xa0005950),
 ('copy16-word-loop',0xa0005992,0xa00059d0),('copy16-return',0xa0005916,0xa0005918),
 ('fill',0xa0024906,0xa00249c4)]
wins=[]; allrows={};checks=[]
for name,start,end in spans:
 r=list(rows(start,end));assert int(r[-1]['address'],16)+len(bytes.fromhex(r[-1]['bytes']))==end
 assert not any(x['op']=='UNKNOWN' for x in r),name
 for x in r:allrows[int(x['address'],16)]=x
 wins.append(dict(name=name,start=hex(start),end_exclusive=hex(end),instructions=r))
def check(a,op,arg):
 r=allrows[a];assert (r['op'],r['operands'])==(op,arg),(hex(a),r)
 checks.append(dict(address=hex(a),op=op,operands=arg))
def dest(a,t):
 assert allrows[a]['target']==hex(t),(hex(a),allrows[a]);checks.append(dict(address=hex(a),target=hex(t)))
for a,op,arg in [
 (0xa00ddc7e,'c.lw','a5, 8(s1)'),(0xa00ddc82,'lhu','a4, 0x32(a5)'),
 (0xa00ddc94,'c.li','a2, 5'),(0xa00ddc96,'c.li','a1, 5'),
 (0xa00ddcbc,'lhu','s2, 0x3e(s1)'),(0xa00ddcc0,'andi','s2, s2, 0x400'),
 (0xa00ddd08,'sw','zero, -0x40(s0)'),(0xa00ddd0c,'sw','zero, -0x3c(s0)'),
 (0xa00ddd16,'sw','a0, -0x38(s0)'),(0xa00ddd22,'sw','a0, -0x34(s0)'),
 (0xa00ddd38,'lbu','a4, 0x40(s1)'),(0xa00ddd46,'c.andi','a5, -8'),
 (0xa00ddd50,'ori','a5, a5, 7'),(0xa00ddd58,'lbu','a4, 0x3d(s1)'),
 (0xa00ddd64,'addi','a1, s0, -0x40'),(0xa00ddd68,'addi','a0, s1, 0x44'),
 (0xa00ddd72,'sw','a5, 0x264(s1)'),(0xa00ddd76,'c.li','a2, 0'),
 (0xa00ddd78,'addi','a1, zero, 0x38'),(0xa00ddd90,'addi','a2, s0, -0x30'),
 (0xa00ddd94,'addi','a1, zero, 0x35'),(0xa00ddda4,'lw','s3, 0x264(s1)'),
 (0xa00dddac,'c.li','a5, 0x1f'),(0xa00dddb6,'sw','zero, 0x264(s1)'),
 (0xa00dddbe,'lw','a0, 0x264(s1)'),(0xa00dddce,'lw','a5, 0x264(s1)'),
 (0xa00ddde0,'c.add','a1, s1'),(0xa00ddde2,'addi','a0, s0, -0x30'),
 (0xa0081516,'sw','s1, -0x2c(s0)'),(0xa008151a,'sw','s1, -0x28(s0)'),
 (0xa0081522,'sw','a2, -0x1c(s0)'),(0xa008152e,'sw','s2, -0x24(s0)'),
 (0xa008ad92,'sw','a5, 0xc(s3)'),(0xa008ad98,'c.jalr','a5'),
 (0xa008ad9e,'andi','s1, a5, 2'),(0xa008adae,'c.li','s1, 1'),
 (0xa008add8,'c.mv','a0, s1'),(0xa008adf0,'c.li','s1, 1'),
 (0xa00e0bba,'sw','zero, 0x264(a5)'),(0xa00e0d08,'blt','s3, a4, 0x356'),
 (0xa00e0d40,'jal','-0x5ffb2'),(0xa00e0d54,'sw','zero, 0x264(a5)'),
 (0xa00e0e10,'sb','s7, 0x244(a5)'),(0xa00e1090,'lw','s9, 0x44(a4)'),
 (0xa00e1094,'lw','s5, 0x48(a4)'),(0xa00e1098,'lw','s8, 0x4c(a4)'),
 (0xa00e109c,'lw','s4, 0x50(a4)'),(0xa00e1240,'c.add','a0, a5'),
]:check(a,op,arg)
for a,t in [(0xa00ddd9a,0xa00814f4),(0xa00ddda0,0xa00ddd82),
 (0xa00ddda8,0xa00dddd6),(0xa00dddb2,0xa00dddbe),(0xa00dddea,0xa00ddd82),
 (0xa00dddca,0xa008b43a),(0xa00dddd4,0xa00ddd72),
 (0xa00e0d94,0xa00e0e14),(0xa00e0dfe,0xa00e0e14),
 (0xa00e0e08,0xa008b43a),(0xa00e1086,0xa00e121e),
 (0xa00e1242,0xa00e1148),(0xa00e1148,0xa00e082e),
 (0xa00e1282,0xa00e0d36),(0xa0081532,0xa008acfa),(0xa0081544,0xa008acfa)]:dest(a,t)
dest(0xa008ada2,0xa008adae)
model=(SOURCE/'evidence/rea-0041-20261017/ghidra/Ghidra/Processors/RISCV/data/languages/ap01thead2.sinc').read_text()
constructors={}
for prefix in [':th.extu rd,rs1,15,0 ',':th.extu rd,rs1,15,15 ',':th.mvnez ',':th.mveqz ',':th.lrbu ',':th.srw ',':th.mula ',':th.lwia ',':th.swia ']:
 pos=model.index(prefix);end=model.index('\n}',pos)+2;constructors[prefix]=model[pos:end]
for a,rd,rs1,hi,lo in [(0xa00dddee,18,18,15,0),(0xa00e0e34,20,20,15,0),(0xa008ad78,13,15,15,15)]:
 w=int.from_bytes(bytes.fromhex(allrows[a]['bytes']),'little')
 assert ((w>>7)&31,(w>>15)&31,w>>26,(w>>20)&63)==(rd,rs1,hi,lo)
 checks.append(dict(address=hex(a),word=hex(w),rd=rd,rs1=rs1,hi=hi,lo=lo))
for a,rd,rs1,f3,top in [(0xa0005992,14,11,4,11),(0xa0005998,14,16,5,11)]:
 w=int.from_bytes(bytes.fromhex(allrows[a]['bytes']),'little')
 assert ((w>>7)&31,(w>>15)&31,(w>>12)&7,w>>27)==(rd,rs1,f3,top)
 checks.append(dict(address=hex(a),word=hex(w),rd=rd,rs1=rs1,f3=f3,top=top))
strings={}
for a in [0xa0569c48,0xa056a3a8,0xa056a360,0xa0569e5c]:
 strings[hex(a)]=ROM[a-BASE:].split(b'\0')[0].decode()
summary=dict(windows=len(wins),bytes=sum(e-s for _,s,e in spans),instructions=len(allrows),checks=len(checks),vendor_words=sum(r['op']=='TH' for r in allrows.values()))
doc=dict(method='Static extraction, no firmware execution or REA target mutation',source=str(SOURCE/'roms/0041/ap01-1.0.2_0041.bin'),mapping='offset=VA-0x9ffff000',summary=summary,windows=wins,checks=checks,model_source=str(SOURCE/'evidence/rea-0041-20261017/ghidra/Ghidra/Processors/RISCV/data/languages/ap01thead2.sinc'),model_constructors=constructors,strings=strings)
(OUT/'evidence.json').write_text(json.dumps(doc,indent=2),encoding='utf-8')
(OUT/'instructions.txt').write_text('\n'.join((f"{r['address']} off={r['offset']:#x} {r['bytes']} {r['op']} {r['operands']}"+(f" => {r['target']}" if r['target'] else '')).rstrip() for win in wins for r in win['instructions'])+'\n',encoding='utf-8')
print(json.dumps(dict(result='passed',**summary)))
