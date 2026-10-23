"""C14 independent, static raw-encoding checks; no target execution."""
import json
from pathlib import Path
from capstone import Cs, CS_ARCH_RISCV, CS_MODE_RISCV32, CS_MODE_RISCVC

HERE = Path(__file__).resolve().parent
TREE = HERE.parents[2]
SOURCE = Path('D:/Documents/PlatformIO/Projects/cuktech-ap01-firmware')
ROM = SOURCE / 'roms/0041/ap01-1.0.2_0041.bin'
data = ROM.read_bytes()
BASE = 0x9ffff000
prior = json.loads((TREE / 'reverse/analysis/text-update-entry-c13-0041-20261023/instruction-evidence.json').read_text())
md = Cs(CS_ARCH_RISCV, CS_MODE_RISCV32 | CS_MODE_RISCVC)
checks = []

def raw(pc, n):
    return data[pc-BASE:pc-BASE+n]

def sx(n, bits):
    return n - (1 << bits) if n & (1 << (bits-1)) else n

def check(pc, kind, actual, expected):
    assert actual == expected, (hex(pc), kind, actual, expected)
    checks.append(dict(pc=hex(pc), kind=kind, raw=raw(pc, 4 if raw(pc, 1)[0] & 3 == 3 else 2).hex(), decoded=actual))

def word(pc):
    return int.from_bytes(raw(pc, 4), 'little')

def half(pc):
    return int.from_bytes(raw(pc, 2), 'little')

def itype(pc, opcode, rd, f3, rs1, imm):
    w = word(pc)
    check(pc, 'I fields [opcode,rd,funct3,rs1,imm]', [w & 127, w >> 7 & 31, w >> 12 & 7, w >> 15 & 31, sx(w >> 20, 12)], [opcode, rd, f3, rs1, imm])

def store(pc, rs1, rs2, f3, offset):
    w = word(pc)
    check(pc, 'S fields [opcode,rs1,rs2,funct3,offset]', [w & 127, w >> 15 & 31, w >> 20 & 31, w >> 12 & 7, sx((w >> 25 << 5) | (w >> 7 & 31), 12)], [35, rs1, rs2, f3, offset])

def cmv(pc, rd, rs2):
    h = half(pc)
    check(pc, 'C.MV fields [quadrant,funct4,rd,rs2]', [h & 3, h >> 12, h >> 7 & 31, h >> 2 & 31], [2, 8, rd, rs2])

def cword(pc, f3, base, reg, off):
    h = half(pc)
    offset = (h >> 10 & 7) * 8 + (h >> 6 & 1) * 4 + (h >> 5 & 1) * 64
    check(pc, 'C.LW/SW fields [quadrant,funct3,base,reg,offset]', [h & 3, h >> 13, 8+(h >> 7 & 7), 8+(h >> 2 & 7), offset], [0, f3, base, reg, off])

def candi(pc, reg, imm):
    h = half(pc)
    check(pc, 'C.ANDI fields', [h & 3, h >> 13, h >> 10 & 3, 8+(h >> 7 & 7), sx((h >> 12 & 1)*32+(h >> 2 & 31), 6)], [1, 4, 2, reg, imm])

windows = []
for start, end in [(0xa0091ee4, 0xa0091f8a), (0xa008bbd8, 0xa008bc64)]:
    ins = list(md.disasm(raw(start, end-start), start))
    assert ins[0].address == start and ins[-1].address + ins[-1].size == end
    assert sum(i.size for i in ins) == end-start
    rows = [dict(pc=hex(i.address), raw=i.bytes.hex(), assembly=i.mnemonic+' '+i.op_str) for i in ins]
    old = next(w for w in prior['windows'] if int(w['start'], 16) == start)
    assert [(r['pc'], r['raw'], r['assembly']) for r in rows] == [(r['address'], r['hex'], r['assembly']) for r in old['instructions']]
    windows.append(dict(start=hex(start), end_exclusive=hex(end), instructions=rows, c13_bytes_and_decode_match=True))

# Raw compressed frame construction and six argument stores, independent of mnemonics.
h = half(0xa0091ee4)
spimm = ((h >> 12 & 1) << 9) | ((h >> 6 & 1) << 4) | ((h >> 5 & 1) << 6) | ((h >> 3 & 3) << 7) | ((h >> 2 & 1) << 5)
check(0xa0091ee4, 'C.ADDI16SP frame', [h & 3, h >> 13, h >> 7 & 31, sx(spimm, 10)], [1, 3, 2, -64])
h = half(0xa0091eea)
off = ((h >> 7 & 15) << 6) | ((h >> 11 & 3) << 4) | ((h >> 5 & 1) << 3) | ((h >> 6 & 1) << 2)
check(0xa0091eea, 'C.ADDI4SPN s0', [h & 3, h >> 13, 8+(h >> 2 & 7), off], [0, 0, 8, 32])
for pc, reg, off in [(0xa0091ef0,12,8),(0xa0091ef2,13,12),(0xa0091ef4,14,16),(0xa0091ef6,15,20)]:
    cword(pc, 6, 8, reg, off)
store(0xa0091ef8,8,16,2,24)
store(0xa0091efc,8,17,2,28)
itype(0xa0091f5e,19,11,0,8,8)
store(0xa0091f64,8,11,2,-20)
cmv(0xa0091f42,9,10)
cmv(0xa0091f44,18,11)
cword(0xa0091f4a,2,9,10,44)
itype(0xa0091f4e,3,15,4,9,92)
candi(0xa0091f52,15,16)
store(0xa0091f5a,9,0,2,44)
cmv(0xa0091f62,10,18)
itype(0xa0091f6c,3,15,4,9,92)
cword(0xa0091f70,6,9,10,44)
cmv(0xa0091f72,10,9)
candi(0xa0091f74,15,-17)
store(0xa0091f76,9,15,0,92)
for pc, rd, rs in [(0xa008bbe2,12,10),(0xa008bbe4,13,11),(0xa008bbfa,10,11),(0xa008bc52,9,10),(0xa008bc5c,10,9)]:
    cmv(pc,rd,rs)
for pc, rs, off in [(0xa008bbe6,11,-28),(0xa008bbea,10,-24),(0xa008bbfc,11,-20)]:
    store(pc,8,rs,2,off)
for pc, rd in [(0xa008bbee,11),(0xa008bbf0,10)]:
    h=half(pc)
    check(pc,'C.LI zero',[h & 3,h >> 13,h >> 7 & 31,sx((h >> 12 & 1)*32+(h >> 2 & 31),6)],[1,2,rd,0])
itype(0xa008bbf6,19,11,0,10,1)
for pc, rd, off in [(0xa008bc04,11,-20),(0xa008bc08,12,-24),(0xa008bc0c,13,-28)]:
    itype(pc,3,rd,2,8,off)

# Every JAL and conditional branch in both complete windows, from encoding bits.
targets = {0xa0091f00:(10,7,0xa0091f42),0xa0091f4c:(10,6,0xa0091f5e),0xa0091f54:(15,7,0xa0091f5e),0xa008bc10:(10,7,0xa008bc52)}
calls = {0xa0091f30:0xa008b51a,0xa0091f3e:0xa0019672,0xa0091f46:0xa00dddf4,0xa0091f56:0xa008ab8a,0xa0091f68:0xa008bbd8,0xa0091f7a:0xa009166e,0xa008bbf2:0xa0053252,0xa008bc00:0xa008aea0,0xa008bc40:0xa008b51a,0xa008bc4e:0xa0019672,0xa008bc54:0xa0053252}
for pc,(reg,f3,dst) in targets.items():
    h=half(pc)
    disp=((h >> 12 & 1)<<8)|((h >> 10 & 3)<<3)|((h >> 5 & 3)<<6)|((h >> 3 & 3)<<1)|((h >> 2 & 1)<<5)
    check(pc,'C branch [quadrant,funct3,rs1,target]',[h & 3,h >> 13,8+(h >> 7 & 7),pc+sx(disp,9)],[1,f3,reg,dst])
for pc,dst in calls.items():
    w=word(pc)
    disp=((w >> 31)<<20)|((w >> 12 & 255)<<12)|((w >> 20 & 1)<<11)|((w >> 21 & 1023)<<1)
    check(pc,'JAL [opcode,rd,target]',[w & 127,w >> 7 & 31,pc+sx(disp,21)],[111,1,dst])
decoded_controls = {int(r['pc'],16) for w in windows for r in w['instructions'] if r['assembly'].split()[0] in ('jal','c.beqz','c.bnez')}
assert decoded_controls == targets.keys() | calls.keys()

strings=[]
for pc in [0xa02641a0,0xa0263224,0xa0263794,0xa02647f4]:
    start=pc-BASE
    value=data[start:data.index(0,start)].decode()
    assert value == next(s['text'] for s in prior['strings'] if int(s['address'],16)==pc)
    strings.append(dict(pc=hex(pc),text=value))
roots=[SOURCE/'reverse/sdk',SOURCE/'tooling']
names={'lv_label.c','lv_text.c','lv_version.h','lvgl.h','lv_mem.c'}
matches=[str(p) for root in roots for p in root.rglob('*') if p.is_file() and p.name.lower() in names]
summary=dict(result='passed',windows=2,bytes=306,instructions=sum(len(w['instructions']) for w in windows),raw_encoding_checks=len(checks),direct_targets=len(calls)+len(targets),source_strings=len(strings),bounded_source_matches=len(matches))
out=dict(task='C14',baseline='a10893d',rom=str(ROM),mapping_base=hex(BASE),summary=summary,windows=windows,raw_encoding_checks=checks,va_layout=[dict(register='a'+str(i),offset_from_entry_sp=-24+4*(i-2)) for i in range(2,8)],strings=strings,source_search=dict(roots=list(map(str,roots)),names=sorted(names),matches=matches),limits=['Static ROM bytes only; no target execution, simulation, device or network.','No formatter, allocator, refresh, diagnostic callee internals reviewed.','No shared writable REA session/database opened; C13 retained provenance reused.','Source search bounded to the stated roots and five filenames; version and vendor changes unknown.'])
(HERE/'review-evidence.json').write_text(json.dumps(out,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
print(json.dumps(summary))
