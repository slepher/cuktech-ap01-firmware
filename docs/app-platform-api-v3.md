# App 平台 C ABI 3.0

2026-11-03，D1 冻结。权威声明为 `tooling/firmware-modules/app_abi_v3.h`、`app_platform_api_v3.h` 及其引用的公开 C 结构。目标 RV32IM AFC、little-endian、ILP32F；指针/int/size_t 为 32 位，变参遵循同一 ABI。不传 C++ 私有对象、String、异常、STL 或 TLS。

## 版本与生命周期

表头 `abi_major=3, abi_minor=0, struct_bytes=296, reserved=0`，能力位 core/files/network/memory/UI/tasks/binding 分别为 1/2/4/8/16/32/64；当前真实 App 必需全部 127。必需函数或嵌套表缺失则启动拒绝。只允许尾部追加兼容 minor，改变已有布局/语义须换 major。RV32 编译断言：UI 100 B、binding 16 B、HTTP 请求 48 B、文件表 52 B、网络表 36 B；原有 LVGL/host 表版本均为 1。

平台传入每 App 独立、不可替换的 table/context，保留至重启；文件/网络子表有自己的 context，调用时不得混用。平台先监听维护端口、预留映像及 App 预算，再校验/复制/修正包、发布缓存、调用 start。start 发布的 instance、注册回调与代码在失败后也必须保留，不在线释放或再次 start。未知 ABI 与旧五入口包拒绝；无 prepare_stop/stop。

`start(api, context, out_instance)`、`event(instance,id,payload,bytes)` 在 UI 执行器运行，不能等待 I/O 或重入 dispatch。start 的 OK 表示实例已发布，线程完成初始化后 health 才能 OK。health 返回 OK=0、PENDING=1、负数失败；App health 实现为并发安全快照，但 D1 `Ap01AppBootV3` 包装器只由 UI 执行器调用，监督线程须通过该执行器取快照，不得并发调用包装器。

事件 1 为 tick（null/0）；2 为原生 UI 事件（调用期间借用的 opaque pointer，bytes=0，须用表查询）；3 为原厂窗口重建（null/0，平台已更新 window）。3 复用同一 App/维护/业务线程，只重建页面。它不是在线更新/卸载。

## 服务与线程合同

- 核心时钟为单调毫秒；UTC 返回 int64 秒，当前 App 的旧 time_t 薄适配限制为有符号 32 位。random 成功为 0，长度 1–256；mac 成功为 0、写入 12 个十六进制字符及 NUL。pause 仅工作线程使用。
- 分配失败为 null；释放仅接受本 context 分配的有效指针或 null，不能跨 App/free 两次。平台使用 malloc/free 加配额头，不使用独立 Arena。配额包含管理头；realloc 增长时旧、新分配同时计费，失败保留旧内容；缩小时可保留原计费。底层分配器必须线程安全，D1 模型 bump allocator 不证明硬件行为。
- task_start 返回 0 或负数；异步工作线程执行 entry，不内联。栈须 16 B 对齐且至少 256 B；当前限 4 线程且累计栈不超过包声明。线程返回也不退还启动预算；创建失败归还预算。maintenance 的线程和存活期归平台。
- 文件操作只在工作线程进行，缓冲区在调用期间借用；平台锁、路径/句柄检查与写许可继续有效。write/rename 语义见 `native_vfs_api_0041.h`。D1 固定根 `/resource/codex-status`，写门默认关闭，不执行 trial/成功开放；D2 要审计维护与业务完整写集，当前根不是已完成的多 App 私有目录隔离。
- 网络工作线程使用直接表；TCP 接收/发送等待绝对单调期限，UDP 非阻塞。listen/accept 返回正句柄；close 成功 0，其余字节数/事件位见头文件。仅准许 TCP 18081/UDP 8767。2026-11-05 固定 ROM 静态审计确认阻塞 accept 不使用接收超时；共享 listener 已用原厂支持的 socket type 0x800 标志，空队列返回 EAGAIN。见 `tooling/scripts/audit-native-network-0041.py`。`test-native-network-qemu-0041.py` 在 james.local Docker 执行原厂标志传播和空队列 accept 分支已通过（连接分配/setup 为替身）；此修正不证明内核锁/调度时延，原厂 accept 的实际耗时仍未硬件验证；单地址空间也不提供沙箱。
- format 是平台 snprintf，固定 RV32 变参/标准返回值；App 不链接私有 formatter。errno_slot 是平台当前调用线程的 errno。format 不拥有传入缓冲区。
- busy/writes_allowed 只读；App 不能自行开放写门。bind 只成功一次，复制 C 回调表，release/acquire 发布。维护请求字符串和 body 仅调用期间有效；pairing 必须且只能 emit 一次，status 100–599、body 不超过 4096 B；平台复制后 emit 才返回。回调在维护工作线程执行，应有界，不访问 UI。绑定前维护仍工作，业务身份/配对返回未就绪。

## UI 与当前范围

唯一 host/window/注册槽属于平台。App 持有 slots/pages/pixels，并通过已存在的 screen_host/LVGL C 表注册及操作；所有 UI 调用/回调在同一执行器。不得直接修改平台 host/window；无需新增 UI 框架。正常根 DELETE 时 App 撤销页面状态，平台 destroy host/detach window；旧绘制异步结果仍使用现有 epoch 防护。根重建事件不重新创建业务线程。

D1 固定一个 codex_status 注册槽，保留原有输入/host poll 回调的直接转发。D2 需要把全局输入/blocked/poll 调度统一到集合平台，使多个 App 不重复消费输入；现有这些表成员不因此成为任意 App 可接管全局宿主的授权。ABI 3.0 表布局保持不变，新增集合能力需显式协商。

## 验证与非承诺

[D1 记录](../project-workflow/ap01-app-update/d1-direct-app.md) 包含真实源码、两次独立打包、完整平台 ROM 构建、宿主消毒器与 james.local Docker QEMU 双基址真实指令执行证据。QEMU 使用模拟 ROM I/O/维护监听、LVGL、线程、分配器和时钟；真实 App 为空业务数据启动，未在模型绘制实际 Bundle。

D1 固定路径 `/resource/app-current.apx2` 只提供文件完整性校验，不是签名/Manifest 授权。生产候选没有经过验证的可执行内存后端，明确拒绝 reserve，保留维护；不可部署。H 实机准入与 D2–D4 集合更新不由 D1 通过代替。

## 维护请求缓冲区预留（2026-11-05）

平台串行维护 worker 的 State 在业务 App 启动前分配，现内含 34817 B HTTP 工作区，复用至响应发送结束；处理器不得保留请求指针或递归复用。允许的头/小请求/ROM 分块上限保持 2048/4096/32768 B。普通 App HTTP 的缺省按请求分配路径保持不变，App C 表布局不变。

RV32 维护 State=35536 B（含工作区），维护对象=200 B，线程栈预算=16384 B。`native-core-audit.json` 报告此成本；旧 chunk/header 数字是容量上限，不应再叠加到预留工作区。已验证解析器不再依赖请求期数组分配，不能推广为响应构造、JSON 处理器、文件/Flash 或 ROM 内部完全无分配。1 MiB resident/16 MiB RAM 仍是未获硬件容量证明的模型预算；完整维护资源准入待完成。

维护与更新 JSON 回执现统一检查完整序列化长度；分配失败不得发出空/部分成功 JSON。HTTP 非 frame 空正文以静态 503 `result=unknown`、`error_code=reply_oom`、`next_action=query_original_operation` 兜底，不需要新 String 分配；动作可能已经提交，所以不能提示换事务重发。该兜底只保证能构造有界错误响应，仍依赖底层连接可写，并不保证业务/Flash 处理器在 OOM 下继续执行。
