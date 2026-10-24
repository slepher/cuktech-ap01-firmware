"""Independent static byte/decode checks; never imports or executes author code."""
from pathlib import Path
import hashlib
import json
import struct
from capstone import Cs, CS_ARCH_RISCV, CS_MODE_RISCV32, CS_MODE_RISCVC

ROOT = Path('D:/Documents/PlatformIO/Projects/cuktech-ap01-firmware')
AUTHOR = Path('D:/CodexHome/visualizations/2026/10/24/01a16ec4-7aa8-7b43-a0e8-609e1021781b/ap01-s/serial-uplink01')
STEM = 'app-serial-uplink-research-01-0041-20261025'
rom = (ROOT / 'roms/0041/ap01-1.0.2_0041.bin').read_bytes()
assert len(rom) == 6769704
assert hashlib.sha256(rom).hexdigest() == '972db4c136c7ed9e24a83c07c1a7fd62040ca018b08ca285216d26b1fee3c6b9'
evidence = ROOT / 'reverse/analysis' / STEM
if not (evidence / 'instructions.json').exists():
    evidence = AUTHOR / 'reverse/analysis' / STEM
rows = json.loads((evidence / 'instructions.json').read_text())
expected = {int(r['va'], 16): r for r in rows}
decoder = Cs(CS_ARCH_RISCV, CS_MODE_RISCV32 | CS_MODE_RISCVC)
windows = [(0xa00be6d8, 0xa00be8a0), (0xa00ba8b2, 0xa00ba994), (0xa00ba536, 0xa00ba5be)]
decoded = {}
unknown = []
for start, end in windows:
    pc = start
    while pc < end:
        off = pc - 0x9ffff000
        size = 4 if rom[off] & 3 == 3 else 2
        raw = rom[off:off + size]
        assert expected[pc]['offset'] == off and expected[pc]['hex'] == raw.hex()
        ins = list(decoder.disasm(raw, pc))
        if not ins or ins[0].size != size:
            unknown.append((hex(pc), raw.hex()))
        else:
            decoded[pc] = ins[0].mnemonic + ' ' + ins[0].op_str
            assert decoded[pc] == expected[pc]['asm']
        pc += size
    assert pc == end
assert len(decoded) + len(unknown) == len(rows)
assert unknown == [('0xa00be880', '8b452b45')]
assert sum(b-a for a,b in windows) == 818

def word(va):
    return struct.unpack_from('<I', rom, va - 0x9ffff000)[0]

def signed(value, bits):
    return value - (1 << bits) if value & (1 << (bits - 1)) else value

lui, addi = word(0xa00be82a), word(0xa00be82e)
assert lui & 0x7f == 0x37 and (lui >> 7) & 31 == 15
assert addi & 0x7f == 0x13 and (addi >> 7) & 31 == 15 and (addi >> 15) & 31 == 15
callback = ((lui & 0xfffff000) + signed(addi >> 20, 12)) & 0xffffffff
assert callback == 0xa00ba8b2
stores = []
for va in expected:
    w = word(va)
    if w & 0x7f == 0x23:
        stores.append((va, (w >> 15) & 31, (w >> 20) & 31,
                       signed(((w >> 25) << 5) | ((w >> 7) & 31), 12), (w >> 12) & 7))
busy = [(hex(v), base, source, offset, width) for v,base,source,offset,width in stores if offset == 0x1fc]
assert busy == [('0xa00ba97e', 19, 15, 508, 0), ('0xa00ba5ac', 9, 10, 508, 0)]
strings = json.loads((evidence / 'strings.json').read_text())
for address, value in strings.items():
    off = int(address, 16) - 0x9ffff000
    assert rom[off:rom.index(b'\0', off)].decode() == value
print(json.dumps({'bytes': 818, 'instructions': len(rows), 'unknown': unknown,
                  'callback': hex(callback), 'busy_stores': busy,
                  'strings_checked': len(strings), 'all_author_rows_match_rom_and_decode': True}, indent=2))
