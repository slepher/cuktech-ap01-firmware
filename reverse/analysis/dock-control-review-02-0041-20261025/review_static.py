"""Independent bounded ROM review; never imports the author's collector."""
import json
from pathlib import Path
from capstone import Cs, CS_ARCH_RISCV, CS_MODE_RISCV32, CS_MODE_RISCVC

ROOT = Path(__file__).resolve().parents[3]
OUT = Path(__file__).resolve().parent
rom = (ROOT / 'roms/0041/ap01-1.0.2_0041.bin').read_bytes()
assert len(rom) == 6769704
init = json.loads((ROOT / 'reverse/analysis/uiiface-lifecycle-0041-20261023/retained-initializer.json').read_text())['function']
helper = json.loads((ROOT / 'reverse/analysis/uart-response-0041-20261023.json').read_text())['functions'][1]
assert init['evidence_id'] == 'ev_6f9f82e5daf0540a1c24a0b85daa2e394785391692765e5e3e100eb7b37ed94c'
assert init['profile']['digest'] == 'bcefdee5092076e55636e077b45523e203f4b870ae7b7ab547945ed1b8162279'
assert helper['profile_digest'] == 'b6368dd18431e8113aa5026c713d41e648ab0f6ddd9421ff6c4a49e23b3cd2f3'
md = Cs(CS_ARCH_RISCV, CS_MODE_RISCV32 | CS_MODE_RISCVC)
records = []
for source, windows in [(init, [(0xa00a85a0, 0xa00a85ac), (0xa00a8602, 0xa00a860a), (0xa00a88f6, 0xa00a8b50)]),
                        (helper, [(0xa0191692, 0xa01916d2)])]:
    assembly = source.get('assembly', source.get('normalized_result', {}).get('assembly'))
    lines = {int(line.split(':')[0], 16): line for line in assembly}
    for start, end in windows:
        raw = rom[start - 0x9ffff000:end - 0x9ffff000]
        rr = next(r for r in source['raw_ranges'] if int(r['start'],16) <= start and int(r['end'],16) >= end-1)
        offset = start - int(rr['start'],16)
        assert raw == bytes.fromhex(rr['hex'])[offset:offset+len(raw)]
        addr = start
        while addr < end:
            off = addr-start
            half = int.from_bytes(raw[off:off+2], 'little')
            size = 4 if half & 3 == 3 else 2
            assert addr in lines and addr+size <= end
            bs = raw[off:off+size]
            decoded = list(md.disasm(bs, addr))
            records.append({'address':hex(addr),'raw':bs.hex(),'retained':lines[addr],
                            'standard_decode': [(i.mnemonic+' '+i.op_str).strip() for i in decoded]})
            addr += size

# Critical dataflow verified using raw standard encodings, separate from retained prose.
byaddr = {int(r['address'],16):r for r in records}
expect = {0xa00a85a8: 'sw a2, -0x4c(s0)', 0xa00a88fe:'c.li a1, 0x18',
          0xa00a8a5c:'lw s2, -0x4c(s0)', 0xa00a8a62:'c.addi s2, 0x17',
          0xa00a8950:'lbu a7, 0x16(a5)', 0xa00a898e:'sb a7, 0x1c(s2)',
          0xa00a8a22:'lbu s3, 0x1c(s2)', 0xa00a8a70:'sb s3, 6(a3)',
          0xa00a8b26:'sb a1, 0x13(a2)'}
for addr, expected in expect.items():
    assert byaddr[addr]['standard_decode'] == [expected], (hex(addr),byaddr[addr],expected)
# Vendor loads: raw fields only; semantics inherit P16/Q review.
for addr in (0xa00a8ad0,0xa00a8aea,0xa00a8b02):
    word = int.from_bytes(bytes.fromhex(byaddr[addr]['raw']), 'little')
    assert ((word>>7)&31, (word>>15)&31, (word>>20)&31) == (15,9,18)
result={'result':'PASS','rom_size':len(rom),'source_identity':{'initializer':init['source'], 'helper':helper['source']},
        'windows':4,'bytes':sum(len(bytes.fromhex(r['raw'])) for r in records),'instruction_boundaries':len(records),
        'critical_standard_assertions':len(expect),'vendor_register_field_assertions':3,'records':records,
        'limitations':'No execution. Custom semantics inherited. No author script imported; no whole-ROM search/hash.'}
(OUT/'review-evidence.json').write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
print({k:result[k] for k in ('result','windows','bytes','instruction_boundaries','critical_standard_assertions','vendor_register_field_assertions')})
