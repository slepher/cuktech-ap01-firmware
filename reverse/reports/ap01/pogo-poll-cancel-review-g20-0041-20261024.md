# G20：Pogo poll 软件撤销与同 fd 提交接入独立复核

2026-10-24；研究基线 `0ea89ca`，独占树/分支 `re0041-g20` / `codex/re-0041-g20`；派发管理基线 `02afb05`。**挂原认领 G19/1、G19/2，限定接受 G19，本轮实质语义纠正0、复核新增功能0。** 接受的是软件mask、链持有、记录更新和调用端ABI/返回消费；不认证OS撤销成功、callback排空、恰好一次或完整Pogo关闭。

已完整读取主仓最新 [reverse-design.md](reverse-design.md) 和唯一 [链条认领表](rolling-management-0041-20261023.md)，不以旧worktree副本授予认领。只核两行本轮差集及必要前提，未另开研究认领；G19/3仍仅为未派锚点，没有读取 `0xa009e0e6` 或 `0xa010e722` 下层body。复核者未参与G19生产，使用已读 [REA技能](C:/Users/cogic/.agents/skills/reverse-engineer-anything/SKILL.md) 的证据/边界纪律，没有运行或导入G19验证器，也没有把其JSON当作原件。

## 继承结论

|认领/旧出处|已解释的行为与局限|本次差集|
|---|---|---|
|G19/1、G19/2；[G19](pogo-poll-cancel-backend-g19-0041-20261024.md)、[J05](transport-reuse-gap-j05-0041-20261024.md)|作者已补两个backend callee；J05已查父级complete/final/SIM、较晚专项及旧extent/实参种子|G19为待审主张，独立原件核实际字段/门/调用端；不重跑J05负搜索、最终ZIP或整资源盘点|
|C06/1；[C06](pogo-close-dispatch-review-c06-0041-20261023.md)|type8 close进入 `0xa009f972` 后登记pending；callback收原poll与业务计数另有合同|直接继承close入口，不重做pending消费、timer或ctx释放，不把登记等同后续已drain|
|G07/1；[G08](display-alternate-review-g08-0041-20261023.md)|stop实参为 `(L,W=P+0x34,0x17)`，之后active/loop计数与 `(L,word(P+0x58))` 原序已验|直接继承stop实参/顺序，只复核 `0xa009f442`、`0xa009e212` 的本轮差集|
|G09/1；[G10](display-ready-review-g10-0041-20261024.md)|W.fd@+0x24与P+0x58同址；W+0x14为fd桶节点，W+0x0c为更新节点，+0x1c请求mask与+0x20比较槽已定位；ready条件回调另有范围|继承同watcher/同fd布局，不重验注册和ready投递，不套用其他MiIO对象|
|F03/1；[F04](miio-loop-close-review-f04-0041-20261023.md)|`0xa0098b4a(node)` 仅双链摘除，不free、不清node、不自环|直接继承helper；本轮核f442实参与其后自环/计数责任，不重新验通用unlink|
|旧page-logic record15；G19所引 `ev_794a176f91454b7304c06fbfaff53024aa96bf8a3a51698dbb831f8b9359f9ef`|`0xa0024906(dst,0,16)`按字节填充的旧合同|仅核本次栈16B调用端，不展开算法或认证标准库来源|

原件统一引用 [CATALOG](../../../roms/CATALOG.md)：AP01 `1.0.2_0041`，主仓 `roms/0041/ap01-1.0.2_0041.bin`，6,769,704 B，既有SHA256 `972db4c136c7ed9e24a83c07c1a7fd62040ca018b08ca285216d26b1fee3c6b9`，映射 `file_offset=VA−0x9ffff000`。本路只核长度并引用既有摘要，没有另算hash；不是0031、unsigned候选或SIM ELF。旧complete/SIM是其受控范围，不能认证ROM ABI或本次OS效果。

## 本轮复核或纠正

独立 [review.py](../../analysis/pogo-poll-cancel-review-g20-0041-20261024/review.py) 直接只读上述主仓原件。标准RV32/RV32C指令用Capstone 5.0.7离线解码，另外自行按bit位核JAL、B、C.B、C.J、word访存与10条indexed厂商字段。结果见 [review-result.json](../../analysis/pogo-poll-cancel-review-g20-0041-20261024/review-result.json)。只保存必要锚点，未重新导出两完整函数或源码，不生成新REA Evidence ID。

本路字段记号沿G19：`A=word(L+0x34)` 是桶数组指针，桶哨兵为 `A+(fd<<3)`；不能把它写成直接对L内联偏移寻址。`B=word(L+0x14)`，`R=word(B+0x114)`；R正式类型/producer未知。W.fd@+0x24、record.fd@+8、下层handle `word(L+0x20)` 是三个不同字段，不能把record写−1说成W.fd被改写。

|原认领/主张|独立原件锚点与判定|接受边界|
|---|---|---|
|G19/1：f442的mask门|`0xa009f442/444/446`读W.fd并比较−1；`0xa009f458/45a`保存W/L；`0xa009f472/474`容量为word、BGEU。`0xa009f478..486`读W+0x1c、NOT mask、AND并写回，以结果非零分流|接受按 `old_mask & ~mask` 清指定位，不能把stop传0x17无条件等同整个字段清0；普通fd前置沿旧限制，不验证异常fd/assert行为|
|G19/1：零mask撤销更新节点|`0xa009f488/48a`以W+0x0c调unlink；`0xa009f48e/492`分别SW该节点地址到W+0x0c/+0x10；`0xa009f496`清W+0x20|接受摘链→caller自环→清比较槽原序，不能把这些副作用归到通用unlink或对象free|
|G19/1：仅撤销同W的fd桶节点|`0xa009f49a/49c/4a0`重读fd/A并取head；`0xa009f4a4`保存next。`0xa009f4c4/4c8`比较node−0x14与W，相等才 `0xa009f4cc`摘除；`0xa009f4d0/4d4/4e8/4ea`检查/递减L+0x3c；`0xa009f4ee..506`重读哨兵，按保存next继续|接受逐节点身份与登记计数责任。不是清空同fd桶，更不代表该fd的其他W被撤销|
|G19/1：非零mask只排更新链|`0xa009f508/50a`比较W+0x0c.next与自身；相同才 `0xa009f50e..51c`尾插L+0x2c/+0x30；`0xa009f520`回公共尾声|接受已排队则不重复插入；此分支保留比较槽及fd桶持有，不直接下层提交|
|G19/2：B/R及R空的直达路径|`0xa009e222/22a`取L+0x14、B+0x114；`0xa009e232..23a`初始化stack16。`0xa009e246`容量BGEU和 `0xa009e256`空桶比较决定直达op2；`0xa009e25a..266`四参真实为 `(word(L+0x20),2,fd,&stack16)`→`0xa010e722`|接受该直达路径没有聚合op3的signed handle门，不能把另一分支的谓词搬来|
|G19/2：R空的剩余mask聚合|`0xa009e2f0..2fe`将node+8即W+0x1c逐项OR到stack.word0；`0xa009e302/306`signed handle<0直接返回，否则 `0xa009e30a`跳到写fd/置op3的共用调用端|接受逐仍登记W的聚合。没有额外aggregate!=0门；不认证mask对应OS状态或实际ready|
|G19/2：R非空按记录和fd匹配|`0xa009e27a..298`索引0、record stride16、record.fd@+8匹配，count为R+8并用signed BGE；`0xa009e29c`indexed SW清record.word0；`0xa009e2a0..2e6`取同fd桶，将node+8请求mask OR回该record|接受同fd剩余集合，不是只看刚停的W；signed记录count与unsigned fd容量门分别保留|
|G19/2：匹配记录的零/非零结果|`0xa009e2be`零结果转 `0xa009e2e8`，SW −1到record.fd，随后index+1继续；非零时 `0xa009e2c2/2c6`signed handle门，`0xa009e2ca..2da`写stack mask/fd并以op3四参调用后返回|接受零mask不减R.count、不free数组；非零服务路径直接退出，不保证继续处理所有同fd记录，也不进入扫描完成六参路径|
|G19/2：扫描完成的六参调用|记录扫描门回 `0xa009e232`再次清stack16；R非零经 `0xa009e23e`到 `0xa009e30c..320`，真实调用为 `(word(L+0x20),B+0x84,word(R),2,fd,&stack16)`→`0xa009e0e6`|仅接受调用端ABI，不读下层body、不为op2命名OS操作，不证明复制/retain或提交成功|
|G19/2：服务后比较槽清零与返回消费|`0xa009e324/328`重读容量，仍在范围才 `0xa009e32c..348`逐桶节点SW0到node+0x0c即W+0x20。四参服务后 `0xa009e26a..278`仅恢复并返回，a0不被比较/替换；六参服务后首先读容量并继续清槽，没有成功判断|接受软件清槽不是成功回执。R空和非零mask早退四参路径不执行此段全桶清槽；不同路径不认证统一业务返回值|

10条indexed原字的字段独立读取一致：`0xa009f4a0/4ae/4f4`、`0xa009e24e/252/29c/2a4/2b2/2e0/334`。本路重新只读既存 `ap01thead2.sinc` 第6/6564/6596行定义，核opcode/funct3/top5/rd/rs1/rs2/shift与`addsl/lrw/srw`语义：加`rs2<<shift`、word读/写。模型仅作既有局部规则来源，不等同独立厂商规范、原源码或精确libuv/NuttX版本认证；未修改或执行模型。

上述逐项限定接受，实质纠正0。节点保存next、重读fd/桶/容量和原位record写入是原字事实；“软件兴趣/比较槽/记录上下文”是受限分析命名。清链不转移W或业务context所有权，record数组仍是R中已有指针。stack16属于当前调用栈；这里只证明指针被传给两个服务，没有证明下层借用结束、复制或保留方式。没有将保存next解释成并发或重入安全保证。

## 真正新增

**复核新增功能0、新ISA规则0、来源排除0、整函数/资源/源码导出0。** 交付只是原G19/1、G19/2差集的非作者独立技术接受。C06/1、G07/1、G09/1和F03/1保持原限定接受，不重计其close/stop/ready/unlink成果。没有因软件撤销成立就升级为OS/设备效果或全生命周期完成。

## 精确未闭与实际验证

仍未知：`0xa010e722`/`0xa009e0e6`服务实现、op正式语义、stack16消费/复制/持有与实际提交结果；B+0x114的R producer/正式类型/生命周期；并发与重入、OS/设备真实撤销、已有callback排空及恰好一次；Pogo timer停止、context最终释放、close后pending再次消费。G19的这些断边保留正确，局部接受不等于原ROM完整恢复。

实际运行本路独立静态脚本：**142项稀疏检查PASS，其中10条indexed字段；另核3个既有规则定义和CATALOG原件长度**。JSON、报告相对链接及diff检查通过。没有运行G19脚本、ROM、SIM、QEMU、构建、回放、模型、设备或外部服务；没有漏洞/异常输入/缺陷验证，没有生产/ROM/配置/模型或共享管理表写入。

后继只引用已登记 **G19/3**：`0xa009e320→0xa009e0e6` 的六参调用下层消费合同，旧extent `ev_5ecc1c04…`/directcall `ev_054cff13…`已在G19留存。它本次未派、未读body；必须先由管理窗口核旧出处不足并登记本体差集后另派，不能以G20新名字扩展到该服务、`0xa010e722`或完整backend。本路提交后结束，不自行接题。
