"""Independent static byte/ABI review. Does not execute firmware or old verifiers."""
import json
from pathlib import Path
from capstone import Cs, CS_ARCH_RISCV, CS_MODE_RISCV32, CS_MODE_RISCVC

HERE = Path(__file__).resolve().parent
TREE = HERE.parents[2]
SOURCE = Path('D:/Documents/PlatformIO/Projects/cuktech-ap01-firmware')
ROM = SOURCE / 'roms/0041/ap01-1.0.2_0041.bin'
BASE = 0x9ffff000
rom = ROM.read_bytes()
md = Cs(CS_ARCH_RISCV, CS_MODE_RISCV32 | CS_MODE_RISCVC)
checks = []
def check(name, actual, expected):
    assert actual == expected, (name, actual, expected)
    checks.append({'name': name, 'actual': actual, 'expected': expected})
def sx(x, bits): return x - (1 << bits) if x >> (bits - 1) else x
def raw(a, n): return rom[a - BASE:a - BASE + n]
def target(a, n, x):
    if n == 4 and x & 127 == 111:
        return a + sx(((x >> 31) << 20) | (((x >> 12) & 255) << 12) | (((x >> 20) & 1) << 11) | (((x >> 21) & 1023) << 1), 21)
    if n == 4 and x & 127 == 99:
        return a + sx(((x >> 31) << 12) | (((x >> 7) & 1) << 11) | (((x >> 25) & 63) << 5) | (((x >> 8) & 15) << 1), 13)
    if n == 2 and x & 3 == 1:
        k = x >> 13
        if k in (6, 7):
            return a + sx((((x >> 12) & 1) << 8) | (((x >> 5) & 3) << 6) | (((x >> 2) & 1) << 5) | (((x >> 10) & 3) << 3) | (((x >> 3) & 3) << 1), 9)
        if k in (1, 5):
            return a + sx((((x >> 12) & 1) << 11) | (((x >> 8) & 1) << 10) | (((x >> 9) & 3) << 8) | (((x >> 6) & 1) << 7) | (((x >> 7) & 1) << 6) | (((x >> 2) & 1) << 5) | (((x >> 11) & 1) << 4) | (((x >> 3) & 7) << 1), 12)

# Ten bounded function contracts. Entry a00ddbf6 remains deliberately partial.
ranges = [(0xa00dddf4, 0xa00dde9a), (0xa01ad6d8, 0xa01ad6ec),
          (0xa008b43a, 0xa008b456), (0xa00ddbf6, 0xa00ddc7e),
          (0xa00ddd82, 0xa00ddd90), (0xa0081804, 0xa008184e),
          (0xa00d7446, 0xa00d749e), (0xa00ddab4, 0xa00ddbf6),
          (0xa00dbff4, 0xa00dc020), (0xa00892ac, 0xa00892d0),
          (0xa00892f4, 0xa008934a)]
vendor = {0xa0089304: (16, 15, 14), 0xa0089314: (15, 14, 13),
          0xa0089322: (13, 14, 17), 0xa0089330: (14, 11, 12)}
windows = []; rows = {}
for start, end in ranges:
    pc = start; win = []
    while pc < end:
        h = int.from_bytes(raw(pc, 2), 'little')
        n = 4 if h & 3 == 3 else 2
        b = raw(pc, n); x = int.from_bytes(b, 'little')
        if pc in vendor:
            rd, r1, r2 = vendor[pc]
            check(f'{pc:#x} vendor fields', [x & 127, x >> 7 & 31, x >> 12 & 7, x >> 15 & 31, x >> 20 & 31, x >> 25], [11, rd, 1, r1, r2, 33])
            asm = f'th.mvnez x{rd},x{r1},x{r2}'
        else:
            ins = list(md.disasm(b, pc))
            assert len(ins) == 1 and ins[0].size == n, hex(pc)
            asm = ins[0].mnemonic + ' ' + ins[0].op_str
        row = dict(address=hex(pc), file_offset=pc - BASE, bytes=b.hex(), assembly=asm)
        dest = target(pc, n, x)
        if dest is not None: row['target'] = hex(dest)
        rows[pc] = row; win.append(row); pc += n
    check(f'{start:#x} continuous end', pc, end)
    windows.append(dict(start=hex(start), end_exclusive=hex(end), instructions=win))

# Compare original bytes against retained producers, without executing their scripts.
prior = ['text-precondition-c15-0041-20261023/instruction-evidence.json',
         'invalidation-gates-c17-0041-20261023/instruction-evidence.json',
         'invalidation-third-gate-c19-0041-20261023/instruction-evidence.json',
         'transform-predicate-c21-0041-20261023/evidence.json']
compared = []
def visit(obj):
    if isinstance(obj, dict):
        a = obj.get('address', obj.get('pc')); b = obj.get('bytes', obj.get('raw'))
        if isinstance(a, str) and isinstance(b, str) and a.startswith('0x') and int(a, 16) in rows:
            check(f'prior byte {a}', rows[int(a, 16)]['bytes'], b)
        for val in obj.values(): visit(val)
    elif isinstance(obj, list):
        for val in obj: visit(val)
for name in prior:
    visit(json.loads((TREE / 'reverse/analysis' / name).read_text(encoding='utf-8')))
    compared.append(name)

def fields(a, expected):
    x = int.from_bytes(raw(a, 4), 'little')
    check(f'{a:#x} I fields', [x & 127, x >> 7 & 31, x >> 12 & 7, x >> 15 & 31, sx(x >> 20, 12)], expected)
fields(0xa00dbffc, [19, 14, 0, 14, -1024])
fields(0xa00dc00c, [3, 15, 5, 15, 50])  # unsigned halfword, not signed/word
fields(0xa00dc012, [19, 15, 0, 15, -2048])
fields(0xa00ddb6a, [19, 11, 0, 8, -48])
fields(0xa00ddc70, [19, 11, 0, 8, -80])
fields(0xa0089340, [19, 10, 4, 15, 1])
for a, dest in {0xa00dc000:0xa00dc008, 0xa00dc00a:0xa00dc018,
                0xa00dc016:0xa00dc01c, 0xa00dc01a:0xa00dc000,
                0xa00dc01e:0xa00dc002, 0xa00ddb16:0xa00dbff4,
                0xa00ddb62:0xa00dbff4, 0xa00ddb1a:0xa00ddb26,
                0xa00ddb66:0xa00ddb74, 0xa00ddb22:0xa00dca48,
                0xa00ddb70:0xa00dca48, 0xa00ddb10:0xa00ddbda,
                0xa00ddb28:0xa00ddbdc, 0xa00ddb32:0xa00ddbda,
                0xa00ddb80:0xa00ddb26, 0xa00ddc54:0xa00ddd82,
                0xa00ddc6c:0xa00ddd82, 0xa00ddc76:0xa00ddab4,
                0xa00ddc7a:0xa00ddd82, 0xa00dde8a:0xa00ddbf6,
                0xa0089338:0xa0089344}.items():
    check(f'{a:#x} branch/call destination', rows[a]['target'], hex(dest))
pred = [r for a, r in rows.items() if 0xa00dbff4 <= a < 0xa00dc020]
stores = [r for r in pred if r['assembly'].split()[0] in ('sw','sh','sb','c.sw','c.swsp')]
check('predicate sole store', [(r['address'],r['assembly']) for r in stores], [('0xa00dbff6','c.swsp s0, 0xc(sp)')])
check('predicate no direct branch outside own extent', all(0xa00dbff4 <= int(r['target'],16) < 0xa00dc020 for r in pred if 'target' in r), True)
for a, bs in {0xa00dbff8:'0567',0xa00dc008:'1c45',0xa00dc010:'f98f',0xa00dc018:'4841',0xa00dc01c:'0545',0xa00ddb1c:'0546',0xa00ddb1e:'ca85',0xa00ddb68:'0546',0xa00ddbe8:'4e85'}.items():
    check(f'{a:#x} key compressed bytes', rows[a]['bytes'], bs)
model_path = SOURCE / 'evidence/rea-0041-20261017/ghidra/Ghidra/Processors/RISCV/data/languages/ap01thead2.sinc'
model = model_path.read_text()
start = model.index(':th.mvnez '); end = model.index('}', start)+1
rule = model[start:end]
check('vendor retained semantics', 'if (rs2 == 0) goto <done>;\n  rd = rs1;' in rule, True)
out = dict(kind='independent static ROM review; no firmware/model execution', rom=str(ROM),
           mapping='file_offset=address-0x9ffff000', baseline='2ee39b3', windows=windows,
           checks=checks, retained_byte_sources=compared, vendor_model=dict(path=str(model_path),text=rule),
           boundary='a00dca48 internal behavior and a00ddc7e onward remain unreviewed')
(HERE/'evidence.json').write_text(json.dumps(out,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
(HERE/'instructions.txt').write_text('\n'.join(f"{r['address']} off={r['file_offset']:#x} {r['bytes']} {r['assembly']}"+(f" => {r['target']}" if 'target' in r else '') for w in windows for r in w['instructions'])+'\n',encoding='utf-8')
print(json.dumps(dict(result='passed',function_contracts=10,windows=len(windows),bytes=sum(e-s for s,e in ranges),instructions=len(rows),checks=len(checks),direct_targets=sum('target' in r for r in rows.values()))))
