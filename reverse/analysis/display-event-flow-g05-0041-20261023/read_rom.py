from pathlib import Path
import capstone,sys,json
BASE=0x9ffff000
rom=Path('D:/Documents/PlatformIO/Projects/cuktech-ap01-firmware/roms/0041/ap01-1.0.2_0041.bin').read_bytes()
cs=capstone.Cs(capstone.CS_ARCH_RISCV,capstone.CS_MODE_RISCV32|capstone.CS_MODE_RISCVC)
def sx(x,b):return x-(1<<b) if x&(1<<(b-1)) else x
def rows(a,z):
 while a<z:
  b=rom[a-BASE:a-BASE+4]; n=4 if b[0]&3==3 else 2; b=b[:n]; w=int.from_bytes(b,'little'); i=next(cs.disasm(b,a),None)
  t=None
  if n==4 and w&127==0x6f:t=a+sx((w>>31<<20)|((w>>12&255)<<12)|((w>>20&1)<<11)|((w>>21&1023)<<1),21)
  if n==2 and w&3==1 and w>>13 in (1,5):t=a+sx(((w>>12&1)<<11)|((w>>11&1)<<4)|((w>>9&3)<<8)|((w>>8&1)<<10)|((w>>7&1)<<6)|((w>>6&1)<<7)|((w>>3&7)<<1)|((w>>2&1)<<5),12)
  if n==4 and w&127==0x17:
   v=int.from_bytes(rom[a-BASE+4:a-BASE+8],'little')
   if v&127==0x67:t=(a+sx(w&0xfffff000,32)+sx(v>>20,12))&0xffffffff
  yield dict(pc=hex(a),raw=b.hex(),asm=(i.mnemonic+' '+i.op_str if i else f'THEAD rd={(w>>7)&31} rs1={(w>>15)&31} rs2={(w>>20)&31} f3={(w>>12)&7} f7={w>>25}'),target=hex(t) if t else None)
  a+=n
if __name__=='__main__':
 if sys.argv[1]=='scan':
  wanted={int(x,16) for x in sys.argv[2:]}
  for r in rows(0xa0000000,0xa01c0000):
   if r['target'] and int(r['target'],16) in wanted:print(r)
 else:
  for r in rows(int(sys.argv[1],16),int(sys.argv[2],16)):print(r['pc'],r['raw'],r['asm'],r['target'] or '')
