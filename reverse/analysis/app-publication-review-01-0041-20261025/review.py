import json
from pathlib import Path
from capstone import Cs, CS_ARCH_RISCV, CS_MODE_RISCV32, CS_MODE_RISCVC
root=Path('D:/Documents/PlatformIO/Projects/cuktech-ap01-firmware')
out=Path('reverse/analysis/app-publication-review-01-0041-20261025');out.mkdir(parents=True,exist_ok=True)
windows=[(0xa011c0da,298),(0xa0113340,92),(0xa0116b5a,202),(0xa0116db0,54),(0xa0116ad0,138)]
dec=Cs(CS_ARCH_RISCV,CS_MODE_RISCV32|CS_MODE_RISCVC)
old=json.loads((root/'reverse/analysis/app-publication-research-01-0041-20261025/raw.json').read_text())
checks=[]; listing=[]; decoded={}
with (root/'roms/0041/ap01-1.0.2_0041.bin').open('rb') as f:
 assert f.seek(0,2)==6769704
 for (va,size),prev in zip(windows,old['windows']):
  f.seek(va-0x9ffff000);buf=f.read(size);rows=list(dec.disasm(buf,va));assert sum(i.size for i in rows)==size
  assert buf.hex()==prev['raw']
  checks.append({'va':hex(va),'bytes':size,'instructions':len(rows),'author_raw_equal':True})
  print(hex(va))
  for i in rows:
   line=f'{i.address:08x} {i.bytes.hex():8} {i.mnemonic} {i.op_str}';print(line);listing.append(line);decoded[i.address]=bytes(i.bytes)
 f.seek(0xa06124b8-0x9ffff000);assert f.read(7)==b'result\0'
(out/'checks.json').write_text(json.dumps({'windows':checks,'bytes':784,'result_string':True,'target_execution':False},indent=2))
expected={0xa011c160:0xa0118a40,0xa011c1cc:0xa011f86c,0xa0113372:0xa011f9da,0xa0116b90:0xa0060cac,0xa0116bb6:0xa0061d20,0xa0116bec:0xa01b38b6,0xa0116c08:0xa0116ad0,0xa0116b36:0xa006929a,0xa0116b54:0xa002e14e}
for pc,target in expected.items():
 w=int.from_bytes(decoded[pc],'little');assert w&127==111
 imm=((w>>31)<<20)|(((w>>12)&255)<<12)|(((w>>20)&1)<<11)|(((w>>21)&1023)<<1)
 if imm&(1<<20):imm-=1<<21
 assert pc+imm==target
(out/'disassembly.txt').write_text('\n'.join(listing))
print('PASS: five ROM windows, 784 bytes, 279 instructions, 9 independently decoded JAL destinations, result string')
