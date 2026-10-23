"""Static original-byte certificate for the E16 fixed positive divisor path.
No firmware, arithmetic helper, input examples, or emulator is executed.
"""
from pathlib import Path
import json
import zipfile
import capstone

HERE=Path(__file__).resolve().parent
ROOT=Path('D:/Documents/PlatformIO/Projects/cuktech-ap01-firmware')
ROM=ROOT/'roms/0041/ap01-1.0.2_0041.bin'
data=ROM.read_bytes()
def read(a,n):
    o=a-0x9ffff000
    assert 0<=o<=len(data)-n
    return data[o:o+n]
def word(a): return int.from_bytes(read(a,4),'little')
def sx(v,n): return (v^(1<<(n-1)))-(1<<(n-1))
checks=[]
def eq(label,a,v,e):
    assert v==e,(label,hex(a),v,e)
    checks.append(dict(label=label,address=hex(a),actual=v,expected=e))
def raw(a,b): eq('original encoding',a,read(a,len(bytes.fromhex(b))).hex(),b)
def branch(a,rs1,rs2,f3,target):
    w=word(a);imm=((w>>31)<<12)|(((w>>7)&1)<<11)|(((w>>25)&63)<<5)|(((w>>8)&15)<<1)
    eq('branch fields/target',a,[w&127,(w>>15)&31,(w>>20)&31,(w>>12)&7,a+sx(imm,13)],[99,rs1,rs2,f3,target])
def op(a,f3,rd,rs1,rs2):
    w=word(a)
    eq('M arithmetic fields',a,[w&127,w>>25,(w>>12)&7,(w>>7)&31,(w>>15)&31,(w>>20)&31],[51,1,f3,rd,rs1,rs2])

# Inherited ABI checked sparsely; no re-export of E16/E17/H15/H16 bodies.
for a,b in [(0xa001b302,'aa88'),(0xa001b304,'ae87'),(0xa001b306,'3288'),(0xa001b308,'3685'),(0xa001b30a,'4683')]:raw(a,b)
for args in [(0xa001b30c,13,0,1,0xa001b518),(0xa001b318,11,12,7,0xa001b3d6),(0xa001b31e,12,14,7,0xa001b3c8),(0xa001b3ce,12,10,6,0xa001b32c),(0xa001b340,10,14,0,0xa001b356),(0xa001b376,15,11,7,0xa001b38e),(0xa001b3aa,6,13,7,0xa001b3c0)]:branch(*args)
for args in [(0xa001b35a,5,13,11,17),(0xa001b368,7,14,11,17),(0xa001b36e,0,11,12,13),(0xa001b390,7,14,15,17),(0xa001b39a,5,15,15,17),(0xa001b3a4,0,13,12,15)]:op(*args)
for a,b in [(0xa001b31c,'4167'),(0xa001b3c8,'37050001'),(0xa001b3cc,'4147'),(0xa001b32c,'3355e600'),(0xa001b330,'aa96'),(0xa001b332,'83c60600'),(0xa001b336,'13050002'),(0xa001b33a,'3697'),(0xa001b33c,'b306e540'),(0xa001b344,'b395d700'),(0xa001b348,'33d7e800'),(0xa001b34c,'3318d600'),(0xa001b350,'d98d'),(0xa001b352,'3393d800'),(0xa001b356,'93580801'),(0xa001b35e,'13160801'),(0xa001b362,'4182'),(0xa001b364,'93570301'),(0xa001b36c,'3685'),(0xa001b372,'4207'),(0xa001b374,'d98f'),(0xa001b38e,'8d8f'),(0xa001b394,'4203'),(0xa001b396,'13530301'),(0xa001b39e,'4207'),(0xa001b3a0,'33636700'),(0xa001b3a8,'3e86'),(0xa001b3c0,'4205'),(0xa001b3c2,'518d'),(0xa001b3c4,'8145'),(0xa001b3c6,'5da8'),(0xa001b47c,'8280')]:raw(a,b)
# Resolve the original normalization lookup address and only its used byte.
x,y=word(0xa001b310),word(0xa001b314)
eq('table AUIPC/ADDI registers',0xa001b310,[x&127,(x>>7)&31,y&127,(y>>7)&31,(y>>15)&31],[23,13,19,13,13])
table=(0xa001b310+sx(x&0xfffff000,32)+sx(y>>20,12))&0xffffffff
eq('normalization lookup base',0xa001b310,table,0xa01bb7f0)
eq('only used lookup byte',table+15,read(table+15,1)[0],4)
h=int.from_bytes(read(0xa001b3c6,2),'little')
imm=(((h>>12)&1)<<11)|(((h>>11)&1)<<4)|(((h>>9)&3)<<8)|(((h>>8)&1)<<10)|(((h>>7)&1)<<6)|(((h>>6)&1)<<7)|(((h>>3)&7)<<1)|(((h>>2)&1)<<5)
eq('compressed jump return target',0xa001b3c6,[h&3,h>>13,0xa001b3c6+sx(imm,12)],[1,5,0xa001b47c])

windows=[('normalization for fixed divisor',0xa001b32c,0xa001b37a),('first remainder and second digit',0xa001b38e,0xa001b3ae),('pair composition and return jump',0xa001b3c0,0xa001b3c8),('fixed divisor bit-length branch',0xa001b3c8,0xa001b3d2),('shared return only',0xa001b47c,0xa001b47e)]
cs=capstone.Cs(capstone.CS_ARCH_RISCV,capstone.CS_MODE_RISCV32|capstone.CS_MODE_RISCVC)
rows=[]
for name,start,end in windows:
    a=start
    while a<end:
        n=2 if int.from_bytes(read(a,2),'little')&3!=3 else 4
        assert a+n<=end
        b=read(a,n);i=next(cs.disasm(b,a),None)
        assert i is not None,(hex(a),b.hex())
        rows.append(dict(window=name,address=hex(a),bytes=b.hex(),asm=i.mnemonic+' '+i.op_str));a+=n

# Constant range facts only; these are not executions of a001b302 or test inputs.
maximum=(2**32-1)*1000000
assert maximum<2**52 and maximum>>32==999999
assert 1000000<<12==0xf4240000
assert (1000000<<12)&65535==0
assert (1000000<<12)>>16==62500
assert 999*1000000<2**31
certificate=dict(domain='t is the one inherited unsigned32 load; D=1000000, high divisor=0',numerator='N=(t//1000)*1000000000+(t%1000)*1000000=t*1000000',maximum_numerator=maximum,maximum_high_word=maximum>>32,normalization_shift=12,normalized_divisor='0xf4240000',radix=65536,normalized_divisor_high_digit=62500,normalized_divisor_low_digit=0,proof=['H<D; actual path bypasses b3d6 and all high-quotient paths.', 'Nprime=N<<12 fits uint64; U=Nprime>>32, V=Nprime mod 2^32; U<62500*65536.', 'q1=U//62500, r1=U%62500; 0<=q1<65536.', 'P=r1*65536+(V>>16); q0=P//62500; 0<=q0<65536.', 'Both MUL operands from the low divisor digit are zero; both unsigned correction gates are taken without correction.', 'q=q1*65536+q0=floor((Nprime>>16)/62500)=floor(N/1000000)=t.', 'a0=(q1<<16)|q0=t; a1=0; shared ret preserves both.'],limit='Numerical identity only. Counter cadence, epoch, writer and runtime scheduling are inherited unknowns.')
summary=dict(result='passed',static_only=True,windows=len(windows),bytes=sum(e-s for _,s,e in windows),instructions=len(rows),assertions=len(checks),vendor_words=0)
(HERE/'evidence.json').write_text(json.dumps(dict(summary=summary,rom=str(ROM),mapping='offset=VA-0x9ffff000',checks=checks,instructions=rows,range_certificate=certificate),ensure_ascii=False,indent=2)+'\n',encoding='utf8')

terms=['a001b302','__udivdi3','udivdi']
reuse=[]
for rel in ['reverse/reports/ap01/application-rehost-complete-0041-20261017.md','reverse/analysis/0041-20261013/0041-ghidra-pass3.txt']:
    p=ROOT/rel
    reuse.append(dict(path=str(p),hits=[dict(line=i+1,text=l[:200]) for i,l in enumerate(p.read_text(encoding='utf8',errors='replace').splitlines()) if any(t in l.lower() for t in terms)]))
zp=ROOT/'reverse/rehost/ap01-ui-0041-complete-source.zip'
with zipfile.ZipFile(zp) as z:
    members=[n for n in z.namelist() if n.endswith(('.c','.h','.md','.py','.json','.txt'))]
    hits=[]
    for n in members:
        matches=[dict(line=i+1,text=l[:200]) for i,l in enumerate(z.read(n).decode('utf8',errors='replace').splitlines()) if any(t in l.lower() for t in terms)]
        if matches:hits.append(dict(member=n,hits=matches))
(HERE/'reuse.json').write_text(json.dumps(dict(terms=terms,files=reuse,zip=dict(path=str(zp),text_members=len(members),hits=hits),limit='Only these exact tokens and carriers; not proof never analyzed. E16/E17/H15/H16 directly inherited.'),ensure_ascii=False,indent=2)+'\n',encoding='utf8')
print(json.dumps(summary))
