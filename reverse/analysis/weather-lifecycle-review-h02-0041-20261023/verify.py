"""H02 independent offline ROM review. Does not import/run H01 verifier."""
import json
from pathlib import Path
import capstone

HERE = Path(__file__).resolve().parent
MAIN = Path('D:/Documents/PlatformIO/Projects/cuktech-ap01-firmware')
ROM = MAIN / 'roms/0041/ap01-1.0.2_0041.bin'
BASE = 0x9ffff000
rom = ROM.read_bytes()
md = capstone.Cs(capstone.CS_ARCH_RISCV, capstone.CS_MODE_RISCV32 | capstone.CS_MODE_RISCVC)
checks, decoded, vendors = [], {}, []

def sx(x, bits):
    return x - (1 << bits) if x & (1 << (bits-1)) else x

def word(at):
    return int.from_bytes(rom[at-BASE:at-BASE+4], 'little')

def require(label, actual, expected):
    assert actual == expected, (label, actual, expected)
    checks.append(dict(check=label, actual=actual))

# Decode from ROM independently, not from H01 disassembly or literal bytes.
spans = [(0xa00b821e,0xa00b82b2),(0xa00b8bb4,0xa00b8bfc),
         (0xa00b3a68,0xa00b3b26),(0xa00b3b26,0xa00b3be6),
         (0xa00b3c14,0xa00b3c26),(0xa00b564e,0xa00b59c4),
         (0xa00b5b58,0xa00b5cec),(0xa00eeae6,0xa00eeb3a)]
for lo, hi in spans:
    pc = lo
    while pc < hi:
        raw = rom[pc-BASE:hi-BASE]
        w = word(pc)
        if w & 127 == 11:
            fields = dict(op=w&127, funct3=(w>>12)&7, rd=(w>>7)&31,
                          rs1=(w>>15)&31, rs2=(w>>20)&31,
                          shift=(w>>25)&3, high=w>>27)
            kind = {(4,8):'lrw',(4,20):'lrhu',(4,4):'lrh',(5,8):'srw'}.get((fields['funct3'],fields['high']))
            if fields['funct3'] == 3 and w>>26 == 15 and (w>>20)&63 == 0:
                kind='extu15_0'
            if fields['funct3'] == 1 and w>>27 == 0:
                kind='addsl'
            assert kind is not None, hex(pc)
            size=4
            text=kind+' '+str(fields)
            vendors.append(dict(address=hex(pc), word=hex(w), kind=kind, fields=fields))
        else:
            ins=next(md.disasm(raw,pc,count=1),None)
            assert ins, hex(pc)
            size=ins.size
            text=ins.mnemonic+' '+ins.op_str
        decoded[pc]=dict(address=hex(pc),offset=pc-BASE,bytes=raw[:size].hex(),text=text.strip())
        pc += size
    require('complete-window-'+hex(lo), pc, hi)

def jal(at, expected):
    w=word(at)
    require('jal-op-'+hex(at),(w&127,(w>>7)&31),(111,1))
    off=((w>>31)<<20)|(((w>>12)&255)<<12)|(((w>>20)&1)<<11)|(((w>>21)&1023)<<1)
    require('jal-target-'+hex(at),at+sx(off,21),expected)

for at, dst in [(0xa00b8246,0xa008e362),(0xa00b827a,0xa008e362),
                (0xa00b8250,0xa00d7806),(0xa00b82a6,0xa00d7806),
                (0xa00b82ac,0xa008ab8a),(0xa00b8bc2,0xa00b3a68),
                (0xa00b8bf4,0xa01ad654),(0xa00b5cde,0xa00b5b58),
                (0xa00b5c82,0xa00b564e),(0xa00b5bb6,0xa00eeae6),
                (0xa00b5c54,0xa00eeae6),(0xa00b5740,0xa0190da4),
                (0xa00b574a,0xa00a6d34),(0xa00b577a,0xa008ce16),
                (0xa00b57ba,0xa008ce16),(0xa00b57d4,0xa008ce16),
                (0xa00b5882,0xa00a6afa),(0xa00b59a0,0xa00a6afa),
                (0xa00b3bca,0xa00b3abe),(0xa00b3bd0,0xa008ab8a)]:
    jal(at,dst)
for at in [0xa00b5b9a,0xa00b5be6,0xa00b5bf4,0xa00b5c02,0xa00b5c10,0xa00b5c1e,0xa00b5c2c]:
    jal(at,0xa000589c)

def mem(at,expected):
    w=word(at); op=w&127
    reg=(w>>7)&31 if op==3 else (w>>20)&31
    off=w>>20 if op==3 else ((w>>25)<<5)|((w>>7)&31)
    value=(op,(w>>12)&7,reg,(w>>15)&31,sx(off,12))
    require('memory-'+hex(at),value,expected)
    return value[-1]

for at, f3, rd, base, off in [
    (0xa00b56b8,1,12,12,12),(0xa00b56e6,1,13,18,10),(0xa00b56ea,1,12,18,8),
    (0xa00b56fc,1,12,18,6),(0xa00b570e,5,13,18,16),(0xa00b5712,5,12,18,14),
    (0xa00b5724,5,13,18,20),(0xa00b5728,5,12,18,18),(0xa00b5736,5,11,18,28),
    (0xa00b5772,5,19,18,24),(0xa00b57ae,5,12,18,22),(0xa00b57cc,5,19,18,26),
    (0xa00b588a,1,12,18,120),(0xa00b5898,1,12,18,134),
    (0xa00b5b96,2,23,15,4),(0xa00b3b44,2,18,9,16),(0xa00b3b4c,2,15,18,4)]:
    mem(at,(3,f3,rd,base,off))
clear=[]
for at in range(0xa00b3b56,0xa00b3bc6,4):
    w=word(at); off=sx(((w>>25)<<5)|((w>>7)&31),12)
    clear.append(mem(at,(35,2,0,15,off)))
require('clear-exact-word-set',sorted(clear),list(range(0,112,4)))
for at, expected in [(0xa00b8bde,(35,2,15,20,0)),(0xa00b8be2,(35,2,18,20,4)),
                     (0xa00b8be6,(35,2,20,9,16)),(0xa00b3bd4,(35,2,0,9,16)),
                     (0xa00b8bd8,(35,0,15,18,112))]:
    mem(at,expected)

# Build each callback address from actual LUI and signed ADDI operands.
for hi,lo in [(0xa00b8bb4,0xa00b8bbe),(0xa00b3b50,0xa00b3bc6)]:
    require('same-key-callback-'+hex(hi),(word(hi)&0xfffff000)+sx(word(lo)>>20,12),0xa00b5cd4)
require('delete-hook-address',(word(0xa00b8bca)&0xfffff000)+sx(word(0xa00b8bee)>>20,12),0xa00b3b26)
# Check compressed move/lw/jalr argument facts using raw fields.
def cmv(at,rd,rs):
    w=word(at)&65535
    require('cmv-'+hex(at),(w&0xf003,(w>>7)&31,(w>>2)&31),(0x8002,rd,rs))
for at,rd,rs in [(0xa00b8bb8,11,9),(0xa00b3b54,11,9),(0xa00b3bce,10,18),
                 (0xa00b3c1c,10,19),(0xa00b5c7c,12,20),(0xa00b5c7e,11,22),
                 (0xa00b5c80,10,23),(0xa00b57d2,11,19),(0xa00b58ee,12,19),
                 (0xa00b591a,12,19)]:
    cmv(at,rd,rs)
require('dispatch-jalr-register',(word(0xa00b3c1e)&65535),0x9782)
def cbzero(at):
    w=word(at)&65535
    off=((w>>12)&1)<<8|((w>>10)&3)<<3|((w>>5)&3)<<6|((w>>3)&3)<<1|((w>>2)&1)<<5
    return (w&0xe003,8+((w>>7)&7),at+sx(off,9))
require('callback-null-gate',cbzero(0xa00b5cd4),(0xc001,11,0xa00b5cea))
for at,kind,rd,rs1,rs2,shift in [
    (0xa00b5c72,'srw',15,21,18,1),(0xa00b5930,'lrw',21,15,19,2),
    (0xa00b596e,'lrhu',12,24,19,3),(0xa00b597e,'lrhu',12,25,19,3),
    (0xa00b598a,'lrw',12,23,12,2),(0xa00b5998,'lrw',11,27,19,2),
    (0xa00b59ac,'lrh',12,14,19,1),(0xa00b59be,'lrh',12,15,19,1)]:
    v=next(v for v in vendors if v['address']==hex(at)); f=v['fields']
    require('vendor-'+hex(at),(v['kind'],f['rd'],f['rs1'],f['rs2'],f['shift']),(kind,rd,rs1,rs2,shift))

# H01 rows are a comparison subject, never the disassembly source above.
h01=json.loads((HERE.parent/'weather-subscriber-lifecycle-h01-0041-20261023/instruction-evidence.json').read_text())
old={int(i['address'],16):i for w in h01['windows'] for i in w['instructions']}
require('all-H01-bytes-match-ROM',all(old[a]['bytes']==v['bytes'] for a,v in decoded.items()),True)

# Retain only decision windows. Full ranges were decoded above, not duplicated here.
focus=[(0xa00b8240,0xa00b8256),(0xa00b8276,0xa00b82b2),(0xa00b8bb4,0xa00b8bfc),
       (0xa00b3b26,0xa00b3b56),(0xa00b3bc2,0xa00b3bd8),(0xa00b3c14,0xa00b3c20),
       (0xa00b5736,0xa00b574e),(0xa00b57cc,0xa00b57e0),(0xa00b58c0,0xa00b58de),
       (0xa00b5c30,0xa00b5c86),(0xa00b5cd4,0xa00b5cec)]
profile=MAIN/'evidence/rea-0041-20261017/ghidra/Ghidra/Processors/RISCV/data/languages/ap01thead2.sinc'
lines=profile.read_text().splitlines()
model=[]
for name in ['th.lrw','th.lrhu','th.lrh','th.srw','th.extu rd,rs1,15,0','th.addsl']:
    candidates=[i for i,s in enumerate(lines) if s.startswith(':'+name+' ')]
    require('one-profile-rule-'+name,len(candidates),1)
    i=candidates[0]
    j=next(j for j in range(i+1,len(lines)) if lines[j]=='}')
    model.append(dict(line=i+1,text='\n'.join(lines[i:j+1])))
strings=[]
for at, expected in [(0xa0561db8,'lv_ui_wx1_dtl1_update_wx_data_cb'),
                     (0xa0562020,'j_ui_wx1_dtl1_update_wx_data'),
                     (0xa037b710,'lv_power_ui/lv_ui_wx1_dtl.c')]:
    start=at-BASE
    value=rom[start:rom.index(b'\0',start)].decode('ascii')
    require('source-string-'+hex(at),value,expected)
    strings.append(dict(address=hex(at),text=value))
result=dict(status='passed',rom=str(ROM),mapping_base=hex(BASE),decoder='capstone '+capstone.__version__,
    decoded_instruction_count=len(decoded),decoded_ranges=[[hex(a),hex(b)] for a,b in spans],
    checks=checks,clear_offsets_in_original_order=clear,vendor_fields=vendors,
    profile_source=str(profile),profile_rules=model,source_strings=strings,
    decision_instructions=[r for a,r in decoded.items() if any(lo<=a<hi for lo,hi in focus)],
    limits=['No firmware execution, replay, emulator, external service, or new REA target.',
            'No allocator, GUI recursion, final context owner, or slot occupancy certification.'])
(HERE/'review-evidence.json').write_text(json.dumps(result,ensure_ascii=False,indent=2),encoding='utf-8')
print(json.dumps({k:result[k] for k in ['status','decoded_instruction_count']}|dict(check_count=len(checks),vendor_count=len(vendors))))
