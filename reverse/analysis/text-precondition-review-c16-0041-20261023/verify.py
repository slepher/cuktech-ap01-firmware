"""Independent C16 static encoding review. Reads ROM; never runs target code."""
import json
from pathlib import Path
from capstone import Cs, CS_ARCH_RISCV, CS_MODE_RISCV32, CS_MODE_RISCVC

HERE = Path(__file__).resolve().parent
TREE = HERE.parents[2]
ROM = Path('D:/Documents/PlatformIO/Projects/cuktech-ap01-firmware/roms/0041/ap01-1.0.2_0041.bin')
BASE = 0x9ffff000
data = ROM.read_bytes()
prior = json.loads((TREE/'reverse/analysis/text-precondition-c15-0041-20261023/instruction-evidence.json').read_text())
md = Cs(CS_ARCH_RISCV, CS_MODE_RISCV32 | CS_MODE_RISCVC)

def sign(v, n):
    return v - (1 << n) if v >> (n-1) else v

def decode(pc, b):
    """Decode only encodings present in these bounded windows, from bit fields."""
    w = int.from_bytes(b, 'little')
    q, f = w & 3, (w >> 13) & 7
    d, s = (w >> 7) & 31, (w >> 2) & 31
    p, r = 8+((w >> 7)&7), 8+((w >> 2)&7)
    ci = sign(((w >> 12)&1)*32+s, 6)
    if len(b) == 4:
        op, rd, f3, rs1, rs2, f7 = w&127, (w>>7)&31, (w>>12)&7, (w>>15)&31, (w>>20)&31, w>>25
        if op == 0x37: return ['lui', rd, w & 0xfffff000]
        if op in (0x13, 3):
            assert f3 == (2 if op == 3 else 0)
            return ['lw' if op == 3 else 'addi', rd, rs1, sign(w>>20,12)]
        if op == 0x23:
            assert f3 == 2
            return ['sw',rs2,rs1,sign((w>>25)*32+((w>>7)&31),12)]
        if op == 0x33:
            assert (f3,f7)==(0,32)
            return ['sub',rd,rs1,rs2]
        if op == 0x6f:
            imm=((w>>31)<<20)|(((w>>12)&255)<<12)|(((w>>20)&1)<<11)|(((w>>21)&1023)<<1)
            return ['jal',rd,pc+sign(imm,21)]
    if q == 0 and f in (2,6):
        return ['lw' if f==2 else 'sw',r,p,((w>>10)&7)*8+((w>>6)&1)*4+((w>>5)&1)*64]
    if q == 0 and f == 0:
        return ['addi',r,2,((w>>7)&15)*64+((w>>11)&3)*16+((w>>5)&1)*8+((w>>6)&1)*4]
    if q == 1 and f == 0: return ['addi',d,d,ci]
    if q == 1 and f == 2: return ['li',d,ci]
    if q == 1 and f == 3 and d == 2:
        imm=((w>>12)&1)*512+((w>>3)&3)*128+((w>>5)&1)*64+((w>>2)&1)*32+((w>>6)&1)*16
        return ['addi',2,2,sign(imm,10)]
    if q == 1 and f in (6,7):
        imm=((w>>12)&1)*256+((w>>5)&3)*64+((w>>2)&1)*32+((w>>10)&3)*8+((w>>3)&3)*2
        return ['beqz' if f==6 else 'bnez',p,pc+sign(imm,9)]
    if q == 1 and f == 5:
        imm=((w>>12)&1)*2048+((w>>8)&1)*1024+((w>>9)&3)*256+((w>>6)&1)*128+((w>>7)&1)*64+((w>>2)&1)*32+((w>>11)&1)*16+((w>>3)&7)*2
        return ['j',pc+sign(imm,12)]
    if q == 2 and f == 2:
        return ['lw',d,2,((w>>2)&3)*64+((w>>12)&1)*32+((w>>4)&7)*4]
    if q == 2 and f == 6:
        return ['sw',s,2,((w>>7)&3)*64+((w>>9)&15)*4]
    if q == 2 and f == 4:
        if not ((w>>12)&1): return ['mv',d,s] if s else ['jr',d]
        assert s != 0
        return ['add',d,d,s]
    raise AssertionError((hex(pc),b.hex()))

windows, rows = [], {}
for start,end in [(0xa00dddf4,0xa00dde9a),(0xa01ad6d8,0xa01ad6ec),(0xa008b43a,0xa008b456),(0xa0091f42,0xa0091f4e)]:
    chunk=data[start-BASE:end-BASE]
    ins=list(md.disasm(chunk,start))
    assert sum(i.size for i in ins)==len(chunk)
    old=next(w for w in prior['windows'] if int(w['start'],16)==start)
    current=[]
    for i, previous in zip(ins,old['instructions'],strict=True):
        fields=decode(i.address,i.bytes)
        row=dict(pc=hex(i.address),raw=i.bytes.hex(),assembly=i.mnemonic+' '+i.op_str,fields=fields)
        assert all(row[k]==previous[k] for k in ('pc','raw','assembly'))
        rows[i.address]=fields
        current.append(row)
    windows.append(dict(start=hex(start),end_exclusive=hex(end),instructions=current))

checks=[]
def expect(pc, fields):
    assert rows[pc]==fields,(hex(pc),rows[pc],fields)
    checks.append(dict(pc=hex(pc),expected=fields))

for pc,fields in {
    0xa00dddf4:['addi',2,2,-32],0xa00dddfe:['addi',8,2,32],
    0xa00dde00:['bnez',10,0xa00dde42],0xa00dde42:['mv',9,10],
    0xa00dde44:['lw',10,10,8],0xa00dde46:['jal',1,0xa01ad6d8],
    0xa00dde4a:['mv',18,10],0xa00dde4c:['addi',11,9,20],
    0xa00dde50:['addi',10,8,-32],0xa00dde54:['jal',1,0xa008b43a],
    0xa00dde5c:['addi',11,8,-32],0xa00dde60:['mv',10,9],
    0xa00dde62:['sub',15,15,18],0xa00dde6e:['sub',15,15,18],
    0xa00dde7a:['add',15,15,18],0xa00dde84:['add',18,18,15],
    0xa00dde8a:['jal',1,0xa00ddbf6],
    0xa01ad6de:['beqz',10,0xa01ad6e8],0xa01ad6e0:['lw',10,10,44],
    0xa01ad6e8:['li',10,0],0xa01ad6ea:['j',0xa01ad6e2],
    0xa0091f42:['mv',9,10],0xa0091f44:['mv',18,11],
    0xa0091f46:['jal',1,0xa00dddf4],0xa0091f4a:['lw',10,9,44],
    0xa0091f4c:['beqz',10,0xa0091f5e],
    0xa00dde30:['jal',1,0xa008b51a],0xa00dde3e:['jal',1,0xa0019672],
}.items(): expect(pc,fields)
for pc,offset in [(0xa00dde58,-32),(0xa00dde6a,-28),(0xa00dde76,-24),(0xa00dde80,-20)]: expect(pc,['lw',15,8,offset])
for pc,reg,offset in [(0xa00dde66,15,-32),(0xa00dde72,15,-28),(0xa00dde7c,15,-24),(0xa00dde86,18,-20)]: expect(pc,['sw',reg,8,offset])
for n,pc in enumerate([0xa008b440,0xa008b446,0xa008b44a,0xa008b44e]): expect(pc,['lw',15,11,n*4])
for n,pc in enumerate([0xa008b444,0xa008b448,0xa008b44c,0xa008b450]): expect(pc,['sw',15,10,n*4])
for pc,reg,offset in [(0xa00dde8e,1,28),(0xa00dde90,8,24),(0xa00dde92,9,20),(0xa00dde94,18,16)]: expect(pc,['lw',reg,2,offset])
expect(0xa00dde96,['addi',2,2,32]);expect(0xa00dde98,['jr',1])
for pc in [0xa01ad6e6,0xa008b454]: expect(pc,['jr',1])
normal=[f for pc,f in rows.items() if 0xa00dde42<=pc<=0xa00dde98]
assert [f for f in normal if f[0] in ('bnez','beqz','j','jr','jal')]==[['jal',1,0xa01ad6d8],['jal',1,0xa008b43a],['jal',1,0xa00ddbf6],['jr',1]]
assert [f[0] for pc,f in rows.items() if 0xa00dde8e<=pc<=0xa00dde98]==['lw','lw','lw','lw','addi','jr']
assert not any(f[0] in ('jal','beqz','bnez','j') for pc,f in rows.items() if 0xa008b43a<=pc<0xa008b456)
strings=[]
for address,value in [(0xa02645f0,'/home/jiangmingmin/ap01/AP01_BL618/apps/graphics/lvgl/lvgl/src/core/lv_obj_pos.c'),(0xa056a33c,'lv_obj_invalidate'),(0xa0263318,'obj != NULL')]:
    off=address-BASE
    actual=data[off:data.index(0,off)].decode()
    assert actual==value
    strings.append(dict(address=hex(address),value=actual))
summary=dict(result='passed',windows=4,bytes=226,instructions=len(rows),independently_decoded=len(rows),contract_assertions=len(checks),c15_byte_and_disassembly_match=True)
result=dict(task='C16',baseline='7373c0f',rom=str(ROM),mapping_base=hex(BASE),summary=summary,windows=windows,contract_checks=checks,strings=strings,limits='Static instruction parsing only; no firmware execution or downstream a00ddbf6 analysis.')
(HERE/'review-evidence.json').write_text(json.dumps(result,indent=2)+'\n')
print(json.dumps(summary))
