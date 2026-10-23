# A10：线程适配入口独立技术复核

2026-10-23；基线 `4359c0b`，分支 `codex/re-0041-a10`。结论为 **accepted_with_scope_limits**：限定接受 [A09](thread-adapter-a09-0041-20261023.md) 的两级间接 ABI、+0x18 局部写入及条件化边界，无需纠正 A09。这里的 ABI 指原指令呈现的整数寄存器传参，不认证完整原始 ABI、对象同一性、运行时可达性或线程调度。

已读管理共同规则/A10任务书、REA 技能及 native guide；本工作树 reverse 子树、工作树/主仓库及相关祖先未发现适用 AGENTS.md。仅本任务报告和 analysis 目录新增文件；不写共享状态/数据库，不执行固件、不连接设备或外部服务、不验证缺陷，不改 ROM、模型或生产代码。没有新增哈希或复制清单。

## 原始来源与独立验证

[review-static.py](../../analysis/thread-adapter-review-a10-0041-20261023/review-static.py) 只读主仓库绝对路径 `D:/Documents/PlatformIO/Projects/cuktech-ap01-firmware/roms/0041/ap01-1.0.2_0041.bin`，按既有 `0x9ffff000` 映射；不运行 A09 collector。脚本独立拆分 load/store/branch/compressed jump/move/immediate/call 编码，核寄存器、宽度、偏移和目标，并逐槽将原 ROM 字节与 A09 留存字节比较。使用宿主 Python 和 Capstone 5.0.7；不打开 REA 会话或共享可写数据库。

本任务 [review-evidence.json](../../analysis/thread-adapter-review-a10-0041-20261023/review-evidence.json) 的 `windows[].instructions` 按 `pc` 可定位原字节/辅助解码，`independent_field_checks` 保存逐项实际值/期望值。三窗口为 `a012f946..a012f9af`（106 B）、`a0051dac..a0051dd1`（38 B）、`a0030ef8..a0031107`（528 B），合计 672 B、223 指令槽，217 普通解码与6未知厂商 word。与 A09 留存字节全部一致，60 项独立字段/来源核对通过。

边界不是此次重新发现：直接读取主仓库 `evidence/rea-0041-20261017/evidence/whole-rom-coverage-0041-20261023-initial.json` 核对 A09 三份 inventory 子集一致；保留 `ghidra-function-body-address-set` 的来源及局限，不能把 enclosing range 当作新发现的完整程序证明。共同 inventory Evidence ID 为 `ev_50cdbf92a7c9800e4d4bc140d70fa8cd1509eca7a199cfd6050d483cf7d695b2`，三个 extent Evidence ID 分别为：

- `a012f946`：`ev_e2ffad5b61861544d2ea01ef165a1fac0b25fb2d9ac733b2dc387ffe29f0fcf2`。
- `a0051dac`：`ev_337290cb345d2dd4356cb5f05ad3959abf1b6e41c8779521908a29c6438258d0`。
- `a0030ef8`：`ev_7b95a2aab54441306936f09e538348ffff4508d98189c925c64e3661ff793aec`。

## 逐项裁定与调用合同

| A09主张 | 裁定 | 原指令依据及适用边界 |
| --- | --- | --- |
| `a012f946` 入口 a0 不直接携带被消费的 userdata | 接受 | 入口前奏未消费传入 a0；`f952/f956` 以 LUI+LW 令 s1=`word(62fc6c18)`。目标对象来自该全局读取，不据此认定其创建者。 |
| 前置条件为两字节无符号比较，helper后为 signed 返回比较 | 接受 | `f95e/f962` 均 LBU，`f966` BGEU a1,a5 到 `f98a`；否则 `f96a` a0=s1，`f96c/970` 调 `a0028d1c(obj,byte_11)`，`f974` BGE a0,zero 到 `f98a`。helper功能/副作用未核；跨调用 s1 保持依赖已有标准保存寄存器约定。 |
| 第一级间接调用为 `target(entry,value)` | 接受 | `f98a` LW a5,0x130(s1)；`f98e` target==0到 `f994`。`f990` C.LW a0,0x18(s1)；`f992` a0!=0到 `f99c`，否则也到 `f994`。`f99c` LW a1,0x134(s1)，`f9a0` `8297`=C.JALR a5。实参 a0=word_18、a1=word_134，未把入口 a0 或对象地址当成 userdata。 |
| 第一级调用/诊断返回不能填成正常 return | 接受 | `f99a` C.J 到 `f97e`；`f9ae` 也到 `f97e`。`f982/986` 调 `a0019672` 后若返回，下一编码为 `f98a`。间接调用若返回则 `f9a2..f9aa` 构造 panic指针/0x92，走相同诊断。窗口内无正常返回；callee是否实际返回未核。 |
| `a0051dac` 非零入口将第二实参作为原 entry 的 a0 | 接受 | `51db4` C.BNEZ a0到 `51dc8`；`51dc8` C.MV a5,a0，`51dca` C.MV a0,a1，`51dcc` C.JALR a5。故直接非零分支是 `entry(value)`。仅条件满足时可组合成第二级调用。 |
| thunk的零入口及调用后行为 | 接受 | 零入口构造路径指针、0x37、0，并于 `51dc4` JAL `a0019672`；若该诊断返回，a0/a1已不再保证原 entry/value，不套用非零合同。`51dce` JAL `a00306b4` 不改写 a0，故 entry返回寄存器可作为后继调用 a0；该 callee语义/返回未核，未认证清理或可用返回值。 |
| `a0030ef8` 保存入参、重载及 +0x18 写入局部 | 接受，完整数据流条件化 | `30f1a` s7=a0；`30f1e/22` SW a2/a3到 s0-0x44/-0x48；`30fc0` LW a5,-0x44(s0)，`30fd2` SW a5,0x14(s7)；`30fda` LW a5,-0x48(s0)，`30ff4` SW a5,0x18(s7)。后一个重载至写入间普通指令未写 a5；早先厂商指令/栈槽/对象保持仍未获证明，不提升为无条件“原entry一定写入”。 |
| “A07创建对象就是本次全局对象”、业务consumer实收userdata、运行时启动/调度 | 未核且保持未知 | 本次未追全局写者，未解释跨厂商word值保持，未执行目标；A09本来也没有把这些写成已证明事实。未核不构成否定。 |

分析表达（不是原始源码）：

```c
// 限定字段合同，且必须实际到达该调用点：
obj = load32(0x62fc6c18);
target = load32(obj + 0x130);
entry  = load32(obj + 0x18);
value  = load32(obj + 0x134);
// 通过原分支的非零条件后，调用target(entry,value)。
// 另须target == 0xa0051dac，才可组合为entry(value)。
```

这只描述观测字段索引：`+0x10/+0x11` 为 byte，`+0x14/+0x18/+0x130/+0x134` 为 word；不认证原始类型。`a0030ef8` 完整返回/错误/其他 setup合同未复核，A07传入的 a2=`a012f946`、a3候选原entry及上游 s9不变量沿用既有有条件结论，未重新证明。

## 厂商指令、来源与恢复程度

以下六项均核原 ROM word（little endian），全部保留未知语义：`a0030fa2=04c5980b`、`a0030fa6=44c5c60b`、`a0030fce=3c0cbc8b`、`a003103a=44a8c80b`、`a0031050=44e6430b`、`a003106a=44e6580b`。尤其 `30fce` 位于 a2槽重载与+0x14存储之间；早先未知指令也阻止无条件认证栈槽及 s7/s0保持。接受原字节和普通编码事实，不给未知指令补造读写集合。

ROM字符串已直接核对：`a01c0598=pthread/pthread_create.c`、`a01bd0e4=task/task_setup.c`、`a01bba2c=panic`。这些与参数形态支持诊断/路径来源推断；未核具体 NuttX版本、逐实现等同、厂商修改范围，三核心不新增开源排除。`a0019672` 不因 panic字符串被指定为 noreturn。

恢复程度：两级字段消费 ABI及+0x18局部写入已限定验收；完整setup、六word语义、全局对象来源/同一性、运行时可达性、启动/调度、调用后清理仍未知。未扩展蜂鸣正常停机或 exited_sem关联。此次没有实质纠正项，未修改 A09。

实际验证：独立脚本通过（60项/672 B/223槽），JSON解析、报告链接存在性和 `git diff --check`通过；只运行宿主静态分析脚本，未编译生产项目。PowerShell启动仍出现 InitializeDefaultDrives提示，每次显式 Set-Location 后操作成功。Git首次暂存因主仓库 `.git/worktrees/re0041-a10/index.lock` Permission denied未执行，按用户明确本地提交授权升级后暂存成功；未修改权限或绕过限制。

下一小任务建议：只在既有 inventory/已留存引用中确认 `62fc6c18` 的一个直接写入者及该写入局部合同，限定最多三个函数；若没有明确证据则交付有界未知，不认证调度或全局对象同一性。
