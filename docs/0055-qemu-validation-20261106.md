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

检查包含原件身份、补丁边界、恢复标记、镜像长度与 CRC、产物摘要、源码审计和链接结果。Release 只包含两个完整 BIN 和对应的 `SHA256SUMS`。构建细节可在 Actions 下载 `ap01-build-details-<tag>`（保留 90 天）。manifest 引用构建机上的原件与审计路径，应在对应构建目录中运行校验。

## App 包与平台检查

```sh
mkdir -p build/apx2-check
python3 -B tooling/scripts/test-apx2.py --out build/apx2-check
```

`test-native-app-platform-v3.py` 使用 `--out` 和 `--package` 检查 `codex_status` 包与宿主平台，需要预建输出目录和 Clang。`test-native-app-set-v3.py` 另外要求 `--tool-prefix`，使用 `codex_status` 包验证 App 集合行为。App 构建方法见 [独立 App 使用说明](../project-workflow/ap01-app-update/d1-direct-app.md)。

## QEMU 模型

`build-app-v3-guest.py` 构建 RV32 guest；`test-app-abi-qemu.py` 接受 `--qemu`、`--expected-engine-sha256`、`--support-dir`、`--fixture-dir` 和 `--output`。运行前需准备匹配的 AP01 模型引擎、支持脚本与 guest fixture，使用 `--help` 查看输入要求。

QEMU 中的 ROM I/O、LVGL、维护监听、线程与时钟可由模型替身提供。模型结果只覆盖实际执行的路径，不证明完整冷启动、射频、外设、掉电恢复或执行内存硬件行为。发布流程以 [Release CI](../.github/workflows/release.yml) 的构建和离线校验为准；实机验收需单独完成。
