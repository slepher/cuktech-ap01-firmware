"""A18 independent bounded ROM encoding review; never runs target code."""
import json
from pathlib import Path
import capstone

OUT = Path(__file__).resolve().parent
ROOT = OUT.parents[1]
SOURCE = Path('D:/Documents/PlatformIO/Projects/cuktech-ap01-firmware')
ROM = SOURCE / 'roms/0041/ap01-1.0.2_0041.bin'
MODEL = SOURCE / 'evidence/rea-0041-20261017/ghidra/Ghidra/Processors/RISCV/data/languages/ap01thead2.sinc'
WINDOWS = [(0xa008ce16, 0xa008ce90), (0xa00ab6cc, 0xa00ab6f0)]
blocks = {}
with ROM.open('rb') as f:
    for lo, hi in WINDOWS:
        f.seek(lo - 0xa0000000 + 0x1000)
        blocks[lo] = f.read(hi-lo)
        assert len(blocks[lo]) == hi-lo

def raw(a, n):
    for start, data in blocks.items():
        if start <= a and a+n <= start+len(data):
            return data[a-start:a-start+n]
    raise ValueError(hex(a))

def bits(w, lo, hi): return (w >> lo) & ((1 << (hi-lo+1))-1)
def signed(v, n): return v - (1 << n) if v >= (1 << (n-1)) else v
checks = []
def verify(a, kind, actual, expected):
    assert actual == expected, (hex(a), kind, actual, expected)
    checks.append(dict(address=hex(a), kind=kind, fields=actual))
def w32(a): return int.from_bytes(raw(a, 4), 'little')
def w16(a): return int.from_bytes(raw(a, 2), 'little')

# Independently select fields rather than importing A17's extractor.
for a, kind, f3, rd, r1, r2 in [
    (0xa008ce6a, 'signed SLT', 2, 14, 11, 13),
    (0xa008ce74, 'signed SLT', 2, 11, 14, 13),
    (0xa008ce6e, 'MVNEZ encoding', 1, 13, 11, 14),
    (0xa008ce78, 'MVNEZ encoding', 1, 14, 13, 11)]:
    w = w32(a)
    custom = kind.startswith('MV')
    verify(a, kind, [bits(w,0,6), bits(w,12,14), bits(w,25,31), bits(w,7,11), bits(w,15,19), bits(w,20,24)],
           [11 if custom else 51, f3, 33 if custom else 0, rd, r1, r2])
for a, rs2 in [(0xa008ce64, 11), (0xa008ce7c, 14)]:
    w = w32(a)
    displacement = signed((bits(w,31,31)<<12) | (bits(w,7,7)<<11) | (bits(w,25,30)<<5) | (bits(w,8,11)<<1), 13)
    verify(a, 'BEQ target', [bits(w,0,6), bits(w,12,14), bits(w,15,19), bits(w,20,24), hex(a+displacement)], [99,0,12,rs2,'0xa008ce86'])
for a, target in [(0xa00ab6ea, 0xa008ce16), (0xa008ce82, 0xa008ccd2), (0xa00ab6e2, 0xa008ce90)]:
    w = w32(a)
    displacement = signed((bits(w,31,31)<<20) | (bits(w,12,19)<<12) | (bits(w,20,20)<<11) | (bits(w,21,30)<<1), 21)
    verify(a, 'JAL target', [bits(w,0,6),bits(w,7,11),hex(a+displacement)], [111,1,hex(target)])
for a, mode, reg, base, offset in [
    (0xa008ce62,2,12,10,64), (0xa008ce68,2,13,10,72),
    (0xa008ce72,2,14,10,68), (0xa008ce80,6,14,10,64),
    (0xa00ab6e6,2,10,9,24), (0xa00ab6ee,2,10,9,28)]:
    w = w16(a)
    off = (bits(w,5,5)<<6) | (bits(w,10,12)<<3) | (bits(w,6,6)<<2)
    verify(a, 'C.LW/C.SW fields', [bits(w,0,1),bits(w,13,15),bits(w,2,4)+8,bits(w,7,9)+8,off], [0,mode,reg,base,offset])
w = w32(0xa00ab6cc)
verify(0xa00ab6cc, 'signed LH fields', [bits(w,0,6),bits(w,12,14),bits(w,7,11),bits(w,15,19),signed(bits(w,20,31),12)], [3,1,18,10,12])
w = w16(0xa00ab6e8)
verify(0xa00ab6e8, 'C.MV fields', [bits(w,0,1),bits(w,12,15),bits(w,7,11),bits(w,2,6)], [2,8,11,18])
verify(0xa008ce8e, 'C.JR ra', hex(w16(0xa008ce8e)), '0x8082')

model_lines = MODEL.read_text().splitlines()
first = next(i for i,s in enumerate(model_lines) if s.startswith(':th.mvnez '))
last = next(i for i in range(first+1,len(model_lines)) if model_lines[i] == '}')
model = '\n'.join(model_lines[first:last+1])
assert 'if (rs2 == 0) goto <done>;' in model and 'rd = rs1;' in model
assert 'op2531=33' in model and 'op1214=1' in model and 'op0006=0xb' in model
custom = {0xa008ce6e:'th.mvnez a3,a1,a4', 0xa008ce78:'th.mvnez a4,a3,a1'}
md = capstone.Cs(capstone.CS_ARCH_RISCV, capstone.CS_MODE_RISCV32 | capstone.CS_MODE_RISCVC)
windows = []
for lo, hi in WINDOWS:
    rows = []
    a = lo
    while a < hi:
        n = 4 if w16(a)&3 == 3 else 2
        b = raw(a,n)
        ins = list(md.disasm(b,a))
        if a in custom:
            assert not ins
            text = custom[a]
        else:
            assert len(ins)==1 and ins[0].size==n
            text = ins[0].mnemonic+' '+ins[0].op_str
        rows.append(dict(address=hex(a),file_offset=a-0xa0000000+0x1000,bytes=b.hex(),instruction=text))
        a += n
    assert a == hi
    windows.append(dict(start=hex(lo),end_exclusive=hex(hi),rows=rows))

# Compare retained predecessor bytes with fresh reads, without rerunning its writer.
previous = json.loads((ROOT/'analysis/weather-current-consumer-a17-0041-20261023/instruction-evidence.json').read_text())
compared = 0
for window in previous['windows']:
    for row in window['rows']:
        b = bytes.fromhex(row['bytes'])
        assert raw(int(row['address'],16),len(b)) == b
        compared += 1
summary = dict(result='passed',static_only=True,windows=2,bytes=158,instructions=sum(len(w['rows']) for w in windows),encoding_checks=len(checks),predecessor_rows_matched=compared,vendor_words=2,remaining_undecoded_words=0)
evidence = dict(summary=summary,rom=str(ROM),mapping='file_offset = VA - 0xa0000000 + 0x1000',decoder='Capstone '+capstone.__version__,windows=windows,encoding_checks=checks,vendor_model=dict(path=str(MODEL),start_line=first+1,end_line=last+1,text=model),limits=['Static decoding only; no target execution or emulation.', 'MVNEZ semantics depend on the existing local model; no external ISA-source authentication.', 'a008ccd2 body not reviewed; a008ce90 body inherited from A15/A16, not reopened.', 'No new digest or artifact copy manifest.'])
(OUT/'instruction-review.json').write_text(json.dumps(evidence,indent=2)+'\n',encoding='utf-8')
(OUT/'review-index.json').write_text(json.dumps(summary,indent=2)+'\n',encoding='utf-8')
print(json.dumps(summary))
