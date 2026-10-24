"""Static source, call-target and vendor-word checks; does not execute target/model."""
import json
from pathlib import Path
from datetime import datetime, timezone

ROOT=Path('D:/Documents/PlatformIO/Projects/cuktech-ap01-firmware')
OUT=Path(__file__).resolve().parent
raw=json.loads((OUT/'raw.json').read_text())
rows={int(r['pc'],16):r for x in raw['windows'] for r in x['rows']}
assert sum(w['length'] for w in raw['windows'])==1566
def signed(v,b): return v-(1<<b) if v>>(b-1) else v
def word(pc): return int.from_bytes(bytes.fromhex(rows[pc]['raw']),'little')
calls={0xa01140e6:0xa011c204,0xa01140f0:0xa005f3d8,0xa01140fe:0xa0113f6c,0xa0114108:0xa01b3c8c,0xa0113fae:0xa0058386,0xa0114062:0xa01b406c,0xa011c222:0xa0110984,0xa011c344:0xa011c0da,0xa011c34a:0xa002e14e,0xa01af7d4:0xa0110984,0xa01af958:0xa0113340,0xa01af972:0xa0116ad0}
for pc,target in calls.items():
    w=word(pc);assert w&127==111
    delta=signed(((w>>31)<<20)|(((w>>12)&255)<<12)|(((w>>20)&1)<<11)|(((w>>21)&1023)<<1),21)
    assert (pc+delta)&0xffffffff==target
pairs={0xa01af7bc:0xa002fcc8,0xa01af7e4:0xa005f3d8,0xa01af824:0xa005fa54,0xa01af902:0xa00602e6,0xa01af964:0xa005f3d8,0xa01af980:0xa002e14e,0xa01afa12:0xa006929a,0xa01afa1c:0xa002e14e}
for pc,target in pairs.items():
    w,v=word(pc),word(pc+4);assert w&127==23 and v&127==103
    assert (w>>7)&31==(v>>15)&31
    assert (pc+signed(w&0xfffff000,32)+signed(v>>20,12))&0xfffffffe==target
model=ROOT/'evidence/rea-0041-20261017/ghidra/Ghidra/Processors/RISCV/data/languages/ap01thead2.sinc'
text=model.read_text(); rules={}
for key in [':th.lrw ',':th.srb ',':th.lwia ',':th.mvnez ']:
    p=text.index(key);rules[key]=text[p:text.index('\n}',p)+2]
vendor={0xa0114126:[4,8,21,23,9,2],0xa0114034:[4,8,10,21,9,2],0xa0114044:[4,8,11,21,20,2],0xa0114066:[4,8,10,21,20,2],0xa0114074:[5,0,0,15,10,0],0xa0114078:[4,11,10,22,4,0],0xa011c364:[4,8,11,23,18,2],0xa01af840:[1,8,18,15,15,1],0xa01af9a6:[4,8,11,13,15,2]}
for pc,fields in vendor.items():
    w=word(pc);assert w&127==11
    assert [(w>>12)&7,w>>27,(w>>7)&31,(w>>15)&31,(w>>20)&31,(w>>25)&3]==fields
assert word(0xa01af840)>>25==33
strings={0xa060eb68:'event.%s',0xa01c3280:'id',0xa056c058:'method',0xa01c2488:'params',0xa05658ec:'retry',0xa0627418:'timestamp',0xa059cf1c:'tick'}
with (ROOT/'roms/0041/ap01-1.0.2_0041.bin').open('rb') as f:
    for a,value in strings.items():
        f.seek(a-0x9ffff000); assert f.read(len(value)+1)==value.encode()+b'\0'
for x in raw['windows']:
    assert sum(len(bytes.fromhex(r['raw'])) for r in x['rows'])==x['length']
    assert ''.join(r['raw'] for r in x['rows'])==x['raw']
result={'status':'PASS; author static checks, independent review pending','new_bytes':1566,'windows':4,'instruction_rows':len(rows),'raw_calls':{hex(a):hex(b) for a,b in (calls|pairs).items()},'vendor_fields':{hex(a):b for a,b in vendor.items()},'model_path':str(model),'model_rules':rules,'strings':{hex(a):b for a,b in strings.items()},'first_observed_utc':'2026-10-24 17:19:36 UTC','checked_utc':datetime.now(timezone.utc).isoformat(),'timing_note':'Initial reading before first observed UTC is uninstrumented; interval is not full task duration or active compute time. Tool waits not separately instrumented; no sleep or target execution.','tokens':None}
(OUT/'checks.json').write_text(json.dumps(result,ensure_ascii=False,indent=2),encoding='utf-8')
print('PASS',len(rows),'rows;',len(calls)+len(pairs),'calls;',len(vendor),'vendor words;',len(strings),'strings')
