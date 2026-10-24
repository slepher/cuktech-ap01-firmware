# F19：MiIO正常接收的localI输出、内部消息摘出及归还边

**正常finite/nonempty接收端已连到caller的localI输出槽。** caller先清localI，无同步消息时以同Q调用接收adapter；下层正常非空分支从K的哨兵链取得Msg，copy接口以 **`dst=&localI, src=Msg+0x0c, len=U16(Msg+0x0a)`** 调用，返回后才归还Msg。caller不比较接收返回a0，只重新读localI，非零才进入既有type分派。

**实际copy长度来自Msg header，不能直接替换成Q.size=4。** 也未证明某次send的Msg就是本次pop的Msg、全部producer只写4B，或任一实际接收/consumer成功。本报告保留copy实际域、有效地址/容量/寿命、并发与执行边界；不因此无条件宣布caller栈可失效或整queue恢复。

2026-10-24；认领 **F11/6**，任务F19，作者 `/root/f12`；独占 `re0041-f19` / `codex/re-0041-f19`，固定基线 `bd457a6`。按主仓[唯一管理记录](rolling-management-0041-20261023.md)、最新[流程](reverse-design.md)与[材料规则](../../analysis/README.md)工作，采用REA技能的留存优先方法。初始仅旧record195定位；adapter、finite服务、正常非空pop/release本体逐次先报实参/旧证据不足，管理登记后才读新窗口。新list helper由F21负责，本题仅按登记条件继承，未重复取证。

不运行目标/指令/模型、固件、SIM/QEMU、构建、回放、设备、外部服务或旧技术脚本；不切换共享REA，不改生产/ROM/配置/模型/主树/共享表，不提交或推送，无下级agent。只写本报告、独占analysis源码/必要合同；生成JSON按原相对路径本地忽略保留。作者交付待非作者复核，不自验冒充独立验收。

## 继承结论

|已有出处|已解释行为与局限|本题处理|
|---|---|---|
|[最终应用验收](application-rehost-complete-0041-20261017.md)、[upper-layer](upper-layer-0041-20261017.md)|旧event-loop/type分派已有局部合同，SIM不认证ROM queue行为|不重做页面/全event-loop或SIM|
|[F11](miio-request-ownership-f11-0041-20261024.md)/[F12](miio-request-ownership-review-f12-0041-20261024.md)|I独立构造、type1 callback `(loop,I)`、返回1与其他返回的持有/归还合同已验|只接到既有dispatcher前，不重验callback/R/P/S或free策略|
|F13/F14、F15/F16、F17/F18|send侧Q/F/K、正常setup size4身份桥、有效word对齐copy n4各有独立范围|均不证明receive Msg.length恒等4或某个实际Msg身份；本题copy域按实际header长度和地址前提判断|
|[F21消息来源](miio-queue-message-source-f21-0041-20261024.md)|0xa010d70e正常有效哨兵H取N=word(H+4)，空时0，非空修复邻接、重读N+4、先清N+4再清N+0，返回原N，无callee|按管理登记只读继承；继承时为F21作者交付、待F22非作者复核。F21的H=gp+0xb8/c0，本题H=K+0x18，**容器不同**，不重读42B或认证独占/容量|

原件沿 [CATALOG](../../../roms/CATALOG.md)：主仓 `roms/0041/ap01-1.0.2_0041.bin`，实查6,769,704B，继承SHA256 `972db4c136c7ed9e24a83c07c1a7fd62040ca018b08ca285216d26b1fee3c6b9`，不重算机械摘要；映射 `file_offset=VA−0x9ffff000`，不是0031/unsigned/SIM。

旧caller直接读主仓 `evidence/rea-0041-20261017/evidence/upper-complete.evidence.json#/records/195`：0xa011e3d6，Evidence `ev_9a7e0a186c4ed2b341b4d42187fcb73bebec13d401cd226033d30027d121387d`，profile `4825fb58a33a3e7d618557975b153b8318cf7e833d190ad16bcbf8bd441ae621`。只取接收必要行，不重导708B thread body/完整大Evidence。

旧whole-ROM index仅提供以下定位，无dossier/已验本体合同；EID不是新语义证据：

- `functions[1461]` 0xa005f508，164B extent `ev_54cbff1a460e907f76edf76d93db859c275f59fc0252a5a00e1dbde0c9b1e2ba`。
- `[5811]` 0xa0197954，314B extent `ev_cd3128d3c3d0683457e73d8bd34de8cf1c818a41a0f1564c6582cee795bc09b2`。
- `[4267]` 0xa01319e8，242B extent `ev_70a433beff50c530955b97a58e0a7101cf143469d0be39bd901ae791af4ef0bb`。
- `[4269]` 0xa0131b68，94B extent `ev_7953e240bb6dbdb5271260352221747d99dc7729e9da82055c0673bd2cb3c27a`。
- `[3828]` 0xa010d70e，42B extent `ev_307bfa85996bc49ba8033818c20586927cfad86def6317ebd4804f3be509ed03`，其正常合同由F21产生，本题不重复。

## 本轮复核或纠正

未纠正旧generic分派/持有合同。新精度是 **receive实际长度来自Msg+0x0a，而Q+0x18只是传入的容量/尺寸参数**；caller以localI值而非返回状态决定进入分派。不能把新文件或旧body字节存在算初次发现，也不把有限精确地址查重无命中称全局未研究。

一次探索读从 `0xa0131a38` 开始，发现它实际位于 `0xa0131a36` 的4B ADDI中部；立即回到前一真实边界读原字，独立复验采用 `0xa0131a36 addi a0,s1,0x5c`，没有把伪压缩指令保存为结论、改ROM或修模型。

工具为 **Capstone 5.0.7 / RV32+RVC**，普通位域/目标另独立解算。adapter `0xa005f56a=8b97d420` 在Capstone保留UNDECODED，字段op0x0b/f3=1/top7=16/rd15/rs1=9/rs2=13匹配既有 `ap01thead2.sinc :th.mula` 的 `rd=rd+rs1*rs2`，仅按该局部模型条件解释。保留原字/规则来源，没有执行/改模型或声称独立厂商ISA认证。

deadline转换只说明adapter的局部字段构造：以opaque clock-like服务填局部两word，对第一word加timeout DIVU1000，对第二word加 `(timeout REMU1000)*1000000`，随后依原signed阈值999999999作一次调整；下层也有自己的正常deadline门。**不展开clock/timer服务、认证单位/时钟来源或任意timeout值域。** 这些算术不参与本报告对copy长度/Msg身份的替代推断。

## 真正新增

对象按实际连接定义：L为loop；Q=word(L+0x18)；F=word(Q+0x0c)、K=word(F+0x18)沿F13布局但本轮核实读取；`outI=s0−0x34`是caller局部I槽地址；`outMsg`是finite服务自己的另一个栈槽地址；Msg是正常摘出节点返回值，区别于invocation I、manager M和caller out地址。

|连接/地址|正常接收、参数与顺序事实|
|---|---|
|旧0xa011e518/51a/51e|先读L+0x2c同步链，清caller localI；只有同步链为空才到native接收。非空同步分支沿既有合同，不与native Msg混同|
|旧0xa011e5ea..0xa011e5fa|timeout默认10000（s7=0x2000+0x710），或取firstTimer+4的word；Q为空直接跳回localI门。否则以 `(Q,outI,timeout)` 调0xa005f508|
|旧0xa011e5fe、e548/e54c/e550|返回后直接跳读localI，不比较a0；localI零回主循环，非零才读byte(I+8)进入既有type分派。返回0不等于某个I被消费|
|新0xa005f518..f528、f592..f5a6|timeout==−1时调用0xa01978a2(Q,outI,n)，只保留该callsite不展开本体；默认10000的finite臂保存原outI，构造本地deadline，再以 `(Q,outI,n=word(Q+0x18),&deadline)` 调0xa0197954。两臂返回汇共同srai a0,31，折为0/−1；caller仍不使用该状态门|
|新0xa0197986..79a0、79ba..79ca|正常入口经过前置诊断门后读取同F/K，检查Q首word的mask1及n对U16(K+0x24)的容量门；s5保存原outI。保存mstatus并清mask0x8，比较K+0x1c与K+0x18 sentinel；本轮只沿**正常非空ready分支**|
|新0xa0197a2e..7a44|以 `(K,word(Q),outMsg)` 调0xa01319e8；返回后先调用opaque控制服务，再判断保存的status，非零到恢复返回；0才读outMsg。这项中间调用不省略，未认证其调度行为|
|新0xa0131a02..1a44|保存原K/outMsg地址，以H=K+0x18调0xa010d70e。依继承F21有效哨兵合同，非零结果为从**此H**摘出的N=Msg，不是gp池节点身份。随后LH K+0x22、减1、SH回；可选通知调用以(K+0x5c,4,4)交既有服务，正常返回后SW同Msg到原outMsg，返回0。本体没有写Msg+0x0a；不因此排除外部别名/回调修改|
|新0xa0197a46..7a66|从outMsg槽读同Msg，非空后 **LHU Msg+0x0a** 保存actual_len，copy实参为 `(outI,Msg+0x0c,actual_len)`，目标独立算为0xa000589c。不是复制整个Msg，也不是直接把Msg指针写到caller localI|
|新0xa0197a6a/7a6c|copy接口返回后，把**原Msg地址**交0xa0131b68。payload复制和内部Msg归还的顺序明确；该callsite不转移I对象自身所有权|
|新0xa0131b68..1b8a|先U8(Msg+8)。kind0把Msg按原四次word写接入gp+0xb8的哨兵链；kind2选gp+0xc0后汇同插入段。写Msg+4=sentinel、Msg+0=oldFirst、oldFirst+4=Msg、sentinel+0=Msg，随后返回|
|新0xa0131b94..1ba8|kind1以原a0=Msg调用0xa002e14e接口后返回；其他kind到诊断边界，不推其是否返回。**不是所有Msg都调用heap free**，也不宣称实测物理回收|
|新0xa0197a70/7a74、79f0..7a06|Msg归还调用后读signed K+0x10 waiter门；非正臂直接恢复mstatus，a0=保存的actual_len返回。其他wake服务保持边界。pop失败状态也走共同返回；adapter折符号后caller只看localI|

F21取候选的gp+0xb8/c0表达式与本归还服务两哨兵表达式相同，可形成**条件来源/归还端接口连接**；但K+0x18是另一个队列容器。没有由此证明某个具体Msg的往返实例、pool初始内容/容量、所有kind初始化或独占寿命。F21本体当前是作者交付、待独立复核的继承前提，本报告不代其独立验收。

对copy的解释分层：事实是它以outI、Msg+0x0c、actual_len同步被调用并在Msg归还之前返回。若actual_len=4且满足F17/F18的有效word对齐等域，copy4合同可说明caller localI四byte获得Msg.payload值；**这个值才可被上层作为I指针读取**，不是Msg地址本身。Q.size4初始化不证明每个收到的header长度4或其全部producer/写入者，其他actual_len按对应已验域或未知边界处理。

局部表达（非原源码；正常ready及边界服务正常返回）：

```c
localI = 0;
if (L.sync_head == 0 && L.queue != 0)
    receive_adapter(L.queue, &localI, timeout); // 其返回a0不作caller门
if (localI != 0) goto inherited_dispatch;

// finite接收正常非空臂：
status = pop_service(K, word(Q), &localMsg);
opaque_control_service();
if (status == 0 && localMsg != 0) {
    Msg = localMsg;
    actual_len = load_u16(Msg + 0x0a);
    copy_interface(outI, Msg + 0x0c, actual_len);
    release_by_kind_u8_at_8(Msg);     // kind0/2入不同gp链；kind1交归还接口
    opaque_waiter_service_if_required();
    result = actual_len;
}
restore_saved_mstatus();
return result;                       // caller不据它替代localI门
```

新恢复为receive adapter、正常ready Msg来源到out槽、header长度、copy前后顺序和Msg按kind归还的条件本体合同；旧type1 dispatcher/业务新增0，ISA/整库排除/完整queue恢复0。不是全producer/完整生命周期、并发顺序或实机行为认证。

## 未闭精确边、检查与后继

未闭：某次send Msg与当前pop Msg的运行身份、全部producer/Msg.length writer、actual_len4值域；Msg.payload与outI的有效性/容量/对齐/分离和I对象寿命；gp池初始化/节点大小/复用/其他别名；实际ready/等待/超时/clock、控制/调度服务行为；真实consumer执行与消息/业务交付。空队列等待、−1服务body、取消/异常输入和完整调度不在本批，不由局部缺口推缺陷。

一个有种子的后继：围绕 **Q=word(L+0x18)、pop出的Msg+0x0a写入者** 查重登记“同Q producer到实际header长度”的必要身份/写入合同；已验send路径SH长度可以继承，仍需区分其Msg与接收Msg和其他producer。没有该桥时就保留actual_len，不在本报告把它改写为4。这里没有继续新caller/producer取证。

实际检查分四段：[locate.py](../../analysis/miio-queue-receive-gap-f19-0041-20261024/locate.py)20项旧留存/0B新ROM；[verify_adapter.py](../../analysis/miio-queue-receive-gap-f19-0041-20261024/verify_adapter.py)20项/90B样本；[verify_receive.py](../../analysis/miio-queue-receive-gap-f19-0041-20261024/verify_receive.py)33项/154B；[verify_message.py](../../analysis/miio-queue-receive-gap-f19-0041-20261024/verify_message.py)38项/152B，均PASS。探索unique原字分别adapter164B、finite264B、pop154B、release94B，样本数不冒称全部读字节。没有重跑F11/F21等作者/历史脚本，未读取a010d70e/allocator/clock或调度callee正文。

四份生成JSON分别为 `locator-evidence.json`、`adapter-evidence.json`、`receive-evidence.json`、`message-evidence.json`，留在本地同名analysis原路径受忽略；原字/VA/偏移、边界、规则和旧引用可定位，没有新造REA ID。[contract.json](../../analysis/miio-queue-receive-gap-f19-0041-20261024/contract.json)只保留必要语义。JSON/引用、空白、独占工作树和`git diff --check`已检查，源码/合同/报告未提交，作者交付停止，待非作者复核。
