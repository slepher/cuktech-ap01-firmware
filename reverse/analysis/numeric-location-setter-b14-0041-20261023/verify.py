"""B14: static ROM decoding only; no target execution or input probes."""
from pathlib import Path
import json
from capstone import Cs, CS_ARCH_RISCV, CS_MODE_RISCV32, CS_MODE_RISCVC

HERE = Path(__file__).resolve().parent
TREE = HERE.parents[2]
SOURCE = Path('D:/Documents/PlatformIO/Projects/cuktech-ap01-firmware')
ROM = SOURCE / 'roms/0041/ap01-1.0.2_0041.bin'
DOSSIER = SOURCE / 'evidence/rea-0041-20261017/evidence/whole-rom-private-20261023-005.json'
BASE = 0x9ffff000
rom = ROM.read_bytes()
ev = json.loads(DOSSIER.read_text(encoding='utf-8'))['structuredContent']
fn = ev['raw_result']['value']
assert ev['parameters']['procedure'] == '0xa009c5fc'
assert fn['procedure']['body']['ranges'] == [{'start': '0xa009c5fc', 'end': '0xa009c661'}]
md = Cs(CS_ARCH_RISCV, CS_MODE_RISCV32 | CS_MODE_RISCVC)
windows = [('predicate', 0xa009c5fc, 0xa009c662),
           ('property_3_8', 0xa009db6e, 0xa009dbb0),
           ('kind5', 0xa00a0dea, 0xa00a0e5c),
           ('callback_constant_3', 0xa00a0c24, 0xa00a0c26)]
rows, raw = {}, {}
for name, start, end in windows:
    seq = []
    p = start
    while p < end:
        size = 4 if rom[p-BASE] & 3 == 3 else 2
        data = rom[p-BASE:p-BASE+size]
        ins = next(md.disasm(data, p), None)
        assert ins and ins.size == size
        raw[p] = int.from_bytes(data, 'little')
        seq.append({'address': hex(p), 'file_offset': p-BASE, 'hex': data.hex(),
                    'decode': ins.mnemonic + ' ' + ins.op_str})
        p += size
    assert p == end
    rows[name] = seq
assert [r['address'] for r in rows['predicate']] == [s.split(':')[0] for s in fn['assembly']]

checks = []
def check(p, label, cond):
    assert cond, (hex(p), label)
    checks.append({'address': hex(p), 'check': label})
def sx(x, bits):
    return x - (1 << bits) if x & (1 << (bits-1)) else x
def branch(p, rs1, rs2, f3, target):
    w = raw[p]
    imm = ((w>>31)<<12)|((w>>7&1)<<11)|((w>>25&63)<<5)|((w>>8&15)<<1)
    check(p, 'raw branch registers/unsigned condition/absolute target',
          w&127==99 and w>>15&31==rs1 and w>>20&31==rs2 and
          w>>12&7==f3 and p+sx(imm,13)==target)
def jal(p, target):
    w = raw[p]
    imm = ((w>>31)<<20)|((w>>12&255)<<12)|((w>>20&1)<<11)|((w>>21&1023)<<1)
    check(p, 'raw JAL ra absolute target', w&127==111 and w>>7&31==1 and p+sx(imm,21)==target)
def iop(p, opcode, f3, rd, rs1, imm):
    w = raw[p]
    check(p, 'raw I-type opcode/registers/immediate/width',
          w&127==opcode and w>>12&7==f3 and w>>7&31==rd and w>>15&31==rs1 and sx(w>>20,12)==imm)
def store(p, f3, rs1, rs2, imm):
    w=raw[p]; v=(w>>25<<5)|(w>>7&31)
    check(p, 'raw store width/registers/offset', w&127==35 and w>>12&7==f3 and w>>15&31==rs1 and w>>20&31==rs2 and sx(v,12)==imm)
def cbeqz(p, rd, target):
    w=raw[p]
    v=((w>>12&1)<<8)|((w>>10&3)<<3)|((w>>5&3)<<6)|((w>>3&3)<<1)|((w>>2&1)<<5)
    check(p, 'raw C.BEQZ register/absolute target', w&3==1 and w>>13==6 and (w>>7&7)+8==rd and p+sx(v,9)==target)

branch(0xa009c60c,13,14,7,0xa009c65c)
branch(0xa009c624,13,14,7,0xa009c660)
branch(0xa009db76,15,9,0,0xa009dba8)
branch(0xa00a0e3e,10,0,0,0xa00a0cce)
branch(0xa00a0e50,15,19,1,0xa00a0e5c)
for p,t in [(0xa009c64e,0xa008b51a),(0xa009db88,0xa009c5fc),
            (0xa009dba4,0xa0061848),(0xa00a0e14,0xa0061848),
            (0xa00a0df8,0xa002dcae),(0xa00a0e2a,0xa002dcae),
            (0xa00a0e3a,0xa00501be),(0xa00a0e46,0xa009c5fc),
            (0xa00a0e54,0xa00a5b90)]: jal(p,t)
for p,t in [(0xa009db8c,0xa009dba8),(0xa00a0e4a,0xa00a0e5c)]:cbeqz(p,10,t)
for p,op,f3,rd,rs,imm in [
 (0xa009c5fe,19,0,14,14,-1696),(0xa009c608,19,0,13,13,1956),
 (0xa009c614,19,0,14,14,344),(0xa009c61c,19,0,13,13,-1288),
 (0xa009c63e,19,0,14,14,1224),(0xa009c642,19,0,13,13,448),
 (0xa009c646,19,0,12,0,1868),(0xa009c64a,19,0,11,11,20),
 (0xa009db72,3,2,15,15,352),(0xa009db7e,19,0,18,18,-256),
 (0xa009db98,19,0,12,18,192),(0xa009db9c,19,0,11,11,636),
 (0xa009dba0,19,0,10,10,104),(0xa00a0dee,19,0,18,18,-256),
 (0xa00a0df2,19,0,22,18,128),(0xa00a0e18,19,0,9,9,44),
 (0xa00a0e1c,3,4,15,9,0),(0xa00a0e22,19,6,15,15,2),
 (0xa00a0e42,3,2,10,18,192),(0xa00a0e4c,3,4,15,9,0)]:iop(p,op,f3,rd,rs,imm)
store(0xa009db84,2,18,9,192)
store(0xa00a0e26,0,9,15,0)
store(0xa00a0e58,0,9,0,0)
# Compressed arithmetic, return and setup: exact raw encoding independently fixed.
for p,w,label in [
 (0xa009c5fc,0x7721,'C.LUI a4,-24 => 0xfffe8000'),
 (0xa009c606,0x972a,'C.ADD a4,a0 full RV32 word'),
 (0xa009c618,0x668d,'C.LUI a3,3'),(0xa009c61a,0x972a,'C.ADD a4,a0'),
 (0xa009c620,0x87aa,'C.MV a5,a0 preserves input for log'),
 (0xa009c622,0x4505,'C.LI a0,1 before second success branch'),
 (0xa009c656,0x4501,'C.LI a0,0 after log'),
 (0xa009c65c,0x4505,'C.LI a0,1 first success'),
 (0xa009c65a,0x8082,'C.JR ra failure'),(0xa009c65e,0x8082,'C.JR ra first success'),
 (0xa009c660,0x8082,'C.JR ra second success'),
 (0xa009db82,0x8526,'C.MV a0,s1 full property value'),
 (0xa009db96,0x4691,'C.LI a3,4 persistence byte count'),
 (0xa00a0c24,0x498d,'C.LI s3,3 callback flag comparison')]:check(p,label,raw[p]==w)
for p,rd,upper in [(0xa009c602,13,0x88000),(0xa009c610,14,0xd8b87000),
 (0xa009c630,14,0xa0265000),(0xa009c634,13,0xa0268000),
 (0xa009c638,11,0xa01c3000),(0xa009db6e,15,0x62fc9000),
 (0xa009db7a,18,0x62fcb000),(0xa00a0dea,18,0x62fcb000),
 (0xa00a0e10,9,0x62fcb000)]:
    w=raw[p];check(p,'raw LUI register/upper constant',w&127==55 and w>>7&31==rd and w&0xfffff000==upper)
# The predicate has only the two explicit stack spills; no business-data store.
assert [r['address'] for r in rows['predicate'] if r['decode'].startswith(('sw ', 'sb ', 'sh ', 'c.sw'))] == ['0xa009c62a','0xa009c62c']
strings = {}
for p,expected in [(0xa02654c8,'[lvgl2miio]Invalid area code: %d'),
                   (0xa02681c0,'ck_miio_is_area_code_valid'),
                   (0xa01c3014,'PogoPinMng/MiIotMng.c'),
                   (0xa01c3068,'ck_config'),(0xa01c327c,'loc_id'),(0xa01c326c,'loc_district')]:
    value=rom[p-BASE:].split(b'\0',1)[0].decode('ascii')
    check(p,'ROM NUL-terminated string',value==expected);strings[hex(p)]=value
out={'status':'passed','rom_path':str(ROM),'mapping':'offset=VA-0x9ffff000',
     'source_dossier':str(DOSSIER),'source_evidence_id':ev['evidence_id'],
     'source_profile':ev['analysis_profile']['digest'],
     'source_function':{k:fn[k] for k in ['procedure','pseudocode','assembly','referenced_strings']},
     'windows':rows,'checks':checks,'strings':strings,
     'limitations':['Static encoding checks only; no firmware execution or input probes.',
                    'Caller snippets do not recover full property/callback or config/logger implementations.',
                    'No source version or unmodified upstream attribution.']}
(HERE/'instruction-evidence.json').write_text(json.dumps(out,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
print(f'passed: {sum(len(v) for v in rows.values())} ordinary instructions; {sum(sum(len(bytes.fromhex(r["hex"])) for r in v) for v in rows.values())} bytes; {len(checks)} checks')
