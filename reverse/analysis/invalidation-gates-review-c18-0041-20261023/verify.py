"""C18 independent static review. Reads ROM bytes, never executes target code."""
import json
from pathlib import Path
from capstone import Cs, CS_ARCH_RISCV, CS_MODE_RISCV32, CS_MODE_RISCVC

OUT = Path(__file__).resolve().parent
TREE = OUT.parents[2]
ROM = Path('D:/Documents/PlatformIO/Projects/cuktech-ap01-firmware/roms/0041/ap01-1.0.2_0041.bin')
BASE = 0x9ffff000
image = ROM.read_bytes()
prior = json.loads((TREE/'reverse/analysis/invalidation-gates-c17-0041-20261023/instruction-evidence.json').read_text())
decoder = Cs(CS_ARCH_RISCV, CS_MODE_RISCV32 | CS_MODE_RISCVC)
checks, windows, fields = [], [], {}

def sign(value, width):
    return value - (1 << width) if value >> (width - 1) else value

def check(pc, name, actual, expected):
    assert actual == expected, (hex(pc), name, actual, expected)
    checks.append(dict(pc=hex(pc), name=name, actual=actual, expected=expected))

def parse(pc, raw):
    """Independent bit fields for standard RV32/RVC classes in these windows."""
    value = int.from_bytes(raw, 'little')
    if len(raw) == 4:
        op = value & 127
        f = dict(opcode=op, rd=value >> 7 & 31, funct3=value >> 12 & 7,
                 rs1=value >> 15 & 31, rs2=value >> 20 & 31, funct7=value >> 25)
        if op in (3, 19, 103):
            f['imm'] = sign(value >> 20, 12)
        elif op == 35:
            f['imm'] = sign((value >> 25 << 5) | (value >> 7 & 31), 12)
        elif op == 55:
            f['imm'] = value & 0xfffff000
        elif op == 99:
            n = (value >> 31 << 12) | ((value >> 7 & 1) << 11) | ((value >> 25 & 63) << 5) | ((value >> 8 & 15) << 1)
            f['target'] = pc + sign(n, 13)
        elif op == 111:
            n = (value >> 31 << 20) | ((value >> 12 & 255) << 12) | ((value >> 20 & 1) << 11) | ((value >> 21 & 1023) << 1)
            f['target'] = pc + sign(n, 21)
        else:
            assert op == 51, (hex(pc), op)
        return f
    q, top = value & 3, value >> 13
    f = dict(quadrant=q, top=top)
    if q == 1 and top in (6, 7):
        n = ((value >> 12 & 1) << 8) | ((value >> 5 & 3) << 6) | ((value >> 2 & 1) << 5) | ((value >> 10 & 3) << 3) | ((value >> 3 & 3) << 1)
        f.update(rs1=8+(value >> 7 & 7), target=pc+sign(n, 9))
    elif q == 1 and top == 2:
        f.update(rd=value >> 7 & 31, imm=sign(((value >> 12 & 1) << 5) | (value >> 2 & 31), 6))
    elif q == 2 and top == 4:
        f.update(bit12=value >> 12 & 1, rd=value >> 7 & 31, rs2=value >> 2 & 31)
    elif q == 0 and top == 2:
        f.update(rd=8+(value >> 2 & 7), rs1=8+(value >> 7 & 7), imm=((value >> 5 & 1) << 6) | ((value >> 10 & 7) << 3) | ((value >> 6 & 1) << 2))
    elif q == 1 and top == 4:
        f.update(bit12=value >> 12 & 1, selector=value >> 10 & 3, operation=value >> 5 & 3, rd=8+(value >> 7 & 7), rs2=8+(value >> 2 & 7))
    elif q == 2 and top == 2:
        f.update(rd=value >> 7 & 31, rs1=2, imm=((value >> 2 & 3) << 6) | ((value >> 12 & 1) << 5) | ((value >> 4 & 7) << 2))
    return f

ranges = [(0xa00ddbf6,0xa00ddc7e),(0xa00ddd82,0xa00ddd90),(0xa0081804,0xa008184e),(0xa00d7446,0xa00d749e)]
for start, end in ranges:
    raw = image[start-BASE:end-BASE]
    instructions = list(decoder.disasm(raw, start))
    assert sum(i.size for i in instructions) == end-start
    rows = []
    for ins in instructions:
        f = parse(ins.address, ins.bytes)
        fields[ins.address] = f
        rows.append(dict(pc=hex(ins.address), raw=ins.bytes.hex(), assembly=ins.mnemonic+' '+ins.op_str, fields=f))
    old = next(w for w in prior['windows'] if int(w['start'],16) == start)
    check(start, 'C17 complete window byte/decode equality',
          [(r['pc'],r['raw'],r['assembly']) for r in rows],
          [(r['pc'],r['raw'],r['assembly']) for r in old['instructions']])
    windows.append(dict(start=hex(start), end_exclusive=hex(end), instructions=rows))

def expect(pc, **wanted):
    check(pc, 'independent instruction fields', {k:fields[pc][k] for k in wanted}, wanted)

expect(0xa00ddc04, quadrant=1, top=7, rs1=10, target=0xa00ddc46)
expect(0xa00ddc46, opcode=35, funct3=2, rs1=8, rs2=11, imm=-84)
expect(0xa00ddc4a, quadrant=2, top=4, bit12=0, rd=9, rs2=10)
for pc, target in [(0xa00ddc4c,0xa00dce2e),(0xa00ddc50,0xa0081804),(0xa00ddc60,0xa008b43a),(0xa00ddc68,0xa00d7446),(0xa00ddc76,0xa00ddab4)]:
    expect(pc, opcode=111, rd=1, target=target)
expect(0xa00ddc54, opcode=99, funct3=0, rs1=10, rs2=0, target=0xa00ddd82)
expect(0xa00ddc58, opcode=3, funct3=2, rd=11, rs1=8, imm=-84)
expect(0xa00ddc5c, opcode=19, funct3=0, rd=10, rs1=8, imm=-80)
expect(0xa00ddc64, quadrant=1, top=2, rd=11, imm=1)
expect(0xa00ddc66, quadrant=2, top=4, bit12=0, rd=10, rs2=9)
expect(0xa00ddc6c, opcode=99, funct3=1, rs1=10, rs2=0, target=0xa00ddd82)
expect(0xa00ddc70, opcode=19, funct3=0, rd=11, rs1=8, imm=-80)
expect(0xa00ddc74, quadrant=2, top=4, bit12=0, rd=10, rs2=9)
expect(0xa00ddc7a, opcode=99, funct3=0, rs1=10, rs2=0, target=0xa00ddd82)
for pc in (0xa0081804,0xa008180e):
    expect(pc, quadrant=1, top=7, rs1=10, target=0xa0081844)
expect(0xa0081806, opcode=55, rd=15, imm=0x62fc9000)
expect(0xa008180a, opcode=3, funct3=2, rd=10, rs1=15, imm=0x590)
expect(0xa0081844, opcode=3, funct3=2, rd=10, rs1=10, imm=0x268)
expect(0xa0081848, opcode=51, funct3=2, funct7=0, rd=10, rs1=0, rs2=10)
expect(0xa008183e, quadrant=1, top=2, rd=10, imm=0)
expect(0xa00d7446, quadrant=1, top=7, rs1=10, target=0xa00d7492)
expect(0xa00d7492, quadrant=0, top=2, rd=10, rs1=10, imm=0x24)
expect(0xa00d7494, quadrant=1, top=4, bit12=0, selector=3, operation=3, rd=10, rs2=11)
expect(0xa00d7496, quadrant=1, top=4, bit12=0, selector=3, operation=0, rd=10, rs2=11)
expect(0xa00d7498, opcode=19, funct3=3, rd=10, rs1=10, imm=1)
for pc, register, offset in [(0xa00ddd82,1,92),(0xa00ddd84,8,88),(0xa00ddd86,9,84),(0xa00ddd88,18,80),(0xa00ddd8a,19,76)]:
    expect(pc, quadrant=2, top=2, rd=register, rs1=2, imm=offset)
for pc in (0xa00ddd8e,0xa0081842,0xa008184c,0xa00d749c):
    expect(pc, quadrant=2, top=4, bit12=0, rd=1, rs2=0)
for pc, n, wanted in [(0xa00ddbf6,2,'1d71'),(0xa00ddc02,2,'8010'),(0xa00ddd8c,2,'2561')]:
    check(pc, 'frame -96; s0=sp+96; restore sp+96 (RVC raw)', image[pc-BASE:pc-BASE+n].hex(), wanted)

# Keep every direct target, including diagnostic-only calls, addressable.
targets = [dict(pc=hex(pc), target=hex(f['target'])) for pc,f in fields.items() if 'target' in f]
check(0xa00ddbf6, 'all 17 direct targets agree with prior evidence', targets, prior['targets'])
strings = []
for address, wanted in [(0xa056a378,'lv_obj_invalidate_area'),(0xa025f608,'lv_display_is_invalidation_enabled'),(0xa05699b4,'lv_obj_has_flag')]:
    offset = address-BASE
    text = image[offset:image.index(0,offset)].decode()
    check(address,'ROM source-name string',text,wanted)
    strings.append(dict(address=hex(address),text=text))
summary = dict(result='passed', windows=len(windows), bytes=sum(e-s for s,e in ranges), instructions=len(fields), independent_field_checks=sum(c['name']=='independent instruction fields' for c in checks), total_checks=len(checks), direct_targets=len(targets))
result = dict(task='C18',baseline='e29de84',rom=str(ROM),mapping_base=hex(BASE),summary=summary, windows=windows, contract_checks=checks, direct_targets=targets, strings=strings, limitations=['No target execution or firmware model','No source-version authentication','No a00dce2e or third-gate body analysis','Four-word-copy callee contract inherited from C15/C16'])
(OUT/'review-evidence.json').write_text(json.dumps(result,indent=2)+'\n')
print(json.dumps(summary))
