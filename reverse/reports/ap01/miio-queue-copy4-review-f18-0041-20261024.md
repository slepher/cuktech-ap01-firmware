# F18：n=4复制路径的非作者限定复核

**限定接受F17在F11/5的正常有效word对齐n=4合同，语义纠正0、新增业务0。** 该路线逐byte交错读取/写入4次，前3组依既有局部 `th.lbuia/th.sbia` 规则在旧地址访存后各自postincrement1，最后普通LBU/SB复制第4B，RET返回原dst。路线不调用其他函数、不用栈、不直接把src/dst参数地址另存入持有对象；并非一次LW/SW或原子4B快照。

2026-10-24；非作者 `/root/f12`，任务F18挂原认领 **F11/5**，独占 `re0041-f18` / `codex/re-0041-f18`，固定基线 `bd457a6`。作者 `/root/a56` 已交付F17并停止，主仓[唯一管理记录](rolling-management-0041-20261023.md)已登记本轮非作者复核。遵循最新 [reverse-design](reverse-design.md)、[材料规则](../../analysis/README.md)及 `reverse-engineer-anything` 技能。

只写本报告、[独立复核源码](../../analysis/miio-queue-copy4-review-f18-0041-20261024/review.py)、[必要合同](../../analysis/miio-queue-copy4-review-f18-0041-20261024/contract.json)；[生成证据](../../analysis/miio-queue-copy4-review-f18-0041-20261024/evidence.json)按Git忽略留在原相对路径。不运行F17作者检查器、旧技术脚本、目标/指令/模型、固件、SIM/QEMU、构建、回放、设备或外部服务；不切换共享REA，不改生产/ROM/配置/模型/主树/共享表，不提交或推送，无下级agent。

## 继承结论

|已有出处|继承行为与实际局限|复核处理|
|---|---|---|
|[F13](miio-native-queue-f13-0041-20261024.md)/[F14](miio-native-queue-review-f14-0041-20261024.md)|queue下层先调用0xa000589c(Msg+0x0c,source,n)，返回后才接Msg链；调用事实不认证未知n/地址形状|直接继承调用端/原序，不展开queue/heap/wait/notify|
|F11/4的F15正常初始化身份桥|限定正常同实例的size4初值/ctx-L-Q接线；不证明某次运行已执行、无后续writer或目的存储有效|不以size4替代src/dst对齐、容量、不别名或寿命前提；本题不接F15的独立验收|
|[G03](invalidation-submit-g03-0041-20261023.md)/[G04](invalidation-submit-review-g04-0041-20261023.md)|0xa000589c的对齐16/20B路径已有合同；业务helper0xa008b43a的“copy4”是四word=16B|直接继承差异，不把四word误作n4，不重导旧循环/1080B body|
|[F17作者报告](miio-queue-copy4-f17-0041-20261024.md)|新增的只是0xa000589c n4有限域分支、byte顺序/返回/无直接参数持有|本轮仅非作者复核同差集，旧代码存在不计新发现|

原件为 [CATALOG](../../../roms/CATALOG.md) 的主仓 `roms/0041/ap01-1.0.2_0041.bin`，实查6,769,704B，继承SHA256 `972db4c136c7ed9e24a83c07c1a7fd62040ca018b08ca285216d26b1fee3c6b9`，未重算摘要。映射 `file_offset=VA−0x9ffff000`，不套0031/unsigned/SIM。

旧完整dossier直接读取主仓 `evidence/rea-0041-20261017/evidence/upper-complete.evidence.json#/records/76`，Evidence `ev_32725e49dc86c4d072d48e396f5c14986a521284bea8c8ff59cd533fc995a848`，profile `4825fb58a33a3e7d618557975b153b8318cf7e833d190ad16bcbf8bd441ae621`。只保留本路线17条旧assembly，未复制整个179MB导出或1080B函数；新原字段证据没有新造REA ID。

## 本轮复核或纠正

独立检查器直接读取原件3个窗口：`[0xa000589c,0xa00058ae)`、`[0xa00058f6,0xa0005918)`、`[0xa000591c,0xa0005920)`，合计 **56B、17位置，30项PASS**。普通指令使用 **Capstone 5.0.7 / RV32+RVC**；6个厂商word保留UNDECODED展示，独立拆字段后才按原局部规则解释。B-format/CJ目标、末LBU/SB编码另外独立解算。没有把反编译或F17脚本输出代替原字。

|复核问题|独立原字段/规则依据|裁定|
|---|---|---|
|n>7与n==4门|0xa00058a4 `63e4c708` 是unsigned BLTU a5,a2，前a5=7；n4不跳0xa000592c。0xa00058aa `6309e606` 是BEQ a2,a4，前a4=4，目标0xa000591c|接受n4选路，不取别的length或大长度循环|
|短长度跳转|0xa000591c `aa87` 令a5=入口dst；0xa000591e `e1bf` 的CJ目标独立解到0xa00058f6|接受同dst基址，非某个word helper|
|3次byte读|0xa00058f6/58fe/5906均 `0bc71598`；独立字段opcode0x0b/rd14/f3=4/base11/simm1/shift0/top5=19|按既有th.lbuia规则读旧a1的U8到a4后a1增1；rd与base不同，未套错误body/宽度|
|3次byte写|0xa00058fa/5902/590a均 `0bd71718`；字段opcode0x0b/rd14/f3=5/base15/simm1/shift0/top5=3|按既有th.sbia规则先写旧a5的byte，再a5增1，保持load/store交错|
|最后1B|0xa000590e `03c70500` 独立I-format为LBU a4,0(a1)；0xa0005912 `2380e700` S-format为SB a4,0(a5)|此时两基址分别原src+3/dst+3，接受第4B；不是先收集完整4B快照|
|返回/直接持有|0xa000589e虽把dst存a6，所选路线没有写a0；0xa0005916 `8280` JR ra。17位置中没有JAL/JALR、栈访存或full pointer store，所有内存写是所述byte数据|接受返回原dst、无callee/栈依赖/直接参数地址持有。载荷4B若含I指针值，复制该值不代表retain/deep-copy I或负责I生命周期|

厂商规则只继承主仓 `evidence/rea-0041-20261017/ghidra/Ghidra/Processors/RISCV/data/languages/ap01thead2.sinc`：`:th.lbuia`（现文件行6431）与`:th.sbia`（行6461）。本轮独立核其 **`ea=rs1`、byte load/store、`thbase=rs1+(simm<<shift)`** 的先后，及文件行3 `thbase: r1519 ... export r1519` 表明更新同base寄存器。规则原文/行号保留在本地JSON；这不是新厂商ISA规范认证，也没有执行/修改模型。

局部表达（非原源码，非指令执行；仅本题有效word对齐等前提域）：

```c
// n==4静态选路；不论初始对齐，当前已验域仍只取注册的word对齐输入。
dstp = original_dst;
srcp = original_src;
byte(dstp++) = u8(srcp++); // 旧地址访存，然后各自+1
byte(dstp++) = u8(srcp++);
byte(dstp++) = u8(srcp++);
byte(dstp)   = u8(srcp);
return original_dst;
```

上式每组读后立刻写；没有把4B写改为原子SW或memmove全域。无并发干扰且满足本题存储前提时，复制源4B值，helper返回后无需再借source继续本路线读取；目的内容若本身代表指针，仍是被复制的数据，不能据此认证上层对象所有权。

## 真正新增

**新增业务0、helper恢复新增0、语义纠正0、ISA/来源认证0、整库排除0。** 本轮提供F17同范围的非作者独立字段/规则/选路证据和限定接受；重读同56B不算新ROM功能。

F11/5复核与F11/4初始化、F11/3queue消费分别保留身份/存储条件；共用0xa000589c只是必要节点继承，不重开G03/G04四word或n16/20研究，也不扩未对齐/任意length/heap。

## 未闭精确边

仍未知某次F11调用是否满足本题输入域：实际src/dst有效性、容量、对齐、不受其他写干扰/适当分离及Msg存储寿命；没有观测真实复制/入队/consumer/云端完成。Q.size4身份即使正常初始化已证，也不能替代这些前提。完整copy算法、其他length、未对齐/任意重叠、原子快照、库精确来源均未认证。不能从helper局部合同直接断言“F11caller栈必可失效”。

一个有种子的后继边为F13既知调用 `0xa0194a14/18→0xa000589c(dst=Msg+0x0c,src=&局部I,n=word(Q+0x18))` 的**实际目的Msg来源/有效存储与地址形状前提**，须由管理窗口先查重登记后另核；本题只保存seed，不沿queue allocator/wait展开。F11/4正常size身份独立维护，不因本轮复核自动认证其运行状态。

实际检查包括30项静态检查、JSON解析、报告相对引用在本树或整合主树可定位、空白/独占文件与 `git diff --check`；没有运行F17或历史技术脚本。交付源码/合同/报告未提交，生成证据JSON受忽略保留，复核者完成后停止。
