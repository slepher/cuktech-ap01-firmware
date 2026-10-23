# 0041 私有功能恢复覆盖记录

当前滚动状态（2026-10-23）：研究基线 `7c17501`；A01/A02、A03/A04、A05/A06、A07/A08、B01、B02/B03、B04/B05、B06/B07、C01/C02、C03/C04、C05/C06、C07/C08已通过限定技术验收。B08已整合待B09复核。当前运行 A09（线程适配入口，基线d85348e）、B09（callback ABI复核，基线99899e3）、C10（详情摘要复核，基线b885567；C09待验收），各自独立worktree；优先维持三worker，后继A10/C10已预备。正常停机、timer最终停止/删除及MCU内部程序仍未知；无新增开源排除，不计算全ROM完成百分比。本轮授权本地提交/整合，禁止推送。详见[任务书、提交与验收交接](rolling-management-0041-20261023.md)。

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
