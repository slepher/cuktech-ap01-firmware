"""Independent bounded ROM/retained-evidence checks; no firmware or model execution."""
import argparse
import hashlib
import json
from pathlib import Path
import struct

from capstone import Cs, CS_ARCH_RISCV, CS_MODE_RISCV32, CS_MODE_RISCVC

p = argparse.ArgumentParser()
p.add_argument('--source-root', type=Path, required=True)
root = p.parse_args().source_root
rom = (root / 'roms/0041/ap01-1.0.2_0041.bin').read_bytes()
sha = hashlib.sha256(rom).hexdigest()
assert (len(rom), sha) == (6769704, '972db4c136c7ed9e24a83c07c1a7fd62040ca018b08ca285216d26b1fee3c6b9')
base = 0x9ffff000
assert struct.unpack_from('<7I', rom, 0xa01bb0cc-base) == (0xa006f5ce, 0xa006fa80, 0xa007016e, 0xa007022c, 0xa0074d30, 0xa0070366, 0xa006fab6)
records = json.loads((root / 'evidence/rea-0041-20261017/evidence/upper-complete.evidence.json').read_text(encoding='utf-8'))['records']
identities = []
for i, proc in [(248, '0xa0064368'), (313, '0xa0115b84'), (157, '0xa007016e'), (287, '0xa007022c'), (37, '0xa0070366')]:
    r = records[i]
    assert r['parameters']['procedure'] == proc
    assert r['subject']['digest']['sha256'] == sha
    assert r['analysis_profile']['digest'] == '4825fb58a33a3e7d618557975b153b8318cf7e833d190ad16bcbf8bd441ae621'
    assert r['analysis_profile']['provider']['version'] == '12.1.4'
    identities.append({'index': i, 'procedure': proc, 'evidence_id': r['evidence_id'], 'profile_digest': r['analysis_profile']['digest']})
for i, rows in {
    248: ['0xa0064632: c.li a2, 0x1c', '0xa0064654: jal ra, 0xa0115b84', '0xa0064658: sw a0, 0x0, s4'],
    313: ['0xa0115c08: addi a0, s1, 0x30', '0xa0115c20: sw s8, 0x4c, s1'],
    157: ['0xa007017c: c.mv a1, a2', '0xa0070188: c.bnez a0, 0xa0070194', '0xa0070190: jal ra, 0xa00b4f54'],
    287: ['0xa007024e: jal ra, 0xa00701f6', '0xa0070260: jal ra, 0xa00b5122', '0xa0070270: c.li s1, -0x1', '0xa007029e: c.mv a0, s1'],
    37: ['0xa007036e: addi a0, a1, 0x4', '0xa0070376: jal ra, 0xa0070322', '0xa007038a: c.li a0, 0x0'],
}.items():
    assert all(s in records[i]['normalized_result']['assembly'] for s in rows)
words = {0xa0070216: '8b97e640', 0xa0070354: '23a60402', 0xa00b4f88: '8d45', 0xa00b4f8a: '09e9', 0xa00b4f94: '63840900', 0xa00b4f98: '93057002', 0xa00b516c: '93c7f7ff', 0xa00b5170: '2300f900', 0xa01addd4: '635ba000', 0xa01adde6: 'fd57', 0xa01adde8: '9cc0'}
for a, h in words.items():
    assert rom[a-base:a-base+len(h)//2].hex() == h, hex(a)
w = struct.unpack_from('<I', rom, 0xa0070216-base)[0]
fields = [w & 127, w >> 12 & 7, w >> 25, w >> 7 & 31, w >> 15 & 31, w >> 20 & 31]
assert fields == [11, 1, 32, 15, 13, 14]
model = root / 'evidence/rea-0041-20261017/ghidra/Ghidra/Processors/RISCV/data/languages/ap01thead2.sinc'
rule = model.read_text(encoding='utf-8').split(':th.mveqz ', 1)[1].split('}', 1)[0] + '}'
assert 'op0006=0xb & op1214=1 & op2531=32' in rule
assert 'if (rs2 != 0) goto <done>;' in rule and 'rd = rs1;' in rule
ranges = [(0xa01bb0cc,0xa01bb0e8), (0xa00645d6,0xa00645f0), (0xa006462e,0xa006465c), (0xa0115bce,0xa0115c2c), (0xa00700b6,0xa007019e), (0xa00701f6,0xa00702a6), (0xa0070322,0xa0070390), (0xa00b4f54,0xa00b503e), (0xa00b5122,0xa00b518c), (0xa01addc6,0xa01addf4)]
md = Cs(CS_ARCH_RISCV, CS_MODE_RISCV32 | CS_MODE_RISCVC)
windows = []
for a, z in ranges:
    raw = rom[a-base:z-base]
    row = {'start': hex(a), 'end_exclusive': hex(z), 'hex': raw.hex()}
    if a != 0xa01bb0cc:
        # Capstone stops at the private word: retain it and decode the suffix separately.
        pieces = [(a,z)] if not a <= 0xa0070216 < z else [(a,0xa0070216),(0xa007021a,z)]
        row['assembly'] = [f'{x.address:#x}: {x.bytes.hex()} {x.mnemonic} {x.op_str}' for lo, hi in pieces for x in md.disasm(rom[lo-base:hi-base],lo)]
    windows.append(row)
out = {'source_sha256': sha, 'capstone_version': __import__('capstone').__version__, 'records': identities, 'vendor_word_fields': fields, 'model_rule_text': ':th.mveqz '+rule, 'windows': windows}
target = Path(__file__).with_name('review-evidence.json')
target.write_text(json.dumps(out,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
print('PASS: ROM identity; seven slots; five record identities/profiles; ABI/order rows; decisive words; static vendor fields/rule; bounded independent evidence')
print('review-evidence.json SHA256', hashlib.sha256(target.read_bytes()).hexdigest())
