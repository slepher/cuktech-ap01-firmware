"""Q-03 bounded static evidence; reads ROM as data, executes no target/model."""
from pathlib import Path
import json
from datetime import datetime, timezone
from capstone import Cs, CS_ARCH_RISCV, CS_MODE_RISCV32, CS_MODE_RISCVC

ROOT = Path('D:/Documents/PlatformIO/Projects/cuktech-ap01-firmware')
HERE = Path(__file__).resolve().parent
BASE = 0x9ffff000
rom = (ROOT/'roms/0041/ap01-1.0.2_0041.bin').read_bytes()
assert len(rom) == 6769704
cs = Cs(CS_ARCH_RISCV, CS_MODE_RISCV32 | CS_MODE_RISCVC)
spans = [
    ('W_factory_call', 0xa01afda6, 0xa01afdae),
    ('base_class_argument', 0xa00d91d0, 0xa00d91de),
    ('same_P_presentation_and_install', 0xa01b0608, 0xa01b0638),
    ('same_P_presentation_helper', 0xa00f50c2, 0xa00f51f4),
    ('DELETE_complete', 0xa00f1b8e, 0xa00f1c28),
    ('Return_call', 0xa00f7194, 0xa00f71b6),
]
windows = []
checks = []
def signed(v, n):
    return v - (1 << n) if v & (1 << (n-1)) else v
for name, start, end in spans:
    rows = []
    pc = start
    while pc < end:
        offset = pc-BASE
        size = 4 if rom[offset]&3 == 3 else 2
        raw = rom[offset:offset+size]
        assert pc+size <= end
        ins = next(cs.disasm(raw, pc), None)
        word = int.from_bytes(raw, 'little')
        row = dict(address=hex(pc), file_offset=offset, bytes=raw.hex(),
                   assembly=ins.mnemonic+' '+ins.op_str if ins else 'opaque')
        if size == 4 and word&127 == 111:
            imm = ((word>>31)<<20) | (((word>>12)&255)<<12) | (((word>>20)&1)<<11) | (((word>>21)&1023)<<1)
            row['direct_target'] = hex(pc+signed(imm,21))
        rows.append(row)
        pc += size
    assert pc == end
    windows.append(dict(name=name, start=hex(start), end_exclusive=hex(end), instructions=rows))
index = {int(r['address'],16):r for w in windows for r in w['instructions']}
for pc, target in [(0xa01afda6,0xa00d91c6),(0xa00d91da,0xa00d76ae),(0xa01b060e,0xa00f50c2),(0xa01b0630,0xa01ad654),(0xa00f1bea,0xa008ae58),(0xa00f1c10,0xa008ab8a),(0xa00f71ae,0xa00ded6c)]:
    assert index[pc]['direct_target'] == hex(target)
    checks.append(dict(callsite=hex(pc),target=hex(target)))
# Compare the old author's address/byte carrier, not its implementation script.
old = json.loads((ROOT/'reverse/analysis/history-init-reset-p19-0041-20261024/static-evidence.json').read_text(encoding='utf8'))
matched = 0
for window in old['windows']:
    for r in window['instructions']:
        pc = int(r['address'],16)
        if pc in index:
            assert index[pc]['bytes'] == r['hex']
            matched += 1
class_address = 0xa0263ef4
raw = rom[class_address-BASE:class_address-BASE+16]
words = [int.from_bytes(raw[i:i+4],'little') for i in range(0,16,4)]
assert words[0] == 0 and words[2] == 0xa00d87d0
assert index[0xa00f1bac]['bytes'] == '83294500'  # original target E+4
assert index[0xa00f1bee]['bytes'] == '4a85'      # a0=s2=R
assert index[0xa01b060c]['bytes'] == '2685'      # a0=s1=P
out = dict(observed_utc=datetime.now(timezone.utc).isoformat(),
    source='roms/0041/ap01-1.0.2_0041.bin', mapping_base=hex(BASE),
    identity='inherited CATALOG SHA256 972db4c136c7ed9e24a83c07c1a7fd62040ca018b08ca285216d26b1fee3c6b9; length checked, digest not recomputed',
    decoder='Capstone RV32+C; unsupported bytes opaque; direct JAL independently extracted; no model import or changes',
    windows=windows, direct_edges=checks, old_carrier_bytes_matched=matched,
    W_class=dict(address=hex(class_address),bytes=raw.hex(),words=[hex(x) for x in words]),
    limitations=['Static only; public GUI/free/timer callees not expanded.', 'No all-ROM P reader/writer or free scan.', 'Old profiles remain absent; no modern profile attached.'])
(HERE/'static-evidence.json').write_text(json.dumps(out,ensure_ascii=False,indent=2)+'\n',encoding='utf8')
print('PASS',len(windows),'windows',sum(len(w['instructions']) for w in windows),'instructions',matched,'old carrier matches')
