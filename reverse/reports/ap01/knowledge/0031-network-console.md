# 0031 OTA 与网络诊断：统一 18080

2026-10-18。已改为同一 HTTP 监听端口，移除独立 18081 服务、独立诊断入口和旧构建脚本。

最新实机状态：临时 `gif-http` 诊断版完成采集后，已按用户要求通过独立 OTA 单次安装保留原版 GIF 的 `ap01-http/tail2` 槽尾版，实际 FW1 启动、槽尾模块、原 GIF 读回和用户操作均已确认，见[实机成功记录](0031-tail-physical-success-20261018.md)。历史离线候选不因本次成功自动获得部署验证。上传期间 STATUS 仍有实机超时记录，不把模拟并发通过冒充全部实机要求通过。

## 服务结构

监听 TASK 只负责 accept、创建请求 TASK 和关闭自己的连接副本，不同步等待 OTA 的整个请求。每个请求有独立任务组、描述符表和 16 KiB 栈；最多四个活动请求，避免无界任务/栈分配。启动时载入持久 OTA 日志，监听器本身不开固件写入句柄，后续诊断 TASK 因而不会继承其他上传任务的 Flash 句柄。

所有任务显式传入父任务的环境数组。原厂 `nxtask_create(..., envp=NULL)` 不继承环境；未修复时更新任务没有 `ro.boot.update_slot`，原厂写入封装回退打开 `app.bin` 并返回 ENOENT。原生回归捕获此问题，修复后 `flash_open rc=0,target_slot=2`。

独立 OTA 请求在调度锁下获取唯一写事务 fence，第二个上传返回 HTTP 409；读日志和诊断不获取此写 fence。日志请求复制 RAM 日志，之后发送独立快照，不把可变 RAM 缓冲区直接用于跨调度发送；诊断 LOGS 使用相同快照，避免磁盘追加/截断期间读出混合内容。必要的持久化仍由 OTA 事务写入 `/data/ap01-ota.jsonl`。

该 fence 只协调新 HTTP 上传请求，没有与原厂米家 OTA 共享锁。用户已明确两种 OTA 均人工触发、顺序执行，跨通道共享锁不作为本次部署前提，不禁用传统 OTA；尚未验证同时使用两个通道的行为。

## 接口

| HTTP 请求 | 行为 |
| --- | --- |
| `GET /health` | 服务版本 |
| `GET /logs` | Bearer 认证，最多 8192 字节 JSONL 快照 |
| `POST /firmware` | Bearer 认证、实际 Content-Length、传输 CRC；原厂非活动槽写入、读回校验、提交和复位 |
| `GET /diagnostic` | Bearer 认证，`Connection: Upgrade` 和 `Upgrade: ap01-diag/1`，成功返回 HTTP 101 |

Upgrade 之后为原生诊断协议，不再重复 AUTH 握手；每条诊断连接执行一个操作：

| 操作 | 返回 |
| --- | --- |
| `SHELL` | `OK SHELL` 后为原厂 NSH；使用 `sh`，不重跑 rcS |
| `STATUS` | 一行 JSON：构建、时间、shell PID、环境槽号、RAM 槽表及两槽启动头校验 |
| `LOGS` | `OK LOGS <字节数>` 加同一 RAM JSONL 快照 |
| `FLASH` | 追加 `%08x %08x\n` 物理地址/长度，返回长度、CRC32 和二进制数据 |
| `INTERRUPT` / `CLOSE` | 只向当前诊断 shell 发送 SIGINT / SIGKILL |

Flash 每次读取 1..65536 字节，范围在 16 MiB NOR 内；客户端按 64 KiB 分块导出完整范围，逐块校验，不自动重试。截断或 CRC 错误不会把当前块写入输出文件。中途失败时文件只有已核对的前缀，不能当成完整备份。

电脑端 `tooling/scripts/diagnostic-console-0031.py` 默认 18080。`--operation` 为 shell/status/logs/flash/interrupt/close；`--command` 可重复指定命令；Ctrl+C 使用另一条认证 HTTP Upgrade 连接发送 INTERRUPT。`--output` 新建文件，拒绝覆盖；Flash 导出必须指定输出。

认证后 NSH 保留原厂命令能力，包括管理员写入和重启命令。协议是本地明文 HTTP/原始升级字节流，未实现 TLS、SSH 或 WebSocket。原生 `dmesg` 的来源是 `/dev/ramlog`。网络未启动、Boot2、CPU 完全卡死和掉电阶段无法通过该接口采集；不承诺 RAM 崩溃日志自动跨复位保存。

## 原版 ABI

仅适用于 SHA256 `8a721fc8ef25458d415b2460e4a251e0503a82f7743fdff85b12612190e5c1cb` 的 0031。

| 地址/结构 | 用途 |
| --- | --- |
| `0xa019d362` | `nxtask_create(name,flags,priority,stack,entry,argv,envp)` |
| `0x62fc6bf8` | 当前 TCB 指针；TCB +8 为 group，TCB +12 为任务 ID |
| group +8 / +80 | 父组 ID / 环境数组，原厂 waitpid/getenv 交叉核对 |
| `0xa002828c` | `nx_dup2(tcb,oldfd,newfd)` |
| `0xa0032348` | 原厂 sh |
| `0xa002651e` | TCB 查询 |
| `0xa01b19e4` / `0xa01b1948` | 调度锁 / 解锁 |
| `0xa00520be` | 信号发送，负 errno 返回 |
| `0xa019f3ea` | 单参数 listen，内部 backlog=32 |
| `0xa0057eaa` | 物理 Flash 读取 (address,buffer,length) |

原厂 `waitpid` 完全忽略 options，不能用 WNOHANG 轮询活动任务。监听器使用调度锁下的 TCB 存活和父子关系检查；不会阻塞等待运行中的 shell，也不向其他任务复用的 PID 发信号。

## 验证与剩余限制

证据位于 Git 忽略的 `evidence/private/ota-expansion-20261018/`：

- `http-protocol-v1.json`：52 项 ASan/UBSan，含 Upgrade 认证/短写、OTA 事务和超时。
- `http-diagnostics-host-final-v2.json`：15 组宿主回归，含日志恢复、客户端错误、截断、CRC 和跨 64 KiB 导出。
- `http-native-concurrency-v12.json`：真实 guest NuttX TCP，没有替换 socket/dup2。上传保持未完成时，HTTP 日志、状态、物理 Flash 导出、NSH 命令均通过，第二个上传返回 409。关闭该上传后，长命令期间 STATUS、重复 shell 拒绝、SIGINT/SIGKILL 和重连通过；`diagnostic_probe_verified=true`。
- 三条同时活动的 guest TCP 连接曾停在第三条建连阶段，尚未确定具体连接容量或资源原因。回环两端均在设备内核中，不能直接等同真实 Wi-Fi 客户端；不把分阶段通过冒充三连接同时通过。
- `http-native-full-upgrade-v15-verified.json`：通过 `verify-http-native-upgrade-0031.py` 独立检查完整写入快照。目标槽逐字节匹配 6,826,328 字节探针包；分区表 CRC/年龄/槽选择有效；引导区、原活动槽、crash/ota 暂存和 reserve 未变，目标槽尾部填充未变。原厂 ff13 返回 0 后请求复位，尚未执行物理 Boot2。/data 日志和原厂 /resource 初始化不属于禁止写入范围。
- 对应原始 runner `http-native-full-upgrade-v15.json` 的顶层 passed=false：它的 safety 模式要求运行到观察窗口结束，本次在已预期的 reset 请求处停止。独立验证器逐项核对提交、快照、无异常和保护区，不能只依赖 runner 顶层字段。模拟停止在复位调用前，没有声称电脑侧已收到最终 HTTP 200。
- `http-unified-final-v2-boot.json`：最终候选在模拟映射下通过自检并记录 `AP01_HTTP_BOOT listener_pid=30 port=18080`；不能证明物理 Boot2 启动。

最终候选 `http-unified-final-v2-rom.bin` 为 6,821,512 字节，SHA256 `6455e59ac8079a19b78cc95f37be4e9550feb9e199143384ac35eef35ec9ae81`。格式 `ap01-http-0031-v1`。原版 256 字节启动头、GIF 与描述符、PEC、传统 miIO.ota 指令保留。启动钩子、rcS、ROMFS 校验和与新增槽尾模块属于预期改动。

`flashable=false`、`startup_mapping_verified=false`。真实 Boot2 未取得，原版至扩容镜像的物理启动尚未验证，当前不刷设备；并无证据证明槽尾必然不能执行。历史 18081 格式只在验证器中保留读取能力，以审计旧证据；构建器已不能生成该模式。进一步证据见[启动链调查](0031-expanded-boot-investigation.md)。

`http-native-full-upgrade-v13.json` 的全包源读取探针曾错误地把 PEC 区当普通 XIP 连续内存读取，产生 Load access fault；v14/v15 改用原厂物理 Flash 读取。该失败属于探针，不作为真实设备 Boot2 根因证据。所有失败报告保留。

最终汇总 `http-unified-final-verification.json` 将离线实现通过与部署条件分开记录：`passed=true` 仅覆盖离线范围，`flashable=false`、`physical_boot_verified=false`、`traditional_ota_concurrency_verified=false`、`three_simultaneous_native_loopback_connections_verified=false`。本轮没有访问或更新设备。
