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
