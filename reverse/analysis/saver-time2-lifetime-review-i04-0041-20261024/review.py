"""I04 independent sparse ROM/ABI review; no target/model execution."""
import json
from pathlib import Path
import re

HERE=Path(__file__).resolve().parent
TREE=HERE.parents[2]
MAIN=Path('D:/Documents/PlatformIO/Projects/cuktech-ap01-firmware')
guide=json.loads((MAIN/'reverse/rehost/guide-complete-0041.json').read_text(encoding='utf-8'))
weather=json.loads((MAIN/'reverse/rehost/weather-calendar-complete-0041.json').read_text(encoding='utf-8'))
old=weather['evidence'][22]
assert old['address']=='A00A4DF8' and old['tool']=='local GNU objdump, bounded offline ROM window'
sources={
 'guide#/bounded_local_disassembly/saver_window_asm':guide['bounded_local_disassembly']['saver_window_asm'],
 'guide#/bounded_local_disassembly/saver_time_creator_asm':guide['bounded_local_disassembly']['saver_time_creator_asm'],
 'guide#/bounded_local_disassembly/saver_wake_asm':guide['bounded_local_disassembly']['saver_wake_asm'],
 'weather-calendar#/evidence/22/stdout':old['stdout']}
retained={}
for source,text in sources.items():
    for line in text.splitlines():
        match=re.match(r'^(a[0-9a-f]+):\s+([0-9a-f]{8}|[0-9a-f]{4})\s',line)
        if match:
            raw=int(match[2],16).to_bytes(len(match[2])//2,'little')
            retained[int(match[1],16)]=(raw,source)

def sx(value,bits):
    return value-(1<<bits) if value & (1<<(bits-1)) else value

rows=[]
def word(pc):
    raw,source=retained[pc]
    with (MAIN/'roms/0041/ap01-1.0.2_0041.bin').open('rb') as stream:
        stream.seek(pc-0x9ffff000)
        assert stream.read(len(raw))==raw,hex(pc)
    if not any(row['pc']==hex(pc) for row in rows):
        rows.append({'pc':hex(pc),'raw':raw.hex(),'retained_source':source})
    return int.from_bytes(raw,'little')

for pc,raw in [
    (0xa00a7d52,'5145'),(0xa00a7d58,'aa8c'),(0xa00a7d70,'13058002'),
    (0xa00a7d78,'2a89'),(0xa00a7fb0,'130cf002'),(0xa00a7fbc,'a685'),
    (0xa00a7fd2,'8146'),(0xa00a7fd4,'13069002'),(0xa00a7fdc,'2685'),
    (0xa00a4f82,'1c45'),(0xa00a4f84,'6177'),(0xa00a4f86,'7d17'),
    (0xa00a4f88,'f98f'),(0xa00a4f8a,'13079002'),(0xa00a4f9e,'4441'),
    (0xa00a4fb0,'a685'),(0xa00a4fde,'4a85'),(0xa00a7660,'a945'),
    (0xa00a79ba,'a947'),(0xa00ab8aa,'c547')]:
    assert word(pc)==int.from_bytes(bytes.fromhex(raw),'little'),hex(pc)

memory=[]
def mem(pc,expected):
    w=word(pc)
    assert (w>>12)&7==2
    if w&127==3:
        got=('load',(w>>7)&31,(w>>15)&31,sx(w>>20,12))
    else:
        assert w&127==0x23
        got=('store',(w>>20)&31,(w>>15)&31,sx(((w>>25)<<5)|((w>>7)&31),12))
    assert got==expected,(hex(pc),got,expected)
    memory.append({'pc':hex(pc),'operation':got[0],'value_register':got[1],'base_register':got[2],'offset':got[3]})

clear=[(0xa00a4fb2,0),(0xa00a4fb6,4),(0xa00a4fba,8),(0xa00a4fbe,24),
       (0xa00a4fc2,12),(0xa00a4fc6,16),(0xa00a4fca,20),(0xa00a4fce,28),(0xa00a4fd2,32)]
for pc,offset in clear:
    mem(pc,('store',0,15,offset))
for pc,expected in [
    (0xa00a7fca,('store',18,25,4)),(0xa00a7fce,('store',24,25,0)),
    (0xa00a7fde,('store',25,9,16)),(0xa00a4fa0,('load',18,9,16)),
    (0xa00a4fa8,('load',15,18,4)),(0xa00a4fe4,('store',0,9,16)),
    (0xa00a79c4,('store',15,19,60)),(0xa00a7668,('load',10,8,-20))]:
    mem(pc,expected)

constants=[]
for hi,lo,rd,want in [(0xa00a7fb8,0xa00a7fbe,10,0xa00ab6b0),
                       (0xa00a4fac,0xa00a4fd6,10,0xa00ab6b0),
                       (0xa00a7fc6,0xa00a7fd8,11,0xa00a4f82)]:
    u,i=word(hi),word(lo)
    assert u&127==0x37 and (u>>7)&31==rd
    assert i&0x707f==0x13 and (i>>7)&31==rd and (i>>15)&31==rd
    actual=((u&0xfffff000)+sx(i>>20,12))&0xffffffff
    assert actual==want
    constants.append({'high_pc':hex(hi),'low_pc':hex(lo),'register':rd,'value':hex(actual)})

calls=[]
for pc,want in [(0xa00a7d4a,0xa00d91c6),(0xa00a7d54,0xa008e362),
    (0xa00a7d74,0xa008e362),(0xa00a7fc2,0xa00b3a68),(0xa00a4fda,0xa00b3abe),
    (0xa00a4fe0,0xa008ab8a),(0xa00ab8ba,0xa00a75e6),(0xa00a7658,0xa008184e),
    (0xa00a7662,0xa00a7334),(0xa00a7694,0xa00ded6c)]:
    w=word(pc)
    assert w&0xfff==0xef
    imm=((w>>31)<<20)|(((w>>12)&255)<<12)|(((w>>20)&1)<<11)|(((w>>21)&1023)<<1)
    assert (pc+sx(imm,21))&0xffffffff==want
    calls.append({'pc':hex(pc),'target':hex(want)})
u,i=word(0xa00a7fe2),word(0xa00a7fe6)
assert u&0xfff==0x97 and i&0xfffff==0x80e7
assert (0xa00a7fe2+sx(u&0xfffff000,32)+sx(i>>20,12))&0xfffffffe==0xa01ad654
calls.append({'pc':'0xa00a7fe2','target':'0xa01ad654'})

edges=[]
for pc,want,condition in [(0xa00a4f8e,0xa00a4ff4,(1,15,14)),(0xa00a4fa4,0xa00a4fe8,(0,18,0)),
                 (0xa00a75fc,0xa00a7658,(1,14,15)),(0xa00ab8ac,0xa00ab894,(1,9,15)),
                 (0xa00a7666,0xa00a766e,(6,10)),(0xa00a766c,0xa00a7694,(7,10))]:
    w=word(pc)
    if len(retained[pc][0])==4:
        assert w&127==0x63
        assert ((w>>12)&7,(w>>15)&31,(w>>20)&31)==condition
        imm=((w>>31)<<12)|(((w>>7)&1)<<11)|(((w>>25)&63)<<5)|(((w>>8)&15)<<1)
        target=pc+sx(imm,13)
    else:
        assert w>>13 in [6,7]
        assert (w>>13,8+((w>>7)&7))==condition
        imm=(((w>>12)&1)<<8)|(((w>>10)&3)<<3)|(((w>>5)&3)<<6)|(((w>>3)&3)<<1)|(((w>>2)&1)<<5)
        target=pc+sx(imm,9)
    assert target==want,(hex(pc),hex(target))
    edges.append({'pc':hex(pc),'target':hex(target),'condition_fields':condition})

# Scope check on OLD handler records only; no second full-body export/ROM read.
old_handler=[(pc,int.from_bytes(raw,'little'),len(raw)) for pc,(raw,_) in retained.items() if 0xa00a4f82<=pc<0xa00a4ff6]
assert [pc for pc,w,n in sorted(old_handler) if n==4 and w&127==0x6f]==[0xa00a4fda,0xa00a4fe0]
assert not any((n==4 and w&127==0x67 and (w>>7)&31==1) or
               (n==2 and w&0xf07f==0x9002 and (w>>7)&31!=0) for pc,w,n in old_handler)
assert len(old_handler)==39,len(old_handler)
for name in ['weather-subscriber-a15-0041-20261023.md','weather-subscriber-review-a16-0041-20261023.md']:
    text=(TREE/'reverse/reports/ap01'/name).read_text(encoding='utf-8')
    assert 'a00a7fc2' in text and 'a00ab6b0' in text

result={'task':'I04','result':'PASS','sparse_instructions':rows,'memory_fields':memory,
        'address_constants':constants,'call_targets':calls,'control_edges':edges,
        'clear_offsets_in_order':[offset for _,offset in clear],
        'old_handler_only_call_sites':['0xa00a4fda','0xa00a4fe0'],
        'limits':['No complete function/window export or new REA target/model execution.',
                  'Only M20 is the observed direct free argument; C40 final ownership remains unknown.',
                  'Wake kind10 lookup may delete a matched object; runtime identity with this R is not established.',
                  'Weather unregister/common recursive delete interfaces inherited; no cross-type context-free inference.']}
(HERE/'review.json').write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
print(f'PASS: {len(rows)} sparse instructions, {len(calls)} calls, {len(edges)} edges, nine ctx clears; old coverage accepted.')
