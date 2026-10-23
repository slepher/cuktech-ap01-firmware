# D12：D11 UART SDK 来源界限独立复核

2026-10-24；基线 `9ea568f`；独立分支 `codex/re-0041-d12`。使用 reverse-engineer-anything skill；只读既存报告及本地 SDK 的两个 LHAL 源文件和 DMA 声明。没有打开 REA target/数据库，没有重读 ROM、全候选扫描、SIM、构建、回放、设备、外网或固件执行；未修改生产代码、ROM、配置、分析器模型及共享索引。

**接受 D11 的限定结论：候选低层 deinit/disable/irq_detach 不能认证三槽 allocator、busy release 或 lower shutdown 的原始来源，也不能填补 ROM callback/pair 析构断边。** 本轮只纠正证据定位的结束行，并补核 mask 的可见实现；新增 ROM 功能 0、整库排除 0。

## 已有成果→本轮复核缺口

|既有出处|已解释行为及证据层|局限与本轮范围|
|---|---|---|
|[D09](uart-dma-channel-d09-0041-20261023.md)、[D10](uart-dma-channel-review-d10-0041-20261023.md)|原字节三槽分配、同 busy byte 清除/post、最后 close→lower shutdown→0x0f；D10 已核 type/channel 重读顺序|直接继承，不重取三槽机器码；只判断候选是否足以认证相同对象/ABI/生命周期|
|[D07](uart-dma-descriptor-d07-0041-20261023.md)、[D08](uart-dma-review-d08-0041-20261023.md)|候选 HEAD `41bf338a57be53919d99f6c6715a96100428c97d`、VERSION 2.3.36；stop 等 MMIO 局部相容，包装及其他差异保留|身份和版本记录直接引用，不重新查询 Git/版本，不外推候选就是 ROM 原源码|
|[D11](uart-channel-source-d11-0041-20261024.md)与其[source-check](../../analysis/uart-channel-source-d11-0041-20261024/source-check.json)|六个近名 LHAL API 操作及有界默认可见 C/H 符号检索，未找到同层 RTOS 实现|局部独立阅读六函数和声明；不重跑 D11 全候选检索。只新增阅读被 deinit/detach 调用的同文件 mask 实现|
|D09/D10 所引用旧 complete、最终 ZIP、SIM 替代与早期反编译|既有复用及证据分类已经留存|直接继承：SIM 不认证 ROM 驱动来源，早期名称不补 ABI，未命中不等于此前从未分析；不再解包或建机械账|

## 继承的结论

`a00288de` 在同步门内选择 `62fc6048[0..2]` 首个零 byte，置 1 后 sign8 返回索引；它不是堆 handle 构造。`a01b5c48(channel)` 只在相同 busy byte 非零时清零、post，再解锁；caller 不消费其返回值。`a00198bc(dev)` 在既有型号/private+e/channel 门内先 stop、再 release busy、最后发布 0x0f。D10 的 type 读取 `9900/992e/9942`、channel 读取 `9908/9916/9922/9932` 及 `9948` 写回直接继承，不能合并 snapshot。

原 stop 为 index→handle 包装，候选 API 为 `struct bflb_device_s*`。软件 slot 归还、固定 LLI pool、callback/pair、硬件寄存器是不同对象。busy 归还不证明 callback 注销、pair free、硬件排空或物理发送完成。以上均为旧合同，本轮不重新验收其原字节。

## 本轮复核或纠正

候选根 `D:/Documents/PlatformIO/Projects/bouffalo_sdk` 只读。下列行号为本轮实际源文本定位；脚本和结果见 [review.py](../../analysis/uart-channel-source-review-d12-0041-20261024/review.py) 与 [review-results.json](../../analysis/uart-channel-source-review-d12-0041-20261024/review-results.json)。

|D11 主张|判定|独立复核及支持范围|
|---|---|---|
|UART deinit/disable 与 lower shutdown 不同层|接受|`drivers/lhal/src/bflb_uart.c:141–158/179–196` 的可见 non-ROMAPI 分支从 device 取 reg_base，读 TX/RX 配置、分别清 UTX_EN/URX_EN、写回。函数体没有直接 DMA API 调用，也没有 ROM type/channel 表操作；不能代替 D09/D10 条件 shutdown|
|DMA deinit 不能代替三槽 release|接受|`drivers/lhal/src/bflb_dma.c:178–186` 返回 void，接收 device*；可见分支只有 stop(dev)→tcint_mask(dev,true)。没有软件三槽、post、0x0f 或直接 detach/free。该 void 声明不能补 ROM release 的返回 ABI|
|stop/isbusy 只支持低层局部同形|接受|同文件 `479–494/496–513` 分别清 CONFIG 的 DMA_E、返回 CONFIG bit0。该 bit 与 `62fc6048` 的 byte 不是同一对象，不计新匹配认证|
|irq_detach 不能补 ROM callback/pair 析构|接受|同文件 `562–568` 按 device idx/sub_idx 依次清候选 callback.handler/arg，再 mask；无直接 free。上列三个 deinit/disable 体无直接 detach。它的存在不提供 ROM caller、安装身份或最终 free 连接|
|mask 不隐藏可见 callback free|局部补核，支持限定接受|同文件 `515–535` non-ROMAPI 分支仅按 mask 参数置/清 CONFIG 的 DMA_ITC；无 callback 表引用、直接 free/detach。ROMAPI 分支仍委派，不能声称所有编译条件下均完成同一清理证明|
|D11 三组默认可见 C/H 检索无命中|继承，未重新运行|本轮只审阅 D11 脚本/结果的模式与范围；无命中限于既存记录，不认证忽略/隐藏文件、binary/archive/history、任意改名实现或编译产物不存在。没有全候选负搜索增量|
|候选版本/宏与 ROM 0041 对应|未核，保持未知|沿用 D07/D08 候选身份；没有 ROM 版本或构建宏证据。源码 ROMAPI 同名委派不足以认证 AP01 0041 机器码|

一处定位精度纠正：D11 `source-check.json` 六项 `lines[1]` 均落在结束 `}` 前一行；实际闭括号分别为 UART deinit **158**、disable **196**，DMA deinit **186**、stop **494**、isbusy **513**、irq_detach **568**。D11 `body()` 以 `\n}` 的换行位置计数产生该差一；提取字符串仍包含全部语句，故不影响其语义检查。D12 用括号深度定位终点，未修改 D11 文件。

这些观察支持“当前候选不足以认证该 ROM 来源”的推断，不支持“ROM 一定私有”“SDK 整体不匹配”或“ROM 漏清理”。没有发现需要修改 D09/D10 行为合同的证据。

## 本轮真正新增

只有独立局部复核、上述定位纠正，以及被调用 `tcint_mask` non-ROMAPI 可见体的范围收紧。**新增 ROM 业务功能 0，新增标准库/开源整库排除 0。** 没有重记候选身份、D07 stop 或 D09/D10 三槽行为为新增恢复。

实际执行 `python -X utf8 -B reverse/analysis/uart-channel-source-review-d12-0041-20261024/review.py`：12 项静态检查通过，定位两文件中的 7 个命名函数。只验证可见文本的必要操作、直接调用顺序和条件分支存在；未展开宏、编译源码或验证运行时硬件。未运行 D11 检索脚本，未复制源函数或创建哈希/整库清单。

## 仍未闭合的精确边

1. `a00288de/a01b5c48/a00198bc` 到原 RTOS 文件、版本、构建宏与同步包装的来源对应未认证。此为当前候选上的有界答案。
2. ROM callback/IRQ pair 最终 detach/free 的实际 caller、对象身份与释放连接仍未知；候选 detach 或 mask 不能填补。
3. pool 跨设备互斥、同步原语内部、硬件排空、RX/type>1、动态 ops 替换不属本轮；未由名称或缺少命中推断。

后续闭包需要取得原 RTOS UART/DMA 来源与版本/构建对应证据，或已有留存中新的 ROM caller 种子后再核。当前没有该种子；不建议重复同候选负检索或再复核纯重复材料。D12 对 D11 的限定来源结论复核完成；主窗口作范围验收，本报告不冒称补齐上述未知。
