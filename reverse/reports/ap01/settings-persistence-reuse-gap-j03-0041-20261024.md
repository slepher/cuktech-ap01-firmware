# J03：正常设置持有/保存的旧成果复用与窄缺口

2026-10-24；基线 `09e11d0`，独立分支 `codex/re-0041-j03`。**新增功能0、新增ROM字节/反编译0。** 设置页面和SIM保存服务已有最终验收；原ROM的亮度、蜂鸣与地点设置也已有字段/读写专项合同。不能把SIM事务回滚推广为ROM存储ABI，也不能将旧reference-map的“SystemSettings关联0”或早期剩余事项直接当成当前全部未恢复。本轮只留下两条同类普通状态setter的可靠旧caller/extent种子，建议优先一个闭包，不接管初始化、动画或Wi-Fi缓存更新。

采用 [reverse-engineer-anything skill](C:/Users/cogic/.agents/skills/reverse-engineer-anything/SKILL.md) 的留存复用/事实边界规则。仅读已有报告、JSON与最终ZIP两个明确文本成员；未读ROM、调用反编译器、重导body、运行固件/SIM/模型/构建/历史回放、访问设备/外网或创建下级agent。只写独占报告/analysis，未改主树共享文件、其他树、生产代码/配置/ROM/模型。

## 继承结论：已有→行为→局限→真实缺口/种子

|已有出处|已恢复的正常行为|证据局限与本轮裁定|
|---|---|---|
|[最终应用验收](application-rehost-complete-0041-20261017.md)、[matrix](application-function-matrix-0041.json) C9-AP01-S003/S004；system-complete父级|七项设置、预览/提交、保存服务及跨进程读回已passed-in-sim；save/apply_settings服务明确绑定实现和旧验收|已有SIM能力直接覆盖，不重跑/新计测试。矩阵的global remaining=[]是其受控SIM范围，不证明物理flash或原ROM所有保存分支闭合|
|主仓settings-0041-round2及b/c/d/e共5批；system-complete#/cached_evidence/settings_a00fd1ac|旧a00fd1ac设置handler完整留存，b记录10、c记录6复用同一 `ev_d2c060...`/`ev_e247f...`；页面类型1b/1c的提交与选择写值已有|父级仍含同目标调用；不能因某批标题只写settings或unknowns=[]就当新callback。资源/文本记录不证明存储callee；不复制整个43KB伪代码|
|[buzzer/backlight](buzzer-backlight-0041-20261023.md)及[round2](buzzer-backlight-round2-0041-20261023.md)、[round3](buzzer-backlight-round3-0041-20261023.md)|`a01b29ec`以低byte写ck_config/lcd_backlight，失败不回滚已提交RAM/PWM；初始化读1B默认100/零改100；`a00ab4d8`另一次原配置写已保留。蜂鸣62fc916e读/保存1B，MiIO 3/9按signed value>0归一后保存/通知，无该局部回滚|这些不是新持久化缺口；静态业务写调用不等于实测落盘。D19/D20/D21/D22动画及A01/A02停止路径均不重做|
|[MiIO延后设置](miio-deferred-settings-0041-20261023.md)、[地点合同](weather-location-request-0041-20261023.md)、[B14](numeric-location-setter-b14-0041-20261023.md)/[B15](numeric-location-review-b15-0041-20261023.md)|8B请求kind/value及共享timer所有权已有；业务从全局槽取值，非独立请求快照。地点文本槽最多63B复制+NUL；city/district持久化取原输入及strlen，不等待任务；数字loc_id以4B保存且校验门/先缓存后配置顺序已有|不能由SIM copy/rollback替换这些原持有/调用顺序；B15已接受a009d8bc/dba4→a0061848，validator不是setter，不重做地点/天气队列|
|[旧reference-map](factory-reference-map-0041-20261020.md) SystemSettings条目；[Wi-Fi格式专项的普通后端段](knowledge/0041-sim-wifi-selection-gaps.md)|旧“关联0”是路径→函数归属空项。较晚专项已有普通`a005f612/a005f80e`的namespace/key文件后端及payload/CRC合同，a0060946/a0061848也有旧retained dossier|不能再泛称原厂所有持久化格式未知；也不能把一台设备样本、列表后端或Wi-Fi特定流程外推所有设置/完整NVS。这里只复用普通配置接口存在，不展开敏感数据/网络/安全或全存储扫描|
|guide-complete#/saver及system父级|旧a00afbec把ScreenSave 0/1/2/3映为180/600/1800/禁用，a00afb42把ScreenOff映为60/600/1800/禁用；SIM用独立persistent字段与enabled flags|UI/超时使用已知，不再恢复整屏保或启动。两条普通setter内部“实际改哪个RAM byte、是否继续保存/通知”的局部合同在本有界报告集中未找到；保留下面真实种子|

上述旧来源定位及必要查询结果见 [reuse-result.json](../../analysis/settings-persistence-reuse-gap-j03-0041-20261024/reuse-result.json)。旧settings-b/c重复同Evidence ID及父级cached文本不是多份独立证据；旧round2 pending/unknown列表须服从父级complete的UI范围和较晚专项。相反，父级UI完成也不能抹去其未证明的存储ABI。本题没有将未检出标题/地址等同于历史未分析。

## 本轮复核或纠正：原ROM与SIM服务分界

本轮仅检索/对照旧证据，未独立验收任何ROM指令。四类强度如下：

- 已有原字节合同及B15等独立复核：直接继承字段宽度、参数/返回门、RAM持有与调用原序。
- 旧反编译/extent/caller：用于定位后继，custom0/unaff等问题保持原限制；新报告不从旧伪码补原ABI。
- SIM服务/源码/截图/验收：证明受控host模型的值保存、反馈与跨进程读回，不证明ROM持久格式或硬件时序。
- 未检到的精确边：仅下面已定位callee的局部保存/状态传播合同；不是整设置家族未知。

最终ZIP `tools/ap01/ap01-sim-service-impl.h:147..164,205..224,277..292` 已实现独立AP01SCF1宿主格式；保存先写`.new`、flush/fsync/close，再读回memcmp并rename；`apply_settings`按值保存旧settings、副本赋给全局模型，persist失败则恢复旧副本。`tools/ap01/ap01-ui.h:236..240`仅在apply_settings返回true时承认提交，失败交服务反馈；亮度编辑确认还保留未提交编辑态。这里只读既有源行，不运行失败路径、服务或测试，也不复制成员源码。

这与ROM已恢复的局部行为不可合并：背光或某些MiIO配置写失败未回滚既有RAM/PWM；文本持久化长度可取原输入而非截断后缓存长度；共享timer请求不持独立业务值快照。SIM实现的事务/文件原子替换是明确替代合同，不是原ROM函数体。函数调用“尝试保存”与设备落盘结果继续区分。

来源/术语纠正仅为覆盖强度收紧，原功能语义纠正0；不把旧最终SIM通过重新计为本轮验证，也不把旧reference-map空归属项变成全存储新题。

## 真正新增：功能0，保留两个旧真实种子

|种子|可复用的旧定位|当前可说/不可说|
|---|---|---|
|优先 `a00ab478`（48B）|settings-round2b#/records/10，Evidence `ev_d2c060238142516e1df7a388e5984d96623578a75366a96c1472e9ed8c8df9fb`：旧汇编 `a00feac4 LBU a0,1(s4)`→`a00feac8 JAL a00ab478`，另一选择 `a00feadc a0=3`→`a00feade`同目标；旧伪码把前者对应DAT62fc402d。whole-ROM extent `ev_5334e642630bb4d54d7d94302fc3589476d1f18aa9d513ec57bf017024348c9d`，范围a00ab478..a00ab4a7|已知UI调用/参数种子，不是本轮字节验收。dossier的callee目录为a00a5bbe/a00ab274，但不证明其完整保存/通知语义。a01afb66旧constructor（round2d record3，`ev_c07160bdb96703feb18244c1eb8d977b82457a383130b34ee98c317357ab7765`）以62fc909a==3设置type1c选项，提供另一个状态消费者，不能据此直接认定setter必写该byte|
|同类备选 `a00ab4a8`（48B）|同旧handler中 `a00fe9f0 a0=3`→`a00fe9f2`及`a00fea06 LBU a0,3(s4)`→`a00fea0a`；旧伪码对应62fc402f。extent `ev_dcacb192dd6c26909541cd09a43a9128cdcd8a5f81847b51c0f4b710e5f9528d`，范围a00ab4a8..a00ab4d7|同样只认证旧调用/extent存在。constructor以62fc909b!=3设置type1b选项；真实写入/持久化下游须以已有完整留存或必要原窗口证明，不能把“没有单独报告标题”当作未恢复|

现有whole-ROM索引这两个入口historical_dossier为空，仅在settings-b/c与system父级发现同call链；本轮近期非管理报告精确地址查询无正文命中。这个有界结果只确定下一步需先找该callee的旧完整合同，不证明整个历史从未分析，也不自动授权新增ROM采集。

唯一后续闭包建议：由管理者另派一题，优先沿旧`a00feac8/a00feade→a00ab478`，先查旧留存，再核正常值输入→状态持有/实际下游保存或通知的原序；若原合同已完整覆盖即收缩。只在其真实callee出现必要接入断边时才下探，不扩所有设置、NVS/driver或重做a00fd1ac整函数。备选a00ab4a8无需并行重复开题。

I05的特定wifi-cache更新、I01/I02启动、I03/I04屏保DELETE、D19/D22动画均保持其他任务所有权。本题不提供factory reset/OTA/安全/异常路径后继。

## 未闭精确边与实际验证

本题盘点闭包已完成，新增业务、ISA、ROM字节、反编译、矩阵/资源重建均为0。仍未知上述普通setter的确切写入字段与正常保存/通知顺序、所有设置是否使用同一持久策略、原设备实际落盘/重启结果；已有普通后端合同不等于这些caller连接已证。没有凭空给RAM指针、事务或持有时长补定义。

[reuse.py](../../analysis/settings-persistence-reuse-gap-j03-0041-20261024/reuse.py)只用标准库读取旧JSON/报告与ZIP指定成员，20项定位/父级/源行检查通过：5个settings批次、4个旧call、2个既有SIM服务、2个旧extent种子。结果不含新ROM字节或完整body/源码副本。JSON解析、报告本地链接和git diff --check另行检查；本轮没有重跑任何历史SIM/持久化测试，不冒称独立技术验收或全设置恢复完成。
