"""B10: static extraction and targeted encoding checks; never executes ROM."""
from pathlib import Path
import json, sys
from capstone import Cs, CS_ARCH_RISCV, CS_MODE_RISCV32, CS_MODE_RISCVC

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
SOURCE = Path(sys.argv[1])
ROM = SOURCE / 'roms/0041/ap01-1.0.2_0041.bin'
BASE = 0x9ffff000
rom = ROM.read_bytes()
md = Cs(CS_ARCH_RISCV, CS_MODE_RISCV32 | CS_MODE_RISCVC)
raw, decoded, windows, checks = {}, {}, [], []
for name, start, end in [('caller_local', 0xa00a8582, 0xa00a873e), ('lookup', 0xa00a53c0, 0xa00a53ee)]:
    p, rows = start, []
    while p < end:
        size = 4 if rom[p-BASE] & 3 == 3 else 2
        b = rom[p-BASE:p-BASE+size]
        raw[p] = int.from_bytes(b, 'little')
        ins = next(md.disasm(b, p), None)
        if ins:
            assert ins.size == size
            asm = ins.mnemonic + ' ' + ins.op_str
            decoded[p] = (ins.mnemonic, ins.op_str)
        else:
            assert p == 0xa00a53de
            asm = 'th.mula a5,a0,a4 (existing local model)'
        rows.append(dict(address=hex(p), file_offset=p-BASE, hex=b.hex(), decode=asm))
        p += size
    assert p == end
    windows.append(dict(name=name, start=hex(start), end_exclusive=hex(end), instructions=rows))

def check(p, label, condition):
    assert condition, (hex(p), label)
    checks.append(dict(address=hex(p), check=label))

def sx(n, bits):
    return n-(1 << bits) if n & (1 << (bits-1)) else n

def branch(p, rs1, rs2, f3, target):
    w = raw[p]
    imm = ((w >> 31) << 12) | ((w >> 7 & 1) << 11) | ((w >> 25 & 63) << 5) | ((w >> 8 & 15) << 1)
    check(p, 'raw branch operands/condition/target', w & 127 == 99 and w >> 15 & 31 == rs1 and w >> 20 & 31 == rs2 and w >> 12 & 7 == f3 and p+sx(imm,13) == target)

def jal(p, target):
    w=raw[p]
    imm=((w>>31)<<20)|((w>>12&255)<<12)|((w>>20&1)<<11)|((w>>21&1023)<<1)
    check(p, 'raw JAL ra target', w & 127 == 111 and w >> 7 & 31 == 1 and p+sx(imm,21)==target)

for p, rs1, rs2, f3, target in [
    (0xa00a85b0,10,15,1,0xa00a85b8), (0xa00a85bc,15,10,6,0xa00a873e),
    (0xa00a85c4,10,15,0,0xa00a93a4), (0xa00a85c8,15,10,6,0xa00a8602),
    (0xa00a8606,10,15,0,0xa00a88f6), (0xa00a860e,10,15,1,0xa00a8616),
    (0xa00a861a,10,15,1,0xa00a85e4), (0xa00a8690,14,13,0,0xa00a8698),
    (0xa00a86b2,18,0,1,0xa00a86ba), (0xa00a53d4,10,14,7,0xa00a53ea)]:
    branch(p,rs1,rs2,f3,target)
for p,target in [(0xa00a862c,0xa00a53c0),(0xa00a8642,0xa000589c),(0xa00a8680,0xa008b51a),(0xa00a86a8,0xa00501be),(0xa00a86c2,0xa000589c),(0xa00a872a,0xa008b51a),(0xa00a8736,0xa00a389c)]:
    jal(p,target)
for p,rs,target in [(0xa00a8632,10,0xa00a8638),(0xa00a86ac,10,0xa00a86b2),(0xa00a53ce,15,0xa00a53e2)]:
    w=raw[p]
    imm=((w>>12&1)<<8)|((w>>10&3)<<3)|((w>>5&3)<<6)|((w>>3&3)<<1)|((w>>2&1)<<5)
    f3=7 if p!=0xa00a53ce else 6
    check(p,'raw compressed zero branch',w&3==1 and w>>13==f3 and (w>>7&7)+8==rs and p+sx(imm,9)==target)
for p,rd,rs in [(0xa00a85ba,9,12),(0xa00a862a,10,22),(0xa00a8630,21,10),(0xa00a8734,10,22),(0xa00a53e4,10,15)]:
    w=raw[p]
    check(p,'raw C.MV flow',w>>12==8 and w&3==2 and w>>7&31==rd and w>>2&31==rs)
for p,rd,rs,imm,f3 in [(0xa00a8626,22,12,0,4),(0xa00a8698,18,21,40,2),(0xa00a53ca,15,15,0x2cc,2),(0xa00a53d0,14,15,6,4)]:
    w=raw[p]
    check(p,'raw load width/register/offset',w&127==3 and w>>7&31==rd and w>>15&31==rs and w>>20==imm and w>>12&7==f3)
w=raw[0xa00a8730]
check(0xa00a8730,'raw SW a5,0(s5)',w&127==35 and w>>12&7==2 and w>>15&31==21 and w>>20&31==15 and (w>>25)==0 and (w>>7&31)==0)
w=raw[0xa00a872e]
check(0xa00a872e,'raw C.LUI a5,4 => 0x4000',w&3==1 and w>>13==3 and w>>7&31==15 and w>>12&1==0 and w>>2&31==4)
w=raw[0xa00a53de]
fields=dict(op=w&127,rd=w>>7&31,funct3=w>>12&7,rs1=w>>15&31,rs2=w>>20&31,funct7=w>>25)
check(0xa00a53de,'raw vendor MULA fields',fields==dict(op=11,rd=15,funct3=1,rs1=10,rs2=14,funct7=16))
expected={0xa00a85b8:('c.mv','s2, a0'),0xa00a8616:('addi','a5, zero, 0x52'),0xa00a8622:('sb','zero, 0x2f0(a5)'),0xa00a8638:('c.li','a2, 8'),0xa00a863a:('addi','a1, s1, 1'),0xa00a863e:('addi','a0, s0, -0x48'),0xa00a8684:('lw','a4, -0x48(s0)'),0xa00a8688:('lui','a5, 0x2b010'),0xa00a868c:('addi','a3, a5, 0x112'),0xa00a869c:('addi','a1, s1, 5'),0xa00a86a0:('c.li','a2, 0x14'),0xa00a86a2:('c.mv','a0, s2'),0xa00a86ba:('lw','a1, -0x64(s0)'),0xa00a86be:('c.li','a2, 0x14'),0xa00a86c0:('c.mv','a0, s2'),0xa00a53d8:('c.lw','a5, 0(a5)'),0xa00a53da:('addi','a4, zero, 0x1a8'),0xa00a53ea:('c.li','a5, 0')}
for p,value in expected.items():
    check(p,'decoded local dataflow contract',decoded[p]==value)
# a callee-saved s6 holds the byte index across the opaque calls; no local write after LBU.
writes_s6=[p for p,(m,o) in decoded.items() if 0xa00a8626<=p<0xa00a8736 and o.split(',')[0]=='s6']
check(0xa00a8626,'s6 sole local writer before dispatch',writes_s6==[0xa00a8626])
model=SOURCE/'evidence/rea-0041-20261017/ghidra/Ghidra/Processors/RISCV/data/languages/ap01thead2.sinc'
lines=model.read_text().splitlines(); i=next(i for i,l in enumerate(lines) if l.startswith(':th.mula ')); j=next(j for j in range(i+1,len(lines)) if lines[j]=='}')+1
inventory=json.loads((ROOT/'reverse/analysis/whole-rom-coverage-0041-20261023-round1.json').read_text())
retained=[dict(address=f['address'],extent=f['extent'],scope=f['scope']) for f in inventory['functions'] if f['address'] in ['0xa00a8582','0xa00a53c0']]
result=dict(result='passed',windows=len(windows),bytes=490,ordinary_instructions=len(decoded),vendor_words=1,checks=len(checks))
(HERE/'instruction-evidence.json').write_text(json.dumps(dict(task='B10',source=str(ROM),mapping='offset=VA-0x9ffff000',validation=result,windows=windows,checks=checks,vendor_fields=fields,model_excerpt=dict(path=str(model),line=i+1,text='\n'.join(lines[i:j])),retained_inventory=retained,limits=['Static reading only. Caller is a local window within a larger function.','Opaque callees retain unknown effects; no runtime or whole-function reachability claim.','MULA semantics use the existing local model.']),indent=2)+'\n')
print(json.dumps(result))
