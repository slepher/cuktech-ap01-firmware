# AUT3 集合事务日志

2026-11-04：D3 日志编码与存储层已实现，开机选择器已实现并验证，生产文件启动组合、下载续传、连续健康观察与重启安排尚未接入。AUT3 引用完整 [AMF3 集合](app-manifest-v3.md)，不复用 AUT2 的单包含义。CRC 只检查存储损坏，不提供授权或包真实性证明。

## 字节合同

两个文件 `/resource/app-store/update.0`、`update.1` 各恰为 320 字节，所有整数小端；禁止直接保存 C++ struct。未列出的字节必须全零。记录文件格式版本为 2，与 AUT3 中的协议代号分开。

| 偏移 | 长度 | 含义 |
| --- | --- | --- |
| 0 | 4 | ASCII AUT3 |
| 4 / 8 / 12 | 各 4 | 格式版本 2 / 长度 320 / 阶段 |
| 16 | 8 | 非零日志序号，每次持久写入加一，禁止回绕 |
| 24 / 32 | 各 8 | 旧 / 候选集合版本序号 |
| 40 / 48 | 各 8 | trial / rollback 消耗时的 boot_id |
| 56 / 57 / 58 | 各 1 | trial 次数 / rollback 次数 / cleanup_pending，均为 0 或 1 |
| 59 / 60 | 各 1 | changed_mask / ready_mask |
| 64 | 8 | 本次变更包的总字节数 |
| 72 | 4 | 错误码，0 表示无错误 |
| 80 | 16 | 非零事务身份 |
| 96 | 6 | 设备 MAC |
| 104 / 136 / 168 | 各 32 | 旧 Manifest / 候选 Manifest / 请求参数指纹 |
| 200 | 65 | principal，1–64 个可见 ASCII 字符，NUL 终止，余量全零 |
| 268 | 32 | 按候选 ID 索引排列的 8 个 uint32 已确认接收偏移 |
| 316 | 4 | 前 316 字节的 CRC32 |

旧集合版本为 0 且摘要全零只表示初始未安装；候选版本非零且大于旧版本，摘要非零且不同于旧摘要。非零版本的空 AMF3 同样是合法集合。changed_mask 按候选 Manifest 的 ID 排序索引标记新增/改包，ready_mask 是其子集；删除条目不占包位，因此纯删除允许两个 mask 和 changed_bytes 都为零。复用包仍须通过完整集合预检。存储层只验证位图、字节总量下界与阶段一致性，安装服务必须对照两个真实 Manifest 验证变化集合及精确字节总量。

## 阶段与围栏

阶段编号依次为 Receiving=1、Ready、SwitchPending、TrialStarted、RollbackPending、RollbackStarted、Succeeded、FailedRolledBack、RecoveryRequired、Cancelled。

正常路径为 Receiving → Ready → SwitchPending → TrialStarted → Succeeded。所有变更包 Ready 后才能离开接收阶段进入 Ready。SwitchPending/TrialStarted 失败转 RollbackPending → RollbackStarted → FailedRolledBack。恢复也失败则进入 RecoveryRequired。Receiving/Ready/SwitchPending 可在候选未执行且重启回调未调用时取消。各非终态均可转 RecoveryRequired。

trial/rollback 次数分别只允许在进入相应 Started 时从 0 增到 1，必须同时记录非零 boot_id，二者不可相同；同事务后续记录不能换 boot_id 或重置次数。允许候选预检失败、尚未运行 trial 就进入 rollback。RollbackPending 起必须有非零错误，后续保持首个错误。每事务的 principal、请求指纹、集合摘要/版本、变更位图和字节总量不可改变；Ready 位只能增加。

只有 Succeeded、FailedRolledBack、Cancelled 且 cleanup_pending=0 可开始不同事务，新事务必须从 Receiving/ready_mask=0 开始；其旧摘要和版本必须等于前一事务确定的活动集合。RecoveryRequired 不自动接受新事务，需要独立的显式恢复策略。初始空集合失败完成回退后可再次安装。首次创建日志前的当前集合验证属于安装服务责任。

## 持久化与未知结果

单一平台事务 worker 独占写入。VFS write 必须包含同步；写交替槽后检查 close，再重新打开、核对长度、逐字节读回并检查 close。任何失败返回 Unknown；禁止后续 save，current() 返回空，必须重新 load 解决不确定性。不能凭写入返回值、旧内存记录或客户端丢 ACK 推断成功。

读取时两文件均不存在才是 Empty。截断/坏 CRC 可用另一个有效槽恢复；存在性、打开、长度查询、读取或关闭的 I/O 错误不冒充不存在。两个有效槽必须相同序号且字节一致，或序号相邻且阶段转换合法；相同序号内容不同、序号跳跃、非法转换、设备 MAC 不同都拒绝。未知 AUT3 格式版本明确 Unsupported，不能退回较旧记录猜测。

旧路径 `/resource/codex-status/app-update.0|1` 存在时返回 Legacy，不自动迁移或删除。新路径中读到完整 AUT2 标识同样 Legacy；其他错误长度拒绝或按坏槽恢复。维护/救援通道必须保留，由上层公开错误，而非继续安装。

## 验证与边界

运行：

```sh
python3 -B tooling/scripts/test-app-set-journal-v3.py --out build/app-install \
  --package build/app-install/d2-business-resume-01/app.apx2 \
  --manifest build/app-install/d2-resume-set/set.amf3 \
  --peer build/app-install/d2-peer-beats-02/app.apx2 \
  --tool-prefix build/s1/toolchains/xpack-riscv-none-elf-gcc-12.5.0-1/bin/riscv-none-elf-
```

输出目录须预先存在。ASan/UBSan 下覆盖两槽 640 个截断写入点、逐字节损坏、修复 CRC 后的保留字段污染、完整写入丢 ACK、I/O/关闭错误、记录冲突、成功/整体回退、首装空集合回退及新事务围栏；同时交叉编译 RV32。报告 `build/app-install/set-journal-v3-report.json` 记录源码指纹。模型不证明硬件掉电持久性，也未覆盖尚不存在的包/Manifest 发布、开机选择和垃圾回收链路。

## 开机选择器（尚未接生产组合）

`Ap01SetSelectorV3` 是单 worker、每 boot 一次的选择器。调用前必须成功 load 日志；未安装日志仅返回 Maintenance，不隐式信任固定路径文件。调用者提供整集预检回调，该回调只能验证并暂存不可变包，禁止执行 App。选择成功后才能把暂存内容发布给 UI 加载器。

- Receiving/Ready/Cancelled/FailedRolledBack 选择完整旧集合；Succeeded 选择完整新集合。
- SwitchPending 先预检候选，随后持久 TrialStarted 和 boot_id，再返回 Trial 授权。预检失败先记 RollbackPending，再预检旧集合并持久 RollbackStarted。
- 前一 boot 的 TrialStarted 或 RollbackPending 只选择旧集合，且必须先持久消耗 rollback。相同 boot_id 不再次执行，防止同 boot 重建控制器造成在线切换。
- RollbackStarted 在另一 boot 被读到则持久 RecoveryRequired，返回 Maintenance；旧集合预检失败也进入维护。
- 选择返回后失败：trial 只持久安排 RollbackPending 并返回需要重启，不能本 boot 加载旧集合；rollback 失败持久 RecoveryRequired。实际安排重启和失败回执仍待上层实现。
- `accept()` 只能由上层完成全集合连续健康观察后调用，持久 Succeeded/FailedRolledBack 和 cleanup_pending=1。正常成功不要求再重启。当前接口不自行证明健康，不自行开放业务写许可。

选择器测试覆盖正常成功、候选预检失败、trial 消耗写入丢 ACK、trial 意外重启、执行失败安排回退、同 boot 拒绝重选、回退成功、回退再重启/执行失败、旧包缺失和空日志拒绝隐式引导。当前合计 11117 项断言，包含前述日志故障覆盖；生产文件启动器仍走 D2 固定路径，不能用这些测试宣称 D3 端到端完成。

## 真实文件暂存接入

`Ap01NativeAppFileBootV3::stageSelected(selector)` 已连接选择器与真实 AMF3/APX2 预检。Manifest 路径由摘要确定为 `/resource/app-store/manifests/<64 位十六进制内容摘要>.amf3`；同时验证文件内摘要及集合 sequence，不接受摘要正确但日志版本错误的候选。包仍使用既定按内容摘要命名的路径。

预检在 worker 私有暂存中完成；selector 的持久消耗成功返回后，才通过 release 发布给 UI。Unknown/Maintenance 会丢弃暂存，不留可执行入口；首次安装回退到版本 0 的空集合不读文件、不执行 App。候选预检失败允许重新暂存完整旧集合，因为尚未发布或执行任何代码。原固定路径 `stage()` 保留用于 D2 引导和模型，原生 hook 尚未切到事务入口。

`test-native-app-set-v3.py` 新增真实包集成场景：持久 trial 后 UI 执行、消耗写入丢 ACK 阻止执行、Manifest 版本不符和候选缺失回退空集合。覆盖的是实际包校验与替身 App 入口，不能替代 james.local Docker 中真实 RV32 入口验证。连续健康观察、持久确认后的写许可与重启执行仍未接入。

## 连续健康确认与写许可

选择器在发布 UI 加载前记录观察起点，重复 beginObservation 不重置预算。首次全集合 Healthy 必须在 10 秒内出现，随后连续健康 30 秒，整段预算最多 40 秒。未健康状态（含 WindowAbsent）或两次观察间隔大于 1 秒打断连续计时；超时/故障通过既有失败裁决持久安排回退或维护。uint32 毫秒差处理正常时钟回绕。

事务 worker 调用 `healthSelected` 读取独立监督快照，不直接执行 App 健康回调。只有连续观察通过且 Succeeded/FailedRolledBack 持久写入及读回成功才开放共享写门；Unknown 保持关闭。成功不安排第二次重启，cleanup_pending 保留给后续垃圾回收。持久成功后新出现的监督故障会关闭写门并返回维护，不把已提交集合在线回退。

宿主集成测试检查两 App 在前 30 秒均不可写、确认落盘后同时可写，以及后续 UI 停滞撤销写许可。日志/选择器累计 11232 断言还覆盖启动超时、健康中断、观察缺口、确认写入丢 ACK 与时间回绕。生产 worker 调度、重启执行/失败回执、HTTP 状态和完整 RV32 模型链仍待接入。

## 有界重启安排

`Ap01AppRebootV3` 由单事务 worker 请求/派发，独立维护读者可观察状态。healthSelected 只在 failed() 成功持久 RollbackPending 且共享写门已排空后 request。延迟 250 ms 后调用平台回调一次；5 秒内本 boot 仍存在则锁存 Failed，包括事务 worker 未派发或回调阻塞。重复 request/tick 不重置期限、不再次调用；空回调直接 Failed。实际软重启仍待原生 hook 传入既有 `ap01_native0041::reboot`。

`app_runtime.reboot_state` 返回 idle/pending/invoked/failed；automatic_reboot 只在 pending/invoked 为 true，不把已调用等同于已重启。HTTP 此时读取原子状态和监督快照，无 App 调用。事务结果中的具体重启错误码、原生入口以及 commit 分支仍待接入。

测试累计 11252 断言，新增单次调用、延迟边界、线程未派发超时、空回调、时间回绕和早于 request 的时间采样；维护 HTTP 回归验证 pending/failed 状态，不代表真实 ROM 重启已执行。

## 原生入口接入（2026-11-04）

上述“原生 hook 尚未接入”记录由本节接续：原生 `start` worker 在维护监听就绪后读取 Wi-Fi MAC，load AUT3，构造该 boot 的 selector，调用 stageSelected，并每 100 ms 处理 healthSelected 和重启派发。原本的固定 `/current.amf3` 不再作为生产引导来源；空日志或损坏/旧格式保持维护，不猜测现有包。MAC 获取/解析失败也不加载。独立监督线程继续运行。

派发回调已绑定既有 `ap01_native0041::reboot()`；失败锁存可从维护状态读取。journal_result 与 journal_phase 用一个原子字发布，读取者不会拼出跨时刻的阶段/错误组合。状态是诊断摘要，完整安装事务回执仍待 D4。

完整候选 `build/app-install/d3-platform-01.bin`，6914856 B，SHA256 `193922c89ae69bc87bb1b321ab4456c7b1d3abeaf41e4038c70f2fb9ad849e70`，镜像验证和跨仓边界检查通过。最终 ELF 保留 journal load/save、selector select/observe/accept、stageSelected/healthSelected 符号；不是仅编译后被裁掉的代码。原生 worker 静态自身栈帧 496 B，不代替完整调用链或运行高水位证明。hardware backend 仍拒绝执行，候选不可部署；真实 RV32 事务链的 Docker QEMU 验证、下载/commit/清理、维护写协调及完整客户端尚未完成。

## 真实 RV32 执行证据

`d3-journal-run01` 在 james.local Docker 两基址通过：预置 SwitchPending → 实际 AUT3 消耗 trial → 按摘要暂存/加载两个真实 App → 连续健康 → Succeeded 写入/读回 → 业务 worker 观察许可并初始化一次。三线程冻结检查后撤销写门。详见 [QEMU 记录](../project-workflow/ap01-app-update/s1-qemu-james.md)。未执行真实 CPU 重启或 Flash 掉电，未实现上传/commit；不能以此勾选整个 D3/D4。

## 多包续传进度（格式版本 2）

原 320 B 记录的保留区加入 8 个独立 received 偏移，记录长度不变。每个偏移仅对应 changed_mask 中的候选条目；其他条目必须零，总接收量不超过 changed_bytes，同事务只能增加、离开 Receiving 后冻结。新事务从全零偏移开始。未部署的 AUT3 格式 1 草稿返回 Unsupported，不能把旧保留区自动当作已验证进度；以前的 QEMU/候选记录仅证明当时的格式 1 链路。

`Ap01SetDownloadV3` 使用已验证且已持久发布的候选 Manifest，将 index、总长度、事务 ID 与 AUT3 摘要/序号核对。每块 1–1024 B，严格顺序；已确认范围内的重复块逐字节比较，不跨过已确认边界。暂存文件为 `/resource/app-store/incoming/<transaction 32hex>-<index>.part`，不得由调用者提供路径。

append 前读取真实大小并比较未确认尾部，拒绝不同内容或超界；写入（含零长度重新同步）和 close 成功后，重新打开校验长度/字节，再持久更新该包偏移。潜在写入后的任何失败冻结下载器为 Unknown；须先 journal.load、重新验证 Manifest，再重建下载器继续。没有未知文件截断/删除。目录创建、空间预留、授权在 begin 层完成，当前还未接入；完整 APX2 校验、发布、Ready 位也尚未实现。

故障测试新增 512 个数据截断点与 320 个进度记录截断点，恢复后比较/补写再提交；两包偏移独立，重复不同字节及跨事务拒绝。日志/选择器/下载合计 53108 断言，ASan/UBSan 与 RV32 编译通过。该测试为字节持久模型，不代替 Flash 掉电。

## APX2 发布与单包 Ready

`ready(transaction,index,dataVersion)` 已实现：校验暂存文件的完整 APX2、精确包长度及 Manifest 全部包字段；复用 `ap01CheckManifestPackageV3`，与开机全集合预检同规则。rename 到 `/resource/app-store/packages/<content-digest>.apx2` 后重新打开并完整校验，再保存 received/ready_mask。只改该包位，不自行将全集合阶段推进为 Ready；全集合/复用包预检仍属于 commit 前置。

若目标已存在，验证其内容后复用，不覆盖、不删坏目标；可恢复 rename 已成功但 ACK 丢失或 ready_mask 尚未写入的情况。潜在变更后失败一律 Unknown 并冻结当前下载器；重新 load 日志后可重新校验目标并补 Ready 位。完成 Ready 的包不再接受 chunk 修改；其余包仍可接收。未引用 incoming 文件的清理由后续 GC 负责，当前不提前删除。

测试使用真实业务包上传，覆盖正常发布、rename 失败/成功丢 ACK、Ready 日志截断、暂存包损坏和同摘要目标损坏；恢复后二次 ready 不重复 rename。当前累计 66439 断言，ASan/UBSan 与 RV32 通过。单个包 Ready 不代表完整事务已 commit，begin 授权/空间/Manifest 发布及全集合围栏仍待实现。

## 全集合 commit 核心

`Ap01SetCommitV3` 核对事务身份、expected_current_manifest 摘要/集合版本，以及候选 Manifest 摘要/版本。变更位不得越过候选数量；全部变更包须 Ready、received 等于其精确包长度，变更包总量须等于 changed_bytes。随后预检完整集合，包含未变化的复用包，不能只依赖 Ready 位。

预检通过后关闭共享写门，等待已有写 lease 排空。返回 Busy 时由单事务 worker 继续推进；5 秒未完成则锁存 DrainTimeout，写门保持关闭，不能默默重启或无限等候。排空后依次保存 Ready、SwitchPending，均要求日志同步与读回成功；仅最后一步成功才 request 一次延迟重启。日志 Unknown 不安排重启。SwitchPending 的重复 commit 核对相同身份后返回原安排状态，不重写日志、不重置重启期限；超时返回 RebootFailed。

该类尚未接 HTTP 或原生安装服务。调用者须先完成 principal/MAC 授权，并持有平台维护操作锁，防止并行 OTA/Wi-Fi 操作或健康 worker 重新开放写门；不能把当前函数本身当作这层协调已经实现。begin 的旧/新 Manifest 验证与持久发布仍是前置工作。

真实业务包测试覆盖 preflight 拒绝、未全部 Ready、旧摘要冲突、写 lease 阻塞及超时、Ready 写入截断、SwitchPending 完整写入丢 ACK、重载恢复、重复 commit 不增序号与单次重启、重启未发生的失败回执。累计 66571 项断言、ASan/UBSan 和 RV32 通过；批量更新的实际整链仍待安装服务和模型验证。

## begin 集合规划与空间边界

`ap01PlanSetBeginV3` 是纯规划函数，不写文件或日志。输入是已解析验证的旧、新 Manifest；初始空安装传 old=null。平台按 app_id 匹配旧条目，再按包摘要判断新增/变化，产生候选 ID 排序下的 changed_mask 和 changed_bytes。插入条目导致索引改变时不误判原有包；纯删除不需要下载位。初始无日志不能声称已有旧集合。

请求指纹用固定域 `AP01-SET-BEGIN-3`、MAC、事务身份、零填充 principal、旧/候选摘要和显式小端序号计算 SHA256。相同事务同指纹返回 Replay 并原样返回当前 phase/sequence/received/ready；不因剩余空间变少而重做 admission、不清零上传进度。参数变化 Conflict；前一事务未结束或 cleanup_pending 未清零 Busy。新事务必须承接确定的活动摘要/版本。

首次 admission 保守预算为所有变更包字节 + 四个最大 Manifest（3584 B 各，包含旧/候选及临时副本）+ 两个 320 B 日志，另扣调用者给定的维护预留。不假设去重节省空间。此处是空间需求检查，尚不是与 OTA/Wi-Fi/VFS 其他写者协调后的实际预留；安装服务必须在维护操作锁内查询/预留空间、持久发布所有被引用 Manifest，最后 journal.save(plan)。当前没有提前保存 Receiving。

测试覆盖空集合首装、精确空间边界、上传中重复 begin 保留进度、身份参数冲突、忙事务、单更/批更/插入移位/纯删除、清理未完成和旧摘要冲突。总计 66623 项断言及 RV32 编译通过；完整 begin 发布/授权流程仍待接入。

## Manifest 持久发布与 begin 写入（2026-11-04）

`ap01PublishManifestV3` 先解析/验证 AMF3，再按其内容摘要生成 `.part` 和 `.amf3` 文件名。已存在临时文件仅在其全部字节与不可变输入前缀一致时续写，不截断未知文件；分块写入、同步和关闭后完整读回比较，再 rename，最后再次完整读回。已存在最终文件只允许逐字节一致复用，不覆盖坏目标。任何可能变更后的错误返回 Unknown。调用者不得在 Unknown 时创建引用它的日志。

`ap01BeginSetV3` 已将上述发布接入：解析旧/候选集合，规划/核对重放，查询 `/resource` 空间并扣维护预留，准备 app-store/manifests/packages/incoming 目录，发布旧/候选 Manifest，最后保存 Receiving。Replay 不重新查空间、不写文件、不清空进度。旧集合对象在堆上按需分配，避免把两份大 Manifest 放入原生 worker 栈。

测试覆盖实际双 App Manifest 的每个临时文件前缀恢复、损坏前缀/最终文件不覆盖、写入截断、rename 失败/成功丢 ACK；begin 验证空间不足无写入、目录失败/发布 Unknown 不提前写日志、重新观测后重试、低剩余空间下幂等 Replay。首次日志自身被截断且没有任何有效槽时仍返回 Corrupt 留维护，不猜测成 Empty。当前总计 72279 断言，ASan/UBSan/RV32 通过。

仍需原生安装服务在平台维护操作锁内调用此入口，提供已认证 principal/MAC 并阻止其他写者抢占预算。空间查询不是文件系统配额预留；当前没有关闭救援入口或宣称 OTA/Wi-Fi 协调已实现。完整客户端上传/commit、取消和垃圾回收仍未完成。

## 取消与重启竞态

`Ap01SetCommitV3::cancel` 复用同一事务 worker/维护操作锁。Receiving/Ready/SwitchPending：停止尚未派发的重启，持久 Cancelled+cleanup_pending；不删除文件、不自行恢复写门。重复取消不改序号。若原生重启回调已经调用（即使随后 5 秒超时），返回 RebootInFlight，不承诺可撤销已经发出的硬件动作。

TrialStarted：关闭写门、等待已有写入排空，持久 RollbackPending（取消错误 7），再单次安排重启；不能在本 boot 装回旧集合。RollbackPending 重试复用原安排，超时明确 RebootFailed。Succeeded 不接受撤销；恢复失败状态也不假装取消成功。

取消写入 Unknown 时保持重启停止，需要重载日志/查询原事务后才能继续。测试验证完整取消记录丢 ACK 后重载为 Cancelled，而截断取消记录重载仍为 SwitchPending；两者在未重新裁决前都不自动重启。超时观察使用 compare-exchange，避免旧观察覆盖已经取消的状态。

Receiving、Ready、SwitchPending、TrialStarted、Succeeded、重启已调用、取消丢 ACK/截断和重复请求已覆盖，累计 72383 断言及 RV32 编译通过。cleanup_pending 仍须由引用安全的 GC 清除；HTTP 取消入口及原生操作锁尚未接入。

## 事务范围内的引用安全清理

`ap01CleanupSetV3` 仅接受 Succeeded、FailedRolledBack、Cancelled，并要求输入的已验证旧/候选 Manifest 摘要与版本匹配日志。RecoveryRequired 不自动清理。cleanup_pending=0 重试无写入。

删除前先将同一终态和 cleanup_pending=1 保存到另一日志槽并读回；这样两个槽都指向相同最终选择，即使后续清理完成记录被截断，也不会回退到仍需淘汰包的 TrialStarted/回退中阶段。屏障写入失败时不删除任何文件。

Succeeded 保留候选集合，回退成功/取消保留旧集合；按包摘要比较，而非按 ID 或位置。任何仍被保留集合引用的共享包都不删除。只删除本事务淘汰集合的独有包、8 个已知 incoming 文件和旧/候选 Manifest 的临时文件，逐个检查删除后不存在；最后保存 cleanup_pending=0。删除失败/丢 ACK 或完成日志 Unknown 不假称完成，重载后可以幂等再做。

最终 Manifest 元数据暂保留供事务回执/重放核对；本实现不是目录扫描。VFS 当前没有目录枚举接口，因此未被日志记录的孤儿 Manifest、较早事务遗留临时文件的扫描回收仍待平台私有接口实现，不能将本函数标为完整 GC。维护操作锁、安装服务调用仍未连接。

目录接口证据入口：`tooling/scripts/audit-native-directory-0041.py --rom <固定0041 ROM> --report <报告路径>`。脚本固定 ROM SHA256、`0xa01bf590` 操作表和四个候选目录回调的完整函数字节摘要。当前仅为静态审计，`callable_abi_verified=false`：读取回调 `0xa00448c4` 内的自定义指令及输出布局须先在 QEMU 中用边界哨兵验证，再接入平台私有目录枚举；不得根据宿主 `dirent` 布局猜测。此证据不替代缺失的历史 `0041-littlefs-abi.json`，也不证明孤儿 GC 已实现。

72983 项断言覆盖三种终态、双槽屏障截断、删除失败/成功丢 ACK、完成记录丢 ACK、共享包保留及 incoming 清理；测试 remove 回调逐次检查两槽都是终态后才允许删除。ASan/UBSan 与 RV32 编译通过，不代替 Flash 掉电。

## 宿主完整事务组合验收

`test-app-set-journal-v3.py` 新增四条组合路径，每条先从空日志实际 begin/双包上传/发布/commit 完成首装，再做单更 A 或批更 A+B，分别成功确认或试运行中断后整集回退。直接调用生产 begin/download/commit/journal/selector/cleanup，持久文件通过同一故障 Disk 保存；commit 重试不增序号，正常每次只派发一次重启请求，重新 load 日志模拟下一 boot 的裁决。

输入为真实业务和 peer APX2；第二版本保留代码负载，仅修改包版本字段后重新计算 APX2 摘要，并更新 AMF3 版本/包摘要/依赖摘要与整体摘要。验证的是实际格式校验和事务组合，不是新版业务行为。单更 A 明确检查 B 摘要、文件字节及零上传偏移不变；回退选择整个旧 Manifest，清理后保留集合完整预检通过，淘汰 A 文件不存在。两包未齐 Ready 时 commit 拒绝。

累计 91452 项断言、ASan/UBSan/RV32 通过，报告包含业务包/peer/Manifest 输入 SHA256。此为宿主事务重建，不执行 App 指令、完整 ROM 或 CPU reboot；HTTP、原生维护锁/服务接入、孤儿扫描和 Bridge 仍不由这些测试证明。
