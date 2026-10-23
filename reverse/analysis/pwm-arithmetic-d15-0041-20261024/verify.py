"""Read-only ROM/retained-evidence checks; no emulation, builds or input probes."""
import hashlib
import json
import struct
import zipfile
from pathlib import Path

import capstone

HERE = Path(__file__).resolve().parent
TREE = HERE.parents[2]
MAIN = Path('D:/Documents/PlatformIO/Projects/cuktech-ap01-firmware')
ROM = MAIN / 'roms/0041/ap01-1.0.2_0041.bin'
BASE = 0x9ffff000
rom = ROM.read_bytes()
old = json.loads((TREE / 'reverse/analysis/buzzer-backlight-round2-20261023/capstone-windows.json').read_text())
w = old['windows'][0]
assert hashlib.sha256(rom).hexdigest() == '972db4c136c7ed9e24a83c07c1a7fd62040ca018b08ca285216d26b1fee3c6b9'
assert rom[w['file_offset']:w['file_offset'] + len(bytes.fromhex(w['hex']))] == bytes.fromhex(w['hex'])
md = capstone.Cs(capstone.CS_ARCH_RISCV, capstone.CS_MODE_RISCV32 | capstone.CS_MODE_RISCVC)

def raw(a, n):
    return rom[a - BASE:a - BASE + n]

# Only new helper/ABI/constant windows. Main driver assembly stays in round2.
spans = [
    (0xa013680e, 0xa0136854, 'frequency-loop-call-ABI'),
    (0xa001fa84, 0xa001fad4, 'u32-to-binary64-normal-path'),
    (0xa001f202, 0xa001f23e, 'leading-zero-helper'),
    (0xa001d814, 0xa001d85e, 'binary64-numerator-unpack'),
    (0xa001d8ca, 0xa001d92c, 'denominator-unpack-and-dispatch'),
    (0xa001d9ca, 0xa001da3a, 'normal-significand-division'),
    (0xa001dbfc, 0xa001dc36, 'rounding-mode-dispatch'),
    (0xa001dc80, 0xa001dcc4, 'binary64-result-pack'),
    (0xa001f042, 0xa001f0dc, 'binary64-to-u32-truncation'),
]
windows = []
for a, end, label in spans:
    data = raw(a, end-a)
    ins = list(md.disasm(data, a))
    assert sum(i.size for i in ins) == len(data), label
    windows.append(dict(label=label, start=hex(a), end_exclusive=hex(end),
                        instructions=[dict(address=hex(i.address), hex=i.bytes.hex(), text=i.mnemonic+' '+i.op_str) for i in ins]))

vendor = []
for a, expected, name in [
    (0xa01367e4, '8b966520', 'th.mula a3,a1,t1'),
    (0xa01367e8, '0b46e680', 'th.lrbu a2,a2,a4,0'),
    (0xa01367fa, 'f797f50e', 'historical PKBB16 a5,a1,a5'),
    (0xa0136804, '8bd7c644', 'th.srw a5,a3,a2,2'),
    (0xa01368ec, '8b966520', 'th.mula a3,a1,t1'),
    (0xa01368f0, '0b46e680', 'th.lrbu a2,a2,a4,0'),
    (0xa0136900, 'f797f50e', 'historical PKBB16 a5,a1,a5'),
    (0xa013690a, '8bd7c644', 'th.srw a5,a3,a2,2'),
    (0xa0136918, '8bc7e780', 'th.lrbu a5,a5,a4,0'),
]:
    assert raw(a,4).hex() == expected
    word = int.from_bytes(raw(a,4),'little')
    vendor.append(dict(address=hex(a), hex=expected, interpretation=name,
                       opcode=word&127, rd=(word>>7)&31, rs1=(word>>15)&31,
                       rs2=(word>>20)&31, funct3=(word>>12)&7,
                       funct7=word>>25, shift=(word>>25)&3))

calls = []
for pc, upper, low, target in [
    (0xa0136822, -0x117000, 0x262, 0xa001fa84),
    (0xa0136832, -0x119000, -0x36, 0xa001d7fc),
    (0xa013683a, -0x117000, -0x7f8, 0xa001f042),
]:
    u, j = struct.unpack('<II', raw(pc,8))
    signed = lambda x, bits: x-(1<<bits) if x&(1<<(bits-1)) else x
    assert signed(u&0xfffff000,32) == upper
    assert signed(j>>20,12) == low
    assert (pc+upper+low)&~1 == target
    calls.append(dict(pc=hex(pc), bytes=raw(pc,8).hex(), target=hex(target)))

anchors=[]
for a, expected, meaning in [
    (0xa01367c4, '6395da04', 'frequency-different branch to a013680e'),
    (0xa01367d2, '83d5c400', 'reload unsigned halfword cached period'),
    (0xa01367ee, 'c582', 'logical shift delta right 17'),
    (0xa0136844, '63688501', 'unsigned period less than 65536 branch to a0136854'),
    (0xa013685c, '23964401', 'cache period using sh before stop wait'),
    (0xa013689e, '8de9', 'nonzero timer high word skips to a01368d0'),
    (0xa01368a0, '63e8ad02', 'elapsed low above 100 skips to a01368d0'),
    (0xa01368ac, '3707ff3f', 'config preserved mask 0x3fff0000'),
    (0xa01368c4, '4177', 'period preserved mask 0xffff0000'),
    (0xa0136934, 'b70600f8fd16', 'lui 0xf8000 then addi -1 gives 0xf7ffffff'),
]:
    assert raw(a,len(bytes.fromhex(expected))).hex() == expected
    anchors.append(dict(address=hex(a), hex=expected, meaning=meaning))

records = []
ep = MAIN/'evidence/rea-0041-20261017/evidence'
for index in [652,668,692,8702]:
    f=ep/f'whole-rom-graph-20261023-{index:03d}.json'
    d=json.loads(json.loads(f.read_text())['content'][0]['text'])
    records.append(dict(path=str(f), evidence_id=d['evidence_id'], operation=d['operation'],
                        parameters=d['parameters'], body=d['normalized_result']['body']))

reuse=[]
for name in ['system-complete-0041.json','guide-complete-0041.json'] + [f'settings-0041-round2{x}.json' for x in ['', 'b','c','d','e']]:
    f=MAIN/'reverse/rehost'/name
    t=f.read_text(errors='replace')
    reuse.append(dict(path=str(f), exact_start_address_present='a0136762' in t))
late=MAIN/'evidence/rea-0041-20261017/round3/request.json'
request=json.loads(late.read_text())
reuse.append(dict(path=str(late), requested_procedures=[c['arguments'].get('procedure') for c in request['commands'] if 'procedure' in c['arguments']]))
zf=MAIN/'reverse/rehost/ap01-ui-0041-complete-source.zip'
with zipfile.ZipFile(zf) as z:
    reuse.append(dict(path=str(zf), pwm_buzzer_members=[n for n in z.namelist() if 'pwm' in n.lower() or 'buzzer' in n.lower()],
                      source_members_with_exact_address=[n for n in z.namelist() if n.endswith(('.c','.h')) and b'a0136762' in z.read(n)]))

assert struct.unpack('<d',raw(0xa061b5a8,8))[0] == 80000000.0
dispatch_base=0xa01bb900
dispatch=[dispatch_base+struct.unpack('<i',raw(dispatch_base+4*i,4))[0] for i in range(15)]
clz_table=0xa001f21c+0x19c000+0x5d4
assert all(raw(clz_table+i,1)[0] == i.bit_length() for i in range(256))
result=dict(method='Static bytes and bounded retained-record reuse only; no target or model execution',
            rom_identity_matches_inherited=True, round2_window_matches_current_ROM=True,
            constant=dict(address='0xa061b5a8', hex=raw(0xa061b5a8,8).hex(), binary64=80000000.0),
            sparse_windows=windows, vendor_words=vendor, calls=calls, anchors=anchors, inherited_records=records,
            reuse_search=reuse, division_dispatch=dict(base=hex(dispatch_base), entries=[hex(a) for a in dispatch], normal_pair_default='0xa001d9ca'),
            clz_table_bit_lengths_match=True,
            limitations=['Instruction interpretation uses inherited THead/P contracts, not hardware execution.',
                         'No source/version certification for software binary64 helpers.',
                         'No negative/zero/out-of-range input execution or synthetic PWM probes.',
                         'Exact-address search does not prove absence of aliases or earlier semantic recovery.'])
(HERE/'review-result.json').write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
print('PASS: inherited bytes, sparse helper windows, 9 vendor words, 3 call targets, constant, CLZ table, bounded reuse')
