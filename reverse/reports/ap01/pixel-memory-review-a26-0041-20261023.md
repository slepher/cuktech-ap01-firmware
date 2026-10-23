# A26：A25 默认 Pixel 内存绑定的独立复核

2026-10-23；基线 `fca1d5e`；分支 `codex/re-0041-a26`。**限定接受 A25 新增的默认三表绑定、raw/free/align ABI、独立对齐槽及 raw→Pixel 归还顺序，无语义纠正。新增原 ROM 功能恢复为 0。** 本次原字节重读全部计为旧结论复核。

只在本报告和独占 `reverse/analysis/pixel-memory-review-a26-0041-20261023/` 写入。遵循管理共同规则、A26 任务书及 REA 技能；复用留存原件证据，不打开或切换共享可写 REA target，不创建下级 agent。不修改 ROM、生产代码、配置或分析器模型；未运行 SIM、构建、回放、目标代码、设备或网络。

## 继承的旧结论与实际缺口

|既有出处|已经解释的行为 / 证据种类|局限与本轮所补|
|---|---|---|
|[A23](png-session-lifecycle-a23-0041-20261023.md)、[A24](png-session-review-a24-0041-20261023.md)|带原件字节的 PNG/session/cache 所有权、Pixel 的 raw/data 区别、独立 `62fc964c` 读取|直接继承；本轮不重新解析 PNG、构造算法、缓存或页面业务|
|主仓 `reverse/analysis/0041-20261013/0041-ghidra-pass3.txt:1931,2048`|旧反编译已记录 UI main 调 `a008e3ac`|仅能证明旧调用记录；该调用不是首次发现，本轮不重复取证|
|[A25](pixel-memory-contract-a25-0041-20261023.md)及其 [reuse-crosscheck.json](../../analysis/pixel-memory-contract-a25-0041-20261023/reuse-crosscheck.json)|三表绑定、raw 加3、4B 对齐、Pixel 零分配包装及归还原序已有带原字节结论；旧 matrix/map、system/charge complete、page/round4 和 ZIP 定点检索已记录|本轮缺口只是独立技术验收，按实际槽地址和寄存器核对；不重复执行检索或重新记业务恢复|
|A25 复用对照中 ZIP `tools/ap01/rehost-assets.py:123,448`|SIM 字体 bitmap callback 的 `lv_draw_buf_t` 参数|重建接口不能认证 ROM 内存 ABI；不执行归档脚本，不复制/全量解包|

A25 的旧材料精确词未命中只代表有界检索，不能推出过去从未分析；SIM 完成状态也不证明原 ROM 的完整内存实现。此次无需另建分类、来源哈希或全函数导出。

## 本轮复核或纠正

核验依据是只读原件 `D:/Documents/PlatformIO/Projects/cuktech-ap01-firmware/roms/0041/ap01-1.0.2_0041.bin`，映射 `offset=VA-0x9ffff000`；沿用既有原件身份，不重算哈希。自写 [verify.py](../../analysis/pixel-memory-review-a26-0041-20261023/verify.py)直接读原字节，独立从 U/I/S 编码逐步求值，跨调用清除 caller-saved 寄存器，未导入、执行或复制 A25 核验脚本。普通 RV32/RVC 锚点用本机 Capstone 解读；没有新增 REA Evidence ID。证据集中在 [review-evidence.json](../../analysis/pixel-memory-review-a26-0041-20261023/review-evidence.json)，保留断言和必要原字节位置。

|项目|复核结果|原件定位与限制|
|---|---|---|
|默认写入地址及值|接受|`a008e3c4..e3d6`、`a008e3fe..e4b8（末端不含）` 的必要初始化窗口。独立算出 `G=62fc957c`、`s3=62fc95fc`，四次清零实参依次为 G/528、9644/24、965c/24、9674/24；三个表的 `+0/+4/+8` 都为 `a007fe60/a007ff40/a007fe4e`。SW 为32位写；`967c` 与 `964c` 地址不同，值相同不代表同一个槽|
|raw callback ABI|接受|`a007fe60..fe74`，`fe68` 对 a0 加3，`fe6a` JAL 目标 `a008aea0`；callback 未读 a1，不把 caller 的 cf 推为其必需参数。加法按 RV32 保留低32位，不增加溢出保护|
|align callback ABI|接受|`a007fe4e..fe5e`，`fe54` 为 NULL 跳过分支，非空 `fe56/fe58` 执行 `(raw+3)&~3`，不读 cf；不能推出 raw 本来已对齐或更高对齐|
|raw free callback|接受|`a007ff40..ff52` 中 `ff48` 直调 `a008ab8a`，原 a0 不作对齐反算；不据名称认证底层 heap|
|Pixel 本体身份|接受|`a0081daa` 传28、`1db4` 直调 `a008e362`；`e36c` 保存长度，`e370` 调 `a002fcc8`，`e374/e376/e378/e37c/e384` 证明成功时以保存长度清零并返回同一指针。它与 raw 的 `a008aea0` adapter 不同|
|接入点 ABI / 发布|接受|`1da8/1db0` 保存 handlers/cf，`1e16/1e6c/1e6e/1e70/1e72` 核出 `alloc(size,cf)`、保留 raw、原 NULL 门；`1e90/1e9c` 真正从 `62fc964c` 取 align，`1ea0..1eac` 保留槽空时 data=0 分支、调用 `align(raw,cf)` 并先写 data 后 raw，`1eb4` 发布借用 handler。未新增 align 返回值的 NULL 检查|
|析构原序及宽度|接受|`1f72` 是 LHU 读取 flags，`1f78/1f7a` 核 owned 门；`1f7c/1f7e` 从 Pixel+18 取 handler；`1fba/1fbc/1fbe/1fc0` 重读 handler+4，非空时取 Pixel+14 的 raw 调用；`1fc2/1fc4` 才归还已保存 Pixel。data+10 未作为 release 实参；空 release 槽跳到 Pixel free|

没有发现本范围中的 custom0、unaff、extraout、错误 no-return 或边界冲突。普通指令锚点解码充分，不以候选 LVGL 源码替换 ROM 事实。完整构造失败诊断、size/stride 和 cache 路由继续引用 A23/A24/A25；本轮未重新审计这些整段合同，也未扩大接受范围。

在默认初始化完成、相关槽未被替换、正常有效对象与成功申请的前提下，A25 的分析伪代码成立：单独获得28B Pixel；raw 申请 size+3；独立964c使 data 为 raw 的4B向上对齐地址；保存 raw/data 和借用表；允许析构时先通过当前 handler+4 归还 raw，再归还 Pixel。此为静态条件结论，没有运行观测。

## 本轮真正新增

新增的是上述结论的独立技术验收；**新增功能为 0，语义纠正为 0**。120 条唯一必要指令、366 B 原字节重读和96项断言全部通过；仅保留有助于定位的锚点，不重复保存三个短 callback 的完整导出，均属“旧结论复核”，不能再计为业务恢复。没有重新导出整函数、完整 init、资源、PNG、源码归档或机械哈希清单。

## 仍未闭合的精确边

后续何时可能改写三表或独立964c仍未穷尽；`a002fcc8/a002e14e` 的 heap 策略、实际复用与 cache eviction 到 payload cleanup 的调用连接仍未知；非 cf10 的完整 size/stride 选择及库版本不在本复核内。A26 不关闭、改写或继承外推这些 A25 断边。

本独立复核问题已得到有界答案，不为增加函数数或时长继续扩扫。后续是否调查动态写者或 cache 清理，应由管理窗口先对既有成果去重后另行决定。
