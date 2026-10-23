"""Static evidence only; no firmware or UI execution."""
import hashlib
import json
import struct
from pathlib import Path
from capstone import Cs, CS_ARCH_RISCV, CS_MODE_RISCV32, CS_MODE_RISCVC, cs_version

HERE=Path(__file__).resolve().parent;ROOT=HERE.parents[2];BASE=0x9ffff000
rom=(ROOT/'roms/0041/ap01-1.0.2_0041.bin').read_bytes();sha=lambda b:hashlib.sha256(b).hexdigest()
identity=sha(rom)
assert identity=='972db4c136c7ed9e24a83c07c1a7fd62040ca018b08ca285216d26b1fee3c6b9'
def save(name,data):
    (HERE/name).write_text(json.dumps(data,indent=2,ensure_ascii=False)+'\n',encoding='utf-8')
rel='evidence/rea-0041-20261017/evidence/whole-rom-private-20261023-079.json'
data=(ROOT/rel).read_bytes();v=json.loads(data);e=v.get('structuredContent') or json.loads(v['content'][0]['text']);n=e['normalized_result']
assert n['procedure']['address']=='0xa00ad07e'
ranges=[]
for s in n['procedure']['body']['ranges']:
    a,b=int(s['start'],16),int(s['end'],16)+1;raw=rom[a-BASE:b-BASE]
    ranges.append(dict(start=hex(a),end_exclusive=hex(b),file_offset=a-BASE,hex=raw.hex(),sha256=sha(raw)))
save('retained-function.json',dict(rom_sha256=identity,source=dict(path=rel,sha256=sha(data)),evidence_id=e['evidence_id'],
     profile=e['analysis_profile'],normalized_result=n,raw_ranges=ranges))
md=Cs(CS_ARCH_RISCV,CS_MODE_RISCV32|CS_MODE_RISCVC);windows=[]
for name,a,b in [('theme_total_callback',0xa00ad07e,0xa00ad486),('animation_count_query',0xa00891b8,0xa00891e6),
                 ('port_state_word_setter',0xa00a5cae,0xa00a5cea)]:
    raw=rom[a-BASE:b-BASE];pc=a;lines=[]
    while pc<b:
        off=pc-BASE;size=4 if rom[off]&3==3 else 2
        assert pc+size<=b
        i=next(md.disasm(rom[off:off+size],pc),None)
        lines.append(dict(address=hex(pc),hex=rom[off:off+size].hex(),assembly=i.mnemonic+' '+i.op_str if i else '.unknown'+str(size*8)))
        pc+=size
    windows.append(dict(name=name,start=hex(a),end_exclusive=hex(b),file_offset=a-BASE,hex=raw.hex(),sha256=sha(raw),instructions=lines))
save('instruction-windows.json',dict(rom_sha256=identity,engine=cs_version(),windows=windows,
     limitations=['Capstone vendor words remain unknown; retained repaired model is separate evidence','Decompiler unreachable warnings do not remove original div/rem instructions']))
strings=[]
for a in [0xa01c3bdc,0xa037ad18,0xa037ad2c,0xa059cf34,0xa06136bc,0xa06130bc,0xa026a530,0xa0268c74]:
    off=a-BASE;end=rom.index(b'\0',off);raw=rom[off:end+1]
    strings.append(dict(address=hex(a),file_offset=off,hex_with_nul=raw.hex(),sha256=sha(raw),text=raw[:-1].decode('utf-8')))
a=0xa0254e74;raw=rom[a-BASE:a-BASE+16]
rel='reverse/analysis/ui-total-consumers-0041-20261023/mode-labels.json';data=(ROOT/rel).read_bytes()
save('resources.json',dict(rom_sha256=identity,strings=strings,mode_image_table=dict(address=hex(a),file_offset=a-BASE,hex=raw.hex(),sha256=sha(raw),pointers=[hex(x) for x in struct.unpack('<4I',raw)]),
     mode_labels_source=dict(path=rel,sha256=sha(data)),scope='Image pointers and exact strings only; image/font/rendering formats not certified'))
save('contracts.json',dict(rom_sha256=identity,status='partial',callback='0xa00ad07e',registration='a005d138 -> a01b29a0(callback,userdata=s4)',
     root_fields={'0x4c':'u8 render enabled','0x50':'u32 deferred change mask, replaced during animations'},
     order=['log; root/snapshot nonNULL guards','query global animation count; if nonzero deferred=snapshot.mask and return','require word62fc4034!=0','require root.byte4c!=0','cache mode/power/temp; update activity bits','child0 power/mode/temp groups','child3 power/mode groups','clear root.word50 if nonzero'],
     effective_group_guard='(snapshot.u16mask@12 & bit)!=0 OR (root.word50 & bit)!=0; reloaded for each group',
     group_bits={'power':1,'temperature':2,'mode':4},
     port_state_word=dict(address='0x62fc4034',setter='0xa00a5cae',log_name='lv_set_dev_port_num',rule='for i<snapshot.count: bit((i+1)&31) = item[i].byte0d !=0; retain other bits',meaning='packed word, not a pointer or plain port count; bit0 and other users remain unknown'),
     power='u16 snapshot+4; integer quotient/10 and remainder%10; full raw power passed to graph helper twice',
     temperature=dict(source='signed byte snapshot+7',progress='t<=24 ? 0 : trunc_signed(((int8)(t-25))*100/50)',position='trunc_signed(progress*66/100)+8; no clamp observed',
                      labels={'25..64':'Excellent','65..74':'High Performance','75..127':'Power Limitation','-128..24':'no label update'},resources=['0xa0254aa8 for first band','0xa055fc0c for second/third band']),
     unknowns=['who re-invokes callback after animations to apply deferred bits','all root4c/word50 writers and destruction','full power graph and digit/image rendering helpers','mode image/font formats','device-side temperature management and mode algorithms','all port-state word semantics and consumers']))
print(json.dumps(dict(windows=len(windows),strings=len(strings),callback=n['procedure']['address'])))
