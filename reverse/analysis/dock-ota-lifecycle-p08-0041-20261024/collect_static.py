"""Bounded retained/ROM evidence collection; no firmware or model execution."""
import json
from pathlib import Path
from datetime import datetime, timezone
import capstone
from capstone import Cs, CS_ARCH_RISCV, CS_MODE_RISCV32, CS_MODE_RISCVC
ROOT = Path('D:/Documents/PlatformIO/Projects/cuktech-ap01-firmware')
OUT = Path(__file__).resolve().parent
BASE = 0x9ffff000
rom = (ROOT/'roms/0041/ap01-1.0.2_0041.bin').read_bytes()
assert len(rom) == 6769704
sources = {}
ota = json.loads((ROOT/'reverse/analysis/usb-interface-ota-0041-20261023.json').read_text())
uart = json.loads((ROOT/'reverse/analysis/uart-retry-receive-0041-20261023.json').read_text())
for rel, d in [('reverse/analysis/usb-interface-ota-0041-20261023.json', ota), ('reverse/analysis/uart-retry-receive-0041-20261023.json', uart)]:
    for i, f in enumerate(d['functions']):
        sources[f['address']] = dict(f, retained=rel, pointer=f'/functions/{i}')
bundle_rel = 'evidence/rea-0041-20261017/evidence/whole-rom-private-20261023.evidence.json'
bundle = json.loads((ROOT/bundle_rel).read_text())
selected = {'0xa00fcd54','0xa00fd1ac','0xa00afc88','0xa00f6064'}
for i,r in enumerate(bundle['records']):
    n=r.get('normalized_result')
    if not isinstance(n,dict) or not isinstance(n.get('procedure'),dict): continue
    a=n['procedure'].get('address')
    if a not in selected or 'assembly' not in n: continue
    sources[a] = dict(address=a, evidence_id=r['evidence_id'], profile_digest=r['analysis_profile']['digest'],
                      retained=bundle_rel, pointer=f'/records/{i}', assembly=n['assembly'],
                      body=n['procedure'].get('body'), limitations=n.get('limitations',[]))
assert selected <= sources.keys()
# Only the chosen windows are copied; no whole caller or full bundle export.
specs = [
 ('enter',0xa00a56d4,0xa00a5810,'0xa00a56d4'),
 ('exit',0xa00a4708,0xa00a4762,'0xa00a4708'),
 ('status_notify',0xa00a3df4,0xa00a3e54,'0xa00a3df4'),
 ('status_dispatch',0xa00a3a0e,0xa00a3a58,'0xa00a3a0e'),
 ('subscribe',0xa01b25e8,0xa01b2634,'0xa01b25e8'),
 ('unsubscribe',0xa01b25ae,0xa01b25e8,'0xa01b25ae'),
 ('normal_exit_cause',0xa00a5b2a,0xa00a5b54,'0xa00a5810'),
 ('normal_selector1_exit',0xa00a5a2c,0xa00a5a64,'0xa00a5810'),
 ('ordinary_pending_enter',0xa00a8856,0xa00a8870,'0xa00a8582'),
 ('rediscover',0xa00a80a8,0xa00a81cc,'0xa00a805a'),
 ('ota_retry_gate',0xa00a831a,0xa00a8330,'0xa00a805a'),
 ('page_allocations',0xa00fcd74,0xa00fcdec,'0xa00fcd54'),
 ('page_subscribe_and_delete_binding',0xa00fd132,0xa00fd1ac,'0xa00fcd54'),
 ('page_status_callback',0xa00f6064,0xa00f61ae,'0xa00f6064'),
 ('app_enter_a',0xa00b0554,0xa00b0570,'0xa00afc88'),
 ('app_enter_b',0xa00fed84,0xa00fedc0,'0xa00fd1ac'),
 ('page_delete',0xa00f42c6,0xa00f4378,None),
]
cs=Cs(CS_ARCH_RISCV,CS_MODE_RISCV32|CS_MODE_RISCVC)
windows=[]; checks=[]; ins_by_addr={}
for name,start,end,owner in specs:
    raw=rom[start-BASE:end-BASE]; instructions=[]; off=0
    old={int(l.split(':')[0],16):l for l in sources[owner]['assembly']} if owner else {}
    while off<len(raw):
        a=start+off; hw=int.from_bytes(raw[off:off+2],'little'); size=2 if hw&3!=3 else 4
        assert off+size<=len(raw),(name,hex(a))
        b=raw[off:off+size]; dec=list(cs.disasm(b,a,count=1)); instruction=dec[0] if dec else None
        if instruction: assert instruction.size==size
        target=None
        if size==4 and int.from_bytes(b,'little')&0x7f==0x6f:
            v=int.from_bytes(b,'little'); imm=((v>>31)<<20)|(((v>>21)&1023)<<1)|(((v>>20)&1)<<11)|(((v>>12)&255)<<12)
            if imm&(1<<20):imm-=1<<21
            target=hex((a+imm)&0xffffffff)
        item=dict(address=hex(a),bytes_hex=b.hex(),size=size,independent=(instruction.mnemonic+' '+instruction.op_str).strip() if instruction else 'UNKNOWN',retained=old.get(a),direct_jal_target=target)
        if owner: assert a in old,(name,hex(a),'missing retained instruction boundary')
        instructions.append(item);ins_by_addr[a]=item;off+=size
    windows.append(dict(name=name,start=hex(start),end_exclusive=hex(end),file_offset=start-BASE,bytes_hex=raw.hex(),owner=owner,instructions=instructions))
# Match complete raw ranges only for the small inherited contracts selected above.
raw_verified=0
for owner in ['0xa00a56d4','0xa00a4708','0xa00a3df4','0xa00a3a0e','0xa01b25e8','0xa01b25ae']:
    for rr in sources[owner]['raw_ranges']:
        b=bytes.fromhex(rr['bytes_hex']);o=rr['file_offset'];assert rom[o:o+len(b)]==b;raw_verified+=len(b)
    checks.append(dict(kind='retained raw range matches ROM',owner=owner,result='PASS'))
for a,t in [(0xa00a575e,0xa00a3df4),(0xa00a57b8,0xa01951e2),(0xa00a580a,0xa00a3df4),(0xa00a4734,0xa00a3df4),(0xa00a5b4e,0xa00a4708),(0xa00a8864,0xa00a56d4),(0xa00fd16a,0xa01b25e8),(0xa00fd1a6,0xa01ad654),(0xa00b056a,0xa00a56d4),(0xa00fed98,0xa00a56d4),(0xa00fedb8,0xa00a56d4),(0xa00f433a,0xa01b25ae),(0xa00f4340,0xa008ab8a)]:
    assert ins_by_addr[a]['direct_jal_target']==hex(t)
    checks.append(dict(kind='independent JAL target',address=hex(a),target=hex(t),result='PASS'))
# RV32 stores: verify widths, source/base registers and signed immediate from raw encoding.
for a,rs2,rs1,imm,width in [(0xa00a5768,14,15,0x50c,0),(0xa00a5772,14,15,0x4f8,0),(0xa00a5782,15,14,0x6c0,2),(0xa00a4724,15,14,0x6c0,2),(0xa00a4730,14,15,0x4f8,0),(0xa00a4740,0,15,0x50c,0),(0xa00a474e,14,15,0x51c,0),(0xa00fd18e,18,21,4,2),(0xa00fd196,21,9,0x10,2)]:
    v=int.from_bytes(bytes.fromhex(ins_by_addr[a]['bytes_hex']),'little');q=((v>>25)<<5)|((v>>7)&31);q=q-4096 if q&2048 else q
    assert (v&127,(v>>20)&31,(v>>15)&31,q,(v>>12)&7)==(0x23,rs2,rs1,imm,width)
    checks.append(dict(kind='store encoding registers/width/offset',address=hex(a),result='PASS'))
# Read the existing boot head initialization without copying the full boot function.
boot=json.loads((ROOT/'reverse/analysis/uiiface-lifecycle-0041-20261023/instruction-windows.json').read_text())
bw=next(w for w in boot['windows'] if w['name']=='service_boot')
head=[i for i in bw['instructions'] if 0xa00a562c<=int(i['address'],16)<0xa00a5640]
for i in head:
    b=bytes.fromhex(i['hex']);a=int(i['address'],16);assert rom[a-BASE:a-BASE+len(b)]==b
checks.append(dict(kind='OTA list boot head offset8/first0/last0 retained raw',result='PASS'))
summary=dict(window_count=len(windows),window_bytes=sum((int(w['end_exclusive'],16)-int(w['start'],16)) for w in windows),instruction_count=sum(len(w['instructions']) for w in windows),unknown_addresses=[i['address'] for w in windows for i in w['instructions'] if i['independent']=='UNKNOWN'],small_contract_raw_bytes=raw_verified,checks=len(checks))
source_index={a:{k:v for k,v in s.items() if k in ['address','evidence_id','profile_digest','retained','pointer','source','body','limitations']} for a,s in sources.items() if a in {w[3] for w in specs}}
result=dict(claim='P-08',rom=dict(path=str(ROOT/'roms/0041/ap01-1.0.2_0041.bin'),size=len(rom),sha256_inherited=ota['rom_sha256'],mapping='file_offset=VA-0x9ffff000'),tool=dict(kind='offline Python/Capstone raw decode; no target/model execution',capstone_version=capstone.__version__),sources=source_index,windows=windows,boot_head=head,checks=checks,summary=summary,limitations=['Static instruction observations only; no runtime or reentrancy/concurrency proof.','Vendor th.lrw on subscription traversal inherits retained model semantics; UNKNOWN stays unknown.','page_delete is a bounded raw-byte window with no newly assigned REA Evidence/profile; no complete owner-body claim.'])
(OUT/'static-evidence.json').write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
lines=[]
for w in windows:
    lines.append('\n'+w['name'])
    lines.extend(i['address']+' '+i['bytes_hex']+' '+i['independent']+(' | '+i['retained'] if i['retained'] else '') for i in w['instructions'])
(OUT/'static-evidence.txt').write_text('\n'.join(lines)+'\n',encoding='utf-8')
print(json.dumps(summary));print('PASS',len(checks))
