"""P-19 independent, bounded ROM/retained-byte and RV32 field checks.

Standard library only. No author verifier, disassembler, ISA model or target execution.
"""
import json
from pathlib import Path
from datetime import datetime, timezone

ROOT = Path(__file__).resolve().parents[3]
HERE = Path(__file__).resolve().parent
BASE = 0x9ffff000
ROM = ROOT / 'roms/0041/ap01-1.0.2_0041.bin'
rom = ROM.read_bytes()
carrier = json.loads((ROOT / 'reverse/analysis/history-init-reset-p19-0041-20261024/static-evidence.json').read_text(encoding='utf8'))
parent = json.loads((ROOT / 'reverse/rehost/charge-complete-0041.json').read_text(encoding='utf8'))
checks = []

def check(label, value, expected):
    assert value == expected, (label, value, expected)
    checks.append(dict(label=label, actual=value, expected=expected))

def raw(pc, n=4):
    return int.from_bytes(rom[pc-BASE:pc-BASE+n], 'little')

def sx(x, n):
    return (x ^ (1 << (n-1))) - (1 << (n-1))

def i(pc):
    w = raw(pc)
    return [w & 127, (w >> 12) & 7, (w >> 7) & 31, (w >> 15) & 31, sx(w >> 20, 12)]

def s(pc):
    w = raw(pc)
    return [w & 127, (w >> 12) & 7, (w >> 15) & 31, (w >> 20) & 31, sx(((w >> 25) << 5) | ((w >> 7) & 31), 12)]

def jal(pc):
    w = raw(pc)
    check(hex(pc)+' JAL opcode', w & 127, 111)
    n = ((w >> 31) << 20) | (((w >> 12) & 255) << 12) | (((w >> 20) & 1) << 11) | (((w >> 21) & 1023) << 1)
    return (pc + sx(n,21)) & 0xffffffff

def pair(pc):
    a, b = raw(pc), raw(pc+4)
    check(hex(pc)+' AUIPC/JALR shape', [a & 127, (a >> 7) & 31, b & 127, (b >> 7) & 31, (b >> 15) & 31], [23,1,103,1,1])
    return (pc + (a & 0xfffff000) + sx(b >> 20,12)) & 0xffffffff

def cmem(pc):
    w = raw(pc,2)
    return [w & 3, w >> 13, 8+((w >> 7) & 7), 8+((w >> 2) & 7), (((w >> 10) & 7) << 3) | (((w >> 6) & 1) << 2) | (((w >> 5) & 1) << 6)]

def mv(pc):
    w = raw(pc,2)
    return [w & 3, w >> 12, (w >> 7) & 31, (w >> 2) & 31]

total = count = 0
for window in carrier['windows']:
    pc = int(window['start'],16)
    for row in window['instructions']:
        check('boundary '+row['address'], int(row['address'],16), pc)
        data = bytes.fromhex(row['hex'])
        check('ROM '+row['address'], rom[pc-BASE:pc-BASE+len(data)].hex(), row['hex'])
        check('length '+row['address'], len(data), 4 if raw(pc,2)&3 == 3 else 2)
        pc += len(data)
        total += len(data)
        count += 1
    check(window['name']+' end',pc,int(window['end_exclusive'],16))

for pc, expected in [(0xa01afde0,[19,0,10,0,108]),(0xa008e378,[3,2,11,8,-20]),(0xa00f1bb8,[3,2,9,18,4]),(0xa00f718c,[3,2,22,15,4])]:
    check(hex(pc)+' I fields',i(pc),expected)
for pc,expected in [(0xa01b0614,[35,2,23,15,0]),(0xa01b0618,[35,2,23,9,4]),(0xa01b0620,[35,2,18,23,16]),(0xa01b0266,[35,2,9,0,76]),(0xa00f1c14,[35,2,19,0,16])]:
    check(hex(pc)+' S fields',s(pc),expected)
for pc,expected in [(0xa01afdec,[2,8,9,10]),(0xa0080d96,[2,8,12,11]),(0xa00f1bee,[2,8,10,18])]:
    check(hex(pc)+' C.MV fields',mv(pc),expected)
for pc,expected in [(0xa01affa0,[0,6,9,10,60]),(0xa01b020c,[0,6,9,10,64]),(0xa01b0276,[0,6,9,10,88]),(0xa00f1bbc,[0,2,9,10,88]),(0xa00f7184,[0,2,10,15,16])]:
    check(hex(pc)+' C.memory fields',cmem(pc),expected)
for pc,target in [(0xa008e370,0xa002fcc8),(0xa008e37c,0xa0080d8e),(0xa0080d9a,0xa0024906),(0xa01b0208,0xa019c64e),(0xa01b0210,0xa019c82a),(0xa01b0218,0xa019c89e),(0xa00f6ecc,0xa01afd56),(0xa00f6f78,0xa01afd56),(0xa00f7024,0xa01afd56),(0xa00f70d0,0xa01afd56),(0xa00f71ae,0xa00ded6c),(0xa00f7180,0xa00dcee4),(0xa00f1bea,0xa008ae58),(0xa00f1c10,0xa008ab8a)]:
    check(hex(pc)+' target',jal(pc),target)
for pc,target in [(0xa01afde4,0xa008e362),(0xa01b026e,0xa008bc64),(0xa01b0278,0xa008bd16)]:
    check(hex(pc)+' pair target',pair(pc),target)
check('zero value argument',rom[0xa0080d98-BASE:0xa0080d9a-BASE].hex(),'8145')
check('Return selector c.li a4,12',rom[0xa00f7194-BASE:0xa00f7196-BASE].hex(),'3147')
w=raw(0xa00f7196)
imm=((w >> 31)<<12)|(((w>>7)&1)<<11)|(((w>>25)&63)<<5)|(((w>>8)&15)<<1)
check('Return branch opcode/funct3/rs1/rs2/target',[w&127,(w>>12)&7,(w>>15)&31,(w>>20)&31,0xa00f7196+sx(imm,13)],[99,0,15,14,0xa00f719e])
# DELETE stores are all word pointer clears, including no store at cursor +0x60.
stores=[]
for pc in range(0xa00f1bbe,0xa00f1c10,4):
    if raw(pc)&127 == 35:
        fields=s(pc)
        check(hex(pc)+' delete P clear shape',fields[:4],[35,2,9,0])
        stores.append(fields[4])
check('DELETE cursor not among bounded stores',96 in stores,False)
continuation={int(r['address'],16):r for r in parent['creator_continuations'][2]['instructions']}
check('chart store retained bytes',continuation[0xa01affa0]['bytes'],rom[0xa01affa0-BASE:0xa01affa2-BASE].hex())
out=dict(utc=datetime.now(timezone.utc).isoformat(),rom=str(ROM),mapping_base=hex(BASE),inherited_sha256='972db4c136c7ed9e24a83c07c1a7fd62040ca018b08ca285216d26b1fee3c6b9',windows=len(carrier['windows']),bytes_compared=total,instructions=count,checks=checks,limitations='Byte identity and selected independent standard-ISA fields only; no target/model execution, no generic custom-opcode semantics, no whole-ROM absence proof.')
(HERE/'independent-checks.json').write_text(json.dumps(out,ensure_ascii=False,indent=2)+'\n',encoding='utf8')
print(len(checks),'PASS;',total,'bytes;',count,'instruction boundaries')
