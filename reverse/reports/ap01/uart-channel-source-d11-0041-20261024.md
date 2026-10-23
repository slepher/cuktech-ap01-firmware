# D11：UART 三槽归还与 shutdown 的本地 SDK 来源界限

2026-10-24；基线 `bccdd65`；独立分支 `codex/re-0041-d11`。使用 reverse-engineer-anything skill，只读既存 ROM 报告及本地 SDK 源文本，没有打开共享 REA target/数据库。本轮没有重新读取 ROM 字节，没有 SIM、构建、回放、固件执行、设备、外网、下载或源码复制；未改生产代码、ROM、配置、分析器模型及共享索引。

**候选 SDK 没有在本次有界检索中提供 D09/D10 三槽 allocator、busy 归还或 UART lower shutdown 的对应实现，不能认证这些函数的原始来源。** 近名的 LHAL deinit/disable 属于更低一层，其参数和操作集合不足以替代 ROM 合同；新发现的是来源适用边界，新增 ROM 业务恢复为 0，新增整库排除为 0。

## 已有成果→实际缺口

|既有出处／证据层|已经解释的行为|证据局限／本轮补什么|
|---|---|---|
|[D09 复用对照及原指令](uart-dma-channel-d09-0041-20261023.md)、[D10 独立复核](uart-dma-channel-review-d10-0041-20261023.md)|原字节支持三槽分配、清 busy/post、File 最后 close 到 lower shutdown 和 0x0f 发布；D10 已纠正 type/channel 重读次数|行为合同直接引用；只核本地 SDK 是否有同对象、同 ABI、同清理顺序实现，不重新逆向|
|[D03](uart-write-object-d03-0041-20261023.md)至[D06](uart-ring-review-d06-0041-20261023.md)|File/inode/dev、lower/private 身份、TX channel 与 DMA callback 安装、ring 归还|初始对象及间接 ABI 已有原字节；本轮不重做驱动或扩 IRQ 析构|
|[D07 来源认证界限](uart-dma-descriptor-d07-0041-20261023.md)、[D08 候选复核](uart-dma-review-d08-0041-20261023.md)|候选 SDK HEAD `41bf338a57be53919d99f6c6715a96100428c97d`、VERSION 2.3.36；LLI、stop/cache 等局部同形及返回/包装差异已解释|候选身份不认证 ROM 版本。身份与旧匹配全部继承；D07 明确未展开 channel allocator/close，D08 仍留该边，不能把旧局部认证外推到 D09|
|D09 的 [21份旧材料/39个 ZIP 成员有界检索](../../analysis/uart-dma-channel-d09-0041-20261023/reuse-check.json)|SIM 最终 complete、factory map、旧 pass3 dma0_ch3、应用与本地替代服务的范围已区分|直接复用该检索，不再导出 ZIP、复制源码或新建同一机械账；旧 pending/remaining 不作为缺失证据，passed-in-sim 不认证驱动来源|
|本地 SDK LHAL 源文件，见下表|有 device* 型 UART/DMA MMIO 操作和 callback 表 detach|与三槽 busy/RTOS shutdown 是不同层；本轮只检查这些最接近候选，报告具体不适用点|

证据分类：D03–D10 的原字节行为及独立复核属可靠既有合同；早期反编译/字符串只保留其旧身份线索，不作来源认证；SIM 本地服务属重建/替代；本题精确未闭边为三个 ROM 函数到匹配版本、编译条件与原始源实现的对应。文本未命中不等于此前从未分析。

## 继承的旧结论

- `a00288de`：等待 `gp-28` 后锁 `gp-38`，按序选 `62fc6048[0..2]` 首个零 byte，置 1、解锁并 sign8 返回 index；非堆分配，不构造 handle。
- `a01b5c48(channel)`：同一锁保护同一 busy byte，非零才清零→post→解锁；不清 callback，不 free pool/pair。caller 不消费其返回寄存器，不能补造 success 返回合同。
- `a00198bc(dev)`：在既有型号及 private+e/channel 门内调用 stop→release busy→发布 channel byte 0x0f。type/channel 的原读取次数与顺序以 D10 精度纠正为准：type 为 9900/992e/9942，channel 为 9908/9916/9922/9932，9948 写回。不能用一次 snapshot 合并。
- 正常最后 close、console/dev 动态门、初始 private/ops 身份，以及 stop 的 index→handle 包装均继承。busy 可归还不证明硬件静止、全局互斥或 DMA callback/IRQ pair 析构。

这些均不是 D11 首次发现。本轮不重读原字节、不重新导出整函数。

## 本轮复核或纠正

### 候选路径与实际层次

候选根为 `D:/Documents/PlatformIO/Projects/bouffalo_sdk`。以下均为只读源文本；路径行号可从 [source-check.json](../../analysis/uart-channel-source-d11-0041-20261024/source-check.json) 定位。本轮不重复认证 Git 身份或 tracked clean，沿用 D07/D08 的限定记录。

|ROM 合同／近名候选|本地源观察|能否认证对应与具体局限|
|---|---|---|
|`a00288de` 三槽软件 allocator|整个候选默认可见 C/H 语料中，对 `dma_channel_(alloc/free/release)`、dma…channel…alloc/free、`g_dmach/dmachannel/nxsem_/nxmutex_` 组合检索无命中|未找到同实现；不把低层 MMIO busy 读当软件 busy 分配，也不凭无命中断言编译产物不存在|
|`a01b5c48` busy 归还 ↔ `drivers/lhal/src/bflb_dma.c:178` `bflb_dma_channel_deinit`|非 ROMAPI 分支只 `stop(dev)`→`tcint_mask(dev,true)`，返回 void；没有该三槽 byte、信号量 post、slot 归还或 0x0f 写回|不是 allocator 配对 free 的等价实现。ROM ABI 为 channel index，候选为 `bflb_device_s*`；不能套候选 void 声明解释 ROM a0 遗留|
|`a00198bc` lower shutdown ↔ `drivers/lhal/src/bflb_uart.c:141` deinit / `:179` disable|非 ROMAPI 分支读取 `dev->reg_base`，读 TX/RX CONFIG，清 UTX_EN/URX_EN 后写回；两者都没有 DMA stop/free、private/type/channel 表或哨兵发布|只提供低层 enable 清除接口，未找到 RTOS lower shutdown 对应；它们不是同层的已证源码差异版本，不能由此说 ROM “漏做/多做”了某操作|
|D07/D08 的旧 stop 同形 ↔ `bflb_dma.c:479` stop|device->reg_base 的 CONFIG 读、清 DMA_E、写回；`:496` isbusy 只读同寄存器 bit0|仅为既有局部匹配复核，不计新增；硬件 enable/busy 与软件 `62fc6048` 三槽不是同一字段/对象|
|未闭 DMA pair 析构 ↔ `bflb_dma.c:562` irq_detach|清 `dma_callback[dev->idx][dev->sub_idx].handler/arg`，再 mask；没有 free|候选确实有另一个 detach API，但上述 UART deinit/disable 与 DMA deinit 函数体都不调用它；不能把它当作 ROM shutdown 的隐式步骤，更不能填 ROM pair 最终 free 断边|

带 `#ifdef romapi_*` 的入口另有 ROM API 委派分支。这里只比较可见 non-ROMAPI 实现，候选编译宏/芯片路径未认证；本地 ROMAPI 表中的同名指针/宏不会提供与 AP01 0041 相同的底层机器码证明。不能把未找到 NuttX 层源码说成 ROM 一定私有或候选库整体不匹配。

没有发现需修改 D09/D10 行为合同的技术结论；只收紧来源外推范围。

## 本轮真正新增

新增的是上述三处来源认证缺口的具体定位，以及候选 deinit/disable/irq_detach 为什么不能替代 ROM 清理合同的源级证据。**新增 ROM 功能 0，新增标准库/开源整库排除 0；不重记 D07 stop/候选身份与 D09 allocator/shutdown 为新增恢复。**

实际运行 [source_check.py](../../analysis/uart-channel-source-d11-0041-20261024/source_check.py)：37 项静态检查通过，定位 6 个候选函数、检查必要操作/缺少的直接调用/次序，完成 3 组有界 C/H 符号检索，并核对 D10 所继承的地址锚点。检查数不是新行为数。只保留定位行号、检查标签和检索范围，没有复制源函数或留存整库清单，也没有新建 ROM 哈希/字节导出。

有界检索遵守 rg 默认 ignore/隐藏规则，只检默认可见 C/H；不含 binary/archive/history 或任意改名实现的语义穷举。无命中只认证本次检索结果，不认证候选永远没有任何同算法实现。

## 仍未闭合的精确边

1. `a00288de/a01b5c48/a00198bc` 对应原始源文件、原始版本、构建宏与 RTOS 同步包装未认证。现候选只能支持更底层相容性，不能认证其就是 0041 原源码。
2. ROM callback/IRQ pair 最终 detach/free 仍是 D09/D10 的独立未知；候选 `irq_detach` 的存在没有提供 ROM caller/安装/释放连接。
3. 全局同步内部、固定 pool 跨设备互斥、硬件排空、RX/type>1、动态 ops 替换不在本题，不由来源名称推断。

本题在当前唯一授权候选上已给出有界答案，没有新的可靠 ROM caller 种子；不建议重复搜索同候选或扩全 IRQ。后续若取得原 RTOS UART/DMA 源文件与版本/构建对应证据，再对这三个函数做来源认证；当前不下载或换题。待独立技术复核，由管理窗口决定后继。
