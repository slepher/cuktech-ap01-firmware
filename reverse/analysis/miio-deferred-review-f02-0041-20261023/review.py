"""F02 independent, bounded static review. Reads bytes; never executes ROM code."""
import json
from pathlib import Path
import capstone
from capstone import Cs, CS_ARCH_RISCV, CS_MODE_RISCV32, CS_MODE_RISCVC

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
ROM = Path('D:/Documents/PlatformIO/Projects/cuktech-ap01-firmware/roms/0041/ap01-1.0.2_0041.bin')
BASE = 0x9ffff000
raw = ROM.read_bytes()
md = Cs(CS_ARCH_RISCV, CS_MODE_RISCV32 | CS_MODE_RISCVC)
md.detail = True

def data(pc, n):
    assert 0 <= pc - BASE < len(raw)
    result = raw[pc-BASE:pc-BASE+n]
    assert len(result) == n
    return result

def sx(v, bits):
    return (v ^ (1 << (bits-1))) - (1 << (bits-1))

# Chosen here from the questions, including independent extensions for the
# mode range constant and the inactive-stop branch destination.
specs = [
    ('outer_argument_binding', 0xa005a736, 0xa005ac38),
    ('loop_dispatch_call', 0xa005c80e, 0xa005c83a),
    ('timer_init', 0xa009d106, 0xa009d146),
    ('timer_start', 0xa009d146, 0xa009d286),
    ('submit', 0xa009d286, 0xa009d304),
    ('dispatch', 0xa009d304, 0xa009d382),
    ('integer_dispatch_constant', 0xa009d910, 0xa009d920),
    ('mode_dispatch', 0xa009dd0e, 0xa009dd26),
    ('brightness', 0xa009dac0, 0xa009dae2),
    ('mode', 0xa009de14, 0xa009de38),
    ('location', 0xa00a0f10, 0xa00a0f5e),
    ('callback', 0xa00a0bd8, 0xa00a0e78),
    ('weather_bridge', 0xa00a5b90, 0xa00a5bbe),
    ('stop_prefix', 0xa01b2b5c, 0xa01b2bb2),
    ('inactive_stop_return', 0xa01b2cae, 0xa01b2cb0),
    ('deinit_local', 0xa005c9ea, 0xa005ca9a),
]
ins = {}
windows = []
for name, first, end in specs:
    p, lines = first, []
    while p < end:
        size = 4 if data(p, 1)[0] & 3 == 3 else 2
        blob = data(p, size)
        i = next(md.disasm(blob, p), None)
        if i:
            assert i.size == size
        ins[p] = i
        lines.append(dict(pc=hex(p), bytes=blob.hex(),
                          asm=i.mnemonic+' '+i.op_str if i else 'UNKNOWN'))
        p += size
    assert p == end
    windows.append(dict(name=name, start=hex(first), end_exclusive=hex(end), instructions=lines))

checks = []
def expect(pc, mnemonic, operands):
    i = ins[pc]
    assert i and (i.mnemonic, i.op_str) == (mnemonic, operands), (hex(pc), i, mnemonic, operands)
    checks.append(dict(pc=hex(pc), claim=mnemonic+' '+operands, method='fresh ROM Capstone operand decode'))

def call(pc, target):
    w = int.from_bytes(data(pc, 4), 'little')
    if w & 0x7f == 0x6f:
        assert (w >> 7) & 31 == 1
        imm = ((w >> 31) << 20) | ((w >> 12 & 255) << 12) | ((w >> 20 & 1) << 11) | ((w >> 21 & 1023) << 1)
        actual = (pc + sx(imm, 21)) & 0xffffffff
    else:
        v = int.from_bytes(data(pc+4, 4), 'little')
        assert w & 0xfff == 0x97 and v & 0xfffff == 0x80e7
        actual = (pc + sx(w & 0xfffff000, 32) + sx(v >> 20, 12)) & 0xfffffffe
    assert actual == target, (hex(pc), hex(actual), hex(target))
    checks.append(dict(pc=hex(pc), target=hex(target), method='independent JAL/AUIPC-JALR bit fields'))

for args in [
    (0xa005a77a, 'c.mv', 's1, a0'),
    (0xa005ac04, 'lui', 'a1, 0x62fc9'), (0xa005ac08, 'addi', 'a1, a1, 0x428'),
    (0xa005ac0c, 'c.mv', 'a0, s1'), (0xa005ac18, 'c.beqz', 'a0, 0x20'),
    (0xa009d10e, 'sb', 'a5, 8(a1)'), (0xa009d118, 'c.sw', 'a0, 4(a1)'),
    (0xa009d11a, 'c.sw', 'a5, 0x2c(a1)'), (0xa009d140, 'c.li', 'a0, 0'),
    (0xa009d15c, 'c.mv', 's5, a3'), (0xa009d168, 'c.mv', 's7, a5'),
    (0xa009d172, 'c.mv', 's4, a2'), (0xa009d174, 'c.mv', 's6, a4'),
    (0xa009d176, 'c.mv', 's3, a1'),
    (0xa009d1a0, 'sw', 's3, 0x30(s1)'), (0xa009d1a4, 'c.sw', 'a0, 0x40(s1)'),
    (0xa009d1a6, 'c.sw', 'a1, 0x44(s1)'), (0xa009d1a8, 'sw', 's6, 0x48(s1)'),
    (0xa009d1ac, 'sw', 's7, 0x4c(s1)'),
    (0xa009d294, 'c.li', 'a0, 8'), (0xa009d2a6, 'sb', 's2, 0(a0)'),
    (0xa009d2aa, 'c.sw', 'a1, 4(a0)'), (0xa009d2b4, 'sw', 's1, 0x428(a0)'),
    (0xa009d2b8, 'c.li', 'a5, 0'), (0xa009d2ba, 'c.li', 'a4, 0'),
    (0xa009d2bc, 'c.li', 'a2, 0'), (0xa009d2be, 'c.li', 'a3, 0'),
    (0xa009d2c0, 'addi', 'a1, a1, -0x428'), (0xa009d2c4, 'addi', 'a0, a0, 0x428'),
    (0xa009d2ce, 'c.beqz', 'a0, 0x2a'), (0xa009d2f2, 'c.mv', 'a0, s1'),
    (0xa009d314, 'lw', 's1, 0x130(s3)'), (0xa009d320, 'addi', 's2, s1, -0x34'),
    (0xa009d340, 'lw', 'a5, -4(s1)'), (0xa009d346, 'c.lw', 'a5, 0x14(s1)'),
    (0xa009d348, 'c.lw', 'a4, 0x18(s1)'), (0xa009d34c, 'c.beqz', 'a5, 0x1e'),
    (0xa009d36a, 'lw', 'a5, -4(s1)'), (0xa009d36e, 'c.mv', 'a0, s2'),
    (0xa009d370, 'c.jalr', 'a5'),
    (0xa009d910, 'c.li', 'a5, 3'), (0xa009dd22, 'beq', 's2, a4, 0xf2'),
    (0xa009dac8, 'sb', 's1, -0x38(a5)'), (0xa009dad4, 'lbu', 'a2, 0x4e5(a5)'),
    (0xa009de18, 'sb', 's1, -0xe(a4)'), (0xa009de1c, 'addi', 'a1, s1, -1'),
    (0xa009de20, 'bltu', 'a5, a1, 0xa'),
    (0xa00a0f14, 'addi', 'a2, zero, 0x3f'), (0xa00a0f2e, 'sb', 'zero, 0x3f(s2)'),
    (0xa00a0bf0, 'lw', 's4, 0(a0)'), (0xa00a0bfc, 'lbu', 'a5, 0(s4)'),
    (0xa00a0c00, 'lw', 'a6, 4(s4)'), (0xa00a0c08, 'c.mv', 's5, a0'),
    (0xa00a0c20, 'lbu', 'a5, 0(s4)'), (0xa00a0cce, 'c.mv', 'a0, s4'),
    (0xa00a0cd4, 'sw', 'zero, 0(s5)'),
    (0xa00a5b9c, 'addi', 'a0, a0, 0x520'), (0xa00a5ba8, 'addi', 'a1, zero, 0x7d0'),
    (0xa01b2b60, 'beqz', 'a5, 0x14e'), (0xa01b2cae, 'c.jr', 'ra'),
    (0xa005ca0e, 'addi', 'a0, a0, 0x480'), (0xa005ca1e, 'addi', 'a0, a0, 0x228'),
    (0xa005ca2e, 'addi', 'a0, s2, -0x76c'), (0xa005ca3a, 'addi', 'a0, s2, -0x76c'),
]: expect(*args)

for pc, target in [
    (0xa005ac0e, 0xa009d106), (0xa005c81a, 0xa009d304),
    (0xa009d17a, 0xa01b2b5c), (0xa009d29a, 0xa002fcc8),
    (0xa009d2c8, 0xa009d146), (0xa009d2f4, 0xa002e14e),
    (0xa009d338, 0xa01b2b5c), (0xa009d350, 0xa01b2b5c), (0xa009d366, 0xa009d146),
    (0xa009dacc, 0xa009d286), (0xa009de26, 0xa009d286), (0xa00a0f32, 0xa009d286),
    (0xa00a0cd0, 0xa002e14e), (0xa00a0d48, 0xa00a5b90),
    (0xa00a5ba0, 0xa01b2b5c), (0xa00a5bae, 0xa01b24c0),
    (0xa005ca12, 0xa01b2b5c), (0xa005ca22, 0xa01b2b5c),
    (0xa005ca32, 0xa01b2cb0), (0xa005ca44, 0xa009fb96),
]: call(pc, target)

# Derive whole-function access lists instead of checking only isolated opcodes.
def between(a, z):
    return [ins[p] for p in sorted(ins) if a <= p < z and ins[p]]

init_stores = [(hex(i.address), i.mnemonic, i.op_str) for i in between(0xa009d106, 0xa009d146)
               if i.mnemonic in ('sw', 'sb', 'c.sw') and '(a1)' in i.op_str]
assert len(init_stores) == 11 and not any(i[2].endswith(', 0(a1)') for i in init_stores)
# The two other initializer stores write through the loop/tail registers.
assert all(i.mnemonic not in ('jal', 'jalr', 'c.jalr') for i in between(0xa009d106,0xa009d146))

callback = between(0xa00a0bd8, 0xa00a0e78)
saved_reads = [(hex(i.address), i.mnemonic, i.op_str) for i in callback
               if i.mnemonic in ('lw','lbu','lb','lhu','lh','c.lw') and '(s4)' in i.op_str]
assert saved_reads == [('0xa00a0bfc','lbu','a5, 0(s4)'), ('0xa00a0c00','lw','a6, 4(s4)'), ('0xa00a0c20','lbu','a5, 0(s4)')]
for reg, writes_expected in [('s4',[0xa00a0bf0,0xa00a0ce2]), ('s5',[0xa00a0c08,0xa00a0ce4])]:
    writes = [i.address for i in callback if i.reg_name(i.operands[0].reg)==reg
              and i.mnemonic not in ('sw','sb','c.sw','c.swsp')]
    assert writes == writes_expected, (reg,writes)
# No other direct or copied data loads through the saved timer register.
assert not any(i.mnemonic in ('lw','c.lw') and '(s5)' in i.op_str for i in callback)

# CFG reachability only: external calls are treated as normal returning calls.
# Proves a shared cleanup in this local callback, not callee termination.
nodes={i.address:i for i in callback}
def edges(i):
    op=i.mnemonic; nxt=i.address+i.size
    if op == 'c.jr':
        return []
    if op == 'c.j':
        return [i.address+i.operands[-1].imm]
    if op in ('beq','bne','bltu','bgeu','beqz','bnez','c.beqz','c.bnez'):
        return [nxt, i.address+i.operands[-1].imm]
    return [nxt]
def reaches_cleanup(pc, seen):
    if pc == 0xa00a0cce:
        return True
    assert pc in nodes and pc not in seen, hex(pc)
    successors=edges(nodes[pc])
    return bool(successors) and all(reaches_cleanup(q,seen|{pc}) for q in successors)
assert reaches_cleanup(0xa00a0c20,set())

# Verify loop register stability from a fresh byte decode of the full prefix.
outer_writes = [hex(i.address) for i in between(0xa005a736,0xa005ac38)
                if i.operands and i.operands[0].type == capstone.CS_OP_REG
                and i.reg_name(i.operands[0].reg)=='s1'
                and i.mnemonic not in ('sw','sb','c.sw','c.swsp')]
assert outer_writes == ['0xa005a77a'], outer_writes

unknown = [(hex(p),data(p,4).hex()) for p,i in ins.items() if i is None]
# Unknown vendor arithmetic in the outer prefix is not interpreted either.
assert (hex(0xa009d18c),'7715aac0') in unknown
assert (hex(0xa009d1bc),'7716c5c0') in unknown

sources=[]
for path,key in [('reverse/analysis/factory-test-0041-20261023/retained-initializer.json','function'),
                 ('reverse/analysis/miio-deferred-settings-0041-20261023/retained-functions.json','functions')]:
    saved=json.loads((ROOT/path).read_text(encoding='utf8'))[key]
    for f in saved if isinstance(saved,list) else [saved]:
        for item in f['raw_ranges']:
            blob=bytes.fromhex(item['hex'])
            assert data(int(item['start'],16),len(blob))==blob
        sources.append(dict(path=path,evidence_id=f['evidence_id'],profile=f['profile']['digest'],raw_ranges_match=True))

out=dict(task='F02',baseline='4a897eecbafb15f94d8e2fe49d1e6772fdd3287d',
         method='new reviewer; fresh original ROM decode and independent field checks; no F01 verifier run',
         rom=str(ROM),base=hex(BASE),capstone=capstone.__version__,sources=sources,
         windows=windows,checks=checks,initializer_timer_stores=init_stores,
         callback_saved_request_reads=saved_reads,outer_s1_writes=outer_writes,
         callback_cfg_all_local_paths_reach_cleanup=True,unknown_instructions=unknown,
         limitations=['No target execution or history replay.', 'External calls assumed to return normally for local callback CFG.',
                     'Vendor UNKNOWN semantics and complete heap algorithm not certified.',
                     'Local deinit is not the loop walker or proof of whole-ROM absence.',
                     'Library names/allocator semantics are prior contracts, not authenticated upstream source.'])
(HERE/'independent-evidence.json').write_text(json.dumps(out,indent=2,ensure_ascii=False)+'\n',encoding='utf8')
print(f'PASS {len(checks)} instruction/call checks; {len(windows)} byte windows; initializer writes/access/CFG/register checks PASS; UNKNOWN {unknown}')
