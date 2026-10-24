# P-11：设备摘要 callback 的选择、去重与双端交替

**可独立使用阶段已闭合但接口未闭；待非作者复核。** 已恢复 `0xa00ad602(timer)` 从五槽门控、单端 FA/FB 去重、双端 F8 交替到 widget/helper 输出调用及本层返回的合同。可实现该选择阶段，但 `0xa00abbf6` 内实际设备摘要数据消费/输出、timer 后续活性和应用生命周期仍未闭。五槽不是五个轮转候选；本 callback 仅按前两槽分派。

认领 P-11；基线 `5bbc331ab429fb76e956e50b8081c56f8d278b11`，独占树 `.worktrees/batch-20261024-p/p11`，只写本报告和同名 analysis。已读主树 reverse-design、管理顶部 P/P-11 行及 P-07/P-R07；不修改主树或他人成果，不接后继或创建代理。使用 [REA skill](C:/Users/cogic/.agents/skills/reverse-engineer-anything/SKILL.md)，留存优先、原 ROM 离线静态；未打开/切换共享会话、执行固件/设备/网络/模型/SIM/QEMU/回放/构建，未改 ROM、生产、配置或分析器，未提交推送。

预估单任务约30分钟，可收敛提前交付。首次可得 UTC `2026-10-24 14:29:55`；实际结束、墙钟及用量口径见文末。

## 继承结论

- [P-07](D:/Documents/PlatformIO/Projects/cuktech-ap01-firmware/reverse/reports/ap01/offline-summary-p07-0041-20261024.md)及[P-R07](D:/Documents/PlatformIO/Projects/cuktech-ap01-firmware/reverse/reports/ap01/offline-summary-review-pr07-0041-20261024.md)已限定接受：S 是 child0 包装对象中的业务上下文；构造 `create(ad602,3000,S)`，句柄存 S+f4。离线尾清当前槽后，五槽低8位和非零时同步 call ad602；两路之后均重读 timer 并条件 pause，然后 SH0 清 S+fa/+fb。这里不重复验收上述离线阶段。
- 主树 `reverse/rehost/system-complete-0041.json#/native_semantics/Power_bottom` 已知3秒互斥轮换；本轮不重计这一概念。该旧文件对 ad602 只有概念说明与 ad486 末端地址，不提供本轮完整状态/参数合同；旧 SIM 四端候选泛化也不等于原五槽 ABI。
- 原件沿主树 `roms/CATALOG.md`：0041，`roms/0041/ap01-1.0.2_0041.bin`，6,769,704B，SHA256 `972db4c136c7ed9e24a83c07c1a7fd62040ca018b08ca285216d26b1fee3c6b9`，RV32 little-endian，`offset=VA-0x9ffff000`。未另建全件哈希账。

## 本轮复核或纠正

唯一业务函数留存来源是主树 `evidence/rea-0041-20261017/evidence/whole-rom-private-20261023.evidence.json#/records[parameters.procedure="0xa00ad602"]`，Evidence `ev_9a7754188b853599f5646fcd698e04fa0a888175362857916605f5ae6e3478f0`；实际 profile 为 Ghidra12.1.4 / `RISCV:LE:32:ap01thead2`，digest `b6368dd18431e8113aa5026c713d41e648ab0f6ddd9421ff6c4a49e23b3cd2f3`。既有 body 为 `ad602..adabb`、1210B；本轮仅借用必要片段，未重导整函数。

针对派发提示的不可达限制，检查该实际 record 的 raw_result 与 normalized pseudocode：**没有 unreachable 警告**。不将父级其他函数的警告移植至此，也不据无警告宣称完整控制流已证明。保留原留存关于间接边、静态分析、ABI/厂商指令的局限；profile 的泛用 RISC-V 局限文字不覆盖实际私有模型身份。

`ad65a` 原字 `0b482d81` 对应留存 `th.lrbu a6,s10,s2,0`。本轮核 rd=16、base=26、index=18；只读原 profile 绑定的主树 `evidence/rea-0041-20261017/ghidra/Ghidra/Processors/RISCV/data/languages/ap01thead2.sinc:6410`，模型表达为 `zext(u8[rs1+(rs2<<shift)])`、不写回 base。配合 `ad64c` s10=S+101、s2=0..4，得到五槽无符号byte读取。这里是原字/私有模型源交叉核对，不冒称独立证明厂商 ISA，也没有执行/修模型。

本轮需保留的不对称：仅 C1 槽值4时，`ad784→ad788→ad78c` 实际调用 **`abbf6(S,2,1,0)`**；仅 C2 槽值4时，`ad8f6..8fc` 调 **`abbf6(S,4,1,1)`**。原伪代码已有这一行为，不能为“对称合理”改成统一原槽值。不是 P-07 的行为更正。

## 真正新增：可实施选择阶段合同

以下名称为说明用别名，伪代码不是原源码。`H(mode,on,k)=ad486(S,mode,on,k)`，`A(widget)=d8f7c(widget,1)`，`U(code,bank,k)=abbf6(S,code,bank,k)`。H/U 均保留原 helper 边界；本题不认证 U 内数据消费与物理显示成功。P-07已验的 H 隐藏分支直接继承；本题新增表中的 H 开启动作保留实参，不把它简写成一个无副作用的可见位写入。

### 输入、五槽门与本地布局

`ad61e` 令 `S=load32(timer+0xc)`；无 NULL/错误返回门。先日志，再对 S+101..105 逐槽读取、日志，逐次 AND255 求和。日志和 helper 之间可能有副作用，因此不是原子快照。非零和之后才重新 LBU S+102 与 S+101，记 `C2`、`C1`。

| 偏移 | 此 callback 的本层读写合同 |
| --- | --- |
| +101..105 | u8 五槽，只读；低8位和为门；只有 +101/+102 决定下面分派 |
| +f8 | u8 双端下一次选择；<=1 选C1、2选C2、>2本次不选；正常选择后写2/1 |
| +fa | u8 单端当前组合编号；双端以 SH 连同FB写0909 |
| +fb | u8 上一次单端已输出组合；单端相等则跳过 H/U；U返回后写组合编号 |
| +f9 | 已识别单端分支在共有尾SB0，含去重跳过；空和、双端、未识别返回路径不由本层清它 |

和为0（`ad680→ada82`）依次 `A(S.wordbc), A(S.worde4), H(1,0,0), H(1,0,1), H(0,1,0)` 后返回；本层不改F8/F9/FA/FB，不调用U。不能把求和替换成逻辑OR：例如多个byte和回绕为0会走此门，虽然正常业务枚举通常不会回绕。

和非0而C1/C2都0时，沿仅C1分支的无匹配出口返回。+103..105单独非零因此**不会成为第三至第五轮转候选**。本层未写这些槽、没有循环寻找其他端口。

### 单端输出与 FA/FB 去重

C2=0 时只认 C1 的1/2/3/4；C1=0且C2!=0时只认 C2 的1/2/3/4。下表先写FA=编号，再比较此前LBU FB；相等只清F9返回。不同才执行表列H/A顺序、U，随后SB编号到FB、SB0到F9并返回。

| 单端槽值 | FA/FB编号 | U(code,bank,k) | 输出前动作序列 |
| --- | --- | --- | --- |
| C1=2 | 1 | (2,2,0) | H(0,0,0), H(2,1,0), A(e4), H(1,0,0), H(1,0,1) |
| C1=1 | 2 | (1,2,0) | H(0,0,0), A(bc), A(e4), H(1,1,0), H(1,0,1) |
| C1=4 | 3 | **(2,1,0)** | 同C1=2的动作序列 |
| C1=3 | 4 | (1,1,0) | 同C1=1的动作序列 |
| C2=2 | 5 | (2,2,1) | H(0,0,0), A(bc), H(2,1,1), H(1,0,0), H(1,0,1) |
| C2=1 | 6 | (1,2,1) | H(0,0,0), A(bc), A(e4), H(1,0,0), H(1,1,1) |
| C2=4 | 7 | (4,1,1) | 同C2=2的动作序列 |
| C2=3 | 8 | (1,1,1) | 同C2=1的动作序列 |

其中 A(bc/e4) 表示先读对应 S.word 槽再调用。C2=2的编号5来自五槽循环结束的 s2=5（跳过了ad690的 s2=2），并非本分支重新装入5；这是状态寄存器数据流，不可按邻近代码猜值。单端其他槽值直接返回，没有本层FA/FB/F9写入或U。FB是输出去重latch，不是遍历五槽的游标；连续相同单端tick不会再次U更新。

### 双端交替

当重新读取的 C1!=0、C2!=0，不要求两者先是合法枚举，`ad94e/952` 以 SH写 `0x0909` 到S+fa（FA=9、FB=9），然后 `H(0,0,0)`，再LBU F8。

| F8入口 | 选择与后续 |
| --- | --- |
| 0或1 | 选k=0，下面公共动作后重读C1；U合法时调用；接着将 `"C1"` 送 `a0091b3a(S.worda4,0xa01c3bd8)`、`a0091b3a(S.wordc0,同串)`；写F8=2返回 |
| 2 | 选k=1，下面公共动作后重读C2；U合法时调用；接着将 `"C2"` 送 `a0091b3a(S.wordcc,0xa01c3bd4)`、`a0091b3a(S.worde8,同串)`；写F8=1返回 |
| >2 | 直接返回；FA/FB已是9且H(0,0,0)已执行，不自修F8、不清F9 |

公共动作顺序为 `A(bc), H(1,0,0), A(e4), H(1,0,1)`，随后**读选中槽**调用 `H(slot,1,k)`，再次**重读该槽**后判值：1/2调用 `U(slot,2,k)`，3/4调用 `U(slot,1,k)`，其他值不调用U，仍更新标签并切换F8。不能合并这两次槽读，也不能先验证合法值而跳过原H调用。字符串原字为 `43320000 43310000`，本题不下探公共label/formatter。

双端没有单端FA/FB去重门，每个正常tick都选择一端并切换F8；本层不写F9。输出helper返回不做成功判断；FB或F8写入只代表本层顺序推进，不是显示成功确认。

### 与 P-07 离线同步 call 的组合

普通周期调用和 `ae3ae` 离线直接call进入完全相同的ad602，本 callback 内不读timer暂停bit，不区分调用来源、不pause/resume/delete timer。离线调用可当场推进F8、触发单端重输出或空门控件更新。根据已接受P-07，返回后两路条件pause，随后SH0清FA/FB；因此单端callback刚写的FB不会成为该离线尾段最终latch，而F8/F9仅按本callback实际分支变化，P-07尾段不清这两byte。不能把普通tick的去重状态直接当作离线尾最终状态。

所有对象均来自既有timer/S/widget；本层无分配、free、timer删除或源对象所有权转移，未保留调用方栈view。没有显式错误、超时、取消返回合同；callback使用void式业务结果，寄存器返回值不作为显示成功。S/widget有效性、并发串行和U是否持有任何内部指针仍非本题证明范围。

新实现策略另列：可以用自有UI与timer适配实现此选择阶段，保留上述重读/状态更新顺序；若产品希望五端轮转、每tick刷新单端数据、自动修复F8或把C1=4统一传4，均属新产品策略，不可标为原ROM合同。

## 实际检查、差集与未闭精确边

[verify.py](../../analysis/summary-rotation-p11-0041-20261024/verify.py)读取原ROM与原始留存，不运行旧脚本或目标模型；产物[evidence.json](../../analysis/summary-rotation-p11-0041-20261024/evidence.json)、[checks.json](../../analysis/summary-rotation-p11-0041-20261024/checks.json)。PASS：15稀疏窗574B/188条、86个目标/operand检查，另核标签原字、长度、profile及record不存在unreachable警告。标准指令使用本地Capstone核助记符/分支目标；完整寄存器参数与顺序仍为人工静态复核，不是全数据流形式证明，不代替非作者验收。

供新非作者合并验收的差集：五槽门与只分派前两槽、FA/FB八种组合及单端去重/F9、C1状态4的不对称U参数、F8<=1/2/>2三分支与0909、双端两次重读/无效值仍标签切换、标签与widget槽、普通tick和已验P-07尾状态组合。P-07构造/暂停/尾SH及旧3秒互斥概念直接继承，不重验公共timer/LVGL。

唯一建议后继种子为 **`ad78c/ad9bc/ada4c→0xa00abbf6(S,code,bank,k)` 的实际设备摘要消费与输出**，建议20–30分钟；先由管理查重登记。主树 `whole-rom-owner-ledger-20261023.json#/functions[address=0xa00abbf6]` 只保留 inventory Evidence `ev_50cdbf92a7c9800e4d4bc140d70fa8cd1509eca7a199cfd6050d483cf7d695b2`，dossiers/source_paths/historical_contracts均空；本次没有把地址存在当成已恢复helper。后继应只追其必要私有数据借用/设备摘要字段，止于公共输出API，不扩formatter内部或底座协议。若新取证需REA且无法隔离，报告管理，不能切共享会话。

仍未知：U内部数据ABI/持有/失败、H开启分支的额外布局副作用、全部字段writer与槽值来源、timer resume/restart/销毁与事件活性、并发、最终物理显示及应用退出。H调用实参已闭不等于这些下层接口闭合；本轮未新增完整函数体恢复。

结束 `2026-10-24 14:35:41 UTC`，从首个可得时间计墙钟约5分46秒；问题收敛提前交付，不用墙钟冒充有效工时。工具/进程时间计入墙钟，无主动等待或任务中断；token由父窗实测统计，本任务不可得，不估算。最初两次登录PowerShell覆盖cwd，仅只读未命中，随后login=false纠正；错误目录没有写入。最终两JSON解析、三条相对引用、尾空格/换行及独占路径检查通过；产物仅本报告、verify.py和两份本地忽略JSON。作者自核不替代非作者接受，交付后停止。
