# CUKTECH AP01 固件平台

本仓库维护 AP01 固件平台、原厂接口适配、独立 App 打包及维护工具。当前平台构建只支持原厂 **0055**，独立 App 只支持 **ABI 3**（平台函数表 3.1）。修改版版本为 **0.1.3**。

> **准备刷入第三方 ROM 的用户：不要将原厂 `1.0.2_0031` 通过米家官方 OTA 升级到原厂 `1.0.2_0041` 或 `1.0.2_0055`。** 从官方 0041 起，OTA 会拒绝未签名固件，升级后无法再通过这条常规 OTA 通道刷入本项目等未签名第三方 ROM。这里禁止的是“0031 → 官方 0041／0055”，不是“0031 → 基于 0055 的自定义 ROM”。更换下载地址或使用 FDS 中转不能绕过签名检查。刷入条件与流程见 [刷机说明](docs/flashing.md)。

源码和脚本文件名不绑定 ROM 版本。当前原件身份与补丁位置在 `tooling/rom-targets/current.json`，原厂地址映射在 `tooling/firmware-modules/native_rom_map.h`。

| 目录 | 内容 |
| --- | --- |
| [平台接口](docs/app-platform-api-v3.md) | App ABI 3／平台 3.1 合同 |
| [包格式](docs/apx-package-format.md) | APX 容器版本 2，App ABI 3 |
| [固件模块](tooling/firmware-modules/README.md) | 平台、维护、OTA、UI 和 ABI 3 服务 |
| [构建工具](tooling/scripts/README.md) | 构建、打包、诊断和离线验证 |
| [刷机说明](docs/flashing.md) | 官方 ROM 转自定义 ROM、升级限制、30 秒健康窗口与失败恢复 |
| [ROM 清单](roms/CATALOG.md) | 0055 原件与固件类型 |
| [版本发布](docs/releasing.md) | tag、Release CI、固件附件和构建产物 |

构建需要 Python 3 和支持 `rv32imafc/ilp32f` 的 RISC-V GCC。ArduinoJson 已随仓库保存；平台构建不依赖外部仓库。

```sh
# 无 App 基版
python3 -B tooling/scripts/build-firmware.py --output build/base.bin --tool-prefix /path/to/riscv-none-elf-
# 独立 App 加载平台
python3 -B tooling/scripts/build-firmware.py --boot-app-v3 --output build/app-platform.bin --tool-prefix /path/to/riscv-none-elf-
python3 -B tooling/scripts/test-firmware.py --manifest build/app-platform.manifest.json
```

基础平台为原厂 **1.0.2_0055**（`roms/0055/ap01-1.0.2_0055.bin`），默认构建目标为 `0055`。输出必须使用新文件名。业务 App 单独通过 `build-app-v3.py --app-config ...` 构建，平台 ROM 与业务 App 分别构建。


来源与许可见 [NOTICE](NOTICE.md) 和 [LICENSE](LICENSE)。
