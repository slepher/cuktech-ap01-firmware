"""P-05 bounded offline byte/metadata verification; never executes firmware or ISA models."""
import json
from pathlib import Path
from capstone import Cs, CS_ARCH_RISCV, CS_MODE_RISCV32, CS_MODE_RISCVC, cs_version

MAIN = Path('D:/Documents/PlatformIO/Projects/cuktech-ap01-firmware')
OUT = Path(__file__).resolve().parent
BASE = 0x9ffff000
DOC = 'reverse/analysis/buzzer-backlight-0041-20261023.json'
doc = json.loads((MAIN / DOC).read_text(encoding='utf-8'))
f = next(x for x in doc['functions'] if x['address'] == '0xa00a8582')
assert doc['rom_sha256'] == '972db4c136c7ed9e24a83c07c1a7fd62040ca018b08ca285216d26b1fee3c6b9'
assert f['profile']['parameters']['language_id'] == 'RISCV:LE:32:ap01thead3'
rom = (MAIN / 'roms/0041/ap01-1.0.2_0041.bin').read_bytes()
assert len(rom) == 6769704
rr = f['raw_ranges'][0]
old = bytes.fromhex(rr['hex'])
origin = int(rr['start'], 16)
asm = {int(s.split(':', 1)[0], 16): s.split(':', 1)[1].strip() for s in f['assembly']}
md = Cs(CS_ARCH_RISCV, CS_MODE_RISCV32 | CS_MODE_RISCVC)
checks = []

def check(label, actual, expected):
    assert actual == expected, (label, actual, expected)
    checks.append(dict(label=label, actual=actual, expected=expected))

def raw(pc, n=4):
    return rom[pc - BASE:pc - BASE + n]

def sx(n, bits):
    return n - (1 << bits) if n & (1 << (bits - 1)) else n

def load(pc, rd, rs, offset, width):
    w = int.from_bytes(raw(pc), 'little')
    check(hex(pc) + ' load', [w & 127, (w >> 7) & 31, (w >> 12) & 7, (w >> 15) & 31, sx(w >> 20, 12)], [3, rd, width, rs, offset])

def branch(pc, target, rs1, rs2, cond):
    w = int.from_bytes(raw(pc), 'little')
    imm = ((w >> 31) << 12) | (((w >> 7) & 1) << 11) | (((w >> 25) & 63) << 5) | (((w >> 8) & 15) << 1)
    check(hex(pc) + ' branch', [w & 127, (w >> 12) & 7, (w >> 15) & 31, (w >> 20) & 31, pc + sx(imm, 13)], [99, cond, rs1, rs2, target])

windows = []
for name, start, end in [('command_partition', 0xa00a85ac, 0xa00a85cc), ('cmd55_dispatch', 0xa00a8602, 0xa00a860a), ('cmd55_clear_path', 0xa00a88f6, 0xa00a8a2a), ('mask_loop_return', 0xa00a8ab4, 0xa00a8aca), ('cmd50_latch', 0xa00a9212, 0xa00a9238)]:
    check(name + ' retained bytes', raw(start, end - start).hex(), old[start-origin:end-origin].hex())
    ins = []
    pc = start
    while pc < end:
        size = 4 if raw(pc, 2)[0] & 3 == 3 else 2
        assert pc + size <= end
        i = next(md.disasm(raw(pc, size), pc), None)
        ins.append(dict(pc=hex(pc), file_offset=pc-BASE, hex=raw(pc,size).hex(), standard_decode=(i.mnemonic+' '+i.op_str) if i else None, retained_decode=asm[pc]))
        pc += size
    check(name + ' boundary', pc, end)
    windows.append(dict(name=name, start=hex(start), end_exclusive=hex(end), hex=raw(start,end-start).hex(), instructions=ins))

branch(0xa00a8606, 0xa00a88f6, 10, 15, 0)
branch(0xa00a8966, 0xa00a8a22, 17, 14, 0)
branch(0xa00a8a06, 0xa00a8ab4, 15, 16, 6)
branch(0xa00a921c, 0xa00a9238, 13, 15, 1)
for args in [(0xa00a8930,14,15,16,5), (0xa00a8934,13,15,18,5), (0xa00a8950,17,15,22,4), (0xa00a8996,10,18,28,4), (0xa00a89e0,16,18,28,4), (0xa00a9212,14,9,4,5), (0xa00a9228,11,12,0,5)]:
    load(*args)
for pc, rs2, rs1, offset, width in [(0xa00a898e,17,18,28,0), (0xa00a8a1e,0,15,0x50a,1), (0xa00a9234,13,12,0,1)]:
    w = int.from_bytes(raw(pc),'little')
    imm = ((w >> 25) << 5) | ((w >> 7) & 31)
    check(hex(pc)+' store', [w&127,(w>>12)&7,(w>>15)&31,(w>>20)&31,sx(imm,12)], [35,width,rs1,rs2,offset])
check('count-zero branch c.beqz', raw(0xa00a899a,2).hex(), '41c5')

# References are scoped to the retained dispatcher dossier, not a global xref inventory.
SOURCE = 'evidence/rea-0041-20261017/round3/evidence/whole-rom-round3-initial.evidence.json'
bundle = json.loads((MAIN / SOURCE).read_text(encoding='utf-8'))
record = bundle['records'][2]
check('record identity', record['evidence_id'], f['evidence_id'])
refs = [q for q in record['normalized_result']['outgoing_references'] if q.get('target_address') == '0x62fcb50a']
check('dispatcher exact target reference sites', [(q['source_address'],q['kind']['type']) for q in refs], [('0xa00a8a1e','WRITE'),('0xa00a9228','READ'),('0xa00a9234','WRITE')])
inspected = []
init = next(q for q in bundle['records'] if q.get('normalized_result',{}).get('procedure',{}).get('address') == '0xa005a736')
init_refs = [q for q in init['normalized_result']['outgoing_references'] if q.get('target_address') == '0x62fcb50a']
check('initializer exact-target metadata', len(init_refs), 0)
inspected.append(dict(address='0xa005a736', source=SOURCE, evidence_id=init['evidence_id'], profile_digest=init['analysis_profile']['digest'], exact_target_references=init_refs, limitation='Only provider-recognized references in this dossier; not indirect effects.'))
retry_path = 'reverse/analysis/uart-retry-receive-0041-20261023.json'
retry = json.loads((MAIN / retry_path).read_text(encoding='utf-8'))
for address in ['0xa0191746','0xa00a5558']:
    q = next(q for q in retry['functions'] if q['address'] == address)
    check(address+' retained pseudocode exact token', q['pseudocode'].lower().count('62fcb50a'), 0)
    inspected.append(dict(address=address, source=retry_path, evidence_id=q['evidence_id'], profile_digest=q['profile_digest'], original_source=q['source'], exact_pseudocode_token_matches=0, limitation='Scoped retained body inspection; no claim about all callee effects.'))
negative = []
for passn in (3,4,5):
    p = MAIN / f'reverse/analysis/0041-20261013/0041-ghidra-pass{passn}.txt'
    text = p.read_text(encoding='utf-8', errors='replace').lower()
    check(p.name+' exact-address text count', text.count('62fcb50a'), 0)
    negative.append(dict(path=str(p.relative_to(MAIN)), exact_token='62fcb50a', matches=0, limitation='Text lookup only; not complete memory-reference coverage.'))
out = dict(claim='P-05', rom_sha256=doc['rom_sha256'], base=hex(BASE), provider=f['profile']['provider'], language=f['profile']['parameters']['language_id'], profile_digest=f['profile']['digest'], source=dict(path=DOC,evidence_id=f['evidence_id'],original_source=f['source']), metadata_source=dict(path=SOURCE,pointer='/records/2/normalized_result/outgoing_references'), exact_target_references=refs, inspected_candidates=inspected, windows=windows, capstone=cs_version(), bounded_negative_searches=negative, checks=checks, limitations=['No global xref inventory available.', 'No consumer, request meaning, or latch-specific notification established.', 'Vendor extu bytes retained; no ISA model loaded/executed.'])
(OUT / 'static-evidence.json').write_text(json.dumps(out,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
print(json.dumps(dict(checks=len(checks),windows=len(windows),bytes=sum(len(bytes.fromhex(w['hex'])) for w in windows),status='PASS')))
