"""Independent, read-only ROM field review; does not execute target instructions."""
import json
import struct
from pathlib import Path
from capstone import Cs, CS_ARCH_RISCV, CS_MODE_RISCV32, CS_MODE_RISCVC

ROOT = Path('D:/Documents/PlatformIO/Projects/cuktech-ap01-firmware')
BASE = 0x9ffff000
rom = (ROOT / 'roms/0041/ap01-1.0.2_0041.bin').read_bytes()
dis = Cs(CS_ARCH_RISCV, CS_MODE_RISCV32 | CS_MODE_RISCVC)
checks = []


def bits(w, low, size):
    return (w >> low) & ((1 << size) - 1)


def signed(n, width):
    return n - (1 << width) if n & (1 << (width - 1)) else n


def word(a, n):
    return int.from_bytes(rom[a-BASE:a-BASE+n], 'little')


def save(a, n, kind, value):
    block = rom[a-BASE:a-BASE+n]
    ins = list(dis.disasm(block, a))
    assert sum(i.size for i in ins) == n
    checks.append({'address': f'{a:08x}', 'raw': block.hex(), 'kind': kind,
                   'value': value, 'decode': [i.mnemonic+' '+i.op_str for i in ins]})


def jump(a, target):
    w = word(a, 4)
    assert bits(w, 0, 7) == 0x6f and bits(w, 7, 5) == 1
    q = bits(w,31,1)*2**20 + bits(w,12,8)*2**12 + bits(w,20,1)*2**11 + bits(w,21,10)*2
    assert a + signed(q, 21) == target
    save(a, 4, 'jal', f'{target:08x}')


def conditional(a, f3, left, right, target):
    w = word(a,4)
    assert (bits(w,0,7),bits(w,12,3),bits(w,15,5),bits(w,20,5)) == (0x63,f3,left,right)
    q=bits(w,31,1)*4096+bits(w,7,1)*2048+bits(w,25,6)*32+bits(w,8,4)*2
    assert a+signed(q,13)==target
    save(a,4,'branch',{'f3':f3,'left':left,'right':right,'target':f'{target:08x}'})


def compressed_branch(a, f3, reg, target):
    w=word(a,2)
    assert (bits(w,0,2),bits(w,13,3),bits(w,7,3)+8)==(1,f3,reg)
    q=bits(w,12,1)*256+bits(w,10,2)*8+bits(w,5,2)*64+bits(w,3,2)*2+bits(w,2,1)*32
    assert a+signed(q,9)==target
    save(a,2,'compressed_branch',f'{target:08x}')


def compressed_jump(a, target):
    w=word(a,2)
    assert (bits(w,0,2),bits(w,13,3))==(1,5)
    layout={12:11,11:4,10:9,9:8,8:10,7:6,6:7,5:3,4:2,3:1,2:5}
    q=sum(bits(w,k,1)*(1<<v) for k,v in layout.items())
    assert a+signed(q,12)==target
    save(a,2,'compressed_jump',f'{target:08x}')


def memory(a, store, f3, base, value, offset):
    w=word(a,4)
    opcode=0x23 if store else 3
    actual_value=bits(w,20,5) if store else bits(w,7,5)
    q=bits(w,7,5)+bits(w,25,7)*32 if store else bits(w,20,12)
    assert (bits(w,0,7),bits(w,12,3),bits(w,15,5),actual_value,signed(q,12))==(opcode,f3,base,value,offset)
    save(a,4,'memory',{'store':store,'width_f3':f3,'base':base,'reg':value,'offset':offset})


def decode(a,n,mnemonic,operands):
    ins=list(dis.disasm(rom[a-BASE:a-BASE+n],a))
    assert len(ins)==1 and (ins[0].mnemonic,ins[0].op_str)==(mnemonic,operands), (hex(a),[(i.mnemonic,i.op_str) for i in ins])
    save(a,n,'decode',mnemonic+' '+operands)


# Only the necessary ancestor-helper control and ABI sites.
compressed_branch(0xa00d81f8,7,10,0xa00d822c)
decode(0xa00d81fa,2,'c.lw','a5, 0(a1)')
decode(0xa00d81fc,2,'c.lw','a0, 0(a5)')
compressed_branch(0xa00d81fe,6,10,0xa00d8230)
decode(0xa00d8200,2,'c.lw','a5, 0xc(a0)')
compressed_branch(0xa00d8202,6,15,0xa00d822c)
memory(0xa00d820e,True,2,11,0,12)
decode(0xa00d8212,2,'c.lw','a5, 0xc(a0)')
decode(0xa00d8214,2,'c.mv','s1, a1')
decode(0xa00d8216,2,'c.jalr','a5')
memory(0xa00d8218,False,4,9,10,24)
decode(0xa00d8220,4,'not','a0, a0')
decode(0xa00d8226,2,'c.andi','a0, 1')
decode(0xa00d822c,2,'c.lw','a0, 0(a0)')
compressed_jump(0xa00d822e,0xa00d81fe)
decode(0xa00d8230,2,'c.li','a0, 1')
decode(0xa00d8232,2,'c.jr','ra')

# Caller class value, target/code, exact status, mask and signedness.
decode(0xa00a4cb8,4,'lui','a0, 0xa0372')
decode(0xa00a4cbc,4,'addi','a0, a0, 0x5cc')
decode(0xa00a4cc0,2,'c.mv','s2, a1')
jump(0xa00a4cc2,0xa00d81f8)
decode(0xa00a4cc6,2,'c.li','a5, 1')
conditional(0xa00a4cc8,1,10,15,0xa00a4cf2)
memory(0xa00a4ccc,False,2,18,15,8)
decode(0xa00a4cd0,2,'c.lui','a4, 0xffff8')
decode(0xa00a4cd2,2,'c.addi','a4, -1')
decode(0xa00a4cd4,2,'c.and','a5, a4')
decode(0xa00a4cd6,4,'addi','a4, zero, 0x31')
memory(0xa00a4cda,False,2,18,9,0)
conditional(0xa00a4cde,1,15,14,0xa00a4cfe)
decode(0xa00a4cfe,2,'c.li','a4, 0x11')
conditional(0xa00a4d00,1,15,14,0xa00a4cf2)
jump(0xa00a4d06,0xa00d8af6)
decode(0xa00a4d04,2,'c.mv','a0, s2')
decode(0xa00a4d0a,2,'c.li','a5, 0x13')
conditional(0xa00a4d0c,1,10,15,0xa00a4d2a)
decode(0xa00a4d2a,2,'c.li','a5, 0x14')
conditional(0xa00a4d2c,1,10,15,0xa00a4d52)
decode(0xa00a4d52,2,'c.li','a5, 0xa')
conditional(0xa00a4d54,1,10,15,0xa00a4cf2)
jump(0xa00a4ce4,0xa00a4116)
jump(0xa00a4cee,0xa00a4aa0)
jump(0xa00a4d12,0xa00a4116)
jump(0xa00a4d32,0xa00a4116)
conditional(0xa00a4d16,5,0,10,0xa00a4d22)
decode(0xa00a4d1a,4,'addi','a1, a0, -1')
jump(0xa00a4d24,0xa00a491c)
decode(0xa00a4d36,4,'addi','a1, a0, 1')
jump(0xa00a4d40,0xa00a491c)
memory(0xa00a4d44,False,2,8,11,-20)
conditional(0xa00a4d48,6,11,10,0xa00a4d4e)
decode(0xa00a4d58,2,'c.lw','a5, 0x38(s1)')
compressed_branch(0xa00a4d5a,6,15,0xa00a4d62)
decode(0xa00a4d62,2,'c.mv','a0, s1')
jump(0xa00a4d64,0xa00ded6c)
decode(0xa00a4d68,4,'lui','a5, 0x62fcb')
memory(0xa00a4d6c,True,2,15,0,0x6b0)
compressed_jump(0xa00a4d70,0xa00a4cf2)

# Installation and global reference; not an ownership/exclusivity proof.
decode(0xa00a8b90,4,'lui','s7, 0x62fcb')
decode(0xa00a8b9c,4,'addi','s7, s7, 0x6b0')
decode(0xa00a8cbc,4,'lui','a0, 0xa0372')
decode(0xa00a8cc0,4,'addi','a0, a0, 0x5cc')
jump(0xa00a8cc4,0xa00d76ae)
decode(0xa00a8cc8,2,'c.mv','s2, a0')
decode(0xa00d76c0,2,'c.mv','s3, a0')
compressed_branch(0xa00d76e0,6,10,0xa00d7724)
memory(0xa00d76e2,True,2,10,19,0)
memory(0xa00a8d1e,True,2,18,9,0x30)
memory(0xa00a8d22,True,2,23,18,0)
memory(0xa00a8d2c,False,2,23,21,0)

# Count width, wrapper result, and the actually present callee gates.
jump(0xa00a495a,0xa00dd144)
for a,op in [(0xa00a495e,('c.lwsp','ra, 0xc(sp)')),(0xa00a4960,('c.lwsp','s0, 8(sp)')),(0xa00a4962,('c.addi','sp, 0x10')),(0xa00a4964,('c.jr','ra'))]:
    decode(a,2,*op)
decode(0xa00dd190,2,'c.lw','a5, 8(a0)')
decode(0xa00dd192,2,'c.li','a0, 0')
compressed_branch(0xa00dd194,6,15,0xa00dd19a)
memory(0xa00dd196,False,5,15,10,0x30)
jump(0xa00a4af0,0xa00a491c)
compressed_branch(0xa00a4af4,6,10,0xa00a4b4e)
conditional(0xa00a4af8,0,15,20,0xa00a4b4e)
memory(0xa00a4c40,True,2,9,0,0x38)
memory(0xa00a4c44,True,2,9,0,0x3c)

table=struct.unpack_from('<4I',rom,0xa03725cc-BASE)
assert table==(0xa0263ef4,0xa00a4bdc,0xa00a4c54,0xa00a4cac)
assert ((0xffff8<<12)-1)&0xffffffff==0xffff7fff
out={'status':'PASS-static-only','review_baseline':'0d8027f','checks':checks,
     'class_words':[f'{n:08x}' for n in table], 'reviewed_functionality_new':0,
     'limitations':['Independent raw-field review, not execution','H04 event/key/delete and old three callee bodies inherited','Count invariants and global exclusivity remain unproved','No complete function/resource/source exports']}
Path(__file__).with_name('review-result.json').write_text(json.dumps(out,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
print(f'PASS: {len(checks)} independent sparse checks and 4 class words')
