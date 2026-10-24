"""Static reference/composition checks only. Does not read ROM or import old scripts."""
import json
from pathlib import Path

ROOT=Path('D:/Documents/PlatformIO/Projects/cuktech-ap01-firmware')
HERE=Path(__file__).parent
c=json.loads((HERE/'contract.json').read_text(encoding='utf-8'))
references={k:(ROOT/'reverse/reports/ap01'/v).read_text(encoding='utf-8') for k,v in c['sources'].items()}
# Necessary semantic anchors, recorded with actual line locators for independent review.
need={
 'A49':['copy(O,W,0x664)','a01b2e3a','2e52','2e6e','回调后重读'],
 'A52':['D+14','D+1c','C+c','低31位','status==0'],
 'A57':['0x62fc9744','N+word(0x62fc9740)+4','首个匹配','W+4=D'],
 'A61':['0x62fc9740','0x62fc9744','word4','word0'],
 'A63':['0x62fc974c','e82a','helper先接头发布N'],
 'A65':['0x62fc96fc','D−0x50','4096','0xa00ef468','0xa00ef502','0xa00ef55e','0xa00ef632'],
 'A67':['H=fd+1','0x1b6','H−1','非负结果折0','实际输出','free(H)'],
 'A68_pending':['作者自检待非作者复核','signed32','out_count'],
 'A70_pending':['作者自检待非作者复核','第二次getter','常数0..12']
}
evidence=[]
for key, phrases in need.items():
    for phrase in phrases:
        lines=references[key].splitlines()
        hits=[i+1 for i,line in enumerate(lines) if phrase in line]
        assert hits,(key,phrase)
        evidence.append(dict(source=c['sources'][key],phrase=phrase,line=hits[0]))
checks=[]
def check(label,condition):
    assert condition,label
    checks.append(label)
o=c['objects']; b=c['binding']
check('registered D and separate slot base',int(o['D']['address'],16)-int(o['slot_base']['address'],16)==0x50 and not o['slot_base']['is_cache_buffer'])
check('four actual slots', b['slots']=={'12':'0xa00ef468','16':'0xa00ef502','20':'0xa00ef55e','28':'0xa00ef632'})
check('ordinary init4096 not special sentinel', b['initial_config']==4096 and b['initial_config'] not in (0,0xffffffff))
check('open ABI mode2 and close ABI',b['mode2_open']==['D','pathSuffix',2] and b['close']==['D','H'])
check('value H; D not reader deallocation roots',not o['H']['heap_object'] and not o['H']['freed_by_reader'] and not o['D']['freed_by_reader'])
check('shallow current-state reader copy',o['W']['copied_bytes']==0x664 and not o['W']['stack_pointer_retained_by_O_contract'] and not o['cache_buffer']['copied_by_W_to_O'] and not o['O']['owns_separate_cache_copy'])
check('C versus B and current k',o['C']['bytes_requested']==0x10 and o['C']['prefix_offset']==8 and o['C']['buffer_field']==12 and o['cache_buffer']['allocation_request']=='current k')
check('source and format boundaries',not o['source']['reader_prefix_owns'] and not o['source']['global_retention_proved'] and not b['format_output_proved'])
check('pending protocols excluded',set(c['pending_dependencies'])=={'A68_A69','A70_A71'})
check('composition no new business',c['new_business']==0)
(HERE/'reference-evidence.json').write_text(json.dumps(dict(task='A72',result='PASS',
    reference_anchors=evidence,composition_checks=checks,rom_bytes_read=0,
    method='standard-library reference and semantic consistency checks; not target execution'),ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
print(f'PASS {len(evidence)} located reference anchors; {len(checks)} composition invariants; ROM reads0')
