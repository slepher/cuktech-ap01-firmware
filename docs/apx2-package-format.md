# APX2 v2 包格式（离线实现）

> 2026-11-03 设计修订提示：本文保留现有单包/旧 ABI 实现及历史验证，不能作为新多 App 重启切换合同。目标已改为复用现有多 App 宿主、直接 C 函数表、Manifest 集合事务与重启切换；见 [当前设计](ap01-app-update-design.md) 第 4–7 节及 [任务](../project-workflow/ap01-app-update/task.md)。APX2 入口/ABI、AUT2 日志和 HTTP 单包字段需显式版本化；APX2 已增加下述 ABI 3 版本隔离，集合事务尚未实现。正文中的待办及导入数量是当时记录，当前状态以 [状态总览](../project-workflow/ap01-app-update/status.md) 为准。

## D1 增补：直接 C ABI 3（真实包非实机验收完成）

容器仍为版本 2；头偏移 24/28 为 ABI 3/0。偏移 88、92、96 分别为 start/event/health 的 text 偏移，均半字对齐且至少含 2 字节；100、104 必须为零。三个入口均必需，无事件功能可使用 no-op。签名见 [app_abi_v3.h](../tooling/firmware-modules/app_abi_v3.h)，冻结表及线程/所有权语义见 [ABI 3.0](app-platform-api-v3.md)。

Python manifest 显式增加 `abi_major: 3`、`entries: [start, event, health]`；未指定 major 的旧 manifest 仍生成 ABI 2。加载端 `Apx2Limits.abi_major=3` 只接受 ABI 3，默认 2 只接受 ABI 2；旧五入口执行器无论调用者参数如何均拒绝 ABI 3。ABI 3 映像进入 start 后保留至重启，不要求 prepare_stop/stop。

新黄金包 SHA256 `39eb8693564d0f9dbd9786624f45499584726269cd4eb99747b9b38f2b050a0f`；新旧互拒、保留入口非零拒绝与原有完整校验通过。报告 `build/app-install/apx2-report.json`；RV32 validate 静态帧 944 B，load 240 B，不是整条调用链高水位。黄金包仅验证格式，不能执行；另已完成真实 App 最终包及 Docker QEMU 双基址执行，见 [D1 最终记录](../project-workflow/ap01-app-update/d1-direct-app.md)。后续正文保留 ABI 2 历史合同。

本规范对应 `tooling/firmware-modules/apx2.{h,cpp}` 与 `tooling/scripts/apx2.py`。
目前实现包校验和有界加载，尚未接入运行中的 0041 维护服务，也未证明完整业务 App 或实机可执行。
格式与生命周期 C ABI 分开：以下五个入口的槽位已预留，调用签名、服务表和生产 App 链接仍待完成，不能将测试包用于部署。

所有整数为无符号小端 uint32；不序列化本机结构体。文件为 256 字节头、初始化映像、BASE32 修正记录，不允许尾随字节。

| 头偏移 | 字段 | 要求 |
| --- | --- | --- |
| 0 | magic | ASCII APX2 |
| 4, 8, 12 | 格式版本、头长、文件总长 | 2、256、实际文件大小 |
| 16, 20 | 目标、ISA | 1=0041、1=RV32IMAFC/ILP32F |
| 24, 28 | ABI 主、次版本 | 2、0 |
| 32, 36 | 必需服务位图低、高 32 位 | 必须为平台服务集合的子集 |
| 40, 44 | 映像文件偏移、字节数 | 256、4 的倍数 |
| 48, 52 | text 映像内偏移、字节数 | 0、非空 |
| 56, 60 | rodata 映像内偏移、字节数 | 偏移对齐 16 |
| 64, 68 | data 映像内偏移、字节数 | 偏移对齐 16，末尾等于映像末尾 |
| 72, 76 | bss 字节数、加载对齐 | bss 紧随映像、16 |
| 80, 84 | App 堆、栈预算 | 栈至少 256 且对齐 16；不是加载器自身栈 |
| 88–104 | 五个生命周期入口 | 每项 uint32，半字对齐且至少 2 字节位于 text |
| 108, 112 | 修正表文件偏移、记录数 | 紧随映像；每条 8 字节 |
| 116, 120, 124 | 可读数据版本最小、最大、写版本 | 包含平台当前数据版本且写版本等于当前版本 |
| 128–159 | App ID | 1–31 字节 ASCII，余下全零 |
| 160–191 | App 版本 | 同 App ID 编码 |
| 192–223 | 内容 SHA256 | 计算时将本字段清零，覆盖整个文件 |
| 224–255 | 保留 | 全零 |

App ID/版本字符限于英文字母、数字、`.`、`_`、`-`、`+`。App ID 可由平台额外精确匹配。
text、rodata、data 顺序排列、不重叠；中间对齐填充必须为零。bss 不存文件，加载时清零。
平台同时限制包大小、总 RAM（映像+bss+堆+栈）、单独堆/栈预算。上述数值使用宽整数检查后才能缩窄。

每条修正为 `[destination, target]`，均相对映像基址。destination 严格递增、4 字节对齐，完整字必须在 rodata 或 data，源字必须等于 target。
target 必须落在实际 text、rodata、data 或 bss 内，不能指向填充和末尾之后。加载后该字变为 `base + target`。
不接受 ELF 重定位类型、任意符号或原厂地址修正。外部服务须通过未来的版本化服务表传入。

`apx2Validate` 不分配内存、不执行代码，读失败或拒绝时输出视图清零。每次读请求不超过 256 字节。
`apx2Load` 先完整校验，再检查调用者提供的容量、16 字节基址对齐和 RV32 地址溢出，复制、清 bss、应用修正。
复制开始后的读失败清零目标区域；调用者不得执行失败映像。
调用者必须在整个校验/加载期间独占不可变文件，并负责可执行内存分配、缓存同步和资源排空；核心不提供文件锁或内存隔离。
SHA256 证明内容一致性，不提供发布者签名；安装授权由固件独立维护协议负责。

## 可复现检查

```sh
mkdir -p build/app-install/apx2
python3 -B tooling/scripts/test-apx2.py --out build/app-install/apx2 \
  --tool-prefix build/s1/toolchains/xpack-riscv-none-elf-gcc-12.5.0-1/bin/riscv-none-elf-
```

宿主 ASan/UBSan 覆盖两基址、36 类损坏字段、全部截断位置、读失败、摘要和预算；Python hashlib 交叉核对 11 组 SHA 输入，打包端拒绝 15 种非法配置。
生成的 320 字节黄金包由 C++ 校验器独立接受。文件 SHA256 为
`a477456f5615660cf35892cceaafeb995d10fc25bb7f9faa50c22ef0cc61d8fe`；内容摘要为
`c34751e7cf21cfd60cfe7293ec1171fe18d6be691e2e3bb9d627e143ac26287b`。
黄金包使用零指令映像，只用于格式检查，不能执行。

指定工具链时还编译两个生产源文件为 RV32 对象，报告包含对象哈希与编译器静态栈用量。
GCC 12.5/Os 当前给出 validate 栈帧 928 字节、load 240、SHA block 304；嵌套调用及文件读取器栈还需累加，不能把单函数数字当作任务高水位。
报告在 `build/app-install/apx2/apx2-report.json`，这些结果不代表 QEMU 执行或实机验证。

## 执行生命周期的当前边界

`app_generation_0041.h` 是固件常驻的执行门，不属于包内 ABI。
生命周期执行器串行调用 `begin/close`；其他线程在访问 App 状态或取用 App 函数指针之前，必须用回调排队时捕获的 generation 创建 `Ap01AppLease0041`，仅在 lease 成功后调用。
lease 要保持到回调返回且所有 App 析构函数执行完毕。队列不能在执行时替换成“当前 generation”，否则旧回调会冒充新 App。

停止顺序为关闭新调用、取消资源与队列、等待所有 lease 退出、调用受控停止入口并完成资源释放、最后释放代码。
关闭门并不取消任务、不抢占卡死的代码，也不等于调用 stop；这些由待实现的生命周期协调器完成。
`drained` 只有关闭且引用数为零时为真；超时仍保留内存，不能强行归零。
门对象由固件拥有，其寿命覆盖所有旧队列条目，不能随 App 释放。代际到 UINT32_MAX 后拒绝继续 begin，交由受控重启处理，防止旧代际重新有效。

```sh
mkdir -p build/app-install/generation build/app-install/generation-tsan
python3 -B tooling/scripts/test-app-generation-0041.py --out build/app-install/generation \
  --tool-prefix build/s1/toolchains/xpack-riscv-none-elf-gcc-12.5.0-1/bin/riscv-none-elf-
python3 -B tooling/scripts/test-app-generation-0041.py --out build/app-install/generation-tsan \
  --thread-sanitizer
```

当前仅验证执行门本身，真实 App 任务、UI 和维护回调接入仍未完成。

维护集成：`Ap01MaintenanceBridge0041` 现在保存 gate/generation 快照，维护路由的 pairing、principal、online 与平台启动健康回调均先申请 lease。
文件 App 绑定必须携带固件常驻 gate 和发布时的 generation。旧 XIP 绑定继续使用 null/0；非零 generation 而 gate 为空会拒绝。绑定快照不能并发修改。
App 关闭时，App 配对/身份查询返回不可用；设备码维护不需要 App lease，仍可查询 `/health` 且 `business_online=false`。
生产 App 当前仍是 XIP；本改动为真实维护调用点加保护，但不代表动态绑定替换、App 数据/任务卸载已接通。

```sh
mkdir -p build/app-install/maintenance-gate
python3 -B tooling/scripts/test-app-maintenance-gate-0041.py \
  --out build/app-install/maintenance-gate --rom build/app-install/platform-gate.bin
```

该宿主检查编译真实维护路由，验证回调内 close 时 lease 仍保持、返回后排空、旧绑定拒绝、新绑定正常、停止后设备码 health 仍可用。
`--rom` 额外运行原有不链接 App 的维护回归，使用私有临时文件和内存 Flash。

## C ABI v2 生命周期入口

`app_abi_v2.h` 定义 APX2 五个入口，顺序为 start、event、prepare_stop、stop、health，对应头内 88–104 偏移。仅传 C 结构、显式宽度整数、借用字节缓冲和 opaque state，不跨边界传 C++ 实例。RV32 services 表为 32 字节，event 为 24 字节，entries 为 20 字节，编译期检查 ILP32 布局。

服务表包含 version/size/generation、能力位图、平台 context 及同步 invoke 入口。服务编号/操作及载荷需由真实网络/存储/UI 适配冻结；当前未实现这些业务服务，不能把该头文件当作完整实际 App SDK。

`app_lifecycle_0041` 使用固件常驻 generation 门包围事件与健康回调。start 入口受重入保护；失败时仍保留部分 state 交给 prepare_stop/stop 清理。事件失败或异常健康结构立即关闭新回调入口。prepare_stop 返回 1 表示仍在取消，0 表示不再产生资源/回调；之后还必须等 gate 引用为零，才调用 stop。stop 成功后 releasable 才允许调用者释放映像。任何停止失败或超时进入 Retained，永不强制 free，等待外层记录恢复意图并受控重启。

所有生命周期方法由同一执行器串行调用；服务不得重入调用这些方法。prepare_stop 必须实际取消任务、队列和 UI 回调，不能仅设置一个布尔 stop；尚未改接现有 App。App prepare_stop 与尚未退出的 native callback 的并发同步仍由适配负责。

```sh
mkdir -p build/app-install/lifecycle
python3 -B tooling/scripts/test-app-lifecycle-0041.py --out build/app-install/lifecycle \
  --tool-prefix build/s1/toolchains/xpack-riscv-none-elf-gcc-12.5.0-1/bin/riscv-none-elf-
```

ASan/UBSan 检查 ABI 拒绝、重入、部分 start 失败、lease 阻止释放、停止失败/超时及旧代际拒绝；C11 头编译和 RV32 生命周期编译通过。报告 `build/app-install/lifecycle/lifecycle-report.json`。入口函数为宿主测试函数，不是加载后实际 App 指令的验证。

## 真实 App 任务返回边界

`app_tasks_0041` 为固件驻留任务跳板。它在创建线程之前取得代际 lease 并登记任务；线程执行 App 入口完整返回之后，才在固件代码中释放 lease 与任务计数。不能由 App 函数末尾写一个 exited 标志代替，因为函数尾部和 return 仍会执行 App 指令。

任务数限制为 4，原生创建失败回收登记；关闭门后不允许新任务。已登记但尚未调度的任务仍持 lease，直到运行并返回；App 必须观察自己的停止请求。创建端口约定非零返回表示任务未创建，与现有 0041 thread 调用约定一致。

真实 `codex_status/ports/ap01/native_0041.cpp` 的业务/bootstrap 和 UDP discovery 两个线程已改走此跳板，维护 pairing/principal/online/health 绑定也携带同一代际。新增内部 request-stop 与 tasks-drained 钩子仅覆盖任务/维护回调；UI timer、绘制回调及维护服务对象仍有额外寿命，不能据此释放 Runtime 或映像。

```sh
mkdir -p build/app-install/tasks
python3 -B tooling/scripts/test-app-tasks-0041.py --out build/app-install/tasks \
  --tool-prefix build/s1/toolchains/xpack-riscv-none-elf-gcc-12.5.0-1/bin/riscv-none-elf-
```

宿主检查创建失败、延迟调度、入口返回后的引用释放、任务上限、关闭后拒绝、旧代际拒绝；ASan/UBSan、RV32 编译通过。完整实际 App ROM 构建/镜像检查也通过，但未执行实机线程。

### 窗口绑定释放约束（2026-11-03）

`ap01_window_unbind` 返回 0 时必须保留 window、上下文和代码。UI 线程内仍有原生根事件订阅，或 timer/event 的嵌套调用尚未返回，都不能解绑；仅将 `win` 置空不会撤销订阅。根 DELETE 回调返回后才清除订阅根记录，保留 timer 时可绑定新根。当前没有凭空指定原厂 remove-event 地址，也没有主动撤销存活根的事件订阅。

返回 1 仅表示窗口根事件/定时器约束满足；调用方仍需排空 App 任务、维护调用、子对象 draw 回调并处理所有资源所有权，才可释放 App。当前 XIP App 尚不具备完整卸载能力。可复现检查：`python3 -B tooling/scripts/test-screen-binding-0041.py --out build/app-install/screen-binding --tool-prefix build/s1/toolchains/xpack-riscv-none-elf-gcc-12.5.0-1/bin/riscv-none-elf-`（先创建输出目录）。测试替代 ROM 注册，不是原生 LVGL/QEMU/实机验收。

### 映像与生命周期所有权（2026-11-03）

`app_image_0041` 将 APX2 校验/重定位和五入口生命周期连接到固件驻留的内存所有者。顺序为服务能力交集检查、完整包校验与期望摘要匹配、后端预留内存、再次校验/加载、缓存发布、入口检查、start。后端的 reserve 必须同时保证映像/bss、heap、stack 预算；publish 必须完成对应执行区域的缓存同步，只解析入口而不执行 App。没有后端明确返回 Unsupported，不能将普通 malloc 或任意 PSRAM 假定为可执行内存。

start 进入 App 之前的失败释放预留；start 已进入后即使返回错误，也只能经 prepare_stop、代际引用排空和 stop 成功释放。回调未返回时保留内存；停止失败或超时永久保留，等待受控重启。执行器串行化 start/event/health/stop，拒绝回调重入；旧代际不能进入新映像。所有者、后端与 gate 必须常驻，析构不是强制卸载操作。

复现：先建 `build/app-install/image`，运行 `python3 -B tooling/scripts/test-app-image-0041.py --out build/app-install/image --package build/app-install/apx2/golden.apx2 --tool-prefix build/s1/toolchains/xpack-riscv-none-elf-gcc-12.5.0-1/bin/riscv-none-elf-`。13 组宿主场景通过 ASan/UBSan，RV32 编译通过。测试后端执行宿主函数，不执行包内指令；真实执行区域与缓存后端、启动选择器调用和平台安装 handler 仍未接入。

### 事务执行器（2026-11-03）

`app_runner_0041` 串行连接启动选择器、实际文件 reader、映像所有者和健康观察。launch 先持久消耗 trial/rollback 机会，再打开选定路径并按摘要加载；运行或停止中重复 launch 不会再次裁决。start/event/health 失败先停止排空，再由下一次 tick 裁决回退；回退再次失败进入恢复，不重复自动尝试。非试运行的已提交 App 故障只进入恢复，不擅自选择旧文件。停止超时/失败保持 RebootRequired，不启动另一个 App，也不释放旧代码。

业务写许可还要求执行器处于 Running。健康 events 来自成功分发次数，stock/maintenance 由调用方提供平台观测计数；App 只报告入口状态/资源故障。成功日志 Unknown 会停止业务并保留不确定状态，不能当成成功或失败重试。HTTP commit/cancel 必须与执行器和文件访问共享互斥：调用 stop 等到 Idle 后提交持久决定，然后显式 launch。HTTP handler 尚未接到此执行器，当前也没有生产调用者提供真实计数与执行后端。

验证：`python3 -B tooling/scripts/test-app-runner-0041.py --out build/app-install/runner --package build/app-install/apx2/golden.apx2 --tool-prefix build/s1/toolchains/xpack-riscv-none-elf-gcc-12.5.0-1/bin/riscv-none-elf-`（先创建输出目录）。8 组宿主文件/日志/五入口流程通过 ASan/UBSan 和 RV32 编译，覆盖旧 App 先排空再切换、试运行成功、部分启动后回退、回退失败、回调等待与超时、停止失败、成功日志 ACK 丢失。入口为宿主测试函数，未执行包内指令。

### 核心 C 服务（2026-11-03）

`app_core_abi_v2.h` 定义 service 1 / required-services bit 0：操作 1 返回 8 字节 uint64 单调毫秒；操作 2 按 output capacity 返回 1..256 字节随机数；操作 3 返回 12 位十六进制 MAC 加 NUL，共 13 字节。输入必须为空，输出长度必须精确。返回 0 成功、-1 非法参数、-2 代际/能力不可用、-3 底层失败；written 只在成功时设置。随机源失败清零已触及的输出，不能把部分随机数当成功。

`app_core_0041` 每次 invoke 获取传入 generation 的 lease，结束后才释放，关闭/过期代际拒绝。`app_core_native_0041` 使用现有原厂适配，不向 App 公开 ROM 地址。C11 调用助手校验服务表版本/大小/能力/返回长度。真实 codex_status App 的随机回调和启动 MAC 查询已改走这个 C 服务表，保留其现有 XIP 生命周期；当前 core/gate 仍由 XIP Runtime 持有，不是完整文件 App 所需的独立常驻服务所有权。网络、存储、内存、显示和任务服务尚未完成迁移。

宿主 ASan/UBSan 检查覆盖精确长度、能力拒绝、随机失败清零、调用期间关闭与旧代际拒绝；C11 头和 RV32 编译通过，报告 `build/app-install/core/core-report.json`。正式五入口样本也改用该 C 服务，实现编入 RV32 guest 后在 james.local Docker 两基址通过，报告 `build/app-install/qemu-james/abi-core-run01.json`；测试随机源返回确定值，不代表实际硬件随机源验收。

### 真实业务 App 的只读恢复（2026-11-03）

实际 `Ap01Business::begin(now,true)` 供试运行/回退入口使用，`BundleStore::bsBegin(true)` 只读取已经挂载的文件系统：不调用可能创建私有根的 prepare、不创建 /bundle、不迁移 legacy 包。已有 Bundle 仍可加载编译缓存并渲染；没有 Bundle 时允许未配置启动。此模式不生成或持久写入新业务 context。

只读状态通过原子标志供业务及配对路径读取：Bundle/data/activate command、本地激活拒绝，配对维护门关闭新配对，bindings 保存回调也拒绝写入。只有平台已持久确认成功/回退完成，串行执行器才应显式调用 `begin(now,false)`，重新恢复并生成新的持久 context。现有 XIP 启动默认参数 false，行为保持原样。

这补齐 App 侧试运行入口能力，不是底层文件服务的代际写隔离：真实文件 App 五入口仍未接入，平台必须保证模式切换与业务 executor 串行，并在未来文件 C 服务处落实写许可/排空。App 不得用此布尔标志替代平台写门。

`test-app-readonly-0041.py --out build/app-install/readonly` 编译真实业务/配对/Bundle/渲染源码。ASan/UBSan 下统计所有变更性 VFS 操作：无 Bundle 首装和已有 Bundle 的只读恢复均为零，已有模板显示成功，原 state.bin/content.bin 逐字节不变；有效配对请求返回 maintenance_busy，Bundle/本地激活拒绝；显式可写恢复才更新 context。报告 `build/app-install/readonly/readonly-report.json`，无设备访问。

### 文件 C 服务与写冻结（2026-11-03）

`app_file_abi_v2.h` 定义 service 2 / required-services bit 1，208 字节固定请求，包含 opaque handle、参数、偏移、origin、两条 96 字节 NUL 补齐路径。读/写单次最多 1024 字节；WRITE 数据紧随请求头。路径使用以 / 开始的业务相对路径，固件补上私有根；拒绝点段、双斜线、反斜线、尾斜线、缺失 NUL 或 NUL 后非零字节。接口不暴露 mount/format，也不暴露原生 fd。私有根由固件准备和拥有，App 没有创建符号链接的接口。

`app_files_0041` 最多记录 16 个句柄，每个带 generation，句柄单调分配且不回绕。服务调用持代际 lease，并由内部非阻塞锁序列化。写许可默认关闭，仅固件执行器能 `writes(generation,true)`；truncate/append open、write（含同步）、mkdir/remove/rename 都在实际 VFS 调用前检查。冻结 `writes(generation,false)` 与文件操作使用同一锁：返回 false 代表有操作尚未退出，调用方必须重试，不能提前宣称冻结完成。已打开写句柄也不能绕过后续冻结。

停止时先关闭代际并排空所有调用，再由固件调用 drain 关闭遗留文件。旧句柄不跨代际复用。close 失败视为描述符状态不确定，保留粘性失败并要求受控重启，不重试可能已经被系统复用的 fd。新 App 不得在旧文件资源未排空时开始执行。此 drain 仍待接到总资源协调器，不能仅凭 image gate 已排空就释放拥有此服务的状态。

`test-app-files-0041.py --out build/app-install/files --tool-prefix build/s1/toolchains/xpack-riscv-none-elf-gcc-12.5.0-1/bin/riscv-none-elf-` 通过宿主 ASan/UBSan、C11 头与 RV32 编译，覆盖冻结变更/允许读取、冻结与进行中写互斥、路径/请求长度、正常改名/删除/空间查询、16 句柄预算、代际和 stale handle 拒绝、引用排空及 close 不确定。报告 `build/app-install/files/files-report.json`。真实 App VFS 客户端、服务表路由及安装执行器的写许可/drain 调用尚未接入，当前平台构建包含源但没有生产调用者。


### 真实 VFS 客户端与释放前资源确认（2026-11-03）

`app_vfs_client_v2.h` 在 App 内部适配 LittleFS 的 C++ 回调，仅通过 C invoke 表进入固件文件服务；校验表布局/代际/能力，去掉固定私有根前缀，大块读写按 1024 字节拆分。prepare 仅查询容量，不创建目录。零长度 write 保留同步语义，中途短写/失败返回失败（可能已写入前缀，不承诺原子写入）。同步成本由底层 VFS 决定，分块不代表减少持久同步次数。

codex_status 的真实 XIP Runtime 已使用此适配器，根目录准备和启动写许可仍由 XIP 启动路径显式完成。真实业务测试增加 3073 字节读写、第二块失败仅写入 1024 字节且调用者收到失败、冻结后旧写句柄及 sync 拒绝。测试报告包含适配器和 ABI 头摘要。

`Ap01AppImagePort0041::drainResources` 是常驻后端的同步资源确认：App stop 完成且 gate 排空后、释放映像之前调用。失败会粘性返回 RebootRequired，保留内存，不重试不确定的资源关闭，也不允许新代际启动。没有映像外资源的后端可省略；生产后端有文件/UI 等资源时必须绑定。15 组宿主映像测试覆盖正常顺序、部分 start 失败后的资源回收失败、重入拒绝及失败后禁止重试；RV32 编译通过。该钩子尚未绑定生产文件/UI 服务，不能视为完整资源卸载已经实现。


### 持久状态驱动的文件写许可（2026-11-03）

映像后端增加常驻 `writePermission(context,generation,allow)`，文件后端应绑定 `Ap01AppFiles0041::writes`，并把 `drainResources` 绑定到全部资源的回收。每一代服务必须默认拒写，App start 包括已确认版本的重启均先只读恢复；runner 在 start 返回后、健康确认持久成功后、事件处理前检查选择器许可，只在后端确认后报告 business_writes。没有业务写服务的后端可不提供此回调。

安装服务在 HTTP 修改日志后立即 reconcile，不等下次 tick 才撤权。开放或撤权失败时关闭整个代际门并进入停止排空，已有调用由 lease 计数等待；不继续接收业务事件，不把权限失败当作成功，不因已持久成功的包权限开启失败就撤销历史成功。实际底层关闭失败仍按资源回收规则保留映像要求重启。

`test-app-runner-0041.py` 的后端已接真实文件服务和宿主文件系统，10 组情形验证每次 start/试运行/回退/停止拒写、持久成功才开放、授权失败和日志 ACK 不确定后撤权失败都会停止 App。HTTP/CLI 首装及运行中升级回归通过。尚未构造生产常驻服务、连接真实 App 的成功后可写恢复，也没有生产 UI/network 等总资源回收；这些仍是未完成项。


### 统一 C 服务路由（2026-11-03）

`app_services_0041.h` 将 core service 1 和 file service 2 汇集到一张 C 表，公布能力位 0/1；未知服务返回 Unavailable 并清零 written。路由器只保存常驻服务引用，每次转发保留调用方 generation，实际服务执行原有 lease/输入验证，不能把旧代际请求改签为当前代际。core/files 必须使用同一执行器 gate，路由器及服务对象必须比 App/服务快照活得更久。

真实 XIP App 的随机数、MAC 与 LittleFS 已改为同一服务快照。CLI/C++ 安装联调后端绑定该生产路由、真实 core/files、写许可与 drain；核心的时钟/随机/MAC 底层是确定性宿主替身，入口仍是宿主函数。每次请求后实际文件 open 结果与 installer 的 business_writes 一致；每代故意保留一个文件句柄交给 drain，释放前确认 drain 已完成；下一代启动验证旧服务快照拒绝核心和文件访问。四组首装/升级及 ACK 丢失流程通过 ASan/UBSan，没有运行包内指令或访问设备。

常驻生产组合仍待构造；XIP Runtime 目前仍拥有这些服务，这次统一调用边界不等同于资源所有权已经迁出 App。


### 网络 C 服务底层（2026-11-03）

`app_network_abi_v2.h` 定义 service 3 / capability bit 2：16 字节请求头、8 字节 IPv4 peer（四个网络顺序地址字节、host-order uint16 port、零 reserved），不跨边界传 native sockaddr 或 fd。监听仅允许业务 TCP 18081 和 UDP 8767，维护端口不对 App 开放。支持 listen/accept/close/poll/receive/send/receive_from/send_to；单次载荷最多 1024 字节，receive_from 输出先放 peer，SEND 类请求在头后携带 payload。poll 是立即快照，AGAIN 区分暂未就绪与 TCP 成功读取零字节 EOF；UDP 空数据报仍携带 peer。

`app_network_0041` 记录最多 8 个单调 opaque 句柄，带代际与 listener/TCP/UDP 类型。每次调用持 lease 和非阻塞互斥锁，旧代际及未排空的旧句柄拒绝进入。关闭代际且所有调用退出后才允许 drain；close 结果不确定是粘性故障，不重复关闭可能复用的 fd，不释放所属映像。原厂适配 `app_network_native_0041` 使用既有原厂接口地址，poll timeout=0、收发 MSG_DONTWAIT；accept 前先查可读，监听沿用既有 2 秒接收 timeout 配置。该 timeout 对 accept 的真实上限尚未实测，不以编译通过证明原厂调度或中断安全。

宿主 ASan/UBSan 使用可注入传输后端验证端口限制、TCP/UDP、AGAIN/EOF、句柄预算、代际拒绝、调用中关门后的排空及关闭失败；C11 头和服务/原厂适配 RV32 编译通过。报告 `build/app-install/network/network-report.json`。目前没有接统一路由和真实 App 网络客户端；App 仍走旧原生网络路径。尚未执行原厂网络指令、模型网络收发或实机网络验证。


### 网络 App 客户端（2026-11-03）

`app_network_client_v2.h` 为 App 内部适配器，复制 C 服务表，监听/accept/close/poll/TCP/UDP 均使用 opaque handle。TCP 每次读写至多 1024 字节，返回实际部分进度，由 HTTP stream 保持外层总期限；UDP 单包不可拆分，超限拒绝。重试仅针对 BUSY/AGAIN，不把 EOF 当成重试；所有重试沿用原 deadline，时钟倒退退出。每次 yield 消耗固定预算，即便时钟停滞也会退出，最多 60000 次。

core service 增加 YIELD=4，无输入/输出，固件调度等待 1 毫秒并持有代际 lease。缺失后端/时钟服务、关闭代际时退出重试，避免 App 私自调用原厂 sleep 地址。监听建立最多重试 5 秒，close 最多 1 秒；关闭 gate 后无法再主动 close 时，由固件 drain 负责遗留句柄。原厂 accept 的实际超时保证仍保留上一节的未验证边界。

统一路由可绑定 network，只有提供时才公告 capability bit 2。真实 XIP Runtime 已绑定网络服务，业务 18081 HTTP stream 和 8767 UDP discovery 均改走客户端；任务排空钩子增加 network drain，依然不能据此推断 UI 和维护服务已可卸载。业务线程的其他时钟/UI/任务/内存调用仍待完整 C 边界迁移。

网络宿主测试覆盖统一路由、真实 service/client、AGAIN/EOF、原始期限、时钟停滞/倒退、关闭 gate、TCP 分块、UDP 不拆包及资源 drain；core YIELD 参数/失败/关闭代际测试与 HTTP/CLI 安装回归通过。底层传输是注入替身，本轮未执行原厂网络或 QEMU，完整真实 HTTP parser 经网络客户端的故障联调仍待补充。


### 真实业务 HTTP 经网络服务联调（2026-11-03）

`test-app-readonly-0041.py` 现编译真实 App 的 http.cpp/application.cpp/business.cpp、固件 HTTP parser，以及 core/network service、统一路由和网络客户端。新增 8 组 wire 级场景：7 字节分段读取/5 字节分段发送、读写交替 AGAIN、3000 字节请求体完整消费、提前 EOF、读超时、写超时、输出 10 字节后的发送错误、读取期间关闭代际、以及大块底层读取受客户端 1 KiB 限制。正常场景返回完整的 app_trial_readonly 503，响应 Content-Length 与实际体长度一致；异常场景 serve 返回 false，不把部分响应宣称成功。读写超时均在原期限结束，关闭后由 drain 回收 listener 和 connection。

整个流程使用真实只读 Bundle 与 App，变更性 VFS 操作仍为零、已持久业务文件逐字节不变。底层网络函数为确定性替身，无宿主 socket 或设备访问，不能代替原厂接口和完整模型运行。报告为 `build/app-install/readonly/readonly-report.json`，包含 parser/客户端/路由 ABI 头与实际业务源摘要。

下一处实际边界是 `native_runtime_0041.cpp`：当前 malloc/free 直达 ROM，realloc/calloc/new/delete 依赖它，并没有 App generation 或 APX2 heap_bytes 预算。后续文件 App 需要独立的 App 分配入口与固件管理的预算，不能直接替换常驻平台全局 malloc，否则维护 HTTP/日志等固件分配也会错误地绑定到可卸载 App。原文件内 time/__errno 也含 ROM 地址，完整文件 App 打包时必须分别改接或提供 App 私有实现；不能仅把业务源改成 PIE 就宣称消除了原厂依赖。


### 文件 App 受限堆服务（2026-11-03）

`app_heap_abi_v2.h` 定义 service 4 / capability bit 3。16 字节请求包含 uint64 address、uint32 bytes、零 reserved；分配/清零分配/重分配输出 uint64 地址，释放无输出。RV32 地址上半部必须为零；同一固定 C 格式允许宿主验证使用宿主地址。所有非零输入地址必须精确匹配本代际已分配块起点，不能以内点、外部地址或已释放地址操作。零尺寸分配返回零，realloc(p,0) 释放，增长失败保留原块及内容。

`app_heap_0041` 使用固件预先独占预留的 16 字节对齐 arena，bind 在 gate.begin 前检查下一代际，容量必须就是 APX2 heap_bytes。分配块头为 16 字节，全部元数据/对齐开销从同一预算扣除，无平台 malloc 回退。线性 first-fit、空闲块合并、相邻空闲空间上的原地增长，不能由一次预算不足推导系统整体 OOM。完整元数据链每次操作前检查；损坏进入粘性故障，drain 拒绝并要求受控重启。这不提供内存隔离，App 仍可能越界破坏进程。

服务调用持 lease 和非阻塞锁；关闭 gate 且所有引用排空后 drain 清零整个 arena、清除绑定，随后后端才能释放该内存。App stop 时服务门已关闭，未释放分配由 drain 统一收回。`app_heap_client_v2.h` 是 App 私有适配，提供 allocate/zeroAllocate/reallocate/free，检查乘法溢出，Busy 通过 core YIELD 最多重试 1000 次；绝不跨分配器 free。统一路由仅在配置 heap 服务时报告能力。

宿主 ASan/UBSan 验证精确预算（包含块头）、零堆、碎片/合并、5000 次确定性随机 realloc 数据保持、溢出/内点/重复释放拒绝、Busy 重试上限、代际与 lease 排空、清零和损坏保留；C11 与 RV32 编译通过。HTTP/CLI 联调后端在 reserve 按包的 heap_bytes 绑定，宿主入口用真实 heap 客户端分配并检查超限拒绝，event/stop 验证存活数据，drain 后才释放映像；四组首装/升级回归通过。

目前仍未替换真实业务 App 的 malloc/new，没有生产执行后端的 arena 预留/绑定，也没有真实 App 堆峰值测量。平台分配器保持原样；完整文件 App 的私有 runtime 改接和生产资源组合仍未完成。报告 `build/app-install/heap/heap-report.json`、`build/app-install/client-http/client-http-report.json`，无实机访问。


### 文件 App 私有分配运行库与 RV32 执行（2026-11-03）

`app_runtime_heap_v2.cpp` 只供文件 App 链接，不在 PLATFORM_SOURCES 中。start 在构造业务 C++ 对象前调用 bind，一份映像只绑定一次，表复制到 App 自身 BSS。malloc/calloc/realloc/free 和当前 App 使用的 nothrow new/new[]、普通/带 size delete/delete[] 均经 heap C 服务，无原厂地址或平台分配回退；失败 free 记录资源故障供运行健康检查，停止关门后的遗留分配仍由固件 drain 回收。没有实现 App 当前未使用的 throwing/aligned new 形式。

`test-app-runtime-heap-v2.py` 宿主只调用同一实现的 prefixed 入口，不覆盖 ASan/宿主平台 malloc；RV32 对象编译包含真实 C/C++ 分配符号，审计无 init_array/ctors，仅剩 memcpy 引用。当前真实 App 24 个源重新 PIE 编译，通过 `probe-app-pic-0041.py --runtime-heap-object build/app-install/runtime-heap/app-runtime-heap.rv32.o` 连接私有运行库，malloc/free/new/delete 等引用全部解析；仍有 98 个其他导入和 35 个 GOT 重定位，不是最终链接包。报告 `build/app-install/app-runtime-pic-v2/pic-report.json`。

正式五入口小样本加入私有运行库：实际 new/delete、calloc/realloc、超预算拒绝、event/stop 访问存活数据、故意遗留分配由资源 drain 清零。guest 使用生产 heap/router/image/lifecycle/APX2；james.local Docker 在 0x62fca000 和 0xa8000000 均通过两代加载与排空，保存寄存器/SP 保持。样本用局部 `std::nothrow_t{}` 避免引用默认可见全局 nothrow 产生 GOT；完整 App 的 GOT 仍须处理，不能把这个样本做法当成已完成全量打包。

证据：`build/app-install/abi-qemu-heap-v2/build-report.json` 与 `build/app-install/qemu-james/abi-heap-run01.json` 指纹一致。guest 11936 字节，SHA256 c5c78102c164d7316e26c364e27239e49ab98520549180c41c99c0c63b695b98；包 SHA256 7264196d304bfb1341dce0a2f5d2375c69a21701e5806e619c9cb05b291838c2。映像 1508 字节、含 BSS 1576 字节、堆 512 字节，仅小样本预算，不是完整 App 的内存需求。

实际业务文件 App 入口还没有绑定该运行库，平台 XIP 构建的全局分配器保持原状。剩余导入集中在原生 Runtime/服务所有权、显示/任务、libc/时钟与数学支持；没有完整业务 App 的最终 APX2、模型整体运行或实际内存/cache 准入证明。


### 纯运行库与日期依赖分离（2026-11-03）

将既有 memcpy/memmove/memset/memcmp/memchr、字符串函数、冻结 32 位 strtol 和三种既有 strftime 格式移到 `runtime_libc_0041.cpp`。平台和文件 App 分别链接同一源，平台 malloc/free/time/errno 与 C++ 分配器仍在 native_runtime_0041 中；没有通过全局替换把维护平台分配绑定到 App。strtol 的负数返回显式经过 int64，保持 RV32 原行为并允许宿主验证同一 32 位饱和合同。该文件不是完整标准 libc；strftime 仍只支持此前的 %H:%M、%m/%d、%m-%d %H:%M，snprintf 仍是未解决导入。

`native_calendar_0041.cpp` 改成纯 Gregorian UTC+8 换算，消除原厂 timesub 地址和私有 tm 布局依赖。按最多 137 个年份和 12 个月迭代，无动态分配/时区全局状态。宿主对照 gmtime_r，覆盖 uint32 秒数域每一天的首尾，共 99,422 个样本，以及所有既有日期格式。宿主测试域覆盖到 2106；RV32 调用 ABI 仍是有符号 32 位 time_t/long，实际可传入正值范围未扩展到 2106，不应据此宣称解决了 2038 问题。

`test-runtime-libc-0041.py` 使用重命名入口，避免覆盖宿主 libc，ASan/UBSan、RV32 PIE 编译通过；报告 `build/app-install/libc/libc-report.json`。真实 Bundle/HTTP/网络回归与完整 App 构建通过。通过 probe-app-pic 的 --support-object 将纯 libc、calendar、SHA 与私有 heap 链入当前 24 个业务源，剩余导入从 98 降到 86，报告 `build/app-install/app-pure-pic/pic-report.json`。这些仍是 ET_REL 对象，GOT、snprintf/time/math、原生 Runtime/显示/任务等尚未完成最终处理，不是已可安装的 APX2。


### UTC 时间与现有数学库（2026-11-03）

core service 新增 UTC_SECONDS=5，无输入、uint64 秒数输出，独立于 MONOTONIC_MS。驻留适配复用平台 time()，保留既有 RTC 本地秒数转 UTC 逻辑；读取失败返回 IO 并清零输出。文件 App 的 `app_runtime_time_v2.cpp` 使用与私有堆相同的不可变服务绑定，导出私有 time()，未绑定/关闭代际/读取失败/秒数超过 INT32_MAX 返回 -1 并写入 out（若非空）。0 是可表达的 epoch，不冒称时钟已校准；业务仍负责判断 RTC 是否已设置。没有扩大 signed-32 time_t ABI 或解决 2038 上限。

宿主验证 UTC 值、零、INT32_MAX、越界、读取失败/清零、请求长度和关门行为；RV32 PIE 审计真实 time 符号通过。APX2 小样本实际调用私有 time()，james.local 既有 Docker 两基址、两代加载通过；报告 `build/app-install/qemu-james/abi-time-run01.json` 已和本地 `abi-qemu-time` 指纹核对。guest SHA 6c1e06cf13a57bc9101ad68f4f5b02620f658be536df9a7a908a4608c29cb622，包 SHA 3361e9f052818d1efdde61938eb80a28d36dba2c64159131402339d51bccccd8。核心 UTC 底层在模型中是确定性替身，不是设备 RTC 验证。

现有 xPack 12.5.0 的 rv32imafc_zicsr/ilp32f libm.a/libgcc.a 作为私有 support objects 参与真实 24 源的 ET_REL 链接，数学与编译器辅助引用已解析；剩余 54 项导入，报告 `build/app-install/app-time-math-pic/pic-report.json` 包含库路径/摘要与最终组合重定位计数。组合中没有 R_RISCV_HI20 绝对高位地址重定位，但仍有 35 个 GOT、209 个 RELAX 及压缩分支等类型，尚未证明最终双基址规范化和包内数学执行。不得把对象链接成功等同于完整可加载 APX2。snprintf 与原生 Runtime/显示/任务/平台服务依赖仍未解决。
