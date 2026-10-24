# P-R02：P-02/P-03 合并非作者复核

**可独立使用阶段已闭合但完整接口未闭；限定接受两份交付，行为纠正0。** P-02正常cmd50生产→同步通知可用于重建；P-03是既有覆盖整理，其“动画期覆盖mask→完成恢复更新门→后续真实通知有条件消费”可用。两者衔接不构成原子快照、动画后必然刷新或完整遥测合同。新增ROM业务恢复0。

复核者未参与P-02/P-03作者工作。基线`5bbc331ab429fb76e956e50b8081c56f8d278b11`；独占树`.worktrees/batch-20261024-p/pr02`；仅写本报告及同名analysis。采用[REA skill](C:/Users/cogic/.agents/skills/reverse-engineer-anything/SKILL.md)，复用留存，不开/切共享REA，不执行固件、设备、网络、SIM/QEMU、构建、回放或指令/输入模型，不修改ROM、生产、配置、分析器或作者稿，不提交推送、不创建代理。

首次可得开始`2026-10-24 13:58:33 UTC`；计划约30分钟，按问题收敛提前交付；结束与墙钟见末节。主树只读，已读reverse-design、管理顶部P及本认领/两作者行；必要继承只查相关合同，不重审旧整套动画或公共库。

## 继承结论

作者材料为主树[P-02](D:/Documents/PlatformIO/Projects/cuktech-ap01-firmware/reverse/reports/ap01/power-producer-p02-0041-20261024.md)及[P-03](D:/Documents/PlatformIO/Projects/cuktech-ap01-firmware/reverse/reports/ap01/deferred-refresh-p03-0041-20261024.md)。两作者已停止，父窗确认主树逐字节保存。本轮只复核这两项差集及必要衔接。

| 继承范围 | 本轮如何使用 | 不作新增/全量认证 |
| --- | --- | --- |
| N02/NR02 | T/I布局、cmd51/52赋mask与56 OR、converter当前mask门 | 不重验51/52/56分类、单位、Cells/Power读者 |
| E01/E02 | item借用、遍历后清缓存数组mask、失活清前0x24B与五资源释放 | 不展开allocator/公共copy/全局销毁 |
| window-history | item/total历史入参LHU、非零返回0x400及完成callback | 不重做180点算法、最大值、采样周期 |
| N03及其复核 | total通知每轮重读T，末尾清当时T+0xc | 不重验注册/摘链/退出及并发callback增删 |
| theme-total、E03/E04、E12/E13 | 总信息与port1栈view消费、离线返回差异 | E13仍按既有局部/自核范围继承；本轮未把它升级成完整离线独立验收 |

原件只读`D:/Documents/PlatformIO/Projects/cuktech-ap01-firmware/roms/0041/ap01-1.0.2_0041.bin`，长度6,769,704B；沿CATALOG身份`972db4c136c7ed9e24a83c07c1a7fd62040ca018b08ca285216d26b1fee3c6b9`，不另造整件哈希清单。RV32 little-endian，`file_offset=VA-0x9ffff000`。

P-02 dispatcher原留存`reverse/analysis/buzzer-backlight-0041-20261023.json#/functions[address=0xa00a8582]`，Evidence `ev_6f9f82e5daf0540a1c24a0b85daa2e394785391692765e5e3e100eb7b37ed94c`，Ghidra12.1.4，`RISCV:LE:32:ap01thead3`，digest `bcefdee5092076e55636e077b45523e203f4b870ae7b7ab547945ed1b8162279`。P-03四份profile仍沿作者evidence中的thead2，不与dispatcher来源混用。厂商mula/ext/extu/srw的语义只承继既有本地SLEIGH及E02；本轮独立提取其编码字段，不宣称独立认证厂商ISA或运行模型。

## 本轮复核或纠正

以下全为原ROM静态观察/推断；名称及公式不是原厂源码。`I`指caller缓存项，`J`指普通值helper重新取得项，`T`需按各读点解释。

| 项目 | 决定 | 独立证据与适用条件 |
| --- | --- | --- |
| raw入口/描述符 | 接受 | `85a0/4/8`写cmd/len/pointer；`85d8→8b72`；`8b76`LBU count、`8b7e`raw指针、`8b88`AND0xf8、`8b8c→a0191652`。原留存显示call后转工厂显示门，未检查返回。固定长度helper本体继承正常合同，不认证外层帧长 |
| I/J身份 | 接受 | `8bcc/8bd0`重读T/count；`91ce`缓存数组、424B步长得I；`390e`重新取全局T、`391c`取数组、`3926`mula得J。helper无本地count门。I=J以及通知器所借项相同均有条件，不能合并成永久身份 |
| 普通V/C/P | 接受 | `392a/394a`两LHU，+50、signed DIV100、比较/SH到+4/+6；变化返回5/OR6。`396e..3982`重新LHU、MUL/+5/DIV10、SH到+8。C不变但V变仍经`3988→398a→396e`重算P；不比较旧P，P位4不要求数值不同 |
| 活动/状态 | 接受 | bit10先比较、日志后重读写+0xc；0→1先SB+0xd再helper并OR0x20；1→2写本身无独立0x20；活动分支重读low2，不等3沿清理后走公共尾。+0xd不能压成bool |
| 特殊分支/半字latch | 接受，读者未决 | inactive条件bit0与(+0x24&0x30)==0x10时只SH电压+4、OR1，无C/P/4。`921c..9234`对`0x62fcb50a` OR(1<<k)后SH；它不是I.mask，消费者/清除未知 |
| R+7转换 | 接受 | `9260`一次LBU，先(b,0,0)再(b,8,first)。独立核两树分支与29个立即数叶；`379e`BGEU选择a2/阈值，`3830`AND0xfd合并21/23。P-02表的18个支持b及其first/threshold/final逐行相符；其他u8支路0，不外推其他mode的API/单位 |
| item历史/mask/通知 | 接受 | `9290..9296`先以s9&4设置本地总重算位1；`9298`LHU I+8交历史；非零OR0x400。`92aa`srw直接赋s9到缓存数组该项，`92e2→389c`，返回后才index+1/R+8及重读T/count。非OR旧I.mask，非先收齐再集中通知 |
| 总量/历史/总通知 | 接受 | 全部item回调后才用循环末T/count条件求和；`8bdc`SH0、`8be6`每步LHU累加槽、`938e`LHU项P、`9394`每步SH。因此sum mod65536，不是u32持久值或饱和。`8c10`重取T做历史，`8c26`再取T，`8c36`直接SH mask，`8c52→536c`。总位域是1/0x400，与item位域不同 |
| 同root双缓存 | 接受 | 额外40B相邻注册桥`5d126..5d14e`核两callback指针、两AUIPC/JALR注册目标和两次`mv a1,s4`。+0x50/+0x54同应用上下文但分属total/item；T/I/view仍不同对象。+0x54不是按端口数组 |
| 动画期缓存 | 接受 | `ad11c→ad128`LHU total.mask后SW+0x50；`adb5c→adb60`LW item.mask后SW+0x54。二者直接覆盖；后续“当前位或cache位”短路门不回写OR累计。更新门关闭的提前返回保留cache，公共正常尾可清cache |
| converter/当前mask | 接受 | `f4938/f4970/f49e0`只LW当前I.mask分别门控0x8000/0x8000/0x20000；没有app/cache参数。在线view先清零；后端cache位能开消费门却不能促使converter填缺失组，行valid门继续有效。`aef66→af12e`、`af180→af250`核失败去向；到公共尾清cache不证明显示成功/重试/逐位确认 |
| 完成callback与重放 | 接受有限否定，全局未决 | 全136B完成窗中`ab632`取anim+0x1c root，`ab638`SB root+0x4c=1；四条直接call为child accessor、两log、timer resume，无其他间接业务call形状。局部不读写双cache/直接调通知；不排除callee/timer下游/别处重放，也不证明完成时animation_query已零或后续通知必然发生 |

复核没有要求作者修正行为或扩大范围。普通值只保留数值算式及既有日志/消费者命名，raw wire物理单位不造；同步回调可复制标量到应用自有存储，借用T/I/view指针不跨回调持有。序号、代际、dirty OR、动画完成主动刷新与成功确认是可选重建设计，不能反写成ROM事实。

### 完整接口与可用阶段分列

| 交付 | 可用阶段 | 完整接口 |
| --- | --- | --- |
| P-02 | 正常cmd50 raw→普通数值/状态→逐项历史/同步通知→回调后总和/历史/总通知，限定接受 | 未闭：工厂显示、物理单位/年龄、跨响应实例与一致性、继承Cells/Power读者、运输/最终退出 |
| P-03 | 已覆盖整理接受；后续真实通知到达且正常门满足时机会式消费 | 未闭：完成后通知活性、全局animation状态/重放来源、双cache全部writer、root退出/注销与并发顺序 |
| 合并接入 | 同步事件mask/借用寿命、双cache覆盖与当前converter门之间的局部衔接成立 | 不保证事件队列、每个延后事件最终显示、跨端口逐位确认、全量原子快照 |

## 真正新增

新增业务恢复0。非作者独立复核不是作者脚本重跑：本轮新写[stdlib静态核验源码](../../analysis/power-refresh-review-pr02-0041-20261024/independent_review.py)，只读ROM、原dispatcher留存、作者JSON位置/字节索引，从原字节独立解析标准32位字段、压缩长度/指定li和分支、JAL及AUIPC/JALR目标。未导入、运行或复制作者验证器实现，未用Capstone或指令模型。

[独立检查记录](../../analysis/power-refresh-review-pr02-0041-20261024/independent-checks.json)：209项PASS；P-02七窗1236B/378边界、P-03必要十八窗810B/265边界，合25窗2046B/643条；另40B相邻注册桥，总原件读取覆盖2086B（未把完整ROM加载长度计作窗口覆盖）。P-02五个已有dispatcher窗另与原raw_ranges逐byte核对。人工静态CFG复核覆盖状态分支、两转换树逐叶、变化P位、通知次序及动画缓存约束；检查数不代表完整数据流形式证明。

编写时修正本复核脚本一个memset直接call预期地址手录错误（`a002e906`→原字节实际`a0024906`），最终重跑PASS；这不是作者稿纠正。厂商字段检查及边界/字节相同不替代厂商语义的独立规范证明。

## 未闭精确边

1. `0xa00a9234→u16[0x62fcb50a]`消费者/清除与业务通知连接未知；只保留真实writer种子，不在本批扩扫。
2. `0xa00ab638`恢复更新门后，后续总/item通知由谁保证、间隔/年龄、全局animation查询结果未知；“完成窗无直接重放”只限该136B本地形状。
3. `0xa00adabc`离线分支`0xa00ae250`之后child0汇总/位清除/timer阶段仍沿P-03建议待管理者查重登记；本复核没有取新窗口或将旧E13升级为全量验收。
4. 全局双cache writer、最终root/订阅销毁、并发/跨响应一致性、wire标定与运输错误均未因本批接受关闭。没有把阶段完成写成完整ROM完成。

结束`2026-10-24 14:05:00 UTC`，墙钟约6分27秒，提前收敛；token由父窗实测统计，本工具不可得，不估算。无主动等待或任务中断，工具读取/编写/检查包含墙钟，墙钟不等于测得有效工时。最终209项独立核验、JSON解析、报告引用/尾换行/尾空格、独占路径状态及diff检查PASS。交付格式检查第一次受Windows默认GBK解码影响，显式UTF-8后通过；不涉及证据或业务结论修改。未提交推送，交付后停止。
