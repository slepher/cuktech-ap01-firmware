# AP01 逆向研究索引

当前派发指令（2026-10-25）：完成文档后提交，不再派发新工作；此前持续补位要求不再作为新派发依据，恢复须用户另行明确授权。以下五席配置为后续流程设计。

最新流程规则（2026-10-25）：后续采用三执行＋一预调研＋一专职整合，整合席交接后独占主树及认领表写入；常规研究包须通过完整阶段与实测预测20–40分钟工作量两项准入，短尾合并处理，研究与复核分别计量。见[统一流程](reverse-design.md#34-专职整合代理与主树单写入)、[派发模板](chain-claim-notice-prompt-20261024.md)及[最新管理规则](rolling-management-0041-20261023.md)。此次只更新并提交文档，不再派发新工作，也不代表五席配置已启动。

既有执行记录见[S滚动检查点](interface-batch-s-0041-20261025.md)：当时为三执行＋独立预调研；运行状态须以唯一管理表和当前代理树核对，不能从历史快照推定当前在跑数量。

最新滚动状态（2026-10-25）：用户已明确持续三席并已补位；[R批次检查点](interface-batch-r-0041-20261025.md)覆盖Q01–Q07及计量。此前“无释放工具未补位”仅为旧指令时快照；当前工具限制不变，未承诺无限新建。

最新：新聊天[Q三组独立复核](interface-review-q-0041-20261024.md)已整合，P-16/P-17、P-18、P-19差集限定接受，完整接口未闭。三代理completed；环境无关闭/释放工具，未继续补位。以下停止/持续滚动等为历史快照。

最新状态：按用户要求停止派发，临时工作树及历史任务分支清理完成；主仓成果/ignored证据保留，待复核项见[精简交接](next-chat-handoff-20261024.md)。下方滚动运行状态为历史快照。

当前持续滚动：[批次P底座协议与应用接入](interface-batch-p-0041-20261024.md)，三席完成即补位；检查点不自动收尾，实时认领见管理表。

最新批次：[底座协议与应用接入接口批次N](interface-batch-n-0041-20261024.md)，三项阶段经合并非作者复核限定接受，完整接口断边保留；包含本批耗时/token实测与清理记录。以下旧“当前”段落保留为当时快照。

按功能替代口径查看现状：[逆向成果、开源替代与剩余缺口评估（2026-10-24）](reverse-gap-and-opensource-replacement-20261024.md)。区分已恢复行为、可用开源方案和专有/硬件缺口，不以函数候选数或 SIM 验收计算全 ROM 完成率。

流程入口：[逆向工作流程与全部注意事项](reverse-design.md)；唯一认领位置：[管理记录的链条认领表](rolling-management-0041-20261023.md#链条认领表)；转达现有任务：[防重复规则通知 prompt](chain-claim-notice-prompt-20261024.md)。以下运行状态与带日期记录属于历史快照，实际状态由当前管理窗口核实。

最新流程（2026-10-24）：新任务 `fork_turns: "none"`，按单代理约半小时工作量切分完整接口/独立状态机阶段，相关小差集合并非作者复核；停止默认深挖可用开源替代的库内部，仅恢复必要原ABI、专有业务及硬件适配。本次只更新规则，未恢复派发；完整要求与交付模板见上述流程和通知。

当前状态（2026-10-24，复核完成）：A77/A81/F33三项非作者复核均限定接受，共173项静态检查通过，A76/A80/F32待复核状态已关闭。%s取参/输出、其它copy长度、实际quit/queued I排空/最终free仍未闭；不恢复滚动派发。详见[管理记录](rolling-management-0041-20261023.md)。未提交、未推送，本地忽略证据仍保留原路径。





最新接口连线：[A63](reader-driver-register-review-a63-0041-20261024.md)接受真实header→node→D注册桥，[A65](reader-driver-slot-review-a65-0041-20261024.md)接受D首byte`/`、config4096及四槽绑定；[A66](reader-driver-open-close-a66-0041-20261024.md)/[A67](reader-driver-open-close-review-a67-0041-20261024.md)确认H为fd+1编码而非可free对象，路径仅证`/%s`与varargs接口，实际格式输出仍未闭。[A68](reader-driver-read-seek-a68-0041-20261024.md)恢复read/seek返回及参数word协议，A69复核中，下层IO/off_t未认证。MiIO的[F25](miio-invocation-queue-lifetime-f25-0041-20261024.md)/[F26](miio-invocation-queue-lifetime-review-f26-0041-20261024.md)给出显式存储/消息身份前提下的I指针值与内部Msg独立生命周期；[F24](miio-queue-send-wait-review-f24-0041-20261024.md)已纠正旧整体caller guard及1处伪码读清顺序，getter本体不变。[F27](miio-queue-mode-init-gap-f27-0041-20261024.md)只证同Q写点7，F28待复核，不推完整返回后mode不变。三席继续滚动，不改变默认五照片mode0或任何实机/完整ROM边界。

继续滚动的局部闭包：[F15同队列size身份桥](miio-queue-size-gap-f15-0041-20261024.md)由[F16](miio-queue-size-review-f16-0041-20261024.md)限定接受，正常同M setup/attach下两ctx保存同L、L持Q且Q.size初值4；[F17有效对齐n4复制](miio-queue-copy4-f17-0041-20261024.md)由[F18](miio-queue-copy4-review-f18-0041-20261024.md)限定接受，实为byte顺序拷贝而非一次word操作。二者不认证Msg存储有效/容量/寿命或实际执行。[A59](reader-driver-writer-review-a59-0041-20261024.md)限定接受A58有界候选排除；[A60两槽初始化writer](reader-driver-global-init-a60-0041-20261024.md)找到真实stride4/head0写端，尚待A61非作者复核，节点登记/真实D/slot仍未闭。三席已补到F19接收端、F21消息来源、A62注册caller旧证据定位，管理表维护实时状态。

当前滚动新增（bd457a6续作）：[F13队列接口与发布顺序](miio-native-queue-f13-0041-20261024.md)由[F14](miio-native-queue-review-f14-0041-20261024.md)限定接受；[G25实际op3实例化](pogo-poll-op3-g25-0041-20261024.md)由[G26](pogo-poll-op3-review-g26-0041-20261024.md)限定接受，新增独立body0；[G27返回槽来源](pogo-poll-error-slot-g27-0041-20261024.md)由[G28](pogo-poll-error-slot-review-g28-0041-20261024.md)限定接受，稳定/别名/异步及正常可达性仍未知；[A58注册writer旧证据消歧](reader-driver-writer-gap-a58-0041-20261024.md)排除一个同偏移栈对象候选，真实writer仍未闭。F15正在补同queue size身份桥、F17核n4对齐copy域、A59非作者复核A58；实时状态继续以唯一管理表为准。

本次三席恢复成果：[MiIO请求寿命独立复核F12](miio-request-ownership-review-f12-0041-20261024.md)限定接受F11/1–2，新增业务0；[环服务G23](pogo-poll-ring-consume-g23-0041-20261024.md)恢复counter门、局部复制与完成记录消费，后段可达性/成功提交仍未知；[driver选择A56](reader-driver-selection-a56-0041-20261024.md)恢复路径首字节到首个匹配D的动态链遍历，实际注册实例/slot目标仍未知。[G24](pogo-poll-ring-consume-review-g24-0041-20261024.md)与[A57](reader-driver-selection-review-a57-0041-20261024.md)已分别独立限定接受G23/A56差集，复核新增0。三位subagent已停止，成果未提交，临时工作区/本地任务分支已清理；完整ROM目标仍未完成。

本轮新增[底座ID接入、五相调度与轮询](dock-presence-polling-0041-20261023.md)：20ms注册、五相轮转、六次有效ID判断与迟滞阈值、两组命令轮询、响应缓存和断连释放。三份MCU流的边界/高熵统计已保存，架构及内部程序仍未知，未尝试执行或解密。

本轮新增[主题在线状态与设置页生命周期](theme-online-0041-20261023.md)：恢复 status1/2/其他三条路径、动态子项构造/删除标志、窗口和页面查找、型号/版本文本，以及固定返回0的MCU OTA标志查询；补回两处删除实参。特殊态来源、完整GUI删除/订阅回收仍未知。

本轮新增[窗口回调与 180 点功率历史](window-history-0041-20261023.md)：恢复窗口开始/执行/完成入口、render_enabled 关闭/恢复、364 B 环形历史及最大值重扫，两个功率历史调用点均为 LHU，返回非零触发0x400。动画结束后的主动重放、采样时间和完整所有权仍未知。

本轮新增[主题总信息消费者](theme-total-state-0041-20261023.md)：恢复动画期覆盖保存掩码、端口活动位图、两块主题页面功率/模式更新，以及温度位置与三段标签。明确区分本地 UI 状态和 MCU 执行；动画结束重放、全部状态字含义与销毁仍未闭合。

本轮新增[UiIFace 快照/订阅生命周期](uiiface-lifecycle-0041-20261023.md)及[总信息 UI 消费者](ui-total-consumers-0041-20261023.md)：380 B 总对象、424 B 端口项、在线/离线与释放顺序、订阅注册/摘链、两个页面 callback 和页面查找合同。ROM 确认模式名为 AI 智配/极速单充/均衡输出/自定义；该名称不认证 MCU 算法。嵌套对象、节点回收、页面销毁及全部响应仍未闭合。

本轮新增[模式控制与 UI/UART 联动](mode-control-0041-20261023.md)：恢复离散功率索引、自定义参数回退、0x60 的 1/4 B 载荷、UI 控制变化掩码及 callback(userdata,snapshot)。本地状态通知与 UART 提交分别记录；响应协调、快照/订阅生命周期及 MCU 执行仍待恢复。

本轮新增[MiIO 延后设置与位置联动](miio-deferred-settings-0041-20261023.md)：恢复共享 timer 的 0..6 全部分支、三个直接提交点、8 B 请求所有权、模式参数传递、城市/区县直接持久化及两位标志条件；天气重排桥为 timer 控制后调用 start(1,2000)。未定位全部间接提交者或完整销毁链，模块仍为部分恢复。

最新功能恢复：[蜂鸣/背光第三轮](buzzer-backlight-round3-0041-20261023.md)补 MiIO 零延时 timer→亮度/蜂鸣间接链及 PWM 额外 ioctl，正常线程退出确认消费方仍未定位；随后新增[工厂测试启动门控与灯效](factory-test-0041-20261023.md)，均为静态、部分恢复。

本目录保存固件研究结论。外部程序入 ROM 的通用方法由本项目维护，具体业务实现及发布由使用方维护。

| 主题 | 入口 |
| --- | --- |
| 天气位置与请求构造 | [缓存/持久化、两条 URL、摘要输入和 RV32 参数](weather-location-request-0041-20261023.md)、[机器合同](../../analysis/weather-location-request-0041-20261023/contracts.json)；只读静态恢复，精确库来源和生命周期仍未闭合 |
| 天气请求与数据发布 | [TLS 适配、156B 天气对象、UI 缓存和双参数订阅](weather-dataflow-0041-20261023.md)、[机器合同](../../analysis/weather-dataflow-0041-20261023/contracts.json)；包含未建函数入口的原字节恢复，模块仍部分恢复 |
| 蜂鸣器与背光第二轮 | [停机边界、通道映射、设置页定时入口](buzzer-backlight-round2-0041-20261023.md)：PWM2/GPIO18、PWM3/GPIO31；线程退出确认消费方仍未定位，模块保持部分恢复 |
| 天气业务调度 | [最近请求节流、重试与逐次注册](weather-scheduling-0041-20261023.md)、[两份函数观测](../../analysis/weather-scheduling-0041-20261023.json)；请求/TLS/解析未据此认证完成 |
| 当前功能恢复覆盖 | [五类覆盖记录](private-coverage-0041.md)、[蜂鸣器与背光恢复](buzzer-backlight-0041-20261023.md)、[8份函数观测及ROM字节](../../analysis/buzzer-backlight-0041-20261023.json)；本次以功能语义恢复为主线，旧缺陷验证计划仅保留历史背景 |
| 范围与证据标准 | [研究需求](requirements.md)、[研究计划](plan.md)、[任务](task.md)、[状态](status.md) |
| 当前持续目标 | [0041 整 ROM 非开源部分逆向](whole-rom-0041.md)：全局来源与覆盖账本、私有实现和依赖闭包；实验与正式 ROM 隔离 |
| 底座私有协议续作 | [UART帧、排队、MCU OTA状态机与内嵌固件](usb-interface-ota-0041-20261023.md)、[27份函数摘录](../../analysis/usb-interface-ota-0041-20261023.json) |
| UART 重试与接收长度 | [耗尽语义、调度门控与长度缺陷回放](uart-retry-receive-0041-20261023.md)、[11份函数摘录及14组回放](../../analysis/uart-retry-receive-0041-20261023.json)；合成内存验证，真实底座可达性待核 |
| UART 普通应答边界 | [短输入、固定长度更新与接口查找](uart-response-0041-20261023.md)、[两份函数证据及14组回放](../../analysis/uart-response-0041-20261023.json)；零页为合成夹具，解析器与回调端到端验证待补 |
| 外部程序编译和打包进 ROM | [打包说明](design.md)、[0041 多屏幕宿主架构](multi-screen-app-host-0041.md)、[宿主实施计划](multi-screen-app-host-implementation-plan-20261020.md)、[codex_status现状](codex-status-host-baseline-20261020.md)、[0031 XIP 实现](app-implementation-20261013.md)、[模块源码](../../../tooling/firmware-modules/README.md) |
| 0041 屏幕宿主验证与接口 | [共存与窗口热重建](screen-host-lifecycle-20261020.md)、[重构交付与验收](screen-host-refactor-20261020.md)、[追加方案验证](screen-host-append-validation-20261020.md)、[当前接口合同](screen-host-interface-0041.md)、[原件执行检查](../../../tooling/scripts/test-screen-window-0041.py) |
| 0041 多应用载入、卸载与应用 OTA 设计 | [Astra 详细方案](app-lifecycle-ota-0041-design-20261021.md)；常驻 OTA 不参与卸载，仅限 0041，设计待实施 |
| 静态工具与来源 | [静态分析方法](reverse-design.md)、[阶段报告](report.md)、[上游材料对照](../cuktech-ap01-repository-value-analysis.md) |
| 0031 分区、启动和堆 | [分区与启动](knowledge/0031分区与启动入口复查.md)、[网络与 HTTP](knowledge/0031网络监听与HTTP复查.md) |
| 0031 首次安装与槽尾实验 | [首次安装](first-install-0031-20261018.md)、[实机成功记录](knowledge/0031-tail-physical-success-20261018.md)、[镜像准入](ota-image-admission-20261019.md) |
| 0031 扩容、物理读取和诊断 | [扩容](ota-expansion-0031-20261018.md)、[启动调查](knowledge/0031-expanded-boot-investigation.md)、[网络控制台](knowledge/0031-network-console.md)、[PEC 与升级](knowledge/0031-pec-readback-and-controlled-upgrade.md) |
| 0041 常驻独立诊断 | [实现、接口与部署记录](independent-diagnostic-0041-20261021.md)、[只读客户端](../../../tooling/scripts/diagnostic-client-0041.py) |
| 0041 续作与原厂上层 | [交接](0041-handoff.md)、[上层恢复](upper-layer-0041-20261017.md)、[MiIO/MiBLE](miio-mible-protocol-rea-0041-20261017.md) |
| 0041 静态比较与签名 | [版本对比](0041-reverse-20261013.md)、[签名分析](knowledge/0041签名与Bridge接口分析.md)、[下载核验](firmware-download-20261013.md) |
| REA / RISC-V / Ghidra | [私有分析环境](private-profile-0041-20261017.md)、[RISC-V 实现](rea-riscv-implementation-20261016.md) |
| QEMU 模型与 OTA | [显示交接](qemu-display-handoff-20261017.md)、[RTC 与显示](qemu-rtc-display-20261017.md)、[0041 OTA](qemu-ota-final-20261017.md)、[0031 OTA](qemu-ota-0031-20261017.md) |
| 0041 显示链路续作 | [刷新就绪、pan 与 LCD 工作回调](display-chain-0041-20261023.md)、[原字节及局部合同](../../analysis/display-chain-0041-20261023.json)；仅离线研究，未进入正式 ROM |
| 原厂 UI 重建 / NuttX SIM | [SIM 环境](nuttx-sim-20261016.md)、[静态 UI](ui-reverse-20261016.md)、[重建验收](application-rehost-complete-0041-20261017.md)、[功能矩阵](application-function-matrix-0041.json)、[Wi-Fi 缺口](knowledge/0041-sim-wifi-selection-gaps.md) |
| 原厂代码、资源与覆盖缺口 | [文件与资源盘点](factory-code-resources-inventory-0041-20261020.md)、[C 文件→函数→资源映射](factory-reference-map-0041-20261020.md)、[机器清单](../../analysis/factory-reference-map-0041.json)、[离线生成器](../../../tooling/scripts/build-factory-reference-map.py)；复核命令 `python tooling/scripts/build-factory-reference-map.py --check`，只重算和比对，不执行固件 |
| 恢复与限制 | [恢复评估](failure-recovery-20261013.md)、[恢复策略](recovery-policy-20261017.md)、[USB 调查](usb-firmware-check-20261013.md) |

带日期的文件保留该阶段的验证边界；“当时未取得原件”“未安装”等表述不能替代后续报告。原始产物与私有材料的位置规则见[仓库入口](../../../README.md)。

本轮滚动成果及独立验收入口：见[覆盖记录追加](private-coverage-0041.md)与[逐任务交接](rolling-management-0041-20261023.md)。正常停机、timer最终删除和来源认证等缺口仍保持开放。
