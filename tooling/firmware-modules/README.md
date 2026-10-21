# AP01 固件模块

## 0041 共享屏幕宿主与平台代码

`screen_host_0041.h/.c` 是不依赖LVGL/ROM地址的宿主核心：调用方提供实际容量的root槽位和应用清单，每应用按稳定screen ID替换屏幕集，支持异步进入准备、双向导航、焦点锁/3秒逃生和隐藏态UI轮询。物理root不删除或重排；逻辑顺序与物理索引分开。只读 `ap01_host_api` 和 `ap01_lvgl_0041` 提供版本与结构长度。

`screen_port_0041.h/.cpp` 绑定精确0041的原厂窗口、普通页面、标签、定时器和LVGL/I4图像；为每页保留独立root/descriptor，图像帧按需分配，离开动画完成才退役源帧。实际draw回调与切入完成分开。普通控件在 `prepare` 中按需创建，`unbind` 清理逻辑页面资源；物理窗口整体由mount/unmount管理。动画期间依赖原厂idle标志，不用300ms固定延迟替代完成。

窗口DELETE期间通过 `ap01_window_detach` 解除本窗口的原厂通知订阅，保留50ms定时器/context作为生命周期锚点；回调必须在缺窗时检查ready。下一次挂钩用 `ap01_window_find` 复用原Runtime/服务，仅重建UI资源。该操作在UI线程、旧对象仍处于DELETE回调时执行。完整对象删除使用原厂公共入口；打包器另装配NULL定时器删除保护，非NULL沿原件尾部执行。验证和补丁范围见[共存与热重建](../../reverse/reports/ap01/screen-host-lifecycle-20261020.md)。

`test_screen_peer_0041.*` 是独立的两页离线应用，仅 `codex_status/tools/check-ap01-native.py --screen-host-probe` 装配；普通候选不含测试入口。它验证自有图像/输入锁/隐藏轮询与codex_status八模板共存，不新增业务HTTP或维护执行器。

从 `codex_status/ports/ap01` 提取的平台实现：

| 模块 | 职责 |
| --- | --- |
| `native_io_0041.*` | 时钟、任务、socket、Flash叶调用、原厂入口识别 |
| `native_diagnostic_0041.*` | 维护鉴权后的独立状态、原厂文件/ramlog和物理Flash只读导出；单块1024 B及CRC |
| `native_vfs_0041.*`、`native_filesystem_0041.h` | 原厂LittleFS/VFS绑定与调用方持有的文件对象 |
| `native_firmware_0041.*`、`native_slot_0041.*` | 独立维护事务、恢复/槽位与原厂分区读写绑定 |
| `native_ota_image_0041.*` | 0041原生维护使用的镜像准入/完整性检查；与0031模块分别构建 |
| `native_runtime_0041.cpp`、`native_string_0041.h`、`native_calendar_0041.cpp` | freestanding运行库、原生String兼容层、UTC+8日历 |
| `native_http_0041.h`、`native_json_0041.h`、`native_integrity_0041.h` | 业务无关的HTTP值类型、请求局部分配器与完整性工具声明 |
| `native_application_0041.ld` | XIP布局、原厂运行库导入及禁止可写静态/TLS/构造器的链接约束 |

维护模块依赖调用方提供的ArduinoJson头文件和已有 `syncSha256` 字节工具，不依赖 `Ap01Business` / `Ap01Application` / C2协议头。维护鉴权调度仍由调用方接入，只启动一个维护执行器。`codex_status` 保留绑定、Bundle、共享渲染与业务HTTP，并通过兼容头引用这里的实现。平台函数地址不能混用于0031。

纯宿主检查（Linux现有C编译器，产物目录须已授权）：

```sh
cc -std=c11 -Wall -Wextra -Werror -fsanitize=address,undefined \
  tooling/firmware-modules/screen_host_0041.c \
  tooling/firmware-modules/test_screen_host_0041.c -o /tmp/ap01-screen-host-check
/tmp/ap01-screen-host-check
```

检查覆盖两应用九root、稳定ID/重排、事务拒绝、隐藏/退役、进入超时、焦点锁、跨应用更新和逃生。原生业务构建从同父目录 `codex_status` 的 `tools/check-ap01-native.py --out <隔离目录>`、`tools/link-ap01-native.py --out <同目录>` 接入；完整ROM候选仍须单独验证，不自动成为可刷产物。

## 0031 独立整包 OTA（2026-10-18）

`ota_channel.c/.h` 提供有界 HTTP 接收、认证、传输 CRC 和事务回调；`ota_0031.c` 绑定原厂非活动槽写入、读回校验、提交及复位；`ota_image.c/.h` 按每次请求的实际长度检查已支持的 AP01 0031 原始包格式、板型参数、型号、包头/尾部校验和 7 MiB 容量。接收端不要求来包包含固定位置的 OTA 模块、固定任务入口或启动脚本文本。参考板型头直接由固定原件嵌入只读区，不从离线分析地址读取运行时包头。Flash 缓冲区显式按字对齐，成功写入句柄只关闭一次，提交后即使回复丢失也会重启；电脑端的未知结果不得自动重发。

构建入口为 `../scripts/build-ota-channel-0031.sh <prefix> <既有输出目录> <模块运行地址> <服务版本>` 与 `../scripts/build-ota-expanded-0031.py`。扩容模块放在文件偏移 `0x67e000`，保留原版所有显示资源；链接禁止可写静态状态。完整审查、兼容过渡和测试结果见 [扩容与升级记录](../../reverse/reports/ap01/ota-expansion-0031-20261018.md)。这套实现更新完整系统包，与下文的维护事务核心及 App-only 更新不同。

历史 bridge/tail 实验包会把 `miIO.ota` 静态改为 busy，这不满足保留传统 OTA 的要求，不作为当前可部署方案。真实扩容启动尚未通过验证，不能把模拟更新成功当作可发布结论。当前统一服务候选使用 `--mode http`，保留传统 OTA 入口。按用户指定方式人工顺序执行两种 OTA，跨通道共享锁不作为部署前提；并发写入未验证。

## 0031 独立网络诊断

用户授权的临时 GIF 诊断版已实机启动，使用 `build-ota-expanded-0031.py --mode gif-http`：与原版同长度，沿用 GIF 内原位置入口，保留传统 OTA，暂时替换猫 GIF。STATUS 已增加控制器原始映射偏移、两张物理分区表和原厂复位原因。实机采集与读取视图限制见[安装记录](../../reverse/reports/ap01/knowledge/0031-gif-diagnostic-install.md)。`build-ram-diagnostics-0031.*` 是未部署的离线实验，不是本次安装包。

`ota_0031.c` 在 18080 接收 HTTP，每个连接由独立的 NuttX TASK 处理，监听任务不等待上传完成。最多四个活动请求任务，每个栈 16 KiB；每次创建显式复制父任务环境，避免丢失 `ro.boot.update_slot`。任务只从监听器克隆描述符，上传的 Flash 句柄不会进入其他请求或诊断 shell。独立上传事务在调度锁下竞争同一个 fence。

`GET /logs` 返回认证后的 RAM JSONL 快照；`GET /diagnostic` 经 Bearer 认证和 `Upgrade: ap01-diag/1` 后提供原生 NSH、状态、同一日志快照、Flash 导出和 shell 中断/关闭。客户端默认 18080。已移除 18081 监听器及单独诊断入口/构建脚本。状态头读取通过原厂物理读取函数，避免额外打开正在写入的固件文件节点。

构建 `../scripts/build-ota-channel-0031.sh <prefix> <输出目录> 0xa067d000 ap01-http/1`，然后用 `build-ota-expanded-0031.py --mode http` 打包。格式为 `ap01-http-0031-v1`；原版 GIF、PEC、启动头、传统 OTA 指令逐字节保留。扩容镜像物理启动未验证，候选标记不可部署。能力边界、协议和证据见[网络控制台记录](../../reverse/reports/ap01/knowledge/0031-network-console.md)，头部和 PEC 证据见[启动链调查](../../reverse/reports/ap01/knowledge/0031-expanded-boot-investigation.md)。

## 独立维护核心（2026-10-15）

`maintenance.h/.c`是可单独编译的维护事务核心：完整身份认证回调、流式接收、包预检、停业务前保存状态、共用排他安装、未知结果查询、显式AMT1恢复记录和内置文案；`test_maintenance.c`在宿主和RV32执行同一组故障检查。核心自身不依赖业务执行单元，但设备端独立任务/HTTP、持久binding、原厂共用排他、文件安装及UI适配尚不存在，**不是已运行的设备服务或维护界面，不是可刷ROM**。现有旁仓库只有补丁源码和原厂二进制，不是原厂完整工程；按用户要求不额外逆向。

构建用 `tooling/scripts/build_maintenance.py`，详细结果及资源见[维护构建记录](../../reverse/reports/ap01/maintenance-build-20261015.md)。下面同步ABI诊断候选保持其原有范围，不用于启动维护服务。

本目录是本项目的可交叉编译源码，不改第三方克隆。首版为**同步 ABI 诊断候选**：原厂创建对象 → 校验固化的 APX1 包 → 初始化 App 状态 → init/step/stop → 释放状态 → 返回原厂对象。它不实现完整 Bridge、任意文件加载、App-only OTA 或持久安全启动。

`entry.S` 包装原厂 `0xa00b2732` 的6字节调用，保留 `s0–s11`、SP、GP及原厂返回值；原厂对象为空时跳过 App。代码固定在原厂 GIF 无损压缩后腾出的 XIP 区，不从通用堆执行，不改 Boot2、分区、原厂网络/更新函数或按键回调。接入点位于原厂 UI 创建路径，并不证明每次开机都会触发；实机须验证实际调用时机。

`app_abi.h` 定义 ABI1：`init/step/stop(api, state, state_bytes, ...)` 和带长度/版本的服务表。API仅诊断回报，调用者提供分配/释放。禁止线程、保留API/栈指针或异步回调；返回后App不继续运行。通用`ap01_runtime_stop`失败留状态供重试，调用者须保持runtime/API/context；本ROM固定同步App结束后不重试，错误返回也释放其唯一workspace，不推广为任意App外部资源恢复。

APX1 为112字节显式小端头：magic/format/header/total/ABI/flags、固定XIP基址、text偏移/长度、三入口相对text偏移、data偏移/长度、BSS长度、16字节状态对齐、payload CRC32、header CRC32、0031原件SHA256和两个零保留字。CRC使用IEEE格式；header CRC计算时自身字段清零。格式见实现中的字段读取顺序，磁盘不写 native struct。校验全部长度/整数溢出/入口/间隙/状态预算后才分配；data复制、BSS清零，raw malloc指针独立保留用于free。**CRC和基线SHA仅检查损坏与兼容性，不验证发布者或代码安全。**

链接脚本拒绝隐含 `.data/.bss/.sdata/.sbss`；模块可写数据只能放包的状态初始化区。`base.c`提供freestanding memcpy/memset。包中的原件SHA是构建期base ID声明比较，并非计算当前运行ROM摘要。包CRC/base ID不提供发布者认证。

每次hook正常返回后，经0031原厂日志`0xa007cfa2`发一次`APX1 diag0031 result=%u (0=init-step-stop-ok)`；0成功，其他值为ABI错误枚举。实际Ghidra确认5个固定参数+varargs，日志sink可为空。同机日志开启/读取通道尚未核实，因此marker存在不等于实机可观测已验。原厂logger帧848 B，连entry16 B至少864 B，再加格式helper/回调栈；模拟304 B排除了logger。首刷前须核实日志回读和UI任务余栈。

构建/测试命令和产物见 [工具说明](../../tooling/scripts/README.md)、[实现验收](../../reverse/reports/ap01/app-implementation-20261013.md)。所有硬件启动、网络保留、看门狗、Flash/XIP映射和更新接受情况仍待刷机后验证；本阶段用户明确要求不刷机。


## AP01 平台与外部 App 边界（2026-10-22）

本目录拥有 `native_maintenance_0041.*` 的维护路由、设备码鉴权/限流、OTA/切槽生命周期；`native_services_0041.*` 拥有原生 Flash/slot 回调、18080 执行器和 Wi-Fi 切网/恢复。`native_http_transport_0041.*` 拥有有界 HTTP 解析及系统端点请求预算；`native_device_code_menu_0041.*`、字体和 hooks 拥有原厂设置菜单。所有现有事务/持久格式、路径、设备码轮换和 Bridge 凭据兼容保持。

外部 `codex_status` 仅拥有 Bridge 配对/绑定、C2 业务和模板显示。平台通过 `native_app_port_0041.h` 的配对、principal 复制、在线回调连接 App；App 只观察系统 busy 门。`native_services_0041.h` 为启动/生命周期连接，不允许在 App 入口重新实现 Flash/切槽/切网策略。菜单通过既有 window/timer 的 services 指针定位固件服务，不读取 App 私有布局，不新增全局可写 singleton 或线程。

完整 ROM 打包和四个固定 Settings hooks 由 `tooling/scripts/build-native-app-rom-0041.py` 负责；外部 `tools/build-ap01-rom.py` 仅为兼容入口。输出包含原 NULL timer guard 与原 OTA/恢复校验。构建采用两个相邻仓库，外部已有 RV32 audit/link/test 工具编排本目录源；不需要历史隔离源码副本。`test_native_maintenance_0041.cpp` 保留维护回归，并通过 `AP01_MAINTENANCE_ONLY_TEST=1` 在不链接 App/渲染器时验证八位码 OTA、轮换/重放、重启恢复和无稳定记录切槽；SHA256 复用外部通用字节工具。

本次是源码职责迁移，不是设备部署。Wi-Fi 菜单原有未完成验收仍留待办；不把编译或 App 回归通过当作菜单/RF/物理救援验收。
