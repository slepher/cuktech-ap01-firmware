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
|J01|/root/e17_uv_time_review（运行）|7119b59|充电领域旧complete与近期复核交叉去重/实际缺口种子|
|I03|/root/g16_fb_file_review（运行）|472f076|屏保Time2 type2f已有成果→正常DELETE/ctx责任缺口|
|B22|/root/h16_clock_source_review（派发中）|本次启动提交|cmd51写item+0e前正常类型决策，继承既有所有权链|
|A55|/root/a46_cache_drop（运行）|46fa469|独立复核A54 reader局部来源与gifdec整文件不同边界|
|J02|/root/a47_reader_mode（运行）|34ff6ba|日历/时间旧complete与近期复核去重/真实缺口种子|
|I02|/root/d19_backlight_animation（运行）|46fa469|独立复核I01旧启动证据范围与精度|

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


## 当前完整任务书 A55（前置已整合，立即接替）

独占reverse/reports/ap01/photo-reader-source-review-a55-0041-20261024.md及reverse/analysis/photo-reader-source-review-a55-0041-20261024/。

待A54整合后，新独立agent只核reader前缀/open/close/注册槽/缓存布局候选映射与配置条件，callback(D,H)以A47/A49 ROM为据；A50内部read消费/A52复核直接继承，不扩全部文件系统/具体D实例，无精确版本/整库排除，新功能0。

仅准备不计运行。实际派发前整合前置并再核重叠，最新管理HEAD创建独占树re0041-ID小写/分支codex/re-0041-ID小写，根D:/CodexHome/visualizations/2026/10/23/01a1691a-e178-7710-86c0-84c2ff2d3dfb。独占指定报告及同名analysis。REA skill、共同/复用/安全规则全适用；已有→实际缺口与四分报告、只必要稀疏证据，不改共享/主树/生产ROM配置模型、不创建下级agent；其他agent同时工作勿撤销。独占精确提交commit/验证/未知/clean，接近提交提前建议。


## 当前完整任务书 I02（前置已整合，立即接替）

独占reverse/reports/ap01/boot-ready-review-i02-0041-20261024.md及reverse/analysis/boot-ready-review-i02-0041-20261024/。

待I01整合后，新独立agent只核其实际补充或覆盖结论：旧guide/system已有启动timer/计数/结束/configured/index8直接引用，SIM固定2s不等于原ROM条件；只核实际新增接入ABI/条件/原字/次序或旧证据范围，不扩驱动/设备初始化，不把没执行等于未分析，新功能0。

仅准备不计运行。实际派发前整合前置并再核重叠，最新管理HEAD创建独占树re0041-ID小写/分支codex/re-0041-ID小写，根D:/CodexHome/visualizations/2026/10/23/01a1691a-e178-7710-86c0-84c2ff2d3dfb。独占指定报告及同名analysis。REA skill、共同/复用/安全规则全适用；已有→实际缺口与四分报告、只必要稀疏证据，不改共享/主树/生产ROM配置模型、不创建下级agent；其他agent同时工作勿撤销。独占精确提交commit/验证/未知/clean，接近提交提前建议。


## 当前完整任务书 I03（2026-10-24，立即接替）

树D:/CodexHome/visualizations/2026/10/23/01a1691a-e178-7710-86c0-84c2ff2d3dfb/re0041-i03；分支codex/re-0041-i03；基线本任务书启动提交。独占reverse/reports/ap01/saver-time2-lifetime-i03-0041-20261024.md及reverse/analysis/saver-time2-lifetime-i03-0041-20261024/。

先guide-complete/system-complete、ui-total-consumers/theme-total-state及其近期复核、page-logic/较晚round3/pass3/最终ZIP相应成员。旧guide已解释mode2/type0x2f与a00ac4c2两种活动布局；ui-total-consumers已恢复a00ac54e callback、ctx+24严格0/1、功率除10/格式布局，且theme-total-state是后续，不得按旧剩余重复。上述业务/活动setter全继承，不重做分类/显示语义。

只核同一屏保Time2 type0x2f的creator/context/page/callback/DELETE所有权已有证据范围，先交已有→行为→局限→精确缺口；只有实际尚未闭的正常DELETE接入、callback注销/ctx/wrapper释放原序或必要ABI才补稀疏窗口。主体已覆盖则直接引用并结束，不用凑函数/全页/整GUI。type0x2f对象不能套用H08/H09 type2 time1 136B或H05 type4 weather1 68B、H01 type19 116B的清理结论。正常上层离页→DELETE无种子不重复全ROM根析构搜索。

REA skill与本文共同/复用/静态安全规则适用，四分报告；不重导整函数/全资源/PNG/源码/机械账，不执行SIM/构建/回放/固件/设备/外网。独占worktree/输出，不改共享/主树/生产ROM配置模型、不创建下级agent，其他agent同时工作勿撤销。必要验证、精确路径提交commit/验证/未知/clean；接近提交先报重叠/真实增量/后继种子。


## 当前完整任务书 J01（2026-10-24，复用检索接替）

树D:/CodexHome/visualizations/2026/10/23/01a1691a-e178-7710-86c0-84c2ff2d3dfb/re0041-j01；分支codex/re-0041-j01；基线本任务书启动提交。独占reverse/reports/ap01/charge-reuse-gap-j01-0041-20261024.md及reverse/analysis/charge-reuse-gap-j01-0041-20261024/。

本题是已有证据检索/范围收缩，不作新增ROM反编译或字节取证。先application-rehost-complete、function-matrix、factory-reference-map与charge-complete，再按地址/callback/字段/state查charge/details round4、page-logic、近期charging/UiIFace/total/theme/E01-E19/C09-C12专项及独立复核/父级验收，必要ZIP只读成员。只针对充电业务原ROM合同与SIM服务替代之间尚有证据不足之处，形成短表：旧出处→解释行为→局限→真实精确缺口/可靠种子。新标题/旧工具入口失识/旧pending不当缺失；特别E07/E08 body边界后被E09/E11 round3纠正、E12/E13已覆盖消费者不得重开。

不重建整分类表/矩阵/资源/源码或机械记账，不重新导出已有函数/全证据，不做新的技术语义裁决。只将已有可靠原字节/旧反编译需局核/SIM照片替代/未检到的精确边分开。可提出少量实际有调用点/extent/字段种子的后继，已无必要增量则明确已覆盖；无种子不提全ROM/heap/driver搜索。主窗口最终决定派发；不自行接题、不创建下级agent。不要与运行I01启动/I03屏保/A54reader争同范围。

REA skill与共同/复用/静态安全规则适用，四分报告、新增功能0；独占worktree/输出，不改共享/主树/生产ROM配置模型，其他agent同时工作勿撤销；必要JSON/链接/差异检查、精确路径提交并回报commit/clean，接近提交提前给种子与重叠。


## 当前完整任务书 J02（2026-10-24，复用检索接替）

树D:/CodexHome/visualizations/2026/10/23/01a1691a-e178-7710-86c0-84c2ff2d3dfb/re0041-j02；分支codex/re-0041-j02；基线本任务书启动提交。独占reverse/reports/ap01/calendar-time-reuse-gap-j02-0041-20261024.md及reverse/analysis/calendar-time-reuse-gap-j02-0041-20261024/。

仅检索既有材料，不新增ROM反编译/字节导出。优先application-rehost-complete/function-matrix/factory-reference-map/weather-calendar-complete，再按函数地址/callback/字段/资源/state检索page-logic/旧pass3/近期日历和time/charge数值handler复核/父级验收/ZIP必要成员。只日历与时间数值/转换/显示接入的证据范围，不重做天气分类/显示，也不重复H13-H18/E16-E19已核counter/ID0/ID1/固定分母或无种子writer/offset搜索。

形成短已有出处→行为→局限→精确缺口表，原字节合同/旧反编译需局核/SIM照片安全替代/未检到种子分别列。旧weather complete remaining的parent X11和time数字handler应先核父级complete与charge-owned后续，不能因pending重开。旧safe lunar bounds、defaultUTC0、hostRTC等仅说明SIM替代，仍要查旧ROM证据是否已解释相应行为。必要ZIP只读成员不执行/全解包/复制。最多提出少量有真实调用/extent/字段/资源种子的增量建议；主体已覆盖就收缩，没有种子不全ROM/全日历库扩扫。此为复用盘点、新功能0，主窗口负责最终范围派发，不自行接题。

REA skill与共同/复用/静态安全规则全适用，四分报告；不重建整分类表/矩阵/源码/资源/机械账，不改共享/主树/生产ROM配置模型、不创建下级agent，其他agent同时工作勿撤销。必要JSON/链接/差异检查，独占精确提交commit/验证/未知/clean，接近提交提前给种子/重叠。


## 当前完整任务书 B22（旧种子已在主仓，J01去重支持，立即接替）

独占reverse/reports/ap01/cmd51-device-type-b22-0041-20261024.md及reverse/analysis/cmd51-device-type-b22-0041-20261024/。

J01去重后唯一有原留存种子的增量：a00a8582 cmd0x51正常设备类型决策→item+0e写入前new_type。E01明确未认证完整分类树、E02仅接受9504后类型变化/分配；旧UiIFace lifecycle/charge/details完整原分类或较晚成果若已有必须直接引用。种子a00a93a4..940c、9454..947c、9504边，buzzer-backlight retained extent8582..9d1d / Evidence ev_6f9f82e5daf0540a1c24a0b85daa2e394785391692765e5e3e100eb7b37ed94c。只补此正常分类实参/记录宽度符号/分支条件/返回或new_type→既有item+0e接入；旧fallback0x15及五指针清理分配原位覆盖全继承，不重导整个dispatcher、不重复全分类目录/资源表、不扩OTA/帧解析/异常输入/长度审计/完整driver。报告区分旧证据存在与本轮解释增量，厂商字/错误反编译只补必要窗口。

仅准备不计运行，派发前整合前置/再核重叠。最新管理HEAD新建独占树re0041-ID小写、分支codex/re-0041-ID小写，根D:/CodexHome/visualizations/2026/10/23/01a1691a-e178-7710-86c0-84c2ff2d3dfb。独占指定报告/同名analysis；REA skill与共同/复用/静态安全规则适用，已有→实际缺口及四分报告、最小稀疏取证；不改共享/主树/生产ROM配置模型、不创建下级agent，其他agent同时工作勿撤销，精确独占提交commit/验证/未知/clean，接近提交提前报后继种子。


## 预备完整任务书 I04（有前置，未启动）

独占reverse/reports/ap01/saver-time2-lifetime-review-i04-0041-20261024.md及reverse/analysis/saver-time2-lifetime-review-i04-0041-20261024/。

待I03整合后，新独立agent只复核同Time2 type2f creator/callback/DELETE的旧覆盖范围与本轮必要ABI/清理精度；旧guide creator与weather evidence[22] DELETE已留，A15/A16已有登记，不算新恢复。ctx40/wrapper20按同对象证据核，不套H08 type2/H05 type4/H01 type19释放。ctx最终free或上层leave连接无种子保持未知，不扩根析构全扫，新功能0。

仅准备不计运行，派发前整合前置/再核重叠。最新管理HEAD新建独占树re0041-ID小写、分支codex/re-0041-ID小写，根D:/CodexHome/visualizations/2026/10/23/01a1691a-e178-7710-86c0-84c2ff2d3dfb。独占指定报告/同名analysis；REA skill与共同/复用/静态安全规则适用，已有→实际缺口及四分报告、最小稀疏取证；不改共享/主树/生产ROM配置模型、不创建下级agent，其他agent同时工作勿撤销，精确独占提交commit/验证/未知/clean，接近提交提前报后继种子。
