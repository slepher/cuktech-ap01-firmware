# AP01 安全回退闭环试验（0031 fallback + ota_1 开发槽）

2026-10-17。目标：ota_0 = 永久固定 0031 fallback（认证 HTTP OTA）；ota_1 = 开发/实验槽。试验最小保护：ota_1 开发镜像**不启动 HTTP OTA**；开发槽基座在开机早期把下一次启动预切回 ota_0，健康运行约 10 s 后锁回 ota_1，使 ota_1 在 1–10 s 内崩溃/卡死时只需重新上电即可回到 ota_0。仅 QEMU + 合成 NOR + 宿主 loopback；不刷实机、不访问设备/串口/云端、不改 Bridge。归 backlog C9。

## Plan

1. 在 0031 基座上做“安全角色”模块（无 HTTP）：builtin 启动即调用原厂 `boardctl(0xff13)` 预切下一次启动到 ota_0；约 9 s 后再次调用以锁回 ota_1。
2. 用真实 OTA 流程把安全镜像装进 ota_1（由 ota_0 的 HTTP fallback 上传），得到 active=ota_1 的 NOR。
3. QEMU 观察窗：在预切后（约 4 guest s）与锁定后（约 19 guest s）分别快照 NOR，解析分区表按 age/active 的 Boot2 选择规则。
4. 预切快照上复启 ota_0 fallback，验证 HTTP 200/401/500（快速回退可用）；正常锁定快照上确认下一启动回到 ota_1。
5. 记录“开发镜像无 socket/listen 调用”作为不启动 HTTP 的直接证据；旋钮强制回退若无 Boot2 证据则列为未验证，不伪造。

## Task / Status

- [x] 安全模块原型 `firmware/ap01/ota_0031_safety.c` + `tools/ap01/build-safety-0031.sh`（无写静态段；栈：`switch_boot` 32 B、`ota_0031_main` 16 B）
- [x] 安全开发镜像 `ota-safety-dev2-0031.bin`（6,804,520 B，sha `2333e9f6…`，build_id `c2065eb5…`；与 fallback 共用 auth key；`flashable=false`）
- [x] 通过真实 OTA 把它装入 ota_1：`ota-safety-upload-162.json`（pass，快照 NOR 由 A→dev2 提交）
- [x] 预切验证：`ota-safety-window-164.json`（25 host s ≈ 3.9 guest s）——`native_ff13_calls` 1 次、payload 调用点 `0xa01f8758`、返回 0；分区表从 `E000 age1/active0, F000 age2/active1` 变为 **`E000 age3/active0, F000 age2/active1`**，即下次启动选择 ota_0
- [x] 预切后复启 fallback：`ota-safety-fallback-health-166.json` 使用同一 NOR（164 快照）、slot0、A 镜像——HTTP 200/401/500 通过，恢复通道可用
- [x] 开发镜像无 HTTP：安全窗口运行 `provider_calls={}`（guest 未发起 socket/bind/listen 等调用），模块本身不含 HTTP 代码
- [x] **锁回 ota_1 成立（模块 v4）**：`ota-safety-lock-168.json`（110 host s）→ 表 `E000 age4/active1, F000 age2/active1`；E000 为最新表且 active=1 指向 Addr1=`0x7b0000`（ota_1）。实现：ff13 预切后 9 s，直接重写同一张 E000 表（active=1、age+1），CRC 用 RAM 原生 `0x62fc168e`、表存储用 `0x62fc1c5e`+`0x62fc159e(0xe000,0x62fc8cd8,596)`。
- [x] 两态复启对照：崩溃窗 `ota-safety-crashwindow-169.json`（25 host s）→ `E000 age3/active0`，同 NOR 复启 fallback A 的 `ota-safety-crashfallback-health-170.json` HTTP 200/401/500 通过；锁定窗 168 的同 NOR 复启 dev3 `ota-safety-locked-boot-171.json` 正常进入系统、无 guest 异常（boot 时重新预切属预期）。
- [ ] 旋钮强制回退（无 Boot2 证据，未验证）

## ff13 内部机制（0031 反编译，2026-10-17 补充）

- boardctl 0xff13（0031 0xa005576c）在 param_2==NULL 时读取 ro.boot.update_slot 属性作为目标槽标识，然后循环两次（seq 0/1）用 custom0.rd() 的返回值 strcmp 比较；匹配后从 RAM 全局（0x62fc8cd4 表 / 0x62fc8ce8 FW 条目区）复制 36 字节条目到栈缓冲、打印 Set boot image=%s seq=%d ret=%d，再调用后续（被 Ghidra no_return 误判截断的）写表/CRC 代码，返回 2。
- 该属性由 Boot2 在启动时写入、镜像内三处只有 getprop 读取（0xa0056e84、0xa0059174、0xa0063f3e），运行期不可改。因此运行时 active 槽不变时，重复 ff13 会持续写同一张 E000 表（实测 age1→3→4、active 恒 0），无法锁回 F000。
- 结论：锁回 ota_1 必须直接写另一张表（F000，active=1，age+1，重算表头/条目 CRC）或以 0031 内部表写入器为目标；下一步反汇编 0xa0056f50..0xa00570bb（ff13 复制后的写路径）与 CRC/表写函数，确认能否从模块以参数指定“目标表 + active”。

## ff13 写表路径（0031 反汇编 0xa0056f40..0xa00570c0，2026-10-17 补充）

- ff13 在栈上复制 36 字节 FW 条目后：`sh count+1 → s3+10`、`sw age+1 → s3+12`、`sw crc(header 12B) → s3+16`、`sw crc(entries count*36B) → entries_base+count*36+20`。
- 写表调用经由 RAM 副本函数指针：CRC = `0x62fc168e(buf,len)`；表写 = `0x62fc159e(target, buf, 596)`，其中 target 取自 `s11`，由 RAM 表区首字节 `0x62fc8cd4` 决定：非 0 → 0xE000，为 0 → 0xF000。
- 这解释了实测：首字节非 0（表 magic 存在）→ 每次 ff13 都写 0xE000；重复调用只推进 E000 age，无法锁回 F000。
- 下一步候选实现：(a) 直接调用 RAM 表写函数 `0x62fc159e(0xf000, buffer, 596)` 写一张自建 F000 表（active=1、age+1、头部/条目 CRC 用 `0x62fc168e` 计算）；(b) 反查这两个 RAM 函数在 flash 的原始地址与参数契约，避免依赖 RAM 布局。两者都需 QEMU 实测校验 CRC 与 Boot2 选择。

## 结果（round 3：锁回成立，最小闭环跑通）

- 模块 v4（[ota_0031_safety.c](D:/Documents/PlatformIO/Projects/codex_status/firmware/ap01/ota_0031_safety.c)，sha `3ea64c29…`）：开机 ff13 预切 E000→active0；9 s 后直接重写 E000 表为 active=1、age+1。RAM 表缓冲在 `0x62fc8cd8`（magic `0x54504642`），复用 RAM 原生 CRC/写入叶。
- 开发镜像 `ota-safety-dev3-0031.bin`（sha `b9cc6ed9…`，build_id `eaf63e0c…`，`flashable=false`），经 fallback HTTP 真实装载 ota_1：`ota-safety-upload-167.json`。
- 崩溃窗：169 → `E000 age3/active0`（下次选 ota_0）；同 NOR 复启 fallback 170 HTTP 200/401/500 通过。
- 锁定窗：168 → `E000 age4/active1`（下次选 ota_1）；同 NOR 复启 dev3 171 正常进入系统。
- 安全窗口的 `provider_calls` 均为 `{}`（168/169/171），即开发镜像没有任何 socket 调用、不启动 HTTP；fallback 窗口 170 的 socket 计数正常（socket/bind/listen/poll/accept/recv/sendto/close）。
- 边界：RAM 叶地址是该固件运行时副本（依赖版本）；只验证了单次启动策略；旋钮强制回退无 Boot2 证据，未验证；未证明物理掉电时序、Boot2 行为、真实 Wi-Fi/USB 恢复。

## boot 阶段的分区表校验（0031 0xa0058f2a / 0xa00575ec，2026-10-17 补充）

- 该函数由 bootctl 0xff01 在 0xa00559ce 调用（早期启动、挂载 procfs/tmpfs 同一阶段），读 0xe000/0xf000 各 0x254 字节。
- 每张表用 0xa00575ec 校验：magic==0x54504642；count(u16@+6)<0x11；头部 CRC（前 12B）== u32@+12；条目 CRC（count*36B @+16）== 条目区后的 u32。失败分别报 PT_CRC_Error / PT_Entry_CRC_Error / PT_Entry_Count_Error，该表判为无效。
- 选择规则：两张都有效时比较表头 age（+8）取较大者；仅一张有效用该张；两张都无效则 boot2_init_fail 返回 -1。
- 选中表复制到 RAM 0x62fc8cd8 后再查 magic，按名字查找 “FW” 条目（entry+3、stride 36）；找不到返回 -2（BL616_partition_entry_cnt_error）。
- 读取选中分区 +0xfc 的 4 字节，写入属性 ap01.boot_header_crc；注册 fw1/fw2/ota/reserve/crash/resource 分区并挂载 littlefs；若选中分区起始不在 {0x10000,0x7b0000} 或长度不是 0x700000 则 panic（chip_bl616_partition.c:0x325）。
- 对安全回退实现的影响：boot 校验不比较“条目 age 与表头 age 是否一致”，选择只看表头 age；但要求两张表各自 CRC 合法、存在名为 FW 的条目、分区几何正确。我们的 E000 重写保留 magic/count/name 并重算两段 CRC，满足这些校验；条目 age 同步仍建议补上（stock commit 会同时递增）。

## Review

- 预切机制已成立：0031 原厂 `0xff13` 单独调用（不打开/写入镜像）即可把非活动表 active 指向 ota_0 并推进 age，因此“1 s 预切 + 掉电回 ota_0”的恢复路径可由该原语实现。
- 锁回需要直接写另一张表（F000，active=1）或以运行槽为目标提交；单纯重复 boardctl 0xff13 会重复写 E000。下一步分析 0031 `0xff13` 内部表写入器（`0xa00571ac` 类比）及其 active 索引来源，优先找到可从模块调用、可指定目标表/active 的内部叶子。
- 若锁回不可行，退路：预切只写一次并依赖“崩溃后回 ota_0，再由 fallback 的 HTTP OTA 重新发布 dev 到 ota_1”——即用户所说“不需要强制保护，能快速恢复即可”的最低版本；需明确代价（每次掉电回 fallback，需重新发布 dev）。
- 边界：全部为 QEMU 合成模型；未证明物理 Boot2、旋钮、掉电时序、真实 Wi-Fi/USB 恢复。
