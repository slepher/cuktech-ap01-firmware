"""B11 independent static raw-field review. Reads ROM; never executes it."""
from pathlib import Path
import json
from capstone import Cs, CS_ARCH_RISCV, CS_MODE_RISCV32, CS_MODE_RISCVC

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
SOURCE = Path('D:/Documents/PlatformIO/Projects/cuktech-ap01-firmware')
ROM = SOURCE / 'roms/0041/ap01-1.0.2_0041.bin'
data = ROM.read_bytes()
base = 0x9ffff000
prior = json.loads((ROOT / 'reverse/analysis/basic-info-dispatch-caller-b10-0041-20261023/instruction-evidence.json').read_text())
md = Cs(CS_ARCH_RISCV, CS_MODE_RISCV32 | CS_MODE_RISCVC)
rows, checks = [], []
def sx(v, n):
    return v - (1 << n) if v & (1 << (n-1)) else v
def word(a):
    return int.from_bytes(data[a-base:a-base+4], 'little')
def record(a, kind, actual, expected):
    assert actual == expected, (hex(a), kind, actual, expected)
    checks.append(dict(address=hex(a), kind=kind, actual=actual, expected=expected))
for window in prior['windows']:
    p = int(window['start'], 16)
    for old in window['instructions']:
        assert int(old['address'],16) == p
        size = 2 if data[p-base] & 3 != 3 else 4
        raw = data[p-base:p-base+size]
        assert raw.hex() == old['hex']
        decoded = next(md.disasm(raw,p), None)
        if decoded:
            asm = decoded.mnemonic + ' ' + decoded.op_str
            assert asm == old['decode'] and decoded.size == size
        else:
            assert p == 0xa00a53de and raw.hex() == '8b17e520'
            asm = 'vendor word; raw fields reviewed separately'
        rows.append(dict(address=hex(p), offset=p-base, raw=raw.hex(), decode=asm))
        p += size
    assert p == int(window['end_exclusive'],16)

def i(a, op, rd, f3, rs1, imm):
    w=word(a)
    record(a,'I fields [opcode,rd,funct3,rs1,signed immediate]',
           [w&127,(w>>7)&31,(w>>12)&7,(w>>15)&31,sx(w>>20,12)], [op,rd,f3,rs1,imm])
def b(a, f3, r1, r2, dst):
    w=word(a)
    disp=((w>>31)<<12)|((w>>7&1)<<11)|((w>>25&63)<<5)|((w>>8&15)<<1)
    record(a,'B fields [opcode,funct3,rs1,rs2,target]',
           [w&127,w>>12&7,w>>15&31,w>>20&31,a+sx(disp,13)], [99,f3,r1,r2,dst])
def j(a, rd, dst):
    w=word(a)
    disp=((w>>31)<<20)|((w>>12&255)<<12)|((w>>20&1)<<11)|((w>>21&1023)<<1)
    record(a,'J fields [opcode,rd,target]',[w&127,w>>7&31,a+sx(disp,21)],[111,rd,dst])
def mv(a, rd, rs):
    w=word(a)&65535
    record(a,'C.MV fields',[w>>12,w&3,w>>7&31,w>>2&31],[8,2,rd,rs])
def cb(a, f3, rs, dst):
    w=word(a)&65535
    disp=((w>>12&1)<<8)|((w>>5&3)<<6)|((w>>2&1)<<5)|((w>>10&3)<<3)|((w>>3&3)<<1)
    record(a,'CB fields',[w&3,w>>13,8+(w>>7&7),a+sx(disp,9)],[1,f3,rs,dst])
def store(a,f3,rs1,rs2,imm):
    w=word(a)
    record(a,'S fields',[w&127,w>>12&7,w>>15&31,w>>20&31,sx(((w>>25)<<5)|(w>>7&31),12)], [35,f3,rs1,rs2,imm])
for a,imm in [(0xa00a85ac,0x57),(0xa00a85c0,0x51),(0xa00a8602,0x55),(0xa00a860a,0x56),(0xa00a8616,0x52)]:
    i(a,19,15,0,0,imm)
for args in [(0xa00a85b0,1,10,15,0xa00a85b8),(0xa00a85bc,6,15,10,0xa00a873e),(0xa00a85c4,0,10,15,0xa00a93a4),(0xa00a85c8,6,15,10,0xa00a8602),(0xa00a8606,0,10,15,0xa00a88f6),(0xa00a860e,1,10,15,0xa00a8616),(0xa00a861a,1,10,15,0xa00a85e4),(0xa00a8690,0,14,13,0xa00a8698),(0xa00a86b2,1,18,0,0xa00a86ba),(0xa00a53d4,7,10,14,0xa00a53ea)]:
    b(*args)
for args in [(0xa00a8626,3,22,4,12,0),(0xa00a8684,3,14,2,8,-72),(0xa00a868c,19,13,0,15,0x112),(0xa00a8698,3,18,2,21,40),(0xa00a869c,19,11,0,9,5),(0xa00a863a,19,11,0,9,1),(0xa00a863e,19,10,0,8,-72),(0xa00a86ba,3,11,2,8,-100),(0xa00a53ca,3,15,2,15,0x2cc),(0xa00a53d0,3,14,4,15,6),(0xa00a53da,19,14,0,0,0x1a8)]:
    i(*args)
for args in [(0xa00a85ba,9,12),(0xa00a862a,10,22),(0xa00a8630,21,10),(0xa00a86a2,10,18),(0xa00a86c0,10,18),(0xa00a8734,10,22),(0xa00a53e4,10,15)]:
    mv(*args)
for args in [(0xa00a862c,1,0xa00a53c0),(0xa00a8642,1,0xa000589c),(0xa00a8680,1,0xa008b51a),(0xa00a86a8,1,0xa00501be),(0xa00a86c2,1,0xa000589c),(0xa00a872a,1,0xa008b51a),(0xa00a8736,1,0xa00a389c),(0xa00a8634,0,0xa00a9aac),(0xa00a8694,0,0xa00a9a8a),(0xa00a86ae,0,0xa00a9aac),(0xa00a86b6,0,0xa00a9aac),(0xa00a873a,0,0xa00a9aac)]:
    j(*args)
for args in [(0xa00a8632,7,10,0xa00a8638),(0xa00a86ac,7,10,0xa00a86b2),(0xa00a53ce,6,15,0xa00a53e2)]:
    cb(*args)
store(0xa00a85a0,0,8,10,-80)
store(0xa00a8622,0,15,0,0x2f0)
store(0xa00a86a4,2,8,11,-100)
store(0xa00a8730,2,21,15,0)
for a,expected in [(0xa00a861e,0x62fcb7b7),(0xa00a8688,0x2b0107b7),(0xa00a53c6,0x62fcb7b7)]:
    record(a,'LUI complete raw word',word(a),expected)
for a,expected in [(0xa00a8638,0x4621),(0xa00a86a0,0x4651),(0xa00a86be,0x4651),(0xa00a872e,0x6791),(0xa00a53d8,0x439c),(0xa00a53ea,0x4781),(0xa00a53ec,0xbfdd),(0xa00a53e8,0x8082)]:
    record(a,'compressed immediate/load/return raw encoding',word(a)&65535,expected)
w=word(0xa00a53de)
record(0xa00a53de,'vendor [opcode,rd,funct3,rs1,rs2,funct7]',[w&127,w>>7&31,w>>12&7,w>>15&31,w>>20&31,w>>25],[11,15,1,10,14,16])
model=SOURCE/'evidence/rea-0041-20261017/ghidra/Ghidra/Processors/RISCV/data/languages/ap01thead2.sinc'
model_text=model.read_text()
assert ':th.mula rd,rs1,rs2 is op0006=0xb & op1214=1 & op2531=16' in model_text
assert 'rd = rd + (rs1 * rs2);' in model_text
result=dict(task='B11',result='passed',source=str(ROM),mapping='offset=VA-0x9ffff000',windows=2,bytes=sum(len(bytes.fromhex(r['raw'])) for r in rows),ordinary_instructions=len(rows)-1,vendor_words=1,raw_checks=len(checks),rows=rows,checks=checks,model=dict(path=str(model),line=25,scope='existing local model only; no upstream ISA verification'))
(HERE/'review-evidence.json').write_text(json.dumps(result,indent=2)+'\n')
print(json.dumps({k:v for k,v in result.items() if k not in ['rows','checks','model']}))
