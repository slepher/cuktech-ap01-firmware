# S1：两基址加载实验与 0041 内存证据

2026-11-02。离线实验通过；未访问设备，未刷 ROM，未冻结 APX2 或产品 ABI。

## 实际编译与执行结果

`probe_app_pic_0041.cpp` 是独立实验样本，不在平台/App 生产源码清单中。它包含内部函数指针、C++ 虚表、初始化 data、零初始化 bss，以及带 version/size 的服务表间接调用。测试关闭去虚拟化，保证虚表路径实际存在。

固定 GCC 12.5.0、RV32/ilp32f、PIE、hidden、medany、禁 relax、小数据阈值 0。在 `0x10000` 和 `0x30000` 分别离线链接；主机从可信 ELF 提取段和重定位，将内部绝对指针转换为相对基址值。规范化后两份映像完全一致。

| 项目 | 实测 |
| --- | --- |
| text | 124 B |
| rodata | 12 B |
| data / bss | 8 B / 4 B |
| 初始化映像 / 内存跨度（含对齐） | 152 B / 156 B |
| BASE32 修正 | 2 处：偏移 136 的虚表函数指针、144 的内部函数指针 |
| 已离线解析的 PC-relative 引用 | HI20/LO12 各 4，CALL_PLT 1 |
| 执行基址 | `0x200000`、`0x400000`，仅模拟地址，不是 AP01 实机候选地址 |
| 每个地址的结果 | 首次 35、第二次 36、错误服务表版本返回 `0xffffffff` |

两处执行均经过实际 RV32 指令模拟；BSS 从零开始、跨调用累计，data 初值正确，内部指针/虚表和外部服务回调均生效。测试有 10,000 条指令预算及返回地址断言。

9 项负向检查通过：入口越界、入口奇数对齐、修正越界、修正写代码区、重复修正、截断映像、超内存预算、指针越界、加载基址加法溢出。修正前完成所有检查，不在拒绝中途写入输出。这里只验证由测试构造的元数据；不是不可信 APX2/ELF 的完整解析器。

实验的 linker RWX 提示来自合成单映像布局，模拟器也未施加硬件隔离；不能据此宣称具有 W^X、进程隔离或沙箱能力。GOT、相对 switch 表、库依赖及真实 App 完整生命周期仍未进入此最小样本。

## 复现

依赖仅装在 `build/s1/python` 虚拟环境：`unicorn==2.1.4`、`pyelftools==0.32`。后者未实现 RISC-V 重定位名称表，脚本只显式接受本样本已观察到的编号，并保存 GNU readelf 输出对照；不把它扩大成设备端通用 ELF 支持。

```sh
python3 -m venv build/s1/python
build/s1/python/bin/python -m pip install 'unicorn==2.1.4' 'pyelftools==0.32'
# 输出目录必须已预建且为空；本机 Unicorn 使用与通过的 RV32 基线相同的提权执行环境。
build/s1/python/bin/python -X faulthandler -B tooling/scripts/test-app-pic-load-0041.py \
  --out build/s1/load-probe-03 \
  --tool-prefix "$PWD/build/s1/toolchains/xpack-riscv-none-elf-gcc-12.5.0-1/bin/riscv-none-elf-"
```

通过证据：`build/s1/load-probe-03/load-report.json`、两份 ELF/dis/readelf 和 `probe.bin`。映像 SHA256 `01e8528d08daae49cb0c05b100be39117e8a0ecaad44bb47d52222f5b0135d38`。现有 `test_0041_unsigned_ota.py` 在该环境下 8 项全部通过，补齐上一轮可选 Unicorn 跳过项。

## 本轮 Python 崩溃确认

北京时间 2026-11-02 18:11:12，`Python-2026-11-02-181112.ips` 对应本对话的 `load-probe-02` 实验。PID 50175、父进程 codex；异常 `EXC_BAD_INSTRUCTION/SIGILL`，工具退出码 132。故障栈为 Unicorn `init_cache_info → machine_initialize → uc_init_engine → uc_mem_map`，发生在宿主模拟器初始化，尚未执行实验 App。

该次实验未通过，不能计入验收。随后提权环境运行既有 RV32 测试及 `load-probe-03` 均通过；已只读确认无残留实验进程。现有证据定位到 Unicorn 宿主缓存初始化，未证明具体系统限制或根因；不能把成功重跑解释为设备代码或真实缓存机制已通过。没有设备连接、写 ROM 或生产应用重启。

## 从本地 Git 历史恢复的 0041 证据

独立逆向仓库目前通过 GitHub/Git 均不可访问，但固件仓库拆分前的本地提交 `81378f4` 保留证据，无须恢复整个旧树。读取以下历史文件：

- `reverse/analysis/0041-20261013/0041-heap-region-gnu.txt`：23 条指令逐字节对照本机固定 SHA 的原厂 0041，全部相同。
- `reverse/sdk/sdk-bl616_memorymap.h`：标注片内 RAM 的缓存/总线别名，以及 PSRAM 的 `0x88000000` / `0xa8000000` 别名；这是 SDK 区域定义，不是设备空闲内存测量。
- `reverse/reports/ap01/qemu-0041-runtime-20261017.md`：历史模型曾执行原厂复制到 `0x62fc20b6` 的 RAM 代码；报告明确缓存 CSR 是模型锁存值，未模拟真实缓存/权限/中断副作用。

可复查命令：`git show 81378f4:<上述路径>`。本轮保存的原始片段和校验摘要在 `build/s1/0041-heap-region-gnu.txt`、`0041-memorymap-history.h`、`memory-evidence.json`。

原件静态观察：`0xa0029640` 一带通过同一堆对象（指针槽 `0x62fc6aec`）调用区域加入函数，参数包含 `0x6302f270` 至 `0x63030000`（3,472 B），以及 `0xa8000000` 至 `0xa8400000`（4 MiB）。本轮另反汇编当前 malloc 入口 `0xa002fcc8`，确认它读取同一堆对象后调用 `0xa002ed8e`。

因此目前可支持的推断是：普通 malloc 使用的堆包含多个地址区域，单凭分配成功不能保证分配到了片内 RAM，也不能保证代码可执行或指令缓存一致。4 MiB 是静态加入区域的跨度，不是当前可用容量、最大连续块或已证明可执行容量。仍须核实硬件实际映射/权限/缓存及分配结果，不能选择该范围直接跳转。

## 真实 App 导入的收敛方向

上一轮 105 个导入并非都应成为平台服务 ID：

| 当前依赖 | 后续边界 |
| --- | --- |
| `Ap01NativeServices0041` 构造/析构/start/busy | 平台拥有生命周期，App 只通过 C 服务及可撤销句柄访问；不跨边界传 C++ 对象 |
| `ap01_native0041::*` 网络、时钟、线程 | 通过有版本的 C 服务表导入，任务/回调登记到 generation；不保留不可排空的回调 |
| screen/window/LVGL 原厂适配 | 固件拥有原厂对象，App 通过受控显示/事件服务访问 |
| `malloc/free`、字符串、new/delete、libgcc/libm | 明确分配所有权；纯运行库可考虑随 App 链接，但必须验证其 PIC/重定位与体积，不能默认静态库可搬移 |
| SHA256、日历等辅助函数 | 选择明确的 C 服务或 App 内部实现，不按当前 C++ 符号名冻结 ABI |

下一步先核实 0041 执行内存及缓存入口，再对真实 App 的这些边界和最终布局做实验。最小样本通过只证明此工具链下两处内部指针可离线归一化并在模拟器搬移执行；完整 App 可加载性、实机容量、健康/停止、掉电恢复和 APX2 黄金样本均未完成。
