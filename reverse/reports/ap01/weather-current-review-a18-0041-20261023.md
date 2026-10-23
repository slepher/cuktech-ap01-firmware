# A18：当前天气值消费合同独立复核

2026-10-23；基线 `2400931`；分支 `codex/re-0041-a18`。限定接受 [A17](weather-current-consumer-a17-0041-20261023.md) 的正常非空 `a008ce16(arc,current)` 参数、字段、两道 equality 早退、signed 钳位顺序、改值写入/调用与返回消费合同。未发现需要修改 A17 的技术结论。验收仅覆盖本 setter 和 callback 必要切片，不表示天气 UI、arc 模块或全 ROM 已恢复。

遵循 [共同规则及 A18 任务书](rolling-management-0041-20261023.md)，使用 `reverse-engineer-anything` skill。worktree 祖先、根及目标目录未发现适用 AGENTS.md。只新增本报告及任务专属证据目录；不更改共享索引、生产代码、ROM、模型或安全检查；没有创建下级 agent。

## 证据与独立检查方法

原件只读：`D:/Documents/PlatformIO/Projects/cuktech-ap01-firmware/roms/0041/ap01-1.0.2_0041.bin`。原件身份沿用 A17 及先前 dossier 的 SHA-256 `972db4c136c7ed9e24a83c07c1a7fd62040ca018b08ca285216d26b1fee3c6b9`，本轮未重新散列或制作复制清单。地址映射仍为 `file_offset = VA - 0xa0000000 + 0x1000`。

本轮 [verify.py](../../analysis/weather-current-review-a18-0041-20261023/verify.py)独立实现位域提取，直接 seek/read 原件的 `a008ce16..a008ce8f` 完整 setter 与 `a00ab6cc..a00ab6ef` 连续 callback 切片，不调用 A17 验证器。普通指令用 Capstone 5.0.7 解码；对 signed LH/SLT、压缩字段 load/store、两道 BEQ、JAL、参数 C.MV、返回 C.JR 单独核编码。新读出的原字节还逐条比对 A17 保留的 44 条记录，全部相符。见 [instruction-review.json](../../analysis/weather-current-review-a18-0041-20261023/instruction-review.json) 的 `windows/encoding_checks/vendor_model` 与 [review-index.json](../../analysis/weather-current-review-a18-0041-20261023/review-index.json)。本轮本地证据以这些文件路径和地址定位，不冒用新 REA Evidence ID。

厂商 word 按既有只读模型 `D:/Documents/PlatformIO/Projects/cuktech-ap01-firmware/evidence/rea-0041-20261017/ghidra/Ghidra/Processors/RISCV/data/languages/ap01thead2.sinc:18–23` 核对。保留的完整构造为 `op0006=0xb & op1214=1 & op2531=33`，语义 `if (rs2 == 0) goto done; rd = rs1;`。这是本地既有模型与 ROM 编码的相互校对，没有新增外部 ISA 文献认证，也没有独立证明芯片运行时的指令实现。未打开或共享可写 REA 会话/数据库。

## 逐项验收

以下地址均可在本轮证据 `windows[].rows` 定位原字节和文件偏移；编码核验见 `encoding_checks`。

| A17 主张 | 结论 | 原指令依据与限制 |
| --- | --- | --- |
| current 是 signed 16→32 参数 | 接受 | `a00ab6cc` 原字 `0x00c51903`：opcode=3/funct3=1/rd=18/rs1=10/imm=12，即 `LH s2,12(a0)`。`a00ab6e8` 的 `0x85ca` 是 `C.MV a1,s2`，没有二次截断。weather 指针身份沿用 A15/A16。 |
| 第一参数是 context 中加载的 arc | 接受 | `a00ab6e6` `884c` 为 `C.LW a0,24(s1)`；`a00ab6ea` `ef10cef2` 的 JAL rd=ra，目标 `a008ce16`。ctx 身份与 +0x18 字段角色沿用 A15/A16。 |
| 非空 arc 进入正常体 | 接受 | 完整 setter 中 `a008ce20` 为 `C.BNEZ a0,+0x42`，到 `a008ce62`。空对象诊断臂在保留字节中，不纳入语义验收。 |
| 三个字段均为 32 bit | 接受 | `a008ce62/68/72` 分别 `C.LW a2,0x40(a0)`、`a3,0x48(a0)`、`a4,0x44(a0)`。value/low/high 是分析名；low/high 的业务身份沿用 A15/A16，signed 比较由本轮核实。 |
| 原值相等则第一次早退 | 接受 | `a008ce64` `6301b602`：BEQ a2,a1 到 `a008ce86`；此门之前未读上下限、无 value 写、无正常 update 调用。 |
| mvnez 在非零条件才移动 | 接受，依赖所引本地模型 | `a008ce6e` word `0x42e5968b`，rd=13/rs1=11/rs2=14；`a008ce78` word `0x42b6970b`，rd=14/rs1=13/rs2=11。均为 opcode=11/funct3=1/funct7=33，与模型 mvnez 一致。不是 mveqz 的 funct7=32。 |
| 先 min(high)，再 max(low) | 接受 | `a008ce6a` 是 signed `SLT a4,a1,a3`，接第一 mvnez 后 a3=`min(requested,high)`。`a008ce74` 是 signed `SLT a1,a4,a3`，接第二 mvnez 后 a4=`max(low,a3)`。步骤顺序由寄存器依赖确定。 |
| 钳位后等于 old 则第二次早退 | 接受 | `a008ce7c` `6305e600`：BEQ a2,a4 到同一 `a008ce86`；它比较最终 a4，第一次门比较原请求 a1，不能合成每次调用均更新。 |
| 仅值变更才写 +0x40 并通知 helper | 接受 | `a008ce80` `38c1` 为 `C.SW a4,0x40(a0)`，紧接 `a008ce82` JAL `a008ccd2`。正常体中 a0 未被改写，callee 第一参数仍为 arc。未恢复 helper 内部或赋予其返回语义。 |
| 返回没有统一结果；callback 覆盖它 | 接受 | 两个早退目标 `a008ce86..8e` 仅恢复栈/ra/s0/s1，C.JR ra，不写 a0；早退时 a0 保持 arc。更新路径的 a0 是 opaque helper 返回后寄存器值。callback `a00ab6ee` `c84c` 立即 `C.LW a0,28(s1)`，未先分支或保存 setter a0。 |

连续 callback 切片还显示 `a00ab6d0` 仅加载 s3，`a00ab6d4..dc` 是 range 参数选择，`a00ab6e0/e2` 调既有 `a008ce90`，然后进入当前值 setter；其间 callback 自身没有写 s2。s2 跨该调用保持的完整依据沿用 A15/A16 的 range 合同与 RISC-V callee-saved ABI，本轮不重新展开 range helper。A17 只保留两个较短 callback 窗口不构成错误，本轮连续窗口补充了可审阅上下文。

## 可读合同与返回边界

`a008ce16` 的分析接口是 `(arc_pointer, int32_t requested)`；本天气调用点 requested 限于 sign-extended int16。最小存储视图为 `arc+0x40:32 bit value`、`arc+0x44:32 bit low`、`arc+0x48:32 bit high`，不是原始结构体声明。正常路径可表示为：

```c
// 仅分析视图；不认证原始 C 函数声明。
old = load32(arc + 0x40);
if (old == requested) goto epilogue;
capped = signed_min(requested, load32(arc + 0x48));
selected = signed_max(load32(arc + 0x44), capped);
if (old == selected) goto epilogue;
store32(arc + 0x40, selected);
a008ccd2(arc);                  // opaque direct dependency
epilogue: restore_and_return(); // 此处不统一赋值 a0
```

先 min 再 max 是指令数据流事实的表达；在既有正常 low<high 合同下解释为区间钳位是推断。没有通过构造输入、边界执行或固件模拟验证。setter 本身没有统一布尔值/零/指针结果，不应建模为有稳定数值返回；调用点覆盖 a0 只证明这个 callback 不消费通常的 scalar 返回寄存器，原始 `void` 声明仍未认证。

调用关系限定为 `a00ab6ea -> a008ce16`，正常值改变时 `a008ce82 -> a008ccd2`；callback 前一 range 调用 `a00ab6e2 -> a008ce90` 仅作为上下文，未重新恢复。诊断调用地址沿用 A17，不对其语义作新增验收。

## 来源、未核项与实际验证

来源状态：A17 的 ROM 诊断字符串 `lv_arc_set_value` 与 `.../lvgl/src/widgets/arc/lv_arc.c` 支持 LVGL arc 来源候选，A18 沿用该候选；未重新读取字符串、认证准确源码版本或证明厂商未修改。没有新增已认证开源排除。天气 callback 的胶合角色沿用 A15/A16。伪代码、字段和 helper 角色名均为分析恢复物，不是原源码。

事实已核：指定原件的正常体指令、signed 位宽、参数传递、字段 offset、两道 equality 门、厂商编码与本地模型极性、调用边及 a0 覆盖。推断为 signed 区间钳位与更新角色。未核/未知：`a008ccd2` 内部角度/模式计算、间接副作用、返回值；range helper 内部本轮未复核；诊断臂返回行为；源码签名/版本；完整天气 UI、图标、对象生命周期、硬件执行行为。本轮没有纠正项；上述未核项不能据此接受。

实际执行 `python reverse/analysis/weather-current-review-a18-0041-20261023/verify.py` 通过：2 窗口、158 B、50 条指令、18 项编码检查、44 条 A17 原字节记录匹配、2 个厂商 word 按模型解释、剩余未解码 word 为 0。脚本首轮因本地 predecessor 路径层级写错失败，修正为 reverse 根后完成上述检查；该失败未触发目标代码。随后检查报告相对链接、专属文件范围和 `git diff --check`。这些检查仅为静态读取/解码/一致性核验，没有固件执行、模拟、设备/服务连接、异常输入、漏洞研究或缺陷验证。

恢复程度：A17 的正常 current setter 局部合同经独立原指令复核接受；没有新增 helper 内部恢复。一个小后继建议：单独恢复 `a008ccd2` 正常值变化更新的参数/字段/返回合同，最多一个直接依赖，继续限制在静态正常路径，不扩天气 UI 或生命周期。
