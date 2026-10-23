"""D05 isolated static evidence. Read original ROM; never execute firmware."""
from pathlib import Path
import json, sys
from capstone import Cs, CS_ARCH_RISCV, CS_MODE_RISCV32, CS_MODE_RISCVC
HERE=Path(__file__).resolve().parent
ROOT=Path('D:/Documents/PlatformIO/Projects/cuktech-ap01-firmware')
BASE=0x9ffff000
raw=(ROOT/'roms/0041/ap01-1.0.2_0041.bin').read_bytes()
model_path=ROOT/'evidence/rea-0041-20261017/ghidra/Ghidra/Processors/RISCV/data/languages/ap01thead2.sinc'
model=model_path.read_text().splitlines()
cs=Cs(CS_ARCH_RISCV, CS_MODE_RISCV32|CS_MODE_RISCVC)
regs='zero ra sp gp tp t0 t1 t2 s0 s1 a0 a1 a2 a3 a4 a5 a6 a7 s2 s3 s4 s5 s6 s7 s8 s9 s10 s11 t3 t4 t5 t6'.split()
sx=lambda x,n:x-(1<<n) if x&(1<<(n-1)) else x
word=lambda a:int.from_bytes(raw[a-BASE:a-BASE+4],'little')
models={}
def custom(w):
    rd=(w>>7)&31;r1=(w>>15)&31;r2=(w>>20)&31;f=(w>>12)&7;hi=w>>27;sh=(w>>25)&3
    if f in (2,3):
        name='ext' if f==2 else 'extu'; args=f'{regs[rd]}, {regs[r1]}, {(w>>26)&31}, {r2}'
        prefix=f':th.{name} rd,rs1,{(w>>26)&31},{r2} '
    else:
        if f==4: name={0:'lrb',8:'lrw',16:'lrbu',19:'lbuia'}[hi]
        elif f==5:name={0:'srb',8:'srw'}[hi]
        elif f==1 and hi==0:name='addsl'
        else: raise ValueError(hex(w))
        args=f'{regs[rd]}, {regs[r1]}, {sx(r2,5) if name=="lbuia" else regs[r2]}, {sh}'
        prefix=f':th.{name} '
    start=next(i for i,l in enumerate(model) if l.startswith(prefix))
    stop=next(i for i in range(start+1,len(model)) if model[i]=='}')
    models[prefix]={'line':start+1,'body':'\n'.join(model[start:stop+1])}
    return 'th.'+name+' '+args

REGIONS=[
 ('tx_available',0xa001a70a,0xa001a946),
 ('tx_start',0xa001a240,0xa001a49c),
 ('tx_callback',0xa0019d9a,0xa0019f42),
 ('tx_release',0xa002d5d8,0xa002d62c),
 ('tx_notify',0xa002be92,0xa002beba),
 ('notify_poll',0xa002bcec,0xa002bd7c),
 ('wake_waiters',0xa002b8de,0xa002b90e),
 ('dma_install',0xa00264ec,0xa00265d6),
 ('dma_configure',0xa0025cec,0xa0025d9e),
 ('dma_irq',0xa0024b12,0xa0024b68),
 ('dma_enable_stop_active_clear',0xa0024b7e,0xa0024c5e),
 ('dma_irq_mask',0xa01a13f8,0xa01a1436),
 ('writer_enqueue',0xa002c140,0xa002c206),
 ('uart_attach',0xa001a1d8,0xa001a214),
 ('uart_irq_tx_slice',0xa0019ae0,0xa0019b44),
 ('uart_irq_epilogue',0xa0019d5a,0xa0019d6a),
 ('uart_irq_other_model_tx_slice',0xa0019c4e,0xa0019c6c),
 ('scalar_drain',0xa002d36a,0xa002d46e),
 ('irq_install',0xa0026498,0xa00264ec),
 ('irq_dispatch_slice',0xa0001012,0xa0001048),
 ('open_attach_slice',0xa002ba6c,0xa002bb28),
 ('txint',0xa0019810,0xa0019876),
 ('dma_submit_wrapper',0xa01a47dc,0xa01a4820),
]
if len(sys.argv)>1:
    for arg in sys.argv[1:]:
        a,b=(int(x,16) for x in arg.split(':'));pc=a
        while pc<b:
            w=word(pc);sz=4 if w&3==3 else 2;buf=raw[pc-BASE:pc-BASE+sz]
            ins=list(cs.disasm(buf,pc));s=custom(w) if sz==4 and w&127==11 else (ins[0].mnemonic+' '+ins[0].op_str if ins else 'UNKNOWN')
            print(f'{pc:08x} {buf.hex():8} {s}');pc+=sz
    sys.exit()
rows={};windows=[]
for name,a,b in REGIONS:
    pc=a;items=[]
    while pc<b:
        w=word(pc);sz=4 if w&3==3 else 2;buf=raw[pc-BASE:pc-BASE+sz];assert pc+sz<=b
        if sz==4 and w&127==11: s=custom(w)
        else:
            ins=list(cs.disasm(buf,pc));assert len(ins)==1 and ins[0].size==sz,(hex(pc),buf.hex())
            s=ins[0].mnemonic+' '+ins[0].op_str
        row={'address':hex(pc),'offset':hex(pc-BASE),'bytes':buf.hex(),'decode':s};rows[pc]=row;items.append(row);pc+=sz
    windows.append({'name':name,'start':hex(a),'end_exclusive':hex(b),'instructions':items})
out={'method':'Original ROM read; independently bounded RV32+C disassembly with local vendor model excerpts. Static only; no REA target/database opened.','rom':str(ROOT/'roms/0041/ap01-1.0.2_0041.bin'),'base':hex(BASE),'model':str(model_path),'model_excerpts':models,'windows':windows}
# Assertions are static instruction/encoding checks, not execution or a simulator.
expect={
0xa001a720:'lbu a5, 0xe(s3)',0xa001a724:'beqz a5, 0x172',
0xa001a1e8:'c.mv a2, a0',0xa001a1f2:'addi a1, a1, -0x520',
0xa002bae6:'c.lw a5, 8(a5)',0xa002bae8:'c.jalr a5',
0xa00264cc:'th.srw a1, a5, s2, 3',0xa00264d4:'c.sw a2, 4(a5)',
0xa0001026:'c.lw a2, 4(a5)',0xa0001044:'c.mv a0, s1',0xa0001046:'c.jalr s2',
0xa0019b22:'and s3, s3, a4',0xa0019b26:'andi a5, s3, 4',
0xa0019b30:'c.bnez a5, 8',0xa0019b3e:'ori a5, a5, 4',
0xa002d38e:'lhu a4, 0x50(s1)',0xa002d392:'lhu a5, 0x52(s1)',
0xa002d3ac:'c.jalr a5',0xa002d3d2:'c.lw a4, 0x30(a5)',
0xa002d3dc:'th.ext a3, a5, 15, 0',0xa002d3e6:'sh a5, 0x52(s1)',
0xa002d3ea:'th.lrbu a1, a1, a3, 0',0xa002d3ee:'c.jalr a4',
0xa002d404:'c.lw a3, 0x48(a5)',0xa002d444:'th.extu a0, a0, 15, 0',
0xa002d454:'th.extu s2, s2, 15, 0',0xa002d468:'sh zero, 0x52(s1)',
0xa001a864:'sw zero, 0x7c(s1)',0xa001a868:'sw zero, 0x84(s1)',
0xa001a872:'c.sw a5, 0x78(s1)',0xa001a886:'sw a5, 0x80(s1)',
0xa001a88e:'c.lw a5, 0x20(a5)',0xa001a894:'c.jalr a5',
0xa001a928:'th.ext a3, a4, 15, 0',0xa001a92c:'lh a4, 0x54(s1)',
0xa001a938:'c.sw a5, 0x7c(s1)',0xa001a942:'c.sw a5, 4(a3)',
0xa001a3fa:'c.mv a2, s3',0xa001a3fc:'addi a1, a1, -0x266',
0xa00264fc:'th.addsl a4, a4, a3, 2',0xa0026500:'th.srw a1, a5, a4, 3',
0xa0026514:'c.sw a2, 4(a5)',0xa0024b4a:'c.lw a0, 4(s1)',0xa0024b4c:'c.jalr a5',
0xa0019e04:'th.srb zero, s4, a5, 0',0xa0019e18:'sw a5, 0x88(s3)',
0xa0019e26:'sw a5, 0x88(s3)',0xa0019e6c:'th.srb s8, s4, a5, 0',
0xa002d5ea:'bne a4, a5, 0x1e',0xa002d5fc:'remu a5, a5, a4',
0xa002d604:'sh a5, 0x52(a0)',0xa002d608:'sw zero, 0x88(a0)',
0xa002d60c:'sw zero, 0x84(a0)',0xa002d610:'sw zero, 0x80(a0)',
0xa002bea8:'addi a0, s1, 0x18',0xa002bd54:'th.addsl a0, a0, s1, 2',
0xa002b8ea:'lhu s1, 0(a0)',0xa002b90a:'c.addi s1, 1',
0xa002c1e0:'c.jalr a5',0xa002c1e4:'jal -0x4978',0xa002c1f6:'csrw mstatus, s8',
}
for pc,s in expect.items():assert rows[pc]['decode']==s,(hex(pc),rows[pc],s)
edges=[]
for pc,target in {0xa001a1f6:0xa0026498,0xa0019b34:0xa002d36a,
 0xa0019c60:0xa002d36a,0xa002d3b4:0xa002be92,0xa001a400:0xa00264ec,
 0xa0019e2c:0xa002d5d8,0xa001a814:0xa002d5d8,0xa002d61e:0xa002be92,
 0xa002bea4:0xa002bcec,0xa002beac:0xa002b8de,0xa002b906:0xa00273cc,
 0xa001a758:0xa0024bec,0xa001a792:0xa0024bb6,0xa001a7a2:0xa0024c20,
 0xa001a3ce:0xa0025cec,0xa001a410:0xa0024c20,0xa001a468:0xa0024b7e,
 0xa01a4814:0xa01b554e}.items():
    w=word(pc);imm=((w>>31)<<20)|(((w>>12)&255)<<12)|(((w>>20)&1)<<11)|(((w>>21)&1023)<<1)
    assert w&127==0x6f and (pc+sx(imm,21))&0xffffffff==target,(hex(pc),hex(target))
    edges.append({'pc':hex(pc),'target':hex(target),'bytes':raw[pc-BASE:pc-BASE+4].hex()})
init=lambda a:0xa00027d4+(a-0x62fc2cc0)
dev=0x62fc36d0;priv=0x62fc36b4
initial={'dev':hex(dev),'private':hex(priv),'private_hex':raw[init(priv)-BASE:init(priv)-BASE+28].hex(),
 'lower_words':{hex(a):hex(word(a)) for a in range(0xa01bcb18,0xa01bcb64,4)},
 'device_words':{hex(o):hex(word(init(dev+o))) for o in (0x58,0xa0,0xa4)}}
assert raw[init(priv)-BASE]==1 and raw[init(priv)+14-BASE]==0
assert word(init(dev+0xa0))==0xa01bcb18 and word(init(dev+0xa4))==priv
assert word(0xa01bcb44)==0xa001a70a and word(0xa01bcb38)==0xa001a240 and word(0xa01bcb60)==0
store_checks=[]
for pc,funct3,rs1,rs2,offset in [
 (0xa002d3e6,1,9,15,0x52),(0xa002d468,1,9,0,0x52),
 (0xa002d604,1,10,15,0x52),(0xa002d608,2,10,0,0x88),
 (0xa002d60c,2,10,0,0x84),(0xa002d610,2,10,0,0x80),
 (0xa0019e18,2,19,15,0x88),(0xa0019e26,2,19,15,0x88)]:
    w=word(pc);imm=sx(((w>>25)<<5)|((w>>7)&31),12)
    assert w&127==0x23 and (w>>12)&7==funct3 and (w>>15)&31==rs1 and (w>>20)&31==rs2 and imm==offset
    store_checks.append({'pc':hex(pc),'width':2 if funct3==1 else 4,'rs1':rs1,'rs2':rs2,'offset':offset})
pairs=[]
for pc,target in [(0xa001a420,0xa01a13f8),(0xa001a454,0xa01a47dc)]:
    a,b=word(pc),word(pc+4)
    assert a&127==0x17 and b&127==0x67
    got=(pc+(a&0xfffff000)+sx(b>>20,12))&0xffffffff
    assert got==target
    pairs.append({'pc':hex(pc),'target':hex(target),'bytes':raw[pc-BASE:pc-BASE+8].hex()})
out.update({'instruction_assertions':len(expect),'jal_edges':edges,'auipc_jalr_edges':pairs,'s_type_checks':store_checks,'initialization':initial})
(HERE/'instruction-evidence.json').write_text(json.dumps(out,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
print(f'{len(windows)} windows; {len(rows)} instructions; {len(models)} vendor model clauses; {len(expect)} instruction assertions; {len(edges)} JAL edges; {len(pairs)} AUIPC/JALR edges; {len(store_checks)} raw S-type checks; initialization checks passed')
