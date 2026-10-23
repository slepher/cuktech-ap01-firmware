"""F09: bounded static old-conclusion verification, never executes firmware."""
import json
import re
import zipfile
from pathlib import Path
from capstone import Cs, CS_ARCH_RISCV, CS_MODE_RISCV32, CS_MODE_RISCVC

ROOT = Path('D:/Documents/PlatformIO/Projects/cuktech-ap01-firmware')
OUT = Path(__file__).resolve().parent
BASE = 0x9ffff000
rom = (ROOT/'roms/0041/ap01-1.0.2_0041.bin').read_bytes()
md = Cs(CS_ARCH_RISCV, CS_MODE_RISCV32 | CS_MODE_RISCVC)
# Only normal allocation gate, transfer/return, successful publication and caller.
# Logging/assertion blocks are inherited opaque boundaries, not re-exported.
spans = [(0xa00ecc76,0xa00ecc7e),(0xa00ecca0,0xa00eccc2),
         (0xa00ecd02,0xa00ecd14),(0xa01b9510,0xa01b951c)]
rows = {}
for start,end in spans:
    p=start
    while p<end:
        n=4 if rom[p-BASE]&3==3 else 2
        raw=rom[p-BASE:p-BASE+n]
        ins=next(md.disasm(raw,p),None)
        assert ins and p+n<=end
        rows[p]={'pc':hex(p),'raw':raw.hex(),'asm':ins.mnemonic+' '+ins.op_str}
        p+=n
checks=[]
def expect(pc,asm):
    assert rows[pc]['asm']==asm,(hex(pc),rows[pc],asm)
    checks.append({'pc':hex(pc),'expected':asm})
for pc,asm in {
    0xa00ecc76:'lbu s3, 0x10(a0)',0xa00ecc7a:'bnez s3, 0x36',
    0xa00ecca8:'c.mv a0, s3',0xa00eccb0:'c.mv s2, a1',
    0xa00eccb2:'c.lw a1, 0xc(a0)',0xa00eccb4:'c.mv s1, a0',
    0xa00eccb6:'c.lw a0, 0(a0)',0xa00eccb8:'mul a1, s2, a1',
    0xa00eccc0:'c.bnez a0, 0x42',0xa00ecd02:'c.lw a5, 4(s1)',
    0xa00ecd04:'c.sw a0, 0(s1)',0xa00ecd06:'sw s2, 8(s1)',
    0xa00ecd0a:'bgeu s2, a5, -0x6a',0xa00ecd0e:'sw s2, 4(s1)',
    0xa01b9510:'c.addi a1, 4',0xa01b9512:'c.mv a0, s1',
    0xa01b9518:'c.bnez a0, -0x30',0xa01b951a:'c.j -0x16',
}.items():expect(pc,asm)
def jal(pc,target):
    w=int.from_bytes(rom[pc-BASE:pc-BASE+4],'little')
    assert w&127==0x6f
    v=((w>>31)<<20)|(((w>>12)&255)<<12)|(((w>>20)&1)<<11)|(((w>>21)&1023)<<1)
    if v&(1<<20):v-=1<<21
    assert pc+v==target
    checks.append({'pc':hex(pc),'target':hex(target),'method':'raw JAL immediate'})
jal(0xa00eccbc,0xa008c332)
jal(0xa01b9514,0xa00ecc68)

needles=['a01b93b4','a008acfa','a00ecc68','a008ac38','a008acc6']
paths=[ROOT/'reverse/reports/ap01'/n for n in [
    'application-rehost-complete-0041-20261017.md',
    'application-function-matrix-0041.json','factory-reference-map-0041-20261020.md']]
for pattern in ['*-complete-0041.json','page-logic*.json','details-0041-round4.json',
                'charge-0041-round4.json','main-knob-0041-round2.json',
                'detail-knob-0041-round2.json','settings-0041-round2*.json']:
    paths+=list((ROOT/'reverse/rehost').glob(pattern))
paths+=[ROOT/'reverse/analysis/0041-20261013/0041-ghidra-pass3.txt']
hits=[]
for path in dict.fromkeys(paths):
    if path.exists():
        text=path.read_text(encoding='utf-8',errors='replace').lower()
        hits.append({'path':str(path.relative_to(ROOT)),
                     'exact_hits':{s:len(re.findall(s,text)) for s in needles if s in text}})
zip_hits=[]
with zipfile.ZipFile(ROOT/'reverse/rehost/ap01-ui-0041-complete-source.zip') as z:
    for info in z.infolist():
        if info.filename.endswith(('.c','.h','.py','.md','.txt','.sh','.json')):
            text=z.read(info).decode('utf-8',errors='replace').lower()
            found=[s for s in needles if s in text]
            if found:zip_hits.append({'member':info.filename,'needles':found})
result={'classification':'old bytes verification; incremental helper ABI contract only',
        'windows':[{'start':hex(a),'end_exclusive':hex(z)} for a,z in spans],
        'instructions':list(rows.values()),'checks':checks,
        'old_priority_exact_address_search':hits,'zip_exact_address_hits':zip_hits,
        'limits':'Exact address misses are bounded; G03-G06 address/field contracts override F06 earlier unknowns.'}
(OUT/'evidence.json').write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
print(json.dumps({'windows':len(spans),'instructions':len(rows),'checks':len(checks),
                  'priority_files':len(hits),'zip_hits':len(zip_hits)}))
