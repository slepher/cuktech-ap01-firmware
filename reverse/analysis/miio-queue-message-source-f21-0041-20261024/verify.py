"""F21: candidate-message source paths only; no allocator/pool body execution."""
from pathlib import Path
import json
import re
MAIN=Path('D:/Documents/PlatformIO/Projects/cuktech-ap01-firmware')
ROM=MAIN/'roms/0041/ap01-1.0.2_0041.bin'
OUT=Path(__file__).resolve().parent
BASE=0x9ffff000
assert ROM.stat().st_size==6769704
checks=[];rows={}
def bits(v,a,n):return (v>>a)&((1<<n)-1)
def sx(v,n):return v-(1<<n) if v&(1<<(n-1)) else v
def w(pc):
    assert 0xa01318de<=pc<0xa0131920 or 0xa010d70e<=pc<0xa010d738
    if pc not in rows:
        with ROM.open('rb') as f:
            f.seek(pc-BASE);r=f.read(2)
            if r[0]&3==3:r+=f.read(2)
        rows[pc]=r
    return int.from_bytes(rows[pc],'little')
def eq(label,got,want):
    assert got==want,(label,got,want)
    checks.append(dict(label=label,value=got))
def it(pc,op,rd,f3,rs1,imm):
    v=w(pc);eq(hex(pc)+' I-format',[v&127,bits(v,7,5),bits(v,12,3),bits(v,15,5),sx(v>>20,12)],
               [op,rd,f3,rs1,imm])
def ci(pc,f3,rd,imm):
    v=w(pc);eq(hex(pc)+' compressed immediate',[v&3,v>>13,bits(v,7,5),
               sx((bits(v,12,1)<<5)|bits(v,2,5),6)],[1,f3,rd,imm])
def cb(pc,f3,reg,target):
    v=w(pc);i=(bits(v,12,1)<<8)|(bits(v,10,2)<<3)|(bits(v,5,2)<<6)|(bits(v,3,2)<<1)|(bits(v,2,1)<<5)
    eq(hex(pc)+' compressed gate',[v&3,v>>13,8+bits(v,7,3),pc+sx(i,9)],[1,f3,reg,target])
def jal(pc,target):
    v=w(pc);i=(bits(v,31,1)<<20)|(bits(v,12,8)<<12)|(bits(v,20,1)<<11)|(bits(v,21,10)<<1)
    eq(hex(pc)+' JAL',[v&127,bits(v,7,5),pc+sx(i,21)],[111,1,target])
ci(0xa01318de,0,2,-16)
for pc,reg,off,store in [(0xa01318e0,8,8,True),(0xa01318e2,1,12,True),
                          (0xa0131902,1,12,False),(0xa0131904,8,8,False)]:
    v=w(pc)
    if store:i=(bits(v,7,2)<<6)|(bits(v,9,4)<<2);r=bits(v,2,5)
    else:i=(bits(v,12,1)<<5)|(bits(v,4,3)<<2)|(bits(v,2,2)<<6);r=bits(v,7,5)
    eq(hex(pc)+' stack word',[v&3,v>>13,r,i],[2,6 if store else 2,reg,off])
v=w(0xa01318e4);i=(bits(v,11,2)<<4)|(bits(v,7,4)<<6)|(bits(v,6,1)<<2)|(bits(v,5,1)<<3)
eq('frame pointer',[v&3,v>>13,8+bits(v,2,3),i],[0,0,8,16])
it(0xa01318e6,19,10,0,3,0xb8);jal(0xa01318ea,0xa010d70e)
cb(0xa01318ee,7,10,0xa0131902)
v=w(0xa01318f0);eq('flag high LUI',[v&127,bits(v,7,5),v&0xfffff000],[55,15,0x62fc6000])
it(0xa01318f4,3,15,2,15,0x34);eq('flag address',0x62fc6000+0x34,0x62fc6034)
cb(0xa01318f8,6,15,0xa013190a)
it(0xa01318fa,19,10,0,3,0xc0);jal(0xa01318fe,0xa010d70e)
ci(0xa0131906,0,2,16);eq('unchanged-a0 return',w(0xa0131908),0x8082)
it(0xa013190a,19,10,0,0,0x14c)
u=w(0xa013190e);v=w(0xa0131912)
eq('allocation boundary pair fields',[u&127,bits(u,7,5),v&127,bits(v,7,5),bits(v,15,5)],
   [23,1,103,1,1])
eq('allocation boundary target',(0xa013190e+sx(u&0xfffff000,32)+sx(v>>20,12))&0xfffffffe,
   0xa002fcc8)
cb(0xa0131916,6,10,0xa0131902);ci(0xa0131918,2,15,1)
v=w(0xa013191a)
eq('normal fallback object byte mark',[v&127,bits(v,12,3),bits(v,15,5),bits(v,20,5),
                                    sx((bits(v,25,7)<<5)|bits(v,7,5),12)],[35,0,10,15,8])
v=w(0xa013191e)
i=(bits(v,12,1)<<11)|(bits(v,11,1)<<4)|(bits(v,9,2)<<8)|(bits(v,8,1)<<10)
i|=(bits(v,7,1)<<6)|(bits(v,6,1)<<7)|(bits(v,3,3)<<1)|(bits(v,2,1)<<5)
eq('marked fallback joins same return',[v&3,v>>13,0xa013191e+sx(i,12)],[1,5,0xa0131902])

# Management approved only the already-seeded gp-list node getter, no allocator body.
def cm(pc,reg,base,off,store=False):
    v=w(pc);off_got=(bits(v,10,3)<<3)|(bits(v,6,1)<<2)|(bits(v,5,1)<<6)
    eq(hex(pc)+' compressed word memory',[v&3,v>>13,8+bits(v,2,3),8+bits(v,7,3),off_got],
       [0,6 if store else 2,reg,base,off])
def cjump(pc,target):
    v=w(pc);i=(bits(v,12,1)<<11)|(bits(v,11,1)<<4)|(bits(v,9,2)<<8)|(bits(v,8,1)<<10)
    i|=(bits(v,7,1)<<6)|(bits(v,6,1)<<7)|(bits(v,3,3)<<1)|(bits(v,2,1)<<5)
    eq(hex(pc)+' compressed jump',[v&3,v>>13,pc+sx(i,12)],[1,5,target])
ci(0xa010d70e,0,2,-16)
eq('list getter saves s0 only',w(0xa010d710),0xc622)
eq('list getter frame base',w(0xa010d712),0x0800)
cm(0xa010d714,15,10,4)
v=w(0xa010d716);i=(bits(v,31,1)<<12)|(bits(v,7,1)<<11)|(bits(v,25,6)<<5)|(bits(v,8,4)<<1)
eq('empty sentinel equality',[v&127,bits(v,12,3),bits(v,15,5),bits(v,20,5),0xa010d716+sx(i,13)],
   [99,0,15,10,0xa010d734])
cm(0xa010d71a,13,15,4);cm(0xa010d71c,14,15,0)
cm(0xa010d71e,14,13,0,True)
cm(0xa010d720,13,15,4);cm(0xa010d722,13,14,4,True)
for pc,off in [(0xa010d724,4),(0xa010d728,0)]:
    v=w(pc)
    eq(hex(pc)+' clear removed-node link',[v&127,bits(v,12,3),bits(v,15,5),bits(v,20,5),
            sx((bits(v,25,7)<<5)|bits(v,7,5),12)],[35,2,15,0,off])
eq('list getter s0 restore',w(0xa010d72c),0x4432)
v=w(0xa010d72e);eq('return selected node value',[v&3,v>>12,bits(v,7,5),bits(v,2,5)],[2,8,10,15])
ci(0xa010d730,0,2,16);eq('list getter return',w(0xa010d732),0x8082)
ci(0xa010d734,2,15,0);cjump(0xa010d736,0xa010d72c)

f13_path=MAIN/'reverse/analysis/miio-native-queue-f13-0041-20261024/evidence.json'
f13=json.loads(f13_path.read_text(encoding='utf8'));caller={int(r['pc'],16):r for r in f13['rows']}
pcs=[0xa0197a8e,0xa0197ac2,0xa0197ac6,0xa0197aca,0xa0197acc,0xa0197ad0,
     0xa0197b12,0xa0197b14,0xa0197b16,0xa0197b18,0xa0197b1a]
selected=[caller[p] for p in pcs]
eq('caller forwards result M',caller[0xa0197b12]['asm'],'c.mv a1, a0')
eq('caller keeps source',caller[0xa0197b16]['asm'],'c.mv a2, s3')
eq('caller keeps length',caller[0xa0197b14]['asm'],'c.mv a3, s4')
defs=[r for r in f13['rows'] if 0xa0197a8e<=int(r['pc'],16)<0xa0197acc and re.match(
      r'(?:c\.)?(?:mv|addi|li|lui|lw|add|sub) a0,',r['asm'])]
eq('no listed ordinary caller a0 overwrite before service',defs,[])
index_path=MAIN/'reverse/analysis/whole-rom-coverage-0041-20261023-round1.json'
idx=json.loads(index_path.read_text(encoding='utf8'));f=next(f for f in idx['functions'] if f['address']=='0xa01318de')
eq('no prior dossier',f['historical_dossier'],None);eq('no dossier list',f['dossiers'],[])
eq('no historical contract list',f['historical_contracts'],[])
pool=next(f for f in idx['functions'] if f['address']=='0xa010d70e')
eq('list getter no old dossier',pool['historical_dossier'],None)
eq('list getter no old dossier list',pool['dossiers'],[])
eq('list getter no direct callees metadata',pool['direct_calls']['callees'],[])
out=dict(status='PASS',task='F21',claim='F11/7',baseline='bd457a6',
    identity=dict(path=str(ROM),length=6769704,mapping='VA-0x9ffff000',
    sha256_inherited='972db4c136c7ed9e24a83c07c1a7fd62040ca018b08ca285216d26b1fee3c6b9',hash_recomputed=False),
    checks=checks,rows=[dict(address=hex(p),offset=hex(p-BASE),raw=b.hex()) for p,b in sorted(rows.items())],
    inherited=dict(caller_path=str(f13_path),caller_rows=selected,index_path=str(index_path),
                   extent=f['extent'],direct_calls=f['direct_calls'],
                   list_getter_extent=pool['extent'],list_getter_direct_calls=pool['direct_calls']),
    method='Independent RV32/RVC fields; necessary local normal source branches only',
    contract='M is a node removed from sentinel list gp+b8; if empty and flag nonzero, use list gp+c0; if empty and flag zero request a002fcc8(0x14c), setting byte M+8=1 on nonzero. List getter returns word(H+4), unlinking and clearing its two links; empty returns zero.',
    limits=['gp absolute value/list initialization/exclusive ownership/node capacity unknown',
            '332B is allocation request, not independent proof of returned capacity',
            'Only specifically registered list-getter added; no allocator/list initialization/wait/copy4/queue lifetime body expansion',
            'Nonzero M does not certify validity/alignment/nonaliasing or release/consumer timing',
            'No target/instruction/model/input/old-script execution'])
(OUT/'evidence.json').write_text(json.dumps(out,ensure_ascii=False,indent=2)+'\n',encoding='utf8')
print(json.dumps(dict(status='PASS',checks=len(checks),instructions=len(rows),bytes=sum(map(len,rows.values())))))
