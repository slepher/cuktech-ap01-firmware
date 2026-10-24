"""P-07 read-only ROM/retained checks. No firmware execution or input model."""
import json, re
from pathlib import Path
from capstone import Cs, CS_ARCH_RISCV, CS_MODE_RISCV32, CS_MODE_RISCVC
MAIN=Path('D:/Documents/PlatformIO/Projects/cuktech-ap01-firmware')
HERE=Path(__file__).resolve().parent
SOURCE='evidence/rea-0041-20261017/evidence/whole-rom-private-20261023.evidence.json'
bundle=json.loads((MAIN/SOURCE).read_text(encoding='utf8'))
records={r.get('parameters',{}).get('procedure'):r for r in bundle['records']}
rom=(MAIN/'roms/0041/ap01-1.0.2_0041.bin').read_bytes();BASE=0x9ffff000
cs=Cs(CS_ARCH_RISCV,CS_MODE_RISCV32|CS_MODE_RISCVC)
checks=[];windows=[]
def add(label,start,end,procedure):
 r=records[procedure]; asm={int(s.split(':')[0],16):s.split(': ',1)[1] for s in r['normalized_result']['assembly']}
 out=[];pc=start
 for ins in cs.disasm(rom[start-BASE:end-BASE],start):
  assert ins.address==pc and ins.address in asm
  retained=asm[pc];kind=retained.split()[0]
  assert {'bnez':'bne','beqz':'beq','li':'addi','not':'xori'}.get(ins.mnemonic,ins.mnemonic)=={'bnez':'bne','beqz':'beq','li':'addi','not':'xori'}.get(kind,kind),(hex(pc),ins.mnemonic,retained)
  if ins.mnemonic in ('jal','beq','bne','bnez','beqz','bltu','bgeu','blt','bge','c.j','c.beqz','c.bnez'):
   target=pc+int(ins.op_str.split(',')[-1],0);expected=int(retained.split()[-1],0)
   assert target==expected,(hex(pc),hex(target),retained)
   checks.append({'address':hex(pc),'kind':'direct_target','target':hex(target)})
  out.append({'address':hex(pc),'file_offset':pc-BASE,'hex':ins.bytes.hex(),'retained_assembly':retained,'capstone':ins.mnemonic+' '+ins.op_str})
  pc+=ins.size
 assert pc==end,(label,hex(pc),hex(end))
 windows.append({'label':label,'start':hex(start),'end_exclusive':hex(end),'source':SOURCE,'procedure':procedure,'evidence_id':r['evidence_id'],'instructions':out})
add('offline_tail',0xa00ae250,0xa00ae340,'0xa00adabc')
add('remaining_state_direct_callback',0xa00ae3aa,0xa00ae3b4,'0xa00adabc')
add('state_save_merge',0xa00adcba,0xa00adce0,'0xa00adabc')
add('port_bit_shift_identity',0xa00ae1b6,0xa00ae1c8,'0xa00adabc')
add('timer_userdata',0xa00ad602,0xa00ad620,'0xa00ad602')
add('timer_constructor_alias',0xa005da14,0xa005da78,'0xa005cc1e')
add('global_base',0xa00adc08,0xa00adc10,'0xa00adabc')
add('global_rebase',0xa00adc2c,0xa00adc46,'0xa00adabc')
# Minimal original operands substantiate width, pointer source, argument preservation and order.
anchors={
0xa00ae1ba:'addi s11, s8, 0x1',0xa00adc36:'addi s4, s4, 0x2c',
0xa00ae250:'c.li a1, 0x0',0xa00ae252:'c.mv a0, s6',0xa00ae25a:'lw s9, 0x4, a5',
0xa00ae25e:'lbu a4, 0x9c, s9',0xa00ae266:'sra a4, a4, s11',
0xa00ae282:'sll a4, a2, s11',0xa00ae290:'sb a4, 0x9c, s9',0xa00ae294:'sb a2, 0x9d, a3',
0xa00ae298:'sb zero, 0x101, a3',0xa00ae29c:'sb zero, 0xfc, a3',
0xa00ae2a2:'andi a3, s8, 0xff',0xa00ae2d8:'andi a4, a4, 0xff',
0xa00ae2ea:'lw a0, 0xf4, s9',0xa00ae2ee:'c.lw a4, 0x14, a0',
0xa00ae328:'sb zero, 0x28, a5',0xa00ae32c:'sh zero, 0xfa, s9',
0xa00ad61e:'c.lw s1, 0xc, a0',0xa005da14:'addi s3, s2, 0x80',
0xa005da50:'c.mv a2, s2',0xa005da5e:'sw a0, 0x74, s3',0xa005da6c:'sw s2, 0x4, s7'}
by={int(i['address'],16):i for w in windows for i in w['instructions']}
for pc,expected in anchors.items():
 assert by[pc]['retained_assembly']==expected,(hex(pc),by[pc])
 checks.append({'address':hex(pc),'kind':'operand_anchor','expected':expected})
# Existing plain Capstone record for only helper modes reached by this caller.
OLD='reverse/rehost/system-complete-0041.json'
old=json.loads((MAIN/OLD).read_text(encoding='utf8'));rows=old['local_disassembly']['0xa00ad486']
assert old['source']['sha256']=='972db4c136c7ed9e24a83c07c1a7fd62040ca018b08ca285216d26b1fee3c6b9'
spans=[(0xa00ad486,0xa00ad4da),(0xa00ad4e6,0xa00ad522),(0xa00ad550,0xa00ad58c),(0xa00ad5ba,0xa00ad5c6),(0xa00ad5de,0xa00ad5ee)]
for lo,hi in spans:
 out=[]
 for r in rows:
  pc=int(r['address'],16)
  if not lo<=pc<hi:continue
  b=bytes.fromhex(r['bytes']);assert rom[pc-BASE:pc-BASE+len(b)]==b
  ins=list(cs.disasm(b,pc));assert len(ins)==1 and ins[0].size==len(b)
  assert ins[0].mnemonic+' '+ins[0].op_str==r['instruction'],(r,ins[0].mnemonic,ins[0].op_str)
  out.append({'address':hex(pc),'hex':b.hex(),'capstone':r['instruction']})
 assert sum(len(bytes.fromhex(x['hex'])) for x in out)==hi-lo
 windows.append({'label':'summary_helper_selected_modes','start':hex(lo),'end_exclusive':hex(hi),'source':OLD,'profile':'Local Capstone5.0.7; no REA profile claimed','instructions':out})
# Direct JAL arguments are manually traced above; independently decode their destinations.
expected_calls={0xa00ae254:0xa00dcee4,0xa00ae278:0xa00d8f7c,0xa00ae2aa:0xa00ad486,0xa00ae2b8:0xa00ad486,0xa00ae2e6:0xa00ad486,0xa00ae2f4:0xa008bd16,0xa00ae3ae:0xa00ad602,0xa005da5a:0xa008bc64,0xa005da62:0xa008bd16}
for pc,dst in expected_calls.items():
 x=next(cs.disasm(rom[pc-BASE:pc-BASE+4],pc));assert x.mnemonic=='jal' and pc+int(x.op_str.split(',')[-1],0)==dst
 checks.append({'address':hex(pc),'kind':'call_target','target':hex(dst)})
profiles=[]
for a in ['0xa00adabc','0xa00ad602','0xa005cc1e']:
 r=records[a];p=r['analysis_profile'];assert p['parameters']['language_id']=='RISCV:LE:32:ap01thead2'
 assert p['digest']=='b6368dd18431e8113aa5026c713d41e648ab0f6ddd9421ff6c4a49e23b3cd2f3'
 profiles.append({'procedure':a,'evidence_id':r['evidence_id'],'provider':r['provider'],'language':p['parameters']['language_id'],'profile_digest':p['digest']})
result={'status':'PASS','identity':old['source']['sha256'],'base':hex(BASE),'profiles':profiles,'checks':checks,'windows':windows,'limits':['Static ROM and retained evidence only; no execution or input model.','Capstone operand anchors plus manual register/CFG review are not complete dataflow proof.','Timer callback internals, actual schedule and full application lifecycle not certified.','Helper selected modes reuse old local Capstone record; not Ghidra ap01thead2 attribution.']}
(HERE/'evidence.json').write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n',encoding='utf8')
summary={'status':'PASS','windows':len(windows),'bytes':sum(int(w['end_exclusive'],16)-int(w['start'],16) for w in windows),'instructions':sum(len(w['instructions']) for w in windows),'checks':len(checks),'new_business_functions':0,'note':'Newly certified caller-stage contract from retained bodies; no fresh function extraction.'}
(HERE/'checks.json').write_text(json.dumps(summary,indent=2)+'\n',encoding='utf8');print(summary)
