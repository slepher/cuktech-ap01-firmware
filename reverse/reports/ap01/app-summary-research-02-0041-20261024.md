# Q-01：同一摘要S的正常分类、五槽值及事件覆盖

**可独立使用阶段已闭合但接口未闭；作者交付待非作者复核，不能标已验。** 恢复 `0xa00adabc(app,item)` 在已构造、有效S上的本地正常生产合同：零分配初态→分类门→普通/非零类分支→同S当前槽→顺序事件覆盖→P-R11已验消费输入。直接生产值域为0/1/2/3/4；分类和后续mask可在一次通知内多次写同槽。全部外部writer、并发/重入和最终生命周期未闭，不把本地合同扩大为整个摘要接口完成。

作者 `/root/app_summary_research_02`；管理唯一表2026-10-24 23:54 HKT及Q-01行，实际HEAD `5bbc331ab429fb76e956e50b8081c56f8d278b11`。只写本报告及同名analysis，未改共享表/作者旧报告、生产代码、ROM、配置或分析器；未提交/推送/reset/clean，未执行固件、模型、SIM、构建、刷机、设备或网络，未派下级。全部shell用主树绝对workdir及login=false。按统一流程3.1/3.2/5.1/7和[REA技能](C:/Users/cogic/.agents/skills/reverse-engineer-anything/SKILL.md)复用留存，未打开/切换共享REA会话。

预测21–30分钟，中低置信：定位3–4、分类7–10、覆盖6–9、检查交付5–7；依据P18作者8分52秒/P17约6分钟，充分定位复核3–5分钟不作为本研究估时。首个可得UTC `2026-10-24 15:55:42`，结束及实际见文末。无主动等待、任务中断或排队；工具时间计入墙钟，无有效工时测量。token由父窗本轮实测累计，cached单列，本子窗不估算。

## 继承结论

- 先核父级 [application complete](application-rehost-complete-0041-20261017.md) 及 `reverse/rehost/system-complete-0041.json#/native_semantics/Power_bottom`：旧3秒互斥轮转及SIM推广已覆盖，后者明确未模拟原五槽精确编码。本轮不新增旧函数body，不把旧SIM/概念重计业务恢复。
- [P18独立复核](app-summary-review-01-0041-20261024.md) 接受正常port解码、child0→wrapper→S、活动零→非零当前槽清零、timer条件resume/reset及进入add16的门。[P-R07](offline-summary-review-pr07-0041-20261024.md) 接受离线清当前槽/同步tick/尾pause及FA/FB清理。[P19独立复核](app-history-review-01-0041-20261024.md) 已接受a008e362成功时按原size分配并fill0的公开API合同；不同对象仅复用该API语义，不把P19的P当S。
- [P-R11](summary-rotation-review-pr11-0041-20261024.md) 接受timer+c→同S、五槽求和但只前两槽作输出候选、游标和实参；[P-R13](summary-output-review-pr13-0041-20261024.md)/[P-R15](summary-pane-review-pr15-0041-20261024.md) 接受固定输出/布局。此处止它们已验输入，不重做选择或输出。
- 较晚P18/Q、P11/13/15明确保留此生产断边，未发现其认证完整条件和覆盖顺序；有限查重范围不证明全仓从未涉及。`theme-online-0041-20261023.md` 已留a00b2a48指示API调用，但未证明其内部有无五槽写。
- 原件沿CATALOG 0041：`roms/0041/ap01-1.0.2_0041.bin`，6,769,704B，SHA256 `972db4c136c7ed9e24a83c07c1a7fd62040ca018b08ca285216d26b1fee3c6b9`，RV32 LE，offset=VA−`0x9ffff000`；复用身份，只核长度/必要窗，不重算整件摘要。

## 本轮复核或纠正

唯一生产主体来源：`evidence/rea-0041-20261017/evidence/whole-rom-private-20261023.evidence.json#/records[parameters.procedure="0xa00adabc"]/normalized_result/assembly`，Evidence `ev_19e11c8fc1582881b289f2b24c2a98bbb305f7c2e57caad784442a60d1fb76e5`，Ghidra12.1.4、`RISCV:LE:32:ap01thead2`、profile `b6368dd18431e8113aa5026c713d41e648ab0f6ddd9421ff6c4a49e23b3cd2f3`。以assembly路径为准，原伪码的unreachable删块不能抹掉原指令路径。本轮无既验行为纠正；下述为新作者静态解释，未独立验收。

独立编写的 [audit.py](../../analysis/app-summary-research-02-0041-20261024/audit.py) 仅读原ROM/原留存，Capstone5.0.7静态解码标准指令，另按RV32/RVC位字段核直接控制目标、所有本轮直接槽store的寄存器/宽度/位移、关键load/常量。结果 [audit.json](../../analysis/app-summary-research-02-0041-20261024/audit.json)：24个稀疏窗982B/297条，131项数值字段检查PASS；人工结合原assembly顺序恢复数据流，不把检查数当完整语义证明。前两次自检发现窗口末端截进下一条指令（add90/de74），改至正确边界add8e/de72后通过，未改变业务结论。

## 真正新增

### 输入、对象及宽度

令正常port为p∈1..5、i=p−1，`S`为child0私有摘要上下文。字段 `C[i]=u8(S+0x101+i)`、`L[i]=u8(S+0x106+i)`；`K[i]=u8(0x62fc4041+i)` 为已保存类别。add16把i截u8供全局byte数组，S当前槽用原s5=i相加，K数组用继承的u16索引s8；正常域三者数值相同，不能据此改写异常索引ABI。

adcd4快照旧K到frame−e4，adcdc快照 `n=u8(item+e)` 到s9。item+c、+d、+21均LBU，item.word0及app+54为LW32事件mask；特殊n=0x15时读取 `A=LW(item+0x30)` 后 `q=LHU(A+8)`。A是借用指针，本层无NULL门，不复制该资源、不持有到S；q保留u16非零判定。一般类别不把item+21或+e预先统一成bool或枚举白名单。

分类总门（add16..38）：`u8[0x62fc4054+i]==1` 且 `u8[0x62fc4038]==1`。任一不满足直接ade8a，**后续事件阶段仍执行**。满足后，item+c==0走普通分类，任何非零走另一分支（本报告称“非零类/安心路径”）；后续0x10阶段只精确认item+c==1，不能把两处门统一为非零。

同S必要初态短差集按父窗指示并入本题，不另派：旧ctor record a005cc1e，Evidence `ev_2f6c46cd278b33760dc15702309279178fd3b14a0bef128e4814088addec2866`，同thead2 profile。原字 `d1a2:1305c010` 为a0=0x10c，`d1a6:ef10c31b` 的独立JAL目标a008e362，`d1aa:2a89` 保存返回为s2=S。沿P19已验公开zero_alloc合同，成功返回时S全0x10c为0，所以五槽C、L、F8/F9/FA/FB均为0。构造record从此到da78可见S直接store均是低位控件/状态以及S+f4 timer；d744/d748另清9c/a0；da14建立s3=S+80后da5e写+74即S+f4，没有明确覆盖f8..10b的store。S地址另传已验H、timer userdata；S+5c借给样式初始化API，止其公开对象域，未深入库。此结论限正常初始化/public API行为，不能升级为无重入/无越界/无外部writer证明。新增四个原字窗106B核caller/字段/登记接线，细节在audit.json；没有重复研究allocator内部。

### 初次分类到当前槽

| 路径 | 精确生产条件和动作 | 原指令锚 |
| --- | --- | --- |
| 普通类，n==旧K | 跳过分类及该段K写，直达事件阶段 | add60/64→ade8a |
| 普通类，n!=旧K但旧K!=0，或n==0，或n>0x20 | 不改C；仍SB n到K，再进事件 | add70..80→ade5c/60 |
| 普通类，旧K==0且1<=n<=0x20，n!=0x15 | 先执行本段通知/已有弹窗调用，清全局4054[i]；item+21非零则SB3到C，否则SB4。随后必要标签调用、SB n到K | adde6/ea、addee..addfc、ae43c..442、ade5c/60 |
| 普通类，上述门且n==0x15 | 清全局4067[i]；通知/已有弹窗；置全局4062[i]=1并清4054[i]；q非零SB3，否则SB4；随后SB n到K | ae4ee、ae536..554、ae5b4..5ba |
| 非零类，n!=旧K，n==0x15 | 同上特殊通知及全局4062/4054动作；q非零SB1，否则SB2；随后SB n到K | ae610..626、ae672..68e、ae6ec..6f2、ae864/868 |
| 非零类，n!=旧K，n!=0x15 | item+d==2时才执行附加详情快照/通知并清4054；无论该门是否成立，都按item+21非零SB1、零SB2，再SB n到K。不要求旧K=0或n在1..0x20 | ae752/758、ae7e8..806、ae912..918、ae864/868 |
| 非零类，n==旧K | item+d!=2直接事件；等于2时仍走详情快照/通知，清4054并SB1到L，但不在此段写C/K | ae990/996、aea26..a38 |

因此C=1/2是非零类的两状态，C=3/4是普通类的两状态；3/1对应一般item+21非零或特殊q非零，4/2对应零。类别更新不总会重新生产C：普通类旧K非零→新类别尤其保留旧C。C=0沿P18接入当前清零和P07离线清零继承；本轮不发明“任何离线通知都必归0”的最终状态保证。

已有弹窗路径会把12B/20B栈记录复制至另一栈记录后传私有构造/更新入口，并写弹窗+40为i，或调用无窗口fallback。这里只确认这些调用在C写之前及本地无返回成功判定；不追该对象所有权，不据本地copy证明callee不保留栈指针。满足正常有效调用前提后，两条弹窗分支均汇入同一全局/槽写。formatter/copy、GUI/弹窗、timer均止公开或既有业务边界，不展开库。

### 同一通知内的覆盖原序

以下按assembly实际先后，不是互斥else-if。E=当段重读item.word0，B=当段按需重读app+54；简化mask只表达布尔门，**不表示同时快照、锁、原子读或清除app+54**。

1. **0x60事件门，ade8a..adecc。** 概念门为`((E|B)&0x60)!=0`，实际先测E&0x20，再按需读B及两者0x40。若L==1、item+d==2、入口快照旧K==0、入口快照n!=0，则SB2到C，随后SB0到L；其他条件不写。分类刚写1/3/4仍可能被这一步改2。L在本层不是每次通知都清。
2. **0x8840事件门，aded0..ae04a。** 原序先测E&0x800，再按需以(E|B)&0x8040及B&0x800补门。当前C为2或4（`((C-2)&0xfd)==0`，C为LBU）时，重读item+e；若等于0x15，以q非零为资格，否则要求重读item+21非零且重读item+e非零。资格满足则2→1、4→3（adf26/2c、aea74/7a/7c）；不满足保留原值，**不对1/3反向降级**。随后本地标签刷新不写C；再重读C，若1/3且入口旧K==2，重读类别在[3,15]或[22,33]时刷新标签并SB入口快照n到K（adfb2..adff4、ae048/04a）。后一次缓存写不是新快照类别值。
3. **0x8事件门，ae04e..ae06c。** 调`a00b2a48(S,u8(i),saved_input_halfword!=0)`；第三参来自入口早期`adc18`的LHU(item+a)，`adc1c`将其SW32保存到frame−e0，`ae05e`只LW重读该栈快照，`ae062/064/066`再规范为0/1。它不是0x8阶段现读item+a，与各事件阶段按需重读E/B的时点不同。这是同S的必要中间依赖，未跳过假设其无副作用；见下段边界核查。此调用后仍继续后续事件。
4. **0x10事件门，ae11e..ae162及aef82..af01e。** E或B的bit0x10非零才处理；只p==1/2改槽，p3..5跳过。若item+c==1，4→2、3→1；否则2→4、1→3。每次先调用已验`U=a00abbf6(S,mode,bank,k)`，返回后才SB新C；无U成功检查。p1 k=0、p2 k=1；向1/2转换bank=2且mode为旧3/4，向3/4转换bank=1且mode为旧1/2，下面C2例外必须保留。该阶段在前两次覆盖后重读当前槽，因此是最后本地槽覆盖。

**C2兼容细节：** p2、item+c!=1、C2==1时，`0xa00af00e`实际LBU **S+0x101（C1槽）** 到a1，调用 `U(S,C1,1,1)`，随后C2写3。不能“修正”为传C2旧1。p2、item+c==1、旧C2==3时，aefec直接SB s8（刚读item+c，已精确等于1），不是借未知循环寄存器。p1与p2动作表由原字段确认，本轮不重验U内部。

### 0x8中间helper的最小业务边界

父窗确认该依赖仍在Q-01同S授权范围。旧`whole-rom-paths-20261023.evidence.json` list_procedures Evidence `ev_50cdbf92a7c9800e4d4bc140d70fa8cd1509eca7a199cfd6050d483cf7d695b2` 给出a00b2a48及下一入口a00b2d6a；不是新Ghidra反编译。本轮仅原ROM边界静态检查802B/239条，69个直接store全为s0/sp栈槽；25个direct JAL只到a00dfc1e/a019d0e6样式API，无间接call，c.jr仅ra返回。其S+低位widget读取/样式设置不直接写五槽或L；细节保留audit.json的store/call清单，未另导完整helper。

此为**直接业务写边界**，公共样式API仍有对象样式副作用；停止其内部，不证明GUI重入、任何第三方callback或并发writer均不改S。S/item/借用A需在同步调用期间有效，本地不分配/归还S或A，不把借用关系推为唯一owner。输出标签/布局会插在槽写之间，不能实现为“先一次算好最终C，再统一输出”的事务。

## 未闭精确边

1. 本轮正常生产阶段可按上述有序转换实现。原先考虑的S初态断边已依父窗提供的P19公开zero_alloc已验合同及本轮真实caller必要原字在同题补齐，不再作为新研究任务。未证明所有后续通知/并发路径仅由本轮生产者写槽；完整运行寿命和全writer唯一性仍未知，不能用“合法值域”承诺任意外部写后仍合法。
2. event0x10之后aee86/后段通知、child1等业务，以及所有全局writer/并发/重入/销毁未纳本题。原record targetless/computed调用不完整限制保留；本地直接写穷举不能证明全ROM唯一生产者。现有P18、P07和本报告组合仍不保证实际下一tick时刻、物理屏幕成功或最终退出。无错误/超时/取消/回滚返回合同可凭本层补造；正常调用前提失效的行为未知。
3. 非作者复核建议合并核本轮全部差集：普通/非零类不对称门、特殊q的LW→LHU借用、相同类别L延迟分支、0x60→0x8840→0x8→0x10次序/重读、C2借C1 mode、缓存写与槽写区别、a00b2a48直接store/call边界、同S 0x10c zero_alloc初态接缝及全部外部副作用未知限定。已验P18/P07/P11/13/15/P19仅作必要前提，不重开主体。目前没有经过查重且足够独立的同摘要新后继；不凭aef16 child1或全writer未知机械新派。下一动作是本批非作者合并复核。本作者交付后停止，不自行接后继。

交付检查结束UTC `2026-10-24T16:07:21.046+00:00`，从首个可得UTC计算墙钟 `699.047秒`。预测21–30分钟偏高；原留存已完整定位、多条路径在同一record，公共边界复用较充分，实际提前收敛，不等待凑时。必要初态短差集已在本题合并。静态读字合计1890B（主生产982B/297条，必要指示helper802B/239条，ctor106B/30条）；131项显式字段/直接目标检查PASS，另helper栈store/call边界断言通过，不把这些数字当完整证明。全部本地报告引用、JSON解析、三文件尾换行/无尾空格检查PASS；限定路径git diff --check无报错（新文件另由手工格式脚本核验）。无主动等待/排队/任务中断；工具启动/读取与自检修正含于墙钟。首次reverse-design相对路径未命中及一次较宽工具预览截断均未作为完整证据；已按精确record/窗口读取，不重复生产分析。Token由父窗本轮实测统计、cached单列，本子窗无数值不估算。独占产物为本报告、audit.py、audit.json（本地忽略材料仍留原路径），未暂存/提交/推送，交付后停止等待同题修正。

同题非作者修正（待复核者确认）：0x8指示helper第三参原先简写为`LHU(item+a)!=0`，未明确读取时点，现纠正为入口早期`adc18→adc1c`保存的u16栈快照，在`ae05e`加载后由`ae062/064/066`规范bool；E/B事件门仍是各阶段按需重读。仅原件两窗26B/9条逐项核原字/加载宽度/寄存器和bool实参，见[snapshot_parameter.py](../../analysis/app-summary-research-02-0041-20261024/snapshot_parameter.py)及audit.json的`indicator_argument_snapshot_correction`。audit.py同步接入该函数以保持未来生成一致；本次只运行该差集脚本，没有重跑131项整批检查。原交付计量保留，修正核查首个可得UTC `2026-10-24 16:09:37`，修正结束UTC `2026-10-24T16:10:25.559+00:00`；修正无主动等待，不扩对象/接口。四个独占文件现为报告、audit.py、audit.json、snapshot_parameter.py。修正后停止。
