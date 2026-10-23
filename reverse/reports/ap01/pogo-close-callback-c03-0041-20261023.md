# C03：PogoPin poll 关闭 callback 的计数与释放

2026-10-23；基线 `6058fb3`，分支 `codex/re-0041-c03`。状态：**关闭 callback 局部恢复，完整关闭生命周期仍部分恢复，待独立复核**。本文伪代码由分析者编写，不是原始源码。仅静态读取 ROM 和保留证据，未执行固件、连接设备或外部服务、开展缺陷验证。

## 回答与范围

`a00a3bc6` 接收 poll 对象地址，从对象首 word 取得 context，递减 context+0x198 的32位计数。递减后结果为有符号正数时直接退出；否则记录 `Done` 日志，再将 context 交给 `a008ab8a`。它没有读取 context+0 的 timer 指针，也不调用 timer 删除接口。该否定结论只适用于此 callback 及此次展开的释放封装，不能替代全生命周期证明。

本任务恢复一个 callback、一个直接释放依赖 `a008ab8a`，并核对既有初始化容器的四个 userdata/计数局部窗口；未展开 `a009fb96` 的完整 close 分派、日志函数或底层 allocator，不扩展 PogoPin/ADC/USB 状态机。

## 证据和函数合同

- [原指令证据](../../analysis/pogo-close-callback-c03-0041-20261023/instruction-evidence.json)：六窗口、每条指令地址/原字节、独立普通 RV32/RVC 解码、六条控制转移的位域解算及三个日志字符串。
- [核对脚本](../../analysis/pogo-close-callback-c03-0041-20261023/check-static.py)：只读主仓库 `roms/0041/ap01-1.0.2_0041.bin`，映射基址 `9ffff000`，仅写 C03 目录；身份沿用既有证据，不新增哈希清单。
- 初始化入口沿用 [保留初始化容器](../../analysis/factory-test-0041-20261023/retained-initializer.json)，证据 `ev_dc0e38b0f382799ea2a8e8ad7f21cefc5998b0767ecf38a58cfdebe8add167c3`。此次验证其 raw ranges 与 ROM 一致，只解释以下局部窗口。
- 四个关闭注册点、条件 fd>0 及 callback 地址沿用已验收 [C01](pogo-timer-lifecycle-c01-0041-20261023.md)/[C02](pogo-timer-review-c02-0041-20261023.md)。C03 另按 C02 精确建议将 C01 伪代码字段名改为 `observed_word_190`，不改变字段偏移或生命周期结论。

| 函数或片段 | 参数/返回 | 原指令事实 |
| --- | --- | --- |
| `a00a3bc6..a00a3c11` | a0=对象地址；业务返回值未确认，不消费返回寄存器 | `3bd0` 从 `0(a0)` 读 context 到 s1；`3bd2/3bd6/3bd8` 读、减一、写回 +198；`3bdc` 为 `blt zero,a5`，目标 `a00a3c08`。因此判定是递减后的有符号值>0，而非仅“等于0才释放”。 |
| 同 callback 释放分支 | a0=context 交给下游 | `3bfe` 调 `a008b51a`，参数 a0=4、a1=`a01c29b4` 文件名、a2=`0x1dc`、a3=`a026a828` callback 名、a4=`a01c3a10` 的 `Done`；`3c02` a0=s1，`3c04` 调 `a008ab8a`，随后返回。 |
| `a008ab8a..a008abaf` | a0=待释放地址；无已确认业务返回值 | `ab8a/ab8e` 构造 `62fc95e0`；`ab92/ab96` 遇该地址或NULL直接到 `abae` 返回。其余路径在 `aba2` 将原 a0 交给 `a002e14e`；本封装不解引用该地址。 |

callback 的入口由四个注册点的精确函数指针及局部序言共同支持；`3c10` 为返回，`3c12` 为下一序言。没有重新发现全 ROM 函数边界。所有新增窗口均为通用解码器可完整解码的普通指令，没有将保留反编译作为唯一语义依据。底层 `a002e14e` 未在本任务展开；称 `a008ab8a` 为释放封装同时沿用 [UiIFace 内存接口研究](uiiface-lifecycle-0041-20261023.md) 的既有识别，本次重新核实其过滤和调用事实。

## 对象、计数与最小伪代码

以下为偏移视图，不是完整原始结构或可编译实现：

```c
struct PollPrefixObserved { void *context; /* +0 */ };
// PogoContext: +0 timer; +8/+68/+cc/+130 为四个内嵌 poll 对象；
// +198 为此 callback 消费的32位计数。其余字段省略。

void close_callback_a00a3bc6(PollPrefixObserved *poll) {
    void *ctx = poll->context;             // 3bd0，无 container_of 减偏移
    uint32_t next = word_at(ctx, 0x198) - 1u; // RV32 运算，保留原指令行为
    set_word_at(ctx, 0x198, next);
    if ((int32_t)next > 0) return;
    log_a008b51a(4, "PogoPinMng/PogoPinMng.c", 0x1dc,
                  "pogo_pin_mng_deinit_cb", "Done");
    release_a008ab8a(ctx);
}
void release_a008ab8a(void *ptr) {
    if (ptr == (void *)0x62fc95e0 || ptr == NULL) return;
    underlying_a002e14e(ptr);
}
```

推断：+198 是已创建 poll 对象的待关闭计数，四个首 word 提供共同 owner/context 回指。这个解释有对应写入者支持，**没有据此证明每次注册成功、每个 callback 恰好执行一次、所有计数值均满足某个全局不变量**。

| 对象偏移 | 保存 ctx 的指令 | 计数读/加一/写 | 后续启动调用 |
| --- | --- | --- | --- |
| +68，ADC | `a005b154` | `b15e/b16a/b16e`：直接访问 ctx+198 | `b174 -> a009f9b6` |
| +cc，temp | `a005b196` | `b1a0/b1ac/b1b0`：直接访问 ctx+198 | `b1b6 -> a009f9b6` |
| +130，port | `a005b1d8` | `b1e2/b1ee/b1f2`：直接访问 ctx+198 | `b1f8 -> a009f9b6` |
| +8，UART | `a005b2f0` | `b2fa` a4=ctx+180，`b2fe/b308/b30a` 访问 a4+18，即 ctx+198 | `b310 -> a009f9b6` |

各窗口均在调用 `a009e4f6(loop,poll,fd)` 后增计数，并将同一 poll 传给启动函数。此处只重核参数/指针和计数指令，不认证这两个 callee 的成功合同。已验收的 deinit 提交顺序为 UART、port、temp、ADC，对应上述四对象；实际 callback 调度顺序、关闭完成时机和中间引用不由此推出。

## 恢复程度、来源和验证

事实已闭合到“对象首 word 回指 context → +198 递减 → signed<=0 分支调用释放封装”。没有消费 ctx+0；释放封装也不读 ctx+0。未知仍包括 timer 停止/删除、context 释放前的调度合同、close dispatcher 是否间接处理 timer、其他计数读写者以及所有路径的计数不变量。本任务不对这些未知构造错误输入或作缺陷结论。

callback/PogoPin 初始化局部继续按私有/来源未知逻辑管理；释放封装及下层库的可核实来源/版本此次未确认，新增开源排除为0。字符串提供厂商模块名称依据，不能独立证明源码身份。

实际运行 `python reverse/analysis/pogo-close-callback-c03-0041-20261023/check-static.py`：保留 initializer raw ranges 与 ROM 一致；六窗口共286 B完整独立解码，未解码字节0；六条分支/调用目标以原字节位域重算通过。没有运行固件、打开共享 REA 会话/数据库、修改分析模型或编译生产项目。脚本核对仅辅助呈现原指令，不替代 ROM 证据。

下一小任务建议：独立复核本 callback 的 signed 分支、四组 userdata/计数和释放封装；通过后再单独挑一个 timer teardown 入口问题，保持边界。
