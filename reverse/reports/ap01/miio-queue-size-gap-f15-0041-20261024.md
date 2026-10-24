# F15：MiIO 同一正常初始化实例的 loop.queue 与4B size身份桥

**在所定位的同一M正常初始化、配置及matching-thread attach路径上，可把F11两个ctx连到同一L/Q，并证明Q+0x18初值为4。** M内 `L=M+0x128` 的queue输出槽是 `M+0x140=L+0x18`；creator把请求a2=4按word写Q+0x18后把Q写入该槽。正常start回调以同L依次attach `ctx=M+0x174`、`M+0x968`，attach将L写ctx+4。于是这些正常初始化实例中的F13长度读取为4，而非从 `a1=&局部I` 猜长度。

这不证明某次实际send已完成该初始化/attach、没有后续writer、所有同名loop都是该实例，或copy4B算法已经认证。**F13的0xa000589c实际4B分支、M消息目的有效性/对齐/寿命仍未闭。** 本报告为作者交付，待非作者独立复核。

2026-10-24；认领 **F11/4**，任务F15，作者 `/root/f12`；独占 `re0041-f15` / `codex/re-0041-f15`，固定基线 **`bd457a6`**。先读主仓最新[流程](reverse-design.md)、[材料规则](../../analysis/README.md)、[唯一认领表](rolling-management-0041-20261023.md)。初始只准旧initializer定位；发现creator后报管理窗口获准0xa005f0b0参数/正常字段/输出槽；再发现attach身份桥后报管理者，获准0xa0110708/718→0xa01ab55a正常ctx+4保存必要原字段，均先登记后读取。

采用 `reverse-engineer-anything` 技能，先复用主仓忽略保留的旧证据，不复制大Evidence。不运行目标/指令/模型、固件、构建、SIM/QEMU、旧技术脚本、回放、设备或外部服务；不打开/切换共享REA，不改生产/ROM/配置/分析器/主树/共享表，不提交或推送，不创建下级agent。F13工作树/成果未改。本题生成JSON留在原相对路径并受Git忽略，仅报告/源码/必要合同作为交付维护。

## 继承结论

|已有出处|已解释行为与边界|本轮差集|
|---|---|---|
|[最终应用验收](application-rehost-complete-0041-20261017.md)、[upper-layer](upper-layer-0041-20261017.md)|业务与共享event-loop已有局部合同；SIM不能认证ROM native queue或实际consumer|不重做业务、全消息队列或SIM|
|[F11](miio-request-ownership-f11-0041-20261024.md)/[F12](miio-request-ownership-review-f12-0041-20261024.md)|两条正常send ctx候选为manager+0x174/+0x968；I.loop取word(ctx+4)；type1跨线程caller取Q=word(L+0x18)，传`(Q,&局部I,−1)`|I/请求构造/持有继承，不重验；此前未绑定Q.size|
|[F13](miio-native-queue-f13-0041-20261024.md)|0xa005f464取n=word(Q+0x18)，经0xa0197a8e→0xa01949f0，先以`(Msg+0x0c,source,n)`调用copy接口再接Msg链|只补同Q初始化及ctx/L身份，不接allocator/wait/notify/全copy算法|
|[G03](invalidation-submit-g03-0041-20261023.md)/[G04](invalidation-submit-review-g04-0041-20261023.md)|有效分离word对齐16/20B的0xa000589c值复制已有合同|本题旧initializer有16B配置表调用，可沿该限定域理解；不据它认证4B或任意n|

“M”是旧master初始化器 `0xa0064368` 中s1保存的manager分配实例；只在该正常初始化路径内维持身份。它不是随意选择的另一个loop或某次运行的实际对象地址。Q在本题表示native queue，区别于F11栈descriptor别名Q；Msg区别于本manager M。

已有→行为→局限→缺口：旧master body已经保存L的创建实参及thread配置；旧thread/start/wrapper body已经保存两ctx的attach调用端；这不自动认证creator的字段写入或attach是否保存同L。因此本轮先精确定位两callee，登记后只补参数/word保存，不因旧完整body存在把新接线计作早已验收。

## 本轮复核或纠正

初始盘点只读旧Evidence，[collect.py](../../analysis/miio-queue-size-gap-f15-0041-20261024/collect.py) **15项PASS、新ROM0B**，输出 [evidence.json](../../analysis/miio-queue-size-gap-f15-0041-20261024/evidence.json) 记录当时“候选creator a2=4、尚缺两桥”的状态。该初始盘点结论在下述获准原字段补证后推进，不把阶段性未知伪装为错误或全局否定。

原件沿 [CATALOG](../../../roms/CATALOG.md)：主仓 `roms/0041/ap01-1.0.2_0041.bin`，实查6,769,704B；继承SHA256 `972db4c136c7ed9e24a83c07c1a7fd62040ca018b08ca285216d26b1fee3c6b9`，不重算机械哈希；`file_offset=VA−0x9ffff000`。不套0031/unsigned/SIM地址。

旧留存统一来自主仓 `evidence/rea-0041-20261017/evidence/upper-complete.evidence.json`，下列4个record实际profile均为 `4825fb58a33a3e7d618557975b153b8318cf7e833d190ad16bcbf8bd441ae621`：

- `[248]` 0xa0064368，`ev_c3dd842723b83165bc8e1a6b235f2005269080da4969520bd0c0f0e413db133a`：M/L、queue creator实参、thread入口、配置表。
- `[195]` 0xa011e3d6，`ev_9a7e0a186c4ed2b341b4d42187fcb73bebec13d401cd226033d30027d121387d`：thread读取L+0x10 vtable，调用start(L,vtable.user)。
- `[96]` 0xa011e08e，`ev_4765a2915f077a6cb63cd6f59f598f6642d3ee1b1c9c4663e62bea464b4ee7c0`：wrapper再读L+0x3c callback与L+0x48 user。
- `[27]` 0xa01106f2，`ev_13c2f5afa1fcfb7c53c117ed097c6a6af54098e5ea57a4724fa9c77a93d547cd`：同L分别attach user+0x8c、user+0x880。
- F11/F12原ctx→I.loop及type1提交调用端沿其原Evidence，不重导或另造ID。

两新callee在主仓旧 `reverse/analysis/whole-rom-coverage-0041-20261023-round1.json` 中都只有extent/directcall、无dossier：`functions[1451]` 0xa005f0b0的158B extent EID `ev_31e7086a1eb58c691e393fa9a05e7bf0d7aade5f96e7aedf894541677b0b923f`；`functions[6143]` 0xa01ab55a的218B extent `ev_2c42e996f2c9dea1d110bd4b5192d941d7b6f5d90aa267c0b57f6d94eca8039b`。它们仅作定位，不拿范围当语义。近期精确地址/调用端未得已验合同的搜索界限见管理登记，不证明全局不存在研究。

获准补证使用 **Capstone 5.0.7、RV32+RVC** 和独立位域，没有厂商未知字、模型变更或目标执行。creator探索158B，只保留64B参数/正常提交/返回样本；attach探索140B，只保留82B正常入口/门/ctx+4/尾插样本。不是整218B attach或其callee恢复，没有全queue扫描。实际 [verify_creator.py](../../analysis/miio-queue-size-gap-f15-0041-20261024/verify_creator.py) **19项PASS**， [verify_bridge.py](../../analysis/miio-queue-size-gap-f15-0041-20261024/verify_bridge.py) **48项PASS**；原字、VA/偏移、普通指令、S-format/B-format/两AUIPC-JALR及旧桥行分别存 [creator-evidence.json](../../analysis/miio-queue-size-gap-f15-0041-20261024/creator-evidence.json)、[bridge-evidence.json](../../analysis/miio-queue-size-gap-f15-0041-20261024/bridge-evidence.json)。无新REA会话/Evidence ID。

## 真正新增

|连接/对象/地址|已证字段、顺序及限定|
|---|---|
|旧master M→L/输出槽：0xa0064f4a、0xa0065438..0xa0065450|s7=M+0x128=L；creator实参a0=M+0x140=L+0x18，a1=0x80，a2=4；返回0才进正常后续。因此是**同L.queue槽的创建请求**，不是别的队列碰巧size4|
|新creator0xa005f0c0..0xa005f0cc、0xa005f0e4|s2保存原out槽，s3保存原a2，s4保存原a1；候选Q请求0x1cB，正常非零结果保存s1=Q。分配/打开callee本体保持opaque|
|新creator0xa005f11a..0xa005f12a|将原a1/a2作word存到局部attrs前两槽，调用0xa01974de；返回非负才进入正常commit边。未凭名称认证整个queue打开/命名/容量语义|
|新creator0xa005f142/144/148|先设置正常a0=0，再 **SW s3,0x18(s1)**（Q.size=原a2），随后 **SW s1,0(s2)**（把同Q发布到原out槽）。独立S-format确认是word、偏移0x18与0，非半字/另一对象。此正常实例原a2=4，所以L.queue→Q且Q.size初值4|
|旧master配置/线程：0xa0064da6、0xa00653ac..0xa0065406、0xa006548e/549e、0xa006556a..0xa0065578|user=M+0xe8；L+0x3c的16B配置表含a01106f2/a0110788/a010f984/user；L+0x10指向M+0x158 vtable，vtable.start=a011e08e、vtable.user=L。线程入口a011e3d6的传参仍同L。配置16B copy继承有效分离/对齐合同前提，不重认证复制算法|
|旧thread/wrapper：0xa011e3f8/e3fc/e428/e42c、0xa011e08e/e09a/e09c/e09e|thread调用start(L,L)；wrapper从第二参L读callback=L+0x3c、user=L+0x48，再以 `(L,user)` 调a01106f2。保留**两层间接调用**，不是把它们压成无证直接边|
|旧start：0xa0110700..0xa0110718|user=M+0xe8，第一个ctx=user+0x8c=M+0x174，第二个ctx=user+0x880=M+0x968；两个调用都a0=保存的L，目标a01ab55a。正好是F11两条ctx来源，而非仅同字段偏移|
|新attach入口：0xa01ab564/568、0xa01ab56a..574、0xa01ab586/58a|s1=ctx、s2=L；先以 `(ctx,0,12)` 调既有零填充接口，再取L+0xc thread-id与opaque当前线程服务返回作比较。**本报告只认证匹配线程的正常分支**到0xa01ab5d4；诊断/其他分支不补行为|
|新attach正常空链：0xa01ab5d4..0xa01ab5e2|L+0x1c为空则先写head=ctx，再 **SW s2,4(s1)**，即ctx+4=L，然后走正常返回。S-format独立核word store对象/偏移|
|新attach正常非空尾插：0xa01ab628..0xa01ab632|读取/遍历next，正常非重复尾部清ctx.next、尾.next=ctx，再跳回 **同0xa01ab5de** 写ctx+4=L。未重做全部watcher/重复注册/关闭生命周期|

因此，在上述**同M、creator成功、有效配置表、thread正常启动、matching-thread attach正常完成**前提下：

```c
// 局部语义表达，非原源码；没有运行这些步骤。
L = M + 0x128;
create_status = creator(&L->queue, 0x80, 4);
// creator正常commit：Q.word18 = 4; L->queue = Q; return 0。
configure_normal_start(L, start=a01106f2, user=M+0xe8);
start(L, user) {
    attach(L, user+0x8c);       // ctx0=M+0x174
    attach(L, user+0x880);      // ctx1=M+0x968
}
// attach的本轮正常分支：ctx.word4 = L。
// F11/F13继承：
I.loop = ctx.word4;             // 同L
Q = word(I.loop+0x18);          // 同Q
n = word(Q+0x18);               // 正常初始化初值4
```

creator对allocation失败的所见路径先清out槽、返回−5；非负打开门之后才提交size/out。没有把局部成功当运行观察。creator与attach都没有在本题归还L/ctx；Q由creator输出而非复制，之后的queue关闭/注销/释放及后续size写入不在本合同。

新增恢复内容为**具体正常实例的size写入与两层callback/attach对象身份桥**；旧body重新定位和旧16B表配置本身不算新增。与F11/3的copy调用/消费是不同连接，F14复核F13不接本题；与G19/J08对象没有身份交集。没有新增完整ROM、整库排除、ISA规则或实机成功结论。

## 未闭精确边

- **仍不能无条件将某次实际F11调用归到这次初始化实例。** 此处认证同M正常setup的静态对象桥；没有实测执行机会、线程成功、attach一定执行或ctx/Q无后续writer。
- 原调用size4在这个正常初始化状态成立；运行期size稳定、全部写入者/替换/关闭生命周期未认证，不外推所有queue/loop的消息尺寸。
- F13的 `0xa0194a14/18→0xa000589c(Msg+0x0c,&局部I,4)` 仍缺**4B实际输入域**的算法认证；旧16/20B不得代用。Msg有效/独立存储、对齐/容量和寿命、native等待/consumer真实执行仍未知。
- 本题creator打开/分配器、attach诊断/异常线程/重复注册分支、callback其他行为及完整事件系统不搭便车。

一个有种子的后继：以本题正常初始化size4为条件输入，只核 **0xa0194a14/18→0xa000589c(dst=Msg+0x0c,src=&局部I,n=4)** 所需的正常4B分支；先明确src word对齐和dst所需对齐/有效性前提，不新导1080B算法、未对齐全域或queue allocator。管理窗口已将这条边登记 **F11/5、F17** 并交另一席 `/root/a56`，本作者没有读取该copy本体，不再重复派发或接管。

交付包含本报告、三份定位/复验源码和[必要合同](../../analysis/miio-queue-size-gap-f15-0041-20261024/contract.json)。生成三份证据JSON忽略留在本地原路径；旧大Evidence只读主仓，不复制。实际检查为15项旧留存定位、19项creator字段、48项身份桥静态检查、JSON解析、必要相对引用/独占范围/空白及`git diff --check`；没有重跑作者/历史技术脚本。全部未提交，作者交付停止，等待非作者复核。
