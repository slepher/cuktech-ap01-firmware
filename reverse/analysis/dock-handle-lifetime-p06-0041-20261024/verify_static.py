"""P-06 bounded offline byte/identity checks; never executes target code."""
from pathlib import Path
import json
import re
from capstone import Cs, CS_ARCH_RISCV, CS_MODE_RISCV32, CS_MODE_RISCVC

ROOT = Path('D:/Documents/PlatformIO/Projects/cuktech-ap01-firmware')
OUT = Path(__file__).resolve().parent
BASE = 0x9ffff000
rom = (ROOT / 'roms/0041/ap01-1.0.2_0041.bin').read_bytes()
assert len(rom) == 6769704
owner_path = 'reverse/analysis/factory-test-0041-20261023/retained-initializer.json'
uart_path = 'reverse/analysis/usb-interface-ota-0041-20261023.json'
owner = json.loads((ROOT / owner_path).read_text(encoding='utf-8'))['function']
uart = next(f for f in json.loads((ROOT / uart_path).read_text(encoding='utf-8'))['functions']
            if f['address'] == '0xa00a8330')
decoder = Cs(CS_ARCH_RISCV, CS_MODE_RISCV32 | CS_MODE_RISCVC)
windows = [
    ('loop_argument_alias', 0xa005a76e, 0xa005a780, owner),
    ('ctx_allocator_result', 0xa005cbc6, 0xa005cbee, owner),
    ('uart_open_and_ctx_fd', 0xa005ab10, 0xa005ab32, owner),
    ('global_fd_alias', 0xa005b214, 0xa005b23e, owner),
    ('same_fd_and_poll_start', 0xa005b2d8, 0xa005b314, owner),
    ('start_result_not_tested', 0xa005b314, 0xa005b32e, owner),
    ('owner_exit_gate', 0xa005c830, 0xa005c842, owner),
    ('same_owner_close', 0xa005c8f8, 0xa005c910, owner),
    ('callback_global_fd_read', 0xa00a839a, 0xa00a83c0, uart),
]
records = []
for name, start, end, source in windows:
    rows = []
    pc = start
    while pc < end:
        off = pc - BASE
        n = 4 if rom[off] & 3 == 3 else 2
        assert pc + n <= end
        raw = rom[off:off+n]
        ds = list(decoder.disasm(raw, pc))
        assert len(ds) == 1 and ds[0].size == n, hex(pc)
        matched = False
        for rr in source['raw_ranges']:
            blob = bytes.fromhex(rr.get('hex', rr.get('bytes_hex', '')))
            lo = int(rr['start'], 16) if 'start' in rr else rr['file_offset'] + BASE
            if lo <= pc and pc + n <= lo + len(blob):
                assert blob[pc-lo:pc-lo+n] == raw
                matched = True
                break
        assert matched, hex(pc)
        rows.append(dict(pc=hex(pc), file_offset=off, raw=raw.hex(), asm=ds[0].mnemonic+' '+ds[0].op_str))
        pc += n
    records.append(dict(name=name, start=hex(start), end_exclusive=hex(end),
                        evidence_id=source['evidence_id'], rows=rows))
rows = {int(r['pc'], 16): r for w in records for r in w['rows']}
checks = []
for pc, needle in [
    (0xa005a77a, 's1, a0'), (0xa005cbca, '0x19c'), (0xa005cbe6, 's2, a0'),
    (0xa005ab14, '0x43'), (0xa005ab20, 'a0, 4(s2)'), (0xa005ab24, 's5, a0'),
    (0xa005b214, 's3, 0x62fc9'), (0xa005b226, 's6, s3, 0x1b0'),
    (0xa005b232, 's5, 0(s6)'), (0xa005b23a, 's3, s3, 0x1b0'),
    (0xa005b2d8, 'a0, 0(s3)'), (0xa005b2e6, 'a2, 4(s2)'),
    (0xa005b2ea, 's3, s2, 8'), (0xa005b2ee, 'a1, s3'),
    (0xa005b2f0, 's2, 8(s2)'), (0xa005b2f4, 'a0, s1'),
    (0xa005b2fa, 'a4, s2, 0x180'), (0xa005b2fe, 'a5, 0x18(a4)'),
    (0xa005b304, 'a2, a2, 0x330'), (0xa005b308, 'a5, 1'),
    (0xa005b30a, 'a5, 0x18(a4)'), (0xa005b30c, 'a1, 1'),
    (0xa005b30e, 'a0, s3'), (0xa005c836, 'zero, 0x18(s1)'),
    (0xa005c8f8, 'a5, 4(s2)'), (0xa005c908, 'a0, s2, 8'),
    (0xa00a839a, 'a2, 1'), (0xa00a83a2, 's2, s2, 0x1b0'),
    (0xa00a83ae, 'a0, 0(s2)'), (0xa00a83b2, 'a2, 1'),
]:
    assert needle in rows[pc]['asm'], (hex(pc), rows[pc]['asm'], needle)
    checks.append(dict(pc=hex(pc), expected=needle))

def signed(v, n):
    return v - (1 << n) if v >> (n-1) else v

for pc, target in {
    0xa005cbe2: 0xa008e362, 0xa005cbea: 0xa005aa68,
    0xa005ab1c: 0xa003f4f6, 0xa005b222: 0xa0024906,
    0xa005b236: 0xa0028170, 0xa005b2e2: 0xa003f6a2,
    0xa005b2f6: 0xa009e4f6, 0xa005b310: 0xa009f9b6,
    0xa005b32a: 0xa005ab48, 0xa005c90c: 0xa009fb96,
    0xa00a83b8: 0xa003f6a2,
}.items():
    v = int.from_bytes(rom[pc-BASE:pc-BASE+4], 'little')
    assert v & 127 == 111
    d = signed(((v>>31)<<20)|(((v>>12)&255)<<12)|(((v>>20)&1)<<11)|(((v>>21)&1023)<<1), 21)
    assert (pc+d)&0xffffffff == target
    checks.append(dict(pc=hex(pc), jal_target=hex(target), rd=(v>>7)&31))
for pc, target, rs1, rs2, funct in [
    (0xa005ab2e, 0xa005b214, 0, 10, 4),
    (0xa005c8fc, 0xa005c910, 0, 15, 5),
    (0xa005c83e, 0xa005c8f8, 20, 0, 0),
]:
    v = int.from_bytes(rom[pc-BASE:pc-BASE+4], 'little')
    assert v & 127 == 99 and (v>>12)&7 == funct and (v>>15)&31 == rs1 and (v>>20)&31 == rs2
    d = signed(((v>>31)<<12)|(((v>>7)&1)<<11)|(((v>>25)&63)<<5)|(((v>>8)&15)<<1), 13)
    assert (pc+d)&0xffffffff == target
    checks.append(dict(pc=hex(pc), branch_target=hex(target), rs1=rs1, rs2=rs2, funct3=funct))

# Bounded retained-definition metadata: no whole-function re-disassembly or CFG claim.
def first_operand_rows(reg, start, end):
    return [s for s in owner['assembly'] if start <= int(s.split(':')[0],16) < end
            and re.search(r': \S+ '+reg+r'(?:,|$)', s)]
s1_rows = first_operand_rows('s1', 0xa005a77c, 0xa005b314)
s2_rows = first_operand_rows('s2', 0xa005aa68, 0xa005c8f8)
assert s1_rows == ['0xa005a8cc: sw s1, 0x17c, s1']
assert all(': sw s2,' in s for s in s2_rows) and len(s2_rows) == 4
# These are stores with s1/s2 as source, not writes to the saved register.
profile = owner['profile']['digest']
result = dict(claim='P-06', status='PASS', mapping='VA - 0x9ffff000',
    rom_identity='Inherited CATALOG: 0041; 6769704 bytes; SHA256 972db4c136c7ed9e24a83c07c1a7fd62040ca018b08ca285216d26b1fee3c6b9',
    method='Bounded offline original bytes, Capstone RV32+C, independent JAL/branch fields; no target/model execution',
    sources=[dict(path=owner_path, evidence_id=owner['evidence_id'], profile_digest=profile,
                  scope='Only selected windows and saved-register definition metadata'),
             dict(path=uart_path, json_pointer='/functions/address=0xa00a8330',
                  evidence_id=uart['evidence_id'], profile_digest=uart['profile_digest'],
                  scope='UART callback global fd read window only')],
    windows=records, checks=checks,
    retained_saved_register_checks=[dict(reg='s1', start='0xa005a77c', end_exclusive='0xa005b314', first_operand_rows=s1_rows),
                                    dict(reg='s2', start='0xa005aa68', end_exclusive='0xa005c8f8', first_operand_rows=s2_rows)],
    successor_seed=dict(path=owner_path, evidence_id=owner['evidence_id'], profile_digest=profile,
                        scope='Retained listing seed only, no CFG/reallocation or post-deinit drain claim',
                        assembly=[s for s in owner['assembly'] if int(s.split(':')[0],16) in
                                  [0xa005c9e6,0xa005cbb2,0xa005cbb6,0xa005cbba,0xa005cbe2]]),
    limitations=['Metadata scan is not a proof of all possible CFG entries or computed control flow.',
                 'Callee-saved register preservation and normal callee returns are conditions.',
                 'No new REA Evidence or profile: listed profiles apply only to retained sources.',
                 'No claim that fd global slot never changes; callback reloads current global fd.',
                 'No proof of post-deinit pending drain, fd close, timer deletion or hardware quiescence.'])
(OUT/'instruction-evidence.json').write_text(json.dumps(result, indent=2)+'\n', encoding='utf-8')
(OUT/'instruction-evidence.txt').write_text('\n\n'.join(w['name']+'\n'+'\n'.join(r['pc']+' '+r['raw']+' '+r['asm'] for r in w['rows']) for w in records)+'\n', encoding='utf-8')
print(json.dumps(dict(status='PASS', windows=len(records), bytes=sum(int(w['end_exclusive'],16)-int(w['start'],16) for w in records), instructions=len(rows), checks=len(checks), retained_register_checks=2)))
