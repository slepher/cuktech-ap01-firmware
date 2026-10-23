# A32：A30 image cache 计量接入独立复核

2026-10-24；基线 `3ba6b963c20ff0f6dffd503c52567c9e013cfc84`；独立分支 `codex/re-0041-a32`。**限定接受 A30 的默认计量安装、成功插入累加及与既有 payload 扣减的连接；未发现语义纠正，新增功能恢复为0。** 复核并不扩展为全 cache、全部插入失败分支、heap 实占或来源版本认证。

使用 [reverse-engineer-anything](C:/Users/cogic/.agents/skills/reverse-engineer-anything/SKILL.md) 的留存优先流程，先读正式 A30 与其 evidence/verify，再定位必要原字节。未打开、切换或修改共享 REA target/database；未执行固件、SIM、构建、历史回放、设备或网络操作。只写本独占报告及 analysis，不改主树共享材料、ROM、生产配置或分析器模型，未创建下级 agent。

## 继承结论与实际复核缺口

|已有出处|已解释的行为|证据局限|本轮处理|
|---|---|---|---|
|[A23](png-session-lifecycle-a23-0041-20261023.md)、A24；A23 原 `instructions.txt` a00eb994..b9b2|`b9ac LW a5,c(a2)`、`b9ae SW a5,-38(s0)`，key+0 来自 Pixel+c；wrapper 写 payload+4/+c/+10/+14|单独不能识别计量消费者|直接引用 key producer 和 wrapper 写字段，不重导 PNG|
|[A25](pixel-memory-contract-a25-0041-20261023.md)、A26|Pixel+c 是 data_size，默认 raw 分配 size+3，Pixel 本体独立28 B|不能据此认定 cache 等于全 heap 实占|字节单位与分配合同直接引用，不复核默认 handler 或 size 分类|
|[A27](image-cache-cleanup-a27-0041-20261023.md)、[A28](image-cache-review-a28-0041-20261024.md)|cache+4=0x18、+8容量、+c used；backend 表/创建者；成功移出用 payload 调 +3c 后扣减；预算 unsigned 比较；cleanup/release 原序|未独立认证 A30 新增 callback 身份及 key/payload 计量连接|直接继承后端对象、容量门、payload 适配与 cleanup；只核连接锚点|
|[A30](image-cache-accounting-a30-0041-20261024.md)及其 [evidence.json](../../analysis/image-cache-accounting-a30-0041-20261024/evidence.json)、[reuse.json](../../analysis/image-cache-accounting-a30-0041-20261024/reuse.json)|短窗口已经留存安装、copy、成功加减和回调；旧 complete/最终 SIM/ZIP/round3 有界复用完成|A30 为待独立复核，旧入口与 no-return refit 元数据不能当行为合同|本轮唯一审查对象；不重复 ZIP/全证据扫描，不重计旧地址发现|

因此实际缺口是 A30 新增连接的对象身份、间接 ABI 和宽度/顺序，不是尚未恢复整个 PNG/cache。A29 失效业务连接与 A27/A28 cleanup 直接继承；旧 SIM、候选源码和 token 搜索无命中均不被提升为 ROM 行为认证。

## 本轮复核或纠正

|A30 主张|结论|核对依据和接受边界|
|---|---|---|
|初始化默认 cache+3c 安装 a00ea5be|接受|`a00f0d6c aa84` 保存 cache 到 s1；`0dea 01cd` 在 a0=0 时跳过安装段，到0e02。`0df0/df4` 的 LUI/ADDI 独立拼出 a00ea5be；`0e00 dcdc` 存至 s1+3c。backend+4=a00f0d1c 及其创建连接直接继承 A27/A30；本轮不重导 initializer。只认证初始化正常成功尾段的默认值，不声称不可重配。|
|callback `(const void *record)->uint32_t` 返回首 word|接受|完整14 B短 callback `a00ea5be..a5cb` 除栈/保存恢复外，只有 `a5c6 0841` 读取 `LW a0,0(a0)`；`a5ca 8280` 返回。独立解 C.LW 位域，基址与结果寄存器均a0，偏移0。没有解引用 Pixel 或 cache，没有乘除/附加常量；uint32_t 是下游预算/word算术解释，指令本身仅返回原word。|
|成功插入按原 key 计量，并在 callback 后重读 used|接受|`a00ebbee` 保存 a1 到 s8；额外必要身份锚点 `a00ebc30 2a89` 保存 cache a0 到 s2。`be1e` node为空绕过，`be20` 读node+10，`be26` payload为空转离当前尾段。`be2c/30/32` 为 load cache+3c、a0=s8、JALR；`be34/38/3a` 才 load cache+c、RV32 ADD、SW同槽。没有把 entry/header 当 callback 实参，没有把 used 提前缓存跨 callback 使用，也不声称每次插入请求均增加。|
|key 首 word 复制到 payload，可与移出同字段扣减连接|接受（引用已核对象适配）|`bdea..bdf4` 使用 cache+4 长度、原 key=s8 源、payload=s1 目的；独立解直接 JAL 目标 a008ab76，后者 `a008ab7e` 调既有 copy 接口 a000589c。cache+4=0x18 及该接口合同继承；A23 wrapper 后续不改首word。`bf60..bf6a` 再核同槽 `(payload)` 后重读+c、SUB、SW；payload身份和成功移出的前置条件继承 A27/A28，不展开移除索引或 cleanup。|
|计量单位为本 PNG 像素 data_size 字节数|接受（连接推断）|原指令事实是 record首word原值；A23/A25 给 key+0=Pixel+c=data_size 字节合同，故该PNG路径使用此逻辑字节量。它不含默认 raw 额外3 B、Pixel本体、索引/header、source副本或 allocator 元数据。不能推为全heap实占；不把此字段语义外推其他backend/格式。|
|计量值接容量预算门|接受继承后的数据连接，未重核全部预算分支|A27 已核 `a00ea78c` 对 key 调+3c、unsigned capacity比较、used+extra+need 的 RV32算术；a019d914 的 extra=0及返回2驱逐后再查直接继承。本轮仅把已核槽的实际含义代入，不扩算术失败/异常或运行时预算保证。|

没有语义纠正。这里的 s2=cache 锚点是对既有寄存器身份的独立确认，不是新功能或新入口恢复。未遇厂商字、custom0、unaff 或 extraout，未改模型。payload 与 entry/header 是不同位置：entry-to-payload 动态偏移适配继承 A27/A28，不用固定0x18替代该适配器。

以下仅表达已接受连接的伪代码，不是原源码，也不补全函数所有分支：

```c
// initializer 的正常成功尾段；后续重配未核
cache->charge = a00ea5be;
uint32_t a00ea5be(const void *record) { return load32(record); }

// 已确认成功插入尾段：key 首word已经按既有 copy 合同进入 payload
amount = cache->charge(original_key);
used = load32(cache + 0x0c);                // callback 后重读
store32(cache + 0x0c, (uint32_t)(used + amount));

// 成功 backend 移出之后；前置条件/适配/cleanup继承 A27/A28
amount = cache->charge(payload);
used = load32(cache + 0x0c);
store32(cache + 0x0c, (uint32_t)(used - amount));
```

业务及所有权含义：该字段只承担逻辑预算计量，不转移 Pixel/source 所有权。插入保留像素资源与 session/cache 持有关系继承 A23；backend 移出扣减发生在既有 payload cleanup 之前，之后的 release、失效和析构由 A27/A28 决定，不能把普通 release 写成必扣减/必free。静态代码连接不证明某张图实际命中、插入或驱逐。

## 真正新增

新增业务功能、资源恢复和来源排除均为0。新增交付只有 A30 的限定独立复核及必要稀疏字节检查。上述原字节重读均标作复核，不重复计算 A23/A25/A27/A28 的恢复成果，没有整函数导出、全cache/heap/PNG展开、资源提取或机械哈希清单。

## 未闭精确边

- 动态计量槽/容量重配是否发生、其他 backend 安装何函数仍未核；本报告只接受默认创建及已核 PNG caller 的连接。
- 所有排序、victim优先级、并发同步、底层heap实际开销和完整插入失败分支未另核；沿用前序边界，不以局部加减认证整个cache。
- ROM 的准确 LVGL 来源版本仍未认证；没有把候选源码、SIM结果或地址清单当来源排除或实际运行证据。

唯一后继建议：如管理者继续派题，应先检索既有材料，再限定调查动态 +3c 或容量写入者；不要再递归复核本报告已经接受的同一条计量连接。

## 实际静态验证

独占 [verify.py](../../analysis/image-cache-accounting-review-a32-0041-20261024/verify.py) 只读主仓原ROM，以 `offset=VA-0x9ffff000` 映射核29个稀疏锚点、88 B，全部通过。除原编码与标准指令核对，还独立解安装地址的LUI/ADDI、C.LW寄存器/偏移位域、两个JAL直接目标；记录在 [review-evidence.json](../../analysis/image-cache-accounting-review-a32-0041-20261024/review-evidence.json)。身份沿用前序ROM认证，不重建哈希账。交付另核 JSON可解析、报告链接存在及 `git diff --check`；没有SIM、构建、固件/设备执行、共享可写target或网络。
