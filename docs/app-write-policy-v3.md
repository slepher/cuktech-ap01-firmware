# ABI 3 集合业务写许可

状态：2026-11-04，集合文件门已实现，D3 持久授权与业务可写恢复尚未接通。默认只读；不是完整安装事务完成记录。

`Ap01AppWriteGateV3` 由共享平台持有，所有 App 的直接 VFS 在截断/追加打开、write（含零长度 sync）、mkdir/remove/rename 时获取同一写操作计数。操作返回后才释放计数；底层 VFS 合同要求 write 成功前已同步。普通读取与关闭不受该门限制。

平台单一事务执行器调用 `Ap01NativeAppSetV3::writes(false)`：先全局关闭新写入，再检查已开始操作；返回 false 表示仍需等待，不表示撤权未生效。重复检查成功后才可报告写入排空。旧的可写句柄每次 write 都重新检查该门。全体 App 共享一个许可，不逐个开放或关闭。

`writes(true)` 仅在集合已成功启动且无在途写入时开放；调用者还必须已完成 D3 持久成功记录，不能用本接口代替持久授权。单个 App 上下文无权改变多 App 集合许可，App C 表只能读 writes_allowed。生产固定 Manifest 启动尚不调用开放入口。

## 当前写集清点

以下路径以 codex_status 私有根 `/resource/codex-status` 为基准。来源为兄弟仓 `src/bundle_store.cpp`、`ports/ap01/application.cpp` 与平台维护实现：

| 写入方 | 相对路径/操作 | 当前覆盖与未完成项 |
| --- | --- | --- |
| BundleStore | `/bundle` 创建；`content.bin`、`incoming.bin`、`state.bin`、`state.tmp` 写入/替换/删除；旧 `a.bin/b.bin/m0.bin/m1.bin/rx.bin` 迁移与清理 | 实际业务走直接文件表；只读 begin 禁止创建、迁移、写元数据；共享门覆盖底层变更 |
| 配对绑定 | `/bindings.pending` 写入、读回、改名为 `/bindings.bin` | 配对业务只读检查与底层文件门双重覆盖 |
| 业务 context/激活 | Bundle state 元数据更新 | 只读恢复不刷新 context；已有 begin(now,false) 可建立新 context，但生产 worker 尚未在集合持久批准后调用 |
| 平台维护 | `/stable.pending/bin`、`/firmware.pending/bin`；Wi-Fi/菜单设备码及 ROM OTA | 维护独立且仍使用原生 I/O，不经 App 文件门；应由 D3/D4 共用协调规则约束冲突操作，不得封死救援通道 |
| 集合包/日志 | `/resource/app-store` | 与 App 数据根分离；新集合日志与下载写集由 D3 实现 |

这是已核对调用点清单，尚未宣称完成全部共享维护写集隔离。没有增加未经审计的 .bak 快照，不改变现有 Bundle/绑定文件格式。

## 直接 VFS 写租约与平台操作锁（2026-11-05）

生产共享集合在构造写门时绑定 `tryAppOperation/endAppOperation`，绑定在发布 C 表之前完成且不可运行期替换。每次 VFS 变更先取得集合许可，再尝试平台操作锁，重新核对集合许可；锁一直持有到底层调用（包括 write/sync）返回。失败返回、撤权竞态也释放锁。已有业务写入未返回时，维护写路由、安装 worker 和切网入队不能取得平台锁；维护 OTA 或 Wi-Fi 已处于忙状态时，新业务写租约被拒绝。

争用直接失败，不等待、不强制打断写入，也不改变健康批准的写许可。因此不会因为短时平台锁争用反复触发 Bundle 可写恢复。读取、关闭及纯查询不取得业务写租约。此处保护单次 VFS 变更，不把完整 Bundle 上传或多次文件操作包装成新事务。

ABI 3 配对回调会通过相同 VFS 写门保存绑定，维护路由不能在调用它时再次持有不可重入的平台锁。固件内部 ABI 3 适配器标记 `coordinatesWrites`，该回调不持外层操作锁、不执行维护 tick，变更由其 VFS 租约保护；旧适配器继续使用原有外层锁。此标记不属于 App C 表，App 无权设置。

`test_native_services_0041.cpp` 直接组合生产服务、维护路由、ABI 3 配对桥与文件适配器：阻塞底层写入时另一线程的维护/切网无法进入，写入失败后锁释放，OTA/Wi-Fi 忙时新写被拒绝；配对写入正常通过，忙时失败，旧外层锁路径仍保持。集合测试核对共享平台接线，写门测试覆盖取得平台锁之后遇到撤权的释放路径。原厂 OTA 自己的启动入口仍未接此锁，忙状态采样不能消除其检查/启动竞态；存储预算和救援优先策略也仍未全部闭环。

### 已复现的业务恢复争用缺口

2026-11-05 进一步用真实 `Ap01Business/BundleStore`、生产直接文件适配器和已安装 Bundle 复现：写门已获健康批准，但平台操作锁占用，第一次 `syncWritePermission(true)` 在底层任何变更之前失败；释放平台锁后再次调用仍失败，因为 `writeResumeFailed` 已锁存。原文件内容及变更计数保持不变。这是缺口证据，不是“争用可恢复”验收；`test-app-readonly-0041.py --direct-files` 报告明确标记 `writable_restore_contention_resolved=false`。

下一步必须在业务开始改变内存/持久状态之前取得完整写操作的准入：未取得只返回 Pending，保留只读状态和健康心跳，之后可以重试；已取得之后遇到真实 I/O 失败或提交未知仍保留既有失败/Unknown 语义，不盲重试。准入应覆盖恢复、Bundle 变更、配对保存与激活的实际写调用点，并与平台维护共用所有权；需处理嵌套 VFS 调用及同 App 多线程，不能用全局“当前 App 已持锁”标志让其他线程误借租约。只在 worker 先读 busy、延长轮询、或把任意 begin 失败都改成重试，均不能消除检查/写入竞态。当前逐 VFS 操作互斥不能作为这一项的完成证据。

### 同线程写操作作用域候选（尚未接 C API）

`Ap01AppFilesV3::writeScope` 在调用业务回调前取得完整集合租约。未准入返回 false，不调用回调且不改结果输出；准入后返回 true，回调返回码单独传回，不能把真实业务失败误认为可重试 Busy。线程身份由常驻平台在发布文件表前注入，零身份拒绝；作用域内只有同一线程的 VFS 变更借用已有租约，其他线程的变更与嵌套作用域均拒绝。回调期间收到集合撤权后，已准入操作继续完成，排空等待其释放；不会为每次 VFS 写重新抢锁。回调同步返回，不允许异常穿越边界。

宿主 TLS 身份与并发测试已覆盖互斥、嵌套、撤权排空、失败释放；真实 Bundle/App 测试验证忙时业务完全未开始、释放争用后可写恢复成功，真实 I/O 失败仍锁存且不盲重试。证据 `build/scope/readonly-direct-report.json` 的 `scoped_admission_candidate_verified=true` 仅表示此候选路径，生产 `writable_restore_contention_resolved` 仍为 false。

原生身份初步核对：固定 0041 的 errno 入口 `0xa00267c0` 调用 `0xa0026784` 取得线程局部区；失败会返回全局兜底 `0x62fc604c`，故不能未经检查直接使用 errno 地址。后续需固定指令证据并验证原生身份、追加兼容的 C 表入口，再接真实 Runtime 的全部业务写操作调用点；当前没有将候选视为端到端完成。

2026-11-05 原生身份路径已增加 `threadIdentity()` 与固定 ROM 审计脚本 `audit-native-thread-0041.py`。james.local Docker 中执行原厂 TLS/errno 指令：两个替代 TCB 分别指向不同 TLS，切回第一 TCB 重现原身份，TLS=0 时 lookup 返回 0 而 errno 返回全局兜底。生产薄包装的宿主 ROM 替身测试、零身份拒绝作用域及 RV32 编译通过。报告 `build/scope/thread-qemu.json` SHA256 `959571e6de6633765c7a38c883149927cb02ca2fed7daa1e7f25c2b251885b53`。任务记录为替身，未执行调度器，不声称线程生命周期/中断上下文已验证；接口限定 worker/task 上下文。C 表与 Runtime 接线仍未完成。

2026-11-05 C 表接线推进：ABI 3.1 在旧 296 B 前缀之后追加 `write_scope`，文件适配器已绑定原生线程身份；C11/RV32 布局、生产多 App C 表的 Busy/零身份/跨线程/嵌套及回调失败区分测试通过，旧表由访问 helper 拒绝新功能。真实 App 重复构建、重定位/加载器审计及完整平台镜像通过。此记录替代“C 表未接”限制，但真实 Runtime 尚未调用新入口，旧逐调用恢复失败仍未解决；下一步必须逐项接恢复、Bundle、配对、激活，不能仅凭 provider 测试关闭任务。

2026-11-05 首次可写恢复已接线：`Ap01BusinessPort` 接收可选写作用域回调，ABI 3 Runtime 绑定到 C 表 helper；bootstrap 总是只读恢复，worker 在健康许可后取得整段租约再调用可写 begin。PENDING 返回正常等待，不执行 begin、不锁存失败；已有可写状态不重复取得租约。真实 I/O 失败或缺少扩展仍失败锁存；新业务运行库在绑定阶段要求 ABI 3.1，旧平台提前拒绝。

宿主真实 Bundle 测试验证连续五次 Busy 后恢复一次、真实 I/O 失败不重试；james.local Docker QEMU 实际业务 worker 在持久健康批准后经 20 轮 Busy 保持健康且 mkdir=0，解除后 mkdir=1，再调度不重复。新业务包 `d2-business-scope-runtime-02/app.apx2` SHA256 `9953fe523ded6584c776da7f6cd6d10c931ed34813e57ce7f8b6e39f102f92f3`；双基址报告 `build/scope-resume/qemu-final.json` SHA256 `4cce51dbcce47944cd7f9ae804b9f86d671b301e218e7ecbc3ec92f53733dd40`，模型调度已给每个协作任务不同身份。真实持久 Bundle 成功恢复由宿主证明，QEMU VFS 仍为空 Bundle 模型，不能合并声称实机文件系统验收。此项关闭首次恢复争用缺口，完整写集仍开放：配对确认当前可从 UI 调用保存，须先迁移至 worker；Bundle、激活的完整操作准入尚未接通。

## 验证

- `test_app_write_gate_v3.cpp`：阻塞一个真实文件适配器写调用，在另一 App 上撤权；新写、元数据操作、旧句柄和 sync 拒绝，读操作仍可用；释放原写调用后才报告排空；显式重新开放后恢复写入。ASan/UBSan 通过。
- `test_native_app_set_v3.cpp`：启动前拒绝开放，两张 C 表同步观察同一许可，单 App 上下文不能修改集合许可。
- `test-app-readonly-0041.py --direct-files`：实际 Bundle/渲染/配对及 HTTP 故障回归，独立文件服务的只读/可写恢复逻辑通过；不把此测试当作生产自动授权接线。
- `d2-gate-run01.json`：真实双包在 james.local Docker 两基址回归，默认集合门关闭；该 QEMU 测试不证明持久批准后已自动恢复业务写入。

## 业务许可恢复接线（2026-11-04）

真实 Runtime 的业务 worker 现经 businessLock 调用 `syncWritePermission`，观察平台 C 表许可。false 关闭业务写入口，不做文件重载；首次 true 调用现有可写 begin 以恢复 Bundle/建立 context。begin 完成前 writesAllowed 保持 false，成功后才开放配对与业务变更；持续 true 不重复初始化。恢复失败后只读并锁存失败，worker 报告健康 Failed，不在原地重复迁移。

这替代上文“worker 尚未调用”的进度限制。授权来源仍未接 D3 日志：固定生产引导不会自动开放，测试显式授予许可不能替代持久批准。底层共享门负责撤权后的立即拒写与在途排空；业务 worker 的下一次循环关闭高层入口，不将该轮询当作 commit 排空屏障。

真实 Bundle 宿主测试覆盖 context 更新、重复许可不更新、撤权拒绝、重新恢复，以及写入失败后保持只读和不重试。`d2-resume-run01.json` QEMU 验证真实业务 worker 在无 Bundle 模型中响应许可、mkdir 成功/失败与失败不重试；持久数据成功恢复由宿主测试证明，未伪称 QEMU 模型完整文件系统验收。

## 事务持有写门（2026-11-04）

共享写门改为一个原子状态：closed、allowed、transaction hold。commit 和候选执行后的 cancel 使用 hold(true)，原子撤销新写入许可并保留已有 lease 排空；后台健康处理的 writes(true) 无法覆盖 hold。普通 writes(false) 也不能解除持有。

只有单事务所有者在日志不确定性、清理及操作交接已经解决后调用 hold(false)；释放只变为 closed，不自动开放写入，仍需后续健康批准。原生 healthSelected 遇到 hold 时保留“健康已批准”结论但不开放写门，也不把正常更新期间的持有误报为 App 健康失败。

测试覆盖 20,000 次并发重开/进入尝试、普通关闭不能释放、已有写 lease 排空、释放后仍关闭及再次明确授权；集合集成验证持久健康批准不能绕过事务持有。现有 91452 项事务断言继续通过。该机制解决 App 写门重开竞态；原生 OTA/Wi-Fi/安装服务操作互斥与救援优先策略仍须另行接入，不能以 hold 替代整个平台操作锁。

## 原生短时操作锁（2026-11-04）

`Ap01NativeServices0041::State` 以原子 flag 串行平台拥有的维护写操作。非健康观察 HTTP 请求从路由处理持锁至 `afterResponse`；鉴权失败、路由失败、网络发送失败也须调用 afterResponse 释放。维护 tick、Wi-Fi tick 和 UI 切网入队使用同一把锁；锁不跨越整个上传事务或 Wi-Fi 连接等待，只保护当前操作，已有 OTA/Wi-Fi busy 状态负责长生命周期围栏。

`tryAppOperation/endAppOperation` 供平台 App worker 使用：持锁后二次检查原厂 OTA busy、维护 OTA active、Wi-Fi busy；不满足则立即释放。原生 App 开机读取/预检、健康落盘和重启派发已接此入口。启动最多等待 5 秒，后续 tick 未获锁则稍后重试，不在 UI 阻塞。健康观察 `/health`、`/api/maintenance/status` 不执行固件 tick、不获取操作锁，可继续查询独立快照；其他请求锁忙返回明确 409。

维护回归验证 App 持锁时健康查询仍可用、其他请求不能进入写处理、错误响应和发送失败释放；独立无绑定 OTA/设备码轮换/重放/重启回执及无稳定记录切槽回归继续通过。完整 `d3-platform-03.bin` 构建/镜像通过。模型替身未运行原厂驱动，不能将这些测试推广为原厂全部代码被锁保护。

边界：原厂自带 OTA 只通过既有 busy 观察，未改它的底层入口，因此其检查/启动竞态尚未由此锁消除；App 安装 HTTP 服务仍待绑定；救援优先/抢占策略和空间预留期间其他业务写者的预算协调仍待实现。不能据此关闭原厂救援或宣称整个平台写集已闭环。

## 原厂 OTA 忙状态传播（2026-11-05）

生产服务的 `busy()` 此前只包含平台维护与 Wi-Fi 状态，遗漏原厂 OTA，和 `tryAppOperation()` 的判断不一致。现复用后者已有的 `State::firmwareBusy`，使业务 C 表和 UI 调度也能观察原厂 OTA。业务 Runtime 的 `systemBusy` 通过 C 表读取该值；未修改原厂 OTA 入口或关闭救援通道。

`test_native_services_0041.cpp` 直接链接生产服务、维护及 Wi-Fi 状态机，替换 ROM/VFS/线程端点且不启动执行器。旧实现触发 busy 断言，新实现通过原厂 OTA 开始/结束、操作锁竞争与释放、Wi-Fi 入队互斥；与独立无绑定 OTA/重放/重启回执/切槽测试一起纳入 `test-app-maintenance-gate-0041.py`。这证明状态传播，尚不证明原厂检查/启动原子性、业务在途写排空或完整资源协调。先前“安装 HTTP 待绑定”的记录已被后续 D3/D4 绑定与闭环证据取代，剩余协调限制仍有效。

2026-11-05：HTTP 整请求准入的宿主专项已覆盖认证 claim、Bundle begin/chunk/commit：Busy 不推进请求序号，原请求重试成功，成功回执重放无额外持久写入；只读 status 在 Busy 时仍可用。测试使用真实 Application/C2/Bundle 与 AppFilesV3，底层磁盘和线程身份为宿主替身；不代表 RV32 HTTP、配对确认或本地激活已验收。

本地激活通过完整 writeScope 执行；仅准入 Busy 返回 retry，worker 重排请求且不覆盖更新请求，存储/渲染失败保留原失败语义。两模板宿主测试已覆盖远程激活 Busy 重试/回执重放和本地激活 Busy 无写入后成功切页；原生 UI 队列并发及 RV32 HTTP 尚未验收。

配对确认：ABI 3 UI 仅记录已显示请求的有效松键及修订号；业务 worker 在写入准入内调用原绑定状态机落盘。Busy 保留待处理确认，worker 使用当前时间检查到期并拒绝修订号变化，防止取消/替换后旧按键授权新请求。绑定锁保护单个待处理确认；无函数表写入准入的旧端口保持原行为。宿主顺序交错已验，原生并发尚未验收。

Busy 的两层边界：仅 writeScope 准入竞争时，status 不需要写入租约；系统 `busy()` 为真时，业务生命周期策略仍返回 `business_offline`（独立维护查询另行保证）。宿主前者和 RV32 分段 HTTP 后者均已验证，不能将“准入竞争时可读”推广为所有维护期间业务 status 可用。

配对保存并发已增加宿主真实线程证据：底层 write 阻塞期间，绑定锁排除 UI、取消/身份查询与重复 worker，释放后提交一次；ThreadSanitizer 与 ASan/UBSan 通过。此项不代表原厂调度与硬件 I/O 延迟已验收。

## 2026-11-06 已验收集合的 UI 心跳恢复
用户明确要求简化运行期保护：只有 selector 已持久批准且健康的集合才启用 UI 过期恢复。UI 心跳过期仍立即撤销新写许可，只有一致、新鲜、全部 App 为 OK 且窗口/维护正常才恢复健康，再由原 healthSelected/事务写门重新准入。试运行 UI 故障、App/worker/维护故障和持久结果未知不自动恢复；transaction hold 仍不可被健康覆盖。seqlock 竞争沿用最后一致样本原期限，不当作停滞，也不无限续期。

### 2026-11-06 稳定集合启动
已通过日志/文件完整性校验选出的 Stable（或已登记 Empty）集合，仅等待本次启动的完整健康样本即恢复业务，不重复30秒连续试运行，不写新的验收记录。Trial 和 Rollback 仍要求30秒连续健康及原持久提交。启动失败/健康超时、事务hold、存储未知和维护路径策略不变。无新增状态、持久字节、堆或栈预算。
