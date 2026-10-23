"""C08 independent bounded raw-encoding review; reads ROM, never executes it."""
import json
from pathlib import Path
from capstone import Cs, CS_ARCH_RISCV, CS_MODE_RISCV32, CS_MODE_RISCVC

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
ROM = Path('D:/Documents/PlatformIO/Projects/cuktech-ap01-firmware/roms/0041/ap01-1.0.2_0041.bin')
BASE = 0x9ffff000
raw = ROM.read_bytes()
old = json.loads((ROOT / 'reverse/analysis/pogo-close-consume-c07-0041-20261023/instruction-evidence.json').read_text())
cs = Cs(CS_ARCH_RISCV, CS_MODE_RISCV32 | CS_MODE_RISCVC)

def sx(v, n):
    return v - (1 << n) if v >> (n - 1) else v

def word(pc):
    return int.from_bytes(raw[pc-BASE:pc-BASE+4], 'little')

controls = []
total = count = 0
for window in old['windows']:
    start, end = int(window['start'], 16), int(window['end_exclusive'], 16)
    code = raw[start-BASE:end-BASE]
    decoded = list(cs.disasm(code, start))
    assert sum(i.size for i in decoded) == len(code)
    assert [(i.address, i.bytes.hex()) for i in decoded] == [(int(i['address'],16), i['hex']) for i in window['instructions']]
    total += len(code)
    count += len(decoded)
    for ins in decoded:
        pc, w = ins.address, int.from_bytes(ins.bytes, 'little')
        target = None
        kind = None
        if ins.size == 4:
            op, rd, f3, rs1, rs2 = w & 127, w >> 7 & 31, w >> 12 & 7, w >> 15 & 31, w >> 20 & 31
            if op == 0x63:
                disp = ((w >> 31 & 1) << 12) | ((w >> 7 & 1) << 11) | ((w >> 25 & 63) << 5) | ((w >> 8 & 15) << 1)
                target, kind = pc + sx(disp,13), 'branch'
            elif op == 0x6f:
                disp = ((w >> 31 & 1) << 20) | ((w >> 12 & 255) << 12) | ((w >> 20 & 1) << 11) | ((w >> 21 & 1023) << 1)
                assert rd == 1
                target, kind = pc + sx(disp,21), 'call-jal'
            elif op == 0x67:
                u = word(pc-4)
                assert f3 == 0 and rd == rs1 == 1 and u & 127 == 0x17 and u >> 7 & 31 == 1
                target = (pc-4 + sx(u & 0xfffff000,32) + sx(w >> 20,12)) & 0xfffffffe
                kind = 'call-auipc-jalr'
        else:
            q, f = w & 3, w >> 13
            if q == 1 and f in (6,7):
                disp = ((w >> 12 & 1) << 8) | ((w >> 10 & 3) << 3) | ((w >> 5 & 3) << 6) | ((w >> 3 & 3) << 1) | ((w >> 2 & 1) << 5)
                target, kind = pc + sx(disp,9), 'branch-compressed'
            elif q == 1 and f in (1,5):
                disp = ((w >> 12 & 1) << 11) | ((w >> 11 & 1) << 4) | ((w >> 9 & 3) << 8) | ((w >> 8 & 1) << 10) | ((w >> 7 & 1) << 6) | ((w >> 6 & 1) << 7) | ((w >> 3 & 7) << 1) | ((w >> 2 & 1) << 5)
                target, kind = pc + sx(disp,12), 'jump-compressed' if f == 5 else 'call-compressed'
            elif q == 2 and f == 4:
                # Only terminal C.JR has rs2=0; other CR encodings are register moves.
                if w >> 2 & 31 == 0:
                    assert pc == 0xa005cad0 and w == 0x8082
                    kind = 'return-ra'
        if kind:
            controls.append(dict(pc=hex(pc), raw=ins.bytes.hex(), kind=kind, target=hex(target) if target is not None else None))

by_pc = {int(c['pc'],16): c for c in controls}
for pc, target in [(0xa005c16e,0xa005c802),(0xa005c19c,0xa005beac),(0xa005c80c,0xa005c16e),(0xa005c810,0xa005c836),(0xa005c832,0xa005bfd2)]:
    assert by_pc[pc]['target'] == hex(target)
assert word(0xa005c83a) == 0xa01c44b7  # LUI s1, a01c4: previous loop alias overwritten.
assert word(0xa005c836) == 0x0004ac23  # SW zero, 18(s1), before alias overwrite.
tail = [c for c in controls if int(c['pc'],16) >= 0xa005c8f8]
branches = [c for c in tail if c['kind'].startswith('branch')]
calls = [c for c in tail if c['kind'].startswith('call')]
assert len(branches) == 6 and all(int(c['pc'],16) < int(c['target'],16) <= 0xa005cad0 for c in branches)
assert len(calls) == 17
assert all(c['kind'] in ('branch','call-jal','call-auipc-jalr','return-ra') for c in tail)
assert tail[-1]['kind'] == 'return-ra'
assert [c['target'] for c in calls if c['kind'] == 'call-auipc-jalr'] == ['0xa01b2b5c','0xa01b2b5c','0xa01b2cb0','0xa01aca1a','0xa01aca1a']
assert set(c['target'] for c in calls if c['kind'] == 'call-jal') == {'0xa008b51a','0xa009fb96'}
out = dict(task='C08', outcome='accepted', selected_bytes=total, instruction_count=count,
    all_C07_raw_instruction_records_match_ROM=True, undecoded_bytes=0, controls=controls,
    checks=dict(tail_forward_branches=len(branches), tail_jal_calls=12, tail_resolved_pairs=5,
                compressed_control_edges=3, exit_clear_before_s1_alias_change=True),
    limits=['Only C07 three windows; callees opaque; normal return is conditional.',
            'No whole-function boundary, loop, timer, callback scheduling or runtime verification.',
            'No new open-source attribution or exclusion.'])
(HERE/'review-evidence.json').write_text(json.dumps(out, ensure_ascii=False, indent=2)+'\n', encoding='utf-8')
print(json.dumps({k:v for k,v in out.items() if k not in ('controls','limits')}))
