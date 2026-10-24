"""A65: independent normal s2 continuity and real D stores, no target bodies."""
from pathlib import Path
import json
import re
import capstone
MAIN=Path('D:/Documents/PlatformIO/Projects/cuktech-ap01-firmware')
OUT=Path(__file__).resolve().parent
ROM=MAIN/'roms/0041/ap01-1.0.2_0041.bin';BASE=0x9ffff000
assert ROM.stat().st_size==6769704
md=capstone.Cs(capstone.CS_ARCH_RISCV,capstone.CS_MODE_RISCV32|capstone.CS_MODE_RISCVC)
checks=[];new_summary=[];anchors={}
normal=[(0xa008e4b8,0xa008e4bc),(0xa008e52a,0xa008e536),
        (0xa008e536,0xa008e598),(0xa008e5d6,0xa008e612),(0xa008e628,0xa008e6ea)]
def eq(label,got,want):
    assert got==want,(label,got,want)
    checks.append(dict(label=label,value=got))
def sx(v,n):return v-(1<<n) if v&(1<<(n-1)) else v
def b(v,a,n):return (v>>a)&((1<<n)-1)
def read(a,z):
    assert any(lo<=a<z<=hi for lo,hi in normal+[(0xa008e770,0xa008e7b2)])
    with ROM.open('rb') as f:f.seek(a-BASE);return f.read(z-a)
def defines(text,reg):
    op,args=text.split(' ',1)
    return args.startswith(reg+',') and op not in {
        'sb','sh','sw','sd','c.sw','c.sd','c.swsp','c.sdsp'} and not op.startswith(('b','c.b'))
for lo,hi in normal:
    raw=read(lo,hi);ins=list(md.disasm(raw,lo))
    eq(hex(lo)+' actual instruction coverage',sum(i.size for i in ins),hi-lo)
    defs=[i for i in ins if defines(i.mnemonic+' '+i.op_str,'s2')]
    expected=[('0xa008e5da','addi s2, s2, 0x57c')] if lo==0xa008e5d6 else []
    eq(hex(lo)+' s2 writes',[(hex(i.address),i.mnemonic+' '+i.op_str) for i in defs],expected)
    if lo==0xa008e5d6:
        eq('true boundary e5f4 is four bytes',next(i.size for i in ins if i.address==0xa008e5f4),4)
        eq('e5f6 is not an instruction start',any(i.address==0xa008e5f6 for i in ins),False)
    new_summary.append(dict(start=hex(lo),end_exclusive=hex(hi),instruction_count=len(ins),
        s2_definitions=[dict(pc=hex(i.address),raw=i.bytes.hex(),asm=i.mnemonic+' '+i.op_str) for i in defs],
        control=[dict(pc=hex(i.address),raw=i.bytes.hex(),asm=i.mnemonic+' '+i.op_str)
                 for i in ins if i.mnemonic.startswith(('b','c.b','j','c.j'))]))
    for i in ins:
        if i.address in [0xa008e596,0xa008e5da]:anchors[i.address]=bytes(i.bytes)
v=int.from_bytes(anchors[0xa008e596],'little')
i=(b(v,12,1)<<8)|(b(v,10,2)<<3)|(b(v,5,2)<<6)|(b(v,3,2)<<1)|(b(v,2,1)<<5)
eq('normal definition gate',[v&3,v>>13,8+b(v,7,3),0xa008e596+sx(i,9)],[1,7,10,0xa008e5d6])
v=int.from_bytes(anchors[0xa008e5da],'little')
eq('actual s2 update',[v&127,b(v,7,5),b(v,12,3),b(v,15,5),sx(v>>20,12)],
   [19,18,0,18,0x57c])

# Published prior fragments only; do not use A60's unretained discovery as bytes.
a25_path=MAIN/'reverse/analysis/pixel-memory-contract-a25-0041-20261023/evidence.json'
a25=json.loads(a25_path.read_text(encoding='utf8'))
old_pre=[r for r in a25['instructions'] if 0xa008e3c4<=int(r['va'],16)<0xa008e4b8]
eq('old actual s2 high definition',[(r['va'],r['asm']) for r in old_pre if defines(r['asm'],'s2')],
   [('0xa008e3c4','lui s2, 0x62fc9')])
a21_path=MAIN/'reverse/analysis/png-info-lifecycle-a21-0041-20261023/instruction-evidence.json'
a21=json.loads(a21_path.read_text(encoding='utf8'))
old={int(r['address'],16):r for win in a21['windows'] for r in win['rows']}
old_pieces=[]
for lo,hi in [(0xa008e4bc,0xa008e4c4),(0xa008e612,0xa008e628),(0xa008e6ea,0xa008e768)]:
    a=lo;selected=[]
    while a<hi:
        r=old[a];selected.append(r);a+=len(bytes.fromhex(r['bytes']))
    eq(hex(lo)+' published old coverage',a,hi)
    eq(hex(lo)+' old ordinary s2 writes',[r['instruction'] for r in selected if defines(r['instruction'],'s2')],[])
    old_pieces.append(dict(source=str(a21_path),start=hex(lo),end_exclusive=hex(hi),rows=len(selected)))
a60_path=MAIN/'reverse/analysis/reader-driver-global-init-a60-0041-20261024/evidence.json'
a60=json.loads(a60_path.read_text(encoding='utf8'));old60={int(r['address'],16):r for r in a60['new_original_anchors']}
lo,hi=0xa008e506,0xa008e52a;a=lo;kept=[]
while a<hi:
    r=old60[a];kept.append(r);a+=len(bytes.fromhex(r['raw']))
eq('A60 published straight-path coverage only',a,hi)
eq('A60 actual published straight-path no s2 definition',[r['instruction'] for r in kept if defines(r['instruction'],'s2')],[])
gate=int.from_bytes(bytes.fromhex(old60[0xa008e4c4]['raw']),'little')
i=(b(gate,12,1)<<8)|(b(gate,10,2)<<3)|(b(gate,5,2)<<6)|(b(gate,3,2)<<1)|(b(gate,2,1)<<5)
eq('old normal entry gate actual target',0xa008e4c4+sx(i,9),0xa008e506)

a62_path=MAIN/'reverse/analysis/reader-driver-register-gap-a62-0041-20261024/evidence.json'
a62=json.loads(a62_path.read_text(encoding='utf8'));r62={r['address']:r for r in a62['new_anchors']}
eq('registered D identity inherited',a62['new_contract'],
   'list=0x62fc9740; N=insert_head(list); on N!=0, N.word0=0x62fc974c')
eq('pre-slot normal external call exists in old fields',r62['0xa008e76c']['instruction'],'jal -0xd9de')

slot=read(0xa008e770,0xa008e7b2);ins=list(md.disasm(slot,0xa008e770))
eq('slot path actual instruction boundaries',sum(i.size for i in ins),len(slot))
eq('auxiliary a5 has single definition',[(hex(i.address),i.mnemonic+' '+i.op_str) for i in ins
    if i.address>=0xa008e77a and defines(i.mnemonic+' '+i.op_str,'a5')],[('0xa008e77a','addi a5, s2, 0x180')])
eq('slot path does not write s2',[i.mnemonic+' '+i.op_str for i in ins if defines(i.mnemonic+' '+i.op_str,'s2')],[])
by={i.address:bytes(i.bytes) for i in ins}
def wi(pc):anchors[pc]=by[pc];return int.from_bytes(by[pc],'little')
v=wi(0xa008e770)
eq('character value ADDI',[v&127,b(v,7,5),b(v,12,3),b(v,15,5),sx(v>>20,12)],[19,15,0,0,0x2f])
v=wi(0xa008e774);q=sx((b(v,12,1)<<5)|b(v,2,5),6)
eq('config is C.LUI value',[v&3,v>>13,b(v,7,5),q,q<<12],[1,3,14,1,4096])
v=wi(0xa008e776)
eq('letter is byte store',[v&127,b(v,12,3),b(v,15,5),b(v,20,5),sx((b(v,25,7)<<5)|b(v,7,5),12)],
   [35,0,18,15,0x1d0])
v=wi(0xa008e77a)
eq('auxiliary B from actual G register',[v&127,b(v,7,5),b(v,12,3),b(v,15,5),sx(v>>20,12)],[19,15,0,18,0x180])
G=0x62fc9000+0x57c;D=0x62fc974c;B=G+0x180
eq('G arithmetic',G,0x62fc957c);eq('D letter address',G+0x1d0,D);eq('B is D-0x50',B,D-0x50)
bindings=[]
for store,boff,doff,target,upc,ipc,imm in [
    (0xa008e77e,0x54,4,4096,None,None,None),
    (0xa008e788,0x5c,12,0xa00ef468,0xa008e780,0xa008e784,0x468),
    (0xa008e792,0x60,16,0xa00ef502,0xa008e78a,0xa008e78e,0x502),
    (0xa008e79c,0x64,20,0xa00ef55e,0xa008e794,0xa008e798,0x55e),
    (0xa008e7b0,0x6c,28,0xa00ef632,0xa008e7a8,0xa008e7ac,0x632)]:
    if upc is not None:
        u=wi(upc);v=wi(ipc)
        eq(hex(upc)+' target LUI',[u&127,b(u,7,5),u&0xfffff000],[55,14,0xa00ef000])
        eq(hex(ipc)+' target ADDI',[v&127,b(v,7,5),b(v,12,3),b(v,15,5),sx(v>>20,12)],
           [19,14,0,14,imm])
        eq(hex(ipc)+' actual target',0xa00ef000+sx(v>>20,12),target)
    v=wi(store);off=(b(v,10,3)<<3)|(b(v,6,1)<<2)|(b(v,5,1)<<6)
    eq(hex(store)+' C.SW register/width/offset',[v&3,v>>13,8+b(v,2,3),8+b(v,7,3),off],[0,6,14,15,boff])
    eq(hex(store)+' effective D field',B+off,D+doff)
    bindings.append(dict(pc=hex(store),effective=hex(B+off),D_offset=hex(doff),value=target))
out=dict(status='PASS',task='A65',claim='J08/6',baseline='bd457a6',reviewer='/root/a56',author='A64 /root/g23',
    identity=dict(path=str(ROM),length=6769704,mapping='VA-0x9ffff000',
    sha256_inherited='972db4c136c7ed9e24a83c07c1a7fd62040ca018b08ca285216d26b1fee3c6b9',hash_recomputed=False),
    checks=checks,new_continuity=new_summary,new_continuity_bytes=sum(z-a for a,z in normal),
    tools=dict(decoder='Capstone '+capstone.__version__+' RV32/RVC',fields='independent I/S/B and RVC bit fields'),
    slot_control_read=dict(start='0xa008e770',end_exclusive='0xa008e7b2',bytes=len(slot)),
    sparse_fields=[dict(pc=hex(p),offset=hex(p-BASE),raw=r.hex()) for p,r in sorted(anchors.items())],
    inherited=dict(A25=str(a25_path),A21_published_pieces=old_pieces,
       A60_published_path=str(a60_path),A62=str(a62_path),
       restrictions='No old clear/registration/selector/callback-body scripts rerun; no A60 unretained exploration used'),
    bindings=bindings,G=hex(G),D=hex(D),B=hex(B),
    conclusion='Limited acceptance: selected normal path s2->G, B=D-0x50, letter/config/four callback stores bind the registered D',
    limits=['Normal gates and ordinary callee-saved s2 convention required; not all exceptional/diagnostic paths',
            'No callback/helper bodies, full initializer or node/selector revalidation',
            'No runtime source match, actual IO, letter uniqueness, field immutability or D lifecycle certification',
            'No target/instruction/model/old-script/input execution or shared REA change'])
(OUT/'review-evidence.json').write_text(json.dumps(out,ensure_ascii=False,indent=2)+'\n',encoding='utf8')
print(json.dumps(dict(status='PASS',checks=len(checks),new_continuity_bytes=out['new_continuity_bytes'],
                      slot_bytes=len(slot),sparse_fields=len(anchors))))
