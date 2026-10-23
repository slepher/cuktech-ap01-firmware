"""Independent bounded B05 static review. Reads ROM, never executes it."""
import json
import sys
from pathlib import Path
from capstone import Cs, CS_ARCH_RISCV, CS_MODE_RISCV32, CS_MODE_RISCVC

HERE = Path(__file__).resolve().parent
TREE = HERE.parents[2]
SOURCE = Path(sys.argv[1])
BASE = 0x9ffff000
rom = (SOURCE / 'roms/0041/ap01-1.0.2_0041.bin').read_bytes()
evidence_path = TREE / 'reverse/analysis/poll-phase-one-b04-0041-20261023/instruction-evidence.json'
evidence = json.loads(evidence_path.read_text(encoding='utf-8'))
decoder = Cs(CS_ARCH_RISCV, CS_MODE_RISCV32 | CS_MODE_RISCVC)
decoded = {}
ordinary = 0
byte_count = 0
for window in evidence['windows']:
    cursor = int(window['start'], 16)
    for row in window['instructions']:
        pc = int(row['address'], 16)
        assert pc == cursor
        expected = bytes.fromhex(row['hex'])
        raw = rom[pc-BASE:pc-BASE+len(expected)]
        assert raw == expected, hex(pc)
        size = 4 if raw[0] & 3 == 3 else 2
        assert size == len(expected)
        if pc not in (0xa00a893a, 0xa00a8b62):
            ins = next(decoder.disasm(raw, pc), None)
            assert ins is not None and ins.size == size, hex(pc)
            # Compare decode anew; do not trust only the retained provider text.
            assert ins.mnemonic + ' ' + ins.op_str == row['independent_decode'], hex(pc)
            decoded[pc] = (ins.mnemonic, ins.op_str)
            ordinary += 1
        cursor += size
        byte_count += size
    assert cursor == int(window['end_exclusive'], 16)

checks = []
def exact(pc, mnemonic, operands):
    assert decoded[pc] == (mnemonic, operands), (hex(pc), decoded[pc])
    checks.append({'address': hex(pc), 'instruction': mnemonic + ' ' + operands})

# Entry uses original a0 for equality, after separately storing a byte view.
exact(0xa00a85a0, 'sb', 'a0, -0x50(s0)')
exact(0xa00a85b8, 'c.mv', 's2, a0')
exact(0xa00a85c8, 'bltu', 'a5, a0, 0x3a')
exact(0xa00a8602, 'addi', 'a5, zero, 0x55')
exact(0xa00a8606, 'beq', 'a0, a5, 0x2f0')
# Returning helper precedes two fresh unsigned halfword reads.
exact(0xa00a88f6, 'lui', 's1, 0x62fcb')
exact(0xa00a88fa, 'addi', 'a2, s0, -0x50')
exact(0xa00a88fe, 'c.li', 'a1, 0x18')
exact(0xa00a8900, 'addi', 'a0, s1, 4')
exact(0xa00a8904, 'jal', '0xe8d4e')
assert 0xa00a8904 + 0xe8d4e == 0xa0191652
exact(0xa00a8908, 'addi', 'a5, s1, 4')
exact(0xa00a8930, 'lhu', 'a4, 0x10(a5)')
exact(0xa00a8934, 'lhu', 'a3, 0x12(a5)')
exact(0xa00a8938, 'c.or', 'a4, a3')
exact(0xa00a893e, 'c.bnez', 'a4, 0x12')
exact(0xa00a894e, 'c.j', '-0x6c')
# Type mapping has only forward branches to its own common store.
exact(0xa00a8918, 'beq', 'a2, a1, 0x10')
exact(0xa00a8922, 'bne', 'a2, a4, 6')
exact(0xa00a892c, 'sb', 'a3, -0x110(a4)')
# Null allocation return branches directly to the common prelude loop.
exact(0xa00a8966, 'beq', 'a7, a4, 0xbc')
exact(0xa00a8a22, 'lbu', 's3, 0x1c(s2)')
exact(0xa00a8a26, 'jal', '-0x4d04')
exact(0xa00a8a2a, 'addi', 'a0, zero, 0x17c')
exact(0xa00a8a2e, 'jal', '-0x1a6cc')
exact(0xa00a8a3c, 'c.beqz', 'a0, 0x46')
assert 0xa00a8a3c + 0x46 == 0xa00a8a82
exact(0xa00a8a82, 'c.li', 's1, 0')
exact(0xa00a8a84, 'lui', 's2, 0xa00a4')
exact(0xa00a8a88, 'blt', 's1, s3, 0xc8')
exact(0xa00a8b50, 'c.mv', 'a1, s1')
exact(0xa00a8b52, 'addi', 'a0, s2, -0x376')
exact(0xa00a8b56, 'auipc', 'ra, 0x10a')
exact(0xa00a8b5a, 'jalr', 'ra, ra, -0x288')
assert ((0xa00a8b56 + 0x10a000 - 0x288) & ~1) == 0xa01b28ce
exact(0xa00a8b5e, 'c.addi', 's1, 1')
exact(0xa00a8b60, 'c.j', '-0xd8')
# Snapshot pointer; phase, done, loop body, selector in that control order.
exact(0xa00a8a8c, 'lui', 'a4, 0x62fc5')
exact(0xa00a8a90, 'addi', 'a5, a4, -0x4d0')
exact(0xa00a8a94, 'c.li', 'a3, 1')
exact(0xa00a8a96, 'c.lw', 'a2, 0(a5)')
exact(0xa00a8a98, 'sb', 'a3, 5(a5)')
exact(0xa00a8a9c, 'sb', 'zero, 7(a5)')
exact(0xa00a8aa0, 'addi', 'a4, a4, -0x4d0')
exact(0xa00a8aa4, 'c.li', 'a5, 0')
exact(0xa00a8aa6, 'lbu', 'a3, 6(a4)')
exact(0xa00a8aaa, 'bltu', 'a5, a3, 0xb8')
exact(0xa00a8b66, 'c.addi', 'a5, 1')
exact(0xa00a8b68, 'sb', 'zero, 6(a3)')
exact(0xa00a8b6c, 'andi', 'a5, a5, 0xff')
exact(0xa00a8b70, 'c.j', '-0xca')
exact(0xa00a8aae, 'jal', '0xe8c98')
assert 0xa00a8aae + 0xe8c98 == 0xa0191746
exact(0xa00a8ab2, 'c.j', '-0x4ce')

# Vendor encodings independently mask all constructor fields against the ROM.
def word(pc):
    return int.from_bytes(rom[pc-BASE:pc-BASE+4], 'little')
ext = word(0xa00a893a)
add = word(0xa00a8b62)
assert (ext & 0x7f, (ext >> 12)&7, (ext >> 7)&31,
        (ext >> 15)&31, (ext >> 26)&63, (ext >> 20)&63) == (11, 3, 14, 14, 15, 0)
assert (add & 0x7f, (add >> 12)&7, (add >> 27)&31,
        (add >> 7)&31, (add >> 15)&31, (add >> 20)&31,
        (add >> 25)&3) == (11, 1, 0, 13, 12, 15, 3)
model_dir = SOURCE / 'evidence/rea-0041-20261017/ghidra/Ghidra/Processors/RISCV/data/languages'
for excerpt in evidence['vendor_model_excerpts']:
    # Evidence was recorded on Windows; basename must also work outside Windows.
    name = excerpt['path'].replace('\\', '/').rsplit('/', 1)[-1]
    lines = (model_dir/name).read_text(encoding='utf-8').splitlines()
    text = excerpt['text']
    start = excerpt['start_line'] - 1
    assert '\n'.join(lines[start:start+len(text.splitlines())]) == text

result = {
    'task': 'B05', 'reviewed_report': 'poll-phase-one-b04-0041-20261023.md',
    'source_evidence_id': evidence['evidence_id'],
    'source_evidence_path': str(evidence_path.relative_to(TREE)),
    'result': 'accepted_with_limits',
    'checks': {'rom_bytes_compared': byte_count, 'windows': len(evidence['windows']),
               'ordinary_redecodes': ordinary, 'targeted_instruction_contracts': len(checks),
               'vendor_words': ['0x3c07370b', '0x06f6168b'],
               'model_excerpts_matched': len(evidence['vendor_model_excerpts'])},
    'instruction_contracts': checks,
    'accepted': ['cmd55 original-register equality', 'cache reads after helper return',
                 'nonzero gate and bounded reachability', 'zero allocation return reaches common loop',
                 'signed snapshot-count prelude and exact a01b28ce target',
                 'phase/done/sent/selector order', '8-bit reset index and reread count',
                 'two vendor words agree with existing model'],
    'corrections': [],
    'unverified': ['full initialization and callback body', 'callee termination and indirect effects',
                   'runtime reachability', 'exhaustive phase writers', 'upstream ISA provenance'],
    'method': 'Read raw ROM and independently decode retained bounded windows; no firmware execution.'
}
(HERE / 'review-result.json').write_text(json.dumps(result, ensure_ascii=False, indent=2)+'\n', encoding='utf-8')
print(json.dumps(result['checks']))
