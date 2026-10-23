"""B12 read-only static instruction checks. Does not execute firmware."""
from pathlib import Path
import json
from capstone import Cs, CS_ARCH_RISCV, CS_MODE_RISCV32, CS_MODE_RISCVC

HERE = Path(__file__).resolve().parent
TREE = HERE.parents[2]
SOURCE = Path('D:/Documents/PlatformIO/Projects/cuktech-ap01-firmware')
ROM = SOURCE / 'roms/0041/ap01-1.0.2_0041.bin'
BASE, START, END = 0x9ffff000, 0xa00501be, 0xa0050202
rom = ROM.read_bytes()
dossier = json.loads((TREE / 'reverse/analysis/usb-interface-ota-0041-20261023.json').read_text())
fn = next(f for f in dossier['functions'] if f['address'] == hex(START))
data = rom[START-BASE:END-BASE]
assert data.hex() == fn['raw_ranges'][0]['bytes_hex']
assert fn['body']['ranges'] == [{'start': hex(START), 'end': hex(END-1)}]
md = Cs(CS_ARCH_RISCV, CS_MODE_RISCV32 | CS_MODE_RISCVC)
raw, rows, checks = {}, [], []
p = START
custom = {0xa00501ee: (15, 10, 14), 0xa00501f4: (13, 11, 14)}
while p < END:
    size = 4 if rom[p-BASE] & 3 == 3 else 2
    b = rom[p-BASE:p-BASE+size]
    w = int.from_bytes(b, 'little')
    raw[p] = w
    ins = next(md.disasm(b, p), None)
    if p in custom:
        rd, rs1, rs2 = custom[p]
        assert w & 127 == 11 and w >> 7 & 31 == rd
        assert w >> 12 & 7 == 4 and w >> 15 & 31 == rs1
        assert w >> 20 & 31 == rs2 and w >> 25 & 3 == 0 and w >> 27 == 16
        asm = f'th.lrbu x{rd},x{rs1},x{rs2},0 (existing local model)'
        checks.append({'address': hex(p), 'check': 'raw vendor opcode/registers/shift=0'})
    else:
        assert ins and ins.size == size
        asm = ins.mnemonic + ' ' + ins.op_str
    rows.append({'address': hex(p), 'file_offset': p-BASE, 'hex': b.hex(), 'decode': asm})
    p += size
assert p == END

def check(p, label, condition):
    assert condition, (hex(p), label)
    checks.append({'address': hex(p), 'check': label})

def sx(x, bits):
    return x - (1 << bits) if x & (1 << (bits-1)) else x

for p, rs1, rs2, f3, target in [
    (0xa00501c0,15,12,7,0xa00501d6),
    (0xa00501d2,13,14,0,0xa00501e2),
    (0xa00501da,12,14,1,0xa00501ee),
    (0xa00501e8,15,12,6,0xa00501ce),
    (0xa00501f8,15,13,0,0xa00501da)]:
    w=raw[p]
    imm=((w>>31)<<12)|((w>>7&1)<<11)|((w>>25&63)<<5)|((w>>8&15)<<1)
    check(p,'raw branch condition/registers/target',w&127==99 and w>>15&31==rs1 and w>>20&31==rs2 and w>>12&7==f3 and p+sx(imm,13)==target)
w=raw[0xa00501ca]
imm=((w>>12&1)<<8)|((w>>10&3)<<3)|((w>>5&3)<<6)|((w>>3&3)<<1)|((w>>2&1)<<5)
check(0xa00501ca,'raw C.BNEZ a5 to byte path',w&3==1 and w>>13==7 and (w>>7&7)+8==15 and 0xa00501ca+sx(imm,9)==0xa00501d6)
w=raw[0xa00501ec]
imm=((w>>12&1)<<11)|((w>>11&1)<<4)|((w>>9&3)<<8)|((w>>8&1)<<10)|((w>>7&1)<<6)|((w>>6&1)<<7)|((w>>3&7)<<1)|((w>>2&1)<<5)
check(0xa00501ec,'raw C.J byte path',w&3==1 and w>>13==5 and 0xa00501ec+sx(imm,12)==0xa00501d6)

# Independently check compressed immediates and word loads.
for p, rd, imm, f3 in [(0xa00501be,15,3,2),(0xa00501cc,15,3,2),(0xa00501d6,14,0,2),(0xa00501de,10,0,2),(0xa00501d8,11,-1,0),(0xa00501e2,12,-4,0),(0xa00501e4,10,4,0),(0xa00501e6,11,4,0),(0xa00501f2,14,1,0)]:
    w=raw[p]
    check(p,'raw C.LI/C.ADDI register/immediate',w&3==1 and w>>13==f3 and w>>7&31==rd and sx(((w>>12&1)<<5)|(w>>2&31),6)==imm)
for p,rd,rs1 in [(0xa00501ce,13,10),(0xa00501d0,14,11)]:
    w=raw[p]
    offset=((w>>10&7)<<3)|((w>>6&1)<<2)|((w>>5&1)<<6)
    check(p,'raw C.LW word width/zero offset',w&3==0 and w>>13==2 and (w>>2&7)+8==rd and (w>>7&7)+8==rs1 and offset==0)
check(0xa00501c4,'raw OR a5,a0,a1',raw[0xa00501c4]==0x00b567b3)
check(0xa00501c8,'raw C.ANDI a5,3',raw[0xa00501c8]==0x8b8d)
check(0xa00501fc,'raw SUB a0,a5,a3',raw[0xa00501fc]==0x40d78533)
for p in [0xa00501e0,0xa0050200]:
    check(p,'raw return C.JR ra',raw[p]==0x8082)
model=SOURCE/'evidence/rea-0041-20261017/ghidra/Ghidra/Processors/RISCV/data/languages/ap01thead2.sinc'
text=model.read_text()
section=text[text.index(':th.lrbu '):]
section=section[:section.index('}')+1]
assert 'local value:1 = *[ram]:1 ea;' in section and 'rd = zext(value);' in section
out={'status':'passed','rom_path':str(ROM),'mapping':'offset=VA-0x9ffff000','source_evidence_id':fn['evidence_id'],'extent':[hex(START),hex(END)],'bytes':len(data),'ordinary_instructions':len(rows)-len(custom),'vendor_words':len(custom),'instructions':rows,'checks':checks,'existing_model_path':str(model),'lrbu_model_excerpt':section,'limitations':['Static only; no ROM execution or runtime inputs.','Vendor semantics depend on existing local model, not new upstream attribution.','Checks are targeted encoding checks, not a formal proof.']}
(HERE/'instruction-evidence.json').write_text(json.dumps(out,indent=2)+'\n')
print(f"passed: {len(data)} bytes, {len(rows)-len(custom)} ordinary instructions, {len(custom)} vendor words, {len(checks)} checks")
