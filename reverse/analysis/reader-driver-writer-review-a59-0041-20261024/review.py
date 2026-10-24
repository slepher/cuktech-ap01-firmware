"""A59 independent review of selected retained metadata only.

No ROM reads, disassembler, REA query, corpus re-search or A58 script execution.
"""
import json
import re
from pathlib import Path

MAIN=Path('D:/Documents/PlatformIO/Projects/cuktech-ap01-firmware')
OUT=Path(__file__).resolve().parent
EV=MAIN/'evidence/rea-0041-20261017/evidence'
checks=[]
def load(p):return json.loads(p.read_text(encoding='utf8'))
def check(label,actual,expected):
    assert actual==expected,(label,actual,expected)
    checks.append(dict(label=label,value=actual))
def line(asm,pc):return next(s for s in asm if s.startswith(pc+':'))
def digest(r):
    p=r.get('analysis_profile')
    return p.get('digest') if isinstance(p,dict) else p

# Historical negative-query record is an input claim, not re-executed evidence.
a58=load(MAIN/'reverse/analysis/reader-driver-writer-gap-a58-0041-20261024/reuse-result.json')
s=a58['search']
check('historical query roots',s['roots'],['evidence/rea-0041-20261017','reverse/rehost','reverse/analysis'])
check('historical textual query pattern',s['pattern'],'62fc974[04]|166072096[04]')
check('decimal slot0 spelling',int('62fc9740',16),1660720960)
check('decimal slot1 spelling',int('62fc9744',16),1660720964)
check('query is frozen and not repeated','not repeated' in s['status'],True)
check('query format filters',[s['command'][i+1] for i,v in enumerate(s['command']) if v=='-g'],
      ['*.json','*.md','*.c','*.txt'])
check('query hidden and ignored files included',all(x in s['command'] for x in ['--hidden','--no-ignore']),True)
check('recorded old hit count',len(s['hits']),2)
for h in s['hits']:check('recorded old hit exists '+h,(MAIN/h).is_file(),True)

idx=load(MAIN/'reverse/analysis/whole-rom-coverage-0041-20261023-round1.json')
check('index original identity',idx['rom_sha256'],'972db4c136c7ed9e24a83c07c1a7fd62040ca018b08ca285216d26b1fee3c6b9')
check('index mapping',idx['base_address'],'0x9ffff000')
check('top-level lacks global-slot-xref facet',[k for k in idx if 'global' in k.lower() or 'xref' in k.lower()],[])
f=idx['functions'][5912]
check('selector identity',f['address'],'0xa019d6a4')
check('selector historical dossier absent',f['historical_dossier'],None)
check('selector dossiers absent',f['dossiers'],[])

r=load(EV/'whole-rom-retained-private-20261023-000.json')['structuredContent']
n=r['normalized_result'];asm=n['assembly']
check('store owner',n['procedure']['address'],'0xa005a736')
check('store text',line(asm,'0xa005a8f4'),'0xa005a8f4: sw zero, 0x1c4, s1')
check('ordinary s1 capture',line(asm,'0xa005a77a'),'0xa005a77a: c.mv s1, a0')
prefix=[t for t in asm if 0xa005a736<=int(t.split(':')[0],16)<0xa005a77a]
check('no displayed prefix call/jump before capture',
      [t for t in prefix if re.search(r': (?:c\.)?(?:jal|jalr|j|jr)\b',t)],[])
check('no displayed prefix a0 definition',
      [t for t in prefix if re.search(r': (?:c\.)?(?:mv|li|lui|lw|addi|add|sub|andi|or|xor|and|srli|slli) a0(?:,| )',t)],[])
before_store=[t for t in asm if int(t.split(':')[0],16)<=0xa005a8f4]
check('bounded ordinary s1 definitions',
      [t for t in before_store if re.search(r': (?:c\.)?(?:mv|li|lui|lw|addi|add|sub|andi|or|xor|and|srli|slli) s1(?:,| )',t)],
      ['0xa005a77a: c.mv s1, a0'])
check('old listed caller',[c['address'] for c in n['callers']],['0xa005cc1e'])
store_prov=dict(path='evidence/rea-0041-20261017/evidence/whole-rom-retained-private-20261023-000.json',
               pointer='/structuredContent/normalized_result',evidence_id=r['evidence_id'],
               profile_digest=digest(r),selected_lines=[line(asm,'0xa005a77a'),line(asm,'0xa005a8f4')])

r=load(EV/'whole-rom-retained-20261023-000.json')['structuredContent']
n=r['normalized_result'];asm=n['assembly']
check('caller owner',n['procedure']['address'],'0xa005cc1e')
for pc,want in [('0xa005cc2a','addi s0, sp, 0x400'),('0xa005cebe','addi a1, s0, -0x314'),
               ('0xa005cec2','addi a0, s0, -0x240'),('0xa005cec6','jal ra, 0xa005a736')]:
    check('actual caller line '+pc,line(asm,pc),pc+': '+want)
caller_prov=dict(path='evidence/rea-0041-20261017/evidence/whole-rom-retained-20261023-000.json',
                pointer='/structuredContent/normalized_result',evidence_id=r['evidence_id'],
                profile_digest=digest(r),selected_lines=[line(asm,p) for p in ['0xa005cc2a','0xa005cec2','0xa005cec6']])
check('global stride offset arithmetic',0x62fc957c+0x1c4,0x62fc9740)
check('global head offset arithmetic',0x62fc957c+0x1c8,0x62fc9744)

screen=load(EV/'screen-host-append-20261020-v2.evidence.json')
r3=screen['records'][3];n3=r3['normalized_result']
r8=screen['records'][8];n8=r8['normalized_result']
check('screen actual G-reference owner',n3['procedure']['address'],'0xa00b2f6c')
check('screen G-reference source',[v['source_address'] for v in n3['referenced_names'] if v['address']=='0x62fc957c'],['0xa00b2f98'])
check('screen G-reference old line',line(n3['assembly'],'0xa00b2f98'),'0xa00b2f98: addi a5, a5, 0x57c')
check('screen separate constant owner',n8['procedure']['address'],'0xa00b3252')
check('screen separate constant line',line(n8['assembly'],'0xa00b330a'),'0xa00b330a: li a2, 0x1c4')
check('separate constant does not publish G name',[v for v in n8['referenced_names'] if v['address']=='0x62fc957c'],[])
check('screen G owner no direct exact-slot target metadata',
      [v for v in n3['outgoing_references'] if v.get('target_address') in ['0x62fc9740','0x62fc9744']],[])

result=dict(status='PASS-old-metadata-limited-review',claim='J08/3',review='A59',baseline='bd457a6',
 checks=checks,provenance=[store_prov,caller_prov,
 dict(path='evidence/rea-0041-20261017/evidence/screen-host-append-20261020-v2.evidence.json',
      pointers=['/records/3/normalized_result','/records/8/normalized_result'],
      evidence_ids=[r3['evidence_id'],r8['evidence_id']],profile_digests=[digest(r3),digest(r8)])],
 negative_search=dict(status='Inherited frozen author record; corpus query not independently rerun',
                     roots=s['roots'],pattern=s['pattern'],formats=['JSON','MD','C','TXT'],
                     snapshot_completeness_not_proven=True),
 acceptance='Selected old caller expression is frame-local; same-offset store not an established G writer; screen owners remain distinct',
 new_business=0,semantic_corrections=0,rom_read=False,new_decompilation=False,
 limits=['Ordinary displayed-definition filter is not a new CFG/alias proof',
         'No global absence-of-writer claim, no unknown format/unretained/history coverage claim',
         'No A58/old scripts executed, no target/ROM/model/query execution'])
(OUT/'review-result.json').write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n',encoding='utf8')
print(f'PASS {len(checks)} old-metadata checks; no ROM or repeated corpus search')
