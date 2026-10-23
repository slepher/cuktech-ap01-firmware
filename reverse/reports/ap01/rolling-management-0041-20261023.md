# 0041 六路滚动管理（2026-10-23恢复）

用户最新授权恢复持续六路推进，取代历史收尾暂停与三路上限。原管理交接已归档至 rolling-task-history-0041-20261023.md。主窗口只管理，不作函数逆向或技术语义判断。环境共7席，主窗口1席，研究/复核6席。最新批次六项均已整合；后继任务经过复用筛选后启动，真实状态见运行快照。

## 共同规则

只做0041静态功能恢复；禁止执行固件、连接设备/外部服务、漏洞/异常输入/缺陷验证、修改安全检查、ROM、生产代码、构建配置和分析器模型；不推送。只写独占reverse/analysis和reverse/reports/ap01文件。只用自己的独立worktree和分支，每次shell显式workdir并在PowerShell Set-Location。其他agent同时工作，不撤销他人修改、不改主树或共享索引，不创建下级agent、不自行接后继。忽略ROM/证据/工具从主仓库绝对路径只读访问；不复制工作区，不共享可写数据库或切换全局REA。优先留存证据；若工具不能隔离则报告管理者。临时状态/日志放各自独占analysis目录。只恢复正常原程序行为，不擅自修正。

交付列问题/范围/结论、业务行为、函数地址/参数/返回/调用、必要伪代码结构体状态转换、所有权生命周期、可定位证据与原指令、事实/推断/未知、来源与恢复程度、实际静态验证、断边和一个后续闭包。伪代码不是原源码；保留调用顺序、重读、宽度/符号、返回判断、失败/清理和间接ABI。边界/厂商指令须核原字节，不仅信反编译。标准库只有来源可核实才排除，适配/回调仍恢复；不新增哈希清单/复制清单/机械重复证据。不编译项目，不运行历史回放。完成标准为原问题闭包得到有证据答案或明确可定位断边，不能缩成短helper声称完成；不设函数数量或时长配额；主体已覆盖即收缩，已无必要增量即报告已覆盖并结束。

接近提交提前报告结论、剩余验证、阻塞和后继建议。检查差异、必要验证、明确路径git add、提交、报告commit/验证/未知/干净状态后结束。主窗口作范围验收，技术验收由新独立agent。恢复成果可先整合为待复核；不得自验冒称验收。每项完成即整合补位，从启动时最新管理提交创建新树；运行任务不移动基线。语义冲突交agent；回收仅限干净且已整合worktree，分支保留。用户要求收尾即停止派发。

主仓库：D:/Documents/PlatformIO/Projects/cuktech-ap01-firmware。所有任务初始共同研究基线 ab9716e；实际启动基线为含本任务书的管理提交，在派发消息及运行表记录。

## 当前任务书



## 实际运行快照

六个subagent已真实启动且均运行中，主窗口另计。维持六路，完成即整合补位；scope去重不作为空席理由。

|任务|agent|基线|实际范围|
|---|---|---|---|
|A31|/root/a31_cache_invalidation_review|9ea568f|独立技术复核已整合增量|
|A32|独立技术复核|待启动，完整任务书已就绪|
|D12|/root/d12_uart_source_review|9ea568f|独立技术复核已整合增量|
|E11|独立技术复核|待启动，完整任务书已就绪|
|G10|独立技术复核|待启动，完整任务书已就绪|
|H09|独立复核type2 DELETE真实增量|待启动，任务书就绪|

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

## 提前准备的后继队列（未启动，不计并发）

- A31：A29交付后，独立复核其真正新增的调用/同cache身份与实参合同；旧照片Evidence全部继承。
- A32：A30交付后，独立复核计量callback/单位/预算数据合同，继承A27/A28 cleanup。
- D12：D11交付后，独立复核候选分层与来源认证范围，避免以候选低层deinit补ROM callback析构。
- E11：改为E09较晚round3覆盖纠正的独立技术复核，避免重复根退出搜索。
- G10：G09交付后，独立复核正常ready到watcher间接ABI，保留运行时触发未知。
- H09：H08交付后，独立复核旧type2未认证ABI/清理合同，分类/资源不重做。

以上需据正式报告收缩为完整独占任务书；若任务已覆盖且无必要技术增量，则从其他已定位缺口换题，不递归复核纯重复材料。主窗口在每项提交前准备具体任务，保持六路。

## 当前完整任务书 A31（已启动，基线9ea568f）

树D:/CodexHome/visualizations/2026/10/23/01a1691a-e178-7710-86c0-84c2ff2d3dfb/re0041-a31；分支codex/re-0041-a31；基线必须为启动时最新整合提交，报告后记录SHA，预备阶段不建旧基线树。独占reverse/reports/ap01/image-cache-invalidation-review-a31-0041-20261024.md及reverse/analysis/image-cache-invalidation-review-a31-0041-20261024/。

新agent独立技术复核：A29的a00ed7f4 +5c门→getter对象+2c旧源→a00890e8→G+11c image-cache source/class key→a019cfbe连接；G+120另一cache必须分开，旧photo调用/custom0新源实参继承且不补成每次切页必失效。A27/A28内部失效/release/cleanup不重做。

正式报告交付后据其最终新增/纠正清单收缩，不按任务标题认定完成或扩大。先已有→复核缺口，逐项接受/纠正/未核，必要旧字节复核标复核、新增功能0；四分类报告、独占证据、必要验证和明确路径提交，报告commit/未知/clean。可靠合同直接引用，不重复整函数导出/源码资源复制/机械账。无必要复核则主窗口立即换真实缺口，保持六路，不无限复核纯重复材料。共同静态/隔离/安全规则适用，不创建下级agent，不改主树共享/ROM生产配置模型，无SIM/构建/历史回放/设备/外网。

## 当前完整任务书 A32（待启动，正式前序已整合）

树D:/CodexHome/visualizations/2026/10/23/01a1691a-e178-7710-86c0-84c2ff2d3dfb/re0041-a32；分支codex/re-0041-a32；基线必须为启动时最新整合提交，报告后记录SHA，预备阶段不建旧基线树。独占reverse/reports/ap01/image-cache-accounting-review-a32-0041-20261024.md及reverse/analysis/image-cache-accounting-review-a32-0041-20261024/。

新agent独立技术复核：A30真正新增计量callback安装身份、参数返回单位、占用增减到容量预算门数据合同；A23/A27/A28 cleanup及A29失效调用链直接继承。不扩排序/heap或重导已有窗口。

正式报告交付后据其最终新增/纠正清单收缩，不按任务标题认定完成或扩大。先已有→复核缺口，逐项接受/纠正/未核，必要旧字节复核标复核、新增功能0；四分类报告、独占证据、必要验证和明确路径提交，报告commit/未知/clean。可靠合同直接引用，不重复整函数导出/源码资源复制/机械账。无必要复核则主窗口立即换真实缺口，保持六路，不无限复核纯重复材料。共同静态/隔离/安全规则适用，不创建下级agent，不改主树共享/ROM生产配置模型，无SIM/构建/历史回放/设备/外网。

## 当前完整任务书 D12（已启动，基线9ea568f）

树D:/CodexHome/visualizations/2026/10/23/01a1691a-e178-7710-86c0-84c2ff2d3dfb/re0041-d12；分支codex/re-0041-d12；基线必须为启动时最新整合提交，报告后记录SHA，预备阶段不建旧基线树。独占reverse/reports/ap01/uart-channel-source-review-d12-0041-20261024.md及reverse/analysis/uart-channel-source-review-d12-0041-20261024/。

新agent独立技术复核：D11候选SDK分层/具体匹配差异和未认证范围，区分低层deinit/irq_detach与NuttX channel allocator/free/shutdown。候选SDK HEAD/version与D07/D08旧认证直接引用，不拿候选detach填ROM未知，不重读三槽全部原字节或重新扫描所有候选源码。

正式报告交付后据其最终新增/纠正清单收缩，不按任务标题认定完成或扩大。先已有→复核缺口，逐项接受/纠正/未核，必要旧字节复核标复核、新增功能0；四分类报告、独占证据、必要验证和明确路径提交，报告commit/未知/clean。可靠合同直接引用，不重复整函数导出/源码资源复制/机械账。无必要复核则主窗口立即换真实缺口，保持六路，不无限复核纯重复材料。共同静态/隔离/安全规则适用，不创建下级agent，不改主树共享/ROM生产配置模型，无SIM/构建/历史回放/设备/外网。

## 当前完整任务书 E11（待启动，正式前序已整合）

树D:/CodexHome/visualizations/2026/10/23/01a1691a-e178-7710-86c0-84c2ff2d3dfb/re0041-e11；分支codex/re-0041-e11；基线为启动时最新整合提交。独占reverse/reports/ap01/ctk-round3-coverage-review-e11-0041-20261024.md及reverse/analysis/ctk-round3-coverage-review-e11-0041-20261024/。

E10现已确认其候选为旧导航覆盖，后继不再重复根退出搜索；E11改为尚未经独立技术复核的E09纠正。只核round3 Evidence ev_dac9ee80…15c3确属同ROM与profile/函数完整body a00a12d0..a00a24a5、a00a1aa8调用/s0-e4保存槽读取+0xa/+0x12链早已有留存、旧二轮截断在a00a1450既有SUB64，及E07/E08仅retained body边界结论不能外推此前分析缺失。E01–E08消费者合同直接引用，不重做CTK/全字节扫描/整函数导出，不将未发现+34/+38等同不存在。重点是技术证据范围/身份与局部厂商字校核，不再制作旧函数清单。先已有→复核缺口，四分类报告、逐项接受纠正未核、新增功能0，必要静态验证与独占提交，报告commit/验证/未知/clean。共同安全/隔离规则适用，不创建下级agent、不改主树共享/ROM生产配置模型，无SIM/构建/回放/设备/外网。

## 当前完整任务书 G10（待启动，正式前序已整合）

树D:/CodexHome/visualizations/2026/10/23/01a1691a-e178-7710-86c0-84c2ff2d3dfb/re0041-g10；分支codex/re-0041-g10；基线必须为启动时最新整合提交，报告后记录SHA，预备阶段不建旧基线树。独占reverse/reports/ap01/display-ready-review-g10-0041-20261024.md及reverse/analysis/display-ready-review-g10-0041-20261024/。

新agent独立技术复核：G09把a009ec98 watcher+14 fd-bucket注册与factory-test旧initializer a005c704..c780 ready消费者的绑定；旧ev_dc0e汇编已留存不算发现后端，只核未认证对象身份、th.addsl/th.lrw与callback ABI。G07/G08 poll业务callback和退出合同继承，不扩所有fd或运行时ready。

正式报告交付后据其最终新增/纠正清单收缩，不按任务标题认定完成或扩大。先已有→复核缺口，逐项接受/纠正/未核，必要旧字节复核标复核、新增功能0；四分类报告、独占证据、必要验证和明确路径提交，报告commit/未知/clean。可靠合同直接引用，不重复整函数导出/源码资源复制/机械账。无必要复核则主窗口立即换真实缺口，保持六路，不无限复核纯重复材料。共同静态/隔离/安全规则适用，不创建下级agent，不改主树共享/ROM生产配置模型，无SIM/构建/历史回放/设备/外网。

## 当前完整任务书 H09（待启动，H08已整合）

树D:/CodexHome/visualizations/2026/10/23/01a1691a-e178-7710-86c0-84c2ff2d3dfb/re0041-h09；分支codex/re-0041-h09；基线必须为启动时最新整合提交，报告后记录SHA，预备阶段不建旧基线树。独占reverse/reports/ap01/weather-type2-review-h09-0041-20261024.md及reverse/analysis/weather-type2-review-h09-0041-20261024/。

新agent独立技术复核：H08真正补充的type2 ctx/wrapper与a00aba9c DELETE/注销原序；a00ab754完整callback、pass3 type2登记挂接及分类显示全继承，不跨用type4 68B或type19 116B，不重导整callback。

正式报告交付后据其最终新增/纠正清单收缩，不按任务标题认定完成或扩大。先已有→复核缺口，逐项接受/纠正/未核，必要旧字节复核标复核、新增功能0；四分类报告、独占证据、必要验证和明确路径提交，报告commit/未知/clean。可靠合同直接引用，不重复整函数导出/源码资源复制/机械账。无必要复核则主窗口立即换真实缺口，保持六路，不无限复核纯重复材料。共同静态/隔离/安全规则适用，不创建下级agent，不改主树共享/ROM生产配置模型，无SIM/构建/历史回放/设备/外网。
