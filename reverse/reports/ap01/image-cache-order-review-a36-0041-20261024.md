# A36：默认 image-cache 顺序合同独立复核

2026-10-24；基线 `f17c7d7`，分支 `codex/re-0041-a36`。限定接受 A34 的双链字段、成功插入接头、非头查询命中提升及尾部零引用 victim 优先级；未发现需要推翻的语义。补清 helper 间重读和返回端重读的表达精度。新增功能恢复为0，不由函数名或候选源码认定全库 LRU。

使用 [reverse-engineer-anything](C:/Users/cogic/.agents/skills/reverse-engineer-anything/SKILL.md) 的既有证据优先流程。只读主仓 ROM 与留存证据，未打开或改变共享 REA target/database；无 SIM、构建、历史回放、固件执行、设备、网络。只写本独占报告及 analysis，未改主树共享文件、生产代码、ROM、配置或模型，未创建下级 agent。

## 继承结论与实际缺口

|既有出处|已解释行为|局限|本轮处理|
|---|---|---|---|
|[A23](png-session-lifecycle-a23-0041-20261023.md)/A24、A25/A26|image cache 接入、session/Pixel/source 所有权及默认析构|不认证链顺序|直接继承，不重导 PNG、像素和资源|
|[A27](image-cache-cleanup-a27-0041-20261023.md)/[A28](image-cache-review-a28-0041-20261024.md)|后端表身份、entry/payload 适配、引用门、release/失效、victim/cleanup/free 原序|当时未恢复链的生产与方向|直接继承容量和清理，只核排序接合点|
|[A30](image-cache-accounting-a30-0041-20261024.md)/[A32](image-cache-accounting-review-a32-0041-20261024.md)|默认初始化、计量槽、首 word 单位、成功加减及重读|不能据此推出链方向|只重核 +30=4、两端清零，不重做计量|
|[A34](image-cache-order-a34-0041-20261024.md)及其 [evidence.json](../../analysis/image-cache-order-a34-0041-20261024/evidence.json)|局部原指令、调用 ABI、链与 backlink 连接、命中提升|研究者自检，待独立复核|本轮唯一技术认证对象|
|A34 [reuse.json](../../analysis/image-cache-order-a34-0041-20261024/reuse.json)，whole-ROM `ev_aff990cb7bf27ac690be8055d08c6b2a8bbb8931c7236669445b04e0d47a417e` / `ev_7b5ea907fa01a5214b7addd303649e19f77bde8d35fe27942a3573bbc3fd1f5d`|旧完整材料、pass3、较晚 round3 与 ZIP 查询边界；函数范围/调用索引早已存在|地址元数据不是顺序合同，精确 token 无命中不证明此前未分析|继承查询，不重新扫描 ZIP 或复制完整函数|

四类证据分开使用：旧原字节合同直接引用；旧反编译/范围与 no-return 元数据只供定位；SIM/照片替代不认证 ROM；本轮只读原字节是旧结论复核。实际缺口是 A34 新增链方向及操作 ABI 的独立核验，不是尚未恢复整个 cache。

## 本轮复核或纠正

|A34 主张|处置|原指令与接受边界|
|---|---|---|
|cache+30=4 是节点内链接偏移，+34/+38 为头/尾|接受|`a00f0dec/0dee` LI4、SW+30；`0df8/0dfc` 清+34/+38。`a0089ce2/ce4` 以 descriptor.word0 作 indexed store 偏移；`9cf6/cf8/cfa` 读同偏移、ADD 后写+4。第一参 cache+30，所以 descriptor+4/+8 对应 cache+34/+38；4 不是时间、分数或引用数。|
|OrderNode+0→TreeNode，+4 prev、+8 next；payload 尾 backlink 指向 OrderNode|接受|`a00ebe5c..be7a` 两次4B copy，第一源为保存 TreeNode 的栈槽、目的承接新节点；第二目的为 tree+10 payload 加 cache+2c−4，源为保存新节点的栈槽。lookup `ba98..baa4` 与移出 `bf40..bf48` 读取同 backlink；victim `ec252/256` 先 node.word0 再 tree.word10，不能把链节点当 entry/header。|
|成功新插入接头，空链同时写尾|接受，补重读精度|`a008aecc/aece/aed0` 保存 descriptor、按 offset+8 分配；`aed6/d8` 保存新节点并检查非NULL。`aee0` set_prev(new,NULL)，`aee4` 读 head 后 `aeea` set_next(new,head)，`aeee` **再次读 head**，非NULL才 `aef6` set_prev(head,new)。`aefa` 读 tail，`aefc` 写 head，旧 tail 为NULL才 `af02` 写 tail。A34 的 old_head 伪变量仅在正常合法链解释下适用，不能代替这两次原读取。|
|a00eb9c0 头命中不改链、未命中不写链、非头命中提升到头|接受|backend+0c 原值 a00eb9c0。`ba54..ba96` 从头候选 tree+10 取 payload，cache+10 comparator 返回0即返回；否则 `ba60` 调 a00ea832(cache+24,key)，NULL 分支直接返回。命中用 backlink 得 s3，重读 head 到 s5，`baa8` 已在头则绕过重接。`bab4` 读取 prev(head) 到 s6；合法非空链该值为NULL，`bab8` 另保留 hit==s6 门。`bac4` unlink 后，`bace/bad8/bae2/baec` 依次 set_next(s6,hit)、set_prev(hit,s6)、set_prev(s5,hit)、set_next(hit,s5)，再条件写 tail/head。由正常 s6=NULL 得出提升至头，不是仅前进一格。|
|提升保留节点，不释放；移出先 unlink 再 free 链节点|接受|a0089d02 的头/尾分支更新端点，中间分支 `9d60` set_next(prev,next)，`9d64` 重读保存 prev，`9d6e` set_prev(next,prev)，不调用 free。命中只调用 unlink 与 setter；移出 `bf56` 调 unlink，`bf5a/5c` 才传原链节点给 a008ab8a。后续计量和 payload cleanup 全继承 A27/A30，不把链节点释放混为 Pixel 或 payload 析构。|
|victim 从尾沿 prev 跳过非零 ref|接受继承门后的方向连接|`ec236` 取 cache+38；`ec252/256/258` node→tree→payload 并取 cache+4 适配 entry。`ec266` 调既有 getter a008b604，零分支返回 entry；非零才 `ec26c` 重读 +30，`ec270` indexed load 更新 node，回到节点门。因 +30=4，该读取就是 prev；跳过不写链接。引用门内部及后续清理不重导。|
|厂商 indexed load/store 无额外基址写回|接受既有模型语义并独立核字段|独立解 `9ce4 0bd6f540`、`9d3a 8bc5e540`、`bab4 0bcbfa40`、`ec270 0b49f940` 的 opcode/f3/top5/rd/rs1/rs2/shift；均为 shift0 的 word 操作。有效地址解释继承 A34 已留存只读模型的 th.lrw/th.srw 规则。ec270 的 rd/base 均s2，加载值替换s2，不附加自增；未改模型，也未另做 ISA 来源认证。|
|可据此认证全部 cache、所有 API、完整树与库版本|未核，不接受外推|只认证该默认实例正常 lookup/insert/remove/victim 链；动态重配、完整树平衡、并发与全部调用者协议不在范围。A34 本来就保留这些边界。|

没有语义纠正。除插入 helper 的两次 head 读取外，lookup 返回端 `a00ebb00` **重新读取 TreeNode+10**，`bb02` **重新读取 cache+4** 后才相加；不能将 A34 末行 return 理解成复用 comparator 前或 unlink 前缓存的 payload/header 值。空头回退 `bb0c` 与端点条件仍按 A34 留存，不为异常对象添加行为保证。

以下为正常合法链的解释性伪代码，不是原源码；保留可观察读取顺序，不补未核分支：

```c
// list=cache+0x30, offset=load32(list)=4
set_prev(list, new_node, NULL);
set_next(list, new_node, load32(list+4));
old_head_again = load32(list+4);
if (old_head_again) set_prev(list, old_head_again, new_node);
old_tail = load32(list+8);
store32(list+4, new_node);
if (!old_tail) store32(list+8, new_node);

// 非头 lookup 命中：s5/s6 在 unlink 前读取，setter 有 NULL 门
unlink(list, hit);
set_next(list, s6, hit);
set_prev(list, hit, s6);
set_prev(list, s5, hit);
set_next(list, hit, s5);
if (!s5) store32(cache+0x38, hit);
if (!s6) store32(cache+0x34, hit);
payload_again = load32(tree+0x10);
header_offset_again = load32(cache+4);
// 后续原非NULL门通过后返回 payload_again+header_offset_again
```

业务含义是该默认实例把最近成功插入或查询命中的节点放在头，从尾往头找首个无引用 entry 作为 victim；节点保有 payload 的关联索引，不转移 Pixel/source 所有权。普通 release 的引用/失效门继承 A27，不能叫作链命中提升。静态顺序不证明任意图片实际命中或被驱逐。

## 真正新增

新增业务功能、资源恢复与来源排除均为0。新增交付只有 A34 的限定独立技术复核、两处原序表达补充及必要稀疏原字节核对；没有把 A23/A27/A30/A32 或旧函数索引重新计为恢复，也没有整函数导出或完整排序树展开。

## 未闭精确边

- 动态 backend/链接偏移/端点重配和同步的实际写者仍未核；不由正常初始化推断不可修改。
- 全部 key 比较等价、重复 insert 的业务前置条件与全部 API 是否改变访问次序未认证；不扩为全库 LRU。
- 实际命中/ref时序、具体图片驱逐、准确 LVGL 来源版本和厂商 ISA 规范来源仍未认证；不把候选源码或 SIM 当运行证据。

本题已闭合限定复核，无需继续重复同一条链。唯一后续闭包建议：若管理者继续研究，先复用旧材料，仅针对已定位的动态 +30/backend 写者选择一条正常配置接入；不要再递归复核本报告的静态默认顺序。

## 实际静态验证

独占 [verify.py](../../analysis/image-cache-order-review-a36-0041-20261024/verify.py) 以 `offset=VA-0x9ffff000` 只读主仓原 ROM，40组稀疏锚点共330 B、17个直接 JAL 目标和4个厂商 word 位域检查全部通过；结果见 [review-evidence.json](../../analysis/image-cache-order-review-a36-0041-20261024/review-evidence.json)。标准指令由 Capstone 解码，JAL 位域与厂商字段独立计算；未重新导出整函数、重建哈希账或修改模型。另作 JSON 可解析、报告链接及 `git diff --check` 交付检查。该检查属于独立复核，不是固件或设备执行验证。
