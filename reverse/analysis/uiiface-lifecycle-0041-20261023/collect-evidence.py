"""Read ROM and retained evidence only. No firmware execution."""
import hashlib
import json
from pathlib import Path
from capstone import Cs, CS_ARCH_RISCV, CS_MODE_RISCV32, CS_MODE_RISCVC, cs_version

HERE=Path(__file__).resolve().parent
ROOT=HERE.parents[2]
BASE=0x9ffff000
rom=(ROOT/'roms/0041/ap01-1.0.2_0041.bin').read_bytes()
sha=lambda b:hashlib.sha256(b).hexdigest()
identity=sha(rom)
assert identity=='972db4c136c7ed9e24a83c07c1a7fd62040ca018b08ca285216d26b1fee3c6b9'
def save(name,data):
    (HERE/name).write_text(json.dumps(data,indent=2,ensure_ascii=False)+'\n',encoding='utf-8')

rel='reverse/analysis/buzzer-backlight-0041-20261023.json'
data=(ROOT/rel).read_bytes();index=json.loads(data)
f=next(f for f in index['functions'] if f['address']=='0xa00a8582')
save('retained-initializer.json',dict(rom_sha256=identity,source_index=dict(path=rel,sha256=sha(data)),function=f,
     review_scope='Only UiIFace initialization inside command55 and its allocation/port descriptor tail. Full response function is not certified.'))

records=[]
for number in [27,30,31]:
    rel=f'evidence/rea-0041-20261017/evidence/whole-rom-private-20261023-{number:03}.json'
    data=(ROOT/rel).read_bytes();obj=json.loads(data)
    e=obj.get('structuredContent') or json.loads(obj['content'][0]['text']);n=e['normalized_result']
    spans=[]
    for span in n['procedure']['body']['ranges']:
        a,b=int(span['start'],16),int(span['end'],16)+1;raw=rom[a-BASE:b-BASE]
        spans.append(dict(start=hex(a),end_exclusive=hex(b),file_offset=a-BASE,hex=raw.hex(),sha256=sha(raw)))
    records.append(dict(source=dict(path=rel,sha256=sha(data)),evidence_id=e['evidence_id'],profile=e['analysis_profile'],normalized_result=n,raw_ranges=spans))
save('retained-functions.json',dict(rom_sha256=identity,functions=records))

md=Cs(CS_ARCH_RISCV,CS_MODE_RISCV32|CS_MODE_RISCVC)
specs=[('service_boot',0xa00a55ba,0xa00a56d4),('control_remove',0xa01b2966,0xa01b29a0),
       ('control_register',0xa01b29a0,0xa01b29ec),('list_append',0xa008af14,0xa008af68),
       ('list_unlink',0xa0089d02,0xa0089d76),('list_link_setters',0xa0089cda,0xa0089d02),
       ('zeroed_allocator',0xa008e362,0xa008e3ac),('zero_fill_adapter',0xa0080d8e,0xa0080da6),
       ('free_adapter',0xa008ab8a,0xa008abb0),('online_dispatch',0xa00a385a,0xa00a389c),
       ('snapshot_deinit',0xa00a3d22,0xa00a3d80),('snapshot_allocate',0xa00a8a22,0xa00a8a82),
       ('snapshot_port_init_cold',0xa00a8aca,0xa00a8b50),('test_total_consumer',0xa00a3c48,0xa00a3c8a),
       ('consumer_register_app',0xa005d126,0xa005d13c),('consumer_register_ui',0xa00a79c0,0xa00a79d6),
       ('consumer_register_page',0xa00b075e,0xa00b0774)]
windows=[]
for name,a,b in specs:
    raw=rom[a-BASE:b-BASE];pc=a;lines=[]
    while pc<b:
        off=pc-BASE;size=4 if rom[off]&3==3 else 2
        assert pc+size<=b,(name,hex(pc))
        i=next(md.disasm(rom[off:off+size],pc),None)
        lines.append(dict(address=hex(pc),hex=rom[off:off+size].hex(),assembly=i.mnemonic+' '+i.op_str if i else '.unknown'+str(size*8)))
        pc+=size
    windows.append(dict(name=name,start=hex(a),end_exclusive=hex(b),file_offset=a-BASE,hex=raw.hex(),sha256=sha(raw),instructions=lines))
save('instruction-windows.json',dict(rom_sha256=identity,engine=cs_version(),windows=windows,
     limitations=['Analyst-selected windows; inline init and registration slices do not certify their containing functions',
                  'Generic Capstone unknown vendor words retained; repaired initializer assembly remains a separate source/profile']))

rel='reverse/analysis/whole-rom-coverage-0041-20261023-round1.json';data=(ROOT/rel).read_bytes();ledger=json.loads(data)
targets=['0xa01b29a0','0xa01b2966','0xa00a55ba','0xa00a3d22']
save('caller-frontier.json',dict(source=dict(path=rel,sha256=sha(data)),callers={t:[f['address'] for f in ledger['functions'] if t in f.get('direct_calls',{}).get('callees',[])] for t in targets},
     limitations=['Existing direct-call model only; empty remove callers is not a whole-ROM absence proof']))
save('contracts.json',dict(rom_sha256=identity,status='partial',snapshot=dict(pointer='0x62fcb2cc',allocation_bytes=380,items_stride=424,
     known_fields={'0':'items pointer','4':'u16 total power, test log evidence','6':'u8 item count','7':'signed byte temperature, test log evidence','8':'mode byte','9..11':'not certified by this lifecycle review','12':'u16 change mask'},
     init='command55 inline: deinit first; zeroed alloc380; zeroed items alloc(count*424); item descriptor bits+index; count; helper calls; online notify1',
     deinit='online notify0 first; release items pointer if nonzero; release current global snapshot; clear global; log',nested_item_cleanup='no per-item traversal in deinit; separate CTK nested ownership remains unclosed'),
     control_list=dict(head='0x62fcb554',head_bytes=12,link_offset=8,node_allocation=16,callback_offset=0,userdata_offset=4,next_offset=12,
     link8='other/back link inferred from generic setter/unlink semantics; vendor word decoding not independently certified here',
     register='a01b29a0: callback-only dedup; existing userdata unchanged; new node appended at tail',remove='a01b2966: callback-only lookup; first match unlinked viaa0089d02; no free in this call chain',
     allocation_failure='append returnsNULL; registration still writes fields per original; no extra recovery branch introduced',
     boot='a00a55ba resets heads with offset8,first0,last0 and registers test_total a00a3c48 userdata100',
     consumers=[{'site':'0xa005d138','callback':'0xa00ad07e','userdata':'s4 app context'},{'site':'0xa00a79d2','callback':'0xa00ac54e','userdata':'s3 UI context'},{'site':'0xa00b0770','callback':'0xa00f3952','userdata':'s5 page context'}]),
     allocator='a008e362 malloc then zero-fill; a008e38c returns62fc95e0 for size0 else delegates; free adapter ignoresNULL/static sentinel',
     unknowns=['all snapshot readers/writers and response field semantics','nested per-item ownership and full disconnect cleanup','registration/removal of all consumers and detached node reclamation','all control callback behavior','repeated service init and callback mutation contract','precise upstream source/version and vendor changes']))
print(json.dumps(dict(windows=len(windows),retained_functions=len(records),initializer='0xa00a8582 scoped')))
