"""Independent Q13 static check; never imports the author's verifier or executes ROM."""
import argparse
import hashlib
import json
from pathlib import Path
from datetime import datetime, timezone
import capstone

p = argparse.ArgumentParser()
p.add_argument('--source-root', type=Path, required=True)
a = p.parse_args()
root = a.source_root
rom = (root / 'roms/0041/ap01-1.0.2_0041.bin').read_bytes()
assert len(rom) == 6769704
assert hashlib.sha256(rom).hexdigest() == '972db4c136c7ed9e24a83c07c1a7fd62040ca018b08ca285216d26b1fee3c6b9'
bundle = json.loads((root / 'evidence/rea-0041-20261017/evidence/upper-complete.evidence.json').read_text(encoding='utf-8'))
need = {
 205: ['0xa0115910: lw s6, 0x4, a2', '0xa01159a6: addi s6, s6, -0x128', '0xa0115a8c: addi s1, s1, -0x470', '0xa0115a90: c.add s1, s6', '0xa0115a98: jal ra, 0xa010f7e8', '0xa0115b0a: jal ra, 0xa01148c4', '0xa0115b4a: c.mv a0, s6', '0xa0115b56: jal ra, 0xa01ac32a'],
 185: ['0xa01148f4: jal ra, 0xa0114790', '0xa01148fa: c.bnez a0, 0xa011492c', '0xa0114902: addi a0, s1, 0x270', '0xa011490e: sw a0, 0x2b4, s1', '0xa011492e: sb zero, 0x50, s1', '0xa0114934: c.lw a1, 0x4c, s1', '0xa0114938: c.jalr a5'],
 271: ['0xa010f838: lbu a5, 0x50, s1', '0xa010f842: c.lw a1, 0x4c, s1', '0xa010f84c: c.jalr a5', '0xa010f850: sb s7, 0x50, s1', '0xa010f868: c.addi s2, 0x1', '0xa010f86c: c.j 0xa010f816'],
 313: ['0xa0115c00: c.li a2, 0x1c', '0xa0115c14: addi s4, s2, -0x470', '0xa0115c20: sw s8, 0x4c, s1', '0xa0115c24: sw s4, 0x8, s1', '0xa0115bce: li a0, 0x2e0', '0xa0115bd2: jal ra, 0xa002fcc8', '0xa0115bd6: c.mv s1, a0', '0xa0115c76: c.mv a0, s1', '0xa0115c78: jal ra, 0xa002e14e']
}
records = []
for n, lines in need.items():
    rec = bundle['records'][n]
    assert rec['analysis_profile']['digest'] == '4825fb58a33a3e7d618557975b153b8318cf7e833d190ad16bcbf8bd441ae621'
    asm = rec['normalized_result']['assembly']
    assert all(line in asm for line in lines)
    records.append({'ordinal': n, 'evidence_id': rec['evidence_id'], 'assembly': asm})
legacy = (root / 'evidence/rea-0041-20261017/evidence/upper-miio-b.md').read_text(encoding='utf-8')
assert 'ev_acec13eb19b12621a674a56b842b3cba123fc76d98212eca7676f53ea1e76459' in legacy
assert 'ev_4999424dc25eab1cd88751ca3fc153972ea5a2e3496073c25e5fdb8d7c368f04' in legacy
start = 0xa0114790
raw = rom[start - 0x9ffff000:0xa01148c4 - 0x9ffff000]
decoder = capstone.Cs(capstone.CS_ARCH_RISCV, capstone.CS_MODE_RISCV32 | capstone.CS_MODE_RISCVC)
instructions = list(decoder.disasm(raw, start))
assert sum(i.size for i in instructions) == 308
ops = {i.address: (i.mnemonic, i.op_str) for i in instructions}
for pc, op in {
 0xa01147b0: ('addi', 's2, a0, 0xb0'), 0xa01147b4: ('lw', 's4, 8(a0)'),
 0xa011481c: ('sb', 'a5, 0x50(s1)'), 0xa0114820: ('addi', 'a2, zero, 0x120'),
 0xa011482e: ('lhu', 'a5, 0x6e(s1)'), 0xa011483e: ('lbu', 'a5, 0x6c(s1)'),
 0xa0114846: ('sw', 's2, -0x140(s0)'), 0xa01148aa: ('lw', 'a0, 0xc(s4)'),
 0xa01148b2: ('c.mv', 'a3, s1'), 0xa01148b8: ('addi', 'a1, s0, -0x140'),
 0xa01148bc: ('jal', '0xd080'), 0xa01148c0: ('c.mv', 's1, a0')
}.items():
    assert ops[pc] == op, (hex(pc), ops[pc])
assert 0xa01148bc + 0xd080 == 0xa012193c
for pc in [0xa0114832, 0xa0114858, 0xa011486c, 0xa0114880]:
    assert ops[pc] == ('addi', 'a2, zero, 0x3f')
for pc, off in [(0xa0114864, '-0xf9'), (0xa0114878, '-0xb9'), (0xa011488c, '-0x79'), (0xa0114898, '-0x39')]:
    assert ops[pc] == ('sb', f'zero, {off}(s0)')
author = json.loads((root / 'reverse/analysis/app-ota-research-02-0041-20261025/raw-windows.json').read_text(encoding='utf-8'))
assert next(w for w in author['windows'] if w['address'] == hex(start))['hex'] == raw.hex()
result = {'utc': datetime.now(timezone.utc).isoformat(), 'source_sha256': hashlib.sha256(rom).hexdigest(),
          'decoder': capstone.__version__, 'records': records, 'start_hex': raw.hex(),
          'start_assembly': [f'{i.address:#x}: {i.mnemonic} {i.op_str}' for i in instructions],
          'result': 'PASS', 'new_business_bytes': 0, 'resampled_start_bytes': 308,
          'boundary': '0xa012193c and table targets not read; D copying and T asynchronous retention unknown'}
Path(__file__).with_name('review-evidence.json').write_text(json.dumps(result, indent=2), encoding='utf-8')
print('PASS: ROM identity, retained object/selector/offer/register assembly, legacy contract IDs, independent 308-byte start decode and author byte equality')
