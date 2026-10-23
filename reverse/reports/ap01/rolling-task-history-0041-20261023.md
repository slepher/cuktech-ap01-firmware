# 0041 已整合任务书与历史交接

本文件保存按原编写顺序迁移的任务书、提交映射和历史运行状态；历史“当前/运行中/待启动”不代表现态。当前调度、共同规则与待办见[滚动管理交接](rolling-management-0041-20261023.md)。研究结论以各任务报告和独立复核为准，整体目标未完成。

## 共同基线

既有报告和证据已在 fa8fe17；本次补归档三个此前未跟踪的历史 UART 辅助脚本（tooling/scripts 下 Ap01UartEndToEndReplay0041.java、Ap01UartResponseReplay0041.java、build-uart-response-evidence-0041.py）。仅保存既有成果，不运行，不新增历史缺陷调查。报告结论未因归档而获得重新验收；dock-presence-polling 的 review-index.json 尚缺，待 B01 复核。Git 提交是基线，不另建哈希或复制清单。

## 首批任务

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

分支 codex/re-0041-b06；worktree D:/CodexHome/visualizations/2026/10/23/01a1689f-d8c8-7821-aacd-286f467e884d/re0041-b06。B05完成验收整合后从最新管理提交启动。只恢复 a01b28ce(a00a3c8a,i) 的直接注册合同（参数、去重/新建、userdata、返回与一个直接依赖），最多3核心函数，不扩展全部通知消费者或基础信息构造。入口B04/B05及保留证据。独占 reverse/reports/ap01/basic-info-register-b06-0041-20261023.md、reverse/analysis/basic-info-register-b06-0041-20261023/。核原指令、事实推断未知、来源、验证、差异检查后提交结束。共同约束适用。B06完成59d2023整合2125a49；范围/差异通过，B07限定验收通过（ffac598）。

## 预备任务 A06：wait成员初始化独立复核

分支 codex/re-0041-a06；worktree D:/CodexHome/visualizations/2026/10/23/01a1689f-d8c8-7821-aacd-286f467e884d/re0041-a06。须A05成果提交整合后从最新管理提交启动。只复核A05三个核心局部的对象创建、+18输出槽写入、consumer+8及线程参数前奏；线程wrapperABI未展开不得补造。入口A05报告和证据，独占 reverse/reports/ap01/wait-member-review-a06-0041-20261023.md、reverse/analysis/wait-member-review-a06-0041-20261023/；必要可精确纠正A05报告。核原指令与宽度/分支、事实推断未知、来源、实际验证，差异检查后提交结束。共同约束适用。A06完成9422994整合b2b262f；限定接受A05，无纠正，308B/105条/282项核验通过。

## 预备任务 C07：deinit后一个消费机会

分支 codex/re-0041-c07；worktree D:/CodexHome/visualizations/2026/10/23/01a1689f-d8c8-7821-aacd-286f467e884d/re0041-c07。须C06验收允许后从最新管理提交启动。只追既存initializer中PogoPin四组关闭登记后，是否有一条直接控制流回到C05已恢复pending消费局部，确定一个消费机会/退出边；最多该容器局部及两个直接依赖，不认证完整loop/全部close/timer生命周期。入口C05/C06与retained initializer。独占 reverse/reports/ap01/pogo-close-consume-c07-0041-20261023.md、reverse/analysis/pogo-close-consume-c07-0041-20261023/。若不闭合，给有界未知及断边，不补造调度。核原指令/边界/别名，来源、事实推断未知、相称验证、差异检查提交后结束。共同约束适用。C07完成eb7843e整合0af470d；范围/差异通过，C08限定验收通过（efefd4a）；局部未闭合登记后回消费边，不否定callee或调用者再消费。

## 预备任务 B07：注册合同独立复核

分支 codex/re-0041-b07；worktree D:/CodexHome/visualizations/2026/10/23/01a1689f-d8c8-7821-aacd-286f467e884d/re0041-b07。须B06成果提交整合后从最新管理提交启动。只复核B06的a01b28ce直接注册合同与最多两个直接依赖，参数、去重/新建、userdata、返回及来源边界，不扩展消费者全集。独占 reverse/reports/ap01/basic-info-register-review-b07-0041-20261023.md、reverse/analysis/basic-info-register-review-b07-0041-20261023/；必要可精确纠正B06报告。核原指令逐项接受/纠正/未核，实际验证与差异检查后提交结束。共同约束适用。B07完成0e049d3整合ffac598；核心注册合同接受，无纠正，4窗口218B/89指令/30项编码核验通过。

## 预备任务 A07：线程注册userdata透传

分支 codex/re-0041-a07；worktree D:/CodexHome/visualizations/2026/10/23/01a1689f-d8c8-7821-aacd-286f467e884d/re0041-a07。须A06验收允许后，从最新管理提交启动。只恢复a0197f02的入口及向已知线程创建API传userdata的直接合同，连接A05注册实参到A03 consumer；最多包装及两个直接依赖，不展开整个线程/调度器。入口A05/A06及既有函数inventory。独占 reverse/reports/ap01/thread-userdata-a07-0041-20261023.md、reverse/analysis/thread-userdata-a07-0041-20261023/。不得猜蜂鸣退出关联。核原指令、事实推断未知/来源/相称验证，差异检查后提交结束。共同约束适用。A07从b2b262f运行中，agent /root/a07_thread_userdata。

## 预备任务 C08：关闭后消费机会独立复核

分支 codex/re-0041-c08；worktree D:/CodexHome/visualizations/2026/10/23/01a1689f-d8c8-7821-aacd-286f467e884d/re0041-c08。须C07成果提交整合后，从最新管理提交启动。仅复核C07局部控制流和边界，原指令核关闭登记到pending消费者的一条机会/退出边、条件与断边，不扩展全loop/timer或做运行验证。独占 reverse/reports/ap01/pogo-close-consume-review-c08-0041-20261023.md、reverse/analysis/pogo-close-consume-review-c08-0041-20261023/；必要可精确纠正C07。逐项接受/纠正/未核及实际验证、差异检查后提交结束。共同约束适用。C08从0af470d运行中，agent /root/c08_consume_review。

## 预备任务 B08：注册callback首个使用点

分支 codex/re-0041-b08；worktree D:/CodexHome/visualizations/2026/10/23/01a1689f-d8c8-7821-aacd-286f467e884d/re0041-b08。须B07验收允许后从最新管理提交启动。仅恢复a00a3c8a入口及被注册userdata的首个直接使用点，最多此callback及两个直接依赖；不能先认定i处于哪个ABI参数，不扩消费者全集/基础信息状态机。入口B04 a00a8b50..8b5a注册参数、B06/B07及whole-rom inventory body Evidence。独占 reverse/reports/ap01/basic-info-callback-b08-0041-20261023.md、reverse/analysis/basic-info-callback-b08-0041-20261023/。核原指令与间接ABI证据，事实推断未知、来源、实际验证、差异检查后提交结束。共同约束适用。B08从ffac598运行中，agent /root/b08_callback_use。

## 预备任务 A08：线程userdata独立复核

分支 codex/re-0041-a08；worktree D:/CodexHome/visualizations/2026/10/23/01a1689f-d8c8-7821-aacd-286f467e884d/re0041-a08。须A07成果提交整合后从最新管理提交启动。仅复核A07两层包装及直接入口/userdata透传合同，最多三个核心函数/已给局部，不扩线程调度或RPC。独占 reverse/reports/ap01/thread-userdata-review-a08-0041-20261023.md、reverse/analysis/thread-userdata-review-a08-0041-20261023/；必要可精确纠正A07。原指令逐项接受/纠正/未核，别名/运行时及底层缺口保留，实际验证、差异检查后提交结束。共同约束适用。A08从ea2d450运行中，agent /root/a08_userdata_review；A07完成1a6ddc2整合ea2d450，待复核。

## 预备任务 C09：详情页gate的一个写入者

分支 codex/re-0041-c09；worktree D:/CodexHome/visualizations/2026/10/23/01a1689f-d8c8-7821-aacd-286f467e884d/re0041-c09。须C08复核完成整合后，从最新管理提交启动。PogoPin尚未闭合缺口保留，不重复扩大负搜索。转既有UiIFace详情页消费者缺口：只恢复gate word62fc4034的一个直接写入者或清理点，解释其与a00f3952局部门控的已证关系。入口ui-total-consumers报告/analysis及既有inventory，最多1–3核心函数与少量直接依赖，不接管完整UI/页面销毁/订阅系统。不定位则有界未知。独占 reverse/reports/ap01/detail-gate-writer-c09-0041-20261023.md、reverse/analysis/detail-gate-writer-c09-0041-20261023/。核原指令、别名/回调边界、来源、事实推断未知/实际验证、差异检查后提交结束。共同约束适用。仅预备，未启动。

## C09 实际任务调整（优先于上方预备任务）

C09从efefd4a启动，agent /root/c09_detail_gate。启动核对发现62fc4034 gate setter/清理已由theme-total-state/theme-online恢复；依用户“若已解决选等量级未完成项”改为只恢复详情页摘要helper a00f3844及最多两个直接依赖，回答ctx字段、模式getter及实际控件更新。入口ui-total-consumers报告明确未展开helper，排除a00f388c、完整UI及页面生命周期。独占输出改为 reverse/reports/ap01/detail-summary-c09-0041-20261023.md、reverse/analysis/detail-summary-c09-0041-20261023/。不新增重复gate验收成果，只在新报告注明调整和旧报告链接。工作树/分支/基线不变，共同约束及交付标准全部适用。

## 预备任务 B09：callback ABI独立复核

分支 codex/re-0041-b09；worktree D:/CodexHome/visualizations/2026/10/23/01a1689f-d8c8-7821-aacd-286f467e884d/re0041-b09。须B08成果提交整合后，从最新管理提交启动。仅复核B08 a00a389c→a00a3c8a间接ABI、注册userdata首个使用点及日志参数，最多三个核心函数/既有局部，不扩基础信息状态机。独占 reverse/reports/ap01/basic-info-callback-review-b09-0041-20261023.md、reverse/analysis/basic-info-callback-review-b09-0041-20261023/；必要可精确纠正B08。原指令逐项接受/纠正/未核、来源/实际验证、差异检查后提交结束。共同约束适用。仅预备，未启动。

## 预备任务 A09：线程适配入口一个消费点

分支 codex/re-0041-a09；worktree D:/CodexHome/visualizations/2026/10/23/01a1689f-d8c8-7821-aacd-286f467e884d/re0041-a09。须A08验收允许后，从最新管理提交启动。只恢复a012f946适配入口如何直接读取对象+130/+134并进入原entry、构造其a0，最多3核心函数/直接依赖；不扩调度器、启动可达性或蜂鸣关联。入口A07/A08及保留inventory。独占 reverse/reports/ap01/thread-adapter-a09-0041-20261023.md、reverse/analysis/thread-adapter-a09-0041-20261023/。核原指令与ABI、事实推断未知、来源/实际验证，差异检查后提交结束。共同约束适用。仅预备，未启动。

## 预备任务 C10：详情摘要独立复核

分支 codex/re-0041-c10；worktree D:/CodexHome/visualizations/2026/10/23/01a1689f-d8c8-7821-aacd-286f467e884d/re0041-c10。须C09实际调整后的detail-summary成果提交整合后，从最新管理提交启动。仅复核a00f3844及C09最多两个直接依赖的ctx/模式/控件合同，不回到已解gate或扩完整UI。独占 reverse/reports/ap01/detail-summary-review-c10-0041-20261023.md、reverse/analysis/detail-summary-review-c10-0041-20261023/；必要可精确纠正C09。核原指令、逐项接受/纠正/未核/来源及实际验证、差异检查后提交结束。共同约束适用。仅预备，未启动。

## 当前交接快照：A09 / B09 / C09

用户再次强调维持3个运行中的subagent是核心调度要求。完成后先范围/差异验收、本地整合、从最新整合提交建新worktree并启动新agent，再更新汇总和清理旧树；预备后继任务缩短空档。不得长期复用同一agent接不同任务。

| 当前任务 | agent | 分支 | 固定基线 | 下一项 |
| --- | --- | --- | --- | --- |
| A09 线程适配入口 | /root/a09_thread_adapter | codex/re-0041-a09 | d85348e | A10独立复核 |
| B09 callback ABI复核 | /root/b09_callback_review | codex/re-0041-b09 | 99899e3 | 根据复核建议选新小缺口 |
| C09 详情摘要helper（已替换已解gate任务） | /root/c09_detail_gate | codex/re-0041-c09 | efefd4a | C10独立复核 |

各工作树仍为同父目录re0041-<id>。最新已整合：B08 32aa8ef→99899e3（待B09）；A08 30dc717→d85348e（限定接受A07）。C08 1f2ee8b→efefd4a（限定接受C07），不等于全生命周期完成。上一代A08/B08已干净且整合，可回收，保留任务分支。

## 预备任务 A10：线程适配入口独立复核

分支 codex/re-0041-a10；worktree D:/CodexHome/visualizations/2026/10/23/01a1689f-d8c8-7821-aacd-286f467e884d/re0041-a10。须A09成果提交整合后，从最新管理提交启动。仅复核A09 a012f946及最多两个直接依赖的entry/userdata读取、调用参数与返回边界，原指令未知不能以伪代码填补，不扩调度/运行时可达性。独占 reverse/reports/ap01/thread-adapter-review-a10-0041-20261023.md、reverse/analysis/thread-adapter-review-a10-0041-20261023/；必要可精确纠正A09。逐项接受/纠正/未核、来源、实际验证、差异检查后提交结束。共同约束适用。仅预备，未启动。

## 预备任务 B10：一个基础信息分派调用者

分支 codex/re-0041-b10；worktree D:/CodexHome/visualizations/2026/10/23/01a1689f-d8c8-7821-aacd-286f467e884d/re0041-b10。须B09验收允许后，从最新管理提交启动。只恢复a00a389c的一个直接调用者，确认index实参来源和局部触发条件；最多调用者及两个直接依赖，不扩全部生产者/基础信息状态机。入口B08/B09及既有inventory，先选有明确ROM证据的小调用点。独占 reverse/reports/ap01/basic-info-dispatch-caller-b10-0041-20261023.md、reverse/analysis/basic-info-dispatch-caller-b10-0041-20261023/。核原指令、参数宽度与间接ABI边界、事实推断未知、来源/实际验证，差异检查后提交结束。共同约束适用。仅预备，未启动。

## C09/C10交接更新

C09实际detail-summary任务完成7c30064→b885567，范围/差异检查通过，技术待C10。只交detail-summary独占文件，gate旧缺口未重复交付。C10已从b885567启动，agent /root/c10_summary_review；C09工作树干净且成果整合，可回收并保留分支。C09据指令报告global mode重读，不能推断与callback snapshot一致。

## 预备任务 C11：详情模式控件更新

分支 codex/re-0041-c11；worktree D:/CodexHome/visualizations/2026/10/23/01a1689f-d8c8-7821-aacd-286f467e884d/re0041-c11。须C10验收允许后，从最新管理提交启动。只恢复 a00f388c(ctx,0,mode) 的局部控件更新合同及最多两个直接依赖；入口ui-total-consumers报告中详情页bit2消费者、C09/C10与已有inventory。若已有后续报告解决则先报告证据，再选同量级未完成helper，不重复交付。排除完整页面构造/销毁/所有订阅。独占 reverse/reports/ap01/detail-mode-update-c11-0041-20261023.md、reverse/analysis/detail-mode-update-c11-0041-20261023/。原指令参数/字段/分支及事实推断未知、来源/相称验证，差异检查后提交结束。共同约束适用。仅预备，未启动。

## B09/B10交接更新

B09完成b4e50b3→446cfec，限定接受B08，无核心纠正；190B/68普通指令/2厂商word/33项独立核验通过。B10已从446cfec启动，agent /root/b10_dispatch_caller；B09工作树干净且整合，可回收保留分支。当前三任务A09/B10/C10，后继A10/C11已预备。

## 预备任务 B11：分派调用者独立复核

分支 codex/re-0041-b11；worktree D:/CodexHome/visualizations/2026/10/23/01a1689f-d8c8-7821-aacd-286f467e884d/re0041-b11。须B10成果提交整合后，从最新管理提交启动。只复核B10一个直接调用者的index来源、触发条件及局部调用链，不扩全部生产者/状态机。独占 reverse/reports/ap01/basic-info-dispatch-review-b11-0041-20261023.md、reverse/analysis/basic-info-dispatch-review-b11-0041-20261023/；必要可精确纠正B10。原指令逐项接受/纠正/未核/来源及实际验证、差异检查后提交结束。共同约束适用。仅预备，未启动。

## 当前交接更新：A10 / B10 / C11

A09 a5671ad→4359c0b已整合，技术待A10；A10从4359c0b运行，agent /root/a10_adapter_review。C10 872ac72→57abfb4已整合，限定接受C09，无纠正；C11从57abfb4运行，agent /root/c11_mode_update，按已预备模式控件helper任务，不扩formatter。B10仍基线446cfec，agent /root/b10_dispatch_caller。后继A11（A10建议待定）、B11已预备、C12应为C11独立复核。A09/C10工作树干净且整合，可回收保留分支。

## 预备任务 C12：详情模式更新独立复核

分支 codex/re-0041-c12；worktree D:/CodexHome/visualizations/2026/10/23/01a1689f-d8c8-7821-aacd-286f467e884d/re0041-c12。须C11成果提交整合后，从最新管理提交启动。只复核C11 a00f388c及最多两个直接依赖的控件字段/参数/模式更新合同，不扩完整UI生命周期。独占 reverse/reports/ap01/detail-mode-update-review-c12-0041-20261023.md、reverse/analysis/detail-mode-update-review-c12-0041-20261023/；必要可精确纠正C11。原指令逐项接受/纠正/未核、来源/实际验证、差异检查后提交结束。共同约束适用。仅预备，未启动。

## 当前交接更新：A10 / B11 / C11

B10 d870680→aabf574已整合，技术待B11；B11从aabf574运行，agent /root/b11_caller_review。A10接近提交，限定验收支持A09，保留跨厂商word/当前对象/运行时未知；C11接近提交，C12已预备。B10工作树干净且整合可回收保留分支。

## 预备任务 A11：当前对象指针一个写入者

分支 codex/re-0041-a11；worktree D:/CodexHome/visualizations/2026/10/23/01a1689f-d8c8-7821-aacd-286f467e884d/re0041-a11。须A10验收完成整合后，从最新管理提交启动。只从已有inventory/留存引用恢复62fc6c18一个直接写者的局部合同（入参来源、写条件、word宽度），最多3核心函数；单写者不证明当前对象同一性/运行时调度。不全ROM重复扫描，不扩调度；无明确证据给有界未知。独占 reverse/reports/ap01/current-object-writer-a11-0041-20261023.md、reverse/analysis/current-object-writer-a11-0041-20261023/。原指令/事实推断未知/来源/实际验证，差异检查后提交结束。共同约束适用。仅预备，未启动。

## A10/A11交接更新

A10 3b6e270→f712c40已整合，限定接受A09，无纠正；672B/223槽/60项核验通过。A11从f712c40运行，agent /root/a11_current_writer。A10工作树干净且整合可回收保留分支。当前A11/B11/C11均运行，C12已预备。

## 预备任务 B12：opaque返回合同

分支 codex/re-0041-b12；worktree D:/CodexHome/visualizations/2026/10/23/01a1689f-d8c8-7821-aacd-286f467e884d/re0041-b12。须B11验收允许后，从最新管理提交启动。只恢复B10局部调用的a00501be正常参数/返回合同及最多两个直接依赖，回答机器返回零/非零的静态语义和来源识别依据，不扩完整响应、不异常输入/缺陷验证，也不假设跨调用对象稳定性。入口B10/B11及既有证据，不重复旧异常回放；若既有报告已完整恢复应先指出证据，再转同量级未完成依赖。独占 reverse/reports/ap01/compare-contract-b12-0041-20261023.md、reverse/analysis/compare-contract-b12-0041-20261023/。核原指令、事实推断未知/来源/实际验证，差异检查后提交结束。共同约束适用。仅预备，未启动。

## 预备任务 A12：当前对象写入者独立复核

分支 codex/re-0041-a12；worktree D:/CodexHome/visualizations/2026/10/23/01a1689f-d8c8-7821-aacd-286f467e884d/re0041-a12。须A11成果提交整合后，从最新管理提交启动。仅复核A11一个写入者的局部原指令/word宽度/参数来源/写条件，不由单写者推出当前对象或运行时调度。独占 reverse/reports/ap01/current-object-writer-review-a12-0041-20261023.md、reverse/analysis/current-object-writer-review-a12-0041-20261023/；必要可精确纠正A11。逐项接受/纠正/未核/来源及实际验证、差异检查后提交结束。共同约束适用。仅预备，未启动。

## C11/C12交接更新

C11 0e5c123→cb16c11已整合，范围/差异通过，技术待C12；C12从cb16c11运行，agent /root/c12_mode_review。C11工作树干净且整合可回收保留分支。当前A11/B11/C12三任务；A12/B12预备，C13按C12建议选新小缺口。

## B11/B12交接更新

B11 07d454b→5cabca7已整合，限定接受B10，无纠正；490B/157普通指令/1厂商word/64项原编码检查通过。B12从5cabca7运行，agent /root/b12_compare_contract。B11工作树干净且整合可回收保留分支。A11仍固定f712c40，C12固定cb16c11。

## 预备任务 B13：比较合同独立复核

分支 codex/re-0041-b13；worktree D:/CodexHome/visualizations/2026/10/23/01a1689f-d8c8-7821-aacd-286f467e884d/re0041-b13。须B12成果提交整合后，从最新管理提交启动。只复核B12最终实际范围的正常参数/返回合同及最多两个直接依赖、来源识别与未认证边界，不扩响应或异常验证。独占 reverse/reports/ap01/compare-contract-review-b13-0041-20261023.md、reverse/analysis/compare-contract-review-b13-0041-20261023/；必要精确纠正B12。原指令逐项接受/纠正/未核/来源及实际验证，差异检查后提交结束。共同约束适用。仅预备，未启动。

## 预备任务 C13：文本格式化更新入口

分支 codex/re-0041-c13；worktree D:/CodexHome/visualizations/2026/10/23/01a1689f-d8c8-7821-aacd-286f467e884d/re0041-c13。须C12验收允许后，从最新管理提交启动。只恢复a0091ee4文本更新入口及一个直接依赖的格式化/文本存储合同，最多3核心函数，不扩完整GUI/printf库。入口C09/C10与C11/C12相关既有证据，先查已解成果避免重复。若识别为开源须记录本地可核实来源/版本或识别依据，未知修改不排除；不能只凭库形状排除。独占 reverse/reports/ap01/text-update-entry-c13-0041-20261023.md、reverse/analysis/text-update-entry-c13-0041-20261023/。核原指令/ABI/所有权的局部事实，事实推断未知、来源/实际验证，差异检查后提交结束。共同约束适用。仅预备，未启动。

## C12/C13交接更新

C12 0bae399→8b82f93已整合，限定接受C11，无纠正；660B/234普通指令/1厂商word/30目标/28字段核验通过。C13从8b82f93运行，agent /root/c13_text_entry；现有报告已核实a0091ee4内部未展开。C12工作树干净且整合可回收保留分支。

## 预备任务 C14：文本更新入口独立复核

分支 codex/re-0041-c14；worktree D:/CodexHome/visualizations/2026/10/23/01a1689f-d8c8-7821-aacd-286f467e884d/re0041-c14。须C13成果提交整合后，从最新管理提交启动。只复核C13最终实际范围内文本更新入口及一个直接依赖（最多3函数），参数/变参/文本存储所有权及来源边界，不扩GUI/printf。独占 reverse/reports/ap01/text-update-entry-review-c14-0041-20261023.md、reverse/analysis/text-update-entry-review-c14-0041-20261023/；必要精确纠正C13。原指令逐项接受/纠正/未核、来源/实际验证、差异检查后提交结束。共同约束适用。仅预备，未启动。

## A11/A12与B12/B13交接更新

A11 4d4d5ed→139d994已整合，范围/差异通过，待A12；A12从139d994运行，agent /root/a12_writer_review。B12 31aae09→123d476已整合，范围/差异通过，待B13；B13从123d476运行，agent /root/b13_compare_review。两旧工作树均干净且整合，可回收保留分支。当前A12/B13/C13三个agent运行，C14已预备；后继不得重复a00a53c0（B10/B11已解）。

## 预备任务 B14：数字位置setter

分支 codex/re-0041-b14；worktree D:/CodexHome/visualizations/2026/10/23/01a1689f-d8c8-7821-aacd-286f467e884d/re0041-b14。须B13验收允许后，从最新管理提交启动。仅恢复a009c5fc数字位置setter正常参数/字段/返回合同及最多两个直接依赖；入口miio-deferred-settings中3/8与kind5调用、天气位置报告及既存inventory，先查已有后续成果避免重复。不要重新扫描kind2全部直接提交者（旧扫描已覆盖3个标准直接点），不扩完整MiIO/天气状态机。独占 reverse/reports/ap01/numeric-location-setter-b14-0041-20261023.md、reverse/analysis/numeric-location-setter-b14-0041-20261023/。核原指令参数宽度/返回分支/持久化边界，事实推断未知/来源/实际验证，差异检查后提交结束。共同约束适用。仅预备，未启动。

## 预备任务 A13：两个函数本地来源识别

分支 codex/re-0041-a13；worktree D:/CodexHome/visualizations/2026/10/23/01a1689f-d8c8-7821-aacd-286f467e884d/re0041-a13。须A12验收允许后，从最新管理提交启动。仅核a0027340/a00272d4两个NuttX形状函数的本地源码候选、可验证版本/识别依据、语义差异及厂商修改边界；入口A11/A12的源路径/结构与本地既有SDK/参考源码，不访问外部服务或下载。没有可靠候选则明确保留来源未知，不凭sched路径或算法同形排除，不扩大调度器或运行时对象同一性。独占 reverse/reports/ap01/scheduler-source-a13-0041-20261023.md、reverse/analysis/scheduler-source-a13-0041-20261023/。已有ROM指令事实与参考源码匹配/差异要分别标识，无法证明未修改实现不得排除；引用准确本地路径和版本依据，不新建哈希清单。实际验证、差异检查后提交结束。共同约束适用。仅预备，未启动。

## C13/C14交接更新

C13 aee8940→a10893d已整合，范围/差异通过，技术待C14；C14从a10893d运行，agent /root/c14_text_review。C13工作树干净且整合可回收保留分支。当前A12/B13/C14三个agent运行，A13/B14预备。C13源码归属仅LVGL候选，精确版本/厂商改动未认证，无新增开源排除。

## A12/A13与B13/B14交接更新

A12 79e7dc3→2b0c716已整合，限定接受A11，无纠正；248B/91指令/66项原编码核验通过。A13从2b0c716运行，agent /root/a13_nuttx_source。B13 afdf195→3c2bdeb已整合，限定接受B12，无纠正；68B/25条完整原编码核验通过。B14从3c2bdeb运行，agent /root/b14_numeric_location。两旧工作树均干净且整合可回收保留分支。当前A13/B14/C14，C14固定a10893d。

## 预备任务 B15：数字位置setter独立复核

分支 codex/re-0041-b15；worktree D:/CodexHome/visualizations/2026/10/23/01a1689f-d8c8-7821-aacd-286f467e884d/re0041-b15。须B14成果提交整合后，从最新管理提交启动。只复核B14最终实际范围正常字段/参数/返回合同，最多3核心函数及已给局部，不扩MiIO/天气全集。独占 reverse/reports/ap01/numeric-location-review-b15-0041-20261023.md、reverse/analysis/numeric-location-review-b15-0041-20261023/；必要精确纠正B14。原指令逐项接受/纠正/未核/来源及实际验证，差异检查后提交结束。共同约束适用。仅预备，未启动。

## 预备任务 A14：两函数来源识别独立复核

分支 codex/re-0041-a14；worktree D:/CodexHome/visualizations/2026/10/23/01a1689f-d8c8-7821-aacd-286f467e884d/re0041-a14。须A13成果提交整合后，从最新管理提交启动。仅复核A13两个函数本地源码匹配/差异、版本和厂商修改识别证据，不外连、不从符号名推定未修改开源实现。独占 reverse/reports/ap01/scheduler-source-review-a14-0041-20261023.md、reverse/analysis/scheduler-source-review-a14-0041-20261023/；必要精确纠正A13。按证据接受/纠正/未核及实际静态验证，差异检查后提交结束。共同约束适用。仅预备，未启动。

## 预备任务 C15：文本入口前置helper

分支 codex/re-0041-c15；worktree D:/CodexHome/visualizations/2026/10/23/01a1689f-d8c8-7821-aacd-286f467e884d/re0041-c15。须C14验收允许后，从最新管理提交启动。仅恢复C13/C14文本入口直接调用的a00dddf4前置helper正常参数/返回/门控合同及最多两个直接依赖，不扩完整GUI/断言系统，不做诊断/缺陷触发。先核本地已恢复成果避免重复；来源未知不得自动称私有或开源排除。暂不重复泛搜LVGL源码（C13已核sdk/tooling文件名未找到可靠版本）；若已有参考源明确可用可记录，但不外连。独占 reverse/reports/ap01/text-precondition-c15-0041-20261023.md、reverse/analysis/text-precondition-c15-0041-20261023/。核原指令/ABI/事实推断未知、来源/实际验证，差异检查后提交结束。共同约束适用。仅预备，未启动。

## C14/C15交接更新

C14 867810f→c021206已整合，限定接受C13，无纠正；306B/101条、51字段/15全部直接控制目标核验通过。C15从c021206运行，agent /root/c15_text_precondition。C14工作树干净且整合可回收保留分支。当前A13/B14/C15三任务。

## 预备任务 C16：前置helper独立复核

分支 codex/re-0041-c16；worktree D:/CodexHome/visualizations/2026/10/23/01a1689f-d8c8-7821-aacd-286f467e884d/re0041-c16。须C15成果提交整合后，从最新管理提交启动。仅复核C15最终实际范围正常参数/返回门控合同及最多两个直接依赖，不扩GUI/断言系统或诊断触发。独占 reverse/reports/ap01/text-precondition-review-c16-0041-20261023.md、reverse/analysis/text-precondition-review-c16-0041-20261023/；必要精确纠正C15。原指令逐项接受/纠正/未核、来源/实际验证，差异检查后提交结束。共同约束适用。仅预备，未启动。

## B15验收后术语纠正授权补充

B14发现a009c5fc无位置/全局/配置写入，仅栈保存及区域码范围判定；这目前待B15独立核准。为让旧报告不继续传播setter误名，另将 reverse/reports/ap01/miio-deferred-settings-0041-20261023.md 独占授予B15：仅在独立核准后按原指令把a009c5fc相关setter命名澄清为validator/有效性判定，保留原调用、返回条件、持久化顺序，并加B14/B15续作链接，不扩展或改其他合同。未核准不得先改结论。共享status/task/README/覆盖仍由主窗口维护。

## 当前交接更新：A14 / B15 / C16

A13 7f44b57→77d4336已整合，范围/差异通过，技术待A14；A14从77d4336运行，agent /root/a14_source_review。B14 44ffc89→f723db0已整合，范围/差异通过，技术待B15；B15从f723db0运行，agent /root/b15_area_code_review，含核准后旧MiIO术语纠正。C15 450d127→7373c0f已整合，范围/差异通过，技术待C16；C16从7373c0f运行，agent /root/c16_preparation_review。A13/C15工作树干净且整合可回收保留分支，B14也已干净整合可回收。下一小任务候选C17只核a00ddbf6两个正常返回门；B16可转工厂active byte一个外部读者；A15待A14建议，避免重复追版本。

## 预备任务 C17：失效区域下游两个门控

分支 codex/re-0041-c17；worktree D:/CodexHome/visualizations/2026/10/23/01a1689f-d8c8-7821-aacd-286f467e884d/re0041-c17。须C16验收允许后，从最新管理提交启动。仅恢复a00ddbf6入口两个正常返回门及必要参数/字段合同，最多3核心函数/少量直接依赖；入口C15/C16调用与保留inventory。排除完整失效队列、显示刷新、全GUI/异常验证。独占 reverse/reports/ap01/invalidation-gates-c17-0041-20261023.md、reverse/analysis/invalidation-gates-c17-0041-20261023/。来源未知不自动排除；核原指令、事实推断未知/实际验证，差异检查后提交结束。共同约束适用。仅预备，未启动。

## 预备任务 B16：工厂active一个外部读者

分支 codex/re-0041-b16；worktree D:/CodexHome/visualizations/2026/10/23/01a1689f-d8c8-7821-aacd-286f467e884d/re0041-b16。须B15验收完成整合后，从最新管理提交启动。只恢复FactoryTestMode active byte62fc92b8在已解initializer和a009f178 callback之外的一个直接读取者合同，最多3核心函数；入口factory-test报告/既有inventory与留存引用。可以针对该byte一次有界静态引用定位，不重复蜂鸣全ROM扫描，不扩整个工厂UI或销毁；无法定位给明确搜索界限/未知。独占 reverse/reports/ap01/factory-active-reader-b16-0041-20261023.md、reverse/analysis/factory-active-reader-b16-0041-20261023/。核原指令宽度/调用/事实推断未知/来源/实际验证，差异检查后提交结束。共同约束适用。仅预备，未启动。

## 预备任务 A15：一个天气订阅消费点

分支 codex/re-0041-a15；worktree D:/CodexHome/visualizations/2026/10/23/01a1689f-d8c8-7821-aacd-286f467e884d/re0041-a15。须A14验收完成整合后，从最新管理提交启动。转weather-dataflow已知五槽订阅缺口，只恢复a00b3a68一个具体注册调用者及其callback首个天气数据消费点，最多3核心函数/少量直接依赖；先核后续报告避免重复。入口weather-dataflow报告的callback(data,user_arg)合同、保留inventory/调用者引用。先选有明确证据的小注册点，不接管全部天气UI/图标转换/生命周期。独占 reverse/reports/ap01/weather-subscriber-a15-0041-20261023.md、reverse/analysis/weather-subscriber-a15-0041-20261023/。核原指令及间接ABI、参数/数据宽度/借用与复制边界，事实推断未知、来源/实际验证，差异检查后提交结束。共同约束适用。仅预备，未启动。

## B15/B16交接更新

B15 fa7edde→30c7797已整合，限定接受B14；284B/88普通指令/16目标/29组独立断言通过。授权旧MiIO报告已将setter改为validator并加续作链接，保留调用、返回条件和持久化顺序；不是改ROM行为。B16从30c7797运行，agent /root/b16_factory_reader。B15工作树干净且整合可回收保留分支。当前A14/B16/C16，A15/C17已预备。

## A14/A15交接更新

A14 c5ddb11→92c9d2e已整合，限定接受A13，0核心纠正；248B/91条、24位域、2字符串、7Git记录/269源码行核验通过。A15从92c9d2e运行，agent /root/a15_weather_subscriber。A14工作树干净且整合可回收保留分支。当前A15/B16/C16；本地NuttX12.10语义参考不等于认证ROM版本/未修改实现，开源新增排除仍0。

## C16/C17交接更新

C16 16190f1→f482b78已整合，限定接受C15，无纠正；226B/81条独立位域解析/52合同断言通过。C17从f482b78运行，agent /root/c17_invalidation_gates。C16工作树干净且整合可回收保留分支。当前A15/B16/C17；B16有界直接编码定位仅命中已解initializer/callback，外部读者仍未知，待其正式交付/B17复核，不扩扫描。

## B16/B17交接更新

B16 1b87a2f→0e1d5b9已整合，范围/差异通过，技术待B17；B17从0e1d5b9运行，agent /root/b17_factory_review。B16仅给一次有界命中（已有initializer sb/callback lbu），外部读者未知，不宣称不存在。B16工作树干净且整合可回收保留分支。当前A15/B17/C17。

## C17/C18交接更新

C17 3920202→e29de84已整合，范围/差异通过，技术待C18；C18从e29de84运行，agent /root/c18_gates_review。C17仅入口两个正常返回门及两个必要helper，不认证第三门/最终提交。C17工作树干净且整合可回收保留分支。当前A15/B17/C18。

## 预备任务 B17：工厂active读者独立复核

分支 codex/re-0041-b17；worktree D:/CodexHome/visualizations/2026/10/23/01a1689f-d8c8-7821-aacd-286f467e884d/re0041-b17。须B16成果提交整合后，从最新管理提交启动。仅复核B16一个读者的原指令/byte宽度/调用触发条件或有界检索结论，不扩工厂UI/销毁。独占 reverse/reports/ap01/factory-active-review-b17-0041-20261023.md、reverse/analysis/factory-active-review-b17-0041-20261023/；必要精确纠正B16。逐项接受/纠正/未核、来源/实际验证、差异检查后提交结束。共同约束适用。仅预备，未启动。

## B17整合记录

bd7747d→319dbdf；范围/差异通过，原编码/引用边界限定验收。纠正opcode0x13筛选、起点范围/跨边界读取、无代码数据过滤及ROMFS出处说明；不改变两个实际命中或外部读者未知结论。

## 预备任务 C18：下游门控独立复核

分支 codex/re-0041-c18；worktree D:/CodexHome/visualizations/2026/10/23/01a1689f-d8c8-7821-aacd-286f467e884d/re0041-c18。须C17成果提交整合后，从最新管理提交启动。仅复核C17入口两个正常返回门/必要字段和参数，最多3核心函数及已给局部，不扩失效队列/GUI全集。独占 reverse/reports/ap01/invalidation-gates-review-c18-0041-20261023.md、reverse/analysis/invalidation-gates-review-c18-0041-20261023/；必要精确纠正C17。原指令逐项接受/纠正/未核、来源/实际验证，差异检查后提交结束。共同约束适用。仅预备，未启动。

## C18整合记录

41ab2b2→dde1cfd；限定接受C17无实质纠正；312B/101条/38字段断言/49项检查/17控制目标核验通过。未认证候选身份、第三门及最终提交。

## 预备任务 A16：天气订阅消费独立复核

分支 codex/re-0041-a16；worktree D:/CodexHome/visualizations/2026/10/23/01a1689f-d8c8-7821-aacd-286f467e884d/re0041-a16。须A15成果提交整合后，从最新管理提交启动。仅复核A15一个注册点及callback首个数据消费合同、间接ABI/借用复制边界，最多3核心函数，不扩全部天气UI。独占 reverse/reports/ap01/weather-subscriber-review-a16-0041-20261023.md、reverse/analysis/weather-subscriber-review-a16-0041-20261023/；必要精确纠正A15。原指令逐项接受/纠正/未核、来源/实际验证，差异检查后提交结束。共同约束适用。仅预备，未启动。

## A16整合记录

b8614d5→ae3956f；8窗口420B/140指令/40编码提取核验通过。限定接受A15三核心合同，精确纠正图标边界首参为load32(context+0x20)，不扩图标内部。生命周期、插槽实际成功、源码版本仍未知。

## 预备任务 B18：正常接收阶段与转义标志

分支 codex/re-0041-b18；worktree D:/CodexHome/visualizations/2026/10/23/01a1689f-d8c8-7821-aacd-286f467e884d/re0041-b18。须B17验收完成整合后，从最新管理提交启动。转正常EsUnitProtocol私有协议：只恢复a00a8330内接收stage取值和escape标志的生产/消费及正常字节流阶段转换，最多该函数与两个直接依赖（可含a00ee934）。入口usb-interface-ota报告已有逐字节/CRC简述、保留dossier和whole-rom source_paths的EsUnitProtocol.c引用；先核后续报告是否已给完整状态表避免重复。已解CRC算法/分派ABI不重做，只引用合同；不扩完整OTA/队列、不做长度审计/漏洞研究/畸形输入或任何回放，不运行历史UART脚本。独占 reverse/reports/ap01/uart-normal-parser-b18-0041-20261023.md、reverse/analysis/uart-normal-parser-b18-0041-20261023/。交付正常状态转换表/可读伪代码、准确读写地址、事实推断未知、来源/原指令/实际静态验证，保留原返回/清理行为不擅自修复；差异检查后提交结束。共同约束适用。仅预备，未启动。

## B18整合记录

fff077c→fad8df6；范围/差异通过，正常接收stage/escape与原清理行为交付，技术待B19。未执行固件/回放/外连，不开展缺陷调查。

## 预备任务 C19：第三门局部合同

分支 codex/re-0041-c19；worktree D:/CodexHome/visualizations/2026/10/23/01a1689f-d8c8-7821-aacd-286f467e884d/re0041-c19。须C18验收允许后，从最新管理提交启动。只恢复a00ddab4(obj,&local)作为a00ddbf6第三门的参数/局部读写/返回及其直接消费条件，最多3核心函数；入口C17/C18及保留inventory。不要因前门已解扩成完整失效队列/全GUI，不推定最终显示刷新；先核是否已有报告解决。独占 reverse/reports/ap01/invalidation-third-gate-c19-0041-20261023.md、reverse/analysis/invalidation-third-gate-c19-0041-20261023/。核原指令/事实推断未知/来源/实际验证，差异检查后提交结束。共同约束适用。仅预备，未启动。

## C19整合记录

ee172d4→9270abb；范围/差异通过，472B/169条/69断言/40目标/4厂商原位域核验，技术待C20。返回1不证明刷新，失败交集也已写局部副本，两个变换callee未知。

## 预备任务 A17：天气当前值首消费

分支 codex/re-0041-a17；worktree D:/CodexHome/visualizations/2026/10/23/01a1689f-d8c8-7821-aacd-286f467e884d/re0041-a17。须A16验收完成整合后，从最新管理提交启动。仅恢复天气callback a00ab6ea调用的a008ce16(arc,current)正常参数/字段/返回合同及最多一个直接依赖，最多3核心函数。入口A15/A16中已知当前温度首消费点；不重复a008ce90范围helper，不扩图标/对象生命周期/全天气UI。先核后续报告是否已解。独占 reverse/reports/ap01/weather-current-consumer-a17-0041-20261023.md、reverse/analysis/weather-current-consumer-a17-0041-20261023/。核原指令及宽度/事实推断未知/来源和实际静态验证，差异检查后提交结束。共同规则适用。仅预备，未启动。

## A17整合记录

f95d973→2400931；范围/差异通过，136B/44指令/20编码/2厂商word核验，技术待A18。只恢复current局部钳位/写入调用，update helper/生命周期未知。

## 预备任务 B19：正常接收状态独立复核

分支 codex/re-0041-b19；worktree D:/CodexHome/visualizations/2026/10/23/01a1689f-d8c8-7821-aacd-286f467e884d/re0041-b19。须B18提交整合后，从最新管理提交启动。只复核B18正常接收stage/escape生产消费及直接依赖，最多3核心函数，不做长度审计/异常回放/缺陷验证/OTA扩展。独占 reverse/reports/ap01/uart-normal-parser-review-b19-0041-20261023.md、reverse/analysis/uart-normal-parser-review-b19-0041-20261023/；必要精确纠正B18。原指令逐项接受/纠正/未核、来源/实际静态验证，差异检查后提交结束。共同规则适用。仅预备，未启动。

## B19整合记录

a5e40e7→b105687；限定接受B18无纠正，204条/35操作数/21控制流/7store字段及既有th.srb模型核验通过。初始化、全局写者、回调副作用/真实时序仍未知；不做历史回放。

## 预备任务 C20：第三门独立复核

分支 codex/re-0041-c20；worktree D:/CodexHome/visualizations/2026/10/23/01a1689f-d8c8-7821-aacd-286f467e884d/re0041-c20。须C19提交整合后，从最新管理提交启动。仅复核C19第三门参数/局部读写/返回与直接消费条件，最多3核心函数，不扩失效队列/GUI全集。独占 reverse/reports/ap01/invalidation-third-gate-review-c20-0041-20261023.md、reverse/analysis/invalidation-third-gate-review-c20-0041-20261023/；必要精确纠正C19。逐项接受/纠正/未核/来源和实际静态验证，差异检查后提交结束。共同规则适用。仅预备，未启动。

## C20整合记录

d6b79f6→fe1fcd4；限定接受C19无实质纠正；472B/169条/40目标与4厂商字/903机械检查通过。身份候选、失败写区域、祖先循环/caller零门成立，不推定1为刷新；两个opaque变换/队列完整行为仍未知。

## 预备任务 A18：当前值消费独立复核

分支 codex/re-0041-a18；worktree D:/CodexHome/visualizations/2026/10/23/01a1689f-d8c8-7821-aacd-286f467e884d/re0041-a18。须A17提交整合后，从最新管理提交启动。只复核A17正常参数/字段/返回合同及最多一个直接依赖，不扩天气UI/图标/生命周期。独占 reverse/reports/ap01/weather-current-review-a18-0041-20261023.md、reverse/analysis/weather-current-review-a18-0041-20261023/；必要精确纠正A17。逐项接受/纠正/未核、来源和实际静态验证，差异检查后提交结束。共同规则适用。仅预备，未启动。

## 预备任务 B20：正常排队命令消费

分支 codex/re-0041-b20；worktree D:/CodexHome/visualizations/2026/10/23/01a1689f-d8c8-7821-aacd-286f467e884d/re0041-b20。须B19验收完成整合后，从最新管理提交启动。只恢复a01915bc尝试消费排队命令的正常字段/选择顺序/调用返回合同及最多两个直接依赖；入口usb-interface-ota报告0x24事件简述、dock报告四待发槽与保留dossier。先核后续报告避免重复。只解释一次取队列动作与槽所有权，不扩完整OTA/超时失败/漏洞调查/长度审计，不运行历史回放。独占 reverse/reports/ap01/queued-command-consume-b20-0041-20261023.md、reverse/analysis/queued-command-consume-b20-0041-20261023/。核原指令/ABI/原有清理与返回，事实推断未知/来源和实际静态验证，差异检查后提交结束。共同规则适用。仅预备，未启动。

## 预备任务 C21：变换前置callee

分支 codex/re-0041-c21；worktree D:/CodexHome/visualizations/2026/10/23/01a1689f-d8c8-7821-aacd-286f467e884d/re0041-c21。须C20验收完成整合后，从最新管理提交启动。只恢复a00dbff4正常参数/返回含义及是否写区域的局部合同，最多3核心函数/必要直接依赖；入口C19/C20中两个区域变换前的非零门，不同时接管a00dca48或完整变换库/GUI。独占 reverse/reports/ap01/transform-predicate-c21-0041-20261023.md、reverse/analysis/transform-predicate-c21-0041-20261023/。核原指令和调用者消费、事实推断未知/来源/实际静态验证，差异检查后提交结束。共同规则适用。仅预备，未启动。

## 用户要求的最终收尾合并

A18 2d443ab→8efb746：限定接受A17，无纠正；158B/50条/18编码检查，原A17的44条记录吻合。

B20 1815c05→46af044：正常四槽消费合同自验208B/70条/27断言/4调用目标，已合并，待独立复核；memcpy内部、并发/生命周期、实际发送结果和状态写入者未知。

C21 9c4ef73→dcda887：44B谓词及调用切片自验82B/33条/70检查，已合并，待独立复核；正式字段名/来源版本/a00dca48内部未知。

三任务均按通知收尾并结束，没有启动后继。用户此次停止滚动派发要求优先于先前维持三agent规则。任务分支保留，干净且已整合的worktree回收。全项目仍未完成，禁止以此次收尾标记全目标complete。


## 六路恢复前管理交接归档

# 0041 静态功能恢复：滚动管理交接

2026-10-23。主窗口仅管理、验收和整合；实质性逆向及技术复核交给独立 worktree 的 subagent。

## 共同规则

当前目标是全部非开源功能静态恢复；尚未完成，不计算整体百分比。禁止执行固件、连接设备/服务、缺陷验证、畸形输入、修改安全检查、ROM、生产代码或分析器模型。新增研究只写 reverse/analysis、reverse/reports/ap01。当前用户授权本地提交和整合，覆盖旧 task.md 的“不提交”历史限制；禁止推送。

共同要求：独立分支/工作树；每次 shell 命令显式指定该 worktree 为工作目录，并在 PowerShell 显式 Set-Location（shell 启动可能改变目录）。不修改主工作区、其他 worktree 或共享 status/task/README/覆盖索引；不撤销他人修改；不创建下级 agent；不自行领取下一任务。已有忽略证据、ROM、工具可从主仓库绝对路径只读访问；不可复制整份工作区，不可共享可写数据库。临时产物只能使用任务专属路径。只读静态证据优先。

交付须回答问题，列函数地址/参数/返回值/调用关系，必要伪代码/结构体，指令地址与可定位证据，事实/推断/未知、来源状态和恢复程度、实际验证及一个小后续建议。涉及边界/厂商指令/扩展/间接调用须核原始指令，不仅依赖反编译。完成后检查差异、相称验证、提交独占文件，报告提交 ID、结论、验证、未知并结束。遇安全限制记录操作及返回原因，不绕过或反复重试。

用户最新收尾要求优先：通知现有agent尽快完成当前任务，不再创建新agent，然后合并全部当前成果。先前“维持三个运行中的subagent”的要求在本次收尾期间停止适用；所有预备任务只保留未启动，不自动补位。

历史调度规则（本次收尾不再启动后继）：用户此前强调维持三个运行中的subagent是调度硬要求。预备后继任务；任务完成后先检查独占范围、证据完整性、实际验证和差异，本地整合，从最新管理提交建立新分支/worktree启动新agent，再更新汇总和回收旧树。最多三个同时运行，不长期复用同一agent承担不同任务。语义冲突和技术判断交新subagent，不盲选。未提交或未整合成果不得强删，保留有价值分支。

主仓库：D:/Documents/PlatformIO/Projects/cuktech-ap01-firmware。工作树父目录：D:/CodexHome/visualizations/2026/10/23/01a1689f-d8c8-7821-aacd-286f467e884d；各任务为re0041-<id>。只读忽略证据/ROM不随Git工作树自动出现，用主仓库绝对路径读取；禁止复制整份未提交工作区。

## 本次收尾结果

用户要求现有subagent快速完成当前任务、不再开启新subagent并合并成果。本次收尾已完成，所有agent已结束，不自动补位；滚动派发暂停。预备任务只保留作后续候选，须用户另行恢复后再启动。

| 已结束任务 | 任务提交 | 管理分支整合提交 | 验收状态 |
| --- | --- | --- | --- |
| A18 | 2d443ab | 8efb746 | 对A17的限定技术复核通过，无纠正 |
| B20 | 1815c05 | 46af044 | 独占范围/差异和任务自验通过；待独立技术复核 |
| C21 | 9c4ef73 | dcda887 | 独占范围/差异和任务自验通过；待独立技术复核 |

三任务工作树仅在确认干净且提交已整合后回收，分支和提交保留。不启动A19/B21/C22或其他预备任务。整体0041非开源功能恢复目标仍未完成；收尾完成不等于逆向全部完成。没有推送。

## 已整合概况与开放缺口

共同研究基线7c17501，后续均通过明确本地Git提交管理，不另建哈希/复制清单。限定验收与报告链接见[覆盖记录](private-coverage-0041.md)。蜂鸣正常停机/确认消费者、timer最终停止删除、完整UI/订阅销毁、MCU内部程序及准确来源版本等仍开放；不得将局部验收变为模块/全ROM完成。没有新增已认证开源排除，不计算全ROM百分比。

此前任务书与提交映射已迁移到[历史任务交接](rolling-task-history-0041-20261023.md)，保留原文；历史状态只代表当时，当前以本次收尾结果为准。以下预备任务均未启动，用户另行恢复前不执行。

## 预备任务 A19：天气图标消费callee

分支 codex/re-0041-a19；worktree D:/CodexHome/visualizations/2026/10/23/01a1689f-d8c8-7821-aacd-286f467e884d/re0041-a19。须A18验收完成整合后，从最新管理提交启动。只恢复A15/A16明确未解的a0198946(load32(context+0x20),icon)正常参数/字段/返回合同及最多两个直接依赖，最多3核心函数。先核已有后续报告，A17已仅检索未见callee合同；不扩全部图标/天气UI/生命周期。独占 reverse/reports/ap01/weather-icon-consumer-a19-0041-20261023.md、reverse/analysis/weather-icon-consumer-a19-0041-20261023/。核原指令/指针与地址边界/来源/事实推断未知/实际静态验证，差异检查后提交结束。共同规则适用。仅预备，未启动。

## 预备任务 B21：排队消费独立复核

分支 codex/re-0041-b21；worktree D:/CodexHome/visualizations/2026/10/23/01a1689f-d8c8-7821-aacd-286f467e884d/re0041-b21。须B20提交整合后，从最新管理提交启动。仅复核B20正常一次取槽/选择/所有权/调用返回合同，最多3核心函数；不扩完整OTA/超时调查/异常输入或回放。独占 reverse/reports/ap01/queued-command-review-b21-0041-20261023.md、reverse/analysis/queued-command-review-b21-0041-20261023/；必要精确纠正B20。逐项接受/纠正/未核、来源和实际静态验证，差异检查后提交结束。共同规则适用。仅预备，未启动。

## 预备任务 C22：变换前置callee独立复核

分支 codex/re-0041-c22；worktree D:/CodexHome/visualizations/2026/10/23/01a1689f-d8c8-7821-aacd-286f467e884d/re0041-c22。须C21提交整合后，从最新管理提交启动。只复核C21正常参数/返回/是否写区域及必要直接依赖，最多3核心函数，不扩完整变换库或GUI。独占 reverse/reports/ap01/transform-predicate-review-c22-0041-20261023.md、reverse/analysis/transform-predicate-review-c22-0041-20261023/；必要精确纠正C21。原指令逐项接受/纠正/未核、来源及实际静态验证，差异检查后提交结束。共同规则适用。仅预备，未启动。


## 六路恢复首批复核已整合

C22：3d59b72→004ff56；B21：d461760→99c02ab。两任务独占范围、差异、报告完整性、JSON及本地链接检查通过。技术判断由独立agent作出：均限定接受，无语义纠正。原worktree干净，待管理者回收，分支保留。

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


## D01/F01恢复成果整合并转独立复核

D01 475b43a→919051d；F01 3df638e→4a897ee。管理范围/差异/JSON/链接检查通过；技术待D02/F02独立复核。原树已确认干净，待回收；分支保留。

### D01：正常命令从描述符提交到构帧、部分写及完成通知

- 分支：codex/re-0041-d01
- worktree：D:/CodexHome/visualizations/2026/10/23/01a1691a-e178-7710-86c0-84c2ff2d3dfb/re0041-d01
- 业务问题/证据入口：usb-interface-ota、queued-command-consume-b20、uart-normal-parser-b18/b19、dock-presence-polling；入口 a01951e2/a00ee9ce/a01a4ff8/a00ee96c/a00a8330，活动区62fcb2f0
- 闭包、包含/排除、可保留合同和断边：恢复提交→活动副本/入队→构帧→部分写→正常完成事件闭包，约5–12核心函数及必要直接依赖。B20槽消费、B18解析和CRC按既有合同核对，不重复完整解码；不修改或复核B20原文，疑义报告管理者。排除超时异常、长度审计、漏洞调查、OTA全模块、历史回放。断边须列底层write合同、回调ABI、状态写者和资源归还限制。
- 独占报告：reverse/reports/ap01/uart-send-lifecycle-d01-0041-20261023.md
- 独占分析目录：reverse/analysis/uart-send-lifecycle-d01-0041-20261023/
- 基线：启动时最新管理提交，见派发记录；其他完成标准及验证遵循共同规则。发现范围外独立业务先报告，不自行扩展。


### F01：MiIO共享延后设置timer的创建、提交、消费及控制生命周期

- 分支：codex/re-0041-f01
- worktree：D:/CodexHome/visualizations/2026/10/23/01a1691a-e178-7710-86c0-84c2ff2d3dfb/re0041-f01
- 业务问题/证据入口：miio-deferred-settings、buzzer-backlight-round3、weather-scheduling、numeric-location-review-b15；入口 a009d286/a00a0bd8/a00a0e78/a009d8bc/a00a5b90，timer/data字段见已有证据
- 闭包、包含/排除、可保留合同和断边：恢复私有timer初始化→三个已知属性提交→数据槽交接→callback清理→停止或销毁连接的小闭包，约5–12核心函数，已恢复kind0..6仅核接口及顺序，不逐分支重复。优先展开真实初始化/控制调用者，不重复kind2直接提交者扫描。保留libuv/allocator/天气重排合同，不重做通用timer库算法；来源不认证则仍列缺口。排除异常重复提交实验、全MiIO、外连。断边须说明外部串行化、data重读、资源与最终销毁。
- 独占报告：reverse/reports/ap01/miio-deferred-lifecycle-f01-0041-20261023.md
- 独占分析目录：reverse/analysis/miio-deferred-lifecycle-f01-0041-20261023/
- 基线：启动时最新管理提交，见派发记录；其他完成标准及验证遵循共同规则。发现范围外独立业务先报告，不自行扩展。


## A19/E01整合并转独立复核

A19 e601fbd→f40ea13；E01 8e2c319→0ff74d9。独占范围/差异/交付/JSON/本地链接通过，技术待A20/E02。A19两个JSON、E01五个JSON解析与报告链接均通过；已确认原树干净，分支保留。

### A19：天气订阅 callback 到图标与控件更新的数据流

- 分支：codex/re-0041-a19
- worktree：D:/CodexHome/visualizations/2026/10/23/01a1691a-e178-7710-86c0-84c2ff2d3dfb/re0041-a19
- 业务问题/证据入口：weather-subscriber-a15、weather-subscriber-review-a16、weather-current-consumer-a17、weather-current-review-a18；入口 a00ab6b0/a00ab6ea、a0198946(load32(context+0x20),icon)
- 闭包、包含/排除、可保留合同和断边：核实图标值的生产、传递、资源选择与控件消费者如何衔接；以图标 callee 及必要更新/资源选择依赖组成约5–12核心函数闭包，针对已验收callback只核合同。保留已知arc范围/current合同。排除全部天气UI、网络请求、重复getter和全量源码搜索。无法闭合时列资源身份、更新副作用、销毁断边。
- 独占报告：reverse/reports/ap01/weather-icon-flow-a19-0041-20261023.md
- 独占分析目录：reverse/analysis/weather-icon-flow-a19-0041-20261023/
- 基线：启动时最新管理提交，见派发记录；其他完成标准及验证遵循共同规则。发现范围外独立业务先报告，不自行扩展。



### E01：UiIFace端口项嵌套资源生产消费与清理

- 分支：codex/re-0041-e01
- worktree：D:/CodexHome/visualizations/2026/10/23/01a1691a-e178-7710-86c0-84c2ff2d3dfb/re0041-e01
- 业务问题/证据入口：uiiface-lifecycle、ui-total-consumers、theme-total-state、mode-control；入口 a00a3d80、a00a8582 的cmd55初始化片段，总对象62fcb2cc，item步长0x1a8，指针+0x28/+0x2c/+0x30/+0x34/+0x38
- 闭包、包含/排除、可保留合同和断边：恢复一组端口项嵌套字段的分配/替换→业务消费→清零/释放闭包，约5–12核心函数及必要直接依赖，避免重新恢复全局快照getter和已验收订阅链。可在该字段族内调整函数集合，不接管独立页面。保留allocator/链表合同；排除全UI/全响应/全销毁扫描。无法证实连接到全局deinit时明确断边，不拼造释放链。
- 独占报告：reverse/reports/ap01/uiiface-item-ownership-e01-0041-20261023.md
- 独占分析目录：reverse/analysis/uiiface-item-ownership-e01-0041-20261023/
- 基线：启动时最新管理提交，见派发记录；其他完成标准及验证遵循共同规则。发现范围外独立业务先报告，不自行扩展。


## D02/F02限定技术验收与补位

D02 9357e0e→1a80623限定接受D01，无纠正；F02 a2626c8→17a125f限定接受F01，无纠正。管理独占范围/差异/JSON/链接检查通过；未知驱动、cursor、两个厂商算术、loop最终销毁/串行化等继续保留。已确认两旧树干净，分支保留。

## 当前完整任务书 F02（已启动，基线4a897ee）

任务ID F02，独立技术复核F01共享延后设置timer完整小闭包；新agent承担，非原作者。分支codex/re-0041-f02；worktree D:/CodexHome/visualizations/2026/10/23/01a1691a-e178-7710-86c0-84c2ff2d3dfb/re0041-f02；基线为启动时含F01的最新管理提交，派发记录补确切commit。独占reverse/reports/ap01/miio-deferred-review-f02-0041-20261023.md和reverse/analysis/miio-deferred-review-f02-0041-20261023/。

问题：F01所述loop/timer初始化→三个已知属性提交→8B请求/data交接→到期stop与callback ABI→业务清理→deinit断边是否由指令成立？入口F01报告及instruction-evidence.json、miio-deferred-settings、weather-scheduling；核心a005a736相关片段/a009d106/a009d146/a009d286/a009d304/a009d8bc/a00a0e78/a00a0bd8/a00a5b90/a01b2b5c前缀，约5–12合同。已验收kind0..6仅针对核接口，不重做通用heap或全MiIO。重点初始化不清data、data与req.kind不同重读、64位参数ABI、callback寄存器/间接重读、free后清data与不同timer对象，两个UNKNOWN厂商算术不得默认为已认证；其未覆盖部分须明确影响边界。不开展异常重复提交实验，不借此修复原程序。

完成逐项接受/纠正/未核，独立核原字节及关键厂商/调用/宽度，必要伪代码布局状态所有权、来源、实际验证与断边；原作者验证不能替代独立复核。准确区分局部片段与全容器、stop与最终close，以及有界负结果。必要纠正写独占报告不改F01原文，不扩loop关闭walker恢复；可将其作为后继。allocator/已验收天气重排与业务kind保留明确合同。排除固件执行、外连、漏洞、历史回放、正式ROM/生产/模型修改；共同规则适用。


## 当前完整任务书 D02（已启动，基线919051d）

任务ID D02，新agent独立技术复核D01正常发送完整闭包。分支codex/re-0041-d02；worktree D:/CodexHome/visualizations/2026/10/23/01a1691a-e178-7710-86c0-84c2ff2d3dfb/re0041-d02；基线启动时含D01的最新管理提交，派发补确切commit。独占reverse/reports/ap01/uart-send-review-d02-0041-20261023.md及reverse/analysis/uart-send-review-d02-0041-20261023/。

业务问题：D01新增构帧、部分write、操作表ABI和正常完成责任边是否符合指令？核心D01报告10函数身份：a01951e2/a01915bc/a00ee9ce/a01a4ff8/a00ee96c/a0027e94/a0025874、a00a8330正常响应窗口/a00a8582 cmd58与0x24/a0191652。先读最新B21独立验收，槽、提交、解析/缓存等既验收合同针对性核对，不复制全套B21证据。重点新增CRC/转义次序、frame_len/cursor初始化及重读/写宽、精确相等完成门、两层write操作表ABI与对象取得/归还边界，厂商字须原指令核。正常cmd58返回空闲/后继提交/0x24门控仅核串接一致性，不能外推所有命令。

逐项接受/纠正/未核；交付可读伪代码/结构/状态所有权、原字节及地址证据、事实推断未知、来源、实际独立静态验证与断边。保留驱动/冷启动cursor/回调寿命/最终销毁边界，不扩实际驱动恢复、超时、异常输入或长度审计。必要纠正只写独占报告，不改D01/B21原文。复制/比较/已验收CRC/轮询可保留明确合同，来源未知不排除。只静态，不固件执行/外连/漏洞/历史回放，不改ROM生产模型；共同规则适用。

近期恢复整合：D01 475b43a→919051d、F01 3df638e→4a897ee；均待独立技术复核，不能标为验收通过。


## E02验收、G01/H01恢复整合及新补位

E02 e9f1fe4→78b8a5d限定接受E01，无纠正；G01 4a695ed→41046d1、H01 ec61679→c9336de为待独立复核恢复。独占范围/差异/完整性/JSON/本地链接通过，旧树均干净，成果已整合，分支保留。E03/G02/H02从对应最新管理提交启动，见当前队列。

## 当前完整任务书 G01（已启动，基线004ff56）

任务ID G01；业务问题：a00dca48(obj,area,1)如何读取对象属性、形成区域变换、写回区域并返回给失效裁剪调用者？需恢复它与必要直接依赖的完整小闭包，参考约5–12函数，不以一个helper结束，也不扩展整个变换库。入口为C19/C20、C21与C22两处caller合同；C22建议只核此边，未读取内部callee，核心依赖清单当前未知，须执行agent自行按原证据定位。拟分支codex/re-0041-g01；拟worktree D:/CodexHome/visualizations/2026/10/23/01a1691a-e178-7710-86c0-84c2ff2d3dfb/re0041-g01。基线为C22整合后启动时最新管理提交，启动记录补确切commit。独占reverse/reports/ap01/region-transform-flow-g01-0041-20261023.md与reverse/analysis/region-transform-flow-g01-0041-20261023/。

包含对象→参数提取→局部坐标/区域处理→写回与caller消费；针对C22已验收部分仅核接口，不重做全失效门控。完成标准为参数/返回、调用顺序、字段宽度/符号、区域每次读写、局部副本和所有权清楚，提供正常路径伪代码/布局/转换、原指令证据与必要静态核验。数学/标准库只有来源认证可作为排除，未认证不得静默跳过；底层算术可作明确合同边界但列证据与限制。未知厂商字不修改模型、不靠反编译补语义。排除全GUI、最终物理刷新、异常坐标/畸形输入/漏洞、执行固件或历史回放。闭合失败要列具体callee/坐标字段/浮点ABI/实际显示断边及一个后继闭包。共同规则全部适用。


## 当前完整任务书 H01（已启动，基线99c02ab）

任务ID H01；业务问题：a00b8bc2调用a00b3a68的另一天气订阅者，如何注册callback/userdata、消费天气字段，并在页面或对象退出时注销/清理？a00b8bc2是已知调用点，不能先当函数入口；准确包含函数、callback地址和清理入口均须由执行agent据指令定位。A19只确认该incoming ref，未扩扫，故这些不是既有结论。参考weather-dataflow、A15/A16已验收五槽/双参callback合同及A19天气图标数据流。拟分支codex/re-0041-h01；worktree D:/CodexHome/visualizations/2026/10/23/01a1691a-e178-7710-86c0-84c2ff2d3dfb/re0041-h01；实际基线为启动时最新整合管理提交。独占reverse/reports/ap01/weather-subscriber-lifecycle-h01-0041-20261023.md和reverse/analysis/weather-subscriber-lifecycle-h01-0041-20261023/。

功能范围是该一个订阅者正常注册→主要callback分支/字段消费→注销或对象清理闭包，参考5–12核心函数及必要短依赖，不以单一注册点草草完成。已验收五槽分发/arc/图标消费者只核相关合同；不恢复完整构造大函数、不重复a00a7766屏保分支、不扫描所有天气订阅者。callback与userdata须从原指令确认，保留宽度、借用/复制、重读和清理顺序；标准库只在来源可核实时排除。完成需交付原指令与地址、正常数据流/伪代码/结构、实际静态验证、事实推断未知和来源。无法证明清理或注销时给出明确断边及检索边界，不编造生命周期，不改模型或正式代码。排除网络请求、全UI、异常输入/缺陷/漏洞、固件执行/历史回放。共同规则适用。




## 当前完整任务书 E02（已启动，基线0ff74d9）

任务ID E02，新agent独立复核E01端口项嵌套字段完整闭包。分支codex/re-0041-e02；worktree D:/CodexHome/visualizations/2026/10/23/01a1691a-e178-7710-86c0-84c2ff2d3dfb/re0041-e02；启动基线为含E01最新管理提交，派发补确切commit。独占reverse/reports/ap01/uiiface-ownership-review-e02-0041-20261023.md及reverse/analysis/uiiface-ownership-review-e02-0041-20261023/。

业务问题：cmd51类型变化→五指针清理/分配→cmd52原位覆盖→a00f4740字段转换借用→失活/类型变化清零释放是否由指令成立？入口E01报告及21窗口、uiiface-lifecycle/ui-total-consumers/mode-control；核心从a00a8582相关cmd50/51/52片段、a00a3d80/a00a53ee/a00f4740及E01列必要依赖圈定约5–12合同，不把大dispatcher全函数算已恢复。已验收快照/订阅/总对象接口针对核。重点分配尺寸/布局、类型和mask、指针持有与dst所有权、写宽/符号/原调用顺序、清理时点与多个入口一致性；来源未认证不得排除。

逐项接受/纠正/未核，独立原字节核验、必要伪代码布局状态所有权、事实推断未知、来源、实际静态验证和断边；必要纠正只独占报告不改E01。+34/+38实际UI读者、a00f4740调用者及dst消费、全局deinit连接可保留明确断边，不拼造释放链、不扩全页面或所有响应。标准allocator合同可保留并明示来源认证缺口。禁止固件执行/外连/漏洞/异常验证/历史回放/ROM生产模型修改；共同规则适用。

近期恢复整合：A19 e601fbd→f40ea13、E01 8e2c319→0ff74d9均待独立复核。当前因四恢复成果集中交付，暂为两恢复四复核；复核席位释放后优先业务断边，不等待整批结束。


## A20纠正后限定验收与A21补位

A20 6915ea9→ab67c6f：有纠正后限定接受A19。复核者裁定a00d8ffe实际callee为a00d7546，状态半字obj+0x28；原A19 add_flag对应说明以A20为准。其余接受和断边见A20。管理范围/差异/JSON/链接检查通过，原树干净且整合可回收，保留分支。A21从ab67c6f新树新agent启动。

## 当前完整任务书 A20（已启动，基线f40ea13）

任务ID A20，新agent独立复核A19天气图标条件闭包。分支codex/re-0041-a20；worktree D:/CodexHome/visualizations/2026/10/23/01a1691a-e178-7710-86c0-84c2ff2d3dfb/re0041-a20；启动基线为含A19的最新管理提交，派发补确切commit。独占reverse/reports/ap01/weather-icon-review-a20-0041-20261023.md及reverse/analysis/weather-icon-review-a20-0041-20261023/。先读A19及A15/A16/A18、weather-dataflow；旧arc/getter合同仅针对核。

业务问题：图标生产→ctx控件生产→code/全局byte条件映射→资源选择→image source/宽高/格式更新和失效调用是否匹配原指令？A19列11核心函数a00a5d5c/a00a6998/a0198946/a00d9044/a00d8f7c/a00dd454/a0082e32/a0082c8c/a00ed560/a01b1ee6/a00ed438及必要flag谓词a00d7446/a00d749e。完整闭包约5–12核心，重核实际可达正常分支，不扩大所有image类型/全GUI。重点两个图标转换不可合并、load32(ctx+0x20)参数、q!=0与q==1非对称、category15清/加flag顺序、source descriptor借用/释放、decoder-info条件性与更新顺序；资源格式校验只做相称静态核对，不把PNG标识/CRC等同解码执行。厂商字须原编码核验，准确库版本未认证不排除。

逐项接受/纠正/未核，独立原字节证据与必要伪代码结构状态所有权、事实推断未知、来源、实际静态验证与断边。decoder注册/info callback真实身份、全局byte生产者、widget/context销毁和物理绘制可保留断边，不恢复完整decoder库。必要纠正仅独占报告，不改A19。禁止固件执行/外连/漏洞/历史回放/ROM生产模型修改；共同规则适用。
