"""J08/1: old report/JSON identity only. No ROM reads or analysis execution."""
from pathlib import Path
import json

OUT=Path(__file__).resolve().parent
TREE=OUT.parents[2]
MAIN=Path('D:/Documents/PlatformIO/Projects/cuktech-ap01-firmware')
checks=[]
def load(p): return json.loads(p.read_text(encoding='utf8'))
def check(label,value):
    assert value,label
    checks.append(label)

management=(MAIN/'reverse/reports/ap01/rolling-management-0041-20261023.md').read_text(encoding='utf8')
design=(MAIN/'reverse/reports/ap01/reverse-design.md').read_text(encoding='utf8')
check('master rules and J08/1 registration present','J08/1' in management and 'A47/1' in management and '管理窗口是认领表的唯一写入者' in design)
check('manager registered J08/2 old evidence scope','J08/2' in management)
catalog=(MAIN/'roms/CATALOG.md').read_text(encoding='utf8')
sha='972db4c136c7ed9e24a83c07c1a7fd62040ca018b08ca285216d26b1fee3c6b9'
check('existing0041 catalog identity only','6,769,704' in catalog and sha in catalog)
index=load(TREE/'reverse/analysis/whole-rom-coverage-0041-20261023-round1.json')
check('index same0041 identity',index['rom_sha256']==sha and index['base_address']=='0x9ffff000')
selector=index['functions'][5912]
check('selector exact entry',selector['address']=='0xa019d6a4')
check('selector extent only500B',selector['extent']['body']['total_bytes']==500)
check('selector has no retained dossier in this index',selector['historical_dossier'] is None and selector['dossiers']==[])

a47=load(TREE/'reverse/analysis/photo-reader-mode-a47-0041-20261024/evidence.json')
rows={r['pc']:r for r in a47['rows']}
for pc,text in [('0xa019d6ec','lbu a2, 0(a1)'),('0xa019d798','sw s1, 4(s2)'),
                ('0xa019d80e','c.lw a4, 0xc(s1)'),('0xa019d818','c.jalr a4')]:
    check('inherited A47 anchor '+pc,rows[pc]['asm']==text)
check('selection gap not supplied by A47 rows',not any(0xa019d708<=int(p,16)<0xa019d798 for p in rows))
check('old negative search inherited not rerun',a47['reuse_search']['boundary'].startswith('main reverse/rehost'))
a49=load(TREE/'reverse/analysis/photo-reader-mode-review-a49-0041-20261024/review-result.json')
check('A49 accepted same interface',a49['status']=='PASS')
a54=load(TREE/'reverse/analysis/photo-reader-source-a54-0041-20261024/candidate-evidence.json')
check('candidate4whole files1GIF difference preserved',[f['local_member_equal'] for f in a54['files']]==[True,True,True,True,False])
a55=(TREE/'reverse/reports/ap01/photo-reader-source-review-a55-0041-20261024.md').read_text(encoding='utf8')
check('A55 does not bind actual instance','实际D' in a55 and '整文件不同' in a55)
a52=(TREE/'reverse/reports/ap01/photo-reader-consumer-review-a52-0041-20261024.md').read_text(encoding='utf8')
check('A52 consumption already accepted','限定接受A50' in a52 and '具体D' in a52)

inverse={}
for target in ['0xa019d6a4','0xa0107d8e']:
    inverse[target]=[dict(pointer=f'/functions/{j}/direct_calls',caller=f['address'],
        evidence_id=f['direct_calls']['evidence_id']) for j,f in enumerate(index['functions'])
        if target in f.get('direct_calls',{}).get('callees',[])]
check('known mode1 wrapper sole listed direct caller',len(inverse['0xa0107d8e'])==1 and inverse['0xa0107d8e'][0]['caller']=='0xa00ed7f4')
check('selector four listed interface users',len(inverse['0xa019d6a4'])==4)

fs=index['source_paths'][239]
check('generic fs source xref only',fs['address']=='0xa02631a8' and fs['text'].endswith('/src/misc/lv_fs.c'))
posix=index['source_paths'][321]
check('actualROM posix source-path anchor',posix['address']=='0xa056b8e0' and posix['text'].endswith('/src/libs/fsdrv/lv_fs_posix.c'))
check('actualROM posix path eight metadata refs',len(posix['references'])==8)
refs=[dict(pointer=f'/source_paths/321/references/{j}',address=r['address'],
    owner=r.get('owner'),xref_evidence=r.get('xref_evidence')) for j,r in enumerate(posix['references'])]
owners=sorted({r.get('owner',{}).get('procedure') for r in posix['references'] if r.get('owner',{}).get('procedure')})
owner_metadata=[]
for j,f in enumerate(index['functions']):
    if f['address'] not in owners: continue
    users=[dict(pointer=f'/functions/{k}/direct_calls',caller=g['address'],evidence_id=g['direct_calls']['evidence_id'])
           for k,g in enumerate(index['functions']) if f['address'] in g.get('direct_calls',{}).get('callees',[])]
    owner_metadata.append(dict(pointer=f'/functions/{j}',address=f['address'],
        historical_dossier=f['historical_dossier'],dossiers=f['dossiers'],historical_contracts=f['historical_contracts'],
        extent_evidence=f['extent']['evidence_id'],direct_call_evidence=f['direct_calls']['evidence_id'],
        direct_calls=f['direct_calls']['callees'],listed_direct_users=users))
check('J08/2 seven exact source owners',len(owner_metadata)==7)
check('J08/2 selected owners only extent/directcall metadata',all(x['historical_dossier'] is None and x['dossiers']==[] and x['historical_contracts']==[] for x in owner_metadata))
check('J08/2 no listed direct callers does not bind slots',all(x['listed_direct_users']==[] for x in owner_metadata))
unknown_containment=[dict(pointer=f'/functions/{j}',address=f['address']) for j,f in enumerate(index['functions'])
    if any(int(r['start'],16)<=0xa00ef67c<=int(r['end'],16) for r in f.get('extent',{}).get('body',{}).get('ranges',[]))]
check('J08/2 unknown source reference still outside listed function extents',unknown_containment==[])

report=(TREE/'reverse/reports/ap01/application-rehost-complete-0041-20261017.md').read_text(encoding='utf8')
check('final confirmsSIM scope distinct',sha in report and '所有模拟成功都只表示SIM服务结果' in report)
out=dict(status='PASS',claim='J08/1',secondary_claim='J08/2',inherited_claim='A47/1',baseline='608da2b',management_update='bc3711a',
    identity=dict(catalog='roms/CATALOG.md:17',bytes=6769704,sha256=sha,mapping='VA-0x9ffff000',ROM_read=False),
    checks=checks,new_functions=0,new_ROM_reads=0,new_decompilation=0,
    selector=dict(pointer='/functions/5912',address=selector['address'],
        extent_evidence=selector['extent']['evidence_id'],direct_call_evidence=selector['direct_calls']['evidence_id'],
        source_path_pointer='/source_paths/239',source_xref_evidence=fs['evidence_ids'],
        known_end='D=s1 saved into W+4 at0xa019d798; A47/1 slots accepted',
        missing_end='selection-chain source and concrete registered D/slot targets not identified'),
    inherited_interface_users=inverse,
    new_connection_request=dict(original_claim='J08/1',registered_claim='J08/2',status='registered old-metadata disambiguation only; no binding found',
        connection='actualROM fsdrv source references -> registration instance -> same selected D (not proven)',
        source=dict(pointer='/source_paths/321',string_address=posix['address'],text=posix['text'],refs=refs),
        intersecting_claims=['A47/1 only shares reader interface; no actualD identity proven',
            'F11/1-2 RPC objects and G19/3 poll objects have no known same-object edge'],
        owner_metadata=owner_metadata,unknown_reference_containment=unknown_containment,
        required_increment='No new ROM/body permission; actual instance/registration/slot bridge remains unknown; any further evidence acquisition needs separate manager registration'),
    limits=['Metadata/source paths are not callback/instance bindings','No whole rehost negative search rerun',
        'Only registered seven-owner old metadata; no new owner-body/registration-callee expansion','Default five photographs remain mode0',
        'No ROM, SIM, QEMU, build, replay, firmware, device, external-service or model execution'])
(OUT/'reuse-result.json').write_text(json.dumps(out,ensure_ascii=False,indent=2)+'\n',encoding='utf8')
print(json.dumps(dict(status='PASS',checks=len(checks),claim='J08/1',metadata_requests=1,new_functions=0,ROM_reads=0)))
