"""Bounded Q-28 static evidence comparison; no firmware/model execution."""
import hashlib
import json
from pathlib import Path
from capstone import Cs, CS_ARCH_RISCV, CS_MODE_RISCV32, CS_MODE_RISCVC

ROOT = Path('D:/Documents/PlatformIO/Projects/cuktech-ap01-firmware')
AUTHOR = Path('D:/CodexHome/visualizations/2026/10/24/01a16ec4-7aa8-7b43-a0e8-609e1021781b/ap01-s/ddf01')
OUT = Path(__file__).resolve().parent
rom = (ROOT / 'roms/0041/ap01-1.0.2_0041.bin').read_bytes()
assert len(rom) == 6769704
assert hashlib.sha256(rom).hexdigest() == '972db4c136c7ed9e24a83c07c1a7fd62040ca018b08ca285216d26b1fee3c6b9'
evidence = json.loads((AUTHOR / 'reverse/analysis/app-ddf-research-01-0041-20261025/instructions.json').read_text(encoding='utf-8'))
cs = Cs(CS_ARCH_RISCV, CS_MODE_RISCV32 | CS_MODE_RISCVC)
total = count = 0
rows = {}
for window in evidence['windows']:
    start, end = int(window['start'], 16), int(window['end_exclusive'], 16)
    cursor = start
    for row in window['rows']:
        pc = int(row['pc'], 16)
        raw = bytes.fromhex(row['raw'])
        assert pc == cursor
        assert rom[pc-0x9ffff000:pc-0x9ffff000+len(raw)] == raw
        decoded = list(cs.disasm(raw, pc, count=1))
        assert len(decoded) == 1 and decoded[0].size == len(raw)
        assert (decoded[0].mnemonic + ' ' + decoded[0].op_str).strip() == row['asm']
        rows[pc] = row
        cursor += len(raw)
        count += 1
    assert cursor == end
    total += end-start
assert (total, count) == (1924, 573)
# Decode I-immediates directly from ROM for the only author correction.
def immediate(pc):
    w = int.from_bytes(rom[pc-0x9ffff000:pc-0x9ffff000+4], 'little')
    assert w & 0x707f == 0x13
    n = w >> 20
    return n - 4096 if n & 2048 else n
assert immediate(0xa00c7114) == 36
assert immediate(0xa00c711a) == -0x164
assert immediate(0xa00c713c) == -0x168
assert immediate(0xa00c711a)-immediate(0xa00c713c) == 4
result = {'claim': 'Q-28/S43', 'rom_bytes': len(rom), 'rom_sha256': hashlib.sha256(rom).hexdigest(), 'compared_bytes': total, 'decoded_instructions': count, 'raw_and_decode_match': True, 'descriptor_zero_start_offset': 4, 'descriptor_zero_bytes': 36, 'author_script_executed': False}
(OUT / 'checks.json').write_text(json.dumps(result, indent=2)+'\n', encoding='utf-8')
print(json.dumps(result))
