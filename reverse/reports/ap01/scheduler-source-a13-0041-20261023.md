# A13：两个链表函数的本地 NuttX 来源候选

2026-10-23；基线 `2b0c716086c92ee14365955cb2625de76214a019`，分支 `codex/re-0041-a13`。**找到可核版本的本地 NuttX 12.10.0 语义参考：普通优先级插入、两个列表分流、状态赋值与返回含义高度对应；尚不能认证 ROM 精确源码版本或未修改实现。** ROM 的独立 `sched_addprioritized.c:74` 诊断位置和调用者锁计数后置诊断，与这份参考源码存在差异；不能直接把差异归因于厂商，也不新增开源排除。

## 范围、来源与本地检索

仅核 `a00272d4..a002733f`（108B）及 `a0027340..a00273cb`（140B），沿用 [A11](current-object-writer-a11-0041-20261023.md)/[A12](current-object-writer-review-a12-0041-20261023.md) 边界和局部合同；不研究第三个调度核心、不扩大对象运行时同一性。已读 REA skill/native guide、管理 A13 与共同规则；适用本树/祖先/reverse 路径未见 AGENTS.md。本地参考库的 AGENTS 已按读取入口检查，仅作静态源码阅读，未修改参考库。WSL 参考树及其 `/home/slepher/nuttx-ap01-sim` 祖先未发现 AGENTS.md。

入口是 A11/A12 的 `sched/sched_addreadytorun.c`、`sched/sched_addprioritized.c` 留存来源；本次直接从原 ROM 复核两个诊断实参指向的字符串，不仅沿用 inventory。只读检索已知 `D:/Documents/PlatformIO/Projects/bouffalo_sdk`、主仓库 `reverse/sdk` 和 `D:/Documents/PlatformIO/Projects/cuktech-ap01-firmware-tools/reference`，未找到两个目标源文件；SDK 目录只留有限芯片参考材料，这个有界检索不能排除其他本地目录、归档或未检索系统。

既有 [nuttx-sim 报告](nuttx-sim-20261016.md) 给出本地 WSL `Ubuntu-24.04:/home/slepher/nuttx-ap01-sim/nuttx`。本次只读 Git 核对：HEAD=`6fc5b3e9dc51dcda46d99519f72b7f2ec6db2e64`，精确本地标签 `nuttx-12.10.0`；相关五个源码文件 `git status --short`、`git diff HEAD --exit-code` 均空。仓库为浅克隆，仅有 `nuttx-12.10.0`、`nuttx-12.10.0-RC0` 本地标签，因此不靠这份不完整历史反推 ROM 年代。标签和提交依据只认证此本地参考树，不认证远端真实性或 ROM 来源。

可重读的证据为 [collect-static.py](../../analysis/scheduler-source-a13-0041-20261023/collect-static.py)、[rom-evidence.json](../../analysis/scheduler-source-a13-0041-20261023/rom-evidence.json)、[source-evidence.json](../../analysis/scheduler-source-a13-0041-20261023/source-evidence.json)。后者保存精确原路径、源码行号、源码摘录和 Git 命令/返回值；只摘五文件必要范围，没有复制整份源码或新建哈希清单。下表源码路径均相对上述 WSL 参考根目录。

## a00272d4 与参考内联插入函数

ROM 分析签名为 `int insert_local(Node *node, HeadTail *list)`，a0=node、a1=list；node+0/+4 为 next/prev word，+`10` 为 unsigned 比较 byte；list+0/+4 为 head/tail word。非零优先级普通路径返回1仅表示写 head，其他插入返回0。这些字段命名是局部解释，完整原始结构体未恢复。

参考实现是 `sched/sched/sched.h:441–518` 的 `static inline_function bool nxsched_add_prioritized(struct tcb_s *tcb, dq_queue_t *list)`，不是独立 `.c`。比较依据分别如下。

| 项目 | ROM 原指令事实 | 本地参考源码精确位置 | 判断 |
| --- | --- | --- | --- |
| 比较宽度与普通入口 | `72d4:03470501` LBU a4,`10`(a0)；`72d8:11ef` 非零跳 `72f4` | `sched.h:446` uint8_t sched_priority；`:451` DEBUGASSERT(priority>=SCHED_PRIORITY_MIN)；`include/sys/types.h:85` MIN=1 | byte 非零与参考≥1一致；诊断实现合同未认证。 |
| 相同优先级次序 | `72f8` LBU current+`10`，`72fc:63fae600` BGEU current,node→`7310`；`7310` 读current.next再循环 | `sched.h:457–459` 循环条件 next && priority<=next.priority | 普通列表中相等项被越过，参考同形；不是仅凭排序算法命名。 |
| 空表写 head/tail | `732c/732e` 读tail并判零；`7330/7334` 清node.next/prev；`7338/733a` 两次 C.SW a0,0/4(a1)；`733c` 返回1 | `sched.h:470–479` tail为空，清两链接，写head/tail，ret=true | 普通空表操作与返回对应。 |
| 前插入 | `7300/7302` 读current.prev并判零；`7304..730c` 写node/current/head，`730e` 去返回1 | `sched.h:495–504` prev为空，写tcb/next/head，ret=true | 普通头插入对应。 |
| 中间/尾插入 | `7322..732a` 写node/current/prev；`7314..731c` 接tail并写list.tail；`731e/7320` 返回0 | `sched.h:485–488` 尾插；`:510–513` 中间插；`:447/:517` 默认false返回 | 在源码预期的正常链表前提下对应，不证明任意别名/不一致列表状态完全等价。 |
| 来源位置 | `72e2/72ec` 构造a0=`a01bc0b0`，原字符串 `sched/sched_addprioritized.c`；`72e8` a1=`0x4a`=74；`72f0` 调 `a0019672` | 本地 Git HEAD 无 `sched/sched/sched_addprioritized.c`；helper在 `sched.h:441–518`，检查在`:451` | 编译来源位置明显不同；不据此认定算法是厂商改写或认证某旧版本。 |

上述诊断调用未展开；若它返回，ROM 的 a0/a1/a4 寄存器合同未知，不能将失败分支接到普通算法后推导完整等价。C.SW 两处head存储的 word32 宽度沿用A12原编码复核，本次从ROM重读的91条指令与A12逐条一致。

## a0027340 与参考非 SMP 分支

ROM 分析签名为 `int add_ready_local(Node *node)`，a0入口node，经s1保存；调用关系仅 `a0027340 → a00272d4` 两臂和未展开的诊断 `a0019672`。参考为 `sched/sched/sched_addreadytorun.c:68–117` 的 `!CONFIG_SMP` 分支 `bool nxsched_add_readytorun(struct tcb_s *btcb)`。选择它作对照是基于下列指令逐项对应，不声称恢复整个 ROM 构建配置。

| 项目 | ROM 原指令事实 | 本地参考源码精确位置 | 判断 |
| --- | --- | --- | --- |
| 原head与锁计数读 | `734c/7350` 从`62fc6c18`读old_head；`7356` LH old_head+`20`；`735a` signed≤0转普通列表臂 | `sched.h:364` !SMP且无up_this_task时this_task=g_readytorun.head；`:396` islocked=(lockcount>0)；`include/nuttx/sched.h:615` lockcount为int16_t | 类型/条件和非SMP参考一致，是字段来源候选；未认证该全局原符号。 |
| 更高优先级且锁定时 | `735e/7362` LBU old/node+`10`，`7366` unsigned old≥node去普通臂；剩余臂 `736a..7372` 传`62fc6c0c`；`7378` 状态byte=1，`737c`返回0 | `sched_addreadytorun.c:80–89` 锁定且old_priority<new_priority时add到pending，state=PENDING、ret=false；`sched.h:55–56` 两list宏 | 普通分流及返回对应；`62fc6c0c`可解释为pending列表候选，非原符号认证。 |
| 普通列表更新head | `738a/738e/7390` 把node、`62fc6c18`传给callee；非零返回后 `73b6` node状态=3、`73ba/73be` node.next状态=2 | `sched_addreadytorun.c:94–105` 插入ready头后state=RUNNING、flink.state=READYTORUN、ret=true | 普通成功路径对应；`include/nuttx/sched.h:245–251` 非SMP枚举值PENDING=1、READYTORUN=2、RUNNING=3也对应。 |
| 普通列表未更新head | `7394` callee返回0去`73c4`；`73c6`状态=2；普通臂保留0 | `sched_addreadytorun.c:107–115` 状态READYTORUN、ret=false | 对应。 |
| 更新head后的诊断条件 | `7396` LH old+`20`；`739a` **非零**进诊断；否则`739c` LW node+`0c`，`739e` signed>0绕诊断；`73b0`诊断调用 | `sched_addreadytorun.c:100` DEBUGASSERT(!islocked(rtcb) && !is_idle_task(btcb))；`sched.h:396` !islocked允许lockcount≤0；`:74` is_idle=(pid<CONFIG_SMP_NCPUS) | 有可见条件差异：ROM锁计数须**等于0**，参考≤0；负值在两者诊断条件不同。仅作静态比较，未构造/执行输入。 |
| pid条件与可省略hook | ROM node+`0c`须signed>0，且普通状态写后无额外call/明显附加写入 | `include/nuttx/sched.h:595` pid字段；`sched.h:74` 参考pid阈值为配置量；`sched_addreadytorun.c:104` up_update_task；`include/nuttx/arch.h:992–994` 未定义时为空宏 | 若NCPUS=1，pid比较对应；未认证ROM该配置/字段偏移。无额外hook指令与默认空宏可兼容，不能据缺call认定厂商删除hook。 |
| 诊断来源位置 | `73a2/73ac` a0=`a01bc0d0`，原字符串 `sched/sched_addreadytorun.c`；`73a8` a1=`0x62`=98 | 参考相对源码位置 `sched/sched/sched_addreadytorun.c:100` | 文件名同源候选但行号不同；路径缩写、代码版本、预处理/行号指示均未恢复，不能用两行差直接定版本。 |

参考结构 `include/nuttx/sched.h:564–565` 的flink/blink、`:595–602` 的pid/uint8优先级/task_state、`:615` 的int16锁计数与ROM访问角色相容。参考结构含多个配置字段；本次没有拿宿主SIM的64位布局套到32位ROM，没有编译结构偏移或认证ROM所有字段类型。ROM后置诊断锁计数差异不改变A11/A12非诊断路径局部结论，也不证明负锁计数可由正常上层状态产生。

## 来源结论、验证与未知

事实：本地参考树版本/相关文件未修改状态可核；ROM两诊断源文件名/行号可由原指令实参与原字符串核对；两个普通算法和状态/返回分支有逐项对应。推断：这两个函数可作为NuttX家族的强来源候选，12.10.0是可复查的语义参考。未知：ROM精确版本/提交、独立helper到内联的历史、诊断条件差异由上游版本还是厂商修改造成、构建配置/优化/断言宏、完整结构体布局与诊断返回合同。不能证明未修改实现，**两个函数仍不新增开源排除，厂商修改边界未认证**。

实际验证：宿主Python/Capstone5.0.7只读ROM两函数248B，解码91条且与A12全量指令记录一致；另只读两处各64B字符串上限，保留实际至NUL的原字节；人工核每项表格的原指令与五个源文件精确行号。WSL仅运行宿主源码/Git读取，没有启动SIM、执行固件、连设备/外部服务、下载、缺陷验证或改安全检查/生产/ROM/分析器模型；没有开共享可写REA会话或数据库。初次WSL只读命令遭sandbox的 `Wsl/E_ACCESSDENIED`；按已授权的本地参考读取范围升级同一操作后成功，未改变权限或绕过限制。PowerShell有初始化驱动提示，但显式Set-Location后读写成功。

恢复程度：两个函数的**本地语义参考来源部分识别**，精确来源未闭合；不是调度器恢复、对象生命周期证明或运行时执行观察。脚本语法、JSON解析/来源摘录、报告相对链接及Git差异检查纳入交付验证。小后续建议：A14独立复核本次两函数匹配表、诊断锁计数差异和“不可认证厂商修改/不可排除”的结论，仅用本次留存证据；无需扩大版本搜索。

首次精确暂存被sandbox拒绝写worktree的Git `index.lock`（Permission denied）；按用户已授权本地提交范围升级同一四路径暂存，不改权限或绕过限制。暂存后核四文件名单及 `git diff --cached --check`，仅提交本任务独占产物。
