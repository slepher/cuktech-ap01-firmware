# App 平台 C ABI 3.1

当前基础平台为原厂 **1.0.2_0055**，修改版为 **0.1.3**，独立 App 使用 ABI 3，平台函数表为 3.1。Release 中的 `ap01-0055-app-platform-0.1.3.bin` 提供 App 加载能力，`ap01-0055-base-0.1.3.bin` 不加载 App；构建与发布见 [README](../README.md)。

权威声明为 `tooling/firmware-modules/app_abi_v3.h`、`app_platform_api_v3.h` 及其引用的公开 C 结构。目标 RV32IMAFC、little-endian、ILP32F；指针/int/size_t 为 32 位，变参遵循同一 ABI。不传 C++ 私有对象、String、异常、STL 或 TLS。

## 版本与生命周期

平台表头为 `abi_major=3, abi_minor=1, struct_bytes=304, reserved=0`；`write_scope` 指针位于偏移 296。能力位 core/files/network/memory/UI/tasks/binding 分别为 1/2/4/8/16/32/64；App 所需能力由包和清单声明，`codex_status` 需要全部 127。必需函数或嵌套表缺失则启动拒绝。只允许尾部追加兼容 minor，改变已有布局/语义须换 major。RV32 编译断言：UI 100 B、binding 16 B、HTTP 请求 48 B、文件表 52 B、网络表 36 B；LVGL/host 表版本均为 1。

`write_scope(context, callback, argument, result)` 为 worker 上的同步写操作准入。INVALID 表示缺失 callback/result，UNSUPPORTED 表示无文件能力，PENDING 表示没有执行回调且 result 不变；OK 只表示执行完成，业务成败取决于 result 中的回调返回值。回调不得抛异常、异步继续、嵌套 scope 或等待另一个写者。同线程 VFS 调用借用整段租约，其他线程不能借用；撤权等待已准入操作完成。调用方通过 `ap01WriteScopeV3` 或 `ap01RuntimeWriteScopeV3` 检查 major=3、minor>=1、字段覆盖长度及非空入口；不满足要求时返回 UNSUPPORTED，不越界读取。

平台传入每 App 独立、不可替换的 table/context，保留至重启；文件/网络子表有自己的 context，调用时不得混用。平台先监听维护端口、预留映像及 App 预算，再校验/复制/修正包、发布缓存、调用 start。start 发布的 instance、注册回调与代码在失败后也必须保留，不在线释放或再次 start。入口为 start、event、health；不提供 prepare_stop/stop。

`start(api, context, out_instance)`、`event(instance,id,payload,bytes)` 在 UI 执行器运行，不能等待 I/O 或重入 dispatch。start 的 OK 表示实例已发布，线程完成初始化后 health 才能 OK。health 返回 OK=0、PENDING=1、负数失败；App health 实现为并发安全快照，`Ap01AppBootV3` 包装器只由 UI 执行器调用，监督线程须通过该执行器取快照，不得并发调用包装器。

事件 1 为 tick（null/0）；2 为原生 UI 事件（调用期间借用的 opaque pointer，bytes=0，须用表查询）；3 为原厂窗口重建（null/0，平台已更新 window）。3 复用同一 App/维护/业务线程，只重建页面。它不是在线更新/卸载。

## 服务与线程合同

- 核心时钟为单调毫秒；UTC 返回 int64 秒，App 的 time_t 薄适配限制为有符号 32 位。random 成功为 0，长度 1–256；mac 成功为 0、写入 12 个十六进制字符及 NUL。pause 仅工作线程使用。
- 分配失败为 null；释放仅接受本 context 分配的有效指针或 null，不能跨 App/free 两次。平台使用 malloc/free 加配额头，不使用独立 Arena。配额包含管理头；realloc 增长时旧、新分配同时计费，失败保留旧内容；缩小时可保留原计费。底层分配器必须线程安全。
- task_start 返回 0 或负数；异步工作线程执行 entry，不内联。栈须 16 B 对齐且至少 256 B；当前限 4 线程且累计栈不超过包声明。线程返回也不退还启动预算；创建失败归还预算。maintenance 的线程和存活期归平台。
- 文件操作只在工作线程进行，缓冲区在调用期间借用；平台锁、路径/句柄检查与写许可继续有效。write/rename 语义见 `native_vfs_api.h`。App 私有根由 `api.private_root` 提供：`codex_status` 使用 `/resource/codex-status`，其他 App 使用 `/resource/apps/<app_id>`。写入由共享事务门控制；健康批准并满足事务条件后开放，撤权时等待已准入写入排空。
- 网络工作线程使用直接表；TCP 接收/发送等待绝对单调期限，UDP 非阻塞。listen/accept 返回正句柄；close 成功 0，其余字节数/事件位见头文件。监听端口由清单授权，不能占用维护端口 18080，同一集合的 App 不能声明重复的 TCP 或 UDP 端口。`codex_status` 默认使用 TCP 18081／UDP 8767。共享 listener 使用非阻塞 socket，空队列返回 EAGAIN；实际调度时延仍需实机验证；单地址空间也不提供沙箱。
- format 是平台 snprintf，固定 RV32 变参/标准返回值；App 不链接私有 formatter。errno_slot 是平台当前调用线程的 errno。format 不拥有传入缓冲区。
- busy/writes_allowed 只读；App 不能自行开放写门。busy 包括维护未监听、原厂 OTA、平台维护 OTA 和 Wi-Fi 切网状态；它是观察值，不是跨检查/写入的锁，不能替代集合写门或平台操作锁。bind 只成功一次，复制 C 回调表，release/acquire 发布。维护请求字符串和 body 仅调用期间有效；pairing 必须且只能 emit 一次，status 100–599、body 不超过 4096 B；平台复制后 emit 才返回。回调在维护工作线程执行，应有界，不访问 UI。绑定前维护仍工作，业务身份/配对返回未就绪。

## UI 与当前范围

共享 host/window 和各 App 注册槽由平台管理。App 持有 slots/pages/pixels，并通过 screen_host/LVGL C 表注册及操作；所有 UI 调用/回调在同一执行器。不得直接修改平台 host/window。正常根 DELETE 时 App 撤销页面状态，平台 destroy host/detach window；异步绘制结果使用 epoch 检查有效性。根重建事件不重新创建业务线程。

集合共享一个屏幕宿主，每个 App 持有自己的注册槽与页面。平台集中分发输入、阻塞状态和轮询，避免多个 App 重复处理同一输入。

## 集合启动与执行内存

平台根据 journal 选择 `/resource/app-store/manifests/<content-digest>.amf3`，核对清单身份、版本、包摘要和预算后启动集合。文件读取在 worker 执行，App start/event/health 由 UI 执行器调度。无可启动集合时保留维护服务。

执行内存后端按 16 字节对齐分配映像，仅接受 `0xa8000000` 至 `0xa8400000` 范围内的分配结果，检查容量和入口后同步数据与指令缓存。已发布的代码保留至重启，不支持在线卸载。地址检查和离线模型不代表完整冷启动、外设或硬件容量已验收。

## 维护请求缓冲区预留

平台串行维护 worker 的 State 在业务 App 启动前分配，包含 34817 B HTTP 工作区，复用至响应发送结束；处理器不得保留请求指针或递归复用。允许的头/小请求/ROM 分块上限为 2048/4096/32768 B。普通 App HTTP 默认按请求分配工作区。

维护线程栈预算为 16384 B；State、维护对象和工作区成本以本次构建的 `native-core-audit.json` 为准。chunk/header 数字是容量上限，不应叠加到预留工作区。解析器使用预留数组，不能推广为响应构造、JSON 处理器、文件/Flash 或 ROM 内部完全无分配。1 MiB resident/16 MiB RAM 仍是未获硬件容量证明的模型预算；完整维护资源准入待完成。

维护与更新 JSON 回执检查完整序列化长度；分配失败不得发出空/部分成功 JSON。HTTP 非 frame 空正文以静态 503 `result=unknown`、`error_code=reply_oom`、`next_action=query_original_operation` 兜底，不需要新 String 分配；动作可能已经提交，所以不能提示换事务重发。该兜底只保证能构造有界错误响应，仍依赖底层连接可写，并不保证业务/Flash 处理器在 OOM 下继续执行。
