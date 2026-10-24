# P-R15：P-15 摘要 pane 开关及布局合并非作者复核

**可独立使用阶段已闭合但接口未闭；P-15 限定接受，行为纠正0项。** `0xa00ad486(S,kind,enable,index)` 的本题 kind0/1/2、enable0/1、有效index条件及原调用顺序可用于实现摘要 pane 的开关阶段。kind2 开启除撤flag1外另调相对布局。它没有提供测量数值生产、业务状态推进或 timer 活性合同；不能据此宣称完整摘要UI已恢复。

复核者 `/root/pr15` 非作者。独占树 `.worktrees/batch-20261024-p/pr15`，实核基线 `5bbc331ab429fb76e956e50b8081c56f8d278b11`；仅读主树，仅读管理顶部P规则及P-15行、reverse-design统一入口和必要继承记录。仅写本报告及同名analysis；不撤销他人修改。采用 [REA skill](C:/Users/cogic/.agents/skills/reverse-engineer-anything/SKILL.md)，复用留存；未开/切REA共享会话、未运行或导入作者验证器、未运行目标/设备/网络/SIM/QEMU/回放/指令模型/构建，未改ROM/生产/配置/模型，未提交推送或创建代理。预估约30分钟，可收敛提前交付；实际计时见末。

## 继承结论

- 原件沿主树 `roms/CATALOG.md` 的0041：`roms/0041/ap01-1.0.2_0041.bin`，6,769,704B，SHA256 `972db4c136c7ed9e24a83c07c1a7fd62040ca018b08ca285216d26b1fee3c6b9`；RV32 little-endian，ROM offset=`VA-0x9ffff000`。复核读取必要body字节，不重新建立整件哈希账。
- `reverse/rehost/system-complete-0041.json#/native_semantics/Power_bottom` 已有互斥可见和轮转概念，`#/local_disassembly/0xa00ad486` 已有body。新增函数体恢复0，不将旧概念计作新业务。该list实际延伸到后续函数；本复核按独立extent筛出 `ad486..ad601` inclusive 的380B/139条，而不把整个list当helper body。
- [P-R07](D:/Documents/PlatformIO/Projects/cuktech-ap01-firmware/reverse/reports/ap01/offline-summary-review-pr07-0041-20261024.md) 已验kind1/2关闭及kind0开启子集、同S离线清理；[P-R11](D:/Documents/PlatformIO/Projects/cuktech-ap01-firmware/reverse/reports/ap01/summary-rotation-review-pr11-0041-20261024.md) 已验H调用实参及caller选择/顺序，本复核不重做五槽轮转。
- [P-R13](D:/Documents/PlatformIO/Projects/cuktech-ap01-firmware/reverse/reports/ap01/summary-output-review-pr13-0041-20261024.md) 的固定资源/颜色/布局及公开GUI边界直接继承，其一般ANDI mask纠正仍有效。本helper不存在ANDI，也不因caller的LBU或别处mask而获得全局u8 ABI。

## 本轮复核或纠正

逐项复核作者主树 [P-15报告](D:/Documents/PlatformIO/Projects/cuktech-ap01-firmware/reverse/reports/ap01/summary-pane-p15-0041-20261024.md) 与同名analysis。独立 [review.py](../../analysis/summary-pane-review-pr15-0041-20261024/review.py) 仅Python stdlib，直接从ROM解析指令长度、JAL/B/C.J/C.B条件目标、LW/C.LW、ADDI/C.LI原字段；并核旧行字节、extent、旧raw inventory及来源profile。它只解释静态编码，不执行指令，不运行数据流模型，不替代人工路径复核。结果见 [checks.json](../../analysis/summary-pane-review-pr15-0041-20261024/checks.json)。

| 项目 | 判定与证据 |
| --- | --- |
| 来源与body边界 | **接受。** 380B/139条连续映射与ROM逐字节相同；旧body来源仍是 `Local Capstone5.0.7 and cached raw Ghidra evidence only; no new REA/network/provider calls`，不能改标本轮Ghidra反编译。独立coverage给出同extent。 |
| 原inventory/profile | **接受。** 在原bundle核 `ev_50cdbf92a7c9800e4d4bc140d70fa8cd1509eca7a199cfd6050d483cf7d695b2` 的raw_result确有ad486；provider Ghidra12.1.4、语言 `RISCV:LE:32:ap01thead2`、profile `b6368dd18431e8113aa5026c713d41e648ab0f6ddd9421ff6c4a49e23b3cd2f3`。该inventory身份与旧Capstone body来源分账，inventory不直接证明行为。 |
| kind门 | **接受。** ad494比较kind==2到ad5ba；ad498为无符号BLTU 2,kind到ad4da；ad49c kind==0到ad4f0，其余本题kind1到ad4a0。没有入口截u8。本题不扩大kind3/4合同。 |
| enable与index门 | **接受。** enable原寄存器零/非零决定增/撤flag；本题仅列0/1。kind1/2先精确index==0，第二组ad552/ad5e0精确要求1，否则到ad4e6返回；kind0忽略index。不能把任意非零index都归第二组。 |
| kind0关闭/开启 | **接受。** 原序54→58→4c；enable0逐个调d8f7c，enable1逐个调d9044。每次call处重新取控件指针；没有pane状态计数更新。 |
| kind1开启 | **接受。** index0原序a4,a8,ac,b0,b8,b4；index1原序cc,d0,d4,d8,e0,dc。s1在首对象加载后加80，后续压缩LW按新基址解释；最后一项经跳转共用ad51c的remove call。因此不能按基本块数替代每路径六次调用。关闭分支沿P-R07并与原行核对。 |
| kind2开启 | **接受。** index0先ad5c6撤bc flag1，再ad5ca重读bc到a1、ad5ce读c8到a0；index1先ad5ee撤e4，再ad5f2重读e4到a1、ad5f6读f0到a0。两组a2=2/a3=0/a4=30，第二组ad600跳ad5d8共用dbb68。API合同为 `align_to(W(c8/f0),W(bc/e4),2,0,30)`；关闭分支跳ad506增flag后退出，没有布局。 |
| 副作用及返回 | **接受。** 完整extent内29个直接JAL目标仅d8f7c/d9044/dbb68；三条store仅ad488/ad48a/ad48c的C.SWSP。全部载入/控制流人工复核未见S字段写、五槽/位图/计数读写、S+f4/F8/F9/FA/FB读取、timer调用、image source/color/text调用、分配/释放或所有权转移。没有API返回值成功判断或业务错误码。这里仅限制helper直接行为，GUI内部对象状态副作用仍存在。 |
| 组合与互斥语义 | **接受并限定。** P07关闭、P11选择和H调用、P13固定输出保留各自原序。H单次调用只作用所选组；它不自动关闭所有其他组，也没有事务、锁或原子切换。caller组合形成的互斥可见意图不能升级为helper原生原子互斥保证。 |

作者91条稀疏指令共256B均独立比对旧行和ROM相同；原报告5窗、19operand锚是作者检查组织，本复核以13个关键控制目标、kind2四条原加载和六条参数立即数另核，不把作者检查数量当独立语义证明。29个直接call及3个store原编码核对通过。旧extent Evidence为 `ev_6678985d6b6d758841b697143e265c7dd21849f3e62dd3003414dac127b6b02b`，direct-calls Evidence为 `ev_c6d769b0a37953b4f0cc4f46aad1923f8ac70cd056c4555cb7b84550dd6a1c7a`；原bundle定位主树 `evidence/rea-0041-20261017/evidence/whole-rom-paths-20261023.evidence.json`。未生成第二份完整反汇编。

行为纠正0项；作者记录的首个绝对UTC `14:55:30` 到交付检查 `14:59:02` 仅3分32秒已测区间，明确不是完整有效工时。其更早开始须由父窗派发/session创建记录补记，复核不估算补造。

## 真正新增

新增的是本题pane开关/布局差集的非作者接受：kind0关闭、kind1开启的逐槽原序，kind2开启在remove后重读对象并以2/0/30布局，以及本helper的直接业务副作用边界。旧body、互斥概念、P07关闭、P11选择与P13固定输出不重复计新增。

可实施的阶段合同仍需S和已有widget在同步调用期间有效，保留call间重读和原调用顺序。无NULL/类别门、超时、取消、回滚或返回值成功保证；这些空白不构成建议的新产品行为。可用公开GUI适配替代实现flag和align，未验证线程、构造销毁或实际屏幕效果。

## 未闭精确边

1. 实际测量/数值label更新来源、控件构造/全体writer、timer后续活性和销毁、并发及完整退出仍未闭。有限helper静态检查不能证明完整UI有活性或成功显示。
2. P-15提出的adabc内adc7c→bd70、adc84→c2d0后继仅按作者已定位种子保留，由管理窗口另行查重登记。本复核不读取其新后继、不重开timer内部，也不以含is_dead的旧value-flow记录证明现场可达。
3. 公开GUI、颜色、timer API为停止边界；本报告不认证原厂库版本或展开库内部。

检查收敛：本报告两条相对analysis引用解析、JSON解析、独占输出及diff检查另见交付记录。复核开始首个UTC为 `2026-10-24T15:01:17.6940294Z`；初始两次登录shell覆盖cwd造成只读未命中，之后显式Set-Location纠正，未在错误目录写入。一次宽预览被截断，随后按地址过滤，截断预览未用作完整证据。最终UTC/墙钟由交付记录保存；无主动等待或任务中断，工具等待计入墙钟，墙钟不等于有效工时；token由父窗实测统计。交付后停止。
