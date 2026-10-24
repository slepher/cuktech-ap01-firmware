# P-R11：P-11 设备摘要选择状态阶段独立复核

**可独立使用阶段已闭合但接口未闭；P-11 选择状态阶段限定接受，行为纠正 0。** 接受 `0xa00ad602(timer)` 从 userdata 取 S、五槽低8位累加门、前两槽分派、单端 FA/FB 去重、双端 F8 交替、实际 helper 参数及本层返回状态。`0xa00abbf6` 内设备摘要消费和输出未验；不能据本阶段验收称完整摘要接口或应用生命周期闭合。

认领 P-11 的非作者复核 P-R11，复核者 `/root/pr11` 未参与作者成果。基线实际读得 `5bbc331ab429fb76e956e50b8081c56f8d278b11`，独占树 `.worktrees/batch-20261024-p/pr11`，仅写本报告及同名 analysis。只读主树 reverse-design、管理顶部 P 与 P-11 行、作者报告和必要证据；不改主树、作者成果或其他工作者文件。使用 [REA skill](C:/Users/cogic/.agents/skills/reverse-engineer-anything/SKILL.md)，只读留存/ROM/原模型源码，不开或切共享 REA，不修改模型。未执行固件、设备、网络、SIM/QEMU、回放、指令模型或构建；未改 ROM、生产、配置，未提交推送或创建代理。

预估约30分钟，问题收敛提前交付。首次可得 UTC 为 `2026-10-24 14:37:38`，实际结束及墙钟见文末；token 由父窗口统计，本任务没有实测值。

## 继承结论

- [P-07](D:/Documents/PlatformIO/Projects/cuktech-ap01-firmware/reverse/reports/ap01/offline-summary-p07-0041-20261024.md)及[P-R07](D:/Documents/PlatformIO/Projects/cuktech-ap01-firmware/reverse/reports/ap01/offline-summary-review-pr07-0041-20261024.md)已接受 S 的 child0 包装身份、`create(ad602,3000,S)` 与 S+f4、离线同步调用和后续条件 pause/SH0 清 FA/FB。本轮仅组合这些已验前提，不重计新恢复。
- `reverse/rehost/system-complete-0041.json#/native_semantics/Power_bottom` 的3秒互斥轮换概念直接继承。五槽和具体游标/实参合同属于本次 P-11 差集，旧概念说明不能替代它。
- [P-11 作者报告](D:/Documents/PlatformIO/Projects/cuktech-ap01-firmware/reverse/reports/ap01/summary-rotation-p11-0041-20261024.md)及其15窗574B/188条/86checks仅作为待验收说明和定位。本复核没有运行、导入或复制作者验证器；作者 JSON 不作为验收依据。
- 原件沿 [CATALOG](D:/Documents/PlatformIO/Projects/cuktech-ap01-firmware/roms/CATALOG.md)：0041 `ap01-1.0.2_0041.bin`，6,769,704B，SHA256 `972db4c136c7ed9e24a83c07c1a7fd62040ca018b08ca285216d26b1fee3c6b9`，RV32 little-endian，`offset=VA-0x9ffff000`。本轮验长度和必要原字段，不另建全件摘要账。

## 本轮复核或纠正

唯一 callback 原始留存为主树 `evidence/rea-0041-20261017/evidence/whole-rom-private-20261023.evidence.json#/records[parameters.procedure="0xa00ad602"]`，Evidence `ev_9a7754188b853599f5646fcd698e04fa0a888175362857916605f5ae6e3478f0`。独立核实际 provider 为 **Ghidra12.1.4**、language **`RISCV:LE:32:ap01thead2`**，profile digest `b6368dd18431e8113aa5026c713d41e648ab0f6ddd9421ff6c4a49e23b3cd2f3`；body 记载 `ad602..adabb`、1210B。没有将泛用 RISC-V 局限文字冒称为实际模型身份，也没有把 private profile 当作全部 ABI 的独立证明。

| 验收项 | 结果及可定位依据 |
| --- | --- |
| timer→S 与求和 | 接受。`ad61e` C.LW 从 timer+c 取 S；`ad648..67c` 初始 index/sum=0、上界5、S+101，循环 LBU、ADD、AND255。每次有日志 call，不能改写为原子快照、OR或五个候选。`ad680` 零和去 ada82，非零才在684/688重读102/101。 |
| 私有 lrbu | 接受。`ad65a` 原字节 `0b482d81`，rd/base/index=16/26/18，opcode/funct/上段与原模型匹配，shift=0；`ap01thead2.reg.sinc:1163` 指定 shift=(25,26)，`ap01thead2.sinc:6410` 构造读取 base+(index<<shift) 的 u8 并零扩展，无 base 写回。仅核该模型合同与原字段，不执行或重新认证整个厂商 ISA。 |
| 零和及只后3槽非零 | 接受。`ada82..daba` 依次 A(bc)、A(e4)、H(1,0,0)、H(1,0,1)、H(0,1,0)，跳公共返回；无本层F8/F9/FA/FB写。和非零但101/102均零时，单端枚举不匹配直接返回；没有扫描103..105的输出候选。 |
| 单端 FA/FB 与八组合 | 接受。各识别分支先读FB/写FA，再比较；相等到ad794仅清F9。不同才H/A/U，U返回在ad790写FB，再清F9。C1值2/1/4/3编号1/2/3/4；C2值2/1/4/3编号5/6/7/8。C2值2的编号5沿s2循环计数保留，不经ad690。无匹配分支到ad798，跳过F9清理。 |
| 单端 U 实参不对称 | 接受。C1值2/1/4/3分别 `(S,2,2,0)/(S,1,2,0)/(S,2,1,0)/(S,1,1,0)`；C2分别 `(S,2,2,1)/(S,1,2,1)/(S,4,1,1)/(S,1,1,1)`。`ad784..78c` 与 `ad8f6..8fc→ad78a` 明证状态4的code为2/4，不能按状态统一。 |
| H/A 顺序与字段 | 接受作者动作表。人工逐分支核原assembly中的 ad486/d8f7c 调用与 a0..a3 装参、bc/e4槽和公共尾跳转；C1 mode2布局使用k0，C2使用k1；mode1两端的隐藏/开启调用顺序保留。H开启实参被接受，H内部额外副作用仍未验。 |
| 双端门及F8 | 接受。两槽非零先 `ad94e/952` SH0909 到FA/FB，再H(0,0,0)，随后读F8。`ad968` 无符号判断<=1走C1；`ad9f8` 只认2走C2，>2直接公共返回，此时FA/FB和H已经改变；不自修F8。 |
| 双端读与输出 | 接受。C1 `ad998→H→ad9a6`、C2 `ada28→H→ada36` 均两次LBU。公共A/H先后为A(bc)、H(1,0,0)、A(e4)、H(1,0,1)；第一次slot读直接作H(slot,1,k)，第二次决定U。1/2用bank2，3/4用bank1，code保留slot。无效slot仍执行此前H，跳U但继续标签和切换。 |
| 标签、状态推进和返回 | 接受。C1用worda4/c0和地址a01c3bd8的C1，C2用wordcc/e8和a01c3bd4的C2；原字节 `4332000043310000`。C1写F8=2，C2经共享SB写1；双端本层不写F9。U返回无成功判断，FB/F8推进不等于显示成功。 |
| 离线调用组合 | 接受。普通tick与ae3ae同步call均进入同一ad602，没有按来源分流或读pause bit。本callback返回后，已验P-07两路条件pause及SH0使FA/FB最终为0；F8/F9只保留本callback所在分支实际变化。不能把普通tick单端FB值当离线尾最终值。 |
| 警告与控制流限制 | 接受。原record raw_result和normalized pseudocode均无unreachable字样，不移植其他函数的警告，不借伪码压缩省分支。无警告不证明所有间接边、ABI或全部writer覆盖；原record静态/未知间接边限制保留。 |

纠正项：**0**。未修改作者报告。上表接受范围为从选择输入到本层实际helper调用/状态返回，不接受下层U内部、H开启内部或成功显示。

## 真正新增与独立检查边界

新增业务恢复 **0**；本轮新增为 P-11 同一选择阶段的非作者验收。接口可用输入是正常有效 timer/S/widgets 与五槽状态，输出是上述按顺序发生的 helper 实参、FA/FB/F8/F9变化和返回。现有S/widget均为借用对象，本callback没有分配/free、timer删除或所有权转移；没有显式错误、超时、取消、创建失败/回滚门，不补造返回成功。没有证据证明U内部是否持有指针、调度串行性或最终物理显示。

独立源码 [audit.py](../../analysis/summary-rotation-review-pr11-0041-20261024/audit.py)及产物 [audit.json](../../analysis/summary-rotation-review-pr11-0041-20261024/audit.json)：仅 Python 标准库读取原ROM、原始留存和原profile模型源；**14稀疏窗522B/169条，311项数值字段检查PASS**。检查包括load/store宽度与寄存器/offset、RV32 branch/JAL目标、RVC立即数/跳转、私有word字段、0909及标签。每窗按原ROM低位求指令长度并校验端点，保存原字节与留存assembly；并非169条完整语义证明。必要动作块人工阅读原留存assembly，不把未列入稀疏字段检查的指令冒称已独立全解码。本脚本不调用Capstone、不运行作者代码或指令语义模型，不复验公共库内部。

## 未闭精确边

1. `ad78c/ad9bc/ada4c→0xa00abbf6(S,code,bank,k)` 的实际设备摘要字段、数据借用/持有、控件输出及失败仍未验；本轮只接受真实调用实参。建议后继仍为该有种子消费边，先由管理查重登记，非本任务自行承接。
2. H=`0xa00ad486` 的开启分支额外布局副作用、全部字段writer和合法状态来源仍未知；调用合同闭合不等于这些内部已验。
3. timer resume/restart/后续活性/销毁、并发、应用退出和完整摘要输出接口未闭；继承3秒轮换与P-07离线阶段不会填平这些断边。

结束 `2026-10-24 14:41:52 UTC`，从首次可得时间计墙钟约4分14秒；本题收敛提前交付。工具/进程时间计入墙钟，无主动等待或任务中断，不将墙钟冒充有效工时。最初登录PowerShell覆盖cwd造成只读未命中，随后login=false与绝对路径纠正；错误目录未写入。token父窗实测统计，本任务不估算。产物仅本报告、audit.py、audit.json；JSON、两条相对引用、空白和独占路径检查PASS。交付后停止，父窗负责保存整合及管理表更新。
