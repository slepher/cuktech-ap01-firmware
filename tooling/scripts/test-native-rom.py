"""Check current ROM identity, address coverage and reviewed ABI instructions offline."""
import json
import re
from rom_target import ROOT, load_target, validate_original


def main():
    profile = load_target()
    rom = (ROOT / profile['original']['path']).read_bytes()
    validate_original(profile, rom)
    modules = ROOT / 'tooling/firmware-modules'
    pairs = re.findall(r'^#define AP01_ROM_ADDRESS_(0x[0-9a-f]+) (0x[0-9a-f]+)$',
                       (modules / 'native_rom_map.h').read_text(), re.M)
    assert len(pairs) == len(dict(pairs)), 'Duplicate address mapping'
    addresses = {int(old, 16): int(current, 16) for old, current in pairs}
    used = set()
    for path in modules.iterdir():
        if path.suffix in ('.cpp', '.inc') and not path.name.startswith('test_'):
            used.update(int(value, 16) for value in re.findall(
                r'AP01_ROM_(?:ADDR|STRING)\((0x[0-9a-f]+)\)', path.read_text()))
    assert used <= addresses.keys(), 'Missing production address mapping'
    base = profile['mapping_base']
    for address in addresses.values():
        assert base + 0x1000 <= address < base + len(rom) or 0x62fc0000 <= address < 0x62fd0000
    checks = json.loads((ROOT / 'tooling/rom-targets/native-abi-checks.json').read_text())['checks']
    for item in checks:
        offset = int(item['new'], 16) - base
        expected = bytes.fromhex(item['instruction_hex'])
        assert rom[offset:offset + len(expected)] == expected, item['contract']
    print(json.dumps(dict(passed=True, target=profile['target'], addresses=len(addresses),
                          used=len(used), abi_instruction_checks=len(checks), device_accessed=False)))


if __name__ == '__main__':
    main()
