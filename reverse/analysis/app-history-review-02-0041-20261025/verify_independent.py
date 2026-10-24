"""Bounded ROM review; standard library only; never imports author verifier."""
import json
from pathlib import Path
from datetime import datetime, timezone

ROOT = Path(__file__).resolve().parents[3]
OUT = Path(__file__).parent
BASE = 0x9ffff000
rom = (ROOT / 'roms/0041/ap01-1.0.2_0041.bin').read_bytes()
assert len(rom) == 6769704
carrier = json.loads((ROOT / 'reverse/analysis/app-history-research-02-0041-20261024/static-evidence.json').read_text())
def raw(a, n): return rom[a-BASE:a-BASE+n]
def word(a): return int.from_bytes(raw(a, 4), 'little')
def sx(x,n): return x-(1<<n) if x>>(n-1) else x
def jal(a):
    w=word(a); assert w&127 == 111
    i=((w>>31)<<20)|(((w>>12)&255)<<12)|(((w>>20)&1)<<11)|(((w>>21)&1023)<<1)
    return (a+sx(i,21))&0xffffffff
def load(a):
    w=word(a); assert w&127==3
    return {'rd':(w>>7)&31,'base':(w>>15)&31,'offset':sx(w>>20,12),'width':(w>>12)&7}
def clw(a):
    w=int.from_bytes(raw(a,2),'little'); assert w&0xe003==0x4000
    return {'rd':8+((w>>2)&7),'base':8+((w>>7)&7),'offset':(((w>>5)&1)<<6)|(((w>>10)&7)<<3)|(((w>>6)&1)<<2)}
matched=0
for win in carrier['windows']:
    cursor=int(win['start'],16)
    for ins in win['instructions']:
        a=int(ins['address'],16); b=bytes.fromhex(ins['bytes'])
        assert a==cursor and raw(a,len(b))==b
        assert len(b)==(4 if b[0]&3==3 else 2)
        cursor+=len(b); matched+=1
    assert cursor==int(win['end_exclusive'],16)
targets={hex(a):hex(jal(a)) for a in [0xa01afda6,0xa00d91da,0xa01b060e,0xa00f1bea,0xa00f1c10,0xa01afdbe]}
assert list(targets.values())==['0xa00d91c6','0xa00d76ae','0xa00f50c2','0xa008ae58','0xa008ab8a','0xa00d7806']
assert raw(0xa01afdac,2).hex()=='2a89'
lui=word(0xa00d91d2); add=word(0xa00d91d6)
assert (lui&127,(lui>>7)&31)==(55,10)
assert (add&0xfffff)==0x50513
klass=((lui&0xfffff000)+sx(add>>20,12))&0xffffffff
assert klass==0xa0263ef4 and word(klass)==0 and word(klass+8)==0xa00d87d0
assert load(0xa00f1bac)==dict(rd=19,base=10,offset=4,width=2)
assert load(0xa00f1bb0)==dict(rd=18,base=19,offset=16,width=2)
assert load(0xa00f1bb8)==dict(rd=9,base=18,offset=4,width=2)
assert clw(0xa00f1bbc)==dict(rd=10,base=9,offset=88)
assert raw(0xa00f1bee,2).hex()=='4a85'
assert raw(0xa01b060c,2).hex()=='2685'
helper=next(w for w in carrier['windows'] if w['name']=='same_P_presentation_helper')
stores=[]; a0loads=[]; calls=[]
for ins in helper['instructions']:
    a=int(ins['address'],16); b=bytes.fromhex(ins['bytes']); w=int.from_bytes(b,'little')
    if len(b)==4:
        if w&127==35:
            base=(w>>15)&31; assert base in (2,8)
            stores.append({'address':hex(a),'base':base,'value':(w>>20)&31})
        if w&127==111: calls.append({'address':hex(a),'target':hex(jal(a))})
        if w&127==3 and (w>>7)&31==10: raise AssertionError('unexpected ordinary a0 load')
    else:
        if w&0xe003==0xc000: raise AssertionError('nonstack compressed store')
        if w&0xe003==0x4000:
            v=clw(a)
            if v['rd']==10:
                assert v['base'] in (9,10)
                a0loads.append({'address':hex(a),**v})
assert {v['offset'] for v in a0loads}=={0,16,20,24,28,32}
assert all(s['value']!=9 for s in stores)
result={'utc':datetime.now(timezone.utc).isoformat(),'identity':'inherited CATALOG SHA256; length checked; no rehash','instruction_bytes_matched':matched,'independent_jal':targets,'class':hex(klass),'class_bytes':raw(klass,16).hex(),'failure_window':raw(0xa01afdb8,10).hex(),'original_target':load(0xa00f1bac),'helper_stack_stores':stores,'helper_a0_field_loads':a0loads,'helper_direct_calls':calls,'limits':'No target/model execution; author JSON only byte carrier. No full-ROM negative search. Old unknown profiles retained.'}
(OUT/'independent-checks.json').write_text(json.dumps(result,indent=2)+'\n')
print(json.dumps({'matched':matched,'targets':targets,'class':hex(klass),'helper_calls':len(calls),'result':'PASS'}))
