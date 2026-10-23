"""Read-only WSL source capture. No candidate import, build or execution."""
import json
import pathlib
import subprocess

ROOT = '/home/slepher/nuttx-ap01-sim/apps/graphics/lvgl/lvgl'
RANGES = {
    'src/misc/cache/lv_image_cache.c': [[54, 68], [106, 145]],
    'src/misc/cache/lv_cache_lru_rb.c': [[59, 68], [111, 123], [150, 177], [216, 237], [267, 288], [304, 313], [329, 341], [416, 425], [441, 449], [458, 462]],
    'src/misc/cache/lv_cache.c': [[48, 65], [104, 117], [299, 329], [332, 347]],
    'src/misc/cache/lv_cache_private.h': [[30, 35], [47, 50], [113, 137], [146, 158], [170, 176]],
    'src/misc/cache/lv_cache_entry.c': [[22, 28], [54, 71], [82, 102], [104, 119], [148, 164]],
    'src/draw/lv_image_decoder_private.h': [[55, 64]],
    'src/draw/lv_image_decoder.h': [[34, 39]],
    'src/misc/lv_rb_private.h': [[27, 39]],
    'src/osal/lv_os.h': [[24, 40]],
}
CHECKS = {
    'src/misc/cache/lv_image_cache.c': ['&lv_cache_class_lru_rb_size', '.create_cb = NULL', 'image_cache_common_compare(lhs->src, lhs->src_type, rhs->src, rhs->src_type)', 'cmp_res > 0 ? 1 : -1', 'if(entry->src_type == LV_IMAGE_SRC_FILE) lv_free((void *)entry->src);'],
    'src/misc/cache/lv_cache_lru_rb.c': ['get_data_size_cb = size_get_data_size_cb', 'lv_ll_ins_head(&lru->ll)', 'lv_memcpy(lru_node, &node, sizeof(void *))', 'lv_memcpy(get_lru_node(lru, node), &lru_node, sizeof(void *))', 'compare_cb(data, key) == 0', 'lv_ll_move_before(&lru->ll, lru_node, head)', 'cache->size += lru->get_data_size_cb(key)', 'cache->size -= lru->get_data_size_cb(data)', 'LV_LL_READ_BACK(&lru->ll, tail)', 'if(lv_cache_entry_get_ref(entry) == 0)', 'return slot->size;'],
    'src/misc/cache/lv_cache.c': ['lv_cache_entry_get_ref(entry) == 0 && lv_cache_entry_is_invalid(entry)', 'cache->ops.free_cb(lv_cache_entry_get_data(victim), user_data);'],
    'src/misc/cache/lv_cache_entry.c': ['int32_t ref_cnt;', 'return (uint8_t *)entry - entry->node_size;'],
    'src/misc/cache/lv_cache_private.h': ['typedef int8_t lv_cache_compare_res_t;', 'size_t size;'],
}
remote = '''import json,pathlib,zipfile
root=pathlib.Path(%r)
ranges=%r
checks=%r
out={'root':str(root),'identity':'Inherited F07/F08, not a new version or provenance certification','files':[],'assertions':0}
with zipfile.ZipFile(root.parent/'v9.2.1.zip') as package:
 for rel,spans in ranges.items():
  data=(root/rel).read_bytes()
  lines=data.decode().splitlines()
  for token in checks.get(rel,[]):
   assert token in data.decode(), (rel,token)
   out['assertions']+=1
  out['files'].append({'path':str(root/rel),'package_member':'lvgl-9.2.1/'+rel,'local_member_equal':data==package.read('lvgl-9.2.1/'+rel),'snippets':[{'start':a,'end':b,'lines':[{'line':i,'text':lines[i-1]} for i in range(a,b+1)]} for a,b in spans]})
print(json.dumps(out,ensure_ascii=False,indent=2))
''' % (ROOT, RANGES, CHECKS)
result = subprocess.run(['wsl.exe', '-d', 'Ubuntu-24.04', '--', 'python3', '-c', remote], capture_output=True, check=True)
evidence = json.loads(result.stdout.decode('utf-8'))
assert all(item['local_member_equal'] for item in evidence['files'])
pathlib.Path(__file__).with_name('candidate-evidence.json').write_text(json.dumps(evidence, ensure_ascii=False, indent=2)+'\n', encoding='utf-8')
print(f"PASS: {len(evidence['files'])} local members equal; {evidence['assertions']} source-token checks; selected lines only")
