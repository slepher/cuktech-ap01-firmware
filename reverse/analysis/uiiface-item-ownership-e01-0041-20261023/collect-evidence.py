"""E01 static evidence: read immutable ROM/retained REA; write only this directory."""
import json
from pathlib import Path
from capstone import Cs, CS_ARCH_RISCV, CS_MODE_RISCV32, CS_MODE_RISCVC

HERE = Path(__file__).resolve().parent
TREE = HERE.parents[2]
ORIGINAL = Path('D:/Documents/PlatformIO/Projects/cuktech-ap01-firmware')
BASE = 0x9ffff000
ROM = (ORIGINAL/'roms/0041/ap01-1.0.2_0041.bin').read_bytes()
MD = Cs(CS_ARCH_RISCV, CS_MODE_RISCV32 | CS_MODE_RISCVC)
REG = 'zero ra sp gp tp t0 t1 t2 s0 s1 a0 a1 a2 a3 a4 a5 a6 a7 s2 s3 s4 s5 s6 s7 s8 s9 s10 s11 t3 t4 t5 t6'.split()

def save(name, value):
    (HERE/name).write_text(json.dumps(value, ensure_ascii=False, indent=2)+'\n', encoding='utf-8')

def retained(number):
    rel = f'evidence/rea-0041-20261017/evidence/whole-rom-private-20261023-{number:03}.json'
    obj = json.loads((ORIGINAL/rel).read_text(encoding='utf-8'))
    e = obj.get('structuredContent') or json.loads(obj['content'][0]['text'])
    n = e['normalized_result']
    facets = ['procedure','pseudocode','assembly','callers','callees','unresolved_calls','referenced_strings','limitations']
    return dict(source=str(ORIGINAL/rel), evidence_id=e['evidence_id'],
                profile=e['analysis_profile'], normalized_result={k:n[k] for k in facets},
                retention_scope='Selected existing dossier facets; full original remains at source. No repeated value-flow/reference inventory.')

consumer = retained(129)
assert consumer['normalized_result']['procedure']['address'] == '0xa00f4740'
save('retained-consumer.json', consumer)
request = retained(48)
save('retained-request.json', request)
response = next(f for f in json.loads((TREE/'reverse/analysis/buzzer-backlight-0041-20261023.json').read_text(encoding='utf-8'))['functions'] if f['address']=='0xa00a8582')
observed = {}
for lines in [response['assembly'], consumer['normalized_result']['assembly'], request['normalized_result']['assembly']]:
    for line in lines:
        addr, asm = line.split(': ', 1)
        observed[int(addr, 16)] = asm

def vendor(word):
    # Explicit field extraction, matched to saved ap01thead2.sinc. Not a model edit.
    if word & 0x7f != 0x0b:
        return None
    rd, rs1, rs2 = [REG[(word >> n) & 31] for n in (7, 15, 20)]
    f3, f7 = (word >> 12) & 7, word >> 25
    if f3 in (2, 3):
        msb, lsb = (word >> 26) & 63, (word >> 20) & 63
        assert lsb <= msb < 32
        return f'th.ext{"u" if f3 == 3 else ""} {rd},{rs1},{msb},{lsb}'
    if f3 == 1 and f7 == 16:
        return f'th.mula {rd},{rs1},{rs2}'
    if f3 == 1 and word >> 27 == 0:
        return f'th.addsl {rd},{rs1},{rs2},{(word >> 25) & 3}'
    if f3 in (4, 5) and word >> 27 == 8:
        return f'th.{"lrw" if f3 == 4 else "srw"} {rd},{rs1},{rs2},{(word >> 25) & 3}'
    if f3 == 4 and word >> 27 == 16:
        return f'th.lrbu {rd},{rs1},{rs2},{(word >> 25) & 3}'
    return None

specs = [
    ('command_dispatch',0xa00a85ac,0xa00a85cc),
    ('command52_lookup_header_dev',0xa00a8616,0xa00a873e),
    ('command52_subtype_dispatch',0xa00a9a8a,0xa00a9ac8),
    ('command52_subtype6',0xa00a9ac8,0xa00a9b3e),
    ('command52_subtype1',0xa00a9b3e,0xa00a9bae),
    ('command52_subtype2',0xa00a9bae,0xa00a9c20),
    ('command52_subtype3',0xa00a9c20,0xa00a9cbc),
    ('command51_fetch_loop',0xa00a93a4,0xa00a9410),
    ('command51_type_ctk_fallback',0xa00a9454,0xa00a947e),
    ('command51_replacement_and_notify',0xa00a9504,0xa00a960a),
    ('command51_other_type_cleanup',0xa00a972a,0xa00a973e),
    ('command50_clear',0xa00a9320,0xa00a937a),
    ('item_cleanup',0xa00a3d80,0xa00a3df4),
    ('borrow_item',0xa00a53c0,0xa00a53ee),
    ('request_pending_remote',0xa00a53ee,0xa00a5498),
    ('dispatch_item',0xa00a389c,0xa00a3904),
    ('compare_bytes',0xa00501be,0xa0050202),
    ('zeroed_alloc',0xa008e362,0xa008e38c),
    ('zero_fill',0xa0080d8e,0xa0080da6),
    ('release_adapter',0xa008ab8a,0xa008abb0),
    ('consumer',0xa00f4740,0xa00f4bf8),
]
windows=[]
for name,start,end in specs:
    pc=start; ins=[]
    while pc<end:
        raw=ROM[pc-BASE:pc-BASE+4]; size=4 if raw[0]&3==3 else 2
        assert pc+size<=end, (name,hex(pc))
        i=next(MD.disasm(raw[:size],pc),None)
        decoded=vendor(int.from_bytes(raw,'little')) if size==4 else None
        ins.append(dict(address=hex(pc), hex=raw[:size].hex(),
                        assembly=decoded or (i.mnemonic+' '+i.op_str if i else '.unknown'),
                        retained_assembly=observed.get(pc)))
        pc+=size
    windows.append(dict(name=name,start=hex(start),end_exclusive=hex(end),file_offset=start-BASE,
                        hex=ROM[start-BASE:end-BASE].hex(),instructions=ins))
save('instruction-windows.json',dict(base=hex(BASE), windows=windows,
    vendor_model_source=str(ORIGINAL/'evidence/rea-0041-20261017/processor/data/languages/ap01thead2.sinc'),
    limits=['Selected static windows; response container is not fully certified.',
            'THead extraction independently records encoded operands; saved local processor semantics are a separate source, not upstream certification.',
            'Unknown vendor instructions remain unknown. No firmware execution.']))
assert vendor(0x2c86b68b) == 'th.extu a3,a3,11,8'
assert vendor(0x1c4b3a8b) == 'th.extu s5,s6,7,4'
strings=[]
for addr in [0xa02697b8,0xa0269810,0xa026986c,0xa02698a8,0xa02698dc,0xa0269934,0xa026a968,0xa059c8b8,0xa059c8f8]:
    start=addr-BASE; raw=ROM[start:ROM.index(0,start)+1]
    strings.append(dict(address=hex(addr),file_offset=start,hex=raw.hex(),text=raw[:-1].decode('utf-8')))
save('resource-strings.json',strings)
print(json.dumps(dict(windows=len(windows),instructions=sum(len(w['instructions']) for w in windows),unknown=[i['address'] for w in windows for i in w['instructions'] if i['assembly']=='.unknown'])))
