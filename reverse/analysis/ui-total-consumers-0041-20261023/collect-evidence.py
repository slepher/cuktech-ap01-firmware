"""Materialize retained static UI-consumer evidence; no target execution."""
import hashlib
import json
import struct
from pathlib import Path
from capstone import Cs, CS_ARCH_RISCV, CS_MODE_RISCV32, CS_MODE_RISCVC, cs_version

HERE=Path(__file__).resolve().parent
ROOT=HERE.parents[2]
BASE=0x9ffff000
rom=(ROOT/'roms/0041/ap01-1.0.2_0041.bin').read_bytes()
h=lambda b:hashlib.sha256(b).hexdigest()
identity=h(rom)
assert identity=='972db4c136c7ed9e24a83c07c1a7fd62040ca018b08ca285216d26b1fee3c6b9'
def save(name,x):
    (HERE/name).write_text(json.dumps(x,indent=2,ensure_ascii=False)+'\n',encoding='utf-8')

records=[]
for number in [57,77,121]:
    rel=f'evidence/rea-0041-20261017/evidence/whole-rom-private-20261023-{number:03}.json'
    data=(ROOT/rel).read_bytes();v=json.loads(data)
    e=v.get('structuredContent') or json.loads(v['content'][0]['text']);n=e['normalized_result'];ranges=[]
    for s in n['procedure']['body']['ranges']:
        a,b=int(s['start'],16),int(s['end'],16)+1;raw=rom[a-BASE:b-BASE]
        ranges.append(dict(start=hex(a),end_exclusive=hex(b),file_offset=a-BASE,hex=raw.hex(),sha256=h(raw)))
    records.append(dict(source=dict(path=rel,sha256=h(data)),evidence_id=e['evidence_id'],profile=e['analysis_profile'],normalized_result=n,raw_ranges=ranges))
save('retained-functions.json',dict(rom_sha256=identity,functions=records))

md=Cs(CS_ARCH_RISCV,CS_MODE_RISCV32|CS_MODE_RISCVC);windows=[]
for name,a,b in [('screensaver_total_cb',0xa00ac54e,0xa00ac6f8),('power_detail_total_cb',0xa00f3952,0xa00f3b36),
                 ('page_lookup',0xa00a72ae,0xa00a7334),('mode_getter_with_null_tail',0xa00a5c50,0xa00a5c94),
                 ('child_count_nonnull_tail',0xa00dd190,0xa00dd19c),('child_count_entry',0xa00dd144,0xa00dd146),
                 ('activity_style_helper',0xa00ac4c2,0xa00ac54e)]:
    raw=rom[a-BASE:b-BASE];pc=a;lines=[]
    while pc<b:
        off=pc-BASE;size=4 if rom[off]&3==3 else 2
        assert pc+size<=b
        i=next(md.disasm(rom[off:off+size],pc),None)
        lines.append(dict(address=hex(pc),hex=rom[off:off+size].hex(),assembly=i.mnemonic+' '+i.op_str if i else '.unknown'+str(size*8)))
        pc+=size
    windows.append(dict(name=name,start=hex(a),end_exclusive=hex(b),file_offset=a-BASE,hex=raw.hex(),sha256=h(raw),instructions=lines))
save('instruction-windows.json',dict(rom_sha256=identity,engine=cs_version(),windows=windows,
     limitations=['Mode getter null branch at a00a5c58 targets a00a5c60; manual window includes tail despite provider splitting at5c60',
                  'Child-count entry and nonnull tail only; assertion path not reimplemented or executed',
                  'No full downstream UI/rendering lifetime certification']))

table=rom[0xa01c473c-BASE:0xa01c474c-BASE];labels=[]
for i in range(4):
    a=struct.unpack_from('<I',table,4*i)[0];off=a-BASE;raw=rom[off:rom.index(b'\0',off)]
    labels.append(dict(index=i,address=hex(a),file_offset=off,hex=raw.hex(),sha256=h(raw),text=raw.decode('utf-8')))
save('mode-labels.json',dict(rom_sha256=identity,table=dict(address='0xa01c473c',file_offset=0xa01c473c-BASE,hex=table.hex(),sha256=h(table)),labels=labels,
     confidence='Exact ROM strings/pointers and indexed access in power detail callback. UI display names only, not MCU scheduling algorithm.'))
save('contracts.json',dict(rom_sha256=identity,status='partial',screensaver=dict(callback='0xa00ac54e',guard='userdata and snapshot nonNULL; no change-mask test',
     power='u16 snapshot+4 read once; pass raw to page2d helper; display raw/10 unsigned integer on page2f',
     activity='OR of four fixed item+0x0d bytes, stride0x1a8; not snapshot count',
     active='if ctx+24==0 style1 then flag1; always update text and layout',inactive='only if ctx+24==1 style0 then flag0'),
     power_detail=dict(callback='0xa00f3952',guards=['userdata!=0','snapshot!=0','word62fc4034!=0'],
     mask='bit2 checked at entry and again before each of second/third page operations',
     pages={'13':'a00f3844(page_ctx), downstream rendering not fully reviewed','15':'a00f388c(page_ctx,0,snapshot.mode)','19':'a0091b3a(*(ctx+1c),mode_labels[snapshot.mode])'}),
     page_lookup=dict(address='0xa00a72ae',signature='int lookup(root,tag,out_child,out_ctx)',
     count='a00dd144(root), a0 input omitted by old pseudocode',child='a00dcee4(root,i)',tag='*(*(child+10)+0)',ctx='*(*(child+10)+4)',
     outputs='out_child written on every iteration; out_ctx only on match; failure returns0 without general output clearing'),
     mode_getter=dict(address='0xa00a5c50',normal='u8 current global snapshot+8',null='branch into logging tail, return0'),
     mode_labels=[x['text'] for x in labels],unknowns=['full page rendering helpers','page/consumer destruction and subscription removal','device-side mode behavior','exact power unit calibration','all other total-info consumers']))
print(json.dumps(dict(retained=len(records),windows=len(windows),labels=[x['text'] for x in labels]),ensure_ascii=True))
