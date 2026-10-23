"""B01 bounded read-only ROM/evidence checks; writes only this task's review index."""
import collections
import hashlib
import json
import math
import re
import sys
from pathlib import Path
from capstone import Cs, CS_ARCH_RISCV, CS_MODE_RISCV32, CS_MODE_RISCVC

HERE = Path(__file__).resolve().parent
TREE = HERE.parents[2]
SOURCE = Path(sys.argv[1])
BASE = 0x9ffff000
rom = (SOURCE / 'roms/0041/ap01-1.0.2_0041.bin').read_bytes()
load = lambda name: json.loads((HERE / name).read_text(encoding='utf-8'))
sha = lambda data: hashlib.sha256(data).hexdigest()
assert sha(rom) == load('contracts.json')['rom_sha256']
checks = {}
source_checks = 0
for name, keys in [('retained-functions.json', []), ('timer-registration-source.json', ['index']), ('mcu-carrier-boundaries.json', ['source']), ('poll-vendor-model.json', ['source'])]:
    obj = load(name)
    sources = [obj[k] for k in keys]
    if name == 'retained-functions.json':
        sources += [r['source'] for r in obj['functions']]
        sources.append(obj['reused_cleanup']['index'])
    for source in sources:
        assert sha((SOURCE / source['path']).read_bytes()) == source['sha256'], source['path']
        source_checks += 1
checks['existing_source_fingerprints'] = source_checks

retained = load('retained-functions.json')
ranges = [r for f in retained['functions'] for r in f['raw_ranges']]
ranges += retained['reused_cleanup']['function']['raw_ranges']
for r in ranges:
    data = bytes.fromhex(r.get('hex') or r['bytes_hex'])
    offset = r['file_offset'] if 'file_offset' in r else int(r['start'], 16) - BASE
    assert rom[offset:offset + len(data)] == data
    assert sha(data) == r['sha256']
checks['retained_raw_ranges'] = len(ranges)

md = Cs(CS_ARCH_RISCV, CS_MODE_RISCV32 | CS_MODE_RISCVC)
windows = load('instruction-windows.json')['windows']
instructions = {}
ordinary = 0
for w in windows:
    data = bytes.fromhex(w['hex'])
    assert rom[w['file_offset']:w['file_offset'] + len(data)] == data
    assert sha(data) == w['sha256']
    pc = int(w['start'], 16)
    for ins in w['instructions']:
        assert int(ins['address'], 16) == pc
        raw = bytes.fromhex(ins['hex'])
        assert len(raw) == (4 if raw[0] & 3 == 3 else 2)
        assert rom[pc-BASE:pc-BASE+len(raw)] == raw
        if not ins['assembly'].startswith('.unknown'):
            decoded = next(md.disasm(raw, pc))
            assert decoded.mnemonic + ' ' + decoded.op_str == ins['assembly']
            ordinary += 1
        instructions[pc] = ins
        pc += len(raw)
    assert pc == int(w['end_exclusive'], 16)
checks['instruction_windows'] = len(windows)
checks['ordinary_instruction_decodes'] = ordinary

model = load('poll-vendor-model.json')
model_lines = (SOURCE / model['source']['path']).read_text().splitlines()
for e in model['excerpts']:
    assert '\n'.join(model_lines[e['start_line']-1:e['end_line']]) == e['text']
reg_path = SOURCE / model['source']['path'].replace('ap01thead2.sinc', 'ap01thead2.reg.sinc')
reg = reg_path.read_text()
assert all(field in reg for field in ['thshift=(25,26)', 'thlsb=(20,25)', 'thmsb=(26,31)'])
# Verify fields against existing model definitions, retaining only needed excerpts.
model_review = []
def word(pc):
    return int.from_bytes(bytes.fromhex(instructions[pc]['hex']), 'little')
def verify(pc, rd, rs1, rs2, funct3, kind, extra):
    w = word(pc)
    assert (w & 127, (w >> 7) & 31, (w >> 15) & 31, (w >> 12) & 7) == (11, rd, rs1, funct3)
    assert ((w >> 20) & 31) == rs2
    if kind == 'addsl': assert (w >> 27) == 0 and ((w >> 25) & 3) == extra
    if kind == 'lrbu': assert (w >> 27) == 16 and ((w >> 25) & 3) == extra
    if kind == 'ext': assert ((w >> 26) & 63, (w >> 20) & 63) == extra
    if kind in ('mula', 'mvnez'): assert (w >> 25) == extra
    model_review.append({'address': hex(pc), 'hex': instructions[pc]['hex'], 'interpretation': kind})
verify(0xa0191786,9,11,15,1,'addsl',3)
verify(0xa01917a6,15,15,13,4,'lrbu',0)
verify(0xa00a42d0,15,15,0,2,'ext',(7,0))
verify(0xa00a4372,15,15,0,2,'ext',(7,0))
verify(0xa00a4338,10,11,16,1,'mula',16)
verify(0xa00a8090,15,0,14,1,'mvnez',33)
verify(0xa00a82b4,15,0,14,1,'mvnez',33)
verify(0xa00a830a,13,12,14,1,'addsl',3)
for prefix in [':th.ext rd,rs1,7,0 ', ':th.mula ', ':th.mvnez ']:
    start = next(i for i,s in enumerate(model_lines) if s.startswith(prefix))
    end = next(i for i in range(start+1,len(model_lines)) if model_lines[i] == '}')
    model_review.append({'model_lines': [start+1,end+1], 'text':'\n'.join(model_lines[start:end+1])})
checks['vendor_words'] = 8

init = load('poll-initializers.json')
for r in init['regions']:
    raw = bytes.fromhex(r['hex'])
    assert int(r['rom_address'],16)-BASE == r['file_offset']
    assert int(r['rom_address'],16) == 0xa00027d4 + int(r['ram'],16) - 0x62fc2cc0
    assert rom[r['file_offset']:r['file_offset']+len(raw)] == raw
raw = bytes.fromhex(init['regions'][0]['hex'])
assert raw == bytes.fromhex('384bfc62010100003c4bfc62040a0000204bfc620a0002005800000050515759')
checks['initializer_regions'] = len(init['regions'])

for p in load('mcu-carrier-boundaries.json')['payloads']:
    body = rom[p['body_file_offset']:p['body_file_offset']+p['body_bytes']]
    assert sha(body) == p['body_sha256']
    counts = collections.Counter(body)
    entropy = -sum(n/len(body)*math.log2(n/len(body)) for n in counts.values())
    assert abs(entropy-p['entropy_bits_per_byte']) < 1e-10
    blocks = collections.Counter(body[i:i+16] for i in range(0,len(body),16))
    assert len(blocks) == p['unique16_blocks'] == p['total16_blocks']
checks['opaque_carrier_statistics'] = 3

prior = json.loads((SOURCE/'reverse/analysis/usb-interface-ota-0041-20261023.json').read_text())
f = next(f for f in prior['functions'] if f['address'] == '0xa00a8582')
assert all(any(hex(a)[2:] in line and text in line for line in f['assembly']) for a,text in [(0xa00a85a0,'sb a0, -0x50'),(0xa00a85a4,'sb a1, -0x4f'),(0xa00a85a8,'sw a2, -0x4c')])
assert rom[0xa00a85a0-BASE:0xa00a85ac-BASE].hex() == '2308a4fa a308b4fa 232ac4fa'.replace(' ','')
checks['response_view_stack_stores'] = 'a00a85a0/a4/a8: command@0,length@1,payload@4'

report = TREE/'reverse/reports/ap01/dock-presence-polling-0041-20261023.md'
links = re.findall(r'\]\(([^)]+)\)', report.read_text(encoding='utf-8'))
for link in links:
    if link.endswith('review-index.json'): continue
    assert (report.parent/link).is_file(), link
checks['report_links'] = len(links)
index = {
 'task_id':'B01', 'status':'accepted_with_correction', 'recovery_status':'partial',
 'scope':'Existing dock report only; static ROM bytes, ordinary ISA, eight vendor words, initializer layout, source references and opaque-carrier statistics. No firmware or hardware execution.',
 'checks':checks, 'vendor_review':model_review,
 'acceptance':[
  {'topic':'ID ADC','result':'accepted','evidence':'instruction-windows.json id_adc_cb a00a4288..a00a43ae; th.ext 7,0 checked from ROM fields, th.mula record stride checked','limit':'Valid-record local decision only; physical units and ADC setup remain unknown.'},
  {'topic':'Timer phases and USB local branches','result':'accepted','evidence':'instruction-windows.json timer_cb a00a806a..a00a832e; registration a005ab4c..a005ab60','limit':'20 is instruction fact; milliseconds follow prior LV timer identification, not independently certified timebase/source/version here.'},
  {'topic':'Poll table and selection','result':'corrected','evidence':'a0191796 branches to a0191766 (write limit); a019179c branches to a019176a (no write)','correction':'Only phase mismatch writes sent=limit. Matching phase with sent>=limit leaves sent unchanged.'},
  {'topic':'Response caching and publication','result':'accepted','evidence':'a0191652..a0191744; response stores at a00a85a0/a4/a8 checked directly against ROM','limit':'Callback target value and argument shape established; complete derived-event consumers not reviewed.'},
  {'topic':'Reset and release order','result':'accepted','evidence':'a00a5558..a00a55b8; a00a3ab6..a00a3b20; ID calls at a00a4302/a00a4306','limit':'UiIFace synchronous notification details inherited from linked report; full deinit body not re-reviewed.'},
  {'topic':'MCU carriers','result':'accepted_as_opaque','evidence':'mcu-carrier-boundaries.json existing statistics recomputed','limit':'No ISA, compression or encryption attribution.'}
 ],
 'instruction_fact_inference_boundary':{'fact':'Pointers, offsets, branches, arithmetic and writes in listed windows; exact initializer bytes.', 'inference':'~100ms phase revisit under normal scheduler, physical label from retained log strings; field names are analysis names.', 'unknown':'All module state writers, teardown and MCU internal program; library source/version not newly certified.'},
 'source_status':'Vendor wrappers/callbacks and unknown-source logic retained. No newly certified open-source exclusions.',
 'validation':'All script assertions passed; git diff --check performed separately before commit. Auxiliary collector not rerun and no shared database touched.',
 'next_small_task':'Identify one writer of poll-controller byte phase@62fc4b35 outside timer; recover its direct caller and exact phase assignment only.'
}
(HERE/'review-index.json').write_text(json.dumps(index,indent=2,ensure_ascii=False)+'\n',encoding='utf-8')
print(json.dumps({'status':index['status'],'checks':checks},ensure_ascii=False))
