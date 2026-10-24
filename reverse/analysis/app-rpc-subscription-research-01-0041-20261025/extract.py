import json,hashlib
from pathlib import Path
import capstone
from capstone import Cs,CS_ARCH_RISCV,CS_MODE_RISCV32,CS_MODE_RISCVC
ROOT=Path('D:/Documents/PlatformIO/Projects/cuktech-ap01-firmware')
OUT=Path(__file__).resolve().parent
WINDOWS=[(0xa00c6368,532),(0xa00c657c,524),(0xa00c6788,524),(0xa00c6994,524),(0xa00c0492,26),(0xa00c04ac,26),(0xa00c2148,26),(0xa00c2438,26),(0xa00c1fd8,184),(0xa00c2090,184),(0xa01adbd4,58),(0xa01adb9a,58),(0xa00c187c,92)]
def main():
 data=(ROOT/'roms/0041/ap01-1.0.2_0041.bin').read_bytes()
 assert len(data)==6769704 and hashlib.sha256(data).hexdigest()=='972db4c136c7ed9e24a83c07c1a7fd62040ca018b08ca285216d26b1fee3c6b9'
 md=Cs(CS_ARCH_RISCV,CS_MODE_RISCV32|CS_MODE_RISCVC)
 result={'method':'offline static raw decode; no target execution','sha256':hashlib.sha256(data).hexdigest(),'decoder':capstone.__version__,'mapping':'offset=VA-0x9ffff000','windows':[]}
 for start,length in WINDOWS:
  raw=data[start-0x9ffff000:start-0x9ffff000+length];rows=[];pos=0
  while pos<length:
   half=int.from_bytes(raw[pos:pos+2],'little');sz=4 if half&3==3 else 2
   chunk=raw[pos:pos+sz];ins=list(md.disasm(chunk,start+pos))
   asm=ins[0].mnemonic+' '+ins[0].op_str if len(ins)==1 and ins[0].size==sz else 'UNDECODED'
   row={'pc':hex(start+pos),'raw':chunk.hex(),'asm':asm}
   if ins and (ins[0].mnemonic=='jal' or ins[0].mnemonic in ['beq','bne','bge','bgeu','blt','bltu','beqz','bnez','c.j','c.beqz','c.bnez']):
    row['relative_target']=hex((start+pos+int(ins[0].op_str.split(',')[-1].strip(),0))&0xffffffff)
   rows.append(row);pos+=sz
  assert pos==length
  result['windows'].append({'start':hex(start),'length':length,'offset':start-0x9ffff000,'sha256':hashlib.sha256(raw).hexdigest(),'raw':raw.hex(),'rows':rows})
 assert len(result['windows'])==13 and sum(w['length'] for w in result['windows'])==2784
 rows={r['pc']:r for w in result['windows'] for r in w['rows']}
 assert all(r['asm']!='UNDECODED' for r in rows.values())
 for pc,target in {'0xa00c639e':'0xa00c6578','0xa00c63aa':'0xa00c6550','0xa00c65b6':'0xa00c6656','0xa00c65c0':'0xa00c6656','0xa00c67c2':'0xa00c6862','0xa00c67cc':'0xa00c6862','0xa00c69ce':'0xa00c6a6e','0xa00c69d8':'0xa00c6a6e'}.items():
  assert rows[pc]['relative_target']==target
 result['literals']={}
 for addr in [0xa01c3280,0xa06124b8,0xa060f238,0xa0565bd0,0xa0565bdc,0xa0564db0,0xa0564dbc,0xa056bd3c]:
  result['literals'][hex(addr)]=data[addr-0x9ffff000:addr-0x9ffff000+96].split(bytes([0]))[0].decode('ascii')
 (OUT/'static-windows.json').write_text(json.dumps(result,indent=2),encoding='utf-8')
 bundle=json.loads((ROOT/'evidence/rea-0041-20261017/evidence/upper-complete.evidence.json').read_text(encoding='utf-8'))
 roots=[bundle['records'][n] for n in [280,56,50,135]]
 assert [r['normalized_result']['procedure']['address'] for r in roots]==['0xa00c1144','0xa00c13f2','0xa00c2162','0xa00c2452']
 (OUT/'inherited-roots.json').write_text(json.dumps(roots,indent=2),encoding='utf-8')
 with (OUT/'disassembly.txt').open('w',encoding='utf-8') as f:
  for w in result['windows']:
   f.write('\n'+w['start']+'\n')
   for r in w['rows']: f.write(r['pc']+' '+r['raw']+' '+r['asm']+(' -> '+r['relative_target'] if 'relative_target' in r else '')+'\n')
 print('windows',len(WINDOWS),'bytes',sum(n for a,n in WINDOWS),'undecoded',sum(r['asm']=='UNDECODED' for w in result['windows'] for r in w['rows']))
 for r in roots: print(r['evidence_id'],r.get('analysis_profile',{}).get('digest'))
if __name__=='__main__':main()
