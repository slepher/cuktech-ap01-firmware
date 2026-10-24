"""A78 static callback fields. No inputs supplied to firmware or host formatter."""
import json
from pathlib import Path
from capstone import Cs, CS_ARCH_RISCV, CS_MODE_RISCV32, CS_MODE_RISCVC

ROOT=Path('D:/Documents/PlatformIO/Projects/cuktech-ap01-firmware')
ROM=ROOT/'roms/0041/ap01-1.0.2_0041.bin'
HERE=Path(__file__).parent
assert ROM.stat().st_size==6769704
windows=[(0xa002af2e,14),(0xa002b4d8,94),(0xa002b536,30)]
cs=Cs(CS_ARCH_RISCV,CS_MODE_RISCV32|CS_MODE_RISCVC)
rows={}
vendor={0xa002b504:'th.mvnez s1,a2,a4',0xa002b524:'th.srb zero,a4,a5,0'}
with ROM.open('rb') as f:
    for start,size in windows:
        f.seek(start-0x9ffff000); data=f.read(size); pos=0
        while pos<size:
            va=start+pos
            width=4 if int.from_bytes(data[pos:pos+2],'little')&3==3 else 2
            raw=data[pos:pos+width]
            assert len(raw)==width
            if va in vendor:
                assert width==4
                text=vendor[va]
            else:
                ins=list(cs.disasm(raw,va,count=1))
                assert len(ins)==1 and ins[0].size==width,(hex(va),raw.hex())
                text=ins[0].mnemonic+' '+ins[0].op_str
            rows[va]=dict(va=hex(va),offset=hex(va-0x9ffff000),raw=raw.hex(),width=width,text=text)
            pos+=width
        assert pos==size

expected={
 0xa002af2e:'c.addi sp, -0x10',0xa002af30:'c.swsp s0, 0xc(sp)',
 0xa002af32:'c.addi4spn s0, sp, 0x10',0xa002af34:'c.lwsp s0, 0xc(sp)',
 0xa002af36:'c.li a0, 0',0xa002af38:'c.addi sp, 0x10',0xa002af3a:'c.jr ra',
 0xa002b4e4:'c.bnez a0, 0x14',0xa002b4f8:'c.lw a5, 0(a0)',
 0xa002b4fa:'c.lw s1, 0x14(a0)',0xa002b4fc:'c.mv s2, a0',
 0xa002b4fe:'c.sub s1, a5',0xa002b500:'sltu a4, a2, s1',
 0xa002b508:'blez s1, 0x20',0xa002b50c:'c.lw a0, 0x10(a0)',
 0xa002b50e:'c.mv a2, s1',0xa002b510:'c.add a0, a5',
 0xa002b516:'lw a5, 0(s2)',0xa002b51a:'lw a4, 0x10(s2)',
 0xa002b51e:'c.add a5, s1',0xa002b520:'sw a5, 0(s2)',
 0xa002b528:'c.lwsp ra, 0xc(sp)',0xa002b52a:'c.lwsp s0, 8(sp)',
 0xa002b52c:'c.lwsp s2, 0(sp)',0xa002b52e:'c.mv a0, s1',
 0xa002b530:'c.lwsp s1, 4(sp)',0xa002b532:'c.addi sp, 0x10',0xa002b534:'c.jr ra',
 0xa002b53e:'sb a1, -0x11(s0)',0xa002b542:'c.li a2, 1',
 0xa002b544:'addi a1, s0, -0x11',0xa002b54c:'c.lwsp ra, 0x1c(sp)',
 0xa002b54e:'c.lwsp s0, 0x18(sp)',0xa002b550:'c.addi16sp sp, 0x20',0xa002b552:'c.jr ra'
}
checks=[]
for a,t in expected.items():
    assert rows[a]['text']==t,(hex(a),rows[a],t)
    checks.append('field:'+hex(a))
def raw(a):return int.from_bytes(bytes.fromhex(rows[a]['raw']),'little')
def sx(x,n):return x-(1<<n) if x>>(n-1) else x
def jal(a):
    w=raw(a)
    return a+sx(((w>>31)<<20)|(((w>>12)&255)<<12)|(((w>>20)&1)<<11)|(((w>>21)&1023)<<1),21)
for a,t in [(0xa002b4f4,0xa0019672),(0xa002b512,0xa000589c),(0xa002b548,0xa002b4d8)]:
    assert jal(a)==t
    checks.append('JAL:'+hex(a))
w=raw(0xa002b508)
imm=((w>>31)<<12)|(((w>>7)&1)<<11)|(((w>>25)&63)<<5)|(((w>>8)&15)<<1)
assert (w&127,(w>>12)&7,(w>>15)&31,(w>>20)&31)==(0x63,5,0,9)
assert 0xa002b508+sx(imm,13)==0xa002b528
checks.append('signed-0>=n-branch-to-epilogue')
def fields(w):return [w&127,(w>>12)&7,(w>>7)&31,(w>>15)&31,(w>>20)&31,(w>>25)&3,(w>>27)&31]
assert fields(raw(0xa002b504))==[11,1,9,12,14,1,8]
assert raw(0xa002b504)>>25==33
checks.append('mvnez-fields-minunsigned')
assert fields(raw(0xa002b524))==[11,5,0,14,15,0,0]
checks.append('srb-fields-zero-byte-no-base-writeback')
model=ROOT/'evidence/rea-0041-20261017/ghidra/Ghidra/Processors/RISCV/data/languages/ap01thead2.sinc'
lines=model.read_text(encoding='utf-8').splitlines()
rules={}
for name,n in [('th.mvnez',9),('th.srb',9)]:
    at=next(i for i,s in enumerate(lines) if s.startswith(':'+name+' '))
    text='\n'.join(lines[at:at+n])
    rules[name]=dict(path=str(model.relative_to(ROOT)),line=at+1,text=text)
assert 'if (rs2 == 0)' in rules['th.mvnez']['text'] and 'rd = rs1;' in rules['th.mvnez']['text']
assert '*[ram]:1 ea = rd:1;' in rules['th.srb']['text'] and 'rs2 << thshift' in rules['th.srb']['text']
checks.append('local-vendor-rule-text')
# Direct retention claims stop at copy: no target/callee side effects are simulated.
assert all(not r['text'].startswith(('jal ','jalr ','c.jalr ')) for a,r in rows.items() if 0xa002af2e<=a<0xa002af3c)
checks.append('af2e-no-callee')
assert all(not r['text'].startswith(('sw ','sb ','sh ','c.sw ')) for a,r in rows.items() if 0xa002af2e<=a<0xa002af3c)
checks.append('af2e-no-external-store')
out=dict(task='A78',result='PASS',checks=checks,windows=[dict(va=hex(a),size=n) for a,n in windows],
    total_bytes=138,anchors=list(rows.values()),rules=rules,
    sha256_inherited='972db4c136c7ed9e24a83c07c1a7fd62040ca018b08ca285216d26b1fee3c6b9',
    profile='Capstone5.0.7 RV32+RVC; independent J/B and vendor fields; static only',
    limits=['A74 stream initialization candidate pending review','engine call ABI not examined',
            'copy arbitrary selected n opaque; no new helper body','no formatter/path output proof'])
(HERE/'evidence.json').write_text(json.dumps(out,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
print(f'PASS {len(checks)} static checks; {len(rows)} positions; 138 bytes; no input enumeration')
