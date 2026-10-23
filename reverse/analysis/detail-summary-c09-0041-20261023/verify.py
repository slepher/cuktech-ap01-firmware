"""C09: static ROM decode and evidence checks only; never execute firmware."""
import json
import struct
import sys
from pathlib import Path
from capstone import Cs, CS_ARCH_RISCV, CS_MODE_RISCV32, CS_MODE_RISCVC

HERE = Path(__file__).resolve().parent
TREE = HERE.parents[2]
SOURCE = Path(sys.argv[1]).resolve()
ROM_PATH = SOURCE / 'roms/0041/ap01-1.0.2_0041.bin'
rom = ROM_PATH.read_bytes()
BASE = 0x9ffff000
md = Cs(CS_ARCH_RISCV, CS_MODE_RISCV32 | CS_MODE_RISCVC)
specs = [('summary', 0xa00f3844, 0xa00f388c),
         ('mode_getter_including_null_tail', 0xa00a5c50, 0xa00a5c94),
         ('child_lookup', 0xa00dcee4, 0xa00dcf52),
         ('caller_lookup', 0xa00f3a16, 0xa00f3a40),
         ('caller_summary_call', 0xa00f3aee, 0xa00f3b12)]
windows, decoded, vendor = [], {}, []
for name, start, end in specs:
    pc, insns = start, []
    while pc < end:
        off = pc - BASE
        size = 4 if rom[off] & 3 == 3 else 2
        raw = rom[off:off+size]
        ins = next(md.disasm(raw, pc), None)
        if ins:
            assert ins.size == size
            asm = ins.mnemonic + ' ' + ins.op_str
            decoded[pc] = ins
        else:
            word = int.from_bytes(raw, 'little')
            fields = dict(op=word & 127, rd=(word >> 7) & 31,
                          funct3=(word >> 12) & 7, rs1=(word >> 15) & 31,
                          rs2=(word >> 20) & 31, shift=(word >> 25) & 3,
                          funct5=word >> 27)
            expected = {0xa00f3870: (12, 15, 9), 0xa00dcf48: (10, 15, 11)}
            assert (fields['op'], fields['funct3'], fields['funct5'], fields['shift']) == (11, 4, 8, 2)
            assert (fields['rd'], fields['rs1'], fields['rs2']) == expected[pc]
            asm = 'th.lrw (existing local model), ' + str(fields)
            vendor.append(dict(address=hex(pc), hex=raw.hex(), fields=fields))
        insns.append(dict(address=hex(pc), hex=raw.hex(), assembly=asm))
        pc += size
    assert pc == end
    windows.append(dict(name=name, start=hex(start), end_exclusive=hex(end),
                        file_offset=start-BASE, instructions=insns))

def target(pc):
    return pc + int(decoded[pc].op_str.split(',')[-1].strip(), 0)

targets = {0xa00f3852:0xa00a5c50, 0xa00f385e:0xa00dcee4,
           0xa00f3864:0xa00dcee4, 0xa00f387c:0xa0091ee4,
           0xa00a5c58:0xa00a5c60, 0xa00a5c86:0xa008b51a,
           0xa00dcee4:0xa00dcf30, 0xa00dcf32:0xa00dcf50,
           0xa00dcf38:0xa00dcf42, 0xa00dcf3e:0xa00dcf4e,
           0xa00dcf42:0xa00dcf4e, 0xa00f3a2e:0xa00a72ae,
           0xa00f3a32:0xa00f3a40, 0xa00f3a38:0xa00f3a40,
           0xa00f3a3e:0xa00f3aee, 0xa00f3b0c:0xa00f3844,
           0xa00f3b10:0xa00f3a5c}
for pc, dest in targets.items():
    assert target(pc) == dest, (hex(pc), hex(target(pc)), hex(dest))
critical = {0xa00f3850:'s2, a0',0xa00f3856:'s1, a0',
            0xa00f3858:'a0, 0(s2)',0xa00f385c:'a1, 0',0xa00f3862:'a1, 2',
            0xa00a5c54:'a5, 0x2cc(a5)',0xa00a5c5a:'a0, 8(a5)',
            0xa00a5c8e:'a0, 0',0xa00dcf30:'a0, 8(a0)',
            0xa00dcf34:'a5, 0x30(a0)',0xa00dcf46:'a5, 0(a0)',
            0xa00dcf4e:'a0, 0',0xa00f3a1e:'a1, 0xd',
            0xa00f3a26:'zero, -0x34(s0)',0xa00f3b08:'a0, -0x34(s0)'}
for pc, operands in critical.items():
    assert decoded[pc].op_str == operands, (hex(pc), decoded[pc].op_str)
assert decoded[0xa00f388a].mnemonic == 'c.jr'

# Existing retained windows must agree byte-for-byte, without new hash inventories.
previous = json.loads((TREE/'reverse/analysis/ui-total-consumers-0041-20261023/instruction-windows.json').read_text(encoding='utf-8'))
matches = 0
for w in previous['windows']:
    if w['name'] in ('mode_getter_with_null_tail', 'power_detail_total_cb'):
        a, b = int(w['start'],16), int(w['end_exclusive'],16)
        assert bytes.fromhex(w['hex']) == rom[a-BASE:b-BASE]
        matches += 1
assert matches == 2
inventory = json.loads((TREE/'reverse/analysis/whole-rom-coverage-0041-20261023-round1.json').read_text(encoding='utf-8'))
f = next(f for f in inventory['functions'] if f['address']=='0xa00f3844')
assert f['extent']['body']['ranges'] == [{'start':'0xa00f3844','end':'0xa00f388b'}]
model = SOURCE/'evidence/rea-0041-20261017/ghidra/Ghidra/Processors/RISCV/data/languages/ap01thead2.sinc'
lines = model.read_text(encoding='utf-8').splitlines()
start = next(i for i,line in enumerate(lines) if line.startswith(':th.lrw '))
end = next(i for i in range(start+1,len(lines)) if lines[i]=='}')+1
excerpt = '\n'.join(lines[start:end])
assert 'rs2 << thshift' in excerpt and '*[ram]:4 ea' in excerpt
strings = []
table = struct.unpack_from('<4I', rom, 0xa01c473c-BASE)
for a in [0xa06136bc, *table]:
    off = a-BASE
    raw = rom[off:rom.index(b'\0',off)+1]
    strings.append(dict(address=hex(a), file_offset=off, hex=raw.hex(), text=raw[:-1].decode('utf-8')))
assert strings[0]['text'] == '%s'
labels = json.loads((TREE/'reverse/analysis/ui-total-consumers-0041-20261023/mode-labels.json').read_text(encoding='utf-8'))['labels']
assert [s['text'] for s in strings[1:]] == [s['text'] for s in labels]
assert [s['address'] for s in strings[1:]] == [s['address'] for s in labels]
checks = dict(result='passed', windows=len(windows), ordinary_instructions=len(decoded),
              vendor_words=len(vendor), direct_targets=len(targets), critical_operands=len(critical),
              prior_windows_byte_equal=matches, summary_boundary_matches_inventory=True)
out = dict(task='C09', rom_path=str(ROM_PATH), base=hex(BASE), checks=checks,
           windows=windows, vendor_words=vendor, mode_table=dict(address='0xa01c473c', pointers=[hex(a) for a in table]),
           strings=strings, model_excerpt=dict(path=str(model), line=start+1, text=excerpt),
           inventory_entry=f,
           limits=['Static decode only; no firmware or helper execution.',
                   'Vendor indexed-load semantics use retained local model, not fresh upstream certification.',
                   'Text formatter implementation and complete object lifecycle remain outside scope.'])
(HERE/'instruction-evidence.json').write_text(json.dumps(out,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
print(json.dumps(checks))
