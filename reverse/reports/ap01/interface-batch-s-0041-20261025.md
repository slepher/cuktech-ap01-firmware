# S：三执行与独立预调研滚动检查点

用户于2026-10-25香港时间明确按新流程继续。目标为三个执行席（研究或非作者复核）加一个专门预调研席，提前维持三份真正可派任务包；每次完成将实际耗时与精确断边回传预调研，动态调整尚未派发的包。队列不足如实记录，不以条件候选、重复研究或公共库内部填数。本文件为滚动检查点，不表示完成或收尾。

主仓初始HEAD `5bbc331ab429fb76e956e50b8081c56f8d278b11`。旧tracked/untracked/ignored成果全部保留。新任务采用独占本地分支/worktree和commit交付，由主窗验收合并；导出中间产物原路径转存核对后清理任务树。不推送、不执行固件/模型/SIM/QEMU/构建/设备或外部服务，不修改ROM/生产配置/分析器。

## 已恢复的真实状态

| 认领 | 当前处理 | 估时与依据 |
| --- | --- | --- |
| PREP-S01 | task_prep_research_01准备本批应用接入/底座候选；独占队列报告 | 初轮9–15分；材料/查重3–5、组包4–7、交付2–3分，中等置信 |
| Q-06 | app_network_review_02接手旧01无报告的非作者复核；只核接线差集和40B close清槽 | 2–4分真实短复核；旧Q04 100秒、Q02约143秒 |
| Q-07 | app_miio_research_02接续原登记，核静态初值hook正常规则/回复/同对象注册删除 | 11–20分，种子1–2、hook4–7、寿命4–7、交付2–4分，中低置信；下调旧20–28分预测 |
| Q-08 | app_ota_research_01研究ROM七槽表注册到open/write/close的同sink合同，止公共文件/HTTP接口 | 11–19分，覆盖2–3、open/write4–7、close3–5、原字交付2–4分，中低置信 |
| Q-09 | Q06结束后立即补app_network_research_02：同N四个已定位helper到cloud-ready/重连计时调用端 | 12–19分，覆盖2–3、四helper5–8、caller/原字3–5、交付2–3分，中低置信 |
| Q-10 | Q08作者完成后补app_weather_research_01：绑定配置启动读入位置缓存并接首次getter/URL条件 | 9–14分，旧完整body已定位，中等置信 |
| Q-11 | Q09作者完成后补app_protocol_research_01：MiIO两属性packed协议配置/两槽refresh/普通提交 | 10–16分，旧完整body已定位，中等置信 |
| Q-12 | Q11作者完成后补app_settings_research_01：sysconfig.bin启动加载/校验/默认回写 | 5–8分；作者216秒交付，待独立复核 |
| Q-13 | Q09复核完成后补app_ota_research_02：正常OTA任务准备/选择/启动，区别文件sink | 7–12分；已核旧upper-miio-b的offer/selector合同直接继承 |
| Q-14 | Q12作者完成后补app_protocol_research_02：cmd59→item+14/+15生产/同步通知→Q11 refresh可见性 | 5–9分；不声称由某次cmd67请求因果确认 |
| Q-15 | Q14作者/复核席结束后补app_property_research_01：typed wrapper→20槽→延后消费/发送，给定有效count的独立阶段 | 6–11分；reset/并发/共享buffer寿命未闭，不以无种子方式补全 |
| Q-16 | OTA业务桥：Q13提交D→constructor持有→HTTP六槽adapter→应用T/C七槽 | 10–16分；约2KB新私有窗口/多callback，停止HTTP公共引擎和安装内部 |
| Q-17 | 网络同生命周期阶段：ready复位、probe请求、许可→Q09已验caller | 6–11分；560B新私有窗口，旧4000ms reboot叶直接继承 |
| Q-05 | 旧review01已交付，198秒限定接受；不重复派发 | 保留默认conn写入/失效和并发生命周期未知 |

启动时实时代理树只有主窗，旧R检查点的运行快照不作为当前事实。UTC16:41已核实三执行加一预调研均运行；首发三包全部取走，预调研继续补足库存，条件候选不计可派。无关闭/释放工具，完成不代表释放；遇真实线程上限如实记录，不跨题复用上下文绕过。

## 旧BLE身份精度补注

依据[Q-05非作者复核](app-ble-review-01-0041-20261025.md)，旧M03本机“动态handle”说法应限定为：`0xa012b62a/2e`把characteristic record的UUID16搬入`+0x1e`，随后arch callback搬入`0x62fd3166..0x62fd3170`。本机stand_auth `0x19`是UUID选择值；对端discovery保存到`0x62fd315c`的value handle另计。它们不能相互替代，也不能据相同conn名称认定可靠context与默认`0x62fcc188`同一对象。此处整合既交付的复核结论，新增业务0。

## 计量

其后已恢复三执行：Q16 OTA桥、Q17网络helper、Q15独立复核；预调研备有S-P19 cmdrpc属性记录/值寿命→双result/error→清理的完整多阶段包，库存1/3，继续准备。Q16作者发现HTTP close实际接安装槽T+0x40，T+0x44普通sink close在error adapter，不能把正常下载结束直接当归还；安装内部止边保持。Q17许可读取另一对象，不能因同领域强认N所有权。

Q15作者`bfed293a5b32c7d0538e41786a2ece71eeccfe82`已merge，UTC17:08:06–17:11:48约222秒，三真body1294B/四wrapper130B/16字符串，两个ignored文件核SHA转存见`tenth-deliveries-transfer.json`，待非作者最终交付。stride为0x20=32B，派发省略0x的含糊措辞已纠正；consumer不清count/send返回忽略，prefix不足早退与value省略分开，reset/并发/队列完成等未闭。

Q14非作者`f067c9a`已merge，ignored核SHA转存见`ninth-deliveries-transfer.json`；预调研第三版`313b18036158a16e0a95a410267d289d09ea8e6f`已merge。包括Q13补修任务在内的五个停止/全commit合并任务树均核tracked/untracked/ignored无遗留，再逐一解析绝对路径验证在固定batch根内，无force清理并branch -d；主树原路径证据保留。

UTC17:10附近的实时缺口：短复核连续完成后仅Q15研究和预调研在跑，另外两执行席待有界可派包；库存0/3，未冒称满额。三份后备曾备齐但消耗速度高于准备速度。预调研继续按真实种子核剩余业务adapter，不将BLE无writer、屏保缺consumer或78B广播微项填数。

Q11非作者`1a2651dfb78016268ca884ec9c01daa754db817c`已merge，UTC16:58:54–17:01:17.983约144秒，之前读取未知；限定接受无修正，824/364B及位宽/9调用目标通过。Q12作者`6abd0bb`已merge，UTC16:56:19–16:59:55为216秒；非作者`3e66b968c63b61c92bf505be7096b7b9378d94cc`已merge，17:02:47–17:04:57总130秒、分析106秒，151指令/27关键/10调用目标，限定接受无修正。Q13作者`63dc73a`已merge，16:58:27–17:01:42仅195秒采样区间；offer已有record271及upper-miio-b合同，材料定位错误已纠正，真正新增为308B start与对象接合。ignored转存见`sixth-deliveries-transfer.json`，已停止合并且无遗留任务树按流程清理。

Q13非作者发现范围措辞过宽，先暂停复核，再从作者63dc73a恢复原同题任务树，作者补`f935f1c9602c6767998cde2f3289c26067ab3474`后停止，再恢复复核。注册record313有T分配/失败释放，只有本轮handler/offer/selector/start段无T/C分配释放。非作者`7f8caefd4d90db88f244164e9afe9a4329c933ff`限定接受，行为纠正0/范围措辞纠正1，结束17:08:15，暂停/补修等待不能精确拆分。两commit已merge；ignored转存见`eighth-deliveries-transfer.json`。

Q14作者`1f3f86f`已merge，17:01:23.838–17:03:58.217为154.379秒采样；非作者`f067c9accb2ab20d98f29bc3dc21e7cf04702dff`待整合，17:06:31–17:08:53观测142秒/原字窗口76秒，限定接受无修正，74边界/3indexed/2SB/3JAL。S/T寿命/数量不变量、+15消费/特定67确认仍未闭。Q14作者与Q12复核ignored转存见`seventh-deliveries-transfer.json`。

队列曾实际达到3/3，S-P07配置加载、S-P08天气复核、S-P09 OTA启动均为完整包，第二版commit`24bca7e8f00bcb8f13110c9613359bbdfd781ba4`已merge。随着即时补位均已消耗，S-P10协议复核和S-P11 cmd59生产也先后消耗；不能将旧3/3快照当当前库存。预调研仍运行补齐，未交付作者的复核只作条件候选。

Q08非作者最终`db3e7b475e3fe2d1256c917db810eeb7789a59ce`已merge，接受作者620f779条件修正；首快照16:50:03、恢复16:52:22、提交16:54:34，中断/补修等待不能精确拆分，不声称有效工时。主窗另外提交`c1b37ca`仅修两条analysis相对链接。Q11作者`7ab7fd20e8c765db2433abddda2ea606e4ddb53f`已merge，采样UTC16:50:59–16:54:59为240秒，首钟前读取未知。两者ignored已核对转存，见`fourth-deliveries-transfer.json`，相应已合并停止任务树已无force清理。

Q09非作者`3718801af3ec369927f7f537fb0a30d2690c9739`已merge，UTC16:53:22–16:56:53为211秒，20原字/15caller断言及2厂商字通过，限定接受/新增纠正0。Q10作者`baeee728`已merge，约197.7秒；非作者`8ccc10dfadb32d686fab8cebd6d9d3154dc73792`已merge，UTC16:55:25–16:57:36.307为131.3秒，358B/7JAL/2BEQ，限定接受/新增纠正0。三ignored文件转存见`fifth-deliveries-transfer.json`，任务停止/commit合并/无遗留后清理相应任务树和已合并分支。完整接口断边未自动关闭。

Q07非作者交付`18bc212b03ae6b94cbf9fcba1a0c67d26e02f53f`已merge，主体UTC16:46:35–16:48:30共115秒；限定接受，无需作者修正，新增业务0。其ignored原字与Q09作者ignored JSON/txt共3份解析/核SHA转存，见`second-deliveries-transfer.json`，确认各任务停止和无遗留后清理两工作树/已合并分支。

Q08作者交付`111499a24a60977ee8c73cd5bcb3ffaac835b9d7`已merge；精确采样UTC16:40:53–16:47:57为424秒，采样前阅读未知，不能当完整工时。非作者复核发现open flags遗漏属性非空分支；先暂停复核再唤醒作者，作者补交`620f7791c0606ce68452f91ea16d99f91ba128d2`后停止，复核恢复确认。修正为属性路径非空固定3，空属性fallback默认app.bin才total非零取0x27、零取3；全OTA仍有间接桥/取消/安装生命周期断边。

Q09作者交付`675db193a57e78bebb787d5a388b3a5ffcc3d391`已merge，待非作者复核。可核区间UTC16:44:59.395–16:49:09.588为250.193秒，首次查重/最后提交未全计；Git记录分支创建UTC16:42:27仅为调度前参照。四helper716B及同caller正常阶段完成，断边保留许可策略/实际动作/跨接口探测/计数全部生产侧，未自动开题。预调研已给出完整复核后备包，暂存库存1/3，其他包继续准备。

Q07作者交付`ac561dacf470ea380445a9886a42eace223b3537`，主树merge为`f02343739f6c18af24e8d989cc15609f93776f67`，仍待非作者复核。主体UTC16:38:27–16:43:41共314秒，提交收尾未并入该值；八窗916B。两个ignored JSON按`miio02-transfer.json`核对转存后清理作者树/已合并分支。非作者app_miio_review_02按预调研完整接口包补位，预测3–5分。

预调研首版`9a9802c663fe93fa02a29fd0f3dd4a3b0ae73a00`已merge为`7e68287`，当前报告仍在本批滚动更新。[队列报告](task-prep-research-01-0041-20261025.md)中的首发与Q09包已消耗，库存曾为0/3，不能说已预备齐三份。Q09四callee只有extent元数据，主窗最初派发“有旧body”措辞已纠正；停止额外留存搜索，按原四个真实入口允许必要原字短窗，不将元数据当body证据。

合并时主树原有三项日志索引删除使ort拒绝合并。先核本地文件均与HEAD blob一致，临时仅恢复这些索引条目，完成两次无关任务merge后立即`git rm --cached`恢复原暂存删除。三个日志文件未删除或改动，原有其他tracked/untracked/ignored成果保留。

Q06非作者复核02：UTC16:38:09.628开始，16:39:47.994技术结束约98秒，16:41:26.853含报告/提交收尾总197秒，命中2–4分预测。592B/8窗、18断言通过，业务纠正和新增均0。最终交付`27c4d34abff7726fc845f26326b97325fa03d3c0`（含前驱`e0408a10fd7c786730d94ed6cf9ef63c5ccb2673`），已fast-forward合并；ignored JSON解析、20351B和SHA核对后转存主树原路径，再移除源副本。记录见`reverse/analysis/interface-batch-s-20261025/network02-transfer.json`。确认任务停止、commit已合并、tracked/untracked/ignored无遗留后，无force清理network02工作树及已合并分支。Q09以新独立上下文和基线27c4d34补位，实测及断边已回传预调研。

各代理记录UTC起止、实际墙钟与可见工具等待；墙钟不冒充有效工时，预算不作实测。当前没有本批独立token快照，不沿用旧R累计数，不编造token或节省比例。派发与运行状态以唯一管理表及当前代理树为准，后续完成实测另补。
