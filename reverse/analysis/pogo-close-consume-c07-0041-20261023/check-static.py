"""C07: read-only ROM checks of selected local paths; never executes firmware."""
import json
from pathlib import Path
from capstone import Cs, CS_ARCH_RISCV, CS_MODE_RISCV32, CS_MODE_RISCVC

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
ROM = Path('D:/Documents/PlatformIO/Projects/cuktech-ap01-firmware/roms/0041/ap01-1.0.2_0041.bin')
BASE = 0x9ffff000
rom = ROM.read_bytes()
retained = json.loads((ROOT / 'reverse/analysis/factory-test-0041-20261023/retained-initializer.json').read_text())['function']
for r in retained['raw_ranges']:
    raw = bytes.fromhex(r['hex'])
    offset = int(r['start'], 16) - BASE
    assert rom[offset:offset + len(raw)] == raw
cs = Cs(CS_ARCH_RISCV, CS_MODE_RISCV32 | CS_MODE_RISCVC)
windows = []
for name, start, end in [
    ('existing_consume_and_local_conditions', 0xa005c166, 0xa005c19e),
    ('existing_consume_and_stop_exit', 0xa005c802, 0xa005c83e),
    ('pogo_four_registrations_to_return', 0xa005c8f8, 0xa005cad2),
]:
    raw = rom[start - BASE:end - BASE]
    ins = list(cs.disasm(raw, start))
    assert sum(i.size for i in ins) == len(raw)
    windows.append(dict(name=name, start=hex(start), end_exclusive=hex(end),
        instructions=[dict(address=hex(i.address), hex=i.bytes.hex(), decode=i.mnemonic + ' ' + i.op_str) for i in ins]))

def word(pc):
    return int.from_bytes(rom[pc - BASE:pc - BASE + 4], 'little')

def sx(n, bits):
    return n - (1 << bits) if n & (1 << (bits - 1)) else n

checks = []
for pc, fields in [
    (0xa005c16e, [1, 10, 0, 0xa005c802]),
    (0xa005c832, [0, 15, 0, 0xa005bfd2]),
    (0xa005c8fc, [5, 0, 15, 0xa005c910]),
    (0xa005c92e, [5, 0, 15, 0xa005c942]),
    (0xa005c964, [5, 0, 15, 0xa005c978]),
    (0xa005c99a, [5, 0, 15, 0xa005c9ae]),
    (0xa005ca52, [0, 10, 20, 0xa005ca62]),
    (0xa005ca6a, [0, 10, 18, 0xa005ca7e]),
]:
    w = word(pc)
    assert w & 127 == 0x63
    imm = ((w >> 31) << 12) | ((w >> 7 & 1) << 11) | ((w >> 25 & 63) << 5) | ((w >> 8 & 15) << 1)
    got = [w >> 12 & 7, w >> 15 & 31, w >> 20 & 31, (pc + sx(imm, 13)) & 0xffffffff]
    assert got == fields
    checks.append(dict(address=hex(pc), kind='branch', fields=got))

pairs = []
for pc, target in [(0xa005ca12, 0xa01b2b5c), (0xa005ca22, 0xa01b2b5c),
                   (0xa005ca32, 0xa01b2cb0), (0xa005ca56, 0xa01aca1a),
                   (0xa005ca6e, 0xa01aca1a)]:
    u, j = word(pc), word(pc + 4)
    assert u & 127 == 0x17 and (u >> 7 & 31) == 1
    assert j & 0x707f == 0x67 and (j >> 7 & 31) == 1 and (j >> 15 & 31) == 1
    got = (pc + sx(u & 0xfffff000, 32) + sx(j >> 20, 12)) & 0xfffffffe
    assert got == target
    pairs.append(dict(address=hex(pc), target=hex(got), kind='auipc-ra/jalr-ra-ra'))

tail = windows[2]['instructions']
tail_calls = []
tail_branches = []
for i in tail:
    pc = int(i['address'], 16)
    w = word(pc)
    if len(i['hex']) == 8 and w & 127 == 0x63:
        tail_branches.append(i['address'])
    if len(i['hex']) == 8 and w & 127 == 0x6f:
        assert w >> 7 & 31 == 1  # all JALs in tail are calls, not unconditional local jumps
        imm = ((w >> 31) << 20) | ((w >> 12 & 255) << 12) | ((w >> 20 & 1) << 11) | ((w >> 21 & 1023) << 1)
        tail_calls.append(dict(address=hex(pc), target=hex((pc + sx(imm, 21)) & 0xffffffff)))
    if pc != 0xa005cad0:
        assert not i['decode'].startswith(('c.j ', 'c.jr ', 'c.jalr ', 'j '))
    if 'jalr' in i['decode']:
        assert pc - 4 in [int(p['address'], 16) for p in pairs] or pc == 0xa005cad0
assert len(tail_branches) == 6
assert len(tail_calls) == 12
assert all(c['target'] in ['0xa008b51a', '0xa009fb96'] for c in tail_calls)
assert rom[0xa005cad0 - BASE:0xa005cad2 - BASE].hex() == '8280'
assert tail[-1]['address'] == '0xa005cad0'

result = dict(task='C07', rom_path=str(ROM), va_base=hex(BASE),
    retained_initializer_evidence_id=retained['evidence_id'], windows=windows,
    raw_branch_checks=checks, resolved_call_pairs=pairs, tail_jal_calls=tail_calls,
    validation=dict(selected_bytes=sum(len(bytes.fromhex(i['hex'])) for w in windows for i in w['instructions']),
        undecoded_selected_bytes=0, retained_raw_ranges_match=True, branch_checks=len(checks),
        pair_checks=len(pairs), tail_branch_count=len(tail_branches), tail_jal_call_count=len(tail_calls),
        tail_all_local_branches_forward=True, tail_return_at='0xa005cad0', firmware_executed=False),
    limitations=['Direct intraprocedural tail only; calls are opaque and their return is conditional.',
        'No proof of callback liveness, absence, caller reinvocation, whole loop or timer lifecycle.',
        'No new source/version attribution or open-source exclusion.'])
(HERE / 'instruction-evidence.json').write_text(json.dumps(result, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
print(json.dumps(result['validation']))
