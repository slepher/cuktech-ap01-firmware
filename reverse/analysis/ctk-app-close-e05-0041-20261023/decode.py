"""E05 ROM byte decoder, adapted from the reviewed E04 helper; executes no target code."""
import json
from pathlib import Path
from capstone import Cs, CS_ARCH_RISCV, CS_MODE_RISCV32, CS_MODE_RISCVC

HERE = Path(__file__).resolve().parent
ROOT = Path('D:/Documents/PlatformIO/Projects/cuktech-ap01-firmware')
ROM = ROOT / 'roms/0041/ap01-1.0.2_0041.bin'
BASE = 0x9ffff000
rom = ROM.read_bytes()
cs = Cs(CS_ARCH_RISCV, CS_MODE_RISCV32 | CS_MODE_RISCVC)
regs = 'zero ra sp gp tp t0 t1 t2 s0 s1 a0 a1 a2 a3 a4 a5 a6 a7 s2 s3 s4 s5 s6 s7 s8 s9 s10 s11 t3 t4 t5 t6'.split()

def signed(v, n):
    return v - (1 << n) if v & (1 << (n - 1)) else v

def custom(word):
    if word & 127 != 11:
        return None
    rd, rs1, rs2 = [regs[(word >> k) & 31] for k in (7, 15, 20)]
    f3, top, shift = (word >> 12) & 7, word >> 27, (word >> 25) & 3
    if f3 == 1 and top == 0:
        return f'th.addsl {rd},{rs1},{rs2},{shift}'
    if f3 == 1 and word >> 25 in (32,33):
        return f'th.{"mveqz" if word >> 25 == 32 else "mvnez"} {rd},{rs1},{rs2}'
    if f3 == 1 and word >> 26 == 4:
        return f'th.srri {rd},{rs1},{(word >> 20)&63}'
    if f3 == 2:
        return f'th.ext {rd},{rs1},{word >> 26},{(word >> 20)&63}'
    if f3 == 3:
        return f'th.extu {rd},{rs1},{word >> 26},{(word >> 20) & 63}'
    if f3 == 4 and top in (8, 16):
        return f'th.{"lrw" if top == 8 else "lrbu"} {rd},{rs1},{rs2},{shift}'
    if f3 == 5 and top == 8:
        return f'th.srw {rd},{rs1},{rs2},{shift}'
    raise AssertionError(hex(word))

def decode(start, end):
    rows = []
    pc = start
    while pc < end:
        pos = pc - BASE
        size = 4 if rom[pos] & 3 == 3 else 2
        raw = rom[pos:pos + size]
        if pc + size > end: break
        word = int.from_bytes(raw, 'little')
        ext = custom(word) if size == 4 else None
        ins = next(cs.disasm(raw, pc), None)
        assert ext or (ins and ins.size == size), hex(pc)
        row = dict(address=hex(pc), file_offset=pos, hex=raw.hex(), assembly=ext or (ins.mnemonic + ' ' + ins.op_str))
        if ext:
            row['fields'] = dict(rd=(word >> 7) & 31, rs1=(word >> 15) & 31, rs2=(word >> 20) & 31,
                                 funct3=(word >> 12) & 7, high5=word >> 27, shift=(word >> 25) & 3,
                                 msb=word >> 26, lsb=(word >> 20) & 63)
        if size == 4 and word & 127 == 111:
            imm = ((word >> 31) << 20) | (((word >> 12) & 255) << 12) | (((word >> 20) & 1) << 11) | (((word >> 21) & 1023) << 1)
            row['target'] = hex(pc + signed(imm, 21))
        elif size == 4 and word & 127 == 99:
            imm = ((word >> 31) << 12) | (((word >> 7) & 1) << 11) | (((word >> 25) & 63) << 5) | (((word >> 8) & 15) << 1)
            row['target'] = hex(pc + signed(imm, 13))
        elif size == 2:
            # Compressed branches/jumps are PC-relative; Capstone prints a displacement.
            if ins.mnemonic in ('c.j', 'c.jal', 'c.beqz', 'c.bnez'):
                delta = int(ins.op_str.split(',')[-1].strip(), 0)
                row['target'] = hex(pc + delta)
        rows.append(row)
        pc += size
    return rows


if __name__ == '__main__':
 import sys
 for r in decode(int(sys.argv[1],16),int(sys.argv[2],16)):
  print(r['address'],r['hex'],r['assembly'],r.get('target',''))
