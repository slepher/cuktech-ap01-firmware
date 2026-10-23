# 0041 六路滚动管理（2026-10-23恢复）

用户最新授权恢复持续六路推进，取代历史收尾暂停与三路上限。原管理交接已归档至 rolling-task-history-0041-20261023.md。主窗口只管理，不作函数逆向或技术语义判断。环境共7席，主窗口1席，研究/复核6席。当前六个任务均已真实启动，见运行快照。

## 共同规则

只做0041静态功能恢复；禁止执行固件、连接设备/外部服务、漏洞/异常输入/缺陷验证、修改安全检查、ROM、生产代码、构建配置和分析器模型；不推送。只写独占reverse/analysis和reverse/reports/ap01文件。只用自己的独立worktree和分支，每次shell显式workdir并在PowerShell Set-Location。其他agent同时工作，不撤销他人修改、不改主树或共享索引，不创建下级agent、不自行接后继。忽略ROM/证据/工具从主仓库绝对路径只读访问；不复制工作区，不共享可写数据库或切换全局REA。优先留存证据；若工具不能隔离则报告管理者。临时状态/日志放各自独占analysis目录。只恢复正常原程序行为，不擅自修正。

交付列问题/范围/结论、业务行为、函数地址/参数/返回/调用、必要伪代码结构体状态转换、所有权生命周期、可定位证据与原指令、事实/推断/未知、来源与恢复程度、实际静态验证、断边和一个后续闭包。伪代码不是原源码；保留调用顺序、重读、宽度/符号、返回判断、失败/清理和间接ABI。边界/厂商指令须核原字节，不仅信反编译。标准库只有来源可核实才排除，适配/回调仍恢复；不新增哈希清单/复制清单/机械重复证据。不编译项目，不运行历史回放。完成标准为原问题闭包得到有证据答案或明确可定位断边，不能缩成短helper声称完成；预计约45–90分钟，提前实质完成立即提交结束。

接近提交提前报告结论、剩余验证、阻塞和后继建议。检查差异、必要验证、明确路径git add、提交、报告commit/验证/未知/干净状态后结束。主窗口作范围验收，技术验收由新独立agent。恢复成果可先整合为待复核；不得自验冒称验收。每项完成即整合补位，从启动时最新管理提交创建新树；运行任务不移动基线。语义冲突交agent；回收仅限干净且已整合worktree，分支保留。用户要求收尾即停止派发。

主仓库：D:/Documents/PlatformIO/Projects/cuktech-ap01-firmware。所有任务初始共同研究基线 ab9716e；实际启动基线为含本任务书的管理提交，在派发消息及运行表记录。

## 当前任务书

### A19：天气订阅 callback 到图标与控件更新的数据流

- 分支：codex/re-0041-a19
- worktree：D:/CodexHome/visualizations/2026/10/23/01a1691a-e178-7710-86c0-84c2ff2d3dfb/re0041-a19
- 业务问题/证据入口：weather-subscriber-a15、weather-subscriber-review-a16、weather-current-consumer-a17、weather-current-review-a18；入口 a00ab6b0/a00ab6ea、a0198946(load32(context+0x20),icon)
- 闭包、包含/排除、可保留合同和断边：核实图标值的生产、传递、资源选择与控件消费者如何衔接；以图标 callee 及必要更新/资源选择依赖组成约5–12核心函数闭包，针对已验收callback只核合同。保留已知arc范围/current合同。排除全部天气UI、网络请求、重复getter和全量源码搜索。无法闭合时列资源身份、更新副作用、销毁断边。
- 独占报告：reverse/reports/ap01/weather-icon-flow-a19-0041-20261023.md
- 独占分析目录：reverse/analysis/weather-icon-flow-a19-0041-20261023/
- 基线：启动时最新管理提交，见派发记录；其他完成标准及验证遵循共同规则。发现范围外独立业务先报告，不自行扩展。

### D01：正常命令从描述符提交到构帧、部分写及完成通知

- 分支：codex/re-0041-d01
- worktree：D:/CodexHome/visualizations/2026/10/23/01a1691a-e178-7710-86c0-84c2ff2d3dfb/re0041-d01
- 业务问题/证据入口：usb-interface-ota、queued-command-consume-b20、uart-normal-parser-b18/b19、dock-presence-polling；入口 a01951e2/a00ee9ce/a01a4ff8/a00ee96c/a00a8330，活动区62fcb2f0
- 闭包、包含/排除、可保留合同和断边：恢复提交→活动副本/入队→构帧→部分写→正常完成事件闭包，约5–12核心函数及必要直接依赖。B20槽消费、B18解析和CRC按既有合同核对，不重复完整解码；不修改或复核B20原文，疑义报告管理者。排除超时异常、长度审计、漏洞调查、OTA全模块、历史回放。断边须列底层write合同、回调ABI、状态写者和资源归还限制。
- 独占报告：reverse/reports/ap01/uart-send-lifecycle-d01-0041-20261023.md
- 独占分析目录：reverse/analysis/uart-send-lifecycle-d01-0041-20261023/
- 基线：启动时最新管理提交，见派发记录；其他完成标准及验证遵循共同规则。发现范围外独立业务先报告，不自行扩展。

### E01：UiIFace端口项嵌套资源生产消费与清理

- 分支：codex/re-0041-e01
- worktree：D:/CodexHome/visualizations/2026/10/23/01a1691a-e178-7710-86c0-84c2ff2d3dfb/re0041-e01
- 业务问题/证据入口：uiiface-lifecycle、ui-total-consumers、theme-total-state、mode-control；入口 a00a3d80、a00a8582 的cmd55初始化片段，总对象62fcb2cc，item步长0x1a8，指针+0x28/+0x2c/+0x30/+0x34/+0x38
- 闭包、包含/排除、可保留合同和断边：恢复一组端口项嵌套字段的分配/替换→业务消费→清零/释放闭包，约5–12核心函数及必要直接依赖，避免重新恢复全局快照getter和已验收订阅链。可在该字段族内调整函数集合，不接管独立页面。保留allocator/链表合同；排除全UI/全响应/全销毁扫描。无法证实连接到全局deinit时明确断边，不拼造释放链。
- 独占报告：reverse/reports/ap01/uiiface-item-ownership-e01-0041-20261023.md
- 独占分析目录：reverse/analysis/uiiface-item-ownership-e01-0041-20261023/
- 基线：启动时最新管理提交，见派发记录；其他完成标准及验证遵循共同规则。发现范围外独立业务先报告，不自行扩展。

### F01：MiIO共享延后设置timer的创建、提交、消费及控制生命周期

- 分支：codex/re-0041-f01
- worktree：D:/CodexHome/visualizations/2026/10/23/01a1691a-e178-7710-86c0-84c2ff2d3dfb/re0041-f01
- 业务问题/证据入口：miio-deferred-settings、buzzer-backlight-round3、weather-scheduling、numeric-location-review-b15；入口 a009d286/a00a0bd8/a00a0e78/a009d8bc/a00a5b90，timer/data字段见已有证据
- 闭包、包含/排除、可保留合同和断边：恢复私有timer初始化→三个已知属性提交→数据槽交接→callback清理→停止或销毁连接的小闭包，约5–12核心函数，已恢复kind0..6仅核接口及顺序，不逐分支重复。优先展开真实初始化/控制调用者，不重复kind2直接提交者扫描。保留libuv/allocator/天气重排合同，不重做通用timer库算法；来源不认证则仍列缺口。排除异常重复提交实验、全MiIO、外连。断边须说明外部串行化、data重读、资源与最终销毁。
- 独占报告：reverse/reports/ap01/miio-deferred-lifecycle-f01-0041-20261023.md
- 独占分析目录：reverse/analysis/miio-deferred-lifecycle-f01-0041-20261023/
- 基线：启动时最新管理提交，见派发记录；其他完成标准及验证遵循共同规则。发现范围外独立业务先报告，不自行扩展。

### B21：包含B20的命令生产、固定槽消费与发送启动闭包独立复核

- 分支：codex/re-0041-b21
- worktree：D:/CodexHome/visualizations/2026/10/23/01a1691a-e178-7710-86c0-84c2ff2d3dfb/re0041-b21
- 业务问题/证据入口：queued-command-consume-b20、usb-interface-ota、dock-presence-polling、uart-normal-parser-b18/b19；a01951e2/a01915bc/a00ee9ce和正常0x24通知调用者
- 闭包、包含/排除、可保留合同和断边：新的独立agent复核B20结论及生产者→槽→活动副本→发送启动→完成通知衔接，约5–12函数合同范围。已验收部分只针对必要合同核对；重点ABI、重读、宽度、清槽时点、返回覆盖、所有权和状态一致性。逐项接受/纠正/未核；必要纠正写独占报告，不改原报告。排除超时异常/漏洞/完整OTA/重复历史回放，发送内部留已知合同及未认证边界。
- 独占报告：reverse/reports/ap01/queued-command-review-b21-0041-20261023.md
- 独占分析目录：reverse/analysis/queued-command-review-b21-0041-20261023/
- 基线：启动时最新管理提交，见派发记录；其他完成标准及验证遵循共同规则。发现范围外独立业务先报告，不自行扩展。

### C22：包含C21的区域门控、祖先谓词与调用者闭包独立复核

- 分支：codex/re-0041-c22
- worktree：D:/CodexHome/visualizations/2026/10/23/01a1691a-e178-7710-86c0-84c2ff2d3dfb/re0041-c22
- 业务问题/证据入口：transform-predicate-c21、invalidation-third-gate-c19/review-c20、invalidation-gates-c17/review-c18、text-precondition-c15/review-c16；a00dbff4/a00ddab4/a00ddbf6/a00dddf4及a00dca48边界
- 闭包、包含/排除、可保留合同和断边：新的独立agent复核区域失效请求→前置门→对象/祖先判定→区域处理→caller消费闭包，约5–12函数合同范围，已验收部分针对性核合同。重点C21只读/掩码/返回、ABI、区域局部写与失败路径、调用顺序、原谓词和实际刷新界限。a00dca48内部可保留不透明合同，不接管完整变换库。逐项接受/纠正/未核，必要纠正独占报告；排除全GUI/最终物理刷新/异常验证。
- 独占报告：reverse/reports/ap01/region-gating-review-c22-0041-20261023.md
- 独占分析目录：reverse/analysis/region-gating-review-c22-0041-20261023/
- 基线：启动时最新管理提交，见派发记录；其他完成标准及验证遵循共同规则。发现范围外独立业务先报告，不自行扩展。

## 实际运行快照

已调用agent工具核实：主窗口1个与下列6个subagent均running。各任务真实启动基线均为 `2ee39b3`，当前未提交/未整合/未技术验收；启动时独立worktree创建成功。此为启动快照，完成状态由后续更新覆盖。

| 任务 | agent | 基线 | 状态 |
| --- | --- | --- | --- |
| A19 | /root/a19_weather_flow | 2ee39b3 | 运行中 |
| D01 | /root/d01_uart_send | 2ee39b3 | 运行中 |
| E01 | /root/e01_ui_ownership | 2ee39b3 | 运行中 |
| F01 | /root/f01_miio_timer | 2ee39b3 | 运行中 |
| B21 | /root/b21_queue_review | 2ee39b3 | 运行中 |
| C22 | /root/c22_region_review | 2ee39b3 | 运行中 |

## 近期滚动候选（未启动）

- A20：A19图标数据流完整闭包独立复核；依赖A19先整合，不重复A18已验收arc合同。核心集合和断边以A19实际交付为准。
- D02：D01提交/构帧/部分写/正常完成闭包独立复核；依赖D01整合，复用B21已验收槽合同，避免重复全解。
- E02：E01嵌套字段生产消费清理闭包独立复核；依赖E01整合，不把独立清理器自动并入全局deinit。
- F02：F01共享timer及私有data所有权闭包独立复核；依赖F01整合，库层通用算法保留明确合同。
- G01：区域门控到实际变换区域的生产/消费小闭包；先由C22明确a00dca48及其必要依赖是否仍未解，若已有覆盖则改选其证实的断边。不得自动扩大为全变换库或最终物理刷新。
- H01：另一个天气订阅者的注册→callback消费→注销/页面清理小闭包；先据A19实际发现选取未覆盖注册点a005e1fc/a005e8dc/a00b8bc2之一，不重复已恢复屏保分支。

以上只是预备问题，不冒称已派发。每次空位时依据最新整合和agent建议确定完整任务书、基线及独占输出，再启动新agent；独立技术复核须换新agent。

## 预备完整任务书 G01（未启动）

任务ID G01；业务问题：a00dca48(obj,area,1)如何读取对象属性、形成区域变换、写回区域并返回给失效裁剪调用者？需恢复它与必要直接依赖的完整小闭包，参考约5–12函数，不以一个helper结束，也不扩展整个变换库。入口为C19/C20、C21与C22两处caller合同；C22建议只核此边，未读取内部callee，核心依赖清单当前未知，须执行agent自行按原证据定位。拟分支codex/re-0041-g01；拟worktree D:/CodexHome/visualizations/2026/10/23/01a1691a-e178-7710-86c0-84c2ff2d3dfb/re0041-g01。基线为C22整合后启动时最新管理提交，启动记录补确切commit。独占reverse/reports/ap01/region-transform-flow-g01-0041-20261023.md与reverse/analysis/region-transform-flow-g01-0041-20261023/。

包含对象→参数提取→局部坐标/区域处理→写回与caller消费；针对C22已验收部分仅核接口，不重做全失效门控。完成标准为参数/返回、调用顺序、字段宽度/符号、区域每次读写、局部副本和所有权清楚，提供正常路径伪代码/布局/转换、原指令证据与必要静态核验。数学/标准库只有来源认证可作为排除，未认证不得静默跳过；底层算术可作明确合同边界但列证据与限制。未知厂商字不修改模型、不靠反编译补语义。排除全GUI、最终物理刷新、异常坐标/畸形输入/漏洞、执行固件或历史回放。闭合失败要列具体callee/坐标字段/浮点ABI/实际显示断边及一个后继闭包。共同规则全部适用。
