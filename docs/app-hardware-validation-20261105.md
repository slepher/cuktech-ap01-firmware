# 0041 独立 App 首次实机验证包

2026-11-05。仅完成离线准备；没有连接、刷写或重启设备，没有修改 0031。候选尚未硬件验收，保留 `flashable:false`、`hardware_verified:false`，不能把离线通过当作刷写授权。首次实机操作须另行明确执行。

## 交付物

本机目录：`build/hardware-validation-20261105/`（从 firmware 仓库根目录解析）。

| 文件 | 用途 | 大小 |
|---|---|---|
| `platform-0041.bin` | 不内置业务 App 的 0041 平台 ROM，AUT3 开机选择、ABI 3 C 表、生产 RAM 执行后端 | 6,933,864 B |
| `platform-0041.manifest.json` | ROM 构建身份、加载配置及未验收标记 | 见文件 |
| `app/codex_status.apx2` | 真实业务 App，版本 d1.0；沿用已执行 QEMU 验证的包 | 205,360 B |
| `app/install.amf3`、`app/install.json` | 完整目标集合，仅 codex_status，无测试 peer；集合序号 1 | 224 B / 配置 |
| `app/empty-recovery.amf3`、`app/empty-recovery.json` | 成功首装后主动停用 App 的空集合；序号 2 | 64 B / 配置 |
| `SHA256SUMS`、`release.json` | 文件校验和、版本及来源 | 见文件 |
| `evidence/` | 平台校验、生产单包校验、App 原始构建报告 | 见文件 |

ROM SHA256：`6be0c0d0d1b3e393b38ea2b04db1c7a1ea0edab46e491e7e6fdf4afbdc769350`。
App 文件 SHA256：`27bb07332aff6eef0726f48ea09c3638eadee8df2be23b652324f6fed0e0b2cb`。
安装集合内容摘要：`6e3eaa070484e60881d4880559103c09d009c7f9203df4636670079db8a8701c`。
App 内容摘要：`c7e249647aa527ab6600abfbd8ee9f27679583ba91662e92f60453ac08bbe11d`。
内容摘要来自包/清单头，与整个文件 SHA256 不同；设备存储按内容摘要命名。

平台 build ID 为 `d395cea07912821f603d2d68cf46f9c1`，执行代码与上一候选相同。新输出路径改变审计 JSON 摘要，因此 ROM 头与完整文件 SHA 变化；核验以本包 SHA 为准。业务包固定到已验证版本，不混入其他对话正在修改的业务协议。

## 离线检查与复建

从仓库根目录执行校验（均不访问设备）：

```sh
(cd build/hardware-validation-20261105 && shasum -a 256 -c SHA256SUMS)
python3 -B tooling/scripts/test-firmware-0041.py --manifest build/hardware-validation-20261105/platform-0041.manifest.json
```

本包实际平台构建命令如下；复建须换全新的输出目录/文件，不能覆盖证据：

```sh
python3 -B tooling/scripts/build-firmware-0041.py --boot-app-v3 \
  --build-dir build/hardware-validation-20261105/platform-build \
  --output build/hardware-validation-20261105/platform-0041.bin \
  --tool-prefix build/s1/toolchains/xpack-riscv-none-elf-gcc-12.5.0-1/bin/riscv-none-elf-
```

单 App 与空集合通过生产 `ap01ReadManifestV3`，真实包通过 `ap01CheckManifestPackageV3`，使用生产启动资源限额（含暂存扣账），宿主 ASan/UBSan 通过。此项未执行 App 指令；既有 QEMU 是双包集合证据，本次没有把单包实机或完整 ROM 启动标成通过。内存/cache、原厂启动、真实调度和恢复入口仍需硬件验证。

## 一、刷入平台 ROM（待现场授权）

1. 认证确认设备 MAC、当前 build、运行槽、稳定槽及两槽镜像身份；记录维护状态与当前事务 revision。历史交接是运行槽 1、0031 救援槽 0，不能用历史数据代替现场读取。导出当前可恢复 ROM 和绑定/Bundle 数据，核对已有备份可用；不清空 `/resource/codex-status`，不轮换凭据或重新配对。
2. **禁止在运行槽 1 时直接 begin/upload。** 现有 `/api/firmware/begin` 自动选 `running_slot ^ 1`，此时会覆盖保留的槽 0。0031 所在槽永远不作为写入目标，也不向它部署 App。
3. 若现场确认为上述布局，路线是先通过已核验的切槽入口选择已有 0031 槽 0 并重启（仅切启动选择，不改其 ROM），确认救援正常且具备可用的 0041 镜像升级通道，再把候选写入非活动槽 1。**旧 0031 的实际升级通道当前没有现场证据；若无法确认，停在原状态，不刷、不改 0031、不猜接口。** 仓库 `upload-ota-0031.py` 只接受特定 0031 镜像格式，不适用于本 0041 候选，不能强行绕过校验。
4. 对现场确认支持现有分块协议的运行固件：读取 `/api/firmware/status` 和 `/api/firmware/slots`；保存唯一 request_id 与 revision；`begin` 提供 device_mac/request_id/expected_revision/length/recovery_crc；按回执 offset 和 max_chunk_bytes 上传 `chunk`；完整校验后 `commit`，确认目标槽是非 0031 槽及 committed，再对同一 request_id `reboot`。CRC 使用 ROM 恢复尾部校验字段，不能用 SHA 或任意整包 CRC 替代。响应丢失只查询原事务，不换 ID 重传。此处是协议顺序，不表示未知 0031 已支持这些接口。
5. 平台首次启动先不安装 App：核对 build、运行槽、0031 未变、原厂页面/旋钮/设备码菜单与维护 HTTP。观察启动稳定后再安装。平台 ROM 没有内置 App，但若已有 AUT3/app-store，会按持久集合加载；不能据 `applications:[]` 推断设备存储为空。发现已有集合则停止按首装包操作，保留日志后另行准备兼容清单。

当前没有把以上未知设备状态做成自动刷写脚本；尤其不能用“自动写非活动槽”替代 0031 保护。

## 二、安装唯一业务 App（待平台验证通过）

以下命令从 firmware 仓库根目录运行。先用现场 IP:18080、12 位 MAC 和菜单设备码文件设置变量，设备码/回执放私有目录，不入库。`RECEIPT` 指向尚不存在的私有文件；首次运行先保存 `status` 输出作为基线。

```sh
BUNDLE=build/hardware-validation-20261105
# 执行前设置 HOST、MAC、CODE_FILE、RECEIPT；本文不提供历史 IP 或凭据。
python3 -B tooling/scripts/app-set-client-v3.py \
  --host "$HOST" --mac "$MAC" --code-file "$CODE_FILE" --action status
python3 -B tooling/scripts/app-set-client-v3.py \
  --host "$HOST" --mac "$MAC" --code-file "$CODE_FILE" \
  --manifest "$BUNDLE/app/install.amf3" --package "$BUNDLE/app/codex_status.apx2" \
  --receipt "$RECEIPT"
```

只适用于当前空集合、版本 0、无待处理事务。客户端检查实际能力、空间与版本；不要绕过拒绝。install 会上传、提交并触发重启，不是仅暂存。成功必须为 `succeeded`，boot_id 已变化、实际运行列表仅 codex_status 且摘要匹配、全体 healthy、cleanup_pending=false；只有 HTTP 200 或重启不算成功。确认业务页面、旋钮、业务/发现线程、既有绑定与 Bundle 恢复。业务 Bundle 仍通过 codex_status 协议管理，不在这里重新发布。

超时/断线用原命令和**同一回执**恢复，或仅查询：

```sh
python3 -B tooling/scripts/app-set-client-v3.py \
  --host "$HOST" --mac "$MAC" --code-file "$CODE_FILE" \
  --action result --receipt "$RECEIPT"
```

result 返回码 0 仅说明查询成功，仍需检查事务与运行字段。

## 三、回退

- **尚未提交的安装**：用相同连接参数、`--action cancel --receipt "$RECEIPT"`，随后查询原事务。提交后的取消是否还能接受由设备阶段决定；不把 cancel 当作通用回退指令。
- **试运行失败**：AUT3 设计会重启退回旧集合；首装的旧集合是空集合。检查 `failed_rolled_back`、运行集合和维护可达性。真实 CPU/调度器整体卡死能否自行恢复尚未实测，不能保证软件监督一定触发重启；维护也不可达时转 ROM 救援流程，不循环重发安装。
- **安装已成功，主动停用 App**：这是一笔新的空集合更新，保留业务数据，以新私有回执执行以下命令。仅在当前集合版本为 1 时使用随包序号 2；更高版本必须另生成更高序号清单。完成后核对 succeeded、运行列表为空和维护正常。

```sh
python3 -B tooling/scripts/app-set-client-v3.py \
  --host "$HOST" --mac "$MAC" --code-file "$CODE_FILE" \
  --manifest "$BUNDLE/app/empty-recovery.amf3" --receipt "$RECOVERY_RECEIPT"
```

空集合提交后只在下次启动停用 App，不在线卸载。随后重新安装需以相同业务包生成序号 3 或高于当前值的新清单，不能重放序号 1。若是以后版本回退到旧业务包，也要以旧包组成**新序号**完整清单，并先核对数据 schema 兼容；不承诺恢复任意业务文件快照。

- **平台启动/维护失败**：使用操作前已确认可用的救援选择路径回到原 0031，保持其镜像不变；平台仍可响应时可用已核验的槽位 switch→reboot 协议，完全不可响应时依赖既有物理救援入口。若物理入口未核验，不开始刷机。0031 只是 ROM 救援，不会运行 APX2；恢复旧一体化 0041 ROM 是另一笔写槽 1 操作，应使用步骤一保存的精确镜像和单独授权，不能把原厂基线当成已部署业务 ROM。

所有回退均保留原事务回执、日志和业务文件，不手动删除 AUT3/app-store 来伪造成功。实机记录应填入实际槽位、镜像哈希、boot_id、事务结果、页面/线程/业务数据检查结果；目前这些项全部待测。
