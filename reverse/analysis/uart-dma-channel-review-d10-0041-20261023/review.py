"""D10 independent bounded old-conclusion review; no firmware execution or re-export."""
from pathlib import Path
import json
from capstone import Cs, CS_ARCH_RISCV, CS_MODE_RISCV32, CS_MODE_RISCVC
OUT=Path(__file__).resolve().parent
ROM=Path('D:/Documents/PlatformIO/Projects/cuktech-ap01-firmware/roms/0041/ap01-1.0.2_0041.bin')
b=ROM.read_bytes(); BASE=0x9ffff000
old=json.loads((OUT.parent/'uart-dma-channel-d09-0041-20261023/instructions.json').read_text())
rows={int(r['va'],16):r for win in old['windows'] for r in win['instructions']}
c=Cs(CS_ARCH_RISCV,CS_MODE_RISCV32|CS_MODE_RISCVC)
checks=[]
def raw(a,n=4):return b[a-BASE:a-BASE+n]
def word(a):return int.from_bytes(raw(a),'little')
def check(label,actual,expected):
 assert actual==expected,(label,actual,expected)
 checks.append({'check':label,'passed':True})
def asm(a,expect):
 r=rows[a]; data=raw(a,len(bytes.fromhex(r['bytes'])))
 check(hex(a)+' retained bytes',data.hex(),r['bytes'])
 z=list(c.disasm(data,a));check(hex(a)+' instruction count',len(z),1)
 check(hex(a)+' normal decode',z[0].mnemonic+' '+z[0].op_str,expect)
def vendor(a,rd,rs1,rs2,f,top):
 w=word(a);check(hex(a)+' retained bytes',raw(a).hex(),rows[a]['bytes'])
 check(hex(a)+' vendor fields',(w&127,w>>7&31,w>>15&31,w>>20&31,w>>12&7,w>>27),(11,rd,rs1,rs2,f,top))
 if f in (4,5):check(hex(a)+' indexed shift',w>>25&3,0)
 else:check(hex(a)+' signed extract high/low',(w>>26&31,w>>20&31),(7,0))
def sx(x,n):return x-(1<<n) if x&(1<<(n-1)) else x
def target(a,pair=False):
 w=word(a)
 if pair:
  k=word(a+4);assert w&127==0x17 and k&127==0x67
  assert w>>7&31==k>>15&31
  return (a+(w&0xfffff000)+sx(k>>20,12))&0xffffffff
 assert w&127==0x6f
 v=(w>>31<<20)|((w>>12&255)<<12)|((w>>20&1)<<11)|((w>>21&1023)<<1)
 return (a+sx(v,21))&0xffffffff
expected={
0xa00288e4:'addi s1, gp, -0x38',0xa00288f0:'c.addi s1, 0x10',
0xa0028920:'lui s2, 0x62fc6',0xa0028924:'lbu a4, 0x48(s2)',0xa0028928:'addi a5, s2, 0x48',
0xa002892e:'lbu a4, 1(a5)',0xa0028934:'lbu a4, 2(a5)',0xa0028942:'c.li s1, 2',
0xa0028944:'c.li a4, 1',0xa002896c:'addi s2, s2, 0x48',0xa0028970:'c.li s1, 0',
0xa0028974:'addi s2, a5, 1',0xa0028978:'c.li s1, 1',
0xa01b5c54:'c.mv s2, a0',0xa01b5c56:'addi a0, gp, -0x38',0xa01b5c6a:'addi a5, a5, 0x48',
0xa01b5c78:'addi a0, gp, -0x28',0xa01b5c84:'addi a0, gp, -0x38',
0xa0027d16:'lw a5, 0x10(s5)',0xa0027d1c:'c.lw a5, 4(a5)',0xa0027d20:'c.mv a0, s1',0xa0027d22:'c.jalr a5',
0xa002c68e:'c.lw a5, 0xc(a0)',0xa002c692:'c.lw s1, 0x18(a5)',0xa002c694:'addi s2, s1, 0x30',
0xa002c69e:'lbu a5, 0(s1)',0xa002c6a8:'c.addi a5, -1',0xa002c6aa:'sb a5, 0(s1)',
0xa002c6ba:'sb zero, 0(s1)',0xa002c6be:'c.li a1, 0',0xa002c6c0:'c.lw a5, 0x18(a5)',
0xa002c6ca:'andi a5, a5, 0x40',0xa002c6e2:'csrrc s3, mstatus, s3',
0xa002c6ec:'c.lw a5, 0xc(a5)',0xa002c6f0:'lbu a5, 2(s1)',0xa002c6fc:'c.lw a5, 4(a5)',
0xa002c744:'lbu a5, 3(s1)',0xa00198c8:'lw s1, 0xa4(a0)',0xa00198ce:'lbu a4, 0(s1)',
0xa00198fa:'lbu a5, 0xe(s1)',0xa0019900:'lbu a5, 0(s1)',0xa0019904:'addi s2, gp, 0x3dc',
0xa001992e:'lbu a5, 0(s1)',0xa0019936:'andi a0, a0, 0xff',0xa0019942:'lbu a5, 0(s1)',0xa0019946:'c.li a4, 0xf'}
for a,e in expected.items():asm(a,e)
# Decode vendor fields independently of D09's model-dependent formatter.
for args in [(0xa0028946,14,15,9,5,0),(0xa0028952,10,9,0,2,3),
 (0xa01b5c6e,14,18,15,4,16),(0xa01b5c74,0,18,15,5,0),
 (0xa0019908,14,18,15,4,16),(0xa001990e,14,14,0,2,3),
 (0xa0019916,14,18,15,4,16),(0xa001991a,14,14,0,2,3),
 (0xa0019922,10,18,15,4,16),(0xa0019926,10,10,0,2,3),
 (0xa0019932,10,18,15,4,16),(0xa0019948,14,18,15,5,0)]:vendor(*args)
for a,t,p in [(0xa00288f4,0xa00288b8,False),(0xa0028900,0xa0027968,False),
 (0xa002894e,0xa00274b2,False),(0xa01b5c5a,0xa0027968,True),
 (0xa01b5c7c,0xa00273cc,True),(0xa01b5c88,0xa00274b2,True),
 (0xa001992a,0xa0024bb6,False),(0xa001993a,0xa01b5c48,True)]:check(hex(a)+' call target',target(a,p),t)
# Independently decode only the normal path gates, without exporting functions.
for a,t in [(0xa00288f8,0xa002890e),(0xa0028904,0xa002891e),(0xa01b5c62,0xa01b5c90),
 (0xa002c6a4,0xa002c6b6),(0xa0019912,0xa001994c),(0xa001991e,0xa001994c)]:
 w=word(a);assert w&127==0x63
 imm=(w>>31<<12)|((w>>7&1)<<11)|((w>>25&63)<<5)|((w>>8&15)<<1)
 check(hex(a)+' branch target',(a+sx(imm,13))&0xffffffff,t)
for a,t in [(0xa002892c,0xa002896c),(0xa0028932,0xa0028974),(0xa01b5c72,0xa01b5c84),
 (0xa002c6f4,0xa002c700),(0xa002c74a,0xa002c6b0),(0xa00198fe,0xa001994c)]:
 w=int.from_bytes(raw(a,2),'little'); assert w&3==1 and w>>13 in (6,7)
 imm=((w>>12&1)<<8)|((w>>10&3)<<3)|((w>>5&3)<<6)|((w>>3&3)<<1)|((w>>2&1)<<5)
 check(hex(a)+' compressed gate',(a+sx(imm,9))&0xffffffff,t)
# Old identities reviewed, not newly recovered.
for a,t in [(0xa066d7cc,0xa002c678),(0xa01bcb1c,0xa00198bc),(0xa0003284,0xa01bcb18),(0xa0003288,0x62fc36b4)]:check(hex(a)+' old ops/private identity',word(a),t)
check('dev initial four bytes',raw(0xa00031e4).hex(),'00000000')
# 4B local anchor for the existing restoration claim omitted from D09 windows.
check('mstatus restoration word',raw(0xa002c700).hex(),'73900930')
rest=list(c.disasm(raw(0xa002c700),0xa002c700))[0]
check('mstatus restoration decode',rest.mnemonic+' '+rest.op_str,'csrw mstatus, s3')
result={'scope':'D09 independent old-conclusion review; new functionality 0; no complete function export',
 'inheritance':'D03-D08 descriptor/IRQ/ring and D09 reuse-check retained unchanged',
 'checks':checks,'normal_decode_anchors':len(expected),'vendor_field_anchors':12,
 'precision_correction':{'type_reads':['0xa0019900','0xa001992e','0xa0019942'],
 'channel_reads':['0xa0019908','0xa0019916','0xa0019922','0xa0019932'],
 'channel_write':'0xa0019948','stop_type_source':'0xa0019900; no fresh type read at 0xa0019922'},
 'only_extra_raw_anchor':{'va':'0xa002c700','bytes':'73900930','asm':'csrw mstatus, s3','classification':'old-conclusion review'}}
(OUT/'review-results.json').write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
print('PASS',len(checks),'checks;',len(expected),'normal anchors; 12 vendor field anchors; 0 new functionality')
