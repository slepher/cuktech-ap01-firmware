# C02：PogoPin timer 创建与 deinit 窗口独立复核

2026-10-23；任务分支 `codex/re-0041-c02`，基线 `ff270d3`。结论：**在限定范围内接受 C01，附一处字段命名澄清；停止/删除仍未恢复**。这是分析者伪代码及指令解释，不是原始源码。没有执行固件、连接实机/服务或开展缺陷验证。

本次只复核 C01 的三个核心函数：初始化容器 `a005a736` 的既有局部窗口、timer 创建器 `a008bc64`、callback `a00a805a` 的 userdata 读取入口。未开展新的生命周期逆向；没有改写 C01 或共享索引。

## 证据与方法

- 被复核报告：[C01](pogo-timer-lifecycle-c01-0041-20261023.md)，及其 `reverse/analysis/pogo-timer-lifecycle-c01-0041-20261023/instruction-evidence.json`、`collect-static.py`。
- 本次独立验证：[review-static.py](../../analysis/pogo-timer-review-c02-0041-20261023/review-static.py)、[review-evidence.json](../../analysis/pogo-timer-review-c02-0041-20261023/review-evidence.json)。直接只读主仓库 `roms/0041/ap01-1.0.2_0041.bin`，沿用 VA 基址 `9ffff000`，未复制 ROM 或新增哈希清单。
- 初始化容器保留证据：`reverse/analysis/factory-test-0041-20261023/retained-initializer.json`，`ev_dc0e38b0f382799ea2a8e8ad7f21cefc5998b0767ecf38a58cfdebe8add167c3`。
- callback 保留证据：`reverse/analysis/dock-presence-polling-0041-20261023/retained-functions.json` 的第二个函数，`ev_5fd69f489ac24670f4c858f79225e681a50079c28b088bb18e6f7b999de4fa59`。

核对原 ROM 字节及五个局部窗口的普通 RV32/RVC 解码；负搜索另用原字节手工位域解析 JAL、C.JAL、C.J 以及相邻 AUIPC/JALR，不依赖 C01 的调用正则。全范围指令地址来自保留汇编，逐条检查地址连续及编码长度；**没有重新发现整个函数边界或重新认证厂商扩展指令语义**。局部创建关系的人工解释仍以原始指令为依据，脚本结果只是核对材料。

## 逐项验收

| C01 项目 | 判定 | 原指令与含义 |
| --- | --- | --- |
| context 分配和失败路径 | 接受局部事实 | `a005cbca` 将 `0x19c` 放入 a0，`a005cbe2` 调 `a008e362`；`a005cbe6` 保存 a0 到 s2；`cbe8` 零分支至 `cbee`，非零经 `cbea` 跳 `aa68`。`cc1c` 为原地跳转，不能替换为返回失败。分配 helper 内部未复核。 |
| 注册三参数及返回保存 | 接受 | `a005ab4c/ab54` 构造 a0=`a00a805a`，`ab50` a2=s2，`ab52` a1=20，`ab58` 调 `a008bc64`，`ab60` 将返回 a0 写入 `0(s2)`。没有局部返回值成功判断。 |
| 创建器字段与返回 | 接受正常路径 | `bc72` s3=a0，`bc80` s2=a2，a1 经栈保存/取回；`bc82` helper 返回非零时 `bc8a` 跳 `bccc`。`bcce` 写 +10=-1，`bcd4` 写 +00=period，`bcd6` 写 +08=callback，`bcea` 写 +04=另一个调用结果，`bcec` 写 +0c=userdata；`bcdc` 清 +14 的 bit0，`bcf4` 置 bit1；`bd0e` 返回 s1。 |
| userdata 读取 | 接受 | callback 入参 a0；`a00a806a` 读取 `0x0c(a0)` 到 s1，`806e` 读取 `0x190(s1)` 到 a5。因此 ctx 首 word 与 timer userdata 构成双向指针关系；不推出所有权或调度串行性。 |
| deinit 四个注册 | 接受调用层事实 | `a005c8f8/c92a/c960/c996` 分别读 s2 的 +4/+12c/+c8/+64；紧随有符号 `bge zero,a5` 跳过注册，故调用条件 fd>0。a0 分别为 s2+8/+130/+cc/+68；a1 均由 `a00a4000-43a` 得到 `a00a3bc6`；`c90c/c93e/c974/c9aa` 目标均 `a009fb96`。 |
| deinit 未直接读取 ctx+0/调用已知 delete | 接受窗口限定 | `a005c8f8..a005c9e9` 没有以 s2+0 读取 timer 的指令，也没有直接到 `a008ae58` 的转移；s2 在此窗口未被指令重赋值。callee 是否间接删除 timer、是否修改相关资源未核。不能据此判定整个 deinit 无停止操作。 |
| 完整观测容器及 callback 的 delete 负搜索 | 接受有界结论 | 原字节解析覆盖 `[a005a736,a005cc1e)` 和 `[a00a805a,a00a8330)` 的保留指令边界；292/20 个可解析链接调用，无 C.JAL，无直接或相邻 AUIPC/JALR 到 `a008ae58` 的转移。这里也检索了非链接直接跳转。其他间接调用仍未知。 |

创建器 helper 返回零时，经过日志及 `a0019672` 后静态顺序进入字段写入；本次没有证明该断言函数是否返回，也不把此路径建模为返回 NULL。创建器末尾另有调用 `a0087b06`，返回值最终由 `bd0e` 的 s1 覆盖；该 callee 的行为未展开。C01 保留这些边界是适当的。

## 精确澄清与最小恢复视图

C01 伪代码中的 `phase = word_at(ctx, 0x190)` 应改为 `observed_word_190 = word_at(ctx, 0x190)`，或明确标注它只是本地分析名称。**本次原指令只证明这是一个 word 字段，没有证明它与 controller 的 `62fc4b35` phase byte 是同一状态**。这属于防止命名混淆的澄清，不否定 C01 的字段偏移或指针关系。

```c
// 只表达已验收的正常路径；不是原始源码或完整可执行实现。
ctx->poll_timer = create_a008bc64(callback_a00a805a, 20, ctx);
// create 正常路径观察布局：
// +00 period; +04 helper_result; +08 callback; +0c userdata;
// +10 signed field=-1; +14 flags=(old_flags & ~1) | 2.
// callback 入口：
ctx = timer->userdata;
observed_word_190 = *(uint32_t *)((char *)ctx + 0x190);
// deinit 窗口，对每组 (fd_offset, object_offset)：
// (4,8), (0x12c,0x130), (0xc8,0xcc), (0x64,0x68)
if (*(int32_t *)((char *)ctx + fd_offset) > 0)
    register_a009fb96((char *)ctx + object_offset, callback_a00a3bc6);
```

参数/返回合同限定：`a008bc64(a0=callback,a1=period,a2=userdata)` 的正常返回为 a0=timer；`a00a805a(a0=timer)` 的业务返回值未确认；容器 `a005a736` 的整体入参、返回及全局控制流未重认证。所谓“关闭注册”沿用 C01 引用的既有 poll 生命周期识别，本次只重新验明参数、条件及调用顺序，未验 `a009fb96`/`a00a3bc6` 的释放合同。周期立即数20已核，毫秒单位仍沿用既有 timer 研究，未重新验调度时钟。

## 未核、来源及验证结果

仍未核：timer 最终停止/删除、context 最终释放、所有 ctx+0 读者、callee/全局 timer 清理、间接调用目标、整个容器到 deinit 的完整可达路径及函数边界重发现。不能把本文的零匹配读成全 ROM 不存在停止或删除，也不能据此推导缺陷。

PogoPin 私有容器/callback 仍按来源未知处理；timer 创建器的开源来源和具体版本本次未认证。没有新增开源排除，创建与 userdata 关系验收通过，完整生命周期仍部分恢复。没有将结构相似当作来源证据。

实际执行 `python reverse/analysis/pogo-timer-review-c02-0041-20261023/review-static.py`：五窗口578 B与原 ROM 一致、独立解码与 C01 一致；两个完整保留 raw range 与原 ROM 一致；逐条长度连续检查通过；扩展负搜索匹配0。未运行 C01 写文件脚本，未写共享数据库/模型，未编译生产项目。

下一小任务建议维持 C01 建议：只恢复 `a00a3bc6` 关闭 callback 的直接字段访问与释放调用，确认它是否读取 ctx+0；不要同时扩展整个 PogoPin 状态机。
