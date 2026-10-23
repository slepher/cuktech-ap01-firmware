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
|A43|完整任务书就绪|准备立即补位|
|A42|完整任务书就绪|准备立即补位|
|D17|完整任务书就绪|准备立即补位|
|E16|完整任务书就绪|准备立即补位|
|G14|设备poll条件链独立复核|准备立即补位|
|H14|完整任务书就绪|准备立即补位|

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

## 当前完整任务书 G14（准备立即补位，G13已整合）

树D:/CodexHome/visualizations/2026/10/23/01a1691a-e178-7710-86c0-84c2ff2d3dfb/re0041-g14；分支codex/re-0041-g14；基线为启动时最新整合任务书提交，届时记录SHA，不提前建旧基线树。独占reverse/reports/ap01/display-device-poll-review-g14-0041-20261024.md及reverse/analysis/display-device-poll-review-g14-0041-20261024/。

独立复核G13实际目标fd/设备ops身份、一个设备poll/revents写者到已安装通知callback的新增接入或精确间接断边。G07/G09/G11/G12 registration/materializer/consumer原序全继承；不能由登记成功/静态指针推实际ready，不扩其他设备/IRQ/全部VFS。

正式报告后据其继承/真正新增/未知清单收缩，先已有→精确缺口，四分类报告。独立复核新增功能0，仅必要旧字节/源行锚点，不重复整函数/资源源码复制/机械账；研究无增量及时覆盖交付主窗口换题补位，不凑时长函数。共同静态/安全/隔离/独占规则适用，不创建下级agent、不改主树共享/生产ROM配置模型，无SIM/构建/历史回放/设备/外网；必要验证后独占提交报告commit/验证/未知/clean。

## 当前完整任务书 H14（准备立即补位，H13已整合）

树D:/CodexHome/visualizations/2026/10/23/01a1691a-e178-7710-86c0-84c2ff2d3dfb/re0041-h14；分支codex/re-0041-h14；基线为启动时最新整合任务书提交，届时记录SHA，不提前建旧基线树。独占reverse/reports/ap01/weather-clock-review-h14-0041-20261024.md及reverse/analysis/weather-clock-review-h14-0041-20261024/。

独立复核H13正常时钟helper调用/原厂商字、两次除1000与64位返回/URL%lld接入单位可证范围；旧条款/较晚反编译与URL摘要合同继承，不套用E14 uv deadline时钟源/epoch，不推实际外网请求或时间回放。

正式报告后据其继承/真正新增/未知清单收缩，先已有→精确缺口，四分类报告。独立复核新增功能0，仅必要旧字节/源行锚点，不重复整函数/资源源码复制/机械账；研究无增量及时覆盖交付主窗口换题补位，不凑时长函数。共同静态/安全/隔离/独占规则适用，不创建下级agent、不改主树共享/生产ROM配置模型，无SIM/构建/历史回放/设备/外网；必要验证后独占提交报告commit/验证/未知/clean。

## 当前完整任务书 A42（准备立即补位，2026-10-24）

树D:/CodexHome/visualizations/2026/10/23/01a1691a-e178-7710-86c0-84c2ff2d3dfb/re0041-a42；分支codex/re-0041-a42；基线为本任务书提交。独占reverse/reports/ap01/photo-destroy-review-a42-0041-20261024.md及reverse/analysis/photo-destroy-review-a42-0041-20261024/。

独立复核A41旧O memory mode0：从owner+5c持旧对象、先旧source失效、O+10门→free(O)、依次清+5c/+74后才新源构造。A33/A35/A37/A39已有源/构造持有合同直接引用，不重导setter/算法；原输入借用不free，内部派生区不另free。非零mode callee/页面DELETE触发/heap保持未知，复核新增0。

先已有→行为→局限→实际缺口，四分类报告，独立复核新增功能0；已有可靠合同引用，不重复整函数/源码/资源导出或机械账。必要原字节/源行锚点验证，无增量及时覆盖交付主窗口补位，不凑时长/函数。共同静态/安全/隔离规则适用，不创建下级agent、不改主树共享/生产ROM配置模型，无SIM/构建/历史回放/设备/外网；独占提交报告commit/验证/未知/clean。

## 当前完整任务书 A43（准备立即补位，2026-10-24）

树D:/CodexHome/visualizations/2026/10/23/01a1691a-e178-7710-86c0-84c2ff2d3dfb/re0041-a43；分支codex/re-0041-a43；基线为本任务书提交。独占reverse/reports/ap01/image-cache-source-a43-0041-20261024.md及reverse/analysis/image-cache-source-a43-0041-20261024/。

A23/A27/A30/A34/A38及对应独立复核已闭默认image-cache键/计量/链/cleanup，准确库来源尚未认证；F07/F08显示/list与D13/D14 draw-buffer认证不覆盖cache backend。只与本地LVGL9.2.1候选对应image-cache/key与LRU backend源文件/必要头局部比对结构字段、comparator/首word计量/链与callback清理，复用候选身份不重扫整库或重读ROM整函数。WSL Ubuntu-24.04候选/home/slepher/nuttx-ap01-sim/apps/graphics/lvgl/lvgl只读；源码不得覆盖ROM差异，不默认配置/enum宽度相同或整库排除，不复制源码库。

先已有→行为→局限→实际缺口，四分类报告，独立复核新增功能0；已有可靠合同引用，不重复整函数/源码/资源导出或机械账。必要原字节/源行锚点验证，无增量及时覆盖交付主窗口补位，不凑时长/函数。共同静态/安全/隔离规则适用，不创建下级agent、不改主树共享/生产ROM配置模型，无SIM/构建/历史回放/设备/外网；独占提交报告commit/验证/未知/clean。

## 当前完整任务书 E16（准备立即补位，2026-10-24）

树D:/CodexHome/visualizations/2026/10/23/01a1691a-e178-7710-86c0-84c2ff2d3dfb/re0041-e16；分支codex/re-0041-e16；基线为本任务书提交。独占reverse/reports/ap01/uv-time-producer-e16-0041-20261024.md及reverse/analysis/uv-time-producer-e16-0041-20261024/。

E14/E15已闭正常deadline算术和unsigned到期合同，实际loop+140/+144缓存时间生产者/单位仍未知。本题沿已知uv start/dispatch和旧initializer已有callee/retained字段写者，仅补一个实际缓存时间刷新函数→底层source→两word回写→已知deadline读取，先查较晚round3和旧调度/关闭报告。无真实writer种子有界交付，不全ROM字段扫描，不重做heap/callback/close；H13天气clock源与epoch不得套用，时间单位只到实际换算证据。

先已有→行为→局限→实际缺口，四分类报告，独立复核新增功能0；已有可靠合同引用，不重复整函数/源码/资源导出或机械账。必要原字节/源行锚点验证，无增量及时覆盖交付主窗口补位，不凑时长/函数。共同静态/安全/隔离规则适用，不创建下级agent、不改主树共享/生产ROM配置模型，无SIM/构建/历史回放/设备/外网；独占提交报告commit/验证/未知/clean。

## 当前完整任务书 D17（准备立即补位，2026-10-24）

树D:/CodexHome/visualizations/2026/10/23/01a1691a-e178-7710-86c0-84c2ff2d3dfb/re0041-d17；分支codex/re-0041-d17；基线为本任务书提交。独占reverse/reports/ap01/pwm-source-auth-d17-0041-20261024.md及reverse/analysis/pwm-source-auth-d17-0041-20261024/。

D15/D16已闭PWM lower a0136762正常算术/ABI，准确来源仍未认证。本题只比对该正常start/频率duty阈值与必要字段在本地NuttX12.10候选PWM lower或SDK PWM候选的对应实现，识别相符/差异/未匹配与厂商适配范围。候选WSL Ubuntu-24.04 /home/slepher/nuttx-ap01-sim/nuttx（身份复用A13/A14/F07）与D:/Documents/PlatformIO/Projects/bouffalo_sdk（身份复用D07/D11/D12）；只读明确PWM文件/必要头，不扫整盘或复制源码，不默认芯片/版本/编译设置同ROM，不整库排除。候选不存在即明确缺口，不下载构建修环境，不再逆向D15全部算术/stop/停机消费者。

先已有→行为→局限→实际缺口，四分类报告，独立复核新增功能0；已有可靠合同引用，不重复整函数/源码/资源导出或机械账。必要原字节/源行锚点验证，无增量及时覆盖交付主窗口补位，不凑时长/函数。共同静态/安全/隔离规则适用，不创建下级agent、不改主树共享/生产ROM配置模型，无SIM/构建/历史回放/设备/外网；独占提交报告commit/验证/未知/clean。
