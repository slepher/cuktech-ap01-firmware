# 0041 常驻独立诊断（2026-10-21）

用户要求先补齐 0041 独立诊断，再刷入。诊断接入 18080 常驻维护执行器，复用现有设备绑定认证，不依赖业务 owner、C2 帧、Bundle 或业务启动成功。原有 OTA、手动切槽与原厂恢复入口保留。

## 接口与范围

- `GET /api/diagnostic/status`：设备 MAC、boot ID、协议、读取能力及单块上限。
- `POST /api/diagnostic/file`：JSON `device_mac/path/offset/length`；只读 `/data/`、`/resource/` 下文件或 `/dev/ramlog`。拒绝相对路径、路径穿越及设备写入口。ramlog 是非阻塞有界采样。
- `POST /api/diagnostic/flash`：JSON `device_mac/offset/length`；调用已用于槽巡检的原厂物理 Flash 读取器，不打开写句柄。范围限 16 MiB NOR，单次 1–1024 B。
- 文件/Flash 回包包含原始字节的 hex、实际长度、CRC32、偏移和 boot ID；普通文件另含总长及 EOF。并发原厂 OTA 或维护升级期间返回 busy，状态查询仍可用。

文件可能包含 Wi-Fi 密码或绑定材料；客户端 `tooling/scripts/diagnostic-client-0041.py` 将字节写入指定私有文件，不打印其内容，拒绝覆盖已有证据，传输失败保留 `.partial`，不冒充完整导出。分块读不是整个文件系统的原子快照。这里没有新增远程命令执行；文件读取、日志、Flash 导出使用 HTTP，恢复继续使用独立维护接口。

## 构建来源

不使用尚未部署的屏幕宿主重构。以已部署 34 的 `ap01-native-0041-candidate-34.audit.json` 为依据，对 265 个源码/头文件逐项核验 SHA256；变动或已迁移文件从 Git blob 恢复。隔离树位于 `evidence/diagnostic-0041-20261021/source34`；来源清单为同目录上级的 `source34-identity.json`。

`tooling/scripts/enable-diagnostic-0041.py` 在隔离树中增加维护路由及只读回调，并记录 `integration.diff`。相邻 `codex_status` 业务源码未修改，部署结果另更新其交接卡。独立平台实现为 `native_diagnostic_0041.*`；文件和物理 Flash 回调复用 `native_vfs_0041.cpp`、`native_slot_0041.cpp` 的原件接口。

当前候选 `evidence/diagnostic-0041-20261021/ap01-0041-independent-diagnostic.bin`：7000056 B，SHA256 `29352943f2301cc7bcb5fac60a504803d3b3488afe11d56c5dc27c23bc6f176c`。候选与部署状态分别记录，不能仅凭构建通过宣称可刷或实机通过。

## 验证与部署进度

- 宿主诊断协议 ASan/UBSan 通过：二进制字节、CRC、EOF、错误、错误设备、路径穿越、范围溢出、busy 和不可用 reader。
- 完整应用及维护服务 ASan/UBSan 通过；增加未认证诊断拒绝和业务 offline 时诊断状态仍可读检查。
- RV32/ilp32f 交叉编译、XIP 可写段限制、完整链接和原厂镜像重建通过。
- 原生模拟通过：34 槽1向新候选槽0完整升级、新候选诊断及回切槽1，逐字节核对保护区；另通过原版 0031 恢复到槽0的精确镜像升级模拟。

## 槽位错误与恢复（2026-10-21）

后续普通应用升级遵守用户指定的固定角色：**救援槽0保留原版，不写入应用；应用写槽1**。需要升级槽1时先启动救援槽0，不能仅依据“非活动槽”选择写入目标。0041自身的诊断用于独立采集，不要求为采集而切换救援版。

首次实机部署错误地将诊断 0041 写入槽0，覆盖了用户要求保留的救援版。该次操作记录保留在 `evidence/diagnostic-0041-20261021/physical-installation.json`，不能描述为“救援未动”。

用户要求恢复后，先启动仍完整的 34 槽1，再把归档原版 0031 恢复到槽0。原版镜像 6822344 B，SHA256 `d843aae4e097c31ce06a315c62e1a66f4fb3bf9299db289b6f31562d0ef2231b`；恢复后已认证启动槽0。恢复过程及后续验证记录在 `evidence/diagnostic-0041-20261021/correct-slot-recovery.json`。

正确的最终布局固定为 **槽0原版0031救援、槽1诊断0041应用**。活动救援槽的读回在镜像相对 `[0x678800,0x67d400)` 出现无效字节，范围与[同机已证实的 PEC 读保护](knowledge/0031-pec-readback-and-controlled-upgrade.md)一致，不能把读接口成功或传输 CRC 当成有效原始数据。其余字节完整匹配原版。通过原有0031升级通道将上述诊断镜像写入槽1，启动槽1后，再完整读回非活动救援槽0核对 SHA256；实际完成状态以下方验证记录为准。

- 原救援 `/firmware` 返回 HTTP 200，`stage=done/error=ok/bytes=7000056`。
- 同 MAC 认证 `/health` 返回上述诊断 build，`/api/firmware/slots` 确认 `running_slot=1`。
- `/api/diagnostic/status` 确认文件及 Flash reader 已接入，并已实际导出非活动槽0字节。
- 维护状态中的旧“恢复救援到槽0”事务在槽1报告 `booted_other_slot`，属于旧事务与当前启动槽不一致；不代表本次原救援通道的槽1升级失败，不重发旧事务。
- 原厂页面、旋钮与物理屏幕观感本轮没有用户目视确认；网络认证与诊断通过不代替该项。

## 最终实机结果

恢复及正确槽位部署已完成，`correct-slot-recovery.json` 的最终状态为 `correct_slots_fully_verified`。

| 物理槽（从0编号） | 最终内容 | 实机验证 |
| --- | --- | --- |
| 0 | 原版0031专用救援，6822344 B，SHA256 `d843aae4e097c31ce06a315c62e1a66f4fb3bf9299db289b6f31562d0ef2231b` | 已认证启动；改从槽1读取后，全镜像逐字节及完整SHA256均匹配归档，包含PEC区 |
| 1 | 独立诊断0041，7000056 B，SHA256 `29352943f2301cc7bcb5fac60a504803d3b3488afe11d56c5dc27c23bc6f176c` | 当前运行；认证build、MAC、槽位及物理头尾匹配，`business_online=true` |

最终救援读回文件：`evidence/diagnostic-0041-20261021/final-inactive-rescue-readback.bin`，同名 `.json` 记录长度、完整哈希及逐块CRC核验。读取期间的临时503仅对同一只读范围有限重试，没有重发刷写。此前活动槽无效读数另存为 `restored-rescue-readback.bin`，不能将其当成原始备份。

新0041已实际完成Flash全量导出及1016 B `/dev/ramlog`采样；未认证诊断返回401。日志采样保存在私有证据 `evidence/private/ramlog-0041-20261021.bin`，未打印内容。`/data/wapi.conf`返回404，Wi-Fi持久化合同验证仍开放，不将诊断部署等同于配网兼容性闭环。

随后在不切槽、不重启、不写设备的条件下，仅用0041自身诊断导出真实data/resource分区，并独立读取11份相关文件。已确认本机使用 `/data/network.ssid`、`/data/e#network.password` 等多份PSM文件，21份原厂PSM文件尾CRC8全部匹配；详细合同及尚未执行的激活/绑定验收见[Wi-Fi选择与配网兼容性缺口](knowledge/0041-sim-wifi-selection-gaps.md#真实配置与持久化合同0041自身诊断2026-10-21)。
