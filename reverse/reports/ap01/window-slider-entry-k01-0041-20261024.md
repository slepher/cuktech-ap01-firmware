# K01：window-slider 动作入口的部分静态接入

2026-10-24；基线 `bd7b344`，分支 `codex/re-0041-k01`。用户要求快速结束，立即停止扩展，按**部分恢复、待技术复核**交付。已取得a00a4cac入口普通指令与三callee旧body，能够记录事件型分流及索引接入；未完成独立原字字段验证或完整对象/注册身份闭包。不宣称首次发现该组件或完整功能已恢复，不创建后继任务。

使用 [reverse-engineer-anything skill](C:/Users/cogic/.agents/skills/reverse-engineer-anything/SKILL.md)。原件只读，无共享REA target、固件/SIM/模型/构建/回放/设备/网络或下级agent；未改主树、其他任务、生产ROM/代码/配置/模型。快速收尾指令后不再取证或展开callee。

## 继承结论：已有→行为→局限→缺口

|已有出处|已知行为/定位|本轮处理|
|---|---|---|
|whole-ROM round1 a00a4cac extent `ev_a516b7ee45ef6385470a3f9afec6e7f7ae97bf725d4ac4ada41f51eac0352150`、calls `ev_bc62d24f75109fd94a41f3bebcf02277e33f5fa6c2ee47c2149d8f3cab8cdc2a`|198B入口及三callee关系早已有；不是未知地址发现|入口语义/参数/门仍需核，未把清单当合同|
|旧whole-rom-private-20261023-036/043/047.json的structuredContent|a00a4116读对象+38；a00a491c调用a00dd144，汇编保留其a0返回；a00a4aa0为按索引选择、更新+38/+3c并按方向安排位置/动画的旧body|直接复用原完整留存，不重新导出三body。043伪码void不能覆盖其汇编a0返回；不展开完整动画|
|J04交叉筛选；[multi-screen-app-host](multi-screen-app-host-0041.md:79)|factory_ui/lv_window_slider.c与日常lv_power_ui/lv_ui_window.c不同，后者以a00b2ff4/a00b3106等为核心|继承组件区分，不套H07/guide/日常窗口合同，也不从目录名绑定GPIO FactoryTestMode|

已有rehost JSON及最终源码ZIP按精确地址/组件词项未取得本caller完整body；此为有界查询，不证明历史从未分析。三份旧callee的地址、Evidence ID与绝对载体保存在 [evidence.json](../../analysis/window-slider-entry-k01-0041-20261024/evidence.json)，不重复拷贝整body。

## 本轮复核或纠正

原入口解码显示：incoming a1保存为E，a0被常量a03725cc覆盖后调用a00d81f8；仅其返回精确1才继续。E+0取得对象O，E+8取得code，按原指令与0xffff7fff做AND后比较0x31/0x11。尚未独立认证a00d81f8和E的正式类型/全部ABI，因此只用地址/偏移，不给常量或首参预设class身份。

三callee已有body明确对象+38与索引有关，和日常组件的+34不同；本轮未改变旧callee语义。a00a491c旧反编译声明void，但其普通尾声在a00dd144后只恢复寄存器并ret，入口caller实际消费a0；这是需保留的返回ABI限制，不新增计数算法恢复。

## 真正新增的部分接入记录

下列是已取得入口指令支持、尚待独立字段/控制流复核的局部表达，不是原源码或完整运行合同：

- code=0x31：以O调a00a4116，返回值作为a1；a2=0、a0=O调用a00a4aa0。不预设该事件名称，也不把“请求当前索引”说成必有可见动作。
- code=0x11：以E调a00d8af6，比较返回19/20/10。返回19时，a00a4116(O)的结果按signed >0决定减1，非正则取a00a491c(O)后减1，再以a2=2接a00a4aa0。返回20时先当前值+1，和count做unsigned比较，小于count保留，否则置0，以a2=1接同callee。只解释正常非空组件路径，不新增空count安全门。
- 返回10：O+38非零时以目标0/方向0接同callee；等于0时以O调用a00ded6c，随后SW清全局62fcb6b0。只证实对象实参与清槽顺序，未认证该global的所有权或上层关闭生命周期，不能关联GPIO stop/close或根析构。

本入口没有已观察的新分配或直接free；其索引状态写入/动画责任沿旧a00a4aa0留存，删除责任的完整下层不展开。不得将静态分支存在表述为实际键序列、界面可见切换或资源释放已观测。

原件读取映射VA−0x9ffff000，已取得入口解码中选留15个必要锚点；完整198B caller不另导出。上述接入是本轮部分解释增量，旧地址、三callee和组件区分不计新功能；没有完成的新增功能闭包，不作整slider/GUI完成宣称。

## 精确未闭与交付检查

未闭：a00d81f8返回1的正式语义；事件布局/0x31/0x11及key helper正式ABI；a03725cc与实际installed callback的绑定；正常count/索引前置条件；62fcb6b0的对象身份/所有权与正常上层触发。关键signed/unsigned门、mask和直接目标尚待独立原字字段验证。快速收尾后不再追这些边，不派发后继。

事实为已有callee留存及本轮取得的普通入口解码；事件/导航职责为局部解释，实际产品关联与执行未知。无SIM/照片替代证据用于认证此组件。交付只做JSON解析与diff/路径检查，不冒称语义测试、独立验收或运行验证。
