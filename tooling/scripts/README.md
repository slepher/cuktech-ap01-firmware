# AP01 固件构建与诊断工具

从仓库根目录执行，模块源码位于 `tooling/firmware-modules/`。

| 工具 | 用途 |
| --- | --- |
| `build-firmware-0041.py` | 默认独立构建平台 ROM；`--app-config` 从 App 源码配置构建；支持 audit/link/rom 阶段 |
| `native_build_0041.py` | 唯一 RV32 平台源码清单、编译参数、XIP 审计、资源预算与链接实现 |
| `test-native-build-0041.py` | App 配置路径边界、源码/对象/配置变化使链接失效的回归 |
| `test-firmware-0041.py` | 真实候选重建、CRC、源码身份、独立依赖边界及越界篡改拒绝检查 |
| `test-platform-independence-0041.py` | 复制平台构建输入到无相邻仓库的新目录，执行完整构建及 ROM/OTA 回归 |
| `test-native-wifi-switch-0041.py` | Linux/WSL 主机 Wi-Fi/诊断回归；使用本仓库头文件，无需 App |
| `build-native-app-rom-0041.py` | 将已审计、链接的外部应用打包为 0041 完整候选 |
| `build-ota-channel-0041.py/.sh`、`patch_0041_unsigned_ota.py` | 0041 OTA 实验模块构建与精确补丁校验 |
| `build_app_rom.py`、`build_maintenance.py`、`build-ota-*-0031.*` | 历史 0031 构建入口 |
| `diagnostic-client-0041.py`、`diagnostic-console-0031.py` | 诊断客户端 |
| `upload-ota-0031.py` | 显式设备 OTA 工具，拆分不执行它 |
| `test*.py` | 固件模块、客户端与打包回归 |

默认入口与可执行命令见[仓库说明](../../README.md)。`python -B tooling/scripts/build-firmware-0041.py --help` 查看参数；默认原件为本仓库 `roms/0041/ap01-1.0.2_0041.bin`。独立构建使用本仓库的平台入口、SHA256 和 ArduinoJson 头文件。`build-native-app-rom-0041.py` 是共享底层打包器，接受平台 ABI 2 或现有 App ABI 1，仍保留外部 App 原有调用方式。

独立性复验：`python -B tooling/scripts/test-platform-independence-0041.py --out build/independence-0041`。输出目录必须尚不存在；可指定 `--tool-prefix`。它只复制平台模块、已保存的依赖、所需脚本与原厂 ROM，生成 `independence-report.json`。unsigned-OTA 检查在临时目录生成自己的候选；可选 Unicorn 从当前 Python 环境导入，缺少时仅跳过该项 RV32 指令执行测试，不探测逆向仓库。

App JSON 配置声明 `format: 1`、相对配置文件的 `root`、相对 App 根目录的 `include_dirs`、`sources`、`plain_sources` 及 `defines`。路径必须存在且位于 App 根目录；源码的对象名必须唯一。`plain_sources` 为不启用原生 String 适配和 App 宏的共享绑定源码，其余 App 源码采用原生编译设置。App ABI 1 继续提供运行入口、manifest、`abi_budget.cpp` 的 `.ap01_budget/.ap01_render_budget` 测量；平台补丁和链接脚本不由 App 配置覆盖。ArduinoJson 默认取本仓库版本，可通过 `--json-header` 显式覆盖。配置文件的身份也随审计记录，变化后必须重审计。

`--app-source-dir` 保留为旧产物打包入口，不再作为推荐 App 构建流程。外部 App 的集成测试需显式提供 App 源码或产物；`enable-*-0041.py` 是要求 `--source-root` 的历史源码迁移工具，不由默认构建调用。历史 0031 构建和官方下载器仍可能使用 `cuktech-ap01-firmware-tools`、指定工具链或模拟依赖，不能作为当前 0041 独立构建的前置步骤。

研究、模拟器和离线复验工具已移至 [逆向工具目录](../../../cuktech-ap01-firmware-reverse/tooling/scripts/README.md)；完整历史命令见 [拆分前工具说明](../../../cuktech-ap01-firmware-reverse/reverse/migration/tooling-guide-before-split-20261026.md)。历史实验输出已迁移，必要时显式传入逆向仓库中的输入路径。
