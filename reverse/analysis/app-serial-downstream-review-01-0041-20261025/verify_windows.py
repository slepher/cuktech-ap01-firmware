from pathlib import Path
import hashlib,json,re,struct
from capstone import Cs,CS_ARCH_RISCV,CS_MODE_RISCV32,CS_MODE_RISCVC
ROOT=Path(r'D:/Documents/PlatformIO/Projects/cuktech-ap01-firmware')
AUTHOR=Path(r'D:/CodexHome/visualizations/2026/10/24/01a16ec4-7aa8-7b43-a0e8-609e1021781b/ap01-s/serial-downstream01/reverse/analysis/app-serial-downstream-research-01-0041-20261025')
OUT=Path(__file__).parent
rom=(ROOT/'roms/0041/ap01-1.0.2_0041.bin').read_bytes()
assert len(rom)==6769704 and hashlib.sha256(rom).hexdigest()=='972db4c136c7ed9e24a83c07c1a7fd62040ca018b08ca285216d26b1fee3c6b9'
md=Cs(CS_ARCH_RISCV,CS_MODE_RISCV32|CS_MODE_RISCVC)
rows=[]; listing=[]
for w in json.loads((AUTHOR/'windows.json').read_text()):
 va=int(w['va'],16); off=va-0x9ffff000; raw=rom[off:off+w['length']]
 assert off==w['offset'] and raw.hex()==w['hex'] and hashlib.sha256(raw).hexdigest()==w['sha256']
 ins=list(md.disasm(raw,va)); assert sum(i.size for i in ins)==len(raw)
 rows.append(dict(va=w['va'],offset=off,length=len(raw),sha256=hashlib.sha256(raw).hexdigest(),instructions=len(ins),undecoded_bytes=0))
 listing += [f'{i.address:08x} {i.bytes.hex():10} {i.mnemonic} {i.op_str}' for i in ins]
refs=json.loads((AUTHOR/'referenced-data.json').read_text())
for addr,s in refs['strings'].items():
 off=int(addr,16)-0x9ffff000
 assert rom[off:off+len(s)+1]==s.encode()+b'\0'
for row in refs['dispatch']:
 off=int(row['va'],16)-0x9ffff000
 assert list(struct.unpack('<5I',rom[off:off+20]))==[int(x,16) for x in row['words']]
 ptr=int(row['words'][0],16)-0x9ffff000; s=row['method'].encode()
 assert rom[ptr:ptr+len(s)+1]==s+b'\0'
(OUT/'independent-disassembly.txt').write_text('\n'.join(listing)+'\n')
result=dict(claim='Q-30',author_commit='138119aece4883d73f0af4c1f9045f3fa5b198d5',review_baseline='5a5b732235c5b0d1654c8bc543b92c9cc5331e0b',rom_length=len(rom),rom_sha256=hashlib.sha256(rom).hexdigest(),windows=rows,total_bytes=sum(w['length'] for w in rows),string_checks=len(refs['strings']),dispatch_entries=len(refs['dispatch']),execution='static only',conclusion='bounded stage accepted; no behavior correction; no new body')
(OUT/'contract.json').write_text(json.dumps(result,indent=2)+'\n')
print(json.dumps(result))
