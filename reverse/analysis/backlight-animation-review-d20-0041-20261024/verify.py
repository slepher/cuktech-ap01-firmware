"""D20 independent static review; no target/model execution or writer search."""
import json
from pathlib import Path
import capstone

HERE = Path(__file__).resolve().parent
REVERSE = HERE.parents[1]
MAIN = Path('D:/Documents/PlatformIO/Projects/cuktech-ap01-firmware')
BASE = 0x9ffff000
rom = (MAIN / 'roms/0041/ap01-1.0.2_0041.bin').read_bytes()
windows = json.loads((REVERSE / 'analysis/backlight-animation-d19-0041-20261024/instruction-windows.json').read_text())
for w in windows:
    a, b = int(w['start'], 16), int(w['end_exclusive'], 16)
    assert rom[a-BASE:b-BASE].hex() == w['hex']

def u32(pc):
    return int.from_bytes(rom[pc-BASE:pc-BASE+4], 'little')

def signed(value, width):
    return value - (1 << width) if value & (1 << (width-1)) else value

def jal(pc):
    w = u32(pc)
    assert w & 127 == 0x6f
    imm = ((w >> 31) << 20) | (((w >> 12) & 255) << 12) | (((w >> 20) & 1) << 11) | (((w >> 21) & 1023) << 1)
    return (pc + signed(imm, 21)) & 0xffffffff

def auipc_call(pc):
    upper, lower = u32(pc), u32(pc+4)
    assert upper & 127 == 0x17 and lower & 127 == 0x67
    assert (upper >> 7) & 31 == (lower >> 15) & 31 == 1
    return (pc + (upper & 0xfffff000) + signed(lower >> 20, 12)) & 0xfffffffe

# Descriptor origin is s0-0x70. Independently decode each 32-bit store offset.
slots = {}
for pc, offset, source in [(0xa00f443a, 0x30, 15), (0xa00f4446, 0x20, 15),
                           (0xa00f4452, 4, 15), (0xa00f445a, 0, 18),
                           (0xa00f445e, 0x28, 15), (0xa00f446c, 0x2c, 15),
                           (0xa00f4470, 0x24, 0), (0xa00f4474, 0x44, 18)]:
    w = u32(pc)
    assert w & 127 == 0x23 and (w >> 12) & 7 == 2
    assert (w >> 15) & 31 == 8 and (w >> 20) & 31 == source
    displacement = signed(((w >> 25) << 5) | ((w >> 7) & 31), 12)
    assert displacement + 0x70 == offset
    slots[hex(pc)] = hex(offset)
assert u32(0xa00f4436) >> 20 == 2000
assert rom[0xa00f4462-BASE:0xa00f4464-BASE].hex() == '7d59'  # s2=-1
assert u32(0xa00f4426) == 0x0104a903  # target = *(s1+0x10)
assert u32(0xa00f441e) >> 20 == 96
assert u32(0xa008bfe6) >> 20 == 96

calls = {0xa00f4432: 0xa008df3c, 0xa008df4c: 0xa0080d8e,
         0xa0080d9a: 0xa0024906, 0xa00f4478: 0xa008bf6e,
         0xa00f4390: 0xa008a73a, 0xa00f43c8: 0xa018fb3c,
         0xa00feb94: 0xa008ae58, 0xa00febaa: 0xa0089184,
         0xa00febb6: 0xa01b2eb4, 0xa00febc0: 0xa018fb3c,
         0xa008ac2a: 0xa008ab8a}
for pc, dest in calls.items():
    assert jal(pc) == dest
assert auipc_call(0xa01b2ef8) == 0xa008ac06

cs = capstone.Cs(capstone.CS_ARCH_RISCV, capstone.CS_MODE_RISCV32 | capstone.CS_MODE_RISCVC)
expected = {0xa00f4462: 'c.li s2, -1', 0xa008c0a2: 'c.li s3, -1',
            0xa008c232: 'beq a4, s3, 0xc', 0xa008c236: 'c.addi a4, -1',
            0xa008c23a: 'c.lw a4, 0x44(s1)', 0xa008c24c: 'c.sw a4, 0x34(s1)',
            0xa008c044: 'c.lw a5, 0x20(s1)', 0xa008c052: 'c.lw a0, 0(s1)',
            0xa008c1f4: 'c.lw a5, 0x10(s1)', 0xa008c1fc: 'c.lw a5, 0x14(s1)',
            0xa008ac20: 'c.lw a5, 0x14(s1)', 0xa008ac26: 'c.jalr a5',
            0xa00feb8c: 'bltu a5, a0, 0xc', 0xa00feb98: 'sw zero, 0x84(s3)',
            0xa00feb9c: 'lw s2, 0x10(s3)', 0xa00febbe: 'c.li a1, 0',
            0xa00f43c4: 'andi a1, a1, 0xff'}
for pc, text in expected.items():
    i = next(cs.disasm(rom[pc-BASE:pc-BASE+4], pc, count=1))
    assert i.mnemonic + ' ' + i.op_str == text

settings = json.loads((MAIN / 'reverse/rehost/settings-0041-round2b.json').read_text(encoding='utf-8'))['records'][10]
assert settings['evidence_id'] == 'ev_d2c060238142516e1df7a388e5984d96623578a75366a96c1472e9ed8c8df9fb'
assembly = settings['normalized_result']['assembly']
assert '0xa00febaa: jal ra, 0xa0089184' in assembly
assert '0xa00febb6: jal ra, 0xa01b2eb4' in assembly
assert rom[0xa00891b2-BASE:0xa00891b6-BASE].hex() == '8bc7e740'
result = {'passed': True, 'prior_windows_match_original': len(windows),
          'descriptor_store_offsets': slots, 'independent_jal_targets': len(calls),
          'independent_auipc_call': 'a01b2ef8 -> a008ac06',
          'sparse_instruction_checks': len(expected),
          'settings_record': 'settings-0041-round2b.json records[10]',
          'accepted': ['96B descriptor', 'duration 2000, infinite repeat sentinel -1',
                       'target=*(ctx+0x10), exec=a00f43bc, path=a00f4378',
                       'completed/deleted slots zero', 'timer clear then animation delete then target zero'],
          'unknown_vendor_word': 'a00891b2:8bc7e740 (unchanged, traversal not certified)',
          'unknown': ['all page DELETE/context release routes', 'target/context complete owners', 'exact upstream typedef/property names'],
          'new_functionality': 0, 'shared_rea_target': False}
(HERE / 'static-review.json').write_text(json.dumps(result, ensure_ascii=False, indent=2)+'\n', encoding='utf-8')
print(json.dumps({'passed': True, 'windows_compared': len(windows), 'calls_checked': len(calls)+1, 'sparse_checks': len(expected)}))
