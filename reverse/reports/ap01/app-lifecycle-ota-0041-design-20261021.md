# 0041 多应用 OTA 载入与卸载工程设计

日期：2026-10-21
状态：**设计待实施；执行 RAM 的地址、容量、可执行性与缓存维护前提未验证。**
范围：仅 `1.0.2_0041` 修改版。本文不修改实现，不代表可刷候选、实机验证或部署批准。

## 1. 目标与边界

新的 OTA 功能是多应用部署和生命周期管理：支持载入或卸载一个或多个应用，支持多个独立应用同时存在，不局限于升级当前 `codex_status`。

**OTA、维护、认证、发现和应用管理器是常驻控制面，不属于可卸载或可热更新的应用集合。** 首版不提供更新这些常驻组件的应用操作。必要的宿主首次改造仍是单独的固件工程，不由本文的应用包安装完成。

用户所说的“卸载”默认是停止内存实例、释放代码及运行资源，保留已经接收的包文件。删除包文件是不同操作，不默认执行。

| 操作 | 运行实例 | 包文件 | 成功后的重启目标 |
| --- | --- | --- | --- |
| 上传并校验包 | 不改变 | 保存已验证包 | 不自动载入 |
| `load` | 创建并启动应用实例 | 使用指定已验证包 | 自动恢复该应用 |
| `unload` | 停止实例、解绑资源、释放代码和状态 | 保留 | 保持未载入 |
| `replace`（后续能力） | 停旧实例，试运行指定新包 | 保留稳定旧包 | 恢复已提交版本 |
| `remove`（首版不提供） | 不隐式改变实例 | 删除指定包 | 与 unload 分开定义 |

首版必须完成包接收、单应用及批量 load/unload、多应用共存、幂等查询和重启恢复。replace 是建立在相同机制上的后续能力，不应阻塞基本载入/卸载交付。暂不建设依赖下载、版本自动求解、包仓库、自动更新或跨应用原子事务。

原生应用共享固件地址空间。资源配额和接口约束不构成恶意代码隔离；死循环、非法访问或堆破坏可能影响整个系统。不能承诺这类失败都能在线回退。

## 2. 已有源码证据与能力缺口

本节记录已读取源码支持的事实；后续章节均为建议设计。

| 位置 | 已有能力或限制 | 对新设计的影响 |
| --- | --- | --- |
| [screen_host_0041.h/.c](../../../tooling/firmware-modules/screen_host_0041.c) | 固定 apps 数组，每应用 slots/capacity/revision，稳定 screen ID、异步进入、逻辑顺序与物理 child 分离 | 可复用多应用屏幕管理；尚无代码加载器 |
| `ap01_host_retire()` | 设置 live=0 并调用 unbind，但保留 ID、descriptor、context 和 app poll | 不是卸载屏障，释放代码后会留下旧引用 |
| `ap01_host_poll()` | 遍历调用每个非空 app poll | 退役后仍可能执行旧代码 |
| `ap01_host_short()` | 可能对当前退役槽调用 input | 所有入口必须统一检查实例状态 |
| [screen_port_0041.h/.cpp](../../../tooling/firmware-modules/screen_port_0041.cpp) | 窗口、root、图像、事件和定时器绑定 | 应作为常驻平台层 |
| `ap01_window_find()/detach()` | 窗口 DELETE 时保留定时器/context，后续重建复用 Runtime | 证明窗口重建，不证明代码热替换 |
| `ap01_window_unbind()` | 删除定时器、清空窗口指针；没有从仍存活窗口移除 event 注册 | 不能当作完整应用回调解绑 |
| `on_draw` 对应的 `draw()` | 直接把传入回调注册给原厂对象 | 长期注册需要常驻转发与应用代次检查 |
| [native_application_0041.ld](../../../tooling/firmware-modules/native_application_0041.ld) | 整体扩展 XIP 起点 0xa0674000，上限 0xa06fe000；禁止可写静态、GOT、TLS及隐式构造器 | 现有产物不是可独立加载的应用 |
| [native_io_0041.h](../../../tooling/firmware-modules/native_io_0041.h) | 有 thread 创建包装，无已证明的 join/退出回收接口 | 首版不采用强制终止应用线程 |
| [模块说明](../../../tooling/firmware-modules/README.md) | 0031 APX1 是同步诊断 ABI，禁止线程和异步回调 | 不能直接作为0041多应用 ABI |

相邻仓库 `codex_status/ports/ap01/native_0041.cpp` 的已核实事实：

- `Runtime` 同时持有 `Flash`、`LittleFSClass`、`Ap01Business`、`unique_ptr<Ap01Application>`、宿主、窗口和队列。
- `Runtime::bootstrap()` 创建维护线程（16 KiB）、发现线程（8 KiB），随后自身进入业务服务；业务线程栈为32 KiB。线程 ID 仅存于局部变量。
- `Runtime::serve(true)` 直接调用 `app->maintenanceTick()/maintenanceResponse()`；`Runtime::udp()` 直接调用 `app->discovery()`。不能把整个 `app` 或 `Runtime` 当作可卸载对象。
- `Frame` 已有 UI epoch、generation 和 transition，但没有独立应用实例身份。`Activation` 也需要应用代次。
- `bootHealthy()` 仅检查 ready、维护监听和 UI 心跳，不能证明某个候选应用健康。

现有窗口生命周期验证见[0041 第二应用共存与窗口热重建](screen-host-lifecycle-20261020.md)。它证明第二应用共存和窗口重建的特定离线路径；没有证明新机器码加载、应用停机屏障、持久应用恢复或真实 RAM 执行条件。

相邻仓库路径仅用代码路径说明，未建立依赖本机目录结构的跨仓库相对链接。

## 3. 执行内存：多个固定槽，而非单一固定地址

单个固定执行地址只能替换一个模块，不能承载多个独立应用同时运行。

| 路线 | 并存方式 | 成本与阻碍 |
| --- | --- | --- |
| 多个固定 RAM 执行槽，按槽分别链接 | 每槽一个应用实例 | 需要各槽 variant；运行时无需通用重定位 |
| 任意地址加载加受限重定位 | 动态分配每个模块 | 必须验证 RV32 重定位集合、导入和指针修正，首版复杂度较高 |
| 多个独立 XIP 应用槽 | 每槽固定地址执行 | 必须证明 Flash 空间、映射、写擦期间执行安全和掉电恢复 |
| 覆写现有整体 XIP 扩展区 | 不适用 | 宿主、维护和回调可能正在该区域执行，不能采用 |

**选择有界多个固定 RAM 执行槽、按槽链接 variant，作为首版待验证路线。** 选择依据是现有固定地址构建方式易于延续，且可避免实现通用 ELF 加载器。不是依据已确认的 RAM 资源。

### 3.1 必须先确认的硬件条件

1. 专用 RAM 的合法执行地址、可执行属性及对齐要求。
2. 与原厂任务栈、堆、显示缓冲、DMA和其他保留区不重叠。
3. 写入机器码后所需的数据/指令缓存维护及执行屏障。
4. 可以长期预留至少两个独立执行槽，并保留原厂运行余量。
5. `/resource` 存储空间和持久写入、同步、rename/恢复的实际语义。

本设计不填写未经验证的 RAM 地址、槽数、大小和原厂缓存函数地址。如果前提失败，暂停 RAM 加载实现并评估独立 XIP 槽；不以 UI 重建替代验收。

### 3.2 槽配置与包选择

宿主构建产生只读配置，示意结构如下，不直接作为磁盘格式：

```c
struct ExecSlotConfig {
    uintptr_t code_base;
    uint32_t code_capacity;
    uint32_t state_limit;
    uint32_t heap_limit;
    uint16_t screen_capacity;
};
```

- 实际槽数 N 和每项值由内存验证确定。多应用验收要求 N 至少为2。
- 每个应用实例独占一个代码槽和对应固定 root 分区。
- 每个包包含适配当前 `layout_id` 的按槽 variant。首版构建要求覆盖该布局全部槽，避免空槽与包地址不匹配。
- loader 选择槽后核对 `slot_id/load_address/code_length`，不移动已经运行的应用，不做内存压缩。
- 没有合适空槽返回 `no_execution_slot`；包超出槽预算返回 `image_too_large`。
- 所有可写状态显式分配，应用通过 state 指针访问；禁止隐式 `.data/.bss/.sdata/.sbss`、TLS、GOT、构造器以及未处理重定位。
- 代码、状态、堆都要有每应用上限，同时还受宿主全局预算约束。宿主维护及恢复路径需要独立保留余量。

现有 XIP 区间长度为 `0x8a000 = 565248 B`，包含当前整个扩展程序，不等于可用空闲空间，更不等于可执行 RAM 容量。

### 3.3 持久包预算

建议在已接入的 `/resource` 下使用0041专属目录，具体路径属于实现配置。至少预算已载入应用稳定包、待接收包、临时接收文件及事务记录。支持 replace 时还需保留该目标的旧稳定包。

上传前预留容量；不足时保持当前实例不变。首版不自动删除用户保留的未载入包。文件名不直接拼接未验证的 app_id；使用规范化ID及内容哈希映射。

## 4. 常驻宿主与应用边界

常驻部分：

- OTA 接收、校验、事务查询、认证和维护；
- 发现、配对、包文件索引、恢复日志；
- 注册表、执行槽分配、调用许可和资源账本；
- `screen_host_0041`、`screen_port_0041`、原厂挂钩、窗口定时器；
- 业务调度、UI转发、加载器、健康检查与恢复。

可卸载部分：

- 业务逻辑、渲染逻辑和该应用的显式实例状态；
- 通过宿主服务登记并归属到该实例的运行资源。

需要拆开现有 `Ap01Application`：认证、维护、发现留在宿主，业务通过注册表分发。`codex_status` 成为其中一个普通应用，而不是唯一可替换业务成员。

OTA 不分配应用执行槽，不出现在可操作注册表中。宿主保留控制面名称空间；包含受保护 ID 的批量请求在任何变更前整体拒绝。包不能通过声明 app_id 覆盖控制面入口。

## 5. 注册表、状态机和依赖策略

### 5.1 注册项

运行实例表采用固定容量，最多 N 个同时载入实例。逻辑应用记录与执行槽解耦：未载入应用保留持久身份/generation/desired-state，但不长期占用运行槽，否则 unload 无法为新应用释放容量。

逻辑记录同样有明确上限，不能无限增长；达到上限返回容量错误。首版可使用独立有界逻辑记录表。运行槽只保存对逻辑记录的稳定句柄，不能用可移动数组元素地址充当长期应用身份。

| 字段 | 含义 |
| --- | --- |
| app_id | 逻辑应用身份，同一时刻最多一个实例 |
| generation | 对外CAS管理版本；不是代码实例身份 |
| instance_epoch | 本次运行实例代次，重建时变化 |
| desired_state | 已提交的重启目标：loaded/unloaded |
| actual_state | 当前实际状态 |
| package_hash/build_id | 稳定版本与当前运行版本，trial时分开记录 |
| exec_slot_id | 运行时槽号，未载入时为空 |
| entry_table/state_pointer | 当前有效应用入口与状态 |
| code/state/heap usage | 配额及实际占用 |
| host_app_pointer/screen_capacity | 固定root分区映射 |
| inflight_calls | 正在执行的应用调用数 |
| stop_requested/worker_parked/ui_cleanup_done | 卸载屏障 |
| resource_ledger | 本实例资源 |
| last_error | 可查询的失败信息 |

`generation`是接口字段名，语义为管理revision：通过校验、资源预检并准备首次改变实例状态时，先持久记录该项操作意图及新的generation，再进入LOADING或STOPPING。该版本即被消费；之后即使停机失败、恢复旧实例或操作被中断，也不回退版本。纯校验/预检失败和unchanged不推进。终态返回该项已经消费的版本，不在成功提交时重复推进。这样旧CAS请求不能在失败停机后被错误地再次接受。

`instance_epoch`独立标识运行实例，在每次create前分配新值，包括恢复同一个旧包；一次未能退出的旧实例保留自己的epoch，但普通调用门保持关闭。回调令牌使用 `boot_id + 稳定应用句柄 + instance_epoch`，另带资源句柄代次。不能用管理generation或复用后的槽号判断机器码实例归属。重启后boot_id改变，使旧令牌失效。

### 5.2 状态机

```text
UNLOADED → LOADING → STARTING → RUNNING
RUNNING → STOPPING → DETACHING → UNLOADED
LOADING / STARTING → CLEANUP → UNLOADED 或 FAILED
STOPPING 超时 → FAILED_STOP（代码及状态继续保留）
```

`FAILED_STOP` 不能复用代码槽。`desired=loaded`而`actual=failed`是允许且应报告的状态；失败不会悄悄取消用户的持久目标。

### 5.3 依赖

首版应用只能依赖宿主 ABI 能力。禁止应用之间直接持有函数地址、状态指针或借用彼此资源。包若声明另一个可卸载应用为依赖，拒绝为 `unsupported_dependency`，不实现隐式级联卸载或依赖求解。

## 6. 固定 apps 数组、root池和窗口重建

宿主窗口建立时为 N 个运行槽一次性建立 root 池，各执行槽对应固定分区；所有物理 child 索引在窗口生命周期内稳定。

- `host.apps` 固定长度且地址稳定。
- 未使用槽保持 `count=0, poll=null, context=null`，没有可见screen。
- 应用通过宿主发布screen集合，数量不得超过该槽 `screen_capacity`。
- unload 删除应用子对象、图像和回调，清空 descriptor/ID，但保留空root。不能删除中间root导致其他应用索引变化。
- 窗口整体 DELETE 才销毁整池；重建后根据仍运行的注册项重新连接UI，不重新载入应用代码。

现有 `ap01_host_init()` 要求 app_id 非空且唯一。固定空槽需要使用宿主内部唯一槽标识，或修改初始化校验以显式支持空槽；不要用多个空字符串绕过约束。逻辑 app_id 与内部槽标识由注册表映射，避免把物理槽身份当成应用身份。

新增卸载清理操作必须完成：禁止所有普通入口、取消涉及该应用的切换、受控unbind、清空ID/descriptor/count/poll/context、推进revision、解除host source/target引用。不得调用全局 `ap01_host_destroy()` 来卸载单个应用。

## 7. 调度、调用许可与阻塞边界

首版保留常驻维护、发现和业务执行器，禁止应用自建线程。业务执行器维护每应用有界请求队列，轮询调度；一个应用不能占满全局队列。

每次进入应用代码：

1. 核对 app 状态、boot_id/instance_epoch和操作许可。
2. 获得调用许可并增加 inflight。
3. 调用入口。
4. 返回常驻代码后减少 inflight，并在需要时确认停驻。

卸载关闭目标应用的新请求和入口许可，不影响其他应用排队请求。生命周期状态切换与调用许可获取必须通过同一同步协议，不能“先检查状态、后无保护调用”。

**单业务执行器的限制：一个慢应用调用会延迟其他应用。** 当前HTTP的5秒期限不能证明任意计算和文件操作都有界。首版ABI要求入口有界返回，等待/网络经宿主有界服务执行，长任务拆成多次step。

应用卡死时维护线程可报告停机超时，但不能释放仍在执行的代码。业务执行器及其他应用可能暂时无法继续工作，需要受控重启恢复。若未来需要每应用worker，必须先验证线程join/回收接口、栈预算和退出屏障。

UI线程只执行短小UI操作及常驻转发，不运行业务HTTP、包读取或完整包校验。

## 8. 资源账本和完整卸载握手

账本至少登记：堆分配、UI子对象/surface/draw注册、定时器、事件订阅、排队工作、Frame/Activation、连接和文件句柄。每项绑定稳定应用句柄与instance_epoch。

原厂长生命周期注册保存常驻trampoline和常驻记录，不能直接保存可卸载函数地址。trampoline验证instance_epoch并取得调用许可后才进入应用。资源账本在原厂已完全停止引用记录之前不能释放。资源账本中的运行归属代次均指instance_epoch；对外expected_generation只用于管理CAS。

拟定内部接口如下，具体类型布局需在实现阶段冻结：

```c
int ap01_app_call_enter(AppHandle, uint64_t instance_epoch, CallKind);
void ap01_app_call_leave(AppHandle, uint64_t instance_epoch);
int ap01_app_request_unload(AppHandle, uint64_t expected_generation);
int ap01_app_ui_detach(AppHandle, uint64_t instance_epoch); /* UI线程 */
int ap01_app_finish_unload(AppHandle); /* 常驻执行器，所有屏障完成后 */
```

普通调用门仅在RUNNING开放。STOPPING/DETACHING关闭普通poll/input/draw/业务回调，但清理调用门允许生命周期管理器按顺序调用request_stop、unbind、destroy；每项只能有一个清理执行者。同步DELETE事件先由常驻代码维护资源账本，如确需调用应用清理函数，也必须使用该受控清理许可并计入inflight。destroy仅能在其他调用全部返回后开始；其自身返回常驻代码后才能最终释放代码与状态。

卸载顺序：

1. 核对 expected_generation，持久记录操作意图及消费后的管理generation，取得目标生命周期操作权。
2. 置STOPPING，停止新请求和UI业务入队，撤销新普通回调许可。
3. UI线程停止poll/input/prepare，取消或等待该应用参与的切换，并切到安全原厂页/宿主页。不能仅清host phase就假定原厂动画已结束。
4. 业务执行器完成或协作取消当前调用，返回常驻代码后确认 worker_parked。取消尚未执行的工作。
5. 清空目标的Frame/Activation及prepare引用，释放对应缓冲。迟到结果以boot_id/instance_epoch、UI epoch、transition一起核对；现有Frame.generation仍表示内容帧版本，不复用为应用管理版本。
6. UI线程执行受控unbind；删除应用子对象和图像，处理DELETE同步回调、缓存失效、timer/subscription解除。
7. 确认inflight为零、worker已停驻、UI清理完成、无未解决资源引用。
8. 在专用清理许可下调用destroy；返回常驻代码后清空入口、释放状态及代码槽。
9. 持久提交desired=unloaded及终态，返回此前已消费的generation。

停止超时不能free代码、复用槽或宣称卸载成功。部分清理后的实例也不能无条件恢复接单；应报告实际失败状态，保留映像直到可证明安全或重启。

应用自己写入 `exited=true` 不构成栈退出证据，因为随后仍可能执行应用的返回/析构路径。确认只能由常驻框架在调用返回后完成，或来自已验证的join。

公开的“清理完成”事件也不能提前释放仍被该回调栈使用的账本或状态。卸载最终动作在下一次安全调度点执行。

## 9. 0041 包与 ABI

采用独立0041格式，不兼容0031 APX1。以下为字段级草案，尚未冻结字节偏移，不是已经实现或冻结的编码合同。显式小端编码，不把native struct直接写磁盘。

### 9.1 包字段

```text
magic, format_version, header_length, total_length
app_id, build_id
target_firmware=0041, baseline_id
host_abi, required_capabilities, layout_id
state_schema, state_bytes, state_alignment
heap_limit, screen_count
variant_count
variants[
  slot_id, load_address,
  code_offset, code_length, entry_offset, payload_hash
]
package_hash, authentication_scheme, authentication
reserved_zero
```

校验顺序：有界读取头部 → 格式/长度/溢出 → variant范围与重叠 → target/基线/宿主ABI/布局 → 入口对齐及位于可执行段 → 配额 → 完整摘要与发布授权 → 标记staged。

精确字段宽度、magic和认证字节覆盖规则须在实现前冻结，并编写独立编码/解码测试。摘要字段及认证字段必须定义清零/排除规则，避免自引用。包哈希与兼容基线只能检查损坏/兼容性，不能替代发布者认证。发布密钥或现有认证上传的信任模型需明确选定，不能留成“CRC安全”。

### 9.2 入口与服务表

应用入口返回版本化C ABI表，提供：

```text
create(host_api, instance_handle, state)
start(state)
request_stop(state)
destroy(state)
handle_request(state, request, response)
step(state, now)
health(state)
```

服务表提供受控分配/释放、时钟、文件、帧提交、UI资源注册/撤销、定时和队列接口。表带abi_version和struct_bytes；扩展必须定义前缀兼容规则。

禁止跨边界传 `String/std::unique_ptr/Ap01Application`等C++对象。输入缓冲只在同步调用期间借用；异步必须复制并明确所有权。API表和context可长期使用的范围写入ABI合同，任何句柄都绑定实例代次。

应用不得直接调用任意ROM地址、创建线程或注册原厂回调。此约束由构建检查和发布审计执行，不宣称在共享地址空间中能阻止恶意机器码。

## 10. OTA 协议、批量、并发与幂等

以下路径、HTTP方法及结果码为拟定的新0041维护API，不是现有已实现路径或冻结接口。沿用常驻维护身份认证，不经过可卸载应用鉴权。

| 方法/路径 | 作用 |
| --- | --- |
| `POST /apps/packages` | 有界上传并校验，完成后返回package_hash；不自动load |
| `POST /apps/operations` | 接受load/unload批量请求，返回202和transaction_id |
| `GET /apps/operations/{transaction_id}` | 查询持久事务及逐项结果 |
| `GET /apps` | 查询逻辑应用记录、实际/期望状态、generation和配额 |

首版不支持分片续传；上传断开可重新上传同内容包，但不能由此重复激活。内容寻址包在重新验证后可去重。

### 10.1 请求示例

```json
{
  "transaction_id": "tx-20261021-001",
  "targets": [
    {
      "action": "load",
      "app_id": "weather",
      "package_hash": "sha256:...",
      "expected_generation": 0
    },
    {
      "action": "unload",
      "app_id": "clock",
      "expected_generation": 7
    }
  ]
}
```

哈希省略号仅为文档占位，实际协议必须要求完整规定长度的摘要。

规则：

- expected_generation=0仅表示从未创建逻辑记录的新app_id；已有未载入应用也有当前generation。
- 同一请求app_id不得重复；targets数量有明确上限。
- 语法错误、重复ID、受保护ID等请求级错误在执行前整体拒绝。
- 每项开始时重新核对generation；冲突仅使该目标失败。
- **按数组顺序串行执行，每项独立提交，失败后继续后续目标。**
- 不隐式重排。若需要先释放容量，应先提交unload目标，再列load目标。
- 首版同一时刻只执行一个生命周期批次。其他生命周期变更返回busy，状态查询继续工作。
- 应用写入/激活与完整固件安装使用常驻排他门。对原厂独立OTA通道，必须验证其与排他门的协调能力；只读取busy标志不等于消除了检查后并发启动的竞态。协调未证明前不能宣称所有写入通道互斥。

### 10.2 部分成功示例

```json
{
  "transaction_id": "tx-20261021-001",
  "state": "completed",
  "result": "partial",
  "targets": [
    {
      "app_id": "weather",
      "action": "load",
      "result": "failed",
      "error": "no_execution_slot",
      "generation": 0,
      "actual_state": "unloaded"
    },
    {
      "app_id": "clock",
      "action": "unload",
      "result": "ok",
      "generation": 8,
      "actual_state": "unloaded",
      "desired_state": "unloaded",
      "package_retained": true
    }
  ]
}
```

批量操作不承诺组原子性。前面的成功不会因后面的失败撤销，成功的unload也不会为了失败load自动恢复。

### 10.3 幂等与未知结果

- 相同transaction_id及规范化后相同参数：返回原状态/结果，不重复执行。
- 相同ID不同参数：`transaction_conflict`。
- 回复丢失：查询原ID，不自动创建新事务重试。
- load当前同包、unload已未载入实例，在generation匹配时返回unchanged，不推进generation。
- generation冲突返回当前版本与状态，客户端重新读取并明确决定后续操作。
- 幂等日志有界，记录保留期/数量在协议中声明。过期ID返回记录不可用，客户端查询当前应用状态，不能将其解释为“未执行”。
- HTTP成功只表示请求受理或结果已查询，不能把202视为全部目标已运行。

## 11. 持久记录、重启恢复与健康

### 11.1 两类持久记录

应用稳定记录保存app_id、稳定包hash、desired_state、generation及必要schema信息。事务记录保存请求摘要、目标列表、每项目标状态、当前操作意图及已提交结果。

采用带版本、长度、序号和校验的双记录，或经过验证的原子文件替换。必须定义同步落盘顺序并验证断电行为；不能默认普通write/rename已经保证持久。

### 11.2 恢复策略

1. 已提交目标保持结果。
2. 尚未开始目标标记not_executed，重启后不隐式继续批次。
3. 当前项只有意图、没有提交：恢复该应用上一稳定记录，记录interrupted。
4. 成功unload提交desired=unloaded，包仍存在不意味着重新启动。
5. 成功load提交desired=loaded和稳定包；重启按稳定顺序分配槽并逐个恢复。
6. 单应用恢复失败不阻止维护、发现和其他应用启动，actual=failed且保留desired。
7. 意图中已消费的管理generation不能因恢复上一稳定包而回退。恢复实例使用新的boot_id/instance_epoch；接口同时返回管理generation与运行代次，明确区分CAS状态和实例身份。

执行槽不是持久应用身份；重启可选择其他空槽的匹配variant。若布局改变且包没有对应variant，报告layout_mismatch，不执行旧地址代码。

### 11.3 健康与replace

load在试运行后提交：初始化成功、入口有界返回、调度可响应、health通过；声明可显示UI的应用需取得该实例真实draw。无UI应用不等待draw。窗口缺席/系统遮挡需报告等待原因并受试运行期限约束。

健康必须绑定app_id、boot_id/instance_epoch和build。宿主心跳和旧帧不能代替候选健康。

后续replace复用停机/加载：保留旧稳定包，新包失败则安全停止候选并重新实例化旧包。不能恢复失败时仍谎报“旧实例未变”。该操作已消费的管理generation不回退，重新实例化分配新的instance_epoch。

候选不得原地进行不可逆持久状态迁移。首版同schema，或使用候选副本并在提交时切换。

应用崩溃、死循环或内存破坏时，可能只能依靠受控重启/看门狗及常驻启动恢复。看门狗和启动恢复本身仍需独立验证，不能把在线回滚与重启恢复混为同一保障。

## 12. 精确实现改动点

下列为实施清单，不表示本次已改动。

| 文件/函数 | 必要改动 |
| --- | --- |
| `screen_host_0041.h/.c` | 定义应用可调用状态、暂停/清空接口；poll/prepare/input/entered/left统一检查；保留固定apps/root布局 |
| `ap01_host_retire()` | 保留窗口退役语义；不把它扩充为会意外破坏窗口重建状态的卸载替代品 |
| 新应用清空函数 | 单应用取消事务、unbind、清空descriptor/ID/count/poll/context、推进revision |
| `screen_port_0041.h/.cpp::draw/image_event/timer/event` | 长期回调常驻转发，注册记录绑定实例代次；清理完整后释放记录 |
| `ap01_window_bind/find/detach` | 保留宿主生命周期锚点，不随应用unload删除公共定时器或窗口 |
| `native_io_0041.*` | 仅在有证据后添加执行RAM/缓存同步绑定；不猜测join地址 |
| `native_application_0041.ld` | 宿主/应用构建分离后保留常驻布局；新增按槽应用链接脚本 |
| 新0041专属包/loader模块 | 解析、验证、槽选择、复制、执行屏障、入口绑定和释放 |
| 新0041专属生命周期/事务模块 | 注册表、配额、资源账本、load/unload、持久状态和幂等查询 |
| `codex_status/ports/ap01/native_0041.cpp::Runtime` | 单业务对象改为多应用注册表调度；维护、发现、窗口状态常驻 |
| `Runtime::bootstrap/serve/udp` | 服务只创建一次；维护/发现不依赖可卸载对象；业务按目标应用分发 |
| `present/processFrames/processActivation` | 补稳定应用身份、boot_id/instance_epoch及队列所有权；拒绝跨实例结果 |
| `timer/eventCallback/imageDrawn/dialogDrawn` | 保留常驻入口，通过许可和实例代次访问应用 |
| `codex_status/ports/ap01/application.h/.cpp`、HTTP接入 | 拆分认证/维护/发现与应用业务；加入批量操作和查询 |
| `codex_status/tools/check-ap01-native.py/link-ap01-native.py` | 明确0041宿主、按槽variant、打包及探针边界，检查导入/节/重定位 |

所有0031模块、APX1 ABI、链接脚本和构建入口保持独立。0041格式校验必须拒绝0031包；不能仅根据相似字段或接口名称推定兼容。

## 13. 分阶段交付与验收

| 阶段 | 交付 | 必须通过的验收 |
| --- | --- | --- |
| 0：资源与执行证据 | RAM地图、槽布局、缓存规则、存储语义 | 至少两个合法独立执行槽；原厂运行无重叠；未通过不得宣传热加载 |
| 1：常驻边界 | 控制面与业务分离 | 零应用时OTA/认证/发现可用；受保护ID操作整体拒绝 |
| 2：静态多应用生命周期 | 注册表、固定root池、资源账本、调用门 | 两应用共存；卸载A不影响B；反复装卸无旧回调/泄漏 |
| 3：动态机器码 | 按槽variant与loader | 两个不同应用同时执行；卸载后复用槽；错误地址/ABI/0031/溢出包拒绝 |
| 4：完整停机 | 队列与UI清理、inflight屏障 | HTTP中、动画中、draw中、迟到帧、窗口缺席逐项验证；超时不释放执行槽 |
| 5：批量协议 | 串行逐项提交、幂等查询 | load/load、unload/load、部分失败、generation冲突、回复丢失均符合协议 |
| 6：持久恢复 | 稳定记录、事务日志、启动恢复 | 每个持久边界注入失败/重启；已提交项保留；unload不复活；未执行项不自动继续 |
| 7：隔离回归 | 0041构建与产物清单 | 0031输入/源码/产物不被新功能修改；普通构建不含探针 |

故障验收还应包括：内存/存储配额耗尽、包认证失败、初始化失败、资源解绑失败、候选无draw、业务入口超时、恢复包损坏。结果必须区分可在线恢复、需重启恢复和无法确认安全三类。

离线模型能证明的是其覆盖路径；真实RAM执行、Flash/XIP并发、LCD/SPI、物理掉电和真实堆栈高水位需要另行证据。本文不授权刷机或部署。

最终成功标准：**至少两个独立机器码应用同时运行，可以分别或批量载入/卸载；卸载保留包、重启遵守desired-state；OTA常驻且始终不属于操作对象。** 只替换一个业务对象或重建窗口不满足该标准。

## 14. 待冻结事项

- 可执行RAM地址、槽数/容量、缓存同步与全局内存余量。
- `/resource`可用空间、耐久写入/恢复语义和事务记录预算。
- 精确包字段宽度、认证模型、ABI版本和能力列表。
- 注册表逻辑记录上限、每应用请求/资源配额及试运行期限。
- 原厂独立OTA与新增维护写入的排他协调。
- 应用长调用、卡死后的重启恢复及看门狗证据。

这些是实施前置验证或接口冻结项，不是已经存在的能力，也不能用任意地址、固定延时或未经核实的原厂入口填补。
