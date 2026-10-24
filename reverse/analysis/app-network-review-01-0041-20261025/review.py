"""Independent Q06 static review. Does not import or execute author verifier."""
import json
from pathlib import Path
from capstone import Cs, CS_ARCH_RISCV, CS_MODE_RISCV32, CS_MODE_RISCVC

ROOT = Path(__file__).resolve().parents[3]
OUT = Path(__file__).resolve().parent
rom = ROOT / 'roms/0041/ap01-1.0.2_0041.bin'
assert rom.stat().st_size == 6769704
spans = [(0xa0065810, 0xa0065814), (0xa0065824, 0xa006582e),
         (0xa006d064, 0xa006d074), (0xa006d0c2, 0xa006d0d8),
         (0xa006d124, 0xa006d158), (0xa006d1a0, 0xa006d1ae),
         (0xa006d1ec, 0xa006d1fc), (0xa006d24a, 0xa006d25a),
         (0xa006722c, 0xa006726a), (0xa005fac4, 0xa005faec)]
md = Cs(CS_ARCH_RISCV, CS_MODE_RISCV32 | CS_MODE_RISCVC)
windows = []
ins = {}
with rom.open('rb') as f:
    for start, end in spans:
        f.seek(start - 0x9ffff000)
        raw = f.read(end - start)
        decoded = list(md.disasm(raw, start))
        assert sum(i.size for i in decoded) == len(raw)
        for i in decoded:
            ins[i.address] = i
        windows.append(dict(start=hex(start), end_exclusive=hex(end), raw=raw.hex(),
                            instructions=[f'{i.address:#x}: {i.bytes.hex()} {i.mnemonic} {i.op_str}' for i in decoded]))

def u(a):
    return int.from_bytes(ins[a].bytes, 'little')

def signed(v, n):
    return v - (1 << n) if v & (1 << (n-1)) else v

def jal(a):
    w = u(a)
    assert w & 127 == 111
    off = ((w >> 31) << 20) | (((w >> 12) & 255) << 12) | (((w >> 20) & 1) << 11) | (((w >> 21) & 1023) << 1)
    return a + signed(off, 21)

checks = []
def check(label, truth):
    assert truth, label
    checks.append(label)

check('N base offset +180', signed(u(0xa0065810) >> 20, 12) == 0x180)
check('callback constructed cda4', (u(0xa0065824) & 0xfffff000) + signed(u(0xa0065828) >> 20, 12) == 0xa006cda4)
c = u(0xa006582c)
off = (((c >> 10) & 7) << 3) | (((c >> 6) & 1) << 2) | (((c >> 5) & 1) << 6)
check('callback C.SW a4,+78(a5): N+1f8 word', c >> 13 == 6 and 8+((c >> 7)&7) == 15 and 8+((c >> 2)&7) == 14 and off == 0x78)
check('association API target', jal(0xa006d064) == 0xa0075d6a)
check('association result s2', u(0xa006d068) == 0x892a)
check('separate DHCP result s5', u(0xa006d1a8) == 0x8aaa)
check('DHCP request API', jal(0xa006d1a4) == 0xa00992d2)
check('stage final tests s2', 's2' in ins[0xa006d0c2].op_str)
check('down LW same global', (u(0xa006722c) & 0xfffff000) + signed(u(0xa0067230) >> 20, 12) == 0x62fc99e4 and (u(0xa0067230)>>12)&7 == 2)
check('down interrupt target', jal(0xa0067236) == 0xa0098a98)
check('helper global address', (u(0xa005face)&0xfffff000) + signed(u(0xa005fad2)>>20,12) == 0x62fc99e4)
check('helper API target distinct from interrupt', jal(0xa005fada) == 0xa0098af0)
check('helper clears whole word after API returns', u(0xa005fade) == 0x0004a023)
check('success uses cleanup helper', jal(0xa006d24a) == 0xa005fac4)
records = json.loads((ROOT/'evidence/rea-0041-20261017/evidence/upper-complete.evidence.json').read_text(encoding='utf-8'))['records']
sources = []
for index in (248,273,252,89):
    r = records[index]
    sources.append(dict(record=index, evidence_id=r['evidence_id'], profile=r['analysis_profile']['digest']))
result = dict(claim='Q-06', status='independent bounded review', windows=windows, byte_count=sum(b-a for a,b in spans), checks=checks, sources=sources,
              source_identity='6769704 B; inherited SHA256 972db4c136c7ed9e24a83c07c1a7fd62040ca018b08ca285216d26b1fee3c6b9; no full hash',
              limitations=['static only','no target or author verifier execution','no public API internals','profile/EID remain source-specific'])
(OUT/'verification.json').write_text(json.dumps(result, indent=2)+'\n',encoding='utf-8')
for w in windows:
    print('\n'.join(w['instructions']))
print(f'{len(checks)} checks PASS; {result["byte_count"]} bytes')
