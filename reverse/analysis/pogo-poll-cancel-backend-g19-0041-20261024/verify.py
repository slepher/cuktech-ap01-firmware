"""Sparse original-word checks only; never runs target instructions or inputs."""
import json
import struct
from pathlib import Path

ROOT=Path('D:/Documents/PlatformIO/Projects/cuktech-ap01-firmware')
BASE=0x9ffff000
rom=(ROOT/'roms/0041/ap01-1.0.2_0041.bin').read_bytes()
checks=[]
def sx(x,n): return x-(1<<n) if x>>(n-1) else x
def word(a): return struct.unpack_from('<I',rom,a-BASE)[0]
def raw(a,h,role):
    assert rom[a-BASE:a-BASE+len(bytes.fromhex(h))].hex()==h,(hex(a),h)
    checks.append(dict(address=f'{a:08x}',raw=h,role=role))
def branch(a,r1,r2,f,target):
    w=word(a)
    assert (w&127,(w>>15)&31,(w>>20)&31,(w>>12)&7)==(0x63,r1,r2,f)
    imm=((w>>31)<<12)|(((w>>7)&1)<<11)|(((w>>25)&63)<<5)|(((w>>8)&15)<<1)
    assert a+sx(imm,13)==target
    checks.append(dict(address=f'{a:08x}',raw=w.to_bytes(4,'little').hex(),branch_target=f'{target:08x}',rs1=r1,rs2=r2,funct3=f))
def jal(a,target):
    w=word(a); assert w&127==0x6f and (w>>7)&31==1
    imm=((w>>31)<<20)|(((w>>12)&255)<<12)|(((w>>20)&1)<<11)|(((w>>21)&1023)<<1)
    assert a+sx(imm,21)==target
    checks.append(dict(address=f'{a:08x}',raw=w.to_bytes(4,'little').hex(),jal_target=f'{target:08x}'))
def cb(a,r,nz,target):
    w=struct.unpack_from('<H',rom,a-BASE)[0]
    assert w&3==1 and w>>13==(7 if nz else 6) and ((w>>7)&7)+8==r
    imm=(((w>>12)&1)<<8)|(((w>>10)&3)<<3)|(((w>>5)&3)<<6)|(((w>>3)&3)<<1)|(((w>>2)&1)<<5)
    assert a+sx(imm,9)==target
    checks.append(dict(address=f'{a:08x}',compressed_branch_target=f'{target:08x}'))
def cj(a,target):
    w=struct.unpack_from('<H',rom,a-BASE)[0];assert w&3==1 and w>>13==5
    imm=(((w>>12)&1)<<11)|(((w>>11)&1)<<4)|(((w>>9)&3)<<8)|(((w>>8)&1)<<10)|(((w>>7)&1)<<6)|(((w>>6)&1)<<7)|(((w>>3)&7)<<1)|(((w>>2)&1)<<5)
    assert a+sx(imm,12)==target
    checks.append(dict(address=f'{a:08x}',compressed_jump_target=f'{target:08x}'))
def mem(a,op,f,base,reg,imm):
    w=word(a); actual_imm=w>>20 if op==3 else ((w>>25)<<5)|((w>>7)&31)
    actual_reg=(w>>7)&31 if op==3 else (w>>20)&31
    assert (w&127,(w>>12)&7,(w>>15)&31,actual_reg,sx(actual_imm,12))==(op,f,base,reg,imm)
    checks.append(dict(address=f'{a:08x}',memory_fields=[op,f,base,reg,imm]))

for row in [
 (0xa009f442,'dc517d57','watcher fd word24; minus1 sentinel'),
 (0xa009f472,'185d','loop capacity word38'),
 (0xa009f478,'dc4d1346f6ff9389c5007d8ed0cd','read desired1c; AND NOT mask; save update node+c; publish result'),
 (0xa009f48e,'23a6340123a8340123a00402','self-link update node+c/+10; clear cached mask20'),
 (0xa009f49a,'d85083274903','reload watcher fd and loop buckets34'),
 (0xa009f4a4,'83290500','save bucket first node'),
 (0xa009f4c4,'9307c5fe','bucket node minus14 compared to watcher'),
 (0xa009f4d0,'8327c903','read registered-node counter loop3c'),
 (0xa009f4e8,'fd17232ef902','decrement counter and store loop3c'),
 (0xa009f4fe,'03a709004e85ba89','save next before remove; a0=current; advance saved node'),
 (0xa009f508,'dc45','read watcher update-node.next'),
 (0xa009f50e,'9307c502dcc51c599cc923a0370123283503','tail insert update node at loop2c/30'),
 (0xa009e222,'032a4501','backend object from loop14'),
 (0xa009e226,'2a89ae84','preserve loop and fd'),
 (0xa009e22a,'83294a11','record-context pointer from backend114'),
 (0xa009e232,'41468145130504fd','initialize 16B stack record with zero'),
 (0xa009e242,'83278903','fd-capacity gate input loop38'),
 (0xa009e24a,'83274903','same fd buckets loop34'),
 (0xa009e25a,'03250902930604fd26868945','service ABI backendfd=loop20,op2,fd,stack16'),
 (0xa009e26a,'b250225492540259f249624a45618280','service tail restores/returns without replacing or comparing a0'),
 (0xa009e27a,'139835000147fd58','fd*8; record index0; minus1 sentinel'),
 (0xa009e282,'83a78900','record-context count word8'),
 (0xa009e28a,'83a64900931747003386f6001046','records pointer word4; stride16; fd word8'),
 (0xa009e2a8,'8325490303a54900c295','bucket sentinel; records pointer; bucket address'),
 (0xa009e2b6,'3303f500','matching record address retained in t1'),
 (0xa009e2c2,'03250902','read backendfd before service3'),
 (0xa009e2ca,'2328c4fc232c94fc930604fd26868d45','stack aggregate mask word0 and fd word8; op3'),
 (0xa009e2dc,'8c464d8e','OR next watcher desired into record mask'),
 (0xa009e2e4,'9442','advance bucket node'),
 (0xa009e2e8,'232413010507','zero aggregate invalidates record.fd to minus1; record index+1'),
 (0xa009e2f0,'9047032704fd518f2328e4fc9c43','context absent: aggregate node+8 into stack0 and advance'),
 (0xa009e30c,'03a6090003250902930704fd2687894693054a08','six-arg service: backendfd,backend+84,context.word0,2,fd,stack16'),
 (0xa009e324,'83278903','capacity rechecked after service6'),
 (0xa009e32c,'8327490393963400','reload bucket array and fd*8'),
 (0xa009e338,'032749033697','reconstruct bucket sentinel'),
 (0xa009e342,'23a607009c43','clear node+c=watcher20; advance node'),
]: raw(*row)

for a,t in [(0xa009f48a,0xa0098b4a),(0xa009f4cc,0xa0098b4a),(0xa009e23a,0xa0024906),(0xa009e266,0xa010e722),(0xa009e320,0xa009e0e6)]:jal(a,t)
for args in [
 (0xa009f446,15,14,0,0xa009f522),(0xa009f45c,15,0,5,0xa009f472),(0xa009f474,15,14,7,0xa009f4b6),(0xa009f4b2,10,15,1,0xa009f4c4),(0xa009f4c8,9,15,1,0xa009f4ee),(0xa009f4fa,19,15,0,0xa009f502),(0xa009f50a,19,15,1,0xa009f4b6),
 (0xa009e22e,19,0,1,0xa009e27a),(0xa009e23e,19,0,1,0xa009e30c),(0xa009e246,9,15,7,0xa009e25a),(0xa009e256,13,15,1,0xa009e2f0),(0xa009e286,14,15,5,0xa009e232),(0xa009e298,12,9,1,0xa009e2ec),(0xa009e2ba,13,11,1,0xa009e2dc),(0xa009e2be,12,0,0,0xa009e2e8),(0xa009e2c6,10,0,4,0xa009e26a),(0xa009e306,10,0,4,0xa009e26a),(0xa009e328,9,15,7,0xa009e26a),(0xa009e33e,15,14,0,0xa009e26a)]:branch(*args)
cb(0xa009f486,12,True,0xa009f508);cb(0xa009f4d4,15,True,0xa009f4e8)
for a,t in [(0xa009f506,0xa009f4a8),(0xa009f520,0xa009f4b6),(0xa009e2da,0xa009e266),(0xa009e2e6,0xa009e2a8),(0xa009e2ee,0xa009e282),(0xa009e30a,0xa009e2ce),(0xa009e348,0xa009e338)]:cj(a,t)
for args in [(0xa009f496,0x23,2,9,0,0x20),(0xa009e22a,3,2,20,19,0x114),(0xa009e2e8,0x23,2,6,17,8),(0xa009e342,0x23,2,15,0,12)]:mem(*args)

vendor=[]
for a,f,top,rd,rs1,rs2,shift in [
 (0xa009f4a0,4,8,10,15,14,3),(0xa009f4ae,1,0,15,15,14,3),(0xa009f4f4,1,0,15,15,14,3),
 (0xa009e24e,1,0,13,15,9,3),(0xa009e252,4,8,15,15,9,3),(0xa009e29c,5,8,0,13,15,0),
 (0xa009e2a4,4,8,13,13,16,0),(0xa009e2b2,4,8,12,10,15,0),(0xa009e2e0,5,8,12,10,15,0),(0xa009e334,4,8,15,15,9,3)]:
    w=word(a);fields=(w&127,(w>>12)&7,w>>27,(w>>7)&31,(w>>15)&31,(w>>20)&31,(w>>25)&3)
    assert fields==(11,f,top,rd,rs1,rs2,shift),(hex(a),fields)
    vendor.append(dict(address=f'{a:08x}',raw=w.to_bytes(4,'little').hex(),fields=fields,rule='addsl' if f==1 else ('lrw' if f==4 else 'srw')))
model=ROOT/'evidence/rea-0041-20261017/ghidra/Ghidra/Processors/RISCV/data/languages/ap01thead2.sinc'
mt=model.read_text(encoding='utf-8')
model_rules=[]
for marker,needles in [(':th.addsl rd,rs1,rs2,thshift',['rd = rs1 + (rs2 << thshift);']),(':th.lrw rd,rs1,rs2,thshift',['local delta:4 = rs2 << thshift;','local updated:4 = rs1 + delta;','local ea:4 = updated;','local value:4 = *[ram]:4 ea;','rd = value;']),(':th.srw rd,rs1,rs2,thshift',['local delta:4 = rs2 << thshift;','local updated:4 = rs1 + delta;','local ea:4 = updated;','*[ram]:4 ea = rd:4;'])]:
    begin=mt.index(marker);end=mt.index('\n}',begin)+2;rule=mt[begin:end]
    for needle in needles:assert needle in rule,(marker,needle)
    model_rules.append(dict(rule=marker,definition_line=mt.count('\n',0,begin)+1,semantics_text_check='PASS'))
result=dict(status='PASS-static-only',baseline='0fa2089',mapping='VA-0x9ffff000',checks=checks,vendor=vendor,model=str(model),model_rules=model_rules,model_limitation='Existing local rule, not external vendor specification or full source/version authentication',inherited=['J05 exact call/object seeds','G07/G08 stop and G09/G10 registration/ready','F03/F04 unlink','page-logic record15 zero-fill helper'],limitations=['No complete function export','Opaque lower services a010e722/a009e0e6 are not OS success evidence','No target/input/model/runtime/network execution','Author checks require independent technical review'])
Path(__file__).with_name('evidence.json').write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
print(f'PASS {len(checks)} sparse checks and {len(vendor)} vendor field instances')
