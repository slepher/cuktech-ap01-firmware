# 0041 静态功能恢复：滚动管理交接

2026-10-23。主窗口仅管理、验收和整合；实质性逆向及技术复核交给独立 worktree 的 subagent。

## 共同基线

既有报告和证据已在 fa8fe17；本次补归档三个此前未跟踪的历史 UART 辅助脚本（tooling/scripts 下 Ap01UartEndToEndReplay0041.java、Ap01UartResponseReplay0041.java、build-uart-response-evidence-0041.py）。仅保存既有成果，不运行，不新增历史缺陷调查。报告结论未因归档而获得重新验收；dock-presence-polling 的 review-index.json 尚缺，待 B01 复核。Git 提交是基线，不另建哈希或复制清单。

当前目标是全部非开源功能静态恢复；尚未完成，不计算整体百分比。禁止执行固件、连接设备/服务、缺陷验证、畸形输入、修改安全检查、ROM、生产代码或分析器模型。新增研究只写 reverse/analysis、reverse/reports/ap01。当前用户授权本地提交和整合，覆盖旧 task.md 的“不提交”历史限制；禁止推送。

## 首批任务

共同要求：独立分支/工作树；每次 shell 命令显式指定该 worktree 为工作目录，并在 PowerShell 显式 Set-Location（shell 启动可能改变目录）。不修改主工作区、其他 worktree 或共享 status/task/README/覆盖索引；不撤销他人修改；不创建下级 agent；不自行领取下一任务。已有忽略证据、ROM、工具可从主仓库绝对路径只读访问；不可复制整份工作区，不可共享可写数据库。临时产物只能使用任务专属路径。只读静态证据优先。

交付须回答问题，列函数地址/参数/返回值/调用关系，必要伪代码/结构体，指令地址与可定位证据，事实/推断/未知、来源状态和恢复程度、实际验证及一个小后续建议。涉及边界/厂商指令/扩展/间接调用须核原始指令，不仅依赖反编译。完成后检查差异、相称验证、提交独占文件，报告提交 ID、结论、验证、未知并结束。遇安全限制记录操作及返回原因，不绕过或反复重试。

| ID | 分支 | 独占输出 | 问题、范围与完成标准 |
| --- | --- | --- | --- |
| A01 | codex/re-0041-a01 | reverse/reports/ap01/buzzer-stop-review-a01-0041-20261023.md；reverse/analysis/buzzer-stop-a01-0041-20261023/ | 从 buzzer-backlight 三份报告及证据追已有 worker、停机入口、退出标志/事件的直接读写者。补正常停机链及退出确认生产者/消费者；限定 1–3 核心函数与少量直接依赖，无法闭合则给有界搜索及断边。排除历史缺陷研究、PWM 算术扩展。 |
| B01 | codex/re-0041-b01 | reverse/reports/ap01/dock-presence-polling-0041-20261023.md；reverse/analysis/dock-presence-polling-0041-20261023/ | 复核现有 dock 报告核心语义、表结构、指令依据及引用，修正不一致，补 review-index.json。不扩展完整 USB，不重复哈希清单。逐项给接受/修正/未验证及实际核对记录。 |
| C01 | codex/re-0041-c01 | reverse/reports/ap01/pogo-timer-lifecycle-c01-0041-20261023.md；reverse/analysis/pogo-timer-lifecycle-c01-0041-20261023/ | 只研究 a005a736 中注册 a00a805a 并存 context+0 的轮询 timer：创建、持有、停止/删除直接调用链。入口为 dock 报告及 timer-registration-source.json。限定创建/销毁的 1–3 核心函数；排除整个 PogoPin/ADC/USB 状态机；未定位销毁须明确有界未知，不补造行为。 |

任务工作树父目录：D:/CodexHome/visualizations/2026/10/23/01a1689f-d8c8-7821-aacd-286f467e884d；分别为 re0041-a01、re0041-b01、re0041-c01。从本管理记录所在基线提交创建。启动状态及提交验收在下文增补。

## 管理队列

- 共同基线：7c17501，基本差异检查通过。三个 worktree 均已从此提交创建。
- A01：b48b36a 已整合为a49e584；范围/差异检查通过，技术验收待 A02。worker退出post已交付，正常停机/唤醒/确认消费者仍未知。
- B01：已完成技术复核 accepted_with_correction；8eab0eb 已整合为37ae2b5。仅相位不匹配写 sent=limit，sent>=limit 分支不写；整体仍部分恢复。9窗口/573普通指令/8厂商word等静态核对通过；无新增开源排除。
- C01：e0241a4 已整合为21d224c；范围和差异检查通过，技术验收待 C02。创建/context+0/userdata 关系已交付，停止删除仍未知。
- Git 元数据初次写入遇 sandbox 的 index.lock Permission denied；按用户明确提交授权使用升级工具后成功，未改动权限或绕过限制。
- 后续：按交付未知拆分小任务，技术结论交 subagent 复核。完成一个先验收整合一个，再从最新整合提交启动新 agent。
- 覆盖边界仍见 private-coverage-0041.md；开源须可核实来源/版本，未知来源不排除。内嵌 MCU 仍不透明，高熵不证明架构、加密或压缩。

## B02 补位任务书

分支 codex/re-0041-b02；worktree D:/CodexHome/visualizations/2026/10/23/01a1689f-d8c8-7821-aacd-286f467e884d/re0041-b02。从包含本任务书的最新管理提交启动。遵守上述共同约束，不创建下级 agent。

问题：只确认轮询 controller phase byte `62fc4b35` 在 timer 之外的一个直接写入者及其直接调用合同。入口为 B01 已验收的 dock 报告、review-index.json 及其建议。范围为1–3核心函数/少量直接依赖，恢复精确phase赋值与触发条件；排除完整应答分派/USB状态机，不扩展异常输入或历史缺陷验证。独占输出 reverse/reports/ap01/poll-phase-writer-b02-0041-20261023.md 和 reverse/analysis/poll-phase-writer-b02-0041-20261023/。完成标准同首批，特别核原指令及 byte宽度，明确其他写入者未知，提交后结束。

B02：从5cc052a运行中，agent /root/b02_phase_writer；A01/C01完成后另排范围明确的新agent技术复核。

## C02 独立技术复核任务书

分支 codex/re-0041-c02；worktree D:/CodexHome/visualizations/2026/10/23/01a1689f-d8c8-7821-aacd-286f467e884d/re0041-c02。从包含本任务书的最新管理提交创建。只复核C01报告的创建/保存/userdata、deinit窗口和负搜索边界，不展开新生命周期；入口为C01报告、instruction-evidence.json和collect-static.py。独占输出 reverse/reports/ap01/pogo-timer-review-c02-0041-20261023.md 和 reverse/analysis/pogo-timer-review-c02-0041-20261023/。必要纠正以独立报告精确列出，避免改共享索引。核原ROM指令、参数和分支、负结果是否过度；区分接受/纠正/未核，实际静态核验后提交。遵守共同约束，不下派、不执行固件、不改模型、不外连。C02从ff270d3运行中，agent /root/c02_timer_review。

## A02 独立技术复核任务书

分支 codex/re-0041-a02；worktree D:/CodexHome/visualizations/2026/10/23/01a1689f-d8c8-7821-aacd-286f467e884d/re0041-a02。从包含本任务书的最新管理提交启动。只复核A01的worker退出post、初始化失败与正常停机区分、52个直接编码候选及7个wait调用点评语的检索边界；不继续寻找新正常停机链、不扩展历史缺陷研究。入口为 buzzer-stop-review-a01 报告、其analysis目录及旧三轮报告的对应证据。独占输出 reverse/reports/ap01/buzzer-stop-review-a02-0041-20261023.md 和 reverse/analysis/buzzer-stop-review-a02-0041-20261023/。核ROM指令、候选不能冒充真实边、别名/间接调用不能被负搜索排除；交付逐项接受/纠正/未核与实际验证，提交后结束。共同约束全部适用。A02待启动。
