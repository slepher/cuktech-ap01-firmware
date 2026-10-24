"""Independent P-R14 raw-field review. stdlib only; no author code import/run."""
import json
from pathlib import Path

ROOT = Path('D:/Documents/PlatformIO/Projects/cuktech-ap01-firmware')
OUT = Path(__file__).resolve().parent
BASE = 0x9ffff000
IDENTITY = '972db4c136c7ed9e24a83c07c1a7fd62040ca018b08ca285216d26b1fee3c6b9'
rom = (ROOT/'roms/0041/ap01-1.0.2_0041.bin').read_bytes()
metadata = json.loads((ROOT/'roms/0041/ap01-1.0.2_0041.json').read_text(encoding='utf-8'))
assert len(rom) == metadata['size'] == 6769704
assert metadata['sha256'] == IDENTITY
old = json.loads((ROOT/'reverse/rehost/charge-complete-0041.json').read_text(encoding='utf-8'))
bundle = json.loads((ROOT/'evidence/rea-0041-20261017/evidence/whole-rom-private-20261023.evidence.json').read_text(encoding='utf-8'))
handler = next(x for x in bundle['records'] if x.get('evidence_id') == 'ev_6044e70f4a6f785a665e891cedb82fc897de52716642b9e9bbe0538f9b9d4c40')
assert handler['subject']['digest']['sha256'] == old['source_sha256'] == IDENTITY
assert handler['analysis_profile']['digest'] == 'b6368dd18431e8113aa5026c713d41e648ab0f6ddd9421ff6c4a49e23b3cd2f3'
assert handler['analysis_profile']['parameters']['language_id'] == 'RISCV:LE:32:ap01thead2'
assert 'analysis_profile' not in old['records'][19]
author_data = json.loads((ROOT/'reverse/analysis/port-control-p14-0041-20261024/static-evidence.json').read_text(encoding='utf-8'))
spans = [('switch_actions',0xa00f7c98,0xa00f7d36), ('safe_on',0xa00f7d8a,0xa00f7dec),
         ('safe_off',0xa00f7fca,0xa00f8016), ('setter',0xa0191834,0xa0191872),
         ('masks',0xa00f5970,0xa00f5a04), ('safe_feedback',0xa00f5b0a,0xa00f5b6c),
         ('switch_feedback',0xa00f5b6c,0xa00f5b86)]
checks = []
def check(label, condition):
    assert condition, label
    checks.append(label)
def raw(a,n=4): return rom[a-BASE:a-BASE+n]
def word(a): return int.from_bytes(raw(a),'little')
def sx(v,n): return v-(1<<n) if v>>(n-1) else v
def fields(a):
    w=word(a)
    return (w&127,(w>>12)&7,(w>>7)&31,(w>>15)&31,(w>>20)&31,sx(w>>20,12))
def i(a,op,fun,rd,rs,imm): check(hex(a),fields(a)[:4]==(op,fun,rd,rs) and fields(a)[5]==imm)
def s(a,fun,rs1,rs2,imm):
    w=word(a)
    check(hex(a),(w&127,(w>>12)&7,(w>>15)&31,(w>>20)&31,sx(((w>>25)<<5)|((w>>7)&31),12))==(35,fun,rs1,rs2,imm))
def branch(a,fun,rs1,rs2,dst):
    w=word(a)
    imm=((w>>31)<<12)|(((w>>7)&1)<<11)|(((w>>25)&63)<<5)|(((w>>8)&15)<<1)
    check(hex(a),(w&127,(w>>12)&7,(w>>15)&31,(w>>20)&31,a+sx(imm,13))==(99,fun,rs1,rs2,dst))
def cli(a,rd,imm):
    w=int.from_bytes(raw(a,2),'little')
    check(hex(a),(w&3,w>>13,(w>>7)&31,sx((((w>>12)&1)<<5)|((w>>2)&31),6))==(1,2,rd,imm))
def candi(a,rd,imm):
    w=int.from_bytes(raw(a,2),'little')
    check(hex(a),(w&3,w>>13,(w>>10)&3,8+((w>>7)&7),sx((((w>>12)&1)<<5)|((w>>2)&31),6))==(1,4,2,rd,imm))
def jal(a,dst):
    w=word(a)
    imm=((w>>31)<<20)|(((w>>12)&255)<<12)|(((w>>20)&1)<<11)|(((w>>21)&1023)<<1)
    check(hex(a),(w&127,(w>>7)&31,a+sx(imm,21))==(111,1,dst))
windows=[]
for j,(name,start,end) in enumerate(spans):
    pc=start; ins=[]
    while pc<end:
        size=4 if raw(pc,1)[0]&3==3 else 2
        check('boundary '+hex(pc),pc+size<=end)
        ins.append({'address':hex(pc),'hex':raw(pc,size).hex()});pc+=size
    check('author blob '+name,raw(start,end-start).hex()==author_data['windows'][j]['hex'])
    if name!='setter':
        source=handler['normalized_result']['assembly'] if start>=0xa00f7c98 else old['records'][19]['assembly']
        retained=[x for x in source if start<=int(x.split(':')[0],16)<end]
        check('retained boundaries '+name,[int(x.split(':')[0],16) for x in retained]==[int(x['address'],16) for x in ins])
    windows.append({'name':name,'start':hex(start),'end':hex(end),'hex':raw(start,end-start).hex(),'instructions':ins})
for a,v in [(0xa00f7cca,0),(0xa00f7d04,1),(0xa00f7dce,1),(0xa00f7ffe,0)]:cli(a,11,v)
for a in [0xa00f7cc6,0xa00f7d00]:i(a,3,4,10,9,7)
for a in [0xa00f7cce,0xa00f7d08]:i(a,19,7,10,10,255)
for a in [0xa00f7db0,0xa00f7fe2]:i(a,3,4,15,9,4)
branch(0xa019183c,7,10,15,0xa0191870)
i(0xa0191838,3,4,15,15,28)
check('global count LUI',word(0xa0191834)==0x62fcb7b7)
i(0xa0191848,19,0,15,0,0x265)
s(0xa019184c,0,8,10,-28);s(0xa019185c,0,8,11,-27)
s(0xa0191850,1,8,15,-24);s(0xa0191860,2,8,15,-20)
i(0xa0191854,19,0,10,8,-24);i(0xa0191858,19,0,15,8,-28)
for a,dst in [(0xa00f7cd2,0xa0191834),(0xa00f7d0c,0xa0191834),(0xa00f7dd6,0xa01917d0),(0xa00f8000,0xa01917d0),(0xa0191864,0xa01951e2),(0xa00f5b7e,0xa00f40ee)]:jal(a,dst)
i(0xa00f5b40,3,4,14,9,12);i(0xa00f5b78,3,5,13,9,10)
branch(0xa00f5b12,1,14,18,0xa00f59ba);branch(0xa00f5b74,1,11,18,0xa00f52ec)
s(0xa00f7dde,1,25,15,8);s(0xa00f8008,1,25,15,8)
candi(0xa00f5972,15,16);candi(0xa00f59bc,15,8)
for a in [0xa00f7db6,0xa00f7fe8]:i(a,19,0,13,15,-24)
branch(0xa00f7dba,6,14,13,0xa00f7dc2);branch(0xa00f7fec,6,14,13,0xa00f7ff4)
i(0xa00f7dbe,19,0,23,15,-23);i(0xa00f7ff0,19,0,24,15,-23)
i(0xa00f7dc2,19,0,22,23,-1);i(0xa00f7ff4,19,0,9,24,-1)
i(0xa00f7dc6,19,7,22,22,255);i(0xa00f7ff8,19,7,9,9,255)
# Sparse necessary premise checks, outside the author's seven spans.
i(0xa00f61ea,3,2,18,10,0);i(0xa00f61fc,3,2,9,18,16)
i(0xa00f531e,3,2,15,23,16);s(0xa00f532a,2,8,15,-132)
s(0xa00f410e,2,8,13,-52);i(0xa00f4158,3,2,13,8,-52)
check('helper c.bnez a3 to nonzero arm',raw(0xa00f4214,2).hex()=='fdf6')
check('LE descriptor bytes',(0x265).to_bytes(2,'little')==bytes([0x65,2]))
result={'status':'PASS','checks':len(checks),'check_labels':checks,'identity_basis':'metadata + source subjects, length checked; full hash inherited, not recomputed',
        'source_sha256':IDENTITY,'source_mapping':'offset=VA-0x9ffff000','windows':windows,
        'handler_evidence':handler['evidence_id'],'handler_profile':handler['analysis_profile']['digest'],
        'historical_feedback_evidence':old['records'][19]['evidence_id'],'historical_feedback_profile':'not supplied',
        'limits':['stdlib raw RV32 I/S/B/J and selected compressed LI field checks; not a full disassembler',
                  'all seven raw spans re-read; author JSON compared only as data; no author validator run/import',
                  'custom0 at callback selector extraction retained opaque; type/nibble downstream mapping read from old assembly',
                  'ownership/copy/cmd63 producer inherited; no target execution or transaction confirmation']}
premises=[('handler_state',handler['normalized_result']['assembly'],[(0xa00f61e6,0xa00f6200)]),
          ('callback_selector',old['records'][19]['assembly'],[(0xa00f531e,0xa00f5374)]),
          ('helper_argument',old['records'][18]['assembly'],[(0xa00f410a,0xa00f4112),(0xa00f4158,0xa00f4162),(0xa00f4210,0xa00f4224)])]
result['necessary_sparse_premises']=[]
for name,assembly,ranges in premises:
    selected=[]
    for line in assembly:
        a=int(line.split(':')[0],16)
        if any(lo<=a<hi for lo,hi in ranges):
            n=4 if raw(a,1)[0]&3==3 else 2
            selected.append({'address':hex(a),'hex':raw(a,n).hex(),'retained_assembly':line})
    result['necessary_sparse_premises'].append({'name':name,'instructions':selected})
(OUT/'review-evidence.json').write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
print(json.dumps({'status':result['status'],'checks':len(checks),'windows':len(windows),'bytes':sum(b-a for _,a,b in spans)}))
