"""Static evidence collection for window transitions and power history."""
import hashlib
import json
from pathlib import Path
from capstone import Cs, CS_ARCH_RISCV, CS_MODE_RISCV32, CS_MODE_RISCVC, cs_version

HERE=Path(__file__).resolve().parent;ROOT=HERE.parents[2];BASE=0x9ffff000
rom=(ROOT/'roms/0041/ap01-1.0.2_0041.bin').read_bytes();sha=lambda b:hashlib.sha256(b).hexdigest()
identity=sha(rom)
assert identity=='972db4c136c7ed9e24a83c07c1a7fd62040ca018b08ca285216d26b1fee3c6b9'
def save(name,obj):
    (HERE/name).write_text(json.dumps(obj,indent=2,ensure_ascii=False)+'\n',encoding='utf-8')

records=[]
for number in [73,146]:
    rel=f'evidence/rea-0041-20261017/evidence/whole-rom-private-20261023-{number:03}.json'
    data=(ROOT/rel).read_bytes();v=json.loads(data);e=v.get('structuredContent') or json.loads(v['content'][0]['text']);n=e['normalized_result'];ranges=[]
    for span in n['procedure']['body']['ranges']:
        a,b=int(span['start'],16),int(span['end'],16)+1;raw=rom[a-BASE:b-BASE]
        ranges.append(dict(start=hex(a),end_exclusive=hex(b),file_offset=a-BASE,hex=raw.hex(),sha256=sha(raw)))
    records.append(dict(source=dict(path=rel,sha256=sha(data)),evidence_id=e['evidence_id'],profile=e['analysis_profile'],normalized_result=n,raw_ranges=ranges))
save('retained-functions.json',dict(rom_sha256=identity,functions=records))

rel='reverse/analysis/buzzer-backlight-0041-20261023.json';data=(ROOT/rel).read_bytes();index=json.loads(data)
f=next(f for f in index['functions'] if f['address']=='0xa00a8582')
save('retained-history-callers.json',dict(source_index=dict(path=rel,sha256=sha(data)),source=f['source'],profile=f['profile'],evidence_id=f['evidence_id'],
     assembly_slices=[x for x in f['assembly'] if any(x.startswith(hex(a)) for a in range(0xa00a8c10,0xa00a8c26,2)) or any(x.startswith(hex(a)) for a in range(0xa00a9298,0xa00a92aa,2))],
     scope='Only total/item history calls: both actual argument loads are LHU, correcting signed casts in old pseudocode. Entire response function remains partial.'))

lang=ROOT/'evidence/rea-0041-20261017/ghidra/Ghidra/Processors/RISCV/data/languages'
inputs={Path(i['path']).name:i for i in f['profile']['parameters']['private_model_inputs']}
model=[]
for name in ['ap01thead2.sinc','ap01thead2.reg.sinc','ap01thead3.slaspec']:
    path=lang/name;data=path.read_bytes();assert sha(data)==inputs[name]['sha256']
    lines=data.decode('utf-8').splitlines()
    if name=='ap01thead2.sinc': selected=[dict(start_line=6503,end_line=6511,text='\n'.join(lines[6502:6511])),dict(start_line=6535,end_line=6542,text='\n'.join(lines[6534:6542]))]
    else:selected=[dict(line=i+1,text=s) for i,s in enumerate(lines) if 'thshift=' in s or '@include' in s]
    model.append(dict(path=path.relative_to(ROOT).as_posix(),sha256=sha(data),matched_prior_profile_input=True,excerpts=selected))
vendor=[]
for address,name in [(0xa00a39b6,'th.srh a1,a5,a3,1'),(0xa00a39e6,'th.lrhu a3,a5,a4,1')]:
    off=address-BASE;raw=rom[off:off+4];word=int.from_bytes(raw,'little')
    assert word&127==11 and (word>>25)&3==1
    vendor.append(dict(address=hex(address),hex=raw.hex(),model_decode=name,rd=(word>>7)&31,rs1=(word>>15)&31,rs2=(word>>20)&31,shift=(word>>25)&3))
save('vendor-memory-model.json',dict(prior_profile=f['profile']['digest'],inputs=model,words=vendor,
     authority='Existing hash-bound private instruction model, not a newly modified decoder or independently executed ISA test'))

md=Cs(CS_ARCH_RISCV,CS_MODE_RISCV32|CS_MODE_RISCVC);windows=[]
for name,a,b in [('window_switch',0xa019d422,0xa019d53a),('window_exec',0xa00b3080,0xa00b30c0),('window_child',0xa00b3036,0xa00b3080),
                 ('window_complete',0xa00ab628,0xa00ab6b0),('power_history',0xa00a398c,0xa00a3a0e),
                 ('total_history_call',0xa00a8c10,0xa00a8c26),('item_history_call',0xa00a9298,0xa00a92aa),('animation_template_init',0xa008df3c,0xa008df84)]:
    raw=rom[a-BASE:b-BASE];pc=a;lines=[]
    while pc<b:
        off=pc-BASE;size=4 if rom[off]&3==3 else 2
        assert pc+size<=b
        i=next(md.disasm(rom[off:off+size],pc),None)
        lines.append(dict(address=hex(pc),hex=rom[off:off+size].hex(),assembly=i.mnemonic+' '+i.op_str if i else '.unknown'+str(size*8)))
        pc+=size
    windows.append(dict(name=name,start=hex(a),end_exclusive=hex(b),file_offset=a-BASE,hex=raw.hex(),sha256=sha(raw),instructions=lines))
save('instruction-windows.json',dict(rom_sha256=identity,engine=cs_version(),windows=windows,
     limitations=['History vendor halfword accesses interpreted using separately retained existing model','Animation field offsets retained without assuming exact upstream struct version']))
save('contracts.json',dict(rom_sha256=identity,status='partial',history=dict(entry='0xa00a398c',bytes=364,samples=180,sample_width=2,max_offset=360,cursor_offset=362,max_slot_offset=363,
     argument='raw word a1; observed callers zero-extend unsigned16 with LHU',store='low16',advance='byte cursor+1 then wrap if>179',
     max='if value>max store max=value_low16 and max_slot=oldcursor; otherwise rescan iff oldcursor==max_slot',
     rescan='setmax0 without resetting max_slot; scan180 halfwords ascending; strict greater updates max and slot; first positive maximum wins ties, all-zero scan retains prior max_slot',
     return_rule='rescan || original_value!=0 || resulting_max!=0',
     embeddings={'total':'snapshot+14, ends at378, outer alloc380','item':'item+60, ends at424, outer stride424'},notify_bit=1024),
     window=dict(entry='0xa019d422',gate='nonnull root; child_count(root)!=0 and target!=root.current34',
     state='previous38=oldcurrent34; current34=target; enabled4c=0',
     positions='old previous set320; outgoing current set0; incoming target set-320',
     descriptor='96B initialized; var@0=root, exec@4=a00b3080, complete@16=a00ab628, userdata@28=root, path@32=a008a93e, raw@36=0,raw@40=80000000,raw@44=320,raw@48=0',
     exec='incoming current x=value-320; outgoing previous x=value',
     complete='enabled4c=1; if current34==7 resume GIF timer when resource+5c nonzero; no direct mask50 access/replay in this callback'),
     unknowns=['all callers of window switching and all field50 writers','animation scheduling/timing field ABI and library provenance','who guarantees another total-info notification after transition','history consumers/plots and actual sampling time interval','complete page teardown and subscription reclamation']))
print(json.dumps(dict(records=len(records),windows=len(windows),history_layout_bytes=364,vendor_words=len(vendor))))
