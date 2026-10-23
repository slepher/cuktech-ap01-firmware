# C01：PogoPin 20 ms 轮询 timer 的创建与销毁边界

2026-10-23；基线 `7c17501`，分支 `codex/re-0041-c01`。状态：**部分恢复，停止/删除未闭合，待独立技术复核**。本文是指令事实及分析者伪代码，不是原始源码。只做静态检查，未执行固件、连接设备或服务，也未做缺陷验证。

## 本任务回答的问题

`a005a736` 创建 PogoPin context 后，在 `a005ab58` 将 `a00a805a`、周期参数20及 context 交给 `a008bc64`；返回 timer 指针存入 context 首 word。timer 创建器将 context 原样存入 timer `+0x0c`，callback 在 `a00a806a` 读回，形成可证实的双向持有关系。

已找到同一初始化容器的 PogoPin deinit 片段 `a005c8f8..a005c9e9`。它针对四个 poll 对象注册关闭 callback，**该片段没有读取 context+0 或删除该 timer**。整个已观测初始化函数和 callback 中也未找到到已知 timer delete 入口 `a008ae58` 的直接调用或相邻 AUIPC/JALR 调用。这是有界负结果；不能据此断言整个 ROM 永不停止、永不删除或有缺陷。未补造正常停机行为。

## 可定位证据

- [本任务指令与有界检索](../../analysis/pogo-timer-lifecycle-c01-0041-20261023/instruction-evidence.json)：五个原字节窗口、独立 Capstone 解码、初始化函数和 callback 的显式调用清单。
- [采集/核对脚本](../../analysis/pogo-timer-lifecycle-c01-0041-20261023/collect-static.py)：只读主仓库 ROM，不使用共享 REA 会话或分析数据库；仅写本任务目录。
- [保留的完整初始化函数](../../analysis/factory-test-0041-20261023/retained-initializer.json)：`ev_dc0e38b0f382799ea2a8e8ad7f21cefc5998b0767ecf38a58cfdebe8add167c3`，profile `bcefdee5092076e55636e077b45523e203f4b870ae7b7ab547945ed1b8162279`；包括原始范围 `a005a736..a005cc1d`、汇编及反编译。这里只验本任务窗口与有界调用搜索，不认证整函数。
- [保留的 callback](../../analysis/dock-presence-polling-0041-20261023/retained-functions.json)：`a00a805a..a00a832f`，`ev_5fd69f489ac24670f4c858f79225e681a50079c28b088bb18e6f7b999de4fa59`，profile `b6368dd18431e8113aa5026c713d41e648ab0f6ddd9421ff6c4a49e23b3cd2f3`。
- [已有 timer 注册摘录](../../analysis/dock-presence-polling-0041-20261023/timer-registration-source.json)及[已有功能说明](dock-presence-polling-0041-20261023.md)。

ROM 只读入口为主仓库 `roms/0041/ap01-1.0.2_0041.bin`，VA 映射基址 `0x9ffff000`。本任务不另建哈希清单；原件身份沿用上述保留证据。

## 核心函数及指令事实

| 函数/片段 | 参数与返回 | 已核事实 |
| --- | --- | --- |
| 容器 `a005a736`，片段 `a005cbba..cc1d`、`a005ab4c..ab6d` | 容器参数及整体返回未在本任务重认证；局部 context 位于 s2 | `a005cbca` 将 `0x19c` 传入 `a008e362`，`a005cbe6` 将返回值放入 s2。非零分支 `a005cbea` 跳 `a005aa68`，随后到注册窗口。NULL 分支日志后 `a005cc1c` 自环；不擅自改为返回失败。 |
| `a008bc64..a008bd15` | a0=callback，a1=period，a2=userdata；正常路径 a0=timer | 保存 callback 至 s3、userdata 至 s2；从 `a008bc82` 的调用取得节点指针。非零路径 `a008bccc..bcf4` 初始化字段；`a008bd0e` 返回节点。分配/链表 helper 不在本任务展开。 |
| `a00a805a..a00a832f` | a0=timer；callback 无已确认业务返回值 | `a00a806a` 从 timer+0x0c 读 context；`a00a806e` 读 context+0x190。五相业务继续沿用旧报告，本任务不扩展。 |

创建器最小布局（字段名为观察视图）：

```c
struct TimerObserved {
    uint32_t period;          // +00: a008bcd4 写入 a1
    uint32_t tick;            // +04: a008bcea 写入 a008bce2 调用的结果
    void (*callback)(void*);  // +08: a008bcd6 写入保存的 a0
    void *userdata;           // +0c: a008bcec 写入保存的 a2
    int32_t repeat_field;     // +10: a008bcce 写 -1；此处不独立证明其调度语义
    uint8_t flags;            // +14: 清 bit0，随后置 bit1，保留其他 bit
};
struct PogoContextObserved {
    struct TimerObserved *poll_timer; // +00: a005ab60
    // 其余字段不在本任务建完整结构
};
```

`a008bc64` 在 `a008bc8a` 对 helper 的返回值分支；零分支经过日志与 `a0019672` 调用后在静态布局上接到字段初始化。该异常路径及该断言接口的控制流合同不在本任务认证，故不写成可安全返回 NULL 的 API。正常路径创建成功后，注册点 `a005ab60` 原样保存返回值，下一段开始 weather 初始化；此处没有新增的成功检查。

```c
// 仅表达已核正常注册关系；不是原始源码或完整可执行实现。
ctx = alloc_like_a008e362(0x19c);
if (ctx == NULL) { log_assert(); for (;;) {} }  // 原指令片段的分支
// 中间是既有 ADC/UART poll 注册，本任务省略。
ctx->poll_timer = create_a008bc64(poll_callback_a00a805a, 20, ctx);
// 创建器正常路径：timer->callback=callback; timer->userdata=ctx; ...
// 回调：ctx = timer->userdata; phase = word_at(ctx, 0x190); ...
```

周期20是立即数事实；毫秒单位沿用已有 LV timer 接口研究，未在此重做时钟/调度认证。这里只证明 callback 能通过 timer 找回 context，不证明调用频率精度、线程串行性或 context 所有权转移。

## 停止/删除的有界检查

PogoPin deinit 片段中 s2 持续作为 context 基址，直到 `a005c9e6` 的日志调用结束，没有重新赋值。原指令依次为：

| 检查的 fd | 条件 | 提交关闭对象 | 共同关闭 callback |
| --- | --- | --- | --- |
| context+4，`a005c8f8` | signed fd > 0 | context+8，`a005c908` | `a00a3bc6` |
| context+0x12c，`a005c92a` | signed fd > 0 | context+0x130，`a005c93a` | 同上 |
| context+0xc8，`a005c960` | signed fd > 0 | context+0xcc，`a005c970` | 同上 |
| context+0x64，`a005c996` | signed fd > 0 | context+0x68，`a005c9a6` | 同上 |

四次调用目标均为 `a009fb96`；关闭 callback 地址由 `LUI a1,0xa00a4` 加 `-0x43a` 构成。表述“提交关闭”沿用现有 poll 生命周期证据；本任务只新增参数/条件/顺序核对，未恢复关闭 callback 的资源计数和释放行为。它们不能当作 timer 已经停止的证据。片段尾 `a005c9cc..c9e6` 是 PogoPin deinit 完成日志，随后进入 MiIot deinit；不能以日志名称替代 timer 释放证明。

有界搜索实际覆盖完整观测范围 `a005a736..a005cc1d` 及 `a00a805a..a00a832f`：提取 `jal ra,target` 和相邻 `auipc ra,imm; jalr ra,ra,off`，在清单中查 `a008ae58`，两者均为空。后者地址来自既有 LV timer delete 识别（见 [screen-host-lifecycle](screen-host-lifecycle-20261020.md)），此次没有认证所有 timer API 或扫描全 ROM 的别名传播。

未知包括：是否经其他 API 暂停、是否有回调或全局 timer 链销毁、context+0 在其他函数中的全部读者、最终 context 释放与 shutdown 顺序。未把“不见 delete”升级为“没有 teardown”，也未执行任何边界或错误输入验证。

## 来源、恢复程度与实际验证

PogoPin 容器及 callback 仍按私有/来源未知逻辑恢复。`a008bc64` 的布局与既有 LV timer 识别相符，但本任务没有补齐可核实开源版本或厂商修改来源，**新增开源排除为0**；该函数不因形状相似而移出覆盖范围。创建与 userdata 往返已恢复；停止/删除和最终所有权未恢复。

运行 `python reverse/analysis/pogo-timer-lifecycle-c01-0041-20261023/collect-static.py`：初始化函数和 callback 的保留 raw ranges 均逐字节匹配主仓库 ROM；五个选定窗口共578 B，全部独立解码成功；两范围的已知 delete 调用搜索为0。脚本初次扩展 callback 窗口至 `a00a809e` 时，Capstone 在 `a00a8090` 停止解码；该点超出 userdata 取回所需窗口，最终将本次独立验证边界收至 `a00a8072`。未更改解码模型，未宣称整个 callback 已由通用 Capstone 重认证。其他 callback 语义只沿用已有绑定厂商模型证据。

本任务未编译生产项目；无固件执行、实机或外部服务访问。辅助工具核对只补充指令证据，不代替 ROM。

下一小任务建议：仅恢复 `a00a3bc6` 关闭 callback 及其 context 计数/释放直接关系，判断它是否消费 context+0；若没有，再将这个断边留给独立 timer 链销毁检索，不扩展完整 PogoPin 状态机。
