"""F15 approved creator parameter/field/output samples; no callee execution."""
import json
from pathlib import Path
import capstone

MAIN=Path('D:/Documents/PlatformIO/Projects/cuktech-ap01-firmware')
ROM=MAIN/'roms/0041/ap01-1.0.2_0041.bin'
OUT=Path(__file__).resolve().parent
BASE=0x9ffff000
assert ROM.stat().st_size==6769704
md=capstone.Cs(capstone.CS_ARCH_RISCV,capstone.CS_MODE_RISCV32|capstone.CS_MODE_RISCVC)
windows=[(0xa005f0c0,0xa005f0cc),(0xa005f0ce,0xa005f0d4),
         (0xa005f0e4,0xa005f0e6),(0xa005f11a,0xa005f12e),
         (0xa005f136,0xa005f14e)]
rows={}
with ROM.open('rb') as f:
    for a,z in windows:
        f.seek(a-BASE);data=f.read(z-a)
        ins=list(md.disasm(data,a));assert sum(x.size for x in ins)==len(data)
        for x in ins:rows[x.address]={'pc':hex(x.address),'file_offset':hex(x.address-BASE),
            'raw':bytes(x.bytes).hex(),'asm':x.mnemonic+' '+x.op_str}
checks=[]
for pc,asm,meaning in [
 (0xa005f0c0,'c.mv s2, a0','preserve out pointer'),
 (0xa005f0c2,'c.li a0, 0x1c','candidate Q request bytes'),
 (0xa005f0c4,'c.mv s4, a1','preserve capacity request'),
 (0xa005f0c6,'c.mv s3, a2','preserve message-size request'),
 (0xa005f0ce,'sw zero, 0(s2)','allocation-failure output clear'),
 (0xa005f0d2,'c.li a0, -5','failure return at observed path'),
 (0xa005f0e4,'c.mv s1, a0','Q is candidate return'),
 (0xa005f11a,'sw s4, -0x50(s0)','capacity passed in stack attributes'),
 (0xa005f11e,'sw s3, -0x4c(s0)','size passed in stack attributes'),
 (0xa005f12a,'bgez a0, 0xc','nonnegative open result to normal commit path'),
 (0xa005f142,'c.li a0, 0','normal return status'),
 (0xa005f144,'sw s3, 0x18(s1)','size word stored in same Q'),
 (0xa005f148,'sw s1, 0(s2)','same Q published to original out pointer'),
 (0xa005f14c,'c.j -0x78','common return epilogue'),
]:
    assert rows[pc]['asm']==asm,(hex(pc),rows[pc]['asm'])
    checks.append({'pc':hex(pc),'observed':asm,'meaning':meaning})
def w(pc):return int.from_bytes(bytes.fromhex(rows[pc]['raw']),'little')
def sx(x,b):return x-(1<<b) if x&(1<<(b-1)) else x
pc=0xa005f144;v=w(pc)
fields=(v&127,(v>>12)&7,(v>>15)&31,(v>>20)&31,((v>>25)<<5)|((v>>7)&31))
assert fields==(35,2,9,19,0x18)
checks.append({'pc':hex(pc),'meaning':'independent S-format SW s3,0x18(s1)','fields':fields})
pc=0xa005f148;v=w(pc)
fields=(v&127,(v>>12)&7,(v>>15)&31,(v>>20)&31,((v>>25)<<5)|((v>>7)&31))
assert fields==(35,2,18,9,0)
checks.append({'pc':hex(pc),'meaning':'independent S-format SW s1,0(s2)','fields':fields})
for pc,jpc,target in [(0xa005f122,0xa005f126,0xa01974de),
                      (0xa005f13a,0xa005f13e,0xa01ac938)]:
    actual=(pc+sx(w(pc)&0xfffff000,32)+sx(w(jpc)>>20,12))&0xfffffffe
    assert actual==target
    checks.append({'pc':hex(pc),'target':hex(target),'meaning':'independent AUIPC/JALR; body remains opaque'})
v=w(0xa005f12a)
imm=((v>>31)<<12)|(((v>>7)&1)<<11)|(((v>>25)&63)<<5)|(((v>>8)&15)<<1)
assert 0xa005f12a+sx(imm,13)==0xa005f136
checks.append({'pc':'0xa005f12a','target':'0xa005f136','meaning':'independent normal-commit B-format target'})
result={'claim':'F11/4','task':'F15','baseline':'bd457a6','static_only':True,
 'source':str(ROM),'length':ROM.stat().st_size,
 'inherited_sha256':'972db4c136c7ed9e24a83c07c1a7fd62040ca018b08ca285216d26b1fee3c6b9',
 'mapping':'file_offset=VA-0x9ffff000','decoder':'Capstone '+capstone.__version__+' RV32+RVC',
 'exploration':'Three bounded creator discovery reads totaled 158 unique bytes; no creator callees read; only field samples retained',
 'windows':[{'start':hex(a),'end_exclusive':hex(z)} for a,z in windows],
 'sample_bytes':sum(z-a for a,z in windows),'rows':list(rows.values()),'checks':checks,
 'conclusion':'On normal success, Q+0x18 receives caller a2 then Q is written to caller output slot',
 'limits':['No allocator/open/name service body','No F11 ctx-to-loop identity by this script',
 'No queue later writer, runtime instance or copy4B certification']}
dest=OUT/'creator-evidence.json'
if dest.exists():raise FileExistsError(dest)
dest.write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
print(json.dumps({'result':'PASS','checks':len(checks),'sample_bytes':result['sample_bytes']}))
