# G08：G07 替代38 poll 增量的独立复核

研究基线 `a825ac8`；复核于 2026-10-24，沿用派发文件日期。结论：**限定接受 G07，未发现需要纠正的语义；新增功能 0，新增开源排除 0**。只复核其 state/poll 对象别名、adapter→stop→刷新→清 pending 原序及 owner 计数归还。没有将本次复核另记为功能恢复，也没有证明整个显示或 libuv 生命周期完成。

## 继承的旧结论：已有成果→实际复核缺口

|既有出处 / 证据类型|已解释的行为|局限 / 本轮复核缺口|
|---|---|---|
|[G07](display-alternate-work-g07-0041-20261023.md) 及其 `reuse-crosscheck.json`；旧 complete、矩阵、最终 SIM 验收和 ZIP 有界检索|SIM 显示重建与服务替代已有成果；G07 已核 20 个旧文本及 39 个 ZIP 文本成员。近期 initializer 留存实际已有 caller、notify、退出登记|直接继承复用对照，不重做检索或导出；无命中仅是该集合的文本结果。SIM 验收不能认证 ROM ABI、驱动或来源|
|factory-test `retained-initializer.json`，Evidence `ev_dc0e38b0f382799ea2a8e8ad7f21cefc5998b0767ecf38a58cfdebe8add167c3`|state 分配、notify 安装、调用 a008335e、两个 poll 和 timer 的关闭登记已有原 raw|这些不是 G07/G08 首次发现；本轮不重新分析 initializer 大函数、不认证其旧反编译 custom0/unaff|
|[G05](display-event-flow-g05-0041-20261023.md)、[G06](display-event-review-g06-0041-20261023.md)，原指令及独立复核|filter38 user=state+58、pending byte 去重、user+8 传给 start、a00806d0 刷新默认 display 后清 pending|继承安装与业务消费；仅重读必要调用/写入锚点确认与 G07 对象合同一致|
|[C03](pogo-close-callback-c03-0041-20261023.md)/[C04](pogo-close-review-c04-0041-20261023.md)、[C05](pogo-close-dispatch-c05-0041-20261023.md)/[C06](pogo-close-dispatch-review-c06-0041-20261023.md)、[F03](miio-loop-close-f03-0041-20261023.md)/[F04](miio-loop-close-review-f04-0041-20261023.md)|poll 实参、close 保存 callback、type8 停止及共用完成尾部传回原 handle 已有合同|不重做共用关闭器，不把 Pogo owner+198 套作本 state+180；仅核 G07 的本 owner callback|
|G07 九个局部窗口，原字节/指令|state fd、poll/watch 内嵌关系、start/adapter/stop、a007ff54 已给出行为合同|仅核 ABI、保存对象、宽度符号和原序；后端 ready→间接调用及退出后 drain 不在复核闭包内|

旧路径不用于判缺；直接采用当前留存文件与其 Evidence。没有重做 SIM、分类、资源或来源认证。上述旧结论均继承，以下原字节读取均为**旧结论复核**。

## 本轮复核或纠正

|检查项|结论|原指令依据及范围|
|---|---|---|
|入口与 fd 身份|接受|a0083376/337a 从参数0取 loop/display；342e 在 getter 前保存 a1=state；3434/3436 从返回对象首 word 读入并写 state+58。只在普通前置条件成立路径论 ABI，不假定断言必不返回|
|state+58 与 state+60 不同对象|接受|G05 a00834a4 把 state 写入 poll 首 word；34da 构造 user=state+58；a0080718 加8得到 state+60。故 user 前缀不是 poll 本体，也不是额外分配的 holder|
|poll 内 watcher 指针与 callback|接受|a009e50e 是 s4=a1+34；补核 e524/e526/e528 三条 mov，将 s3/s2/s5 分别绑定 loop/fd/poll；随后 G07 e604 写 loop、e62c 以 s4 调 watcher init。e614/e628 构造 a009f8ea；cd86/cd88 写 watcher callback/fd。无需重导初始化整函数；周边厂商字不用于推断其算法|
|start 参数、发布顺序和返回|接受|a009f9da 保存 callback；f9e2 先 stop，f9e6 重载保存的 events，f9fe 登记 backend，fa1c 才写 poll+30 callback。输入2映射为 backend mask4；正常返回0，G05 caller 未消费返回值。没有推导必然 ready|
|adapter ABI|接受|a009f8fe 以 watcher-34 得 poll；f964 从 watcher-4 取 callback，f96a/f96c/f96e 以 `(poll,0,mapped_events)` 调用。已列状态分支的 `(poll,-9,0)` 也与 retained 原指令一致，但未作输入构造或执行|
|stop、刷新、pending 原序|接受|G05 a00806da 先保存 poll 首 word owner；06dc/e0 的 AUIPC/JALR 目标是 a01b2cb0，正常分支再转 a009f972；后者先取消 watcher mask17、清 active、必要时减 loop 计数并调用 a009e212。06e4/e6 再以 NULL 调 a00e0ac8，06ea 最后 byte 清 state+5c。注册 display 与默认 display 运行时同一性未证明|
|owner 计数归还|接受|a007ff5e 从原 handle 首 word 取 owner；ff60/ff64/ff66 为 32 位读、减一、写 owner+180；ff6a 是 `blt zero,a5,+2c`，即有符号减后>0才跳过释放；否则 ff90 将同一 owner 传 ff92→a008ab8a。不能改成仅零才释放，也不能据此声称全部计数写者/恰好一次已证明|

没有技术语义纠正。补充三个初始化寄存器别名锚点只提高 G07 指针证明的可定位性，不计新增恢复。继承窗口中 stop wrapper 的断言分支不被当作已认证 no-return；结论限定正常路径，未拓展异常输入研究。

## 本轮真正新增

独立技术复核及可重跑的局部字段检查。**新增 ROM 功能为 0**；G07 的身份、adapter/stop 和本 owner callback 合同仍归 G07，factory initializer/notify/关闭登记及 G05/G06 合同仍归旧成果。

静态执行 [review.py](../../analysis/display-alternate-review-g08-0041-20261023/review.py)，G07 留存的 215 条指令 raw 全部与原 ROM 对应位置一致；共 266 项检查通过（215 条连续位置检查、51 项编码字段/目标/锚点检查）。I/S/J/B 与 AUIPC/JALR 由脚本按编码字段独立拆解，不仅复用旧 asm 文本。结果见 [review-result.json](../../analysis/display-alternate-review-g08-0041-20261023/review-result.json)。没有第二份整函数/指令导出、完整资源提取、源码复制或哈希账。

## 仍未闭合的精确边

- a009ec98 的登记到真实 ready 后 watcher+0 间接调用的后端消费链未核；接受 adapter 本身不等于接受其必达。
- 退出登记之后 loop 是否继续 drain、所有 owner+180 写者及 callback 恰好一次未核；共用 close walker 合同不能独自补这些时序边。
- NULL 刷新的默认 display 与注册 display 是否始终相同、另一 poll 的 filter42 业务、物理 flush 及确切来源版本未核。

不为这些未核项扩扫整个后端/libuv；下一任务如有必要，应由管理者另设精确 ready 消费接点。未启动 SIM、构建、历史回放、固件或设备，未连接外部服务；未修改生产代码、ROM、配置、分析器模型或共享索引。
