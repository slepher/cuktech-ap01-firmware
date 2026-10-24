"""F19 registered nonempty message out-slot and release branch samples."""
import json
from pathlib import Path
import capstone
MAIN=Path('D:/Documents/PlatformIO/Projects/cuktech-ap01-firmware')
OUT=Path(__file__).resolve().parent;BASE=0x9ffff000
ROM=MAIN/'roms/0041/ap01-1.0.2_0041.bin'
assert ROM.stat().st_size==6769704
md=capstone.Cs(capstone.CS_ARCH_RISCV,capstone.CS_MODE_RISCV32|capstone.CS_MODE_RISCVC)
windows=[(0xa0131a02,0xa0131a46),(0xa0131abc,0xa0131ad6),
         (0xa0131b68,0xa0131b8c),(0xa0131b94,0xa0131baa)]
rows={}
with ROM.open('rb') as f:
    for a,z in windows:
        f.seek(a-BASE);data=f.read(z-a);ins=list(md.disasm(data,a))
        assert sum(x.size for x in ins)==len(data)
        for x in ins:rows[x.address]={'pc':hex(x.address),'offset':hex(x.address-BASE),
            'raw':bytes(x.bytes).hex(),'asm':x.mnemonic+' '+x.op_str}
checks=[]
for pc,asm,meaning in [
 (0xa0131a02,'c.mv s1, a0','preserve K'),
 (0xa0131a04,'c.mv s4, a2','preserve caller internal Msg output slot'),
 (0xa0131a06,'addi s5, a0, 0x18','list service argument K+18'),
 (0xa0131a14,'c.mv a0, s5','same list service argument'),
 (0xa0131a1a,'c.mv s2, a0','preserve returned candidate Msg'),
 (0xa0131a1c,'c.beqz a0, 0x2a','nonnull message selects registered path'),
 (0xa0131a1e,'lh a5, 0x22(s1)','old signed message count'),
 (0xa0131a22,'addi a4, a5, -1','count decrement'),
 (0xa0131a26,'sh a4, 0x22(s1)','count halfword write'),
 (0xa0131a2a,'lh a4, 0x20(s1)','capacity/count comparison'),
 (0xa0131a2e,'bne a4, a5, 0x10','skip optional notification to out publication'),
 (0xa0131a32,'c.li a2, 4','notification mask argument only'),
 (0xa0131a34,'c.li a1, 4','notification element count argument only'),
 (0xa0131a36,'addi a0, s1, 0x5c','notification slots from same K'),
 (0xa0131a3e,'sw s2, 0(s4)','publish identical Msg to original slot'),
 (0xa0131a42,'c.li a0, 0','nonnull path returns status0'),
 (0xa0131a44,'c.j 0x78','common return'),
 (0xa0131ad4,'c.jr ra','return to finite receive caller'),
 (0xa0131b68,'lbu a4, 8(a0)','message storage-kind byte'),
 (0xa0131b6c,'c.mv a5, a0','preserve same Msg in a5'),
 (0xa0131b6e,'c.bnez a4, 0x12','kind0 uses first list'),
 (0xa0131b70,'addi a4, gp, 0xb8','first release sentinel'),
 (0xa0131b74,'c.lw a3, 0(a4)','old sentinel next'),
 (0xa0131b76,'c.sw a4, 4(a5)','Msg prev sentinel'),
 (0xa0131b78,'c.sw a3, 0(a5)','Msg next old first'),
 (0xa0131b7a,'c.sw a5, 4(a3)','old first prev Msg'),
 (0xa0131b7c,'c.sw a5, 0(a4)','sentinel next Msg'),
 (0xa0131b7e,'c.jr ra','list-return branch exits without heap call'),
 (0xa0131b80,'c.li a3, 2','second list kind2'),
 (0xa0131b86,'addi a4, gp, 0xc0','second release sentinel'),
 (0xa0131b8a,'c.j -0x16','second list joins same insertion'),
 (0xa0131b94,'c.li a5, 1','kind1 calls inherited return interface'),
 (0xa0131b96,'bne a4, a5, 0x14','other kinds to diagnostic boundary'),
 (0xa0131ba8,'c.jr ra','kind1 return'),
]:
    assert rows[pc]['asm']==asm,(hex(pc),rows[pc]['asm'])
    checks.append({'pc':hex(pc),'observed':asm,'meaning':meaning})
def w(pc):return int.from_bytes(bytes.fromhex(rows[pc]['raw']),'little')
def sx(x,b):return x-(1<<b) if x&(1<<(b-1)) else x
for pc,target in [(0xa0131a16,0xa010d70e),(0xa0131a3a,0xa003e2a0)]:
    v=w(pc);imm=((v>>31)<<20)|(((v>>12)&255)<<12)|(((v>>20)&1)<<11)|(((v>>21)&1023)<<1)
    assert v&127==0x6f and pc+sx(imm,21)==target
    checks.append({'pc':hex(pc),'target':hex(target),'meaning':'independent JAL; body not read by this task'})
pc=0xa0131b9a
target=(pc+sx(w(pc)&0xfffff000,32)+sx(w(0xa0131b9e)>>20,12))&0xfffffffe
assert target==0xa002e14e
checks.append({'pc':hex(pc),'target':hex(target),'meaning':'kind1 same original a0 Msg; no allocator-body claim'})
v=w(0xa0131a3e)
assert (v&127,(v>>12)&7,(v>>15)&31,(v>>20)&31,((v>>25)<<5)|((v>>7)&31))==(35,2,20,18,0)
checks.append({'pc':'0xa0131a3e','meaning':'independent S-format SW s2,0(s4); exact candidate identity'})
result={'claim':'F11/6','task':'F19','baseline':'bd457a6','static_only':True,
 'source':str(ROM),'length':ROM.stat().st_size,'mapping':'file_offset=VA-0x9ffff000',
 'decoder':'Capstone '+capstone.__version__+' RV32+RVC',
 'exploration':'pop discovery: 80B a01319e8,48B a0131a38,16B a0131a36,26B a0131abc =154 distinct bytes; release94B. First a0131a38 discovery began midinstruction and was corrected using a0131a36 boundary; no conclusion uses spurious halfword decode.',
 'windows':[{'start':hex(a),'end_exclusive':hex(z)} for a,z in windows],
 'sample_bytes':sum(z-a for a,z in windows),'rows':list(rows.values()),'checks':checks,
 'conclusion':'nonzero list-service result Msg published to original slot after count decrement; release dispatches by Msg+8 into two gp-based lists or inherited return interface',
 'inherited_helper':{'report':'miio-queue-message-source-f21-0041-20261024.md','status':'F21 author-delivered; F22 independent review pending when inherited',
 'contract':'Valid sentinel H: N=word(H+4); N==H returns0; otherwise repair neighbors with N+4 reread, clear N+4 then N+0 and return N; no callee',
 'object_boundary':'F19 H=K+0x18; F21 H=gp+0xb8/gp+0xc0; containers are distinct'},
 'limits':['List helper a010d70e body inherited conditionally from F21, not independently re-read/reviewed by this task',
 'Only normal nonempty path; waiting/diagnostic services opaque',
 'No actual pool content/size/lifetime or physical heap return observation',
 'No same runtime send-message identity or universal Msg length4 claim']}
dest=OUT/'message-evidence.json'
if dest.exists():raise FileExistsError(dest)
dest.write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
print(json.dumps({'result':'PASS','checks':len(checks),'sample_bytes':result['sample_bytes']}))
