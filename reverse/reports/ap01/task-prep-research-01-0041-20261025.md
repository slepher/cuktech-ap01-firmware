# PREP-S01：底座协议与应用接入预分配队列

本报告为滚动定题队列，不是业务取证或独立技术验收。**最新可派与实际消耗见文末快照**；下文按轮保留当时库存，不能将旧数字视作实时状态。初版首发Q-06/Q-07/Q-08和后续S-P01/Q09均已由主窗取走，当时后备0/3、缺3；缺口不能用未交付复核、BLE无writer或短胶水填充。管理表唯一写入者为主窗，本报告不授权认领。

基线 `5bbc331ab429fb76e956e50b8081c56f8d278b11`；分支 `codex/task-prep-research-01-20261025`。主仓根 `D:/Documents/PlatformIO/Projects/cuktech-ap01-firmware` 下述所有证据均从该绝对根只读访问，新规则及未提交成果不能从本worktree推断不存在。独占worktree `D:/CodexHome/visualizations/2026/10/24/01a16ec4-7aa8-7b43-a0e8-609e1021781b/ap01-s/prep01`。

原件绝对路径 `D:/Documents/PlatformIO/Projects/cuktech-ap01-firmware/roms/0041/ap01-1.0.2_0041.bin`，6769704 B，沿用SHA256 `972db4c136c7ed9e24a83c07c1a7fd62040ca018b08ca285216d26b1fee3c6b9`，offset=VA−0x9ffff000。不重算hash；不执行固件、模型、SIM、QEMU、回放、构建、设备或网络；不改ROM、生产、配置或分析器。已读reverse-design 3.1/3.2/3.3/5.1/7及管理顶部/Q05–Q07，参考REA skill，仅复用留存和定题所需28B表定位；未启动REA或下级。

## 首发消耗记录

|包|查重、差集和材料|状态与估时|
|---|---|---|
|Q-06 / app_network_review_02|Q06作者已停止；review01只有脚本、无完成报告且上下文不可恢复。复核0xa006580c..0xa0065840注册→0xa006cda4同N/DHCP→0xa0066296 down：注册槽、s2关联/s5 DHCP返回分离、同0x62fc99e4中断与0xa005fac4关闭清槽。继承upper record248/273/252及I05/I06，不重做monitor或公开DHCP内部。作者绝对报告为 `D:/Documents/PlatformIO/Projects/cuktech-ap01-firmware/reverse/reports/ap01/app-network-research-01-0041-20261025.md`，analysis同stem。|主窗已派。短复核2–4分钟：定位<1、原字/对象1–2、交付约1；据Q04 100秒/Q02 143秒。建议独占报告/analysis app-network-review-02-0041-20261025，分支codex/app-network-review-02-20261025。验收只限定本差集，不将IPv4调用当实际ready。|
|Q-07 / app_miio_research_02|继承Q04六实参、policy P=0x62fc4944和D04启动映射；新种子0xa0004458+0xc初值0xa011860a。只正常hook规则/handler回复及同规则add/delete寿命，不再无writer负搜。主仓 `reverse/analysis/interface-batch-r-20261024/policy-initializer-seed.json` 为种子实际位置；旧research02目录仅留存hook-static-window.json、0xa011f186.retained.json和0xa0121886.retained.json，无完成报告。|主窗已派。阶段种子1–2、hook4–7、同对象寿命4–7、原字交付2–4=11–20分钟，中低置信；旧Q研究约3–12分钟，不能继续沿旧20–28机械预测。独占app-miio-research-02-0041-20261025与同名分支。验收初值与运行不变性分开，止公开容器/调度。|
|Q-08 / app_ota_research_01|见下方完整包。|主窗已派，11–19分钟；本报告不重复授认领。|

Q05已有非作者完成报告 `D:/Documents/PlatformIO/Projects/cuktech-ap01-firmware/reverse/reports/ap01/app-ble-review-01-0041-20261025.md`，198秒限定接受，不能重派review01。需主窗补注的旧M03实际在 `D:/Documents/PlatformIO/Projects/cuktech-ap01-firmware/evidence/rea-0041-20261017/evidence/mible-recovered.md` §M03（53/57/61/67行），本机UUID16与peer动态handle分开；本预调研不作技术纠正作者。

## Q-08已消耗包：原厂ota_app下载sink接入

问题是应用OTA下载sink的open→write→close与同file_ctx所有权，止验签/安装入口。相交Q06/Q07只共享manager创建，不共享问题；P08是底座OTA对象；app-lifecycle-ota设计和ota-image-admission为自有OTA，不是本原厂sink。继承父级miio-recovered §10已解释prepare/HTTP/tag与knowledge安装后段，不能重计为新增。

真实种子：0xa006462e..0xa0064658从0xa01bb0cc复制28B七槽，经0xa0064654→0xa0115b84注册，返回存0x62fcaa08。仅为定题读回七word：0xa006f5ce、0xa006fa80、0xa007016e、0xa007022c、0xa0074d30、0xa0070366、0xa006fab6。不是由名称猜函数入口。既存upper-complete record248/157/287/37分别定位注册/open/write/close；record248 Evidence ev_c3dd842723b83165bc8e1a6b235f2005269080da4969520bd0c0f0e413db133a，157 ev_797aab000b487ace912a0bc365e076a1eccf81de4e00f11cf6cba7aa2f70226b，287 ev_e27bcee0e1cc00a12f36681769a1fe8f03dbb56c5e590575211447b81e839bd1，37 ev_1c4eb2f20e1a5e81c5b27e47f687fece4c5e71ae5d9bf7f8a8f7983a6d12ada9，沿各源profile，不混贴。

必要绝对材料：

- `D:/Documents/PlatformIO/Projects/cuktech-ap01-firmware/evidence/rea-0041-20261017/evidence/upper-complete.evidence.json`，上述records的normalized_result。
- `D:/Documents/PlatformIO/Projects/cuktech-ap01-firmware/evidence/rea-0041-20261017/evidence/miio-recovered.md` §10。
- `D:/Documents/PlatformIO/Projects/cuktech-ap01-firmware/reverse/reports/ap01/knowledge/0041签名与Bridge接口分析.md` §后续验签、CRC与切槽，明确下载写入尚未完整追踪。
- `D:/Documents/PlatformIO/Projects/cuktech-ap01-firmware/reverse/analysis/0041-20261013/0041-ghidra-pass2.txt`、pass3.txt、pass5.txt仅上述种子的必要窗口，先核是否已完整覆盖。

有限依赖：0xa007016e→0xa00700b6，0xa007022c→0xa00701f6，0xa0070366→0xa0070322；同ctx+4下0xa00b4f54/0xa00b5122/0xa01addc6仅必要接口。排除0xa006f5ce prepare重做、0xa0074d30验签安装、0xa0074b94、CRC/board、MCU、HTTP/TLS/公共FS内部；新跨对象边另报。验收给真实callback ABI/返回宽度、file_ctx来源、sink开闭/持有归还、写入返回合同与未闭，不以短wrapper宣称镜像安装成功。

阶段覆盖/槽ABI2–3、open/write4–7、close/归还3–5、原字交付2–4=11–19分钟，中低置信，依据本批多阶段研究实测3–12分钟与三个短callback已有定位；如旧已覆盖则提前引用收缩，不追库补时。建议输出app-ota-research-01-0041-20261025报告/analysis，分支codex/app-ota-research-01-20261025，worktree同本batch根ota01。

最小派发：`沿新登记Q08，在0041/5bbc331恢复原厂ota_app表0xa01bb0cc的open0xa007016e→write0xa007022c→close0xa0070366对0x62fcaa08 file_ctx的正常下载sink接口；先继承upper records248/157/287/37及旧pass2/3/5，差集限上述有限依赖。独占app-ota-research-01报告/analysis，本地commit、不推送，静态限制沿统一流程，11–19分钟预测，已有覆盖立即收缩。`

## S-P01已消耗为Q09：netMonitor同N的云接入计时阶段

候选代理app_network_research_02，新认领由主窗决定。问题是既验monitor正常循环下(N,elapsed)驱动的cloud-ready/探测/重连字段及返回→caller动作，绝非重做完整monitor。相交Q06继承注册/关联/DHCP/IPv4，不读同40B close差集；I05/I06仅配置cache，F11队列为公共止边，Q07策略对象不同。

已有出处与差集：miio-recovered §6已解释monitor事件0..11与30/1800秒外层，明确0xa0067b94/0xa0067aec/0xa0068854/0xa0068914 helper未全恢复；Q06作者也保留此既有helper缺口。精确报告地址检索仅该父级与Q06引用，未找到较晚完整helper合同；这只说明已查范围，不证明全历史无分析。

对象N=0x62fca7f8，必要种子upper-complete `#/records/89/normalized_result`（0xa006d260）。callee元数据分别为0xa0067aec..0xa0067b93（168B）、0xa0067b94..0xa0067be5（82B）、0xa0068854..0xa0068913（192B）、0xa0068914..0xa0068a25（274B）。四者均被真实caller以(N,elapsed)调用；其返回驱动0xa0195ce4、0xa01b3d12及正常分支，不能凭名称补联网成功。

必要证据绝对路径为 `D:/Documents/PlatformIO/Projects/cuktech-ap01-firmware/evidence/rea-0041-20261017/evidence/upper-complete.evidence.json#/records/89/normalized_result`、同目录miio-recovered.md §6，及主仓 `reverse/analysis/0041-20261013/0041-ghidra-pass5.txt` 仅四种子窗口。起点为既验loop elapsed；终点为四helper返回/直接业务通知调用点。允许同N必要字段/常数和直接调用接口，止公开网络、timer、调度、formatter；不扩5644B monitor、其他helper、实际无线/云端、凭据或安全验证。旧pass5若已给合同则引用收缩。

阶段旧覆盖2–3、同字段四helper5–8、caller合成/必要原字3–5、交付2–3=12–19分钟，中低置信；依据旧Q06覆盖复用后339秒、Q01多阶段约12分。真实低于20分钟如实保留；这是完整同接口短阶段，不能机械抄30分钟或跨域拼量。验收应给elapsed原单位证据/未知、字段宽度/条件重读/返回、正常caller动作与所有权，不能将通知或计数当真实联网。

独占建议：batch根network03，分支codex/app-network-research-02-20261025；报告和analysis同stem app-network-research-02-0041-20261025。最小派发：`登记新认领后，沿0041/5bbc331同N=0x62fca7f8的monitor既验elapsed调用，仅恢复0xa0067aec/0xa0067b94/0xa0068854/0xa0068914四helper与必要返回→caller连接；先复用record89/miio-recovered §6/pass5，不重做Q06或整monitor，有限依赖止公开API，12–19分钟，静态、本地独占commit交付。`

## 不计可派的候选

1. BLE默认conn：Q05确定读点0xa019060a→0x62fcc188；作者和review01都无writer。有限核upper-mible.md/mible-recovered.md及Q05已选10条、ble-callbacks七份留存，未取得真实writer。这个有限范围无命中不等于全ROM无writer；0x62fd2af8/0x62fd2b0c可靠handle不能与default conn对象认同。状态待消歧，停止负搜。
2. Q07非作者复核：作者尚未交付，只列条件候选app_miio_review_02，不能计库存，待成果/差集/耗时再定题。
3. Q08非作者复核同理等待作者，不计库存。
4. 云消息广播0xa01b38dc→0xa0197686，upper record278/Evidence ev_dabc78c1a24a31952d71194b8efa1dd5e523fcc8da2b7da86e791ef85e9f1a98给真实78B callee extent至0xa01976d3；父级明确广播/并发fd管理未闭，但单78B胶水不足完整包，fd表管理主体已由旧loop覆盖。暂留同接口差集待合并，不为补库存另造微任务。

## 计量与后续

首个即时包已在落盘前回主窗；后经主窗消息确认三首发已消耗。首次工具前未取UTC，不伪造全任务起点；首个实测UTC采样为2026-10-24T16:37:50.2757810Z。此后结束时间见queue.json；此前时间未知，不能把采样区间称完整实际工时。工具正常读取含在可见墙钟，未逐项完整跟踪；无排队/睡眠/外部等待，token不可得不估造。初轮9–15分钟是预测，当前无完整起点不能宣称实测吻合。

本轮原字仅为OTA表28B定题定位，没有完整业务恢复。首发包已落盘可供验收，后备已消耗为Q09，现0/3，接收完成/真实耗时与断边后继续滚动补位；不把条件项冒充可派，不修改共享管理表。

滚动更新：主窗确认Q06 review02总墙钟197秒（含提交工具），技术检查98秒，不混用。限定接受、新增/纠正0，交付及主树ff为27c4d34abff7726fc845f26326b97325fa03d3c0；Q09已按新基线27c4d34派发app_network_research_02，S-P01从库存移出。PREP本树基线仍5bbc331不移动。

## 第二轮队列快照（UTC 2026-10-24 16:54）

以下是本轮后续完整包。S-P02/Q07复核、S-P03/Q10天气研究、S-P04/Q08复核、S-P05/Q11协议研究、S-P06/Q09复核均已被主窗取走；不计库存。新S-P07/08/09同时准备完成时为 **3/3可派**，后续主窗实际派发会消耗，不宣称永远保持库存。技术复核暂停/补修不形成新包。

关键澄清：Q09四callee仅有record89的callee extent元数据及已存caller，没有四callee旧body。主窗已澄清派发中的“已有body”误述，并授权四精确入口716B必要原窗。原S-P01段落中的“callee元数据”必须按此理解，停止重复搜缺失材料，不能将元数据升级正文。

### 已消耗S-P02：Q07非作者合批复核

app_miio_review_02，仍在Q07原认领下。作者ac561dacf470ea380445a9886a42eace223b3537后停止，复核18bc212b03ae6b94cbf9fcba1a0c67d26e02f53f限定接受，无需作者修正/新增业务0。主体115秒，不当作含提交总时长。

完整问题：P初始化映射→默认六参hook→规则遍历/handler或回复→同P节点增删。已有Q04安装/消费前提直接继承，差集为P=0x62fc4944、ROM0xa0004458初值0xa011860a；hook0xa011860a..0xa0118711，回复0xa0110c76..0xa0110d7d，旧add0xa0121886/delete0xa011f186/unlink0xa006929a仅必要连接。必要绝对证据为主仓 `D:/Documents/PlatformIO/Projects/cuktech-ap01-firmware/reverse/reports/ap01/app-miio-research-02-0041-20261025.md` 与同stem analysis的verification.json、bounded-raw.json.tmp、retained-selection.json.tmp（主窗已merge/转存）；upper-complete records248/272及启动映射沿旧profile。

验收OR谓词((origin|flags)&3)==3、P.next sentinel/完整名、handler返回忽略/hook0与拒绝hook−1区别、reply header栈借用/回调门、重复strlen/len+9节点/插入原序/先unlink再free。止JSON/allocator/manager关闭，不做权限绕过或同步推断。阶段定位<1、hook/回复1–2、节点/边界1、交付约1=3–5分，作者314秒主体/Q06总197秒校准。独占app-miio-review-02-0041-20261025，分支codex/app-miio-review-02-20261025。最小派发：`同Q07非作者仅核以上默认P完整阶段和必要继承前提，静态、独占本地commit、不推送；保留运行时替换/增删caller同步/关闭/handler外部持有断边。`

### 已消耗S-P03：Q10天气启动位置研究

app_weather_research_01，commit baeee7285a15762a786e9a4b5ae89e15d84e96df已交付停止。首个时钟至交付外层采样约197.7秒，报告正文检查182.3秒，两者不同收尾端点，不当有效工时；远低9–14分钟预测，后备据此继续下调。

问题为绑定配置启动加载→位置缓存→首次getter/URL。真body绝对材料 `D:/Documents/PlatformIO/Projects/cuktech-ap01-firmware/reverse/analysis/buzzer-backlight-0041-20261023.json#/functions/6`，0xa005a736，ev_dc0e38b0f382799ea2a8e8ad7f21cefc5998b0767ecf38a58cfdebe8add167c3。真实前驱0xa005ae7c..aec8及0xa005b8a4..b9ae，仅必要基址定义；不是整initializer。已有weather-location-request/deferred/B14/B15只运行时setter/URL，差集是启动读入。四调用0xa005b8be/b8d6/b8ee/b906以a0060946读ck_config/loc_province/city/district/loc_id至0x62fc90a0/90e0/9120/9160，b930写100000，b944调用a0061848，b988写0x62fc3fec字节1。

边界止这些槽和既验0xa00a0906/0xa00aab1c条件，不读配置后端/MD5/TLS/formatter、其他初始化字段或writer。验收key/RAM/读长度返回、bind读返回与byte双门、默认和回写、文本终止未知、getter fallback不拷out及loc_id/location_id区别，不能把调用当持久成功。与Q09 N、I05缓存、H页面对象分开。输出app-weather-research-01-0041-20261025，branch codex/app-weather-research-01-20261025，worktree weather01。原阶段1–2/3–5/3–4/2–3=9–14分预测已证偏高。最小派发：`沿同位置启动阶段，只核指定前驱/四键/同缓存首次getter和URL，继承setter/API、静态独占commit交付，旧覆盖立即收缩。`

### 已消耗S-P04：Q08 sink非作者复核与补修状态

app_ota_review_01原包以作者111499a24a60977ee8c73cd5bcb3ffaac835b9d7为输入，主窗已取用。主仓报告和analysis同stem，原始作者树ota01；后续以主树已合并/转存绝对路径为准。合批复核七槽copy/T-C身份→open整数ABI→write五参/hash先于可能原地src[0]变换→close原序。旧upper records248/313/157/287/37；表0xa01bb0cc、C=0x62fcaa08、T+30七槽、T+4c=C；主体0xa007016e/0xa007022c/0xa0070366及0xa00700b6/0xa00701f6/0xa0070322，文件边界0xa00b4f54/0xa00b5122/0xa01addc6仅差集。

验收total值非指针、整数返回、write len/−1、0xa0070216厂商字字段、先hash后首byte变换/无本层恢复、可写借用、先final/free H清槽再fd>0归还置−1/返回0不free C/T。止公共FS/散列内部，不认HTTP六槽为七槽。阶段<1/1–2/1/1–2=4–6分，中置信；作者可见424秒为采样区间，不是完整总时长。独占app-ota-review-01-0041-20261025与同名branch。

复核发现真实修正，主窗已先中断复核再唤醒原作者同题补修：0xa00b4f8a bnez→0xa00b4f9c跳过total检查；ro.boot.update_slot非空时flags保3，仅空属性fallback的total非零才设0x27、零为3。不能沿旧泛化“total控制flags”。这不是新包，作者补修commit和复核恢复状态由主窗后续给定，不提前标接受。最小派发仍为原Q08同题差集复核，修正后只重核必要条件。

### 已消耗S-P05：Q11 packed协议禁用配置

app_protocol_research_01，问题MiIO属性4/0x0e和4/0x11→同C1/C2缓存→协议禁用mask提交。真实caller绝对材料 `D:/Documents/PlatformIO/Projects/cuktech-ap01-firmware/reverse/analysis/miio-deferred-settings-0041-20261023/retained-functions.json#/functions/1/normalized_result` 的0xa009d8bc两分支。核心824B真body为 `D:/Documents/PlatformIO/Projects/cuktech-ap01-firmware/evidence/rea-0041-20261017/evidence/whole-rom-private-20261023-008.json` normalized_result，ev_ed7e71f1bd106ab36710c56dfbcad813bb82ce7c1c69484bfd18f4da5eddf6d7；必要refresh0xa009c662 364B真body为同绝对目录whole-rom-private-20261023-006.json，ev_32edb8a17764f474455354c17df1d950e43cd7dbf42deeec64921a33c9ad23d7。独立JSON若无structuredContent，从content[0].text解析同字段。

对象0x62fc91a0/0x62fc91a4两槽，各4B；限packed位→字段/保留位→反向mask→0xa01b272c(0/1,mask)，caller通知截断值。下游完整旧body `D:/Documents/PlatformIO/Projects/cuktech-ap01-firmware/reverse/rehost/charge-complete-0041.json#/records/22` 继承，不计新增。E07只列item+14，buzzer-round3只排除c662两槽伪蜂鸣；P14普通开关/安心、N01 mode和自定义功率不同。a009cc0c自定义功率已验排除，GET/cache9192、天气90a0排除。有限refresh→a00a53c0只必要item字段/返回接口，submit沿a01951e2已验栈payload借用，止copy/queue/MCU；不扩全属性/协议物理生效。

验收两属性关系/C1C2位域、宽度、保留位/变化门、mask方向/port索引、提交与通知非确认、输入和局部payload借用。独占app-protocol-research-01-0041-20261025，branch codex/app-protocol-research-01-20261025，protocol01。阶段2–3/4–6/2–4/2–3=10–16分预测，随后Q10约198秒说明充分定位包仍偏高，未派新包继续下调。最小派发：`仅上述两属性到同协议缓存再到已验submit的完整正常配置阶段，旧body复用，必要原字，静态独占commit交付；保留确认/实际协议生效未知。`

### 已消耗S-P06：Q09非作者合批复核

app_network_review_03，作者675db193a57e78bebb787d5a388b3a5ffcc3d391已停止、merge/转存，主窗已取走复核包。必要绝对报告 `D:/Documents/PlatformIO/Projects/cuktech-ap01-firmware/reverse/reports/ap01/app-network-research-02-0041-20261025.md` 与主仓同stem analysis的verify.py/verification.json/inspection.txt。只核四callee716B及旧upper record89必要caller，不运行作者脚本、不重验Q06。

验收elapsed累加、unsigned3599/14门/清零原序、N+188阈值、十项先移再差/每轮一格/不保余秒、N+18c重读复位、0xa006895a/0xa00689ce完整厂商word与旧SINC字段、锁重读/0或1动作门。caller state2+ready、state1 C触发后仍D且不经a0067c20、其他state分流；不当实际ready或重启。止a0067c20/a0069356/a0195ce4/a01b3d12调用端/诊断与公开锁，不找全部计数writer。独占app-network-review-03-0041-20261025，branch codex/app-network-review-03-20261025，network-review03。阶段<1/1–2/1–2/1=4–6分，依据Q09可见250.193秒区间非总、Q07复核115秒主体/Q06总197秒。最小派发：`同Q09非作者，仅核四helper及必要caller消费，静态独占commit交付，保留许可/动作/跨接口/并发断边。`

### 可派S-P07：系统配置8B启动加载、校验与默认

候选app_settings_research_01，新认领由主窗登记。问题原厂/data/sysconfig.bin启动load/校验→默认回写→G=0x62fc9098初始化。种子来自已验L03 writer使用的精确pathname0xa026a21c留存引用，有限旧private条目只定位071 writer与072 reader，不是相邻猜函数。

真body绝对材料 `D:/Documents/PlatformIO/Projects/cuktech-ap01-firmware/evidence/rea-0041-20261017/evidence/whole-rom-private-20261023-072.json` structuredContent.normalized_result（或content[0].text解析），0xa00ab2e8..0xa00ab433 332B，ev_85099f331255aab9e146bc35df48bcdbe3e38160b9802c06864c877f036f7d00，原profile分列。其caller metadata为0xa005cc1e，只证明定位，不能凭它认证主入口完整时序。继承L03/L04 writer、L05/L06 byte消费者、M01/M02已验G前6B算法及低16位，不重做；system/guide complete仅SIM行为前提。较晚精确a00ab2e8/SysSettingsInit报告查询未找到专项，不说全历史不存在。

有限范围：init对注册头0x62fcb4ec的初始写；文件read调用/返回是否消费；算法u32与G+6 u16比较；close后失败→0xa00a3a96默认（32B只有extent、无现成body，准精确入口必要原窗）→已验0xa00ab274 writer，以及G+2/+3已验消费者的默认值接合。安装0xa00a40c4到0xa01b2474(,100)只保留指针/调用边，不追callback。止公共FS/日志/allocator，不扩NVS/CRC/GUI/线程/其它G写者。与Q10位置配置、Q11协议缓存地址/对象不同，Q08 T/F也不同，无未交作者依赖。

验收读取实参8/1及是否检查返回、校验位宽/成功失败门、默认实际写值/宽度和回写原序、H句柄归还、注册头初始形状及明确未知。真实不足20分钟，阶段覆盖1、load/default2–3、消费/资源原字1–2、交付1–2=5–8分，中置信；参考Q10充分定位约198秒，默认32B需新核。独占app-settings-research-01-0041-20261025报告/analysis，branch codex/app-settings-research-01-20261025，settings01。

最小派发：`登记新认领，0041/最新管理基线，沿0xa026a21c→已存reader0xa00ab2e8恢复G8B加载/校验/默认回写和必要消费者前提；限072真body与默认32B必要原窗，继承L03–L06/M01–M02，callback/FS到调用边即止，5–8分钟预测，静态独占本地commit不推送。`

### 可派S-P08：Q10启动天气非作者复核

候选app_weather_review_01，Q10原认领。作者baeee7285a15762a786e9a4b5ae89e15d84e96df已交付停止，无尚未交付依赖。当前作者绝对报告在 `D:/CodexHome/visualizations/2026/10/24/01a16ec4-7aa8-7b43-a0e8-609e1021781b/ap01-s/weather01/reverse/reports/ap01/app-weather-research-01-0041-20261025.md`，analysis/verify.py与evidence.json；主窗merge/转存后首选主仓同相对路径。真body及已有getter/URL证据沿S-P03。

只核358B差集：0xa005ae7c..aec8 bind返回=1及0xa005b8a4非零byte双门；0xa005b8a4..b9ae四key/目标/长度/返回忽略；loc_id默认100000先RAM后回写；bind读失败不先造默认0；b988标志非定位成功；继承getter0xa00a0906/URL0xa00aab1c必要条件，loc_id≠location_id、fallback修cache不拷out、unsigned legacy_id>100000及文本首byte门。止原S-P03接口边界，不读配置后端、setter/H页面、MD5/TLS，不补文本NUL或跨线程启动先后。

验收独立源身份/原字、7JAL/2分支与上述对象/返回/未知，不运行作者脚本。阶段定位<1、原字/门1、接合/未知<1、交付1=2–4分，中置信（Q10作者约198秒、Q07复核115秒主体、Q06总197秒）。独占app-weather-review-01-0041-20261025报告/analysis，branch codex/app-weather-review-01-20261025，weather-review01。最小派发：`Q10同认领非作者合批复核上述启动及必要getter/URL差集，正文/原字源独立核、不执行作者脚本，2–4分钟，静态独占commit交付。`

### 可派S-P09：原厂OTA manager任务准备与T启动交接

候选app_ota_research_02，新认领由主窗决定。与Q08 C+4/F文件sink、当前file-open补修不同对象/所有权阶段，不借用未完成补修。独立输入均为旧upper根留存；Q08只作边界参照。问题正常miIO.ota请求参数→manager task列表/选T→start交接/返回，止HTTP/实际sink/安装。

父级protocol报告仅解释miIO.ota来源位/参数/忙态，miio-recovered §10只prepare/HTTP/tag；精确0xa010f7e8/0xa01148c4/0xa0114790旧报告查询无专门启动接口合同，旧根采集不等于依赖闭合。真body绝对材料 `D:/Documents/PlatformIO/Projects/cuktech-ap01-firmware/evidence/rea-0041-20261017/evidence/upper-complete.evidence.json#/records/205/normalized_result`（0xa01158f6..0xa0115b83 654B，ev_a19c9b52372ecb98fa3751f092a2269b416466b6fc4a07098a49b6a982fab463）与record185（0xa01148c4..0xa011493d 122B，ev_940624df09f090be66676c31a0efe6ef3e40b3e6f0380cb01487b1cf832b0db1），各原profile不混贴。

真实callsite0xa0115a98→0xa010f7e8(manager,type,params,len)、0xa0115b0a→0xa01148c4(manager)、0xa01148f4→0xa0114790(T)。后两新callee范围为0xa010f7e8..0xa010f86d 134B及0xa0114790..0xa01148c3 308B；它们只有extent/直接callee元数据、没有已定位旧body。明确准从两精确入口定点短窗恢复，定位handoff即收缩，不能再声称材料已有body。T注册列表沿record313旧body，T+30七槽/C@+4c；manager基址的M偏移须按实际参数证明，不能按数值相近认同。

有限只params借用/复制、T state+50/选中列表、start返回门、T+48 completion callback(T,C)及必要正常header/时间写入。0xa012193c仅下一跳参数/返回接口，若其内部才是真启动即保存精确断边，不能展开新callee。排除Q08 sink/file-open补修、HTTP、prepare、验签/安装、MCU/无线、公共JSON/allocator。保留来源位检查但不做权限/异常实验。

验收任务接受/启动/完成区别、输入与T/C持有、mutex范围/回调时点、普通无task/失败返回及有限资源归还；start0不等下载/安装成功。阶段coverage/对象1–2、两小callee3–5、handler接合2–3、原字交付1–2=7–12分，中低置信；Q08可见424秒/Q10约198秒，442B新原窗增加不确定性。独占app-ota-research-02-0041-20261025报告/analysis，branch codex/app-ota-research-02-20261025，ota02。最小派发：`登记0041新认领，继承upper205/185/313真body，仅恢复miIO.ota参数到manager选T和start交接；两已知callee134B/308B必要新短窗，0xa012193c止调用端，不读Q08 F/sink、HTTP/安装，7–12分钟，静态独占本地commit。`

第二轮计量：可得UTC采样16:37:50.275781→16:54:39.652564约1009.377秒，仅为该采样区间，完整任务开始仍未知；期间持续补包/即时交接和文档，不等于有效计算工时。全部工具为正常本地读取、JSON定位/文档/git提交；未逐项完整汇总等待、无sleep/外部排队，token不可得。中间queue.json继续忽略留存；报告本地追加commit交付，之后同题等待主窗真实消耗/新结果再补。

最新消耗补注（主窗消息）：三包曾同时达到3/3，随后S-P08/Q10非作者app_weather_review_01、S-P07/Q12 app_settings_research_01均在11c90bc派出，现库存仅S-P09，1/3、缺2。Q08补修620f779经非作者db3e7b475e3fe2d1256c917db810eeb7789a59ce限定接受，flags真实修正1；首精确快照16:50:03、恢复16:52:22、提交16:54:34，暂停/补修等待无法精确拆分，不当有效工时。Q11作者7ab7fd20e8c765db2433abddda2ea606e4ddb53f完成，采样240秒非完整总时长，复核包另补。

## 第三轮滚动快照

S-P09已作为Q13、S-P10作为Q11复核、S-P11作为Q14研究、S-P12作为Q12复核、S-P13作为Q13复核、S-P14作为Q14复核全部取走。本报告第三次更新时只有S-P15新包已备、待主窗登记；若尚未取走则库存1/3，缺2。不能把进行中的作者后续复核算库存。屏保slide_param/time仅有短冷启动读默认、缺完整消费种子，已停止，不派微任务。

### 准备覆盖错误与技术复核修正

Q13原S-P09称offer0xa010f7e8“仅extent无旧body”错误：预调研核了upper-complete与round1 metadata/报告目录，漏核领域upper-miio-b父级语义卡，且实际upper-complete record271已有真body。作者找到upper-miio-b中offer ev_acec13eb19b12621a674a56b842b3cba123fc76d98212eca7676f53ea1e76459和selector ev_4999424dc25eab1cd88751ca3fc153972ea5a2e3496073c25e5fdb8d7c368f04；它们应继承，不重计原字134/308B或新业务。真新增缩为M/L接合及start308B/D/T关联。此处保留原准备错误，不静默回写成当时已核；后续定题加上对应upper父级卡核对，不能只查报告标题/精确地址。

Q13非作者另指出“本题未见T/C alloc/free”过宽，record313明确alloc T 0x2e0及注册失败free T。主窗暂停复核后同题作者补f935f1c9602c6767998cde2f3289c26067ab3474，只收窄为handler/offer/selector/start段未做该行为，C来源寿命未知；5旧行复核、无新原字，作者停止后恢复非作者。补修不是新包或新取证阶段。

### 已消耗S-P10：Q11 packed配置非作者复核

app_protocol_review_01，作者输入7ab7fd20e8c765db2433abddda2ea606e4ddb53f，主窗取走后非作者交1a2651dfb78016268ca884ec9c01daa754db817c限定接受/纠正0/新增0。可测144秒，之前读取未计。对象和来源沿S-P05：主仓完整报告app-protocol-research-01-0041-20261025.md、analysis同stem合同/verify.py/原字，whole-rom-private-008/006真824/364B、deferred functions/1 caller。

复核范围是两属性共u32 setter→C1/C2 refresh/变化门→已验cmd67调用及通知低8位；只核bits0–3/8–11→各byte0高4位/SB保留→反向0xb8；refresh比较完整byte2、NULL不改/未映射位更新byte2但bool可false；setter不写byte2，重复可抑制非确认；镜像完整u32而通知p&ff。继承B10/B11 getter及charge-complete record22，止a00a533a/a01951e2/公共API，不核item14生产或物理生效。输入按值、静态槽、borrow item、wrapper栈payload寿命与规格名限制。独占app-protocol-review-01-0041-20261025及同名branch，protocol-review01。预测3–5分钟，阶段<1/1–2/1/1，据作者240秒/Q07非作者115秒；最小派发为同Q11非作者合批核以上差集、独立原字/旧卡片、不运行作者脚本、静态独占本地commit。

### 已消耗S-P11：Q14 cmd59状态生产及refresh可见性

app_protocol_research_02，交1f3f86fa7f376d0bbd78d94b17f0e3ce9f19fb9b。独立真seed为 `D:/Documents/PlatformIO/Projects/cuktech-ap01-firmware/reverse/analysis/uart-response-0041-20261023.json#/functions/0/normalized_result`，EID ev_6f9f82e5daf0540a1c24a0b85daa2e394785391692765e5e3e100eb7b37ed94c、原profile bcefdee5092076e55636e077b45523e203f4b870ae7b7ab547945ed1b8162279。0xa00a874e..8756比较0x59→0xa00a973e；正常writer窗口0xa00a973e..983e。S=load32(0x62fcb6c4)为raw缓存，T=load32(0x62fcb2cc)、A+index*0x1a8为item。0xa00a97bc indexed byte→97ce SB item14，97f4→9800 SB item15；9828直接赋mask1000/2000，9830同步notify(i&ff)。这不是cmd67因果确认。

既有N02仅51/52/56、P17仅63/65、P10仅查询调度、UART response14用例不含59、E07只是消费者引用；upper-MiIO卡不覆盖硬件writer。相交Q11是已交作者的另一读端，不重验其转换/submit，两个writer窗口不同。有限只copy请求表达式/count重读/两byte/通知/既验refresh条件接合；继承a0191652、B19/B21正常CRC与活动cmd门、E01/E02借用、P10慢组59。止MCU/copy/queue、S/T全局数量与寿命；不做异常回放或无种子找67。

验收copy n与实际loop数不同来源、mask覆盖非OR、相等仍query推进、S缓存但T/count/A重读、借用/后续refresh非即时必达/非物理确认。独占app-protocol-research-02-0041-20261025、branch codex/app-protocol-research-02-20261025，protocol02。预测5–9分，阶段1–2/2–3/1–2/1–2；实际可测154.379秒前读未知，说明仍高估，不因此扩量。最小派发为同协议完整正常观测阶段，上述旧seed/有限差集，静态独占commit。

### 已消耗S-P12：Q12 sysconfig非作者复核

app_settings_review_01，作者6abd0bbd749d8e34634bf819c294df50fb33b811已merge/转存。主仓报告 `D:/Documents/PlatformIO/Projects/cuktech-ap01-firmware/reverse/reports/ap01/app-settings-research-01-0041-20261025.md` 与同stem verify.py/result.json；旧072 reader、071 writer、L03–L06/M01–M02是必要继承。只核reader332B/default32B及接合，不运行作者脚本、不重验算法/FS。

验收头{8,0,0}/callback实参只调用边；read返回不检查；完整u32 a0比零扩展G+6 u16；非零读H两分支先close再keep/reset；默认SW0到G0..3再SH0164于G4，仅覆盖6B；失败writer独立新H、init无setter通知/保存成功门；G2/G3默认0接消费者。FS实际保证/subscriber寿命/100单位保持未知。输出app-settings-review-01-0041-20261025、同名branch，settings-review01。预测2–4分，阶段<1/1/1/1；据作者可见216秒、Q10非作者131秒。非作者最终交3e66b968c63b61c92bf505be7096b7b9378d94cc，新增/修正0；总130秒、分析106秒，不能混同。最小派发为Q12同认领限定非作者独立原字/合同核，静态独占commit。

### 已消耗S-P13：Q13 manager-T启动交接非作者复核

app_ota_review_02，初始作者63dc73afe87399d6405d0a612db75bea3cc0298d已merge，修正输入f935f1c9602c6767998cde2f3289c26067ab3474待同题确认。主仓报告app-ota-research-02-0041-20261025.md及analysis verify.py/raw-windows.json；主仓upper records205/185/271/313、upper-miio-b旧offer/selector真合同。只核M/L/T参数同一性与旧接合、新308B start，原offer134B不算新。

验收B=*(arg3+4)、M=B−0x128、L=M+0x1b90、T+8=L；offer可多T接受/params同步borrow；selector首start0停，失败先state0再锁内T+48(T,C)后继续；start stackD0x120借T+b0 URL、四63B字符串/末NUL、u16/u8写宽度、0xa01148bc→a012193c(*(L+c),D,0xa060fd34,T)且L非service；清T+270/70后写T+2b4；接受数/start/selector/RPC返回分层。止a012193c/table targets/HTTP/F/sink/验签/安装/取消，D复制/T异步持有/完成仍未知。对象alloc/free范围按上述补修收窄。独占app-ota-review-02-0041-20261025、同名branch，ota-review02。预测3–4分，阶段<1/1/1/1；作者195秒采样非完整总。最小派发为Q13同认领独立非作者上述合批、旧卡片及原字，不运行作者脚本，静态commit。

### 已消耗S-P14：Q14 cmd59非作者复核

app_protocol_review_02，作者1f3f86fa7f376d0bbd78d94b17f0e3ce9f19fb9b已停并merge/转存。主仓报告app-protocol-research-02-0041-20261025.md与analysis verify.py/原字；原seed及profile沿S-P11。独立核358B之外本题74边界/3indexed/2SB/3JAL及正常writer合成，不重做Q11转换器/公共API。

验收copy n=(u8[62fcb01c]<<3)&f8非T.count*8；S为pointer且helper后加载；T/count/A每轮重读、S缓存；S[8i]/[8i+1]完整u8→item14/15；mask直接覆盖/同步notify(i&ff)，相等仍推进；Q11同14读端仅后续refresh时可见/受byte2门，无即时边或特定67因果。止S/T全局寿命/数量不变量、item15新消费者、底座物理确认。独占app-protocol-review-02-0041-20261025、同名branch，protocol-review02。预测2–4分，阶段<1/1/<1/1；据Q14作者可见154秒、Q11review144秒、Q10review131秒。最小派发为Q14同认领非作者独立原字/正常合同、静态独占commit。

### 可派S-P15：应用typed结果收集、延后消费与发送边界

候选app_property_research_01，新认领由主窗串行登记；同接口整阶段不是为库存拆四wrapper。问题正常wrapper输入→20槽收集→延后result/properties_changed构造→发送调用边/必要持有。真实对象count=0x62fcb044、数组base0x62fcb048、stride0x20、输出buffer0x62fda0a8。既有deferred/F01/Q11仅核caller实参并笼统称通知，未解释收集/延后消费；本预调研不先作业务纠正。upper-miio-a/b/routing领域卡已按接口精确核，无该完整合同。

必要绝对真body材料：

- `D:/Documents/PlatformIO/Projects/cuktech-ap01-firmware/evidence/rea-0041-20261017/evidence/whole-rom-private-20261023-144.json#/structuredContent/normalized_result`，0xa0195034..50e3 176B，ev_89e3ae9d1a09935389925ac12a464c788cae672e9b1631dccf95d099355d501f。
- 同绝对目录 `whole-rom-private-20261023-159.json`，0xa01b5d70..606b 764B，ev_d130f16f50acaa43d7f20c98370e94baef9d75355aea1e27d2af68d7ebee7db2。
- 同绝对目录 `whole-rom-private-20261023-024.json`，0xa00a2578正常GET/SET两处真实a01b5d70(0)调用；只必要前后窗口，不重导整个dispatcher/接收parser。
- 同绝对目录 `whole-rom-private-20261023-021.json`，0xa00a116e..12cf 354B，ev_e56e7bf85b43acfb10c1c6065be0dd6f8d6ff82cbb1c1c92f3665a396e97610e，只正常字符串持有与queue API调用边。

独立JSON无structuredContent时解析content[0].text同字段，旧Evidence/profile各自保留。0xa01950e4..5105 34B、0xa0195106..5121 28B、0xa0195122..5143 34B、0xa0195144..5165 34B四typed wrapper只有extent和direct a0195034，准这四入口必要新原字，不宣称旧body存在。formatter/JSON/strlen/queue算法公开API止步。

有限依赖：type/param6/result flag、byte/short/word内嵌及string指针保留、count>=20门与递增时点；consumer count重读/最多20、状态halfword有符号消费、mode0/1、512/0x201边界及早退；必要a00a116e正常调用参数/返回和消息借用/持有。止formatter、MQ、接收parser、全部属性、云/设备执行，不取真实配置或安全材料。

**count reset没有已证写端，不能虚构。** 144是递增writer，159为延后reader；024的GET前置真实调用0xa00a12d0(0)只保留锚点，022为bad-instruction截断且E07明确旧extent不覆盖后面的未知owner，禁止据reset假设展开它。验收将“外部给定有效count”的收集/消费独立阶段与reset/并发/共享buffer寿命未闭分开。只在已有144/159/021精确写端中回答有无本层清count，未取得即保留未知，不全ROM负搜。此包不宣称完整跨事务接口闭合。

验收wrapper实际类型/宽度；数值复制与指针borrow延续至consumer的区别；result flag的消费；buffer/length边界与发送前后资源/返回门；caller调用不等云通知或云成功。相交Q11/Q14仅引用caller参数/peer item来源，不读其业务转换/原字窗口；Q12 G、Q13 T不同对象，无live作者后续依赖。独占app-property-research-01-0041-20261025报告/analysis，branch codex/app-property-research-01-20261025，property01。

阶段旧覆盖/四wrapper1–2、typed收集/consumer3–5、正常send寿命1–2、原字交付1–2=6–11分，中低置信；按近期充分定位约1K代码任务240秒校准，不把30分目标抄成预测。最小派发：`登记0041新认领/最新基线，沿144/159/024/021真body和四已知typed wrapper短入口恢复同count/20槽数组的收集→延后result构造→正常send边界；reset只已有写端，不扩截断a00a12d0，不读公共formatter/MQ内部。有效count前提和跨事务断边明确，静态独占commit，不推送，6–11分钟。`

最新消耗：S-P15已登记Q15 app_property_research_01在7f7c37a派发，当前库存0/3、缺3，Q15复核未交付只条件项。Q13非作者7f8caefd4d90db88f244164e9afe9a4329c933ff接受f935f1c，行为纠正0/范围表述纠正1；结束17:08:15，暂停/补修等待不能精确拆分，不能当有效工时。当前有界后备尚未形成新的完整可派包；连续2–4分短任务消耗超过准备速度，不能靠短配置/公共库或无种子搜索冒充3包。

## 第四轮：相关完整阶段与3份提前队列

本轮已取走S-P16/Q16 OTA bridge、S-P17/Q17网络政策、S-P18/Q15复核、S-P19/Q18 RPC property、S-P20/Q19 event、S-P21/Q20 subscription。当前新备S-P22/Q16非作者、S-P23/Q17非作者及S-P24 named-property研究三份；主窗未取走时为3/3，实际派发后按消耗更新。Q18/Q19/Q20未交成果的复核仍只是条件项。

以下均继承本报告首节0041身份、静态限制、原件绝对路径、派发前唯一管理登记及最新管理基线；PREP本树基线不移动。研究者必须是独立上下文/独占输出、本地精确路径commit、不推送。预调研只查足以定题的父级卡、现有body/metadata和确切表，不完成作者业务取证。为Q16定题额外只读ROM0xa060fd34的24B表，未执行任何目标。

### 已消耗S-P16：Q16 constructor持有与六槽→七槽adapter

app_ota_research_03，commit3972bfa0277a9496961d498cc71d07eee8c8544c已停。问题Q13 D提交→request复制/借用→HTTP六槽adapter对应用T/C七槽的真实桥接。必要证据绝对路径 `D:/Documents/PlatformIO/Projects/cuktech-ap01-firmware/evidence/rea-0041-20261017/evidence/upper-complete.evidence.json` records313/205/185/271及主仓app-ota-research-01/02、review-01/02；`D:/Documents/PlatformIO/Projects/cuktech-ap01-firmware/evidence/rea-0041-20261017/evidence/miio-recovered.md` §10已解释HTTP六槽引擎调用侧，upper-miio-a/b/routing无本批adapter/constructor完整合同。Q08/Q13均明确止边，不读live作者未完成果。

真固定表0xa060fd34 24B为 `763a11a000000000ac3a11a04e3b11a0025711a0f8f910a0`，六word `[0xa0113a76,0,0xa0113aac,0xa0113b4e,0xa0115702,0xa010f9f8]`。新研究入口只有extent/directcall，未找到旧body：constructor0xa012193c..1dc1 1158B、open0xa0113a76..3aab54B、write0xa0113aac..3b4d162B、HTTP close0xa0113b4e..3ba9 92B、error0xa0115702..57fd252B、stats0xa010f9f8..fadb228B，共1946B；shared0xa011398a..3a75 236B仅这些adapter真实T状态/应用槽交接。允许必要新原窗，不能把extent当正文。

有限依赖：D值/URL字符串复制和指针例外、T userdata、R本层分配/入队失败回收、adapter ABI/长度/返回/状态及正常完成/错误归还的原序；shared状态及业务通知只到调用边。止HTTP worker0xa0123dca、FS/hash/TLS/JSON/queue/allocator内部；不重做Q08 F/file-open或Q13 start，不展开install/签名/board。error中0xa01143de/0xa01ac65c新callee只参数/返回，跨owner另报。验收D/T真实寿命、六槽到七槽不能按同名硬接、缓冲借用/状态先后/失败回收；保留并发取消/T销毁/安装未知。

阶段覆盖1–2、constructor4–6、五adapter/shared3–5、原字交付2–3=10–16分，中低置信，约2KB新原窗/多callback，不抄Q13仅308B的预测。作者可测17:12:46→17:17:36=290秒，前读未知；Q16实际发现HTTP close→T+40 install，而error先T+44普通close，不能拼接正常HTTP结束为Q08归还；D/URL复制、TLS/T浅持有、queue失败freeR等为作者待复核结论。独占app-ota-research-03-0041-20261025，同名branch、ota03。最小派发：`仅上述原始constructor与table五adapter/shared的正常持有/归还接口，旧引擎调用侧继承，新原窗2182B有界，未知指令原字留存，不执行，独占commit交付。`

### 已消耗S-P17：Q17同N ready、外部门与probe

app_network_research_03，bc4ed028de4aa5d60f0fc88578f2f66bd278192e已停。继承Q09及非作者4计时门/monitor，不重做716B或5644B。绝对种子 `D:/Documents/PlatformIO/Projects/cuktech-ap01-firmware/evidence/rea-0041-20261017/evidence/upper-complete.evidence.json#/records/89/normalized_result`，ev_4150d456a78d9d2a6c00fda793101e8915ff107084a8356d31e91552e2b072de；主仓miio-recovered §6/10及app-network-research-02/review-03。真实caller ready→0xa0067be6(N)、B=1→0xa0195ce4(M,N)、state2触发0xa006e768→0xa0067c20()，保留state1例外。三个只有extent的新入口58/128/374B共560B，分别0xa0067be6..7c1f、0xa0067c20..7c9f、0xa0195ce4..5e59。

查较晚qemu-ota-validation及qemu-rtc-display已确认0xa0069356安排4000ms reboot，26B直接继承、不重读、不运行QEMU；不能再以动作未知为新题。upper卡无三helper合同；前两directcalls锁/日志，第三为业务适配，下游0xa0119638/socket/format只API。对象N=0x62fca7f8/M=word(N)，另有callee真实外部owner必须区分；不预设三函数同owner。

范围只字段宽度/复位/许可原义、probe局部描述符和请求数据来源/借用/返回、本层资源及已有caller动作门；止G生产者、a0119638、callback、新私有callee/网络/driver/crypto/全writer。验收请求≠联网/完成，保留单位/外部copy未知。阶段1–2/3–5/1–2/1–2=6–11分，中低置信，Q09采样250秒作类比；作者可测166.031秒，前读未知。其作者结果为ready SW0/解锁后SH1，另G政策，probe20B及7000原值，不先当单位ms。输出app-network-research-03-0041-20261025，同名branch、network-research03。最小派发：`三精确入口及同caller正常接合，旧reboot叶继承，真实N/M/外owner分账，API止边，静态独占commit。`

### 已消耗S-P18：Q15 typed collector非作者

app_property_review_01，作者bfed293a5b32c7d0538e41786a2ece71eeccfe82已merge/转存，绝对报告 `D:/Documents/PlatformIO/Projects/cuktech-ap01-firmware/reverse/reports/ap01/app-property-research-01-0041-20261025.md`，analysis同stem verify.py/bounded-evidence.json.tmp。三真body1294B沿144/159/021、四wrapper130B、024局部consumer(0)，不运行作者脚本、不重验deferred/Q11业务。

验收stride0x20=32B而非十进制20；count signed>=20门/六参/完整type比较与byte存储；SH0状态由LH消费；type1/2 byte/type3 half/type4 word复制、type0 string借用到consumer完，flag取caller低byte。consumer每轮重读count/最多20、mode0/nonzero、prefix过长早退/value过长只省value继续、type5/9无完整构造链；513/512不是B容量证明。send附CR/0x101 format、unsigned返回<=256门、queue handle重读、仅−1失败、consumer忽略返回。止formatter/MQ、count reset/截断a00a12d0/并发/云端，不将命令文本当JSON或collector调用当云通知。

阶段<1/1/1–2/1=3–5分中置信；作者采样222秒、成稿190秒不同端点，Q12review总130秒作类比。独占app-property-review-01-0041-20261025，同名branch、property-review01。最小派发：`Q15同认领非作者仅typed收集→consumer→send给定有效count阶段，独立原字/字符串，不运行作者脚本，保留reset/队列完成未知，静态commit。`

### 已消耗S-P19：Q18 RPC property staged生命周期

app_rpc_property_research_01。问题cmdrpc get/set_properties输入→72B staged record/raw值持有→result/error回调→同list归还；不是Q15 UI数组。领域父级绝对文件 `D:/Documents/PlatformIO/Projects/cuktech-ap01-firmware/evidence/rea-0041-20261017/evidence/upper-miio-a.md` §0xa00bb880/0xa00bbb6c已解释根局部，EIDs ev_ccf8947ba0ace57f9a4011dc3f0596e163b52e67c237c5a2e8e0ab7161b3f7a0 / ev_356b7dc60bc5a619a8c2c7af6a983114de52ca84bdf70843a8c5379ef8af65ce，明确留下record/value/callback cleanup边。另一profile真root在绝对upper-complete.evidence.json records59/164，ev_29f77800b52f12cedb687a2038119b3cf1012aabd3390128a8e525a327669e0a / ev_7de861b43b55102a6679af754b6a5508870ea194da05c0545639ff53ec2960c3，各profile分账。

对象ctx+0x228/+0x22c staging head；根用局部72B DID/IDs/raw value+len调0xa00bb67e，成功装ctx+6c result/get0xa00be8ca/set0xa00bea78、+70 error0xa00bb0c2/0xa00bb0dc；失败a01afb26。准新精确原窗（只有extent，无旧body）：stage0xa00bb67e..bb6d9 92B、两result0xa00be8ca..bea77 430B及0xa00bea78..bec0b404B、两个error各26B；shared0xa00bb6da..bb80d308B仅同property响应适配。0xa00bb80e格式层及generic allocator/listclear到接口，不读a0058386/a01afb26公共库补量。作者发现必要matcher0xa01adc0e(head,&local_record,status)96B只同head正常匹配更新，已由主窗另核登记；预调研仅给metadata无旧卡，不并行完整取证。

有限回答record拷贝/raw string深copy或借用、doc与原JSON寿命分界、回调ABI/记录匹配/状态和输出、成功/错误清链时点/字段归属及callback槽保持。排除v3/其它action/全handler/真实云应用/权限实验；ctx全寿命并发未知不追。验收不能从doc释放推raw已copy，不能把callback0当设备已应用。阶段1–2/2–3/4–6/2–3=9–14分中低置信，约1.3KB新回调，提前即交付。独占app-rpc-property-research-01-0041-20261025，同名branch、rpc-property01。最小派发：`继承两root卡/真body，只同staged head输入到result/error和归还闭包，必要新helper/回调原窗，公共JSON/list边界停止，静态commit。`

### 已消耗S-P20：Q19 cmd.event输入与flush

app_event_research_01。父级绝对upper-miio-a.md §0xa00ba444 cmd.event，ev_a443a9d8aa26648e225c4f146153d31ea375d78457793653893e2aac63e5e293，明确borrow argv、0xa011408a回0才0xa01af798/ok，留下queued ownership。另一profile真root绝对upper-complete.evidence.json record233，ev_b7f9c05652b41f5486cbdecf96f07079792f9d25bf48dcfb216ec0448259d9a0。不重做root/tokenizer，近期无callee专项。

只准四metadata入口新原窗：0xa011408a..4149 192B、0xa0113f6c..4089 286B、0xa011c204..c3af428B、0xa01af798..fa2b660B，共1566B。对象从component参数追实head/entry，不因同event名认F11对象；name/argv copy/保留、record字段/时戳、分支与锁、flush描述符、本层回收/返回/callback ctx为一个完整输入到handoff阶段。不得按名字猜即时/队列分支。止0xa0110984/0xa0113340/0xa0116ad0参数返回、公共JSON/formatter/allocator/queue/transport；不扩真实设备/云接收/认证。与Q18 staged head、Q15结果数组不同。

验收借用输入到owned/callee边界和归还，root ok不等event被处理；保留外部submit复制/并发未知。阶段1–2/3–4/3–5/2–3=9–14分中低置信，1566B新callback；独占app-event-research-01-0041-20261025，同名branch、event01。最小派发：`四真实新入口正常event记录/分支/flush原序，根borrow继承，API到边即止，静态独占commit，跨owner先报。`

### 已消耗S-P21：Q20 subscription正常移除

app_subscription_research_01。父级绝对 `D:/Documents/PlatformIO/Projects/cuktech-ap01-firmware/evidence/rea-0041-20261017/evidence/upper-miio-b.md` §0xa0115f7e/§0xa011d202，EIDs ev_c9c083522ddaa5a7c350aad4fd271a4e9fd7998e751e2f4db869cbe71d44272a / ev_d4942aedf1d2ed7b7ee29db9fb686a68f9f7155c6d5706b91f8c5b96da16a7c8；另一profile真root为绝对upper-complete records245/48，ev_c22e8476e961b1745b154b77d021ebafc0cedf6d943f1eb10ef9c9b712f6e21b / ev_221426fb577a1866be99a4825a47510530b45aec1e8d468aed90c0e391e9f036。根成功创建/请求门/88B descriptor已有，不重做已知allocation-failure缺陷或任何异常验证。

对象peer head0x62fcab94/topichead0x62fcaba0/mutex0x62fcaba8。有限新入口0xa011d10e..d201244B、0xa01abe54..befd170B、0xa0113c8a..3f6b738B、必要0xa0118b08..8b5376B、0xa011bffe..c0d9220B/0xa011bfc4..bffd58B、0xa01188a6..89b7274B，均metadata非旧body，约1.8KB。问题精确/aggregate有效移除→双向边/计数/空对象/类型登记原序；matcher0xa0118a40及generic allocator/unlink/formatter止API，不扩fanout/全部topic语法/OTA/无线/crypto。N03 UiIFace/Q07 policy P是其它头，Q19只生产事件不做本graph更新。

**作者原字纠正准备假设：0xa0113c8a是只读graph diagnostic dump，无unlink/free，不能按旧父级“cleanup”或本包问题名称当已证清理；真删边/归还在d10e/bffe/bfc4。** 0xa01abe7e原word8bc7994c未知完整保留，不改模型。后续复核须核dump只读与调用时点，这不是新body/扩库许可。验收正常有效peer/topic到graph变更/归还/status，外层0不当移除成功，保留并发/真实投递/manager销毁未知。阶段1–2/3–4/3–5/2–3=9–14分中低置信。输出app-subscription-research-01-0041-20261025，同名branch、subscription01。最小派发：`已有有效root/descriptor前提下，仅上述具体graph移除/归还/登记与dump边，原字未知保留，公共库停止，静态commit。`

### 可派S-P22：Q16 OTA bridge非作者

app_ota_review_03，作者3972bfa0277a9496961d498cc71d07eee8c8544c已停止。主树merge后绝对报告 `D:/Documents/PlatformIO/Projects/cuktech-ap01-firmware/reverse/reports/ap01/app-ota-research-03-0041-20261025.md` 与analysis collect.py/verify.py/raw-windows.json；源前提沿S-P16。只核2182B七窗口/24B表、Q08/Q13/HTTP调用侧必要继承，不运行作者脚本。

验收D/URL及四串复制、TLS/T浅持有；R单分配布局/timeout min/queue&R及非0freeR原错不freeT/C；5完整厂商word原字段/旧SINC分账；open读*total→T+38、write T+3c借可写buf/要求len推进却返callback原值；HTTP close先state4/统计→T+40 install，0才可T+48 completion，不能接Q08普通close；error先T+44普通close再有限重试/state7/selector；stats64B不补NUL/不持有S；shared先状态/非负进度、解锁后通知栈snapshot未知。止install/完成内部、a01143de/a01ac65c、snapshot消费、HTTPworker/FS/hash/queue；保留正常F/H/fd归还/T销毁/配置寿命/取消重入未知。

阶段<1/1–2/2–3/1=4–7分钟中置信，作者2KB新窗290秒可测非完整。独占app-ota-review-03-0041-20261025，同名branch、ota-review03。最小派发：`Q16同认领非作者，独立原字/5vendor/表/ABI与有限归还，重视close→install纠正而非同名硬接，静态commit。`

### 可派S-P23：Q17网络政策非作者

app_network_review_04，作者bc4ed028de4aa5d60f0fc88578f2f66bd278192e已停。主树绝对报告app-network-research-03-0041-20261025.md与analysis verify.py/verification.json/inspection.txt；真源与有限旧caller沿S-P17。只核560B/20关键字段及caller门，不重验Q09716B或旧reboot叶，不执行作者脚本/模型。

验收ready锁内SW0 N+1d0、解锁后SH1 N+1d4且非bool返回；许可另G=0x62fcad78/G+0锁/G+8 byte，15/20/30位掩码与50→1，state2返回0才请求/state1不套门，不命名G枚举/找writer；probe prefix3/domain16/DNS成功才R20B：ip、u16 8053、cb0xa0068a26、N、7000原值/padding未知；0xa0119638(M+128,4,"otn.ntp",R,20,M+e8)原返回/caller忽略。三对象不强合、7000不假设ms，R/buf寿命及APIcopy/callback未闭。止a0119638/callback/DNS/formatter/调度/锁/日志，不新callee或Gwriter，probe0不是联网完成。

阶段<1/1/1/1=2–4分钟中置信，作者166.031秒可见非完整，Q12review总130/Q14review142秒参照。独占app-network-review-04-0041-20261025，同名branch、network-review04。最小派发：`Q17同认领非作者，三helper及必要caller对象/宽度/返回/局部借用，独立静态原字，保留全部外部持有断边，commit交付。`

### 可派S-P24：cmd.props named-property条目阶段

候选app_named_property_research_01。问题正常cmd.props name/value更新→组件条目持有/替换→即时报告调用及显式归还阶段，独立于Q18 MIOT staged72B/ctx228和Q15结果32B数组。领域父级绝对upper-miio-a.md §0xa00ba35a根卡ev_32e5d4799b24d8b2676f0461c9349f5a6ec6980ea777ad502e1b14f4c1c04785只解释偶数pair循环/首非0停止/既更新不回滚，明确typing/retention/duplicate/persistence未闭。另一profile真root绝对upper-complete.evidence.json record256，ev_cae45a84ae40a1571e17792b4854ee16d8f5d44a3f6fe046f24ad031b85410da。root/tokenizer不重做。

真实callee0xa0116a3a(component,name,value)→0xa0116900/0xa011c3b0；0xa0116ad0被Q19 flush调用但Q19明确止调用端、不读body。仅四metadata新入口（无已定位旧body）：0xa0116a3a..6acf150B、0xa0116900..6a39314B、0xa011c3b0..c513356B、0xa0116ad0..6b59138B，共958B。对象从component真实head/entry决定，不按和event函数形状相似认同。Q19独占0xa01af798及event四body，本包不读/重验/依赖其未交结论；本包独占named-property四helper。发现同event节点/跨owner须报冲突并暂停增量，不以名称先认同或先否认。

有限typing接受到JSON/解析API；同名更新/替换/复制或借用、node字段/长度/旧值归还、锁/即时报告参数/返回、0xa0116ad0真实对象/计数/逐条行为。不要预断cleanup函数角色。止0xa0110984/0xa011c0da参数/返回/局部buffer、generic allocator/JSON/formatter/queue/transport，不追全部props/source writer/persistence/云送达。验收name/value borrow到条目/报告/归还原序、status/共享头身份与并发下游copy未知；不能只因listclear名称说已free全部字段。近期报告除Q19止边无四helper合同，upper卡只有root引用，无未交作者依赖。

阶段coverage/对象1–2、update/typing/retention2–3、report/归还2–4、原字交付1–2=6–11分钟中低置信，958B新私有字段/两路径，参考Q15齐材222秒但新body增加不确定性，不追库凑20–40。独占app-named-property-research-01-0041-20261025，同名branch、named-property01。最小派发：`登记新认领，继承cmd.props根，只四确切helper的正常名称值更新/持有/报告调用与真实归还，Q19 flush不读、跨owner先报、API止边，静态独占commit。`

第四轮最终状态（主窗确认）：S-P22 OTAreview、S-P23 NETreview、S-P24 named-property均未派，真实库存3/3；当前执行Q18/Q19/Q20，不把它们的未来复核算库存。Q20作者二次实字核正覆盖上述中间说法：a0113c8a本层为dump，但0xa0113ca8入口先调用a011bffe，shared stale-peer清理有副作用（now−peer+0x10按unsigned差>78）；所以不能称整个调用只读或无清理。0xa01188a6仅9类计数与delta，并非外部callback注册/注销。前次‘cleanup’→‘只读dump’两项历史表述保留作纠正轨迹，当前Q20验收/复核必须采用本段最终事实，不因中间说法漏掉callee清理。

## 第五轮：S25/S26/S27三份非作者完整包

第四轮S22/Q16非作者、S23/Q17非作者已从库存取走（基线8782ea6）；S24已收窄为820B并登记Q21补位。新作者Q18/Q19/Q20均已停止交付，复核现可计可派，不再是条件项。S25/S26/S27完整包均已交主窗，未取走时3/3；实际派发仍由主窗串行登记。后续每份新包要求**执行者第一工具先取UTC clock，再读取材料**，结束、提交、暂停/等待分别记，token不可得不估算；避免重复缺首时钟。

### S24对象纠正与正确范围（已消耗为Q21）

Q19新交付确认 `a0116ad0(H=C+0xdc,id,0)` 属于event恢复/按id处理边，不能从函数邻近或形状放进named-property归还族。S24在尚未派发时已向主窗纠正并删除该138B body，正确独占范围仅0xa0116a3a150B、0xa0116900314B、0xa011c3b0356B，共820B。问题仍是名称值更新/替换持有/即时报告交接；旧节点替换/回收只从6900本体证明，完整publication回收保未知。Q19 flush及a0116ad0本体不在S24范围；如果追到同event节点/跨owner先报冲突。原958B准备记录保留为纠正历史，当前派发/验收必须用820B边界。

### 可派S-P25：Q18 RPC staged property非作者

候选app_rpc_property_review_01，同Q18认领，作者72a10cb66106a1a1a66ba4f62a75c4213fa58dac已停。合并/转存后必要绝对报告 `D:/Documents/PlatformIO/Projects/cuktech-ap01-firmware/reverse/reports/ap01/app-rpc-property-research-01-0041-20261025.md`，analysis同stem verify_windows.py/windows.json/windows.txt/parent-links.json；未合并时独占rpc-property01树同路径。独立源是主仓upper-miio-a根卡、upper-complete records59/164，前述不同profile分账；新七窗1382B为stage92/result430+404/error26+26/serializer308/matcher96。不重验root/public list/JSON，不运行作者脚本。

验收H=ctx+0x228同head，calloc84后copy72到N+8为浅拷贝、N+0x50=-4004；matcher两ID，type3额外第三ID，不比DID，只首个默认−4004项回填status/ptr/len，caller忽略返回；回填仍−4004不等一次性完成。callback ABI、token适配与local清零，四get厂商load完整raw未知保留；独立字段/已有SINC若能对应仍分账，不把同族/对称推断升格为独立ISA验收，不运行/改模型。

serializer输出普通siid/piid或type3 IID、code与ptr+len raw value，写后清字段不free指针；**关闭JSON对象后、finalize之前清H**，finalize失败链也已清。两error只清H返−1，不序列化error JSON、不调用ctx+64；result把栈descriptor交ctx+64及ctx+68，返回间接回调原结果；ctx+6c/+70未清。原set raw跨ACK是否必须保活取决旧a00bb80e接口，本复核不读它或宣称deepcopy；响应value只同步borrow。止tokenizer/JSON/清链公共API，保留ctx全寿命/并发/取消/真实设备应用，callback0不当应用成功。

独占app-rpc-property-review-01-0041-20261025报告/analysis，branch codex/app-rpc-property-review-01-20261025，rpc-property-review01，最新管理基线。阶段材料<1、stage/matcher1、双result/unknown/清链1–2、serializer/交付1–2=4–6分中置信；作者成稿317秒/外层348秒不同端点，前读未知，Q16复杂2KB复核4–7作参照。最小派发：`Q18同认领非作者，只七窗口和根接合的浅持有/匹配/输出清链/回调合同，4custom字不升级语义，首工具clock，静态独占commit。`

### 可派S-P26：Q19 event owned记录与单项flush非作者

候选app_event_review_01，同Q19，作者1d7890db5a6288260bf576122fdaa01d300e9075已停。必要绝对报告 `D:/Documents/PlatformIO/Projects/cuktech-ap01-firmware/reverse/reports/ap01/app-event-research-01-0041-20261025.md`，analysis同stem extract.py/verify.py/raw.json/inherited-root.json/checks.json，未合并时event01树同路径。只四窗1566B/508raw/20calls/9vendor/7strings及upper root233必要前提，不执行作者脚本/目标/模型。

验收n/name正常门与验证器API边；先a011c204即时旁路且忽略返回，再锁C+e4→record(H=C+dc)；calloc0x88+sum(strlen+1)、event.name33B、最多16指针都指own尾部、逐串copy+NUL/尾插链、timestamp/tick/过期原值不猜单位。即时D/K均栈、P0x558先交a011c0da后free。flush P0x559/builder0x558、锁内跳pending/expired先unlink再free；retry>0且旧id非零才替当前id；序列化失败继续且不标pending；首成功写R+74/id与byte+70后break/解锁，一次最多1项；a0113340后无论返回都freeP，非0只重新锁调用a0116ad0(H,id,0)到API，不能声称删记录/清pending/retry已证。normal R不直接free、只有过期本层free；callbacks0xa0116db0/0xa0116b5a仅指针，外部copy/完成未知。root ok仅记录返回0，与即时/flush发送成败不同。

9完整vendor word按原字段与已有SINC分账，不NOP、不执行/改模型。止a011c0da/a0113340/a0116ad0/formatter/JSON/queue/allocator内部，不抢S24已删除的event恢复body，不扩C生命周期/并发/云接收。输出app-event-review-01-0041-20261025报告/analysis，branch codex/app-event-review-01-20261025，event-review01，最新基线。阶段<1/1–2/1–2/1=4–6分钟中置信，作者268.609秒采样前读未知/Q18相近差集参照。最小派发：`Q19同认领非作者，只owned输入/即时旁路/单项flush及本层归还，a0116ad0止边不猜语义，首工具clock，静态独占commit。`

### 可派S-P27：Q20正常subscription删边/过期清理非作者

候选app_subscription_review_01，同Q20，作者64326568681c7d1970e911e92a4e49de31cca825已停。必要绝对报告 `D:/Documents/PlatformIO/Projects/cuktech-ap01-firmware/reverse/reports/ap01/app-subscription-research-01-0041-20261025.md` 与analysis verify.py/原字，未合并时subscription01同路径。独立核7窗1780B和upper-miio-b、upper245/48的root锁/flag/响应，不同profile分账，不重做sub创建/失败缺陷。

验收G=0x62fcab6c九word类型计数/peer-topic哨兵与双方独立edge；精确erase非0才各侧减1，空P先/空T后释放，typecount先Tfree；找到T最终0非至少删边保证。aggregate flag0使type5/6跳过，缓存next/不同类型target偏移，返回忽略。a0113c8a本层dump但入口0xa0113ca8先a011bffe stale清理，失败root也可能变更其它peer；stale每peer重读now、unsigned差>0x78而非>=，无单位假设，不看erase返回直接减/T signed新值<=0，与精确==0分别核。0xa01188a6只九类word+delta，没有外部callback注册注销。

6UNKNOWN全部raw保留，四preincrement编码族只按已有规则/字段及普通callsite支持作限定，不执行/改模型，不升级为独立ISA认证；0xa0113e54/58只日志未知不当graph依赖。删边/sharedcleanup先于100B响应，outer0不当删成功/送达；公共unlink/free/matcher语法止API，不扩fanout/Gwriter/并发/总manager销毁。输出app-subscription-review-01-0041-20261025报告/analysis，branch codex/app-subscription-review-01-20261025，subscription-review01，最新基线。阶段<1/1–2/1–2/1=4–6分中置信；作者只有结束17:25:43.373、开始未知，不能算全耗时；Q18/Q16相近窗口复核估算作参照。最小派发：`Q20同认领非作者，只正常graph删边及stale/dump/typecount差异和6unknown限定，首工具clock，静态独占commit，不运行作者脚本。`

第五轮实际消耗补注：主窗曾确认S25/S26/S27短暂3/3，随后取走S25/Q18与S26/Q19补位，最新库存仅S27，1/3、缺2；Q21作者未交复核只条件项。Q16非作者06a5197e446727c7b1475a48156d6b2fc8e18b9a，语义纠正0，仅L+0x10=-33001/通知M+payload精化，采样17:25:38.086–17:27:42.687，前读未知。Q17非作者d646b3c2dd39ac365484d25170acc887f067a94e，纠正/新增0，采样17:25:42–17:27:50=128秒，前读未知，不冒充全工时。

## 第六轮包段（后续派发可直接引用包ID）

S27已取走Q20非作者，S28/Q22 action研究、S29/Q21非作者、S30/Q23身份构造研究、S31/Q24 publication均已由主窗取走。新S32为Q22已交作者的非作者包；尚未取走时可派1/3，不能把未来Q23/Q24复核算可派。报告和本机ignored queue始终是候选记录，主窗唯一登记不变。所有新任务首工具clock，静态/不执行/不改ROM生产配置模型/独占本地commit/不推送等统一限制继承。

### 已消耗S-P28：Q22普通action与v3 ACK阶段

app_rpc_action_research_01，同接口两版本合包：ctx动作元数据→ACK/token借用→输出JSON/上层reply→本层归还，不执行实际action。领域真前提为绝对 `D:/Documents/PlatformIO/Projects/cuktech-ap01-firmware/evidence/rea-0041-20261017/evidence/upper-miio-a.md` §0xa00bb110（ev_6bde5d9aff5af2968564572019754faaba3c3c75e5f78ebb490d47b2fdc0e97b）及同目录upper-miio-b.md §0xa00c0b96（ev_e88416f40cb09d4f766cc0b49a71bfce06f52bcca97488565cae5c8171f8aef2）；另一profile真root同目录upper-complete.evidence.json records297/54，ev_ecf6e8c1592c11cde466318e02e74ee337b4493e2c4cff9d3f3fe3a4aecdda71 / ev_24a567d316d2266ca0c3faa04db22e09e5ea377b4dc6d3a88fbdb09be4bc6d16，各profile不混贴。根已验请求格式/ctx字段/装回调，不重做。

真实root ctx+6c装普通result0xa00bec0c、v3 result0xa00c5b8c，+70装error0xa00bd924/0xa00c0b5a。新原窗只有extent：0xa00bec0c..beeaf676B、0xa00c5b8c..c5e23664B、两个error20B各、shared0xa00bd7fa..bd90f278B，共1658B。回调字段继承ctx+230 DID/+250 version/+254..25c IDs，但访问/清理以原字证明，不因Q18同ctx套staged-list。近期无callback专项，两个upper根均明确callback/权限/激活状态未闭。

范围result ABI/状态/normal out数量和类型、两版本ID/output异同、token/原ACK borrow、error JSON/status适配、ctx+64 reply和栈descriptor、返回/清字段/本层资源。v1a00b7878、v3a0191d52及cmd.result a00ba5be已有父级卡，继承其有限tokenizer/state/deadline，不深挖库，不把v3当通用JSON验证。止formatter/JSON/allocator、实际action/权限/并发/激活writer/传输，保留外部持有未知。独占app-rpc-action-research-01-0041-20261025、同名branch，rpc-action01。阶段1–2/4–6/2–3/1–2=8–13分中低置信，1658B新多版本callback，对比Q18 1382B348秒，提前交付不补时。最小派发：`继承两action根，仅五callback/shared新原窗的正常ACK/输出/归还，API止边、未知原字不升级语义，首工具clock，静态commit。`

作者9f9220cab18fa8982e23a224b5877de15df73602已停；技术17:35:12→17:39:31=259秒，提交17:39:50、停止17:39:56，总284秒，均分列；1658B/1custom/JSON及安装接合已由作者检查，待非作者。v3 indexedload仅推断，reply/action/权限并发未闭。

### 已消耗S-P29：Q21 named-property非作者

app_named_property_review_01，作者5be2e80b03c56e1af6ece0eadddb7bef9be0e57f，必要绝对报告 `D:/Documents/PlatformIO/Projects/cuktech-ap01-firmware/reverse/reports/ap01/app-named-property-research-01-0041-20261025.md`，analysis同stem verify_static.py/windows.json/root-record-256.json/root-profile.json。只820B三正确body/281指令、root256实参、1vendor/2strings，排除event0xa0116ad0/flush。

验收先report忽略返回后锁C+d8→update H=C+d0，返回仅update；64B条目内联name32+终止/独立value ptr+capacity、同名复用不改name；足容量复用，不足先alloc成功再free旧/copyNUL；existing分配失败保旧/new撤链free节点；status0/−1/−5、标志1+(entry+38!=0)，未证字段不命refcount。唯一srb旧SINC/字段分账不执行。report P0x558/栈S、K88/tag5，finalize0才a011c0da，call后freeP撤栈、返回忽略，callback仅指针；validator/raw-builder/下游复制/完整publication回收未知。首工具clock，独占app-named-property-review-01-0041-20261025、同名branch，named-property-review01。阶段<1/1–2/1/1=3–5分中置信，据作者总342/冻结316秒及Q18review技术182秒；最小派发为Q21同认领独立原字/替换/临时借用，不跑作者脚本。

非作者要求拓扑措辞修正，主窗pause→作者58cd281（17:38:34–49仅15秒/只一处）停止→恢复确认；不要武断叫H/+0方向“链尾”。非作者e2742cd5f1a65b97171b01ec4370cea6c2307113确认范围修正1/新增0；起17:36:37、技术17:40:07、提交最终17:40:30总233秒；17:38:08–17:39:04观测56秒含补修调度，不当纯等待或有效工时。

### 已消耗S-P30：Q23 subscription身份比较与正常构造

app_subscription_research_02，把相关身份/构造差集合同合并，不单派336B matcher。旧version/classifier补充卡已经完整：绝对主仓upper-miio-b.md supplemental、upper-helpers-second-002/003，ev_d1e4f42de34b3fc8ff67a2423a4be7cd2727d4e7d19df4a5ddfd5c09cf12d3c8 / ev_b62850fb9162668ae6954b55ed52b3dde46af021b1f8a3bb8ad0fe14b1210c23，profile4825；136+610B不是本包新body。真root绝对upper-complete records245/48及Q20有效graph前提继承，不读删除/过期七body。

真实root245依type调用a01189b8/a01189f6/strcmp，a0118a40(T+8,desc)，a0118b8a(desc)/a0118bd6(DID8)构造、a0118c20(head,target)存在性、a0118c46(DID8)lookup。准新精确原窗（只有metadata）：a01189b8..89f5 62B、a01189f6..8a3f74B、a0118a40..8b07200B、a0118b8a..8bd576B、a0118bd6..8c1f74B、a0118c20..8c4538B、a0118c46..8c9580B，共604B。b8a/bd6 directcalloc/clear/copy，不能按模糊命名误称lookup。

完整问题：有效88B描述的9type字段/target/symbol比较、0/非0语义、DID8键与指针存在性区别、构造实际size/值copy/内head计数/borrow终点、root重用/新建及reciprocal成功接口。pair allocator a018eddc已在旧父级明确两wrapper ownership，直接继承；a0118b08已由Q20核，只实例化新matcher语义。generic compare/allocator止API；不扩不完整图/失败缺陷/异常输入/fanout/云/全root，保留外部锁/总manager寿命。与Q20非作者不重复删除/类型计数，N03/Q07不同对象。独占app-subscription-research-02-0041-20261025、同名branch，subscription02。预调研1–2/2–3/2–3/1–2=6–10分，主窗按Q21完整820B342秒/Q20review1780B225秒下调实际派发4–7分；仍完整身份+构造阶段，不扩公共库。最小派发：`仅七身份/构造helper604B，旧746B分类不重计，正常有效图/descriptor前提，首工具clock，静态commit。`

### 已消耗S-P31：Q24 publication路由、copy及event回调恢复

app_publication_research_01，问题Q19/Q21即时publication与保留event下游copy/recipient→ACK/error→按id恢复/归还。绝对源报告 `D:/Documents/PlatformIO/Projects/cuktech-ap01-firmware/reverse/reports/ap01/app-event-research-01-0041-20261025.md`、app-named-property-research-01同目录：真实a011c0da(C,D,K)后freeP、a0113340(C,D)后freeP；K tag6 event/tag5 props，callbacks a0116db0/a0116b5a，非0a0116ad0(H=C+dc,id,0)。这些已交/非作者止边，不重验820/1566B producer。根owner从参数证明，不套F11同名对象。

只有metadata的新窗口0xa011c0da..c203298B、0xa0113340..339b92B、0xa0116b5a..6c23202B、0xa0116db0..6de554B、0xa0116ad0..6b59138B，共784B。领域upper卡无五入口合同；generic a011f9da→a011f86c复制/会话构造在绝对 `D:/Documents/PlatformIO/Projects/cuktech-ap01-firmware/evidence/rea-0041-20261017/evidence/miio-recovered.md` §10及session段已解释，继承而不重读库。a0116ad0为event owner，S24已删，无live重复取证。

范围D/callbackctx实际copy、tag5/6匹配/peer route、每peer输出/返回消费、临时D/P何时变SDK owned、event callback ABI/ID/状态/恢复真实pending/retry/free、本层顺序。a0118a40只已知0匹配接口，不读新336B，S30另题；a011bffe stale沿Q20已交条件前提，不重验；止graph生产/构造、传输/crypto/HTTP/MQ/全C析构、JSON内部。验收不要从async名推copy或从ACK推物理应用，保留C全寿命/并发/recipient送达。独占app-publication-research-01-0041-20261025、同名branch，publication01。阶段1–2/2–3/2–3/1–2=6–10分中低置信，784B新多对象阶段/旧session可直接引用。最小派发：`五publication后端入口/正常ACK恢复784B，旧generic请求copy继承，peer matcher仅API，不扩库，首工具clock，静态commit。`

### 可派S-P32：Q22普通action/v3非作者

候选app_rpc_action_review_01，同Q22认领，作者9f9220cab18fa8982e23a224b5877de15df73602已停。必要绝对报告 `D:/Documents/PlatformIO/Projects/cuktech-ap01-firmware/reverse/reports/ap01/app-rpc-action-research-01-0041-20261025.md`，analysis同stem verify_windows.py/contract.json/原窗与parent-links.json；未合并时rpc-action01同路径。源upper297/54及两根卡/tokenizer补充卡沿S28，profile独立。只五窗1658B、1custom、必要JSON字符串和安装点，独立核，不运行作者脚本/目标/模型。

验收result(ctx,ACK) v1 n>2且奇数/IDs两项，v3 n>3无奇偶/IDs三项；status非0可成功回复但不输出out，0且有多token时v1 piid/value pair、v3逐value；无out边界和raw值borrow/无本地类型验证；v3唯一indexedload原字推断保持限定，不升级ISA。两error20B保留a0/a1/a2调shared，shared buffer=ctx+74/cap=min(unsigned ctx+78,558)、error code unsigned status+10000<=5000才保留[-10000,-5000]否则-10000；空message省略。invalid ACK调用error(-9998)后强制-1，不因helper返回可能已reply而推未发送。

三个路径40B栈descriptor+0 id、+1c length、+20 payload，调用ctx+64(&descriptor,ctx+68)返原值；finalize失败不reply，ACK和栈descriptor只借用、不malloc/free、不清ctx字段/回调槽/state。serial writer实际ctx+0x14（旧+20是十进制）与reply+0x64分开。止tokenizer/数字转换/JSON/formatter/reply复制与传输、实际action/权限/激活writer/并发，不能说callback0等设备动作成功。独占app-rpc-action-review-01-0041-20261025、branch codex/app-rpc-action-review-01-20261025，rpc-action-review01，最新基线/首工具clock/静态独占commit不推送。

阶段定位<1、两result/门/1custom1–2、shared error/reply/borrow1–2、交付1=4–6分中置信，作者技术259秒/总284分列，Q18非作者技术182秒/Q19非作者170秒参照。最小派发：`Q22同认领非作者，只五callback/shared阶段和必要旧根/tokenizer，限定custom推断/返回层次/借用，首工具UTC clock再读，静态commit交付。`

### 可派S-P33：v3 property report-config请求到结果适配

候选app_report_config_research_01，新认领主窗登记；普通get/set_property_report_config_v3请求上下文→异步ACK结果适配→reply调用/本层归还，不研究真正report调度/设备接受集合。两root父级已解释，未闭的是callback结果链。绝对父级 `D:/Documents/PlatformIO/Projects/cuktech-ap01-firmware/evidence/rea-0041-20261017/evidence/upper-miio-b.md` §0xa00c0ec2（ev_14adfa074a1d9499eebc51b4935ce6904d0d69e74bc576ca5c3977b93ecfb211）及§0xa00c1c88（ev_4c25cb0c4b403592189b2e7f9b2e452af7b437b262aee735a65463f933ff54a0）；get iid3/set min/max/raw change输入、doc释放/串行writer及0/−1根返回均继承，不重做root/formatter。另一profile真root同绝对目录upper-complete.evidence.json records26/45，ev_12f73038adef84341e7cb66ecab11785ac4dded7585b16b6bb9cfccf4bc09875 / ev_20f6138d97a4e7749550583a9cfe9af14eb270f104fb15e4219dfce699d89a33，各自profile分账。

真注册端root装ctx+6c：get0xa00c6198/set0xa00c607e，+70：get0xa00c0b82/set0xa00c0b6e。无已定位旧callback body，准metadata精确新窗0xa00c6198..c6367464B、0xa00c607e..c6197282B、两error各20B（0xa00c0b82..c0b95与0xa00c0b6e..c0b81），总786B。upper领域卡只有root引用，近期报告无这四callback专项。与S28/Q22 action callbacks不同入口；共同error helper0xa00bd7fa由Q22作者已交、非作者中，**此包只到该API调用边，不读/重复裁决其278B**，不得提前以未验helper输出细节标config接口闭合。

范围ACK/token的正常门、ID/status/min-max/change字段来源和宽度、get/set输出形状差异、value是否raw借用、ctx+64回复参数/栈descriptor和返回、本层临时对象/回调槽保持或清理。v3 tokenizer0xa0191d52有upper-miio-b supplemental合同，继承最多64/quote-span/非通用JSON验证，不展开tokenizer/JSON/formatter/数字转换/allocator。set根未检查min<=max是已有正常代码事实，不做异常/配置实验；get根local DID没有显式append，不先假设callback有同ctx DID字段。callback实际字段以原字决定，不能从method名补合法性/持久化或真正报告调度。止reply持有/真实设备属性效果/SDK权限/并发/取消；输出0仅本层生成/交接，不等配置生效。与Q18 staged property/Q20 graph/Q21 named条目不共享本体取证，无live作者依赖。

验收给两root输入上下文到callback输出的可独立适配阶段、类型/状态门/borrow终点、error委托与真正施加配置断边，不以同名type推语义；未知word完整保留，不改模型。独占app-report-config-research-01-0041-20261025报告/analysis，branch codex/app-report-config-research-01-20261025，report-config01；最新管理基线、首工具clock、静态/独占本地commit/不推送。阶段旧根/对象1、双result/字段2–3、error/reply/持有1–2、原字交付1–2=5–8分钟中低置信，786B新回调/两操作，Q22 1658B技术259秒作参照，不重新包装成30分。最小派发：`登记S33普通v3报告配置ACK适配阶段，只四回调786B与必要两根接合，shared error/tokenizer到API，不研究配置实际应用，首UTC clock，静态commit。`

### 可派S-P34：v3 property/event subscribe与unsubscribe结果生命周期

候选app_rpc_subscription_research_01，新认领由主窗登记。同接口properties/events两个记录族、subscribe/unsubscribe两方向合包，覆盖有效请求的staged持有→ACK同链回填→结果序列化→清链/上层回复；不等同Q20全局miIO.sub peer/topic图，也不重做Q18普通get/set_property。父级绝对 `D:/Documents/PlatformIO/Projects/cuktech-ap01-firmware/evidence/rea-0041-20261017/evidence/upper-miio-b.md` 已解释四root：0xa00c1144（ev_790146c2658bc4f0705d54d3515b34e162566b36bd4c28d0d17db5e7fc55ed87）、0xa00c13f2（ev_7e388cdc7b77a16a8cf3ceb82eb6694b9a4209aa9fa70bd6958cd13d7b6fbfa9）、0xa00c2162（ev_d1be944ad55ee4d06a920d328d83b3f62e6fdc82b5cb63ca85dbfa234ff590a1）、0xa00c2452（ev_bb7cfc79fe6b9e1a145136959ed6f377984b3f6c747fb9f7529a580575bd2f43）。真root另profile同绝对目录upper-complete.evidence.json records280/56/50/135，EIDs按顺序ev_db33625e03f3e24175d2c317d0ae631e60913589eb0092b638ac297783c535d4 / ev_258c7b21e4dc01703c69987989b83a48d23b1119eba1ef1453d59850fc304916 / ev_23b0ebaa7eb99216dc55fee2bae1a78df430f63d4a6bf4d7d2e5575e8cbfb7cb / ev_64e2320c9090aa5a2752dcf26591052825d7913ac7b0d0458e233b965b70d383，各原profile保留。

继承四root optional DID/IID3 array、缺/空数组本地可接受、成功保链/失败clear和装callback，不重验请求/parser/串行grammar。明确四head：properties sub ctx+0x2e4、unsub+0x30c，events sub+0x334、unsub+0x35c；各DID槽+2c4/+2ec/+314/+33c。不能按同ctx把它们当Q18 head+228，也不能把72B property与56B event record混同。已有Q18 stage0xa00bb67e和generic clear0xa01afb26是property族已交接口，直接继承；event stage未闭。

新metadata入口无旧body，准精确原窗：property result0xa00c6368..c657b532B、0xa00c657c..c6787524B；event result0xa00c6788..c6993524B、0xa00c6994..c6b9f524B；四error26B各0xa00c0492..c04ab/0xa00c04ac..c04c5/0xa00c2148..c2161/0xa00c2438..c2451；两serializer0xa00c1fd8..c208f184B、0xa00c2090..c2147184B；两matcher0xa01adbd4..adc0d58B、0xa01adb9a..adbd358B；event stage0xa00c187c..c18d792B，总2784B，所有入口来自root安装或callback真实directcall，不拼其它业务。serializer输入root0xa00c10f6/0xa00c16a0仅继承API，不读其78B或公共formatter补量。event clear0xa01afae6为旧root明确委托的清链API，本体64B不展开库。

范围两族record布局/初值/值copy或借用、type3 IID3/其他匹配字段/默认status门、callback ACK正常分组/状态回填、DID/IID输出/清链与finalize/reply先后、四error的真正清理/返回、槽是否清与本层资源归还。property与event matcher必须分别原字证明，不能从相似形状套72B布局。v3 tokenizer补充卡/JSON/string公共API止边，未解厂商字保留raw/字段及限定，不执行/改模型。保留真正后台订阅施加、完整ctx生命周期、并发取消/云送达、generic clear内部free保证；callback返回0不当设备订阅生效。当前Q22/shared error helper、本包不调用其body；S33 report-config四callback不同入口，无重叠。输入root请求接受只是给定有效阶段前提，不扩缺陷/异常/权限实验。

验收同四head的输入staged→ACK匹配→输出/清理连贯性及两族差异，所有权/位宽/返回/借用/失败清理和条件unknown明确；不能把root array可空推广后台效果。独占app-rpc-subscription-research-01-0041-20261025报告/analysis，branch codex/app-rpc-subscription-research-01-20261025，rpc-subscription01；最新基线、首工具clock、静态独占commit、不推送。阶段旧四root/head2–3、staging与两matcher2–3、四result/error/两serializer5–7、原字交付2–3=11–16分钟中低置信；2784B新同接口callbacks/两对象族，参照Q18 1382B外层348秒但不机械倍增，不强凑20–40，提前闭合即交付。最小派发：`登记S34，继承四v3根，只2784B同property/event订阅ACK生命周期新入口，public API止边，两record族不互套，首UTC clock，静态commit。`

### 可派S-P35：Q23 subscription身份/构造非作者

候选app_subscription_review_02，同Q23，作者97b1af4824514615b01ad40a2d0cb94a03f5a25a已停。必要绝对报告 `D:/Documents/PlatformIO/Projects/cuktech-ap01-firmware/reverse/reports/ap01/app-subscription-research-02-0041-20261025.md`，analysis同stem extract.py/static-windows.json/session.json及复验材料；未合并时subscription02独占树同路径。源upper245/48、旧version/classifier补充卡与pair allocator已解释前提沿S30，不重验旧746B、Q20删除七body/76B peer matcher或库。不执行作者脚本/目标/模型，只604B七窗及必要root成功分支实参/门独立核。

验收三个层次不可混同：数字比较器word减法差/字符串不等−1只用0/非0；0xa0118a40为**非对称首参覆盖**，type9/7/8及type1..6各字段偏移/目标匹配原门；sub调用(stored T+8,incoming D)，Q20 peer删除接口调用(incoming D,stored)，不得交换；全局topic重用先同type，再89b8/89f6或strcmp同型identity，不是覆盖匹配。旧classifier type5/6不copy target及新matcher不读其target两者接合，不给未用字段造语义。

peer lookup按P+8原始8B DID键而非文本/sender；a0118c20只E+8指针存在性，不是descriptor或DID相等。构造T=108B全零/copy88B到T+8/内sentinel T+64/+68，P=48B全零/copy8B到P+8/内sentinel P+24/+28、计数各0，输入不持留，构造不插global链。正常root在外mutex下不同P/T存在组合的重用/配额/双边存在门与已验pair allocator接口；peer无门unsigned<4、edge门signed<=9不能混同，成功后类型只是计数+1非外部callback注册。重复peer覆盖命中不加边不等整root无变更，common cleanup副作用沿Q20保留，不重验。allocator/compare到API，正式版本/权限/损坏图/失败缺陷/fanout/全manager寿命排除。

验收给七helper的0/非0/借用查询与owned构造、方向/字段/位宽及正常root接口，不能只把两callback输入名换位。独占app-subscription-review-02-0041-20261025报告/analysis，branch codex/app-subscription-review-02-20261025，subscription-review02，最新管理基线/首工具clock/静态独占commit、不推送。阶段定位<1、覆盖谓词/根方向1–2、双构造/查询/边界1、交付1=3–5分钟中置信；作者完整17:39:24→17:42:59总215秒/技术180秒分列，Q21review含修正总233秒/Q20review技术177秒参照。最小派发：`Q23同认领非作者，七窗604B与必要旧根/卡前提，重点非对称方向及同型identity/owned构造，首UTC clock再读，静态commit。`

第六轮最新准备快照：S32已取走Q22非作者；S33 report-config、S34 RPC subscription ACK、S35 Q23非作者已先落盘，尚未取走时3/3。S31/Q24实际派发由主窗按Q21完整342秒/Q22完整284秒将6–10分下调5–8分；不是把原预测改写成实测。S28..31的历史派发/继承和当前新包位置已齐，后续按主窗实际消耗继续更新；未交Q24复核仍条件项。


### 可派S-P36：Q24 publication提交/callback非作者

候选app_publication_review_01，同Q24，作者b2c1453681afa24b306834a49286b045bd6e592f已停止。必要绝对报告 `D:/Documents/PlatformIO/Projects/cuktech-ap01-firmware/reverse/reports/ap01/app-publication-research-01-0041-20261025.md`，analysis同stem extract.py/verify.py/raw.json/checks.json。父级与S31相同；SDK同步copy旧合同继承 `D:/Documents/PlatformIO/Projects/cuktech-ap01-firmware/evidence/rea-0041-20261017/evidence/miio-recovered.md` session段，ev_3c1987c9d0b0223c28b66671236fb3303aea3c0ccb028253ec8660393dd03e02、ev_e7a80442abbf3a1af9636c77de5a9a5b9993e5b10a7b0758e6ffcff375d61317，不重做其body。与live Q25/Q26不相交；matcher/Q20 stale仅已交API，不复验其body。

独立核五精确窗：0xa011c0da..0xa011c203 298B、0xa0113340..0xa011339b 92B、0xa0116b5a..0xa0116c23 202B、0xa0116db0..0xa0116de5 54B、0xa0116ad0..0xa0116b59 138B，总784B/279指令/11JAL/16原字。不得运行作者脚本/固件/模型；原ROM与offset规则沿本报告头，只静态必要窗。

验收路由matcher调用(T+8,K)非对称方向、逐topic/edge recipient无去重、peer快照0x30B与word(B+18)门、D+14 sender8及SDK message=D+4接合；直接a011f86c与经a011f9da清metadata的两路径不能混同。C+1134/C+1c8 bit20选择session/time/mode及无路由−12；一次成功返回1后续失败不撤销，调用端是否消费返回沿原字。D/P/B/K同步SDKcopy与cb/ctx浅持有分开；跨unlock缓存next不证明并发安全。

event callback只检result存在，不检内容成功；先释放解析doc再锁C+e4，调用a0116ad0(C+dc,id,status?0:2)。helper遍历所有同id，state0清pending再retry++保留record/id/时间/argv，非0先写pending后unlink/free，不先验pending、不只首命中；即时callback只日志/返0。保持C生命周期/并发/实际递送/物理应用未闭，不以ACK或返回0补成功。未知原字保留，不改模型。独占app-publication-review-01-0041-20261025报告/analysis，branch codex/app-publication-review-01-20261025，publication-review01，最新主窗基线、首工具UTC clock、本地精确路径commit不推送。

阶段定位<1、recipient/同步copy1–2、ACK恢复/归还1–2、交付1=3–5分钟中置信。作者完整17:42:30→17:46:28 238秒、技术209秒分列；最近Q23复核总174秒/技术144秒作校准。最小派发：`Q24同认领非作者，只784B五窗及旧SDKcopy API，核路由方向/不同submit/ACK恢复所有权，第一工具UTC clock，静态独占commit。`

### 可派S-P37：Q25 report-config结果非作者

候选app_report_config_review_01，同Q25，作者1890c41d135ed66bf282d601645096c3e7d09a41已停止。必要绝对报告 `D:/Documents/PlatformIO/Projects/cuktech-ap01-firmware/reverse/reports/ap01/app-report-config-research-01-0041-20261025.md` 及同stem analysis作者实际留存（先只读目录定位，不执行脚本）。父级两root/两个profile/EIDs/输入上下文及API排除严格沿S33，不因旧根complete重复研究请求。新四窗0xa00c6198..0xa00c6367 464B、0xa00c607e..0xa00c6197 282B、0xa00c0b82..0xa00c0b95 20B、0xa00c0b6e..0xa00c0b81 20B，总786B，作者6关键检查无unknown；独立必要ROM原字复核，不运行作者脚本。

验收get/set ACK正常门与IID/status/min/max/change字段来源和宽度、两输出结构差异、raw借用/本地类型验证界限、ctx+64栈descriptor回复与返回/错误委托顺序、是否清槽/归还。只恢复作者实际合同，不先按method名承诺配置生效；共享a00bd7fa沿已交Q22及非作者合同API，不再读其278B，tokenizer/JSON/formatter/数字转换止API。两root get optional DID/set minmax接受规则沿旧卡，不做缺陷/异常/配置实验。与Q26四订阅head/result不同对象；止真实report调度/设备应用/reply持有/并发取消/完整ctx生命周期。

独占app-report-config-review-01-0041-20261025报告/analysis，branch codex/app-report-config-review-01-20261025，report-config-review01。首工具UTC clock，最新管理基线，静态独占commit不推送。阶段材料<1、两result与字段1–2、error/reply/归还1、原字交付1=3–5分钟中置信；作者17:49:21→技术17:52:56 215秒，commit17:53:15，停止17:53:28总247秒；不能把215秒称完整工时。最小派发：`Q25同认领非作者，只四callback786B与必要旧根接口，核get/set门和输出/borrow/返回/清理，shared错误只API，第一工具UTC clock，静态精确路径commit。`

### 条件S-P38：Q26 property/event订阅结果非作者模板

作者app_rpc_subscription_research_01仍在跑，未有交付SHA、实际窗口和最终报告，**不是可派库存**。待作者停止交付后填SHA/真实新差集/实测，再由主窗转ready；不得并行抢作者原字。预定app_rpc_subscription_review_01、branch codex/app-rpc-subscription-review-01-20261025、rpc-subscription-review01及同stem报告/analysis。

父级四root/四head/两record族与2784B入口精确范围沿S34；待交付后以作者实际保留窗为上限，不自动扩全部metadata。核心已知差异须验：property-sub bad ACK直接−1不清，其它三callback略过回填仍输出清；matcher无type/−4004门，不套Q18普通property。其余按作者最终合同验两族stage/匹配字段/默认状态、四result输出/清理、四error、两serializer所有权/返回、公共clear API止边和完整ctx/实际订阅生效未闭。首工具UTC clock，独立静态原字、不得运行作者脚本，精确独占路径commit不推送。估时待作者实际差集/计时后校准，不预报虚精度。

第七轮即时快照：S33/S34/S35已分别取走Q25/Q26/Q23非作者，旧3/3已消耗。Q23非作者389c58014df0ed6e08eb4c8270b7fc411e3ed60d，17:50:19→17:53:13总174秒（技术144/提交13/末检查17），新增纠正0。现新增S36/Q24和S37/Q25两份可派；S38条件不计。两份若补空席取走即库存0/3，仍缺三个后备，不以条件填数。


S38转可派补记：作者9dc5fd4af492bd1ef180a5833cd83b05d56e51cd已停止，2784B/13窗/8分组跳转PASS。完整17:49:30→技术17:54:30 300秒、提交17:55:05、停止17:55:24总354秒。必要绝对报告 `D:/Documents/PlatformIO/Projects/cuktech-ap01-firmware/reverse/reports/ap01/app-rpc-subscription-research-01-0041-20261025.md` 及同stem analysis。验收追加closeJSON→clear→finalize→reply顺序，error仅clear−1/槽不清、owner并发后台未知；只propsub invalid ACK直接−1保链，另外三者输出清链。阶段材料1、两族matcher/staging1–2、四result/error/serializer2–3、交付1=5–7分中置信，据作者总354秒/技术300秒及同域非作者174–233秒校准，不机械以字节倍增。S36/S37/S38由主窗同认领派发即消耗，本段补齐实际SHA与差集，非另开新题。

### 可派S-P39：DDF transfer缓存到discovery结果/归还阶段

候选app_ddf_research_01，新认领由主窗登记；与Q24/25/26非作者不同入口/对象，当前认领表未见DDF专项。只正常有效DDF缓存输入→discovery level选择/结果构造→reply和本层cache归还，非DDF模型执行/内容解码/完整设备语义。父级绝对 `D:/Documents/PlatformIO/Projects/cuktech-ap01-firmware/evidence/rea-0041-20261017/evidence/upper-miio-b.md` §0xa00c1a00 ev_586b87930c1ebb9fa5abd60af3f4c077909ab784b12171ad40e6b6fa2d4395d2、§0xa00c756e ev_e06417125856a36a910255f4f2645f550163c84f543b45a6699b8c1030883101。另一profile同目录upper-complete.evidence.json records176/291，ev_8d07ce5cc468be325f93e2a6d44b97a82dc7fa14407f2cf5b1dcb06cacbdaa94 / ev_e4976417818c57a53dbe04bdafb461c5a441dae4f402c82c2563f0d647ff8909，各保原profile，不混证据。

继承旧transfer全body：ctx mutex+2c0、type1..5五head+298/+2a0/+2a8/+2b0/+2b8、type/IDs键缓存node32B（type+8、IDs+12/+16/+20、len+24、buf+28）、新分配先于旧free、失败保旧与旧normal输入形状。不重做956B transfer/parser/quote边界/缓存失败实验；根discovery optional DID+260、level字节+280、miid+284、siid+288及callback安装+6c/+70继承，level>=3/==5门是旧卡事实，不伪造新发现。

真新入口来自根注册或结果真实directcall，只有metadata extent无旧body：0xa00c6f8e..0xa00c756d 1504B（result）；0xa00c6f56..0xa00c6f8d 56B（error）；0xa00c1930..0xa00c1967 56B与0xa00c1968..0xa00c19ff 152B（结果字段适配）；0xa00c6efe..0xa00c6f55 88B与0xa00c6eba..0xa00c6efd 68B（锁/归还路径，具体角色待原字）。总1924B；必要绝对metadata `D:/Documents/PlatformIO/Projects/cuktech-ap01-firmware/reverse/analysis/whole-rom-coverage-0041-20261023-round1.json` 精确这六地址函数项，只能当边界/directcall，不当已留存body。可按本报告ROM/映射读必要短窗独立静态解码并保存raw/指令；不以函数名猜清理作用。

恢复正常ACK门/level分支与五cache对象接合、节点/字符串/JSON数据来源和复制或借用、输出字段/数组层次、ctx+64回复及本层返回、close/finalize/归还先后、error是否同归还和槽状态。六函数为同对象缓存消费与归还完整阶段，不拆清理微题。shared error0xa00bd7fa沿Q22已交API；JSON/string/format/allocator/通用unlink内部止边，不扩库，不执行模型或校验DDF业务内容，不以cache输出等价设备支持/云接受。上下文全寿命、并发/后台真实DDF来源及reply外部持有明确未闭；未知word留raw不改ISA模型。父级解释了transfer本体，新研究只接到其既有缓存格式，不能把旧body重计新量。

验收给level/IDs/cache选择与输出来源的可独立合同、所有权/锁/归还/返回和真正外部效果断边，输入为已有正常有效缓存，不做异常探测。独占app-ddf-research-01-0041-20261025报告/analysis，branch codex/app-ddf-research-01-20261025，ddf01，最新主窗基线、第一工具UTC clock、本地精确路径commit不推送。阶段旧接口/head1–2、result及两字段helper3–5、归还/回复1–2、原字交付1–2=6–11分钟中低置信；1924B新六入口、旧transfer现成，参照Q26 2784B完整354秒/Q22 1658B完整284秒，提前闭合即交付，不凑半小时。最小派发：`登记S39，继承两DDF根/transfer完整缓存合同，只六新入口1924B恢复discovery结果到归还正常阶段，公共库止API，不执行DDF模型，第一工具UTC clock，静态独占commit。`


### 可派S-P40：MCU OTA应用七槽生命周期适配

候选app_mcu_ota_research_01，主窗先登记新认领；与Q08/Q13/Q16 ota_app和Q24/25/26复核不重叠，只同MiIO OTA handler架构下**ota_mcu应用侧ctx/table**从准备→资源打开/写入→完成/错误归还的阶段，止MCU传输/安装和内部固件。必要绝对父级 `D:/Documents/PlatformIO/Projects/cuktech-ap01-firmware/evidence/rea-0041-20261017/evidence/miio-recovered.md` §3末段：独立0x38c MCU命令对象/900B接收与两1025B buffer、七槽注册；同目录upper-complete.evidence.json record248的初始化段0xa00661f2..0xa0066218为注册真种子，继承该大root不重做。0xa01bb0e8只读ROM28B已核LE七word依次为0xa006fbe8、0xa0074b22、0xa007019e、0xa00702a6、0xa0074ea2、0xa0070390、0xa006faca；不是凭七槽名推ABI。ROM来源/映射沿本报告头。

已解释父级 `D:/Documents/PlatformIO/Projects/cuktech-ap01-firmware/evidence/rea-0041-20261017/evidence/upper-miio-a.md` §0xa0074ea2（ev_9da86361ce16fc84dba2cdf02382d0ad5f7241c94d366c9256e11464fa3bcb17，282B）完整本地完成槽合同继承：ctx tag+16、flag+24、header+16c、retry+174、signal+178；验证/写8Bheader/trigger委托及每出口signal。不重做282B或1886B验证a00703ce/密码库。`D:/Documents/PlatformIO/Projects/cuktech-ap01-firmware/reverse/reports/ap01/usb-interface-ota-0041-20261023.md` 和uart-retry-receive-0041-20261023.md/P08下游已验UART state/opaque固件项目流均继承，**不下探其控制器或MCU内部，不把应用完成等价真实烧写**。

新metadata只有边界/调用无旧body：0xa006fbe8..0xa00700b5 1230B、0xa0074b22..0xa0074b93 114B、0xa007019e..0xa00701f5 88B、0xa00702a6..0xa0070321 124B、0xa0070390..0xa00703cd 62B、0xa006faca..0xa006fadd 20B，共1638B六槽。必要绝对metadata `D:/Documents/PlatformIO/Projects/cuktech-ap01-firmware/reverse/analysis/whole-rom-coverage-0041-20261023-round1.json` 对应六函数精确项；upper领域卡只有已验完成槽，当前报告/认领未见六槽专项。六槽实际ABI/返回/调用时点须对已验MiIO七槽handler/selector/start/Q16 HTTPadapter接口恢复，不能照搬ota_app F布局；共享handler/HTTPbody只已交API，不重复取证。

范围准备槽有效参数与ctx字段宽度/配置和header来源、持有对象/内嵌资源初始化、打开/写入槽的ctx+参数到已知文件/验证接口、完成与错误槽的信号/归还对称性、最后通知槽与注册ctx接合。a00700b6/a00701f6/a0070322只直接API边界，若角色未有可信合同则完整地址/实参/raw保留未知，不为闭合而展开新helper；a006fade实际trigger依旧未闭，不扩其266B，更不读验证1886B/MCU二进制。普通allocator/config/sem/file服务到API；a01addc6沿Q08 fd>0关闭合同，是否传同对象须本层原字证明，不凭函数名认定。不能把0x38c命令对象等同MCU OTA ctx、不能从七槽索引先认open/write完整原型。

验收六槽和已验完成槽的同注册ctx关联、正常输入借用/复制/资源归还/信号/返回、本地配置写何时发生及trigger止边；保留构造/全析构/并发取消/底层flash实际保证/MCU硬件效果未知。未知厂商字保raw不改模型，所有操作纯静态，不执行任何OTA/模型/设备/回放/构建。独占app-mcu-ota-research-01-0041-20261025报告/analysis，branch codex/app-mcu-ota-research-01-20261025，mcu-ota01；最新基线、第一工具UTC clock、精确路径本地commit不推送。

阶段表/旧接口1–2、准备大槽3–4、其余槽/ctx接合2–3、原字交付1–2=7–11分钟中低置信；1638B真新六入口，多对象但父级完成槽现成，参照Q16 2182B采样290秒前读未知/Q26 2784B完整354秒，不把采样当完整预测依据。若接口到API已足立刻交付，不要求无种子trigger闭合。最小派发：`登记S40 ota_mcu应用七槽，只六新槽1638B及表/旧完成槽接合，继承MiIO/HTTP与下游UART合同，验证/trigger/API边界停止，不运行固件/模型，首工具UTC clock，静态独占commit。`

第七版交付快照：S36/S37/S38为已交Q24/Q25/Q26的完整非作者包，主窗已授权即时取走补三席；另已准备独立S39 DDF、S40 MCU应用七槽，若未取走为2/3，真实缺1。没有以条件复核/旧完整body/公共库补数。本次准备只原件精确表28B和已有卡/metadata定位，未进行六槽业务完整取证；UTC首观测17:56:36，结束以提交后clock记，token不可得不造值。queue JSON ignored另交转存，不force-add。
