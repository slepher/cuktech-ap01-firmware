# 0041 B17：FactoryTest active 有界定位独立复核

结论：**限定接受 B16，纠正检索边界措辞；外部读者仍未知**。两个实际候选只认证为既有 initializer 的 byte 写入和既有 callback 的 byte 首门，不构成新增外部 reader。没有复跑或扩大 ROM 定位，没有扩工厂 UI/销毁。

基线 `0e1d5b9`；独立分支 `codex/re-0041-b17`。按本树滚动管理记录共同规则/B17任务书及 `C:/Users/cogic/.agents/skills/reverse-engineer-anything/SKILL.md` 静态复核；本树与祖先未发现适用 AGENTS.md。原 ROM/evidence 位于 `D:/Documents/PlatformIO/Projects/cuktech-ap01-firmware`，仅只读。未开 REA 会话/数据库，未执行固件、连接设备/外部服务、修改 ROM/模型/生产代码/安全检查、做缺陷验证或新建哈希清单。

## 依据与逐项判定

输入为 [B16报告](factory-active-reader-b16-0041-20261023.md)、其 [locate.py](../../analysis/factory-active-reader-b16-0041-20261023/locate.py)、[localization.json](../../analysis/factory-active-reader-b16-0041-20261023/localization.json)、[instruction-evidence.json](../../analysis/factory-active-reader-b16-0041-20261023/instruction-evidence.json)、[保存引用](../../analysis/factory-active-reader-b16-0041-20261023/retained-reference-hits.json)。本轮独立 [verify.py](../../analysis/factory-active-review-b17-0041-20261023/verify.py) 与 [review-index.json](../../analysis/factory-active-review-b17-0041-20261023/review-index.json) 是本地派生证据，无新造 REA Evidence ID。

| 项目 | 判定 | 原始依据与边界 |
| --- | --- | --- |
| 两个候选及归类 | 接受 | 保存列表仅 `a005b7b4→a005b7ba` store、`a009f178→a009f17c` load；逐点核原 ROM，共7条/24B，见下表。没有声称独立重做完整定位。 |
| initializer byte写1 | 接受 | LUI a5；C.LI a4,1；SB的funct3=0、rs1=15、rs2=14、S立即数=0x2b8，地址 `62fc9000+2b8`。这是大容器 `a005a736` 的已知内联块，非新bool接口。 |
| callback byte零门 | 接受 | LBU funct3=4，8 bit零扩展；BEQ rs1=15/rs2=0，B偏移0x1c6，目标 `a009f346` C.JR ra。active=0直接返回，非零落到 `a009f184`；该门不消费入参，未认证a0返回值或C返回类型。 |
| 留存引用回源 | 接受所选引用 | 4个既存JSON，27条保存pointer逐项回源，6条normalized/raw target边均 `a005b7ba→62fc92b8 WRITE/read=false`。其余为pseudocode/referenced_names。父record包含 `a005a736`，不是新reader。重复表示不等于独立指令访问。 |
| 完整literal命中计数/全局引用完备性 | 未核 | 本轮只回源保存pointer，没有重做目录字面量搜索，也不重认证318/310等完整计数或“仅四文件”完备性。native_value_flow出现状态位置不自行形成机器指令读边。 |
| 检索谓词 | 纠正描述 | AST核 `LUI` 后 `+4,+6,…,+66` 半字起点，opcode3/19或35，rs1相同及立即数字段0x2b8。没有funct3筛选，opcode19不限ADDI；没有寄存器kill/CFG跟踪、代码数据过滤。B16报告及JSON scope不应暗示数据已过滤。 |
| 检索区间 | 纠正引用/精度 | 起点范围 `[0,0x1bee24)`；最后一个起点的4B slice可跨末端2B，故非所有字节严格落在区间内。`0x1bee24`见[0041-handoff.md](0041-handoff.md)，本轮核该处 `-rom1fs-` 原字节；不是factory inventory中已证明的全代码段边界。 |
| 外部读者不存在 | 不接受此推广；B16未作此推广 | 别名、结构基址、GP/PC相对、其他地址拆分、跨64B生存期、间接指针、宽读涵盖byte、区间外代码仍未知。负结果只属于保存的这次直接编码候选定位。 |

## 原指令与局部合同

| 地址 | ROM字节 | 独立原编码结论 |
| --- | --- | --- |
| `a005b7b4` | `b797fc62` | LUI x15,62fc9000 |
| `a005b7b8` | `0547` | C.LI x14,1 |
| `a005b7ba` | `238ce72a` | SB x14,0x2b8(x15)，8 bit写1 |
| `a009f178` | `b797fc62` | LUI x15,62fc9000 |
| `a009f17c` | `83c7872b` | LBU x15,0x2b8(x15)，8 bit零扩展 |
| `a009f180` | `6383071c` | BEQ x15,x0,a009f346 |
| `a009f346` | `8280` | C.JR x1，返回调用者 |

无中间基址改写的这两个短链可认证目标地址；泛搜索模式本身不能认证其他候选数据流。独立对照旧 [callback原窗口](../../analysis/factory-test-0041-20261023/instruction-windows.json) 的464B与ROM完全一致，但不因此重认证callback完整非零分支/调度/销毁。initializer来源沿用 [retained-initializer](../../analysis/factory-test-0041-20261023/retained-initializer.json) 中 `a005a736` / `ev_dc0e38b0f382799ea2a8e8ad7f21cefc5998b0767ecf38a58cfdebe8add167c3`；本轮不重新生成该provider记录。

恢复程度仍部分：只验收已知写1与callback首门、保存引用和负搜索边界。新增外部函数地址、参数、返回、直接调用者/被调用者、触发条件均未认证；active=1不证明timer继续周期执行。`PogoPinMng/FactoryTestMode.c`支持厂商业务的暂定归属，不能证明精确来源版本或未修改开源实现；新增开源排除为0。

## 实际验证与后继

实际运行 `python reverse/analysis/factory-active-review-b17-0041-20261023/verify.py`：通过7条/24B独立位域、464B留存窗口、27条JSON pointer及6条WRITE精确目标回源、定位器AST与ROMFS magic核验。初次本轮脚本因AST格式化括号预期不符停止，修正本轮断言后通过；未运行B16的locate.py/verify.py，也未写其证据。报告链接与 `git diff --check` 检查另行通过。以上均为静态验证，无运行时结论。

只精确修正B16报告一段检索说明，不改其两个命中或核心未知结论。后继建议转向一个已有明确入口的新私有正常协议小链；不要重复工厂active负扫描。本轮不开展新项。
