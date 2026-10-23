"""A20 independent static-byte review. Never execute or emulate target code."""
from pathlib import Path
import json
import struct
import capstone

OUT = Path(__file__).resolve().parent
SOURCE = Path('D:/Documents/PlatformIO/Projects/cuktech-ap01-firmware')
PREDECESSOR = OUT.parent / 'weather-icon-flow-a19-0041-20261023/instruction-evidence.json'
ROM = SOURCE / 'roms/0041/ap01-1.0.2_0041.bin'
image = ROM.read_bytes()

def read(address, size):
    offset = address - 0xa0000000 + 0x1000
    assert 0 <= offset <= len(image) - size
    return image[offset:offset + size]

def word(address, size=4):
    return int.from_bytes(read(address, size), 'little')

def signed(value, bits):
    return value - (1 << bits) if value & (1 << (bits - 1)) else value

def fields(address):
    """Raw RV32/RVC field extraction, independent of disassembler text."""
    h = word(address, 2)
    if h & 3 == 3:
        w = word(address)
        op, rd, f3, r1, r2, f7 = w & 127, (w >> 7) & 31, (w >> 12) & 7, (w >> 15) & 31, (w >> 20) & 31, w >> 25
        if op in (3, 19, 103):
            return ['I', op, f3, rd, r1, signed(w >> 20, 12)]
        if op == 35:
            return ['S', f3, r2, r1, signed(((w >> 25) << 5) | ((w >> 7) & 31), 12)]
        if op == 99:
            imm = ((w >> 31) << 12) | (((w >> 7) & 1) << 11) | (((w >> 25) & 63) << 5) | (((w >> 8) & 15) << 1)
            return ['B', f3, r1, r2, hex(address + signed(imm, 13))]
        if op == 111:
            imm = ((w >> 31) << 20) | (((w >> 12) & 255) << 12) | (((w >> 20) & 1) << 11) | (((w >> 21) & 1023) << 1)
            return ['J', rd, hex(address + signed(imm, 21))]
        if op in (23, 55):
            return ['U', op, rd, hex(w & 0xfffff000)]
        return ['R', op, f3, f7, rd, r1, r2]
    quadrant, f3 = h & 3, h >> 13
    if quadrant == 0 and f3 in (2, 6):
        imm = (((h >> 5) & 1) << 6) | (((h >> 10) & 7) << 3) | (((h >> 6) & 1) << 2)
        return ['C.memory', f3, 8 + ((h >> 2) & 7), 8 + ((h >> 7) & 7), imm]
    if quadrant == 1 and f3 in (6, 7):
        imm = (((h >> 12) & 1) << 8) | (((h >> 10) & 3) << 3) | (((h >> 5) & 3) << 6) | (((h >> 3) & 3) << 1) | (((h >> 2) & 1) << 5)
        return ['C.branch', f3, 8 + ((h >> 7) & 7), hex(address + signed(imm, 9))]
    if quadrant == 1 and f3 in (1, 5):
        imm = (((h >> 12) & 1) << 11) | (((h >> 11) & 1) << 4) | (((h >> 9) & 3) << 8) | (((h >> 8) & 1) << 10) | (((h >> 7) & 1) << 6) | (((h >> 6) & 1) << 7) | (((h >> 3) & 7) << 1) | (((h >> 2) & 1) << 5)
        return ['C.jump', f3, hex(address + signed(imm, 12))]
    if quadrant == 1 and f3 == 4 and ((h >> 10) & 3) == 3 and ((h >> 12) & 1) == 0:
        return ['C.ALU', (h >> 5) & 3, 8 + ((h >> 7) & 7), 8 + ((h >> 2) & 7)]
    if quadrant == 2 and f3 == 4:
        return ['C.CR', (h >> 12) & 1, (h >> 7) & 31, (h >> 2) & 31]
    return ['C.raw', hex(h)]

ranges = [
    ('constructor glue', 0xa00a5d5c, 0xa00a5da8),
    ('code mapper', 0xa00a6998, 0xa00a6afa),
    ('icon selector', 0xa0198946, 0xa0198a9e),
    ('remove flag', 0xa00d9044, 0xa00d9110),
    ('add flag', 0xa00d8f7c, 0xa00d9044),
    ('classifier', 0xa00dd454, 0xa00dd482),
    ('info wrapper', 0xa0082e32, 0xa0082e76),
    ('info dispatcher', 0xa0082c8c, 0xa0082e32),
    ('source setter', 0xa00ed560, 0xa00ed7f4),
    ('size sentinel', 0xa01b1ee6, 0xa01b1f2c),
    ('scale update', 0xa00ed438, 0xa00ed560),
    ('all flag predicate', 0xa00d7446, 0xa00d749e),
    ('any flag predicate', 0xa00d749e, 0xa00d74f4),
    ('state predicate correcting A19 call target', 0xa00d7546, 0xa00d759e),
    ('widget production slice', 0xa00a7f7e, 0xa00a7f9e),
    ('two conversions slice', 0xa00aa58a, 0xa00aa5e2),
    ('callback contract', 0xa00ab6b0, 0xa00ab754),
]
vendor = {0xa00ed5f8: 'th.extu a5,a5,15,0', 0xa00ed6c0: 'th.extu a5,a5,15,0', 0xa00ed748: 'th.extu a5,a5,15,0', 0xa00ed4f2: 'th.mvnez a2,s2,a5'}
md = capstone.Cs(capstone.CS_ARCH_RISCV, capstone.CS_MODE_RISCV32 | capstone.CS_MODE_RISCVC)
windows, by_address = [], {}
for name, lo, hi in ranges:
    rows = []
    address = lo
    while address < hi:
        size = 4 if word(address, 2) & 3 == 3 else 2
        raw = read(address, size)
        decoded = list(md.disasm(raw, address))
        if address in vendor:
            assert not decoded
            text = vendor[address]
        else:
            assert len(decoded) == 1 and decoded[0].size == size, hex(address)
            text = decoded[0].mnemonic + ' ' + decoded[0].op_str
        row = dict(address=hex(address), file_offset=address-0xa0000000+0x1000, bytes=raw.hex(), instruction=text, raw_fields=fields(address))
        rows.append(row)
        by_address[address] = row
        address += size
    assert address == hi
    windows.append(dict(name=name, start=hex(lo), end_exclusive=hex(hi), rows=rows))

# Full predecessor byte comparison is corroboration, never the semantic oracle.
previous = json.loads(PREDECESSOR.read_text(encoding='utf-8'))
matched = 0
for window in previous['windows']:
    for row in window['rows']:
        address = int(row['address'], 16)
        assert by_address[address]['bytes'] == row['bytes'], row['address']
        matched += 1

checks = []
def expect(address, expected, meaning):
    actual = fields(address)
    assert actual == expected, (hex(address), actual, expected)
    checks.append(dict(address=hex(address), bytes=by_address[address]['bytes'], fields=actual, meaning=meaning))

calls = {
    0xa00aa5d0:0xa0053f46, 0xa00aa5da:0xa0053f46, 0xa00ab714:0xa0198946,
    0xa00a7f96:0xa00a5d5c, 0xa00a5d74:0xa00ed0a8, 0xa00a5d82:0xa00ed560, 0xa00a5d96:0xa00dbb68,
    0xa0198956:0xa00a6998, 0xa0198960:0xa00d9044, 0xa0198a20:0xa00ed560, 0xa0198a98:0xa00d8f7c,
    0xa00d9098:0xa00d749e, 0xa00d90a0:0xa00d8f02, 0xa00d90e2:0xa00dddf4,
    0xa00d90e8:0xa00d8f42, 0xa00d90ee:0xa00d8f42, 0xa00d90f4:0xa00d8f02, 0xa00d90fe:0xa00d8f42,
    0xa00d8fd2:0xa00d7446, 0xa00d8fda:0xa00d8f02, 0xa00d8fea:0xa00dddf4,
    0xa00d8ffe:0xa00d7546, 0xa00d9006:0xa00d759e, 0xa00d900e:0xa00d85ea,
    0xa00d9014:0xa00d73c6, 0xa00d901a:0xa00dddf4, 0xa00d9020:0xa00d8f02,
    0xa00d902a:0xa00d8f42, 0xa00d9030:0xa00d8f42,
    0xa0082e4a:0xa0080d8e, 0xa0082e54:0xa00dd454, 0xa0082e62:0xa0082c8c,
    0xa0082cae:0xa0080d8e, 0xa0082d90:0xa0089bde, 0xa0082e12:0xa00897c2,
    0xa00ed5b6:0xa00dddf4, 0xa00ed5bc:0xa00dd454, 0xa00ed62c:0xa0082e32,
    0xa00ed6ca:0xa008ab8a, 0xa00ed700:0xa01b1ee6, 0xa00ed706:0xa00ed438,
    0xa00ed720:0xa00d89c6, 0xa00ed726:0xa00dddf4,
    0xa00ed45c:0xa00ed198, 0xa00ed462:0xa019dd98, 0xa00ed470:0xa00d929a,
    0xa00ed476:0xa00d93a2, 0xa00ed48a:0xa00d93fa, 0xa00ed49c:0xa00ed314,
    0xa01b1f1c:0xa00d8f42,
}
for address, target in calls.items():
    expect(address, ['J', 1, hex(target)], 'direct call target, link register ra')

memory = {
    0xa00aa5d4:['S',2,10,8,-192], 0xa00aa5de:['S',2,10,8,-188],
    0xa00a7f7e:['I',3,2,11,18,24], 0xa00a7f9a:['S',2,10,18,32],
    0xa00ab6c0:['C.memory',2,15,11,16], 0xa00ab6ca:['C.memory',2,9,15,4],
    0xa00ab6d0:['I',3,2,19,10,28], 0xa00ab710:['C.memory',2,10,9,32],
    0xa00a69cc:['I',3,4,15,15,95], 0xa00a69f6:['I',3,4,13,15,95],
    0xa00a6a0a:['I',3,4,15,15,95], 0xa00a6a1a:['I',3,4,14,15,95],
    0xa00a6a7a:['I',3,4,15,15,95], 0xa00a6a8a:['I',3,4,13,15,95],
    0xa00d7492:['C.memory',2,10,10,36], 0xa00d74ea:['C.memory',2,10,10,36],
    0xa00d7592:['I',3,5,10,10,40],
    0xa00d90ce:['C.memory',2,15,9,36], 0xa00d90da:['C.memory',6,15,9,36],
    0xa00d8fee:['C.memory',2,11,9,36], 0xa00d8ff4:['C.memory',6,11,9,36],
    0xa00dd45c:['I',3,4,14,10,0], 0xa0082e50:['S',2,9,8,-80], 0xa0082e58:['S',0,10,8,-76],
    0xa0082cb2:['I',3,4,21,22,16], 0xa0082cb6:['I',3,2,23,22,12],
    0xa0082cbe:['I',3,2,15,23,16], 0xa0082d76:['I',3,2,9,20,276],
    0xa0082d82:['C.memory',2,15,9,0], 0xa0082d86:['C.memory',2,15,9,4],
    0xa0082d94:['C.memory',2,15,9,0], 0xa0082da2:['I',3,5,15,19,8],
    0xa0082da8:['I',3,4,10,19,1], 0xa0082dae:['I',3,5,18,19,4],
    0xa0082db8:['S',1,18,19,8], 0xa0082e22:['I',3,2,15,20,272],
    0xa0082e28:['C.memory',2,9,9,4],
    0xa00ed67c:['I',3,5,15,8,-66], 0xa00ed684:['I',3,2,15,18,20],
    0xa00ed688:['I',3,2,16,18,24], 0xa00ed6b6:['I',3,5,15,9,88],
    0xa00ed6c8:['C.memory',2,10,9,44], 0xa00ed6ce:['S',2,18,9,44],
    0xa00ed6d2:['I',3,5,15,8,-64], 0xa00ed6d6:['I',3,4,10,8,-67],
    0xa00ed6de:['C.memory',6,15,9,60], 0xa00ed6e0:['I',3,5,15,8,-62],
    0xa00ed6ea:['C.memory',6,15,9,64], 0xa00ed6ec:['I',3,4,15,9,88],
    0xa00ed6fa:['S',0,10,9,88], 0xa00ed70a:['C.memory',2,15,9,68],
    0xa00ed70e:['C.memory',2,15,9,72], 0xa00ed718:['C.memory',2,14,9,76],
    0xa00ed444:['I',3,5,13,10,88], 0xa00ed47e:['C.memory',2,10,9,60],
    0xa00ed48e:['C.memory',2,12,9,64], 0xa00ed4d8:['C.memory',2,10,9,60],
    0xa00ed4e8:['C.memory',2,10,9,64], 0xa00ed526:['C.memory',2,10,9,60],
    0xa00ed536:['C.memory',2,10,9,64],
}
for address, expected in memory.items():
    expect(address, expected, 'memory operation width/register/base/offset')

for address, expected in {
    0xa00ab712:['C.CR',0,11,19], 0xa0082d96:['C.CR',0,12,19],
    0xa0082d98:['C.CR',0,11,22], 0xa0082d9a:['C.CR',0,10,9],
    0xa0082d9c:['C.CR',1,15,0], 0xa0082e6e:['R',51,3,0,10,0,10],
    0xa00a69d0:['R',51,3,0,15,0,15], 0xa00a6a0e:['R',51,3,0,15,0,15],
    0xa00a6a7e:['R',51,3,0,15,0,15],
    0xa00a69fe:['B',1,13,14,'0xa00a69d6'], 0xa00a6a20:['B',1,14,15,'0xa00a69d6'],
    0xa00a6a92:['B',1,13,14,'0xa00a69d6'],
    0xa01989ce:['B',0,9,15,'0xa0198a94'],
    0xa0082d9e:['B',1,10,25,'0xa0082e22'],
    0xa00ed632:['B',0,10,15,'0xa00ed678'], 0xa00ed678:['B',1,19,0,'0xa00ed72c'],
    0xa00ed682:['C.branch',6,15,'0xa00ed6b6'], 0xa00ed68c:['C.branch',6,15,'0xa00ed692'],
    0xa00ed68e:['B',1,16,0,'0xa00ed6b6'], 0xa00ed6c4:['B',6,14,15,'0xa00ed6ce'],
    0xa00ed714:['B',1,15,14,'0xa00ed71e'], 0xa00ed71a:['B',0,14,15,'0xa00ed724'],
    0xa00ed480:['R',51,4,1,11,11,10], 0xa00ed496:['R',51,4,1,12,10,12],
    0xa00ed4ee:['R',51,2,0,15,18,12], 0xa00ed53c:['R',51,2,0,15,12,18],
    0xa00ed540:['C.jump',5,'0xa00ed4f2'],
    0xa00a69a6:['B',6,14,15,'0xa00a6a28'], 0xa00a69b0:['B',0,10,13,'0xa00a69d6'],
    0xa00a69b4:['B',6,13,10,'0xa00a69de'], 0xa00a69b8:['B',0,10,14,'0xa00a6a06'],
    0xa00a69c4:['B',6,14,10,'0xa00a69d6'], 0xa00a69e2:['B',0,10,15,'0xa00a6a16'],
    0xa00a69ee:['B',6,14,10,'0xa00a69d6'], 0xa00a6a30:['B',6,14,15,'0xa00a6a9a'],
    0xa00a6a3c:['B',7,13,14,'0xa00a69d6'], 0xa00a6a44:['B',6,15,10,'0xa00a6a68'],
    0xa00a6a4c:['B',6,15,10,'0xa00a6a86'], 0xa00a6a54:['B',7,15,10,'0xa00a6a76'],
    0xa00a6a60:['B',7,14,10,'0xa00a69d6'], 0xa00a6a6e:['B',1,10,14,'0xa00a69d6'],
    0xa00a6a9e:['B',6,14,15,'0xa00a6aec'], 0xa00a6aa4:['B',6,14,15,'0xa00a6ab6'],
    0xa00a6aae:['B',1,10,14,'0xa00a69d6'], 0xa00a6abe:['B',7,13,14,'0xa00a69d6'],
    0xa00a6ac6:['B',0,10,14,'0xa00a69d6'], 0xa00a6ace:['B',0,10,14,'0xa00a69d6'],
    0xa00a6ad4:['B',6,14,10,'0xa00a69d6'], 0xa00a6adc:['B',0,10,13,'0xa00a6ab2'],
    0xa00a6ae0:['B',0,10,14,'0xa00a69d6'],
    0xa00d909c:['C.branch',6,10,'0xa00d9102'], 0xa00d8fd6:['C.branch',7,10,'0xa00d9034'],
    0xa00d9002:['C.branch',6,10,'0xa00d901e'], 0xa00d900c:['C.branch',6,10,'0xa00d901e'],
    0xa00d9018:['C.branch',6,10,'0xa00d901e'],
    0xa00d7498:['I',19,3,10,10,1], 0xa00d74ee:['R',51,3,0,10,0,10],
    0xa00d7598:['R',51,3,0,10,0,10],
    0xa00d7494:['C.ALU',3,10,11], 0xa00d7496:['C.ALU',0,10,11],
    0xa00d74ec:['C.ALU',3,10,11], 0xa00d7596:['C.ALU',3,10,11],
    0xa00d90d8:['C.ALU',3,15,14],
}.items():
    expect(address, expected, 'ABI, predicate, conditional gate, arithmetic or shared control-flow')

# Vendor words: independently compare fields against the retained local ISA model.
for address in (0xa00ed5f8, 0xa00ed6c0, 0xa00ed748):
    w = word(address)
    values = [w & 127, (w >> 12) & 7, (w >> 7) & 31, (w >> 15) & 31, w >> 26, (w >> 20) & 63]
    assert values == [11,3,15,15,15,0]
    checks.append(dict(address=hex(address), bytes=read(address,4).hex(), fields=values, meaning='extu opcode/f3/rd/rs1/msb/lsb'))
expect(0xa00ed4f2, ['R',11,1,33,12,18,15], 'mvnez rd=a2 rs1=s2 rs2=a5; nonzero move per retained model')

# PC-relative call pairs are decoded separately from JAL.
for address, target in [(0xa01b1ef6,0xa00901cc),(0xa01b1f04,0xa00901e2)]:
    a, b = word(address), word(address+4)
    assert (a & 127, (a >> 7)&31, b & 127, (b>>7)&31, (b>>15)&31) == (23,1,103,1,1)
    actual = (address + signed(a & 0xfffff000,32) + signed(b >> 20,12)) & 0xfffffffe
    assert actual == target
    checks.append(dict(address=hex(address), bytes=read(address,8).hex(), target=hex(actual), meaning='AUIPC/JALR call pair'))

# Only the 12 descriptor arms reachable from this mapper, not every image source type.
selection = {
    1:(0xa0198a4e,0xa0251da8),2:(0xa0198a58,0xa062ff20),3:(0xa0198a62,0xa062fb30),
    4:(0xa01989a0,0xa062fd24),6:(0xa0198a16,0xa062eee8),7:(0xa01989c2,0xa062f2bc),
    8:(0xa0198a30,0xa062f414),9:(0xa0198a3a,0xa062f618),11:(0xa0198a80,0xa0630658),
    12:(0xa01989ec,0xa062f9a4),13:(0xa0198a44,0xa062f834),14:(0xa01989fc,0xa062f16c),
}
resources=[]
for category, (address, expected) in selection.items():
    a, b = word(address), word(address+4)
    assert (a & 127, (a >> 7)&31, b & 127, (b>>7)&31, (b>>15)&31) == (55,11,19,11,11)
    descriptor = ((a & 0xfffff000) + signed(b >> 20,12)) & 0xffffffff
    assert descriptor == expected
    header = struct.unpack('<7I',read(descriptor,28))
    assert header[0:3] == (0x119,0,0) and header[5:] == (0,0) and header[4] == descriptor+28
    payload = read(header[4], header[3])
    assert payload[:8] == b'\x89PNG\r\n\x1a\n' and payload[12:16] == b'IHDR'
    width,height=struct.unpack('>II',payload[16:24])
    assert width > 0 and height > 0
    resources.append(dict(category=category, instruction=hex(address), descriptor=hex(descriptor), bytes=read(descriptor,28).hex(), words=list(header), payload=hex(header[4]), size=header[3], ihdr_width=width, ihdr_height=height, classifier=0, evidence_boundary='Signature/IHDR only; no decoder execution or success assertion'))

model = SOURCE / 'evidence/rea-0041-20261017/ghidra/Ghidra/Processors/RISCV/data/languages/ap01thead2.sinc'
lines=model.read_text().splitlines()
excerpts=[]
for prefix in (':th.extu rd,rs1,15,0 ',':th.mvnez '):
    start=next(i for i,line in enumerate(lines) if line.startswith(prefix))
    end=next(i for i in range(start+1,len(lines)) if lines[i] == '}')
    excerpts.append(dict(start_line=start+1,end_line=end+1,text='\n'.join(lines[start:end+1])))

strings=[]
for address in (0xa0269c4c,0xa0569930,0xa05699b4,0xa05699a0,0xa056d750,0xa056af14):
    offset=address-0xa0000000+0x1000
    end=image.index(b'\0',offset)
    strings.append(dict(address=hex(address),text=image[offset:end].decode('utf-8')))
assert strings[0]['text']=='ico'
assert strings[1]['text']=='lv_obj_has_state'

result=dict(static_only=True,rom=str(ROM),mapping='file offset = VA - 0xa0000000 + 0x1000',windows=windows,encoding_checks=checks,resources=resources,strings=strings,retained_model=dict(path=str(model),excerpts=excerpts),predecessor_byte_rows_matched=matched,limitations=['No target execution, simulation, input replay, device or network access.','Decoder registration and info callback, q writers, widget/context destruction and physical drawing remain unreviewed.','Predecessor extra selector arms 5/10/17/22/23 not resource-validated; unreachable from this mapper.','Local ISA model correspondence is not independent hardware/vendor ISA certification.'])
(OUT/'instruction-review.json').write_text(json.dumps(result,indent=2,ensure_ascii=False)+'\n',encoding='utf-8')
(OUT/'instructions.txt').write_text('\n\n'.join(w['name']+'\n'+'\n'.join(r['address']+' '+r['bytes']+' '+r['instruction']+' | '+str(r['raw_fields']) for r in w['rows']) for w in windows)+'\n',encoding='utf-8')
summary=dict(result='passed',core_functions=11,necessary_predicates=3,windows=len(windows),bytes=sum(hi-lo for _,lo,hi in ranges),instructions=len(by_address),encoding_checks=len(checks),vendor_words=4,predecessor_rows_matched=matched,reachable_resources=len(resources),unknown_instructions=0,capstone_version=capstone.__version__)
(OUT/'review-index.json').write_text(json.dumps(summary,indent=2)+'\n',encoding='utf-8')
print(json.dumps(summary))
