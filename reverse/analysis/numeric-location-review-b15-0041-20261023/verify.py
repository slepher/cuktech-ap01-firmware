"""Independent B15 static byte/encoding review. Never executes firmware."""
import json
from pathlib import Path
from capstone import Cs, CS_ARCH_RISCV, CS_MODE_RISCV32, CS_MODE_RISCVC

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
ROM = Path('D:/Documents/PlatformIO/Projects/cuktech-ap01-firmware/roms/0041/ap01-1.0.2_0041.bin')
BASE = 0x9ffff000
data = ROM.read_bytes()
md = Cs(CS_ARCH_RISCV, CS_MODE_RISCV32 | CS_MODE_RISCVC)
windows = [(0xa009c5fc, 0xa009c662), (0xa009db6e, 0xa009dbb0),
           (0xa00a0dea, 0xa00a0e5c), (0xa00a0c24, 0xa00a0c26)]
rows = []
for start, end in windows:
    chunk = data[start-BASE:end-BASE]
    seq = list(md.disasm(chunk, start))
    assert sum(i.size for i in seq) == end-start
    for i in seq:
        rows.append(dict(va=hex(i.address), offset=i.address-BASE,
                         raw=i.bytes.hex(), text=i.mnemonic+' '+i.op_str))
words = {int(r['va'], 16): int.from_bytes(bytes.fromhex(r['raw']), 'little') for r in rows}
sx = lambda n, bits: (n ^ (1 << (bits-1))) - (1 << (bits-1))
checks = []
def record(addr, label, value, expected):
    assert value == expected, (hex(addr), label, value, expected)
    checks.append(dict(va=hex(addr), label=label, actual=value))

# Decode every direct branch/JAL from its bits, not Capstone's relative text.
controls = []
for r in rows:
    p = int(r['va'], 16); w = words[p]
    if len(r['raw']) == 8 and w & 127 == 0x63:
        disp = ((w>>31&1)<<12)|((w>>7&1)<<11)|((w>>25&63)<<5)|((w>>8&15)<<1)
        controls.append([hex(p), 'branch', w>>12&7, w>>15&31, w>>20&31, hex(p+sx(disp,13))])
    elif len(r['raw']) == 8 and w & 127 == 0x6f:
        disp = ((w>>31&1)<<20)|((w>>12&255)<<12)|((w>>20&1)<<11)|((w>>21&1023)<<1)
        controls.append([hex(p), 'jal', w>>7&31, hex(p+sx(disp,21))])
    elif len(r['raw']) == 4 and w&3 == 1 and w>>13 in (6,7):
        disp = ((w>>12&1)<<8)|((w>>10&3)<<3)|((w>>5&3)<<6)|((w>>3&3)<<1)|((w>>2&1)<<5)
        controls.append([hex(p), 'c.branch', w>>13, 8+(w>>7&7), hex(p+sx(disp,9))])
expected_controls = [
 ['0xa009c60c','branch',7,13,14,'0xa009c65c'],
 ['0xa009c624','branch',7,13,14,'0xa009c660'],
 ['0xa009c64e','jal',1,'0xa008b51a'],
 ['0xa009db76','branch',0,15,9,'0xa009dba8'],
 ['0xa009db88','jal',1,'0xa009c5fc'],
 ['0xa009db8c','c.branch',6,10,'0xa009dba8'],
 ['0xa009dba4','jal',1,'0xa0061848'],
 ['0xa00a0df8','jal',1,'0xa002dcae'],
 ['0xa00a0e14','jal',1,'0xa0061848'],
 ['0xa00a0e2a','jal',1,'0xa002dcae'],
 ['0xa00a0e3a','jal',1,'0xa00501be'],
 ['0xa00a0e3e','branch',0,10,0,'0xa00a0cce'],
 ['0xa00a0e46','jal',1,'0xa009c5fc'],
 ['0xa00a0e4a','c.branch',6,10,'0xa00a0e5c'],
 ['0xa00a0e50','branch',1,15,19,'0xa00a0e5c'],
 ['0xa00a0e54','jal',1,'0xa00a5b90']]
record(windows[0][0], 'all direct branch/JAL targets and condition/register fields', controls, expected_controls)

def lui(p):
    w=words[p]; assert w&127==0x37
    return w&0xfffff000
def imm(p):
    w=words[p]; assert w&127==0x13
    return sx(w>>20,12)
w=words[0xa009c5fc]
record(0xa009c5fc, 'C.LUI signed six-bit immediate', sx(((w>>12&1)<<5)|(w>>2&31),6), -24)
record(0xa009c5fe, 'first lower bound negative, modulo RV32', ((-24<<12)+imm(0xa009c5fe))&0xffffffff, (-100000)&0xffffffff)
record(0xa009c608, 'first inclusive span', lui(0xa009c602)+imm(0xa009c608), 659012-100000)
record(0xa009c614, 'second lower bound negative, modulo RV32', (lui(0xa009c610)+imm(0xa009c614))&0xffffffff, (-659001000)&0xffffffff)
record(0xa009c61c, 'second inclusive span', (3<<12)+imm(0xa009c61c), 659012000-659001000)
for p,expected in [(0xa009c606,0x972a),(0xa009c61a,0x972a),
 (0xa009c620,0x87aa),(0xa009c622,0x4505),(0xa009c656,0x4501),
 (0xa009c65c,0x4505),(0xa009c65a,0x8082),(0xa009c65e,0x8082),
 (0xa009c660,0x8082),(0xa009db82,0x8526),(0xa009db96,0x4691),
 (0xa00a0c24,0x498d)]:
    record(p, 'compressed arithmetic/input/return encoding', words[p], expected)

# Independently extract all ordinary memory widths, bases, values and offsets.
memory=[]
for r in rows:
    p=int(r['va'],16); w=words[p]
    if len(r['raw'])!=8: continue
    if w&127==3:
        memory.append([hex(p),'load',w>>12&7,w>>7&31,w>>15&31,sx(w>>20,12)])
    elif w&127==0x23:
        off=(w>>25<<5)|(w>>7&31)
        memory.append([hex(p),'store',w>>12&7,w>>20&31,w>>15&31,sx(off,12)])
record(0xa009db84, '3/8 store is SW s1,s2+192 before validator', next(x for x in memory if x[0]=='0xa009db84'), ['0xa009db84','store',2,9,18,192])
record(0xa00a0e42, 'kind5 reads LW a0,s2+192', next(x for x in memory if x[0]=='0xa00a0e42'), ['0xa00a0e42','load',2,10,18,192])
record(0xa00a0e58, 'kind5 clears flags with SB zero,s1+0', next(x for x in memory if x[0]=='0xa00a0e58'), ['0xa00a0e58','store',0,0,9,0])
predicate_memory=[r for r in rows if int(r['va'],16)<0xa009c662 and any(r['text'].startswith(op) for op in ('c.sw','c.lw','sw ','lw ','sb ','sh ','lb ','lh ','lbu ','lhu '))]
record(0xa009c628, 'complete predicate memory operations are stack-only', [r['text'] for r in predicate_memory], ['c.swsp s0, 8(sp)','c.swsp ra, 0xc(sp)','c.lwsp ra, 0xc(sp)','c.lwsp s0, 8(sp)'])
strings={}
for p,expected in [(0xa02654c8,'[lvgl2miio]Invalid area code: %d'),(0xa02681c0,'ck_miio_is_area_code_valid'),(0xa01c3014,'PogoPinMng/MiIotMng.c'),(0xa01c3068,'ck_config'),(0xa01c327c,'loc_id'),(0xa01c326c,'loc_district')]:
    actual=data[p-BASE:].split(b'\0',1)[0].decode('ascii')
    record(p,'ROM string',actual,expected); strings[hex(p)]=actual

# B14 is comparison evidence only: all bytes are freshly read above.
prior=json.loads((ROOT/'reverse/analysis/numeric-location-setter-b14-0041-20261023/instruction-evidence.json').read_text(encoding='utf-8'))
prior_rows=[r for seq in prior['windows'].values() for r in seq]
record(0xa009c5fc,'all B14 addresses/raw bytes match independent fresh ROM decode',[(r['va'],r['raw']) for r in rows],[(r['address'],r['hex']) for r in prior_rows])
out=dict(status='passed', rom=str(ROM), mapping='offset=VA-0x9ffff000', windows=[list(map(hex,x)) for x in windows],
         byte_count=sum(b-a for a,b in windows), instruction_count=len(rows), rows=rows,
         controls=controls,memory_fields=memory,strings=strings,checks=checks,
         limitations=['Static decoding, not target execution or input testing.', 'Caller snippets only; no config/logger implementations or source authentication.'])
(HERE/'review-evidence.json').write_text(json.dumps(out,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
print(f"PASS: {out['byte_count']} bytes, {len(rows)} instructions, {len(controls)} control transfers, {len(checks)} assertions")
for r in rows: print(r['va'],r['raw'],r['text'])
