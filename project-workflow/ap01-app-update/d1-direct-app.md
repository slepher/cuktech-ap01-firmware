# D1 真实 App 边界审计与实现记录

2026-11-03。D1 非实机纵向验收完成，无设备访问。下文保留分阶段记录，最终证据以末节为准。

## 53 项旧导入的迁移决定

输入为 `build/app-install/app-format-pic/pic-report.json` 与 `undefined-imports.txt`：24 源旧 PIE ET_REL 审计，**不是新 ABI 的最终导入数**。下表每行对应一个旧导入，列出的处理尚需真实新包最终链接验证；不得直接将所有 C++ 符号导出为 ABI。

| 旧符号（省略参数） | 新边界处理 |
| --- | --- |
| `ap01RomVfs` | 删除 App 中的平台后端构造依赖；平台提供已绑定本 App 上下文的直接文件/核心/网络函数。 |
| `ap01ServeNativeHttp0041` | 本地薄适配：HTTP parser/response 留在包内；String/Ap01HttpReply 不跨 C ABI。 |
| `ap01NativeAppCorePort0041` | 删除 App 中的平台后端构造依赖；平台提供已绑定本 App 上下文的直接文件/核心/网络函数。 |
| `ap01NativeAppNetworkPort0041` | 删除 App 中的平台后端构造依赖；平台提供已绑定本 App 上下文的直接文件/核心/网络函数。 |
| `Ap01AppCore0041::invoke` | 删除 invoke 依赖；客户端改成对应直接函数调用，平台保留配额、路径和写许可检查。 |
| `Ap01AppHeap0041::invoke` | 删除 invoke 依赖；客户端改成对应直接函数调用，平台保留配额、路径和写许可检查。 |
| `ap01_native0041::randomBytes` | 平台直接导出时钟/随机/让出执行，App 本地适配保持业务调用方式。 |
| `ap01_native0041::registerStock` | 删除 App 依赖；原厂 hook/事件转发属于常驻平台。 |
| `ap01_native0041::nowMs` | 平台直接导出时钟/随机/让出执行，App 本地适配保持业务调用方式。 |
| `ap01_native0041::pause` | 平台直接导出时钟/随机/让出执行，App 本地适配保持业务调用方式。 |
| `ap01_native0041::thread` | 平台导出带 App 上下文的任务创建；栈/任务预算由平台检查，不跨 C++ 任务类。 |
| `ap01_native0041::mainHook` | 删除 App 依赖；原厂 hook/事件转发属于常驻平台。 |
| `Ap01AppFiles0041::drain` | 删除更新卸载依赖；普通 close 保留，映像和回调保留至重启。 |
| `Ap01AppFiles0041::invoke` | 删除 invoke 依赖；客户端改成对应直接函数调用，平台保留配额、路径和写许可检查。 |
| `Ap01AppFiles0041::writes` | 删除 App 自行开放写门；写许可归平台裁决。 |
| `Ap01AppTasks0041::start` | 平台导出带 App 上下文的任务创建；栈/任务预算由平台检查，不跨 C++ 任务类。 |
| `Ap01AppNetwork0041::drain` | 删除更新卸载依赖；普通 close 保留，映像和回调保留至重启。 |
| `Ap01AppNetwork0041::invoke` | 删除 invoke 依赖；客户端改成对应直接函数调用，平台保留配额、路径和写许可检查。 |
| `Ap01NativeServices0041::start` | 维护实例移到平台且先于 App 启动；App 仅接 busy 与 C 格式的配对/身份回调。 |
| `Ap01NativeServices0041::Ap01NativeServices0041` | 维护实例移到平台且先于 App 启动；App 仅接 busy 与 C 格式的配对/身份回调。 |
| `Ap01NativeServices0041::~Ap01NativeServices0041` | 维护实例移到平台且先于 App 启动；App 仅接 busy 与 C 格式的配对/身份回调。 |
| `Ap01NativeServices0041::busy` | 维护实例移到平台且先于 App 启动；App 仅接 busy 与 C 格式的配对/身份回调。 |
| `ap01_event_code` | 原厂事件解析归平台；App 使用明确 C 事件或 UI 表的回调查询，不引用外部全局符号。 |
| `ap01_event_context` | 原厂事件解析归平台；App 使用明确 C 事件或 UI 表的回调查询，不引用外部全局符号。 |
| `ap01_event_key` | 原厂事件解析归平台；App 使用明确 C 事件或 UI 表的回调查询，不引用外部全局符号。 |
| `ap01_event_target` | 原厂事件解析归平台；App 使用明确 C 事件或 UI 表的回调查询，不引用外部全局符号。 |
| `ap01_host_api` | 平台导出已有页面集合操作，绑定本 App 注册上下文；复用现有 C 页面描述。 |
| `ap01_host_button` | 宿主所有权和全局输入/轮询移至平台；业务通过本 App 页面操作/状态访问。 |
| `ap01_host_cancel` | 宿主所有权和全局输入/轮询移至平台；业务通过本 App 页面操作/状态访问。 |
| `ap01_host_current` | 宿主所有权和全局输入/轮询移至平台；业务通过本 App 页面操作/状态访问。 |
| `ap01_host_destroy` | 宿主所有权和全局输入/轮询移至平台；业务通过本 App 页面操作/状态访问。 |
| `ap01_host_enter_ready` | 平台导出已有页面集合操作，绑定本 App 注册上下文；复用现有 C 页面描述。 |
| `ap01_host_find` | 平台导出已有页面集合操作，绑定本 App 注册上下文；复用现有 C 页面描述。 |
| `ap01_host_init` | 宿主所有权和全局输入/轮询移至平台；业务通过本 App 页面操作/状态访问。 |
| `ap01_host_poll` | 宿主所有权和全局输入/轮询移至平台；业务通过本 App 页面操作/状态访问。 |
| `ap01_host_retire` | 平台导出已有页面集合操作，绑定本 App 注册上下文；复用现有 C 页面描述。 |
| `ap01_host_rotate` | 宿主所有权和全局输入/轮询移至平台；业务通过本 App 页面操作/状态访问。 |
| `ap01_host_set_blocked` | 宿主所有权和全局输入/轮询移至平台；业务通过本 App 页面操作/状态访问。 |
| `ap01_host_short` | 宿主所有权和全局输入/轮询移至平台；业务通过本 App 页面操作/状态访问。 |
| `ap01_lvgl_0041` | 平台提供现有版本化 LVGL C 表；只在 UI 执行器使用，回调与像素所有权显式约束。 |
| `ap01_window_active` | 平台直接提供本 App 的可见/活跃状态与 overlay/wake/activity UI 操作。 |
| `ap01_window_activity` | 平台直接提供本 App 的可见/活跃状态与 overlay/wake/activity UI 操作。 |
| `ap01_window_awake` | 平台直接提供本 App 的可见/活跃状态与 overlay/wake/activity UI 操作。 |
| `ap01_window_bind` | 唯一 window 生命周期/挂载归平台，App 注册页面；不复制 window/host。 |
| `ap01_window_detach` | 唯一 window 生命周期/挂载归平台，App 注册页面；不复制 window/host。 |
| `ap01_window_find` | 唯一 window 生命周期/挂载归平台，App 注册页面；不复制 window/host。 |
| `ap01_window_idle` | 平台直接提供本 App 的可见/活跃状态与 overlay/wake/activity UI 操作。 |
| `ap01_window_mount` | 唯一 window 生命周期/挂载归平台，App 注册页面；不复制 window/host。 |
| `ap01_window_overlay` | 平台直接提供本 App 的可见/活跃状态与 overlay/wake/activity UI 操作。 |
| `ap01_window_port` | 唯一 window 生命周期/挂载归平台，App 注册页面；不复制 window/host。 |
| `ap01_window_unmount` | 唯一 window 生命周期/挂载归平台，App 注册页面；不复制 window/host。 |
| `ap01_window_visible` | 平台直接提供本 App 的可见/活跃状态与 overlay/wake/activity UI 操作。 |
| `ap01_window_wake` | 平台直接提供本 App 的可见/活跃状态与 overlay/wake/activity UI 操作。 |

## 数据重定位与运行库

- 原源对象汇总有 35 个 GOT_HI20；旧合并对象还含 R_RISCV_32、32_PCREL、ADD32/SUB32、CALL_PLT、PCREL_HI20/LO12、BRANCH/JAL/RVC 与 RELAX。它们只是清点，不能直接整表加入加载器白名单。
- JSON allocator 虚表、字体表、operationNames 和 Bundle legacy 列表含 `.data.rel.ro*` 指针。保留业务数据；最终链接时逐项生成有界 BASE32 修正，双链接基址归一化必须逐字节一致。
- 该报告的 24 个源对象没有非空 `.init_array/.fini_array/.tdata/.tbss` 节；仍须检查最终链接加入的运行库。启动只做显式构造，不能漏掉构造器或依赖 ROM 初始化。
- 旧链接审计使用私有 heap/time/format 对象、纯 mem/string/calendar/SHA 对象和 libm/libgcc。新包不继续扩张私有 libc：malloc/free/time/格式化优先通过平台直接函数；C++ new/delete 只做本地薄适配；数学与编译器辅助保留在包内并纳入最终 relocation 审计。
- `Ap01HttpReply` 含 String，旧维护 pairing 回调不能跨新 ABI。平台独立维护应在没有 App 时可启动；配对桥需明确长度和调用期间有效的 C 缓冲区，不能强转旧类布局。

## 已完成：容器与入口隔离

沿用 APX2 容器格式 2、256 字节头，新增 ABI major=3/minor=0。偏移 88/92/96 为 start/event/health，100/104 必须为零。三个入口均必需；无事件功能时提供 no-op。签名与生命周期见 `tooling/firmware-modules/app_abi_v3.h`，平台函数表成员尚未冻结。

Apx2Limits 显式选择 ABI，默认仍为 2；新启动路径必须选择 3，两个版本相互拒绝。旧五入口执行器额外拒绝 ABI 3 limits，避免调用者改变 limits 后误执行新包。ABI 3 进入 start 后映像保留至重启，失败也不得在线释放/替换。

验证：`test-apx2.py --out build/app-install --tool-prefix build/s1/toolchains/xpack-riscv-none-elf-gcc-12.5.0-1/bin/riscv-none-elf-`，ASan/UBSan、11 组 SHA、两基址加载、损坏/截断/I/O/预算检查、新旧 ABI 互拒与保留入口拒绝通过，生产源 RV32 编译通过。新格式黄金包 SHA256 `39eb8693564d0f9dbd9786624f45499584726269cd4eb99747b9b38f2b050a0f`，仅格式样本，不能执行。报告 `build/app-install/apx2-report.json`。

旧执行器 `test-app-image-0041.py --out build/app-install --package build/app-install/golden.apx2 --tool-prefix build/s1/toolchains/xpack-riscv-none-elf-gcc-12.5.0-1/bin/riscv-none-elf-` 的 15 组路径与 ABI 3 拒绝通过，报告 `build/app-install/image-report.json`。这是迁移保护，不将旧热卸载测试记为新 App 启动证据。

## 直接文件/网络表：真实业务宿主验证

新增 `native_vfs_api_0041.h` 将原有 Ap01VfsOps C 表从 C++ File 包装中分离，RV32 布局 52 B；业务的 File/LittleFS、BundleStore、Ap01Business 和 Ap01Application 无需改写。`app_files_v3` 是常驻平台适配：16 个 App 本地句柄、私有根路径检查、默认只读、已有句柄同步受写门约束；关闭失败保留失败状态至重启。write 直接传入缓冲区，不再编码 208 B 请求或拆 1KB 块。平台变更写许可必须取得同一锁，成功意味着先前写入已结束。

新增 `app_network_api_v3.h`（RV32 表 36 B、peer 8 B）与 `app_network_v3`：直接 TCP/UDP 函数、8 个不复用的 App 本地句柄、分配端口检查、单调绝对期限与有界重试。复用已有原厂 transport port；不调用其旧 invoke 服务。App 侧 `app_network_client_v3.h` 仅作类型/长度薄适配，期限在平台执行。实际原厂 accept/调度时限仍需后端验收，不由宿主 fake 证明。

`test-app-readonly-0041.py --out build/app-install --direct-files --tool-prefix build/s1/toolchains/xpack-riscv-none-elf-gcc-12.5.0-1/bin/riscv-none-elf-` 验证真实业务的 Bundle 恢复、渲染、只读配对/写入拒绝、写许可重新开放，以及真实 HTTP parser 的 8 类读写/期限/部分回复故障。另覆盖 1300 B UDP、维护端口拒绝、错误类型/失效句柄、文件容量和路径越界。直接模式不链接旧 core/files/network/heap invoke 源，并检查产物中无这些 invoke 符号。报告 `build/app-install/readonly-direct-report.json` 含源哈希和 RV32 适配对象/静态栈信息。

这仅证明真实业务源消费直接文件/网络 C 表；原生 `native_0041.cpp` Runtime 尚未迁移，不能宣称整个 App 已使用 ABI 3。核心/内存/任务/UI/维护回调表和平台启动组合仍待完成。旧 `--out build/app-install` 模式回归也通过，未删除原生产路径。

## 真实 Runtime、最终链接与独立包（本轮新增）

真实 `codex_status/ports/ap01/native_0041.cpp` 增加 `AP01_FILE_APP_V3` 分支，沿用同一业务/UI 实现，不复制另一份 App。该分支不构造旧 core/files/network invoke、代际任务或维护实例；接平台直接文件/网络表、任务创建和 busy/write 状态，host/window/registry slot 改为平台持有的引用，UI 通过现有 C 表调用。旧 XIP 分支保留且 RV32 编译通过。平台具体所有者、启动顺序和 input/poll 调度尚需接通，不能将引用改造视为常驻平台已经完成。

`app_platform_api_v3.h` 提供真实调用所需的 C 表成员（仍是集成中的草案布局），包括版本/大小/能力、每 App 上下文、文件/网络、核心时钟/随机/MAC、配额分配、任务、已有 UI 表和维护绑定。配对通过 C 请求和借用回复缓冲区回调返回，不跨 `String/Ap01HttpReply`。`app_runtime_v3` 只做 malloc/new/time 等薄适配；snprintf 通过函数指针直接传递 RV32 变参，不链接私有 printf 实现。platform_build/App 包摘要由平台提供，不引用 ROM manifest 绝对符号。

包内入口 `ap01_app_start_v3/event_v3/health_v3` 已最终链接。start 发布 instance 后即保留至重启；工作线程退出、监听失败反映为健康失败。业务 HTTP 监听成功才进入 ready；完整健康语义还需模型监督验证。试运行写许可由平台决定，业务在暴露配对回调前进行只读恢复。

构建入口：`build/s1/python/bin/python -B tooling/scripts/build-app-v3-0041.py --out <预建空目录> --app-config /Users/slepher/project/codex_status/ports/ap01/build-0041.json --tool-prefix build/s1/toolchains/xpack-riscv-none-elf-gcc-12.5.0-1/bin/riscv-none-elf-`。编译业务 22 源（不装入旧 ROM manifest/私有布局预算记录）和 5 个本地运行/HTTP/calendar/SHA 支持源；链接 libm/libgcc，记录工具链版本、源/头/库哈希与静态栈。使用 medany 的直接 PC-relative 地址；由最终重定位审计与双基址归一化证明可重定位，不把编译选项本身当证据。

已验证两份独立构建 `build/app-install/d1-v3-08` 和 `d1-v3-09`，APX2 字节完全一致：

| 项目 | 结果 |
| --- | --- |
| APX2 大小 / SHA256 | 203,520 B / `534aaf63864de293da1b399c9f887c4920cc5b007f862b6732abfa4da7dd458a` |
| 初始化映像 / image+bss | 202,688 B / 202,696 B |
| BASE32 / 三入口偏移 | 72 / 0、744、812 |
| 最终未解析导入 | 0 |
| 离线链接基址 | 0x10000、0x100000，归一化映像/修正/入口一致 |
| 包声明堆 / 任务栈 | 2,097,152 B / 40,960 B，模型限额，非硬件容量承诺 |
| 最大源函数静态栈帧 | BundleStore::bsInstall 1,024 B；bootstrap 480 B，非调用链高水位 |

本包有 599 对 ADD32/SUB32 跳转表差值重定位：离线解析只接受同一对齐数据字、紧邻成对、两个目标均在包内且链接后字值恰为目标差；保持基址无关的差值，不生成运行期修正。GOT/隐式初始化/TLS 被链接脚本拒绝。六项篡改（缺失/错序配对、错误差值、外部目标、未对齐字、GOT 类型）均拒绝。其余保持原有相对指令与 BASE32 白名单；设备仍只理解 BASE32。

验证命令：`build/s1/python/bin/python -B tooling/scripts/test-app-v3-artifact-0041.py --build build/app-install/d1-v3-08 --repeat build/app-install/d1-v3-09 --out build/app-install`。报告 `build/app-install/artifact-report.json`。生产 `apx2Load` 在宿主 ASan/UBSan 下对真实包执行两处**合成**基址加载，逐项检查全部修正、BSS 和边界守卫，通过；没有执行 App 指令，不代表所用地址在实机可执行。旧 XIP 原生源交叉编译、跨仓边界检查及两仓 diff 检查通过。

## D1 最终验收：平台组合与真实包执行

上述草案、待执行与旧包数字是分阶段历史；本节替代这些状态。直接表已冻结为 [ABI 3.0 合同](../../docs/app-platform-api-v3.md)，包含版本/布局、每 App 上下文、线程/阻塞/缓冲区所有权及入口事件。RV32 C/C++ 布局断言通过。

`native_app_platform_v3` 拥有唯一维护、screen_host/window/注册槽、直接文件/网络 provider、分配/线程预算和 boot owner。维护监听确认后才调用 App start；未绑定业务回调时维护保持可用。`app_binding_v3` 转换旧维护 C++ 请求/回复与 C 缓冲区回调；绑定只发布一次。`app_boot_v3` 完成校验、预留、加载、publish 和入口调用；预留后失败也保留映像至重启，不提供释放/卸载。

平台 worker 打开固定 `/resource/app-current.apx2` 并排队，UI tick 进行 load/start，结束后关闭文件。摘要取自包头并校验完整内容，尚无 Manifest 授权或新事务。默认生产 backend 明确拒绝 reserve，保留维护，不未经 H 验证执行 RAM。

正常 root DELETE 时平台销毁 host/detach window，业务清理页面并保留 Runtime/线程。下一次 root 注册以 event=3 重建页面，不重新 start。D1 沿用原 App 的输入/poll 转发，D2 才扩展为多 App 全局调度。

最终真实包为 `build/app-install/d1-v3-11/app.apx2`，与 `d1-v3-12` 独立构建字节一致：

| 项目 | 最终结果 |
| --- | --- |
| APX2 大小 / SHA256 | 203,696 B / `581eafe33e3e524a3aefdb32e30905be75be304cfa202f14efcdbda113de1dcc` |
| image / image+bss | 202,864 / 202,872 B |
| BASE32 / 三入口偏移 | 72 / 0、498、646 |
| 最终未解析导入 | 0 |
| 链接基址 | 0x10000、0x100000，归一化一致 |
| 堆 / 任务栈声明 | 2 MiB / 40,960 B，模型预算 |

`test-app-v3-artifact-0041.py --build build/app-install/d1-v3-11 --repeat build/app-install/d1-v3-12 --out build/app-install` 通过：源码/头文件哈希、重复构建、六种坏 relocation 拒绝、生产 loader 全部修正/BSS/守卫。最大源函数静态帧仍为 bsInstall 1024 B、bootstrap 480 B，不是调用链高水位。

完整平台构建使用 `build-firmware-0041.py --boot-app-v3 --build-dir build/app-install/d1-platform-v3-02 --output build/app-install/d1-platform-v3-02.bin --tool-prefix build/s1/toolchains/xpack-riscv-none-elf-gcc-12.5.0-1/bin/riscv-none-elf-`，目录预建、输出须不存在。候选 6,897,352 B，SHA256 `53629b54908e6681c73dad6f256c299a9d0245a800e9301c4b5fb7d0e0ab141c`；`test-firmware-0041.py --manifest build/app-install/d1-platform-v3-02.manifest.json` 通过。manifest 记录硬件 backend 不可用，**不可部署、未部署**。

宿主 `test-native-app-platform-v3.py --out build/app-install --package build/app-install/d1-v3-11/app.apx2` 的 10 场景通过 ASan/UBSan：维护先行、一次启动、身份/能力/包错误、预留/发布/启动失败保留、固定文件关闭一次、配额与不可变 C 回调复制。此测试使用宿主 App 入口替身。

### james.local Docker 真实 RV32 执行

`build-app-v3-guest-0041.py --out build/app-install/d1-v3-guest-03 --package build/app-install/d1-v3-11/app.apx2 --tool-prefix build/s1/toolchains/xpack-riscv-none-elf-gcc-12.5.0-1/bin/riscv-none-elf-` 构建模型 guest；runner 复用 `test-app-abi-qemu-0041.py --direct-v3` 的有界 GDB 传输。

最终 `build/app-install/qemu-james/d1-v3-run02.json`：两个基址 0xa8000000、0xa8040000 均返回 0，SP 与整数 callee-saved 保持。guest SHA256 `ea21214e107a9aabccd7eb9767f2ac95b714d3d9dab930392eb9e2774b4c4d20`。实际执行生产 loader/provider/host、包内 start/event/health、真实业务 bootstrap/HTTP listen 和 UDP discovery。8 页面槽注册，业务栈 32768 B、发现栈 8192 B，空数据启动 online/health OK。root DELETE 后 Pending，重建后 OK，维护仍一次、线程仍两个；模型线程栈底 64 B 守卫完整，非实机高水位。

Docker 为 `ap01-abi-qemu:20261103`，image ID `sha256:0478bf66b12b274e5d365560dfbc0869897abc6dc80ef974066df04d98e69681`；只读 rootfs、network none、2 CPU/512 MiB/64 pids、非 root、临时 /tmp、输入只读/独立输出。engine SHA256 `25a9c3620f83411672359412d6aca73c20f0e2eb94d6a8fbae5e4c39f3be3f11`，support SHA256 `28d04c47a497ba2c4caaf646ed651e01558545ba71f0345682e8f8972dc60a02`。未安装宿主依赖、未操作实机。

| 真正执行 | 替身或未证明 |
| --- | --- |
| 真包三入口、业务/发现线程代码、C 调用 | 协作模型线程替代 RTOS，无抢占/中断证明 |
| 维护先就绪与不可变业务绑定 | maintenance listener 替身，完整维护 HTTP 未在 guest 执行 |
| 固定文件读取、校验、加载 | 内存映射 VFS，无 Flash/掉电证明 |
| 空数据恢复、HTTP/UDP listen/等待 | 网络无数据/AGAIN，不证明实际收发/ROM accept 时限 |
| 真实 host 注册与 root 重建 | LVGL/窗口底层替身，不证明像素/旋钮/完整原厂 ROM |
| 平台堆/任务配额 | bump allocator 不回收物理内存，整数 formatter/固定 UTC 替代 ROM |
| 双地址修正与执行 | 模型 PSRAM，不证明硬件权限/cache/容量 |

真实 Bundle 恢复/渲染/网络故障仍由前述宿主测试覆盖，不能与 QEMU 空数据启动混称实机证据。跨仓边界及 3 项统一构建测试通过。

D1 六项已验收。D2 的 Manifest、第二独立包、全局输入/健康监督、私有目录/总资源预留，以及 D3/D4 集合事务、重启切换、单更/批更产品闭环尚待完成。H 实机准入排除于本轮且未完成。
