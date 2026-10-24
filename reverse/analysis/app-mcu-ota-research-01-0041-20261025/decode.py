from pathlib import Path
import hashlib,json,struct
from capstone import Cs,CS_ARCH_RISCV,CS_MODE_RISCV32,CS_MODE_RISCVC
root=Path('D:/Documents/PlatformIO/Projects/cuktech-ap01-firmware')
out=Path(__file__).resolve().parent
rom=(root/'roms/0041/ap01-1.0.2_0041.bin').read_bytes(); base=0x9ffff000
assert len(rom)==6769704 and hashlib.sha256(rom).hexdigest()=='972db4c136c7ed9e24a83c07c1a7fd62040ca018b08ca285216d26b1fee3c6b9'
cs=Cs(CS_ARCH_RISCV,CS_MODE_RISCV32|CS_MODE_RISCVC)
wins=[(0xa006fbe8,1230),(0xa0074b22,114),(0xa007019e,88),(0xa00702a6,124),(0xa0070390,62),(0xa006faca,20)]
allrows=[];lines=[]
for start,n in wins:
 p=start; rows=[];lines.append('\nFUNCTION '+hex(start))
 while p<start+n:
  off=p-base; size=4 if rom[off]&3==3 else 2; raw=rom[off:off+size]; ins=next(cs.disasm(raw,p),None)
  asm=(ins.mnemonic+' '+ins.op_str) if ins and ins.size==size else 'UNKNOWN raw='+raw.hex()
  target=None
  if ins and ins.mnemonic in ('jal','c.j','c.jal','c.beqz','c.bnez','beq','bne','bge','bgeu','blt','bltu','beqz','bnez','blez','bgez','bltz','bgtz'):
   delta=int(ins.op_str.split(',')[-1].strip(),0);target=hex((p+delta)&0xffffffff)
  row={'address':hex(p),'offset':off,'raw':raw.hex(),'asm':asm,'target':target};rows.append(row)
  lines.append(f'{p:08x} {raw.hex():8s} {asm}'+(' => '+target if target else ''));p+=size
 assert p==start+n
 for a,b in zip(rows,rows[1:]):
  if a['asm'].startswith('auipc ra,') and b['asm'].startswith('jalr ra, ra,'):
   b['target']=hex((int(a['address'],16)+(int(a['asm'].split(',')[-1],0)<<12)+int(b['asm'].split(',')[-1],0))&0xffffffff)
 allrows.append({'start':hex(start),'size':n,'sha256':hashlib.sha256(rom[start-base:start-base+n]).hexdigest(),'instructions':rows})
table=rom[0xa01bb0e8-base:0xa01bb0e8-base+28]
(out/'raw.json').write_text(json.dumps({'rom_sha256':hashlib.sha256(rom).hexdigest(),'table_hex':table.hex(),'table_words':[hex(x) for x in struct.unpack('<7I',table)],'functions':allrows},indent=2))
(out/'disassembly.txt').write_text('\n'.join(lines))
print('\n'.join(lines))
