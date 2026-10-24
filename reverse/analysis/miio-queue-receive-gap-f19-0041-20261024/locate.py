"""F19 initial retained-record receive callsite locator; no ROM access."""
import json
from pathlib import Path

MAIN=Path('D:/Documents/PlatformIO/Projects/cuktech-ap01-firmware')
OUT=Path(__file__).resolve().parent
source=MAIN/'evidence/rea-0041-20261017/evidence/upper-complete.evidence.json'
index_path=MAIN/'reverse/analysis/whole-rom-coverage-0041-20261023-round1.json'
upper=json.loads(source.read_text(encoding='utf-8'));r=upper['records'][195]
assert r['normalized_result']['procedure']['address']=='0xa011e3d6'
assert r['evidence_id']=='ev_9a7e0a186c4ed2b341b4d42187fcb73bebec13d401cd226033d30027d121387d'
assembly={int(s.split(':')[0],16):s for s in r['normalized_result']['assembly']}
checks=[]
for pc,asm in [
 (0xa011e408,'c.lui s7, 0x2'),(0xa011e416,'addi s7, s7, 0x710'),
 (0xa011e518,'c.lw a5, 0x2c, s1'),(0xa011e51a,'sw zero, -0x34, s0'),
 (0xa011e51e,'c.beqz a5, 0xa011e5ea'),
 (0xa011e5ea,'c.lw a5, 0x20, s1'),(0xa011e5ec,'c.mv a2, s7'),
 (0xa011e5ee,'c.beqz a5, 0xa011e5f2'),(0xa011e5f0,'c.lw a2, 0x4, a5'),
 (0xa011e5f2,'c.lw a0, 0x18, s1'),(0xa011e5f4,'c.beqz a0, 0xa011e548'),
 (0xa011e5f6,'addi a1, s0, -0x34'),(0xa011e5fa,'jal ra, 0xa005f508'),
 (0xa011e5fe,'c.j 0xa011e548'),(0xa011e548,'lw a1, -0x34, s0'),
 (0xa011e54c,'beq a1, zero, 0xa011e41a'),(0xa011e550,'lbu s2, 0x8, a1'),
 (0xa011e554,'bne s2, zero, 0xa011e608'),
]:
    assert assembly[pc]==hex(pc)+': '+asm,(hex(pc),assembly[pc])
    checks.append({'pc':hex(pc),'retained_assembly':assembly[pc]})
assert 0x2000+0x710==10000
checks.append({'meaning':'default timeout value 10000; timer field copied as word; no unit or runtime range certification'})
index=json.loads(index_path.read_text(encoding='utf-8'))
matches=[(i,x) for i,x in enumerate(index['functions']) if x['address']=='0xa005f508']
assert len(matches)==1
i,metadata=matches[0]
assert metadata['historical_dossier'] is None and metadata['dossiers']==[]
checks.append({'meaning':'known receive adapter only extent/directcall, no indexed retained dossier',
 'address':metadata['address'],'pointer':'#/functions/'+str(i)})
result={'claim':'F11/6','task':'F19','baseline':'bd457a6','static_only':True,'new_rom_bytes':0,
 'retained_source':str(source),'record':195,'evidence_id':r['evidence_id'],
 'profile':r['analysis_profile']['digest'],'selected_rows':[assembly[int(x['pc'],16)] for x in checks if 'pc' in x],
 'index_source':str(index_path),'metadata':metadata,'checks':checks,
 'call':'0xa011e5fa -> 0xa005f508(Q=word(L+0x18),&localI=s0-0x34,timeout)',
 'return_gate':'adapter a0 ignored; localI word gate at e548/e54c decides dispatch entry',
 'limits':['No adapter/new callee body in initial phase','No all timer/timeout range','No internal M copy/release or real receive observation']}
dest=OUT/'locator-evidence.json'
if dest.exists():raise FileExistsError(dest)
dest.write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
print(json.dumps({'result':'PASS','checks':len(checks),'new_rom_bytes':0}))
