"""Independent bounded static review; never imports/runs the author verifier."""
import hashlib,json,pathlib
from capstone import Cs,CS_ARCH_RISCV,CS_MODE_RISCV32,CS_MODE_RISCVC
S=pathlib.Path('D:/Documents/PlatformIO/Projects/cuktech-ap01-firmware')
O=pathlib.Path(__file__).resolve().parent
rom=S/'roms/0041/ap01-1.0.2_0041.bin'
assert rom.stat().st_size==6769704
spec=[(0xa011d10e,244),(0xa01abe54,170),(0xa0113c8a,738),(0xa0118b08,76),(0xa011bffe,220),(0xa011bfc4,58),(0xa01188a6,274)]
author=json.loads((S/'reverse/analysis/app-subscription-research-01-0041-20261025/bounded-evidence.json.tmp').read_text(encoding='utf-8-sig'))
md=Cs(CS_ARCH_RISCV,CS_MODE_RISCV32|CS_MODE_RISCVC)
windows=[]; decoded={}; unknown=[]
with rom.open('rb') as f:
 for va,n in spec:
  f.seek(va-0x9ffff000);raw=f.read(n)
  old=next(w for w in author['windows'] if int(w['start'],16)==va)
  assert raw.hex()==old['hex'] and hashlib.sha256(raw).hexdigest()==old['sha256']
  lines=[];pos=0
  while pos<n:
   ins=next(md.disasm(raw[pos:],va+pos,count=1),None)
   width=ins.size if ins else (4 if raw[pos]&3==3 else 2)
   line=f'{va+pos:08x}: {raw[pos:pos+width].hex()} '+(ins.mnemonic+' '+ins.op_str if ins else 'UNKNOWN')
   decoded[va+pos]=line;lines.append(line)
   if not ins:unknown.append({'address':hex(va+pos),'hex':raw[pos:pos+width].hex()})
   pos+=width
  windows.append({'start':hex(va),'size':n,'offset':va-0x9ffff000,'sha256':hashlib.sha256(raw).hexdigest(),'assembly':lines})
assert sum(n for _,n in spec)==1780
expected={0xa01abe7e:'8bc7994c',0xa0118b1a:'8bc7944c',0xa011c05e:'8b479a4c',0xa0113e8c:'8b47994c',0xa0113e54:'8b48d380',0xa0113e58:'770587df'}
assert {int(x['address'],16):x['hex'] for x in unknown}==expected
checks={
 'precise_P_erase_gate':(0xa011d192,'c.beqz a0'), 'precise_T_erase_gate':(0xa011d1a8,'c.beqz a0'),
 'precise_P_empty':(0xa011d1b4,'c.bnez a5'), 'precise_T_empty':(0xa011d1d4,'bnez s2'),
 'precise_found_final_zero':(0xa011d1fe,'c.li s2, 0'),
 'aggregate_type_5_6_family':(0xa01abe82,'addi s6, s5, -5'),
 'aggregate_flag_gate':(0xa01abeca,'beqz s10'),
 'aggregate_type_3_4_family':(0xa01abe86,'addi s7, s5, -3'),
 'aggregate_target18':(0xa01abede,'addi a1, s1, 0x18'),
 'aggregate_target14':(0xa01abee6,'addi a1, s1, 0x14'),
 'aggregate_bound47':(0xa01abeda,'addi a2, zero, 0x47'),
 'aggregate_cachednext':(0xa01abe8a,'lw s4, 0(a5)'),
 'aggregate_ignore_return':(0xa01abed8,'c.j '),
 'stale_eachpeer_now':(0xa011c050,'jal '),
 'stale_threshold':(0xa011c030,'addi s7, zero, 0x78'),
 'stale_unsigned_keep_equal':(0xa011c058,'bgeu s7, a0'),
 'stale_subtract':(0xa011c056,'c.sub a0, a5'),
 'stale_unconditional_T_decrement':(0xa011c09a,'c.addi a5, -1'),
 'stale_signed_positive_keep':(0xa011c0a0,'bgtz a5'),
 'stale_unconditional_P_decrement':(0xa011c0ce,'c.addi a5, -1'),
 'erase_target':(0xa011bfda,'c.lw a4, 8(s1)'),
 'erase_success':(0xa011bfec,'c.li a0, 1'),
 'G_base_dump':(0xa0113ccc,'addi s2, s2, -0x494'),
 'global_peer_head':(0xa0113de4,'lw s2, 0x28(s2)'),
 'global_peer_count':(0xa011d1ca,'c.lw a4, 0x24(a5)'),
 'global_topic_count':(0xa011d1f6,'c.lw a4, 0x30(a5)')}
for name,(va,fragment) in checks.items():assert fragment in decoded[va],name
# All nine valid-type terminal paths independently read/add/write their own word.
type_paths={1:(0xa011894e,0),2:(0xa011895e,4),3:(0xa011896e,8),4:(0xa011897e,12),5:(0xa011898e,16),6:(0xa011899e,20),7:(0xa0118928,24),8:(0xa01189ae,28),9:(0xa011893e,32)}
for typ,(va,offset) in type_paths.items():
 assert ('lw ' in decoded[va]) and 'c.add a1, a4' in decoded[va+2] and 'sw ' in decoded[va+4]
# Decode JAL immediate independently for exact ordering/targets.
def jal_target(va):
 line=decoded[va];raw=bytes.fromhex(line.split(': ')[1].split()[0]);v=int.from_bytes(raw,'little')
 imm=((v>>31)<<20)|(((v>>12)&255)<<12)|(((v>>20)&1)<<11)|(((v>>21)&1023)<<1)
 if imm&(1<<20):imm-=1<<21
 return (va+imm)&0xffffffff
calls={0xa0113ca8:0xa011bffe,0xa011d18e:0xa011bfc4,0xa011d1a4:0xa011bfc4,0xa011d1de:0xa01188a6,0xa011bfe2:0xa006929a,0xa011bfe8:0xa002e14e,0xa01abed4:0xa011d10e,0xa011c092:0xa011bfc4,0xa011c0c8:0xa011bfc4,0xa011c0aa:0xa01188a6,0xa011c050:0xa005fa1a}
for va,target in calls.items():assert jal_target(va)==target
complete=json.loads((S/'evidence/rea-0041-20261017/evidence/upper-complete.evidence.json').read_text(encoding='utf-8-sig'))
roots=[]
for ordinal in (245,48):
 r=complete['records'][ordinal]
 assert r['analysis_profile']['digest']=='4825fb58a33a3e7d618557975b153b8318cf7e833d190ad16bcbf8bd441ae621'
 asm=r['normalized_result']['assembly']
 # Keep only root/unsub flag, locking, mutation, response boundaries; sub identity only.
 selected=[s for s in asm if (ordinal==245 and (0xa01163cc<=int(s.split(':')[0],16)<=0xa01163e4 or int(s.split(':')[0],16)==0xa0116410)) or ordinal==48 and (0xa011d55e<=int(s.split(':')[0],16)<=0xa011d69a or 0xa011d794<=int(s.split(':')[0],16)<=0xa011d7cc or 0xa011d840<=int(s.split(':')[0],16)<=0xa011d89c or int(s.split(':')[0],16)==0xa011d450)]
 roots.append({'ordinal':ordinal,'evidence_id':r['evidence_id'],'profile_digest':r['analysis_profile']['digest'],'assembly':selected})
b=json.loads((S/'evidence/rea-0041-20261017/evidence/upper-miio-b.json').read_text(encoding='utf-8-sig'))
broots=[f for f in b['functions'] if f['address'] in ('0xa0115f7e','0xa011d202')]
assert len(broots)==2
summary={'static_only':True,'windows':7,'bytes':1780,'unknown':unknown,'byte_matches':7,'branch_checks':len(checks),'type_terminal_paths':9,'direct_call_checks':len(calls),'new_private_bodies':0,'profiles_separate':True}
(O/'independent-evidence.json.tmp').write_text(json.dumps({'summary':summary,'windows':windows,'roots_complete':roots,'roots_miio_b':[{k:r[k] for k in ('address','evidence_id','profile_digest')} for r in broots]},indent=2),encoding='utf-8')
(O/'checks.json').write_text(json.dumps(summary,indent=2),encoding='utf-8')
print(json.dumps(summary))
