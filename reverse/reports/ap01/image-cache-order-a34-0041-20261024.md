# A34：image cache 的访问次序与 victim 优先级

2026-10-24；基线 `173ee40`，分支 `codex/re-0041-a34`。本默认 image-cache backend `a0263afc` 的 `+34` 是双链头，`+38` 是双链尾，`+30=4` 是节点内链接区域的偏移，**不是分数或时间戳**。成功新插入接头；backend+0c 查询命中非头条目时移到头，头命中不改次序；victim 从尾向头找第一个零引用条目。因此本默认路径呈现“最近插入/命中在头，较早未再命中者先成为驱逐候选”的次序。结论来自指针写入与访问顺序，不来自 LRU 名称或候选开源实现。

应用已读的 `reverse-engineer-anything` skill。静态只读主仓原 ROM/既有证据，不打开或切换共享 REA target/database；无固件执行、SIM、构建、历史回放、设备、网络。只写本报告和独占 analysis，不改生产、ROM、配置、模型或其他报告。新增结果待独立技术复核。

## 继承结论与实际缺口

|既有出处|已解释行为|证据局限|本题范围|
|---|---|---|---|
|A23/A24：`png-session-lifecycle-a23-0041-20261023.md`；A25/A26|G+11c image cache、session hit/miss、插入包装、entry/payload、pixel/source 所有权和析构|不解释排序链|原样继承，不重做 PNG、资源、source 或 heap|
|A27/A28：`image-cache-cleanup-a27-0041-20261023.md` 与独立复核|backend 表身份、容量门、release、byte+c 失效、victim 跳过非零 ref、移出后 cleanup/free|明确保留 cache+38/+30 全链排序和优先级|只补链字段生产、命中提升和移出链接|
|A30/A32：`image-cache-accounting-a30-0041-20261024.md` 与独立复核|init 的 +30=4、+34/+38=0、+3c 计量；key/payload 首 word 和成功加减|没有据此解释排序|初始化字段列本轮旧结论复核；计量完全继承|
|whole-ROM round1：a00eb9c0 extent `ev_aff990cb7bf27ac690be8055d08c6b2a8bbb8931c7236669445b04e0d47a417e`，direct_calls `ev_7b5ea907fa01a5214b7addd303649e19f77bde8d35fe27942a3573bbc3fd1f5d`；其他 backend 入口索引|早已有函数范围、调用 helper、LVGL 来源候选|不是排序行为合同，不能认证准确库版本|沿该有限入口核窗口，不宣称首次分析函数|
|pass3、complete、page/knob/照片、round4、settings、较晚 round3，最终 ZIP|旧完整恢复/SIM/照片重建可复用|43 个既有文件的精确词项查询仅较晚 `sub64-no-return-20261023.json` 命中四 backend 入口；这是边界修复元数据。ZIP 35 文本成员无命中；有界负结果不证明从未分析|见 `reuse.json`，只补已定位字段断边，无重复整函数导出或源码复制|

证据四类分别为旧原字节合同、待局部核的地址/反编译元数据、SIM/照片替代重建、下述本轮原字节接入。没有把旧 pending 或 token 未命中当作功能缺失。

## 本轮复核或纠正

仅复核 A30 已有 `a00f0dec/0dee` 写 cache+30=4、`0df8/0dfc` 清两端，及 A27 已有 victim 从 cache+38 开始/零引用门/`ec270` 无写回的 indexed load。这些不是新增 init、引用检查或 cleanup 恢复。

A27 的“节点关联 word+10 转 entry”现可细化为两级关系：victim 循环 `ec252` 先取 **链节点 word+0 → 查找树节点**，`ec256` 再取 **树节点 word+10 → payload**，然后加 cache+4 得 entry。旧结论的选择结果和引用门不变；不能把链节点本身当 entry/header。

## 真正新增：链字段生产与操作

### 结构和默认初始化

以下为局部结构化描述，不是原源码，不宣称完整对象布局：

```c
// Cache 中查找树与优先级链是两个结构。
cache+0x24: 查找树状态（内部平衡算法继承/不展开）
cache+0x2c: payload 分配长度字段，尾部含一个链节点指针
cache+0x30: uint32_t link_offset = 4;
cache+0x34: OrderNode *head;
cache+0x38: OrderNode *tail;

OrderNode+0: TreeNode *tree;       // 本实例数据区4 B
OrderNode+4: OrderNode *prev;     // *(node+link_offset)，指向头方向
OrderNode+8: OrderNode *next;     // *(node+link_offset+4)，指向尾方向
TreeNode+0x10: payload;
*(payload + load32(cache+0x2c) - 4): OrderNode *backlink;
```

两个 setter 是实际 helper `a0089cda(list,node,value)` 与 `a0089cee(list,node,value)`：node 为 NULL 时不写；前者写 `*(node+load32(list))=value`，后者写 `*(node+load32(list)+4)=value`。第一参在本题各调用点均是 `cache+30`；不要将 `4` 当树比较器结果、年龄或计量。`a0089ce4` 的 `th.srw a2,a1,a5,0` 与普通 `9cfa SW a2,4(a1)` 确定两个方向。

### 成功新插入：新链节点接头并双向关联

在原 `a00ebb90(cache,key,...)` 已有成功 payload 路径，`bdf8/bdfc` 以 `cache+30` 调 `a008aec0`。只核它的指针段 `aed8..af06`：非空新节点先 `prev(new)=NULL`、`next(new)=old_head`；old_head 非空才 `prev(old_head)=new`；随后写 head=new，原 tail 为空才 tail=new。由 offset=4，节点数据4 B，后面是两个 word 链接。分配失败返回 NULL 的门由 `be04` 保留，本题不将失败插入说成成功增加优先级节点，也不重做其旧 tree 回滚/计量合同。

成功分支 `be5c..be7a` 两次使用既有 4 B copy adapter `a008ab76`：第一次把栈内保存的 TreeNode 指针复制至新 OrderNode 的首 word；第二次把新 OrderNode 指针复制到 payload+cache+2c−4。这个 backlink 是正常查询与移出找回链节点的实际来源。entry/header 仍按 A27 由 payload+cache+4 得出，与 backlink 不同。

### 查询命中：提升至头部

backend 表 `+0c=a00eb9c0`。ABI 在正常有效对象范围为 `(cache,key,...) -> entry*/NULL`；未被本窗口使用的后续寄存器实参不作签名认证。

`ba54..ba96` 先读 head。非空时由 head.word0→tree.word10 取 payload，以 `cache+10` comparator `(payload,key)` 检查头候选：返回0即返回该 entry，没有链写入。无 head 或头比较非零，`ba5a..ba66` 转 `a00ea832(cache+24,key)`；返回 NULL 时返回 NULL，不作链写入。命中则 `ba98..baa4` 用 payload 尾 backlink 得到 hit OrderNode，并读当前 head。

`baa8` 若 hit==head 直接取 payload/返回。其余正常路径读 `s6=prev(head)`（`bab4`），默认合法非空链的该值为 NULL；调用顺序严格是：

```c
// a00ebabc..bafe；描述实际写序，保留原重新读取和 NULL setter 门。
unlink(list, hit);               // a0089d02，不释放 hit
set_next(list, s6, hit);         // a0089cee；正常 s6=NULL，跳过写
set_prev(list, hit, s6);         // a0089cda
set_prev(list, old_head, hit);   // a0089cda
set_next(list, hit, old_head);   // a0089cee
if (old_head == NULL) tail=hit;
if (s6 == NULL) head=hit;
return tree_payload + cache_header_offset;
```

原代码仍含 `old_head==NULL`、hit==s6 等局部门和 `bb0c` 空头回退读 tail；这些保留在证据，不以本题解释其异常对象用途。正常完整链的 s6=NULL，因此这里是移到头，不是每次只前进一格。没有增加年龄计数，没有按 payload 首 word 重新数值排序；头部快路径也没有重分配节点。此断言限定已核正常 lookup/insert 接口，未外推所有 API 都影响“最近使用”。

### 移出和选 victim 的连接

`a00ebe98` 正常成功移出 `bf40..bf5c` 从同一 payload 尾 backlink 得 OrderNode，先执行既有树移出，再 `a0089d02(cache+30,node)`，随后 `a008ab8a(node)` 释放**链节点**。计量减法和 payload cleanup/free 的后续顺序完全继承 A27/A30。命中提升只 unlink 再接头，不调这个 node free。

`a0089d02` 的必要指针窗口 `9d10..9d74`：移除头则 head=next，空后 tail=NULL；移除尾则 tail=prev，空后 head=NULL；中间节点则 `next(prev)=next`、`prev(next)=prev`。相邻存取经上述 setter，端点分支也保留 NULL 门。此 helper 不修改 key/comparator，不清理 payload，不释放节点；释放责任在调用者。

既有 `a00ec1e6` 从 tail 开始，关联到 entry 后检查 ref；非零时 `ec270` 读取 `prev(node)`，直到第一个零引用 entry 或 NULL。与以上生产/提升相接后，**较旧访问次序在尾，victim 优先选择从尾起第一个未被引用者**；跳过有引用条目本身不改链。新插入与后续成功查询都可以改变相对驱逐次序。普通 release 的已核路径只有 ref/失效清理门，没有本链提升；不能把 release 叫作再次命中。

## 静态验证、恢复程度与精确未知

独占 [verify.py](../../analysis/image-cache-order-a34-0041-20261024/verify.py) 对主仓只读原 ROM 作 VA−`0x9ffff000` 映射：9 个必要窗口，540 B、198 条指令、43 项原编码/表槽/直接目标/厂商字段断言，全通过。[evidence.json](../../analysis/image-cache-order-a34-0041-20261024/evidence.json) 保留原字节和指令、5 个厂商 word 及只读旧模型的两条短规则；[reuse.json](../../analysis/image-cache-order-a34-0041-20261024/reuse.json) 保留43份旧件及 ZIP 成员复用边界。没有使用不可信 custom0 反编译作为语义依据，未修改模型。5 字分别核：`bab4 th.lrw s6,s5,a5,0`、`9ce4 th.srw a2,a1,a5,0`、`9d3a th.lrw a1,a1,a4,0`、`be86 th.srw s2,s1,s4,0`、`ec270 th.lrw s2,s2,a5,0`；均无额外基址写回，be86 仅是 entry 所属 cache 接入，未重做 header 合同。

本题原字段排序断边在默认正常插入/命中/移出/victim 范围内得到静态答案。仍未知：

- 动态重配 backend/链接偏移或 callback 的所有写者、并发同步和完整树平衡算法；没有扩展扫描所有 cache/heap。
- tree 比较器的全部 key 等价语义与各调用者正常协议（例如重复 insert 的业务前置条件）未在本题认证；不以这条链结论保证任意重复插入行为。
- 实际运行的命中序列、ref 变化时机、某张图是否被驱逐与准确 LVGL 版本来源未认证；没有运行时观察或开源排除。

唯一建议后继：独立复核本轮双链方向、backlink 两端生产和 `a00eb9c0` 命中提升的间接 helper ABI；容量/计量/cleanup/跳过非零 ref 继续继承既有复核，不重新展开。以上验证是自检，不冒称独立技术验收。
