"""G19/3: static checks of the nonfallback op2 caller; no target execution."""
import json
import struct
from pathlib import Path

ROOT=Path('D:/Documents/PlatformIO/Projects/cuktech-ap01-firmware')
ROM=ROOT/'roms/0041/ap01-1.0.2_0041.bin'
rom=ROM.read_bytes()
assert len(rom)==6769704
BASE=0x9ffff000
checks=[]
def sx(x,n):return x-(1<<n) if x>>(n-1) else x
def word(a):return struct.unpack_from('<I',rom,a-BASE)[0]
def raw(a,h,meaning):
    assert rom[a-BASE:a-BASE+len(bytes.fromhex(h))].hex()==h,(hex(a),h)
    checks.append(dict(address=f'0x{a:08x}',raw=h,meaning=meaning))
def branch(a,r1,r2,f,target):
    w=word(a);assert (w&127,(w>>15)&31,(w>>20)&31,(w>>12)&7)==(0x63,r1,r2,f)
    imm=((w>>31)<<12)|(((w>>7)&1)<<11)|(((w>>25)&63)<<5)|(((w>>8)&15)<<1)
    assert a+sx(imm,13)==target
    checks.append(dict(address=f'0x{a:08x}',branch_target=f'0x{target:08x}',fields=[r1,r2,f]))
def jal(a,target):
    w=word(a);assert w&127==0x6f and (w>>7)&31==1
    imm=((w>>31)<<20)|(((w>>12)&255)<<12)|(((w>>20)&1)<<11)|(((w>>21)&1023)<<1)
    assert a+sx(imm,21)==target
    checks.append(dict(address=f'0x{a:08x}',raw=w.to_bytes(4,'little').hex(),jal_target=f'0x{target:08x}'))
def memory(a,op,f,base,reg,imm):
    w=word(a);actual_imm=w>>20 if op==3 else ((w>>25)<<5)|((w>>7)&31)
    actual_reg=(w>>7)&31 if op==3 else (w>>20)&31
    assert (w&127,(w>>12)&7,(w>>15)&31,actual_reg,sx(actual_imm,12))==(op,f,base,reg,imm)
    checks.append(dict(address=f'0x{a:08x}',memory_fields=[op,f,base,reg,imm]))

for row in [
 (0xa009e104,'3a8ad85d3e89fd57aa8a368b','snapshot fd/record/backend_fd/op and read ctx3c sentinel'),
 (0xa009e168,'dc4183acc500ae898443','tail pointer ctx4; index mask ctx+c; save ctx; load old tail'),
 (0xa009e172,'ca85328c','source=record; preserve original scratch base'),
 (0xa009e176,'13871400b3f49401939b4400b29b98c3','oldtail+1; i=oldtail&mask; scratch+i*16; publish tail before copy'),
 (0xa009e186,'41465e85','n16; destination scratch slot'),
 (0xa009e18e,'83ad8902139d6400130600043389ad0181454a85','load ctx28 entry base after copy; stride64; zero64 service args'),
 (0xa009e1a6,'9357fa412326f90023287901232a0900','sign-extended fd high; scratch-slot pointer low; pointer high0'),
 (0xa009e1b6,'23225901232c690123244901','entry4 backendfd; entry18 op; entry8 fd'),
 (0xa009e1c2,'f5478a04','byte value29; index<<2'),
 (0xa009e1ca,'b3e464012320990223224903','index<<2 OR op to entry20; fd to entry24'),
 (0xa009e1d6,'83a7090003a749009c431843b98fb3f79701','reload ctx head/tail pointers, then both values, xor and mask'),
 (0xa009e1ea,'6286ce855685','conditional service ABI backendfd,ctx,original scratch'),
 (0xa009e1f4,'f2506254d2544259b259225a925a025bf24b624cd24c424db24d21618280','restore/return; no a0 success comparison or replacement'),
]:raw(*row)
branch(0xa009e110,14,15,1,0xa009e168)
for a,target in [(0xa009e18a,0xa000589c),(0xa009e1a2,0xa0024906),(0xa009e1f0,0xa009dfcc)]:jal(a,target)
for args in [(0xa009e16a,3,2,11,25,12),(0xa009e18e,3,2,19,27,40),(0xa009e1aa,0x23,2,18,15,12),(0xa009e1ae,0x23,2,18,23,16),(0xa009e1b2,0x23,2,18,0,20),(0xa009e1b6,0x23,2,18,21,4),(0xa009e1ba,0x23,2,18,22,24),(0xa009e1be,0x23,2,18,20,8),(0xa009e1ce,0x23,2,18,9,32),(0xa009e1d2,0x23,2,18,20,36)]:memory(*args)
w=struct.unpack_from('<H',rom,0xa009e1e8-BASE)[0]
assert w&3==1 and w>>13==7 and ((w>>7)&7)+8==15
imm=(((w>>12)&1)<<8)|(((w>>10)&3)<<3)|(((w>>5)&3)<<6)|(((w>>3)&3)<<1)|(((w>>2)&1)<<5)
assert 0xa009e1e8+sx(imm,9)==0xa009e1f4
checks.append(dict(address='0xa009e1e8',condition='masked head/tail xor nonzero skips conditional service',target='0xa009e1f4'))
w=word(0xa009e1c6)
fields=(w&127,(w>>12)&7,w>>27,(w>>7)&31,(w>>15)&31,(w>>20)&31,(w>>25)&3)
assert fields==(11,5,0,15,27,26,0)
model=ROOT/'evidence/rea-0041-20261017/ghidra/Ghidra/Processors/RISCV/data/languages/ap01thead2.sinc'
mt=model.read_text(encoding='utf8');marker=':th.srb rd,rs1,rs2,thshift';start=mt.index(marker);end=mt.index('\n}',start)+2;rule=mt[start:end]
assert 'rs2 << thshift' in rule and 'rs1 + delta' in rule and '*[ram]:1' in rule and 'rd:1' in rule
result=dict(status='PASS-static-only',claim='G19/3',baseline='cb4abfd',original_identity=dict(path=str(ROM),length=6769704,sha256_inherited_from_CATALOG='972db4c136c7ed9e24a83c07c1a7fd62040ca018b08ca285216d26b1fee3c6b9',mapping='VA-0x9ffff000',digest_recomputed=False),checks=checks,vendor=dict(address='0xa009e1c6',raw=w.to_bytes(4,'little').hex(),fields=fields,rule=marker,model=str(model),definition_line=mt.count('\n',0,start)+1),inherited=['G11/1 fallback not reverified','G19/2 callsite input and stack16','G03/G04 aligned16 copy and aligned64 zero-fill'],limits=['No target/input/model execution','No complete300B export','No a010e722/native service analysis','a009dfcc body remains an anchor until management authorizes any expansion','Alignment/valid ring capacity and concurrent publication are not inferred'])
Path(__file__).with_name('evidence.json').write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n',encoding='utf8')
print(f'PASS {len(checks)} sparse checks and 1 vendor byte-store field')
