# 历史成果提交与已结束任务清理（2026-10-25）

历史遗留成果及流程文档已在本地提交 `4dd198e`：123个文件，包含研究报告、复验源码、必要合同、索引与管理/流程说明；三份NuttX日志取消跟踪，本地文件保留。未推送。

54份新增Python复验脚本通过语法解析，2份新增合同JSON可解析，暂存差异格式检查通过。仅修正两份脚本末尾空行，没有执行研究脚本、固件、构建、模拟器或设备操作。

清理时逐树确认任务会话最后生命周期事件为 `task_complete`，任务提交为主树祖先，tracked/untracked状态干净且ignored无遗留；既有转存清单中的55份中间产物在主树逐文件SHA256一致。重新核对上述条件后，以不带force的 `git worktree remove` 移除24个任务树，并用 `git branch -d` 删除对应已合并分支。所有目标绝对路径均限定在本批 `ap01-s` 根目录下。清理后再次核对主树55份中间产物哈希及三份本地日志仍存在。

清理计划、逐树停止事件、提交SHA、转存哈希及操作结果保留在本地主树 `reverse/analysis/repository-cleanup-20261025/plan.json` 和 `results.json`，按分析生成物规则忽略。

## 已清理任务

| 分支 | 提交 |
| --- | --- |
| `codex/app-event-review-01-20261025` | `5365b64ee958` |
| `codex/app-event-research-01-20261025` | `1d7890db5a62` |
| `codex/app-named-property-review-01-20261025` | `e2742cd5f1a6` |
| `codex/app-named-property-research-01-20261025` | `58cd281071fe` |
| `codex/app-network-research-03-20261025` | `bc4ed028de4a` |
| `codex/app-network-review-04-20261025` | `d646b3c2dd39` |
| `codex/app-ota-review-03-20261025` | `06a5197e4467` |
| `codex/app-ota-research-03-20261025` | `3972bfa0277a` |
| `codex/app-property-review-01-20261025` | `f4822d506443` |
| `codex/app-property-research-01-20261025` | `bfed293a5b32` |
| `codex/app-publication-review-01-20261025` | `3921359e57a7` |
| `codex/app-publication-research-01-20261025` | `b2c1453681af` |
| `codex/app-report-config-review-01-20261025` | `77965fe26dca` |
| `codex/app-report-config-research-01-20261025` | `1890c41d135e` |
| `codex/app-rpc-action-review-01-20261025` | `26ae6245f997` |
| `codex/app-rpc-action-research-01-20261025` | `9f9220cab18f` |
| `codex/app-rpc-property-review-01-20261025` | `0e2e312b1676` |
| `codex/app-rpc-property-research-01-20261025` | `72a10cb66106` |
| `codex/app-rpc-subscription-review-01-20261025` | `b6f6f7f6a493` |
| `codex/app-rpc-subscription-research-01-20261025` | `9dc5fd4af492` |
| `codex/app-subscription-review-01-20261025` | `639119ec3a49` |
| `codex/app-subscription-review-02-20261025` | `389c58014df0` |
| `codex/app-subscription-research-01-20261025` | `64326568681c` |
| `codex/app-subscription-research-02-20261025` | `97b1af482451` |

## 保留任务

计划快照中另13个任务树未纳入清理：9个任务分支尚未合并，1个预调研任务和3个新复核任务仍在执行。新复核分支虽从主树基线创建、基线已在主树历史中，但不因此视为任务完成；其未提交/忽略产物及工作区全部保留。后续状态由运行中的管理窗口维护，本次不合并待验收成果，不中断或启动研究。

| 分支 | 保留原因 |
| --- | --- |
| `codex/app-ddf-review-01-20261025` | 提交尚未合并，保留待验收成果及中间产物 |
| `codex/app-ddf-research-01-20261025` | 提交尚未合并，保留待验收成果及中间产物 |
| `codex/app-mcu-ota-review-01-20261025` | 提交尚未合并，保留待验收成果及中间产物 |
| `codex/app-mcu-ota-research-01-20261025` | 提交尚未合并，保留待验收成果及中间产物 |
| `codex/app-ot-integration-review-01-20261025` | 仍在执行或未确认结束 |
| `codex/app-ot-integration-research-01-20261025` | 提交尚未合并，保留待验收成果及中间产物 |
| `codex/task-prep-research-01-20261025` | 仍在执行或未确认结束 |
| `codex/app-rpc-property-review-02-20261025` | 提交尚未合并，保留待验收成果及中间产物 |
| `codex/app-rpc-property-research-02-20261025` | 提交尚未合并，保留待验收成果及中间产物 |
| `codex/app-serial-downstream-review-01-20261025` | 仍在执行或未确认结束 |
| `codex/app-serial-downstream-research-01-20261025` | 提交尚未合并，保留待验收成果及中间产物 |
| `codex/app-serial-uplink-review-01-20261025` | 仍在执行或未确认结束 |
| `codex/app-serial-uplink-research-01-20261025` | 提交尚未合并，保留待验收成果及中间产物 |
