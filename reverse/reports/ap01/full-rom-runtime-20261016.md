# 原厂0031完整运行调查（2026-10-16）

## Plan
用户要求根据应用逆向结果完整运行原厂ROM。先核对SIM与芯片仿真的区别，使用既有Unicorn执行精确原件的有界入口探测，记录首个未支持行为。不会将SIM菜单、函数stub或跳过初始化当作完整ROM运行。

## Task
1. 核对完整镜像、现有执行引擎和板级支持。
2. 原样加载并从已知应用入口执行；只提供声明的RAM，不模拟外设成功或修改指令。
3. 保存指令/异常证据、明确完整运行缺口。

## 硬件模型实施（后续授权）
用户明确授权继续实现CSR0x7c5及逐步启动/外设模型。先用固定提交的博流SDK核对CSR定义，在Unicorn外层实现可审计指令语义，不改ROM、不用函数成功stub；未知指令/寄存器继续明确停止。每个依赖有定向语义测试和真实ROM回放。模型与基线探测分开，保留原失败证据；完整启动只按系统/应用/显示实际里程碑验收。

### 本轮实际实现与路线调整

**用户随后指出可采用开源NuttX、仅重建应用层；后续主线转为[应用重建方案](application-rehost-plan-20261016.md)，硬件模型不作为应用移植前置条件。** 本轮已完成部分模型及测试，原厂ROM仍未完整启动；没有将应用重建版与原厂BIN运行混称。

- 模型 [emulate_ap01.py](../../../tooling/scripts/emulate_ap01.py)：复用Unicorn2.1.4，原件只读。实现MHINT及其他已遇到的CSR软件可见读改写；MTVEC/MTVT保存CLIC模式，CLIC配置及80个槽的初始化读写；RAM物理/缓存/重映射地址共享底层存储。
- 实现实际遇到的INSB、ADDSL、EXT/EXTU、RV32 T-Head字节/半字/字索引及前后递增访存、功能性cache维护；ROM指令不改写，普通函数不替换成功stub。未知编码继续异常停止。ADDSL按厂商规范移位rs2，定向回归覆盖两操作数非对称和32位溢出，避免受QEMU解码文件旧注释误导。
- GLB/PDS/HBN、TZ配置、SF_CTRL配置、SYSMAP及eFuse控制仅实现启动已遇到的寄存器白名单；未知地址拒绝。配置寄存器有文档复位值/写掩码或显式模型初态，不把状态寄存器一概返回ready。TZ隔离、flash事务、实际USB/无线、完整中断派发、计时和OTP加载仍未实现；这些寄存器锁存不能视为完整外设模型。
- 原厂真实回放观察 **180961条指令尝试**，MHINT由0读改写到0x100000，执行进入RAM `0x62fc1d5c`。两块搬运结果分别7104 B/10536 B，与原件文件0x1c14/0x37d4源数据逐字节一致；执行流来自原厂搬运代码，不是宿主预填充。
- 最终停在T-Head存储指令访问eFuse影子地址 `0x20056000`；该影子区清零/OTP加载尚未建模。**不是遇到设备私钥不足的已证实结论，也没有把首个eFuse控制访问误当设备身份读取。** 0x20056800实际是EF_IF_CTRL_0，按SDK复位值实现后已通过首个读取。
- [最终回放JSON](../../analysis/hardware-model-final-20261016.json)、[REA静态证据](../../analysis/rea-hardware-model-20261016.json)（5条记录）；逐步失败在同目录hardware-model-step1..20.json。step7包含已纠正的ADDSL移位错误，step15为旧版每指令停启导致的时间预算耗尽，不能拿它们作为最终验收。最终CLI成功输出的是调查证据，`full_rom_boot_verified=false`。
- [11项语义测试](../../../tooling/scripts/test_ap01_hardware.py)通过，覆盖CSR六种读改写、零寄存器/别名、ADDSL操作数顺序与溢出、INSB各字节、原厂复制指令对、访存前后更新/负偏移、符号提取、RAM别名、MMIO掩码/子字节、未知CSR/MMIO与ROM写入拒绝。参数路径与模型相同。

```powershell
python -B tooling/scripts/test_ap01_hardware.py --deps reverse/app-0031/deps
python -B tooling/scripts/emulate_ap01.py --image ../cuktech-ap01-firmware-tools/artifacts/firmware/original/ap01-1.0.2_0031.bin --deps reverse/app-0031/deps --output <已有目录中的新JSON>
```

来源固定为博流SDK commit `41bf338a57be53919d99f6c6715a96100428c97d`：[CSR定义](https://github.com/bouffalolab/bouffalo_sdk/blob/41bf338a57be53919d99f6c6715a96100428c97d/drivers/lhal/include/arch/risc-v/t-head/Core/Include/csi_rv32_gcc.h)、[内存映射](https://github.com/bouffalolab/bouffalo_sdk/blob/41bf338a57be53919d99f6c6715a96100428c97d/drivers/lhal/config/bl616/bl616_memorymap.h)、[寄存器目录](https://github.com/bouffalolab/bouffalo_sdk/tree/41bf338a57be53919d99f6c6715a96100428c97d/drivers/soc/bl616/std/include/hardware)。本地sdk-*.h/c/S均为artifacts只读参考；原厂0031未证明与该SDK提交完全对应，已用ROM实际访问交叉核对。扩展指令语义参考[厂商ADDSL规范](https://github.com/XUANTIE-RV/thead-extension-spec/blob/master/xtheadba/addsl.adoc)、[LWIA规范](https://github.com/XUANTIE-RV/thead-extension-spec/blob/master/xtheadmemidx/lwia.adoc)和OpenOCD的旧版Packed指令编码；不把最新RISC-V P草案当作原厂旧版P编码。

资源/限制：内置RAM480KiB、外部RAM4MiB各只有一份真实缓冲、别名共享；XIP按6804520 B向页取整。trace64项、详细event512项且计数保留，10秒/100万指令默认有界。RAM/eFuse等初态不是Boot2快照，MHINT初值可指定；CLIC控制位宽4为显式模型选择，未经实机验证。cache使用一致性功能模型、无时间/功耗精度；异常当前返回诊断而不派发原厂异常处理器。宿主峰值RAM/栈未测，未新增持久格式或NVS项。

## Status
现有SIM为x86-64源码目标，不接纳AP01原厂RV32裸BIN。WSL未安装qemu-system-riscv32/64，现有Unicorn2.1.4位于app0031-20261013/deps，包含Windows原生库，可复用。已有材料是应用槽镜像，非全闪存/BootROM/Boot2/实际分区与外部文件系统备份。

## Review
**完整原厂ROM尚未运行成功。** 已复用现有Unicorn2.1.4 Windows库实际执行原件入口探测；原件哈希前后不变。证据 [rom-startup-probe-20261016.json](../../analysis/rom-startup-probe-20261016.json)，工具 [probe_rom_startup.py](../../../tooling/scripts/probe_rom_startup.py)。本轮无ROM补丁、外设stub、设备访问或SIM变更。

```powershell
python -B tooling/scripts/probe_rom_startup.py --image ../cuktech-ap01-firmware-tools/artifacts/firmware/original/ap01-1.0.2_0031.bin --deps reverse/app-0031/deps --output <已有目录中的新JSON>
```

结果：观察到7条指令尝试，SP=0x62fdb890；最后一条hook记录为0xa0000018，原字节 `f322507c`，小端指令字0x7c5022f3，按标准CSR编码为 `csrrs t0,0x7c5,zero`。执行引擎随后产生异常号2，回调/停止时PC=0xa000001c。**最后尝试的指令地址与异常回调PC分别记录，不能把0xa000001c称为已证明的故障指令地址。** 未进入系统初始化、应用表或图形界面。

这证明当前generic RV32配置不能直接越过该CSR访问，不证明更完整的CPU实现一定也失败。没有跳过CSR或随意返回0；这种修补也不能证明硬件初始化成功。脚本限100000条/2秒；镜像只读可执行、候选片内RAM及4MiB外部RAM零填充。不提供MMIO；此初态是探测假设，不是已验证的AP01 Boot2交接状态。映射约11MiB、记录最多32条指令，峰值宿主RAM/栈未测；无持久格式/NVS改变。

## 完整运行仍缺什么

| 范围 | 当前证据 | 待实现/核对 |
| --- | --- | --- |
| 处理器 | RV32镜像，0x7c5访问在当前引擎异常 | AP01 CPU扩展、CSR语义、特权/中断初态 |
| 启动与内存 | 应用入口与部分RAM范围已知 | Boot2交接状态、BootROM服务、初始化数据/中断向量/缓存 |
| SoC外设 | 原厂芯片驱动、分区代码线索 | 时钟/复位、定时器/中断、SPI/闪存、DMA、显示及输入模型 |
| 外部状态 | 当前是应用槽镜像 | 实际分区/文件系统内容或明确定义并验证的替代初态 |
| 产品依赖 | 页面及米家/蓝牙任务入口 | 无线固件/服务、充电底座等依赖或明确限定的模拟设备 |

正确路线是实现AP01/BL616家族板级模型并逐段验证原厂启动；已有NuttX SIM可继续用于独立应用源码重建，但不能因此宣称完整原厂ROM启动。若只重建页面，那是另一种产物；本次未将用户要求改写成UI复刻。

[QEMU官方说明](https://www.qemu.org/docs/master/system/target-riscv.html)明确：RISC-V固件需要匹配板级模型，CPU架构相同不足以跨板运行；通用virt不是AP01。公开文档定向搜索未找到AP01/BL616板级模型，未声称已穷尽所有第三方模拟器。WSL本轮未安装QEMU，没有伪造QEMU启动失败记录。
