# PREP-S01：底座协议与应用接入预分配队列

本报告为定题核对，不是业务取证或独立技术验收。首发Q-06/Q-07/Q-08已由主窗登记派出；首发三包不再计库存。主窗后续已取走S-P01登记Q09；当前后备 **0/3可派，缺3份**；缺口不能用未交付复核、BLE无writer或短胶水填充。管理表唯一写入者为主窗，本报告不授权认领。

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
