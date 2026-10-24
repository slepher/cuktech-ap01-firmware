"""Independent bounded static review. Python stdlib only; no target execution."""
import json
from pathlib import Path
from datetime import datetime, timezone

ROOT = Path('D:/Documents/PlatformIO/Projects/cuktech-ap01-firmware')
OUT = Path(__file__).resolve().parent
START, END, BASE = 0xa00ad486, 0xa00ad602, 0x9ffff000

def read(rel):
    return json.loads((ROOT / rel).read_text(encoding='utf-8'))

def signed(value, width):
    return value - (1 << width) if value & (1 << (width - 1)) else value

parent = read('reverse/rehost/system-complete-0041.json')
body = [x for x in parent['local_disassembly']['0xa00ad486']
        if START <= int(x['address'], 16) < END]
rom = (ROOT / 'roms/0041/ap01-1.0.2_0041.bin').read_bytes()
assert len(rom) == 6769704
cursor = START
calls, branches, stores, loads, immediates = {}, {}, [], {}, {}
for row in body:
    pc = int(row['address'], 16)
    data = bytes.fromhex(row['bytes'])
    assert pc == cursor
    assert data == rom[pc-BASE:pc-BASE+len(data)]
    word = int.from_bytes(data, 'little')
    assert len(data) == (4 if word & 3 == 3 else 2)
    cursor += len(data)
    if len(data) == 4:
        op, f3 = word & 127, (word >> 12) & 7
        rd, rs1, rs2 = (word >> 7) & 31, (word >> 15) & 31, (word >> 20) & 31
        if op == 0x6f:
            imm = ((word >> 31) << 20) | (((word >> 12) & 255) << 12) | (((word >> 20) & 1) << 11) | (((word >> 21) & 1023) << 1)
            assert rd == 1
            calls[hex(pc)] = hex(pc + signed(imm, 21))
        if op == 0x63:
            imm = ((word >> 31) << 12) | (((word >> 7) & 1) << 11) | (((word >> 25) & 63) << 5) | (((word >> 8) & 15) << 1)
            branches[hex(pc)] = {'funct3': f3, 'rs1': rs1, 'rs2': rs2, 'target': hex(pc + signed(imm, 13))}
        if op == 3:
            assert f3 == 2
            loads[hex(pc)] = [rd, rs1, signed(word >> 20, 12)]
        if op == 0x23:
            stores.append(hex(pc))
        if op == 0x13:
            assert f3 == 0  # no ANDI, shifts or other immediate operation
            immediates[hex(pc)] = [rd, rs1, signed(word >> 20, 12)]
    else:
        q, f3 = word & 3, word >> 13
        if q == 2 and f3 == 6:
            stores.append(hex(pc))
        if q == 1 and f3 in (6, 7):
            imm = (((word >> 12) & 1) << 8) | (((word >> 10) & 3) << 3) | (((word >> 5) & 3) << 6) | (((word >> 3) & 3) << 1) | (((word >> 2) & 1) << 5)
            branches[hex(pc)] = {'compressed': True, 'nonzero': f3 == 7, 'rs1': 8 + ((word >> 7) & 7), 'target': hex(pc + signed(imm, 9))}
        if q == 1 and f3 == 5:
            imm = (((word >> 12) & 1) << 11) | (((word >> 11) & 1) << 4) | (((word >> 9) & 3) << 8) | (((word >> 8) & 1) << 10) | (((word >> 7) & 1) << 6) | (((word >> 6) & 1) << 7) | (((word >> 3) & 7) << 1) | (((word >> 2) & 1) << 5)
            branches[hex(pc)] = {'jump': True, 'target': hex(pc + signed(imm, 12))}
        if q == 0 and f3 == 2:
            imm = (((word >> 5) & 1) << 6) | (((word >> 10) & 7) << 3) | (((word >> 6) & 1) << 2)
            loads[hex(pc)] = [8 + ((word >> 2) & 7), 8 + ((word >> 7) & 7), imm]
        if q == 1 and f3 == 2:
            immediates[hex(pc)] = [(word >> 7) & 31, 0, signed((((word >> 12) & 1) << 5) | ((word >> 2) & 31), 6)]
assert cursor == END and len(body) == 139
assert len(calls) == 29 and set(calls.values()) == {'0xa00d8f7c', '0xa00d9044', '0xa00dbb68'}
assert stores == ['0xa00ad488', '0xa00ad48a', '0xa00ad48c']
for pc, target in {
    '0xa00ad494':'0xa00ad5ba', '0xa00ad498':'0xa00ad4da',
    '0xa00ad49c':'0xa00ad4f0', '0xa00ad4a0':'0xa00ad550',
    '0xa00ad4aa':'0xa00ad522', '0xa00ad4f4':'0xa00ad50c',
    '0xa00ad552':'0xa00ad4e6', '0xa00ad55c':'0xa00ad58c',
    '0xa00ad5ba':'0xa00ad5de', '0xa00ad5c2':'0xa00ad506',
    '0xa00ad5e0':'0xa00ad4e6', '0xa00ad5ea':'0xa00ad506',
    '0xa00ad600':'0xa00ad5d8',
}.items():
    assert branches[pc]['target'] == target
assert branches['0xa00ad498']['funct3'] == 6
assert loads['0xa00ad5ca'] == [11, 9, 0xbc]
assert loads['0xa00ad5ce'] == [10, 9, 0xc8]
assert loads['0xa00ad5f2'] == [11, 9, 0xe4]
assert loads['0xa00ad5f6'] == [10, 9, 0xf0]
for pc, expected in {'0xa00ad5d2':[14,0,30], '0xa00ad5d4':[13,0,0], '0xa00ad5d6':[12,0,2], '0xa00ad5fa':[14,0,30], '0xa00ad5fc':[13,0,0], '0xa00ad5fe':[12,0,2]}.items():
    assert immediates[pc] == expected
author = read('reverse/analysis/summary-pane-p15-0041-20261024/evidence.json')
assert author['direct_call_targets'] == calls
old_by_pc = {x['address']: x for x in body}
for x in author['selected_instructions']:
    old = old_by_pc[x['address']]
    assert old['bytes'] == x['bytes'] and old['instruction'] == x['assembly']
coverage = read('reverse/analysis/whole-rom-coverage-0041-20261023-round1.json')
inventory = next(x for x in coverage['functions'] if x['address'] == hex(START))
assert inventory['extent']['body']['total_bytes'] == 380
assert inventory['extent']['body']['ranges'] == [{'start':hex(START), 'end':hex(END-1)}]
bundle = read('evidence/rea-0041-20261017/evidence/whole-rom-paths-20261023.evidence.json')
record = next(x for x in bundle['records'] if x['evidence_id'] == inventory['inventory_evidence'])
assert record['analysis_profile']['digest'] == 'b6368dd18431e8113aa5026c713d41e648ab0f6ddd9421ff6c4a49e23b3cd2f3'
assert record['analysis_profile']['parameters']['language_id'] == 'RISCV:LE:32:ap01thead2'
assert record['provider'] == {'id':'ghidra', 'name':'Ghidra', 'version':'12.1.4'}
assert any(x.get('address') == hex(START) for x in record['raw_result'])
assert sum(len(bytes.fromhex(x['bytes'])) for x in author['selected_instructions']) == 256
result = {'status':'PASS', 'completed_utc':datetime.now(timezone.utc).isoformat(),
          'method':'stdlib raw encoding fields, byte identity, retained evidence; no author code imported/executed; no instruction execution/model',
          'body_bytes':380, 'body_instructions':len(body), 'author_sparse_rows_matched':len(author['selected_instructions']),
          'direct_call_targets':calls, 'raw_control_edges':branches, 'raw_load_operands':loads,
          'raw_immediate_operands':immediates, 'store_sites':stores,
          'old_body_source':parent['source'], 'inventory_evidence':inventory['inventory_evidence'],
          'inventory_profile_digest':record['analysis_profile']['digest'],
          'limitations':['Manual static path composition; no formal proof, GUI execution, hardware or lifecycle validation.', 'Only kind0/1/2 contract; no new successors or library internals.']}
(OUT/'checks.json').write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
print(json.dumps({k:result[k] for k in ('status','completed_utc','body_bytes','body_instructions','author_sparse_rows_matched')}))
