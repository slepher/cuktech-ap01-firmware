"""NR01 independent bounded offline decode. Does not import/run N01 verifier."""
from pathlib import Path
import json
from capstone import Cs, CS_ARCH_RISCV, CS_MODE_RISCV32, CS_MODE_RISCVC

ROOT = Path('D:/Documents/PlatformIO/Projects/cuktech-ap01-firmware')
OUT = Path(__file__).resolve().parent
BASE = 0x9ffff000
image = (ROOT / 'roms/0041/ap01-1.0.2_0041.bin').read_bytes()
assert len(image) == 6769704
retained = json.loads((ROOT / 'reverse/analysis/uart-response-0041-20261023.json').read_text(encoding='utf-8'))
decoder = Cs(CS_ARCH_RISCV, CS_MODE_RISCV32 | CS_MODE_RISCVC)
windows = [
 ('query',0xa00a4158,0xa00a417c), ('control16',0xa00a417c,0xa00a41ba),
 ('ack_copy',0xa01ad024,0xa01ad04a),
 ('dispatch_entry',0xa00a8582,0xa00a85c0),
 ('route_60',0xa00a873e,0xa00a874e), ('ack60',0xa00a8794,0xa00a87d2),
 ('report57',0xa00a983e,0xa00a98d0), ('report5e',0xa00a99f0,0xa00a9a8a),
 ('ack62_61',0xa00a9cbc,0xa00a9d06),
 ('common_submit',0xa00a882c,0xa00a8836), ('selector_tail',0xa00a8aae,0xa00a8ab4),
 ('submit',0xa01951e2,0xa019530a), ('control_change',0xa0195166,0xa01951e2),
 ('control_dispatch',0xa00a536c,0xa00a53c0),
 ('custom_apply',0xa019530a,0xa019537a), ('mode_apply',0xa019537a,0xa01953f6),
 ('cache',0xa0191652,0xa0191700), ('retry',0xa00eea08,0xa00eea82),
 ('reset_modes',0xa00a5558,0xa00a55ba), ('cleanup_stage',0xa00a3ab6,0xa00a3b22),
]
records=[]
for name,start,end in windows:
    pc=start; rows=[]
    while pc<end:
        off=pc-BASE; half=int.from_bytes(image[off:off+2],'little')
        size=4 if half&3==3 else 2
        raw=image[off:off+size]
        decoded=list(decoder.disasm(raw,pc))
        row={'pc':hex(pc),'offset':off,'raw':raw.hex(),'asm':decoded[0].mnemonic+' '+decoded[0].op_str if len(decoded)==1 and decoded[0].size==size else 'UNDECODED'}
        if 0xa00a8582<=pc<0xa00a9d1e or 0xa0191652<=pc<0xa0191700:
            f=retained['functions'][0 if pc<0xa0190000 else 1]
            matches=[b for b in f['raw_ranges'] if int(b['start'],16)<=pc and pc+size-1<=int(b['end'],16)]
            assert len(matches)==1,hex(pc)
            b=matches[0]; pos=pc-int(b['start'],16)
            assert bytes.fromhex(b['hex'])[pos:pos+size]==raw,hex(pc)
            row['retained_match']=True
        rows.append(row);pc+=size
    assert pc==end, (name,hex(pc),hex(end))
    records.append({'name':name,'start':hex(start),'end_exclusive':hex(end),'rows':rows})
result={'method':'independent bounded ROM decoding, retained raw comparison only; no target execution',
        'source_profile_dispatcher':retained['functions'][0]['profile_digest'],
        'source_profile_cache':retained['functions'][1]['profile_digest'],
        'windows':records,'instruction_count':sum(len(x['rows']) for x in records)}
assert not [r for x in records for r in x['rows'] if r['asm']=='UNDECODED']
calls={0xa00a4170:0xa01951e2,0xa00a41ac:0xa01951e2,
       0xa00a87cc:0xa00a4158,0xa00a9850:0xa0191652,
       0xa00a9878:0xa00a417c,0xa00a987c:0xa00a4158,0xa00a9880:0xa0195166,
       0xa00a98ac:0xa019530a,0xa00a98b2:0xa019537a,0xa00a98ca:0xa00a417c,
       0xa00a99fe:0xa0191652,0xa00a9a7a:0xa00a536c,
       0xa0195332:0xa0195166,0xa019536a:0xa01951e2,
       0xa0195398:0xa0195166,0xa01953ce:0xa019530a,0xa01953f0:0xa01951e2,
       0xa00eea7c:0xa00ee9ce}
def signed(v,bits):
    return v-(1<<bits) if v>>(bits-1) else v
for pc,target in calls.items():
    w=int.from_bytes(image[pc-BASE:pc-BASE+4],'little')
    assert w&127==111
    delta=signed(((w>>31)<<20)|(((w>>12)&255)<<12)|(((w>>20)&1)<<11)|(((w>>21)&1023)<<1),21)
    assert (pc+delta)&0xffffffff==target,(hex(pc),hex(target))
pairs={0xa00a87b6:0xa01ad024,0xa00a9cc6:0xa01ad024,0xa01ad03a:0xa000589c}
for pc,target in pairs.items():
    w=int.from_bytes(image[pc-BASE:pc-BASE+4],'little')
    v=int.from_bytes(image[pc-BASE+4:pc-BASE+8],'little')
    assert w&127==23 and v&127==103 and (w>>7)&31==(v>>15)&31
    assert ((pc+signed(w&0xfffff000,32)+signed(v>>20,12))&0xfffffffe)==target
result['raw_call_targets_checked']={hex(k):hex(v) for k,v in (calls|pairs).items()}
branches={0xa00a4188:0xa00a4190,0xa00a418c:0xa00a41b8,
          0xa00a9860:0xa00a9888,0xa00a988a:0xa00a9880,
          0xa00a989a:0xa00a98b8,0xa00a98a0:0xa00a98b2,
          0xa00a98c4:0xa00a9880,0xa00a9a4a:0xa00a9a82,
          0xa00a9a82:0xa00a9a88,0xa00eea20:0xa00eea5a,
          0xa00eea3a:0xa00eea5a,0xa00eea44:0xa00eea64}
for pc,target in branches.items():
    w=int.from_bytes(image[pc-BASE:pc-BASE+4],'little')
    if w&3==3:
        assert w&127==99
        delta=signed(((w>>31)<<12)|(((w>>7)&1)<<11)|(((w>>25)&63)<<5)|(((w>>8)&15)<<1),13)
    else:
        w &=65535
        assert (w>>13)&7 in (6,7)
        delta=signed((((w>>12)&1)<<8)|(((w>>5)&3)<<6)|(((w>>2)&1)<<5)|(((w>>10)&3)<<3)|(((w>>3)&3)<<1),9)
    assert pc+delta==target,(hex(pc),hex(target))
result['raw_branch_targets_checked']={hex(k):hex(v) for k,v in branches.items()}
author=json.loads((ROOT/'reverse/analysis/mode-interface-n01-0041-20261024/instruction-evidence.json').read_text(encoding='utf-8'))
ours={r['pc']:r for x in records for r in x['rows']}
count=0
for window in author['windows']:
    for row in window['instructions']:
        independent=ours[row['pc']]
        assert independent['raw']==row['hex']
        assert independent['asm']==row['mnemonic']+' '+row['operands']
        count+=1
assert count==184
result['author_rows_independently_matched']=count
(OUT/'independent-decode.json').write_text(json.dumps(result,indent=2)+'\n',encoding='utf-8')
(OUT/'independent-decode.txt').write_text('\n\n'.join(x['name']+'\n'+'\n'.join(r['pc']+' '+r['raw']+' '+r['asm'] for r in x['rows']) for x in records)+'\n',encoding='utf-8')
print(json.dumps({'windows':len(records),'instructions':result['instruction_count'],'retained_byte_matches':sum(bool(r.get('retained_match')) for x in records for r in x['rows'])}))
