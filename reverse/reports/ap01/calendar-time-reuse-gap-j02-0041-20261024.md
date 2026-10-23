# J02：日历/时间已有成果与实际缺口盘点

2026-10-24；基线 `34ff6ba`，独占分支 `codex/re-0041-j02`。**本题主要行为已有覆盖，没有必要新增的业务恢复种子。** 旧weather-calendar的parent X11与time handler pending均有父级/后续留存，不能据此重新派发日历或时间数字菜单。新增ROM功能0、技术验收/争议裁决0；本报告仅盘点既有证据，不宣称日历库或ROM全部完成。

采用 [reverse-engineer-anything 技能](C:/Users/cogic/.agents/skills/reverse-engineer-anything/SKILL.md) 的既有证据优先规则。未读ROM、未新增反编译/原字导出、未建REA target/database；无SIM、构建、回放、设备、外网或下级agent；只写本题报告/analysis，不改主树共享、生产ROM、配置、模型或他人文件。本文的地址和行为均来自旧材料，不是本轮重新技术认证。

## 继承结论：已有出处→行为→局限→精确缺口

主仓只读前缀`R=D:/Documents/PlatformIO/Projects/cuktech-ap01-firmware/reverse/rehost/`。以下R路径均指已存在原材料；[reuse-index.json](../../analysis/calendar-time-reuse-gap-j02-0041-20261024/reuse-index.json)保存必要JSON指针/状态/旧地址索引，不复制原字节、dossier、源码或完整资源表。

|已有出处|已解释行为/证据层次|局限与当前处理|
|---|---|---|
|[最终应用验收](application-rehost-complete-0041-20261017.md)、[功能矩阵](application-function-matrix-0041.json)|Date overview/detail及Time overview/format四creator的SIM家族场景均passed-in-sim、remaining=[]；最终同候选502步/99图、可见30步/15图|SIM家族场景与服务验证，不是每条ROM分支或硬件执行证明；不能从全通过推出全部来源/ABI已认证|
|R`weather-calendar-complete-0041.json#/calendar`与`#/evidence/0..4`|旧原ROM反汇编已定位subtitle入口`a00eefa8`、Gregorian→lunar `a01acf40`、solar/lunar festival `a00eee7e/a00eeee4`、term `a01aceb6`、day-number `a00eee2a`；已有日期表、优先级、闰月/除夕解释|已有算法/表解释，不按“安全SIM”重新视为未恢复；若今后要求机器ABI独立认证，应从这些明确旧窗口复用，而非重导整日历库。本轮不验算/裁决算法|
|同complete`#/calendar/geometry`及`#/evidence/19..34`|overview日期map/constructor/draw，detail constructor、row/text接入已有定位；例如`a00f0e52`与`a010df3e/a010e0da`|布局和资源消费已留，不重建整表/几何。旧离线窗口是范围证据，非所有显示时序/当前执行观测；本轮没有找到需要推翻的具体接入缺口|
|同complete`#/calendar/bounds,timezone,rtc_boundary`，`#/evidence/3,5..8`|旧材料明确原converter无边界门；localtime可受TZ影响，ROM回退`UTC0@a01c1108`；term使用低32秒，前1970可绕回且year匹配失败；浏览不写RTC|此处分别是旧ROM解释与SIM政策，不能混成“ROM安全处理”。UTC0是已证回退语境，不认证设备实际TZ。SIM安全边界不证明原程序越界行为|
|R`calendar-complete-verification.json`及complete`#/verification/result`|81772天、1888-02-12..2111-12-31、闰月/除夕/节日/节气锚点已有校验；scope明示algorithm/ROM tables only|历史宿主校验和重建算法结果，不是本轮运行，也不替代ROM调用ABI；不重跑农历测试或提取表|
|R`system-complete-0041.json#/callback_branch_audit/time_a00b3252`与`#/local_disassembly/0xa00b3252`|继charge/controller分工后的实际留存：screen23，selection42/43/44，key19/20限界、key10选24h/12h/返回；296条旧原指令。既有whole-ROM extent924B及dossier已定位|这已覆盖旧weather complete所称“charge-owned numeric handler audit/controller integration”。事务持久化/miio传输由SIM服务替代，不据此说物理RTC/云端已核；不重新恢复菜单|
|R`photo-evidence-round3.json#/time_options`，main-knob round2，pass3 creator及[round3报告](application-rehost-0041-round3-20261016.md)|内联format creator`a00b0dd6`、list `a019471a`、24/12/返回行、字体/checkmark资源已有；00:37与12:37四位数字SIM像素验证已有|大数字像素比对是指定离线场景，不是整页/ROM更新时间全等。checkmark坐标表`62fc54d0`当时未映射，不能当成可直接追写者种子或“整个菜单未恢复”|
|[factory-reference-map](factory-reference-map-0041-20261020.md)日历两C路径项|`lv_lunar_calendar/lv_calendar_ck.c`与`lv_comp_calendar/lv_calendar_comp.c`仍写“待补函数关联”，同时明确已有日历行为/测试|这是路径→函数归属/来源账空白；不能把0关联误读成0算法，也没有真实xref足以派“找完整日历实现”|

## 本轮复核或纠正：旧pending必须回到父级

这部分是**盘点状态纠偏**，不是ROM语义纠正。

1. Weather complete顶层`status`和`remaining[0]`仍写latest parent build/X11 pending，但同文件`parent_runtime_verification.status=passed-in-sim`已指最终候选；R`complete-nuttx-sim-verification.json`为passed、502步/99截图，`complete-live-verification.json`为passed、30步/15截图，与最终报告一致。矩阵四creator的remaining均空。不能再次派“补日历X11验收”。
2. `remaining[1]`/`time.detail`把time数字handler交charge/controller，而不是断言全历史未恢复。按地址查询后，实际完整分支审计位于sibling system complete。`a00b3252`旧local_disassembly从入口到`a00b35ec`共296条；whole-ROM既有extent为`a00b3252..a00b35ed`924B，dossier=`ev_34b0faac07e2714b4fd24afebd2bf9a900dd9d56247e44b725c9c90e80abc503`。这是既有证据，不能重新记作新增发现/恢复。
3. `remaining[2]`是SIM边界声明，不是三个空白算法：safe lunar bounds由SIM guard实现；defaultUTC0及低32秒对应旧ROM专门窗口；host RTC/冻结照片场景来自宿主共享时钟替代。[round3报告](application-rehost-0041-round3-20261016.md)已明确普通启动用宿主RTC、固定1970-01-01 00:37仅对照、不写系统时钟。不能用这些替代政策抹去原件已有解释，也不能把它们升级为原件硬件时间来源证明。

本轮按已知地址及字段定位旧JSON、pass3和近期报告，不从旧pending或单份round4局限重开。最终ZIP没有必要增量问题需要回答，故未读/解包其成员；所有SIM边界已有complete/父级明确证据，不为盘点重复读取源码包。

## 真正新增：四类证据裁定，新功能0

|类别|本题裁定|
|---|---|
|已有原字节/已复核合同|H13–H18/E16–E19时间源、selector和除法范围全部直接继承且排除重做；旧日历complete的离线原指令作为可定位旧证据保留。两者认证强度不同，不统一叫本轮验收|
|旧反编译/窗口需局部核时|pass3内联creator、round3资源、system handler旧dossier可复用；provider `collected-not-implementation-reviewed`标签不是此前没有行为审计。若需要进一步ABI证明，应指具体字段/调用点，当前未形成必要新题|
|SIM/照片/安全替代|最终通过证明SIM实现/服务流程；81772天校验、截图及像素比对各有明确范围；hostRTC、越界guard及服务事务不能证明ROM硬件/边界/云端实际行为|
|未检到真实种子|calendar路径归属、RAM checkmark精确坐标来源、正常设备TZ/RTC运行来源仍有限制；已有未闭time1 ctx78安装继承H10无种子结论，不沿其重新搜索天气timer，更不重开counter/offset writer|

新增ROM功能、源规则、反编译/原字导出、源码/资源提取、技术争议裁决均为0。主要日历/时间数值转换与显示接入的既有覆盖已足以避免重复派发；本题提出的必要增量建议为 **0项**。这不等于完整日历库、所有来源或设备运行生命周期已认证。

## 未闭精确边、重叠与实际验证

保留的边界是：精确ROM源码/版本/编译配置、部分C路径到函数归属、原硬件/实际TZ/RTC行为、RAM资源来源与真实运行时序。它们不因SIM通过消失；但本轮没有得到可合法缩成新正常行为闭包的具体writer/xref/安装种子。没有把“未查到”当“不存在”，也没有为填槽扩扫全ROM/全日历库。

重叠排除：不做天气分类/字段显示；不做H13–H18/E16–E19已核时间源、ID0/1、固定分母、无种子writer/offset；不跨用H08/H09/H10的time1上下文与正在I03研究的Time2 type2f生命周期。J01的charge领域复用盘点独立负责其他充电数据，本文只引用已存在time格式handler关闭旧分工pending。

[audit_reuse.py](../../analysis/calendar-time-reuse-gap-j02-0041-20261024/audit_reuse.py)只读旧JSON，核四creator状态/空remaining、两个父级验收计数、旧calendar校验范围、time handler的296条留存/924B索引及地址种子；输出必要reuse索引，不复制指令或表，不执行任何历史验证器。JSON解析、报告链接、`git diff --check`通过。此为有界复用盘点，管理者决定是否基于今后新种子派发，本轮不自行接后继。
