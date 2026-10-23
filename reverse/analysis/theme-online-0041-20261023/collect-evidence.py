"""Static collection for theme online-state behavior; no target execution."""
import hashlib
import json
from pathlib import Path
from capstone import Cs, CS_ARCH_RISCV, CS_MODE_RISCV32, CS_MODE_RISCVC, cs_version

HERE=Path(__file__).resolve().parent;ROOT=HERE.parents[2];BASE=0x9ffff000
rom=(ROOT/'roms/0041/ap01-1.0.2_0041.bin').read_bytes();sha=lambda b:hashlib.sha256(b).hexdigest();identity=sha(rom)
assert identity=='972db4c136c7ed9e24a83c07c1a7fd62040ca018b08ca285216d26b1fee3c6b9'
def save(name,obj):
    (HERE/name).write_text(json.dumps(obj,indent=2,ensure_ascii=False)+'\n',encoding='utf-8')
records=[]
for number in [52,58,78]:
    rel=f'evidence/rea-0041-20261017/evidence/whole-rom-private-20261023-{number:03}.json'
    data=(ROOT/rel).read_bytes();v=json.loads(data);e=v.get('structuredContent') or json.loads(v['content'][0]['text']);n=e['normalized_result'];spans=[]
    for span in n['procedure']['body']['ranges']:
        a,b=int(span['start'],16),int(span['end'],16)+1;raw=rom[a-BASE:b-BASE]
        spans.append(dict(start=hex(a),end_exclusive=hex(b),file_offset=a-BASE,hex=raw.hex(),sha256=sha(raw)))
    records.append(dict(source=dict(path=rel,sha256=sha(data)),evidence_id=e['evidence_id'],profile=e['analysis_profile'],normalized_result=n,raw_ranges=spans))
save('retained-functions.json',dict(rom_sha256=identity,functions=records))

md=Cs(CS_ARCH_RISCV,CS_MODE_RISCV32|CS_MODE_RISCVC);windows=[]
for name,a,b in [('theme_online_cb',0xa00ac93c,0xa00ad07e),('ota_flag_query',0xa00a5b5c,0xa00a5b90),
                 ('window_lookup',0xa00a7334,0xa00a73ac),('model_name',0xa00a5498,0xa00a54d2),
                 ('setting_indicator',0xa00fa34e,0xa00fa37e),('setting_version',0xa00fa37e,0xa00fa3b4),
                 ('online_register',0xa01b291a,0xa01b2966),('online_dispatch',0xa00a385a,0xa00a389c),
                 ('app_register',0xa005d14e,0xa005d160)]:
    raw=rom[a-BASE:b-BASE];pc=a;lines=[]
    while pc<b:
        off=pc-BASE;size=4 if rom[off]&3==3 else 2
        assert pc+size<=b,(name,hex(pc))
        i=next(md.disasm(rom[off:off+size],pc),None)
        lines.append(dict(address=hex(pc),hex=rom[off:off+size].hex(),assembly=i.mnemonic+' '+i.op_str if i else '.unknown'+str(size*8)))
        pc+=size
    windows.append(dict(name=name,start=hex(a),end_exclusive=hex(b),file_offset=a-BASE,hex=raw.hex(),sha256=sha(raw),instructions=lines))
save('instruction-windows.json',dict(rom_sha256=identity,engine=cs_version(),windows=windows,
     limitations=['Capstone vendor unknowns remain separate from repaired retained model','Large downstream builders/popups are boundaries, not certified visual implementations']))
strings=[]
for a in [0xa0607610,0xa037aa7c,0xa037aa90,0xa059cf24,0xa0268b40,0xa0268b48,0xa0569848,0xa0569ac8,0xa026a3e4,0xa06130bc,0xa059cf34]:
    off=a-BASE;end=rom.index(b'\0',off);raw=rom[off:end+1]
    strings.append(dict(address=hex(a),file_offset=off,hex_with_nul=raw.hex(),sha256=sha(raw),text=raw[:-1].decode('utf-8')))
save('resources.json',dict(rom_sha256=identity,strings=strings,scope='Exact display/helper names and format strings; no device version inferred from initial display text'))
save('contracts.json',dict(rom_sha256=identity,status='partial',entry='0xa00ac93c',registration=dict(site='0xa005d15c',callback='0xa00ac93c',userdata='s4 root',api='a01b291a',head='62fcb548'),
     states={'1':'set port-state word1; wake;403a=1; maybe switch root index0; four item-field0a indicators; reset child3 text0; update/lazy-build settings',
             '2':'set word1 first; if root4d!=0 return; create special popup, ctx38=1, call(ctx,75,1), rootmeta bytes2=31/1=75,root4d=1,403b=0',
             'other':'set word0; wake;403a=1; delete window tag3 if found; maybe root index3/6; clear power/mode views; settings indicator0; delete child1 of settings container if constructed and clear flag'},
     root_fields={'0x10':'metadata pointer used for byte1/2 special-state writes','0x34':'current child index','0x4d':'special-state latch, not cleared here'},
     settings_page={'tag0x1a':'ctx+8 existing control passed to indicator helper','tag0x1e':'ctx+8 container,ctx+0c upgrade bool,ctx+10 constructed bool'},
     ota_query=dict(address='0xa00a5b5c',behavior='log then explicit return0, no flag read',caller_effect='both positive checks get false under reviewed ROM implementation; preserve caller branches'),
     model_name=dict(address='0xa00a5498',field='u16 62fcb006',mapping={'0x0a01':'TA1208','0x0a02':'TA1408'},other='NULL'),
     version=dict(address='0xa00fa37e',field='u16 62fcb00e',format='当前版本 V%d.%d',arguments=['high byte','low byte'],initial_subtree_text='当前版本 V1.2, not ROM/device version certification'),
     window_lookup=dict(address='0xa00a7334',match='child+0x3c word == tag',outputs='out_window written every iteration, failure does not uniformly clear',root='child_count receives root in a0 despite omitted decompiler argument'),
     deletions=['a00acfcc passes selected window pointer to a00ded6c','a00ad062 obtains child(ctx+8,1), a00ad066 deletes it; then a01ace30(ctx+8); clear ctx10'],
     unknowns=['product reason for state2','all root4d writers/reset and popup lifecycle','full lazy-built subtree rendering/helper semantics','recursive GUI deletion and all subscription teardown','all port-state word writers','actual firmware/version producers and entire OTA admission policy']))
print(json.dumps(dict(records=len(records),windows=len(windows),strings=len(strings))))
