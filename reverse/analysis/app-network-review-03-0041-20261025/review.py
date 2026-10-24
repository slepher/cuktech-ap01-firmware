"""Independent read-only Q09 byte/retained-caller inspection; no target execution."""
from pathlib import Path
import json
import hashlib
import capstone

ROOT = Path('D:/Documents/PlatformIO/Projects/cuktech-ap01-firmware')
OUT = Path(__file__).resolve().parent
rom = (ROOT / 'roms/0041/ap01-1.0.2_0041.bin').read_bytes()
assert len(rom) == 6769704
md = capstone.Cs(capstone.CS_ARCH_RISCV, capstone.CS_MODE_RISCV32 | capstone.CS_MODE_RISCVC)
ranges = [(0xa0067aec, 0xa0067b94), (0xa0067b94, 0xa0067be6),
          (0xa0068854, 0xa0068914), (0xa0068914, 0xa0068a26)]
vendor = {0xa006895a: 0x5847d68b, 0xa00689ce: 0x44f9568b}
retained = []
for lo, hi in ranges:
    raw = rom[lo-0x9ffff000:hi-0x9ffff000]
    lines = []
    pc = lo
    while pc < hi:
        off = pc - 0x9ffff000
        if pc in vendor:
            w = int.from_bytes(rom[off:off+4], 'little')
            assert w == vendor[pc]
            fields = dict(op=w & 127, rd=(w >> 7) & 31, f3=(w >> 12) & 7,
                          rs1=(w >> 15) & 31, rs2=(w >> 20) & 31,
                          shift=(w >> 25) & 3, top=(w >> 27) & 31)
            lines.append(f'{pc:08x} {rom[off:off+4].hex()} vendor {fields}')
            pc += 4
        else:
            ins = next(md.disasm(rom[off:off+4], pc, 1), None)
            assert ins is not None, hex(pc)
            lines.append(f'{pc:08x} {ins.bytes.hex()} {ins.mnemonic} {ins.op_str}')
            pc += ins.size
    assert pc == hi
    retained.append(dict(start=hex(lo), end_exclusive=hex(hi), length=len(raw),
                         sha256=hashlib.sha256(raw).hexdigest(), raw=raw.hex(), assembly=lines))
record = json.loads((ROOT/'evidence/rea-0041-20261017/evidence/upper-complete.evidence.json').read_text(encoding='utf-8'))['records'][89]
caller = [l for l in record['normalized_result']['assembly']
          if 0xa006e350 <= int(l.split(':')[0], 16) <= 0xa006e85c
          or 0xa006e200 <= int(l.split(':')[0], 16) <= 0xa006e224
          or int(l.split(':')[0], 16) == 0xa006e348]
expected_bytes = {
    0xa0067b10: '23a0b41c', 0xa0067b14: '9307f9e0',
    0xa0067b18: '63f8b704', 0xa0067b24: '23a0041c',
    0xa0067bb4: 'b947', 0xa0067bb8: '63e3b702',
    0xa0067bbc: '23a8b41c', 0xa0067bde: '23a8041c',
    0xa0068874: '83a78418', 0xa006887a: '23a2b418',
    0xa006887e: '63e6f506', 0xa006888c: '23a20418',
    0xa006893a: 'b3d7e702', 0xa0068940: '23a8b418',
    0xa0068946: '63eaf508', 0xa006895e: 'e39de7fe',
    0xa006896a: '1cdf', 0xa0068970: '63e3e708',
    0xa00689c2: '83a6c418', 0xa00689d4: 'e39de7fe',
}
for va, raw_hex in expected_bytes.items():
    off = va - 0x9ffff000
    assert rom[off:off+len(raw_hex)//2].hex() == raw_hex
expected_caller = [
    '0xa006e348: beq s11, a4, 0xa006e350',
    '0xa006e378: bne a5, a4, 0xa006e786',
    '0xa006e386: beq a5, zero, 0xa006e604',
    '0xa006e5b0: jal ra, 0xa0068914',
    '0xa006e6ae: jal ra, 0xa0067b94',
    '0xa006e6e8: c.j 0xa006e778',
    '0xa006e764: beq a0, zero, 0xa006e5ac',
    '0xa006e76c: c.bnez a0, 0xa006e778',
    '0xa006e786: bne a5, s11, 0xa006e7ce',
    '0xa006e7a0: beq s6, zero, 0xa006e778',
    '0xa006e7ac: c.bnez a0, 0xa006e6da',
    '0xa006e7b6: c.beqz a0, 0xa006e7c2',
    '0xa006e7c6: jal ra, 0xa0068914',
    '0xa006e7cc: c.j 0xa006e76e',
    '0xa006e83a: c.j 0xa006e7ca',
]
assert all(line in caller for line in expected_caller)
sinc = (ROOT/'evidence/rea-0041-20261017/processor/data/languages/ap01thead2.sinc').read_text(encoding='utf-8').splitlines()
result = dict(source_size=len(rom), mapping='offset=VA-0x9ffff000', capstone=capstone.__version__,
              total_helper_bytes=sum(v['length'] for v in retained), helpers=retained,
              caller_evidence=record['evidence_id'], caller=caller,
              sinc=[f'{i+1}: {sinc[i]}' for i in range(6595, 6622)],
              checks=dict(raw_bytes=len(expected_bytes), caller_edges=len(expected_caller),
                          vendor_words=len(vendor), decode_extents=len(ranges)))
assert result['total_helper_bytes'] == 716
(OUT/'review-evidence.json').write_text(json.dumps(result, ensure_ascii=False, indent=2)+'\n', encoding='utf-8')
print('\n'.join(l for h in retained for l in h['assembly']))
print('\nCALLER\n'+'\n'.join(caller))
