"""Independent A73 document anchors only. No ROM, author code or model execution."""
import json
from pathlib import Path

MAIN = Path('D:/Documents/PlatformIO/Projects/cuktech-ap01-firmware')
REPORTS = MAIN / 'reverse/reports/ap01'
HERE = Path(__file__).parent
anchors = {
 'reader-driver-lifetime-a72-0041-20261024.md': [
   'source分类1、选择器确实首匹配', '当前配置不是0xffffffff', 'generic层**不拿callback返回值作清理门**',
   '低31位掩码与总实际消费word不能混成', '默认五ROM照片仍沿已验**mode0**',
   '实际输出/截断/NUL及路径解析未证'],
 'photo-reader-mode-review-a49-0041-20261024.md': [
   'd798 SW W+4=D', 'd7bc将结果写W+8', '2e52重读O+4', '2e6e重读O+8',
   '入口两个空门跳过', '返回值没有用于后继门'],
 'photo-reader-consumer-review-a52-0041-20261024.md': [
   'count/filled/out_count均32位独立通道', '不能把跨缓存copy的`&7fffffff`改写成纯min',
   'ba66重新LW C', '浅复制不复制B数据', '返回未用于这里后续read门'],
 'reader-driver-selection-review-a57-0041-20261024.md': [
   '首个匹配才进入可选D+8回调门', '动态 `N+word(0x62fc9740)+4`'],
 'reader-driver-register-review-a63-0041-20261024.md': [
   'helper先接头发布N，caller随后才填N.word0=D'],
 'reader-driver-slot-review-a65-0041-20261024.md': [
   'B=G+0x180=0x62fc96fc=D−0x50', 'D+4为4096',
   '0xa00ef468/0xa00ef502/0xa00ef55e/0xa00ef632'],
 'reader-driver-open-close-review-a67-0041-20261024.md': [
   'H=fd+1', 'callback没有独立H对象或free(H)路径', '非负结果折0', '不检查format返回'],
 'photo-decoder-review-a39-0041-20261024.md': [
   'copy(O,W,0x664)', '不是保存 W 地址', '保存的是 O 与 O 内部区域的32位指针值'],
 'photo-destroy-review-a42-0041-20261024.md': [
   'mode0 直接归还整个 O', '清 owner+0x5c、owner+0x74']
}
found=[]
for name, snippets in anchors.items():
    lines=(REPORTS/name).read_text(encoding='utf-8').splitlines()
    for snippet in snippets:
        matches=[i+1 for i,line in enumerate(lines) if snippet in line]
        assert matches,(name,snippet)
        found.append({'file':'reverse/reports/ap01/'+name,'needle':snippet,'lines':matches})

def load(relative):
    return json.loads((MAIN/'reverse/analysis'/relative/'contract.json').read_text(encoding='utf-8'))

author=load('reader-driver-lifetime-a72-0041-20261024')
read=load('reader-driver-read-seek-review-a69-0041-20261024')
mapper=load('reader-driver-result-map-review-a71-0041-20261024')
checks={
 'source_condition': any('actual first matching node' in v for v in author['preconditions']),
 'mutable_fields': any('no blanket immutability' in v for v in author['preconditions']),
 'D': author['objects']['D']['address']=='0x62fc974c' and not author['objects']['D']['freed_by_reader'],
 'slot_not_buffer': author['objects']['slot_base']['relation']=='D-0x50' and not author['objects']['slot_base']['is_cache_buffer'],
 'H_not_heap': not author['objects']['H']['heap_object'] and not author['objects']['H']['freed_by_reader'],
 'copy_not_B': author['objects']['W']['copied_bytes']==0x664 and not author['objects']['cache_buffer']['copied_by_W_to_O'],
 'config_domains': 'k != 0xffffffff' in author['ordinary_config_domain'] and 'not substituted' in author['ordinary_config_domain'],
 'count_boundaries': len(author['count_boundaries'])==4 and any('low31' in v for v in author['count_boundaries']),
 'A69_latest': read['decision']=='limited acceptance of A68' and any('including0' in v for v in read['read']),
 'A71_latest': mapper['review']=='independently-limited-accepted-A70' and mapper['static_pairs_decimal']['0']==0,
 'no_output_or_delete_closure': not author['binding']['format_output_proved'] and 'final DELETE' in author['not_proved'],
 'new_business_zero': author['new_business']==0
}
assert all(checks.values()),checks
out={'task':'A73','rom_bytes_read':0,'executed_author_scripts':False,
     'method':'document anchors plus contract consistency; semantic order manually reviewed',
     'anchor_count':len(found),'consistency_count':len(checks),'anchors':found,'checks':checks,
     'status_refresh':{'A69':'limited accepted A68','A71':'limited accepted A70; zero input returns zero'},
     'semantic_corrections':0,'new_business':0}
(HERE/'reference-evidence.json').write_text(json.dumps(out,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
print(f'PASS {len(found)} source anchors + {len(checks)} contract consistency checks; ROM0B')
