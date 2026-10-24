"""Static window verification only; never executes target code."""
import argparse
import hashlib
import json
from pathlib import Path
import capstone

parser = argparse.ArgumentParser()
parser.add_argument('rom', type=Path)
args = parser.parse_args()
root = Path(__file__).parent
windows = json.loads((root / 'windows.json').read_text())
image = args.rom.read_bytes()
assert len(image) == 6769704
assert [(int(w['va'], 16), w['length']) for w in windows] == [
    (0xa00bb67e, 92), (0xa00be8ca, 430), (0xa00bea78, 404),
    (0xa00bb0c2, 26), (0xa00bb0dc, 26), (0xa00bb6da, 308),
    (0xa01adc0e, 96),
]
allowed_unknown = {0xa00be922, 0xa00be940, 0xa00be95e, 0xa00be980}
unknown = set()
md = capstone.Cs(capstone.CS_ARCH_RISCV,
                 capstone.CS_MODE_RISCV32 | capstone.CS_MODE_RISCVC)
for window in windows:
    va = int(window['va'], 16)
    assert window['offset'] == va - 0x9ffff000
    raw = image[window['offset']:window['offset'] + window['length']]
    assert raw.hex() == window['hex']
    assert hashlib.sha256(raw).hexdigest() == window['sha256']
    position = 0
    while position < len(raw):
        instruction = next(md.disasm(raw[position:], va + position, count=1), None)
        if instruction:
            position += instruction.size
        else:
            unknown.add(va + position)
            position += 4 if raw[position] & 3 == 3 else 2
    assert position == len(raw)
assert unknown == allowed_unknown
print(f'PASS: {len(windows)} windows, {sum(w["length"] for w in windows)} bytes; 4 explicit vendor words retained')
