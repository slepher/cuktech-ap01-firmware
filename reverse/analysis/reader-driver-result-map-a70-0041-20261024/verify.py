"""A70 static result mapper fields. No host input evaluation or target/model run."""
import json
from pathlib import Path
from capstone import Cs,CS_ARCH_RISCV,CS_MODE_RISCV32,CS_MODE_RISCVC

MAIN=Path('D:/Documents/PlatformIO/Projects/cuktech-ap01-firmware')
OUT=Path(__file__).resolve().parent
ROM=MAIN/'roms/0041/ap01-1.0.2_0041.bin'
assert ROM.stat().st_size==6769704
LO=0xa00ea524;HI=0xa00ea5b0
with ROM.open('rb') as f:f.seek(LO-0x9ffff000);body=f.read(HI-LO)
d=Cs(CS_ARCH_RISCV,CS_MODE_RISCV32|CS_MODE_RISCVC)
decoded=list(d.disasm(body,LO))
assert sum(r.size for r in decoded)==140
checks=[]
def check(label,got,want):
    assert got==want,(label,got,want)
    checks.append(dict(label=label,value=got))
def raw(a,n):
    assert LO<=a and a+n<=HI
    return body[a-LO:a-LO+n]
def sx(v,n):return v-(1<<n) if v&(1<<(n-1)) else v
def constant(a,reg,value):
    h=int.from_bytes(raw(a,2),'little')
    if h&3==1:
        q=(((h>>12)&1)<<5)|((h>>2)&31)
        check('independent C.LI '+hex(a),(h&3,h>>13,(h>>7)&31,sx(q,6)),(1,2,reg,value))
        b=raw(a,2)
    else:
        w=int.from_bytes(raw(a,4),'little')
        check('independent ADDI constant '+hex(a),(w&127,(w>>12)&7,(w>>7)&31,(w>>15)&31,sx(w>>20,12)),
              (0x13,0,reg,0,value));b=raw(a,4)
    return dict(address=hex(a),raw=b.hex(),register=reg,value=value)
constants=[]
for a,r,v in [(0xa00ea52a,15,16),(0xa00ea534,14,12),(0xa00ea536,15,10),
 (0xa00ea540,14,2),(0xa00ea542,15,3),(0xa00ea548,14,5),(0xa00ea54a,15,1),
 (0xa00ea550,15,12),(0xa00ea554,15,0),(0xa00ea55e,14,13),(0xa00ea560,15,6),
 (0xa00ea566,14,14),(0xa00ea568,15,12),(0xa00ea56e,15,2),(0xa00ea572,14,38),
 (0xa00ea576,15,9),(0xa00ea580,14,22),(0xa00ea582,15,11),(0xa00ea588,14,28),
 (0xa00ea58a,15,12),(0xa00ea590,15,4),(0xa00ea594,14,110),(0xa00ea598,15,8),
 (0xa00ea59e,14,114),(0xa00ea5a2,15,12),(0xa00ea5a8,15,5),(0xa00ea5ac,15,7)]:
    constants.append(constant(a,r,v))
branches=[]
for a,f,r1,r2,target in [(0xa00ea52c,0,10,15,0xa00ea5ac),
 (0xa00ea530,4,15,10,0xa00ea572),(0xa00ea538,0,10,14,0xa00ea556),
 (0xa00ea53c,4,14,10,0xa00ea55e),(0xa00ea544,0,10,14,0xa00ea556),
 (0xa00ea54c,0,10,14,0xa00ea556),(0xa00ea562,0,10,14,0xa00ea556),
 (0xa00ea56a,1,10,14,0xa00ea556),(0xa00ea578,0,10,14,0xa00ea556),
 (0xa00ea57c,4,14,10,0xa00ea594),(0xa00ea584,0,10,14,0xa00ea556),
 (0xa00ea58c,1,10,14,0xa00ea556),(0xa00ea59a,0,10,14,0xa00ea556),
 (0xa00ea5a4,1,10,14,0xa00ea556)]:
    w=int.from_bytes(raw(a,4),'little')
    q=((w>>31)<<12)|(((w>>7)&1)<<11)|(((w>>25)&63)<<5)|(((w>>8)&15)<<1)
    check('independent B '+hex(a),(w&127,(w>>12)&7,(w>>15)&31,(w>>20)&31,a+sx(q,13)),
          (0x63,f,r1,r2,target))
    branches.append(dict(address=hex(a),raw=raw(a,4).hex(),funct3=f,rs1=r1,rs2=r2,target=hex(target)))
for a,target in [(0xa00ea570,0xa00ea556),(0xa00ea592,0xa00ea556),
                 (0xa00ea5aa,0xa00ea556),(0xa00ea5ae,0xa00ea556)]:
    h=int.from_bytes(raw(a,2),'little')
    q=(((h>>12)&1)<<11)|(((h>>11)&1)<<4)|(((h>>9)&3)<<8)|(((h>>8)&1)<<10)|(((h>>7)&1)<<6)|(((h>>6)&1)<<7)|(((h>>3)&7)<<1)|(((h>>2)&1)<<5)
    check('independent C.J '+hex(a),(h&3,h>>13,a+sx(q,12)),(1,5,target))
h=int.from_bytes(raw(0xa00ea552,2),'little')
q=(((h>>12)&1)<<8)|(((h>>10)&3)<<3)|(((h>>5)&3)<<6)|(((h>>3)&3)<<1)|(((h>>2)&1)<<5)
check('independent nonzero/default gate',(h&3,h>>13,((h>>7)&7)+8,0xa00ea552+sx(q,9)),(1,7,10,0xa00ea556))

for a,t in [(0xa00ea524,'c.addi sp, -0x10'),(0xa00ea526,'c.swsp s0, 0xc(sp)'),
 (0xa00ea528,'c.addi4spn s0, sp, 0x10'),(0xa00ea556,'c.lwsp s0, 0xc(sp)'),
 (0xa00ea558,'c.mv a0, a5'),(0xa00ea55a,'c.addi sp, 0x10'),(0xa00ea55c,'c.jr ra')]:
    r=next(i for i in decoded if i.address==a)
    check('entry/return '+hex(a),r.mnemonic+' '+r.op_str,t)
memset={'lb','lbu','lh','lhu','lw','ld','sb','sh','sw','sd','c.lw','c.ld','c.lwsp','c.ldsp','c.sw','c.sd','c.swsp','c.sdsp'}
check('only local stack memory accesses',[(hex(r.address),r.mnemonic+' '+r.op_str) for r in decoded if r.mnemonic in memset],
 [('0xa00ea526','c.swsp s0, 0xc(sp)'),('0xa00ea556','c.lwsp s0, 0xc(sp)')])
check('no calls',[(hex(r.address),r.mnemonic) for r in decoded if r.mnemonic in {'jal','jalr','c.jal','c.jalr'}],[])

# This table records manual static path conclusions. It is never executed as a
# mapping implementation and is not tested against enumerated host/target inputs.
pairs={'0':0,'2':3,'5':1,'12':10,'13':6,'14':2,'16':7,'22':11,'28':4,'38':9,'110':8,'114':5}
paths=[dict(input_word=x,result=y,compare=pc,constant_return=vp) for x,y,pc,vp in [
 (0,0,'0xa00ea552','0xa00ea554'),(2,3,'0xa00ea544','0xa00ea542'),
 (5,1,'0xa00ea54c','0xa00ea54a'),(12,10,'0xa00ea538','0xa00ea536'),
 (13,6,'0xa00ea562','0xa00ea560'),(14,2,'0xa00ea56a','0xa00ea56e'),
 (16,7,'0xa00ea52c','0xa00ea5ac'),(22,11,'0xa00ea584','0xa00ea582'),
 (28,4,'0xa00ea58c','0xa00ea590'),(38,9,'0xa00ea578','0xa00ea576'),
 (110,8,'0xa00ea59a','0xa00ea598'),(114,5,'0xa00ea5a4','0xa00ea5a8')]]
contract=dict(claim='J08/9',task='A70',baseline='bd457a6',review_status='author-awaiting-independent-review',
 input='raw RV32 a0 numeric error word, not a dereferenced pointer',return_width_bits=32,
 exact_pairs_decimal=pairs,default=12,default_domain='every other 32-bit input word; no external lookup',
 comparisons='signed BLT thresholds16/12/38; BEQ/BNE equality; C.BNEZ zero split',
 memory='only local16B frame with save/restore s0; no external read/write or calls',
 naming='numeric facts only; errno/LVGL enum/source-version names not certified',
 callsite_use='A66/A68 pass the second getter-read value after log, not necessarily the first word or original negative IO result')
(OUT/'contract.json').write_text(json.dumps(contract,ensure_ascii=False,indent=2)+'\n',encoding='utf8')
(OUT/'evidence.json').write_text(json.dumps(dict(status='PASS-static-fields-no-input-execution',
 checks=checks,constant_fields=constants,branch_fields=branches,static_path_notes=paths,
 original=dict(path=str(ROM),length=6769704,mapping='VA-0x9ffff000',
 sha256_inherited='972db4c136c7ed9e24a83c07c1a7fd62040ca018b08ca285216d26b1fee3c6b9',digest_recomputed=False),
 exploratory_windows=[['0xa00ea524','0xa00ea554'],['0xa00ea554','0xa00ea584'],['0xa00ea584','0xa00ea5b0']],
 tools='Capstone5.0.7 RV32/RVC plus independent constant/B/C.J/C.BNEZ bit fields',
 limits=['No host input enumeration, target call, emulation, model or old script run',
         'No standard errno/LVGL names, independent SDK/version or actual error state claimed'],contract=contract),ensure_ascii=False,indent=2)+'\n',encoding='utf8')
print(f'PASS {len(checks)} static fields/control/effect checks; no input enumeration')
