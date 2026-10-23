# A14：两函数本地来源识别独立复核

2026-10-23；基线 `77d4336`；分支 `codex/re-0041-a14`。**限定接受 A13，无需纠正其核心结论。** 两个 ROM 函数的普通链表路径与本地 NuttX 12.10.0 参考逐项对应；helper 文件组织、诊断行号与后置锁计数条件确有差异。此结果只增强来源候选，不认证 ROM 精确版本、未修改开源实现或厂商修改边界，不新增开源排除。

## 范围与证据

仅复核 [A13](scheduler-source-a13-0041-20261023.md) 的 `a00272d4..a002733f` 与 `a0027340..a00273cb`，合计 248B。已读管理 A14/共同规则、REA skill 及 native guide；检查本工作树祖先及 `reverse`、`reverse/reports/ap01`、`reverse/analysis` 路径未见适用 AGENTS.md。未开共享可写 REA 会话或数据库，直接读取既存证据与 ROM 原字节。

可重读产物：[review-static.py](../../analysis/scheduler-source-review-a14-0041-20261023/review-static.py)、[review-evidence.json](../../analysis/scheduler-source-review-a14-0041-20261023/review-evidence.json)、[local-source-check.json](../../analysis/scheduler-source-review-a14-0041-20261023/local-source-check.json)。引用的 A13 [rom-evidence.json](../../analysis/scheduler-source-a13-0041-20261023/rom-evidence.json) 保留全部 91 条原编码/反汇编；[source-evidence.json](../../analysis/scheduler-source-a13-0041-20261023/source-evidence.json) 保留五个参考源文件 269 行及 Git 命令。A14 不重复复制源码或建立哈希清单。

原 ROM 只读位置为 `D:/Documents/PlatformIO/Projects/cuktech-ap01-firmware/roms/0041/ap01-1.0.2_0041.bin`；VA 映射基址 `9ffff000`。两函数连续 248B 与 A13 留存编码完全相等，指令覆盖连续、结束于 `a00273cc`。另从 ROM 重读 `a01bc0b0`、`a01bc0d0` 两个至 NUL 的字符串。24 项关键编码使用独立位域解析核寄存器、宽度、立即数及控制目标，不仅比较解码器文本；其余普通路径逐条人工核对留存指令和源码。

## 逐项复核

下面源码均位于 `Ubuntu-24.04:/home/slepher/nuttx-ap01-sim/nuttx`。表格区分 ROM 事实与参考解释；函数及字段名为分析名称。

| 项目 | ROM 原指令定位 | 本地参考定位与结论 | 处置 |
| --- | --- | --- | --- |
| 插入函数参数/字段 | `a00272d4` LBU node+`10`；`72f4` 读list.head；`7300` 读current.prev；`732c` 读list.tail。a0=node、a1=list，next/prev word位于+0/+4。 | `sched/sched/sched.h:441–447,457,470,495` 的 `nxsched_add_prioritized(tcb,list)` 对应局部角色；完整结构布局未认证。 | 接受 |
| 普通优先级入口/相等项 | `72d8` 非零到`72f4`；`72fc` BGEU current优先级,node优先级到`7310`再沿next循环。 | `sched.h:451,457–459` 与 `include/sys/types.h:85`：uint8优先级至少1；遍历时新优先级≤当前优先级。相等项被越过。 | 接受；仅普通非诊断路径 |
| 空表/头插入 | `7330..733a` 清node链接并写list.head/tail；`7304..730c` 写node、current.prev、list.head；均到`733c`返回1。`730c/7338/733a` C.SW 编码独立核为word32。 | `sched.h:470–479,495–504` 与head变更返回true对应。 | 接受 |
| 中间/尾插入 | `7322..7328` 写双链；`7314..731c` 清next、接prev与tail；到`731e/7320`返回0。 | `sched.h:485–488,510–513,447,517` 对应。只在源码预期的正常链表前提下比较。 | 接受；不认证任意别名情形 |
| helper诊断/文件组织 | `72e2/72ec` 合成a0=`a01bc0b0`，ROM字符串为 `sched/sched_addprioritized.c`；`72e8` a1=74；`72f0` JAL `a0019672`。 | 本地HEAD该独立`.c`不存在，helper在 `sched/sched/sched.h:441–518`，DEBUGASSERT在451行。不能从独立函数机器码推导参考inline宏的展开形式，也不能从文件组织差异识别历史版本/厂商作者。 | 接受差异及限制 |
| 外层签名/调用 | `a0027340`入口a0经`7354`存s1；`7372`与`7390`均JAL `a00272d4`；`73b0` JAL诊断`a0019672`。 | `sched/sched/sched_addreadytorun.c:69,87,94,100` 与 `add_ready_local(node)` 局部调用形状一致；返回a0为是否改变ready头的候选布尔值。 | 接受；诊断callee不展开 |
| 两列表与前置锁条件 | `734c/7350` 从`62fc6c18`读old；`7356` LH old+`20`；`735a` signed≤0到普通臂；`7366` unsigned old≥node亦到普通臂；否则传`62fc6c0c`插入、`7378` state=1且返回0。 | `sched.h:55–56,364,396`、`sched_addreadytorun.c:80–89`：锁定且新优先级更高才进pending。参考lockcount为 `include/nuttx/sched.h:615` 的int16。两全局只作为ready/pending候选，未认证原符号。 | 接受 |
| ready状态与返回 | `7394` callee返回0到`73c4`，`73c6` state=2；普通非零路径`73b6` node.state=3、`73ba/73be` node.next.state=2。 | `sched_addreadytorun.c:94–115` 及 `include/nuttx/sched.h:245–251` 非SMP枚举对应。普通路径a0保留callee的0/1。 | 接受；不延伸诊断返回合同 |
| 后置锁条件差异 | `7396` LH old+`20`；`739a` C.BNEZ直接到诊断`73a2`；计数为0才读node+`0c`并以`739e` signed>0跳过诊断。 | `sched_addreadytorun.c:100` 使用 `!nxsched_islocked_tcb(old)`；`sched.h:396` 定义islocked为>0，故其否定允许≤0。ROM要求计数**等于0**，参考条件允许**≤0**。前置分流本身均用>0，不应混为一项差异。 | 接受；仅静态条件比较，未执行负值输入 |
| pid条件/空hook | `739c/739e` 的word读取及signed>0；`73b6..73c2` 状态更新后无额外call。 | `sched.h:74` 使用 `pid<CONFIG_SMP_NCPUS`；若NCPUS=1则与ROM条件相容。`include/nuttx/arch.h:992–994` 默认空up_update_task能解释无call，不能推为厂商删hook。 | 接受条件性对应；配置未核 |
| 外层诊断行号 | `73a2/73ac` 合成a0=`a01bc0d0`，字符串 `sched/sched_addreadytorun.c`；`73a8` a1=98；`73b0`到`a0019672`。 | 参考为 `sched/sched/sched_addreadytorun.c:100`。路径层级/行号有别，预处理、原构建路径、源码版本均未知。 | 接受；两行差不定版本 |

优先级为0时的诊断调用尚未恢复返回/寄存器合同；后置诊断同样可能改变a0等调用者保存寄存器。本次不把诊断返回接入普通算法证明完整等价，也不判断诊断是否会返回。未将宿主SIM结构布局套给ROM，没有核ROM整个配置或全部struct偏移。

## 本地版本与来源边界

独立重读本地WSL树，七项Git命令的退出值/标准输出与 A13 留存完全相同：HEAD=`6fc5b3e9dc51dcda46d99519f72b7f2ec6db2e64`；exact tag=`nuttx-12.10.0`；浅克隆=true；本地仅 `nuttx-12.10.0` 与 `nuttx-12.10.0-RC0` 标签。五个指定文件的 `status --short` 和 `diff HEAD --exit-code` 均空；独立helper路径 `git ls-tree` 无结果。重新逐行读取五文件269行，与留存路径/行号/文本全部一致。此处版本认证针对**当前本地参考树**，没有远端访问或来源签名验证，不能扩展成上游真实性或ROM来源认证。

逐项结果均为接受，核心纠正为0；未核事项是ROM精确版本/提交、历史helper移动、差异由上游还是厂商引入、完整构建配置/结构布局、诊断内部及返回合同、正常上层能否出现负锁计数、运行时调度与当前对象同一性。参考源码注释中的调用者临界区/移除原列表等前提，不等于已证ROM所有调用者遵守。**不可凭sched路径或同形排序算法排除开源，也不可把未认证差异称为已证厂商修改。** 恢复程度仍为两个函数来源部分识别。

## 实际验证与交付

执行 `review-static.py`：只读248B、91条留存编码全量匹配、连续覆盖及2处原字符串通过；24项独立位域检查通过。执行 `review-static.py --local-source`：7项本地Git记录、5文件269行全部通过。人工核对上述匹配表的普通链表写入、状态/返回、两处诊断、锁条件和来源限制。脚本语法、JSON可解析、报告相对链接及 `git diff --check` 纳入提交前检查。

首次WSL只读命令被sandbox拒绝，返回 `Wsl/E_ACCESSDENIED`；按已授权本地源码读取范围升级固定读取后成功，未改权限。PowerShell初始化驱动提示不影响显式Set-Location后的操作。没有运行SIM/固件、连接设备/外部服务、下载、异常输入/缺陷验证或修改ROM/模型/生产/安全检查；没有扩大调度器或版本追溯。

首次精确暂存四个独占文件被sandbox拒绝，Git `index.lock` 返回Permission denied；依用户本地提交授权升级同一四路径暂存，再核暂存名单/差异后提交，未修改权限或绕过限制。

后续建议：来源差异保留为有界未知，无需继续搜NuttX版本；可按管理计划转Weather五槽订阅的一个具体注册调用者及其callback首个数据消费点，先查既有报告避免重复。本任务未对该后继范围开展分析。
