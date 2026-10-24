"""Independent Q01 review: original bytes and retained assembly, static only."""
from pathlib import Path
import json
import capstone

ROOT = Path('D:/Documents/PlatformIO/Projects/cuktech-ap01-firmware')
OUT = Path(__file__).parent
BASE = 0x9ffff000
source = ROOT/'evidence/rea-0041-20261017/evidence/whole-rom-private-20261023.evidence.json'
bundle = json.loads(source.read_text(encoding='utf8'))
records = {}
for proc, eid in [('0xa00adabc','ev_19e11c8fc1582881b289f2b24c2a98bbb305f7c2e57caad784442a60d1fb76e5'),('0xa005cc1e','ev_2f6c46cd278b33760dc15702309279178fd3b14a0bef128e4814088addec2866')]:
    r = next(x for x in bundle['records'] if x.get('parameters',{}).get('procedure') == proc)
    assert r['evidence_id'] == eid
    assert r['analysis_profile']['digest'] == 'b6368dd18431e8113aa5026c713d41e648ab0f6ddd9421ff6c4a49e23b3cd2f3'
    records[proc] = {int(s.split(':')[0],16):s.split(': ',1)[1] for s in r['normalized_result']['assembly']}

md = capstone.Cs(capstone.CS_ARCH_RISCV,capstone.CS_MODE_RISCV32|capstone.CS_MODE_RISCVC)
rows=[]
raws={}
def window(f,lo,hi,proc=None):
    f.seek(lo-BASE)
    data=f.read(hi-lo)
    ins=list(md.disasm(data,lo))
    assert sum(x.size for x in ins)==len(data),(hex(lo),hex(hi))
    if proc:
        assert [x.address for x in ins]==[a for a in records[proc] if lo<=a<hi],(hex(lo),hex(hi))
    for x in ins:
        raws[x.address]=int.from_bytes(x.bytes,'little')
        rows.append({'va':hex(x.address),'raw':x.bytes.hex(),'decoded':x.mnemonic+' '+x.op_str,'retained':records[proc].get(x.address) if proc else None})
    return ins

with (ROOT/'roms/0041/ap01-1.0.2_0041.bin').open('rb') as f:
    assert f.seek(0,2)==6769704
    for lo,hi in [(0xa00adc18,0xa00adc20),(0xa00adcd0,0xa00adce4),(0xa00add16,0xa00add8e),(0xa00adde6,0xa00ade06),(0xa00ade5c,0xa00adf36),(0xa00adfb2,0xa00adff4),(0xa00ae048,0xa00ae070),(0xa00ae11e,0xa00ae166),(0xa00ae43c,0xa00ae44c),(0xa00ae4ee,0xa00ae4f6),(0xa00ae536,0xa00ae55c),(0xa00ae5b4,0xa00ae5c2),(0xa00ae610,0xa00ae632),(0xa00ae672,0xa00ae696),(0xa00ae6ec,0xa00ae6fa),(0xa00ae752,0xa00ae75c),(0xa00ae7e8,0xa00ae80e),(0xa00ae864,0xa00ae86c),(0xa00ae912,0xa00ae926),(0xa00ae990,0xa00ae99a),(0xa00aea26,0xa00aea3c),(0xa00aea68,0xa00aea80),(0xa00aee70,0xa00aee86),(0xa00aef82,0xa00af020)]:
        window(f,lo,hi,'0xa00adabc')
    for lo,hi in [(0xa005d1a2,0xa005d1ae),(0xa005d672,0xa005d686),(0xa005da14,0xa005da1c),(0xa005da4a,0xa005da78)]:
        window(f,lo,hi,'0xa005cc1e')
    helper=window(f,0xa00b2a48,0xa00b2d6a)

def signed(v,n):
    return v-(1<<n) if v>>(n-1) else v
checks=[]
def check(a,kind,actual,expected):
    assert actual==expected,(hex(a),kind,actual,expected)
    checks.append({'va':hex(a),'kind':kind,'expected':expected})
check(0xa005d1a2,'allocation size immediate',raws[0xa005d1a2]>>20,0x10c)
check(0xa005d1aa,'return captured in s2',raws[0xa005d1aa],0x892a)
for a,want in [(0xa00ae062,0x4601),(0xa00ae066,0x4605)]:
    check(a,'boolean argument literal',raws[a],want)
# Independently unpack selected I/S fields. These are semantic anchors, not a full proof.
for a,rd,rs,off,width in [(0xa00adc18,15,18,10,5),(0xa00ae05e,15,8,-224,2),(0xa00adcd4,15,15,21,4),(0xa00adcdc,25,18,14,4),(0xa00add30,15,18,12,4),(0xa00addee,15,18,33,4),(0xa00adeaa,13,15,262,4),(0xa00adeb4,14,18,13,4),(0xa00adf0c,14,18,14,4),(0xa00ae544,14,18,48,2),(0xa00ae548,14,14,8,5),(0xa00ae680,14,18,48,2),(0xa00ae684,14,14,8,5),(0xa00aea68,14,18,48,2),(0xa00aea6c,14,14,8,5),(0xa00af00e,11,9,257,4)]:
    w=raws[a]
    check(a,'load opcode/rd/base/offset/width',[w&127,(w>>7)&31,(w>>15)&31,signed(w>>20,12),(w>>12)&7],[3,rd,rs,off,width])
for a,rs,base,off in [(0xa00adc1c,15,8,-224),(0xa00addfc,15,14,257),(0xa00ade60,25,15,21),(0xa00adec8,14,15,257),(0xa00adecc,0,15,262),(0xa00adf2c,15,14,257),(0xa00ae04a,25,24,21),(0xa00ae15e,15,9,257),(0xa00ae442,15,14,257),(0xa00ae554,14,13,257),(0xa00ae5ba,14,13,257),(0xa00ae68e,15,14,257),(0xa00ae6f2,14,13,257),(0xa00ae806,15,14,257),(0xa00ae868,25,15,21),(0xa00ae918,15,14,257),(0xa00aea34,14,15,262),(0xa00aee82,19,9,257),(0xa00aefd4,19,9,258),(0xa00aefec,24,9,258),(0xa00af004,15,9,258)]:
    w=raws[a]
    check(a,'store fields',[w&127,(w>>20)&31,(w>>15)&31,signed(((w>>25)<<5)|((w>>7)&31),12),(w>>12)&7],[35,rs,base,off,2 if a==0xa00adc1c else 0])
# All selected direct branches/jumps: formula independent of the disassembler.
for a,w in raws.items():
    expected=records.get('0xa00adabc',{}).get(a) or records.get('0xa005cc1e',{}).get(a)
    if expected and w<65536 and w&3==1 and w>>13 in (6,7):
        d=(((w>>12)&1)<<8)|(((w>>10)&3)<<3)|(((w>>5)&3)<<6)|(((w>>3)&3)<<1)|(((w>>2)&1)<<5)
        check(a,'compressed branch target',a+signed(d,9),int(expected.rsplit(' ',1)[1],16))
    if expected and w<65536 and w&3==1 and w>>13==5:
        d=(((w>>12)&1)<<11)|(((w>>11)&1)<<4)|(((w>>9)&3)<<8)|(((w>>8)&1)<<10)|(((w>>7)&1)<<6)|(((w>>6)&1)<<7)|(((w>>3)&7)<<1)|(((w>>2)&1)<<5)
        check(a,'compressed jump target',a+signed(d,12),int(expected.rsplit(' ',1)[1],16))
    if w&127==0x63:
        d=((w>>31)<<12)|(((w>>7)&1)<<11)|(((w>>25)&63)<<5)|(((w>>8)&15)<<1)
        expected=records.get('0xa00adabc',{}).get(a)
        if expected: check(a,'branch target',(a+signed(d,13))&0xffffffff,int(expected.rsplit(' ',1)[1],16))
    if w&127==0x6f:
        d=((w>>31)<<20)|(((w>>12)&255)<<12)|(((w>>20)&1)<<11)|(((w>>21)&1023)<<1)
        expected=records.get('0xa00adabc',{}).get(a) or records.get('0xa005cc1e',{}).get(a)
        if expected: check(a,'JAL target',(a+signed(d,21))&0xffffffff,int(expected.rsplit(' ',1)[1],16))
stores=[]; calls=[]; returns=[]
for x in helper:
    w=int.from_bytes(x.bytes,'little')
    if x.mnemonic in ('sw','sb','sh'):
        assert ((w>>15)&31) in (2,8)
        stores.append(hex(x.address))
    elif x.mnemonic in ('c.sw','c.swsp'):
        assert x.mnemonic=='c.swsp' or 8+((w>>7)&7)==8
        stores.append(hex(x.address))
    if x.mnemonic=='jal':
        d=((w>>31)<<20)|(((w>>12)&255)<<12)|(((w>>20)&1)<<11)|(((w>>21)&1023)<<1)
        target=(x.address+signed(d,21))&0xffffffff
        assert target in (0xa00dfc1e,0xa019d0e6)
        calls.append({'va':hex(x.address),'target':hex(target)})
    if x.mnemonic in ('jalr','c.jalr'): raise AssertionError(x.address)
    if x.mnemonic=='c.jr':
        assert (w>>7)&31==1
        returns.append(hex(x.address))
assert len(stores)==69 and len(calls)==25
boundary_source=ROOT/'evidence/rea-0041-20261017/evidence/whole-rom-paths-20261023.evidence.json'
boundary_bundle=json.loads(boundary_source.read_text(encoding='utf8'))
boundary_record=next(x for x in boundary_bundle['records'] if x['evidence_id']=='ev_50cdbf92a7c9800e4d4bc140d70fa8cd1509eca7a199cfd6050d483cf7d695b2')
entries=[int(x['address'],16) for x in boundary_record['normalized_result'] if x['address'].startswith('0x')]
check(0xa00b2a48,'next retained procedure entry',min(x for x in entries if x>0xa00b2a48),0xa00b2d6a)
result={'source':str(source),'record_procedures':list(records),'profile_digest':'b6368dd18431e8113aa5026c713d41e648ab0f6ddd9421ff6c4a49e23b3cd2f3','capstone':capstone.__version__,'bytes':sum(len(x['raw'])//2 for x in rows),'instructions':len(rows),'checks':checks,'helper':{'bytes':802,'instructions':len(helper),'stack_stores':stores,'direct_calls':calls,'ra_returns':returns,'source':'original ROM + Capstone; retained list_procedures gives entry boundary, not an original REA helper assembly record'},'rows':rows}
(OUT/'review.json').write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n',encoding='utf8')
print(json.dumps({k:result[k] for k in ['bytes','instructions']}),len(checks),'checks; helper',len(stores),'stack stores',len(calls),'direct calls PASS')
