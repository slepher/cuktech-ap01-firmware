"""A60 selected old flows plus explicitly registered initializer short window.

No model/target/corpus query or prior technical script execution. New original
reads are fenced inside the registered [a008e4c4,a008e612) interval.
"""
import json
import re
from pathlib import Path
from capstone import Cs, CS_ARCH_RISCV, CS_MODE_RISCV32, CS_MODE_RISCVC

MAIN=Path('D:/Documents/PlatformIO/Projects/cuktech-ap01-firmware')
EV=MAIN/'evidence/rea-0041-20261017/evidence'
OUT=Path(__file__).resolve().parent
checks=[];sources=[]
def load(p):return json.loads(p.read_text(encoding='utf8'))
def check(label,actual,want):
    assert actual==want,(label,actual,want)
    checks.append(dict(label=label,value=actual))
def selected(r,wants,path,pointer):
    n=r['normalized_result'];a=n['assembly'];lines=[]
    for pc,text in wants.items():
        got=next(t for t in a if t.startswith(pc+':'))
        check(pc,got,pc+': '+text);lines.append(got)
    prof=r.get('analysis_profile')
    sources.append(dict(path=path,pointer=pointer,owner=n['procedure']['address'],
                        evidence_id=r['evidence_id'],
                        profile_digest=prof.get('digest') if isinstance(prof,dict) else prof,
                        selected_old_lines=lines))
    return a

r=load(EV/'whole-rom-retained-20261023-000.json')['structuredContent']
caller=selected(r,{
 '0xa005cc68':'lui a5, 0x62fc9','0xa005cc6c':'lbu a4, 0x57c, a5',
 '0xa005cc70':'addi a5, a5, 0x57c','0xa005cc74':'sw a5, -0x3c4, s0',
 '0xa005cc78':'c.beqz a4, 0xa005cd36','0xa005cd36':'jal ra, 0xa008e3ac',
 '0xa005cd3a':'c.j 0xa005cc9c','0xa005cd62':'lw a5, -0x3c4, s0',
 '0xa005cd66':'c.sw a0, 0x68, a5','0xa005ced2':'lw a5, -0x3c4, s0',
 '0xa005ced6':'lbu a5, 0x0, a5','0xa005ee9a':'lw a5, -0x3c4, s0',
 '0xa005ee9e':'c.li a0, 0x0','0xa005eea0':'lbu a5, 0x1, a5',
 '0xa005eeaa':'sw a0, -0x3c4, s0','0xa005eeb2':'lw a0, -0x3c4, s0',
},'evidence/rea-0041-20261017/evidence/whole-rom-retained-20261023-000.json',
 '/structuredContent/normalized_result')
slot=[s for s in caller if re.search(r', -0x3c4, s0$',s)]
check('exact caller frame-slot references',[s.split(':')[0] for s in slot],
      ['0xa005cc74','0xa005cd62','0xa005ced2','0xa005ee9a','0xa005eeaa','0xa005eeb2'])

r=load(EV/'whole-rom-retained-private-20261023-000.json')['structuredContent']
private=selected(r,{
 '0xa005be32':'lui s5, 0x62fc9','0xa005be3a':'addi a4, s5, 0x57c',
 '0xa005be48':'sw a5, 0x9c, a4','0xa005be4c':'sw s4, 0xa0, a4',
 '0xa005be50':'jal ra, 0xa008335e','0xa005be54':'addi a4, s5, 0x57c',
 '0xa005be58':'sw a4, -0x160, s0','0xa005be5e':'bge a0, zero, 0xa005beb6',
 '0xa005be62':'lui a4, 0xa01c4','0xa005bebe':'lui s5, 0xa01c4',
 '0xa005bec4':'lui a4, 0xa01c4','0xa005bee8':'lui a4, 0xa01c3',
 '0xa005bf18':'c.li a4, 0x2','0xa005c8ae':'lw a5, -0x160, s0',
 '0xa005c8b8':'sw zero, 0x9c, a5','0xa005c8bc':'sw zero, 0xa0, a5',
},'evidence/rea-0041-20261017/evidence/whole-rom-retained-private-20261023-000.json',
 '/structuredContent/normalized_result')
check('exact private frame-slot references',[s.split(':')[0] for s in private if re.search(r', -0x160, s0$',s)],
      ['0xa005be58','0xa005c8ae'])

r=load(EV/'screen-host-append-20261020-v2.evidence.json')['records'][3]
screen=selected(r,{
 '0xa00b2f94':'lui a5, 0x62fc9','0xa00b2f98':'addi a5, a5, 0x57c',
 '0xa00b2f9c':'c.lw a4, 0x40, a5','0xa00b2fa2':'sw a4, 0x2c, s2',
 '0xa00b2fa6':'c.sw a0, 0x40, a5','0xa00b2faa':'c.mv a0, s3',
 '0xa00b2fac':'jal ra, 0xa0080dfe',
},'evidence/rea-0041-20261017/evidence/screen-host-append-20261020-v2.evidence.json',
 '/records/3/normalized_result')

a21_path=MAIN/'reverse/analysis/png-info-lifecycle-a21-0041-20261023/instruction-evidence.json'
a21=load(a21_path)
iw=[w for w in a21['windows'] if 0xa008e3ac<=int(w['start'],16)<0xa008e876]
by_pc={r['address']:r for w in iw for r in w['rows']}
for pc,text in {
 '0xa008e3c4':'lui s2, 0x62fc9','0xa008e3c8':'addi a1, zero, 0x210',
 '0xa008e3cc':'addi a0, s2, 0x57c','0xa008e3d0':'jal -0xd642',
 '0xa008e3d4':'addi s1, s2, 0x57c','0xa008e4c0':'addi s4, s1, 0x100',
}.items():check('inherited A21 '+pc,by_pc[pc]['instruction'],text)
a25_path=MAIN/'reverse/analysis/pixel-memory-contract-a25-0041-20261023/evidence.json'
a25=load(a25_path)
a25_init=[r for r in a25['instructions'] if 0xa008e3ac<=int(r['va'],16)<0xa008e876]
intervals=[]
for row in a25_init:
    start=int(row['va'],16);end=start+len(bytes.fromhex(row['raw']))
    if intervals and intervals[-1][1]==start:intervals[-1][1]=end
    else:intervals.append([start,end])
check('A25 retained initializer interval',[[hex(a),hex(b)] for a,b in intervals],
      [['0xa008e3ac','0xa008e4b8']])
check('G address arithmetic',0x62fc9000+0x57c,0x62fc957c)
for off in [0x1c4,0x1c8]:check('inherited clear covers full word '+hex(off),off+4<=0x210,True)

# Management registered exact missing-window upgrade before these reads.
ROM=MAIN/'roms/0041/ap01-1.0.2_0041.bin'
check('original length',ROM.stat().st_size,6769704)
decoder=Cs(CS_ARCH_RISCV,CS_MODE_RISCV32|CS_MODE_RISCVC)
new_anchors=[]
def raw(pc,n):
    assert 0xa008e4c4<=pc and pc+n<=0xa008e612
    with ROM.open('rb') as fh:
        fh.seek(pc-0x9ffff000);return fh.read(n)
def inst(pc,text):
    n=4 if int.from_bytes(raw(pc,2),'little')&3==3 else 2
    b=raw(pc,n);rows=list(decoder.disasm(b,pc))
    check('new sparse decode '+hex(pc),[(i.mnemonic+' '+i.op_str) for i in rows],[text])
    new_anchors.append(dict(address=hex(pc),raw=b.hex(),instruction=text))
for pc,text in {
 0xa008e4c4:'c.bnez a0, 0x42',0xa008e506:'c.li a5, 0x18',
 0xa008e508:'c.sw a5, 0x74(s1)',0xa008e50a:'sw zero, 0x78(s1)',
 0xa008e50e:'sw zero, 0x7c(s1)',0xa008e512:'sb s8, 0x80(s1)',
 0xa008e516:'jal -0x6a10',0xa008e51a:'c.lw a0, 0x58(s1)',
 0xa008e51c:'c.li a5, 4',0xa008e51e:'sw a5, 0x1c4(s1)',
 0xa008e522:'sw zero, 0x1c8(s1)',0xa008e526:'sw zero, 0x1cc(s1)',
}.items():inst(pc,text)
for pc,reg,off,target in [(0xa008e51e,15,0x1c4,0x62fc9740),
                          (0xa008e522,0,0x1c8,0x62fc9744),
                          (0xa008e526,0,0x1cc,0x62fc9748)]:
    w=int.from_bytes(raw(pc,4),'little');im=((w>>25)<<5)|((w>>7)&31)
    im=im-4096 if im&2048 else im
    check('independent SW fields '+hex(pc),(w&127,(w>>12)&7,(w>>15)&31,(w>>20)&31,im),
          (0x23,2,9,reg,off))
    check('exact target '+hex(pc),0x62fc957c+im,target)
h=int.from_bytes(raw(0xa008e4c4,2),'little')
im=(((h>>12)&1)<<8)|(((h>>10)&3)<<3)|(((h>>5)&3)<<6)|(((h>>3)&3)<<1)|(((h>>2)&1)<<5)
im=im-512 if im&256 else im
check('independent normal compressed gate',(h&3,h>>13,((h>>7)&7)+8,0xa008e4c4+im),
      (1,7,10,0xa008e506))
h=int.from_bytes(raw(0xa008e51c,2),'little')
im=(((h>>12)&1)<<5)|((h>>2)&31);im=im-64 if im&32 else im
check('independent CLI value',(h&3,h>>13,(h>>7)&31,im),(1,2,15,4))
check('A25 displayed normal s1 definitions',
      [(r['va'],r['asm']) for r in a25_init if int(r['va'],16)>=0xa008e3d4 and
       re.match(r'(?:c\.)?(?:mv|li|lui|lw|addi|add|sub|andi|or|xor|and|srli|slli) s1(?:,| )',r['asm'])],
      [('0xa008e3d4','addi s1, s2, 0x57c')])

result=dict(status='PASS-registered-initializer-field-increment',claim='J08/4',task='A60',baseline='bd457a6',
 checks=checks,sources=sources,
 inherited_initializer=dict(paths=[str(a21_path.relative_to(MAIN)),str(a25_path.relative_to(MAIN))],
   windows=[{k:w[k] for k in ['name','start','end_exclusive']} for w in iw],
   known_clear='G=0x62fc957c length0x210; both slot words initially cleared, inherited new writer0',
   last_known_base='0xa008e4c0 s4=G+0x100',
   prior_selected_export_gap=['0xa008e4c4','0xa008e612'],
   limitation='Gap in these selected exports only; no claim about all retained files or actual missing code'),
 new_original_anchors=new_anchors,
 original_identity=dict(path=str(ROM),length=6769704,mapping='VA-0x9ffff000',
   inherited_sha256='972db4c136c7ed9e24a83c07c1a7fd62040ca018b08ca285216d26b1fee3c6b9',digest_recomputed=False),
 new_input=dict(authorized_interval=['0xa008e4c4','0xa008e612'],
   exploratory_instruction_windows=[['0xa008e4c4','0xa008e4f4'],['0xa008e506','0xa008e536']],
   exploratory_window_bytes=96,stopped_after_exact_writes_found=True,
   decoder='Capstone 5.0.7 RV32/RVC; independent SW/CLI/C.BNEZ fields'),
 result='Normal initializer s1=G path writes stride4/head0 at exact slots; registration N.word0=D still unknown',
 new_business='Specific initializer state relation only, not a new registration body or complete fsdrv',
 new_decompilation=0,
 limits=['No dynamic CFG/alias proof; caller-saved pointers not propagated through opaque calls',
 'Direct non-target offsets identified only to delimit G uses, not restored as new field behavior',
 'No A58/A59 corpus query repeated, no model/target/old-script execution',
 'Only registered initializer fields read; no new callee body, known zeroing inherited, registration remains unknown',
 's1=G continuity uses prior ordinary body and normal callee-preserved-register ABI; error gate not certified'])
(OUT/'evidence.json').write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n',encoding='utf8')
print(f'PASS {len(checks)} bounded checks; registered sparse original fields, new decompilation0')
