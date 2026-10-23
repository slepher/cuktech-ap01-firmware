"""A09: bounded static ROM reads, no execution or shared analysis state."""
import json
from pathlib import Path
from capstone import Cs, CS_ARCH_RISCV, CS_MODE_RISCV32, CS_MODE_RISCVC, __version__
HERE = Path(__file__).resolve().parent
ROOT = Path('D:/Documents/PlatformIO/Projects/cuktech-ap01-firmware')
raw = (ROOT/'roms/0041/ap01-1.0.2_0041.bin').read_bytes()
BASE = 0x9ffff000
md = Cs(CS_ARCH_RISCV, CS_MODE_RISCV32 | CS_MODE_RISCVC)
checks = []
def u(pc, n=4): return int.from_bytes(raw[pc-BASE:pc-BASE+n], 'little')
def signed(v,n): return (v ^ (1 << (n-1))) - (1 << (n-1))
def ck(pc, kind, actual, expected):
    assert actual == expected, (hex(pc),kind,actual,expected)
    checks.append(dict(pc=hex(pc),kind=kind,actual=actual,expected=expected))
def mem(pc,store,reg,base,off,width=2):
    w=u(pc); imm=signed(((w>>25)<<5)|(w>>7&31),12) if store else signed(w>>20,12)
    ck(pc,'raw memory fields',[w&127,w>>12&7,w>>15&31,w>>(20 if store else 7)&31,imm],[0x23 if store else 3,width,base,reg,off])
def mv(pc,rd,rs):
    w=u(pc,2);ck(pc,'C.MV fields',[w&0xf003,w>>7&31,w>>2&31],[0x8002,rd,rs])
def call(pc,target,pair=False):
    w=u(pc)
    if pair:
        v=u(pc+4);ck(pc,'AUIPC/JALR fields',[w&0xfff,v&0xfffff],[0x97,0x80e7]); actual=pc+signed(w&0xfffff000,32)+signed(v>>20,12)
    else:
        ck(pc,'JAL ra fields',w&0xfff,0xef); imm=(w>>31<<20)|((w>>12&255)<<12)|((w>>20&1)<<11)|((w>>21&1023)<<1);actual=pc+signed(imm,21)
    ck(pc,'direct target',hex(actual&0xffffffff),hex(target))
def window(lo,hi):
    start=lo; ins=[]
    while lo<hi:
        b=raw[lo-BASE:lo-BASE+4];i=next(md.disasm(b,lo,1),None);n=i.size if i else (4 if b[0]&3==3 else 2)
        ins.append(dict(pc=hex(lo),bytes=b[:n].hex(),asm=i.mnemonic+' '+i.op_str if i else 'UNKNOWN; no vendor semantics assigned'));lo+=n
    assert lo==hi
    return dict(start=hex(start),end_exclusive=hex(hi),instructions=ins)
windows=[window(0xa012f946,0xa012f9b0),window(0xa0051dac,0xa0051dd2),window(0xa0030ef8,0xa0031108)]
for args in [(0xa012f956,False,9,15,-1000),(0xa012f95e,False,11,9,17,4),(0xa012f962,False,15,9,16,4),(0xa012f98a,False,15,9,304),(0xa012f99c,False,11,9,308),(0xa0030f1e,True,12,8,-68),(0xa0030f22,True,13,8,-72),(0xa0030fc0,False,15,8,-68),(0xa0030fd2,True,15,23,20),(0xa0030fda,False,15,8,-72),(0xa0030ff4,True,15,23,24)]: mem(*args)
for args in [(0xa012f96a,10,9),(0xa0051dc8,15,10),(0xa0051dca,10,11),(0xa0030f1a,23,10)]:mv(*args)
ck(0xa012f990,'C.LW a0,24(s1)',u(0xa012f990,2),0x4c88)
for pc in [0xa012f9a0,0xa0051dcc]:ck(pc,'C.JALR a5',u(pc,2),0x9782)
def compact_branch(pc,mask,reg,target):
    w=u(pc,2);imm=((w>>12&1)<<8)|((w>>10&3)<<3)|((w>>5&3)<<6)|((w>>3&3)<<1)|((w>>2&1)<<5)
    ck(pc,'compact conditional fields',[w&0xe003,(w>>7&7)+8,hex(pc+signed(imm,9))],[mask,reg,hex(target)])
compact_branch(0xa012f98e,0xc001,15,0xa012f994)
compact_branch(0xa012f992,0xe001,10,0xa012f99c)
compact_branch(0xa0051db4,0xe001,10,0xa0051dc8)
for pc,kind,target in [(0xa012f966,7,0xa012f98a),(0xa012f974,5,0xa012f98a)]:
    w=u(pc);imm=((w>>31)<<12)|((w>>7&1)<<11)|((w>>25&63)<<5)|((w>>8&15)<<1)
    ck(pc,'branch target and funct3',[w&127,w>>12&7,hex(pc+signed(imm,13))],[0x63,kind,hex(target)])
ck(0xa012f952,'LUI a5',u(0xa012f952),0x62fc77b7)
call(0xa012f96c,0xa0028d1c,True);call(0xa012f982,0xa0019672,True)
call(0xa0051dc4,0xa0019672);call(0xa0051dce,0xa00306b4)
inventory=json.loads((ROOT/'evidence/rea-0041-20261017/evidence/whole-rom-coverage-0041-20261023-initial.json').read_text(encoding='utf8'))
selected=[]
for f in inventory['functions']:
    if f['address'] in ['0xa012f946','0xa0051dac','0xa0030ef8']:
        selected.append({k:f[k] for k in ['address','inventory_evidence','extent','source_paths','families','excluded_as_verified_open_source']})
assert len(selected)==3
out=dict(task='A09',capstone=__version__,base=hex(BASE),windows=windows,checks=checks,inventory=selected,limits=['Original-entry/userdata provenance across A07 custom words remains conditional','Third function only argument-save/reload/store local semantics restored','No actual current-object identity, launch, scheduler or buzzer connection proven'])
out['strings']=[dict(address=hex(a),text=raw[a-BASE:a-BASE+150].split(b'\0')[0].decode('ascii')) for a in [0xa01c0598,0xa01bd0e4,0xa01bba2c]]
(HERE/'instruction-evidence.json').write_text(json.dumps(out,indent=2)+'\n',encoding='utf8')
print('PASS',len(checks),'checks;',sum(len(w['instructions']) for w in windows),'instruction slots;',sum(int(w['end_exclusive'],16)-int(w['start'],16) for w in windows),'bytes')
