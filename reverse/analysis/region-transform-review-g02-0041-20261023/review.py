"""G02 independent, execution-free ROM decoding and instruction-contract checks.
Does not import or run G01/C22 verifiers, emulate code, or open an REA database.
"""
from pathlib import Path
import json
import capstone

OUT = Path(__file__).resolve().parent
ROOT = OUT.parents[1]
SOURCE = Path('D:/Documents/PlatformIO/Projects/cuktech-ap01-firmware')
ROM = SOURCE / 'roms/0041/ap01-1.0.2_0041.bin'
BASE = 0x9ffff000
data = ROM.read_bytes()
decoder = capstone.Cs(capstone.CS_ARCH_RISCV,
                      capstone.CS_MODE_RISCV32 | capstone.CS_MODE_RISCVC)
spans = [
    (0xa00dca48,0xa00dcb22,'area'), (0xa00dc9ba,0xa00dca48,'walk'),
    (0xa00dc862,0xa00dc9ba,'node'), (0xa0083796,0xa00837ae,'angle'),
    (0xa019dfd0,0xa019dff0,'scale-x'), (0xa019dff0,0xa019e010,'scale-y'),
    (0xa00dc658,0xa00dc862,'style-default'),
    (0xa00dc070,0xa00dc19a,'style-select'),
    (0xa00dc020,0xa00dc070,'style-property'),
    (0xa0089e10,0xa0089ff0,'points'), (0xa0089d76,0xa0089e10,'sine'),
    (0xa00dbff4,0xa00dc020,'predicate-contract'),
    (0xa00ddb14,0xa00ddb2a,'first-caller-contract'),
    (0xa00ddb60,0xa00ddb84,'ancestor-caller-contract'),
]
rows = {}; windows = []; checks = []
def raw(a,n):
    b = data[a-BASE:a-BASE+n]
    assert len(b)==n
    return b
def signed(v,b): return v-(1<<b) if v & (1<<(b-1)) else v
def verify(label,got,want):
    assert got==want,(label,got,want)
    checks.append({'claim':label,'observed':got,'required':want})
def custom(w):
    fields = dict(rd=(w>>7)&31, rs1=(w>>15)&31, rs2=(w>>20)&31,
                  f3=(w>>12)&7, f7=w>>25, msb=w>>26, lsb=(w>>20)&63,
                  scale=(w>>25)&3)
    f=fields['f3']; top=w>>27
    if f in (2,3): name='ext' if f==2 else 'extu'
    elif f==1 and fields['f7'] in (16,17,32,33):
        name={16:'mula',17:'muls',32:'mveqz',33:'mvnez'}[fields['f7']]
    elif f==1 and top==0: name='addsl'
    else: name={(4,8):'lrw',(5,8):'srw',(4,20):'lrhu',(4,16):'lrbu'}[(f,top)]
    return name, fields
def dest(a,n,w):
    if n==4 and w&127==0x6f:
        bits=((w>>31)<<20)|(((w>>12)&255)<<12)|(((w>>20)&1)<<11)|(((w>>21)&1023)<<1)
        return a+signed(bits,21)
    if n==2 and w&3==1 and w>>13 in (1,5):
        bits=(((w>>12)&1)<<11)|(((w>>11)&1)<<4)|(((w>>9)&3)<<8)|(((w>>8)&1)<<10)|(((w>>7)&1)<<6)|(((w>>6)&1)<<7)|(((w>>3)&7)<<1)|(((w>>2)&1)<<5)
        return a+signed(bits,12)
for start,end,name in spans:
    pc=start; entries=[]
    while pc<end:
        h=int.from_bytes(raw(pc,2),'little'); n=4 if h&3==3 else 2
        b=raw(pc,n); word=int.from_bytes(b,'little')
        row={'address':hex(pc),'offset':pc-BASE,'bytes':b.hex()}
        if n==4 and word&127==11:
            op,fields=custom(word); row.update(op='th.'+op,fields=fields)
        else:
            ins=list(decoder.disasm(b,pc)); assert len(ins)==1 and ins[0].size==n,hex(pc)
            row.update(op=ins[0].mnemonic,operands=ins[0].op_str)
        t=dest(pc,n,word)
        if t is not None:row['jump_target']=hex(t)
        row['call']=(n==4 and word&127==0x6f and (word>>7)&31==1) or (n==2 and word&3==1 and word>>13==1)
        rows[pc]=row; entries.append(row); pc+=n
    verify(name+' exact extent',pc,end)
    windows.append({'name':name,'start':hex(start),'end_exclusive':hex(end),'instructions':entries})

# Independent byte agreement with the retained report evidence, not its assertions.
prior=json.loads((ROOT/'analysis/region-transform-flow-g01-0041-20261023/evidence.json').read_text(encoding='utf-8'))
matched=0
for win in prior['functions']:
    for old in win['instructions']:
        a=int(old['address'],16)
        if a in rows:
            assert rows[a]['bytes']==old['bytes'],hex(a)
            matched+=1
verify('overlapping original instructions agree',matched,793)

def asm(a,op,operands=None):
    verify(hex(a)+' opcode',rows[a]['op'],op)
    if operands is not None:verify(hex(a)+' operands',rows[a]['operands'],operands)
def fields(a,expected):
    for key,v in expected.items():verify(hex(a)+' '+key,rows[a]['fields'][key],v)
def calls(name,want):
    win=next(w for w in windows if w['name']==name)
    verify(name+' direct calls',sorted(set(r['jump_target'] for r in win['instructions'] if r['call'])),[hex(a) for a in sorted(want)])
calls('area',[0xa00dc9ba]); calls('walk',[0xa00dc862,0xa00dc9ba])
calls('node',[0xa0083796,0xa019dfd0,0xa019dff0,0xa00dc658,0xa0089e10])
calls('points',[0xa0089d76]); calls('sine',[])
calls('style-select',[0xa00dc020]); calls('style-property',[])
calls('style-default',[0xa00dc070,0xa008b51a,0xa0019672])
for name in ('angle','scale-x','scale-y'):calls(name,[0xa00dc658])
fields(0xa00dc9d6,dict(rd=19,rs1=19,msb=27,lsb=26,f3=3))
for a,op,arg in [
 (0xa00dc9da,'andi','a5, a3, 2'),(0xa00dc9e2,'andi','s4, a3, 1'),
 (0xa00dca24,'c.li','a3, 0'),(0xa00dca06,'c.li','a3, 1'),
 (0xa00dca3e,'c.lw','a0, 4(s1)'),(0xa00dc9ec,'c.lw','a0, 4(a0)'),
 (0xa00dca64,'c.addi','a4, 1'),(0xa00dca68,'c.addi','a5, 1'),
 (0xa00dcaf4,'slt','a0, a3, a4'),
 (0xa00dcab6,'c.sw','a4, 0(s1)'),(0xa00dcad4,'c.sw','a5, 8(s1)'),
 (0xa00dcafc,'c.sw','a4, 4(s1)'),(0xa00dcb16,'c.sw','a5, 0xc(s1)'),
 (0xa00dc8b0,'addi','a2, zero, 0x71'),(0xa00dc8c4,'addi','a2, zero, 0x72'),
 (0xa00dc90e,'mul','a5, a5, a3'),(0xa00dc916,'div','a5, a5, a3'),
 (0xa00dc950,'mul','a0, a0, a5'),(0xa00dc958,'div','a0, a0, a5'),
 (0xa00dc986,'div','s5, a3, s5'),(0xa00dc98e,'div','a4, a5, a4'),
 (0xa00dc992,'xori','a6, s4, 1'),(0xa00dc996,'addi','a5, s0, -0x28'),
 (0xa0089e94,'c.srai','a0, 8'),(0xa0089ea8,'c.srai','a0, 8'),
 (0xa0089f52,'srai','t1, t1, 5'),(0xa0089f56,'srai','a7, a7, 5'),
 (0xa0089f7c,'srai','t3, t3, 0xa'),(0xa0089f8a,'c.srai','a2, 0xa'),
 (0xa0089fba,'srai','t3, t3, 0x12'),(0xa0089fc8,'c.srai','a2, 0x12'),
 (0xa00dc00c,'lhu','a5, 0x32(a5)'),(0xa00ddb1c,'c.li','a2, 1'),
 (0xa00ddb68,'c.li','a2, 1'),(0xa00ddb74,'addi','a2, s0, -0x30'),
]:asm(a,op,arg)
for a in (0xa0089ee4,0xa0089ef4,0xa0089f02,0xa0089f10):fields(a,dict(msb=15,lsb=0,f3=2))
fields(0xa00dc0c6,dict(msb=25,lsb=20,f3=3))
fields(0xa00dc104,dict(msb=25,lsb=20,f3=3))
for a in (0xa00dcaa2,0xa00dcaaa,0xa00dcab2,0xa00dcabc,0xa00dcac4,0xa00dcacc,0xa00dcae8,0xa00dcaf0,0xa00dcaf8,0xa00dcb02,0xa00dcb0a,0xa00dcb12):
    verify(hex(a)+' conditional selection',rows[a]['op'] in ('th.mveqz','th.mvnez'),True)
verify('property metadata',raw(0xa056a49e,5).hex(),'3232320000')
table=[int.from_bytes(raw(0xa02640dc+2*i,2),'little') for i in range(91)]
verify('table first',table[0],0);verify('table last',table[90],32768)
# Compare the C21 halfword and G01 word masks by static byte location, no execution.
verify('mask byte positions coincide',[(0x32*8)+10,(0x32*8)+11],[(0x30*8)+26,(0x30*8)+27])
model=SOURCE/'evidence/rea-0041-20261017/ghidra/Ghidra/Processors/RISCV/data/languages/ap01thead2.sinc'
text=model.read_text(); constructors={}
for row in rows.values():
    if 'fields' not in row:continue
    name=row['op']; f=row['fields']; key=':'+name+' '
    if name in ('th.ext','th.extu'):key+=f"rd,rs1,{f['msb']},{f['lsb']} "
    start=text.index(key); end=text.index('}',start)+1
    constructors[key]={'line':text[:start].count('\n')+1,'text':text[start:end]}
result={'method':'fresh original ROM reads and static decoding; no target/model execution',
 'rom':str(ROM),'base':hex(BASE),'capstone':capstone.__version__,'windows':windows,
 'model_source':str(model),'constructors':constructors,'checks':checks,
 'sine_table':{'address':'0xa02640dc','u16':table},'byte_agreement_count':matched}
(OUT/'evidence.json').write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
(OUT/'instructions.txt').write_text('\n'.join('\n'+w['name']+' '+w['start']+'..'+w['end_exclusive']+'\n'+'\n'.join(r['address']+' '+r['bytes'].ljust(8)+' '+r['op']+' '+r.get('operands',json.dumps(r.get('fields',{})))+(' -> '+r['jump_target'] if 'jump_target'in r else '') for r in w['instructions']) for w in windows)+'\n',encoding='utf-8')
print(json.dumps({'result':'passed','core_functions':11,'windows':len(windows),
 'instructions':len(rows),'bytes':sum(len(bytes.fromhex(r['bytes'])) for r in rows.values()),
 'vendor_words':sum('fields'in r for r in rows.values()),'checks':len(checks),'matched':matched}))
