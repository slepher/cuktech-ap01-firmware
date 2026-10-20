# AP01 逆向研究索引

本目录保存固件研究结论。外部程序入 ROM 的通用方法由本项目维护，具体业务实现及发布由使用方维护。

| 主题 | 入口 |
| --- | --- |
| 范围与证据标准 | [研究需求](requirements.md)、[研究计划](plan.md)、[任务](task.md)、[状态](status.md) |
| 外部程序编译和打包进 ROM | [打包说明](design.md)、[0041 多屏幕宿主架构](multi-screen-app-host-0041.md)、[0031 XIP 实现](app-implementation-20261013.md)、[模块源码](../../../tooling/firmware-modules/README.md) |
| 静态工具与来源 | [静态分析方法](reverse-design.md)、[阶段报告](report.md)、[上游材料对照](../cuktech-ap01-repository-value-analysis.md) |
| 0031 分区、启动和堆 | [分区与启动](knowledge/0031分区与启动入口复查.md)、[网络与 HTTP](knowledge/0031网络监听与HTTP复查.md) |
| 0031 首次安装与槽尾实验 | [首次安装](first-install-0031-20261018.md)、[实机成功记录](knowledge/0031-tail-physical-success-20261018.md)、[镜像准入](ota-image-admission-20261019.md) |
| 0031 扩容、物理读取和诊断 | [扩容](ota-expansion-0031-20261018.md)、[启动调查](knowledge/0031-expanded-boot-investigation.md)、[网络控制台](knowledge/0031-network-console.md)、[PEC 与升级](knowledge/0031-pec-readback-and-controlled-upgrade.md) |
| 0041 续作与原厂上层 | [交接](0041-handoff.md)、[上层恢复](upper-layer-0041-20261017.md)、[MiIO/MiBLE](miio-mible-protocol-rea-0041-20261017.md) |
| 0041 静态比较与签名 | [版本对比](0041-reverse-20261013.md)、[签名分析](knowledge/0041签名与Bridge接口分析.md)、[下载核验](firmware-download-20261013.md) |
| REA / RISC-V / Ghidra | [私有分析环境](private-profile-0041-20261017.md)、[RISC-V 实现](rea-riscv-implementation-20261016.md) |
| QEMU 模型与 OTA | [显示交接](qemu-display-handoff-20261017.md)、[RTC 与显示](qemu-rtc-display-20261017.md)、[0041 OTA](qemu-ota-final-20261017.md)、[0031 OTA](qemu-ota-0031-20261017.md) |
| 原厂 UI 重建 / NuttX SIM | [SIM 环境](nuttx-sim-20261016.md)、[静态 UI](ui-reverse-20261016.md)、[重建验收](application-rehost-complete-0041-20261017.md)、[功能矩阵](application-function-matrix-0041.json)、[Wi-Fi 缺口](knowledge/0041-sim-wifi-selection-gaps.md) |
| 恢复与限制 | [恢复评估](failure-recovery-20261013.md)、[恢复策略](recovery-policy-20261017.md)、[USB 调查](usb-firmware-check-20261013.md) |

带日期的文件保留该阶段的验证边界；“当时未取得原件”“未安装”等表述不能替代后续报告。原始产物与私有材料的位置规则见[仓库入口](../../../README.md)。
