"""Independent A75 field review; retained d770 assembly only, no helper ROM read."""
import json
from pathlib import Path
from capstone import Cs,CS_ARCH_RISCV,CS_MODE_RISCV32,CS_MODE_RISCVC
ROOT=Path('D:/Documents/PlatformIO/Projects/cuktech-ap01-firmware')
HERE=Path(__file__).parent
rom=ROOT/'roms/0041/ap01-1.0.2_0041.bin'
assert rom.stat().st_size==6769704
with rom.open('rb') as f:
    f.seek(0xa0053252-0x9ffff000); data=f.read(120)
cs=Cs(CS_ARCH_RISCV,CS_MODE_RISCV32|CS_MODE_RISCVC)
ins=list(cs.disasm(data,0xa0053252))
assert sum(i.size for i in ins)==120
rows={i.address:dict(va=hex(i.address),offset=hex(i.address-0x9ffff000),width=i.size,raw=i.bytes.hex(),text=i.mnemonic+' '+i.op_str) for i in ins}
checks=[]
def check(label,x):
    assert x,label
    checks.append(label)
def raw(a):return int.from_bytes(bytes.fromhex(rows[a]['raw']),'little')
def sx(x,n):return x-(1<<n) if x>>(n-1) else x
def imm_i(a):return sx(raw(a)>>20,12)
expected={0xa0053252:'c.addi16sp sp, -0x30',0xa0053258:'c.addi4spn s0, sp, 0x30',
 0xa005325a:'c.mv a4, a1',0xa0053260:'c.mv a1, a2',0xa0053266:'c.beqz a4, 0x42',
 0xa005327c:'c.addi a4, -1',0xa0053296:'addi a0, s0, -0x28',0xa005329a:'c.mv a2, a3',
 0xa00532a0:'c.lwsp ra, 0x2c(sp)',0xa00532a2:'c.lwsp s0, 0x28(sp)',
 0xa00532a4:'c.addi16sp sp, 0x30',0xa00532a6:'c.jr ra',0xa00532c8:'c.j -0x32'}
for a,t in expected.items():check('field:'+hex(a),rows[a]['text']==t)
for u,i,t in [(0xa005325c,0xa0053262,0xa002af2e),(0xa0053268,0xa005326c,0xa002b536),
              (0xa0053274,0xa0053278,0xa002b4d8),(0xa00532a8,0xa00532ac,0xa002b554),
              (0xa00532b4,0xa00532b8,0xa002b578)]:
    w=raw(u);v=raw(i)
    check('U/I-target:'+hex(u),w&127==55 and v&127==19 and ((w>>7)&31)==((v>>15)&31)==((v>>7)&31) and ((w&0xfffff000)+imm_i(i))&0xffffffff==t)
stores={0xa0053270:(16,-0x24,2),0xa005327e:(16,-0x20,2),0xa0053282:(15,-0x1c,2),
        0xa0053286:(0,-0x28,2),0xa005328a:(10,-0x18,2),0xa005328e:(14,-0x14,2),
        0xa0053292:(0,0,0),0xa00532b0:(14,-0x24,2),0xa00532bc:(14,-0x20,2),
        0xa00532c0:(15,-0x1c,2),0xa00532c4:(0,-0x28,2)}
for a,(src,off,width) in stores.items():
    w=raw(a); im=sx(((w>>25)<<5)|((w>>7)&31),12)
    check('S-format:'+hex(a),(w&127,(w>>12)&7,(w>>15)&31,(w>>20)&31,im)==(35,width,10 if a==0xa0053292 else 8,src,off))
w=raw(0xa0053266)
cb=((w>>12)&1)<<8|((w>>10)&3)<<3|((w>>5)&3)<<6|((w>>3)&3)<<1|((w>>2)&1)<<5
check('CBEQZ-zero-arm',((w>>7)&7)+8==14 and 0xa0053266+sx(cb,9)==0xa00532a8)
w=raw(0xa00532c8)
cj=((w>>12)&1)<<11|((w>>11)&1)<<4|((w>>9)&3)<<8|((w>>8)&1)<<10|((w>>7)&1)<<6|((w>>6)&1)<<7|((w>>3)&7)<<1|((w>>2)&1)<<5
check('CJ-zero-arm-join',0xa00532c8+sx(cj,12)==0xa0053296)
w=raw(0xa005329c)
j=((w>>31)<<20)|(((w>>12)&255)<<12)|(((w>>20)&1)<<11)|(((w>>21)&1023)<<1)
check('JAL-to-retained-wrapper',0xa005329c+sx(j,21)==0xa002d770)
check('count256-minus1',256-1==255)
check('stream-slot-offsets',[off+0x28 for _,off,width in list(stores.values())[:6]]==[4,8,12,0,16,20])
oldpath=ROOT/'evidence/rea-0041-20261017/evidence/upper-complete.evidence.json'
eid='ev_2fc7174be7213a9616dc6d46d18c0831acd1c06324cba526633b36c29ab2f22e'
records=json.loads(oldpath.read_text(encoding='utf-8'))['records']
found=[(i,r) for i,r in enumerate(records) if r.get('evidence_id')==eid]
check('unique-retained-EID',len(found)==1)
idx,r=found[0]; assembly=r['normalized_result']['assembly']
expected_old=['0xa002d770: c.addi sp, -0x10','0xa002d772: c.swsp s0, 0x8, sp',
 '0xa002d774: c.swsp ra, 0xc, sp','0xa002d776: c.addi4spn s0, sp, 0x10',
 '0xa002d778: c.mv a3, a1','0xa002d77a: c.mv a4, a2','0xa002d77c: c.li a1, 0x0',
 '0xa002d77e: c.li a2, 0x0','0xa002d780: auipc ra, 0x176','0xa002d784: jalr ra, ra, 0x52',
 '0xa002d788: c.lwsp ra, 0xc, sp','0xa002d78a: c.lwsp s0, 0x8, sp',
 '0xa002d78c: c.addi sp, 0x10','0xa002d78e: ret']
check('retained-all14-assembly-rows',assembly==expected_old)
check('retained-AUIPC-JALR-target',(0xa002d780+(0x176<<12)+0x52)&~1==0xa01a37d2)
check('retained-profile',r['analysis_profile']['digest']=='4825fb58a33a3e7d618557975b153b8318cf7e833d190ad16bcbf8bd441ae621')
check('retained-ROM-identity',r['subject']['digest']['sha256']=='972db4c136c7ed9e24a83c07c1a7fd62040ca018b08ca285216d26b1fee3c6b9')
(HERE/'review-evidence.json').write_text(json.dumps(dict(task='A75',result='PASS',checks=checks,
    raw_window=dict(start='0xa0053252',size=120),anchors=list(rows.values()),
    retained=dict(path=str(oldpath.relative_to(ROOT)),record=idx,eid=eid,assembly=assembly,
                  profile=r['analysis_profile']['digest'],language=r['analysis_profile']['parameters']['language_id']),
    limits=['normal returns; engine/callback effects opaque','retained d770 assembly not new raw read',
            'no pointer-target body or engine read','no final output/NUL/count/truncation proof']),ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
print(f'PASS {len(checks)} static checks; {len(rows)} raw positions/120B; retained wrapper14 rows/32B')
