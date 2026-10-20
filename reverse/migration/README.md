# 历史迁移材料

`migration-manifest.json`、`migration-check.json` 保留原始来源路径及校验结果。`scripts/` 收纳原 `reverse/analysis/artifacts-ap01/` 中的迁移/文档同步脚本及原 `tooling/scripts/resource_budget.py` 业务尺寸探针，文件字节保持不变。

这些脚本是历史记录，不是当前工具入口：其中硬编码的目录、外部源码及输出位置属于原环境，不能在当前仓库直接执行。通用 ROM 打包方法见[打包说明](../reports/ap01/design.md)。

`checksums/SHA256SUMS.txt` 是历史全量归档清单，仍保留旧路径和原始摘要；本次移动不重写这份历史清单。当前 Git 文件位置以仓库树为准。
