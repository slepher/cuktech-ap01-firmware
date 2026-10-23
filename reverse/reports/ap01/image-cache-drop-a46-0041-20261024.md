# A46：默认 image-cache backend 的 drop / drop_all

2026-10-24；基线 `e2991b9`，分支 `codex/re-0041-a46`。默认 backend 的真实 `+18=a00ebf7c` 是按 key 直接 drop，`+1c=a00ec084` 是 drop_all；通用 `a019cfbe` 仍是另一个失效层，不改名为 backend drop。**正常 source=NULL 的 `a00890e8` 确实接到 image-cache drop_all。drop_all 只对零引用 entry 调 payload cleanup，却随后释放全部树 payload/node；非零引用分支只作 warning，未标 invalid，也未延迟这些分配的释放。** 这是原静态行为，不以 A27 的指定 key 失效协议替换。

应用 [reverse-engineer-anything skill](C:/Users/cogic/.agents/skills/reverse-engineer-anything/SKILL.md)；无共享 REA target/database，无执行固件、SIM、构建、历史回放、设备或网络。仅独占报告/analysis 写入。函数名、结构名及伪代码是分析映射，不是原源码。

## 继承结论：已有→行为→局限→实际缺口

|已有出处|已知行为与证据|局限及本轮处理|
|---|---|---|
|[A27](image-cache-cleanup-a27-0041-20261023.md)/A28；其 evidence.json 的 backend_table|完整 a0263afc 十 word 表，entry→payload、引用/header、invalid门及cleanup/free|复用原表，不重建表；只核+18/+1c两个实际槽和body|
|[A29](image-cache-invalidation-a29-0041-20261024.md)/A31|a00890e8 非NULL source→双cache各自key→a019cfbe；明确留下NULL source→a019cf58|只展开已定位NULL正常分支；G+120另一cache内部不展开|
|[A30](image-cache-accounting-a30-0041-20261024.md)/A32、[A34](image-cache-order-a34-0041-20261024.md)/A36、[A38](image-cache-key-a38-0041-20261024.md)/A40|计量首word、树/链/backlink、比较器、remove与零ref victim均已有原字节及独立复核|直接继承，drop上的调用顺序另核；不扩树平衡/所有cache/异常重复操作|
|[A43](image-cache-source-a43-0041-20261024.md)/[A44](image-cache-source-review-a44-0041-20261024.md)|class十槽及局部LVGL候选来源相符；明确drop/drop_all body未认证|不拿候选源码代替ROM；只补实际正常路径，版本仍未知|
|whole-rom-coverage-0041-20261023-round1.json|ebf7c extent ev_9639717bcd26ac42910d1e595e98f18f708d892661c385c0d245bede3b8bdc88；ec084 extent ev_47f2f0b831fa75ff139c8a6294cd5f964a85d181fe849811e6e57c3444aff88c；cf58 extent ev_8fbc8fd71a9fee20be41e5a17b59bf042e718d1f05483ecd749fdab9844c681f|旧body/地址清单只定位，不当语义或来源证明；其body包含assert/diagnostic，本轮只留必要窗口|

旧complete/ZIP/SIM查询边界沿A27/A34/A38继承，不重复导出或声称此前从未分析。四种证据层次分开：已复核原字节合同直接继承；旧反编译/地址清单仅作定位；SIM/照片/安全替代不证明ROM ABI；本轮真正缺口仅上列两个槽及正常all-key连接。

## 本轮复核或纠正

旧十word表未变；只对+18/+1c两word与既有留存值交叉检查。A29已明确NULL源分支，本轮属于展开其断边，不纠正非NULL合同。A27的release/指定key失效/victim、A34的链和A38的key语义均不重做、不改写。A43/A44未认证body，不能据候选名反推出下面的ref行为。

单drop没有A27通用失效的引用/invalid门；drop_all的非零ref不走通用失效的“标记→移出→最后release”路径。这是不同入口的事实，不是旧报告错误。

## 真正新增：接入、状态及所有权

### 正常all-key API连接

`a00890e8(source)` 的 `a00890f6/fa` 形成 G=`62fc957c`，`90fe` 读G+120；`9102 1de1` 是source非零跳往`9128`。source为0时：

```text
9104 a0=load32(G+120) → 9106 AUIPC/JALR a019cf58
910e a0=load32(G+11c) → 9112 AUIPC/JALR a019cf58 → 返回
```

第二个cache槽=`62fc9698`，与A23 image-cache创建身份相同。第一个仍是另一cache，不套本默认backend结论。`a019cf58` 正常非NULL cache 尾部 `cfac..cfb2` 为 `table=load32(cache); a1=0; fn=load32(table+1c); fn(cache,0)`。故NULL source是原API显式支持的all-key选择，**不能新增source非NULL门**。它不是向key比较器传NULL；NULL源直接避开key构造/lookup。此连接证明静态可达，不证明某次页面操作实际传入NULL或缓存条目当时有引用。

`a019cfbe` 正常入口通过table+0c get，随后按ref选remove/invalid路径，继承A27。它没有调用table+18。本轮有界检查已知lv_cache.c来源函数清单及A29 caller种子，未认证任何normal通用API对table+18的实际派发；因此不能伪造一条“a019cfbe→backend drop”。真实+18的安装身份和正常函数体已闭，其上层实际消费者保留断边。

### 单key backend drop：a00ebf7c(cache,key,user_data)

正常有效参数段 `c00c..c072`：s5=cache+24，保存user_data，`c018→a00ea832(cache+24,key)`查树，返回NULL直接结束。命中后顺序为：

```c
// 结构化伪代码；忽略assert诊断，仅保留正常命中原序。
payload = tree_node->word10;
cache->cleanup(payload, user_data);           // c028..c02e，cache+18
amount = cache->measure(payload);            // c030..c034，cache+3c，cleanup之后重读
cache->used_word -= amount;                  // c036..c03a，RV32 word
entry = payload + load32(cache+4);
order = load32(tree_node->word10 + load32(cache+2c) - 4);
tree_remove(cache+24, tree_node);             // c058 a00ea9a6；内部沿既有合同
destroy_entry(entry);                        // c05e a008b6a6→payload基址free
unlink(cache+30, order);                     // c068 a0089d02
free(order);                                // c06e a008ab8a
```

它不查询entry ref、不读/写invalid、不调用backend+14，也不走victim选择。cleanup调用第2参来自本函数第3参；不能把所有接口userdata归为0。函数正常末端恢复寄存器返回，没有布尔命中状态的认证；查找未命中没有cleanup/计量/移出。对命中路径也不凭这段函数推定正常调用者允许任意有引用条目或重复drop；调用协议正是待闭边。

cleanup先于measure与树移出，与A27通用失效的先remove后cleanup不同。计量和树/链helper本体直接继承；本题只恢复这个新入口的真实原序。A23 cleanup只清owned pixel/source，不释放payload；payload基址仍在destroy_entry释放，链节点另free。

### drop_all：a00ec084(cache,user_data)

`c0e0` s2=head(cache+34)，s5=user_data，s4=cache+30。循环从头向尾，经 `order.word0→tree.word10` 得payload，加cache+4得到entry；`c172→a008b604(entry)`读ref。`c17a 11e9` ref非零跳`c18e`，后者调用warning `a008b51a`并增加本地计数，随后与零ref分支合流到`c184`。ref==0才在`c17c..c182` 调cache+18 `(payload,user_data)`；两分支均按 `*(order+load32(cache+30)+4)` 取next。

没有SB invalid写入，没有backend+14移出，没有逐项used扣减，也没有将有引用payload从后续树清理排除。遍历结束后，非零ref计数仅参与warning，随后仍进入`c126`树清理（warning正文不展开）。

第二阶段从cache+24树根开始，只为正常整树拆除而向left(+4)/right(+8)下行；无孩子时断开父节点(+0)对应的left/right边，`c1cc..c1d6`依次 `free(node->word10)`、`free(node)`，回到父节点，直到根处理完。此处直接free payload，**不是a008b6a6，也不按ref再次筛选**。这段不是完整树算法恢复，不展开平衡/旋转。

最后 `c130` 写root=0；`c136→a008ae42(cache+30)` 清双链；`c13a` 写used_word=0。必要链清理适配器 `a008ae42→a008adf4(list,0)` 先保存next，再调用既有unlink，最后free当前OrderNode；不再解引用node.word0的已释放TreeNode，不重复cleanup/free payload。head/tail归零由既有unlink端点合同继承。cache对象本身、backend表和capacity不在此路径释放/重建。

因此本入口的责任分为：零ref才payload资源cleanup；所有树payload和TreeNode均被拆除释放；所有OrderNode被清除释放；used最终清0。有引用分支没有cleanup但仍发生容器分配释放，不能补成invalid延迟回收，也不能从静态路径推断实际调用时存在有引用条目。它没有受认证的状态/数量返回值。

## 未闭精确边、恢复等级与验证

- 继承结论：release/指定key失效/victim、key比较、计量单位、backlink/链方向和payload清理责任均沿既有已复核合同。
- 本轮复核/纠正：只核两个旧表槽身份，旧语义纠正0；原API NULL源分支展开，不是异常输入研究。
- 真正新增：正常all-key到同image-cache +1c连接、两backend body的清理/引用/计量/树链责任。事实依据原字节；drop/drop_all符号名是已知表次序与行为映射的推断。新增开源未改排除0，精确LVGL版本仍未知。
- 未闭精确边：table+18在ROM的正常通用API消费者/上层业务协议尚未认证；NULL source在实际应用时何时发生及正常all-key调用的外部引用前置条件未知。不同cache、动态重配、完整同步/树平衡/heap、诊断和任意重复输入均未展开。不能借ROM静态可达声称真实运行命中或free时序已观测。

唯一后续闭包：新独立agent复核+18/+1c层级、all-key正常连接、非零ref warning后仍进入全树释放、cleanup在单drop中的原序；若另追功能，仅追table+18真实正常消费者，不重复A27/A34/A38。

独占 [verify.py](../../analysis/image-cache-drop-a46-0041-20261024/verify.py) 对主仓只读ROM使用`offset=VA-0x9ffff000`：12个必要窗口、372 B、128条指令、46项原编码/分支/目标/槽断言通过；无厂商未知字。字节及指令保存在 [evidence.json](../../analysis/image-cache-drop-a46-0041-20261024/evidence.json)。不重导完整函数或原十word表。一次本地候选源WSL只读访问受E_ACCESSDENIED阻止；未尝试修环境或网络，报告所有新增行为均以ROM为据，不依赖该读取。交付另检查JSON解析、报告相对链接和git diff --check。作者静态自检不冒称独立技术验收。
