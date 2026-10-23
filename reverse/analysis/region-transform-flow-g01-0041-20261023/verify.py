"""Static G01 evidence extraction; no target/model execution or old verifier replay."""
from pathlib import Path
import json, re
import capstone
from capstone import Cs, CS_ARCH_RISCV, CS_MODE_RISCV32, CS_MODE_RISCVC
HERE=Path(__file__).resolve().parent
SOURCE=Path('D:/Documents/PlatformIO/Projects/cuktech-ap01-firmware')
E=SOURCE/'evidence/rea-0041-20261017'
BASE=0x9ffff000
ROM=SOURCE/'roms/0041/ap01-1.0.2_0041.bin'
rom=ROM.read_bytes()
md=Cs(CS_ARCH_RISCV,CS_MODE_RISCV32|CS_MODE_RISCVC)
model_path=E/'ghidra/Ghidra/Processors/RISCV/data/languages/ap01thead2.sinc'
model=model_path.read_text()
reg_path=model_path.with_name('ap01thead2.reg.sinc')
reg_model=reg_path.read_text()
checks=[]; rows={}; used_models={}
def check(name,actual,expected):
 assert actual==expected,(name,actual,expected)
 checks.append(dict(name=name,actual=actual,expected=expected))
def sx(x,b):return x-(1<<b) if x>>(b-1) else x
def raw(a,n):return rom[a-BASE:a-BASE+n]
def target(a,n,x):
 if n==4 and x&127==111:return a+sx((x>>31<<20)|((x>>12&255)<<12)|((x>>20&1)<<11)|((x>>21&1023)<<1),21)
 if n==4 and x&127==99:return a+sx((x>>31<<12)|((x>>7&1)<<11)|((x>>25&63)<<5)|((x>>8&15)<<1),13)
 if n==2 and x&3==1:
  k=x>>13
  if k in (6,7):return a+sx(((x>>12&1)<<8)|((x>>5&3)<<6)|((x>>2&1)<<5)|((x>>10&3)<<3)|((x>>3&3)<<1),9)
  if k in (1,5):return a+sx(((x>>12&1)<<11)|((x>>8&1)<<10)|((x>>9&3)<<8)|((x>>6&1)<<7)|((x>>7&1)<<6)|((x>>2&1)<<5)|((x>>11&1)<<4)|((x>>3&7)<<1),12)
def vendor(x):
 rd=x>>7&31; f=x>>12&7; r1=x>>15&31; r2=x>>20&31; f7=x>>25; top=x>>27; shift=x>>25&3
 fields=dict(opcode=x&127,rd=rd,funct3=f,rs1=r1,rs2=r2,funct7=f7)
 assert x&127==11
 if f==1 and f7 in (16,17,32,33):
  name={16:'mula',17:'muls',32:'mveqz',33:'mvnez'}[f7]; key=f':th.{name} '; asm=f'th.{name} x{rd},x{r1},x{r2}'
 elif f==1 and top==0:
  key=':th.addsl '; asm=f'th.addsl x{rd},x{r1},x{r2},{shift}'; fields['shift']=shift
 elif f in (2,3):
  msb=x>>26;lsb=x>>20&63; name='ext' if f==2 else 'extu'; key=f':th.{name} rd,rs1,{msb},{lsb} '; asm=f'th.{name} x{rd},x{r1},{msb},{lsb}'; fields.update(msb=msb,lsb=lsb)
 elif f in (4,5) and top in (8,9,20,16):
  name={(4,8):'lrw',(5,8):'srw',(4,9):'lwib',(5,9):'swib',(4,20):'lrhu',(4,16):'lrbu'}[(f,top)]
  key=f':th.{name} '; immediate= sx(r2,5) if top==9 else r2
  asm=f'th.{name} x{rd},x{r1},'+(str(immediate) if top==9 else 'x'+str(r2))+f',{shift}'; fields.update(shift=shift,index_or_immediate=immediate)
 else:raise ValueError(hex(x))
 start=model.index(key); end=model.index('}',start)+1
 used_models[key]=dict(line=model[:start].count('\n')+1,text=model[start:end])
 return asm,fields,key
wanted=[0xa00dca48,0xa00dc9ba,0xa00dc862,0xa0083796,0xa019dfd0,0xa019dff0,0xa00dc658,0xa00dc070,0xa00dc020,0xa0089e10,0xa0089d76]
queue=json.loads((E/'whole-rom-graph-queue-20261023.json').read_text())['commands']
records={}
for i,c in enumerate(queue):
 p=c['arguments']['procedure']
 if p.startswith('0x') and int(p,16) in wanted:
  path=E/f'evidence/whole-rom-graph-20261023-{i:03d}.json'
  j=json.loads(path.read_text());j=json.loads(j['content'][0]['text'])
  records[(int(p,16),c['name'])]=dict(file=str(path),evidence_id=j['evidence_id'],normalized_result=j['normalized_result'])
windows=[]
for entry in wanted:
 info=records[(entry,'procedure_info')]; body=info['normalized_result']['body']
 check(f'{entry:#x} contiguous inventory',body['non_contiguous'],False)
 r=body['ranges'][0]; windows.append(dict(entry=hex(entry),start=r['start'],end_exclusive=hex(int(r['end'],16)+1),kind='core',inventory=info,callee_inventory=records[(entry,'procedure_callees')]))
# Only the two already-reviewed caller contract windows and signed intersection dependency.
for start,end in [(0xa00ddb14,0xa00ddb26),(0xa00ddb60,0xa00ddb84),(0xa00892f4,0xa008934a)]:
 windows.append(dict(start=hex(start),end_exclusive=hex(end),kind='caller contract'))
for w in windows:
 pc=int(w['start'],16);end=int(w['end_exclusive'],16);insns=[]
 while pc<end:
  n=4 if int.from_bytes(raw(pc,2),'little')&3==3 else 2;b=raw(pc,n);x=int.from_bytes(b,'little')
  r=dict(address=hex(pc),file_offset=pc-BASE,bytes=b.hex())
  if n==4 and x&127==11:r['assembly'],r['vendor_fields'],r['model_key']=vendor(x)
  else:
   ii=list(md.disasm(b,pc)); assert len(ii)==1 and ii[0].size==n,hex(pc)
   r['assembly']=ii[0].mnemonic+' '+ii[0].op_str
  t=target(pc,n,x)
  if t is not None:r['target']=hex(t)
  r['direct_call']=(n==4 and x&127==111 and x>>7&31==1) or (n==2 and x&3==1 and x>>13==1)
  rows[pc]=r;insns.append(r);pc+=n
 check(w['start']+' exact end',pc,end);w['instructions']=insns
 if w['kind']=='core':
  actual=sorted(set(r['target'] for r in insns if r['direct_call']))
  check(w['start']+' calls vs retained graph',actual,sorted(w['callee_inventory']['normalized_result']))
 for r in insns:
  if w['kind']=='core' and 'target' in r and not r['direct_call']:
   check(r['address']+' branch target is instruction start in window',int(r['target'],16) in [int(z['address'],16) for z in insns],True)
# Width, flags, geometry and inverse arithmetic operands, independently checked against encoded fields.
def fields(a,e):
 x=int.from_bytes(raw(a,4),'little');check(hex(a)+' I fields',[x&127,x>>7&31,x>>12&7,x>>15&31,sx(x>>20,12)],e)
fields(0xa00dc9d2,[3,19,2,15,48])
fields(0xa00dc9da,[19,15,7,13,2]);fields(0xa00dc9e2,[19,20,7,13,1])
fields(0xa00dc8b0,[19,12,0,0,113]);fields(0xa00dc8c4,[19,12,0,0,114])
fields(0xa019dfd8,[19,12,0,0,110]);fields(0xa019dff8,[19,12,0,0,111]);fields(0xa008379e,[19,12,0,0,112])
fields(0xa00dc996,[19,15,0,8,-40]);fields(0xa00dc992,[19,16,4,20,1])
check('mode bits width',rows[0xa00dc9d6]['vendor_fields']['msb'],27)
check('mode bits shift',rows[0xa00dc9d6]['vendor_fields']['lsb'],26)
for a,b in {0xa00dca64:'0507',0xa00dca68:'8507',0xa00dca72:'1146',0xa00dc978:'630d0a00',0xa00dca88:'eff03ff3',0xa00dcad4:'9cc4',0xa00dcafc:'d8c0',0xa00dcb16:'dcc4',0xa00ddb1c:'0546',0xa00ddb68:'0546'}.items():check(hex(a)+' geometry/ABI bytes',raw(a,len(bytes.fromhex(b))).hex(),b)
# Match caller/intersection bytes against C22 retained rows without running its verifier.
c22=HERE.parents[0]/'region-gating-review-c22-0041-20261023/evidence.json'
prior=json.loads(c22.read_text())
def visit(o):
 if isinstance(o,dict):
  a=o.get('address');b=o.get('bytes')
  if isinstance(a,str) and a.startswith('0x') and int(a,16) in rows and isinstance(b,str): check('C22 bytes '+a,rows[int(a,16)]['bytes'],b)
  for v in o.values():visit(v)
 elif isinstance(o,list):
  for v in o:visit(v)
visit(prior)
# Actual static halfword table used by sin helper; values retained, no emulator.
lut=raw(0xa02640dc,182);values=[int.from_bytes(lut[i:i+2],'little') for i in range(0,182,2)]
check('sin table first halfword',values[0],0);check('sin table 90 degree endpoint',values[90],32768)
# Keep crucial min/max source/destination registers explicit, independently of pseudocode.
for a,e in {0xa00dcaa2:[14,15,10,32],0xa00dcaaa:[14,12,10,33],0xa00dcab2:[14,13,10,33],0xa00dcabc:[15,11,14,33],0xa00dcac4:[15,12,14,33],0xa00dcacc:[15,13,14,33],0xa00dcae8:[14,15,10,32],0xa00dcaf0:[14,12,10,33],0xa00dcaf8:[14,13,10,33]}.items():
 f=rows[a]['vendor_fields'];check(hex(a)+' min/max register selection',[f['rd'],f['rs1'],f['rs2'],f['funct7']],e)
check('outer area write order',[r['address'] for r in windows[0]['instructions'] if r['assembly'].startswith('c.sw ') and '(s1)' in r['assembly']],['0xa00dcab6','0xa00dcad4','0xa00dcafc','0xa00dcb16'])
check('last a0 assignment',rows[0xa00dcaf4]['assembly'],'slt a0, a3, a4')
metadata=raw(0xa056a49e,5)
check('transform property metadata 0x6e..0x72',metadata.hex(),'3232320000')
strings=[]
for a in [0xa0569318,0xa01c38d4,0xa0263318,0xa01c2994,0xa056a3b4]:
 b=rom[a-BASE:rom.index(0,a-BASE)];strings.append(dict(address=hex(a),file_offset=a-BASE,bytes=b.hex(),text=b.decode()))
for a,t in {0xa00ddb1a:0xa00ddb26,0xa00ddb66:0xa00ddb74,0xa00ddb22:0xa00dca48,0xa00ddb70:0xa00dca48,0xa00ddb80:0xa00ddb26}.items():check(hex(a)+' caller control target',rows[a]['target'],hex(t))
out=dict(property_metadata=dict(address='0xa056a49e',ids=['0x6e','0x6f','0x70','0x71','0x72'],bytes=metadata.hex()),source_strings=strings,method='fresh static ROM extraction and encoding checks; no firmware/model execution',rom=str(ROM),base=hex(BASE),capstone=capstone.__version__,functions=windows,models=dict(source=str(model_path),constructors=used_models,register_source=str(reg_path),tokens=[line for line in reg_model.splitlines() if any(t in line for t in ('thshift=','thmsb=','thlsb=','thsimm='))]),sine_table=dict(address='0xa02640dc',file_offset=0xa02640dc-BASE,bytes=lut.hex(),unsigned_halfwords=values),checks=checks)
(HERE/'evidence.json').write_text(json.dumps(out,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
(HERE/'instructions.txt').write_text('\n'.join('\n'+w['kind']+' '+w['start']+'..'+w['end_exclusive']+'\n'+'\n'.join(r['address']+' '+r['bytes'].ljust(8)+' '+r['assembly']+(' -> '+r['target'] if 'target'in r else '') for r in w['instructions']) for w in windows)+'\n',encoding='utf-8')
print(json.dumps(dict(result='passed',core_functions=len(wanted),windows=len(windows),bytes=sum(len(bytes.fromhex(r['bytes'])) for r in rows.values()),instructions=len(rows),vendor_words=sum('vendor_fields'in r for r in rows.values()),checks=len(checks))))
