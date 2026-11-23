# 0055／0.1.3 平台离线验证

使用 Python 3 和 xPack RISC-V GCC 12.5.0-1，在仓库根目录执行。每次构建使用新的输出路径。

## ROM 构建与校验

```sh
python3 -B tooling/scripts/test-rom-target.py
python3 -B tooling/scripts/build-firmware.py --target 0055 --build-dir build/check-base --output build/check/ap01-0055-base-0.1.3.bin --tool-prefix /path/to/riscv-none-elf-
python3 -B tooling/scripts/test-firmware.py --manifest build/check/ap01-0055-base-0.1.3.manifest.json
python3 -B tooling/scripts/build-firmware.py --target 0055 --boot-app-v3 --build-dir build/check-app-platform --output build/check/ap01-0055-app-platform-0.1.3.bin --tool-prefix /path/to/riscv-none-elf-
python3 -B tooling/scripts/test-firmware.py --manifest build/check/ap01-0055-app-platform-0.1.3.manifest.json
```

检查包含原件身份、补丁边界、恢复标记、镜像长度与 CRC、产物摘要、源码审计和链接结果。发布附件与 CI 构建产物见 [版本发布](releasing.md)。manifest 引用构建机上的原件与审计路径，应在对应构建目录中运行校验。

## App 包与平台检查

```sh
mkdir -p build/apx2-check
python3 -B tooling/scripts/test-apx2.py --out build/apx2-check
```

`test-native-app-platform-v3.py` 使用 `--out` 和 `--package` 检查 `codex_status` 包与宿主平台，需要预建输出目录和 Clang。`test-native-app-set-v3.py` 另外要求 `--tool-prefix`，使用 `codex_status` 包验证 App 集合行为。App 构建方法见 [独立 App 使用说明](../project-workflow/ap01-app-update/d1-direct-app.md)。

## QEMU 模型

`build-app-v3-guest.py` 构建 RV32 guest；`test-app-abi-qemu.py` 接受 `--qemu`、`--expected-engine-sha256`、`--support-dir`、`--fixture-dir` 和 `--output`。运行前需准备匹配的 AP01 模型引擎、支持脚本与 guest fixture，使用 `--help` 查看输入要求。

QEMU 运行器为 ROM I/O、LVGL、维护监听、线程与时钟提供模型替身，用于检查 RV32 指令执行、接口调用和状态转换。
