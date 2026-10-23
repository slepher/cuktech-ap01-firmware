"""B03 static review. Reads ROM and retained B02 evidence; writes only B03 result."""
import json
import sys
from pathlib import Path
from capstone import Cs, CS_ARCH_RISCV, CS_MODE_RISCV32, CS_MODE_RISCVC

HERE = Path(__file__).resolve().parent
TREE = HERE.parents[2]
SOURCE = Path(sys.argv[1]).resolve()
rom = (SOURCE / 'roms/0041/ap01-1.0.2_0041.bin').read_bytes()
evidence = json.loads((TREE / 'reverse/analysis/poll-phase-writer-b02-0041-20261023/instruction-evidence.json').read_text(encoding='utf-8'))
base = 0x9ffff000
decoder = Cs(CS_ARCH_RISCV, CS_MODE_RISCV32 | CS_MODE_RISCVC)
decoded = {}
for window in evidence['windows']:
    start, end = int(window['start'], 16), int(window['end_exclusive'], 16)
    raw = rom[start-base:end-base]
    assert raw == bytes.fromhex(window['hex'])
    pc = start
    for record in window['instructions']:
        assert pc == int(record['address'], 16)
        b = bytes.fromhex(record['hex'])
        assert rom[pc-base:pc-base+len(b)] == b
        ins = next(decoder.disasm(b, pc))
        assert ins.size == len(b)
        assert ins.mnemonic + ' ' + ins.op_str == record['capstone_assembly']
        decoded[pc] = ins
        pc += ins.size
    assert pc == end

def instruction(pc, mnemonic, operands):
    ins = decoded[pc]
    assert (ins.mnemonic, ins.op_str) == (mnemonic, operands), hex(pc)

def target(pc):
    return pc + int(decoded[pc].op_str.split(',')[-1].strip(), 0)

for pc, mnemonic, operands in [
    (0xa00a85a0, 'sb', 'a0, -0x50(s0)'),
    (0xa00a85a4, 'sb', 'a1, -0x4f(s0)'),
    (0xa00a85a8, 'sw', 'a2, -0x4c(s0)'),
    (0xa00a8772, 'addi', 's1, a0, 0x504'),
    (0xa00a8776, 'addi', 'a2, s0, -0x50'),
    (0xa00a877a, 'c.li', 'a1, 4'),
    (0xa00a8784, 'c.lw', 'a5, 0(s1)'),
    (0xa00a878e, 'sb', 'zero, -0x4cb(a5)'),
    (0xa00a8514, 'lbu', 'a1, 0x33(s3)'),
    (0xa00a8522, 'addi', 'a2, s3, 0x34'),
    (0xa00a8534, 'lbu', 'a0, 0x32(s3)'),
    (0xa00a8538, 'c.jalr', 'a5'),
    (0xa00a853a, 'lw', 'a5, 0(s4)'),
    (0xa00a8546, 'c.jalr', 'a5'),
    (0xa019168e, 'sb', 'a5, 7(a3)'),
    (0xa01916ba, 'lw', 'a5, 0x6c0(a5)'),
    (0xa01916c0, 'lbu', 'a0, 0(s1)'),
    (0xa01916cc, 'andi', 'a0, a0, 0xff'),
    (0xa01916d0, 'c.jalr', 'a5'),
]:
    instruction(pc, mnemonic, operands)
for pc, expected in [(0xa00a8780, 0xa0191652), (0xa00a8786, 0xa00a8aae),
                     (0xa00a8792, 0xa00a8aae), (0xa00a8aae, 0xa0191746),
                     (0xa00a876a, 0xa00a85e4), (0xa01916a8, 0xa01916d2),
                     (0xa0191688, 0xa01916e0), (0xa01916f2, 0xa0191692)]:
    assert target(pc) == expected

# Independently extract the critical S-type encoding, without assembly labels.
w = int.from_bytes(rom[0xa00a878e-base:0xa00a8792-base], 'little')
imm = ((w >> 25) << 5) | ((w >> 7) & 31)
imm -= 4096 if imm & 2048 else 0
assert (w & 127, (w >> 12) & 7, (w >> 15) & 31, (w >> 20) & 31) == (0x23, 0, 15, 0)
assert 0x62fc5000 + imm == 0x62fc4b35
# Enumerate direct stores in the entire helper, making the negative claim bounded.
stores = [{'address': hex(pc), 'instruction': ins.mnemonic + ' ' + ins.op_str}
          for pc, ins in decoded.items() if 0xa0191652 <= pc < 0xa0191700
          and ins.mnemonic in ('sb', 'sh', 'sw', 'c.sw', 'c.swsp')]
result = {
    'task_id': 'B03', 'result': 'accepted_with_scope_clarification',
    'method': 'Read-only ROM byte comparison and independent Capstone decoding; manual register/control-flow review; no firmware execution or shared REA session.',
    'windows_verified': len(evidence['windows']), 'instructions_verified': len(decoded),
    'critical_store_encoding_verified': True, 'helper_direct_stores': stores,
    'accepted': ['post-helper word load, not helper return/payload test', 'byte phase clear',
                 'view layout and byte dispatch arguments', 'slot reread and indirect target boundary',
                 'helper may set round_done before caller clears phase'],
    'clarification': 'No direct sent/round_done reset in the cmd58 local branch or helper; selector and unresolved indirect handler effects are outside that negative claim.',
    'not_reverified': ['complete parser admission', 'all callback-slot writers', 'selector body',
                       'compare/copy implementation internals', 'other phase writers'],
    'evidence_reference': '../poll-phase-writer-b02-0041-20261023/instruction-evidence.json',
}
(HERE / 'review-result.json').write_text(json.dumps(result, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
print(json.dumps({k: result[k] for k in ('task_id', 'result', 'windows_verified', 'instructions_verified')}, ensure_ascii=False))
