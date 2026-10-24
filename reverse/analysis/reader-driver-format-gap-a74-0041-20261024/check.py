"""A74: bounded static field checks only; never executes/emulates firmware."""
import json
from pathlib import Path
from capstone import Cs, CS_ARCH_RISCV, CS_MODE_RISCV32, CS_MODE_RISCVC

MAIN = Path('D:/Documents/PlatformIO/Projects/cuktech-ap01-firmware')
OUT = Path(__file__).resolve().parent
START = 0xa0053252
with (MAIN / 'roms/0041/ap01-1.0.2_0041.bin').open('rb') as f:
    f.seek(START - 0x9ffff000)
    raw = f.read(120)
assert len(raw) == 120
md = Cs(CS_ARCH_RISCV, CS_MODE_RISCV32 | CS_MODE_RISCVC)
rows = [{'va': hex(i.address), 'bytes': i.bytes.hex(), 'asm': i.mnemonic + ' ' + i.op_str}
        for i in md.disasm(raw, START)]
assert sum(len(bytes.fromhex(r['bytes'])) for r in rows) == 120
checks = []
def check(label, actual, expected):
    assert actual == expected, (label, actual, expected)
    checks.append({'label': label, 'actual': actual})
def word(va):
    return int.from_bytes(raw[va-START:va-START+4], 'little')
def sx(n, bits):
    return n - (1 << bits) if n & (1 << (bits-1)) else n
def i_fields(va):
    w = word(va)
    return (w & 127, (w >> 7) & 31, (w >> 12) & 7, (w >> 15) & 31, sx(w >> 20, 12))
def store_fields(va):
    w = word(va)
    return (w & 127, (w >> 12) & 7, (w >> 15) & 31, (w >> 20) & 31,
            sx(((w >> 25) << 5) | ((w >> 7) & 31), 12))
for va, rd, rs1, imm in [(0xa0053262,15,15,-0xd2),(0xa005326c,16,16,0x536),
                         (0xa0053278,16,16,0x4d8),(0xa0053296,10,8,-0x28),
                         (0xa00532ac,14,14,0x554),(0xa00532b8,14,14,0x578)]:
    check(hex(va)+' I fields', i_fields(va), (19,rd,0,rs1,imm))
for va, rs2, imm in [(0xa0053270,16,-0x24),(0xa005327e,16,-0x20),
                     (0xa0053282,15,-0x1c),(0xa0053286,0,-0x28),
                     (0xa005328a,10,-0x18),(0xa005328e,14,-0x14),
                     (0xa00532b0,14,-0x24),(0xa00532bc,14,-0x20),
                     (0xa00532c0,15,-0x1c),(0xa00532c4,0,-0x28)]:
    check(hex(va)+' SW fields', store_fields(va), (35,2,8,rs2,imm))
check('initial output byte store', store_fields(0xa0053292), (35,0,10,0,0))
for va, rd, high in [(0xa005325c,15,0xa002b000),(0xa0053268,16,0xa002b000),
                     (0xa0053274,16,0xa002b000),(0xa00532a8,14,0xa002b000),
                     (0xa00532b4,14,0xa002b000)]:
    w=word(va)
    check(hex(va)+' U fields', (w&127,(w>>7)&31,w&0xfffff000), (55,rd,high))
w = word(0xa005329c)
off = sx(((w >> 31) << 20) | (((w >> 12) & 255) << 12) |
         (((w >> 20) & 1) << 11) | (((w >> 21) & 1023) << 1),21)
check('direct JAL', (w&127,(w>>7)&31,hex(0xa005329c+off)), (111,1,'0xa002d770'))
for va, hx in [(0xa005325a,'2e87'),(0xa0053260,'b285'),(0xa005327c,'7d17'),
               (0xa005329a,'3686'),(0xa00532a6,'8280')]:
    check(hex(va)+' compressed anchor', raw[va-START:va-START+2].hex(), hx)
h=int.from_bytes(raw[0xa0053266-START:0xa0053268-START], 'little')
boff=sx(((h>>12)&1)<<8 | ((h>>10)&3)<<3 | ((h>>5)&3)<<6 |
         ((h>>3)&3)<<1 | ((h>>2)&1)<<5,9)
check('count zero branch', ((h>>13)&7,8+((h>>7)&7),hex(0xa0053266+boff)), (6,14,'0xa00532a8'))
h=int.from_bytes(raw[-2:], 'little')
joff=sx(((h>>12)&1)<<11 | ((h>>11)&1)<<4 | ((h>>9)&3)<<8 |
         ((h>>8)&1)<<10 | ((h>>7)&1)<<6 | ((h>>6)&1)<<7 |
         ((h>>3)&7)<<1 | ((h>>2)&1)<<5,12)
check('zero count join', ((h>>13)&7,hex(0xa00532c8+joff)), (5,'0xa0053296'))
parent = json.loads((MAIN / 'evidence/rea-0041-20261017/evidence/upper-complete.evidence.json').read_text(encoding='utf-8'))
r = next(x for x in parent['records'] if x.get('evidence_id') == 'ev_2fc7174be7213a9616dc6d46d18c0831acd1c06324cba526633b36c29ab2f22e')
asm = r['normalized_result']['assembly']
check('retained adapter complete lines', len(asm), 14)
for n, value in [(4,'0xa002d778: c.mv a3, a1'),(5,'0xa002d77a: c.mv a4, a2'),
                 (6,'0xa002d77c: c.li a1, 0x0'),(7,'0xa002d77e: c.li a2, 0x0'),
                 (8,'0xa002d780: auipc ra, 0x176'),(9,'0xa002d784: jalr ra, ra, 0x52'),
                 (13,'0xa002d78e: ret')]:
    check('old assembly '+str(n),asm[n],value)
check('old AUIPC/JALR target arithmetic',hex(0xa002d780+(0x176<<12)+0x52),'0xa01a37d2')
OUT.mkdir(parents=True, exist_ok=True)
(OUT/'evidence.json').write_text(json.dumps({'range':['0xa0053252','0xa00532ca'],
    'new_bytes':120,'decoder':'capstone RV32/RVC','instructions':rows,
    'retained_d770':{'eid':r['evidence_id'],'profile':r['analysis_profile']['digest'],'assembly':asm},
    'checks':checks,'check_count':len(checks)},indent=2)+'\n',encoding='utf-8')
print('A74 static checks:',len(checks),'new bytes: 120; no execution/emulation')
