"""Independent E04 byte/ABI checks. Reads immutable ROM; executes no target code."""
import json
from pathlib import Path
from capstone import Cs, CS_ARCH_RISCV, CS_MODE_RISCV32, CS_MODE_RISCVC

HERE = Path(__file__).resolve().parent
ROOT = Path('D:/Documents/PlatformIO/Projects/cuktech-ap01-firmware')
ROM = ROOT / 'roms/0041/ap01-1.0.2_0041.bin'
BASE = 0x9ffff000
rom = ROM.read_bytes()
cs = Cs(CS_ARCH_RISCV, CS_MODE_RISCV32 | CS_MODE_RISCVC)
regs = 'zero ra sp gp tp t0 t1 t2 s0 s1 a0 a1 a2 a3 a4 a5 a6 a7 s2 s3 s4 s5 s6 s7 s8 s9 s10 s11 t3 t4 t5 t6'.split()

def signed(v, n):
    return v - (1 << n) if v & (1 << (n - 1)) else v

def custom(word):
    if word & 127 != 11:
        return None
    rd, rs1, rs2 = [regs[(word >> k) & 31] for k in (7, 15, 20)]
    f3, top, shift = (word >> 12) & 7, word >> 27, (word >> 25) & 3
    if f3 == 3:
        return f'th.extu {rd},{rs1},{word >> 26},{(word >> 20) & 63}'
    if f3 == 4 and top in (8, 16):
        return f'th.{"lrw" if top == 8 else "lrbu"} {rd},{rs1},{rs2},{shift}'
    if f3 == 5 and top == 8:
        return f'th.srw {rd},{rs1},{rs2},{shift}'
    raise AssertionError(hex(word))

def decode(start, end):
    rows = []
    pc = start
    while pc < end:
        pos = pc - BASE
        size = 4 if rom[pos] & 3 == 3 else 2
        raw = rom[pos:pos + size]
        assert pc + size <= end
        word = int.from_bytes(raw, 'little')
        ext = custom(word) if size == 4 else None
        ins = next(cs.disasm(raw, pc), None)
        assert ext or (ins and ins.size == size), hex(pc)
        row = dict(address=hex(pc), file_offset=pos, hex=raw.hex(), assembly=ext or (ins.mnemonic + ' ' + ins.op_str))
        if ext:
            row['fields'] = dict(rd=(word >> 7) & 31, rs1=(word >> 15) & 31, rs2=(word >> 20) & 31,
                                 funct3=(word >> 12) & 7, high5=word >> 27, shift=(word >> 25) & 3,
                                 msb=word >> 26, lsb=(word >> 20) & 63)
        if size == 4 and word & 127 == 111:
            imm = ((word >> 31) << 20) | (((word >> 12) & 255) << 12) | (((word >> 20) & 1) << 11) | (((word >> 21) & 1023) << 1)
            row['target'] = hex(pc + signed(imm, 21))
        elif size == 4 and word & 127 == 99:
            imm = ((word >> 31) << 12) | (((word >> 7) & 1) << 11) | (((word >> 25) & 63) << 5) | (((word >> 8) & 15) << 1)
            row['target'] = hex(pc + signed(imm, 13))
        elif size == 2:
            # Compressed branches/jumps are PC-relative; Capstone prints a displacement.
            if ins.mnemonic in ('c.j', 'c.jal', 'c.beqz', 'c.bnez'):
                delta = int(ins.op_str.split(',')[-1].strip(), 0)
                row['target'] = hex(pc + delta)
        rows.append(row)
        pc += size
    return rows

# The E03 evidence is checked byte-for-byte, never executed/imported or rewritten.
old = json.loads((HERE.parent / 'ctk-view-dataflow-e03-0041-20261023/instruction-windows.json').read_text(encoding='utf-8'))
checked = 0
for window in old['windows']:
    fresh = decode(int(window['start'], 16), int(window['end_exclusive'], 16))
    assert len(fresh) == len(window['instructions'])
    for actual, prior in zip(fresh, window['instructions']):
        assert all(actual[k] == prior[k] for k in ('address', 'file_offset', 'hex', 'assembly'))
        checked += 1

# Keep focused independently read windows, including the previously split state path.
spans = [
    ('head_init', 0xa00a5652, 0xa00a5664),
    ('registration_abi', 0xa005d13c, 0xa005d14e),
    ('registration_node', 0xa01b28ce, 0xa01b291a),
    ('dispatch_abi', 0xa00a38c0, 0xa00a3904),
    ('frame_and_guards', 0xa00adabc, 0xa00adc3a),
    ('port_alternatives', 0xa00ae166, 0xa00ae194),
    ('index', 0xa00add16, 0xa00add22),
    ('child_normal', 0xa00dcf30, 0xa00dcf52),
    ('offline_return_unused', 0xa00ae216, 0xa00ae250),
    ('port1_prepare', 0xa00aef16, 0xa00aef82),
    ('port1_consume_and_state', 0xa00af062, 0xa00af12e),
    ('port2_reuse', 0xa00af12e, 0xa00af18e),
    ('finish', 0xa00af250, 0xa00af262),
    ('name_all', 0xa00f44e8, 0xa00f4610),
    ('values_all', 0xa00f4610, 0xa00f4740),
    ('status_all', 0xa00ef0ec, 0xa00ef1d4),
    ('battery_all', 0xa00ef2da, 0xa00ef468),
]
windows = [dict(name=n, start=hex(a), end_exclusive=hex(b), instructions=decode(a, b)) for n, a, b in spans]
index = {int(i['address'], 16): i for w in windows for i in w['instructions']}
checks = []
def exact(pc, raw, name):
    assert index[pc]['hex'] == raw, (name, hex(pc))
    checks.append(dict(name=name, address=hex(pc), hex=raw))

for pc, raw, name in [
    (0xa005d142,'1305c5ab','callback=a00adabc'), (0xa005d140,'d285','userdata=s4'),
    (0xa00a38f2,'c840','a0=node.userdata'), (0xa00a38f4,'d685','a1=cached item'),
    (0xa00a38f6,'8297','indirect callback'), (0xa00adabc,'1171','frame=0x100'),
    (0xa00adad8,'0002','s0=entry sp'), (0xa00aef50,'1305c4f6','dst=s0-0x94'),
    (0xa00aef4c,'13062005','fill=0x52'), (0xa00aef5c,'8545','port1'),
    (0xa00aef78,'130c94f7','ordinal base=dst+13'), (0xa00aef7c,'930c84f7','kind base=dst+12'),
    (0xa00af062,'8504','preincrement label index'), (0xa00af07e,'834624f7','a3=u8 total'),
    (0xa00f4526,'b68b','fourth argument saved in s7'), (0xa00af100,'1147','four value slots'),
    (0xa00af102,'c10c','row step16'), (0xa00af104,'93840402','slot step32'),
    (0xa00af12a,'e3e3f9f6','unsigned state >1'), (0xa00af16a,'1305c4f6','port2 same dst'),
    (0xa00af176,'8945','port2'), (0xa00adb3a,'1161','frame returned'),
]: exact(pc,raw,name)

edges = {0xa00aef62:0xa00f4740, 0xa00af17c:0xa00f4740, 0xa00ae238:0xa00f4740,
         0xa00aef66:0xa00af12e, 0xa00af180:0xa00af250, 0xa00af076:0xa00f44e8,
         0xa00af0ee:0xa00ef0ec, 0xa00af0f6:0xa00f4610, 0xa00af124:0xa00ef2da,
         0xa00aef72:0xa00af12a, 0xa00aef80:0xa00af07e,
         0xa00ae242:0xa00ef1d4, 0xa00ae24c:0xa00ef2da}
for a, b in edges.items():
    assert index[a]['target'] == hex(b), hex(a)

# Decode the AUIPC/JALR pair independently, using encoded immediates.
hi = int.from_bytes(bytes.fromhex(index[0xa005d146]['hex']), 'little')
lo = int.from_bytes(bytes.fromhex(index[0xa005d14a]['hex']), 'little')
assert (0xa005d146 + signed(hi & 0xfffff000,32) + signed(lo >> 20,12)) & 0xfffffffe == 0xa01b28ce
assert custom(int.from_bytes(rom[0xa00adbc4-BASE:0xa00adbc8-BASE],'little')) == 'th.extu a4,a5,5,4'
assert custom(int.from_bytes(rom[0xa00af068-BASE:0xa00af06c-BASE],'little')) == 'th.lrbu a2,s8,a5,0'
assert custom(int.from_bytes(rom[0xa00af06c-BASE:0xa00af070-BASE],'little')) == 'th.lrbu a1,s9,a5,0'
assert -0x100 <= -0x94 and -0x94+0x52 <= -0x34
for i in range(1,5):
    assert -0x87 + 16*i == -0x94 + 13 + 16*i
    assert -0x88 + 16*i == -0x94 + 12 + 16*i

bundle = json.loads((ROOT/'evidence/rea-0041-20261017/evidence/whole-rom-private-20261023.evidence.json').read_text(encoding='utf-8'))
record = next(r for r in bundle['records'] if r.get('evidence_id') == 'ev_19e11c8fc1582881b289f2b24c2a98bbb305f7c2e57caad784442a60d1fb76e5')
n = record['normalized_result']
assert [(r['source_address'],r['target_address']) for r in n['incoming_references']] == [('0xa005d142','0xa00adabc')]
refs = [r for r in n['outgoing_references'] if r.get('target_address') == '0xa00f4740']
assert {r['source_address'] for r in refs} == {'0xa00ae238','0xa00aef62','0xa00af17c'}

out = dict(method='Independent immutable ROM decode; prior E03 windows are input expectations only; no target execution.',
           source=str(ROM), base=hex(BASE), prior_windows=len(old['windows']), prior_instructions_checked=checked,
           windows=windows, exact_checks=checks, direct_edges={hex(a):hex(b) for a,b in edges.items()},
           callback_record=record['evidence_id'], incoming_refs=n['incoming_references'], converter_refs=refs,
           limitations=['No execution or reachability observation.', 'Vendor semantics compared only with existing local SLEIGH, not an independent vendor specification.',
                       'Selected callback normal path, not the complete page state machine; consumer store/argument review is manual.'])
(HERE/'independent-checks.json').write_text(json.dumps(out,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
print(json.dumps(dict(result='pass', old_windows=len(old['windows']), old_instructions=checked, retained_windows=len(windows),
                      retained_instructions=sum(len(w['instructions']) for w in windows), exact_checks=len(checks), direct_edges=len(edges))))
