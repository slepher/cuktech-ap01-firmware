import json,hashlib
from pathlib import Path
from capstone import *
root=Path('D:/Documents/PlatformIO/Projects/cuktech-ap01-firmware')
author=Path('D:/CodexHome/visualizations/2026/10/24/01a16ec4-7aa8-7b43-a0e8-609e1021781b/ap01-s/report-config01/reverse/analysis/app-report-config-research-01-0041-20261025')
if (root/'reverse/analysis/app-report-config-research-01-0041-20261025/static-windows.json').exists():
 author=root/'reverse/analysis/app-report-config-research-01-0041-20261025'
b=(root/'roms/0041/ap01-1.0.2_0041.bin').read_bytes()
assert len(b)==6769704 and hashlib.sha256(b).hexdigest()=='972db4c136c7ed9e24a83c07c1a7fd62040ca018b08ca285216d26b1fee3c6b9'
ref=json.loads((author/'static-windows.json').read_text())
md=Cs(CS_ARCH_RISCV,CS_MODE_RISCV32|CS_MODE_RISCVC)
result=[]
for start,n in [(0xa00c6198,464),(0xa00c607e,282),(0xa00c0b82,20),(0xa00c0b6e,20)]:
 raw=b[start-0x9ffff000:start-0x9ffff000+n]
 rr=next(w for w in ref['windows'] if int(w['start'],16)==start)
 assert raw.hex()==rr['raw'] and hashlib.sha256(raw).hexdigest()==rr['sha256']
 lines=[]
 for i in md.disasm(raw,start):
  s=f'{i.address:08x} {i.bytes.hex():8} {i.mnemonic} {i.op_str}'
  if i.mnemonic in ['jal','c.j','c.beqz','c.bnez','beq','bne','blt','bge','bltu','bgeu']:
   s+=f' => {i.address+int(i.op_str.split(",")[-1].strip(),0):08x}'
  lines.append(s)
 assert sum(i.size for i in md.disasm(raw,start))==n
 print('\n'.join(lines))
 result.append(dict(start=hex(start),length=n,sha256=hashlib.sha256(raw).hexdigest(),raw=raw.hex(),instructions=lines,author_bytes_equal=True))
roots=json.loads((author/'inherited-roots.json').read_text())
print('ROOT KEYS', [list(r) for r in roots])
Path(__file__).with_name('independent-windows.json').write_text(json.dumps(result,indent=2))
