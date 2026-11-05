"""Pin the immutable 0041 ROM evidence for nonblocking listener creation.

Static instruction audit only: no network, emulator, or hardware execution.
The words for th.extu encode high/low bit indices in bits 25:20/31:26;
both are 11 here. Do not substitute Linux socket constants for this evidence.
"""
import argparse
import hashlib
import json
from pathlib import Path
import struct

BASE = 0x9ffff000


def audit(rom):
    digest = hashlib.sha256(rom).hexdigest()
    assert digest == '972db4c136c7ed9e24a83c07c1a7fd62040ca018b08ca285216d26b1fee3c6b9', 'exact original 0041 required'
    # Call chain: socket -> psock_socket -> IPv4 ops.accept -> TCP wait.
    evidence = {
        0xa00268e2: ('8bb7b52c', 'socket extracts type bit 11'),
        0xa00360e2: ('b7f7f7ff9387077fed8ff1eb93f7f500', 'type validation permits bit 11; strips flags from socket kind'),
        0xa0036194: ('8b35b92cdc4099c503c7d70113678700a38ee700', 'psock_socket maps type bit 11 to conn.flags bit 3'),
        0xa01be928: ('d64903a0', 'IPv4 ops offset 32 selects TCP accept at a00349d6'),
        0xa0034a4c: ('03c7d901218b41cbd554cda8', 'empty backlog with bit 3 set returns -11'),
        0xa0034af6: ('fd55', 'blocking accept passes timeout -1'),
        0xa0034b1a: ('ef704057', 'blocking accept calls wait at a003c08e'),
        0xa003c0ac: ('fd572a8926856384f502', 'wait branches on timeout -1'),
        0xa003c0da: ('efb02ef9', 'timeout -1 invokes indefinite semaphore wait'),
    }
    for address, (expected, _) in evidence.items():
        value = bytes.fromhex(expected)
        assert rom[address-BASE:address-BASE+len(value)] == value, hex(address)
    for address in (0xa00268e2, 0xa0036194):
        word = struct.unpack_from('<I', rom, address-BASE)[0]
        assert (word >> 20) & 63 == 11 and (word >> 26) & 63 == 11
    return {'passed': True, 'scope': 'static immutable ROM instruction audit',
            'rom_sha256': digest, 'socket_nonblock': 0x800,
            'device_accessed': False, 'instructions_executed': False,
            'evidence': {hex(a): {'bytes': b, 'meaning': meaning}
                         for a, (b, meaning) in evidence.items()}}


if __name__ == '__main__':
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('--rom', type=Path)
    p.add_argument('--report', type=Path, required=True)
    args = p.parse_args()
    rom = args.rom or Path(__file__).resolve().parents[2]/'roms/0041/ap01-1.0.2_0041.bin'
    result = audit(rom.read_bytes())
    args.report.write_text(json.dumps(result, indent=2)+'\n')
    print('0041 static network audit passed; no runtime or hardware claim')
