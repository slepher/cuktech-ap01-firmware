"""F17 static n=4, valid word-aligned src/dst contract; no target execution."""
from pathlib import Path
import json
MAIN=Path('D:/Documents/PlatformIO/Projects/cuktech-ap01-firmware')
OUT=Path(__file__).resolve().parent
ROM=MAIN/'roms/0041/ap01-1.0.2_0041.bin'
BASE=0x9ffff000
assert ROM.stat().st_size==6769704
checks=[];rows={}
def bits(v,a,n):return (v>>a)&((1<<n)-1)
def sx(v,n):return v-(1<<n) if v&(1<<(n-1)) else v
def word(pc):
    assert pc in {0xa000589c,0xa000589e,0xa00058a0,0xa00058a4,0xa00058a8,0xa00058aa,
                  0xa000591c,0xa000591e,0xa00058f6,0xa00058fa,0xa00058fe,
                  0xa0005902,0xa0005906,0xa000590a,0xa000590e,0xa0005912,0xa0005916}
    with ROM.open('rb') as f:
        f.seek(pc-BASE);r=f.read(2)
        if r[0]&3==3:r+=f.read(2)
    rows[pc]=r
    return int.from_bytes(r,'little')
def eq(pc,label,got,want):
    assert got==want,(hex(pc),label,got,want)
    checks.append(dict(address=hex(pc),label=label,value=got))
def ci(pc,rd,imm):
    v=word(pc);eq(pc,'C.LI',[v&3,v>>13,bits(v,7,5),sx((bits(v,12,1)<<5)|bits(v,2,5),6)],
                  [1,2,rd,imm])
def mv(pc,rd,src):
    v=word(pc);eq(pc,'C.MV',[v&3,v>>12,bits(v,7,5),bits(v,2,5)],[2,8,rd,src])
def branch(pc,f3,r1,r2,target):
    v=word(pc);i=(bits(v,31,1)<<12)|(bits(v,7,1)<<11)|(bits(v,25,6)<<5)|(bits(v,8,4)<<1)
    eq(pc,'B-format',[v&127,bits(v,12,3),bits(v,15,5),bits(v,20,5),pc+sx(i,13)],
       [99,f3,r1,r2,target])
ci(0xa000589c,15,7);mv(0xa000589e,16,10)
v=word(0xa00058a0)
eq(0xa00058a0,'ADD dst+n',[v&127,bits(v,7,5),bits(v,12,3),bits(v,15,5),bits(v,20,5),v>>25],
   [51,14,0,10,12,0])
branch(0xa00058a4,6,15,12,0xa000592c)
eq(0xa00058a4,'static n4 unsigned selector',7<4,False)
ci(0xa00058a8,14,4);branch(0xa00058aa,0,12,14,0xa000591c)
eq(0xa00058aa,'static n4 equality selector',4==4,True)
mv(0xa000591c,15,10)
v=word(0xa000591e)
i=(bits(v,12,1)<<11)|(bits(v,11,1)<<4)|(bits(v,9,2)<<8)|(bits(v,8,1)<<10)
i|=(bits(v,7,1)<<6)|(bits(v,6,1)<<7)|(bits(v,3,3)<<1)|(bits(v,2,1)<<5)
eq(0xa000591e,'C.J byte sequence',[v&3,v>>13,0xa000591e+sx(i,12)],[1,5,0xa00058f6])
vendors=[]
for pc,f3,base,top in [(0xa00058f6,4,11,19),(0xa00058fa,5,15,3),
                       (0xa00058fe,4,11,19),(0xa0005902,5,15,3),
                       (0xa0005906,4,11,19),(0xa000590a,5,15,3)]:
    v=word(pc)
    fields=[v&127,bits(v,7,5),bits(v,12,3),bits(v,15,5),sx(bits(v,20,5),5),bits(v,25,2),v>>27]
    eq(pc,'existing vendor byte/postincrement fields',fields,[11,14,f3,base,1,0,top])
    vendors.append(dict(address=hex(pc),fields=dict(op=11,rd=14,f3=f3,base=base,simm=1,shift=0,top5=top)))
v=word(0xa000590e)
eq(0xa000590e,'final unsigned byte load',[v&127,bits(v,7,5),bits(v,12,3),bits(v,15,5),sx(v>>20,12)],
   [3,14,4,11,0])
v=word(0xa0005912)
eq(0xa0005912,'final byte store',[v&127,bits(v,12,3),bits(v,15,5),bits(v,20,5),
                                  sx((bits(v,25,7)<<5)|bits(v,7,5),12)],[35,0,15,14,0])
eq(0xa0005916,'RET unchanged a0',word(0xa0005916),0x8082)

# Existing profile text supplies the byte-width and postincrement semantics.
model_path=MAIN/'evidence/rea-0041-20261017/ghidra/Ghidra/Processors/RISCV/data/languages/ap01thead2.sinc'
m=model_path.read_text(encoding='utf8');rules=[]
for marker,required in [(':th.lbuia ',['local ea:4 = rs1;','local value:1 = *[ram]:1 ea;',
                                    'rd = zext(value);','thbase = updated;']),
                         (':th.sbia ',['local ea:4 = rs1;','*[ram]:1 ea = rd:1;','thbase = updated;'])]:
    p=m.index(marker);r=m[p:m.index('\n}',p)+2]
    eq(0xa00058f6,marker+' existing rule clauses',all(s in r for s in required),True)
    rules.append(dict(path=str(model_path),line=m.count('\n',0,p)+1,text=r))

bundle=MAIN/'evidence/rea-0041-20261017/evidence/upper-complete.evidence.json'
j=json.loads(bundle.read_text(encoding='utf8'));r=j['records'][76]
eq(0xa000589c,'inherited dossier EID',r['evidence_id'],
   'ev_32725e49dc86c4d072d48e396f5c14986a521284bea8c8ff59cd533fc995a848')
eq(0xa000589c,'inherited profile',r['analysis_profile']['digest'],
   '4825fb58a33a3e7d618557975b153b8318cf7e833d190ad16bcbf8bd441ae621')
old=[s for s in r['normalized_result']['assembly'] if int(s.split(':')[0],16) in rows]
eq(0xa000589c,'only selected old rows retained',len(old),17)

out=dict(status='PASS',task='F17',claim='F11/5',baseline='bd457a6',
    identity=dict(path=str(ROM),length=6769704,mapping='VA-0x9ffff000',
    sha256_inherited='972db4c136c7ed9e24a83c07c1a7fd62040ca018b08ca285216d26b1fee3c6b9',hash_recomputed=False),
    domain='n=4, normally valid source/destination with word alignment; no arbitrary-length/unaligned contract',
    checks=checks,rows=[dict(address=hex(p),offset=hex(p-BASE),raw=b.hex()) for p,b in sorted(rows.items())],
    inherited=dict(path=str(bundle),pointer='#/records/76',evidence_id=r['evidence_id'],
    profile=r['analysis_profile']['digest'],selected_assembly=old),vendor_fields=vendors,existing_rules=rules,
    contract='Three postincrement byte load/store pairs followed by final byte load/store at offset3; return original dst in a0; no direct memory retention of pointer parameters or calls on this route',
    limits=['Model semantics inherited from existing private profile, not new upstream ISA authentication',
            'Validity/alignment/capacity/noninterference remain caller conditions; no arbitrary input or overlap certification',
            'F11 actual queue size/loop identity and allocator lifetime are separate claims',
            'No firmware/instruction/model/old-script execution or full libc/body export'])
(OUT/'evidence.json').write_text(json.dumps(out,ensure_ascii=False,indent=2)+'\n',encoding='utf8')
print(json.dumps(dict(status='PASS',checks=len(checks),instructions=len(rows),bytes=sum(map(len,rows.values())))))
