"""N01 bounded offline ROM decoding and contract checks; no target execution."""
import json
from pathlib import Path
from capstone import Cs, CS_ARCH_RISCV, CS_MODE_RISCV32, CS_MODE_RISCVC

ROOT = Path('D:/Documents/PlatformIO/Projects/cuktech-ap01-firmware')
HERE = Path(__file__).resolve().parent
BASE = 0x9ffff000
rom = (ROOT/'roms/0041/ap01-1.0.2_0041.bin').read_bytes()
assert len(rom) == 6769704
src = ROOT/'reverse/analysis/uart-response-0041-20261023.json'
response = json.loads(src.read_text(encoding='utf-8'))['functions'][0]
assert response['normalized_result']['procedure']['address'] == '0xa00a8582'
provider = {int(x.split(':')[0],16):x.split(': ',1)[1] for x in response['normalized_result']['assembly']}
md = Cs(CS_ARCH_RISCV, CS_MODE_RISCV32 | CS_MODE_RISCVC)
windows = [
    ('response_route_57',0xa00a85ac,0xa00a85c0,'retained-response'),
    ('response_route_5e_60',0xa00a873e,0xa00a874e,'retained-response'),
    ('mode_ack_60',0xa00a8794,0xa00a87d2,'retained-response'),
    ('mode_report_57',0xa00a983e,0xa00a98d0,'retained-response'),
    ('custom_report_5e',0xa00a99f0,0xa00a9a8a,'retained-response'),
    ('control16_ack_62',0xa00a9cbc,0xa00a9d06,'retained-response'),
    ('common_submit',0xa00a882c,0xa00a8836,'retained-response'),
    ('common_selector',0xa00a8aae,0xa00a8ab4,'retained-response'),
    ('query_custom',0xa00a4158,0xa00a417c,'new-body'),
    ('set_control16',0xa00a417c,0xa00a41ba,'new-body'),
    ('ack_copy',0xa01ad024,0xa01ad04a,'new-body'),
]
rows=[]; at={}; checked=[]
for name,a,b,kind in windows:
    pc=a; instructions=[]
    while pc<b:
        off=pc-BASE
        size=4 if int.from_bytes(rom[off:off+2],'little')&3==3 else 2
        raw=rom[off:off+size]
        ins=list(md.disasm(raw,pc))
        assert len(ins)==1 and ins[0].size==size,hex(pc)
        if kind=='retained-response':
            assert pc in provider
            blocks=[x for x in response['raw_ranges'] if int(x['start'],16)<=pc<=int(x['end'],16)]
            assert len(blocks)==1
            block=blocks[0]; ix=pc-int(block['start'],16)
            assert bytes.fromhex(block['hex'])[ix:ix+size]==raw
        row=dict(pc=hex(pc),file_offset=off,hex=raw.hex(),mnemonic=ins[0].mnemonic,
                 operands=ins[0].op_str,retained=provider.get(pc))
        rows.append(row);instructions.append(row);at[pc]=row;pc+=size
    assert pc==b
    checked.append(dict(name=name,start=hex(a),end_exclusive=hex(b),authority=kind,instructions=instructions))

checks=[]
def exact(pc,mnemonic,operands):
    r=at[pc];assert (r['mnemonic'],r['operands'])==(mnemonic,operands),(hex(pc),r)
    checks.append(dict(pc=hex(pc),kind='exact-decode',expect=[mnemonic,operands]))
def jal(pc,target):
    w=int.from_bytes(bytes.fromhex(at[pc]['hex']),'little');assert w&0x7f==0x6f
    imm=((w>>31)<<20)|(((w>>12)&255)<<12)|(((w>>20)&1)<<11)|(((w>>21)&1023)<<1)
    if imm&(1<<20):imm-=1<<21
    assert (pc+imm)&0xffffffff==target
    checks.append(dict(pc=hex(pc),kind='raw-JAL',target=hex(target)))
def pair(pc,target):
    w=int.from_bytes(bytes.fromhex(at[pc]['hex']),'little');v=int.from_bytes(bytes.fromhex(at[pc+4]['hex']),'little')
    assert w&127==0x17 and v&127==0x67 and (w>>7)&31==(v>>15)&31
    hi=w&0xfffff000;hi=hi-(1<<32) if hi&(1<<31) else hi
    lo=v>>20;lo=lo-4096 if lo&2048 else lo
    assert ((pc+hi+lo)&0xffffffff)&~1==target
    checks.append(dict(pc=hex(pc),kind='raw-AUIPC/JALR',target=hex(target)))
def branch(pc,target):
    raw=bytes.fromhex(at[pc]['hex']);w=int.from_bytes(raw,'little')
    if len(raw)==4:
        assert w&127==0x63
        imm=((w>>31)<<12)|(((w>>7)&1)<<11)|(((w>>25)&63)<<5)|(((w>>8)&15)<<1)
        if imm&4096:imm-=8192
    else:
        assert w&3==1 and (w>>13)&7 in (6,7)
        imm=(((w>>12)&1)<<8)|(((w>>5)&3)<<6)|(((w>>2)&1)<<5)|(((w>>10)&3)<<3)|(((w>>3)&3)<<1)
        if imm&256:imm-=512
    assert (pc+imm)&0xffffffff==target,(hex(pc),hex(pc+imm),hex(target))
    checks.append(dict(pc=hex(pc),kind='raw-conditional-branch',target=hex(target)))

for pc,m,o in [
    (0xa00a87b0,'c.li','a1, 1'),(0xa00a87b2,'addi','a0, a0, 0x50d'),
    (0xa00a87c2,'lbu','a4, 0x1d(a5)'),(0xa00a984a,'c.li','a1, 6'),
    (0xa00a984c,'addi','a0, a0, 0x510'),(0xa00a9858,'addi','a5, a5, 0x51d'),
    (0xa00a9862,'lbu','a3, 2(s1)'),(0xa00a986c,'sb','a3, 0x1d(a4)'),
    (0xa00a9870,'c.li','a0, 0xa'),(0xa00a9874,'sb','a4, 0(a5)'),
    (0xa00a9892,'lbu','a0, 0x1d(a5)'),(0xa00a9896,'lbu','a5, 2(s1)'),
    (0xa00a98a8,'addi','a0, a0, 0x518'),(0xa00a98bc,'lhu','a0, 0x51e(a5)'),
    (0xa00a98c0,'lhu','a5, 0(s1)'),(0xa00a98c8,'c.li','a1, 1'),
    (0xa00a99f8,'c.li','a1, 3'),(0xa00a9a1e,'sb','a3, 9(a4)'),
    (0xa00a9a34,'sb','a3, 0xa(a4)'),(0xa00a9a4e,'sb','a3, 0xb(a4)'),
    (0xa00a9a54,'sh','a5, 0xc(a4)'),(0xa00a4160,'addi','a5, zero, 0x5e'),
    (0xa00a4168,'sh','a5, -0x18(s0)'),(0xa00a416c,'sw','zero, -0x14(s0)'),
    (0xa00a4180,'lhu','a4, 0x51e(a5)'),(0xa00a4198,'sh','a0, 0(a5)'),
    (0xa00a419c,'addi','a4, zero, 0x262'),(0xa00a41a8,'sw','a5, -0x14(s0)'),
    (0xa01ad02c,'c.mv','a5, a2'),(0xa01ad032,'c.mv','a2, a1'),
    (0xa01ad034,'c.mv','a1, a5'),(0xa01ad036,'sb','zero, 0x2f0(a4)'),
    (0xa00a9cf2,'sh','a4, 0(a5)'),(0xa00a9cf6,'addi','a4, zero, 0x261'),
]: exact(pc,m,o)
for pc,target in [(0xa00a4170,0xa01951e2),(0xa00a41ac,0xa01951e2),
 (0xa00a87cc,0xa00a4158),(0xa00a9850,0xa0191652),(0xa00a9878,0xa00a417c),
 (0xa00a987c,0xa00a4158),(0xa00a9880,0xa0195166),(0xa00a98ac,0xa019530a),
 (0xa00a98b2,0xa019537a),(0xa00a98ca,0xa00a417c),(0xa00a99fe,0xa0191652),
 (0xa00a9a7a,0xa00a536c),(0xa00a8830,0xa01951e2),(0xa00a8aae,0xa0191746)]:jal(pc,target)
for pc,target in [(0xa00a87b6,0xa01ad024),(0xa00a9cc6,0xa01ad024),(0xa01ad03a,0xa000589c)]:pair(pc,target)
for pc,target in [(0xa00a85b0,0xa00a85b8),(0xa00a87a8,0xa00a85e4),
 (0xa00a87c8,0xa00a85e4),(0xa00a9860,0xa00a9888),(0xa00a988a,0xa00a9880),
 (0xa00a989a,0xa00a98b8),(0xa00a98a0,0xa00a98b2),(0xa00a98c4,0xa00a9880),
 (0xa00a4188,0xa00a4190),(0xa00a418c,0xa00a41b8),(0xa00a9a1a,0xa00a9a24),
 (0xa00a9a30,0xa00a9a3a),(0xa00a9a4a,0xa00a9a82),(0xa00a9a82,0xa00a9a88),
 (0xa00a9cd2,0xa00a9cda),(0xa00a9cea,0xa00a9cf2)]:branch(pc,target)

result=dict(status='static_checks_passed',identity_reference='roms/CATALOG.md;0041',base=hex(BASE),
    response_source=str(src),response_evidence_id=response['evidence_id'],profile=response['profile_digest'],
    method='Independent ROM instruction lengths/Capstone; retained response bytes matched only in selected windows; raw call targets checked. No target execution.',
    instruction_count=len(rows),checks=checks,windows=checked,
    new_body_bytes=sum(b-a for _,a,b,k in windows if k=='new-body'),
    limitations=['Selected normal interface windows, not full dispatcher','No hardware/MCU execution','Ordinary helper names are analysis names'])
(HERE/'instruction-evidence.json').write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
print(json.dumps({k:result[k] for k in ['status','instruction_count','new_body_bytes']}))
print('contract_checks='+str(len(checks)))
