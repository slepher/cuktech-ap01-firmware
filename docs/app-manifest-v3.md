# AMF3 完整 App 集合 Manifest

D2 第一版编码与生产校验已实现。Manifest 表示一次开机的完整集合，独立于 APX2 容器和后续集合事务日志。解析器为 `app_manifest_v3.cpp`，离线写入器为 `app-manifest-v3.py`；字段逐字节小端读取，不序列化 C++ struct。

## 编码

文件恰为 `64 + count*160 + dependencies*40` 字节，禁止尾随数据。格式最大 8 个条目、56 条有向依赖；这是解析器边界，实际允许数由平台能力和预算决定，不承诺设备能运行 8 个 App。空集合合法，用于未安装或首装回退。

| 头偏移 | 字节 | 内容 |
| --- | --- | --- |
| 0 | 4 | ASCII AMF3 |
| 4 | 2 | 格式版本 1 |
| 6 | 2 | 头大小 64 |
| 8 | 4 | 文件总长度 |
| 12 | 2 | App 条目数 |
| 14 | 2 | 条目大小 160 |
| 16 | 8 | 非零集合序号 |
| 24 | 2 | 依赖条目数 |
| 26 | 6 | 全零保留 |
| 32 | 32 | SHA256：将本字段置零后覆盖整个文件 |

App 条目严格按 app_id ASCII 字节排序，ID 唯一。所有字符串含 NUL，剩余填零；长度 1–31，只接受字母、数字、点、下划线、横线和加号。ID 额外禁止 `.`、`..`，目录不接受调用者路径。version 使用同样字符范围。

| 条目偏移 | 字节 | 内容 |
| --- | --- | --- |
| 0 / 32 | 各 32 | app_id / version |
| 64 | 32 | APX2 内容摘要，即包头 192..223，非整个文件 SHA |
| 96 | 4 | 包长度 |
| 100 | 4 | image+bss 大小，不含堆/栈 |
| 104 / 108 | 各 4 | 堆预算 / 累计任务栈预算 |
| 112 / 116 / 120 | 各 4 | 数据读取最小 / 最大 / 写版本 |
| 124 | 8 | 必需能力位 |
| 132 / 134 | 各 2 | 分配 TCP / UDP 端口，0 表示没有 |
| 136 | 2 | 启动序号，必须完整排列为 0..count-1 |
| 138 / 140 | 各 2 | 任务上限 / 页面槽上限 |
| 142 | 2 | 全零 |
| 144 | 4 | App ABI major，当前必须 3 |
| 148 | 12 | 全零保留 |

依赖表按 `(owner_index,target_index)` 严格排序；索引指 ID 排序后的条目，不是启动序号。偏移 0/2 为 uint16 owner/target；4..7 全零；8..39 为依赖方声明接受的目标 APX2 内容摘要。禁止缺项、自依赖、重复依赖和摘要不匹配；目标启动序号必须小于依赖方，所以环直接拒绝。首期用精确包摘要声明兼容集合，不实现 semver 区间。只更新被依赖包而未提供兼容声明会拒绝，不能因整集回退自动推定版本兼容。声明是授权发布者提供的集合元数据，不是从业务二进制自动推断的依赖；同一包可在不同已审阅集合中声明不同兼容目标。跨 App 共享持久数据仍不支持。

## 资源与完整包预检

当前每项上限 4 任务、32 页面；整体上限从 `Ap01ManifestLimitsV3` 输入。同协议非零端口不得重复，平台保留端口 18080 不分配。映像逐项向上对齐 16 B，再累计映像/堆/栈/任务/页面/存储，使用 uint64 防求和溢出；总 RAM 先扣 resident 维护预留。这里验证声明，实际创建任务/分配内存/挂页还须由平台 per-App provider 执行同一限额。

`ap01CheckManifestPackagesV3` 复用生产 `apx2Validate`，在任何执行预留/start 前遍历整个集合；核对真实包 ID、版本、内容摘要、大小、映像/堆/栈、能力和数据合同，读取平台提供的当前数据版本。open 成功的 reader 在任何结果下均 close。预检通过不允许调用者随后修改文件；启动时仍通过 loader 再校验摘要。

`Ap01AppSetBootV3` 等待维护 ready，核对受信任选择方提供的 Manifest 摘要，预检全部包后才按 order 准备独立 loader/API/context 并启动。缺包/坏包使 prepare/start 次数为零；第二项启动失败保留所有已预留映像，整个集合失败，本次开机再调用 boot 返回 AlreadyAttempted。空集合启动成功；health 聚合所有已启动 App，但 10/30/40 秒持续监督和重启裁决尚待接入。

## 生成与验证

输入 JSON 只接受 sequence/apps；每项含 package、order、tcp、udp、tasks、pages、requires。包路径相对 JSON 文件；requires 将目标 app_id 映射到其 APX2 内容摘要。包内身份/预算从实际包读取并完整校验，输出使用排他创建，拒绝覆盖已有 Manifest。输入 App 列表顺序不影响输出字节。

```
python3 -B tooling/scripts/app-manifest-v3.py --config release.json --output release.amf3
python3 -B tooling/scripts/test-app-manifest-v3.py --out build/app-install/d2-manifest --package build/app-install/d1-v3-11/app.apx2 --tool-prefix build/s1/toolchains/xpack-riscv-none-elf-gcc-12.5.0-1/bin/riscv-none-elf-
```

输出目录须预建。报告 `build/app-install/d2-manifest/manifest-report.json`：宿主 ASan/UBSan、RV32 严格编译，覆盖空/两项/上限、规范编码、资源/依赖/端口冲突、所有截断点、读失败、第二包失败不启动、启动部分失败保留和重复启动拒绝。第二个包目前只是元数据 fixture，start/event/health 为宿主入口替身，未执行它的 RV32 指令。

尚未完成：常驻原生平台从单槽改为多槽、真实第二 App、Manifest 持久选择、平台所有权/资源限额和持续监督、重启集合事务及客户端。以上模块尚未替换 D1 的生产固定文件入口。无实机操作，不代表硬件准入。

多包宿主接线使用 resident-only `ap01_host_append`：平台在稳定数组的下一个位置填入该 App 注册信息，再追加到已有 host。注册不得重置先前 App 页面、revision 或输入状态；容量/身份/根冲突或转场中均拒绝。这不改变 ABI 3.0 表，不允许 App 自行追加宿主成员。D1 attach 已复用此入口，多槽 provider 仍待接入。

Manifest Entry 现可直接构造 `Ap01NativeAppPlatformV3` 上下文，条目按值保留。资源预留前再次核对实际包身份/摘要/大小/能力，任务与页面创建按该项上限执行。端口由该项分配；codex_status 兼容既有 `/resource/codex-status` 数据根，其他 ID 由平台生成 `/resource/apps/<id>`。这是后续集合容器的 per-App 授权路径；现有默认入口仍只创建一个平台，共享维护/宿主接线、目录创建/首次迁移与维护写集隔离尚待完成。
