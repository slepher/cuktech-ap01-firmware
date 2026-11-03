# App 更新日志 AUT2

> 2026-11-03 设计修订提示：本文保留现有单包/旧 ABI 实现及历史验证，不能作为新多 App 重启切换合同。目标已改为复用现有多 App 宿主、直接 C 函数表、Manifest 集合事务与重启切换；见 [当前设计](ap01-app-update-design.md) 第 4–7 节及 [任务](../project-workflow/ap01-app-update/task.md)。APX2 入口/ABI、AUT2 日志和 HTTP 单包字段需显式版本化；相关实现尚未修改。正文中的待办及导入数量是当时记录，当前状态以 [状态总览](../project-workflow/ap01-app-update/status.md) 为准。

实现：`app_update_record_0041.{h,cpp}`。这是安装事务的持久化基础，尚未接入 HTTP、文件切换或启动执行器，不代表完整事务已完成。

两个私有文件 `/app-update.0` 和 `/app-update.1` 各 256 字节，仅存元数据。保存时覆盖非当前记录，写入同步后重新打开读回、逐字节核对，才更新内存中的已提交记录。包文件不在这两个记录内，没有新增 App A/B 槽。

| 字节偏移 | 内容 |
| --- | --- |
| 0–3 | ASCII AUT2 |
| 4, 8 | uint32 小端格式版本 1、长度 256 |
| 12 | uint32 phase，依次为 Receiving=1、Ready、SwitchPending、TrialStarted、RollbackPending、RollbackStarted、Succeeded、FailedRolledBack、RecoveryRequired、Cancelled |
| 16–23 | uint64 小端提交序号，非零，不回绕 |
| 24, 28, 32 | uint32 包总长、持久接收偏移、运行 generation |
| 36–38 | 各一字节 trialStarts、rollbackStarts、cleanupPending，均 0 或 1 |
| 40–55 | 非零事务 ID，16 字节 |
| 56–61 | 设备 MAC，6 字节 |
| 64–95, 96–127 | 旧/新包内容摘要；旧摘要全零表示首装，新摘要不能为空 |
| 128–192 | principal，1–64 字节可见 ASCII 加全零终止填充 |
| 252–255 | 前 252 字节的 IEEE CRC32，小端 |

未列出的字节必须为零。CRC 只检测损坏，不提供来源认证；调用方仍须鉴权并检查 MAC、事务 ID、预期当前摘要和 APX2 内容。

同一事务中包身份不可变，接收偏移不倒退，trial/rollback 启动计数不减少，每类启动最多一次。Ready 必须先进入 SwitchPending，TrialStarted 成功后才能进入 Succeeded；回退须经过 RollbackPending、RollbackStarted。成功/回退成功必须保持对应 generation。非终态不能换事务，cleanupPending 未清除也不能开始新事务。

写入失败、短写或读回失败均返回 Unknown；即便写入实际完成也不能凭错误重发下一状态。必须 load 重新选择持久记录。两个有效记录按序号选择；同序号但内容不同、序号间隔大于一、外设备记录均拒绝。仅一个记录有效时采用它，以恢复交替写入中断。两个记录都不存在才返回 Empty；损坏不能伪装为首次安装。

该恢复规则依赖底层“同步成功的数据跨断电持久”的约定；不保证任意事后介质损坏不会丢失最近状态。文件系统同步语义尚待实机验证。启动执行器必须在 TrialStarted/RollbackStarted 保存并读回之后才执行相应代码；加载后已消耗的启动不能再次尝试。当前日志不会自行启动、删除或改名包，不能替代启动选择、健康观察与掉电文件角色裁决。

## 检查

```sh
mkdir -p build/app-install/journal
python3 -B tooling/scripts/test-app-update-record-0041.py --out build/app-install/journal \
  --tool-prefix build/s1/toolchains/xpack-riscv-none-elf-gcc-12.5.0-1/bin/riscv-none-elf-
```

ASan/UBSan 覆盖逐字节记录损坏、状态字段边界、全部 256 个截断写入位置、写成功回执丢失、重启计数恢复、计数重置/中途新事务拒绝与外设备记录拒绝。RV32 编译通过。测试使用故障注入的内存文件系统；不声称验证真实文件系统耐久性。报告在 `build/app-install/journal/journal-report.json`。

## 下载接入

`app_download_0041.{h,cpp}` 将日志与 `/app-incoming.apx2`、APX2 校验器接通，由单个维护执行器独占调用。鉴权、MAC/当前 App 摘要与空间预算检查仍须由安装入口在 begin 前完成；当前尚未接入 HTTP。

begin 先提交 Receiving；不截断已存在的未知 incoming。重复事务校对完整身份后返回已有进度，不能倒退。新事务须等旧临时包清理完毕。
chunk 限 1024 字节，只接受当前连续偏移或完全位于已确认范围内的相同重复块。超前、跨越已确认边界或重复内容不同均拒绝。数据写入、同步、读回后才提交日志偏移。

断电可能留下比日志偏移长的包文件。重传时先比较已有重叠字节，仅追加缺失尾部，然后再次同步并读回；即使整个块已在文件中也要重新同步。这样既支持部分写入恢复，也避免“数据成功但日志回执未知”导致重复追加。`File::sync` 使用已有 VFS write 的零长度同步语义；0041 writeFile 本身每次都会调用 syncFile，真实耐久性仍待实机验证。

ready 要求收到全部字节、文件长度精确、APX2 目标/ABI/服务/预算/数据版本校验通过、内容摘要等于原事务，才提交 Ready。包损坏不能把事务推进到可切换阶段。日志 Unknown 会冻结后续包写入，直到 load 完成裁决。下载器不会自行启动或清理包。

```sh
mkdir -p build/app-install/download
python3 -B tooling/scripts/test-app-download-0041.py --out build/app-install/download \
  --package build/app-install/apx2/golden.apx2 \
  --tool-prefix build/s1/toolchains/xpack-riscv-none-elf-gcc-12.5.0-1/bin/riscv-none-elf-
```

宿主真实临时文件测试覆盖 161 种尾部截断/重启、相同重复块与冲突、包已持久但日志未写、日志写成功 ACK 丢失、同步错误、错误事务/越界、摘要不符及 Ready 重放。ASan/UBSan 与 RV32 编译通过。完整启动选择、文件角色切换、取消、清理和协议接入尚未完成。

## 启动选择与成功清理

`app_selection_0041.{h,cpp}` 使用同一日志与 APX2 校验器，按摘要在 current/incoming/previous 三个逻辑路径中查找包。文件名不是授权依据；候选试运行时可仍留在 incoming，旧包仍在 current，角色由日志确定。成功后才把选中包规范化为 current。整个过程不复制完整包，不增加固定 App 槽。

调用者必须持有平台更新互斥，并在 commit/select 前确认所有 App 任务与资源已停止排空。select 仅返回选择结果，不执行代码；不是查询 API，不能对运行中的 App 轮询调用。新启动使用生命周期执行器分配的新 generation。

- Ready 的 commit 提交 SwitchPending；重复 commit 不重写日志或重启。
- SwitchPending 找到完整新包后，先保存 TrialStarted、次数 1、generation，再返回 Launch。保存未知时不返回可执行路径。
- 重启/失败后遇到 TrialStarted，持久记录 RollbackPending；完整旧包存在时先保存 RollbackStarted、次数 1，再返回旧包。首装或旧包无效则进入 RecoveryRequired。
- 遇到已消耗的 RollbackStarted 进入 RecoveryRequired，不重复启动。
- Receiving/Ready/Cancelled 正常选择旧包；Succeeded 只选择新包；FailedRolledBack 只选择旧包。成功后新包缺失也不能暗中选旧包。
- observe 只接受正在试运行/回退的 generation 与摘要。入口须在 10 秒内就绪，事件循环、原厂调度、维护执行器三项计数每次采样均需推进，采样间隔不超过 1 秒，连续健康 30 秒才提交成功。总预算 40 秒；停滞或采样缺口重置连续窗口，资源失败、时钟倒退、入口就绪回退或超时为粘性失败。计数须来自固件实际观测，不能用 App 自报或 HTTP 流量替代。
- 成功先持久提交终态与 cleanupPending，再删除未选中包，将选中包改名到 current，重新核验后清除 cleanupPending。删除/改名失败不撤销成功；重启按摘要继续清理。文件改名成功但回执丢失可安全重试。

```sh
mkdir -p build/app-install/selection
python3 -B tooling/scripts/test-app-selection-0041.py --out build/app-install/selection \
  --package build/app-install/apx2/golden.apx2 \
  --tool-prefix build/s1/toolchains/xpack-riscv-none-elf-gcc-12.5.0-1/bin/riscv-none-elf-
```

真实宿主文件检查覆盖一次试运行/回退、重启、启动记录回执丢失、首装失败、身份不符健康拒绝、清理删除失败、改名回执丢失重放、重复 commit、成功后不回选。ASan/UBSan 和 RV32 编译通过，报告在 `build/app-install/selection/selection-report.json`。尚未连接真实执行后端、资源排空、业务写入冻结、健康观察、cancel 与 HTTP/CLI；这些仍是整体目标的未完成项。

### 健康判据更新

上一节“健康观察尚未连接”现明确为：计时与判据已连接选择器，真实固件计数源尚未接入。选择器只在 trial/rollback Launch 后建立内存态观察器；重启按持久次数处理失败，不能续用重启前的健康秒数。公开 API 不再提供直接成功提交入口。

`businessWritesAllowed(generation)` 限同一执行器调用：仅允许当前选中代际在 Receiving/Ready/Cancelled 或 Succeeded/FailedRolledBack 时写入；切换、试运行、回退、Unknown 和恢复态拒绝。目前尚未接入真实 App 全部业务写服务，不能宣称设备数据已全面冻结。

宿主选择测试扩展到 15 组流程，包括启动超时、三类计数各自停滞、采样缺口、时钟倒退、资源失败、错误摘要/代际、连续健康和业务写门。ASan/UBSan 与 RV32 编译通过。

## 取消与恢复后重装

`cancel()` 仍由同一执行器调用。Receiving/Ready 先提交 Cancelled 与 cleanupPending，再由 cleanup 删除 incoming，保留 current/previous。清理失败阻止新事务，但不影响旧 App 正常运行；成功后才清除 pending。重复取消不改序号、不重复启动。

SwitchPending/TrialStarted 的取消进入 RollbackPending，有旧包时后续 select 仍只启动旧包一次；试运行 App 必须先停止排空。没有旧包则进入 RecoveryRequired。已经进入回退或成功终态的取消仅返回原状态，不能重置次数或删除成功的新包。

RecoveryRequired 也记录待清理标志。cleanup 只清理失败 incoming，保留 current/previous，完成后允许显式新事务，因此首装失败不会形成“必须已有 App 才能重新安装”的依赖。无法确认旧包是否占用 incoming 时保留文件并报告 Storage，不擅自删除。

新增 7 组取消流程覆盖下载中、Ready、切换准备、试运行、首装失败、已成功、取消记录 ACK 丢失；另外验证清理失败阻止新事务、重放不增序号、回退中取消不重启、首装恢复后可重新建事务。选择器、下载器、日志宿主回归和 RV32 编译通过。维护 HTTP/鉴权与 CLI 尚未接入 cancel。
