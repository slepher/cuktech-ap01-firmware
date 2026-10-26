# 仓库拆分（2026-10-26）

来源：`cuktech-ap01-firmware`，拆分基点 `a2738ce8b92742a4e8ad7bbb7575514021e73f8d`。

- 固件仓库拥有 `tooling/firmware-modules/`、构建/打包/诊断工具及 ROM 构建输入；0041 原厂 ROM 保留。
- 逆向仓库拥有 `reverse/`、研究工具、`evidence/` 和 `checksums/`，仅迁入 `roms/0041/`。
- 保留研究目录内部的相对层次，区分 reports、analysis、raw、sdk、rehost、evidence，避免冻结证据互相失联。
- 本地中间产物随目录直接迁移；按用户要求未计算迁移哈希。Git 忽略规则继续生效，私有会话、工具安装和大产物不提交。
- 184 个含 0031 的完整镜像/Flash 快照留在固件仓库 `roms/0031/reverse-archive/<原相对路径>`；原有 `roms/0031/` 也未迁入。历史小型载荷、报告、源码仍保留作对照。
- 迁移清单见逆向仓库 `checksums/split-20261026.local.json`（本地忽略），记录原路径、归属和适配文件，不作为运行验证结果。
- 历史报告/导出中的绝对路径、哈希与提交号保留生成时含义；新研究入口的仓库根路径已适配。旧清理归档 `cuktech-ap01-firmware-archive-20261024` 保持原位。
- 本次新仓库为独立本地 Git 仓库，迁入源码建立初始快照，原提交历史仍由固件仓库持有；未创建远程或推送。

推荐相邻放置两个仓库：`cuktech-ap01-firmware/` 与 `cuktech-ap01-firmware-reverse/`。固件构建使用本地原厂 ROM；研究工具需要构建器时引用相邻固件仓库。

## 0041 平台依赖复验

默认 `build-firmware-0041.py` 的编译、链接、打包输入全部位于本仓库；外部只需 Python 和 RV32 GCC 工具链。`--app-config` 显式接入 App 源码与声明式配置，仍由固件仓库统一编译、审计、链接和打包；App 原有命令只保留转发入口。`--app-source-dir` 仅兼容已有产物。平台启动使用空 App 回调也能提供设备码鉴权的维护/OTA/诊断与 Wi-Fi 服务。

- Wi-Fi 主机测试改用本仓库 ArduinoJson 与 String 适配头；兼容旧命令的 `--app-repo` 参数已不读取任何 App 文件。
- unsigned-OTA 回归在临时目录生成自身候选，不读取逆向仓库的历史候选或依赖；Unicorn 指令执行检查是当前 Python 环境中的可选项。
- `/resource/codex-status` 是设备上已有维护/槽位事务的兼容存储目录，VFS 会按需创建，不要求 App 存在。保留该名称以维持已有事务记录可读。
- `application/vnd.codex-status.frame` 是共享 HTTP 传输中的可选 App 线协议，平台维护路由返回 JSON；既有 ROM 的 `AP01APP1` 标记和 App ABI 1 同样保留兼容含义。平台单独使用 ABI 2，不读取 App 私有布局。
- `test_maintenance_app_0041.h` 及维护测试中受 `AP01_MAINTENANCE_ONLY_TEST` 控制的 App 分支用于显式集成测试；平台维护测试可用 `AP01_MAINTENANCE_ONLY_TEST=1` 单独构建。文档中的研究链接仅为证据引用。

`test-platform-independence-0041.py` 将构建必需输入复制到无相邻仓库的新目录，再运行完整构建与 ROM/OTA 检查。它不复制历史构建产物，也不访问设备。
