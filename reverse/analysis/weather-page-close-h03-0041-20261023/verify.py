"""H03 static byte/ABI/order verification. No firmware execution or emulation."""
import json
from pathlib import Path
from rom_inspect import ROM, BASE, MAIN, HERE, decode

checks=[]
def req(label,actual,expected):
    assert actual==expected,(label,actual,expected)
    checks.append(dict(check=label,actual=actual))
def word(at): return int.from_bytes(ROM[at-BASE:at-BASE+4],'little')
def sx(x,n): return x-(1<<n) if x&(1<<(n-1)) else x
def jal(at,dst):
    w=word(at); req('JAL encoding '+hex(at),(w&127,(w>>7)&31),(111,1))
    off=((w>>31)<<20)|(((w>>12)&255)<<12)|(((w>>20)&1)<<11)|(((w>>21)&1023)<<1)
    req('JAL target '+hex(at),(at+sx(off,21))&0xffffffff,dst)
def mem(at,expected):
    w=word(at); op=w&127
    reg=(w>>7)&31 if op==3 else (w>>20)&31
    off=w>>20 if op==3 else ((w>>25)<<5)|((w>>7)&31)
    req('memory op/funct3/reg/base/offset '+hex(at),(op,(w>>12)&7,reg,(w>>15)&31,sx(off,12)),expected)
def raw(at,expected): req('raw '+hex(at),ROM[at-BASE:at-BASE+len(bytes.fromhex(expected))].hex(),expected)
def const(lui,addi,value):
    x,y=word(lui),word(addi)
    req('LUI '+hex(lui),x&127,55)
    req('ADDI '+hex(addi),(y&0x707f,(y>>15)&31),(0x13,(x>>7)&31))
    req('constant '+hex(lui),((x&0xfffff000)+sx(y>>20,12))&0xffffffff,value)

# Inclusive starts, exclusive ends: complete core functions, selected constructor
# and input branch windows. No addresses inferred from guessed function names.
spans=[('parent setup',0xa00b14cc,0xa00b15b2),
 ('parent shared installation tail',0xa00b07c4,0xa00b07cc),
 ('parent DELETE',0xa00b1a02,0xa00b1a82),
 ('input prefix',0xa00b35ee,0xa00b366a),
 ('enter close',0xa00b37ca,0xa00b3910),
 ('key getter',0xa00d8af6,0xa00d8b3e),
 ('public delete',0xa00ded6c,0xa00dee1e),
 ('delete core',0xa00dcf52,0xa00dd144),
 ('event send and dispatch',0xa00d81f8,0xa00d8370),
 ('event list delivery',0xa008acfa,0xa008adf4),
 ('weather DELETE',0xa00b3b26,0xa00b3be6),
 ('weather constructor tail',0xa00b8bb4,0xa00b8bfc),
 ('class destructor walker',0xa00d7806,0xa00d7832),
 ('base destructor',0xa00d87d0,0xa00d8860),
 ('window destructor',0xa00b1df8,0xa00b1e54),
 ('object factory prefix',0xa00d91c6,0xa00d91de),
 ('event add adapter',0xa01ad654,0xa01ad6d8),
 ('event descriptor stores',0xa01b9432,0xa01b943c),
 ('child access',0xa00dcf30,0xa00dcf52)]
decoded={}
for name,lo,hi in spans:
    rows=decode(lo,hi); req('complete decode '+name,all(x['text']!='unknown' for x in rows),True)
    decoded[name]=rows
byaddr={int(x['address'],16):x for rows in decoded.values() for x in rows}

for at,dst in [(0xa00b14dc,0xa00b2f6c),(0xa00b14e4,0xa008e362),
 (0xa00b151a,0xa00b821e),(0xa00b1554,0xa00b564e),(0xa00b1566,0xa008bc64),
 (0xa00b157e,0xa01ad654),(0xa00b158c,0xa01ad654),(0xa00b159a,0xa01ad654),(0xa00b07c4,0xa01ad654),
 (0xa00b1a70,0xa008ae58),(0xa00b1a76,0xa008ab8a),
 (0xa00b3660,0xa00d8af6),(0xa00b38d4,0xa01b2086),(0xa00b3900,0xa01b2086),
 (0xa00b3906,0xa00ded6c),(0xa00dedac,0xa00dcf52),
 (0xa00dcf88,0xa00d831a),(0xa00dcfc0,0xa00dcee4),(0xa00dd000,0xa00d7806),
 (0xa00dd03e,0xa008ab8a),(0xa00dd126,0xa008c332),
 (0xa00d8358,0xa00d8234),(0xa00d828a,0xa008acfa),(0xa00d82a4,0xa00d81f8),
 (0xa00d82be,0xa008acfa),(0xa00b3bca,0xa00b3abe),(0xa00b3bd0,0xa008ab8a),
 (0xa00b8bf4,0xa01ad654),(0xa00d881c,0xa008ab8a),(0xa00d8830,0xa008ab8a),
 (0xa00d91da,0xa00d76ae),(0xa01ad6ca,0xa01b93b4)]: jal(at,dst)

for at,expected in [
 (0xa00b156a,(35,2,18,9,16)),(0xa00b1534,(35,0,15,18,2)),
 (0xa00b1538,(35,0,0,18,6)),(0xa00b1544,(3,2,20,15,4)),
 (0xa00b1a20,(3,2,18,9,16)),(0xa00b1a7a,(35,2,0,9,16)),
 (0xa00b3610,(3,2,18,9,16)),(0xa00b37f2,(3,4,15,9,100)),
 (0xa00b3818,(3,4,14,18,2))]: mem(at,expected)
for at,expected in [
 (0xa00dcf52,(3,5,15,10,42)),(0xa00dcf7c,(35,1,15,10,42)),
 (0xa00dcf98,(35,1,15,9,42)),(0xa00dd108,(3,5,15,14,48)),
 (0xa00dd112,(35,1,15,14,48)),(0xa00dd12a,(35,2,10,18,0)),
 (0xa00d833a,(35,2,10,8,-44)),(0xa00d833e,(35,2,10,8,-40)),
 (0xa00d834a,(35,2,11,8,-36)),(0xa00d834e,(35,2,0,8,-32)),
 (0xa00d8352,(35,2,12,8,-28)),(0xa00d8346,(35,2,15,8,-24)),
 (0xa008ad92,(35,2,15,19,12)),(0xa008ad9a,(3,4,15,19,24)),
 (0xa00b3b44,(3,2,18,9,16)),(0xa00b3b4c,(3,2,15,18,4)),
 (0xa00b3bd4,(35,2,0,9,16)),(0xa00b8be2,(35,2,18,20,4)),
 (0xa00b8be6,(35,2,20,9,16))]: mem(at,expected)

for at,bs in [(0xa00b14e2,'2145'),(0xa00b1532,'e547'),(0xa00b15a4,'13069002'),
 (0xa00b3904,'2685'),(0xa00b1a74,'4a85'),(0xa00dcf80,'0146'),
 (0xa00dcf82,'93059002'),(0xa00dd044,'3937'),
 (0xa00d8278,'83a98700'),(0xa00d8286,'0546'),(0xa00d82b8,'0146'),
 (0xa008ad90,'4e85'),(0xa008ad98,'8297'),(0xa00b3bce,'4a85'),
 (0xa00d7818,'a685'),(0xa00d781a,'8297'),
 (0xa01b9432,'0cc1'),(0xa01b9438,'90c7'),(0xa01b943a,'d4c3'),
 (0xa00d8afe,'1c49'),(0xa00d8b04,'8843')]: raw(at,bs)

for lo,ad,value in [(0xa00b156e,0xa00b1578,0xa00b35ee),
 (0xa00b159e,0xa00b15a8,0xa00b1a02),(0xa00b8bca,0xa00b8bee,0xa00b3b26),
 (0xa00d91d2,0xa00d91d6,0xa0263ef4)]: const(lo,ad,value)

# Vendor words: decode from original byte word and cross-check immutable model.
vendor_checks=[]
for at,expected in [(0xa00b3878,(11,1,20,10,15,32)),
 (0xa008ad78,(11,3,13,15,15,15)),(0xa00dcf5c,(11,3,14,14,0,15)),
 (0xa00dd102,(11,3,10,10,0,15)),
 (0xa00dd0e0,(11,4,12,13,15,34)),(0xa00dd0ee,(11,4,14,10,15,34)),
 (0xa00dcf48,(11,4,10,15,11,34))]:
    w=word(at)
    fields=(w&127,(w>>12)&7,(w>>7)&31,(w>>15)&31,(w>>20)&31,w>>26 if (w>>12)&7==3 else w>>25)
    req('vendor fields '+hex(at),fields,expected)
    vendor_checks.append(dict(address=hex(at),word=hex(w),fields=fields))
req('preprocess bit field',(word(0xa008ad78)>>20)&63,15)
req('DELETE excluded from bubbling bitmap',(0x58189ff1>>(0x29-0x16))&1,1)
raw(0xa00d8300,'37a71858'); raw(0xa00d8308,'4517')
model=MAIN/'evidence/rea-0041-20261017/ghidra/Ghidra/Processors/RISCV/data/languages/ap01thead2.sinc'
lines=model.read_text().splitlines()
need=[':th.mveqz rd,rs1,rs2',':th.extu rd,rs1,15,15',':th.extu rd,rs1,15,0',':th.lrw rd,rs1,rs2,thshift']
rules=[]
for rule in need:
    matches=[i for i,s in enumerate(lines) if s.startswith(rule+' ')]
    req('one model rule '+rule,len(matches),1)
    i=matches[0]; rules.append(dict(source=str(model),line=i+1,text='\n'.join(lines[i:i+7])))

# Context reference boundary: complete constructor, all s2 register uses after
# allocation; include raw fields for vendor words to avoid textual blind spots.
constructor=decode(0xa00b821e,0xa00b8bfc)
rootuses=[x for x in constructor if 's2' in x['text'] or
 (int.from_bytes(bytes.fromhex(x['bytes']),'little')&127==11 and
  any(((int.from_bytes(bytes.fromhex(x['bytes']),'little')>>n)&31)==18 for n in [7,15,20]))]
direct_s2_stores=[x['address'] for x in constructor if len(x['bytes'])==8 and
 (int.from_bytes(bytes.fromhex(x['bytes']),'little')&127)==35 and
 ((int.from_bytes(bytes.fromhex(x['bytes']),'little')>>20)&31)==18]
req('constructor direct persistent SW s2',direct_s2_stores,['0xa00b8be2'])
req('constructor passes no s2 directly as argument',any('c.mv a' in x['text'] and ', s2' in x['text'] for x in constructor),False)

# Weather cleanup contract rechecked at the ownership boundary.
clear=[]
for at in range(0xa00b3b56,0xa00b3bc6,4):
    w=word(at)
    req('ctx clear store '+hex(at),(w&127,(w>>12)&7,(w>>15)&31,(w>>20)&31),(35,2,15,0))
    clear.append(sx(((w>>25)<<5)|((w>>7)&31),12))
req('ctx cleared offsets',sorted(clear),list(range(0,112,4)))

table=[]
for address,expected in [(0xa0263ef4,0),(0xa0263efc,0xa00d87d0),
 (0xa05647fc,0xa0263ef4),(0xa0564804,0xa00b1df8)]:
    req('class pointer '+hex(address),word(address),expected)
    table.append(dict(address=hex(address),bytes=ROM[address-BASE:address-BASE+4].hex(),value=hex(expected)))
strings=[]
for address in [0xa0561fac,0xa05604f0,0xa0560554]:
    off=address-BASE; text=ROM[off:ROM.index(0,off)].decode()
    strings.append(dict(address=hex(address),text=text))

out=dict(scope='H03 static normal enter-key exit; no firmware execution',
 rom=str(MAIN/'roms/0041/ap01-1.0.2_0041.bin'),mapping='file_offset=VA-0x9ffff000',
 decoded_ranges=[dict(name=n,start=hex(lo),end_exclusive=hex(hi),instruction_count=len(decoded[n])) for n,lo,hi in spans],
 instruction_count=sum(map(len,decoded.values())),checks=checks,instructions=decoded,
 vendor_checks=vendor_checks,model_rules=rules,class_pointers=table,strings=strings,
 bounded_context_search=dict(constructor_start='0xa00b821e',end_exclusive='0xa00b8bfc',
 instruction_count=len(constructor),s2_uses=rootuses,
 limit='Direct uses of allocation root s2; derived ctx+0x54 and opaque callees are not a global alias analysis. No absence claim outside selected functions.'))
(HERE/'instruction-evidence.json').write_text(json.dumps(out,ensure_ascii=False,indent=2))
print(json.dumps(dict(passed=True,instructions=out['instruction_count'],checks=len(checks),constructor_reference_instructions=len(constructor))))
