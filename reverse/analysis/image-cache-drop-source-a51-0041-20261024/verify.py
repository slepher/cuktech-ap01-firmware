"""Validate retained selected source lines and local mapping assertions only."""
import json
from pathlib import Path

HERE = Path(__file__).resolve().parent
evidence = json.loads((HERE/'candidate-excerpts.json').read_text(encoding='utf-8'))
assert evidence['range'] == [343,406]
files = {evidence['path']:evidence['lines']}
for item in evidence['neighbors']:
    files[item['path']] = [line for span in item['snippets'] for line in span['lines']]
assert len(files) == 3
line_maps = {path:{line['line']:line['text'] for line in lines} for path,lines in files.items()}
assert sum(len(lines) for lines in files.values()) == 123

def lines_for(suffix):
    matches = [lines for path,lines in line_maps.items() if path.endswith(suffix)]
    assert len(matches) == 1
    return matches[0]

backend = lines_for('/lv_cache_lru_rb.c')
rb = lines_for('/lv_rb.c')
ll = lines_for('/lv_ll.c')
checks = []

def exact(label, mapping, numbered):
    for number, text in numbered:
        assert mapping[number].strip() == text,(label,number,mapping[number])
    checks.append({'label':label,'lines':[number for number,_ in numbered],'result':'PASS'})

exact('drop signature, lookup and miss return',backend,[
    (343,'static void drop_cb(lv_cache_t * cache, const void * key, void * user_data)'),
    (354,'lv_rb_node_t * node = lv_rb_find(&lru->rb, key);'),
    (355,'if(node == NULL) {'),(356,'return;')])
exact('single drop cleanup then meter then entry/backlink and removal',backend,[
    (359,'void * data = node->data;'),
    (361,'lru->cache.ops.free_cb(data, user_data);'),
    (362,'cache->size -= lru->get_data_size_cb(data);'),
    (364,'lv_cache_entry_t * entry = lv_cache_entry_get_entry(data, cache->node_size);'),
    (365,'void * lru_node = *get_lru_node(lru, node);'),
    (367,'lv_rb_remove_node(&lru->rb, node);'),(368,'lv_cache_entry_delete(entry);'),
    (370,'lv_ll_remove(&lru->ll, lru_node);'),(371,'lv_free(lru_node);')])
single='\n'.join(backend[n] for n in range(343,373))
assert not any(token in single for token in ['get_ref','invalid','get_victim'])
checks.append({'label':'no ref/invalid/victim gate in selected candidate single drop','result':'PASS'})
exact('all signature, traversal, zero ref cleanup and warning count',backend,[
    (374,'static void drop_all_cb(lv_cache_t * cache, void * user_data)'),
    (384,'uint32_t used_cnt = 0;'),(386,'LV_LL_READ(&lru->ll, node) {'),
    (388,'void * search_key = (*node)->data;'),
    (389,'lv_cache_entry_t * entry = lv_cache_entry_get_entry(search_key, cache->node_size);'),
    (390,'if(lv_cache_entry_get_ref(entry) == 0) {'),
    (391,'lru->cache.ops.free_cb(search_key, user_data);'),
    (395,'used_cnt++;'),(398,'if(used_cnt > 0) {')])
assert 'LV_LOG_WARN' in backend[394] and 'LV_LOG_WARN' in backend[399]
exact('all warning branch followed by tree clear then list clear then used reset',backend,[
    (400,'}'),(402,'lv_rb_destroy(&lru->rb);'),
    (403,'lv_ll_clear(&lru->ll);'),(405,'cache->size = 0;')])
exact('tree destroy leaf traversal, parent detach and payload-before-node free',rb,[
    (265,'lv_rb_node_t * node = tree->root;'),(268,'while(node != NULL) {'),
    (269,'if(node->left != NULL) {'),(270,'node = node->left;'),
    (272,'else if(node->right != NULL) {'),(273,'node = node->right;'),
    (276,'parent = node->parent;'),(278,'if(parent->left == node) {'),
    (279,'parent->left = NULL;'),(282,'parent->right = NULL;'),
    (285,'lv_free(node->data);'),(286,'lv_free(node);'),
    (287,'node = parent;'),(290,'tree->root = NULL;')])
exact('clear list NULL cleanup wrapper and save-next/remove/free sequence',ll,[
    (165,'i      = lv_ll_get_head(ll_p);'),(168,'while(i != NULL) {'),
    (169,'i_next = lv_ll_get_next(ll_p, i);'),(170,'if(cleanup == NULL) {'),
    (171,'lv_ll_remove(ll_p, i);'),(172,'lv_free(i);'),
    (177,'i = i_next;'),(294,'void lv_ll_clear(lv_ll_t * ll_p)'),
    (296,'lv_ll_clear_custom(ll_p, NULL);')])
result = {'task':'A51','result':'PASS','files':len(files),'selected_lines':123,
          'checks':checks,'limitations':['Checks validate selected source text, not target execution or ROM bytes.',
          'ROM contracts inherited from A46/A48; no exact build/version/unmodified-source claim.',
          'Neighbor source files use inherited candidate-tree identity, no new package/ZIP authentication.']}
(HERE/'verification.json').write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
print(f'PASS: 3 files, 123 selected lines, {len(checks)} source contract checks; no target execution.')
