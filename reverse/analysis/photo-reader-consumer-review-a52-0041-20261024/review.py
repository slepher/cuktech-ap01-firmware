"""A52 independent static ABI/width review; does not run A50 or any model."""
import json
from pathlib import Path

HERE = Path(__file__).resolve().parent
REV = HERE.parents[1]
MAIN = Path('D:/Documents/PlatformIO/Projects/cuktech-ap01-firmware')
BASE = 0x9ffff000
rom = (MAIN / 'roms/0041/ap01-1.0.2_0041.bin').read_bytes()
prior = json.loads((REV / 'analysis/photo-reader-consumer-a50-0041-20261024/evidence.json').read_text())
checks = []

def raw(pc, n):
    return rom[pc-BASE:pc-BASE+n]

def word(pc):
    return int.from_bytes(raw(pc, 4), 'little')

def sx(value, width):
    return value - (1 << width) if value & (1 << (width-1)) else value

def check(pc, actual, expected, kind):
    assert actual == expected, (hex(pc), kind, actual, expected)
    checks.append({'pc': hex(pc), 'kind': kind})

for row in prior['instructions']:
    pc = int(row['address'], 16)
    b = bytes.fromhex(row['bytes'])
    check(pc, raw(pc, len(b)), b, 'retained raw matches original')

def clw(pc, register, base, offset):
    w = int.from_bytes(raw(pc, 2), 'little')
    fields = (w & 3, w >> 13, 8+((w >> 2) & 7), 8+((w >> 7) & 7),
              (((w >> 5) & 1) << 6) | (((w >> 10) & 7) << 3) | (((w >> 6) & 1) << 2))
    check(pc, fields, (0, 2, register, base, offset), 'compressed LW fields')

for args in [(0xa008b8ae,10,9,4), (0xa008b8b8,15,10,20),
             (0xa008b8c2,14,10,28), (0xa008b934,10,9,4),
             (0xa008b936,11,9,0), (0xa008b93a,15,10,28),
             (0xa008ba52,10,9,4), (0xa008ba58,11,9,0),
             (0xa008ba5a,15,10,20), (0xa008b9d4,15,10,28),
             (0xa008b94e,15,10,20), (0xa008ba66,15,9,8),
             (0xa008ba70,14,9,8)]:
    clw(*args)

def mem(pc, op, register, base, offset, funct3=2):
    w = word(pc)
    value = w >> 20 if op == 3 else ((w >> 25) << 5) | ((w >> 7) & 31)
    reg = (w >> 7) & 31 if op == 3 else (w >> 20) & 31
    check(pc, (w & 127, (w >> 12) & 7, reg, (w >> 15) & 31, sx(value,12)),
          (op,funct3,register,base,offset), 'ordinary memory fields')

for args in [(0xa010a5e2,3,14,10,16,4), (0xa008b8b4,3,20,10,4,2),
             (0xa008b8d6,3,19,14,8,2), (0xa008b8dc,3,23,14,12,2),
             (0xa008ba04,35,10,23,12,2), (0xa008ba0a,3,23,15,12,2),
             (0xa008ba6c,35,19,15,0,2), (0xa008ba72,3,12,8,-52,2),
             (0xa008b980,35,15,21,0,2), (0xa008b8cc,35,0,8,-56,2)]:
    mem(*args)

def cmv(pc, dst, source):
    w = int.from_bytes(raw(pc, 2), 'little')
    check(pc, (w & 3, w >> 12, (w >> 7) & 31, (w >> 2) & 31),
          (2,8,dst,source), 'compressed move fields')

for args in [(0xa008b8a0,9,10), (0xa008b8a2,22,11),
             (0xa008b8a4,18,12), (0xa008b8a6,21,13),
             (0xa008b9fe,10,20), (0xa008ba60,13,20),
             (0xa008ba62,12,23), (0xa008ba9a,13,18),
             (0xa008ba9c,12,22), (0xa008b960,20,10), (0xa008b996,10,20)]:
    cmv(*args)

for pc, target in [(0xa010a5ea,0xa008b888), (0xa008ba00,0xa008aea0),
                   (0xa008b912,0xa008ab76), (0xa008ba8e,0xa008ab76)]:
    w=word(pc)
    imm=((w >> 31) << 20) | (((w >> 12) & 255) << 12) | (((w >> 20) & 1) << 11) | (((w >> 21) & 1023) << 1)
    check(pc,(w & 127,(w >> 7) & 31,(pc+sx(imm,21)) & 0xffffffff),
          (111,1,target),'JAL target fields')

vendors = {0xa008b96c:(1,33,19,18,15), 0xa008b9c6:(1,32,12,24,15),
           0xa008b9ca:(3,30,12,12,0), 0xa008ba86:(1,32,12,18,15)}
for pc, fields in vendors.items():
    w=word(pc)
    check(pc,(w & 127,(w >> 12) & 7,w >> 25,(w >> 7) & 31,(w >> 15) & 31,(w >> 20) & 31),
          (11,*fields),'inherited vendor rule encoding')
model = Path(prior['vendor_rules']['path']).read_text()
assert all(rule in model for rule in prior['vendor_rules']['rules'])

sparse = [{'pc':hex(pc),'raw':raw(pc,2).hex(),'role':role} for pc,role in [
    (0xa008b8fe,'hit source adds B to derived position-start'),
    (0xa008b960,'save callback status in s4 before count clamp'),
    (0xa008b996,'return status s4 in a0')]]
result = {'passed': True, 'checks':checks, 'old_raw_rows':len(prior['instructions']),
          'sparse_anchors':sparse,'inherited_vendor_rules_match_text':True,
          'accepted':['read D+14: (D,H,dst,want,&count)', 'seek D+1c: (D,H,position,0)',
                      'C+c lazy buffer allocation and post-callback C reload',
                      'u32 count/out-count/cursor and cross-copy low31 mask',
                      'W/O copy and conditional return inherited from A47/A49'],
          'corrections':0,'new_functionality':0,
          'unknown':['concrete D and callback implementation','actual photo mode1 execution',
                     'special config ffffffff','all failed I/O branches and final DELETE'],
          'shared_rea_target':False}
(HERE / 'review-result.json').write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
print(json.dumps({'passed':True,'checks':len(checks),'old_raw_rows':len(prior['instructions']),'sparse_anchors':len(sparse),'new_functionality':0}))
