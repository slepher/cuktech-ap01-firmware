"""F19 approved receive adapter samples; no target/model execution."""
import json
from pathlib import Path
import capstone
MAIN=Path('D:/Documents/PlatformIO/Projects/cuktech-ap01-firmware')
OUT=Path(__file__).resolve().parent
ROM=MAIN/'roms/0041/ap01-1.0.2_0041.bin'
BASE=0x9ffff000
assert ROM.stat().st_size==6769704
md=capstone.Cs(capstone.CS_ARCH_RISCV,capstone.CS_MODE_RISCV32|capstone.CS_MODE_RISCVC)
windows=[(0xa005f508,0xa005f53c),(0xa005f53c,0xa005f548),
         (0xa005f56a,0xa005f56e),(0xa005f592,0xa005f5a8)]
rows={}
with ROM.open('rb') as f:
    for a,z in windows:
        f.seek(a-BASE);data=f.read(z-a);off=0
        while off<len(data):
            size=4 if data[off]&3==3 else 2;b=data[off:off+size];pc=a+off
            ins=list(md.disasm(b,pc))
            asm=ins[0].mnemonic+' '+ins[0].op_str if ins else 'UNDECODED'
            rows[pc]={'pc':hex(pc),'offset':hex(pc-BASE),'raw':b.hex(),'asm':asm};off+=size
checks=[]
for pc,asm,meaning in [
 (0xa005f508,'c.beqz a0, 0xa0','null Q guard'),
 (0xa005f518,'c.li a5, -1','infinite wait comparison'),
 (0xa005f51a,'c.mv s2, a0','preserve same Q'),
 (0xa005f51c,'c.mv s1, a2','preserve timeout'),
 (0xa005f51e,'bne a2, a5, 0x1e','finite default10000 branch'),
 (0xa005f522,'c.lw a2, 0x18(a0)','infinite service n from Q+18'),
 (0xa005f536,'c.srai a0, 0x1f','fold returned sign to0/-1'),
 (0xa005f53a,'c.jr ra','common adapter return'),
 (0xa005f53c,'c.mv s3, a1','preserve original out address'),
 (0xa005f53e,'c.li a0, 0','clock-like service selector only'),
 (0xa005f540,'addi a1, s0, -0x28','deadline scratch starts here'),
 (0xa005f592,'lw a2, 0x18(s2)','finite service n from same Q+18'),
 (0xa005f596,'addi a3, s0, -0x28','deadline pointer as lower arg3'),
 (0xa005f59a,'c.mv a1, s3','restore same caller out pointer'),
 (0xa005f59c,'c.mv a0, s2','same Q as lower arg0'),
 (0xa005f5a6,'c.j -0x7a','lower returns to common sign fold'),
]:
    assert rows[pc]['asm']==asm,(hex(pc),rows[pc]['asm'])
    checks.append({'pc':hex(pc),'observed':asm,'meaning':meaning})
def w(pc):return int.from_bytes(bytes.fromhex(rows[pc]['raw']),'little')
def sx(x,b):return x-(1<<b) if x&(1<<(b-1)) else x
for pc,jpc,target in [(0xa005f524,0xa005f528,0xa01978a2),
                      (0xa005f59e,0xa005f5a2,0xa0197954)]:
    actual=(pc+sx(w(pc)&0xfffff000,32)+sx(w(jpc)>>20,12))&0xfffffffe
    assert actual==target
    checks.append({'pc':hex(pc),'target':hex(target),'meaning':'independent AUIPC/JALR; service body separate scope'})
v=w(0xa005f56a)
fields={'op':v&127,'rd':(v>>7)&31,'f3':(v>>12)&7,'rs1':(v>>15)&31,'rs2':(v>>20)&31,'top7':v>>25}
assert fields==dict(op=11,rd=15,f3=1,rs1=9,rs2=13,top7=16)
checks.append({'pc':'0xa005f56a','fields':fields,'meaning':'local th.mula match only; no clock semantics authentication'})
model_path=MAIN/'evidence/rea-0041-20261017/ghidra/Ghidra/Processors/RISCV/data/languages/ap01thead2.sinc'
model=model_path.read_text(encoding='utf-8');at=model.index(':th.mula ');rule=model[at:model.index('\n}',at)+2]
assert 'op0006=0xb & op1214=1 & op2531=16' in rule and 'rd = rd + (rs1 * rs2);' in rule
checks.append({'meaning':'existing local th.mula rule read without execution or model change'})
result={'claim':'F11/6','task':'F19','baseline':'bd457a6','static_only':True,
 'rom':str(ROM),'length':ROM.stat().st_size,
 'inherited_sha256':'972db4c136c7ed9e24a83c07c1a7fd62040ca018b08ca285216d26b1fee3c6b9',
 'mapping':'file_offset=VA-0x9ffff000','decoder':'Capstone '+capstone.__version__+' RV32+RVC',
 'exploration':'164 unique adapter bytes inspected in bounded reads; selected transfer/return fields retained below',
 'windows':[{'start':hex(a),'end_exclusive':hex(z)} for a,z in windows],
 'sample_bytes':sum(z-a for a,z in windows),'rows':list(rows.values()),'checks':checks,
 'local_rule':{'path':str(model_path),'text':rule},
 'conclusion':'same out pointer and Q.size passed to finite/infinite receive services; adapter sign-fold return does not gate caller dispatch',
 'limits':['No clock service body/unit/range certification','Only actual default10000 finite route intended for lower followup',
 'No lower source message copy/release or actual receive by adapter evidence alone']}
dest=OUT/'adapter-evidence.json'
if dest.exists():raise FileExistsError(dest)
dest.write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
print(json.dumps({'result':'PASS','checks':len(checks),'sample_bytes':result['sample_bytes']}))
