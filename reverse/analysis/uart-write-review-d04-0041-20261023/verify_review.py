"""Independent D04 static review; reads ROM, never executes target code."""
from pathlib import Path
import json, struct
from capstone import Cs, CS_ARCH_RISCV, CS_MODE_RISCV32, CS_MODE_RISCVC

HERE = Path(__file__).resolve().parent
ROOT = Path('D:/Documents/PlatformIO/Projects/cuktech-ap01-firmware')
BASE = 0x9ffff000
ROM = ROOT/'roms/0041/ap01-1.0.2_0041.bin'
raw = ROM.read_bytes()
cs = Cs(CS_ARCH_RISCV, CS_MODE_RISCV32 | CS_MODE_RISCVC)
regions = [
 ('file_dispatch_lookup',0xa0025874,0xa002595c),
 ('release_wrapper',0xa0027e54,0xa0027eee),
 ('registration_callers',0xa0029690,0xa00296e0),
 ('inode_uart_registration',0xa01b5a12,0xa01b5b0e),
 ('file_install',0xa01b5bec,0xa01b5c3a),
 ('open_inner_slice',0xa003eb4e,0xa003eb7c),
 ('open_wrapper',0xa003f4f6,0xa003f546),
 ('application_open',0xa005ab10,0xa005ab32),
 ('application_fd_config',0xa005b214,0xa005b2e6),
 ('ring_and_write',0xa002c140,0xa002c3a6),
 ('direct_send',0xa002ad82,0xa002adde),
 ('lower_ready',0xa001972c,0xa001973a),
 ('lower_callbacks',0xa0019810,0xa00198bc),
 ('context_predicate',0xa0027830,0xa002786c),
 ('final_close_boundary',0xa0027d9a,0xa0027dc0),
]
regs = 'zero ra sp gp tp t0 t1 t2 s0 s1 a0 a1 a2 a3 a4 a5 a6 a7 s2 s3 s4 s5 s6 s7 s8 s9 s10 s11 t3 t4 t5 t6'.split()
sx = lambda n,b: n-(1<<b) if n & (1<<(b-1)) else n
word = lambda a: int.from_bytes(raw[a-BASE:a-BASE+4], 'little')
model_path=ROOT/'evidence/rea-0041-20261017/ghidra/Ghidra/Processors/RISCV/data/languages/ap01thead2.sinc'
model=model_path.read_text().splitlines()
vendor_rows=[]; model_rows={}; rows={}; windows=[]

def custom(pc,w):
    rd=(w>>7)&31; r1=(w>>15)&31; r2=(w>>20)&31
    f=(w>>12)&7; hi=w>>27; shift=(w>>25)&3
    fields={'opcode':w&127,'rd':rd,'rs1':r1,'rs2':r2,'funct3':f,'high5':hi,'shift':shift}
    if f==1 and w>>25==16:
        name='mula'; args=f'{regs[rd]}, {regs[r1]}, {regs[r2]}'
    elif f==4 and hi in (8,16):
        name={8:'lrw',16:'lrbu'}[hi]; args=f'{regs[rd]}, {regs[r1]}, {regs[r2]}, {shift}'
    elif f==5 and hi==0:
        name='srb'; args=f'{regs[rd]}, {regs[r1]}, {regs[r2]}, {shift}'
    elif f==4 and hi==19:
        name='lbuia'; args=f'{regs[rd]}, {regs[r1]}, {sx(r2,5)}, {shift}'
    elif f in (2,3):
        name='ext' if f==2 else 'extu'; args=f'{regs[rd]}, {regs[r1]}, {(w>>26)&31}, {r2}'
    else: raise AssertionError((hex(pc),hex(w)))
    prefix=f':th.{name} '
    if name in ('ext','extu'): prefix=f':th.{name} rd,rs1,{(w>>26)&31},{r2} '
    start=next(i for i,line in enumerate(model) if line.startswith(prefix))
    stop=next(i for i in range(start+1,len(model)) if model[i]=='}')
    model_rows[prefix]={'line':start+1,'body':'\n'.join(model[start:stop+1])}
    decode=f'th.{name} {args}'
    vendor_rows.append({'address':hex(pc),'word':hex(w),'fields':fields,'decode':decode})
    return decode

for name,start,end in regions:
    items=[]; pc=start
    while pc<end:
        w=word(pc); size=2 if w&3!=3 else 4
        b=raw[pc-BASE:pc-BASE+size]; assert pc+size<=end
        if size==4 and w&127==11: decoded=custom(pc,w)
        else:
            ins=list(cs.disasm(b,pc)); assert len(ins)==1 and ins[0].size==size
            decoded=ins[0].mnemonic+' '+ins[0].op_str
        item={'address':hex(pc),'file_offset':hex(pc-BASE),'bytes':b.hex(),'decode':decoded}
        rows[pc]=item; items.append(item); pc+=size
    windows.append({'name':name,'start':hex(start),'end_exclusive':hex(end),'instructions':items})

# New assertions emphasize control flow omitted from D03's simplified pseudocode.
expect = {
0xa00258ce:'c.beqz a3, 0x12',0xa00258d0:'c.lw a5, 4(a0)',
0xa00258d2:'c.bnez a5, -0x12',0xa00258c0:'c.addi a5, 1',
0xa00258c2:'c.sw a5, 4(a0)',0xa00258d4:'c.li a5, 2',
0xa00258da:'sb a5, 0(a3)',0xa00258f2:'c.li a3, 0',
0xa00258ae:'th.lrw a0, a5, a1, 2',0xa00258b4:'th.mula a0, a2, a5',
0xa00258e6:'rem a2, a1, a5',0xa00258f4:'div a1, a1, a5',
0xa0025904:'sw zero, 0(a1)',0xa002591c:'lbu a5, 0x5c(a5)',
0xa0025926:'bge a0, a5, 0x32',0xa00258a8:'csrrc a4, mstatus, a4',
0xa00258c4:'csrw mstatus, a4',0xa0027e72:'csrrc a4, mstatus, a4',
0xa0027e78:'c.addi a5, -1',0xa0027e7c:'csrw mstatus, a4',
0xa0027ec6:'c.mv s1, a0',0xa0027ec8:'lw a0, -0x14(s0)',
0xa0027ed0:'bgez s1, 0x10',0xa0027edc:'c.sw s1, 0(a0)',
0xa0027ee6:'c.mv a0, s1',0xa0025890:'c.jalr a4',
0xa01b5a3a:'bltz a0, 0x32',0xa01b5a4a:'c.sw s1, 0x10(a4)',
0xa01b5a4c:'c.sw a2, 0x18(a4)',0xa01b5a54:'sh a5, 0xe(a4)',
0xa01b5af6:'c.mv a2, s1',0xa01b5afa:'addi a1, a1, 0x7c8',
0xa005ab2e:'bgtz a0, 0x6e6',0xa005b232:'sw s5, 0(s6)',
0xa01b5c08:'c.sw a4, 4(a1)',0xa002c228:'c.lw s1, 0x18(a5)',
0xa002c324:'th.lrbu a1, s6, a5, 0',0xa002c30a:'th.extu s5, s5, 6, 6',
0xa002c338:'c.bnez a4, 0x18',0xa002c350:'andi a5, a5, 0x24',
0xa002c348:'c.addi s4, -1',0xa002c36a:'bgeu s4, s3, 8',
0xa002c36e:'sub s2, s3, s4',0xa002c272:'c.mv a0, s2',
0xa002c15c:'lh a5, 0x54(a0)',0xa002c162:'th.ext s2, s2, 15, 0',
0xa002c192:'th.srb s3, a4, a5, 0',0xa002c196:'sh s2, 0x50(s1)',
0xa002c1e0:'c.jalr a5',0xa002c1f4:'c.jalr a5',
0xa002c1f6:'csrw mstatus, s8',0xa002c25a:'c.mv s2, s3',
0xa002adba:'c.beqz a4, 0x16',0xa002add2:'th.lbuia a1, s1, 1, 0',
0xa002add8:'c.addi s2, -1',0xa002adda:'c.jalr a5',
0xa0019882:'sw a1, -0x14(s0)',0xa001988c:'bltu a5, a3, 0x18',
0xa00198b0:'c.li a2, 1',0xa00198b4:'addi a1, s0, -0x14',
0xa0019734:'c.li a0, 1',
}
for pc,decode in expect.items(): assert rows[pc]['decode']==decode,(hex(pc),rows[pc],decode)

edges=[]
for pc,target in {0xa002593a:0xa00258e4,0xa00258f8:0xa00258a0,
 0xa0027eae:0xa0025904,0xa0027ec2:0xa0025874,0xa0027ecc:0xa0027e54,
 0xa0027e84:0xa0027d9a,0xa01b5a36:0xa01b5908,0xa01b5afe:0xa01b5a12,
 0xa003f524:0xa003eb14,0xa005ab1c:0xa003f4f6,
 0xa002c33e:0xa002c140,0xa002c360:0xa002c140,0xa002c252:0xa002ad82,
 0xa002c292:0xa002ad82,0xa002c29e:0xa002ad82,
 0xa002c2c2:0xa002ad82,0xa002c2ce:0xa002ad82}.items():
    w=word(pc); assert w&127==0x6f
    imm=((w>>31)<<20)|(((w>>12)&255)<<12)|(((w>>20)&1)<<11)|(((w>>21)&1023)<<1)
    assert (pc+sx(imm,21))&0xffffffff==target
    edges.append({'pc':hex(pc),'target':hex(target),'kind':'raw J'})
for pc,target in {0xa00296c4:0xa01b5a7e,0xa003eb66:0xa01b5b74,0xa0019894:0x62fc22ae}.items():
    w,z=word(pc),word(pc+4); assert w&127==0x17 and z&127==0x67
    assert (pc+sx(w&0xfffff000,32)+sx(z>>20,12))&0xfffffffe==target
    edges.append({'pc':hex(pc),'target':hex(target),'kind':'raw AUIPC/JALR'})
# Independent compressed B immediate reconstruction for the correction edge.
hw=word(0xa00258d2)&0xffff
imm=(((hw>>12)&1)<<8)|(((hw>>10)&3)<<3)|(((hw>>5)&3)<<6)|(((hw>>3)&3)<<1)|(((hw>>2)&1)<<5)
assert (hw>>13)==7 and ((hw>>7)&7)+8==15
assert 0xa00258d2+sx(imm,9)==0xa00258c0
edges.append({'pc':'0xa00258d2','target':'0xa00258c0','kind':'raw C.BNEZ; rs1=a5'})
# Width checks use encodings, not the disassembler's text.
stores=[]
for pc,f,r1,r2,disp in [(0xa002c196,1,9,18,0x50),(0xa01b5a54,1,14,15,14),
 (0xa005b232,2,22,21,0),(0xa0019882,2,8,11,-20)]:
    w=word(pc); actual=((w>>7)&31)|((w>>25)<<5)
    assert (w&127,(w>>12)&7,(w>>15)&31,(w>>20)&31,sx(actual,12))==(35,f,r1,r2,disp)
    stores.append({'pc':hex(pc),'width_bytes':1<<f,'base_register':r1,'source_register':r2,'offset':disp})

init=0xa00027d4+0x62fc36d0-0x62fc2cc0
assert init==0xa00031e4
checks={0xa066d7d4:0xa002c206,init+0xa0:0xa01bcb18,init+0xa4:0x62fc36b4,
 init+0x58:0x62fc78a8,0xa01bcb48:0xa0019876,0xa01bcb4c:0xa0019810,
 0xa01bcb50:0xa001972c,0xa01bcb44:0xa001a70a,0xa01bcb60:0}
for pc,v in checks.items(): assert word(pc)==v
assert struct.unpack_from('<HHH',raw,init+0x50-BASE)==(0,0,0x400)
assert raw[0xa00027d4+0x62fc36b4-0x62fc2cc0-BASE]==1
assert raw[0xa01bc32c-BASE:0xa01bc32c-BASE+11]==b'/dev/ttyS1\0'
assert raw[0xa0566d7c-BASE]==13 and raw[0xa062cda0-BASE]==10

# Only compare after decoding and semantic assertions; D03 does not drive them.
prior=json.loads((HERE.parent/'uart-write-object-d03-0041-20261023/instruction-evidence.json').read_text(encoding='utf-8'))
overlap=0
for win in prior['windows']:
    for row in win['instructions']:
        pc=int(row['address'],16)
        if pc in rows:
            assert rows[pc]['bytes']==row['bytes']; overlap+=1
out={'task':'D04','rom':str(ROM),'mapping':'offset=VA-0x9ffff000',
 'windows':windows,'exact_assertions':[{'pc':hex(p),'decode':d} for p,d in expect.items()],
 'raw_edges':edges,'raw_stores':stores,'vendor_words':vendor_rows,
 'model':{'path':str(model_path),'excerpts':list(model_rows.values())},
 'initializer_checks':[{'rom':hex(p),'word':hex(v)} for p,v in checks.items()],
 'prior_raw_overlap':overlap,
 'limitations':['Static only; no execution, replay, external source lookup, model changes or shared REA session.',
 'RAM copy mapping uses reviewed startup contract, not runtime state.',
 'No source/version certification; path resolver, final close and ring consumer remain bounded unknowns.']}
(HERE/'review-evidence.json').write_text(json.dumps(out,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
print(json.dumps({'passed':True,'windows':len(windows),'instructions':len(rows),'exact_assertions':len(expect),
 'raw_edges':len(edges),'raw_stores':len(stores),'vendor_words':len(vendor_rows),'prior_overlap':overlap}))
