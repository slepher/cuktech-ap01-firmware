"""F32 retained-evidence selection and identity checks only. No ROM access."""
import json
from pathlib import Path
ROOT=Path('D:/Documents/PlatformIO/Projects/cuktech-ap01-firmware')
HERE=Path(__file__).parent
source=ROOT/'evidence/rea-0041-20261017/evidence/upper-complete.evidence.json'
j=json.loads(source.read_text(encoding='utf-8'))
profile='4825fb58a33a3e7d618557975b153b8318cf7e833d190ad16bcbf8bd441ae621'
selection={
248:['0xa00653b8: lui a5, 0xa0110','0xa00653bc: addi a5, a5, 0x788','0xa00653c0: sw a5, -0x124, s0',
     '0xa00653c4: lui a5, 0xa0110','0xa00653c8: addi a5, a5, -0x67c','0xa00653d4: sw a5, -0x120, s0',
     '0xa00653d8: sw s10, -0x11c, s0','0xa00653ec: lui a5, 0xa011e','0xa00653f0: addi a5, a5, 0xac',
     '0xa00653f4: sw a5, 0x15c, s1','0xa00653fe: sw s7, 0x160, s1',
     '0xa006556a: c.mv a4, s7','0xa0065578: jalr ra, ra, -0x66','0xa006557c: c.beqz a0, 0xa00655da',
     '0xa00655b8: c.mv a0, s7','0xa00655ba: jal ra, 0xa011fd3c','0xa00655be: c.j 0xa0064fa2'],
195:['0xa011e3ee: c.mv s1, a0','0xa011e436: c.lw a4, 0x10, s1','0xa011e440: c.lw a5, 0x4, a4',
     '0xa011e442: c.beqz a5, 0xa011e44c','0xa011e444: c.lw a1, 0x8, a4','0xa011e446: c.mv a0, s1',
     '0xa011e448: c.jalr a5','0xa011e44a: c.mv s2, a0','0xa011e454: c.sw a5, 0x14, s1'],
309:['0xa011e0ac: c.lw a5, 0x40, a1','0xa011e0ae: c.beqz a5, 0xa011e0c8',
     '0xa011e0b8: c.mv a0, a1','0xa011e0ba: c.lw a1, 0x48, a1','0xa011e0bc: c.jalr a5',
     '0xa011e0c2: c.li a0, 0x0','0xa011e0c8: c.li a0, 0x0'],
77:['0xa011fd3c: c.lw a5, 0x18, a0','0xa011fd3e: beq a5, zero, 0xa011fe74',
    '0xa011fd52: c.mv s1, a0','0xa011fdc6: c.lw a0, 0x18, s1',
    '0xa011fdd0: jal ra, 0xa01b3c64','0xa011fdd4: sw zero, 0x18, s1']}
checks=[];records=[]
for n,expected in selection.items():
 r=j['records'][n];assert r['analysis_profile']['digest']==profile
 a=r['normalized_result']['assembly']
 for s in expected:
  assert a.count(s)==1,(n,s)
  checks.append(f'record{n}:{s.split(":")[0]}')
 records.append(dict(record=n,eid=r['evidence_id'],profile=profile,assembly=expected))
old=ROOT/'evidence/rea-0041-20261017/evidence/upper-miio-b.json'
u=json.loads(old.read_text(encoding='utf-8'))
contracts=[]
for addr in ['0xa011e0ac','0xa011e3d6','0xa0110788','0xa010f984']:
 hits=[x for x in u['functions'] if x['address']==addr]
 assert len(hits)==1
 x=hits[0];assert x['profile_digest']=='04b34bbb41e8ff5d0cbbc2c7471d390693c40fe70f2e21519e2b21d268c9237d'
 contracts.append(dict(address=addr,role=x['role'],eid=x['evidence_id'],profile=x['profile_digest']))
 checks.append('existing-local-contract:'+addr)
routing=ROOT/'evidence/rea-0041-20261017/evidence/upper-routing.md'
rt=routing.read_text(encoding='utf-8')
assert '## 0xa011fd3c' in rt and 'caller-owned group storage is not freed' in rt
checks.append('existing-routing-contract-boundary')
assert 0x164-0x128==0x3c and 0x15c-0x128==0x34 and 0x158-0x128==0x30
assert 0x140-0x128==0x18 and 0xe8+0x880==0x968 and 0xe8+0x8c==0x174
checks.append('same-manager-offset-identities')
(HERE/'evidence.json').write_text(json.dumps(dict(task='F32',result='PASS',checks=checks,
 sources=[str(source.relative_to(ROOT)),str(old.relative_to(ROOT)),str(routing.relative_to(ROOT))],
 records=records,existing_contracts=contracts,rom_bytes_read=0,
 limits=['failure-path close caller only; not actual quit','generic drain inherited, no queued-I completion claim',
         'lower queue-return/callback helpers remain opaque']),ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
print(f'PASS {len(checks)} retained-reference/identity checks; ROM0B')
