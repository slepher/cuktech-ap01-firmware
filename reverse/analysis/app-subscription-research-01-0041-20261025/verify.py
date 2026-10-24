import json,hashlib,datetime
from pathlib import Path
from capstone import *
S=Path('D:/Documents/PlatformIO/Projects/cuktech-ap01-firmware'); O=Path(__file__).resolve().parent
rom=(S/'roms/0041/ap01-1.0.2_0041.bin').read_bytes(); assert len(rom)==6769704
md=Cs(CS_ARCH_RISCV,CS_MODE_RISCV32|CS_MODE_RISCVC)
w=[]
for start,n in [(0xa011d10e,244),(0xa01abe54,170),(0xa0113c8a,738),(0xa0118b08,76),(0xa011bffe,220),(0xa011bfc4,58),(0xa01188a6,274)]:
 raw=rom[start-0x9ffff000:start-0x9ffff000+n]; lines=[]; at=0
 while at<n:
  ins=next(md.disasm(raw[at:],start+at,count=1),None)
  if ins: lines.append(f'{ins.address:08x}: {ins.bytes.hex()} {ins.mnemonic} {ins.op_str}'); at+=ins.size
  else:
   width=4 if raw[at]&3==3 else 2
   lines.append(f'{start+at:08x}: {raw[at:at+width].hex()} UNKNOWN'); at+=width
 w.append(dict(start=hex(start),size=n,file_offset=start-0x9ffff000,hex=raw.hex(),sha256=hashlib.sha256(raw).hexdigest(),assembly=lines))
j=json.loads((S/'evidence/rea-0041-20261017/evidence/upper-complete.evidence.json').read_text(encoding='utf-8-sig'))
r=[]
for i in [245,48]:
 x=j['records'][i]
 r.append(dict(ordinal=i,record={k:x[k] for k in ['evidence_id','analysis_profile','normalized_result']}))
assert sum(x['size'] for x in w)==1780
assert len(w)==7
assert rom[0xa011632e-0x9ffff000:0xa0116332-0x9ffff000].hex()=='0bc7994c'
(O/'bounded-evidence.json.tmp').write_text(json.dumps(dict(windows=w,roots=r),indent=2),encoding='utf-8')
(O/'disassembly.txt.tmp').write_text('\n\n'.join('\n'.join(x['assembly']) for x in w),encoding='utf-8')
print(json.dumps({'static_only':True,'window_count':len(w),'window_bytes':1780,'unknown_instructions':sum('UNKNOWN' in l for x in w for l in x['assembly']),'root_evidence_ids':[x['record']['evidence_id'] for x in r]},indent=2))
