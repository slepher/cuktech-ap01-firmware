"""Independent, bounded static byte/ABI checks; does not execute target code."""
import argparse
import hashlib
import json
from pathlib import Path
import capstone

p = argparse.ArgumentParser()
p.add_argument("main", type=Path)
p.add_argument("author_analysis", type=Path)
a = p.parse_args()
rom = (a.main / "roms/0041/ap01-1.0.2_0041.bin").read_bytes()
assert len(rom) == 6769704
windows = json.loads((a.author_analysis / "windows.json").read_text())
expected = [(0xa00bb67e,92),(0xa00be8ca,430),(0xa00bea78,404),
            (0xa00bb0c2,26),(0xa00bb0dc,26),(0xa00bb6da,308),(0xa01adc0e,96)]
assert [(int(w['va'],16),w['length']) for w in windows] == expected
md = capstone.Cs(capstone.CS_ARCH_RISCV, capstone.CS_MODE_RISCV32 | capstone.CS_MODE_RISCVC)
decoded, unknown, summary = {}, {}, []
for w in windows:
    va = int(w['va'],16)
    offset = va - 0x9ffff000
    raw = rom[offset:offset+w['length']]
    assert offset == w['offset'] and raw.hex() == w['hex']
    digest = hashlib.sha256(raw).hexdigest()
    assert digest == w['sha256']
    cursor = 0
    while cursor < len(raw):
        ins = next(md.disasm(raw[cursor:],va+cursor, count=1),None)
        if ins:
            decoded[ins.address] = (ins.mnemonic,ins.op_str)
            cursor += ins.size
        else:
            assert raw[cursor] & 3 == 3
            unknown[va+cursor] = raw[cursor:cursor+4].hex()
            cursor += 4
    assert cursor == len(raw)
    summary.append(dict(va=hex(va),length=len(raw),sha256=digest))
assert unknown == {0xa00be922:'8bc92a45',0xa00be940:'8bc9fa44',
                   0xa00be95e:'8bcb3a45',0xa00be980:'0bc53a45'}
# Anchors are independently read from ROM, not parsed from author's text dump.
anchors = {
    0xa00bb690:('addi','a1, zero, 0x54'),
    0xa00bb6aa:('addi','a2, zero, 0x48'),
    0xa00bb6b0:('c.addi','a0, 8'),
    0xa01adc30:('lw','a7, 0x24(a1)'),
    0xa01adc3c:('lw','a7, 0x38(a1)'),
    0xa01adc48:('lw','a7, 0x3c(a1)'),
    0xa01adc58:('c.sw','a2, 0x50(a5)'),
    0xa01adc5c:('c.sw','a4, 0x4c(a5)'),
    0xa01adc60:('c.sw','a4, 0x48(a5)'),
    0xa00bea3e:('c.lw','a5, 0x64(s1)'),
    0xa00bea40:('c.lw','a1, 0x68(s1)'),
    0xa00bea4e:('c.jalr','a5'),
    0xa00beb60:('lw','a5, 0x64(s3)'),
    0xa00beb64:('lw','a1, 0x68(s3)'),
    0xa00beb74:('c.jalr','a5'),
    0xa00bb7de:('sw','zero, 0x4c(s1)'),
    0xa00bb7e2:('sw','zero, 0x48(s1)'),
}
for address, instruction in anchors.items():
    assert decoded[address] == instruction,(hex(address), decoded[address])
records = json.loads((a.main/'evidence/rea-0041-20261017/evidence/upper-complete.evidence.json').read_text())['records']
links = json.loads((a.author_analysis/'parent-links.json').read_text())
for index, link in zip((59,164),links):
    record = records[index]
    assert record['evidence_id'] == link['evidence_id']
    assert record['analysis_profile']['digest'] == link['profile_digest']
    assembly = record['normalized_result']['assembly']
    assert any('addi s5, a0, 0x228' in line for line in assembly)
    assert any('0xa00bb67e' in line for line in assembly)
    assert any('0xa00bb80e' in line for line in assembly)
result = {'result':'PASS','windows':summary,'bytes':sum(n for _,n in expected),
          'anchor_checks':len(anchors),'vendor_words_unknown':{hex(k):v for k,v in unknown.items()},
          'parent_records':[59,164],'target_execution':False}
(Path(__file__).parent/'review-results.json').write_text(json.dumps(result,indent=2)+'\n')
print('PASS: 7 windows / 1382 bytes, 17 raw instruction anchors, 2 parent links; 4 vendor words remain unknown')
