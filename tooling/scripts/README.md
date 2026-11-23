# AP01 固件构建与诊断工具

当前基础平台为原厂 1.0.2_0055，只构建 0055，App 只支持 ABI 3。文件名不带 ROM 版本；`--target` 当前只接受 `0055`。默认原件由 `rom_target.py` 读取 `../rom-targets/current.json`，严格核对大小、SHA256 和补丁原字节。

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

构建示例见仓库 [README](../../README.md)。RV32 工具链通过 `--tool-prefix` 显式指定；Release CI 固定使用 xPack GCC 12.5.0-1。真实 App 打包还使用 pyelftools。

[Release CI](../../.github/workflows/release.yml) 在任意 tag 推送到 GitHub 后构建无 App 基版和 ABI 3 加载平台。两者分别使用独立构建目录，并运行 `test-rom-target.py` 和 `test-firmware.py`；全部通过后，Release 仅发布两个完整 ROM 和只包含它们的 `SHA256SUMS`。payload、ELF、map、manifest、审计与链接报告通过 Actions 的 `ap01-build-details-<tag>` 构建产物保存 90 天。业务 App 包不属于此发布流程，tag 不自动修改设备上报的源码版本。发布命令见 [README](../../README.md#tag-自动发布)。

测试通常要求预建输出目录；ROM 候选必须使用新输出路径。

`--app-source-dir` 只打包具有当前目标与源码审计的产物。构建目录必须与目标、源码和工具链一致。

修改版版本为 `0.1.2`，由 `native_version.h` 定义。独立 App 的版本取自 App 配置，与固件版本分别管理。当前接口与包格式见 [平台接口](../../docs/app-platform-api-v3.md) 和 [APX2 格式](../../docs/apx2-package-format.md)。

对于已发布版本，可在 Actions 手动运行 Release 工作流并填写 `release_tag`，下载并校验现有附件后归档调试文件。手动运行不重编固件、不创建 Release，也不删除附件；清理附件前须先确认归档成功。
