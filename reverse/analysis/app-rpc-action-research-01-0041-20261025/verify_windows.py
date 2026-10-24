"""Offline, bounded ROM-byte extraction; never executes target code."""
from pathlib import Path
import hashlib,json,sys
import capstone
out=Path(__file__).parent
rom=Path(sys.argv[1]).read_bytes()
assert len(rom)==6769704
assert hashlib.sha256(rom).hexdigest()=='972db4c136c7ed9e24a83c07c1a7fd62040ca018b08ca285216d26b1fee3c6b9'
expected=json.loads((out/'contract.json').read_text())
md=capstone.Cs(capstone.CS_ARCH_RISCV,capstone.CS_MODE_RISCV32|capstone.CS_MODE_RISCVC)
windows=[]; lines=[]; unknown=[]
for va,n in [(0xa00bec0c,676),(0xa00c5b8c,664),(0xa00bd924,20),(0xa00c0b5a,20),(0xa00bd7fa,278)]:
 raw=rom[va-0x9ffff000:va-0x9ffff000+n]
 windows.append(dict(va=hex(va),length=n,offset=va-0x9ffff000,sha256=hashlib.sha256(raw).hexdigest(),hex=raw.hex()))
 lines.append('\nWINDOW '+hex(va))
 p=0
 while p<n:
  ins=next(md.disasm(raw[p:],va+p,count=1),None)
  if ins:
   lines.append(f'{ins.address:08x} {ins.bytes.hex():10s} {ins.mnemonic:10s} {ins.op_str}');p+=ins.size
  else:
   unknown.append(va+p)
   size=4 if raw[p]&3==3 else 2
   lines.append(f'{va+p:08x} {raw[p:p+size].hex():10s} UNKNOWN');p+=size
 assert p==n
assert unknown==[0xa00c5d74]
assert [{k:v for k,v in w.items() if k!='hex'} for w in windows]==expected['windows']
(out/'windows.json').write_text(json.dumps(windows,indent=2)+'\n')
(out/'disassembly.txt').write_text('\n'.join(lines)+'\n')
print('\n'.join(lines))
print('PASS: 5 bounded windows, 1658 bytes, ROM identity verified')
