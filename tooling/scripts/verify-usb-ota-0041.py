"""Check ROM-derived USB OTA tables and payload ranges; no firmware execution."""
import argparse
import hashlib
import json
from pathlib import Path
import struct

ROOT = Path(__file__).resolve().parents[2]
BASE = 0x9ffff000
SHA = '972db4c136c7ed9e24a83c07c1a7fd62040ca018b08ca285216d26b1fee3c6b9'


def verify():
    image = (ROOT/'roms/0041/ap01-1.0.2_0041.bin').read_bytes()
    assert hashlib.sha256(image).hexdigest() == SHA, 'Wrong ROM'
    table = struct.unpack_from('<256H', image, 0xa056d058-BASE)
    polynomial = table[1]
    assert polynomial == 0x1021
    for byte in range(256):
        value = byte << 8
        for _ in range(8):
            value = ((value << 1) ^ (polynomial if value & 0x8000 else 0)) & 0xffff
        assert value == table[byte], byte

    def crc(data, initial):
        assert data, 'Original helper is a do/while; zero length is not modeled'
        value = initial
        for byte in data:
            value = ((value << 8) ^ table[(value >> 8) ^ byte]) & 0xffff
        return value

    vectors = []
    for data in (b'123456789', bytes(range(256)), bytes([0xa5, 0x5a, 0xaa]), b'\0'):
        for initial in (0, 0xffff, 0x1234):
            bitwise = initial
            for byte in data:
                bitwise ^= byte << 8
                for _ in range(8):
                    bitwise = ((bitwise << 1) ^ (polynomial if bitwise & 0x8000 else 0)) & 0xffff
            assert crc(data, initial) == bitwise
            vectors.append(dict(data_hex=data.hex(), initial=initial, result=bitwise))
    assert crc(b'123456789', 0) == 0x31c3
    payloads = []
    for address, target in ((0xa026adb0, 'shared-selector-1'),
                            (0xa0276dc4, 'TA1208-selector-0'),
                            (0xa0281458, 'TA1408-selector-0')):
        offset = address-BASE
        header = image[offset:offset+18]
        blocks = struct.unpack_from('<H', header, 14)[0]
        length = 18+blocks*16
        assert blocks > 0 and offset+length <= len(image)
        payloads.append(dict(address=hex(address), file_offset=offset, target=target,
            header_hex=header.hex(), header_words_u16=list(struct.unpack('<9H', header)),
            block_count=blocks, block_stream_bytes=blocks*16, header_and_stream_bytes=length,
            sha256=hashlib.sha256(image[offset:offset+length]).hexdigest(),
            architecture='unknown; not established by the AP01 RV32 mapping'))
    for a, b in zip(payloads, payloads[1:]):
        assert a['file_offset']+a['header_and_stream_bytes'] <= b['file_offset']
    return dict(schema=1, rom_sha256=SHA, source='fixed original ROM and static consumer contract',
        validation='host-only table/bitwise comparison and bounded ROM reads; not guest execution',
        crc=dict(helper='0xa00ee8fc', table='0xa056d058', polynomial=hex(polynomial),
            table_sha256=hashlib.sha256(image[0xa056d058-BASE:0xa056d258-BASE]).hexdigest(),
            table_entries_checked=256, vectors=vectors,
            decompiler_return_type='void is contradicted by assembly a0 result and caller use'),
        embedded_payloads=payloads, complete_module=False)


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--out', type=Path)
    args = parser.parse_args()
    result = verify()
    if args.out:
        assert not args.out.exists(), 'Refusing to overwrite existing evidence'
        args.out.write_text(json.dumps(result, indent=2)+'\n', encoding='utf-8')
    print('PASS: 256 ROM CRC entries, 12 independent vector comparisons, 3 bounded payload streams')
