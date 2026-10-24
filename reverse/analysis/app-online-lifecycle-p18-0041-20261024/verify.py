"""Read retained static evidence and bounded ROM windows; never execute the target."""
import json
from pathlib import Path
import capstone

ROOT = Path('D:/Documents/PlatformIO/Projects/cuktech-ap01-firmware')
OUT = Path(__file__).resolve().parent
BASE = 0x9ffff000
PROFILE = 'b6368dd18431e8113aa5026c713d41e648ab0f6ddd9421ff6c4a49e23b3cd2f3'
bundle_path = ROOT / 'evidence/rea-0041-20261017/evidence/whole-rom-private-20261023.evidence.json'
bundle = json.loads(bundle_path.read_text(encoding='utf8'))
rom = (ROOT / 'roms/0041/ap01-1.0.2_0041.bin').read_bytes()
assert len(rom) == 6769704
records = {}
for address in ['0xa00adabc', '0xa005cc1e', '0xa00ad602']:
    r = next(r for r in bundle['records'] if r.get('parameters', {}).get('procedure') == address)
    assert r['analysis_profile']['digest'] == PROFILE
    assert r['analysis_profile']['parameters']['language_id'] == 'RISCV:LE:32:ap01thead2'
    records[address] = r

md = capstone.Cs(capstone.CS_ARCH_RISCV, capstone.CS_MODE_RISCV32 | capstone.CS_MODE_RISCVC)
windows = [
    ('0xa00adabc', 0xa00adae8, 0xa00adaec, 'arguments'),
    ('0xa00adabc', 0xa00adb02, 0xa00adb20, 'app-null'),
    ('0xa00adabc', 0xa00adb3e, 0xa00adb64, 'item-null and defer'),
    ('0xa00adabc', 0xa00adb84, 0xa00adbbc, 'defer-return and active'),
    ('0xa00adabc', 0xa00adc14, 0xa00adc42, 'child0 bridge and activity gate'),
    ('0xa00adabc', 0xa00adc42, 0xa00adc88, 'online stores and timer calls'),
    ('0xa00adabc', 0xa00adc88, 0xa00adce8, 'online join and regular inputs'),
    ('0xa00adabc', 0xa00add16, 0xa00add3c, 'regular insertion gate'),
    ('0xa00adabc', 0xa00ae196, 0xa00ae19e, 'nonzero to nonzero gate'),
    ('0xa005cc1e', 0xa005da4a, 0xa005da78, 'inherited timer and child attachment'),
    ('0xa00ad602', 0xa00ad61e, 0xa00ad620, 'inherited timer userdata'),
]
evidence = {'authority': 'shipped-artifact static; not runtime', 'rom_identity': {
    'path': str(ROOT / 'roms/0041/ap01-1.0.2_0041.bin'), 'bytes': len(rom),
    'sha256_inherited_from_catalog': '972db4c136c7ed9e24a83c07c1a7fd62040ca018b08ca285216d26b1fee3c6b9',
    'base': hex(BASE)}, 'retained_bundle': str(bundle_path), 'records': [], 'windows': []}
for address, r in records.items():
    evidence['records'].append({'procedure': address, 'evidence_id': r['evidence_id'],
        'profile_digest': PROFILE, 'provider': r['analysis_profile']['provider'],
        'language_id': r['analysis_profile']['parameters']['language_id'],
        'limitations': r['normalized_result']['limitations'],
        'pseudocode_has_unreachable_warning': 'unreachable' in r['normalized_result']['pseudocode'].lower()})

decoded = {}
for proc, start, end, purpose in windows:
    retained = [x for x in records[proc]['normalized_result']['assembly'] if start <= int(x.split(':')[0], 16) < end]
    insns = list(md.disasm(rom[start-BASE:end-BASE], start))
    assert insns and sum(x.size for x in insns) == end-start
    assert [x.address for x in insns] == [int(x.split(':')[0],16) for x in retained]
    for x in insns:
        decoded[x.address] = x
    evidence['windows'].append({'procedure': proc, 'start': hex(start), 'end_exclusive': hex(end),
        'purpose': purpose, 'retained_assembly': retained,
        'rom': [{'address': hex(x.address), 'bytes': x.bytes.hex(), 'mnemonic': x.mnemonic,
                 'operands': x.op_str} for x in insns]})

checks = []
def insn(address, mnemonic, operands):
    x = decoded[address]
    assert (x.mnemonic, x.op_str) == (mnemonic, operands), (hex(address), x.mnemonic, x.op_str)
    checks.append({'address': hex(address), 'expect': mnemonic+' '+operands, 'pass': True})

for address, mnemonic, operands in [
    (0xa00adae8,'c.mv','s6, a0'), (0xa00adaea,'c.mv','s2, a1'),
    (0xa00adb5c,'lw','a5, 0(s2)'), (0xa00adb60,'sw','a5, 0x54(s6)'),
    (0xa00adba4,'lbu','a5, 0x4c(s6)'),
    (0xa00adc24,'c.lw','a5, 0x10(a0)'), (0xa00adc2a,'c.lw','s1, 4(a5)'),
    (0xa00adc32,'lbu','a5, 0x10(a5)'),
    (0xa00adc52,'sb','a4, 0x28(a5)'), (0xa00adc5a,'sb','zero, 0x9d(a5)'),
    (0xa00adc5e,'sb','zero, 0x101(a5)'), (0xa00adc62,'sh','zero, 0xfa(s1)'),
    (0xa00adc66,'sb','zero, 0xfc(a5)'), (0xa00adc6a,'lw','a0, 0xf4(s1)'),
    (0xa00adc6e,'sb','a4, 0xe(s4)'), (0xa00adc76,'c.lw','a5, 0x14(a0)'),
    (0xa00adc78,'c.andi','a5, 1'), (0xa00adc80,'lw','a0, 0xf4(s1)'),
    (0xa00adccc,'sb','a4, 0x10(a5)'), (0xa00adcd4,'lbu','a5, 0x15(a5)'),
    (0xa00adcd8,'lbu','a4, 0x21(s2)'), (0xa00adcdc,'lbu','s9, 0xe(s2)'),
    (0xa00add1e,'lbu','a5, 0x28(t1)'), (0xa00add28,'lbu','a4, 0xc(s4)'),
    (0xa00add30,'lbu','a5, 0xc(s2)'),
    (0xa005da50,'c.mv','a2, s2'), (0xa005da5e,'sw','a0, 0x74(s3)'),
    (0xa005da6c,'sw','s2, 4(s7)'), (0xa005da74,'sw','s7, 0x10(s1)'),
    (0xa00ad61e,'c.lw','s1, 0xc(a0)'),
]:
    insn(address, mnemonic, operands)

def sext(v,bits):
    return v-(1<<bits) if v>>(bits-1) else v
def jal(address, target):
    w = int.from_bytes(rom[address-BASE:address-BASE+4], 'little')
    assert w & 0x7f == 0x6f
    imm = ((w>>31)<<20)|(((w>>12)&255)<<12)|(((w>>20)&1)<<11)|(((w>>21)&1023)<<1)
    assert (address+sext(imm,21)) & 0xffffffff == target
    checks.append({'address':hex(address),'jal_target':hex(target),'pass':True})
for a,t in [(0xa00adc20,0xa00dcee4),(0xa00adc46,0xa00a769a),
            (0xa00adc7c,0xa008bd70),(0xa00adc84,0xa008c2d0),
            (0xa005da5a,0xa008bc64),(0xa005da62,0xa008bd16)]:
    jal(a,t)

def branch(address, target, funct3, rs1, rs2):
    w = int.from_bytes(rom[address-BASE:address-BASE+4], 'little')
    assert w & 0x7f == 0x63
    assert ((w>>12)&7, (w>>15)&31, (w>>20)&31) == (funct3,rs1,rs2)
    imm = ((w>>31)<<12)|(((w>>7)&1)<<11)|(((w>>25)&63)<<5)|(((w>>8)&15)<<1)
    assert (address+sext(imm,13)) & 0xffffffff == target
    checks.append({'address':hex(address),'branch_target':hex(target),'pass':True})
for args in [(0xa00adc3a,0xa00adcd0,0,14,15), (0xa00adc3e,0xa00ae196,1,15,0),
             (0xa00adc42,0xa00adcc4,0,14,0), (0xa00ae19a,0xa00adcc4,1,15,0),
             (0xa00add24,0xa00ade8a,1,15,14), (0xa00add2c,0xa00ade8a,1,14,15),
             (0xa00add38,0xa00ae5ec,1,15,0)]:
    branch(*args)
h = int.from_bytes(rom[0xa00adc7a-BASE:0xa00adc7c-BASE],'little')
assert (h&3,(h>>13)&7,((h>>7)&7)+8)==(1,6,15)
imm=(((h>>12)&1)<<8)|(((h>>5)&3)<<6)|(((h>>2)&1)<<5)|(((h>>10)&3)<<3)|(((h>>3)&3)<<1)
assert 0xa00adc7a+sext(imm,9)==0xa00adca4
checks.append({'address':'0xa00adc7a','branch_target':'0xa00adca4','pass':True})

# Only the normal nonnull API effect is needed, not the public timer implementation.
api_start, api_end = 0xa008c31c, 0xa008c328
api = list(md.disasm(rom[api_start-BASE:api_end-BASE],api_start))
assert sum(x.size for x in api) == api_end-api_start
decoded.update({x.address:x for x in api})
insn(0xa008c31c,'c.mv','s1, a0')
insn(0xa008c322,'c.sw','a0, 4(s1)')
jal(0xa008c31e,0xa008b17e)
jal(0xa008c324,0xa0087b06)
evidence['timer_reset_api_normal_effect'] = {
    'source':'ROM/Capstone 5.0.7, no new REA Evidence ID; normal nonnull path only',
    'start':hex(api_start),'end_exclusive':hex(api_end),
    'instructions':[{'address':hex(x.address),'bytes':x.bytes.hex(),'mnemonic':x.mnemonic,'operands':x.op_str} for x in api],
    'boundary':'store current tick from inherited a008b17e into T+4, then inherited notifier a0087b06; no deeper analysis'}
coverage = json.loads((ROOT / 'reverse/analysis/whole-rom-coverage-0041-20261023-round1.json').read_text(encoding='utf8'))
evidence['timer_reset_extent'] = next(x for x in coverage['functions'] if x['address']=='0xa008c2d0')
result = {'pass':True, 'capstone_version':capstone.__version__, 'checks':checks,
    'window_count':len(windows), 'retained_window_bytes':sum(b-a for _,a,b,_ in windows),
    'retained_instructions':sum(len(x['rom']) for x in evidence['windows']),
    'additional_api_bytes':api_end-api_start,
    'limitations':['Selected operand and JAL checks, not a formal dataflow proof.',
    'Vendor extu and port/index semantics inherited from accepted E04/E13, not reinterpreted with Capstone.',
    'No target, instruction model, scheduler, build or runtime execution.',
    'Regular producer classification beyond insertion gate remains a separate unclosed stage.']}
OUT.mkdir(parents=True,exist_ok=True)
(OUT/'evidence.json').write_text(json.dumps(evidence,ensure_ascii=False,indent=2)+'\n',encoding='utf8')
(OUT/'checks.json').write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n',encoding='utf8')
print(json.dumps({k:v for k,v in result.items() if k not in ['checks','limitations']}))
