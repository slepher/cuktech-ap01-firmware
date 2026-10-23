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
|A44|任务书就绪|准备立即补位|
|A45|完整任务书就绪|准备立即补位|
|D18|任务书就绪|准备立即补位|
|E16|完整任务书就绪|准备立即补位|
|G15|完整任务书就绪|准备立即补位|
|H15|任务书就绪|准备立即补位|

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

## 当前完整任务书 E16（准备立即补位，2026-10-24）

树D:/CodexHome/visualizations/2026/10/23/01a1691a-e178-7710-86c0-84c2ff2d3dfb/re0041-e16；分支codex/re-0041-e16；基线为本任务书提交。独占reverse/reports/ap01/uv-time-producer-e16-0041-20261024.md及reverse/analysis/uv-time-producer-e16-0041-20261024/。

E14/E15已闭正常deadline算术和unsigned到期合同，实际loop+140/+144缓存时间生产者/单位仍未知。本题沿已知uv start/dispatch和旧initializer已有callee/retained字段写者，仅补一个实际缓存时间刷新函数→底层source→两word回写→已知deadline读取，先查较晚round3和旧调度/关闭报告。无真实writer种子有界交付，不全ROM字段扫描，不重做heap/callback/close；H13天气clock源与epoch不得套用，时间单位只到实际换算证据。

先已有→行为→局限→实际缺口，四分类报告，独立复核新增功能0；已有可靠合同引用，不重复整函数/源码/资源导出或机械账。必要原字节/源行锚点验证，无增量及时覆盖交付主窗口补位，不凑时长/函数。共同静态/安全/隔离规则适用，不创建下级agent、不改主树共享/生产ROM配置模型，无SIM/构建/历史回放/设备/外网；独占提交报告commit/验证/未知/clean。

## 当前完整任务书 G15（准备，2026-10-24）

树D:/CodexHome/visualizations/2026/10/23/01a1691a-e178-7710-86c0-84c2ff2d3dfb/re0041-g15；分支codex/re-0041-g15；基线为启动时最新整合任务书提交。独占reverse/reports/ap01/fb-file-lifecycle-g15-0041-20261024.md及reverse/analysis/fb-file-lifecycle-g15-0041-20261024/。

G13/G14已闭a01c1368 ops+20 poll、F=file+10与登记槽/通知接入，但具体F正常创建/初始化与close归还未核。本题从同ops表实际open/close槽的真实目标开始（不能把source-xref a0055a14擅自命名为open），只补file+10私有F分配/字段/槽初始化、正常open接入及close对已登记poll槽/对象的清理合同。F05/F07 pathname/flags3/backend fd保存与G07 watcher fd传递全继承，不重做通用VFS路径解析或强行证明运行时fd命中；open真实执行/异步ready保持条件。若槽空/已有覆盖直接引用，不扩所有设备/IRQ。

先已有→行为→局限→精确缺口，四分类报告，复核新增功能0；可靠合同引用，只补必要原字节/源行，不重复整函数/源码资源导出/机械账，无增量及时交付主窗口补位，不凑函数时长。共同静态/安全/隔离规则适用，不创建下级agent、不改主树共享/生产ROM配置模型，无SIM/构建/历史回放/设备/外网；必要验证独占提交报告commit/验证/未知/clean。

## 当前完整任务书 A45（准备，2026-10-24）

树D:/CodexHome/visualizations/2026/10/23/01a1691a-e178-7710-86c0-84c2ff2d3dfb/re0041-a45；分支codex/re-0041-a45；基线为启动时最新整合任务书提交。独占reverse/reports/ap01/photo-class-destroy-a45-0041-20261024.md及reverse/analysis/photo-class-destroy-a45-0041-20261024/。

A33/A37/A41及独立复核已闭构造O与setter替换free；本题只沿旧照片ctx[0] widget实际creator/类常量找到已安装class析构入口→同owner+5c旧O及+74派生区的DELETE清理连接。先复用photo/knob/最终ZIP与较晚round3、H03通用class walker合同；具体照片class若已有完整合同直接引用，只核字段身份/ABI/原序，不重做整个setter或公共DELETE。主app正常退出触发仍为E10/H07共同未知，不再重复root搜索；无实际类/callee种子有界交付，不扩所有GUI/动画/解码算法。

先已有→行为→局限→精确缺口，四分类报告，复核新增功能0；可靠合同引用，只补必要原字节/源行，不重复整函数/源码资源导出/机械账，无增量及时交付主窗口补位，不凑函数时长。共同静态/安全/隔离规则适用，不创建下级agent、不改主树共享/生产ROM配置模型，无SIM/构建/历史回放/设备/外网；必要验证独占提交报告commit/验证/未知/clean。

## 当前完整任务书 D18（准备立即补位，前序已整合）

树D:/CodexHome/visualizations/2026/10/23/01a1691a-e178-7710-86c0-84c2ff2d3dfb/re0041-d18；分支codex/re-0041-d18；基线为启动时最新整合任务书提交。独占reverse/reports/ap01/pwm-source-review-d18-0041-20261024.md及reverse/analysis/pwm-source-review-d18-0041-20261024/。

独立复核D17正常PWM lower的本地候选来源范围：NuttX BL602差异、SDK PWM v2寄存器局部对应与ROM 80MHz binary64/居中duty不由候选证明。D15/D16算术及旧source身份继承，只核D17具体源行/有界匹配范围，不重复全候选搜索、ROM导出或整库排除。

先已有→行为→局限→精确缺口，四分类报告，复核新增功能0；可靠合同引用，只补必要原字节/源行，不重复整函数/源码资源导出/机械账，无增量及时交付主窗口补位，不凑函数时长。共同静态/安全/隔离规则适用，不创建下级agent、不改主树共享/生产ROM配置模型，无SIM/构建/历史回放/设备/外网；必要验证独占提交报告commit/验证/未知/clean。

## 当前完整任务书 H15（准备立即补位，前序已整合）

树D:/CodexHome/visualizations/2026/10/23/01a1691a-e178-7710-86c0-84c2ff2d3dfb/re0041-h15；分支codex/re-0041-h15；基线为启动时最新整合任务书提交。独占reverse/reports/ap01/clock-source-offset-h15-0041-20261024.md及reverse/analysis/clock-source-offset-h15-0041-20261024/。

H13/H14天气ID0算术与E16 uv ID1缓存刷新分开；E16明确只核a002696a ID1→a002645a分支，不追底层。本题只补a002645a正常输出表示/单位，以及a002696a ID0 offset合并/归一化所用62fc5c74字段的有定位来源写入连接；先查旧天气/较晚round3/现有source候选与retained调用，已有合同直接引用。无真实offset writer种子就明确停边，不全ROM字段扫描或硬件/校时政策推测，epoch/厂商时钟精确来源无证保持未知，不跑时间回放。

先已有→行为→局限→精确缺口，四分类报告，复核新增功能0；可靠合同引用，只补必要原字节/源行，不重复整函数/源码资源导出/机械账，无增量及时交付主窗口补位，不凑函数时长。共同静态/安全/隔离规则适用，不创建下级agent、不改主树共享/生产ROM配置模型，无SIM/构建/历史回放/设备/外网；必要验证独占提交报告commit/验证/未知/clean。

## 当前完整任务书 A44（准备立即补位，前序已整合）

树D:/CodexHome/visualizations/2026/10/23/01a1691a-e178-7710-86c0-84c2ff2d3dfb/re0041-a44；分支codex/re-0041-a44；基线为启动时最新整合任务书提交。独占reverse/reports/ap01/image-cache-source-review-a44-0041-20261024.md及reverse/analysis/image-cache-source-review-a44-0041-20261024/。

独立复核A43默认image-cache/backend与LVGL9.2.1候选局部匹配/差异范围、enum/字段ABI强度和不作未改认证结论。F07/F08及D13/D14候选身份和A23/A27/A30/A34/A38合同继承，只读A43相应源行/必要头，不重扫整库、复制源码或重读完整ROM，不以候选补ROM差异。

先已有→行为→局限→精确缺口，四分类报告，复核新增功能0；可靠合同引用，只补必要原字节/源行，不重复整函数/源码资源导出/机械账，无增量及时交付主窗口补位，不凑函数时长。共同静态/安全/隔离规则适用，不创建下级agent、不改主树共享/生产ROM配置模型，无SIM/构建/历史回放/设备/外网；必要验证独占提交报告commit/验证/未知/clean。

## 预备完整任务书 E17（待E16正式报告整合，不计运行）

树D:/CodexHome/visualizations/2026/10/23/01a1691a-e178-7710-86c0-84c2ff2d3dfb/re0041-e17；分支codex/re-0041-e17；基线为启动时最新整合任务书提交。独占reverse/reports/ap01/uv-time-producer-review-e17-0041-20261024.md及reverse/analysis/uv-time-producer-review-e17-0041-20261024/。

新agent独立复核E16真实writer a0098b60→a019e1a2→a002696a(1,out8)、UMAR64组合返回pair、除数0:0xf4240的helper接口→loop+140/+144回写及dispatch前消费连接。H13/H14 ID0 offset分支与E14/E15期限/unsigned比较全继承，不把来源/epoch或单位相互套用；helper若仅必要路径支持unsigned quotient，保持推断/未认证完整算法范围。H15负责a002645a/offset下层，E17不重复核其内部。先已有→复核缺口，四分类逐项接受纠正未核/新增功能0，必要稀疏原字节/厂商规则/ABI验证，不重导全函数、heap或close。共同静态/安全/隔离规则适用，不创建下级agent、不改主树共享/生产ROM配置模型，无SIM/构建/历史回放/设备/外网；独占提交报告commit/验证/未知/clean。
