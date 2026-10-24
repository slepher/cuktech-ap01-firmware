"""A79 finite static fields; no author verifier, instruction execution or input trials."""
import json
from pathlib import Path
from capstone import Cs,CS_ARCH_RISCV,CS_MODE_RISCV32,CS_MODE_RISCVC

MAIN=Path('D:/Documents/PlatformIO/Projects/cuktech-ap01-firmware')
rom=(MAIN/'roms/0041/ap01-1.0.2_0041.bin').read_bytes()
assert len(rom)==6769704
base=0x9ffff000
windows=[(0xa002af2e,14),(0xa002b4d8,94),(0xa002b536,30)]
md=Cs(CS_ARCH_RISCV,CS_MODE_RISCV32|CS_MODE_RISCVC)
decoded={}; unknown=[]
for start,size in windows:
    pc=start
    while pc<start+size:
        if pc in (0xa002b504,0xa002b524):
            assert int.from_bytes(rom[pc-base:pc-base+2],'little')&3==3
            unknown.append(pc); pc+=4; continue
        ins=next(md.disasm(rom[pc-base:min(pc-base+4,start+size-base)],pc,count=1),None)
        assert ins is not None,hex(pc)
        decoded[pc]=(ins.mnemonic,ins.op_str); pc+=ins.size
    assert pc==start+size
checks=[]; evidence=[]
def word(pc,n=4): return int.from_bytes(rom[pc-base:pc-base+n],'little')
def sx(x,n): return x-(1<<n) if x&(1<<(n-1)) else x
def check(name,actual,expected):
    assert actual==expected,(name,actual,expected)
    checks.append(name)
    evidence.append({'check':name,'actual':actual})

expected={
 0xaf2e:('c.addi','sp, -0x10'),0xaf30:('c.swsp','s0, 0xc(sp)'),
 0xaf32:('c.addi4spn','s0, sp, 0x10'),0xaf34:('c.lwsp','s0, 0xc(sp)'),
 0xaf36:('c.li','a0, 0'),0xaf38:('c.addi','sp, 0x10'),0xaf3a:('c.jr','ra'),
 0xb4f8:('c.lw','a5, 0(a0)'),0xb4fa:('c.lw','s1, 0x14(a0)'),
 0xb4fc:('c.mv','s2, a0'),0xb4fe:('c.sub','s1, a5'),
 0xb50c:('c.lw','a0, 0x10(a0)'),0xb50e:('c.mv','a2, s1'),0xb510:('c.add','a0, a5'),
 0xb516:('lw','a5, 0(s2)'),0xb51a:('lw','a4, 0x10(s2)'),0xb51e:('c.add','a5, s1'),
 0xb520:('sw','a5, 0(s2)'),0xb528:('c.lwsp','ra, 0xc(sp)'),
 0xb52a:('c.lwsp','s0, 8(sp)'),0xb52c:('c.lwsp','s2, 0(sp)'),
 0xb52e:('c.mv','a0, s1'),0xb530:('c.lwsp','s1, 4(sp)'),
 0xb532:('c.addi','sp, 0x10'),0xb534:('c.jr','ra'),
 0xb53e:('sb','a1, -0x11(s0)'),0xb542:('c.li','a2, 1'),
 0xb544:('addi','a1, s0, -0x11'),0xb54c:('c.lwsp','ra, 0x1c(sp)'),
 0xb54e:('c.lwsp','s0, 0x18(sp)'),0xb550:('c.addi16sp','sp, 0x20'),0xb552:('c.jr','ra')}
for suffix,value in expected.items():
    check('decode:'+hex(suffix),decoded[0xa0020000+suffix],value)

# Independent normal fields establish byte width, actual registers and original order.
w=word(0xa002b53e)
check('stack SB', [w&127,(w>>12)&7,(w>>15)&31,(w>>20)&31,sx(((w>>25)<<5)|((w>>7)&31),12)], [35,0,8,11,-17])
w=word(0xa002b544)
check('address of stack byte',[w&127,(w>>7)&31,(w>>12)&7,(w>>15)&31,sx(w>>20,12)],[19,11,0,8,-17])
for pc,rd,rs1,imm in [(0xa002b516,15,18,0),(0xa002b51a,14,18,16)]:
    w=word(pc)
    check('LW:'+hex(pc),[w&127,(w>>7)&31,(w>>12)&7,(w>>15)&31,sx(w>>20,12)],[3,rd,2,rs1,imm])
w=word(0xa002b520)
check('count SW',[w&127,(w>>12)&7,(w>>15)&31,(w>>20)&31,((w>>25)<<5)|((w>>7)&31)],[35,2,18,15,0])
w=word(0xa002b500)
check('unsigned request less than remaining',[w&127,(w>>7)&31,(w>>12)&7,(w>>15)&31,(w>>20)&31,w>>25],[51,14,3,12,9,0])
w=word(0xa002b504)
check('mvnez fields',[w&127,(w>>7)&31,(w>>12)&7,(w>>15)&31,(w>>20)&31,w>>25],[11,9,1,12,14,33])
w=word(0xa002b524)
check('srb byte indexed fields',[w&127,(w>>7)&31,(w>>12)&7,(w>>15)&31,(w>>20)&31,(w>>25)&3,w>>27],[11,0,5,14,15,0,0])
w=word(0xa002b508)
imm=((w>>31)<<12)|(((w>>7)&1)<<11)|(((w>>25)&63)<<5)|(((w>>8)&15)<<1)
check('signed 0>=n skip',[w&127,(w>>12)&7,(w>>15)&31,(w>>20)&31,0xa002b508+sx(imm,13)],[99,5,0,9,0xa002b528])
w=word(0xa002b4e4,2)
imm=(((w>>12)&1)<<8)|(((w>>10)&3)<<3)|(((w>>5)&3)<<6)|(((w>>3)&3)<<1)|(((w>>2)&1)<<5)
check('nonzero S normal gate',[w&3,w>>13,8+((w>>7)&7),0xa002b4e4+sx(imm,9)],[1,7,10,0xa002b4f8])
for pc,target in [(0xa002b4f4,0xa0019672),(0xa002b512,0xa000589c),(0xa002b548,0xa002b4d8)]:
    w=word(pc); imm=((w>>31)<<20)|(((w>>12)&255)<<12)|(((w>>20)&1)<<11)|(((w>>21)&1023)<<1)
    check('JAL:'+hex(pc),[w&127,(w>>7)&31,pc+sx(imm,21)],[111,1,target])

# Reuse exact short rule text, never run p-code/model.
rp=MAIN/'evidence/rea-0041-20261017/ghidra/Ghidra/Processors/RISCV/data/languages/ap01thead2.sinc'
rules=rp.read_text(encoding='utf-8')
mv=rules[rules.index(':th.mvnez'):rules.index(':th.mula')]
sb=rules[rules.index(':th.srb '):rules.index(':th.sbib ')]
check('local mvnez rule',all(t in mv for t in ('op2531=33','if (rs2 == 0) goto <done>;','rd = rs1;')),True)
check('local srb rule',all(t in sb for t in ('op2731=0','local delta:4 = rs2 << thshift;','local updated:4 = rs1 + delta;','*[ram]:1 ea = rd:1;')) and 'rs1 =' not in sb,True)
check('finite boundary inventory',[len(decoded),len(unknown)],[52,2])
check('noop exact local-only body',[decoded[pc] for pc in sorted(decoded) if 0xa002af2e<=pc<0xa002af3c],list(expected.values())[:7])
result={'task':'A79','checks_pass':len(checks),'bytes':138,'ordinary_positions':52,'vendor_positions':2,
 'method':'static decode/independent fields and short rule text only','fields':evidence,
 'vendor_raw':{'0xa002b504':word(0xa002b504).to_bytes(4,'little').hex(),'0xa002b524':word(0xa002b524).to_bytes(4,'little').hex()},
 'limits':['no copy body or arbitrary selected-n effects certified','no engine ABI','local rule not external ISA authority','normal valid255-capacity domain and callee-saved assumptions']}
Path(__file__).with_name('evidence.json').write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
print(f'PASS {len(checks)} static checks; 138B; 52 ordinary +2 vendor positions')
