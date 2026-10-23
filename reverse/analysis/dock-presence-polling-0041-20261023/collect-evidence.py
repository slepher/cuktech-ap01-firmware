"""Static PogoPin/polling recovery and opaque MCU-carrier statistics."""
import collections
import hashlib
import json
import math
from pathlib import Path
from capstone import Cs, CS_ARCH_RISCV, CS_MODE_RISCV32, CS_MODE_RISCVC, cs_version

HERE=Path(__file__).resolve().parent;ROOT=HERE.parents[2];BASE=0x9ffff000
rom=(ROOT/'roms/0041/ap01-1.0.2_0041.bin').read_bytes();sha=lambda b:hashlib.sha256(b).hexdigest();identity=sha(rom)
assert identity=='972db4c136c7ed9e24a83c07c1a7fd62040ca018b08ca285216d26b1fee3c6b9'
def save(name,obj):
    (HERE/name).write_text(json.dumps(obj,indent=2,ensure_ascii=False)+'\n',encoding='utf-8')

records=[]
for number in [37,66]:
    rel=f'evidence/rea-0041-20261017/evidence/whole-rom-private-20261023-{number:03}.json'
    raw=(ROOT/rel).read_bytes();v=json.loads(raw);e=v.get('structuredContent') or json.loads(v['content'][0]['text']);n=e['normalized_result'];ranges=[]
    for s in n['procedure']['body']['ranges']:
        a,b=int(s['start'],16),int(s['end'],16)+1;data=rom[a-BASE:b-BASE]
        ranges.append(dict(start=hex(a),end_exclusive=hex(b),file_offset=a-BASE,hex=data.hex(),sha256=sha(data)))
    records.append(dict(source=dict(path=rel,sha256=sha(raw)),evidence_id=e['evidence_id'],profile=e['analysis_profile'],normalized_result=n,raw_ranges=ranges))
rel='reverse/analysis/usb-interface-ota-0041-20261023.json';raw=(ROOT/rel).read_bytes();prior=json.loads(raw)
cleanup=next(f for f in prior['functions'] if f['address']=='0xa00a3ab6')
save('retained-functions.json',dict(rom_sha256=identity,functions=records,reused_cleanup=dict(index=dict(path=rel,sha256=sha(raw)),function=cleanup)))

rel='reverse/analysis/buzzer-backlight-0041-20261023.json';raw=(ROOT/rel).read_bytes();prior=json.loads(raw)
f=next(f for f in prior['functions'] if f['address']=='0xa005a736')
save('timer-registration-source.json',dict(index=dict(path=rel,sha256=sha(raw)),source=f['source'],profile=f['profile'],evidence_id=f['evidence_id'],
     assembly=[s for s in f['assembly'] if 0xa005ab4c<=int(s.split(':')[0],16)<0xa005ab64],scope='Only 20ms LV timer registration and context storage reviewed'))
model_path=ROOT/'evidence/rea-0041-20261017/ghidra/Ghidra/Processors/RISCV/data/languages/ap01thead2.sinc'
model_raw=model_path.read_bytes();model_lines=model_raw.decode('utf-8').splitlines()
expected=next(i['sha256'] for i in f['profile']['parameters']['private_model_inputs'] if Path(i['path']).name=='ap01thead2.sinc')
assert sha(model_raw)==expected
model_excerpts=[]
for needle in [':th.addsl ',':th.lrbu ']:
    start=next(i for i,s in enumerate(model_lines) if s.startswith(needle));end=next(i for i in range(start+1,len(model_lines)) if model_lines[i]=='}')
    model_excerpts.append(dict(start_line=start+1,end_line=end+1,text='\n'.join(model_lines[start:end+1])))
save('poll-vendor-model.json',dict(source=dict(path=model_path.relative_to(ROOT).as_posix(),sha256=sha(model_raw)),prior_profile=f['profile']['digest'],excerpts=model_excerpts,
     words=[dict(address='0xa0191786',hex=rom[0xa0191786-BASE:0xa019178a-BASE].hex(),decode='th.addsl s1,a1,a5,3'),dict(address='0xa01917a6',hex=rom[0xa01917a6-BASE:0xa01917aa-BASE].hex(),decode='th.lrbu a5,a5,a3,0')]))

md=Cs(CS_ARCH_RISCV,CS_MODE_RISCV32|CS_MODE_RISCVC);windows=[]
for name,a,b in [('id_adc_cb',0xa00a41f2,0xa00a43b0),('timer_cb',0xa00a805a,0xa00a8330),('copy_response',0xa0191652,0xa0191700),
                 ('adc_status_publish',0xa0191700,0xa0191746),('next_poll_command',0xa0191746,0xa01917d0),('usb_state_setter',0xa00a5506,0xa00a5558),
                 ('usb_reset_state',0xa00a5558,0xa00a55ba),('usb_cleanup',0xa00a3ab6,0xa00a3b22),('timer_registration',0xa005ab4c,0xa005ab64)]:
    data=rom[a-BASE:b-BASE];pc=a;lines=[]
    while pc<b:
        off=pc-BASE;size=4 if rom[off]&3==3 else 2;assert pc+size<=b
        i=next(md.disasm(rom[off:off+size],pc),None)
        lines.append(dict(address=hex(pc),hex=rom[off:off+size].hex(),assembly=i.mnemonic+' '+i.op_str if i else '.unknown'+str(size*8)));pc+=size
    windows.append(dict(name=name,start=hex(a),end_exclusive=hex(b),file_offset=a-BASE,hex=data.hex(),sha256=sha(data),instructions=lines))
save('instruction-windows.json',dict(rom_sha256=identity,engine=cs_version(),windows=windows,limitations=['Vendor unknowns retained; only two polling words newly interpreted from existing hash-bound model','No target execution, malformed input replay or safety-check changes']))

data=[]
for ram,size in [(0x62fc4b20,32),(0x62fc4b30,8),(0x62fc4b38,1),(0x62fc4b3c,4)]:
    va=0xa00027d4+(ram-0x62fc2cc0);off=va-BASE;b=rom[off:off+size]
    data.append(dict(ram=hex(ram),rom_address=hex(va),file_offset=off,hex=b.hex(),sha256=sha(b)))
save('poll-initializers.json',dict(rom_sha256=identity,relocation='ROMa00027d4 ->RAM62fc2cc0 startup copy, prior reviewed contract',regions=data,
     groups=[dict(entry='62fc4b20',commands_pointer='62fc4b38',commands=[88],limit=1,period=1,initial_sent=0),dict(entry='62fc4b28',commands_pointer='62fc4b3c',commands=[80,81,87,89],limit=4,period=10,initial_sent=0)],
     controller=dict(address='62fc4b30',group_pointer='62fc4b20',byte4=10,phase=0,count=2,round_done=0)))

rel='reverse/analysis/usb-ota-payloads-0041-20261023.json';raw=(ROOT/rel).read_bytes();old=json.loads(raw);payloads=[]
for x in old['embedded_payloads']:
    off=x['file_offset'];whole=rom[off:off+x['header_and_stream_bytes']];assert sha(whole)==x['sha256'];body=whole[18:];counts=collections.Counter(body);blocks=collections.Counter(body[i:i+16] for i in range(0,len(body),16))
    ent=-sum((n/len(body))*math.log2(n/len(body)) for n in counts.values());longest=run=0
    for byte in body:
        run=run+1 if 32<=byte<127 else 0;longest=max(longest,run)
    payloads.append(dict(target=x['target'],rom_address=x['address'],file_offset=off,header_hex=whole[:18].hex(),whole_sha256=sha(whole),body_file_offset=off+18,body_bytes=len(body),body_sha256=sha(body),prefix64_hex=body[:64].hex(),
                         entropy_bits_per_byte=ent,unique16_blocks=len(blocks),total16_blocks=len(body)//16,max16_block_multiplicity=max(blocks.values()),longest_printable_ascii_run=longest,architecture='unknown',interpretation='opaque MCU-carrier data; entropy and repetition do not prove encryption/compression algorithm'))
save('mcu-carrier-boundaries.json',dict(rom_sha256=identity,source=dict(path=rel,sha256=sha(raw)),payloads=payloads,limits=['No architecture/base/reset entry established','No brute force, decryption or code execution attempted','Existing host OTA contract copies/sends16-byte items; data statistics are not an ISA identification']))

save('contracts.json',dict(rom_sha256=identity,status='partial',timer=dict(entry='a00a805a',period_argument_ms=20,context='timer+0c',phase_offset='context+190',phases={'0':'ioctl IDfd@+64,b01,0','1':'tempfd@+c8','2':'portfd@+12c','3':'USB process and memory log counter','4':'no phase work'},advance='phase+1, if>4 then0'),
     adc=dict(entry='a00a41f2',context='*(handle+0)',fd='context+64',read_max=40,message_stride=5,value_offset=1,mean='uint32 sum wrapping / count, unsigned division',counter='context+c4',presence='context+c5',thresholds={'offline_to_online':'1500..1800 inclusive','stay_online':'1480..1820 inclusive'},confirmations=6,skip='negative poll status/read error, no read bit, no/partial messages, or USB initstate3 do not clear counter',on_disconnect=['presence/counter pair=0','a00a3d22','a00a3ab6']),
     poll=dict(controller='62fc4b30',entry_bytes=8,fields=['commands pointer@0','limit@4','period@5','sent@6','unknown@7'],selection='first group phase%period==0 and sent<limit; phase mismatch writes sent=limit; exhausted matching-phase group leaves sent unchanged; send commands[sent],len0,NULL then sent++',cycle='if controller.done: clear done, bytephase++, clear sent, select next',copy='clear transportstate; set done when no eligible group remains; compare/copy n; if changed activehandler((cmd+0x20)&255,0,NULL)'),
     payload_architecture='unknown; byte statistics retained separately',unknowns=['phase timer actual scheduling latency and sample units','all USB initstate transitions, reconnect and complete cleanup','all poll controller writers and byte4 meaning','ADC hardware/channel configuration','opaque MCU container encoding, architecture and code','complete notification consumers and task teardown']))
print(json.dumps(dict(records=len(records),windows=len(windows),payloads=len(payloads))))
