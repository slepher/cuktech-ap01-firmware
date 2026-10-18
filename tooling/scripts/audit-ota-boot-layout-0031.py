#!/usr/bin/env python3
"""Read-only comparison of AP01 0031 boot metadata; never asserts physical boot."""
import argparse
import hashlib
import json
from pathlib import Path
import struct
import zlib

BASE = 0x9ffff000
PEC = 0x677800
GIF = (0x1f80ac, 385834)
HOOK = 0x1ba8f0
STOCK_SHA = '8a721fc8ef25458d415b2460e4a251e0503a82f7743fdff85b12612190e5c1cb'


def sha(data):
    return hashlib.sha256(data).hexdigest()


def word(data, offset):
    return struct.unpack_from('<I', data, offset)[0]


def inspect(path, stock):
    data = path.read_bytes()
    span_end = 0x1000 + word(data, 0x84)
    aligned = (span_end + 0x7ff) & ~0x7ff
    pec = data[PEC:len(stock)-40]
    result = dict(path=str(path), bytes=len(data), sha256=sha(data),
        header_crc_ok=zlib.crc32(data[:252]) == word(data, 252),
        header_identical_to_stock=data[:256] == stock[:256],
        basic_config_word=word(data, 0x78),
        header_hash_ignore_bit=bool(word(data, 0x78) & (1 << 17)),
        header_first_hash_word=word(data, 0x88),
        image_span=word(data, 0x84), declared_span_end=span_end,
        next_2k_boundary=aligned,
        pec_at_fixed_offset=data[PEC:PEC+4] == b'PEC:',
        pec_at_next_2k_boundary=data[aligned:aligned+4] == b'PEC:',
        pec_identical_to_stock=pec == stock[PEC:len(stock)-40],
        pec_sha256=sha(pec),
        gif_identical_to_stock=data[GIF[0]:sum(GIF)] == stock[GIF[0]:sum(GIF)],
        gif_descriptor_identical=data[0x1f809c:0x1f80ac] == stock[0x1f809c:0x1f80ac],
        native_ota_entry_identical=data[0x1135b2:0x1135b6] == stock[0x1135b2:0x1135b6],
        builtin_entry=word(data, HOOK),
        trailer_length_ok=struct.unpack_from('>I', data, len(data)-8)[0] == len(data),
        trailer_crc_ok=struct.unpack_from('<I', data, len(data)-4)[0] ==
            (zlib.crc32(data[:-4], 0xffffffff) ^ 0xffffffff))
    if data[0x67e000:0x67e008] in (b'AP01OTA1', b'AP01HTTP', b'AP01DIA1'):
        offset = 0x67e000
        header = bytearray(data[offset:offset+256])
        stored = word(header, 32)
        struct.pack_into('<I', header, 32, 0)
        size, entry = word(header, 20), word(header, 24)
        result['module'] = dict(magic=header[:8].decode('ascii'), offset=offset,
            size=size, entry=entry, entry_matches_builtin=entry == word(data, HOOK),
            entry_inside_code=BASE+offset+256 <= entry < BASE+offset+size,
            self_length_ok=word(header, 12) == len(data),
            self_offset_ok=word(header, 16) == offset,
            manifest_crc_ok=zlib.crc32(header) == stored,
            code_crc_ok=zlib.crc32(data[offset+256:offset+size]) == word(header, 28))
    return result


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--stock', type=Path, required=True)
    parser.add_argument('--candidate', type=Path, action='append', required=True)
    parser.add_argument('--output', type=Path, required=True)
    args = parser.parse_args()
    stock = args.stock.read_bytes()
    if sha(stock) != STOCK_SHA:
        parser.error('stock image identity mismatch')
    images = [inspect(path, stock) for path in [args.stock, *args.candidate]]
    report = dict(schema='ap01-0031-offline-boot-layout-v1', images=images,
        pec_file_offset=PEC, pec_virtual_address=BASE+PEC,
        boundary_relation_is_observation_only=True,
        actual_boot2_available=False, physical_root_cause_confirmed=False,
        physical_boot_verified=False,
        scope='Byte comparison only. Does not infer PEC discovery or XIP limits from alignment.')
    with args.output.open('x', encoding='utf-8') as stream:
        json.dump(report, stream, indent=2)
        stream.write('\n')
    print(json.dumps(dict(output=str(args.output), images=len(images), physical_root_cause_confirmed=False)))


if __name__ == '__main__':
    main()
