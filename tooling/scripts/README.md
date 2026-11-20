# AP01 固件构建与诊断工具

当前平台只构建 0055，App 只支持 ABI 3。文件名不带 ROM 版本；`--target` 当前只接受 `0055`。默认原件由 `rom_target.py` 读取 `../rom-targets/current.json`，严格核对大小、SHA256 和补丁原字节。

| 入口 | 用途 |
| --- | --- |
| `build-firmware.py` | 基版或 `--boot-app-v3` 应用版，支持 audit/link/rom 分阶段 |
| `build-app-v3.py` | 从 `--app-config` 构建独立 ABI 3 APX2 包 |
| `build-native-app-rom.py` | 打包已审计、目标一致的 ROM 产物 |
| `app-set-client-v3.py` | 集合更新；共享 HTTP/回执逻辑在 `app_client_common.py` |
| `diagnostic-client.py` | 设备码认证的只读诊断 |
| `download_official.py` | 官方查询下载，默认要求 0055，也可显式查询最新版本 |
| `test-rom-target.py` / `test-native-rom.py` | 原件身份、补丁边界、地址覆盖和 ABI 指令核对 |
| `test-apx2.py` | ABI 3 包校验、加载、损坏拒绝和 SHA256 |
| `test-native-app-platform-v3.py` / `test-native-app-set-v3.py` | 平台和集合的宿主验证 |
| `test-platform-independence.py` | 无兄弟仓库的独立完整构建 |
| `build-app-v3-guest.py` / `test-app-abi-qemu.py` | 仅 ABI 3 的 QEMU 模型构建／执行 |

构建示例见仓库 [README](../../README.md)。RV32 工具链通过 `--tool-prefix` 显式指定；推荐兼容的 xPack GCC 12.5。真实 App 打包还使用 pyelftools。测试通常要求预建输出目录；ROM 候选必须使用新输出路径。

`--app-source-dir` 只打包具有当前目标与源码审计的产物，不能复用旧目标对象。外部 App 的配置和 include 路径需要同步使用新的共享文件名；仓库不提供旧文件名兼容转发。

0041 专属补丁、旧 ABI 2 单包更新客户端与测试已删除。0031 历史工具仍保留，依赖与使用范围见对应文件说明；它们不是当前平台构建前置步骤。协议中已有的历史标识不等于支持旧 ROM 构建。
