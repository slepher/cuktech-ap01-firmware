# Q-01 同S分类与事件覆盖的独立复核

**可独立使用阶段已闭合但接口未闭。Q-01本批差集限定接受；读取时点措辞纠正1项，作者修正后已独立确认。** 正常有效S的零分配初态、普通/非零类分类、当前C/L槽及顺序事件覆盖，可作为接到P-R11输入的本地生产合同。全writer、公共API重入、并发及最终生命周期仍未闭，不能将本结论登记为整个摘要接口完成。

复核者`/root/app_summary_review_02`为本批非作者；管理表Q-01行已登记。实核HEAD `5bbc331ab429fb76e956e50b8081c56f8d278b11`。读取reverse-design的3.1/3.2/5.1/7及[REA技能](C:/Users/cogic/.agents/skills/reverse-engineer-anything/SKILL.md)，沿同题有限边界复核。仅写本报告及同名analysis；主树独占产物，不创建worktree，不改共享表或作者成果、不提交推送/reset/clean，不撤销他人成果。不执行目标、模型、SIM、构建、回放、刷机、设备或网络，不修改ROM/生产配置/分析器，不创建下级或打开/切换共享REA会话。所有shell显式主树workdir及login=false。

预测6–9分钟：定位1、分类覆盖3–4、helper/初态1–2、报告1–2；参照作者699秒及前批短复核195–264秒，差集较大但原留存已定位，提前收敛即交付。UTC首可得开始`2026-10-24 16:08:18`。父窗日志提供中断工具发出`16:09:41.533`、恢复followup发出`16:10:46.773`，间隔65.240秒；这些是调用发出时刻，并非有效工时边界。中断期间作者完成本题修正，恢复后本窗只核修正差集并继续尚未完成的独立原字检查。结束和墙钟见文末；工具读写/启动计入墙钟，没有有效计算工时测量。token由父窗实际遥测统一记录，cached单列，本窗无数值不估算。

## 继承结论

- [P18独立复核](app-summary-review-01-0041-20261024.md)的正常port、child0→wrapper→S、活动零→非零清当前槽、timer条件resume/reset、进入add16门直接继承；[P-R07](offline-summary-review-pr07-0041-20261024.md)离线清槽/同步tick/尾pause亦继承，不重做接入。
- [P-R11](summary-rotation-review-pr11-0041-20261024.md)的timer+c→S、五槽求和/前两槽候选与选择，以及[P-R13](summary-output-review-pr13-0041-20261024.md)/[P-R15](summary-pane-review-pr15-0041-20261024.md)的输出/布局继承。本批止它们的输入，不重算选择或输出。
- [P19独立复核](app-history-review-01-0041-20261024.md)已验a008e362按原size分配并fill0的公开合同，只复用API语义，不将P与S混为同对象。[作者本批](app-summary-research-02-0041-20261024.md)为待验命题与定位来源；没有执行或导入作者audit.py、snapshot_parameter.py，也未用作者断言通过替代独立判断。
- 原件沿CATALOG身份：`roms/0041/ap01-1.0.2_0041.bin`，6,769,704B，SHA256 `972db4c136c7ed9e24a83c07c1a7fd62040ca018b08ca285216d26b1fee3c6b9`，RV32 LE，offset=VA−0x9ffff000。本窗核长度及必要原字，不重算整件hash。

## 本轮复核或纠正

生产与ctor原assembly来自`evidence/rea-0041-20261017/evidence/whole-rom-private-20261023.evidence.json`的对应records：adabc=`ev_19e11c8fc1582881b289f2b24c2a98bbb305f7c2e57caad784442a60d1fb76e5`；a005cc1e=`ev_2f6c46cd278b33760dc15702309279178fd3b14a0bef128e4814088addec2866`。独立核profile digest均为`b6368dd18431e8113aa5026c713d41e648ab0f6ddd9421ff6c4a49e23b3cd2f3`，沿Ghidra12.1.4/RISCV:LE:32:ap01thead2来源。本次以原assembly和ROM为准，反编译的unreachable删除不能否认指令路径。

| 差集 | 独立验收 |
| --- | --- |
| 对象/位宽及分类总门 | 接受。正常i=p−1时C=S+101+i，L=S+106+i，均byte；K=62fc4041+i。add16仅给全局数组截u8，S用原s5、K用s8；不推广异常索引等价。add24/2c两个精确等于1的门失败只跳到事件阶段；item+c为0/非0决定分类，而0x10阶段是精确等于1。 |
| 普通类不对称门 | 接受。add64相同类别直接事件，不写分类K；不同类别仅旧K=0、1≤入口n≤0x20才生产。普通类别读item+21非零写3、零写4；n=0x15经LW(item+30)→LHU(A+8)判非零写3/零写4。旧K非0、n=0或>0x20保留C，仍经ade60写入口n到K。 |
| 非零类与延迟L | 接受。ae614相同类别转ae990；item+d=2才通知/清4054并在aea34写L=1，不写C/K。不同类别无普通类的旧K=0/范围门：特殊0x15按q写1/2，其余按item+21写1/2，即使item+d!=2仍生产；K从入口s9写入。 |
| 0x60覆盖 | 接受。ade8a开始重新LW事件，按需LW app+54；L=1、item+d=2、旧K快照=0且入口n!=0才在adec8先SB2到C，再在adecc清L。没有每次通知清L的保证。 |
| 0x8840覆盖及K | 接受。aded0再次LW事件，不与0x60共用一次快照。C为2/4才按重读类别/资格单向变1/3；特殊q是LW→LHU，不截成byte。adfb6又重读C，旧K快照=2且重读类别属于[3,15]或[22,33]时可刷新标签；ae04a写回的是入口s9，不是该段重读类别。 |
| 0x8实参时点纠正 | 原报告第3步用LHU(item+a)!=0简写，未说明时点，已交父窗转作者修正。独立原字确认adc18为LHU a5,item+a，adc1c为SW a5,frame−e0；ae05e是LW此快照，ae062先a2=0、ae064零分支、ae066非零置1；ae068/06a传u8(i)/S，ae06c调用helper。现报告明确早期快照，接受修正版。不能实现成helper调用前重新读取item+a。 |
| 0x10最后本地覆槽 | 接受。ae11e再次读E，按需读B；只p1/p2写槽。item+c==1做4→2/3→1，否则2→4/1→3；每次先U(S,mode,bank,k)，返回后SB，无成功判定。af00e原字段确为LBU a1,S+101：p2从C2=1向3时借C1作mode；aefec则SB s8到C2，该s8已精确等于1，不能替换为未知循环值。p3..5不在本阶段直接覆槽。 |
| 同S helper边界 | 接受限定边界。旧paths bundle的list_procedures Evidence `ev_50cdbf92a7c9800e4d4bc140d70fa8cd1509eca7a199cfd6050d483cf7d695b2`给出a00b2a48及下一入口a00b2d6a。独立ROM/Capstone解802B/239条，69个直接store均以s0/sp为栈基址；25个JAL只到a00dfc1e/a019d0e6；没有间接call，c.jr仅ra返回。直接指令不写C/L不等于样式API没有对象副作用或重入writer，公共API内部停止。此处没有新helper REA assembly Evidence，不能冒标为上述adabc同源记录。 |
| 同S构造初态 | 接受必要短接缝。d1a2原字1305c010传0x10c，d1a6 ef10c31b独立JAL得a008e362，d1aa 2a89保存a0为s2=S。沿P19已验zero_alloc，成功时f8..10b及五C/L均0。原ctor d1aa..da78的直接S stores为低位widget/state及f4 timer；da14令s3=S+80，da5e写+74即S+f4，没有直接覆盖f8..10b。S+5c交样式初始化及S交H/timer依公开/既验对象边界理解；不由局部store穷举证明公共callee绝无越界、重入或所有外部writer。 |

四阶段次序接受为0x60→0x8840→0x8 helper→0x10。中间标签/样式调用仍发生，不能将它改写为只算一次最终C后统一输出的事务。C本地直接生产域0/1/2/3/4，0沿既验在线/离线清槽；不承诺外部写后或下一tick时刻仍满足此值域。S/item/A均为本层同步借用；特殊A不复制、不持有至S，本层无A空指针恢复门。没有本地S/A释放，也不能补造所有权独占、失败回滚、超时或取消合同。

## 真正新增

新增业务恢复0；新增非作者限定验收与1项读取时点纠正。独立编写[review.py](../../analysis/app-summary-review-02-0041-20261025/review.py)，只读原ROM、原留存，Capstone5.0.7解标准指令；另独立位字段解I/S、RV32 JAL/branch、RVC条件/无条件跳转。[review.json](../../analysis/app-summary-review-02-0041-20261025/review.json)保存稀疏原字、对应原assembly、原字段/目标检查及helper store/call清单。未复制或导出完整adabc/ctor，不做全ROM负搜。ctor直接store观察来自原留存的限定构造区段；不把稀疏原字覆盖说成重验整函数。

实际原字1936B/583条（含helper802B/239条）；本窗独立131项字段/目标/边界断言PASS，编号数量与作者131项偶合，内容与覆盖不是继承作者脚本。helper另核69直接栈store/25 direct JAL。首次自检发现选ctor窗d674位于d672四字节store中，改从d672起，随后指令边界及留存地址一致；未改变业务解释。一次读取paths记录按dict访问失败，纠正其normalized_result为list后核相邻入口，没有重复生产分析。检查数及解码字节数均不代表完整函数或完整接口证明。

## 未闭精确边

1. Q-01本批正常生产阶段接受；所有其他writer、并发/重入及最终销毁仍未知，不能用本地合法值域/直接store清单关闭完整摘要API。
2. 公共样式、formatter/copy、弹窗、timer止公开或既验边界；对象真实显示成功、下一tick即时性、callee是否保留借用栈记录等不由本批证据保证。原record computed/targetless调用覆盖限制继承。
3. 0x10之后aee86后段、child1及全局writer不在本批。本批不新增独立后继任务；若未来获得同S外部writer/销毁的具体caller或callback种子，再由管理窗口查重登记。不能仅凭全writer未知机械继续扫描。

交付检查结束UTC 2026-10-24T16:14:17.964181+00:00，从首可得UTC起墙钟 359.964秒。父窗中断/恢复调用间隔65.240秒单列；墙钟减此间隔仅为约294.724秒的活动区间估值，不当作有效工时。除此无主动等待、排队或任务中断；工具启动、原件读取、自检修正包含在墙钟。JSON解析、全部本地引用、三文件尾换行/无尾空格通过；限定路径git diff --check结果见交付消息。未暂存/提交/推送。交付后停止，由父窗更新唯一管理表。
