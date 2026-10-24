"""Independent static Q17 review; never imports or executes author tooling."""
import hashlib
import json
from pathlib import Path
from datetime import datetime, timezone
import capstone

ROOT = Path('D:/Documents/PlatformIO/Projects/cuktech-ap01-firmware')
OUT = Path(__file__).resolve().parent
rom = (ROOT / 'roms/0041/ap01-1.0.2_0041.bin').read_bytes()
assert len(rom) == 6769704
digest = hashlib.sha256(rom).hexdigest()
assert digest == '972db4c136c7ed9e24a83c07c1a7fd62040ca018b08ca285216d26b1fee3c6b9'
md = capstone.Cs(capstone.CS_ARCH_RISCV, capstone.CS_MODE_RISCV32 | capstone.CS_MODE_RISCVC)
windows, ins = [], {}
for start, size in [(0xa0067be6, 58), (0xa0067c20, 128), (0xa0195ce4, 374)]:
    data = rom[start - 0x9ffff000:start - 0x9ffff000 + size]
    decoded = list(md.disasm(data, start))
    assert sum(i.size for i in decoded) == size
    rows = []
    for i in decoded:
        ins[i.address] = (i.mnemonic, i.op_str)
        rows.append(f'{i.address:08x} {i.bytes.hex()} {i.mnemonic} {i.op_str}')
    windows.append(dict(va=hex(start), offset=hex(start - 0x9ffff000), size=size, hex=data.hex(), assembly=rows))

# Independent register/width/order assertions against decoded original words.
expected = {
    0xa0067bf2: ('lw', 'a0, 0x1e0(a0)'),
    0xa0067c02: ('sw', 'zero, 0x1d0(s1)'),
    0xa0067c0c: ('jalr', 'ra, ra, 0x84'),
    0xa0067c12: ('sh', 'a5, 0x1d4(s1)'),
    0xa0067c30: ('addi', 's2, s1, -0x288'),
    0xa0067c34: ('lw', 'a0, 0(s2)'),
    0xa0067c42: ('lbu', 'a4, 8(s2)'),
    0xa0067c48: ('bgeu', 'a5, a4, 0x32'),
    0xa0067c4c: ('addi', 'a5, zero, 0x32'),
    0xa0067c7a: ('lui', 'a5, 0x40108'),
    0xa0067c98: ('c.mv', 'a0, s2'),
    0xa0195d10: ('sh', 'zero, -0x88(s0)'),
    0xa0195d14: ('sb', 'zero, -0x86(s0)'),
    0xa0195d40: ('c.li', 'a1, 0x10'),
    0xa0195d5e: ('c.beqz', 'a0, 0x5c'),
    0xa0195d66: ('c.li', 's1, -1'),
    0xa0195dc0: ('sh', 'a4, -0x70(s0)'),
    0xa0195dda: ('sw', 'a4, -0x6c(s0)'),
    0xa0195dde: ('sw', 'a5, -0x64(s0)'),
    0xa0195de2: ('sw', 's4, -0x68(s0)'),
    0xa0195e40: ('addi', 'a0, s1, 0x128'),
    0xa0195e44: ('c.mv', 'a5, s3'),
    0xa0195e46: ('c.li', 'a4, 0x14'),
    0xa0195e48: ('addi', 'a3, s0, -0x74'),
    0xa0195e50: ('c.li', 'a1, 4'),
    0xa0195e56: ('c.mv', 's1, a0'),
    0xa0195d9e: ('c.mv', 'a0, s1'),
}
for address, pair in expected.items():
    assert ins[address] == pair, (hex(address), ins[address], pair)
assert (0x62fcb000 - 0x288) == 0x62fcad78
blocked = [v for v in range(256) if ((0x40108000 >> v) & 1) if v <= 30]
blocked.append(50)
assert blocked == [15, 20, 30, 50]
assert 0xa0067c08 + 0x14c000 + 0x84 == 0xa01b3c8c
assert 0xa0195e52 - 0x7c81a == 0xa0119638
assert 0xa0069000 - 0x5da == 0xa0068a26
assert 0x2000 - 0x8b == 8053 and 0x2000 - 0x4a8 == 7000
assert (rom[0xa062c718 - 0x9ffff000:0xa062c718 - 0x9ffff000 + 8]) == b'otn.ntp\0'

record = json.loads((ROOT / 'evidence/rea-0041-20261017/evidence/upper-complete.evidence.json').read_text(encoding='utf-8'))['records'][89]
assembly = record['normalized_result']['assembly']
bounds = [(0xa006e37c, 0xa006e3d0), (0xa006e5a6, 0xa006e5b8), (0xa006e6aa, 0xa006e6c0), (0xa006e75c, 0xa006e7ce)]
caller = [line for line in assembly if any(lo <= int(line.split(':')[0], 16) <= hi for lo, hi in bounds)]
for line in [
    '0xa006e5a8: jal ra, 0xa0067be6',
    '0xa006e5b0: jal ra, 0xa0068914',
    '0xa006e768: jal ra, 0xa0067c20',
    '0xa006e76c: c.bnez a0, 0xa006e778',
    '0xa006e7cc: c.j 0xa006e76e',
]:
    assert line in caller, line
result = dict(utc=datetime.now(timezone.utc).isoformat(), rom_sha256=digest,
              capstone=capstone.__version__, static_bytes=560, windows=windows,
              decoded_assertions=len(expected), blocked=blocked,
              caller_evidence_id=record['evidence_id'], caller_profile=record['analysis_profile'],
              caller_pointer='#/records/89/normalized_result', caller=caller)
(OUT / 'verification.json').write_text(json.dumps(result, indent=2, ensure_ascii=False), encoding='utf-8')
(OUT / 'inspection.txt').write_text('\n'.join(row for w in windows for row in w['assembly']) + '\n\n' + '\n'.join(caller) + '\n', encoding='utf-8')
print(f'PASS: original SHA256; 560 B complete decode; {len(expected)} instruction assertions; values={blocked}; caller slices={len(caller)}')
