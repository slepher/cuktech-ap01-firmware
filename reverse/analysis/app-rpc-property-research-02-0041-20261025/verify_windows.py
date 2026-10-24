"""Read and decode only Q29's five authorized static ROM windows."""
import argparse, hashlib, json
from pathlib import Path
import capstone
p=argparse.ArgumentParser();p.add_argument('rom',type=Path);a=p.parse_args()
b=a.rom.read_bytes();assert len(b)==6769704
md=capstone.Cs(capstone.CS_ARCH_RISCV,capstone.CS_MODE_RISCV32|capstone.CS_MODE_RISCVC)
windows=[];lines=[]
for va,n in [(0xa00beeb0,468),(0xa00c59d4,440),(0xa00bb0f6,26),(0xa00c0478,26),(0xa00bb80e,114)]:
 raw=b[va-0x9ffff000:va-0x9ffff000+n];pos=0;unknown=[];out=[]
 while pos<n:
  ins=next(md.disasm(raw[pos:],va+pos,count=1),None)
  if ins: size=ins.size;desc=ins.mnemonic+' '+ins.op_str
  else: size=4 if raw[pos]&3==3 else 2;desc='UNDECODED';unknown.append(hex(va+pos))
  
  if ins and ins.mnemonic == 'jal': desc += f' ; target={va+pos+int(ins.op_str,0):#x}'
  out.append(f'{va+pos:08x} {raw[pos:pos+size].hex():8} {desc}');pos+=size
 assert pos==n
 windows.append(dict(va=hex(va),offset=va-0x9ffff000,length=n,hex=raw.hex(),sha256=hashlib.sha256(raw).hexdigest(),unknown=unknown))
 lines.extend([f'\nWINDOW {va:x} {n} B']+out)
assert {u for w in windows for u in w['unknown']} == {'0xa00bef08','0xa00bef26','0xa00bef44','0xa00bef62','0xa00bef84'}
r=Path(__file__).parent
(r/'windows.json').write_text(json.dumps(windows,indent=2)+'\n')
assert all(x in '\n'.join(lines) for x in ['target=0xa0191d52','target=0xa01adc0e','target=0xa00bb6da','target=0xa01afb26','target=0xa00602e6','target=0xa00b55a0','target=0xa00b5636'])
(r/'windows.txt').write_text('\n'.join(lines)+'\n')
print('PASS: five windows, 1074 bytes, full instruction-width coverage')
