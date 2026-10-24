"""A58: old metadata only; no ROM, target, decoder, or historical script use."""
from pathlib import Path
import json
import re

MAIN=Path('D:/Documents/PlatformIO/Projects/cuktech-ap01-firmware')
OUT=Path(__file__).resolve().parent
EV=MAIN/'evidence/rea-0041-20261017/evidence'
checks=[]
def check(label,got,want):
    assert got==want,(label,got,want)
    checks.append(dict(label=label,value=got))
def read(rel): return json.loads((MAIN/rel).read_text(encoding='utf8'))

# Search only existing retained text by exact slot spellings, not ROM or all fsdrv code.
roots=['evidence/rea-0041-20261017','reverse/rehost','reverse/analysis']
pattern='62fc974[04]|166072096[04]'
cmd=['rg','-l','-i',pattern,*roots,'-g','*.json','-g','*.md','-g','*.c','-g','*.txt',
     '--hidden','--no-ignore']
# Frozen output from the already-completed bounded query in this task; do not repeat
# that negative search merely to rerun the remaining metadata assertions.
hits=['reverse/analysis/reader-driver-selection-a56-0041-20261024/evidence.json',
      'reverse/analysis/reader-driver-selection-review-a57-0041-20261024/evidence.json']
check('exact slots only inherited reader evidence in selected roots',hits,
      ['reverse/analysis/reader-driver-selection-a56-0041-20261024/evidence.json',
       'reverse/analysis/reader-driver-selection-review-a57-0041-20261024/evidence.json'])

idx=read('reverse/analysis/whole-rom-coverage-0041-20261023-round1.json')
check('index original digest',idx['rom_sha256'],
      '972db4c136c7ed9e24a83c07c1a7fd62040ca018b08ca285216d26b1fee3c6b9')
check('index does not publish global-slot xrefs',
      [k for k in idx if any(t in k.lower() for t in ['global','xref'])],[])
check('selector index entry',idx['functions'][5912]['address'],'0xa019d6a4')
check('selector has no historical dossier',idx['functions'][5912]['historical_dossier'],None)
check('selector has no new dossiers',idx['functions'][5912]['dossiers'],[])
check('generic fs source path identity',idx['source_paths'][239]['address'],'0xa02631a8')
check('posix path identity kept separate',idx['source_paths'][321]['address'],'0xa056b8e0')

a56=read('reverse/analysis/reader-driver-selection-a56-0041-20261024/evidence.json')
a57=read('reverse/analysis/reader-driver-selection-review-a57-0041-20261024/evidence.json')
check('A56 accepted head seed',a56['derived']['head_slot'],'0x62fc9744')
check('A56 accepted stride seed',a56['derived']['stride_slot'],'0x62fc9740')
check('A56 baseline frozen',a56['baseline'],'32f9c9e')
check('A57 inherited identity digest',a57['identity']['inherited_sha256'],
      '972db4c136c7ed9e24a83c07c1a7fd62040ca018b08ca285216d26b1fee3c6b9')

# Necessary old owner/name/ref facets and at most six already-retained assembly lines per seed.
selected=[]
spec=[('whole-rom-retained-20261023-000.json','0xa005cc1e',
       ['0xa005cc6c','0xa005cc70','0xa005cc74','0xa005cd62','0xa005ced6']),
      ('whole-rom-retained-private-20261023-000.json','0xa005a736',
       ['0xa005be3a','0xa005be58','0xa005c8ae'])]
for name,owner,seeds in spec:
    j=json.loads((EV/name).read_text(encoding='utf8'));r=j['structuredContent'];n=r['normalized_result']
    check(name+' owner',n['procedure']['address'],owner)
    references=[x for x in n.get('referenced_names',[]) if x.get('address')=='0x62fc957c']
    check(name+' exact source locations',[x['source_address'] for x in references],seeds)
    outgoing=[dict(source=x.get('source_address'),target=x.get('target_address'),
                   kind=x.get('kind',{}).get('type'),write=x.get('kind',{}).get('write'))
              for x in n.get('outgoing_references',[]) if x.get('target_address')=='0x62fc957c']
    check(name+' no exact slot name',
          [x for x in n.get('referenced_names',[]) if x.get('address') in ('0x62fc9740','0x62fc9744')],[])
    asm=n.get('assembly',[]);clips=[]
    for seed in seeds:
        i=next(i for i,s in enumerate(asm) if str(s).startswith(seed+':'))
        clips.append(dict(source=seed,start_index=max(0,i-2),lines=asm[max(0,i-2):i+4]))
    selected.append(dict(file='evidence/rea-0041-20261017/evidence/'+name,
                         pointer='#/structuredContent/normalized_result',
                         evidence_id=r.get('evidence_id'),profile=r.get('analysis_profile'),owner=owner,
                         names=references,outgoing=outgoing,clips=clips,
                         source_bundle=j.get('source_bundle')))

# Management explicitly allowed the one encountered +0x1c4 store's old s1/caller chain.
old_owner=json.loads((EV/'whole-rom-retained-private-20261023-000.json').read_text())['structuredContent']
oa=old_owner['normalized_result']['assembly']
store_i=next(i for i,s in enumerate(oa) if s.startswith('0xa005a8f4:'))
check('encountered store text',oa[store_i],'0xa005a8f4: sw zero, 0x1c4, s1')
s1_defs=[s for s in oa[:store_i+1] if re.match(
    r'0x[0-9a-f]+: (?:c\.)?(?:mv|li|lui|lw|addi|add|sub|andi|or|xor|and|srli|slli) s1(?:,| )',s)]
check('selected ordinary s1 definitions before store',s1_defs,['0xa005a77a: c.mv s1, a0'])
check('owner old listed caller',
      [c['address'] for c in old_owner['normalized_result']['callers']],['0xa005cc1e'])
caller=json.loads((EV/'whole-rom-retained-20261023-000.json').read_text())['structuredContent']
ca=caller['normalized_result']['assembly']
def line(pc): return next(s for s in ca if s.startswith(pc+':'))
check('caller frame base',line('0xa005cc2a'),'0xa005cc2a: addi s0, sp, 0x400')
check('caller passes local pointer',line('0xa005cec2'),'0xa005cec2: addi a0, s0, -0x240')
check('caller direct target',line('0xa005cec6'),'0xa005cec6: jal ra, 0xa005a736')
candidate_disambiguation=dict(owner='0xa005a736',owner_evidence=old_owner['evidence_id'],
    store=oa[store_i],s1_definitions=s1_defs,
    caller='0xa005cc1e',caller_evidence=caller['evidence_id'],
    caller_lines=[line('0xa005cc2a'),line('0xa005cebe'),line('0xa005cec2'),line('0xa005cec6')],
    conclusion='The observed old callsite supplies a caller-frame local pointer, not an established G/slot binding; not a proven 0x62fc9740 writer',
    limitation='Old displayed assembly/owner/caller metadata only; ordinary s1 definition filter is bounded, not a complete new alias/control-flow proof')

screen=read('evidence/rea-0041-20261017/evidence/screen-host-append-20261020-v2.evidence.json')
screen_r=screen['records'][3];sn=screen_r['normalized_result']
check('screen base-reference owner',sn['procedure']['address'],'0xa00b2f6c')
screen_names=[x for x in sn.get('referenced_names',[]) if x.get('address')=='0x62fc957c']
check('screen base xref count',len(screen_names),1)
check('screen no exact slot target',
      [x for x in sn.get('outgoing_references',[]) if x.get('target_address') in ('0x62fc9740','0x62fc9744')],[])
screen_meta=dict(file='evidence/rea-0041-20261017/evidence/screen-host-append-20261020-v2.evidence.json',
                 pointer='#/records/3/normalized_result',evidence_id=screen_r.get('evidence_id'),
                 owner='0xa00b2f6c',names=screen_names,
                 unrelated_immediate='Separate records/8 owner 0xa00b3252 has 0xa00b330a: li a2, 0x1c4; constant alone does not bind a slot')

owner_entries=[]
for owner in ['0xa005cc1e','0xa005a736','0xa00b2f6c']:
    entry=next(f for f in idx['functions'] if f['address']==owner)
    owner_entries.append(dict(address=owner,extent=entry.get('extent'),dossiers=entry.get('dossiers'),
                              historical_dossier=entry.get('historical_dossier'),
                              limitation='Owner of a global-base reference, not a proven reader-slot writer'))
check('three base owners distinct',len({f['address'] for f in owner_entries}),3)

reports={}
for name in ['application-rehost-complete-0041-20261017.md','reader-driver-reuse-gap-j08-0041-20261024.md',
             'photo-reader-source-a54-0041-20261024.md','reader-driver-selection-review-a57-0041-20261024.md']:
    p=MAIN/'reverse/reports/ap01'/name
    check(name+' available',p.is_file(),True)
    reports[name]=dict(path=str(p.relative_to(MAIN)),
                       use='Inherited coverage/source and unresolved-instance boundary only')

out=dict(status='PASS-old-metadata-only',task='A58',claim='J08/3',baseline='bd457a6',
         identity=dict(version='AP01 1.0.2_0041',path='roms/0041/ap01-1.0.2_0041.bin',
                       length_inherited=6769704,sha256_inherited=idx['rom_sha256'],
                       mapping='file_offset = VA - 0x9ffff000',rom_read=False,hash_recomputed=False),
         checks=checks,search=dict(command=cmd,roots=roots,pattern=pattern,hits=hits,
              status='Frozen successful rg output observed earlier in A58; not repeated by this collector',
              limitation='Text fields in selected retained roots; no claim about unretained data, dynamic writes, aliases or all history'),
         selected_base_metadata=selected,screen_metadata=screen_meta,owner_index=owner_entries,
         source_path239=dict(pointer='#/source_paths/239',address=idx['source_paths'][239]['address'],
                             owners=sorted({r['owner']['procedure'] for r in idx['source_paths'][239]['references']})),
         rejected_as_identity=dict(address='0xa005a8f4',retained_instruction='sw zero, 0x1c4, s1',
                                    reason='Old actual caller supplies frame-local a0; no proof s1 is G=0x62fc957c'),
         candidate_disambiguation=candidate_disambiguation,
         inherited_reports=reports,
         result='No proven initializer/registration writer -> reader N.word0=D bridge in selected retained metadata',
         next_seed=dict(targets=['0x62fc9740','0x62fc9744'],
                        required='A bounded write-xref/initialization metadata record tying an owner to these exact slots; new query/window needs management registration'),
         limits=['No ROM or new decompilation','No shared REA state changed','No target/model/input execution',
                 'No actual driver or POSIX/slot binding','No full fsdrv or callee expansion'])
(OUT/'reuse-result.json').write_text(json.dumps(out,ensure_ascii=False,indent=2)+'\n',encoding='utf8')
print(json.dumps(dict(status=out['status'],checks=len(checks),exact_slot_hits=len(hits),base_owner_count=3)))
