"""Independent bounded byte/source review; never imports author validators."""
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
OUT = Path(__file__).resolve().parent
def load(path):
    return json.loads((ROOT / path).read_text(encoding='utf-8'))
def sx(x, bits):
    return x - (1 << bits) if x & (1 << (bits - 1)) else x
rom = (ROOT / 'roms/0041/ap01-1.0.2_0041.bin').read_bytes()
base = 0x9ffff000
p16 = load('reverse/analysis/port-selector-p16-0041-20261024/static-evidence.json')
p17 = load('reverse/analysis/port-response-p17-0041-20261024/static-evidence.json')
bundle = load(p16['sources']['handler']['path'])
handler = next(r for r in bundle['records'] if r['evidence_id'] == p16['sources']['handler']['evidence_id'])
charge = load('reverse/rehost/charge-complete-0041.json')
init = load('reverse/analysis/uiiface-lifecycle-0041-20261023/retained-initializer.json')['function']
sources = {'handler': handler['normalized_result'], 'callback': charge['records'][19],
           'getter_view': charge['records'][7], 'initializer': init}
dispatcher = load('reverse/analysis/buzzer-backlight-0041-20261023.json')['functions'][5]
other = load('reverse/analysis/uart-response-0041-20261023.json')['functions'][0]
results = []
def raw(addr, n):
    return rom[addr-base:addr-base+n]
def word(addr):
    return int.from_bytes(raw(addr, 4), 'little')
def require(ok, label):
    assert ok, label
    results.append(label)
def source_slice(f, start, end):
    f = f.get('normalized_result', f)
    return [s for s in f['assembly'] if start <= int(s.split(':')[0],16) < end]
windows = []
for claim, data in [('P16', p16), ('P17', p17)]:
    for w in data['windows']:
        start, end = int(w['start'],16), int(w['end_exclusive'],16)
        instructions = w['instructions']
        expect = b''.join(bytes.fromhex(i['hex']) for i in instructions)
        require(raw(start,end-start)==expect, claim+':ROM:'+w['name'])
        addr = start
        for i in instructions:
            require(int(i['address'],16)==addr, claim+':boundary:'+i['address'])
            addr += 4 if int.from_bytes(raw(addr,2),'little') & 3 == 3 else 2
        require(addr==end, claim+':end:'+w['name'])
        if claim=='P16':
            require(source_slice(sources[w['source']],start,end)==w['retained_assembly'], 'source:'+w['name'])
        elif w['name']!='ack_copy':
            retained = [i['retained'] for i in instructions]
            for f in [dispatcher,other]:
                require(source_slice(f,start,end)==[i['address']+': '+i['retained'] for i in instructions], 'dispatcher-source:'+w['name'])
                r=next(r for r in f['raw_ranges'] if int(r['start'],16)<=start and int(r['end'],16)>=end-1)
                offset=start-int(r['start'],16)
                require(bytes.fromhex(r['hex'])[offset:offset+end-start]==expect,'dispatcher-raw:'+w['name'])
        windows.append({'claim':claim,'name':w['name'],'start':w['start'],'end_exclusive':w['end_exclusive'],'hex':expect.hex()})
def jal_target(addr):
    w=word(addr)
    imm=((w>>31)<<20)|(((w>>12)&255)<<12)|(((w>>20)&1)<<11)|(((w>>21)&1023)<<1)
    return addr+sx(imm,21)
def branch(addr):
    w=word(addr)
    imm=((w>>31)<<12)|(((w>>7)&1)<<11)|(((w>>25)&63)<<5)|(((w>>8)&15)<<1)
    return ((w>>12)&7,(w>>15)&31,(w>>20)&31,addr+sx(imm,13))
for k,addr in enumerate([0xa00f6e48,0xa00f6ef4,0xa00f6fa0,0xa00f704c],1):
    h=int.from_bytes(raw(addr,2),'little')
    require((h&0xe003)==0x4001 and ((h>>7)&31)==11 and (((h>>2)&31)|((h>>12)&1)<<5)==k,'entry getter k='+str(k))
    require(jal_target(addr+2)==0xa00f3b36,'getter target k='+str(k))
    for delta,rs,offset in [(18,21,4),(26,15,7)]:
        w=word(addr+delta)
        require(w&127==0x23 and (w>>12)&7==0 and (w>>15)&31==9 and (w>>20)&31==rs and (((w>>25)<<5)|((w>>7)&31))==offset,'entry S store '+str(k)+'/'+str(offset))
for addr,rd in [(0xa00f5340,15),(0xa00f5350,14)]:
    w=word(addr)
    require(w&127==11 and (w>>12)&7==3 and (w>>7)&31==rd and (w>>15)&31==15 and (w>>20)&63==4 and (w>>26)&63==5,'custom type fields '+hex(addr))
model=(ROOT/'evidence/rea-0041-20261017/processor/data/languages/ap01thead2.sinc').read_text(encoding='utf-8')
require(':th.extu rd,rs1,5,4' in model and 'local value:4 = rs1 << 26;' in model and 'rd = value >> 30;' in model,'local model reference only')
require(branch(0xa00a85bc)==(6,15,10,0xa00a873e),'route >57')
require(branch(0xa00a874a)==(6,15,10,0xa00a8794),'route >5e')
require(branch(0xa00a8798)==(6,15,10,0xa00a87d2),'route upper 68')
require(branch(0xa00a87a0)==(7,15,10,0xa00a87a8),'route lower 60')
require(jal_target(0xa00a87a4)==0xa00a9cbc,'route shared')
require(branch(0xa00a9cd2)==(0,18,15,0xa00a9cda),'only62 follows')
require(jal_target(0xa00a9cd6)==0xa00a85e4,'63/65 return')
require((0xa00a9cc6+sx(word(0xa00a9cc6)&0xfffff000,32)+sx(word(0xa00a9cca)>>20,12))&0xfffffffe==0xa01ad024,'ack helper target')
require(word(0xa01ad036)==0x2e070823,'state SB zero')
seams=[]
for start,end in [(0xa00f6e28,0xa00f6e44),(0xa00f6ed4,0xa00f6ef0),(0xa00f6f80,0xa00f6f9c),(0xa00f702c,0xa00f7048)]:
    lines=source_slice(handler['normalized_result'],start,end)
    require(jal_target(end-4)==0xa008b51a,'entry seam log target '+hex(start))
    require(len(lines)==8,'entry seam retained coverage '+hex(start))
    seams.append({'start':hex(start),'end_exclusive':hex(end),'hex':raw(start,end-start).hex(),'retained_assembly':lines})
require(len(rom)==6769704,'ROM length')
record={'status':'PASS independent bounded static review','checks':len(results),'windows':windows,'entry_seams':seams,'labels':results,'source_ids':{k:v['evidence_id'] for k,v in p16['sources'].items()},'limits':['No target/model execution','No descriptor-order equality certified','No business success or cache reader inferred','Copy semantics inherited N01/NR01; setter inherited PR14'],'new_business_recovery':0}
(OUT/'review-evidence.json').write_text(json.dumps(record,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
print('PASS',len(results),'checks;',len(windows),'windows;',sum(len(bytes.fromhex(w['hex'])) for w in windows),'bytes')
