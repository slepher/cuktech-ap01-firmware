# 0041 六路滚动管理（2026-10-23恢复）

用户最新授权恢复持续六路推进，取代历史收尾暂停与三路上限。原管理交接已归档至 rolling-task-history-0041-20261023.md。主窗口只管理，不作函数逆向或技术语义判断。环境共7席，主窗口1席，研究/复核6席。最新批次六项均已整合；后继任务经过复用筛选后启动，真实状态见运行快照。

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
|A33|/root/a33_photo_source|b673714|照片新源接入ABI|
|A32|/root/a32_accounting_review|3ba6b96|计量合同独立复核|
|D13|/root/d13_pixel_source|b673714|Pixel候选来源比对|
|E11|/root/e11_round3_review|3ba6b96|较晚round3覆盖独立复核|
|G10|/root/g10_ready_review|3ba6b96|ready接入独立复核|
|H10|type2 timer创建/更新实际缺口|准备立即补位|

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

## 当前完整任务书 A32（已启动，基线3ba6b96）

树D:/CodexHome/visualizations/2026/10/23/01a1691a-e178-7710-86c0-84c2ff2d3dfb/re0041-a32；分支codex/re-0041-a32；基线必须为启动时最新整合提交，报告后记录SHA，预备阶段不建旧基线树。独占reverse/reports/ap01/image-cache-accounting-review-a32-0041-20261024.md及reverse/analysis/image-cache-accounting-review-a32-0041-20261024/。

新agent独立技术复核：A30真正新增计量callback安装身份、参数返回单位、占用增减到容量预算门数据合同；A23/A27/A28 cleanup及A29失效调用链直接继承。不扩排序/heap或重导已有窗口。

正式报告交付后据其最终新增/纠正清单收缩，不按任务标题认定完成或扩大。先已有→复核缺口，逐项接受/纠正/未核，必要旧字节复核标复核、新增功能0；四分类报告、独占证据、必要验证和明确路径提交，报告commit/未知/clean。可靠合同直接引用，不重复整函数导出/源码资源复制/机械账。无必要复核则主窗口立即换真实缺口，保持六路，不无限复核纯重复材料。共同静态/隔离/安全规则适用，不创建下级agent，不改主树共享/ROM生产配置模型，无SIM/构建/历史回放/设备/外网。

## 当前完整任务书 E11（已启动，基线3ba6b96）

树D:/CodexHome/visualizations/2026/10/23/01a1691a-e178-7710-86c0-84c2ff2d3dfb/re0041-e11；分支codex/re-0041-e11；基线为启动时最新整合提交。独占reverse/reports/ap01/ctk-round3-coverage-review-e11-0041-20261024.md及reverse/analysis/ctk-round3-coverage-review-e11-0041-20261024/。

E10现已确认其候选为旧导航覆盖，后继不再重复根退出搜索；E11改为尚未经独立技术复核的E09纠正。只核round3 Evidence ev_dac9ee80…15c3确属同ROM与profile/函数完整body a00a12d0..a00a24a5、a00a1aa8调用/s0-e4保存槽读取+0xa/+0x12链早已有留存、旧二轮截断在a00a1450既有SUB64，及E07/E08仅retained body边界结论不能外推此前分析缺失。E01–E08消费者合同直接引用，不重做CTK/全字节扫描/整函数导出，不将未发现+34/+38等同不存在。重点是技术证据范围/身份与局部厂商字校核，不再制作旧函数清单。先已有→复核缺口，四分类报告、逐项接受纠正未核、新增功能0，必要静态验证与独占提交，报告commit/验证/未知/clean。共同安全/隔离规则适用，不创建下级agent、不改主树共享/ROM生产配置模型，无SIM/构建/回放/设备/外网。

## 当前完整任务书 G10（已启动，基线3ba6b96）

树D:/CodexHome/visualizations/2026/10/23/01a1691a-e178-7710-86c0-84c2ff2d3dfb/re0041-g10；分支codex/re-0041-g10；基线必须为启动时最新整合提交，报告后记录SHA，预备阶段不建旧基线树。独占reverse/reports/ap01/display-ready-review-g10-0041-20261024.md及reverse/analysis/display-ready-review-g10-0041-20261024/。

新agent独立技术复核：G09把a009ec98 watcher+14 fd-bucket注册与factory-test旧initializer a005c704..c780 ready消费者的绑定；旧ev_dc0e汇编已留存不算发现后端，只核未认证对象身份、th.addsl/th.lrw与callback ABI。G07/G08 poll业务callback和退出合同继承，不扩所有fd或运行时ready。

正式报告交付后据其最终新增/纠正清单收缩，不按任务标题认定完成或扩大。先已有→复核缺口，逐项接受/纠正/未核，必要旧字节复核标复核、新增功能0；四分类报告、独占证据、必要验证和明确路径提交，报告commit/未知/clean。可靠合同直接引用，不重复整函数导出/源码资源复制/机械账。无必要复核则主窗口立即换真实缺口，保持六路，不无限复核纯重复材料。共同静态/隔离/安全规则适用，不创建下级agent，不改主树共享/ROM生产配置模型，无SIM/构建/历史回放/设备/外网。

## 当前完整任务书 A33（已启动，基线b673714）

树D:/CodexHome/visualizations/2026/10/23/01a1691a-e178-7710-86c0-84c2ff2d3dfb/re0041-a33；分支codex/re-0041-a33；基线为本任务书提交。独占reverse/reports/ap01/photo-source-abi-a33-0041-20261024.md及reverse/analysis/photo-source-abi-a33-0041-20261024/。

A29/A31明确留存照片主旋钮调用a00ed7f4的新源实参custom0未可信。photo-evidence-round3 ev_e3db…、main/detail-knob round2、最终ZIP照片重建与较晚round3先继承。仅核这一个已知正常照片分支到image setter的新源身份、厂商指令、实参ABI与借用/复制连接；A29已闭旧源失效、A23–A28 decoder/cleanup合同不重做，不重做资源提取/PNG解码/照片分类。不把较早custom0当较晚仍未知，先查最新完整body；若已有覆盖直接引用结束。保留实际切页时序/执行命中未知，不扩全旋钮函数。

先已有→解释行为→局限→精确缺口，四分类交付，必要局部静态验证，不重复整函数/源码/资源/哈希账。无增量报覆盖不擅自换题，完成及时提交供立即补位。共同安全/隔离/独占输出规则适用，不创建下级agent、不改主树共享/生产ROM配置模型，无SIM/构建/历史回放/设备/外网。提交明确独占文件，报告commit/验证/未知/clean后结束。

## 当前完整任务书 D13（已启动，基线b673714）

树D:/CodexHome/visualizations/2026/10/23/01a1691a-e178-7710-86c0-84c2ff2d3dfb/re0041-d13；分支codex/re-0041-d13；基线为本任务书提交。独占reverse/reports/ap01/pixel-source-auth-d13-0041-20261024.md及reverse/analysis/pixel-source-auth-d13-0041-20261024/。

A25/A26默认raw/free/独立align表绑定与Pixel/raw析构、A30计量字段已有ROM合同，准确库来源匹配尚未认证；F07/F08只认证候选显示/list差异，不等于draw-buffer来源。仅将这些已知draw-buffer默认handler/字段/对齐/清理合同与本地WSL Ubuntu-24.04候选/home/slepher/nuttx-ap01-sim/apps/graphics/lvgl/lvgl的LVGL9.2.1实现逐项比对，复用候选身份，不重做display/list认证或整库排除。候选根只读（WSL访问必要时require_escalated，已有静态读取授权），禁止启动SIM/构建/网络/修配置。源码不能覆盖ROM差异；不匹配明确字段/ABI差异，不重读完整ROM函数或复制整源码。

先已有→解释行为→局限→精确缺口，四分类交付，必要局部静态验证，不重复整函数/源码/资源/哈希账。无增量报覆盖不擅自换题，完成及时提交供立即补位。共同安全/隔离/独占输出规则适用，不创建下级agent、不改主树共享/生产ROM配置模型，无SIM/构建/历史回放/设备/外网。提交明确独占文件，报告commit/验证/未知/clean后结束。

## 当前完整任务书 H10（待启动，H09已整合）

树D:/CodexHome/visualizations/2026/10/23/01a1691a-e178-7710-86c0-84c2ff2d3dfb/re0041-h10；分支codex/re-0041-h10；基线为启动时最新整合提交。独占reverse/reports/ap01/time1-timer-lifecycle-h10-0041-20261024.md及reverse/analysis/time1-timer-lifecycle-h10-0041-20261024/。

H08/H09 type2/time1的136B ctx与20B wrapper以及DELETE先借ctx+78再timer_delete已闭；真正未核为ctx+78 timer的实际创建安装、callback主要正常更新与page/ctx身份。本题只补这条timer创建→正常callback/数据使用→既有删除借用连接。先查pass3 type2构造附近、weather-calendar-complete、page-logic-evidence/asset-index的lv_ui_time1_update_wx_data_cb、最终ZIP及较晚round3，已有登记/天气callback a00ab754全继承，不重做分类显示/资源/DELETE。不套用type4/type19，正常主app teardown触发仍归共同未知，不再搜天气DELETE上层。若创建/更新旧证据已解释，只局部核ABI/厂商字/字段接入；若无真实callback种子有界交付，不泛扫所有timer。四分类报告、必要静态验证、独占提交并报告commit/验证/未知/clean。共同安全/隔离规则适用，不创建下级agent、不改主树共享/生产ROM配置模型，无SIM/构建/回放/设备/网络，不重复整函数导出/复制资源或源码。
