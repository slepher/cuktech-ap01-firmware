"""Independent C02 offline review: read ROM, write this task directory only."""
import json
from pathlib import Path
from capstone import Cs, CS_ARCH_RISCV, CS_MODE_RISCV32, CS_MODE_RISCVC
HERE=Path(__file__).resolve().parent
ROOT=HERE.parents[2]
BASE=0x9ffff000
rom=Path('D:/Documents/PlatformIO/Projects/cuktech-ap01-firmware/roms/0041/ap01-1.0.2_0041.bin').read_bytes()
prior=json.loads((ROOT/'reverse/analysis/pogo-timer-lifecycle-c01-0041-20261023/instruction-evidence.json').read_text())
init=json.loads((ROOT/'reverse/analysis/factory-test-0041-20261023/retained-initializer.json').read_text())['function']
cb=json.loads((ROOT/'reverse/analysis/dock-presence-polling-0041-20261023/retained-functions.json').read_text())['functions'][1]
cs=Cs(CS_ARCH_RISCV,CS_MODE_RISCV32|CS_MODE_RISCVC)
def raw(pc,n):return rom[pc-BASE:pc-BASE+n]
def signed(v,n):return v-(1<<n) if v>>(n-1) else v
def jal_imm(v):return signed(((v>>31)<<20)|(((v>>12)&255)<<12)|(((v>>20)&1)<<11)|(((v>>21)&1023)<<1),21)
def cj_imm(v):return signed((((v>>12)&1)<<11)|(((v>>11)&1)<<4)|(((v>>9)&3)<<8)|(((v>>8)&1)<<10)|(((v>>7)&1)<<6)|(((v>>6)&1)<<7)|(((v>>3)&7)<<1)|(((v>>2)&1)<<5),12)
windows=[]
for w in prior['windows']:
 lines=[]
 for old in w['instructions']:
  pc=int(old['address'],16); b=raw(pc,len(bytes.fromhex(old['hex'])))
  assert b.hex()==old['hex']
  ins=next(cs.disasm(b,pc),None);assert ins and ins.size==len(b)
  assert ins.mnemonic+' '+ins.op_str==old['decode']
  lines.append(old)
 windows.append(dict(name=w['name'],start=w['start'],end_exclusive=w['end_exclusive'],instructions=lines))
search=[]
for label,record,asm in [('initializer',init,init['assembly']),('callback',cb,cb['normalized_result']['assembly'])]:
 for r in record['raw_ranges']:
  assert raw(int(r['start'],16),len(bytes.fromhex(r['hex'])))==bytes.fromhex(r['hex'])
 pcs=[int(s.split(':')[0],16) for s in asm]
 calls=[]; transfers=[]; unresolved=[]
 for i,pc in enumerate(pcs):
  v=int.from_bytes(raw(pc,4),'little');h=v&65535
  size=4 if h&3==3 else 2
  if i+1<len(pcs):assert pcs[i+1]==pc+size
  target=None;kind=None;rd=None
  if size==4 and v&127==0x6f:
   target=(pc+jal_imm(v))&0xffffffff;rd=(v>>7)&31;kind='jal'
  elif size==2 and h&0xe003 in (0x2001,0xa001):
   target=(pc+cj_imm(h))&0xffffffff;rd=1 if h&0xe003==0x2001 else 0;kind='c.jal' if rd else 'c.j'
  elif size==4 and v&127==0x17 and i+1<len(pcs) and pcs[i+1]==pc+4:
   nxt=int.from_bytes(raw(pc+4,4),'little');reg=(v>>7)&31
   if nxt&0x707f==0x67 and (nxt>>15)&31==reg:
    target=(pc+signed(v&0xfffff000,32)+signed(nxt>>20,12))&0xfffffffe;rd=(nxt>>7)&31;kind='adjacent_auipc_jalr'
  if target is not None:
   item=dict(site=hex(pc),kind=kind,rd=rd,target=hex(target));transfers.append(item)
   if rd in (1,5):calls.append(item)
  if (size==4 and v&0x707f==0x67) or (size==2 and h&0xf07f in (0x8002,0x9002)):
   unresolved.append(hex(pc))
 search.append(dict(body=label,boundary_source='retained assembly addresses; contiguous instruction sizes checked, vendor semantics not redecoded',start=hex(pcs[0]),end_exclusive=hex(pcs[-1]+(4 if int.from_bytes(raw(pcs[-1],2),'little')&3==3 else 2)),call_count=len(calls),compressed_direct_calls=[x for x in calls if x['kind']=='c.jal'],known_delete_calls=[x for x in calls if x['target']=='0xa008ae58'],known_delete_transfers=[x for x in transfers if x['target']=='0xa008ae58'],indirect_sites_not_all_resolved=unresolved,calls=calls))
result=dict(task='C02',review='accepted_with_naming_clarification',windows=windows,bounded_raw_search=search,checks=dict(window_bytes=sum(len(bytes.fromhex(x['hex'])) for w in windows for x in w['instructions']),windows_match_original_rom=True,selected_decode_matches_C01=True,retained_raw_ranges_match_rom=True,firmware_executed=False),limitations=['No independent whole-function boundary rediscovery or vendor instruction model validation.','Unresolved indirect targets and wrappers may reach delete; no global lifecycle conclusion.','RAM state and timer scheduling never observed.'])
(HERE/'review-evidence.json').write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
print(json.dumps(dict(checks=result['checks'],search=[{k:v for k,v in s.items() if k not in ('calls','indirect_sites_not_all_resolved')} for s in search]),ensure_ascii=False,indent=2))
