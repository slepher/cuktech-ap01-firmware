"""M01 sparse static wrapper checks; no algorithm evaluation or target execution."""
import json
from pathlib import Path

HERE = Path(__file__).resolve().parent
MAIN = Path('D:/Documents/PlatformIO/Projects/cuktech-ap01-firmware')
BASE = 0x9ffff000
rom = (MAIN/'roms/0041/ap01-1.0.2_0041.bin').read_bytes()
def raw(pc, n): return rom[pc-BASE:pc-BASE+n]
def word(pc): return int.from_bytes(raw(pc, 4), 'little')
def sx(v, n): return v-(1 << n) if v & (1 << (n-1)) else v
checks = []
def require(pc, condition, meaning):
    assert condition, (hex(pc), meaning)
    checks.append({'pc':hex(pc),'meaning':meaning})

w = word(0xa00a46f0)
require(0xa00a46f0, (w & 127,(w >> 7) & 31,w & 0xfffff000) == (0x37,11,0x62fc9000), 'LUI a1,62fc9')
w = word(0xa00a46f6)
require(0xa00a46f6, (w & 127,(w >> 12) & 7,(w >> 7) & 31,(w >> 15) & 31,sx(w >> 20,12)) == (0x13,0,11,11,0x98), 'ADDI a1,a1,98: input G=62fc9098')
for pc, rd, value in [(0xa00a46f4,12,6),(0xa00a46fa,10,0)]:
    h = int.from_bytes(raw(pc,2),'little')
    imm = sx((((h >> 12) & 1) << 5) | ((h >> 2) & 31), 6)
    require(pc, (h & 3,h >> 13,(h >> 7) & 31,imm) == (1,2,rd,value), 'C.LI '+('a2=6' if rd == 12 else 'a0=0'))
w = word(0xa00a46fc)
d = ((w >> 31) << 20) | (((w >> 12) & 255) << 12) | (((w >> 20) & 1) << 11) | (((w >> 21) & 1023) << 1)
require(0xa00a46fc, (w & 127,(w >> 7) & 31,0xa00a46fc+sx(d,21)) == (0x6f,1,0xa00ee8fc), 'JAL ra,a00ee8fc')
for pc, expected, meaning in [(0xa00a4700,'b240','restore ra from sp+c'),
                              (0xa00a4702,'2244','restore s0 from sp+8'),
                              (0xa00a4704,'4101','restore sp+10'),
                              (0xa00a4706,'8280','return via ra; no a0 overwrite')]:
    require(pc,raw(pc,2).hex() == expected,meaning)
anchors = [(0xa00a46f0,4),(0xa00a46f4,2),(0xa00a46f6,4),(0xa00a46fa,2),
           (0xa00a46fc,4),(0xa00a4700,2),(0xa00a4702,2),(0xa00a4704,2),(0xa00a4706,2)]

# Reuse identity/coverage only. Do not run the old algorithm, tests, table generator,
# whole-ROM tooling, writer verifier or SIM service.
old = MAIN/'evidence/rea-0041-20261017/evidence'
extent = json.loads((old/'whole-rom-graph-20261023-4848.json').read_text())['structuredContent']
edge = json.loads((old/'whole-rom-graph-20261023-4849.json').read_text())['structuredContent']
crc = json.loads((old/'whole-rom-usb-crc-20261023-000.json').read_text())['structuredContent']
assert extent['normalized_result']['entrypoint'] == '0xa00a46e8'
assert edge['normalized_result'] == ['0xa00ee8fc']
assert crc['normalized_result']['procedure']['address'] == '0xa00ee8fc'
assert any(r['source_address'] == '0xa00a46fc' for r in crc['normalized_result']['incoming_references'])
contract_path = MAIN/'reverse/reports/ap01/usb-interface-ota-0041-20261023.md'
contract = contract_path.read_text(encoding='utf-8')
assert 'crc = ((crc << 8) ^ table[(crc >> 8) ^ byte]) & 0xffff' in contract
assert '0x1021' in contract and '不是原厂函数的运行向量验收' in contract
reuse = {'algorithm_contract':str(contract_path),'algorithm_evidence_id':crc['evidence_id'],
         'wrapper_extent_evidence_id':extent['evidence_id'],'wrapper_callee_evidence_id':edge['evidence_id'],
         'inherited':['positive-length unsigned16 table recurrence, polynomial0x1021',
                      'old table/host verification is static analyst contract, not guest execution or upstream source identification',
                      'L03/L04 call, low16 SH G+6, 8/1 write-service parameters and notification order'],
         'bounded_queries':[]}
terms = ['a00a46e8','62fc909e','62fc9098']
for name in ['system-complete-0041.json','guide-complete-0041.json','settings-0041-round2b.json','page-logic-0041.json']:
    p = MAIN/'reverse/rehost'/name
    if not p.exists():
        reuse['bounded_queries'].append({'file':str(p),'available':False})
        continue
    text = p.read_text(encoding='utf-8').lower()
    reuse['bounded_queries'].append({'file':str(p),'matching_terms':[t for t in terms if t in text]})
result = {'baseline':'1dcbfe6','static_only':True,'anchors':[{'pc':hex(pc),'raw':raw(pc,n).hex()} for pc,n in anchors],
          'checks':checks,'input':{'initial':0,'pointer':'0x62fc9098','length_bytes':6,'range':'62fc9098..62fc909d inclusive'},
          'return':'inherited algorithm a0 is unsigned16; wrapper does not alter it',
          'limits':['No target, instructions, algorithm inputs, vector enumeration, SIM, build, replay, model, device or service executed.',
                    'No CRC body/table exported or independently re-certified; inherited old local algorithm contract only.',
                    'No actual storage, readback, boot validation, field structure or upstream source guarantee.']}
(HERE/'evidence.json').write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
(HERE/'reuse.json').write_text(json.dumps(reuse,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
print(json.dumps({'passed':True,'sparse_anchors':len(anchors),'selected_bytes':sum(n for _,n in anchors),'checks':len(checks),'algorithm_evaluations':0}))
