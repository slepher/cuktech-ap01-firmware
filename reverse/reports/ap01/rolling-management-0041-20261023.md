# 0041 六路滚动管理（2026-10-23恢复）

当前派发指令（2026-10-25）：完成文档后提交，不再派发新工作；此前持续补位要求不再作为新派发依据，恢复须用户另行明确授权。以下五席配置为后续流程设计。

## 2026-10-25 专职整合与工作量准入（文档更新）

后续协作配置为三席执行研究/非作者复核、一席预调研、一席专职整合，共五个子代理；主窗口负责调度、最终范围与争议。整合席经明确交接后是主树、Git整合及唯一认领表的单一写入者；主窗口发送已确认的登记请求，收到认领行与基线后派发，不能同时写主树。未启用整合席时主窗口兼任。此次只更新并提交文档，不启动、唤醒或派发新工作，不执行成果合并、转存或清理；下方历史配置和运行快照不改写。

交付完成消息同时进入预调研补包队列和整合队列，整合不再等待主窗口攒批。分别记录运行状态、技术验收状态与整合状态；已交付但未合并属于“整合待办”，不能称“研究未完成”。中断复核及未提交文件须单列，满足停止、全部commit合并、产物转存核对、tracked/untracked及ignored无遗留后才能清理。整合积压增长时优先恢复整合能力，不继续用新研究堆积任务树。

常规研究包须同时满足完整可用阶段和据近期实测预测20–40分钟真实未闭工作量。此前短helper/回调虽构成小阶段，却多次只需几分钟；仅下调估时而不改变实际范围，不能满足工作量要求。后续合并同接口相关未闭阶段，扣除旧覆盖、已定位材料和公共API止边；不足20分钟且无相关阶段可并的列“短尾待合并”，纳入原任务补充或相关合批复核，不逐段另起作者→复核链。复核按差集单独估时，可短于20分钟，但不充当半小时研究包；提前完成立即交付，不等待凑时长。

预调研保持执行席之外3份可派库存，分别报告常规研究和合批复核数量；短尾、条件模板、待消歧、缺材料不计可派。现有分钟级候选必须重新筛选，不能因已有包名就视为满足研究准入。作者运行时提前备条件复核模板，最终commit、停止和差集确认后才转可派。细则见[统一流程3.2–3.4节](reverse-design.md#32-按约半小时工作量切块按接口交付)及[派发模板](chain-claim-notice-prompt-20261024.md)；认领表仍为本文件原表。

## 2026-10-25 新聊天恢复：三执行＋一预调研

用户明确授权按新流程启动并持续补位。实时代理树初始只有/root，旧R批次运行中快照不代表当前。基线5bbc331ab429fb76e956e50b8081c56f8d278b11；主树全部未提交成果保留。新任务使用独占worktree/分支、本地commit交付、主窗口验收合并，预调研维持3份可派队列并按完成实测调整；不推送，静态限制不变。

预调研认领PREP-S01：/root/task_prep_research_01，底座协议/应用接入本补位批次，独占task-prep-research-01-0041-20261025报告及同名analysis；只读既有证据、覆盖和新种子，不做完整业务取证、不修改认领表、不派下级。先查Q05/Q06交付完整性及Q07可接续材料，优先回传三份直接可派包；当前队列0/3，准备中，不把条件候选算可派。预计初轮查重/材料3–5分、三包组成/估时4–7分、交付2–3分，共9–15分，中等置信；旧Q研究约3–12分、短复核约2–6分，不能抄30分钟预算。worktree/分支codex/task-prep-research-01-20261025，主窗登记后派发。

## 2026-10-25 专门预调研与动态补位（流程更新，历史）

用户要求三席执行研究/复核之外，另设一席独立预调研代理，提前保持与执行席位数相同的可派任务包（当前3份）。主窗口接到结束消息后，把结论、实测耗时/等待、token及新断边通知预调研代理；由其更新覆盖、滚动补齐队列，按近期同类实测动态合并/拆分下一任务大小。主窗口只做最终冲突/依赖/授权核对、唯一认领登记和派发，不再每次临时找题。包须有真实未闭阶段和可用证据，不能用预算代预测、拆微任务或跨域拼量；队列不足如实说明。细则见[统一流程3.3节](reverse-design.md#33-专门预调研代理预分配队列与动态切块)，模板见[通知文档](chain-claim-notice-prompt-20261024.md)。本次按“先更新到文档”只修改规则，不新建/唤醒代理或改变现有任务状态；旧三席总上限记录保留为历史，实际启动后默认三执行加一预调研。

## 2026-10-25 提交、合并与中间产物转存规则（后续派发适用）

任务派发即授权研究者/复核者在独占 worktree 的本地任务分支按精确路径提交报告、必要合同/清单和复验源码，无需额外申请提交许可；交付分支、基线、commit SHA、实际检查、未决项及工作树状态，由主树管理窗口验收后合并，记录交付SHA与整合SHA。禁止以仅回报指导意见或复制成果代替 commit 整合；推送仍须单独授权。独立技术验收要求不变，先行整合的成果仍标待复核。

导出、日志等中间产物不进 commit。任务停止后，管理窗口将其转存到主树相同相对路径并确认被忽略，先复制并逐文件核对字节或SHA256，再移除任务树源副本；同名异内容不得覆盖。应入库的遗留成果先补交并合并。确认全部commit已合并、tracked/untracked干净且ignored产物全部转存无遗留，核实任务绝对路径后无force移除worktree，再用 `git branch -d` 删除对应分支；有未保存/未合并成果或冲突则保留并记录阻塞，不用reset/clean/force强清。具体步骤见[统一流程第7节](reverse-design.md#7-独立复核整合和收尾)。

本节覆盖下方历史“不提交”“提交另行授权”“仅主树输出/无提交复制整合”的派发约定；历史事实和证据不改写。此次更新不启动研究、不改变并发或认领状态，用户后续明确指令优先。

## 2026-10-24 23:54 HKT 用户明确恢复持续三席

用户新指令“继续保持三个agent，结束了就补位”授权在无释放工具条件下继续尝试新建独立上下文；交付整合后即尝试补位，若thread limit拒绝则如实报告，不增加上限、不跨题复用上下文，不虚称已释放。已登记Q-01/02/03三项独占同接口包，预测据阶段与旧P17约6分/P18作者8分52秒及本轮短复核3–5分校准，不把预算当预测。材料覆盖或种子不足则提前按已覆盖/明确未知交付，不凑量。仅主树独占报告/analysis，不改生产，不提交推送，不reset/clean。

## 2026-10-24 23:50 HKT 当前整合状态（Q）

用户在新聊天明确接续后，指定三个fork_turns:none非作者均已交付，list_agents确认completed：P-16/P-17、P-18、P-19差集全部限定接受，行为纠正0、新增业务0；完整接口断边不变。P-19另补全system-complete-0041.json来源文件名。报告、派发/创建/开始/结束时间、实测token与cached input单列见[本轮Q汇总](interface-review-q-0041-20261024.md)。环境只有interrupt，没有close/release工具；completed不等于线程已释放，未继续补位或复用旧上下文。后续五槽生产候选已合成同接口21–30分钟包，仍未派发/未验。以下历史停止/待派/limit或持续补位快照不代表当前。


## 最新：停止派发，清理已完成（2026-10-24）

按用户要求不再派新任务。剩余19个工作树的73产物（含37 ignored）逐字节确认已在主仓，35JSON/177本地引用通过，再无force移除19树及对应分支。历史147个分支全量git cherry核对，149补丁均在主干；用户明确“抽查1/10如果都是这样直接清理”后已删除这147个残留分支。现仅主工作树/master，HEAD不变。N/P合计152产物再核SHA通过（N的3条复核注记按最终hash核），无提交推送。P-16/P-17、P-18、P-19仍待新聊天独立复核，不因清理标已验。机器记录：reverse/analysis/interface-batch-p-20261024/cleanup-final.json。以下持续派发/工作树状态均为历史快照。

## 持续滚动批次P（2026-10-24最新授权）

当前转交（用户已选择准备精简交接、新聊天恢复三席）：新建dock_control_review_01被运行环境以agent thread limit reached拒绝，未创建；当前工具无关闭旧代理接口。全部已有作者/复核者均已交付停止，当前运行0，不复用旧上下文绕过上限。P-16/P-17、P-18、P-19三组待新聊天独立复核，不标已验；用户的持续补位意图由新聊天接续，不代表整ROM完成。

估时校准：用户指出P-17约6分钟而标30分钟失败，后续先列阶段/估时/实测类比，短setter/应答约4–10分钟不再独立标半小时；同接口短阶段合并20–40分钟工作包，复核按差集单独预测。P-16/P-17合并复核预计6–10分钟。P-18错误地址前缀已由原字改正，两个目标是公开timer API，不另开其内部研究；将同S槽生产/在线分类合入当前接入接口，不再拆微任务。

后续代理命名按用户最新要求：领域_research/review_两位递增序号，如dock_control_review_01、app_summary_research_01；现有p*/pr*代理保留原名，认领ID/产物路径不改。新任务继续fork_turns:none。

第一检查点已保存：[批次P报告](interface-batch-p-0041-20261024.md)。P-01/P-R01、P-02+P-03/P-R02限定接受无返工，22产物已保存并清理五个已停止工作树/分支；p05/p06/pr03继续运行，仍持续补位。耗时/token为22:09:12香港快照，包含三个进行中任务，不作为停机或完整接口完成。

用户要求“持续下一批，做完了马上补位”。恢复三席持续滚动：研究/非作者复核合计最多3，完成即整合并新建独立上下文补位，不在一批结束后自动停止。每块约30分钟工作量，接口内差集合并复核；无新种子的旧root退出、公共库内部不补位凑题。先派P-01模式停机、P-02总量/普通功率生产、P-03动画期延后刷新；任务名p01/p02/p03不作为认领ID，避免与历史输入idle的P01/P02混淆；基线5bbc331，主树新流程和批次N只读继承。不提交推送、不改生产/ROM/配置/模型、不执行固件/设备/网络/SIM/QEMU/构建/回放。按轮保存实际耗时与token差值；新任务fork_turns:none。

## 批次N：三并行接口研究（2026-10-24，新授权）

本批已完成并整合：N01/NR01、N02/NR02、N03/NR03三个可用阶段限定接受，两个profile来源标注由作者修正并复核，行为纠正0，完整接口断边保留。6位代理已停止、运行0；26文件逐字节保存，13JSON/64本地引用检查通过；6个独占worktree/本地分支已无force清理，无提交推送。统计截止21:39:31香港，经过约26分7秒，累计子任务墙钟约51分21秒；实测输入25,107,254（其中缓存24,408,192、非缓存699,062）、输出125,802，总25,233,056，推理23,742已含输出。主窗口与审批/快照排除口径见[批次报告](interface-batch-n-0041-20261024.md)。

用户要求按新流程继续，保持三个并行，优先底座协议和应用接入；研究/复核运行席位合计最多3。首批N01模式设置、N02遥测快照、N03订阅寿命各按单代理约30分钟工作量规划，完整接口过大时明确阶段和断边；新任务均fork_turns:none，独占工作树，静态范围不变。作者完成后由新的非作者按接口相关性合并复核，不跨题复用作者。基线5bbc331；主树未提交文档作为最新流程只读参考。不提交推送；此节覆盖此前停止派发状态，旧成果不重置。计时从本轮用户消息起，token只取本地会话遥测的实测差值，缓存输入与非缓存输入分列，不将推理输出重复相加。

## 最新工作流程调整（2026-10-24，后续任务适用）

用户要求降低上下文与碎片交付开销。后续以[统一流程](reverse-design.md)为准：新研究任务和新复核批次显式 `fork_turns: "none"`，不继承完整主上下文、不跨题复用长期子代理；每块按单代理约30分钟有效工作量估算（参考20–40分钟），按完整接口或可独立验收的状态机阶段交付；相关小差集合并非作者复核。公共能力允许功能等价开源替代，停止默认深挖原库内部，只有必要原ABI/厂商差异才局部研究。约半小时是切块预算，超出时保留部分结果/阻塞及续作估计，不到点冒称接口完成。

管理窗口派发一次给齐接口边界、有限必要依赖、证据定位、验收与时间估算；边界内且无认领冲突的必要下层可同题完成，不再逐字段申请。跨接口/对象所有权、冲突或突破静态限制仍先登记。复核每批统一整合，并按闭合接口/独立阶段、耗时及可获得的token用量评价产出；缺用量不编造。下文旧的必须复用现有代理、逐helper派发/逐项复核、必须认证精确原库及逐新callee登记要求均由此与统一流程覆盖，旧证据/认领状态保留。

此次仅更新流程文档，不启动或恢复研究/复核、不增加并发、不提交推送；最后收尾状态继续有效。派发模板与转达文本见[通知 prompt](chain-claim-notice-prompt-20261024.md)。

## 当前限定复核已完成并关闭（2026-10-24，用户最新授权）

收尾核对PASS：三位非作者均完成并停止；3份报告及同名analysis共12文件（含忽略证据）逐字节保存在主仓原路径，全部JSON解析、23个相对引用、独占文件范围及diff检查通过。本轮3个review-close工作树及对应本地分支已安全清理，先核解析路径在本batch内再删除，无force。HEAD仍bd457a6，未提交推送；没有新派任务。

三项非作者复核已完成：A77接受A76（65项），A81接受A80的n1域（24项），F33接受F32（84项），共173项静态检查PASS；语义纠正/新增业务均0。三个待复核状态已关闭，所有功能断边保留；未补位或开展后继。

用户要求“为我复核以及关闭”。本轮只恢复三项待复核差集的非作者独立复核：A77挂J08/12核A76；A81挂J08/14核A80；F33挂F11/12核F32。没有滚动补位或新逆向链授权，不展开未闭功能边（包括3ae0、广copy、实际quit）。复核通过则关闭该交付的待复核状态，并独立保留未闭功能边；不冒称完整ROM恢复。固定基线bd457a6，原件/映射及静态限制沿原记录；仅独占报告/analysis，不提交、不推送，完成后整合清理本轮工作区/分支。
## 前次收尾（2026-10-24，历史）

用户要求“当前分发的任务结束后，不再派发新任务”。立即停止新派发/补位；F31已交付的/root/f12保持停止，当前/root/g23 A76和/root/a56 F32只在已授权范围内收敛、保存现有证据及精确断边。A76尚未登记的新分支窗不再展开，不为闭合固定format扩大引擎；F32不新增ROM/callee。未派A77/A81及其它准备项冻结，不因旧滚动文字自动恢复。

管理窗口继续整合已交付的报告/源码/合同/本地忽略证据、检查引用/差异，并在作者停止及全部产物逐字节保存主树后，按路径边界/无force规则清理本批完成和未派工作区及本地分支。主树成果仍未提交、不推送；原件/生产/配置/模型不改，不运行固件/模拟器/构建/设备或外部服务。仍待独立复核的作者成果不因本次收尾标已验，整个ROM目标未完成。以下持续滚动及预备文字自此均为历史，以本节与行内最新状态为准。

最终收尾（2026-10-24）：实时确认3个subagent均completed，运行0；停止补位指令后没有新派任务、没有启动A77/A81复核。F31已限定接受F30四字节回环。最后A76仅完成7个已授权窗560B/59项静态检查，断边0xa01a3abe→0xa01a3ae0，未读未授权3ae0窗口；F32仅旧证据同M退出绑定/线程创建失败caller，45项检查、ROM0B。A76/A80/F32仍待独立复核，不能借管理整合标已验；固定%s取参/输出/最终NUL、广copy域、实际quit/queued I排空/最终free及完整ROM目标未闭。

尾批17个已停止任务68个全部独占文件（含ignored JSON）逐字节保存主树、JSON解析及173相对引用通过，已安全清理这些树/分支。A76最后4文件也逐字节保存、两JSON/8链接通过；A77/A81从未派发且tracked/untracked/ignored均空，均安全移除工作树及本地分支。全部删除都在解析后本会话batch绝对路径内、无force、分支仅指固定bd457a6无新commit，不动主仓原件/成果或其它批次。最后单任务PowerShell数组展平曾被路径存在性校验拦下、未执行删除；显式嵌套及形状断言修正后才成功清理。

主树保存全部本轮报告、复验源码、必要合同与原路径本地忽略生成物，未提交、未推送；生产代码/ROM/配置/分析器模型未改，没有执行固件/指令模型/SIM/QEMU/构建/历史回放/设备/外部服务。用户后续若要求恢复，必须重新查重登记并以当时基线开独占树；本文旧滚动队列不自动恢复。

最终整合核对PASS：本轮47个已创建任务引用逐一检查，45份交付报告及同名analysis共177文件仍在主仓原路径（含本地忽略产物），全部JSON可解析、671个本地相对引用可定位（支持既有:行号链接）。本batch工作树0、对应本地分支0、目录无遗留、表内活动认领0，HEAD仍bd457a6；A77/A81两准备任务从未派发/无报告。diff检查通过，仅报告/analysis/研究索引和管理文档改动，未暂存/提交/推送。

## 前一阶段三席持续滚动（2026-10-24，历史）

用户明确要求“继续逆向，按照三个并行，完成就补位”。本管理窗口/root恢复3个研究席位，完成即安排已查重的新差集或非作者复核，不按一批完成自动收尾；旧停止/清理和上一批运行0记录均为历史。当前基线为主仓HEAD `bd457a6`，本轮不提交、不推送；遵循最新reverse-design及analysis/README的本地原路径保留规则：导出证据仍保留原路径并受Git忽略，源码/合同/结论单独维护。只做0041有种子静态分析，不运行目标/固件/模型/SIM/QEMU/构建/历史回放/设备/外部服务，不修改生产、ROM、配置或分析器。

首发三席：F13在F11/1的native queue断边补指针复制/持有问题；G25在G19/5补G24已定位的实际op3消费/持有；A58在J08/3仅查head/stride槽的旧writer metadata以定位真实注册桥，尚不新取无边界ROM。已搜索近期报告与认领表，三个问题未有已验本体合同、无活动作者；F11/1–2、G19/3–4、J08/1已验部分全部继承，不重新恢复。任何超范围caller/callee只报种子，由管理窗口先查重登记再展开。管理表只由主窗口写；研究者不自行接后继或创建下级agent。完成后回报并停止该任务，管理窗口串行整合、登记、补位，最多3席运行。

F13必要增量登记（2026-10-24）：作者核0xa005f464的正常−1路线，仅转交a1并把word(queue+0x18)作a2，返回折成0/−1；adapter未复制。新增唯一连接0xa005f480/484→0xa0197a8e，对同一源pointer/长度的消费是原F11/3问题所必需。作者所查functions5812仅164B extent/directcall，无dossier；主窗近期非管理报告搜索a0197a8e/a01949f0/a0197b32无命中，和G19/J08无对象交集。准该正常callee必要稀疏窗口，不扩定时/其他下层服务；新调用边再报登记。


F13二次必要增量登记（2026-10-24）：正常非零message路径到0xa0197b1a→0xa01949f0，source仍作为a2、原长度作a3转交，回答F11/3必须追其最小复制/持有接点。旧functions5771仅366B extent及directcall、无dossier；主窗近期非管理报告a01949f0/a01318de/a0131920搜索无命中。准0xa01949f0正常源/长度消费的必要原字段，候选message来源/等待保持opaque，不扩allocator、全queue、调度或其他输入；同queue长度=4身份仍未知。新依赖再报，不能沿helper名称证明复制。


G27必要增量（2026-10-24）：0xa00267c0本层call0xa0026784后，非零返回其+4、零返回固定0x62fc604c；本层除栈无已见写，未知callee副作用不抹去。主窗近期报告精确a0026784/0x62fc604c无命中，作者旧functions431仅38B extent/directcall无dossier/contracts。准同G19/6补0xa00267c8→0xa0026784返回对象来源的必要原字段，不追0xa002671a或全TLS/调度，新边另报。

G26预登记（2026-10-24）：G25已交付停止，原G19/5挂非作者/root/a56，在A58交付停止后立即补位。只核实际op3实例化、旧完成I与新提交j及record来源区别、E+0x18/E+0x20、符号扩展/直接持有限定；不重验共用body/递归/其他op。独占pogo-poll-op3-review-g26报告及同名analysis，研究基线bd457a6。G25新增独立body0，复核新增0如实写。


G27二次增量登记（2026-10-24）：0xa0026784本层仅以(0,&out)调用0xa002671a，非负返回时取out+4为B，负时B=0，尚无对象来源。准0xa0026792→0xa002671a对out+4写入/返回的必要106B服务窗口；作者旧functions430仅extent/directcall无dossier/contracts，主窗近期精确a002671a报告搜索无命中。0xa002661e/诊断/全调度均不展开，不以路径候选推TLS或稳定B。


滚动复核队列（2026-10-24，最多3运行席）：F13已交付，挂F11/3非作者/root/g23，G27交付停止后在新树执行F14，只核Q→F→K、source/length实际转交、copy服务先于接链/计数、符号返回及copy域限定；不重验全copy/allocator/wait。G27交付后挂G19/6非作者/root/a56，G26交付停止后执行G28，只核getter的global T→out+4→B+4/fallback链与正常a0=0绕下层分支、局部out写/稳定性条件，不扩TLS调度。独占miio-native-queue-review-f14和pogo-poll-error-slot-review-g28报告/analysis，基线bd457a6，复核新增0如实写；未收到作者交付不提前把预登记算运行。


F15新窗口登记（2026-10-24）：作者旧upper-complete record248定位0xa0064f4a s7=M+0x128；0xa0065438/3a/48/4c以(M+0x140,0x80,4)调用0xa005f0b0，输出槽=s7+0x18；0xa006556a/6c把s7交线程入口0xa011e3d6。主窗近期精确creator/callsite地址报告搜索未有该size写入合同，旧functions1451仅158B metadata无dossier。准0xa005f0b0入口参数绑定、成功Q→Q+0x18与输出槽写入必要稀疏原字段，不展开queue开/allocator；F11请求ctx+4→该候选loop仍未知，只认证候选同loop输出size4，不冒称全部实际F11路径已绑定。可继续旧留存必要身份桥，新callee另报。

滚动整合清理（2026-10-24）：G25/A58/F13/G27四作者均交付停止，13个全部独占报告/源码/合同/本地忽略JSON已逐字节保存主树原路径，JSON解析及47相对链接通过。核4树tracked/staged无改、未跟踪及忽略恰为已保存成果，解析后路径均在本会话batch根内，移除临时副本后用无force的worktree remove及branch -d回收codex/re-0041-g25/a58/f13/g27（均无新commit，只指bd457a6）。主树成果仍未提交，忽略导出保留原路径，三运行席F15/F14/G28不受影响；G26作者复核已交付待整合。

A59预登记：同J08/3挂非作者/root/g23，F14交付停止后补位，只核A58有限搜索边界、0xa005a8f4基址来自caller栈局部的排除与必要旧dossier，不重搜全载体、不新ROM/不推全局无writer；独占reader-driver-writer-review-a59报告/analysis，复核新增0如实写。


F15身份桥必要增量（2026-10-24）：creator原字段已证保存a2并在成功后写Q+0x18、*out=Q；旧record248/195/96/27又定位同L的start callback/user链，0xa0110708/718实际以(L,M+0x174)/(L,M+0x968)调用0xa01ab55a。旧functions6143仅218B metadata无dossier，主窗近期精确地址无已有合同。准该attach入口参数与正常ctx+4保存L的必要稀疏原字段，不能凭调用名认同；其他log/memset/callback保持opaque。两个ctx与F11来源仍需此次存槽证据后才限定接受，新callback本体不随之展开。


复核补位预备：F15交付后在F11/4挂非作者F16，仅同queue正常size4/ctx+4保存loop身份桥、实际存槽及成功门，F13copy域不搭便车；F17交付后在F11/5挂非作者F18，仅n4且有效word对齐路径的copy/返回/持有与前提，旧n16/20不重复。独占miio-queue-size-review-f16、miio-queue-copy4-review-f18报告/analysis，实际作者停止和复核者在派发前更新本行，无新agent/并发增加。


第二组完成复核清理（2026-10-24）：G26/F14/G28已交付停止并整合，9个独占文件与各树逐字节一致、JSON/31相对引用通过，tracked/staged无改、untracked/ignored均已保存。核解析路径在本会话batch内后，清理三个已保存临时副本、无force移除worktree，branch -d删除codex/re-0041-g26/f14/g28（仅bd457a6，无新commit）；本地忽略证据仍在主仓原路径，不删除原件/历史导出。F15/F17/A59三运行席不受影响。

A60输入与工具边界：A58/A59仅旧metadata/有限排除不能回答已知G使用指令里的两槽初始化，后继A60改读三已定位owner的必要旧assembly定义/用途，差集明确，禁止再全盘同头负搜。管理窗口只读REA binary_session观察当前open=false，未打开/切换target、未建分析数据库；不为此任务修复/修改共享REA/profile或运行模型。旧assembly不足时只报确切owner/地址及需取得的xref，不将缺facet当全局无writer。


A60必要旧证据增量（2026-10-24）：0xa005cd36→0xa008e3ac是A25/A26已验callsite，A21/A22及A25已有清零G=0x62fc957c、长度0x210合同；覆盖两槽的初始清零直接继承，不计新writer。准只读该initializer在A21/A25已存证据中与两槽清零/可能stride初始化有关的必要行，旧index functions2121 extent1226B不能作body合同，不新ROM/反编译、不整段重导initializer、不读新callee。该增量仅补J08/4已知初始化callsite的两槽用途，和A21/25既验PNG/像素内存合同不重开。


A60精确缺窗升级登记（2026-10-24）：三owner与A21/A25旧留存只解释已验G清零，缺0xa008e4c4..0xa008e612的定义/用途片段；0xa008e4c0已知s4=G+0x100，而右侧s2+0x18来源未留存。主窗按a008e3ac在旧pass1..5精确检索仅pass3两条caller，无新增callee body。为回答同J08/4两精确槽初始化，准仅缺窗[0xa008e4c4,0xa008e612)最多334B，按短窗从已知基址追到两槽的地址构造/调用端，定位即收缩停止，不扩其他G字段、整1226B initializer、全ROM/新callee body；没有真实身份依然标未知。新输入为确切旧窗口缺口及两端锚点，非重复metadata负搜索；厂商未知须保留，不修模型。

第三组整合清理（2026-10-24）：A59/F17/F15三作者/复核者已交付停止，14个全部独占源码/合同/报告及忽略证据已逐字节存主树，JSON/39链接通过，tracked/staged无改、所有untracked/ignored均纳入。路径核本batch内，已回收对应worktree与codex/re-0041-a59/f17/f15分支（均仅bd457a6，无新提交），主仓本地导出原路径保留；A60/F16/F18运行席不变。


F19接收adapter增量（2026-10-24）：旧record195定位无同步链时0xa011e5fa→0xa005f508(Q=word(L+0x18),&localI,timeout)，localI预清零，timeout为10000或旧timer项+4；call返回后不比较a0，直接读localI非零才进入既验分派。functions1461仅164B extent/directcall、无dossier，主窗近期精确a005f508/a01978a2/a0197954未有本体合同。准该adapter的正常输出槽/长度/timeout转交与返回最小原字段，不展开下层两服务、clock/timer或整个consumer，新边另报。


F21池候选必要增量（2026-10-24）：本层覆盖原a0、依次用gp+0xb8、条件gp+0xc0调用0xa010d70e，另臂仅把0x14c作为a0交0xa002fcc8并给非零M写byte(M+8)=1。G11只有从backend+0x3c取节点的调用角色，不能据同callee认池同一。准先核G11/G12旧callee留存/合同，若无正常取节点body合同，仅补0xa010d70e(gp+两偏移)节点取出/返回必要字段；不展开allocator0xa002fcc8/调度/等待/池初始化，不把332请求或非零M当容量/实际分配认证。其他报告对a002fcc8的既有接口角色只引用，事实/推断分列。


F19有限receive下层增量（2026-10-24）：adapter实际timeout=10000走finite路线，以(Q,out,word(Q+18),&deadline)在0xa005f59e/5a2调0xa0197954，返回经SRAI31；−1路线a01978a2仅锚点。functions5811仅314B metadata无dossier，主窗近期精确地址无已有body合同。准该正常finite service对out/n及消息copy/归还调用端的必要字段，不展开新下层caller/clock或−1服务。a005f56a的原字8b97d420未知转换具体保留，不NOP、不推deadline单位/时钟精度。

A61预登记：A60作者已交付停止，J08/4待非作者，只核两槽确切writer、正常分支/s1保存前提及第三次同序SW锚点，不重验G清零/PNG/caller/节点登记。独占reader-driver-global-init-review-a61报告/analysis，复核者在派发前更新，新增0如实写。A62继承A60仅作待复核候选，不提前标初始化已验。


F19消息输出/归还必要增量（2026-10-24）：finite非空分支0xa0197a36→0xa01319e8(K,word(Q),&localMsg)，返回0后以Msg+0xc、U16(Msg+0xa)作copy源/长度，copy到原out后才0xa0197a6c→0xa0131b68(Msg)。实际copy长度是Msg字段不是直接Q.size，不能把F15初值4替代。主窗近期两服务精确地址无已验报告，准同F11/6仅正常非空pop/out写入、Msg字段是否保持及正常归还分支/下一跳参数的必要字段；不接空队列等待/调度/新下层heap/helper，新边先报。发送端M与本次首Msg是否同一运行实例仍未知，只恢复条件静态连接，不借参数/类型名认同。


A62登记缺窗原字段增量（2026-10-24）：旧helper逆directcall仅9个caller，PNG/display/group/animation等已验不同header直接排除不重做。真实caller候选a008e3ac有fs.c诊断源xref0xa008e800/0xa008e820及insert-head边；A21 BIN选窗止e768、PNG选窗始e82c，之间196B缺失，不能单凭路径推注册。准仅[0xa008e768,0xa008e82c)逐短窗从已知G基址找a0=G+1c4调用与返回node.word0保存D，定位即收缩，保留未知/诊断门；不读其他caller、新helper或D槽目标body，遇新连接先报。新输入为确切caller/缺窗/两端和目标header种子，非无种子fsdrv扫描。


F19/F21共用helper去重（2026-10-24）：F21作者已交付停止，a010d70e正常取链42B合同只在F11/7一次研究；F19不得重读/重验相同body。主窗已整合F21报告/同名analysis原路径供F19只读继承待复核合同，标明F21尚待非作者F22；实际F21 H=gp+b8/c0，F19 H=K+18，是不同容器实例，不能因共helper认同。允许在给定有效哨兵/链接前提下实例化返回节点/摘链原序，未经验收部分保留条件；F19自身out/length/归还字段差集继续独占。


下一轮复核补位预登记（最多3运行席）：F19交付后在F11/6挂F20非作者，只核finite接收adapter/out/Msg长度与正常pop/归还分支，F21共用helper不重复取；F21已交付，在F11/7挂F22非作者只核候选M三来源/当前caller flag门、gp两池取链/清槽与申请332请求边界；A62交付后在J08/5挂A63非作者只核header0x62fc9740→insert-head成功node→D0x62fc974c保存及s1/正常分支前提，不读slots。实际作者停止及复核人派发前更新对应行。独占miio-queue-receive-review-f20、miio-queue-message-source-review-f22、reader-driver-register-review-a63报告/analysis，基线bd457a6，复核新增0如实写。


F23必要原字段增量（2026-10-24）：旧caller已证flag6034为0时，经K计数门到0xa0197af8→0xa0131920(a0=K,a1=word(Q))；返回0重试快速getter，非零直达恢复mstatus/原值返回，source/n仍保存在s3/s4。没有outM参数或返回值直作M，先前任务问题中的outM只是待找端假设，已纠正。F13缺[0xa0197ad2,0xa0197ae8)22B，且服务旧index200B extent无dossier，近期报告仅opaque引用；准这22B caller缺口和该服务正常状态/返回必要原字段，不读下层等待/调度/其他输入/定时send。新callee先报，不能从名称解释阻塞/成功。

F24预登记：F23作者交付停止后，在F11/8挂非作者只核正常send flag/count→状态服务→0重试getter/非零退出、source/n持有、缺窗控制及本体正常返回/下一跳，不借名补outM/阻塞/成功。独占miio-queue-send-wait-review-f24报告/analysis，实际复核者派发前登记，复核新增0如实写。


F23对F21/F22 caller覆盖的纠正登记（2026-10-24，待F24独立核）：新旧caller行定位flag6034==0且signed count<max时，0xa0197af0仍可回0xa0197acc调用getter。因此F21/F22“caller第一次flag非零才进getter”的整体表述过强，应仅限0xa0197aca的直接落入边；不能用它覆盖所有正常前驱，稳定flag0的该回边仍允许第一池空后到332请求。两gp链/flag重读/申请接口/helper42B本体合同继续保留，不因caller覆盖纠正推翻。旧冻结报告/合同不静默改写，F23保存新边/字段及明确范围纠正，F24须独立核af0目标及count/flag前提；不作任何输入实验或缺陷验证。后续F25必须继承新旧边并集，不重复旧有限前驱错误。


A64必要原字段登记（2026-10-24）：旧A25/A21目前只留s2在e3c4的高位62fc9000，A60/A62最小锚点不足证明之后定义。准先[0xa008e536,0xa008e612)最多220B逐短窗找s2普通定义，找到即停，不读其他字段/helper；若定义不在该首gap先报精确下一候选，不猜。证明e77a s2+180=已登记D后，才准[0xa008e770,0xa008e7de)最多110B中盘符/config和已验open/close/read/seek槽四个必要写入/常量，不读任何callback body。若A60探索末尾有未留存定义需先指出小缺口，不能把最小锚点缺失当无定义。

F25合成边界：只综合已验F11/F14/F16/F18/F20/F22等正常typed接口，F23状态路径及caller覆盖纠正目前待F24，必须标明未验依赖不提前闭合；不能借同size4/同field合并运行Msg或补消息存储有效/容量/不别名/对齐/寿命。新增应是旧native queue断边在限定域内的语义连接，不以重读字节/文件数计恢复。


A64基址式与缺段收敛（2026-10-24）：e5da实际ADDI候选使s2=G=0x62fc957c；e77a中间B=s2+0x180=0x62fc96fc，本身不是D974c，B+0x5c等有效地址才对应D+0xc。先前“中间基址等于D才读slot”的门条件撤销，改为精确有效地址相等，不能为类型名强行重命名寄存器。核正常定义连续性仅补[0xa008e4b8,0xa008e4bc)4B、[0xa008e52a,0xa008e536)12B、[0xa008e5f6,0xa008e612)28B、[0xa008e628,0xa008e6ea)194B必要定义/控制短窗；A60原探索无保留字段不当连续性证明，旧A21/A25其它两端直接继承。不读正常流跳过的诊断/其他helper/字段，若遇call仅保留正常callee-saved约定。连续性核完再应用已登记slot110B，发现别的定义先报不猜。

F24在进行的原序精确化：a0131972先LW(T+0xc)存寄存器，1974才SH0到T+0x22，1978比较旧读值；F23表内地址正确但末伪码应保留v=load→clear→compare(v)，不能clear后重读。F24最终意见列此限定伪码纠正，旧字节/本体不变；F25继承时用正确原序，不静默修改冻结F23。


F26/A65复核预备：F25交付后在F11/9挂非作者F26，只核条件合成/原F11 native断边、I指针值与I对象/Msg/两个局部槽区分、证据域与未闭前提，不新取ROM/重跑作者脚本；A64交付后在J08/6挂非作者A65，只核s2正常连续性/B+offset有效地址到已注册D、盘符/config/four-slot实际写端，继承注册/selector不重验，不读target body。独占miio-invocation-queue-lifetime-review-f26与reader-driver-slot-review-a65报告/analysis，派发前更新实际复核人/作者停止，最多3运行席。

A64指令边界记录：e5f6落在e5f4四字节ADDI中部；仅回到已授权首gap内真实e5f4边界重读前2B，按30B窗至e612，未采用中途伪压缩解码。此为必要边界校准非新模型/语义/范围授权；正常s2连续性条件与callee保存前提保留。

F24最终已限定接受：65项/288B独立检查，caller范围纠正1、F23伪码load→clear→compare旧值精确化1，新增业务0。F25写作时F24待验属历史，后续非作者可继承最新F24条件，不推mode名/T运行身份/循环进展/交付/存储寿命；旧冻结报告不改。

A66派发依据：A64报告前原字进展已给真实候选open/close target a00ef468/a00ef502，亦为J08/2原ROM source_path已存owner，足以按精确函数种子独立恢复正常body；对D槽绑定仍标A64待A65，不提前验收。两callback本体与A64初始写入窗口互不重叠，新callee另登记。


F27创建参数必要增量（2026-10-24）：F15只保留attrs/调用，调用前[a005f10a,a005f11a)16B参数缺失；旧functions5799对a01974de仅48B metadata无dossier，主窗近期两个精确wrapper/下层地址无已有mode写入合同。准16B caller组和a005f122/126→a01974de正常参数/返回最小48B wrapper，先明确同Q及真实flags/varargs，不读a010e320新body、不执行open或FS。只有请求flags事实尚不等于Q.word0，下一写端另报登记，不补正式bit名/后续无writer。


F27首word写端增量（2026-10-24）：creator已核(a0=Q,a1=&name,a2=7,a3=0x180,a4=&attrs)，a01974de把原a3..a7装本地包，转(a0同Q,a1同name,a2=7,a3=0,a4=&包,a5=0)到a010e320。wrapper不写Q首word；旧functions3840仅530B metadata无dossier，近期无该写端合同。准仅a0197502→a010e320同Q/flags7的首word初始化/正常控制必要片段，定位写端即收缩，保持后续callback/writer效应未知，不读新FS/allocator/driver callback。

A66路径数据/wrapper增量（2026-10-24）：准仅literal a06371e4的NUL字符串最多64B且遇NUL停；及a00ef4a4→a008ab4c的42B格式化wrapper参数/返回桥（旧metadata→a0053252无body合同）。下层formatter算法仍不准展开，区分实际format字符串/argv事实与按格式family解释的推断；不以wrapper调用当输出字节已证。底层a003f4f6 pathname/flags与fd角色继承D03，a0026888接口/归还边界继承F05/F06，不新读它们或errno-map。H=fd+1的低word编码/close减1和无free(H)按callback原字段解释，非FILE*。


A67/F28复核预备：A66交付后在J08/7挂非作者A67，仅mode2路径接口/format argv与literal事实、H=fd+1/close−1及返回/无free(H)正常条件，不读formatter/底层IO；F27交付后在F11/10挂非作者F28，仅同Q flags/首word写端身份和成功/后续writer边界，不把请求7自动当最终word(Q)，不读FS/driver body。独占reader-driver-open-close-review-a67、miio-queue-mode-init-review-f28报告/analysis，作者停止/实际复核者在派发时登记。


第四/五组滚动整合清理（2026-10-24）：F16/F18/A60/F21/A61共16文件逐字节保存、JSON/62引用验证后，已回收5树及codex/re-0041-f16/f18/a60/f21/a61；F19/A62/F22/F20共20文件逐字节保存、JSON/49引用通过，已回收4树及同名本地分支；F23/A63/F24/F25共17文件逐字节保存、JSON/57引用通过，已回收4树及同名分支。各组均先确认作者/复核者停止、tracked/staged无改、全部untracked/ignored已保存、解析路径在本batch内，再无force移除worktree/branch -d（均仅基线bd457a6无新commit）。所有主仓本地忽略导出仍保留原路径，未提交/推送，运行中的3席和未派准备树不动。F24/F25之pending状态按写作历史，最新复核/补位仍以本表为准。

A69预登记：A68作者交付停止后，同J08/8挂非作者只核真实callback ef55e/ef632入口、H−1、buffer/position/out字段宽度、read成功才写out/零读同门、seek unsigned whence>2原11、只判a0 signed返回及error前后重读，不套邻近write边界、不读新IO/errno-map。独占reader-driver-read-seek-review-a69报告/analysis，实际复核人派发前更新。

A68精确target校准：callback0xa00ef632的0xa00ef64e原JAL独立取位后真实下层为0xa00281d8；中途速报a00221d8/对应无entry查询已弃用，未登记或读取错误目标，最终报告/合同/字段检查均281d8。后续A69只核原字段，不据标准off_t补ABI，不扩大IO。

A71预登记：A70交付后在J08/9挂非作者仅核a00ea524静态signed树/常数/default/返回宽度与外部写，不能命正式enum/版本，不运行输入枚举/目标或host模拟。独占reader-driver-result-map-review-a71报告/analysis，实际作者停止和复核者派发前更新。

第六组整合清理：F26/A64/A66/F27四已停止任务16文件含所有本地忽略产物逐字节保存主树，JSON/53相对链接通过；tracked/staged无改、untracked/ignored全部保存，解析路径在本batch后，无force回收4树及同名codex本地分支（均仅bd457a6）。未提交/推送，主仓导出原路径保留，运行席/准备树不动。

A74必要适配层增量：C13/C14/C23/C24只验两遍调用/candidate语境未验真实输出，不重开已验部分；functions1350 a0053252仅120B metadata无dossier。准其正常参数/输出流/返回必要原字段，并仅复用a002d770既存32B historical dossier ev_2fc7174…（profile4825）作必要参数/返回桥；a01a37d2新body先不读，不展开任意格式/输入枚举/模型。

A73/A75预登记：A72交付后在J08/10挂非作者A73仅核实际D条件生命周期合成/边界与引用，不新ROM；A74交付后在J08/11挂非作者A75只核count256适配层/S结构/初始SB0/旧32B桥ABI与原返回，不读engine/writer。独占reader-driver-lifetime-review-a73、reader-driver-format-review-a75报告/analysis，实际复核者派发前更新，复核新增0如实写。

A76入口增量：旧procedure仅两不连续extent总3144B、13条direct edges，无dossier/合同；upper/近期精确种子无body。准[0xa01a37d2,0xa01a3852)128B五参数保存/首fmt字节/literal或percent入口，固定fmt实际地址与S域继承A74候选，不整engine/补满间隙/读A78三个指针body。实际后继地址再报，保留direct/indirect遗漏及body边界限制。

A76固定literal入口续窗：已核S→s1、va→s6、逻辑计数s2=0，fmt首U8为/走非percent门，S+4加载callback并以a1=该byte/a0=S准备；入口窗恰止实际call前。准仅[1a3852,1a38c0)110B核真实间接调用与percent入口控制，frame搬运的无关doubleword不提取/不解释float路径，结束4410先只留锚点；A78 callback本体不重读。

A79登记：同J08/13非作者/root/f12仅核A78三精确入口的参数、unsigned min/signed n门、copy调用后重读/计数先写再NUL、n0无更新、noop返回，无新copy/engine/任意输入；独占reader-driver-format-stream-review-a79报告/analysis。A76续窗：literal S+4(S,47)真实JALR后J→4408，固定s经38bc unsigned门→38e4；准[38e4,3950)108B及[4408,4430)40B只核固定转换入口/续读与终止返回，不读跳过38c0..e4或其它fmt分支。

A77预登记：A76在当前固定format问题交付后，同J08/12挂非作者核已交付入口/真实间接ABI/固定s分支/计数与返回，不读未登记engine旁支或A78 bodies。独占reader-driver-format-engine-review-a77报告/analysis，实际作者停止/复核者派发前更新。

A76固定s缺口续窗：38e8 BNE('s',0x30)实际跳回38c8，原按范围未读此段；准[1a38c8,1a38e4)28B只核此真实门，不推进38f4旁支停解或修模型。4408/440c已核回3832，zero fmt到4410/4428 a0=s2/442e RET，无终止callback；计数s2与S.word0保持区分。


A80 n1必要增量：旧record76已定位n1从589c小量门经58ae..58c2到590e LBU/5912 SB/5916 RET，F18两端已有字段，缺24B dispatcher。准仅[58ae,58c6)核n1门/原dst设置，不触n8..255其它alignment body。旧B25 n12仅caller接口不是算法域认证，后续域矩阵须明确，不将src向下对齐读的padding可达性补猜或做异常试验。

A76固定s续窗：38c8减0x30后ANDff，38d0 unsigned比较9<0x43真跳3a78；准[1a3a78,1a3ad8)96B固定s实际调度，数字支路38dc停解保留未解释但该固定路径不执行，不补未知/NOP或修模型。

A76下一50B实际控制：3a78对0x2a不等→3aa8，对0x2e不等又回3a46，准[1a3a46,1a3a78)50B只核固定s实际门；3a80/3ad2未选旁支未知保留，不伪造连续覆盖。F31/A81预登记：分别同F11/11/J08/14非作者只核F30四字节回环与A80已交付n1域，独占miio-queue-mode-name-review-f31及reader-driver-format-copy-review-a81报告/analysis，待作者停止/实际派发更新，不重复old prefix或1080B算法。

## 上一批三席恢复（2026-10-24，历史）

用户已明确要求继续逆向并按3个subagent启动，覆盖下方旧停止/六席派发规则。当前管理窗口/root串行登记，以主树HEAD `32f9c9e` 为研究基线；本轮不提交、不推送。保留主树已有README、reverse-design及通知prompt改动。只做原厂0041有界静态取证，沿本表统一原件身份及VA映射；不执行固件、构建、SIM/QEMU、设备或外部服务，不修改生产/ROM/配置/分析器。

恢复范围：F12在F11/1–2原认领下做非作者复核；G23恢复G19/4的0xa009dfcc本体差集；A56恢复J08/1的0xa019d708..0xa019d796选择窗口。三个问题及对象不重叠；继承已验部分，新增callee只留锚点、报管理窗口查重后再展开。工作区均置于本会话可写根，独占报告/analysis；共享REA不切换。作者完成标待复核，复核新增0须如实记录。以下历史停止与旧预登记文字保留追溯，以本节及行内最新状态为准。


本轮进展与复核登记（2026-10-24）：F12已独立限定接受F11/1–2，106项稀疏字段检查PASS，新增业务/语义纠正0，报告`miio-request-ownership-review-f12-0041-20261024.md`；原native queue及实际执行边界不变。A56作者已停止，41项选择窗口检查PASS；J08/1挂非作者/root/f12执行A57，只核144B选择窗口及必要继承前提，独占`reader-driver-selection-review-a57-0041-20261024.md`及同名analysis，不重验A47接口/新登记writer。G19/4挂非作者/root/a56执行G24，待G23作者交付停止后只核新增0xa009dfcc的重读、诊断门、完成环、副本消费和返回差集，独占`pogo-poll-ring-consume-review-g24-0041-20261024.md`及同名analysis，不展开新callee/op3/native服务。复用现有3个subagent/原独占worktree，不增并发和新agent；管理窗口只整合范围，不冒称技术验收。


本轮完成与清理（2026-10-24）：3个subagent均已交付停止，实际运行0，未增第四个agent。F12独立限定接受F11/1–2；G24独立限定接受G23的G19/4条件本体；A57独立限定接受A56的J08/1选择窗口。复核语义纠正/新增业务均0。G19/4入口到完成环正常可达性、诊断返回、op3本体、counter/副本寿命仍未闭；J08/1实际D/slot/注册writer及寿命仍未闭，J08/2不因此闭合。整ROM目标未完成。

5份报告及配套脚本/JSON共15文件均已逐字节保存到主树工作区，JSON解析和54个相对引用检查通过，未重跑作者/历史脚本。F12/A57/G23/A56/G24实际原字段检查分别106/36/100/41/90项PASS，范围与局限见各报告。仅文档及analysis改动，未提交/推送，HEAD保持32f9c9e；原README/reverse-design/通知prompt改动保留。F12报告见[独立复核](miio-request-ownership-review-f12-0041-20261024.md)。

清理前逐树核实全部tracked/staged无改动、untracked恰为独占15文件、ignored为空，核主树副本逐字节相等；研究/复核者均停止。解析本轮根`D:/CodexHome/visualizations/2026/10/24/01a16c54-73c1-74d2-a8ca-eba16f78f706`下的re0041-f12/re0041-g23/re0041-a56后，移除已保存的独占临时产物，用不带force的git worktree remove清理3树，再git branch -d删除codex/re-0041-f12-resume、codex/re-0041-g23-resume、codex/re-0041-a56-resume。三分支均只指向基线32f9c9e，无新提交需要合并；此次整合为主树未提交文件保存，不冒称已提交。3树/3分支已回收，其他历史树/分支未触碰。

## 已完成任务的工作区清理规则（2026-10-24新增）

任务完成且全部成果已合并后，管理窗口必须清理对应 worktree 并删除本地任务分支；本规则取代下方历史“分支保留”的约定，历史清理快照按当时事实保留。清理前确认作者/复核者已停止、成果已纳入管理分支、tracked/untracked/ignored 无未保存产物，并记录分支名、提交、合并依据和清理结果。核实解析后的绝对路径位于该批任务根目录内，退出该 worktree 后用不带 force 的 `git worktree remove` 清理，再用 `git branch -d` 删除对应本地任务分支。cherry-pick 导致祖先关系不成立时先核成果等价性并报告阻塞，不直接使用 `-D`。仍运行、未合并或有未保存成果的保留并注明原因；不删除主分支、其他任务或远端分支。认领行、报告、证据引用和合并记录永久保留可追溯性。详见[流程收尾要求](reverse-design.md#7-独立复核整合和收尾)。


## 当前停止收尾（2026-10-24，最新指令）

用户后续要求连分支一并清理（2026-10-24）：已再次核对本轮23个任务分支均无worktree占用，且其独占任务文件与主分支完全一致（成果先前按记录cherry-pick整合）。现已删除这23个本轮分支；主分支、其他历史分支和既有未提交文档改动保留。下文“23个分支保留”记录的是前一次worktree清理时状态，已由本次明确指令取代。未启动任何subagent或取证任务。

用户要求：当前任务结束后不再启动新的subagent；现有工作完整收尾、合并并清理worktree。已核实时状态：所有subagent均已提交并结束，运行0；不再续派，不激活已完成agent执行新任务。F12、A56、G23仅曾预登记，均未派发、未创建工作树或产物，不启动。

全部已交付任务提交已整合入主分支。G19/1–2由G20、G19/3由G22、P01/1由P02非作者限定接受，复核新增0；F11/1–2只有作者研究交付4bff422，仍待独立复核，不因本次停止而标已验。J08/1–2仅旧证据盘点，D实例/注册/slot绑定仍未闭；G19/4条件提交服务body未展开。完整ROM目标未完成，所有旧来源差异、SIM边界和精确断边保留。

本轮23个独占worktree逐一核实：作者/复核者已停止、tracked/untracked状态干净、无ignored遗留产物，任务所有文件与主分支逐路径完全一致；在已解析绝对目标均位于本轮根D:/CodexHome/visualizations/2026/10/24/01a16bef-15d6-7830-875b-f181b475b4d4内后，使用不带force的git worktree remove安全回收23个目录，23个分支及全部提交保留，本轮树剩余0。主树和其他日期历史worktree未删除；README/reverse-design/通知prompt的既有外部未提交修改保留。

只完成整合JSON/本地引用/差异/归并等价检查，没有重跑技术脚本、SIM/QEMU、构建、历史回放、目标固件、设备或外部服务。没有生产/ROM/配置/分析器模型变更，不推送。以下旧运行/准备记录均为历史，以本节和唯一认领表的停止状态为准；任何恢复需用户明确要求。

## 链条认领与查重规则（2026-10-24新增）

本节补充并优先于下方旧派发/队列规则中的去重做法；不改变当前会话授权的研究范围、并发数或静态限制，不据此启动或停止任务。完整流程与注意事项统一见[逆向工作流程](reverse-design.md)，向现有任务传达的[通知 prompt](chain-claim-notice-prompt-20261024.md)另存。历史快照不是实时运行状态。

**本文件下表是唯一链条认领表，由当前管理窗口单人维护，串行查重、登记后才派发。** 研究者通过报告/消息请求登记，不修改共享表；独立 worktree 中的旧表不能自行授予认领。派发时附最新登记行和管理基线。管理窗口交接时移交最新表及实际任务状态，不能有两个窗口同时派发。

认领按“原件版本/身份 + 具体连接 + 对象身份 + 问题”划分。地址用统一 `0x` 写法，保留旧别名；具体连接列已知函数/callsite/callback/字段与对象来源，未知端写待找及精确问题。任务名、领域、文件名、worktree 不作为独占依据。

### 派发前

1. 查父级 complete、最终验收及近期专项/独立复核，再用地址、callsite、callback、字段、对象和问题查下表。空表或无相同行不证明未研究；相关旧覆盖按需补录，不全量重建历史。
2. 与研究中同链同问题重叠：合并、收缩或等待。与待复核重叠：挂原认领安排非作者复核。与已验重叠：继承证据。共享节点但连接/问题不同：写明差集后可以并行；对象身份或范围不清：标待消歧，先核已有证据，不派重叠取证。
3. 写明已有出处、继承范围、真正增量和相交行，登记负责人/状态/独占范围后才派发。没有真实锚点或无法说明差集则不派取证。

### 扩范围前

发现超出认领连接和问题的新 caller/callee/callback/字段/对象，只保存偶遇锚点，不沿新链展开。研究者提交原认领 ID、新连接/问题、相交行、旧证据和必要增量；管理窗口查重并更新范围或新增关联行后再展开。原有不重叠范围可以继续，新名字或新 worktree 不能绕过这一步。

### 状态与交付

状态使用待补登记、待消歧、研究中、待复核、已验、未闭、暂停。独立复核列在同一认领行，注明非作者复核者及证据；只复查差集和必要继承前提，不把复核当新增研究。报告分列继承、复核/纠正、真正新增、未闭边。

完成、暂停、交接都更新行并保留历史；移交先确认原研究者停止，不按超时自动释放。已验部分与未闭边分别写清，重开须给旧证据不足、新输入/证据及理由。主体已覆盖则收缩，无必要增量报已覆盖并换题，不重复整函数/全资源或旧负搜索，不以无种子推断全局完成。

### 链条认领表

Q-30/Q-31/Q-32本轮S成熟后备补位：Q-27/28/29非作者均停止后取ready S48/S49/S50，分别登记/root/app_serial_downstream_review_01、/root/app_ot_integration_review_01、/root/app_serial_uplink_review_01；独占各同名review-01-0041-20261025报告/analysis和codex/<领域>-review-01-20261025，基线创建时HEAD。成熟段PREP报告605/611/617行，作者138119a/a5abd02/f51ccd0均停；只原4窗1610B/7body3658B(8片段、12B非body不补)/3窗818B及旧根必要接口。Q30新ACKcallback只安装止边；Q31 7vendor未知/09d6同步serializer/同owner身份/框架API止边；Q32 call无busy1/callback写2或3而非清0/旧SDK接口止边。预估3–5/4–6/3–4分，据作者完整278/290/205秒校准；首工具UTC，不扩新body/库/模型。三后备已取走，预调研补下一3真实独立业务阶段，不将未交成果或旧快照充当库存。

Q-27/Q-28/Q-29本轮S成熟后备补位：Q-30/31/32作者均交付停止后，从库存取ready S42/S43/S44，分别登记/root/app_mcu_ota_review_01、/root/app_ddf_review_01、/root/app_rpc_property_review_02非作者；独占各领域review-01/02-0041-20261025报告/analysis及codex/<领域>-review-01/02-20261025分支，基线创建时HEAD。三作者342abd2/e8de704/47653c4已停止，S42/S43/S44初包493/499/505行、成熟动态556/562/568行。只原六新槽1638B+表/六DDF入口1924B/五v3属性入口1074B及各必要已验API接合，不重读旧完成/UART/transfer/Q18共有体，不扩大验证trigger/MCU内部/公共JSONSDK。预估3–5/4–6/3–5分中置信，据完整281/308/221秒作者工时；首工具UTC。S42/43/44从库存取走，S48/Q-30、S49/Q-31、S50/Q-32按138119a/a5abd02/f51ccd0交付动态转ready补回3，不把未交条件当库存。

Q24/Q25/Q26完成触发复核补位（本轮S）：原已备S31/S33/S34边界及作者完整交付构成可直接转派的同认领非作者包，不开新链/不扩范围。分别登记/root/app_publication_review_01、/root/app_report_config_review_01、/root/app_rpc_subscription_review_01，独占各同名review-01-0041-20261025报告/analysis及codex/<领域>-review-01-20261025分支，基线创建时HEAD；作者b2c1453/1890c41/9dc5fd4均已停止。Q24只5窗784B及旧copy/路由接口、eventID恢复归还；Q25只4窗786B/ACK字段/reply，shared error仅API；Q26只13窗2784B/四head/两record族/门/匹配/清链-finalize-reply，genericAPI止边。分别预估3–5/2–4/5–8分，按作者完整238/247/354秒及各复核实测校准；不执行作者脚本/目标/模型、首工具UTC clock。来源/VA/对象沿原三认领行和作者报告，所有unknown保留，未经非作者确认不标已验。为避免空席不再等待重复整理完整已定义范围；预调研改为优先下一3份独立真包并提前条件复核模板（未交作者不计ready）。

Q23本轮S非作者补位：/root/app_subscription_review_02登记后派发，作者97b1af4已停待整合；完整包S-P35在PREP报告402行，独占app-subscription-review-02-0041-20261025报告/analysis及codex/app-subscription-review-02-20261025。只七helper604B/必要root245接合/非对称coverage顺序、全局同型重用与双owned构造；继承旧version/classifier/删除/76B matcher，不扩fanout/旧缺陷/库/真实权限。预测3–5分中置信，据作者完整215秒/技术180秒；首工具UTC clock，基线创建时HEAD。

Q22本轮S非作者补位：/root/app_rpc_action_review_01登记后派发，作者9f9220c已停/合并、三ignored已主树转存。预调研完整包S-P32在prep01报告370行段；独占app-rpc-action-review-01-0041-20261025报告/analysis及codex/app-rpc-action-review-01-20261025。只五窗1658B/两版本result error shared及旧root实参，1custom仅有限推断、JSON/lexer继承止API，不扩真实action/权限并发；ACK/bodyreply返回分层/栈40B借用/ctx槽保留和长度门。预测4–6分中置信，据作者完整284秒，首工具UTC clock；基线创建时HEAD。

Q21本轮S非作者补位：/root/app_named_property_review_01登记后派发，作者5be2e80已停待整合；独占app-named-property-review-01-0041-20261025报告/analysis及codex/app-named-property-review-01-20261025。只820B/root256必要实参、node64B/name内联/value独立、report先于C+d8锁内update/返回仅update、容量不足先新alloc再free旧及失败保留、report栈/payload同步call后撤销；严格排除event a0116ad0，不认证validators语法/downstreamcopy/publication回收。预测3–5分中置信，据作者完整342秒/技术冻结316秒/Q18review182秒；首工具UTC clock，基线创建时HEAD。

Q20本轮S非作者补位：/root/app_subscription_review_01登记后派发，作者6432656已停/合并，独占app-subscription-review-01-0041-20261025报告/analysis及codex/app-subscription-review-01-20261025。只7窗1780B/root245/48有效输入，精确双erase计数/空P先T后释放/aggregate flag0跳5和6/stale先cleanup后dump及unsigned age>78/signed新topiccount<=0差异/type九word+delta；6UNKNOWN原字/4处同族推断限定，不能独立认证ISA，不做旧缺陷/模型/formatter容器内部。预测4–6分中置信，作者起点未知不能算全工时；首工具UTC clock再读，基线创建时HEAD。

Q18本轮S非作者补位：/root/app_rpc_property_review_01登记后派发，作者72a10cb已停待整合，独占app-rpc-property-review-01-0041-20261025报告/analysis及codex/app-rpc-property-review-01-20261025。只7窗1382B/root59/164必要接合，stage浅copy/matcher默认-4004按ID回填/非DID/无额外donebit/result清链时点/error不回复JSON/回调槽保留；4vendor load原字未认证保持未知，不跨a00bb80e/tokenizer/list内部。预测4–6分中置信，据作者348秒采样/成稿317秒分列；首工具UTC时钟再读，基线创建时HEAD。

Q19本轮S非作者补位：/root/app_event_review_01登记后派发，作者1d7890d已停待整合，独占app-event-review-01-0041-20261025报告/analysis及codex/app-event-review-01-20261025。只4窗1566B/root233，owned argv/即时旁路先于锁内record/flush一次最多1/两payload提交后free/非0仅a0116ad0(H,id,0)止边，不推其语义/不和命名属性混owner，9vendor保分账。预测4–6分中置信，据作者268.609秒采样；首工具UTC时钟再读，基线创建时HEAD。

Q16本轮S复核补位：/root/app_ota_review_03登记后派发，作者3972bfa已停/合并、raw已主树转存。独占app-ota-review-03-0041-20261025报告/analysis及codex/app-ota-review-03-20261025。只2182B constructor/adapter/shared与24B表，继承Q08/Q13；核D/URL复制vsT/TLS浅持有/queuefailfreeR/五vendor/六至七槽真实ABI，HTTP close→install+completion而error→sinkclose，通知snapshot止边。不得展开安装/完成/公共HTTP/queue/a010d8ca内部。预测4–7分中置信，据作者可测290秒/复杂度高于308B单段，基线创建时HEAD。

Q17本轮S复核补位：/root/app_network_review_04登记后派发，作者bc4ed02已停/合并、两ignored已主树转存。独占app-network-review-04-0041-20261025报告/analysis及codex/app-network-review-04-20261025。仅三helper560B及record89 caller，核N ready宽度/另ownerG许可枚举及state1特例/probe20B描述API返回、7000单位未知；止a0119638/callback/Gwriter/publicAPI，继承4000ms reboot叶。预测2–4分中置信，据作者166.031秒采样/Q12review130秒，基线创建时HEAD。

Q18必要同链增量登记：get/set两个result实际调用a01adc0e(head,&local_record,status)，为同staged链的匹配/更新身份桥，准先查既有父级/留存metadata的精确入口/extent，再仅同head/record/status正常匹配与字段更新必要原窗；不沿generic list/allocator/clear内部，不跨新owner或全root。主窗精确近期报告/upper领域卡检索无已验本体；新下层若不是这三实参同链更新则止于API并保留未知。a00b7878文本解析wrapper已有旧接口直接继承，不推完整token grammar/不新读a00b7776。

Q15本轮S非作者补位：/root/app_property_review_01登记后派发，作者bfed293已停止待合并；独占app-property-review-01-0041-20261025报告/analysis及codex/app-property-review-01-20261025，基线创建时HEAD。仅三真body1294B/四wrapper130B/024真实consumer的typed收集和延后send阶段，stride明确0x20=32B、count signed门/状态SH-LH/数值copy-stringborrow/flag低byte/consumer容量早退差别/send CR与256门；不执行作者脚本，不展开formatter/MQ/reset截断/云接收。预测3–5分中置信，按作者222秒/Q12review130秒校准。

Q14本轮S非作者补位：/root/app_protocol_review_02登记后派发，作者1f3f86f已停待合并；独占app-protocol-review-02-0041-20261025报告/analysis及codex/app-protocol-review-02-20261025，基线创建时HEAD。仅cmd59 producer与后续Q11 refresh条件接合，核copy请求count与T.count不同、缓存S pointer/loop重读、两u8→item14/15/覆盖mask/同步notify/相等query推进；止copy/通知/调度既验接口，不推即时refresh/67因果。预测2–4分中置信，按作者154.379秒采样/Q11复核144秒校准。

Q13本轮S复核补位：非作者/root/app_ota_review_02登记后派发，作者63dc73a已停止/合并，材料和ignored在主树同路径。独占app-ota-review-02-0041-20261025报告/analysis及codex/app-ota-review-02-20261025，基线创建时HEAD。只M/L/T接合、继承offer/selector与新308B start栈D120B提交，records205/185/271/313/upper-miio-b前提继承，不重计offer新body；止a012193c/表targets，D复制/T持有及完成未知不展开HTTP/sink/安装/取消。预测3–4分中置信（材料<1/对象1/start1/交付1），按作者195秒采样/Q11复核144秒校准。

Q12本轮S复核补位：非作者/root/app_settings_review_01登记后派发，作者6abd0bb已停止待合并，可从settings01作者绝对树只读。独占app-settings-review-01-0041-20261025报告/analysis及codex/app-settings-review-01-20261025，基线创建时HEAD。仅reader a00ab2e8..ab433/默认a00a3a96..3ab5与必要既验writer/算法/消费者连接，不重验FS/算法。核read返回未检查/u32对u16/close后决定/默认SW再SH仅前6B/独立writer新H/注册头与callback止边。预测2–4分中置信，据作者216秒/Q10复核131.3秒。

Q11本轮S非作者补位：Q10复核停止后取S-P10，/root/app_protocol_review_01登记后派发；作者7ab7fd2已停止/合并，材料及ignored原字均在主树同路径。独占app-protocol-review-01-0041-20261025报告/analysis及codex/app-protocol-review-01-20261025，基线创建时HEAD。只核两属性完整u32 setter/两静态槽refresh变化门/反向mask0xb8/SB保留/普通submit和通知低8位；公共wrapper record22继承，止a00a533a/a01951e2，不核响应/物理生效。预测3–5分中置信（定位<1/body1–2/caller1/交付1），按作者采样240秒/Q07复核115秒校准。

Q10本轮S复核补位：作者baeee728已交付停止/合并，非作者/root/app_weather_review_01登记后派发；独占app-weather-review-01-0041-20261025报告/analysis及codex/app-weather-review-01-20261025，基线创建时HEAD。仅358B启动差集及既验getter/URL必要接合，原body functions/6，bind返回1/byte非0双门、四key/长度/返回/默认回写、loc_id与location_id区分。止配置后端/MD5/TLS，不重做setter/天气页，不补文本NUL或全系统时序。预测2–4分中置信（定位<1/原字门1/接合<1/交付1），按作者197.7秒/Q07复核115秒校准。

Q09本轮S复核补位：Q10作者交付停止后取预调研S-P06包，非作者/root/app_network_review_03登记后派发；独占app-network-review-03-0041-20261025报告/analysis及codex/app-network-review-03-20261025，基线创建时HEAD。只核作者675db19四helper716B与record89 caller差集，继承Q06；止a0067c20/a0069356/a0195ce4/a01b3d12调用端，不展开下层或全部writer。材料对象<1、四helper原字1–2、caller1–2、交付1=4–6分中置信，依据Q09采样250.193秒/Q07复核主体115秒；未复核不标已验。

Q08本轮S非作者补位：作者/root/app_ota_research_01已停止，交付111499a24a60977ee8c73cd5bcb3ffaac835b9d7待独立验收；可见采样16:40:53–16:47:57为424秒，起点前阅读未计。非作者/root/app_ota_review_01登记后派发，独占app-ota-review-01-0041-20261025报告/analysis及codex/app-ota-review-01-20261025。只核七槽copy/注册C与T→open整数ABI→write五参/散列先于可能改src[0]→close归还原序，有限helpers及公共止边同Q08，不执行作者脚本，不扩HTTP间接桥/安装/签名/取消。材料对象<1、ABI/写序1–2、close1、交付1–2=4–6分，中置信，参考Q07复核主体115秒/Q06总197秒；实际基线为创建时HEAD。

Q07本轮S独立复核补位：作者/root/app_miio_research_02已停止，ac561dacf470ea380445a9886a42eace223b3537已合并待验，主体314秒；两个ignored JSON已原路径转存/解析/核SHA。非作者/root/app_miio_review_02登记后派发，独占app-miio-review-02-0041-20261025报告/analysis、codex/app-miio-review-02-20261025分支。合批核P=62fc4944初值映射→a011860a正常hook规则/handler→a0110c76错误回复→同P add/delete寿命；Q04安装消费直接继承。有限主体a011860a..a0118711、a0110c76..a0110d7d及既存a0121886/a011f186/a006929a必要连接，不展开JSON/allocator/manager关闭/权限绕过。预计3–5分（定位<1、hook回复1–2、节点/边界1、交付约1），按作者314秒主体与Q06总197秒校准。新基线为本次实际worktree创建HEAD，不改变作者原基线。

本轮S状态补注（覆盖旧Q行运行快照，2026-10-25）：Q-05现存app-ble-review-01正文/检查已交付，198秒限定接受，主窗待整合旧M03措辞；不重复派复核。Q-06旧review01无交付且当前代理树无该会话，确认停止，以新非作者/root/app_network_review_02接手同认领差集，独占app-network-review-02-0041-20261025报告/analysis及codex/app-network-review-02-20261025分支；继承作者和upper旧根，只核注册、s2/s5分离、同global中断/close清槽；预测2–4分短复核，静态限制不变，登记后启动。Q-07旧research02仅预登记无会话/无报告，以/root/app_miio_research_02继续原认领；独占app-miio-research-02-0041-20261025报告/analysis及codex/app-miio-research-02-20261025分支；继承Q04/启动映射，研究a011860a正常hook规则/回复和同对象注册删除生命周期，止公开库。阶段原种子核1–2分、hook/规则4–7分、同对象生命周期4–7分、原字交付2–4分，预计11–20分，中低置信；较旧20–28分向下校准，材料不足立即保存断边不凑量。两席基线5bbc331，新流程commit交付，管理表唯一写入者/root。

## 2026-10-24 23:44 HKT 新聊天三组复核登记（当前）

基线 HEAD `5bbc331ab429fb76e956e50b8081c56f8d278b11`；此前停止/待派/limit文字为历史。当前环境仅有中断，没有关闭/释放代理工具，现树仅主代理；本轮只先建指定三席，不承诺持续补位。不reset/clean、不提交推送，保留全部未提交及ignored成果。复核者使用主仓只读证据及独占新报告/analysis路径，不改共享表或作者成果；不创建需提交/合并的工作树。管理窗口统一整合。

派发前查重：P-16/P-17只合并其待验selector/普通响应差集，继承PR14；P-18只核在线门/初始化/句柄重读/公共timer API接入，继承PR07，不包括S五槽分类；P-19只核creator/首次门/换端口/销毁边界，继承PR12。均与既验前提分界，不新建同题研究。UTC计量起点2026-10-24 15:44:36；派发/开始/结束另记，token仅记录可取得实测，cached input单列，不以预测冒充实测。


实际状态已由本管理窗口核实（2026-10-24本轮补录）：J05/J06/J07盘点均已提交停止，G19与P01作者均已提交停止；当前F11作者与P02非作者复核者已确认暂停新增取证并回报实际链条。G20仅有预建worktree，尚未派发，不能算运行。下面登记不是重新派发旧任务；研究基线保持不动，逐行确认后才恢复对应差集。

本表各行“0041原件”统一引用[ROM目录](../../../roms/CATALOG.md:17)和[最终应用身份记录](application-rehost-complete-0041-20261017.md:7)：AP01 1.0.2_0041，主仓roms/0041/ap01-1.0.2_0041.bin，6,769,704 B，既有SHA256 `972db4c136c7ed9e24a83c07c1a7fd62040ca018b08ca285216d26b1fee3c6b9`，本批代码VA映射file_offset=VA−0x9ffff000。不重算摘要；不是0031、unsigned候选或SIM ELF。每行继承的Evidence保留各自profile，不把不同profile重标成同一份。

|认领 ID／关联任务|版本／原件身份引用|具体连接、对象身份及问题|独占范围／继承范围及证据|负责人／非作者复核者|状态|查重结论／相交行／后续断边及重开理由|
|---|---|---|---|---|---|---|
|Q-30|0041沿CATALOG，基线创建时HEAD|get_down/json_get_down已验root→a00bdb74 poll命令交接/两mode→a00ba712/a00ba4b4/a00ba7c0 result/queue回传接口接合|app-serial-downstream-research-01-0041-20261025报告/analysis及codex/app-serial-downstream-research-01-20261025；完整包S-P45 PREP报告514行，旧root/result state消费者继承，四新1064+174+130+242=1610B必要原窗|/root/app_serial_downstream_research_01登记后派发|正常串行下行poll到result有限阶段未验|与Q27/28/29不同本体；只SDKdequeue有效pending/mode文本JSON输出/方法参数长度/临时borrow/state timeout callback槽/handled返回/queuefallback，止a011f43e/a01a5268/MQ/read/formatterparserAPI，不重做network根/实际MCU执行/ctx总寿命/并发。预计7–11分中低置信，据1610B新四入口/旧root现成，首工具clock、提前即交|
|Q-31|0041沿CATALOG，基线创建时HEAD|旧OT owner两child+8c/+880启动注册→a0112dae事件/a010fd4e callback/a01129be及a0112734→a01137f6/a0110aca/a01109d6周期/解除交接|app-ot-integration-research-01-0041-20261025报告/analysis及codex/app-ot-integration-research-01-20261025；完整包S-P46 PREP报告527行；upper两接入根/dyna_params/SDKcopy继承，七body3658B精确窗见包；a01129be两段中12B不计body不补NOP|/root/app_ot_integration_research_01登记后派发|同owner事件到周期上报/解除本层接入阶段未验|不同Q17网络N许可probe，不重做SDK/F11生命周期。只数字event门/owner字段/changed门/上行字段/idtime周期/schedule ctx/取消重排API/局部资源到SDKcopy；不从事件名猜云鉴权成功，不扩a010d8ca等框架/容器/网络/OTA下层，C/child全寿命/真实timer/并发未知。预计9–13分中低置信，据3658B同owner多阶段/Q26完整354秒，首工具clock、提前即交|
|Q-32|0041沿CATALOG，基线创建时HEAD|旧cmd.call/json_send两根→a00be6d8 call解析构造/SDK接受→a00ba8b2/a00ba536两异步串行回复/ctxbusy复位归还|app-serial-uplink-research-01-0041-20261025报告/analysis及codex/app-serial-uplink-research-01-20261025；完整包S-P47 PREP报告541行，callback literal a00be82a/82e→a00ba8b2真实种子；三新456+226+136=818B必要窗，旧SDKcopy根继承|/root/app_serial_uplink_research_01登记后派发|串行主动请求接受到正常异步reply阶段未验|不同Q30下行poll四窗；共享busy+1fc不推同周期。只正常call参数/方法raw构造/id D busy设定/两callback消息状态输出/doc buffer归还/busy复位返值，止SDK/parser/tokenizer/formatter/传输/真实执行权限/取消/ctx总寿命，不补丢失伪码。预计4–6分中置信，据818B新三body/Q25完整247秒，首工具clock、提前即交|
|Q-27|0041沿CATALOG，基线创建时HEAD|record248 a00661f2..6218注册表a01bb0e8的ota_mcu七槽→六新准备/打开/写入/关闭/通知槽1638B→旧a0074ea2完成槽接口|app-mcu-ota-research-01-0041-20261025报告/analysis及codex/app-mcu-ota-research-01-20261025；预调研S-P40报告459行完整包；继承miio-recovered MCU命令对象/P08/UART/upper已验完成282B，六新边界见包|/root/app_mcu_ota_research_01登记后派发|MCU OTA应用侧正常七槽生命周期适配阶段未验|不同ota_app ctx，不能套F布局或认命令38c对象同ctx；只参数/头配置/内嵌资源/文件接口/信号归还/返回，止a006fade trigger/a00703ce验证/MCU传输和内部固件/API，不重做旧UART/完成槽。预计7–11分中低置信，据1638B六新槽和已验旧完成接口，首工具UTC，提前即交|
|Q-28|0041沿CATALOG，基线创建时HEAD|旧DDF transfer五cache head+298/+2a0/+2a8/+2b0/+2b8正常输入→discovery root level/IDs→a00c6f8e等六新result/error/字段/归还helper1924B→reply及本层cache归还|app-ddf-research-01-0041-20261025报告/analysis及codex/app-ddf-research-01-20261025；预调研S-P39报告446行完整包，upper-miio-b两根/upper176,291各profile，旧transfer956B完整直接继承|/root/app_ddf_research_01登记后派发|DDF缓存消费/正常discovery输出与归还阶段未验|旧transfer/head/node32B不重验，不执行DDF模型/内容；只level选cache/输出字段数组/借用copy/锁/close-finalize归还/return/error槽。shared error/JSON/string/format/allocator/unlink止API，不真假设备能力/云接受/后台来源/并发/全ctx寿命。预计6–11分中低置信，据1924B新六入口和旧transfer现成，首工具UTC、提前即交|
|Q-29|0041沿CATALOG，基线创建时HEAD|get/set_properties_v3旧root同H=ctx+228 stage/matcher→新a00beeb0/a00c59d4 result及两error→旧response serializer/clear；并核a00bb80e请求raw消费114B|app-rpc-property-research-02-0041-20261025报告/analysis及codex/app-rpc-property-research-02-20261025；预调研S-P41报告476行完整包，Q18已验stage/matcher/serializer/clear继承；五新468+440+26+26+114=1074B精确原窗|/root/app_rpc_property_research_02登记后派发|v3同链请求raw消费/三元IID结果适配归还阶段未验|区别Q18普通二IID和Q26四订阅head无默认门，沿Q18同H首-4004 matcher，不重读旧1382B；只ACK/ID/status/raw借用/请求消费/clear-finalize-reply/error槽。a00b55a0/a00b5636格式API止边，不为raw保证深挖库，不实际设备应用/权限/并发/传输。预计5–7分中置信，据1074B新五入口/Q25完整247秒/Q22完整284秒，首工具UTC、提前即交|
|Q-25|0041沿CATALOG，基线创建时HEAD|get/set_property_report_config_v3旧root ctx→get a00c6198/set a00c607e及a00c0b82/a00c0b6e error→ACK字段/JSON/reply借用归还|app-report-config-research-01-0041-20261025报告/analysis及codex/app-report-config-research-01-20261025；预调研S-P33报告380行完整包，upper-miio-b两根/upper26,45原profile继承；四新464+282+20+20=786B精确原窗|/root/app_report_config_research_01登记后派发|v3报告配置请求到正常ACK适配独立阶段未验|Q22 shared error a00bd7fa仅API不重复body/提前验收；不同Q18/Q20/Q21对象，root/tokenizer卡继承。只ID/status/minmax/change宽度/raw借用/getset输出/reply栈descriptor返回/槽临时资源，不认证实际配置生效/后台调度/validators/权限并发/传输，不深挖JSON/formatter。预测5–8分中低置信，据Q22技术259/总284秒和786B双操作，首工具clock、提前交付|
|Q-26|0041沿CATALOG，基线创建时HEAD|四v3 properties/events subscribe/unsubscribe旧root的四head→stage/两matcher→四result/error/两serializer→同head状态回填/清链/reply|app-rpc-subscription-research-01-0041-20261025报告/analysis及codex/app-rpc-subscription-research-01-20261025；预调研S-P34报告390行完整包，upper280/56/50/135根继承；2784B同接口新精确窗口见包，property head+2e4/+30c和event+334/+35c，不套Q18+228或全局graph|/root/app_rpc_subscription_research_01登记后派发|两记录族订阅ACK/归还同接口阶段未验|继承Q18 property stage/genericclear到API，不重验四root/旧parser，eventstage新body；不互套72B/56B记录，两个matcher分别证明。仅staged持有/初值/匹配状态/输出/clear-finalize-reply原序/四error归还/槽；公共JSONtokenizerclear库止边，不真实后台施加/权限异常实验/并发取消。预计11–16分中低置信，2.8KB同接口多callback真实实量，首工具clock，提前交付不凑20–40|
|Q-24|0041沿CATALOG，基线创建时HEAD|Q19/Q21 publication栈D/P→a011c0da(C,D,K) recipient匹配路由/拷贝、a0113340(C,D)→a0116db0即时/a0116b5a event回调→a0116ad0(H=C+dc,id,...)记录恢复/归还|app-publication-research-01-0041-20261025报告/analysis及codex/app-publication-research-01-20261025；继承Q19/Q21生产、Q20stale和旧miio-recovered session a011f9da/a011f86c真合同；五新298+92+202+54+138=784B必要原窗|/root/app_publication_research_01登记后派发|publication路由/持有及event完成恢复独立阶段未验|与Q23 matcher仅API0匹配不同问题/不读其body，eventowner已从S24排除不抢namedprops。只D/字符串copy与callbackctx、tag5/6选择peer、每peer输出/返回消费、eventID状态pending/retry/free/本层失败恢复；不套F11名称owner，generic sessioncopy已有直接继承，不扩transport/crypto/HTTP/MQ/全C析构/graph生产。预调研6–10分，主窗按Q21完整342秒/Q22完整284秒向下校准5–8分中低置信；首工具clock，提前交付不补库|
|Q-23|0041沿CATALOG，基线创建时HEAD|有效sub descriptor→a01189b8/a01189f6/a0118a40 topic type身份匹配，a0118c20指针存在性/a0118c46 DID8查找→a0118b8a(desc)/a0118bd6(DID8)正常owned构造与root重用门|app-subscription-research-02-0041-20261025报告/analysis及codex/app-subscription-research-02-20261025；upper-miio-b supplemental version/classifier/88B布局已完整直接继承，upper245/48 root前提；七新62+74+200+76+74+38+80=604B必要原窗|/root/app_subscription_research_02登记后派发|正常身份比较/查询/owned节点构造阶段未验|Q20删边/stale/type计数独立已验；本题不读其7body/76B peer matcher，继承pair allocator已有owner合同，不重计旧746B classifier/version。只type实际字段/比较宽度/0非0语义、DID8key/指针存在vsdescriptor相等、size/copy/heads-count初始化/borrow终点/root成功重用构造；排除图不完整/旧allocationfailure缺陷/异常、fanout、库/全root。预调研6–10分经主窗按Q21完整820B342秒/Q20复核1780B225秒向下校准4–7分中低置信；首工具UTC，提前即交，不拿旧卡或库填量|
|Q-22|0041沿CATALOG，基线创建时HEAD|已验cmdrpc.action a00bb110/action_v3 a00c0b96装ctx result/error→a00bec0c/a00c5b8c及a00bd924/a00c0b5a，共同a00bd7fa→JSON/status/ctx+64 reply及本层归还|app-rpc-action-research-01-0041-20261025报告/analysis及codex/app-rpc-action-research-01-20261025；upper-miio-a/b根卡和upper297/54独立profile继承，五新676+664+20+20+278=1658B必要原窗|/root/app_rpc_action_research_01登记后派发|两版本正常异步result/error消费输出阶段未验|与Q18 property callback不同问题，不套其staged-list；不重做请求/root/tokenizer和已验cmd.result state/deadline。只实际callbackABI/状态/out值/版本字段/输入borrow/JSON输出/ctx64 stackdescriptor/返回清理，止JSON/formatter/allocator/传输/权限/真实设备action/并发取消；旧tokenizer补充卡继承不深挖。覆盖对象1–2、双result4–6、双error共享寿命2–3、原字交付1–2=8–13分中低置信，据1658B新多版本/Q18外层348秒；首工具UTC clock，提前即交付|
|Q-21|0041沿CATALOG，基线创建时HEAD|正常cmd.props a00ba35a已验root name/value借用→a0116a3a(component,name,value)→a0116900条目update/替换持有及a011c3b0即时report交接|app-named-property-research-01-0041-20261025报告/analysis及codex/app-named-property-research-01-20261025；upper-miio-a根卡/upper records256真root继承；新150+314+356=820B必要原窗，明确排除a0116ad0事件owner|/root/app_named_property_research_01登记后派发|命名属性update/替换和即时report交接阶段未验，完整publication回收仍未知|准备S24原曾误含a0116ad0，派前依据Q19实际H=C+dc事件身份删除，避免错接。只真实component head/entry/namevalue类型/同名替换copyborrow/旧值归还/锁/返回/下游调用端；不读live Q19 flush/event body，不默认与事件节点同一。止a0110984/a011c0da及公共JSON/formatter/queue/allocator，不扩持久化/云送达；旧root不重做，ok不当设备应用。原S24 6–11分中低置信按820B修正范围，提前即交付；首工具须UTC clock记录完整开始|
|Q-20|0041沿CATALOG，基线创建时HEAD|正常miIO.unsub根有效88B descriptor→a011d10e精确/a01abe54 typed aggregate移除→a0113c8a cleanup reciprocal peer/topic图→空对象归还/type注册更新|app-subscription-research-01-0041-20261025报告/analysis及codex/app-subscription-research-01-20261025；upper-miio-b a0115f7e/a011d202根卡及upper records245/48真body，各profile分账；新244+170+738B及必要同图76+220+58+274B原窗|/root/app_subscription_research_01登记后派发|有效正常订阅移除/清理阶段未验|peerhead62fcab94/topichead62fcaba0/mutex62fcaba8，不同N03 UiIFace/Q07 P/Q19 eventproducer。只正常存在peer/topic及无匹配返回、双向边计数/锁/unlink-free/最后对象/type注销/响应status，不重做sub allocation-failure缺陷，不异常权限实验；generic container allocator止API、不展开消息fanout/crypto/全部语法/OTA/无线/manager总销毁。覆盖对象1–2、精确aggregate3–4、cleanup注册3–5、原字交付2–3=9–14分中低置信，约1.8KB私有图多阶段实量，不追公共容器补量|
|Q-19|0041沿CATALOG，基线创建时HEAD|已验cmd.event a00ba444 borrowed argv→a011408a(component,name,argv,n)→a0113f6c/a011c204事件记录/分支→a01af798 flush handoff/本层归还|app-event-research-01-0041-20261025报告/analysis及codex/app-event-research-01-20261025；upper-miio-a根卡留异步flush/ownership、upper records233真实root独立profile，四callee192+286+428+660B仅extent准必要新窗|/root/app_event_research_01登记后派发|正常事件输入到flush/归还独立阶段未验|父级root借用已验不重做；与Q15 UI数组/Q18 stagedproperty ctx228不同对象，不套F11 loop。只name/argv copy保留/record字段时戳/分支锁/flush组织/本层回收/callback ctx，止a0110984/a0113340/a0116ad0调用端和公共JSON/formatter/allocator/queue/transport；不扩真实设备/云接收/认证。覆盖对象1–2、输入保留3–4、flush归还3–5、原字交付2–3=9–14分中低置信，按1566B新callback/多所有权实量，不凑公共库|
|Q-18|0041沿CATALOG，基线创建时HEAD|cmdrpc get/set_properties已验root的72B局部record→a00bb67e staged ctx+228/22c→get a00be8ca/set a00bea78 result和a00bb0c2/a00bb0dc error→同链节点/原value寿命清理|app-rpc-property-research-01-0041-20261025报告/analysis及codex/app-rpc-property-research-01-20261025；upper-miio-a get/set父级明确此所有权/回调缺口，upper records59/164各profile独立；新92+430+404+26+26+308B必要原窗|/root/app_rpc_property_research_01登记后派发|同staged记录输入到回调/归还多阶段未验|不同于Q15 UI B044数组/发送，不重做两个root；只DID/siid/piid/raw值pointer长度的record复制/borrow、parse doc释放边界、callback ABI/匹配状态/输出、清链/值归属/callback槽。shared a00bb6da仅实际回调适配；止JSON/formatter/list/allocator API，不扩a0058386/a01afb26内部/v3/action/云应用/ctx全寿命。父级对象1–2、record值2–3、双result error4–6、原字交付2–3=9–14分中低置信，据约1.3KB新callback/多所有权实量，提前闭合即交付|
|Q-17|0041沿CATALOG，基线创建时HEAD|Q09同N ready→a0067be6(N)，notready/state1 B→a0195ce4(M,N)，触发动作前a0067c20许可；恢复正常ready复位/probe请求/许可→已验caller接合|app-network-research-03-0041-20261025报告/analysis及codex/app-network-research-03-20261025；继承Q09/复核03/record89 caller/miio-recovered6；三callee58+128+374B仅extent准必要原窗；a0069356安排4000ms reboot已有较晚QEMU报告直接继承|/root/app_network_research_03登记后派发|三同生命周期helper阶段未验|Q09只计时/caller已验，此阶段明确止边新body差集；upper领域卡查无合同。只N字段复位/返回/外部门/M=word(N)/probe输入局部借用API，不扩a0119638传输/formatter/socket内部/私有新owner/reset/driver/HTTP/crypto/全writer；不运行QEMU。覆盖1–2、三helper3–5、caller1–2、原字交付1–2=6–11分中低置信，据Q09采样250秒/本560B不同ABI，提前闭合即交付|
|Q-16|0041沿CATALOG，基线创建时HEAD|Q13 a01148bc→a012193c(service,D,table a060fd34,T)构造持有→六槽a0113a76/0/a0113aac/a0113b4e/a0115702/a010f9f8→Q08七槽T/C sink实际业务桥|app-ota-research-03-0041-20261025报告/analysis及codex/app-ota-research-03-20261025；继承Q08/Q13已验/HTTP公共六槽调用侧miio-recovered10，精确24B表定题；constructor1158B/五adapter54+162+92+252+228B/shared a011398a236B仅extent允许必要新短窗|/root/app_ota_research_03登记后派发|正常请求构造持有/六至七槽adapter多阶段未验|Q08/Q13止边现已交付，只有公共前提相交，无活动作者；upper领域卡核无本体，实际取证仍先查已有。只D复制/URL借用/T userdata/入队失败本层回收和adapter ABI/返回/状态/归还；止公共HTTP/TLS/URL/JSON/queue/allocator/hash，不读worker a0123dca、不重做Q08/Q13/安装签名；error a01143de/a01ac65c只调用端不新所有权。覆盖表1–2、constructor4–6、adapter状态3–5、原字交付2–3=10–16分中低置信，据约2KB新窗/多callback实量，不抄308B短项估时|
|Q-15|0041沿CATALOG，基线创建时HEAD|a01950e4/5106/5122/5144 typed wrapper→a0195034 count62fcb044/20槽base62fcb048 stride0x20（32B）→a01b5d70 result/properties_changed→a00a116e发送接口，buffer62fda0a8|app-property-research-01-0041-20261025报告/analysis及codex/app-property-research-01-20261025；whole-private144/159/021真body及024 GET/SET consumer seed；四wrapper仅extent允许精确新原字|/root/app_property_research_01登记后派发|给定有效count下收集/延后消费发送阶段未验；reset/并发/共享buffer寿命明确未闭|旧deferred/F01/Q11仅caller参数，upper-miio-a/b/routing无本体合同；不拿通知caller当云成功。只typed数值复制/string借用/count20门/消费/状态宽度/flag0或1/输出长度早退/正常send持有接口；不展开formatter/JSON/mq；a00a12d0截断不能猜reset，不全局负搜。覆盖wrapper1–2、收集消费3–5、send1–2、原字交付1–2=6–11分中低置信，据约1KB齐材240秒校准，不能称全事务闭合|
|Q-14|0041沿CATALOG，基线3a66026|a00a874e..8756 cmd59→a00a973e..983e缓存source62fcb6c4 stride8→item+14/+15及mask1000/2000→a00a389c同步通知→已验Q11 refresh条件可见性|app-protocol-research-02-0041-20261025报告/analysis及codex/app-protocol-research-02-20261025；真body uart-response-0041-20261023.json#/functions/0/normalized_result ev_6f9f82e5daf0540a1c24a0b85daa2e394785391692765e5e3e100eb7b37ed94c；继承N02/P17/P10/B19/B21/E01/E02必要前提|作者/root/app_protocol_research_02已停/1f3f86f已合并；非作者/root/app_protocol_review_02已停/f067c9a待合并|复核限定接受（142秒，新增纠正0），完整确认未闭|现Q11非作者只读转换器不重叠本writer；旧N02仅51/52/56、P17 63/65、旧14用例不含59。只source宽度/count重读/两字段/覆盖mask/同步借用和refresh接合；不认定某cmd67请求因果确认，不扩MCU/copy/queue/异常回放。覆盖1–2、字段通知2–3、refresh1–2、原字交付1–2=5–9分中置信，据Q11可见240秒/定位完整，不凑预算|
|Q-13|0041沿CATALOG，基线c1b37ca|miIO.ota a01158f6→a010f7e8(manager,type,params,len)→a01148c4(manager)→a0114790(T)，正常任务选择/参数持有/state+50/启动返回与T+48 completion(T,C)|app-ota-research-02-0041-20261025报告/analysis及codex/app-ota-research-02-20261025；upper records205/185真body及313注册前提，a010f7e8 134B/a0114790 308B仅extent允许必要新短窗；与Q08 C+4 sink所有权阶段分开继承|作者/root/app_ota_research_02已停/63dc73a及f935f1c已合并；非作者/root/app_ota_review_02已停/7f8caef已合并|已验（范围措辞纠正1项确认），a012193c异步持有未闭；旧offer/selector继承|旧protocol仅来源/参数/忙态，miio-recovered只HTTP/prepare/tag，较晚精确报告无本启动合同；不能由根收集冒闭合。仅正常参数/manager列表/T选择/启动调用和completion接口，不读HTTP/prepare/sink/file/签名安装/无线/MCU；a012193c止参数返回，新下层未知保留。覆盖对象1–2、两callee3–5、handler接合2–3、原字交付1–2=7–12分中低置信，按Q10约198秒/Q08可见424秒及442B新窗校准|
|Q-12|0041沿CATALOG，基线11c90bc|同pathname a026a21c的a00ab2e8启动load sysconfig.bin→G=62fc9098校验/默认→既验a00ab274 writer回写及G+2/+3消费者接合|app-settings-research-01-0041-20261025报告/analysis及codex/app-settings-research-01-20261025；真body whole-rom-private-20261023-072.json/ev_85099f331255aab9e146bc35df48bcdbe3e38160b9802c06864c877f036f7d00；L03/04/05/06 setter writer、M01/02校验继承|作者/root/app_settings_research_01已停/6abd0bb已合并；非作者/root/app_settings_review_01已停/3e66b96已合并|已验（130秒限定接受），作者216秒，FS保证未闭|072 reader与071已验writer同path非邻接猜测，SIM前提不代原件；限332B init、a00a3a96默认32B新必要原窗及已验writer，注册a00a40c4→a01b2474(,100)只记录不追callback；止FS/算法/GUI，区别Q10位置槽。覆盖1、load默认2–3、消费者/原字1–2、交付1–2=5–8分中置信，据Q10齐材197.7秒及32B新窗，不凑半小时|
|Q-11|0041沿CATALOG，基线816b09d|MiIO属性4/0xe与4/0x11→a009c8a4两缓存62fc91a0/91a4的packed协议位/反向禁用mask→a01b272c(port,mask)普通提交及caller通知；同缓存refresh a009c662|app-protocol-research-01-0041-20261025报告/analysis及codex/app-protocol-research-01-20261025；caller deferred retained functions/1，whole-rom-private-20261023-008.json a009c8a4完整824B/ev_ed7e71f1bd106ab36710c56dfbcad813bb82ce7c1c69484bfd18f4da5eddf6d7，006.json a009c662完整364B；charge-complete records22 submit继承|作者/root/app_protocol_research_01已停/7ab7fd2已合并；非作者/root/app_protocol_review_01已停/1a2651d已合并|已验（复核可测144秒，限定接受），作者可测240秒，完整物理确认未闭|与P14开关/安心充、N01 mode和已验a009cc0c自定义功率不同；E07仅既验wrapper，buzzer-round3只排除蜂鸣用途，不覆盖转换。只两属性与缓存同对象refresh/已验submit接合，止copy/queue/MCU及真实物理生效，不扩全dispatcher。覆盖caller2–3、两槽转换4–6、refresh/submit2–4、原字交付2–3=10–16分中置信，据Q07主体314秒/材料完整，不凑预算|
|Q-10|0041沿CATALOG，基线816b09d|a005a736启动局部a005b8a4..b9b0及真实bind_flag前驱→loc_province/city/district/loc_id读入62fc90a0/90e0/9120/9160→既验a00a0906 getter/a00aab1c URL首次条件|app-weather-research-01-0041-20261025报告/analysis及codex/app-weather-research-01-20261025；真body主树reverse/analysis/buzzer-backlight-0041-20261023.json#/functions/6，ev_dc0e38b0f382799ea2a8e8ad7f21cefc5998b0767ecf38a58cfdebe8add167c3；继承weather-location/deferred/B14/B15运行时setter/URL|作者/root/app_weather_research_01已停止/baeee728已合并；非作者/root/app_weather_review_01已停止/8ccc10d已合并|已验（131.3秒限定接受，新增0），启动全时序未闭|预调研已核完整assembly/pseudocode/raw_ranges非extent；旧天气报告重启初始化未闭，I05/Q09对象不同。仅绑定门、四读入、loc_id失败默认100000/回写及首次getter接线；止配置后端/MD5/formatter/TLS，不重做大initializer/运行setter。覆盖1–2、启动读默认3–5、getter/URL3–4、原字交付2–3=9–14分中置信，依据Q07主体314秒/Q06总197秒；不足20不凑量|
|Q-09|0041沿CATALOG，基线27c4d34|旧record89 netMonitor中同N=62fca7f8及elapsed→a0067aec/a0067b94/a0068854/a0068914四helper→同caller cloud-ready/重连计时分支，恢复正常状态/返回/资源接口|app-network-research-02-0041-20261025报告/analysis及codex/app-network-research-02-20261025；继承miio-recovered §6/§10已验整个monitor局部合同/Q06接入；只四已存callee和同调用点必要接线，止网络/线程/调度公共API|作者/root/app_network_research_02已停止/675db19已合并|已验（非作者/root/app_network_review_03交3718801已合并，211秒限定接受）；四入口716B，完整应用接入未闭|预调研确认旧根明确四helper未全解释且有留存body，主窗报告精确四地址无新增合同；先核pass5已有即继承收缩，不重做5644B monitor/Q06/全部loop，不跨接口凑量。覆盖2–3、四helper5–8、caller合成原字3–5、交付2–3=12–19分中低置信，依据当前Q06技术98秒/总197秒及Q01约12分多阶段；不得将预算当预测|
|Q-08|0041沿CATALOG，基线5bbc331|a006462e..4658复制ROM表a01bb0cc的28B→a0115b84注册/返回存62fcaa08；下载sink a007016e open→a007022c write→a0070366 close，同ctx/file所有权|app-ota-research-01-0041-20261025报告/analysis及codex/app-ota-research-01-20261025独占分支；继承miio-recovered §10 prepare/HTTP/tag、knowledge签名/安装和upper记录157/287/37；有限依赖a00700b6/a00701f6/a0070322及必要已存a00b4f54/a00b5122/a01addc6接口，止文件/HTTP公共API|作者/root/app_ota_research_01已停止/111499a已合并/620f779补修；非作者/root/app_ota_review_01已停/db3e7b4已合并|已验（flags修正1项经确认），全OTA未闭|预调研定位真表/已有body；主窗精确报告检索无sink三入口合同，签名旧文明确下载写入未全追。先核pass2/3/5已有覆盖即收缩，不重做prepare/验签/CRC/board安装/MCU/HTTP/TLS内部，不做安全/异常输入。覆盖2–3、open/write4–7、close3–5、原字交付2–4=11–19分，中低置信；不凑半小时|
|Q-07|0041沿CATALOG，基线5bbc331|既验启动复制a00027d4..5123→62fc2cc0..560f涵盖P=62fc4944，ROMa0004458+0xc初值a011860a→Q04既验六实参消费；正常hook规则/handler回复与add/delete对象寿命|app-miio-research-02报告/analysis；继承Q04/upper-routing和D04已验映射；只新初值hook实际正常逻辑及必要同规则注册/释放，止公开容器/调度，不做权限绕过/安全实验|作者/root/app_miio_research_02已停止/ac561da已合并；非作者/root/app_miio_review_02已停止/18bc212已合并|已验（复核主体115秒，限定接受，新增0），完整接口仍未闭|改变输入明确：Q04只查xref未有低RAM映射；本轮原件24B按既验range映射给初值，不重跑无writer负搜。policy-initializer-seed.json定位；映射3–4、hook ABI/正常路径7–10、同对象规则生命周期6–8、原字交付4–6=20–28分钟，中低置信，类比Q01约12分钟多阶段恢复；真实差集不足即短项|
|Q-06|0041沿CATALOG，基线5bbc331|a006580c..5840连接回调注册→a006cda4正常DHCP/IPv4门→a0066296同链路down/就绪通知，区分a006d260 monitor身份|app-network-research-01报告/analysis；继承mijia-task-dependencies/upper根局部合同/localhost/I05-I06；只正常连接事件到IPv4/断连接线，止DHCP/IP/无线/线程公开API|作者/root/app_network_research_01已停止；非作者/root/app_network_review_02已交付停止，27c4d34已合并|已验（197秒含收尾，技术98秒），无业务纠正；旧01无报告保留；主体覆盖复用，40B关闭清槽差集|app-network-research-01-0041-20261025.md；复核同global handle注册/普通关联和DHCP返回分离/interrupt与close清槽差别，预测2–4分钟（Q04 100秒/Q02 143秒类比）|
|Q-05|0041沿CATALOG，基线5bbc331|MiBLE可靠帧a012511c/a01251cc→role0 a01905be(characteristic,data,len)/role1 a00b4d56(conn,characteristic,data,len)→正常ATT提交ABI/返回/借用与完成边界，必要同连接ingress a0125280|app-ble-research-01报告/analysis；继承upper-mible U01/U02/U03及旧BLE80根，限应用角色适配/characteristic连接/同缓冲寿命，止公开ATT/GATT/无线二进制与公共copy|作者/root/app_ble_research_01已停止；非作者/root/app_ble_review_01已交付停止|已验（198秒限定接受，接口未闭）；role0 UUID16/role1发现handle区别确认|app-ble-research-01-0041-20261025.md；复核覆盖定位1、双角色身份/返回1–2、同步借用/完成1–2、交付1–2=4–7分钟；旧M03纠正需原字确认后补注|
|Q-04|0041沿CATALOG，基线5bbc331|MiIO普通下行0xa01214f8 context+28→policy62fc4944+0xc(62fc4950)，从0xa0064368真实安装与既存xref/初始数据来源恢复正常hook注册/ABI/寿命边界|app-miio-research-01报告/analysis；继承upper-routing六合同、upper-layer及F11/15同manager身份；只同策略对象安装/消费/正常返回/注销边，止公共容器及上游API，不做安全缺陷/异常/权限绕过研究|作者/root/app_miio_research_01及非作者/root/app_miio_review_01已停止|有限输入/调用点差集限定接受，纠正0；4950未知hook未闭，无新writer|app-miio-review-01-0041-20261025.md；100.178秒；上轮六实参合同保留，不把反编译a6目标当第七业务实参|
|Q-01|0041沿CATALOG，基线5bbc331|同S摘要通知0xa00add16..38→普通/安心分类addfc/ae442/ae5ec及后续mask覆盖→PR11五槽输入|app-summary-research-02报告/analysis；继承P18/Q复核、PR11/13/15；限同对象分类/覆写/借用，止公开API|作者/root/app_summary_research_02及非作者/root/app_summary_review_02均已交付停止|Q01限定接受，快照读取时点纠正1项已由作者修正/非作者确认；全接口未闭|app-summary-review-02-0041-20261025.md；UTC16:08:18–16:14:17.964，359.964秒含中断65.240秒；原参数早期snapshot差集26B已确认|
|Q-02|同Q-01|cmd55上游desc基址→0xa00a8ad0/8aea/8b02→desc[i+17]/I+24/I+13及真实条目顺序、count与替换生命周期→P16 selector约束|dock-control-research-01报告/analysis；继承P16/P17/Q复核、E01/E02及UiIFace基础信息；只同描述表正常来源/条目/替换与消费者桥，止MCU/公共copy|作者/root/dock_control_research_01及非作者/root/dock_control_review_02已交付停止|Q02输入来源/count/重建限定接受，纠正0；实际远端条目值/顺序与count语义未闭|dock-control-review-02-0041-20261025.md；UTC16:02:41–16:05:04，143秒；不继续无远端值的同输入静态搜索|
|Q-03|同Q-01|page0x13 W/R/P登记0xa01b0614..0630→0xa00f1b8e DELETE和0xa00ded6c入口→同payload P所有权及正常关闭资源边界|app-history-research-02报告/analysis；继承P19/Q复核、PR12/E06；先既存容器完整析构证据，限同R/P注册/回调/普通关闭，止free/GUI/timer API|作者/root/app_history_research_02及非作者/root/app_history_review_02均已交付停止|Q03差集限定接受；旧P19失败callee措辞纠正1项；P最终归还未闭|app-history-review-02-0041-20261025.md；UTC16:01:10–16:03:29.994509，139.995秒；原字afdbe→a00d7806仅class walker，不证明freeW|
|P-18|0041沿CATALOG，基线5bbc331|0xa00adabc在线入口adc7c→0xa008bd70、adc84→0xa008c2d0及前置门/对象；S+101实际生产者addfc等业务分类；合成在线初始化/业务timer激活复位→P07离线pause的正常接入生命周期|仅app-online-lifecycle-p18报告/analysis；继承P07/PR07、P11/PR11、P13/PR13、P15/PR15；原派发错误补成a00abd70/a00ac2d0，原字更正两目标为公开resume/reset；仅核调用接口/必要ctor/userdata及同S槽分类，止公共timer/LVGL，不追无种子主W退出|原作者已停止；非作者/root/app_summary_review_01已交付停止|本轮限定接受在线接入阶段，纠正0；完整五槽生产/应用接口未闭|app-summary-review-01-0041-20261024.md；75项静态检查；UTC15:45:29–15:48:44，3分15秒，预测6–10分；cached token见本轮快照|
|P-19|同P-18|P12已验ordinary图表panel P+60首次装载门、creator/series初始化与端口换项复位→常规ring读取的生命周期|仅history-init-reset-p19报告/analysis；继承P12/PR12/P10/PR10及charge-complete record19/creator；限真实P字段writer/normal ctor/换项分支及公共chart API边界，不扩T全局reader/库绘制|原作者已停止；非作者/root/app_history_review_01已交付停止|初始化/首次门/换项限定接受；Q03后续纠正失败callee仅class walker，不证明freeW；P最终归还未闭|app-history-review-01-0041-20261024.md；916项含机械检查；UTC15:45:38–15:49:04.656，206.656秒，预测8–12分；来源文件名补全不改行为；新复核02限定已补注P19及复核01|
|P-17|0041沿CATALOG，基线5bbc331|P-14真实cmd63/cmd65提交→普通parser匹配与0xa00a8582对应响应分支→缓存/后续查询/遥测通知，核普通连接控制结果可观察边界|仅port-response-p17报告/analysis；继承P14/PR14、B19/B21/B02、N01缓存/传输；只取普通cmd63/65实际分派及必要payload/active上下文，不扩全dispatcher/MCU/异常输入/公共queue|原作者已停止；非作者/root/dock_control_review_01已交付停止|本轮合批限定接受selector/普通响应差集，行为纠正0；完整端口控制接口未闭|dock-control-review-01-0041-20261024.md；393项含机械检查；UTC15:45:16–15:49:40，264秒，预测6–10分；请求不等执行确认|
|P-16|0041沿CATALOG，基线5bbc331|P-14 safe请求7db0/7fe2读S+4，switch读S+7，反馈5b0e/5b70读S+7与I+24映射；补S两字段真实writer/creator与UiIFace身份桥|仅port-selector-p16报告/analysis；继承P14（待验）及charge-complete/旧detail-knob/E01，限真实constructor/赋值/分派接口与旧5350必要原字，profile未知照实保留；不扩全UI/MCU/公共库|原作者已停止；非作者/root/dock_control_review_01已交付停止|本轮合批限定接受selector/普通响应差集，行为纠正0；完整端口控制接口未闭|dock-control-review-01-0041-20261024.md；393项含机械检查；UTC15:45:16–15:49:40，264秒，预测6–10分；请求不等执行确认|
|P-15|0041沿CATALOG，基线5bbc331|真实ad998/ad9a2→0xa00ad486(S,kind,1,k)开启，与P-07已验关闭mode0/1/2组合；核私有pane/位图/计数/timer副作用接入|仅summary-pane-p15报告/analysis；继承P-07/PR07/P-11/PR11及system-complete#/local_disassembly/0xa00ad486；限实际kind0/1/2与enable0/1，止于公开GUI/timer/颜色API，不重做库/摘要选择/无种子退出|作者/root/p15、非作者/root/pr15已停止|P-R15限定接受pane开关/布局，无纠正；UI活性未闭|旧父级已有互斥可见语义及body，关闭子集已验；差集仅开启原字段/额外状态副作用与开关组合，旧概念不计新；若完整已覆盖直接继承收缩|
|P-14|0041沿CATALOG，基线5bbc331|真实普通详情handler0xa00f61ae的端口开关/放心充动作→实际业务setter/命令提交→反馈/确认，分开mode0x60与port控制|仅port-control-p14报告/analysis；继承charge-complete/旧detail-knob及N01/P02已有模式/反馈；先核旧父级，限真实UI动作到同端口业务请求/应答，不扩全部UI/MCU/库内部|作者/root/p14、非作者/root/pr14已停止|P-R14限定接受请求提交/呈现阶段，无返工；完整确认未闭|mode-control已列f61ae为真实caller，旧SIM含开关/放心充但真实后端由本地服务替代；差集为真实设备端接入，不将旧行为重新计新，P-12仅读历史不重叠|
|P-12|0041沿CATALOG，基线5bbc331|T+0xe/I+0x3c历史writer0xa00a8c1a/0xa00a92a0，经真实普通详情callback0xa00f5288等已留消费者到一个绘图reader，核ring顺序/0x400/复制寿命|仅history-reader-p12报告/analysis；继承P-10/P-02/window-history及charge-complete record19、E07旧ordinary历史覆盖；只核实际reader接线，停止于公开图表API，不扩LVGL绘图内部/时间基准/MCU/全ROM负搜|作者/root/p12、非作者/root/pr12已停止|P-R12限定接受I ring接缝；writer顺序纠正1项已关闭|旧UI历史行为已恢复不重计；差集为新明确ring布局到实际reader的对象/顺序桥，不能仅凭theme名字或同偏移假认；若旧父级完整覆盖即继承收缩，与P-13摘要输出分开|
|P-13|0041沿CATALOG，基线5bbc331|P-11真实ad78c/ad9bc/ada4c→0xa00abbf6(S,mode,1,selected)，补被实际模式选择的设备摘要数据读取/格式/控件输出及借用|仅summary-output-p13报告/analysis；继承P-11未预认证及P-07/PR07；先旧ledger/反编译/必要ROM只核真实参数模式，止于公开GUI/formatter API，不扩全部页面/公共库/主W退出|作者/root/p13、非作者/root/pr13已停止|P-R13限定接受，ANDI一般谓词纠正1项已确认，实际1..4表不变|精确abbf6报告检索仅P07/PR07/P11未验边；P11 ledger无dossier，实际callsite/参数已有；旧3s概念非helper内部认证，若更早完整覆盖即收缩|
|P-11|0041沿CATALOG，基线5bbc331|0xa00ad602(timer)→S=timer+c，S+101五槽/FA-FB游标→0xa00abbf6等设备摘要更新，核普通tick与P-07同步离线调用的私有状态/输出合同|仅summary-rotation-p11报告/analysis；继承P-07及system-complete#/native_semantics/Power_bottom已知3s互斥轮换；允许该callback必要私有字段/设备摘要借用，不扩公共LVtimer/LVGL、主W退出或底座协议|作者/root/p11、非作者/root/pr11已停止|P-R11限定接受选择状态阶段，无纠正；摘要输出由P-13接续|指定旧charge-complete/round4/ui-total未命中ad602，system-complete仅概念说明与ad486末端地址；完整1210B已留ev_9a775.../b636...，只补五槽/游标/输出接线，不将已知轮换行为重计新增|
|P-10|0041沿CATALOG，基线5bbc331|0xa00a805a五相timer→0xa0191746默认表cmd50选择/提交→正常匹配cmd50→0xa00a8c14/0xa00a9298历史采样，核样本时序/时轴接入合同|仅history-sampling-p10报告/analysis；继承dock/B01/B03/B05/B19/B21、P-02/P-R02与window-history；只核真实cmd50调度/样本门和数据身份，不重做历史算法/公共timer/传输driver|作者/root/p10、非作者/root/pr10已停止|P-R10限定接受采样事件阶段，无纠正；物理时基未闭|旧各局部已验，历史真实采样周期仍未知；差集为业务请求到样本的事件关系与名义/实际时基边界，不能把20ms timer或180点当固定秒数，也不做目标运行|
|P-09|0041沿CATALOG，基线5bbc331|模块deinit末0xa005c9e6后同owner延续，与0xa005cbb6/0xa005cbba冷分配/ctx替换之间实际CFG及同loop pending消费机会|仅dock-owner-exit-p09报告/analysis；继承P-06及C07/C08/P-01；限业务退出/重建caller和loop身份，原backend接入需要该边界；不推相邻必达、不重做walker/timer/allocator或缺陷验证|未派作者；无需新复核|候选撤回：C07/C08已核尾部到cad0返回，邻接冷分配非新可达种子|精确地址检索命中P-06及C01，追加查C07/C08已有c9e6后清理到cad0返回，不能按P-06相邻冷代码再派同题；差集为上层模块退出/冷路径的真实可达与owner状态，不以排空未知无限追库|
|P-08|0041沿CATALOG，基线5bbc331|0xa00a56d4 OTA进入→handler0xa00a5810→0xa00a4708正常退出→重新发现恢复普通handler，核应用可调用阶段/回调持有/返回普通通信|仅dock-ota-lifecycle-p08报告/analysis；继承usb-interface-ota、UARTretry、P-01及P-R01；允许正常enter/exit/业务回调槽与ordinary恢复必要静态片段，不扩异常输入/MCU内部/CRC及公共队列|作者/root/p08、非作者/root/pr08已停止|P-R08限定接受OTA应用生命周期阶段，无纠正；U/ready/最终关闭未闭|已有OTA状态/传输局部，P-01仅继承退出复位；差集为正常进入/handler切换/退出的应用接口及恢复边界，不重做已验状态机或缺陷调查|
|P-07|0041沿CATALOG，基线5bbc331|0xa00adabc离线旧非零→新零，在0xa00ae250后child0汇总指示/位清除/业务timer至常规更新汇合，app=s6、index沿E13|仅offline-summary-p07报告/analysis；继承E13、P-03/P-R02；允许同callback汇总写入/业务timer调用参数与必要对象桥，不复核selector/滑动/converter/公共timer或另一theme-online对象|作者/root/p07、非作者/root/pr07已停止|P-R07限定接受离线汇总/timer接入，无纠正|精确ae250检索仅E13未验尾与P-03/P-R02建议；theme-online为另一0xa00ac93c；差集是业务汇总/取消接入，不重开主W退出无种子搜索|
|P-05|0041沿CATALOG，基线5bbc331|cmd50真实writer0xa00a9234→0x62fcb50a latch的读/清/业务请求连接|仅telemetry-latch-p05报告/analysis；继承P-02及旧poll-phase，允许同latch真实引用/状态门及必要业务调用，不重做raw功率/公共队列/全ROM字节扫描|作者/root/p05、非作者/root/pr05已停止|P-R05限定接受写/条件复位阶段，无返工，业务消费未闭|P-02提供真实写者，单点有界引用查重暂无独立latch消费接口；相交P-02只继承写端，P-01只继承停机复位|
|P-06|同P-05|旧initializer0xa005b300..b310以(s3,1,0xa00a8330)→0xa009f9b6，s3业务handle来源/owner与fd0x62fc91b0绑定，至owner stop/close接口|仅dock-handle-lifetime-p06报告/analysis；继承P-01、G19–G28及D10/D12；允许该真实s3的业务创建/存槽/注销caller，不展开公共poll stop backend/driver内部，不重搜所有fd|作者/root/p06、非作者/root/pr06已停止|P-R06限定接受owner/fd接入阶段，无返工；完整关闭未闭|P-01提供实际调用种子；旧G/D已验通用链不重做，任务只补业务owner同一性/开关及归还边界；无close种子保留未知|
|P-04|0041身份沿CATALOG，基线5bbc331|0xa00a417c(value,force)→cmd62、cmd62应答→cmd61；b51e/b516控制半字的真实正常caller/consumer与应用字段对应|仅aux-control-p04报告/analysis；继承N01/NR01；允许同字段正常业务调用者/协议表的必要既有证据和最小ROM窗口，不重做已验set_control16或P-01停机，不扩MCU/公共库|作者/root/p04、非作者/root/pr03已停止|P-R04限定接受不透明控制阶段，无纠正；产品API未闭|N01明确control16/companion16产品语义未知；按实际来源映射API，无证据单位/状态码保留，不以常量10/100猜含义|
|P-01|0041身份沿CATALOG；基线5bbc331|0xa00a3b10/0xa00a557c→模式状态复位与0x62fc9428共享timer，在途cmd57/60及排队mode的关闭/迟到工作合同|仅mode-stop-p01报告/analysis；继承N01/NR01、dock、F01/F02；允许停机直接caller与同对象清理/业务timer必要边界，不扩公共queue/timer/MCU或P02/P03|作者/root/p01、非作者/root/pr01已停止|P-R01限定接受，局部关闭/重新发现可用，完整排空未闭|N01/NR01明确未闭；不重复cmd57/60正常协调；无证据取消/排空不补造|
|P-02|同P-01|cmd50入口0xa00a8b72、历史caller0xa00a8c14/0xa00a9298，raw record→T+4/I+8等正常功率状态→通知|仅power-producer-p02报告/analysis；继承N02/NR02、E01/E02、window-history；允许同cmd50正常记录写入及必要T/I通知，不扩公共历史算法/driver/MCU|作者/root/p02、非作者/root/pr02已停止|P-R02限定接受，正常生产阶段可用，完整遥测未闭|N02明确未核生产；物理单位/跨响应序列无证据保持未知，不重做51/52/56|
|P-03|同P-01|应用0xa00ad07e/0xa00adabc动画门、root+0x4c及+0x50/+0x54缓存mask，0xa00ab628完成callback→后续通知/值消费|仅deferred-refresh-p03报告/analysis；继承theme-total、window-history、E03/E04/E12/E13与N02；允许真实callback/本地mask写读必要窗口，不下探LVGL动画内部/全ROM读写扫描|作者/root/p03、合并非作者/root/pr02已停止|P-R02限定接受机会式刷新整理，新增ROM业务0|旧局部说重放未知，本题接口事件→缓存→完成→下次通知的精确可用性；不得以无直接call推全局无重放，不接N01控制/P02生产或无种子root退出|
|N01（新流程批次N）|0041，SHA及映射沿CATALOG；基线5bbc331|0xa019537a/0xa019530a→0xa01951e2的mode请求，至0xa00a8582普通响应中的控制回写/通知；恢复应用设置模式接口完整本地合同，区分提交与确认|独占mode-interface-n01报告/analysis；继承mode-control、B19/B21及MiIO延后设置；允许同对象cmd60必要应答分支，不扩全dispatcher/MCU/公共库|作者/root/n01、非作者/root/nr01均已停止|NR01限定接受，profile修正已复核；正常协调阶段已闭合/完整接口未闭|按精确入口搜索仅旧mode与deferred已有局部；差集为请求→回写的接口整合/必要未闭边；不接N02项遥测或N03订阅销毁|
|N02（新流程批次N）|同N01|0xa00a8582的cmd51/52/56→item/total→0xa00f4740及UiIFace通知；恢复底座遥测到应用快照的可用字段/更新合同|独占telemetry-interface-n02报告/analysis；继承B22–B26/E01/E02；允许同对象正常字段写入/转换必要依赖；不扩传输driver/MCU或新单位假设|作者/root/n02、非作者/root/nr02均已停止|NR02限定接受，profile修正已复核；捕获阶段已闭合/完整遥测未闭|原字段已有局部合同；本题形成接口映射与增量证据，不能重复把局部成果当新增；不接N01控制请求或N03注册注销|
|N03（新流程批次N）|同N01|0xa01b29a0/0xa01b2966/0xa00a536c与应用0xa005d134、0xa00a79ce、0xa00b076c注册/DELETE；恢复应用订阅接入/退出合同|独占subscription-interface-n03报告/analysis；继承UiIFace与E01–E13；允许注册userdata/必要页面退出callsite；通用链表/allocator替代不深挖|作者/root/n03、非作者/root/nr03均已停止|NR03限定接受，阶段已闭合/完整退出未闭|现有注册/摘链/部分DELETE已恢复；补面向重建接入的完整寿命边界及真实注销种子，不能重跑全ROM负搜；不接N01/N02业务转换|
|G19/6（G27）|0041原件，沿本表统一身份/VA映射|已验0xa009e016/0xa009e01e→0xa00267c0，两次a0作为可写word槽，待找该服务返回地址来源/正常返回及是否能支撑G23稳定槽假设|仅pogo-poll-error-slot-g27报告/同名analysis；先旧dossier/metadata与必要原字段；不扩diagnostic/日志/native系统、counter初始化或异常输入；仅补0xa00267c8→0xa0026784的返回对象来源/必要副作用，旧functions431为38B metadata无dossier；二次增量仅0xa0026792→0xa002671a(0,&out)对out+4写入/返回及必要副作用，旧functions430仅106B metadata无dossier；不展开0xa002661e/diagnostic或全调度|作者/root/g23、非作者/root/a56均已交付停止|已验（G28限定接受，稳定/别名/异步未知）|近期报告仅G23/G24调用形状及未知副作用，无此本体合同；与G19/4共享callee调用端但问题是独立返回地址来源，不重验counter门或宣称同线程两次必同槽。新下层边先报登记|
|J08/10（A72）|0041原件，沿本表统一身份/VA映射|合成A47/A49、A50/A52、A56/A57、A60..A71已有合同，问给定source类型1匹配已注册slash driver、正常open/read/seek/close下D/H/C/cache-buffer/W/O的表示、借用/持有及归还边界|仅reader-driver-lifetime-a72报告/同名analysis；不新ROM/新helper/重跑旧脚本，目标是实际D实例到既有reader通用生命周期的条件连线，未验A69/A71标依赖不提前接受|作者/root/a56、非作者/root/f12均已交付停止|已验（A73仅条件生命周期，不补实际IO/DELETE）|D全局借用、H低word fd+1非可free对象、C/B/O分别持有，slot_base=D−50不可混cache buffer；config重读不折初值，format输出/实际mode1照片/IO及注销继续未知|
|J08/12（A76）|0041原件，沿本表统一身份/VA映射|A74实参桥a005329c→旧a002d770→a01a37d2(S,0,0,fmt,va)，其中fmt为固定/%s、count256流S；待找引擎相关literal/%s分支与S+4/+8/+c间接调用的真实ABI/旧材料覆盖|仅reader-driver-format-engine-gap-a76报告/同名analysis；首阶段仅旧metadata/dossier相关固定format必要片段，仅升级入口[0xa01a37d2,0xa01a3852)128B五参保存/首fmt字节/literal-percent控制，不整engine/任意fmt/输入实验，再准[0xa01a3852,0xa01a38c0)110B真实indirect call/percent入口最小控制，再准[0xa01a38e4,0xa01a3950)108B固定s入口，及[0xa01a4408,0xa01a4430)40B续读/结束控制返回；再准[0xa01a38c8,0xa01a38e4)28B固定s真实回跳门；再准[0xa01a3a78,0xa01a3ad8)96B固定s实际调度；再准[0xa01a3a46,0xa01a3a78)50B实际s回跳门，不读数字余路/整switch，新分支另报|作者/root/g23、非作者/root/f12均已停止；[A77](reader-driver-format-engine-review-a77-0041-20261024.md)|已验（A77限定接受，待复核关闭；%s功能边未闭）|与J08/11适配层不同连接，字符串输出未因函数名闭合；S新writer targets由J08/13独占，不能并行重取同body；保持varargs推进/返回边界|
|J08/14（A80）|0041原件，沿本表统一身份/VA映射|A78明确0xa002b512→0xa000589c(buf+old_count,src,n)，给定有效S/count<=255时n>0且<=255；prefix-char实际n1、suffix后续dst常为buf+1，任意alignment的实际copy域仍未验|仅reader-driver-format-copy-gap-a80报告/同名analysis；首阶段只upper record76旧完整assembly必要dispatcher/已验G03/G04/F17/F18等合同，定位n1及n<=255/alignment分支的最小缺口，仅升级[0xa00058ae,0xa00058c6)24B n1实际dispatcher原字段，其余旧F18端点/record76继承，不重导1080B/任意length或host输入试验|作者/root/f12、非作者/root/a56均已停止；[A81](reader-driver-format-copy-review-a81-0041-20261024.md)|已验（A81限定接受，待复核关闭；其它copy域未闭）|与F11/5仅n4域、G03仅n16/20不同问题；不可把函数同名推广全域，不把src/dst表达式不同当分离/有效证明；S有效容量/分离前提保留，新原字段或helper先报|
|J08/13（A78）|0041原件，沿本表统一身份/VA映射|A74 count256流S初始化字段+4=a002b536/+8=a002b4d8/+c=a002af2e/+10=buf/+14=255；问三个实际callback本体的参数、内存写/计数/终止/返回域，不按slot名先命writer|仅reader-driver-format-stream-a78报告/同名analysis；先旧留存/合同，必要原字段仅三callback与count256给定有效S域，不读格式engine/新copy/helper，不跑字符串输入或target/模型|作者/root/a56、非作者/root/f12均已交付停止|已验（A79仅stream本体，任意n copy仍边界）|与J08/12 parser角色不同、与J08/11只交初始化pointer值；ABI只有本体字段或engine已验调用端支撑时才认证，新callee先报，不由buffer255推实际输出/截断已证|
|J08/11（A74）|0041原件，沿本表统一身份/VA映射|A66/A67已验a008ab4c→a0053252(buf,256,ROM literal /%s,指向suffix的varargs包)，问有效分离NUL输入短路径下实际输出/返回/终止契约的最小缺口|仅reader-driver-format-gap-a74报告/同名analysis；首阶段仅旧a0053252 metadata/dossier/已有合同定位真实参数/下层，仅升级a0053252自身120B正常参数/输出流/返回必要字段，复用a002d770旧32B历史dossier（profile4825）核参数/返回，不新读a01a37d2，不恢复任意格式/全printf，不执行字符串输入试验|作者/root/g23、非作者/root/a56均已交付停止|已验（A75仅adapter/旧桥，不补engine输出）|与A66 wrapper argv不同连接，是原路径输出未闭边；不能由标准sprintf名字替实现，不读IO/allocator/外部服务；新字段/新callee先报登记|
|J08/9（A70）|0041原件，沿本表统一身份/VA映射|A66/A68失败返回都从第二次getter读取error_word交0xa00ea524；问该函数实际比较/默认分支/数值status映射及返回宽度，不以标准enum名补原值|仅reader-driver-result-map-a70报告/同名analysis；先旧metadata/合同（functions3328仅140B/no callees/no dossier），若未覆盖只该纯数值函数必要原字段；不执行目标或输入枚举实验、不读errno getter/IO/其他driver|作者/root/g23、非作者/root/f12均已交付停止|已验（A71限定接受数值表，不命正式enum/IO）|与J08/7-8仅共享opaque调用端，差集为返回数值协议；旧POSIX/LVGL候选来源不认证精确enum/版本，静态分支重建保持signed/unsigned与默认值，非漏洞/异常输入验证|
|J08/8（A68）|0041原件，沿本表统一身份/VA映射|A64实际slot候选D+0x14→0xa00ef55e、D+0x1c→0xa00ef632，继承A50/A52五参read/四参seek及A66 H=fd+1候选；问正常read/seek参数转换、count/position宽度、返回/借用原序|仅reader-driver-read-seek-a68报告/同名analysis；先旧留存/精确callback入口，必要新原字段仅两body正常路径，不读底层IO/copy/errno-map；若旧owner/边界冲突以callback入口/原字为准，不套邻近write owner0xa00ef5c8|作者/root/g23、非作者/root/f12均已交付停止|已验（A69限定read/seek接口，不补下层IO/ABI）|与A50 generic cache/read分流、J08/6 slot写、J08/7 open-close不同连接；不默认off_t/FILE或library版本，不执行IO/设备，不扩dir/write/cache算法；新callee先报|
|J08/7（A66）|0041原件，沿本表统一身份/VA映射|A64已原字段定位D+c→0xa00ef468、D+10→0xa00ef502但整项待A65；继承A47真实(D,pathSuffix,2)/(D,H)接口，问正常mode2 open→H表示/持有→close的路径处理、参数/返回/归还原序|仅reader-driver-open-close-a66报告/同名analysis；先J08/2旧owner/source_paths与既有callee留存，必要原字段只两callback正常body；新增数据仅a06371e4处NUL字符串最多64B、遇NUL即停，及a00ef4a4→a008ab4c的42B格式化wrapper参数/返回，先旧留存；下层a0053252及底层open/close/allocator不新读，D03/F05/F06已验接口直接继承，不执行文件IO，不读read/seek/dir|作者/root/a56、非作者/root/f12均已交付停止|已验（A67限定接受mode2/H编码/format接口）|与A47/A49通用槽调用、J08/6具体槽写绑定不同问题；旧POSIX路径只能佐证家族，不能套版本/标准FILE类型或实机成功。默认五ROM照片mode0保留，不证source1实际运行|
|J08/6（A64）|0041原件，沿本表统一身份/VA映射|A62偶遇initializer 0xa008e77a以s2+0x180形成callback写基址，已验/待复核登记D=0x62fc974c；待证s2定义→该基址是否同D，以及实际盘符/配置/已验read槽绑定|仅reader-driver-slot-bind-a64报告/同名analysis；先A21/A25/A60/A62旧必要寄存器定义/基址及slot写锚点，未准新ROM/全initializer/slot目标body，新原字段仅准[0xa008e536,0xa008e612)最多220B逐短窗寻找s2定义，找到即停；e5da候选s2=G的定义链只补[0xa008e4b8,0xa008e4bc)4B/[0xa008e52a,0xa008e536)12B/[0xa008e5f6,0xa008e612)28B/[0xa008e628,0xa008e6ea)194B必要连续性，跳过正常流外片段；再核已登记slot110B的有效地址B+offset映D字段，不强求B==D、不读target body|作者/root/g23、非作者/root/a56均已交付停止|已验（A65限定接受D字段/four-slot绑定）|与J08/5节点D保存不同连接；D已登记不证明s2+180同对象，A47接口及J08/2 POSIX路径不替代真实slot绑定。不读a00ef468等目标body，不默认五ROM照片mode1|
|F11/12（F32）|0041原件，沿本表统一身份/VA映射|F15同M/L/Q身份已验，L+0x3c配置16B/start已验；待找同配置其它callback在旧worker0xa011e3d6退出段的真实使用及Q归还caller身份/参数|仅miio-loop-exit-gap-f32报告/同名analysis；首阶段只旧master record248/worker195及upper-miio-b必要配置/退出行，先查父级complete/较晚合同，不新ROM/新callback/close body，不预设offset即stop角色|作者/root/a56、非作者/root/g23均已停止；[F33](miio-loop-exit-review-f33-0041-20261024.md)|已验（F33限定接受，待复核关闭；实际quit等功能边未闭）|与F11/4 start/size/mode及F11/9消息正常dispatch不同连接；旧generic退出已覆盖则直接引用不重恢复，同名loop不能合对象，不推实际quit/queued I排空或最终free|
|F11/11（F30）|0041原件，沿本表统一身份/VA映射|F27/F28正常prefix已验，未读0xa010e392→0xa010e43c name臂到common Q首word写端的控制/寄存器变化；问给定同Q/请求7，该正常臂的mode写入/汇合或返回边界|仅miio-queue-mode-name-branch-f30报告/同名analysis；先旧F27/F28与metadata，再仅[0xa010e43c,0xa010e532)最多246B逐短窗到真实汇合/正常返回即停，common prefix只继承；新FS/创建/allocator/driver callee先报，不执行open|作者/root/a56、非作者/root/f12均已交付停止|已验（F31限定4B回环，创建/保持仍未闭）|与F11/10写点初值不同路径；新输入是原明确未读arm，不重复530B函数；不能要求其结果必7，按实际s3/s6变化/位40事实，返回/后续writer未知保留|
|F11/10（F27）|0041原件，沿本表统一身份/VA映射|已验同Q creator0xa005f0b0与Q.size4，F23实际传mode=word(Q)&0x40；待找creator正常创建参数/接口返回到Q首word mode的写入身份，以限定typed调用选择，不预设正式flag名|仅miio-queue-mode-init-gap-f27报告/同名analysis；首阶段只旧F15 creator caller/原件身份和已存必要metadata定位创建flags/word(Q)写端，现仅准creator缺窗[0xa005f10a,0xa005f11a)16B实参及0xa005f122/126→0xa01974de的48B wrapper正常参数/返回，二次只准a0197502→a010e320同Q/flags7到Q首word的初始化字段/正常控制最小片段，旧530B extent无dossier；不展开下层FS/allocator/driver open callback，新callee再报|作者/root/f12、非作者/root/a56均已交付停止|已验（F28限定写点7，不补所有返回/后续保持）|与F11/4 size+18不同字段/问题，与F11/8使用&40不同写入端，旧size4不证明mode位值或无后续writer；不执行queue/file open，不扩文件系统/调度/全heap|
|F11/9（F25）|0041原件，沿本表统一身份/VA映射|将F11/F13/F15/F17/F19/F21及相应独立复核的同L/Q、source=&localI、n4、copy域、Msg.len/out及Msg归还与I分派连接，回答正常typed消息的局部I槽/heap I/内部Msg各自持有和可失效边界|仅miio-invocation-queue-lifetime-f25报告/同名analysis；只合同/原证据必要连线，不新ROM/新helper/重跑作者脚本；F23另一分支及待复核服务不提前当已验，不把不同运行Msg认同|作者/root/a56、非作者/root/g23均已交付停止|已验（F26仅限定域条件合成，不补运行/存储前提）|真正差集是原F11 native队列未闭边在现有size4/copy4/receive证据下的条件合成；不重计功能/字节数，不认证有效存储/对齐/不别名/容量/调度执行/云端或全producer稳定，只给精确前提与未闭|
|J08/5（A62）|0041原件，沿本表统一身份/VA映射|已验选择容器head0x62fc9744/stride槽0x62fc9740；A60待复核初始化write作候选；继承A21/A22的0xa008aec0(list*)→node角色，待找以真实list参数0x62fc9740调用insert-head并将D写node.word0的注册caller身份|仅reader-driver-register-gap-a62报告/同名analysis；本阶段只旧索引对a008aec0的direct-call caller及对应旧dossier最小实参metadata，不新ROM/新反编译/全fsdrv，仅升级已知initializer缺窗[0xa008e768,0xa008e82c)最多196B逐短窗核G+1c4实参/insert调用/返回node.word0保存D，找到即停；其他caller/新helper本体不读|作者/root/g23、非作者/root/f12均已交付停止|已验（A63限定接受注册桥，slots另归A64）|与J08/1选择/J08/4初始化不同连接，A21是别的header G+110/28B payload不能套fsregistry；只筛a0真实G+1c4的insertcaller/节点D保存，未知保持，不能由同helper认同对象|
|J08/4（A60）|0041原件，沿本表统一身份/VA映射|A58旧dossier已知G=0x62fc957c的实际owner/source：0xa005cc1e@cc6c/cc70/cc74/cd62/ced6、0xa005a736@be3a/be58/c8ae、0xa00b2f6c@b2f98；只问这些已知G定义在同owner必要旧指令流能否形成G+0x1c4/0x1c8写入/初始化调用端|仅reader-driver-global-init-a60报告/同名analysis；改变输入为三已知owner旧assembly必要寄存器定义/用途，A58只metadata不足直接继承；不重读a005a8f4栈对象消歧、不新ROM/全fsdrv/全ROM扫描、不扩G其他字段；必要旧增量仅已验a005cd36→a008e3ac的A21/A22/A25/A26留存中与G清零/两槽初始化直接相关行，旧片段缺失已定位后，仅准新原字段0xa008e4c4..0xa008e612（不含终点、最多334B）逐短窗寻找两槽初始化地址构造/实参，既验G/s4基址继承；定位两槽端即停，不读新callee/整initializer|作者/root/g23、非作者/root/a56均已交付停止|已验（A61限定接受两槽初值writer）|与J08/3相交G引用metadata但问题/证据层不同；只从实际G锚点沿必要旧指令核两槽初始化callsite，无slot/注册身份即保留断边；不是重复旧负搜索或全global重建|
|F11/8（F23）|0041原件，沿本表统一身份/VA映射|F13已定位0xa0197a8e正常−1 send服务的另一0xa0131920等待服务连接，F21揭示flag0x62fc6034对取M来源的分支；问该实际send分支如何取得M并保留source到copy|仅miio-queue-send-wait-gap-f23报告/同名analysis；首阶段只旧F13 caller/evidence必要行定位flag门、实际callsite/a0..aN及outM、成功返回到copy连接，不新ROM/下层body首阶段禁止；现仅准缺caller[0xa0197ad2,0xa0197ae8)22B及实际0xa0197af8→0xa0131920(K,word(Q))正常状态/返回的必要200B服务前缀/路径，不预设outM；无新的等待/调度callee本体|作者/root/a56、非作者/root/f12均已交付停止|已验（F24核心接受；caller范围纠正1/伪码原序精确化1）|与F11/3只交copy发布端，与F11/7取M快速来源不同连接；不假设MiIO线程必走某flag值、0xa0131920名称证明等待行为或当前typed调用已成功。具体下层增量先报登记|
|F11/6（F19）|0041原件，沿本表统一身份/VA映射|已验同loop入口0xa011e3d6及Q=word(loop+0x18)，问正常接收端把队列内容交局部I到既有dispatcher前的实际服务/实参/返回门及与Q的身份连接|仅miio-queue-receive-gap-f19报告/同名analysis；首阶段只旧record195同函数/必要metadata定位receive callsite，不新ROM/新callee；继承既有type1 callback/free语义不重复，具体新原字段仅准0xa011e5fa→0xa005f508(Q,&localI,timeout)适配层对输出槽/长度/timeout转交及返回；timeout正常10000或word(firstTimer+4)来源直接继承，不展开timer；仅补正常finite实际a005f59e/5a2→a0197954(Q,out,n,&deadline)对out/n、消息copy/归还调用端必要字段；−1的a01978a2不展开，0xa005f56a转换仅按既有th.mula局部规则条件解释；二次增量仅正常非空0xa0197a36→0xa01319e8(K,word(Q),&localMsg)的Msg来源/out保存/length保留与0xa0197a6c→0xa0131b68(Msg)正常归还分支/调用端，先旧留存后必要字段，新下层服务不展开|作者/root/f12、非作者/root/g23均已交付停止|已验（F20限定接受finite/nonempty，不补实际消息/容量）|与F11/3 send、F11/4 init、F11/5 copy4不同连接；旧generic dispatcher不证明下层如何复制/归还internal M。无真实callee前只盘点，不全队列或超时/取消扩展|
|F11/7（F21）|0041原件，沿本表统一身份/VA映射|F13已验0xa0197acc→0xa01318de，非零返回M后0xa0197b1a以M交下层copy(M+0xc,source,n)；问正常候选M来源/持有及可定位的存储容量边界|仅miio-queue-message-source-f21报告/同名analysis；先旧callee/dossier/index与caller实际实参，再只核本callee正常返回来源必要原字段，新allocator/调度/等待callee先报，不扩全heap；必要增量仅0xa01318ea/18fe→0xa010d70e(gp+0xb8或gp+0xc0)正常节点取出/返回合同，先继承G11调用角色和旧留存，再必要原字段；0xa002fcc8仅332B请求调用端不读allocator|作者/root/a56、非作者/root/f12均已交付停止|已验（F22 helper本体；F24已接受F23 caller范围纠正）|与F13只共用opaque调用端，本题差集是M来源/正常持有，不重验copy4/接链；不能由M非零或queue size4推存储有效/不别名/容量。新callback边保留原序|
|F11/5（F17）|0041原件，沿本表统一身份/VA映射|F13已证0xa0194a14/18→0xa000589c(M+0xc,source,n)，F15旧caller创建候选n=4；只问该helper在n=4且src/dst正常有效word对齐时的必要读写、是否持有参数及返回|仅miio-queue-copy4-f17报告/同名analysis；先旧G03/G04及其他copy合同/留存，已有16/20B不覆盖4B；若4B未验，只取到n=4路径必要旧assembly/原字段，不重导1080B/任意length/未对齐算法|作者/root/a56、非作者/root/f12均已交付停止|已验（F18限定接受n4有效对齐域，不补目的存储前提）|主窗G03/G04只见16/20B明确域，“copy4”另有业务helper需消歧；新n4是已定位候选创建输入，差集是实际小长度路径，不解决F11真实loop身份/源目标对齐及容量；不扩heap/全libc|
|F11/4（F15）|0041原件，沿本表统一身份/VA映射|F11已验type1跨线程caller的Q=word(loop+0x18)，F13已证size=word(Q+0x18)经0xa005f464/0xa0197a8e传给copy服务；待找同Q的创建/初始化→size值身份桥|仅miio-queue-size-gap-f15报告/同名analysis；先旧event-loop caller/constructor/queue初始化留存metadata，不新ROM/不扫全queue；新窗口仅准0xa005f0b0 creator入口/正常成功Q字段和输出槽必要原字段，实际候选来自旧record248的a0065438..a006544c，s7=M+0x128与输出槽s7+0x18；不读分配器/queue开服务；二次增量只准0xa0110708/718→0xa01ab55a正常ctx+4=L存槽及入口参数必要原字段，旧callbacks/start/user身份桥直接继承，不展开log/memset/callback|作者/root/f12、非作者/root/a56均已交付停止|已验（F16限定接受正常setup/attach的身份/size4）|继承F11/F12/F13调用及对象，差集是同Q的size写入身份；没有4B初始化证据，不能由a1=&I推4B。与F11/3copy消费不同连接，不接allocator/wait/整个事件系统|
|F11/3（F13）|0041原件，沿本表统一身份/VA映射|0xa011e33e→0xa005f464(queue,&局部I指针,−1)，问正常send如何消费a1、同步复制pointer word还是持有栈地址及返回原序|仅miio-native-queue-f13报告/同名analysis；继承F11/F12的I构造、type1提交和caller实参；先旧留存callee，再必要稀疏原字段，不扩全队列/transport/heap；本轮扩范围登记仅−1路线0xa005f480/484→0xa0197a8e(queue,原a1,word(queue+0x18))：恢复该callee对源pointer与长度的正常消费/复制/持有，先旧留存再必要字段，不展开定时0xa0197b32；二次必要增量仅0xa0197b1a→0xa01949f0(a0=word(word(queue+0xc)+0x18),a1=候选message,a2=原源pointer,a3=原长度)对a2/a3的复制或持有/返回；0xa01318de/0xa0131920保持opaque，不扩allocator/wait/调度|作者/root/f12、非作者/root/g23均已交付停止|已验（F14限定接受接口/顺序，copy实际4B域另题）|精确地址在近期报告仅为F11/F12未闭建议，未有本体合同；与F11/1只共享queue调用端，差集为native adapter对局部pointer的消费；新callee本体先报锚点|
|G19/5（G25）|0041原件，沿本表统一身份/VA映射|0xa009e0e2→0xa009e0e6(backend_fd,C,S,3,high,local16+(index<<4))，只问实际op3下对record的复制/持有、entry字段、返回及条件下一跳|仅pogo-poll-op3-g25报告/同名analysis；继承G21/G22 op2共用前缀/copy/zero和G23/G24条件调用端，不套op2最终字段；只核op3真实差集，不展开native/fallback诊断/其他op|作者/root/g23、非作者/root/a56均已交付停止|已验（G26限定接受，语义纠正/新增body0）|与G19/3共享函数但实际op输入不同，G11只覆盖fallback；近期G23/G24只有op3 callsite无body合同。新callsite/递归仅记录，不扩服务/初始化/完成全闭包|
|J08/3（A58）|0041原件，沿本表统一身份/VA映射|J08/1已验word(0x62fc9744)为head、word(0x62fc9740)+4为动态next偏移；待找两槽初始化/注册writer→N.word0=D的真实身份桥|仅reader-driver-writer-gap-a58报告/同名analysis；继承A56/A57选择144B及A47接口；本阶段仅旧留存xref/owner/caller/写入metadata，不新ROM/反编译、不全fsdrv扫描；新窗口另登记|作者/root/a56、非作者/root/g23均已交付停止|已验（A59仅有界盘点排除；真实writer未闭）|与J08/1只共享已验reader容器读取端，差集为writer/注册连接；J08/2 POSIX路径端尚无绑定不能替代。本轮搜索近期报告两槽仅A56/A57读端，无已验writer；无种子不推具体D或slot|
|J05（盘点已结束）|0041原件，见本表身份引用|C06 type8 close→0xa009f972；0xa009f986→0xa009f442(L,P+0x34,0x17)；0xa009f9a8→0xa009e212(L,word(P+0x58))。W=P+0x34且W.fd@+0x24，确认同poll的已存调用/字段种子，非callee本体语义|仅transport-reuse-gap-j05同名报告/analysis；[J05](transport-reuse-gap-j05-0041-20261024.md)，0fa2089整合；盘点新增0|/root/k03已停止；主窗口范围核对，不冒称技术复核|已验（仅盘点定位）|与C06/1、G07/1、G09/1相交已验上层直接继承；新本体问题已移G19/1、G19/2，不再派同一盘点|
|J06（盘点已结束）|0041原件，见本表身份引用|0xa01b6146@0xa01b632a栈D→0xa0111ff6→0xa011f9da→0xa011f86c及0xa005f222回调；旧pending head 0x62fca4c8、32B记录callback+0x10/fd+0x14→0xa01977cc的callback(fd,message,length)已解释。仅筛尚缺copy/retain/对象寿命接入|仅miio-reuse-gap-j06同名报告/analysis；[J06](miio-reuse-gap-j06-0041-20261024.md)，ee220d8；upper-complete records197/91/13/163/278/282与旧miio-rpc reply_matching，盘点新增0|/root/b25已停止盘点，另持F11；无盘点技术验收冒称|已验（仅盘点定位）|原pending三参ABI候选撤销为继承；F11/1只补D复制/持有，F11/2补R/S回调对象连接。与G19的loop名称不构成同对象，不能套fd watcher布局|
|J07（盘点已结束）|0041原件，见本表身份引用|0xa00afd5c→global byte 0x62fc403a；0xa00af262尾部0xa00afa78/0xa00afab0两次读同byte→0x62fcbcc4/0x62fcbcc8。s2=0x62fc402c全局，非timer borrowed app；只筛原字段顺序独立认证不足|仅input-idle-reuse-gap-j07同名报告/analysis；[J07](input-idle-reuse-gap-j07-0041-20261024.md)，327d557；main-knob records1、screen-host-append functions4、guide父级，盘点新增0|/root/l03已停止；主窗口范围核对|已验（仅盘点定位）|与E05/1及guide阈值/唤醒旧合同相交直接继承；userdata候选已撤销。具体精度问题归P01/1，不新派完整timer/idle题|
|C06/1（必要继承）|0041原件，见本表身份引用|type8 handle正常close的0xa009ffbe→0xa009f972，随后pending登记/消费与cb(poll)→ctx+0x198计数释放合同；问题仅作已验入口前提|[C06](pogo-close-dispatch-review-c06-0041-20261023.md)、C04/C08；无新增独占取证|历史作者/独立复核已结束；本轮只引用|已验（原报告限定范围）|与G19/1、G19/2共用close入口，差集是两backend callee本体；不重开timer删除、drain或ctx完整释放|
|G07/1（必要继承）|0041原件，见本表身份引用|0xa009f972的W=P+0x34、mask0x17、word(P+0x58)调用端；stop中的active/loop计数原序|[G07](display-alternate-work-g07-0041-20261023.md)/[G08](display-alternate-review-g08-0041-20261023.md)，仅引用既验stop本体|历史作者/复核者已结束|已验（限定）|G19/1、G19/2继承实参及上层顺序，不能把G07 opaque backend当整stop未研究|
|G09/1（必要继承）|0041原件，见本表身份引用|W+0x14入同fd bucket、W.fd@+0x24、ready→W.callback→poll callback；问题仅保证G19使用同watcher/fd布局|[G09](display-ready-dispatch-g09-0041-20261024.md)/[G10](display-ready-review-g10-0041-20261024.md)|历史作者/复核者已结束|已验（限定）|与G19/1、G19/2共享bucket字段，ready投递不重做；不能外推close后callback已排空|
|F03/1（必要继承）|0041原件，见本表身份引用|0xa0098b4a局部链摘除及F03/F04已验pending/close链合同；G19只引用所需摘链helper|[F03](miio-loop-close-f03-0041-20261023.md)/[F04](miio-loop-close-review-f04-0041-20261023.md)|历史作者/复核者已结束|已验（限定）|G19/1只核W+0x0c/W+0x14节点和loop链的本轮连接，不重验通用unlink/整个close链；不据MiIO名称同一化F11对象|
|G19/1（关联G20）|0041原件，见本表身份引用|0xa009f986→0xa009f442(L,W,0x17)：W=P+0x34、W+0x1c请求mask、W+0x0c更新链、W+0x14 fd桶链、W+0x20比较槽、W.fd+0x24。回答mask清除后两链持有/loop计数/槽变化及返回|pogo-poll-cancel-backend-g19报告/analysis；[G19](pogo-poll-cancel-backend-g19-0041-20261024.md)，bedf291→0ea89ca；必要链helper沿F03/1；[G20](pogo-poll-cancel-review-g20-0041-20261024.md)，821b8e9→91ce915|作者/root/k03原G19已结束；非作者/root/k04提交G20停止|已验（G20限定接受，复核新增0）|与G07/1、G09/1只共享前提；差集为0xa009f442本体状态转换，不恢复整stop/ready，不认证OS成功。G20挂本行只查差集|
|G19/2（关联G20）|0041原件，见本表身份引用|0xa009f9a8→0xa009e212(L,fd=P+0x58)；B=word(L+0x14)、R=word(B+0x114)，同fd剩余W+0x1c聚合、record mask/fd改写；四参0xa010e722与六参0xa009e0e6实参/返回消费。问软件记录/提交边界|同G19独占报告/analysis；继承G09/1 fd桶；仅到下层callsite，不含下层body；[G20](pogo-poll-cancel-review-g20-0041-20261024.md)，821b8e9→91ce915|作者/root/k03原G19已结束；非作者/root/k04提交G20停止|已验（G20限定接受，复核新增0）|与G19/1是同W fd的下游但不同callee问题，无第二作者。R正式类型/栈16B下层复制不预设；0xa009e0e6本体另见G19/3，不在复核中扩展|
|G11/1（必要继承）|0041原件，见本表身份引用|0xa009e0e6的submit_ctx+0x3c=−1 fallback→0xa010e722(backend_fd,op,fd,record)调用端ABI；G11的ADD/ready materializer及G12重读原序纠正继续保留|[G11](display-ready-producer-g11-0041-20261024.md)/[G12](display-producer-review-g12-0041-20261024.md)；只继承既验fallback，不重导initializer/producer|历史作者/复核者已结束|已验（限定fallback）|G19/3真正差集仅非fallback ring分支的实际op2输入/栈记录消费，不再把整个0xa009e0e6称未恢复；不重做ADD/MOD/ready或fallback失败路径|
|G19/3（G21→G22）|0041原件，见本表身份引用|0xa009e320→0xa009e0e6(word(L+0x20),B+0x84,word(R),2,fd,&stack16)，待找服务对六参/栈16B的消费、复制/持有、提交及返回合同；对象身份沿G19/2，不猜OS操作名|G21仅拥有pogo-poll-submit-g21报告及同名analysis；旧extent ev_5ecc1c04…/directcall ev_054cff13…；继承G11/1，限定实际op2及submit_ctx+0x3c非−1分支；[G21](pogo-poll-submit-g21-0041-20261024.md)，e6b1b3a→793e9a4，只到副本/条目/条件提交边界；[G22](pogo-poll-submit-review-g22-0041-20261024.md)，2cee89d→0a9b03a|作者/root/k03 G21停止；非作者/root/k04 G22提交停止|已验（G22限定接受，复核新增0）|与G19/2相交仅六参callsite ABI已覆盖；与G11/1相交fallback已验直接继承。旧证据不足是nonfallback ring消费/复制未核，新输入为e320实际op2/栈16B/B+0x84/word(R)。只核该服务对栈记录/上下文/提交原序与返回；不扩0xa010e722、整backend或OS效果；“栈可失效”仅在scratch副本独立/有效/对齐/容量及寿命条件下成立，不由参数来源不同证明不别名|
|G19/4（G23本轮恢复）|0041原件，见本表身份引用|G21偶遇0xa009e1f0→0xa009dfcc(backend_fd,ctx,original_scratch)，条件为((word(*ctx+0)^word(*ctx+4))&mask)==0；待证该服务如何消费环/tail/副本及返回。不是G19/3栈16B复制问题本身|[G23作者报告](pogo-poll-ring-consume-g23-0041-20261024.md)及同名analysis已无提交整合主树，100个静态锚点PASS；[G24独立复核](pogo-poll-ring-consume-review-g24-0041-20261024.md)90项PASS、语义纠正/新增业务0；保留G21实际条件callsite与旧functions2356 extent/directcall锚点，本轮授权仅此本体差集|作者/root/g23、非作者/root/a56均已交付停止|已验（G24限定接受；可达性/寿命未闭）|与已验G19/3相交仅条件callsite/已复制记录来源，不重验op2条目本体；差集为0xa009dfcc消费ctx环/第三参副本、正常下层提交callsite及返回原序。旧证据只有extent无body合同，新输入为e1f0已证条件和三实参；不预设环满/空，不扩0xa010e722/native service。若回调0xa009e0e6不同op只留实参锚点，不套op2或展开其他op|
|F11/1|0041原件，见本表身份引用|0xa01b6146@0xa01b62fc..0xa01b632a栈D=s0−0x54→0xa0111ff6@0xa0112062的D+4适配→0xa011f9da@0xa011fa1a→0xa011f86c构造R；R+0x20长度/+0x24消息/+0x2c callback/+0x30 user为待原字核字段。经0xa011f610/0xa011f66c建立Invocation I的{ctx,R} payload，至0xa011f84a/0xa011e2f0 type1入队交接。问D/载荷复制或持有及R/I队列持有|仅miio-request-ownership-f11报告/analysis，树re0041-f11基线ee220d8；J06旧upper records197/91/13及相应callee已有body。状态暂存于同名analysis/status.json，无完成证据冒称；扩范围只补旧upper-complete records142/assembly（ev_6bef28…）0xa011f79a门及0xa011f818..0xa011f832：R+0x34、R+0x24两门、payload.R消息归还实参与两次清同+0x24槽。构造0xa011f952写R+0x34已在原差集核过；a5=0跳过写不能凭空推默认零；[F11报告](miio-request-ownership-f11-0041-20261024.md)，08f4bea→4bff422，作者已停止；各新增窗口按本行历次批准留证|作者/root/b25已提交停止；本轮非作者/root/f12已交付F12独立报告|已验（F12本轮限定接受，复核新增0）|与J06相交旧定位/旧pending三参全部继承；与F11/2共用R但本行止于请求构造/入队，不新增响应匹配/清理取证；与G19只共用泛称loop，没有证据同对象，禁止套布局。当前无另一研究者同题；与F11/2共享f718但不同问题：本行R消息提前归还，后者session保存R/借用S消息。已查upper-miio-a/b、routing及近期报告未有该精确条件合同，旧raw存在不当已验；只核两门/调用实参/清槽，不展开0xa018ee34/backend/timer或allocator；F12仅核该行差集/必要旧前提，R对象/R消息/S消息/I分别保留，不认同id唯一或某次运行实例；按本次停止指令保留研究成果和待复核状态，不用管理收尾冒充独立验收|
|F11/2|0041原件，见本表身份引用|已偶遇0xa01ac226→0xa01ac2cc装0xa011f67e、0xa01ac2d0→0xa011f610，{ctx,S}→0xa011f67e；0xa011f6ae从matched session+0x10取R，0xa011f6b4/0xa011f6b6读R+0x30/+0x2c，callback(S+4,user)→0xa005f222读view+0x20/+0x1c。待证明matched session所持R与F11/1构造R身份、S+4临时view/消息借用与callback后0xa0119b72(session)/0xa0119720(S)归还|同F11独占输出；旧upper-complete records142（0xa011f718，payload.ctx/请求R经0xa011f740→0xa0119c8e(a0=ctx,a1=0,a2=R)）、163/278；whole-ROM functions3991/3986/3990/4039/6165仅extent，无dossier。允许必要稀疏原字核0xa0119c8e正常R存槽、0xa0119748正常匹配返回、0xa0119b72 callback后正常归还；0xa01ac226/0xa011f67e仅已有观察字段再核；匹配桥新增仅0xa0119748@0xa0119772设predicate 0xa0116cea、0xa0119782→0xa01ab82c(ctx+0x20,predicate,&criterion)，核kind/id/out槽及遍历回调实参/返回消费。旧index functions3928/6149为46B/54B extent无dossier；0xa0119720先复用upper-coverage历史dossier ev_a02f78ca…，不凭调用名宣称最终释放；[F11报告](miio-request-ownership-f11-0041-20261024.md)，08f4bea→4bff422，作者已停止；各新增窗口按本行历次批准留证|作者/root/b25已提交停止；本轮非作者/root/f12已交付F12独立报告|已验（F12本轮限定接受，复核新增0）|与F11/1共用R但不重做D复制/I入队；与J06旧pending/回执只相交消费端。已先查父级四complete及近期报告，未得三服务本体合同；旧metadata不能回答session+0x10是否保存该R。新证据是f718@f740实际a2=R端和f67e读slot端，允许仅三桥必要原字，不预设同对象，不展开上层transport/response parser/超时/取消/加密或native queue；再遇新连接先报再登记；扩范围二次查重：0xa0116cea（非0xa0117cea）/0xa01ab82c在近期非管理报告未有已验body合同、未与其他认领重叠；只是lookup匹配身份的必要差集，禁止扩通用路由/全链表库；F12仅核该行差集/必要旧前提，R对象/R消息/S消息/I分别保留，不认同id唯一或某次运行实例；按本次停止指令保留研究成果和待复核状态，不用管理收尾冒充独立验收|
|E05/1（必要继承）|0041原件，见本表身份引用|T1=0xa008bc64(0xa00af262,1000,borrowed app)，callback entry timer+0x0c→app；不同于尾段s2=global0x62fc402c。仅作P01/1对象排除前提|[E05](ctk-app-close-e05-0041-20261023.md)/[E06](ctk-app-close-review-e06-0041-20261023.md)|历史作者/复核者已结束|已验（限定）|P01/1不重做timer注册/userdata/DELETE；只核global activity→两counter字段顺序。J07已撤userdata新缺口口径|
|P01/1（关联P02）|0041原件，见本表身份引用|0xa00afd52/0xa00afd56构造global0x62fc402c，0xa00afd5c SB1→0x62fc403a；0xa00afa78 LBU→0xa00afa8c零门；非零0xa00afaa8 SW0@0x62fcbcc4→0xa00afaac诊断→0xa00afab0重读byte→0xa00afabc零门；第二读非零才0xa00afac0 SW0@0x62fcbcc8→0xa00afac4 SB清byte。问宽度/基址/目标/重读与原顺序，新增功能0|input-idle-activity-p01报告/analysis（a09959e整合）；P02只拥有input-idle-activity-review-p02报告/analysis，树re0041-p02基线a09959e。继承J07、guide阈值/唤醒、E05/1，不复验整callback；非作者[P02](input-idle-activity-review-p02-0041-20261024.md)，8e4f7b5→f069c0a，引用P01/1，通知后仅整理提交|作者/root/l03已停止；非作者/root/l04提交停止已确认|已验（P02限定接受，新增0）|与J07同链旧精度候选合并本行；P02挂本行非新研究。已读110B中20条/76B为独立字段记录；无剩余ROM读取。与F11、G19对象/地址/问题无交集；跨调用flag稳定/全writer/真实秒数仍未闭|
|A47/1（J08必要继承）|0041原件，见本表身份引用|source类型1→0xa0107d8e栈W→0xa019d6a4(W,source)保存D到W+4；0xa019d80e..0xa019d828经D+0x0c调用(D,pathSuffix,2)；0xa01b2e44..0xa01b2e50经D+0x10调用(D,H)。A50/A52已验D+0x14 read五参/+0x1c seek四参与缓存持有|[A47](photo-reader-mode-a47-0041-20261024.md)/[A49](photo-reader-mode-review-a49-0041-20261024.md)、A50/A52、A54/A55；只继承接口/缓存/候选局部来源，不认证实际D和具体driver|历史作者/复核者已结束|已验（限定接口）|J08/1不重做构造/读写/归还或来源版本认证；具体D注册/选定绑定仍未证，默认五ROM照片mode0不升级mode1|
|J08/1（盘点结束；A56本轮恢复）|0041原件，见本表身份引用|已知0xa019d6a4@0xa019d798..0xa019d7bc产生/保存D到W+4，之后D+0x0c/+0x10/+0x14/+0x1c为A47/1已验reader回调槽。待找旧留存中选定D的来源、注册链/实例与这些slot目标的真实绑定种子；不预设D身份|盘点[报告](reader-driver-reuse-gap-j08-0041-20261024.md)9aa0d61→a0133ed已整合；[A56作者报告](reader-driver-selection-a56-0041-20261024.md)及同名analysis已无提交整合主树；41项静态检查PASS；[A57独立复核](reader-driver-selection-review-a57-0041-20261024.md)36项PASS、语义纠正/新增业务0，仅0xa019d708..0xa019d796原字段证据层|作者/root/a56、非作者/root/f12均已交付停止|已验（A57限定接受选择窗口；实例绑定未闭）|与A47/1相交已验source前缀0xa019d6ec..0xa019d704及0xa019d798后保存/调用段直接继承；旧rows缺选取窗口、index/functions5912仅extent500B无dossier，盘点不足已具体定位。新证据为定点原字段窗口，不重跑盘点、不整500B导出；只证source→候选D→保存的选择/门/调用端，不预设POSIX D/已注册槽地址；J08/2仍未知，新callee target本体先报再登记|
|J08/2（仅旧证据候选消歧）|0041原件，见本表身份引用|whole-ROM source_paths/321：ROM路径串0xa056b8e0结尾/src/libs/fsdrv/lv_fs_posix.c；references/0..7含0xa00ef4e4且owner0xa00ef468（ev_c7fbfbb3…）及其余已存引用。仅问这些实际owner/旧caller/注册metadata能否提供初始化→driver实例→J08/1选择D的绑定种子；D关系未知|同J08独占报告/analysis；只旧source-xref及对应owner/caller/directcall/历史dossier必要部分，不新ROM/反编译，不导出整个fsdrv/initializer，不把源路径引用当slot绑定；盘点9aa0d61→a0133ed已整合，七owner仅extent/directcall、无dossier/逆caller，另owner未知|原/root/l03仅旧盘点已提交停止；本体研究未派|未闭（旧消歧已结束，无真实注册/slot绑定）|与J08/1共享待找D但新增端是具体fsdrv源路径/owner，已查近期非管理报告精确路径/地址未得已验绑定，A47/1接口/候选来源直接继承；任何新ROM登记/slot本体题先另报差集，不恢复整个文件系统或套默认五照片mode1|

新行使用现有任务 ID；一个任务有数条连接时加 `任务ID/1`、`任务ID/2`，不要另建一套编号系统。每行只登记可区分的连接与问题；证据列链接旧报告，避免复制长篇正文。状态迁移/范围变更在本文件追加简短说明并引用原行，保留可追溯记录。


认领补录决定（2026-10-24）：F11/1与P01/1及G19/1–2无相同对象/连接/问题的并行研究冲突；F11/1可在收到本表管理基线通知后恢复原差集，F11/2保持待消歧且只整理既有证据。P02挂P01/1，只补报告认领注记并提交；作者已停止，不能重派P01研究。G19作者提交停止已核实，G20尚未派，后续只在原G19/1–2挂非作者复核；G19/3未派。未重置进度、未增并发、未重派旧任务。管理者仅编辑本表；README/reverse-design/通知prompt的外部现有修改保留，不撤销。


认领变更（2026-10-24，承接02afb05）：P01/1获P02非作者限定接受，f069c0a整合，作者/复核者均已停止，不重开。G19/1、G19/2正在同认领下G20复核，G19/3不在其复核范围。对G19/3再查重发现G11/G12已有fallback合同，补G11/1继承行后将G21收缩为非fallback实际op2/栈16B消费，登记后才派。F11/2先完成旧body/索引消歧，三服务只有extent无dossier且四父级/近期精确地址未得已验合同；据具体R输入端/slot输出端将新增取证限定为session保存/匹配/正常callback后归还，身份本身仍待证明，不以“同字段”认同对象。主窗口确认与其他行无同题并行冲突后方可恢复该窄差集；F11/1不重做。任何新服务/transport/native queue再按扩范围流程处理。


认领变更（2026-10-24，承接cb4abfd/e961bd1）：G20已提交并整合91ce915，G19/1、G19/2限定接受、新增0；原G20停止。F11/2请求新增lookup predicate依赖前已停止相交部分，经旧报告/metadata查重后仅准0xa0116cea与0xa01ab82c的kind/id/out及遍历ABI；地址笔误0xa0117cea未授权取证。G21新增0xa009dfcc只保留在G19/4锚点，不自动扩大G19/3。为继续其他未闭领域，在已结束P01作者席位下登记J08/1旧reader-driver实例绑定盘点，只旧证据、待消歧、不新ROM；先读表确认后派发，三席上限不变。


认领变更（2026-10-24）：G21作者停止、793e9a4整合，G19/3转待复核，G22预登记非作者/root/k04，只核非fallback副本/条目/条件调用端；G19/4仍仅锚点。J08/1已证旧selector缺选取窗口，source_paths/321偶遇的实际fsdrv路径引用不等于D实例；新增J08/2只准旧owner/caller/xref消歧，与J08/1同席，无新增ROM权限。主窗口查近期报告未有该精确绑定合同，查重/登记完成后才转达，不能按文件名绕过已验A47/1。


认领扩范围确认（2026-10-24，F11/1）：研究者先暂停0xa011f79a及0xa011f818..0xa011f832新worker字段窗口，已查旧manual/较晚报告无对应已解释合同，只旧records142 body可定位。主窗口确认仅“R消息是否正常提前归还及同槽两次清写”是原消息持有问题的必要差集，登记在F11/1后才放行；R对象继续由session持有与S回执消息借用归F11/2，三者不能合并寿命。对a5=0未写R+0x34不补默认初始化，不派allocator/后端。G22仍只原G19/3复核，不因收紧副本独立性前提读取G19/4下层。


认领续派决定（2026-10-24）：G22已停止、0a9b03a整合，G19/3限定接受且别名/独立有效存储条件明确；G19/4以已证三实参/条件登记G23本体差集，不重做G19/3，也不扩其他op。F11作者已停止、4bff422整合，两原认领转待复核并登记非作者F12，不重开同题研究。J08盘点已停止、a0133ed整合；先旧消歧已穷尽所指载体而非全局穷尽，J08/1只把精确缺失的选择窗口升级到A56原字段证据层，已验两端继承，注册/具体D仍未知；J08/2模块路径metadata不足，继续未闭，不借basename扩全部fsdrv。登记完成后分别派G23/F12/A56，最高3席，旧基线不移动。

## 最新跨领域推进指令（2026-10-24）

用户明确：继续推进，上一批无新种子不能当成整体无事可做；用3个subagent从其他未闭领域的既有报告/留存去重盘点，取得真实地址/字段/callback种子后继续研究及独立复核。不重复已验合同，不无种子扩扫，静态限制不变。本节覆盖下方上一批运行0/无新种子的范围快照，历史结论保留而非全局终止条件。

该段记录先前跨领域派发历史；实时状态以上方唯一链条认领表为准。原3席盘点基线a462ff5，后转入研究/精度复核，历史树根D:/CodexHome/visualizations/2026/10/24/01a16bef-15d6-7830-875b-f181b475b4d4。

|任务|agent/独占树|拥有范围|
|---|---|---|
|G19（J05种子）|/root/k03已结束；G20仅预建未派|研究0ea89ca已整合待复核；认领G19/1、G19/2；后继G19/3仅锚点|
|F11（J06种子）|/root/b25；re0041-f11|基线ee220d8不动；F11/1补录确认后可恢复，F11/2先既有证据消歧；新规则通知已回执|
|P01→P02（J07种子）|/root/l03已结束；/root/l04仅整理提交|P01 a09959e已整合；独立复核挂P01/1，基线a09959e不动，无剩余ROM读取|

盘点整合J05 a81502c→0fa2089、J07 fe78562→327d557、J06 561a90e→ee220d8；功能新增0。J06原pending三参ABI、J07原timer userdata候选因旧合同已覆盖被撤下，不能新计。F09/F10编号已有历史event-array分支，未覆盖/复用，MiIO新题使用F11。

盘点不新增ROM读取/反编译，不重跑既有负搜索/历史回放，先父级complete/final/SIM再较晚专项和独立复核，按地址/字段/callback/对象身份去重。首个可靠候选尽早回报；管理者筛重后另派独占研究与非作者技术复核，不把元数据/旧地址当新功能，不按领域单份无种子终止整体推进。所有生产/ROM/配置/模型和执行限制继续适用。


用户最新恢复指令（2026-10-24，本节覆盖下文历史停止/六席规则）：现在开始完成K01、B24、L01三项未验收边，独立技术复核后继续派发任务。本次研究并发为3个subagent，管理窗口另计。已从565dc6e创建三个独占worktree并实际派发；不重置既有进度，不把passed-in-sim或局部验收升级为原ROM完整恢复。后继必须有地址/字段/callback种子并先去重；研究作者不得自验冒充独立验收。

## 2026-10-24恢复运行快照（最新）

根：D:/CodexHome/visualizations/2026/10/24/01a16bef-15d6-7830-875b-f181b475b4d4；首批研究基线565dc6e，后继研究基线1dcbfe6；复核基线分别为L06 b0b1df1、K06 7e633b1、M02 6fef66e。历史冻结快照只代表此前停止时状态。

|任务|agent/独占树|范围/状态|
|---|---|---|
|K05→K06|/root/k03研究；/root/k04独立复核|已整合7e633b1/0bae256，限定接受；本路无新必要GUI种子|
|L05→L06|/root/l03研究；/root/l04独立复核|已整合b0b1df1/2d58179，限定接受；无新必要设置种子|
|M01→M02|/root/b25研究；/root/b26独立复核|已整合6fef66e/a5add8d，限定接受；算法主体旧覆盖，无新必要扩扫种子|

本批运行研究/复核席位0；三席上限和用户续派授权仍保留，没有恢复历史冻结。原三项及按真实种子续派的三项均已独立局部验收。本批报告均未提出新的必要功能种子，当前未另开全GUI/全NVS/全ROM扫描；这不是整体目标完成或证明未知边不存在。

三项未验收边的局部验收已完成：K03→0d8027f、K04→1dcbfe6；B25→dbd788a、B26→be0d2f8；L03→5eb1222、L04→a0c2e62。三次独立复核均新增功能0；K01 count全程不变量/唯一owner，B24物理单位/跨命令稳定性，L01底层实际持久成功/subscriber生命周期仍未证。未把局部验收扩成全组件或ROM完整恢复。后继仅上述真实种子，不重复三项已验窗口。

每路只拥有同名新报告和analysis目录；完整任务书在派发消息。主窗口只整合/范围验收，技术验收交未参与该研究的agent。三项验收后按真实缺口续派，复核新增0。静态与安全边界、局部合同继承和四分报告要求不变。

历史停止指令（2026-10-24，已被顶部恢复指令取代）：快速结束当前任务。停止派发与六席补位，已有成果保留；只整合现有提交并收尾未完成任务，不声称整个ROM恢复完成。历史六路要求由本次收尾指令取代。

## 共同规则

只做0041静态功能恢复；禁止执行固件、连接设备/外部服务、漏洞/异常输入/缺陷验证、修改安全检查、ROM、生产代码、构建配置和分析器模型；不推送。只写独占reverse/analysis和reverse/reports/ap01文件。只用自己的独立worktree和分支，每次shell显式workdir并在PowerShell Set-Location。其他agent同时工作，不撤销他人修改、不改主树或共享索引，不创建下级agent、不自行接后继。忽略ROM/证据/工具从主仓库绝对路径只读访问；不复制工作区，不共享可写数据库或切换全局REA。优先留存证据；若工具不能隔离则报告管理者。临时状态/日志放各自独占analysis目录。只恢复正常原程序行为，不擅自修正。

交付列问题/范围/结论、业务行为、函数地址/参数/返回/调用、必要伪代码结构体状态转换、所有权生命周期、可定位证据与原指令、事实/推断/未知、来源与恢复程度、实际静态验证、断边和一个后续闭包。伪代码不是原源码；保留调用顺序、重读、宽度/符号、返回判断、失败/清理和间接ABI。边界/厂商指令须核原字节，不仅信反编译。标准库只有来源可核实才排除，适配/回调仍恢复；不新增哈希清单/复制清单/机械重复证据。不编译项目，不运行历史回放。完成标准为原问题闭包得到有证据答案或明确可定位断边，不能缩成短helper声称完成；不设函数数量或时长配额；主体已覆盖即收缩，已无必要增量即报告已覆盖并结束。

接近提交提前报告结论、剩余验证、阻塞和后继建议。检查差异、必要验证、明确路径git add、提交、报告commit/验证/未知/干净状态后结束。主窗口作范围验收，技术验收由新独立agent。恢复成果可先整合为待复核；不得自验冒称验收。每项完成即整合补位，从启动时最新管理提交创建新树；运行任务不移动基线。语义冲突交agent；回收仅限干净且已整合worktree，分支保留。用户要求收尾即停止派发。

主仓库：D:/Documents/PlatformIO/Projects/cuktech-ap01-firmware。所有任务初始共同研究基线 ab9716e；实际启动基线为含本任务书的管理提交，在派发消息及运行表记录。

## 当前任务书



## 实际运行快照

用户已要求快速结束：停止补位。全部研究/复核席位已停止；无继续运行或待自动派发任务。

|任务|agent|基线|实际范围|
|---|---|---|---|
|T02|已停止；独立复核完成|52ccc51|接受T01限定复用接入，新增0|
|B23|已停止；独立复核完成|0d98345|接受B22限定分类合同，新增0|
|B24|已停止；线索未复核|0f9957e|cmd56候选写入线索保留，不认证生产者|
|K01|已停止；部分/待复核|934c176|最小报告与入口锚点保留，未完成边明确|
|L01|已中断；草稿未验证|e792632|仅保存脚本草稿及状态，未运行/未验收|
|J04|已停止；纯盘点已整合|2237f36|唯一UI动作种子已交K01；定位支持完成|

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


## 本批继承与增量快照（df35f44启动）

A48继承A46/既有cache合同，只独立复核，新增0；A49继承A47及mode0合同，只独立复核，新增0；D20继承settings-round2b清理接线与D19，只独立复核，新增0。E18只补实际固定分母除法返回合同，不重做时间上层；G17只补NuttX fb候选来源认证，不用LVGL认证替代；H17只找计数writer正常连接，不重搜offset未知。六个agent已由实时状态确认全部running；管理窗口另计。


## 预备完整任务书 L02（有前置，未启动）

独占reverse/reports/ap01/settings-mode-entry-review-l02-0041-20261024.md及reverse/analysis/settings-mode-entry-review-l02-0041-20261024/。

待L01整合后，新独立agent只核两旧caller→a00ab478参数宽度/返回/字段或服务接入与旧覆盖范围，不能先声称持久保存；继承旧settings/guide等主体，不重复大函数/全NVS/GUI，新功能0。

最新管理HEAD新建独占树re0041-l02，分支codex/re-0041-l02，根同K01。REA skill及本文共同/复用/静态安全规则全适用；先已有→行为→局限→精确缺口，四分报告，必要稀疏窗口而非重复整函数/资源/源码/机械账。独占树/输出、不改共享/主树/生产ROM配置模型、不创建下级agent，其他agent同时工作勿撤销。精确路径提交commit/验证/未知/clean，接近提交先报重叠与真实种子。


## 预备完整任务书 K02（有前置，未启动）

独占reverse/reports/ap01/window-slider-entry-review-k02-0041-20261024.md及reverse/analysis/window-slider-entry-review-k02-0041-20261024/。

待K01整合后，新独立agent只核其实际新增UI动作入口/实参/索引门与组件身份，不把factory_ui目录等同GPIO FactoryTestMode关系；已有callee合同直接继承，不扩根析构/全GUI，新功能0。

最新管理HEAD新建独占树re0041-k02，分支codex/re-0041-k02，根同K01。REA skill及本文共同/复用/静态安全规则全适用；先已有→行为→局限→精确缺口，四分报告，必要稀疏窗口而非重复整函数/资源/源码/机械账。独占树/输出、不改共享/主树/生产ROM配置模型、不创建下级agent，其他agent同时工作勿撤销。精确路径提交commit/验证/未知/clean，接近提交先报重叠与真实种子。


## 用户要求快速收尾（2026-10-24）

不再创建新worktree、不再补位、不再开取证窗口。B23/J04/T02已整合；K01/L01/B24已保存已有证据、草稿与明确断边，均未独立验收。已备未派任务全部冻结，不视为待自动启动。最终验收只报告实际完成与待复核，不把部分报告算闭包。


## 最终收尾状态（2026-10-24）

运行研究席位0；停止派发与自动补位。B23/J04/T02已整合，K01为部分待复核，B24只保留未复核生产者线索，L01由管理窗口中断并保存未验证草稿。未派任务书冻结；需用户明确恢复才重新评估范围。未重置任何旧进度，未声称原ROM完整恢复。没有生产/ROM/配置/模型变更，没有SIM、构建、历史回放、设备或外部服务执行。


## 2026-10-24三席恢复批的证据范围

- 继承：早期SIM/final complete、A46/A48/A51/A53、A47/A49/A50/A52/A54/A55、E18/E19、B22/B23与已确认来源差异均保留；CRC主体沿旧USB合同，factory/事件/删除沿E06/H04，不重计恢复。
- 复核纠正：六次独立复核均限定接受、实质语义纠正0、复核新增功能0；L01未验证草稿原字375afc62→374afc62已在L03新产物纠正，不改旧稿或ROM。
- 真正新增：K03祖先状态/class创建/全局引用与count前置精度；B25同对象族字段写入及copy后原序；L03两UI→G+2→通知/旧writer连接；K05请求次数与实际count/初始位置条件分离；L05不同caller/byte/reason4；M01 seed0/G前6B/原样返回连接。旧字节、算法主体、SIM通过不重计。
- 精确未闭：全程count/索引不变量、唯一owner/target与global一致性；DCap物理单位及跨命令时序/实例稳定；subscriber生命周期、全8B正式结构、下层完整服务/真实保存；精确源码版本及既有来源差异。只按局部静态范围验收，不声称整个组件或ROM恢复。

本批全部研究者与独立复核者各自提交并报告树干净；主窗口只做范围、差异和整合JSON/引用检查，不重跑作者/复核脚本、不充当技术验收者。所有改动限reverse/reports/ap01和reverse/analysis，未改生产/ROM/配置/分析器模型，未执行SIM/构建/历史回放/目标固件/设备/外部服务。
