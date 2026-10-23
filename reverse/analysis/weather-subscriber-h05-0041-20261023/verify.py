"""H05 bounded original-ROM static extraction; never executes target code."""
import json
from pathlib import Path
import capstone
HERE=Path(__file__).resolve().parent
MAIN=Path('D:/Documents/PlatformIO/Projects/cuktech-ap01-firmware')
BASE=0x9ffff000
rom=MAIN/'roms/0041/ap01-1.0.2_0041.bin'
b=rom.read_bytes()
md=capstone.Cs(capstone.CS_ARCH_RISCV,capstone.CS_MODE_RISCV32|capstone.CS_MODE_RISCVC)
spans=[('containing-prologue',0xa005cc1e,0xa005cc5a),('page-wrapper-creation',0xa005cfd8,0xa005cff8),('ctx-allocation-failure',0xa005e4e6,0xa005e524),('registration-ownership-event',0xa005e8d2,0xa005e90a),('weather-callback',0xa00abed2,0xa00abfe6),('weather-delete-hook',0xa00abb62,0xa00abbf6),('direct-icon-consumer',0xa019cbc0,0xa019cd14),('zero-alloc-wrapper',0xa008e362,0xa008e38c),('zero-fill-adapter',0xa0080d8e,0xa0080da6),('dispatch-ABI-contract',0xa00b3c14,0xa00b3c26)]
windows=[]; ins={}; checks=[]
for name,start,end in spans:
 rows=[];at=start
 while at<end:
  i=next(md.disasm(b[at-BASE:end-BASE],at,count=1),None)
  assert i is not None,hex(at)
  r=dict(address=hex(at),offset=hex(at-BASE),bytes=bytes(i.bytes).hex(),text=i.mnemonic+' '+i.op_str)
  rows.append(r);ins[at]=r;at+=i.size
 assert at==end
 windows.append(dict(name=name,start=hex(start),end_exclusive=hex(end),instructions=rows))
def word(a):return int.from_bytes(b[a-BASE:a-BASE+4],'little')
def sx(x,n):return (x^(1<<(n-1)))-(1<<(n-1))
def ck(name,actual,expected):
 assert actual==expected,(name,actual,expected)
 checks.append(dict(name=name,actual=actual,expected=expected))
def mem(a,opcode,rd_rs2,rs1,imm,f3):
 w=word(a); v=sx(((w>>25)<<5|((w>>7)&31)) if opcode==0x23 else w>>20,12)
 ck(hex(a)+' fields',[w&127,(w>>12)&7,((w>>20)&31) if opcode==0x23 else ((w>>7)&31),(w>>15)&31,v],[opcode,f3,rd_rs2,rs1,imm])
def jal(a,target):
 w=word(a);imm=((w>>31)<<20)|(((w>>12)&255)<<12)|(((w>>20)&1)<<11)|(((w>>21)&1023)<<1)
 ck(hex(a)+' JAL',[w&127,(w>>7)&31,a+sx(imm,21)],[0x6f,1,target])
for a,rd,off,f3 in [(0xa00abef2,18,28,2),(0xa00abef6,23,6,1),(0xa00abefc,24,8,1),(0xa00abf00,25,10,1),(0xa00abf04,21,14,5),(0xa00abf08,22,16,5),(0xa00abf0c,19,18,5),(0xa00abf10,20,20,5),(0xa00abf14,12,12,1)]:mem(a,3,rd,10,off,f3)
for a,t in [(0xa005e8dc,0xa00b3a68),(0xa00abf22,0xa0091ee4),(0xa00abf62,0xa0091ee4),(0xa00abf72,0xa0091ee4),(0xa00abf7a,0xa019cbc0),(0xa00abf86,0xa00a6d34),(0xa00abf94,0xa0091ee4),(0xa00abfa2,0xa0091ee4),(0xa00abbcc,0xa008ab8a),(0xa00abbda,0xa00b3abe),(0xa00abbe0,0xa008ab8a),(0xa005cfe4,0xa008e362),(0xa005e4ea,0xa008e362),(0xa005e51c,0xa008ab8a),(0xa019cbd0,0xa00a6998),(0xa019cbda,0xa00d9044),(0xa019cc40,0xa00ed560),(0xa019cc96,0xa00d8f7c),(0xa008e370,0xa002fcc8),(0xa008e37c,0xa0080d8e)]:jal(a,t)
for a,rs1,off in [(0xa00abb8c,10,0x1c),(0xa00abb90,10,0x34),(0xa00abb94,10,8),(0xa00abb98,10,0x10),(0xa00abb9c,10,0x14),(0xa00abba0,10,0),(0xa00abba4,10,0xc),(0xa00abba8,10,0x30),(0xa00abbac,10,0x28),(0xa00abbb0,10,0x2c),(0xa00abbb4,10,4),(0xa00abbb8,10,0x24),(0xa00abbbc,10,0x20),(0xa00abbc0,10,0x18),(0xa00abbc4,10,0x38),(0xa00abbc8,10,0x3c),(0xa00abbe4,9,0x10)]:mem(a,0x23,0,rs1,off,2)
for a,rs2,rs1,off in [(0xa005e8e2,15,24,0),(0xa005e8e6,18,24,4),(0xa005e8ee,24,21,0x10)]:mem(a,0x23,rs2,rs1,off,2)
def branch(a,f3,r1,r2,target):
 w=word(a);imm=((w>>31)<<12)|(((w>>7)&1)<<11)|(((w>>25)&63)<<5)|(((w>>8)&15)<<1)
 ck(hex(a)+' branch fields',[w&127,(w>>12)&7,(w>>15)&31,(w>>20)&31,a+sx(imm,13)],[0x63,f3,r1,r2,target])
branch(0xa00abed2,0,11,0,0xa00abfe4)
branch(0xa00abb6e,1,15,14,0xa00abbf4)
branch(0xa00abb84,0,18,0,0xa00abbe8)
# Exact compressed ABI moves/loads and frame-free argument sequencing.
for a,h in [(0xa005e8d6,0x85d6),(0xa00abbde,0x854a),(0xa00abbd4,0x85a6),(0xa00abef0,0x499c),(0xa00abefa,0x43c4),(0xa019cbce,0x852e),(0xa00abb88,0x00492503)]:
 ck(hex(a)+' original encoding',int.from_bytes(b[a-BASE:a-BASE+(4 if h>65535 else 2)],'little'),h)
# LUI+ADDI callback constants, event installer AUIPC/JALR.
for a,target in [(0xa005e8d2,0xa00abed2),(0xa00abbd0,0xa00abed2),(0xa005e8ea,0xa00abb62)]:
 w=word(a); add=word(a+6 if a in [0xa005e8d2,0xa00abbd0] else a+14)
 ck(hex(a)+' address constant',(w&0xfffff000)+sx(add>>20,12),target)
w=word(0xa005e8fe);j=word(0xa005e902)
ck('event callback installer',0xa005e8fe+(w&0xfffff000)+sx(j>>20,12),0xa01ad654)
# Raw branch and mask instructions, no guessed mnemonic interpretation.
ck('DELETE mask lui/addi',[ins[0xa00abb64]['bytes'],ins[0xa00abb66]['bytes']],['6177','7d17'])
ck('DELETE event immediate',sx(word(0xa00abb6a)>>20,12),0x29)
ck('ctx size immediate',sx(word(0xa005e4e6)>>20,12),0x44)
ck('wrapper allocation size compressed',ins[0xa005cfe2]['bytes'],'5145')
strings={}
for a in [0xa01c3b98,0xa01c42a0,0xa037bce8,0xa037a774,0xa01c3cb4,0xa01c3ccc,0xa0564a9c,0xa06130bc]:
 raw=b[a-BASE:b.index(0,a-BASE)];strings[hex(a)]=dict(bytes=raw.hex(),text=raw.decode('utf-8'))
# Resource literals selected by category in this specific setter (ROM pointers borrowed).
resources={1:0xa0251fd4,2:0xa063461c,3:0xa0633960,4:0xa0633f50,5:0xa06318b0,6:0xa06315bc,7:0xa0631f78,8:0xa0632308,9:0xa0632968,10:0xa0636644,11:0xa0636130,12:0xa06334ec,13:0xa06330b8,14:0xa0631c68,22:0xa0634fe4,23:0xa0635878}
for cat,at in {1:0xa019ccd8,2:0xa019cce2,3:0xa019ccec,4:0xa019cc1a,5:0xa019cc9c,6:0xa019cc36,7:0xa019ccc4,8:0xa019ccb0,9:0xa019ccba,10:0xa019cd0a,11:0xa019cc66,12:0xa019ccce,13:0xa019cc76,14:0xa019cca6,22:0xa019ccf6,23:0xa019cd00}.items():
 ck('category '+str(cat)+' ROM resource',(word(at)&0xfffff000)+sx(word(at+4)>>20,12),resources[cat])
ck('zero-fill adapter ABI',[ins[0xa0080d96]['bytes'],ins[0xa0080d98]['bytes']],['2e86','8145'])
record=dict(source=str(rom),base=hex(BASE),decoder=capstone.__version__,windows=windows,encoding_checks=checks,strings=strings,icon_category_resources={str(k):hex(v) for k,v in resources.items()},limitations=['Static original-byte analysis; no execution','Historical inventory identifies containing procedure; complete surrounding main/UI initialization not recovered','No new REA Evidence ID or mutable shared session'])
(HERE/'instruction-evidence.json').write_text(json.dumps(record,ensure_ascii=False,indent=2),encoding='utf-8')
(HERE/'instructions.txt').write_text('\n'.join(r['address']+' '+r['bytes']+' '+r['text'] for w in windows for r in w['instructions']),encoding='utf-8')
summary=dict(status='passed',windows=len(windows),bytes=sum(e-s for _,s,e in spans),instructions=len(ins),encoding_checks=len(checks),unknown_decodes=0)
(HERE/'review-index.json').write_text(json.dumps(summary,indent=2),encoding='utf-8');print(json.dumps(summary))
