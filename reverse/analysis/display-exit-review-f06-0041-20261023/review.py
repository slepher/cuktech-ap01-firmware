"""Independent F06 static ROM review; no target execution or F05 script import."""
import json
from pathlib import Path
import capstone
from capstone import Cs, CS_ARCH_RISCV, CS_MODE_RISCV32, CS_MODE_RISCVC

OUT = Path(__file__).resolve().parent
ROOT = Path('D:/Documents/PlatformIO/Projects/cuktech-ap01-firmware')
ROM = (ROOT/'roms/0041/ap01-1.0.2_0041.bin').read_bytes()
BASE = 0x9ffff000
md = Cs(CS_ARCH_RISCV, CS_MODE_RISCV32 | CS_MODE_RISCVC)
spans = [
 ('caller',0xa005cc9c,0xa005ccd8),('caller_return',0xa005cebe,0xa005ced2),
 ('initializer_entry',0xa0084b96,0xa0084bd2),
 ('object_allocation',0xa0084d9a,0xa0084e32),
 ('payload',0xa0084e32,0xa0084e84),
 ('backend_install',0xa0086ca8,0xa0086ce2),
 ('backend_fd',0xa0086d26,0xa0086d44),('publish',0xa00873b6,0xa0087412),
 ('list_allocator',0xa008aec0,0xa008af14),('zero_wrapper',0xa0080d8e,0xa0080da6),
 ('payload_default',0xa0081978,0xa0081a36),
 ('registration_wrapper',0xa007ffa0,0xa0080002),
 ('registration',0xa01b93b4,0xa01b951c),
 ('sender',0xa00814f4,0xa0081554),('dispatch',0xa008acfa,0xa008adf4),
 ('backend_callback',0xa00800b4,0xa0080134),('backend_getter',0xa007fe32,0xa007fe4e),
 ('delete',0xa0081554,0xa0081646),('free_wrapper',0xa008ab8a,0xa008abb0),
]
custom = {0xa008ad78:'th.extu a3,a5,15,15',0xa01b94f2:'th.mula a0,a2,a5'}
rows = {}; windows = []; text = []
for name,a,z in spans:
    p=a; rr=[]; text.append('\n'+name)
    while p<z:
        b=ROM[p-BASE:p-BASE+4]; n=4 if b[0]&3==3 else 2
        i=next(md.disasm(b[:n],p),None)
        assert p+n<=z,(name,hex(p),n,hex(z))
        asm=i.mnemonic+' '+i.op_str if i else custom.get(p,'UNDECODED')
        assert asm!='UNDECODED',(hex(p),b.hex())
        row=dict(pc=hex(p),raw=b[:n].hex(),asm=asm)
        rows[p]=row;rr.append(row);text.append(f'{p:08x} {b[:n].hex():8} {asm}')
        p+=n
    windows.append(dict(name=name,start=hex(a),end=hex(z),instructions=rr))

checks=[]
def expect(pc,asm):
    assert rows[pc]['asm']==asm,(hex(pc),rows[pc],asm)
    checks.append(dict(pc=hex(pc),asm=asm))
def sx(v,b):return v-(1<<b) if v&(1<<(b-1)) else v
def direct(pc,target):
    w=int.from_bytes(ROM[pc-BASE:pc-BASE+4],'little')
    if w&127==0x6f:
        off=sx((w>>31)<<20|((w>>12)&255)<<12|((w>>20)&1)<<11|((w>>21)&1023)<<1,21)
    else:
        assert w&127==0x17
        v=int.from_bytes(ROM[pc-BASE+4:pc-BASE+8],'little')
        assert v&127==0x67 and ((w>>7)&31)==((v>>15)&31)
        off=sx(w&0xfffff000,32)+sx(v>>20,12)
    assert (pc+off)&0xffffffff==target
    checks.append(dict(pc=hex(pc),target=hex(target),method='raw immediate fields'))

for pc,asm in {
 0xa005ccae:'sw a5, -0x308(s0)',0xa005ccc2:'sw a5, -0x304(s0)',
 0xa005ccba:'addi a1, s0, -0x314',0xa005ccbe:'addi a0, s0, -0x308',
 0xa005cebe:'addi a1, s0, -0x314',0xa005cec2:'addi a0, s0, -0x240',
 0xa005ceca:'lw a0, -0x314(s0)',0xa0084bb4:'sw a0, -0xa4(s0)',0xa0084bba:'c.mv s7, a1',
 0xa0084d9e:'addi a0, a0, 0x580',0xa0084da6:'c.mv s1, a0',
 0xa0084de8:'addi a1, zero, 0x324',0xa0080d96:'c.mv a2, a1',0xa0080d98:'c.li a1, 0',
 0xa0084e26:'addi a0, zero, 0x58',0xa0084e2e:'sw a0, 0x2b0(s1)',
 0xa0084e72:'lw a5, 0x2b4(s1)',0xa0084e7e:'c.jalr a5',
 0xa0081a1c:'addi a1, zero, 0x58',0xa00819c8:'c.sw a5, 0x38(a0)',0xa00819ca:'sb zero, 0x3c(a0)',
 0xa0086cc2:'sw a5, 0(s5)',0xa0086cc6:'sw s5, 0x2e0(s1)',
 0xa0086cb0:'lui a1, 0xa0080',0xa0086cce:'addi a1, a1, 0xb4',
 0xa0086cb4:'c.mv a3, s1',0xa0086cca:'addi a2, zero, 0x29',0xa0086cd2:'c.mv a0, s1',
 0xa00873ea:'sw s1, 0(s7)',0xa007ffec:'addi a0, a0, 0x2e8',
 0xa01b93c2:'c.li a0, 0xc',0xa01b9432:'c.sw a1, 0(a0)',
 0xa01b9438:'c.sw a2, 8(a5)',0xa01b943a:'c.sw a3, 4(a5)',
 0xa01b9502:'c.sw a5, 4(s1)',0xa0081516:'sw s1, -0x2c(s0)',
 0xa008151a:'sw s1, -0x28(s0)',0xa0081522:'sw a2, -0x1c(s0)',0xa008152e:'sw s2, -0x24(s0)',
 0xa0081538:'bne a0, a5, 0x10',0xa008153c:'c.li a2, 0',
 0xa008ad42:'c.lui s5, 0xffff8',0xa008ad50:'c.addi s5, -1',
 0xa008ad4e:'c.lui s8, 0x10',0xa008ad72:'and a3, a5, s8',
 0xa008ad80:'and a5, a5, s5',0xa008ad8a:'bne a5, a3, -0x1e',
 0xa008ad8e:'c.lw a5, 4(a4)',0xa008ad92:'sw a5, 0xc(s3)',
 0xa008ad96:'c.lw a5, 0(a4)',0xa008ad98:'c.jalr a5',
 0xa008ad9e:'andi s1, a5, 2',0xa008ada4:'c.andi a5, 1',
 0xa00800c0:'lw s2, 0xc(a0)',0xa00800ce:'bnez s2, 0x10',
 0xa00800de:'sw zero, 0x2e0(s2)',0xa00800e2:'sw zero, 0x2c(s2)',
 0xa00800e6:'c.lw a0, 0(s1)',0xa00800e8:'bltz a0, 0xc',
 0xa00800f2:'c.sw a5, 0(s1)',0xa00800f4:'c.lw a0, 0x34(s1)',
 0xa00800fc:'sw zero, 0x34(s1)',0xa0080100:'c.mv a0, s1',
 0xa007fe44:'lw a0, 0x2e0(a0)',0xa0086d40:'sw a0, 0(s2)',
 0xa00815e8:'lw a5, 0x2b8(s1)',0xa00815ee:'lw a1, 0x2b0(s1)',
 0xa00815f2:'c.mv a0, s1',0xa00815f4:'c.jalr a5',0xa00815f6:'lw a0, 0x2b0(s1)',
 0xa00815fe:'c.mv a0, s1',0xa008160c:'sw a5, 0x14(s2)',0xa0081614:'sw zero, 0x10(s2)',
}.items():expect(pc,asm)
for pc,target in [
 (0xa005ccc6,0xa0084b96),(0xa005cec6,0xa005a736),(0xa005cece,0xa0081554),
 (0xa0084da2,0xa008aec0),(0xa0084dec,0xa0080d8e),(0xa0084e2a,0xa008ae8c),
 (0xa0084e6e,0xa00819d0),(0xa0081a22,0xa0080d8e),(0xa0081a28,0xa0081978),
 (0xa0080d9a,0xa0024906),(0xa0086cd4,0xa007ffa0),(0xa007fff0,0xa01b93b4),
 (0xa01b93d0,0xa008ae8c),(0xa01b94f6,0xa008ab76),
 (0xa0081532,0xa008acfa),(0xa0081544,0xa008acfa),
 (0xa00800c6,0xa007fe32),(0xa00800ec,0xa0026888),(0xa00800f8,0xa002e14e),(0xa0080102,0xa008ab8a),
 (0xa008157e,0xa00814f4),(0xa0081586,0xa008b7f0),(0xa00815cc,0xa008ae42),
 (0xa00815da,0xa0089d02),(0xa00815e4,0xa008ae58),
 (0xa00815fa,0xa008ab8a),(0xa0081600,0xa008ab8a),
 (0xa0086d28,0xa007fe32),(0xa0086d34,0xa0026888),(0xa0086d3c,0xa003f4f6),
 (0xa008aba2,0xa002e14e),
]:direct(pc,target)

def word(pc):return int.from_bytes(ROM[pc-BASE:pc-BASE+4],'little')
ext=word(0xa008ad78);mul=word(0xa01b94f2)
assert (ext&127,(ext>>7)&31,(ext>>12)&7,(ext>>15)&31,(ext>>20)&63,ext>>26)==(11,13,3,15,15,15)
assert (mul&127,(mul>>7)&31,(mul>>12)&7,(mul>>15)&31,(mul>>20)&31,mul>>25)==(11,10,1,12,15,16)
checks.append(dict(vendor='extu/mula raw opcode, registers and bitfields',pcs=['0xa008ad78','0xa01b94f2']))
mask=((sx(0xffff8000,32)-1)&0xffffffff)
assert mask==0xffff7fff and (0x29&mask)==0x29
checks.append(dict(filter_mask=hex(mask),note='Clears bit15 only, not low15 extraction'))
strings=[]
for a,b in [(0xa01c3af4,b'/dev/fb0'),(0xa01c3b00,b'/dev/input0')]:
    actual=ROM[a-BASE:].split(b'\0',1)[0];assert actual==b
    strings.append(dict(pc=hex(a),value=actual.decode()))
matches=[]
for off in range(0,len(ROM)-3,2):
    w=int.from_bytes(ROM[off:off+4],'little')
    if (w&127)==0x23 and ((w>>12)&7)==2 and (((w>>25)<<5)|((w>>7)&31))==0x2b8:
        matches.append(dict(pc=hex(BASE+off),raw=ROM[off:off+4].hex()))
assert [m['pc'] for m in matches]==['0xa00efd3e','0xa00eff32','0xa014e264']
checks.append(dict(search='halfword aligned ordinary SW immediate=0x2b8',matches=matches))
model=ROOT/'evidence/rea-0041-20261017/ghidra/Ghidra/Processors/RISCV/data/languages/ap01thead2.sinc'
lines=model.read_text().splitlines(); excerpts=[]
for prefix in [':th.extu rd,rs1,15,15 ',':th.mula ']:
    k=next(i for i,l in enumerate(lines) if l.startswith(prefix))
    excerpts.append(dict(path=str(model),line=k+1,text='\n'.join(lines[k:k+6])))
unknown=[];p=0xa0084b96
while p<0xa00874b0:
    b=ROM[p-BASE:p-BASE+4];n=4 if b[0]&3==3 else 2
    if not next(md.disasm(b[:n],p),None):unknown.append(dict(pc=hex(p),raw=b[:n].hex()))
    p+=n
retained=json.loads((OUT.parents[2]/'reverse/analysis/factory-test-0041-20261023/retained-initializer.json').read_text())['function']
for rr in retained['raw_ranges']:
    b=bytes.fromhex(rr.get('hex') or rr.get('bytes_hex'));a=int(rr['start'],16)
    assert ROM[a-BASE:a-BASE+len(b)]==b
checks.append(dict(retained_container=retained['evidence_id'],profile=retained['profile']['digest'],raw_ranges_match=True))

(OUT/'instructions.txt').write_text('\n'.join(text)+'\n',encoding='utf-8')
(OUT/'independent-evidence.json').write_text(json.dumps(dict(task='F06',mode='static ROM only',engine=capstone.__version__,mapping='VA-0x9ffff000',windows=windows,checks=checks,strings=strings,vendor_model_excerpts=excerpts,constructor_unknown_words=unknown,sw_search=dict(start=hex(BASE),end=hex(BASE+len(ROM)),alignment=2,matches=matches,limitations='Encoding scan only. No complete alias, bulk-write, indexed custom store or code/data coverage.')),indent=2)+'\n',encoding='utf-8')
print('PASS',len(windows),'windows;',sum(z-a for _,a,z in spans),'bytes;',len(checks),'checks')
