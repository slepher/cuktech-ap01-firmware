"""H11 bounded static cursor check. Reads original ROM; never runs firmware."""
from pathlib import Path
import json
import capstone

HERE = Path(__file__).resolve().parent
MAIN = Path('D:/Documents/PlatformIO/Projects/cuktech-ap01-firmware')
ROM = (MAIN / 'roms/0041/ap01-1.0.2_0041.bin').read_bytes()
BASE = 0x9ffff000
CS = capstone.Cs(capstone.CS_ARCH_RISCV, capstone.CS_MODE_RISCV32 | capstone.CS_MODE_RISCVC)

def decode(lo, hi):
    rows = []
    while lo < hi:
        raw = ROM[lo-BASE:lo-BASE+4]
        w = int.from_bytes(raw, 'little')
        size = 4 if w & 3 == 3 else 2
        if w & 127 == 11:
            text = f'vendor word={w:#010x} rd={(w>>7)&31} rs1={(w>>15)&31} rs2={(w>>20)&31}'
        else:
            ins = next(CS.disasm(raw, lo, count=1))
            assert ins.size == size
            text = ins.mnemonic + ' ' + ins.op_str
            if ins.mnemonic in ('jal', 'c.j', 'c.jal', 'bne', 'bnez'):
                text += ' -> ' + hex((lo + int(ins.op_str.split(',')[-1].strip(), 0)) & 0xffffffff)
        rows.append(dict(va=hex(lo), raw=raw[:size].hex(), asm=text))
        lo += size
    assert lo == hi
    return rows

# Cursor is live only before 8994 and in the branch block at 8a54..8b80.
ranges = [('cursor_head_exit', 0xa00b8818, 0xa00b8996),
          ('cursor_nonzero_rows', 0xa00b8a54, 0xa00b8b82),
          ('consumer_ctx', 0xa00b56b2, 0xa00b56c8),
          ('consumer_row0', 0xa00b584c, 0xa00b5886)]
decoded = {name: decode(lo, hi) for name, lo, hi in ranges}
checks = []
def check(label, got, want):
    assert got == want, (label, got, want)
    checks.append(dict(label=label, value=got))

def raw(at, want):
    check(hex(at), ROM[at-BASE:at-BASE+len(bytes.fromhex(want))].hex(), want)

for at, want in {
    0xa00b8818: '93094905', 0xa00b883a: '631d0c20',
    0xa00b8860: '232aa904', 0xa00b8936: '050c',
    0xa00b8938: '9d47', 0xa00b893a: '9109',
    0xa00b893c: 'e31ffcee', 0xa00b8994: 'aa89',
    0xa00b8a82: '23a0a900', 0xa00b8b80: '65b3',
    0xa00b56b2: 'aa84', 0xa00b5850: '83aa4405',
    0xa00b5856: '5685', 0xa00b5862: '5685',
    0xa00b586e: '5685',
}.items(): raw(at, want)

cursor_rows = decoded['cursor_head_exit'] + decoded['cursor_nonzero_rows']
uses = [x for x in cursor_rows if 's3' in x['asm']]
check('complete ordinary s3 references within cursor live ranges',
      [x['va'] for x in uses],
      ['0xa00b8818', '0xa00b893a', '0xa00b8994', '0xa00b8a82',
       '0xa00b8abc', '0xa00b8af6', '0xa00b8b10', '0xa00b8b44', '0xa00b8b72'])
vendor = [x for x in cursor_rows if x['asm'].startswith('vendor')]
check('vendor instructions in cursor ranges', [x['va'] for x in vendor], ['0xa00b8a76'])
w = int.from_bytes(ROM[0xa00b8a76-BASE:0xa00b8a7a-BASE], 'little')
check('vendor fields do not reference cursor register x19',
      [(w >> n) & 31 for n in (7, 15, 20)], [15, 15, 0])

def call(at, target):
    w = int.from_bytes(ROM[at-BASE:at-BASE+4], 'little')
    off = ((w>>31)<<20) | (((w>>12)&255)<<12) | (((w>>20)&1)<<11) | (((w>>21)&1023)<<1)
    if off & (1<<20): off -= 1<<21
    check('JAL ' + hex(at), (w&127, (w>>7)&31, at+off), (111, 1, target))
for at in [0xa00b8858, 0xa00b895a, 0xa00b8a7e]: call(at, 0xa00a643a)
for at in [0xa00b5858, 0xa00b5864, 0xa00b5870]: call(at, 0xa00dcee4)

sources = []
for filename, indexes in [('weather-calendar-complete-0041.json', [14]),
                          ('details-0041-round4.json', [7, 9])]:
    p = MAIN / 'reverse/rehost' / filename
    j = json.loads(p.read_text(encoding='utf-8'))
    for i in indexes:
        x = j['evidence'][i]
        sources.append(dict(path=str(p), json_pointer=f'/evidence/{i}', address=x['address'],
                            fields=list(x)))
detail = json.loads((MAIN/'reverse/rehost/details-0041-round4.json').read_text(encoding='utf-8'))
check('old creator explicitly has row cursor', 'puVar7 = puVar3 + 0x15;' in detail['evidence'][7]['pseudocode'], True)
check('old consumer explicitly reads row0', 'param_1 + 0x54' in detail['evidence'][9]['pseudocode'], True)
check('old consumer traverses row children', 'FUN_ram_a00dcee4(uVar7,1)' in detail['evidence'][9]['pseudocode'], True)

out = dict(status='PASS', new_functionality=0, checks=checks, sources=sources,
           cursor_references=uses,
           ranges=[dict(name=n, start=hex(lo), end_exclusive=hex(hi), instructions=len(decoded[n])) for n,lo,hi in ranges],
           limitation='Only C+0x54 constructor cursor and one old row0 consumer. No global alias/free claim; ctx final owner remains unknown.')
(HERE/'instruction-evidence.json').write_text(json.dumps(out, ensure_ascii=False, indent=2)+'\n', encoding='utf-8')
(HERE/'instruction-windows.txt').write_text('\n\n'.join(n+'\n'+'\n'.join(x['va']+' '+x['raw']+' '+x['asm'] for x in rows) for n,rows in decoded.items())+'\n', encoding='utf-8')
print(json.dumps(dict(status='PASS', instructions=sum(map(len,decoded.values())), checks=len(checks))))
