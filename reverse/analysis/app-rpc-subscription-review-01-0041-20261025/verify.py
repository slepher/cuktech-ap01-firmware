"""Independent offline Q26 byte comparison and RV32C disassembly; never runs ROM."""
import hashlib
import json
from pathlib import Path
import capstone

HERE = Path(__file__).resolve().parent
REPO = HERE.parents[2]
MAIN = Path('D:/Documents/PlatformIO/Projects/cuktech-ap01-firmware')
AUTHOR = MAIN / 'reverse/analysis/app-rpc-subscription-research-01-0041-20261025'
if not (AUTHOR / 'static-windows.json').exists():
    AUTHOR = HERE.parents[3] / 'rpc-subscription01/reverse/analysis/app-rpc-subscription-research-01-0041-20261025'
SPEC = [(0xa00c6368,532),(0xa00c657c,524),(0xa00c6788,524),(0xa00c6994,524),
        (0xa00c0492,26),(0xa00c04ac,26),(0xa00c2148,26),(0xa00c2438,26),
        (0xa00c1fd8,184),(0xa00c2090,184),(0xa01adbd4,58),(0xa01adb9a,58),(0xa00c187c,92)]

def main():
    data = (REPO / 'roms/0041/ap01-1.0.2_0041.bin').read_bytes()
    sha = hashlib.sha256(data).hexdigest()
    assert len(data) == 6769704
    assert sha == '972db4c136c7ed9e24a83c07c1a7fd62040ca018b08ca285216d26b1fee3c6b9'
    author = json.loads((AUTHOR / 'static-windows.json').read_text(encoding='utf-8'))
    decoder = capstone.Cs(capstone.CS_ARCH_RISCV, capstone.CS_MODE_RISCV32 | capstone.CS_MODE_RISCVC)
    windows = []
    rows = {}
    for (address, length), old in zip(SPEC, author['windows'], strict=True):
        raw = data[address - 0x9ffff000:address - 0x9ffff000 + length]
        assert old['start'] == hex(address) and old['length'] == length
        assert raw.hex() == old['raw'] and hashlib.sha256(raw).hexdigest() == old['sha256']
        insns = list(decoder.disasm(raw, address))
        assert sum(i.size for i in insns) == length
        decoded = []
        for insn in insns:
            entry = {'pc': hex(insn.address), 'raw': insn.bytes.hex(), 'asm': insn.mnemonic + ' ' + insn.op_str}
            if insn.mnemonic in ('jal','beq','bne','beqz','bnez','bge','bgeu','blt','bltu','c.j','c.beqz','c.bnez'):
                entry['target'] = hex((insn.address + int(insn.op_str.rsplit(',', 1)[-1].strip(), 0)) & 0xffffffff)
            rows[insn.address] = entry
            decoded.append(entry)
        assert [(x['pc'], x['raw'], x['asm']) for x in decoded] == [(x['pc'], x['raw'], x['asm']) for x in old['rows']]
        windows.append({'address': hex(address), 'length': length, 'sha256': hashlib.sha256(raw).hexdigest(), 'rows': decoded})
    targets = {0xa00c639e:0xa00c6578,0xa00c63aa:0xa00c6550,0xa00c65b6:0xa00c6656,0xa00c65c0:0xa00c6656,
               0xa00c67c2:0xa00c6862,0xa00c67cc:0xa00c6862,0xa00c69ce:0xa00c6a6e,0xa00c69d8:0xa00c6a6e}
    assert all(rows[pc]['target'] == hex(target) for pc,target in targets.items())
    result = {'rom_bytes':len(data),'rom_sha256':sha,'decoder':capstone.__version__, 'author_source':str(AUTHOR),
              'window_bytes':sum(n for _,n in SPEC),'windows':windows,'invalid_gate_targets':'8/8 PASS',
              'raw_hash_decode_comparison':'13/13 PASS','mode':'independent static ROM read; author script not executed'}
    (HERE / 'independent-windows.json').write_text(json.dumps(result, indent=2),encoding='utf-8')
    (HERE / 'independent-disassembly.txt').write_text('\n'.join(f"{r['pc']} {r['raw']} {r['asm']}" + (' -> ' + r['target'] if 'target' in r else '') for w in windows for r in w['rows']),encoding='utf-8')
    print('PASS ROM identity; 13 windows / 2784 bytes; independent decode and raw compare; 8 invalid-gate targets')

if __name__ == '__main__':
    main()
