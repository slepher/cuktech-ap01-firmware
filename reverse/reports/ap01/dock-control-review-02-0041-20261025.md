# Q-02：描述表输入与替换生命周期非作者复核

**可独立使用阶段已闭合但接口未闭。Q-02作者本轮差集逐项接受；技术纠正0，业务新增0。** 描述符直接来自本次cmd55原payload+23，count另取基础信息缓存并可沿旧值；固定24B缓存通知不覆盖整个描述表。真实远端条目值/顺序仍未知，不能据此认证selector等于数组序号加1或设备执行成功。

复核者`/root/dock_control_review_02`未参与作者成果。认领依据为唯一管理表Q-02行；作者为[dock-control-research-01](dock-control-research-01-0041-20261024.md)。实查HEAD `5bbc331ab429fb76e956e50b8081c56f8d278b11`。已读reverse-design 3.1/3.2/5.1/7及[REA技能](C:/Users/cogic/.agents/skills/reverse-engineer-anything/SKILL.md)，采用留存优先、有界原字复核。仅写本报告及同名analysis；不改管理表、作者文件、ROM、生产配置或分析器，不开共享REA，不执行固件、模型、SIM、构建、刷机、网络，不提交推送，不建worktree、不派下级。所有shell显式workdir及login:false。

预估3–5分钟：定位不足1分钟、原字/数据流1–2分钟、报告1–2分钟；据同批3分15/3分26/4分24的充分定位复核校准。开始UTC `2026-10-24 16:02:41`，结束及实际墙钟见文末。token不可由本子任务取得，父窗采本轮实际input/cached input/output/reasoning，cached独列，不估算。

## 继承结论

P16/P17及[dock-control-review-01](dock-control-review-01-0041-20261024.md)的四入口同数组项、descriptor selector映射、请求与普通响应语义直接继承，不重做selector提取/getter/setter。E01/E02的同步借用、旧对象离线通知和deinit释放断边，B04/PR05的缓存非零门、phase/轮询后奏，B19/B21/NR01的普通parser/copy合同直接继承；本轮只核原payload来源、固定缓存边界、count和替换序列，不把已有段登记为新增。

原件`roms/0041/ap01-1.0.2_0041.bin`实查6,769,704B；SHA256身份继承`972db4c136c7ed9e24a83c07c1a7fd62040ca018b08ca285216d26b1fee3c6b9`，未重算整件hash。RV32 little-endian，offset=VA−0x9ffff000。

## 本轮复核或纠正

独立源码[review_static.py](../../analysis/dock-control-review-02-0041-20261025/review_static.py)直接读ROM及旧留存，不运行或导入作者collect_static.py。输出[review-evidence.json](../../analysis/dock-control-review-02-0041-20261025/review-evidence.json)保存原字、地址、留存指令与Capstone 5.0.7标准解码。四窗686B、208条指令边界与各自raw_ranges逐字相符，9个关键标准编码断言、3个厂商load寄存器字段断言通过；另人工核必要分支、调用目标及循环接缝。数量只说明本轮检查范围。

initializer来自`reverse/analysis/uiiface-lifecycle-0041-20261023/retained-initializer.json#/function`，Evidence `ev_6f9f82e5daf0540a1c24a0b85daa2e394785391692765e5e3e100eb7b37ed94c`，language `RISCV:LE:32:ap01thead3`，profile `bcefdee5092076e55636e077b45523e203f4b870ae7b7ab547945ed1b8162279`；原source `evidence/rea-0041-20261017/round3/evidence/whole-rom-round3-initial.evidence.json`，留存source SHA `689b060f96eaba167291ecf78c8998e5aea590555e793cac735d448265d1d385`。只验所选窗口，不认证完整6044B dispatcher及其警告范围。

helper另来自`reverse/analysis/uart-response-0041-20261023.json#/functions/1`，Evidence `ev_3a861f94ddb2b4481b6d96b4f46d593f35e2729ecb9022aa64949e92b607615c`，profile `b6368dd18431e8113aa5026c713d41e648ab0f6ddd9421ff6c4a49e23b3cd2f3`，source `evidence/rea-0041-20261017/evidence/whole-rom-uart-retry-20261023-001.json`。两来源/profile独立分账；callback旧profile仍未知。helper的copy/compare内部语义继承已验合同，本轮只核参数和通知输入边界。

| 验收项 | 结论与必要证据 |
| --- | --- |
| 原payload保存与恢复 | 接受。`85a8`原字`232ac4fa`为`sw a2,-0x4c(s0)`；`8a5c`为`lw s2,-0x4c(s0)`，`8a62`为`s2+=0x17`。cmd55由`8606`直接进88f6，原指针未替换成b004。 |
| 固定缓存与表来源分离 | 接受。`88fe`给a1=24，`8900`给a0=b004，a2=&frame视图；helper `1692/1694`取view+4及固定n，不消费view.length。固定缓存覆盖payload[0..23]，仅包含首descriptor。其余项直接按本次payload读取。 |
| count ff及重读 | 接受。`8950`读缓存byte22，`8966`在ff时跳8a22，绕过`898e`的b01c写入；`8996/89ba/89d4/89e0`均有必要重读。最终`8a22`读取u8 b01c为s3=N，之后沿该N重建。ff沿旧N，0仍进入撤旧和新总对象路径；本窗无≤4/5门。 |
| 原序填项，无排序 | 接受。`8aca`以完整i×424定位项，`8ad0/8aea/8b02`三次读s2+i，分组写I+0x24；`8b26`写u8(I+0x13)=i，`8b4c/4e`递增回8a64。三条厂商原字rd=a5/rs1=s1/rs2=s2字段独立核对；读取语义沿P16/Q已验合同，不新认证厂商ISA。 |
| 替换、发布、失败与借用 | 接受。`8a26`先call3d22 deinit，`8a2a/2e`申请380B，`8a36`先发布全局，`8a3c`为总对象NULL门；后申请N×424数组并存T+0，正常有效数组为填充前提，无独立数组NULL回滚门。`8a70`填完才写T+6=N，之后header/OTA/在线1调用。总对象失败时旧对象已撤销、跳过本块在线1；后续注册循环仍存在，不能扩写成整个handler提前返回。payload只在同步初始化期间借用，描述值复制入项，未把源指针存进项。离线通知/嵌套清理限制沿E02。 |
| 0x75含义 | 接受。helper按固定n比较/复制，在变化分支取view.cmd+0x20并截u8，55→75。即使固定前24B相同，caller后续仍可读取本次payload第24字节起不同条目；因此0x75只能代表固定前缀变化，不能认证全表变化。此为静态可达行为推断，不宣称实际发生。 |
| 输入extent与length | 接受。固定前缀需24B，正N条目从23起需N字节，合成源有效前提为max(24,23+N)。这是正常重建调用者须保证的可读/稳定寿命，未见本条路径用保存len验证该条件；不将推导冒称原程序length验证，不据此额外作异常输入结论。 |
| 条件恒等表 | 接受。沿P16映射，i=0/1/2须type0且nibble=0/1/2；i=3须type1，i=4须type2，后两者nibble任意；bit6无影响。映射最大5，i≥5不能满足selector=i+1。四正常入口仍需实际前四条值满足条件，单有本次来源定位不足以证明。 |

## 真正新增

业务新增0、技术纠正0、作者返工0。本轮新增仅为非作者验收证据：把作者报告中的原payload/固定缓存/旧count/替换顺序连接独立核到所选ROM原字及各自留存来源。标准分支的Capstone显示相对偏移，已按PC加偏移核回上述目标；不把相对数误当绝对VA。没有补造事务替换、代际隔离、远端成功确认或跨回调原子快照。

## 未闭精确边

完整接口未闭：**同一次真实cmd55响应payload[23..23+N)的实际条目值/顺序及count语义 → selector恒等条件是否成立**。现有RAM地址不是ROM常量，选中留存无实际响应，不能推真实物理端口顺序。唯一有种子的后续是有来源身份、len、N的既存同次响应字节或明确底座协议条目合同；拿到后逐项核条件即可，无需重做getter/parser/copy。没有这种材料时停于远端输入边界，不全ROM负搜、不转MCU、不搜无种子reader。

P16/P17已有控制结果、遥测因果/年龄与跨替换迟到关联继续未知；E02全局deinit不接逐项嵌套清理的限制继续保留。静态复核不等于设备执行观察。

本轮产物仅本报告、独立复核源码及本地ignored证据JSON。JSON可解析，限定文件尾换行/尾空白、引用存在及git diff --check结果见最终交付采时。未改共享表/作者文件，交付后停止。

UTC结束采时 `2026-10-24 16:05:04`；开始至结束实际墙钟143秒（2分23秒），充分定位后提前收敛，未凑预测时长。无主动等待、排队或中断；工具往返/读取包含于墙钟，未独立测量工具等待总量或有效工时。格式、JSON解析、5个本地引用及限定路径git diff --check均通过；报告/源码untracked，证据JSON ignored。父窗采实际token及cached input单列。交付后停止，不自行接后继。
