"""P-R11: independent offline field checks; no target/model/author code execution."""
import json
from pathlib import Path

ROOT = Path('D:/Documents/PlatformIO/Projects/cuktech-ap01-firmware')
OUT = Path(__file__).resolve().parent
SOURCE = ROOT / 'evidence/rea-0041-20261017/evidence/whole-rom-private-20261023.evidence.json'
record = next(r for r in json.loads(SOURCE.read_text(encoding='utf-8'))['records']
              if r.get('parameters', {}).get('procedure') == '0xa00ad602')
profile = record['analysis_profile']
assert profile['parameters']['language_id'] == 'RISCV:LE:32:ap01thead2'
assert profile['digest'] == 'b6368dd18431e8113aa5026c713d41e648ab0f6ddd9421ff6c4a49e23b3cd2f3'
assert 'unreachable' not in json.dumps(record['raw_result']).lower()
assert 'unreachable' not in str(record['normalized_result']['pseudocode']).lower()
rom = (ROOT / 'roms/0041/ap01-1.0.2_0041.bin').read_bytes()
assert len(rom) == 6769704
asm = dict((int(s.split(': ', 1)[0], 16), s.split(': ', 1)[1])
           for s in record['normalized_result']['assembly'])
windows = [(0xad61e,0xad620),(0xad648,0xad6a4),(0xad6de,0xad6f6),
           (0xad72e,0xad74a),(0xad784,0xad798),(0xad7b4,0xad7c6),
           (0xad7fe,0xad81a),(0xad854,0xad86c),(0xad8a4,0xad8bc),
           (0xad8f6,0xad912),(0xad94e,0xad96c),(0xad998,0xad9fc),
           (0xada28,0xada82),(0xadaae,0xadabc)]
regs = ['zero','ra','sp','gp','tp','t0','t1','t2','s0','s1','a0','a1',
        'a2','a3','a4','a5','a6','a7','s2','s3','s4','s5','s6','s7',
        's8','s9','s10','s11','t3','t4','t5','t6']
checks = []
rows = []
def sx(v, n):
    return v - (1 << n) if v & (1 << (n-1)) else v
def note(addr, kind, actual, expected):
    assert actual == expected, (hex(addr), kind, actual, expected)
    checks.append({'address':hex(addr),'kind':kind,'value':actual})
def cj(w):
    return sx(((w>>12&1)<<11)|((w>>11&1)<<4)|((w>>9&3)<<8)|
              ((w>>8&1)<<10)|((w>>7&1)<<6)|((w>>6&1)<<7)|
              ((w>>3&7)<<1)|((w>>2&1)<<5),12)
for lo, hi in windows:
    a = 0xa0000000 + lo
    end = 0xa0000000 + hi
    while a < end:
        off = a - 0x9ffff000
        h = int.from_bytes(rom[off:off+2], 'little')
        size = 4 if h & 3 == 3 else 2
        b = rom[off:off+size]
        w = int.from_bytes(b, 'little')
        text = asm[a]
        parts = text.replace(',', '').split()
        op, args = parts[0], parts[1:]
        decoded = None
        if size == 4:
            rd, r1, r2 = (w>>7)&31, (w>>15)&31, (w>>20)&31
            opcode, f3 = w&127, (w>>12)&7
            if opcode == 0x03:
                decoded = [regs[rd], sx(w>>20,12), regs[r1]]
                note(a,'load',decoded,[args[0],int(args[1],0),args[2]])
                note(a,'load-width',f3,{'lw':2,'lbu':4}[op])
            elif opcode == 0x23:
                imm = sx(((w>>25)<<5)|((w>>7)&31),12)
                decoded = [regs[r2],imm,regs[r1]]
                note(a,'store',decoded,[args[0],int(args[1],0),args[2]])
                note(a,'store-width',f3,{'sb':0,'sh':1}[op])
            elif opcode == 0x13:
                decoded = [regs[rd],regs[r1],sx(w>>20,12)]
                note(a,'immediate',decoded,[args[0],args[1],int(args[2],0)])
                note(a,'immediate-op',f3,{'addi':0,'andi':7}[op])
            elif opcode == 0x63:
                delta = sx(((w>>31)<<12)|((w>>7&1)<<11)|
                           ((w>>25&63)<<5)|((w>>8&15)<<1),13)
                decoded = [regs[r1],regs[r2],a+delta]
                note(a,'branch',decoded,[args[0],args[1],int(args[2],0)])
                note(a,'branch-condition',f3,{'beq':0,'bne':1,'bltu':6}[op])
            elif opcode == 0x6f:
                delta = sx(((w>>31)<<20)|((w>>12&255)<<12)|
                           ((w>>20&1)<<11)|((w>>21&1023)<<1),21)
                note(a,'JAL',[regs[rd],a+delta],[args[0],int(args[1],0)])
            elif opcode == 0x0b:
                note(a,'private-word',b.hex(),'0b482d81')
                note(a,'private-register-fields',[rd,r1,r2],[16,26,18])
                note(a,'private-op-fields',[opcode,f3,w>>27],[11,4,16])
                note(a,'private-shift',w>>25&3,0)
        else:
            rd = w>>7&31
            if op == 'c.li':
                note(a,'C.LI', [regs[rd],sx(((w>>12&1)<<5)|(w>>2&31),6)],
                     [args[0],int(args[1],0)])
                note(a,'C.LI-op', [w&3,w>>13], [1,2])
            elif op == 'c.j':
                note(a,'C.J',a+cj(w),int(args[0],0))
                note(a,'C.J-op',[w&3,w>>13],[1,5])
            elif op == 'c.mv':
                note(a,'C.MV',[regs[rd],regs[w>>2&31]],[args[0],args[1]])
            elif op == 'c.lw':
                imm = ((w>>10&7)<<3)|((w>>6&1)<<2)|((w>>5&1)<<6)
                note(a,'C.LW',[regs[8+(w>>2&7)],imm,regs[8+(w>>7&7)]],
                     [args[0],int(args[1],0),args[2]])
        rows.append({'address':hex(a),'bytes':b.hex(),'retained':text})
        a += size
    assert a == end
note(0xa01c3bd4,'labels',rom[0xa01c3bd4-0x9ffff000:0xa01c3bdc-0x9ffff000].hex(),
     '4332000043310000')
model_path = ROOT / 'evidence/rea-0041-20261017/ghidra/Ghidra/Processors/RISCV/data/languages/ap01thead2.sinc'
model = model_path.read_text(encoding='utf-8')
section = model.split(':th.lrbu rd,rs1,rs2,thshift is',1)[1].split('\n}',1)[0]
assert 'rs2 << thshift' in section and 'rd = zext(value)' in section
assert 'thbase =' not in section
reg_path = model_path.with_name('ap01thead2.reg.sinc')
assert 'thshift=(25,26)' in reg_path.read_text(encoding='utf-8')
off = 0xa00ad642 - 0x9ffff000
h = int.from_bytes(rom[off:off+2], 'little')
note(0xa00ad642,'C.LUI-base',[h&3,h>>13,h>>7&31,
     sx(((h>>12&1)<<5)|(h>>2&31),6)<<12],[1,3,20,4096])
note(0xa00ad94e,'dual-halfword-value',4096-0x6f7,0x0909)
result = {'status':'PASS','source':str(SOURCE),'evidence_id':record['evidence_id'],
          'profile':profile,'window_count':len(windows),'bytes':sum(b-a for a,b in windows),
          'instruction_count':len(rows),'check_count':len(checks),'checks':checks,
          'instructions':rows,'private_model_source':str(model_path),
          'private_model_constructor':section,'private_register_source':str(reg_path),
          'limits':'Field checks only; manual register-flow review is separate. No execution or full decoder.'}
(OUT / 'audit.json').write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
print(json.dumps({k:result[k] for k in ('status','window_count','bytes','instruction_count','check_count')}))
