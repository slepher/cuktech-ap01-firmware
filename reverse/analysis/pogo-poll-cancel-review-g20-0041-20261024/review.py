"""G19/1-2 independent static field review. No target or model execution."""
import json
from pathlib import Path
from capstone import Cs, CS_ARCH_RISCV, CS_MODE_RISCV32, CS_MODE_RISCVC

ROOT=Path('D:/Documents/PlatformIO/Projects/cuktech-ap01-firmware')
BASE=0x9ffff000
rom=(ROOT/'roms/0041/ap01-1.0.2_0041.bin').read_bytes()
assert len(rom)==6769704  # Existing CATALOG identity; digest is cited, not recomputed.
dis=Cs(CS_ARCH_RISCV,CS_MODE_RISCV32|CS_MODE_RISCVC)
checks=[]


def bit(w,p,n): return (w>>p)&((1<<n)-1)
def signed(n,width): return n-(1<<width) if n&(1<<(width-1)) else n
def read(a,n): return int.from_bytes(rom[a-BASE:a-BASE+n],'little')


def save(a,n,kind,meaning):
    code=rom[a-BASE:a-BASE+n]
    ins=list(dis.disasm(code,a))
    if kind!='vendor': assert sum(i.size for i in ins)==n
    checks.append(dict(address=f'0x{a:08x}',raw=code.hex(),kind=kind,meaning=meaning,
                       decode=[i.mnemonic+' '+i.op_str for i in ins]))


def ins(a,n,m,ops):
    decoded=list(dis.disasm(rom[a-BASE:a-BASE+n],a))
    assert len(decoded)==1 and (decoded[0].mnemonic,decoded[0].op_str)==(m,ops),(hex(a),[(i.mnemonic,i.op_str) for i in decoded])
    save(a,n,'instruction',m+' '+ops)


def branch(a,f3,rs1,rs2,dest):
    w=read(a,4)
    assert (bit(w,0,7),bit(w,12,3),bit(w,15,5),bit(w,20,5))==(0x63,f3,rs1,rs2)
    q=bit(w,31,1)*4096+bit(w,7,1)*2048+bit(w,25,6)*32+bit(w,8,4)*2
    assert a+signed(q,13)==dest
    save(a,4,'branch',dict(funct3=f3,rs1=rs1,rs2=rs2,destination=f'0x{dest:08x}'))


def cb(a,nz,reg,dest):
    w=read(a,2)
    assert (bit(w,0,2),bit(w,13,3),bit(w,7,3)+8)==(1,7 if nz else 6,reg)
    q=bit(w,12,1)*256+bit(w,10,2)*8+bit(w,5,2)*64+bit(w,3,2)*2+bit(w,2,1)*32
    assert a+signed(q,9)==dest
    save(a,2,'compressed_branch',f'0x{dest:08x}')


def cj(a,dest):
    w=read(a,2)
    assert (bit(w,0,2),bit(w,13,3))==(1,5)
    pairs={12:11,11:4,10:9,9:8,8:10,7:6,6:7,5:3,4:2,3:1,2:5}
    q=sum(bit(w,k,1)*(1<<v) for k,v in pairs.items())
    assert a+signed(q,12)==dest
    save(a,2,'compressed_jump',f'0x{dest:08x}')


def jal(a,dest):
    w=read(a,4)
    assert (bit(w,0,7),bit(w,7,5))==(0x6f,1)
    q=bit(w,31,1)*2**20+bit(w,12,8)*4096+bit(w,20,1)*2048+bit(w,21,10)*2
    assert a+signed(q,21)==dest
    save(a,4,'jal',f'0x{dest:08x}')


def mem(a,store,base,reg,offset):
    w=read(a,4)
    q=bit(w,7,5)+bit(w,25,7)*32 if store else bit(w,20,12)
    actual=bit(w,20,5) if store else bit(w,7,5)
    assert (bit(w,0,7),bit(w,12,3),bit(w,15,5),actual,signed(q,12))==(0x23 if store else 3,2,base,reg,offset)
    save(a,4,'word_memory',dict(store=store,base=base,reg=reg,offset=offset))


def vendor(a,f3,top,rd,rs1,rs2,shift):
    w=read(a,4)
    fields=(bit(w,0,7),bit(w,12,3),bit(w,27,5),bit(w,7,5),bit(w,15,5),bit(w,20,5),bit(w,25,2))
    assert fields==(11,f3,top,rd,rs1,rs2,shift)
    save(a,4,'vendor',dict(fields=fields,rule={1:'addsl',4:'lrw',5:'srw'}[f3]))


# G19/1: only cancellation body and its two chain branches.
ins(0xa009f442,2,'c.lw','a5, 0x24(a1)')
ins(0xa009f444,2,'c.li','a4, -1')
branch(0xa009f446,0,15,14,0xa009f522)
ins(0xa009f458,2,'c.mv','s1, a1')
ins(0xa009f45a,2,'c.mv','s2, a0')
ins(0xa009f472,2,'c.lw','a4, 0x38(a0)')
branch(0xa009f474,7,15,14,0xa009f4b6)
ins(0xa009f478,2,'c.lw','a5, 0x1c(a1)')
ins(0xa009f47a,4,'not','a2, a2')
ins(0xa009f47e,4,'addi','s3, a1, 0xc')
ins(0xa009f482,2,'c.and','a2, a5')
ins(0xa009f484,2,'c.sw','a2, 0x1c(a1)')
cb(0xa009f486,True,12,0xa009f508)
ins(0xa009f488,2,'c.mv','a0, s3')
jal(0xa009f48a,0xa0098b4a)
mem(0xa009f48e,True,9,19,12)
mem(0xa009f492,True,9,19,16)
mem(0xa009f496,True,9,0,32)
ins(0xa009f49a,2,'c.lw','a4, 0x24(s1)')
mem(0xa009f49c,False,18,15,52)
mem(0xa009f4a4,False,10,19,0)
ins(0xa009f4a8,2,'c.lw','a4, 0x24(s1)')
mem(0xa009f4aa,False,18,15,52)
branch(0xa009f4b2,1,10,15,0xa009f4c4)
ins(0xa009f4c4,4,'addi','a5, a0, -0x14')
branch(0xa009f4c8,1,9,15,0xa009f4ee)
jal(0xa009f4cc,0xa0098b4a)
mem(0xa009f4d0,False,18,15,60)
cb(0xa009f4d4,True,15,0xa009f4e8)
ins(0xa009f4e8,2,'c.addi','a5, -1')
mem(0xa009f4ea,True,18,15,60)
ins(0xa009f4ee,2,'c.lw','a4, 0x24(s1)')
mem(0xa009f4f0,False,18,15,52)
branch(0xa009f4fa,0,19,15,0xa009f502)
mem(0xa009f4fe,False,19,14,0)
ins(0xa009f502,2,'c.mv','a0, s3')
ins(0xa009f504,2,'c.mv','s3, a4')
cj(0xa009f506,0xa009f4a8)
ins(0xa009f508,2,'c.lw','a5, 0xc(a1)')
branch(0xa009f50a,1,19,15,0xa009f4b6)
ins(0xa009f50e,4,'addi','a5, a0, 0x2c')
ins(0xa009f512,2,'c.sw','a5, 0xc(a1)')
ins(0xa009f514,2,'c.lw','a5, 0x30(a0)')
ins(0xa009f516,2,'c.sw','a5, 0x10(a1)')
mem(0xa009f518,True,15,19,0)
mem(0xa009f51c,True,10,19,48)
cj(0xa009f520,0xa009f4b6)

# G19/2: backend identities, absent-context route and four-param callsite.
mem(0xa009e222,False,10,20,20)
ins(0xa009e226,2,'c.mv','s2, a0')
ins(0xa009e228,2,'c.mv','s1, a1')
mem(0xa009e22a,False,20,19,0x114)
branch(0xa009e22e,1,19,0,0xa009e27a)
ins(0xa009e232,2,'c.li','a2, 0x10')
ins(0xa009e234,2,'c.li','a1, 0')
ins(0xa009e236,4,'addi','a0, s0, -0x30')
jal(0xa009e23a,0xa0024906)
branch(0xa009e23e,1,19,0,0xa009e30c)
mem(0xa009e242,False,18,15,56)
branch(0xa009e246,7,9,15,0xa009e25a)
mem(0xa009e24a,False,18,15,52)
branch(0xa009e256,1,13,15,0xa009e2f0)
mem(0xa009e25a,False,18,10,32)
ins(0xa009e25e,4,'addi','a3, s0, -0x30')
ins(0xa009e262,2,'c.mv','a2, s1')
ins(0xa009e264,2,'c.li','a1, 2')
jal(0xa009e266,0xa010e722)
# The call's common epilogue restores saved regs, leaving a0 untested/unreplaced.
for a,m,ops in [(0xa009e26a,'c.lwsp','ra, 0x2c(sp)'),(0xa009e26c,'c.lwsp','s0, 0x28(sp)'),
                (0xa009e26e,'c.lwsp','s1, 0x24(sp)'),(0xa009e270,'c.lwsp','s2, 0x20(sp)'),
                (0xa009e272,'c.lwsp','s3, 0x1c(sp)'),(0xa009e274,'c.lwsp','s4, 0x18(sp)'),
                (0xa009e276,'c.addi16sp','sp, 0x30'),(0xa009e278,'c.jr','ra')]:
    ins(a,2,m,ops)

# Existing record context route: signed count loop, exact-fd match, aggregation.
ins(0xa009e27a,4,'slli','a6, a1, 3')
ins(0xa009e27e,2,'c.li','a4, 0')
ins(0xa009e280,2,'c.li','a7, -1')
mem(0xa009e282,False,19,15,8)
branch(0xa009e286,5,14,15,0xa009e232)
mem(0xa009e28a,False,19,13,4)
ins(0xa009e28e,4,'slli','a5, a4, 4')
ins(0xa009e292,4,'add','a2, a3, a5')
ins(0xa009e296,2,'c.lw','a2, 8(a2)')
branch(0xa009e298,1,12,9,0xa009e2ec)
mem(0xa009e2a0,False,18,13,52)
mem(0xa009e2a8,False,18,11,52)
mem(0xa009e2ac,False,19,10,4)
ins(0xa009e2b0,2,'c.add','a1, a6')
ins(0xa009e2b6,4,'add','t1, a0, a5')
branch(0xa009e2ba,1,13,11,0xa009e2dc)
branch(0xa009e2be,0,12,0,0xa009e2e8)
mem(0xa009e2c2,False,18,10,32)
branch(0xa009e2c6,4,10,0,0xa009e26a)
mem(0xa009e2ca,True,8,12,-48)
mem(0xa009e2ce,True,8,9,-40)
ins(0xa009e2d2,4,'addi','a3, s0, -0x30')
ins(0xa009e2d6,2,'c.mv','a2, s1')
ins(0xa009e2d8,2,'c.li','a1, 3')
cj(0xa009e2da,0xa009e266)
ins(0xa009e2dc,2,'c.lw','a1, 8(a3)')
ins(0xa009e2de,2,'c.or','a2, a1')
ins(0xa009e2e4,2,'c.lw','a3, 0(a3)')
cj(0xa009e2e6,0xa009e2a8)
mem(0xa009e2e8,True,6,17,8)
ins(0xa009e2ec,2,'c.addi','a4, 1')
cj(0xa009e2ee,0xa009e282)

# Context absent aggregation and the scan-complete six-param call, body excluded.
ins(0xa009e2f0,2,'c.lw','a2, 8(a5)')
mem(0xa009e2f2,False,8,14,-48)
ins(0xa009e2f6,2,'c.or','a4, a2')
mem(0xa009e2f8,True,8,14,-48)
ins(0xa009e2fc,2,'c.lw','a5, 0(a5)')
branch(0xa009e2fe,1,13,15,0xa009e2f0)
mem(0xa009e302,False,18,10,32)
branch(0xa009e306,4,10,0,0xa009e26a)
cj(0xa009e30a,0xa009e2ce)
mem(0xa009e30c,False,19,12,0)
mem(0xa009e310,False,18,10,32)
ins(0xa009e314,4,'addi','a5, s0, -0x30')
ins(0xa009e318,2,'c.mv','a4, s1')
ins(0xa009e31a,2,'c.li','a3, 2')
ins(0xa009e31c,4,'addi','a1, s4, 0x84')
jal(0xa009e320,0xa009e0e6)
mem(0xa009e324,False,18,15,56)
branch(0xa009e328,7,9,15,0xa009e26a)
mem(0xa009e32c,False,18,15,52)
ins(0xa009e330,4,'slli','a3, s1, 3')
mem(0xa009e338,False,18,14,52)
ins(0xa009e33c,2,'c.add','a4, a3')
branch(0xa009e33e,0,15,14,0xa009e26a)
mem(0xa009e342,True,15,0,12)
ins(0xa009e346,2,'c.lw','a5, 0(a5)')
cj(0xa009e348,0xa009e338)

# Indexed instructions: independently read fields, then read exact existing rule text.
for row in [(0xa009f4a0,4,8,10,15,14,3),(0xa009f4ae,1,0,15,15,14,3),
            (0xa009f4f4,1,0,15,15,14,3),(0xa009e24e,1,0,13,15,9,3),
            (0xa009e252,4,8,15,15,9,3),(0xa009e29c,5,8,0,13,15,0),
            (0xa009e2a4,4,8,13,13,16,0),(0xa009e2b2,4,8,12,10,15,0),
            (0xa009e2e0,5,8,12,10,15,0),(0xa009e334,4,8,15,15,9,3)]:
    vendor(*row)

rule_path=ROOT/'evidence/rea-0041-20261017/ghidra/Ghidra/Processors/RISCV/data/languages/ap01thead2.sinc'
rules=rule_path.read_text(encoding='utf-8')
rule_checks=[]
for name,f3,top,semantics in [
    ('addsl',1,0,['rd = rs1 + (rs2 << thshift);']),
    ('lrw',4,8,['local delta:4 = rs2 << thshift;','local updated:4 = rs1 + delta;',
                'local ea:4 = updated;','local value:4 = *[ram]:4 ea;','rd = value;']),
    ('srw',5,8,['local delta:4 = rs2 << thshift;','local updated:4 = rs1 + delta;',
                'local ea:4 = updated;','*[ram]:4 ea = rd:4;'])]:
    pos=rules.index(':th.'+name+' rd,rs1,rs2,thshift')
    end=rules.index('\n}',pos)+2
    text=rules[pos:end]
    assert f'op0006=0xb & op1214={f3} & op2731={top}' in text
    for needed in semantics: assert needed in text
    rule_checks.append(dict(name=name,line=rules.count('\n',0,pos)+1,semantics_checked=True))

out=dict(status='PASS-static-only',claims=['G19/1','G19/2'],management_baseline='02afb05',
         research_baseline='0ea89ca',catalog_identity=dict(version='0041',bytes=len(rom),digest='972db4c136c7ed9e24a83c07c1a7fd62040ca018b08ca285216d26b1fee3c6b9',digest_recomputed=False),
         checks=checks,existing_rule_path=str(rule_path),existing_rule_checks=rule_checks,
         limitations=['Review functionality new=0','G19/3 and lower service bodies excluded',
                      'Existing local profile is not independent vendor/source certification',
                      'Software state/ABI only; OS completion, drain and lifetime unproved'])
Path(__file__).with_name('review-result.json').write_text(json.dumps(out,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
print(f'PASS: {len(checks)} independent sparse checks; 10 indexed fields; 3 existing rule definitions')
