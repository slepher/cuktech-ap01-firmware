"""E17 independent sparse ROM/ABI review; no target/model execution."""
import json
from pathlib import Path
from capstone import Cs, CS_ARCH_RISCV, CS_MODE_RISCV32, CS_MODE_RISCVC

HERE = Path(__file__).resolve().parent
TREE = HERE.parents[2]
ROM = Path('D:/Documents/PlatformIO/Projects/cuktech-ap01-firmware/roms/0041/ap01-1.0.2_0041.bin')
BASE = 0x9ffff000
md = Cs(CS_ARCH_RISCV, CS_MODE_RISCV32 | CS_MODE_RISCVC)
checks = []

def sx(x, n):
    return x - (1 << n) if x & (1 << (n - 1)) else x

def read(pc, n):
    with ROM.open('rb') as stream:
        stream.seek(pc - BASE)
        data = stream.read(n)
    assert len(data) == n
    return data

def anchor(pc, expected):
    data = read(pc, len(bytes.fromhex(expected)))
    assert data.hex() == expected, hex(pc)
    insn = next(md.disasm(data, pc), None)
    checks.append(dict(pc=hex(pc), raw=data.hex(),
                       instruction=(insn.mnemonic + ' ' + insn.op_str) if insn else 'existing UMAR64 rule'))
    return int.from_bytes(data, 'little')

# Explicit calling convention and source/return register anchors, not full bodies.
for pc, data in [
    (0xa0098b6a,'aa84'), (0xa0098b74,'37460f00'), (0xa0098b78,'13060624'),
    (0xa0098b7c,'8146'), (0xa019e1a2,'0111'), (0xa019e1a8,'0010'),
    (0xa019e1aa,'930584fe'), (0xa019e1ae,'0545'), (0xa019e1b8,'01cd'),
    (0xa019e1d8,'f240'), (0xa019e1da,'6244'), (0xa019e1dc,'3e85'),
    (0xa019e1de,'93d5f741'), (0xa019e1e2,'b7d79a3b'), (0xa019e1e6,'938707a0'),
    (0xa019e1ee,'0561'), (0xa019e1f0,'8280'), (0xa0026974,'1d89'),
    (0xa0026976,'8547'), (0xa0026982,'2e85'), (0xa0026988,'aa84'),
    (0xa00269f4,'2685'), (0xa005c172,'2685'), (0xa005c178,'2685'),
    (0xa005c812,'2685'), (0xa005c818,'2685')]:
    anchor(pc, data)

# Independently extract JAL or AUIPC/JALR target bits, including both caller pairs.
calls = []
for pc, want in [(0xa0098b6c,0xa019e1a2), (0xa0098b7e,0xa001b302),
                 (0xa019e1b0,0xa002696a), (0xa0026984,0xa002645a),
                 (0xa005c174,0xa0098b60), (0xa005c17a,0xa009d304),
                 (0xa005c814,0xa0098b60), (0xa005c81a,0xa009d304)]:
    data = read(pc, 4)
    w = int.from_bytes(data, 'little')
    if w & 127 == 0x6f:
        assert (w >> 7) & 31 == 1
        displacement = ((w >> 31) << 20) | (((w >> 12) & 255) << 12) | (((w >> 20) & 1) << 11) | (((w >> 21) & 1023) << 1)
        target = (pc + sx(displacement, 21)) & 0xffffffff
    else:
        qdata = read(pc + 4, 4)
        q = int.from_bytes(qdata, 'little')
        assert w & 0xfff == 0x97 and q & 0xfffff == 0x80e7
        target = (pc + sx(w & 0xfffff000, 32) + sx(q >> 20, 12)) & 0xfffffffe
        data += qdata
    assert target == want
    calls.append(dict(pc=hex(pc), raw=data.hex(), target=hex(target)))

# Extract standard 32-bit word load/store fields, not only assembly strings.
memory = []
for pc, data, want in [
    (0xa019e1d0,'8327c4fe',('load',15,8,-20)),
    (0xa019e1d4,'032784fe',('load',14,8,-24)),
    (0xa0098b82,'23a0a414',('store',10,9,0x140)),
    (0xa0098b86,'23a2b414',('store',11,9,0x144))]:
    w = anchor(pc, data)
    assert (w >> 12) & 7 == 2
    if w & 127 == 3:
        fields = ('load',(w >> 7) & 31,(w >> 15) & 31,sx(w >> 20,12))
    else:
        assert w & 127 == 0x23
        fields = ('store',(w >> 20) & 31,(w >> 15) & 31,sx(((w >> 25) << 5) | ((w >> 7) & 31),12))
    assert fields == want
    memory.append(dict(pc=hex(pc), operation=fields[0], value_register=fields[1], base_register=fields[2], offset=fields[3]))

branches = []
for pc, data, want in [(0xa0026978,'6305f500',(0,10,15,0xa0026982)),
                       (0xa002698a,'63d30406',(5,9,0,0xa00269f0))]:
    w = anchor(pc,data)
    assert w & 127 == 0x63
    imm = ((w >> 31) << 12) | (((w >> 7) & 1) << 11) | (((w >> 25) & 63) << 5) | (((w >> 8) & 15) << 1)
    got = ((w >> 12) & 7,(w >> 15) & 31,(w >> 20) & 31,pc + sx(imm,13))
    assert got == want
    branches.append(dict(pc=hex(pc), funct3=got[0], rs1=got[1], rs2=got[2], target=hex(got[3])))

w = anchor(0xa019e1ea,'7715f7a4')
umar = dict(op=w & 127,funct3=(w >> 12) & 7,funct7=w >> 25,rd=(w >> 7) & 31,rs1=(w >> 15) & 31,rs2=(w >> 20) & 31)
assert umar == dict(op=119,funct3=1,funct7=82,rd=10,rs1=14,rs2=15)
patch = (TREE / 'tooling/scripts/qemu-ap01-cpu.patch').read_text()
body = patch.split('+static bool trans_ap01_umar64(',1)[1].split('+}\n',1)[0]
rule_tokens = ['int rd = a->rd & ~1;', 'get_gpr(ctx, rd, EXT_ZERO)',
               'get_gpr(ctx, rd + 1, EXT_ZERO)', 'get_gpr(ctx, a->rs1, EXT_ZERO)',
               'get_gpr(ctx, a->rs2, EXT_ZERO)', 'tcg_gen_mulu2_i32(pl, ph, left, right);',
               'tcg_gen_add2_i32(low, high, al, ah, pl, ph);',
               'gen_set_gpr(ctx, rd, result);', 'gen_set_gpr(ctx, rd + 1, result);']
for token in rule_tokens:
    assert token in body

# Sparse unsigned arithmetic support only: no complete division CFG claim.
division = []
for pc, data, funct3, rd, rs1, rs2 in [(0xa001b35a,'b3d61503',5,13,11,17),
                                    (0xa001b368,'33f71503',7,14,11,17),
                                    (0xa001b36e,'b305d602',0,11,12,13)]:
    w = anchor(pc,data)
    got = (w & 127,w >> 25,(w >> 12) & 7,(w >> 7) & 31,(w >> 15) & 31,(w >> 20) & 31)
    assert got == (0x33,1,funct3,rd,rs1,rs2)
    division.append(dict(pc=hex(pc), fields=got))

result = dict(task='E17', result='PASS', sparse_instructions=checks, calls=calls,
              memory_fields=memory, selector_branches=branches, umar64_fields=umar,
              existing_rule_tokens=rule_tokens, division_support_only=division,
              inherited=['H13/H14 ID0 offset and weather consumers','E14/E15 deadline/unsigned consumption','H15 lower pair contract; not re-exported'],
              limitations=['No target or analyzer model execution.','No full division algorithm or library authentication.','No source frequency, epoch, concurrency or error-path contract authentication.'])
(HERE / 'review.json').write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
print(f'PASS: {len(checks)} sparse instructions, {len(calls)} call targets, memory/branch fields and existing UMAR64 rule; division remains qualified.')
