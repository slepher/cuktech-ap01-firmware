"""A63 independent registry-call/node-D bridge and s1 path continuity only."""
import json
from pathlib import Path
import capstone
MAIN=Path('D:/Documents/PlatformIO/Projects/cuktech-ap01-firmware')
OUT=Path(__file__).resolve().parent
ROM=MAIN/'roms/0041/ap01-1.0.2_0041.bin';BASE=0x9ffff000
assert ROM.stat().st_size==6769704
md=capstone.Cs(capstone.CS_ARCH_RISCV,capstone.CS_MODE_RISCV32|capstone.CS_MODE_RISCVC)
# Straight prefix is inspected only for instruction widths/control and s1 writes;
# no driver slot semantics or callback targets are recovered here.
windows=[(0xa008e75e,0xa008e7ec),(0xa008e826,0xa008e82c)]
all_rows={}
with ROM.open('rb') as f:
    for a,z in windows:
        f.seek(a-BASE);data=f.read(z-a);ins=list(md.disasm(data,a))
        assert sum(x.size for x in ins)==len(data)
        for x in ins:all_rows[x.address]={'pc':hex(x.address),'offset':hex(x.address-BASE),
            'raw':bytes(x.bytes).hex(),'mnemonic':x.mnemonic,'operands':x.op_str}
checks=[]
def expect(pc,asm,meaning):
    r=all_rows[pc];actual=r['mnemonic']+' '+r['operands']
    assert actual==asm,(hex(pc),actual,asm)
    checks.append({'pc':hex(pc),'observed':actual,'meaning':meaning})
for pc,asm,meaning in [
 (0xa008e75e,'lui s1, 0x62fc9','s1 is high constant, not A60 G value'),
 (0xa008e764,'addi a1, zero, 0x34','clear-interface size argument inherited'),
 (0xa008e768,'addi a0, s1, 0x74c','driver global address D'),
 (0xa008e7d8,'lui a0, 0x62fc9','actual list a0 upper'),
 (0xa008e7dc,'c.sw a4, 0x78(a5)','intervening store does not overwrite a0 or s1; no slot identity claim'),
 (0xa008e7de,'addi a0, a0, 0x740','actual list address0x62fc9740'),
 (0xa008e7e6,'c.bnez a0, 0x40','nonnull node takes direct success edge'),
 (0xa008e7e8,'lui s1, 0xa0263','null branch first s1 overwrite skipped on success'),
 (0xa008e826,'addi s1, s1, 0x74c','high constant becomes D only on selected success'),
 (0xa008e82a,'c.sw s1, 0(a0)','return node word0 receives same D'),
]:expect(pc,asm,meaning)
def w(pc):return int.from_bytes(bytes.fromhex(all_rows[pc]['raw']),'little')
def sx(x,b):return x-(1<<b) if x&(1<<(b-1)) else x
for pc,target in [(0xa008e76c,0xa0080d8e),(0xa008e7e2,0xa008aec0)]:
    v=w(pc);imm=((v>>31)<<20)|(((v>>12)&255)<<12)|(((v>>20)&1)<<11)|(((v>>21)&1023)<<1)
    assert v&127==0x6f and pc+sx(imm,21)==target
    checks.append({'pc':hex(pc),'target':hex(target),'meaning':'independent JAL target; helper body inherited'})
for pc,rd,rs1,imm in [(0xa008e768,10,9,0x74c),(0xa008e7de,10,10,0x740),
                       (0xa008e826,9,9,0x74c)]:
    v=w(pc)
    assert (v&127,(v>>12)&7,(v>>7)&31,(v>>15)&31,sx(v>>20,12))==(19,0,rd,rs1,imm)
    checks.append({'pc':hex(pc),'meaning':'independent I-format register/base/immediate'})
v=w(0xa008e7e6)
imm=(((v>>12)&1)<<8)|(((v>>10)&3)<<3)|(((v>>5)&3)<<6)|(((v>>3)&3)<<1)|(((v>>2)&1)<<5)
assert (v&3,(v>>13)&7,8+((v>>7)&7))==(1,7,10)
assert 0xa008e7e6+sx(imm,9)==0xa008e826
checks.append({'pc':'0xa008e7e6','target':'0xa008e826','meaning':'independent C.BNEZ normal edge skips error s1 overwrite'})
v=w(0xa008e82a)
offset=(((v>>5)&1)<<6)|(((v>>10)&7)<<3)|(((v>>6)&1)<<2)
assert (v&3,(v>>13)&7,8+((v>>7)&7),8+((v>>2)&7),offset)==(0,6,10,9,0)
checks.append({'pc':'0xa008e82a','meaning':'independent C.SW word width, base=a0, source=s1, offset0'})
checkpoints=[];calls=[];definitions=[];branches=[]
for pc,r in all_rows.items():
    if 0xa008e75e<pc<0xa008e7e6:
        m,o=r['mnemonic'],r['operands']
        if m in ['jal','jalr','c.jalr']:calls.append(hex(pc))
        if m.startswith(('b','c.b')) or m in ['j','c.j','c.jr']:branches.append(hex(pc))
        # Memory stores have a source first operand, not a register destination.
        if m not in ['sw','sb','sh','c.sw','c.swsp'] and o.split(',')[0]=='s1':definitions.append(hex(pc))
        checkpoints.append({'pc':hex(pc),'bytes':len(bytes.fromhex(r['raw']))})
assert not definitions and not branches
assert calls==['0xa008e76c','0xa008e7e2']
checks.append({'meaning':'normal straight prefix has no explicit s1 redefinition or extra control transfer',
 'calls':calls,'condition':'both inherited helpers return normally and obey callee-saved s1; no helper-body validation'})
assert 0x62fc9000+0x740==0x62fc9740 and 0x62fc9000+0x74c==0x62fc974c
checks.append({'meaning':'actual header and D independently formed from constant high word',
 'header':'0x62fc9740','D':'0x62fc974c'})

old_path=MAIN/'reverse/analysis/png-info-lifecycle-a21-0041-20261023/instruction-evidence.json'
old=json.loads(old_path.read_text(encoding='utf-8'))
def select(x):
    out=[]
    if isinstance(x,dict):
        if x.get('address') in ['0xa008e75e','0xa008e764']:out.append(x)
        else:
            for v in x.values():out+=select(v)
    elif isinstance(x,list):
        for v in x:out+=select(v)
    return out
old_rows=select(old);assert len(old_rows)==2
checks.append({'meaning':'two necessary old A21 endpoint rows available; old helper body not reread'})
anchor_pcs={0xa008e75e,0xa008e762,0xa008e764,0xa008e768,0xa008e76c,
            0xa008e7d8,0xa008e7dc,0xa008e7de,0xa008e7e2,0xa008e7e6,
            0xa008e7e8,0xa008e826,0xa008e82a}
result={'claim':'J08/5','review':'A63','reviewer':'/root/f12','baseline':'bd457a6','static_only':True,
 'source':str(ROM),'length':ROM.stat().st_size,
 'inherited_sha256':'972db4c136c7ed9e24a83c07c1a7fd62040ca018b08ca285216d26b1fee3c6b9',
 'mapping':'file_offset=VA-0x9ffff000','decoder':'Capstone '+capstone.__version__+' RV32+RVC',
 'windows':[{'start':hex(a),'end_exclusive':hex(z)} for a,z in windows],
 'read_bytes':sum(z-a for a,z in windows),'anchor_bytes':sum(len(bytes.fromhex(all_rows[p]['raw'])) for p in anchor_pcs),
 'anchors':[all_rows[p] for p in sorted(anchor_pcs)],'prefix_width_checkpoints':checkpoints,'checks':checks,
 'inherited_A21':{'path':str(old_path),'rows':old_rows},
 'helper_contract':'A21/A22 insert_head returns linked node or NULL; helper publishes node before caller stores D',
 'initialization_status':'A60 now limited-accepted by A61; A62 earlier pending text is historical',
 'decision':'limited acceptance; semantic correction0; new business0',
 'limits':['Normal successful helper return with callee-saved s1, not verified arbitrary helper/clobber behavior',
 'No driver letter/callback slot/source-path binding or structure identity from incidental stores',
 'No actual registration execution, concurrent visibility, node/D lifetime or later writer certification']}
dest=OUT/'evidence.json'
if dest.exists():raise FileExistsError(dest)
dest.write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
print(json.dumps({'result':'PASS','checks':len(checks),'read_bytes':result['read_bytes'],'anchor_bytes':result['anchor_bytes']}))
