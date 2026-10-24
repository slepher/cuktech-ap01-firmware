"""Independent F11/3 review; original-byte facts, no F13 script/import/run."""
import json
from pathlib import Path
from capstone import Cs, CS_ARCH_RISCV, CS_MODE_RISCV32, CS_MODE_RISCVC

MAIN=Path('D:/Documents/PlatformIO/Projects/cuktech-ap01-firmware')
OUT=Path(__file__).resolve().parent
ROM=MAIN/'roms/0041/ap01-1.0.2_0041.bin'
rom=ROM.read_bytes()
assert len(rom)==6769704
BASE=0x9ffff000
d=Cs(CS_ARCH_RISCV,CS_MODE_RISCV32|CS_MODE_RISCVC)
checks=[]
def raw(a,n):return rom[a-BASE:a-BASE+n]
def bits(w,i,n):return (w>>i)&((1<<n)-1)
def sx(w,n):return w-(1<<n) if w&(1<<(n-1)) else w
def inst(a,text):
    n=4 if int.from_bytes(raw(a,2),'little')&3==3 else 2
    v=list(d.disasm(raw(a,n),a))
    assert len(v)==1 and v[0].mnemonic+' '+v[0].op_str==text,(hex(a),text)
    checks.append(dict(address=hex(a),raw=raw(a,n).hex(),decode=text))
def mem(a,op,f,base,reg,off):
    w=int.from_bytes(raw(a,4),'little')
    q=(bits(w,25,7)<<5)|bits(w,7,5) if op==0x23 else bits(w,20,12)
    r=bits(w,20,5) if op==0x23 else bits(w,7,5)
    assert (w&127,bits(w,12,3),bits(w,15,5),r,sx(q,12))==(op,f,base,reg,off)
    checks.append(dict(address=hex(a),raw=raw(a,4).hex(),kind='independent-memory-fields',
                       fields=[op,f,base,reg,off]))
def jal(a,dest):
    w=int.from_bytes(raw(a,4),'little')
    q=(bits(w,31,1)<<20)|(bits(w,12,8)<<12)|(bits(w,20,1)<<11)|(bits(w,21,10)<<1)
    assert (w&127,bits(w,7,5),a+sx(q,21))==(0x6f,1,dest)
    checks.append(dict(address=hex(a),raw=raw(a,4).hex(),kind='independent-jal',target=hex(dest)))
def pair(a,dest):
    w=int.from_bytes(raw(a,4),'little');v=int.from_bytes(raw(a+4,4),'little')
    assert (w&127,bits(w,7,5),v&127,bits(v,7,5),bits(v,15,5),bits(v,12,3))==(0x17,1,0x67,1,1,0)
    target=((a+sx(w&0xfffff000,32)+sx(v>>20,12))&0xffffffff)&~1
    assert target==dest
    checks.append(dict(address=hex(a),raw=raw(a,8).hex(),kind='independent-auipc-jalr',target=hex(dest)))
def branch(a,f,r1,r2,dest):
    w=int.from_bytes(raw(a,4),'little')
    q=(bits(w,31,1)<<12)|(bits(w,7,1)<<11)|(bits(w,25,6)<<5)|(bits(w,8,4)<<1)
    assert (w&127,bits(w,12,3),bits(w,15,5),bits(w,20,5),a+sx(q,13))==(0x63,f,r1,r2,dest)
    checks.append(dict(address=hex(a),raw=raw(a,4).hex(),kind='independent-branch',target=hex(dest)))
def cj(a,dest):
    h=int.from_bytes(raw(a,2),'little')
    q=(bits(h,12,1)<<11)|(bits(h,11,1)<<4)|(bits(h,9,2)<<8)|(bits(h,8,1)<<10)|(bits(h,7,1)<<6)|(bits(h,6,1)<<7)|(bits(h,3,3)<<1)|(bits(h,2,1)<<5)
    assert (h&3,h>>13,a+sx(q,12))==(1,5,dest)
    checks.append(dict(address=hex(a),raw=raw(a,2).hex(),kind='independent-cj',target=hex(dest)))

for a,t in {
 0xa005f464:'c.beqz a0, 0xa0',0xa005f474:'c.li a5, -1',
 0xa005f476:'c.mv s2, a0',0xa005f478:'c.mv s1, a2',
 0xa005f47e:'c.lw a2, 0x18(a0)',
 0xa005f488:'c.lwsp ra, 0x2c(sp)',0xa005f48a:'c.lwsp s0, 0x28(sp)',
 0xa005f48c:'c.lwsp s1, 0x24(sp)',0xa005f48e:'c.lwsp s2, 0x20(sp)',
 0xa005f490:'c.lwsp s3, 0x1c(sp)',0xa005f492:'c.srai a0, 0x1f',
 0xa005f494:'c.addi16sp sp, 0x30',0xa005f496:'c.jr ra',
 0xa0197a8e:'c.lw a5, 0xc(a0)',0xa0197a90:'c.beqz a5, 0x90',
 0xa0197aa2:'c.lw s1, 0x18(a5)',0xa0197aa4:'c.beqz a1, 0x80',
 0xa0197aaa:'c.lw a5, 0(a0)',0xa0197aac:'c.andi a5, 2',
 0xa0197aae:'c.beqz a5, 0x7a',0xa0197ab0:'lhu a5, 0x24(s1)',
 0xa0197ab8:'c.mv s4, a2',0xa0197aba:'c.mv s3, a1',
 0xa0197abc:'c.li s2, 8',0xa0197abe:'csrrc s2, mstatus, s2',
 0xa0197ad0:'c.bnez a0, 0x42',0xa0197b12:'c.mv a1, a0',
 0xa0197b14:'c.mv a3, s4',0xa0197b16:'c.mv a2, s3',0xa0197b18:'c.mv a0, s1',
 0xa0197afe:'csrw mstatus, s2',0xa0197b10:'c.jr ra',
 0xa0194a00:'c.mv s2, a1',0xa0194a02:'c.mv s1, a0',
 0xa0194a04:'c.mv a1, a2',0xa0194a0a:'c.mv a2, a3',
 0xa0194a10:'addi a0, s2, 0xc',0xa0194a1c:'c.lw a3, 0x1c(s1)',
 0xa0194a1e:'c.li a5, 0',0xa0194a20:'addi a2, s1, 0x18',
 0xa0194a24:'c.mv a4, a3',0xa0194a2e:'c.lw a4, 4(a5)',
 0xa0194a38:'c.lw a4, 4(a5)',0xa0194a46:'addi a4, a5, 1',
 0xa0194ac0:'c.mv a5, a4',0xa0194ac2:'c.lw a4, 4(a4)',
 0xa0194ace:'c.lw a5, 0x1c(s1)',
 0xa0194b3c:'c.lwsp ra, 0x2c(sp)',0xa0194b3e:'c.lwsp s0, 0x28(sp)',
 0xa0194b40:'c.lwsp s1, 0x24(sp)',0xa0194b42:'c.lwsp s2, 0x20(sp)',
 0xa0194b44:'c.lwsp s3, 0x1c(sp)',0xa0194b46:'c.lwsp s4, 0x18(sp)',
 0xa0194b48:'c.li a0, 0',0xa0194b4a:'c.addi16sp sp, 0x30',0xa0194b4c:'c.jr ra',
}.items():inst(a,t)
for a,op,f,base,r,off in [
 (0xa0194a06,0x23,1,18,13,10),(0xa0194a0c,0x23,0,18,0,9),
 (0xa0194a30,0x23,2,18,15,0),(0xa0194a34,0x23,2,18,14,4),
 (0xa0194a3a,0x23,2,14,18,0),(0xa0194a3e,0x23,2,15,18,4),
 (0xa0194a42,3,1,9,15,34),(0xa0194a4a,0x23,1,9,14,34),
 (0xa0194ac6,0x23,2,18,13,4),(0xa0194aca,0x23,2,18,14,0),
 (0xa0194ad0,0x23,2,15,18,0),(0xa0194ad4,0x23,2,9,18,28),
]:mem(a,op,f,base,r,off)
pair(0xa005f480,0xa0197a8e);pair(0xa0194a14,0xa000589c)
jal(0xa0197b1a,0xa01949f0)
for args in [(0xa005f47a,1,12,15,0xa005f498),(0xa0197aa6,0,9,0,0xa0197b24),
 (0xa0197ab4,6,15,12,0xa0197b2c),(0xa0194a26,1,14,12,0xa0194ac0),
 (0xa0194a2a,0,15,0,0xa0194ac6)]:branch(*args)
for a,t in [(0xa0197b1e,0xa0197afe),(0xa0194ac4,0xa0194a26),(0xa0194ad8,0xa0194a42)]:cj(a,t)

result=dict(status='PASS-static-only',claim='F11/3',review='F14',baseline='bd457a6',
 original=dict(path=str(ROM),length=len(rom),mapping='VA-0x9ffff000',
 sha256_inherited='972db4c136c7ed9e24a83c07c1a7fd62040ca018b08ca285216d26b1fee3c6b9',digest_recomputed=False),
 tools=dict(decoder='Capstone 5.0.7 RV32/RVC',independent_fields='load/store widths; B/JAL/CJ/AUIPC-JALR'),
 checks=checks,acceptance='F13 actual -1 route source/length bridge and copy-call-before-M-publication only',
 new_business=0,semantic_corrections=0,
 limits=['Q+0x18 actual length remains unknown; F15 identity bridge not inspected',
 'Copy body not read: no arbitrary-n or actual4B value-copy claim',
 'Existing G03/G04 copy domain only valid separated aligned16/20B',
 'M storage/ownership/wait/notify/allocator/concurrency/consumer opaque',
 'No F13 or old scripts imported/executed, no target/instruction/model execution'])
(OUT/'review-result.json').write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n',encoding='utf8')
print(f'PASS {len(checks)} independent static anchors')
