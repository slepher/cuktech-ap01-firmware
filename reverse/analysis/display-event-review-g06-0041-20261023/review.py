"""Independent G06 ROM-only extraction. No firmware, historical validator or model execution."""
from pathlib import Path
import json
import capstone

ROOT = Path(__file__).resolve().parent
ROM = Path('D:/Documents/PlatformIO/Projects/cuktech-ap01-firmware/roms/0041/ap01-1.0.2_0041.bin')
IMAGE = ROM.read_bytes()
BASE = 0x9ffff000
decoder = capstone.Cs(capstone.CS_ARCH_RISCV, capstone.CS_MODE_RISCV32 | capstone.CS_MODE_RISCVC)

def signed(v, width):
    return v - (1 << width) if v & (1 << (width - 1)) else v

def read(a, n):
    assert 0 <= a - BASE <= len(IMAGE) - n
    return IMAGE[a - BASE:a - BASE + n]

def target(a, raw):
    w = int.from_bytes(raw, 'little')
    if len(raw) == 2:
        f = w >> 13
        if w & 3 == 1 and f in (1, 5):
            imm = ((w >> 12 & 1) << 11 | (w >> 11 & 1) << 4 | (w >> 9 & 3) << 8 |
                   (w >> 8 & 1) << 10 | (w >> 7 & 1) << 6 | (w >> 6 & 1) << 7 |
                   (w >> 3 & 7) << 1 | (w >> 2 & 1) << 5)
            return (a + signed(imm, 12)) & 0xffffffff
        if w & 3 == 1 and f in (6, 7):
            imm = ((w >> 12 & 1) << 8 | (w >> 10 & 3) << 3 | (w >> 5 & 3) << 6 |
                   (w >> 3 & 3) << 1 | (w >> 2 & 1) << 5)
            return (a + signed(imm, 9)) & 0xffffffff
    elif w & 127 == 0x63:
        imm = ((w >> 31) << 12 | (w >> 7 & 1) << 11 | (w >> 25 & 63) << 5 | (w >> 8 & 15) << 1)
        return (a + signed(imm, 13)) & 0xffffffff
    elif w & 127 == 0x6f:
        imm = ((w >> 31) << 20 | (w >> 12 & 255) << 12 | (w >> 20 & 1) << 11 | (w >> 21 & 1023) << 1)
        return (a + signed(imm, 21)) & 0xffffffff
    elif w & 127 == 0x17:
        nxt = int.from_bytes(read(a + 4, 4), 'little')
        # Require JALR base to be the AUIPC destination; unrelated adjacent pairs do not count.
        if nxt & 127 == 0x67 and (nxt >> 15 & 31) == (w >> 7 & 31):
            return (a + signed(w & 0xfffff000, 32) + signed(nxt >> 20, 12)) & 0xfffffffe
    return None

SPANS = [
    ('identity', 0xa0084da6, 0xa0084daa), ('init_and_timer', 0xa0084de8, 0xa0084eea),
    ('install38', 0xa0086b98, 0xa0086bc6), ('reload_timer', 0xa00872e8, 0xa00872ee),
    ('replace_cb', 0xa00873b6, 0xa00873c6), ('register_wrapper', 0xa007ffa0, 0xa0080002),
    ('callback38', 0xa0080002, 0xa0080030), ('descriptor', 0xa01b93b4, 0xa01b951c),
    ('event_frame', 0xa00814f4, 0xa0081554), ('dispatch', 0xa008acfa, 0xa008adf4),
    ('timer_create_pause_resume', 0xa008bc64, 0xa008bdd4), ('notify', 0xa0087b06, 0xa0087b30),
    ('scheduler', 0xa00804e2, 0xa00806d0), ('poll_adapter', 0xa0080da6, 0xa0080dfe),
    ('backend_getter', 0xa007fe32, 0xa007fe4e), ('consumer_entry', 0xa00e0ac8, 0xa00e0b04),
    ('consumer_default', 0xa00e0b3c, 0xa00e0b4a),
    ('delete_events', 0xa0081554, 0xa008158a), ('delete_timer', 0xa00815c8, 0xa0081604),
    ('unregister_all', 0xa008b7f0, 0xa008b888), ('event_cleanup', 0xa008ac38, 0xa008acfa),
    ('timer_remove_free', 0xa008ae58, 0xa008ae8c),
]
rows = {}
windows = []
for name, start, end in SPANS:
    address = start
    part = []
    while address < end:
        size = 4 if read(address, 2)[0] & 3 == 3 else 2
        raw = read(address, size)
        assert address + size <= end, (name, hex(address))
        ins = next(decoder.disasm(raw, address), None)
        w = int.from_bytes(raw, 'little')
        row = {'address': hex(address), 'offset': hex(address - BASE), 'bytes': raw.hex(),
               'instruction': f'{ins.mnemonic} {ins.op_str}'.strip() if ins else 'vendor/undecoded',
               'target': hex(target(address, raw)) if target(address, raw) is not None else None}
        if ins is None:
            row['fields'] = {'opcode': w & 127, 'rd': w >> 7 & 31, 'rs1': w >> 15 & 31,
                             'rs2': w >> 20 & 31, 'funct3': w >> 12 & 7, 'funct7': w >> 25}
        rows[address] = row
        part.append(row)
        address += size
    windows.append({'name': name, 'start': hex(start), 'end_exclusive': hex(end), 'rows': part})

# Read the new listing before adding contract checks. Expected values are kept separate from decode output.
listing = '\n'.join('\n' + w['name'] + '\n' + '\n'.join(
    f"{r['address']} @{r['offset']} {r['bytes']:8} {r['instruction']} {r['target'] or ''}".rstrip()
    for r in w['rows']) for w in windows)
(ROOT / 'instructions.txt').write_text(listing, encoding='utf-8')
checks = []
def check(pc, key, expected):
    actual = rows[pc][key]
    assert actual == expected, (hex(pc), key, actual, expected)
    checks.append({'address': hex(pc), 'field': key, 'expected': expected})

for pc, dest in {
    0xa0084ee2: 0xa008bc64, 0xa0086bba: 0xa007ffa0, 0xa007fff0: 0xa01b93b4,
    0xa0080022: 0xa008bd70, 0xa008bdc6: 0xa0087b06, 0xa0080594: 0xa008b236,
    0xa00805b0: 0xa008b17e, 0xa0080ddc: 0xa003f546, 0xa0080dee: 0xa00e0ac8,
    0xa00e0af4: 0xa008bd16, 0xa0081586: 0xa008b7f0, 0xa00815e4: 0xa008ae58,
    0xa008ae6e: 0xa0089d02, 0xa008ae7e: 0xa008ab8a,
    0xa008000e: 0xa008002e, 0xa0080018: 0xa008002e,
    0xa00872ec: 0xa00873b6, 0xa0081538: 0xa0081548,
    0xa008ad76: 0xa008ad6c, 0xa008ad7c: 0xa008ad6c,
    0xa008ad8a: 0xa008ad6c, 0xa008ada2: 0xa008adae,
    0xa008ad5c: 0xa008ada8, 0xa008ad1e: 0xa008adc4,
    0xa0087b16: 0xa0087b2e, 0xa008058c: 0xa00805f0,
    0xa008059c: 0xa00805c8, 0xa00805a4: 0xa00805b0,
    0xa00805be: 0xa00805c8, 0xa00805c0: 0xa00805c8,
    0xa00805cc: 0xa00805e2, 0xa00805d2: 0xa00805e2,
    0xa00805dc: 0xa00805f4, 0xa0080de0: 0xa0080df2,
    0xa0080dea: 0xa0080df2, 0xa008acce: 0xa008acf8,
    0xa008acd2: 0xa008acf8, 0xa008acae: 0xa008ab8a,
    0xa00815e2: 0xa00815e8, 0xa00e0aee: 0xa00e0b3c,
}.items():
    check(pc, 'target', hex(dest))

for pc, asm in {
    0xa0084da6: 'c.mv s1, a0', 0xa0084ed2: 'c.mv a2, s1',
    0xa0084ed4: 'c.li a1, 0x10', 0xa0084eca: 'lui a0, 0xa00e1',
    0xa0084ed6: 'addi a0, a0, -0x538', 0xa0084ee6: 'sw a0, 8(s3)',
    0xa0084e94: 'addi s3, s1, 0x300', 0xa0086baa: 'c.li a3, 0',
    0xa0086bac: 'addi a2, zero, 0x38', 0xa0086bb0: 'addi a1, a1, 2',
    0xa0086bb4: 'c.mv a0, s1', 0xa007ffec: 'addi a0, a0, 0x2e8',
    0xa00873ba: 'addi a5, a5, -0x25a', 0xa00873be: 'c.sw a5, 8(a4)',
    0xa01b9432: 'c.sw a1, 0(a0)', 0xa01b9438: 'c.sw a2, 8(a5)',
    0xa01b943a: 'c.sw a3, 4(a5)', 0xa0080012: 'c.lw a5, 4(a0)',
    0xa0080014: 'lw a0, 0x308(a5)', 0xa008ad50: 'c.addi s5, -1',
    0xa008ad92: 'sw a5, 0xc(s3)', 0xa008ad98: 'c.jalr a5',
    0xa008adae: 'c.li s1, 1', 0xa008bccc: 'c.li a5, -1',
    0xa008bcce: 'c.sw a5, 0x10(a0)', 0xa008bcd4: 'c.sw a1, 0(a0)',
    0xa008bcd6: 'sw s3, 8(a0)', 0xa008bcea: 'c.sw a0, 4(s1)',
    0xa008bcec: 'sw s2, 0xc(s1)', 0xa008bcf0: 'ori a5, a5, 2',
    0xa008bdc0: 'c.andi a5, -2', 0xa008bdc2: 'sb a5, 0x14(a0)',
    0xa008bd66: 'ori a5, a5, 1', 0xa0087b0e: 'lw a4, 0x9c(a5)',
    0xa0087b12: 'sw zero, 0x84(a5)', 0xa0087b20: 'lw a0, 0xa0(a5)',
    0xa0087b24: 'c.jalr a4', 0xa00805a0: 'lw s9, 0x10(s2)',
    0xa00805ac: 'sw a5, 0x10(s2)', 0xa00805b4: 'lw a5, 8(s2)',
    0xa00805b8: 'sw a0, 4(s2)', 0xa00805c4: 'c.mv a0, s2',
    0xa00805c6: 'c.jalr a5', 0xa0080db4: 'c.lw a0, 0xc(a0)',
    0xa007fe44: 'lw a0, 0x2e0(a0)', 0xa0080dce: 'sw a5, -0x28(s0)',
    0xa0080dd8: 'sw a5, -0x24(s0)', 0xa0080de4: 'lw a5, -0x20(s0)',
    0xa0080de8: 'c.andi a5, 4', 0xa00e0af0: 'c.lw a5, 0xc(a0)',
    0xa008b884: 'c.sw a5, 8(a4)', 0xa00815de: 'lw a0, 0x308(s1)',
    0xa008ae7a: 'sb a4, 0x5fe(a5)',
}.items():
    check(pc, 'instruction', asm)

model = Path('D:/Documents/PlatformIO/Projects/cuktech-ap01-firmware/evidence/rea-0041-20261017/ghidra/Ghidra/Processors/RISCV/data/languages/ap01thead2.sinc')
text = model.read_text(encoding='utf-8')
vendor_contracts = {}
for needle in (':th.mula rd,rs1,rs2 ', ':th.extu rd,rs1,15,15 ', ':th.mveqz rd,rs1,rs2 ', ':th.mvnez rd,rs1,rs2 '):
    begin = text.index(needle)
    vendor_contracts[needle] = text[begin:text.index('\n}', begin) + 2]
for pc, value, fields in [
    (0xa01b94f2, '0b15f620', {'opcode': 11, 'rd': 10, 'rs1': 12, 'rs2': 15, 'funct3': 1, 'funct7': 16}),
    (0xa008ad78, '8bb6f73c', {'opcode': 11, 'rd': 13, 'rs1': 15, 'rs2': 15, 'funct3': 3, 'funct7': 30}),
    (0xa0086ba6, '8b976441', {'opcode': 11, 'rd': 15, 'rs1': 9, 'rs2': 22, 'funct3': 1, 'funct7': 32}),
    (0xa008061c, '0b99e742', {'opcode': 11, 'rd': 18, 'rs1': 15, 'rs2': 14, 'funct3': 1, 'funct7': 33}),
]:
    check(pc, 'bytes', value)
    check(pc, 'fields', fields)

result = {'rom_read_only': str(ROM), 'mapping': 'file offset = VA - 0x9ffff000',
          'decoder': f'Capstone {capstone.__version__} RISCV32/RVC',
          'windows': windows, 'checks': checks, 'vendor_model_read_only': str(model),
          'vendor_contract_text': vendor_contracts,
          'coverage': {'windows': len(windows), 'instructions': len(rows), 'checks': len(checks)}}
# A bounded register-definition audit supports the selected constructor identity;
# retain only s1 definitions and nearby instructions, rather than another whole constructor dump.
audit = []
address = 0xa0084da6
while address < 0xa00873c0:
    size = 4 if read(address, 2)[0] & 3 == 3 else 2
    raw = read(address, size)
    ins = next(decoder.disasm(raw, address), None)
    w = int.from_bytes(raw, 'little')
    audit.append({'address': hex(address), 'bytes': raw.hex(),
                  'instruction': f'{ins.mnemonic} {ins.op_str}' if ins else 'vendor/undecoded',
                  'target': hex(target(address, raw)) if target(address, raw) is not None else None,
                  'definition_candidate': bool((ins and ins.op_str.startswith('s1,') and
                     not ins.mnemonic.startswith(('b', 'sb', 'sh', 'sw', 'c.sw'))) or
                     (not ins and (w >> 7 & 31) == 9))})
    address += size
selected = set()
for index, item in enumerate(audit):
    if item['definition_candidate']:
        selected.update(range(max(0, index - 3), min(len(audit), index + 16)))
result['constructor_s1_audit'] = {
    'start': '0xa0084da6', 'end_exclusive': '0xa00873c0', 'decoded_instructions': len(audit),
    'limitation': 'Linear definition candidates plus context; not whole-CFG reachability or callee proof.',
    'rows': [audit[i] for i in sorted(selected)]}
(ROOT / 'evidence.json').write_text(json.dumps(result, ensure_ascii=False, indent=2), encoding='utf-8')
print(json.dumps(result['coverage']))
