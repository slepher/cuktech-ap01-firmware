"""A67 independent mode2/open/encoded-H/close/interface review; no IO."""
import json
from pathlib import Path
import capstone
MAIN=Path('D:/Documents/PlatformIO/Projects/cuktech-ap01-firmware')
OUT=Path(__file__).resolve().parent
ROM=MAIN/'roms/0041/ap01-1.0.2_0041.bin';BASE=0x9ffff000
assert ROM.stat().st_size==6769704
md=capstone.Cs(capstone.CS_ARCH_RISCV,capstone.CS_MODE_RISCV32|capstone.CS_MODE_RISCVC)
windows=[(0xa00ef468,0xa00ef55e),(0xa008ab4c,0xa008ab76)]
rows={}
with ROM.open('rb') as f:
    for a,z in windows:
        f.seek(a-BASE);data=f.read(z-a);ins=list(md.disasm(data,a))
        assert sum(x.size for x in ins)==len(data)
        for x in ins:rows[x.address]={'pc':hex(x.address),'offset':hex(x.address-BASE),
            'raw':bytes(x.bytes).hex(),'asm':x.mnemonic+' '+x.op_str}
    f.seek(0xa06371e4-BASE);literal=f.read(4)
checks=[]
for pc,asm,meaning in [
 (0xa00ef468,'c.addi16sp sp, -0x110','open frame, not separate H allocation'),
 (0xa00ef476,'c.addi4spn s0, sp, 0x110','frame base relation'),
 (0xa00ef478,'c.li a5, 1','mode1 equality is false for selected mode2'),
 (0xa00ef47a,'c.mv a3, a1','save original suffix as first variadic value'),
 (0xa00ef47e,'beq a2, a5, 0x16','mode1 selector only'),
 (0xa00ef482,'c.li a5, 2','mode2 equality value'),
 (0xa00ef484,'c.li s1, 1','selected numeric open flags1'),
 (0xa00ef486,'beq a2, a5, 0xe','mode2 goes directly to format block'),
 (0xa00ef49c,'addi a1, zero, 0x100','format bound argument256, not verified output length'),
 (0xa00ef4a0,'addi a0, s0, -0x110','format destination same stack work area'),
 (0xa00ef4a8,'addi a2, zero, 0x1b6','open third numeric value'),
 (0xa00ef4ac,'c.mv a1, s1','open selected flags1'),
 (0xa00ef4ae,'addi a0, s0, -0x110','open destination path address, replacing formatter a0 result'),
 (0xa00ef4b6,'addi a5, a0, 1','compute low32(fd+1) before signed gate'),
 (0xa00ef4ba,'bgez a0, 0x36','nonnegative fd accepted'),
 (0xa00ef4c2,'lw a7, 0(a0)','open negative path reads first error slot'),
 (0xa00ef4ee,'c.li a5, 0','after logging normal return H0'),
 (0xa00ef4fc,'c.mv a0, a5','return encoded H value, no handle dereference'),
 (0xa00ef500,'c.jr ra','open return'),
 (0xa00ef50c,'addi s1, a1, -1','close decodes low32(H-1) from second argument'),
 (0xa00ef510,'c.mv a0, s1','close interface receives decoded fd'),
 (0xa00ef516,'c.mv a5, a0','save underlying close result'),
 (0xa00ef518,'c.li a0, 0','nonnegative result folded to0'),
 (0xa00ef51a,'bgez a5, 0x3a','signed nonnegative branch to common return'),
 (0xa00ef522,'lw a6, 0(a0)','first close error value used for log boundary'),
 (0xa00ef54e,'c.lw a0, 0(a0)','second getter result reread after log'),
 (0xa00ef55c,'c.jr ra','close common return preserves conversion a0'),
 (0xa008ab52,'c.addi4spn s0, sp, 0x20','wrapper frame relation'),
 (0xa008ab54,'c.sw a3, 0xc(s0)','first saved vararg is original suffix value'),
 (0xa008ab56,'addi a3, s0, 0xc','forward address of saved arguments'),
 (0xa008ab5a,'c.sw a4, 0x10(s0)','next packed word'),
 (0xa008ab5c,'c.sw a5, 0x14(s0)','next packed word'),
 (0xa008ab5e,'sw a6, 0x18(s0)','next packed word'),
 (0xa008ab62,'sw a7, 0x1c(s0)','last packed register word'),
 (0xa008ab74,'c.jr ra','wrapper returns lower result without rewriting a0'),
]:
    assert rows[pc]['asm']==asm,(hex(pc),rows[pc]['asm'])
    checks.append({'pc':hex(pc),'observed':asm,'meaning':meaning})
def w(pc):return int.from_bytes(bytes.fromhex(rows[pc]['raw']),'little')
def sx(x,b):return x-(1<<b) if x&(1<<(b-1)) else x
for pc,target in [(0xa00ef4a4,0xa008ab4c),(0xa008ab6a,0xa0053252),
                  (0xa00ef4b2,0xa003f4f6),(0xa00ef4be,0xa00267c0),
                  (0xa00ef4ea,0xa008b51a),(0xa00ef512,0xa0026888),
                  (0xa00ef51e,0xa00267c0),(0xa00ef546,0xa008b51a),
                  (0xa00ef54a,0xa00267c0),(0xa00ef550,0xa00ea524)]:
    v=w(pc);imm=((v>>31)<<20)|(((v>>12)&255)<<12)|(((v>>20)&1)<<11)|(((v>>21)&1023)<<1)
    assert v&127==0x6f and pc+sx(imm,21)==target
    checks.append({'pc':hex(pc),'target':hex(target),'meaning':'independent JAL; inherited/opaque body not read'})
for pc,target,expected in [(0xa00ef486,0xa00ef494,(99,0,12,15)),
                          (0xa00ef4ba,0xa00ef4f0,(99,5,10,0)),
                          (0xa00ef51a,0xa00ef554,(99,5,15,0))]:
    v=w(pc);imm=((v>>31)<<12)|(((v>>7)&1)<<11)|(((v>>25)&63)<<5)|(((v>>8)&15)<<1)
    assert (v&127,(v>>12)&7,(v>>15)&31,(v>>20)&31)==expected
    assert pc+sx(imm,13)==target
    checks.append({'pc':hex(pc),'target':hex(target),'meaning':'independent mode equality/signed nonnegative B-format'})
literal_address=(w(0xa00ef494)&0xfffff000)+sx(w(0xa00ef498)>>20,12)
assert literal_address==0xa06371e4 and literal==b'/%s\0'
checks.append({'meaning':'exact4B literal with NUL, not formatter output evidence',
 'address':hex(literal_address),'raw':literal.hex()})
for pc,rd,rs1,imm in [(0xa00ef4b6,15,10,1),(0xa00ef50c,9,11,-1)]:
    v=w(pc)
    assert (v&127,(v>>12)&7,(v>>7)&31,(v>>15)&31,sx(v>>20,12))==(19,0,rd,rs1,imm)
    checks.append({'pc':hex(pc),'meaning':'independent I-format low32 H arithmetic'})
after_format=[r['asm'] for pc,r in rows.items() if 0xa00ef4a8<=pc<0xa00ef4b2]
assert len(after_format)==3 and not any(s.startswith(('b','c.b')) for s in after_format)
checks.append({'meaning':'callback does not branch on or compare formatter return; next a0 replaced with buffer address'})
wrapper_tail=[r['asm'] for pc,r in rows.items() if 0xa008ab6e<=pc<0xa008ab76]
assert not any(s.split(' ',1)[1].startswith('a0') for s in wrapper_tail)
checks.append({'meaning':'wrapper tail does not replace formatter a0'})
close_tail=[r['asm'] for pc,r in rows.items() if 0xa00ef554<=pc<0xa00ef55e]
assert not any(s.split(' ',1)[1].startswith('a0') for s in close_tail)
checks.append({'meaning':'close common tail preserves0 or opaque conversion return'})
anchor_pcs={int(c['pc'],16) for c in checks if 'pc' in c}
result={'claim':'J08/7','review':'A67','reviewer':'/root/f12','baseline':'bd457a6','static_only':True,
 'source':str(ROM),'length':ROM.stat().st_size,
 'inherited_sha256':'972db4c136c7ed9e24a83c07c1a7fd62040ca018b08ca285216d26b1fee3c6b9',
 'mapping':'file_offset=VA-0x9ffff000','decoder':'Capstone '+capstone.__version__+' RV32+RVC',
 'windows':[{'start':hex(a),'end_exclusive':hex(z)} for a,z in windows],
 'read_bytes':sum(z-a for a,z in windows),'literal_bytes':len(literal),
 'anchor_bytes':sum(len(bytes.fromhex(rows[p]['raw'])) for p in anchor_pcs),
 'anchors':[rows[p] for p in sorted(anchor_pcs)],'checks':checks,
 'literal':{'address':hex(literal_address),'raw':literal.hex(),'meaning':'printf-family intent inference only'},
 'decision':'limited acceptance of A66 body; semantic correction0; new business0',
 'limits':['D-slot binding inherited as pending/conditional, not independently accepted by this body review',
 'Formatter body/output/truncation/NUL rule and actual path/IO/close/error-map semantics unknown',
 'Numeric H encoding is not FILE* or allocated handle structure; no direct free(H) claim is limited to callbacks',
 'No runtime fd identity/reuse/concurrency/lifetime or default photos mode1 conclusion']}
dest=OUT/'evidence.json'
if dest.exists():raise FileExistsError(dest)
dest.write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
print(json.dumps({'result':'PASS','checks':len(checks),'read_bytes':result['read_bytes'],'literal_bytes':len(literal),'anchor_bytes':result['anchor_bytes']}))
