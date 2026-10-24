# F22：候选消息来源与哨兵摘尾的非作者复核

**限定接受F21在F11/7的候选来源及正常42B链helper合同；语义纠正0、新增业务0。** getter覆盖原a0，先从gp+0xb8链取尾节点，非零原值返回；空时才重读word(0x62fc6034)，非零从gp+0xc0链取节点并直接返回（第二链空也直接0），零才向0xa002fcc8请求332B，返回非零只写byte(M+8)=1。

链helper在正常有效哨兵/节点前提下摘出N、修复邻接、重读N+4，先清N+4后清N+0，返回原N。这个解除链接合同**不认证节点大小、有效容量、对齐、独占、无别名或寿命**；332B只是请求，`332−12=320`不是实测/已证可用容量。

2026-10-24；非作者 `/root/f12`，任务F22挂原认领 **F11/7**；固定基线 `bd457a6`，独占 `re0041-f22` / `codex/re-0041-f22`。F21作者 `/root/a56` 已交付停止，主仓[唯一管理记录](rolling-management-0041-20261023.md)已登记本轮复核。沿最新 [reverse-design](reverse-design.md)、[材料规则](../../analysis/README.md)及REA技能，先继承留存，只核本差集。

没有运行F21作者检查器、历史技术脚本、目标/指令/模型、固件、SIM/QEMU、构建、回放、设备或外部服务；不读heap/池初始化/调度callee，不切换共享REA，不改生产/ROM/配置/模型/主树/共享表，无下级agent、提交或推送。只写本报告、[独立源码](../../analysis/miio-queue-message-source-review-f22-0041-20261024/review.py)、[必要合同](../../analysis/miio-queue-message-source-review-f22-0041-20261024/contract.json)，[生成证据](../../analysis/miio-queue-message-source-review-f22-0041-20261024/evidence.json)忽略留在本地原路径。

## 继承结论

|已有出处|行为与实际边界|本轮差集|
|---|---|---|
|[F13](miio-native-queue-f13-0041-20261024.md)/[F14](miio-native-queue-review-f14-0041-20261024.md)|正常候选调用0xa0197acc→0xa01318de，原a0仍Q；非零结果作为M交下层copy/接链。caller先读flag，仅非零才落到此call|旧caller连接继承，不重做send/queue对象或copy；本轮只核来源/条件申请与返回|
|[F21作者报告](miio-queue-message-source-f21-0041-20261024.md)|两gp链/重读flag/条件申请、byte标记与42B正常helper合同|同认领下非作者复核，不另开来源题或重复全heap|
|[G11](display-ready-producer-g11-0041-20261024.md)/[G12](display-producer-review-g12-0041-20261024.md)|另一backend+0x3c链也调用0xa010d70e，未认证本gp池大小或全部生命周期|共用callee不等于同容器/节点大小，不套显示对象布局|
|F19 receive差集|另以H=K+0x18调用同链helper，属于接收端自己的队列容器|本轮通用有效哨兵合同可供条件继承；gp两池与K队列不合并身份，不验收F19其他本体|

原件为 [CATALOG](../../../roms/CATALOG.md) 主仓 `roms/0041/ap01-1.0.2_0041.bin`，实查6,769,704B，继承SHA256 `972db4c136c7ed9e24a83c07c1a7fd62040ca018b08ca285216d26b1fee3c6b9`，不重算机械摘要；`file_offset=VA−0x9ffff000`。不套0031/unsigned/SIM。

旧metadata位于主仓本地忽略 `reverse/analysis/whole-rom-coverage-0041-20261023-round1.json`：0xa01318de extent `ev_1f1e3392319d6066dfa0ec7153bc38011175d4593b14a5c98911e7e25e0ddfc8`、directcall `ev_bf2124b1c8f7a4884a8d71ba4cc962d18dc9ee9e7b0e244fb5be4ac81c9ae0e8`；0xa010d70e extent `ev_307bfa85996bc49ba8033818c20586927cfad86def6317ebd4804f3be509ed03`、无callee directcall `ev_460634c36b25a27df15c7629aa1ba0823995e3bc867a320cfd2a893f3fe38c0f`。它们只定位，不当作已验语义；本轮Capstone/原字段复核没有新造REA ID或把旧profile重标。

## 本轮复核或纠正

独立检查器直接读原件 `[0xa01318de,0xa0131920)` 与 `[0xa010d70e,0xa010d738)`，两小函数的必要条件/返回总 **108B、41条普通指令，35项PASS**。使用 **Capstone 5.0.7 / RV32+RVC**，另独立解两JAL、申请AUIPC/JALR、sentinel B-format及三处S-format宽度/偏移；没有厂商未知字或模型语义依赖。没有运行/导入F21检查器，未取allocator/池初始化/调度body。

|复核点|独立字段/控制依据|裁定|
|---|---|---|
|覆盖原a0与第一池|0xa01318e6 `1385810b`，a0=gp+0xb8；0xa01318ea目标独立算0xa010d70e；0xa01318ee非零跳共同尾声|接受；不是把入参Q/K/n当分配尺寸或池对象|
|flag重读与第二池|0xa01318f0/f4读取word(0x62fc6034)，只在第一池空后出现；f8零到0xa013190a，非零以gp+0xc0调同helper|接受重读；不缓存caller第一次flag或把它命名为未经来源认证的状态|
|第二链空返回|0xa01318fe调用后顺序落到0xa0131902..1908，尾声未改a0，无“空再申请”分支|接受第二池空也直接0，不能改为两池均空才申请|
|332请求与marker|0xa013190a令a0=0x14c；190e/1912独立算到0xa002fcc8。1916返回0跳尾；非零1918/191a只SB1到原a0+8|接受请求数值/条件byte写；不认证真实分配容量、清零、成功或整体节点布局|
|N与空链|0xa010d714读N=word(H+4)，716的BEQ独立解到d734；N==H则a5=0再共同返回|接受sentinel空门；不是N==NULL或取H.next|
|邻接写与重读|d71a读P=N+4，d71c读R=N+0；d71e写P.next=R；**d720再读N+4**，d722写R.prev=P|接受原序，不把第二读优化为稳定值|
|清槽/返回|d724 `23a20700`为SW0到N+4；d728 `23a00700`为SW0到N+0；d72e将原a5=N给a0，JR ra；空链汇同尾声|接受先+4后+0、返回原节点。helper无callee，不分配/复制节点或另retain调用者对象|

F13必要caller行从主仓 `reverse/analysis/miio-native-queue-f13-0041-20261024/evidence.json`只读继承，不重跑脚本：0xa0197ac2/7ac6取flag，7aca零跳过7acc，7acc才调用本getter；非零结果经7ad0→7b12..7b1a交正常send。这证明本caller**第一次读flag非零才进getter**。

若第一池空后getter第二次flag与第一次保持同值，且链操作不通过别名改变flag/读值，那么它继续第二池并直接返回，不走332B申请。**这些稳定、无别名/无异步修改前提尚未认证，不能据第一次非零排除申请分支，亦不能说某次实际申请发生。** 本轮没有运行条件变化试验或据此推缺陷。

局部语义（非原源码；仅正常有效链/ABI前提）：

```c
M = remove_last(gp+0xb8);
if (M != 0) return M;
if (word(0x62fc6034) != 0)
    return remove_last(gp+0xc0);     // 空也直接返回0
M = request_interface(0x14c);
if (M != 0) byte(M+8) = 1;
return M;

// remove_last(H)；别把重读删去：
N = word(H+4);
if (N == H) return 0;
P = word(N+4); R = word(N);
word(P) = R;
P = word(N+4);
word(R+4) = P;
word(N+4) = 0;
word(N) = 0;
return N;
```

上式表明链上解除连接与原指针返回；它不等同于全系统独占、没有其他alias、payload容量充分或对象持续有效。getter没有本层payload拷贝/最终归还；后续调用者责任沿F13/F19各自合同，不由本轮补猜。

## 真正新增

**非作者复核新增业务0、语义纠正0、ISA/来源认证0、整库排除0。** F21的正常两链/条件申请及42B helper合同获得限定接受，重读同108B不是新功能。

H=gp+0xb8、H=gp+0xc0是两条不同池表达式；G11的H=backend+0x3c、F19的H=K+0x18又是不同对象。正常泛化helper合同可按其有效sentinel前提引用，但不能把相同callee作为池/queue身份或容量证据。gp的绝对值仍未知。

## 未闭精确边

仍未知gp绝对base、两池初始化/填充writer、链节点真实大小和payload容量、池同步/独占/别名/对齐/寿命、flag两次读取稳定性、申请服务内部和正常返回存储保证、实际候选/queue/consumer运行身份。332B仅请求；只有另有连续有效申请区合同等前提，才可谈从+0x0c剩余320B的条件算式，本轮不把算式写成实际可用容量。

一个有种子的后继是 **H=gp+0xb8/gp+0xc0的节点初始化/填充写入者→真实节点存储来源/大小**，由管理窗口先查重登记，必要时先定位gp来源和旧writer metadata，不泛扫整heap。此处不接新writer/allocator或调度，也不将未闭边变成假成功。

实际检查包括35项独立字段/目标检查、JSON解析、报告相对引用在本树或整合主树可定位、空白/独占范围及 `git diff --check`。生成证据JSON本地忽略保留，源码/合同/报告未提交，复核者交付后停止。
