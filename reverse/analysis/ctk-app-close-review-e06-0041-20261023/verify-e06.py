"""Independent E06 static review. ROM bytes are data; no firmware execution."""
import json
from pathlib import Path
from capstone import Cs, CS_ARCH_RISCV, CS_MODE_RISCV32, CS_MODE_RISCVC

HERE = Path(__file__).resolve().parent
ROOT = Path('D:/Documents/PlatformIO/Projects/cuktech-ap01-firmware')
ROM_PATH = ROOT / 'roms/0041/ap01-1.0.2_0041.bin'
BASE = 0x9ffff000
blob = ROM_PATH.read_bytes()
engine = Cs(CS_ARCH_RISCV, CS_MODE_RISCV32 | CS_MODE_RISCVC)
old = json.loads((HERE.parent / 'ctk-app-close-e05-0041-20261023/instruction-evidence.json').read_text())

def sx(v, bits):
    return v - (1 << bits) if v >> (bits - 1) else v

def read_word(pc):
    return int.from_bytes(blob[pc-BASE:pc-BASE+4], 'little')

def decode_window(name, begin, end):
    rows = []
    pc = begin
    while pc < end:
        size = 2 if blob[pc-BASE] & 3 != 3 else 4
        assert pc + size <= end
        raw = blob[pc-BASE:pc-BASE+size]
        word = int.from_bytes(raw, 'little')
        row = dict(address=hex(pc), file_offset=pc-BASE, hex=raw.hex())
        if size == 4 and word & 127 == 11:
            f3 = (word >> 12) & 7
            fields = dict(rd=(word >> 7) & 31, rs1=(word >> 15) & 31,
                          rs2=(word >> 20) & 31, shift=(word >> 25) & 3,
                          high5=word >> 27, msb=word >> 26, lsb=(word >> 20) & 63)
            if f3 == 3:
                kind = 'extu'
            elif f3 == 4 and word >> 27 == 8:
                kind = 'lrw'
            elif f3 == 5 and word >> 27 == 8:
                kind = 'srw'
            elif f3 == 1 and word >> 27 == 0:
                kind = 'addsl'
            else:
                raise AssertionError((hex(pc), hex(word)))
            row.update(vendor=kind, fields=fields)
        else:
            ins = next(engine.disasm(raw, pc), None)
            assert ins is not None and ins.size == size, hex(pc)
            row['assembly'] = ins.mnemonic + ' ' + ins.op_str
            if size == 4 and word & 127 == 111:
                displacement = ((word >> 31) << 20) | (((word >> 12) & 255) << 12) | (((word >> 20) & 1) << 11) | (((word >> 21) & 1023) << 1)
                row['target'] = hex(pc + sx(displacement, 21))
            elif size == 4 and word & 127 == 99:
                displacement = ((word >> 31) << 12) | (((word >> 7) & 1) << 11) | (((word >> 25) & 63) << 5) | (((word >> 8) & 15) << 1)
                row['target'] = hex(pc + sx(displacement, 13))
            elif size == 2 and ins.mnemonic in ('c.j', 'c.jal', 'c.beqz', 'c.bnez'):
                row['target'] = hex(pc + int(ins.op_str.split(',')[-1].strip(), 0))
        rows.append(row)
        pc += size
    return dict(name=name, start=hex(begin), end_exclusive=hex(end), instructions=rows)

windows = [decode_window(w['name'], int(w['start'], 16), int(w['end_exclusive'], 16)) for w in old['windows']]
compared = 0
for prior, fresh in zip(old['windows'], windows):
    assert len(prior['instructions']) == len(fresh['instructions'])
    for p, n in zip(prior['instructions'], fresh['instructions']):
        assert (p['address'], p['hex']) == (n['address'], n['hex'])
        if 'assembly' in n:
            assert p['assembly'] == n['assembly']
        else:
            assert p['assembly'].startswith('th.' + n['vendor'] + ' ')
            assert p['fields'] == {**n['fields'], 'funct3': (int.from_bytes(bytes.fromhex(n['hex']), 'little') >> 12) & 7}
        assert p.get('target') == n.get('target')
        compared += 1
windows += [decode_window('adapter_nonnull_entry', 0xa01ad654, 0xa01ad6a8),
            decode_window('descriptor_allocation', 0xa01b93b4, 0xa01b9432),
            decode_window('other_remover_state_origin', 0xa00f2f54, 0xa00f2f98),
            decode_window('independent_group_list_allocation', 0xa00d733a, 0xa00d7352)]
windows += [decode_window('neighbor_head_dispatch',0xa00a3a1c,0xa00a3a30),
            decode_window('head_initialization',0xa00a562c,0xa00a5664),
            decode_window('clobbered_candidate',0xa00ab18e,0xa00ab1a4),
            decode_window('neighbor_head_users',0xa01b25ae,0xa01b260a)]
index = {int(r['address'], 16): r for w in windows for r in w['instructions']}
checks = []
def fields(pc, **expected):
    actual = index[pc]['fields']
    assert all(actual[k] == v for k, v in expected.items()), hex(pc)
    checks.append(dict(address=hex(pc), expected_fields=expected))
fields(0xa00d76d0, rd=10, rs1=13, msb=19, lsb=4)
fields(0xa00d7800, rd=9, rs1=14, rs2=15, shift=2)
fields(0xa0089ce4, rd=12, rs1=11, rs2=15, shift=0)
fields(0xa0089d3a, rd=11, rs1=11, rs2=14, shift=0)
fields(0xa00f2fca, rd=11, rs1=11, rs2=15, shift=0)
for pc,target in [(0xa00ab930,0xa008b51a),(0xa00ab95a,0xa008ae58),
                  (0xa00ab960,0xa008ab8a),(0xa008ae6e,0xa0089d02),
                  (0xa008ae7e,0xa008ab8a),(0xa00f2fba,0xa0089d02),
                  (0xa00f2fc0,0xa008ab8a),(0xa00dd044,0xa00dcf52),
                  (0xa00dd000,0xa00d7806),(0xa00dd03e,0xa008ab8a)]:
    assert index[pc]['target'] == hex(target)
    checks.append(dict(address=hex(pc), direct_target=hex(target)))
for pc, target in [(0xa005d146,0xa01b28ce),(0xa005d198,0xa01ad654)]:
    u, j = read_word(pc), read_word(pc+4)
    assert u & 127 == 23 and j & 127 == 103
    assert (u >> 7) & 31 == (j >> 15) & 31
    actual = (pc + (u & 0xfffff000) + sx(j >> 20,12)) & 0xffffffff
    assert actual == target
    checks.append(dict(address=hex(pc), pair_target=hex(actual)))
# Independently evaluate fixed comparison constants, not just disassembly text.
assert ((sx(0x38,6) << 12) - 1) & 0xffffffff == 0xffff7fff
assert (read_word(0xa00f2fa4) & 0xfffff000) + sx(read_word(0xa00f2fa8) >> 20,12) == 0xa00f5288
assert (read_word(0xa005d13c) & 0xfffff000) + sx(read_word(0xa005d142) >> 20,12) == 0xa00adabc
class_base = 0xa05647fc
class_words = [hex(read_word(class_base+i)) for i in range(0,40,4)]
assert class_words[2] == '0xa00b1df8'
assert (int(class_words[8],16) >> 4) & 0xffff == 0x68

candidates = []
for pc in range(0xa0000000,0xa01b9800,2):
    u = read_word(pc)
    if u & 127 != 55 or u & 0xfffff000 != 0x62fcb000:
        continue
    reg = (u >> 7) & 31
    for q in range(pc+4,pc+38,2):
        v = read_word(q)
        imm = sx(v >> 20,12)
        if v & 127 in (3,19) and (v >> 15) & 31 == reg and 0x530 <= imm <= 0x53c:
            candidates.append(dict(lui=hex(pc), candidate=hex(q), register_number=reg, immediate=hex(imm)))
assert [(x['lui'],x['candidate'],x['immediate']) for x in candidates] == [(x['lui'],x['candidate'],x['immediate']) for x in old['head_candidate_search']['candidates']]

source = ROOT / 'evidence/rea-0041-20261017/evidence/whole-rom-private-20261023.evidence.json'
records = []
for r in json.loads(source.read_text())['records']:
    if r['operation'] == 'analyze_function' and r['parameters']['procedure'] in ('0xa005cc1e','0xa00adabc','0xa00afc88'):
        n = r['normalized_result']
        records.append(dict(procedure=r['parameters']['procedure'], evidence_id=r['evidence_id'], incoming_references=n['incoming_references'], callers=n['callers']))
assert len(records) == 3
result = dict(rom=str(ROM_PATH), base=hex(BASE), prior_instructions_independently_compared=compared,
              windows=windows, checks=checks, class_words=class_words,
              bounded_head_candidates=candidates, retained_source=str(source), retained_boundaries=records)
(HERE / 'independent-checks.json').write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
print(f'{compared} prior instructions independently matched; {len(windows)} windows, {sum(len(w["instructions"]) for w in windows)} instructions; {len(checks)} field/pair checks; {len(candidates)} bounded candidates; {len(records)} provenance records')
