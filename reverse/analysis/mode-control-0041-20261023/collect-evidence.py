"""Static ROM/evidence materialization; never executes the target."""
import hashlib
import json
from pathlib import Path
from capstone import Cs, CS_ARCH_RISCV, CS_MODE_RISCV32, CS_MODE_RISCVC, cs_version

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
BASE = 0x9ffff000
rom = (ROOT/'roms/0041/ap01-1.0.2_0041.bin').read_bytes()
sha = lambda b: hashlib.sha256(b).hexdigest()
identity = sha(rom)
assert identity == '972db4c136c7ed9e24a83c07c1a7fd62040ca018b08ca285216d26b1fee3c6b9'
def save(name,obj):
    (HERE/name).write_text(json.dumps(obj,indent=2,ensure_ascii=False)+'\n',encoding='utf-8')
def spans(body):
    out=[]
    for s in body['ranges']:
        a,b=int(s['start'],16),int(s['end'],16)+1
        raw=rom[a-BASE:b-BASE]
        out.append(dict(start=hex(a),end_exclusive=hex(b),file_offset=a-BASE,hex=raw.hex(),sha256=sha(raw)))
    return out

retained=[]
for number in [9,145]:
    rel=f'evidence/rea-0041-20261017/evidence/whole-rom-private-20261023-{number:03}.json'
    data=(ROOT/rel).read_bytes();v=json.loads(data)
    e=v.get('structuredContent') or json.loads(v['content'][0]['text'])
    n=e['normalized_result']
    retained.append(dict(source=dict(path=rel,sha256=sha(data)),evidence_id=e['evidence_id'],
                         profile=e['analysis_profile'],normalized_result=n,raw_ranges=spans(n['procedure']['body'])))
save('retained-functions.json',dict(rom_sha256=identity,functions=retained))

rel='reverse/analysis/usb-interface-ota-0041-20261023.json'
data=(ROOT/rel).read_bytes();old=json.loads(data)
fs=[f for f in old['functions'] if f['address'] in ['0xa01951e2','0xa01a4ff8','0xa00ee9ce']]
assert len(fs)==3
save('retained-transport.json',dict(rom_sha256=identity,index=dict(path=rel,sha256=sha(data)),functions=fs,
     scope='Existing command admission, frame builder and first-send contracts reused; no defect replay or expanded input validation.'))

md=Cs(CS_ARCH_RISCV,CS_MODE_RISCV32|CS_MODE_RISCVC);windows=[]
for name,a,b in [('control_change',0xa0195166,0xa01951e2),('command_submit',0xa01951e2,0xa019530a),
                 ('custom_apply',0xa019530a,0xa019537a),('mode_apply',0xa019537a,0xa01953f6),
                 ('custom_param',0xa009cc0c,0xa009cd4e),('power_index',0xa009c100,0xa009c188),
                 ('control_dispatch',0xa00a536c,0xa00a53c0)]:
    raw=rom[a-BASE:b-BASE];pc=a;lines=[]
    while pc<b:
        off=pc-BASE;size=4 if rom[off]&3==3 else 2
        assert pc+size<=b
        i=next(md.disasm(rom[off:off+size],pc),None)
        lines.append(dict(address=hex(pc),hex=rom[off:off+size].hex(),assembly=i.mnemonic+' '+i.op_str if i else '.unknown'+str(size*8)))
        pc+=size
    windows.append(dict(name=name,start=hex(a),end_exclusive=hex(b),file_offset=a-BASE,hex=raw.hex(),sha256=sha(raw),instructions=lines))
save('instruction-windows.json',dict(rom_sha256=identity,engine=cs_version(),windows=windows,
     method='Analyst-selected entries and independently checked return/prologue boundaries, not new provider-defined procedures. Unknown words are retained.'))

ledger_rel='reverse/analysis/whole-rom-coverage-0041-20261023-round1.json'
data=(ROOT/ledger_rel).read_bytes();ledger=json.loads(data)
targets=['0xa019537a','0xa019530a','0xa0195166','0xa00a536c']
save('caller-frontier.json',dict(source=dict(path=ledger_rel,sha256=sha(data)),
     callers={t:[dict(address=f['address'],source_paths=f['source_paths']) for f in ledger['functions'] if t in f.get('direct_calls',{}).get('callees',[])] for t in targets},
     limitation='Existing model direct-call frontier only. Large UI and response callers are not certified by this report.'))

mapping={0:0,15:4,20:6,33:9,45:13,67:17,80:19,100:20,120:21,140:23}
save('contracts.json',dict(rom_sha256=identity,status='partial',authority='static instruction facts plus analyst names',
     power_index=dict(address='0xa009c100',mapping=mapping,other=255),
     custom_param=dict(address='0xa009cc0c',high='input >> 8, not masked to 8 bits before validation',low='input & 255',
                       accept='both map !=255 and high+low <101',fallback='if model@62fc9194==2 and high+low>125 then (80,45), otherwise (67,33)',
                       payload='[3,u8(62fcb000),index(high_selected),index(low_selected)]',record='store original input low16 to62fc9190 after custom_apply'),
     custom_apply=dict(address='0xa019530a',guard='input[0]==3',updates=['62fcb01d=3','62fcb512=3','notify control change','copy input4 to62fcb518'],command=96,length=4),
     mode_apply=dict(address='0xa019537a',updates=['62fcb512=u8(input)','62fcb01d=u8(input)','notify control change'],
                     mode3='custom_apply([3,b000,b001,b002]); second control-change call occurs',other='cmd96 len1 payload pointer62fcb01d',range_guard='none in this helper; known MiIO caller normalizes0..3'),
     control_change=dict(snapshot_pointer='0x62fcb2cc',field7_source='signed byte62fcb514',field8_source='byte62fcb512',change_mask={'field7':2,'field8':4},mask_store='replace u16 snapshot+12, not OR with previous',dispatch='a00a536c'),
     control_dispatch=dict(head='0x62fcb554',first='*(head+4)',callback='node+0',userdata='node+4',call='callback(userdata,current snapshot pointer)',
                           next='*(node + *(u32*)head +4)',on_finish='clear current snapshot+12 halfword',ownership='borrowed snapshot; no allocation/free in dispatcher'),
     transport='descriptor cmd/len/payload@+4; cmd0x60 len1/4; copy synchronously into active or four queued slots, or return without admission; no explicit status contract',
     unknowns=['mode0..2 product names','meaning of b000/b001/b002 and complete device-side execution',
               'control snapshot creation/free and listener registration/removal','all mode callers and response reconciliation',
               'exact open source provenance/version and vendor changes','buzzer normal shutdown and exit acknowledgement consumer']))
print(json.dumps(dict(retained_functions=len(retained),reused_transport=len(fs),windows=len(windows))))
