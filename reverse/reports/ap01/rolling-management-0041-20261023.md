# 0041 六路滚动管理（2026-10-23恢复）

用户最新授权恢复持续六路推进，取代历史收尾暂停与三路上限。原管理交接已归档至 rolling-task-history-0041-20261023.md。主窗口只管理，不作函数逆向或技术语义判断。环境共7席，主窗口1席，研究/复核6席。前批六项均已整合；六个后继立即补位，真实状态见运行快照。

## 共同规则

只做0041静态功能恢复；禁止执行固件、连接设备/外部服务、漏洞/异常输入/缺陷验证、修改安全检查、ROM、生产代码、构建配置和分析器模型；不推送。只写独占reverse/analysis和reverse/reports/ap01文件。只用自己的独立worktree和分支，每次shell显式workdir并在PowerShell Set-Location。其他agent同时工作，不撤销他人修改、不改主树或共享索引，不创建下级agent、不自行接后继。忽略ROM/证据/工具从主仓库绝对路径只读访问；不复制工作区，不共享可写数据库或切换全局REA。优先留存证据；若工具不能隔离则报告管理者。临时状态/日志放各自独占analysis目录。只恢复正常原程序行为，不擅自修正。

交付列问题/范围/结论、业务行为、函数地址/参数/返回/调用、必要伪代码结构体状态转换、所有权生命周期、可定位证据与原指令、事实/推断/未知、来源与恢复程度、实际静态验证、断边和一个后续闭包。伪代码不是原源码；保留调用顺序、重读、宽度/符号、返回判断、失败/清理和间接ABI。边界/厂商指令须核原字节，不仅信反编译。标准库只有来源可核实才排除，适配/回调仍恢复；不新增哈希清单/复制清单/机械重复证据。不编译项目，不运行历史回放。完成标准为原问题闭包得到有证据答案或明确可定位断边，不能缩成短helper声称完成；不设函数数量或时长配额；主体已覆盖即收缩，已无必要增量即报告已覆盖并结束。

接近提交提前报告结论、剩余验证、阻塞和后继建议。检查差异、必要验证、明确路径git add、提交、报告commit/验证/未知/干净状态后结束。主窗口作范围验收，技术验收由新独立agent。恢复成果可先整合为待复核；不得自验冒称验收。每项完成即整合补位，从启动时最新管理提交创建新树；运行任务不移动基线。语义冲突交agent；回收仅限干净且已整合worktree，分支保留。用户要求收尾即停止派发。

主仓库：D:/Documents/PlatformIO/Projects/cuktech-ap01-firmware。所有任务初始共同研究基线 ab9716e；实际启动基线为含本任务书的管理提交，在派发消息及运行表记录。

## 当前任务书



## 实际运行快照

以下六项真实运行，已结束任务即时补位，主窗口另计；不创建下级agent。

|任务|agent|基线|实际范围|
|---|---|---|---|
|T02|/root/e17_uv_time_review（派发中）|本次启动提交|独立核T01复用接入/运行时限定|
|B23|/root/g16_fb_file_review（运行）|14e7291|独立核B22 cmd51真正新增分类合同|
|I06|/root/h16_clock_source_review（运行）|14e7291|独立核I05旧配置read/cache合同衔接|
|J03|/root/a46_cache_drop（运行）|09e11d0|正常设置持久化旧成果复用/精确缺口种子|
|L01|/root/a47_reader_mode（派发中）|本次启动提交|设置UI两caller到a00ab478的必要接入合同|
|J04|/root/d19_backlight_animation（运行）|09e11d0|工厂正常UI/资源生命周期旧证据复用与真实种子|

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

## 并发纠正（2026-10-24用户最新要求）

必须维持六个实际运行的独立worktree subagent；完成即补位。范围去重用于换题/收缩，不能作为长时间空席理由。主窗口维护准备队列；不为数量重复恢复已有成果。以下四项均以已定位断边或来源认证缺口为题。

## 后继队列规则

后继以文件内仍标“预备完整任务书”的章节为准；移入当前任务书或历史后即不再计排队。不得从旧静态ID列表重复派发。


## 本批继承与增量快照（df35f44启动）

A48继承A46/既有cache合同，只独立复核，新增0；A49继承A47及mode0合同，只独立复核，新增0；D20继承settings-round2b清理接线与D19，只独立复核，新增0。E18只补实际固定分母除法返回合同，不重做时间上层；G17只补NuttX fb候选来源认证，不用LVGL认证替代；H17只找计数writer正常连接，不重搜offset未知。六个agent已由实时状态确认全部running；管理窗口另计。


## 当前完整任务书 B23（前置已整合，立即接替）

独占reverse/reports/ap01/cmd51-device-type-review-b23-0041-20261024.md及reverse/analysis/cmd51-device-type-review-b23-0041-20261024/。

待B22整合后，新独立agent只核cmd51写item+0e前本轮实际新增分类条件/输入记录宽度/厂商字/new_type接入。E01/E02既有五指针生命周期/类型变化与fallback继承，不能算新发现或整dispatcher验收；不扩cmd52/帧/OTA/异常输入/driver。若B22为已覆盖结论则只核证据范围，新功能0。

仅准备不计运行，派发前整合前置并核重叠。最新管理HEAD独占树re0041-ID小写/分支codex/re-0041-ID小写，根D:/CodexHome/visualizations/2026/10/23/01a1691a-e178-7710-86c0-84c2ff2d3dfb。独占指定报告/同名analysis；REA skill与共同/复用/静态安全规则适用，已有→实际缺口及四分报告；不改共享/主树/生产ROM配置模型，不创建下级agent，其他agent同时工作勿撤销；精确独占提交commit/验证/未知/clean，接近提交提前报种子。


## 当前完整任务书 J03（先行复用盘点，立即接替）

独占reverse/reports/ap01/settings-persistence-reuse-gap-j03-0041-20261024.md及reverse/analysis/settings-persistence-reuse-gap-j03-0041-20261024/。

仅既有证据检索不新增ROM字节/反编译。先application最终SIM验收/matrix/reference-map/system-complete与settings-round2各批，再按地址/字段/callback/state检索近期settings/backlight/theme/miio/config专项及独立复核/父级结论/ZIP必要成员。只正常设置值的读取/保存/持有原ROM合同与SIM持久本地服务替代的证据范围，给短已有→行为→局限→真实缺口/可靠种子表，不重复D19/D22动画/背光、I01/I02启动、I05特定wifi-cache更新。旧pending须核较晚complete，已有回调/写值不因报告标题缺失当未分析；SIM服务源码/截图不证明ROM存储ABI。不重建整矩阵/分类资源表/源码/机械账，不扩OTA安全/异常或全driver/NVS扫描。少量真实调用/extent/字段种子才建议后继，无必要增量直接覆盖结论，新功能0；主窗口决定派发，不自行接题。

仅准备不计运行，派发前整合前置并核重叠。最新管理HEAD独占树re0041-ID小写/分支codex/re-0041-ID小写，根D:/CodexHome/visualizations/2026/10/23/01a1691a-e178-7710-86c0-84c2ff2d3dfb。独占指定报告/同名analysis；REA skill与共同/复用/静态安全规则适用，已有→实际缺口及四分报告；不改共享/主树/生产ROM配置模型，不创建下级agent，其他agent同时工作勿撤销；精确独占提交commit/验证/未知/clean，接近提交提前报种子。


## 当前完整任务书 J04（2026-10-24立即接替）

树D:/CodexHome/visualizations/2026/10/23/01a1691a-e178-7710-86c0-84c2ff2d3dfb/re0041-j04；分支codex/re-0041-j04；基线本次启动提交。独占reverse/reports/ap01/factory-reuse-gap-j04-0041-20261024.md及reverse/analysis/factory-reuse-gap-j04-0041-20261024/。

仅既有证据检索，不新增ROM字节/反编译。先reference-map/application最终SIM范围与factory-test、factory-active B16/B17、buzzer两轮、settings/system complete、近期对应专项/复核，按地址/字段/callback/state核工厂正常UI/入口/资源生命周期已覆盖范围。B16外部active reader有界未知与搜索边界直接继承，不重复全ROM字段扫；factory-test启动门、GPIO三轮保持、fd取得等已有合同不得新发现。只表列旧出处→行为→局限→真实精确缺口，有真实extent/caller/对象种子才给少量后继；无种子不派stop/close/根析构/全driver扫描，不将物理极性/设备效果视为静态已恢复。不执行工厂命令/设备，不扩安全/缺陷/异常或重建整分类资源表；主窗口决定后继，不自行接题，新功能0。

REA skill、本文共同/复用/静态安全规则全适用；独占树/输出、不改共享/主树/生产ROM配置模型、不创建下级agent，其他agent同时工作勿撤销。先已有→行为→局限→精确缺口，四分报告，只必要稀疏证据；已覆盖直接收缩，无可靠种子不扩扫。必要JSON/链接/差异检查、精确独占提交commit/验证/未知/clean，接近提交提前报重叠/种子。


## 当前完整任务书 I06（前置已整合，立即接替）

独占reverse/reports/ap01/wifi-config-cache-review-i06-0041-20261024.md及reverse/analysis/wifi-config-cache-review-i06-0041-20261024/。

待I05整合后，新独立agent只复核旧a005a736内联初始化配置read a0060946参数/精确rc1/62fc919c字节失败清0成功读取及同I01 getter关系；PSM旧static/原字/flags覆盖必须继承，不当新的setter/持久写，不扩事件writer/网络或底层NVS。主体已有新功能0，必要稀疏锚点标复核。

仅准备不计运行，派发前整合前置核重叠，最新管理HEAD新建独占树re0041-ID小写/分支codex/re-0041-ID小写，根D:/CodexHome/visualizations/2026/10/23/01a1691a-e178-7710-86c0-84c2ff2d3dfb。独占指定报告/同名analysis；REA skill与共同/复用/静态安全规则全适用，已有→实际缺口与四分报告、最小稀疏验证，不改共享/主树/生产ROM配置模型、不创建下级agent，其他agent同时工作勿撤销，独占提交commit/验证/未知/clean，接近提交先报后继种子。


## 当前完整任务书 T02（T01已整合，立即接替）

独占reverse/reports/ap01/timer-repeat-release-review-t02-0041-20261024.md及reverse/analysis/timer-repeat-release-review-t02-0041-20261024/。

待T01整合后，新独立agent只核其实际正常repeat_count0 callback后scheduler/auto-delete/归还接入或有界无种子结论。G05/G06已核a008ae58合同与I01/I02 callback直接引用，不重导旧函数或全timer/IRQ扫描，不用候选当ROM；userdata和timer分开。只核实际新增，不递归扩库，新功能0。

仅准备不计运行，派发前整合前置核重叠，最新管理HEAD新建独占树re0041-ID小写/分支codex/re-0041-ID小写，根D:/CodexHome/visualizations/2026/10/23/01a1691a-e178-7710-86c0-84c2ff2d3dfb。独占指定报告/同名analysis；REA skill与共同/复用/静态安全规则全适用，已有→实际缺口与四分报告、最小稀疏验证，不改共享/主树/生产ROM配置模型、不创建下级agent，其他agent同时工作勿撤销，独占提交commit/验证/未知/clean，接近提交先报后继种子。


## 当前完整任务书 L01（2026-10-24，立即接替）

树D:/CodexHome/visualizations/2026/10/23/01a1691a-e178-7710-86c0-84c2ff2d3dfb/re0041-l01；分支codex/re-0041-l01；基线本次启动提交。独占reverse/reports/ap01/settings-mode-entry-l01-0041-20261024.md及reverse/analysis/settings-mode-entry-l01-0041-20261024/。

J03复用盘点给旧真实call种子：settings-round2b records[10] a00feac8(a0从s4+1 LBU)/a00feade(a0=3)→a00ab478，旧extent48B ev_5334e642…；不能仅按报告无标题认缺失。先查system/guide complete父级cached settings、page-logic/较晚round3/pass3/近期settings/saver/mode专报告及ZIP必要成员，按callee/字段/state交叉核是否早已解释。

只核这两正常UI调用进入同48B helper的参数宽度/返回消费、所写字段或下层服务接入；不能先将其命名持久保存或推全设置行为。旧设置状态、重绘、D19/D22背光动画、I01/I05配置和J03盘点均继承，不接管其主题。主体已覆盖则直接引用结束，只补实际不可信/缺接入窗口，不重导完整设置大函数/分类表/源码/全资源；不扩NVS/驱动/网络/异常/安全/全GUI。

REA skill与本文共同/复用/静态安全规则适用，先已有→行为→局限→精确缺口和四分报告；独占树/输出，不改共享/主树/生产ROM配置模型，不创建下级agent，其他agent同时工作勿撤销。必要静态验证、精确路径提交commit/验证/未知/clean，接近提交先报重叠与真实种子。
