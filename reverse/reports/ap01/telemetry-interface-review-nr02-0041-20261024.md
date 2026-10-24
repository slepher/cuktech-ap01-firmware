# NR02：N02 底座遥测→应用快照接口合并非作者复核

**可独立使用阶段已闭合但接口未闭；修正差集已确认，限定接受。** N02 的正常同步 item 增量捕获合同可用于重建；三个 cmd51 普通字段的源/宽度、最后一项 type 非零门、本轮变化位直接赋 mask 后通知均得到独立原件检查支持。无行为语义纠正，新增 ROM 功能0。不能将本结果登记为全量底座遥测、实机成功或任意时刻一致全量快照。

认领仍为 N02，复核者 NR02 未参与作者生产。基线 `5bbc331ab429fb76e956e50b8081c56f8d278b11`；独占树 `.worktrees/batch-20261024-n/nr02`。计划约30分钟，允许有界问题提前完成。开始 `2026-10-24 13:28:36 UTC`；结束与实际墙钟见末节。已读主树最新 reverse-design 流程和管理 N02 行；主树仅只读参考。采用 [REA skill](C:/Users/cogic/.agents/skills/reverse-engineer-anything/SKILL.md)，复用留存、不切共享 REA、不创建子代理。

本轮只写本报告与同名 analysis；未运行/导入任何作者或继承验证器，不执行目标、模型、SIM、QEMU、回放、构建、设备或网络，不改 ROM、生产、配置、分析器，不提交推送，不撤销其他修改。下文分析名和顺序表达均非原源码。

## 继承结论

复核对象为主树 [N02报告](telemetry-interface-n02-0041-20261024.md)及其 [interface.json](../../analysis/telemetry-interface-n02-0041-20261024/interface.json)。旧独立验收直接继承，不把已有静态研究重算为本轮发现：

| 已有来源 | 本次继承及边界 |
| --- | --- |
| B22/B23 | cmd51 unsigned16 两级分类、三处 `item+0x18` 门/阈值、byte 类型发布；未知一级 fallback 与 05ac 二级默认不混用。B23当时的 writer 断边已经由 B25/B26 补足。 |
| B24→B25/B26 | 正常 cmd56 的13B长度门、整12B比较/复制、复制后重读当前对象、OR 0x800 后同步通知。容量单位、跨响应同实例仍未知。 |
| E01/E02 | 五资源分配/覆盖/释放，item getter，item 通知借用与完整 walker 后清 mask，cmd52 五项原位覆盖，converter 已列公式。只接受已列局部闭包，不推广整个 dispatcher 或全局逐项销毁。 |
| E03/E04、E12 | 真实间接 callback、主要 port1 消费、0x52B 栈视图；保留 port1/port2 谓词互斥纠正。E12只是已覆盖纠正，不是第二次指令验收。 |
| E13 | 旧非零→新零的离线分支、共用 converter call、忽略其返回后 reset→SOC、reset严格 row.valid==1、values→name→status。E13为复用/局部自核，本轮只核继承出处，不把它冒称新的独立完整离线验收。 |
| 生命周期、总信息/主题/历史合同 | T 的380B与独立424B项数组、总 mask 与 item mask 分离、功率显示比例、signed8温度、借用和释放顺序。cmd50 正常生产、模式和订阅外部边界未搭便车纳入。 |

本轮重读6份直接相关合同的必要段落并核原路径；没有通读滚动历史或重新研究整分类/转换器。机器索引的 cmd51 三条映射、cmd52 五资源尺寸/位与继承合同一致；18个项目内链接存在。此类文件/引用检查属于证据完整性检查，不是功能执行。

## 本轮复核或纠正

原件只读 `D:/Documents/PlatformIO/Projects/cuktech-ap01-firmware/roms/0041/ap01-1.0.2_0041.bin`；沿用身份 `972db4c136c7ed9e24a83c07c1a7fd62040ca018b08ca285216d26b1fee3c6b9`，little-endian RV32，`file_offset=VA−0x9ffff000`。未另造整件哈希清单。旧来源 `reverse/analysis/buzzer-backlight-0041-20261023.json#/functions[address=0xa00a8582]`，Evidence `ev_6f9f82e5daf0540a1c24a0b85daa2e394785391692765e5e3e100eb7b37ed94c`。

[独立脚本](../../analysis/telemetry-interface-review-nr02-0041-20261024/review.py)直接读取原 ROM，从标准 RV32 编码解算 load/store 位宽、寄存器、立即数、B/JAL/C.J 目标及关键压缩原字；旧 assembly 仅辅助定位/人工流追踪。4个有界窗口 `93a4..941a / 9504..951e / 9580..960a / 972a..973e`（均高位 `0xa00a`，右端不含）共302B/84条指令与旧 raw 逐byte一致；[independent-checks.json](../../analysis/telemetry-interface-review-nr02-0041-20261024/independent-checks.json)保存原字与56项PASS。标准库脚本不执行这些指令或枚举输入。

| N02合同项 | 判定 | 独立依据及限制 |
| --- | --- | --- |
| raw更新长度、返回不作item处理先决门 | 接受 | `93a8/93b0/93ba/93be`给全局raw、LBU数量/掩码和helper目标；`93be`后直接建立总对象处理，不检查a0返回。shift与描述符ABI沿旧留存/接口核对；不认证外层帧长。 |
| record与item区分、active门 | 接受 | `93e8..940c`重读总对象/count、signed BGE循环界、424步长、array+index、u8 active；`9738/973a/973c`为index+1、record+8、回到重读。没有把record+0x18写成item+0x18。 |
| u16 record+2→u16 item+0x10 / 0x100 | 接受 | `9598..95a8`为两个LHU、相等跳过、SH、ORI本轮changes。直传，未见缩放。 |
| u8 record+0→u8 item+0x12 / 0x200 | 接受 | `95ac..95bc`两个LBU、相等跳过、SB、ORI。正式协议名/物理单位未知。 |
| u8 record+1→u8 item+0x0f / 0x80 | 接受 | `95c0/95c4`读取当前type，零跳9734；非零才`95c8..95d8`比较/写入。先前`950e`已写新type，因此type变化时检查新值；type0不清旧+0x0f。 |
| changes形成与任一变化通知 | 接受 | `9508`先置0；变化type两路径置0x40；普通字段只OR本轮寄存器。`9734`在+0x0f未写的路径仍按changes!=0进入发布，不要求最后字段变化。 |
| mask直接赋值→日志→通知 | 接受，厂商语义来源限定 | `95e4`原字独立解出 custom0/f3=5/upper5=8、rd=a6/rs1=s9/rs2=s4/shift0；对照旧局部SLEIGH为32位直接store至array+index*424。`95fc`日志、`9600`index低8位、`9604`通知目标。没有load旧mask再OR。 |
| cmd52五资源与cmd56三种mask写法 | 继承接受 | cmd51直接赋本轮changes、cmd52直接赋单事件位、cmd56对复制后重读的当前item做OR；三者不可统一为持续有效位。五资源尺寸20/24/12/24/24B与E02一致。 |
| 两个12B BMS相关对象 | 接受对象边界 | cmd56是内联`[I+0x18,I+0x24)`；remote BMS为`load32(I+0x30)`指向的独立12B。两者与cmd51分类/CTK SOC分别连接，不凭日志名称或尺寸合并。 |
| converter/借用/有效性 | 继承接受 | 三指针非零只保证本地转换门；SOC/时间各自重读0x8000，行组读0x20000，其他位不自动填这些组。同步回调捕获自有副本是重建设计建议，非ROM已有队列/原子快照实现。 |
| 页面/离线/最终销毁 | 限定继承 | 在线转换0跳过主要消费不能套用离线；callback栈view返回后失效；全局deinit未证逐项清理，userdata/注销属N03。运输错误/取消/超时未形成统一遥测结果码。 |

**唯一修正项：来源元数据，现已解决。** 初审N02正文“cmd51接入精度”将旧dispatcher标为 `RISCV:LE:32:ap01thead2`；该函数实际保存的 `profile.parameters.language_id` 为 **`RISCV:LE:32:ap01thead3`**，作者static-checks也写3。作者已修此处，Ghidra12.1.4及Evidence不变，并明确 `th.srw`语义对照E02所引 `ap01thead2.sinc` 属另一局部规则来源；私有模型不等于独立厂商ISA规范。NR02仅重核修正后的主树正文两处、作者15秒修正记录、旧来源profile及static-checks，确认一致。本项无行为影响，未直接改作者文件。

## 真正新增

新增ROM功能0、行为语义纠正0；本复核产物仅为N02新增cmd51精确映射的非作者限定接受、必要继承串接核对及1处profile标注修正请求。[artifact-checks.json](../../analysis/telemetry-interface-review-nr02-0041-20261024/artifact-checks.json)记录机器合同/链接/继承来源检查及修正定位。未运行N02的32项脚本，也未复用其164B/45条计数作为本轮独立结果。

## 未闭精确边

| 真实断边 | 状态及可用后继种子 |
| --- | --- |
| 全量total/普通端口生产 | cmd50入口`0xa00a8b72`，历史caller`0xa00a8c14/0xa00a9298`；本轮不扩。若管理者授权后继，可先核其正常raw→T+4/I+8→通知，公共历史算法继承。 |
| Cells/Power应用数值 | `I+0x34/+0x38`覆盖/所有权可用，24B解释/真实数值读者未闭。保留raw；无真实reader种子时不扩全ROM搜索。 |
| 物理单位、响应年龄、实例一致性 | cmd56容量单位、remote物理标定、cmd56→cmd51实际先后、线程串行化/序号/时间戳未知。相同索引/布局不证明跨响应同一实例；当前合同不提供全量原子快照。 |
| 接入退出及运输边界 | N01模式确认、N03订阅销毁、逐项最终释放和完整运输错误/超时/取消合同不在此验收。callback借用不等于可异步持有item/资源。 |

阶段结论：来源标注修正差集已确认，同步正常item-delta捕获阶段限定通过；完整底座遥测接口继续未闭。没有实机观察、SIM或目标执行证据，不从静态图外推物理效果。

结束 `2026-10-24 13:34:27 UTC`，至末次技术核验墙钟5分51秒。56项ROM检查、2份JSON解析、N02的18个项目内链接、本报告6个链接、4份交付文件范围/尾换行/无尾空格检查通过，`git diff --check`通过；两份新JSON受现有忽略规则保留在原路径，非缺失。没有主动等待或任务中断；工具耗时计入实际墙钟，未另测有效工时。token由父窗实测统计，本工具无用量数据，不估算。修正请求后本题停止，若作者同题修正仅复核该差集。

同题修正复核：`2026-10-24 13:36:26..13:37:02 UTC`，墙钟36秒，无等待/中断；保留前次技术计时。仅确认主树报告profile改为ap01thead3、局部thead2模型参考分列及作者15秒修正记录，与旧来源/既存static-checks一致。更新本报告与artifact-checks，JSON解析/格式检查通过；未重跑ROM检查、任何验证脚本或开展新研究。修正差集已确认，限定接受，完成后停止。
