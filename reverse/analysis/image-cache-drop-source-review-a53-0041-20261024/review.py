"""A53 independent fixed-line source comparison; no ROM or target execution."""
from pathlib import Path
import json
import subprocess

OUT=Path(__file__).resolve().parent
TREE=OUT.parents[2]
prior=json.loads((TREE/'reverse/analysis/image-cache-drop-source-a51-0041-20261024/candidate-excerpts.json').read_text(encoding='utf8'))
root='/home/slepher/nuttx-ap01-sim/apps/graphics/lvgl/lvgl'
spans={'src/misc/cache/lv_cache_lru_rb.c':[(343,406)],'src/misc/lv_rb.c':[(257,291)],'src/misc/lv_ll.c':[(160,179),(294,297)]}
remote='spans='+repr(spans)+'\n'+r'''
import json
from pathlib import Path
root=Path('/home/slepher/nuttx-ap01-sim/apps/graphics/lvgl/lvgl')
out=[]
for rel,ranges in spans.items():
 selected=[]
 with (root/rel).open() as f:
  for n,t in enumerate(f,1):
   if any(a<=n<=b for a,b in ranges):selected.append(dict(line=n,text=t.rstrip('\n')))
   if n==max(b for a,b in ranges):break
 out.append(dict(path=str(root/rel),lines=selected))
print(json.dumps(out))
'''
p=subprocess.run(['wsl','-d','Ubuntu-24.04','--','python3','-c',remote],text=True,capture_output=True,encoding='utf8')
assert p.returncode==0,p.stderr
fresh=json.loads(p.stdout)
old={prior['path']:prior['lines']}
for x in prior['neighbors']:old[x['path']]=[l for s in x['snippets'] for l in s['lines']]
assert len(fresh)==len(old)==3
assert sum(len(x['lines']) for x in fresh)==123
files={}
equality=[]
for x in fresh:
 assert x['lines']==old[x['path']]
 rel=x['path'][len(root)+1:]
 files[rel]={l['line']:l['text'].strip() for l in x['lines']}
 equality.append(dict(path=x['path'],spans=spans[rel],lines=len(x['lines']),equal=True))
b=files['src/misc/cache/lv_cache_lru_rb.c'];r=files['src/misc/lv_rb.c'];l=files['src/misc/lv_ll.c']
checks=[]
def expect(label,mapping,anchors):
 for n,t in anchors.items():assert t in mapping[n],(label,n,t,mapping[n])
 checks.append(dict(label=label,lines=list(anchors),result='PASS'))
expect('drop lookup/miss and third userdata',b,{343:'const void * key, void * user_data',354:'lv_rb_find(&lru->rb, key)',355:'node == NULL',356:'return;',361:'free_cb(data, user_data)'})
expect('cleanup then new measure/subtraction',b,{361:'free_cb(data, user_data)',362:'cache->size -= lru->get_data_size_cb(data)'})
expect('entry/backlink saved before tree removal, then entry/list freeing',b,{364:'lv_cache_entry_get_entry(data, cache->node_size)',365:'*get_lru_node(lru, node)',367:'lv_rb_remove_node',368:'lv_cache_entry_delete',370:'lv_ll_remove',371:'lv_free(lru_node)'})
single='\n'.join(b[n] for n in range(343,373))
assert not any(t in single for t in ['get_ref','invalid','get_victim'])
checks.append(dict(label='complete selected single-drop body has no ref/invalid/victim gate',result='PASS'))
expect('all cleanup only in zero-ref branch',b,{374:'void * user_data',386:'LV_LL_READ',388:'(*node)->data',390:'get_ref(entry) == 0',391:'free_cb(search_key, user_data)',393:'else {'})
expect('per-entry warning/count and summary warning',b,{394:'LV_LOG_WARN',395:'used_cnt++',398:'used_cnt > 0',399:'LV_LOG_WARN'})
expect('unconditional post-loop tree/list destruction and size reset',b,{397:'}',400:'}',402:'lv_rb_destroy',403:'lv_ll_clear',405:'cache->size = 0'})
expect('tree left/right leaf traversal and saved parent',r,{265:'tree->root',269:'node->left != NULL',272:'node->right != NULL',276:'parent = node->parent',278:'parent->left == node',279:'parent->left = NULL',282:'parent->right = NULL'})
expect('tree frees data then node then goes parent, clears root',r,{285:'lv_free(node->data)',286:'lv_free(node)',287:'node = parent',290:'tree->root = NULL'})
treebody='\n'.join(r.values())
assert not any(t in treebody for t in ['get_ref','invalid','free_cb'])
checks.append(dict(label='tree destroy has no entry-ref/invalid/payload-cleanup callback gate',result='PASS'))
expect('list NULL cleanup wrapper',l,{294:'void lv_ll_clear',296:'lv_ll_clear_custom(ll_p, NULL)'})
expect('list save-next then unlink/free only NULL branch, advance saved next',l,{169:'i_next = lv_ll_get_next',170:'cleanup == NULL',171:'lv_ll_remove',172:'lv_free(i)',177:'i = i_next'})
result=dict(status='PASS',baseline='85cf93c',source_files=equality,source_lines=123,checks=checks,
 decision='Accept A51 local source mapping with no semantic correction',new_rom_functions=0,whole_library_exclusions=0,
 inherited=['A46/A48 ROM behavior','A43/A44 candidate identity and known layout limits'],
 limits=['No ROM read/export or producer script execution','No new ZIP/version/upstream identity authentication',
         'Normal valid-object paths only; assertions/log config/ABI/actual consumers remain unverified'])
(OUT/'review-evidence.json').write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n',encoding='utf8')
print(json.dumps(dict(status='PASS',files=3,lines=123,source_contract_checks=len(checks))))
