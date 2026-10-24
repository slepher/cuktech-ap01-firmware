"""A64 old base-definition inputs; new fields require explicit registered fences."""
import json
import re
from pathlib import Path
from capstone import Cs,CS_ARCH_RISCV,CS_MODE_RISCV32,CS_MODE_RISCVC

MAIN=Path('D:/Documents/PlatformIO/Projects/cuktech-ap01-firmware')
OUT=Path(__file__).resolve().parent
checks=[]
def load(p):return json.loads(p.read_text(encoding='utf8'))
def check(label,got,want):
    assert got==want,(label,got,want)
    checks.append(dict(label=label,value=got))
a25path=MAIN/'reverse/analysis/pixel-memory-contract-a25-0041-20261023/evidence.json'
a25=load(a25path)
old_init=[r for r in a25['instructions'] if 0xa008e3ac<=int(r['va'],16)<0xa008e4b8]
defs=[r for r in old_init if re.match(r'(?:c\.)?(?:mv|li|lui|lw|addi|add|sub|andi|or|xor|and|srli|slli) s2(?:,| )',r['asm'])]
check('old A25 s2 ordinary definitions',[(r['va'],r['asm']) for r in defs],
      [('0xa008e3c4','lui s2, 0x62fc9')])
a21path=MAIN/'reverse/analysis/png-info-lifecycle-a21-0041-20261023/instruction-evidence.json'
a21=load(a21path)
selected=[r for w in a21['windows'] if 0xa008e3ac<=int(w['start'],16)<0xa008e876 for r in w['rows']]
defs21=[r for r in selected if re.match(r'(?:c\.)?(?:mv|li|lui|lw|addi|add|sub|andi|or|xor|and|srli|slli) s2(?:,| )',r['instruction'])]
check('old A21 selected s2 definitions',[(r['address'],r['instruction']) for r in defs21],
      [('0xa008e3c4','lui s2, 0x62fc9')])
a62path=MAIN/'reverse/analysis/reader-driver-register-gap-a62-0041-20261024/evidence.json'
a62=load(a62path)
rows={r['address']:r for r in a62['new_anchors']}
check('old A62 actual D address bridge',a62['new_contract'],
      'list=0x62fc9740; N=insert_head(list); on N!=0, N.word0=0x62fc974c')
check('old A62 base-forming instruction',rows['0xa008e77a']['instruction'],'addi a5, s2, 0x180')
check('old A62 incidental callback write',rows['0xa008e788']['instruction'],'c.sw a4, 0x5c(a5)')
check('old A62 leaves s2 unresolved',any('s2 identity' in v for v in a62['limits']),True)

ROM=MAIN/'roms/0041/ap01-1.0.2_0041.bin'
check('original length',ROM.stat().st_size,6769704)
d=Cs(CS_ARCH_RISCV,CS_MODE_RISCV32|CS_MODE_RISCVC)
new=[]
def raw(a,n):
    assert any(lo<=a and a+n<=hi for lo,hi in [(0xa008e4b8,0xa008e4bc),
      (0xa008e52a,0xa008e536),(0xa008e536,0xa008e612),
      (0xa008e628,0xa008e6ea),(0xa008e770,0xa008e7de)])
    with ROM.open('rb') as f:f.seek(a-0x9ffff000);return f.read(n)
def inst(a,text):
    n=4 if int.from_bytes(raw(a,2),'little')&3==3 else 2
    b=raw(a,n);r=list(d.disasm(b,a));check(hex(a),[v.mnemonic+' '+v.op_str for v in r],[text])
    new.append(dict(address=hex(a),raw=b.hex(),decode=text))
inst(0xa008e596,'c.bnez a0, 0x40')
inst(0xa008e5da,'addi s2, s2, 0x57c')
w=int.from_bytes(raw(0xa008e5da,4),'little')
check('independent s2 ADDI fields',(w&127,(w>>12)&7,(w>>7)&31,(w>>15)&31,w>>20),
      (0x13,0,18,18,0x57c))

normal_windows=[]
for lo,hi in [(0xa008e4b8,0xa008e4bc),(0xa008e52a,0xa008e536),
              (0xa008e536,0xa008e598),(0xa008e5d6,0xa008e612),(0xa008e628,0xa008e6ea)]:
    rs=list(d.disasm(raw(lo,hi-lo),lo))
    check('aligned normal continuity decode '+hex(lo),sum(r.size for r in rs),hi-lo)
    writes=[r for r in rs if r.op_str.startswith('s2,') and
            r.mnemonic not in {'sb','sh','sw','sd','c.sw','c.sd','c.swsp','c.sdsp'} and
            not r.mnemonic.startswith(('b','c.b'))]
    expected=[('0xa008e5da','addi s2, s2, 0x57c')] if lo==0xa008e5d6 else []
    check('normal s2 definitions '+hex(lo),[(hex(r.address),r.mnemonic+' '+r.op_str) for r in writes],expected)
    normal_windows.append(dict(start=hex(lo),end_exclusive=hex(hi),
       s2_definitions=[dict(address=hex(r.address),raw=r.bytes.hex(),decode=r.mnemonic+' '+r.op_str) for r in writes],
       control=[dict(address=hex(r.address),raw=r.bytes.hex(),decode=r.mnemonic+' '+r.op_str)
                for r in rs if r.mnemonic.startswith(('b','c.b','j','c.j'))]))
# Ordinary definitions in the old post-definition fragments were retained already.
old_after=[r for r in selected if 0xa008e612<=int(r['address'],16)<0xa008e768]
check('old A21 post-definition ordinary s2 writes',
      [r['instruction'] for r in old_after if re.match(r'(?:c\.)?(?:mv|li|lui|lw|addi|add|sub|andi|or|xor|and|srli|slli) s2(?:,| )',r['instruction'])],[])
a60=load(MAIN/'reverse/analysis/reader-driver-global-init-a60-0041-20261024/evidence.json')
check('old A60 normal s2 definitions',
      [r['instruction'] for r in a60['new_original_anchors'] if re.match(r'(?:c\.)?(?:mv|li|lui|lw|addi|add|sub|andi|or|xor|and|srli|slli) s2(?:,| )',r['instruction'])],[])

for pc,text in {
 0xa008e770:'addi a5, zero, 0x2f',0xa008e774:'c.lui a4, 1',
 0xa008e776:'sb a5, 0x1d0(s2)',0xa008e77a:'addi a5, s2, 0x180',
 0xa008e77e:'c.sw a4, 0x54(a5)',0xa008e780:'lui a4, 0xa00ef',
 0xa008e784:'addi a4, a4, 0x468',0xa008e788:'c.sw a4, 0x5c(a5)',
 0xa008e78a:'lui a4, 0xa00ef',0xa008e78e:'addi a4, a4, 0x502',
 0xa008e792:'c.sw a4, 0x60(a5)',0xa008e794:'lui a4, 0xa00ef',
 0xa008e798:'addi a4, a4, 0x55e',0xa008e79c:'c.sw a4, 0x64(a5)',
 0xa008e7a8:'lui a4, 0xa00ef',0xa008e7ac:'addi a4, a4, 0x632',
 0xa008e7b0:'c.sw a4, 0x6c(a5)',
}.items():inst(pc,text)
G=0x62fc9000+0x57c;D=0x62fc974c;B=G+0x180
check('s2 equals G on preserved normal path',G,0x62fc957c)
check('registered D relation',G+0x1d0,D)
check('auxiliary base is before D',B,D-0x50)
w=int.from_bytes(raw(0xa008e776,4),'little');im=((w>>25)<<5)|((w>>7)&31)
check('independent byte store fields',(w&127,(w>>12)&7,(w>>15)&31,(w>>20)&31,im),
      (0x23,0,18,15,0x1d0))
h=int.from_bytes(raw(0xa008e774,2),'little');q=(((h>>12)&1)<<5)|((h>>2)&31)
check('independent config C.LUI',(h&3,h>>13,(h>>7)&31,q),(1,3,14,1))
check('config word value',q<<12,4096)
bindings=[]
for pc,boff,doff,target in [(0xa008e77e,0x54,4,4096),
 (0xa008e788,0x5c,12,0xa00ef468),(0xa008e792,0x60,16,0xa00ef502),
 (0xa008e79c,0x64,20,0xa00ef55e),(0xa008e7b0,0x6c,28,0xa00ef632)]:
    h=int.from_bytes(raw(pc,2),'little')
    off=(((h>>10)&7)<<3)|(((h>>6)&1)<<2)|(((h>>5)&1)<<6)
    check('independent C.SW '+hex(pc),(h&3,h>>13,((h>>7)&7)+8,((h>>2)&7)+8,off),(0,6,15,14,boff))
    check('effective D field '+hex(pc),B+boff,D+doff)
    bindings.append(dict(store=hex(pc),base_offset=hex(boff),D_offset=hex(doff),target=hex(target)))
for pc,imm in [(0xa008e784,0x468),(0xa008e78e,0x502),(0xa008e798,0x55e),(0xa008e7ac,0x632)]:
    w=int.from_bytes(raw(pc,4),'little')
    check('independent target ADDI '+hex(pc),(w&127,(w>>12)&7,(w>>7)&31,(w>>15)&31,w>>20),
          (0x13,0,14,14,imm))
for pc in [0xa008e780,0xa008e78a,0xa008e794,0xa008e7a8]:
    w=int.from_bytes(raw(pc,4),'little')
    check('independent target LUI '+hex(pc),(w&127,(w>>7)&31,w&0xfffff000),
          (0x37,14,0xa00ef000))
for pc,rd,rs,imm in [(0xa008e770,15,0,0x2f),(0xa008e77a,15,18,0x180)]:
    w=int.from_bytes(raw(pc,4),'little')
    check('independent byte/base ADDI '+hex(pc),(w&127,(w>>12)&7,(w>>7)&31,(w>>15)&31,w>>20),
          (0x13,0,rd,rs,imm))
h=int.from_bytes(raw(0xa008e596,2),'little')
q=(((h>>12)&1)<<8)|(((h>>10)&3)<<3)|(((h>>5)&3)<<6)|(((h>>3)&3)<<1)|(((h>>2)&1)<<5)
q=q-512 if q&256 else q
check('independent normal s2-definition gate',(h&3,h>>13,((h>>7)&7)+8,0xa008e596+q),
      (1,7,10,0xa008e5d6))
slot_rows=list(d.disasm(raw(0xa008e77a,0x38),0xa008e77a))
check('auxiliary a5 base unchanged between stores',
      [(hex(r.address),r.mnemonic+' '+r.op_str) for r in slot_rows if r.op_str.startswith('a5,') and
       r.mnemonic not in {'sb','sh','sw','sd','c.sw','c.sd','c.swsp','c.sdsp'} and
       not r.mnemonic.startswith(('b','c.b'))],
      [('0xa008e77a','addi a5, s2, 0x180')])

exploration=[(0xa008e536,0xa008e566),(0xa008e564,0xa008e594),(0xa008e592,0xa008e5c2),
 (0xa008e5d6,0xa008e5f6),(0xa008e4b8,0xa008e4bc),(0xa008e52a,0xa008e536),
 (0xa008e5f6,0xa008e612),(0xa008e628,0xa008e658),(0xa008e658,0xa008e688),
 (0xa008e688,0xa008e6b8),(0xa008e6b8,0xa008e6e8),(0xa008e6e8,0xa008e6ea),
 (0xa008e5f4,0xa008e612),(0xa008e770,0xa008e794),(0xa008e794,0xa008e7b2)]

result=dict(status='PASS-registered-D-slot-binding',claim='J08/6',task='A64',baseline='bd457a6',checks=checks,
 inherited_inputs=[str(p.relative_to(MAIN)) for p in [a25path,a21path,a62path]],
 old_gap='Old inputs only s2 high constant; newly registered normal ADDI/continuity resolves this',
 new_original_anchors=new,normal_continuity=normal_windows,bindings=bindings,
 registered_D=hex(D),auxiliary_B=hex(B),first_byte='0x2f',config=4096,new_decompilation=0,
 exploratory_windows=[[hex(a),hex(b)] for a,b in exploration],
 exploratory_requested_bytes=sum(b-a for a,b in exploration),
 exploratory_unique_bytes=len({pc for a,b in exploration for pc in range(a,b)}),
 limits=['A63 now independently accepted A62; no register body recheck',
         'Normal conditional branches and callee-saved-register ABI required; diagnostics not certified to resume normally',
         'No slot target bodies or default-photo mode1 claim',
         'No old scripts/target/model execution; no shared REA mutation'])
(OUT/'evidence.json').write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n',encoding='utf8')
print(f'PASS {len(checks)} old-input/registered base/slot checks')
