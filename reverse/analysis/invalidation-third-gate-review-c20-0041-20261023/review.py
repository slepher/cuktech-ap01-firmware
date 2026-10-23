"""C20: independent static ROM decoding and narrow contract checks; no emulation."""
import json
from pathlib import Path
from capstone import Cs, CS_ARCH_RISCV, CS_MODE_RISCV32, CS_MODE_RISCVC

HERE = Path(__file__).resolve().parent
TREE = HERE.parents[2]
SOURCE = Path('D:/Documents/PlatformIO/Projects/cuktech-ap01-firmware')
ROM = SOURCE / 'roms/0041/ap01-1.0.2_0041.bin'
BASE = 0x9ffff000
data = ROM.read_bytes()
prior = json.loads((TREE / 'reverse/analysis/invalidation-third-gate-c19-0041-20261023/instruction-evidence.json').read_text(encoding='utf-8'))
md = Cs(CS_ARCH_RISCV, CS_MODE_RISCV32 | CS_MODE_RISCVC)
checks, rows = [], []

def require(name, actual, expected):
    assert actual == expected, (name, actual, expected)
    checks.append({'check': name, 'actual': actual, 'expected': expected})

def signed(value, bits):
    return value - (1 << bits) if value >> (bits - 1) else value

def target(pc, bs):
    w = int.from_bytes(bs, 'little')
    if len(bs) == 4 and w & 127 == 0x63:
        return pc + signed(((w >> 31) << 12) | ((w >> 7 & 1) << 11) | ((w >> 25 & 63) << 5) | ((w >> 8 & 15) << 1), 13)
    if len(bs) == 4 and w & 127 == 0x6f:
        return pc + signed(((w >> 31) << 20) | ((w >> 12 & 255) << 12) | ((w >> 20 & 1) << 11) | ((w >> 21 & 1023) << 1), 21)
    if len(bs) == 2 and w & 3 == 1 and w >> 13 in (6, 7):
        return pc + signed(((w >> 12 & 1) << 8) | ((w >> 5 & 3) << 6) | ((w >> 2 & 1) << 5) | ((w >> 10 & 3) << 3) | ((w >> 3 & 3) << 1), 9)
    if len(bs) == 2 and w & 3 == 1 and w >> 13 == 5:
        return pc + signed(((w >> 12 & 1) << 11) | ((w >> 8 & 1) << 10) | ((w >> 9 & 3) << 8) | ((w >> 6 & 1) << 7) | ((w >> 7 & 1) << 6) | ((w >> 2 & 1) << 5) | ((w >> 11 & 1) << 4) | ((w >> 3 & 7) << 1), 12)
    return None

vendor = {0xa0089304: (16, 15, 14), 0xa0089314: (15, 14, 13), 0xa0089322: (13, 14, 17), 0xa0089330: (14, 11, 12)}
for win in prior['windows']:
    pc = int(win['start'], 16)
    for old in win['instructions']:
        require('continuous address', pc, int(old['pc'], 16))
        off = pc - BASE
        size = 4 if data[off] & 3 == 3 else 2
        bs = data[off:off+size]
        require(hex(pc) + ' retained bytes', bs.hex(), old['raw'])
        if pc in vendor:
            w = int.from_bytes(bs, 'little')
            rd, rs1, rs2 = vendor[pc]
            require(hex(pc) + ' vendor encoding', [w & 127, w >> 12 & 7, w >> 25, w >> 7 & 31, w >> 15 & 31, w >> 20 & 31], [11, 1, 33, rd, rs1, rs2])
            asm = f'th.mvnez x{rd},x{rs1},x{rs2}'
        else:
            decoded = list(md.disasm(bs, pc))
            require(hex(pc) + ' one decoded instruction', len(decoded), 1)
            require(hex(pc) + ' decoded width', decoded[0].size, size)
            asm = decoded[0].mnemonic + ' ' + decoded[0].op_str
            require(hex(pc) + ' retained decode', asm, old['assembly'])
        row = {'address': hex(pc), 'offset': off, 'bytes': bs.hex(), 'instruction': asm}
        dest = target(pc, bs)
        if dest is not None:
            row['target'] = hex(dest)
            require(hex(pc) + ' target', hex(dest), old['target'])
        rows.append(row)
        pc += size
    require('window end', pc, int(win['end_exclusive'], 16))

by_pc = {int(r['address'], 16): r for r in rows}
expected = {
    0xa00ddada: ('bne s3, a0, 0xaa', 0xa00ddb84),
    0xa00ddb10: ('beqz a0, 0xca', 0xa00ddbda),
    0xa00ddb28: ('c.beqz s1, 0xb4', 0xa00ddbdc),
    0xa00ddb32: ('c.bnez a0, 0xa8', 0xa00ddbda),
    0xa00ddbb8: ('beq s3, s5, -0xda', 0xa00ddade),
    0xa00ddbc2: ('beq s3, a0, -0xe4', 0xa00ddade),
    0xa00ddbcc: ('beq s3, a0, -0xee', 0xa00ddade),
    0xa00ddbd6: ('beq s3, a0, -0xf8', 0xa00ddade),
    0xa00ddb80: ('c.bnez a0, -0x5a', 0xa00ddb26),
    0xa00ddc7a: ('beqz a0, 0x108', 0xa00ddd82),
}
for pc, (asm, dest) in expected.items():
    require(hex(pc) + ' branch polarity', by_pc[pc]['instruction'], asm)
    require(hex(pc) + ' branch destination', by_pc[pc]['target'], hex(dest))

model_path = SOURCE / 'evidence/rea-0041-20261017/ghidra/Ghidra/Processors/RISCV/data/languages/ap01thead2.sinc'
lines = model_path.read_text().splitlines()
line = next(i for i, s in enumerate(lines) if s.startswith(':th.mvnez '))
model = '\n'.join(lines[line:line+6])
require('existing mvnez model', model, ':th.mvnez rd,rs1,rs2 is op0006=0xb & op1214=1 & op2531=33 & rd & rs1 & rs2\n{\n  if (rs2 == 0) goto <done>;\n  rd = rs1;\n<done>\n}')
output = {'method': 'fresh ROM decoding; retained C19 evidence compared, not executed', 'rom': str(ROM), 'mapping': 'offset=address-0x9ffff000', 'instructions': rows, 'checks': checks, 'vendor_model': {'path': str(model_path), 'line': line+1, 'text': model}}
(HERE / 'review-evidence.json').write_text(json.dumps(output, ensure_ascii=False, indent=2)+'\n', encoding='utf-8')
(HERE / 'instructions.txt').write_text('\n'.join(f"{r['address']} off={r['offset']:#x} {r['bytes']:8} {r['instruction']}" + (f" => {r['target']}" if 'target' in r else '') for r in rows)+'\n', encoding='utf-8')
print(json.dumps({'result': 'passed', 'windows': len(prior['windows']), 'instructions': len(rows), 'bytes': sum(len(r['bytes'])//2 for r in rows), 'checks': len(checks)}))
