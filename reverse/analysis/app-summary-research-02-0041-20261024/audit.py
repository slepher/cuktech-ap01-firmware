"""Q-01 bounded original-byte audit; static decoding only, no target execution."""
import json
import re
from pathlib import Path
import capstone
from snapshot_parameter import verify_snapshot

ROOT = Path('D:/Documents/PlatformIO/Projects/cuktech-ap01-firmware')
OUT = Path(__file__).parent
BASE = 0x9ffff000
SOURCE = ROOT/'evidence/rea-0041-20261017/evidence/whole-rom-private-20261023.evidence.json'
bundle = json.loads(SOURCE.read_text(encoding='utf8'))
record = next(r for r in bundle['records'] if r.get('parameters', {}).get('procedure') == '0xa00adabc')
assert record['evidence_id'] == 'ev_19e11c8fc1582881b289f2b24c2a98bbb305f7c2e57caad784442a60d1fb76e5'
assert record['analysis_profile']['digest'] == 'b6368dd18431e8113aa5026c713d41e648ab0f6ddd9421ff6c4a49e23b3cd2f3'
assert record['analysis_profile']['parameters']['language_id'] == 'RISCV:LE:32:ap01thead2'
saved = {int(line.split(':')[0], 16): line.split(': ', 1)[1] for line in record['normalized_result']['assembly']}
# Only branch/width/value windows needed for this contract. Public UI bodies excluded.
windows = [
 (0xa00adcd0,0xa00adce8),(0xa00add16,0xa00add8e),
 (0xa00adde6,0xa00ade06),(0xa00ade5c,0xa00ade72),
 (0xa00ade8a,0xa00adf36),(0xa00adfb2,0xa00adff4),
 (0xa00ae048,0xa00ae04e),(0xa00ae11e,0xa00ae166),
 (0xa00ae43c,0xa00ae44c),(0xa00ae4ee,0xa00ae4f2),
 (0xa00ae536,0xa00ae55c),(0xa00ae5b4,0xa00ae5c2),
 (0xa00ae610,0xa00ae632),(0xa00ae672,0xa00ae696),
 (0xa00ae6ec,0xa00ae6fa),(0xa00ae752,0xa00ae75c),
 (0xa00ae7e8,0xa00ae80e),(0xa00ae864,0xa00ae86c),
 (0xa00ae912,0xa00ae926),(0xa00ae990,0xa00ae99a),
 (0xa00aea26,0xa00aea3c),(0xa00aea68,0xa00aea80),
 (0xa00aee70,0xa00aee86),(0xa00aef82,0xa00af020),
]
md = capstone.Cs(capstone.CS_ARCH_RISCV, capstone.CS_MODE_RISCV32 | capstone.CS_MODE_RISCVC)
rows = []
raws = {}
with (ROOT/'roms/0041/ap01-1.0.2_0041.bin').open('rb') as rom:
 assert rom.seek(0,2) == 6769704
 for lo, hi in windows:
  rom.seek(lo-BASE)
  data = rom.read(hi-lo)
  seq = list(md.disasm(data,lo))
  assert sum(i.size for i in seq) == hi-lo,(hex(lo),hex(hi),[(hex(i.address),i.mnemonic) for i in seq[-3:]])
  assert [i.address for i in seq] == sorted(a for a in saved if lo <= a < hi)
  for i in seq:
   raws[i.address] = bytes(i.bytes)
   rows.append(dict(address=hex(i.address),raw=i.bytes.hex(),decoded=i.mnemonic+' '+i.op_str,retained=saved[i.address]))

checks=[]
def sx(n,b): return n-(1<<b) if n & (1<<(b-1)) else n
def yes(a,kind,got,want):
 assert got == want,(hex(a),kind,got,want)
 checks.append(dict(address=hex(a),kind=kind,expected=want,passed=True))

# Independently decode control targets and compare to original retained absolute addresses.
for a,raw in raws.items():
 w=int.from_bytes(raw,'little'); text=saved[a]; mnemonic=text.split()[0]
 if len(raw)==4 and w&127==0x63:
  d=((w>>31)<<12)|((w>>7&1)<<11)|((w>>25&63)<<5)|((w>>8&15)<<1)
  yes(a,'RV32 branch target',(a+sx(d,13))&0xffffffff,int(text.rsplit(', ',1)[1],16))
 elif len(raw)==4 and w&127==0x6f:
  d=((w>>31)<<20)|((w>>12&255)<<12)|((w>>20&1)<<11)|((w>>21&1023)<<1)
  yes(a,'RV32 jump target',(a+sx(d,21))&0xffffffff,int(text.rsplit(', ',1)[-1].split()[-1],16))
 elif len(raw)==2 and w&3==1 and w>>13 in (6,7):
  d=((w>>12&1)<<8)|((w>>10&3)<<3)|((w>>5&3)<<6)|((w>>3&3)<<1)|((w>>2&1)<<5)
  yes(a,'RVC branch target',a+sx(d,9),int(text.rsplit(', ',1)[1],16))
 elif len(raw)==2 and w&3==1 and w>>13==5:
  d=((w>>12&1)<<11)|((w>>11&1)<<4)|((w>>9&3)<<8)|((w>>8&1)<<10)|((w>>7&1)<<6)|((w>>6&1)<<7)|((w>>3&7)<<1)|((w>>2&1)<<5)
  yes(a,'RVC jump target',a+sx(d,12),int(text.split()[-1],16))

# Explicit register/width/immediate contracts for every new direct slot/latch store.
# (address, source register, base register, byte displacement).
for a,rs,base,disp in [
 (0xa00addfc,15,14,0x101),(0xa00adec8,14,15,0x101),
 (0xa00adecc,0,15,0x106),(0xa00adf2c,15,14,0x101),
 (0xa00ae15e,15,9,0x101),(0xa00ae442,15,14,0x101),
 (0xa00ae554,14,13,0x101),(0xa00ae5ba,14,13,0x101),
 (0xa00ae68e,15,14,0x101),(0xa00ae6f2,14,13,0x101),
 (0xa00ae806,15,14,0x101),(0xa00ae918,15,14,0x101),
 (0xa00aea34,14,15,0x106),(0xa00aee82,19,9,0x101),
 (0xa00aefd4,19,9,0x102),(0xa00aefec,24,9,0x102),
 (0xa00af004,15,9,0x102),
]:
 w=int.from_bytes(raws[a],'little')
 yes(a,'SB fields',[w&127,w>>12&7,w>>20&31,w>>15&31,sx((w>>25<<5)|(w>>7&31),12)],[0x23,0,rs,base,disp])

# Important loads preserve unsigned width, pointer origin and the C2 mode-from-C1 quirk.
for a,rd,base,disp,fn in [
 (0xa00add1e,15,6,0x28,4),(0xa00add28,14,20,0xc,4),
 (0xa00add30,15,18,0xc,4),(0xa00addee,15,18,0x21,4),
 (0xa00adeaa,13,15,0x106,4),(0xa00adeb4,14,18,0xd,4),
 (0xa00ae544,14,18,0x30,2),(0xa00ae548,14,14,8,5),
 (0xa00ae680,14,18,0x30,2),(0xa00ae684,14,14,8,5),
 (0xa00aea68,14,18,0x30,2),(0xa00aea6c,14,14,8,5),
 (0xa00aefb6,24,18,0xc,4),(0xa00aefba,15,9,0x102,4),
 (0xa00af00e,11,9,0x101,4),
]:
 w=int.from_bytes(raws[a],'little')
 yes(a,'load fields',[w&127,w>>7&31,w>>15&31,sx(w>>20,12),w>>12&7],[3,rd,base,disp,fn])

for a,value in [(0xa00add22,1),(0xa00add84,0x15),(0xa00addf6,3),
 (0xa00adeae,1),(0xa00adeb8,2),(0xa00adf26,1),(0xa00ae15c,2),
 (0xa00ae43c,4),(0xa00ae54e,3),(0xa00ae5b4,4),(0xa00ae676,1),
 (0xa00ae6ec,2),(0xa00ae800,1),(0xa00ae916,2),(0xa00aea2e,1),
 (0xa00aea7a,3),(0xa00aef94,4),(0xa00aefaa,3),(0xa00af002,4),(0xa00af01c,3)]:
 h=int.from_bytes(raws[a],'little')
 yes(a,'C.LI value',[h&3,h>>13,sx(((h>>12&1)<<5)|(h>>2&31),6)],[1,2,value])

result=dict(scope='Q-01 same S production and later mask writes; static only',source=str(SOURCE),
 evidence_id=record['evidence_id'],profile=record['analysis_profile'],
 windows=[dict(start=hex(a),end_exclusive=hex(b)) for a,b in windows],
 bytes=sum(b-a for a,b in windows),instruction_count=len(rows),checks=checks,
 check_count=len(checks),instructions=rows,
 limitations=record['normalized_result']['limitations'])
# Necessary intervening same-S indicator helper: inventory next entry bounds it.
# Store/call-only boundary evidence, not a new full drawing implementation export.
with (ROOT/'roms/0041/ap01-1.0.2_0041.bin').open('rb') as rom:
 rom.seek(0xa00b2a48-BASE)
 helper_bytes=rom.read(0x322)
helper=list(md.disasm(helper_bytes,0xa00b2a48))
assert sum(i.size for i in helper)==802
stores=[];calls=[]
for i in helper:
 if i.mnemonic in ('sb','sh','sw','c.sw','c.swsp'):
  assert '(s0)' in i.op_str or '(sp)' in i.op_str,(hex(i.address),i.op_str)
  stores.append(dict(address=hex(i.address),raw=i.bytes.hex(),decoded=i.mnemonic+' '+i.op_str))
 if i.mnemonic=='jal':
  t=(i.address+int(i.op_str,0))&0xffffffff
  assert t in (0xa00dfc1e,0xa019d0e6)
  calls.append(dict(address=hex(i.address),target=hex(t),raw=i.bytes.hex()))
 assert i.mnemonic not in ('jalr','c.jalr')
 if i.mnemonic=='c.jr':assert i.op_str=='ra'
result['intervening_indicator_helper']=dict(start='0xa00b2a48',end_exclusive='0xa00b2d6a',
 source='Original ROM, local Capstone '+capstone.__version__+'; old list_procedures next-entry boundary',
 inventory_evidence_id='ev_50cdbf92a7c9800e4d4bc140d70fa8cd1509eca7a199cfd6050d483cf7d695b2',
 bytes=802,instruction_count=len(helper),stores=stores,calls=calls,
 limitation='Direct stores/calls only; public style implementations stopped at API boundary; no new REA evidence ID')
ctor=next(r for r in bundle['records'] if r.get('parameters',{}).get('procedure')=='0xa005cc1e')
ctor_rows=[]
with (ROOT/'roms/0041/ap01-1.0.2_0041.bin').open('rb') as rom:
 for lo,hi in [(0xa005d1a2,0xa005d1ae),(0xa005d66a,0xa005d68a),(0xa005d73c,0xa005d74c),(0xa005da4a,0xa005da78)]:
  rom.seek(lo-BASE);raw=rom.read(hi-lo);seq=list(md.disasm(raw,lo))
  assert sum(i.size for i in seq)==hi-lo
  ctor_rows.extend(dict(address=hex(i.address),raw=i.bytes.hex(),decoded=i.mnemonic+' '+i.op_str) for i in seq)
first=next(x for x in ctor_rows if x['address']=='0xa005d1a2')
assert first['decoded']=='addi a0, zero, 0x10c'
call=int.from_bytes(bytes.fromhex(next(x['raw'] for x in ctor_rows if x['address']=='0xa005d1a6')),'little')
delta=((call>>31)<<20)|((call>>12&255)<<12)|((call>>20&1)<<11)|((call>>21&1023)<<1)
assert (0xa005d1a6+sx(delta,21))&0xffffffff==0xa008e362
result['constructor_initial_state']=dict(evidence_id=ctor['evidence_id'],profile=ctor['analysis_profile'],
 instructions=ctor_rows,bytes=106,
 inherited_zero_alloc_contract='app-history-review-01-0041-20261024.md: a008e362 successful allocation zero-fills original requested size',
 limitation='Same-S caller/visible initializer stores only; no new allocator/library analysis or proof against reentrancy')
result['indicator_argument_snapshot_correction'] = verify_snapshot()
(OUT/'audit.json').write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n',encoding='utf8')
print(json.dumps({k:result[k] for k in ('bytes','instruction_count','check_count')}))
print(json.dumps(dict(indicator_bytes=802,instructions=len(helper),stack_stores=len(stores),direct_calls=len(calls))))
