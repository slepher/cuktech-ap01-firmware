"""B13 independent raw-instruction review. Reads ROM; never runs target code."""
from pathlib import Path
import json

HERE = Path(__file__).resolve().parent
TREE = HERE.parents[2]
SOURCE = Path('D:/Documents/PlatformIO/Projects/cuktech-ap01-firmware')
BASE, START, END = 0x9ffff000, 0xa00501be, 0xa0050202
ROM = SOURCE / 'roms/0041/ap01-1.0.2_0041.bin'
data = ROM.read_bytes()[START - BASE:END - BASE]

def signed(value, bits):
    return value - (1 << bits) if value & (1 << (bits - 1)) else value

def decode(w, size, pc):
    if size == 4:
        op, rd, f3, r1, r2, f7 = w & 127, w >> 7 & 31, w >> 12 & 7, w >> 15 & 31, w >> 20 & 31, w >> 25
        if op == 0x63:
            imm = (w >> 31 << 12) | ((w >> 7 & 1) << 11) | ((w >> 25 & 63) << 5) | ((w >> 8 & 15) << 1)
            return [{0:'beq',1:'bne',6:'bltu',7:'bgeu'}[f3], r1, r2, pc + signed(imm, 13)]
        if op == 0x33:
            return [{(6,0):'or',(0,32):'sub'}[(f3,f7)], rd, r1, r2]
        assert op == 11 and f3 == 4 and w >> 27 == 16
        return ['indexed_u8_local_model', rd, r1, r2, w >> 25 & 3]
    q, f3 = w & 3, w >> 13
    if q == 0:
        assert f3 == 2
        off = ((w >> 10 & 7) << 3) | ((w >> 6 & 1) << 2) | ((w >> 5 & 1) << 6)
        return ['lw', (w >> 2 & 7) + 8, (w >> 7 & 7) + 8, off]
    if q == 2:
        assert f3 == 4 and w >> 12 & 1 == 0 and w >> 2 & 31 == 0
        return ['jr', w >> 7 & 31]
    assert q == 1
    if f3 in (0,2):
        return ['addi' if f3 == 0 else 'li', w >> 7 & 31, signed(((w >> 12 & 1) << 5) | (w >> 2 & 31), 6)]
    if f3 == 4:
        assert w >> 10 & 3 == 2
        return ['andi', (w >> 7 & 7) + 8, signed(((w >> 12 & 1) << 5) | (w >> 2 & 31), 6)]
    if f3 == 7:
        imm = ((w >> 12 & 1) << 8) | ((w >> 10 & 3) << 3) | ((w >> 5 & 3) << 6) | ((w >> 3 & 3) << 1) | ((w >> 2 & 1) << 5)
        return ['bnez', (w >> 7 & 7) + 8, pc + signed(imm, 9)]
    assert f3 == 5
    imm = ((w >> 12 & 1) << 11) | ((w >> 11 & 1) << 4) | ((w >> 9 & 3) << 8) | ((w >> 8 & 1) << 10) | ((w >> 7 & 1) << 6) | ((w >> 6 & 1) << 7) | ((w >> 3 & 7) << 1) | ((w >> 2 & 1) << 5)
    return ['j', pc + signed(imm, 12)]

# Expected operand-level contract, separately specified from B12's checker.
expected = [
    (0x1be,['li',15,3]), (0x1c0,['bgeu',15,12,0xa00501d6]),
    (0x1c4,['or',15,10,11]), (0x1c8,['andi',15,3]),
    (0x1ca,['bnez',15,0xa00501d6]), (0x1cc,['li',15,3]),
    (0x1ce,['lw',13,10,0]), (0x1d0,['lw',14,11,0]),
    (0x1d2,['beq',13,14,0xa00501e2]), (0x1d6,['li',14,0]),
    (0x1d8,['addi',11,-1]), (0x1da,['bne',12,14,0xa00501ee]),
    (0x1de,['li',10,0]), (0x1e0,['jr',1]),
    (0x1e2,['addi',12,-4]), (0x1e4,['addi',10,4]),
    (0x1e6,['addi',11,4]), (0x1e8,['bltu',15,12,0xa00501ce]),
    (0x1ec,['j',0xa00501d6]), (0x1ee,['indexed_u8_local_model',15,10,14,0]),
    (0x1f2,['addi',14,1]), (0x1f4,['indexed_u8_local_model',13,11,14,0]),
    (0x1f8,['beq',15,13,0xa00501da]), (0x1fc,['sub',10,15,13]),
    (0x200,['jr',1]),
]
rows, cursor = [], 0
for low, want in expected:
    pc = 0xa0050000 + low
    assert pc == START + cursor
    size = 4 if data[cursor] & 3 == 3 else 2
    raw = data[cursor:cursor+size]
    actual = decode(int.from_bytes(raw,'little'),size,pc)
    assert actual == want, (hex(pc),actual,want)
    rows.append({'va':hex(pc),'offset':pc-BASE,'raw':raw.hex(),'decoded':actual,'status':'accepted'})
    cursor += size
assert cursor == 68 == len(data)
dossier = json.loads((TREE / 'reverse/analysis/usb-interface-ota-0041-20261023.json').read_text())
fn = next(f for f in dossier['functions'] if f['address'] == hex(START))
assert fn['raw_ranges'][0]['bytes_hex'] == data.hex()
assert fn['body']['ranges'] == [{'start':hex(START),'end':hex(END-1)}]
b12 = json.loads((TREE / 'reverse/analysis/compare-contract-b12-0041-20261023/instruction-evidence.json').read_text())
assert [(r['va'],r['raw']) for r in rows] == [(r['address'],r['hex']) for r in b12['instructions']]
model = SOURCE / 'evidence/rea-0041-20261017/ghidra/Ghidra/Processors/RISCV/data/languages/ap01thead2.sinc'
model_text = model.read_text()
excerpt = model_text[model_text.index(':th.lrbu '):].split('}',1)[0] + '}'
assert excerpt == b12['lrbu_model_excerpt']
assert 'local delta:4 = rs2 << thshift;' in excerpt
assert 'local updated:4 = rs1 + delta;' in excerpt
assert 'local value:1 = *[ram]:1 ea;' in excerpt
assert 'rd = zext(value);' in excerpt
assert 'rs1 =' not in excerpt and 'rs2 =' not in excerpt
result = {'status':'passed','bytes':68,'instruction_count':25,'ordinary':23,'vendor':2,
          'mapping':'offset=VA-0x9ffff000','rom':str(ROM),'range_inclusive':[hex(START),hex(END-1)],
          'retained_evidence':fn['evidence_id'],'instructions':rows,
          'model_path':str(model),'model_excerpt':excerpt,
          'checks':['25 instructions decoded directly from raw bits with operand/target assertions',
                    'contiguous 68-byte extent and retained dossier bytes/body agree',
                    'B12 preserved instruction byte sequence agrees',
                    'existing lrbu model agrees; no base/index writeback in constructor'],
          'limits':['Static only; no execution, emulator, input generation or target connection.',
                    'Vendor meaning remains conditional on existing local model; no independent upstream ISA certification.',
                    'No source/version attribution or caller-wide invariant is established.']}
(HERE / 'review-evidence.json').write_text(json.dumps(result,indent=2)+'\n')
print('passed: 68B / 25 raw decodes (23 ordinary + 2 vendor); dossier, B12 bytes and local model agree')
