# AP01 逆向研究索引

当前滚动状态（2026-10-23恢复）：当前G01/H01/D03/F03功能恢复及A20/E02独立复核六路运行。B21→99c02ab接受B20，C22→004ff56接受C21；D02→1a80623接受D01，F02→17a125f接受F01（均限定验收）。A19→f40ea13待A20，A20已报告一处callee/字段谓词纠正、正式报告未整合；E01→0ff74d9待E02。完整目标未完成，不计算百分比、无新增开源排除、不推送。详见[管理队列](rolling-management-0041-20261023.md)。

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
