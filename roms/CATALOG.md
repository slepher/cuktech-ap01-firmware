# ROM 清单（0031 / 0041）

CUKTECH AP01 屏幕控制器，固件标识 `1.0.2_0031` 与 `1.0.2_0041`。
`0031` 是设备当前的用户报告版本；`0041` 是官方可升级版本。两者均为**米家 miIO.ota 应用更新容器**，
不是 16 MiB 整片 Flash 备份，分析中的 VA/文件偏移不等于实机烧录地址。

本目录只放可直接复现实验的镜像；每条记录都写明它是原件、基线还是我方构建的模拟候选。

Git 已收录原厂 `0031/ap01-1.0.2_0031.bin` 和 `0041/ap01-1.0.2_0041.bin`，检出即可作为对应版本的 ROM 打包输入。
其余镜像和下载元数据仍仅保留在本地归档；重编应用仍需另行准备 RISC-V 工具链和 ArduinoJson。

## 原件（官方、未修改）

| 文件 | 版本 | 字节 | SHA256 |
|---|---|---|---|
| `0031/ap01-1.0.2_0031.bin` | 1.0.2_0031 | 6,804,520 | `8a721fc8ef25458d415b2460e4a251e0503a82f7743fdff85b12612190e5c1cb` |
| `0041/ap01-1.0.2_0041.bin` | 1.0.2_0041 | 6,769,704 | `972db4c136c7ed9e24a83c07c1a7fd62040ca018b08ca285216d26b1fee3c6b9` |

- `0041/ap01-1.0.2_0041.json`：官方下载元数据，746 B，SHA256 `6c9c4cf3d1ebc568f7af778645446c0f69e83611fe5c599ddf5808dcb347849c`。
- `0031` 原件来源：同父目录 `cuktech-ap01-firmware-tools/artifacts/firmware/original/`（上游只读克隆），为逐字节副本，哈希与上文一致。
- `0041` 原件来源：本项目的下载专项（2026-10-13），MD5 `3c2d962be82c73860daff903178d9b9e` 与 SHA256 均已在前序文档核验。
- 0041 原件含小米签名链校验；0031 原件的签名/校验路径见 `reverse/reports/ap01/knowledge/0041签名与Bridge接口分析.md` 与 `0031分区与启动入口复查.md`。

## 我方候选

**历史构建清单保留 `flashable=false`。** 每个候选都由 `tooling/` 下的脚本在冻结的原件基线上重新构建并重建清单。2026-10-18 用户明确授权后，0031 A 候选完成一次实机首次安装及认证健康检查，见 [实机安装记录](../reverse/reports/ap01/first-install-0031-20261018.md)。其余候选仍仅有离线证据；模拟通过不等于实机验收，首次安装通过也不证明掉电恢复或独立通道实际更新已验。

### 0031

| 文件 | 字节 | SHA256 | 说明 |
|---|---|---|---|
| `candidates/ap01-1.0.2_0031-app-xip.bin` | 6,804,520 | `6f3394f64050780ee756397496bad8e2f0b14e6efe171745daeac721b85fed01` | 最小同步 XIP 诊断 App（第一版） |
| `candidates/ap01-1.0.2_0031-app-xip-candidate2.bin` | 6,804,520 | `61af60e00475f24f4460e60734d7b93a67fb05bb5b756077ccf9d81d4ba7f849` | 最终 0031 最小 XIP App 候选（2026-10-13 验收） |
| `candidates/ota-channel-a-0031.bin` | 6,804,520 | `cca6a2431ee24b7260334a08c2e24ce9f8cccddebd24f8f91e8ea393cce928d2` | 0031 独立 HTTP OTA 方案 B，A 槽 |
| `candidates/ota-channel-b-0031.bin` | 6,804,520 | `c0b1461654fbe16d2d563d4796c1f8ad756489e3cf8adeb97b8a052677cfea34` | 0031 方案 B，B 槽 |
| `candidates/ota-channel-b2-0031.bin` | 6,804,520 | `c909ae30256402ac113c3311663bad8244495dc3f3c0dbd665e133c3134b6024` | 0031 方案 B，B2 变体 |
| `candidates/ota-safety-dev-0031-v1.bin` | 6,804,520 | `0f206db307c862b62733a1701dece079fd03d7255fa8f9bd540aa4b83e480258` | 崩溃窗口/回退安全试验 dev1 |
| `candidates/ota-safety-dev2-0031.bin` | 6,804,520 | `2333e9f6facf10176c57b46632417ff605a6b15e6a3a668dd2fba5b8d9a9a6fb` | 同上，dev2 |
| `candidates/ota-safety-dev3-0031.bin` | 6,804,520 | `b9cc6ed94e9fb1d3ba3b6ad29849a141db4dd5bf25b21dbbecf6acb480288c49` | 同上，dev3 |

说明：`ota-channel-a/b/b2` 证明「A 装 B → 同一 NOR 虚拟复启 → B 回刷 A → 通道仍可用」；
`safety-dev*` 用于崩溃窗口/锁定槽位的负向试验。0031 的 OTA 闭环报告在
`evidence/qemu/0031-20261017/` 与 `reverse/reports/ap01/qemu-ota-0031-20261017.md`。

### 0041

| 文件 | 字节 | SHA256 | 说明 |
|---|---|---|---|
| `candidates/ap01-1.0.2_0041-unsigned-ota.bin` | 6,769,704 | `1bbe8f45359eb7cdb55f337643f3ce28894999ffb21beab92fb62e995cd4854d` | 撤销 0041 新增 unsigned OTA 拒绝的冻结基线 |
| `candidates/ota-channel-a-004.bin` | 6,769,704 | `8570f4cd0ffe631802be16da3b11d27683fcfe6d5c0c9b24f4e360d3dca539a6` | 0041 注入独立 OTA 模块，A |
| `candidates/ota-channel-b-005.bin` | 6,769,704 | `4f71fd731f45c9c45cc1d010e8d2326cbfdfd1bc136df8f8f6073f2dd03ed806` | 同上，B |

A/B 使用同一 v5 代码、不同 build_id，用于证明更新连续性，不代表新增业务。
完整闭环（A→B→同 NOR 复启→B→A→复启）与引擎/清单哈希见
`reverse/reports/ap01/qemu-ota-final-20261017.md`；运行证据在 `evidence/qemu/0041-20261017/`。

## 其它同名镜像的位置

`evidence/qemu/` 里保留了每个实验轮的完整输入/输出，因此还存在同内容或仅差 build id 的镜像
（如 `ota-channel-a-001..004`、`injection*.qemu-only.bin`、16 MiB NOR 快照）。本目录是**规范入口**；
`evidence/` 是过程材料，二者的同内容文件 SHA256 一致。全量清单见 `../checksums/SHA256SUMS.txt`。
