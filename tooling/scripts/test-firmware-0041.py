"""Check a real packaged 0041 candidate without a compiler or device."""
from pathlib import Path
import argparse
import hashlib
import importlib.util
import json
import struct
import zlib

ROOT = Path(__file__).resolve().parents[2]
spec = importlib.util.spec_from_file_location('packager', Path(__file__).with_name('build-native-app-rom-0041.py'))
packager = importlib.util.module_from_spec(spec)
spec.loader.exec_module(packager)


def check(manifest_path):
    manifest = json.loads(manifest_path.read_text(encoding='utf-8'))
    image = Path(manifest['image']['path']).read_bytes()
    packager.validate_candidate(image, manifest_path)
    assert image[:0x1000] == Path(manifest['original']['path']).read_bytes()[:0x1000]
    assert len(image) <= 0x700000
    assert struct.unpack_from('>I', image, len(image)-8)[0] == len(image)
    assert struct.unpack_from('<I', image, len(image)-4)[0] == zlib.crc32(image[:-4], 0xffffffff) ^ 0xffffffff
    assert image.count(b'0x5245434f56455259544147') == 2
    assert len(manifest['settings_menu_hooks']) == 4
    assert manifest['timer_delete_guard']['null_is_noop']
    assert not manifest['flashable'] and not manifest['hardware_verified']
    audit_path = Path(manifest['audit']['path'])
    audit = json.loads(audit_path.read_text(encoding='utf-8'))
    link = json.loads(Path(manifest['link']['path']).read_text(encoding='utf-8'))
    assert audit['passed'] and link['linked'] and not link['undefined_imports']
    assert hashlib.sha256(audit_path.read_bytes()).hexdigest() == link['audit_sha256']
    for item in audit['objects']:
        assert hashlib.sha256(Path(item['source']).read_bytes()).hexdigest() == item['source_sha256']
    for item in audit['input_headers']:
        assert hashlib.sha256(Path(item['path']).read_bytes()).hexdigest() == item['sha256']
    if manifest['runtime'] == 'platform':
        assert manifest['applications'] == [] and manifest['platform_abi']['version'] == 2
        assert all(Path(item['source']).resolve().is_relative_to(ROOT) for item in audit['objects'])
        assert all(Path(item['path']).resolve().is_relative_to(ROOT) for item in audit['input_headers'])
    else:
        assert manifest['runtime'] == 'application' and manifest['screen_host']['abi'] == 1
    # A changed stock byte must be rejected, even with an updated recovery CRC.
    corrupt = bytearray(image)
    corrupt[0x1001] ^= 1
    struct.pack_into('<I', corrupt, len(corrupt)-4, zlib.crc32(corrupt[:-4], 0xffffffff) ^ 0xffffffff)
    try:
        packager.validate_candidate(bytes(corrupt), manifest_path)
    except ValueError:
        pass
    else:
        raise AssertionError('out-of-range mutation accepted')
    print(json.dumps({'passed': True, 'runtime': manifest['runtime'], 'bytes': len(image),
                      'sha256': packager.sha(image), 'device_accessed': False}))


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--manifest', type=Path, required=True)
    check(parser.parse_args().manifest.resolve())
