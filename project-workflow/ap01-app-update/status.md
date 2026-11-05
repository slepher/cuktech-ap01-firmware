# 当前状态

2026-11-05 真实 Runtime 可写恢复接线：bootstrap 固定只读，业务 worker 经 ABI 3.1 写作用域后才执行可写 begin；Busy 保持只读/健康，成功恢复一次，真实存储失败仍锁存。新运行库绑定时拒绝缺少扩展的平台。宿主真实 Bundle/C 表回归、跨仓边界通过，报告 `build/scope-resume/readonly-direct-report.json` SHA256 `97f3231b94dc2a41d3a8d5294cf131fa8f596eec380b2ad7236cc262f3bb8647`。james.local Docker 实际 App 双基址 Busy→恢复→不重复验证通过，`qemu-final.json` SHA256 `4cce51dbcce47944cd7f9ae804b9f86d671b301e218e7ecbc3ec92f53733dd40`；App `d2-business-scope-runtime-02/app.apx2` 204464 B，SHA256 `9953fe523ded6584c776da7f6cd6d10c931ed34813e57ce7f8b6e39f102f92f3`。原厂服务与调度仍为模型，无新完整 ROM/实机操作。首次恢复缺口已关闭，Bundle/激活/配对操作准入及 UI 配对保存迁至 worker 仍待完成。

2026-11-05 ABI 3.1 写作用域 C 表：保留 296 B 旧前缀及填充，偏移 296 追加 write_scope（总长 304 B）；原生文件适配器绑定已审计 TLS lookup，旧/短表通过 helper 返回 Unsupported。C11/RV32 布局、生产集合 C 表忙/零身份/跨线程/嵌套/回调失败测试及平台回归通过，`build/scope-api/native-app-set-report.json` SHA256 `90d69adb661c063ef3c8204ee02fef628446055404256e035c06a701fcf8d7b8`。真实 App 两次构建一致、零导入及加载器/重定位审计通过：`d2-business-scope-api-01/app.apx2` 204288 B，SHA256 `154e1b755d5e84e775c149c84a386acba8295e6c59fd95d381d8c93f2ecb10a5`。完整候选 `d3-platform-20.bin` 6933336 B，SHA256 `c76b1467d9c61758cdbc184b39c38dc0fef8dee51764c8c952e3cd9c83695e93`，镜像检查通过。真实 Runtime 写调用点仍未调用扩展，生产争用故障尚未解决；本轮无 QEMU/实机操作、不可部署。

2026-11-05 原生线程身份：固定 0041 TLS lookup 指令审计、threadIdentity 薄包装/零身份拒绝和 RV32 编译通过。james.local 原有 Docker 镜像中完成原厂指令执行，验证不同替代 TCB 的 TLS、切回身份及 TLS 缺失时与 errno 全局兜底的差别；保留 5 项 socket/accept 回归，共 9 案例。`build/scope/thread-qemu.json` SHA256 `959571e6de6633765c7a38c883149927cb02ca2fed7daa1e7f25c2b251885b53`，本地输入与远端指纹一致。任务记录为模型，未执行调度器/完整 ROM；未安装宿主依赖、未操作实机。本轮无新完整 ROM，写作用域 C 表与真实业务接线仍待完成。

2026-11-05 写作用域候选：文件适配器新增同步 writeScope，先取得集合/平台租约再调用业务，同线程 VFS 借用租约，跨线程/嵌套拒绝，撤权等待整个操作退出；Busy 与回调失败分开。宿主并发及真实 Bundle/App 测试证明忙时零业务副作用、解除争用后恢复成功，真实 I/O 失败仍锁存。`build/scope/readonly-direct-report.json` SHA256 `969aed284080f0b425350b1bfbd63f14f69607808c53c4d832d01a376c3c9e50`；native-app-set-report SHA256 `ae1fc94e7f1a48baea2c4c21a0bb96d36627f337a2a3c04348c5f0ebe938ff87`。完整候选 `d3-platform-19.bin` 6933048 B，SHA256 `b8be42fd44d0c01a5bcef89a59ba2a38534d8386b21b22e3abc36c9f3f2c0653`，RV32/镜像检查通过。当前身份为宿主 TLS 替身，原生身份、C 表入口和真实 Runtime 调用点尚未连接，生产争用问题仍未解决；未操作实机、不可部署。

2026-11-05 真实业务争用缺口复现：`test-app-readonly-0041.py --out build/wc-probe --direct-files` 通过 ASan/UBSan 执行实际 Bundle/App、直接文件/网络表；新增反例证明平台写锁短时忙时，可写恢复在零底层变更下失败并永久锁存，释放锁后仍无法恢复。报告 `build/wc-probe/readonly-direct-report.json` SHA256 `0c21aad670d944b5cab03251986da5ea844353cd828b30c8ae62d73cb3892a46` 显式记录 `writable_restore_contention_resolved=false`；测试通过表示反例成功复现，不能算功能验收。下一步为完整业务写操作的可重试准入与嵌套/线程所有权，真实 I/O/未知提交仍不得盲重试，详见写策略。当前逐 VFS 锁接线尚不能视为可用的最终业务协调方案。本轮仅修改测试/文档，无新 ROM、无实机操作。

2026-11-05 业务写入协调：共享集合写门绑定平台操作锁，VFS 变更持锁到底层 write/sync 返回，拒绝 OTA/Wi-Fi 忙时新写；争用不撤销健康写许可。ABI 3 配对桥显式由 VFS 租约协调，避免维护外层锁重入，旧适配器保留外层锁。生产服务/维护/配对桥/文件适配器并发及失败回归、共享集合接线、撤权竞态、102956 项事务检查、独立维护和跨仓边界通过。报告目录 `build/app-install/d3-write-coordination-01/`，maintenance-gate SHA256 `186432aabb732e8ba7566b3e6046e5ae351e4e5bb2798c69ddac4778aa1db253`，native-app-set SHA256 `1d3a2bb17f2737206a2df5781761ebbff26cf0a68223e209c27861f4dd382a74`，set-journal SHA256 `4117c49838ec82ffd905c8e3ffb89938095025fd84367d9f803157a414cfe17f`。完整候选 `d3-platform-18.bin` 6932968 B，SHA256 `2039f0aedcb0618182053b62ff6a875d63b829468f1f4fe525a513e73039be9f`，镜像检查通过。单次 VFS 互斥不等于完整 Bundle 事务、原厂 OTA 入口互斥或完整资源/救援优先实现；无实机操作、不可部署。

2026-11-05 忙时原事务查询：维护路由对精确 GET App v3 status/result 放行长期 OTA/Wi-Fi busy，仍鉴权并持短时操作锁，不执行维护 tick；更新写操作、错误方法/后缀继续拒绝。生产 HTTP→维护→集合服务组合测试验证原回执可读且文件及写/删/改名计数不变，102956 项集合检查、独立维护和 ASan/UBSan 通过。证据 `build/app-install/d3-busy-query-01/`：maintenance-gate-report SHA256 `9856d48fcabce694fda1c49fcc4060f123cb098ca54963dd5dba5879cd3a4ca0`，set-journal-v3-report SHA256 `a4de353748d7accebd736fd52c265f189a19b991da17db841b2567cbe5f9d6c3`。完整候选 `d3-platform-16.bin` 6932760 B，SHA256 `de2f2af19cdc4c6e89b051846fe7e1a8b999d38be901483d4cedf9392d579f89`，镜像校验通过。尚未实现维护对业务在途写入的协调，也未消除原厂启动竞态；未操作实机、不可部署。

2026-11-05 原厂 OTA 忙门：修正生产服务 busy() 遗漏原厂 OTA 的问题，复用 App 操作入口已有判断。新增直接链接生产服务/维护/Wi-Fi 的宿主测试（ROM/VFS/线程替身，不启动执行器），旧代码断言失败、新代码及 ASan/UBSan、独立维护与跨仓职责边界通过。报告 `build/app-install/d2-service-busy-01/maintenance-gate-report.json` SHA256 `aaee8418f26f3ecab85316f93e375bebbf74cb9c5bff01ef05132d8b24e7bcd1`。完整候选 `d3-platform-15.bin` 6932664 B，SHA256 `3617bef184482fa3c9dbbe6a387358a064807ecbe5bb31b268cf16c61cf953ff`，镜像校验通过。状态观察不消除原厂启动竞态或替代在途写排空，D2/D4 协调仍未完成；无实机操作、不可部署。

2026-11-05 网络时钟失败收敛：新增 checked monotonicMs，区分合法启动时刻 0 与 ROM 时钟读取失败；App 网络 C 表透传失败，poll 超时检查时钟推进，EINTR/EAGAIN 重试经暂停并检查推进，避免冻结/倒退时钟下循环。故障注入及原生平台 ASan/UBSan 回归通过，证据 `build/app-install/d2-clock-failure-01/native-app-platform-v3-report.json`。完整候选 `d3-platform-14.bin` 为 6932696 B，SHA256 `0abc2d2d50015c7f738f4bbd2a4456d9f6426d984bfc53e208da765b8e184e8c`，镜像检查通过。旧 nowMs 调用约定保留，尚不证明全系统时钟异常恢复或完整资源保证；未访问实机、未部署。

2026-11-05 响应 OOM：故障注入复现 ArduinoJson String writer 在最终 flush 失败时仍返回非零计数，旧判断可留下空/不完整成功正文。统一 ap01EncodeJson0041 保留一次预分配，检查文档溢出、输出上限、序列化计数和实际长度；集合、维护/ROM 及保留的旧 App 更新回执复用。HTTP 对非 frame 空正文直接发送无需 String 分配的 503/unknown，指引查询原事务，避免将可能已提交的动作报为成功或拒绝。新回归、ASan/UBSan 原生平台、102896 集合检查、独立维护及旧 HTTP 均通过。完整候选 d3-platform-13.bin 6932440 B，SHA `f9690ed792daa30d30af512c7a3cb5c20ae8de98e3281cb4996cabcb7c081eaf`，镜像校验通过；证据 `build/app-install/d2-response-oom-01/`。不是全处理器 OOM 矩阵或整机资源保证，未操作实机、不可部署。

2026-11-05 维护请求预留：Ap01NativeServices0041::State 在 App 启动前持有并复用 34817 B HTTP 工作区（2048 B 头+32768 B ROM 块+终止位），串行维护请求解析不再逐次申请 6145 B/大块缓冲区。生产 RV32 State=35536 B（已含工作区）、维护对象=200 B、维护线程栈=16384 B；构建报告明确嵌套计费，避免再叠加旧 HTTP 上限。注入解析器数组分配失败后，空/小/最大分块及复用通过，越界/截断拒绝；ASan/UBSan 原生平台、集合 102896 检查、独立维护 OTA/重放/重启回执/无稳定记录切槽、跨仓职责边界均通过。完整候选 d3-platform-12.bin 6932600 B，SHA `d063186246c5daa8e977abd2091928f38da6fdef47ea0c58a964b079284ecd53`，校验通过。证据在 `build/app-install/d2-maintenance-reserve-01/`；仍不保证响应/处理器及 ROM 分配或整机维护储备，未操作实机、不可部署。

2026-11-05 原生 I/O 截止修复：waitFd 原先两次读取单调时钟，100→102 ms/截止 101 ms 会导致无符号下溢并请求 poll 1000 ms；新增真实适配器宿主回归先复现失败，改为单次采样后通过。覆盖已截止、等待上限、EINTR、I/O 错误、就绪/挂断，以及 TCP/UDP 非阻塞参数和各初始化失败的关闭路径；已接 test-native-app-platform-v3.py，原有双 App/宿主回归与 ASan/UBSan 一并通过。报告 `build/app-install/d2-native-io-01/native-app-platform-v3-report.json`，SHA `912740522e5de52aae4f4061509a6f1f8e528760cc87969434fd5e44445286d4`。完整候选 `d3-platform-10.bin` 6932264 B，SHA `17ae3f3f7e43fc045a11a96f6b86d5c5127273693070922defb84b582de1ad54`，镜像校验通过；未操作实机，不可部署。ROM 时钟/poll 为测试替身，不证明实际时延、时钟失效恢复或维护资源预留。

2026-11-05 原厂网络指令执行：james.local Docker QEMU（rv32,xtheadbb=true）运行编译后的监听器前段及固定 ROM 的 psock_socket/TCP accept。TCP/UDP type=0x801/0x802；原厂将 bit 11 映射为 conn.flags bit 3；空队列下非阻塞返回 -11、不进入 wait。阻塞对照即使设置接收超时 20 deciseconds，仍到达 timeout=-1 的等待入口，测试在该处断点停止。五项检查通过，报告 `build/app-install/d2-network-qemu-01/network-20261105-03.json`，SHA `facfb56108c944973903f1043b17437aa42d599151bbe26b62cef6ae49800da0`；脚本、ROM、监听器片段及引擎/支持脚本摘要一致。分配/setup 和空连接为替身，未执行完整内核引导/真实网络，不能宣称内核锁耗时或维护预留已验；未操作实机。

2026-11-05 网络阻塞审计：固定 0041 ROM 的 TCP accept 在空队列/阻塞模式下传 -1 无限等待，并不使用监听器接收超时。共享 native listener 创建 socket 时新增 ROM 已支持的 type bit 11（0x800），同时覆盖维护和 App；接收/发送仍用非阻塞 flags 及既有 deadline。新增 audit-native-network-0041.py 固定 ROM SHA/关键指令与调用链，变更 ROM 拒绝。完整 ABI 3 平台构建及候选校验通过，`d3-platform-09.bin` 6932264 B，SHA `f84b41d9529b9ca9d262bdc9e7c63ad09b464aa97554c17120aac73fb02f528b`；反汇编确认 TCP/UDP type=0x801/0x802。证据 `build/app-install/d2-network-audit-01/report.json`。本轮是静态原厂指令审计/构建，不是实际网络时序验收；维护预留、内核锁等待和资源完整审计仍待完成，未操作实机、不可部署。

2026-11-05 Bridge UI/Rust/RV32 闭环：生产页面函数经测试 IPC、真实 Rust worker、回环 TCP 和生产 C++ HTTP 完成五事务（首装失败空回退→同包新 ID 重装→A 单更→A+B 批更→整集回退）。james.local Docker 中真实 App 双基址运行，导出日志/运行快照返回原客户端；每事务一次 commit，重启等待期间 20 次原事务查询，boot=13/14/15/16/18，终态 cleanup_pending=false。页面重开恢复、成功/回退标签、查询与归档均通过。报告 `build/app-install/set-rv32-ui-v3-report-01.json`，SHA `26d67fcd842758202b07668a861420a9a82314c2463c011649c2f5ffe9fe2982`；全部快照、子报告和终态二进制摘要复核一致。原生 Tauri IPC/文件对话框、网络变化自动发现、完整 RV32 HTTP/原厂启动仍未验证，未操作实机或生产 Bridge。

2026-11-05 TCP/RV32 闭环：Python 原客户端经回环 TCP 完成五事务（首装失败空回退、同包重装、单更、批更、整集回退）；每事务一次 commit，重启执行期间 26 次查询原事务，实际 RV32 日志/运行快照导入后由生产服务清理并返回，boot=13/14/15/16/18，终态 cleanup_pending=false。报告 `build/app-install/set-rv32-tcp-v3-report-02.json`，SHA `436ca005efa953a19c51567a7caa759745fa1d47c750eba6471bd04cc4f9ebca`。实际 App 在 james.local Docker 双基址执行，宿主不注入健康。Bridge UI/Rust 与真实 RV32 的同次闭环、原生 HTTP/原厂启动仍待验证；未操作实机。

2026-11-04 原客户端/RV32 闭环：实时 HTTP commit 快照交 james.local Docker 双基址运行，实际日志和 boot.runtime() 快照回到原生产 service/cleanup/HTTP；Python 客户端五事务（首装失败空回退→同包重装→单更→批更→整集回退）通过，每事务 commit 一次，丢回复原事务恢复，boot=13/14/15/16/18，最终清理完成。客户端逐字段核验实际运行身份/健康，宿主不注入健康。权威报告 `set-rv32-closure-v3-report-02.json`，SHA `157e8941c6d475415f87a2fcd8179960f5e7f1526bfaa705daf41cf7b61ff84e`。HTTP 传输仍为管道，TCP/Bridge、完整 RV32 HTTP/原厂引导和资源/回收目标仍开放，未操作实机。

2026-11-04 空集合回退：HTTP/CLI --fail-first 五事务通过（首装失败清理→相同 Manifest 新 ID 重装→单更→批更→整集回退）；RV32 同 VM fail-trial→reset→empty-rollback 两基址通过，无 App 执行池/线程/页面，健康空集合持久 FailedRolledBack，trial/rollback 各一。输入/输出摘要已核验，报告 `set-empty-retry-tcp-v3-report.json` 和 `d4-empty-reset-run01.json`。两段未串为 RV32 终态返回客户端的连续闭环，其他资源/回收目标仍开放，未操作实机。

2026-11-04 同 VM reset：runner 复用 QMP system_reset 与 ELF BSS 初始化，实际导出日志逐字节传递；候选失败→旧集合成功、候选失败→旧集合失败→维护两条链在 james.local Docker 双基址通过。reset PC=0xa0000000，三阶段各基址同 PID、两次 reset，所有输入/输出指纹已核验；错误日志连接在 reset 前拒绝。报告 `d4-reset-rollback-run01`、`d4-reset-maintenance-run01`、负向 `d4-reset-mismatch-run01`。不是原厂 Boot ROM/reboot 寄存器验证，HTTP/客户端闭环、空集合再安装及资源/回收目标仍开放，未操作实机。

2026-11-04 RV32 维护兜底：旧集合真实 worker 失败后持久 RecoveryRequired，再以该日志第三次启动，双基址均无 App 线程/页面/执行池分配，模型维护监听保留；重复 poll/stage 不改变双槽字节或计数。报告 `d4-http-rollback-fail-run01`、`d4-http-maintenance-run01`，输入/输出指纹已核验。runner 已区分无 App 维护与真实执行。仍未覆盖真实救援网络、同 VM reset、空集合再安装和客户端闭环，未操作实机。

2026-11-04 RV32 回退：HTTP 第四事务快照启动真实候选，停滞实际 worker 触发生产监督并写 RollbackPending；原样导出双日志交给下一 CPU 启动，按 oldDigest 加载完整旧双 App，健康后 FailedRolledBack。james.local Docker 两阶段均双基址通过，trial/rollback 各消耗一次，旧两包+Manifest 与前次成功集合逐项同 SHA；正常 Succeeded 日志导出也通过。报告 `d4-http-fail-run01`、`d4-http-rollback-run01`、`d4-http-export-run01`，详见 QEMU 记录。同 VM 复位、RV32 结果返回客户端/清理及维护兜底仍开放，未操作实机。

2026-11-04 HTTP→RV32 文件桥接：新增精确 commit 前重启快照导出及 --snapshot guest 构建。宿主 102896 检查/四链 TCP 通过；首装、A 单更、A+B 批更快照在 james.local Docker 各双基址执行真实两 App/三线程及持久健康提交通过，六份输入和源快照摘要一致，单更 B 包不变。报告 `qemu-james/d4-http-run00/01/02.json`。HTTP 仍在宿主、QEMU 为独立新 CPU，回退再启动/结果返回客户端及同 VM 重启仍未完成，未操作实机。

2026-11-04 RV32 当前日志回归：james.local Docker `d3-journal2-run01.json` 两基址通过，当前 AUT3 format 2 接收偏移持久读回、真实双 App/三 worker 与 runtime 完整集合身份均验证，五项输入指纹一致。guest SHA `54312d89a28958980f55863833270f6bf8c7149a1f0ef41774be67dfc53ec26a`。仍是预置 SwitchPending/内存 VFS，HTTP→CPU 重启→回退重载整链未完成；未操作实机。

2026-11-04 Bridge 暂存：新增 128 MiB 总量限制及无活动回执时的 24 小时过期清理；活动/损坏回执保留缓存，原始文件不参与清理。5 项应用测试、职责边界与 UI/Rust/C++ 四链复验通过。模型与测试 IPC 边界不变，未操作实机。

2026-11-04 D4 UI/Rust/C++：生产页面函数经测试 IPC 调用真实 Rust 暂存/准备/worker/查询/归档，连续完成真实双包首装、单更、批更、失败整集回退。每条丢一次回复、重开页面恢复原事务，commit 各一次，回退不误报成功；报告 `build/app-install/set-ui-rust-tcp-v3-report.json`（交叉命令用 `--rust-ui`）。DOM/Tauri IPC 与固定测试端点由适配器代替，原生 IPC/文件对话框仍未验，健康/CPU 重启仍为模型。其他网络变化、资源/GC/RV32 目标开放，未操作实机或生产 Bridge。

2026-11-04 D4 Bridge UI：AP01 卡片支持完整清单/单个或多个包、校验后显式 run、逐包进度/复用、取消/原事务恢复/归档。Node、原生 WKWebView 88 个窄/宽场景及截图审阅通过，Rust 暂存/应用回归与跨仓职责检查通过。页面轮询只读本地任务；未重建运行 Bridge。UI IPC 为模拟，UI→Rust/C++ 同次全链、自动发现网络变化、桌面暂存清理和平台资源/GC/RV32 待办仍开放，未访问实机。

2026-11-04 D4 Bridge worker：有界后台推进原回执，任务内存持设备码/已校验包、取消意图先落盘，每步操作锁、临时失败退避查询，预算到期保留回执。应用 4 项及 worker→生产 C++ TCP 真实双包四链通过：首装/单更/批更/失败整集回退，四种丢回复自动恢复，commit 各一次。报告 `build/app-install/set-worker-tcp-v3-report.json`（原交叉命令加 `--rust-worker`）；仅宿主重启/健康模型。UI、自动发现网络变化验收、资源协调/GC/RV32 整链仍待完成，未启停生产 Bridge 或访问设备。

2026-11-04 D4 Bridge 恢复：显式 reconnect 在新地址只查询原事务，MAC/事务/Manifest/进度通过后原子保存地址；未确认进度的 404 另认证 status，允许保留围栏迁移或本地 abandoned 取消，已确认过期/未知不丢回执。core 10 项、app 3 项通过，含全 GET 错误身份/摘要/503/写失败及应用新地址恢复后取消无额外 POST。自动 worker/发现策略、UI 和其他非实机目标仍待完成；未部署、未访问实机。

2026-11-04 D4 Bridge 归档：离线 inspect 不依赖设备地址，query 只观察原事务；archive 重新确认终态/清理与成功运行身份后，先同步历史副本再释放活动回执，支持再次 prepare。core 8 项（含归档冲突/复制后中断恢复）、app 3 项（未完成/未清理/旧 boot 拒绝及接续更新）通过。地址迁移、未发送事务取消、自动 worker/UI 及其余平台待办仍开放；未部署、未访问实机。

2026-11-04 D4 Bridge 应用层：Tauri/MCP 共用 prepare/inspect/advance/cancel，要求已登记 AP01 并复用操作锁。prepare 仅认证能力/校验产物并独占保存原回执，推进前核对原 operation_id；设备码不落盘，保留发送前失败/未知分类。3 项隔离应用测试通过（回环准备/推进、损坏回执拒绝、登记/锁）。自动 worker、终态归档/地址恢复及 UI 页面仍待完成；未启停 Bridge 或操作实机。

2026-11-04 D4 Rust/C++：复用 TCP 故障中继，Bridge core 协调器对接生产 C++ HTTP/AUT3 模型，以真实双包完成首装、A 单更（B 不上传/身份不变）、A+B 批更及失败整集回退。每条分别丢 begin/chunk/commit/ready 回复，重载原回执恢复，commit 各一次；boot_id 12/13/14/16。报告 `build/app-install/set-rust-tcp-v3-report.json`。只回环 TCP，健康注入/CPU 重启模型，不执行 App 指令；Bridge application service/UI、RV32 整链和资源/回收待办仍开放。复现见兄弟仓库 `project-workflow/ap01-app-set-v3/status.md`。

2026-11-04 D4 Bridge 单步协调：core 每次先重载回执并查询原事务，按确认进度上传/Ready/commit 或显式取消；Succeeded 校验新 boot 与完整健康运行集合。7 项定向测试（含真实双包和 commit 回复丢失恢复 TCP）通过。application worker/service/UI 及 Rust/C++ 交叉验收仍未完成，未部署或操作实机。

2026-11-04 D4 Bridge 回执：Rust Receipt 首次独占/fsync、后续复用原子替换，保存原事务/Manifest/旧集合围栏，拒绝身份或文件变化、偏移/序号/阶段回退；只持久化类型化进度，不存设备码/任意响应。3 项离线测试含真实集合与写入故障通过。尚未接异步上传/重连/取消协调和 UI，未部署、未访问设备。

2026-11-04 D4 能力闭环：固件报告共用加载限制和 RAM/存储预留，Python CLI 与 Bridge Rust 按整集合核对资源和服务位图。CLI 超预算在回执创建/begin 前拒绝；472 无效输入、10 故障流程、102896 事务断言、真实回环 TCP 与 Rust 真包能力测试通过。候选 `d3-platform-08.bin` 6932264 B，SHA256 `fb99d42bbd5cb5a70534ea67aaa24efd03cf09df58b518debdda1255172ac559`，镜像验收通过，未部署。限制为模型配置，不是硬件容量/存储预留证明；Bridge 持久协调/UI、孤儿回收及 RV32 整链待办。

2026-11-04 D4 Bridge 产物：兄弟 core 新增 AMF3 规范/摘要/依赖/端口与资源汇总、ABI 3 APX2 段布局/入口/BASE32 校验，以及按 changed_mask 选择提供包。真实业务+peer、空集合/截断/重复/缺包、重算摘要后的非法入口/保留位/重定位字测试通过。未接 Bridge 持久协调/application service/UI，设备资源能力准入仍以平台为准，未部署或访问实机。

2026-11-04 D4 Bridge core：兄弟 codex_status 复用 bounded HTTP transport 新增 v3 强类型动作、MAC/事务查询围栏、块 SHA256、长度限制及菜单码鉴权；设备身份错误/JSON 或响应截断保留 AckUnknown，不自动重发。定向 Rust 路由/真实回环 TCP 两测试通过；application service、产物校验/持久恢复和 UI 尚未接入，未启停/部署 Bridge 或访问设备。跟踪见兄弟 `project-workflow/ap01-app-set-v3/`。

2026-11-04 D4 TCP：v3 CLI 原有 urllib Transport 经 127.0.0.1 随机端口连接 C++ HTTP 服务模型，首装/单更/批更/回退四链通过。begin/commit 处理后断开、chunk/ready 截断响应正文后关闭，客户端保持同一事务并查询恢复，commit 各一次。报告 `build/app-install/set-client-tcp-v3-report.json`；只本机回环，未连接设备或外网，CPU 重启/健康仍为模型。Bridge、孤儿回收、RV32 整链及剩余资源协调仍待推进。

2026-11-04 D4 CLI/C++ 交叉验证：Python v3 CLI 通过管道 HTTP 字节调用生产 C++ 路由/服务、AUT3 选择与清理。真实包连续首装→A 单更→A+B 批更→试运行失败整集回退通过，分别注入 begin/chunk/commit/ready 回复丢失；B 单更期间无上传且运行身份不变，回退列表与旧集合全部一致，boot_id 为 12/13/14/16。报告 `build/app-install/set-client-http-v3-report.json`；宿主注入健康、模拟 CPU 重启、内存 VFS，不执行 App 指令或接触实机。Bridge、孤儿回收、真实 TCP 客户端和 RV32 整链等仍待完成。

2026-11-04 D4 v3 CLI：复用旧客户端 Transport/回执持久化/退避，新增完整 Manifest+变更包上传、发布、commit、查询和取消。首次请求前保存同一事务 ID/旧集合围栏/原 boot，未知先查询，已确认回执过期拒绝新建。真实包注入对端验证 10 条单更/批更丢回复、进程恢复后只查询、回退/取消/过期拒绝通过；未连接设备。真实 C++ HTTP 模型交叉测试、Bridge、孤儿扫描与 RV32 整链待完成。

2026-11-04 D4 客户端校验：新增 AMF3/提供包核验与单更/批更选择，复用 APX2 规范校验；成功须核对新 boot、清理结束、完整健康运行集合及逐 App 身份。真实双包和 453 项无效输入拒绝通过，不连接设备。v3 CLI 上传/持久回执/断线恢复循环尚未接入。

2026-11-04 D4 运行快照：HTTP 从 UI 已发布的不可变加载器选择返回成功 start 的 App 列表、摘要/版本、完整性及监督健康；候选日志与实际启动集合分别报告。未采样健康为 null，第二个 App start 失败只列成功前缀并标 partial_failed。102895 事务/HTTP 断言、13 文件启动场景及监督/写门/RV32 回归通过。候选 `d3-platform-07.bin` 6931544 B，SHA256 `8051e345a37319ae9f81d11a2fa59f74f015848dd6687d7e34609ca552ee4c2f`，构建与镜像验收通过。未部署；客户端核验、孤儿扫描和 RV32 整链仍待完成。

2026-11-04 D3/D4 自动清理：原生 worker 在维护操作锁内每秒尝试终态事务清理，复用双槽终态屏障；Unknown 冻结至状态查询重载，缺失 Manifest 保留 pending，成功仅解除 transaction hold。真实包单更/批更成功及回退后允许下一次事务，取消缺失文件/删除丢 ACK 恢复通过，共 102871 断言，ASan/UBSan/RV32 编译及维护回归通过。候选 `d3-platform-06.bin` 6929704 B，SHA256 `5351fbd36e9bcbca5a317487add6e67693a341f80e374ee768c4cb085b03d903`，镜像验收通过，未部署。孤儿扫描/Manifest 元数据回收、运行列表、CLI/Bridge 和 RV32 整链仍待完成。

2026-11-04 D4 HTTP 组合：真实双包经生产传输层→设备码鉴权→维护锁→事务服务，分段收发、错误设备码、begin/commit 持久后响应丢失及原事务重放、Unknown 续传、发布/取消/排空超时通过。共 102759 断言，ASan/UBSan/RV32 服务编译通过；发送失败也释放操作锁。该证据为宿主流模型，不代表真实网络/CPU 重启；RV32 新事务链、运行列表、自动清理及 CLI/Bridge 继续待完成。

2026-11-04 D4 原生接线：0041 维护启动前配置安装回调，日志加载/选择后发布服务；HTTP 与健康 worker 共用操作锁，OTA/Wi-Fi busy 拒绝安装并保留健康查询。修复新增事务后健康快照仍报告初始 Empty；完整候选 `d3-platform-05.bin` 6928536 B，SHA256 `620971a08380a0a187f60c121697f24625079e3f19daf0e63e5945dfc54c7c8c`，镜像验收、96042 事务断言、集合/监督/写门/维护回归通过。未部署；HTTP 传输与服务组合执行、RV32 新事务链、运行列表、自动清理和 CLI/Bridge 尚待完成。

2026-11-04 D4 服务适配：真实双包请求链覆盖 begin/上传/发布/commit/取消、跨 principal 拒绝及 Unknown 查询续传；修复重放或拒绝 begin 重置排空期限，取消不再依赖候选 Manifest。宿主 ASan/UBSan 与 RV32 编译通过，共 96042 断言。原生维护回调、运行列表、自动清理、CLI/Bridge 仍未完成；未进行实机操作。

2026-11-04 D4 请求合同：新增 /api/app/v3/ 严格解析，64 B ASB3+AMF3 begin 保持 4096 B 请求限额，chunk 沿用 query 事务/MAC/offset/SHA256；方法、索引、溢出、保留位、摘要错误拒绝。宿主及 RV32 通过，合同见 [HTTP v3](../../docs/app-set-http-v3.md)。生产处理器仍未绑定，响应/运行列表与 CLI/Bridge 尚未实现。

2026-11-04 原生短时协调：维护 HTTP（持锁至 afterResponse）、维护/Wi-Fi tick、UI 切网入队与 App worker journal/health 共用原子操作锁；App 进入后二次检查 OTA/Wi-Fi busy，健康查询免锁保留。锁回归、无绑定 OTA/设备码/重启回执/无稳定记录切槽、集合回归通过。候选 `d3-platform-03.bin` 6915176 B，SHA256 `07d1727526c8aa380dc08c51266c013ac729864baa217c21f275c97dbb568313`，镜像通过，未部署。原厂 OTA 启动竞态、救援优先/预算协调及安装 HTTP 服务仍未闭环。

2026-11-04 写门竞态修复：commit/cancel 使用原子 transaction hold，后台健康 writes(true) 和普通关闭都不能解除；释放仍需后续健康授权。并发 20000 次重开/进入尝试与持有时已有 lease 排空通过，原生集合 healthSelected 集成及 91452 事务断言/RV32 回归通过。OTA/Wi-Fi 与安装服务统一操作锁尚未实现，未操作实机。

2026-11-04 D3 组合验收：宿主四条完整事务从双包首装到单更/批更成功或整集回退，串联 begin→chunk→发布→commit→重载裁决→连续健康→cleanup。单更验证 B 文件字节/摘要不变；未齐 Ready 拒绝、重复 commit 不增序号、淘汰包删除均通过，累计 91452 断言及 RV32 编译。更新包仅重写版本元数据和摘要，未执行新 App 指令；原生维护锁/安装服务、HTTP/Bridge、孤儿扫描仍未完成。

2026-11-04 D3 事务清理：先读回确认双槽同一终态，再删除未被最终集合引用的本事务包及已知临时文件，最后清 cleanup_pending。三种终态、屏障截断、删除失败/丢 ACK、完成记录丢 ACK、共享包保留通过，累计 72983 断言及 RV32 编译。最终 Manifest 元数据与无日志孤儿尚未扫描回收；完整 GC/私有目录枚举和安装服务接入仍待完成。

2026-11-04 D3 取消：候选执行前持久 Cancelled/cleanup_pending 并撤销未调用的重启；已调用回调明确 RebootInFlight。TrialStarted 取消只持久安排整集回退，不在线加载旧包。取消 Unknown 不自动恢复重启，重载区分已取消与仍待切换；重复请求不增序号。72383 断言及 RV32 编译通过。GC、原生操作锁/HTTP 入口仍待完成。

2026-11-04 D3 begin 持久化：实现 AMF3 前缀一致续写、同步/读回、rename 及目标读回；begin 查询空间/准备目录、发布旧与候选 Manifest 后才保存 Receiving。实际双 App Manifest 每个前缀恢复、发布失败/丢 ACK、空间不足、目录失败和低空间 Replay 通过，总计 72279 断言及 RV32 编译。原生安装服务/鉴权/统一维护操作锁、取消/GC/D4 仍待接入，未操作实机。

2026-11-04 D3 begin 规划：平台按 ID/包摘要推导变更位图和字节总量，固定字节指纹约束重放；同请求保留上传进度，参数变化冲突。保守空间需求扣维护预留，支持单更/批更/新增移位/纯删除。66623 断言及 RV32 编译通过。函数不写文件/日志，尚需安装服务锁内空间预留、Manifest 发布后再创建 Receiving；未宣称完整 begin 已完成。

2026-11-04 D3 commit 核心：核对旧摘要/版本和全包 Ready/长度，预检整个候选集合，关闭写门并有界排空后持久 Ready→SwitchPending，再单次安排重启；Unknown 不重启，重复 commit 不增序号/重置期限。真实包故障测试通过，累计 66571 断言及 RV32 编译。未接安装服务与维护操作锁；begin/Manifest 发布、空间预留、GC 和 D4 仍待实现。

2026-11-04 D3 包发布：真实 APX2 暂存校验→摘要路径 rename→目标完整读回校验→单包 Ready 位落盘。与开机预检共用 Manifest/APX2 字段校验；目标已存在只验证复用、不覆盖坏包。真实业务包发布故障/重放回归通过，累计 66439 断言及 RV32 编译。尚未接 begin、全集合 Ready/commit、空间预留与 GC。

当前格式 2 平台候选：`build/app-install/d3-platform-02.bin`，6914344 B，SHA256 `02e89989510c00c9d0a2205c0fef67a62803d71ee6feade1ec524fe237098868`；完整构建、镜像校验与集合回归通过。下载器尚未接原生安装入口，硬件 backend 仍拒绝执行，未部署。

2026-11-04 D3 续传基础：AUT3 格式升级 2，320 B 内存储 8 包已确认偏移，旧草稿格式 1 明确 Unsupported。新增逐包有界 chunk、未确认尾部比较、同步/关闭/读回后提交偏移；Unknown 冻结并要求重载。53108 断言包含 512 数据截断点+320 进度截断点，两包偏移和重放围栏通过。尚未接 begin 授权/空间、包发布/Ready/commit；此前 QEMU 记录仅适用于格式 1，待新链路复验。

2026-11-04 D3 RV32：james.local Docker `d3-journal-run01.json` 两基址通过，真实两 App/三 worker 经 AUT3 选择与连续健康裁决，Succeeded 写入读回后开放写许可；真实 worker 恢复写初始化一次，线程故障后撤权。五份输入指纹核对一致，guest SHA `ddd5f5c1c2fe24c16125134b0c01886a86d0bd2a49372a6fca5aa1b3e30eb862`。使用预置 SwitchPending 和内存日志槽，不代表 HTTP commit/真实重启/掉电已验证；下载、发布、commit、清理及 D4 仍未完成。

2026-11-04 D3 原生接入：维护先行，按 MAC/boot_id 读取 AUT3 并启动所选完整集合；worker 每 100 ms 做健康提交与单次重启派发，绑定既有 ROM reboot。维护新增原子 journal_result/phase。完整候选 `d3-platform-01.bin` 6914856 B，SHA256 `193922c89ae69bc87bb1b321ab4456c7b1d3abeaf41e4038c70f2fb9ad849e70`，镜像/链接符号/边界检查及集合、维护回归通过。硬件 backend 不可用、未部署；QEMU 真实事务链和 D3 下载/commit/清理仍待推进。

2026-11-04 D3 重启安排：补 250 ms 延迟单次派发、5 秒未重启失败锁存；持久回退且写门排空后才安排。维护 app_runtime 暴露 reboot_state，宿主维护回归及集合回归通过，日志/选择器/重启共 11252 断言通过。原生回调与 commit 路径尚未接入，不宣称真实重启闭环；无实机访问。

2026-11-04 D3 健康提交：实现 10 秒启动/连续健康 30 秒/总计 40 秒裁决；观察缺口打断计时，持久确认后 healthSelected 才开放共享写门，确认 Unknown 保持关闭。日志/选择器 11232 断言和双 App 集成回归通过；原生 worker 调度、重启安排及协议回执仍未接入，未操作实机。

2026-11-04 D3 文件组合：stageSelected 接入按 Manifest 摘要寻址的真实文件预检，核对 sequence；持久 trial/rollback 后才向 UI 发布，Unknown 丢弃暂存。真实 APX2 + 宿主入口集成验证了丢 ACK 不执行、候选缺失/版本错回退初始空集合；D2 集合/监督/写门回归与 RV32 编译通过。原生 hook、连续健康确认/重启尚待接入，无实机操作。

2026-11-04 D3 开机裁决：新增每 boot 一次的集合选择器，完整预检后持久 trial/rollback 消耗再授权加载；执行失败只安排下次 boot 整集回退，回退重启中断进入维护。AUT3 与选择器合计 11117 项断言、ASan/UBSan/RV32 通过。文件启动器暂存发布、连续健康计时、重启执行/回执仍未连接，未勾选 D3 开机整链任务。

2026-11-04 D3：AUT3 集合日志编码/双槽存储层通过 10894 项断言（含两个槽共 640 个截断写入点）、ASan/UBSan 与 RV32 编译。Unknown 时禁止后续写入并隐藏旧 current；旧 AUT2 显式拒绝。合同见 [AUT3](../../docs/app-set-journal-v3.md)，报告 `build/app-install/set-journal-v3-report.json`。尚未接入下载、开机选择、持久健康确认或重启；无实机操作。

2026-11-04 可写恢复接线：真实业务 worker 在串行锁内观察平台 writes_allowed；开放后调用一次可写 begin，完成前不向配对/业务命令公布可写状态；重复许可不重建 context。撤权关闭业务入口，底层集合门立即拒绝写入。恢复失败保持只读、健康 Failed，且本次运行不重复迁移。实际 Bundle 的开放/幂等/撤权/失败不重试，direct-files 与旧服务兼容回归均通过。

真实双包 `d2-resume-run01.json` 在 james.local Docker 两基址通过，验证实际 worker 在模型许可开放后初始化一次，撤权后再次恢复失败时不重试；该许可为测试显式注入，未冒充 D3 持久批准。业务包 `d2-business-resume-01/app.apx2` 204,080 B，SHA256 `c3bf0c7d4a01d6788532cf178c7f8e969862af5088c42062b522df5eec5e9913`，72 项 BASE32、零导入，01/02 重复构建一致。候选 `d2-platform-11.bin` 6,907,160 B，SHA256 `a042af91eec958a601c0f9986270530d25fcc5bbd8f1b7c445a3988c0667b2cf`，镜像及跨仓检查通过。生产默认只读；D3 持久授权和维护共享写协调仍待完成，未操作实机。

2026-11-04 集合写入门：所有 App 直接文件变更共用 `Ap01AppWriteGateV3`。撤权先拒绝全部新变更（含旧可写句柄与零字节 sync），在途操作返回后才报告排空；不逐 App 切换。启动前拒绝开放，单 App 上下文不能改多 App 许可。共享门并发测试、集合/平台/Manifest/监督回归、实际业务 direct-files 只读恢复和跨仓边界通过。写集与未接线边界见 [写许可记录](../../docs/app-write-policy-v3.md)。

真实双包默认只读回归 `d2-gate-run01.json` 两基址通过，五项输入摘要已核对。候选 `d2-platform-10.bin` 为 6,907,160 B，SHA256 `55886521e2e807f70c646a469e09e7bdaffe812fabcfd497c200b8b0f456bb66`，镜像验收通过。D3 持久成功后授权与业务 worker 可写恢复尚未接通，维护/OTA/Wi-Fi 的共享写协调仍开放；不能宣称试运行事务完成。未操作实机。

2026-11-04 工作线程活性：codex_status ABI 3 增加业务/发现循环心跳和启动位；尚未进入两条循环时 Pending，业务 15 s 或发现 5 s 无进展时 Failed，发现线程退出也标记失败。peer 改为检查最近任务心跳（5 s），不再仅判断曾运行。读取心跳后再采时钟；平台监督也容忍并发发布者略新于已采样时钟，避免误判 uint32 回绕。

真实双包 `d2-beats-run02.json` 在 james.local Docker 两基址通过：分别冻结业务、peer、发现线程，同时保持 UI/其他线程运行，准确定位所属 App；恢复线程后 App 健康恢复，但平台已记录故障仍锁存。新业务包 `d2-business-beats-02/app.apx2` 为 203,904 B，SHA256 `7325faf42b12c57d892e76ca2517ae45393c77baf7dc00c2f81ff6dfdcdf1656`，72 项 BASE32、零导入，02/03 独立构建字节相同。peer 为 992 B，SHA256 `93ebd331efc55e0f0adaabda2239ae81288367d72762ec33a1286b9a7dd56cad`。阈值是观察策略，不是已验证 ROM/VFS/渲染最长耗时。

集合/监督宿主、跨仓边界和完整平台候选验收通过：`d2-platform-09.bin` 6,906,856 B，SHA256 `03a37f8c1c3cad21be5348e576d4af312fa888e058411938b0835c9ae53e9229`。接下来仍需业务写集/试运行写许可、D3 重启事务与失败回执；独立硬件看门狗未验证。未访问实机、未部署。

2026-11-04 集合健康监督：UI 在各 App tick 后串行调用 health 并发布原子快照；独立 `ap01-watch` 工作线程每 100 ms 检查启动、UI 快照和维护循环心跳。启动/Pending 30 s、UI 快照 5 s、维护心跳 10 s 阈值，故障锁存至重启；窗口销毁单独标记 `window_absent`，不误报 UI 卡死。`GET /health` 与 `/api/maintenance/status` 增加 `app_runtime`，配置监督器后不再调用 App online；设备码查询保持平台独立性。

监督单元测试（含时钟回绕、并发快照）、12 个文件组合场景、维护 HTTP、既有平台/Manifest/边界回归通过。真实双包 QEMU `d2-watch-run01.json` 两基址通过，验证健康、窗口状态转换及注入 UI 停滞；五项输入摘要已核对。完整候选 `d2-platform-08.bin` 为 6,906,840 B，SHA256 `b74a7f72c4ae3240abdd378b9a1cadeab971901ba1610bd4d37ccd310c4e8c76`，镜像检查通过，未部署。

监督仍未完成：codex_status 健康入口主要依赖 UI，业务/发现线程的独立心跳尚待补充；模型显式调度监督 tick，不证明独立硬件看门狗或整机调度卡死恢复。自动重启关闭，必须等 D3 持久选择后接入重启请求及失败回执。业务写集/试运行写许可和 D3/D4 继续待推进。

2026-11-04 生产文件组合：原生 hook 改为先启动维护监听，再由工作线程读取 `/resource/app-store/current.amf3` 和 `/resource/app-store/packages/<APX2内容摘要>.apx2`。包存储与 App 私有目录分离。暂存总上限 4 MiB，作为额外 resident 预算从总 RAM 中扣除；工作线程全包校验后 release/acquire 发布不可变快照，UI 回调加载，不执行 VFS I/O，结束后释放暂存，执行映像仍保留至重启。

12 个暂存场景、Manifest 460 项、共享平台与跨仓边界检查通过；覆盖缺文件、短读、损坏、关闭失败、预算、摘要和 backend 不可用，维护原厂导航保持。真实双包文件组合在 james.local Docker 两基址通过，报告 `build/app-install/qemu-james/d2-files-run02.json` 五项输入摘要已核对。候选 `d2-platform-06.bin` 为 6,904,216 B，SHA256 `b8216325af9b83d009b57eda415fafb675f927d6aba515ba1d49ab7437bb5522`，镜像检查通过，ELF 确认保留文件组合符号。

限制：这是固定 Manifest 的 D2 引导路径，不是 D3 日志选择；数据版本固定为既有 schema 1，不执行迁移，写许可仍默认关闭。持续监督、业务写集、单更/批更事务与客户端继续待做。硬件 backend 不可用，未部署或访问实机。

2026-11-04 真实双包：codex_status 与新独立 z_probe 已经 AMF3、生产集合加载器与共享平台，在 james.local Docker QEMU 两基址执行成功。第二包 880 B，SHA256 `98966125e3c3ffb8a8e7dd7d993880da74ac268391aa5e6aabef9791f4473faa`；608 B 映像、2 项 BASE32、零导入，双链接归一化与重复独立构建字节一致。guest 验证监听前零启动、两个注册项、三个后台任务、集合 Pending→OK、peer 页面切换，以及两包窗口重建不重复任务/维护监听。报告 `build/app-install/qemu-james/d2-set-run01.json` 的 guest/主包/构建报告/Manifest/peer 五项输入摘要已核对。

两包执行真实 RV32 指令，ROM I/O、LVGL、维护监听和调度仍为模型。集合宿主、Manifest 460 项检查与跨仓边界回归通过。生产 Manifest 文件/选择入口、持续健康监督和 D3/D4 仍待推进，本轮没有新 ROM 或实机操作。

2026-11-04 集合组合：新增 `Ap01NativeAppSetV3`，连接 AMF3 全包预检、每 App 授权 C 表、集合启动器和唯一共享维护/窗口宿主。所有上下文保留至重启。组合测试通过 ASan/UBSan 和 RV32 编译，覆盖监听前不读包、坏第二包零启动、第二包 publish/start 失败时保留映像、读者成对关闭、共享宿主，以及窗口重建不重启 App/维护服务。报告 `build/app-install/d2-native-set/native-app-set-report.json`；入口与第二包仍为宿主/元数据替身。

共享平台的真实单包在 james.local Docker 两基址回归通过，报告 `build/app-install/qemu-james/d2-shared-run01.json` 已与本地输入摘要核对。完整候选 `d2-platform-04.bin` 为 6,899,240 B，SHA256 `cd00fc3037e0a6e2032951d1cf625927686bd1578499be2f8fa28165f4b888bd`，镜像及跨仓边界通过。集合模块进入编译清单，但生产 hook 仍是固定单包入口，未引用集合代码可被链接器裁掉。真实第二包、生产 Manifest 文件/选择路径和持续监督仍待完成，D2 未完成；未部署、未访问设备。

2026-11-04：D2 已抽出唯一共享维护服务、窗口和 screen_host；每 App 保留独立授权、文件/网络上下文和任务统计。宿主双上下文验证了增量注册、单次输入分发和轮询，原有 16 场景及九根页面导航通过 ASan/UBSan。Manifest 460 项检查与 RV32 编译重新通过。最新候选 `build/app-install/d2-platform-03.bin` 为 6,899,240 B，SHA256 `7ccddb1921fe9b01a26a992752af75314757941838d497be3e491ad5064fbb92`，新版诊断元数据与镜像验收通过。以下较早记录中的“共享容器待实现”已被本条进展替代。

边界：双上下文测试使用宿主 App 入口替身，生产开机仍为固定文件单包路径；Manifest 与原生多槽加载尚未接通。本轮未新增 QEMU 结果，真实第二独立包、共享窗口重建及集合健康监督仍待验证，D2 未完成。未访问实机、未部署。

D2 每 App 授权已接入平台上下文：Manifest 条目决定 ID、能力、TCP/UDP、任务数和页面槽；执行内存预留前核对包摘要及 image/heap/stack 声明。codex_status 保留原业务根，其他合法 ID 使用 `/resource/apps/<id>`；无效 ID、维护端口和跨根访问被拒绝。平台宿主验证增至 16 场景，ASan/UBSan、RV32 严格编译、跨仓边界通过。最新候选 `build/app-install/d2-platform-02.bin` 为 6,898,088 B，SHA256 `7fb8623b64ae8fc463fc788bfa9e554f9420adaaf5759dc56a3dfd2c7a39d60d`，镜像验收通过、未部署。当前仍需共享唯一维护/host 的多上下文容器；不能创建多个当前独立平台实例冒充完成。

D2 宿主接线进展：新增平台专用 `ap01_host_append`，独立 App 顺序注册时不重新初始化已有宿主。D1 平台 attach 已改用此入口；重复 ID、根/child 冲突、容量不足、正在切换时拒绝，成功保留已有页面、revision、transition 和输入状态。宿主 ASan/UBSan、平台 10 场景和跨仓边界通过。完整平台候选 `build/app-install/d2-platform-01.bin` 为 6,897,496 B，SHA256 `166a5de72b80570b797be03764ad4d4ca4412c2bc0792f97453896a40202c47d`，镜像验收通过，未部署。原生多槽 provider 和真实第二包仍未完成；这不是多个独立包已经运行的证据。

D2 进行中：已实现 [AMF3 完整集合编码](../../docs/app-manifest-v3.md)、真实 APX2 全包预检及按顺序启动的集合核心。宿主消毒器与 RV32 编译通过；坏第二包使零 App 启动，启动部分失败保留至重启并拒绝同次重载。报告 `build/app-install/d2-manifest/manifest-report.json`。原生平台仍为 D1 单槽，第二包是元数据 fixture，未宣称 D2 多 App 运行完成。完整非实机目标仍 active。

更新：2026-11-03，D1 非实机纵向验收完成。真实 Runtime 消费 ABI 3.0 直接 C 表，最终 ELF/APX2 零导入、72 项 BASE32、双链接基址归一化一致，两次独立构建包字节一致。最终包 203,696 B，SHA256 `581eafe33e3e524a3aefdb32e30905be75be304cfa202f14efcdbda113de1dcc`；见 [D1 记录](d1-direct-app.md)、[接口合同](../../docs/app-platform-api-v3.md) 和 `build/app-install/artifact-report.json`。

平台拥有维护/host/window/provider，固定文件先维护后 App 的加载路径已接通。完整平台候选 `d1-platform-v3-02.bin` 为 6,897,352 B，SHA256 `53629b54908e6681c73dad6f256c299a9d0245a800e9301c4b5fb7d0e0ab141c`，镜像检查通过。生产加载器宿主验证、六种坏 relocation、平台 ASan/UBSan 10 场景与跨仓边界通过。

james.local Docker QEMU 已执行真实包，两个地址均完成三入口、宿主注册、业务/发现线程、正常窗口销毁与重建，未重复启动线程。报告 `build/app-install/qemu-james/d1-v3-run02.json`。ROM I/O、维护监听、LVGL 和调度等仍为模型替身，不是完整原厂 ROM 启动。

**不可部署、未部署、未访问设备**：生产执行内存 backend 显式不可用，拒绝 reserve 并保留维护；H 尚未验证。QEMU 只在 james.local Docker 运行，未安装宿主依赖。

当前目标为复用现有多 App screen_host，使用直接 C 函数表和开机完整集合加载，支持单个/批量 App 更新，commit 后重启、集合级成功或回退。见 [新设计](../../docs/ap01-app-update-design.md) 与 [当前任务](task.md)。在线热卸载不再是目标。

已有证据：多 App 界面宿主及双 App 测试；统一构建和工具链；旧 APX2/单包日志/下载/HTTP/CLI 模块及宿主测试；旧真实 24 源 PIE 审计（当时剩 53 项导入；新 ABI 3 最终链接已为零）；james.local Docker 中小样本双基址 RV32 执行。它们不是新集合更新方案的完成证据。

尚未完成：D2 多包 Manifest/启动/全局输入仲裁/资源与健康监督，D3 集合日志/重启切换与整集回退，D4 HTTP/CLI/Bridge 单更/批更端到端。生产安装服务默认 501 的缺口未改变；实机可执行内存/cache/容量与掉电准入未通过。

文档迁移：总设计、计划和任务已重整；APX2 增补 ABI 3 编码，AUT2/HTTP 保留旧实现合同和版本提示。下列全部为历史记录，其中“最新”“下一步”“未实施”等按各自记录时间理解，不覆盖本节。

## 历史实施记录（修订前，保留证据）


更新：2026-11-02。

最新：按用户要求在 james.local Docker 内复用现有 AP01 QEMU 10.1.0。模型基线 55 项通过；同一最小映像在模型片内 RAM/PSRAM 两处执行通过，与 Unicorn 结果一致，SP/s0/s1 保持。依赖仅安装在容器内，无宿主安装、无设备访问。报告已取回，S1 实机准入仍未通过。见 [远端 QEMU 验证](s1-qemu-james.md)。

S0 设计完成；S1 已恢复本机平台/App 可复现构建，并完成真实 App PIE 编译清点；实机执行可行性未通过。S2–S5 未实施。未连接设备、未部署，本轮新增修改未提交。

本轮用户明确：不增加双槽，但允许失败回退，成功后可清理旧 App。设计已采用单运行实例、临时 previous 文件、持久试运行/回退记录和成功后清理。

本轮确认：0041 原件哈希匹配；App 配置的 24 个源文件和 include 目录存在；APX1 宿主测试通过 ASan/UBSan。当前 XIP 与 APX1 均不提供 0041 文件代码加载。本次仅针对 0041；0031 不部署 App，只保留为救援底座，不参与 App 加载验证。

按用户要求已完整快进合并 origin/master 至 `69015e7`，本地 README 与设计文档保留、无内容冲突。统一构建与依赖已补齐；固定 xPack GCC 12.5.0-1，修复时间 ABI 参数和 App 显式 time.h include。平台 6,879,560 B、App 7,052,968 B，候选验收与隔离平台构建通过；同路径重复完整构建 App 的 ROM 字节一致。产物保持不可部署候选。

真实 App 24 个源文件 PIE 编译通过；存在 105 个外部导入、GOT 与虚表/指针数据，尚未满足稳定 C ABI 或文件加载条件。下一步收敛服务边界及离线修正布局，并核实 0041 可执行内存和缓存机制；实机容量、两基址执行及存储掉电语义仍待验证。详细命令、哈希、兼容修复及验收边界见 [S1 构建记录](s1-build.md)。

证据与限制：[设计](../../docs/ap01-app-update-design.md)、[审阅](review.md)。现场仍以 codex_status/PROGRESS.md 为准。

S1 继续推进：最小 C++ 映像经两处离线链接归一化后相同，在两处 RV32 模拟加载地址执行通过，覆盖函数指针/虚表/data/bss/服务回调及 9 项拒绝检查；原 OTA Unicorn 检查 8 项通过。确认一次本对话 Python/Unicorn 宿主初始化 SIGILL，后续独立重跑通过，无设备访问或残留进程。从本地 Git 历史找回 0041 堆区域证据，23 条指令与原件逐字节匹配；多区域堆不能推导可执行性。见 [加载实验与内存证据](s1-load-probe.md)。

2026-11-03 离线实现进展：新增 APX2 包校验/加载核心、Python 包生成器与流式 SHA256。ASan/UBSan 下两基址、36 类损坏字段、全部截断位置与读失败通过；11 组独立 SHA 对照、15 项打包端拒绝通过。GCC 12.5 RV32 两个生产源文件编译通过。见 [包格式](../../docs/apx2-package-format.md) 与 `build/app-install/apx2/apx2-report.json`。这推进了 S1 格式与 S2 加载核心，尚未集成运行服务；事务、ABI 服务、真实 App/Bridge 接入仍未完成。上文“S2–S5 未实施”为此前状态，不能再理解为没有任何 S2 代码。

2026-11-03 生命周期进展：新增固件常驻 `app_generation_0041.h` 执行门与 RAII lease。close 后不接受新调用；只有已关闭且引用为零才能卸载/开始下一代；旧代际回调拒绝，代际计数不回绕。四线程 2,000 次卸载/重载竞争测试分别通过 ASan/UBSan 与 ThreadSanitizer；RV32 编译没有未定义符号，不依赖 libatomic。证据 `build/app-install/generation/generation-report.json` 和 `build/app-install/generation-tsan/generation-report.json`。尚未将真实 App 所有任务/UI/维护回调接到此门，也未实现资源取消与排空协调器，不能宣称停止/卸载已完成。已有 maintenance.c 的 AMT1 是早期实验，只能作为复用参考，缺少本需求的持久 trial/rollback 状态。

2026-11-03 维护调用点接入：Ap01MaintenanceBridge0041 增加代际快照，pairing/principal/online 与服务启动健康回调持有 lease。真实路由 ASan/UBSan 测试证明 close 后拒绝 App 回调，而设备码 health 仍返回正常；旧绑定不能进入新代际。独立维护回归通过设备码 OTA、轮换/重放、重启回执及无稳定记录切槽。平台候选 `build/app-install/platform-gate.bin` 为 6,880,248 字节，SHA256 `b0c17c520741ddfe9fa27882df2d73b4f40dce8a27cc9eb88ab7a0e7bf6ecb13`，完整镜像验收通过；跨仓边界检查通过。为本机宿主检查将 ELF 固件预算 section 限定到 RV32，目标预算保留。现有 App 仍 XIP，动态替换、任务/UI lease、持久事务和真实文件 App 接入仍待完成。

同轮带真实 XIP App 的完整构建及镜像验收也通过：`build/app-install/app-gate.bin`，7,053,656 字节，SHA256 `4f78e092ea1325226c9fd661dfa51f79c0b1818234c2fc9b7044b0c5c6fd2f6a`。这是现有入口兼容性回归，不是文件 App 执行证据。无实机访问。

2026-11-03 S3 日志基础：新增 AUT2 双元数据记录、序号/CRC/设备身份校验、读回提交和 Unknown 后重新加载规则。同事务身份不可变、计数不倒退、非法阶段跳转拒绝；新事务限无待清理终态。ASan/UBSan 下 256 个截断写入位置、逐字节损坏、丢失回执、重启次数和重置拒绝通过，RV32 编译通过。规范 [AUT2 日志](../../docs/app-update-journal.md)，报告 `build/app-install/journal/journal-report.json`。尚未接入下载、启动裁决、改名/清理、健康判据，不能称为已可安装 App。

2026-11-03 S3 下载接入：app_download_0041 将真实文件、AUT2 日志和 APX2 校验器连接。1024 字节连续块/一致重复块，部分尾部恢复，重新同步后读回再推进日志；Ready 需要完整 APX2 校验与原事务摘要一致。161 种部分写入/重启、日志 ACK 丢失、偏移未提交、同步失败、内容冲突/摘要拒绝通过 ASan/UBSan，RV32 编译通过。报告 `build/app-install/download/download-report.json`。未接入 HTTP/鉴权、空间预留、取消/清理或启动执行器。

2026-11-03 S3 启动选择/清理核心：app_selection_0041 按 APX2 完整摘要查找两个实际包的角色，先持久消耗 trial/rollback 再返回 Launch；重启后不重复同类启动，首装/旧包失败进入 Recovery。成功日志提交后才删除旧包并规范化 current，改名回执丢失可重放，不因旧文件存在撤销成功。7 组宿主流程含重复 commit、丢失启动记录 ACK、回退失败、清理失败通过 ASan/UBSan，RV32 编译通过；下载故障回归通过。报告 `build/app-install/selection/selection-report.json`。执行后端、资源排空、健康计时/业务写冻结、取消和接口接入仍未完成。

2026-11-03 健康判据接入选择器：公开 observe 取代直接 confirm，10 秒入口初始化、30 秒连续事件/原厂调度/维护计数推进、1 秒最大采样间隔、40 秒总预算；粘性失败不被后续好样本清除。当前代际业务写门在试运行/回退和 Unknown 时关闭，成功/回退终态后开放。15 组宿主流程覆盖三类计数停滞、缺口、时钟倒退、资源失败、身份拒绝、持续观察与写门，ASan/UBSan、RV32 编译通过。尚未接入真实计数源/执行器与全部业务写服务，不代表设备级冻结或运行健康已验证。

2026-11-03 S3 取消：Receiving/Ready 提交 Cancelled 后仅清理 incoming；切换/试运行取消转持久回退意图，已回退/成功状态重放不重启、不删 current。RecoveryRequired 清理失败候选后允许显式新事务，首装失败不依赖旧 App 即可重装。新增 7 组取消/回执丢失/清理故障流程通过；选择、下载与日志回归及 RV32 编译通过。接口仍未接入运行服务。

2026-11-03 维护协议离线接入：新增 app_http_0041，连接下载/日志/启动选择核心到真实 HTTP parser 与固件设备码鉴权。覆盖六条 App API，逐次 MAC/事务身份、序号/当前摘要围栏、块 SHA、principal 回执隔离、存储预算、stop_pending 与提交重放。HTTP 链 ASan/UBSan、RV32 核心编译通过；原独立维护 OTA 回归及跨仓边界检查通过。当前平台服务尚未绑定安装执行器，设备路径明确 501，不承诺已可部署安装。协议见 docs/app-update-http.md。

HTTP 路由改动后的完整独立平台构建及镜像检查通过：`build/app-install/platform-http.bin`，6,880,568 字节，SHA256 `96eddca0b029a62e83a622a77ad5116ceaf4fc137c616d40bcae373fe77bce85`。候选未部署，App handler 仍需执行器绑定。

2026-11-03 CLI：新增 app-update-client-0041.py，标准库 install/status/result/cancel，首次 mutation 前持久回执与原始围栏；同回执重连查询/续传、块 SHA、MAC/目标/偏移检查、终态回退拒绝、固定预算退避。注入对端测试通过 begin/chunk/commit/cancel ACK 丢失、无新 ID/重复提交、失败终态与预算/身份围栏。未联网或部署；尚待 CLI 与运行中 C++ 服务整体联调、真实执行器和 Bridge 接入。

2026-11-03 CLI/C++ 交叉联调完成：客户端真实 HTTP 构造经管道进入持续运行的 C++ parser、菜单鉴权、文件下载、日志和健康选择器。正常/丢 begin ACK/丢 chunk ACK/丢 commit ACK 四组均成功，begin/chunk/commit 各一次，重新打开成功回执只查询一次。服务侧 ASan/UBSan，候选文件逐字节等于输入。报告 `build/app-install/client-http/client-http-report.json`。无网络/设备，健康计数模拟、未执行 App 指令；实际 App C ABI、加载后运行、真实资源排空与 Bridge 仍未完成。

2026-11-03 真实 App 边界核对：native_0041.cpp 的 Runtime 当前拥有 Ap01NativeServices0041、业务/发现线程和 UI 回调，因此不能只设置 stop 再释放 Runtime。新增 C ABI v2 五入口与生命周期协调器，事件/健康持 lease，先 prepare_stop 再排空，stop 成功才可释放，超时/失败保留代码要求受控重启。宿主 ASan/UBSan、C11 头、RV32 布局/编译通过。真实 App 源码尚未改接，维护服务生命周期仍需从 App 中分离，服务编号/载荷也未冻结。

2026-11-03 真实 App 任务改接：固件 app_tasks_0041 以驻留跳板持有 generation lease，App 入口完整返回后再释放；上限 4 个任务，创建失败回收。codex_status 的业务/bootstrap 与 discovery 两任务已接入，维护回调带同一 gate/generation；新增内部任务停止/排空钩子，不宣称完成 UI 撤销或完整卸载。宿主/任务预算/RV32 检查、跨仓边界、统一构建测试通过。实际 App 候选 `build/app-install/app-tasks-v2.bin`，7,054,584 字节，SHA256 `2c3ebddac45eccc3658741697a794c481f8b33b16571e7bdde19427fa64e5a48`，完整镜像验收通过。未部署。

2026-11-03 UI 绑定生命周期保护：screen_port_0041 记录原生 event_root 和嵌套 dispatch_depth；重复同根绑定幂等，旧订阅仍在时拒绝换根；unbind 改为返回成功/拒绝，活动订阅或回调栈未退出时保留 timer/window。根 DELETE 回调返回后清除根记录，可复用 timer 重新绑定。宿主生产代码配假 ROM 调用的 ASan/UBSan 检查覆盖创建失败、重复绑定、嵌套 timer、DELETE、重绑定；RV32 编译和跨仓边界检查通过。完整 App 候选 `build/app-install/app-window.bin` 7,054,744 字节、SHA256 `4608dba5ce185895f80fd839f751557d59fc275c552d1b0275dde19ea23efad1`；独立平台候选 `build/app-install/platform-window.bin` 6,880,728 字节、SHA256 `7826471e1bf41724fbfe199818f1bd78eb85bc794b65913373627eddc9fe9448`；两份完整镜像验收通过。报告 `build/app-install/screen-binding/screen-binding-report.json`。这是拒绝不安全解绑的保护，不是运行中撤销原生事件的实现；子对象 draw 回调和维护服务仍需独立生命周期，真实 App 还不能释放。未运行 QEMU、未访问设备、未部署。

2026-11-03 映像内存所有权：新增 app_image_0041，将 APX2 校验/加载与五入口生命周期连接，要求后端先预留预算、发布缓存后才允许 start；失败启动仍走正常停止排空，超时/停止失败保留内存，禁止旧代际与重入。13 组宿主故障场景通过 ASan/UBSan、RV32 编译通过，报告 `build/app-install/image/image-report.json` 明确使用宿主入口，未执行包内指令。加入统一平台源清单，3 项构建测试与完整平台候选验收通过：`build/app-install/platform-image.bin` 6,880,728 字节，SHA256 `b9b6a28ed061f7b31978f8af063070311bb005857652fc159fd494537afe21ae`。当前尚无生产调用，链接器会裁掉未引用逻辑；真实执行后端、事务执行器与平台 handler 接入仍未完成。没有设备访问或部署。

2026-11-03 事务执行器：新增 app_runner_0041，串行连接选择/文件读取/映像加载/健康观察/停止排空与失败回退。8 组真实宿主文件日志 + 宿主入口流程通过 ASan/UBSan、RV32 编译；运行旧 App 的停止等待不会提前提交切换，Unknown 健康提交停止业务，停止失败/超时不释放也不启动第二 App。报告 `build/app-install/runner/runner-report.json`。统一平台源清单加入执行器/选择/日志，修正 paths 指针表为只读以满足 XIP 无可写静态数据约束。3 项构建测试、跨仓边界与完整平台镜像检查通过：`build/app-install/platform-runner.bin`，6,880,728 字节，SHA256 `ba3a38ab9fa5f4d1fe3fd3d5fbb818e4ef29af429ee56008a5e333d1a832dcd5`。尚未有生产调用，未接维护 handler、真实执行后端和真实 App C ABI，未执行包内 RV32 指令，无设备访问。

2026-11-03 维护 HTTP 与执行器组合：新增 app_installer_0041，统一持久日志、下载、选择、runner、HTTP，stop_pending 保持旧 App 停止而不在 Ready 查询时重启，成功后自动归位清理文件。客户端/C++ framed HTTP 联调换用该生产组合对象，四组首次安装/回执丢失 + 各一组运行中升级通过；升级 prepare_stop Pending 后查询原事务，commit 两次完成，最终 current 文件逐字节匹配。入口为宿主函数，实际调用 start/event/health/stop，未执行包内 RV32；报告 `build/app-install/client-http/client-http-report.json`，服务 ASan/UBSan。HTTP 回归、RV32 HTTP 编译、统一构建 3 项、跨仓边界通过。完整平台候选 `build/app-install/platform-installer.bin` 为 6,881,160 字节，SHA256 `0e7560b96c0ee7a3accc00f89830acf8dbb341dc3eb619f690e43844d8e0bb40`，验收通过。原生服务尚未构造安装服务/提供执行后端，设备默认 501 未解除；共享平台执行序列、业务服务写门与真实 App 仍待完成。无网络/设备访问。

2026-11-03 包内 RV32 执行：新增正式五入口 APX2 小样本与 RV32 验证程序，将生产 APX2 加载器/映像所有者/生命周期/SHA 编译进 guest。在 james.local Docker 内两基址（0x62fca000、0xa8000000）均通过两代加载、服务回调、event/health、prepare_stop Pending、引用排空/释放和错误摘要拒绝，全部整数保存寄存器与 SP 保持。最终 `build/app-install/qemu-james/abi-run02.json` 指纹核对通过；重建容器下 55 项模型基线通过。旧镜像已清理，本次依赖只在 Docker 重建，无宿主安装。详见 s1-qemu-james.md。仍是小样本与模型后端，不是完整业务 App、生产执行内存/cache 准入或完整安装服务在 QEMU 运行，目标未完成。

2026-11-03 成功回执补齐运行实例：HTTP port 增加执行器快照，返回 runtime_reporting 与当前 state/generation/写许可/加载摘要/版本；未 Running 不冒充运行，跨 principal 不泄露实例。CLI 新事务要求报告能力，succeeded 同时验证当前运行摘要/版本/代际与写门，历史成功但实例不可用时只查询原事务至预算，不重新安装。新增故障/隐私检查、ASan HTTP 回归、四组首次安装+运行中升级交叉联调通过，RV32 HTTP 编译与统一构建检查通过。平台候选 `build/app-install/platform-runtime-status.bin`，6,880,776 字节，SHA256 `39ba0d1a8e4fa323ebe9305ede2431e140891f96b93b459382334fea10aa604f`，镜像检查通过。生产平台构造点/真实 App/执行后端仍未接入；未访问实机。

2026-11-03 真实 App 开始改接 C 服务：增加 core service 1（单调毫秒/随机数/MAC）与 C11 助手，平台 invoke 持代际 lease，失败随机输出清零。codex_status 的配对随机回调及启动 MAC 查询已改走服务表。宿主 ASan/UBSan、C11、RV32、跨仓边界与 3 项统一构建检查通过；完整真实 App 候选 `build/app-install/app-core.bin` 7,055,576 字节、SHA256 `be044884b0424523bf7047954d9db7b0aa119544a0acabf4c0f54fb704ac0a32`，镜像验收通过。五入口样本接同一生产 core 服务，james.local Docker 两基址再次通过，报告 `build/app-install/qemu-james/abi-core-run01.json` 与本地输入摘要一致。当前仍 XIP Runtime 持 core/gate，不是完整独立服务所有权；网络/文件/内存/UI 及真实文件 App 生命周期继续待迁移。未部署、未访问实机。

2026-11-03 真实 App 只读启动：发现现有启动会 mkdir/迁移旧 Bundle 并持久更新 context，补充 BundleStore/Ap01Business 只读恢复模式。可加载/显示已有内容但不改文件，未配置可启动；业务命令/本地激活/配对保存拒绝，持久批准后显式可写恢复刷新 context。实际业务/配对/Bundle/渲染源码 ASan/UBSan 测试统计变更性 VFS 为零、文件逐字节不变，有效配对请求确认为 maintenance_busy；跨仓边界和统一构建检查通过。完整 App 候选 `build/app-install/app-readonly.bin` 7,056,024 字节，SHA256 `0f1b1034d7e3d5e6caacedac8a22786c9c29d8c8accdda0bc07fd74fbdad688a`，镜像验收通过。当前 XIP 默认可写启动未改成试运行；文件 App 五入口与平台写服务门尚待连接，不宣称已完成设备级写冻结。报告 `build/app-install/readonly/readonly-report.json`。

2026-11-03 底层文件服务：新增 service 2 固定 C ABI 与 app_files_0041，私有根路径验证、16 个带代际的 opaque 句柄、1 KiB 有界 I/O，写许可默认关闭；冻结与 VFS 操作同锁，未退出返回 Busy，已有写句柄不能绕过冻结。代际关闭/lease 排空后 drain 文件，关闭结果不确定时粘性保留要求重启。宿主 ASan/UBSan、C11、RV32 检查通过，报告 `build/app-install/files/files-report.json`。加入统一平台源，构建 3 项及完整平台镜像验收通过：`build/app-install/platform-files.bin` 6,880,776 字节、SHA256 `f8f2a13c8ccf106f55bab881cc1a442c6a6908ba48fb250728b95793e1643505`。尚未接真实 App VFS 客户端与安装执行器，设备级写冻结/文件资源排空仍未完成；无设备访问。


2026-11-03 真实 App 文件客户端：LittleFS 已经由 app_vfs_client_v2 通过 C service 2 访问固件文件服务，真实 Bundle/配对/渲染测试通过 ASan/UBSan，覆盖 3073 字节分块、第二块失败不误报成功及冻结后的旧句柄拒写。完整 App 候选 `build/app-install/app-file-client.bin` 为 7,059,736 字节，SHA256 `6b8d2db9033d72d2ff9e1aec9c59c4c61fbc6c7284009d44d82cc47a3801ae83`，镜像验收与跨仓边界检查通过。随后映像后端新增 drainResources：stop/lease 排空后确认常驻资源回收，失败粘性保留映像要求重启；15 组映像故障测试、runner 回归及 RV32 编译通过。该候选构建早于 drainResources 修改，后者本轮只做独立编译/宿主验证。当前 XIP Runtime 仍拥有文件服务并显式开放启动写许可；安装器持久状态与文件写门、生产 drain 绑定和常驻所有权尚未完成。未运行新的 QEMU、未访问设备或部署。


2026-11-03 执行器写许可联动：runner 按持久选择状态同步后端 writePermission，只有确认后才报告 business_writes；installer 每次 HTTP 操作后 reconcile，开放或撤权失败关闭代际门并停止排空。runner 测试接真实 app_files 与宿主文件系统，10 组流程含 start/试运行/回退/停止拒写、成功开放、开放失败、Unknown 后撤权失败通过 ASan/UBSan 和 RV32 编译。HTTP/CLI 四组首次安装及运行中升级回归通过。统一构建及完整平台镜像检查通过：`build/app-install/platform-write-gate.bin` 6,880,776 字节，SHA256 `18b43c51ab9b64e9846f06fc67051946c3f6c60a83d63e30bde8d3e25ef5e78d`。仍未构造生产常驻安装组合，镜像链接器会裁掉未调用逻辑；真实文件 App 的成功后可写恢复、生产资源绑定及完整包执行继续未完成。本轮未运行 QEMU、未访问实机或部署。


2026-11-03 服务路由与整体联调：新增常驻 app_services_0041 汇集 core/files，保留调用代际，拒绝未知服务。真实 XIP App 的随机数/MAC/VFS 已共用同一服务表。HTTP/CLI 四组首装及运行中升级后端接入生产路由、实际 core/files、writePermission/drain，逐请求核对底层写权限；每代故意遗留一个 fd 给常驻 drain，确认释放前回收及旧代际拒绝。ASan/UBSan、HTTP RV32 编译、跨仓边界通过。真实 App 候选 `build/app-install/app-service-router.bin`，7,059,800 字节，SHA256 `2e94e2d06940c36cf5063927a2c165f7ebfab955a187b720c7fe711bb05d7ce4`，完整构建/镜像检查通过，兄弟仓交接卡更新。core 底层在联调中为宿主替身，入口为宿主函数；未新增 QEMU 或实机运行。完整文件 App、其余 C 服务与生产常驻构造仍未完成，目标继续推进。


2026-11-03 网络服务底层：新增 service 3 固定 C ABI，8 个代际句柄、业务端口限制、TCP/UDP 类型校验、1 KiB 收发、AGAIN/EOF 区分和关闭不确定保护。原厂适配使用既有地址，poll 立即返回、收发非阻塞；accept 实际超时上限仍待模型/实机证据，不能由源码配置推出已验证。宿主 ASan/UBSan、C11、服务/适配 RV32 编译及 3 项统一构建测试通过。完整平台候选 `build/app-install/platform-network.bin` 6,880,776 字节，SHA256 `1cf9407c90940907d0b54bcf2a05c1244657468a95f95d0ea087826df560400a`，镜像验收通过。尚未接统一路由/真实 App 客户端；未引用代码可能被链接器裁掉。没有 QEMU/实机运行，目标仍未完成。


2026-11-03 真实 App 网络改接：app_network_client_v2 与统一路由连接 TCP/UDP 服务；core YIELD 为 1 毫秒调度等待，重试保留 deadline、有时钟停滞预算，关闭代际退出。真实 XIP HTTP/发现流与关闭已改接，排空钩子加入 network drain。网络/core ASan/UBSan、C11/RV32、HTTP/CLI 回归、跨仓边界与构建测试通过。最终候选 `build/app-install/app-network-client-v2.bin` 7,063,192 字节，SHA256 `bd453ec3a4acf35d35920460a5875b56527c955c00bd2c114c84b90b55b5d273`，完整镜像验收通过。首次候选之后修正重试计数写法，原路径重建被脚本拒绝，使用新候选路径完成当前源码构建。没有 QEMU 或实机运行；完整 parser 经网络客户端联调、UI/任务/内存 C 服务及生产常驻平台仍未完成。


2026-11-03 实际业务网络协议联调：扩展真实 App 只读测试，编译 http.cpp 和固件 parser，通过实际网络客户端/core/network/router 处理 wire 请求。8 组分段收发、AGAIN、3000 字节体、EOF、读写原期限、部分响应失败和关闭代际测试通过 ASan/UBSan，正常响应长度一致，异常 serve 返回 false；业务持久文件无变更，两个网络句柄经 drain 回收。报告 `build/app-install/readonly/readonly-report.json`。本轮修改测试与说明，不产生新 ROM 候选，无网络/实机访问。继续核对到 native_runtime 的 malloc/free/time/errno 仍含 ROM 依赖，需 App 私有分配入口和常驻预算服务，不能全局替换平台分配器。完整文件 App 与安装目标仍未完成。


2026-11-03 受限堆：新增 service 4 固定 C ABI、app_heap_0041 arena 分配器与 App 私有客户端，全部元数据/对齐包含于 heap_bytes；无平台 malloc 回退。代际、内点/重复释放、增长失败保留、合并、零堆、Busy 上限、lease 排空/清零和损坏保留通过 ASan/UBSan，5000 次随机操作保持所有存活块内容。C11/RV32 与统一构建检查通过。安装 HTTP/CLI 后端按实际包 heap_bytes 绑定，宿主入口经客户端分配，event/stop 持有至 drain，四组首次安装/升级回归通过；网络/真实只读业务回归通过。平台候选 `build/app-install/platform-heap.bin` 6,880,776 字节，SHA256 `b297443142ffac6081da766b26ddd621dfee363de20ec6567c222e6a83e831d7`，镜像验收通过。真实 App malloc/new 与生产 arena 后端尚未接入，未执行 QEMU 或实机，目标未完成。


2026-11-03 App 私有分配运行库：新增 app_runtime_heap_v2，绑定一次服务表，C malloc/calloc/realloc/free 与当前使用的 C++ nothrow new/delete 经受限堆；宿主验证不覆盖平台 malloc，RV32 PIC 符号/无静态初始化审计通过。当前实际 App 24 源 PIE 对象链接该运行库后分配引用全部解析，仍 98 项其他导入、35 个 GOT 重定位，报告 app-runtime-pic-v2/pic-report.json，不是完整包。APX2 小样本实际执行私有运行库，经生产 heap/router/image/lifecycle 在 james.local 既有 Docker 两基址通过，报告 `build/app-install/qemu-james/abi-heap-run01.json` 与本地输入指纹一致。guest 11936 字节 SHA c5c78102c164d7316e26c364e27239e49ab98520549180c41c99c0c63b695b98；包 SHA 7264196d304bfb1341dce0a2f5d2375c69a21701e5806e619c9cb05b291838c2。无宿主安装、无实机或部署。真实文件 App 入口、其他运行库/服务边界、GOT/最终打包与生产平台仍未完成。


2026-11-03 纯运行库分离：runtime_libc_0041 从平台 runtime 提取既有内存/字符串/格式化支持，共享源码独立链接；平台分配器不变。calendar 改纯 UTC+8 Gregorian 实现，移除 ROM timesub 依赖；99422 个宿主独立对照样本（每日首尾、闰世纪）及 ASan/UBSan、RV32 PIE 通过，32 位 time_t ABI 不变。真实业务/HTTP/网络回归、跨仓边界、构建测试通过。完整候选 `build/app-install/app-pure-runtime.bin` 7,064,792 字节，SHA256 `e44a07c80314fb24ed3bef15bf02cb51c9adcad1dbf0d48ce74c7bb5ab73b4df`，镜像验收通过；交接卡更新。当前 24 源 PIE 链私有 heap+libc+calendar+SHA 后剩 86 项导入，仍有 GOT、格式化/系统时间/math、原生服务与显示/任务边界，完整文件 App 未完成。本轮无 QEMU/实机运行或部署。


2026-11-03 UTC 服务与数学依赖核对：core 增加 UTC_SECONDS，App 私有 time() 通过不可变服务绑定调用，失败/关门/32 位越界返回 -1；宿主/C11/RV32 检查及 Docker QEMU 两基址实际调用通过，报告 abi-time-run01 指纹一致。完整 App 候选 `build/app-install/app-core-time.bin` 7,064,872 字节，SHA256 `d6fd33e51e0c2666bc5bf4dcc63f5508d5a5affe3f45687797b25faeb304de2d`，镜像/边界/构建测试通过。当前 App 24 源 PIE 对象接私有 heap/time/libc/calendar/SHA 与现有 libm/libgcc 后剩 54 项导入；新增组合重定位清单，仍有 GOT/RELAX/压缩分支等待最终规范化，不宣称数学或完整 App 已执行。snprintf、UI/任务及生产常驻服务/Bridge 仍未完成。没有宿主依赖安装、实机访问或部署。


2026-11-03 App 私有格式化：新增 app_runtime_format_v2，覆盖当前实际调用的 d/i/u/x/X、s/c、l/ll、宽度及左对齐/零填充；不支持的格式显式失败，不替换平台 snprintf。宿主 libc 差分、截断哨兵、整数极值、超大宽度计数与 ASan/UBSan 通过，RV32 PIE 仅引用 libgcc 整数除法。真实 24 源 App 组合链接剩 53 项导入，snprintf 已解析，报告 `build/app-install/app-format-pic/pic-report.json`，仍不是完整可加载 App。五入口执行样本增加实际 64 位格式化，离线双基址归一化一致；检查器允许局部分支的 RVC 重定位，并仅接受紧随指令重定位的有效 RELAX 提示。样本映像预算扩为 8 KiB、总预算包含 512 字节堆和 4096 字节栈，包输入地址避开执行区；首次模型运行因旧总预算拒绝，修正后 james.local 既有 Docker 两基址、两代生命周期通过，报告 `build/app-install/qemu-james/abi-format-run02.json`。包 5580 字节 SHA256 `740a66af88078e13609d195bc99b94583c4ba8074dc815bc5fa493334841e1bd`，输入与远端报告指纹一致。未安装宿主依赖、未访问实机、未部署；平台源未改接此私有模块，无新 ROM 候选。UI/任务 C ABI、完整文件 App 入口/打包、生产常驻安装组合与 Bridge 仍未完成。

### 2026-11-05 分批提交边界

业务仓库新增 HTTP 变更请求的整请求 writeScope 接入，准入位于 session/replay 更新之前；当前只读恢复宿主回归与跨仓库边界检查通过。该 HTTP 接入尚缺认证 C2 Busy 后同请求重试、提交回执重放的专项测试，既有 RV32 包证据不包含这次 HTTP 接入；本地激活与配对确认写入仍未闭环。此次仅提交源码与文档，不操作实机。

### 2026-11-05 C2 整请求准入专项

`test-app-readonly-0041.py --out build/commit-check --direct-files` 新增真实 Application/C2/Bundle 与生产 AppFilesV3 的组合测试：宿主线程身份、磁盘和 Busy 状态替身；状态查询在 Busy 时成功，认证 claim、Bundle begin/chunk/commit 均在 Busy 拒绝后以完全相同的请求重试成功，成功回执再次重放字节一致且无额外磁盘写入/上下文变更。ASan/UBSan 通过；报告 `build/commit-check/readonly-direct-report.json`。此前该项专项缺口已补齐，未覆盖 RV32 HTTP、HTTP 激活、本地激活及 UI 配对确认线程迁移，未操作实机。

### 2026-11-05 激活写入准入

远程 `/api/activate` 已纳入真实 C2 Busy 原请求重试及无额外写入的回执重放测试；两模板夹具验证切到索引 1。本地 `localActivate` 在完整 writeScope 中更新 context、落盘、恢复和渲染；Busy 不生成新 context、不写盘并显式返回 retry，worker 保留待处理请求且不覆盖更新的请求；真实 I/O 失败不重试。宿主验证 Busy 后切回索引 0、context 更新以及 I/O 失败分类，ASan/UBSan 通过。原生队列并发及实际 UI 执行仍待验证。

真实 App 交叉构建 `build/app-install/d2-business-activation-scope-01/app.apx2`，204928 B，SHA256 `94cf12d85e5cb59609b93c34df8388816806d829014cadc07336102191e4bdf7`；外部未解析符号 0、双基址归一化一致。该包包含 HTTP 和本地激活准入，尚未执行 QEMU；不继承旧包的执行证据，未操作实机。配对确认迁移仍待推进。

### 2026-11-05 配对确认迁移到 worker

ABI 3 App UI 的有效松键仅保存 event/revision（绑定锁保护、单个待处理确认），不调用持久 save。业务 worker 在 writeScope 内完成确认；Busy 保留，取消/替换通过 revision 淘汰，过期以 worker 当前时间判定，失败或执行后清除。无 writeScope 的旧端口行为保留。

真实 Application/Binding/AppFilesV3 宿主 ASan/UBSan 测试通过：UI 零写入、Busy 零写入、取消并换请求后旧确认不授权、有效松键延迟到期不授权、重新确认 Busy 后落盘一次及重复处理无写入。报告 `build/commit-check/readonly-direct-report.json`；这是顺序交错测试，不证明原生 UI/worker 并发。跨仓库边界检查通过。

交叉包 `build/app-install/d2-business-pair-worker-01/app.apx2` 205360 B，SHA256 `27bb07332aff6eef0726f48ea09c3638eadee8df2be23b652324f6fed0e0b2cb`，零未解析符号、双基址归一化一致；新包未执行 QEMU/实机。后续仍需原生并发和 RV32 HTTP/配对/激活链验证。

### 2026-11-05 新配对 worker 包的 RV32 回归

james.local 既有 Docker 镜像 `5eb73f3723ae561b43d9a416f1d29730fb5c945800fe5501b2e0ec6a8101365e` 中执行 `d2-business-pair-worker-01` 真包及 peer 集合，两基址 `0xa8000000`/`0xa8040000` 返回 0，栈和保留寄存器校验通过。生产 APX2 加载、集合启动、健康确认、Busy 后首次可写恢复、各 worker 停滞检测通过。报告 `build/pair-worker/qemu.json` SHA256 `eb7d1ef4d5e6f4de4a30c8f04abfc5405cfc6f91e185b167916a6259fa9ef12a`；guest、App、Manifest、peer、构建报告及运行脚本哈希与本地一致。

该 guest 仍用模型 VFS/network/LVGL 与协作调度；未发送配对/业务 HTTP 请求，不能替代这些请求路径的 RV32 验证，也不证明原厂 RTOS 并发或完整 ROM 启动。未安装远端宿主依赖、未访问实机。

### 2026-11-05 真实 RV32 worker HTTP 拒绝路径

模型网络新增可选单请求字节夹具，默认无请求，7B 分段读取/11B 分段发送；集合 guest 向真实 App worker 交付有效 C2 帧。james.local 既有 Docker 中两基址返回 0，校验请求被完整读取、连接关闭且无额外 mkdir：Trial Bundle begin → 503 app_trial_readonly；status → 401 unauthorized；系统 Busy 时 Bundle begin → 503 maintenance_busy、status → 503 business_offline；Busy 解除后 status → 401。

报告 `build/pair-worker/http-wire-qemu.json` SHA256 `93fb627caa9eeef9ea957948a35029d77cf12adaa52225157212d00df66d7a38`，guest `e9d707d14e23f12ee370b4c6ab038737473062c16f7cde111a95dac206b18d99`，真实包仍为 `27bb07332aff6eef0726f48ea09c3638eadee8df2be23b652324f6fed0e0b2cb`；构建报告及全部输入哈希已核对。此前“未发送业务 HTTP”的边界由此部分推进：现在覆盖实际 RV32 HTTP 拒绝路径，尚不覆盖认证成功、配对确认/Bundle 持久写入、原厂 socket 或原生抢占调度。模型仅空业务 VFS，不据此宣称磁盘成功路径已验。

### 2026-11-05 RV32 配对成功与认证状态

真实 App 经 resident pairing bridge 受理请求，模型触发真实 App 注册的绘制回调及共享窗口按下/松开事件；UI 无绑定写入，系统 Busy 时 worker 不写入，解除后 worker 完成 APB1 保存、读回验证和一次 rename。随后使用该令牌经模型分段网络、真实 HTTP/C2 worker 获得 200/session_nonce。两基址返回 0、栈/保留寄存器通过，james.local 既有 Docker 执行。

报告 `build/pair-worker/pair-http-qemu.json` SHA256 `e38e1193c1599e2e099b2c01f911d2e0aaf597fd801453531fe3e89f54c654d3`，guest `aece24c2223daf8cb8c0951afcde56e81f7ec25c7373e7edfcd04b18eca8d3e0`；App 仍为 `27bb07332aff6eef0726f48ea09c3638eadee8df2be23b652324f6fed0e0b2cb`，全部输入/构建报告哈希已核对。早期 400ms 调度不足以跨过 worker 最长 1s 的 listen wait，配对仍 awaiting；延长到 2s 调度后通过，没有改变生产状态机。

边界：绑定存储仅两个 512B 内存文件，单条 APB1 夹具；绘制完成是显式模型事件，配对入口直接经过 resident bridge（不覆盖维护 HTTP parser/鉴权），状态查询经过真实业务 HTTP parser。尚不证明硬件 VFS、掉电持久性、真实 LVGL 绘制/按键、原厂抢占调度或 Bundle 安装成功链。

### 2026-11-05 配对保存真实线程交错

只读/准入宿主夹具改用与原生 Runtime 相同的 atomic_flag 绑定锁语义，并以真实 std::thread 执行 `processConfirmation`，在底层 write 内用有界条件变量暂停。暂停期间 UI button/displayed/pairingUi 不进入状态，principal 返回 503，取消请求返回 maintenance_busy，第二次 worker 调用不产生写入；释放后原 worker 完成一次提交，重复处理不再写入。ASan/UBSan 与 ThreadSanitizer 均通过。

运行 `test-app-readonly-0041.py --out build/commit-check --direct-files --thread-sanitizer`；报告 `readonly-direct-tsan-report.json` SHA256 `34be5e98a76e527d17606c8f3a44cdcb0a97e25a8b3ca28498809f1b76a6bcfa`。该证据覆盖真实 Application/Binding/VFS 代码的宿主线程互斥，仍不替代原厂 RTOS 调度/锁内最长延迟、真实 UI 队列并发或设备磁盘时序。

### 2026-11-05 Bundle RV32 模型存储准备

从实际 BundleStore 安装流程确认需同时读 content 并追加编译缓存；模型 VFS 因而扩展为 6 个显式文件、16 个独立游标句柄：两绑定文件各 512B，incoming/content 各 256KiB，state.tmp/state.bin 各 2KiB，按需分配。支持 read/append/seek、关闭后 rename/remove、UI 写拒绝及超容量无写入；不模拟真实 flash 块/掉电。宿主 ASan/UBSan 对独立游标、边界和关闭所有权的专项及多 App 回归通过。

扩展后配对/认证状态 guest 在 james.local Docker QEMU 双基址仍返回 0；报告 `build/pair-worker/bundle-vfs-qemu.json` SHA256 `9a3e01a0f53f5c8a59abeca6b4da976b4b4514f8e653cdc1c2a71d028333b04d`，输入哈希逐项核对。Bundle claim/begin/chunk/commit 成功请求序列尚未接入 guest，因此 Bundle 安装 RV32 验收仍未完成。

### 2026-11-05 RV32 Bundle 安装成功链

在前述真实配对/认证基础上，guest 经实际 HTTP/C2 worker 执行 status 开 session、claim、Bundle begin/chunk/commit；最小单模板矩形 Bundle 的长度/CRC 随 fixture 固定，真实 BundleStore 执行校验、模板编译、正文追加缓存、readback 与状态提交。校验 content/state 存在、incoming 已退役、content 大于原始 JSON，提交后 status configured=true 且模板 ID 匹配；同一个 commit 帧重放回执逐字节一致且无新增写入/rename。

james.local Docker QEMU 双基址返回 0、栈/保留寄存器通过。报告 `build/pair-worker/bundle-http-qemu.json` SHA256 `255120870719aa0ad80b4f0fe76995020ed49cb4a9b76ff1e0e16f623e105894`；guest `f97a5bf2b820aab04c4f53a08dc90919d32fc667771fc6eac45760586a870229`，真实 App 包仍 `27bb07332aff6eef0726f48ea09c3638eadee8df2be23b652324f6fed0e0b2cb`；输入/构建报告/脚本哈希核对通过。

本次发现旧测试 guest 的不回收 bump heap 上界写到 QEMU 未映射的 a8400000 以上。故障日志定位在 malloc，最终陷入 trap 后 QEMU 被终止。guest 已改为复用现有 Ap01AppHeap0041 allocator/client，仅占已映射的 2MiB，可回收；这是测试 ROM malloc 替身，真实 ABI 3 App 不重新接入旧堆服务。运行器现在记录清理前退出状态并支持有界 guest 异常日志。

仍不证明硬件 VFS/掉电、原生抢占、真实显示、完整业务模板/中文字体、Bundle 重启恢复及完整 ROM 启动。此处是最小有效 Bundle 的真实 RV32 安装与请求幂等成功证据。

### 2026-11-05 Full AP01 template RV32 evidence

The guest builder now accepts --business-template and records source/header hashes. The complete codex-status-ap01.json (SHA256 98ef1b21821025070ad2c10c93a1befd1024c141e184002d6f36df40ac0b99af) was packaged without removing elements: 6496 bytes in seven chunks of at most 1024 bytes. The real C2 worker completed claim/begin/chunks/commit. Each chunk and commit replay returned identical receipts without additional writes/renames; final status was configured=true with codex-status-a.

Both relocation bases passed in james.local Docker QEMU. Report: build/pair-worker/full-template-qemu.json, SHA256 f867ca561d6a79150cf16b2fd4d0f7f1e5f47ae13db32348d58ccad7cdbd21c1. Guest SHA256: 157b85c10756a0713c3e048d7cf422244dee33ae61294d082f202beeccce0c5c. Source template, generated header, guest, App, Manifest, peer and build-report hashes were verified. External fonts, actual display, reboot restoration, hardware storage and original RTOS scheduling remain unverified.

### 2026-11-05 Exact business files across independent RV32 boots

Builder/runner now export and import a bounded BFV1 test snapshot (six explicit lengths plus exact file bytes). Real full-template installation at boot 42 produced bindings=86B, content/cache=17850B, state=420B; both bases exported SHA256 ca967b4588835572fd02efc67b9bc7757750ff7f716704c56d7b60989ca2cf51. A fresh guest at boot 43 loaded those bytes, accepted the retained binding token, reported configured=true and codex-status-a while trial writes remained zero. After health approval, writable restoration updated state while binding and content/cache bytes stayed identical. Output file snapshot SHA256 66b5185a2e0db210ecc7f483dc419d147c61fcb618e9a814c634fc3d4e1fc9ba.

Report build/pair-worker/business-resume-qemu.json SHA256 64be8ba043949f2bb55cf21d760775911a4e59728e0f5e2ca757da249334058c; guest 26f5e3699e85acfdbb78914511265fe7f8b49c4da29b69ea0eb4e920b5cefa2c. Both bases passed in james.local Docker, inputs and output files verified locally. This is independent-boot file handoff, not same-VM reset or physical power loss. Window rebuild/health remain checked; the empty-business rotation-to-peer assertion is inapplicable to configured restore and remains only in the empty scenario. External fonts, actual display, original RTOS, full ROM boot and hardware storage remain outside this evidence.

### 2026-11-05 Same-VM business recovery and journal regression

The existing QMP reset runner now supports exact BFV1 business-file handoff in addition to AUT3 journals. For each relocation base, installation and restore ran in one QEMU process with system_reset between stages; PC returned to 0xa0000000 and the next input matched the actual previous export byte-for-byte. Both stages returned 0 with preserved stack/registers. Report build/pair-worker/business-reset-qemu.json, SHA256 82f81230dad5e4cf07611a129b09d0a3c8ae2aa66f81be73c9c64071d2e31bbc.

The same updated runner also passed the existing fail-trial -> rollback journal fixtures at both bases, preserving exact journal handoff. Report build/pair-worker/journal-regression-qemu.json, SHA256 7a65d837def531f72f50492b6ff1a2b4d00856006e27f0c7b9beff6bdbbe0cc3. Script and both stage build-report hashes were checked. The journal regression uses its archived App/guest fixtures and is not evidence for executing the newest App in that rollback chain.

Boundary: the CPU really resets, but the runner reloads the guest and injects verified file bytes into the model VFS; this is not original-ROM reboot execution, flash persistence or power-cut recovery. Those boundaries remain open.
