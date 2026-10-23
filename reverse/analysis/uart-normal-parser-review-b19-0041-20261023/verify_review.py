"""B19: decode fixed ROM ranges; assert parser state stores and static edges.

Reads local files only. No firmware execution, emulation, hashing or byte streams.
Does not execute or import any earlier investigation script.
"""
import json
from pathlib import Path
import capstone
from capstone import Cs, CS_ARCH_RISCV, CS_MODE_RISCV32, CS_MODE_RISCVC

HERE = Path(__file__).resolve().parent
SOURCE = Path('D:/Documents/PlatformIO/Projects/cuktech-ap01-firmware')
ROM = SOURCE / 'roms/0041/ap01-1.0.2_0041.bin'
RECORD = SOURCE / 'reverse/analysis/usb-interface-ota-0041-20261023.json'
BASE = 0x9ffff000
rom = ROM.read_bytes()
record = json.loads(RECORD.read_text(encoding='utf-8'))
decoder = Cs(CS_ARCH_RISCV, CS_MODE_RISCV32 | CS_MODE_RISCVC)
rows, by_pc, functions = [], {}, []

# Start/end addresses selected from the two bounded function bodies. Each
# instruction boundary below comes from ROM prefix bits, not provider rows.
for start, end in ((0xa00a8330, 0xa00a8582), (0xa00ee934, 0xa00ee96c)):
    fn = next(f for f in record['functions'] if int(f['address'], 16) == start)
    provider = {int(s.split(':')[0], 16): s.split(': ', 1)[1] for s in fn['assembly']}
    for block in fn['raw_ranges']:
        raw = bytes.fromhex(block['bytes_hex'])
        assert rom[block['file_offset']:block['file_offset'] + len(raw)] == raw
    pc = start
    count = 0
    while pc < end:
        offset = pc - BASE
        half = int.from_bytes(rom[offset:offset + 2], 'little')
        size = 4 if half & 3 == 3 else 2
        raw = rom[offset:offset + size]
        assert pc in provider, hex(pc)
        if pc == 0xa00ee94e:
            word = int.from_bytes(raw, 'little')
            fields = dict(opcode=word & 127, funct3=(word >> 12) & 7,
                          high=word >> 27, source=(word >> 7) & 31,
                          base=(word >> 15) & 31, index=(word >> 20) & 31,
                          shift=(word >> 25) & 3)
            assert fields == dict(opcode=11, funct3=5, high=0, source=10,
                                  base=15, index=13, shift=0)
            mnemonic, operands = 'th.srb', 'a0, a5, a3, 0'
        else:
            insns = list(decoder.disasm(raw, pc))
            assert len(insns) == 1 and insns[0].size == size, hex(pc)
            mnemonic, operands = insns[0].mnemonic, insns[0].op_str
        row = dict(pc=hex(pc), file_offset=offset, bytes=raw.hex(),
                   mnemonic=mnemonic, operands=operands, provider=provider[pc])
        rows.append(row)
        by_pc[pc] = row
        pc += size
        count += 1
    assert pc == end and count == len(provider)
    functions.append(dict(entry=hex(start), end_exclusive=hex(end),
                          instruction_count=count, evidence_id=fn['evidence_id'],
                          retained_source=fn['source']['path'],
                          retained_profile=fn['profile_digest']))

checks = []
def exact(pc, mnemonic, operands, meaning):
    row = by_pc[pc]
    assert (row['mnemonic'], row['operands']) == (mnemonic, operands), hex(pc)
    checks.append(dict(pc=hex(pc), claim=meaning, checked='mnemonic/operands'))

for args in [
 (0xa00a83f8, 'lui', 's1, 0x62fcb', 'parser base upper'),
 (0xa00a8400, 'addi', 's1, s1, 0x458', 'parser base=62fcb458'),
 (0xa00a8418, 'c.li', 's4, 3', 'stage3 gate constant'),
 (0xa00a8432, 'lbu', 'a0, 6(a4)', 'raw byte lives in a0'),
 (0xa00a8442, 'lbu', 'a5, 0x30(s1)', 'old stage byte in a5'),
 (0xa00a8446, 'sb', 'a4, 4(s2)', 'read cursor committed before stage3 gate'),
 (0xa00a8486, 'lbu', 'a4, 0x31(s1)', 'escape read byte'),
 (0xa00a848c, 'addi', 'a4, zero, 0xa5', 'A5 compare constant'),
 (0xa00a8494, 'c.li', 'a5, 1', 'A5 value for halfword write'),
 (0xa00a8496, 'sb', 'zero, 0x2f(s1)', 'A5 clears count byte'),
 (0xa00a849a, 'sh', 'a5, 0x30(s1)', 'A5 writes stage1 AND escape0'),
 (0xa00a84a0, 'addi', 'a4, zero, 0xaa', 'AA compare constant'),
 (0xa00a84a8, 'c.li', 'a5, 1', 'AA producer value'),
 (0xa00a84aa, 'sb', 'a5, 0x31(s1)', 'AA sets escape byte'),
 (0xa00a84b0, 'c.li', 'a4, 1', 'stage1 consumer constant'),
 (0xa00a84b6, 'addi', 'a5, zero, 0x5a', 'tail marker constant'),
 (0xa00a84be, 'lbu', 's11, 0x2f(s1)', 'count byte read'),
 (0xa00a84c8, 'c.li', 'a4, 2', 'stage2 producer value'),
 (0xa00a84ca, 'addi', 'a2, s11, -2', 'CRC length count-2'),
 (0xa00a84ce, 'c.mv', 'a1, s1', 'CRC data pointer'),
 (0xa00a84d0, 'c.li', 'a0, 0', 'CRC initial argument'),
 (0xa00a84d2, 'sb', 'a4, 0x30(s1)', 'stage2 byte store before CRC'),
 (0xa00a84f2, 'sb', 's4, 0x30(s1)', 'stage3 byte store on CRC equality'),
 (0xa00a8548, 'sb', 'zero, 0x30(s1)', 'success clears only stage byte'),
 (0xa00a8568, 'sb', 'zero, 0x2f(s1)', 'existing CRC mismatch cleanup count'),
 (0xa00a856c, 'sb', 'zero, 0x30(s1)', 'existing cleanup stage byte'),
 (0xa00a8572, 'sb', 'zero, 0x31(s1)', 'escape consumer clears byte first'),
 (0xa00a8576, 'c.li', 'a4, 1', 'escape consumer compares saved stage'),
 (0xa00ee93e, 'addi', 'a5, a5, 0x458', 'append base lower'),
 (0xa00ee942, 'lbu', 'a3, 0x2f(a5)', 'append uses old count index'),
 (0xa00ee946, 'addi', 'a4, a3, 1', 'append count increment'),
 (0xa00ee94a, 'andi', 'a4, a4, 0xff', 'append count byte truncation'),
 (0xa00ee952, 'sb', 'a4, 0x2f(a5)', 'append commits count byte'),
 (0xa00ee95e, 'sb', 'zero, 0x2f(a5)', 'retained append count reset'),
 (0xa00ee962, 'sb', 'zero, 0x30(a5)', 'retained append stage reset only'),
]:
    exact(*args)

edges = []
for pc, target in [
 (0xa00a844a, 0xa00a8486), (0xa00a844e, 0xa00ee96c),
 (0xa00a848a, 0xa00a8572), (0xa00a8490, 0xa00a84a0),
 (0xa00a849e, 0xa00a8422), (0xa00a84a4, 0xa00a84b0),
 (0xa00a84ae, 0xa00a8422), (0xa00a84b2, 0xa00a8422),
 (0xa00a84ba, 0xa00a857c), (0xa00a84c4, 0xa00a856c),
 (0xa00a84d8, 0xa00ee8fc), (0xa00a84ea, 0xa00a8552),
 (0xa00a84f6, 0xa00a8548), (0xa00a8502, 0xa00a8548),
 (0xa00a8532, 0xa00a8548), (0xa00a854c, 0xa00ee9ce),
 (0xa00a8550, 0xa00a8414), (0xa00a8578, 0xa00a8422),
 (0xa00a857c, 0xa00ee934), (0xa00a8580, 0xa00a8422),
 (0xa00ee95a, 0xa00ee966),
]:
    row = by_pc[pc]
    assert pc + int(row['operands'].split(',')[-1].strip(), 0) == target
    edges.append(dict(pc=hex(pc), target=hex(target), mnemonic=row['mnemonic']))

# The escape path performs no instruction that writes a0 before append.
assert [by_pc[p]['mnemonic'] for p in (0xa00a8572, 0xa00a8576, 0xa00a8578, 0xa00a857c)] == ['sb','c.li','bne','jal']
assert all('a0' not in by_pc[p]['operands'] for p in (0xa00a8572, 0xa00a8576, 0xa00a8578))
store_fields = []
for pc, rs2, offset, width in [
 (0xa00a8496, 0, 0x2f, 0), (0xa00a849a, 15, 0x30, 1),
 (0xa00a84aa, 15, 0x31, 0), (0xa00a84d2, 14, 0x30, 0),
 (0xa00a84f2, 20, 0x30, 0), (0xa00a8548, 0, 0x30, 0),
 (0xa00a8572, 0, 0x31, 0),
]:
    word = int.from_bytes(bytes.fromhex(by_pc[pc]['bytes']), 'little')
    actual = dict(opcode=word & 127, width=(word >> 12) & 7,
                  base=(word >> 15) & 31, source=(word >> 20) & 31,
                  displacement=((word >> 25) << 5) | ((word >> 7) & 31))
    assert actual == dict(opcode=35, width=width, base=9, source=rs2, displacement=offset)
    store_fields.append(dict(pc=hex(pc), fields=actual))
MODEL = SOURCE / 'evidence/rea-0041-20261017/processor/data/languages/ap01thead2.sinc'
model_text = MODEL.read_text(encoding='utf-8')
vendor_semantic = model_text.split(':th.srb ', 1)[1].split(':th.sbib ', 1)[0]
assert 'local delta:4 = rs2 << thshift;' in vendor_semantic
assert 'local updated:4 = rs1 + delta;' in vendor_semantic
assert '*[ram]:1 ea = rd:1;' in vendor_semantic
assert 'thbase = updated;' not in vendor_semantic
result = dict(task='B19', result='static_review_passed', capstone=capstone.__version__,
              rom=str(ROM), retained_record=str(RECORD), mapping_base=hex(BASE),
              functions=functions, vendor_encoding_fields=fields,
              vendor_model=str(MODEL), vendor_semantic=vendor_semantic.strip(),
              raw_store_fields=store_fields,
              exact_checks=checks, edges=edges, instructions=rows,
              limits=['Static instruction inspection only; no execution or input generation.',
                      'Vendor byte-store semantic tied to retained SLEIGH model, not an ISA certification.',
                      'CRC internals and dispatch ABI referenced, not reviewed again.'])
(HERE / 'review-evidence.json').write_text(json.dumps(result, ensure_ascii=False, indent=2)+'\n', encoding='utf-8')
print(json.dumps(dict(result=result['result'], instructions=len(rows), exact_checks=len(checks), edges=len(edges))))
