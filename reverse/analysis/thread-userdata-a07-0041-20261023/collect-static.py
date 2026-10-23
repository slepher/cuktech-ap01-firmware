"""A07 bounded original-ROM evidence; no firmware execution or shared REA state."""
import json
from pathlib import Path
from capstone import Cs, CS_ARCH_RISCV, CS_MODE_RISCV32, CS_MODE_RISCVC, __version__
HERE = Path(__file__).resolve().parent
ROM = Path('D:/Documents/PlatformIO/Projects/cuktech-ap01-firmware/roms/0041/ap01-1.0.2_0041.bin')
BASE = 0x9ffff000
raw = ROM.read_bytes()
md = Cs(CS_ARCH_RISCV, CS_MODE_RISCV32 | CS_MODE_RISCVC)
checks = []
def s(v, n): return (v ^ (1 << (n-1))) - (1 << (n-1))
def u(pc, n=4): return int.from_bytes(raw[pc-BASE:pc-BASE+n], 'little')
def check(pc, kind, actual, expected):
    assert actual == expected, (hex(pc), kind, actual, expected)
    checks.append(dict(pc=hex(pc), kind=kind, actual=actual, expected=expected))
def mv(pc, rd, rs):
    w = u(pc, 2)
    check(pc, 'C.MV fields', [w & 0xf003, w >> 7 & 31, w >> 2 & 31], [0x8002, rd, rs])
def mem(pc, store, reg, base, off, width=2):
    w = u(pc)
    imm = s(((w >> 25) << 5) | (w >> 7 & 31), 12) if store else s(w >> 20, 12)
    check(pc, 'store/load fields', [w & 127, w >> 12 & 7, w >> 15 & 31, w >> (20 if store else 7) & 31, imm], [0x23 if store else 3, width, base, reg, off])
def addi(pc, rd, rs, imm):
    w = u(pc)
    check(pc, 'ADDI fields', [w & 0x707f, w >> 7 & 31, w >> 15 & 31, s(w >> 20, 12)], [0x13, rd, rs, imm])
def call(pc, target, paired=True):
    w = u(pc)
    if paired:
        v = u(pc+4)
        check(pc, 'AUIPC/JALR call fields', [w & 0xfff, v & 0xfffff], [0x97, 0x80e7])
        actual = (pc + s(w & 0xfffff000, 32) + s(v >> 20, 12)) & 0xffffffff
    else:
        check(pc, 'JAL ra fields', w & 0xfff, 0xef)
        imm = (w >> 31 << 20) | ((w >> 12 & 255) << 12) | ((w >> 20 & 1) << 11) | ((w >> 21 & 1023) << 1)
        actual = (pc + s(imm, 21)) & 0xffffffff
    check(pc, 'direct call target', hex(actual), hex(target))
def window(lo, hi):
    start = lo; out = []
    while lo < hi:
        b = raw[lo-BASE:lo-BASE+4]; i = next(md.disasm(b, lo, 1), None)
        n = i.size if i else (4 if b[0] & 3 == 3 else 2)
        out.append(dict(pc=hex(lo), bytes=b[:n].hex(), asm=i.mnemonic+' '+i.op_str if i else 'UNKNOWN; no vendor semantics assigned'))
        lo += n
    assert lo == hi
    return dict(start=hex(start), end_exclusive=hex(hi), instructions=out)
windows = [window(0xa0197f02, 0xa0197fa8), window(0xa0052fee, 0xa0053252)]
for args in [(0xa0197f12,19,11),(0xa0197f18,20,10),(0xa0197f1a,18,12),(0xa0197f54,12,18),(0xa0197f5a,13,14),(0xa0197f5c,9,10),(0xa0197f66,18,10),(0xa0197f9c,11,19),(0xa005300a,18,11),(0xa0053010,22,10),(0xa0053012,25,12),(0xa0053022,23,13),(0xa0053106,13,25)]: mv(*args)
for args in [(0xa0197f26,True,13,8,-56),(0xa0197f2a,True,14,8,-52),(0xa0197f36,False,13,8,-56),(0xa0197f3e,True,13,8,-36),(0xa0197f42,True,15,8,-41,0),(0xa0197f50,False,14,8,-52),(0xa0197f98,True,9,20,0),(0xa0053132,True,15,9,304),(0xa0053136,True,23,9,308)]: mem(*args)
for args in [(0xa0197f22,10,8,-44),(0xa0197f56,11,8,-44),(0xa0053108,12,12,-1722),(0xa005312e,15,15,-596)]: addi(*args)
for pc,target in [(0xa0197f2e,0xa000589c),(0xa0197f46,0xa002fcc8),(0xa0197f5e,0xa0052fee),(0xa0197f6c,0xa002e14e),(0xa0197f7c,0xa0024906)]: call(pc,target)
call(0xa0197f9e, 0xa01a9038, False)
call(0xa005310e, 0xa0030ef8, False)
check(0xa0053100, 'LUI entry adapter', u(0xa0053100), 0xa0130637)
check(0xa0053126, 'LUI callback base', u(0xa0053126), 0xa00527b7)
# Independently check the two compact zero branches and terminal jumps of wrapper.
def cb(pc, target):
    w=u(pc,2); imm=((w>>12&1)<<8)|((w>>10&3)<<3)|((w>>5&3)<<6)|((w>>3&3)<<1)|((w>>2&1)<<5)
    check(pc,'C.BEQZ a0', [w&0xe003,(w>>7&7)+8,hex((pc+s(imm,9))&0xffffffff)], [0xc001,10,hex(target)])
cb(0xa0197f4e,0xa0197fa4); cb(0xa0197f68,0xa0197f96)
result = dict(task='A07', capstone=__version__, method='bounded original-ROM reads and independent instruction fields; no target execution', windows=windows, checks=checks,
    inventory_source='evidence/rea-0041-20261017/evidence/final-seeded-roots-205.json; ghidra-function-manager body ranges 0xa0197f02..0xa0197fa7 and 0xa0052fee..0xa0053251',
    limits=['a0052fee lower thread/adapter bodies not expanded', 'Three vendor words preserved without assigning semantics', 'Final consumer a0 and actual launch/scheduling remain unproven', 'No buzzer exited_sem link'])
(HERE/'instruction-evidence.json').write_text(json.dumps(result,indent=2)+'\n',encoding='utf8')
print('PASS',len(checks),'checks;',sum(len(w['instructions']) for w in windows),'instruction slots;',sum(int(w['end_exclusive'],16)-int(w['start'],16) for w in windows),'bytes')
