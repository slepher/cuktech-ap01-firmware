"""A62: bounded direct-caller metadata, then registered initializer gap fields.

Never executes a target, instruction, model, prior script or REA query.
"""
import json
from pathlib import Path
from capstone import Cs,CS_ARCH_RISCV,CS_MODE_RISCV32,CS_MODE_RISCVC

MAIN=Path('D:/Documents/PlatformIO/Projects/cuktech-ap01-firmware')
OUT=Path(__file__).resolve().parent
checks=[]
def load(p):return json.loads(p.read_text(encoding='utf8'))
def check(label,value,want):
    assert value==want,(label,value,want)
    checks.append(dict(label=label,value=value))
idx=load(MAIN/'reverse/analysis/whole-rom-coverage-0041-20261023-round1.json')
check('index identity',idx['rom_sha256'],'972db4c136c7ed9e24a83c07c1a7fd62040ca018b08ca285216d26b1fee3c6b9')
callers=[]
for i,f in enumerate(idx['functions']):
    if '0xa008aec0' in f.get('direct_calls',{}).get('callees',[]):
        callers.append(dict(pointer='/functions/'+str(i),address=f['address'],extent=f['extent'],
          directcall_evidence=f['direct_calls']['evidence_id'],dossiers=f['dossiers'],
          historical_dossier=f['historical_dossier'],source_paths=f['source_paths']))
check('bounded inverse direct callers',[r['address'] for r in callers],
 ['0xa0082914','0xa0084b96','0xa008bc64','0xa008bf6e','0xa008e3ac',
  '0xa00d733a','0xa00d9452','0xa00e0ac8','0xa00ebb90'])
check('this index no caller dossiers',all(r['dossiers']==[] and r['historical_dossier'] is None for r in callers),True)
fsrefs=[r for r in idx['source_paths'][239]['references'] if r['owner']['procedure']=='0xa008e3ac']
check('initializer fs-path source-xrefs',[r['address'] for r in fsrefs],['0xa008e800','0xa008e820'])

a21path=MAIN/'reverse/analysis/png-info-lifecycle-a21-0041-20261023/instruction-evidence.json'
a21=load(a21path);oldrows={r['address']:r for w in a21['windows'] for r in w['rows']}
for pc,text in [('0xa008291e','lui a0, 0x62fc9'),('0xa0082922','addi a0, a0, 0x68c'),
               ('0xa0082926','jal 0x859a'),('0xa008e75e','lui s1, 0x62fc9'),
               ('0xa008e764','addi a1, zero, 0x34')]:
    check('old A21 anchor '+pc,oldrows[pc]['instruction'],text)
timer=load(MAIN/'reverse/analysis/pogo-timer-lifecycle-c01-0041-20261023/instruction-evidence.json')
trows={r['address']:r for w in timer['windows'] for r in w['instructions']}
check('old timer list hi',trows['0xa008bc74']['decode'],'lui a0, 0x62fc9')
check('old timer list lo',trows['0xa008bc78']['decode'],'addi a0, a0, 0x5f0')
check('PNG different actual header',0x62fc9000+0x68c,0x62fc968c)
check('timer different actual header',0x62fc9000+0x5f0,0x62fc95f0)

ROM=MAIN/'roms/0041/ap01-1.0.2_0041.bin'
check('original length',ROM.stat().st_size,6769704)
d=Cs(CS_ARCH_RISCV,CS_MODE_RISCV32|CS_MODE_RISCVC)
new=[]
def raw(a,n):
    assert 0xa008e768<=a and a+n<=0xa008e82c
    with ROM.open('rb') as fh:fh.seek(a-0x9ffff000);return fh.read(n)
def inst(a,text,kind='registration'):
    n=4 if int.from_bytes(raw(a,2),'little')&3==3 else 2
    b=raw(a,n);r=list(d.disasm(b,a))
    check('new sparse '+hex(a),[i.mnemonic+' '+i.op_str for i in r],[text])
    new.append(dict(address=hex(a),raw=b.hex(),instruction=text,kind=kind))
for a,t in {
 0xa008e768:'addi a0, s1, 0x74c',0xa008e76c:'jal -0xd9de',
 0xa008e7d8:'lui a0, 0x62fc9',0xa008e7de:'addi a0, a0, 0x740',
 0xa008e7e2:'jal -0x3922',0xa008e7e6:'c.bnez a0, 0x40',
 0xa008e7e8:'lui s1, 0xa0263',0xa008e826:'addi s1, s1, 0x74c',
 0xa008e82a:'c.sw s1, 0(a0)',
}.items():inst(a,t)
# Incidental future seeds only: no s2 identity or D-slot mapping is asserted.
for a,t in {
 0xa008e776:'sb a5, 0x1d0(s2)',0xa008e77a:'addi a5, s2, 0x180',
 0xa008e780:'lui a4, 0xa00ef',0xa008e784:'addi a4, a4, 0x468',
 0xa008e788:'c.sw a4, 0x5c(a5)',
}.items():inst(a,t,kind='incidental-unresolved-s2-base')

def sx(w,n):return w-(1<<n) if w&(1<<(n-1)) else w
for a,rd,rs,imm in [(0xa008e768,10,9,0x74c),(0xa008e7de,10,10,0x740),(0xa008e826,9,9,0x74c)]:
    w=int.from_bytes(raw(a,4),'little')
    check('independent ADDI '+hex(a),(w&127,(w>>12)&7,(w>>7)&31,(w>>15)&31,sx(w>>20,12)),
          (0x13,0,rd,rs,imm))
for a,target in [(0xa008e76c,0xa0080d8e),(0xa008e7e2,0xa008aec0)]:
    w=int.from_bytes(raw(a,4),'little')
    q=((w>>31)<<20)|(((w>>12)&255)<<12)|(((w>>20)&1)<<11)|(((w>>21)&1023)<<1)
    check('independent JAL '+hex(a),(w&127,(w>>7)&31,a+sx(q,21)),(0x6f,1,target))
h=int.from_bytes(raw(0xa008e7e6,2),'little')
q=(((h>>12)&1)<<8)|(((h>>10)&3)<<3)|(((h>>5)&3)<<6)|(((h>>3)&3)<<1)|(((h>>2)&1)<<5)
check('independent node nonzero gate',(h&3,h>>13,((h>>7)&7)+8,0xa008e7e6+sx(q,9)),
      (1,7,10,0xa008e826))
h=int.from_bytes(raw(0xa008e82a,2),'little')
q=(((h>>10)&7)<<3)|(((h>>6)&1)<<2)|(((h>>5)&1)<<6)
check('independent node.word0 SW',(h&3,h>>13,((h>>7)&7)+8,((h>>2)&7)+8,q),(0,6,10,9,0))
check('actual list parameter',0x62fc9000+0x740,0x62fc9740)
check('actual D pointer',0x62fc9000+0x74c,0x62fc974c)

result=dict(status='PASS-static-registered-node-D-bridge',claim='J08/5',task='A62',baseline='bd457a6',
 checks=checks,metadata_callers=callers,metadata_boundary='Only this index direct-call edges; indirect/undefined functions may be absent',
 source_xrefs=fsrefs,inherited_A21=dict(path=str(a21path.relative_to(MAIN)),
   selected_source_rows=[oldrows[p] for p in ['0xa008e75e','0xa008e764']],
   helper='a008aec0(list*) -> new linked node, A21/A22; no body rerun'),
 original=dict(path=str(ROM),length=6769704,mapping='VA-0x9ffff000',
 sha256_inherited=idx['rom_sha256'],digest_recomputed=False),
 new_anchors=new,
 exploratory_windows=[['0xa008e768','0xa008e798'],['0xa008e794','0xa008e7c4'],
                      ['0xa008e7c4','0xa008e7f4'],['0xa008e826','0xa008e82c']],
 exploratory_requested_bytes=150,exploratory_unique_bytes=146,
 new_contract='list=0x62fc9740; N=insert_head(list); on N!=0, N.word0=0x62fc974c',
 limits=['s1 is inherited high constant 0x62fc9000, not A60 s1=G; normal callee register preservation required',
 'Null branch changes s1 and is not certified to resume normally',
 'A60 stride4/head0 is pending A61; not independently accepted here',
 's2 identity and incidental callback-write base not proven, no D slot or callback body expansion',
 'No target/model/old-script execution or new decompilation/REA state changes'])
(OUT/'evidence.json').write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n',encoding='utf8')
print(f'PASS {len(checks)} metadata/original-field checks; actual header/node/D bridge')
