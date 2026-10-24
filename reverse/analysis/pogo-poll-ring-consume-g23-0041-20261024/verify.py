"""G19/4 bounded original-byte checks; no target or instruction execution."""
import json
from pathlib import Path
from capstone import Cs, CS_ARCH_RISCV, CS_MODE_RISCV32, CS_MODE_RISCVC

MAIN = Path('D:/Documents/PlatformIO/Projects/cuktech-ap01-firmware')
OUT = Path(__file__).resolve().parent
ROM = MAIN / 'roms/0041/ap01-1.0.2_0041.bin'
BASE = 0x9ffff000
rom = ROM.read_bytes()
assert len(rom) == 6769704
dec = Cs(CS_ARCH_RISCV, CS_MODE_RISCV32 | CS_MODE_RISCVC)
checks = []

def bits(x, low, n): return (x >> low) & ((1 << n) - 1)
def sx(x, n): return x - (1 << n) if x & (1 << (n - 1)) else x
def raw(a, n): return rom[a-BASE:a-BASE+n]
def ins(a, text):
    n = 4 if int.from_bytes(raw(a, 2), 'little') & 3 == 3 else 2
    got = list(dec.disasm(raw(a, n), a))
    assert len(got) == 1 and got[0].mnemonic+' '+got[0].op_str == text, (hex(a), got, text)
    checks.append(dict(address=hex(a), raw=raw(a, n).hex(), instruction=text))
def jal(a, dest):
    w = int.from_bytes(raw(a, 4), 'little')
    imm = bits(w,31,1)*2**20+bits(w,12,8)*4096+bits(w,20,1)*2048+bits(w,21,10)*2
    assert (w & 127, bits(w,7,5), a+sx(imm,21)) == (0x6f, 1, dest)
    checks.append(dict(address=hex(a), raw=raw(a,4).hex(), jal_target=hex(dest)))
def branch(a, f, r1, r2, dest):
    w = int.from_bytes(raw(a,4), 'little')
    imm = bits(w,31,1)*4096+bits(w,7,1)*2048+bits(w,25,6)*32+bits(w,8,4)*2
    assert (w&127,bits(w,12,3),bits(w,15,5),bits(w,20,5),a+sx(imm,13)) == (0x63,f,r1,r2,dest)
    checks.append(dict(address=hex(a),raw=raw(a,4).hex(), branch=dict(funct3=f,rs1=r1,rs2=r2,target=hex(dest))))

# Selected data-flow and gate instructions; stack-save padding is not exported.
rows = {
0xa009dfcc:'c.addi16sp sp, -0x30',0xa009dfde:'c.addi4spn s0, sp, 0x30',
0xa009dfe0:'c.lw a4, 0x3c(a1)', 0xa009dfe2:'c.li a5, -1',
0xa009dfe8:'c.li a2, 0', 0xa009dfea:'addi a1, zero, 0x4f4',
0xa009dfee:'lui a0, 0xa01c4', 0xa009dff2:'addi a0, a0, -0x648',
0xa009dffa:'c.lw a5, 0(a1)', 0xa009dffc:'c.mv s1, a1',
0xa009dffe:'c.lw a4, 0(a5)', 0xa009e000:'c.lw a5, 4(a1)',
0xa009e002:'c.lw a5, 0(a5)',0xa009e004:'sub s4, a5, a4',
0xa009e00c:'c.mv s3, a0',0xa009e00e:'c.mv s2, a2',
0xa009e010:'addi s6, zero, 0x26',0xa009e014:'c.li s5, 4',
0xa009e01a:'sw s6, 0(a0)',0xa009e022:'c.lw a5, 0(a0)',
0xa009e028:'lui a0, 0xa01c4',0xa009e02c:'addi a0, a0, -0x630',
0xa009e034:'c.li a5, -1',0xa009e03a:'c.li a2, 0',
0xa009e03c:'addi a1, zero, 0x500',0xa009e040:'c.j -0x52',
0xa009e042:'c.li a2, 0',0xa009e044:'addi a1, zero, 0x4f5',
0xa009e048:'c.j -0x5a',0xa009e04a:'c.lw a4, 0(s1)',
0xa009e04c:'c.lw a5, 4(s1)',0xa009e04e:'c.lw a4, 0(a4)',
0xa009e050:'c.lw a5, 0(a5)',0xa009e056:'c.li a2, 0',
0xa009e058:'addi a1, zero, 0x502',0xa009e05c:'c.j -0x6e',
0xa009e05e:'c.li a2, 0x10',0xa009e060:'c.mv a1, s2',
0xa009e062:'addi a0, s0, -0x30',0xa009e06a:'c.li s4, 2',
0xa009e06c:'c.li s5, 1',0xa009e06e:'c.li s6, -0x11',
0xa009e070:'c.lw a4, 0x14(s1)',0xa009e072:'c.lw a3, 0x18(s1)',
0xa009e074:'c.lw a5, 0(a4)',0xa009e076:'c.lw a3, 0(a3)',
0xa009e07c:'c.lwsp ra, 0x2c(sp)',0xa009e07e:'c.lwsp s0, 0x28(sp)',
0xa009e080:'c.lwsp s1, 0x24(sp)',0xa009e082:'c.lwsp s2, 0x20(sp)',
0xa009e084:'c.lwsp s3, 0x1c(sp)',0xa009e086:'c.lwsp s4, 0x18(sp)',
0xa009e088:'c.lwsp s5, 0x14(sp)',0xa009e08a:'c.lwsp s6, 0x10(sp)',
0xa009e08c:'c.addi16sp sp, 0x30',0xa009e08e:'c.jr ra',0xa009e090:'addi a3, a5, 1',
0xa009e094:'c.sw a3, 0(a4)',0xa009e096:'c.lw a3, 0x1c(s1)',
0xa009e098:'c.lw a4, 0x24(s1)',0xa009e09a:'c.and a5, a3',
0xa009e09c:'c.slli a5, 4',0xa009e09e:'c.add a5, a4',
0xa009e0a0:'c.lw a4, 8(a5)',0xa009e0a2:'c.beqz a4, -0x32',
0xa009e0a4:'c.lw a2, 0(a5)',0xa009e0a6:'c.lw a3, 4(a5)',
0xa009e0a8:'andi a1, a2, 3',0xa009e0b0:'andi a5, a5, 0xff',
0xa009e0bc:'c.li a2, 0',0xa009e0be:'addi a1, zero, 0x51c',
0xa009e0c2:'c.j -0xd4',0xa009e0c8:'c.li a2, 0',
0xa009e0ca:'addi a1, zero, 0x51f',0xa009e0ce:'c.j -0xe0',
0xa009e0d0:'addi a4, s0, -0x30',0xa009e0d4:'c.slli a5, 4',
0xa009e0d6:'c.add a5, a4',0xa009e0d8:'c.mv a2, s2',
0xa009e0da:'c.mv a4, a3',0xa009e0dc:'c.mv a1, s1',
0xa009e0de:'c.li a3, 3',0xa009e0e0:'c.mv a0, s3',
0xa009e0e2:'c.jal 4',0xa009e0e4:'c.j -0x74',
}
for a,t in rows.items(): ins(a,t)
for args in [(0xa009dfe4,1,14,15,0xa009dffa),(0xa009e008,0,14,15,0xa009e042),
 (0xa009e024,0,15,21,0xa009e016),(0xa009e036,0,20,15,0xa009e04a),
 (0xa009e052,0,14,15,0xa009e05e),(0xa009e078,1,15,13,0xa009e090),
 (0xa009e0b4,0,11,20,0xa009e070),(0xa009e0b8,0,11,21,0xa009e0c4),
 (0xa009e0c4,0,14,22,0xa009e0d0)]: branch(*args)
for a,d in [(0xa009dff6,0xa0019672),(0xa009e016,0xa00267c0),
 (0xa009e01e,0xa00267c0),(0xa009e030,0xa0134716),(0xa009e066,0xa000589c)]: jal(a,d)

w = int.from_bytes(raw(0xa009e0ac,4),'little')
assert (w&127,bits(w,12,3),bits(w,25,7),bits(w,7,5),bits(w,15,5),bits(w,20,5)) == (0x77,0,0x6f,15,12,2)
model = MAIN/'evidence/rea-0041-20261017/ghidra/Ghidra/Processors/RISCV/data/languages/ap01thead2.sinc'
mt = model.read_text(encoding='utf8')
marker = ':wexti rd,rs1,op2024'
p = mt.index(marker); end = mt.index('\n}',p)+2
rule = mt[p:end]
assert 'local src:8 = (high << 32) | low;' in rule and 'src >> op2024' in rule and 'rd = shifted:4;' in rule
checks.append(dict(address='0xa009e0ac',raw=raw(0xa009e0ac,4).hex(),kind='vendor_wexti',
 fields=dict(opcode=0x77,funct3=0,top7=0x6f,rd=15,rs1_pair_low=12,shift=2),
 rule=rule,model=str(model),definition_line=mt.count('\n',0,p)+1,
 limitation='Existing private model only; not an independent ISA specification or execution.'))

result = dict(status='PASS-static-only',claim='G19/4',task='G23',baseline='32f9c9e',
 identity=dict(path=str(ROM),length=len(rom),mapping='file_offset=VA-0x9ffff000',
 sha256_inherited='972db4c136c7ed9e24a83c07c1a7fd62040ca018b08ca285216d26b1fee3c6b9',digest_recomputed=False),
 tool=dict(decoder='Capstone 5.0.7 RV32/RVC',branch_jal='independent bit fields',shared_REA_target_changed=False),
 checks=checks, limits=['No target or instruction/model execution','No callee-body expansion',
 'Diagnostic return behavior unknown; post-diagnostic reachability is conditional',
 'op3 callsite only; op2 contract not applied to op3','No native submission/OS success/lifetime certification'])
(OUT/'evidence.json').write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n',encoding='utf8')
print(f'PASS {len(checks)} static anchors, including one existing-model vendor instance')
