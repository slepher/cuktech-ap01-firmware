# F25：F11/9 invocation指针队列的条件寿命合同合成

2026-10-24；认领 **F11/9**，作者 `/root/a56`；固定基线 `bd457a6`，独占 `re0041-f25` / `codex/re-0041-f25`。主仓[唯一认领表](rolling-management-0041-20261023.md#链条认领表)已登记只合成已独立接受的正常接口。遵循[流程](reverse-design.md)、[本地保留规则](../../analysis/README.md)和REA技能的证据边界；不新读ROM/helper、运行技术脚本、目标/固件/指令/模型、SIM/QEMU、构建、回放、输入实验、设备或外部服务，不切换共享REA/改生产配置模型或共享表，无下级agent、提交推送。

**在下列明确前提下，native队列传递的是heap invocation I的4B指针值，既不深拷贝I，也不深拷贝R。发送copy返回时，本数据通路对发送方局部I指针槽的直接借用结束；I对象仍须存活。接收copy把该值写入另一个局部I槽后，先归还内部Msg，再由caller重读/分派I；选定type1 executor正常返回0之后，才沿既有合同本地归还I。** 这是一组条件静态连线，不是某次实际投递、存储条件或调度已成立的证明。

本项把原F11 native队列opaque边在**成功到copy/receive的限定域**内连起来。并未全局关闭native队列：实际Msg身份/len、全producer、有效容量/对齐/分离、后续writer、等待/调度及实际执行仍有限制。作者合成待F26独立复核。

## 继承结论

|已独立接受来源|本项引用的合同|不能外推的部分|
|---|---|---|
|[F11](miio-request-ownership-f11-0041-20261024.md)/[F12](miio-request-ownership-review-f12-0041-20261024.md)|R与heap I分别构造；I.payload保存ctx/R；异线程submit传局部I指针槽地址；generic type1 executor/本地I清理合同|不重构造/回执，不补R消息与R对象同寿命，不把native opaque旧语句当永远不可推进|
|[F13](miio-native-queue-f13-0041-20261024.md)/[F14](miio-native-queue-review-f14-0041-20261024.md)|实际source=&局部I槽、n=word(Q+0x18)；先SH n到Msg+0x0a、copy(Msg+0x0c,source,n)，copy返回后才发布Msg/更新计数|仅选定正常到copy/共同返回的路径；adapter返回0本身不证明已发生copy或consumer执行|
|[F15](miio-queue-size-gap-f15-0041-20261024.md)/[F16](miio-queue-size-review-f16-0041-20261024.md)|同Manager正常setup/config/thread及matching-thread attach，把ctx0/1+4接到L、L+0x18接同Q，Q+0x18初值4|初值不证明某次send的实际n、无后续writer、所有queue尺寸或真实线程执行|
|[F17](miio-queue-copy4-f17-0041-20261024.md)/[F18](miio-queue-copy4-review-f18-0041-20261024.md)|n4且正常有效word对齐等前提下，4次交错byte读写，返回原dst，无直接参数地址持有|不是原子4B快照，不覆盖任意长度/干扰/重叠；指针值复制不retain/deep-copy其对象|
|[F19](miio-queue-receive-gap-f19-0041-20261024.md)/[F20](miio-queue-receive-review-f20-0041-20261024.md)|finite正常非空pop，copy(outI,Msg+0x0c,U16(Msg+0x0a))，之后按Msg.kind归还；caller忽略状态并重读localI再分派|实际len来自Msg，不替换为Q.size；不认证当前Msg就是某次send节点或全部producer写4B|
|[F21](miio-queue-message-source-f21-0041-20261024.md)/[F22](miio-queue-message-source-review-f22-0041-20261024.md)|只继承getter两gp链/条件申请及有效哨兵摘节点算法；receive的K队列是不同容器|非零Msg/332B请求/相同helper不认证实际容量、对齐、独占、寿命或pool与queue同对象|

**F23/F24待验依赖单独隔离。** F23的状态服务、caller新回边及对F21/F22整体flag guard覆盖强度的纠正，合成时仍待F24；本项不提前标已验，也不采用F22机器合同的 `caller_flag_condition` 作为所有正常前驱的全局前提。F22已验getter/list_helper本体可继续引用。本合同从“选定正常发送确已到copy/发布”开始，不声称MiIO线程必走某flag值、哪条等待边或一定取得Msg；因此不依赖该待验服务闭合。F24进行中的T字段伪码原序精确化也未被本项拿来补调度/等待证明，冻结F23文件未改。

原件身份仅继承上述合同/[CATALOG](../../../roms/CATALOG.md)：0041 `ap01-1.0.2_0041.bin`，6,769,704B，既有SHA256 `972db4c136c7ed9e24a83c07c1a7fd62040ca018b08ca285216d26b1fee3c6b9`，VA映射`VA−0x9ffff000`。本项不打开ROM、重算摘要或产生新REA Evidence ID/profile；各原字段/旧Evidence/profile沿来源保留，合成不是新字节观测。

## 本轮复核或纠正

本项没有重核任何原指令，不冒充非作者验收。需要收紧的合成用语是三点：

1. **Q.size4与pop的Msg.len4是两个条件。** F16给同正常初始化状态的size初值，F14给send时SH n到当次Msg；F20的receive仍重新LHU实际Msg+0x0a。只有匹配同次Msg且该header/payload未变，或另有证据给本次actual_len=4，才能接F18。不能由Q.size、相同kind或某个相似producer直接给所有receive填4。
2. **逻辑对象不同不等于物理存储已分离。** Msg、I、R、send槽、receive槽及内部outMsg都须分别列出；地址表达式不同不能代替有效存储/容量/对齐/非干扰及所需分离的证明。
3. **归还接口先后不等于已观测物理free。** Msg.kind0/2是回池写链，kind1调用既有归还接口；I是在正常executor返回后走另一对象的归还。不能笼统说“先free所有Msg再free所有I”，也不能把callback返回1的持有转移路径并入本例。

既有合同中的“未知native队列”在各自历史时点有相应范围；本轮只连已验差集和显式前提，不静默改写冻结F11/F13/F19或旧机器合同的历史pending状态。

## 真正新增：条件连线与寿命边界

### 对象与三个局部槽

|对象/槽|具体含义|寿命/责任|
|---|---|---|
|Manager|F16的同setup实例，L=Manager+0x128，两个ctx=Manager+0x174/+0x968|不是内部消息Msg；其有效/后续writer属于前提|
|R|独立heap请求，含其消息指针，I.payload中保存R指针|queue不复制R；R对象/R消息寿命按F11，不能跟Msg或I一起归还|
|I|独立heap invocation，payload={ctx,R}，type1 dispatcher/executor绑定|queue载荷是其RV32指针值，I对象须持续有效直至正常分派/清理；不是发送方局部I槽本身|
|send_slot|发送caller的局部I **word槽**，存I指针，source=&send_slot|copy期间借用该槽4B；不把槽地址挂到Msg作为payload|
|Msg|native queue内部header/链节点，payload=Msg+0x0c，actual_len=U16(Msg+0x0a)，kind=U8(Msg+8)|持载荷值及queue节点；不是I，也不是R。kind字段与I+8 type字段不能混同|
|receive_slot|consumer caller的localI word槽，s0−0x34|接收前清0；copy写I指针值；caller重新读非零值后才访问I/type|
|receive_msg_slot|finite服务自己的outMsg局部word，位于该帧s0−0x24|保存被pop的Msg指针，用于取payload及Msg归还；不是前两个I word槽，不转交给executor|

### 最小前提

以下是合成成立所需条件，**并非本项已认证的运行事实**：

- F16指定的同Manager正常setup/配置/线程接口/matching-thread attach成立；到实际send copy时ctx→L→Q是该实例且n=4，不能用“初值”排除后续改写。
- 选定send实际到达copy(Msg+0x0c,&send_slot,4)、正常发布及已验正常返回，且constructor按F11成功分支保留I/R。单看adapter零值不足以选定这条轨迹。
- send源/目的和receive源/目的各自满足F18的4B正常有效、word对齐、足够容量、无干扰及所需分离条件；Msg header/链存储有效。不能由Msg非零、queue guard或332B请求自动推出这些条件。
- 若要说“此send传到此receive”，pop的就是同一个**运行Msg实例**，payload4B和header长度未变；本次actual_len确实为4。也可只认证某条独立receive载荷已知为有效I指针值，但那不能反向证明某次send/Msg对应。
- I保持有效且非零，Msg回池/归还不能通过别名破坏I/receive_slot；有效ctx/R/user与类型/绑定在执行期间维持。I、R、Msg身份在文字上不同不证明实际非别名。
- finite非空接收及中间控制/归还/后续服务按所选正常接口返回；Msg.kind为0/1/2的已验正常分支，caller最终返回到localI门；本例typed executor正常返回0。其他类型/返回1/超时、异常及诊断路径不混入。

### 发送方局部槽何时可失效

F14的实际长度与上述前提给出n4，F18给出发送helper返回前已完成四次byte读写且无直接存src/dst地址，F14再给出copy返回之后才发布Msg。因此在 **send copy返回点**，Msg.payload已有当次读到的I指针值，**native载荷复制这条数据通路**不再依赖send_slot的存储；槽可结束这项借用。普通正常send返回并使该局部栈槽失效时，不必等待consumer读取原send_slot。

这只结束对**局部word槽**的借用，不允许I/R/ctx/user随之失效。程序若另有借用者、地址别名、opaque服务对该区域的外部引用，仍须满足各自寿命；本项没有全局“任何引用均不存在”证明。4B载荷也不是I对象备份：释放I后，Msg中的指针值仍会悬空，队列并没有深拷贝其对象来兜底。

### 先归还内部Msg，再执行/归还heap I

在同Msg、actual_len4及地址域前提成立时，正常事件顺序为：

```text
send copy返回 → 发布Msg → finite非空pop该Msg
→ copy(receive_slot, Msg+0x0c, actual_len=4)返回
→ Msg.kind0/2回对应gp池，或kind1交Msg归还接口
→ 接收正常返回，caller忽略a0并重读receive_slot
→ 非零有效I的type1分派 → executor正常返回0
→ 按F11 generic合同本地归还heap I
```

Msg回池/归还后，即便节点可被复用，consumer后续分派所需I指针值已经在**receive_slot**，而不是继续借用Msg.payload；这条解释仍依赖节点归还/复用不通过alias破坏I/receive_slot。归还接口是否物理回收、是否真实复用没有观察；不把相同kind/gp池当同一次对象往返。

F11的type1 executor一般返回非1才本地归还I，返回1是持有转移。本例只选其既验正常worker返回0；不重新恢复generic callback，不推广所有callback都不保留指针。R不因Msg或I归还自动消失：正常worker可把R交session持有，R消息又可能按已有两门提前归还。R对象、R消息、session、response的后续清理继续按F11/F12各自合同，不能压成“I释放同时free R”。

### 对原native断边的回答强度

原F11“是否复制局部I指针槽”现在可在上述域给出**条件静态答案**：复制4B值并先归还内部Msg后才分派heap I；source槽借用不需持续到consumer执行。真正新增是将已验setup/长度域、copy、Msg发布、actual_len/out复制、Msg/I分离清理接成一条可复用语义合同；新字节/新helper/新业务均0，未声称全部native分支或运行前提闭合。

最小机器合同见 [contract.json](../../analysis/miio-invocation-queue-lifetime-f25-0041-20261024/contract.json)：保留4组前提、独立对象、顺序事件和待验F23/F24，明确排除F22全局caller guard；只表示条件规则，不是执行结果或完整覆盖账本。

## 未闭精确边与实际检查

仍未证明：同次发送/接收Msg身份、全producer/Msg+0x0a writer、actual_len4全域、真实映射/size稳定、有效存储/容量/对齐/别名/独占/持续寿命、调度执行机会和发布同步、waiting/timeout/诊断/clock完整行为、物理heap释放、generic callback其他持有、R/ctx/user完整生命周期及业务/云端成功。F23/F24差集待验；本项不借新回边/状态伪码结论提前关闭这些边。

唯一有种子后继是原 **F11/9** 下非作者F26复核该合成：核send copy返回的槽借用边界、actual Msg.len4/同运行Msg前提、Msg归还→I分派→选定I归还的顺序及R独立性，确认没有将F23待验或F22旧guard纳入已验全局前提。若要认证真实运行实例，则须另有精确producer→pop Msg身份/header写入证据，由管理窗口先登记，不能再导出相同helper或所有queue。

[check.py](../../analysis/miio-invocation-queue-lifetime-f25-0041-20261024/check.py) 实际 **20项静态引用/合同一致性检查PASS**：六份独立复核来源可定位、copy/actual_len/归还分支/初始化限定有来源、F23/F24不在已验依赖、局部槽身份分列、事件顺序和前提组完整。该检查不运行任何旧技术脚本、不读ROM/新helper、不模拟执行；不是对运行前提的测试或新语义独立证明。输出 [check-result.json](../../analysis/miio-invocation-queue-lifetime-f25-0041-20261024/check-result.json) 本地忽略保留。

JSON、报告相对引用、Git忽略和diff检查通过。仅交付本报告、机器合同、静态检查源码及本地结果；作者完成停止，待F26独立复核，无提交推送。
