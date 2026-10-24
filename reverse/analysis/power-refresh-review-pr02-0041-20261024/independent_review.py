"""P-R02 offline encoding review. stdlib only; never imports author checkers.
No firmware execution, emulation, arithmetic input enumeration, or REA mutation.
"""
from pathlib import Path
import json
import struct

ROOT = Path('D:/Documents/PlatformIO/Projects/cuktech-ap01-firmware')
OUT = Path(__file__).resolve().parent
ROM = (ROOT/'roms/0041/ap01-1.0.2_0041.bin').read_bytes()
BASE = 0x9ffff000
checks = []

def check(label, actual, expected):
    checks.append(dict(label=label, actual=actual, expected=expected, passed=actual==expected))
    if actual != expected:
        raise AssertionError((label, actual, expected))

def signed(v, n):
    return v-(1<<n) if v>>(n-1) else v

def word(pc):
    return struct.unpack_from('<I', ROM, pc-BASE)[0]

def half(pc):
    return struct.unpack_from('<H', ROM, pc-BASE)[0]

def fields(pc):
    w=word(pc)
    op=w&127; rd=(w>>7)&31; f=(w>>12)&7; r1=(w>>15)&31; r2=(w>>20)&31
    if op in (3,19,103): return [op,rd,f,r1,signed(w>>20,12)]
    if op==35: return [op,f,r1,r2,signed(((w>>25)<<5)|((w>>7)&31),12)]
    if op==51: return [op,rd,f,r1,r2,w>>25]
    if op==99:
        imm=((w>>31)<<12)|(((w>>7)&1)<<11)|(((w>>25)&63)<<5)|(((w>>8)&15)<<1)
        return [op,f,r1,r2,hex(pc+signed(imm,13))]
    if op==111:
        imm=((w>>31)<<20)|(((w>>12)&255)<<12)|(((w>>20)&1)<<11)|(((w>>21)&1023)<<1)
        return [op,rd,hex(pc+signed(imm,21))]
    if op==11: return [op,rd,f,r1,r2,w>>25,(w>>25)&3]
    return [op,rd,f,r1,r2,w>>25]

def at(pc, expected, label='instruction fields'):
    check(f'{hex(pc)} {label}', fields(pc), expected)

def cli(pc, rd, imm):
    w=half(pc)
    check(f'{hex(pc)} c.li', [w&3,w>>13,(w>>7)&31,signed(((w>>2)&31)|(((w>>12)&1)<<5),6)], [1,2,rd,imm])

def cbranch(pc, target):
    w=half(pc)
    imm=(((w>>12)&1)<<8)|(((w>>10)&3)<<3)|(((w>>5)&3)<<6)|(((w>>3)&3)<<1)|(((w>>2)&1)<<5)
    check(f'{hex(pc)} compressed branch target',hex(pc+signed(imm,9)),hex(target))

# Author evidence is used only as a byte/location index, never executable code.
p02=json.loads((ROOT/'reverse/analysis/power-producer-p02-0041-20261024/static-checks.json').read_text())
p03=json.loads((ROOT/'reverse/analysis/deferred-refresh-p03-0041-20261024/evidence.json').read_text())
windows=[]
for group, source in [('P-02',p02),('P-03',p03)]:
    for w in source['windows']:
        start=int(w['start'],16); end=int(w['end_exclusive'],16)
        raw=ROM[start-BASE:end-BASE]
        indexed=b''.join(bytes.fromhex(i['hex']) for i in w['instructions'])
        check(f'{group}/{w["name"]} ROM/index bytes',raw.hex(),indexed.hex())
        pc=start; locations=[]
        while pc<end:
            n=4 if half(pc)&3==3 else 2
            locations.append(hex(pc)); pc+=n
        key='pc' if group=='P-02' else 'address'
        check(f'{group}/{w["name"]} independent instruction lengths',locations,[i[key] for i in w['instructions']])
        check(f'{group}/{w["name"]} end',pc,end)
        windows.append(dict(group=group,name=w['name'],start=hex(start),end_exclusive=hex(end),bytes=len(raw),instructions=len(locations)))

# Raw transport, fresh total/count/item address source, and ordinary helper.
original=json.loads((ROOT/'reverse/analysis/buzzer-backlight-0041-20261023.json').read_text())
dispatch=next(f for f in original['functions'] if f['address']=='0xa00a8582')
check('original dispatcher profile',dispatch['profile']['parameters']['language_id'],'RISCV:LE:32:ap01thead3')
retained=dispatch['raw_ranges'][0]
retained_start=int(retained['start'],16); retained_bytes=bytes.fromhex(retained['hex'])
for w in p02['windows'][:5]:
    s=int(w['start'],16); e=int(w['end_exclusive'],16)
    check(w['name']+' original retained raw',ROM[s-BASE:e-BASE].hex(),retained_bytes[s-retained_start:e-retained_start].hex())

# Adjacent registration is a bounded 40-byte original ROM bridge, not a new
# callback/library analysis. Decode both AUIPC/JALR targets and shared s4.
bridge=ROM[0xa005d126-BASE:0xa005d14e-BASE]
check('registration bridge bytes',bridge.hex(),'37d50aa0d2852328fa001305e50797601500e780c08637e50aa0d2851305c5ab97501500e7808078')
for pc in (0xa005d12a,0xa005d140):
    w=half(pc)
    check(hex(pc)+' c.mv a1,s4', [w&3,w>>12,(w>>7)&31,(w>>2)&31],[2,8,11,20])
for hi,lo,target in ((0xa005d126,0xa005d130,0xa00ad07e),(0xa005d13c,0xa005d142,0xa00adabc)):
    check(hex(hi)+' callback pointer',hex((word(hi)&0xfffff000)+signed(word(lo)>>20,12)),hex(target))
for pc,target in ((0xa005d134,0xa01b29a0),(0xa005d146,0xa01b28ce)):
    check(hex(pc)+' AUIPC/JALR call',hex(pc+(word(pc)&0xfffff000)+signed(word(pc+4)>>20,12)),hex(target))

for pc,e in {
0xa00a85a0:[35,0,8,10,-80],0xa00a85a4:[35,0,8,11,-79],0xa00a85a8:[35,2,8,12,-76],
0xa00a85d8:[99,0,10,15,'0xa00a8b72'],0xa00a8b76:[3,11,4,9,28],
0xa00a8b7e:[3,10,2,22,720],0xa00a8b88:[19,11,7,11,248],0xa00a8b8c:[111,1,'0xa0191652'],
0xa00a8bcc:[3,14,2,20,716],0xa00a8bd0:[3,11,4,14,6],0xa00a8bd4:[99,4,18,11,'0xa00a91c6'],
0xa00a91ce:[3,24,2,14,0],0xa00a3912:None,
0xa00a390e:[3,15,2,15,716],0xa00a392a:[3,14,5,11,0],0xa00a3930:[19,14,0,14,50],
0xa00a3934:[51,14,4,14,13,1],0xa00a3938:[3,13,5,15,4],0xa00a3944:[35,1,15,14,4],
0xa00a394a:[3,14,5,11,2],0xa00a3952:[19,14,0,14,50],0xa00a3956:[51,14,4,14,13,1],
0xa00a3966:[35,1,15,14,6],0xa00a396a:[19,10,6,10,6],0xa00a396e:[3,13,5,15,6],
0xa00a3972:[3,14,5,15,4],0xa00a3976:[51,14,0,14,13,1],0xa00a3982:[35,1,15,14,8],
}.items():
    if e is not None: at(pc,e)
cli(0xa00a3948,10,5)
cbranch(0xa00a3988,0xa00a3914)

# State, special branch, common tail, notification ordering and truncating sum.
for pc,e in {
0xa00a924a:[35,0,26,14,13],0xa00a9254:[111,1,'0xa00a3904'],0xa00a925c:[19,25,6,15,32],
0xa00a9260:[3,14,4,9,7],0xa00a926e:[111,1,'0xa00a36ca'],0xa00a927c:[111,1,'0xa00a36ca'],
0xa00a9288:[35,1,26,10,10],0xa00a928c:[19,25,6,25,8],0xa00a9290:[19,14,7,25,4],
0xa00a9298:[3,11,5,26,8],0xa00a92a0:[111,1,'0xa00a398c'],0xa00a92a6:[19,25,6,25,1024],
0xa00a92e2:[111,1,'0xa00a389c'],0xa00a92ec:[3,14,4,26,36],0xa00a92f2:[19,14,7,14,48],
0xa00a9316:[35,1,26,14,4],0xa00a931a:[19,25,6,25,1],0xa00a9330:[35,0,26,14,13],
0xa00a9334:[3,14,5,9,4],0xa00a9348:[111,1,'0xa0024906'],0xa00a935e:[111,1,'0xa00a3d80'],
0xa00a9370:[111,1,'0xa00a3904'],0xa00a938e:[3,12,5,12,8],0xa00a9394:[35,1,14,15,4],
0xa00a8bdc:[35,1,14,0,4],0xa00a8be6:[3,15,5,14,4],0xa00a8c10:[3,10,2,20,716],
0xa00a8c14:[3,11,5,10,4],0xa00a8c1a:[111,1,'0xa00a398c'],0xa00a8c26:[3,15,2,20,716],
0xa00a8c36:[35,1,15,19,12],0xa00a8c52:[111,1,'0xa00a536c'],
}.items(): at(pc,e)
cli(0xa00a9296,19,1)

# Vendor encoding fields, independently extracted; semantic authority remains
# the existing local SLEIGH excerpt, not an independent vendor ISA standard.
for pc,e in {
0xa00a3926:[11,15,1,10,14,16,0],0xa00a393c:[11,14,3,14,0,30,2],
0xa00a91d8:[11,17,3,17,10,20,0],0xa00a92aa:[11,25,5,24,23,32,0],
0xa00a9388:[11,12,1,13,10,16,0],0xa00a38d8:[11,0,5,20,18,32,0],
}.items(): at(pc,e,'vendor fields only')

# All numeric leaf constants are checked as raw immediates. Branch graph was
# read statically, not evaluated over a range of b/mode inputs.
first={0xa00a36da:400,0xa00a36e8:150,0xa00a36f6:75,0xa00a3708:50,0xa00a371a:100,
0xa00a3722:180,0xa00a3736:200,0xa00a373e:300,0xa00a3746:800,0xa00a3754:650,
0xa00a3762:450,0xa00a376c:451,0xa00a3774:650,0xa00a377c:1001,0xa00a3786:1400,0xa00a3790:1000}
second={0xa00a3796:225,0xa00a37a8:900,0xa00a37ae:1200,0xa00a37dc:100,0xa00a37f8:220,
0xa00a3800:330,0xa00a3822:550,0xa00a382a:670,0xa00a383c:1000,0xa00a3842:150,
0xa00a3848:180,0xa00a384e:650,0xa00a3854:450}
for pc,imm in first.items(): at(pc,[19,10,0,0,imm],'mode0 leaf')
for pc,imm in second.items(): at(pc,[19,14,0,0,imm],'mode8 threshold')
at(0xa00a379e,[99,7,12,14,'0xa00a3712'],'unsigned a2/threshold choice')
at(0xa00a3830,[19,14,7,10,253],'21/23 shared threshold classifier')

# P-03 necessary linkage only: cache overwrite, current mask, completion.
for pc,e in {
0xa00ad11c:[3,15,5,19,12],0xa00ad128:[35,2,18,15,80],
0xa00adb5c:[3,15,2,18,0],0xa00adb60:[35,2,22,15,84],
0xa00ad15e:[3,15,4,18,76],0xa00adba4:[3,15,4,22,76],
0xa00ad3fc:[35,2,18,0,80],0xa00af25a:[35,2,22,0,84],
0xa00af0cc:[3,14,2,18,0],0xa00af0da:[3,14,2,22,84],
0xa00af10c:[3,14,2,18,0],0xa00af116:[3,14,2,22,84],
0xa00f4938:[3,14,2,18,0],0xa00f4970:[3,14,2,18,0],0xa00f49e0:[3,14,2,18,0],
0xa00ab638:[35,0,9,15,76],0xa00a5394:[3,11,2,18,716],0xa00a539a:[35,1,11,0,12],
0xa00aef66:[99,0,10,0,'0xa00af12e'],
}.items(): at(pc,e)
cbranch(0xa00af180,0xa00af250)
direct=[]; indirect=[]; pc=0xa00ab628
while pc<0xa00ab6b0:
    w=half(pc); n=4 if w&3==3 else 2
    if n==4 and word(pc)&127==111 and (word(pc)>>7)&31==1: direct.append(fields(pc)[2])
    if n==4 and word(pc)&127==103: indirect.append(hex(pc))
    if n==2 and w&3==2 and w>>13==4 and (w>>12)&1 and ((w>>2)&31)==0 and ((w>>7)&31)!=0: indirect.append(hex(pc))
    pc+=n
check('complete direct call targets',direct,['0xa00dcee4','0xa008b51a','0xa008b51a','0xa008bd70'])
check('complete indirect calls (return excluded)',indirect,[])

result=dict(claim='P-R02',method='Independent stdlib ROM fields and static manual CFG review; no author validator imports/execution',
    rom_path=str(ROOT/'roms/0041/ap01-1.0.2_0041.bin'),rom_length=len(ROM),identity='Inherited CATALOG SHA-256 972db4c136c7ed9e24a83c07c1a7fd62040ca018b08ca285216d26b1fee3c6b9; not rehashed',
    windows=windows,checks=checks,passed=all(c['passed'] for c in checks),
    limits=['Static only; no execution or input model','Raw byte match does not independently validate vendor ISA semantics',
    'No complete animation callback or library re-review','No assertion of global absence of replay','No snapshot atomicity, physical unit or liveness guarantee'])
(OUT/'independent-checks.json').write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
print(json.dumps(dict(passed=result['passed'],checks=len(checks),windows=len(windows),bytes=sum(w['bytes'] for w in windows),instructions=sum(w['instructions'] for w in windows))))
