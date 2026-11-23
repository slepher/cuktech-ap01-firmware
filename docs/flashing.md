# AP01 0055／0.1.3 刷机说明

本文说明原厂 ROM 转入自定义 ROM 的条件、完整固件安装、双槽更新和故障恢复操作。

## 先确认正在运行的 ROM

| 当前运行固件 | 可用路径与限制 |
| --- | --- |
| 原厂 `1.0.2_0031` | 保留该版本；首刷入口为认证的 miIO OTA。需要核对目标设备、镜像、下载通道与恢复条件后再执行。 |
| 原厂 `1.0.2_0041` 或 `1.0.2_0055` | 未签名 OTA 被拒绝，不能直接用常规 miIO OTA 安装本项目 ROM；本仓库不提供已验证的通用解锁或降级流程。 |
| 已安装支持未签名 OTA 或独立维护升级的自定义 ROM | 按当前运行固件实际提供的升级接口操作，先核对运行槽与目标槽，避免覆盖可用恢复镜像。 |

**不要执行原厂 0031 → 原厂 0041／0055 的米家官方 OTA 升级来“准备刷机”。** 0041 起的签名门禁会关闭通过常规 OTA 安装未签名第三方 ROM 的入口。此限制描述的是 OTA 通道，不等于已证明所有硬件恢复手段都失效；也不能假定可通过普通 OTA 降回 0031。

本项目以 0055 为构建基线，但生成的是自定义镜像。打包器启用 `unsigned_ota`，允许其运行后的未签名 OTA；这个补丁只有在自定义 ROM 已安装并运行时才生效，不能改变正在运行的官方 0041／0055 对首次安装包的拒绝行为。`signed_file=false`、`app_force` 或 FDS 中转均不能替代该前置条件。

## 从官方 0031 转入自定义 ROM

1. **确认设备。** 通过设备所有者的米家账号确认 DID、型号 `njcuk.enstor.ap01`、MAC 和正在运行的 `1.0.2_0031`；不要只依据下载包名或米家更新提示判断当前版本。首刷不使用自定义固件才提供的设备码接口。
2. **选择完整镜像。** 从同一 Release 下载 `ap01-0055-base-0.1.3.bin` 或 `ap01-0055-app-platform-0.1.3.bin` 及 `SHA256SUMS`。前者提供无 App 基版，后者提供 ABI 3 加载平台。不能刷 `.payload.bin`、ELF 或 `.apx`。
3. **校验与恢复准备。** 使用 `SHA256SUMS` 核对完整 BIN，确认目标版本、运行槽和写入槽；保留恢复镜像和必要数据。附件与构建产物说明见 [版本发布](releasing.md)。
4. **准备固件下载地址。** 使用设备可访问、与安装工具要求一致的 HTTPS／FDS 通道，确认 URL 返回的字节与本地 BIN 完全一致。FDS 上传权限和 AP01 安装权限分别校验；中转仅解决传输。不要把 GitHub Release 链接直接假定为设备可接受的 OTA 地址。
5. **一次下发安装。** 经认证的工具向已核对的 AP01 DID 发送 `miIO.ota`，绑定目标 BIN 的 URL、MD5 和长度。应使用明确支持本项目完整镜像的安装流程；本仓库目前没有随版本交付的通用首刷客户端。外部安装工具不替代本项目镜像的实机验收。
6. **观察完成并验收。** 持续查询 `miIO.get_ota_state` 和 `miIO.get_ota_progress`，确认安装阶段、设备重启和重新上线；RPC 返回成功或下载达到 100% 都不能单独证明刷机成功。超时或断连时先查询状态，不重复下发安装。
7. **核对新系统。** 检查原厂页面、旋钮、网络及设备码菜单；通过维护诊断确认 `rom.base_version=1.0.2_0055`、`rom.modified_version=0.1.3` 和对应 build ID。基版应为 `supports_app=false`，加载平台应为 `true`。业务 App 另行安装，不把无业务 App 当作 ROM 安装失败。

在下载附件的目录可用 `sha256sum --check SHA256SUMS`（Linux）或 `shasum -a 256 -c SHA256SUMS`（macOS）校验；校验清单只包含两个完整 BIN，完整校验需下载这两个文件。只下载一个 BIN 时，单独计算其 SHA256 并与清单对应行比较。

## 自定义 ROM 的后续更新

先读取当前维护接口的能力、版本、槽位和事务状态。使用独立维护协议时，按设备回执执行 begin、分块上传、commit 和状态查询；未知结果继续查询同一事务，不创建第二笔升级。当前维护实现选择非活动槽，升级前必须确认该槽没有需要保留的恢复镜像。

## ROM 启动失败与恢复

### 30 秒健康窗口与 60 秒试启动超时

**30 秒是连续健康确认窗口，60 秒是启动保护启用后的总观察超时；都不是断电后必须等待的时长。** 本项目的 ROM 保护流程如下：

1. 必须事先登记一个有效的稳定槽，且该槽的镜像仍完整可用。
2. 新 ROM 运行在另一个槽时，维护服务读取固定的稳定槽编号，并先把**下次启动目标**设为稳定槽。成功后状态为 `armed`；当前运行不会立即切槽。
3. 维护监听和平台提供的健康检查连续通过 **30 秒**后，下次启动目标改为当前新 ROM，状态为 `healthy_locked`。
4. 从保护启用起 **60 秒**仍未完成连续健康确认，状态变为 `retained_stable`，下次启动目标继续保留为稳定槽。该分支本身**不会主动重启**；随后正常重启或断电再上电，才会尝试启动稳定槽。

计时从 `armBoot()` 启用保护开始，不保证与接通电源或屏幕亮起的时间一致。平台健康检查也不等于所有 App、页面和外设功能均已验收。App 集合的“连续健康 30 秒”属于另一层机制，不能用它判断 ROM 的回退状态。

### 刷机前准备恢复槽

通过已认证的 `GET /api/firmware/slots` 核对 `running_slot`、`stable_slot`、`stability` 和 `boot_safety`。稳定槽是固定的槽位指定，不绑定 ROM 版本、build 或镜像摘要；更换镜像后仍保留，无需重新登记。

`POST /api/firmware/stable` 接受 `device_mac`、唯一 `request_id`、`slot`（0 或 1）和 `confirm=true`。可以在任一运行槽指定另一个槽为稳定槽，目标槽不需要提供本项目接口。因此也可以指定装有原厂 ROM 的槽位。接口不暴露稳定记录修订号，不自动改变稳定槽编号。指定只保存回退目标，不保证目标 ROM 完整、可启动或具备维护接口。

### 刷入类型与稳定槽保护

刷写前运行 `python3 -B tooling/scripts/classify-rom.py <完整ROM.bin>`。工具先验证上传镜像格式和 CRC，以已知 SHA256 识别原厂原件，以镜像内类型字段识别本项目 base/App 平台，其余归为第三方 ROM。文件名不参与判断。

认证客户端将识别出的 `rom_kind` 传给 `POST /api/firmware/begin`；固件在打开 Flash 写入前执行以下规则。未申报类型按 `third_party` 处理。`force` 默认 `false`，必须显式传布尔值 `true` 才能强制覆盖稳定槽为 App 平台。

| 类型 | 刷写规则 |
| --- | --- |
| `base` | 默认允许，包括稳定槽 |
| `official_0031` | 默认允许，包括稳定槽 |
| `official_0041` | 允许，返回 `official_0041_restricts_third_party_ota` 警告 |
| `official_0055` | 允许，返回 `official_0055_restricts_third_party_ota` 警告 |
| `third_party` | 允许，返回 `third_party_recovery_unknown` 警告 |
| `app_platform` | 非稳定槽允许；稳定槽默认返回 `stable_slot_app_platform_requires_force` 且不开始写入；`force=true` 时允许并返回 `stable_slot_app_platform_forced` 警告 |

原厂 0041／0055 限制第三方 ROM 的常规 OTA 入口，也没有本项目维护接口；其他第三方 ROM 的恢复能力未知。警告与 `rom_kind` 随上传事务返回，客户端应在开始上传前展示本地识别结果。固件在提交时再核对本项目镜像内的类型与申报类型。上传和提交阶段保留整包 CRC 校验；已安装镜像不做运行内存比较或整包 CRC 重算。

原厂 ROM 无需提供指定接口，但从原厂 ROM 启动后，也不会执行本项目的启动保护逻辑。`stable_slot=null` 表示尚未指定稳定槽。

### 发生启动故障时

1. **先排除仍在刷写。** 下载、Flash 写入、校验和提交过程中不要断电。OTA 响应超时不等于刷写停止，先查询原事务或 OTA 状态，不重复安装。
2. **维护仍可访问时，先查状态。** 读取 `/api/firmware/status` 和 `/api/firmware/slots`，核对设备、运行槽、稳定槽及保护状态。处于 `armed` 时观察其转为 `healthy_locked` 或 `retained_stable`，不要把“已等 30 秒”作为回退已准备好的唯一依据。
3. **确认 `retained_stable` 后恢复。** 确认无 Flash 写入或提交进行中，使用已核对的重启路径；维护不可用但已确认稳定槽启动选择保留时，可断开 AP01 电源，确认设备完全掉电后再上电。代码没有规定“断电后再等 30 秒”。重新上电后核对实际版本、运行槽、画面和网络，不能只凭亮屏判定恢复成功。
4. **已经 `healthy_locked` 时不能靠等待回退。** 单次重启通常仍启动当前 ROM，但每次启动会重新预切稳定槽。在预切成功、尚未完成连续 30 秒健康确认的窗口内再次断电，下次上电可进入稳定槽。过早或过晚断电均不能保证切槽；不能以通电后固定秒数代替实际状态。维护仍可用时，可通过 `POST /api/firmware/switch` 明确选择已验证可用的另一个槽，再按事务回执执行 `/api/firmware/reboot`。切槽请求需绑定设备、唯一 `request_id`、`target_slot` 和当前 `expected_revision`；不得猜槽或反复重放新事务。
5. **`unconfigured`、`unknown` 或未进入维护启动阶段时，不保证断电可救回。** 若保护未执行、稳定槽损坏或启动选择写入失败，本机制不能保证恢复。停止循环断电和重复刷写，转用刷前已核实的物理恢复入口或厂商维修；本仓库不提供可保证成功的通用硬件救砖操作。

这套机制保存的是可启动槽位选择，不会自动恢复被覆盖的 ROM、用户数据或所有硬件故障。

## 核查依据

- [上游首次安装说明](https://github.com/wqytommy666/cuktech-screen-controller/blob/main/skills/cuktech-ap01-screen-kit/references/realtime-firmware.md)：说明官方 0041 对未签名 Loader 的拒绝，以及 FDS 中转不能绕过签名门禁。
- [0055 目标配置](../tooling/rom-targets/current.json) 中 `unsigned_ota` 定义文件偏移 `0x6cd60` 的 `dde7` → `7da0` 补丁；[打包器](../tooling/scripts/build-native-app-rom.py) 在两种自定义镜像中应用该补丁。
- [平台离线验证](0055-qemu-validation-20261106.md) 与 [ROM 清单](../roms/CATALOG.md) 说明产物校验与原件身份。来源与许可见 [NOTICE](../NOTICE.md)。

- [ROM 启动保护实现](../tooling/firmware-modules/native_firmware.cpp) 与 [维护回归](../tooling/firmware-modules/test_native_maintenance.cpp)：稳定槽登记、30 秒连续健康、60 秒超时与故障状态。
