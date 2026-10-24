"""Q-01 review correction: only verify indicator-argument snapshot timing."""
import json
from pathlib import Path
import capstone

ROOT = Path('D:/Documents/PlatformIO/Projects/cuktech-ap01-firmware')

def verify_snapshot():
    md = capstone.Cs(capstone.CS_ARCH_RISCV, capstone.CS_MODE_RISCV32 | capstone.CS_MODE_RISCVC)
    expected = {
        0xa00adc18: ('lhu', 'a5, 0xa(s2)'),
        0xa00adc1c: ('sw', 'a5, -0xe0(s0)'),
        0xa00ae05e: ('lw', 'a5, -0xe0(s0)'),
        0xa00ae062: ('c.li', 'a2, 0'),
        0xa00ae064: ('c.beqz', 'a5, 4'),
        0xa00ae066: ('c.li', 'a2, 1'),
        0xa00ae068: ('c.mv', 'a1, s11'),
        0xa00ae06a: ('c.mv', 'a0, s1'),
        0xa00ae06c: ('jal', '0x49dc'),
    }
    rows = []
    with (ROOT/'roms/0041/ap01-1.0.2_0041.bin').open('rb') as rom:
        for lo, hi in [(0xa00adc18, 0xa00adc20), (0xa00ae05e, 0xa00ae070)]:
            rom.seek(lo-0x9ffff000)
            seq = list(md.disasm(rom.read(hi-lo), lo))
            assert sum(i.size for i in seq) == hi-lo
            for i in seq:
                assert (i.mnemonic, i.op_str) == expected[i.address]
                rows.append(dict(address=hex(i.address), raw=i.bytes.hex(),
                                 decoded=i.mnemonic+' '+i.op_str, passed=True))
    return dict(scope='Non-author review correction only; no unrelated checks rerun',
                source='Original 0041 ROM; static Capstone '+capstone.__version__,
                parameter='a00b2a48 a2 = (entry_snapshot_u16_item_plus_0a != 0)',
                capture='adc18 LHU item+0a; adc1c SW frame-0xe0 before child0 lookup',
                consumption='ae05e LW saved frame-0xe0, ae062/064/066 normalize bool; no item+0a reread here',
                bytes=26, instruction_count=9, checks=rows)

if __name__ == '__main__':
    path = Path(__file__).with_name('audit.json')
    data = json.loads(path.read_text(encoding='utf8'))
    data['indicator_argument_snapshot_correction'] = verify_snapshot()
    path.write_text(json.dumps(data,ensure_ascii=False,indent=2)+'\n',encoding='utf8')
    print('PASS: 26 bytes, 9 instructions; early u16 snapshot to later bool argument')
