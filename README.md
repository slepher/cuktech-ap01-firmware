# CUKTECH AP01 固件逆向

本项目独立研究 CUKTECH AP01 的 `1.0.2_0031` / `1.0.2_0041` 固件，保存机器码分析、原厂行为复查、模拟模型及实验性 ROM 构建工具。没有原厂完整源码，更新包也不是整片 Flash 备份。

外部项目可以引用本项目的结论和工具，将自己的程序编译、链接并打包进 ROM。程序的业务需求、产品协议和发布状态由外部项目维护；本项目维护固件基线、注入约束、打包方法及验证证据。

## 文件位置

| 位置 | 用途 |
| --- | --- |
| [roms/CATALOG.md](roms/CATALOG.md) | 原厂镜像及实验候选的版本、长度、哈希与验证范围 |
| `roms/0031/`、`roms/0041/` | Git 收录的未修改原厂 0031 / 0041 镜像；实验候选须另行准备 |
| [reverse/reports/ap01/](reverse/reports/ap01/README.md) | 研究索引、阶段报告和交接；`knowledge/` 保存专题结论 |
| [reverse/analysis/](reverse/analysis/README.md) | 必要语义合同、资源清单、来源摘要及复验脚本；逐指令导出不入库 |
| `reverse/raw/` | 保留原始探针源码；交叉反汇编及历史测量输出存本地归档 |
| `reverse/sdk/` | 用于交叉核对的 SDK 头文件和少量源码摘录 |
| `reverse/nuttx-sim/` | SIM 配置和验证记录；历史诊断构建产物另存本地归档 |
| [reverse/migration/](reverse/migration/README.md) | 历史迁移清单及停用的迁移、文档同步、业务尺寸探针 |
| [tooling/scripts/](tooling/scripts/README.md) | 分析、ROM 打包、QEMU 模型、模拟运行及验证脚本 |
| [tooling/firmware-modules/](tooling/firmware-modules/README.md) | 实验载荷、链接脚本、APX1 加载器、OTA 和诊断模块源码 |
| `evidence/` | 本机私有实验输出、QEMU/REA/Ghidra 会话；不随 Git 分发 |
| `reverse/rehost/` | 本机应用重宿主生成物；不随 Git 分发 |

## 阅读与复现

- [研究索引](reverse/reports/ap01/README.md)：按版本和主题查找证据。
- [外部程序打包进 ROM](reverse/reports/ap01/design.md)：基线、编译、链接、注入、资源与镜像校验。
- [工具说明](tooling/scripts/README.md)：现用命令与环境要求；命令从仓库根目录执行。
- [0041 逆向交接](reverse/reports/ap01/0041-handoff.md)：原厂上层恢复与 QEMU 缺口。
- [0031 槽尾版实机记录](reverse/reports/ap01/knowledge/0031-tail-physical-success-20261018.md)及[2026-10-19 镜像准入记录](reverse/reports/ap01/ota-image-admission-20261019.md)：已记录的单次实机结果，不代表其他候选均可安装。

Git 检出不包含全部运行证据、工具链或第三方依赖。RISC-V 工具链、WSL/QEMU、NuttX/LVGL、REA/Ghidra 和只读上游材料按各实验需要另行配置。文档中的历史命令不代表已在当前机器重跑。

2026-10-24 起，逐指令 JSON、整段反汇编、重复工具导出及构建输出取消 Git 跟踪，并从本地提交历史清除。生成 JSON 仍保留在本地项目原路径，供研究和复验使用；其他输出按本地归档解释。Git 保留结论、合同、原件身份和复验源码。规则及归档位置见 [分析材料说明](reverse/analysis/README.md)，处理记录见 [仓库清理](reverse/reports/ap01/repository-cleanup-20261024.md)。

## 证据边界与来源

原厂字节、源码标签、静态推断、模拟结果和实机结果分别记账。0041 原厂代码已在必要 Mock 下运行部分初始化和 OTA 往返；原厂完整主界面、真实无线网络、Boot2 回滚和掉电恢复仍不能由模拟结果推出。NuttX SIM 的界面重建也不等于整 ROM 已在真实硬件运行。

日志、反汇编、JSON 导出和迁移清单保留生成时的路径、名称和哈希；它们是冻结证据，不作为当前目录或外部产品需求的定义。历史文档中的缺失材料会明确标注，不能据此声称当前仓库包含该证据。

原厂 ROM 及资源、第三方源码和本仓库自有内容的归属见 [NOTICE.md](NOTICE.md) 与 [LICENSE](LICENSE)。账号、密钥和私有会话不提交。
