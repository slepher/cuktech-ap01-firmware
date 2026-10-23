# 0041 私有功能恢复覆盖记录

当前滚动状态（2026-10-23恢复）：成果复用规则已调整；A25/D08/E07/F08/G06/H06均已整合，后继A26/D09/E08/F09/G07/H07正在按精确断边准备。D08/G06/H06独立复核，F08精度纠正后限定接受，均不重复记新增功能；E07未闭消费者。SIM验收不等于ROM完成，来源未新增整库排除。详见[管理队列](rolling-management-0041-20261023.md)。

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

最新独立纠正验收：[A20](weather-icon-review-a20-0041-20261023.md)已整合ab67c6f；A19 flag状态与更新副作用所列add写位后callee及谓词说明须以A20纠正为准。其余仅按A20逐项表限定接受，decoder身份、q写者、销毁与物理显示仍未知。

新增独立闭包验收：[G02](region-transform-review-g02-0041-20261023.md)限定接受[G01](region-transform-flow-g01-0041-20261023.md)，[H02](weather-lifecycle-review-h02-0041-20261023.md)限定接受[H01](weather-subscriber-lifecycle-h01-0041-20261023.md)。[D03](uart-write-object-d03-0041-20261023.md)、[F03](miio-loop-close-f03-0041-20261023.md)仅作者静态验证通过，已整合待独立复核；实际硬件、完整关闭和全部生命周期断边保留。

新增：[F04](miio-loop-close-review-f04-0041-20261023.md)限定接受F03关闭条件链及其断边，无语义纠正；[E03](ctk-view-dataflow-e03-0041-20261023.md)恢复真实注册/触发→CTK栈view→主要port1消费，待E04独立复核。

最新纠正验收：[D04](uart-write-review-d04-0041-20261023.md)有一处optional_mark分支纠正后限定接受D03；helper对应伪代码以D04为准。实际acquire a3=0的正常fd→write→ring复制闭包不变，最终close、DMA/tail/唤醒和硬件交付仍断边。

新增：[E04](ctk-view-review-e04-0041-20261023.md)对E03有一处范围措辞纠正后限定接受：port1/port2共用局部地址但端口谓词互斥，不表示同次通知连续两转换。[A21](png-info-lifecycle-a21-0041-20261023.md)真实PNG registry/info/clear条件闭包与[G03](invalidation-submit-g03-0041-20261023.md)提交/内嵌记录/直接消费闭包已整合，分别待A22/G04独立复核。

新增[H03](weather-page-close-h03-0041-20261023.md)：真实确认键离页→父/子DELETE→递归控件与类析构的条件闭包，已整合2ac1fd0待H04独立复核；116B ctx最终释放仍为精确断边，未作缺陷判断。

新增：[A22](png-info-review-a22-0041-20261023.md)限定接受A21并明确class0公共cache元数据读取边界；[G04](invalidation-submit-review-g04-0041-20261023.md)对G03两处事件表达纠正后限定接受，filter仅清bit15及bit0按位置不同返回须以G04为准。[D05](uart-ring-drain-d05-0041-20261023.md)真实IRQ/条件DMA闭包与[F05](miio-exit-callback-f05-0041-20261023.md)显示DELETE/后端清理闭包已整合待独立复核，不认证硬件交付或完整MiIO退出。

新增：[H04](weather-page-close-review-h04-0041-20261023.md)限定接受H03实际离页/DELETE合同，无核心纠正但ctx最终free仍未证；[F06](display-exit-review-f06-0041-20261023.md)纠正F05通用filter掩码为仅清bit15后限定接受，实际filter29闭包不变。[E05](ctk-app-close-e05-0041-20261023.md)是局部构造/DELETE合同与目标订阅注销精确断边，待E06，未认证完整app退出归还。

新增验收：[E06](ctk-app-close-review-e06-0041-20261023.md)限定接受E05局部DELETE/持有与有界注销断边，不认证完整退出；[D06](uart-ring-review-d06-0041-20261023.md)纠正D05 type>1计数发布次数、补DMA IRQ trampoline/pair实参后限定接受，相关替换段以D06为准。[A23](png-session-lifecycle-a23-0041-20261023.md)与[G05](display-event-flow-g05-0041-20261023.md)恢复成果已整合待A24/G06；硬件、cache驱逐、所有动态handler及完整资源归还仍未闭合。

新增整合（复用分类）：A25默认raw/free/align绑定待A26独立复核；D08限定接受D07；G06三处精度纠正后限定接受G05；H06限定接受H05显式ABI/free，旧注册身份不算新增；F08纠正F07 array前缀尺寸/enum packing表述，ROM来源未知；E07只补调用边界，item+34/+38消费仍未恢复。各项链接与精确断边见管理对照，不重复旧功能账。
