"""A24 independent static byte review. Never executes target instructions."""
from pathlib import Path
import json
import capstone

OUT = Path(__file__).resolve().parent
BASE = Path('D:/Documents/PlatformIO/Projects/cuktech-ap01-firmware')
ROM = BASE / 'roms/0041/ap01-1.0.2_0041.bin'
blob = ROM.read_bytes()
def take(va, size):
    off = va - 0xa0000000 + 0x1000
    assert off >= 0 and off + size <= len(blob)
    return blob[off:off+size]
def word(va, n=4): return int.from_bytes(take(va,n), 'little')
def signed(value, bits): return value - (1 << bits) if value & (1 << (bits-1)) else value
cs = capstone.Cs(capstone.CS_ARCH_RISCV, capstone.CS_MODE_RISCV32 | capstone.CS_MODE_RISCVC)
regions = [
 ('owner prologue',0xa00e5c78,0xa00e5cb0),
 ('owner open consume close',0xa00e5d1a,0xa00e5db8),
 ('generic open',0xa019b168,0xa019b270),
 ('png open',0xa00eb7b6,0xa00eb9c0),
 ('identity entry',0xa00829e4,0xa0082a16),
 ('identity exit',0xa0082b80,0xa0082bdc),
 ('generic close',0xa00828d6,0xa0082914),
 ('png close',0xa00eab9a,0xa00eabc4),
 ('pixel create',0xa0081d90,0xa0081eba),
 ('pixel destroy',0xa0081f26,0xa0081ff6),
 ('cache insert',0xa0082980,0xa00829e4),
 ('cache payload cleanup',0xa008abb0,0xa008abe4),
 ('cache init fragment',0xa008e642,0xa008e694),
 ('png registration',0xa008e82c,0xa008e858),
 ('decode constructor first',0xa01928f2,0xa0192948),
 ('decode constructor second',0xa0192ac6,0xa0192af6),
 ('decode temporary cleanup',0xa0193bd6,0xa0193bea),
 ('entry payload adapter',0xa008b654,0xa008b6a6),
 ('allocator adapter',0xa008aea0,0xa008aec0),
 ('free adapter',0xa008ab8a,0xa008abb0),
 ('zero adapter',0xa0080d8e,0xa0080da6),
 ('consumer entry ABI only',0xa018f9e8,0xa018fa1c),
]
vendor_addresses = [0xa00eb7f2,0xa00eb942,0xa00eb946,0xa00eb94a,0xa00eb94e]
vendor=[]
for va in vendor_addresses:
    w=word(va)
    fields=dict(opcode=w&127,func3=(w>>12)&7,top=w>>27,reg=(w>>7)&31,base=(w>>15)&31,index=(w>>20)&31,shift=(w>>25)&3)
    assert fields['opcode']==11
    is_store=fields['func3']==5
    kind='store8' if is_store else ('load32' if fields['top']==8 else 'load_unsigned8')
    assert (fields['func3'],fields['top']) in [(4,8),(4,16),(5,0)]
    vendor.append(dict(address=hex(va),bytes=take(va,4).hex(),fields=fields,operation=kind,effective_address='base + (index << shift)',base_writeback=False))
vendor_by_va={int(x['address'],16):x for x in vendor}
rows=[]
for name,start,end in regions:
    pos=start
    while pos<end:
        n=4 if word(pos,2)&3==3 else 2
        assert pos+n<=end
        raw=take(pos,n)
        decoded=next(cs.disasm(raw,pos),None)
        if decoded:
            asm=decoded.mnemonic+' '+decoded.op_str
        else:
            assert pos in vendor_by_va, (hex(pos),raw.hex())
            asm=json.dumps(vendor_by_va[pos],sort_keys=True)
        rows.append(dict(region=name,va=hex(pos),offset=hex(pos-0xa0000000+0x1000),raw=raw.hex(),instruction=asm.strip()))
        pos+=n
by_va={int(x['va'],16):x for x in rows}
checks=[]
def check(va,label,actual,want):
    assert actual==want,(hex(va),label,actual,want)
    checks.append(dict(va=hex(va),claim=label,actual=actual,expected=want))
for va,want in [
    (0xa00eb7f2,[4,8,16,14,15,2]),
    (0xa00eb942,[4,16,11,13,10,2]),
    (0xa00eb946,[4,16,12,14,10,2]),
    (0xa00eb94a,[5,0,11,14,10,2]),
    (0xa00eb94e,[5,0,12,13,10,2])]:
    fields=vendor_by_va[va]['fields']
    check(va,'vendor width registers indexed shift',[fields[k] for k in ['func3','top','reg','base','index','shift']],want)
def instruction(va,expected): check(va,'decoded instruction',by_va[va]['instruction'],expected)
def mem(va,want):
    w=word(va); op=w&127
    imm=((w>>25)<<5)|((w>>7)&31) if op==35 else w>>20
    reg=(w>>20)&31 if op==35 else (w>>7)&31
    check(va,'raw memory opcode width register base signed offset',[op,(w>>12)&7,reg,(w>>15)&31,signed(imm,12)],want)
def direct(va,target):
    w=word(va)
    if w&127==111:
        bits=((w>>31)<<20)|(((w>>12)&255)<<12)|(((w>>20)&1)<<11)|(((w>>21)&1023)<<1)
        actual=(va+signed(bits,21))&0xffffffff
    else:
        z=word(va+4)
        check(va,'call pair registers',[w&127,(w>>7)&31,z&127,(z>>7)&31,(z>>15)&31],[23,1,103,1,1])
        actual=(va+(w&0xfffff000)+signed(z>>20,12))&0xfffffffe
    check(va,'direct call destination',actual,target)
def branch(va,want):
    w=word(va)
    b=((w>>31)<<12)|(((w>>7)&1)<<11)|(((w>>25)&63)<<5)|(((w>>8)&15)<<1)
    check(va,'branch opcode predicate operands destination',[w&127,(w>>12)&7,(w>>15)&31,(w>>20)&31,va+signed(b,13)],want)

for va,expected in [
 (0xa00e5d2e,'addi a0, s0, -0x7c'),(0xa00e5d7c,'addi a2, s0, -0x7c'),(0xa00e5d88,'addi a0, s0, -0x7c'),
 (0xa019b176,'addi a1, zero, 0x4c'),(0xa019b190,'c.mv a0, s2'),(0xa019b1fc,'c.lw a5, 4(a0)'),(0xa019b1fe,'c.mv a1, s1'),(0xa019b200,'c.jalr a5'),(0xa019b204,'c.mv s2, a0'),
 (0xa019b1d2,'c.lw a5, 0xc(a0)'),(0xa019b1d4,'c.sw a5, 0x2c(s1)'),(0xa019b1d6,'c.lw a5, 0x10(a0)'),
 (0xa00eb91c,'c.lw a5, 0xc(a1)'),(0xa00eb922,'c.lw s1, 0xc(a5)'),(0xa00eb8c8,'c.li s1, 0'),
 (0xa00eb92a,'c.lw a4, 0x10(s1)'),(0xa00eb930,'mul a5, a5, a3'),(0xa00eb934,'addi a3, a4, 2'),(0xa00eb952,'c.addi a0, 1'),
 (0xa0082bd4,'c.mv a0, s1'),(0xa00828e2,'c.lw a0, 0(a0)'),(0xa00828e6,'c.lw a5, 0xc(a0)'),(0xa00828ea,'c.mv a1, s1'),(0xa00828ec,'c.jalr a5'),
 (0xa0081f78,'c.andi a5, 0x10'),(0xa0081fba,'c.lw a5, 4(a5)'),(0xa0081fbe,'c.lw a0, 0x14(a0)'),(0xa0081fc0,'c.jalr a5'),(0xa0081fc2,'c.mv a0, s1'),
 (0xa0081e6c,'c.mv a1, s2'),(0xa0081e6e,'c.jalr a5'),(0xa0081ea4,'c.mv a1, s2'),(0xa0081ea6,'c.jalr a4'),(0xa0081eaa,'c.sw a5, 0x10(s1)'),
 (0xa0081e90,'lui a5, 0x62fc9'),(0xa008abca,'lbu a4, 8(s1)')]: instruction(va,expected)
for va,want in [
 (0xa019b198,[35,2,18,9,12]),(0xa019b1a2,[35,0,10,9,16]),(0xa019b1f4,[35,2,0,9,4]),(0xa019b1f8,[35,0,0,9,8]),
 (0xa00eb91e,[3,2,19,15,16]),(0xa00eb8ca,[3,4,14,18,16]),(0xa00eb980,[35,2,12,18,44]),(0xa00eb9ba,[35,2,10,18,68]),
 (0xa0082a02,[3,4,15,10,4]),(0xa0082b80,[3,4,15,23,5]),(0xa0081f72,[3,5,15,10,2]),
 (0xa0081e9c,[3,2,14,15,0x64c]),(0xa0081eac,[35,2,24,9,20]),(0xa0081eb4,[35,2,21,9,24]),
 (0xa0081e8c,[35,1,20,9,4]),(0xa0081e94,[35,1,23,9,6]),(0xa0081e98,[35,1,19,9,8])]: mem(va,want)
for va,want in [(0xa00e5d38,[99,0,10,15,0xa00e5d74]),(0xa019b206,[99,1,10,15,0xa019b18a]),(0xa00eb938,[99,1,15,10,0xa00eb942]),(0xa0082a08,[99,0,15,0,0xa0082b80])]: branch(va,want)
for va,target in [
 (0xa00e5d32,0xa019b168),(0xa00e5d84,0xa018f9e8),(0xa00e5d8c,0xa00828d6),(0xa019b17c,0xa0080d8e),(0xa019b1e8,0xa0082c8c),
 (0xa00eb8b4,0xa019262e),(0xa00eb8c4,0xa0081f26),(0xa00eb95a,0xa00829e4),(0xa00eb964,0xa0081f26),(0xa00eb974,0xa0081f26),(0xa00eb9b2,0xa0082980),
 (0xa00eabb6,0xa0081f26),(0xa0082902,0xa019d9f6),(0xa0081fc4,0xa008ab8a),(0xa008abc6,0xa0081f26),(0xa008abd6,0xa008ab8a),
 (0xa00829a0,0xa019d914),(0xa00829ac,0xa008b654),(0xa0192914,0xa0081d90),(0xa019293c,0xa0081f26),(0xa0192ade,0xa0081d90)]: direct(va,target)
model_path=BASE/'evidence/rea-0041-20261017/ghidra/Ghidra/Processors/RISCV/data/languages/ap01thead2.sinc'
model=model_path.read_text()
rules=[]
for marker in [':th.lrbu ',':th.srb ',':th.lrw ']:
    start=model.index(marker); end=model.index('\n}',start)+2
    rules.append(model[start:end])
summary=dict(status='passed',static_only=True,core=10,regions=len(regions),bytes=sum(z-a for _,a,z in regions),instructions=len(rows),checks=len(checks),vendor_words=len(vendor),unknown_instructions=0)
(OUT/'review.json').write_text(json.dumps(dict(summary=summary,rom=str(ROM),mapping='VA - a0000000 + 1000',regions=[dict(name=n,start=hex(a),end_exclusive=hex(z)) for n,a,z in regions],checks=checks,vendor=vendor,local_model=dict(path=str(model_path),rules=rules),instructions=rows),ensure_ascii=False,indent=2)+'\n',encoding='utf8')
(OUT/'instructions.txt').write_text('\n'.join(f"{r['va']} {r['raw']:8s} {r['instruction']} [{r['region']}]" for r in rows)+'\n',encoding='utf8')
(OUT/'review-index.json').write_text(json.dumps(summary,indent=2)+'\n',encoding='utf8')
print(json.dumps(summary))
