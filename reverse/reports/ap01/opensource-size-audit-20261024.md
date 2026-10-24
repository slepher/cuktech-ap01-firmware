# ROM 开源来源与规模核查（2026-10-24）

本文的 diff、目录规模及文件位置统计为同日清理前快照。随后按用户要求将生成物移出仓库并改写本地历史；当前保留内容与旧路径解释见[清理结果](repository-cleanup-20261024.md)和[归档规则](../../analysis/README.md)。ROM 体积测量与开源来源结论不因仓库清理改变。

结论：约 37 万行 diff 主要是逆向证据的逐指令 JSON，不代表充电站业务源码规模。原厂 ROM 确实集成多个公共组件；仓库也收录了明确的第三方 SDK 参考源码。原厂完整源码与精确构建版本尚未取得，不能从 ROM 或导出行数还原原项目总行数。

机器记录、ROM 字符串偏移、克隆提交、SDK 逐文件校对结果见 [opensource-audit-20261024.json](../../analysis/opensource-audit-20261024.json)。本轮只读 ROM、复用既有静态证据并克隆参考源码，没有执行固件或连接设备。

## 1. 这次 diff 到底是什么

固定比较：本地 `origin/master` = `ab9716ee8bc2c8408529893a5fdaa0354718c299`，HEAD = `32f9c9e0e0d4ebd1a72633a19a6f711aab28cb6d`。没有 fetch；此处不代表远端此刻最新状态。统计不含工作区原有未提交修改和本报告。

| 目录 | 变化文件 | 新增行 | 删除行 |
| --- | ---: | ---: | ---: |
| reverse/analysis | 418 | 354,610 | 0 |
| reverse/reports | 176 | 15,958 | 29 |
| 合计 | 594 | 370,568 | 29 |

新增行的 95.7% 是分析导出。最大新增文件 `weather-icon-review-a20-0041-20261023/instruction-review.json` 有 15,474 行；其结构对每条短指令重复保存地址、ROM 偏移、机器码、助记符和 raw_fields。一条机器指令可展开成十余行 JSON。多个专项还会为交叉复核保存重叠窗口，不能按导出行数累加业务量。

当前整个 Git 跟踪树中，`reverse/analysis` 约 184 万文本行；`tooling/firmware-modules` 约 10,065 行（含头文件、测试、数据及说明），`tooling/scripts` 约 32,339 行。这也都不是原厂源码行数。366,737 行的首轮全 ROM 总账本已经在比较基线中，不属于此次新增。

## 2. 第三方代码是否收进了本仓库

是。`reverse/sdk/` 共 15 文件、1,599,520 B、27,279 行，全部与同级 `bouffalo_sdk` 的对应文件在统一 CRLF/LF 后一致。其参考提交为 `41bf338a57be53919d99f6c6715a96100428c97d`。这是直接源码副本，不能算作本项目独立实现的业务量；这些文件也不在上述 37 万行 diff 中。

还存在用于来源对照的少量上游源码摘录，例如 A13 的 `source-evidence.json` 保存五个 NuttX 参考文件共 269 行；不宜笼统声称分析目录完全没有上游源码。主体仍是研究证据与反汇编。

`NOTICE.md` 已声明 SDK 等第三方来源，但将 Bouffalo SDK 一概写成 Apache-2.0 不够精确：例如 `sdk-bl616_clock.c` 自带的是三条款 BSD 风格声明；应按具体文件原始头部核对。此轮记录问题，没有代替所有文件做许可认证。

## 3. ROM 的实际字节规模

0041 固定 SHA256：`972db4c136c7ed9e24a83c07c1a7fd62040ca018b08ca285216d26b1fee3c6b9`。

| 内容 | 实测/既有模型规模 | 占 ROM |
| --- | ---: | ---: |
| 完整更新镜像 | 6,769,704 B / 6.46 MiB | 100% |
| PNG，199 个 | 689,182 B / 0.66 MiB | 10.2% |
| GIF，11 个 | 3,434,444 B / 3.28 MiB | 50.7% |
| 图像合计 | 4,123,626 B / 3.93 MiB | 60.9% |
| 首轮模型识别函数体并集 | 1,730,593 B / 1.65 MiB | 25.6% |
| 底座三份 MCU 载荷（含头部） | 141,878 B / 138.6 KiB | 2.1% |
| 按上述区间并集去重后的剩余空间 | 773,625 B / 0.74 MiB | 11.4% |

PNG/GIF 依既有清单逐项重读 ROM 并核 SHA256，区间去重后与函数体并集无重叠。三个 MCU 载荷（含头部）的 SHA256 也已重核。历史模型的三个短函数体与 MCU 载荷有合计 18 B 重叠，证明枚举结果包含可疑识别，不能等同真实 AP01 程序；上表剩余量已扣除这种重复计数。剩余空间可能包含字体、字符串、表、填充及漏识别代码，不能全部称为资源或未逆向代码。55 项字体 wrapper 已有记录，但不是全部字体的去重字节统计。

函数体并集来自首轮模型 6,487 节点（含一个外部边界），不是全部真实函数数或严格代码段大小。图像之外的 2.65 MB 也不能全算代码。详见 [首轮范围与限制](whole-rom-0041.md)。

## 4. 模块规模：可观测锚点与估算分别记账

首轮通过诊断路径关联到的函数：

| 模块候选 | 直接关联函数 | 对应函数体并集 |
| --- | ---: | ---: |
| 定制 UI、页面、主题与工厂滑动器 | 98 | 91,854 B |
| PogoPinMng 下的底座、天气、设备业务 | 61 | 39,690 B |
| SystemSettings | 3 | 530 B |
| miio_sdk/miio_instance/client/miio_client.c | 1 | 4,096 B |

这些是**局部关联锚点，不是模块总量或严格下界**：同一个初始化函数会引用多个路径，跨组可能重叠，函数边界也有模型误差；没有日志路径的函数无法在此归组。特别是 530 B 的设置关联绝不意味着整个设置系统只有 530 B。全部 293 个私有/混合候选之外仍有 5,396 个来源未决函数，不能将它们都归为私有业务，也不能全部排除为开源。

若目的是规划将充电站专用逻辑恢复为可维护 C/C++，可暂用下表作为**低置信度工作量级假设**。区间依据已知功能、至少 30 条厂商应用路径、UI 17 个功能家族和局部机器码锚点；没有从机器码做固定比例的源码行数换算。排除公共库、自动生成资源、测试与逆向导出，行数约指人工业务实现，精确恢复原版可能超出这些区间。

| 私有模块 | 暂估人工实现行数 | 主要复杂点 |
| --- | ---: | --- |
| 页面、主题、窗口、动画、旋钮交互 | 8,000–20,000 | 页面生命周期、切屏、历史曲线、资源引用 |
| 底座 UART/USB、命令队列与 MCU OTA | 3,000–8,000 | 帧、重试、回调、升级状态机 |
| 功率/模式/端口状态、UiIFace 发布订阅 | 2,000–5,000 | 对象所有权、模式参数和多消费者 |
| 米家业务适配，不含 MiIO/MiBLE SDK | 2,000–6,000 | 属性分发、延后提交和绑定状态 |
| 天气请求与日历业务，不含通用库 | 1,000–4,000 | 缓存、调度、位置、数据转换 |
| 设置持久化、蜂鸣背光、工厂测试 | 1,000–4,000 | 持久化兼容、线程与外设控制 |
| AP01 自身 OTA 与启动适配 | 1,000–4,000 | 镜像、分区、校验与恢复合同 |
| 上述应用逻辑合计 | 18,000–51,000 | 规划时取约 2–6 万行量级 |

这不包括无线驱动、私有 SDK、底座 MCU 内部程序；其源码规模暂无法估计。若要求从零实现所有操作系统、图形、TLS、蓝牙和驱动，整体会远大于专用应用层；当前没有证据支持需要把这些公共组件逐行重新逆向。恢复难度更多由异步所有权、间接调用、厂商改动和硬件行为决定，不能按输出文档行数衡量进度。

## 5. 已准备的同父目录源码

目录统一位于 `D:/Documents/PlatformIO/Projects/`。本轮新增 13 个浅克隆（depth=1），已检出源码且跟踪文件状态干净；没有初始化子模块或构建依赖。完整提交号、origin 和状态存于机器记录。

| 本地目录 | 上游 | 使用依据/限制 |
| --- | --- | --- |
| nuttx | [apache/nuttx](https://github.com/apache/nuttx) | nuttx-12.10.0；沿用既有对照版本，不认证原厂版本 |
| nuttx-apps | [apache/nuttx-apps](https://github.com/apache/nuttx-apps) | nuttx-12.10.0；配套应用/组件集成参考 |
| lvgl | [lvgl/lvgl](https://github.com/lvgl/lvgl) | v9.2.1；包含原 ROM 指出的 NuttX libuv/cache 路径；不认证原厂版本 |
| libuv | [libuv/libuv](https://github.com/libuv/libuv) | 官方默认分支快照；该检出没有 src/unix/nuttx.c |
| libuv-openvela | [open-vela/apps_system_libuv](https://github.com/open-vela/apps_system_libuv) | 存在 src/unix/nuttx.c；补充 NuttX 移植候选，未认证原厂 fork |
| littlefs | [littlefs-project/littlefs](https://github.com/littlefs-project/littlefs) | ROM 有 littlefs/littlefs/lfs.c |
| tlsf | [mattconte/tlsf](https://github.com/mattconte/tlsf) | ROM 有 tlsf/tlsf/tlsf.c；具体 fork 未定 |
| mbedtls | [Mbed-TLS/mbedtls](https://github.com/Mbed-TLS/mbedtls) | ROM 有多个 mbedtls 调用失败日志；版本与适配未定 |
| zephyr | [zephyrproject-rtos/zephyr](https://github.com/zephyrproject-rtos/zephyr) | Bluetooth host 路径及初始化字符串；不代表整机采用 Zephyr 内核 |
| lodepng | [lvandeve/lodepng](https://github.com/lvandeve/lodepng) | ROM 有 LVGL lodepng 路径及专用错误文本 |
| gifdec | [lecram/gifdec](https://github.com/lecram/gifdec) | ROM 有 LVGL gifdec.c；LVGL 版本包含适配，独立上游仅供对照 |
| cJSON | [DaveGamble/cJSON](https://github.com/DaveGamble/cJSON) | 仅接口/类型形状候选；尚未确认原 ROM 精确来源 |
| ArduinoJson | [bblanchon/ArduinoJson](https://github.com/bblanchon/ArduinoJson) | 我方实验载荷 native_json_0041.h 显式依赖；不据此归入原厂 ROM |

已有并保留原状：`bouffalo_sdk`、`cuktech-ap01-firmware-tools`、`cuktech-screen-controller`。后两个项目是参考研究项目，不是已证实编进原厂 ROM 的公共库。

0031 与 0041 均直接检查了上述主要组件字符串，偏移分别保存。`NuttX/6.xx.x` 是通用 HTTP User-Agent 字符串，不能据此判定实际 NuttX 为 6.x。官方参考版本、SIM 构建版本和原厂版本三者不能混用。

ROM 还含 `RWNX + LwIP driver`、`bl6_wpa_supplicant` 与 `fatfs/fatfs_vfs.c` 线索，仅凭这些不能确认实际独立引入的 lwIP/hostap/FatFs 上游及版本，本轮没有把它们认证为未修改开源实现。zlib 错误文本来自 LodePNG 的可能性明确，不能再凭该字符串重复计算一个独立 zlib 组件。

## 6. 后续校对的优先级

先复用公共系统/图形组件源码，定位 ROM 使用的版本和厂商适配差异；重点人工恢复 PogoPinMng、页面生命周期、状态发布订阅、MiIO 业务胶水和更新合同。图像以原件提取与哈希复用，避免当成业务源码处理；三个 MCU 载荷单独建账。当前源码对照不认证任何整库无修改，不改变已有逆向完成率。
