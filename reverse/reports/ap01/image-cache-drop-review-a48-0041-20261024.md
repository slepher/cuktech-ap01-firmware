# A48：默认 image-cache drop / drop_all 独立复核

**限定接受 A46：同 backend 的 +18/+1c 槽、NULL source→同 image-cache drop_all 接线、单 drop 清理原序，以及 drop_all 的零引用 cleanup 门与随后全部树/链释放均成立。语义纠正0，新增功能0。** 非零引用 warning 分支仍汇回遍历，再进入同一树清理；不补成 invalid/延迟回收协议，不据此推断实际发生过有引用条目的 all-key 清理或缺陷。

2026-10-24；基线 `df35f44`，独立树 `re0041-a48`、分支 `codex/re-0041-a48`。复核者未参与 A46 生产。采用 reverse-engineer-anything 技能，只读主仓 ROM 和既有报告/证据，未打开或切换共享 REA target/database，未运行模型、固件、SIM、构建、历史回放、设备或外网。仅写本报告和独占同名 analysis，不改主树共享、ROM、生产代码、配置、模型，不创建下级 agent，不撤销其他任务改动。函数/字段名称是分析映射；伪代码不是原源码。

## 继承结论：已有 → 行为 → 局限 → 实际缺口

| 已有出处 | 已有行为与证据层次 | 本轮处理/实际缺口 |
| --- | --- | --- |
| [A46](image-cache-drop-a46-0041-20261024.md)及其 `evidence.json` | 已恢复真实 drop/drop_all 槽、NULL-source正常入口、cleanup与容器释放责任；作者自检不是独立验收 | 独立稀疏原字检查，不运行其 verify.py，不把其 JSON 当本轮原件 |
| [A27](image-cache-cleanup-a27-0041-20261023.md)/A28，A23/A24 | 十word表、G+11c image-cache身份、cache+18 payload cleanup、entry偏移/ref/invalid、cleanup后payload基址释放 | 可靠原字合同直接继承；只复核两个槽，不重建表或PNG/heap，不把通用 `a019cfbe` 改名 backend 回调 |
| [A34](image-cache-order-a34-0041-20261024.md)/A36，A30/A32 | +30链接偏移4、+34头/+38尾、OrderNode.word0→TreeNode.word10→payload、尾backlink；unlink不释放，调用者free节点；计量首word | 结构/链helper内部和计量单位继承；本题只核新入口中调用与重读原序，不重做平衡树 |
| [A38](image-cache-key-a38-0041-20261024.md)/A40 | key source/class与默认比较器、树/头比较方向及零判命中 | 继承；NULL source的正常入口避开key构造，不是把NULL当key送比较器 |
| [A43](image-cache-source-a43-0041-20261024.md)/[A44](image-cache-source-review-a44-0041-20261024.md) | 本地LVGL候选的class声明和部分合同相符；明确drop/drop_all body未认证；精确ROM版本未知 | 不用候选代替ROM，不重复其9文件/ZIP读取；本题仅复核A46新增ROM接线 |
| A27/A34/A38的旧complete、最终验收、ZIP复用边界；本轮 `reverse/reports/ap01` 下 `*complete*.md`/`*final*.md` 有界文本查询 | 既有服务/SIM/照片是替代重建，不证明ROM ABI；本轮四词 `a00ebf7c/a00ec084/a019cf58/lv_cache` 无命中 | 不重复ZIP导出，不以无命中声称从未分析；旧whole-ROM extent只定位，不能作body语义或来源认证 |

本题缺口仅为 A46 正常有效对象路径的独立技术接受。证据分层保持：已复核原字合同直接引用；旧反编译/地址清单只定位；SIM/照片/安全替代不证明ROM；未有真实消费者/xref种子的边继续未知。

## 本轮复核或纠正：逐项接受

原件为主仓 `roms/0041/ap01-1.0.2_0041.bin`，映射 `offset=VA-0x9ffff000`。本路 [review.py](../../analysis/image-cache-drop-review-a48-0041-20261024/review.py) 独立稀疏读取原件，提取调用目标、标准/压缩分支位移、word访存字段；结果 [review.json](../../analysis/image-cache-drop-review-a48-0041-20261024/review.json) 只保留必要锚点，不重导完整函数或原表，不虚构新REA Evidence ID。

| A46主张 | 独立原字与控制锚点 | 判定/限定范围 |
| --- | --- | --- |
| 同backend +18/+1c | 只读 `a0263afc+18/+1c` 两word，分别为 `a00ebf7c/a00ec084` | **接受**安装身份；cache+18是对象的cleanup指针，table+18才是backend drop槽，两层不能混淆 |
| NULL source到同image-cache all-key | `90f6/fa`构造G=`62fc957c`，`90fe`读G+120；`9102:1de1` 为source非零→9128。零时`9104/06`以另一cache调用`a019cf58`，`910e:03a5c411`读G+11c，再`9112/16`到同helper | **接受**原API显式零source分支；第二槽G+11c身份继承A23。第一cache内部不外推，同次业务实际传NULL未知 |
| generic all-key派发ABI | `cfac:1c41`读cache首word表；`cfae:8145` a1=0；`cfb0:dc4f`读table+1c；`cfb2:8297`调用a5 | **接受** `(cache,0)`→backend drop_all。`a019cfbe`属于另一个通用失效层，未被这条链调用 |
| 单drop查找、命中门和cleanup参数 | `c00c/c010`保存cache及tree=cache+24；`c014/c024`保存/恢复第三实参；`c018`→`a00ea832`；`c01e:31c9` NULL结果→c072返回；`c020`读tree.word10→s2；`c028..2e`调用cache+18 `(payload,原第三参)` | **接受** miss直接退出，hit先cleanup。查找/比较内部继承，不为返回寄存器补造布尔结果 |
| 单drop重新计量与释放顺序 | `c030/c034`在cleanup后重读cache+3c并调；`c036/38/3a`读used、word减法、写回；`c03c/c048`算entry，`c04a/c052/c054`重读payload取backlink；`c058`→tree_remove，`c05e`→entry destroy，`c068`→unlink，`c06e`→free OrderNode | **接受** cleanup→measure/扣量→树移除→payload基址free→摘链→free链节点。没有以release/ref/invalid或victim协议替换单drop的直达路径；实际上层有效调用协议未认证 |
| drop_all遍历对象和零引用cleanup门 | `c0e0`头→s2，`c0e6`保存userdata→s5，`c0e8` list=cache+30；`c158/c15c`两级取payload→s9；`c160/c16a/c16c`算entry；`c172`→`a008b604`；`c17a:11e9` ref非零→c18e；零分支`c17c..182`为cache+18 `(payload,原第二参)` | **接受**零ref才payload cleanup，userdata不是强制0。ref读取和entry内部合同继承；遍历阶段不因此成为逐entry delete |
| 非零引用warning与整树释放汇合 | `c1a2`→warning helper，`c1a6`计数+1，`c1a8:f1bf`→c184；共同next由`c184/186/188`取得，`c18c:bdb7`→c0fa。`c0fa`非空→c158；空时`c0fe`无warning→c126，另一支`c122` warning调用后也顺落c126 | **接受**正常调用返回后的静态原序：两种ref分支均结束于同一树清理入口，未把有引用payload排除。诊断helper内部及真实运行时ref状态未核 |
| 全树释放和清链/清计量责任 | `c126`读cache+24根；`c12a/c12c`非空→c1aa；`c1aa/c1b0/c1b8`读left/right/parent；`c1c8`或`c1dc`断父边；`c1cc`读node.word10，`c1d0`free payload，`c1d4/c1d6`free node；`c1da`回父遍历。根空后`c130`写root0，`c134/136`以cache+30调清链，`c13a`写used0 | **接受**第二阶段不再按ref筛payload，不调用entry destroy；处理完所有树节点后才清链和used。只核整树拆除所需边，不认证完整树平衡或任意结构 |
| 清链不重复访问已free树对象 | `a008ae4a/4c`以a1=0进`a008adf4`；`ae04/06/08`保存head/list/callback0；`ae1c/20/22`先从链偏移取next至s4；`ae26`因callback0不取非零分支；`ae2e`unlink、`ae32/34`free当前链节点，`ae38/3a`用保存next继续 | **接受**只清OrderNode，不再用其word0解引用TreeNode或重复cleanup payload；head/tail归零沿A34的unlink端点合同。allocator和可选非零callback分支不展开 |

以上9项限定接受，语义纠正0。单drop的cleanup第三实参和drop_all的第二实参均被保存/传递；从NULL-source调用点得到的0只属于该接入，不能推广所有backend调用。返回类型/状态未认证。局部正常合同可表示为下列伪代码，**非原源码**：

```c
// A46已有结构/原序；省略assert/diagnostic内部，不改正常路径。
single_drop(cache, key, userdata):
    tree = find(cache + 0x24, key);
    if (tree == NULL) return;
    payload = tree->word10;
    cache->cleanup(payload, userdata);
    cache->used_word -= cache->measure(payload); // callback在cleanup后重读
    entry = payload + cache->entry_offset;
    order = backlink(tree->word10, cache->tree_payload_size);
    tree_remove(cache + 0x24, tree);
    destroy_entry(entry); // 继承：重算payload基址并free
    unlink(cache + 0x30, order); free(order);

drop_all(cache, userdata):
    for (order = cache->head; order != NULL; order = next(order)) {
        payload = order->tree->word10;
        if (entry_ref(payload + cache->entry_offset) == 0)
            cache->cleanup(payload, userdata);
        else warning_and_count();
    }
    if (warning_count != 0) warning();
    dismantle_all_tree_nodes_freeing_payload_then_node(); // 不再按ref筛选
    cache->root = NULL;
    clear_order_list_with_null_callback();
    cache->used_word = 0;
```

所有权沿A23/A27继承：image cleanup只处理owned pixel/source资源，不free payload分配。单drop经entry destroy释放payload；drop_all的树阶段直接释放payload/TreeNode，链阶段另释放OrderNode。没有新增cache对象或表/capacity的释放/重建。对非零ref而言，当前静态路径未cleanup其资源，但仍进入容器分配释放；这仅描述指令，不认证外部正常引用前置条件，更不报告运行时缺陷。

## 真正新增与实际验证

**新增ROM功能0、ISA规则0、完整函数导出0、来源排除0；新增交付只有独立复核证据和限定接受。** A27/A34/A38/helper、A43/A44候选对应均为继承，不重计成果。本轮没有新厂商指令；未以候选源码替换原字或修正原行为。

运行 `python -X utf8 -B reverse/analysis/image-cache-drop-review-a48-0041-20261024/review.py`：PASS，97条稀疏指令、16个独立调用目标、17个独立控制边、23条word访存字段及两个旧表槽。另补检查 `c0fa/c0fe/c122` 的遍历结束汇合边，未重导诊断正文；脚本不导入A46脚本、不执行目标或输入实验。JSON解析、报告相对链接和 `git diff --check` 通过。

## 未闭精确边与一个后续闭包

仍未知：table+18的真实ROM上层正常消费者/调用协议；业务层何时把NULL source传给`a00890e8`及all-key调用时引用状态的外部保证；动态backend/callback/链接偏移重配、同步、完整heap/树平衡；诊断helper内部、原C返回类型及精确LVGL版本/构建来源。A46正常静态body的接受不等于发生过实际释放、图像解码或页面事件。

一个经过重叠检查的后续建议：只认证本题新闭ROM drop/drop_all与本地候选 `src/misc/cache/lv_cache_lru_rb.c` 的 `drop_cb/drop_all_cb` 局部对应。实际种子是A43 `candidate-evidence.json` 已留class初始化111..123行（两个槽名称）和本题两个确定ROM目标；A43/A44明确未认证其body，A46又明确新增行为以ROM为据、候选读取曾受E_ACCESSDENIED，因此尚非重复认证。保持候选局部合同等级，不再恢复key/计量/LRU/cleanup，不扩版本/整库，不修环境。table+18消费者尚无新xref种子，不为凑题扩扫。由管理者决定后继，本轮结束。
