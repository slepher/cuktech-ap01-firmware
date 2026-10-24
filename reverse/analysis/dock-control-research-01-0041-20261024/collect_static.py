"""Q-02: read-only ROM checks; writes only this task's evidence."""
import json
from pathlib import Path
from capstone import Cs, CS_ARCH_RISCV, CS_MODE_RISCV32, CS_MODE_RISCVC

ROOT = Path(__file__).resolve().parents[3]
OUT = Path(__file__).resolve().parent
source = ROOT / 'reverse/analysis/uiiface-lifecycle-0041-20261023/retained-initializer.json'
f = json.loads(source.read_text(encoding='utf-8'))['function']
rom = (ROOT / 'roms/0041/ap01-1.0.2_0041.bin').read_bytes()
assert len(rom) == 6769704
base = 0x9ffff000
old = {int(x.split(':')[0], 16): x for x in f['assembly']}
md = Cs(CS_ARCH_RISCV, CS_MODE_RISCV32 | CS_MODE_RISCVC)
windows = [(0xa00a8582, 0xa00a85ac), (0xa00a8602, 0xa00a860a),
           (0xa00a88f6, 0xa00a8a82), (0xa00a8aca, 0xa00a8b50)]
rows = []
for lo, hi in windows:
    pos = lo
    while pos < hi:
        half = int.from_bytes(rom[pos-base:pos-base+2], 'little')
        size = 4 if half & 3 == 3 else 2
        assert pos + size <= hi and pos in old
        raw = rom[pos-base:pos-base+size]
        rr = next(r for r in f['raw_ranges'] if int(r['start'],16) <= pos and pos+size <= int(r['end'],16)+1)
        off = pos-int(rr['start'],16)
        assert raw == bytes.fromhex(rr['hex'])[off:off+size]
        decoded = list(md.disasm(raw, pos))
        custom = size == 4 and raw[0] & 0x7f == 0x0b
        assert custom or (len(decoded) == 1 and decoded[0].size == size)
        rows.append({'va':hex(pos), 'offset':pos-base, 'hex':raw.hex(),
                     'retained':old[pos], 'independent':None if custom else decoded[0].mnemonic+' '+decoded[0].op_str,
                     'custom_word':custom})
        pos += size

# Key dataflow checkpoints, separately tied to retained assembly and ROM above.
expected = {
    0xa00a85a8:'sw a2, -0x4c, s0',
    0xa00a88fe:'c.li a1, 0x18', 0xa00a8904:'jal ra, 0xa0191652',
    0xa00a8950:'lbu a7, 0x16, a5', 0xa00a8966:'beq a7, a4, 0xa00a8a22',
    0xa00a898e:'sb a7, 0x1c, s2', 0xa00a8996:'lbu a0, 0x1c, s2',
    0xa00a8a22:'lbu s3, 0x1c, s2', 0xa00a8a26:'jal ra, 0xa00a3d22',
    0xa00a8a36:'sw a0, 0x2cc, s4', 0xa00a8a3c:'c.beqz a0, 0xa00a8a82',
    0xa00a8a5c:'lw s2, -0x4c, s0', 0xa00a8a62:'c.addi s2, 0x17',
    0xa00a8a64:'andi a1, s1, 0xff', 0xa00a8a6c:'bltu a1, s3, 0xa00a8aca',
    0xa00a8a70:'sb s3, 0x6, a3', 0xa00a8b26:'sb a1, 0x13, a2',
    0xa00a8b4c:'c.addi s1, 0x1', 0xa00a8b4e:'c.j 0xa00a8a64',
}
for va, asm in expected.items():
    assert old[va].split(': ',1)[1] == asm, (hex(va), old[va])

# The indexed-byte operations are inherited P16 semantics, not a new ISA proof.
indexed = []
for va in [0xa00a8ad0,0xa00a8aea,0xa00a8b02]:
    word = int.from_bytes(rom[va-base:va-base+4], 'little')
    fields = {'opcode':word&127,'rd':(word>>7)&31,'f3':(word>>12)&7,
              'rs1':(word>>15)&31,'rs2':(word>>20)&31,'upper':word>>25}
    assert fields['opcode']==11 and fields['rd']==15
    assert fields['rs1']==9 and fields['rs2']==18
    indexed.append({'va':hex(va),'word':hex(word),'fields':fields})

contract = {
    'entry':{'command':85,'payload':'entry a2, saved at frame-0x4c',
             'fixed_cache':{'address':'0x62fcb004','bytes':24},
             'count_source':'cached byte at +0x16; ff preserves prior 0x62fcb01c',
             'descriptor_source':'original payload + 0x17 + i'},
    'valid_source_requirement':'24 readable prefix bytes, and N readable descriptor bytes starting +23; stable through synchronous initialization',
    'input_extent_when_N_positive':'at least max(24,23+N) readable bytes; this is a reconstruction precondition, not a recovered length check',
    'identity_requirement':{'i0':'type0,nibble0','i1':'type0,nibble1','i2':'type0,nibble2','i3':'type1,any nibble','i4':'type2,any nibble'},
    'actual_values':'not present in selected static evidence; no observed remote payload',
    'status':'author delivery, awaiting non-author review',
}
evidence = {'rom_sha256_inherited':'972db4c136c7ed9e24a83c07c1a7fd62040ca018b08ca285216d26b1fee3c6b9',
            'source':str(source.relative_to(ROOT)), 'evidence_id':f['evidence_id'],
            'profile_digest':f['profile']['digest'], 'windows':[[hex(a),hex(b)] for a,b in windows],
            'window_bytes':sum(b-a for a,b in windows),'instruction_count':len(rows),
            'key_checkpoints':len(expected),'instructions':rows,'indexed_fields':indexed,'contract':contract}
(OUT/'static-evidence.json').write_text(json.dumps(evidence,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
print(json.dumps({'result':'PASS','bytes':evidence['window_bytes'],'instructions':len(rows),'checkpoints':len(expected)},ensure_ascii=False))
