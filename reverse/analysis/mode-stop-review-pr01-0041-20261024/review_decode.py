"""P-01 non-author review: bounded ROM decoding; never executes target code."""
import json
from pathlib import Path
from capstone import Cs, CS_ARCH_RISCV, CS_MODE_RISCV32, CS_MODE_RISCVC

ROOT = Path('D:/Documents/PlatformIO/Projects/cuktech-ap01-firmware')
OUT = Path(__file__).resolve().parent
ROM = ROOT / 'roms/0041/ap01-1.0.2_0041.bin'
rom = ROM.read_bytes()
assert len(rom) == 6769704
BASE = 0x9ffff000
decoder = Cs(CS_ARCH_RISCV, CS_MODE_RISCV32 | CS_MODE_RISCVC)
# Explicitly selected from the interface question, including object-base setup.
ranges = [
 ('cleanup',0xa00a3ab6,0xa00a3b22),('ui_deinit',0xa00a3d22,0xa00a3d80),
 ('adc_offline',0xa00a42d4,0xa00a430c),('ota_exit',0xa00a4708,0xa00a4762),
 ('desired_reset',0xa00a5558,0xa00a55ba),('init_prefix',0xa00a55ba,0xa00a5600),
 ('timer_object',0xa00a805a,0xa00a8084),('rediscovery',0xa00a80a8,0xa00a8190),
 ('timer_daily_exit',0xa00a82a6,0xa00a82be),('timer_retry',0xa00a82be,0xa00a831a),
 ('timer_stage3',0xa00a831a,0xa00a8330),('parser_object',0xa00a83f8,0xa00a8422),
 ('parser_dispatch',0xa00a84be,0xa00a8552),('event23',0xa00a8836,0xa00a8856),
 ('miio_entry',0xa00a0bd8,0xa00a0c42),('miio_release',0xa00a0cce,0xa00a0cf0),
 ('miio_mode',0xa00a0cf0,0xa00a0d08),('poll_seed',0xa005b300,0xa005b314),
]
def signed(n,bits):
 return n-(1<<bits) if n & (1<<(bits-1)) else n
def target(pc,b):
 w=int.from_bytes(b,'little')
 if len(b)==4 and w&127==0x6f:
  n=((w>>31)<<20)|(((w>>12)&255)<<12)|(((w>>20)&1)<<11)|(((w>>21)&1023)<<1)
  return pc+signed(n,21)
 if len(b)==4 and w&127==0x63:
  n=((w>>31)<<12)|(((w>>7)&1)<<11)|(((w>>25)&63)<<5)|(((w>>8)&15)<<1)
  return pc+signed(n,13)
 if len(b)==2 and w&3==1 and w>>13 in (6,7):
  n=(((w>>12)&1)<<8)|(((w>>10)&3)<<3)|(((w>>5)&3)<<6)|(((w>>3)&3)<<1)|(((w>>2)&1)<<5)
  return pc+signed(n,9)
 if len(b)==2 and w&3==1 and w>>13 in (1,5):
  n=(((w>>12)&1)<<11)|(((w>>11)&1)<<4)|(((w>>9)&3)<<8)|(((w>>8)&1)<<10)|(((w>>7)&1)<<6)|(((w>>6)&1)<<7)|(((w>>3)&7)<<1)|(((w>>2)&1)<<5)
  return pc+signed(n,12)
 return None
windows=[]; rows={}
for name,start,end in ranges:
 pc=start; decoded=[]
 while pc<end:
  off=pc-BASE; size=4 if rom[off]&3==3 else 2; b=rom[off:off+size]
  assert pc+size<=end,(name,hex(pc),'partial instruction')
  ins=list(decoder.disasm(b,pc,count=1))
  asm=(ins[0].mnemonic+' '+ins[0].op_str).strip() if ins else 'UNKNOWN'
  row={'pc':hex(pc),'raw':b.hex(),'asm':asm}
  t=target(pc,b)
  if t is not None: row['independent_target']=hex(t)
  decoded.append(row); rows[pc]=row; pc+=size
 windows.append({'name':name,'start':hex(start),'end_exclusive':hex(end),'rows':decoded})
# This table asserts interface edges, independent of author check operands.
edges={0xa00a4302:0xa00a3d22,0xa00a4306:0xa00a3ab6,
 0xa00a4710:0xa00a3d22,0xa00a4714:0xa00a3ab6,
 0xa00a884c:0xa00a3d22,0xa00a8850:0xa00a3ab6,
 0xa00a55fc:0xa00a5558,0xa00a8150:0xa00a5558,
 0xa00a80b2:0xa00a826c,0xa00a814e:0xa00a81ae,
 0xa00a0c34:0xa00a0cf0,0xa00a0cfe:0xa00a0cce,
 0xa00a0d02:0xa019537a,0xa00a0d06:0xa00a0cce,
 0xa005b310:0xa009f9b6,0xa00a82bc:0xa00a8084}
for pc,t in edges.items(): assert rows[pc]['independent_target']==hex(t),(hex(pc),rows[pc],hex(t))
# Only now compare independent output to the author's data, never import verifier.
author=json.loads((ROOT/'reverse/analysis/mode-stop-p01-0041-20261024/instruction-evidence.json').read_text())
matches=0
for w in author['windows']:
 for r in w['rows']:
  p=int(r['pc'],16)
  assert rows[p]['raw']==r['raw'] and rows[p]['asm']==r['asm'],(r,rows[p])
  matches+=1
sources=[]; raw_matches=0
for s in author['sources']:
 data=json.loads((ROOT/s['path']).read_text())
 f=next(f for f in data['functions'] if f['evidence_id']==s['evidence_id'])
 digest=f.get('profile_digest',f.get('profile',{}).get('digest'))
 # Profile schemas may wrap digest under analysis_profile_digest.
 if digest is None: digest=f.get('profile',{}).get('analysis_profile_digest')
 assert digest==s['profile_digest'],(s['path'],digest)
 for raw in f.get('raw_ranges',[]):
  off=raw.get('file_offset')
  if isinstance(off,str): off=int(off,0)
  if off is None: off=int(raw['start'],16)-BASE
  b=bytes.fromhex(raw.get('bytes_hex',raw.get('hex','')))
  assert b and rom[off:off+len(b)]==b,(s['path'],raw.keys())
  raw_matches+=len(b)
 sources.append(s)
unknown=[r['pc'] for r in rows.values() if r['asm']=='UNKNOWN']
metadata_path='evidence/rea-0041-20261017/evidence/whole-rom-coverage-0041-20261023-initial.json'
metadata=json.loads((ROOT/metadata_path).read_text())
callers=[{'address':f['address'],'evidence_id':f['direct_calls']['evidence_id']} for f in metadata['functions'] if '0xa00a5558' in f.get('direct_calls',{}).get('callees',[])]
assert {c['address'] for c in callers}=={'0xa00a55ba','0xa00a805a'}
seed=json.loads((ROOT/'reverse/analysis/factory-test-0041-20261023/retained-initializer.json').read_text())['function']
assert seed['evidence_id']=='ev_dc0e38b0f382799ea2a8e8ad7f21cefc5998b0767ecf38a58cfdebe8add167c3'
assert seed['profile']['digest']=='bcefdee5092076e55636e077b45523e203f4b870ae7b7ab547945ed1b8162279'
result={'claim':'P-01 / P-R01','method':'Independent ROM halfword boundary decode and J/B/CB/CJ bitfields; author verifier neither read nor executed',
 'rom':'CATALOG 0041 identity inherited; actual length 6769704; VA-0x9ffff000',
 'windows':windows,'sources':sources,'reset_direct_callers':{'source':metadata_path,'callers':callers,'limit':'Existing metadata direct edges only; not an exhaustive ROM or indirect-call census'},'seed':{'evidence_id':seed['evidence_id'],'profile':seed['profile']['digest'],'limit':'Argument construction/call only; s3 ownership and close remain unknown'},'checks':{'windows':len(windows),'bytes':sum(b-a for _,a,b in ranges),'instructions':len(rows),'edge_assertions':len(edges),'author_rows_matched':matches,'source_raw_bytes_matched':raw_matches,'unknown':unknown}}
(OUT/'independent-decode.json').write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
(OUT/'independent-decode.txt').write_text('\n\n'.join(w['name']+'\n'+'\n'.join(r['pc']+' '+r['raw']+' '+r['asm']+(' -> '+r['independent_target'] if 'independent_target' in r else '') for r in w['rows']) for w in windows)+'\n',encoding='utf-8')
print(json.dumps(result['checks']))
