"""D08 independent static ROM review. Does not read previous analysis JSON."""
from pathlib import Path
import json
from capstone import Cs, CS_ARCH_RISCV, CS_MODE_RISCV32, CS_MODE_RISCVC

ROOT = Path('D:/Documents/PlatformIO/Projects/cuktech-ap01-firmware')
ROM = ROOT/'roms/0041/ap01-1.0.2_0041.bin'
MODEL = ROOT/'evidence/rea-0041-20261017/ghidra/Ghidra/Processors/RISCV/data/languages/ap01thead2.sinc'
OUT = Path(__file__).resolve().parent
blob = ROM.read_bytes()
lines = MODEL.read_text().splitlines()
regs = 'zero ra sp gp tp t0 t1 t2 s0 s1 a0 a1 a2 a3 a4 a5 a6 a7 s2 s3 s4 s5 s6 s7 s8 s9 s10 s11 t3 t4 t5 t6'.split()
cs = Cs(CS_ARCH_RISCV, CS_MODE_RISCV32 | CS_MODE_RISCVC)
def raw(pc,n): return blob[pc-0x9ffff000:pc-0x9ffff000+n]
def word(pc,n=4): return int.from_bytes(raw(pc,n),'little')
def sign(v,n): return v-(1<<n) if v>>(n-1) else v
clauses = {}
def custom(w):
    f=(w>>12)&7; rd=(w>>7)&31; rs=(w>>15)&31; rt=(w>>20)&31
    if f in (2,3):
        name=('ext','extu')[f-2]; hi=(w>>26)&31
        key=f':th.{name} rd,rs1,{hi},{rt} '
        operands=f'{regs[rd]}, {regs[rs]}, {hi}, {rt}'
    elif w==0x0297800b:
        return 'cache-address .insn i 0x0b,0,x0,a5,0x29'
    else:
        name={(1,0):'addsl',(4,8):'lrw',(4,16):'lrbu',(4,20):'lrhu',(5,0):'srb',(5,8):'srw'}[(f,w>>27)]
        key=f':th.{name} '
        operands=f'{regs[rd]}, {regs[rs]}, {regs[rt]}, {(w>>25)&3}'
    matches=[i for i,x in enumerate(lines) if x.startswith(key)]
    assert len(matches)==1,key
    a=matches[0]; b=next(i for i in range(a+1,len(lines)) if lines[i]=='}')
    clauses[key]={'line':a+1,'text':'\n'.join(lines[a:b+1])}
    return f'th.{name} {operands}'

windows=[('start',0xa001a240,0xa001a49c),('wrapper',0xa01a47dc,0xa01a4820),('builder',0xa01b554e,0xa01b56be),('configure',0xa0025cec,0xa0025d9e),('cache',0xa0025d9e,0xa0025dcc),('enable-stop-active-clear',0xa0024b7e,0xa0024c5e),('completion',0xa0019d9a,0xa0019f42),('release',0xa002d5d8,0xa002d62c)]
decoded=[]; allrows={}
for name,start,end in windows:
    pc=start; rows=[]
    while pc<end:
        n=4 if word(pc,2)&3==3 else 2
        w=word(pc,n)
        if n==4 and w&127==11: text=custom(w)
        else:
            ins=list(cs.disasm(raw(pc,n),pc)); assert len(ins)==1,(hex(pc),raw(pc,n).hex())
            text=ins[0].mnemonic+' '+ins[0].op_str
        r={'va':f'{pc:08x}','offset':hex(pc-0x9ffff000),'bytes':raw(pc,n).hex(),'asm':text}
        rows.append(r);allrows[pc]=r;pc+=n
    assert pc==end
    decoded.append({'name':name,'rows':rows})

# Independent immediate-field extraction, not Capstone's rendered destinations.
def btarget(pc):
    w=word(pc);assert w&127==0x63
    v=((w>>31)<<12)|(((w>>7)&1)<<11)|(((w>>25)&63)<<5)|(((w>>8)&15)<<1)
    return (pc+sign(v,13))&0xffffffff
def cjump(pc):
    h=word(pc,2)
    v=((h>>12&1)<<11)|((h>>11&1)<<4)|((h>>9&3)<<8)|((h>>8&1)<<10)|((h>>7&1)<<6)|((h>>6&1)<<7)|((h>>3&7)<<1)|((h>>2&1)<<5)
    return (pc+sign(v,12))&0xffffffff
def cbranch(pc):
    h=word(pc,2)
    v=((h>>12&1)<<8)|((h>>10&3)<<3)|((h>>5&3)<<6)|((h>>3&3)<<1)|((h>>2&1)<<5)
    return (pc+sign(v,9))&0xffffffff
def callpair(pc):
    w=word(pc);n=word(pc+4);assert w&127==0x17 and n&127==0x67
    return (pc+(w&0xfffff000)+sign(n>>20,12))&0xffffffff
checks=[]
for pc,target in [(0xa01b5656,0xa01b5688),(0xa01b565e,0xa01b55b0),(0xa01b5648,0xa01b5608),(0xa0025db6,0xa0025dc4)]:
    assert btarget(pc)==target; checks.append([hex(pc),'B',hex(target)])
for pc,target in [(0xa01b56ac,0xa01b5688),(0xa01b56b8,0xa01b5688)]:
    assert cbranch(pc)==target;checks.append([hex(pc),'CB',hex(target)])
assert cjump(0xa0019eea)==0xa0019e24
for pc,target in [(0xa01b5680,0xa0025d9e),(0xa001a454,0xa01a47dc)]:
    assert callpair(pc)==target;checks.append([hex(pc),'AUIPC/JALR',hex(target)])
stores=[]
for pc,r in allrows.items():
    w=word(pc)
    if len(r['bytes'])==8 and w&127==0x23:
        stores.append({'va':hex(pc),'width':1<<((w>>12)&7),'base':regs[(w>>15)&31],'source':regs[(w>>20)&31],'offset':sign(((w>>25)<<5)|((w>>7)&31),12)})
expected=[(0xa01b560c,'a0','s4',0),(0xa01b5610,'a0','s5',4),(0xa01b5614,'a0','zero',8),(0xa01b5640,'a0','a6',12),(0xa01b5666,'a7','a5',0),(0xa01b566c,'a7','a5',4),(0xa01b5672,'a7','a5',8),(0xa01b567c,'a7','a5',12),(0xa0019e18,'s3','a5',0x88),(0xa0019e26,'s3','a5',0x88)]
for pc,base,src,off in expected:
    assert {'va':hex(pc),'width':4,'base':base,'source':src,'offset':off} in stores, (hex(pc), [x for x in stores if x['va']==hex(pc)])
assert word(0xa0025dc4)==0x0297800b
assert raw(0xa001a45c,4).hex()=='83c70400'
table=[word(0xa066d580+i*2,2) for i in range(3)]
assert table==[4064,8128,16256]
assert raw(0xa01bb000,20).hex()=='0100000000000000010000000100000000000000'
result={'rom':str(ROM),'model':str(MODEL),'method':'Fresh original-ROM bytes; no previous evidence JSON loaded; no firmware execution','windows':decoded,'vendor_clauses':clauses,'store_fields':stores,'control_flow_checks':checks,'constants':{'template':raw(0xa01bb000,20).hex(),'width_step_u16':table}}
(OUT/'independent-instructions.json').write_text(json.dumps(result,indent=2,ensure_ascii=False)+'\n',encoding='utf-8')
print(f'Independent static review: {len(allrows)} instructions, {len(clauses)} exact vendor clauses, {len(stores)} S stores; all field checks passed')
