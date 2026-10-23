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
|A48|/root/e17_uv_time_review（运行）|df35f44|独立复核A46|
|A49|/root/g16_fb_file_review（运行）|df35f44|独立复核A47分类1→a0107d8e→mode1 W→既有O复制；a01b2e3a实参callback(D,H)、条件缓存归还和O前三word清零，不能直接命名fclose|
|D21|/root/h16_clock_source_review（派发中）|本次启动提交|背光动画具体属性/selector及局部来源认证|
|E18|/root/a46_cache_drop（运行）|df35f44|只补E16/E17调用a001b302的正常unsigned64除法合同：实际分母0:0xf4240、分子构造、返回pair及必要carry/归一化路径|
|G17|/root/a47_reader_mode（运行）|df35f44|只认证G13/G15/G16具体fb open/close/poll/notify与本地NuttX12.10候选对应关系|
|H17|/root/d19_backlight_animation（运行）|df35f44|只补H15/H16读者62fc6c64的真实writer/正常计数更新连接|

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


## 当前完整任务书 A48（2026-10-24立即补位）

树D:/CodexHome/visualizations/2026/10/23/01a1691a-e178-7710-86c0-84c2ff2d3dfb/re0041-a48；分支codex/re-0041-a48；启动基线为本任务书最新整合提交。独占reverse/reports/ap01/image-cache-drop-review-a48-0041-20261024.md及reverse/analysis/image-cache-drop-review-a48-0041-20261024/。

独立复核A46。同backend +18=a00ebf7c/+1c=a00ec084；NULL source到同image-cache drop_all接线；零引用cleanup与随后全部树/链释放原序；单drop的门和责任。继承A27/A34/A38/A43/A44可靠合同；不把a019cfbe叫backend回调，不修原行为，不推断实际运行或缺陷。新功能0，必要稀疏复核。

先读REA skill C:/Users/cogic/.agents/skills/reverse-engineer-anything/SKILL.md及本文共同规则/复用规则。先检索优先complete、最终验收及近期对应报告/独立复核，按地址字段交叉检索；表列已有出处→行为→局限→实际缺口。报告四分：继承、本轮复核纠正、真正新增、精确未闭；旧字节复核不算新增功能。只必要稀疏窗口/ABI，不全导出/复制/机械记账。独占输出、独占worktree，不改共享文档/主树/生产ROM配置模型，不创建下级agent；其他agent同时工作勿撤销。静态安全边界全适用。必要验证、精确路径提交、报告commit/clean/未知；接近提交先给后继建议。


## 当前完整任务书 A49（2026-10-24立即补位）

树D:/CodexHome/visualizations/2026/10/23/01a1691a-e178-7710-86c0-84c2ff2d3dfb/re0041-a49；分支codex/re-0041-a49；启动基线为本任务书最新整合提交。独占reverse/reports/ap01/photo-reader-mode-review-a49-0041-20261024.md及reverse/analysis/photo-reader-mode-review-a49-0041-20261024/。

独立复核A47分类1→a0107d8e→mode1 W→既有O复制；a01b2e3a实参callback(D,H)、条件缓存归还和O前三word清零，不能直接命名fclose。继承A37/A39/A41/A42 mode0；具体D/open/close与默认五照片实际mode1仍未知。新功能0。

先读REA skill C:/Users/cogic/.agents/skills/reverse-engineer-anything/SKILL.md及本文共同规则/复用规则。先检索优先complete、最终验收及近期对应报告/独立复核，按地址字段交叉检索；表列已有出处→行为→局限→实际缺口。报告四分：继承、本轮复核纠正、真正新增、精确未闭；旧字节复核不算新增功能。只必要稀疏窗口/ABI，不全导出/复制/机械记账。独占输出、独占worktree，不改共享文档/主树/生产ROM配置模型，不创建下级agent；其他agent同时工作勿撤销。静态安全边界全适用。必要验证、精确路径提交、报告commit/clean/未知；接近提交先给后继建议。


## 当前完整任务书 E18（2026-10-24立即补位）

树D:/CodexHome/visualizations/2026/10/23/01a1691a-e178-7710-86c0-84c2ff2d3dfb/re0041-e18；分支codex/re-0041-e18；启动基线为本任务书最新整合提交。独占reverse/reports/ap01/uv-time-division-e18-0041-20261024.md及reverse/analysis/uv-time-division-e18-0041-20261024/。

只补E16/E17调用a001b302的正常unsigned64除法合同：实际分母0:0xf4240、分子构造、返回pair及必要carry/归一化路径。继承H15/H16单U32 t分拆、E14/E15 deadline和E16/E17接线，不重做clock/heap；由研究者判断该正常范围能否支持缓存商=t，实际计数节奏/epoch仍未知。仅固定非零分母实际范围，不扩零除/任意异常/整个数值库，不整函数重导。

先读REA skill C:/Users/cogic/.agents/skills/reverse-engineer-anything/SKILL.md及本文共同规则/复用规则。先检索优先complete、最终验收及近期对应报告/独立复核，按地址字段交叉检索；表列已有出处→行为→局限→实际缺口。报告四分：继承、本轮复核纠正、真正新增、精确未闭；旧字节复核不算新增功能。只必要稀疏窗口/ABI，不全导出/复制/机械记账。独占输出、独占worktree，不改共享文档/主树/生产ROM配置模型，不创建下级agent；其他agent同时工作勿撤销。静态安全边界全适用。必要验证、精确路径提交、报告commit/clean/未知；接近提交先给后继建议。


## 当前完整任务书 G17（2026-10-24立即补位）

树D:/CodexHome/visualizations/2026/10/23/01a1691a-e178-7710-86c0-84c2ff2d3dfb/re0041-g17；分支codex/re-0041-g17；启动基线为本任务书最新整合提交。独占reverse/reports/ap01/fb-source-auth-g17-0041-20261024.md及reverse/analysis/fb-source-auth-g17-0041-20261024/。

只认证G13/G15/G16具体fb open/close/poll/notify与本地NuttX12.10候选对应关系。候选/home/slepher/nuttx-ap01-sim/nuttx/drivers/video/fb.c及必要file_operations/pollfd头；身份继承A13/A14，F07/F08的LVGL认证不覆盖此题。按匹配/差异/配置条件/未知列出，尊重ROM F16B和poll字段；候选不能覆盖ROM差异或证明精确版本。不重导ROM/复制全源码/扫描全NuttX/整库排除。WSL只读，无构建/SIM/网络。

先读REA skill C:/Users/cogic/.agents/skills/reverse-engineer-anything/SKILL.md及本文共同规则/复用规则。先检索优先complete、最终验收及近期对应报告/独立复核，按地址字段交叉检索；表列已有出处→行为→局限→实际缺口。报告四分：继承、本轮复核纠正、真正新增、精确未闭；旧字节复核不算新增功能。只必要稀疏窗口/ABI，不全导出/复制/机械记账。独占输出、独占worktree，不改共享文档/主树/生产ROM配置模型，不创建下级agent；其他agent同时工作勿撤销。静态安全边界全适用。必要验证、精确路径提交、报告commit/clean/未知；接近提交先给后继建议。


## 当前完整任务书 H17（2026-10-24立即补位）

树D:/CodexHome/visualizations/2026/10/23/01a1691a-e178-7710-86c0-84c2ff2d3dfb/re0041-h17；分支codex/re-0041-h17；启动基线为本任务书最新整合提交。独占reverse/reports/ap01/clock-counter-writer-h17-0041-20261024.md及reverse/analysis/clock-counter-writer-h17-0041-20261024/。

只补H15/H16读者62fc6c64的真实writer/正常计数更新连接。优先既有source-xrefs/global refs/较晚round3/clock_timer或clock_systimer候选定位，实际有种子才补一条increment/reset/timer周期链；无可靠writer有界交付精确未知，不承诺节奏/单调/epoch。不重复offset62fc5c74无种子搜索，不全ROM字节/字段扫、不扫全IRQ、无硬件执行。候选源只定位不等于ROM。

先读REA skill C:/Users/cogic/.agents/skills/reverse-engineer-anything/SKILL.md及本文共同规则/复用规则。先检索优先complete、最终验收及近期对应报告/独立复核，按地址字段交叉检索；表列已有出处→行为→局限→实际缺口。报告四分：继承、本轮复核纠正、真正新增、精确未闭；旧字节复核不算新增功能。只必要稀疏窗口/ABI，不全导出/复制/机械记账。独占输出、独占worktree，不改共享文档/主树/生产ROM配置模型，不创建下级agent；其他agent同时工作勿撤销。静态安全边界全适用。必要验证、精确路径提交、报告commit/clean/未知；接近提交先给后继建议。


## 本批继承与增量快照（df35f44启动）

A48继承A46/既有cache合同，只独立复核，新增0；A49继承A47及mode0合同，只独立复核，新增0；D20继承settings-round2b清理接线与D19，只独立复核，新增0。E18只补实际固定分母除法返回合同，不重做时间上层；G17只补NuttX fb候选来源认证，不用LVGL认证替代；H17只找计数writer正常连接，不重搜offset未知。六个agent已由实时状态确认全部running；管理窗口另计。


## 预备完整任务书 A50（有前置，未启动）

独占reverse/reports/ap01/photo-reader-consumer-a50-0041-20261024.md及reverse/analysis/photo-reader-consumer-a50-0041-20261024/。

A49有界重叠筛选得到旧weather-calendar-complete evidence[30]真实a010a5d6非零mode→a008b888种子，whole-ROM round1已有a008b888 extent(ev_0cf7b05a…/544B)；并非此前未分析。只补同reader前缀进入此callee的ABI、D读取/reader回调槽、缓存持有连接；先核旧complete内部与A47/A49覆盖，若已覆盖直接收缩交付。具体D实例/真实mode1 source仍未知，不扩全部文件系统/所有解码算法/失败分支，不重导544B全函数。

准备队列不等于运行或已交付。实际派发前须整合前置、再核重叠，使用当时最新管理HEAD创建独立worktree；树名re0041-ID小写，分支codex/re-0041-ID小写，根D:/CodexHome/visualizations/2026/10/23/01a1691a-e178-7710-86c0-84c2ff2d3dfb。独占本文指定报告与同名analysis目录。REA skill及共同/复用规则适用：先已有出处→行为→局限→缺口、四分报告、最小稀疏取证、静态安全边界、不创建下级agent、不改共享/主树/生产ROM配置模型、其他agent同时工作勿撤销、独占提交commit/验证/未知/clean，接近提交预告后继建议。


## 预备完整任务书 A51（有前置，未启动）

独占reverse/reports/ap01/image-cache-drop-source-a51-0041-20261024.md及reverse/analysis/image-cache-drop-source-a51-0041-20261024/。

待A48独立复核整合后，只补A43/A44当时未展开、现A46/A48新核backend drop/drop_all的局部来源认证。候选沿用本地LVGL9.2.1 lv_cache_lru_rb.c及必要邻接接口，旧key/meter/LRU/source家族匹配全继承不重复。分匹配/差异/配置条件/未知，尊重非零ref原序与单drop实际门，候选不覆盖ROM、不证明精确版本、不整库排除。不复制整源码、不重导ROM或全库版本搜索。

准备队列不等于运行或已交付。实际派发前须整合前置、再核重叠，使用当时最新管理HEAD创建独立worktree；树名re0041-ID小写，分支codex/re-0041-ID小写，根D:/CodexHome/visualizations/2026/10/23/01a1691a-e178-7710-86c0-84c2ff2d3dfb。独占本文指定报告与同名analysis目录。REA skill及共同/复用规则适用：先已有出处→行为→局限→缺口、四分报告、最小稀疏取证、静态安全边界、不创建下级agent、不改共享/主树/生产ROM配置模型、其他agent同时工作勿撤销、独占提交commit/验证/未知/clean，接近提交预告后继建议。


## 当前完整任务书 D21（D20已整合，立即接替）

独占reverse/reports/ap01/backlight-animation-source-d21-0041-20261024.md及reverse/analysis/backlight-animation-source-d21-0041-20261024/。

待D20整合后，优先补其提出的真实a00f43bc→a018fb3c→a00df94c(target,0x3e,value,0x20000) property/selector语义认证，回答三角动画的具体UI效果；只核必要薄wrapper/属性定义，不扩通用style引擎。D20已筛旧complete/settings只含通用setter/清理，不能据标题认首次发现。其次仅在尚未覆盖时认证D19/D20的96B descriptor必要字段与start/get/delete/target/exec/path合同到本地LVGL9.2.1 lv_anim.c/lv_anim.h相应行。先核F07/F08等旧来源报告有无已覆盖，匹配直接引用；对未核字段/删除callback与ROM差异给局部答案。厂商遍历字未认证不能用候选替代；不扩完整动画调度/GUI/生命周期，也不假定ctx最终释放。候选精确ROM版本未知。

准备队列不等于运行或已交付。实际派发前须整合前置、再核重叠，使用当时最新管理HEAD创建独立worktree；树名re0041-ID小写，分支codex/re-0041-ID小写，根D:/CodexHome/visualizations/2026/10/23/01a1691a-e178-7710-86c0-84c2ff2d3dfb。独占本文指定报告与同名analysis目录。REA skill及共同/复用规则适用：先已有出处→行为→局限→缺口、四分报告、最小稀疏取证、静态安全边界、不创建下级agent、不改共享/主树/生产ROM配置模型、其他agent同时工作勿撤销、独占提交commit/验证/未知/clean，接近提交预告后继建议。


## 预备完整任务书 E19（有前置，未启动）

独占reverse/reports/ap01/uv-time-division-review-e19-0041-20261024.md及reverse/analysis/uv-time-division-review-e19-0041-20261024/。

待E18整合后，新独立agent只复核固定分母1M正常路径、H15/H16已证t范围下返回商及高word、分支范围/必要table/厂商字/ABI和静态代数。E16/E17接线继承，不复核整个数值库/计数cadence/epoch，不执行输入或异常测试。新增功能0。

准备队列不等于运行或已交付。实际派发前须整合前置、再核重叠，使用当时最新管理HEAD创建独立worktree；树名re0041-ID小写，分支codex/re-0041-ID小写，根D:/CodexHome/visualizations/2026/10/23/01a1691a-e178-7710-86c0-84c2ff2d3dfb。独占本文指定报告与同名analysis目录。REA skill及共同/复用规则适用：先已有出处→行为→局限→缺口、四分报告、最小稀疏取证、静态安全边界、不创建下级agent、不改共享/主树/生产ROM配置模型、其他agent同时工作勿撤销、独占提交commit/验证/未知/clean，接近提交预告后继建议。


## 预备完整任务书 G18（有前置，未启动）

独占reverse/reports/ap01/fb-source-review-g18-0041-20261024.md及reverse/analysis/fb-source-review-g18-0041-20261024/。

待G17整合后，新独立agent只复核具体fb open/close/poll/notify候选映射、ROM字段与CONFIG条件边界；G13–G16行为继承，不重导ROM。精确版本与配置不能由候选自动认证；不整库排除，新增功能0。

准备队列不等于运行或已交付。实际派发前须整合前置、再核重叠，使用当时最新管理HEAD创建独立worktree；树名re0041-ID小写，分支codex/re-0041-ID小写，根D:/CodexHome/visualizations/2026/10/23/01a1691a-e178-7710-86c0-84c2ff2d3dfb。独占本文指定报告与同名analysis目录。REA skill及共同/复用规则适用：先已有出处→行为→局限→缺口、四分报告、最小稀疏取证、静态安全边界、不创建下级agent、不改共享/主树/生产ROM配置模型、其他agent同时工作勿撤销、独占提交commit/验证/未知/clean，接近提交预告后继建议。


## 预备完整任务书 H18（有前置，未启动）

独占reverse/reports/ap01/clock-counter-review-h18-0041-20261024.md及reverse/analysis/clock-counter-review-h18-0041-20261024/。

待H17整合后，新独立agent只复核H17实际增量或有界负结论。只核其真实writer种子、必要字段/原字节/周期连接与解释强度；若无种子则核搜索边界，不重复全ROM搜索，不将未找到等于不存在，不再搜offset writer。H15/H16既有读者继承，新增功能0。

准备队列不等于运行或已交付。实际派发前须整合前置、再核重叠，使用当时最新管理HEAD创建独立worktree；树名re0041-ID小写，分支codex/re-0041-ID小写，根D:/CodexHome/visualizations/2026/10/23/01a1691a-e178-7710-86c0-84c2ff2d3dfb。独占本文指定报告与同名analysis目录。REA skill及共同/复用规则适用：先已有出处→行为→局限→缺口、四分报告、最小稀疏取证、静态安全边界、不创建下级agent、不改共享/主树/生产ROM配置模型、其他agent同时工作勿撤销、独占提交commit/验证/未知/clean，接近提交预告后继建议。
