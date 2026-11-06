"""Check reviewed address coverage, call targets, ABI operands and stock fonts."""
from pathlib import Path
import json
import re
import struct
from rom_target import ROOT, load_target, validate_original


def word(data, at):
    return struct.unpack_from('<I', data, at)[0]


def jal_target(data, at, base):
    value = word(data, at)
    assert value & 0x7f == 0x6f
    delta = ((value >> 31) << 20) | (((value >> 12) & 255) << 12)
    delta |= ((value >> 20) & 1) << 11 | ((value >> 21) & 1023) << 1
    if delta & (1 << 20):
        delta -= 1 << 21
    return base + at + delta


def main():
    profiles = {v: load_target(v) for v in ('0041', '0055')}
    roms = {v: (ROOT / p['original']['path']).read_bytes() for v, p in profiles.items()}
    for v, p in profiles.items():
        validate_original(p, roms[v])
    base = profiles['0055']['mapping_base']
    header = (ROOT / 'tooling/firmware-modules/native_rom_addresses_0055.h').read_text()
    pairs = re.findall(r'^#define AP01_ROM_0055_(0x[0-9a-f]+) (0x[0-9a-f]+)$', header, re.M)
    assert len(pairs) == len(dict(pairs)), 'Duplicate address definition'
    locations = {int(a, 16): int(b, 16) for a, b in pairs}
    used = set()
    for path in (ROOT / 'tooling/firmware-modules').iterdir():
        if path.suffix in ('.cpp', '.inc'):
            used.update(int(x, 16) for x in re.findall(
                r'AP01_ROM_(?:ADDR|STRING)\((0x[0-9a-f]+)\)', path.read_text(encoding='utf-8')))
    assert used <= locations.keys(), 'Unmapped production ROM address'
    for old, new in locations.items():
        assert (0xa0000000 <= old < base + len(roms['0041'])) or 0x62fc0000 <= old < 0x62fd0000
        assert (0xa0000000 <= new < base + len(roms['0055'])) or 0x62fc0000 <= new < 0x62fd0000

    checks = json.loads((ROOT / 'tooling/rom-targets/0055-abi-checks.json').read_text())['checks']
    for item in checks:
        expected = bytes.fromhex(item['instruction_hex'])
        for v, key in (('0041', 'old'), ('0055', 'new')):
            offset = int(item[key], 16) - base
            assert roms[v][offset:offset + len(expected)] == expected, item['contract']

    new = roms['0055']
    profile = profiles['0055']
    at = profile['ui_hook']['offset']
    upper, lower = word(new, at), word(new, at + 4)
    assert upper & 0xfff == 0x97 and lower & 0xfffff == 0x80e7
    low = lower >> 20
    if low & 0x800:
        low -= 0x1000
    assert (base + at + (upper & 0xfffff000) + low) & 0xffffffff == locations[0xa01ad654]
    for item in profile['menu_hooks'][:3]:
        assert jal_target(new, item['offset'], base) == locations[0xa01ad654]
    assert jal_target(new, profile['menu_hooks'][3]['offset'], base) == locations[0xa01a2c02]
    # The reviewed stolen instruction changed in 0055; the target-specific
    # stubs must restore ADDI a1,s1,0x6be rather than the old filter setup.
    assert all(new[x['offset'] + 4:x['offset'] + 8] == bytes.fromhex('9385e46b')
               for x in profile['menu_hooks'][:2])
    assert locations[0xa008ae60] == profile['timer_delete']['nonnull_tail']
    # Matching native operation tables and Font36 wrappers independently tie
    # data locations to translated callbacks rather than prologue similarity.
    old_at, new_at = 0xa01bf590 - base, locations[0xa01bf590] - base
    assert roms['0041'][old_at:old_at + 96] == new[new_at:new_at + 96]
    for old in (0xa02549f4, 0xa025488c, 0xa02548d4, 0xa055fb7c):
        old_words = struct.unpack_from('<9I', roms['0041'], old - base)
        new_words = struct.unpack_from('<9I', new, locations[old] - base)
        assert new_words[:2] == tuple(locations[x] for x in old_words[:2])
        assert old_words[3:6] == new_words[3:6]
    print(json.dumps(dict(passed=True, address_locations=len(locations), used_locations=len(used),
                          exact_abi_instruction_checks=len(checks), device_accessed=False)))


if __name__ == '__main__':
    main()
