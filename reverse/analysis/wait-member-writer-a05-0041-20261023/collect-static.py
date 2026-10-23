"""A05 original ROM static evidence only; target instructions are not executed."""
import json
from pathlib import Path
from capstone import Cs, CS_ARCH_RISCV, CS_MODE_RISCV32, CS_MODE_RISCVC, __version__
HERE=Path(__file__).resolve().parent
ROM=Path('D:/Documents/PlatformIO/Projects/cuktech-ap01-firmware/roms/0041/ap01-1.0.2_0041.bin')
BASE=0x9ffff000
raw=ROM.read_bytes(); md=Cs(CS_ARCH_RISCV,CS_MODE_RISCV32|CS_MODE_RISCVC)
def u32(pc): return int.from_bytes(raw[pc-BASE:pc-BASE+4],'little')
def signed(n,b): return (n^(1<<(b-1)))-(1<<(b-1))
def pair(pc):
 w=u32(pc); v=u32(pc+4)
 assert w&0xfff==0x97 and v&0x707f==0x67
 return (pc+signed(w&0xfffff000,32)+signed(v>>20,12))&0xffffffff
def jal(pc):
 w=u32(pc); assert w&0x7f==0x6f
 v=(w>>31<<20)|((w>>12&255)<<12)|((w>>20&1)<<11)|((w>>21&1023)<<1)
 return (pc+signed(v,21))&0xffffffff
def window(lo,hi):
 start=lo; out=[]
 while lo<hi:
  b=raw[lo-BASE:lo-BASE+4]; i=next(md.disasm(b,lo,1),None)
  n=i.size if i else (4 if b[0]&3==3 else 2)
  out.append(dict(pc=hex(lo),bytes=b[:n].hex(),asm=i.mnemonic+' '+i.op_str if i else 'unknown; no semantics assigned')); lo+=n
 assert lo==hi
 return dict(start=hex(start),end_exclusive=hex(hi),instructions=out)
windows=[window(0xa006329c,0xa006334c),window(0xa0197ebc,0xa0197f02),window(0xa01a8d2e,0xa01a8d6c)]
pairs={0xa0063306:0xa0197ebc,0xa0063342:0xa0197f02,0xa0197ecc:0xa002fcc8,0xa0197ee2:0xa002e14e,0xa01a8d3a:0xa0026844,0xa01a8d5e:0xa00267c0}
jals={0xa00632ae:0xa0058386,0xa00632ba:0xa002fcc8,0xa00632cc:0xa0024906,0xa00632e4:0xa0058386,0xa0063318:0xa00b7bc0,0xa0197eda:0xa01a8d2e,0xa01a8d50:0xa01a4468}
assert all(pair(k)==v for k,v in pairs.items())
assert all(jal(k)==v for k,v in jals.items())
# Verify the decisive output write, passed slot address and queue attachment as RV32 fields.
def sw(pc,rs1,rs2,imm):
 w=u32(pc); got=signed(((w>>25)<<5)|(w>>7&31),12)
 assert w&0x707f==0x2023 and w>>15&31==rs1 and w>>20&31==rs2 and got==imm
sw(0xa0197ef8,18,9,0); sw(0xa006332c,23,26,8)
w=u32(0xa0063302)
assert w&0x707f==0x13 and w>>7&31==10 and w>>15&31==26 and signed(w>>20,12)==24
w=u32(0xa0063336)
assert w&0x707f==0x13 and w>>7&31==12 and w>>15&31==12
assert ((0xa0127000+signed(w>>20,12))&0xffffffff)==0xa0126946
strings=[]
for pc in (0xa02566c4,):
 b=raw[pc-BASE:pc-BASE+100].split(b'\0')[0]; strings.append(dict(address=hex(pc),bytes=b.hex(),text=b.decode('ascii')))
out=dict(task='A05',method='bounded original ROM reads; no target execution or ROM-wide search',capstone=__version__,windows=windows,checks=dict(auipc_jalr_targets={hex(k):hex(v) for k,v in pairs.items()},jal_targets={hex(k):hex(v) for k,v in jals.items()},decisive_RV32_fields_verified=True),strings=strings,limits=['Only initialization local in a0062d28 plus two helper bodies recovered.','a0197f02 registration ABI and a01a4468 initialization internals not recovered.','Consumer input identity through thread registration remains inferred, not proven.','No buzzer exited_sem alias is established.'])
(HERE/'instruction-evidence.json').write_text(json.dumps(out,indent=2)+'\n',encoding='utf8')
print('PASS',sum(len(w['instructions']) for w in windows),'instructions',sum(int(w['end_exclusive'],16)-int(w['start'],16) for w in windows),'bytes',strings)
