"""A77 independent static selected-edge review; no author code/model/input execution."""
import json
from pathlib import Path
from capstone import Cs,CS_ARCH_RISCV,CS_MODE_RISCV32,CS_MODE_RISCVC
MAIN=Path('D:/Documents/PlatformIO/Projects/cuktech-ap01-firmware')
WINDOWS=[(0xa01a37d2,0xa01a3852),(0xa01a3852,0xa01a38c0),(0xa01a38e4,0xa01a3950),
 (0xa01a4408,0xa01a4430),(0xa01a38c8,0xa01a38e4),(0xa01a3a78,0xa01a3ad8),(0xa01a3a46,0xa01a3a78)]
p=MAIN/'roms/0041/ap01-1.0.2_0041.bin'
assert p.stat().st_size==6769704
raw={}
with p.open('rb') as f:
 for lo,hi in WINDOWS:
  f.seek(lo-0x9ffff000); b=f.read(hi-lo); assert len(b)==hi-lo
  raw.update({lo+i:v for i,v in enumerate(b)})
def w(pc,n=4):return int.from_bytes(bytes(raw[pc+i] for i in range(n)),'little')
def sx(x,n):return x-(1<<n) if x&(1<<(n-1)) else x
checks=[]
def check(name,value,expected):
 assert value==expected,(name,value,expected)
 checks.append({'check':name,'value':value})
def I(pc):
 x=w(pc);return [x&127,(x>>7)&31,(x>>12)&7,(x>>15)&31,sx(x>>20,12)]
def B(pc):
 x=w(pc);off=((x>>31)<<12)|(((x>>7)&1)<<11)|(((x>>25)&63)<<5)|(((x>>8)&15)<<1)
 return [x&127,(x>>12)&7,(x>>15)&31,(x>>20)&31,pc+sx(off,13)]
def S(pc):
 x=w(pc);return [x&127,(x>>12)&7,(x>>15)&31,(x>>20)&31,sx(((x>>25)<<5)|((x>>7)&31),12)]
for pc,opcode,rd,f3,rs,imm in [
 (0xa01a3832,3,19,4,13,0),(0xa01a383a,19,15,0,0,37),(0xa01a3842,19,15,0,13,1),
 (0xa01a3858,3,19,4,13,1),(0xa01a385c,19,14,0,13,2),
 (0xa01a3878,19,14,0,0,63),(0xa01a387c,19,27,0,0,116),(0xa01a3880,19,25,0,0,106),
 (0xa01a3884,19,24,0,0,76),(0xa01a3892,19,10,0,0,42),(0xa01a3896,19,17,0,0,46),
 (0xa01a38a0,19,11,0,0,43),(0xa01a38a4,19,28,0,0,45),(0xa01a38a8,19,29,0,0,48),
 (0xa01a38c8,19,15,0,19,-48),(0xa01a38cc,19,15,7,15,255),
 (0xa01a3a46,19,15,0,0,122),(0xa01a3aba,19,15,7,19,223),
 (0xa01a4408,3,13,2,8,-108)]:
 check('I:'+hex(pc),I(pc),[opcode,rd,f3,rs,imm])
for pc,funct,r1,r2,target in [
 (0xa01a3836,0,19,0,0xa01a4410),(0xa01a383e,0,19,15,0xa01a3858),
 (0xa01a3864,0,19,15,0xa01a384a),(0xa01a38b4,6,14,26,0xa01a3a42),
 (0xa01a38b8,0,19,11,0xa01a3a2c),(0xa01a38bc,6,11,19,0xa01a38e4),
 (0xa01a38e4,0,19,28,0xa01a3a36),(0xa01a38e8,1,19,29,0xa01a38c8),
 (0xa01a38d0,6,7,15,0xa01a3a78),(0xa01a3a78,1,19,10,0xa01a3aa8),
 (0xa01a3aa8,1,19,17,0xa01a3a46),(0xa01a3a4a,0,19,15,0xa01a3ac2),
 (0xa01a3a4e,0,19,27,0xa01a3ac2),(0xa01a3a52,1,19,25,0xa01a3aba),
 (0xa01a3abe,1,15,24,0xa01a3ae0)]:
 check('B:'+hex(pc),B(pc),[99,funct,r1,r2,target])
for pc,src in [(0xa01a3846,15),(0xa01a3860,14)]:
 check('saved-next-fmt:'+hex(pc),S(pc),[35,2,8,src,-108])
for pc,rd,rs in [(0xa01a37f4,22,14),(0xa01a37fe,9,10),(0xa01a384e,11,19),(0xa01a3850,10,9),(0xa01a4428,10,18)]:
 x=w(pc,2)
 check('C.MV:'+hex(pc),[x&3,x>>13,(x>>12)&1,(x>>7)&31,(x>>2)&31],[2,4,0,rd,rs])
for pc,rd,val in [(0xa01a3814,18,0),(0xa01a3872,20,0),(0xa01a3874,21,0),(0xa01a3876,26,0),(0xa01a3890,7,9)]:
 x=w(pc,2)
 check('C.LI:'+hex(pc),[x&3,x>>13,(x>>7)&31,sx(((x>>2)&31)|(((x>>12)&1)<<5),6)],[1,2,rd,val])
x=w(0xa01a384a,2)
check('C.ADDI engine-count',[x&3,x>>13,(x>>7)&31,sx(((x>>2)&31)|(((x>>12)&1)<<5),6)],[1,0,18,1])
x=w(0xa01a384c,2)
check('C.LW callback-slot',[x&3,x>>13,8+((x>>2)&7),8+((x>>7)&7),(((x>>10)&7)<<3)|(((x>>6)&1)<<2)|(((x>>5)&1)<<6)],[0,2,15,9,4])
x=w(0xa01a3852,2)
check('C.JALR actual call',[x&3,x>>13,(x>>12)&1,(x>>7)&31,(x>>2)&31],[2,4,1,15,0])
for pc,target in [(0xa01a3854,0xa01a4408),(0xa01a440c,0xa01a3832)]:
 x=w(pc);off=((x>>31)<<20)|(((x>>12)&255)<<12)|(((x>>20)&1)<<11)|(((x>>21)&1023)<<1)
 check('J:'+hex(pc),[x&127,(x>>7)&31,pc+sx(off,21)],[111,0,target])

# Ordinary finite coverage/stop audit. No continuation past an undecoded prefix except true aa8 branch target.
md=Cs(CS_ARCH_RISCV,CS_MODE_RISCV32|CS_MODE_RISCVC)
stops={0xa01a38e4:0xa01a38f4,0xa01a38c8:0xa01a38dc,0xa01a3a78:0xa01a3a80,0xa01a3a46:0xa01a3a5e}
decoded={}
for lo,hi in WINDOWS:
 b=bytes(raw[pc] for pc in range(lo,hi)); rows=list(md.disasm(b,lo))
 end=lo+sum(i.size for i in rows)
 check('decode-boundary:'+hex(lo),end,stops.get(lo,hi))
 decoded.update({i.address:i for i in rows})
lo=0xa01a3aa8; hi=0xa01a3ad8
rows=list(md.disasm(bytes(raw[pc] for pc in range(lo,hi)),lo))
check('true-target-aa8-decode-boundary',lo+sum(i.size for i in rows),0xa01a3ad2)
decoded.update({i.address:i for i in rows})
check('entry-frame',decoded[0xa01a37d2].op_str,'sp, -0xa0')
ep=[i for pc,i in sorted(decoded.items()) if 0xa01a4410<=pc<0xa01a4430]
check('epilogue-effect-inventory',[i.mnemonic for i in ep],['c.lwsp']*12+['c.mv','c.lwsp','c.addi16sp','c.jr'])
check('return-count-before-restore',[decoded[0xa01a4428].op_str,decoded[0xa01a442a].op_str,decoded[0xa01a442c].op_str,decoded[0xa01a442e].op_str],['a0, s2','s2, 0x90(sp)','sp, 0xa0','ra'])
saved={i.op_str.split(',')[0] for pc,i in decoded.items() if 0xa01a37d2<=pc<0xa01a37f4 and i.mnemonic=='c.swsp'}
check('callee-save-entry-set',sorted(saved),sorted(['ra','s0','s1','s2','s3','s4','s5','s6','s7','s8','s9','s10','s11']))
check('entry-fmt-not-redefined',any(i.op_str.startswith('a3,') for pc,i in decoded.items() if 0xa01a37d2<=pc<0xa01a3832 and not i.mnemonic.startswith(('sw','c.sw'))),False)
selected_spans=[(0xa01a37f6,0xa01a3858),(0xa01a3858,0xa01a38c0),(0xa01a38e4,0xa01a38ec),
 (0xa01a38c8,0xa01a38d4),(0xa01a3a78,0xa01a3a7c),(0xa01a3aa8,0xa01a3aac),
 (0xa01a3a46,0xa01a3a56),(0xa01a3aba,0xa01a3ac2)]
selected=[i for pc,i in decoded.items() if any(lo<=pc<hi for lo,hi in selected_spans)]
check('selected-post-save-no-va-register-use',any('s6' in i.op_str for i in selected),False)
out={'task':'A77','checks_pass':len(checks),'checks':checks,'windows':[[hex(a),hex(b)] for a,b in WINDOWS],
 'read_bytes':sum(b-a for a,b in WINDOWS),'five_offpath_unknown_prefixes':{hex(pc):w(pc).to_bytes(4,'little').hex() for pc in [0xa01a38f4,0xa01a38dc,0xa01a3a80,0xa01a3ad2,0xa01a3a5e]},
 'method':'static fields; Capstone5.0.7 RV32/RVC coverage only; no model or input execution',
 'frontier':'a01a3abe ->a01a3ae0; no bytes at3ae0 read','new_business':0}
Path(__file__).with_name('evidence.json').write_text(json.dumps(out,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
print(f'PASS {len(checks)} independent static checks; seven windows560B; 3ae0 untouched')
