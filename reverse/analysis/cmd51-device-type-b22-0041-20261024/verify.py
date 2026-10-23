"""B22 static classification evidence; no dispatcher execution/input replay."""
import json
from pathlib import Path
from capstone import Cs, CS_ARCH_RISCV, CS_MODE_RISCV32, CS_MODE_RISCVC

HERE=Path(__file__).resolve().parent
REV=HERE.parents[1]
MAIN=Path('D:/Documents/PlatformIO/Projects/cuktech-ap01-firmware')
BASE=0x9ffff000
rom=(MAIN/'roms/0041/ap01-1.0.2_0041.bin').read_bytes()
old=next(f for f in json.loads((REV/'analysis/buzzer-backlight-0041-20261023.json').read_text())['functions'] if f['address']=='0xa00a8582')
assert old['evidence_id']=='ev_6f9f82e5daf0540a1c24a0b85daa2e394785391692765e5e3e100eb7b37ed94c'
retained=old['raw_ranges'][0]
old_start=int(retained['start'],16)
old_bytes=bytes.fromhex(retained['hex'])

def raw(pc,n):return rom[pc-BASE:pc-BASE+n]
def u32(pc):return int.from_bytes(raw(pc,4),'little')
def sx(v,n):return v-(1<<n) if v&(1<<(n-1)) else v

cs=Cs(CS_ARCH_RISCV,CS_MODE_RISCV32|CS_MODE_RISCVC)
ranges=[('record_loop_and_primary_decision',0xa00a93a4,0xa00a9454),
        ('primary_branches_and_secondary_prefix',0xa00a947e,0xa00a9504),
        ('new_type_join',0xa00a9504,0xa00a9512),
        ('secondary_branches_and_item_scalar',0xa00a960a,0xa00a972a),
        ('record_and_item_advance',0xa00a9738,0xa00a973e)]
rows=[]
branches=[]
for label,start,end in ranges:
    assert raw(start,end-start)==old_bytes[start-old_start:end-old_start]
    pc=start
    while pc<end:
        h=int.from_bytes(raw(pc,2),'little')
        size=2 if h&3!=3 else 4
        assert pc+size<=end
        code=raw(pc,size)
        ins=next(cs.disasm(code,pc,count=1),None)
        if ins is None:
            assert pc in [0xa00a96c0,0xa00a96f0,0xa00a9714]
            asm='th.extu a3,a3,15,0 (inherited local rule)'
        else:
            asm=ins.mnemonic+' '+ins.op_str
        rows.append({'window':label,'pc':hex(pc),'raw':code.hex(),'asm':asm})
        if size==4 and (w:=u32(pc))&127==0x63:
            imm=((w>>31)<<12)|(((w>>7)&1)<<11)|(((w>>25)&63)<<5)|(((w>>8)&15)<<1)
            branches.append({'pc':hex(pc),'target':hex(pc+sx(imm,13)),'kind':'B','funct3':(w>>12)&7})
        if size==2 and h&3==1 and h>>13==5:
            imm=(((h>>12)&1)<<11)|(((h>>11)&1)<<4)|(((h>>9)&3)<<8)|(((h>>8)&1)<<10)|(((h>>7)&1)<<6)|(((h>>6)&1)<<7)|(((h>>3)&7)<<1)|(((h>>2)&1)<<5)
            branches.append({'pc':hex(pc),'target':hex(pc+sx(imm,12)),'kind':'C.J'})
        pc+=size

checks=[]
def require(pc,condition,label):
    assert condition,(hex(pc),label)
    checks.append({'pc':hex(pc),'label':label})

# Record/classification loads and final byte publication, independently field-decoded.
for pc,rd,rs1,offset in [(0xa00a9410,14,18,4),(0xa00a94c0,14,18,6),
                         (0xa00a96b4,12,27,24),(0xa00a96e4,12,27,24),
                         (0xa00a9708,12,27,24)]:
    w=u32(pc)
    require(pc,(w&127,(w>>12)&7,(w>>7)&31,(w>>15)&31,sx(w>>20,12))==(3,5,rd,rs1,offset),'LHU unsigned field')
for pc,rd,rs1,offset in [(0xa00a9408,15,27,13),(0xa00a9504,14,27,14)]:
    w=u32(pc)
    require(pc,(w&127,(w>>12)&7,(w>>7)&31,(w>>15)&31,sx(w>>20,12))==(3,4,rd,rs1,offset),'LBU active/type field')
w=u32(0xa00a950e)
require(0xa00a950e,(w&127,(w>>12)&7,(w>>20)&31,(w>>15)&31,sx(((w>>25)<<5)|((w>>7)&31),12))==(35,0,15,27,14),'publish a5 as byte item+0e')

for pc in [0xa00a96c0,0xa00a96f0,0xa00a9714]:
    w=u32(pc)
    require(pc,(w&127,(w>>12)&7,(w>>26)&63,(w>>20)&63,(w>>7)&31,(w>>15)&31)==(11,3,15,0,13,13),'extu a3,a3 bits15..0')
model_path=MAIN/'evidence/rea-0041-20261017/ghidra/Ghidra/Processors/RISCV/data/languages/ap01thead2.sinc'
text=model_path.read_text()
at=text.index(':th.extu rd,rs1,15,0 ')
rule=text[at:text.index('\n}',at)+2]
assert 'rd = value >> 16' in rule

# Static constant extraction, never evaluate the dispatcher on supplied inputs.
constants={}
for pc in [0xa00a93da,0xa00a93e4,0xa00a9422,0xa00a942e,0xa00a943c,0xa00a9444,0xa00a944c,
           0xa00a947e,0xa00a9488,0xa00a9490,0xa00a949a,0xa00a94a2,0xa00a94ae,0xa00a94b8,
           0xa00a94c4,0xa00a94d2,0xa00a94e0,0xa00a94ee,0xa00a94f8,
           0xa00a960a,0xa00a9614,0xa00a9622,0xa00a962c,0xa00a9638,0xa00a9642,
           0xa00a9650,0xa00a965c,0xa00a966a,0xa00a9674,0xa00a9682,0xa00a968c,
           0xa00a96a2,0xa00a96ac,0xa00a96d6]:
    w=u32(pc)
    assert w&127==0x13 and (w>>12)&7==0
    base={(21):0x2000,(26):0x7000,(13):0x1000,(0):0}.get((w>>15)&31)
    if pc==0xa00a94ae:base=0x3000  # preceding c.lui a3,3
    assert base is not None
    constants[hex(pc)]=hex(base+sx(w>>20,12))
assert constants['0xa00a93da']=='0x183d' and constants['0xa00a93e4']=='0x751b'
assert constants['0xa00a94ae']=='0x339b'
old_assembly={int(line[2:10],16):line for line in old['assembly']}
for branch in branches:
    pc=int(branch['pc'],16)
    assert int(branch['target'],16)==int(old_assembly[pc].rsplit('0x',1)[1],16)
for pc in [0xa00a96bc,0xa00a96ec,0xa00a9710]:
    require(pc,u32(pc)==0xfff60693,'subtract one before u16 mask')
for pc in [0xa00a96ca,0xa00a971e]:
    require(pc,u32(pc)>>20==169,'threshold 169')
require(0xa00a96fa,u32(0xa00a96fa)>>20==159,'threshold 159')
for pc,value in [(0xa00a9418,0x12),(0xa00a9432,0x10),(0xa00a9482,0x10),
                 (0xa00a9494,0x10),(0xa00a949e,0x13),(0xa00a94a6,1),
                 (0xa00a94b2,0x14),(0xa00a94bc,0x11),(0xa00a94c8,0x1e),
                 (0xa00a94d6,0x16),(0xa00a94e4,0x18),(0xa00a94f2,0x17),
                 (0xa00a94fc,2),(0xa00a9502,0x1a),(0xa00a960e,0x1b),
                 (0xa00a9618,2),(0xa00a961e,0x1f),(0xa00a9626,0x1c),
                 (0xa00a963c,0x1d),(0xa00a9646,2),(0xa00a964c,0x19),
                 (0xa00a9660,4),(0xa00a966e,3),(0xa00a9678,2),
                 (0xa00a967e,6),(0xa00a9686,5),(0xa00a9694,2),
                 (0xa00a9698,0xc),(0xa00a96a6,0xd),(0xa00a96da,2),
                 (0xa00a96e0,8),(0xa00a96c4,2),(0xa00a96f4,2),
                 (0xa00a96fe,7),(0xa00a9704,0xb),(0xa00a9718,2)]:
    h=int.from_bytes(raw(pc,2),'little')
    require(pc,(h&3,h>>13,(h>>7)&31,sx((((h>>12)&1)<<5)|((h>>2)&31),6))==(1,2,15,value),'new_type C.LI value')
require(0xa00a9630,u32(0xa00a9630)==0x02000793,'new_type 0x20 ordinary LI')

overlap=[]
for filename in ['charge-complete-0041.json','system-complete-0041.json','charge-0041-round4.json','guide-0041-round2.json','page-logic-0041.json']:
    path=MAIN/'reverse/rehost'/filename
    contents=path.read_text(encoding='utf-8').lower()
    overlap.append({'file':str(path),'query':'a00a94c0|a00a9504|0x751b|0x711e|b2d4',
                    'matching_terms':[t for t in ['a00a94c0','a00a9504','0x751b','0x711e','b2d4'] if t in contents]})
result={'static_only':True,'retained_evidence_id':old['evidence_id'],
        'prior_raw_matches_selected_original':True,'windows':[{'name':n,'start':hex(a),'end_exclusive':hex(b)} for n,a,b in ranges],
        'instructions':rows,'branch_targets':branches,'field_checks':checks,'derived_constants':constants,
        'vendor_rule':{'path':str(model_path),'text':rule},'bounded_overlap':overlap,
        'inherited':['fallback 0/15','five-pointer lifecycle and item+0e post-join updates','cmd52/frames/consumers'],
        'limits':['Old dispatcher bytes/pseudocode already existed; new work is normal classification interpretation.',
                  'No dispatcher execution, input replay, full export, resource-catalog rebuild or driver expansion.',
                  'Record ID and item+18 protocol/brand names and scalar producer remain unknown.']}
(HERE/'evidence.json').write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
print(json.dumps({'passed':True,'selected_bytes':sum(b-a for _,a,b in ranges),'instructions':len(rows),'branches':len(branches),'field_checks':len(checks)}))
