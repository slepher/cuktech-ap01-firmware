"""P01 sparse static RV32 fields; never executes firmware or input scenarios."""
from pathlib import Path
import json

OUT=Path(__file__).resolve().parent
TREE=OUT.parents[2]
MAIN=Path('D:/Documents/PlatformIO/Projects/cuktech-ap01-firmware')
ROM=(MAIN/'roms/0041/ap01-1.0.2_0041.bin').read_bytes()
BASE=0x9ffff000
records=[]
def sx(x,n): return x-(1<<n) if x&(1<<(n-1)) else x
def word(p,n=4): return int.from_bytes(ROM[p-BASE:p-BASE+n],'little')
def keep(p,n,meaning): records.append(dict(pc=hex(p),raw=ROM[p-BASE:p-BASE+n].hex(),meaning=meaning))
def lui(p,rd,upper):
    w=word(p); assert (w&127,(w>>7)&31,w&0xfffff000)==(0x37,rd,upper)
    keep(p,4,f'LUI x{rd},{upper:x}')
def i(p,op,f3,rd,rs1,imm,meaning):
    w=word(p); assert (w&127,(w>>12)&7,(w>>7)&31,(w>>15)&31,sx(w>>20,12))==(op,f3,rd,rs1,imm)
    keep(p,4,meaning)
def s(p,f3,rs2,rs1,imm,meaning):
    w=word(p); im=((w>>25)<<5)|((w>>7)&31)
    assert (w&127,(w>>12)&7,(w>>20)&31,(w>>15)&31,sx(im,12))==(0x23,f3,rs2,rs1,imm)
    keep(p,4,meaning)
def jal(p,rd,target):
    w=word(p); im=((w>>31)<<20)|(((w>>12)&255)<<12)|(((w>>20)&1)<<11)|(((w>>21)&1023)<<1)
    assert (w&127,(w>>7)&31,p+sx(im,21))==(0x6f,rd,target)
    keep(p,4,f'JAL x{rd},{target:x}')

lui(0xa00afd52,22,0x62fc4000)
i(0xa00afd56,0x13,0,27,22,0x2c,'s11=62fc402c')
w=word(0xa00afd5a,2)
assert (w&3,w>>13,(w>>7)&31,sx(((w>>12)&1)<<5|((w>>2)&31),6))==(1,2,15,1)
keep(0xa00afd5a,2,'C.LI a5,1')
s(0xa00afd5c,0,15,27,14,'SB 1 at global62fc403a')
jal(0xa00afd60,1,0xa00a769a)
lui(0xa00af78a,18,0x62fc4000)
i(0xa00af79a,0x13,0,18,18,0x2c,'s2=62fc402c, separate from app userdata')
i(0xa00afa78,3,4,15,18,14,'LBU activity first time')
lui(0xa00afa7c,9,0x62fcc000)
i(0xa00afa80,0x13,0,9,9,-0x33c,'s1=62fcbcc4')
w=word(0xa00afa8c,2)
im=(((w>>12)&1)<<8)|(((w>>10)&3)<<3)|(((w>>5)&3)<<6)|(((w>>3)&3)<<1)|(((w>>2)&1)<<5)
assert (w&3,w>>13,8+((w>>7)&7),0xa00afa8c+sx(im,9))==(1,6,15,0xa00afb42)
keep(0xa00afa8c,2,'C.BEQZ a5 -> afb42; first zero path skips first clear')
s(0xa00afaa8,2,0,9,0,'SW zero at62fcbcc4')
jal(0xa00afaac,1,0xa008b51a)
i(0xa00afab0,3,4,15,18,14,'LBU activity again after diagnostic call')
lui(0xa00afab4,9,0x62fcc000)
i(0xa00afab8,0x13,0,9,9,-0x338,'s1=62fcbcc8')
w=word(0xa00afabc)
im=((w>>31)<<12)|(((w>>7)&1)<<11)|(((w>>25)&63)<<5)|(((w>>8)&15)<<1)
assert (w&127,(w>>12)&7,(w>>15)&31,(w>>20)&31,0xa00afabc+sx(im,13))==(0x63,0,15,0,0xa00afbec)
keep(0xa00afabc,4,'BEQ a5,zero -> afbec; second zero path skips second clear and byte clear')
s(0xa00afac0,2,0,9,0,'SW zero at62fcbcc8')
s(0xa00afac4,0,0,18,14,'SB zero at62fc403a after second SW')
jal(0xa00afac8,0,0xa00af2a8)

old=json.loads((TREE/'reverse/analysis/screen-host-append-20261020.json').read_text(encoding='utf8'))['functions'][4]
assert old['procedure']=='0xa00af262'
check_order=['0xa00afa78:','0xa00afa8c:','0xa00afaa8:','0xa00afaac:',
             '0xa00afab0:','0xa00afabc:','0xa00afac0:','0xa00afac4:','0xa00afac8:']
positions=[next(i for i,x in enumerate(old['assembly']) if x.startswith(p)) for p in check_order]
assert positions==sorted(positions)
out=dict(status='PASS',baseline='327d557',records=records,record_count=len(records),
    bytes=sum(len(bytes.fromhex(r['raw'])) for r in records),new_functions=0,
    inherited_evidence=old['evidence_id'],inherited_pointer='screen-host-append-20261020.json#/functions/4',
    static_order_checked=check_order,
    limits=['Two actual activity loads remain separate; do not assume value stable across call',
        'No timing/atomicity/concurrency/input-execution claim',
        'No threshold, timer registration, app lifecycle or whole callback verification',
        'No SIM/build/replay/firmware/device/external-service/model execution'])
(OUT/'evidence.json').write_text(json.dumps(out,ensure_ascii=False,indent=2)+'\n',encoding='utf8')
print(json.dumps(dict(status='PASS',records=len(records),bytes=out['bytes'],new_functions=0)))
