# App 集合 HTTP v3 请求合同

2026-11-04：请求解析器 `app_set_http_v3.cpp` 已实现并测试；已绑定 0041 原生维护回调并完成离线链接，尚未在设备上验证。服务适配器已连接事务核心并通过宿主请求测试和 RV32 编译；当前响应提供事务阶段、偏移、错误和启动/健康快照，客户端仍待实现。旧 `/api/app/update/*` 不由新解析器自动解释为集合请求。

## 路由与身份

所有路径位于 `/api/app/v3/`，维护端口仍为 18080；先经现有设备码鉴权（Authorization Bearer），解析器本身不代替鉴权。沿用传输层查询参数 operation_id（或 request_id）、device_mac、offset、sha256，不新增请求头。除 status 外，事务 ID 必须为 32 位十六进制且非零，MAC 必须精确匹配设备规范字符串。principal 来自已鉴权维护入口，不能从客户端正文注入。

| 方法与路径 | 请求体 | 其他参数 |
| --- | --- | --- |
| GET `/api/app/v3/status` | 空 | 无事务要求，仍须设备码鉴权 |
| GET `/api/app/v3/update/result` | 空 | operation_id、device_mac |
| POST `/api/app/v3/update/begin` | ASB3 + 完整 AMF3 | operation_id、device_mac |
| PUT `/api/app/v3/package/0/chunk` | 1–1024 B 原始包字节 | operation_id、device_mac、offset、sha256 |
| POST `/api/app/v3/package/0/ready` | 空 | operation_id、device_mac |
| POST `/api/app/v3/update/commit` | 空 | operation_id、device_mac |
| POST `/api/app/v3/update/cancel` | 空 | operation_id、device_mac |

包索引只能是单字符 0–7，指候选 Manifest 按 ID 排序的条目；具体是否存在/属于 changes 由事务核心二次检查。offset 为无符号规范十进制（允许 0，拒绝前导零、符号、尾随字符及 uint32 溢出），offset+块长度也不能溢出。sha256 是本块字节 SHA256，须逐字节匹配。begin/chunk 的 Content-Type 必须为 application/octet-stream。

## begin 二进制头

恰为 64 B 头 + 原始 AMF3，不做 Base64/JSON 膨胀。总上限 3648 B，低于现有维护请求体上限 4096 B；保留传输层既有限额。

| 偏移 | 字节 | 含义 |
| --- | --- | --- |
| 0 | 4 | ASCII ASB3 |
| 4 | 2 | 小端头版本 1 |
| 6 | 2 | 小端头长度 64 |
| 8 | 32 | expected_current_manifest 内容摘要 |
| 40 | 8 | 小端 expected_current_manifest 集合版本 |
| 48 | 4 | 小端后续 AMF3 字节数，须恰等于正文长度减 64 |
| 52 | 12 | 全零保留 |
| 64 | 64–3584 | 完整 AMF3，由事务核心解析/验证摘要、资源、依赖 |

首次安装 expected 摘要全零、版本为 0；其他情况二者均非零。这里的版本是 Manifest 序号，不是上传进度频繁更新的日志序号。commit 绑定 begin 已冻结的事务身份与围栏，不允许临时改变候选集合。

解析只验证请求边界并返回借用的正文视图，不分配大缓冲、不修改文件或日志。调用者必须检查解析成功，且不能在 HTTP handle 返回后保留正文指针。语法/摘要错误 400，未知路径 404，错误方法 405，正文超限 413。事务级 Conflict/Unknown/Busy 等响应映射尚待处理器实现，不将这些状态混为解析错误。

验证包含合法 begin/chunk/ready，旧路径拒绝、字段保留位污染、MAC 不符、方法/索引错误、整数边界、零事务身份和块摘要不符；宿主 ASan/UBSan 与 RV32 编译通过。尚未进行客户端与真实 HTTP 服务器的完整 v3 往返验证。

## 服务适配器验证（2026-11-04）

`app_set_service_v3` 复用 begin/download/commit 核心。真实双包请求测试覆盖 begin 重放、跨 principal 拒绝、上传丢 ACK 后查询重载与续传、逐包发布、commit 重放、取消和排空超时。重复或被拒绝的 begin 不替换执行器，不重置 5 秒排空期限；Unknown 查询恢复保留同一事务的 commit 状态，新事务按 ID 隔离。取消不依赖 Manifest 仍可读取，缺失候选文件的恢复实例也可取消。

`test-app-set-journal-v3.py` 同时编译服务和文件预检器，以 ASan/UBSan 运行请求测试，并独立 RV32 编译服务。原生回调已绑定，但不代表设备 HTTP 安装或真实重启验证；事务范围自动清理已接入；完整错误映射尚待完善。

原生安装服务在维护启动前注册回调，在 AUT3 读取和开机选择后发布实例；未就绪返回 503。服务与 journal 同驻启动 worker 生命周期，HTTP 及健康提交共用维护操作锁，响应结束后释放。App 路由先通过设备码鉴权；OTA/Wi-Fi busy 或维护固件事务活跃时，更新写操作返回 409，精确的 GET `/api/app/v3/status` 与 GET `/api/app/v3/update/result` 继续读取原事务。查询不执行维护 tick，仍持有短时操作锁以保护 journal/cache 重载；锁被占用时返回 409，客户端稍后重查，不能绕锁并发访问服务。健康快照查询保持既有无锁路径。现有跨 principal 检查保留，生产 principal 为维护入口注入的固定身份。

该接线尚未解决原厂 OTA 自发启动的竞态、事务长期预算协调、孤儿文件扫描，完整 HTTP 传输→服务链已在宿主验证，但尚未证明 HTTP→服务→重启整链在 RV32 执行。硬件可执行内存 backend 仍拒绝执行，候选镜像不是已部署固件。

### HTTP 传输组合验证

宿主使用生产 `ap01ServeMaintenanceHttp0041`、维护路由和真实事务服务，按 17 B/19 B 分段读写请求和响应，上传实际业务包及 peer 包。覆盖错误设备码不进入服务、begin 与 commit 已持久化但响应发送失败、原事务重放不增序号、上传 Unknown 查询恢复、发布及排空超时；每次响应结束（包括发送失败）验证维护操作锁释放。未模拟真实网络、CPU 重启或原生 ROM I/O，取消缺失 Manifest 的恢复实例仍为服务级测试。

### 终态后台清理

原生启动 worker 在同一维护操作锁内调用服务 `tick`。仅对 Succeeded、FailedRolledBack、Cancelled 执行现有双槽终态屏障清理，最多每秒尝试一次；Manifest 缺失或存储错误保留 cleanup_pending。潜在已执行的删除/日志写入返回 Unknown 时冻结服务，后台不自行重复，须通过状态查询重载后再继续。成功清理后解除 transaction hold，但不会直接开放业务写许可，后续健康裁决仍是唯一授权入口。

此调度只清理本事务已知的包和临时文件，保留回执所需 Manifest；尚无私有目录枚举/孤儿包扫描。宿主验证成功与整集回退后的清理允许下一次 begin、空集合取消清理、缺失 Manifest 阻止清理，以及删除丢 ACK 的冻结/查询恢复；不是实际掉电耐久性证明。

### 实际启动集合快照

已绑定平台提供者时 `runtime_reporting=true`，`runtime.boot_state` 为 pending / started / partial_failed / failed；`complete` 仅在整个集合成功启动时为 true。`runtime.running` 按依赖启动顺序列出成功返回 start 的 App，包含 index、app_id、version、digest 和最近健康值。健康尚未采样时 health 为 null；sampled_at、health_state、fault 来自驻留监督器，HTTP 不调用 App。失败的 start 可能留下资源，partial_failed 不表示已卸载或其线程已停止。

`runtime.manifest/version` 来自 UI 已发布、此后不可变的加载器选择；不是持久日志候选摘要。部分启动也带该选择摘要，但 complete=false，只列成功前缀。预检失败/尚未启动时不提供选择摘要；初始空集合成功时列表为空、版本为 0。顶部 candidate_manifest/candidate_version 仍描述更新事务，客户端必须分别核对。

读取方仅在 acquire 观察到终止启动结果后读取加载器元数据；UI 执行器在结果发布后不再修改这些字段。宿主验证完整双包、文件预检失败、第二个 App start 失败只报告一个成功 App，以及服务返回的运行集合与事务候选不同。

### 客户端校验模块

`tooling/scripts/app_set_client_v3.py` 检查有界 AMF3 摘要、规范元数据、启动顺序/依赖和端口冲突，复用打包器核对 APX2 与集合条目。未变更包可省略，但服务端 changed_mask 内所有包必须提供；实际资源预算仍由平台裁决。

成功核验要求候选身份正确、新的非零 boot_id、cleanup_pending=false，以及完整健康运行集合和逐 App 身份匹配。未采样、部分失败、原 boot 或待清理只能继续查询；身份不符拒绝。模块已接入 `app-set-client-v3.py` 上传/持久回执循环，旧单包客户端不能直接调用 v3。

离线验证：
```sh
python3 -B tooling/scripts/test-app-set-client-v3.py --manifest build/app-install/d2-resume-set/set.amf3 --package build/app-install/d2-business-resume-01/app.apx2 --package build/app-install/d2-peer-beats-02/app.apx2
```
覆盖真实双包、单更/批更掩码、453 项无效输入拒绝及重启/运行集合确认，不连接设备。

### v3 CLI（离线流程验证完成，未操作设备）

```sh
python3 -B tooling/scripts/app-set-client-v3.py --host DEVICE:18080 --mac AABBCCDDEEFF --code-file /path/to/menu-code --manifest /path/to/full-set.amf3 --package /path/to/changed-a.apx2 --package /path/to/changed-b.apx2 --receipt /path/to/operation.json
```

完整集合 Manifest 必须包含未变更 App；`--package` 可重复，单更只需提供变更包。首次修改前以独占创建方式落盘事务 ID、原集合摘要/版本和原 boot；不保存设备码。恢复时沿用相同命令与回执，也可使用 `--action result` 或 `--action cancel`（这两项无需提供包/Manifest）。`--action status` 不需要回执。

上传/发布结果未知先查询原事务；SwitchPending 以后只查询。曾确认的回执返回过期时拒绝另建事务；缺失变更包可以补齐后使用原回执恢复。CLI 返回 0 表示 install 成功且运行集合核验通过（cancel 则为取消/已回退），1 为拒绝或失败终态，2 为未知/预算耗尽，保留回执用于恢复。`result` 的退出码只表示查询成功，不代表安装成功。

`test-app-set-client-flow-v3.py` 用真实包和注入协议对端验证 10 条单更/批更丢回复链、回执恢复、commit 后只查询、回退、取消和过期回执；未连接实机，CLI 与 C++ HTTP 模型的交叉验证见下。

### CLI / C++ HTTP 交叉验证

`test-app-set-client-http-v3.py` 启动宿主测试二进制的 `--http-peer` 模式，以管道传递真实 HTTP 字节。对端执行生产 HTTP 解析/鉴权、事务服务、AUT3 选择器、包预检和清理器。四条连续事务覆盖首装、A 单更（B 不上传且运行摘要不变）、A+B 批更和候选失败整集回退；begin/chunk/commit/ready 分别丢一次回复。前三次各模拟一次重启，失败事务模拟试运行及回退两次重启，核对 boot_id 12/13/14/16 和回退全部 App 身份。

报告 `build/app-install/set-client-http-v3-report.json` 保留结果及宿主二进制 SHA256。此对端使用内存 VFS、注入连续健康和模拟 CPU 重启，不执行 App 指令，不调用设备；TCP/urllib 通道另见下节，仍不得当作 RV32 或掉电耐久验收。

### 本机 TCP / urllib 验证

同一交叉测试增加 `--tcp`，只监听 `127.0.0.1` 随机端口，把真实 CLI `Transport`（urllib、无代理、不跟随重定向）的 HTTP 字节转交 C++ 服务。四条连续更新流程保持相同断言。begin/commit 在对端执行后直接断开连接，chunk/ready 发送不足 Content-Length 的响应再关闭，验证网络结果未知后查询原事务、只提交一次及整体回退。

报告：`build/app-install/set-client-tcp-v3-report.json`。此验证覆盖真实本机套接字与客户端异常处理，不访问设备或外网；后端仍是内存 VFS、模拟重启和注入健康，不能替代 RV32/实机验证。

### 集合资源能力

响应 `limits` 直接来自服务/加载器共用的 Ap01ManifestLimitsV3：package_bytes、image_bytes、heap_bytes、stack_bytes、tasks、pages 是全集合上限；capabilities 是允许位图；ram_bytes 是可计入 RAM，resident_bytes 包含维护及暂存预留。镜像总量逐 App 向上对齐 16 B，镜像+堆+栈不得超过 ram_bytes-resident_bytes。`app_max` 单独约束数量；`storage_reserve` 是 begin 空间检查的维护存储预留，不是 RAM 预留。

CLI 新事务在创建回执和发送 begin 前检查这些字段；Bridge `Manifest::check_capabilities` 使用相同算法。缺字段、超量或未知服务位拒绝。设备准入仍是最终裁决；客户端检查不是存储预留或硬件容量证明，当前原生预算仍为模型阶段配置值。
