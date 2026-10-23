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
|A46|任务书就绪|准备立即补位|
|A47|任务书就绪|准备立即补位|
|D19|任务书就绪|准备立即补位|
|E17|任务书就绪|准备立即补位|
|G16|任务书就绪|准备立即补位|
|H16|任务书就绪|准备立即补位|

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

## 当前完整任务书 E17（准备立即补位，E16已整合）

树D:/CodexHome/visualizations/2026/10/23/01a1691a-e178-7710-86c0-84c2ff2d3dfb/re0041-e17；分支codex/re-0041-e17；基线为启动时最新整合任务书提交。独占reverse/reports/ap01/uv-time-producer-review-e17-0041-20261024.md及reverse/analysis/uv-time-producer-review-e17-0041-20261024/。

新agent独立复核E16真实writer a0098b60→a019e1a2→a002696a(1,out8)、UMAR64组合返回pair、除数0:0xf4240的helper接口→loop+140/+144回写及dispatch前消费连接。H13/H14 ID0 offset分支与E14/E15期限/unsigned比较全继承，不把来源/epoch或单位相互套用；helper若仅必要路径支持unsigned quotient，保持推断/未认证完整算法范围。H15负责a002645a/offset下层，E17不重复核其内部。先已有→复核缺口，四分类逐项接受纠正未核/新增功能0，必要稀疏原字节/厂商规则/ABI验证，不重导全函数、heap或close。共同静态/安全/隔离规则适用，不创建下级agent、不改主树共享/生产ROM配置模型，无SIM/构建/历史回放/设备/外网；独占提交报告commit/验证/未知/clean。

## 当前完整任务书 G16（准备立即补位，2026-10-24）

树D:/CodexHome/visualizations/2026/10/23/01a1691a-e178-7710-86c0-84c2ff2d3dfb/re0041-g16；分支codex/re-0041-g16；基线为本任务书提交。独占reverse/reports/ap01/fb-file-review-g16-0041-20261024.md及reverse/analysis/fb-file-review-g16-0041-20261024/。

独立复核G15 ops实际open=a012fabc/close=a012f3e0、16B F零化/字段初始化、D链和file+10持有、close lower可选调用→摘链→free F原序。G13/G14 poll槽teardown继承；close本体未遍历槽不能外推所有lower callback无清理，更不能作缺陷结论。实际open执行、poll teardown与close时序仍未知，只必要稀疏ABI/字段锚点，新增功能0。

先已有→行为→局限→精确缺口，四分类报告，复核新增功能0；可靠合同引用，只补必要原字节/源行，不重复整函数/源码/资源导出/机械账。无增量及时覆盖交付主窗口补位，不凑函数时长。共同静态/安全/隔离规则适用，不创建下级agent、不改主树共享/生产ROM配置模型，无SIM/构建/历史回放/设备/外网；必要验证独占提交报告commit/验证/未知/clean。

## 当前完整任务书 D19（准备立即补位，2026-10-24）

树D:/CodexHome/visualizations/2026/10/23/01a1691a-e178-7710-86c0-84c2ff2d3dfb/re0041-d19；分支codex/re-0041-d19；基线为本任务书提交。独占reverse/reports/ap01/backlight-animation-d19-0041-20261024.md及reverse/analysis/backlight-animation-d19-0041-20261024/。

早期buzzer/backlight-round2明确a00f43d4(timer)读timer+c ctx与ctx+8c亮度、调用setter并创建2000ms动画，动画/UI所有权未闭。管理在当前reports/rehost/tooling按地址仅旧两报告命中、ZIP文本未命中，此范围不表示从未分析。只补此正常callback的动画descriptor/对象userdata、exec/ready主要更新与完成/清理身份；先查旧system/guide/settings/page-logic与较晚round3按地址/字段，已解释的背光setter/PWM全继承，不恢复所有动画或所有UI，不能拿SIM动画当ROM生命周期。

先已有→行为→局限→精确缺口，四分类报告，复核新增功能0；可靠合同引用，只补必要原字节/源行，不重复整函数/源码/资源导出/机械账。无增量及时覆盖交付主窗口补位，不凑函数时长。共同静态/安全/隔离规则适用，不创建下级agent、不改主树共享/生产ROM配置模型，无SIM/构建/历史回放/设备/外网；必要验证独占提交报告commit/验证/未知/clean。

## 当前完整任务书 A46（准备立即补位，2026-10-24）

树D:/CodexHome/visualizations/2026/10/23/01a1691a-e178-7710-86c0-84c2ff2d3dfb/re0041-a46；分支codex/re-0041-a46；基线为本任务书提交。独占reverse/reports/ap01/image-cache-drop-a46-0041-20261024.md及reverse/analysis/image-cache-drop-a46-0041-20261024/。

A43/A44明确backend drop/drop_all分支未展开；A27/A34/A38已有默认表a0263afc十word和remove/计量/链/cleanup。只核这同一backend的真实drop/drop_all槽及其normal通用API接入、条目/索引/链移除、引用/失效门与cleanup/free责任。先复用原表，不重建表，不能将通用a019cfbe直接命名backend drop_cb。旧release/victim/key合同继承，不扩平衡树/所有cache/任意异常重复操作；合法all-key分支须按原正常API证据认定，不擅加NULL门。

先已有→行为→局限→精确缺口，四分类报告，复核新增功能0；可靠合同引用，只补必要原字节/源行，不重复整函数/源码/资源导出/机械账。无增量及时覆盖交付主窗口补位，不凑函数时长。共同静态/安全/隔离规则适用，不创建下级agent、不改主树共享/生产ROM配置模型，无SIM/构建/历史回放/设备/外网；必要验证独占提交报告commit/验证/未知/clean。

## 当前完整任务书 A47（准备立即补位，2026-10-24）

树D:/CodexHome/visualizations/2026/10/23/01a1691a-e178-7710-86c0-84c2ff2d3dfb/re0041-a47；分支codex/re-0041-a47；基线为本任务书提交。独占reverse/reports/ap01/photo-reader-mode-a47-0041-20261024.md及reverse/analysis/photo-reader-mode-a47-0041-20261024/。

A41/A42留下非零O+10 mode分支callee a01b2e3a内部未核，memory mode0已闭。本题只沿已知setter正常非零reader mode的真实实参到该callee及对应构造/持有字段，核mode语义与资源归还（文件型只是候选，不能先把a01b2e3a命名fclose）。先查旧photo/较晚round3及retained caller，正常路径源指针/句柄身份有证才写合同；无真实构造种子精确交付，不扩解码算法/文件系统/全部失败臂。ROM输入借用与mode0析构全继承，不能虚构实际照片调用该mode。

先已有→行为→局限→精确缺口，四分类报告，复核新增功能0；可靠合同引用，只补必要原字节/源行，不重复整函数/源码/资源导出/机械账。无增量及时覆盖交付主窗口补位，不凑函数时长。共同静态/安全/隔离规则适用，不创建下级agent、不改主树共享/生产ROM配置模型，无SIM/构建/历史回放/设备/外网；必要验证独占提交报告commit/验证/未知/clean。

## 当前完整任务书 H16（准备立即补位，2026-10-24）

树D:/CodexHome/visualizations/2026/10/23/01a1691a-e178-7710-86c0-84c2ff2d3dfb/re0041-h16；分支codex/re-0041-h16；基线为本任务书提交。独占reverse/reports/ap01/clock-source-review-h16-0041-20261024.md及reverse/analysis/clock-source-review-h16-0041-20261024/。

独立复核H15 a002645a正常8B调用者buffer、单次uint32 load62fc6c64、DIVU/REMU1000及乘1000000、return0；候选只支持秒/纳秒形状与刻度解释，counter writer/cadence/epoch与offset writer未证。H13/H14/E16已核两ID上层区别全继承，不重导上层或全ROM搜writer，不把候选源当ROM周期证明。新增功能0，必要稀疏原字节/源行锚点。

先已有→行为→局限→精确缺口，四分类报告，复核新增功能0；可靠合同引用，只补必要原字节/源行，不重复整函数/源码/资源导出/机械账。无增量及时覆盖交付主窗口补位，不凑函数时长。共同静态/安全/隔离规则适用，不创建下级agent、不改主树共享/生产ROM配置模型，无SIM/构建/历史回放/设备/外网；必要验证独占提交报告commit/验证/未知/clean。
