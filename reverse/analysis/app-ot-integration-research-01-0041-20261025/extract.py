from pathlib import Path
import hashlib,json
from capstone import *
R=Path('D:/Documents/PlatformIO/Projects/cuktech-ap01-firmware')
O=Path(__file__).resolve().parent
b=(R/'roms/0041/ap01-1.0.2_0041.bin').read_bytes(); base=0x9ffff000
assert len(b)==6769704 and hashlib.sha256(b).hexdigest()=='972db4c136c7ed9e24a83c07c1a7fd62040ca018b08ca285216d26b1fee3c6b9'
wins=[('event',0xa0112dae,0xa0113340),('parent_cb',0xa010fd4e,0xa010fdf0),('owner_cb_a',0xa01129be,0xa0112b12),('owner_cb_b',0xa0112b1e,0xa0112b5e),('adapter',0xa0112734,0xa01129be),('periodic',0xa01137f6,0xa011398a),('pull',0xa0110aca,0xa0110c3a),('pull_reply',0xa01109d6,0xa0110aca)]
cs=Cs(CS_ARCH_RISCV,CS_MODE_RISCV32|CS_MODE_RISCVC); rec=[]; lines=[]
for name,s,e in wins:
 p=s; rows=[]; lines.append('\n## '+name)
 while p<e:
  h=int.from_bytes(b[p-base:p-base+2],'little'); n=4 if h&3==3 else 2; raw=b[p-base:p-base+n]; ds=list(cs.disasm(raw,p)); asm=ds[0].mnemonic+' '+ds[0].op_str if len(ds)==1 and ds[0].size==n else 'UNDECODED'
  rows.append({'pc':hex(p),'raw':raw.hex(),'asm':asm});lines.append(f'{p:08x} {raw.hex():8} {asm}');p+=n
 assert p==e
 rec.append({'name':name,'start':hex(s),'end_exclusive':hex(e),'size':e-s,'sha256':hashlib.sha256(b[s-base:e-base]).hexdigest(),'rows':rows})
assert sum(x['size'] for x in rec)==3658
(O/'instructions.txt').write_text('\n'.join(lines),encoding='utf-8')
(O/'evidence.json').write_text(json.dumps({'rom_sha256':hashlib.sha256(b).hexdigest(),'base':hex(base),'body_bytes':3658,'excluded_gap':{'start':'0xa0112b12','end_exclusive':'0xa0112b1e','raw':b[0xa0112b12-base:0xa0112b1e-base].hex()},'windows':rec},indent=2),encoding='utf-8')
print('instructions',sum(len(x['rows']) for x in rec),'unknown',[(r['pc'],r['raw']) for x in rec for r in x['rows'] if r['asm']=='UNDECODED'])
