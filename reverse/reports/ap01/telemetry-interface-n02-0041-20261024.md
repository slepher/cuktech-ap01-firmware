# N02：0041 底座遥测到应用快照接口

后续状态：已获[非作者复核限定接受](telemetry-interface-review-nr02-0041-20261024.md)，阶段闭合、完整接口断边保留；以下“待复核”是原作者交付时状态。

**可独立使用阶段已闭合但接口未闭，待非作者复核。** 已形成 `cmd51/52/56 → UiIFace item → 同步变化通知 → CTK 数值视图` 的接入合同。真正新增只限 cmd51 三个普通字段的源偏移、类型门和通知精度；分类、扩展缓冲区、cmd56、转换器和真实页面消费均继承旧合同。本交付可用于实现同步数值捕获与应用自有缓存，不能称为全部底座遥测或任意时刻的一致全量快照。

认领 N02，基线 `5bbc331`；独占 `batch-20261024-n/n02`。计划约30分钟（参考20–40）；开始 `2026-10-24 13:16:29 UTC`，结束及实际墙钟见末节。采用 [REA skill](C:/Users/cogic/.agents/skills/reverse-engineer-anything/SKILL.md)；只读主仓留存及 ROM，不打开/切换共享 REA，不执行固件、模型、SIM、构建、历史回放、设备或网络，不改生产/ROM/配置/分析器，不提交推送、不创建代理。仅写本报告和同名 analysis，不撤销他人修改。

原件沿用 `roms/0041/ap01-1.0.2_0041.bin`，身份 `972db4c136c7ed9e24a83c07c1a7fd62040ca018b08ca285216d26b1fee3c6b9`；RV32 little-endian，`file_offset=VA−0x9ffff000`。本次无新 REA Evidence ID、无整函数重导。字段名是分析命名，以下伪代码不是原源码；所有 `+0x` 为十六进制偏移，数量/尺寸/除数明确按十进制。

## 继承结论与接入对象

| 来源 | 直接继承范围；本轮不重计 |
| --- | --- |
| [B22](cmd51-device-type-b22-0041-20261024.md)/[B23](cmd51-device-type-review-b23-0041-20261024.md) | cmd51 两级 unsigned16 ID 分类表、三处 item+0x18 阈值、类型 byte 写入。精确分类表保留原报告，不替换成品牌/USB 协议推测。 |
| [B24](cmd51-item-field-producer-b24-0041-20261024.md)→[B25](cmd56-item-field-contract-b25-0041-20261024.md)/[B26](cmd56-item-field-review-b26-0041-20261024.md) | B24 候选已由 B25/B26 接受为 cmd56 正常有效项的12B写入；不能继续把它作为未证 writer，也不重复计新增。 |
| [E01](uiiface-item-ownership-e01-0041-20261023.md)/[E02](uiiface-ownership-review-e02-0041-20261023.md) | 五嵌套缓冲区分配/覆盖/清理、item getter、通知 ABI、完整已列 CTK 转换公式及局部失败门。 |
| [E03](ctk-view-dataflow-e03-0041-20261023.md)/[E04](ctk-view-review-e04-0041-20261023.md)、[E12](ctk-snapshot-consumer-e12-0041-20261024.md)/[E13](ctk-offline-transition-e13-0041-20261024.md) | 真实 callback、port1 主要消费、0x52B 栈视图、离线复位。保留 E04 的端口互斥纠正，不再把 caller 当缺口。E13是旧合同复用/局部自核，不冒称独立验收。 |
| [生命周期](uiiface-lifecycle-0041-20261023.md)、[总信息消费](ui-total-consumers-0041-20261023.md)、[主题总信息](theme-total-state-0041-20261023.md)、[历史](window-history-0041-20261023.md) | total/array 身份、总功率显示比例、温度 signed8、历史布局和离线释放顺序。仅作本接口背景，不扩 cmd50、动画/公共库或 N01/N03。 |

`T=load32(0x62fcb2cc)` 指向380B总对象，`A=load32(T+0x00)` 是独立 item 数组，`count=load8(T+0x06)`；`I=A+index*0x1a8` 是424B项。`0xa00a53c0(index_word)` 在总对象为空或 unsigned index≥count 时返回0，否则借用 I；没有 retain/分配。item 的 `u8+0x13` 是创建索引，`+0x24` 描述字节支持应用端口映射；不是 cmd51 记录起点。

| 对象字段 | 位宽 | 本合同使用 |
| --- | --- | --- |
| T+0x04 / +0x07 / +0x08 | u16 / i8 / u8 | 总功率 raw / 温度 raw / 模式；功率已有显示 `raw/10`、`raw%10`，温度不新增 °C 单位承诺。模式生产/确认归 N01。 |
| T+0x0c / I+0x00 | u16 / u32 | **不同事件掩码**，均在各自同步 walker 结束清零；不是持续有效位。 |
| T+0x0e / I+0x3c | 各364B | 180个u16样本及最大值/游标；历史 bit0x400 不等于当前值变化，也不带已证采样秒数。 |
| I+0x0d / +0x0e | u8 / u8 | active / device_type；type0x15 为既有 CTK 分支。 |

`cmd51/52/56` 在这里的结果是 item 事件；不能因 T 持有数组就把 item 的 `0x8000/0x20000` 当 total mask，或推断同时调用 total callback `0xa00a536c`。total callback 借用 T、item callback 借用 I，分别由旧合同描述。本阶段不认证 cmd50 总功率/普通端口功率生产者；已有 total 视图可独立读取，但其所有生产字段尚未合成完整遥测接口。

## 本轮复核或纠正：cmd51 接入精度

旧 E01/E02 已列三个后继字段与变化位，但未给出源 record 偏移及 `+0x0f` 类型门。本轮必要旧留存/原件核验见 [static-checks.json](../../analysis/telemetry-interface-n02-0041-20261024/static-checks.json)。源为 `buzzer-backlight-0041-20261023.json#/functions[address=0xa00a8582]`，Evidence `ev_6f9f82e5daf0540a1c24a0b85daa2e394785391692765e5e3e100eb7b37ed94c`，Ghidra12.1.4 / 私有 `RISCV:LE:32:ap01thead3`。

cmd51 先以原始记录全局 `0x62fcb2d4` 为目的调用既有 `0xa0191652`；请求复制长度是 **`(u8[0x62fcb01c]<<3)&0xf8`**，响应描述符在 caller 栈上，payload 指针位于描述符+4。沿旧 helper 的比较/复制合同；这里不认证外层帧长度。随后独立遍历 UiIFace，**不检查 helper 返回值、不以本次 raw 内容发生变化为分类先决条件**。每轮重读 T/count/A，index 是 signed word 循环索引，record 每次+8；仅 `I.active!=0` 才走下表。

| record 源 | item 目的 | 更新/缩放 | 变化位；证据 |
| --- | --- | --- | --- |
| u16+0x04，条件读取u16+0x06和 I 的u16+0x18 | u8+0x0e | B22/B23完整分类表；变化先写新type再清理/条件分配 | 0x40；分类/所有权直接继承 |
| **u16+0x02** | **u16+0x10** | 不等才 SH，直传，无缩放证据 | 0x100；9598..95a8 |
| **u8+0x00** | **u8+0x12** | 不等才 SB，直传，无缩放证据 | 0x200；95ac..95bc |
| **u8+0x01** | **u8+0x0f** | 先读**当前/新**type，type非零且值不等才 SB；type0时保留旧+0x0f | 0x80；95c0..95d8、9734 |

后面三个字段的正式协议名仍未知，不能从宽度推断温度、协议、功率或单位。局部 changes 从0开始，只 OR 本轮各位；`9734` 使其他字段有变化但 `+0x0f` 未变时仍进入通知。`95e4` 是 `th.srw a6,s9,s4,0`：把 changes **直接赋给** I.mask；继而日志、`9604→0xa00a389c(index&0xff)`。不是与 I 的旧 mask 做 OR，也没有“必须+0x0f变更才通知”的门。

没有发现需推翻 E01/E02 的行为错误；上面是旧压缩表述的源映射补齐和必要门控收紧。私有 indexed-word-store 的寄存器/编码独立核验，语义继承 E02 所引 `ap01thead2.sinc` 的局部 SLEIGH 规则；这是局部语义参考，与上述 dispatcher 留存的 `ap01thead3` profile 来源分开，未认证厂商指令规范。

## 真正新增：可供应用采用的字段与更新合同

### cmd52：资源快照覆盖

`payload[0]` 是u8索引；先借用 item，再复制 `payload+1` 的8B header，首 word 按小端比较；subtype byte为 `payload[8]`。资源源指针均是 **payload+5**。

| header / subtype | item 持有的32位指针 | 覆盖字节数 | 赋值事件位 | 应用使用 |
| --- | --- | ---: | --- | --- |
| 0x2b010112 | +0x28 Dev | 20 | 0x4000 | 下表数量/模式源 |
| 0x2b010114 / 1 | +0x30 BMS | 12 | 0x8000 | SOC、时间 |
| 同上 / 2 | +0x34 Cells | 24 | 0x10000 | 保存raw；实际页面数值读者未闭 |
| 同上 / 3 | +0x2c Port | 24 | 0x20000 | 四槽行值 |
| 同上 / 6 | +0x38 Power | 24 | 0x40000 | 保存raw；实际页面数值读者未闭 |

全部沿 E02：缓存目的指针→compare→不等门→目的非零门→copy→日志→直接赋 mask→同步通知；不改写为先判空或 OR，比较相等不通知。它们原位覆盖，不交换资源指针、不分配。未知 header/subtype进入既有查询推进；本阶段不提供“畸形数据被拒绝”的统一返回合同。cmd51 类型变化进入0x15才分别零分配20/24/12/24/24B；type同值不会补齐缺指针，五项没有整组成功门/回滚。

### cmd56：内联容量类raw，独立于 remote BMS

继承 B26：**len==13**，正常 T非零且 index<count；整12B比较不同后，把 `payload+1` 复制到 `[I+0x18,I+0x24)`。随后重读 T/count/A，用当时 I.mask **OR 0x800**，日志后同步通知。不能把复制前缓存目的与复制后当前数组强行合并成稳定实例。

`u16 I+0x18/+0x1a/+0x1c` 分别是日志 DCap/FCap/RCap；+0x1e..+0x23保留为6B opaque，**所有单位/缩放未证**。cmd51 的7515/7517/7519分类读取这个 inline `I+0x18`；cmd56不直接重算分类。这个12B区域与 `load32(I+0x30)` 指向的12B remote BMS **不是同一对象**，不能用 DCap 当 SOC、也不能由同名 BMS 日志认同两种载荷。与 cmd51 的真实响应先后、跨响应同实例保持均未知。

### CTK转换：可用的是事件视图

`0xa00f4740(dst,port_word)` 使用 `(port-1)&0xff` 作 getter 索引，依次要求 item及 p28/p2c/p30 非零，否则返回0；成功返回1。它不检查 dst、p34/p38，成功也不表示远端数据已经收到：零分配的缓冲区可能尚无新遥测。端口映射沿 E04：描述字节bits5..4为0时，低nibble0/1/2→port1/2/3；高位1/2→port4/5。本轮只采用既验收正常映射。

以下 `D=dst`，`B=load32(I+0x30)`，`V=load32(I+0x28)`，`P=load32(I+0x2c)`；load16均为unsigned，整数除法/半字截断保留。门每处按原代码重读 I.mask，不合并为一次固定快照。

| 输入 | 输出及精确算式 | 写入门/含义 |
| --- | --- | --- |
| u8 V+5/+4/+0xb/+0xa/+0x11 | u8 D+1/+2/+3/+4/+5；u8 D+6=五项和 mod256 | 三指针门成功后总会写；日志支持C/A/无线/DC/Mux数量分析名 |
| 上述数量 | 四行kind/ordinal：C/A/无线/Mux→1/2/3/6；单项ordinal0，多项从1起 | u8总数≤4才生成；DC数量计入总数却无独立标签循环，保留此差别 |
| s=u16 B+8，u16 V+6 | V+6==0：u16 D+8=(s+99)/100，D+0xa=0，u8 D+0x50=0；否则D+8=s/100，D+0xa=(s%100)/10，D+0x50=1 | **I.mask&0x8000**；SOC整数/一位小数及显示模式，不能把本算式外推 wire物理标定 |
| u16 B+0xa | m=(raw<<3)/60；u16 D+0xc=m/60、D+0xe=m%60 | **再次读取0x8000门**；消费者按小时/分钟显示；不把raw额外命名为秒 |
| port_word | u8 D+0=port低8位 | 在SOC与时间两门之间写，不依赖BMS变化 |
| u16 P+2 的bits7..4 / bits3..0 | start/end；1/0特例把end改1；输出从D+16*start推进 | **I.mask&0x20000**才先清四个row.valid；仅 `(u8)(slot-1)<4` 写行，输入序号在跳过输出时仍推进 |
| 每条输入 P+4*j：u16+6 的bits11..8=kind | row+0=u8(kind!=0)；kind3→row+1=0、kind4→1，其余保留旧direction | 被写行；row=D+0x10+16*i，i=0..3 |
| 同条u16+4、u8+6 | v=(raw16+50)/100；c=(raw8+1)>>1；u16 row+4/+6=v/10,v%10；row+8/+0xa=c/10,c%10；row+2=(v*c+50)/100；u8 row+0xe=1 | 同上；消费者格式为电压 `%d.%d V`、电流 `%d.%d A`、功率整数；只认证这条显示换算 |

row+0xc/+0xd 为kind/ordinal，row+0xe是本次写行标志；D+0x50是SOC小数显示模式。三者都不是总数据有效性位。**I.mask=0x40/0x80/0x100/0x200/0x800/0x4000/0x10000/0x40000不使SOC或行组自动重算。** converter对非本门字段保留旧dst内容；caller先清零只提供初值，不会把缺失的遥测组变成有效零值。

### 捕获、所有权与离线/错误边界

原 item dispatcher `0xa00a389c(index)` 固定借用数组/item，调用 `callback(userdata,I)`；完整walker结束才清该缓存数组中 I.mask。回调内可以读取事件位和当前字段，回调返回后不能靠原mask判断“是否曾收到数据”。资源仍归item；payload只同步比较/复制，dst只取得数值，无资源/数组所有权转移。

**应用接入建议（重建设计选择，不是新增ROM实现）**：在同步回调内复制index、事件mask及需用的数值/raw到应用自有对象；单独记录该对象是否曾收到Dev/BMS/Port等组与离线状态。按捕获时真实I.mask合并组，不用converter返回1或数值为0代替有效性，不把后续读取到的清零mask当作“无数据”。若转交异步UI，转交复制值，保留获取事件时的组标志。此阶段没有提供ROM线程锁/原子性/代际句柄承诺；重建若需一致性须自行串行捕获，并把该策略与已证原序分开。

既有真实页面路径为 `0xa00a389c → 间接0xa00adabc(app,I) → 0xa00f4740`。在线port1/2谓词互斥；正常已核port1先清0x52B栈view，转换返回0跳过主要消费；返回非零仍受全局/初始化状态门及item.mask/app+0x54短路重读门。app+0x54是动画时**覆盖保存mask**，不是完整数据副本，也不改变converter只读当前I.mask的事实；本阶段不保证延后期间每条事件最终显示。

离线阶段继承E13：旧active非零→新0时清端口初始化字节；C1/C2共用 `0xa00ae238` 转换调用，**不判断其返回**，随后 reset→SOC。reset严格row.valid==1才按 values→name→status 消费，否则做无效行复位；在线是row.valid!=0，不能统一条件。view在callback栈上，主要消费者仅读标量，callback返回失效。不能从在线返回0跳消费推出所有caller都跳，也不能宣称失败必然回滚/清零全部dst。

cmd50指定失活分支沿E02：先清item前0x24B再逐个释放/清零五指针，mask0xfff进入公共通知尾部。总对象deinit则先同步offline通知，后重读全局并释放数组/总对象；没有证据把逐项嵌套清理自动插入deinit。订阅最终注销、userdata寿命及回调增删属于N03；这里仅要求同步借用，不能据此认证异步持有。

## 未闭精确边、验证与交接

新增语义是 cmd51 `record+2/+0/+1 → item+0x10/+0x12/+0x0f` 的精确源/位宽及最后一项的type门，并把直接赋mask与变化累积接到通知。事件视图/有效性/inline容量与remote BMS分离是旧事实的接入解释，不另计新ROM功能。分类、cmd52、cmd56、转换/消费者、离线合同不重计新增，也不把作者自核写作独立接受。

| 未闭 | 精确边及影响 |
| --- | --- |
| 全量total/普通端口生产 | 已知cmd50入口 `0xa00a8b72`，总功率历史caller `0xa00a8c14`、端口历史caller `0xa00a9298`；本题未扩其正常字段写入，故不能称完整底座遥测。若授权下一块，先复用这几个caller旧证据核 `raw record → T+4/I+8 → 通知`，估10–20分钟，公共历史算法直接继承。 |
| Cells/Power应用含义 | `I+0x34/+0x38` 的24B覆盖/持有/释放已闭，实际数值读者未定位；可保留raw，不能输出自造电芯/功率数组结构。没有真实reader种子时不无种子扩扫。 |
| 载荷单位/真实时间线 | cmd56单位、remote各raw物理标定、cmd56→cmd51实际先后、响应年龄/序号/线程串行化仍未知；当前地址关系只保证同实例同index条件下同址。 |
| 生命周期外部边界 | N01控制请求/确认、N03订阅注销、全局逐项最终释放不由本报告闭合；运输错误/超时也没有映射成新的遥测结果码。 |

[机器接口索引](../../analysis/telemetry-interface-n02-0041-20261024/interface.json)可供一次批量复核；所有数值偏移在该JSON中为十进制，字符串hex保持0x。必要新增证据为[验证器](../../analysis/telemetry-interface-n02-0041-20261024/verify_static.py)及其static-checks：3个稀疏旧窗口164B/45条指令与ROM、旧raw逐byte一致，32项静态字段/分支/调用/字符串检查PASS。未运行任何旧作者验证器；不重验既有整分类/转换器，也不执行输入/目标模型。

作者本次还核两份JSON可解析、19个报告链接、接口索引形状、独占文件范围及 `git diff --check`，均PASS；所有4个交付文件（含被Git忽略的2份JSON）保留原路径，未提交。非作者建议一次核：cmd51三个源及门→本轮赋mask→通知；其余按上述已接受接口串接，重点三种mask写法、两个BMS对象、converter事件门及离线不判返回。不要重新导整个dispatcher或扩大公共copy/formatter。

结束 `2026-10-24 13:27:03 UTC`，至末次技术核验墙钟10分34秒；没有主动等待/任务中断，工具读取与静态核验包含在墙钟中，未单独测有效工时。可用独立阶段提前收敛，不为接近计划时长扩题；全量接口断边如上。子工具未提供token用量，记不可得，由父窗会话遥测统一统计，不估算或重复相加。

NR02元数据修正：`2026-10-24 13:35:25..13:35:40 UTC`（15秒，原技术计时保留）。核旧记录 `profile.parameters.language_id` 与既存static-checks均为 `RISCV:LE:32:ap01thead3`，修正本报告原误写的dispatcher profile；另明确 E02 的 `ap01thead2.sinc` 仅为局部store语义参考。仅改报告标注及本记录，业务合同/证据JSON不变；未重读ROM、运行作者脚本或开展新研究。
