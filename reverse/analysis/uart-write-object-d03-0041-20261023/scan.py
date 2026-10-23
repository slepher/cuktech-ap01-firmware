from pathlib import Path
import struct,sys
raw=Path('D:/Documents/PlatformIO/Projects/cuktech-ap01-firmware/roms/0041/ap01-1.0.2_0041.bin').read_bytes();base=0x9ffff000
sx=lambda v,n:v-(1<<n) if v>>(n-1) else v
for targ in [int(a,16) for a in sys.argv[1:]]:
 print('TARGET',hex(targ),'words',[hex(base+i) for i in range(len(raw)-3) if raw[i:i+4]==struct.pack('<I',targ)][:50])
 for i in range(0,min(len(raw)-4,0x1b9000),2):
  w=int.from_bytes(raw[i:i+4],'little');pc=base+i
  if w&127==0x6f:
   imm=((w>>31)<<20)|(((w>>12)&255)<<12)|(((w>>20)&1)<<11)|(((w>>21)&1023)<<1)
   if (pc+sx(imm,21))&0xffffffff==targ:print('J',hex(pc))
  if w&127==0x37 and ((targ+0x800)&0xfffff000)==w&0xfffff000:
   rd=(w>>7)&31
   for j in range(i+4,min(i+44,len(raw)-4),2):
    z=int.from_bytes(raw[j:j+4],'little')
    if z&127 in (0x13,3,0x23) and (z>>15)&31==rd:
     imm=(z>>20) if z&127!=0x23 else ((z>>25)<<5)|((z>>7)&31)
     if ((w&0xfffff000)+sx(imm,12))&0xffffffff==targ:print('LUI',hex(pc),'use',hex(base+j))
