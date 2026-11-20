# CUKTECH AP01 固件平台

本仓库维护 AP01 固件平台、原厂接口适配、独立 App 打包及维护工具。当前平台构建只支持原厂 **0055**，独立 App 只支持 **ABI 3**（平台函数表 3.1）。0041 构建和 ABI 2 接口、执行器、专属测试已移除；原厂镜像与历史验证记录保留用于追溯。

源码和脚本文件名不绑定 ROM 版本。当前原件身份与补丁位置在 `tooling/rom-targets/current.json`，原厂地址映射在 `tooling/firmware-modules/native_rom_map.h`。部分 C 符号和对外协议仍保留历史命名，以免无关地改变接口。

| 目录 | 内容 |
| --- | --- |
| [平台接口](docs/app-platform-api-v3.md) | App ABI 3／平台 3.1 合同 |
| [包格式](docs/apx2-package-format.md) | APX2 容器版本 2，App ABI 3 |
| [固件模块](tooling/firmware-modules/README.md) | 平台、维护、OTA、UI 和 ABI 3 服务 |
| [构建工具](tooling/scripts/README.md) | 构建、打包、诊断和离线验证 |
| [ROM 清单](roms/CATALOG.md) | 原件与历史候选 |

构建需要 Python 3 和支持 `rv32imafc/ilp32f` 的 RISC-V GCC。ArduinoJson 已随仓库保存；平台构建不依赖相邻 App 或逆向仓库。

```sh
# 无 App 基版
python3 -B tooling/scripts/build-firmware.py --output build/base.bin --tool-prefix /path/to/riscv-none-elf-
# 独立 App 加载平台
python3 -B tooling/scripts/build-firmware.py --boot-app-v3 --output build/app-platform.bin --tool-prefix /path/to/riscv-none-elf-
python3 -B tooling/scripts/test-firmware.py --manifest build/app-platform.manifest.json
```

默认目标为 0055；显式 `--target 0041` 会拒绝。输出必须使用新文件名。业务 App 单独通过 `build-app-v3.py --app-config ...` 构建，ROM 构建不再接受静态嵌入业务源码。

既有合法 ABI 3 包保持格式兼容；ABI 2 包拒绝加载。APX2 名称中的 2 是容器版本，与 App ABI 不同。业务 Bundle 的 `compiler_abi: 2` 也属于另一套协议，不因本次移除 App ABI 2 而修改。

完整冷启动和实机外设尚待验收，候选不代表可部署版本。本地构建和检查不访问设备。

历史 0031 独立工具不属于本次移除范围。逆向研究见 [接续入口](docs/reverse-engineering-quickstart.md)；来源与许可见 [NOTICE](NOTICE.md) 和 [LICENSE](LICENSE)。
