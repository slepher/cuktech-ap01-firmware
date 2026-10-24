"""Read-only sparse ROM/field checks; never execute target or supplied inputs."""
import json
from pathlib import Path
from capstone import Cs, CS_ARCH_RISCV, CS_MODE_RISCV32, CS_MODE_RISCVC

HERE = Path(__file__).resolve().parent
MAIN = Path('D:/Documents/PlatformIO/Projects/cuktech-ap01-firmware')
BASE = 0x9ffff000
rom = (MAIN / 'roms/0041/ap01-1.0.2_0041.bin').read_bytes()
old = next(f for f in json.loads((MAIN / 'reverse/analysis/buzzer-backlight-0041-20261023.json').read_text())['functions'] if f['address'] == '0xa00a8582')
retained = old['raw_ranges'][0]
old_base = int(retained['start'], 16)
old_raw = bytes.fromhex(retained['hex'])
def raw(pc, n): return rom[pc-BASE:pc-BASE+n]
def word(pc): return int.from_bytes(raw(pc, 4), 'little')
def sx(v, n): return v-(1 << n) if v & (1 << (n-1)) else v
def branch(pc):
    w = word(pc)
    assert w & 127 == 0x63
    d = ((w >> 31) << 12) | (((w >> 7) & 1) << 11) | (((w >> 25) & 63) << 5) | (((w >> 8) & 15) << 1)
    return pc + sx(d, 13)
def jal(pc):
    w = word(pc)
    assert w & 127 == 0x6f
    d = ((w >> 31) << 20) | (((w >> 12) & 255) << 12) | (((w >> 20) & 1) << 11) | (((w >> 21) & 1023) << 1)
    return pc + sx(d, 21)
def load(pc, f3, rd, rs, off):
    w = word(pc)
    assert (w & 127, (w >> 12) & 7, (w >> 7) & 31, (w >> 15) & 31, sx(w >> 20, 12)) == (3, f3, rd, rs, off)

windows = [(0xa00a85b8, 0xa00a85c8), (0xa00a8602, 0xa00a8616),
           (0xa00a98d0, 0xa00a995c), (0xa00a997c, 0xa00a9988),
           (0xa00a93c2, 0xa00a93ce), (0xa00a93e8, 0xa00a9408)]
cs = Cs(CS_ARCH_RISCV, CS_MODE_RISCV32 | CS_MODE_RISCVC)
rows = []
for start, end in windows:
    assert raw(start, end-start) == old_raw[start-old_base:end-old_base]
    pc = start
    while pc < end:
        n = 2 if int.from_bytes(raw(pc, 2), 'little') & 3 != 3 else 4
        assert pc + n <= end
        code = raw(pc, n)
        ins = next(cs.disasm(code, pc), None)
        assert ins is not None or pc in [0xa00a9900, 0xa00a9940, 0xa00a994c]
        rows.append({'pc': hex(pc), 'raw': code.hex(), 'decode': ins.mnemonic+' '+ins.op_str if ins else 'vendor; fields checked separately'})
        pc += n

branches = {0xa00a8606: 0xa00a88f6, 0xa00a860e: 0xa00a8616,
            0xa00a98da: 0xa00a9ab6, 0xa00a98ec: 0xa00a9906,
            0xa00a98f4: 0xa00a9988, 0xa00a9912: 0xa00a9ab6,
            0xa00a992c: 0xa00a9d06, 0xa00a9934: 0xa00a9d06}
for pc, target in branches.items(): assert branch(pc) == target
for pc, expected in [(0xa00a98da,(1,11,15)), (0xa00a98ec,(0,18,0)),
                     (0xa00a98f4,(7,19,15)), (0xa00a9912,(0,10,0)),
                     (0xa00a992c,(0,15,0)), (0xa00a9934,(7,19,13))]:
    w = word(pc)
    assert ((w >> 12) & 7,(w >> 15) & 31,(w >> 20) & 31) == expected
assert word(0xa00a860a) == 0x05600793
assert word(0xa00a98d4) == 0x2e078823  # SB zero to global active command
calls = {0xa00a8612: 0xa00a98d0, 0xa00a990e: 0xa00501be,
         0xa00a991c: 0xa000589c, 0xa00a997c: 0xa008b51a,
         0xa00a9982: 0xa00a389c}
for pc, target in calls.items(): assert jal(pc) == target
for args in [(0xa00a98e2,2,18,15,0x2cc), (0xa00a98e6,4,19,12,0),
             (0xa00a98f0,4,15,18,6), (0xa00a98f8,2,18,18,0),
             (0xa00a9920,2,15,20,0x2cc), (0xa00a9930,4,13,15,6),
             (0xa00a9950,5,17,15,0x1a), (0xa00a9954,5,16,15,0x18),
             (0xa00a9958,5,15,15,0x1c), (0xa00a93c6,2,14,15,0x2cc),
             (0xa00a93ec,2,15,15,0x2cc), (0xa00a93f0,4,14,15,6),
             (0xa00a9400,2,25,15,0)]: load(*args)
for pc, expected in {0xa00a98fc:0x1a800793, 0xa00a9924:0x1a800713,
                     0xa00a9928:0x02e98733, 0xa00a93f8:0x1a800a13,
                     0xa00a93fc:0x03448a33, 0xa00a9404:0x014c8db3}.items():
    assert word(pc) == expected
for pc, expected in {0xa00a85ba:'b284', 0xa00a98d8:'b547', 0xa00a9904:'6109',
                     0xa00a9906:'8504', 0xa00a9908:'3146', 0xa00a990a:'ca85',
                     0xa00a990c:'2685', 0xa00a9916:'3146', 0xa00a9918:'a685',
                     0xa00a991a:'4a85', 0xa00a9938:'9443', 0xa00a993a:'8565',
                     0xa00a994a:'4d8e', 0xa00a9980:'4e85'}.items(): assert raw(pc,2).hex() == expected, (hex(pc), raw(pc,2).hex(), expected)
vendor = []
for pc, expected in [(0xa00a9900,(11,1,18,19,15,16)),
                     (0xa00a9940,(11,4,12,13,14,32)),
                     (0xa00a994c,(11,5,12,13,14,32))]:
    w = word(pc)
    fields = (w & 127,(w >> 12) & 7,(w >> 7) & 31,(w >> 15) & 31,(w >> 20) & 31,w >> 25)
    assert fields == expected
    vendor.append({'pc':hex(pc),'raw':raw(pc,4).hex(),'fields':fields})
model_path = MAIN / 'evidence/rea-0041-20261017/ghidra/Ghidra/Processors/RISCV/data/languages/ap01thead2.sinc'
model = model_path.read_text()
rules = []
for token, required in [(':th.mula ', 'rd = rd + (rs1 * rs2)'), (':th.lrw ', 'local value:4 = *[ram]:4 ea'), (':th.srw ', '*[ram]:4 ea = rd:4')]:
    at = model.index(token)
    rule = model[at:model.index('\n}',at)+2]
    assert required in rule
    rules.append(rule)
assert (word(0xa00a9940) >> 25) & 3 == 0  # indexed shift=0
assert (word(0xa00a994c) >> 25) & 3 == 0
assert word(0xa00a993c) == 0x80058593  # 0x1000 - 0x800 = notification bit0x800
strings = {}
for pc in [0xa0269760,0xa026a3b8]:
    off = pc-BASE
    strings[hex(pc)] = rom[off:rom.index(0,off)].decode('ascii')
assert strings['0xa0269760'] == 'UiIFaceMngBmsChange = %d, DCap=%d,FCap=%d,RCap=%d'
result = {'static_only':True,'baseline':'565dc6e','retained_evidence_id':old['evidence_id'],
          'windows':[{'start':hex(a),'end_exclusive':hex(b)} for a,b in windows],
          'instructions':rows,'branches':{hex(a):hex(b) for a,b in branches.items()},
          'calls':{hex(a):hex(b) for a,b in calls.items()},'vendor_fields':vendor,
          'vendor_rule_source':str(model_path),'inherited_local_rules':rules,'strings':strings,
          'limits':['No target execution, model run, inputs, replay, SIM, build, device or external service.',
                    'Local SLEIGH rules are inherited semantic evidence, not independent vendor specification.',
                    '12-byte copy is a byte-sequence contract; no direct SH width or atomicity is asserted.',
                    'Physical unit and scheduling relative to a future cmd51 remain unknown.']}
(HERE/'evidence.json').write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
print(json.dumps({'passed':True,'selected_bytes':sum(b-a for a,b in windows),'instructions':len(rows),'branches':len(branches),'calls':len(calls),'vendor_words':len(vendor)}))
