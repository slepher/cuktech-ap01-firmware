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


## G02/H02验收、D03/F03恢复整合与补位

G02 a579bc9→da4c9dc限定接受G01；H02 f47434d→dcc2a08限定接受H01，均无核心语义纠正。D03 b066e30→d07ed94、F03 d019bed→48af5ae已整合但待D04/F04独立复核。四项管理独占范围/差异/JSON/报告链接检查通过，原树均干净，分支保留。G03/H03/D04/F04从各自最新整合提交新树新agent补位，见当前队列。

## 当前完整任务书 D03（已启动，基线1a80623）

任务ID D03，业务恢复：UART写对象的取得→操作表选择→实际write→归还与缓冲借用合同。分支codex/re-0041-d03；worktree D:/CodexHome/visualizations/2026/10/23/01a1691a-e178-7710-86c0-84c2ff2d3dfb/re0041-d03；基线为D02整合后启动时最新管理提交。独占reverse/reports/ap01/uart-write-object-d03-0041-20261023.md及reverse/analysis/uart-write-object-d03-0041-20261023/。

入口D01已恢复a0027e94(fd,buffer,count)→a0025904(fd,&object)→a0025874(object,buffer,count)→a0027e54(object)，以及操作表object+0xc→+0x10→+0xc；普通fd槽62fc91b0。D02确认后的write ABI作为已验收合同，不重复帧编码/队列/parser。要回答此fd的对象如何取得和归还、操作表安装到哪个具体驱动入口、该正常write是否同步消费传入frame地址或保留其指针。以取得/归还/安装/具体write及必要直接依赖组成约5–12核心函数小闭包；若具体驱动入口无法唯一静态定位，列候选和精确间接断边，不冒称已恢复实际设备行为。

包含正常fd创建/配置至所需安装片段（仅为定位此write，不能扩全UART驱动），对象计数/锁/返回值传递、错误返回原序和buffer所有权；来源有可核实版本/比对才排除标准实现，厂商适配仍恢复。外部RTOS/通用复制和硬件最终效果可留明确合同；不为确认时序运行设备/固件。完成须伪代码/布局/调用/状态/资源归还、原指令地址与证据、事实推断未知、来源、相称静态验证和一个后继闭包。排除超时、异常输入、漏洞、完整驱动、历史回放、正式ROM生产模型修改、外连；共同规则适用。


## 当前完整任务书 F03（已启动，基线17a125f）

任务ID F03，业务恢复：共享timer注册链→关闭walker→handle关闭回调→data资源归还连接。分支codex/re-0041-f03；worktree D:/CodexHome/visualizations/2026/10/23/01a1691a-e178-7710-86c0-84c2ff2d3dfb/re0041-f03；基线F02整合后启动时最新管理提交。独占reverse/reports/ap01/miio-loop-close-f03-0041-20261023.md及reverse/analysis/miio-loop-close-f03-0041-20261023/。

入口F01/F02实际loop参数来自a005a736容器；a009d106初始化将timer62fc9428的+0x10/+0x14链接到loop+8/+0xc，deinit片段a005c9ea..ca99仅显式控制其他对象；F01列a009fb96为另一handle close边。walker/loop最终关闭入口当前未知，执行agent须由已有注册链引用/容器退出后调用关系定位，不凭libuv命名假造连接。要回答注册的9428能否经正常loop关闭链到达close callback，谁清理仍挂data，以及与容器释放的次序；正常无挂data/有业务请求两种静态路径分开描述，不做异常提交实验。

范围约5–12核心函数及必要依赖，只恢复该注册链的遍历/close/回调和业务衔接；已验收start/stop/请求callback仅核接口，不重解通用heap或全libuv。若loop关闭没有调用证据，给明确断边与有界搜索范围，不补一条理想销毁链、不重复全ROM泛扫。可核实开源候选记录来源版本及厂商修改边界，未知实现不排除。交付函数地址/ABI、结构与生命周期伪代码、原指令/厂商编码、事实推断未知、来源、实际静态核验与一个后继闭包。排除全MiIO、固件执行/外连/漏洞/历史回放/正式ROM生产模型修改；共同规则适用。

近期复核整合：D02 9357e0e→1a80623、F02 a2626c8→17a125f均无语义纠正，限定验收通过。A20运行中发现A19 add_flag内部callee/字段谓词需纠正，待正式报告提交，不将A19标为无纠正接受。当前恢复四路/复核两路。


## 当前完整任务书 G02（已启动，基线41046d1）

任务ID G02，新agent独立复核G01区域变换完整小闭包。分支codex/re-0041-g02；worktree D:/CodexHome/visualizations/2026/10/23/01a1691a-e178-7710-86c0-84c2ff2d3dfb/re0041-g02；基线含G01最新管理提交，派发补commit。独占reverse/reports/ap01/region-transform-review-g02-0041-20261023.md及reverse/analysis/region-transform-review-g02-0041-20261023/。

业务问题：a00dca48(obj,area,1)四点构造→父链选择→参数提取→点变换/算术→有符号包围框写回与caller是否吻合原指令？入口G01正式报告/原字节及C22合同，已知主链a00dca48→a00dc9ba→a00dc862→a0089e10，具体getter/算术依赖以G01正式11核心清单为准，不猜未交付地址。约5–12核心函数/必要直接依赖，C22已验收门控只针对核。重点flag1本节点/父链顺序、mode与C21字段对应关系、右/下+1与最终不减1、角度/比例/支点/符号宽度、厂商字和返回a0覆盖、栈点数组/指针持有。逐项接受纠正未核，必要纠正只独占文件，不改G01。算术来源未认证保留在范围，不靠反编译定厂商语义，不改模型。交付原指令与新独立验证、必要伪代码/结构/状态/所有权、事实推断未知、来源和断边。排除完整GUI/刷新队列/物理显示/异常坐标实验/固件执行/外连/漏洞/历史回放/ROM生产模型修改；共同规则适用。


## 当前完整任务书 H02（已启动，基线c9336de）

任务ID H02，新agent独立复核H01另一天气订阅者完整生命周期闭包。分支codex/re-0041-h02；worktree D:/CodexHome/visualizations/2026/10/23/01a1691a-e178-7710-86c0-84c2ff2d3dfb/re0041-h02；基线含H01最新管理提交，派发补commit。独占reverse/reports/ap01/weather-lifecycle-review-h02-0041-20261023.md及reverse/analysis/weather-lifecycle-review-h02-0041-20261023/。

问题：a00b821e构造注册点a00b8bc2→callback a00b5cd4→a00b5b58拆156B天气视图→a00b564e主要当前指标/七行消费→DELETE事件a00b3b26注销/清理是否由原指令成立？具体核心范围以H01正式函数清单为准，约5–12核心及必要依赖，已验收五槽双参分发/图标/arc只针对核合同。重点callback(data,page) ABI、page+0x10 wrapper与context区别、栈视图借用、LHU图标第二参及湿度零扩展、正常失败分支、先清context28word再注销再free(wrapper)的顺序与context最终释放断边。不能把a00b8bc2当新函数入口，不能把free(wrapper)写成free(ctx)。

独立原字节、间接/调用ABI、厂商字与宽度/返回覆盖核验，逐项接受/纠正/未核，纠正只独占报告不改H01；交付伪代码/布局/状态/所有权、事实推断未知、来源、实际静态验证和断边。已有图标/通用格式化等保留明确合同，精确来源未认证不得排除。constructor只核该type分支与必要失败清理，不扩全页面/所有天气格式/最终物理显示。ctx最终所有权和离页DELETE触发可留后继，不为关闭断边拼造理想销毁链。禁止固件执行/外连/漏洞/畸形输入/历史回放/ROM生产模型修改；共同规则适用。

最新整合：E02 e9f1fe4→78b8a5d通过限定复核；G01 4a695ed→41046d1、H01 ec61679→c9336de待独立复核。


## E03恢复与F04限定复核整合

E03 b0c4ea8→85c61e2待E04独立复核；F04 1a100d8→3aba13a限定接受F03，语义纠正0。管理范围/差异/JSON/链接检查通过，原树干净、提交已整合、分支保留。E04/F05新树新agent补位。

## 当前完整任务书 E03（已启动，基线78b8a5d）

任务ID E03，业务恢复a00f4740调用者→CTK数值dst消费及借用寿命小闭包。分支codex/re-0041-e03；worktree D:/CodexHome/visualizations/2026/10/23/01a1691a-e178-7710-86c0-84c2ff2d3dfb/re0041-e03；基线E02整合后最新管理提交。独占reverse/reports/ap01/ctk-view-dataflow-e03-0041-20261023.md及reverse/analysis/ctk-view-dataflow-e03-0041-20261023/。

业务问题：E01字段转换消费者a00f4740由哪个实际caller触发、如何取得端口号和dst、返回0/1怎样门控显示/数据更新、dst何时消费与归还？先读E01/E02及retained-consumer/dossier/incoming refs，只选一条有证据的真实caller和必要注册/清理片段，约5–12函数组成注册或触发→转换→主要dst消费者→释放/复用闭包。a00a389c的callback(userdata,item)已知，但E01明确它与a00f4740的直接关系未证实，不能直接拼成call chain。a00f4740内部转换与五资源生产/释放作为已验收合同针对核，不重复所有cmd50/51/52字节。

完成需准确ABI/端口索引/结构/返回分支/借用与复制/原顺序、伪代码状态与所有权、原指令证据/事实推断未知/来源/实际静态验证。未定位直接或间接caller则给明确引用搜索范围和候选断边，不将单helper认闭包完成。排除全CTK页面/全UI、+34/+38独立读者、全局deinit、异常输入/漏洞/固件执行/外连/历史回放、正式ROM生产模型修改；allocator/已有转换与订阅链保留明确合同。共同规则适用。


## 当前完整任务书 F04（已启动，基线48af5ae）

任务ID F04，新agent独立复核F03条件关闭链与真实loop退出断边。分支codex/re-0041-f04；worktree D:/CodexHome/visualizations/2026/10/23/01a1691a-e178-7710-86c0-84c2ff2d3dfb/re0041-f04；基线含F03最新管理提交。独占reverse/reports/ap01/miio-loop-close-review-f04-0041-20261023.md及reverse/analysis/miio-loop-close-review-f04-0041-20261023/。

问题：F03 type13 close→stop→pending→完成分派摘链→handle+0xc回调是否成立，是否足以连接9428共享timer与data归还，caller栈loop和返回后间接callback边证据范围是否准确？入口F03正式报告/21窗口1428B、F01/F02合同；已知a009fb96/a009fc50/a009fd94/a009c228/a009f524/a0098b4a及a005cc1e→a005cec6、a0081554/a00815f4 obj+0x2b8。具体完整核心以F03表为准，约5–12函数合同。已验收stop/data callback只针对核，关闭dispatcher完整正常type13和链表字段/回调ABI/写宽/顺序需独立原指令核。

逐项接受纠正未核；重点注册节点+0x10与close callback+0xc、到期callback+0x30区别，不自动调用业务data清理，caller loop参数身份/局部栈区和返回后对象参数不能混同。9428实际close登记/walker及obj+0x2b8安装/身份未解须保留精确断边，有界负搜索不得变不存在。必要纠正只独占报告不改F03。完成原字节/厂商编码/间接ABI、伪代码结构状态所有权、事实推断未知、来源、实际独立静态验证及一个后继闭包；不接管obj+2b8恢复或全loop/heap。排除异常提交/漏洞/固件执行/外连/历史回放/ROM生产模型修改；共同规则适用。


## D04纠正后限定验收及D05补位

D04 30a9d6f→59d81c2，有一处optional_mark非NULL分支伪代码纠正后限定接受D03；实际acquire a3=0主链不受影响，D03对应helper视图须以D04为准。管理范围/差异/JSON/链接检查通过，原树干净且已整合，分支保留；D05从59d81c2新树新agent补位。

## 当前完整任务书 D04（已启动，基线d07ed94）

任务ID D04，新agent独立复核D03 UART fd→实际write→同步缓冲所有权闭包。分支codex/re-0041-d04；worktree D:/CodexHome/visualizations/2026/10/23/01a1691a-e178-7710-86c0-84c2ff2d3dfb/re0041-d04；基线含D03最新管理提交。独占reverse/reports/ap01/uart-write-review-d04-0041-20261023.md及reverse/analysis/uart-write-review-d04-0041-20261023/。

业务问题：同名/dev/ttyS1的注册安装与fd62fc91b0怎样静态连接到具体write=a002c206；对象页式取得/引用加减和正常write是否同步消费frame并写TX ring，返回值与实际硬件交付的边界是否准确？核心按D03正式12函数表及短lower/context依赖，约5–12核心；已知a0025904/a00258e4/a00258a0/a0025874/a0027e54、注册a00296bc→a01b5a7e、inode ops a066d7c8、device62fc36d0、应用open a005ab1c、具体write a002c206，必要三初始化区。既验收D02 write wrapper/帧/队列/parser只针对核，不重做全链证据。

重点路径安装关联的条件性/别名与动态换表限制、24B对象/每页6项/引用临界区与锁范围、负返回/errno原序、按byte源读取与ring半字head/tail/缓冲复制、直接lower按值发送和未安装批量槽、frame指针不持有的范围、返回源字节接受数而非硬件完成。原厂商字/间接ABI/写宽与返回覆盖须独立原指令核；标准实现仅来源版本认证才排除。

逐项接受纠正未核，纠正只独占报告不改D03。来源未认证、完整path解析、零引用final close、ring后续a001a70a/DMA/tail/唤醒可保留精确断边，不恢复实际DMA后继或全UART驱动。交付原字节独立证据、必要伪代码布局状态所有权、事实推断未知、来源、实际静态验证与一个后继闭包。排除异常输入/超时/漏洞、固件执行/外连/历史回放/ROM生产模型修改；共同规则适用。

最新：G02→da4c9dc、H02→dcc2a08限定验收通过；D03→d07ed94、F03→48af5ae已整合待独立复核。旧动态快照仅记录当时，本表覆盖。


## A21/G03恢复及E04纠正验收整合

A21 fae576d→875f762待A22；G03 1b1ae05→f82380b待G04；E04 fb5aaeb→f31a27a有一处范围措辞纠正后限定接受E03：port1/2静态同栈布局，端口谓词互斥，非同次通知连续转换。相关描述以E04为准。管理范围/差异/JSON/报告链接检查通过，旧树均干净，成果已整合且分支保留；A22/E05/G04新树新agent补位。

## 当前完整任务书 A21（已启动，基线ab67c6f）

任务ID A21，业务恢复PNG decoder注册→info callback→正常图标描述符信息提取小闭包。分支codex/re-0041-a21；worktree D:/CodexHome/visualizations/2026/10/23/01a1691a-e178-7710-86c0-84c2ff2d3dfb/re0041-a21；基线含A20最新管理提交。独占reverse/reports/ap01/png-info-lifecycle-a21-0041-20261023.md及reverse/analysis/png-info-lifecycle-a21-0041-20261023/。

问题：A19的ROM PNG源在info dispatcher a0082c8c正常class0分支怎样匹配注册decoder、调用哪个确切info callback、向image setter返回哪些宽高/格式/状态，decoder对象注册及注销/生命周期如何衔接？入口A19/A20及a0082e32/a0082c8c/a00ed560合同，具体PNG注册/callback地址目前未知，agent须据原证据定位，不以PNG header/CRC代替执行路径身份。约5–12核心及必要依赖，注册→选择/间接ABI→正常PNG信息读取→结果返回→注册对象回收或已知常驻边界；不恢复完整像素解码/压缩通用算法/所有image格式。

A20对add_flag callee/字段谓词纠正须作为既有合同，不能沿用A19旧误名。PNG容器格式静态证据可用于参数界限，不进行畸形输入/漏洞/错误触发测试。恢复函数地址/布局/所有权/返回分支/原指令、事实推断未知、准确来源/版本或未认证状态、必要静态验证；精确decoder或注销未能定位时列断边与有界检索，不外连下载，不修改分析模型。标准实现只有可核实来源才排除，厂商注册/回调恢复。排除全GUI/最终显示、固件执行/外连/历史回放/ROM生产模型修改；共同规则适用。



## 当前完整任务书 G03（已启动，基线da4c9dc）

任务ID G03，业务恢复区域门控成功后的失效区域提交→合并/入队→直接消费闭包。分支codex/re-0041-g03；worktree D:/CodexHome/visualizations/2026/10/23/01a1691a-e178-7710-86c0-84c2ff2d3dfb/re0041-g03；基线含G02最新管理提交。独占reverse/reports/ap01/invalidation-submit-g03-0041-20261023.md及reverse/analysis/invalidation-submit-g03-0041-20261023/。

业务问题：a00ddbf6在第三门非零后从a00ddc7e继续，怎样使用已变换裁剪的入口区域副本、写入谁的区域记录/队列、何时合并或通知，以及哪一个直接消费者读取它？a00ddc7e只是已知续接地址，不是新函数入口；后段callee与实际队列结构目前未知，不按名字假设。先复用C22/G01/G02正常门控与变换合同，只对必要接口针对核，展开提交后段及其必要直接依赖/一个直接消费者，约5–12核心函数小闭包，不把整个显示刷新栈接管。

完成需原写入顺序、区域布局/容量状态、返回覆盖/失败原分支、合并次序、通知ABI、借用栈副本或复制所有权、伪代码/状态转换及原指令证据。若没有队列或合并，按实际结构纠正任务术语而不造队列；如果消费为另一个独立业务，恢复到精确合同/入口并列断边，不无限扩成最终DMA/LCD完成。来源未知不排除，若已认证开源则记录来源版本/修改边界；已有数学/复制/allocator可作明确合同。独立相称静态验证，事实推断未知、来源与一个后继闭包。排除物理显示、设备/固件执行、异常区域/漏洞测试、外连、历史回放、正式ROM生产模型修改；共同规则适用。


## 当前完整任务书 E04（已启动，基线85c61e2）

任务ID E04，新agent独立复核E03真实CTK callback→栈dst→主消费闭包。分支codex/re-0041-e04；worktree D:/CodexHome/visualizations/2026/10/23/01a1691a-e178-7710-86c0-84c2ff2d3dfb/re0041-e04；基线含E03最新管理提交。独占reverse/reports/ap01/ctk-view-review-e04-0041-20261023.md及reverse/analysis/ctk-view-review-e04-0041-20261023/。

问题：注册a005d142参数a00adabc，经a005d146/14a调用a01b28ce挂到62fcb530，是否真连接a00a389c→a00adabc→a00f4740→port1主要dst消费？入口E03正式报告/约9核心清单及E01/E02合同，已知真实调用点a00ae238/a00aef62/a00af17c，必要消费者a00f44e8/a00f4610/a00ef2da，具体功能以正式交付为准。重点端口来源、s0-0x94的0x52B栈view/0x100B帧、返回0跳消费、port1与port2复用、4槽/标签/SOC消费、f44e8第4参a3总数量、dst不逃逸及间接callback ABI。E02已验收转换/五嵌套资源只针对核，不重做cmd50/51/52。

逐项接受纠正未核，独立原指令/厂商字/宽度符号/返回覆盖/循环重读和必要伪代码布局状态所有权，事实推断未知、来源、实际静态验证与断边。纠正只独占报告不改E03。页面/订阅最终清理、其他端口分支/+34/+38及全局deinit保持原边界，不扩完整CTK页面或所有通知。来源未认证不排除，formatter/已验收转换/allocator可留明确合同。禁止固件执行/外连/漏洞/异常输入/历史回放/ROM生产模型修改；共同规则适用。


## H03实际离页删除恢复与H04复核补位

H03 beeca33→2ac1fd0待H04独立技术复核。管理范围/差异/JSON/本地链接通过，原树已确认干净，提交整合、分支保留；H04从2ac1fd0新树新agent启动。ctx116B最终free未证，不能因父state8B或wrapper20B归还而认证ctx销毁。

## 当前完整任务书 H03（已启动，基线dcc2a08）

任务ID H03，业务恢复type0x19天气页context最终所有权和离页删除触发闭包。分支codex/re-0041-h03；worktree D:/CodexHome/visualizations/2026/10/23/01a1691a-e178-7710-86c0-84c2ff2d3dfb/re0041-h03；基线含H02最新管理提交。独占reverse/reports/ap01/weather-page-close-h03-0041-20261023.md及reverse/analysis/weather-page-close-h03-0041-20261023/。

业务问题：a00b821e构造分配的0x74B context由谁持有和最终归还，上层正常导航/离页如何把0x29 DELETE事件交给a00b3b26，wrapper清理与控件递归销毁怎样排序？先读H01/H02的真实page/type0x19挂接/删除合同；a00b3b26仅清28word→注销→free(wrapper)→清page+10，不能假装已释放context。沿一个实际离页调用者/事件分发→删除回调→context引用归还或未归还边组成约5–12函数小闭包；真实ctx释放者尚未知，需据原指令查，不能凭类型名称拼造。

包含必要导航注册/触发、事件ABI、页面/ctx/wrapper/子控件所有权，既验收天气重排/主要显示/五槽注销只针对核，不重复全天气数据流。若无法证实最终free(ctx)，给明确正常路径、引用搜索边界和精确断边，不扩所有GUI删除、不作缺陷判断。完成需生命周期/状态伪代码结构、原指令/返回/宽度/顺序、事实推断未知、来源、实际静态核验与一个后继闭包。通用事件/allocator库仅来源认证才排除，厂商适配仍恢复。排除全UI/所有导航、固件执行/外连/漏洞/历史回放/正式ROM生产模型修改；共同规则适用。

A20已整合ab67c6f，正式技术裁定为有一处callee/字段谓词纠正后限定接受A19，原add_flag状态门说明以A20为准。旧待正式报告仅为历史记录，本状态覆盖。


## A22验收、D05/F05恢复、G04纠正验收与补位

A22 c32fc41→a295c3a限定接受A21，无实质纠正，补class0公共cache元数据读取；D05 8204cbe→1c79f0d、F05 f699ea0→a1a40f5待D06/F06；G04 926f1a5→7c3a3cf两处事件机器表达纠正后限定接受G03（filter仅清bit15，bit0按检查位置不同返回），主提交消费合同接受。四项管理范围/差异/JSON/链接通过，旧树均干净，成果已整合，保留分支。A23/D06/F06/G05从各自最新管理提交新树新agent补位。

## 当前完整任务书 D05（已启动，基线59d81c2）

任务ID D05，业务恢复UART TX ring启动→正常完成callback→tail推进/等待者通知。分支codex/re-0041-d05；worktree D:/CodexHome/visualizations/2026/10/23/01a1691a-e178-7710-86c0-84c2ff2d3dfb/re0041-d05；基线含D04最新管理提交。独占reverse/reports/ap01/uart-ring-drain-d05-0041-20261023.md及reverse/analysis/uart-ring-drain-d05-0041-20261023/。

业务问题：D03已恢复a002c206把frame byte同步放dev TX ring；从a001a70a(dev)传输启动，哪个正常完成callback推进dev+0x50/+0x52 head/tail、何时使等待write继续，缓冲所有权/忙标志及唤醒怎样衔接？先读D03/D04，D04的optional_mark分支纠正为既有合同，不重复文件页表/引用/帧编码。具体DMA/中断callback身份与安装者目前未知，执行agent从实际lower表/初始化和a001a70a直接依赖定位，约5–12函数组成启动→完成→归还/唤醒闭包，只此TX ring不扩全UART或DMA框架。

完成需原指令调用/间接ABI、head/tail宽度/重读/截断、分段/回绕、计数与状态发布顺序、资源持有、正常返回/清理/唤醒、伪代码布局状态和所有权。硬件最终发出无运行证据，不能由回调命名证明对端交付；无法定位真实安装给候选/精确断边，不连接设备验证。不做异常/超时/长度审计或缺陷。来源只有可核实版本/未修改比对才能排除，厂商适配保持恢复。事实推断未知、实际静态验证及一个后继闭包；禁止固件执行/外连/历史回放/ROM生产模型修改；共同规则适用。


## 当前完整任务书 F05（已启动，基线3aba13a）

任务ID F05，业务恢复a0081554对象来源→obj+0x2b8安装→实际返回后callback及loop连接。分支codex/re-0041-f05；worktree D:/CodexHome/visualizations/2026/10/23/01a1691a-e178-7710-86c0-84c2ff2d3dfb/re0041-f05；基线含F04最新管理提交。独占reverse/reports/ap01/miio-exit-callback-f05-0041-20261023.md及reverse/analysis/miio-exit-callback-f05-0041-20261023/。

问题：a005cc1e调用容器a005cec6返回后，将s0-314内容交给a0081554；a00815f4读取obj+2b8间接callback，这个对象/回调由谁安装、参数与资源归还合同是什么、是否实际触及本loop(s0-240)/timer9428或其data？F03/F04明确这只是精确断边，不能预命名walker。沿其对象创建/字段安装→正常消费→回调/释放形成约5–12核心函数，必要短依赖允许，若回调是另一业务且无loop连接，按实际命名并结束在有证据边，不扩大全MiIO或全进程退出。

已验收type13关闭/摘链/callback合同只针对核，避免重复timer扫描；未知间接目标保留候选和有界引用搜索，不凭日志/名字补清理。完成原指令/地址/ABI/写宽/返回覆盖、伪代码结构状态所有权、事实推断未知、来源、实际静态验证和一个后继闭包。普通库认证来源版本才可排除，厂商注册适配继续恢复；排除全loop/heap、漏洞/异常输入、固件执行/外连/历史回放/ROM生产模型修改；共同规则适用。

最新：E03 b0c4ea8→85c61e2待E04；F04 1a100d8→3aba13a通过限定复核。D04已报告D03 optional_mark非空分支伪代码需纠正；实际acquire参数a3=0主链未受影响，正式报告待提交，不冒称无纠正接受。


## 当前完整任务书 G04（已启动，基线f82380b）

任务ID G04，新agent独立复核G03失效提交/记录合并/直接消费完整闭包。分支codex/re-0041-g04；worktree D:/CodexHome/visualizations/2026/10/23/01a1691a-e178-7710-86c0-84c2ff2d3dfb/re0041-g04；基线含G03最新管理提交。独占reverse/reports/ap01/invalidation-submit-review-g04-0041-20261023.md及reverse/analysis/invalidation-submit-review-g04-0041-20261023/。

业务问题：a00ddbf6成功后段a00ddc7e怎样把区域写入display内嵌记录、何时事件门控/省略/退化全屏，a00e0ac8怎样合并、消费并清空？按G03正式核心清单约5–12函数及必要短依赖，已验收C22/G02数学/门控只针对核。已定位display+44的32×16B记录、+244的32B标记、+264的word count，a00e0ac8消费者/a00e082e边界。重点无动态节点队列、mode2全屏置1、普通event35恰1门及调用后重读count、完全包含省略、满32回退、event38(param0)、unsigned低32位面积和严格小于合并、标记顺序、mode1借记录与mode0栈分行、最后512B→32B→count0清理原序。

独立核原字节/厂商字、宽度符号/返回/ABI/原调用重读、记录与栈指针所有权。逐项接受纠正未核，必要纠正仅独占报告不改G03。事件callback未知可能持有param、a00e082e后具体绘制与物理完成保留断边，不追完整绘制/事件注册后继。交付可读伪代码结构状态生命周期、事实推断未知、来源、实际独立静态核验及一个后继闭包；标准库来源未认证不排除，已验收复制/面积/allocator可作明确合同。排除异常区域/漏洞/固件执行/外连/历史回放/ROM生产模型修改；共同规则适用。


## 当前完整任务书 A22（已启动，基线875f762）

任务ID A22，新agent独立复核A21 PNG decoder注册/info/注销条件闭包。分支codex/re-0041-a22；worktree D:/CodexHome/visualizations/2026/10/23/01a1691a-e178-7710-86c0-84c2ff2d3dfb/re0041-a22；基线含A21最新管理提交。独占reverse/reports/ap01/png-info-review-a22-0041-20261023.md及reverse/analysis/png-info-review-a22-0041-20261023/。

问题：a008e3ac初始化片段→a0082914创建/registry插入→a0082c8c class0匹配a00eb6fe PNG info→descriptor/header输出→registry deinit回收是否可由真实注册写入/间接ABI连接？具体核心以A21正式清单为准约5–12函数。已知registry base62fc957c、+110 payload28B、+114/+118 head/tail；创建36B头插、PNG最后注册优先BIN；a008e82c创建/a008e838写callback，close字段真实地址a00eab9a，不能沿用A21早期临时误报a00eb39a；deinit a008be06在a008bed2清registry。重点PNG signature实际data前8B与data+10取低16位宽高、format0x10/返回1、info只借decoder、list unlink/free、构造/注销所有权及顺序，header认证不等于像素/物理绘制执行。

独立原指令/厂商字/函数边界/间接ABI/返回覆盖/资源宽度、逐项接受纠正未核，必要纠正只独占报告不改A21；source classifier/image setter及A20纠正后的flag合同仅针对核，不重复整个image链。完整open/decode/压缩算法、其他格式、动态注册全集及最终显示保留边界，不扩完整图像库。来源版本可核实才排除标准实现，厂商注册适配恢复。交付伪代码结构状态所有权、事实推断未知、来源、实际独立静态验证和断边；排除固件执行/外连/漏洞/畸形输入/历史回放/ROM生产模型修改；共同规则适用。

D04正式报告已整合59d81c2：D03 helper optional_mark非NULL分支以D04纠正为准，正常acquire a3=0闭包限定接受。E04运行中报告port1/port2栈复用措辞需收紧：同布局不等于同次通知执行两支，待正式报告提交。


## E05局部恢复、H04验收、F06纠正验收与补位

E05 5fb2b32→26fc8d7局部生命周期/精确注销断边待E06，未称完整app退出；H04 3e6ebce→8a7807e限定接受H03、ctx最终free仍未证；F06 964d999→f22ec27一处filter mask纠正后限定接受F05，filter29主链不变。管理范围/差异/JSON/链接通过，原树均干净且成果已整合，保留分支。E06/H05/F07从各自最新管理提交新树新agent启动。H04建议a00b8818的C+54派生别名为后续候选，本轮H05改选未覆盖订阅者，不重复原ctx检索。

## 当前完整任务书 E05（已启动，基线f31a27a）

任务ID E05，业务恢复CTK app订阅与正常离页注销/对象归还闭包。分支codex/re-0041-e05；worktree D:/CodexHome/visualizations/2026/10/23/01a1691a-e178-7710-86c0-84c2ff2d3dfb/re0041-e05；基线含E04最新管理提交。独占reverse/reports/ap01/ctk-app-close-e05-0041-20261023.md及reverse/analysis/ctk-app-close-e05-0041-20261023/。

业务问题：a005d142注册的a00adabc(app,item)与app由谁持有、正常退出如何停止回调/注销62fcb530节点、先后归还哪些app/page资源？先读E03/E04已验收注册/触发/栈消费链，E04对port1/port2互斥与栈布局措辞纠正须沿用。选择一个实际app退出/DELETE触发者→注销→节点/app清理闭包，约5–12核心和必要短依赖；具体退出callback/注销器地址目前未知，须据注册caller、app挂接和保留incoming refs定位，不凭同名GUI函数拼链。

包含真实callback键/userdata、注销是否仅摘链或还free、app/页面/上下文分配与清理顺序、回调期间可达性；不重复a00f4740内部或port1数值显示，既有订阅链/allocator合同针对核。未能证明节点回收/退出触发时给有界检索与精确断边，不把注销等同释放，不扩大所有UI/所有订阅者/全局deinit。完成伪代码结构状态生命周期、原指令/地址/ABI/写宽/返回覆盖、事实推断未知、来源、实际静态验证和一个后继闭包。来源未认证不排除标准实现/厂商修改。禁止固件执行/外连/漏洞/异常/历史回放/ROM生产模型修改；共同规则适用。


## 当前完整任务书 H04（已启动，基线2ac1fd0）

任务ID H04，新agent独立复核H03真实按键离页→父/子DELETE→递归析构与context断边闭包。分支codex/re-0041-h04；worktree D:/CodexHome/visualizations/2026/10/23/01a1691a-e178-7710-86c0-84c2ff2d3dfb/re0041-h04；基线含H03最新管理提交。独占reverse/reports/ap01/weather-page-close-review-h04-0041-20261023.md及reverse/analysis/weather-page-close-review-h04-0041-20261023/。

问题：a00afc88天气子页创建片段及8B父state(type19)→输入hook a00b35ee event11/key10/窗口64零门→恢复主页面/删除a00ded6c(window)→父DELETE a00b1a02→子天气DELETE a00b3b26→控件递归/类析构摘链free的原序与所有权是否成立？核心以H03正式清单约5–12函数为准，只核该正常type19路径，不复核全GUI删除系统。已验收H02子hook/重排/注销只针对核。重点父8B state、20B wrapper、116B ctx三者区分，父stop timer/free state与子清28word/unregister/free wrapper排序、事件mask/vendor条件/返回门、对象递归/类析构前后指针持有及ctx最终free未证的有界范围。

独立原指令/厂商字/事件ABI/宽度/调用重读/失败分支，逐项接受纠正未核；必要纠正仅独占报告不改H03。不要把构造直接引用搜索变穷尽别名、不要把对象free拼成ctx free、不引入缺陷判断。交付伪代码布局状态生命周期、事实推断未知、来源、实际独立静态验证和断边；标准库仅来源认证可排除，私有胶合保留恢复。排除全导航/其他窗口类型、固件执行/外连/漏洞/异常/历史回放/ROM生产模型修改；共同规则适用。

最新整合：E04→f31a27a范围措辞纠正后限定接受E03；A21→875f762、G03→f82380b为待独立复核恢复，A22/G04运行中。


## 当前完整任务书 F06（已启动，基线a1a40f5）

任务ID F06，新agent独立复核F05显示对象来源/DELETE清理与可选callback断边闭包。分支codex/re-0041-f06；worktree D:/CodexHome/visualizations/2026/10/23/01a1691a-e178-7710-86c0-84c2ff2d3dfb/re0041-f06；基线含F05最新管理提交。独占reverse/reports/ap01/display-exit-review-f06-0041-20261023.md及reverse/analysis/display-exit-review-f06-0041-20261023/。

问题：a005ccc6→a0084b96→a008aec0分配zero324对象/58B payload→a00873ea写out，配置/dev/fb0与/dev/input0，是否确为返回后a0081554显示清理对象，而不是loop walker？真实DELETE注册a0086cd4→a007ffa0→a01b93b4(obj+2e8 event list,cb=a00800b4,filter29,userdata=obj)及a008acfa分发event+c userdata→callback后端归还→后续可选obj+2b8/payload/obj清理顺序是否成立？按F05正式约5–12核心与必要片段；F03/F04栈loop/关闭合同只针对核，不重新扫timer。

重点+2b8仅可证构造zero初值，非NULL安装/真实callback未定位，普通SW立即数有界搜索不涵盖别名/批量/厂商store，不能推返回时必NULL；backend=obj+2e0清理、fd>=0 close wrapper/free backend+34/backend与对象资源顺序、callback返回后字段重读须原指令核。显示闭包无已证loop9428连接但opaque callee不能作全局否定。独立核ABI/厂商字/写宽/返回分支/所有权，逐项接受纠正未核，纠正只独占报告不改F05。不扩全部显示/输入或obj+2b8后继恢复，保留来源认证和上层loop断边。交付必要伪代码结构状态生命周期、事实推断未知、来源、实际静态验证与一个后继闭包；禁止固件执行/外连/漏洞/异常/历史回放/ROM生产模型修改；共同规则适用。

H03已整合2ac1fd0待H04。G04正在独立复核，报告G03 filter机器表达及不同bit0检查位置需精确纠正/补充，正式报告待提交，不提前标无纠正接受。


## E06验收、D06纠正、A23/G05恢复及补位

E06 b5e53e4→0724167限定接受E05局部合同、完整退出注销仍未闭合。D06 27816f6→e8ce444型号发布次数纠正后限定接受D05并补DMA IRQ trampoline/pair ABI，已知ttyS1 type1主合同不变。A23 be2d913→5e0da7b待A24；G05 02c30d3→a6a4e7c待G06。四项管理范围/差异/JSON/报告链接通过，旧树均干净，成果已整合、分支保留；E07/D07/A24/G06新树新agent从对应最新管理提交补位。

## 当前完整任务书 A23（已启动，基线a295c3a）

任务ID A23，业务恢复PNG class0 open→decoder-session资源→已注册close归还闭包。分支codex/re-0041-a23；worktree D:/CodexHome/visualizations/2026/10/23/01a1691a-e178-7710-86c0-84c2ff2d3dfb/re0041-a23；基线含A22最新管理提交。独占reverse/reports/ap01/png-session-lifecycle-a23-0041-20261023.md及reverse/analysis/png-session-lifecycle-a23-0041-20261023/。

业务问题：A21/A22已确认open a00eb7b6、close a00eab9a真实注册；正常class0 ROM源怎样进入open、分配/保存像素或user_data、由谁持有decoder-session、close如何归还，成功与失败清理分支怎样保持原行为？从真实open调用/注册ABI和该class0分支出发，只展开session创建/像素对象持有/转换或包装/close及必要直接依赖，约5–12核心；底层通用解压/PNG算法可先作为明确调用合同，但来源未认证仍保留未恢复/未认证记录，不能静默排除。

既验收registry/info/header和A20状态门只针对核，不重复整个image setter、其他image class或完整压缩算法。对象/内存分配/所有权、decoded指针与src借用、返回值和清理顺序、间接open/close ABI必须原字节核，失败分支不能擅自修正，不做错误输入测试。若session owner或最终close调用者未连上，列实际字段/调用入口与精确断边，不以注册存在推成功执行。交付伪代码结构状态生命周期、原指令证据/厂商字/宽度、事实推断未知、来源、实际静态验证和一个后继闭包。排除像素执行/渲染观察、固件执行/外连/漏洞/历史回放、ROM生产模型修改；共同规则适用。


## 当前完整任务书 G05（已启动，基线7c3a3cf）

任务ID G05，业务恢复display事件35/38 descriptor注册→callback/param消费→刷新调度通知闭包。分支codex/re-0041-g05；worktree D:/CodexHome/visualizations/2026/10/23/01a1691a-e178-7710-86c0-84c2ff2d3dfb/re0041-g05；基线含G04最新管理提交。独占reverse/reports/ap01/display-event-flow-g05-0041-20261023.md及reverse/analysis/display-event-flow-g05-0041-20261023/。

业务问题：G03提交过程借用clipped栈矩形发0x35，新增记录后发0x38 param0，display+2e8的事件descriptor由谁安装、真实callback怎样读/改/保存param及0x38如何触发a00e0ac8消费者？入口G03/G04合同、a00814f4、a008ad80..ad98过滤/userdata/callback(event*)、提交a00ddd90/ddd76和event timer消费者a00e0ac8。安装callback身份/调度连接当前未知，须先定位真实descriptor写入及参数，不猜timer回调，不把event38默认当唤醒。

范围约5–12核心及必要短依赖，选择同一display正常注册/回调/直接调度消费小闭包，明确callback同步返回/bit0/bit1归一门、param持有/复制、生命周期与注销；已验收区域记录合并/复位只针对核，不重做全部数学。若多个独立callback并存，选实际必要目标，其他列候选/断边，不接管整个GUI事件系统或最终绘制。完成原字节/间接ABI/厂商字/宽度返回/顺序、伪代码结构状态与所有权、事实推断未知、来源、实际静态验证和一个后继闭包。来源未认证不排除，标准list/timer合同可保留并说明认证缺口。排除物理刷新/DMA/LCD、异常param/漏洞、固件执行/外连/历史回放、ROM生产模型修改；共同规则适用。


## 当前完整任务书 D06（已启动，基线1c79f0d）

任务ID D06，新agent独立复核D05 UART TX ring实际IRQ主路径与条件DMA的消费/通知闭包。分支codex/re-0041-d06；worktree D:/CodexHome/visualizations/2026/10/23/01a1691a-e178-7710-86c0-84c2ff2d3dfb/re0041-d06；基线含D05最新管理提交。独占reverse/reports/ap01/uart-ring-review-d06-0041-20261023.md及reverse/analysis/uart-ring-review-d06-0041-20261023/。

业务问题：已知设备private+e初值0怎样使a001a70a DMA入口早退，而真实open的lower+8→a001a1d8安装IRQ3d/a0019ae0(dev)，common dispatcher a0001012..1046把arg装a2，status门→a002d36a消费ring→tail/等待者通知，条件+e非零又怎样经DMA安装/回调归还？按D05正式核心清单，约5–12核心及必要短IRQ/安装片段；重点私有初值与运行时写者未知的区别，不把初值当永恒配置、不省实际IRQ以DMA替代。

原指令独立核halfword tail先发布再读取ring及按值lower发送、回绕/重读、lower+48=0/ready恒1的条件、空环txint0、有进度a002be92先poll通知再唤醒dev+18；条件DMA lower+20=a001a240、a001a3f6..a400注册a0019d9a/a00264ec、dev+88累计与a002d5d8清+88/+84/+80后的通知，具体边以最终报告为准。先发布tail不等同硬件发送完成。已验收D04 source复制/引用和帧队列只针对核，厂商字/间接ABI/写宽符号/返回覆盖须原编码核。

逐项接受纠正未核，必要纠正只独占报告不改D05；保留动态private/ops写者、完整中断优先级/硬件交付、final close及未解同步内部断边，不扩全IRQ/DMA/UART或异常超时。交付伪代码结构状态生命周期、事实推断未知、来源、实际独立静态验证及一个后继闭包。来源未认证不排除。禁止固件执行/设备/外连/漏洞/历史回放/ROM生产模型修改；共同规则适用。



## 当前完整任务书 E06（已启动，基线26fc8d7）

任务ID E06，新agent独立复核E05 CTK app所有权/DELETE清理与注销断边闭包。分支codex/re-0041-e06；worktree D:/CodexHome/visualizations/2026/10/23/01a1691a-e178-7710-86c0-84c2ff2d3dfb/re0041-e06；基线含E05最新管理提交。独占reverse/reports/ap01/ctk-app-close-review-e06-0041-20261023.md及reverse/analysis/ctk-app-close-review-e06-0041-20261023/。

问题：a00b2f6c创建0x68B app window、parent child array持有、app+10单独8B state；62fc95bc实际为独立组/输入关联句柄而非app根，app+2c/+30分别保存旧/新句柄、a005d142注册a00adabc，以及DELETE a00ab8ec的1s timer删除/free state/清挂接，是否符合原字节和生命周期？核心以E05正式约5–12函数清单/必要片段为准，E04数据消费与互斥谓词只针对核。重点真实DELETE注册参数/timer userdata/实际free、window析构及公共删除原序、同头62fcb530的a00f2f98内联移除器固定键a00f5288与a00adabc不能混同、a0089d02仅摘链不free的证据与有界搜索范围。

逐项接受纠正未核，原指令/间接ABI/厂商字/宽度/返回与重读、伪代码结构状态所有权，事实推断未知/来源/实际独立静态验证/精确断边。真实a00adabc注销、订阅节点回收、app root正常退出触发未证须保留；不能将window对象free或另一个callback移除拼成此订阅销毁。必要纠正只独占报告不改E05，不接管root删除incoming或全registry teardown后继，不扩全UI。来源未认证不排除；禁止固件执行/外连/漏洞/异常/历史回放/ROM生产模型修改；共同规则适用。


## 成果复用调整前任务书归档

## 当前完整任务书 H05（已启动，基线8a7807e）

任务ID H05，业务恢复另一个未覆盖天气订阅点a005e8dc的注册→callback主要消费→页面/对象退出闭包。分支codex/re-0041-h05；worktree D:/CodexHome/visualizations/2026/10/23/01a1691a-e178-7710-86c0-84c2ff2d3dfb/re0041-h05；基线含H04最新管理提交。独占reverse/reports/ap01/weather-subscriber-h05-0041-20261023.md及reverse/analysis/weather-subscriber-h05-0041-20261023/。

问题：五槽注册器a00b3a68既有incoming ref之一a005e8dc对应哪一个真实调用者、callback/userdata、它怎样消费天气字段/触发显示或业务状态、何时注销/对象归还？准确包含函数/callback和退出入口当前未知；a005e8dc是调用点不是函数入口。先核已有A15/H01及后续报告是否已恢复此点，若已覆盖则给证据报告管理者，不擅自领取其他独立业务。以一个真实订阅者注册/主要callback分支/直接字段消费者/注销或清理形成约5–12核心，不重做既验收五槽分发、arc/图标/PNG info与H03页面删除全套证据。

保留callback(data,userdata)顺序、原宽度符号/重读/返回门、借用与复制、注册/注销键和资源持有；不能把清字段/摘链/删除widget等同释放ctx。未定位退出时给精确字段/入口与有界搜索，不重复H03 ctx free检索，不扩所有天气订阅者/全UI或网络。交付原指令/证据、可读伪代码布局状态生命周期、事实推断未知、来源、实际静态验证及一个后继闭包。源码来源未认证不排除，标准调用保留明确合同。禁止固件执行/外连/漏洞/异常/历史回放/ROM生产模型修改；共同规则适用。

最新整合：A22→a295c3a限定验收；G04→7c3a3cf两处事件表达纠正后限定验收；D05→1c79f0d与F05→a1a40f5待D06/F06。F06运行中已报告F05通用filter描述也需按mask ffff7fff收紧，正式报告待提交。E05作者已纠正即时摘要中62fc95bc身份，正式报告待交付；不得当app根引用。

## 当前完整任务书 F07（已启动，基线f22ec27）

任务ID F07，技术来源认证：F05显示对象/DELETE后端闭包与本地LVGL候选源码的可核实匹配及厂商差异。分支codex/re-0041-f07；worktree D:/CodexHome/visualizations/2026/10/23/01a1691a-e178-7710-86c0-84c2ff2d3dfb/re0041-f07；基线含F06最新管理提交。独占reverse/reports/ap01/display-source-auth-f07-0041-20261023.md及reverse/analysis/display-source-auth-f07-0041-20261023/。

问题：此前按来源未知恢复的显示create/delete/list/event/backend适配约5–12函数，哪些可与本地可核实上游源码一致识别，哪些存在厂商包装/修改/配置差异，哪些仍不能排除？入口F05/F06正式核心表、ROM路径lv_display.c/lv_nuttx_entry.c、0041-handoff.md中本地候选根。已知本地WSL Ubuntu-24.04根/home/slepher/nuttx-ap01-sim，历史报告候选NuttX12.10/LVGL9.2.1，apps固定提交8ff533beb37eeef1f288c467acd7c50b542464eb；这只是本地SIM候选，绝不是ROM准确版本。先在该明确根内只读定位实际LVGL源码/版本元数据（可经WSL本地文件路径），不可启动SIM/QEMU/固件、构建、网络或下载，不改候选树。不存在或不可读则记录实际界限，不另装软件/修复权限/全盘扫库。

以F05显示create a0084b96/list a008aec0/publish a00873ea/delete a0081554/事件注册分发/后端DELETE a00800b4等约5–12核心选择完整小功能闭包，已有ROM合同只核来源所需证据，不重做指令全量复制。逐函数比较源码调用顺序、字段布局/编译结构、返回与清理分支、资源所有权、callback ABI及适配路径；记录实际源码绝对路径与Git/版本/包来源依据，不新增哈希清单。仅算法同形/字符串不能认证未修改实现；明确区分候选相符、来源可识别但版本未知、确证未改可排除、厂商修改/封装仍须恢复、未匹配。

不得凭相似性把整LVGL/图像/事件库一并排除，不例行重扫+2b8普通SW。F06 filter mask纠正为既有合同。交付源-ROM函数映射表、具体匹配/差异证据和未认证边界、事实推断未知、实际只读验证、可复用的认证范围与一个后继闭包；不写参考实现、不编译或修原程序。仅静态、不外连/漏洞/历史回放/ROM生产模型修改；共同规则适用。

## 当前完整任务书 A24（已启动，基线5e0da7b）

任务ID A24，新agent独立复核A23 PNG真实session owner/open/close/缓存持有转移闭包。分支codex/re-0041-a24；worktree D:/CodexHome/visualizations/2026/10/23/01a1691a-e178-7710-86c0-84c2ff2d3dfb/re0041-a24；基线含A23最新管理提交。独占reverse/reports/ap01/png-session-review-a24-0041-20261023.md及reverse/analysis/png-session-review-a24-0041-20261023/。

问题：a00e5c78的s0-7c 76B栈session→a00e5d32/a019b168 open清session/cache miss/info/decoder+4→PNG a00eb7b6像素包装/session+2c→a018f9e8消费者→a00e5d8c/a00828d6 close→a00eab9a及cache/非cache归还，是否符合原字节和所有权？核心以A23正式清单约5–12函数及必要短依赖，已验收A22 registry/info/header只针对核，不重做全PNG或像素压缩算法。重点严格1门、src借用/像素byte0/2交换、normal options+4/+5零使a00829e4对象直返、非cache a0081f26先可选handler+4(raw+14)再free、cache启用PNG close跳过销毁/session仅a019d9f6 release、初始化a008abb0 payload清理与驱逐/引用内部断边，不能把release称实际像素free。

独立原指令/ABI/厂商字/宽度/重读/返回覆盖及失败清理原序，逐项接受纠正未核，必要纠正只独占报告不改A23。通用解压算法保留明示未恢复/来源未认证合同，实际cache驱逐与像素handler安装未解精确保留，不扩全部cache/图像/物理绘制。交付伪代码结构状态生命周期、事实推断未知、来源、实际独立静态验证和一个后继闭包。禁止固件执行/外连/漏洞/错误输入/历史回放/ROM生产模型修改；共同规则适用。

最新：E05→26fc8d7待E06且仅部分生命周期；H04→8a7807e限定接受H03；F06→f22ec27 filter表达纠正后接受F05。F07已只读定位本地候选实际路径/home/slepher/nuttx-ap01-sim/apps/graphics/lvgl/lvgl（lv_display.c/lv_version.h），尚未认证ROM来源/排除；未启动SIM或构建联网。

## 当前完整任务书 D07（已启动，基线e8ce444）

任务ID D07，业务恢复D05条件DMA实际提交者a01b554e的本地描述符/缓冲持有→配置启动→归还连接小闭包。分支codex/re-0041-d07；worktree D:/CodexHome/visualizations/2026/10/23/01a1691a-e178-7710-86c0-84c2ff2d3dfb/re0041-d07；基线含D06最新管理提交。独占reverse/reports/ap01/uart-dma-descriptor-d07-0041-20261023.md及reverse/analysis/uart-dma-descriptor-d07-0041-20261023/。

业务问题：条件+e非零时UART TX怎样把ring一/两段地址/长度交a01b554e，本地DMA描述符谁分配/填充/持有、channel参数与callback对保存地址的依赖、正常完成后何时可复用/归还？具体核心从D05/D06真实a001a240提交和a01b554e直接依赖定位，约5–12函数及必要短配置/回调片段，只此UART TX调用，不接管所有DMA channel/RX框架。D06对型号分支dev+88发布次数和IRQ trampoline/pair安装的纠正作为既有合同；IRQ初始主路径不重做，不把条件DMA当默认。

原指令核descriptor布局/宽度符号/传参/发布顺序、cache维护调用边、buffer指针持有与复制、busy/phase及正常返回/清理；a0019d9a→a002d5d8归还合同针对核，不无限追硬件运行。若存在本地官方SDK候选可只读对照D:/Documents/PlatformIO/Projects/bouffalo_sdk（已有交接固定41bf338a57be53919d99f6c6715a96100428c97d），来源版本/芯片适配须核实，不下载不构建不默认与ROM相同。已认证标准实现才排除，厂商封装继续恢复。交付伪代码结构状态所有权、原字节/厂商编码/间接ABI、事实推断未知、来源、实际静态验证与精确断边及一个后继闭包。禁止设备/固件执行、外连、异常/超时/漏洞、历史回放、ROM生产模型修改；共同规则适用。

## 当前完整任务书 E07（已启动，基线0724167）

任务ID E07，业务恢复CTK剩余item+0x34/+0x38扩展字段的一条实际数值消费闭包。分支codex/re-0041-e07；worktree D:/CodexHome/visualizations/2026/10/23/01a1691a-e178-7710-86c0-84c2ff2d3dfb/re0041-e07；基线含E06最新管理提交。独占reverse/reports/ap01/ctk-extra-consumers-e07-0041-20261023.md及reverse/analysis/ctk-extra-consumers-e07-0041-20261023/。

问题：E01/E02已核此两字段创建/响应覆盖/通知/清零释放，但真正页面/业务数值消费者仍未解；它们由谁读取、如何转换/触发更新和保持借用寿命？以一条真实call/data链从cmd52生产/通知合同→一个实际消费者/必要注册→主要数值下游→复用/清理范围组成约5–12函数，若两字段属于同一小数据族可一并恢复，否则选一条并列另一独立后继，不扩全CTK页。入口E01/E02五字段布局/日志、a00a8582 cmd52片段、item查找a00a53c0与item通知a00a389c、已有whole-ROM retained consumer/call索引；a00f4740只读前3组，不能将它当这两组已解消费者。

先核既有E03/E04/E05/E06并避免重复port1栈view或root DELETE负搜索。生产/清理已验收部分只针对核，核心工作是定位新实际读者、结构/数值宽度符号/索引/掩码/返回分支、借用与复制、主要下游调用ABI及正常生命周期。未定位实际读者时给精确引用界限与候选断边，不用单helper冒充完成、不扩全ROM泛扫。字段业务名须有日志/用途依据，未知不猜。交付原指令/伪代码结构状态所有权、事实推断未知、来源、实际静态验证和一个后继闭包。来源未认证不排除；禁止固件执行/外连/漏洞/异常/历史回放/ROM生产模型修改；共同规则适用。

## 当前完整任务书 G06（已启动，基线a6a4e7c）

任务ID G06，新agent独立复核G05 display真实event38安装→timer resume/通知→调度与poll门→区域消费者闭包。分支codex/re-0041-g06；worktree D:/CodexHome/visualizations/2026/10/23/01a1691a-e178-7710-86c0-84c2ff2d3dfb/re0041-g06；基线含G05最新管理提交。独占reverse/reports/ap01/display-event-review-g06-0041-20261023.md及reverse/analysis/display-event-review-g06-0041-20261023/。

问题：a0086bba向同display+2e8安装callback a0080002/filter38/userdata0、timer a0084ee2(a00e0ac8,16,display)后在a00873b6..be改+8为a0080da6，event38怎样通过display+308/a008bd70清timer+14 bit0/a0087b06通知，在a00804e2 elapsed>=period且repeat非零后间接timer*调用，再由poll非负/revents4门控a00e0ac8？具体核心按G05正式约12合同/必要片段，G04 mask/bit0返回纠正与记录消费只针对核。

重点同display对象关系/真实注册字段和间接ABI、timer16实际单位合同、resume不是立即绘制、callback只读event+8/+4且不读/改/保存param/flags、内建filter38/29对event35不匹配但不能否定动态35/ALL handler、创建/替换/删除资源原序及notifier+9c实际安装断边。a008335e删除同timer并装a00806f8/filter38/userdata=&state+58为替代链候选，保持未知不接管其恢复。独立原字节/厂商编码/宽度/返回重读/所有权，逐项接受纠正未核，纠正只独占报告不改G05。交付伪代码结构状态生命周期、事实推断未知、来源、实际独立静态验证及一个后继闭包；不扩全GUI事件/全部timer/物理绘制、固件执行/外连/漏洞/异常/历史回放/ROM生产模型修改；共同规则适用。

最新整合：E06→0724167局部验收；D06→e8ce444发布次数纠正+DMA IRQ精确ABI后验收；A23→5e0da7b/G05→a6a4e7c待A24/G06。A24运行中发现A23对齐data回调全局槽应为62fc964c而非handler表+8，正式报告待提交。


整合：A25→3ed71d2；D08→26f1f4f；E07→bcfcb63；F08→3569ab7；G06→6c11f60/064320f；H06→7a8f3bc/52e61b9。复核不重复记新增。


## 当前完整任务书 E08（已启动，基线fca1d5e）

问题：独立复核E07边界与增量口径。

继承charge-complete records[8]/[9]/[19]、round4及E07复用对照。只复核a00a1aa8→a00a53c0不能归属最近a00a12d0 retained body的证据，以及14 getter/3注册候选有界检索能支持的结论。未找到item+34/+38读者不能宣称恢复。不要重扫CTK/全部消费者；已有充分证据可短报告结束，新增功能0。

分支codex/re-0041-e08；worktree D:/CodexHome/visualizations/2026/10/23/01a1691a-e178-7710-86c0-84c2ff2d3dfb/re0041-e08。基线为本任务书提交（启动时最新整合提交，另记实际SHA）。独占reverse/reports/ap01/ctk-extra-review-e08-0041-20261023.md及reverse/analysis/ctk-extra-review-e08-0041-20261023/。

先交简短复用/精确缺口对照，按共同规则仅做必要静态验证。完成标准为回答本题或保留有界、可定位断边；无增量即报告已覆盖，禁止凑闭包扩扫。提交独占成果、报告验证/未知/clean后结束，不创建下级agent。技术纠正只写独占报告不改原成果。

E08 208dcc7→08dfc7c：限定接受E07候选/retained body结论，真实函数归属未知；新增功能0。


## 当前完整任务书 A26（已启动，基线fca1d5e）

问题：独立复核A25新增默认内存绑定。

A23/A24、A25及其reuse-crosscheck；旧pass3初始化调用已知。只核a008e3ac实际表写入、a007fe60/a007ff40/a007fe4e raw/free/align ABI、Pixel与raw身份及析构原序。旧PNG合同直接引用，不重导整个函数，不扩heap/cache/动态替换。结果逐项接受/纠正/未核，新增功能记0。

分支codex/re-0041-a26；worktree D:/CodexHome/visualizations/2026/10/23/01a1691a-e178-7710-86c0-84c2ff2d3dfb/re0041-a26。基线为本任务书提交（启动时最新整合提交，另记实际SHA）。独占reverse/reports/ap01/pixel-memory-review-a26-0041-20261023.md及reverse/analysis/pixel-memory-review-a26-0041-20261023/。

先交简短复用/精确缺口对照，按共同规则仅做必要静态验证。完成标准为回答本题或保留有界、可定位断边；无增量即报告已覆盖，禁止凑闭包扩扫。提交独占成果、报告验证/未知/clean后结束，不创建下级agent。技术纠正只写独占报告不改原成果。

71bcb56→872972c：限定接受A25，新增功能0。


## 当前完整任务书 F09（已启动，基线fca1d5e）

问题：event array维护与重入精确断边。

继承F05/F06/G05/G06事件注册/分发合同及F07/F08来源差异。派发后交叉检索确认G03/G04已留ac38/acc6快照清理，G05/G06已恢复dirty/busy、压紧/free及capacity=count+4调用，全部继承。实际范围收缩为a00ecc68容量helper内部owned门、大小计算/realloc/回写/限幅与caller返回消费；只补未解释语义窗口，不再恢复重入/删除，不重导已有原指令。候选源码不能替代ROM事实，20B不是完整list尺寸。

分支codex/re-0041-f09；worktree D:/CodexHome/visualizations/2026/10/23/01a1691a-e178-7710-86c0-84c2ff2d3dfb/re0041-f09。基线为本任务书提交（启动时最新整合提交，另记实际SHA）。独占reverse/reports/ap01/event-array-maintenance-f09-0041-20261023.md及reverse/analysis/event-array-maintenance-f09-0041-20261023/。

先交简短复用/精确缺口对照，按共同规则仅做必要静态验证。完成标准为回答本题或保留有界、可定位断边；无增量即报告已覆盖，禁止凑闭包扩扫。提交独占成果、报告验证/未知/clean后结束，不创建下级agent。技术纠正只写独占报告不改原成果。

f166c84→e0e357d：仅容量helper局部合同，新增业务0，待F10。


## 当前完整任务书 H07（已启动，基线fca1d5e）

问题：type4 weather1正常上层离页到DELETE连接。

继承pass3第2653–2657行注册a00abed2/type4/context/DELETE a00abb62，weather-calendar-complete全部分类文字图标合同及H05/H06。仅补H05明确缺的正常上层离页动作→本页DELETE连接，先查page-logic/knob/system/guide和ZIP现有导航证据，SIM导航不等于ROM连接。目标对象type4/68B；type19/116B不在本题，不套用释放结论。若已有足够证据仅报告覆盖；不得改题为另一个旧订阅者或全UI。

分支codex/re-0041-h07；worktree D:/CodexHome/visualizations/2026/10/23/01a1691a-e178-7710-86c0-84c2ff2d3dfb/re0041-h07。基线为本任务书提交（启动时最新整合提交，另记实际SHA）。独占reverse/reports/ap01/weather1-navigation-h07-0041-20261023.md及reverse/analysis/weather1-navigation-h07-0041-20261023/。

先交简短复用/精确缺口对照，按共同规则仅做必要静态验证。完成标准为回答本题或保留有界、可定位断边；无增量即报告已覆盖，禁止凑闭包扩扫。提交独占成果、报告验证/未知/clean后结束，不创建下级agent。技术纠正只写独占报告不改原成果。

H07 69ee808→89875e2：普通切出旧成果覆盖，新增业务0；实际teardown断边与E05/E06同源，合并归属，不另派天气DELETE负搜索。


## 当前完整任务书 D09（已启动，基线fca1d5e）

问题：channel分配到正常close与槽归还。

D07/D08已覆盖描述符持有/提交/IRQ合同，继承不重做。精确种子a001a8ee→a00288de；旧优先材料按地址检索未命中不等于从未分析，先按调用者/字段别名再核。仅回答本UART路径channel如何分配、callback/pool槽何时解绑归还，正常close实际连接是否可证。硬件行为保留未知，不扩全部DMA/RX。

分支codex/re-0041-d09；worktree D:/CodexHome/visualizations/2026/10/23/01a1691a-e178-7710-86c0-84c2ff2d3dfb/re0041-d09。基线为本任务书提交（启动时最新整合提交，另记实际SHA）。独占reverse/reports/ap01/uart-dma-channel-d09-0041-20261023.md及reverse/analysis/uart-dma-channel-d09-0041-20261023/。

先交简短复用/精确缺口对照，按共同规则仅做必要静态验证。完成标准为回答本题或保留有界、可定位断边；无增量即报告已覆盖，禁止凑闭包扩扫。提交独占成果、报告验证/未知/clean后结束，不创建下级agent。技术纠正只写独占报告不改原成果。

e85bf9a→1b0cd8c：channel busy/最后close增量待D10。


## 当前完整任务书 G07（已启动，基线fca1d5e）

问题：event38替代work调度与状态归还。

继承G05/G06已知主路径和三项纠正，旧system/settings timer/SIM调度不再恢复。派发后交叉检索确认G05已有替代38注册/去重/clear窗口，C03/C04已有a009e4f6→a009f9b6成组初始化/启动合同，全部继承；实际范围收缩为display state+58/+60对象身份、a009f9b6到实际消费及正常归还/退出连接。优先材料按4地址无精确命中仅为检索范围事实，须再核字段/调用者/旧Evidence。未安装的hook不假定已运行，不扩所有poll/event。

分支codex/re-0041-g07；worktree D:/CodexHome/visualizations/2026/10/23/01a1691a-e178-7710-86c0-84c2ff2d3dfb/re0041-g07。基线为本任务书提交（启动时最新整合提交，另记实际SHA）。独占reverse/reports/ap01/display-alternate-work-g07-0041-20261023.md及reverse/analysis/display-alternate-work-g07-0041-20261023/。

先交简短复用/精确缺口对照，按共同规则仅做必要静态验证。完成标准为回答本题或保留有界、可定位断边；无增量即报告已覆盖，禁止凑闭包扩扫。提交独占成果、报告验证/未知/clean后结束，不创建下级agent。技术纠正只写独占报告不改原成果。

0c7abd3→ef1bdf3：poll身份/正常消费及owner归还增量待G08。


## 当前完整任务书 F10（已启动，基线f2d4bc9）

独立树D:/CodexHome/visualizations/2026/10/23/01a1691a-e178-7710-86c0-84c2ff2d3dfb/re0041-f10，分支codex/re-0041-f10；基线为本任务书提交，启动时另记SHA。独占reverse/reports/ap01/event-array-review-f10-0041-20261023.md及reverse/analysis/event-array-review-f10-0041-20261023/。

独立复核F09收缩后的a00ecc68 owned/宽度/返回/字段发布和caller仅测非零合同；G03–G06的重入/删除/压紧全部继承，不再导出。只核F09真正补充的必要原字节与ABI。零返回后的断言是否返回与底层realloc可保留精确未知，不开展异常输入/缺陷研究、不扩失败链或堆。新增功能0；已有证据充分可以短报告。

先交简短已有出处→解释行为→证据局限→实际缺口；只补未覆盖/不可信窗口，重读bytes标旧结论复核。报告分继承、复核纠正、真正新增、未闭精确边。无必要增量即报告覆盖，不凑时长/函数。共同规则全部适用，仅静态/独占输出，无SIM/构建/回放/生产ROM配置模型修改，不创建下级agent。必要验证后提交独占路径，报告commit/未知/clean并结束。

F10 6c61383→2052338：限定接受F09，无语义纠正/新增功能，无必要继续扩扫。
