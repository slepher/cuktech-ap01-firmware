# 0041 静态功能恢复：滚动管理交接

2026-10-23。主窗口仅管理、验收和整合；实质性逆向及技术复核交给独立 worktree 的 subagent。

## 共同规则

当前目标是全部非开源功能静态恢复；尚未完成，不计算整体百分比。禁止执行固件、连接设备/服务、缺陷验证、畸形输入、修改安全检查、ROM、生产代码或分析器模型。新增研究只写 reverse/analysis、reverse/reports/ap01。当前用户授权本地提交和整合，覆盖旧 task.md 的“不提交”历史限制；禁止推送。

共同要求：独立分支/工作树；每次 shell 命令显式指定该 worktree 为工作目录，并在 PowerShell 显式 Set-Location（shell 启动可能改变目录）。不修改主工作区、其他 worktree 或共享 status/task/README/覆盖索引；不撤销他人修改；不创建下级 agent；不自行领取下一任务。已有忽略证据、ROM、工具可从主仓库绝对路径只读访问；不可复制整份工作区，不可共享可写数据库。临时产物只能使用任务专属路径。只读静态证据优先。

交付须回答问题，列函数地址/参数/返回值/调用关系，必要伪代码/结构体，指令地址与可定位证据，事实/推断/未知、来源状态和恢复程度、实际验证及一个小后续建议。涉及边界/厂商指令/扩展/间接调用须核原始指令，不仅依赖反编译。完成后检查差异、相称验证、提交独占文件，报告提交 ID、结论、验证、未知并结束。遇安全限制记录操作及返回原因，不绕过或反复重试。

用户强调维持三个运行中的subagent是调度硬要求。预备后继任务；任务完成后先检查独占范围、证据完整性、实际验证和差异，本地整合，从最新管理提交建立新分支/worktree启动新agent，再更新汇总和回收旧树。最多三个同时运行，不长期复用同一agent承担不同任务。语义冲突和技术判断交新subagent，不盲选。未提交或未整合成果不得强删，保留有价值分支。

主仓库：D:/Documents/PlatformIO/Projects/cuktech-ap01-firmware。工作树父目录：D:/CodexHome/visualizations/2026/10/23/01a1689f-d8c8-7821-aacd-286f467e884d；各任务为re0041-<id>。只读忽略证据/ROM不随Git工作树自动出现，用主仓库绝对路径读取；禁止复制整份未提交工作区。

## 当前调度

| 任务 | agent | 固定基线 | 当前职责 | 下一项 |
| --- | --- | --- | --- | --- |
| A18 | /root/a18_current_review | 2400931 | 当前值首消费独立复核 | A19图标消费callee |
| B19 | /root/b19_parser_review | fad8df6 | 正常stage/escape独立复核 | B20排队命令消费 |
| C20 | /root/c20_third_gate_review | 9270abb | 第三门正常合同独立复核 | 选一个变换callee |

最新已整合：A17 f95d973→2400931（当前值正常字段合同，技术待A18）；B18 fff077c→fad8df6（正常stage/escape研究，技术待B19）；C19 ee172d4→9270abb（第三门局部成果，技术待C20）。旧工作树仅在确认干净并整合后回收，任务分支保留。

## 已整合概况与开放缺口

共同研究基线7c17501，后续均通过明确本地Git提交管理，不另建哈希/复制清单。限定验收与报告链接见[覆盖记录](private-coverage-0041.md)。蜂鸣正常停机/确认消费者、timer最终停止删除、完整UI/订阅销毁、MCU内部程序及准确来源版本等仍开放；不得将局部验收变为模块/全ROM完成。没有新增已认证开源排除，不计算全ROM百分比。

此前任务书与提交映射已迁移到[历史任务交接](rolling-task-history-0041-20261023.md)，保留原文；历史状态只代表当时，当前以上表为准。以下任务书保留原启动门槛，实际运行/待启动以上表为准。

## 预备任务 B19：正常接收状态独立复核

分支 codex/re-0041-b19；worktree D:/CodexHome/visualizations/2026/10/23/01a1689f-d8c8-7821-aacd-286f467e884d/re0041-b19。须B18提交整合后，从最新管理提交启动。只复核B18正常接收stage/escape生产消费及直接依赖，最多3核心函数，不做长度审计/异常回放/缺陷验证/OTA扩展。独占 reverse/reports/ap01/uart-normal-parser-review-b19-0041-20261023.md、reverse/analysis/uart-normal-parser-review-b19-0041-20261023/；必要精确纠正B18。原指令逐项接受/纠正/未核、来源/实际静态验证，差异检查后提交结束。共同规则适用。仅预备，未启动。

## 预备任务 C20：第三门独立复核

分支 codex/re-0041-c20；worktree D:/CodexHome/visualizations/2026/10/23/01a1689f-d8c8-7821-aacd-286f467e884d/re0041-c20。须C19提交整合后，从最新管理提交启动。仅复核C19第三门参数/局部读写/返回与直接消费条件，最多3核心函数，不扩失效队列/GUI全集。独占 reverse/reports/ap01/invalidation-third-gate-review-c20-0041-20261023.md、reverse/analysis/invalidation-third-gate-review-c20-0041-20261023/；必要精确纠正C19。逐项接受/纠正/未核/来源和实际静态验证，差异检查后提交结束。共同规则适用。仅预备，未启动。

## 预备任务 A18：当前值消费独立复核

分支 codex/re-0041-a18；worktree D:/CodexHome/visualizations/2026/10/23/01a1689f-d8c8-7821-aacd-286f467e884d/re0041-a18。须A17提交整合后，从最新管理提交启动。只复核A17正常参数/字段/返回合同及最多一个直接依赖，不扩天气UI/图标/生命周期。独占 reverse/reports/ap01/weather-current-review-a18-0041-20261023.md、reverse/analysis/weather-current-review-a18-0041-20261023/；必要精确纠正A17。逐项接受/纠正/未核、来源和实际静态验证，差异检查后提交结束。共同规则适用。仅预备，未启动。

## 预备任务 B20：正常排队命令消费

分支 codex/re-0041-b20；worktree D:/CodexHome/visualizations/2026/10/23/01a1689f-d8c8-7821-aacd-286f467e884d/re0041-b20。须B19验收完成整合后，从最新管理提交启动。只恢复a01915bc尝试消费排队命令的正常字段/选择顺序/调用返回合同及最多两个直接依赖；入口usb-interface-ota报告0x24事件简述、dock报告四待发槽与保留dossier。先核后续报告避免重复。只解释一次取队列动作与槽所有权，不扩完整OTA/超时失败/漏洞调查/长度审计，不运行历史回放。独占 reverse/reports/ap01/queued-command-consume-b20-0041-20261023.md、reverse/analysis/queued-command-consume-b20-0041-20261023/。核原指令/ABI/原有清理与返回，事实推断未知/来源和实际静态验证，差异检查后提交结束。共同规则适用。仅预备，未启动。

## 预备任务 A19：天气图标消费callee

分支 codex/re-0041-a19；worktree D:/CodexHome/visualizations/2026/10/23/01a1689f-d8c8-7821-aacd-286f467e884d/re0041-a19。须A18验收完成整合后，从最新管理提交启动。只恢复A15/A16明确未解的a0198946(load32(context+0x20),icon)正常参数/字段/返回合同及最多两个直接依赖，最多3核心函数。先核已有后续报告，A17已仅检索未见callee合同；不扩全部图标/天气UI/生命周期。独占 reverse/reports/ap01/weather-icon-consumer-a19-0041-20261023.md、reverse/analysis/weather-icon-consumer-a19-0041-20261023/。核原指令/指针与地址边界/来源/事实推断未知/实际静态验证，差异检查后提交结束。共同规则适用。仅预备，未启动。

## 预备任务 C21：变换前置callee

分支 codex/re-0041-c21；worktree D:/CodexHome/visualizations/2026/10/23/01a1689f-d8c8-7821-aacd-286f467e884d/re0041-c21。须C20验收完成整合后，从最新管理提交启动。只恢复a00dbff4正常参数/返回含义及是否写区域的局部合同，最多3核心函数/必要直接依赖；入口C19/C20中两个区域变换前的非零门，不同时接管a00dca48或完整变换库/GUI。独占 reverse/reports/ap01/transform-predicate-c21-0041-20261023.md、reverse/analysis/transform-predicate-c21-0041-20261023/。核原指令和调用者消费、事实推断未知/来源/实际静态验证，差异检查后提交结束。共同规则适用。仅预备，未启动。
