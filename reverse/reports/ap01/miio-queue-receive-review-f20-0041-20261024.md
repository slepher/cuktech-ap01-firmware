# F20：F11/6 finite非空接收、实际Msg长度与归还顺序独立复核

2026-10-24；基线 `bd457a6`，分支 `codex/re-0041-f20`；挂原认领 **F11/6**，非作者 `/root/g23`，F19作者 `/root/f12`已停止。**限定接受F19正常finite/nonempty合同，核心语义纠正0、复核新增业务0。** caller清localI后按同步链/queue门接收，忽略返回a0、重新读localI；下层pop得到Msg后以`(outI,Msg+0x0c,U16(Msg+0x0a))`调用copy，返回后才按Msg.kind归还。kind0/2回不同gp池，kind1才调用既有归还接口，不是全部Msg heapfree。

**实际copy长度保持Msg header读取值，不能替换为Q.size4。** 不认证某次send Msg与当前pop Msg同一运行实例、全部producer只写4B或实际I执行。F21共用helperbody没有重读；复核期间已收到[F22独立限定接受](miio-queue-message-source-review-f22-0041-20261024.md)，按其有效哨兵条件合同继承，不将K队列与gp池合成同容器。F19写作时待F22的记录按历史保留，不算语义错误。

已读主仓 [F19](miio-queue-receive-gap-f19-0041-20261024.md)、[必要合同](../../analysis/miio-queue-receive-gap-f19-0041-20261024/contract.json)与 [唯一管理表](rolling-management-0041-20261023.md#链条认领表) F20登记；遵循本批已读 [流程](reverse-design.md)、[保留规则](../../analysis/README.md)及 [REA技能](C:/Users/cogic/.agents/skills/reverse-engineer-anything/SKILL.md)。本轮直接核必要旧caller及原字段，不运行/导入F19或旧检查器，不以作者逐指令JSON替代原件。

没有目标/指令/模型执行、固件、SIM/QEMU、构建、回放、设备、外部服务或异常输入；不切换共享REA/修改profile、生产ROM配置模型、主树/共享表，无下级agent、提交或推送。clock、空队列等待、allocator/notify及新下层callee保持opaque，未读F21的42B helperbody。本文是静态合同及条件解释，非原源码/执行观察。

## 继承结论

|来源|继承内容|接受边界|
|---|---|---|
|[F11](miio-request-ownership-f11-0041-20261024.md)/[F12](miio-request-ownership-review-f12-0041-20261024.md)、旧upper-layer|同loop入口、I/type1分派及callback/free的既有合同|本题止于localI门到既有dispatcher，不重验R/P/S和业务回执|
|F13/F14、F15/F16、F17/F18|正常send、同Q setup size4及copy4有效word对齐域各有独立限定合同|不由这些合同认每个receive Msg.length恒为4，也不扩任意长度copy域/全producer|
|[F21](miio-queue-message-source-f21-0041-20261024.md)，F11/7|有效H时0xa010d70e取N=word(H+4)，正常修邻接、重读N+4、清N+4再N+0，返回N；空时0|F22已非作者限定接受，原有效性条件不变；F19 H=K+0x18，F21 H=gp+0xb8/c0，只共用算法，不认同节点运行实例或池大小|
|旧caller `upper-complete.evidence.json#/records/195`|owner0xa011e3d6，Evidence `ev_9a7e0a186c4ed2b341b4d42187fcb73bebec13d401cd226033d30027d121387d`，profile `4825fb58a33a3e7d618557975b153b8318cf7e833d190ad16bcbf8bd441ae621`|只读接收必要旧行，不重导708B线程函数或完整大Evidence|

原件沿 [CATALOG](../../../roms/CATALOG.md)：AP01 `1.0.2_0041`，主仓`roms/0041/ap01-1.0.2_0041.bin`，6,769,704B，继承SHA256 `972db4c136c7ed9e24a83c07c1a7fd62040ca018b08ca285216d26b1fee3c6b9`，映射`file_offset=VA−0x9ffff000`。本轮核长度、不重算hash，不混0031/SIM。F19所列extent/directcall只沿历史定位，不冒充新REA分析或完整body合同。

## 本轮复核或纠正

记L为loop，Q=word(L+0x18)，F=word(Q+0x0c)，K=word(F+0x18)。outI是caller的`s0−0x34`，outMsg是finite服务自己的`s0−0x24`，Msg是K队列摘出的内部节点，I则是payload值所指的invocation。**Msg+8的池归还kind与I+8的dispatcher type不是同一对象字段**。

独立 [review.py](../../analysis/miio-queue-receive-review-f20-0041-20261024/review.py) 用Capstone 5.0.7离线RV32/RVC；JAL/AUIPC-JALR、关键访存宽度和B型门另按位核字段。结果见本地忽略的 [review-result.json](../../analysis/miio-queue-receive-review-f20-0041-20261024/review-result.json)，没有新REA Evidence ID；旧profile、私有规则及其局限分别保留。

|待审主张|独立必要证据|判定/限制|
|---|---|---|
|先清localI、无同步头才native receive|旧e518读L+0x2c，e51a SW0到localI，e51e零门；e5f2读同L的Q，e5f6以&localI为a1，e5fa调adapter|接受caller对象/槽身份，非同步分支不与native内部Msg混同|
|实际timeout与caller忽略状态|旧e408/e416构成s7=0x2000+0x710=10000，e5ec默认取s7或e5f0取firstTimer+4；e5fe直接跳e548重读localI，零回loop、非零读I+8|接受值来源/返回消费；不由a0=0推出任何I已收到|
|finite参数、长度、deadline及符号返回|f51e BNE −1→f53c，原outI存s3；f592读word(Q+0x18)作a2，f596/59a/59c置deadline/outI/Q，f59e/5a2独立解到a0197954；共同f536 SRAI31|接受finite输入与0/−1折符号；−1服务/任意timeout及clock内部不展开|
|正常非空K队列门|a0197986/798e从Q+0xc和F+0x18取K，79ba保留outI，79c2取K+0x1c与79c6的K+0x18 sentinel比较；79ca非等到7a2e|接受本次K/非空门；并发或此后变化未知，不认同gp池|
|pop的outMsg接口与status门|7a2e/30/34传(K,word(Q),&localMsg)，7a36 JAL到a01319e8；7a3a保存status，7a3c/40先调opaque控制服务，再7a44判断status；0才读localMsg|接受中间调用原序，不省略其副作用边界；不把服务名当调度保证|
|Msg来源/输出与长度保留强度|a0131a06/14以H=K+0x18调已继承helper；1a1a保存返回Msg；LH K+0x22、−1、SH回后，可选notify，再1a3e SW原Msg到outMsg、1a42置0|接受本体保存/传回同指针；本体未写Msg+0xa，继承helper只清链word0/4。opaque notify/别名/并发可能影响字段仍未知，不作全程不变认证|
|copy实际len和归还顺序|7a56为**LHU Msg+0xa**，7a5a源Msg+0xc，7a5e目的outI，7a60长度；7a62/66独立解到copy；返回后7a6a置a0为原Msg、7a6c调release|接受实际读取长度与接口原序；不是复制整个Msg，也不是把Msg指针直接存localI；copy效果须满足相应已验域|
|kind0/2回池|a0131b68 U8(Msg+8)；kind0用gp+0xb8，kind2改gp+0xc0；共用四次word写依次Msg+4=sentinel、Msg+0=oldFirst、oldFirst+4=Msg、sentinel+0=Msg|接受两哨兵分别回链；不推池初始化、节点容量、独占/往返运行实例|
|kind1归还接口|1b94/96检查1；1b9a/9e独立解到a002e14e，a0仍原Msg，之后返回；其他kind进诊断边界|接受接口实参，不解释heap完整算法/物理释放；不是所有Msg都free|
|正常return|7a70 LH K+0x10，7a74 signed非正到79f0恢复mstatus；7a00把当前s1作a0。成功copy后s1为actual_len，pop错误则是保存status；adapter再折符号|接受所选直接正常尾；正waiter门的wake/其他分支保持opaque，caller依旧只按localI门分派|

### th.mula与deadline的条件解释

`0xa005f56a`原字 **8b97d420** 在Capstone保持UNDECODED。独立字段`(op,f3,top7,rd,rs1,rs2)=(0x0b,1,16,15,9,13)`匹配只读私有`ap01thead2.sinc:25`的`:th.mula rd,rs1,rs2`，规则为`rd=rd+(rs1*rs2)`。没有执行模型、改成NOP或声称独立厂商规范认证。

只在该既有局部规则成立且opaque服务正常返回的前提下，adapter的普通DIVU/REMU与此word说明：局部第一word加timeout DIVU1000，第二word累加timeout REMU1000与1000000的乘积；随后按原signed阈值999999999最多调整一次。复核接受的是传给opaque服务的局部输出地址、之后的读取/运算及deadline指针转交，**不认证该服务实际填充值/clock单位、时钟来源、任意timeout规范化或全值域行为**。此算术与Msg.len身份没有替代关系。

核心语义纠正0。F19最终报告已经区分调用事实/实际复制、Msg.len/Q.size以及正常/opaque边界，本复核只接受该限定强度；没有用同kind、同size或相同gp表达式消除对象身份与运行时差异。

## 真正新增

复核新增业务 **0**、F21 helper本体 **0**、copy算法域 **0**、ISA/来源排除 **0**。交付为非作者对F19正常finite/nonempty差集的限定接受和独立原件/字段索引，旧generic type1 dispatcher不重复恢复。

若当时actual_len确为4、Msg.payload与outI满足F17/F18有效word对齐等已验域，则可条件推导localI获得payload中的四byte指针值；本题未证每条Msg的长度/producer/地址域，更没有看到运行。Q.size4、发送端同形Msg或pool申请值不能代替这些前提。copy在归还之前返回只是原序事实，不证明I对象最终执行/存活或copy全输入安全域。

## 未闭精确边与实际检查

仍未知同次send/pop Msg身份、全部producer/Msg+0xa writer、actual_len4全域、payload/outI容量/对齐/分离及I寿命、gp池初始化/复用/容量、实际等待/超时/clock/控制/唤醒服务、诊断返回与真实consumer/业务成功。F22已独立限定接受F21，容量/GP实例/稳定等前提不变，本题没有重验；K+0x18与gp两池只共享helper，容器保持分离。

本路实际 **135项独立旧caller/原字段检查PASS**，包含三组AUIPC/JALR、三条JAL、六个B型门、关键U8/U16/LH/SH/word访存及一条厂商实例/既有规则；没有运行F19/旧脚本、重读a010d70e body或读取新heap/clock/wait/helper正文。JSON解析、相对链接、Git忽略、独占文件与diff检查通过。生成JSON留本地原路径并忽略，报告/源码未提交推送。

有种子后继保持F19原建议：同Q producer到**pop Msg+0xa**写入者/实际长度身份桥；管理窗口须先查重登记，不能由已有SH n或Q.size4直接给全部receive补4，也不能复派本次相同消费原字当新增。
