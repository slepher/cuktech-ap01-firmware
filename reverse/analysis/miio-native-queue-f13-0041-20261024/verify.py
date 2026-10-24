"""F13 static, bounded original-byte checks. Never executes target instructions."""
import json
from pathlib import Path
import capstone

MAIN=Path('D:/Documents/PlatformIO/Projects/cuktech-ap01-firmware')
ROM=MAIN/'roms/0041/ap01-1.0.2_0041.bin'
OUT=Path(__file__).resolve().parent
BASE=0x9ffff000
assert ROM.stat().st_size==6769704
md=capstone.Cs(capstone.CS_ARCH_RISCV,capstone.CS_MODE_RISCV32|capstone.CS_MODE_RISCVC)
# Actual a2 == -1 caller route only. The timeout route is not analyzed.
WINDOWS=[(0xa005f464,0xa005f498),
 (0xa0197a8e,0xa0197ad2),(0xa0197ae8,0xa0197afe),
 (0xa0197afe,0xa0197b32),
 (0xa0194a00,0xa0194a50),(0xa0194a60,0xa0194a68),
 (0xa0194ac0,0xa0194ae2),(0xa0194b3c,0xa0194b4e)]
rows={}
with ROM.open('rb') as f:
    for a,z in WINDOWS:
        f.seek(a-BASE);data=f.read(z-a)
        decoded=list(md.disasm(data,a))
        assert sum(i.size for i in decoded)==len(data)
        for i in decoded:rows[i.address]={'pc':hex(i.address),
            'file_offset':hex(i.address-BASE),'raw':bytes(i.bytes).hex(),
            'asm':i.mnemonic+' '+i.op_str}
checks=[]
def expect(pc,asm,meaning):
    assert rows[pc]['asm']==asm,(hex(pc),rows[pc]['asm'],asm)
    checks.append({'pc':hex(pc),'observed':asm,'meaning':meaning})
for pc,asm,meaning in [
 (0xa005f464,'c.beqz a0, 0xa0','null queue guard to a005f504'),
 (0xa005f474,'c.li a5, -1','infinite wait comparison'),
 (0xa005f476,'c.mv s2, a0','preserve queue'),
 (0xa005f478,'c.mv s1, a2','preserve caller wait'),
 (0xa005f47a,'bne a2, a5, 0x1e','actual -1 takes fallthrough'),
 (0xa005f47e,'c.lw a2, 0x18(a0)','callee length from queue+18'),
 (0xa005f480,'auipc ra, 0x138','downstream target upper'),
 (0xa005f484,'jalr ra, ra, 0x60e','downstream target lower'),
 (0xa005f492,'c.srai a0, 0x1f','return sign fold: nonnegative to0, negative to-1'),
 (0xa005f496,'c.jr ra','return after sign fold'),
 (0xa0197a8e,'c.lw a5, 0xc(a0)','adapter object link'),
 (0xa0197aa2,'c.lw s1, 0x18(a5)','inner queue object'),
 (0xa0197aa4,'c.beqz a1, 0x80','source null gate'),
 (0xa0197ab0,'lhu a5, 0x24(s1)','unsigned queue size limit'),
 (0xa0197ab4,'bltu a5, a2, 0x78','source length limit gate'),
 (0xa0197ab8,'c.mv s4, a2','preserve length'),
 (0xa0197aba,'c.mv s3, a1','preserve source pointer'),
 (0xa0197abc,'c.li s2, 8','mstatus clear mask0x8'),
 (0xa0197abe,'csrrc s2, mstatus, s2','preserve prior mstatus and clear supplied mask'),
 (0xa0197ad0,'c.bnez a0, 0x42','nonzero message service result to commit path'),
 (0xa0197afe,'csrw mstatus, s2','restore saved mstatus before return'),
 (0xa0197b12,'c.mv a1, a0','message result as lower arg1'),
 (0xa0197b14,'c.mv a3, s4','length as lower arg3'),
 (0xa0197b16,'c.mv a2, s3','source pointer as lower arg2'),
 (0xa0197b18,'c.mv a0, s1','inner queue as lower arg0'),
 (0xa0194a00,'c.mv s2, a1','preserve candidate message M'),
 (0xa0194a02,'c.mv s1, a0','preserve inner queue K'),
 (0xa0194a04,'c.mv a1, a2','source as copy arg1'),
 (0xa0194a06,'sh a3, 0xa(s2)','length stored as halfword to M+a'),
 (0xa0194a0a,'c.mv a2, a3','length as copy arg2'),
 (0xa0194a0c,'sb zero, 9(s2)','byte M+9 cleared'),
 (0xa0194a10,'addi a0, s2, 0xc','M+c as copy destination'),
 (0xa0194a1c,'c.lw a3, 0x1c(s1)','read list only after copy call'),
 (0xa0194a20,'addi a2, s1, 0x18','list sentinel address'),
 (0xa0194a30,'sw a5, 0(s2)','link field uses node, not original source'),
 (0xa0194a34,'sw a4, 4(s2)','second message link'),
 (0xa0194a3a,'sw s2, 0(a4)','publish M in previous node'),
 (0xa0194a3e,'sw s2, 4(a5)','publish M in next node'),
 (0xa0194a42,'lh a5, 0x22(s1)','reload signed count'),
 (0xa0194a46,'addi a4, a5, 1','increment count'),
 (0xa0194a4a,'sh a4, 0x22(s1)','store count halfword'),
 (0xa0194a60,'c.lw a5, 0x28(s1)','post-link notification gate'),
 (0xa0194ac6,'sw a3, 4(s2)','append message link'),
 (0xa0194aca,'sw a4, 0(s2)','append message other link'),
 (0xa0194ad0,'sw s2, 0(a5)','append publish M'),
 (0xa0194ad4,'sw s2, 0x1c(s1)','queue tail update with M'),
 (0xa0194ada,'lh a5, 0x12(s1)','waiter count gate only; service bodies excluded'),
 (0xa0194b48,'c.li a0, 0','common normal epilogue return zero'),
 (0xa0194b4c,'c.jr ra','lower return'),
]:expect(pc,asm,meaning)
def sx(n,b):return n-(1<<b) if n&(1<<(b-1)) else n
def w(pc):return int.from_bytes(bytes.fromhex(rows[pc]['raw']),'little')
target=(0xa005f480+sx(w(0xa005f480)&0xfffff000,32)+sx(w(0xa005f484)>>20,12))&0xfffffffe
assert target==0xa0197a8e
checks.append({'pc':'0xa005f480','target':hex(target),'meaning':'independent AUIPC/JALR fields'})
copytarget=(0xa0194a14+sx(w(0xa0194a14)&0xfffff000,32)+sx(w(0xa0194a18)>>20,12))&0xfffffffe
assert copytarget==0xa000589c
checks.append({'pc':'0xa0194a14','target':hex(copytarget),'meaning':'copy interface target; body-domain inherited, not generalized'})
def jal(pc,expected):
    v=w(pc)
    imm=((v>>31)<<20)|(((v>>12)&255)<<12)|(((v>>20)&1)<<11)|(((v>>21)&1023)<<1)
    assert v&127==0x6f and pc+sx(imm,21)==expected
    checks.append({'pc':hex(pc),'target':hex(expected),'meaning':'independent JAL fields; callee body not read'})
jal(0xa0197acc,0xa01318de)
jal(0xa0197af8,0xa0131920)
jal(0xa0197b1a,0xa01949f0)

index_path=MAIN/'reverse/analysis/whole-rom-coverage-0041-20261023-round1.json'
index=json.loads(index_path.read_text(encoding='utf-8'))
selected=[]
for i,r in enumerate(index['functions']):
    if r['address'] in ['0xa005f464','0xa0197a8e','0xa01949f0']:
        selected.append({'pointer':'#/functions/'+str(i),'metadata':r})
assert len(selected)==3
result={'claim':'F11/3','task':'F13','baseline':'bd457a6','static_only':True,
 'identity':{'path':str(ROM),'length':ROM.stat().st_size,
  'inherited_sha256':'972db4c136c7ed9e24a83c07c1a7fd62040ca018b08ca285216d26b1fee3c6b9',
  'mapping':'file_offset=VA-0x9ffff000'},
 'decoder':'Capstone '+capstone.__version__+' RV32+RVC',
 'exploratory_read_note':'Discovery reads: adapter 64B at a005f464; selected service 164B in three consecutive bounded reads; lower helper 96B at a01949f0,52B at a0194a50,50B at a0194ac0,38B at a0194b38. Only semantic samples retained below; no helper-body export or execution.',
 'windows':[{'start':hex(a),'end_exclusive':hex(z)} for a,z in WINDOWS],
 'rows':list(rows.values()),'checks':checks,
 'metadata_source':str(index_path),'metadata':selected,
 'limits':['No timeout branch body','No a1 source dereference in adapter path',
 'queue+18 actual value not established; no unconditional pointer4B claim',
 'Existing copy body contract only aligned16/20B; this callsite does not establish arbitrary length semantics',
 'Allocator/wait/scheduler/notification services remain opaque; no runtime observation',
 'Lower helper only sampled normal copy/link/gates and common epilogue; not full service restoration']}
dest=OUT/'evidence.json'
if dest.exists():raise FileExistsError(dest)
dest.write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
print(json.dumps({'result':'PASS','checks':len(checks),'bytes':sum(z-a for a,z in WINDOWS)}))
