# F16：F11/4 同M正常setup的queue size4身份桥独立复核

2026-10-24；认领 **F11/4**，非作者复核 `/root/a56`，作者F15 `/root/f12` 已交付停止；固定基线 `bd457a6`，独占 `re0041-f16` / `codex/re-0041-f16`。主仓[唯一认领表](rolling-management-0041-20261023.md#链条认领表)已登记F16。遵循主仓最新[流程](reverse-design.md)、[本地保留规则](../../analysis/README.md)与REA技能的留存优先边界。

**限定接受F15，语义纠正0、新增功能0。** 在同M正常creator成功、配置/线程接口及matching-thread非重复attach正常成立的条件下，`L=M+0x128`、`L+0x18=同Q`、`Q+0x18初值=4`；两个ctx分别为M+0x174/M+0x968，均保存同L到ctx+4。该结论是一个具体正常初始化状态的静态身份桥，不是观察到某次send已经经过setup、证明后续无writer或认证所有queue都是4B。

未运行作者三个脚本、旧技术脚本、目标/指令/固件/模型、SIM/QEMU、构建、回放、异常输入、设备或外部服务；不打开/切换共享REA、不改生产ROM配置模型或共享表，无下级agent、提交或推送。只读主仓旧留存及最小原字段，不读取copy4算法、allocator或新callback本体；生成JSON本地原路径忽略保留。

## 继承结论

|出处|继承行为与本轮不扩展的界面|
|---|---|
|[F11](miio-request-ownership-f11-0041-20261024.md)/[F12](miio-request-ownership-review-f12-0041-20261024.md)|两正常ctx为manager+0x174/+0x968，I.loop取ctx+4；type1跨线程caller取Q=word(L+0x18)。请求/I持有合同直接继承，不重构造或回执|
|[F13](miio-native-queue-f13-0041-20261024.md)/[F14](miio-native-queue-review-f14-0041-20261024.md)|copy长度来自word(Q+0x18)，先调用copy接口再接消息链/改计数。只接同Q size初始化身份，不重验wait/notify/heap/copy域|
|[G03](invalidation-submit-g03-0041-20261023.md)/[G04](invalidation-submit-review-g04-0041-20261023.md)|正常有效、分离、word对齐16B值复制合同用于本题配置表的解释；接口条件和ABI直接继承，不新认证复制算法或配置实际执行|
|[F15作者报告](miio-queue-size-gap-f15-0041-20261024.md)|creator size/out字段及两层callback/attach身份桥。其三份脚本自检不代替独立接受，本次另写位域/旧行检查器，不运行或导入作者代码|

原件沿[CATALOG](../../../roms/CATALOG.md)：AP01 `1.0.2_0041`，主仓 `roms/0041/ap01-1.0.2_0041.bin`，6,769,704B，既有SHA256 `972db4c136c7ed9e24a83c07c1a7fd62040ca018b08ca285216d26b1fee3c6b9`，VA映射`file_offset=VA−0x9ffff000`。仅核长度、继承摘要，不重算哈希；不套0031/unsigned/SIM地址。

旧对象桥统一读 `evidence/rea-0041-20261017/evidence/upper-complete.evidence.json` 的必要行，全部profile为 `4825fb58a33a3e7d618557975b153b8318cf7e833d190ad16bcbf8bd441ae621`：

- records[248] master0xa0064368，EID `ev_c3dd842723b83165bc8e1a6b235f2005269080da4969520bd0c0f0e413db133a`。
- records[195] thread0xa011e3d6，EID `ev_9a7e0a186c4ed2b341b4d42187fcb73bebec13d401cd226033d30027d121387d`。
- records[96] wrapper0xa011e08e，EID `ev_4765a2915f077a6cb63cd6f59f598f6642d3ee1b1c9c4663e62bea464b4ee7c0`。
- records[27] start0xa01106f2，EID `ev_13c2f5afa1fcfb7c53c117ed097c6a6af54098e5ea57a4724fa9c77a93d547cd`。

只复用必要行和既有线程/配置接口，不复制整dossier。creator/attach的旧extent/directcall EID沿F15定位，本次没有新REA生产Evidence ID/profile；原字段JSON是独立静态复核产物。

## 本轮复核或纠正

本次新原字段验证使用自行拆RV32/RVC位域，未依赖Capstone或作者指令预期文本：C.MV/LI、I/S-format、word宽度、signed成功门、B/C.BNEZ/C.J目标等；另独立核旧对象桥的参数/偏移及必要callback行。

|连接/必要锚点|独立结果与裁定|
|---|---|
|旧master `0xa0064f4a` 与 `0xa0065438/5448/544c`|s7=M+0x128=L，a2=4、a0=M+0x140传creator；算得0x128+0x18=0x140。不是从source=&I猜size。旧master此段普通s7定义筛选无覆盖，普通callee-saved ABI为继承前提，不认证所有动态别名|
|新creator `0xa005f0c0/0c4/0c6/0cc/0e4`|原out存s2、a1存s4、a2存s3；非零候选分支到0xa005f0e4，s1保存同返回Q。分配器body未展开，非零有效结果是正常前提|
|`0xa005f11a/11e/12a`|原capacity/size按word写局部attrs，BLT/非负门精确为BGE a0,zero→0xa005f136。打开服务及该分支之后的服务正常返回按F15界面条件保留，不认证其完整实现|
|`0xa005f142/144/148`|a0置0，然后SW原a2(s3)到Q+0x18，再SW同Q(s1)到原out(s2)。本实例原a2=4，所以Q.size初值4、L.queue=同Q；均是word，没有把size写到另一对象或半字|
|旧master user及配置表 `0xa0064da6/53ac/53b0/53b4/53d8`|user=M+0xe8；表首word由0xa0110000+0x6f2构成start0xa01106f2，user置表+0x0c。n16配置复制目的M+0x164=L+0x3c，故L+0x48持该user。copy16有效/分离/对齐前提不省略|
|旧master `0xa00653e0/53e4/53e8/53fe/548e/549e`|M+0x158的start为0xa011e08e，M+0x160=该vtable+8保存L；L+0x10=M+0x138保存M+0x158的地址。vtable.start/user和L.callback/user是两个不同层，不能压成一条无证直接调用|
|旧thread `0xa011e3f8/e3fc/e428/e42a/e42c`|取L+0x10 vtable、取其start，a0=L、a1=vtable.user=L再间接调用；线程入口/参数L从旧master接口继承，未认证线程实际已启动|
|旧wrapper `0xa011e08e/e09a/e09c/e09e`|以第二参L读L+0x3c callback，再a0=L、a1=word(L+0x48)=user调用start。保留这层间接ABI，不用名称猜callback身份|
|旧start `0xa0110700..0718`|先保存user再算ctx0=user+0x8c=M+0x174，保存L；另以user+0x880=M+0x968作ctx1。两次目标0xa01ab55a，a0均是保存同L。不是由不同对象同字段偏移推相同身份|
|新attach `0xa01ab564/568/56a/56c/56e`|s1=ctx、s2=L；传 `(ctx,0,12)` 给既有清零接口，仅认参数/界面，不接该helper全域或新callee。此处不靠假设清零成功来代替后续ctx+4实际SW|
|`0xa01ab586/58a`|LW L+0x0c与a0服务返回作BEQ，匹配到0xa01ab5d4。本题仅该matching-thread正常分支，不认证实际thread-id或异常/诊断返回|
|`0xa01ab5d4/5d8/5da/5de`|head=word(L+0x1c)；空链先SW ctx到head，然后SW L到ctx+4。S-format独立核源/基址/偏移4与word宽度|
|`0xa01ab5e4/5e6/628/62a/62c/630/632`|非空链以current比较ctx，非重复到0xa01ab628取next；next非零回遍历，正常尾部先清ctx.next，再把ctx挂尾，CJ到同0xa01ab5de执行ctx+4=L。未展开重复项/诊断/关闭路径|

没有发现F15语义错误。补核非空链必要MV/BNE共6B只用于确认其正常非重复尾部如何汇合，不是新列表服务恢复；没有沿其余链/字段扩范围。明确保存了same-M、creator及opaque服务正常返回、配置16B有效存储与ABI、thread正常接口、matching-thread非重复attach等条件。

局部身份合同（非原源码；正常路径静态表达）：

```c
L = M + 0x128;
// 成功creator提交，原a2由master明确传4：
word(Q + 0x18) = 4;
word(L + 0x18) = Q;
// 配置及两层间接start按上述条件发生：
ctx0 = M + 0x174;
ctx1 = M + 0x968;
// 各自matching-thread正常attach的空链/非空尾插汇合：
word(ctx0 + 4) = L;
word(ctx1 + 4) = L;
// 接回既验F11/F13：从该ctx+4得L、L+0x18得Q、Q+0x18初值4。
```

两个ctx的最后两项是各自调用条件下的结果，不表达同一时刻必执行或任意ctx都接同L。Q为输出指针值，没复制整个Q；L/ctx/Q后续所有者与归还并未由这些SW认证。

## 真正新增

新增业务/语义纠正/ISA或整库排除均0。新增为非作者独立原字段和旧身份桥复核证据，对F11/4作限定接受；不把原body重读或额外6B检查计作新增功能。copy4算法/F11/5不在本项接受范围。

## 未闭精确边与实际检查

仍未知某次实际send是否经过本次setup/配置/attach、thread正常启动/执行机会、ctx+4/L+0x18/Q+0x18后续writer/替换、运行期size稳定、完整queue生命周期、实际consumer或交付。不能把“初始化初值4”改成所有queue/loop固定4B。copy源/消息目的有效/对齐/容量与持续寿命、allocator/wait/notify和callback其他行为由其他具体合同处理，本项不读取或认证。

有种子后继：若要把本静态正常初始化桥推广到某个具体调用状态，必须以 **0xa005f144/148的Q.size/out发布与0xa01ab5de的ctx.loop存槽** 为已知端另查后续writer/实际对象状态证据，先由管理窗口查重登记；本项不无种子扫描所有queue，也不重派本身份桥。若无这类输入，则保留条件合同即可，不为“全局完成”补假设。

[review.py](../../analysis/miio-queue-size-review-f16-0041-20261024/review.py) 实际 **79项PASS，29个新原字段锚点、82B**，其余为四个旧record/profile/必要行和偏移一致性检查。两次小范围探索用于核branch/正常尾插，未取其他body；复验样本不冒充全部探索读量。结果见本地忽略的 [review-evidence.json](../../analysis/miio-queue-size-review-f16-0041-20261024/review-evidence.json)，只保存原字/偏移与选定旧行，不复制大dossier。JSON、相对链接、Git忽略及diff检查通过；没有运行作者三个脚本或新算法。交付后停止本项，供主窗口整合/补位，无提交推送。
