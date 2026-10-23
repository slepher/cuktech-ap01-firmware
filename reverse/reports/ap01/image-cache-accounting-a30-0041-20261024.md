# A30：image cache 的计量 callback 与预算数据合同

2026-10-24；基线 `bccdd65`；独立分支 `codex/re-0041-a30`。本题仅补 A27/A28 明示的 cache+3c 断边。初始化成功时该槽安装 **a00ea5be**，实际 ABI 是 `(const void *record) -> uint32_t`，直接返回 record 首个 word。沿 A23/A25 已恢复的 PNG 插入者，首 word 来自 Pixel+c 的 data_size，因此预算计量的是该像素 data_size 对应的逻辑字节量，不是 entry 数、压缩资源大小，也不是完整 heap 实占认证。

应用已读的 `reverse-engineer-anything` skill；复用原 REA 留存及 A23–A28，不切换共享 REA target/database，不改 ROM/模型。全部为只读原件的静态分析；未执行固件、SIM、构建、历史回放、设备或外部服务。只写本报告与独占 analysis，不改原报告或共享索引；未创建下级 agent。新增恢复待独立技术复核。

## 继承的旧结论与实际缺口

|既有出处|已解释行为|证据局限|本轮补什么|
|---|---|---|---|
|[A23](png-session-lifecycle-a23-0041-20261023.md)，A24；A23 `instructions.txt` a00eb994..b9b2|PNG 将 source/class 放 key+4/+8，`b9ac LW a5,c(a2)`、`b9ae SW a5,-38(s0)` 已留 key+0=Pixel+c；wrapper 写 payload+c/+10/+14；cleanup 表安装已知|报告将 payload 首 word 记 unknown，未连接计量消费者|直接继承 key producer，不重新导出 PNG、callback 或析构|
|[A25](pixel-memory-contract-a25-0041-20261023.md)，A26|Pixel+c 保存 size；默认 raw allocator 按 size+3 申请；本 PNG cf10/显式 stride 分支 size 为 RV32 `(width<<2)*height`|并未说明 cache 计量读取哪个字段|直接继承分配 size 的字节合同，不凭 LVGL 名字猜单位|
|[A27](image-cache-cleanup-a27-0041-20261023.md)，A28 独立复核|cache+8 容量，+c 用量；容量门 unsigned 比较；成功移出后 cache+3c(payload) 结果从+c扣除；release/victim 到 cleanup 已闭|计量槽身份、key/payload 首 word 数据连接未恢复；排序/victim策略另有未知|只补 init 写槽、首 word callback、成功插入增量与既有扣减对称连接|
|whole-ROM round1 索引 a00f0d1c/a00ebb90/a00ea78c 等；round3 `sub64-no-return-20261023.json` repair_events[642]/[662]|已有函数范围、来源候选、no-return 边界修复；a00ebb90/a00f0d1c 此前已经分析定位|repair_events 是边界/refit 元数据，不是计量行为合同，不能因此写“首次分析这些函数”|沿已知范围只核必要短窗口，不整函数重导|
|旧 final SIM 报告、matrix、factory map、四 complete、page-logic、round4/knob/settings/照片留存、pass3、ZIP 文本成员|旧 SIM 行为及其原证据保留；本题地址/字段有界检索见 `reuse.json`|检索未命中不能证明从未分析；SIM/替代服务不能证明 ROM cache ABI|无 SIM 重做，无旧 remaining 重记；只补上述已明确断边|

旧材料复用查询覆盖当前路径的上述文件及 ZIP 的35个文本成员。较晚 round3 唯一相关地址命中是已述 no-return 修复记录；`private-rea-tool-schemas.json` 的 cache_entry 仅工具 schema。范围见 [reuse.json](../../analysis/image-cache-accounting-a30-0041-20261024/reuse.json)，未复制旧 stdout/源码。证据类别分别是：A23–A28 的原字节行为合同；whole-ROM/round3 的地址与边界元数据；旧 SIM 重建；本题确切未闭的计量接入。

## 本轮复核或纠正

仅将 a00ebf60..bf6a 再读原字节列为**旧结论复核**：cache+3c `(payload)` 返回后，重读 cache+c，RV32 SUB 后 SW。这不是新增移出/驱逐恢复；其索引移除、payload 适配、cleanup 和释放原序全部继承 A27/A28。

A23 `CachePayload.unknown00[4]` 现可在本 PNG/cache 路径细化为 `uint32_t charge_data_size`，依据是旧 key producer 加本轮 callback 消费者，不改写旧成果。该细化不适用于所有其他 cache backend 或格式对象。未遇到需要修改模型/原 no-return 修复的字；新增窗口没有 custom0/unaff/extraout 或未知指令。

## 本轮真正新增

### cache+3c 的实际安装

A27 已核 backend 常量表 a0263afc 的 +4=a00f0d1c，以及创建器 a01985e4..85ea 以 `a0=cache` 调 backend+4。本轮只追这个已知 initializer 的正常成功尾段：a00f0d6c 保存 cache 至 s1；a00f0dea 根据初始化返回值分支，成功才执行：

```text
a00f0df0 b7a70ea0  LUI  a5,a00ea
a00f0df4 9387e75b  ADDI a5,a5,5be  -> a00ea5be
a00f0df8/dfc        cache+34=0；cache+38=0
a00f0e00 dcdc      SW   a5,3c(s1)
```

其 +30=4 与链字段清零只用于解释该实例初始化，不推导完整排序或所有 cache。此处确认创建时默认槽；不声称后续永不可重配。A23 中 image cache 的创建及保存到 G+11c、容量0xe1000 已有，不计新增。

### 参数、返回与单位

a00ea5be..a00ea5cb 中唯一记录内容读取是 `a00ea5c6 0841 C.LW a0,0(a0)`，随后返回，没有读取 cache、entry header 或 Pixel 指针，也没有乘除/饱和/附加常量。ABI 的有效输入只有 a0=record，结果为原32位 word。signed/unsigned 的业务解释由消费者确定：预算门使用 unsigned 比较，增减是 RV32 word 算术。

由 A23 原字节，PNG 在 key+0 放 Pixel+c；A25 证明 Pixel+c 是传给默认 raw allocator 的 size，后者额外申请3 B。故本路径 charge 的单位是**像素 data_size 的字节数**。计量不额外加入 raw 对齐余量3 B、28 B Pixel 结构、entry/header/索引节点或 source 字符串副本；这不是 heap 总占用上限。cf10 正常 PNG 分支的 size 公式直接继承 A25，不再次恢复格式分类/stride/解码。

### 正常成功插入与移出的数据连接

a00ebbee 已将原 a1=key 保存在 s8。a00ebdea..df4 将 `cache+4` 长度、key 源、payload 目的传给 a008ab76；该短 adapter 的 a008ab7e JAL 到既有 copy 接口 a000589c。A27 已核本实例 cache+4=0x18，故首 word 随 key 复制到 payload；后续 A23 wrapper 只写 payload+4/+c/+10/+14，不改首 word。

只在成功尾段 a00ebe1a..be3a：node 非空且 payload 非空时，从 payload 加 cache+4 得返回 entry；加载 cache+3c，以 **a0=原 key(s8)** 间接调用，返回后重读 cache+c，`used += charge` 并 SW。它没有把 callback 直接参数改成 entry，也没有在每次请求一进函数就加用量。树路径、平衡算法与所有失败分支不在本题，不能把这一成功尾段外推为每个 insert 调用都增加。

移出端继承 A27：先由 entry 得 payload，再在成功移出后调用同槽 `(payload)`，重读 cache+c，`used -= charge`。由于 payload 首 word 已由 key 复制，两端在本路径使用同一逻辑字节值。entry 的引用 header 与 payload 首 word 是不同对象位置，不把引用数或 entry 数当计量。

### 接上既有预算门

以下为接入合同伪代码，不是原源码；预算门与驱逐循环本来已经恢复：

```c
uint32_t charge(const void *record) { return load32(record); }

// A27 既有 a00ea78c；本轮只解析其 callback 的实际含义。
need = key ? cache->charge(key) : 0;
if (capacity < need) return 1;                // unsigned
return capacity < (uint32_t)(used+extra+need) ? 2 : 0;

// a019d914 的 extra=0；返回2可驱逐并重新检查，1拒绝，继承A27。
// 本轮连接的成功插入尾段：
amount = cache->charge(original_key);
used = load32(cache+0x0c);
store32(cache+0x0c, (uint32_t)(used+amount));
// 成功移出后：callback(payload)，再load used，再sub/store。
```

所有加减截断为32位；未提升为64位，也不新增异常/溢出实验。初始化 used=0、预算0xe1000 以及 victim跳过非零引用继承 A27；不作运行时命中率、真实驱逐次数或全局物理内存保证。

## 仍未闭合的精确边

- 动态计量 callback/容量重配及其他 backend 是否安装不同函数未展开；本结论限定该 image cache 的创建默认表和已核 PNG caller。
- 全排序/victim优先级、索引算法、并发同步与底层 heap 实占仍未知；不为闭包扩全cache/heap/PNG。
- A29 独占失效 API 上层业务连接；A23–A28 的析构与 release 合同不在本轮重复恢复。普通 release 不等于成功 backend 移出，不能自行添加一次计量扣减。
- 原 ROM 准确 LVGL 来源版本仍未认证；候选源未参与推定单位，没有新增开源排除。静态安装/数据连接不证明某张图实际执行成功。

本题限定断边已获静态接入证据；一个后继应独立复核 +3c 实际安装、key/payload 首 word 别名及成功加减原序，继承旧预算/cleanup，不重新导出整函数。

## 必要静态验证

[verify.py](../../analysis/image-cache-accounting-a30-0041-20261024/verify.py) 对只读原 ROM 的8个短窗口、114 B、44条指令作25项原编码/直接调用目标断言，全部通过；其中移出扣减是明确标注的旧结论复核。无厂商或未知指令；没有整函数导出。原指令与偏移保存在 [evidence.json](../../analysis/image-cache-accounting-a30-0041-20261024/evidence.json)，映射 `file_offset=VA-0x9ffff000`。身份沿用既有 ROM 认证，不另建哈希清单。JSON解析、报告相对链接及 `git diff --check` 另作交付检查。
