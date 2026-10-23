"""B07 independent bounded ROM/encoding review. Never executes target code."""
import json
import sys
from pathlib import Path
from capstone import Cs, CS_ARCH_RISCV, CS_MODE_RISCV32, CS_MODE_RISCVC

HERE = Path(__file__).resolve().parent
TREE = HERE.parents[2]
SOURCE = Path(sys.argv[1])
rom = (SOURCE / 'roms/0041/ap01-1.0.2_0041.bin').read_bytes()
evidence = json.loads((TREE / 'reverse/analysis/basic-info-register-b06-0041-20261023/instruction-evidence.json').read_text(encoding='utf-8'))
md = Cs(CS_ARCH_RISCV, CS_MODE_RISCV32 | CS_MODE_RISCVC)
words = {}
checked = []
ordinary = 0
for window in evidence['windows']:
    pc = int(window['start'], 16)
    for record in window['instructions']:
        assert pc == int(record['address'], 16)
        off = pc - 0x9ffff000
        size = 4 if rom[off] & 3 == 3 else 2
        raw = rom[off:off + size]
        assert raw.hex() == record['hex'], hex(pc)
        words[pc] = int.from_bytes(raw, 'little')
        if pc not in (0xa01b2912, 0xa0089ce4):
            ins = next(md.disasm(raw, pc))
            assert ins.size == size
            assert ins.mnemonic + ' ' + ins.op_str == record['decode'], hex(pc)
            ordinary += 1
        pc += size
    assert pc == int(window['end_exclusive'], 16)
    checked.append(dict(name=window['name'], start=window['start'], end_exclusive=window['end_exclusive'], bytes=pc-int(window['start'], 16)))

checks = []
def check(name, actual, expected):
    assert actual == expected, (name, actual, expected)
    checks.append(dict(check=name, value=actual))

def sext(n, width):
    return n - (1 << width) if n & (1 << (width-1)) else n

def compact_mem(pc):
    w = words[pc]
    return (w & 3, w >> 13, 8 + ((w >> 7) & 7), 8 + ((w >> 2) & 7),
            ((w >> 10) & 7) * 8 + ((w >> 6) & 1) * 4 + ((w >> 5) & 1) * 64)

# Independent compressed memory fields: quadrant, opcode, base, destination/source, offset.
for pc, expected in {
    0xa01b28d6: (0,2,13,14,4), 0xa01b28d8: (0,2,13,13,0),
    0xa01b290c: (0,2,14,12,0), 0xa01b28fa: (0,6,10,9,0),
    0xa008af22: (0,2,10,10,0), 0xa008af38: (0,2,9,12,8),
    0xa008af42: (0,2,9,11,8), 0xa008af4e: (0,2,9,15,4),
    0xa0089ce2: (0,2,10,15,0), 0xa0089cf6: (0,2,10,15,0),
    0xa0089cfa: (0,6,11,12,4),
}.items():
    check(hex(pc) + ' compressed word memory fields', compact_mem(pc), expected)

for pc, expected in {0xa01b28fc:(10,18,4), 0xa008af50:(9,18,8), 0xa008af56:(9,18,4)}.items():
    w = words[pc]
    check(hex(pc) + ' SW fields', (w & 127, (w >> 12) & 7, (w >> 15) & 31, (w >> 20) & 31,
          sext(((w >> 25) << 5) | ((w >> 7) & 31),12)), (35,2,*expected))

w = words[0xa01b290e]
imm = ((w >> 31) << 12) | (((w >> 7) & 1) << 11) | (((w >> 25) & 63) << 5) | (((w >> 8) & 15) << 1)
check('callback-only BEQ fields and destination', (w&127,(w>>12)&7,(w>>15)&31,(w>>20)&31,0xa01b290e+sext(imm,13)), (99,0,10,12,0xa01b2918))
for pc, expected in {0xa01b2912:(14,4,14,13),0xa0089ce4:(12,5,11,15)}.items():
    w=words[pc]
    check(hex(pc)+' indexed fields', (w&127,(w>>7)&31,(w>>12)&7,(w>>15)&31,(w>>20)&31,(w>>25)&3,w>>27), (11,*expected,0,8))

for hi, lo, expected in [(0xa01b28f2,0xa01b28f6,0xa008af14),(0xa00a8b56,0xa00a8b5a,0xa01b28ce)]:
    u, i = words[hi], words[lo]
    check(hex(hi)+' AUIPC/JALR fields and target', (u&127,(u>>7)&31,i&127,(i>>7)&31,(i>>15)&31,(hi+sext(u&0xfffff000,32)+sext(i>>20,12))&0xfffffffe), (23,1,103,1,1,expected))

for pc in (0xa01b290a,0xa01b2918,0xa008af66,0xa0089cec,0xa0089d00):
    check(hex(pc)+' compressed return encoding',words[pc],0x8082)
# Exact encodings preserve the parameter saves, next-offset snapshot and explicit return move.
for pc, expected in {0xa01b28da:0x0691,0xa01b28ea:0x84aa,0xa01b28f0:0x892e,
                     0xa008af2a:0x892a,0xa008af60:0x854a,0xa0089cf8:0x95be}.items():
    check(hex(pc)+' dataflow encoding', words[pc], expected)
model = SOURCE / 'evidence/rea-0041-20261017/ghidra/Ghidra/Processors/RISCV/data/languages/ap01thead2.sinc'
lines = model.read_text(encoding='utf-8').splitlines()
for item in evidence['model_excerpts']:
    start = item['line']-1
    assert '\n'.join(lines[start:start+len(item['text'].splitlines())]) == item['text']
result = dict(task='B07',result='passed',windows=checked,ordinary_decode_matches=ordinary,
              independent_encoding_checks=len(checks),checks=checks,
              vendor_model='Existing local observation model only; two excerpts matched read-only source.',
              limitations=['No target execution or service/device access.', 'No upstream ISA/source certification.',
                           'Callback consumer, allocator, initialization and lifecycle excluded.'])
(HERE/'review-results.json').write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
print(json.dumps({k:result[k] for k in ('task','result','ordinary_decode_matches','independent_encoding_checks')}))
