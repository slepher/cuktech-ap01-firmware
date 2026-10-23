"""Static, bounded A15 ROM verification; never loads or executes firmware."""
import json
from pathlib import Path

import capstone

ROOT = Path(__file__).resolve().parent
MAIN = Path('D:/Documents/PlatformIO/Projects/cuktech-ap01-firmware')
ROM = MAIN / 'roms/0041/ap01-1.0.2_0041.bin'
BASE = 0xa0000000
rom = ROM.read_bytes()
md = capstone.Cs(capstone.CS_ARCH_RISCV,
                 capstone.CS_MODE_RISCV32 | capstone.CS_MODE_RISCVC)

# Each end is exclusive. Only normal registration prerequisites are decoded;
# failure arms and the remainder of the page constructor are outside A15.
spans = [
    ('registration-normal-prerequisites', 0xa00a7d42, 0xa00a7d5c),
    ('context-allocation', 0xa00a7d70, 0xa00a7d7c),
    ('range-widget-store', 0xa00a7f3e, 0xa00a7f5a),
    ('registration-and-context-link', 0xa00a7fb8, 0xa00a7fe2),
    ('callback', 0xa00ab6b0, 0xa00ab754),
    ('first-consumer', 0xa008ce90, 0xa008cf0a),
    ('dispatch-abi', 0xa00b3c14, 0xa00b3c26),
]
windows = []
instructions = {}
for name, start, end in spans:
    offset = start - BASE + 0x1000
    data = rom[offset:offset + end - start]
    decoded = list(md.disasm(data, start))
    assert sum(i.size for i in decoded) == len(data), name
    rows = []
    for i in decoded:
        assert bytes(i.bytes) == rom[i.address - BASE + 0x1000:
                                    i.address - BASE + 0x1000 + i.size]
        row = {'address': hex(i.address), 'bytes': i.bytes.hex(),
               'mnemonic': i.mnemonic, 'operands': i.op_str}
        instructions[i.address] = row
        rows.append(row)
    windows.append({'name': name, 'start': hex(start), 'end_exclusive': hex(end),
                    'file_offset': offset, 'hex': data.hex(), 'instructions': rows})

# Independent bit-field checks of all 32-bit weather reads and consumer field
# accesses, rather than accepting pseudocode types or Capstone text as the ABI.
checks = []
def field(addr, opcode, funct3, reg, base, imm):
    w = int.from_bytes(rom[addr-BASE+0x1000:addr-BASE+0x1004], 'little')
    assert w & 0x7f == opcode
    assert (w >> 12) & 7 == funct3
    assert (w >> 15) & 31 == base
    if opcode == 3:
        assert (w >> 7) & 31 == reg
        value = w >> 20
    else:
        assert (w >> 20) & 31 == reg
        value = ((w >> 25) << 5) | ((w >> 7) & 31)
    value = value - 4096 if value & 0x800 else value
    assert value == imm
    checks.append({'kind': 'raw-field', 'address': hex(addr), 'opcode': opcode,
                   'funct3': funct3, 'register': reg, 'base': base, 'offset': imm})

for args in [
    (0xa00ab6c2,3,1,12,10,8), (0xa00ab6c6,3,1,11,10,10),
    (0xa00ab6cc,3,1,18,10,12), (0xa00ab6d0,3,2,19,10,28),
    (0xa00a7f56,35,2,10,18,24),
    (0xa00a7fca,35,2,18,25,4), (0xa00a7fce,35,2,24,25,0),
    (0xa00a7fde,35,2,25,9,16),
]:
    field(*args)

def jal(addr, expected):
    w = int.from_bytes(rom[addr-BASE+0x1000:addr-BASE+0x1004], 'little')
    assert w & 0x7f == 0x6f and (w >> 7) & 31 == 1
    value = ((w >> 31) << 20) | (((w >> 12) & 255) << 12)
    value |= ((w >> 20) & 1) << 11 | ((w >> 21) & 1023) << 1
    if value & 0x100000: value -= 0x200000
    assert addr + value == expected
    checks.append({'kind':'raw-jal', 'address':hex(addr), 'target':hex(expected)})

for a, b in [(0xa00a7fc2,0xa00b3a68), (0xa00ab6e2,0xa008ce90),
             (0xa00ab6ea,0xa008ce16), (0xa00ab6fc,0xa019d0ae),
             (0xa00ab70c,0xa0091ee4), (0xa00ab714,0xa0198946),
             (0xa008cefc,0xa008ccd2)]:
    jal(a,b)

# RV32C c.lw/c.sw fields at all pointer/range accesses in the bounded path.
def compressed(addr, store, reg, base, offset):
    w = int.from_bytes(rom[addr-BASE+0x1000:addr-BASE+0x1002], 'little')
    assert w & 3 == 0 and w >> 13 == (6 if store else 2)
    assert ((w >> 2) & 7)+8 == reg and ((w >> 7) & 7)+8 == base
    value = (((w >> 5) & 1) << 6) | (((w >> 10) & 7) << 3) | (((w >> 6) & 1) << 2)
    assert value == offset
    checks.append({'kind':'raw-compressed-field','address':hex(addr),
                   'store':store,'register':reg,'base':base,'offset':offset})

for a,st,r,b,o in [
    (0xa00ab6c0,False,15,11,16), (0xa00ab6ca,False,9,15,4),
    (0xa00ab6e0,False,10,9,24),
    (0xa008cedc,False,15,10,68), (0xa008cee2,False,15,10,72),
    (0xa008cee8,False,15,10,64), (0xa008ceea,True,11,10,68),
    (0xa008ceec,True,12,10,72), (0xa008cef2,True,11,10,64),
    (0xa008cef4,False,15,10,64), (0xa008cefa,True,12,10,64),
    (0xa00b3c14,False,15,9,0), (0xa00b3c18,False,11,9,4),
]:
    compressed(a,st,r,b,o)

# Key short ABI instructions and signed comparison encodings.
expected = {
    0xa00a7fbc:'a685', 0xa00a7fb8:'37b50aa0', 0xa00a7fbe:'1305056b',
    0xa00ab6b0:'cdc1', 0xa00ab6d4:'63c6c500', 0xa00ab6d8:'1306c003',
    0xa00ab6dc:'930540fc', 0xa008cede:'6395b700', 0xa008cee4:'638ec700',
    0xa008ceee:'63d3b700', 0xa008cef6:'6353f600',
    0xa00b3c1c:'4e85', 0xa00b3c1e:'8297',
}
for addr, raw in expected.items():
    assert instructions[addr]['bytes'] == raw
    checks.append({'kind':'raw-encoding','address':hex(addr),'bytes':raw})

# Reuse one retained dossier, retaining only the selected constructor slices.
source = MAIN / 'evidence/rea-0041-20261017/evidence/whole-rom-private-20261023-064.json'
record = json.loads(source.read_text(encoding='utf-8'))['structuredContent']
assert record['parameters']['procedure'] == '0xa00a7766'
assert record['subject']['digest']['sha256'] == '972db4c136c7ed9e24a83c07c1a7fd62040ca018b08ca285216d26b1fee3c6b9'
retained_asm = [line for line in record['normalized_result']['assembly']
                if any(a <= int(line.split(':')[0],16) < b
                       for _,a,b in spans[:4])]
assert len(retained_asm) == sum(len(w['instructions']) for w in windows[:4])
retained = {'source': str(source), 'evidence_id': record['evidence_id'],
            'parameters': record['parameters'], 'assembly_selected': retained_asm,
            'scope': 'Selected registration slices only; constructor not fully recovered.'}

def write(name, obj):
    (ROOT/name).write_text(json.dumps(obj,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')

write('instruction-windows.json', {'rom':str(ROM),'mapping':'file_offset = VA - 0xa0000000 + 0x1000',
                                  'decoder':f'Capstone {capstone.__version__} RV32C','windows':windows})
write('retained-registration.json', retained)
strings = []
for addr, expected_text in [
    (0xa0268a90, 'lv_power_ui/lv_ui_scr_saver.c'),
    (0xa037bb30, 'lv_ui_ssr_tim2_update_wx_data_cb'),
    (0xa037a5b0, 'lv_ui_ssr_tim2_update_wx_data_cb: update ui ssr tim2 wx data finished\n'),
    (0xa026ab14, 'lv_win_ui_scr_saver_dtl_create'),
    (0xa0263324, '/home/jiangmingmin/ap01/AP01_BL618/apps/graphics/lvgl/lvgl/src/widgets/arc/lv_arc.c'),
    (0xa0263870, 'lv_arc_set_range'),
]:
    offset = addr - BASE + 0x1000
    observed = rom[offset:rom.index(0, offset)].decode('ascii')
    assert observed == expected_text
    strings.append({'address':hex(addr),'file_offset':offset,'text':observed})
write('strings.json', strings)
write('review-index.json', {'static_only':True,'complete_module':False,
      'windows':len(windows), 'bytes':sum((b-a) for _,a,b in spans),
      'instructions':sum(len(w['instructions']) for w in windows),
      'raw_checks':checks, 'retained_instruction_count':len(retained_asm),
      'strings':len(strings), 'result':'passed', 'limits':['No firmware execution or device/network connection.',
       'No full constructor recovery, lifecycle proof, or all-subscriber enumeration.',
       'No new hash or copied inventory; existing dossier identity reused.']})
print(json.dumps({'result':'passed','windows':len(windows),
                  'bytes':sum(b-a for _,a,b in spans),'instructions':len(instructions),
                  'raw_checks':len(checks),'retained_instructions':len(retained_asm)}))
