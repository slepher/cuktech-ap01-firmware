"""C10 independent static checks. Reads ROM; never executes target code."""
import json
import struct
from pathlib import Path
from capstone import Cs, CS_ARCH_RISCV, CS_MODE_RISCV32, CS_MODE_RISCVC

HERE = Path(__file__).resolve().parent
TREE = HERE.parents[2]
SOURCE = Path('D:/Documents/PlatformIO/Projects/cuktech-ap01-firmware')
ROM = SOURCE / 'roms/0041/ap01-1.0.2_0041.bin'
rom = ROM.read_bytes()
base = 0x9ffff000
prior = json.loads((HERE.parent / 'detail-summary-c09-0041-20261023/instruction-evidence.json').read_text(encoding='utf-8'))
md = Cs(CS_ARCH_RISCV, CS_MODE_RISCV32 | CS_MODE_RISCVC)
insns, windows = {}, []
for window in prior['windows']:
    start, end = int(window['start'], 16), int(window['end_exclusive'], 16)
    pc = start
    out = []
    for saved in window['instructions']:
        assert pc == int(saved['address'], 16)
        h = int.from_bytes(rom[pc-base:pc-base+2], 'little')
        size = 4 if h & 3 == 3 else 2
        raw = rom[pc-base:pc-base+size]
        assert raw.hex() == saved['hex']
        decoded = next(md.disasm(raw, pc), None)
        if decoded:
            asm = decoded.mnemonic + ' ' + decoded.op_str
            assert asm == saved['assembly']
        else:
            asm = 'vendor encoding checked separately'
        insns[pc] = (int.from_bytes(raw, 'little'), size, decoded)
        out.append({'address': hex(pc), 'hex': raw.hex(), 'assembly': asm})
        pc += size
    assert pc == end
    windows.append({'name': window['name'], 'start': hex(start), 'end_exclusive': hex(end), 'instructions': out})

def sign(v, bits):
    return v - (1 << bits) if v & (1 << (bits - 1)) else v

# Independently unpack JAL and compressed conditional branch immediate fields.
direct = {}
for pc, expected in {
    0xa00f3852:0xa00a5c50, 0xa00f385e:0xa00dcee4,
    0xa00f3864:0xa00dcee4, 0xa00f387c:0xa0091ee4,
    0xa00a5c86:0xa008b51a, 0xa00f3a2e:0xa00a72ae,
    0xa00f3b04:0xa008b51a, 0xa00f3b0c:0xa00f3844,
}.items():
    w, size, _ = insns[pc]
    assert size == 4 and w & 127 == 0x6f and (w >> 7) & 31 == 1
    imm = ((w >> 31) << 20) | (((w >> 21) & 1023) << 1) | (((w >> 20) & 1) << 11) | (((w >> 12) & 255) << 12)
    dest = (pc + sign(imm, 21)) & 0xffffffff
    assert dest == expected
    direct[hex(pc)] = hex(dest)
branches = {}
for pc, expected in {0xa00a5c58:0xa00a5c60, 0xa00dcee4:0xa00dcf30,
                     0xa00dcf32:0xa00dcf50, 0xa00f3a32:0xa00f3a40,
                     0xa00f3a38:0xa00f3a40, 0xa00f3a3e:0xa00f3aee}.items():
    w, size, _ = insns[pc]
    assert size == 2 and (w >> 13) in (6, 7)
    imm = (((w >> 12) & 1) << 8) | (((w >> 10) & 3) << 3) | (((w >> 5) & 3) << 6) | (((w >> 3) & 3) << 1) | (((w >> 2) & 1) << 5)
    dest = pc + sign(imm, 9)
    assert dest == expected
    branches[hex(pc)] = hex(dest)

# Opcode/funct3 and register fields confirm load widths independently of text.
loads = []
for pc, rd, rs1, funct3, imm in [
    (0xa00f3858,10,18,2,0), (0xa00a5c54,15,15,2,0x2cc),
    (0xa00a5c5a,10,15,4,8), (0xa00dcf34,15,10,5,0x30),
    (0xa00f3b08,10,8,2,-0x34),
]:
    w, size, _ = insns[pc]
    fields = [w & 127, (w >> 7) & 31, (w >> 15) & 31, (w >> 12) & 7, sign(w >> 20,12)]
    assert size == 4 and fields == [3,rd,rs1,funct3,imm]
    loads.append({'address':hex(pc), 'fields':fields})
vendors = []
for pc, rd, rs1, rs2 in [(0xa00f3870,12,15,9),(0xa00dcf48,10,15,11)]:
    w, size, _ = insns[pc]
    fields = [w & 127, (w >> 12) & 7, w >> 27, (w >> 25) & 3,
              (w >> 7) & 31, (w >> 15) & 31, (w >> 20) & 31]
    assert size == 4 and fields == [11,4,8,2,rd,rs1,rs2]
    vendors.append({'address':hex(pc), 'word':hex(w), 'fields_op_f3_f5_shift_rd_rs1_rs2':fields})

model = SOURCE / 'evidence/rea-0041-20261017/ghidra/Ghidra/Processors/RISCV/data/languages/ap01thead2.sinc'
lines = model.read_text(encoding='utf-8').splitlines()
i = next(i for i,s in enumerate(lines) if s.startswith(':th.lrw '))
j = next(j for j in range(i+1,len(lines)) if lines[j] == '}')
excerpt = '\n'.join(lines[i:j+1])
assert excerpt == prior['model_excerpt']['text']
pointers = list(struct.unpack_from('<4I',rom,0xa01c473c-base))
assert [hex(p) for p in pointers] == prior['mode_table']['pointers']
for item in prior['strings']:
    offset = int(item['address'],16) - base
    raw = rom[offset:rom.index(b'\0',offset)+1]
    assert raw.hex() == item['hex'] and raw[:-1].decode() == item['text']

checks = {'result':'passed','windows':len(windows),'bytes':sum(int(w['end_exclusive'],16)-int(w['start'],16) for w in windows),
          'ordinary_instructions':sum(v[2] is not None for v in insns.values()),
          'vendor_words':len(vendors),'independent_jal_targets':len(direct),
          'independent_compressed_branches':len(branches),'load_encoding_checks':len(loads),
          'table_pointers':len(pointers),'strings':len(prior['strings'])}
out = {'task':'C10','rom_path':str(ROM),'mapping_base':hex(base),'checks':checks,'windows':windows,
       'jal_targets':direct,'compressed_branch_targets':branches,'load_encodings':loads,'vendor_encodings':vendors,
       'model':{'path':str(model),'line':i+1,'text':excerpt},
       'limits':['Static ROM reading/decoding only; no firmware execution.',
                 'Vendor semantics remain dependent on the existing local model.',
                 'Formatter, snapshot consistency and object ownership remain unreviewed.']}
(HERE/'review-evidence.json').write_text(json.dumps(out,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
print(json.dumps(checks))
