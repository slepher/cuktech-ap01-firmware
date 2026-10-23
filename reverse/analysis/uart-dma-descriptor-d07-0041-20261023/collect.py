"""D07 original-ROM descriptor evidence. Static reads only; no target execution."""
from pathlib import Path
import json
from capstone import Cs, CS_ARCH_RISCV, CS_MODE_RISCV32, CS_MODE_RISCVC

OUT = Path(__file__).resolve().parent
ROOT = Path('D:/Documents/PlatformIO/Projects/cuktech-ap01-firmware')
ROM = ROOT / 'roms/0041/ap01-1.0.2_0041.bin'
MODEL = ROOT / 'evidence/rea-0041-20261017/ghidra/Ghidra/Processors/RISCV/data/languages/ap01thead2.sinc'
data = ROM.read_bytes()
model = MODEL.read_text().splitlines()
base = 0x9ffff000
reg = 'zero ra sp gp tp t0 t1 t2 s0 s1 a0 a1 a2 a3 a4 a5 a6 a7 s2 s3 s4 s5 s6 s7 s8 s9 s10 s11 t3 t4 t5 t6'.split()
cs = Cs(CS_ARCH_RISCV, CS_MODE_RISCV32 | CS_MODE_RISCVC)
def offset(a):
    # Startup a0029cf6..9d0e/a0029e2c..34 copies this ROM span into RAM.
    return (0xa0000c14+a-0x62fc1100 if 0x62fc1100 <= a < 0x62fc2cc0 else a)-base
def get(a, n=4): return data[offset(a):offset(a)+n]
def u(a, n=4): return int.from_bytes(get(a,n), 'little')
def sx(n,b): return n-(1<<b) if n & (1<<(b-1)) else n
clauses = {}
def vendor(w):
    rd=(w>>7)&31; rs=(w>>15)&31; rt=(w>>20)&31
    f=(w>>12)&7; top=w>>27; shift=(w>>25)&3
    if f in (2,3):
        name='ext' if f==2 else 'extu'; msb=(w>>26)&31
        args=f'{reg[rd]}, {reg[rs]}, {msb}, {rt}'
        prefix=f':th.{name} rd,rs1,{msb},{rt} '
    else:
        name={(1,0):'addsl',(4,0):'lrb',(4,8):'lrw',(4,16):'lrbu',
              (4,20):'lrhu',(4,19):'lbuia',(4,11):'lwia',(5,0):'srb',(5,8):'srw',(5,11):'swia'}[(f,top)]
        args=f'{reg[rd]}, {reg[rs]}, {sx(rt,5) if name in ("lbuia","lwia","swia") else reg[rt]}, {shift}'
        prefix=f':th.{name} '
    i=next(i for i,s in enumerate(model) if s.startswith(prefix))
    j=next(j for j in range(i+1,len(model)) if model[j]=='}')
    clauses[prefix]={'line':i+1,'text':'\n'.join(model[i:j+1])}
    return 'th.'+name+' '+args

regions=[('uart-start',0xa001a240,0xa001a49c),('configure',0xa0025cec,0xa0025d9e),('submit-wrapper',0xa01a47dc,0xa01a4820),('lli-build',0xa01b554e,0xa01b56be),('cache-clean',0xa0025d9e,0xa0025dcc),('channel-ops',0xa0024b7e,0xa0024c5e),('completion',0xa0019d9a,0xa0019f42),('release',0xa002d5d8,0xa002d62c)]
rows=[]; bypc={}
for name,start,end in regions:
 pc=start; seq=[]
 while pc<end:
  w=u(pc); size=4 if w&3==3 else 2
  assert pc+size<=end
  if w==0x0297800b: decoded='vendor.cache-clean-address a5 [SDK .insn i imm=0x29]'
  elif size==4 and w&127==11: decoded=vendor(w)
  else:
   ins=list(cs.disasm(get(pc,size),pc)); assert len(ins)==1,(hex(pc),get(pc,size).hex()); decoded=ins[0].mnemonic+' '+ins[0].op_str
  r={'va':f'{pc:08x}','offset':f'{offset(pc):x}','raw':get(pc,size).hex(),'instruction':decoded};seq.append(r);bypc[pc]=r;pc+=size
 rows.append({'name':name,'start':hex(start),'end_exclusive':hex(end),'instructions':seq})
def pair(pc):
 w=u(pc); n=u(pc+4); assert w&127==0x17 and n&127==0x67;return (pc+(w&0xfffff000)+sx(n>>20,12))&0xffffffff
assert pair(0xa01b5680)==0xa0025d9e
assert pair(0xa001a454)==0xa01a47dc
assert get(0xa001a45c,4).hex()=='83c70400' # immediate channel reload after ignored submit return
assert get(0xa01b5688,2).hex()=='b640' # no used-count move after cache
assert get(0xa0025dc4,4).hex()=='0b809702'
assert u(0xa01bb000+12)==1 and u(0xa01bb000+16)==0
assert [u(0xa066d580+i*2,2) for i in range(3)]==[4064,8128,16256]
# Raw S-type stores: independently check descriptor widths/order and publication targets.
stores=[]
for pc in bypc:
 w=u(pc)
 if w&127==0x23:
  stores.append({'va':hex(pc),'width':1<<((w>>12)&7),'base':reg[(w>>15)&31],'value':reg[(w>>20)&31],'offset':sx(((w>>25)<<5)|((w>>7)&31),12)})
for pc,basereg,val,off in [(0xa01b560c,'a0','s4',0),(0xa01b5610,'a0','s5',4),(0xa01b5614,'a0','zero',8),(0xa01b5640,'a0','a6',12),(0xa01b5666,'a7','a5',0),(0xa01b566c,'a7','a5',4),(0xa01b5672,'a7','a5',8),(0xa01b567c,'a7','a5',12)]:
 assert {'va':hex(pc),'width':4,'base':basereg,'value':val,'offset':off} in stores
payload={'rom':str(ROM),'base':hex(base) if isinstance(base,int) else '0x9ffff000','model_source':str(MODEL),'method':'Fresh original-ROM static decode; no target execution, no shared REA target/database','regions':rows,'vendor_clauses':clauses,'raw_stores':stores,'constants':{'uart_template':get(0xa01bb000,20).hex(),'chunk_halfwords':[u(0xa066d580+i*2,2) for i in range(3)]},'checks':['AUIPC/JALR submit and cache targets','descriptor/MMIO S-width order','original cache word and ignored submit return','UART template and halfword width offsets']}
(OUT/'instructions.json').write_text(json.dumps(payload,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
print(f'{len(rows)} windows, {len(bypc)} instructions, {len(clauses)} vendor clauses; static checks passed')

# Independent B/J/CB field extraction for critical loop/publication and original return joins.
def branch(pc):
 w=u(pc); assert w&127==0x63
 im=((w>>31)<<12)|(((w>>7)&1)<<11)|(((w>>25)&63)<<5)|(((w>>8)&15)<<1)
 return (pc+sx(im,13))&0xffffffff
def cb(pc):
 h=u(pc,2); im=((h>>12&1)<<8)|((h>>10&3)<<3)|((h>>5&3)<<6)|((h>>3&3)<<1)|((h>>2&1)<<5)
 return (pc+sx(im,9))&0xffffffff
for pc,target in [(0xa01b5656,0xa01b5688),(0xa01b565e,0xa01b55b0),(0xa01b5648,0xa01b5608),(0xa0025db6,0xa0025dc4)]: assert branch(pc)==target
assert cb(0xa01b56ac)==0xa01b5688 and cb(0xa01b56b8)==0xa01b5688
print('Independent original branch/CB return joins passed')
