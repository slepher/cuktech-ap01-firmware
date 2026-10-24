from pathlib import Path
from capstone import *
import hashlib,json
rom=Path('D:/Documents/PlatformIO/Projects/cuktech-ap01-firmware/roms/0041/ap01-1.0.2_0041.bin').read_bytes()
assert len(rom)==6769704 and hashlib.sha256(rom).hexdigest()=='972db4c136c7ed9e24a83c07c1a7fd62040ca018b08ca285216d26b1fee3c6b9'
cs=Cs(CS_ARCH_RISCV,CS_MODE_RISCV32|CS_MODE_RISCVC)
rows=[]
for start,end in [(0xa00be6d8,0xa00be8a0),(0xa00ba8b2,0xa00ba994),(0xa00ba536,0xa00ba5be)]:
 pc=start
 while pc<end:
  o=pc-0x9ffff000;n=4 if rom[o]&3==3 else 2;raw=rom[o:o+n];i=next(cs.disasm(raw,pc),None)
  a=(i.mnemonic+' '+i.op_str) if i and i.size==n else 'RAW_UNKNOWN'
  row={'va':hex(pc),'offset':o,'hex':raw.hex(),'asm':a}
  if a.startswith('jal '): row['target']=hex(pc+int(a[4:],0))
  rows.append(row)
  print(hex(pc),raw.hex(),a)
  pc+=n
Path('reverse/analysis/app-serial-uplink-research-01-0041-20261025/instructions.json').write_text(json.dumps(rows,indent=2)+'\n')

strings={}
for v in [0xa0564aa8,0xa056549c,0xa05654a8,0xa056c058,0xa01c3280,0xa01c2488,0xa06124b8,0xa0610014,0xa06189f0]:
 o=v-0x9ffff000;strings[hex(v)]=rom[o:rom.find(b'\0',o)].decode('utf-8',errors='replace')
Path('reverse/analysis/app-serial-uplink-research-01-0041-20261025/strings.json').write_text(json.dumps(strings,indent=2)+'\n')
assert sum(len(bytes.fromhex(r['hex'])) for r in rows)==818
assert sum(r['asm']=='RAW_UNKNOWN' for r in rows)==1
