"""Offline ROM/retained checks only; no target or instruction model execution."""
import json
from pathlib import Path
import capstone
from capstone import Cs, CS_ARCH_RISCV, CS_MODE_RISCV32, CS_MODE_RISCVC

MAIN = Path('D:/Documents/PlatformIO/Projects/cuktech-ap01-firmware')
HERE = Path(__file__).resolve().parent
BASE = 0x9ffff000
rom = (MAIN/'roms/0041/ap01-1.0.2_0041.bin').read_bytes()
assert len(rom) == 6769704
old = json.loads((MAIN/'reverse/rehost/system-complete-0041.json').read_text(encoding='utf8'))
assert old['source']['sha256'] == '972db4c136c7ed9e24a83c07c1a7fd62040ca018b08ca285216d26b1fee3c6b9'
rows = [x for x in old['local_disassembly']['0xa00ad486'] if int(x['address'],16) < 0xa00ad602]
assert rows[0]['address'] == '0xa00ad486'
pos = 0xa00ad486
for r in rows:
    at = int(r['address'],16)
    raw = bytes.fromhex(r['bytes'])
    assert at == pos and rom[at-BASE:at-BASE+len(raw)] == raw
    pos += len(raw)
assert pos == 0xa00ad602
# Reuse the complete old body, save only necessary sparse views.
cs = Cs(CS_ARCH_RISCV, CS_MODE_RISCV32 | CS_MODE_RISCVC)
ins = list(cs.disasm(rom[0xa00ad486-BASE:0xa00ad602-BASE],0xa00ad486))
assert len(ins) == len(rows) and sum(i.size for i in ins) == 380
by = {i.address:i for i in ins}
for i,r in zip(ins,rows):
    assert i.address == int(r['address'],16) and i.bytes.hex() == r['bytes']
calls = {hex(i.address):hex(i.address+int(i.op_str.split(',')[-1],0)) for i in ins if i.mnemonic=='jal'}
assert set(calls.values()) == {'0xa00d8f7c','0xa00d9044','0xa00dbb68'}
assert calls['0xa00ad5d8'] == '0xa00dbb68'
stores = [{'address':hex(i.address),'assembly':i.mnemonic+' '+i.op_str} for i in ins if i.mnemonic in ('sb','sh','sw','c.sw','c.swsp')]
assert len(stores)==3 and all(x['assembly'].startswith('c.swsp ') and '(sp)' in x['assembly'] for x in stores)
assert not any(i.mnemonic=='andi' for i in ins)
anchors = {
 0xad494:('beq','a1, a5, 0x126'),0xad498:('bltu','a5, a1, 0x42'),
 0xad49c:('beqz','a1, 0x54'),0xad4a0:('bnez','a3, 0xb0'),
 0xad4aa:('c.bnez','a2, 0x78'),0xad4f4:('c.bnez','a2, 0x18'),
 0xad552:('bne','a3, a5, -0x6c'),0xad55c:('c.bnez','a2, 0x30'),
 0xad5c2:('beqz','a2, -0xbc'),0xad5ca:('lw','a1, 0xbc(s1)'),
 0xad5ce:('lw','a0, 0xc8(s1)'),0xad5d2:('c.li','a4, 0x1e'),
 0xad5d4:('c.li','a3, 0'),0xad5d6:('c.li','a2, 2'),
 0xad5e0:('bne','a3, a5, -0xfa'),0xad5ea:('beqz','a2, -0xe4'),
 0xad5f2:('lw','a1, 0xe4(s1)'),0xad5f6:('lw','a0, 0xf0(s1)'),
 0xad600:('c.j','-0x28')}
for at,(mn,op) in anchors.items():
    i=by[0xa0000000+at]
    assert (i.mnemonic,i.op_str)==(mn,op),(hex(i.address),i.mnemonic,i.op_str)
coverage=json.loads((MAIN/'reverse/analysis/whole-rom-coverage-0041-20261023-round1.json').read_text(encoding='utf8'))
f=next(x for x in coverage['functions'] if x['address']=='0xa00ad486')
assert f['extent']['body']['total_bytes']==380
assert f['direct_calls']['callees']==['0xa00d8f7c','0xa00d9044','0xa00dbb68']
bundle=json.loads((MAIN/'evidence/rea-0041-20261017/evidence/whole-rom-paths-20261023.evidence.json').read_text(encoding='utf8'))
r=next(x for x in bundle['records'] if x['evidence_id']==f['inventory_evidence'])
assert r['analysis_profile']['parameters']['language_id']=='RISCV:LE:32:ap01thead2'
assert r['analysis_profile']['digest']=='b6368dd18431e8113aa5026c713d41e648ab0f6ddd9421ff6c4a49e23b3cd2f3'
spans=[(0xad490,0xad4ac),(0xad4f0,0xad522),(0xad522,0xad550),(0xad550,0xad55e),(0xad58c,0xad602)]
selected=[{'address':hex(i.address),'bytes':i.bytes.hex(),'assembly':i.mnemonic+' '+i.op_str} for i in ins if any(0xa0000000+lo<=i.address<0xa0000000+hi for lo,hi in spans)]
evidence={'status':'PASS','original_identity':'roms/CATALOG.md / 0041','old_body_source':'reverse/rehost/system-complete-0041.json#/local_disassembly/0xa00ad486','old_body_profile':old['source']['tools'],'local_decoder':'Capstone '+capstone.__version__+' RV32+C; standard instructions only','inventory_profile':r['analysis_profile'],'inventory':f,'selected_instructions':selected,'direct_call_targets':calls,'all_local_stores':stores,'limitations':['Complete old body reused, not a new REA decompilation.','No firmware/model/runtime/display execution.','Manual register and branch interpretation, not formal value-flow proof.','Contract scoped to kind 0/1/2, enable 0/1, index 0/1. Public GUI side effects remain API boundary.']}
(HERE/'evidence.json').write_text(json.dumps(evidence,ensure_ascii=False,indent=2)+'\n',encoding='utf8')
checks={'status':'PASS','retained_body_bytes_matched':380,'retained_body_instructions_matched':len(ins),'sparse_spans':len(spans),'sparse_bytes':sum(len(bytes.fromhex(x['bytes'])) for x in selected),'sparse_instructions':len(selected),'operand_anchors':len(anchors),'direct_calls_checked':len(calls),'store_sites_checked':len(stores),'new_decompilations':0,'target_executions':0}
(HERE/'checks.json').write_text(json.dumps(checks,indent=2)+'\n',encoding='utf8')
print(checks)
