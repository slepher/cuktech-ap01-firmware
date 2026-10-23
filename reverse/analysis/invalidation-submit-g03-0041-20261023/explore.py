from pathlib import Path
import capstone,sys
ROM=Path('D:/Documents/PlatformIO/Projects/cuktech-ap01-firmware/roms/0041/ap01-1.0.2_0041.bin').read_bytes()
BASE=0x9ffff000
cs=capstone.Cs(capstone.CS_ARCH_RISCV,capstone.CS_MODE_RISCV32|capstone.CS_MODE_RISCVC)
def signed(v,b):return v-(1<<b) if v&(1<<(b-1)) else v
def target(a,n,w):
 if n==4 and w&127==0x63:
  v=(((w>>31)&1)<<12)|(((w>>7)&1)<<11)|(((w>>25)&63)<<5)|(((w>>8)&15)<<1);return a+signed(v,13)
 if n==2 and w&3==1 and w>>13 in (6,7):
  v=(((w>>12)&1)<<8)|(((w>>10)&3)<<3)|(((w>>5)&3)<<6)|(((w>>3)&3)<<1)|(((w>>2)&1)<<5);return a+signed(v,9)
 if n==4 and w&127==0x6f:
  v=((w>>31)<<20)|(((w>>12)&255)<<12)|(((w>>20)&1)<<11)|(((w>>21)&1023)<<1);return a+signed(v,21)
 if n==2 and w&3==1 and w>>13 in (1,5):
  v=(((w>>12)&1)<<11)|(((w>>11)&1)<<4)|(((w>>9)&3)<<8)|(((w>>8)&1)<<10)|(((w>>7)&1)<<6)|(((w>>6)&1)<<7)|(((w>>3)&7)<<1)|(((w>>2)&1)<<5);return a+signed(v,12)
def rows(start,end):
 a=start
 while a<end:
  h=int.from_bytes(ROM[a-BASE:a-BASE+2],'little');n=4 if h&3==3 else 2;b=ROM[a-BASE:a-BASE+n];w=int.from_bytes(b,'little');ins=list(cs.disasm(b,a));t=target(a,n,w)
  if n==4 and w&127==11:
   op='TH';arg=f'rd={(w>>7)&31} rs1={(w>>15)&31} rs2={(w>>20)&31} f3={(w>>12)&7} f7={w>>25} hi={w>>26} lo={(w>>20)&63}'
  else:op,arg=(ins[0].mnemonic,ins[0].op_str) if ins else ('UNKNOWN','')
  yield dict(address=hex(a),offset=a-BASE,bytes=b.hex(),op=op,operands=arg,target=hex(t) if t else None)
  a+=n
if __name__=='__main__':
 for r in rows(int(sys.argv[1],16),int(sys.argv[2],16)):
  print(r['address'],r['bytes'],r['op'],r['operands'],('=> '+r['target']) if r['target'] else '')
