"""P-14 bounded static evidence; no target/model execution or shared REA mutation."""
import json
from pathlib import Path
from capstone import Cs, CS_ARCH_RISCV, CS_MODE_RISCV32, CS_MODE_RISCVC

ROOT = Path('D:/Documents/PlatformIO/Projects/cuktech-ap01-firmware')
OUT = Path(__file__).resolve().parent
BASE = 0x9ffff000
rom = (ROOT/'roms/0041/ap01-1.0.2_0041.bin').read_bytes()
bundle = json.loads((ROOT/'evidence/rea-0041-20261017/evidence/whole-rom-private-20261023.evidence.json').read_text(encoding='utf-8'))
e = next(x for x in bundle['records'] if x['evidence_id']=='ev_6044e70f4a6f785a665e891cedb82fc897de52716642b9e9bbe0538f9b9d4c40')
old = json.loads((ROOT/'reverse/rehost/charge-complete-0041.json').read_text(encoding='utf-8'))
assert old['source_sha256']=='972db4c136c7ed9e24a83c07c1a7fd62040ca018b08ca285216d26b1fee3c6b9'
assert e['analysis_profile']['digest']=='b6368dd18431e8113aa5026c713d41e648ab0f6ddd9421ff6c4a49e23b3cd2f3'
md = Cs(CS_ARCH_RISCV, CS_MODE_RISCV32|CS_MODE_RISCVC)
spans = [
 ('switch_actions',0xa00f7c98,0xa00f7d36),
 ('safe_select_on',0xa00f7d8a,0xa00f7dec),
 ('safe_select_off',0xa00f7fca,0xa00f8016),
 ('switch_setter',0xa0191834,0xa0191872),
 ('feedback_masks',0xa00f5970,0xa00f5a04),
 ('safe_feedback',0xa00f5b0a,0xa00f5b6c),
 ('switch_feedback',0xa00f5b6c,0xa00f5b86),
]
windows=[]
for name,a,b in spans:
    lines=[]; pc=a
    while pc<b:
        raw=rom[pc-BASE:pc-BASE+4]
        size=4 if raw[0]&3==3 else 2
        assert pc+size<=b
        raw=raw[:size]; ins=next(md.disasm(raw,pc),None)
        lines.append({'address':hex(pc),'hex':raw.hex(),'assembly':ins.mnemonic+' '+ins.op_str if ins else 'unknown-preserved'})
        pc+=size
    retained=[]
    sources=e['normalized_result']['assembly'] if a>=0xa00f7c98 and b<=0xa00f8016 else old['records'][19]['assembly']
    if name!='switch_setter':
        retained=[x for x in sources if a<=int(x.split(':')[0],16)<b]
        assert len(retained)==len(lines)
        assert [int(x.split(':')[0],16) for x in retained]==[int(x['address'],16) for x in lines]
    windows.append({'name':name,'start':hex(a),'end_exclusive':hex(b),'hex':rom[a-BASE:b-BASE].hex(),'instructions':lines,'retained_assembly':retained})

def word(a): return int.from_bytes(rom[a-BASE:a-BASE+4],'little')
def jal(a):
    w=word(a); assert w&127==0x6f
    n=((w>>31)<<20)|(((w>>12)&255)<<12)|(((w>>20)&1)<<11)|(((w>>21)&1023)<<1)
    return (a+(n-(1<<21) if n&(1<<20) else n))&0xffffffff
calls={0xa00f7cd2:0xa0191834,0xa00f7d0c:0xa0191834,0xa00f7dd6:0xa01917d0,0xa00f8000:0xa01917d0,0xa0191864:0xa01951e2,0xa00f5b7e:0xa00f40ee}
for a,b in calls.items(): assert jal(a)==b
assert word(0xa0191848)==0x26500793 # addi a5,zero,0x265 -> cmd65 len2 LE
assert word(0xa019184c)==0xfea40223 # sb a0,-0x1c(s0)
assert word(0xa019185c)==0xfeb402a3 # sb a1,-0x1b(s0)
result={'status':'PASS','source_rom_identity_inherited':old['source_sha256'],'mapping':'offset=VA-0x9ffff000',
 'handler_source':{'path':'evidence/rea-0041-20261017/evidence/whole-rom-private-20261023.evidence.json','evidence_id':e['evidence_id'],'profile':e['analysis_profile']},
 'historical_feedback':{'path':'reverse/rehost/charge-complete-0041.json#/records/19','evidence_id':old['records'][19]['evidence_id'],'analysis_profile':'not supplied in historical record; do not assign newer profile'},
 'windows':windows,'checks':{'window_count':len(windows),'bytes':sum(b-a for _,a,b in spans),'instruction_boundaries':True,'retained_address_alignment':True,'direct_jal_targets':{hex(k):hex(v) for k,v in calls.items()},'cmd65_len2_and_stack_bytes':True},
 'limits':['No full handler export','No independent static execution','No device success or request-to-response correlation','Capstone standard RV32+C; historical Ghidra profile recorded separately']}
(OUT/'static-evidence.json').write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
print(json.dumps(result['checks']))
