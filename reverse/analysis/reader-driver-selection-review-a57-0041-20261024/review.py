"""A57: independent bounded static review of J08/1 selection only."""
import json
from pathlib import Path
import capstone

MAIN=Path('D:/Documents/PlatformIO/Projects/cuktech-ap01-firmware')
OUT=Path(__file__).resolve().parent
ROM=MAIN/'roms/0041/ap01-1.0.2_0041.bin'
BASE=0x9ffff000
START,END=0xa019d708,0xa019d798
assert ROM.stat().st_size==6769704
with ROM.open('rb') as f:
    f.seek(START-BASE)
    raw=f.read(END-START)
assert len(raw)==144
md=capstone.Cs(capstone.CS_ARCH_RISCV,capstone.CS_MODE_RISCV32|capstone.CS_MODE_RISCVC)
rows={}
for start,end in [(START,0xa019d750),(0xa019d754,END)]:
    chunk=raw[start-START:end-START]
    ins=list(md.disasm(chunk,start))
    assert sum(i.size for i in ins)==len(chunk)
    for i in ins:rows[i.address]={'pc':hex(i.address),'file_offset':hex(i.address-BASE),
        'raw':bytes(i.bytes).hex(),'asm':i.mnemonic+' '+i.op_str}
vendor=raw[0xa019d750-START:0xa019d754-START]
rows[0xa019d750]={'pc':'0xa019d750','file_offset':hex(0xa019d750-BASE),
    'raw':vendor.hex(),'asm':'UNDECODED'}

checks=[]
def check(ok,what,**detail):
    assert ok,(what,detail)
    checks.append({'check':what,**detail})
for pc,asm in [
 (0xa019d708,'lui a3, 0x62fc9'),(0xa019d70c,'addi a3, a3, 0x57c'),
 (0xa019d710,'lw a4, 0x1c8(a3)'),(0xa019d714,'lw a3, 0x1c4(a3)'),
 (0xa019d718,'c.addi a3, 4'),(0xa019d71a,'c.bnez a4, 0x2c'),
 (0xa019d742,'c.li s3, 3'),(0xa019d746,'c.lw s1, 0(a4)'),
 (0xa019d748,'lbu a0, 0(s1)'),(0xa019d74c,'beq a0, a2, 0x118'),
 (0xa019d756,'c.mv a0, s1'),(0xa019d758,'sw a5, -0x28(s0)'),
 (0xa019d75c,'sw a1, -0x24(s0)'),(0xa019d760,'c.jalr a4'),
 (0xa019d762,'lw a1, -0x24(s0)'),(0xa019d766,'lw a5, -0x28(s0)'),
 (0xa019d76a,'bnez a0, 0x100'),(0xa019d794,'c.li s3, 1')]:
    check(rows[pc]['asm']==asm,'ordinary instruction operands',pc=hex(pc),observed=rows[pc]['asm'])

def sx(x,bits):return x-(1<<bits) if x&(1<<(bits-1)) else x
def word(pc):return int.from_bytes(bytes.fromhex(rows[pc]['raw']),'little')
g=(word(0xa019d708)&0xfffff000)+sx(word(0xa019d70c)>>20,12)
head=g+sx(word(0xa019d710)>>20,12)
stride=g+sx(word(0xa019d714)>>20,12)
check((g,head,stride)==(0x62fc957c,0x62fc9744,0x62fc9740),
      'independent LUI/I-format global addresses',base=hex(g),head=hex(head),stride=hex(stride))
# B-format targets, independent of disassembler aliases.
def btarget(pc,expected):
    w=word(pc)
    imm=((w>>31)<<12)|(((w>>7)&1)<<11)|(((w>>25)&63)<<5)|(((w>>8)&15)<<1)
    target=pc+sx(imm,13)
    check(target==expected,'B-format target',pc=hex(pc),target=hex(target))
btarget(0xa019d74c,0xa019d864)
btarget(0xa019d76a,0xa019d86a)
# Compressed CJ/CB target decoding, also used below on inherited branch bytes.
def ctarget(pc,w,expected,isbranch=False):
    if isbranch:
        imm=(((w>>12)&1)<<8)|(((w>>10)&3)<<3)|(((w>>5)&3)<<6)|(((w>>3)&3)<<1)|(((w>>2)&1)<<5)
        bits=9
    else:
        imm=(((w>>12)&1)<<11)|(((w>>11)&1)<<4)|(((w>>9)&3)<<8)|(((w>>8)&1)<<10)|(((w>>7)&1)<<6)|(((w>>6)&1)<<7)|(((w>>3)&7)<<1)|(((w>>2)&1)<<5)
        bits=12
    target=pc+sx(imm,bits)
    check(target==expected,'compressed target',pc=hex(pc),target=hex(target))
ctarget(0xa019d71a,word(0xa019d71a),0xa019d746,True)
ctarget(0xa019d744,word(0xa019d744),0xa019d6dc)
ctarget(0xa019d754,word(0xa019d754),0xa019d71a)
ctarget(0xa019d796,word(0xa019d796),0xa019d6dc)
for pc,jpc in [(0xa019d73a,0xa019d73e),(0xa019d78c,0xa019d790)]:
    target=(pc+sx(word(pc)&0xfffff000,32)+sx(word(jpc)>>20,12))&0xfffffffe
    check(target==0xa008b51a,'AUIPC/JALR call target',pc=hex(pc),target=hex(target))

w=int.from_bytes(vendor,'little')
fields={'opcode':w&127,'rd':(w>>7)&31,'f3':(w>>12)&7,'base':(w>>15)&31,
        'index':(w>>20)&31,'shift':(w>>25)&3,'top5':w>>27}
check(fields==dict(opcode=11,rd=14,f3=4,base=14,index=13,shift=0,top5=8),
      'vendor independent bit fields',pc='0xa019d750',fields=fields)
rule_path=MAIN/'evidence/rea-0041-20261017/ghidra/Ghidra/Processors/RISCV/data/languages/ap01thead2.sinc'
model=rule_path.read_text(encoding='utf-8')
at=model.index(':th.lrw rd,rs1,rs2,thshift')
rule=model[at:model.index('\n}',at)+2]
check('op0006=0xb & op1214=4 & op2731=8' in rule and
      'local delta:4 = rs2 << thshift;' in rule and
      'local updated:4 = rs1 + delta;' in rule and
      'local value:4 = *[ram]:4 ea;' in rule and 'rd = value;' in rule,
      'inherited local th.lrw rule match; not upstream ISA authentication')

# Read old A47 evidence directly, not the author's A56 script or selected-row copy.
old_path=MAIN/'reverse/analysis/photo-reader-mode-a47-0041-20261024/evidence.json'
old=json.loads(old_path.read_text(encoding='utf-8'))
def collect(x):
    result=[]
    if isinstance(x,dict):
        if x.get('pc') in ['0xa019d6ec','0xa019d6f0','0xa019d6f2','0xa019d798',
                            '0xa019d864','0xa019d866','0xa019d86a','0xa019d86c']:result.append(x)
        else:
            for v in x.values():result+=collect(v)
    elif isinstance(x,list):
        for v in x:result+=collect(v)
    return result
inherited=collect(old)
index={r['pc']:r for r in inherited}
check(len(index)==8,'eight necessary A47 rows available')
for pc,asm in [('0xa019d6ec','lbu a2, 0(a1)'),('0xa019d798','sw s1, 4(s2)'),
               ('0xa019d864','c.lw a4, 8(s1)'),('0xa019d86a','c.lw a4, 0xc(s1)')]:
    check(index[pc]['asm']==asm,'inherited A47 operand',pc=pc,observed=index[pc]['asm'])
for pc,target in [('0xa019d866',0xa019d756),('0xa019d86c',0xa019d798)]:
    data=bytes.fromhex(index[pc]['raw']);w=int.from_bytes(data,'little');p=int(pc,16)
    if len(data)==4:
        imm=((w>>31)<<12)|(((w>>7)&1)<<11)|(((w>>25)&63)<<5)|(((w>>8)&15)<<1)
        check(p+sx(imm,13)==target,'inherited B-target',pc=pc,target=hex(target))
    else:ctarget(p,w,target,True)

result={'claim':'J08/1','review':'A57','reviewer':'/root/f12','baseline':'32f9c9e',
 'identity':{'path':str(ROM),'length':ROM.stat().st_size,
 'inherited_sha256':'972db4c136c7ed9e24a83c07c1a7fd62040ca018b08ca285216d26b1fee3c6b9',
 'mapping':'file_offset=VA-0x9ffff000'},'static_only':True,
 'read':{'start':hex(START),'end_exclusive':hex(END),'bytes':len(raw)},
 'decoder':'Capstone '+capstone.__version__+' RV32+RVC',
 'rows':[rows[k] for k in sorted(rows)],'checks':checks,
 'vendor_rule':{'path':str(rule_path),'rule':rule,'fields':fields},
 'inherited':{'path':str(old_path),'rows':inherited},
 'conclusion':'bounded acceptance; semantic correction=0; new business=0',
 'limits':['No actual head/stride values or writer','No concrete D or slot target',
 'No ready callback body, complete return ABI, registration lifecycle or runtime success']}
dest=OUT/'evidence.json'
if dest.exists():raise FileExistsError(dest)
dest.write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
print(json.dumps({'result':'PASS','checks':len(checks),'bytes':len(raw),'rows':len(rows)}))
