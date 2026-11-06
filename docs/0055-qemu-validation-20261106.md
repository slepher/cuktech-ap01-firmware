# 0055：WSL 工具链修复与 QEMU 执行验证

2026-11-06。用户要求解释 GCC 8 限制、在 QEMU 先验证，并指定确认本机现有 WSL。本轮复用本机 Ubuntu-24.04 的 AP01 QEMU，没有连接设备或写入 Flash。

## GCC 8 与 0041 的关系

限制来自 Windows PlatformIO GCC 8.4.0 所带的预编译 `libm.a`，不依赖原厂 ROM 是 0041 还是 0055。该库引入 44 个绝对 HI20 和 84 个 LO12_I 指令重定位。固定地址的 ROM 模块可以在最终链接时解析这些地址；独立 App 必须在搬移后仍可执行，不能把这类指令直接当作数据 BASE32 修正。构建器正确拒绝了这个包，没有放宽白名单或生成待部署包。

此前 0041 的成功记录使用官方 xPack GCC 12.5.0-1；见 [原工具链记录](../project-workflow/ap01-app-update/s1-build.md)。换机器本身不是解决条件，复用兼容的编译器和数学库才是。本轮在同一台机器的 WSL 用同版本 Linux x64 工具链实测解决，没有修改业务源码或 App 格式。

- 官方发布：[xPack GCC 12.5.0-1](https://github.com/xpack-dev-tools/riscv-none-elf-gcc-xpack/releases/tag/v12.5.0-1)。Linux x64 归档 344,722,823 B，SHA256 `624fae17fb5dfaa0d8a9f8b345c9831cca9e06322a34254342a19eea61915e82`，与官方 release API 的 asset digest 一致。
- 归档及发布元数据保存在 `build/qemu-0055-20261106/toolchains/`。解包到本任务独立 WSL 临时目录，实际路径记录在 `wsl-toolchain-path.txt`；不修改系统 PATH、包管理器或已有工具链。临时目录被系统清理后可从已校验归档重解。
- WSL Python 复用工作区内的纯 Python pyelftools 副本，没有在 WSL 宿主安装依赖。Windows 挂载目录解包缓慢的一次尝试已停止，部分输出保留；实际使用的是 WSL 临时目录中的完整工具链。

当前仓库真实业务 App 为 `codex_status 0.18.108-ap01`，这不是对设备当前已部署版本的查询。构建得到 205,360 B APX2，SHA256 `a1aef9e51d0517739ed4089210097d17b3391a3597e4c7268e2feb1d708684ec`，image/BSS 为 204,528/8 B，72 条 BASE32，零未解析导入，两个链接基址归一映像完全相同。两个独立完整构建另核对包逐字节一致，见最终 `release.json`。本机 GCC 8 的失败和 WSL GCC 12 的成功对照保存在 `build/qemu-0055-20261106/toolchain-comparison.json`。

## 已有 WSL 模拟器

发行版 Ubuntu-24.04，现有模拟器 `/home/slepher/qemu-ap01-boot-safety-20261019/build/qemu-system-riscv32`，QEMU 10.1.0 dirty，SHA256 `b46de0508e0f4be6c4ef5ded168360c7bf4bc5e23bf43e44e9f244a79d33b0ce`。复用相邻逆向仓库 `tooling/scripts/run-qemu-ap01.py` 的有界 GDB 传输，SHA256 `b999b2ae80b0926ed5a8cff0328a6fb27f3bab48ca1a39257a9796a8cd4f5eec`。没有重编或修改既有模拟器。

本机另有 `/home/slepher/qemu-ap01-0041/build/qemu-system-riscv32`，本轮未用作验收引擎。历史 james.local 主机名当前无法解析；本轮按用户新指示使用已有 WSL 环境，历史远端记录没有被视为本轮通过证据。

## 执行结果

| 检查 | 结果 | 证据 |
| --- | --- | --- |
| 既有 AP01 模型合成基线 | 55 项通过 | `build/qemu-0055-20261106/baseline/model-baseline.json` |
| 原厂 0055 实际指令 | 10 项通过 | `build/qemu-0055-20261106/native-canonical/original.json` |
| 最终基版实际指令与跳板 | 19 项通过 | `build/0055-qemu-verified-20261106/qemu-native/base.json` |
| 最终应用版实际指令与跳板 | 19 项通过 | `build/0055-qemu-verified-20261106/qemu-native/app.json` |
| 真实业务 App，0055 单 App 模型平台 | 两基址返回 0，SP/保存寄存器保持 | `single-0055-run01.json` |
| 真实业务 App + peer，0055 集合 | 两基址返回 0，SP/保存寄存器保持 | `collection-0055-run02.json` |
| 同一业务包、peer 和 Manifest，0041 集合回归 | 两基址返回 0，SP/保存寄存器保持 | `collection-0041-run01.json` |

最后三份报告位于 `build/qemu-0055-20261106/app-executionreports/`，运行基址为 `0xa8000000` 和 `0xa8040000`。

原厂指令检查覆盖 TLS、线程 errno/全局兜底、socket 非阻塞标记、空 accept backlog 和目录回调。候选检查还执行编译后的 TCP/UDP 监听参数、ROM UI 入口跳转及注册 fallback、四个菜单跳板的续执行指令，以及 NULL 定时器保护和原序言续接。对应可复现脚本已保存为 `tooling/scripts/test-native-0055-qemu.py`，调用者必须固定 ROM、ELF 和模拟器 SHA。

业务模型执行真实生产 APX2 校验/加载/修正、真实 App start/event/health、worker、UI 删除与重新绑定；集合模式还执行生产 `native_exec_memory_v3` reserve/publish、缓存发布指令、AMF3/AUT3 选择、健康监督、写门和已有业务 HTTP 断言。0055 模型与生产宿主统一采用 11 个原厂页；App 包、AMF3、AUT3、ABI 3/平台 3.1 均保持原合同。

保留两类首轮失败，均未放宽产品检查：

1. 实际原厂 memset 使用 `th_mula`，初次 CPU 配置没有启用 QEMU 已支持的 `xtheadmac`。显式启用对应扩展后目录检查通过，未修改 ROM 或模拟器源码。原厂指令套件的完整 CPU 参数记录在 JSON。
2. 集合 guest 测试将 peer 物理页写死为旧值 17。精确预期改为 `AP01_STOCK_SCREEN_COUNT + 8`；0055 检查 19，0041 回归仍检查 17。首轮 `collection-0055-run01.json` 及日志保留。测试头变更后重新生成最终 ROM、刷新源码审计，并按新 SHA 重跑候选指令检查。

## 最终产物

### 2026-11-07：原厂 OTA 新增门禁的确认

按用户要求，单独核对从 0041 起新增的未签名 OTA 拒绝检查。0055 原厂在文件 `0x6cd60` / VA `0xa006bd60` 为 `dde7`（依据 signed_file 条件跳转），基版和应用版均已替换成 `7da0`（无条件跳到 `0xa006be0e`），与 0041 的既有放行机制一致。

生产 QEMU 检查脚本增加原厂/改版对照：两份改版在 `signed_file=0` 时均继续，且标志保持 0；后续 `0xa006fce6` 的选择分支因此跳过签名验证。`signed_file=1` 仍选择原有签名验证路径，没有移除其余证书、CRC 或镜像完整性检查。准确行为是允许未签名 OTA，并跳过该类镜像的签名验证。

本轮原厂 14 项、基版 23 项、应用版 23 项全部通过。报告在 `build/0055-unsigned-ota-confirmation-20261107/`，输入 ROM SHA 与下表一致；只执行相关原厂指令/跳板，未调用实机 OTA。候选字节无需再修改。

| 文件 | 字节 | SHA256 |
| --- | --- | --- |
| `build/0055-qemu-verified-20261106/ap01-0055-base.bin` | 6,881,304 | `f72f429ab0cdf7706e584af24c6c8a9ecea036a35c9d0889ddf0062269033209` |
| `build/0055-qemu-verified-20261106/ap01-0055-app.bin` | 6,932,616 | `972650864f49f5f62b8ba1128fdb5b6d6d5dadd789b11971518d8fecdb612752` |

最终目录另有 ELF、审计、链接映射、`release.json` 和 `SHA256SUMS`。基版 `supports_app=false`，应用版 `supports_app=true`。生产包/ABI 合同文件与迁移前 HEAD 原文一致；最终候选重新通过镜像重建和未声明字节不修改检查。

## 复现真实集合执行

以下在当前 WSL 的固件仓库根目录执行，输出文件必须不存在；fixture、模拟器和传输脚本均为本轮已保存的输入。运行这一步不需要重新编译或安装 Python 依赖。

```sh
mkdir -p build/qemu-recheck-0055
python3 -B tooling/scripts/test-app-abi-qemu-0041.py --direct-v3 \
  --qemu /home/slepher/qemu-ap01-boot-safety-20261019/build/qemu-system-riscv32 \
  --expected-engine-sha256 b46de0508e0f4be6c4ef5ded168360c7bf4bc5e23bf43e44e9f244a79d33b0ce \
  --support-dir ../cuktech-ap01-firmware-reverse/tooling/scripts \
  --fixture-dir build/qemu-0055-20261106/guest-collection-0055-fixed \
  --output build/qemu-recheck-0055/collection.json
```

从源码重编 guest 时使用 `build-app-v3-guest-0041.py --target 0055`，传入本轮业务 APX2、`guest-collection-input/set.amf3` 和 `guest-peer/app.apx2`。工具链前缀是 `wsl-toolchain-path.txt` 中的目录加 `/bin/riscv-none-elf-`；构建 Python 的 `PYTHONPATH` 指向 `build/qemu-0055-20261106/python`。0055 编译选择与 11 页模型必须成对，不能把默认 0041 的 guest 作为新版布局验收。

## 覆盖边界

以上属于实际指令与业务 App 的 QEMU 执行证据。原厂指令检查对内核分配/锁、TCB 记录及重型 UI handler 使用明确替身；业务 guest 替代原厂维护监听、VFS/网络/LVGL、时钟和分配地址，采用模型协作线程。没有执行原厂调度器、完整 ROM 冷启动、真实 Wi-Fi、LCD 或 Flash 掉电恢复。

因此最终清单仍保留 `flashable=false`、`hardware_verified=false` 和广义 `simulator_verified=false`；专项 QEMU 报告记录本轮已通过的准确范围。完整原厂 ROM 启动与实机外设仍是未验收项，不能由上述局部和模型执行结果推定。
