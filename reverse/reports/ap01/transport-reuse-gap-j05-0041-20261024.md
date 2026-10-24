# J05：transport 旧证据复用与 Pogo poll 取消后端种子

2026-10-24；基线 `a462ff5`；独占树/分支 `re0041-j05` / `codex/re-0041-j05`。**筛出一个有真实调用及同对象字段依据的窄研究候选：Pogo type8 close 已经进入的 `a009f972`，向 `a009f442(loop,poll+34,17h)` 取消 watcher 后，再将同 watcher 的fd交 `a009e212(loop,fd)`。** stop本体及ready注册/投递已经由较晚G07–G10闭合，不能重复；两个后端callee的取消/同步合同尚未在本次所查父级和较晚报告中认证。此为旧证据盘点，新增ROM功能0，不对两callee作技术裁决。

使用已读 [reverse-engineer-anything skill](C:/Users/cogic/.agents/skills/reverse-engineer-anything/SKILL.md) 及rolling-management/history共同规则。用户本次明确跨领域继续派发，历史停止与上一批无种子不是本领域结论。只读既有JSON/报告/索引文本；没有新增ROM读取/反编译、共享REA会话、固件/SIM/模型/构建/历史回放/设备/外部服务或异常输入/漏洞/缺陷验证。仅写本报告与同名analysis，不改主树共享、生产代码、ROM、配置或分析器模型，无下级agent。

## 继承结论：已有→行为→局限→收缩

|既有出处|已解释行为与保留纠正|本轮处置|
|---|---|---|
|[application最终SIM验收](application-rehost-complete-0041-20261017.md)，四份domain complete，G09/J04的既有final ZIP/父级范围盘点|可达应用业务与本地服务替代已验收；USB/UART/设备/实际驱动不是整ROM恢复证明|passed-in-sim保持SIM层；不重建矩阵/源码包/资源，不重跑SIM。四父级新增精确词查询只限下述文件|
|D01/D02、[D03](uart-write-object-d03-0041-20261023.md)/[D04](uart-write-review-d04-0041-20261023.md)|提交/构帧/部分write、同步frame复制、fd对象引用已有；D04修正optional_mark非空分支，正常acquire的a3=0条件保留|不把D01/D03旧write未知重新派发；不重做帧/队列/parser|
|D05/[D06](uart-ring-review-d06-0041-20261023.md)、D07/[D08](uart-dma-review-d08-0041-20261023.md)|ring消费/IRQ/normal completion、持久LLI与栈transfer借用已验；D06真实IRQ入口为RAM trampoline `62fc133c`、arg为8B pair，非直接安装DMA公共函数|不把完成归还tail或descriptor固定池称heap释放；不重复安装/descriptor正文|
|[D09](uart-dma-channel-d09-0041-20261023.md)/[D10](uart-dma-channel-review-d10-0041-20261023.md)、D11/D12|File close→lower shutdown→busy归还→channel写0fh已经闭合；D10 type读取3次/channel读取4次的精度纠正保留；D11/D12候选LHAL不能替代RTOS来源|旧D08的allocator/final-close pending已被后续关闭，不再派；IRQ pair最终注销、pool跨设备复用仍未知，但本次没有新实际free/detach种子，不重跑负搜索|
|[C01](pogo-timer-lifecycle-c01-0041-20261023.md)–[C08](pogo-close-consume-review-c08-0041-20261023.md)|ctx+0 timer创建/借用；四poll登记；close入pending→消费→cb(poll)→ctx+198递减/条件free；登记后尾部无直接再消费边已独立接受|ctx+190 word不套controller phase byte；不重新查整容器timer delete，不由无局部回边推callback不运行|
|[dock/B01](dock-presence-polling-0041-20261023.md)、B18/[B19](uart-normal-parser-review-b19-0041-20261023.md)、B20/[B21](queued-command-review-b21-0041-20261023.md)|B01仅相位不匹配写sent=limit，匹配但sent≥limit直接跳组；B19接受正常接收状态/escape原值追加；B21的0x24不是无条件消费或成功回执|不把旧pending与早期宽泛表述当缺口；不重复B25/B26同item字段，不扩帧长度/OTA/异常主题|
|[G07](display-alternate-work-g07-0041-20261023.md)/[G08](display-alternate-review-g08-0041-20261023.md)，[G09](display-ready-dispatch-g09-0041-20261024.md)/[G10](display-ready-review-g10-0041-20261024.md)|较晚已恢复poll init/start/stop、watcher+14入fd bucket、ready→watcher callback→poll callback；G07明确内部backend取消未展开|C05/C06当时opaque的stop和list摘链部分已有后继，不重复。只补实际两个后端callee的窄取消/同步合同|

本盘点没有宣称已穷尽transport所有未知。按上述真实跨报告连接收敛后，不为凑候选再泛列所有UART/Pogo/dock断边；MiIO与输入idle由其他并行任务负责。

## 本轮复核或纠正：旧 pending 的层次更新

没有新增指令语义纠正。C05/C06的 `opaque_a009f972` 是其当时范围，较晚G07/G08已经解释它的poll+34 mask17取消、active/loop计数与poll+58传参；C05/C06的 `a0098b4a` 局部摘链也被F03/F04解释，不能再以旧opaque字样立题。G09/G10后来闭合的是ready投递，不是close drain，更不是Pogo定时器删除或context释放保证。

本次对主仓 `reverse/rehost/{system,charge,guide,weather-calendar}-complete-0041.json` 查询精确词 `a009f442/a009e212/a009f972/uv__io_stop/uv__platform_invalidate_fd` 均为0，仅认证这些命名文本集合无命中。全rehost有一个 `a009e212` 命中，实际在 `page-logic-0041.json#/records/15/normalized_result/callers/195`，该record的procedure是 `a0024906`，Evidence `ev_794a176f91454b7304c06fbfaff53024aa96bf8a3a51698dbb831f8b9359f9ef`；这只是callee记录中的caller元数据，不能当作e212 body/语义已恢复，也不能反过来据无标题声称从未分析。

G09/G10已有final ZIP、矩阵、complete复用分层直接继承，不再导出ZIP/整源码。候选名仅为检索词，未据名称给ROM函数正式命名、认证libuv版本或排除整库。

## 真正新增：一份可派发的窄问题定位，功能0

以下主仓路径统一前缀 `D:/Documents/PlatformIO/Projects/cuktech-ap01-firmware/`。本轮只读已有字段，不重新解码或比较ROM。

|真实种子|现存载体与JSON pointer/Evidence|已解释行为→尚待研究|
|---|---|---|
|Pogo type8 close→stop|`reverse/reports/ap01/pogo-close-dispatch-review-c06-0041-20261023.md`：`a009ffbe→a009f972`，原handle随后入pending|同Pogo poll的真实关闭入口已有；不另恢复close登记/callback计数|
|同poll的watcher与取消实参|`reverse/analysis/display-alternate-work-g07-0041-20261023/evidence.json#/windows/5/rows/6` 为 `a009f97e` poll+34；`/rows/8` 为 `a009f984` mask17；`/rows/9` 为 `a009f986→a009f442`|同通用type8 stop已有实参；f442是否/如何读写登记相关掩码、节点/桶持有与零mask后处理未核，desired/applied命名须据其实际字段另证|
|同poll的fd同步|同G07载体 `#/windows/5/rows/21` 为 `a009f9a4` 读poll+58；`/rows/23` 为 `a009f9a8→a009e212`|G10已证watcher.fd@+24，poll+34+24=+58，所以两个调用操作同poll的watcher/fd，非仅偏移字面匹配；e212返回/提交/状态消费仍未核|
|f442真实函数范围/依赖|`reverse/analysis/whole-rom-coverage-0041-20261023-round1.json#/functions/2374/extent`，`ev_081b932aef5c913e5bfe964e0de29c1d1f2df29191f1f84fb4ccb079f406a1df`；范围 `a009f442..a009f523`，226 B；`#/functions/2374/direct_calls`，`ev_986196a3813fdf2cffa1e9e109f6893eca5627cd5822ce57a5b04477df554104`|实际callees `a0019672/a0098b4a`；仅元数据，不能将extent/地址列表冒充取消合同|
|e212真实函数范围/依赖|同索引 `#/functions/2358/extent`，`ev_b23824a106e243ccc1d0fd43f5503f559517c5e31f04a68e66450c1f64002098`；范围 `a009e212..a009e349`，312 B；`#/functions/2358/direct_calls`，`ev_d143fb45aafbd683c4bfab2c180f5ba117b977adf1e627874fc6c272c5381aee`|实际callees `a0024906/a009e0e6/a010e722`；它们仅作为必要真实依赖，不凭名字预设poll syscall、close、同步成功或新owner|

建议任务书：**仅研究Pogo正常type8关闭已经进入stop之后，同watcher登记/掩码撤销与同fd后端同步的静态合同。** 以G07/G08原有实参为起点，先核f442必要字段宽度/重读、mask清除、节点/桶身份与返回；必要时核e212消费该fd的状态/下层提交/返回消费。可靠链摘除及已恢复注册/ready合同直接引用。只有真实调用需要才局核上述依赖，不展开assert/helper全库，不重新导出整stop、initializer或fd后端系统。

交付要回答：关闭是否撤销与G09/G10同一watcher的当前/期望登记；是否只修改软件状态而将更新留待另一个已定位提交点；e212的同fd调用到底消费哪些状态/返回，caller是否检查。任何“取消成功”“无后续回调”或“硬件停止”须分别有证据，否则保留条件合同。不得把同fd同步当作关闭OS fd、释放Pogo context、drain pending、停止ctx+0定时器或证明callback恰好一次。

## 精确未闭与实际验证

f442/e212 body内部尚未本轮验证；本报告不认证业务语义、OS行为、实际取消成功、排空、线程/重入保证、Pogo timer teardown或全资源最终归还。UART callback/IRQ pair最终detach/free与固定pool跨设备复用仍是D10/D12原断边，没有新种子时不派同一负搜索。此领域找到一个可研究切口不等于整个transport已恢复；没有切口的另一条边也不代表整体无事可做。

[inventory.py](../../analysis/transport-reuse-gap-j05-0041-20261024/inventory.py) 实际只读既有JSON/文本，核G07五个必要row、三项索引身份/extent/direct-call Evidence、四父级词项及page-logic caller命中层次；结果见 [reuse.json](../../analysis/transport-reuse-gap-j05-0041-20261024/reuse.json)。JSON解析、报告相对链接与 `git diff --check` 通过。没有访问ROM文件、解码器或分析器，不运行旧生成器/扫描器，不复制原函数/源码/资源或机械哈希账。

盘点新增功能0、技术验收0。主窗口可据上述任务书另派研究，研究后由未参与作者的agent独立复核；本路提交即结束，不自行接后继。
