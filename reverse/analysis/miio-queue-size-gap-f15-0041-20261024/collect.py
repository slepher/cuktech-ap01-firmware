"""F15 old retained-evidence locator only; no ROM or target access."""
import json
from pathlib import Path

MAIN=Path('D:/Documents/PlatformIO/Projects/cuktech-ap01-firmware')
OUT=Path(__file__).resolve().parent
UPPER=MAIN/'evidence/rea-0041-20261017/evidence/upper-complete.evidence.json'
INDEX=MAIN/'reverse/analysis/whole-rom-coverage-0041-20261023-round1.json'
upper=json.loads(UPPER.read_text(encoding='utf-8'))
index=json.loads(INDEX.read_text(encoding='utf-8'))
r=upper['records'][248]
assert r['normalized_result']['procedure']['address']=='0xa0064368'
profile=r['analysis_profile']['digest']
assert profile=='4825fb58a33a3e7d618557975b153b8318cf7e833d190ad16bcbf8bd441ae621'
assembly=r['normalized_result']['assembly']
by_pc={int(s.split(':')[0],16):s for s in assembly}
checks=[]
def has(pc,expected):
    line=by_pc[pc]
    assert line==hex(pc)+': '+expected,(hex(pc),line,expected)
    checks.append({'pc':hex(pc),'retained_assembly':line})
for pc,expected in [
 (0xa0064f4a,'addi s7, s1, 0x128'),
 (0xa0065438,'c.li a2, 0x4'),
 (0xa006543a,'li a1, 0x80'),
 (0xa0065448,'addi a0, s1, 0x140'),
 (0xa006544c,'jal ra, 0xa005f0b0'),
 (0xa0065450,'c.beqz a0, 0xa006547e'),
 (0xa0065562,'lui a2, 0xa011e'),
 (0xa006556a,'c.mv a4, s7'),
 (0xa006556c,'addi a2, a2, 0x3d6'),
 (0xa0065570,'addi a0, s0, -0x12c'),
 (0xa0065574,'auipc ra, 0x132'),
 (0xa0065578,'jalr ra, ra, -0x66'),
]:has(pc,expected)
assert 0x128+0x18==0x140
assert 0xa011e000+0x3d6==0xa011e3d6
assert 0xa0065574+0x132000-0x66==0xa019750e
checks.append({'meaning':'output slot and candidate thread argument loop identity',
 'loop':'M+0x128','output_slot':'M+0x140 = loop+0x18',
 'create_request':'0xa005f0b0(&loop.queue,0x80,4)',
 'thread_entry':'0xa011e3d6','thread_create_target':'0xa019750e'})
# The bounded master interval preserves its s7 object through the observed calls.
# This is retained instruction inspection, not emulation or a full alias proof.
definitions=[]
for pc,s in by_pc.items():
    if 0xa0064f4a<pc<=0xa0065578:
        tail=s.split(': ',1)[1]
        if any(tail.startswith(prefix+' s7,') for prefix in
               ['addi','c.addi','c.mv','lw','c.lw','lui','c.lui','add','sub','c.li','li']):
            definitions.append(s)
assert not definitions,definitions
checks.append({'meaning':'no direct listed s7 redefinition in retained master interval',
 'start_exclusive':'0xa0064f4a','end_inclusive':'0xa0065578',
 'limit':'ordinary callee-saved ABI retained; not exhaustive alias/indirect writer certification'})

thread=upper['records'][195]
assert thread['normalized_result']['procedure']['address']=='0xa011e3d6'
refs=[x for x in thread['normalized_result']['incoming_references']
      if x.get('source_address')=='0xa006556c']
assert len(refs)==1
creator=[(i,x) for i,x in enumerate(index['functions']) if x['address']=='0xa005f0b0']
assert len(creator)==1
i,c=creator[0]
assert c['historical_dossier'] is None and c['dossiers']==[]
checks.append({'meaning':'creator body not present in the indexed retained dossier coverage',
 'address':c['address'],'index_pointer':'#/functions/'+str(i)})

result={'claim':'F11/4','task':'F15','baseline':'bd457a6','static_only':True,
 'new_rom_bytes':0,'sources':{'upper':str(UPPER),'index':str(INDEX)},
 'master':{'record':248,'evidence_id':r['evidence_id'],'profile':profile,
 'selected_assembly':[by_pc[pc] for pc in sorted(by_pc) if pc in
 [int(x['pc'],16) for x in checks if 'pc' in x]]},
 'thread_reference':{'record':195,'evidence_id':thread['evidence_id'],
 'profile':thread['analysis_profile']['digest'],'incoming':refs},
 'creator':{'pointer':'#/functions/'+str(i),'metadata':c},'checks':checks,
 'conclusion':'candidate loop.queue constructor request has a2=4; Q.size and F11 ctx-to-loop binding remain open',
 'limits':['No new ROM or creator body','Request a2=4 does not prove stored Q+0x18=4',
 'Candidate thread loop is not automatically identical to F11 ctx+4 loop',
 'No runtime instance, queue lifecycle, or copy4B certification']}
dest=OUT/'evidence.json'
if dest.exists():raise FileExistsError(dest)
dest.write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
print(json.dumps({'result':'PASS','retained_checks':len(checks),'new_rom_bytes':0}))
