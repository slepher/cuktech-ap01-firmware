"""Bounded static evidence extraction; never executes the target firmware."""
import json
import hashlib
from pathlib import Path
from capstone import Cs, CS_ARCH_RISCV, CS_MODE_RISCV32, CS_MODE_RISCVC

SOURCE = Path('D:/Documents/PlatformIO/Projects/cuktech-ap01-firmware')
OUT = Path(__file__).resolve().parent
rom = (SOURCE / 'roms/0041/ap01-1.0.2_0041.bin').read_bytes()
assert len(rom) == 6769704
base = 0x9ffff000
records = []
windows = []
for record, start, size in [('144', 0xa0195034, 176), ('159', 0xa01b5d70, 764), ('021', 0xa00a116e, 354)]:
    path = SOURCE / f'evidence/rea-0041-20261017/evidence/whole-rom-private-20261023-{record}.json'
    j = json.loads(path.read_text(encoding='utf-8-sig'))
    s = j.get('structuredContent')
    if not s:
        s = json.loads(j['content'][0]['text'])['structuredContent']
    r = s['normalized_result']
    assert r['procedure']['body']['total_bytes'] == size
    assert int(r['procedure']['address'], 16) == start
    records.append({'source': str(path), 'pointer': '/structuredContent/normalized_result',
                    'evidence_id': s['evidence_id'], 'analysis_profile': s['analysis_profile'],
                    'procedure': r['procedure'], 'assembly': r['assembly'], 'pseudocode': r['pseudocode']})
    raw = rom[start-base:start-base+size]
    windows.append({'start': hex(start), 'size': size, 'file_offset': start-base,
                    'hex': raw.hex(), 'sha256': hashlib.sha256(raw).hexdigest(), 'kind': 'inherited-body-raw-check'})
md = Cs(CS_ARCH_RISCV, CS_MODE_RISCV32 | CS_MODE_RISCVC)
for start, size in [(0xa01950e4,34),(0xa0195106,28),(0xa0195122,34),(0xa0195144,34)]:
    raw = rom[start-base:start-base+size]
    ins = list(md.disasm(raw, start))
    assert sum(i.size for i in ins) == size
    calls = [i for i in ins if i.mnemonic == 'jal']
    assert len(calls) == 1
    assert calls[0].address + int(calls[0].op_str, 0) == 0xa0195034
    windows.append({'start':hex(start),'size':size,'file_offset':start-base,'hex':raw.hex(),
                    'sha256':hashlib.sha256(raw).hexdigest(),'kind':'new-wrapper-raw',
                    'assembly':[f'{i.address:#x}: {i.bytes.hex()} {i.mnemonic} {i.op_str}' for i in ins]})
strings = []
for start in [0xa06124b8,0xa05656d8,0xa066c284,0xa066c290,0xa066c2cc,0xa066c2d4,0xa066c2dc,0xa066c2e4,0xa0266f78,0xa056580c,0xa0614cb0,0xa0616168,0xa056493c,0xa05652c0,0xa01bd768,0xa01bd484]:
    raw=rom[start-base:start-base+96].split(b'\0')[0]+b'\0'
    strings.append({'start':hex(start),'file_offset':start-base,'hex':raw.hex(),'text':raw[:-1].decode('ascii')})
seed = json.loads((SOURCE/'evidence/rea-0041-20261017/evidence/whole-rom-private-20261023-024.json').read_text(encoding='utf-8-sig'))['structuredContent']
a=seed['normalized_result']['assembly']
seed_lines=[]
for k,line in enumerate(a):
    if '0xa01b5d70' in line or '0xa00a12d0' in line:
        seed_lines.extend(a[max(0,k-4):k+2])
seed_pseudo = seed['normalized_result']['pseudocode'].splitlines()
seed_context = []
for k,line in enumerate(seed_pseudo):
    if 'FUN_ram_a01b5d70(0)' in line:
        seed_context.extend(seed_pseudo[max(0,k-2):k+3])
result={'records':records,'windows':windows,'strings':strings,'seed024':{'evidence_id':seed['evidence_id'],'assembly':seed_lines,'pseudocode_context':seed_context},
        'checks':{'body_bytes':1294,'new_wrapper_bytes':130,'wrapper_direct_targets':True,'static_only':True}}
(OUT/'bounded-evidence.json.tmp').write_text(json.dumps(result,ensure_ascii=False,indent=2),encoding='utf-8')
print(json.dumps({'checks':result['checks'],'strings':strings,'seed024':result['seed024']},ensure_ascii=False,indent=2))
