from pathlib import Path
import hashlib,json,sys,capstone
out=Path(__file__).parent
rom=Path(sys.argv[1]).read_bytes()
assert len(rom)==6769704
assert hashlib.sha256(rom).hexdigest()=='972db4c136c7ed9e24a83c07c1a7fd62040ca018b08ca285216d26b1fee3c6b9'
md=capstone.Cs(capstone.CS_ARCH_RISCV,capstone.CS_MODE_RISCV32|capstone.CS_MODE_RISCVC)
windows=[]; lines=[]; unknown=[]
for va,n in [(0xa00bdb74,1064),(0xa00ba712,174),(0xa00ba4b4,130),(0xa00ba7c0,242)]:
 raw=rom[va-0x9ffff000:va-0x9ffff000+n]
 windows.append(dict(va=hex(va),length=n,offset=va-0x9ffff000,sha256=hashlib.sha256(raw).hexdigest(),hex=raw.hex()))
 lines.append('\nWINDOW '+hex(va)); p=0
 while p<n:
  ins=next(md.disasm(raw[p:],va+p,count=1),None)
  if ins:
   lines.append(f'{ins.address:08x} {ins.bytes.hex():10s} {ins.mnemonic:10s} {ins.op_str}');p+=ins.size
  else:
   unknown.append(hex(va+p)); size=4 if raw[p]&3==3 else 2
   lines.append(f'{va+p:08x} {raw[p:p+size].hex():10s} UNKNOWN');p+=size
 assert p==n
(out/'windows.json').write_text(json.dumps(windows,indent=2)+'\n')
(out/'disassembly.txt').write_text('\n'.join(lines)+'\n')
print('\n'.join(lines));print('unknown',unknown)
