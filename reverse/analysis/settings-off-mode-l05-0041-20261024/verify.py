"""L05 sparse static fields. No target execution, model, replay or service calls."""
from pathlib import Path
import json

OUT = Path(__file__).resolve().parent
MAIN = Path('D:/Documents/PlatformIO/Projects/cuktech-ap01-firmware')
ROM = (MAIN/'roms/0041/ap01-1.0.2_0041.bin').read_bytes()
BASE = 0x9ffff000
records = []

def sx(v,n):
    return v-(1<<n) if v&(1<<(n-1)) else v

def word(pc):
    return int.from_bytes(ROM[pc-BASE:pc-BASE+4], 'little')

def keep(pc, n, meaning):
    records.append(dict(pc=hex(pc), raw=ROM[pc-BASE:pc-BASE+n].hex(), meaning=meaning))

def raw(pc,h,meaning):
    assert ROM[pc-BASE:pc-BASE+len(bytes.fromhex(h))].hex()==h, hex(pc)
    keep(pc,len(bytes.fromhex(h)),meaning)

def i(pc,op,f3,rd,rs1,imm,meaning):
    w=word(pc)
    assert (w&127,(w>>12)&7,(w>>7)&31,(w>>15)&31,sx(w>>20,12))==(op,f3,rd,rs1,imm),hex(pc)
    keep(pc,4,meaning)

def jal(pc,target):
    w=word(pc)
    im=((w>>31)<<20)|(((w>>12)&255)<<12)|(((w>>20)&1)<<11)|(((w>>21)&1023)<<1)
    assert (w&127,(w>>7)&31)==(0x6f,1)
    assert pc+sx(im,21)==target
    keep(pc,4,'JAL ra '+hex(target))

raw(0xa00fd1d0,'374afc62','inherited caller s4 high62fc4000')
i(0xa00fd1e8,0x13,0,20,20,0x2c,'caller s4=62fc402c')
raw(0xa00fe9f0,'0d45','caller a0=3')
i(0xa00fea06,3,4,10,20,3,'caller LBU a0,3(s4): unsigned byte62fc402f')
for pc,target in [(0xa00fe9f2,0xa00ab4a8),(0xa00fea0a,0xa00ab4a8),
    (0xa00fe9fe,0xa018f232),(0xa00fea16,0xa018f232),
    (0xa00ab4c6,0xa00a5bbe),(0xa00ab4ca,0xa00ab274)]:
    jal(pc,target)
for pc,flag in [(0xa00fe9f6,0),(0xa00fea0e,1)]:
    i(pc,3,2,15,8,-0x58,'overwrite a5 with local58')
    raw(pc+4,'8145' if flag==0 else '8545',f'a1={flag}')
    raw(pc+6,'8847','overwrite a0 with word(local58+8); prior result unused')
raw(0xa00ab4a8,'b797fc62','setter G high62fc9000')
i(0xa00ab4ac,0x13,0,15,15,0x98,'setter G=62fc9098')
i(0xa00ab4b0,3,4,14,15,3,'LBU old G+3=62fc909b')
w=word(0xa00ab4b4)
im=((w>>31)<<12)|(((w>>7)&1)<<11)|(((w>>25)&63)<<5)|(((w>>8)&15)<<1)
assert (w&127,(w>>12)&7,(w>>15)&31,(w>>20)&31)==(0x63,0,14,10)
assert 0xa00ab4b4+sx(im,13)==0xa00ab4d6
keep(0xa00ab4b4,4,'BEQ old unsigned byte,full a0 -> equal-return ab4d6')
raw(0xa00ab4b8,'411106c622c40008','difference-arm stack frame only')
w=word(0xa00ab4c0)
assert (w&127,(w>>12)&7,(w>>20)&31,(w>>15)&31,((w>>25)<<5)|((w>>7)&31))==(0x23,0,10,15,3)
keep(0xa00ab4c0,4,'SB incoming a0 low byte to G+3 before calls')
raw(0xa00ab4c4,'1145','notification reason a0=4')
raw(0xa00ab4ce,'b2402244410182808280','both exits restore/return without explicit success result')

source=json.loads((MAIN/'reverse/rehost/settings-0041-round2b.json').read_text(encoding='utf8'))['records'][10]
refs=source['normalized_result']['outgoing_references']
for pc in ['0xa00fe9f2','0xa00fea0a']:
    assert any(r.get('source_address')==pc and r.get('target_address')=='0xa00ab4a8' for r in refs)
parent=json.loads((MAIN/'reverse/rehost/system-complete-0041.json').read_text(encoding='utf8'))['cached_evidence']['settings_a00fd1ac']
assert 'a00ab4a8' in parent
constructor=json.loads((MAIN/'reverse/rehost/settings-0041-round2d.json').read_text(encoding='utf8'))['records'][3]
assert "DAT_ram_62fc909b != '\\x03'" in constructor['normalized_result']['pseudocode']
inventory=json.loads((MAIN/'reverse/analysis/whole-rom-coverage-0041-20261023-round1.json').read_text(encoding='utf8'))
f=next(f for f in inventory['functions'] if f['address']=='0xa00ab4a8')
assert f['extent']['body']['total_bytes']==48

result=dict(status='PASS',baseline='1dcbfe6',records=records,record_count=len(records),
    inherited=dict(caller='settings-0041-round2b.json#/records/10',caller_evidence=source['evidence_id'],
      parent='system-complete-0041.json#/cached_evidence/settings_a00fd1ac',
      constructor='settings-0041-round2d.json#/records/3',constructor_evidence=constructor['evidence_id'],
      extent_evidence=f['extent']['evidence_id'],
      services='L03/L04: a00a5bbe callback ABI/live G and a00ab274 writer interface'),
    differences_from_L03=dict(caller_constant='fe9f2 value3 display0',caller_byte='fea0a Gedit+3 display1',
      field='G+3 instead of G+2',reason='4 instead of 3'),
    limits=['No notification/writer internals revalidated','No persisted-success claim',
      'No target/SIM/build/replay/device/external service/model execution','a00a46e8 owned by M01; not inspected'])
(OUT/'evidence.json').write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n',encoding='utf8')
print(json.dumps(dict(status='PASS',records=len(records),direct_calls=6,branch_targets=1)))
