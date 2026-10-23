"""A26 independent sparse review; original-byte rereads, no new functional recovery."""
from pathlib import Path
import json
import capstone
OUT=Path(__file__).resolve().parent
ROM=Path("D:/Documents/PlatformIO/Projects/cuktech-ap01-firmware/roms/0041/ap01-1.0.2_0041.bin")
b=ROM.read_bytes()
md=capstone.Cs(capstone.CS_ARCH_RISCV,capstone.CS_MODE_RISCV32|capstone.CS_MODE_RISCVC)
rows={}; checks=[]
def signed(x,n):return x-(1<<n) if x>>(n-1) else x
def inst(a):
    o=a-0x9ffff000; n=4 if b[o]&3==3 else 2
    i=next(md.disasm(b[o:o+n],a),None); assert i and i.size==n
    rows[a]={"va":hex(a),"offset":hex(o),"raw":i.bytes.hex(),"instruction":i.mnemonic+" "+i.op_str}
    return i
def ck(label,v,w):
    assert v==w,(label,v,w)
    checks.append({"claim":label,"actual":v,"expected":w})
def instruction(a,text):
    i=inst(a);ck(hex(a)+" decoded original",i.mnemonic+" "+i.op_str,text)
def jal(a,target):
    i=inst(a);x=int.from_bytes(i.bytes,"little");ck(hex(a)+" JAL opcode",x&127,111)
    q=((x>>31)<<20)|(((x>>12)&255)<<12)|(((x>>20)&1)<<11)|(((x>>21)&1023)<<1)
    ck(hex(a)+" JAL target",(a+signed(q,21))&0xffffffff,target)
# Independent U/I/S symbolic evaluation, retaining only callee-saved values across calls.
r={0:0};stores=[];zero_calls=[]
for start,end in [(0xa008e3c4,0xa008e3d8),(0xa008e3fe,0xa008e4b8)]:
    a=start
    while a<end:
        i=inst(a);x=int.from_bytes(i.bytes,"little");op=x&127
        if i.size==4 and op==55:r[(x>>7)&31]=x&0xfffff000
        elif i.size==4 and op==19 and (x>>12)&7==0:
            base=r.get((x>>15)&31)
            if base is not None:r[(x>>7)&31]=(base+signed(x>>20,12))&0xffffffff
        elif i.mnemonic=='c.li':
            d,v=i.op_str.split(', ');alias={'a1':11,'s8':24,'a5':15};r[alias[d]]=int(v,0)
        elif i.size==4 and op==35 and (x>>12)&7==2:
            base=r.get((x>>15)&31);src=(x>>20)&31
            if base is not None and src in r:
                off=signed(((x>>25)<<5)|((x>>7)&31),12)
                stores.append([hex(a),hex((base+off)&0xffffffff),hex(r[src])])
        elif i.size==4 and op==111:
            zero_calls.append([hex(a),hex(r[10]),r[11]])
            for n in [1,5,6,7,10,11,12,13,14,15,16,17,28,29,30,31]:r.pop(n,None)
        a+=i.size
ck('zero call arguments',zero_calls,[['0xa008e3d0','0x62fc957c',528],['0xa008e42c','0x62fc9644',24],['0xa008e472','0x62fc965c',24],['0xa008e498','0x62fc9674',24]])
expected={0x62fc9644:0xa007fe60,0x62fc9648:0xa007ff40,0x62fc964c:0xa007fe4e,0x62fc965c:0xa007fe60,0x62fc9660:0xa007ff40,0x62fc9664:0xa007fe4e,0x62fc9674:0xa007fe60,0x62fc9678:0xa007ff40,0x62fc967c:0xa007fe4e}
for addr,value in expected.items():ck('actual SW '+hex(addr),[v for _,dst,v in stores if int(dst,16)==addr],[hex(value)])
for a in [0xa008e3d0,0xa008e42c,0xa008e472,0xa008e498]:jal(a,0xa0080d8e)
# Complete tiny callbacks read only; no function export is saved.
for a,z in [(0xa007fe4e,0xa007fe76),(0xa007ff40,0xa007ff54)]:
    while a<z:
        i=inst(a)
        # ABI a1 is never read by any decoded instruction in these callbacks.
        ck(hex(a)+' no cf operand','a1' in i.op_str,False)
        a+=i.size
for a,t in [(0xa007fe54,'c.beqz a0, 6'),(0xa007fe56,'c.addi a0, 3'),(0xa007fe58,'c.andi a0, -4'),(0xa007fe68,'c.addi a0, 3'),(0xa0081daa,'c.li a0, 0x1c'),(0xa008e374,'c.mv s1, a0'),(0xa008e376,'c.beqz a0, 0xa'),(0xa008e378,'lw a1, -0x14(s0)'),(0xa008e384,'c.mv a0, s1'),(0xa0081da8,'c.mv s5, a0'),(0xa0081db0,'c.mv s2, a3'),(0xa0081e16,'lw a5, 0(s5)'),(0xa0081e6c,'c.mv a1, s2'),(0xa0081e6e,'c.jalr a5'),(0xa0081e70,'c.mv s8, a0'),(0xa0081e72,'c.beqz a0, -0x54'),(0xa0081e90,'lui a5, 0x62fc9'),(0xa0081e9c,'lw a4, 0x64c(a5)'),(0xa0081ea0,'c.li a5, 0'),(0xa0081ea2,'c.beqz a4, 8'),(0xa0081ea4,'c.mv a1, s2'),(0xa0081ea6,'c.jalr a4'),(0xa0081ea8,'c.mv a5, a0'),(0xa0081eaa,'c.sw a5, 0x10(s1)'),(0xa0081eac,'sw s8, 0x14(s1)'),(0xa0081eb4,'sw s5, 0x18(s1)'),(0xa0081f72,'lhu a5, 2(a0)'),(0xa0081f76,'c.mv s1, a0'),(0xa0081f78,'c.andi a5, 0x10'),(0xa0081f7a,'c.beqz a5, 0x58'),(0xa0081f7c,'c.lw a5, 0x18(a0)'),(0xa0081f7e,'c.bnez a5, 0x3c'),(0xa0081fba,'c.lw a5, 4(a5)'),(0xa0081fbc,'c.beqz a5, 6'),(0xa0081fbe,'c.lw a0, 0x14(a0)'),(0xa0081fc0,'c.jalr a5'),(0xa0081fc2,'c.mv a0, s1')]:instruction(a,t)
for a,t in [(0xa007fe6a,0xa008aea0),(0xa007ff48,0xa008ab8a),(0xa0081db4,0xa008e362),(0xa008e370,0xa002fcc8),(0xa008e37c,0xa0080d8e),(0xa0081fc4,0xa008ab8a)]:jal(a,t)
# Read exactly the zero-wrapper input/save dependency; its returned pointer stays s1.
instruction(0xa008e36c,'sw a0, -0x14(s0)')
result={'result':'passed','kind':'old conclusion review','new_functional_recovery':0,'checks':len(checks),'unique_instructions':len(rows),'unique_bytes':sum(len(v['raw'])//2 for v in rows.values()),'shared_REA_target_opened':False}
critical={0xa007fe54,0xa007fe56,0xa007fe58,0xa007fe68,0xa007fe6a,0xa007ff48}
anchors=[v for a,v in rows.items() if not (0xa007fe4e<=a<0xa007fe76 or 0xa007ff40<=a<0xa007ff54) or a in critical]
result['retained_anchors']=len(anchors)
(OUT/'review-evidence.json').write_text(json.dumps({'summary':result,'claims':checks,'original_byte_anchors':anchors,'installation_stores':stores,'limitations':['Not a new business recovery; old A25 claims reread independently.','No heap/cache implementation, dynamic slot replacement or non-cf10 size recovery.','No ROM execution, SIM, build, replay, device, network, archive script execution.']},indent=2),encoding='utf8')
print(json.dumps(result))
