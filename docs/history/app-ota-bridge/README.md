# 已撤出的 codex_status App OTA 实现

按用户于 2026-11-05 明确的仓库边界，将 App OTA 维护功能归 firmware。当前可执行入口为 firmware 的 Python 多包 CLI，见 [归属与命令](../../app-ota-ownership.md)。这些补丁是历史源码证据，不参与构建，也不是已迁移可运行的独立 Rust 应用。

补丁源自 codex_status 提交，仅包含 bridge/tools 路径：

- c556f2b：AMF3/APX2 校验、维护传输、回执、单步协调。
- cc9bd35：回执恢复与终态归档。
- ba7d9b5：Bridge worker、Tauri/MCP 命令。
- 754692a：Bridge UI 与交叉测试。
- b16450e：桌面暂存缓存约束。

撤出按上述逆序应用，各次反向应用均先通过 git apply --check。不回退业务协议整改、Bundle 存储、配对 worker、C 函数表或 App 入口。恢复历史需从匹配基线按正序应用，不能向当前业务开发分支盲目应用。
