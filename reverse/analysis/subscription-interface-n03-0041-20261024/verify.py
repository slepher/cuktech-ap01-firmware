"""N03 bounded static evidence: retained anchors and two new glue fragments only.

Reads the main checkout's ROM and retained JSON; writes only beside this file.
Does not run firmware, historical verifiers, REA, instruction models, or builds.
"""
import json
import re
from pathlib import Path
from capstone import Cs, CS_ARCH_RISCV, CS_MODE_RISCV32, CS_MODE_RISCVC

MAIN = Path('D:/Documents/PlatformIO/Projects/cuktech-ap01-firmware')
OUT = Path(__file__).resolve().parent
BASE = 0x9ffff000
rom = (MAIN / 'roms/0041/ap01-1.0.2_0041.bin').read_bytes()
checks = []
anchors = []


def check(name, actual, expected):
    assert actual == expected, (name, actual, expected)
    checks.append({'name': name, 'actual': actual, 'expected': expected})


def retained(relative, selected):
    data = json.loads((MAIN / relative).read_text(encoding='utf-8'))
    for wi, window in enumerate(data['windows']):
        if window['name'] not in selected:
            continue
        for ii, ins in enumerate(window['instructions']):
            address = int(ins['address'], 16)
            raw = bytes.fromhex(ins['hex'])
            check(f'retained byte {address:#x}', rom[address-BASE:address-BASE+len(raw)].hex(), raw.hex())
            anchors.append({'source': relative, 'pointer': f'/windows/{wi}/instructions/{ii}',
                            'address': ins['address'], 'hex': raw.hex(),
                            'assembly': ins.get('assembly'),
                            'vendor_inherited': ins.get('vendor'),
                            'fields_inherited': ins.get('fields')})


retained('reverse/analysis/uiiface-lifecycle-0041-20261023/instruction-windows.json',
         {'control_register', 'control_remove', 'consumer_register_app',
          'consumer_register_ui', 'consumer_register_page'})
retained('reverse/analysis/mode-control-0041-20261023/instruction-windows.json', {'control_dispatch'})
retained('reverse/analysis/ctk-app-close-review-e06-0041-20261023/independent-checks.json',
         {'other_remover_state_origin', 'same_head_other_key_remover'})


def legacy_lines(relative, pointer, lo, hi):
    data = json.loads((MAIN / relative).read_text(encoding='utf-8'))
    for part in pointer.strip('/').split('/'):
        data = data[int(part)] if isinstance(data, list) else data[part]
    result = []
    for line in data.splitlines():
        match = re.match(r'\s*([a-fA-F0-9]{8}):\s+([a-fA-F0-9]{4,8})\s+(.*)', line)
        if not match:
            continue
        address = int(match[1], 16)
        if not lo <= address < hi:
            continue
        encoded = match[2]
        raw = int(encoded, 16).to_bytes(len(encoded)//2, 'little')
        check(f'legacy byte {address:#x}', rom[address-BASE:address-BASE+len(raw)].hex(), raw.hex())
        result.append({'source': relative, 'pointer': pointer, 'address': hex(address),
                       'hex': raw.hex(), 'assembly': match[3]})
    assert result, (relative, pointer, hex(lo))
    anchors.extend(result)
    return result


legacy_lines('reverse/rehost/weather-calendar-complete-0041.json', '/evidence/22/stdout',
             0xa00a4edc, 0xa00a4f82)
legacy_lines('reverse/rehost/guide-complete-0041.json',
             '/bounded_local_disassembly/saver_window_asm', 0xa00a79ce, 0xa00a7a1c)

# New bounded glue: previous lifecycle evidence stops at 0xa00b0774;
# E06 retained DELETE begins at 0xa00f2f54. Neither range follows new callees.
decoder = Cs(CS_ARCH_RISCV, CS_MODE_RISCV32 | CS_MODE_RISCVC)
windows = []
for lo, hi in [(0xa00b0774, 0xa00b07c8), (0xa00f2f38, 0xa00f2f54)]:
    instructions = []
    cursor = lo
    while cursor < hi:
        first = rom[cursor-BASE]
        width = 4 if first & 3 == 3 else 2
        raw = rom[cursor-BASE:cursor-BASE+width]
        decoded = list(decoder.disasm(raw, cursor))
        assert len(decoded) == 1 and decoded[0].size == width
        ins = decoded[0]
        instructions.append({'address': hex(cursor), 'file_offset': cursor-BASE,
                             'hex': raw.hex(), 'assembly': ins.mnemonic+' '+ins.op_str})
        cursor += width
    check(f'new boundary {lo:#x}', cursor, hi)
    windows.append({'start': hex(lo), 'end_exclusive': hex(hi), 'instructions': instructions})


def word(address):
    return int.from_bytes(rom[address-BASE:address-BASE+4], 'little')


def sext(number, bits):
    return number - (1 << bits) if number >> (bits-1) else number


def jal(address):
    value = word(address)
    check(f'jal opcode {address:#x}', value & 0x7f, 0x6f)
    immediate = ((value >> 31) << 20 | ((value >> 12) & 255) << 12 |
                 ((value >> 20) & 1) << 11 | ((value >> 21) & 1023) << 1)
    return (address + sext(immediate, 21)) & 0xffffffff


def lui_addi(a, b):
    x, y = word(a), word(b)
    check(f'lui opcode {a:#x}', x & 0x7f, 0x37)
    check(f'addi opcode {b:#x}', y & 0x707f, 0x13)
    check(f'constant register continuity {a:#x}', (x >> 7) & 31, (y >> 15) & 31)
    return ((x & 0xfffff000) + sext(y >> 20, 12)) & 0xffffffff


def auipc_jalr(a, b):
    x, y = word(a), word(b)
    check(f'auipc opcode {a:#x}', x & 0x7f, 0x17)
    check(f'jalr opcode {b:#x}', y & 0x707f, 0x67)
    check(f'call register continuity {a:#x}', (x >> 7) & 31, (y >> 15) & 31)
    return ((a + (x & 0xfffff000) + sext(y >> 20, 12)) & 0xffffffff) & ~1


check('detail control key', lui_addi(0xa00b075e, 0xa00b0768), 0xa00f3952)
check('detail control register', auipc_jalr(0xa00b076c, 0xa00b0770), 0xa01b29a0)
check('detail item key', lui_addi(0xa00b0774, 0xa00b077a), 0xa00f5288)
check('detail item register', auipc_jalr(0xa00b077e, 0xa00b0782), 0xa01b28ce)
check('detail DELETE key', lui_addi(0xa00b07b4, 0xa00b07be), 0xa00f2f38)
check('detail DELETE installer', jal(0xa00b07c4), 0xa01ad654)
check('detail DELETE filter29', word(0xa00b07ba), 0x02900613)
for address, raw in [(0xa00b0766, 'd685'), (0xa00b0778, 'd685'),
                     (0xa00b07b8, '8146'), (0xa00b07c2, '5685')]:
    check(f'detail shared userdata/event ABI {address:#x}',
          rom[address-BASE:address-BASE+2].hex(), raw)
check('detail DELETE ignores bit15 then filter29 branch', word(0xa00f2f44), 0x08e79663)
check('detail remove control key', lui_addi(0xa00f2f8c, 0xa00f2f90), 0xa00f3952)
check('detail remove control call', jal(0xa00f2f94), 0xa01b2966)
check('detail remove item key', lui_addi(0xa00f2fa4, 0xa00f2fa8), 0xa00f5288)
check('detail item unlink', jal(0xa00f2fba), 0xa0089d02)
check('detail free adapter', jal(0xa00f2fc0), 0xa008ab8a)
check('detail free uses saved state s2', rom[0xa00f2fbe-BASE:0xa00f2fc0-BASE].hex(), '4a85')
check('saver unregister pair', auipc_jalr(0xa00a4f5c, 0xa00a4f60), 0xa01b2966)
check('saver unregister key', lui_addi(0xa00a4f54, 0xa00a4f58), 0xa00ac54e)

result = {'claim': 'N03', 'status': 'PASS', 'base': hex(BASE),
          'rom': str(MAIN / 'roms/0041/ap01-1.0.2_0041.bin'),
          'rom_identity_inherited': '972db4c136c7ed9e24a83c07c1a7fd62040ca018b08ca285216d26b1fee3c6b9',
          'engine': 'Capstone static RV32/RVC; new windows contain no custom0; retained vendor semantics inherited',
          'check_count': len(checks), 'retained_anchor_count': len(anchors),
          'new_window_bytes': sum(int(w['end_exclusive'],16)-int(w['start'],16) for w in windows),
          'checks': checks, 'retained_anchors': anchors, 'new_glue_windows': windows,
          'limitations': ['No target execution or new REA evidence.', 'Static event installation is an attempt, not runtime delivery.',
                         'No node reclamation, callback mutation, thread/quiescence guarantee, or main-app exit recovered.']}
(OUT / 'static-checks.json').write_text(json.dumps(result, ensure_ascii=False, indent=2)+'\n', encoding='utf-8')
print(json.dumps({k: result[k] for k in ['status','check_count','retained_anchor_count','new_window_bytes']}))
