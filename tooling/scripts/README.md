# AP01 固件构建与诊断工具

从仓库根目录执行，模块源码位于 `tooling/firmware-modules/`。

| 工具 | 用途 |
| --- | --- |
| `build-native-app-rom-0041.py` | 将已审计、链接的外部应用打包为 0041 完整候选 |
| `build-ota-channel-0041.py/.sh`、`patch_0041_unsigned_ota.py` | 0041 OTA 实验模块构建与精确补丁校验 |
| `build_app_rom.py`、`build_maintenance.py`、`build-ota-*-0031.*` | 历史 0031 构建入口 |
| `diagnostic-client-0041.py`、`diagnostic-console-0031.py` | 诊断客户端 |
| `upload-ota-0031.py` | 显式设备 OTA 工具，拆分不执行它 |
| `test*.py` | 固件模块、客户端与打包回归 |

`python -B tooling/scripts/build-native-app-rom-0041.py --help` 查看参数；默认原件仍为本仓库 `roms/0041/ap01-1.0.2_0041.bin`。交叉工具链、依赖和输出目录按脚本要求预先准备。

研究、模拟器和离线复验工具已移至 [逆向工具目录](../../../cuktech-ap01-firmware-reverse/tooling/scripts/README.md)；完整历史命令见 [拆分前工具说明](../../../cuktech-ap01-firmware-reverse/reverse/migration/tooling-guide-before-split-20261026.md)。历史实验输出已迁移，必要时显式传入逆向仓库中的输入路径。
