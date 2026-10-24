"""Independent offline RV32/RVC source decoding; never executes firmware."""
import hashlib
import json
from pathlib import Path
from capstone import Cs, CS_ARCH_RISCV, CS_MODE_RISCV32, CS_MODE_RISCVC

ROOT = Path(r'D:/Documents/PlatformIO/Projects/cuktech-ap01-firmware')
OUT = Path(__file__).parent
rom = (ROOT / 'roms/0041/ap01-1.0.2_0041.bin').read_bytes()
assert len(rom) == 6769704
assert hashlib.sha256(rom).hexdigest() == '972db4c136c7ed9e24a83c07c1a7fd62040ca018b08ca285216d26b1fee3c6b9'
decoder = Cs(CS_ARCH_RISCV, CS_MODE_RISCV32 | CS_MODE_RISCVC)
rows = []
for lo, hi in [(0xa00ab2e8, 0xa00ab434), (0xa00a3a96, 0xa00a3ab6), (0xa00ab274, 0xa00ab2e8)]:
    raw = rom[lo - 0x9ffff000:hi - 0x9ffff000]
    decoded = list(decoder.disasm(raw, lo))
    assert sum(i.size for i in decoded) == len(raw)
    rows.extend(dict(address=hex(i.address), raw=i.bytes.hex(), mnemonic=i.mnemonic, operands=i.op_str) for i in decoded)
by = {int(r['address'], 16): r for r in rows}
checks = []
def instruction(address, mnemonic, operands):
    r = by[address]
    assert (r['mnemonic'], r['operands']) == (mnemonic, operands), r
    checks.append(hex(address))

for a, m, o in [
    (0xa00ab306,'c.li','a4, 8'), (0xa00ab308,'addi','a1, zero, 0x64'),
    (0xa00ab310,'sw','zero, 4(a5)'), (0xa00ab314,'sw','zero, 8(a5)'), (0xa00ab318,'c.sw','a4, 0(a5)'),
    (0xa00ab336,'c.mv','s4, a0'), (0xa00ab348,'beqz','s4, 0xd0'),
    (0xa00ab34c,'c.mv','a3, s4'), (0xa00ab34e,'c.li','a2, 1'), (0xa00ab350,'c.li','a1, 8'),
    (0xa00ab35e,'lhu','a6, 6(s1)'), (0xa00ab364,'bne','a0, a6, 0x96'),
    (0xa00ab382,'c.li','s5, 1'), (0xa00ab384,'c.mv','a0, s4'), (0xa00ab38a,'bnez','s5, 0x26'),
    (0xa00ab414,'c.li','s5, 0'), (0xa00ab416,'c.j','-0x92'), (0xa00ab432,'c.j','-0xa4'),
    (0xa00a3a9c,'lui','a5, 0x62fc9'), (0xa00a3aa0,'sw','zero, 0x98(a5)'),
    (0xa00a3aa4,'addi','a4, zero, 0x164'), (0xa00a3aa8,'addi','a5, a5, 0x98'), (0xa00a3aac,'sh','a4, 4(a5)'),
    (0xa00ab292,'c.bnez','a0, 0x2e'), (0xa00ab2c0,'c.mv','s1, a0'),
    (0xa00ab2ce,'sh','a0, 6(a4)'), (0xa00ab2e0,'c.mv','a0, s1')]:
    instruction(a,m,o)

calls = {}
for a, target in [(0xa00ab332,0xa0134856),(0xa00ab356,0xa0132acc),(0xa00ab35a,0xa00a46e8),
                  (0xa00ab386,0xa01a8de6),(0xa00ab3a8,0xa00a3a96),(0xa00ab3ac,0xa00ab274),
                  (0xa00ab28e,0xa0134856),(0xa00ab2c2,0xa00a46e8),(0xa00ab2dc,0xa0134adc),(0xa00ab2e2,0xa01a8de6)]:
    r = by[a]
    assert r['mnemonic'] == 'jal' and a + int(r['operands'], 0) == target
    calls[hex(a)] = hex(target)
assert 0xa00ab31a + 0x107000 + 0x15a == 0xa01b2474
for address, string in [(0xa026a218,b'wb\0'),(0xa026a21c,b'/data/sysconfig.bin\0'),(0xa026a258,b'rb\0')]:
    assert rom[address-0x9ffff000:address-0x9ffff000+len(string)] == string
retained = []
for suffix, lo, size in [('072',0xa00ab2e8,332),('071',0xa00ab274,116)]:
    p = ROOT / f'evidence/rea-0041-20261017/evidence/whole-rom-private-20261023-{suffix}.json'
    j = json.loads(p.read_text(encoding='utf-8'))
    n = j['structuredContent']['normalized_result']
    assert n['procedure']['address'] == hex(lo) and n['procedure']['body']['total_bytes'] == size
    assert [int(line.split(':')[0],16) for line in n['assembly']] == sorted(a for a in by if lo <= a < lo+size)
    retained.append({'path':str(p),'evidence_id':json.loads(j['content'][0]['text'])['evidence_id'],'assembly':n['assembly']})
result = dict(status='PASS',rom_sha256=hashlib.sha256(rom).hexdigest(),decode='Capstone 5.0.7 RV32+RVC',
              instruction_checks=checks,call_targets=calls,raw_decode=rows,retained=retained,
              target_execution=False,author_script_executed=False,algorithm_evaluations=0)
(OUT/'result.json').write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
print('PASS: independent whole-window static decode and focused control/resource checks')
