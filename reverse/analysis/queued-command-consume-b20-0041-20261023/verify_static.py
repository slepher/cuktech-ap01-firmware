"""B20 bounded static ROM decoding. No firmware execution or historical scripts.

Only reads the selected ROM/retained dossier, writes this task's JSON.
No hashes, shared databases, live targets or network calls.
"""
import json
from pathlib import Path
import capstone
from capstone import Cs, CS_ARCH_RISCV, CS_MODE_RISCV32, CS_MODE_RISCVC

HERE = Path(__file__).resolve().parent
SOURCE = Path('D:/Documents/PlatformIO/Projects/cuktech-ap01-firmware')
RECORD = SOURCE / 'reverse/analysis/usb-interface-ota-0041-20261023.json'
ROM = SOURCE / 'roms/0041/ap01-1.0.2_0041.bin'
BASE = 0x9ffff000
rom = ROM.read_bytes()
record = json.loads(RECORD.read_text(encoding='utf-8'))
decoder = Cs(CS_ARCH_RISCV, CS_MODE_RISCV32 | CS_MODE_RISCVC)
rows, functions, by_pc = [], [], {}
for start, end in ((0xa01915bc, 0xa0191652), (0xa00ee9ce, 0xa00eea08)):
    fn = next(f for f in record['functions'] if int(f['address'], 16) == start)
    provider = {int(s.split(':')[0], 16): s.split(': ', 1)[1] for s in fn['assembly']}
    for block in fn['raw_ranges']:
        raw = bytes.fromhex(block['bytes_hex'])
        assert rom[block['file_offset']:block['file_offset'] + len(raw)] == raw
    pc, count = start, 0
    while pc < end:
        offset = pc - BASE
        half = int.from_bytes(rom[offset:offset + 2], 'little')
        size = 4 if half & 3 == 3 else 2
        raw = rom[offset:offset + size]
        insns = list(decoder.disasm(raw, pc))
        assert len(insns) == 1 and insns[0].size == size, hex(pc)
        ins = insns[0]
        assert pc in provider
        row = dict(pc=hex(pc), file_offset=offset, bytes=raw.hex(),
                   mnemonic=ins.mnemonic, operands=ins.op_str, provider=provider[pc])
        rows.append(row)
        by_pc[pc] = row
        pc += size
        count += 1
    assert pc == end and count == len(provider)
    functions.append(dict(entry=hex(start), end_exclusive=hex(end),
                          instruction_count=count, evidence_id=fn['evidence_id'],
                          retained_source=fn['source'], profile=fn['profile_digest']))

checks = []
def exact(pc, mnemonic, operands, claim):
    row = by_pc[pc]
    assert (row['mnemonic'], row['operands']) == (mnemonic, operands), (hex(pc), row)
    checks.append(dict(pc=hex(pc), claim=claim))

for args in [
    (0xa01915cc, 'addi', 'a5, s1, 0x354', 'slot0 base'),
    (0xa01915d0, 'lbu', 'a4, 0(a5)', 'slot0 occupied'),
    (0xa01915d4, 'c.bnez', 'a4, 0x64', 'slot0 wins: PC+0x64=0xa0191638'),
    (0xa01915d6, 'lbu', 'a4, 0x30(a5)', 'slot1 occupied'),
    (0xa01915da, 'c.bnez', 'a4, 0x64', 'slot1 wins: PC+0x64=0xa019163e'),
    (0xa01915dc, 'lbu', 'a4, 0x60(a5)', 'slot2 occupied'),
    (0xa01915e0, 'c.bnez', 'a4, 0x68', 'slot2 wins: PC+0x68=0xa0191648'),
    (0xa01915e2, 'lbu', 'a5, 0x90(a5)', 'slot3 occupied'),
    (0xa01915e6, 'c.beqz', 'a5, 0x46', 'no occupied slot exits at PC+0x46'),
    (0xa01915f4, 'addi', 's2, s2, 0x2f0', 'transport state base'),
    (0xa01915fc, 'c.bnez', 'a5, 0x30', 'busy exits at PC+0x30, leaves selected slot intact'),
    (0xa01915fe, 'lbu', 'a2, 2(s1)', 'unsigned payload length'),
    (0xa0191606, 'addi', 'a1, s1, 1', 'copy source slot command'),
    (0xa019160a, 'c.addi', 'a2, 2', 'copy command and length plus payload'),
    (0xa019160c, 'addi', 'a0, a0, 0x2f3', 'copy destination active command'),
    (0xa0191618, 'lbu', 'a5, 0(s2)', 'state reloaded after copy'),
    (0xa019161c, 'c.bnez', 'a5, 8', 'preserve nonzero state, jump PC+8'),
    (0xa019161e, 'c.li', 'a5, 1', 'prepare state1'),
    (0xa0191620, 'sb', 'a5, 0(s2)', 'write state1 only if still idle'),
    (0xa0191628, 'sb', 'zero, 0(s1)', 'clear only occupied byte after starter returns'),
    (0xa0191636, 'c.jr', 'ra', 'ordinary return no explicit result'),
    (0xa00ee9e2, 'lbu', 's2, 0(s1)', 'starter reads state'),
    (0xa00ee9e6, 'c.li', 'a5, 1', 'starter gate constant'),
    (0xa00ee9e8, 'bne', 's2, a5, 0x14', 'only state1 starts send; otherwise PC+0x14'),
    (0xa00ee9f4, 'sb', 's2, 1(s1)', 'attempt counter set1 after calls'),
    (0xa00ee9f8, 'sb', 'zero, 2(s1)', 'wait counter cleared after calls'),
    (0xa00eea06, 'c.jr', 'ra', 'starter return has no business status'),
]:
    exact(*args)

def signed(value, bits):
    return value - (1 << bits) if value & (1 << (bits - 1)) else value

def jal_target(pc):
    word = int.from_bytes(bytes.fromhex(by_pc[pc]['bytes']), 'little')
    assert word & 127 == 0x6f and (word >> 7) & 31 == 1
    imm = ((word >> 31) << 20 | ((word >> 12) & 255) << 12 |
           ((word >> 20) & 1) << 11 | ((word >> 21) & 1023) << 1)
    return (pc + signed(imm, 21)) & 0xffffffff

edges = []
for pc, target in ((0xa0191624, 0xa00ee9ce), (0xa00ee9ec, 0xa01a4ff8),
                   (0xa00ee9f0, 0xa00ee96c)):
    assert jal_target(pc) == target
    edges.append(dict(pc=hex(pc), target=hex(target), kind='raw JAL immediate'))
hi = int.from_bytes(bytes.fromhex(by_pc[0xa0191610]['bytes']), 'little')
lo = int.from_bytes(bytes.fromhex(by_pc[0xa0191614]['bytes']), 'little')
assert hi & 127 == 0x17 and (hi >> 7) & 31 == 1
assert lo & 0x707f == 0x67 and (lo >> 7) & 31 == 1 and (lo >> 15) & 31 == 1
copy_target = (0xa0191610 + signed(hi & 0xfffff000, 32) + signed(lo >> 20, 12)) & 0xfffffffe
assert copy_target == 0xa000589c
edges.append(dict(pc='0xa0191610/0xa0191614', target=hex(copy_target), kind='raw AUIPC/JALR immediate'))

result = dict(task='B20', result='static_checks_passed', capstone=capstone.__version__,
              rom=str(ROM), retained_record=str(RECORD), mapping_base=hex(BASE),
              functions=functions, exact_checks=checks, edges=edges, instructions=rows,
              limits=['Two bounded functions; memcpy ABI only, body not newly recovered.',
                      'No runtime, full OTA, retries, length audit or malformed input.',
                      'Existing source IDs retained without rehashing or relabeling.'])
(HERE / 'instruction-evidence.json').write_text(json.dumps(result, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
print(json.dumps(dict(result=result['result'], functions=len(functions), instructions=len(rows),
                      exact_checks=len(checks), raw_call_edges=len(edges))))
