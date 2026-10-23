# 0041 B16：FactoryTestMode active 外部读者的有界定位

结论：**未定位到可认证的外部直接读者，合同仍未知**。本轮按任务书的负结果分支交付搜索边界；没有将 initializer 或 `a009f178` timer callback 重新算成新增读者，也不证明其他读者不存在。FactoryTestMode 整体仍为部分恢复，来源按既有报告的厂商业务暂定，未新增开源排除。

本轮基线 `30c7797`，只读原厂 0041 ROM `D:/Documents/PlatformIO/Projects/cuktech-ap01-firmware/roms/0041/ap01-1.0.2_0041.bin`，映射基址 `9ffff000`。未重算哈希、未复制清单、未打开共享可写 REA 会话/数据库；未执行固件、连接设备/服务、修改 ROM/生产代码/安全检查/分析模型，未作缺陷验证。

## 入口与证据

- [既有 factory-test 报告](factory-test-0041-20261023.md)及其 [retained-initializer](../../analysis/factory-test-0041-20261023/retained-initializer.json)：初始化容器 `a005a736`，Evidence ID `ev_dc0e38b0f382799ea2a8e8ad7f21cefc5998b0767ecf38a58cfdebe8add167c3`。
- [既有代码/资源 inventory](factory-code-resources-inventory-0041-20261020.md)、[引用映射](factory-reference-map-0041-20261020.md)：有 `PogoPinMng/FactoryTestMode.c` 路径，未提供一个已认证的外部 active reader seed。
- [一次有界定位结果](../../analysis/factory-active-reader-b16-0041-20261023/localization.json)及 [定位脚本](../../analysis/factory-active-reader-b16-0041-20261023/locate.py)。它是直接编码候选搜索，不是 provider 全局 xref 查询。
- [既存引用命中摘要](../../analysis/factory-active-reader-b16-0041-20261023/retained-reference-hits.json)：保留原证据绝对路径所对应的相对路径、JSON pointer、所属函数及摘录；[原指令复核](../../analysis/factory-active-reader-b16-0041-20261023/instruction-evidence.json)、[复核脚本](../../analysis/factory-active-reader-b16-0041-20261023/verify.py)。新 JSON 是本地派生静态证据，不伪造 REA Evidence ID。

## 搜索边界与结果

先检查本树报告/analysis 中的地址文字、既有 inventory 和留存引用。主树 `evidence/rea-0041-20261017` 下 JSON 的区分大小写字面量 `62fc92b8` 检索命中四个既存文件：`round3/evidence/whole-rom-round3-initial.evidence.json`、`evidence/whole-rom-retained-private-20261023-000.json`、`evidence/whole-rom-private-20261023.evidence.json`、`evidence/whole-rom-usb-closure-20261023.evidence.json`。四者命中所属函数均是 `a005a736`；三个 bundle 的 normalized/raw 表示含重复记录。native_value_flow 中反复出现的内存状态位置不是新的机器指令读者，不按命中数计访问数。其保留 outgoing reference 的精确目标边均是 `a005b7ba -> 62fc92b8`、`WRITE/read=false`。

随后仅一次运行 `locate.py`：ROM 文件偏移 `[0,0x1bee24)`，即虚拟地址 `[9ffff000,a01bde24)`，按 2 字节步长定位 32 位 `LUI` 的 upper=`62fc9000`，检查其后 64 字节内同基址寄存器、I-type load/ADDI 或 S-type store 的立即数 `0x2b8`。区间末端取既有 inventory 的 ROMFS 起点，**不是**已证明的全部代码段边界；半字候选也可能落在数据/指令中部，必须逐点核原指令。这里没有跟踪中间寄存器改写，因此只产候选、不自动认证真实数据流。

只得到两条候选，逐点原编码已认证：

| 地址 | 原字节 / 指令 | 局部事实 | 分类 |
| --- | --- | --- | --- |
| `a005b7b4` | `b797fc62` / LUI a5,62fc9000 | 后接 `a005b7b8: 0547`，a4=1 | 既有 initializer |
| `a005b7ba` | `238ce72a` / SB a4,0x2b8(a5) | 写 **8 bit** 的 1 到 `62fc92b8` | 既有写者，排除为新读者 |
| `a009f178` | `b797fc62` / LUI a5,62fc9000 | callback 的全局地址构造 | 既有 callback |
| `a009f17c` | `83c7872b` / LBU a5,0x2b8(a5) | 读 **8 bit 零扩展** 到 RV32 a5 | 既有读者，任务明确排除 |
| `a009f180` | `6383071c` / BEQ a5,zero,a009f346 | active=0 时直接跳到 `a009f346: 8280` / JR ra | 既有 gate，无新调用边 |

以上不能排除别名/结构体基址加偏移、不同 LUI 拆分、GP/PC 相对构造、跨越 64 字节的地址生存期、间接指针、宽读涵盖该 byte、区间外代码或遗漏的 retained evidence。尤其没有把“无这个直接编码模式”转换为“无外部状态消费者”。没有扩大到工厂 UI、销毁或蜂鸣扫描。

## 合同恢复程度

新增外部函数地址、入参宽度、返回值、直接调用者/被调用者、业务条件和数据布局均**未知，未认证**；本轮不补造函数或 getter。已核原指令只用于说明两个候选为何不满足新增 reader 的范围：

```c
// 既有局部对照，不是新增恢复的外部接口。
// initializer a005a736 内联成功尾部：*(uint8_t *)0x62fc92b8 = 1;
// callback a009f178 的首门：
if (*(const uint8_t *)0x62fc92b8 == 0) return;
// 非零后续行为沿用旧报告，本轮不重认证整个 callback。
```

callback 此门不使用传入参数，LBU 结果保存在 a5、零时直接返回；未建立返回寄存器 a0 的值语义，也不从这三条指令推断 C 返回类型。initializer 是大容器内联块，不能把它写成独立 bool 接口。active=1 仍不能推导 timer 继续周期运行。

## 实际验证与后继

`python reverse/analysis/factory-active-reader-b16-0041-20261023/locate.py` 运行一次，得到 2 候选；之后未重跑定位。`verify.py` 通过：24B 选定窗口的 Capstone 解码与独立原编码 LUI/SB/LBU/BEQ/return 字段核对、既有 callback 464B 留存原字节对照、候选列表及保存 JSON pointer 回源核验，确认 retained 精确目标边的 WRITE 标记。脚本只静态读原件，未进行运行时验证。报告本地链接及 `git diff --check` 另行通过。

本轮已完成任务书允许的有界未知交付；外部 reader 仍未恢复。小后续建议：独立复核这一次搜索的边界和负结论；若继续功能恢复，先从一个已有明确消费者 seed 做局部别名解析，避免按同一模式重复全 ROM 扫描。工厂 UI/销毁仍留在原有未知范围。
