from pathlib import Path
from capstone import *
import sys
raw=Path('D:/Documents/PlatformIO/Projects/cuktech-ap01-firmware/roms/0041/ap01-1.0.2_0041.bin').read_bytes(); base=0x9ffff000
cs=Cs(CS_ARCH_RISCV,CS_MODE_RISCV32|CS_MODE_RISCVC)
for arg in sys.argv[1:]:
 a,b=[int(x,16) for x in arg.split(':')];pc=a
 while pc<b:
  off=pc-base;sz=4 if raw[off]&3==3 else 2;v=raw[off:off+sz];ins=list(cs.disasm(v,pc))
  print(f'{pc:08x} {v.hex():8} '+(ins[0].mnemonic+' '+ins[0].op_str if ins else 'UNKNOWN'));pc+=sz
