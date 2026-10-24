"""Read-only static evidence check; does not execute firmware or instruction models."""
import argparse
import hashlib
import json
from pathlib import Path
import struct

parser = argparse.ArgumentParser()
parser.add_argument('--source-root', type=Path, required=True)
args = parser.parse_args()
root = args.source_root
rom = (root / 'roms/0041/ap01-1.0.2_0041.bin').read_bytes()
assert len(rom) == 6769704
assert hashlib.sha256(rom).hexdigest() == '972db4c136c7ed9e24a83c07c1a7fd62040ca018b08ca285216d26b1fee3c6b9'
base = 0x9ffff000
slots = struct.unpack_from('<7I', rom, 0xa01bb0cc - base)
assert slots == (0xa006f5ce, 0xa006fa80, 0xa007016e, 0xa007022c,
                 0xa0074d30, 0xa0070366, 0xa006fab6)
bundle = root / 'evidence/rea-0041-20261017/evidence/upper-complete.evidence.json'
records = json.loads(bundle.read_text(encoding='utf-8'))['records']
identities = {}
for index, entry in [(157, 0xa007016e), (287, 0xa007022c), (37, 0xa0070366),
                     (248, 0xa0064368), (313, 0xa0115b84)]:
    record = records[index]
    assert record['parameters']['procedure'] == hex(entry)
    assert record['subject']['digest']['sha256'] == hashlib.sha256(rom).hexdigest()
    identities[str(index)] = {'procedure': record['parameters']['procedure'],
                              'evidence_id': record['evidence_id']}
# Check decisive ABI, release, marker mutation, and private condition encoding.
words = {0xa0070216: '8b97e640', 0xa0070354: '23a60402',
         0xa007036e: '13854500', 0xa007038a: '0145',
         0xa00b516c: '93c7f7ff', 0xa00b5170: '2300f900',
         0xa01adde6: 'fd57', 0xa01adde8: '9cc0'}
for address, expected in words.items():
    assert rom[address-base:address-base+len(expected)//2].hex() == expected, hex(address)
w = struct.unpack_from('<I', rom, 0xa0070216-base)[0]
assert ((w & 127), (w >> 12 & 7), (w >> 25), (w >> 7 & 31),
        (w >> 15 & 31), (w >> 20 & 31)) == (11, 1, 32, 15, 13, 14)
# Inclusive-end windows are confined to the claimed sink and necessary API boundaries.
ranges = [(0xa01bb0cc, 0xa01bb0e7), (0xa00645d6, 0xa00645ec),
          (0xa006462e, 0xa006465b), (0xa00700b6, 0xa007019d),
          (0xa00701f6, 0xa00702a5), (0xa0070322, 0xa007038f),
          (0xa00b4f54, 0xa00b503d), (0xa00b5122, 0xa00b518b),
          (0xa01addc6, 0xa01addf3)]
out = {'source_sha256': hashlib.sha256(rom).hexdigest(), 'base': hex(base),
       'slots': [hex(v) for v in slots], 'retained_records': identities,
       'windows': [{'start': hex(a), 'end_inclusive': hex(z), 'offset': hex(a-base),
                    'hex': rom[a-base:z-base+1].hex()} for a, z in ranges]}
(Path(__file__).parent / 'raw-windows.json').write_text(
    json.dumps(out, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
print('PASS: artifact identity, 7 ROM slots, 5 retained identities, 8 decisive words, mveqz fields; wrote bounded raw windows')
