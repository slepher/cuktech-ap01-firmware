"""Independent bounded static review. Python stdlib only; never imports author code.

Decodes selected RV32I/RVC fields from ROM, alongside original retained text.
This is an offline decoder, not an instruction interpreter or firmware runner.
"""
import json
from pathlib import Path

ROOT = Path('D:/Documents/PlatformIO/Projects/cuktech-ap01-firmware')
OUT = Path(__file__).parent
BASE = 0x9ffff000
rom = (ROOT / 'roms/0041/ap01-1.0.2_0041.bin').read_bytes()
assert len(rom) == 6769704
saved = json.loads((ROOT / 'evidence/rea-0041-20261017/evidence/whole-rom-private-20261023.evidence.json').read_text(encoding='utf-8'))
old = json.loads((ROOT / 'reverse/rehost/system-complete-0041.json').read_text(encoding='utf-8'))
PROCS = ['0xa00adabc', '0xa005cc1e', '0xa00ad602']
records = {p: next(r for r in saved['records'] if r.get('parameters', {}).get('procedure') == p) for p in PROCS}
text = {}
for record in records.values():
    assert record['analysis_profile']['parameters']['language_id'] == 'RISCV:LE:32:ap01thead2'
    assert record['analysis_profile']['digest'] == 'b6368dd18431e8113aa5026c713d41e648ab0f6ddd9421ff6c4a49e23b3cd2f3'
    for line in record['normalized_result']['assembly']:
        address, assembly = line.split(': ', 1)
        text[int(address, 16)] = assembly
helper = {int(i['address'], 16): i for i in old['local_disassembly']['0xa00ad486']}
text.update({a: i['instruction'] for a, i in helper.items()})

def sx(n, bits):
    return n - (1 << bits) if n & (1 << (bits - 1)) else n

def decode(a):
    h = int.from_bytes(rom[a-BASE:a-BASE+2], 'little')
    if h & 3 == 3:
        w = int.from_bytes(rom[a-BASE:a-BASE+4], 'little')
        op, rd, f3, r1, r2 = w & 127, w >> 7 & 31, w >> 12 & 7, w >> 15 & 31, w >> 20 & 31
        d = dict(width=4, opcode=op, rd=rd, rs1=r1, rs2=r2, funct3=f3)
        if op in (3, 0x13): d['imm'] = sx(w >> 20, 12)
        if op == 0x23: d['imm'] = sx((w >> 25 << 5) | (w >> 7 & 31), 12)
        if op == 0x37: d['imm'] = w & 0xfffff000
        if op == 0x6f:
            delta = ((w >> 31) << 20) | ((w >> 12 & 255) << 12) | ((w >> 20 & 1) << 11) | ((w >> 21 & 1023) << 1)
            d['target'] = a + sx(delta, 21)
        if op == 0x63:
            delta = ((w >> 31) << 12) | ((w >> 7 & 1) << 11) | ((w >> 25 & 63) << 5) | ((w >> 8 & 15) << 1)
            d['target'] = a + sx(delta, 13)
        return d
    q, f = h & 3, h >> 13
    d = dict(width=2, quadrant=q, funct3=f)
    if q == 0 and f == 2:
        d.update(rd=8+(h >> 2 & 7), rs1=8+(h >> 7 & 7), imm=((h >> 5 & 1) << 6) | ((h >> 10 & 7) << 3) | ((h >> 6 & 1) << 2))
    if q == 1 and f in (0, 2, 3):
        d.update(rd=h >> 7 & 31, imm=sx(((h >> 12 & 1) << 5) | (h >> 2 & 31), 6))
        if f == 3 and d['rd'] != 2: d['imm'] <<= 12
    if q == 1 and f == 4:
        d.update(rd=8+(h >> 7 & 7), subop=h >> 10 & 3, rs2=8+(h >> 2 & 7), imm=sx(((h >> 12 & 1) << 5) | (h >> 2 & 31), 6))
    if q == 1 and f == 5:
        bits = [(12,11),(11,4),(10,9),(9,8),(8,10),(7,6),(6,7),(5,3),(4,2),(3,1),(2,5)]
        d['target'] = a + sx(sum(((h >> s) & 1) << t for s,t in bits), 12)
    if q == 1 and f in (6,7):
        bits = [(12,8),(11,4),(10,3),(6,7),(5,6),(4,2),(3,1),(2,5)]
        d.update(rs1=8+(h >> 7 & 7), target=a + sx(sum(((h >> s) & 1) << t for s,t in bits),9))
    if q == 2 and f == 4: d.update(rd=h >> 7 & 31, rs2=h >> 2 & 31, add=bool(h & 0x1000))
    return d

windows = [(0xa00ae250,0xa00ae340),(0xa00ae3aa,0xa00ae3b4),(0xa00adcba,0xa00adce0),(0xa00ae1b6,0xa00ae1c8),(0xa00ad602,0xa00ad620),(0xa005da14,0xa005da78),(0xa00adc08,0xa00adc10),(0xa00adc2c,0xa00adc46),(0xa00ad486,0xa00ad4da),(0xa00ad4e6,0xa00ad522),(0xa00ad550,0xa00ad58c),(0xa00ad5ba,0xa00ad5c6),(0xa00ad5de,0xa00ad5ee)]
rows=[]
for lo,hi in windows:
    a=lo
    while a<hi:
        d=decode(a); n=d['width']
        assert a in text and a+n <= hi
        raw=rom[a-BASE:a-BASE+n]
        if a in helper: assert raw.hex() == helper[a]['bytes']
        rows.append(dict(address=hex(a),hex=raw.hex(),retained=text[a],decoded=d))
        a+=n
    assert a==hi

checks=[]
def check(a, **expected):
    actual=decode(a)
    assert all(actual[k]==v for k,v in expected.items()), (hex(a),actual,expected)
    checks.append(dict(address=hex(a),expected=expected))

# Numeric registers follow the RV32 ABI: S=s9=x25, index=s8=x24.
for a,rs,rd,imm,f in [(0xa00ae25a,15,25,4,2),(0xa00ae25e,25,14,0x9c,4),(0xa00ae27c,25,11,0x9c,4),(0xa00ae2bc,25,13,0x102,4),(0xa00ae2c0,25,14,0x103,4),(0xa00ae2c6,25,13,0x104,4),(0xa00ae2cc,25,13,0x105,4),(0xa00ae2d2,25,13,0x101,4),(0xa00ae2ea,25,10,0xf4,2),(0xa00ae3aa,25,10,0xf4,2)]:
    check(a,opcode=3,rs1=rs,rd=rd,imm=imm,funct3=f)
for a,rs,r2,imm,f in [(0xa00ae290,25,14,0x9c,0),(0xa00ae294,13,12,0x9d,0),(0xa00ae298,13,0,0x101,0),(0xa00ae29c,13,0,0xfc,0),(0xa00ae328,15,0,0x28,0),(0xa00ae32c,25,0,0xfa,1),(0xa005da5e,19,10,0x74,2),(0xa005da6c,23,18,4,2),(0xa005da74,9,23,0x10,2)]:
    check(a,opcode=0x23,rs1=rs,rs2=r2,imm=imm,funct3=f)
for a,t in [(0xa00ae254,0xa00dcee4),(0xa00ae278,0xa00d8f7c),(0xa00ae2aa,0xa00ad486),(0xa00ae2b8,0xa00ad486),(0xa00ae2e6,0xa00ad486),(0xa00ae2f4,0xa008bd16),(0xa00ae3ae,0xa00ad602),(0xa005da5a,0xa008bc64),(0xa005da62,0xa008bd16)]: check(a,opcode=0x6f,rd=1,target=t)
for a,t in [(0xa00ae26c,0xa00ae298),(0xa00ae2dc,0xa00ae3aa),(0xa00ae2f2,0xa00ae318),(0xa00ae3b2,0xa00ae2ea),(0xa00ae33e,0xa00adcba),(0xa00ad494,0xa00ad5ba),(0xa00ad49c,0xa00ad4f0),(0xa00ad4a0,0xa00ad550),(0xa00ad552,0xa00ad4e6),(0xa00ad5ba,0xa00ad5de),(0xa00ad5e0,0xa00ad4e6),(0xa00ad5c2,0xa00ad506),(0xa00ad5ea,0xa00ad506)]: check(a,target=t)
for a,rd,imm in [(0xa00ae2a6,11,2),(0xa00ae2b4,11,1),(0xa00ae2de,13,0),(0xa00ae2e0,12,1),(0xa00ae2e2,11,0),(0xa005da4a,11,4096)]: check(a,rd=rd,imm=imm)
for a,rs,rd,imm in [(0xa00ae2a2,24,13,255),(0xa00ae2ae,24,13,255),(0xa00ae2d8,14,14,255),(0xa00ae318,24,15,255),(0xa005da14,18,19,128),(0xa005da52,11,11,-0x448),(0xa005da56,10,10,0x602),(0xa00adc36,20,20,0x2c),(0xa00ae1ba,24,27,1)]: check(a,opcode=0x13,rs1=rs,rd=rd,imm=imm)
check(0xa005da4c,opcode=0x37,rd=10,imm=0xa00ad000)
check(0xa00ad61e,rd=9,rs1=10,imm=12)
check(0xa00ae2ee,rd=14,rs1=10,imm=20)
check(0xa00ae2f0,rd=14,subop=2,imm=1)
# Selected helper widget loads. s1 is rebased +0x80 on the six-widget paths.
for a,rs,offset in [(0xa00ad4a4,9,0xa4),(0xa00ad556,9,0xcc),(0xa00ad5bc,9,0xbc),(0xa00ad5e4,9,0xe4)]:
    check(a,opcode=3,rd=10,rs1=rs,imm=offset,funct3=2)
for a,rs,offset in [(0xa00ad4b4,9,0x28),(0xa00ad4bc,9,0x2c),(0xa00ad4c4,9,0x30),(0xa00ad4cc,9,0x38),(0xa00ad4d4,9,0x34),(0xa00ad566,9,0x50),(0xa00ad56e,9,0x54),(0xa00ad576,9,0x58),(0xa00ad57e,9,0x60),(0xa00ad586,9,0x5c),(0xa00ad4f0,10,0x54),(0xa00ad510,9,0x58),(0xa00ad518,9,0x4c)]:
    check(a,rd=10,rs1=rs,imm=offset)
for a in [0xa00ad4b0,0xa00ad4b8,0xa00ad4c0,0xa00ad4c8,0xa00ad4d0,0xa00ad506,0xa00ad562,0xa00ad56a,0xa00ad572,0xa00ad57a,0xa00ad582]: check(a,opcode=0x6f,rd=1,target=0xa00d8f7c)
for a in [0xa00ad50c,0xa00ad514,0xa00ad51c]: check(a,opcode=0x6f,rd=1,target=0xa00d9044)
check(0xa00ad4ac,opcode=0x13,rd=9,rs1=9,imm=0x80)
check(0xa00ad55e,opcode=0x13,rd=9,rs1=9,imm=0x80)
check(0xa00ad4f4,target=0xa00ad50c)
check(0xa00ad4d8,target=0xa00ad506)
check(0xa00ad58a,target=0xa00ad506)
# No instruction between load T and pause writes a0: load/AND/branch all use a4.
check(0xa00ae2f2,rs1=14,funct3=7)
check(0xa005da50,rd=12,rs2=18,add=False)
check(0xa00ae2a8,rd=10,rs2=25,add=False)
result=dict(status='PASS',windows=len(windows),bytes=sum(b-a for a,b in windows),instructions=len(rows),raw_operand_checks=len(checks),profiles=[dict(procedure=p,evidence_id=r['evidence_id'],profile=r['analysis_profile']['digest']) for p,r in records.items()],helper_source=old['source'],checks=checks,instructions_detail=rows,limits=['Partial RV32 field decoder; not whole-instruction semantic validation or formal dataflow proof.','Only assigned caller-stage and selected helper modes reviewed. No execution or ad602 internal state-machine acceptance.'])
(OUT/'audit.json').write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
print(json.dumps({k:v for k,v in result.items() if k in ['status','windows','bytes','instructions','raw_operand_checks']}))
