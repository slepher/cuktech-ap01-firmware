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
| A16 | /root/a16_weather_review | f966a5e | 天气订阅三核心独立复核 | 按验收建议选小缺口 |
| B18 | /root/b18_normal_parser | 319dbdf | 正常接收阶段/转义标志 | B19独立复核 |
| C18 | /root/c18_gates_review | e29de84 | 失效入口两门复核 | C19第三门 |

最新已整合：A15 5f3f3db→f966a5e（技术待A16）；B17 bd7747d→319dbdf（限定接受B16并精确纠正检索描述，外部读者仍未知）；C17 3920202→e29de84（技术待C18）。旧工作树仅在确认干净并整合后回收，任务分支保留。

## 已整合概况与开放缺口

共同研究基线7c17501，后续均通过明确本地Git提交管理，不另建哈希/复制清单。限定验收与报告链接见[覆盖记录](private-coverage-0041.md)。蜂鸣正常停机/确认消费者、timer最终停止删除、完整UI/订阅销毁、MCU内部程序及准确来源版本等仍开放；不得将局部验收变为模块/全ROM完成。没有新增已认证开源排除，不计算全ROM百分比。

此前任务书与提交映射已迁移到[历史任务交接](rolling-task-history-0041-20261023.md)，保留原文；历史状态只代表当时，当前以上表为准。以下任务书保留原启动门槛，实际运行/待启动以上表为准。

## 预备任务 A16：天气订阅消费独立复核

分支 codex/re-0041-a16；worktree D:/CodexHome/visualizations/2026/10/23/01a1689f-d8c8-7821-aacd-286f467e884d/re0041-a16。须A15成果提交整合后，从最新管理提交启动。仅复核A15一个注册点及callback首个数据消费合同、间接ABI/借用复制边界，最多3核心函数，不扩全部天气UI。独占 reverse/reports/ap01/weather-subscriber-review-a16-0041-20261023.md、reverse/analysis/weather-subscriber-review-a16-0041-20261023/；必要精确纠正A15。原指令逐项接受/纠正/未核、来源/实际验证，差异检查后提交结束。共同约束适用。仅预备，未启动。

## 预备任务 C18：下游门控独立复核

分支 codex/re-0041-c18；worktree D:/CodexHome/visualizations/2026/10/23/01a1689f-d8c8-7821-aacd-286f467e884d/re0041-c18。须C17成果提交整合后，从最新管理提交启动。仅复核C17入口两个正常返回门/必要字段和参数，最多3核心函数及已给局部，不扩失效队列/GUI全集。独占 reverse/reports/ap01/invalidation-gates-review-c18-0041-20261023.md、reverse/analysis/invalidation-gates-review-c18-0041-20261023/；必要精确纠正C17。原指令逐项接受/纠正/未核、来源/实际验证，差异检查后提交结束。共同约束适用。仅预备，未启动。

## 预备任务 B18：正常接收阶段与转义标志

分支 codex/re-0041-b18；worktree D:/CodexHome/visualizations/2026/10/23/01a1689f-d8c8-7821-aacd-286f467e884d/re0041-b18。须B17验收完成整合后，从最新管理提交启动。转正常EsUnitProtocol私有协议：只恢复a00a8330内接收stage取值和escape标志的生产/消费及正常字节流阶段转换，最多该函数与两个直接依赖（可含a00ee934）。入口usb-interface-ota报告已有逐字节/CRC简述、保留dossier和whole-rom source_paths的EsUnitProtocol.c引用；先核后续报告是否已给完整状态表避免重复。已解CRC算法/分派ABI不重做，只引用合同；不扩完整OTA/队列、不做长度审计/漏洞研究/畸形输入或任何回放，不运行历史UART脚本。独占 reverse/reports/ap01/uart-normal-parser-b18-0041-20261023.md、reverse/analysis/uart-normal-parser-b18-0041-20261023/。交付正常状态转换表/可读伪代码、准确读写地址、事实推断未知、来源/原指令/实际静态验证，保留原返回/清理行为不擅自修复；差异检查后提交结束。共同约束适用。仅预备，未启动。

## 预备任务 C19：第三门局部合同

分支 codex/re-0041-c19；worktree D:/CodexHome/visualizations/2026/10/23/01a1689f-d8c8-7821-aacd-286f467e884d/re0041-c19。须C18验收允许后，从最新管理提交启动。只恢复a00ddab4(obj,&local)作为a00ddbf6第三门的参数/局部读写/返回及其直接消费条件，最多3核心函数；入口C17/C18及保留inventory。不要因前门已解扩成完整失效队列/全GUI，不推定最终显示刷新；先核是否已有报告解决。独占 reverse/reports/ap01/invalidation-third-gate-c19-0041-20261023.md、reverse/analysis/invalidation-third-gate-c19-0041-20261023/。核原指令/事实推断未知/来源/实际验证，差异检查后提交结束。共同约束适用。仅预备，未启动。

## 预备任务 B19：正常接收状态独立复核

分支 codex/re-0041-b19；worktree D:/CodexHome/visualizations/2026/10/23/01a1689f-d8c8-7821-aacd-286f467e884d/re0041-b19。须B18提交整合后，从最新管理提交启动。只复核B18正常接收stage/escape生产消费及直接依赖，最多3核心函数，不做长度审计/异常回放/缺陷验证/OTA扩展。独占 reverse/reports/ap01/uart-normal-parser-review-b19-0041-20261023.md、reverse/analysis/uart-normal-parser-review-b19-0041-20261023/；必要精确纠正B18。原指令逐项接受/纠正/未核、来源/实际静态验证，差异检查后提交结束。共同规则适用。仅预备，未启动。
