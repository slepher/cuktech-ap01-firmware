"""Pin the fixed 0041 current-thread TLS lookup; static evidence, no execution."""
import argparse
import hashlib
import json
from pathlib import Path


def audit(rom):
    digest = hashlib.sha256(rom).hexdigest()
    assert digest == '972db4c136c7ed9e24a83c07c1a7fd62040ca018b08ca285216d26b1fee3c6b9'
    evidence = {
        0xa0026724: ('b777fc6283a487c1', 'load current TCB from 0x62fc6c18'),
        0xa0026742: ('0dc5', 'task ID zero selects the current TCB path at 0xa002676c'),
        0xa002676c: ('985f014598c1d85fd8c1bc439cc5', 'copy TCB offsets 56, 60, 64 into caller buffer; return zero'),
        0xa0026784: ('011122cc06ce0010930544fe0145eff09ff8814763440500832784fef24062443e8505618280',
                     'request task ID zero; on negative result return zero, otherwise return buffer word 1 (TCB offset 60)'),
        0xa00267c0: ('411122c406c60008eff0dffb11c51105b2402244410182803765fc621305c504c5bf',
                     'errno uses TLS+4 when available, otherwise global 0x62fc604c; do not use fallback as identity'),
    }
    for address, (expected, _) in evidence.items():
        value = bytes.fromhex(expected)
        assert rom[address-0x9ffff000:address-0x9ffff000+len(value)] == value, hex(address)
    return dict(passed=True, rom_sha256=digest, lookup='0xa0026784',
                scope='static fixed-ROM call chain only', instructions_executed=False,
                device_accessed=False,
                limitations=['Worker/task context required; no interrupt-context guarantee.',
                             'Does not prove scheduler TLS lifetime or uniqueness at runtime.'],
                evidence={hex(a): dict(bytes=b, meaning=m) for a, (b, m) in evidence.items()})


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--rom', type=Path)
    parser.add_argument('--report', type=Path, required=True)
    args = parser.parse_args()
    rom = args.rom or Path(__file__).resolve().parents[2]/'roms/0041/ap01-1.0.2_0041.bin'
    args.report.write_text(json.dumps(audit(rom.read_bytes()), indent=2)+'\n')
    print('0041 thread identity static audit passed; scheduler/runtime identity not proven')
