"""C15 static ROM reads and raw RISC-V encoding checks; never runs target code."""
import json
from pathlib import Path
from capstone import Cs, CS_ARCH_RISCV, CS_MODE_RISCV32, CS_MODE_RISCVC

HERE = Path(__file__).resolve().parent
TREE = HERE.parents[2]
ROM = Path('D:/Documents/PlatformIO/Projects/cuktech-ap01-firmware/roms/0041/ap01-1.0.2_0041.bin')
BASE = 0x9ffff000
data = ROM.read_bytes()
md = Cs(CS_ARCH_RISCV, CS_MODE_RISCV32 | CS_MODE_RISCVC)
checks = []

def raw(pc, n):
    return data[pc-BASE:pc-BASE+n]

def sx(v, bits):
    return v-(1 << bits) if v & (1 << (bits-1)) else v

def check(pc, kind, got, want):
    assert got == want, (hex(pc), kind, got, want)
    checks.append(dict(pc=hex(pc), kind=kind, decoded=got, raw=raw(pc, 4 if raw(pc,1)[0]&3 == 3 else 2).hex()))

def itype(pc, op, rd, f3, rs, imm):
    w = int.from_bytes(raw(pc,4),'little')
    check(pc,'I fields',[w&127,w>>7&31,w>>12&7,w>>15&31,sx(w>>20,12)],[op,rd,f3,rs,imm])

def store(pc, base, reg, offset):
    w = int.from_bytes(raw(pc,4),'little')
    check(pc,'S word fields',[w&127,w>>12&7,w>>15&31,w>>20&31,sx((w>>25<<5)|(w>>7&31),12)],[35,2,base,reg,offset])

def cword(pc, f3, base, reg, offset):
    h = int.from_bytes(raw(pc,2),'little')
    check(pc,'C.LW/SW fields',[h&3,h>>13,8+(h>>7&7),8+(h>>2&7),(h>>10&7)*8+(h>>6&1)*4+(h>>5&1)*64],[0,f3,base,reg,offset])

def cmv(pc, rd, rs):
    h = int.from_bytes(raw(pc,2),'little')
    check(pc,'C.MV fields',[h&3,h>>12,h>>7&31,h>>2&31],[2,8,rd,rs])

windows = []
for start,end in [(0xa00dddf4,0xa00dde9a),(0xa01ad6d8,0xa01ad6ec),(0xa008b43a,0xa008b456),(0xa0091f42,0xa0091f4e)]:
    ins = list(md.disasm(raw(start,end-start),start))
    assert sum(i.size for i in ins) == end-start
    windows.append(dict(start=hex(start),end_exclusive=hex(end),instructions=[dict(pc=hex(i.address),raw=i.bytes.hex(),assembly=i.mnemonic+' '+i.op_str) for i in ins]))

cmv(0xa00dde42,9,10)
cword(0xa00dde44,2,10,10,8)
cmv(0xa00dde4a,18,10)
for pc,rd,rs,off in [(0xa00dde4c,11,9,20),(0xa00dde50,10,8,-32),(0xa00dde5c,11,8,-32)]:
    itype(pc,19,rd,0,rs,off)
cmv(0xa00dde60,10,9)
for pc,off in [(0xa00dde58,-32),(0xa00dde6a,-28),(0xa00dde76,-24),(0xa00dde80,-20)]:
    itype(pc,3,15,2,8,off)
for pc,reg,off in [(0xa00dde66,15,-32),(0xa00dde72,15,-28),(0xa00dde7c,15,-24),(0xa00dde86,18,-20)]:
    store(pc,8,reg,off)
for pc in [0xa00dde62,0xa00dde6e]:
    w=int.from_bytes(raw(pc,4),'little')
    check(pc,'R SUB fields',[w&127,w>>7&31,w>>12&7,w>>15&31,w>>20&31,w>>25],[51,15,0,15,18,32])
for pc,rd,rs in [(0xa00dde7a,15,18),(0xa00dde84,18,15)]:
    h=int.from_bytes(raw(pc,2),'little')
    check(pc,'C.ADD fields',[h&3,h>>12,h>>7&31,h>>2&31],[2,9,rd,rs])
cword(0xa01ad6e0,2,10,10,44)
h=int.from_bytes(raw(0xa01ad6e8,2),'little')
check(0xa01ad6e8,'C.LI zero',[h&3,h>>13,h>>7&31,sx((h>>12&1)*32+(h>>2&31),6)],[1,2,10,0])
for n in range(4):
    cword(0xa008b440 if n==0 else 0xa008b442+n*4,2,11,15,n*4)
    cword(0xa008b444+n*4,6,10,15,n*4)
cmv(0xa0091f42,9,10)
cword(0xa0091f4a,2,9,10,44)

expected = {0xa00dde00:0xa00dde42,0xa00dde30:0xa008b51a,0xa00dde3e:0xa0019672,0xa00dde46:0xa01ad6d8,0xa00dde54:0xa008b43a,0xa00dde8a:0xa00ddbf6,0xa01ad6de:0xa01ad6e8,0xa01ad6ea:0xa01ad6e2,0xa0091f46:0xa00dddf4,0xa0091f4c:0xa0091f5e}
targets=[]
for win in windows:
    for row in win['instructions']:
        pc=int(row['pc'],16); b=bytes.fromhex(row['raw']); w=int.from_bytes(b,'little'); target=None
        if len(b)==4 and w&127==111:
            imm=((w>>31&1)<<20)|((w>>21&1023)<<1)|((w>>20&1)<<11)|((w>>12&255)<<12)
            target=pc+sx(imm,21)
            check(pc,'JAL rd',w>>7&31,1)
        elif len(b)==2 and w&3==1 and w>>13 in [6,7]:
            imm=((w>>12&1)<<8)|((w>>10&3)<<3)|((w>>5&3)<<6)|((w>>3&3)<<1)|((w>>2&1)<<5)
            target=pc+sx(imm,9)
            check(pc,'CB funct/reg',[w>>13,8+(w>>7&7)],[7 if pc==0xa00dde00 else 6,10])
        elif len(b)==2 and w&3==1 and w>>13==5:
            imm=((w>>12&1)<<11)|((w>>11&1)<<4)|((w>>9&3)<<8)|((w>>8&1)<<10)|((w>>7&1)<<6)|((w>>6&1)<<7)|((w>>3&7)<<1)|((w>>2&1)<<5)
            target=pc+sx(imm,12)
        if target is not None:
            check(pc,'direct target',hex(target),hex(expected[pc])); targets.append(dict(pc=hex(pc),target=hex(target)))
assert len(targets)==len(expected)
inventory=json.loads((TREE/'reverse/analysis/whole-rom-coverage-0041-20261023-round1.json').read_text())
selected=[]
def visit(x):
    if isinstance(x,dict):
        if x.get('address') in [w['start'] for w in windows[:3]] and 'extent' in x:
            selected.append({k:x[k] for k in ['address','extent','direct_calls','source_paths','scope','excluded_as_verified_open_source']})
        for v in x.values(): visit(v)
    elif isinstance(x,list):
        for v in x: visit(v)
visit(inventory)
assert len(selected)==3
for record in selected:
    win=next(w for w in windows if w['start']==record['address'])
    assert record['extent']['body']['ranges']==[dict(start=win['start'],end=hex(int(win['end_exclusive'],16)-1))]
strings=[]
for a,expected_text in [(0xa02645f0,'/home/jiangmingmin/ap01/AP01_BL618/apps/graphics/lvgl/lvgl/src/core/lv_obj_pos.c'),(0xa056a33c,'lv_obj_invalidate'),(0xa0263318,'obj != NULL')]:
    off=a-BASE; text=data[off:data.index(0,off)].decode()
    assert text==expected_text
    strings.append(dict(address=hex(a),text=text))
result=dict(task='C15',baseline='c021206',rom=str(ROM),mapping_base=hex(BASE),checks=dict(result='passed',windows=len(windows),bytes=sum(int(w['end_exclusive'],16)-int(w['start'],16) for w in windows),instructions=sum(len(w['instructions']) for w in windows),raw_checks=len(checks),all_direct_control_targets=len(targets)),windows=windows,raw_checks=checks,targets=targets,strings=strings,inherited_inventory=selected)
(HERE/'instruction-evidence.json').write_text(json.dumps(result,indent=2)+'\n')
print(json.dumps(result['checks']))
