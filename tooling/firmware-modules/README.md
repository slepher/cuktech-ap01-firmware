# AP01 固件模块

当前基础平台为原厂 **1.0.2_0055**，支持 App ABI 3／平台函数表 3.1。修改版为 **0.1.2**。共享文件名不绑定 ROM 版本。

## 平台诊断版本协议

`GET /api/diagnostic/versions` 返回版本 JSON；`GET /api/diagnostic/status` 同时包含这些字段。
两者使用设备码 Bearer 鉴权、限流和维护互斥，不开放匿名访问。
外层包含 `protocol: "ap01-diagnostic-0041-v1"`、`device_mac`、`boot_id`；版本字段如下：

```json
{
  "versions_protocol": 1,
  "rom": {
    "base_version": "1.0.2_0055",
    "modified_version": "0.1.2",
    "build_id": "<本次 ROM 构建的 32 位十六进制标识>",
    "supports_app": true
  },
  "apps_scope": "loaded_this_boot",
  "apps": [{"app_id": "codex_status", "version": "0.18.108-ap01"}]
}
```

原厂基线与 CUKTECH 修改版版本的源码唯一入口为 `native_version.h`。
CUKTECH 当前源码版本为 `0.1.2`，独立递增；同一发布的无载入器/有载入器构建由
`supports_app` 和 `build_id` 区分，当前原厂目标为 0055。
App 版本由 App 仓库源码配置的 `version` 字段声明，构建器读取该字段；`--version` 可显式覆盖。
固件仓库不内置业务 App 的默认版本，不从已有包推导新版本。ROM 与 App 分别发版，修改源码版本后须重新构建和安装才会改变设备返回值。

[Release CI](../../.github/workflows/release.yml) 在推送 tag 时构建 0055 无 App 基版与 ABI 3 加载平台，离线校验通过后发布附件。tag 不自动改写 `native_version.h`；如需更新设备上报版本，须先修改该文件再打 tag。发布方法见 [README](../../README.md#tag-自动发布)。

`apps` 仅列本次开机成功加载的 App，按启动顺序返回，不枚举磁盘上的旧包、候选包或未启动条目。
部分启动失败时只返回已成功启动的前缀；健康状态查运行状态接口。
App 版本取自已验证的加载清单。
无载入器 ROM 返回 `supports_app: false` 和 `apps: []`；支持载入但尚未启动或无 App 时
返回 `supports_app: true` 和 `apps: []`。`supports_app` 指此 ROM 支持 ABI 3 文件 App 加载。
无效运行快照返回 HTTP 503 / `runtime_snapshot`，不返回误导性的空列表。

客户端：`python -B tooling/scripts/diagnostic-client.py --host IP:18080 --token-file CREDENTIAL.json --mac MAC --operation versions`。

## 共享屏幕宿主与平台代码

`native_platform.cpp` 提供默认无 App 启动入口：保持原厂页面与事件注册，通过独立窗口观察器/50ms timer 保存服务生命周期，在后台启动维护服务；窗口 DELETE 后解除订阅，下一次创建窗口时复用服务。`native_sha256.cpp` 为独立构建提供 SHA256 字节工具实现。构建/打包入口为 `tooling/scripts/build-firmware.py`，不依赖外部 App 仓库。

`screen_host.h/.c` 是不依赖LVGL/ROM地址的宿主核心：调用方提供实际容量的root槽位和应用清单，每应用按稳定screen ID替换屏幕集，支持异步进入准备、双向导航、焦点锁/3秒逃生和隐藏态UI轮询。物理root不删除或重排；逻辑顺序与物理索引分开。只读 `ap01_host_api` 和 `ap01_lvgl_0041` 提供版本与结构长度。

`screen_port.h/.cpp` 通过当前地址映射绑定原厂窗口、普通页面、标签、定时器和LVGL/I4图像；为每页保留独立root/descriptor，图像帧按需分配，离开动画完成才退役源帧。实际draw回调与切入完成分开。普通控件在 `prepare` 中按需创建，`unbind` 清理逻辑页面资源；物理窗口整体由mount/unmount管理。动画期间依赖原厂idle标志，不用300ms固定延迟替代完成。

窗口DELETE期间通过 `ap01_window_detach` 解除本窗口的原厂通知订阅，保留50ms定时器/context作为生命周期锚点；回调必须在缺窗时检查ready。下一次挂钩用 `ap01_window_find` 复用原Runtime/服务，仅重建UI资源。该操作在UI线程、旧对象仍处于DELETE回调时执行。完整对象删除使用原厂公共入口；打包器另装配NULL定时器删除保护，非NULL沿原件尾部执行。


平台模块职责：

| 模块 | 职责 |
| --- | --- |
| `native_io.*` | 时钟、任务、socket、Flash叶调用、原厂入口识别 |
| `native_diagnostic.*` | 维护鉴权后的独立状态、原厂文件/ramlog和物理Flash只读导出；单块1024 B及CRC |
| `native_vfs.*`、`native_filesystem.h` | 原厂LittleFS/VFS绑定与调用方持有的文件对象 |
| `native_firmware.*`、`native_slot.*` | 独立维护事务、恢复/槽位与原厂分区读写绑定 |
| `native_ota_image.*` | 平台原生维护使用的镜像准入/完整性检查 |
| `native_runtime.cpp`、`native_string.h`、`native_calendar.cpp` | freestanding运行库、原生String兼容层、UTC+8日历 |
| `native_http.h`、`native_json.h`、`native_integrity.h` | 业务无关的HTTP值类型、请求局部分配器与完整性工具声明 |
| `native_application.ld` | XIP布局、原厂运行库导入及禁止可写静态/TLS/构造器的链接约束 |

维护模块使用ArduinoJson头文件和 `syncSha256` 字节工具；独立构建由本仓库提供，外部 App 可使用自己的依赖和同名字节工具（只链接一份实现）。它不依赖 `Ap01Business` / `Ap01Application` / C2协议头。维护鉴权调度由平台或 App 启动入口接入，只启动一个维护执行器。`codex_status` 保留绑定、Bundle、共享渲染与业务HTTP，并通过公开头文件引用平台接口。

纯宿主检查（需要宿主 C 编译器）：

```sh
cc -std=c11 -Wall -Wextra -Werror -fsanitize=address,undefined \
  tooling/firmware-modules/screen_host.c \
  tooling/firmware-modules/test_screen_host.c -o /tmp/ap01-screen-host-check
/tmp/ap01-screen-host-check
```

检查覆盖两应用九root、稳定ID/重排、事务拒绝、隐藏/退役、进入超时、焦点锁、跨应用更新和逃生。完整 ROM 使用 `build-firmware.py` 构建，业务 App 使用 `build-app-v3.py --app-config ...` 独立打包。

## AP01 平台与外部 App 边界

本目录拥有 `native_maintenance.*` 的维护路由、设备码鉴权/限流、OTA/切槽生命周期；`native_services.*` 拥有原生 Flash/slot 回调、18080 执行器和 Wi-Fi 切网/恢复。`native_http_transport.*` 拥有有界 HTTP 解析及系统端点请求预算；`native_device_code_menu.*`、字体和 hooks 拥有原厂设置菜单。

外部 `codex_status` 仅拥有 Bridge 配对/绑定、C2 业务和模板显示。平台通过 `native_app_port.h` 的配对、principal 复制、在线回调连接 App；App 只观察系统 busy 门。`native_services.h` 为启动/生命周期连接，不允许在 App 入口重新实现 Flash/切槽/切网策略。菜单通过既有 window/timer 的 services 指针定位固件服务，不读取 App 私有布局，不使用全局可写 singleton 或额外线程。

完整 ROM 打包和四个固定 Settings hooks 由 `tooling/scripts/build-native-app-rom.py` 负责。输出包含 NULL timer guard 与 OTA/恢复校验。`build-firmware.py` 与 `native_build.py` 统一负责独立版及 App 版的平台编译、审计、预算提取、链接与打包；外部 App 单独使用 `build-app-v3.py --app-config ...` 构建，不静态嵌入平台 ROM。`test_native_maintenance.cpp` 保留维护回归，并通过 `AP01_MAINTENANCE_ONLY_TEST=1` 在不链接 App/渲染器时验证八位码 OTA、轮换/重放、重启恢复和无稳定记录切槽。

完整冷启动、Wi-Fi 菜单、外设与物理救援需实机验收。构建与离线检查不访问设备。

维护凭据使用说明见 [本地维护凭据菜单](access-menu-0031.md)；App 接口见 [平台 C ABI](../../docs/app-platform-api-v3.md)。
