"""F19 approved finite receive output/copy/return samples only."""
import json
from pathlib import Path
import capstone
MAIN=Path('D:/Documents/PlatformIO/Projects/cuktech-ap01-firmware')
OUT=Path(__file__).resolve().parent
ROM=MAIN/'roms/0041/ap01-1.0.2_0041.bin';BASE=0x9ffff000
assert ROM.stat().st_size==6769704
md=capstone.Cs(capstone.CS_ARCH_RISCV,capstone.CS_MODE_RISCV32|capstone.CS_MODE_RISCVC)
windows=[(0xa0197986,0xa01979a4),(0xa01979ba,0xa01979ce),
         (0xa01979f0,0xa0197a08),(0xa0197a2e,0xa0197a7e)]
rows={}
with ROM.open('rb') as f:
    for a,z in windows:
        f.seek(a-BASE);data=f.read(z-a);ins=list(md.disasm(data,a))
        assert sum(x.size for x in ins)==len(data)
        for x in ins:rows[x.address]={'pc':hex(x.address),'offset':hex(x.address-BASE),
            'raw':bytes(x.bytes).hex(),'asm':x.mnemonic+' '+x.op_str}
checks=[]
for pc,asm,meaning in [
 (0xa0197986,'c.lw a5, 0xc(a0)','same Q descriptor link'),
 (0xa0197988,'c.mv s1, a0','preserve same Q'),
 (0xa019798e,'lw s2, 0x18(a5)','same K through descriptor'),
 (0xa0197998,'c.andi a5, 1','read-mode bit gate'),
 (0xa019799c,'lhu a5, 0x24(s2)','queue maximum size is U16'),
 (0xa01979a0,'bltu a2, a5, 0xe4','n buffer capacity gate'),
 (0xa01979ba,'c.mv s5, a1','preserve original output address'),
 (0xa01979bc,'c.li s4, 8','mstatus mask0x8'),
 (0xa01979be,'csrrc s4, mstatus, s4','save and clear mask'),
 (0xa01979c2,'lw a4, 0x1c(s2)','K list end/head field'),
 (0xa01979c6,'addi a5, s2, 0x18','K sentinel'),
 (0xa01979ca,'bne a4, a5, 0x64','selected nonempty ready path'),
 (0xa0197a2e,'c.lw a1, 0(s1)','service arg1 from Q firstword'),
 (0xa0197a30,'addi a2, s0, -0x24','address of local internal message slot'),
 (0xa0197a34,'c.mv a0, s2','service arg0 same K'),
 (0xa0197a3a,'c.mv s1, a0','preserve pop service status'),
 (0xa0197a44,'c.bnez s1, -0x54','nonzero status to restore/return'),
 (0xa0197a46,'lw s3, -0x24(s0)','load candidate Msg returned in slot'),
 (0xa0197a4a,'bnez s3, 0xc','nonnull candidate to copy'),
 (0xa0197a56,'lhu s1, 0xa(s3)','actual copied length from message U16, not Q size'),
 (0xa0197a5a,'addi a1, s3, 0xc','copy source Msg+c'),
 (0xa0197a5e,'c.mv a0, s5','copy destination original caller out'),
 (0xa0197a60,'c.mv a2, s1','copy length actual message U16'),
 (0xa0197a6a,'c.mv a0, s3','same Msg passed to release service after copy'),
 (0xa0197a70,'lh a5, 0x10(s2)','waiter count gate after release call'),
 (0xa0197a74,'blez a5, -0x84','no-positive-waiter path restores and returns'),
 (0xa01979f0,'csrw mstatus, s4','restore prior mstatus'),
 (0xa0197a00,'c.mv a0, s1','return message length or preserved status'),
 (0xa0197a06,'c.jr ra','finite receive common return'),
]:
    assert rows[pc]['asm']==asm,(hex(pc),rows[pc]['asm'])
    checks.append({'pc':hex(pc),'observed':asm,'meaning':meaning})
def w(pc):return int.from_bytes(bytes.fromhex(rows[pc]['raw']),'little')
def sx(x,b):return x-(1<<b) if x&(1<<(b-1)) else x
pc=0xa0197a62
actual=(pc+sx(w(pc)&0xfffff000,32)+sx(w(0xa0197a66)>>20,12))&0xfffffffe
assert actual==0xa000589c
checks.append({'pc':hex(pc),'target':hex(actual),'meaning':'independent copy target; no copy-body read'})
for pc,target in [(0xa0197a36,0xa01319e8),(0xa0197a6c,0xa0131b68)]:
    v=w(pc);imm=((v>>31)<<20)|(((v>>12)&255)<<12)|(((v>>20)&1)<<11)|(((v>>21)&1023)<<1)
    assert v&127==0x6f and pc+sx(imm,21)==target
    checks.append({'pc':hex(pc),'target':hex(target),'meaning':'independent JAL; body left opaque'})
v=w(0xa0197a56)
assert (v&127,(v>>7)&31,(v>>12)&7,(v>>15)&31,v>>20)==(3,9,5,19,10)
checks.append({'pc':'0xa0197a56','meaning':'independent I-format unsigned-halfword Msg+0xa'})

index_path=MAIN/'reverse/analysis/whole-rom-coverage-0041-20261023-round1.json'
idx=json.loads(index_path.read_text(encoding='utf-8'))
metadata=[]
for i,x in enumerate(idx['functions']):
    if x['address'] in ['0xa0197954','0xa01319e8','0xa0131b68']:
        metadata.append({'pointer':'#/functions/'+str(i),'metadata':x})
assert len(metadata)==3
result={'claim':'F11/6','task':'F19','baseline':'bd457a6','static_only':True,
 'source':str(ROM),'length':ROM.stat().st_size,
 'inherited_sha256':'972db4c136c7ed9e24a83c07c1a7fd62040ca018b08ca285216d26b1fee3c6b9',
 'mapping':'file_offset=VA-0x9ffff000','decoder':'Capstone '+capstone.__version__+' RV32+RVC',
 'exploration':'Finite receive discovery reads 80B at a0197954,80B at a01979a4,80B at a0197a2e,24B at a01979f0; distinct bytes264; no pop/release/wait bodies read',
 'windows':[{'start':hex(a),'end_exclusive':hex(z)} for a,z in windows],
 'sample_bytes':sum(z-a for a,z in windows),'rows':list(rows.values()),'checks':checks,
 'metadata_source':str(index_path),'metadata':metadata,
 'conclusion':'normal finite nonempty path passes internal Msg+c and Msg U16 length to original caller out via copy interface, then calls release(Msg); actual release semantics open',
 'limits':['Nonempty ready route only; not timeout/empty queue/scheduler bodies',
 'Actual message length derives Msg+0xa; Q size4 does not prove every received Msg length4 or same send instance',
 'Copy semantics require the appropriate inherited domain/address validity; real output not observed',
 'Internal message pop and release remain opaque callsites; no physical free or full queue lifecycle claim']}
dest=OUT/'receive-evidence.json'
if dest.exists():raise FileExistsError(dest)
dest.write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
print(json.dumps({'result':'PASS','checks':len(checks),'sample_bytes':result['sample_bytes']}))
