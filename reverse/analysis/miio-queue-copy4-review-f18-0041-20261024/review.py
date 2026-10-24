"""F18 independent review of the registered n=4 route, never target execution."""
import json
from pathlib import Path
import capstone

MAIN=Path('D:/Documents/PlatformIO/Projects/cuktech-ap01-firmware')
OUT=Path(__file__).resolve().parent
ROM=MAIN/'roms/0041/ap01-1.0.2_0041.bin'
BASE=0x9ffff000
assert ROM.stat().st_size==6769704
windows=[(0xa000589c,0xa00058ae),(0xa00058f6,0xa0005918),(0xa000591c,0xa0005920)]
raws={}
with ROM.open('rb') as f:
    for a,z in windows:
        f.seek(a-BASE);data=f.read(z-a)
        pc=a
        while pc<z:
            off=pc-a;size=4 if data[off]&3==3 else 2
            assert pc+size<=z
            raws[pc]=data[off:off+size];pc+=size
md=capstone.Cs(capstone.CS_ARCH_RISCV,capstone.CS_MODE_RISCV32|capstone.CS_MODE_RISCVC)
rows={};checks=[]
vendor_pcs={0xa00058f6,0xa00058fa,0xa00058fe,0xa0005902,0xa0005906,0xa000590a}
for pc,b in raws.items():
    ins=list(md.disasm(b,pc))
    if pc in vendor_pcs:asm='UNDECODED; fields interpreted only under inherited local rule'
    else:
        assert len(ins)==1 and ins[0].size==len(b)
        asm=ins[0].mnemonic+' '+ins[0].op_str
    rows[pc]={'pc':hex(pc),'offset':hex(pc-BASE),'raw':b.hex(),'asm':asm}
def check(ok,meaning,**details):
    assert ok,(meaning,details)
    checks.append({'meaning':meaning,**details})
for pc,asm in [
 (0xa000589c,'c.li a5, 7'),(0xa000589e,'c.mv a6, a0'),
 (0xa00058a0,'add a4, a0, a2'),(0xa00058a4,'bltu a5, a2, 0x88'),
 (0xa00058a8,'c.li a4, 4'),(0xa00058aa,'beq a2, a4, 0x72'),
 (0xa000591c,'c.mv a5, a0'),(0xa000591e,'c.j -0x28'),
 (0xa000590e,'lbu a4, 0(a1)'),(0xa0005912,'sb a4, 0(a5)'),
 (0xa0005916,'c.jr ra')]:
    check(rows[pc]['asm']==asm,'ordinary operand check',pc=hex(pc),observed=rows[pc]['asm'])
def sx(x,b):return x-(1<<b) if x&(1<<(b-1)) else x
def w(pc):return int.from_bytes(raws[pc],'little')
for pc,target,f3 in [(0xa00058a4,0xa000592c,6),(0xa00058aa,0xa000591c,0)]:
    v=w(pc);imm=((v>>31)<<12)|(((v>>7)&1)<<11)|(((v>>25)&63)<<5)|(((v>>8)&15)<<1)
    check((v&127,(v>>12)&7)==(99,f3) and pc+sx(imm,13)==target,
          'independent unsigned/equality B-format target',pc=hex(pc),target=hex(target))
v=w(0xa000591e)
imm=(((v>>12)&1)<<11)|(((v>>11)&1)<<4)|(((v>>9)&3)<<8)|(((v>>8)&1)<<10)|(((v>>7)&1)<<6)|(((v>>6)&1)<<7)|(((v>>3)&7)<<1)|(((v>>2)&1)<<5)
check(0xa000591e+sx(imm,12)==0xa00058f6,'independent CJ target',target='0xa00058f6')
check(not (7<4) and 4==4,'static n=4 branch selection; no instruction execution')
vendor=[]
for pc in sorted(vendor_pcs):
    v=w(pc)
    fields={'opcode':v&127,'rd':(v>>7)&31,'f3':(v>>12)&7,'base':(v>>15)&31,
            'simm':sx((v>>20)&31,5),'shift':(v>>25)&3,'top5':v>>27}
    isload=pc in [0xa00058f6,0xa00058fe,0xa0005906]
    expected=dict(opcode=11,rd=14,f3=4 if isload else 5,base=11 if isload else 15,
                  simm=1,shift=0,top5=19 if isload else 3)
    check(fields==expected,'independent vendor field check',pc=hex(pc),fields=fields)
    vendor.append({'pc':hex(pc),'fields':fields,'role':'byte load postincrement1' if isload else 'byte store postincrement1'})
v=w(0xa000590e)
check((v&127,(v>>7)&31,(v>>12)&7,(v>>15)&31,v>>20)==(3,14,4,11,0),
      'final I-format LBU a4,0(a1)')
v=w(0xa0005912)
check((v&127,(v>>12)&7,(v>>15)&31,(v>>20)&31,((v>>25)<<5)|((v>>7)&31))==(35,0,15,14,0),
      'final S-format SB a4,0(a5)')

model_path=MAIN/'evidence/rea-0041-20261017/ghidra/Ghidra/Processors/RISCV/data/languages/ap01thead2.sinc'
model=model_path.read_text(encoding='utf-8')
check('thbase: r1519 is r1519 { export r1519; }' in model,'base update aliases rs1 register in local model')
rules=[]
for name in ['th.lbuia','th.sbia']:
    at=model.index(':'+name+' ');end=model.index('\n}',at)+2;rule=model[at:end]
    common=['local delta:4 = thsimm << thshift;','local updated:4 = rs1 + delta;',
            'local ea:4 = rs1;','thbase = updated;']
    specific=['local value:1 = *[ram]:1 ea;','rd = zext(value);'] if name=='th.lbuia' else ['*[ram]:1 ea = rd:1;']
    check(all(x in rule for x in common+specific),'old-address byte access before postincrement in local rule',rule=name)
    rules.append({'name':name,'line':model[:at].count('\n')+1,'text':rule})

old_path=MAIN/'evidence/rea-0041-20261017/evidence/upper-complete.evidence.json'
upper=json.loads(old_path.read_text(encoding='utf-8'));r=upper['records'][76]
check(r['evidence_id']=='ev_32725e49dc86c4d072d48e396f5c14986a521284bea8c8ff59cd533fc995a848','inherited dossier identity')
check(r['analysis_profile']['digest']=='4825fb58a33a3e7d618557975b153b8318cf7e833d190ad16bcbf8bd441ae621','inherited profile identity')
selected=[s for s in r['normalized_result']['assembly'] if int(s.split(':')[0],16) in raws]
check(len(selected)==17 and len(rows)==17,'all and only 17 necessary route positions retained')
# All route writes are enumerated above: register calculations, a4 byte data,
# postincremented a1/a5, and destination byte stores. a0 is never a destination.
check(all(not x['asm'].startswith(('jal ','jalr ','c.jalr ','c.swsp ','sw ','c.sw '))
          for x in rows.values()),'route has no call, stack store or full pointer store')

result={'claim':'F11/5','review':'F18','reviewer':'/root/f12','baseline':'bd457a6',
 'static_only':True,'rom':str(ROM),'length':ROM.stat().st_size,
 'inherited_sha256':'972db4c136c7ed9e24a83c07c1a7fd62040ca018b08ca285216d26b1fee3c6b9',
 'mapping':'VA-0x9ffff000','domain':'n=4; normal valid word-aligned storage, without arbitrary overlap/interference certification',
 'windows':[{'start':hex(a),'end_exclusive':hex(z)} for a,z in windows],
 'bytes':sum(z-a for a,z in windows),'decoder':'Capstone '+capstone.__version__+' RV32+RVC',
 'rows':list(rows.values()),'checks':checks,'vendor':vendor,
 'local_model':{'path':str(model_path),'rules':rules},
 'retained':{'path':str(old_path),'record':76,'evidence_id':r['evidence_id'],
             'profile':r['analysis_profile']['digest'],'assembly':selected},
 'conclusion':'limited acceptance; semantic correction0; new business0',
 'limits':['Vendor semantics inherit local model, not independent ISA authentication',
 'No actual queue address/capacity/alignment/lifetime certification',
 'No all-length/unaligned/full-helper/overlap/atomic snapshot certification',
 'No actual execution or unconditional caller stack expiry conclusion']}
dest=OUT/'evidence.json'
if dest.exists():raise FileExistsError(dest)
dest.write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
print(json.dumps({'result':'PASS','checks':len(checks),'bytes':result['bytes'],'positions':len(rows)}))
