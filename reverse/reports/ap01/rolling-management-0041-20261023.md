# 0041 六路滚动管理（2026-10-23恢复）

用户最新授权恢复持续六路推进，取代历史收尾暂停与三路上限。原管理交接已归档至 rolling-task-history-0041-20261023.md。主窗口只管理，不作函数逆向或技术语义判断。环境共7席，主窗口1席，研究/复核6席。最新批次六项均已整合；后继任务经过复用筛选后启动，真实状态见运行快照。

## 共同规则

只做0041静态功能恢复；禁止执行固件、连接设备/外部服务、漏洞/异常输入/缺陷验证、修改安全检查、ROM、生产代码、构建配置和分析器模型；不推送。只写独占reverse/analysis和reverse/reports/ap01文件。只用自己的独立worktree和分支，每次shell显式workdir并在PowerShell Set-Location。其他agent同时工作，不撤销他人修改、不改主树或共享索引，不创建下级agent、不自行接后继。忽略ROM/证据/工具从主仓库绝对路径只读访问；不复制工作区，不共享可写数据库或切换全局REA。优先留存证据；若工具不能隔离则报告管理者。临时状态/日志放各自独占analysis目录。只恢复正常原程序行为，不擅自修正。

交付列问题/范围/结论、业务行为、函数地址/参数/返回/调用、必要伪代码结构体状态转换、所有权生命周期、可定位证据与原指令、事实/推断/未知、来源与恢复程度、实际静态验证、断边和一个后续闭包。伪代码不是原源码；保留调用顺序、重读、宽度/符号、返回判断、失败/清理和间接ABI。边界/厂商指令须核原字节，不仅信反编译。标准库只有来源可核实才排除，适配/回调仍恢复；不新增哈希清单/复制清单/机械重复证据。不编译项目，不运行历史回放。完成标准为原问题闭包得到有证据答案或明确可定位断边，不能缩成短helper声称完成；不设函数数量或时长配额；主体已覆盖即收缩，已无必要增量即报告已覆盖并结束。

接近提交提前报告结论、剩余验证、阻塞和后继建议。检查差异、必要验证、明确路径git add、提交、报告commit/验证/未知/干净状态后结束。主窗口作范围验收，技术验收由新独立agent。恢复成果可先整合为待复核；不得自验冒称验收。每项完成即整合补位，从启动时最新管理提交创建新树；运行任务不移动基线。语义冲突交agent；回收仅限干净且已整合worktree，分支保留。用户要求收尾即停止派发。

主仓库：D:/Documents/PlatformIO/Projects/cuktech-ap01-firmware。所有任务初始共同研究基线 ab9716e；实际启动基线为含本任务书的管理提交，在派发消息及运行表记录。

## 当前任务书



## 实际运行快照

上一批A25/D08/E07/F08/G06/H06均已整合结束。以下六项已真实启动，独立worktree基线均为fca1d5e；主窗口另计，无下级agent。

|任务|范围|状态|
|---|---|---|
|A27|cache release到payload cleanup的既有断边|准备（A26已整合872972c）|
|D09|既有DMA合同之外的channel分配/正常close/槽归还|运行中：/root/d09_dma_channel|
|E09|a00a1aa8真实正常函数边界与保存槽别名|运行中：/root/e09_ctk_caller_alias，基线3f0a7e0|
|F10|独立复核F09容量helper局部合同|准备（F09已整合e0e357d）|
|G07|event38替代work调度/归还断边|运行中：/root/g07_alternate_work|
|H07|type4 weather1正常上层离页→已知DELETE连接|运行中：/root/h07_weather1_navigation|

## 派发规则（本次用户调整优先）

先检索旧complete、最终验收、近期研究/独立复核，再按地址、调用点、callback、字段、资源和状态定位。旧路径先在当前reverse/rehost、reverse/reports/ap01、tooling和最终ZIP成员按basename/address/Evidence ID寻找。ZIP只读成员，不执行、不全解包/复制。旧round2/round4 remaining及单份pending须核父级complete；passed-in-sim仅SIM验收，不能外推ROM ABI/驱动/云端/来源。

每项先列既有出处→解释行为→证据局限→实际缺口，并区分原字节行为、旧反编译需局部核、SIM/照片/安全替代、未检到的精确边。可靠合同直接引用；仅补接入ABI/宽度符号/厂商字/对象身份/清理顺序。不可信custom0/unaff/extraout/no-return/边界具体定位，仅核必要窗口。重读原字节标旧结论复核，不算新增功能。禁止重复整函数导出、全资源提取、分类重建、PNG解码、全源码复制及机械哈希账。

报告必须分列继承结论、本轮复核或纠正、真正新增、未闭精确边。主体已有覆盖则收缩；无必要增量报已覆盖结束，由管理者决定换题。技术争议交研究/独立复核，不由管理者裁决。

## 本批已有成果→实际缺口

|任务/既有出处|已解释行为|局限与本轮真正增量|
|---|---|---|
|A25：A23/A24；pass3第1931/2048行；旧complete/ZIP复用对照|PNG session/pixel所有权及旧init调用已知|3ed71d2仅新增默认raw/free/align实际表绑定与实现；动态替换、heap/cache仍未知；A26只审新增|
|D08：D03–D07；charge/system complete服务替代|UART/DMA提交、持久描述符持有与归还合同|26f1f4f独立复核，新增功能0；channel分配到close及pool复用未闭|
|E07：charge-complete records[8]/[9]/[19]、round4、ZIP charge.h|a00f4610/a00f44e8/a00f5288旧原指令及SOC/时间/消费者已留存|bcfcb63仅补a00a1aa8调用边界；item+34/+38实际读者仍未找到，不计消费闭包恢复|
|F08：旧SIM最终验收、F07、ZIP来源|候选LVGL9.2.1匹配与差异已确认|3569ab7精度纠正：20B仅array前缀，另有list+14；enum packing不能覆盖ROM差异；新增功能/整库排除均0|
|G06：G05/G04/F06；system/settings round2b/c、page-logic[15]、ZIP timer|timer/create/resume和已恢复event主路径可继承|6c11f60/064320f仅3项尺寸/原序纠正；新增功能0；替代38 work生命周期未闭|
|H06：pass3第2653–2657行、weather-calendar-complete、H05|a00abed2/type4/ctx挂接/DELETE a00abb62早已有；文字/分类/arc/tiny消费者继承|7a8f3bc/52e61b9独立复核新增0；H05只增ABI/direct a019cbc0/显式free原序；正常离页连接仍缺|

H05/H06 type4 68B与H01/H03 type19 116B是不同对象；type19最终context释放另有断边，不套用。a019cbc0不得混同a0198946。旧SIM已覆盖weather分类/显示，不再重新恢复。

## 当前完整任务书 D09（已启动，基线fca1d5e）

问题：channel分配到正常close与槽归还。

D07/D08已覆盖描述符持有/提交/IRQ合同，继承不重做。精确种子a001a8ee→a00288de；旧优先材料按地址检索未命中不等于从未分析，先按调用者/字段别名再核。仅回答本UART路径channel如何分配、callback/pool槽何时解绑归还，正常close实际连接是否可证。硬件行为保留未知，不扩全部DMA/RX。

分支codex/re-0041-d09；worktree D:/CodexHome/visualizations/2026/10/23/01a1691a-e178-7710-86c0-84c2ff2d3dfb/re0041-d09。基线为本任务书提交（启动时最新整合提交，另记实际SHA）。独占reverse/reports/ap01/uart-dma-channel-d09-0041-20261023.md及reverse/analysis/uart-dma-channel-d09-0041-20261023/。

先交简短复用/精确缺口对照，按共同规则仅做必要静态验证。完成标准为回答本题或保留有界、可定位断边；无增量即报告已覆盖，禁止凑闭包扩扫。提交独占成果、报告验证/未知/clean后结束，不创建下级agent。技术纠正只写独占报告不改原成果。

## 当前完整任务书 G07（已启动，基线fca1d5e）

问题：event38替代work调度与状态归还。

继承G05/G06已知主路径和三项纠正，旧system/settings timer/SIM调度不再恢复。派发后交叉检索确认G05已有替代38注册/去重/clear窗口，C03/C04已有a009e4f6→a009f9b6成组初始化/启动合同，全部继承；实际范围收缩为display state+58/+60对象身份、a009f9b6到实际消费及正常归还/退出连接。优先材料按4地址无精确命中仅为检索范围事实，须再核字段/调用者/旧Evidence。未安装的hook不假定已运行，不扩所有poll/event。

分支codex/re-0041-g07；worktree D:/CodexHome/visualizations/2026/10/23/01a1691a-e178-7710-86c0-84c2ff2d3dfb/re0041-g07。基线为本任务书提交（启动时最新整合提交，另记实际SHA）。独占reverse/reports/ap01/display-alternate-work-g07-0041-20261023.md及reverse/analysis/display-alternate-work-g07-0041-20261023/。

先交简短复用/精确缺口对照，按共同规则仅做必要静态验证。完成标准为回答本题或保留有界、可定位断边；无增量即报告已覆盖，禁止凑闭包扩扫。提交独占成果、报告验证/未知/clean后结束，不创建下级agent。技术纠正只写独占报告不改原成果。

## 当前完整任务书 H07（已启动，基线fca1d5e）

问题：type4 weather1正常上层离页到DELETE连接。

继承pass3第2653–2657行注册a00abed2/type4/context/DELETE a00abb62，weather-calendar-complete全部分类文字图标合同及H05/H06。仅补H05明确缺的正常上层离页动作→本页DELETE连接，先查page-logic/knob/system/guide和ZIP现有导航证据，SIM导航不等于ROM连接。目标对象type4/68B；type19/116B不在本题，不套用释放结论。若已有足够证据仅报告覆盖；不得改题为另一个旧订阅者或全UI。

分支codex/re-0041-h07；worktree D:/CodexHome/visualizations/2026/10/23/01a1691a-e178-7710-86c0-84c2ff2d3dfb/re0041-h07。基线为本任务书提交（启动时最新整合提交，另记实际SHA）。独占reverse/reports/ap01/weather1-navigation-h07-0041-20261023.md及reverse/analysis/weather1-navigation-h07-0041-20261023/。

先交简短复用/精确缺口对照，按共同规则仅做必要静态验证。完成标准为回答本题或保留有界、可定位断边；无增量即报告已覆盖，禁止凑闭包扩扫。提交独占成果、报告验证/未知/clean后结束，不创建下级agent。技术纠正只写独占报告不改原成果。

## 当前完整任务书 E09（已启动，基线3f0a7e0）

独立树D:/CodexHome/visualizations/2026/10/23/01a1691a-e178-7710-86c0-84c2ff2d3dfb/re0041-e09；分支codex/re-0041-e09；基线为本任务书提交，启动记实际SHA。独占reverse/reports/ap01/ctk-caller-alias-e09-0041-20261023.md及reverse/analysis/ctk-caller-alias-e09-0041-20261023/。

先继承charge-complete records[8]/[9]/[19]及E01–E08，尤其E07继承对照与E08限定结论。旧消费者/SOC/时间合同不重做，14/3候选不是全集。真正问题仅为a00a1aa8→a00a53c0这个已知调用点的正常函数边界、传入索引/返回item及s0-e4保存槽身份；再判断本已知数据链是否真读item+34/+38。无法连到这两字段即保留精确断边，不继续泛扫CTK。不能以最近旧反编译入口或owner=null认证真实函数边界。

先按地址/字段/调用者/旧Evidence检索完整阶段与近期留存，给已有出处→解释行为→局限→实际缺口。已有原指令直接引用，仅补边界/ABI不可信窗口，不整函数重导、不重跑全ROM扫描，不复制源ZIP。无必要增量即报已覆盖结束，不凑闭包。报告分继承、复核纠正、真正新增、精确未闭边。完成后必要静态验证、明确独占路径提交、报告commit/未知/clean；共同安全、隔离和不创建下级agent规则适用。

## 当前完整任务书 A27（准备）

独立树D:/CodexHome/visualizations/2026/10/23/01a1691a-e178-7710-86c0-84c2ff2d3dfb/re0041-a27，分支codex/re-0041-a27；基线为本任务书提交，启动时另记SHA。独占reverse/reports/ap01/image-cache-cleanup-a27-0041-20261023.md及reverse/analysis/image-cache-cleanup-a27-0041-20261023/。

A23/A24/A25/A26已恢复session、PNG构造、默认表与raw/Pixel析构，全部直接引用；本轮只补cache release a019d9f6→引用/驱逐决策→实际payload cleanup a008abb0安装目标连接。先查A23留存及字段/回调身份，旧complete/pass3/ZIP按三地址的主窗口有界检索无精确命中，不表示此前未分析。仅追一个已知cache entry正常释放与cleanup触发条件，区分release与真实Pixel/raw free；不扩全cache/heap/PNG或解码资源。若旧留存已足则报告覆盖，不重复导出整函数。

先交简短已有出处→解释行为→证据局限→实际缺口；只补未覆盖/不可信窗口，重读bytes标旧结论复核。报告分继承、复核纠正、真正新增、未闭精确边。无必要增量即报告覆盖，不凑时长/函数。共同规则全部适用，仅静态/独占输出，无SIM/构建/回放/生产ROM配置模型修改，不创建下级agent。必要验证后提交独占路径，报告commit/未知/clean并结束。

## 当前完整任务书 F10（准备）

独立树D:/CodexHome/visualizations/2026/10/23/01a1691a-e178-7710-86c0-84c2ff2d3dfb/re0041-f10，分支codex/re-0041-f10；基线为本任务书提交，启动时另记SHA。独占reverse/reports/ap01/event-array-review-f10-0041-20261023.md及reverse/analysis/event-array-review-f10-0041-20261023/。

独立复核F09收缩后的a00ecc68 owned/宽度/返回/字段发布和caller仅测非零合同；G03–G06的重入/删除/压紧全部继承，不再导出。只核F09真正补充的必要原字节与ABI。零返回后的断言是否返回与底层realloc可保留精确未知，不开展异常输入/缺陷研究、不扩失败链或堆。新增功能0；已有证据充分可以短报告。

先交简短已有出处→解释行为→证据局限→实际缺口；只补未覆盖/不可信窗口，重读bytes标旧结论复核。报告分继承、复核纠正、真正新增、未闭精确边。无必要增量即报告覆盖，不凑时长/函数。共同规则全部适用，仅静态/独占输出，无SIM/构建/回放/生产ROM配置模型修改，不创建下级agent。必要验证后提交独占路径，报告commit/未知/clean并结束。
