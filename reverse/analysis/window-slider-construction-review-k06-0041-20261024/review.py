"""Independent sparse static review of construction flow. No target execution."""
import json
import re
from pathlib import Path
from capstone import Cs, CS_ARCH_RISCV, CS_MODE_RISCV32, CS_MODE_RISCVC

ROOT = Path('D:/Documents/PlatformIO/Projects/cuktech-ap01-firmware')
BASE = 0x9ffff000
rom = (ROOT/'roms/0041/ap01-1.0.2_0041.bin').read_bytes()
dis = Cs(CS_ARCH_RISCV,CS_MODE_RISCV32|CS_MODE_RISCVC)
checks=[]


def b(w,p,n): return (w>>p)&((1<<n)-1)
def sign(n,w): return n-(1<<w) if n&(1<<(w-1)) else n
def read(a,n): return int.from_bytes(rom[a-BASE:a-BASE+n],'little')


def record(a,n,kind,result):
    block=rom[a-BASE:a-BASE+n]
    ins=list(dis.disasm(block,a))
    assert sum(i.size for i in ins)==n
    checks.append(dict(address=f'{a:08x}',raw=block.hex(),kind=kind,result=result,
                       decode=[i.mnemonic+' '+i.op_str for i in ins]))


def inst(a,n,m,ops):
    ins=list(dis.disasm(rom[a-BASE:a-BASE+n],a))
    assert len(ins)==1 and (ins[0].mnemonic,ins[0].op_str)==(m,ops)
    record(a,n,'instruction',m+' '+ops)


def jal(a,target):
    w=read(a,4)
    assert (b(w,0,7),b(w,7,5))==(0x6f,1)
    q=b(w,31,1)*2**20+b(w,12,8)*4096+b(w,20,1)*2048+b(w,21,10)*2
    assert a+sign(q,21)==target
    record(a,4,'jal',f'{target:08x}')


def branch(a,f,left,right,target):
    w=read(a,4)
    assert (b(w,0,7),b(w,12,3),b(w,15,5),b(w,20,5))==(0x63,f,left,right)
    q=b(w,31,1)*4096+b(w,7,1)*2048+b(w,25,6)*32+b(w,8,4)*2
    assert a+sign(q,13)==target
    record(a,4,'branch',dict(f3=f,left=left,right=right,target=f'{target:08x}'))


def cb(a,nz,reg,target):
    w=read(a,2)
    assert (b(w,0,2),b(w,13,3),b(w,7,3)+8)==(1,7 if nz else 6,reg)
    q=b(w,12,1)*256+b(w,10,2)*8+b(w,5,2)*64+b(w,3,2)*2+b(w,2,1)*32
    assert a+sign(q,9)==target
    record(a,2,'compressed_branch',f'{target:08x}')


def cj(a,target):
    w=read(a,2)
    assert (b(w,0,2),b(w,13,3))==(1,5)
    positions={12:11,11:4,10:9,9:8,8:10,7:6,6:7,5:3,4:2,3:1,2:5}
    q=sum(b(w,k,1)*(1<<v) for k,v in positions.items())
    assert a+sign(q,12)==target
    record(a,2,'compressed_jump',f'{target:08x}')


def mem(a,store,base,reg,offset):
    w=read(a,4)
    q=b(w,7,5)+b(w,25,7)*32 if store else b(w,20,12)
    actual_reg=b(w,20,5) if store else b(w,7,5)
    assert (b(w,0,7),b(w,12,3),b(w,15,5),actual_reg,sign(q,12))==(0x23 if store else 3,2,base,reg,offset)
    record(a,4,'word_memory',dict(store=store,base=base,reg=reg,offset=offset))


# Request numbering, child result and separate 20B request.
inst(0xa00a8d2a,2,'c.li','s2, 0')
mem(0xa00a8d2c,False,23,21,0)
branch(0xa00a8d30,1,21,0,0xa00a8d68)
cj(0xa00a8d66,0xa00a8d66)
inst(0xa00a8d68,2,'c.mv','a0, s5')
jal(0xa00a8d6a,0xa00d91c6)
inst(0xa00a8d6e,2,'c.mv','s1, a0')
cb(0xa00a8d70,False,10,0xa00a8d82)
inst(0xa00a8d72,2,'c.li','a0, 0x14')
jal(0xa00a8d74,0xa008e362)
inst(0xa00a8d78,2,'c.mv','s10, a0')
cb(0xa00a8d7a,True,10,0xa00a8dd0)
inst(0xa00a8d7c,2,'c.mv','a0, s1')
jal(0xa00a8d7e,0xa00d7806)
inst(0xa00a8d82,2,'c.addi','s2, 1')
inst(0xa00a8d84,2,'c.li','a5, 8')
branch(0xa00a8d86,1,18,15,0xa00a8d2c)
inst(0xa00a8d8a,4,'lbu','s1, 0(s3)')
inst(0xa00a8dd4,2,'c.mv','a0, s1')
jal(0xa00a8dd6,0xa00d9044)
inst(0xa00a8ddc,2,'c.mv','a0, s1')
jal(0xa00a8dde,0xa00d9044)
mem(0xa00a8de2,True,9,26,16)

# Count uses parent, and only the unsigned 1<N predicate retains x=320.
inst(0xa00a8e5e,2,'c.mv','a0, s5')
jal(0xa00a8e60,0xa00a491c)
inst(0xa00a8e64,2,'c.li','a5, 1')
inst(0xa00a8e66,2,'c.li','a2, 0')
inst(0xa00a8e68,4,'addi','a1, zero, 0x140')
branch(0xa00a8e6c,6,15,10,0xa00a8e72)
inst(0xa00a8e70,2,'c.li','a1, 0')
inst(0xa00a8e72,2,'c.mv','a0, s1')
jal(0xa00a8e74,0xa00d8d1e)

# Configuration-route exits only; resource values and setup internals are inherited/opaque.
branch(0xa00a8e7a,0,18,15,0xa00a904c)
branch(0xa00a8e80,0,18,15,0xa00a8f9c)
branch(0xa00a8e84,1,18,0,0xa00a8d82)
cj(0xa00a8f86,0xa00a8d82)
cj(0xa00a904a,0xa00a8d82)
cj(0xa00a90fa,0xa00a8d82)

# Thin ordinary-child ABI, not a re-review of generic append.
inst(0xa00d91d0,2,'c.mv','a1, a0')
inst(0xa00d91d2,4,'lui','a0, 0xa0264')
inst(0xa00d91d6,4,'addi','a0, a0, -0x10c')
jal(0xa00d91da,0xa00d76ae)
cb(0xa00d91de,True,10,0xa00d9220)
inst(0xa00d9220,2,'c.mv','s1, a0')
jal(0xa00d9222,0xa00d9110)
inst(0xa00d922a,2,'c.mv','a0, s1')
inst(0xa00d9230,2,'c.jr','ra')

# Query exactly one retained body for explicit setter and counter assignments.
old_path=ROOT/'evidence/rea-0041-20261017/evidence/whole-rom-private-20261023-068.json'
old=json.loads(old_path.read_text(encoding='utf-8'))['structuredContent']
assembly=old['normalized_result']['assembly']
setter=[line for line in assembly if re.search(r': (?:jal|c\.jal)\b',line) and '0xa00a4aa0' in line]
assert not setter
counter=[]
for line in assembly:
    address=int(line.split(':',1)[0],16)
    if 0xa00a8d2a<=address<=0xa00a90fa and re.search(r': (?:c\.)?(?:li|mv|addi|lw|lwsp|add|sub|lui) s2(?:,|\s)',line):
        counter.append(line)
assert counter==['0xa00a8d2a: c.li s2, 0x0','0xa00a8d82: c.addi s2, 0x1'],counter
out=dict(status='PASS-static-only',review_baseline='7e633b1',checks=checks,
         bounded_old_body=dict(evidence_id=old['evidence_id'],explicit_setter_calls=setter,counter_assignments=counter),
         limits=['Only normal returned paths; no allocation/input/firmware execution',
                 'No success count or lifetime invariant inferred','Generic append and class walker inherited from independent E06/H04',
                 'Retained explicit-call query does not exclude indirect callback effects'])
Path(__file__).with_name('review-result.json').write_text(json.dumps(out,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
print(f'PASS: {len(checks)} independent sparse checks; bounded retained-call/counter query')
