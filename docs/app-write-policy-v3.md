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
