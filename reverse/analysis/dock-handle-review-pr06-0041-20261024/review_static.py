"""P-R06 independent bounded ROM review. Python standard library only.
Does not import or execute P-06's checker; does not execute the target.
"""
import json
import re
from pathlib import Path

ROOT = Path('D:/Documents/PlatformIO/Projects/cuktech-ap01-firmware')
OUT = Path(__file__).resolve().parent
BASE = 0x9ffff000
ROM = ROOT / 'roms/0041/ap01-1.0.2_0041.bin'
INIT = 'reverse/analysis/factory-test-0041-20261023/retained-initializer.json'
CALLBACK = 'reverse/analysis/usb-interface-ota-0041-20261023.json'
init = json.loads((ROOT / INIT).read_text(encoding='utf-8'))['function']
cb = next(f for f in json.loads((ROOT / CALLBACK).read_text(encoding='utf-8'))['functions'] if f['address'] == '0xa00a8330')
assert init['evidence_id'] == 'ev_dc0e38b0f382799ea2a8e8ad7f21cefc5998b0767ecf38a58cfdebe8add167c3'
assert init['profile']['digest'] == 'bcefdee5092076e55636e077b45523e203f4b870ae7b7ab547945ed1b8162279'
assert cb['evidence_id'] == 'ev_6f900403de24d247461a1e302c564c71481c3d43d481acdc83bbb716318e1159'
assert cb['profile_digest'] == 'b6368dd18431e8113aa5026c713d41e648ab0f6ddd9421ff6c4a49e23b3cd2f3'

def sx(x, n):
    return x - (1 << n) if x & (1 << (n - 1)) else x

def decode(b, pc):
    h = int.from_bytes(b[:2], 'little')
    if h & 3 != 3:
        q, f = h & 3, h >> 13
        r = (h >> 7) & 31
        imm = sx(((h >> 12) & 1) << 5 | ((h >> 2) & 31), 6)
        if q == 1 and f in (0, 2):
            return ('addi', r, r if f == 0 else 0, imm)
        if q == 2 and f == 4 and not (h & 0x1000) and (h >> 2) & 31:
            return ('mv', r, (h >> 2) & 31)
        if q == 0 and f in (2, 6):
            off = ((h >> 10) & 7) << 3 | ((h >> 6) & 1) << 2 | ((h >> 5) & 1) << 6
            return ('lw' if f == 2 else 'sw', 8 + ((h >> 2) & 7), 8 + ((h >> 7) & 7), off)
        if q == 1 and f == 4 and (h >> 10) & 3 == 2:
            return ('andi', 8 + ((h >> 7) & 7), 8 + ((h >> 7) & 7), imm)
        if q == 1 and f in (6, 7):
            off = ((h >> 12) & 1) << 8 | ((h >> 10) & 3) << 3 | ((h >> 5) & 3) << 6 | ((h >> 3) & 3) << 1 | ((h >> 2) & 1) << 5
            return ('beq' if f == 6 else 'bne', 8 + ((h >> 7) & 7), 0, pc + sx(off, 9))
        raise AssertionError(('unsupported compressed', hex(pc), b.hex()))
    w = int.from_bytes(b[:4], 'little')
    op, rd, f3, rs1, rs2 = w & 127, (w >> 7) & 31, (w >> 12) & 7, (w >> 15) & 31, (w >> 20) & 31
    if op == 0x37:
        return ('lui', rd, w & 0xfffff000)
    if op in (0x13, 0x03):
        assert (op, f3) in ((0x13, 0), (0x03, 2))
        return ('addi' if op == 0x13 else 'lw', rd, rs1, sx(w >> 20, 12))
    if op == 0x23:
        assert f3 == 2
        return ('sw', rs2, rs1, sx((w >> 25) << 5 | ((w >> 7) & 31), 12))
    if op == 0x6f:
        imm = ((w >> 31) & 1) << 20 | ((w >> 12) & 255) << 12 | ((w >> 20) & 1) << 11 | ((w >> 21) & 1023) << 1
        return ('jal', rd, pc + sx(imm, 21))
    if op == 0x63:
        imm = ((w >> 31) & 1) << 12 | ((w >> 7) & 1) << 11 | ((w >> 25) & 63) << 5 | ((w >> 8) & 15) << 1
        return ({0: 'beq', 1: 'bne', 4: 'blt', 5: 'bge'}[f3], rs1, rs2, pc + sx(imm, 13))
    raise AssertionError(('unsupported standard', hex(pc), b.hex()))

windows = [
    ('loop_argument', 0xa005a76e, 0xa005a780, init),
    ('allocation_success', 0xa005cbc6, 0xa005cbee, init),
    ('open_result', 0xa005ab10, 0xa005ab32, init),
    ('global_fd', 0xa005b214, 0xa005b23e, init),
    ('register', 0xa005b2d8, 0xa005b314, init),
    ('post_start', 0xa005b314, 0xa005b32e, init),
    ('exit_gate', 0xa005c830, 0xa005c842, init),
    ('owner_close', 0xa005c8f8, 0xa005c910, init),
    ('callback_current_fd', 0xa00a839a, 0xa00a83c0, cb),
]
decoded, result_windows = {}, []
assert ROM.stat().st_size == 6769704
with ROM.open('rb') as rom:
    for name, start, end, source in windows:
        rom.seek(start - BASE)
        raw = rom.read(end - start)
        carrier = next(r for r in source['raw_ranges'] if int(r.get('start', hex(BASE + r['file_offset'])), 16) <= start and BASE + r['file_offset'] + r.get('length', len(r.get('hex', r.get('bytes_hex', ''))) // 2) >= end)
        retained = bytes.fromhex(carrier.get('hex', carrier.get('bytes_hex')))
        off = start - (BASE + carrier['file_offset'])
        assert raw == retained[off:off + len(raw)], name
        rows, pos = [], 0
        while pos < len(raw):
            size = 4 if raw[pos] & 3 == 3 else 2
            piece = raw[pos:pos + size]
            assert len(piece) == size
            instruction = decode(piece, start + pos)
            decoded[start + pos] = instruction
            rows.append({'pc': hex(start + pos), 'raw': piece.hex(), 'decoded': instruction})
            pos += size
        result_windows.append({'name': name, 'start': hex(start), 'end_exclusive': hex(end), 'evidence_id': source['evidence_id'], 'rows': rows})

# Independently specified critical ABI/operand assertions (register numbers RV32).
expected = {
    0xa005a77a: ('mv', 9, 10),
    0xa005cbca: ('addi', 10, 0, 0x19c),
    0xa005cbe2: ('jal', 1, 0xa008e362),
    0xa005cbe6: ('mv', 18, 10),
    0xa005cbe8: ('beq', 10, 0, 0xa005cbee),
    0xa005cbea: ('jal', 0, 0xa005aa68),
    0xa005ab1c: ('jal', 1, 0xa003f4f6),
    0xa005ab20: ('sw', 10, 18, 4),
    0xa005ab24: ('mv', 21, 10),
    0xa005ab2e: ('blt', 0, 10, 0xa005b214),
    0xa005b214: ('lui', 19, 0x62fc9000),
    0xa005b226: ('addi', 22, 19, 0x1b0),
    0xa005b232: ('sw', 21, 22, 0),
    0xa005b2e6: ('lw', 12, 18, 4),
    0xa005b2ea: ('addi', 19, 18, 8),
    0xa005b2ee: ('mv', 11, 19),
    0xa005b2f0: ('sw', 18, 18, 8),
    0xa005b2f4: ('mv', 10, 9),
    0xa005b2f6: ('jal', 1, 0xa009e4f6),
    0xa005b2fa: ('addi', 14, 18, 0x180),
    0xa005b2fe: ('lw', 15, 14, 0x18),
    0xa005b300: ('lui', 12, 0xa00a8000),
    0xa005b304: ('addi', 12, 12, 0x330),
    0xa005b308: ('addi', 15, 15, 1),
    0xa005b30a: ('sw', 15, 14, 0x18),
    0xa005b30c: ('addi', 11, 0, 1),
    0xa005b30e: ('mv', 10, 19),
    0xa005b310: ('jal', 1, 0xa009f9b6),
    0xa005c830: ('lw', 15, 9, 0x18),
    0xa005c836: ('sw', 0, 9, 0x18),
    0xa005c83e: ('beq', 20, 0, 0xa005c8f8),
    0xa005c8f8: ('lw', 15, 18, 4),
    0xa005c8fc: ('bge', 0, 15, 0xa005c910),
    0xa005c900: ('lui', 11, 0xa00a4000),
    0xa005c904: ('addi', 11, 11, -0x43a),
    0xa005c908: ('addi', 10, 18, 8),
    0xa005c90c: ('jal', 1, 0xa009fb96),
    0xa00a839a: ('andi', 12, 12, 1),
    0xa00a839e: ('lui', 18, 0x62fc9000),
    0xa00a83a2: ('addi', 18, 18, 0x1b0),
    0xa00a83ae: ('lw', 10, 18, 0),
    0xa00a83b2: ('addi', 12, 0, 1),
    0xa00a83b4: ('addi', 11, 8, -0x41),
    0xa00a83b8: ('jal', 1, 0xa003f6a2),
}
for pc, want in expected.items():
    assert decoded[pc] == want, (hex(pc), decoded[pc], want)
# init return not used before start, and start return not tested in selected suffix.
assert all(i[0] not in ('beq', 'bne', 'blt', 'bge') for pc, i in decoded.items() if 0xa005b2fa <= pc < 0xa005b314 or 0xa005b314 <= pc < 0xa005b32e)

registers = []
for reg, start, end in [('s1', 0xa005a77c, 0xa005b314), ('s2', 0xa005aa68, 0xa005c8f8)]:
    hits = []
    unknown = []
    for line in init['assembly']:
        m = re.match(r'(0x[0-9a-f]+):\s+(\S+)\s+([^,\s]+)', line)
        if m and start <= int(m[1], 16) < end:
            if m[3] == reg:
                hits.append(line)
                assert m[2] in ('sw', 'sh', 'sb', 'c.sw', 'c.swsp'), line
            if m[2].startswith(('custom', 'unknown', '.')):
                unknown.append(line)
    registers.append({'register': reg, 'start': hex(start), 'end_exclusive': hex(end), 'first_operand_rows': hits, 'unknown_mnemonics': unknown, 'limitation': 'Retained textual definition audit only; not complete CFG, arbitrary entries, vendor implicit effects or callee ABI proof.'})

result = {'review': 'P-R06', 'status': 'PASS for bounded stage; full close unresolved', 'method': 'stdlib manual RV32+C fields, ROM/retained raw comparison; author checker neither read nor imported nor executed', 'mapping': hex(BASE), 'rom_identity': 'inherited CATALOG SHA256 972db4c136c7ed9e24a83c07c1a7fd62040ca018b08ca285216d26b1fee3c6b9; exact length independently checked', 'sources': [{'path': INIT, 'evidence_id': init['evidence_id'], 'profile_digest': init['profile']['digest']}, {'path': CALLBACK, 'evidence_id': cb['evidence_id'], 'profile_digest': cb['profile_digest']}], 'bytes': sum(b-a for _,a,b,_ in windows), 'instructions': len(decoded), 'critical_assertions': len(expected), 'windows': result_windows, 'register_metadata': registers, 'new_helper_bodies': 0, 'limitations': ['normal ABI-preserving callees', 'no complete CFG or reachability proof', 'no global fd stability proof', 'no fd close, timer delete, pending drain, exactly-once or hardware shutdown proof']}
(OUT / 'independent-checks.json').write_text(json.dumps(result, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
print(json.dumps({k: result[k] for k in ('status', 'bytes', 'instructions', 'critical_assertions', 'register_metadata')}, ensure_ascii=False))
