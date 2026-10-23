"""H12 independent, bounded ROM review; no firmware execution or prior verifier import."""
from pathlib import Path
import json
import re
import capstone

HERE = Path(__file__).resolve().parent
ROM_PATH = Path('D:/Documents/PlatformIO/Projects/cuktech-ap01-firmware/roms/0041/ap01-1.0.2_0041.bin')
ROM = ROM_PATH.read_bytes()
BASE = 0x9ffff000
cs = capstone.Cs(capstone.CS_ARCH_RISCV, capstone.CS_MODE_RISCV32 | capstone.CS_MODE_RISCVC)
checks = []

def expect(label, value, wanted):
    assert value == wanted, (label, value, wanted)
    checks.append({'claim': label, 'value': value})

def scan(lo, end):
    result = []
    while lo < end:
        data = ROM[lo-BASE:lo-BASE+4]
        word = int.from_bytes(data, 'little')
        n = 4 if word & 3 == 3 else 2
        if n == 4 and word & 127 == 11:
            asm = 'vendor rd=%d rs1=%d rs2=%d' % tuple((word >> k) & 31 for k in (7, 15, 20))
        else:
            ins = next(cs.disasm(data[:n], lo, 1))
            assert ins.size == n
            asm = ins.mnemonic + ' ' + ins.op_str
        result.append({'va': hex(lo), 'raw': data[:n].hex(), 'asm': asm})
        lo += n
    assert lo == end
    return result

live = scan(0xa00b8818, 0xa00b8996) + scan(0xa00b8a54, 0xa00b8b82)
consumer = scan(0xa00b56b2, 0xa00b5874)
by_va = {int(x['va'],16): x for x in live + consumer}
refs = [x for x in live if re.search(r'\bs3\b', x['asm'])]
expect('all ordinary cursor references in two live code intervals',
       [x['va'] for x in refs], [hex(a) for a in
        (0xa00b8818,0xa00b893a,0xa00b8994,0xa00b8a82,0xa00b8abc,
         0xa00b8af6,0xa00b8b10,0xa00b8b44,0xa00b8b72)])
vendor = [x for x in live if x['asm'].startswith('vendor')]
expect('only custom word in live ranges', [(x['va'],x['raw'],x['asm']) for x in vendor],
       [('0xa00b8a76','8ba7073c','vendor rd=15 rs1=15 rs2=0')])

def word(va):
    return int.from_bytes(ROM[va-BASE:va-BASE+4], 'little')

def sext(x,n):
    return x-(1<<n) if x & (1<<(n-1)) else x

def itype(va, wanted):
    w=word(va)
    expect(hex(va)+' I fields opcode/rd/f3/rs1/imm',
           (w&127,(w>>7)&31,(w>>12)&7,(w>>15)&31,sext(w>>20,12)), wanted)

itype(0xa00b8818,(19,19,0,18,84))
itype(0xa00b5850,(3,21,2,9,84))
for va,rd in [(0xa00b8abc,14),(0xa00b8af6,11),(0xa00b8b10,14),
              (0xa00b8b44,14),(0xa00b8b72,11)]:
    itype(va,(3,rd,2,19,0))
for va,rs1,imm in [(0xa00b8860,18,84),(0xa00b8a82,19,0)]:
    w=word(va)
    expect(hex(va)+' S fields opcode/f3/rs1/rs2/imm',
           (w&127,(w>>12)&7,(w>>15)&31,(w>>20)&31,
            sext(((w>>25)<<5)|((w>>7)&31),12)),(35,2,rs1,10,imm))

for va,asm in [(0xa00b8820,'c.li s8, 0'),(0xa00b8936,'c.addi s8, 1'),
               (0xa00b8938,'c.li a5, 7'),(0xa00b893a,'c.addi s3, 4'),
               (0xa00b8994,'c.mv s3, a0'),(0xa00b56b2,'c.mv s1, a0')]:
    expect(hex(va)+' decoded scalar operation',by_va[va]['asm'],asm)

def jal(va,target):
    w=word(va)
    displacement=sext(((w>>31)<<20)|(((w>>12)&255)<<12)|(((w>>20)&1)<<11)|(((w>>21)&1023)<<1),21)
    expect(hex(va)+' JAL opcode/link/target',(w&127,(w>>7)&31,hex(va+displacement)),(111,1,hex(target)))

for va in (0xa00b8858,0xa00b8a7e): jal(va,0xa00a643a)
jal(0xa00b8990,0xa00d76ae)
for va in (0xa00b5858,0xa00b5864,0xa00b5870): jal(va,0xa00dcee4)
for va in (0xa00b8854,0xa00b8a6a): expect(hex(va)+' creator second arg',by_va[va]['asm'],'c.mv a1, s1')
for va in (0xa00b8856,0xa00b8a6c): expect(hex(va)+' creator first arg',by_va[va]['asm'],'c.mv a0, s1')
for va,index in ((0xa00b5854,1),(0xa00b5860,2),(0xa00b586c,3)):
    expect(hex(va)+' child index',by_va[va]['asm'],f'c.li a1, {index}')
    expect(hex(va+2)+' parent value',by_va[va+2]['asm'],'c.mv a0, s5')

# Independently decode branch immediates; the nonzero block rejoins the shared tail.
for va,rs1,rs2,target in ((0xa00b883a,24,0,0xa00b8a54),(0xa00b893c,24,15,0xa00b883a)):
    w=word(va)
    off=sext(((w>>31)<<12)|(((w>>7)&1)<<11)|(((w>>25)&63)<<5)|(((w>>8)&15)<<1),13)
    expect(hex(va)+' BNE fields/target',(w&127,(w>>12)&7,(w>>15)&31,(w>>20)&31,hex(va+off)),(99,1,rs1,rs2,hex(target)))
expect('nonzero row jump displacement',by_va[0xa00b8b80]['asm'],'c.j -0x258')
expect('nonzero rejoin address',hex(0xa00b8b80-0x258),'0xa00b8928')

# Verify context register remains unchanged through the row0 consumer connection.
s1refs=[x for x in consumer if re.search(r'\bs1\b',x['asm'])]
expect('consumer interval has no unhandled vendor words',
       [x['va'] for x in consumer if x['asm'].startswith('vendor')], [])
expect('s1 destination writes in consumer interval',
       [x['va'] for x in s1refs if re.match(r'[^ ]+ s1(?:,|$)',x['asm'])], ['0xa00b56b2'])
bar=scan(0xa00b8b82,0xa00b8b88)
expect('later s3 object byte access',bar[0]['asm'],'lbu a5, 0x70(s3)')

# Retain only decisive sparse windows, not another complete constructor export.
keep=set(int(x['va'],16) for x in refs)
for lo,end in [(0xa00b883a,0xa00b8864),(0xa00b8928,0xa00b8940),
               (0xa00b8986,0xa00b8996),(0xa00b8a54,0xa00b8a86),
               (0xa00b8abc,0xa00b8ae6),(0xa00b8af6,0xa00b8b10),
               (0xa00b8b68,0xa00b8b82),(0xa00b5826,0xa00b5838),
               (0xa00b5850,0xa00b5874)]:
    keep.update(a for a in by_va if lo<=a<end)
out={'status':'PASS','new_functionality':0,'method':'independent local read-only Capstone and raw RV32 fields; no REA shared target',
     'checked_instruction_count':len(live)+len(consumer)+len(bar),'checks':checks,
     'cursor_refs':refs,'consumer_s1_refs':s1refs,'later_bar_access':bar[0],
     'sparse_instructions':[by_va[a] for a in sorted(keep)],
     'limits':'Only H11 cursor chain and row0 ABI. No global alias/free absence claim; context116 final free unknown.'}
(HERE/'review-evidence.json').write_text(json.dumps(out,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
print(json.dumps({'status':out['status'],'checked_instructions':out['checked_instruction_count'],'checks':len(checks),'sparse_retained':len(keep)}))
