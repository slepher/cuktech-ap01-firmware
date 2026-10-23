"""Independent bounded ROM-byte review. Does not execute/emulate target code."""
import json
from pathlib import Path
import capstone

OUT = Path(__file__).resolve().parent
PRIOR = OUT.parent / 'weather-subscriber-a15-0041-20261023'
ROM = Path('D:/Documents/PlatformIO/Projects/cuktech-ap01-firmware/roms/0041/ap01-1.0.2_0041.bin')
image = ROM.read_bytes()
BASE = 0xa0000000
def raw(a, n=4):
    p = a - BASE + 0x1000
    return image[p:p+n]
def word(a, n=4): return int.from_bytes(raw(a,n),'little')
def sx(x,n): return x-(1<<n) if x & (1<<(n-1)) else x
checks=[]
def check(a, kind, actual, expected):
    assert actual == expected, (hex(a),kind,actual,expected)
    checks.append(dict(address=hex(a),kind=kind,raw=raw(a,2 if word(a,2)&3 !=3 else 4).hex(),decoded=actual))
def mem(a, expected):
    w=word(a); op=w&127; f=(w>>12)&7; base=(w>>15)&31
    reg=(w>>7)&31 if op==3 else (w>>20)&31
    imm=w>>20 if op==3 else ((w>>25)<<5)|((w>>7)&31)
    check(a,'I/S-memory [opcode,width,reg,base,offset]',[op,f,reg,base,sx(imm,12)],expected)
def cmem(a, expected):
    w=word(a,2)
    off=((w>>5)&1)*64+((w>>10)&7)*8+((w>>6)&1)*4
    check(a,'C-memory [quadrant,funct3,reg,base,offset]',[w&3,w>>13,8+((w>>2)&7),8+((w>>7)&7),off],expected)
def branch(a, expected):
    w=word(a)
    imm=((w>>31)<<12)|(((w>>7)&1)<<11)|(((w>>25)&63)<<5)|(((w>>8)&15)<<1)
    check(a,'B [opcode,funct3,rs1,rs2,target]',[w&127,(w>>12)&7,(w>>15)&31,(w>>20)&31,hex(a+sx(imm,13))],expected)
def jal(a, target):
    w=word(a)
    imm=((w>>31)<<20)|(((w>>12)&255)<<12)|(((w>>20)&1)<<11)|(((w>>21)&1023)<<1)
    check(a,'J [opcode,rd,target]',[w&127,(w>>7)&31,hex(a+sx(imm,21))],[111,1,hex(target)])
def addi(a, rd, rs, imm):
    w=word(a)
    check(a,'ADDI [opcode,funct3,rd,rs1,imm]',[w&127,(w>>12)&7,(w>>7)&31,(w>>15)&31,sx(w>>20,12)],[19,0,rd,rs,imm])
def cbranch(a, target):
    w=word(a,2)
    imm=((w>>12)&1)*256+((w>>10)&3)*8+((w>>5)&3)*64+((w>>3)&3)*2+((w>>2)&1)*32
    check(a,'CB [quadrant,funct3,rs1,target]',[w&3,w>>13,8+((w>>7)&7),hex(a+sx(imm,9))],[1,6,11,hex(target)])

# Independent field extraction, using numeric RV32 registers rather than prior text.
for a,e in [
 (0xa00ab6c2,[3,1,12,10,8]),(0xa00ab6c6,[3,1,11,10,10]),
 (0xa00ab6cc,[3,1,18,10,12]),(0xa00ab6d0,[3,2,19,10,28]),
 (0xa00a7f56,[35,2,10,18,24]),(0xa00a7fca,[35,2,18,25,4]),
 (0xa00a7fce,[35,2,24,25,0]),(0xa00a7fde,[35,2,25,9,16])]: mem(a,e)
for a,e in [
 (0xa00ab6c0,[0,2,15,11,16]),(0xa00ab6ca,[0,2,9,15,4]),
 (0xa00ab6e0,[0,2,10,9,24]),(0xa00ab710,[0,2,10,9,32]),
 (0xa008cedc,[0,2,15,10,68]),(0xa008cee2,[0,2,15,10,72]),
 (0xa008cee8,[0,2,15,10,64]),(0xa008ceea,[0,6,11,10,68]),
 (0xa008ceec,[0,6,12,10,72]),(0xa008cef2,[0,6,11,10,64]),
 (0xa008cef4,[0,2,15,10,64]),(0xa008cefa,[0,6,12,10,64]),
 (0xa00b3c14,[0,2,15,9,0]),(0xa00b3c18,[0,2,11,9,4])]: cmem(a,e)
for a,e in [
 (0xa00ab6d4,[99,4,11,12,'0xa00ab6e0']),
 (0xa008cede,[99,1,15,11,'0xa008cee8']),
 (0xa008cee4,[99,0,15,12,'0xa008cf00']),
 (0xa008ceee,[99,5,15,11,'0xa008cef4']),
 (0xa008cef6,[99,5,12,15,'0xa008cefc'])]: branch(a,e)
for a,b in [(0xa00a7fc2,0xa00b3a68),(0xa00ab6e2,0xa008ce90),
            (0xa008cefc,0xa008ccd2),(0xa00ab714,0xa0198946)]: jal(a,b)
addi(0xa00a7fbe,10,10,0x6b0)
addi(0xa00a7fb0,24,0,0x2f)
addi(0xa00ab6d8,12,0,60)
addi(0xa00ab6dc,11,0,-60)
cbranch(0xa00ab6b0,0xa00ab752)
for a,h in [(0xa00a7fb8,'37b50aa0'),(0xa00a7fbc,'a685'),
            (0xa00b3c1c,'4e85'),(0xa00b3c1e,'8297')]:
    check(a,'fixed ABI encoding',raw(a,len(bytes.fromhex(h))).hex(),h)

# Re-decode original bytes and compare every retained A15 row; no A15 script runs.
md=capstone.Cs(capstone.CS_ARCH_RISCV,capstone.CS_MODE_RISCV32|capstone.CS_MODE_RISCVC)
previous=json.loads((PRIOR/'instruction-windows.json').read_text())
windows=[]
for old in previous['windows']:
    a=int(old['start'],16); b=int(old['end_exclusive'],16)
    data=raw(a,b-a); assert data.hex()==old['hex']
    rows=[dict(address=hex(i.address),bytes=i.bytes.hex(),mnemonic=i.mnemonic,operands=i.op_str) for i in md.disasm(data,a)]
    assert sum(len(bytes.fromhex(i['bytes'])) for i in rows)==len(data)
    assert rows==old['instructions']
    windows.append(dict(name=old['name'],start=hex(a),end_exclusive=hex(b),file_offset=a-BASE+0x1000,hex=data.hex(),instructions=rows))
# A15 mentioned kind 0x2f without retaining its assignment; this 8B slice supplies it.
a=0xa00a7fb0
rows=[dict(address=hex(i.address),bytes=i.bytes.hex(),mnemonic=i.mnemonic,operands=i.op_str) for i in md.disasm(raw(a,8),a)]
windows.append(dict(name='kind-assignment-before-registration',start=hex(a),end_exclusive=hex(a+8),file_offset=a-BASE+0x1000,hex=raw(a,8).hex(),instructions=rows))
strings=json.loads((PRIOR/'strings.json').read_text())
for row in strings:
    p=int(row['address'],16)-BASE+0x1000
    assert image[p:image.index(0,p)].decode('ascii')==row['text']
def save(name,obj): (OUT/name).write_text(json.dumps(obj,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
save('instruction-review.json',dict(rom=str(ROM),mapping='offset=VA-0xa0000000+0x1000',decoder='Capstone '+capstone.__version__,windows=windows,raw_field_checks=checks))
result=dict(result='passed',static_only=True,prior_windows_equal=len(previous['windows']),windows=len(windows),bytes=sum(len(bytes.fromhex(w['hex'])) for w in windows),instructions=sum(len(w['instructions']) for w in windows),independent_raw_checks=len(checks),prior_strings_equal=len(strings),corrections=['a00ab710 loads pointer stored at context+0x20, not address context+0x20'],limits=['No target execution, emulation, replay, network or device access.','No new digest, inventory, source version or lifecycle certification.','Full callback direct stores are only stack saves; downstream ownership not established.'])
save('review-index.json',result)
print(json.dumps(result,ensure_ascii=False))
