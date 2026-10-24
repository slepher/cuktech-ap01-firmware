"""P-R04 independent bounded stdlib review. Does not load author code."""
import hashlib
import json
from pathlib import Path

ROOT = Path('D:/Documents/PlatformIO/Projects/cuktech-ap01-firmware')
HERE = Path(__file__).resolve().parent
BASE = 0x9ffff000
ROM = ROOT / 'roms/0041/ap01-1.0.2_0041.bin'
assert ROM.stat().st_size == 6769704

def read_json(path):
    return json.loads((ROOT / path).read_text(encoding='utf-8'))

def sx(value, bits):
    return value - (1 << bits) if value & (1 << (bits - 1)) else value

def decode(pc, raw):
    w = int.from_bytes(raw, 'little')
    if len(raw) == 4:
        op, rd, f3, rs1, rs2 = w & 127, w >> 7 & 31, w >> 12 & 7, w >> 15 & 31, w >> 20 & 31
        if op == 0x37:
            return ['lui', rd, w & 0xfffff000]
        if op == 0x13 and f3 == 0:
            return ['addi', rd, rs1, sx(w >> 20, 12)]
        if op == 3 and f3 == 5:
            return ['lhu', rd, rs1, sx(w >> 20, 12)]
        if op == 0x23 and f3 == 0:
            return ['sb', rs2, rs1, sx((w >> 25 << 5) | (w >> 7 & 31), 12)]
        if op == 0x63 and f3 in (0, 1):
            imm = ((w >> 31) << 12) | ((w >> 7 & 1) << 11) | ((w >> 25 & 63) << 5) | ((w >> 8 & 15) << 1)
            return ['beq' if f3 == 0 else 'bne', rs1, rs2, pc + sx(imm, 13)]
        if op == 0x6f:
            imm = ((w >> 31) << 20) | ((w >> 12 & 255) << 12) | ((w >> 20 & 1) << 11) | ((w >> 21 & 1023) << 1)
            return ['jal', rd, pc + sx(imm, 21)]
        if op == 0x0b and f3 == 3:
            return ['vendor-extu-fields', rd, rs1, w >> 26 & 63, w >> 20 & 63]
    else:
        assert w & 3 == 1
        f3, rd = w >> 13, w >> 7 & 31
        imm6 = (w >> 2 & 31) | (w >> 12 & 1) << 5
        if f3 == 2:
            return ['li', rd, sx(imm6, 6)]
        if f3 == 3:
            return ['lui', rd, sx(imm6, 6) << 12]
        if f3 == 4 and w >> 10 & 3 == 3 and w >> 5 & 3 == 2 and not (w >> 12 & 1):
            return ['or', 8 + (w >> 7 & 7), 8 + (w >> 2 & 7)]
        if f3 == 7:
            imm = ((w >> 12 & 1) << 8) | ((w >> 10 & 3) << 3) | ((w >> 5 & 3) << 6) | ((w >> 3 & 3) << 1) | ((w >> 2 & 1) << 5)
            return ['bnez', 8 + (w >> 7 & 7), pc + sx(imm, 9)]
        if f3 == 5:
            # CJ immediate bits 11|4|9:8|10|6|7|3:1|5.
            imm = ((w >> 12 & 1) << 11) | ((w >> 11 & 1) << 4) | ((w >> 9 & 3) << 8) | ((w >> 8 & 1) << 10) | ((w >> 7 & 1) << 6) | ((w >> 6 & 1) << 7) | ((w >> 3 & 7) << 1) | ((w >> 2 & 1) << 5)
            return ['j', pc + sx(imm, 12)]
    raise AssertionError((hex(pc), raw.hex()))

expected = {
    0xa00a8602: ['addi',15,0,0x55], 0xa00a8606: ['beq',10,15,0xa00a88f6],
    0xa00a88f6: ['lui',9,0x62fcb000], 0xa00a88fa: ['addi',12,8,-80],
    0xa00a88fe: ['li',11,24], 0xa00a8900: ['addi',10,9,4],
    0xa00a8904: ['jal',1,0xa0191652], 0xa00a8908: ['addi',15,9,4],
    0xa00a890c: ['lhu',12,15,2], 0xa00a8910: ['lui',14,4096],
    0xa00a8912: ['addi',11,14,-1535], 0xa00a8916: ['li',13,1],
    0xa00a8918: ['beq',12,11,0xa00a8928], 0xa00a891c: ['addi',14,14,-1534],
    0xa00a8920: ['li',13,0], 0xa00a8922: ['bne',12,14,0xa00a8928],
    0xa00a8926: ['li',13,2], 0xa00a8928: ['lui',14,0x62fcb000],
    0xa00a892c: ['sb',13,14,-272], 0xa00a8930: ['lhu',14,15,16],
    0xa00a8934: ['lhu',13,15,18], 0xa00a8938: ['or',14,13],
    0xa00a893a: ['vendor-extu-fields',14,14,15,0],
    0xa00a893e: ['bnez',14,0xa00a8950], 0xa00a8940: ['li',10,2],
    0xa00a8942: ['jal',1,0xa00a3a58], 0xa00a8946: ['li',11,1],
    0xa00a8948: ['li',10,10], 0xa00a894a: ['jal',1,0xa00a417c],
    0xa00a894e: ['j',0xa00a88e2], 0xa00a88e2: ['li',10,2],
    0xa00a88e4: ['jal',1,0xa00a385a], 0xa00a88e8: ['j',0xa00a85e4],
}
response_path = 'reverse/analysis/uart-response-0041-20261023.json'
f = read_json(response_path)['functions'][0]
assert f['normalized_result']['procedure']['address'] == '0xa00a8582'
assert f['profile_digest'] == 'bcefdee5092076e55636e077b45523e203f4b870ae7b7ab547945ed1b8162279'
rows = []
with ROM.open('rb') as rom:
    for start, end in [(0xa00a8602,0xa00a860a),(0xa00a88f6,0xa00a8950),(0xa00a88e2,0xa00a88ea)]:
        pc = start
        while pc < end:
            rom.seek(pc-BASE)
            first = rom.read(2)
            raw = first + rom.read(2) if int.from_bytes(first,'little') & 3 == 3 else first
            actual = decode(pc,raw)
            assert actual == expected[pc], (hex(pc),actual,expected[pc])
            rr = [r for r in f['raw_ranges'] if int(r['start'],16) <= pc and pc+len(raw)-1 <= int(r['end'],16)]
            assert len(rr) == 1
            offset = pc-int(rr[0]['start'],16)
            assert bytes.fromhex(rr[0]['hex'])[offset:offset+len(raw)] == raw
            rows.append({'pc':hex(pc),'file_offset':pc-BASE,'hex':raw.hex(),'decoded_fields':actual})
            pc += len(raw)
        assert pc == end
assert len(rows) == len(expected) == 33 and sum(len(bytes.fromhex(r['hex'])) for r in rows) == 106

model_path = 'evidence/rea-0041-20261017/ghidra/Ghidra/Processors/RISCV/data/languages/ap01thead2.sinc'
model = (ROOT/model_path).read_bytes()
lines = model.decode().splitlines()
line = next(i for i,s in enumerate(lines) if s.startswith(':th.extu rd,rs1,15,0 is'))
excerpt = lines[line:line+5]
assert 'local value:4 = rs1 << 16;' in excerpt[2] and 'rd = value >> 16;' in excerpt[3]
regs = (ROOT/model_path.replace('.sinc','.reg.sinc')).read_text()
assert 'thmsb=(26,31)' in regs and 'thlsb=(20,25)' in regs

negative = []
for path, addresses in [
    ('reverse/analysis/miio-deferred-settings-0041-20261023/retained-functions.json', {'0xa009d8bc','0xa00a0bd8','0xa00a0e78'}),
    ('reverse/analysis/mode-control-0041-20261023/retained-functions.json', {'0xa0195166'}),
]:
    selected = [g for g in read_json(path)['functions'] if g['normalized_result']['procedure']['address'] in addresses]
    assert {g['normalized_result']['procedure']['address'] for g in selected} == addresses
    for g in selected:
        assert g['normalized_result']['assembly'] and g['normalized_result']['pseudocode']
        negative.append((path,g,g.get('profile_digest') or g.get('profile',{}).get('digest')))
property_path = 'evidence/rea-0041-20261017/evidence/whole-rom-private-20261023-024.json'
obj = read_json(property_path)
g = obj.get('structuredContent') or json.loads(obj['content'][0]['text'])
assert g['normalized_result']['assembly'] and g['normalized_result']['pseudocode']
negative.append((property_path,g,g['analysis_profile']['digest']))
searches = []
for path,g,profile in negative:
    n = g['normalized_result']
    text = json.dumps(n, ensure_ascii=False).lower()
    counts = {key:text.count(key) for key in ('62fcb51e','62fcb516','a00a417c')}
    assert not any(counts.values())
    assert profile == 'b6368dd18431e8113aa5026c713d41e648ab0f6ddd9421ff6c4a49e23b3cd2f3'
    searches.append({'path':path,'procedure':n['procedure']['address'],'evidence_id':g['evidence_id'],'profile_digest':profile,'normalized_exact_hits':counts,
                     'assembly_rows':len(n['assembly']),'pseudocode_characters':len(n['pseudocode'])})
assert len(searches) == 5 and searches[-1]['procedure'] == '0xa00a2578'

assembly = f['normalized_result']['assembly']
sites = [s for s in assembly if 'jal ra, 0xa00a417c' in s]
assert [s.split(':')[0] for s in sites] == ['0xa00a894a','0xa00a9878','0xa00a98ca']
index_path = 'reverse/analysis/whole-rom-coverage-0041-20261023-round1.json'
callers = [g['address'] for g in read_json(index_path)['functions'] if '0xa00a417c' in g['direct_calls']['callees']]
assert callers == ['0xa00a8582']
context = [s for s in assembly if int(s.split(':')[0],16) in (0xa00a85a0,0xa00a85a4,0xa00a85a8,0xa00a85e4,0xa00a85e6)]
out = {'claim':'P-04 / P-R04','method':'independent Python standard-library bitfield decoding; no author validator imported/executed; no REA session/model execution',
       'rom_identity_inherited':'roms/CATALOG.md','mapping':'file_offset = VA - 0x9ffff000','rows':rows,
       'response_source':{'path':response_path,'json_pointer':'/functions/0','evidence_id':f['evidence_id'],'profile_digest':f['profile_digest'],'source':f['source']},
       'vendor_model':{'path':model_path,'sha256':hashlib.sha256(model).hexdigest(),'start_line':line+1,'excerpt':excerpt,'limitation':'existing model source read only, not manufacturer specification or full ISA certification'},
       'bounded_searches':searches,'direct_frontier':{'path':index_path,'callers':callers,'retained_sites':sites,'limitation':'direct index only; excludes no indirect callers or alias writers'},
       'inherited_context_only':context,'limits':['No product units/names or property mapping recovered','No new helper/dispatcher full-body analysis','Property GET successor seed not authenticated from ROM in this review']}
(HERE/'independent-review.json').write_text(json.dumps(out,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
print(json.dumps({'instructions':len(rows),'bytes':106,'dossiers':len(searches),'raw_and_decode':'PASS','profile_and_bounded_search':'PASS'}))
