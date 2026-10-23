"""G08 independent passive checks. No export or execution of target code."""
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
OUT = Path(__file__).resolve().parent
ROM = Path('D:/Documents/PlatformIO/Projects/cuktech-ap01-firmware/roms/0041/ap01-1.0.2_0041.bin').read_bytes()
BASE = 0x9ffff000
source = ROOT / 'reverse/analysis/display-alternate-work-g07-0041-20261023/evidence.json'
prior = json.loads(source.read_text(encoding='utf-8'))
checks = []

def word(a, n=4):
    return int.from_bytes(ROM[a-BASE:a-BASE+n], 'little')

def sx(v, n):
    return v - (1 << n) if v & (1 << (n-1)) else v

def expect(label, actual, expected):
    assert actual == expected, (label, actual, expected)
    checks.append({'claim': label, 'result': 'accepted'})

# Compare retained raw in place; do not produce a second instruction export.
rows = 0
for w in prior['windows']:
    pc = int(w['start'], 16)
    for r in w['rows']:
        assert int(r['pc'],16) == pc
        b = bytes.fromhex(r['raw'])
        assert ROM[pc-BASE:pc-BASE+len(b)] == b
        pc += len(b)
        rows += 1
    assert pc == int(w['end'],16)

def I(a, op, rd, rs1, imm, f3=0):
    x = word(a)
    expect(hex(a)+' I fields', (x&127,(x>>7)&31,(x>>15)&31,sx(x>>20,12),(x>>12)&7), (op,rd,rs1,imm,f3))

def S(a, rs1, rs2, imm, f3):
    x=word(a)
    expect(hex(a)+' S fields', (x&127,(x>>15)&31,(x>>20)&31,sx(((x>>25)<<5)|((x>>7)&31),12),(x>>12)&7), (0x23,rs1,rs2,imm,f3))

def raw16(a, v):
    expect(hex(a)+' compressed encoding', word(a,2), v)

def jal(a, target):
    x=word(a)
    off=sx(((x>>31)<<20)|(((x>>12)&255)<<12)|(((x>>20)&1)<<11)|(((x>>21)&1023)<<1),21)
    expect(hex(a)+' JAL target', (x&127,(a+off)&0xffffffff), (0x6f,target))

def pair(a, target):
    u,v=word(a),word(a+4)
    expect(hex(a)+' AUIPC/JALR', (u&127,v&127,(u>>7)&31,(v>>15)&31, (a+sx(u&0xfffff000,32)+sx(v>>20,12))&0xffffffff), (0x17,0x67,1,1,target))

# Explicit argument aliases supplement the prior window's register names only.
I(0xa009e50e,0x13,20,11,0x34)
raw16(0xa009e524,0x89aa)  # mv s3,a0 = loop
raw16(0xa009e526,0x8932)  # mv s2,a2 = fd
raw16(0xa009e528,0x8aae)  # mv s5,a1 = poll
I(0xa0083376,3,22,10,0,2)
I(0xa008337a,3,19,10,4,2)
raw16(0xa008342e,0x84ae)  # state saved before getter
jal(0xa0083430,0xa007fe32)
raw16(0xa0083434,0x411c)  # lw a5,0(a0)
raw16(0xa0083436,0xccbc)  # sw a5,0x58(s1)
S(0xa009e5fc,21,15,8,0)
S(0xa009e600,21,15,0x2c,2)
S(0xa009e604,21,19,4,2)
I(0xa009e628,0x13,11,11,-0x716)
expect('watcher callback constant', (word(0xa009e614)&0xfffff000)-0x716, 0xa009f8ea)
raw16(0xa009cd86,0xc10c)
raw16(0xa009cd88,0xd150)

# G05 identity and exact refresh order remain inherited; verify selected bytes.
raw16(0xa00834a4,0xd0a4)
I(0xa00834da,0x13,23,9,0x58)
raw16(0xa0080718,0x0521)
S(0xa008070e,10,15,4,0)
raw16(0xa00806da,0x4104)
pair(0xa00806dc,0xa01b2cb0)
raw16(0xa00806e4,0x4501)
jal(0xa00806e6,0xa00e0ac8)
S(0xa00806ea,9,0,0x5c,0)

# Callback publication is after backend registration, with preserved pointer.
raw16(0xa009f9da,0x8932)
jal(0xa009f9e2,0xa009f972)
I(0xa009f9e6,3,11,8,-0x14,2)
I(0xa009f9fa,0x13,11,9,0x34)
jal(0xa009f9fe,0xa009ec98)
S(0xa009fa1c,9,18,0x30,2)
I(0xa009f8fe,0x13,18,11,-0x34)
I(0xa009f964,3,14,9,-4,2)
raw16(0xa009f96a,0x4581)
raw16(0xa009f96c,0x854a)
raw16(0xa009f96e,0x9702)
pair(0xa01b2cd4,0xa009f972)
I(0xa009f97e,0x13,11,10,0x34)
raw16(0xa009f984,0x465d)
jal(0xa009f986,0xa009f442)
I(0xa009f992,0x13,14,15,-5,7)
raw16(0xa009f9a4,0x4cac)
jal(0xa009f9a8,0xa009e212)

# Owner return: word decrement, signed >0 branch, original owner as free arg.
raw16(0xa007ff5e,0x4104)
I(0xa007ff60,3,15,9,0x180,2)
raw16(0xa007ff64,0x17fd)
S(0xa007ff66,9,15,0x180,2)
x=word(0xa007ff6a)
off=sx(((x>>31)<<12)|(((x>>7)&1)<<11)|(((x>>25)&63)<<5)|(((x>>8)&15)<<1),13)
expect('owner signed branch', (x&127,(x>>12)&7,(x>>15)&31,(x>>20)&31,off),(0x63,4,0,15,0x2c))
raw16(0xa007ff90,0x8526)
jal(0xa007ff92,0xa008ab8a)

result={'classification':'independent review; old conclusions rechecked; new functionality 0',
        'inherited_evidence':str(source.relative_to(ROOT)), 'retained_rows_matched':rows,
        'checks':checks,
        'limits':['backend ready dispatch not expanded','post-exit drain not proved','all owner counter writers not enumerated','no whole-function export; no target execution']}
(OUT/'review-result.json').write_text(json.dumps(result,ensure_ascii=False,indent=2),encoding='utf-8')
print('PASS',rows,'retained rows matched;',rows+len(checks),'checks; new functionality 0')
