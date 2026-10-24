"""P-04: bounded retained-evidence and original-byte checks; no target execution."""
import json
import hashlib
from pathlib import Path
from capstone import Cs, CS_ARCH_RISCV, CS_MODE_RISCV32, CS_MODE_RISCVC, cs_version

ROOT = Path('D:/Documents/PlatformIO/Projects/cuktech-ap01-firmware')
HERE = Path(__file__).resolve().parent
BASE = 0x9ffff000
rom = (ROOT/'roms/0041/ap01-1.0.2_0041.bin').read_bytes()
assert len(rom) == 6769704
response_path = 'reverse/analysis/uart-response-0041-20261023.json'
f = json.loads((ROOT/response_path).read_text())['functions'][0]
assert f['normalized_result']['procedure']['address'] == '0xa00a8582'
source_lines = {int(x.split(':')[0],16): x for x in f['normalized_result']['assembly']}
md = Cs(CS_ARCH_RISCV, CS_MODE_RISCV32 | CS_MODE_RISCVC)
windows = []
at = {}
for name, start, end in [
    ('cmd55_route', 0xa00a8602, 0xa00a860a),
    ('cmd55_control_source', 0xa00a88f6, 0xa00a8950),
    ('cmd55_after_submit', 0xa00a88e2, 0xa00a88ea),
]:
    rows = []; pc = start
    while pc < end:
        off = pc-BASE
        size = 4 if int.from_bytes(rom[off:off+2], 'little') & 3 == 3 else 2
        raw = rom[off:off+size]
        blocks = [r for r in f['raw_ranges'] if int(r['start'],16) <= pc <= int(r['end'],16)]
        assert len(blocks) == 1
        block = blocks[0]; index = pc-int(block['start'],16)
        assert bytes.fromhex(block['hex'])[index:index+size] == raw
        decoded = list(md.disasm(raw,pc))
        # The single vendor word is preserved. Its narrow branch predicate is
        # established by the existing provider, not invented by Capstone.
        row = dict(pc=hex(pc), file_offset=off, hex=raw.hex(), retained=source_lines[pc],
                   decoded=(decoded[0].mnemonic+' '+decoded[0].op_str) if decoded else None)
        rows.append(row); at[pc] = row; pc += size
    assert pc == end
    windows.append(dict(name=name,start=hex(start),end_exclusive=hex(end),rows=rows))

checks=[]
def exact(pc, mnemonic, operands):
    assert at[pc]['decoded'] == mnemonic+' '+operands, at[pc]
    checks.append(dict(pc=hex(pc),kind='independent-decode',expected=mnemonic+' '+operands))
def jal(pc, target):
    w=int.from_bytes(bytes.fromhex(at[pc]['hex']),'little')
    assert w & 127 == 0x6f
    v=((w>>31)<<20)|(((w>>12)&255)<<12)|(((w>>20)&1)<<11)|(((w>>21)&1023)<<1)
    if v & (1<<20): v -= 1<<21
    assert (pc+v)&0xffffffff == target
    checks.append(dict(pc=hex(pc),kind='raw-JAL',target=hex(target)))

for pc,m,o in [
    (0xa00a8602,'addi','a5, zero, 0x55'),
    (0xa00a88f6,'lui','s1, 0x62fcb'),
    (0xa00a88fe,'c.li','a1, 0x18'),
    (0xa00a8900,'addi','a0, s1, 4'),
    (0xa00a8908,'addi','a5, s1, 4'),
    (0xa00a8930,'lhu','a4, 0x10(a5)'),
    (0xa00a8934,'lhu','a3, 0x12(a5)'),
    (0xa00a8938,'c.or','a4, a3'),
    (0xa00a8940,'c.li','a0, 2'),
    (0xa00a8946,'c.li','a1, 1'),
    (0xa00a8948,'c.li','a0, 0xa'),
    (0xa00a88e2,'c.li','a0, 2'),
    (0xa00a894e,'c.j','-0x6c'),
    (0xa00a88e8,'c.j','-0x304'),
]: exact(pc,m,o)
for pc,target in [(0xa00a8904,0xa0191652),(0xa00a8942,0xa00a3a58),
                  (0xa00a894a,0xa00a417c),(0xa00a88e4,0xa00a385a)]: jal(pc,target)
# Both source halfwords are zero iff their OR is zero; the vendor extu
# cannot change this because the OR already has bits 31:16 clear.
w=int.from_bytes(bytes.fromhex(at[0xa00a893a]['hex']),'little')
assert w&127 == 0x0b
assert 'th.extu a4, a4' in at[0xa00a893a]['retained']
assert ((w>>12)&7,(w>>7)&31,(w>>15)&31,(w>>26)&63,(w>>20)&63)==(3,14,14,15,0)
model_path='evidence/rea-0041-20261017/ghidra/Ghidra/Processors/RISCV/data/languages/ap01thead2.sinc'
model_bytes=(ROOT/model_path).read_bytes()
assert hashlib.sha256(model_bytes).hexdigest()=='0ea85159802b556616fb6d074d71624a81c393836e0f8132d228ae2cfdd748ba'
lines=model_bytes.decode().splitlines()
register_path=model_path.replace('.sinc','.reg.sinc')
register_lines=(ROOT/register_path).read_text().splitlines()
register_excerpt=[x for x in register_lines if 'thmsb=' in x or 'thlsb=' in x]
assert [x.strip() for x in register_excerpt]==['thlsb=(20,25)','thmsb=(26,31)']
k=next(i for i,x in enumerate(lines) if x.startswith(':th.extu rd,rs1,15,0 is'))
assert 'local value:4 = rs1 << 16;' in lines[k+2] and 'rd = value >> 16;' in lines[k+3]
checks.append(dict(pc='0xa00a893a',kind='vendor-bounded',raw=at[0xa00a893a]['hex'],
                   decode='th.extu a4,a4,15,0',model_path=model_path,start_line=k+1,
                   register_path=register_path,register_excerpt=register_excerpt,
                   model_sha256=hashlib.sha256(model_bytes).hexdigest(),excerpt=lines[k:k+5],
                   limitation='Read-only existing source model and original instruction bitfields; no model execution or full vendor decoder certification.'))
for pc,target,funct3 in [(0xa00a8606,0xa00a88f6,0), (0xa00a893e,0xa00a8950,7)]:
    raw=bytes.fromhex(at[pc]['hex']); w=int.from_bytes(raw,'little')
    if len(raw)==4:
        assert (w&127,(w>>12)&7)==(0x63,funct3)
        v=((w>>31)<<12)|(((w>>7)&1)<<11)|(((w>>25)&63)<<5)|(((w>>8)&15)<<1)
        if v&4096:v-=8192
    else:
        assert w&3==1 and w>>13==funct3
        v=(((w>>12)&1)<<8)|(((w>>5)&3)<<6)|(((w>>2)&1)<<5)|(((w>>10)&3)<<3)|(((w>>3)&3)<<1)
        if v&256:v-=512
    assert pc+v==target
    checks.append(dict(pc=hex(pc),kind='raw-branch',target=hex(target)))

ledger=json.loads((ROOT/'reverse/analysis/whole-rom-coverage-0041-20261023-round1.json').read_text())
callers=[x['address'] for x in ledger['functions'] if '0xa00a417c' in x['direct_calls']['callees']]
assert callers == ['0xa00a8582']
sites=[x for x in f['normalized_result']['assembly'] if 'jal ra, 0xa00a417c' in x]
assert [x.split(':')[0] for x in sites] == ['0xa00a894a','0xa00a9878','0xa00a98ca']
checks.append(dict(kind='retained-caller-frontier',callers=callers,sites=sites,
                   limitation='Direct provider edges only; not all indirect callers or global writers.'))

negative=[]
for path, wanted in [
    ('reverse/analysis/miio-deferred-settings-0041-20261023/retained-functions.json',
     ['0xa009d8bc','0xa00a0bd8','0xa00a0e78']),
    ('reverse/analysis/mode-control-0041-20261023/retained-functions.json',['0xa0195166']),
]:
    data=json.loads((ROOT/path).read_text())
    for g in data['functions']:
        n=g['normalized_result']; address=n['procedure']['address']
        if address not in wanted: continue
        # Exact textual/reference search is deliberately only a finite exclusion.
        text=json.dumps(n)
        hits={s:text.count(s) for s in ['62fcb51e','62fcb516','a00a417c']}
        assert not any(hits.values())
        negative.append(dict(path=path,procedure=address,evidence_id=g['evidence_id'],
                             profile_digest=g.get('profile_digest') or g.get('profile',{}).get('digest'),hits=hits,
                             limitation='No exact named field/helper occurrence in this retained dossier. Aliases, indirect access and other procedures are not excluded.'))

property_path='evidence/rea-0041-20261017/evidence/whole-rom-private-20261023-024.json'
obj=json.loads((ROOT/property_path).read_text())
e=obj.get('structuredContent') or json.loads(obj['content'][0]['text'])
n=e['normalized_result']
assert n['procedure']['address']=='0xa00a2578'
hits={s:json.dumps(n).count(s) for s in ['62fcb51e','62fcb516','a00a417c']}
assert not any(hits.values())
negative.append(dict(path=property_path,procedure='0xa00a2578',evidence_id=e['evidence_id'],
                     profile_digest=e['analysis_profile']['digest'],hits=hits,
                     limitation='Retained set/get_properties dispatcher exact-name search only. Property cache aliases and refresh callees are not resolved.'))

out=dict(claim='P-04',rom_identity_inherited_from='roms/CATALOG.md',
         method='Capstone bounded offline decode plus raw standard branch/JAL field checks; no REA session created.',
         engine=cs_version(),retained_response=dict(path=response_path,evidence_id=f['evidence_id'],
         profile_digest=f['profile_digest'],source=f['source']),windows=windows,
         checks=checks,negative_searches=negative,
         uncovered=['product/API units and semantic names','all indirect callers/writers',
                    'application property mapping','ack-byte status codes','global shutdown ordering'])
(HERE/'instruction-evidence.json').write_text(json.dumps(out,indent=2,ensure_ascii=False)+'\n',encoding='utf-8')
print(json.dumps(dict(windows=len(windows),bytes=sum(int(x['end_exclusive'],16)-int(x['start'],16) for x in windows),
                     instructions=len(at),checks=len(checks),bounded_negative_dossiers=len(negative))))
