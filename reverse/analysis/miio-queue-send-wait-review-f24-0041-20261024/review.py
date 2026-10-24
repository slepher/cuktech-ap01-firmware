"""F24 independent send counter/service/retry review; no callee execution."""
import json
from pathlib import Path
import capstone
MAIN=Path('D:/Documents/PlatformIO/Projects/cuktech-ap01-firmware')
OUT=Path(__file__).resolve().parent
ROM=MAIN/'roms/0041/ap01-1.0.2_0041.bin';BASE=0x9ffff000
assert ROM.stat().st_size==6769704
md=capstone.Cs(capstone.CS_ARCH_RISCV,capstone.CS_MODE_RISCV32|capstone.CS_MODE_RISCVC)
windows=[(0xa0197ab8,0xa0197b1e),(0xa0131920,0xa013197c),(0xa013198a,0xa01319e8)]
rows={}
with ROM.open('rb') as f:
    for a,z in windows:
        f.seek(a-BASE);data=f.read(z-a);ins=list(md.disasm(data,a))
        assert sum(x.size for x in ins)==len(data)
        for x in ins:rows[x.address]={'pc':hex(x.address),'offset':hex(x.address-BASE),
            'raw':bytes(x.bytes).hex(),'asm':x.mnemonic+' '+x.op_str}
checks=[]
for pc,asm,meaning in [
 (0xa0197ab8,'c.mv s4, a2','outer saved n'),
 (0xa0197aba,'c.mv s3, a1','outer saved source address, not loaded source content'),
 (0xa0197aca,'c.beqz a5, 0x1e','flag0 to counter branch'),
 (0xa0197ad0,'c.bnez a0, 0x42','only nonzero quick getter result to M-copy route'),
 (0xa0197ad6,'c.li a2, 0','getter0 diagnostic argument'),
 (0xa0197ad8,'addi a1, zero, 0x79','getter0 diagnostic line argument'),
 (0xa0197ae8,'lh a4, 0x22(s1)','signed current count'),
 (0xa0197aec,'lh a5, 0x20(s1)','signed comparison limit'),
 (0xa0197af0,'blt a4, a5, -0x24','flag0 count<limit also reaches getter'),
 (0xa0197af4,'c.lw a1, 0(a0)','actual second argument word(Q) on direct clean branch'),
 (0xa0197af6,'c.mv a0, s1','first argument K'),
 (0xa0197afc,'c.beqz a0, -0x30','service0 retries quick getter, not copy'),
 (0xa0197afe,'csrw mstatus, s2','nonzero service return restores then returns original a0'),
 (0xa0197b12,'c.mv a1, a0','quick getter result M as copy caller arg1'),
 (0xa0197b14,'c.mv a3, s4','saved n passed after quick getter'),
 (0xa0197b16,'c.mv a2, s3','saved source passed after quick getter'),
 (0xa0131926,'c.swsp s3, 0x1c(sp)','preserve caller source register before local mode use'),
 (0xa0131932,'c.swsp s4, 0x18(sp)','preserve caller n register before local global-address use'),
 (0xa0131938,'c.mv s2, a0','service saved K'),
 (0xa013193a,'andi s3, a1, 0x40','local mode mask only, no formal bit name'),
 (0xa0131944,'addi s7, a0, 8','second opaque service receives K+8'),
 (0xa0131948,'lh a4, 0x22(s2)','reload signed count on every loop'),
 (0xa013194c,'lh a5, 0x20(s2)','reload signed limit on every loop'),
 (0xa0131950,'bge a4, a5, 8','not-less routes to mode gate'),
 (0xa0131954,'c.li a0, 0','count<limit return0'),
 (0xa0131958,'bnez s3, 0x8c','nonzero mask routes constant -11'),
 (0xa013195c,'addi s4, s5, -0x3e8','global pointer slot address'),
 (0xa0131960,'lw s1, 0(s4)','saved T from global slot, no null gate added'),
 (0xa0131964,'sw s2, 0x44(s1)','word T+44=K'),
 (0xa0131968,'lhu a5, 0x10(s2)','unsigned halfword increment input'),
 (0xa013196c,'c.addi a5, 1','increment before halfword truncate'),
 (0xa013196e,'sh a5, 0x10(s2)','K+10 halfword store'),
 (0xa0131972,'c.lw a5, 0xc(s1)','read T+c before clearing T+22'),
 (0xa0131974,'sh zero, 0x22(s1)','clear after the condition value was loaded'),
 (0xa0131978,'bgtz a5, 0x1a','normal path tests saved prior load'),
 (0xa0131992,'c.li a1, 1','first opaque arg1=1'),
 (0xa0131994,'c.mv a0, s1','first opaque arg0=T'),
 (0xa013199e,'c.mv s8, a0','save first service return'),
 (0xa01319a0,'sb s6, 0x1c(s1)','T+1c byte8 before second service'),
 (0xa01319a4,'c.mv a1, s7','second opaque arg1=K+8'),
 (0xa01319a6,'c.mv a0, s1','second opaque arg0=T'),
 (0xa01319b0,'beqz s8, 0x12','third service only if first return nonzero'),
 (0xa01319b4,'lw a0, 0(s4)','third service arg0 is reread global, not assumed saved T'),
 (0xa01319b8,'c.mv a1, s1','third service arg1 is saved T'),
 (0xa01319c2,'lh a0, 0x22(s1)','signed halfword result'),
 (0xa01319c6,'c.beqz a0, -0x7e','zero result loops to fresh count loads'),
 (0xa01319c8,'neg a0, a0','nonzero result returns32-bit opposite, not always negative'),
 (0xa01319d4,'c.lwsp s3, 0x1c(sp)','restore outer source value'),
 (0xa01319d6,'c.lwsp s4, 0x18(sp)','restore outer n value'),
 (0xa01319e2,'c.jr ra','normal service return'),
 (0xa01319e4,'c.li a0, -0xb','constant -11 branch, no formal error enum name'),
]:
    assert rows[pc]['asm']==asm,(hex(pc),rows[pc]['asm'])
    checks.append({'pc':hex(pc),'observed':asm,'meaning':meaning})
def w(pc):return int.from_bytes(bytes.fromhex(rows[pc]['raw']),'little')
def sx(x,b):return x-(1<<b) if x&(1<<(b-1)) else x
for pc,target in [(0xa0197acc,0xa01318de),(0xa0197af8,0xa0131920),
                  (0xa0197b1a,0xa01949f0)]:
    v=w(pc);imm=((v>>31)<<20)|(((v>>12)&255)<<12)|(((v>>20)&1)<<11)|(((v>>21)&1023)<<1)
    assert v&127==0x6f and pc+sx(imm,21)==target
    checks.append({'pc':hex(pc),'target':hex(target),'meaning':'independent caller JAL'})
for pc,jpc,target in [(0xa0197ae0,0xa0197ae4,0xa0019672),
                      (0xa013198a,0xa013198e,0xa0019672),
                      (0xa0131996,0xa013199a,0xa002772e),
                      (0xa01319a8,0xa01319ac,0xa00272d4),
                      (0xa01319ba,0xa01319be,0xa001ad30)]:
    actual=(pc+sx(w(pc)&0xfffff000,32)+sx(w(jpc)>>20,12))&0xfffffffe
    assert actual==target
    checks.append({'pc':hex(pc),'target':hex(target),'meaning':'independent AUIPC/JALR, no callee body'})
for pc,expected,target in [(0xa0197af0,(99,4,14,15),0xa0197acc),
                          (0xa0131950,(99,5,14,15),0xa0131958),
                          (0xa0131978,(99,4,0,15),0xa0131992)]:
    v=w(pc);imm=((v>>31)<<12)|(((v>>7)&1)<<11)|(((v>>25)&63)<<5)|(((v>>8)&15)<<1)
    assert (v&127,(v>>12)&7,(v>>15)&31,(v>>20)&31)==expected
    assert pc+sx(imm,13)==target
    checks.append({'pc':hex(pc),'target':hex(target),'fields':expected,'meaning':'independent signed B-format'})
for pc,expected in [(0xa0197afc,0xa0197acc),(0xa01319c6,0xa0131948)]:
    v=w(pc);imm=(((v>>12)&1)<<8)|(((v>>10)&3)<<3)|(((v>>5)&3)<<6)|(((v>>3)&3)<<1)|(((v>>2)&1)<<5)
    assert (v&3,(v>>13)&7)==(1,6) and pc+sx(imm,9)==expected
    checks.append({'pc':hex(pc),'target':hex(expected),'meaning':'independent C.BEQZ retry target'})
flag=(w(0xa0197ac2)&0xfffff000)+sx(w(0xa0197ac6)>>20,12)
global_slot=(w(0xa013193e)&0xfffff000)+sx(w(0xa013195c)>>20,12)
diag_address=(w(0xa0197ad2)&0xfffff000)+sx(w(0xa0197adc)>>20,12)
assert (flag,global_slot,diag_address)==(0x62fc6034,0x62fc6c18,0xa062c874)
checks.append({'meaning':'independent LUI/I-format flag/global/diagnostic argument addresses',
               'flag':hex(flag),'global_slot':hex(global_slot),'diagnostic_arg0':hex(diag_address)})
result={'claim':'F11/8','review':'F24','reviewer':'/root/f12','baseline':'bd457a6','static_only':True,
 'source':str(ROM),'length':ROM.stat().st_size,
 'inherited_sha256':'972db4c136c7ed9e24a83c07c1a7fd62040ca018b08ca285216d26b1fee3c6b9',
 'mapping':'file_offset=VA-0x9ffff000','decoder':'Capstone '+capstone.__version__+' RV32+RVC',
 'windows':[{'start':hex(a),'end_exclusive':hex(z)} for a,z in windows],
 'bytes':sum(z-a for a,z in windows),'rows':list(rows.values()),'checks':checks,
 'decision':'limited acceptance of F23 core; confirmed old caller scope correction; one pseudocode ordering refinement',
 'ordering_refinement':'a0131972 reads T+c before a0131974 clears T+22; branch uses previously loaded value, not a new post-clear read',
 'caller_scope_correction':'F21/F22 first-nonzero flag premise applies only to 7aca direct fallthrough; 7af0 flag0 count<limit also enters getter',
 'limits':['No scheduler/diagnostic/three opaque service bodies or formal mode/error enum naming',
 'No runtime T/thread identity, null guarantee, loop progress or successful queue delivery',
 'Source/n register preservation requires normal service/callee ABI; source memory lifetime remains unknown']}
dest=OUT/'evidence.json'
if dest.exists():raise FileExistsError(dest)
dest.write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
print(json.dumps({'result':'PASS','checks':len(checks),'bytes':result['bytes']}))
