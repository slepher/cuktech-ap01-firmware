"""C03: read-only ROM instruction checks; no firmware execution or REA session."""
import json
from pathlib import Path
from capstone import Cs, CS_ARCH_RISCV, CS_MODE_RISCV32, CS_MODE_RISCVC, cs_version

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
MAIN = Path('D:/Documents/PlatformIO/Projects/cuktech-ap01-firmware')
BASE = 0x9ffff000
rom = (MAIN / 'roms/0041/ap01-1.0.2_0041.bin').read_bytes()
retained = json.loads((ROOT / 'reverse/analysis/factory-test-0041-20261023/retained-initializer.json').read_text())['function']
for raw in retained['raw_ranges']:
    start = int(raw['start'], 16)
    expected = bytes.fromhex(raw['hex'])
    assert rom[start-BASE:start-BASE+len(expected)] == expected

cs = Cs(CS_ARCH_RISCV, CS_MODE_RISCV32 | CS_MODE_RISCVC)
windows = []
for name, start, end in [
    ('close_callback', 0xa00a3bc6, 0xa00a3c12),
    ('release_wrapper', 0xa008ab8a, 0xa008abb0),
    ('adc_userdata_count', 0xa005b14e, 0xa005b178),
    ('temp_userdata_count', 0xa005b190, 0xa005b1ba),
    ('port_userdata_count', 0xa005b1d2, 0xa005b1fc),
    ('uart_userdata_count', 0xa005b2e6, 0xa005b314),
]:
    raw = rom[start-BASE:end-BASE]
    instructions = list(cs.disasm(raw, start))
    assert sum(i.size for i in instructions) == len(raw), name
    windows.append(dict(name=name, start=hex(start), end_exclusive=hex(end), instructions=[
        dict(address=hex(i.address), hex=i.bytes.hex(), decode=i.mnemonic+' '+i.op_str)
        for i in instructions]))

# Independently resolve the ordinary RV32 branch/JAL immediates used in the conclusion.
def sx(value, bits):
    return value - (1 << bits) if value & (1 << (bits-1)) else value

def target(pc, kind):
    w = int.from_bytes(rom[pc-BASE:pc-BASE+4], 'little')
    if kind == 'jal':
        assert w & 0x7f == 0x6f
        imm = ((w >> 31) << 20) | (((w >> 12) & 255) << 12) | (((w >> 20) & 1) << 11) | (((w >> 21) & 1023) << 1)
        return (pc + sx(imm, 21)) & 0xffffffff
    assert w & 0x7f == 0x63
    imm = ((w >> 31) << 12) | (((w >> 7) & 1) << 11) | (((w >> 25) & 63) << 5) | (((w >> 8) & 15) << 1)
    return (pc + sx(imm, 13)) & 0xffffffff

transfers = []
for pc, kind, expected in [(0xa00a3bdc, 'branch', 0xa00a3c08), (0xa00a3bfe, 'jal', 0xa008b51a), (0xa00a3c04, 'jal', 0xa008ab8a), (0xa008aba2, 'jal', 0xa002e14e), (0xa008ab92, 'branch', 0xa008abae), (0xa008ab96, 'branch', 0xa008abae)]:
    actual = target(pc, kind)
    assert actual == expected
    transfers.append(dict(site=hex(pc), kind=kind, target=hex(actual)))
strings = []
for address in [0xa01c29b4, 0xa026a828, 0xa01c3a10]:
    data = rom[address-BASE:address-BASE+128].split(b'\0')[0]
    strings.append(dict(address=hex(address), hex=data.hex(), text=data.decode('ascii')))

result = dict(task='C03', rom_path=str(MAIN / 'roms/0041/ap01-1.0.2_0041.bin'), va_base=hex(BASE),
    retained_initializer_evidence_id=retained['evidence_id'], capstone_version=cs_version(),
    windows=windows, resolved_transfers=transfers, strings=strings,
    validation=dict(retained_initializer_raw_ranges_match_rom=True, selected_bytes=sum(sum(len(bytes.fromhex(i['hex'])) for i in w['instructions']) for w in windows), undecoded_selected_bytes=0, firmware_executed=False),
    limitations=['Callback bounds are a local entry/prologue/return view, not a new whole-ROM function-boundary discovery.', 'No full libuv close dispatch, allocator implementation, timer deletion, count invariant, or all-ROM alias search is certified.'])
(HERE / 'instruction-evidence.json').write_text(json.dumps(result, ensure_ascii=False, indent=2)+'\n', encoding='utf-8')
print(json.dumps(result['validation']))
