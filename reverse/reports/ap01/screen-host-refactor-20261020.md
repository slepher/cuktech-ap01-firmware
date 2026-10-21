# 0041 多屏宿主代码重构交付记录

日期：2026-10-20。后续已补充[第二应用与窗口热重建](screen-host-lifecycle-20261020.md)，本文件保留首轮候选05的验收边界。两个仓库均已落地代码；本次仅离线构建和验证，未刷机、未访问设备、未部署Bridge。候选与已部署34分开保存，ABI v1仍为实验接口。

## 代码归属

`cuktech-ap01-firmware/tooling/firmware-modules` 现在持有纯C宿主状态机、0041原厂窗口/LVGL绑定，以及从应用仓库提取的socket/任务、VFS、独立维护/槽位、镜像检查、运行库与XIP链接脚本。维护核心不包含Ap01Business、Ap01Application或C2业务协议头。

`codex_status/ports/ap01/native_0041.cpp` 保留应用装配、配对/鉴权、业务执行器和显示队列，使用共享宿主API，不再包含ROM地址或win字段偏移。旧平台头保留薄兼容引用，旧实现移入本仓库；业务、Bundle、单active context与I4渲染继续使用现有实现。构建工具从同父目录的本仓库取共享源码，提供隔离输出参数。

每应用提供有界槽位数组，逻辑screen-set按稳定ID原子替换。同ID保留物理root，逻辑重排不动原厂0..8或已分配root。codex_status声明容量8；共享核心可同时接入多个应用，纯核心测试使用两应用九root。当前完整候选只装配codex_status，第二个真实业务应用尚未接入。

## 调度与生命周期

- 每应用50ms轮询持续消费present/retire，隐藏页也确认Bundle退役；不按八个页面重复执行。
- UI只入队激活请求。现有业务线程执行localActivate/redraw，帧携带切换token，取消/超时的迟到帧丢弃；没有新增线程。10秒准备期限包含前方最长5秒HTTP请求，超时保持源快照并请求业务回滚。
- 源与目标有独立图像descriptor和像素，原厂动画idle后退役源图。真实draw才发displayed，数据ACK、图像提交和entered均不替代draw。
- 页面集更新只作用于所属应用；原厂页发布不抢焦点，原页面稳定ID及输入修订号决定是否自动恢复。配对/维护阻止新切换并取消未完成准备。
- root删除后拒收帧、解除定时器并保留维护/发现执行器。整窗口热重建与执行器复用尚未证明，不能宣称热卸载完成。

## 离线验证

原件追加机制检查：9/10/17孩子、24次双向滑动/ready、tag查找和早期初始化索引行为，见[追加验证](screen-host-append-validation-20261020.md)。实际root分配和I4绘制使用下述完整候选执行，区别于机制检查中的合成对象。

| 检查 | 结果与范围 |
| --- | --- |
| 共享宿主ASan/UBSan | 通过：两应用九root、稳定ID/重排、容量/版本/重复拒绝、隐藏poll、失败/超时/迟到prepare、焦点锁/逃生、跨应用更新/退役、全局阻止和销毁句柄 |
| RV32编译/链接 | 通过：无未解析符号，无可写静态/TLS/构造器段；原厂资源及允许补丁范围由打包器核对 |
| 原生业务与维护ASan/UBSan | 通过：八页业务重排/激活/删除、Bundle重放、真实确认输入模型、维护鉴权/OTA/未知结果/槽位回切等；Flash使用fake callbacks，不证明原厂Flash ABI |
| 完整候选八页原生QEMU | 分组通过：05通过完整正反向导航及Bundle重排/删除/单页替换/原厂页不抢焦点，随后达到墙钟上限，总passed仍为false；06使用同一候选完成独立探针，总passed=true：实际不同root为child9–16，Pet7↔八root↔Settings6双向通过，激活重放通过，native_execution_clean=true |
| 像素 | codex、weekly-only、zero、full均有一张实际活动LVGL帧缓冲与共享渲染输出逐像素零差异；replace-reorder两个缓冲均零差异 |

QEMU显式建模BootROM、MAC、输入、fbdev就绪和厂商动画指令，socket限制为合成业务输入。帧缓冲验证不等于物理LCD/SPI完成，也不证明真实无线、掉电或整机长期运行。34份编译源码及254份输入头文件与候选审计哈希逐一一致，精简验收回执见[机器可读证据](../../analysis/screen-host-refactor-20261020.json)。

## 产物与资源

本地隔离目录：`codex_status/artifacts/ap01-screen-host-20261020/`（不入库）。

- 完整候选：`ap01-screen-host-candidate-05.bin`，7,002,648 B，SHA256 `fb3e25d3804667bd9f7984874b9b1cfe9507f52abce8e090d73e68e9b4ccc912`。
- ELF：501,944 B，SHA256 `07dc1c32c92ebde093a4040d78cd6608cb0399fb098ddbbefe5057048c1410b8`。
- 原件SHA256：`972db4c136c7ed9e24a83c07c1a7fd62040ca018b08ca285216d26b1fee3c6b9`。只替换已有8字节UI挂钩和2字节无签名OTA分支，追加XIP载荷；GIF/ROMFS/传统OTA入口保留。
- RV32 Runtime2232 B（原34为2088 B），含Business1776 B；八槽124×8=992 B，八页tag+surface64×8=512 B，合计Runtime与这两数组3736 B，另计allocator、LVGL对象、Application及其他既有状态。
- 队列Frame152 B，Activation8 B，均另计allocator；latest-only队列分别最多一项待处理及一项处理中，不按输入数量增长。
- 每个I4图像38464 B（38400像素+64调色板）；通常稳定一帧，滑动至少两帧，另有渲染/拷贝与生产队列瞬态，不把两帧下界当完整堆峰值。没有八份常驻全帧。
- 编译器静态栈帧：screen-set替换336 B、UI processFrames384 B、I4提交80 B；不等于完整调用链高水位。真机堆/栈峰值尚未量测。

两份原生报告使用相同镜像SHA256，机器回执的 `native_split_acceptance_passed=true` 仅代表上述两组断言合并通过；05超时未被改成整体成功，06为正常完成。06提前正常结束、未跑满CPU安全窗口，因此其 `cpu_safety_passed=false` 不代表原生异常；完整持久恢复/OTA放行字段仍为false。

候选manifest仍标记不可刷/未实机验证；原生OTA、同NOR重启、热重建、第二应用真实LVGL集成、真实分配失败注入和物理高水位属于后续验收，不能继承34证据。本次不执行P6部署。

接口以[当前合同](screen-host-interface-0041.md)和C头文件为准；实施前分期保留在[计划](multi-screen-app-host-implementation-plan-20261020.md)。
