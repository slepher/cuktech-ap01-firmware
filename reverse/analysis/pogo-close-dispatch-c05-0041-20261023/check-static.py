"""C05 bounded static ROM checks. Does not execute target code."""
import json
from pathlib import Path
from capstone import Cs, CS_ARCH_RISCV, CS_MODE_RISCV32, CS_MODE_RISCVC, cs_version

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
ROM = Path('D:/Documents/PlatformIO/Projects/cuktech-ap01-firmware/roms/0041/ap01-1.0.2_0041.bin')
BASE = 0x9ffff000
rom = ROM.read_bytes()
cs = Cs(CS_ARCH_RISCV, CS_MODE_RISCV32 | CS_MODE_RISCVC)
windows = []
for name, start, end in [
    ('close_registration_type8_dispatch', 0xa009fb96, 0xa009fc10),
    ('close_common_enqueue', 0xa009fcde, 0xa009fce6),
    ('close_type8_stop_call', 0xa009ffbe, 0xa009ffc4),
    ('close_return', 0xa00a0026, 0xa00a003a),
    ('pending_link', 0xa009c228, 0xa009c26a),
    ('finish_entry_type_mask', 0xa009f524, 0xa009f5a4),
    ('finish_return', 0xa009f5ba, 0xa009f5ce),
    ('finish_callback_tail', 0xa009f8b6, 0xa009f8ea),
    ('retained_loop_detach', 0xa005c166, 0xa005c172),
    ('retained_loop_consume', 0xa005c802, 0xa005c80e),
    ('poll_init_type_corroboration', 0xa009e5f6, 0xa009e608),
    ('existing_callback_context', 0xa00a3bc6, 0xa00a3be0),
]:
    raw = rom[start-BASE:end-BASE]
    ins = list(cs.disasm(raw, start))
    assert sum(i.size for i in ins) == len(raw), name
    windows.append(dict(name=name, start=hex(start), end_exclusive=hex(end),
        instructions=[dict(address=hex(i.address), hex=i.bytes.hex(), decode=i.mnemonic+' '+i.op_str) for i in ins]))

def sx(n, bits):
    return n-(1 << bits) if n & (1 << (bits-1)) else n

checks = []
def check(pc, kind, expected):
    w = int.from_bytes(rom[pc-BASE:pc-BASE+4], 'little')
    h = w & 0xffff
    if kind in ('lw', 'lbu'):
        assert w & 127 == 3 and (w >> 12 & 7) == (2 if kind == 'lw' else 4)
        got = [w >> 7 & 31, w >> 15 & 31, sx(w >> 20, 12)]
    elif kind in ('sw', 'sb'):
        assert w & 127 == 0x23 and (w >> 12 & 7) == (2 if kind == 'sw' else 0)
        got = [w >> 20 & 31, w >> 15 & 31, sx(((w >> 25) << 5) | (w >> 7 & 31), 12)]
    elif kind in ('c.lw', 'c.sw'):
        assert h & 3 == 0 and h >> 13 == (2 if kind == 'c.lw' else 6)
        got = [8+(h >> 2 & 7), 8+(h >> 7 & 7), ((h >> 10 & 7) << 3) | ((h >> 6 & 1) << 2) | ((h >> 5 & 1) << 6)]
    elif kind == 'c.mv':
        assert h & 0xf003 == 0x8002 and h & 0x1000 == 0
        got = [h >> 7 & 31, h >> 2 & 31]
    elif kind == 'c.jalr':
        assert h & 0xf07f == 0x9002
        got = [h >> 7 & 31]
    elif kind == 'c.j':
        assert h & 0xe003 == 0xa001
        imm = ((h >> 12 & 1) << 11) | ((h >> 11 & 1) << 4) | ((h >> 9 & 3) << 8) | ((h >> 8 & 1) << 10) | ((h >> 7 & 1) << 6) | ((h >> 6 & 1) << 7) | ((h >> 3 & 7) << 1) | ((h >> 2 & 1) << 5)
        got = [(pc+sx(imm,12)) & 0xffffffff]
    elif kind == 'jal':
        assert w & 127 == 0x6f
        imm = ((w >> 31) << 20) | ((w >> 12 & 255) << 12) | ((w >> 20 & 1) << 11) | ((w >> 21 & 1023) << 1)
        got = [w >> 7 & 31, (pc+sx(imm,21)) & 0xffffffff]
    elif kind == 'branch':
        assert w & 127 == 0x63
        imm = ((w >> 31) << 12) | ((w >> 7 & 1) << 11) | ((w >> 25 & 63) << 5) | ((w >> 8 & 15) << 1)
        got = [w >> 12 & 7, w >> 15 & 31, w >> 20 & 31, (pc+sx(imm,13)) & 0xffffffff]
    else:
        raise ValueError(kind)
    assert got == expected, (hex(pc), kind, got, expected)
    checks.append(dict(address=hex(pc), kind=kind, decoded_fields=got))

for args in [
    (0xa009fbc6,'c.sw',[14,10,0x2c]),
    (0xa009fbc8,'lbu',[14,10,8]),
    (0xa009fbcc,'c.sw',[11,10,0xc]),
    (0xa009fbd0,'c.mv',[18,10]),
    (0xa009fc06,'branch',[0,14,13,0xa009ffbe]),
    (0xa009ffbe,'jal',[1,0xa009f972]),
    (0xa009ffc2,'c.j',[0xa009fcde]),
    (0xa009fcde,'c.mv',[10,18]),
    (0xa009fce0,'jal',[1,0xa009c228]),
    (0xa009fce4,'c.j',[0xa00a0026]),
    (0xa009c256,'c.lw',[15,10,4]),
    (0xa009c258,'lw',[14,15,0xd4]),
    (0xa009c25c,'c.sw',[14,10,0x28]),
    (0xa009c25e,'sw',[10,15,0xd4]),
    (0xa005c166,'lw',[10,9,0xd4]),
    (0xa005c16a,'sw',[0,9,0xd4]),
    (0xa005c16e,'branch',[1,10,0,0xa005c802]),
    (0xa005c802,'lw',[21,10,0x28]),
    (0xa005c806,'jal',[1,0xa009f524]),
    (0xa005c80a,'c.mv',[10,21]),
    (0xa005c80c,'c.j',[0xa005c16e]),
    (0xa009f56c,'c.mv',[9,10]),
    (0xa009f58e,'branch',[1,15,0,0xa009f8b6]),
    (0xa009f8de,'c.lw',[15,9,0xc]),
    (0xa009f8e4,'c.mv',[10,9]),
    (0xa009f8e6,'c.jalr',[15]),
    (0xa009f8e8,'c.j',[0xa009f5ba]),
    (0xa009e5fc,'sb',[15,21,8]),
    (0xa009e600,'sw',[15,21,0x2c]),
    (0xa009e604,'sw',[19,21,4]),
    (0xa00a3bd0,'c.lw',[9,10,0]),
]:
    check(*args)

# Exact constants/encodings establish type 8 and membership of the common-tail mask.
assert rom[0xa009e5f6-BASE:0xa009e5f8-BASE].hex() == 'a147'
assert rom[0xa009f586-BASE:0xa009f58c-BASE].hex() == '89679387e775'
assert 0x275e & (1 << 8)
retained = json.loads((ROOT/'reverse/analysis/factory-test-0041-20261023/retained-initializer.json').read_text())['function']
for item in retained['raw_ranges']:
    pc = int(item['start'],16); raw = bytes.fromhex(item['hex'])
    assert rom[pc-BASE:pc-BASE+len(raw)] == raw
result = dict(task='C05', rom_path=str(ROM), va_base=hex(BASE), capstone_version=cs_version(),
    retained_initializer_evidence_id=retained['evidence_id'], windows=windows, raw_field_checks=checks,
    validation=dict(selected_bytes=sum(int(w['end_exclusive'],16)-int(w['start'],16) for w in windows),
        undecoded_selected_bytes=0, raw_field_checks=len(checks), retained_initializer_ranges_match=True,
        type8_in_common_tail_mask=True, firmware_executed=False),
    limitations=['Only selected paths of three core functions are restored; callees, full loop lifecycle and timer teardown remain unexpanded.',
        'Poll init and inherited loop/callback windows are corroboration only; no new whole-function recovery is claimed.',
        'No source/version identity or open-source exclusion is established.'])
(HERE/'instruction-evidence.json').write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
print(json.dumps(result['validation']))
