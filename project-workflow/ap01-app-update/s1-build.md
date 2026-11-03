# S1：本机 0041 构建恢复与 PIE 初验

2026-11-02，arm64 macOS。无设备访问、切槽或部署；S1 实机准入尚未通过。

## 合并与本轮修改

按用户要求，当前 master 已快进合并完整远端更新至 `69015e7713394449ee40e7e6f1b17246516d82fe`，没有内容冲突。README 本地设计导航保留，docs/ 和 project-workflow/ 未被覆盖。

- `2b88cb6` 恢复 0041 统一构建、平台独立入口、SHA256、ArduinoJson 7.4.3 与验收脚本。
- `69015e7` 增加 0031 恢复底座设备码菜单、持久授权和限流。这是源码同步，0031 不参与 App 加载验证，也没有部署。
- 本轮新增的未提交修改：构建固定 `_USE_LONG_TIME_T`；calendar 编译断言要求 32 位时间 ABI；相邻 App `ports/ap01/native_0041.cpp` 显式包含 `time.h`；增加离线 PIE 清点脚本及本记录。

App HEAD 为 `7b5c5ab`，实际工作区源文件和头文件摘要以构建 audit 为准。本轮仅修改上述 App include，保留其余既有工作区改动。

## 固定工具链

采用官方 [xPack GCC 12.5.0-1](https://github.com/xpack-dev-tools/riscv-none-elf-gcc-xpack/releases/tag/v12.5.0-1) 的 darwin-arm64 包，编译器报告 GCC 12.5.0。下载文件 SHA256：

```text
47331601bd7c87cf6d0b7090f381b184773e8e55113106cacbc401f4b7c7cd99
```

已与官方 release asset digest 核对。归档与 release JSON 保存在 `build/s1/toolchains/`；解包位置为 `build/s1/toolchains/xpack-riscv-none-elf-gcc-12.5.0-1/`，未修改系统 PATH 或全局工具。

复现安装（目录不存在时先按本机规则预建；已有安装无需重复解包）：

```sh
curl -fL --retry 2 --connect-timeout 15 --max-time 600 \
  https://github.com/xpack-dev-tools/riscv-none-elf-gcc-xpack/releases/download/v12.5.0-1/xpack-riscv-none-elf-gcc-12.5.0-1-darwin-arm64.tar.gz \
  -o build/s1/toolchains/xpack-riscv-none-elf-gcc-12.5.0-1-darwin-arm64.tar.gz
shasum -a 256 build/s1/toolchains/xpack-riscv-none-elf-gcc-12.5.0-1-darwin-arm64.tar.gz
# 摘要与上方相同才解包。
tar xzf build/s1/toolchains/xpack-riscv-none-elf-gcc-12.5.0-1-darwin-arm64.tar.gz -C build/s1/toolchains
```

先尝试的 GCC 13.4.0 在 `-ffreestanding` 下不提供当前代码所依赖的完整 C++ stdlib 声明，未作为基线。GCC 12 的新 newlib 默认 `time_t` 是 64 位，导致既有 calendar 的 C++ 符号变为 `long long`；本轮固定 `_USE_LONG_TIME_T` 恢复既有 32 位 long 约定，而不是放宽打包器的 ABI 假设。已实测不带该宏编译 calendar 会被断言拒绝。

## 构建与验收命令

从固件仓库执行；输出文件须为新文件，目录按需预建。命令再次运行时更换 output 文件名，保持 build-dir 可以检验同路径重编确定性。

```sh
ap01_tool_prefix="$PWD/build/s1/toolchains/xpack-riscv-none-elf-gcc-12.5.0-1/bin/riscv-none-elf-"
python3 -B tooling/scripts/build-firmware-0041.py --tool-prefix "$ap01_tool_prefix" \
  --build-dir build/s1/platform/objects --output build/s1/platform/platform-abi32.bin
python3 -B tooling/scripts/test-firmware-0041.py --manifest build/s1/platform/platform-abi32.manifest.json
python3 -B tooling/scripts/build-firmware-0041.py --tool-prefix "$ap01_tool_prefix" \
  --app-config ../codex_status/ports/ap01/build-0041.json \
  --build-dir build/s1/app/objects --output build/s1/app/app.bin
python3 -B tooling/scripts/test-firmware-0041.py --manifest build/s1/app/app.manifest.json
python3 -B tooling/scripts/test-native-build-0041.py
python3 -B tooling/scripts/test-platform-independence-0041.py \
  --out build/s1/independence --tool-prefix "$ap01_tool_prefix"
python3 -B ../codex_status/tools/test-ap01-firmware-boundary.py
```

平台独立检查的 out 必须不存在；PIE 检查的 out 必须存在且为空。构建日志中的 App offsetof 与 ArduinoJson deprecated 警告仍存在，未作为本轮无关清理范围。

| 离线候选 | 字节数 | SHA256 |
| --- | ---: | --- |
| `build/s1/platform/platform-abi32.bin` | 6,879,560 | `bf810e766632cdc41f932dc324e4b4611b98e65c4b698ef51ec0e3645f2ebf3a` |
| `build/s1/app/app.bin` | 7,052,968 | `4e44741d4e51749d64eb782464abb294719707f8dcfadf590156359b09d39ed3` |
| `build/s1/repeat/app.bin` | 7,052,968 | 与上行逐字节相同 |

全部保持 `flashable=false`、`hardware_verified=false`。早期未固定时间 ABI 的平台候选 `platform.bin` 已被 `platform-abi32.bin` 取代。

验收结果：平台/App 候选重建、原厂资源/补丁边界、CRC、篡改拒绝通过；3 项构建配置/过期输入回归通过；无相邻 App/逆向仓库的隔离平台全构建通过；OTA 回归 7 项通过、1 项因未安装可选 Unicorn 跳过；跨仓边界检查通过；错误时间 ABI 的负向编译检查通过。同一源码/工具链/构建目录完整重编 App 后 ROM 逐字节相同。

可复现性范围：当前 audit 嵌入绝对输入/输出路径，其摘要进入 ROM manifest，因此不承诺更换 checkout 路径或另一台机器仍有相同 ROM 哈希。跨路径隔离构建通过的是功能/结构验收，不是字节一致性验收。

本地证据汇总 `build/s1/build-verification.json`；每个候选附带 ELF、map、audit、link、manifest 和 payload。工具链、产物和日志均位于忽略目录，没有入库或发布。

## 真实 App PIE 初验

新增 `tooling/scripts/probe-app-pic-0041.py`，复用已验证 audit 与 App 配置，以同一编译器重编全部 24 个 App 源文件；只替换 `-fno-pic` 为 `-fpie -fvisibility=hidden -mcmodel=medany`，保留 RV32/ilp32f、禁 relax、小数据阈值 0 等条件，不改生产 XIP 链接规则。

```sh
python3 -B tooling/scripts/probe-app-pic-0041.py \
  --audit-dir build/s1/app/objects --out build/s1/pic --tool-prefix "$ap01_tool_prefix"
```

24 个源文件全部编译并合并为 RV32 single-float ABI 的 ET_REL。报告在 `build/s1/pic/pic-report.json`，原始重定位与未解析导入也已保存。

| 编译器重定位 | 数量 |
| --- | ---: |
| R_RISCV_32 | 117 |
| R_RISCV_ADD32 / SUB32 | 各 981 |
| R_RISCV_CALL_PLT | 5,154 |
| R_RISCV_GOT_HI20 | 32 |
| R_RISCV_PCREL_HI20 | 1,619 |
| R_RISCV_PCREL_LO12_I | 1,651 |

这是未最终链接的编译器输出清点，不是设备修正表。ADD32/SUB32 的实例包含 switch 相对跳转表，可能离线消解；GOT 引用和绝对数据指针需要最终布局后再裁决。不能直接将这七种重定位开放给设备。

当前存在 105 个外部导入，包含 C++ `Ap01NativeServices0041`、`ap01_native0041::*`、screen/window API、libgcc/libm 与 C 运行时。虚表、字体指针和命令名称表产生 `.data.rel.ro*`，bundle_store 还产生 44 B `.data`。因此原 XIP 禁 data/GOT 的规则不能直接套用，完整 App 也尚未变成稳定 C ABI 的可加载文件。

现有平台+App XIP 模块最终 text 214,968 B、rodata 66,920 B，总计含 manifest/ABI 282,236 B。这包括平台代码，不能称作独立 App 包容量。静态预算给出的单帧 38,400 B、CompiledTemplate 11,321 B、维护线程栈 16,384 B 也只是局部项，不能相加冒称实机峰值或可用执行 RAM。

下一步：从这份导入清单收敛 C 服务边界，离线确定内部指针/GOT/跳转表如何修正；恢复 0041 内存映射与缓存证据，准备最小实机取指实验。尚未完成最终受限链接、两基址执行、APX2 黄金样本、完整 App RAM 预算及存储掉电实验；S1 保持进行中。
