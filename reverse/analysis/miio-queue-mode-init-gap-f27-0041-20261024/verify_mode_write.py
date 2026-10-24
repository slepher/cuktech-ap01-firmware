"""F27 approved same-Q first-word initialization block; no FS/open execution."""
import json
from pathlib import Path
import capstone
MAIN=Path('D:/Documents/PlatformIO/Projects/cuktech-ap01-firmware')
OUT=Path(__file__).resolve().parent
ROM=MAIN/'roms/0041/ap01-1.0.2_0041.bin';BASE=0x9ffff000
assert ROM.stat().st_size==6769704
md=capstone.Cs(capstone.CS_ARCH_RISCV,capstone.CS_MODE_RISCV32|capstone.CS_MODE_RISCVC)
# Discovery stopped at the first write and its local success cleanup/return.
# Other prefix arms/remaining530B body and all callees are out of scope.
a,z=0xa010e320,0xa010e43c
with ROM.open('rb') as f:f.seek(a-BASE);data=f.read(z-a)
ins=list(md.disasm(data,a));assert sum(x.size for x in ins)==len(data)
rows={x.address:{'pc':hex(x.address),'offset':hex(x.address-BASE),'raw':bytes(x.bytes).hex(),
                  'asm':x.mnemonic+' '+x.op_str} for x in ins}
checks=[]
for pc,asm,meaning in [
 (0xa010e338,'c.mv s5, a5','wrapper original arg5=0 retained'),
 (0xa010e33a,'lbu a5, 0(a1)','normal prefix starts from supplied name'),
 (0xa010e342,'c.beqz a5, 0x42','empty-name arm not called success'),
 (0xa010e344,'c.mv s3, a0','same Q saved'),
 (0xa010e348,'c.mv s6, a2','request flags7 saved'),
 (0xa010e35c,'andi s8, s6, 4','selected request-bit normal prefix'),
 (0xa010e392,'beq a4, a5, 0xaa','another name-prefix arm beyond samples remains conditional'),
 (0xa010e3d6,'bltz a0, 0x6a','local lookup nonnegative gate'),
 (0xa010e3e4,'lhu a5, 0xe(a5)','loaded object type field'),
 (0xa010e3e8,'c.andi a5, 0xf','only low4 type bits compared'),
 (0xa010e3ea,'bne a5, a4, 0x120','local success requires low4 bits5'),
 (0xa010e3ee,'c.li a2, 0x18','clear interface length24, not inferred full-Q size'),
 (0xa010e3f0,'c.li a1, 0','clear interface value0'),
 (0xa010e3f2,'c.mv a0, s3','clear interface same Q'),
 (0xa010e3fc,'sw s6, 0(s3)','actual Q.word0 request value write'),
 (0xa010e400,'sw a5, 0xc(s3)','separate Q+c field after word0'),
 (0xa010e404,'beqz s5, 0xa','wrapper arg5=0 skips auxiliary output write'),
 (0xa010e40e,'lw a0, -0x78(s0)','optional cleanup takes another local-loaded pointer'),
 (0xa010e412,'c.beqz a0, 0xa','skip cleanup if that pointer0'),
 (0xa010e418,'sw zero, -0x78(s0)','clear local cleanup slot only'),
 (0xa010e41c,'csrw mstatus, s4','restore saved mstatus'),
 (0xa010e420,'c.li s1, 0','local successful status0'),
 (0xa010e434,'c.mv a0, s1','common epilogue returns saved status'),
 (0xa010e43a,'c.jr ra','normal return'),
]:
    assert rows[pc]['asm']==asm,(hex(pc),rows[pc]['asm'])
    checks.append({'pc':hex(pc),'observed':asm,'meaning':meaning})
def w(pc):return int.from_bytes(bytes.fromhex(rows[pc]['raw']),'little')
def sx(x,b):return x-(1<<b) if x&(1<<(b-1)) else x
v=w(0xa010e3fc)
fields=(v&127,(v>>12)&7,(v>>15)&31,(v>>20)&31,((v>>25)<<5)|((v>>7)&31))
assert fields==(35,2,19,22,0)
checks.append({'pc':'0xa010e3fc','fields':fields,'meaning':'independent S-format full word store s6 to same Q base s3+0'})
assert 7&0x40==0
checks.append({'meaning':'at this exact store, initialized word7 has mask0x40 clear; not an all-return/later-state invariant'})
definitions=[]
for pc,r in rows.items():
    if 0xa010e348<pc<0xa010e3fc:
        m,o=r['asm'].split(' ',1)
        if m not in ['sw','sb','sh','c.sw','c.swsp'] and o.split(',')[0] in ['s3','s6']:
            definitions.append(r)
assert not definitions
checks.append({'meaning':'no explicit Q/flags register redefinition in inspected prefix; normal callees preserve saved registers',
 'limit':'unread name/creation arms are not silently joined or certified'})
for pc,target in [(0xa010e3d2,0xa01a3772),(0xa010e3f4,0xa0024906),(0xa010e414,0xa002e14e)]:
    v=w(pc);imm=((v>>31)<<20)|(((v>>12)&255)<<12)|(((v>>20)&1)<<11)|(((v>>21)&1023)<<1)
    assert v&127==0x6f and pc+sx(imm,21)==target
    checks.append({'pc':hex(pc),'target':hex(target),'meaning':'independent normal-boundary JAL; body not read'})
anchor_pcs={int(c['pc'],16) for c in checks if 'pc' in c}
result={'claim':'F11/10','task':'F27','baseline':'bd457a6','static_only':True,
 'rom':str(ROM),'length':ROM.stat().st_size,
 'inherited_sha256':'972db4c136c7ed9e24a83c07c1a7fd62040ca018b08ca285216d26b1fee3c6b9',
 'mapping':'file_offset=VA-0x9ffff000','decoder':'Capstone '+capstone.__version__+' RV32+RVC',
 'window':{'start':hex(a),'end_exclusive':hex(z),'read_bytes':z-a},
 'anchors':[rows[p] for p in sorted(anchor_pcs)],
 'prefix_width_checkpoints':[{'pc':hex(p),'bytes':len(bytes.fromhex(r['raw']))} for p,r in rows.items()],
 'checks':checks,
 'conclusion':'selected normal common initialization block stores original request7 as full word(Q) before local cleanup/return',
 'limits':['Normal path reaching the block, valid Q/object and callee-saved register preconditions; unread path arms not certified',
 'Optional post-write cleanup interface can only be excluded as a direct Q argument, not all alias effects',
 'No unconditional complete successful-open return value or later mode invariant',
 'No formal O_NONBLOCK name, filesystem/provider/allocator/driver body or execution']}
dest=OUT/'mode-write-evidence.json'
if dest.exists():raise FileExistsError(dest)
dest.write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
print(json.dumps({'result':'PASS','checks':len(checks),'read_bytes':z-a,'anchor_bytes':sum(len(bytes.fromhex(rows[p]['raw'])) for p in anchor_pcs)}))
