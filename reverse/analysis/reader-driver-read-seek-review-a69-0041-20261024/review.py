"""A69 independent fields for registered read/seek callbacks, no IO execution."""
import json
from pathlib import Path
import capstone
MAIN=Path('D:/Documents/PlatformIO/Projects/cuktech-ap01-firmware')
OUT=Path(__file__).resolve().parent
ROM=MAIN/'roms/0041/ap01-1.0.2_0041.bin';BASE=0x9ffff000
assert ROM.stat().st_size==6769704
md=capstone.Cs(capstone.CS_ARCH_RISCV,capstone.CS_MODE_RISCV32|capstone.CS_MODE_RISCVC)
windows=[(0xa00ef55e,0xa00ef5c8),(0xa00ef632,0xa00ef69c)]
rows={}
with ROM.open('rb') as f:
    for a,z in windows:
        f.seek(a-BASE);data=f.read(z-a);ins=list(md.disasm(data,a))
        assert sum(x.size for x in ins)==len(data)
        for x in ins:rows[x.address]={'pc':hex(x.address),'offset':hex(x.address-BASE),
            'raw':bytes(x.bytes).hex(),'asm':x.mnemonic+' '+x.op_str}
checks=[]
for pc,asm,meaning in [
 (0xa00ef55e,'c.addi sp, -0x20','actual read entry, not adjacent write body'),
 (0xa00ef562,'c.mv s1, a1','save second-argument H value'),
 (0xa00ef56a,'c.addi s1, -1','low32 H-1 decode'),
 (0xa00ef56c,'c.mv a1, a2','original buffer word to arg1'),
 (0xa00ef56e,'c.mv a0, s1','decoded fd to arg0'),
 (0xa00ef570,'c.mv a2, a3','original count word to arg2'),
 (0xa00ef572,'sw a4, -0x14(s0)','save original out_count address across IO interface'),
 (0xa00ef57a,'lw a4, -0x14(s0)','reload same out_count address'),
 (0xa00ef57e,'bgez a0, 0x44','signed result>=0, including zero, selects output store'),
 (0xa00ef586,'lw a6, 0(a0)','read first error word for log only'),
 (0xa00ef5b2,'c.lw a0, 0(a0)','log-following second getter/read before mapping'),
 (0xa00ef5c0,'c.jr ra','common read return preserves mapper a0'),
 (0xa00ef5c2,'c.sw a0, 0(a4)','success writes whole returned count word'),
 (0xa00ef5c4,'c.li a0, 0','callback success status0, not count return'),
 (0xa00ef5c6,'c.j -0xe','success goes to common read epilogue'),
 (0xa00ef632,'c.li a5, 2','actual seek entry origin limit'),
 (0xa00ef634,'c.li a0, 0xb','out-of-range direct status11'),
 (0xa00ef636,'bltu a5, a3, 0x64','unsigned2<origin returns before frame and IO'),
 (0xa00ef63a,'c.addi sp, -0x10','allowed-origin path allocates frame after gate'),
 (0xa00ef63e,'c.mv s1, a1','seek H comes from original second argument'),
 (0xa00ef646,'c.addi s1, -1','seek low32 H-1'),
 (0xa00ef648,'c.mv a1, a2','original position word to explicit arg1'),
 (0xa00ef64a,'c.mv a2, a3','original origin word to explicit arg2'),
 (0xa00ef64c,'c.mv a0, s1','seek explicit arg0 decoded fd'),
 (0xa00ef652,'c.mv a5, a0','save lower result word a0'),
 (0xa00ef654,'c.li a0, 0','success folded to callback0'),
 (0xa00ef656,'bgez a5, 0x3a','only signed a0 lower result governs success'),
 (0xa00ef65e,'lw a6, 0(a0)','first seek error word used for log only'),
 (0xa00ef68a,'c.lw a0, 0(a0)','second seek getter/read before map'),
 (0xa00ef698,'c.jr ra','seek common return preserves0 or mapper result'),
 (0xa00ef69a,'c.jr ra','early origin return without frame construction'),
]:
    assert rows[pc]['asm']==asm,(hex(pc),rows[pc]['asm'])
    checks.append({'pc':hex(pc),'observed':asm,'meaning':meaning})
def w(pc):return int.from_bytes(bytes.fromhex(rows[pc]['raw']),'little')
def sx(x,b):return x-(1<<b) if x&(1<<(b-1)) else x
for pc,target in [(0xa00ef576,0xa003f6a2),(0xa00ef582,0xa00267c0),
                  (0xa00ef5aa,0xa008b51a),(0xa00ef5ae,0xa00267c0),
                  (0xa00ef5b4,0xa00ea524),(0xa00ef64e,0xa00281d8),
                  (0xa00ef65a,0xa00267c0),(0xa00ef682,0xa008b51a),
                  (0xa00ef686,0xa00267c0),(0xa00ef68c,0xa00ea524)]:
    v=w(pc);imm=((v>>31)<<20)|(((v>>12)&255)<<12)|(((v>>20)&1)<<11)|(((v>>21)&1023)<<1)
    assert v&127==0x6f and pc+sx(imm,21)==target
    checks.append({'pc':hex(pc),'target':hex(target),'meaning':'independent JAL target; body not read'})
for pc,target,expected in [(0xa00ef57e,0xa00ef5c2,(99,5,10,0)),
                          (0xa00ef636,0xa00ef69a,(99,6,15,13)),
                          (0xa00ef656,0xa00ef690,(99,5,15,0))]:
    v=w(pc);imm=((v>>31)<<12)|(((v>>7)&1)<<11)|(((v>>25)&63)<<5)|(((v>>8)&15)<<1)
    assert (v&127,(v>>12)&7,(v>>15)&31,(v>>20)&31)==expected
    assert pc+sx(imm,13)==target
    checks.append({'pc':hex(pc),'target':hex(target),'meaning':'independent signed result/unsigned origin B-format'})
v=w(0xa00ef5c2)
offset=(((v>>5)&1)<<6)|(((v>>10)&7)<<3)|(((v>>6)&1)<<2)
assert (v&3,(v>>13)&7,8+((v>>7)&7),8+((v>>2)&7),offset)==(0,6,14,10,0)
checks.append({'pc':'0xa00ef5c2','meaning':'independent C.SW full count word to original out address'})
v=w(0xa00ef572)
assert (v&127,(v>>12)&7,(v>>15)&31,(v>>20)&31,sx(((v>>25)<<5)|((v>>7)&31),12))==(35,2,8,14,-0x14)
checks.append({'pc':'0xa00ef572','meaning':'independent S-format saved output pointer is word, not count'})
read_stores=[r['pc'] for pc,r in rows.items() if 0xa00ef582<=pc<0xa00ef5c2 and
             r['asm'].split(' ',1)[0] in ['sb','sh','sw','c.sw','c.swsp']]
assert not read_stores
checks.append({'meaning':'read negative callback path has no direct store/initialization of out_count',
               'limit':'opaque IO/log/getter/map side effects and aliasing not excluded'})
seek_setup=[r for pc,r in rows.items() if 0xa00ef646<=pc<0xa00ef64e]
assert len(seek_setup)==4 and not any(r['asm'].startswith(('srai ','sra ','srli ','c.srai ','c.srli ')) for r in seek_setup)
checks.append({'meaning':'explicit seek transfer is low-word H arithmetic plus register words; no separately constructed position high word or sign extension',
               'limit':'does not certify lower off_t/prototype/full argument count or return width'})
anchor_pcs={int(c['pc'],16) for c in checks if 'pc' in c}
result={'claim':'J08/8','review':'A69','reviewer':'/root/f12','baseline':'bd457a6','static_only':True,
 'source':str(ROM),'length':ROM.stat().st_size,
 'inherited_sha256':'972db4c136c7ed9e24a83c07c1a7fd62040ca018b08ca285216d26b1fee3c6b9',
 'mapping':'file_offset=VA-0x9ffff000','decoder':'Capstone '+capstone.__version__+' RV32+RVC',
 'windows':[{'start':hex(a),'end_exclusive':hex(z)} for a,z in windows],
 'read_bytes':sum(z-a for a,z in windows),'anchor_bytes':sum(len(bytes.fromhex(rows[p]['raw'])) for p in anchor_pcs),
 'anchors':[rows[p] for p in sorted(anchor_pcs)],'checks':checks,
 'decision':'limited acceptance of A68; semantic correction0; new business0',
 'limits':['No adjacent write owner body, IO, error getter/map or logger body read',
 'Explicit callback word transfers do not certify lower off_t/ssize_t/full ABI',
 'No actual output/buffer validity, memory lifetime/retention or IO success observation',
 'A70 numerical map independent; result mapper remains opaque at this review boundary']}
dest=OUT/'evidence.json'
if dest.exists():raise FileExistsError(dest)
dest.write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
print(json.dumps({'result':'PASS','checks':len(checks),'read_bytes':result['read_bytes'],'anchor_bytes':result['anchor_bytes']}))
