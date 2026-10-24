# P-R07：P-07 离线汇总 / timer 应用接入独立复核

**可独立使用阶段已闭合但接口未闭；P-07 本次差集限定接受，行为纠正 0。** 接受 `0xa00adabc` 旧活动非零→新活动零路径中 `0xa00ae250` 后的 child0 状态清理、必要 widget 模式、同步业务 callback / 条件 pause 及常规更新汇合。完整 `0xa00ad602` 轮转状态机、timer 后续活性和最终退出仍未认证；本报告不接受整套离线 UI 或完整应用生命周期已经闭合。

认领 P-07 的非作者复核 P-R07，复核者 `/root/pr07` 未参与作者成果。基线实际读得 `5bbc331ab429fb76e956e50b8081c56f8d278b11`，独占树 `.worktrees/batch-20261024-p/pr07`；只写本报告及同名 analysis。已读主树 reverse-design、管理顶部 P 与 P-07 行；继承 E13、P-03/P-R02，不复核 selector/converter/滑动/公共 timer，不展开 P08/P10 或其他业务。已使用 [REA skill](C:/Users/cogic/.agents/skills/reverse-engineer-anything/SKILL.md)，复用原始留存和 ROM，没有切换共享会话/模型、执行目标或创建代理；未改作者文件、主树、ROM、生产、配置或分析器，未构建、回放、SIM/QEMU、联网、连接设备、提交或推送。

预估约 30 分钟；关键差集收敛提前交付。首次可得 UTC 开始 `2026-10-24 14:23:13`；结束与实际墙钟见文末。token 由父窗口统计，本子任务没有实测值。

## 继承结论

- [P-07 作者报告](D:/Documents/PlatformIO/Projects/cuktech-ap01-firmware/reverse/reports/ap01/offline-summary-p07-0041-20261024.md)提供本批验收差集及定位；作者 59 checks 只作为作者自核记录，本复核未运行或导入其脚本，也没有用其检查输出替代独立判断。
- [E13](D:/Documents/PlatformIO/Projects/cuktech-ap01-firmware/reverse/reports/ap01/ctk-offline-transition-e13-0041-20261024.md)提供旧非零→新零门、`app=s6`、零扩展 `u16(port-1)=s8`、详细 panel reset→SOC 和借用 view 寿命；E13 在 `0xa00ae250` 明确保留未验尾段，本题恰好承接该阶段。
- [P-03](D:/Documents/PlatformIO/Projects/cuktech-ap01-firmware/reverse/reports/ap01/deferred-refresh-p03-0041-20261024.md)、[P-R02](D:/Documents/PlatformIO/Projects/cuktech-ap01-firmware/reverse/reports/ap01/power-refresh-review-pr02-0041-20261024.md)的延后刷新/cache 边界直接继承。G05/G06 的 pause bit0 与 timer 保留语义同样仅继承公开接口，不展开库内部。
- 原件沿 [CATALOG](D:/Documents/PlatformIO/Projects/cuktech-ap01-firmware/roms/CATALOG.md)：0041，6,769,704B，SHA256 `972db4c136c7ed9e24a83c07c1a7fd62040ca018b08ca285216d26b1fee3c6b9`，RV32 little-endian，`file_offset=VA-0x9ffff000`。本次只验证长度及必要窗口，不重做整件摘要账。

## 本轮复核或纠正

直接输入为主树 `evidence/rea-0041-20261017/evidence/whole-rom-private-20261023.evidence.json#/records[parameters.procedure=...]` 的原始 assembly；三条实际记录 profile 均独立确认 `Ghidra12.1.4 / RISCV:LE:32:ap01thead2`，digest `b6368dd18431e8113aa5026c713d41e648ab0f6ddd9421ff6c4a49e23b3cd2f3`：

| procedure | Evidence ID |
| --- | --- |
| `0xa00adabc` | `ev_19e11c8fc1582881b289f2b24c2a98bbb305f7c2e57caad784442a60d1fb76e5` |
| `0xa005cc1e` | `ev_2f6c46cd278b33760dc15702309279178fd3b14a0bef128e4814088addec2866` |
| `0xa00ad602` | `ev_9a7754188b853599f5646fcd698e04fa0a888175362857916605f5ae6e3478f0` |

`0xa00ad486` 只读 `reverse/rehost/system-complete-0041.json#/local_disassembly/0xa00ad486`，其自述来源仍为 **Local Capstone5.0.7 and cached raw Ghidra evidence**。全部选窗 helper bytes 与 ROM 一致；不得把该来源改标为私有 thead2。继承的 unreachable-block 与函数覆盖局限保留。

| 验收项 | 独立检查与结果 |
| --- | --- |
| S 对象身份与索引 | 接受。`ae250..25a` 为 `child(app,0)` → child.word10 → wrapper.word4，S 留在 s9；`ae1ba` 的 s11=index+1 用于 port 位，数组加的是原 s8；helper 参数另外 `AND 0xff`，不能混成统一下标。 |
| mask 与条件 +9d | 接受。`ae26c→ae298` 绕过条件块；位成立时 widget90 flag1 后，`ae27c` **重读** byte9c，清 port 位再 SB，并置 `S+9d+index=1`。未成立不写该槽。 |
| 无条件状态清理 | 接受。`ae298/29c` 分别 SB0 到 `S+101+index`、`S+fc+index`，随后 `(S,2,0,u8(index))` → `(S,1,0,u8(index))`。 |
| ad486 必要分支 | 接受。mode2/index0、1 取 bc/e4；mode1/index0 为 a4,a8,ac,b0,b8,b4，index1 为 cc,d0,d4,d8,e0,dc，全部 flag1 添加；其他 index 返回。`(0,1,0)` 依次取54,58,4c并 call d9044 撤 flag1；未接受其他 mode。 |
| 五槽和与两种动作 | 接受。LBU 102,103,104,105,101 累加后 AND255；零调用 `(S,0,1,0)`，非零 `ae3ae→ad602(S.wordf4)` 同步调用。低8位和为门，不能替换为逻辑 OR 或非零槽计数。 |
| 两路重读与条件 pause ABI | 接受。`ae3b2→ae2ea` 和零和路径均到 `LW a0,f4(s9)`；`ae2ee` 只加载 a4=timer.word14，随后 AND/branch 只用 a4；`ae2f4→a008bd16` 前 a0 没有被重写。旧反编译省略参数不可沿用为无参 pause。bit0=0 才 pause，bit0=1 跳过。 |
| 构造桥 | 接受。`da14` s3=s2+80；`da4a..56` 构造 `(ad602,0x1000-0x448=3000,s2)`；`da5a` create 返回 a0，`da5e` 存 s3+74，即 S+f4，接着 `da62` 同 a0 pause；`da6c/74` 将 S 包在 child.word10→wrapper.word4。`ad61e` 从 timer+c 取 S，未把 app+58 的 timer 混入。 |
| 尾清理与汇合 | 接受。s4 在 adc08=62fc4000、adc36+=2c；`ae328` 的 byte0 目标是 `62fc4054+u8(index)`。`ae32c` 为 **SH0** 到 S+fa，包含 fb，发生在同步 callback 返回之后；`ae33e→adcba` 经日志到 adcc4..ccC 保存本次新状态至 `62fc403c+index`，继而 adcd0 常规更新，不直接 return。 |

纠正项：0。作者已经把无参 pause 伪代码和 helper profile 来源收紧，本复核接受其最终表述，无需修改作者成果。

## 真正新增与检查边界

本复核新增业务恢复 **0**；新增的是上述同一 P-07 阶段的非作者验收。可实施输入为 E13 已判定的离线事件、正常有效的 child0/S/widgets/timer；输出为指定顺序的状态/控件更新、必要同步业务调用及条件 pause，之后继续当前通知更新。原本地没有 NULL/创建失败/回滚门，不能补造成功、超时或错误返回合同。S/widget/timer 为既有借用对象，本阶段没有分配/free/timer 删除，不持久保存 item/view；并发、物理显示与原库调度精度未由静态证据证明。

独立源码 [audit.py](../../analysis/offline-summary-review-pr07-0041-20261024/audit.py)，产物 [audit.json](../../analysis/offline-summary-review-pr07-0041-20261024/audit.json)。仅 Python 标准库读取原 ROM 与两份原始留存；未调用 Capstone、作者脚本或指令执行模型。选定 13 窗 702B/237 条均存在于原留存，指令长度由 ROM 低位取得且每窗结束对齐；helper 原字节逐条一致。独立 **99** 项 numeric operand/width/branch/JAL 断言通过，涵盖端口位、byte/halfword store、五槽 load、两路汇合、timer 参数桥、必要 helper 槽及共享尾调用。JSON 保留每条 raw bytes、地址、原 assembly 和局部解码字段，便于再次定位。

该 stdlib 解码器只解析所需 RV32/RVC 字段，不宣称完整反汇编器或全指令语义证明；237 条不是237项完整解码验收。没有重新证明整个 callback、所有指针 writer、被调用业务内部或公共库实现。接受依据是原留存、必要 ROM 字段与人工顺序/对象流复核的组合。

## 未闭精确边

1. `0xa00ae3ae→0xa00ad602(timer)` 的完整业务轮转仍未验。已确认 userdata 是同 S，仅同步 call 不足以认证轮转。下一块真实种子可沿 `ad61e` timer+c、`ad64c` 五槽及 S+f8/f9/fa/fb 到 `ad78c→a00abbf6` 的应用参数/返回清理，止于该 callback 返回；本复核未展开，不自行接后继。
2. timer 全部 resume/restart、事件间活性、最终销毁、全体 writer/并发及常规更新的完整显示结果仍未知；本题不产生主 W 退出的新种子，不重开无种子搜索。
3. E13 + 本阶段接受不等于完整离线 UI、完整 timer 接口、应用退出或整 ROM 目标完成；P-01/P-02、P08/P10 其他问题保持各自边界。

结束 `2026-10-24 14:28:35 UTC`，从首个可得时间计算墙钟约5分22秒；收敛后提前完成，无主动等待或任务中断。工具读写/进程启动计入墙钟，没有有效工时实测，不用墙钟代替有效工时。首两次只读相对路径受 PowerShell cwd/profile 影响未命中，随后改绝对路径；没有在错误目录写入。最终产物仅本报告、audit.py、audit.json；JSON/引用/空白与独占路径检查后交付并停止，父窗口负责整合、计量和管理表更新。
