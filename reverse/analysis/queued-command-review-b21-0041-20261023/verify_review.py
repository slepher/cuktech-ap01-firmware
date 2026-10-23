"""B21 independent bounded static review. Reads ROM; never executes target code."""
import json
from pathlib import Path
from capstone import Cs, CS_ARCH_RISCV, CS_MODE_RISCV32, CS_MODE_RISCVC

ROOT = Path('D:/Documents/PlatformIO/Projects/cuktech-ap01-firmware')
HERE = Path(__file__).resolve().parent
SOURCE = ROOT / 'reverse/analysis/usb-interface-ota-0041-20261023.json'
ROM = ROOT / 'roms/0041/ap01-1.0.2_0041.bin'
data = json.loads(SOURCE.read_text(encoding='utf-8'))
rom = ROM.read_bytes()
decoder = Cs(CS_ARCH_RISCV, CS_MODE_RISCV32 | CS_MODE_RISCVC)
# Three full bodies, one full direct dependency and two targeted contract slices.
windows = {
    0xa01951e2: [(0xa01951e2, 0xa019530a)],
    0xa01915bc: [(0xa01915bc, 0xa0191652)],
    0xa00ee9ce: [(0xa00ee9ce, 0xa00eea08)],
    0xa00ee96c: [(0xa00ee96c, 0xa00ee9ce)],
    0xa00a8330: [(0xa00a83f8, 0xa00a8422), (0xa00a84ee, 0xa00a8552)],
    0xa00a8582: [(0xa00a8582, 0xa00a8602), (0xa00a873e, 0xa00a8794),
                 (0xa00a8820, 0xa00a8836),
                 (0xa00a8856, 0xa00a8870)],
}
rows, functions, by_pc = [], [], {}
for entry, ranges in windows.items():
    fn = next(f for f in data['functions'] if int(f['address'], 16) == entry)
    provider = {int(line.split(':')[0], 16): line.split(': ', 1)[1] for line in fn['assembly']}
    # All retained function bytes are checked, even for contract-only slices.
    for block in fn['raw_ranges']:
        raw = bytes.fromhex(block['bytes_hex'])
        assert rom[block['file_offset']:block['file_offset'] + len(raw)] == raw
    functions.append(dict(entry=hex(entry), ranges=[[hex(a), hex(b)] for a, b in ranges],
                          evidence_id=fn['evidence_id'], source=fn['source'],
                          profile=fn['profile_digest']))
    for start, end in ranges:
        pc = start
        while pc < end:
            offset = pc - 0x9ffff000
            prefix = int.from_bytes(rom[offset:offset + 2], 'little')
            size = 4 if prefix & 3 == 3 else 2
            raw = rom[offset:offset + size]
            decoded = list(decoder.disasm(raw, pc))
            assert len(decoded) == 1 and decoded[0].size == size, hex(pc)
            ins = decoded[0]
            row = dict(pc=hex(pc), offset=offset, raw=raw.hex(), mnemonic=ins.mnemonic,
                       operands=ins.op_str, retained=provider[pc])
            rows.append(row)
            by_pc[pc] = row
            pc += size
        assert pc == end

cache_source = ROOT / 'reverse/analysis/poll-phase-writer-b02-0041-20261023/instruction-evidence.json'
cache = next(w for w in json.loads(cache_source.read_text(encoding='utf-8'))['windows']
             if w['name'] == 'cache-helper')
functions.append(dict(entry='0xa0191652', ranges=[['0xa0191652', '0xa019166c']],
                      evidence_id=cache['evidence_id'], source=cache['source'],
                      retained_record=str(cache_source), scope='entry/state-clear contract only'))
for instruction in cache['instructions']:
    pc = int(instruction['address'], 16)
    if pc >= 0xa019166c:
        break
    raw = bytes.fromhex(instruction['hex'])
    offset = pc - 0x9ffff000
    assert rom[offset:offset + len(raw)] == raw
    decoded = list(decoder.disasm(raw, pc))
    assert len(decoded) == 1 and decoded[0].size == len(raw)
    ins = decoded[0]
    row = dict(pc=hex(pc), offset=offset, raw=raw.hex(), mnemonic=ins.mnemonic,
               operands=ins.op_str, retained=instruction['retained_assembly'])
    rows.append(row)
    by_pc[pc] = row

checks = []
def exact(pc, mnemonic, operands):
    row = by_pc[pc]
    assert (row['mnemonic'], row['operands']) == (mnemonic, operands), row
    checks.append(hex(pc))

for args in [
    (0xa01951fa, 'c.mv', 's2, a0'),
    (0xa0195224, 'lbu', 'a2, 2(s3)'),
    (0xa019522c, 'lw', 'a0, 4(s2)'),
    (0xa0195230, 'addi', 'a1, s3, 3'),
    (0xa019523c, 'c.beqz', 'a0, 0x60'),
    (0xa0195268, 'sb', 'a5, 0(s1)'),
    (0xa0195270, 'lbu', 'a2, 1(s2)'),
    (0xa0195274, 'lw', 'a1, 4(s2)'),
    (0xa0195278, 'sb', 'a5, 1(s1)'),
    (0xa0195280, 'sb', 'a2, 2(s1)'),
    (0xa0195290, 'addi', 'a0, s1, 3'),
    (0xa01952c4, 'lbu', 'a2, 1(a0)'),
    (0xa01952cc, 'sb', 'a5, 3(s1)'),
    (0xa01952d4, 'c.lw', 'a1, 4(a0)'),
    (0xa01952da, 'sb', 'a2, 4(s1)'),
    (0xa01952e8, 'sb', 'a5, 0(s1)'),
    (0xa0195302, 'lbu', 'a5, 0(s1)'),
    (0xa01915f8, 'lbu', 'a5, 0(s2)'),
    (0xa01915fe, 'lbu', 'a2, 2(s1)'),
    (0xa0191606, 'addi', 'a1, s1, 1'),
    (0xa019160a, 'c.addi', 'a2, 2'),
    (0xa0191618, 'lbu', 'a5, 0(s2)'),
    (0xa0191620, 'sb', 'a5, 0(s2)'),
    (0xa0191628, 'sb', 'zero, 0(s1)'),
    (0xa00ee9e2, 'lbu', 's2, 0(s1)'),
    (0xa00ee9f4, 'sb', 's2, 1(s1)'),
    (0xa00ee9f8, 'sb', 'zero, 2(s1)'),
    (0xa00ee99c, 'blez', 'a0, 0x28'),
    (0xa00ee9b2, 'bne', 'a5, a0, 0x12'),
    (0xa00ee9bc, 'sb', 'a4, 0x2f0(a5)'),
    (0xa00ee9c0, 'sh', 'zero, 0x5e(s1)'),
    (0xa00a851a, 'sb', 'a5, 0(s3)'),
    (0xa00a852e, 'lw', 'a5, 0(s4)'),
    (0xa00a8538, 'c.jalr', 'a5'),
    (0xa00a853a, 'lw', 'a5, 0(s4)'),
    (0xa00a853e, 'c.li', 'a2, 0'),
    (0xa00a8540, 'c.li', 'a1, 0'),
    (0xa00a8542, 'addi', 'a0, zero, 0x24'),
    (0xa00a8546, 'c.jalr', 'a5'),
    (0xa00a8548, 'sb', 'zero, 0x30(s1)'),
    (0xa00a85a0, 'sb', 'a0, -0x50(s0)'),
    (0xa00a85a4, 'sb', 'a1, -0x4f(s0)'),
    (0xa00a85a8, 'sw', 'a2, -0x4c(s0)'),
    (0xa00a8824, 'sh', 'a5, -0x48(s0)'),
    (0xa00a8828, 'sw', 'zero, -0x44(s0)'),
    (0xa00a885a, 'lbu', 'a4, 0x2ef(a5)'),
    (0xa0191668, 'sb', 'zero, 0x2f0(a5)'),
]:
    exact(*args)

def sign(value, bits):
    return value - (1 << bits) if value & (1 << (bits - 1)) else value

edges = []
for pc, target in [(0xa0191624, 0xa00ee9ce), (0xa01952ec, 0xa00ee9ce),
                   (0xa00ee9ec, 0xa01a4ff8), (0xa00ee9f0, 0xa00ee96c),
                   (0xa00ee998, 0xa0027e94), (0xa00a8510, 0xa000589c),
                   (0xa00a854c, 0xa00ee9ce), (0xa00a8830, 0xa01951e2),
                   (0xa00a8780, 0xa0191652),
                   (0xa00a8864, 0xa00a56d4), (0xa00a886a, 0xa01915bc)]:
    w = int.from_bytes(bytes.fromhex(by_pc[pc]['raw']), 'little')
    assert w & 127 == 0x6f and (w >> 7) & 31 == 1
    imm = (w >> 31) << 20 | ((w >> 12) & 255) << 12 | ((w >> 20) & 1) << 11 | ((w >> 21) & 1023) << 1
    assert (pc + sign(imm, 21)) & 0xffffffff == target
    edges.append(dict(pc=hex(pc), target=hex(target), encoding='JAL'))
for pc, target in [(0xa0195234, 0xa00501be), (0xa0195294, 0xa000589c),
                   (0xa01952fa, 0xa000589c), (0xa0191610, 0xa000589c)]:
    hi = int.from_bytes(bytes.fromhex(by_pc[pc]['raw']), 'little')
    lo = int.from_bytes(bytes.fromhex(by_pc[pc+4]['raw']), 'little')
    assert hi & 127 == 0x17 and (hi >> 7) & 31 == 1
    assert lo & 0x707f == 0x67 and (lo >> 7) & 31 == 1 and (lo >> 15) & 31 == 1
    assert (pc + sign(hi & 0xfffff000, 32) + sign(lo >> 20, 12)) & 0xfffffffe == target
    edges.append(dict(pc=hex(pc), target=hex(target), encoding='AUIPC/JALR'))

# Store width/source/base encoded independently from the disassembler text.
flow = []
for row in rows:
    mnemonic = row['mnemonic']
    if mnemonic in ('beq', 'bne', 'blt', 'bge', 'bltu', 'bgeu', 'beqz', 'bnez',
                    'blez', 'bgez', 'c.beqz', 'c.bnez', 'c.j', 'j', 'jal'):
        absolute = int(row['retained'].split(',')[-1].split()[-1], 16)
        delta = int(row['operands'].split(',')[-1].strip(), 0)
        pc = int(row['pc'], 16)
        assert (pc + delta) & 0xffffffff == absolute, row
        flow.append(dict(pc=row['pc'], target=hex(absolute)))
stores = []
for pc, width in [(0xa0195268, 0), (0xa0195280, 0), (0xa0191628, 0),
                  (0xa00ee9f4, 0), (0xa00ee9f8, 0), (0xa00ee9c0, 1),
                  (0xa00a851a, 0), (0xa00a8548, 0), (0xa00a8824, 1),
                  (0xa0191668, 0)]:
    w = int.from_bytes(bytes.fromhex(by_pc[pc]['raw']), 'little')
    assert w & 127 == 0x23 and (w >> 12) & 7 == width
    stores.append(dict(pc=hex(pc), bytes=1 << width, rs1=(w >> 15) & 31,
                       rs2=(w >> 20) & 31, immediate=sign(((w >> 25) << 5) | ((w >> 7) & 31),12)))

result = dict(task='B21', result='static_review_passed', rom=str(ROM), source=str(SOURCE),
              functions=functions, instructions=rows, exact_checks=checks,
              raw_call_edges=edges, raw_store_checks=stores, control_flow=flow,
              limits=['Static only; no historical script replay or guest execution.',
                      'Dispatcher/parser are contract slices, not whole-function certification.',
                      'No authentication of memcpy/memcmp source or lower write driver.'])
(HERE / 'review-evidence.json').write_text(json.dumps(result, ensure_ascii=False, indent=2)+'\n', encoding='utf-8')
print(json.dumps(dict(result=result['result'], functions=len(functions), instructions=len(rows),
                      exact_checks=len(checks), raw_call_edges=len(edges), raw_store_checks=len(stores),
                      control_flow=len(flow))))
