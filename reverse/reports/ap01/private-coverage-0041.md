# 0041 私有功能恢复覆盖记录

当前滚动状态（2026-10-23恢复）：当前G01/H01/D03/F03功能恢复及A20/E02独立复核六路运行。B21→99c02ab接受B20，C22→004ff56接受C21；D02→1a80623接受D01，F02→17a125f接受F01（均限定验收）。A19→f40ea13待A20，A20已报告一处callee/字段谓词纠正、正式报告未整合；E01→0ff74d9待E02。完整目标未完成，不计算百分比、无新增开源排除、不推送。详见[管理队列](rolling-management-0041-20261023.md)。

更新：2026-10-23。原件 SHA256 `972db4c136c7ed9e24a83c07c1a7fd62040ca018b08ca285216d26b1fee3c6b9`。目标仍为全部非开源程序逻辑；本表是功能导航，不是完整函数认证清单。历史缺陷调查不作为默认续作。

已新增的局部合同：

- [蜂鸣/背光](buzzer-backlight-round3-0041-20261023.md)：请求/线程、PWM 映射、驱动停机及 MiIO 间接入口；正常线程退出消费方仍未知。
- 天气：[调度](weather-scheduling-0041-20261023.md)、[请求/TLS/UI 数据流](weather-dataflow-0041-20261023.md)、[位置与 URL 构造](weather-location-request-0041-20261023.md)；完整库来源、消费者及销毁仍未闭合。
- [工厂门控/灯效](factory-test-0041-20261023.md)、[MiIO 延后设置](miio-deferred-settings-0041-20261023.md)、[模式/自定义功率](mode-control-0041-20261023.md)；嵌套所有权、全部触发者和 MCU 内部行为仍未知。
- UiIFace：[快照/订阅生命周期](uiiface-lifecycle-0041-20261023.md)、[详情页/屏保消费者](ui-total-consumers-0041-20261023.md)、[主题消费者](theme-total-state-0041-20261023.md)。最新补齐动画期掩码覆盖、端口活动位图、功率/模式/温度显示；节点回收、页面销毁、动画结束重放仍待恢复。

- [窗口回调与功率历史](window-history-0041-20261023.md)：开始/执行/完成、render_enabled、180 项环形历史和0x400通知；采样时间、动画重放与所有权仍未闭合。

- [主题在线/设置生命周期](theme-online-0041-20261023.md)：三类在线状态、动态子项构造/清理、型号与版本文本、固定0查询；弹页和GUI/订阅回收仍待恢复。

- [底座接入/轮询](dock-presence-polling-0041-20261023.md)：ID迟滞/有效确认、五相调度、命令组和缓存/断连；MCU封装边界已有统计，内部程序和架构仍未知。

首轮 6487 个枚举节点是模型下界，来源未知 5396；新增局部合同不修改历史分母，不据此计算 ROM 完成率。模式显示名和 MD5 算法已识别，也不等于准确开源来源/版本已认证。

| 分类 | 当前范围 | 证据与限制 |
| --- | --- | --- |
| 已确认开源 | 本轮新增排除 0；全局首轮账本逐函数认证排除也是 0 | NuttX、LVGL、libuv 等有路径/接口识别依据；准确版本、未修改实现范围须另核，不能仅凭名称排除；SIM 版本不代表 ROM 版本 |
| 私有逻辑已恢复 | 普通蜂鸣提交、线程局部合同、背光 setter/关屏包装；天气字段存储及 UI 缓存/五槽注册分发、工厂门控/灯效、UiIFace 生命周期及三个总信息消费者的局部职责 | [蜂鸣器报告](buzzer-backlight-0041-20261023.md)、[天气数据流](weather-dataflow-0041-20261023.md)；仅认证对应入口/局部职责，不代表依赖闭包全部完成 |
| 部分恢复 | BuzzerMng、WeatherApi、FactoryTestMode、UiIFace 控制；MiIO/MiBLE、UI、Wi-Fi、UART/底座 OTA、显示链路 | 天气已连起 timer→request→TLS adapter→JSON sink→UI cache→subscriber；未认证库版本、所有消费者和销毁闭包；其他成果见[索引](README.md) |
| 尚未分析 | 内嵌 MCU 内部函数、PWM 剩余厂商算术及天气请求/数据结构中未审阅部分 | 蜂鸣正常停机入口与退出确认消费方为“已检索但未定位”；PWM 驱动停机和天气调度已获局部合同，不再作为完全未展开范围；已有线索不冒称从未分析 |
| 来源未知 | 第一轮模型 5396 个无来源判定函数，以及未完成来源/修改核对的 SDK 区域 | [首轮机器账本](../../analysis/whole-rom-coverage-0041-20261023-round1.json)保留基线；本轮不改历史分母，不将 UI 重建当原厂源码 |

新增证据：[8 份观测与原字节](../../analysis/buzzer-backlight-0041-20261023.json)、[本轮 getter 原始 REA 结果](../../analysis/buzzer-getter-0041-20261023.json)。指令事实、分析命名/推断、未知项在报告中分别标明。后续按模块功能闭包推进，不恢复短帧、异常内存或端到端缺陷验证待办。

## 本轮独立验收追加（2026-10-23）

- 蜂鸣退出：[A02复核](buzzer-stop-review-a02-0041-20261023.md)接受退出post局部合同，正常停机/确认消费者仍未知；[A04](wait-wrapper-review-a04-0041-20261023.md)与[A06](wait-member-review-a06-0041-20261023.md)接受wait包装及一个成员初始化合同，未证明蜂鸣对象关联。线程userdata透传正在A07恢复。
- 底座轮询：[B01](dock-presence-polling-0041-20261023.md)纠正sent赋值条件；[B03](poll-phase-review-b03-0041-20261023.md)、[B05](poll-phase-one-review-b05-0041-20261023.md)接受cmd58清phase及cmd55 phase=1局部合同，副作用/完整写者仍未知；[B07](basic-info-register-review-b07-0041-20261023.md)接受callback去重及userdata登记合同，ABI/消费者仍待B08。
- PogoPin：[C02](pogo-timer-review-c02-0041-20261023.md)接受timer/context双向字段关系，[C04](pogo-close-review-c04-0041-20261023.md)接受关闭计数及释放封装，[C06](pogo-close-dispatch-review-c06-0041-20261023.md)接受登记/链/消费者传参局部合同。关闭后消费机会的C07有界结论已由[C08](pogo-close-consume-review-c08-0041-20261023.md)复核接受；timer最终删除/调度/全局不变量仍未知。
- 以上均为限定静态验收，整体模块仍部分恢复；新增开源认证排除0。来源未知及厂商封装不排除，MCU内部逻辑尚未分析，不计算整体完成百分比。

追加：[A08](thread-userdata-review-a08-0041-20261023.md)限定接受线程注册userdata透传；[B09](basic-info-callback-review-b09-0041-20261023.md)限定接受分派ABI及日志使用；[C10](detail-summary-review-c10-0041-20261023.md)限定接受详情摘要文本路径。最终适配/触发、runtime对象同一性、ctx所有权和snapshot一致性仍未知；没有新增开源排除。

追加：[A10](thread-adapter-review-a10-0041-20261023.md)限定接受适配ABI，[A12](current-object-writer-review-a12-0041-20261023.md)限定接受一个全局head写入合同；来源识别交A13，不据此认证运行时同一性。[B11](basic-info-dispatch-review-b11-0041-20261023.md)及[B13](compare-contract-review-b13-0041-20261023.md)接受局部分派门控与比较正常返回合同。[C12](detail-mode-update-review-c12-0041-20261023.md)接受模式控件更新，flag视觉含义/查询内部仍未知。没有新增开源排除。

追加：[C14](text-update-entry-review-c14-0041-20261023.md)限定接受格式化文本入口/两遍缓冲合同，准确LVGL版本、下层printf/allocator及生命周期仍未知。[A13](scheduler-source-a13-0041-20261023.md)本地NuttX12.10参考对照待A14；[B14](numeric-location-setter-b14-0041-20261023.md)区域码predicate命名纠正待B15；[C15](text-precondition-c15-0041-20261023.md)实际失效准备合同待C16。以上新增开源排除仍0。

追加：[B15](numeric-location-review-b15-0041-20261023.md)核准a009c5fc为只读区域码判定器（含栈保存/日志），并澄清[旧MiIO报告](miio-deferred-settings-0041-20261023.md)setter误名。正常返回及两个调用局部已认证；配置/logger内部和实际落盘仍未知，无新增开源排除。

追加：[A14来源复核](scheduler-source-review-a14-0041-20261023.md)限定接受本地NuttX12.10候选对照及锁条件/文件组织差异；ROM精确版本、构建配置、厂商修改归因仍未知，新增开源排除0。

追加：[A16](weather-subscriber-review-a16-0041-20261023.md)限定接受一个天气注册/双参callback/首range消费者合同，精确纠正一处指针加载实参记法；[C18](invalidation-gates-review-c18-0041-20261023.md)接受失效入口两门局部；[B17](factory-active-review-b17-0041-20261023.md)澄清有界检索描述，外部active读者仍未知。无新增开源排除，不作整模块认证。

追加：[B19](uart-normal-parser-review-b19-0041-20261023.md)限定接受正常stage/escape状态表与清理写宽度，初始化、所有写入者/真实时序仍未知。未执行固件/回放，未扩历史缺陷任务，无新增开源排除。

追加：[C20](invalidation-third-gate-review-c20-0041-20261023.md)限定接受第三门局部裁剪/祖先遍历/caller零值门，失败交集仍写局部，返回1不等于刷新。两个变换callee、队列/最终显示完成仍未认证，无新增开源排除。

本次用户要求收尾：[A18复核](weather-current-review-a18-0041-20261023.md)已整合，限定接受当前值消费；[B20排队消费](queued-command-consume-b20-0041-20261023.md)、[C21变换谓词](transform-predicate-c21-0041-20261023.md)已整合，均待独立技术复核。其余来源、生命周期、全协议和MCU等开放缺口保留，不因任务结束而认证完成；未新增开源排除。
