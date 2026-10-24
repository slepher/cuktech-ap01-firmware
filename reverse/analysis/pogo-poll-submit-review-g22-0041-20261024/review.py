"""G19/3 independent static review, actual op2 nonfallback branch only."""
import json
from pathlib import Path
from capstone import Cs, CS_ARCH_RISCV, CS_MODE_RISCV32, CS_MODE_RISCVC

ROOT=Path('D:/Documents/PlatformIO/Projects/cuktech-ap01-firmware')
BASE=0x9ffff000
rom=(ROOT/'roms/0041/ap01-1.0.2_0041.bin').read_bytes()
assert len(rom)==6769704
dis=Cs(CS_ARCH_RISCV,CS_MODE_RISCV32|CS_MODE_RISCVC)
checks=[]


def field(w,pos,size):return (w>>pos)&((1<<size)-1)
def sign(n,width):return n-(1<<width) if n&(1<<(width-1)) else n
def word(a,n=4):return int.from_bytes(rom[a-BASE:a-BASE+n],'little')


def save(a,n,kind,meaning):
    raw=rom[a-BASE:a-BASE+n]
    ins=list(dis.disasm(raw,a))
    if kind!='vendor_byte_store':assert sum(i.size for i in ins)==n
    checks.append(dict(address=f'0x{a:08x}',raw=raw.hex(),kind=kind,meaning=meaning,
                       decode=[i.mnemonic+' '+i.op_str for i in ins]))


def inst(a,n,m,ops):
    decoded=list(dis.disasm(rom[a-BASE:a-BASE+n],a))
    assert len(decoded)==1 and (decoded[0].mnemonic,decoded[0].op_str)==(m,ops),(hex(a),[(i.mnemonic,i.op_str)for i in decoded])
    save(a,n,'instruction',m+' '+ops)


def mem(a,store,base,reg,offset):
    w=word(a)
    q=field(w,7,5)+field(w,25,7)*32 if store else field(w,20,12)
    r=field(w,20,5) if store else field(w,7,5)
    assert (field(w,0,7),field(w,12,3),field(w,15,5),r,sign(q,12))==(0x23 if store else 3,2,base,reg,offset)
    save(a,4,'word_memory',dict(store=store,base=base,reg=reg,offset=offset))


def jal(a,dest):
    w=word(a)
    assert (field(w,0,7),field(w,7,5))==(0x6f,1)
    q=field(w,31,1)*2**20+field(w,12,8)*4096+field(w,20,1)*2048+field(w,21,10)*2
    assert a+sign(q,21)==dest
    save(a,4,'jal',f'0x{dest:08x}')


def branch(a,f,rs1,rs2,dest):
    w=word(a)
    assert (field(w,0,7),field(w,12,3),field(w,15,5),field(w,20,5))==(0x63,f,rs1,rs2)
    q=field(w,31,1)*4096+field(w,7,1)*2048+field(w,25,6)*32+field(w,8,4)*2
    assert a+sign(q,13)==dest
    save(a,4,'branch',dict(funct3=f,rs1=rs1,rs2=rs2,destination=f'0x{dest:08x}'))


def cb(a,reg,dest):
    w=word(a,2)
    assert (field(w,0,2),field(w,13,3),field(w,7,3)+8)==(1,7,reg)
    q=field(w,12,1)*256+field(w,10,2)*8+field(w,5,2)*64+field(w,3,2)*2+field(w,2,1)*32
    assert a+sign(q,9)==dest
    save(a,2,'compressed_branch',f'0x{dest:08x}')


# Only the register bindings and nonfallback entrance, not G11/1 fallback body.
inst(0xa009e104,2,'c.mv','s4, a4')
inst(0xa009e106,2,'c.lw','a4, 0x3c(a1)')
inst(0xa009e108,2,'c.mv','s2, a5')
inst(0xa009e10a,2,'c.li','a5, -1')
inst(0xa009e10c,2,'c.mv','s5, a0')
inst(0xa009e10e,2,'c.mv','s6, a3')
branch(0xa009e110,1,14,15,0xa009e168)

# Tail and mask, source parameter, original scratch, and pre-copy tail store.
inst(0xa009e168,2,'c.lw','a5, 4(a1)')
mem(0xa009e16a,False,11,25,12)
inst(0xa009e16e,2,'c.mv','s3, a1')
inst(0xa009e170,2,'c.lw','s1, 0(a5)')
inst(0xa009e172,2,'c.mv','a1, s2')
inst(0xa009e174,2,'c.mv','s8, a2')
inst(0xa009e176,4,'addi','a4, s1, 1')
inst(0xa009e17a,4,'and','s1, s1, s9')
inst(0xa009e17e,4,'slli','s7, s1, 4')
inst(0xa009e182,2,'c.add','s7, a2')
inst(0xa009e184,2,'c.sw','a4, 0(a5)')
inst(0xa009e186,2,'c.li','a2, 0x10')
inst(0xa009e188,2,'c.mv','a0, s7')
jal(0xa009e18a,0xa000589c)

# Entries are reloaded after copy; distinct 64B zeroed entry and published fields.
mem(0xa009e18e,False,19,27,40)
inst(0xa009e192,4,'slli','s10, s1, 6')
inst(0xa009e196,4,'addi','a2, zero, 0x40')
inst(0xa009e19a,4,'add','s2, s11, s10')
inst(0xa009e19e,2,'c.li','a1, 0')
inst(0xa009e1a0,2,'c.mv','a0, s2')
jal(0xa009e1a2,0xa0024906)
inst(0xa009e1a6,4,'srai','a5, s4, 0x1f')
mem(0xa009e1aa,True,18,15,12)
mem(0xa009e1ae,True,18,23,16)
mem(0xa009e1b2,True,18,0,20)
mem(0xa009e1b6,True,18,21,4)
mem(0xa009e1ba,True,18,22,24)
mem(0xa009e1be,True,18,20,8)
inst(0xa009e1c2,2,'c.li','a5, 0x1d')
inst(0xa009e1c4,2,'c.slli','s1, 2')
inst(0xa009e1ca,4,'or','s1, s1, s6')
mem(0xa009e1ce,True,18,9,32)
mem(0xa009e1d2,True,18,20,36)

# Head/tail values are reread; mask stays s9. Only the lower callsite is reviewed.
mem(0xa009e1d6,False,19,15,0)
mem(0xa009e1da,False,19,14,4)
inst(0xa009e1de,2,'c.lw','a5, 0(a5)')
inst(0xa009e1e0,2,'c.lw','a4, 0(a4)')
inst(0xa009e1e2,2,'c.xor','a5, a4')
inst(0xa009e1e4,4,'and','a5, a5, s9')
cb(0xa009e1e8,15,0xa009e1f4)
inst(0xa009e1ea,2,'c.mv','a2, s8')
inst(0xa009e1ec,2,'c.mv','a1, s3')
inst(0xa009e1ee,2,'c.mv','a0, s5')
jal(0xa009e1f0,0xa009dfcc)

# Tail only: saved regs are restored, a0 is neither compared nor replaced.
epilogue=[('c.lwsp','ra, 0x3c(sp)'),('c.lwsp','s0, 0x38(sp)'),
          ('c.lwsp','s1, 0x34(sp)'),('c.lwsp','s2, 0x30(sp)'),
          ('c.lwsp','s3, 0x2c(sp)'),('c.lwsp','s4, 0x28(sp)'),
          ('c.lwsp','s5, 0x24(sp)'),('c.lwsp','s6, 0x20(sp)'),
          ('c.lwsp','s7, 0x1c(sp)'),('c.lwsp','s8, 0x18(sp)'),
          ('c.lwsp','s9, 0x14(sp)'),('c.lwsp','s10, 0x10(sp)'),
          ('c.lwsp','s11, 0xc(sp)'),('c.addi16sp','sp, 0x40'),('c.jr','ra')]
for n,(m,ops) in enumerate(epilogue):inst(0xa009e1f4+n*2,2,m,ops)

# The one vendor byte store: address is entries + (i << 6), source low byte=0x1d.
a=0xa009e1c6
w=word(a)
fields=(field(w,0,7),field(w,12,3),field(w,27,5),field(w,7,5),field(w,15,5),field(w,20,5),field(w,25,2))
assert fields==(11,5,0,15,27,26,0)
save(a,4,'vendor_byte_store',dict(fields=fields,rule='th.srb',byte_address='s11+(s10<<0)',source_low8='a5'))
model=ROOT/'evidence/rea-0041-20261017/ghidra/Ghidra/Processors/RISCV/data/languages/ap01thead2.sinc'
text=model.read_text(encoding='utf-8')
pos=text.index(':th.srb rd,rs1,rs2,thshift')
end=text.index('\n}',pos)+2
rule=text[pos:end]
for needed in ['op0006=0xb & op1214=5 & op2731=0','local delta:4 = rs2 << thshift;',
               'local updated:4 = rs1 + delta;','local ea:4 = updated;','*[ram]:1 ea = rd:1;']:
    assert needed in rule,needed

out=dict(status='PASS-static-only',claim='G19/3',management_and_research_baseline='bc3711a',
         original=dict(version='0041',length=len(rom),inherited_catalog_sha256='972db4c136c7ed9e24a83c07c1a7fd62040ca018b08ca285216d26b1fee3c6b9',digest_recomputed=False,mapping='VA-0x9ffff000'),
         checks=checks,existing_rule=dict(path=str(model),line=text.count('\n',0,pos)+1,rule='th.srb',checked=True),
         inherited=['G11/1 fallback','G19/1-2 cancellation and e320 actual input','G03/G04 aligned16 copy and aligned64 zero'],
         limitations=['No G21 verifier import/execution','Valid aligned ctx/scratch/entry and capacity/lifetime are preconditions',
                      'Independent destination lifetime/nonalias with caller stack not established','G19/4 dfcc and native service bodies excluded',
                      'Software stores/callsite only; no OS success or reuse protocol proof'])
Path(__file__).with_name('review-result.json').write_text(json.dumps(out,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
print(f'PASS: {len(checks)} independent sparse checks, including one vendor byte-store; existing rule checked')
