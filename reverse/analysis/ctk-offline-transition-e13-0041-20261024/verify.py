"""E13 bounded retained-source and ROM checks; never executes firmware."""
import json
from pathlib import Path
from capstone import Cs, CS_ARCH_RISCV, CS_MODE_RISCV32, CS_MODE_RISCVC
MAIN=Path('D:/Documents/PlatformIO/Projects/cuktech-ap01-firmware')
HERE=Path(__file__).resolve().parent
old=MAIN/'reverse/rehost'
charge=json.loads((old/'charge-0041-round4.json').read_text(encoding='utf-8'))
reset=charge['records'][4]
assert reset['parameters']=={'procedure':'0xa00ef1d4'}
assert reset['procedure']['body']['ranges']==[{'start':'0xa00ef1d4','end':'0xa00ef2d9'}]
bundle=json.loads((MAIN/'evidence/rea-0041-20261017/evidence/whole-rom-private-20261023.evidence.json').read_text(encoding='utf-8'))
callback=next(r for r in bundle['records'] if r.get('parameters',{}).get('procedure')=='0xa00adabc')
rom=(MAIN/'roms/0041/ap01-1.0.2_0041.bin').read_bytes(); base=0x9ffff000
cs=Cs(CS_ARCH_RISCV,CS_MODE_RISCV32|CS_MODE_RISCVC)
by={}
for r in (reset,callback):
 n=r.get('normalized_result',r)
 by.update({int(s.split(':')[0],16):s.split(': ',1)[1] for s in n['assembly']})
anchors={
0xa00adc3a:'beq a4, a5, 0xa00adcd0',0xa00adc3e:'bne a5, zero, 0xa00ae196',
0xa00ae196:'lw a5, -0xd4, s0',0xa00ae19a:'bne a5, zero, 0xa00adcc4',
0xa00ae20a:'sb zero, 0x36, a5',0xa00ae20e:'sb zero, 0x3b, a5',
0xa00ae22a:'lw s9, 0x4, a5',0xa00ae238:'jal ra, 0xa00f4740',
0xa00ae242:'jal ra, 0xa00ef1d4',0xa00ae24c:'jal ra, 0xa00ef2da',
0xa00ae3a6:'c.li a1, 0x2',0xa00ae3a8:'c.j 0xa00ae234',
0xa00ef1f0:'c.mv s4, a1',0xa00ef1f2:'addi s2, a1, 0x10',
0xa00ef1f6:'addi s1, a0, 0x20',0xa00ef1fa:'addi s3, a0, 0xa0',
0xa00ef1fe:'addi s7, a1, 0x50',0xa00ef210:'lbu a5, 0xe, s2',
0xa00ef214:'bne a5, s6, 0xa00ef288',0xa00ef21c:'jal ra, 0xa00f4610',
0xa00ef220:'lbu a3, 0x6, s4',0xa00ef22e:'jal ra, 0xa00f44e8',
0xa00ef238:'jal ra, 0xa00ef0ec',0xa00ef23c:'sb s6, 0x0, s3',
0xa00ef240:'c.addi s2, 0x10',0xa00ef242:'addi s1, s1, 0x20',
0xa00ef246:'c.addi s3, 0x1',0xa00ef248:'bne s2, s7, 0xa00ef210',
0xa00ef2be:'jal ra, 0xa0091b3a',0xa00ef2d0:'jal ra, 0xa019d0e6',
0xa00ef2d4:'sb zero, 0x0, s3',0xa00ef2d8:'c.j 0xa00ef240'}
checks=[]
for pc,expected in anchors.items():
 assert by[pc]==expected,(hex(pc),by[pc])
 raw=rom[pc-base:pc-base+4];size=4 if raw[0]&3==3 else 2
 ins=next(cs.disasm(raw[:size],pc));assert ins.size==size
 # Capstone aliases use different register names and PC-relative compressed operands;
 # independently check instruction kind, then branch/call targets below.
 assert {'bnez':'bne'}.get(ins.mnemonic,ins.mnemonic)==expected.split()[0],(hex(pc),ins.mnemonic,expected)
 if ins.mnemonic in ('jal','beq','bne','bnez'):
  assert pc+int(ins.op_str.split(',')[-1],0)==int(expected.split()[-1],0)
 if ins.mnemonic=='c.j':assert pc+int(ins.op_str,0)==int(expected.split()[-1],0)
 checks.append({'address':hex(pc),'file_offset':pc-base,'hex':raw[:size].hex(),'retained_assembly':expected})
# These selected blocks are entirely standard instructions; prove their boundaries.
spans=[(0xa00adc32,0xa00adc46),(0xa00ae196,0xa00ae1c8),(0xa00ae1e8,0xa00ae250),(0xa00ae36e,0xa00ae3aa),(0xa00ef1d4,0xa00ef2da)]
count=0
for start,end in spans:
 ins=list(cs.disasm(rom[start-base:end-base],start))
 assert sum(i.size for i in ins)==end-start
 assert all(i.address in by for i in ins)
 count+=len(ins)
assert rom[0xa0607610-base:0xa0607610-base+3]==b'--\x00'
# No view stores except saved incoming registers/local color; caller passes borrowed view.
# Full store/call list is reviewed at the original record, not re-exported.
search=[]
for name in ['charge-complete-0041.json','charge-0041-round4.json','page-logic-0041.json','page-logic-evidence.json','page-logic-evidence2.json']:
 t=(old/name).read_text(encoding='utf-8').lower()
 search.append({'source':name,'address_hits':{a:t.count(a) for a in ['a00adabc','a00ef1d4','a00ef2da']}})
host=json.loads((HERE.parent/'screen-host-append-20261020.json').read_text(encoding='utf-8'))
slider=next(r for r in host['functions'] if r['procedure']=='0xa00b3106')
assert slider['body']['total_bytes']==332
assert slider['evidence_id']=='ev_182941f3e3fa2b7a776b17694b73e08f88952c81a3f8a48af0f4513bc5808b76'
guide=json.loads((old/'guide-complete-0041.json').read_text(encoding='utf-8'))
assert 'guide' in guide and 'hooks' in guide
round3=list((MAIN/'evidence/rea-0041-20261017/round3/evidence').glob('*.json'))
hits=[]
for p in round3:
 if p.stat().st_size>5000000:continue
 t=p.read_text(encoding='utf-8').lower()
 if 'a00ef1d4' in t or 'a00adabc' in t:hits.append(p.name)
result={'status':'PASS','new_business_recovery':0,'source_records':[{'source':'charge-0041-round4.json records[4]','evidence_id':reset['evidence_id']},{'source':'whole-rom-private-20261023.evidence.json callback','evidence_id':callback['evidence_id']}], 'source_search':search,'reused_slider_evidence':slider['evidence_id'],'guide_scope':'guide/hooks are reconstruction, not native slider ABI','round3_json_count':len(round3),'round3_address_hits':hits,'checked_boundary_instruction_count':count,'anchors':checks,'literal':{'address':'0xa0607610','bytes':'2d2d00','text':'--'},'limits':['Retained semantic reuse plus local standard-instruction checks; not new function recovery or full callback certification.','No execution, model change, provider opening, global aliases or physical display proof.']}
(HERE/'static-checks.json').write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
print('PASS',len(checks),'anchors;',count,'bounded instructions;',len(round3),'round3 JSON candidates; new recovery 0')
