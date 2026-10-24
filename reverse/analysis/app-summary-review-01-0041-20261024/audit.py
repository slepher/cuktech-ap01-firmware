"""Independent P-18 bounded static review; never imports or executes author code."""
import json
from pathlib import Path
import capstone

ROOT = Path('D:/Documents/PlatformIO/Projects/cuktech-ap01-firmware')
OUT = Path(__file__).parent
BASE = 0x9ffff000
rom = (ROOT/'roms/0041/ap01-1.0.2_0041.bin').read_bytes()
assert len(rom) == 6769704
bundle = json.loads((ROOT/'evidence/rea-0041-20261017/evidence/whole-rom-private-20261023.evidence.json').read_text(encoding='utf8'))
procs = ['0xa00adabc', '0xa005cc1e', '0xa00ad602']
records = {p: next(r for r in bundle['records'] if r.get('parameters',{}).get('procedure') == p) for p in procs}
saved = {}
for r in records.values():
    assert r['analysis_profile']['digest'] == 'b6368dd18431e8113aa5026c713d41e648ab0f6ddd9421ff6c4a49e23b3cd2f3'
    assert r['analysis_profile']['parameters']['language_id'] == 'RISCV:LE:32:ap01thead2'
    saved.update({int(s.split(':')[0],16):s for s in r['normalized_result']['assembly']})
md = capstone.Cs(capstone.CS_ARCH_RISCV,capstone.CS_MODE_RISCV32|capstone.CS_MODE_RISCVC)
# Sparse original windows only. Unknown vendor instructions are inherited, not decoded here.
windows = [(0xa00adae8,0xa00adaec),(0xa00adb02,0xa00adb06),(0xa00adb3e,0xa00adb64),
           (0xa00adb9e,0xa00adbbc),(0xa00adbf6,0xa00adc04),(0xa00adc08,0xa00adc10),
           (0xa00adc14,0xa00adce8),(0xa00add16,0xa00add3c),(0xa00ae196,0xa00ae19e),
           (0xa005da14,0xa005da18),(0xa005da4a,0xa005da78),(0xa00ad61e,0xa00ad620),
           (0xa008bd70,0xa008bd7c),(0xa008bdbc,0xa008bdca),
           (0xa008c2d0,0xa008c2dc),(0xa008c31c,0xa008c328)]
insns = {}
evidence=[]
for lo,hi in windows:
    seq=list(md.disasm(rom[lo-BASE:hi-BASE],lo))
    assert seq and sum(i.size for i in seq)==hi-lo
    if lo >= 0xa00ad000 or 0xa005cc1e <= lo < 0xa005e000:
        assert [i.address for i in seq] == sorted(a for a in saved if lo <= a < hi)
    for i in seq:
        insns[i.address]=i
        evidence.append(dict(address=hex(i.address),raw=i.bytes.hex(),assembly=i.mnemonic+' '+i.op_str,
                             retained=saved.get(i.address),source='original ROM; static Capstone '+capstone.__version__))

checks=[]
def check(a,m,o):
    i=insns[a]
    assert (i.mnemonic,i.op_str)==(m,o),(hex(a),i.mnemonic,i.op_str)
    checks.append(dict(address=hex(a),expected=m+' '+o,passed=True))

for a,m,o in [
 (0xa00adae8,'c.mv','s6, a0'),(0xa00adaea,'c.mv','s2, a1'),
 (0xa00adb5c,'lw','a5, 0(s2)'),(0xa00adb60,'sw','a5, 0x54(s6)'),
 (0xa00adba4,'lbu','a5, 0x4c(s6)'),(0xa00adbf6,'c.li','a1, 0'),(0xa00adbf8,'c.mv','a0, s6'),
 (0xa00adc08,'lui','s4, 0x62fc4'),(0xa00adc24,'c.lw','a5, 0x10(a0)'),
 (0xa00adc26,'lw','a4, -0xd4(s0)'),(0xa00adc2a,'c.lw','s1, 4(a5)'),
 (0xa00adc30,'c.add','a5, s8'),(0xa00adc32,'lbu','a5, 0x10(a5)'),
 (0xa00adc36,'addi','s4, s4, 0x2c'),(0xa00adc4a,'andi','a5, s8, 0xff'),
 (0xa00adc4e,'c.li','a4, 1'),(0xa00adc50,'c.add','a5, s4'),
 (0xa00adc52,'sb','a4, 0x28(a5)'),(0xa00adc56,'add','a5, s1, s8'),
 (0xa00adc5a,'sb','zero, 0x9d(a5)'),(0xa00adc5e,'sb','zero, 0x101(a5)'),
 (0xa00adc62,'sh','zero, 0xfa(s1)'),(0xa00adc66,'sb','zero, 0xfc(a5)'),
 (0xa00adc6a,'lw','a0, 0xf4(s1)'),(0xa00adc6e,'sb','a4, 0xe(s4)'),
 (0xa00adc76,'c.lw','a5, 0x14(a0)'),(0xa00adc78,'c.andi','a5, 1'),
 (0xa00adc80,'lw','a0, 0xf4(s1)'),(0xa00adcc4,'lw','a4, -0xd4(s0)'),
 (0xa00adcc8,'add','a5, s4, s8'),(0xa00adccc,'sb','a4, 0x10(a5)'),
 (0xa00adcd4,'lbu','a5, 0x15(a5)'),(0xa00adcd8,'lbu','a4, 0x21(s2)'),
 (0xa00adcdc,'lbu','s9, 0xe(s2)'),(0xa00add16,'andi','s11, s5, 0xff'),
 (0xa00add1e,'lbu','a5, 0x28(t1)'),(0xa00add22,'c.li','a4, 1'),
 (0xa00add28,'lbu','a4, 0xc(s4)'),(0xa00add30,'lbu','a5, 0xc(s2)'),
 (0xa005da14,'addi','s3, s2, 0x80'),(0xa005da50,'c.mv','a2, s2'),
 (0xa005da52,'addi','a1, a1, -0x448'),(0xa005da56,'addi','a0, a0, 0x602'),
 (0xa005da5e,'sw','a0, 0x74(s3)'),(0xa005da6c,'sw','s2, 4(s7)'),
 (0xa005da74,'sw','s7, 0x10(s1)'),(0xa00ad61e,'c.lw','s1, 0xc(a0)'),
 (0xa008bdbc,'lbu','a5, 0x14(a0)'),(0xa008bdc0,'c.andi','a5, -2'),
 (0xa008bdc2,'sb','a5, 0x14(a0)'),(0xa008c31c,'c.mv','s1, a0'),
 (0xa008c322,'c.sw','a0, 4(s1)')]: check(a,m,o)

def sx(n,b): return n-(1<<b) if n&(1<<(b-1)) else n
def direct(a,target):
    w=int.from_bytes(rom[a-BASE:a-BASE+4],'little')
    assert w&127==0x6f and w>>7&31==1
    delta=((w>>31)<<20)|((w>>12&255)<<12)|((w>>20&1)<<11)|((w>>21&1023)<<1)
    assert (a+sx(delta,21))&0xffffffff==target
    checks.append(dict(address=hex(a),jal_target=hex(target),raw=rom[a-BASE:a-BASE+4].hex(),passed=True))
for a,t in [(0xa00adc20,0xa00dcee4),(0xa00adc46,0xa00a769a),(0xa00adc7c,0xa008bd70),
 (0xa00adc84,0xa008c2d0),(0xa005da5a,0xa008bc64),(0xa005da62,0xa008bd16),
 (0xa008bdc6,0xa0087b06),(0xa008c31e,0xa008b17e),(0xa008c324,0xa0087b06)]:direct(a,t)
for a,t,f,r1,r2 in [(0xa00adb02,0xa00adb3e,1,22,0),(0xa00adb3e,0xa00adb54,1,18,0),
 (0xa00adc3a,0xa00adcd0,0,14,15),(0xa00adc3e,0xa00ae196,1,15,0),
 (0xa00adc42,0xa00adcc4,0,14,0),(0xa00ae19a,0xa00adcc4,1,15,0),
 (0xa00add24,0xa00ade8a,1,15,14),(0xa00add2c,0xa00ade8a,1,14,15),
 (0xa00add38,0xa00ae5ec,1,15,0)]:
    w=int.from_bytes(rom[a-BASE:a-BASE+4],'little')
    d=((w>>31)<<12)|((w>>7&1)<<11)|((w>>25&63)<<5)|((w>>8&15)<<1)
    assert (w&127,w>>12&7,w>>15&31,w>>20&31,a+sx(d,13))==(0x63,f,r1,r2,t)
    checks.append(dict(address=hex(a),branch_target=hex(t),passed=True))
# RVC conditional branches encode PC-relative targets; independent immediate extraction.
for a,t,fn,rs in [(0xa00adb5a,0xa00adba4,6,10),(0xa00adba8,0xa00adbbc,7,15),(0xa00adc7a,0xa00adca4,6,15),
                  (0xa008bd7a,0xa008bdbc,7,10),(0xa008c2da,0xa008c31c,7,10)]:
    h=int.from_bytes(rom[a-BASE:a-BASE+2],'little')
    d=((h>>12&1)<<8)|((h>>10&3)<<3)|((h>>5&3)<<6)|((h>>3&3)<<1)|((h>>2&1)<<5)
    assert (h&3,h>>13,8+(h>>7&7),a+sx(d,9))==(1,fn,rs,t)
    checks.append(dict(address=hex(a),compressed_branch_target=hex(t),passed=True))
result=dict(scope='P-18 online difference only; no execution',records=[dict(procedure=p,evidence_id=r['evidence_id'],profile=r['analysis_profile']) for p,r in records.items()],
            windows=[dict(start=hex(a),end_exclusive=hex(b)) for a,b in windows],bytes=sum(b-a for a,b in windows),
            instructions=evidence,checks=checks,summary=dict(instructions=len(evidence),checks=len(checks),passed=True))
(OUT/'audit.json').write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n',encoding='utf8')
print(json.dumps(result['summary']))
