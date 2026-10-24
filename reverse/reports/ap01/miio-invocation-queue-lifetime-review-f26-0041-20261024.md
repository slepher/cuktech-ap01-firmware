# F26：F11/9 invocation指针队列条件寿命合同的非作者复核

2026-10-24；固定基线 `bd457a6`，分支 `codex/re-0041-f26`；挂原认领 **F11/9**，非作者 `/root/g23`，F25作者 `/root/a56`已停止。**限定接受F25条件合成，语义纠正0、复核新增业务0。** 在同Manager正常setup、实际n4、所需有效/对齐/分离/容量/稳定性、同运行Msg及其actual_len4、正常服务回返和有效I/R/ctx等前提成立时，native队列传递heap I的4B指针值，send copy返回结束这条数据通路对发送方局部word槽的直接借用；不会深拷贝I或R。

接收copy先把该值写入另一个localI槽，再归还内部Msg；caller随后重读/分派I，选定type1 worker正常返回0后才走I本地归还接口。R/R消息/session按F11自己的分支寿命处理，不能由Msg/I顺序推其清理时刻。**这是条件静态规则，运行前提本身没有因此得到认证，原native队列全域仍未闭合。**

已读主仓 [F25报告](miio-invocation-queue-lifetime-f25-0041-20261024.md)、[F25机器合同](../../analysis/miio-invocation-queue-lifetime-f25-0041-20261024/contract.json)及 [唯一管理表](rolling-management-0041-20261023.md#链条认领表) F26登记；沿本批已读 [流程](reverse-design.md)、[保留规则](../../analysis/README.md)和 [REA技能](C:/Users/cogic/.agents/skills/reverse-engineer-anything/SKILL.md)。只核必要已验报告/合同与连线，没有读取ROM、新helper或完整大Evidence，没有运行F25的check.py或任何旧技术脚本、指令、模型、目标、固件、SIM/QEMU、构建、回放、输入实验、设备或外部服务。

未切换共享REA/profile，未改主树/共享表、生产ROM配置模型，无下级agent、提交或推送。以下为合同合成审查及条件推理，非新原字、执行观察或存储保证；各来源的原Evidence/profile仍沿各自报告，不重标为本轮新REA结果。

## 继承结论

|独立接受来源|本次独立核对的连接|原有限定保留|
|---|---|---|
|[F12](miio-request-ownership-review-f12-0041-20261024.md)|heap R、heap invocation I与payload={ctx,R}；type1正常executor返回非1后本地归还I，本例选worker0|局部指针槽不是I对象；I归还不代表R/R消息同刻归还，不推广所有callback返回/持有|
|[F14](miio-native-queue-review-f14-0041-20261024.md)|source=&sender局部I槽，实际n=word(Q+0x18)；SH n到Msg.len，copy接口返回后才发布Msg/改计数|adapter零返回不证明已到copy/发布；本题选择已到达并正常返回的轨迹|
|[F16](miio-queue-size-review-f16-0041-20261024.md)及F15必要合同|同M正常配置/线程接口/matching-thread attach：L=M+0x128、ctx=M+0x174/+0x968保存L，L+0x18为同Q，Q+0x18初值4|只认证具体正常setup状态；仍须实际send读到同Q与n4，不能排除后续writer/替换|
|[F18](miio-queue-copy4-review-f18-0041-20261024.md)|有效word对齐n4的交错byte读写、原dst返回、此路线无直接参数地址持有|非原子4B快照，不认证任意长度/重叠/干扰；没有I/R对象复制或retain|
|[F20](miio-queue-receive-review-f20-0041-20261024.md)|finite非空接收copy长度为U16(Msg+0xa)，copy后Msg按kind归还，caller忽略status重读localI|Q.size4不替换实际Msg.len；pool/heap接口不等于已观察物理free或业务交付|
|[F22](miio-queue-message-source-review-f22-0041-20261024.md)|只继承getter及有效哨兵摘节点本体|332B请求/非零Msg不证容量；gp两池与K队列不同；旧整体caller guard单独排除|
|[F24最新独立复核](miio-queue-send-wait-review-f24-0041-20261024.md)|caller新增进入边及伪码原序精确化已独立接受|只更新继承状态/范围，不把状态服务、等待或调度行为塞成已证运行前提|

原件身份仅继承各来源/[CATALOG](../../../roms/CATALOG.md)：0041 `ap01-1.0.2_0041.bin`，6,769,704B，既有SHA256 `972db4c136c7ed9e24a83c07c1a7fd62040ca018b08ca285216d26b1fee3c6b9`，VA映射`VA−0x9ffff000`；本题未打开ROM、校长度/摘要或新造Evidence ID。F16没有单独contract.json，本题用其正式限定接受报告核F15机器合同的身份/初始化状态，不把缺文件解释为新缺口或自行补技术证明。

## 本轮复核或纠正

### 条件连线没有把初始化/接口提升为运行事实

同M身份桥核对到ctx→L→Q；queue输出槽的偏移算术0x128+0x18=0x140与F15/F16一致。Q.size4只是该初始化状态，F25另列“实际copy时n=4且没有相关后续改写”的前提，因此未由`&局部I`猜队列尺寸，也未把所有queue认证为4B。

F14给send时SH n与copy接口；F18只为真实n4和相应地址域补复制效果；F20在receive端仍取实际U16 Msg.len。**把一次send与一次receive连成同一指针值传递，必须额外有同运行Msg实例、payload四byte及header长度稳定、本次actual_len4。** F25均明确列出，不能由同queue、同kind、同helper或相似producer代替。4B copy的逐byte原序要求无干扰条件，F25没有把它改成原子指针快照。

### 槽、对象与归还顺序独立

|身份|复核结果与条件|
|---|---|
|send_slot|sender局部word，存heap I指针；source是该槽地址。copy返回后，只结束native payload-copy这项直接借用；其他借用/alias需要的寿命未被抹去|
|Msg|内部header/链节点，payload+0xc、U16 len+0xa、kind byte+8；不是I或R。有效容量/对齐/独占/归还复用仍未证明|
|receive_msg_slot|finite函数自己的outMsg局部word，保存Msg指针；不是caller的localI输出槽，不交executor|
|receive_slot|caller先清零的localI word，receive copy写入I指针值；Msg归还后caller从这里重新读，不再凭该数据通路借用Msg.payload|
|heap I|队列仅复制其指针值，I对象及type/payload绑定必须继续有效；worker0返回后才按generic合同本地归还，return1路径另有持有转移|
|R及其消息、ctx/user|I.payload复制的是地址，queue不深拷贝/retain这些目标；R可交session，R消息可提前归还，具体寿命继续依F11/F12|

文字上不同对象/地址表达式不是实际不别名证明。F25分别列出有效存储/容量/对齐/分离、没有其他source借用、Msg归还/复用不经alias破坏I或receive_slot，以及ctx/I/R/user持续有效的前提，合成没有把这些条件当自动事实。

核对的条件偏序为：

```text
send copy返回 → 发布Msg → pop同运行Msg → receive copy返回
→ kind0/2回各自gp池或kind1交Msg归还接口
→ caller重读非零有效I → type1分派 → 选定worker返回0 → I归还接口
```

这一偏序来自分开的正常接口，既不宣称所有Msg heapfree，也不观察物理回收、实际复用或执行。R没有被插入该I清理事件替代其自身合同；generic其他type/返回1、超时/诊断/异常和未选分支不纳入。

### F24状态更新及旧guard排除

F25写作时F23/F24待验的文字保留为历史，**不算F25语义错误**。当前F24已独立接受：除7aca flag非零直接落入边，还存在signed BLT7af0和服务返回零7afc进入getter；稳定flag0/count<limit/第一池空可到332B请求。F22冻结的`caller_flag_condition`不能成为所有正常前驱的全局前提。

本复核确认F25有效前提组没有使用这个全局flag guard。F25条件轨迹从“选定normal send实际已到copy/发布”开始，本来不需要证明哪条状态/等待路径使其到达；F24被接受也没有赋予实际进展保证。F24对1972先读T+c、1974清T+22、1978测试先读值的精确化只在其本体范围使用，本合成没有重新排序或拿它补调度证明。冻结F21/F22/F23/F25文件与历史pending状态不静默改写。

**对F25的核心语义纠正0。** F24的既有纠正是已存在的独立来源，本轮只据最新状态限定依赖，未重复取原字或把它计成复核新增。

## 真正新增

复核新增业务 **0**、新ROM字节 **0**、新helper/ISA/来源认证 **0**。新增交付为非作者对F25条件合成的接受及独立引用/机器合同一致性记录，不将合成当新存储/ABI/运行证据。

可接受的回答是：在全部显式条件成立时，**send_slot在copy返回点可结束这项借用，I对象不能随之失效；receive端先归还Msg再reload/分派I，选定worker0后归还I；R另有寿命。** 只缺任一实际长度、地址域、运行Msg身份/稳定、别名、其他borrower或正常回返前提，就不能把该规则变成某次实际caller栈可失效或整native队列已闭。

必要复核合同见 [contract.json](../../analysis/miio-invocation-queue-lifetime-review-f26-0041-20261024/contract.json)，只记录限定接受/更新依赖/未证域，不复制F25完整机器合同或指令材料。

## 未闭精确边与实际检查

同运行Msg、所有producer/Msg+0xa writer、actual_len4全域、setup后ctx/L/Q/size稳定、有效存储/容量/对齐/分离/独占/持续寿命、载荷稳定和无其他source借用、等待/调度/同步/实际执行、物理heap回收及R/ctx/user完整生命周期仍未闭。服务返回0、queue尺寸初值、不同参数表达式或332B申请都不能填这些事实。

本题新 [review.py](../../analysis/miio-invocation-queue-lifetime-review-f26-0041-20261024/review.py) 实际 **35项独立引用/合同不变量检查PASS**：七份限定复核来源、同M偏移/初值限定、实际n/Msg.len分离、七对象/三局部槽、四组前提、Msg/I顺序及R独立、旧guard排除与F24新状态。它仅解析既存Markdown/JSON并核一致性，**不是执行测试或新的语义独立证明**；本报告同时进行上述范围与条件推理审查。未运行F25 check.py或任何旧技术脚本。

JSON解析、报告引用、Git忽略、独占文件及diff检查通过；[review-result.json](../../analysis/miio-invocation-queue-lifetime-review-f26-0041-20261024/review-result.json) 本地原路径忽略，报告/源码/必要合同未提交推送。

有种子后继仍为**同Q producer→pop Msg+0xa实际长度/运行身份**，须管理窗口先查重登记；仅有send SH n和receive LHU、相同queue/池kind不足认证这项。不要重复同批copy/helper导出或把本条件规则当全域关闭理由。
