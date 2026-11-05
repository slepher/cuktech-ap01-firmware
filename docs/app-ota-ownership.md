# App OTA 归属与独立业务主线

2026-11-05：App 可执行包更新属于 firmware OTA；codex_status 不再实现 App OTA 客户端、后台协调器、Tauri/MCP 命令或更新 UI。业务 Bundle/C2/BLE、配对、显示和必要的 ABI 3.1 App 适配继续由 codex_status 维护。

## 维护入口

复用 firmware 现有 `tooling/scripts/app-set-client-v3.py`，不另起 Rust/桌面框架：

```sh
python3 tooling/scripts/app-set-client-v3.py --host HOST:18080 --mac MAC12 --code-file /private/path/code --action status
python3 tooling/scripts/app-set-client-v3.py --host HOST:18080 --mac MAC12 --code-file /private/path/code --manifest set.amf3 --package business.apx2 --receipt /private/path/update.json
```

单更只传变更包，Manifest 始终描述完整目标集合；批更重复 `--package`。同一回执用于续传；`--action result` 查询，`--action cancel` 取消。丢 ACK/重启断连按原事务恢复，不能换 ID 重装。结果包含持久集合和实际运行列表。设备码不入库。这些是操作说明，本次不连接设备。

原 Bridge 的暂存缓存、自动 worker、桌面 UI 不迁成新的运行时依赖；其实现完整保留于 [历史补丁](history/app-ota-bridge/README.md)。本机 Bridge 数据、旧回执和暂存产物不删除、不自动转换为 CLI 回执；两种格式不同，不能假装可直接续传。当前迁移没有生产部署，原运行实例不被重启。

## 当前交付主线

1. 真实业务源码独立编译为 APX2，零外部导入，通过 C 函数表调用平台。
2. 平台开机读取并校验完整 Manifest，加载各包，调用 start；不做在线卸载。
3. firmware OTA 下载并验证变更包，持久切换记录后重启；单更与批更共用一条路径。
4. 启动成功确认，失败恢复旧集合；验证 Bundle 与绑定保持。

历史孤儿目录扫描、Bridge 原生 IPC/自动发现、完整桌面更新 UI 不作为此主线的前置。现有资源边界、基本空间拒绝、事务文件清理和恢复保护保留；不借收敛删除已实现的必要校验。QEMU 只在 james.local Docker 中执行，实机操作另行授权。
