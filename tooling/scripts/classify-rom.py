"""Identify an AP01 OTA image before writing; filenames are not trusted."""
import argparse
import hashlib
import json
from pathlib import Path
import struct
import zlib

OFFICIAL = {
    '8a721fc8ef25458d415b2460e4a251e0503a82f7743fdff85b12612190e5c1cb': 'official_0031',
    '972db4c136c7ed9e24a83c07c1a7fd62040ca018b08ca285216d26b1fee3c6b9': 'official_0041',
    '0d4a2c10314e984e8425f77385f3be89ebe33937eaa711938fda8f318a909bb7': 'official_0055',
}
WARNINGS = {
    'official_0041': '原厂 0041 限制第三方 ROM 的常规 OTA 入口，且没有本项目维护接口。',
    'official_0055': '原厂 0055 限制第三方 ROM 的常规 OTA 入口，且没有本项目维护接口。',
    'third_party': '其他第三方 ROM：维护接口及恢复能力未知。',
}

def classify(data):
    if not 296 <= len(data) <= 0x700000:
        raise ValueError('Invalid complete OTA image size')
    if zlib.crc32(data[:252]) != struct.unpack_from('<I', data, 252)[0]:
        raise ValueError('Invalid boot header CRC')
    if data[-40:-16] != b'0x5245434f56455259544147' or struct.unpack_from('>I', data, len(data)-8)[0] != len(data):
        raise ValueError('Invalid recovery framing')
    crc = struct.unpack_from('<I', data, len(data)-4)[0]
    if (zlib.crc32(data[:-4], 0xffffffff) ^ 0xffffffff) != crc:
        raise ValueError('Invalid upload CRC')
    digest = hashlib.sha256(data).hexdigest()
    kind = OFFICIAL.get(digest, 'third_party')
    if kind == 'third_party' and len(data) >= 0x675100:
        header = bytearray(data[0x675000:0x675100])
        if header[:8] == b'AP01APP1':
            stored = struct.unpack_from('<I', header, 32)[0]
            struct.pack_into('<I', header, 32, 0)
            if zlib.crc32(header) != stored or struct.unpack_from('<III', header, 8) != (1, len(data), 0x675000):
                raise ValueError('Invalid platform manifest')
            kind = {1: 'base', 2: 'app_platform'}.get(struct.unpack_from('<I', header, 252)[0], 'third_party')
    return {'rom_kind': kind, 'length': len(data), 'sha256': digest, 'recovery_crc': f'{crc:08x}', 'warning': WARNINGS.get(kind)}

if __name__ == '__main__':
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('rom', type=Path)
    a=p.parse_args()
    try:
        print(json.dumps(classify(a.rom.read_bytes()), ensure_ascii=False, indent=2))
    except ValueError as error:
        p.error(str(error))
