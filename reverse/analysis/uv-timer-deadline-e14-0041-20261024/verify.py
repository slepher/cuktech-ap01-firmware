"""E14 bounded static evidence checks. Never runs ROM or the analyzer model."""
import json
from pathlib import Path
from capstone import Cs, CS_ARCH_RISCV, CS_MODE_RISCV32, CS_MODE_RISCVC

HERE = Path(__file__).resolve().parent
TREE = HERE.parents[2]
MAIN = Path('D:/Documents/PlatformIO/Projects/cuktech-ap01-firmware')
LANG = MAIN / 'evidence/rea-0041-20261017/ghidra/Ghidra/Processors/RISCV/data/languages'
ROM = MAIN / 'roms/0041/ap01-1.0.2_0041.bin'
raw = ROM.read_bytes()
base = 0x9ffff000
old = json.loads((TREE / 'reverse/analysis/miio-deferred-review-f02-0041-20261023/independent-evidence.json').read_text())
old_ins = {int(i['pc'], 16): i for w in old['windows'] for i in w['instructions']}
model = (LANG / 'ap01thead2.sinc').read_text()
regs = (LANG / 'ap01thead2.reg.sinc').read_text()
profile = (LANG / 'ap01thead3.slaspec').read_text()
assert '@include "ap01thead2.sinc"' in profile
assert ':add64 rd,rs1,rs2 is op0006=0x77 & op1214=1 & op2531=0x60' in model
for fragment in ['th2p1lo=(16,19)', 'th2p2lo=(21,24)', 'th2pdlo=(8,11)']:
    assert fragment in regs
for fragment in ['local result:8 = src1 + src2;', 'th2dlo = result:4;', 'th2pdhi = result(4);']:
    assert fragment in model

md = Cs(CS_ARCH_RISCV, CS_MODE_RISCV32 | CS_MODE_RISCVC)
windows = []
custom = []
for first, end in [(0xa009d182, 0xa009d1ce), (0xa009d314, 0xa009d336)]:
    pc = first
    lines = []
    while pc < end:
        size = 4 if raw[pc-base] & 3 == 3 else 2
        blob = raw[pc-base:pc-base+size]
        assert blob.hex() == old_ins[pc]['bytes']
        if pc in [0xa009d18c, 0xa009d1bc]:
            word = int.from_bytes(blob, 'little')
            fields = dict(op=word & 127, funct3=(word >> 12) & 7,
                          funct7=word >> 25, rd=(word >> 7) & 31,
                          rs1=(word >> 15) & 31, rs2=(word >> 20) & 31)
            expected = (10, 20, 10) if pc == 0xa009d18c else (12, 10, 12)
            assert (fields['op'], fields['funct3'], fields['funct7']) == (0x77, 1, 0x60)
            assert (fields['rd'], fields['rs1'], fields['rs2']) == expected
            # Independently decode the pair selectors declared in retained reg.sinc.
            selectors = ((word >> 8) & 15, (word >> 16) & 15, (word >> 21) & 15)
            assert tuple(s * 2 for s in selectors) == expected
            pairs = {k: [v, v+1] for k, v in zip(['destination', 'source1', 'source2'], expected)}
            asm = 'retained ADD64: ' + str(pairs)
            custom.append(dict(pc=hex(pc), bytes=blob.hex(), fields=fields,
                               pair_selectors=selectors, register_pairs=pairs))
        else:
            ins = next(md.disasm(blob, pc), None)
            assert ins is not None and ins.size == size
            asm = ins.mnemonic + ' ' + ins.op_str
            assert asm == old_ins[pc]['asm']
        lines.append(dict(pc=hex(pc), bytes=blob.hex(), asm=asm))
        pc += size
    assert pc == end
    windows.append(dict(start=hex(first), end_exclusive=hex(end), instructions=lines))

# The later retained round3 hits are caller evidence, not a new timer body.
round3 = MAIN / 'evidence/rea-0041-20261017/round3/evidence'
hits = []
for path in sorted(round3.glob('*.json')):
    text = path.read_text()
    if 'a009d146' not in text and 'a009d304' not in text:
        continue
    outer = json.loads(text)
    entries = outer.get('records', [outer]) if isinstance(outer, dict) else outer
    records = []
    for entry in entries:
        if not isinstance(entry, dict):
            continue
        record = entry.get('structuredContent', entry)
        if isinstance(record, dict) and ('a009d146' in json.dumps(record) or 'a009d304' in json.dumps(record)):
            records.append(dict(evidence_id=record.get('evidence_id'),
                                operation=record.get('operation'), parameters=record.get('parameters'),
                                profile=record.get('analysis_profile', {}).get('digest')))
    hits.append(dict(path=str(path), records=records,
                     exact_d18c_present='a009d18c' in text,
                     exact_d1bc_present='a009d1bc' in text))
assert all(not h['exact_d18c_present'] and not h['exact_d1bc_present'] for h in hits)
result = dict(task='E14', result='PASS', method='read-only bytes and retained model text; no model execution',
              model_sources=[str(LANG / x) for x in ['ap01thead2.sinc', 'ap01thead2.reg.sinc', 'ap01thead3.slaspec']],
              prior_source=str(TREE / 'reverse/analysis/miio-deferred-review-f02-0041-20261023/independent-evidence.json'),
              custom_words=custom, windows=windows, round3_bounded_hits=hits,
              instruction_count=sum(len(w['instructions']) for w in windows),
              limits=['Private retained ISA clause reused, not vendor specification authentication.',
                      'No arithmetic execution, overflow inputs, firmware, analyzer, SIM or replay.',
                      'No whole-function export or heap/source-version authentication.'])
(HERE / 'verification.json').write_text(json.dumps(result, indent=2, ensure_ascii=False) + '\n')
print('PASS:', result['instruction_count'], 'sparse instructions; 2 existing ADD64 clauses matched; round3 hits', len(hits))
