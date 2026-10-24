"""Independent bounded static review; does not execute firmware or author scripts."""
import argparse, hashlib, json, struct
from pathlib import Path
import capstone
p=argparse.ArgumentParser(); p.add_argument('--source-root',type=Path,required=True); a=p.parse_args()
b=(a.source_root/'roms/0041/ap01-1.0.2_0041.bin').read_bytes()
assert len(b)==6769704 and hashlib.sha256(b).hexdigest()=='972db4c136c7ed9e24a83c07c1a7fd62040ca018b08ca285216d26b1fee3c6b9'
def get(v,n): return b[v-0x9ffff000:v-0x9ffff000+n]
windows=[(0xa012193c,1158),(0xa0113a76,54),(0xa0113aac,162),(0xa0113b4e,92),(0xa0115702,252),(0xa010f9f8,228),(0xa011398a,236)]
assert sum(n for _,n in windows)==2182
assert struct.unpack('<6I',get(0xa060fd34,24))==(0xa0113a76,0,0xa0113aac,0xa0113b4e,0xa0115702,0xa010f9f8)
md=capstone.Cs(capstone.CS_ARCH_RISCV,capstone.CS_MODE_RISCV32|capstone.CS_MODE_RISCVC)
vendor={0xa0121bc4:'8b17d740',0xa0121c5a:'8b19fb40',0xa0121cb2:'0bd04701',0xa0121cce:'0bd07701',0xa0121ce6:'0bd03701'}
lines=[]; allbytes={}
for va,n in windows:
 raw=get(va,n); pos=0; lines.append('\nWINDOW '+hex(va)+' '+str(n))
 while pos<n:
  addr=va+pos
  if addr in vendor:
   chunk=raw[pos:pos+4]; assert chunk.hex()==vendor[addr]; desc='VENDOR preserved; see existing SINC separately'
  else:
   ins=next(md.disasm(raw[pos:],addr,count=1),None); assert ins is not None,hex(addr)
   chunk=bytes(ins.bytes); desc=ins.mnemonic+' '+ins.op_str
  assert pos+len(chunk)<=n
  allbytes[addr]=chunk.hex(); lines.append(f'{addr:08x} {chunk.hex():10s} {desc}'); pos+=len(chunk)
 assert pos==n
out=Path(__file__).parent/'independent-disassembly.txt'; out.write_text('\n'.join(lines)+'\n',encoding='utf-8')
# Compare author saved raw bytes only after independent collection, never execute author source.
author=json.loads((a.source_root/'reverse/analysis/app-ota-research-03-0041-20261025/raw-windows.json').read_text())
assert [(int(w['address'],16),w['length']) for w in author['windows']]==windows
for w in author['windows']: assert get(int(w['address'],16),w['length']).hex()==w['hex']
sinc=(a.source_root/'evidence/rea-0041-20261017/ghidra/Ghidra/Processors/RISCV/data/languages/ap01thead2.sinc').read_text()
for key in [':th.mveqz rd,rs1,rs2 is op0006=0xb & op1214=1 & op2531=32',':th.srb rd,rs1,rs2,thshift is op0006=0xb & op1214=5 & op2731=0','if (rs2 != 0) goto <done>;','*[ram]:1 ea = rd:1;']: assert key in sinc
for va,h in vendor.items():
 w=int.from_bytes(get(va,4),'little'); fields=(w&127,(w>>12)&7,(w>>25)&127,(w>>7)&31,(w>>15)&31,(w>>20)&31)
 lines.append(hex(va)+' vendor fields '+str(fields))
print('\n'.join(lines)); print('PASS bounded original-byte coverage/table/author raw identity; SINC is historical model evidence only.')
