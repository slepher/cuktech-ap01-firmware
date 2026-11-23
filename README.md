# CUKTECH AP01 固件平台

本仓库维护 AP01 固件平台、原厂接口适配、独立 App 打包及维护工具。当前平台构建只支持原厂 **0055**，独立 App 只支持 **ABI 3**（平台函数表 3.1）。修改版版本为 **0.1.2**。

> **准备刷入第三方 ROM 的用户：不要将原厂 `1.0.2_0031` 通过米家官方 OTA 升级到原厂 `1.0.2_0041` 或 `1.0.2_0055`。** 从官方 0041 起，OTA 会拒绝未签名固件，升级后无法再通过这条常规 OTA 通道刷入本项目等未签名第三方 ROM。这里禁止的是“0031 → 官方 0041／0055”，不是“0031 → 基于 0055 的自定义 ROM”。更换下载地址或使用 FDS 中转不能绕过签名检查。刷入条件与流程见 [刷机说明](docs/flashing.md)。

源码和脚本文件名不绑定 ROM 版本。当前原件身份与补丁位置在 `tooling/rom-targets/current.json`，原厂地址映射在 `tooling/firmware-modules/native_rom_map.h`。

| 目录 | 内容 |
| --- | --- |
| [平台接口](docs/app-platform-api-v3.md) | App ABI 3／平台 3.1 合同 |
| [包格式](docs/apx2-package-format.md) | APX2 容器版本 2，App ABI 3 |
| [固件模块](tooling/firmware-modules/README.md) | 平台、维护、OTA、UI 和 ABI 3 服务 |
| [构建工具](tooling/scripts/README.md) | 构建、打包、诊断和离线验证 |
| [刷机说明](docs/flashing.md) | 官方 ROM 转自定义 ROM、升级限制、30 秒试启动保护与失败恢复 |
| [ROM 清单](roms/CATALOG.md) | 0055 原件与发布附件 |

构建需要 Python 3 和支持 `rv32imafc/ilp32f` 的 RISC-V GCC。ArduinoJson 已随仓库保存；平台构建不依赖外部仓库。

```sh
# 无 App 基版
python3 -B tooling/scripts/build-firmware.py --output build/base.bin --tool-prefix /path/to/riscv-none-elf-
# 独立 App 加载平台
python3 -B tooling/scripts/build-firmware.py --boot-app-v3 --output build/app-platform.bin --tool-prefix /path/to/riscv-none-elf-
python3 -B tooling/scripts/test-firmware.py --manifest build/app-platform.manifest.json
```

基础平台为原厂 **1.0.2_0055**（`roms/0055/ap01-1.0.2_0055.bin`），默认构建目标为 `0055`。输出必须使用新文件名。业务 App 单独通过 `build-app-v3.py --app-config ...` 构建，平台 ROM 与业务 App 分别构建。

## Tag 自动发布

向 GitHub 推送任意新 tag 后，[Release CI](.github/workflows/release.yml) 会使用 xPack RISC-V GCC 12.5.0-1 构建 0055 无 App 基版与 ABI 3 App 加载平台，运行原件及固件离线校验，通过后创建同名 GitHub Release，并自动生成变更说明。

```sh
git tag -a v0.1.2 -m "AP01 0055 platform release"
git push origin v0.1.2
```

Release 附件包含 `ap01-0055-base-0.1.2.bin`、`ap01-0055-app-platform-0.1.2.bin`和 `SHA256SUMS`（仅包含这两个完整 BIN 的校验和）。payload、ELF、map、manifest、审计与链接报告存放在对应 Actions 运行的 `ap01-build-details-<tag>` 构建产物中，保留 90 天，刷机无需下载。附件版本号读取 `native_version.h` 中的 `AP01_MODIFIED_ROM_VERSION`（当前为 `0.1.2`，不带后缀），与设备上报的修改版版本一致；原厂基础平台版本仍为 0055。发布前更新源码版本，再推送对应 tag（如 `v0.1.2`）。仅创建本地 tag 不触发 CI；工作流使用内置 `GITHUB_TOKEN` 的 `contents: write` 权限，无需额外发布密钥。自动发布仅表示构建与离线校验通过，不代表完成实机验收。

APX2 名称中的 2 是容器版本，与 App ABI 不同。业务 Bundle 的 `compiler_abi: 2` 也属于另一套协议。

完整冷启动和实机外设尚待验收，候选不代表可部署版本。本地构建和检查不访问设备。

来源与许可见 [NOTICE](NOTICE.md) 和 [LICENSE](LICENSE)。
