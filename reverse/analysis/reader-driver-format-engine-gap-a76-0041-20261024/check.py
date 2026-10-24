"""Only registered bounded static decode/bitfield assertions; no ISA execution."""
import json
from pathlib import Path
from capstone import Cs, CS_ARCH_RISCV, CS_MODE_RISCV32, CS_MODE_RISCVC
MAIN=Path('D:/Documents/PlatformIO/Projects/cuktech-ap01-firmware')
OUT=Path(__file__).resolve().parent
WINDOWS=[(0xa01a37d2,0xa01a3852),(0xa01a3852,0xa01a38c0),
         (0xa01a38e4,0xa01a3950),(0xa01a4408,0xa01a4430),
         (0xa01a38c8,0xa01a38e4),(0xa01a3a78,0xa01a3ad8),
         (0xa01a3a46,0xa01a3a78)]
md=Cs(CS_ARCH_RISCV,CS_MODE_RISCV32|CS_MODE_RISCVC)
raw={}; rows=[]
with (MAIN/'roms/0041/ap01-1.0.2_0041.bin').open('rb') as f:
    for start,end in WINDOWS:
        f.seek(start-0x9ffff000); b=f.read(end-start)
        assert len(b)==end-start
        raw.update({start+n:x for n,x in enumerate(b)})
        rr=[{'va':hex(i.address),'bytes':i.bytes.hex(),'asm':i.mnemonic+' '+i.op_str}
            for i in md.disasm(b,start)]
        decoded=sum(len(bytes.fromhex(r['bytes'])) for r in rr)
        if start==0xa01a38e4:
            assert start+decoded==0xa01a38f4  # off selected fixed-s path; do not skip/fill unknown
        elif start==0xa01a38c8:
            assert start+decoded==0xa01a38dc  # digit side-path, not selected fixed-s
        elif start==0xa01a3a78:
            assert start+decoded==0xa01a3a80  # star side-path, not selected fixed-s
        elif start==0xa01a3a46:
            assert start+decoded==0xa01a3a5e  # j side-path, not selected fixed-s
        else:
            assert decoded==len(b)
        rows.extend(rr)
        if start==0xa01a3a78:
            rr=[{'va':hex(i.address),'bytes':i.bytes.hex(),'asm':i.mnemonic+' '+i.op_str}
                for i in md.disasm(b[0xa01a3aa8-start:],0xa01a3aa8)]
            assert 0xa01a3aa8+sum(len(bytes.fromhex(r['bytes'])) for r in rr)==0xa01a3ad2
            rows.extend(rr)  # start is an independently checked direct BNE target
checks=[]
def check(label,actual,expected):
    assert actual==expected,(label,actual,expected)
    checks.append({'label':label,'actual':actual})
def w(va,n=4):return sum(raw[va+i]<<(8*i) for i in range(n))
def sx(x,n):return x-(1<<n) if x&(1<<(n-1)) else x
def ifields(va):
    x=w(va);return (x&127,(x>>7)&31,(x>>12)&7,(x>>15)&31,sx(x>>20,12))
def sfields(va):
    x=w(va);return (x&127,(x>>12)&7,(x>>15)&31,(x>>20)&31,sx(((x>>25)<<5)|((x>>7)&31),12))
def bfields(va):
    x=w(va);imm=((x>>31)<<12)|(((x>>7)&1)<<11)|(((x>>25)&63)<<5)|(((x>>8)&15)<<1)
    return (x&127,(x>>12)&7,(x>>15)&31,(x>>20)&31,hex(va+sx(imm,13)))
def jfields(va):
    x=w(va);imm=((x>>31)<<20)|(((x>>12)&255)<<12)|(((x>>20)&1)<<11)|(((x>>21)&1023)<<1)
    return (x&127,(x>>7)&31,hex(va+sx(imm,21)))
for va,expect in [(0xa01a37f4,0x8b3a),(0xa01a37fe,0x84aa),(0xa01a3814,0x4901),
                  (0xa01a384a,0x0905),(0xa01a384e,0x85ce),(0xa01a3850,0x8526)]:
    check(hex(va)+' C anchor',w(va,2),expect)
check('fmt initial U8',ifields(0xa01a3832),(3,19,4,13,0))
check('zero format branch',bfields(0xa01a3836),(99,0,19,0,'0xa01a4410'))
check('percent constant',ifields(0xa01a383a),(19,15,0,0,0x25))
check('percent branch',bfields(0xa01a383e),(99,0,19,15,'0xa01a3858'))
check('literal continuation',ifields(0xa01a3842),(19,15,0,13,1))
check('literal continuation slot',sfields(0xa01a3846),(35,2,8,15,-0x6c))
x=w(0xa01a384c,2)
check('C.LW S+4',((x>>13)&7,8+((x>>2)&7),8+((x>>7)&7),
    ((x>>10)&7)<<3|((x>>6)&1)<<2|((x>>5)&1)<<6),(2,15,9,4))
for va,rd,rs,off in [(0xa01a37f6,14,15,0x1e8),(0xa01a37fa,15,15,0x1ec),
                     (0xa01a380c,14,15,0x698),(0xa01a3810,15,15,0x69c),
                     (0xa01a3822,14,15,0x690),(0xa01a3826,15,15,0x694)]:
    check(hex(va)+' constant LW',ifields(va),(3,rd,2,rs,off))
for va,rs,off in [(0xa01a3800,14,-0x80),(0xa01a3804,15,-0x7c),
                  (0xa01a3816,14,-0x88),(0xa01a381a,15,-0x84),
                  (0xa01a382a,14,-0x70),(0xa01a382e,15,-0x8c)]:
    check(hex(va)+' local SW',sfields(va),(35,2,8,rs,off))
check('literal C.JALR a5',w(0xa01a3852,2),0x9782)
check('literal continuation jump',jfields(0xa01a3854),(111,0,'0xa01a4408'))
check('percent U8 next',ifields(0xa01a3858),(3,19,4,13,1))
check('percent fmt+2',ifields(0xa01a385c),(19,14,0,13,2))
check('percent next slot',sfields(0xa01a3860),(35,2,8,14,-0x6c))
check('double percent branch',bfields(0xa01a3864),(99,0,19,15,'0xa01a384a'))
for va,hx in [(0xa01a3872,0x4a01),(0xa01a3874,0x4a81),(0xa01a3876,0x4d01)]:
    check(hex(va)+' zero state anchor',w(va,2),hx)
check('flags unsigned gate',bfields(0xa01a38b4),(99,6,14,26,'0xa01a3a42'))
check('plus equality',bfields(0xa01a38b8),(99,0,19,11,'0xa01a3a2c'))
check('unsigned plus compare',bfields(0xa01a38bc),(99,6,11,19,'0xa01a38e4'))
check('minus equality skipped',bfields(0xa01a38e4),(99,0,19,28,'0xa01a3a36'))
check('zero inequality taken',bfields(0xa01a38e8),(99,1,19,29,'0xa01a38c8'))
check('saved fmt reload',ifields(0xa01a4408),(3,13,2,8,-0x6c))
check('format loop back',jfields(0xa01a440c),(111,0,'0xa01a3832'))
check('return local counter',w(0xa01a4428,2),0x854a)
check('engine RET',w(0xa01a442e,2),0x8082)
check('digit normalization',ifields(0xa01a38c8),(19,15,0,19,-0x30))
check('digit byte mask',ifields(0xa01a38cc),(19,15,7,15,255))
check('fixed s beyond digit branch',bfields(0xa01a38d0),(99,6,7,15,'0xa01a3a78'))
check('star constant',ifields(0xa01a3892),(19,10,0,0,0x2a))
check('dot constant',ifields(0xa01a3896),(19,17,0,0,0x2e))
check('fixed s skips star',bfields(0xa01a3a78),(99,1,19,10,'0xa01a3aa8'))
check('fixed s skips dot',bfields(0xa01a3aa8),(99,1,19,17,'0xa01a3a46'))
for va,rd,v in [(0xa01a387c,27,0x74),(0xa01a3880,25,0x6a),(0xa01a3884,24,0x4c),
                (0xa01a3a46,15,0x7a)]:
    check(hex(va)+' modifier constant',ifields(va),(19,rd,0,0,v))
check('fixed s skips z',bfields(0xa01a3a4a),(99,0,19,15,'0xa01a3ac2'))
check('fixed s skips t',bfields(0xa01a3a4e),(99,0,19,27,'0xa01a3ac2'))
check('fixed s skips j',bfields(0xa01a3a52),(99,1,19,25,'0xa01a3aba'))
check('modifier case mask',ifields(0xa01a3aba),(19,15,7,19,0xdf))
check('fixed s skips L/l',bfields(0xa01a3abe),(99,1,15,24,'0xa01a3ae0'))
OUT.mkdir(parents=True,exist_ok=True)
(OUT/'evidence.json').write_text(json.dumps({'windows':[[hex(a),hex(b)] for a,b in WINDOWS],
    'instructions':rows,'decoder_stops_off_selected_path':['0xa01a38f4','0xa01a38dc','0xa01a3a80','0xa01a3ad2','0xa01a3a5e'],
    'undecoded_prefix_bytes':{hex(a):bytes(raw[a+i] for i in range(4)).hex() for a in [0xa01a38f4,0xa01a38dc,0xa01a3a80,0xa01a3ad2,0xa01a3a5e]},
    'checks':checks,'check_count':len(checks)},indent=2)+'\n',encoding='utf-8')
print('A76 static checks',len(checks),'registered bytes',sum(b-a for a,b in WINDOWS))
