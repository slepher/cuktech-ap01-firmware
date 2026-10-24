# P-03：已有覆盖与机会式刷新接口整理

**已有覆盖无新增；机会式刷新阶段可用，完整接口未闭，待合并非作者复核。** 可用阶段是“同步事件→动画期覆盖 mask→完成时恢复更新门→后续真实通知有条件消费”。原 ROM 不提供本题可证的“每个延后事件最终显示”承诺。主体已由 theme-total、window-history、E03/E04、E12/E13、N02/NR02 覆盖；**新增 ROM 业务恢复0、整函数导出0、新动画内部恢复0**。本轮将旧合同合成接入约束并复核必要原字节，不能把完成 callback 无直接重放 call 当作全局无重放证明。

认领 P-03；基线 `5bbc331ab429fb76e956e50b8081c56f8d278b11`，独占树 `.worktrees/batch-20261024-p/p03`。计划约30分钟（20–40为切块参考，允许已覆盖时提前收敛）；开始 `2026-10-24 13:48:44 UTC`，结束见末节。主树只读，仅读统一 reverse-design、管理顶部P及P-03行与本题必要旧资料。采用 REA skill，未打开或切换共享 REA/模型，未执行固件、设备、网络、SIM、QEMU、构建、回放或输入模型；不改生产、配置、ROM，不提交推送，不创建代理或接后继。没有撤销他人修改。以下伪代码与名称均是静态分析视图，非原源码。

## 继承结论

| 出处 | 本题直接继承 | 限制 |
| --- | --- | --- |
| [theme-total-state](theme-total-state-0041-20261023.md) | `0xa00ad07e(root,T)` 总信息注册、动画期覆盖 `root+0x50`、正常分组短路重读、当前 T 数值、末尾清缓存 | 当时“重放未知”不是已排定任务；不重算新增 |
| [window-history](window-history-0041-20261023.md) | 窗口开始 `+0x4c=0`，完成 `0xa00ab628(anim)` 从 `anim+0x1c`取同root并置1；特殊child7恢复GIF timer | 开始/完成原局部全部继承；不下探动画库 |
| [E03](ctk-view-dataflow-e03-0041-20261023.md)、[E04](ctk-view-review-e04-0041-20261023.md) | 真实注册→item dispatcher→`0xa00adabc(app,I)`；`+0x54`覆盖、栈view、在线port1消费、公共尾清cache | 保留port1/port2互斥；E04完整消费验收仅port1；不推广整6054B callback |
| [E12](ctk-snapshot-consumer-e12-0041-20261024.md)、[E13](ctk-offline-transition-e13-0041-20261024.md) | 已覆盖纠正、离线旧非零→新零、两个端口共用离线converter call、忽略返回后的reset→SOC | 在线转换失败跳消费不能套到离线；栈view没有持久化 |
| [N02](telemetry-interface-n02-0041-20261024.md)、[NR02](telemetry-interface-review-nr02-0041-20261024.md) | I.mask为事件变化位；cmd51/52直接赋，cmd56重读当前I后OR；walker之后清I.mask；converter仍只读当前I.mask | 没有持续有效性、历史事件队列、跨响应原子快照或最终显示保证 |
| [mode-control](mode-control-0041-20261023.md)、[lifecycle](uiiface-lifecycle-0041-20261023.md) | 总通知 `0xa00a536c` 使用`62fcb554`，调用`callback(userdata,current T)`，完整walker后清T+0xc；总回调在`0xa005d134/138`注册 | 与item链`62fcb530`和I.mask分开；不接P-02生产路径 |

原件只读 `D:/Documents/PlatformIO/Projects/cuktech-ap01-firmware/roms/0041/ap01-1.0.2_0041.bin`；沿用 CATALOG/上述资料身份 `972db4c136c7ed9e24a83c07c1a7fd62040ca018b08ca285216d26b1fee3c6b9`，little-endian RV32，`file_offset=VA−0x9ffff000`。未新增整件哈希账。三份直接retained与item callback的实际profile已核均为 Ghidra12.1.4 / `RISCV:LE:32:ap01thead2`，digest及Evidence见[evidence.json](../../analysis/deferred-refresh-p03-0041-20261024/evidence.json)的profiles。N02的响应dispatcher另为thead3，NR02已纠正；不把该来源移植到这里。

可定位Evidence：总callback `ev_48c0198ff89867a929bd03b8b4df8db7f898c5b0579e9cf06545a71c3dc77bc4`；完成callback `ev_6284955279e3fe7628b002dcf25b72407bbdab81296fb6c51d4d97a69fbebe46`；item callback `ev_19e11c8fc1582881b289f2b24c2a98bbb305f7c2e57caad784442a60d1fb76e5`；converter `ev_a83096b36b47fd87435b94d459872366820aeacdc83d31b3cff59acfd8dcf791`。原件路径不因worktree缺ignored留存而失效，helper显式读主树绝对路径，不复制整个旧函数。

## 本轮复核或纠正

两个app参数都来自相邻注册的同一构造上下文s4，分别由总/item链保存userdata。root/app在本报告同指该应用上下文，T、I、panel与栈view仍是不同对象。缓存是该root上的两个标量槽，不是T/I的副本或队列；尤其`+0x54`没有端口索引维度，入口写cache时尚未进入本次端口解码，不能默认为每端口各有缓存。

| 阶段 | 总信息 | item / CTK |
| --- | --- | --- |
| 事件输入 | 同步callback借用当前T；mask是u16 T+0xc | 同步callback借用I；mask是u32 I+0 |
| 动画查询非零 | `ad11c` LHU mask，`ad128` SW到root+50，日志后返回 | `adb5c` LW mask，`adb60` SW到app+54，日志后返回 |
| 动画查询零但更新禁用 | 还要求全局`62fc4034!=0`和root.byte4c非零；提前返回保留cache | `adba4`检查byte4c，零则日志返回，保留cache；没有凭此推整个callback的其他门 |
| 动画完成 | `ab632`取anim.userdata root，`ab638`写byte4c=1；可选处理child7 GIF timer | 同一更新开关；没有直接读写+50/+54或直接调两个callback/dispatcher |
| 下一次正常通知 | 每组先查当次T.mask，未满足才重读+50；读取当次T的功率/模式/温度 | 在线port1/2先fill栈view、以port调用converter；converter依据它重新借到的当前item及其当前mask生成数值。port1显示层另按当前I.mask或app+54决定值/SOC消费者 |
| 消费结束 | 正常两页组处理到`ad3f4..400`，非零+50清0 | 到公共`af250..25e`时非零+54清0；不是每组/每端口确认 |
| 外层通知结束 | 清当时全局T+0xc，dispatcher每次callback前重读T | 清dispatcher先缓存数组中该I.mask；对象重读规则不与总路径混同 |

**覆盖与OR必须分两层。** 两个动画入口均无load旧cache/OR/store的累积链，直接覆盖（总mask零扩展16→32，item32→32）。后续分组的“当前位成立或缓存位成立”是短路门控，并未回写OR后的cache，也不表示原代码只读取一次combined mask。动画期先后收到位1、位4，在这两个入口的顺序赋值语义下最后cache为4；这只是静态赋值结果，不是本轮运行或异常输入验证，也不能推断实际通知序列必然如此。

**缓存mask不等于当前数据。** 总callback在动画结束后的新通知中使用新T内当前字段；原入口没有保存旧T指针、旧值或历史时间。item callback的+54更不能补齐converter输入：`f4938/f4970`只取当前I.mask测试0x8000，`f49e0`只取当前I.mask测试0x20000；其参数为(dst,port)，没有app/cache参数。缓存0x8000可能打开后端SOC消费门，但若本次I.mask不含该位，converter不会因此重新写SOC/时间组；在线caller先清零view，不能把这说成补回旧SOC。行值还有view.row.valid门，因此缓存行位本身不使缺失行变有效。这个约束已经由N02/NR02给出，本轮只是串接到延后状态阶段，不记新增功能。

**清cache不等于显示成功。** port1 converter返回0在`aef66`跳port2判定；已验互斥意味着成功选择port1时不自动再执行port2。port2的`af180`转换0直接到公共`af250`，那里仍可清cache；两个转换失败门/尾路径已核原字与分支目标。故本阶段不提供重试、保留到成功或逐位确认合同。更不能反过来把cache仍非零当作拥有一份可延后安全使用的view；view只活到本次callback返回。

完成函数全部136B已由window-history保存。本次仅从旧窗口/原ROM复核其四条直接call，集合为child accessor `a00dcee4`、日志`a008b51a`（两次）、timer resume `a008bd70`；不是总/item通知或消费者。没有间接业务call的本地指令形状也可在该窗口逐行复核。没有展开这些库callee，不能据该集合排除别处、timer下游或后续正常事件触发更新，亦没有证明完成时全局animation_query已为0。

## 真正新增为0与实际验证

本轮仅将既有合同整理成可实施阶段：两类cache分离、覆盖而非积累、当前数据与事件mask分离、清cache不是显示成功。无新ROM业务、整函数导出、开源来源认证或完整重放触发发现。18个必要窗口都是旧留存的有界重读，不按字节数重算功能恢复。该稿可与P-02生产→通知合同合并非作者复核，只审接口衔接及必要继承，不重复全套旧动画验收。

[verify.py](../../analysis/deferred-refresh-p03-0041-20261024/verify.py)可由非作者一次运行：只读主树选定ROM和旧JSON、独立按Capstone核标准指令边界及固定原字/operand、解直接JAL目标、核两条converter失败分支，并核四份实际profile；只写本独占目录。[checks.json](../../analysis/deferred-refresh-p03-0041-20261024/checks.json)为PASS，[evidence.json](../../analysis/deferred-refresh-p03-0041-20261024/evidence.json)保存窗口、原字和来源索引。厂商清I.mask指令`a38d8:0b502a41`只比较原字、承继E02局部SLEIGH语义；不冒称Capstone独立认证vendor ISA。脚本不执行指令或枚举输入，没有导入/重跑旧作者验证器。字节锚点、文档/来源一致性检查不等于动态观察或完整数据流形式证明。

**可自定义的新实现策略，与ROM事实分开：** 若重建目标需要保证动画后刷新，可在同步通知时复制所需组到应用自有缓存，并单独维护有效组和按端口dirty位；动画期间合并dirty，完成后主动请求一次UI刷新，只有实际消费的组才确认。此策略是实现选择，ROM本题没有证明这种OR累积/主动刷新/按组确认，也没有给线程安全、锁或原子快照承诺。异步UI不能持有原T/I/view借用指针；N02的同步复制/有效性合同直接继承即可，无需恢复LVGL内部。

## 未闭精确边与一个后继

1. `ab638`恢复byte4c之后，谁保证再产生一次总/item业务通知、完成时全局动画查询结果、通知年龄/间隔均未知；本题没有有种子的自动业务重放call，不扩大到全ROM负搜或库内部寻找假设触发器。后续真实通知存在时才可依本阶段推导，不能以静态可达替代“必然发生”。
2. +50/+54的全局全部writer、root最终退出/注销、所有并发顺序仍未闭；本题未对无种子退出重新派生任务。P-01模式停机和P-02正常生产分别归原作者，不搭便车。
3. 可登记的一个真实后继是 **`0xa00adabc`旧非零→新零路径在`0xa00ae250`汇合后的child0汇总指示/位清除/业务timer阶段**。E13明确止于详细panel reset→SOC，保留`ae250`之后未验；同callback既存assembly已给真实入口和app=s6、端口index来源，可追该阶段UI状态写入与本地timer调用参数，止于再次汇入常规更新；不重复E13 selector/滑动、converter/控件库，不扩P-01/P-02底座生产。预估20–30分钟，派发前仍由管理者核其与旧theme-online（另一`a00ac93c`）及较晚成果的对象/连接差集；本作者没有取新窗口或自动接题。

本交付回答的是有条件刷新可用性，完整“延后事件最终刷新”接口仍未闭；作者自核不代替非作者接受。

结束 `2026-10-24 13:56:29 UTC`；至交付检查墙钟约7分45秒，旧合同覆盖明确而提前收敛，未填满计划工时。工具耗时包含墙钟，未另测有效工时；无主动等待/任务中断。helper最终成功核18窗810B/265条、25个原字/operand锚点、7个直接call目标、2条converter失败分支和4份profile；编写期间修正helper的旧JSON字段兼容及压缩分支解码并重跑至PASS，不运行输入模型。2份JSON解析、14个报告链接定位与尾换行/尾空格检查通过；N02/NR02只在主树，按整合目的原路径核对，其余产物在独占树；`git diff --check`通过。token由父窗实测统计，本工具无用量数据，不估算。完成后停止，不自动接后继。
