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
