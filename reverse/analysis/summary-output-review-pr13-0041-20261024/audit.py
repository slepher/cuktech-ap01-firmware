"""Independent read-only ROM field audit. Standard library; never execute firmware."""
import json
from pathlib import Path

ROOT = Path(r'D:/Documents/PlatformIO/Projects/cuktech-ap01-firmware')
OUT = Path(__file__).resolve().parent
BASE = 0x9ffff000
rom = (ROOT / 'roms/0041/ap01-1.0.2_0041.bin').read_bytes()
assert len(rom) == 6769704
def raw(a,n): return rom[a-BASE:a-BASE+n]
def sx(x,n): return x-(1<<n) if x&(1<<(n-1)) else x
def bits(x,a,n=1): return (x>>a)&((1<<n)-1)
checks=[]
def check(label, actual, expected):
    assert actual == expected, (label,actual,expected)
    checks.append({'label':label,'actual':actual,'expected':expected})

def decode(a):
    h=int.from_bytes(raw(a,2),'little'); n=4 if h&3==3 else 2
    w=int.from_bytes(raw(a,n),'little'); d={'address':hex(a),'bytes':raw(a,n).hex(),'size':n}
    if n==4:
        op=w&127; rd=bits(w,7,5); f=bits(w,12,3); rs1=bits(w,15,5); rs2=bits(w,20,5); imm=sx(w>>20,12)
        d.update(opcode=op,rd=rd,rs1=rs1,rs2=rs2,funct3=f)
        if op in (3,0x13,0x67): d['imm']=imm
        if op==0x23: d['imm']=sx(bits(w,7,5)|(bits(w,25,7)<<5),12)
        if op==0x37: d['value']=w&0xfffff000
        if op==0x6f:
            off=sx((bits(w,31)<<20)|(bits(w,12,8)<<12)|(bits(w,20)<<11)|(bits(w,21,10)<<1),21)
            d.update(kind='jal',target=hex((a+off)&0xffffffff))
        elif op==0x63:
            off=sx((bits(w,31)<<12)|(bits(w,7)<<11)|(bits(w,25,6)<<5)|(bits(w,8,4)<<1),13)
            d.update(kind='branch',target=hex((a+off)&0xffffffff))
        else: d['kind']={3:'load',0x23:'store',0x13:'opimm',0x37:'lui',0x67:'jalr'}.get(op,'opaque')
    else:
        q=w&3; f=w>>13; rd=bits(w,7,5); rs2=bits(w,2,5)
        d.update(quadrant=q,funct3=f,rd=rd,rs2=rs2)
        if q==0 and f==0:
            d.update(kind='c.addi4spn',reg=8+bits(w,2,3),imm=(bits(w,7,4)<<6)|(bits(w,11,2)<<4)|(bits(w,5)<<3)|(bits(w,6)<<2))
        elif q==0 and f in (2,6):
            d.update(kind='c.lw' if f==2 else 'c.sw',base=8+bits(w,7,3),reg=8+bits(w,2,3),imm=(bits(w,10,3)<<3)|(bits(w,6)<<2)|(bits(w,5)<<6))
        elif q==1 and f in (0,2):
            d.update(kind='c.addi' if f==0 else 'c.li',imm=sx((bits(w,12)<<5)|bits(w,2,5),6))
        elif q==1 and f==3 and rd!=2:
            d.update(kind='c.lui',value=sx((bits(w,12)<<5)|bits(w,2,5),6)<<12)
        elif q==1 and f==3 and rd==2:
            d.update(kind='c.addi16sp',imm=sx((bits(w,12)<<9)|(bits(w,6)<<4)|(bits(w,5)<<6)|(bits(w,3,2)<<7)|(bits(w,2)<<5),10))
        elif q==1 and f in (1,5):
            off=sx((bits(w,12)<<11)|(bits(w,11)<<4)|(bits(w,9,2)<<8)|(bits(w,8)<<10)|(bits(w,7)<<6)|(bits(w,6)<<7)|(bits(w,3,3)<<1)|(bits(w,2)<<5),12)
            d.update(kind='c.jal' if f==1 else 'c.j',target=hex((a+off)&0xffffffff))
        elif q==1 and f in (6,7):
            off=sx((bits(w,12)<<8)|(bits(w,10,2)<<3)|(bits(w,5,2)<<6)|(bits(w,3,2)<<1)|(bits(w,2)<<5),9)
            d.update(kind='c.beqz' if f==6 else 'c.bnez',reg=8+bits(w,7,3),target=hex((a+off)&0xffffffff))
        elif q==2 and f==4: d.update(kind='c.reg',high=bits(w,12))
        elif q==2 and f==2: d.update(kind='c.lwsp',imm=(bits(w,12)<<5)|(bits(w,4,3)<<2)|(bits(w,2,2)<<6))
        elif q==2 and f==6: d.update(kind='c.swsp',imm=(bits(w,9,4)<<2)|(bits(w,7,2)<<6))
        else: d['kind']='c.other'
    return d

# Walk the known body only, plus the already-scoped color adapter. No new callees.
rows=[]
for lo,hi in [(0xa00abbf6,0xa00abd9c),(0xa00a5e8e,0xa00a5ed6)]:
    a=lo
    while a<hi:
        d=decode(a);rows.append(d);a+=d['size']
    check('window_end_'+hex(lo),a,hi)
by={int(x['address'],16):x for x in rows}
# Compare saved observation bytes and independently decoded branch/call targets.
author=json.loads((ROOT/'reverse/analysis/summary-output-p13-0041-20261024/evidence.json').read_text(encoding='utf-8'))
for x in author['selected_instructions']:
    a=int(x['address'],16);check('bytes_'+hex(a),raw(a,len(bytes.fromhex(x['bytes']))).hex(),x['bytes'])
    if 'direct_target' in x: check('target_'+hex(a),decode(a)['target'],x['direct_target'])
for addr,h in author['resource_headers'].items(): check('header_'+addr,raw(int(addr,16),24).hex(),h)
for addr,h in author['opaque_color_adapter_custom_words'].items(): check('opaque_'+addr,raw(int(addr,16),4).hex(),h)
check('image_gate_imm',by[0xa00abc00]['imm'],253)
check('flag_gate_imm',by[0xa00abd36]['imm'],253)
check('flag_subtract',by[0xa00abd34]['imm'],-2)
check('image_gate_regs',[by[0xa00abc00][k] for k in ('rd','rs1')],[14,11])
check('flag_gate_regs',[by[0xa00abd36][k] for k in ('rd','rs1')],[11,11])
def fields(a,expected):
    d=by[a]
    for k,v in expected.items(): check(hex(a)+'_'+k,d[k],v)
fields(0xa00abbfe,{'kind':'c.addi4spn','reg':8,'imm':32})
for a,reg,imm in [(0xa00abc14,9,128),(0xa00abc60,9,128)]: fields(a,{'rd':reg,'rs1':reg,'imm':imm})
for hi,lo,value in [(0xa00abc10,0xa00abc18,0xa0242574),(0xa00abc5c,0xa00abc64,0xa0242808),(0xa00abc28,0xa00abc2c,0x6ff8b),(0xa00abc72,0xa00abc76,0xff7a00),(0xa00abcbe,0xa00abcc2,0x89d8f3),(0xa00abd00,0xa00abd04,0x6ff8b)]:
    check('constant_'+hex(hi),(by[hi]['value']+by[lo]['imm'])&0xffffffff,value)
for a,off in [(0xa00abc20,48),(0xa00abc26,48),(0xa00abc34,48),(0xa00abc6a,48),(0xa00abc70,48),(0xa00abc7e,48),(0xa00abca6,56),(0xa00abcb6,88),(0xa00abcbc,88),(0xa00abcca,88),(0xa00abcf4,96),(0xa00abcf8,88),(0xa00abcfe,88),(0xa00abd0c,88)]: fields(a,{'kind':'c.lw','base':9,'reg':10,'imm':off})
for a,x,y in [(0xa00abc36,92,168),(0xa00abc80,98,170),(0xa00abccc,98,170),(0xa00abd0e,92,168)]:
    fields(a,{'rd':12,'rs1':0,'imm':x});fields(a+4,{'kind':'c.li','rd':11,'imm':1});fields(a+6,{'rd':13,'rs1':0,'imm':y})
for a,imm in [(0xa00abc56,0x20000),(0xa00abca2,0x20000),(0xa00abcf0,0x20000),(0xa00abd2e,0x20000)]:fields(a,{'rd':12,'value':imm})
for a,off in [(0xa00abd44,0xc4),(0xa00abd58,0xc4),(0xa00abd74,0xec),(0xa00abd8c,0xec),(0xa00abd66,0xbc),(0xa00abd6a,0xc0),(0xa00abd82,0xe4),(0xa00abd86,0xe8)]:fields(a,{'kind':'load','funct3':2,'rs1':9,'imm':off})
for a,align,x in [(0xa00abd4c,1,22),(0xa00abd60,2,0),(0xa00abd7c,2,0),(0xa00abd94,1,22)]:
    fields(a,{'kind':'c.li','rd':14,'imm':7});fields(a+2,{'kind':'c.li','rd':13,'imm':x});fields(a+4,{'kind':'c.li','rd':12,'imm':align})
for a,off,width in [(0xa00abc94,-32,1),(0xa00abc9a,-30,0),(0xa00abce0,-28,1),(0xa00abce8,-26,0),(0xa00abd20,-20,1),(0xa00abd26,-18,0)]:fields(a,{'kind':'store','rs1':8,'imm':off,'funct3':width})
for a,off in [(0xa00abc52,-24),(0xa00abc9e,-32),(0xa00abcec,-28),(0xa00abd2a,-20)]:fields(a,{'kind':'load','rd':11,'rs1':8,'imm':off,'funct3':2})
check('orange_low16',(by[0xa00abc8e]['value']^by[0xa00abc90]['imm'])&0xffff,0x7a00)
check('blue_low16',(by[0xa00abcda]['value']+by[0xa00abcdc]['imm'])&0xffff,0xd8f3)
fields(0xa00abc98,{'imm':-1});fields(0xa00abce4,{'imm':-119})
# Only stack stores occur in this body; no direct S write or measurement load.
check('store_bases',sorted({d['rs1'] for d in rows if d.get('kind')=='store' and int(d['address'],16)>=0xa00abbf6}),[8])
for a,reg,base,imm,width in [(0xa00abc48,15,8,-24,1),(0xa00abc4e,15,8,-22,0)]:
    d=by[a];check('store_fields_'+hex(a),[d['rs2'],d['rs1'],d['imm'],d['funct3']],[reg,base,imm,width])
coverage=json.loads((ROOT/'reverse/analysis/whole-rom-coverage-0041-20261023-round1.json').read_text(encoding='utf-8'))
inv=next(x for x in coverage['functions'] if x['address']=='0xa00abbf6')
check('extent',inv['extent']['body']['total_bytes'],422)
calls=sorted({d['target'] for d in rows if d.get('kind')=='jal' and 0xa00abbf6<=int(d['address'],16)<0xa00abd9c})
check('direct_callees',calls,sorted(inv['direct_calls']['callees']))
bundle=json.loads((ROOT/'evidence/rea-0041-20261017/evidence/whole-rom-paths-20261023.evidence.json').read_text(encoding='utf-8'))
record=next(x for x in bundle['records'] if x['evidence_id']==inv['inventory_evidence'])
check('profile',record['analysis_profile']['digest'],'b6368dd18431e8113aa5026c713d41e648ab0f6ddd9421ff6c4a49e23b3cd2f3')
check('language',record['analysis_profile']['parameters']['language_id'],'RISCV:LE:32:ap01thead2')
check('provider_version',next(x for x in bundle['providers'] if x['id']=='ghidra')['version'],'12.1.4')
result={'status':'PASS','checks':checks,'instructions':rows,'inventory':inv,'profile':record['analysis_profile'],'providers':bundle['providers'],'method':'stdlib raw instruction fields, no author script import or execution; no ISA execution','limitations':['c.other and custom opaque rows have raw bytes only','manual control/dataflow assessment is separate from numerical field checks','not physical display or image decoding evidence']}
(OUT/'audit.json').write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
for d in rows: print(d)
print('PASS',len(checks),'checks',len(rows),'rows',sum(d['size'] for d in rows),'bytes')
