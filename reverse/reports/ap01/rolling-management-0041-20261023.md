# 0041 六路滚动管理（2026-10-23恢复）

用户最新授权恢复持续六路推进，取代历史收尾暂停与三路上限。原管理交接已归档至 rolling-task-history-0041-20261023.md。主窗口只管理，不作函数逆向或技术语义判断。环境共7席，主窗口1席，研究/复核6席。当前六个任务均已真实启动，见运行快照。

## 共同规则

只做0041静态功能恢复；禁止执行固件、连接设备/外部服务、漏洞/异常输入/缺陷验证、修改安全检查、ROM、生产代码、构建配置和分析器模型；不推送。只写独占reverse/analysis和reverse/reports/ap01文件。只用自己的独立worktree和分支，每次shell显式workdir并在PowerShell Set-Location。其他agent同时工作，不撤销他人修改、不改主树或共享索引，不创建下级agent、不自行接后继。忽略ROM/证据/工具从主仓库绝对路径只读访问；不复制工作区，不共享可写数据库或切换全局REA。优先留存证据；若工具不能隔离则报告管理者。临时状态/日志放各自独占analysis目录。只恢复正常原程序行为，不擅自修正。

交付列问题/范围/结论、业务行为、函数地址/参数/返回/调用、必要伪代码结构体状态转换、所有权生命周期、可定位证据与原指令、事实/推断/未知、来源与恢复程度、实际静态验证、断边和一个后续闭包。伪代码不是原源码；保留调用顺序、重读、宽度/符号、返回判断、失败/清理和间接ABI。边界/厂商指令须核原字节，不仅信反编译。标准库只有来源可核实才排除，适配/回调仍恢复；不新增哈希清单/复制清单/机械重复证据。不编译项目，不运行历史回放。完成标准为原问题闭包得到有证据答案或明确可定位断边，不能缩成短helper声称完成；预计约45–90分钟，提前实质完成立即提交结束。

接近提交提前报告结论、剩余验证、阻塞和后继建议。检查差异、必要验证、明确路径git add、提交、报告commit/验证/未知/干净状态后结束。主窗口作范围验收，技术验收由新独立agent。恢复成果可先整合为待复核；不得自验冒称验收。每项完成即整合补位，从启动时最新管理提交创建新树；运行任务不移动基线。语义冲突交agent；回收仅限干净且已整合worktree，分支保留。用户要求收尾即停止派发。

主仓库：D:/Documents/PlatformIO/Projects/cuktech-ap01-firmware。所有任务初始共同研究基线 ab9716e；实际启动基线为含本任务书的管理提交，在派发消息及运行表记录。

## 当前任务书



## 实际运行快照

当前4恢复/来源认证与2独立复核共6个运行subagent，主窗口另计；已结束任务不计运行。

|任务|agent|启动基线|状态|
|---|---|---|---|
|A23|/root/a23_png_session|a295c3a|运行中|
|E06|/root/e06_ctk_close_review|26fc8d7|运行中|
|D06|/root/d06_uart_ring_review|1c79f0d|运行中|
|F07|/root/f07_source_auth|f22ec27|运行中，只读本地候选来源认证|
|G05|/root/g05_display_events|7c3a3cf|运行中|
|H05|/root/h05_weather_subscriber|8a7807e|运行中|

整合及限定验收映射见历史交接与覆盖记录，每项完成即检查整合补位。

## 近期滚动候选（未启动）

- A24：A23正常PNG session完整闭包独立复核，待A23整合；A23已启动。
- D07：D06验收后按其建议圈a01b554e本地DMA描述符消费/归还小闭包；D06已启动。
- E07：E06后转CTK剩余item+34/+38字段的真实数值消费者闭包，不重复root DELETE负搜索；E05真实退出/注销另留候选。E06已启动。
- F08：F07本地显示来源映射/厂商差异结论独立复核，待F07整合；F07已启动。
- G06：G05真实事件安装/param/调度完整闭包独立复核，待G05整合；G05已启动。
- H06：H05另一天气订阅者数据流/显式ctx释放完整闭包独立复核，待H05整合。H05已证callback=a00abed2、DELETE=a00abb62；正式范围待其报告。

以上只是预备问题，不冒称已派发。每次空位时依据最新整合和agent建议确定完整任务书、基线及独占输出，再启动新agent；独立技术复核须换新agent。

















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

## 预备完整任务书 A24（待A23整合）

任务ID A24，新agent独立复核A23 PNG真实session owner/open/close/缓存持有转移闭包。分支codex/re-0041-a24；worktree D:/CodexHome/visualizations/2026/10/23/01a1691a-e178-7710-86c0-84c2ff2d3dfb/re0041-a24；基线含A23最新管理提交。独占reverse/reports/ap01/png-session-review-a24-0041-20261023.md及reverse/analysis/png-session-review-a24-0041-20261023/。

问题：a00e5c78的s0-7c 76B栈session→a00e5d32/a019b168 open清session/cache miss/info/decoder+4→PNG a00eb7b6像素包装/session+2c→a018f9e8消费者→a00e5d8c/a00828d6 close→a00eab9a及cache/非cache归还，是否符合原字节和所有权？核心以A23正式清单约5–12函数及必要短依赖，已验收A22 registry/info/header只针对核，不重做全PNG或像素压缩算法。重点严格1门、src借用/像素byte0/2交换、normal options+4/+5零使a00829e4对象直返、非cache a0081f26先可选handler+4(raw+14)再free、cache启用PNG close跳过销毁/session仅a019d9f6 release、初始化a008abb0 payload清理与驱逐/引用内部断边，不能把release称实际像素free。

独立原指令/ABI/厂商字/宽度/重读/返回覆盖及失败清理原序，逐项接受纠正未核，必要纠正只独占报告不改A23。通用解压算法保留明示未恢复/来源未认证合同，实际cache驱逐与像素handler安装未解精确保留，不扩全部cache/图像/物理绘制。交付伪代码结构状态生命周期、事实推断未知、来源、实际独立静态验证和一个后继闭包。禁止固件执行/外连/漏洞/错误输入/历史回放/ROM生产模型修改；共同规则适用。

最新：E05→26fc8d7待E06且仅部分生命周期；H04→8a7807e限定接受H03；F06→f22ec27 filter表达纠正后接受F05。F07已只读定位本地候选实际路径/home/slepher/nuttx-ap01-sim/apps/graphics/lvgl/lvgl（lv_display.c/lv_version.h），尚未认证ROM来源/排除；未启动SIM或构建联网。

## 预备完整任务书 D07（待D06纠正报告整合）

任务ID D07，业务恢复D05条件DMA实际提交者a01b554e的本地描述符/缓冲持有→配置启动→归还连接小闭包。分支codex/re-0041-d07；worktree D:/CodexHome/visualizations/2026/10/23/01a1691a-e178-7710-86c0-84c2ff2d3dfb/re0041-d07；基线含D06最新管理提交。独占reverse/reports/ap01/uart-dma-descriptor-d07-0041-20261023.md及reverse/analysis/uart-dma-descriptor-d07-0041-20261023/。

业务问题：条件+e非零时UART TX怎样把ring一/两段地址/长度交a01b554e，本地DMA描述符谁分配/填充/持有、channel参数与callback对保存地址的依赖、正常完成后何时可复用/归还？具体核心从D05/D06真实a001a240提交和a01b554e直接依赖定位，约5–12函数及必要短配置/回调片段，只此UART TX调用，不接管所有DMA channel/RX框架。D06对型号分支dev+88发布次数和IRQ trampoline/pair安装的纠正作为既有合同；IRQ初始主路径不重做，不把条件DMA当默认。

原指令核descriptor布局/宽度符号/传参/发布顺序、cache维护调用边、buffer指针持有与复制、busy/phase及正常返回/清理；a0019d9a→a002d5d8归还合同针对核，不无限追硬件运行。若存在本地官方SDK候选可只读对照D:/Documents/PlatformIO/Projects/bouffalo_sdk（已有交接固定41bf338a57be53919d99f6c6715a96100428c97d），来源版本/芯片适配须核实，不下载不构建不默认与ROM相同。已认证标准实现才排除，厂商封装继续恢复。交付伪代码结构状态所有权、原字节/厂商编码/间接ABI、事实推断未知、来源、实际静态验证与精确断边及一个后继闭包。禁止设备/固件执行、外连、异常/超时/漏洞、历史回放、ROM生产模型修改；共同规则适用。

## 预备完整任务书 E07（待E06整合）

任务ID E07，业务恢复CTK剩余item+0x34/+0x38扩展字段的一条实际数值消费闭包。分支codex/re-0041-e07；worktree D:/CodexHome/visualizations/2026/10/23/01a1691a-e178-7710-86c0-84c2ff2d3dfb/re0041-e07；基线含E06最新管理提交。独占reverse/reports/ap01/ctk-extra-consumers-e07-0041-20261023.md及reverse/analysis/ctk-extra-consumers-e07-0041-20261023/。

问题：E01/E02已核此两字段创建/响应覆盖/通知/清零释放，但真正页面/业务数值消费者仍未解；它们由谁读取、如何转换/触发更新和保持借用寿命？以一条真实call/data链从cmd52生产/通知合同→一个实际消费者/必要注册→主要数值下游→复用/清理范围组成约5–12函数，若两字段属于同一小数据族可一并恢复，否则选一条并列另一独立后继，不扩全CTK页。入口E01/E02五字段布局/日志、a00a8582 cmd52片段、item查找a00a53c0与item通知a00a389c、已有whole-ROM retained consumer/call索引；a00f4740只读前3组，不能将它当这两组已解消费者。

先核既有E03/E04/E05/E06并避免重复port1栈view或root DELETE负搜索。生产/清理已验收部分只针对核，核心工作是定位新实际读者、结构/数值宽度符号/索引/掩码/返回分支、借用与复制、主要下游调用ABI及正常生命周期。未定位实际读者时给精确引用界限与候选断边，不用单helper冒充完成、不扩全ROM泛扫。字段业务名须有日志/用途依据，未知不猜。交付原指令/伪代码结构状态所有权、事实推断未知、来源、实际静态验证和一个后继闭包。来源未认证不排除；禁止固件执行/外连/漏洞/异常/历史回放/ROM生产模型修改；共同规则适用。

## 预备完整任务书 G06（待G05整合）

任务ID G06，新agent独立复核G05 display真实event38安装→timer resume/通知→调度与poll门→区域消费者闭包。分支codex/re-0041-g06；worktree D:/CodexHome/visualizations/2026/10/23/01a1691a-e178-7710-86c0-84c2ff2d3dfb/re0041-g06；基线含G05最新管理提交。独占reverse/reports/ap01/display-event-review-g06-0041-20261023.md及reverse/analysis/display-event-review-g06-0041-20261023/。

问题：a0086bba向同display+2e8安装callback a0080002/filter38/userdata0、timer a0084ee2(a00e0ac8,16,display)后在a00873b6..be改+8为a0080da6，event38怎样通过display+308/a008bd70清timer+14 bit0/a0087b06通知，在a00804e2 elapsed>=period且repeat非零后间接timer*调用，再由poll非负/revents4门控a00e0ac8？具体核心按G05正式约12合同/必要片段，G04 mask/bit0返回纠正与记录消费只针对核。

重点同display对象关系/真实注册字段和间接ABI、timer16实际单位合同、resume不是立即绘制、callback只读event+8/+4且不读/改/保存param/flags、内建filter38/29对event35不匹配但不能否定动态35/ALL handler、创建/替换/删除资源原序及notifier+9c实际安装断边。a008335e删除同timer并装a00806f8/filter38/userdata=&state+58为替代链候选，保持未知不接管其恢复。独立原字节/厂商编码/宽度/返回重读/所有权，逐项接受纠正未核，纠正只独占报告不改G05。交付伪代码结构状态生命周期、事实推断未知、来源、实际独立静态验证及一个后继闭包；不扩全GUI事件/全部timer/物理绘制、固件执行/外连/漏洞/异常/历史回放/ROM生产模型修改；共同规则适用。
