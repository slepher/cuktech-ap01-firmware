"""H10: bounded static call-site and direct-store checks; no target execution."""
import json
from pathlib import Path
from capstone import Cs, CS_ARCH_RISCV, CS_MODE_RISCV32, CS_MODE_RISCVC
H=Path(__file__).resolve().parent
M=Path('D:/Documents/PlatformIO/Projects/cuktech-ap01-firmware')
b=(M/'roms/0041/ap01-1.0.2_0041.bin').read_bytes(); BASE=0x9ffff000
cs=Cs(CS_ARCH_RISCV,CS_MODE_RISCV32|CS_MODE_RISCVC)
def window(a,e):
 rows=[]; at=a
 for i in cs.disasm(b[a-BASE:e-BASE],a):
  assert i.address==at
  rows.append(dict(address=hex(at),offset=hex(at-BASE),bytes=i.bytes.hex(),mnemonic=i.mnemonic,operands=i.op_str));at+=i.size
 assert at==e,(hex(at),hex(e))
 return rows
def w(a):return int.from_bytes(b[a-BASE:a-BASE+4],'little')
def sx(x,n):return (x^(1<<(n-1)))-(1<<(n-1))
checks=[]
def ck(n,a,e):
 assert a==e,(n,a,e)
 checks.append(dict(name=n,actual=a,expected=e))
# The earlier H08/H09 object identity and DELETE contract are inherited.
ck('helper argument a0 = ctx+5c',[(w(0xa005e196)>>7)&31,(w(0xa005e196)>>15)&31,sx(w(0xa005e196)>>20,12)],[10,18,92])
ck('a1=a2=page/s3 raw RVC',b[0xa005e192-BASE:0xa005e196-BASE].hex(),'4e86ce85')
ck('helper target',0xa005e19e+sx(w(0xa005e19e)&0xfffff000,32)+sx(w(0xa005e1a2)>>20,12),0xa0198d3e)
ck('helper saves incoming a0 in s1',b[0xa0198d48-BASE:0xa0198d4a-BASE].hex(),'aa84')
body=window(0xa0198d3e,0xa0199064)
# Bound conclusion to direct stores through the preserved incoming s1.
stores=[r for r in body if r['mnemonic'] in ('sw','c.sw','sh','sb') and '(s1)' in r['operands']]
ck('direct s1 store offsets',[int(r['operands'].split(', ')[1].split('(')[0],0) for r in stores],[0,12,4,8,16,40])
ck('helper return',body[-1]['bytes'],'8280')
ck('direct s1 reassignment count',len([r for r in body if r['mnemonic'] not in ('sw','c.sw','sh','sb','c.swsp','c.lwsp') and r['operands'].split(',')[0]=='s1']),1)
ck('substructure target offset',0x78-0x5c,0x1c)
# Independent S-format decode of the two uncompressed substructure stores.
for a,reg,off in [(0xa0198f8a,18,12),(0xa0199020,0,16)]:
 q=w(a);ck(hex(a)+' S format',[q&127,(q>>12)&7,(q>>15)&31,(q>>20)&31,sx(((q>>25)<<5)|((q>>7)&31),12)],[35,2,9,reg,off])
# Inherited historical callback label is only a weather consumer, not a timer seed.
d=json.loads((M/'reverse/rehost/weather-calendar-complete-0041.json').read_text(encoding='utf8'))
ck('weather callback source address',d['evidence'][18]['address'],'a00ab754')
p=json.loads((M/'reverse/rehost/page-logic-evidence.json').read_text(encoding='utf8'))
ck('page logic string source is 0031',p['records'][3]['subject']['local_path'].endswith('ap01-1.0.2_0031.bin'),True)
result=dict(scope='bounded helper exclusion, not timer lifecycle closure',checks=checks,helper_scanned=dict(start='0xa0198d3e',end_exclusive='0xa0199064',bytes=0x326,instructions=len(body),retained='only incoming-s1 direct stores and small ABI windows; no complete helper export'),windows=[dict(name='type2-helper-call-ABI',instructions=window(0xa005e192,0xa005e1a6)),dict(name='helper-incoming-object',instructions=window(0xa0198d48,0xa0198d4a))],direct_stores=stores,unknowns=['actual ctx+0x78 writer','timer callback and normal update ABI','runtime timer and DELETE reachability'],new_timer_functionality=0)
(H/'evidence.json').write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n',encoding='utf8')
print(f'PASS: {len(checks)} checks; {len(body)} helper instructions inspected; {len(stores)} direct stores; no lifecycle closure claimed')
