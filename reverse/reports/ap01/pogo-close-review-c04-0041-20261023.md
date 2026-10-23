# C04：PogoPin 关闭 callback 独立限定复核

2026-10-23；分支 `codex/re-0041-c04`，基线 `ff34a7f`。**限定接受 C03，未发现需纠正的核心语义；完整 timer/关闭生命周期仍部分恢复。** 本文的伪代码是分析者表达，不是原始源码。仅离线静态读取原 ROM，未执行固件、连接实机/外部服务或开展缺陷验证。

## 范围、入口与证据

仅复核 [C03](pogo-close-callback-c03-0041-20261023.md) 的 `a00a3bc6`、`a008ab8a` 与四组 userdata/计数窗口，并检查 [C02](pogo-timer-review-c02-0041-20261023.md) 字段命名澄清的落实。不展开 close dispatcher、底层 allocator、timer 扫描或完整 PogoPin 状态机。

本次证据：[review-evidence.json](../../analysis/pogo-close-review-c04-0041-20261023/review-evidence.json)，生成方法：[review-static.py](../../analysis/pogo-close-review-c04-0041-20261023/review-static.py)。脚本只读主仓库 `roms/0041/ap01-1.0.2_0041.bin`，沿用 `9ffff000` 映射；仅写 C04 目录，不运行 C03 写文件脚本，不打开共享 REA 会话/数据库。REA 技能已阅读；采用既有保留证据及直接原字节核对，不新建会话。不新增哈希清单。

独立从 ROM 重解码六窗口全部普通 RV32/RVC 指令，与 C03 地址、字节、解码逐项比较；另从原编码提取 load/store 的寄存器和偏移、压缩 ADDI/访存、BLT/BEQ 的 funct3 和比较寄存器、JAL 的 rd 和目标。后者独立于反编译及 Capstone 的分支别名呈现。窗口入口/末尾序言与返回仍按 C03 的局部视图，不重认全 ROM 函数边界，不认证厂商扩展模型。

## 逐项验收

| 项目 | 判定 | 原指令依据与边界 |
| --- | --- | --- |
| callback 参数与 ctx 回溯 | 接受 | `a00a3bd0` 原字节 `0441` 为 `c.lw s1,0(a0)`；a0 是传入对象地址，ctx 是其首 word。此窗口没有按内嵌对象偏移做减法，不能把它写成 container_of。对象类型/命名沿用既有注册证据。 |
| 计数读、减、写 | 接受 | `a00a3bd2` LW 取 s1+198 到 a5；`3bd6` C.ADDI a5,-1；`3bd8` SW 写回同一 word。RV32 低32位运算；没有补造饱和、检查或全局计数不变量。 |
| signed 条件 | 接受 | `a00a3bdc` 原字节 `6346f002`：opcode=63、funct3=4、rs1=x0、rs2=x15、目标 `a00a3c08`，即 `blt zero,a5`。递减后 signed>0 跳过日志/释放；否则进入释放路径。不能改写成仅 next==0，或无符号比较。 |
| 释放参数与调用 | 接受 | `a00a3bfe` JAL 至 `a008b51a`；`3c02` 原字节 `2685` 为 a0=s1；`3c04` JAL 至 `a008ab8a`；`3c08..3c10` 为恢复寄存器并返回。callback 的业务返回值未确认。日志字符串内容沿用 C03，本轮未另重验字符串。 |
| 释放封装 | 接受局部事实 | `a008ab8a/ab8e` 构造 `62fc95e0`；`ab92` a0==该值、`ab96` a0==0 均转 `abae` 返回。其余路径保持原 a0，在 `aba2` JAL 至 `a002e14e`。本封装不解引用 a0。称“释放封装”沿用 C03 引用的内存接口研究；本轮未认证底层 allocator 或开源来源。 |
| ADC/temp/port 回指和计数 | 接受局部事实 | `a005b154/b196/b1d8` 分别把 s2 写到 s2+68/+cc/+130；对应对象地址由 `b14e/b190/b1d2` 放入 s3。各组直接对 s2+198 做 LW、+1、SW。局部 init JAL 均至 `a009e4f6`，后续启动 JAL 均至 `a009f9b6`，a0 在启动前设为 s3。 |
| UART 别名窗口 | 接受 | `a005b2e6` a2=word(s2+4)，`b2ea` s3=s2+8，`b2f0` 保存 s2 到该对象首 word。`b2fa` a4=s2+180，`b2fe/b30a` C.LW/C.SW 的偏移都是18，因此访问位置为 s2+198；`b308` 加一。init/start 目标同上，未将 a4 当作新 context。 |
| 四组的生命周期含义 | 接受为推断 | 相同 owner 回指、各组增计数和 callback 减计数支持“待关闭计数”的解释。没有核各次 init/start 返回合同、全部计数写者、callback 恰好一次或实际关闭完成顺序；ADC/temp/port 的 fd 上游来源也不在这六窗口中。 |
| C02 命名澄清 | 接受、已落实 | C01 现使用 `observed_word_190 = word_at(ctx,0x190)`，并明确不等同于 controller `62fc4b35` phase byte。C03 未将二者合并。本轮核文本落实，不重复 C02 的 timer 创建器/回调指令验收。 |

核心函数合同：`a00a3bc6(a0=poll对象)` 取对象首 word 为 ctx，消费 ctx+198，必要时把 ctx 交给 `a008ab8a(a0=ptr)`；后者过滤 NULL 与 `62fc95e0`，再调用 `a002e14e(ptr)`。两个函数的业务返回值未确认。四组窗口以既有初始化容器的 s2=context 为入口合同，本次核的是相对地址与直接参数，不重建该容器全局控制流。

## 最小接受视图与未核项

```c
// 偏移视图；非原始源码、非完整结构体。
// poll+0: ctx 回指；ctx+198: 此处增减的32位 word。
void observed_close_callback(PollPrefix *poll) {
    Context *ctx = poll->context;
    uint32_t next = read_word(ctx, 0x198) - 1u;
    write_word(ctx, 0x198, next);
    if ((int32_t)next > 0) return; // RV32 signed BLT 的解释
    observed_log_call();
    observed_release_wrapper(ctx);
}
```

**事实边界：**六窗口内 callback 的业务读取是 poll+0 与 ctx+198，另有栈恢复；释放封装没有 ctx 解引用。因此接受“callback 与已展开封装本身未读取 ctx+0 timer，也没有直接 timer 删除调用”。这不涵盖日志函数、底层 `a002e14e`、`a009fb96` close dispatcher 或其他链路，不能推出它们绝无间接 timer 行为。完整停止、删除、context 最终释放的调度时序、其他计数读写者、timer 与 context 所有权仍未知；本轮未扫描这些未知，也不推出缺陷。

来源状态：PogoPin 私有封装/callback 继续按私有或来源未知管理；底层库和释放封装本轮未确认开源出处或版本。新增开源排除为0。恢复程度只到上述局部字段与直接调用关系，不能据此宣布完整生命周期完成。

实际验证：运行 `python reverse/analysis/pogo-close-review-c04-0041-20261023/review-static.py`，六窗口286 B原字节及独立解码全部与 C03 一致，未解码字节0；43项原编码字段核对通过；C02中性命名检查通过。辅助脚本只核静态指令呈现，没有执行目标或生产构建。`git diff --check` 在提交前执行；输出范围仅本 C04 报告与 analysis 目录。

下一小任务建议：仅选择 `a009fb96` 的一个直接 close-callback 调用点，确认 a0 对象和 callback 字段的传递合同；不要同时扩大到 timer 扫描或完整 dispatcher。
