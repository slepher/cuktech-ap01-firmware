"""P-01: bounded original-byte checks; no target, simulator or model execution."""
from pathlib import Path
import json
from capstone import Cs, CS_ARCH_RISCV, CS_MODE_RISCV32, CS_MODE_RISCVC

ROOT = Path('D:/Documents/PlatformIO/Projects/cuktech-ap01-firmware')
OUT = Path(__file__).resolve().parent
BASE = 0x9ffff000
rom = (ROOT/'roms/0041/ap01-1.0.2_0041.bin').read_bytes()
assert len(rom) == 6769704
decoder = Cs(CS_ARCH_RISCV, CS_MODE_RISCV32 | CS_MODE_RISCVC)
sources = []

def load(rel):
    return json.loads((ROOT/rel).read_text(encoding='utf-8'))

usb = load('reverse/analysis/usb-interface-ota-0041-20261023.json')
dock = load('reverse/analysis/dock-presence-polling-0041-20261023/retained-functions.json')
miio = load('reverse/analysis/miio-deferred-settings-0041-20261023/retained-functions.json')
uart = load('reverse/analysis/uart-response-0041-20261023.json')
selected = []
for address in ['0xa00a3ab6','0xa00a3d22','0xa00a4708','0xa00a8330']:
    f = next(f for f in usb['functions'] if f['address']==address)
    selected.append((address,f, 'reverse/analysis/usb-interface-ota-0041-20261023.json'))
for address in ['0xa00a41f2','0xa00a805a']:
    f = next(f for f in dock['functions'] if f['normalized_result']['procedure']['address']==address)
    selected.append((address,f,'reverse/analysis/dock-presence-polling-0041-20261023/retained-functions.json'))
for address in ['0xa00a0bd8']:
    f = next(f for f in miio['functions'] if f['normalized_result']['procedure']['address']==address)
    selected.append((address,f,'reverse/analysis/miio-deferred-settings-0041-20261023/retained-functions.json'))
selected.append(('0xa00a8582',uart['functions'][0],'reverse/analysis/uart-response-0041-20261023.json'))
for address,f,rel in selected:
    sources.append(dict(address=address,path=rel,evidence_id=f['evidence_id'],profile_digest=f.get('profile_digest') or f['profile']['digest']))

windows = [
 ('cleanup',0xa00a3ab6,0xa00a3b22), ('ui_deinit',0xa00a3d22,0xa00a3d80),
 ('adc_offline',0xa00a42d4,0xa00a430c), ('ota_exit',0xa00a4708,0xa00a4762),
 ('reset',0xa00a5558,0xa00a55ba), ('initializer_prefix',0xa00a55ba,0xa00a5600),
 ('timer_phase3_restart',0xa00a80a8,0xa00a8190),
 ('timer_retry_resume',0xa00a82be,0xa00a831a),
 ('timer_stage3',0xa00a831a,0xa00a8330),
 ('event23',0xa00a8836,0xa00a8856),
 ('parser_dispatch',0xa00a84be,0xa00a8552),
 ('miio_entry',0xa00a0bd8,0xa00a0c42),
 ('miio_release',0xa00a0cce,0xa00a0cf0),
 ('miio_mode',0xa00a0cf0,0xa00a0d08),
]
records=[]
for name,start,end in windows:
    rows=[]; pc=start
    while pc<end:
        off=pc-BASE; size=4 if rom[off]&3==3 else 2
        assert pc+size<=end, (name,hex(pc))
        raw=rom[off:off+size]; ins=list(decoder.disasm(raw,pc))
        asm=ins[0].mnemonic+' '+ins[0].op_str if len(ins)==1 else 'UNKNOWN'
        row=dict(pc=hex(pc),raw=raw.hex(),asm=asm)
        for address,f,rel in selected:
            for b in f.get('raw_ranges',[]):
                payload=bytes.fromhex(b.get('hex',b.get('bytes_hex','')))
                a=int(b['start'],16) if 'start' in b else b['file_offset']+BASE
                z=a+len(payload)
                if a<=pc and pc+size<=z:
                    assert payload[pc-a:pc-a+size]==raw, (hex(pc),rel)
                    row['retained_evidence']=f['evidence_id']
                    break
        rows.append(row);pc+=size
    records.append(dict(name=name,start=hex(start),end_exclusive=hex(end),rows=rows))

rows={int(r['pc'],16):r for w in records for r in w['rows']}
checks=[]
def check(pc,needle):
    assert needle in rows[pc]['asm'], (hex(pc),rows[pc],needle)
    checks.append(dict(pc=hex(pc),expected=needle))
for pc,needle in [
 (0xa00a3b10,'zero, 0x51d'),(0xa00a3b18,'zero, 0x50c'),
 (0xa00a557c,'zero, 0x1d'),(0xa00a55fc,'jal '),
 (0xa00a80ae,'0xc5(s1)'),(0xa00a80b2,'beqz'),
 (0xa00a80ba,'0x50c'),(0xa00a80ce,'0x32'),
 (0xa00a80e0,'0x60'),(0xa00a80f6,'0x61'),
 (0xa00a8110,'zero, 0x6c0'),(0xa00a8114,'zero, 0(s3)'),
 (0xa00a814e,'c.bnez'),(0xa00a8160,'a5, 0x6c0'),
 (0xa00a816c,'zero, 0(a5)'),(0xa00a8170,'zero, 0x30'),
 (0xa00a8174,'zero, 0x60'),(0xa00a8178,'zero, 0x90'),
 (0xa00a8848,'a4, 0(a5)'),(0xa00a851a,'a5, 0(s3)'),
 (0xa00a852e,'0(s4)'),(0xa00a8538,'c.jalr'),
 (0xa00a853a,'0(s4)'),(0xa00a8546,'c.jalr'),
 (0xa00a0bf0,'0(a0)'),(0xa00a0c20,'0(s4)'),
 (0xa00a0cd4,'zero, 0(s5)'),(0xa00a0cf4,'-0xe(a5)'),
 (0xa00a0cf8,'a0, -1'),(0xa00a0cfa,'a0, a0, 0xff'),
 (0xa00a0cfe,'bltu'),(0xa00a0d06,'c.j')]: check(pc,needle)

def signed(v,n): return v-(1<<n) if v>>(n-1) else v
calls={0xa00a4302:0xa00a3d22,0xa00a4306:0xa00a3ab6,
       0xa00a4710:0xa00a3d22,0xa00a4714:0xa00a3ab6,
       0xa00a55fc:0xa00a5558,0xa00a8150:0xa00a5558,
       0xa00a818c:0xa01951e2,0xa00a82be:0xa00eea08,
       0xa00a82ee:0xa0191746,0xa00a832a:0xa00eea08,
       0xa00a884c:0xa00a3d22,0xa00a8850:0xa00a3ab6,
       0xa00a0cd0:0xa002e14e,0xa00a0d02:0xa019537a}
for pc,target in calls.items():
    v=int.from_bytes(rom[pc-BASE:pc-BASE+4],'little');assert v&127==111
    d=signed(((v>>31)<<20)|(((v>>12)&255)<<12)|(((v>>20)&1)<<11)|(((v>>21)&1023)<<1),21)
    assert (pc+d)&0xffffffff==target,(hex(pc),hex(target))
    checks.append(dict(pc=hex(pc),call_target=hex(target)))
branches={0xa00a80b2:0xa00a826c,0xa00a80be:0xa00a8118,
          0xa00a80c6:0xa00a82be,0xa00a84f6:0xa00a8548,
          0xa00a8502:0xa00a8548,0xa00a0c34:0xa00a0cf0,
          0xa00a0cfe:0xa00a0cce,0xa00a8844:0xa00a85e4}
for pc,target in branches.items():
    v=int.from_bytes(rom[pc-BASE:pc-BASE+4],'little');assert v&127==99
    d=signed(((v>>31)<<12)|(((v>>7)&1)<<11)|(((v>>25)&63)<<5)|(((v>>8)&15)<<1),13)
    assert (pc+d)&0xffffffff==target,(hex(pc),hex(target),hex(pc+d))
    checks.append(dict(pc=hex(pc),branch_target=hex(target)))

# Discovery is bounded to existing metadata, not a ROM-wide instruction scan.
meta=load('evidence/rea-0041-20261017/evidence/whole-rom-coverage-0041-20261023-initial.json')
callers=[dict(address=f['address'],evidence_id=f['direct_calls']['evidence_id']) for f in meta['functions']
         if '0xa00a5558' in f.get('direct_calls',{}).get('callees',[])]
assert {f['address'] for f in callers}=={'0xa00a55ba','0xa00a805a'}
result=dict(claim='P-01',rom_identity='CATALOG 0041; length 6769704; inherited SHA256 972db4c136c7ed9e24a83c07c1a7fd62040ca018b08ca285216d26b1fee3c6b9',
    mapping='VA - 0x9ffff000',method='Capstone bounded offline original-byte decode and independent JAL bitfields; no new REA Evidence/profile',
    sources=sources,windows=records,checks=checks,reset_direct_callers_metadata=callers,
    metadata_source='evidence/rea-0041-20261017/evidence/whole-rom-coverage-0041-20261023-initial.json',
    limitations=['Timer slice a00a830a is retained UNKNOWN; inherited vendor addsl interpretation not re-certified here.',
                 'Direct caller lists do not cover unknown computed aliases or external concurrency.',
                 'Source profiles apply only to their stated retained Evidence; original-byte-only initializer prefix has no REA profile.'])
owner=load('reverse/analysis/factory-test-0041-20261023/retained-initializer.json')['function']
result['successor_seed']=dict(path='reverse/analysis/factory-test-0041-20261023/retained-initializer.json',
    evidence_id=owner['evidence_id'],profile_digest=owner['profile']['digest'],
    scope='Retained assembly seed only; s3 handle ownership/close not yet established.',
    assembly=[s for s in owner['assembly'] if 0xa005b2f4<=int(s.split(':')[0],16)<=0xa005b310])
(OUT/'instruction-evidence.json').write_text(json.dumps(result,indent=2)+'\n',encoding='utf-8')
(OUT/'instruction-evidence.txt').write_text('\n\n'.join(w['name']+'\n'+'\n'.join(r['pc']+' '+r['raw']+' '+r['asm'] for r in w['rows']) for w in records)+'\n',encoding='utf-8')
print(json.dumps(dict(status='PASS',windows=len(records),bytes=sum(int(w['end_exclusive'],16)-int(w['start'],16) for w in records),instructions=len(rows),checks=len(checks),unknown=[r['pc'] for r in rows.values() if r['asm']=='UNKNOWN'],retained_compared=sum('retained_evidence' in r for r in rows.values()))))
