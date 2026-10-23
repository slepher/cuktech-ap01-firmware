"""A32 independent, read-only sparse review; no firmware execution."""
from pathlib import Path
import json
import capstone

HERE = Path(__file__).resolve().parent
ROM = Path('D:/Documents/PlatformIO/Projects/cuktech-ap01-firmware/roms/0041/ap01-1.0.2_0041.bin')
data = ROM.read_bytes()
cs = capstone.Cs(capstone.CS_ARCH_RISCV, capstone.CS_MODE_RISCV32 | capstone.CS_MODE_RISCVC)
# Selected independently by the ABI/data-flow questions; not a function export.
anchors = [
    (0xa00f0d6c, 'aa84', 'c.mv s1, a0'),
    (0xa00f0dea, '01cd', 'c.beqz a0, 0x18'),
    (0xa00f0df0, 'b7a70ea0', 'lui a5, 0xa00ea'),
    (0xa00f0df4, '9387e75b', 'addi a5, a5, 0x5be'),
    (0xa00f0e00, 'dcdc', 'c.sw a5, 0x3c(s1)'),
    (0xa00ea5be, '411122c600083244084141018280', None),
    (0xa00ebbee, '2e8c', 'c.mv s8, a1'),
    (0xa00ebc30, '2a89', 'c.mv s2, a0'),
    (0xa00ebdea, '032a4900', 'lw s4, 4(s2)'),
    (0xa00ebdee, 'e285', 'c.mv a1, s8'),
    (0xa00ebdf0, '2685', 'c.mv a0, s1'),
    (0xa00ebdf2, '5286', 'c.mv a2, s4'),
    (0xa00ebdf4, 'efe039d8', None),
    (0xa008ab7e, 'efa0f7d1', None),
    (0xa00ebe1e, '85c0', 'c.beqz s1, 0x20'),
    (0xa00ebe20, '8448', 'c.lw s1, 0x10(s1)'),
    (0xa00ebe26, 'e38804ec', 'beqz s1, -0x130'),
    (0xa00ebe2c, '8327c903', 'lw a5, 0x3c(s2)'),
    (0xa00ebe30, '6285', 'c.mv a0, s8'),
    (0xa00ebe32, '8297', 'c.jalr a5'),
    (0xa00ebe34, '8327c900', 'lw a5, 0xc(s2)'),
    (0xa00ebe38, 'aa97', 'c.add a5, a0'),
    (0xa00ebe3a, '2326f900', 'sw a5, 0xc(s2)'),
    (0xa00ebf60, 'dc5c', 'c.lw a5, 0x3c(s1)'),
    (0xa00ebf62, '4a85', 'c.mv a0, s2'),
    (0xa00ebf64, '8297', 'c.jalr a5'),
    (0xa00ebf66, 'dc44', 'c.lw a5, 0xc(s1)'),
    (0xa00ebf68, '898f', 'c.sub a5, a0'),
    (0xa00ebf6a, 'dcc4', 'c.sw a5, 0xc(s1)'),
]
rows = []
for address, encoded, expected in anchors:
    off = address - 0x9ffff000
    raw = data[off:off + len(bytes.fromhex(encoded))]
    assert raw.hex() == encoded, hex(address)
    decoded = list(cs.disasm(raw, address))
    assert sum(i.size for i in decoded) == len(raw)
    assembly = [(i.mnemonic + ' ' + i.op_str).strip() for i in decoded]
    if expected is not None:
        assert assembly == [expected], (hex(address), assembly)
    rows.append(dict(address=hex(address), offset=hex(off), bytes=encoded, assembly=assembly))

# Decode decisive fields without relying on printed mnemonic text.
def word(a, n=4):
    return int.from_bytes(data[a-0x9ffff000:a-0x9ffff000+n], 'little')
hi = word(0xa00f0df0) & 0xfffff000
imm = word(0xa00f0df4) >> 20
imm = (imm ^ 0x800) - 0x800
assert (hi + imm) & 0xffffffff == 0xa00ea5be
w = word(0xa00ea5c6, 2)
assert w & 3 == 0 and w >> 13 == 2  # C.LW
assert 8 + ((w >> 2) & 7) == 10 and 8 + ((w >> 7) & 7) == 10
assert (((w >> 5) & 1) << 6 | ((w >> 10) & 7) << 3 | ((w >> 6) & 1) << 2) == 0
for a, target in [(0xa00ebdf4, 0xa008ab76), (0xa008ab7e, 0xa000589c)]:
    w = word(a)
    delta = ((w >> 31) << 20) | (((w >> 12) & 255) << 12) | (((w >> 20) & 1) << 11) | (((w >> 21) & 1023) << 1)
    delta = (delta ^ (1 << 20)) - (1 << 20)
    assert w & 127 == 0x6f and (w >> 7) & 31 == 1
    assert (a + delta) & 0xffffffff == target
result = dict(static_only=True, result='passed', anchors=len(rows), bytes=sum(len(bytes.fromhex(r['bytes'])) for r in rows),
              scope='A30 independent review; A23/A25 units and A27/A28 cleanup inherited; zero new functions',
              rom=str(ROM), mapping='offset=VA-0x9ffff000', anchors_reviewed=rows)
(HERE / 'review-evidence.json').write_text(json.dumps(result, ensure_ascii=False, indent=2) + '\n', encoding='utf8')
print(json.dumps({k: result[k] for k in ['static_only', 'result', 'anchors', 'bytes']}))
