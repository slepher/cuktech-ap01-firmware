# 0041 六路滚动管理（2026-10-23恢复）

用户最新授权恢复持续六路推进，取代历史收尾暂停与三路上限。原管理交接已归档至 rolling-task-history-0041-20261023.md。主窗口只管理，不作函数逆向或技术语义判断。环境共7席，主窗口1席，研究/复核6席。当前六个任务均已真实启动，见运行快照。

## 共同规则

只做0041静态功能恢复；禁止执行固件、连接设备/外部服务、漏洞/异常输入/缺陷验证、修改安全检查、ROM、生产代码、构建配置和分析器模型；不推送。只写独占reverse/analysis和reverse/reports/ap01文件。只用自己的独立worktree和分支，每次shell显式workdir并在PowerShell Set-Location。其他agent同时工作，不撤销他人修改、不改主树或共享索引，不创建下级agent、不自行接后继。忽略ROM/证据/工具从主仓库绝对路径只读访问；不复制工作区，不共享可写数据库或切换全局REA。优先留存证据；若工具不能隔离则报告管理者。临时状态/日志放各自独占analysis目录。只恢复正常原程序行为，不擅自修正。

交付列问题/范围/结论、业务行为、函数地址/参数/返回/调用、必要伪代码结构体状态转换、所有权生命周期、可定位证据与原指令、事实/推断/未知、来源与恢复程度、实际静态验证、断边和一个后续闭包。伪代码不是原源码；保留调用顺序、重读、宽度/符号、返回判断、失败/清理和间接ABI。边界/厂商指令须核原字节，不仅信反编译。标准库只有来源可核实才排除，适配/回调仍恢复；不新增哈希清单/复制清单/机械重复证据。不编译项目，不运行历史回放。完成标准为原问题闭包得到有证据答案或明确可定位断边，不能缩成短helper声称完成；预计约45–90分钟，提前实质完成立即提交结束。

接近提交提前报告结论、剩余验证、阻塞和后继建议。检查差异、必要验证、明确路径git add、提交、报告commit/验证/未知/干净状态后结束。主窗口作范围验收，技术验收由新独立agent。恢复成果可先整合为待复核；不得自验冒称验收。每项完成即整合补位，从启动时最新管理提交创建新树；运行任务不移动基线。语义冲突交agent；回收仅限干净且已整合worktree，分支保留。用户要求收尾即停止派发。

主仓库：D:/Documents/PlatformIO/Projects/cuktech-ap01-firmware。所有任务初始共同研究基线 ab9716e；实际启动基线为含本任务书的管理提交，在派发消息及运行表记录。

## 当前任务书



## 实际运行快照

当前4恢复2独立复核共6个运行subagent，主窗口另计；已结束任务不计运行。

|任务|agent|启动基线|状态|
|---|---|---|---|
|A22|/root/a22_png_review|875f762|运行中|
|E05|/root/e05_ctk_close|f31a27a|运行中|
|D05|/root/d05_uart_drain|59d81c2|运行中|
|F05|/root/f05_exit_callback|3aba13a|运行中|
|G04|/root/g04_submit_review|f82380b|运行中|
|H03|/root/h03_weather_close|dcc2a08|运行中|

整合及限定验收映射见历史交接与覆盖记录，每项完成即检查整合补位。

## 近期滚动候选（未启动）

- A23：A22验收后，PNG class0 open→会话像素对象→注册close归还的小闭包，不扩通用解压算法；A22已启动。
- D06：D05 TX ring正常启动/完成/唤醒闭包独立复核，待D05整合；D05已启动。
- E06：E05 app注销/归还完整闭包独立复核，待E05整合；E05已启动。
- F06：F05返回后对象callback完整闭包独立复核，待F05整合；F05已启动。
- G05：G04验收后恢复display event35/38实际descriptor注册→callback/param消费→38调度连接闭包；G04已启动。
- H04：H03页面context/离页触发完整小闭包独立复核，待H03整合；H03已启动。

以上只是预备问题，不冒称已派发。每次空位时依据最新整合和agent建议确定完整任务书、基线及独占输出，再启动新agent；独立技术复核须换新agent。










## 当前完整任务书 H03（已启动，基线dcc2a08）

任务ID H03，业务恢复type0x19天气页context最终所有权和离页删除触发闭包。分支codex/re-0041-h03；worktree D:/CodexHome/visualizations/2026/10/23/01a1691a-e178-7710-86c0-84c2ff2d3dfb/re0041-h03；基线含H02最新管理提交。独占reverse/reports/ap01/weather-page-close-h03-0041-20261023.md及reverse/analysis/weather-page-close-h03-0041-20261023/。

业务问题：a00b821e构造分配的0x74B context由谁持有和最终归还，上层正常导航/离页如何把0x29 DELETE事件交给a00b3b26，wrapper清理与控件递归销毁怎样排序？先读H01/H02的真实page/type0x19挂接/删除合同；a00b3b26仅清28word→注销→free(wrapper)→清page+10，不能假装已释放context。沿一个实际离页调用者/事件分发→删除回调→context引用归还或未归还边组成约5–12函数小闭包；真实ctx释放者尚未知，需据原指令查，不能凭类型名称拼造。

包含必要导航注册/触发、事件ABI、页面/ctx/wrapper/子控件所有权，既验收天气重排/主要显示/五槽注销只针对核，不重复全天气数据流。若无法证实最终free(ctx)，给明确正常路径、引用搜索边界和精确断边，不扩所有GUI删除、不作缺陷判断。完成需生命周期/状态伪代码结构、原指令/返回/宽度/顺序、事实推断未知、来源、实际静态核验与一个后继闭包。通用事件/allocator库仅来源认证才排除，厂商适配仍恢复。排除全UI/所有导航、固件执行/外连/漏洞/历史回放/正式ROM生产模型修改；共同规则适用。

A20已整合ab67c6f，正式技术裁定为有一处callee/字段谓词纠正后限定接受A19，原add_flag状态门说明以A20为准。旧待正式报告仅为历史记录，本状态覆盖。




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

## 当前完整任务书 E05（已启动，基线f31a27a）

任务ID E05，业务恢复CTK app订阅与正常离页注销/对象归还闭包。分支codex/re-0041-e05；worktree D:/CodexHome/visualizations/2026/10/23/01a1691a-e178-7710-86c0-84c2ff2d3dfb/re0041-e05；基线含E04最新管理提交。独占reverse/reports/ap01/ctk-app-close-e05-0041-20261023.md及reverse/analysis/ctk-app-close-e05-0041-20261023/。

业务问题：a005d142注册的a00adabc(app,item)与app由谁持有、正常退出如何停止回调/注销62fcb530节点、先后归还哪些app/page资源？先读E03/E04已验收注册/触发/栈消费链，E04对port1/port2互斥与栈布局措辞纠正须沿用。选择一个实际app退出/DELETE触发者→注销→节点/app清理闭包，约5–12核心和必要短依赖；具体退出callback/注销器地址目前未知，须据注册caller、app挂接和保留incoming refs定位，不凭同名GUI函数拼链。

包含真实callback键/userdata、注销是否仅摘链或还free、app/页面/上下文分配与清理顺序、回调期间可达性；不重复a00f4740内部或port1数值显示，既有订阅链/allocator合同针对核。未能证明节点回收/退出触发时给有界检索与精确断边，不把注销等同释放，不扩大所有UI/所有订阅者/全局deinit。完成伪代码结构状态生命周期、原指令/地址/ABI/写宽/返回覆盖、事实推断未知、来源、实际静态验证和一个后继闭包。来源未认证不排除标准实现/厂商修改。禁止固件执行/外连/漏洞/异常/历史回放/ROM生产模型修改；共同规则适用。

## 预备完整任务书 H04（待H03整合）

任务ID H04，新agent独立复核H03真实按键离页→父/子DELETE→递归析构与context断边闭包。分支codex/re-0041-h04；worktree D:/CodexHome/visualizations/2026/10/23/01a1691a-e178-7710-86c0-84c2ff2d3dfb/re0041-h04；基线含H03最新管理提交。独占reverse/reports/ap01/weather-page-close-review-h04-0041-20261023.md及reverse/analysis/weather-page-close-review-h04-0041-20261023/。

问题：a00afc88天气子页创建片段及8B父state(type19)→输入hook a00b35ee event11/key10/窗口64零门→恢复主页面/删除a00ded6c(window)→父DELETE a00b1a02→子天气DELETE a00b3b26→控件递归/类析构摘链free的原序与所有权是否成立？核心以H03正式清单约5–12函数为准，只核该正常type19路径，不复核全GUI删除系统。已验收H02子hook/重排/注销只针对核。重点父8B state、20B wrapper、116B ctx三者区分，父stop timer/free state与子清28word/unregister/free wrapper排序、事件mask/vendor条件/返回门、对象递归/类析构前后指针持有及ctx最终free未证的有界范围。

独立原指令/厂商字/事件ABI/宽度/调用重读/失败分支，逐项接受纠正未核；必要纠正仅独占报告不改H03。不要把构造直接引用搜索变穷尽别名、不要把对象free拼成ctx free、不引入缺陷判断。交付伪代码布局状态生命周期、事实推断未知、来源、实际独立静态验证和断边；标准库仅来源认证可排除，私有胶合保留恢复。排除全导航/其他窗口类型、固件执行/外连/漏洞/异常/历史回放/ROM生产模型修改；共同规则适用。

最新整合：E04→f31a27a范围措辞纠正后限定接受E03；A21→875f762、G03→f82380b为待独立复核恢复，A22/G04运行中。

## 预备完整任务书 A23（待A22整合）

任务ID A23，业务恢复PNG class0 open→decoder-session资源→已注册close归还闭包。分支codex/re-0041-a23；worktree D:/CodexHome/visualizations/2026/10/23/01a1691a-e178-7710-86c0-84c2ff2d3dfb/re0041-a23；基线含A22最新管理提交。独占reverse/reports/ap01/png-session-lifecycle-a23-0041-20261023.md及reverse/analysis/png-session-lifecycle-a23-0041-20261023/。

业务问题：A21/A22已确认open a00eb7b6、close a00eab9a真实注册；正常class0 ROM源怎样进入open、分配/保存像素或user_data、由谁持有decoder-session、close如何归还，成功与失败清理分支怎样保持原行为？从真实open调用/注册ABI和该class0分支出发，只展开session创建/像素对象持有/转换或包装/close及必要直接依赖，约5–12核心；底层通用解压/PNG算法可先作为明确调用合同，但来源未认证仍保留未恢复/未认证记录，不能静默排除。

既验收registry/info/header和A20状态门只针对核，不重复整个image setter、其他image class或完整压缩算法。对象/内存分配/所有权、decoded指针与src借用、返回值和清理顺序、间接open/close ABI必须原字节核，失败分支不能擅自修正，不做错误输入测试。若session owner或最终close调用者未连上，列实际字段/调用入口与精确断边，不以注册存在推成功执行。交付伪代码结构状态生命周期、原指令证据/厂商字/宽度、事实推断未知、来源、实际静态验证和一个后继闭包。排除像素执行/渲染观察、固件执行/外连/漏洞/历史回放、ROM生产模型修改；共同规则适用。

## 预备完整任务书 G05（待G04整合）

任务ID G05，业务恢复display事件35/38 descriptor注册→callback/param消费→刷新调度通知闭包。分支codex/re-0041-g05；worktree D:/CodexHome/visualizations/2026/10/23/01a1691a-e178-7710-86c0-84c2ff2d3dfb/re0041-g05；基线含G04最新管理提交。独占reverse/reports/ap01/display-event-flow-g05-0041-20261023.md及reverse/analysis/display-event-flow-g05-0041-20261023/。

业务问题：G03提交过程借用clipped栈矩形发0x35，新增记录后发0x38 param0，display+2e8的事件descriptor由谁安装、真实callback怎样读/改/保存param及0x38如何触发a00e0ac8消费者？入口G03/G04合同、a00814f4、a008ad80..ad98过滤/userdata/callback(event*)、提交a00ddd90/ddd76和event timer消费者a00e0ac8。安装callback身份/调度连接当前未知，须先定位真实descriptor写入及参数，不猜timer回调，不把event38默认当唤醒。

范围约5–12核心及必要短依赖，选择同一display正常注册/回调/直接调度消费小闭包，明确callback同步返回/bit0/bit1归一门、param持有/复制、生命周期与注销；已验收区域记录合并/复位只针对核，不重做全部数学。若多个独立callback并存，选实际必要目标，其他列候选/断边，不接管整个GUI事件系统或最终绘制。完成原字节/间接ABI/厂商字/宽度返回/顺序、伪代码结构状态与所有权、事实推断未知、来源、实际静态验证和一个后继闭包。来源未认证不排除，标准list/timer合同可保留并说明认证缺口。排除物理刷新/DMA/LCD、异常param/漏洞、固件执行/外连/历史回放、ROM生产模型修改；共同规则适用。

## 预备完整任务书 D06（待D05整合）

任务ID D06，新agent独立复核D05 UART TX ring实际IRQ主路径与条件DMA的消费/通知闭包。分支codex/re-0041-d06；worktree D:/CodexHome/visualizations/2026/10/23/01a1691a-e178-7710-86c0-84c2ff2d3dfb/re0041-d06；基线含D05最新管理提交。独占reverse/reports/ap01/uart-ring-review-d06-0041-20261023.md及reverse/analysis/uart-ring-review-d06-0041-20261023/。

业务问题：已知设备private+e初值0怎样使a001a70a DMA入口早退，而真实open的lower+8→a001a1d8安装IRQ3d/a0019ae0(dev)，common dispatcher a0001012..1046把arg装a2，status门→a002d36a消费ring→tail/等待者通知，条件+e非零又怎样经DMA安装/回调归还？按D05正式核心清单，约5–12核心及必要短IRQ/安装片段；重点私有初值与运行时写者未知的区别，不把初值当永恒配置、不省实际IRQ以DMA替代。

原指令独立核halfword tail先发布再读取ring及按值lower发送、回绕/重读、lower+48=0/ready恒1的条件、空环txint0、有进度a002be92先poll通知再唤醒dev+18；条件DMA lower+20=a001a240、a001a3f6..a400注册a0019d9a/a00264ec、dev+88累计与a002d5d8清+88/+84/+80后的通知，具体边以最终报告为准。先发布tail不等同硬件发送完成。已验收D04 source复制/引用和帧队列只针对核，厂商字/间接ABI/写宽符号/返回覆盖须原编码核。

逐项接受纠正未核，必要纠正只独占报告不改D05；保留动态private/ops写者、完整中断优先级/硬件交付、final close及未解同步内部断边，不扩全IRQ/DMA/UART或异常超时。交付伪代码结构状态生命周期、事实推断未知、来源、实际独立静态验证及一个后继闭包。来源未认证不排除。禁止固件执行/设备/外连/漏洞/历史回放/ROM生产模型修改；共同规则适用。

## 预备完整任务书 F06（待F05整合）

任务ID F06，新agent独立复核F05显示对象来源/DELETE清理与可选callback断边闭包。分支codex/re-0041-f06；worktree D:/CodexHome/visualizations/2026/10/23/01a1691a-e178-7710-86c0-84c2ff2d3dfb/re0041-f06；基线含F05最新管理提交。独占reverse/reports/ap01/display-exit-review-f06-0041-20261023.md及reverse/analysis/display-exit-review-f06-0041-20261023/。

问题：a005ccc6→a0084b96→a008aec0分配zero324对象/58B payload→a00873ea写out，配置/dev/fb0与/dev/input0，是否确为返回后a0081554显示清理对象，而不是loop walker？真实DELETE注册a0086cd4→a007ffa0→a01b93b4(obj+2e8 event list,cb=a00800b4,filter29,userdata=obj)及a008acfa分发event+c userdata→callback后端归还→后续可选obj+2b8/payload/obj清理顺序是否成立？按F05正式约5–12核心与必要片段；F03/F04栈loop/关闭合同只针对核，不重新扫timer。

重点+2b8仅可证构造zero初值，非NULL安装/真实callback未定位，普通SW立即数有界搜索不涵盖别名/批量/厂商store，不能推返回时必NULL；backend=obj+2e0清理、fd>=0 close wrapper/free backend+34/backend与对象资源顺序、callback返回后字段重读须原指令核。显示闭包无已证loop9428连接但opaque callee不能作全局否定。独立核ABI/厂商字/写宽/返回分支/所有权，逐项接受纠正未核，纠正只独占报告不改F05。不扩全部显示/输入或obj+2b8后继恢复，保留来源认证和上层loop断边。交付必要伪代码结构状态生命周期、事实推断未知、来源、实际静态验证与一个后继闭包；禁止固件执行/外连/漏洞/异常/历史回放/ROM生产模型修改；共同规则适用。
