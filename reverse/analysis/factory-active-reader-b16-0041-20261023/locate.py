from pathlib import Path
import json
from capstone import Cs,CS_ARCH_RISCV,CS_MODE_RISCV32,CS_MODE_RISCVC
src=Path('D:/Documents/PlatformIO/Projects/cuktech-ap01-firmware')
r=(src/'roms/0041/ap01-1.0.2_0041.bin').read_bytes();base=0x9ffff000
md=Cs(CS_ARCH_RISCV,CS_MODE_RISCV32|CS_MODE_RISCVC)
# One bounded static candidate localization, halfword positions only in ROM code lower bound.
# Match LUI 0x62fc9000 then within 64B an I/S encoding using same base +0x2b8.
rows=[]
for off in range(0,0x1bee24,2):
 w=int.from_bytes(r[off:off+4],'little')
 if w&127!=55 or w&0xfffff000!=0x62fc9000:continue
 rd=w>>7&31
 for q in range(off+4,min(off+68,0x1bee24),2):
  v=int.from_bytes(r[q:q+4],'little'); op=v&127
  if op in (3,19) and v>>15&31==rd and v>>20==0x2b8:
   rows.append({'lui':hex(base+off),'candidate':hex(base+q),'hex':r[q:q+4].hex(),'kind':'load' if op==3 else 'address','decode':[i.mnemonic+' '+i.op_str for i in md.disasm(r[q:q+4],base+q)]})
  if op==35 and v>>15&31==rd and ((v>>25<<5)|(v>>7&31))==0x2b8:
   rows.append({'lui':hex(base+off),'candidate':hex(base+q),'hex':r[q:q+4].hex(),'kind':'store','decode':[i.mnemonic+' '+i.op_str for i in md.disasm(r[q:q+4],base+q)]})
out={'scope':'halfword candidates file offsets [0,0x1bee24); LUI upper=0x62fc9000 + next64B exact I/S offset 0x2b8; candidates, not exhaustive xrefs; aliases, pointers, long-distance constructions and data excluded','candidates':rows}
Path('reverse/analysis/factory-active-reader-b16-0041-20261023/localization.json').write_text(json.dumps(out,indent=2)+'\n')
print(json.dumps(out,indent=2))
