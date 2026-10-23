# B09：基础信息 callback ABI 独立复核

2026-10-23；分支 `codex/re-0041-b09`，基线 `99899e3`。只复核 B08 两个既有窗口，不扩展基础信息状态机或其他消费者。本文是静态指令恢复的验收说明，不是原始源码或运行观察。

## 结论及验收项目

**限定接受 B08，无核心语义纠正。** `a00a389c` 将节点 `+4` 送入 callback 的 a0，将所选记录指针送入 a1；若该节点的 `+0` 在调用时确为 `a00a3c8a`，则注册 userdata 的首个直接使用是 `a00a3c94` 的 `a5=a0`，随后作为日志首个可变参数。注册去重语义继续沿用 B06/B07，不据注册循环推断实际 userdata 值。

| B08 主张 | 验收及原指令定位 |
| --- | --- |
| 分派 ABI 为 a0=userdata、a1=record | 接受。`38ee` C.LW 读 node+0 至 a5；`38f0` 为零跳过调用；`38f2` C.LW 读 node+4 至 a0；`38f4` C.MV a1,s5；`38f6` 原编码 `8297` 为 C.JALR a5。原寄存器/偏移另从压缩编码字段核对。 |
| record=base+index*0x1a8 | 接受局部数据流。`38a0/a4` 读 owner 并判零；`38aa/ae` 乘法；`38c0` 读 owner 首 word 至 s4；`38ce` 得 s5。业务名 index/record 属分析命名，未证明索引来源或运行值。 |
| callback 首次使用 userdata 为 3c94 | 接受。`3c92` 是通过入口 a1 读 record+24，而非使用 a0；`3c94` 原编码 `aa87` 将 a0 复制到 a5。独立核 callback 每条写目的寄存器，仅此一条在日志调用前写 a5。保持结论截至 `3cd4` 调用前，不能扩展到日志返回后的 a5。 |
| callback 读取字段宽度与日志参数 | 接受。`3ca6/3cb4` LBU record+e/+d；`3cbc/3cc0` LHU record+6/+4；四个 C.SWSP 的源寄存器及偏移由原编码核对，见下表。字段业务类型、单位不在此次认证范围。 |
| 调用目标与字符串 | 接受调用点合同。`3cd4` 原 JAL 立即数字段独立还原至 `a008b51a`；三个字符串逐字从原 ROM 读取，并核 LUI/ADDI 取址。日志函数内部实现和原 typedef 未核。 |
| 循环取 next、结束清 record 首 word | 接受局部控制流。`38f8/fc/fe` 在 callback 返回后重读 header 首 word、加到当前节点、从+4读 next；`3900` 回 `38d6`。节点为空才到 `38d8`，按既存模型执行 word[base+offset]=0。不能推断回调对链表的其他副作用。 |
| 两个厂商 word | 接受原位域与既存模型的一致性；上游 ISA 权威认证仍未核，详见下文。 |

## 函数、局部结构与伪代码

两个窗口为 `a00a389c..a00a3903`（104B，尾 ret 起于 `3902`）及 `a00a3c8a..a00a3cdf`（86B，尾 ret 起于 `3cde`）。边界沿用 B08 保留 inventory extent，本次核连续原字节与尾指令；未宣称全 ROM 不存在其他入口或别名。`a008b51a` 仅作不透明直接依赖，不展开其实现。

```c
// 可读伪代码；所有地址、参数均为32位word投影。
// node+0 callback；node+4 userdata；record字段见下表。
if (U32(node) != 0)
    indirect_call(U32(node), U32(node + 4), base + index * 0x1a8);
// 对上式节点目标为 a00a3c8a 的条件路径：
// callback入口 a0=userdata，a1=record；返回语义未认证。
```

`a00a3cd4` 调用前的日志实参投影如下。采用寄存器及调用者当前 sp 的槽位表示，避免将未知原型补造为已证 C 声明。

| 位置 | 值及依据 |
| --- | --- |
| a0 | 4，`3cb8` |
| a1 | `a02684f0` → `PogoPinMng/UiIFaceMng.c`，`3cc8/3cd0` |
| a2 | `0xc5`，`3c96` |
| a3 | `a026a5d0` → `TestItemInfoChangeCallBack`，`3caa/3cae` |
| a4 | `a0268540` 格式串，`3cc4/3ccc` |
| a5 | 入口 userdata，`3c94` |
| a6 | U16(record+4)，`3cc0`，格式标签 V |
| a7 | U16(record+6)，`3cbc`，格式标签 C |
| word[sp+0] | U8(record+d)，`3cb4/3cba`，格式标签 Mode |
| word[sp+4] | U8(record+e)，`3ca6/3cb2`，格式标签 Dev |
| word[sp+8] | (U32(record+24)>>4)&3，`3c92/3c9e/3ca4`，port 首项，依赖厂商模型 |
| word[sp+c] | U32(record+24)&15，`3c92/3c9a/3ca2`，port 次项 |

格式串为 `UserData = 0x%lx, V = %d, C = %d, Mode = %d, Dev = %d, port = %d:%d`。参数槽位与字符串标签对应是静态解释；并未观测日志实际输出。callback 内没有可见 userdata 解引用或以其为条件的分支。`3cd8..3cde` 仅恢复 ra/s0/sp 并返回，保留日志返回后的 a0 寄存器形状；不认证原返回类型或业务返回值。

厂商字 `a00a3c9e=1447370b` 的 op=0xb、rd=a4、funct3=3、rs1=a4、lsb=4、msb=5，与既存 `ap01thead2.sinc:3324` 的 `th.extu` 摘录一致，模型将其解释为提取 bit5:4。`a00a38d8=412a500b` 的 op=0xb、rd=zero、funct3=5、rs1=s4、rs2=s2、shift=0、funct5=8，与同模型 `6596` 的 `th.srw` 一致。此次只读核对模型文本与原编码，没有修改模型，也没有把本地模型提升为新取得的上游 ISA 认证。

## 证据与实际验证

- 既有报告：[B08](basic-info-callback-b08-0041-20261023.md)；原字节/指令表及保留 extent Evidence：[instruction-evidence.json](../../analysis/basic-info-callback-b08-0041-20261023/instruction-evidence.json)。extent Evidence 为 `ev_9a05bdd8ae76e6994ac97a92a7f363d1303d76b44ffd7d7d2acd619f472e1588`、`ev_84c93d8edb9ab25626ad1db20f5fd014eab1d4df05e78b52f457d361d5b59a65`；callback body 为 `ev_0d64ebd9da37487a253776f36efd79021421859ed0b498eda428293e008e0cec`。
- 独立检查：[verify.py](../../analysis/basic-info-callback-review-b09-0041-20261023/verify.py) 只读原仓库 `roms/0041/ap01-1.0.2_0041.bin`，映射 `offset=VA-0x9ffff000`；将两个完整窗口逐指令字节/偏移与 B08 留存表核对，以 Capstone 5.0.7 RV32+C 重新解码普通指令，再独立核压缩 ABI/栈槽、无符号 load、日志常量/取址/JAL、a5 唯一写者、字符串和厂商字段/模型摘录。
- 实际执行 `python reverse/analysis/basic-info-callback-review-b09-0041-20261023/verify.py D:/Documents/PlatformIO/Projects/cuktech-ap01-firmware`：**passed**，2 窗口/190B、68 普通指令、2 厂商 word、33 项独立检查。结果：[review-results.json](../../analysis/basic-info-callback-review-b09-0041-20261023/review-results.json)。这不是仅重跑 B08 脚本；B08 文件未改。
- `git diff --check` 通过。无固件执行、设备/外部服务访问、缺陷验证或生产构建；未创建 REA 共享会话/数据库，复用留存 Evidence 并核原 ROM；没有新增哈希清单。

**事实**为原字节、寄存器/栈槽流、偏移/宽度、目标编码、字符串和可见局部控制流。**推断或模型依赖**为字段业务命名、日志解释及两个厂商字的语义。**未核/未知**为动态节点目标及列表内容、实际触发顺序、index 来源、owner 生命周期、日志内部合同、并发重入、字段业务单位和完整基础信息状态机。厂商/来源未知的代码仍纳入恢复，没有足够来源/版本识别据以排除为开源组件。恢复程度仅为两个局部合同获独立验收，模块整体仍部分恢复。

下一小任务建议：只恢复 `a00a389c` 的一个直接调用者，核 a0/index 的来源及其局部触发条件；最多调用者及两个直接依赖，不扩消费者集合或完整基础信息状态机。
