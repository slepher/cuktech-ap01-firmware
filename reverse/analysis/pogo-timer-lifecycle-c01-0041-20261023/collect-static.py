"""C01: offline instruction checks only; no target execution or model writes."""
import json,re
from pathlib import Path
from capstone import Cs, CS_ARCH_RISCV, CS_MODE_RISCV32, CS_MODE_RISCVC, cs_version
HERE=Path(__file__).resolve().parent
ROOT=HERE.parents[2]
MAIN=Path('D:/Documents/PlatformIO/Projects/cuktech-ap01-firmware')
BASE=0x9ffff000
rom=(MAIN/'roms/0041/ap01-1.0.2_0041.bin').read_bytes()
f=json.loads((ROOT/'reverse/analysis/factory-test-0041-20261023/retained-initializer.json').read_text())['function']
cb=json.loads((ROOT/'reverse/analysis/dock-presence-polling-0041-20261023/retained-functions.json').read_text())['functions'][1]
assert cb['normalized_result']['procedure']['address']=='0xa00a805a'
for rec in [f,cb]:
    for r in rec['raw_ranges']:
        start=int(r['start'],16); expected=bytes.fromhex(r['hex'])
        assert rom[start-BASE:start-BASE+len(expected)]==expected
cs=Cs(CS_ARCH_RISCV,CS_MODE_RISCV32|CS_MODE_RISCVC)
windows=[]
for name,start,end in [('context_alloc',0xa005cbba,0xa005cc1e),('registration',0xa005ab4c,0xa005ab6e),('timer_create',0xa008bc64,0xa008bd16),('callback_context',0xa00a805a,0xa00a8072),('pogo_deinit',0xa005c8f8,0xa005c9ea)]:
    lines=[]; pc=start
    while pc<end:
        size=4 if rom[pc-BASE]&3==3 else 2
        raw=rom[pc-BASE:pc-BASE+size]
        ins=next(cs.disasm(raw,pc),None)
        assert ins is not None,hex(pc)
        lines.append(dict(address=hex(pc),hex=raw.hex(),decode=ins.mnemonic+' '+ins.op_str))
        pc+=size
    assert pc==end
    windows.append(dict(name=name,start=hex(start),end_exclusive=hex(end),instructions=lines))
# Resolve the simple adjacent AUIPC/JALR pairs as well as explicit JAL targets.
def calls(asm):
    out=[]
    for i,s in enumerate(asm):
        addr=int(s.split(':')[0],16)
        m=re.search(r'jal ra, (0x[0-9a-f]+)$',s)
        if m: out.append(dict(site=hex(addr),target=m[1],kind='jal'))
        m=re.search(r'auipc ra, (0x[0-9a-f]+)$',s)
        if m and i+1<len(asm):
            n=re.search(r'jalr ra, ra, (-?0x[0-9a-f]+)$',asm[i+1])
            if n: out.append(dict(site=asm[i+1].split(':')[0],target=hex((addr+(int(m[1],16)<<12)+int(n[1],16))&0xffffffff),kind='auipc/jalr'))
    return out
initcalls=calls(f['assembly']); cbcalls=calls(cb['normalized_result']['assembly'])
search=dict(bounds={'initializer':f['procedure'],'callback':cb['normalized_result']['procedure']},
            known_delete_target='0xa008ae58',initializer_delete_calls=[x for x in initcalls if x['target']=='0xa008ae58'],callback_delete_calls=[x for x in cbcalls if x['target']=='0xa008ae58'],
            initializer_calls=initcalls,callback_calls=cbcalls,
            deinit_assembly=[s for s in f['assembly'] if 0xa005c8f8<=int(s.split(':')[0],16)<0xa005c9ea],
            limitations=['Only observed initializer and callback body searched; no all-ROM pointer alias proof.', 'Resolved adjacent AUIPC/JALR and explicit JAL; other indirect calls remain unknown.','No shutdown conclusion is inferred from absence of the known delete target.'])
result=dict(task='C01',sources=[dict(path='reverse/analysis/factory-test-0041-20261023/retained-initializer.json',evidence_id=f['evidence_id'],profile_digest=f['profile']['digest']),dict(path='reverse/analysis/dock-presence-polling-0041-20261023/retained-functions.json',evidence_id=cb['evidence_id'],profile_digest=cb['profile']['digest'])],engine=dict(capstone=cs_version()),windows=windows,bounded_search=search,
            validation={'retained_raw_ranges_match_rom':True,'window_instruction_bytes':sum(sum(len(bytes.fromhex(i['hex'])) for i in w['instructions']) for w in windows),'unknown_instructions_in_selected_windows':0,'firmware_executed':False})
(HERE/'instruction-evidence.json').write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
print(json.dumps(result['validation']))
