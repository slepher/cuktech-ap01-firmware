"""Q28: bounded static ROM decoding only; never executes firmware or DDF."""
import hashlib, json
from pathlib import Path
from capstone import Cs, CS_ARCH_RISCV, CS_MODE_RISCV32, CS_MODE_RISCVC
ROOT=Path('D:/Documents/PlatformIO/Projects/cuktech-ap01-firmware')
OUT=Path(__file__).resolve().parent
rom=(ROOT/'roms/0041/ap01-1.0.2_0041.bin').read_bytes()
assert len(rom)==6769704
assert hashlib.sha256(rom).hexdigest()=='972db4c136c7ed9e24a83c07c1a7fd62040ca018b08ca285216d26b1fee3c6b9'
cs=Cs(CS_ARCH_RISCV,CS_MODE_RISCV32|CS_MODE_RISCVC)
ranges=[(0xa00c6f8e,0xa00c756e),(0xa00c6f56,0xa00c6f8e),(0xa00c1930,0xa00c1968),(0xa00c1968,0xa00c1a00),(0xa00c6efe,0xa00c6f56),(0xa00c6eba,0xa00c6efe)]
def signed(x,n): return x-(1<<n) if x&(1<<(n-1)) else x
def target(pc,b):
 w=int.from_bytes(b,'little')
 if len(b)==4 and w&127==0x6f: return pc+signed(((w>>31)<<20)|(((w>>12)&255)<<12)|(((w>>20)&1)<<11)|(((w>>21)&1023)<<1),21)
 if len(b)==4 and w&127==0x63: return pc+signed(((w>>31)<<12)|(((w>>7)&1)<<11)|(((w>>25)&63)<<5)|(((w>>8)&15)<<1),13)
 if len(b)==2 and w&3==1 and w>>13 in (6,7): return pc+signed((((w>>12)&1)<<8)|(((w>>10)&3)<<3)|(((w>>5)&3)<<6)|(((w>>3)&3)<<1)|(((w>>2)&1)<<5),9)
 if len(b)==2 and w&3==1 and w>>13 in (1,5): return pc+signed((((w>>12)&1)<<11)|(((w>>11)&1)<<4)|(((w>>9)&3)<<8)|(((w>>8)&1)<<10)|(((w>>7)&1)<<6)|(((w>>6)&1)<<7)|(((w>>3)&7)<<1)|(((w>>2)&1)<<5),12)
windows=[]; lines=[]
for start,end in ranges:
 rows=[]; pc=start; lines.append('\nFUNCTION '+hex(start))
 while pc<end:
  off=pc-0x9ffff000; n=4 if rom[off]&3==3 else 2; b=rom[off:off+n]; assert pc+n<=end
  ins=list(cs.disasm(b,pc,count=1)); asm=(ins[0].mnemonic+' '+ins[0].op_str).strip() if ins else 'UNKNOWN'
  t=target(pc,b); r={'pc':hex(pc),'raw':b.hex(),'asm':asm}
  if t is not None:r['target']=hex(t)
  rows.append(r); lines.append(f'{pc:08x} {b.hex():8} {asm}'+(f' -> {t:08x}' if t is not None else '')); pc+=n
 windows.append({'start':hex(start),'end_exclusive':hex(end),'bytes':end-start,'rows':rows})
metadata=json.loads((ROOT/'reverse/analysis/whole-rom-coverage-0041-20261023-round1.json').read_text(encoding='utf-8'))
selected=[f for f in metadata['functions'] if f['address'] in {hex(s) for s,e in ranges}]
assert len(selected)==6
result={'claim':'Q28/S-P39','base':'0x9ffff000','rom_sha256':hashlib.sha256(rom).hexdigest(),'windows':windows,'metadata_only':selected,'new_bytes':sum(e-s for s,e in ranges)}
assert result['new_bytes']==1924
literal_addresses=[0xa01c3280,0xa06124b8,0xa056bd3c,0xa0565c0c,0xa0565c14,0xa0267a60,0xa0565a3c,0xa0565a44,0xa0565c60]
result['api_literals']=[{'va':hex(a),'raw_hex':rom[a-0x9ffff000:a-0x9ffff000+100].split(b'\0')[0].hex(),'text':rom[a-0x9ffff000:a-0x9ffff000+100].split(b'\0')[0].decode('ascii')} for a in literal_addresses]
parents=json.loads((ROOT/'evidence/rea-0041-20261017/evidence/upper-complete.evidence.json').read_text(encoding='utf-8'))
result['inherited_supplemental_roots']=[{'record_index':i,'evidence_id':parents['records'][i]['evidence_id'],'profile_digest':parents['records'][i]['analysis_profile']['digest']} for i in [176,291]]
result['inherited_upper_card_profile']='04b34bbb41e8ff5d0cbbc2c7471d390693c40fe70f2e21519e2b21d268c9237d'
rows={int(r['pc'],16):r for w in windows for r in w['rows']}
for f in selected:
 w=next(w for w in windows if w['start']==f['address'])
 assert f['extent']['body']['total_bytes']==w['bytes']
 assert f['extent']['body']['ranges']==[{'start':w['start'],'end':hex(int(w['end_exclusive'],16)-1)}]
 calls={r['target'] for r in w['rows'] if r['asm'].startswith(('jal ','c.jal '))}
 assert calls==set(f['direct_calls']['callees']),(w['start'],calls,f['direct_calls']['callees'])
 for r in w['rows']:
  if 'target' in r and int(w['start'],16)<=int(r['target'],16)<int(w['end_exclusive'],16): assert int(r['target'],16) in rows
edges={0xa00c6fce:0xa0191d52,0xa00c7100:0xa00c6efe,0xa00c710c:0xa00602e6,0xa00c7568:0xa00bd7fa,0xa00c6f72:0xa00c6efe,0xa00c6f7e:0xa00bd7fa,0xa00c6f1c:0xa00c6eba,0xa00c6f24:0xa00c6eba,0xa00c6f2c:0xa00c6eba,0xa00c6f34:0xa00c6eba,0xa00c6f3c:0xa00c6eba,0xa00c6ee4:0xa006929a,0xa00c6eec:0xa002e14e,0xa00c6ef2:0xa002e14e}
for pc,t in edges.items(): assert rows[pc]['target']==hex(t)
result['checks']={'metadata_extents':6,'metadata_call_sets':6,'critical_edges':len(edges),'internal_targets_on_instruction_boundaries':True,'unknown':sum(r['asm']=='UNKNOWN' for r in rows.values())}
(OUT/'instructions.json').write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
(OUT/'instructions.txt').write_text('\n'.join(lines)+'\n',encoding='utf-8')
print({'new_bytes':result['new_bytes'],'instructions':sum(len(w['rows']) for w in windows),'unknown':[r['pc'] for w in windows for r in w['rows'] if r['asm']=='UNKNOWN']})
