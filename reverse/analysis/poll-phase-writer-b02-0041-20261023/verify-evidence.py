"""B02: read existing evidence and ROM; retain only bounded instruction windows."""
import json
import sys
from pathlib import Path
from capstone import Cs, CS_ARCH_RISCV, CS_MODE_RISCV32, CS_MODE_RISCVC

HERE = Path(__file__).resolve().parent
TREE = HERE.parents[2]
SOURCE = Path(sys.argv[1])
BASE = 0x9ffff000
rom = (SOURCE / 'roms/0041/ap01-1.0.2_0041.bin').read_bytes()
load = lambda p: json.loads(p.read_text(encoding='utf-8'))
usb = load(TREE / 'reverse/analysis/usb-interface-ota-0041-20261023.json')
response = load(TREE / 'reverse/analysis/uart-response-0041-20261023.json')
functions = {f['address']: f for f in usb['functions']}
helper = response['functions'][1]
decoder = Cs(CS_ARCH_RISCV, CS_MODE_RISCV32 | CS_MODE_RISCVC)
windows = []
decoded = {}
specs = [
    ('callback-slot-install-only', 0xa00a4718, 0xa00a4728, functions['0xa00a4708']),
    ('dispatch-base-only', 0xa00a83f8, 0xa00a8408, functions['0xa00a8330']),
    ('dispatch-call-only', 0xa00a8514, 0xa00a8548, functions['0xa00a8330']),
    ('writer-entry-discriminant', 0xa00a8582, 0xa00a85cc, functions['0xa00a8582']),
    ('writer-58-branch', 0xa00a873e, 0xa00a8794, functions['0xa00a8582']),
    ('writer-continuation', 0xa00a8aae, 0xa00a8ab4, functions['0xa00a8582']),
    ('cache-helper', 0xa0191652, 0xa0191700, helper),
]
for name, start, end, f in specs:
    asm = f.get('assembly', f.get('normalized_result', {}).get('assembly'))
    relevant = [s for s in asm if start <= int(s.split(':')[0], 16) < end]
    raw = rom[start-BASE:end-BASE]
    retained = next(r for r in f['raw_ranges']
                    if r['file_offset'] <= start-BASE
                    and r['file_offset'] + len(bytes.fromhex(r.get('bytes_hex', r.get('hex', '')))) >= end-BASE)
    retained_bytes = bytes.fromhex(retained.get('bytes_hex', retained.get('hex', '')))
    offset = start-BASE-retained['file_offset']
    assert raw == retained_bytes[offset:offset+len(raw)]
    records = []
    pc = start
    for s in relevant:
        addr = int(s.split(':')[0], 16)
        assert addr == pc
        n = 4 if rom[pc-BASE] & 3 == 3 else 2
        b = rom[pc-BASE:pc-BASE+n]
        ins = next(decoder.disasm(b, pc))
        assert ins.size == n
        decoded[pc] = ins
        records.append({'address': hex(pc), 'hex': b.hex(),
                        'retained_assembly': s.split(': ', 1)[1],
                        'capstone_assembly': ins.mnemonic + ' ' + ins.op_str})
        pc += n
    assert pc == end
    windows.append({'name': name, 'start': hex(start), 'end_exclusive': hex(end),
                    'file_offset': start-BASE, 'hex': raw.hex(),
                    'source': f['source'], 'evidence_id': f['evidence_id'],
                    'instructions': records})

# Decode key ordinary RV32 fields independently of provider pseudocode.
word = lambda pc: int.from_bytes(rom[pc-BASE:pc-BASE+4], 'little')
w = word(0xa00a878e)
imm = ((w >> 25) << 5) | ((w >> 7) & 31)
imm = imm - 4096 if imm & 2048 else imm
assert (w & 127, (w >> 12) & 7, (w >> 15) & 31, (w >> 20) & 31) == (0x23, 0, 15, 0)
assert imm == -0x4cb and 0x62fc5000 + imm == 0x62fc4b35
assert word(0xa00a878a) & 0xfffff000 == 0x62fc5000
assert decoded[0xa00a877a].op_str == 'a1, 4'
assert decoded[0xa00a8784].op_str == 'a5, 0(s1)'
assert decoded[0xa00a8786].mnemonic == 'beqz'
# Capstone RISCV renders PC-relative offsets, retained Ghidra renders targets.
target = lambda pc: pc + int(decoded[pc].op_str.split(',')[-1].strip(), 0)
assert target(0xa00a8786) == 0xa00a8aae
assert target(0xa00a8780) == 0xa0191652
assert target(0xa00a8aae) == 0xa0191746
assert target(0xa00a876a) == 0xa00a85e4
result = {'task_id': 'B02', 'method': 'Read-only ROM bytes plus retained evidence; no firmware execution or shared database.',
          'windows': windows, 'checks': {'windows': len(windows), 'ordinary_instructions': len(decoded),
          'store_width': '8-bit sb zero, -0x4cb(a5), a5=0x62fc5000',
          'writer_address': '0xa00a878e', 'phase_address': '0x62fc4b35',
          'post_helper_condition': '32-bit cache load != 0',
          'direct_continuation': 'a0191746', 'vendor_instructions_in_windows': 0},
          'limits': ['Frame parser acceptance is inherited, not re-reviewed.',
                     'Only cmd 0x58 branch of a00a8582 is recovered here.',
                     'Other phase writes and indirect callers remain outside scope.',
                     'No new hashes or baseline copies created.']}
(HERE / 'instruction-evidence.json').write_text(json.dumps(result, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
print(json.dumps(result['checks'], ensure_ascii=False))
