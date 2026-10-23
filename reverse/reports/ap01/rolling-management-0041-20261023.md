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
|C25|/root/e17_uv_time_review（运行）|29002d0|既有区域变换的局部候选来源认证|
|D22|/root/g16_fb_file_review（运行）|9f76584|独立核D21属性映射与四项来源差异|
|A52|/root/h16_clock_source_review（派发中）|本次启动提交|独立复核A50 reader read/seek/缓存持有ABI|
|I01|/root/a46_cache_drop（运行）|92e733a|启动就绪分支旧成果→实际缺口与必要接入核实|
|A53|/root/a47_reader_mode（运行）|85cf93c|独立复核A51 drop/drop_all局部候选映射|
|A54|/root/d19_backlight_animation（运行）|aabdfcd|reader前缀及open/close局部候选认证，不接A50内部消费|

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


## 当前完整任务书 A52（A50已整合，立即接替）

独占reverse/reports/ap01/photo-reader-consumer-review-a52-0041-20261024.md及reverse/analysis/photo-reader-consumer-review-a52-0041-20261024/。

待A50整合后，新独立agent只复核同reader进入a008b888的ABI、D+14 read(D,H,dst,want,&count)、必要seek/config/C持有/游标和A47归还连接。具体D实例/真实mode1照片仍未知；继承A47/A49构造析构，不扩解码/所有失败/文件系统，新功能0。

仅准备，不计运行。实际派发前整合前置并再核重叠，使用最新管理HEAD新建独占树re0041-ID小写/分支codex/re-0041-ID小写，根D:/CodexHome/visualizations/2026/10/23/01a1691a-e178-7710-86c0-84c2ff2d3dfb。独占指定报告/同名analysis。REA skill与共同/复用规则适用；先已有出处→行为→局限→缺口、四分报告、只必要稀疏原字节/源行；静态安全边界、不创建下级agent、不改共享/主树/生产ROM配置模型，其他agent同时工作勿撤销。独占精确提交commit/验证/未知/clean；接近提交预告后继，主体已覆盖则收缩结束不扩扫。


## 当前完整任务书 A53（A51已整合，立即接替）

独占reverse/reports/ap01/image-cache-drop-source-review-a53-0041-20261024.md及reverse/analysis/image-cache-drop-source-review-a53-0041-20261024/。

待A51整合后，新独立agent只核backend drop/drop_all候选3文件必要行映射、warning与整树/链释放责任及来源强度；A46/A48原行为继承，不重核整函数/复制全源码，不扩版本或无xref消费者。新功能0/整库排除0。

仅准备，不计运行。实际派发前整合前置并再核重叠，使用最新管理HEAD新建独占树re0041-ID小写/分支codex/re-0041-ID小写，根D:/CodexHome/visualizations/2026/10/23/01a1691a-e178-7710-86c0-84c2ff2d3dfb。独占指定报告/同名analysis。REA skill与共同/复用规则适用；先已有出处→行为→局限→缺口、四分报告、只必要稀疏原字节/源行；静态安全边界、不创建下级agent、不改共享/主树/生产ROM配置模型，其他agent同时工作勿撤销。独占精确提交commit/验证/未知/clean；接近提交预告后继，主体已覆盖则收缩结束不扩扫。


## 当前完整任务书 D22（D21已整合，立即接替）

独占reverse/reports/ap01/backlight-animation-source-review-d22-0041-20261024.md及reverse/analysis/backlight-animation-source-review-d22-0041-20261024/。

待D21整合后，新独立agent只核property3e/selector20000的候选定义与ROMwrapper、动画descriptor size/early_apply/start顺序/repeat超期余时四项来源差异及其证据强度。D19/D20继承；不能候选覆盖ROM/推断真实视觉效果、控件类型或ctx free，不扩style引擎，新功能0。

仅准备，不计运行。实际派发前整合前置并再核重叠，使用最新管理HEAD新建独占树re0041-ID小写/分支codex/re-0041-ID小写，根D:/CodexHome/visualizations/2026/10/23/01a1691a-e178-7710-86c0-84c2ff2d3dfb。独占指定报告/同名analysis。REA skill与共同/复用规则适用；先已有出处→行为→局限→缺口、四分报告、只必要稀疏原字节/源行；静态安全边界、不创建下级agent、不改共享/主树/生产ROM配置模型，其他agent同时工作勿撤销。独占精确提交commit/验证/未知/clean；接近提交预告后继，主体已覆盖则收缩结束不扩扫。


## 当前完整任务书 C25（已有行为验收已整合，立即接替）

独占reverse/reports/ap01/region-transform-source-c25-0041-20261024.md及reverse/analysis/region-transform-source-c25-0041-20261024/。

G01/G02已经恢复a00dca48四点变换/父链/包围区域和相关缩放旋转，旧C22未知已解决，不能再当新增功能。只核本地LVGL9.2.1对应区域变换家族必要源码/属性定义，认证四word区域/旗标1/右下+1无减1/运算宽度与候选差异及配置条件。先查近期来源报告，已有匹配引用；不重做11函数/厂商字/物理刷新、无整源码复制/整库排除。

仅准备，不计运行。实际派发前整合前置并再核重叠，使用最新管理HEAD新建独占树re0041-ID小写/分支codex/re-0041-ID小写，根D:/CodexHome/visualizations/2026/10/23/01a1691a-e178-7710-86c0-84c2ff2d3dfb。独占指定报告/同名analysis。REA skill与共同/复用规则适用；先已有出处→行为→局限→缺口、四分报告、只必要稀疏原字节/源行；静态安全边界、不创建下级agent、不改共享/主树/生产ROM配置模型，其他agent同时工作勿撤销。独占精确提交commit/验证/未知/clean；接近提交预告后继，主体已覆盖则收缩结束不扩扫。


## 当前完整任务书 A54（A47/A49已整合，立即接替）

独占reverse/reports/ap01/photo-reader-source-a54-0041-20261024.md及reverse/analysis/photo-reader-source-a54-0041-20261024/。

A47/A49已恢复reader前缀构造/归还，A50/A52若尚运行则其内部消费不重复接管。只作本地LVGL9.2.1 lv_fs相关前缀/driver注册槽/open/close/缓存布局到A47/A49可靠ROM合同的局部来源认证；先查旧complete/ZIP/近期source报告。候选名/ABI不能代替ROM实参callback(D,H)，具体实例/精确版本仍未知；不全文件系统/所有缓存算法/全源码复制/ROM重导。

仅准备，不计运行。实际派发前整合前置并再核重叠，使用最新管理HEAD新建独占树re0041-ID小写/分支codex/re-0041-ID小写，根D:/CodexHome/visualizations/2026/10/23/01a1691a-e178-7710-86c0-84c2ff2d3dfb。独占指定报告/同名analysis。REA skill与共同/复用规则适用；先已有出处→行为→局限→缺口、四分报告、只必要稀疏原字节/源行；静态安全边界、不创建下级agent、不改共享/主树/生产ROM配置模型，其他agent同时工作勿撤销。独占精确提交commit/验证/未知/clean；接近提交预告后继，主体已覆盖则收缩结束不扩扫。


## 当前完整任务书 I01（2026-10-24，立即接替）

树D:/CodexHome/visualizations/2026/10/23/01a1691a-e178-7710-86c0-84c2ff2d3dfb/re0041-i01；分支codex/re-0041-i01；基线本任务书启动提交。独占reverse/reports/ap01/boot-ready-increment-i01-0041-20261024.md及reverse/analysis/boot-ready-increment-i01-0041-20261024/。

先优先复用guide-complete boot/证据、system-complete boot_final、page-logic、main-knob/较晚round3/pass3/近期报告/最终ZIP相应basename。旧guide已知a00a7472 timer1000ms、无device-ready分支计数两次、a00a73fe揭示应用并删boot；system已有configured与a00b2ea6→a00b2f48 index8，均不得首次发现。SIM固定2秒就绪是替代，不等于ROM原就绪条件恢复。主窗口在近期reports仅按两地址未命中，此搜索不证明此前未分析。

任务先给已有出处→行为→局限→精确缺口对照；只针对该正常callback的device-ready条件、实际callee/返回、挂接参数与完成次序检查旧证据是否已闭合。已有完整行为直接引用；只补不可信指令/必要接入ABI/字段/正常分支。若已无必要增量报已覆盖，不扩boot/硬件初始化/全驱动/所有页面；真实物理ready效果不能静态代替。不重新导整callback/全资源/分类表/源码，不运行SIM/构建/回放/ROM/设备/外网。

REA skill及本文共同/复用规则全适用，四分报告；旧字节重核标复核不计新增。独占worktree与输出、不改共享/主树/生产ROM配置模型、不创建下级agent；其他agent同时工作勿撤销。必要静态验证、精确路径提交、回报commit/验证/未知/clean；接近提交提前给范围重叠与后继种子，无种子不扩扫。


## 预备完整任务书 C24（有前置，未启动）

独占reverse/reports/ap01/text-entry-source-review-c24-0041-20261024.md及reverse/analysis/text-entry-source-review-c24-0041-20261024/。

待C23整合后，新独立agent只核正常格式化入口/两遍格式化/len+1申请/label持有/static标记与本地LVGL候选映射；核va_copy及配置/布局解释强度，尤其ROM+5c mask10与候选bitfield差异不能覆盖。不重做C13/C14字节/完整printf或GUI，新功能0。

仅准备不计运行。实际派发前整合前置并再核重叠，最新管理HEAD创建独占树re0041-ID小写/分支codex/re-0041-ID小写，根D:/CodexHome/visualizations/2026/10/23/01a1691a-e178-7710-86c0-84c2ff2d3dfb。独占指定报告及同名analysis。REA skill、共同/复用/安全规则全适用；已有→实际缺口与四分报告、只必要稀疏证据，不改共享/主树/生产ROM配置模型、不创建下级agent；其他agent同时工作勿撤销。独占精确提交commit/验证/未知/clean，接近提交提前建议。


## 预备完整任务书 C26（有前置，未启动）

独占reverse/reports/ap01/region-transform-source-review-c26-0041-20261024.md及reverse/analysis/region-transform-source-review-c26-0041-20261024/。

待C25整合后，新独立agent只核G01/G02可靠行为到本地候选必要行/属性/flags/坐标与宽度映射及差异强度，不重复11函数与厂商字恢复，不认证精确版本或整库排除，新功能0。

仅准备不计运行。实际派发前整合前置并再核重叠，最新管理HEAD创建独占树re0041-ID小写/分支codex/re-0041-ID小写，根D:/CodexHome/visualizations/2026/10/23/01a1691a-e178-7710-86c0-84c2ff2d3dfb。独占指定报告及同名analysis。REA skill、共同/复用/安全规则全适用；已有→实际缺口与四分报告、只必要稀疏证据，不改共享/主树/生产ROM配置模型、不创建下级agent；其他agent同时工作勿撤销。独占精确提交commit/验证/未知/clean，接近提交提前建议。


## 预备完整任务书 A55（有前置，未启动）

独占reverse/reports/ap01/photo-reader-source-review-a55-0041-20261024.md及reverse/analysis/photo-reader-source-review-a55-0041-20261024/。

待A54整合后，新独立agent只核reader前缀/open/close/注册槽/缓存布局候选映射与配置条件，callback(D,H)以A47/A49 ROM为据；A50内部read消费/A52复核直接继承，不扩全部文件系统/具体D实例，无精确版本/整库排除，新功能0。

仅准备不计运行。实际派发前整合前置并再核重叠，最新管理HEAD创建独占树re0041-ID小写/分支codex/re-0041-ID小写，根D:/CodexHome/visualizations/2026/10/23/01a1691a-e178-7710-86c0-84c2ff2d3dfb。独占指定报告及同名analysis。REA skill、共同/复用/安全规则全适用；已有→实际缺口与四分报告、只必要稀疏证据，不改共享/主树/生产ROM配置模型、不创建下级agent；其他agent同时工作勿撤销。独占精确提交commit/验证/未知/clean，接近提交提前建议。


## 预备完整任务书 I02（有前置，未启动）

独占reverse/reports/ap01/boot-ready-review-i02-0041-20261024.md及reverse/analysis/boot-ready-review-i02-0041-20261024/。

待I01整合后，新独立agent只核其实际补充或覆盖结论：旧guide/system已有启动timer/计数/结束/configured/index8直接引用，SIM固定2s不等于原ROM条件；只核实际新增接入ABI/条件/原字/次序或旧证据范围，不扩驱动/设备初始化，不把没执行等于未分析，新功能0。

仅准备不计运行。实际派发前整合前置并再核重叠，最新管理HEAD创建独占树re0041-ID小写/分支codex/re-0041-ID小写，根D:/CodexHome/visualizations/2026/10/23/01a1691a-e178-7710-86c0-84c2ff2d3dfb。独占指定报告及同名analysis。REA skill、共同/复用/安全规则全适用；已有→实际缺口与四分报告、只必要稀疏证据，不改共享/主树/生产ROM配置模型、不创建下级agent；其他agent同时工作勿撤销。独占精确提交commit/验证/未知/clean，接近提交提前建议。
