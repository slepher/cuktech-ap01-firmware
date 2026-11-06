"""Compiler-free checks for pinned ROM profile and patch boundaries."""
from copy import deepcopy
from pathlib import Path
import importlib.util
import json
import struct
import sys
import zlib
import argparse

from rom_target import ROOT, load_target, validate_original, validate_profile

spec = importlib.util.spec_from_file_location('packager', Path(__file__).with_name('build-native-app-rom-0041.py'))
packager = importlib.util.module_from_spec(spec)
spec.loader.exec_module(packager)


def rejected(operation):
    try:
        operation()
    except (ValueError, FileNotFoundError):
        return
    raise AssertionError('Invalid profile or ROM accepted')


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--target', choices=('0041', '0055'), default='0041')
    target = parser.parse_args().target
    profile = load_target(target)
    original = (ROOT / profile['original']['path']).read_bytes()
    validate_original(profile, original)
    assert profile['target'] == target
    rejected(lambda: load_target('unknown'))
    for mutate in (
        lambda p: p.update(status='candidate'),
        lambda p: p.update(payload_offset='0x1000'),
        lambda p: p['original'].update(sha256='0' * 64),
        lambda p: p['ui_hook'].update(original_hex='00'),
        lambda p: p['timer_delete'].update(nonnull_tail='0xa008ae62'),
        lambda p: p['menu_hooks'][0].update(symbol='ap01MenuList0041'),
        lambda p: p['unsigned_ota'].update(offset=p['ui_hook']['offset']),
    ):
        bad = deepcopy(profile)
        mutate(bad)
        rejected(lambda: validate_profile(bad, target))
    damaged = bytearray(original)
    damaged[0x1001] ^= 1
    rejected(lambda: validate_original(profile, damaged))

    # Exercise all patch paths, then prove no unlisted original byte changed.
    payload = bytearray(512)
    payload[:8] = b'AP01APP1'
    payload[192:200] = b'AP01MNU1'
    struct.pack_into('<I', payload, 200, 4)
    entry = profile['mapping_base'] + profile['payload_offset'] + 256
    changed = [(profile['ui_hook']['offset'], 8), (profile['timer_delete']['offset'], 8),
               (profile['unsigned_ota']['offset'], 2)]
    for index, record in enumerate(profile['menu_hooks']):
        span = len(bytes.fromhex(record['original_hex']))
        struct.pack_into('<3I', payload, 204 + index * 12, record['offset'], entry + index * 2, span)
        changed.append((record['offset'], span))
    image = packager.assemble(original, bytes(payload), entry, True, entry, target)
    assert len(image) <= 0x700000
    assert struct.unpack_from('>I', image, len(image)-8)[0] == len(image)
    assert struct.unpack_from('<I', image, len(image)-4)[0] == zlib.crc32(image[:-4], 0xffffffff) ^ 0xffffffff
    preserved = bytearray(image[:len(original)-40])
    for offset, span in changed:
        preserved[offset:offset+span] = original[offset:offset+span]
    assert preserved == original[:-40]
    assert packager.assemble(original, bytes(payload), entry, True, entry, target) == image
    assert image.count(b'0x5245434f56455259544147') == 2
    rejected(lambda: packager.assemble(original, bytes(payload), entry - 256, True, entry, target))
    rejected(lambda: packager.assemble(original, bytes(payload), entry, True, entry,
                                     '0055' if target == '0041' else '0041'))
    print(json.dumps({'passed': True, 'target': target, 'patch_paths': 7,
                      'unlisted_original_bytes_preserved': True, 'device_accessed': False}))


if __name__ == '__main__':
    main()
