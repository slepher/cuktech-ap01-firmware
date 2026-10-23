# 0041 六路滚动管理（2026-10-23恢复）

用户最新授权恢复持续六路推进，取代历史收尾暂停与三路上限。原管理交接已归档至 rolling-task-history-0041-20261023.md。主窗口只管理，不作函数逆向或技术语义判断。环境共7席，主窗口1席，研究/复核6席。最新批次六项均已整合；后继任务经过复用筛选后启动，真实状态见运行快照。

## 共同规则

只做0041静态功能恢复；禁止执行固件、连接设备/外部服务、漏洞/异常输入/缺陷验证、修改安全检查、ROM、生产代码、构建配置和分析器模型；不推送。只写独占reverse/analysis和reverse/reports/ap01文件。只用自己的独立worktree和分支，每次shell显式workdir并在PowerShell Set-Location。其他agent同时工作，不撤销他人修改、不改主树或共享索引，不创建下级agent、不自行接后继。忽略ROM/证据/工具从主仓库绝对路径只读访问；不复制工作区，不共享可写数据库或切换全局REA。优先留存证据；若工具不能隔离则报告管理者。临时状态/日志放各自独占analysis目录。只恢复正常原程序行为，不擅自修正。

交付列问题/范围/结论、业务行为、函数地址/参数/返回/调用、必要伪代码结构体状态转换、所有权生命周期、可定位证据与原指令、事实/推断/未知、来源与恢复程度、实际静态验证、断边和一个后续闭包。伪代码不是原源码；保留调用顺序、重读、宽度/符号、返回判断、失败/清理和间接ABI。边界/厂商指令须核原字节，不仅信反编译。标准库只有来源可核实才排除，适配/回调仍恢复；不新增哈希清单/复制清单/机械重复证据。不编译项目，不运行历史回放。完成标准为原问题闭包得到有证据答案或明确可定位断边，不能缩成短helper声称完成；不设函数数量或时长配额；主体已覆盖即收缩，已无必要增量即报告已覆盖并结束。

接近提交提前报告结论、剩余验证、阻塞和后继建议。检查差异、必要验证、明确路径git add、提交、报告commit/验证/未知/干净状态后结束。主窗口作范围验收，技术验收由新独立agent。恢复成果可先整合为待复核；不得自验冒称验收。每项完成即整合补位，从启动时最新管理提交创建新树；运行任务不移动基线。语义冲突交agent；回收仅限干净且已整合worktree，分支保留。用户要求收尾即停止派发。

主仓库：D:/Documents/PlatformIO/Projects/cuktech-ap01-firmware。所有任务初始共同研究基线 ab9716e；实际启动基线为含本任务书的管理提交，在派发消息及运行表记录。

## 当前任务书



## 实际运行快照

上一批A25/D08/E07/F08/G06/H06均已整合结束。当前A28运行；A29准备。D10/E09/G08/H07/F10均已整合结束，不计运行。空席不用于重复扫描或填配额；主窗口另计，无下级agent。

|任务|范围|状态|
|---|---|---|
|A28|独立复核A27 cache连接|运行中：/root/a28_cache_review，基线6eec181|
|D10|已整合限定结论，见历史映射|结束；无必要重复取证|
|E09|已整合限定结论，见历史映射|结束；无必要重复取证|
|F10|已限定接受容量helper合同|已整合2052338，无必要重复扩扫|
|G08|已整合限定结论，见历史映射|结束；无必要重复取证|
|H07|普通主浏览切出已有覆盖；teardown断边并入E05/E06|已整合89875e2，无独立天气增量；空席待实际缺口|

## 派发规则（本次用户调整优先）

先检索旧complete、最终验收、近期研究/独立复核，再按地址、调用点、callback、字段、资源和状态定位。旧路径先在当前reverse/rehost、reverse/reports/ap01、tooling和最终ZIP成员按basename/address/Evidence ID寻找。ZIP只读成员，不执行、不全解包/复制。旧round2/round4 remaining及单份pending须核父级complete；passed-in-sim仅SIM验收，不能外推ROM ABI/驱动/云端/来源。

每项先列既有出处→解释行为→证据局限→实际缺口，并区分原字节行为、旧反编译需局部核、SIM/照片/安全替代、未检到的精确边。可靠合同直接引用；仅补接入ABI/宽度符号/厂商字/对象身份/清理顺序。不可信custom0/unaff/extraout/no-return/边界具体定位，仅核必要窗口。重读原字节标旧结论复核，不算新增功能。禁止重复整函数导出、全资源提取、分类重建、PNG解码、全源码复制及机械哈希账。

报告必须分列继承结论、本轮复核或纠正、真正新增、未闭精确边。主体已有覆盖则收缩；无必要增量报已覆盖结束，由管理者决定换题。技术争议交研究/独立复核，不由管理者裁决。

## 本批已有成果→实际缺口

|任务/既有出处|已解释行为|局限与本轮真正增量|
|---|---|---|
|A25：A23/A24；pass3第1931/2048行；旧complete/ZIP复用对照|PNG session/pixel所有权及旧init调用已知|3ed71d2仅新增默认raw/free/align实际表绑定与实现；动态替换、heap/cache仍未知；A26只审新增|
|D08：D03–D07；charge/system complete服务替代|UART/DMA提交、持久描述符持有与归还合同|26f1f4f独立复核，新增功能0；channel分配到close及pool复用未闭|
|E07：charge-complete records[8]/[9]/[19]、round4、ZIP charge.h|a00f4610/a00f44e8/a00f5288旧原指令及SOC/时间/消费者已留存|bcfcb63仅为旧body边界信息；719b38d确认round3早已完整留存该函数与保存槽，E07/E08不可外推此前分析缺失；item+34/+38读者仍未知|
|F08：旧SIM最终验收、F07、ZIP来源|候选LVGL9.2.1匹配与差异已确认|3569ab7精度纠正：20B仅array前缀，另有list+14；enum packing不能覆盖ROM差异；新增功能/整库排除均0|
|G06：G05/G04/F06；system/settings round2b/c、page-logic[15]、ZIP timer|timer/create/resume和已恢复event主路径可继承|6c11f60/064320f仅3项尺寸/原序纠正；新增功能0；替代38 work生命周期未闭|
|H06：pass3第2653–2657行、weather-calendar-complete、H05|a00abed2/type4/ctx挂接/DELETE a00abb62早已有；文字/分类/arc/tiny消费者继承|7a8f3bc/52e61b9独立复核新增0；H05只增ABI/direct a019cbc0/显式free原序；正常离页连接仍缺|

H05/H06 type4 68B与H01/H03 type19 116B是不同对象；type19最终context释放另有断边，不套用。a019cbc0不得混同a0198946。旧SIM已覆盖weather分类/显示，不再重新恢复。

## 当前完整任务书 A28（已启动，基线6eec181，2026-10-24）

独立树D:/CodexHome/visualizations/2026/10/23/01a1691a-e178-7710-86c0-84c2ff2d3dfb/re0041-a28；分支codex/re-0041-a28；基线为本任务书提交，启动另记实际SHA。独占reverse/reports/ap01/image-cache-review-a28-0041-20261024.md及reverse/analysis/image-cache-review-a28-0041-20261024/。

独立复核A27新增release引用减一/重读、失效门→cache+18(payload,NULL)→基址free与容量/victim移出→同cleanup连接。A23–A26已恢复cleanup内部和Pixel/raw析构、默认表与PNG session，直接引用不重做；旧SIM/cache配置不能证明ROM实际时序。仅核本轮新增窗口的宽度/对象别名/ABI/厂商lrw/返回和清理原序。完整排序、失效API上层业务调用者、计量单位/heap可保留精确未知，不扩全cache或PNG。

先已有→复核缺口对照，四分类交付、逐项接受纠正未核；原字节复核不计新增功能，不整函数重复导出，不凑时长/函数。技术纠正只独占报告，不改原成果。共同安全/静态/隔离/独占输出规则适用，不创建下级agent，无SIM/构建/回放。必要验证提交明确独占路径，报告commit/验证/未知/clean后结束。

## 当前完整任务书 A29（准备，2026-10-24）

独立树D:/CodexHome/visualizations/2026/10/23/01a1691a-e178-7710-86c0-84c2ff2d3dfb/re0041-a29；分支codex/re-0041-a29；基线为本任务书提交，启动另记SHA。独占reverse/reports/ap01/image-cache-invalidation-a29-0041-20261024.md及reverse/analysis/image-cache-invalidation-a29-0041-20261024/。

问题仅为A27未追的a019cfbe失效API：其正常调用者/业务触发是否实际标记同一image cache entry，及该标记如何接到既有release/cleanup合同。A23–A27 session/构造/raw/cleanup/release内部直接继承；A28在独立复核这些合同，不重叠。管理窗口已在reverse/reports/ap01、reverse/rehost、tooling和ZIP按精确地址检索，仅A27报告命中；这不代表此前未分析。执行者先查既存whole-ROM retained caller/Evidence和较晚round3、字段/调用者/别名，给已有→实际缺口。旧caller若已留存直接引用，只核不可信接入ABI/身份/门；无可靠caller种子就有界报告，不做全ROM字节incoming重扫。

只选本已知API的一条正常image-cache失效业务连接；不预设照片退出/主页面切换一定标记，不扩所有invalidate/全cache/PNG/heap，不重导整函数或复制源码。计量/排序算法及运行时实际时序保留未知。若已有可靠合同覆盖即报已覆盖结束，不凑时长/函数/闭包。报告分继承、复核纠正、真正新增、未闭精确边；必要静态验证后提交独占成果并报告commit/验证/未知/clean。共同安全/独占/隔离规则适用，不创建下级agent，无SIM/构建/历史回放/生产ROM配置模型修改。
