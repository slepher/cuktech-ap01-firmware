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
