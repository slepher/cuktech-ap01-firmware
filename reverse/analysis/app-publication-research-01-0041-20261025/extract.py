import json
from pathlib import Path
import capstone
from capstone import Cs,CS_ARCH_RISCV,CS_MODE_RISCV32,CS_MODE_RISCVC
ROOT=Path('D:/Documents/PlatformIO/Projects/cuktech-ap01-firmware')
OUT=Path(__file__).resolve().parent
WINDOWS=[(0xa011c0da,298),(0xa0113340,92),(0xa0116b5a,202),(0xa0116db0,54),(0xa0116ad0,138)]
def main():
 image=ROOT/'roms/0041/ap01-1.0.2_0041.bin';assert image.stat().st_size==6769704
 dec=Cs(CS_ARCH_RISCV,CS_MODE_RISCV32|CS_MODE_RISCVC);result=[]
 with image.open('rb') as f:
  for start,n in WINDOWS:
   f.seek(start-0x9ffff000);data=f.read(n);rows=[];p=0
   while p<n:
    h=int.from_bytes(data[p:p+2],'little');sz=4 if h&3==3 else 2;raw=data[p:p+sz];ins=list(dec.disasm(raw,start+p));asm=ins[0].mnemonic+' '+ins[0].op_str if len(ins)==1 and ins[0].size==sz else 'UNDECODED'
    rows.append(dict(pc=hex(start+p),raw=raw.hex(),asm=asm));p+=sz
   assert p==n
   result.append(dict(start=hex(start),length=n,raw=data.hex(),rows=rows))
   print('\n'+hex(start))
   for row in rows: print(row['pc'],row['raw'],row['asm'])
 (OUT/'raw.json').write_text(json.dumps(dict(decoder=capstone.__version__,windows=result),indent=2),encoding='utf-8')
if __name__=='__main__':main()
