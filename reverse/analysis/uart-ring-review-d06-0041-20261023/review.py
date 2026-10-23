"""D06 original-ROM static review. No target execution or shared analysis state."""
from pathlib import Path
import json
from capstone import Cs, CS_ARCH_RISCV, CS_MODE_RISCV32, CS_MODE_RISCVC

OUT = Path(__file__).resolve().parent
ROOT = Path('D:/Documents/PlatformIO/Projects/cuktech-ap01-firmware')
ROM = ROOT / 'roms/0041/ap01-1.0.2_0041.bin'
MODEL = ROOT / 'evidence/rea-0041-20261017/ghidra/Ghidra/Processors/RISCV/data/languages/ap01thead2.sinc'
data = ROM.read_bytes()
model = MODEL.read_text().splitlines()
base = 0x9ffff000
reg = 'zero ra sp gp tp t0 t1 t2 s0 s1 a0 a1 a2 a3 a4 a5 a6 a7 s2 s3 s4 s5 s6 s7 s8 s9 s10 s11 t3 t4 t5 t6'.split()
cs = Cs(CS_ARCH_RISCV, CS_MODE_RISCV32 | CS_MODE_RISCVC)
def offset(a):
    # Startup a0029cf6..9d0e/a0029e2c..34 copies this ROM span into RAM.
    return (0xa0000c14+a-0x62fc1100 if 0x62fc1100 <= a < 0x62fc2cc0 else a)-base
def get(a, n=4): return data[offset(a):offset(a)+n]
def u(a, n=4): return int.from_bytes(get(a,n), 'little')
def sx(n,b): return n-(1<<b) if n & (1<<(b-1)) else n
clauses = {}
def vendor(w):
    rd=(w>>7)&31; rs=(w>>15)&31; rt=(w>>20)&31
    f=(w>>12)&7; top=w>>27; shift=(w>>25)&3
    if f in (2,3):
        name='ext' if f==2 else 'extu'; msb=(w>>26)&31
        args=f'{reg[rd]}, {reg[rs]}, {msb}, {rt}'
        prefix=f':th.{name} rd,rs1,{msb},{rt} '
    else:
        name={(1,0):'addsl',(4,0):'lrb',(4,8):'lrw',(4,16):'lrbu',
              (4,19):'lbuia',(4,11):'lwia',(5,0):'srb',(5,8):'srw',(5,11):'swia'}[(f,top)]
        args=f'{reg[rd]}, {reg[rs]}, {sx(rt,5) if name in ("lbuia","lwia","swia") else reg[rt]}, {shift}'
        prefix=f':th.{name} '
    i=next(i for i,s in enumerate(model) if s.startswith(prefix))
    j=next(j for j in range(i+1,len(model)) if model[j]=='}')
    clauses[prefix]={'line':i+1,'text':'\n'.join(model[i:j+1])}
    return 'th.'+name+' '+args

regions = [
 ('open-first-attach',0xa002ba6c,0xa002bb28), ('attach',0xa001a1d8,0xa001a214),
 ('install-irq',0xa0026498,0xa00264ec), ('dispatch-irq',0xa0001012,0xa0001048),
 ('uart-irq-first-tx',0xa0019ae0,0xa0019b44), ('uart-irq-alt-tx',0xa0019c4e,0xa0019c6c),
 ('uart-irq-return',0xa0019d5a,0xa0019d6a), ('drain',0xa002d36a,0xa002d46e),
 ('ready',0xa001972c,0xa001973a), ('scalar-send',0xa0019876,0xa00198bc),
 ('tx-interrupt',0xa0019810,0xa0019876), ('available',0xa001a70a,0xa001a946),
 ('start-dma',0xa001a240,0xa001a49c), ('dma-complete',0xa0019d9a,0xa0019f42),
 ('install-dma',0xa00264ec,0xa00265d6), ('dma-irq',0xa0024b12,0xa0024b68),
 ('dma-state',0xa0024b7e,0xa0024c5e), ('dma-configure',0xa0025cec,0xa0025d9e),
 ('dma-mask',0xa01a13f8,0xa01a1436), ('submit-wrapper',0xa01a47dc,0xa01a4820),
 ('release',0xa002d5d8,0xa002d62c), ('notify',0xa002be92,0xa002beba),
 ('notify-poll',0xa002bcec,0xa002bd7c), ('notify-waiters',0xa002b8de,0xa002b90e),
 ('enqueue',0xa002c140,0xa002c206),
 ('ram-copy-setup',0xa0029cf6,0xa0029d12), ('ram-copy-loop',0xa0029e2c,0xa0029e36),
 ('dma-irq-trampoline',0x62fc133c,0x62fc1354),
]
windows=[]; bypc={}
for name,start,end in regions:
    pc=start; items=[]
    while pc < end:
        raw=u(pc); size=4 if raw&3==3 else 2
        assert pc+size<=end, (name,hex(pc))
        if size==4 and raw&127==11: decoded=vendor(raw)
        else:
            ins=list(cs.disasm(get(pc,size),pc))
            assert len(ins)==1 and ins[0].size==size,(hex(pc),get(pc,size).hex())
            decoded=ins[0].mnemonic+' '+ins[0].op_str
        row={'va':f'{pc:08x}','offset':f'{offset(pc):x}','raw':get(pc,size).hex(),'instruction':decoded}
        items.append(row); bypc[pc]=row
        pc+=size
    windows.append({'name':name,'start':hex(start),'end_exclusive':hex(end),'instructions':items})

# Independently extract every direct control transfer, not copied target assertions.
edges=[]
for pc,row in bypc.items():
    w=u(pc); op=w&127
    if len(row['raw'])!=8: continue
    if op==0x6f:
        imm=((w>>31)<<20)|(((w>>12)&255)<<12)|(((w>>20)&1)<<11)|(((w>>21)&1023)<<1)
        edges.append({'va':hex(pc),'kind':'jal','target':hex((pc+sx(imm,21))&0xffffffff),'rd':(w>>7)&31})
    elif op==0x63:
        imm=((w>>31)<<12)|(((w>>7)&1)<<11)|(((w>>25)&63)<<5)|(((w>>8)&15)<<1)
        edges.append({'va':hex(pc),'kind':'branch','target':hex((pc+sx(imm,13))&0xffffffff),'funct3':(w>>12)&7})
pairs=[]
for pc,row in bypc.items():
    w=u(pc)
    if len(row['raw'])==8 and w&127==0x17 and pc+4 in bypc:
        next_word=u(pc+4)
        if next_word&127==0x67 and (next_word>>15)&31==(w>>7)&31:
            pairs.append({'va':hex(pc),'target':hex((pc+(w&0xfffff000)+sx(next_word>>20,12))&0xffffffff)})
stores=[]
for pc,row in bypc.items():
    w=u(pc)
    if len(row['raw'])==8 and w&127==0x23:
        stores.append({'va':hex(pc),'raw':row['raw'],'width':1<<((w>>12)&7),
                       'base':reg[(w>>15)&31],'value':reg[(w>>20)&31],
                       'offset':sx(((w>>25)<<5)|((w>>7)&31),12)})
mapinit=lambda a:0xa00027d4+a-0x62fc2cc0
dev=0x62fc36d0; private=0x62fc36b4
initial={'map_contract':'ROM a00027d4 -> RAM 62fc2cc0 (D04)',
 'private':{'ram':hex(private),'rom':hex(mapinit(private)),'bytes':get(mapinit(private),28).hex()},
 'dev':{hex(o):hex(u(mapinit(dev+o),2 if o in (0x50,0x52,0x54) else 4)) for o in (0x50,0x52,0x54,0x58,0xa0,0xa4)},
 'lower':{hex(o):hex(u(0xa01bcb18+o)) for o in range(0,0x4c,4)}}
assert initial['dev']['0xa0']=='0xa01bcb18' and initial['dev']['0xa4']==hex(private)
assert get(mapinit(private),2)==bytes([1,0x3d]) and u(mapinit(private+14),1)==0
assert initial['lower']['0x48']=='0x0'
assert bypc[0xa0019734]['instruction']=='c.li a0, 1'
# JAL edges recomputed from original instruction fields above.
required_edges={0xa001a1f6:0xa0026498,0xa0019b34:0xa002d36a,
 0xa001a400:0xa00264ec,0xa0019e2c:0xa002d5d8,0xa002d3b4:0xa002be92,
 0xa002d61e:0xa002be92,0xa002bea4:0xa002bcec,0xa002beac:0xa002b8de,
 0xa002658e:0xa0026498,0xa002b906:0xa00273cc,0xa002c1e4:0xa002786c}
for pc,target in required_edges.items():
    assert any(e['va']==hex(pc) and e['kind']=='jal' and e['target']==hex(target) for e in edges)
required_stores={0xa002d3e6:(2,'s1','a5',0x52),0xa002d604:(2,'a0','a5',0x52),
 0xa002d608:(4,'a0','zero',0x88),0xa002d60c:(4,'a0','zero',0x84),
 0xa002d610:(4,'a0','zero',0x80),0xa0019e18:(4,'s3','a5',0x88),
 0xa0019e26:(4,'s3','a5',0x88)}
for pc,expected in required_stores.items():
    found=next(s for s in stores if s['va']==hex(pc))
    assert tuple(found[k] for k in ('width','base','value','offset'))==expected
def cj_target(pc):
    h=u(pc,2)
    imm=((h>>12&1)<<11)|((h>>11&1)<<4)|((h>>9&3)<<8)|((h>>8&1)<<10)|((h>>7&1)<<6)|((h>>6&1)<<7)|((h>>3&7)<<1)|((h>>2&1)<<5)
    assert h&0xe003==0xa001
    return (pc+sx(imm,12))&0xffffffff
assert cj_target(0xa0019eea)==0xa0019e24
assert cj_target(0xa0019e30)==0xa0019e8a
assert cj_target(0xa0029e34)==0xa0029d0e
assert any(e['va']=='0xa001a724' and e['target']=='0xa001a896' for e in edges)
for pc,target in ((0xa001a420,0xa01a13f8),(0xa001a454,0xa01a47dc),(0xa0019894,0x62fc22ae)):
    assert {'va':hex(pc),'target':hex(target)} in pairs
assert bypc[0x62fc1344]['instruction']=='c.lw a5, 0(a2)'
assert bypc[0x62fc1346]['instruction']=='c.lw a1, 4(a2)'
assert bypc[0x62fc1348]['instruction']=='c.jalr a5'
payload={'rom':str(ROM),'base':hex(base),'method':'Static original-byte independent linear decode; no target executed. No D05 evidence imported.',
         'model_source':str(MODEL),'vendor_clauses':clauses,'initial':initial,'regions':windows,'direct_edges':edges,'auipc_jalr_pairs':pairs,'raw_stores':stores,
         'validation':{'required_jal_edges':len(required_edges),'required_s_stores':len(required_stores),
                       'type_gt1_join':hex(cj_target(0xa0019eea)),'ram_trampoline_offset':hex(offset(0x62fc133c))}}
(OUT/'original-instructions.json').write_text(json.dumps(payload,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
print(f'{len(windows)} regions, {len(bypc)} instructions, {len(clauses)} vendor clauses, {len(edges)} direct edges, {len(pairs)} AUIPC/JALR pairs, {len(stores)} raw S stores; required edges, stores, joins and initial checks passed')
