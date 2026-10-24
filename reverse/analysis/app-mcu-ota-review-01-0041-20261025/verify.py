"""Independent read-only ROM review; never imports or executes author code."""
from pathlib import Path
import hashlib
import json
import struct
from capstone import Cs, CS_ARCH_RISCV, CS_MODE_RISCV32, CS_MODE_RISCVC

ROOT = Path('D:/Documents/PlatformIO/Projects/cuktech-ap01-firmware')
OUT = Path(__file__).resolve().parent
rom = (ROOT / 'roms/0041/ap01-1.0.2_0041.bin').read_bytes()
assert len(rom) == 6769704
assert hashlib.sha256(rom).hexdigest() == '972db4c136c7ed9e24a83c07c1a7fd62040ca018b08ca285216d26b1fee3c6b9'
base = 0x9ffff000
windows = [(0xa006fbe8, 1230), (0xa0074b22, 114), (0xa007019e, 88), (0xa00702a6, 124), (0xa0070390, 62), (0xa006faca, 20)]
cs = Cs(CS_ARCH_RISCV, CS_MODE_RISCV32 | CS_MODE_RISCVC)
lines, evidence = [], []
for start, length in windows:
    data = rom[start-base:start-base+length]
    instructions = list(cs.disasm(data, start))
    assert sum(i.size for i in instructions) == length
    assert instructions[-1].address + instructions[-1].size == start + length
    lines.append(f'\nWINDOW {start:08x} {length}')
    for i in instructions:
        lines.append(f'{i.address:08x} {i.bytes.hex():8} {i.mnemonic} {i.op_str}')
    evidence.append({'start': hex(start), 'bytes': length, 'sha256': hashlib.sha256(data).hexdigest(), 'instructions': len(instructions)})
table = rom[0xa01bb0e8-base:0xa01bb0e8-base+28]
assert struct.unpack('<7I', table) == (0xa006fbe8, 0xa0074b22, 0xa007019e, 0xa00702a6, 0xa0074ea2, 0xa0070390, 0xa006faca)
# Absolute author tree supplied by the parent; plain JSON data, no author code.
author_dir = Path('D:/CodexHome/visualizations/2026/10/24/01a16ec4-7aa8-7b43-a0e8-609e1021781b/ap01-s/mcu-ota01/reverse/analysis/app-mcu-ota-research-01-0041-20261025')
author_raw = json.loads((author_dir / 'raw.json').read_text())
for ours, theirs in zip(evidence, author_raw['functions'], strict=True):
    assert ours['start'] == theirs['start'] and ours['bytes'] == theirs['size'] and ours['sha256'] == theirs['sha256']
    for instruction in theirs['instructions']:
        offset = int(instruction['address'], 16) - base
        raw = bytes.fromhex(instruction['raw'])
        assert rom[offset:offset+len(raw)] == raw
boundary = json.loads((author_dir / 'boundary-evidence.json').read_text())
for item in boundary['strings']:
    offset = int(item['address'], 16) - base
    expected = bytes.fromhex(item['hex'])
    assert rom[offset:offset+len(expected)] == expected
    assert expected.rstrip(b'\0').decode() == item['text']
# Necessary old registration anchors only; no old completed slot body.
for start, length in [(0xa006462e, 4), (0xa0065fe4, 4), (0xa00661f2, 42)]:
    lines.append(f'\nREGISTRATION {start:08x}')
    for i in cs.disasm(rom[start-base:start-base+length], start):
        lines.append(f'{i.address:08x} {i.bytes.hex():8} {i.mnemonic} {i.op_str}')
(OUT / 'review-disassembly.txt').write_text('\n'.join(lines), encoding='utf-8')
(OUT / 'review-checks.json').write_text(json.dumps({'rom_sha256': hashlib.sha256(rom).hexdigest(), 'table': table.hex(), 'new_body_bytes': sum(n for _, n in windows), 'author_raw_matches': True, 'string_matches': len(boundary['strings']), 'windows': evidence}, indent=2), encoding='utf-8')
print('\n'.join(lines))
