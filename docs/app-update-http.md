# App 安装维护协议（离线接入）

> 2026-11-03 设计修订提示：本文保留现有单包/旧 ABI 实现及历史验证，不能作为新多 App 重启切换合同。目标已改为复用现有多 App 宿主、直接 C 函数表、Manifest 集合事务与重启切换；见 [当前设计](ap01-app-update-design.md) 第 4–7 节及 [任务](../project-workflow/ap01-app-update/task.md)。APX2 入口/ABI、AUT2 日志和 HTTP 单包字段需显式版本化；相关实现尚未修改。正文中的待办及导入数量是当时记录，当前状态以 [状态总览](../project-workflow/ap01-app-update/status.md) 为准。

实现为 `app_http_0041.{h,cpp}`，通过固件 `Ap01MaintenancePort0041::appUpdate` 接入已有 18080 HTTP 监听。不是 App 回调。未绑定安装执行器时返回 501 `app_install_unavailable`；当前生产启动代码尚未绑定，不能声称设备已经支持此协议。

所有 `/api/app/` 请求使用当前设备菜单中的八位码，`Authorization: Bearer <code>`。复用固件码校验和失败限流，不调用业务 owner/principal。固件传入稳定 principal `ap01-menu-maintenance`，请求 JSON 不能指定 principal。内部 handler 仍检查 principal 边界，不能读取别人的事务回执。

| 方法/路径 | 参数与行为 |
| --- | --- |
| GET /api/app/status | 查询能力、当前事务阶段和序号，不要求已有 App |
| POST /api/app/update/begin | 查询参数 operation_id、device_mac；JSON 见下 |
| PUT /api/app/update/chunk | operation_id、device_mac、offset、sha256；二进制 body，最多 1024 字节 |
| POST /api/app/update/commit | operation_id、device_mac；空 body；先完整校验至 Ready，再调用固件停止/排空端口，成功后提交 SwitchPending |
| GET /api/app/update/result | operation_id、device_mac；查询原事务，平台忙时仍可查询 |
| POST /api/app/update/cancel | operation_id、device_mac；空 body；按持久状态取消/回退 |

operation_id 是 32 位十六进制文本，device_mac 是 12 位文本，摘要是 64 位十六进制。各 query 字段不允许重复；旧解析器的 request_id 别名仍兼容，但与 operation_id 同时传入会拒绝。status 返回 MAC，其他操作逐次检查请求 MAC。

begin 的 Content-Type 为 application/json，恰好六个字段：

```json
{
  "device_mac": "010203040506",
  "app_id": "golden.app",
  "length": 320,
  "sha256": "<APX2 头内内容摘要，64 个十六进制字符>",
  "expected_current": "<当前已提交包摘要；首装为 64 个 0>",
  "expected_sequence": 0
}
```

新事务必须匹配 status 返回的日志序号与预期 current 摘要，并预留包总长加 4096 字节元数据空间。已有未登记 current 文件时不伪装为空设备。相同 operation_id 重放校对不可变身份，返回原进度/终态，不重复覆盖候选；不同参数返回冲突。旧事务被替换后查询返回 receipt_expired，不能靠重发旧 begin 越过序号围栏。

chunk 使用 application/octet-stream，其 query sha256 为该块本身的普通 SHA256，与 APX2 头内“全包摘要字段清零后计算”的摘要不同。只有块校验和同步/读回通过后才提交偏移。

响应含 device_mac、phase、state、sequence、error_code、retryable、next_action、chunk_max、package_max；可见事务额外含 operation_id、current_sha256、target_sha256、received、length、cleanup_pending。current_sha256 是已提交/可回退的当前身份，不代表新试运行已经成功。真实运行代际/摘要状态尚待执行器接入后补全。

202 表示进行中，200 的 phase 仍须区分 succeeded、failed_rolled_back、cancelled、recovery_required。503/网络超时只查询原 operation_id，不换 ID。停止未完成返回 stop_pending，Ready 不被误报为成功；重复 commit 不再次调用 stop。错误码来自真实拒绝阶段，不把下载 ACK 当成功。

独立 ROM 救援路径保留。固件执行器必须提供共享更新互斥和实际排空实现；HTTP 的 stop 端口返回 true 是严格承诺。当前测试用可控端口验证此调用边界，尚未替代真实任务/UI 排空。当前单线程路由会同步完成文件检查，不代表已测量完整实际 App 的 15 秒客户端预算；生产超时/异步校验仍须验证。

## 离线验收

```sh
mkdir -p build/app-install/http
python3 -B tooling/scripts/test-app-http-0041.py --out build/app-install/http \
  --package build/app-install/apx2/golden.apx2 \
  --tool-prefix build/s1/toolchains/xpack-riscv-none-elf-gcc-12.5.0-1/bin/riscv-none-elf-
```

测试使用真实 HTTP parser、固件菜单码鉴权、临时文件、APX2 校验、AUT2 日志和选择/健康核心，覆盖 begin/块/commit/result/cancel、错码/错 MAC、序号冲突、不同参数重放、块摘要失败、跨 principal 隔离、stop_pending、单次提交、30 秒健康提交和忙时查询。ASan/UBSan 与 HTTP 核心 RV32 编译通过。报告 `build/app-install/http/http-report.json`。没有执行包内指令、连接设备或部署 Bridge。

## CLI 安装、续传、查询与取消

`tooling/scripts/app-update-client-0041.py` 只使用 Python 标准库。必须显式指定 host、MAC 和包含当前八位菜单码的文件；不在命令行传码，也不将码写入回执。禁止 HTTP 重定向携带鉴权，单请求最多 15 秒，安装默认总预算 180 秒、查询退避上限 2 秒。

```sh
python3 -B tooling/scripts/app-update-client-0041.py \
  --host DEVICE:18080 --mac DEVICE_MAC --code-file /path/to/menu-code \
  --action status

python3 -B tooling/scripts/app-update-client-0041.py \
  --host DEVICE:18080 --mac DEVICE_MAC --code-file /path/to/menu-code \
  --package /path/to/app.apx2 --receipt /path/to/install-receipt.json

python3 -B tooling/scripts/app-update-client-0041.py \
  --host DEVICE:18080 --mac DEVICE_MAC --code-file /path/to/menu-code \
  --action result --receipt /path/to/install-receipt.json

python3 -B tooling/scripts/app-update-client-0041.py \
  --host DEVICE:18080 --mac DEVICE_MAC --code-file /path/to/menu-code \
  --action cancel --receipt /path/to/install-receipt.json
```

首次安装在发送 begin 之前用新文件保存随机 operation_id、设备/端点/包身份和原始序号围栏，文件权限 0600 并同步。重复同一安装命令会读取该回执，先查询原事务再从设备确认偏移续传。包、端点或 MAC 不符会拒绝。网络超时或 503 后只查询原事务；服务器明确没有回执时，仍只能使用同一 ID 和原始围栏重放 begin，不能刷新序号或偷偷生成新事务。

每块先计算普通 SHA256。ACK 偏移不能倒退、超包长，operation_id/目标摘要/MAC 必须匹配。成功还要求已提交 current 摘要匹配目标；保存过的终态不能在重连时退回进行态。客户端不会把 HTTP 202、start 返回或 failed_rolled_back 当成功。

install 退出码：0 为 succeeded，1 为明确拒绝或失败终态，2 为未知/预算耗尽，需继续查询同一回执。result 的 0 只表示查询成功，不能替代 JSON phase。cancel 的 0 仅表示 cancelled 或 failed_rolled_back。当前服务尚未暴露真实运行代际/摘要，CLI 成功证明的是认证事务提交，不是额外的硬件运行验收。

```sh
python3 -B tooling/scripts/test-app-update-client-0041.py
```

客户端测试使用注入协议对端，覆盖 begin/chunk/commit/cancel ACK 丢失、仅查询原事务、单次提交、回执续传、失败终态区分、查询预算、包和端点围栏；不访问任何网络或设备。真实 HTTP parser 的固件测试见上一节，CLI 到运行中固件/Bridge 的整体接入仍待完成。

## CLI → C++ HTTP 交叉联调

```sh
mkdir -p build/app-install/client-http
python3 -B tooling/scripts/test-app-client-http-0041.py \
  --binary build/app-install/http/test-http \
  --package build/app-install/apx2/golden.apx2 \
  --out build/app-install/client-http
```

先运行前文 test-app-http-0041.py 重建测试二进制。联调使用客户端的真实 Request 构造、HTTP JSON/身份检查和安装循环；测试 opener 将完整 HTTP 请求字节通过有长度边界的管道送入持续运行的 C++ HTTP parser/维护鉴权/下载/日志/选择器。没有网络或设备连接。

四种流程为正常、begin 回复丢失、chunk 回复丢失、commit 回复丢失。每种均持久写出与输入逐字节相同的包，返回 succeeded，begin/chunk/commit 各一次；丢失回复后立即查询原 operation_id；重新创建客户端并使用已成功回执时只执行结果查询。C++ 服务使用 ASan/UBSan。

健康计数与时间明确由测试 fixture 模拟，没有执行 APX2 包内指令；不能将联调成功称为真实 App 加载或硬件健康通过。报告 `build/app-install/client-http/client-http-report.json` 记录二进制、包和客户端哈希以及请求/修改次数。下一步重点为实际 App 的 C ABI、执行器和资源生命周期接入。

## 固件安装服务组合（2026-11-03）

`app_installer_0041` 将 journal、download、selection、runner 和 HTTP handler 组合为同一个常驻对象。begin 加载启动记录，tick 根据持久决定启动/观察/回退，并在成功后重试文件清理；event 接受平台分发的业务事件。维护路由的 appUpdate 回调可以直接调用其 handle。stop_pending 时旧 App 保持停止中或已停止，不因为下一次查询看到 Ready 就重新启动；只有持久 SwitchPending/RollbackPending 才调度下一次启动。启动记录不确定时禁止猜测选择，但已经开始的停止排空仍继续。

调用前提：handle/tick/event、文件更新和原生 OTA/Wi-Fi 变更使用同一个平台执行序列；组合对象不另开线程，也不提供一个与 OTA 无关的独立锁。platformBusy 由平台提供。当前原生服务构造点尚未建立这个对象，仍缺真实执行后端、共享执行序列接入及实际 App C ABI；因此当前设备端默认 501 的安装限制没有解除。

客户端交叉测试的 `--serve` 端已换用此生产组合对象，经过真实 HTTP parser/设备码鉴权、下载/文件、APX2 加载、五入口 start/event/health/prepare_stop/stop、健康确认及 current 归位。后端入口是宿主测试函数，时钟与原厂/维护计数模拟，不能作为包内 RV32 执行证据。四组正常/丢 begin/chunk/commit ACK 均成功；每组还完成运行中第二次升级，prepare_stop 首次 Pending，commit 共两次，其间查询原事务；首次安装 begin/chunk/commit 各一次。报告 `build/app-install/client-http/client-http-report.json`。

## 运行实例核对（2026-11-03）

`runtime_reporting` 表示服务已绑定执行器状态快照。允许查看当前事务的 principal 还收到 `runtime`：`state`（idle/running/stopping/recovery/unknown/reboot_required）、`generation`、`business_writes`；仅 Running 时附带已加载映像的 `sha256` 和 `version`。停止中/恢复中即使内存被保留，也不冒充正在运行。不同 principal 仍只能看能力，不能读取他人的运行摘要、版本、代际或事务回执。

`current_sha256` 是持久提交结果；`runtime.sha256` 是此刻执行器中的实例，两者不能混用。succeeded 记录不会因晚发故障被改写，但设备可能已经停止该 App。CLI 在新建事务前要求运行实例报告能力；确认 succeeded 时同时核对提交摘要、Running 状态、有效 uint32 非零代际、业务写许可、实际运行摘要和包版本。运行状态缺失/恢复中时只查询原事务，预算耗尽返回不确定，不发送新的 begin/commit；正在运行的摘要/版本不符则拒绝成功。回执仍保存历史 succeeded，供人工区分“曾提交成功”和“现在仍正常运行”。

检查新增了不支持运行报告时禁止上传、缺失/停止实例、布尔伪代际、写门关闭、错误摘要/版本，以及跨 principal 隐私隔离。CLI/C++ 安装服务四组首次安装与四组运行中升级均通过新核对。此快照仍依赖原生平台接入真实执行器；仅有宿主联调不能宣称设备能力已上线。
