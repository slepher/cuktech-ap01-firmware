"""Bounded static H01 extraction. Reads ROM/Evidence; never executes firmware."""
import json
from pathlib import Path
import capstone

HERE = Path(__file__).resolve().parent
MAIN = Path('D:/Documents/PlatformIO/Projects/cuktech-ap01-firmware')
SOURCE = MAIN / 'evidence/rea-0041-20261017/evidence'
ROM = MAIN / 'roms/0041/ap01-1.0.2_0041.bin'
BASE = 0x9ffff000
image = ROM.read_bytes()

def evidence(index):
    path = SOURCE / f'whole-rom-private-20261023-{index:03}.json'
    record = json.loads(path.read_text(encoding='utf-8-sig'))
    e = record.get('structuredContent') or json.loads(record['content'][0]['text'])
    return path, e

retained = []
for index in [94, 95, 96, 98, 100, 101]:
    path, e = evidence(index)
    n = e['normalized_result']
    # Whole constructor UI creation is outside H01. Retain only the ownership
    # prerequisites and final registration/linkage, with the exact body metadata.
    if index == 101:
        assembly = [s for s in n['assembly'] if int(s.split(':')[0], 16) < 0xa00b82b2
                    or int(s.split(':')[0], 16) >= 0xa00b8bb4]
        pseudo = None
    else:
        assembly, pseudo = n['assembly'], n['pseudocode']
    retained.append(dict(source=str(path), evidence_id=e['evidence_id'],
        authority=e['authority'], confidence=e['confidence'],
        analysis_profile=e['analysis_profile'], procedure=n['procedure'],
        assembly=assembly, pseudocode=pseudo, limitations=e['limitations']))

spans = [
    ('constructor-ownership-prefix', 0xa00b821e, 0xa00b82b2),
    ('constructor-registration-and-delete-hook', 0xa00b8bb4, 0xa00b8bfc),
    ('registration', 0xa00b3a68, 0xa00b3abe),
    ('unregistration', 0xa00b3abe, 0xa00b3b26),
    ('delete-hook-unindexed-entry', 0xa00b3b26, 0xa00b3be6),
    ('dispatch-contract', 0xa00b3c14, 0xa00b3c26),
    ('update-consumer', 0xa00b564e, 0xa00b59c4),
    ('normalization', 0xa00b5b58, 0xa00b5cd4),
    ('callback-unindexed-entry', 0xa00b5cd4, 0xa00b5cec),
    ('weekday-short-dependency', 0xa00eeae6, 0xa00eeb3a),
]
md = capstone.Cs(capstone.CS_ARCH_RISCV,
                 capstone.CS_MODE_RISCV32 | capstone.CS_MODE_RISCVC)
# Vendor instructions are not silently skipped or reclassified as terminal.
# These exact words are checked below using the existing private model's
# indexed-load/store operand fields; no model/ROM is modified.
custom = {
    0xa00b58c8: 'th.extu a5,a5,15,0',
    0xa00b5930: 'th.lrw s5,a5,s3,2',
    0xa00b596e: 'th.lrhu a2,s8,s3,3',
    0xa00b597e: 'th.lrhu a2,s9,s3,3',
    0xa00b598a: 'th.lrw a2,s7,a2,2',
    0xa00b5998: 'th.lrw a1,s11,s3,2',
    0xa00b59ac: 'th.lrh a2,a4,s3,1',
    0xa00b59be: 'th.lrh a2,a5,s3,1',
    0xa00b5c72: 'th.srw a5,s5,s2,1',
}
windows = []
insns = {}
source_assembly = {int(s.split(':')[0],16):s.split(': ',1)[1]
                   for record in retained for s in record['assembly']}
for name, start, end in spans:
    rows = []
    at = start
    while at < end:
        data = image[at-BASE:end-BASE]
        if at in custom:
            size, text = 4, custom[at]
            assert int.from_bytes(data[:4], 'little') & 0x7f == 0xb
        else:
            decoded = next(md.disasm(data, at, count=1), None)
            if decoded is None:
                text = source_assembly.get(at, '')
                assert text.startswith('th.') and int.from_bytes(data[:4], 'little') & 127 == 11, hex(at)
                custom[at] = text
                size = 4
            else:
                size, text = decoded.size, decoded.mnemonic + ' ' + decoded.op_str
        row = dict(address=hex(at), bytes=data[:size].hex(), text=text.strip(),
                   decoder='explicit-vendor-fields' if at in custom else 'capstone-5.0.7')
        insns[at] = row
        rows.append(row)
        at += size
    assert at == end
    windows.append(dict(name=name, start=hex(start), end_exclusive=hex(end),
                        file_offset=start-BASE, instructions=rows))

checks = []
def word(at):
    return int.from_bytes(image[at-BASE:at-BASE+4], 'little')

def jal(at, target):
    w = word(at)
    assert w & 0x7f == 0x6f and (w >> 7) & 31 == 1
    delta = ((w >> 31) << 20) | (((w >> 12) & 255) << 12)
    delta |= ((w >> 20) & 1) << 11 | ((w >> 21) & 1023) << 1
    if delta & 0x100000: delta -= 0x200000
    assert at + delta == target
    checks.append(dict(kind='raw-jal', address=hex(at), target=hex(target)))

for at, target in [(0xa00b8bc2,0xa00b3a68),(0xa00b8bf4,0xa01ad654),
                   (0xa00b5cde,0xa00b5b58),(0xa00b5c82,0xa00b564e),
                   (0xa00b3bca,0xa00b3abe),(0xa00b3bd0,0xa008ab8a),
                   (0xa00b5740,0xa0190da4),(0xa00b5882,0xa00a6afa),
                   (0xa00b59a0,0xa00a6afa)]:
    jal(at,target)

def memory(at, opcode, funct3, reg, base, offset):
    w = word(at)
    assert w & 127 == opcode and (w >> 12) & 7 == funct3
    assert (w >> 15) & 31 == base
    if opcode == 3:
        assert (w >> 7) & 31 == reg
        imm = w >> 20
    else:
        assert (w >> 20) & 31 == reg
        imm = ((w >> 25) << 5) | ((w >> 7) & 31)
    if imm & 0x800: imm -= 0x1000
    assert imm == offset
    checks.append(dict(kind='raw-memory', address=hex(at), opcode=opcode,
                       funct3=funct3, register=reg, base=base, offset=offset))

# Weather read signedness and the cleanup's complete word-clear set.
for args in [(0xa00b56b8,3,1,12,12,12),(0xa00b56e6,3,1,13,18,10),
             (0xa00b56ea,3,1,12,18,8),(0xa00b56fc,3,1,12,18,6),
             (0xa00b5736,3,5,11,18,28),(0xa00b5772,3,5,19,18,24),
             (0xa00b57ae,3,5,12,18,22),(0xa00b57cc,3,5,19,18,26),
             (0xa00b3bd4,35,2,0,9,16),(0xa00b8be6,35,2,20,9,16)]:
    memory(*args)
clear_offsets = [0x18,0x30,0x40,0x38,4,12,0x34,0x10,0x44,0x48,
                 0x1c,0x20,0x3c,8,0x24,0,0x2c,0x28,0x14,0x4c,
                 0x50,0x54,0x58,0x5c,0x60,0x64,0x68,0x6c]
for j, off in enumerate(clear_offsets):
    memory(0xa00b3b56+j*4,35,2,0,15,off)
assert sorted(clear_offsets) == list(range(0,0x70,4))

# Confirm exact callback constants and both ownership operations. These are
# literal byte checks, independent of Ghidra's missing callback prototypes.
for at, raw in {
    0xa00b8bb4:'37650ba0', 0xa00b8bb8:'a685', 0xa00b8bbe:'130545cd',
    0xa00b3b50:'37650ba0', 0xa00b3b54:'a685', 0xa00b3bc6:'130545cd',
}.items():
    assert image[at-BASE:at-BASE+len(raw)//2].hex() == raw, hex(at)
    checks.append(dict(kind='literal-bytes', address=hex(at), bytes=raw))

# T-Head indexed operations: opcode, destination/source, base and index fields;
# preserve exact word and existing-model shift in the output for independent QA.
vendor_fields = [
    (0xa00b5c72,15,21,18,1), (0xa00b5930,21,15,19,2),
    (0xa00b596e,12,24,19,3), (0xa00b597e,12,25,19,3),
    (0xa00b598a,12,23,12,2), (0xa00b5998,11,27,19,2),
    (0xa00b59ac,12,14,19,1), (0xa00b59be,12,15,19,1),
]
for at, rd, rs1, rs2, shift in vendor_fields:
    w = word(at)
    assert w & 127 == 11
    assert (w >> 7) & 31 == rd and (w >> 15) & 31 == rs1
    assert (w >> 20) & 31 == rs2 and (w >> 25) & 3 == shift
    kind = 'srw' if at == 0xa00b5c72 else ('lrhu' if at in [0xa00b596e,0xa00b597e]
            else ('lrh' if at in [0xa00b59ac,0xa00b59be] else 'lrw'))
    assert (w >> 12) & 7 == (5 if kind == 'srw' else 4)
    assert w >> 27 == {'srw':8,'lrw':8,'lrhu':20,'lrh':4}[kind]
    checks.append(dict(kind='vendor-indexed-fields', address=hex(at),
                       word=hex(w), reg=rd, base=rs1,index=rs2,shift=shift))
w = word(0xa00b58c8)
assert w & 127 == 11 and (w >> 12) & 7 == 3
assert (w >> 7) & 31 == 15 and (w >> 15) & 31 == 15
assert w >> 26 == 15 and (w >> 20) & 63 == 0
checks.append(dict(kind='vendor-extu-fields',address='0xa00b58c8',word=hex(w),
                   destination=15,source=15,msb=15,lsb=0))

model = MAIN/'evidence/rea-0041-20261017/ghidra/Ghidra/Processors/RISCV/data/languages/ap01thead2.sinc'
lines = model.read_text().splitlines()
starts = [i for i,s in enumerate(lines) if any(s.startswith(prefix) for prefix in
          [':th.extu rd,rs1,15,0 ',':th.lrw ',':th.lrhu ',':th.lrh ',':th.srw '])]
snippets = []
for i in starts:
    end = next(j for j in range(i+1,len(lines)) if lines[j] == '}')
    snippets.append(dict(line=i+1,text='\n'.join(lines[i:end+1])))
(HERE/'vendor-model-excerpts.json').write_text(json.dumps(dict(source=str(model),
    snippets=snippets),ensure_ascii=False,indent=2),encoding='utf-8')

(HERE/'retained-functions.json').write_text(json.dumps(retained,ensure_ascii=False,indent=2),encoding='utf-8')
(HERE/'instruction-evidence.json').write_text(json.dumps(dict(
    rom=str(ROM), mapping_base=hex(BASE), windows=windows, checks=checks,
    limitations=['No runtime observation; no slot-success assertion.',
                 'Constructor UI rendering and generic toolkit deletion are outside H01.',
                 'Vendor mnemonics use the retained AP01 private profile; fields checked independently.']),
    ensure_ascii=False,indent=2),encoding='utf-8')
print(json.dumps(dict(status='pass', windows=len(windows),
                      instructions=len(insns), checks=len(checks),
                      retained_procedures=len(retained))))
