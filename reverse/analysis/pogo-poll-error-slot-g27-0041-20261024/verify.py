"""G19/6 return-address derivation; static original-byte checks only."""
import json
from pathlib import Path
from capstone import Cs, CS_ARCH_RISCV, CS_MODE_RISCV32, CS_MODE_RISCVC

MAIN = Path('D:/Documents/PlatformIO/Projects/cuktech-ap01-firmware')
OUT = Path(__file__).resolve().parent
ROM = MAIN/'roms/0041/ap01-1.0.2_0041.bin'
rom = ROM.read_bytes()
assert len(rom) == 6769704
BASE = 0x9ffff000
d = Cs(CS_ARCH_RISCV, CS_MODE_RISCV32 | CS_MODE_RISCVC)
checks = []

def raw(a,n): return rom[a-BASE:a-BASE+n]
def ins(a,text):
    n = 4 if int.from_bytes(raw(a,2),'little')&3 == 3 else 2
    got = list(d.disasm(raw(a,n),a))
    assert len(got)==1 and got[0].mnemonic+' '+got[0].op_str==text
    checks.append(dict(address=hex(a),raw=raw(a,n).hex(),decode=text))

for a,t in {
 0xa002671a:'c.addi sp, -0x20',0xa002671c:'c.swsp s0, 0x18(sp)',
 0xa002671e:'c.swsp s1, 0x14(sp)',0xa0026720:'c.swsp ra, 0x1c(sp)',
 0xa0026722:'c.addi4spn s0, sp, 0x20',0xa0026724:'lui a5, 0x62fc7',
 0xa0026728:'lw s1, -0x3e8(a5)',0xa0026740:'c.mv a5, s1',
 0xa002676c:'c.lw a4, 0x38(a5)',0xa002676e:'c.li a0, 0',
 0xa0026770:'c.sw a4, 0(a1)',0xa0026772:'c.lw a4, 0x3c(a5)',
 0xa0026774:'c.sw a4, 4(a1)',0xa0026776:'c.lw a5, 0x40(a5)',
 0xa0026778:'c.sw a5, 8(a1)',0xa002677a:'c.lwsp ra, 0x1c(sp)',
 0xa002677c:'c.lwsp s0, 0x18(sp)',0xa002677e:'c.lwsp s1, 0x14(sp)',
 0xa0026780:'c.addi16sp sp, 0x20',0xa0026782:'c.jr ra',
 0xa0026784:'c.addi sp, -0x20',0xa0026786:'c.swsp s0, 0x18(sp)',
 0xa0026788:'c.swsp ra, 0x1c(sp)',0xa002678a:'c.addi4spn s0, sp, 0x20',
 0xa002678c:'addi a1, s0, -0x1c',0xa0026790:'c.li a0, 0',
 0xa0026796:'c.li a5, 0',0xa002679c:'lw a5, -0x18(s0)',
 0xa00267a0:'c.lwsp ra, 0x1c(sp)',0xa00267a2:'c.lwsp s0, 0x18(sp)',
 0xa00267a4:'c.mv a0, a5',0xa00267a6:'c.addi16sp sp, 0x20',0xa00267a8:'c.jr ra',
 0xa00267c0:'c.addi sp, -0x10',0xa00267c2:'c.swsp s0, 8(sp)',
 0xa00267c4:'c.swsp ra, 0xc(sp)',0xa00267c6:'c.addi4spn s0, sp, 0x10',
 0xa00267ce:'c.addi a0, 4',0xa00267d0:'c.lwsp ra, 0xc(sp)',
 0xa00267d2:'c.lwsp s0, 8(sp)',0xa00267d4:'c.addi sp, 0x10',
 0xa00267d6:'c.jr ra',0xa00267d8:'lui a0, 0x62fc6',
 0xa00267dc:'addi a0, a0, 0x4c',0xa00267e0:'c.j -0x10',
}.items():ins(a,t)
a=0xa00267c8;w=int.from_bytes(raw(a,4),'little')
im=((w>>31)<<20)|(((w>>12)&255)<<12)|(((w>>20)&1)<<11)|(((w>>21)&1023)<<1)
im=im-(1<<21) if im&(1<<20) else im
assert (w&127,(w>>7)&31,a+im)==(0x6f,1,0xa0026784)
checks.append(dict(address=hex(a),raw=raw(a,4).hex(),kind='independent-jal-fields',target='0xa0026784'))
a=0xa00267cc;h=int.from_bytes(raw(a,2),'little')
im=(((h>>12)&1)<<8)|(((h>>10)&3)<<3)|(((h>>5)&3)<<6)|(((h>>3)&3)<<1)|(((h>>2)&1)<<5)
im=im-(1<<9) if im&(1<<8) else im
assert (h&3,h>>13,((h>>7)&7)+8,a+im)==(1,6,10,0xa00267d8)
checks.append(dict(address=hex(a),raw=raw(a,2).hex(),kind='independent-cbeqz-fields',target='0xa00267d8'))

a=0xa0026792;w=int.from_bytes(raw(a,4),'little')
im=((w>>31)<<20)|(((w>>12)&255)<<12)|(((w>>20)&1)<<11)|(((w>>21)&1023)<<1)
im=im-(1<<21) if im&(1<<20) else im
assert (w&127,(w>>7)&31,a+im)==(0x6f,1,0xa002671a)
checks.append(dict(address=hex(a),raw=raw(a,4).hex(),kind='independent-jal-fields',target='0xa002671a'))
a=0xa0026798;w=int.from_bytes(raw(a,4),'little')
im=((w>>31)<<12)|(((w>>7)&1)<<11)|(((w>>25)&63)<<5)|(((w>>8)&15)<<1)
im=im-(1<<13) if im&(1<<12) else im
assert (w&127,(w>>12)&7,(w>>15)&31,(w>>20)&31,a+im)==(0x63,4,10,0,0xa00267a0)
checks.append(dict(address=hex(a),raw=raw(a,4).hex(),kind='independent-signed-branch-fields',target='0xa00267a0'))

for a,funct,reg,dest in [(0xa002672c,7,9,0xa0026740),(0xa0026742,6,10,0xa002676c)]:
    h=int.from_bytes(raw(a,2),'little')
    im=(((h>>12)&1)<<8)|(((h>>10)&3)<<3)|(((h>>5)&3)<<6)|(((h>>3)&3)<<1)|(((h>>2)&1)<<5)
    im=im-(1<<9) if im&(1<<8) else im
    assert (h&3,h>>13,((h>>7)&7)+8,a+im)==(1,funct,reg,dest)
    checks.append(dict(address=hex(a),raw=raw(a,2).hex(),kind='independent-compressed-gate-fields',target=hex(dest)))
w=int.from_bytes(raw(0xa0026728,4),'little')
imm=w>>20;imm=imm-4096 if imm&2048 else imm
assert (w&127,(w>>12)&7,(w>>7)&31,(w>>15)&31,imm)==(3,2,9,15,-0x3e8)
assert ((0x62fc7<<12)+imm)&0xffffffff == 0x62fc6c18
checks.append(dict(address='0xa0026728',raw=raw(0xa0026728,4).hex(),
                   kind='independent-global-word-load-fields',global_address='0x62fc6c18'))

result=dict(status='PASS-static-only',task='G27',claim='G19/6',baseline='bd457a6',
 identity=dict(path=str(ROM),length=len(rom),mapping='VA-0x9ffff000',
 sha256_inherited='972db4c136c7ed9e24a83c07c1a7fd62040ca018b08ca285216d26b1fee3c6b9',digest_recomputed=False),
 tools=dict(decoder='Capstone 5.0.7 RV32/RVC',branch_and_call='independent bit fields'),
 checks=checks,contract='On T=word(0x62fc6c18)!=0: B=word(T+0x3c); return B!=0 ? low32(B+4) : 0x62fc604c;',
 normal_output_bridge='a0026784 passes a0=0,a1=&local_out; a002671a writes local_out[0..2]={T+0x38,T+0x3c,T+0x40} values and returns zero; wrapper reads local_out[1]',
 limits=['T identity/lifetime and fixed slot type not inferred from errno-like use',
         'No expansion of pid-nonzero path, a002661e, diagnostics or scheduler',
         'No two-call stability, task identity or nonaliasing assertion',
         'No target/instruction/model/input or old-script execution'])
(OUT/'evidence.json').write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n',encoding='utf8')
print(f'PASS {len(checks)} static anchors')
