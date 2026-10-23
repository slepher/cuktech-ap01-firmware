"""Independent H04 static ROM decoding; no firmware execution or H03 imports."""
from pathlib import Path
import json
import capstone

OUT = Path(__file__).resolve().parent
MAIN = Path('D:/Documents/PlatformIO/Projects/cuktech-ap01-firmware')
ROM = (MAIN/'roms/0041/ap01-1.0.2_0041.bin').read_bytes()
BASE = 0x9ffff000
CS = capstone.Cs(capstone.CS_ARCH_RISCV, capstone.CS_MODE_RISCV32 | capstone.CS_MODE_RISCVC)
RANGES = [
 ('assembly',0xa00b14cc,0xa00b15b2), ('install_tail',0xa00b07c4,0xa00b07cc),
 ('key_prefix',0xa00b35ee,0xa00b366a),('key_selection',0xa00b373e,0xa00b37ca),('key_enter',0xa00b37ca,0xa00b3910),
 ('parent_delete',0xa00b1a02,0xa00b1a82),('public_delete',0xa00ded6c,0xa00dee1e),
 ('delete_core',0xa00dcf52,0xa00dd144),('event_dispatch',0xa00d81f8,0xa00d8370),
 ('descriptor_dispatch',0xa008acfa,0xa008adf4),('weather_delete',0xa00b3b26,0xa00b3be6),
 ('dtor_walk',0xa00d7806,0xa00d7832),('base_dtor',0xa00d87d0,0xa00d8860),
 ('window_dtor',0xa00b1df8,0xa00b1e54),('key_getter',0xa00d8af6,0xa00d8b3e),
 ('event_install',0xa01ad654,0xa01ad6d8),('descriptor_store',0xa01b9432,0xa01b943c),
 ('constructor',0xa00b821e,0xa00b8bfc),('factory',0xa00d91c6,0xa00d91de),
 ('child_access',0xa00dcee4,0xa00dcf52),('window_class_argument',0xa00b2f6c,0xa00b2f8c)]

def w(a): return int.from_bytes(ROM[a-BASE:a-BASE+4], 'little')
def signed(v,n): return v-(1<<n) if v>>(n-1) else v
def decode(lo,hi):
    rows=[]
    while lo<hi:
        n=4 if w(lo)&3==3 else 2
        raw=ROM[lo-BASE:lo-BASE+n]
        if n==4 and w(lo)&127==11:
            word=w(lo)
            text=f'vendor rd={(word>>7)&31} rs1={(word>>15)&31} rs2={(word>>20)&31} f3={(word>>12)&7} high25={word>>25} high26={word>>26}'
        else:
            inst=list(CS.disasm(raw,lo,count=1))
            assert len(inst)==1 and inst[0].size==n,hex(lo)
            text=inst[0].mnemonic+' '+inst[0].op_str
            if inst[0].group(capstone.CS_GRP_JUMP) or inst[0].mnemonic in ('jal','c.jal'):
                try: text+=' -> '+hex((lo+int(inst[0].op_str.split(',')[-1].strip(),0))&0xffffffff)
                except ValueError: pass
        rows.append(dict(va=hex(lo),file_offset=lo-BASE,raw=raw.hex(),asm=text.strip()))
        lo+=n
    assert lo==hi
    return rows

CS.detail=True
decoded={name:decode(lo,hi) for name,lo,hi in RANGES}
def retained(name,rows):
    if name!='constructor': return rows
    return [r for r in rows if int(r['va'],16)<0xa00b82b2 or int(r['va'],16)>=0xa00b8bb4 or 's2' in r['asm'] or (len(r['raw'])==8 and int(r['raw'][0:2],16)&127==11 and any((w(int(r['va'],16))>>n)&31==18 for n in (7,15,20)))]
(OUT/'review-disassembly.txt').write_text('\n\n'.join(name+'\n'+'\n'.join(f"{r['va']} {r['raw']:8} {r['asm']}" for r in retained(name,rows)) for name,rows in decoded.items()),encoding='utf-8')

checks=[]
def check(label,got,want):
    assert got==want,(label,got,want)
    checks.append(dict(label=label,value=got))
def jal(at,to):
    x=w(at)
    off=((x>>31)<<20)|(((x>>12)&255)<<12)|(((x>>20)&1)<<11)|(((x>>21)&1023)<<1)
    check('call '+hex(at),(x&127,(x>>7)&31,(at+signed(off,21))&0xffffffff),(0x6f,1,to))
def memory(at,op,f3,reg,base,off):
    x=w(at)
    i=(x>>20) if op==3 else ((x>>25)<<5)|((x>>7)&31)
    r=(x>>7)&31 if op==3 else (x>>20)&31
    check('memory '+hex(at),(x&127,(x>>12)&7,r,(x>>15)&31,signed(i,12)),(op,f3,reg,base,off))
def raw(at,b): check('raw '+hex(at),ROM[at-BASE:at-BASE+len(bytes.fromhex(b))].hex(),b)

# Decisive observations added after reading independent disassembly.
CALLS = {
 0xa00b14dc:0xa00b2f6c,0xa00b14e4:0xa008e362,0xa00b151a:0xa00b821e,
 0xa00b1566:0xa008bc64,0xa00b157e:0xa01ad654,0xa00b158c:0xa01ad654,
 0xa00b159a:0xa01ad654,0xa00b07c4:0xa01ad654,0xa00b3658:0xa00a769a,
 0xa00b3660:0xa00d8af6,0xa00b38d4:0xa01b2086,0xa00b3900:0xa01b2086,
 0xa00b3906:0xa00ded6c,0xa00b1a70:0xa008ae58,0xa00b1a76:0xa008ab8a,
 0xa00dedac:0xa00dcf52,0xa00dcf88:0xa00d831a,0xa00dcfc0:0xa00dcee4,
 0xa00dd000:0xa00d7806,0xa00dd03e:0xa008ab8a,0xa00dd126:0xa008c332,
 0xa00d828a:0xa008acfa,0xa00d82a4:0xa00d81f8,0xa00d82be:0xa008acfa,
 0xa00d8358:0xa00d8234,0xa00b3bca:0xa00b3abe,0xa00b3bd0:0xa008ab8a,
 0xa00d881c:0xa008ab8a,0xa00d8830:0xa008ab8a,0xa00b1e0c:0xa008ae58,
 0xa00b8246:0xa008e362,0xa00b8250:0xa00d7806,0xa00b827a:0xa008e362,
 0xa00b82a6:0xa00d7806,0xa00b82ac:0xa008ab8a,0xa00b8bf4:0xa01ad654,
 0xa01ad6ca:0xa01b93b4,0xa00b2f86:0xa00d76ae}
MEMORY = [
 (0xa00b1534,35,0,15,18,2),(0xa00b1538,35,0,0,18,6),(0xa00b156a,35,2,18,9,16),
 (0xa00b1544,3,2,20,15,4),(0xa00b3654,35,0,14,15,58),
 (0xa00b37f2,3,4,15,9,100),(0xa00b37fc,35,0,0,9,100),(0xa00b3818,3,4,14,18,2),
 (0xa00b1a20,3,2,18,9,16),(0xa00b1a7a,35,2,0,9,16),
 (0xa00dcf52,3,5,15,10,42),(0xa00dcf7c,35,1,15,10,42),(0xa00dcf98,35,1,15,9,42),
 (0xa00dd108,3,5,15,14,48),(0xa00dd112,35,1,15,14,48),(0xa00dd12a,35,2,10,18,0),
 (0xa00d833a,35,2,10,8,-44),(0xa00d833e,35,2,10,8,-40),
 (0xa00d834a,35,2,11,8,-36),(0xa00d834e,35,2,0,8,-32),
 (0xa00d8352,35,2,12,8,-28),(0xa00d8346,35,2,15,8,-24),
 (0xa008ad92,35,2,15,19,12),(0xa008ad9a,3,4,15,19,24),
 (0xa00b3b44,3,2,18,9,16),(0xa00b3b4c,3,2,15,18,4),(0xa00b3bd4,35,2,0,9,16),
 (0xa00b8bde,35,2,15,20,0),(0xa00b8be2,35,2,18,20,4),(0xa00b8be6,35,2,20,9,16)]
RAWS = {
 0xa00b14e2:'2145',0xa00b3666:'631cf50c',0xa00b373e:'d147',0xa00b3740:'6315f508',
 0xa00b37ca:'a947',0xa00b3904:'2685',0xa00b1a56:'4845',0xa00b1a58:'01ed',0xa00b1a74:'4a85',
 0xa00dcf8c:'1de1',0xa00dd03c:'2685',0xa00dd044:'3937',0xa00dd046:'9dbf',
 0xa00d8294:'e315f5fc',0xa00d82ac:'e31955fb',0xa00d82c4:'e31d45f9',
 0xa00d8332:'e19b',0xa00d8356:'e8d4',0xa00d8364:'fcd4',
 0xa008ad90:'4e85',0xa008ad98:'8297',0xa008ad9e:'93f42700',0xa008ada4:'858b',
 0xa00d7818:'a685',0xa00d781a:'8297',0xa00d7822:'9cc0',0xa00d7826:'c537',
 0xa00b3bce:'4a85',0xa00d8818:'8843',0xa00d8826:'8844',0xa00d882e:'8844',
 0xa00b8244:'5145',0xa00b8276:'13054007',0xa00b82aa:'5285',
 0xa00b2f7e:'374556a0',0xa00b2f82:'1305c57f',
 0xa01b9432:'0cc1',0xa01b9438:'90c7',0xa01b943a:'d4c3'}
for at,to in CALLS.items(): jal(at,to)
for args in MEMORY: memory(*args)
for at,b in RAWS.items(): raw(at,b)
def constant(lo,ad,value):
    x,y=w(lo),w(ad)
    check('constant '+hex(lo),(x&127,y&0x707f,(x>>7)&31,(y>>15)&31,((x&0xfffff000)+signed(y>>20,12))&0xffffffff),(55,19,(x>>7)&31,(x>>7)&31,value))
for lo,ad,value in [(0xa00b1558,0xa00b1562,0xa00b59c4),(0xa00b156e,0xa00b1578,0xa00b35ee),
 (0xa00b159e,0xa00b15a8,0xa00b1a02),(0xa00b8bca,0xa00b8bee,0xa00b3b26),
 (0xa00d91d2,0xa00d91d6,0xa0263ef4)]: constant(lo,ad,value)
for at,b in [(0xa00b15a2,'ce86'),(0xa00b155c,'4e86'),(0xa00b155e,'9305803e'),
 (0xa00b38ac,'3ec4'),(0xa00b38fa,'02c4'),(0xa00b3606,'6177'),(0xa00b3608,'7d17')]: raw(at,b)
for at,reg,off in [(0xa00b38ae,15,-36),(0xa00b38b2,17,-38),(0xa00b38bc,15,-37),
 (0xa00b38c0,14,-47),(0xa00b38c4,13,-48),(0xa00b38ca,15,-45),
 (0xa00b38d8,15,-36),(0xa00b38dc,17,-38),(0xa00b38e6,15,-37),
 (0xa00b38ea,14,-47),(0xa00b38ee,13,-48),(0xa00b38f4,15,-45)]: memory(at,3,4,reg,8,off)
memory(0xa00b38b6,3,5,16,8,-40); memory(0xa00b38e0,3,5,16,8,-40)

clears=[]
for at in range(0xa00b3b56,0xa00b3bc6,4):
    x=w(at); off=signed(((x>>25)<<5)|((x>>7)&31),12)
    memory(at,35,2,0,15,off); clears.append(off)
check('clear order',clears,[24,48,64,56,4,12,52,16,68,72,28,32,60,8,36,0,44,40,20,76,80,84,88,92,96,100,104,108])
check('clear set excludes context byte112',sorted(clears),list(range(0,112,4)))

vendor=[]
for at,fields in [(0xa00b3878,(11,1,20,10,15,32)),(0xa008ad78,(11,3,13,15,15,30)),
 (0xa00dcf5c,(11,3,14,14,0,30)),(0xa00dd102,(11,3,10,10,0,30)),
 (0xa00dd0e0,(11,4,12,13,15,34)),(0xa00dd0ee,(11,4,14,10,15,34)),
 (0xa00dd0f2,(11,1,10,10,15,2)),(0xa00dd134,(11,4,14,15,10,34)),
 (0xa00dd138,(11,1,15,15,10,2)),(0xa00dcf48,(11,4,10,15,11,34))]:
    x=w(at); got=(x&127,(x>>12)&7,(x>>7)&31,(x>>15)&31,(x>>20)&31,x>>25)
    check('vendor '+hex(at),got,fields)
    vendor.append(dict(va=hex(at),raw=ROM[at-BASE:at-BASE+4].hex(),fields=got,shift=(x>>25)&3))
raw(0xa00d8300,'37a71858'); raw(0xa00d8308,'4517')
check('DELETE bitmap bit19',(0x58189ff1>>19)&1,1)
tables=[]
for at,value in [(0xa0263ef4,0),(0xa0263efc,0xa00d87d0),(0xa05647fc,0xa0263ef4),(0xa0564804,0xa00b1df8)]:
    check('class table '+hex(at),w(at),value)
    tables.append(dict(va=hex(at),raw=ROM[at-BASE:at-BASE+4].hex(),value=hex(value)))
constructor=decoded['constructor']
rootuses=[r for r in retained('constructor',constructor) if 's2' in r['asm'] or (len(r['raw'])==8 and w(int(r['va'],16))&127==11 and any((w(int(r['va'],16))>>n)&31==18 for n in (7,15,20)))]
stores=[r['va'] for r in constructor if len(r['raw'])==8 and w(int(r['va'],16))&127==35 and (w(int(r['va'],16))>>20)&31==18]
check('bounded constructor ordinary SW of root register',stores,['0xa00b8be2'])
check('bounded constructor direct compressed arg move of s2',[r['va'] for r in constructor if r['asm'].startswith('c.mv a') and r['asm'].endswith(', s2')],[])
model=MAIN/'evidence/rea-0041-20261017/ghidra/Ghidra/Processors/RISCV/data/languages/ap01thead2.sinc'
lines=model.read_text().splitlines(); rules=[]
for name in [':th.mveqz rd,rs1,rs2',':th.extu rd,rs1,15,15',':th.extu rd,rs1,15,0',':th.lrw rd,rs1,rs2,thshift',':th.addsl rd,rs1,rs2,thshift']:
    idx=[i for i,s in enumerate(lines) if s.startswith(name+' ')]
    check('one rule '+name,len(idx),1)
    i=idx[0]; rules.append(dict(path=str(model),line=i+1,rule='\n'.join(lines[i:i+9])))

result=dict(scope='H04 independent static review; no target execution',rom=str(MAIN/'roms/0041/ap01-1.0.2_0041.bin'),mapping='offset=VA-0x9ffff000',
 decode_ranges=[dict(name=name,start=hex(lo),end_exclusive=hex(hi),instructions=len(decoded[name])) for name,lo,hi in RANGES],checks=checks,
 vendor=vendor,class_tables=tables,model_rules=rules,constructor_root_uses=rootuses,
 limits='Direct root register references within full constructor only; derived ctx+0x54 and opaque callees are not exhaustively followed. No global alias or heap lifetime claim.')
(OUT/'review-evidence.json').write_text(json.dumps(result,ensure_ascii=False,indent=2),encoding='utf-8')
print(json.dumps(dict(passed=True,instructions=sum(map(len,decoded.values())),checks=len(checks))))
