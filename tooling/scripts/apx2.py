"""Offline APX2 package writer. Input is a normalized linked image, never arbitrary ELF.

The target loader accepts only BASE32 records; ELF handling belongs to the linker.
Use test-apx2.py to cross-check these bytes with the firmware validator.
"""
from pathlib import Path
import argparse
import hashlib
import json
import struct

HEADER = 256


def package(image, config):
    required = {'app_id', 'version', 'text_bytes', 'ro_offset', 'ro_bytes', 'data_offset',
                'data_bytes', 'bss_bytes', 'heap_bytes', 'stack_bytes', 'entries',
                'data_read_min', 'data_read_max', 'data_write_version', 'required_services', 'fixups'}
    if set(config) - {'abi_major'} != required:
        raise ValueError('Exact APX2 manifest fields required: ' + ', '.join(sorted(required)))
    abi = config.get('abi_major', 2)
    if type(abi) is not int or abi not in (2, 3):
        raise ValueError('Supported ABI majors: 2 (legacy), 3 (direct C)')
    if len(config['entries']) != (5 if abi == 2 else 3):
        raise ValueError('ABI 2 requires five entries; ABI 3 requires start/event/health')
    integers = [config[k] for k in required - {'app_id','version','entries','fixups','required_services'}]
    integers += config['entries']
    for fix in config['fixups']:
        if len(fix) != 2: raise ValueError('Fixups must be [destination, target] pairs')
        integers += fix
    if any(type(n) is not int or not 0 <= n <= 0xffffffff for n in integers):
        raise ValueError('Fields must be uint32')
    services = config['required_services']
    if type(services) is not int or not 0 <= services < 2**64:
        raise ValueError('required_services must be uint64')
    text = config['text_bytes']
    ro, ro_size = config['ro_offset'], config['ro_bytes']
    data, data_size = config['data_offset'], config['data_bytes']
    end = len(image) + config['bss_bytes']
    if (not text or text > ro or ro % 16 or ro + ro_size > data or data % 16
            or data + data_size != len(image) or len(image) % 4 or end > 0xffffffff):
        raise ValueError('Invalid image section layout')
    if any(image[text:ro]) or any(image[ro + ro_size:data]):
        raise ValueError('Image alignment padding must be zero')
    if any(at % 2 or at + 2 > text for at in config['entries']):
        raise ValueError('Lifecycle entries must be aligned inside text')
    if config['stack_bytes'] < 256 or config['stack_bytes'] % 16:
        raise ValueError('Stack must be at least 256 bytes and aligned to 16')
    if not config['data_read_min'] <= config['data_write_version'] <= config['data_read_max']:
        raise ValueError('App must read its own data version')
    h = bytearray(HEADER)
    h[:4] = b'APX2'
    fixes = config['fixups']
    for at, target in fixes:
        if not (ro <= at and at + 4 <= ro + ro_size or data <= at and at + 4 <= len(image)):
            raise ValueError('Fixup destination must be in rodata or data')
        if not (target < text or ro <= target < ro + ro_size or data <= target < end):
            raise ValueError('Fixup target must be in a defined section')
        if at % 4 or at + 4 > len(image) or struct.unpack_from('<I', image, at)[0] != target:
            raise ValueError('Image must contain the normalized pointer at each fixup')
    if [x[0] for x in fixes] != sorted(set(x[0] for x in fixes)):
        raise ValueError('Fixup destinations must be strictly ascending')
    total = HEADER + len(image) + 8 * len(fixes)
    if total > 0xffffffff:
        raise ValueError('Package exceeds uint32 size')
    entries = config['entries'] + ([0, 0] if abi == 3 else [])
    words = [2, HEADER, total, 1, 1, abi, 0, services & 0xffffffff, services >> 32,
             HEADER, len(image), 0, config['text_bytes'], config['ro_offset'], config['ro_bytes'],
             config['data_offset'], config['data_bytes'], config['bss_bytes'], 16,
             config['heap_bytes'], config['stack_bytes'], *entries,
             HEADER + len(image), len(fixes), config['data_read_min'], config['data_read_max'],
             config['data_write_version']]
    struct.pack_into('<31I', h, 4, *words)
    for offset, key in ((128, 'app_id'), (160, 'version')):
        value = config[key].encode('ascii')
        if not 1 <= len(value) < 32 or any(chr(c) not in 'abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789._-+' for c in value):
            raise ValueError('Invalid ' + key)
        h[offset:offset+len(value)] = value
    result = h + image + b''.join(struct.pack('<II', *fix) for fix in fixes)
    result[192:224] = hashlib.sha256(result).digest()
    return bytes(result)


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('--image', type=Path, required=True)
    p.add_argument('--manifest', type=Path, required=True)
    p.add_argument('--output', type=Path, required=True)
    args = p.parse_args()
    blob = package(args.image.read_bytes(), json.loads(args.manifest.read_text()))
    with args.output.open('xb') as stream:
        stream.write(blob)
    print(json.dumps({'bytes': len(blob), 'content_sha256': blob[192:224].hex(),
                      'file_sha256': hashlib.sha256(blob).hexdigest(), 'hardware_verified': False}))


if __name__ == '__main__':
    main()
