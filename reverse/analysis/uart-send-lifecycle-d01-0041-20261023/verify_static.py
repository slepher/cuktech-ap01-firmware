"""D01 bounded read-only ROM review. No target execution or shared REA state."""
import json
from pathlib import Path
import capstone
from capstone import Cs, CS_ARCH_RISCV, CS_MODE_RISCV32, CS_MODE_RISCVC

HERE = Path(__file__).resolve().parent
ROOT = Path('D:/Documents/PlatformIO/Projects/cuktech-ap01-firmware')
BASE = 0x9ffff000
rom = (ROOT / 'roms/0041/ap01-1.0.2_0041.bin').read_bytes()
record = json.loads((ROOT / 'reverse/analysis/usb-interface-ota-0041-20261023.json').read_text(encoding='utf-8'))
dock = json.loads((ROOT / 'reverse/analysis/dock-presence-polling-0041-20261023/instruction-windows.json').read_text(encoding='utf-8'))
decoder = Cs(CS_ARCH_RISCV, CS_MODE_RISCV32 | CS_MODE_RISCVC)
functions = {int(f['address'], 16): f for f in record['functions']}
windows = [
    ('submit', 0xa01951e2, 0xa019530a, 0xa01951e2),
    ('queue_contract', 0xa01915bc, 0xa0191652, 0xa01915bc),
    ('start', 0xa00ee9ce, 0xa00eea08, 0xa00ee9ce),
    ('frame', 0xa01a4ff8, 0xa01a50fe, 0xa01a4ff8),
    ('write_progress', 0xa00ee96c, 0xa00ee9ce, 0xa00ee96c),
    ('response_dispatch_contract', 0xa00a84ee, 0xa00a8552, 0xa00a8330),
    ('poll_progress_call', 0xa00a844e, 0xa00a8454, 0xa00a8330),
    ('normal_handler_entry', 0xa00a85a0, 0xa00a85e4, 0xa00a8582),
    ('normal_handler_event24', 0xa00a8856, 0xa00a8870, 0xa00a8582),
    ('normal_handler_cmd58', 0xa00a876e, 0xa00a8794, 0xa00a8582),
    ('normal_cache_state_clear', 0xa0191652, 0xa0191700, None),
    ('write_wrapper', 0xa0027e94, 0xa0027eee, None),
    ('write_operation_dispatch', 0xa0025874, 0xa00258a0, None),
]
vendor_fields = {
    0xa01a5052: (5, 0, 10, 20, 15),  # th.srb a0,s4,a5,0
    0xa01a5064: (5, 0, 10, 14, 15),
    0xa01a50b0: (5, 0, 13, 15, 14),
    0xa01a50b6: (4, 16, 10, 11, 19),  # th.lrbu a0,a1,s3,0
    0xa01a50ca: (5, 0, 17, 15, 14),
    0xa01a50da: (5, 0, 10, 15, 14),
}
model = ROOT / 'evidence/rea-0041-20261017/ghidra/Ghidra/Processors/RISCV/data/languages/ap01thead2.sinc'
model_lines = model.read_text(encoding='utf-8').splitlines()
model_excerpts = []
for needle in (':th.srb ', ':th.lrbu '):
    start = next(i for i, line in enumerate(model_lines) if line.startswith(needle))
    end = next(i for i in range(start + 1, len(model_lines)) if model_lines[i] == '}')
    model_excerpts.append(dict(line=start + 1, text='\n'.join(model_lines[start:end + 1])))

by_pc, output, provenance = {}, [], {}
for name, start, end, owner in windows:
    provider = {}
    if owner:
        fn = functions[owner]
        for block in fn['raw_ranges']:
            raw = bytes.fromhex(block['bytes_hex'])
            assert rom[block['file_offset']:block['file_offset'] + len(raw)] == raw
        provider = {int(s.split(':')[0], 16): s.split(': ', 1)[1] for s in fn['assembly']}
        provenance[hex(owner)] = dict(evidence_id=fn['evidence_id'], source=fn['source']['path'], profile=fn['profile_digest'], body=fn['body']['ranges'])
    elif name == 'normal_cache_state_clear':
        old = next(w for w in dock['windows'] if w['name'] == 'copy_response')
        assert rom[start-BASE:end-BASE] == bytes.fromhex(old['hex'])
        provider = {int(i['address'], 16): i['assembly'] for i in old['instructions']}
    rows, pc = [], start
    while pc < end:
        off = pc - BASE
        half = int.from_bytes(rom[off:off+2], 'little')
        size = 4 if half & 3 == 3 else 2
        assert pc + size <= end
        raw = rom[off:off+size]
        if pc in vendor_fields:
            word = int.from_bytes(raw, 'little')
            assert word & 127 == 11
            actual = ((word >> 12) & 7, (word >> 27) & 31, (word >> 7) & 31,
                      (word >> 15) & 31, (word >> 20) & 31)
            assert actual == vendor_fields[pc], (hex(pc), actual)
            assert (word >> 25) & 3 == 0
            mnemonic, operands = 'vendor_fields_verified', str(actual)
        else:
            ins = next(decoder.disasm(raw, pc), None)
            assert ins is not None and ins.size == size, hex(pc)
            mnemonic, operands = ins.mnemonic, ins.op_str
        if owner or name == 'normal_cache_state_clear':
            assert pc in provider
        row = dict(pc=hex(pc), file_offset=off, bytes=raw.hex(), mnemonic=mnemonic,
                   operands=operands, retained_text=provider.get(pc))
        rows.append(row)
        by_pc[pc] = row
        pc += size
    output.append(dict(name=name, start=hex(start), end_exclusive=hex(end), instructions=rows,
                       source_kind='retained bytes compared to ROM' if owner or name == 'normal_cache_state_clear' else 'new bounded ROM decoding; boundary inferred from return and next entry'))

checks = []
def exact(pc, mnemonic, operands, claim):
    row = by_pc[pc]
    assert (row['mnemonic'], row['operands']) == (mnemonic, operands), (hex(pc), row)
    checks.append(dict(pc=hex(pc), claim=claim))

for args in [
    (0xa0195224, 'lbu', 'a2, 2(s3)', 'duplicate compare length is slot length'),
    (0xa0195268, 'sb', 'a5, 0(s1)', 'queue marked occupied before byte copy'),
    (0xa0195270, 'lbu', 'a2, 1(s2)', 'queued copy length'),
    (0xa0195274, 'lw', 'a1, 4(s2)', 'queued copy source pointer'),
    (0xa01952cc, 'sb', 'a5, 3(s1)', 'active command byte'),
    (0xa01952da, 'sb', 'a2, 4(s1)', 'active length byte'),
    (0xa0195302, 'lbu', 'a5, 0(s1)', 'submit rereads state after copy'),
    (0xa0191628, 'sb', 'zero, 0(s1)', 'slot release after starter return; B20 contract'),
    (0xa00ee9f4, 'sb', 's2, 1(s1)', 'starter stores saved1 after both calls'),
    (0xa00ee9f8, 'sb', 'zero, 2(s1)', 'starter clears wait after both calls'),
    (0xa01a501a, 'sb', 'a4, 0x5e(a5)', 'builder initializes frame length only'),
    (0xa01a502e, 'sh', 'a5, 0x48c(s1)', 'builder writes A5 and zero byte together'),
    (0xa01a5056, 'lbu', 'a4, 4(s2)', 'builder rereads length for CRC high destination'),
    (0xa01a5068, 'lbu', 'a3, 4(s2)', 'builder rereads length for loop count'),
    (0xa01a5072, 'andi', 'a3, a3, 0xff', 'loop bound byte truncation'),
    (0xa00ee984, 'lbu', 'a1, 0x5f(s1)', 'cursor read before write'),
    (0xa00ee992, 'andi', 'a2, a2, 0xff', 'remaining count byte truncation'),
    (0xa00ee9a0, 'lbu', 'a5, 0x5f(s1)', 'cursor reread after write'),
    (0xa00ee9a6, 'lbu', 'a5, 0x5e(s1)', 'frame length reread after write'),
    (0xa00ee9aa, 'andi', 'a0, a0, 0xff', 'new cursor byte truncation'),
    (0xa00ee9ae, 'sb', 'a0, 0x5f(s1)', 'positive write advances cursor'),
    (0xa00ee9bc, 'sb', 'a4, 0x2f0(a5)', 'full write sets state2'),
    (0xa00ee9c0, 'sh', 'zero, 0x5e(s1)', 'full write clears length and cursor together'),
    (0xa00a851a, 'sb', 'a5, 0(s3)', 'matching response sets state3 before callback'),
    (0xa00a852e, 'lw', 'a5, 0(s4)', 'first handler load'),
    (0xa00a853a, 'lw', 'a5, 0(s4)', 'handler reread after first callback'),
    (0xa00a8542, 'addi', 'a0, zero, 0x24', 'second event command'),
    (0xa00a8548, 'sb', 'zero, 0x30(s1)', 'only parser stage reset here'),
    (0xa0191668, 'sb', 'zero, 0x2f0(a5)', 'normal cache helper clears transmission state'),
    (0xa0027ec8, 'lw', 'a0, -0x14(s0)', 'wrapper releases acquired handle after write'),
    (0xa0027ee6, 'c.mv', 'a0, s1', 'wrapper returns saved write result'),
    (0xa0025874, 'c.lw', 'a5, 0(a0)', 'operation dispatcher tests object flags'),
    (0xa002587a, 'c.lw', 'a4, 0xc(a0)', 'first object link'),
    (0xa0025880, 'c.lw', 'a4, 0x10(a4)', 'operations link'),
    (0xa0025884, 'c.lw', 'a4, 0xc(a4)', 'write operation pointer'),
]:
    exact(*args)

edges = []
for pc, expected in [
    (0xa01952ec, 0xa00ee9ce), (0xa0191624, 0xa00ee9ce),
    (0xa00ee9ec, 0xa01a4ff8), (0xa00ee9f0, 0xa00ee96c),
    (0xa01a5032, 0xa00ee8fc), (0xa01a5046, 0xa00ee8fc),
    (0xa00ee998, 0xa0027e94), (0xa00ee99c, 0xa00ee9c4),
    (0xa00ee9b2, 0xa00ee9c4), (0xa00a844e, 0xa00ee96c),
    (0xa00a84f6, 0xa00a8548), (0xa00a8502, 0xa00a8548),
    (0xa00a8532, 0xa00a8548), (0xa00a854c, 0xa00ee9ce),
    (0xa00a85d0, 0xa00a8856), (0xa00a8860, 0xa00a886a),
    (0xa00a886a, 0xa01915bc), (0xa00a8780, 0xa0191652),
    (0xa0027eae, 0xa0025904), (0xa0027ec2, 0xa0025874),
    (0xa0027ecc, 0xa0027e54), (0xa0027ed0, 0xa0027ee0),
]:
    row = by_pc[pc]
    target = (pc + int(row['operands'].split(',')[-1].strip(), 0)) & 0xffffffff
    assert target == expected, (hex(pc), hex(target), hex(expected))
    edges.append(dict(pc=hex(pc), target=hex(target)))
for pc, reg in [(0xa00a8538, 'a5'), (0xa00a8546, 'a5'), (0xa0025890, 'a4')]:
    exact(pc, 'c.jalr', reg, 'indirect call ABI target register')

def signed(value, bits):
    return value - (1 << bits) if value & (1 << (bits - 1)) else value

for pc, target in [(0xa0195234, 0xa00501be), (0xa0195294, 0xa000589c),
                   (0xa01952fa, 0xa000589c)]:
    hi = int.from_bytes(bytes.fromhex(by_pc[pc]['bytes']), 'little')
    lo = int.from_bytes(bytes.fromhex(by_pc[pc + 4]['bytes']), 'little')
    assert hi & 127 == 0x17 and (hi >> 7) & 31 == 1
    assert lo & 0x707f == 0x67 and (lo >> 7) & 31 == 1 and (lo >> 15) & 31 == 1
    actual = (pc + signed(hi & 0xfffff000, 32) + signed(lo >> 20, 12)) & 0xfffffffe
    assert actual == target
    edges.append(dict(pc=hex(pc), target=hex(target), kind='raw AUIPC/JALR fields'))

result = dict(task='D01', result='static_checks_passed', capstone=capstone.__version__,
              rom=str(ROOT / 'roms/0041/ap01-1.0.2_0041.bin'), mapping_base=hex(BASE),
              retained_record='reverse/analysis/usb-interface-ota-0041-20261023.json',
              retained_dock_record='reverse/analysis/dock-presence-polling-0041-20261023/instruction-windows.json',
              provenance=provenance, windows=output, exact_checks=checks, direct_edges=edges,
              vendor_model=dict(path=str(model), excerpts=model_excerpts),
              limits=['Static only; no firmware execution, input replay or timing proof.',
                      'Wrapper/operation boundaries newly inferred from bytes; no source/version certification.',
                      'Selected normal handler and parser windows only; B20/B18/CRC retained contracts.',
                      'Driver indirect target, all global writers, initial cursor and final teardown remain boundaries.'])
(HERE / 'instruction-evidence.json').write_text(json.dumps(result, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
print(json.dumps(dict(result=result['result'], windows=len(output), instructions=len(by_pc),
                      vendor=len(vendor_fields), exact_checks=len(checks), edges=len(edges))))
