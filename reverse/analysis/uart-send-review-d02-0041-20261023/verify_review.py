"""D02 independent static instruction review; never executes target instructions."""
import json
from pathlib import Path
from capstone import Cs, CS_ARCH_RISCV, CS_MODE_RISCV32, CS_MODE_RISCVC

HERE = Path(__file__).resolve().parent
ROOT = Path('D:/Documents/PlatformIO/Projects/cuktech-ap01-firmware')
ROM = ROOT / 'roms/0041/ap01-1.0.2_0041.bin'
BASE = 0x9ffff000
raw = ROM.read_bytes()
prior = json.loads((HERE.parent / 'uart-send-lifecycle-d01-0041-20261023/instruction-evidence.json').read_text(encoding='utf-8'))
old = {int(i['pc'], 16): i for w in prior['windows'] for i in w['instructions']}
decoder = Cs(CS_ARCH_RISCV, CS_MODE_RISCV32 | CS_MODE_RISCVC)
# Full new bodies, narrowly selected previously accepted interface windows.
regions = [
    ('submit_contract', 0xa01952c0, 0xa019530a),
    ('queue_release_contract', 0xa01915f8, 0xa019162c),
    ('start', 0xa00ee9ce, 0xa00eea08),
    ('frame', 0xa01a4ff8, 0xa01a50fe),
    ('progress', 0xa00ee96c, 0xa00ee9ce),
    ('wrapper', 0xa0027e94, 0xa0027eee),
    ('operation', 0xa0025874, 0xa00258a0),
    ('response_contract', 0xa00a84ee, 0xa00a8552),
    ('event24_contract', 0xa00a8856, 0xa00a8870),
    ('cmd58_contract', 0xa00a876e, 0xa00a8794),
    ('cache_idle_contract', 0xa0191652, 0xa019166c),
    ('cmd58_selector_join', 0xa00a8aae, 0xa00a8ab4),
]
vendors = {
    0xa01a5052: (5, 0, 10, 20, 15, 0),
    0xa01a5064: (5, 0, 10, 14, 15, 0),
    0xa01a50b0: (5, 0, 13, 15, 14, 0),
    0xa01a50b6: (4, 16, 10, 11, 19, 0),
    0xa01a50ca: (5, 0, 17, 15, 14, 0),
    0xa01a50da: (5, 0, 10, 15, 14, 0),
}
rows, windows = {}, []
for label, begin, end in regions:
    pc, instructions = begin, []
    while pc < end:
        offset = pc - BASE
        word = int.from_bytes(raw[offset:offset+4], 'little')
        size = 4 if word & 3 == 3 else 2
        assert pc + size <= end
        b = raw[offset:offset+size]
        if pc in old:
            assert b.hex() == old[pc]['bytes'], hex(pc)
        if word & 127 == 11 and size == 4:
            fields = ((word >> 12) & 7, (word >> 27) & 31, (word >> 7) & 31,
                      (word >> 15) & 31, (word >> 20) & 31, (word >> 25) & 3)
            assert fields == vendors[pc]
            mnemonic, operands = 'th.srb' if fields[0] == 5 else 'th.lrbu', str(fields)
        else:
            ins = list(decoder.disasm(b, pc))
            assert len(ins) == 1 and ins[0].size == size, hex(pc)
            mnemonic, operands = ins[0].mnemonic, ins[0].op_str
        row = dict(pc=hex(pc), file_offset=offset, bytes=b.hex(), mnemonic=mnemonic, operands=operands)
        rows[pc] = row
        instructions.append(row)
        pc += size
    windows.append(dict(name=label, start=hex(begin), end_exclusive=hex(end), instructions=instructions))

checks = []
def exact(pc, text):
    r = rows[pc]
    assert r['mnemonic'] + ' ' + r['operands'] == text, (hex(pc), r)
    checks.append(dict(pc=hex(pc), expected=text))

for pc, text in {
    0xa01a501a:'sb a4, 0x5e(a5)', 0xa01a502e:'sh a5, 0x48c(s1)',
    0xa01a5036:'lbu s4, 4(s2)', 0xa01a5042:'addi a2, s4, 2',
    0xa01a5056:'lbu a4, 4(s2)', 0xa01a5062:'c.srli a0, 8',
    0xa01a5068:'lbu a3, 4(s2)', 0xa01a5072:'andi a3, a3, 0xff',
    0xa01a50a0:'lbu a4, 0x5e(a5)', 0xa01a50a8:'sb a3, 0x5e(a5)',
    0xa01a50ce:'andi a4, a2, 0xff', 0xa01a50d6:'andi a2, a2, 0xff',
    0xa00ee97e:'lbu a2, 0x5e(s1)', 0xa00ee984:'lbu a1, 0x5f(s1)',
    0xa00ee98c:'lw a0, 0x1b0(a5)', 0xa00ee992:'andi a2, a2, 0xff',
    0xa00ee9a0:'lbu a5, 0x5f(s1)', 0xa00ee9a6:'lbu a5, 0x5e(s1)',
    0xa00ee9aa:'andi a0, a0, 0xff', 0xa00ee9ae:'sb a0, 0x5f(s1)',
    0xa00ee9bc:'sb a4, 0x2f0(a5)', 0xa00ee9c0:'sh zero, 0x5e(s1)',
    0xa0027ea4:'c.mv s2, a1', 0xa0027eaa:'sw a2, -0x24(s0)',
    0xa0027eb8:'lw a2, -0x24(s0)', 0xa0027ebc:'lw a0, -0x14(s0)',
    0xa0027ec0:'c.mv a1, s2', 0xa0027ec6:'c.mv s1, a0',
    0xa0027ec8:'lw a0, -0x14(s0)', 0xa0027ee6:'c.mv a0, s1',
    0xa0025874:'c.lw a5, 0(a0)', 0xa0025876:'c.andi a5, 2',
    0xa002587a:'c.lw a4, 0xc(a0)', 0xa0025880:'c.lw a4, 0x10(a4)',
    0xa0025884:'c.lw a4, 0xc(a4)', 0xa0025890:'c.jalr a4',
    0xa00a851a:'sb a5, 0(s3)', 0xa00a852e:'lw a5, 0(s4)',
    0xa00a8538:'c.jalr a5', 0xa00a853a:'lw a5, 0(s4)',
    0xa00a8546:'c.jalr a5', 0xa00a8548:'sb zero, 0x30(s1)',
    0xa0191668:'sb zero, 0x2f0(a5)', 0xa0191628:'sb zero, 0(s1)',
    0xa0195302:'lbu a5, 0(s1)', 0xa00ee9f4:'sb s2, 1(s1)',
}.items():
    exact(pc, text)

def sign(n, bits):
    return n - (1 << bits) if n & (1 << (bits - 1)) else n

# Decode J/B immediates directly, separately from Capstone targets.
edges = []
for pc, target in {
    0xa01a5032:0xa00ee8fc, 0xa01a5046:0xa00ee8fc,
    0xa00ee998:0xa0027e94, 0xa0027eae:0xa0025904,
    0xa0027ec2:0xa0025874, 0xa0027ecc:0xa0027e54,
    0xa00ee99c:0xa00ee9c4, 0xa00ee9b2:0xa00ee9c4,
    0xa01a50ba:0xa01a50c6, 0xa01a50be:0xa01a50c6,
    0xa01a50c2:0xa01a50d2, 0xa01a50de:0xa01a50f6,
    0xa00a8780:0xa0191652, 0xa00a8aae:0xa0191746,
    0xa00a854c:0xa00ee9ce, 0xa00a886a:0xa01915bc,
}.items():
    w = int.from_bytes(bytes.fromhex(rows[pc]['bytes']), 'little')
    if w & 127 == 0x6f:
        imm = ((w >> 31) << 20) | (((w >> 12) & 255) << 12) | (((w >> 20) & 1) << 11) | (((w >> 21) & 1023) << 1)
        actual = (pc + sign(imm, 21)) & 0xffffffff
    else:
        assert w & 127 == 0x63
        imm = ((w >> 31) << 12) | (((w >> 7) & 1) << 11) | (((w >> 25) & 63) << 5) | (((w >> 8) & 15) << 1)
        actual = (pc + sign(imm, 13)) & 0xffffffff
    assert actual == target, (hex(pc), hex(actual))
    edges.append(dict(pc=hex(pc), target=hex(target)))
# Critical B opcodes: signed <=0 and exact inequality, not unsigned/threshold completion.
for pc, funct3, rs1, rs2 in [(0xa00ee99c,5,0,10),(0xa00ee9b2,1,15,10),(0xa01a50de,7,29,12)]:
    w = int.from_bytes(bytes.fromhex(rows[pc]['bytes']), 'little')
    assert ((w >> 12)&7,(w >> 15)&31,(w >> 20)&31) == (funct3,rs1,rs2)

# S-format encoding independently establishes byte / halfword stores.
stores = []
for pc, width, rs1, rs2, displacement in [
    (0xa01a501a,0,15,14,94),(0xa01a502e,1,9,15,1164),
    (0xa00ee9ae,0,9,10,95),(0xa00ee9bc,0,15,14,752),
    (0xa00ee9c0,1,9,0,94),(0xa0191668,0,15,0,752),
]:
    w = int.from_bytes(bytes.fromhex(rows[pc]['bytes']), 'little')
    actual = (w&127,(w>>12)&7,(w>>15)&31,(w>>20)&31,sign(((w>>25)<<5)|((w>>7)&31),12))
    assert actual == (0x23,width,rs1,rs2,displacement)
    stores.append(dict(pc=hex(pc), fields=actual))

model = ROOT / 'evidence/rea-0041-20261017/ghidra/Ghidra/Processors/RISCV/data/languages/ap01thead2.sinc'
lines = model.read_text(encoding='utf-8').splitlines()
excerpts = []
for name in (':th.srb ', ':th.lrbu '):
    start = next(i for i,s in enumerate(lines) if s.startswith(name))
    stop = next(i for i in range(start+1,len(lines)) if lines[i] == '}')
    excerpts.append(dict(line=start+1,text='\n'.join(lines[start:stop+1])))
result = dict(task='D02', result='independent_static_checks_passed', rom=str(ROM), mapping_base=hex(BASE),
              windows=windows, exact_operand_checks=checks, direct_raw_edges=edges, raw_stores=stores,
              vendor_fields={hex(k):v for k,v in vendors.items()}, vendor_model=dict(path=str(model),excerpts=excerpts),
              provenance=prior['provenance'],
              limits=['No target execution or recorded-input replay.', 'Vendor semantics use retained local SLEIGH, not vendor source certification.',
                      'Existing queue/CRC/parser/cache contracts retained; no claim of full dispatcher review.',
                      'Driver, acquire/release internals, cold-start cursor, callback lifetime and final destruction remain unknown.'])
(HERE/'review-evidence.json').write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
print(json.dumps(dict(result=result['result'],windows=len(windows),instructions=len(rows),exact_checks=len(checks),raw_edges=len(edges),raw_stores=len(stores),vendor_words=len(vendors))))
