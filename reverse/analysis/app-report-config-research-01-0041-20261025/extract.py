"""Q25: offline four-callback exact-byte static extraction, no target execution."""
import hashlib,json
from pathlib import Path
import capstone
from capstone import Cs,CS_ARCH_RISCV,CS_MODE_RISCV32,CS_MODE_RISCVC
ROOT=Path('D:/Documents/PlatformIO/Projects/cuktech-ap01-firmware')
OUT=Path(__file__).resolve().parent
BASE=0x9ffff000
WINDOWS=[(0xa00c6198,464),(0xa00c607e,282),(0xa00c0b82,20),(0xa00c0b6e,20)]
def main():
 data=(ROOT/'roms/0041/ap01-1.0.2_0041.bin').read_bytes()
 digest=hashlib.sha256(data).hexdigest()
 assert len(data)==6769704 and digest=='972db4c136c7ed9e24a83c07c1a7fd62040ca018b08ca285216d26b1fee3c6b9'
 dec=Cs(CS_ARCH_RISCV,CS_MODE_RISCV32|CS_MODE_RISCVC)
 result={'method':'offline bounded static decoding; no target execution','decoder':capstone.__version__,'sha256':digest,'size':len(data),'mapping':'offset=VA-0x9ffff000','windows':[]}
 for start,length in WINDOWS:
  raw=data[start-BASE:start-BASE+length];pos=0;rows=[]
  while pos<len(raw):
   half=int.from_bytes(raw[pos:pos+2],'little');size=4 if half&3==3 else 2
   word=raw[pos:pos+size];ins=list(dec.disasm(word,start+pos))
   asm=ins[0].mnemonic+' '+ins[0].op_str if len(ins)==1 and ins[0].size==size else 'UNDECODED'
   row={'pc':hex(start+pos),'raw':word.hex(),'asm':asm}
   if asm.startswith('jal '): row['target']=hex(start+pos+int(asm.split()[-1],0))
   rows.append(row);pos+=size
  assert pos==length
  result['windows'].append({'start':hex(start),'length':length,'offset':start-BASE,'sha256':hashlib.sha256(raw).hexdigest(),'raw':raw.hex(),'rows':rows})
  print('\n'+hex(start))
  for row in rows: print(row['pc'],row['raw'],row['asm'])
 result['strings']=[]
 for va in [0xa01c3280,0xa06124b8,0xa056bd3c,0xa0565a9c,0xa0565ae4,0xa0565b2c]:
  raw=data[va-BASE:va-BASE+80].split(bytes([0]))[0]
  result['strings'].append({'va':hex(va),'raw':raw.hex(),'text':raw.decode('ascii')})
 (OUT/'static-windows.json').write_text(json.dumps(result,indent=2),encoding='utf-8')
 bundle=json.loads((ROOT/'evidence/rea-0041-20261017/evidence/upper-complete.evidence.json').read_text(encoding='utf-8'))
 roots=[bundle['records'][i] for i in [26,45]]
 (OUT/'inherited-roots.json').write_text(json.dumps(roots,indent=2),encoding='utf-8')
if __name__=='__main__':main()
