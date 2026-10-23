"""A12: bounded ROM reads and instruction-field review; never execute target code."""
import json
from pathlib import Path
import capstone

HERE = Path(__file__).resolve().parent
ROOT = Path('D:/Documents/PlatformIO/Projects/cuktech-ap01-firmware')
ROM = ROOT / 'roms/0041/ap01-1.0.2_0041.bin'
BASE = 0x9ffff000
prior_path = HERE.parent / 'current-object-writer-a11-0041-20261023/instruction-evidence.json'
prior = json.loads(prior_path.read_text(encoding='utf8'))
with ROM.open('rb') as stream:
    stream.seek(0xa00272d4 - BASE)
    raw = stream.read(248)
assert len(raw) == 248
def word(pc, n=4):
    return int.from_bytes(raw[pc-0xa00272d4:pc-0xa00272d4+n], 'little')
def signed(x, n):
    return x - (1 << n) if x & (1 << (n-1)) else x
checks = []
def check(pc, claim, actual, expected):
    assert actual == expected, (hex(pc), claim, actual, expected)
    checks.append(dict(pc=hex(pc), claim=claim, actual=actual, expected=expected))
def mem(pc, op, fn, reg, base, offset):
    x = word(pc)
    imm = ((x >> 25) << 5) | ((x >> 7) & 31) if op == 35 else x >> 20
    check(pc, 'memory opcode/width/register/base/offset',
          [x & 127, (x >> 12) & 7, (x >> (20 if op == 35 else 7)) & 31,
           (x >> 15) & 31, signed(imm, 12)], [op, fn, reg, base, offset])
def cm(pc, store, reg, base, offset):
    x = word(pc, 2)
    off = ((x >> 10) & 7) * 8 + ((x >> 6) & 1) * 4 + ((x >> 5) & 1) * 64
    check(pc, 'compressed word opcode/register/base/offset',
          [x & 0xe003, 8+((x >> 2) & 7), 8+((x >> 7) & 7), off],
          [0xc000 if store else 0x4000, reg, base, offset])
def br(pc, fn, rs1, rs2, target):
    x = word(pc)
    d = ((x >> 31) << 12) | (((x >> 7) & 1) << 11) | (((x >> 25) & 63) << 5) | (((x >> 8) & 15) << 1)
    check(pc, 'branch unsigned/signed operands and target',
          [x & 127, (x >> 12) & 7, (x >> 15) & 31, (x >> 20) & 31, hex(pc+signed(d,13))],
          [99,fn,rs1,rs2,hex(target)])
def cb(pc, nz, reg, target):
    x = word(pc,2)
    d = (((x >> 12)&1)<<8) | (((x >> 10)&3)<<3) | (((x >> 5)&3)<<6) | (((x >> 3)&3)<<1) | (((x >> 2)&1)<<5)
    check(pc, 'compressed conditional target', [x & 0xe003,8+((x>>7)&7),hex(pc+signed(d,9))], [0xe001 if nz else 0xc001,reg,hex(target)])
def jump(pc, target, compact=False):
    x = word(pc,2 if compact else 4)
    if compact:
        d = (((x>>12)&1)<<11)|(((x>>11)&1)<<4)|(((x>>9)&3)<<8)|(((x>>8)&1)<<10)|(((x>>7)&1)<<6)|(((x>>6)&1)<<7)|(((x>>3)&7)<<1)|(((x>>2)&1)<<5)
        check(pc, 'C.J target', [x & 0xe003, hex(pc+signed(d,12))], [0xa001,hex(target)])
    else:
        d = ((x>>31)<<20)|(((x>>12)&255)<<12)|(((x>>20)&1)<<11)|(((x>>21)&1023)<<1)
        check(pc, 'JAL ra target', [x & 0xfff, hex(pc+signed(d,21))], [0xef,hex(target)])

# Each original row is independently fetched/decoded, never used as input bytes.
decoder = capstone.Cs(capstone.CS_ARCH_RISCV, capstone.CS_MODE_RISCV32 | capstone.CS_MODE_RISCVC)
windows = []
for lo,hi in [(0xa00272d4,0xa0027340),(0xa0027340,0xa00273cc)]:
    rows=[]
    for ins in decoder.disasm(raw[lo-0xa00272d4:hi-0xa00272d4],lo):
        rows.append(dict(pc=hex(ins.address),bytes=ins.bytes.hex(),asm=ins.mnemonic+' '+ins.op_str))
    assert sum(len(bytes.fromhex(r['bytes'])) for r in rows) == hi-lo
    old = next(w for w in prior['windows'] if int(w['start'],16)==lo)
    assert rows == old['instructions']
    windows.append(dict(start=hex(lo),end_exclusive=hex(hi),instructions=rows,a11_rows_equal=True))

for pc,op,fn,reg,base,off in [
    (0xa00272d4,3,4,14,10,16),(0xa00272f8,3,4,13,15,16),
    (0xa0027306,35,2,0,10,4),(0xa0027314,35,2,0,10,0),
    (0xa0027330,35,2,0,10,0),(0xa0027334,35,2,0,10,4),
    (0xa0027350,3,2,18,11,-1000),(0xa0027356,3,1,15,18,32),
    (0xa002735e,3,4,14,18,16),(0xa0027362,3,4,15,10,16),
    (0xa0027378,35,0,15,9,28),(0xa0027396,3,1,15,18,32),
    (0xa00273b6,35,0,15,9,28),(0xa00273be,35,0,14,15,28),
    (0xa00273c6,35,0,15,9,28)]: mem(pc,op,fn,reg,base,off)
for args in [(0xa00272f4,False,15,11,0),(0xa0027300,False,14,15,4),
    (0xa0027304,True,15,10,0),(0xa002730a,True,10,15,4),
    (0xa002730c,True,10,11,0),(0xa0027310,False,15,15,0),
    (0xa0027318,True,15,10,4),(0xa002731a,True,10,15,0),
    (0xa002731c,True,10,11,4),(0xa0027322,True,15,10,0),
    (0xa0027324,True,14,10,4),(0xa0027326,True,10,14,0),
    (0xa0027328,True,10,15,4),(0xa002732c,False,15,11,4),
    (0xa0027338,True,10,11,0),(0xa002733a,True,10,11,4),
    (0xa002739c,False,15,9,12),(0xa00273ba,False,15,9,0)]: cm(*args)
for args in [(0xa00272fc,7,13,14,0xa0027310),(0xa002735a,5,0,15,0xa002738a),
    (0xa0027366,7,14,15,0xa002738a),(0xa002739e,4,0,15,0xa00273b4)]: br(*args)
for args in [(0xa00272d8,True,14,0xa00272f4),(0xa00272f6,False,15,0xa002732c),
    (0xa0027302,True,14,0xa0027322),(0xa002732e,True,15,0xa0027314),
    (0xa0027394,False,10,0xa00273c4),(0xa002739a,True,15,0xa00273a2)]: cb(*args)
for pc,to in [(0xa00272f0,0xa0019672),(0xa0027372,0xa00272d4),
    (0xa0027390,0xa00272d4),(0xa00273b0,0xa0019672)]: jump(pc,to)
for pc,to in [(0xa002730e,0xa002733c),(0xa0027312,0xa00272f6),
    (0xa002732a,0xa002731e),(0xa00273c2,0xa002737e),(0xa00273ca,0xa002737e)]: jump(pc,to,True)
for pc,value,n in [(0xa002734c,0x62fc75b7,4),(0xa0027354,0x84aa,2),
    (0xa002736a,0x62fc75b7,4),(0xa002736e,0xc0c58593,4),
    (0xa002738a,0xc1858593,4),(0xa002738e,0x8526,2),
    (0xa002731e,0x4501,2),(0xa0027320,0x8082,2),
    (0xa002733c,0x4505,2),(0xa002733e,0x8082,2),
    (0xa002737c,0x4501,2),(0xa00273b4,0x478d,2),
    (0xa00273bc,0x4709,2),(0xa00273c4,0x4789,2)]: check(pc,'literal transfer/return/state encoding',word(pc,n),value)
out=dict(task='A12',baseline='139d99431cf70fbd8fc74b3e87522677f0fb0b19',rom=str(ROM),mapping_base=hex(BASE),rom_offset=hex(0xa00272d4-BASE),bytes_reviewed=len(raw),capstone=capstone.__version__,windows=windows,checks=checks,source=prior['source_path_records'],verdict='accepted; no A11 correction',limits=['Two functions only; inherited Ghidra extents','No firmware execution, runtime object identity or scheduler contract','No diagnostic return ABI or source/version equivalence established'])
(HERE/'review-evidence.json').write_text(json.dumps(out,indent=2)+'\n',encoding='utf8')
print(f'PASS: {len(checks)} field/target/literal checks; 248 bytes; 91 instruction rows equal A11')
