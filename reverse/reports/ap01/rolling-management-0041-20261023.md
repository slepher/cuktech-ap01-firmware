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
- A01：b48b36a 已整合为a49e584；范围/差异检查通过，A02限定技术验收通过（c4d7c4f）。worker退出post已交付，正常停机/唤醒/确认消费者仍未知。
- B01：已完成技术复核 accepted_with_correction；8eab0eb 已整合为37ae2b5。仅相位不匹配写 sent=limit，sent>=limit 分支不写；整体仍部分恢复。9窗口/573普通指令/8厂商word等静态核对通过；无新增开源排除。
- C01：e0241a4 已整合为21d224c；范围和差异检查通过，C02限定技术验收通过（301d05c），附字段命名澄清。创建/context+0/userdata 关系已交付，停止删除仍未知。
- Git 元数据初次写入遇 sandbox 的 index.lock Permission denied；按用户明确提交授权使用升级工具后成功，未改动权限或绕过限制。
- 后续：按交付未知拆分小任务，技术结论交 subagent 复核。完成一个先验收整合一个，再从最新整合提交启动新 agent。
- 覆盖边界仍见 private-coverage-0041.md；开源须可核实来源/版本，未知来源不排除。内嵌 MCU 仍不透明，高熵不证明架构、加密或压缩。

## B02 补位任务书

分支 codex/re-0041-b02；worktree D:/CodexHome/visualizations/2026/10/23/01a1689f-d8c8-7821-aacd-286f467e884d/re0041-b02。从包含本任务书的最新管理提交启动。遵守上述共同约束，不创建下级 agent。

问题：只确认轮询 controller phase byte `62fc4b35` 在 timer 之外的一个直接写入者及其直接调用合同。入口为 B01 已验收的 dock 报告、review-index.json 及其建议。范围为1–3核心函数/少量直接依赖，恢复精确phase赋值与触发条件；排除完整应答分派/USB状态机，不扩展异常输入或历史缺陷验证。独占输出 reverse/reports/ap01/poll-phase-writer-b02-0041-20261023.md 和 reverse/analysis/poll-phase-writer-b02-0041-20261023/。完成标准同首批，特别核原指令及 byte宽度，明确其他写入者未知，提交后结束。

B02：973240d已整合为bd21fff，范围/差异检查通过，B03限定技术验收通过（62aad5b）；cmd0x58在缓存helper返回且word@62fcb504非零时清phase byte，其他写者未知；A01/C01独立技术复核已完成，详见A02/C02。

## C02 独立技术复核任务书

分支 codex/re-0041-c02；worktree D:/CodexHome/visualizations/2026/10/23/01a1689f-d8c8-7821-aacd-286f467e884d/re0041-c02。从包含本任务书的最新管理提交创建。只复核C01报告的创建/保存/userdata、deinit窗口和负搜索边界，不展开新生命周期；入口为C01报告、instruction-evidence.json和collect-static.py。独占输出 reverse/reports/ap01/pogo-timer-review-c02-0041-20261023.md 和 reverse/analysis/pogo-timer-review-c02-0041-20261023/。必要纠正以独立报告精确列出，避免改共享索引。核原ROM指令、参数和分支、负结果是否过度；区分接受/纠正/未核，实际静态核验后提交。遵守共同约束，不下派、不执行固件、不改模型、不外连。C02已完成，812f612整合为301d05c；原指令限定接受C01创建/userdata/deinit局部事实，停止删除仍未知；observed_word_190命名澄清交C03落实。

## A02 独立技术复核任务书

分支 codex/re-0041-a02；worktree D:/CodexHome/visualizations/2026/10/23/01a1689f-d8c8-7821-aacd-286f467e884d/re0041-a02。从包含本任务书的最新管理提交启动。只复核A01的worker退出post、初始化失败与正常停机区分、52个直接编码候选及7个wait调用点评语的检索边界；不继续寻找新正常停机链、不扩展历史缺陷研究。入口为 buzzer-stop-review-a01 报告、其analysis目录及旧三轮报告的对应证据。独占输出 reverse/reports/ap01/buzzer-stop-review-a02-0041-20261023.md 和 reverse/analysis/buzzer-stop-review-a02-0041-20261023/。核ROM指令、候选不能冒充真实边、别名/间接调用不能被负搜索排除；交付逐项接受/纠正/未核与实际验证，提交后结束。共同约束全部适用。A02完成，55cfd1b整合为c4d7c4f；核心语义接受，无实质纠正，所有负搜索限制保留。

## C03 关闭 callback 小任务书

分支 codex/re-0041-c03；worktree D:/CodexHome/visualizations/2026/10/23/01a1689f-d8c8-7821-aacd-286f467e884d/re0041-c03。从本任务书最新管理提交启动。问题只限 a00a3bc6 的poll关闭callback：参数/容器回溯、关闭计数与context释放关系，最多此函数及2个直接依赖；不扩展整个PogoPin或timer删除扫描。入口C01/C02和保留initializer的四个注册点。独占输出 reverse/reports/ap01/pogo-close-callback-c03-0041-20261023.md、reverse/analysis/pogo-close-callback-c03-0041-20261023/；另外授权按C02原文将C01伪代码phase字段改名observed_word_190，标引用C02复核，不作其他范围扩展。其余共同行为/证据/验证/提交要求均适用。C03已完成ff84cba并整合a5d730a；范围/差异检查通过，C04限定验收通过，19edade已整合；无核心纠正。C02命名澄清已落实。

## B03 独立技术复核任务书

分支 codex/re-0041-b03；worktree D:/CodexHome/visualizations/2026/10/23/01a1689f-d8c8-7821-aacd-286f467e884d/re0041-b03。从本任务书管理提交启动。只复核B02 cmd0x58局部分支及直接helper、分派参数，入口为poll-phase-writer-b02报告和analysis目录。核helper后条件读取、byte宽度、是否清sent/round_done及间接调用目标边界；不展开phase=1或完整分派。独占 reverse/reports/ap01/poll-phase-review-b03-0041-20261023.md 和 reverse/analysis/poll-phase-review-b03-0041-20261023/。核原ROM指令、事实推断未知和逐项接受/纠正/未核，完成相称验证、差异检查及提交。共同边界全部适用。B03已完成b045349并整合62aad5b；核心合同接受，sent/round_done负结论仅局部直接写入，不推广全调用链。

## A03 非空 wait 入参小任务书

分支 codex/re-0041-a03；worktree D:/CodexHome/visualizations/2026/10/23/01a1689f-d8c8-7821-aacd-286f467e884d/re0041-a03。从本任务书管理提交启动。问题只限 a00b8bfc 的非空 a0 来源及一个直接调用者合同；入口 A01/A02 的7个wait点评语与候选窗口。最多该函数及两个直接调用者/依赖，确认是否有证据连接蜂鸣exited_sem，不以地址邻近推断；若无连接则交付此包装局部行为并保留未知。不继续全ROM重复扫描，不展开完整信号量系统或历史缺陷。独占 reverse/reports/ap01/wait-wrapper-a03-0041-20261023.md 和 reverse/analysis/wait-wrapper-a03-0041-20261023/。共同证据/验证/提交要求适用。A03完成1b9f238并整合46dde31；范围/差异检查通过，A04技术验收通过（09d81e9）。未建立蜂鸣exited_sem连接，有限等待与厂商算术未知保留。

## C04 独立技术复核任务书

分支 codex/re-0041-c04；worktree D:/CodexHome/visualizations/2026/10/23/01a1689f-d8c8-7821-aacd-286f467e884d/re0041-c04。从本任务书管理提交启动。仅复核C03 callback的ctx回溯、ctx+198减计数及signed条件、释放封装、四组userdata和UART别名窗口，及C02命名澄清是否准确；不扩展close dispatcher或timer扫描。独占 reverse/reports/ap01/pogo-close-review-c04-0041-20261023.md、reverse/analysis/pogo-close-review-c04-0041-20261023/。核原指令，区分局部未读timer和全链未知，逐项接受/纠正/未核，验证差异检查后提交结束。共同约束适用。C04完成19edade并整合；6窗口286B、43项原编码字段核对通过，停止删除及全局计数不变量仍未知。

## B04 phase=1 局部分支小任务书

分支 codex/re-0041-b04；worktree D:/CodexHome/visualizations/2026/10/23/01a1689f-d8c8-7821-aacd-286f467e884d/re0041-b04。从本任务书管理提交启动。仅恢复响应callback中写62fc4b35=1的一个局部分支，确定命令、精确前置条件、byte写入顺序及紧邻调用；入口B02/B03报告及原响应函数保留证据。最多1–3核心函数/少量直接依赖，不扩展整个大响应函数、USB状态机或其他phase写者。独占 reverse/reports/ap01/poll-phase-one-b04-0041-20261023.md、reverse/analysis/poll-phase-one-b04-0041-20261023/。另授权按B03原文澄清B02的sent/round_done否定结论仅限局部直接写入，不改变其核心合同。共同指令证据、验证及提交要求适用，完成后结束。B04完成cbab6d7整合为3bc3001，范围/差异通过，B05限定技术验收通过（59b27d4）。

## A04 独立技术复核任务书

分支 codex/re-0041-a04；worktree D:/CodexHome/visualizations/2026/10/23/01a1689f-d8c8-7821-aacd-286f467e884d/re0041-a04。从本任务书管理提交启动。只复核A03包装 a00b8bfc 与 a0126946 的一个直接调用局部（入参、a1=-1与1000分支、返回、别名和厂商算术未知），不追新成员写者或扩大RPC状态机。入口A03报告/证据及A02 wait合同。独占 reverse/reports/ap01/wait-wrapper-review-a04-0041-20261023.md、reverse/analysis/wait-wrapper-review-a04-0041-20261023/。核原指令，逐项接受/纠正/未核，验证差异检查后提交结束。共同约束适用。A04完成954b245并整合09d81e9；核心合同接受，无语义纠正。

## C05 poll关闭注册传参小任务书

分支 codex/re-0041-c05；worktree D:/CodexHome/visualizations/2026/10/23/01a1689f-d8c8-7821-aacd-286f467e884d/re0041-c05。从本任务书管理提交启动。只恢复a009fb96到一个直接callback调用/传参点的合同，核C03的a00a3bc6如何取得poll首word作为context；最多该函数及两个直接依赖，不扩展完整libuv/poll/timer或全局关闭状态机。入口C03/C04及initializer四组注册点。独占 reverse/reports/ap01/pogo-close-dispatch-c05-0041-20261023.md、reverse/analysis/pogo-close-dispatch-c05-0041-20261023/。核原指令，来源未知不得排除，事实推断未知及实际验证，差异检查后提交结束。共同约束适用。C05完成3cdf4db整合6802ed6；范围/差异通过，C06限定技术验收通过（c3797ab）。

## 预备任务 B05：phase=1独立复核

分支 codex/re-0041-b05；worktree D:/CodexHome/visualizations/2026/10/23/01a1689f-d8c8-7821-aacd-286f467e884d/re0041-b05。必须在B04提交完成整合后，从当时最新管理提交创建启动。仅复核B04的cmd55前置条件/phase=1、done和sent复位顺序、两条厂商指令及8-bit循环，核“分配成功”不能代替实际可达条件的边界，不展开完整初始化。入口B04报告和证据，独占 reverse/reports/ap01/poll-phase-one-review-b05-0041-20261023.md、reverse/analysis/poll-phase-one-review-b05-0041-20261023/。另独占允许按本次复核精确纠正B04报告（若需）。原指令逐项接受/纠正/未核、实际验证、差异检查、提交后结束。共同约束适用。B05完成74e6544整合59b27d4；核心合同接受，无纠正，前奏/副作用未知保留。

## 预备任务 A05：wait成员一个写入者

分支 codex/re-0041-a05；worktree D:/CodexHome/visualizations/2026/10/23/01a1689f-d8c8-7821-aacd-286f467e884d/re0041-a05。须A04验收允许后，从最新已整合管理提交创建。只追A03 QueuePartial.wait_member_18 的一个直接写入者，最多1–3核心函数，不做全ROM重复扫描或整个RPC状态机。入口A03/A04及既存inventory。若证据无法定位则保留有界未知，不猜与蜂鸣exited_sem的连接。独占 reverse/reports/ap01/wait-member-writer-a05-0041-20261023.md、reverse/analysis/wait-member-writer-a05-0041-20261023/。事实推断未知、原指令、来源、相称验证、差异检查与提交要求同前。A05完成85b4e0e整合f7243c9；范围/差异检查通过，A06限定验收通过（b2b262f）。

## 预备任务 C06：关闭分派独立复核

分支 codex/re-0041-c06；worktree D:/CodexHome/visualizations/2026/10/23/01a1689f-d8c8-7821-aacd-286f467e884d/re0041-c06。须C05提交完成整合后从最新管理提交创建。只复核C05登记/入队/consumer局部合同的三个核心函数及initializer已给出的摘链窗口，特别type8条件、链指针偏移、先存next及原poll传参。不得扩展完整event loop或timer。入口C05报告及证据，独占 reverse/reports/ap01/pogo-close-dispatch-review-c06-0041-20261023.md、reverse/analysis/pogo-close-dispatch-review-c06-0041-20261023/；必要可精确纠正C05报告。原指令逐项接受/纠正/未核及实际验证，差异检查后提交结束。共同约束适用。C06完成6fcb1f8整合c3797ab；限定接受C05，无需纠正，12窗口490B/70原编码字段/13直接目标核对通过。

## 预备任务 B06：基础信息注册前奏

分支 codex/re-0041-b06；worktree D:/CodexHome/visualizations/2026/10/23/01a1689f-d8c8-7821-aacd-286f467e884d/re0041-b06。B05完成验收整合后从最新管理提交启动。只恢复 a01b28ce(a00a3c8a,i) 的直接注册合同（参数、去重/新建、userdata、返回与一个直接依赖），最多3核心函数，不扩展全部通知消费者或基础信息构造。入口B04/B05及保留证据。独占 reverse/reports/ap01/basic-info-register-b06-0041-20261023.md、reverse/analysis/basic-info-register-b06-0041-20261023/。核原指令、事实推断未知、来源、验证、差异检查后提交结束。共同约束适用。B06完成59d2023整合2125a49；范围/差异通过，待B07技术验收。

## 预备任务 A06：wait成员初始化独立复核

分支 codex/re-0041-a06；worktree D:/CodexHome/visualizations/2026/10/23/01a1689f-d8c8-7821-aacd-286f467e884d/re0041-a06。须A05成果提交整合后从最新管理提交启动。只复核A05三个核心局部的对象创建、+18输出槽写入、consumer+8及线程参数前奏；线程wrapperABI未展开不得补造。入口A05报告和证据，独占 reverse/reports/ap01/wait-member-review-a06-0041-20261023.md、reverse/analysis/wait-member-review-a06-0041-20261023/；必要可精确纠正A05报告。核原指令与宽度/分支、事实推断未知、来源、实际验证，差异检查后提交结束。共同约束适用。A06完成9422994整合b2b262f；限定接受A05，无纠正，308B/105条/282项核验通过。

## 预备任务 C07：deinit后一个消费机会

分支 codex/re-0041-c07；worktree D:/CodexHome/visualizations/2026/10/23/01a1689f-d8c8-7821-aacd-286f467e884d/re0041-c07。须C06验收允许后从最新管理提交启动。只追既存initializer中PogoPin四组关闭登记后，是否有一条直接控制流回到C05已恢复pending消费局部，确定一个消费机会/退出边；最多该容器局部及两个直接依赖，不认证完整loop/全部close/timer生命周期。入口C05/C06与retained initializer。独占 reverse/reports/ap01/pogo-close-consume-c07-0041-20261023.md、reverse/analysis/pogo-close-consume-c07-0041-20261023/。若不闭合，给有界未知及断边，不补造调度。核原指令/边界/别名，来源、事实推断未知、相称验证、差异检查提交后结束。共同约束适用。C07完成eb7843e整合0af470d；范围/差异通过，待C08技术验收；局部未闭合登记后回消费边，不否定callee或调用者再消费。

## 预备任务 B07：注册合同独立复核

分支 codex/re-0041-b07；worktree D:/CodexHome/visualizations/2026/10/23/01a1689f-d8c8-7821-aacd-286f467e884d/re0041-b07。须B06成果提交整合后从最新管理提交启动。只复核B06的a01b28ce直接注册合同与最多两个直接依赖，参数、去重/新建、userdata、返回及来源边界，不扩展消费者全集。独占 reverse/reports/ap01/basic-info-register-review-b07-0041-20261023.md、reverse/analysis/basic-info-register-review-b07-0041-20261023/；必要可精确纠正B06报告。核原指令逐项接受/纠正/未核，实际验证与差异检查后提交结束。共同约束适用。B07从2125a49运行中，agent /root/b07_registration_review。

## 预备任务 A07：线程注册userdata透传

分支 codex/re-0041-a07；worktree D:/CodexHome/visualizations/2026/10/23/01a1689f-d8c8-7821-aacd-286f467e884d/re0041-a07。须A06验收允许后，从最新管理提交启动。只恢复a0197f02的入口及向已知线程创建API传userdata的直接合同，连接A05注册实参到A03 consumer；最多包装及两个直接依赖，不展开整个线程/调度器。入口A05/A06及既有函数inventory。独占 reverse/reports/ap01/thread-userdata-a07-0041-20261023.md、reverse/analysis/thread-userdata-a07-0041-20261023/。不得猜蜂鸣退出关联。核原指令、事实推断未知/来源/相称验证，差异检查后提交结束。共同约束适用。A07从b2b262f运行中，agent /root/a07_thread_userdata。

## 预备任务 C08：关闭后消费机会独立复核

分支 codex/re-0041-c08；worktree D:/CodexHome/visualizations/2026/10/23/01a1689f-d8c8-7821-aacd-286f467e884d/re0041-c08。须C07成果提交整合后，从最新管理提交启动。仅复核C07局部控制流和边界，原指令核关闭登记到pending消费者的一条机会/退出边、条件与断边，不扩展全loop/timer或做运行验证。独占 reverse/reports/ap01/pogo-close-consume-review-c08-0041-20261023.md、reverse/analysis/pogo-close-consume-review-c08-0041-20261023/；必要可精确纠正C07。逐项接受/纠正/未核及实际验证、差异检查后提交结束。共同约束适用。C08从0af470d运行中，agent /root/c08_consume_review。

## 预备任务 B08：注册callback首个使用点

分支 codex/re-0041-b08；worktree D:/CodexHome/visualizations/2026/10/23/01a1689f-d8c8-7821-aacd-286f467e884d/re0041-b08。须B07验收允许后从最新管理提交启动。仅恢复a00a3c8a入口及被注册userdata的首个直接使用点，最多此callback及两个直接依赖；不能先认定i处于哪个ABI参数，不扩消费者全集/基础信息状态机。入口B04 a00a8b50..8b5a注册参数、B06/B07及whole-rom inventory body Evidence。独占 reverse/reports/ap01/basic-info-callback-b08-0041-20261023.md、reverse/analysis/basic-info-callback-b08-0041-20261023/。核原指令与间接ABI证据，事实推断未知、来源、实际验证、差异检查后提交结束。共同约束适用。仅预备，未启动。

## 预备任务 A08：线程userdata独立复核

分支 codex/re-0041-a08；worktree D:/CodexHome/visualizations/2026/10/23/01a1689f-d8c8-7821-aacd-286f467e884d/re0041-a08。须A07成果提交整合后从最新管理提交启动。仅复核A07两层包装及直接入口/userdata透传合同，最多三个核心函数/已给局部，不扩线程调度或RPC。独占 reverse/reports/ap01/thread-userdata-review-a08-0041-20261023.md、reverse/analysis/thread-userdata-review-a08-0041-20261023/；必要可精确纠正A07。原指令逐项接受/纠正/未核，别名/运行时及底层缺口保留，实际验证、差异检查后提交结束。共同约束适用。仅预备，未启动。

## 预备任务 C09：详情页gate的一个写入者

分支 codex/re-0041-c09；worktree D:/CodexHome/visualizations/2026/10/23/01a1689f-d8c8-7821-aacd-286f467e884d/re0041-c09。须C08复核完成整合后，从最新管理提交启动。PogoPin尚未闭合缺口保留，不重复扩大负搜索。转既有UiIFace详情页消费者缺口：只恢复gate word62fc4034的一个直接写入者或清理点，解释其与a00f3952局部门控的已证关系。入口ui-total-consumers报告/analysis及既有inventory，最多1–3核心函数与少量直接依赖，不接管完整UI/页面销毁/订阅系统。不定位则有界未知。独占 reverse/reports/ap01/detail-gate-writer-c09-0041-20261023.md、reverse/analysis/detail-gate-writer-c09-0041-20261023/。核原指令、别名/回调边界、来源、事实推断未知/实际验证、差异检查后提交结束。共同约束适用。仅预备，未启动。
