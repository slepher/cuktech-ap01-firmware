"""L04 independent static field review; reads original ROM, never executes it."""
from pathlib import Path
import json

MAIN = Path('D:/Documents/PlatformIO/Projects/cuktech-ap01-firmware')
ROM = (MAIN / 'roms/0041/ap01-1.0.2_0041.bin').read_bytes()
BASE = 0x9ffff000
OUT = Path(__file__).resolve().parent
items = []

def signed(x, bits):
    return x - (1 << bits) if x >> (bits - 1) else x

def value(pc, size=4):
    return int.from_bytes(ROM[pc-BASE:pc-BASE+size], 'little')

def record(pc, size, decoded, expected):
    assert decoded == expected, (hex(pc), decoded, expected)
    items.append({'pc': hex(pc), 'raw': ROM[pc-BASE:pc-BASE+size].hex(), 'fields': decoded})

def i(pc, op, funct3, rd, rs, imm):
    w = value(pc)
    record(pc, 4, [w & 127, (w >> 12) & 7, (w >> 7) & 31, (w >> 15) & 31, signed(w >> 20, 12)], [op, funct3, rd, rs, imm])

def lui(pc, rd, upper):
    w = value(pc)
    record(pc, 4, [w & 127, (w >> 7) & 31, w & 0xfffff000], [0x37, rd, upper])

def store(pc, funct3, rs1, rs2, offset):
    w = value(pc)
    displacement = signed(((w >> 25) << 5) | ((w >> 7) & 31), 12)
    record(pc, 4, [w & 127, (w >> 12) & 7, (w >> 15) & 31, (w >> 20) & 31, displacement], [0x23, funct3, rs1, rs2, offset])

def jal(pc, target):
    w = value(pc)
    d = ((w >> 31) << 20) | (((w >> 12) & 255) << 12) | (((w >> 20) & 1) << 11) | (((w >> 21) & 1023) << 1)
    record(pc, 4, [w & 127, (w >> 7) & 31, pc + signed(d, 21)], [0x6f, 1, target])

def beq(pc, rs1, rs2, target):
    w = value(pc)
    d = ((w >> 31) << 12) | (((w >> 7) & 1) << 11) | (((w >> 25) & 63) << 5) | (((w >> 8) & 15) << 1)
    record(pc, 4, [w & 127, (w >> 12) & 7, (w >> 15) & 31, (w >> 20) & 31, pc + signed(d, 13)], [0x63, 0, rs1, rs2, target])

def cli(pc, rd, imm):
    w = value(pc, 2)
    record(pc, 2, [w & 3, w >> 13, (w >> 7) & 31, signed(((w >> 12) & 1) * 32 + ((w >> 2) & 31), 6)], [1, 2, rd, imm])

def clw(pc, rd, rs, offset):
    w = value(pc, 2)
    d = (((w >> 5) & 1) << 6) | (((w >> 10) & 7) << 3) | (((w >> 6) & 1) << 2)
    record(pc, 2, [w & 3, w >> 13, 8 + ((w >> 2) & 7), 8 + ((w >> 7) & 7), d], [0, 2, rd, rs, offset])

def cmv(pc, rd, rs, add=False):
    w = value(pc, 2)
    record(pc, 2, [w & 3, w >> 12, (w >> 7) & 31, (w >> 2) & 31], [2, 9 if add else 8, rd, rs])

def cb(pc, nonzero, rs, target):
    w = value(pc, 2)
    d = (((w >> 12) & 1) << 8) | (((w >> 10) & 3) << 3) | (((w >> 5) & 3) << 6) | (((w >> 3) & 3) << 1) | (((w >> 2) & 1) << 5)
    record(pc, 2, [w & 3, w >> 13, 8 + ((w >> 7) & 7), pc + signed(d, 9)], [1, 7 if nonzero else 6, rs, target])

def cj(pc, target):
    w = value(pc, 2)
    d = (((w >> 12) & 1) << 11) | (((w >> 11) & 1) << 4) | (((w >> 9) & 3) << 8) | (((w >> 8) & 1) << 10) | (((w >> 7) & 1) << 6) | (((w >> 6) & 1) << 7) | (((w >> 3) & 7) << 1) | (((w >> 2) & 1) << 5)
    record(pc, 2, [w & 3, w >> 13, pc + signed(d, 12)], [1, 5, target])

# Original caller addressing and zero-extension, not the unverified L01 byte literal.
lui(0xa00fd1d0, 20, 0x62fc4000)
i(0xa00fd1e8, 0x13, 0, 20, 20, 0x2c)
i(0xa00feac4, 3, 4, 10, 20, 1)
cli(0xa00feadc, 10, 3)
for pc in (0xa00feacc, 0xa00feae2):
    i(pc, 3, 2, 15, 8, -0x58)
for pc, arg in ((0xa00fead0, 0), (0xa00feae6, 1)):
    cli(pc, 11, arg)
    clw(pc + 2, 10, 15, 8)

# Same-value branch bypasses publication and both calls. No input masking before compare.
lui(0xa00ab478, 15, 0x62fc9000)
i(0xa00ab47c, 0x13, 0, 15, 15, 0x98)
i(0xa00ab480, 3, 4, 14, 15, 2)
beq(0xa00ab484, 14, 10, 0xa00ab4a6)
store(0xa00ab490, 0, 15, 10, 2)
cli(0xa00ab494, 10, 3)

# Notify's live global pointer and callback ABI, then dynamic next-link reload.
lui(0xa00a5bcc, 15, 0x62fcb000)
i(0xa00a5bd2, 0x13, 0, 14, 15, 0x4ec)
clw(0xa00a5bd6, 9, 14, 4)
cmv(0xa00a5bd8, 19, 10)
i(0xa00a5bda, 0x13, 0, 18, 15, 0x4ec)
lui(0xa00a5bde, 20, 0x62fc9000)
cb(0xa00a5be2, True, 9, 0xa00a5bf4)
clw(0xa00a5bf4, 15, 9, 0)
cb(0xa00a5bf6, False, 15, 0xa00a5c02)
clw(0xa00a5bf8, 10, 9, 4)
cmv(0xa00a5bfa, 12, 19)
i(0xa00a5bfc, 0x13, 0, 11, 20, 0x98)
record(0xa00a5c00, 2, [value(0xa00a5c00, 2) & 3, value(0xa00a5c00, 2) >> 12, (value(0xa00a5c00, 2) >> 7) & 31, (value(0xa00a5c00, 2) >> 2) & 31], [2, 9, 15, 0])
i(0xa00a5c02, 3, 2, 15, 18, 0)
cmv(0xa00a5c06, 9, 15, add=True)
clw(0xa00a5c08, 9, 9, 4)
cj(0xa00a5c0a, 0xa00a5be2)

# Writer's existing body is inherited; verify only the service boundary and return consumption.
lui(0xa00ab27e, 11, 0xa026a000)
lui(0xa00ab282, 10, 0xa026a000)
i(0xa00ab286, 0x13, 0, 11, 11, 0x218)
i(0xa00ab28a, 0x13, 0, 10, 10, 0x21c)
cb(0xa00ab292, True, 10, 0xa00ab2c0)
cmv(0xa00ab2c0, 9, 10)
lui(0xa00ab2c6, 15, 0x62fc9000)
i(0xa00ab2ca, 0x13, 0, 14, 15, 0x98)
store(0xa00ab2ce, 1, 14, 10, 6)
cmv(0xa00ab2d2, 13, 9)
cli(0xa00ab2d4, 12, 1)
cli(0xa00ab2d6, 11, 8)
i(0xa00ab2d8, 0x13, 0, 10, 15, 0x98)
cmv(0xa00ab2e0, 10, 9)
cj(0xa00ab2e6, 0xa00ab2b6)

for pc, target in [(0xa00feac8,0xa00ab478),(0xa00feade,0xa00ab478),(0xa00fead4,0xa018f232),(0xa00feaea,0xa018f232),(0xa00ab496,0xa00a5bbe),(0xa00ab49a,0xa00ab274),(0xa00ab28e,0xa0134856),(0xa00ab2b2,0xa008b51a),(0xa00ab2c2,0xa00a46e8),(0xa00ab2dc,0xa0134adc),(0xa00ab2e2,0xa01a8de6)]:
    jal(pc, target)

# Confirm the local tails contain only register restores, stack adjustment and ret.
for start, end, expected in [(0xa00ab49e,0xa00ab4a8,'b2402244410182808280'),(0xa00ab2b6,0xa00ab2c0,'b2402244924441018280')]:
    actual=ROM[start-BASE:end-BASE].hex()
    assert actual==expected
    items.append({'pc':hex(start),'raw':actual,'meaning':'restore-only tail, no success assignment'})

strings={}
for pc, expected in [(0xa026a218,'wb'),(0xa026a21c,'/data/sysconfig.bin')]:
    actual=ROM[pc-BASE:pc-BASE+64].split(b'\0')[0].decode('ascii')
    assert actual==expected
    strings[hex(pc)]=actual

old=json.loads((MAIN/'evidence/rea-0041-20261017/evidence/whole-rom-private-20261023-071.json').read_text(encoding='utf-8'))['structuredContent']
assert old['parameters']['procedure']=='0xa00ab274'
result={'status':'PASS','reviewed':'L03','baseline':'dbd788a','field_records':len(items),'original_rom':str(MAIN/'roms/0041/ap01-1.0.2_0041.bin'),'items':items,'strings':strings,'inherited_writer_evidence':old['evidence_id'],'limits':['Independent static field decode; no L03 script import or execution','No target, SIM, input replay, build, model or device execution','No file-service or subscriber lifecycle recovery; no durable-success claim','New recovered functionality: 0']}
(OUT/'review-result.json').write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
print(json.dumps({'status':'PASS','field_records':len(items),'strings':len(strings)}))
