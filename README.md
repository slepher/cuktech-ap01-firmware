# CUKTECH AP01 固件平台

本仓库维护 AP01 固件模块、原厂接口适配、离线构建、ROM 打包及诊断客户端。逆向研究已拆分到相邻的 [cuktech-ap01-firmware-reverse](../cuktech-ap01-firmware-reverse/README.md)。

| 目录 | 内容 |
| --- | --- |
| [tooling/firmware-modules/](tooling/firmware-modules/README.md) | 共享屏幕宿主、平台服务、维护、OTA、链接脚本与模块测试 |
| [tooling/scripts/](tooling/scripts/README.md) | 构建、打包、诊断与相关回归检查 |
| [roms/](roms/CATALOG.md) | 原厂镜像和本地候选；保留 0041 构建基线 |

0041 原厂基线为 `roms/0041/ap01-1.0.2_0041.bin`，6,769,704 字节，既有 SHA256 标识为 `972db4c136c7ed9e24a83c07c1a7fd62040ca018b08ca285216d26b1fee3c6b9`。逆向仓库也保存相同基线；本仓库的正常构建不依赖逆向仓库。

默认构建不带业务 App：保留原厂页面，接入设备码菜单、Wi-Fi、维护/诊断和 OTA 平台服务。ArduinoJson 7.4.3 头文件已随仓库保存，只需另行安装 Python 3 和支持 `rv32imafc/ilp32f` 的 RISC-V GCC 工具链。

```sh
python -B tooling/scripts/build-firmware-0041.py --output build/standalone-0041/ap01-platform-0041.bin
python -B tooling/scripts/test-firmware-0041.py --manifest build/standalone-0041/ap01-platform-0041.manifest.json
```

脚本从 PATH 或 Windows PlatformIO 标准安装目录寻找 `riscv32-esp-elf-` 工具，也可指定 `--tool-prefix /path/to/riscv32-esp-elf-`。输出目录自动创建；候选 ROM 和配套文件必须使用新文件名。默认构建只读取本仓库源码、依赖和原厂 ROM，不需要相邻 App 或逆向仓库。生成物仍为未实机验证的候选，构建不访问设备。

可运行 `python -B tooling/scripts/test-platform-independence-0041.py --out build/independence-0041`，在没有相邻 App/逆向仓库的全新副本中复验编译、链接、ROM 打包和 OTA 检查；输出目录须不存在。依赖边界见[拆分记录](REPOSITORY-SPLIT.md)。

`codex_status` 是可选外部 App，仅提供源码与 `ports/ap01/build-0041.json` 配置。编译、平台源码清单、审计、预算提取、链接布局和 ROM 打包均由本仓库执行：

```sh
python -B tooling/scripts/build-firmware-0041.py --app-config ../codex_status/ports/ap01/build-0041.json --build-dir build/with-app/objects --output build/with-app/ap01-codex-status-0041.bin
```

`--stage audit|link|rom` 支持分阶段执行，默认 `rom` 从源码执行完整流程。App 原有 `check-ap01-native.py`、`link-ap01-native.py` 仅转发到该入口，`build-ap01-rom.py` 仅转发共享打包器；不再维护平台源码清单、编译/链接参数或预算实现。旧 `--app-source-dir` 只用于打包已有产物；源码、对象、头文件、App 配置和 ELF 必须通过身份检查。默认 App 构建同样使用本仓库保存的 ArduinoJson 与 SHA256，无需 App 的 `.pio` 目录。

研究报告、语义合同、分析源码、QEMU/Ghidra/REA 工具和历史中间产物归逆向仓库维护。

[拆分记录](REPOSITORY-SPLIT.md)说明两仓边界和历史路径。来源与许可见 [NOTICE.md](NOTICE.md) 和 [LICENSE](LICENSE)。
