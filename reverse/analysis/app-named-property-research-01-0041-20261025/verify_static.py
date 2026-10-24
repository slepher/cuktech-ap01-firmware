"""Read-only, bounded Q21 evidence reproduction; does not run firmware."""
import hashlib
import json
from pathlib import Path
import sys

import capstone

ROOT = Path(sys.argv[1]) if len(sys.argv) > 1 else Path(__file__).resolve().parents[3]
OUT = Path(__file__).resolve().parent
BASE = 0x9FFFF000
ROM_SHA = "972db4c136c7ed9e24a83c07c1a7fd62040ca018b08ca285216d26b1fee3c6b9"
rom = (ROOT / "roms/0041/ap01-1.0.2_0041.bin").read_bytes()
assert len(rom) == 6769704 and hashlib.sha256(rom).hexdigest() == ROM_SHA
md = capstone.Cs(capstone.CS_ARCH_RISCV,
                 capstone.CS_MODE_RISCV32 | capstone.CS_MODE_RISCVC)
windows = []
count = 0
for start, end in [(0xA0116900, 0xA0116A3A), (0xA0116A3A, 0xA0116AD0),
                   (0xA011C3B0, 0xA011C514)]:
    data = rom[start - BASE:end - BASE]
    pc = start
    instructions = []
    while pc < end:
        off = pc - BASE
        size = 4 if rom[off] & 3 == 3 else 2
        raw = rom[off:off + size]
        if pc == 0xA0116A0C:
            word = int.from_bytes(raw, "little")
            fields = [word & 127, (word >> 7) & 31, (word >> 12) & 7,
                      (word >> 15) & 31, (word >> 20) & 31,
                      (word >> 25) & 3, word >> 27]
            assert fields == [11, 0, 5, 15, 10, 0, 0]
            text = "th.srb zero,a5,a0,0 (existing model: byte[a5+a0]=0)"
        else:
            decoded = list(md.disasm(raw, pc))
            assert len(decoded) == 1 and decoded[0].size == size, hex(pc)
            ins = decoded[0]
            text = ins.mnemonic + " " + ins.op_str
        instructions.append({"address": hex(pc), "bytes": raw.hex(), "text": text})
        count += 1
        pc += size
    assert pc == end
    windows.append({"start": hex(start), "end_exclusive": hex(end),
                    "size": len(data), "sha256": hashlib.sha256(data).hexdigest(),
                    "hex": data.hex(), "instructions": instructions})

# JAL immediate checks are independent of mnemonic display.
edges = {0xA0116A9A: 0xA011C3B0, 0xA0116AA4: 0xA005F3D8,
         0xA0116AB0: 0xA0116900, 0xA0116ABA: 0xA01B3C8C,
         0xA011C3C8: 0xA0110984, 0xA011C4CC: 0xA011C0DA}
for pc, target in edges.items():
    word = int.from_bytes(rom[pc - BASE:pc - BASE + 4], "little")
    assert word & 127 == 0x6F
    imm = (((word >> 31) << 20) | (((word >> 12) & 255) << 12)
           | (((word >> 20) & 1) << 11) | (((word >> 21) & 1023) << 1))
    if imm & (1 << 20):
        imm -= 1 << 21
    assert pc + imm == target, hex(pc)
assert sum(w["size"] for w in windows) == 820
strings = {}
for addr, expected in [(0xA0565828, b"props"), (0xA056C058, b"method")]:
    actual = rom[addr - BASE:addr - BASE + len(expected) + 1]
    assert actual == expected + b"\0"
    strings[hex(addr)] = expected.decode()
result = {"rom_sha256": ROM_SHA, "base": hex(BASE),
          "capstone": capstone.__version__, "instruction_count": count,
          "windows": windows, "checked_jal_edges": {hex(k): hex(v) for k, v in edges.items()},
          "strings": strings,
          "limits": "Only 820 body bytes plus two literal strings; library semantics stop at API edges."}
(OUT / "windows.json").write_text(json.dumps(result, indent=2) + "\n", encoding="utf-8")
print(f"PASS: ROM identity; 820 bytes; {count} instructions; 6 JAL edges; 1 vendor word; 2 strings")
