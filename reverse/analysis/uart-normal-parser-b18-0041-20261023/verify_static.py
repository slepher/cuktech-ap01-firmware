"""B18 read-only instruction review; no emulation, input generation or hashing."""
import json
from pathlib import Path
from capstone import Cs, CS_ARCH_RISCV, CS_MODE_RISCV32, CS_MODE_RISCVC

HERE = Path(__file__).resolve().parent
SOURCE = Path('D:/Documents/PlatformIO/Projects/cuktech-ap01-firmware')
BASE = 0x9ffff000
rom = (SOURCE / 'roms/0041/ap01-1.0.2_0041.bin').read_bytes()
saved = json.loads((SOURCE / 'reverse/analysis/usb-interface-ota-0041-20261023.json').read_text(encoding='utf-8'))
decoder = Cs(CS_ARCH_RISCV, CS_MODE_RISCV32 | CS_MODE_RISCVC)
decoded, functions = {}, []
for fn in saved['functions']:
    if fn['address'] not in ('0xa00a8330', '0xa00ee934'):
        continue
    for block in fn['raw_ranges']:
        raw = bytes.fromhex(block['bytes_hex'])
        off = block['file_offset']
        assert rom[off:off + len(raw)] == raw
    rows = []
    for index, line in enumerate(fn['assembly']):
        address = int(line.split(':')[0], 16)
        end = (int(fn['assembly'][index + 1].split(':')[0], 16)
               if index + 1 < len(fn['assembly'])
               else int(fn['body']['ranges'][-1]['end'], 16) + 1)
        raw = rom[address - BASE:end - BASE]
        if address == 0xa00ee94e:
            # th.srb a0,a5,a3,0; independently inspect encoding, not execute it.
            word = int.from_bytes(raw, 'little')
            assert (word & 127, (word >> 12) & 7, (word >> 27) & 31) == (11, 5, 0)
            assert ((word >> 7) & 31, (word >> 15) & 31, (word >> 20) & 31) == (10, 15, 13)
            assert (word >> 25) & 3 == 0
            rendered = 'th.srb a0,a5,a3,0 [encoding fields verified]'
        else:
            instruction = next(decoder.disasm(raw, address))
            assert instruction.size == len(raw), hex(address)
            decoded[address] = instruction
            rendered = instruction.mnemonic + ' ' + instruction.op_str
        rows.append({'address': hex(address), 'hex': raw.hex(), 'provider': line.split(': ', 1)[1], 'independent': rendered})
    functions.append({'address': fn['address'], 'evidence_id': fn['evidence_id'],
                      'profile_digest': fn['profile_digest'], 'source': fn['source']['path'],
                      'range': fn['body']['ranges'], 'instructions': rows})

def exact(pc, mnemonic, operands):
    item = decoded[pc]
    assert (item.mnemonic, item.op_str) == (mnemonic, operands), hex(pc)

for pc, mnemonic, operands in [
    (0xa00a8400, 'addi', 's1, s1, 0x458'),
    (0xa00a8442, 'lbu', 'a5, 0x30(s1)'),
    (0xa00a8486, 'lbu', 'a4, 0x31(s1)'),
    (0xa00a8496, 'sb', 'zero, 0x2f(s1)'),
    (0xa00a849a, 'sh', 'a5, 0x30(s1)'),
    (0xa00a84aa, 'sb', 'a5, 0x31(s1)'),
    (0xa00a84d2, 'sb', 'a4, 0x30(s1)'),
    (0xa00a84f2, 'sb', 's4, 0x30(s1)'),
    (0xa00a8548, 'sb', 'zero, 0x30(s1)'),
    (0xa00a8568, 'sb', 'zero, 0x2f(s1)'),
    (0xa00a856c, 'sb', 'zero, 0x30(s1)'),
    (0xa00a8572, 'sb', 'zero, 0x31(s1)'),
    (0xa00ee942, 'lbu', 'a3, 0x2f(a5)'),
    (0xa00ee952, 'sb', 'a4, 0x2f(a5)'),
    (0xa00ee95e, 'sb', 'zero, 0x2f(a5)'),
    (0xa00ee962, 'sb', 'zero, 0x30(a5)'),
]:
    exact(pc, mnemonic, operands)

branches = []
for pc, expected in [
    (0xa00a844a, 0xa00a8486), (0xa00a848a, 0xa00a8572),
    (0xa00a8490, 0xa00a84a0), (0xa00a84a4, 0xa00a84b0),
    (0xa00a84b2, 0xa00a8422), (0xa00a84ba, 0xa00a857c),
    (0xa00a84c4, 0xa00a856c), (0xa00a84d8, 0xa00ee8fc),
    (0xa00a84ea, 0xa00a8552), (0xa00a854c, 0xa00ee9ce),
    (0xa00a8578, 0xa00a8422), (0xa00a857c, 0xa00ee934),
    (0xa00ee95a, 0xa00ee966),
]:
    item = decoded[pc]
    actual = pc + int(item.op_str.split(',')[-1].strip(), 0)
    assert actual == expected, hex(pc)
    branches.append({'address': hex(pc), 'target': hex(actual)})

result = {'task': 'B18', 'result': 'static_instruction_checks_passed',
          'method': 'Retained body byte equality; Capstone 5 RV32+C independent instruction boundaries and selected operands/targets; th.srb encoding fields and retained SLEIGH semantic review. No firmware execution.',
          'source_record': str(SOURCE / 'reverse/analysis/usb-interface-ota-0041-20261023.json'),
          'rom': str(SOURCE / 'roms/0041/ap01-1.0.2_0041.bin'),
          'functions': functions, 'branch_targets': branches,
          'ordinary_instructions': len(decoded), 'vendor_instructions': 1,
          'limitations': ['No runtime observation or synthetic byte stream.', 'No source/version authentication.', 'Selected operand/branch checks are not a complete ISA equivalence proof.']}
(HERE / 'instruction-review.json').write_text(json.dumps(result, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
print(json.dumps({key: result[key] for key in ('task', 'result', 'ordinary_instructions', 'vendor_instructions')}))
