"""NR02 independent, bounded ROM field checks; no target execution or imports of prior verifiers."""
import json
import re
from pathlib import Path

MAIN = Path('D:/Documents/PlatformIO/Projects/cuktech-ap01-firmware')
OUT = Path(__file__).resolve().parent
BASE = 0x9ffff000
rom = (MAIN / 'roms/0041/ap01-1.0.2_0041.bin').read_bytes()
source = json.loads((MAIN / 'reverse/analysis/buzzer-backlight-0041-20261023.json').read_text(encoding='utf-8'))
fn = next(x for x in source['functions'] if x['address'] == '0xa00a8582')
checks = []


def eq(label, got, expected):
    assert got == expected, (label, got, expected)
    checks.append({'label': label, 'actual': got, 'expected': expected})


def read(pc, n=4):
    return int.from_bytes(rom[pc-BASE:pc-BASE+n], 'little')


def signed(v, width):
    return v - (1 << width) if v >> (width-1) else v


def insn(pc, op, f3, rd=None, rs1=None, rs2=None, imm=None):
    w = read(pc)
    got = [w & 127, w >> 12 & 7]
    expected = [op, f3]
    for value, wanted in [(w >> 7 & 31, rd), (w >> 15 & 31, rs1), (w >> 20 & 31, rs2)]:
        if wanted is not None:
            got.append(value)
            expected.append(wanted)
    if imm is not None:
        v = ((w >> 25) << 5 | (w >> 7 & 31)) if op == 35 else w >> 20
        got.append(signed(v, 12))
        expected.append(imm)
    eq(hex(pc), got, expected)


def branch(pc, a, b, f3, target):
    w = read(pc)
    v = (w >> 31) << 12 | (w >> 7 & 1) << 11 | (w >> 25 & 63) << 5 | (w >> 8 & 15) << 1
    eq(hex(pc)+' branch', [w & 127, w >> 12 & 7, w >> 15 & 31, w >> 20 & 31, pc+signed(v,13)], [99,f3,a,b,target])


def jump(pc, target):
    w = read(pc)
    v = (w >> 31) << 20 | (w >> 12 & 255) << 12 | (w >> 20 & 1) << 11 | (w >> 21 & 1023) << 1
    eq(hex(pc)+' jal', [w & 127,w >> 7 & 31,pc+signed(v,21)], [111,1,target])


def compressed_jump(pc, target):
    h = read(pc,2)
    v = (h >> 12 & 1) << 11 | (h >> 11 & 1) << 4 | (h >> 9 & 3) << 8 | (h >> 8 & 1) << 10
    v |= (h >> 7 & 1) << 6 | (h >> 6 & 1) << 7 | (h >> 3 & 7) << 1 | (h >> 2 & 1) << 5
    eq(hex(pc)+' c.j', [h&3,h>>13,pc+signed(v,12)], [1,5,target])


assembly = {int(x.split(':',1)[0],16): x.split(':',1)[1].strip() for x in fn['assembly']}
windows = [(0xa00a93a4,0xa00a941a), (0xa00a9504,0xa00a951e), (0xa00a9580,0xa00a960a), (0xa00a972a,0xa00a973e)]
records = []
for lo, hi in windows:
    carrier = next(r for r in fn['raw_ranges'] if int(r['start'],16) <= lo and int(r['start'],16)+len(bytes.fromhex(r['hex'])) >= hi)
    start = int(carrier['start'],16)
    eq(hex(lo)+' retained raw', rom[lo-BASE:hi-BASE].hex(), bytes.fromhex(carrier['hex'])[lo-start:hi-start].hex())
    pc = lo
    while pc < hi:
        n = 4 if read(pc,2)&3 == 3 else 2
        assert pc+n <= hi and pc in assembly
        records.append({'pc':hex(pc),'file_offset':pc-BASE,'raw':rom[pc-BASE:pc-BASE+n].hex(),'retained_decode':assembly[pc]})
        pc += n
    eq(hex(lo)+' boundaries',pc,hi)

# Raw record copy, then fresh per-iteration object/count/array/index formation.
insn(0xa00a93a8,3,4,rd=11,rs1=19,imm=0x1c)
insn(0xa00a93b0,3,2,rd=10,rs1=9,imm=0x2d4)
insn(0xa00a93ba,19,7,rd=11,rs1=11,imm=0xf8)
jump(0xa00a93be,0xa0191652)
insn(0xa00a93c6,3,2,rd=14,rs1=15,imm=0x2cc)
insn(0xa00a93e8,3,2,rd=15,rs1=8,imm=-0x64)
insn(0xa00a93ec,3,2,rd=15,rs1=15,imm=0x2cc)
insn(0xa00a93f0,3,4,rd=14,rs1=15,imm=6)
branch(0xa00a93f4,9,14,5,0xa00a8aae)
insn(0xa00a93f8,19,0,rd=20,rs1=0,imm=424)
eq('index *424 mul',read(0xa00a93fc),0x03448a33)
insn(0xa00a9400,3,2,rd=25,rs1=15,imm=0)
eq('item = array + scaled index add',read(0xa00a9404),0x014c8db3)
insn(0xa00a9408,3,4,rd=15,rs1=27,imm=13)
branch(0xa00a940c,15,0,0,0xa00a9738)
eq('changes starts c.li a6,0',read(0xa00a9508,2),0x4801)
insn(0xa00a9504,3,4,rd=14,rs1=27,imm=14)
branch(0xa00a950a,14,15,0,0xa00a9598)
insn(0xa00a950e,35,0,rs1=27,rs2=15,imm=14)
insn(0xa00a9580,19,0,rd=16,rs1=0,imm=64)
insn(0xa00a972e,19,0,rd=16,rs1=0,imm=64)
compressed_jump(0xa00a9732,0xa00a9598)
# Three scalar equality/store/bit sequences, independently derived from ROM formats.
for loadpc,sourceoff,destoff,width,mask in [(0xa00a9598,2,16,5,256),(0xa00a95ac,0,18,4,512),(0xa00a95c8,1,15,4,128)]:
    insn(loadpc,3,width,rd=15,rs1=18,imm=sourceoff)
    insn(loadpc+4,3,width,rd=14,rs1=27,imm=destoff)
    target = {0xa00a9598:0xa00a95ac,0xa00a95ac:0xa00a95c0,0xa00a95c8:0xa00a9734}[loadpc]
    branch(loadpc+8,14,15,0,target)
    insn(loadpc+12,35,1 if width==5 else 0,rs1=27,rs2=15,imm=destoff)
    insn(loadpc+16,19,6,rd=16,rs1=16,imm=mask)
insn(0xa00a95c0,3,4,rd=17,rs1=27,imm=14)
branch(0xa00a95c4,17,0,0,0xa00a9734)
branch(0xa00a9734,16,0,1,0xa00a95dc)
# Custom indexed word store: local model meaning is separately inherited.
w=read(0xa00a95e4)
eq('95e4 custom fields op/rd/rs1/rs2/f3/upper5/shift', [w&127,w>>7&31,w>>15&31,w>>20&31,w>>12&7,w>>27,w>>25&3], [11,16,25,20,5,8,0])
jump(0xa00a95fc,0xa008b51a)
insn(0xa00a9600,19,7,rd=10,rs1=9,imm=255)
jump(0xa00a9604,0xa00a389c)
compressed_jump(0xa00a9608,0xa00a9738)
compressed_jump(0xa00a973c,0xa00a93e8)
eq('loop index +1',read(0xa00a9738,2),0x0485)
eq('loop record +8',read(0xa00a973a,2),0x0921)

result={'claim':'N02','reviewer':'NR02','static_only':True,'target_execution':False,'author_verifier_imported_or_executed':False,'source':'reverse/analysis/buzzer-backlight-0041-20261023.json','evidence_id':fn['evidence_id'],'source_language':fn['profile']['parameters']['language_id'],'mapping':'VA - 0x9ffff000','rom_identity_inherited':source['rom_sha256'],'checks':checks,'check_count':len(checks),'windows':[{'lo':hex(a),'hi_exclusive':hex(b)} for a,b in windows],'byte_count':sum(b-a for a,b in windows),'instruction_count':len(records),'instructions':records,'limitation':'Standard encoding fields checked; custom semantic interpretation inherited from E02 local SLEIGH, not an independent vendor ISA specification.'}
(OUT/'independent-checks.json').write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
print(json.dumps({k:result[k] for k in ['check_count','byte_count','instruction_count','source_language']}))

# Artifact consistency and inherited-reference checks are separate from ROM checks.
index_path = MAIN / 'reverse/analysis/telemetry-interface-n02-0041-20261024/interface.json'
index = json.loads(index_path.read_text(encoding='utf-8'))
assert [(f['record_offset'],f['input_width'],f['item_offset'],f['output_width'],f['event_bit']) for f in index['cmd51']['fields'][1:]] == [(2,'u16',16,'u16','0x100'),(0,'u8',18,'u8','0x200'),(1,'u8',15,'u8','0x80')]
assert [(f['item_pointer_offset'],f['length'],f['event_bit']) for f in index['cmd52']['updates']] == [(40,20,'0x4000'),(48,12,'0x8000'),(52,24,'0x10000'),(44,24,'0x20000'),(56,24,'0x40000')]
report_path = MAIN / 'reverse/reports/ap01/telemetry-interface-n02-0041-20261024.md'
report = report_path.read_text(encoding='utf-8')
links = re.findall(r'\]\(([^)]+)\)',report)
local_links = []
for link in links:
    if link.startswith(('http:','https:','C:')):
        continue
    p = (report_path.parent / link.split('#')[0]).resolve()
    assert p.exists(), str(p)
    local_links.append(link)
inheritance = []
for name,terms in [
    ('cmd51-device-type-review-b23-0041-20261024.md',['限定接受','LHU','950e']),
    ('cmd56-item-field-review-b26-0041-20261024.md',['限定接受','0x800','同一total/array实例']),
    ('uiiface-ownership-review-e02-0041-20261023.md',['38d8','8730','8000h','20000h']),
    ('ctk-view-review-e04-0041-20261023.md',['互斥','0x52 B','a00aef66']),
    ('ctk-snapshot-consumer-e12-0041-20261024.md',['新增业务恢复0','主要消费者不向持久对象存储']),
    ('ctk-offline-transition-e13-0041-20261024.md',['不冒称独立技术验收','没有依据 converter 返回值作门控','values→name→status'])]:
    text = (report_path.parent/name).read_text(encoding='utf-8')
    for term in terms:
        assert term in text,(name,term)
    inheritance.append({'report':name,'checked_terms':terms,'method':'source contract text only; no inherited verifier execution'})
artifact = {'interface_json_parse':True,'scalar_mapping_matches_rom_checked_expectations':True,'cmd52_table_matches_E02':True,'local_links_exist':local_links,'inherited_sources':inheritance,'correction_required':{'file':str(report_path.relative_to(MAIN)),'location':'cmd51接入精度 source/profile sentence','reported_language':'RISCV:LE:32:ap01thead2','actual_retained_dispatcher_language':fn['profile']['parameters']['language_id'],'kind':'source metadata only; behavior unaffected'}}
(OUT/'artifact-checks.json').write_text(json.dumps(artifact,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
print(json.dumps({'local_links':len(local_links),'inherited_contracts':len(inheritance)}))
