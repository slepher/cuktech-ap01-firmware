"""G04 independent static ROM reading; no old verifier import or execution."""
import json
from pathlib import Path
from capstone import Cs, CS_ARCH_RISCV, CS_MODE_RISCV32, CS_MODE_RISCVC

OUT = Path(__file__).resolve().parent
ROOT = Path('D:/Documents/PlatformIO/Projects/cuktech-ap01-firmware')
ROM = ROOT / 'roms/0041/ap01-1.0.2_0041.bin'
BASE = 0x9ffff000
data = ROM.read_bytes()
decoder = Cs(CS_ARCH_RISCV, CS_MODE_RISCV32 | CS_MODE_RISCVC)
spans = [
    ('submit', 0xa00ddbf6, 0xa00dddf4),
    ('width-height', 0xa0080e3e, 0xa0080e9a),
    ('four-word-copy', 0xa008b43a, 0xa008b456),
    ('contains', 0xa00894aa, 0xa008954c),
    ('event-wrapper', 0xa00814f4, 0xa0081554),
    ('event-list', 0xa008acfa, 0xa008adf4),
    ('overlap', 0xa0089472, 0xa00894aa),
    ('size', 0xa008928c, 0xa00892ac),
    ('consumer', 0xa00e0ac8, 0xa00e1294),
    ('event-cleanup', 0xa008ac38, 0xa008acfa),
    ('zero-wrapper', 0xa0080d8e, 0xa0080da6),
    ('slot-normal', 0xa00ecd68, 0xa00ecd76),
    ('copy-entry', 0xa000589c, 0xa00058aa),
    ('copy-alignment', 0xa000592c, 0xa0005950),
    ('copy-word-loop', 0xa0005992, 0xa00059d0),
    ('copy-return', 0xa0005916, 0xa0005918),
    ('zero-fill', 0xa0024906, 0xa00249c4),
    ('third-gate-tail', 0xa00ddbe4, 0xa00ddbf6),
]

def sext(value, bits):
    return value - (1 << bits) if value >> (bits - 1) else value

def bits(word, hi, lo):
    return (word >> lo) & ((1 << (hi - lo + 1)) - 1)

def destination(word, length, pc):
    # Decode control offsets without relying on Capstone's printed operands.
    if length == 4 and word & 127 == 0x63:
        off = (bits(word,31,31)<<12 | bits(word,7,7)<<11 |
               bits(word,30,25)<<5 | bits(word,11,8)<<1)
        return pc + sext(off,13)
    if length == 4 and word & 127 == 0x6f:
        off = (bits(word,31,31)<<20 | bits(word,19,12)<<12 |
               bits(word,20,20)<<11 | bits(word,30,21)<<1)
        return pc + sext(off,21)
    if length == 2 and word & 3 == 1 and word >> 13 in (1,5):
        off = (bits(word,12,12)<<11 | bits(word,11,11)<<4 |
               bits(word,10,9)<<8 | bits(word,8,8)<<10 |
               bits(word,7,7)<<6 | bits(word,6,6)<<7 |
               bits(word,5,3)<<1 | bits(word,2,2)<<5)
        return pc + sext(off,12)
    if length == 2 and word & 3 == 1 and word >> 13 in (6,7):
        off = (bits(word,12,12)<<8 | bits(word,11,10)<<3 |
               bits(word,6,5)<<6 | bits(word,4,3)<<1 | bits(word,2,2)<<5)
        return pc + sext(off,9)

rows = {}
windows = []
for label, start, stop in spans:
    pc = start
    current = []
    while pc < stop:
        off = pc - BASE
        half = int.from_bytes(data[off:off+2], 'little')
        length = 4 if half & 3 == 3 else 2
        raw = data[off:off+length]
        word = int.from_bytes(raw, 'little')
        decoded = list(decoder.disasm(raw, pc))
        vendor = length == 4 and word & 127 == 0x0b
        assert vendor or (len(decoded) == 1 and decoded[0].size == length), hex(pc)
        r = dict(address=hex(pc), offset=off, raw=raw.hex(), length=length,
                 mnemonic='vendor' if vendor else decoded[0].mnemonic,
                 operands='' if vendor else decoded[0].op_str)
        target = destination(word, length, pc)
        if target is not None: r['target'] = hex(target)
        if vendor:
            r['fields'] = dict(rd=bits(word,11,7), rs1=bits(word,19,15),
                               rs2=bits(word,24,20), funct3=bits(word,14,12),
                               funct7=bits(word,31,25), hi=bits(word,31,26),
                               lo=bits(word,25,20))
        rows[pc] = r
        current.append(r)
        pc += length
    assert pc == stop
    windows.append(dict(label=label, start=hex(start), stop=hex(stop), rows=current))

checks = []
def instruction(pc, name, operands):
    r = rows[pc]
    assert (r['mnemonic'], r['operands']) == (name, operands), r
    checks.append(dict(address=hex(pc), kind='instruction', expected=[name,operands]))

def target(pc, addr):
    assert rows[pc].get('target') == hex(addr), rows[pc]
    checks.append(dict(address=hex(pc), kind='control-target', expected=hex(addr)))

# Assertions selected independently after manual review of the new listing.
# These test bytes/decoded contracts, not execution or source equivalence.
for pc, name, args in [
    (0xa00ddc76,'jal','-0x1c2'),(0xa00ddc82,'lhu','a4, 0x32(a5)'),
    (0xa00ddcbc,'lhu','s2, 0x3e(s1)'),(0xa00ddcc0,'andi','s2, s2, 0x400'),
    (0xa00ddd08,'sw','zero, -0x40(s0)'),(0xa00ddd0c,'sw','zero, -0x3c(s0)'),
    (0xa00ddd16,'sw','a0, -0x38(s0)'),(0xa00ddd22,'sw','a0, -0x34(s0)'),
    (0xa00ddd46,'c.andi','a5, -8'),(0xa00ddd50,'ori','a5, a5, 7'),
    (0xa00ddd58,'lbu','a4, 0x3d(s1)'),(0xa00ddd62,'c.li','a2, 0x10'),
    (0xa00ddd64,'addi','a1, s0, -0x40'),(0xa00ddd72,'sw','a5, 0x264(s1)'),
    (0xa00ddd76,'c.li','a2, 0'),(0xa00ddd78,'addi','a1, zero, 0x38'),
    (0xa00ddd90,'addi','a2, s0, -0x30'),(0xa00ddd94,'addi','a1, zero, 0x35'),
    (0xa00ddd9e,'c.li','a5, 1'),(0xa00ddda0,'bne','a0, a5, -0x1e'),
    (0xa00ddda4,'lw','s3, 0x264(s1)'),(0xa00ddda8,'bltu','s2, s3, 0x2e'),
    (0xa00dddb2,'bgeu','a5, s3, 0xc'),(0xa00dddb6,'sw','zero, 0x264(s1)'),
    (0xa00dddbe,'lw','a0, 0x264(s1)'),(0xa00dddce,'lw','a5, 0x264(s1)'),
    (0xa00dddde,'c.li','a2, 0'),(0xa00894fa,'c.beqz','a2, -0x32'),
    (0xa0081516,'sw','s1, -0x2c(s0)'),(0xa008151a,'sw','s1, -0x28(s0)'),
    (0xa0081522,'sw','a2, -0x1c(s0)'),(0xa008152a,'c.li','a2, 1'),
    (0xa0081538,'bne','a0, a5, 0x10'),(0xa008153c,'c.li','a2, 0'),
    (0xa008ad16,'lbu','a5, 0x18(a1)'),(0xa008ad1a,'c.li','s1, 0'),
    (0xa008ad26,'c.li','a2, 0x14'),(0xa008ad3a,'lw','s7, 4(s2)'),
    (0xa008ad42,'c.lui','s5, 0xffff8'),(0xa008ad50,'c.addi','s5, -1'),
    (0xa008ad56,'lbu','s1, 0x18(s3)'),(0xa008ad5a,'c.andi','s1, 1'),
    (0xa008ad80,'and','a5, a5, s5'),(0xa008ad8a,'bne','a5, a3, -0x1e'),
    (0xa008ad92,'sw','a5, 0xc(s3)'),(0xa008ad98,'c.jalr','a5'),
    (0xa008ad9a,'lbu','a5, 0x18(s3)'),(0xa008ad9e,'andi','s1, a5, 2'),
    (0xa008ada4,'c.andi','a5, 1'),(0xa008adae,'c.li','s1, 1'),
    (0xa008adb4,'lbu','s1, 0x18(s3)'),(0xa008adb8,'c.andi','s1, 1'),
    (0xa008add8,'c.mv','a0, s1'),(0xa008adf0,'c.li','s1, 1'),
    (0xa00892a4,'mul','a0, a4, a5'),
    (0xa00e0c16,'lw','a5, 0x264(s2)'),(0xa00e0c1a,'bltu','s5, a5, -0x14'),
    (0xa00e0d04,'lw','a4, 0x264(a5)'),(0xa00e0d08,'blt','s3, a4, 0x356'),
    (0xa00e0d22,'sh','a5, 0x3e(a4)'),(0xa00e0d28,'lw','a4, 0x264(a5)'),
    (0xa00e0d38,'addi','a1, zero, 0x200'),(0xa00e0d3c,'addi','a0, a0, 0x44'),
    (0xa00e0d46,'addi','a1, zero, 0x20'),(0xa00e0d4a,'addi','a0, a0, 0x244'),
    (0xa00e0d54,'sw','zero, 0x264(a5)'),(0xa00e0d6c,'bgeu','s3, a5, -0x15c'),
    (0xa00e0dfe,'bgeu','s4, s2, 0x16'),(0xa00e0e10,'sb','s7, 0x244(a5)'),
    (0xa00e1090,'lw','s9, 0x44(a4)'),(0xa00e1094,'lw','s5, 0x48(a4)'),
    (0xa00e1098,'lw','s8, 0x4c(a4)'),(0xa00e109c,'lw','s4, 0x50(a4)'),
    (0xa00e1220,'andi','a4, a4, 0xff'),(0xa00e123e,'c.li','a1, 0'),
    (0xa00e1240,'c.add','a0, a5'),(0xa00e126e,'c.li','a2, 0x10'),
]: instruction(pc,name,args)
for pc, addr in [
    (0xa00ddc76,0xa00ddab4),(0xa00ddc7a,0xa00ddd82),
    (0xa00ddc9c,0xa00892ac),(0xa00ddd32,0xa00892f4),
    (0xa00ddd6c,0xa000589c),(0xa00ddd7e,0xa00814f4),
    (0xa00ddd9a,0xa00814f4),(0xa00ddda0,0xa00ddd82),
    (0xa00dddca,0xa008b43a),(0xa00dddd4,0xa00ddd72),
    (0xa00ddde6,0xa00894aa),(0xa00dddea,0xa00ddd82),
    (0xa0081532,0xa008acfa),(0xa0081544,0xa008acfa),
    (0xa008ad1e,0xa008adc4),(0xa008ad5c,0xa008ada8),
    (0xa008ada2,0xa008adae),(0xa008ada6,0xa008ad6c),
    (0xa008adba,0xa008ade0),(0xa008adec,0xa008acc6),
    (0xa00e0d40,0xa0080d8e),(0xa00e0d4e,0xa0080d8e),
    (0xa00e0d90,0xa0089472),(0xa00e0de8,0xa008928c),
    (0xa00e0df0,0xa008928c),(0xa00e0df8,0xa008928c),
    (0xa00e0dfe,0xa00e0e14),(0xa00e0e08,0xa008b43a),
    (0xa00e1148,0xa00e082e),(0xa00e11fc,0xa00e082e),
    (0xa00e1242,0xa00e1148),(0xa00e1260,0xa008af14),
    (0xa00e1272,0xa000589c),(0xa00e1282,0xa00e0d36),
]: target(pc,addr)

for pc, fields in [
    (0xa00dddee, dict(rd=18,rs1=18,funct3=3,hi=15,lo=0)),
    (0xa008ad78, dict(rd=13,rs1=15,funct3=3,hi=15,lo=15)),
    (0xa00e0daa, dict(rd=14,rs1=13,rs2=12,funct3=1,funct7=33)),
    (0xa00e0dbc, dict(rd=14,rs1=13,rs2=12,funct3=1,funct7=33)),
    (0xa00e0dce, dict(rd=14,rs1=13,rs2=12,funct3=1,funct7=33)),
    (0xa00e0de0, dict(rd=15,rs1=14,rs2=13,funct3=1,funct7=33)),
    (0xa0005992, dict(rd=14,rs1=11,funct3=4,funct7=44)),
    (0xa0005998, dict(rd=14,rs1=16,funct3=5,funct7=44)),
    (0xa00e1052, dict(rd=14,rs1=15,rs2=18,funct3=4,funct7=64)),
]:
    assert all(rows[pc]['fields'][k] == v for k,v in fields.items())
    checks.append(dict(address=hex(pc),kind='vendor-fields',expected=fields))

MODEL = ROOT / 'evidence/rea-0041-20261017/ghidra/Ghidra/Processors/RISCV/data/languages/ap01thead2.sinc'
model = MODEL.read_text(encoding='utf-8')
constructors = {}
for token in (':th.extu rd,rs1,15,0 ', ':th.extu rd,rs1,15,15 ',
              ':th.mvnez ', ':th.mveqz ', ':th.lrbu ', ':th.srw ',
              ':th.lwia ', ':th.swia ', ':th.mula '):
    begin = model.index(token)
    constructors[token] = model[begin:model.index('\n}',begin)+2]

def save():
    evidence = dict(method='Independent raw ROM extraction and static field review; no firmware/model execution',
                    rom=str(ROM), mapping='file offset = VA - 0x9ffff000', windows=windows,
                    checks=checks, model_source=str(MODEL), constructors=constructors)
    (OUT/'evidence.json').write_text(json.dumps(evidence,indent=2),encoding='utf-8')
    lines=[]
    for w in windows:
        lines.append('\n# '+w['label'])
        for r in w['rows']:
            lines.append((f"{r['address']} off={r['offset']:#x} {r['raw']} {r['mnemonic']} {r['operands']}"+
                         (' '+str(r['fields']) if 'fields' in r else '')+
                         (' -> '+r['target'] if 'target' in r else '')).rstrip())
    (OUT/'instructions.txt').write_text('\n'.join(lines)+'\n',encoding='utf-8')
    print(json.dumps(dict(windows=len(windows),bytes=sum(b-a for _,a,b in spans),
                         instructions=len(rows),vendor=sum('fields' in r for r in rows.values()),
                         checks=len(checks),result='passed')))

save()
