# cuktech-ap01-firmware

CUKTECH AP01 屏幕控制器 `1.0.2_0031` / `1.0.2_0041` 固件的**离线逆向与模拟验证资料库**。

当前实机状态（2026-10-18）：`192.168.3.191` 已通过独立 OTA 成功运行保留原版 GIF、原启动头、PEC 和传统 OTA 入口的 `ap01-http/tail2` 槽尾版。用户确认猫居中、显示/旋钮/米家正常；完整提交、复位、实际 FW1 启动和读回证据见[槽尾版实机成功记录](reverse/reports/ap01/knowledge/0031-tail-physical-success-20261018.md)。此结论不自动适用于其他历史候选。

本目录是 2026-10-18 从 `D:\Documents\PlatformIO\Projects\codex_status` 提取的独立快照：
原 `artifacts/ap01-research/`（4.78 GB）的全部内容、`project-workflow/ap01/` 的报告、
`tools/ap01/` 的 QEMU 重宿主模型与构建脚本、`firmware/ap01/` 的注入模块源码。
原仓库中的对应内容**未删除**，因此当前两份并存；确认新项目可用后可回收原目录。

> 说明：`reverse/reports/` 是原 `project-workflow/ap01/` 的**原样快照**，正文里的相对链接
> （如 `../../tools/ap01`、`../single-copy-updates/design.md`）仍按 `codex_status` 的目录结构书写，
> 在独立项目中会指向不存在的位置。原仓库内的路径映射见
> `codex_status/artifacts/ap01-research/README-extracted-20261018.md`。

> 不是原厂固件工程：没有原厂源码、没有整片 Flash 备份。
> 2026-10-18 已通过原版米家 OTA 首次安装 0031 OTA A 候选，实机独立更新服务认证健康检查通过，见 [实机安装记录](reverse/reports/ap01/first-install-0031-20261018.md)。历史构建清单的 `flashable=false` 保留原值；其余候选仍仅有离线证据。Ghidra 伪代码不是可编译源码。

## 目录

| 目录 | 内容 | 文件数 | 大小 |
|---|---|---|---|
| `roms/` | 0031/0041 原件 + 我方候选 + 清单（[CATALOG](roms/CATALOG.md)） | 15 | 84 MB |
| `reverse/reports/` | 逆向报告、知识文档、交接与平台分析（`project-workflow/ap01` 快照） | 61 | 0.6 MB |
| `reverse/analysis/` | 反汇编/对比表/资源映射/硬件模型/REA 结构导出 | 68 | 24.5 MB |
| `reverse/rehost/` | 0041 应用层在 NuttX+LVGL 上的重宿主构建与 462 张界面截图 | 580 | 213.7 MB |
| `reverse/app-0031/` | 0031 最小 XIP App 的构建产物、依赖与模拟报告 | 145 | 74.6 MB |
| `reverse/raw/` `sdk/` `nuttx-sim/` `migration/` | 原始探针、Bouffalo SDK 摘录、NuttX SIM、迁移清单 | 48 | 12.7 MB |
| `tooling/scripts/` | QEMU AP01 模型、ROM 构建/校验、REA 反编译辅助脚本 | 100 | 1.3 MB |
| `tooling/firmware-modules/` | `ota_channel.c/.h`、`ota_0031`、`ota_0041`、App 加载器、维护事务源码 | 23 | 0.2 MB |
| `evidence/qemu/` | 0041（1466 文件）与 0031（209 文件）的每次运行报告、16 MiB NOR 快照、日志 | 1675 | 944.5 MB |
| `evidence/rea-0041-20261017/` | 私有 REA 6.5.0 + Ghidra 12.1.4 分析会话（Evidence 导出 + profile 胶水 + Ghidra 安装副本） | 8540 | 3429.9 MB |
| `evidence/ghidra-project-0041/` | Ghidra 项目数据库 `ap01-0041.gpr/.rep` | 13 | 76.8 MB |
| `checksums/` | 全树 SHA256 清单（`sha256sum -c` 兼容） | 1 | — |

`evidence/rea-0041-20261017/rea/node_modules` 是指向同父目录 `../rea/node_modules` 的**目录联结**，
不计入本项目体积（约 546 MB 复用现有 REA 依赖）；搬动本项目后需重建该联结。

## 版本与关键哈希

| 对象 | 字节 | SHA256 |
|---|---|---|
| 0031 原件 | 6,804,520 | `8a721fc8ef25458d415b2460e4a251e0503a82f7743fdff85b12612190e5c1cb` |
| 0041 原件 | 6,769,704 | `972db4c136c7ed9e24a83c07c1a7fd62040ca018b08ca285216d26b1fee3c6b9` |
| 0031 最终 XIP App 候选 | 6,804,520 | `61af60e00475f24f4460e60734d7b93a67fb05bb5b756077ccf9d81d4ba7f849` |
| 0041 unsigned 基线 | 6,769,704 | `1bbe8f45359eb7cdb55f337643f3ce28894999ffb21beab92fb62e995cd4854d` |
| 0041 OTA A (`ota-channel-a-004.bin`) | 6,769,704 | `8570f4cd0ffe631802be16da3b11d27683fcfe6d5c0c9b24f4e360d3dca539a6` |
| 0041 OTA B (`ota-channel-b-005.bin`) | 6,769,704 | `4f71fd731f45c9c45cc1d010e8d2326cbfdfd1bc136df8f8f6073f2dd03ed806` |

全部镜像见 [roms/CATALOG.md](roms/CATALOG.md)。ROM 身份以字节数和 SHA256 双重核对，不靠文件名或时间戳。
QEMU 10.1.0 引擎 SHA256 `7246b77aa123e3b785d8c1093b4ee2bac19a3fb1b489bc0d1035963d87e18b9d`（位于 WSL，不在本目录）。

## 用 REA 续做

`evidence/rea-0041-20261017/` 是一个冻结的私有分析环境，对应 0041 原件的完整逆向主力工作：

- **语言**：`RISCV:LE:32:ap01thead2`（v2，含 REV/WEXTI/ADD64/MINW 等厂商指令），v1 为 `ap01thead`。
- **Evidence**：`evidence/` 下 1216 个 `*.evidence.json`（约 2.54 GB）。最大的是 `upper-complete.evidence.json`（170.8 MB）；
  `final-0041.evidence.json` 是 276 函数 / 168,348,248 B 的整包导出（SHA256 `80c93186…`）。
  这些是 REA 的规范导出，**路径无关**，可直接 `import_evidence_bundle` 载入后 `inspect_analysis_view` 续读。
- **Ghidra 项目**：`evidence/ghidra-project-0041/ap01-0041.gpr` 可用 Ghidra 12.1.4 直接打开。
- **自定义处理器**：`evidence/rea-0041-20261017/processor/data/languages/` 下的
  `ap01thead{,2}.{ldefs,sinc,reg.sinc,sla,slaspec}`；构建脚本为 `scripts/build_ap01_processor*.py`。
- **修复脚本**：`scripts/Ap01NoReturnRepair.java`（no-return 清除与调用点重建）、`Ap01ProcessorCheck*.java`。
- **profile**：`profile.json` 记录语言、原件 SHA、57 个模型输入指纹与修复报告；最终 digest
  `04b34bbb41e8ff5d0cbbc2c7471d390693c40fe70f2e21519e2b21d268c9237d`，上层续作 profile
  `4825fb58a33a3e7d618557975b153b8318cf7e833d190ad16bcbf8bd441ae621`。

⚠️ 迁移注意：`profile.json`、`evidence/manifest-final.json` 等文件里的**绝对路径仍指向原
`codex_status/artifacts/ap01-research/`**。因此：

1. 只读复用 Evidence → 直接导入即可，不受影响；
2. 要重新跑私有 MCP 会话 → 必须先在新根重新执行
   `scripts/freeze_private_profile.py --round2 --late-callbacks` 生成绑定新路径的 profile
   （digest 会变，旧 Evidence 内的旧 digest 文本**不得改写**，两类证据按各自 profile 记账）。

复现入口与验收门槛见 `reverse/reports/ap01/private-profile-0041-20261017.md` 与 `0041-handoff.md`。

## 复现

- **QEMU 模拟**：`python tooling/scripts/run-qemu-ota-channel.py --qemu <WSL qemu-system-riscv32> --image … --manifest … --flash-fixture … --rom-shim … --profile … --output …`；
  每次安装后必须用 `verify-qemu-ota-boot.py` 独立核对 NOR 表/CRC/保护区，再用**同一快照 NOR** 虚拟复启。
- **构建**：`tooling/firmware-modules/README.md` 与 `tooling/scripts/build-ota-channel-{0031,0041}.sh`；
  交叉工具链与 Bouffalo SDK 在同父目录只读复用，不在本目录。
- **NuttX SIM / 重宿主**：见 `reverse/reports/ap01/nuttx-sim-20261016.md`、`application-rehost-*.md`。

## 空间占用（四种口径）

单位为资源管理器口径（1 MB = 1024² B）；按 10⁶ 计需 ×1.048（全量约 5.10 GB）。

| 口径 | 组成 | 大小 |
|---|---|---|
| T0 纯成果 | 两个原件 13 + 报告 0.6 + 全量反汇编/分析 24.5 + 原始探针/SDK 摘录 3.3 + 工具脚本 1.4 | **43 MB** |
| T0+ 全候选 | T0 + 11 个候选镜像（0031 八个、0041 三个，各约 6.5 MB） | **114 MB** |
| A 可离线重建 | T0+ + 再托管构建 214 + 0031 XIP 构建（含 deps）75 + NuttX SIM 9（不含 REA 会话与 QEMU 运行证据） | **412 MB** |
| B + REA 中间产物 | A + Evidence 2,536 + profile 胶水 29 + Ghidra 项目 77 | **3,054 MB** |
| C + 私有 Ghidra 环境 | B + 完整 Ghidra 12.1.4 安装副本 865（可删、可重装） | **3,918 MB** |
| D 全量 | C + QEMU/0031/0041 运行证据 944 | **4,863 MB**（11,270 文件，4.75 GiB） |

**ROM 本身只有 13 MB。** A 与 T0 的 370 MB 差额全是「可重建但需要项目外工具链」的产物：
`reverse/rehost/` 214（ROM 资源转成的 4 份 C 头文件 51、ELF 47、tgz 26、462 张截图 25、JSON 53）、
`reverse/app-0031/` 75（其中依赖库 57，`unicorn.lib` 单文件 48）、`reverse/nuttx-sim/` 9。
保留它们的唯一理由是外部环境（WSL QEMU 引擎、交叉工具链、Bouffalo SDK、REA 依赖）变化后仍能离线复现。

即：**REA 可续用中间产物比 T0 多占约 2.7 GB；若连 Ghidra 运行环境一起打包，多占约 3.6 GB。**

QEMU 运行证据里有大量同内容大文件（16 MiB NOR 快照、重复镜像），实测可去重约 352 MB；
去重后全量约 4.51 GB。`evidence/qemu/` 内 16 MiB NOR 与 6.5 MB 候选镜像也重复出现在 `roms/` 的规范副本中。

## 边界与未完成

- 2026-10-18 首次实机安装 0031 OTA A 候选通过：原厂米家 OTA 下载、重启、原厂米家重新在线，以及独立 18080 正确密钥 200 / 错误密钥 401。已复用本地加密账号缓存，未输出凭据。屏幕/旋钮、长时间稳定性及独立通道实际更新仍待验。
- 0041 只在「必要 Mock」下证明了 HTTP OTA 安装 → 原厂 NOR 写入/CRC/提交 → 同 NOR 虚拟复启 → 通道连续可用；
  0041 尚未验证物理 Wi-Fi、真实 Boot2 回滚、掉电恢复、永久底座。0031 已完成一次实机首次安装和独立通道健康检查，实机回滚、掉电恢复和永久底座仍未验。
- 网络是 `payload` 范围内的宿主 loopback provider，没有空口 Wi-Fi/关联；LCD 只到开机 Logo，完整主界面未验。
- 原厂 MiIO/MiBLE 私有实现只恢复了合同与调用图，**没有可编译的完整源码**；伪代码数量不等于源码完整度。
- 0041 新增的 unsigned OTA 拒绝只被离线撤销，绕过未在实机证实。

## 许可、隐私与来源

- 原厂 ROM、字库、图片资源版权归 CUKTECH / 小米生态链所有；本目录是个人研究存档，不分发、不商用。
- 上游工具 `cuktech-ap01-firmware-tools`（commit `3bd98a8ca4fb35a9f8869121b13961d405b16dff`，MIT）与
  `cuktech-screen-controller` 的作者归属与许可说明见 `reverse/reports/cuktech-ap01-repository-value-analysis.md`。
- `evidence/private/xiaomi-account.dpapi` 是本地 DPAPI 加密的账号缓存；`evidence/qemu/` 内的 `*.auth-key`
  是模拟通道的测试密钥。**二者都不要提交到 Git、不要外发。** 本目录未初始化 Git；若初始化，请先排除 `evidence/`。

