# CUKTECH AP01 固件平台

本仓库维护 AP01 固件模块、原厂接口适配、离线构建、ROM 打包及诊断客户端。逆向研究已拆分到相邻的 [cuktech-ap01-firmware-reverse](../cuktech-ap01-firmware-reverse/README.md)。

| 目录 | 内容 |
| --- | --- |
| [tooling/firmware-modules/](tooling/firmware-modules/README.md) | 共享屏幕宿主、平台服务、维护、OTA、链接脚本与模块测试 |
| [tooling/scripts/](tooling/scripts/README.md) | 构建、打包、诊断与相关回归检查 |
| [roms/](roms/CATALOG.md) | 原厂镜像和本地候选；保留 0041 构建基线 |

0041 原厂基线为 `roms/0041/ap01-1.0.2_0041.bin`，6,769,704 字节，既有 SHA256 标识为 `972db4c136c7ed9e24a83c07c1a7fd62040ca018b08ca285216d26b1fee3c6b9`。逆向仓库也保存相同基线；本仓库的正常构建不依赖逆向仓库。

外部 `codex_status` 继续使用本仓库的 `tooling/firmware-modules/` 与 `tooling/scripts/build-native-app-rom-0041.py`。研究报告、语义合同、分析源码、QEMU/Ghidra/REA 工具和历史中间产物归逆向仓库维护。实验依赖与私有输出需按各工具要求准备。

[拆分记录](REPOSITORY-SPLIT.md)说明两仓边界和历史路径。来源与许可见 [NOTICE.md](NOTICE.md) 和 [LICENSE](LICENSE)。
