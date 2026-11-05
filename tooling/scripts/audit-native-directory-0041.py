"""Pin candidate 0041 directory callbacks; static evidence, not a callable ABI proof."""
import argparse
import hashlib
import json
import struct
from pathlib import Path


def audit(rom):
    digest = hashlib.sha256(rom).hexdigest()
    assert digest == '972db4c136c7ed9e24a83c07c1a7fd62040ca018b08ca285216d26b1fee3c6b9'
    base = 0x9ffff000
    table = [0xa00480c8, 0xa0041e00, 0xa00455c8, 0xa0045d34,
             0xa0041ea8, 0xa00484d0, 0, 0xa0045dec, 0, 0xa0041e5e,
             0xa004031a, 0xa0043d42, 0xa0045ab0, 0xa0044b9a,
             0xa0040362, 0xa00448c4, 0xa00444fa, 0xa0041f58,
             0xa0042144, 0xa00421bc, 0xa0041f12, 0xa00485e4,
             0xa0044e78, 0xa004888c, 0xa0044cd4, 0xa004223a, 0]
    assert list(struct.unpack_from('<27I', rom, 0xa01bf590-base)) == table
    candidates = [
        ('open', 0x34, 0xa0044b9a, 0x13a, '1bc3e793b5c772a535d56a8be74f524998064d010fb13f10472547e03e89edd7'),
        ('close', 0x38, 0xa0040362, 0x50, 'c955bdd5fc108414a90bfd7c5954c4b61d767595e0751f452dd0f827ddfa06cd'),
        ('read', 0x3c, 0xa00448c4, 0x11e, '9be6d804a8aebea6b08d2785f4510dbe2b07bcbcad8e71a708c8ad59059443dd'),
        ('rewind', 0x40, 0xa00444fa, 0x56, 'fc2bd4ea95b37766aaa534ee1a743aea8ac70c559ec9ce004ef698055fc80dcf'),
    ]
    evidence = {}
    for role, offset, address, size, expected in candidates:
        assert table[offset//4] == address
        assert hashlib.sha256(rom[address-base:address-base+size]).hexdigest() == expected
        evidence[role] = dict(table_offset=hex(offset), address=hex(address), bytes=size, sha256=expected)
    return dict(passed=True, rom_sha256=digest, instructions_executed=False,
                device_accessed=False, callable_abi_verified=False,
                operation_table='0xa01bf590', candidates=evidence,
                observations=[
                    'Callbacks load mount-private pointer from inode+24 and use lock 0xa0027968 / unlock 0xa00274b2.',
                    'Open allocates 60 bytes; close unlinks handle+8 from mount-private+280 before freeing.',
                    'Read uses handle+48 as position; synthesizes dot entries and copies 129 name bytes.',
                    'Read contains custom instruction 0x1815578b at 0xa004493c; output layout is not established by this audit.',
                    'Rewind resets handle+12 and handle+48 after successful internal seek.',
                ], limitations=[
                    'Candidate roles inferred from fixed-ROM disassembly, not from upstream NuttX headers.',
                    'Must execute callbacks with guarded output buffers and lock/error cases before defining the private enumeration ABI.',
                    'No directory traversal, flash persistence, or reference-safe orphan deletion is proven.',
                ])


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--rom', type=Path, required=True)
    parser.add_argument('--report', type=Path, required=True)
    args = parser.parse_args()
    args.report.write_text(json.dumps(audit(args.rom.read_bytes()), indent=2)+'\n')
    print('0041 directory static audit passed; callable ABI and orphan GC remain unverified')
