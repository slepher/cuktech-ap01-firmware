"""Read ROM bytes and verify the C21 local contract. Never execute firmware."""
import json
from pathlib import Path
from capstone import Cs, CS_ARCH_RISCV, CS_MODE_RISCV32, CS_MODE_RISCVC

HERE = Path(__file__).resolve().parent
TREE = HERE.parents[2]
ROM = Path('D:/Documents/PlatformIO/Projects/cuktech-ap01-firmware/roms/0041/ap01-1.0.2_0041.bin')
BASE = 0x9ffff000
data = ROM.read_bytes()
md = Cs(CS_ARCH_RISCV, CS_MODE_RISCV32 | CS_MODE_RISCVC)
checks = []

def check(label, actual, expected):
    assert actual == expected, (label, actual, expected)
    checks.append(dict(label=label, actual=actual, expected=expected))

def sx(v, n):
    return v - (1 << n) if v & (1 << (n - 1)) else v

rows = []
windows = [(0xa00dbff4, 0xa00dc020), (0xa00ddb14, 0xa00ddb26), (0xa00ddb60, 0xa00ddb74)]
for start, end in windows:
    pc = start
    while pc < end:
        off = pc - BASE
        h = int.from_bytes(data[off:off+2], 'little')
        n = 4 if h & 3 == 3 else 2
        bs = data[off:off+n]
        decoded = list(md.disasm(bs, pc))
        check(hex(pc) + ' one complete instruction', [len(decoded), decoded[0].size], [1, n])
        ins = decoded[0]
        row = dict(pc=hex(pc), file_offset=hex(off), raw=bs.hex(), mnemonic=ins.mnemonic, operands=ins.op_str)
        w = int.from_bytes(bs, 'little')
        target = None
        if n == 4 and w & 127 == 111:
            imm = ((w>>31&1)<<20)|((w>>21&1023)<<1)|((w>>20&1)<<11)|((w>>12&255)<<12)
            target = pc + sx(imm, 21)
            row['rd'] = w >> 7 & 31
        elif n == 2 and h & 3 == 1 and h >> 13 in (6, 7):
            imm = ((h>>12&1)<<8)|((h>>10&3)<<3)|((h>>5&3)<<6)|((h>>3&3)<<1)|((h>>2&1)<<5)
            target = pc + sx(imm, 9)
            row['branch_fields'] = [h>>13, 8+(h>>7&7)]
        elif n == 2 and h & 3 == 1 and h >> 13 == 5:
            imm = ((h>>12&1)<<11)|((h>>11&1)<<4)|((h>>9&3)<<8)|((h>>8&1)<<10)|((h>>7&1)<<6)|((h>>6&1)<<7)|((h>>3&7)<<1)|((h>>2&1)<<5)
            target = pc + sx(imm, 12)
        if target is not None:
            row['target'] = hex(target)
        rows.append(row)
        pc += n
    check(hex(start) + ' continuous extent', pc, end)

by_pc = {int(r['pc'],16): r for r in rows}
expected = [
    ('4111','c.addi','sp, -0x10'), ('22c6','c.swsp','s0, 0xc(sp)'),
    ('0567','c.lui','a4, 1'), ('0008','c.addi4spn','s0, sp, 0x10'),
    ('130707c0','addi','a4, a4, -0x400'), ('01e5','c.bnez','a0, 8'),
    ('3244','c.lwsp','s0, 0xc(sp)'), ('4101','c.addi','sp, 0x10'),
    ('8280','c.jr','ra'), ('1c45','c.lw','a5, 8(a0)'),
    ('99c7','c.beqz','a5, 0xe'), ('83d72703','lhu','a5, 0x32(a5)'),
    ('f98f','c.and','a5, a4'), ('93870780','addi','a5, a5, -0x800'),
    ('99c3','c.beqz','a5, 6'), ('4841','c.lw','a0, 4(a0)'),
    ('ddb7','c.j','-0x1a'), ('0545','c.li','a0, 1'), ('d5b7','c.j','-0x1c')]
core = [r for r in rows if 0xa00dbff4 <= int(r['pc'],16) < 0xa00dc020]
check('complete predicate instruction sequence', [(r['raw'],r['mnemonic'],r['operands']) for r in core], expected)
targets = {0xa00dc000:0xa00dc008, 0xa00dc00a:0xa00dc018, 0xa00dc016:0xa00dc01c,
           0xa00dc01a:0xa00dc000, 0xa00dc01e:0xa00dc002,
           0xa00ddb16:0xa00dbff4, 0xa00ddb1a:0xa00ddb26, 0xa00ddb22:0xa00dca48,
           0xa00ddb62:0xa00dbff4, 0xa00ddb66:0xa00ddb74, 0xa00ddb70:0xa00dca48}
for pc, target in targets.items():
    check(hex(pc)+' independently decoded target', by_pc[pc]['target'], hex(target))
for pc, fields in [(0xa00dbffc,[19,14,0,14,-1024]), (0xa00dc00c,[3,15,5,15,50]), (0xa00dc012,[19,15,0,15,-2048])]:
    w = int.from_bytes(bytes.fromhex(by_pc[pc]['raw']),'little')
    check(hex(pc)+' I encoding fields', [w&127,w>>7&31,w>>12&7,w>>15&31,sx(w>>20,12)], fields)
check('mask formation', (1<<12)-1024, 0x0c00)
check('only predicate store is saved s0 on stack', [(r['pc'],r['mnemonic'],r['operands']) for r in core if r['mnemonic'] in ('sw','sh','sb','c.sw','c.swsp')], [('0xa00dbff6','c.swsp','s0, 0xc(sp)')])
check('no predicate calls', [r for r in core if r['mnemonic'] in ('jal','jalr','c.jal','c.jalr')], [])
prior = json.loads((TREE/'reverse/analysis/invalidation-third-gate-review-c20-0041-20261023/review-evidence.json').read_text())
prior_by_pc = {r['address']:r for r in prior['instructions']}
for r in rows[len(core):]:
    check(r['pc']+' caller bytes equal accepted C20', r['raw'], prior_by_pc[r['pc']]['bytes'])
inventory = json.loads((TREE/'reverse/analysis/whole-rom-coverage-0041-20261023-round1.json').read_text())
def find_record(x):
    if isinstance(x,dict):
        if x.get('address') == '0xa00dbff4' and 'extent' in x:
            return x
        for v in x.values():
            found = find_record(v)
            if found: return found
    elif isinstance(x,list):
        for v in x:
            found = find_record(v)
            if found: return found
record = find_record(inventory)
check('retained body range', record['extent']['body']['ranges'], [dict(start='0xa00dbff4',end='0xa00dc01f')])
check('retained no direct callees', record['direct_calls']['callees'], [])
out = dict(kind='local-static-ROM-byte-verification; no firmware/model execution',rom=str(ROM),base=hex(BASE),
           core_inventory=record,windows=[dict(start=hex(a),end_exclusive=hex(z)) for a,z in windows],
           instructions=rows,checks=checks,summary=dict(bytes=sum(z-a for a,z in windows),instructions=len(rows),checks=len(checks)))
(HERE/'evidence.json').write_text(json.dumps(out,indent=2)+'\n',encoding='utf-8')
(HERE/'instructions.txt').write_text('\n'.join(f"{r['pc']} off={r['file_offset']} {r['raw']} {r['mnemonic']} {r['operands']}"+(f" => {r['target']}" if 'target' in r else '') for r in rows)+'\n',encoding='utf-8')
print(json.dumps(dict(result='passed',**out['summary'])))
