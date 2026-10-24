# G22：认领G19/3实际op2非fallback条目接入独立复核

2026-10-24；管理/研究基线 `bc3711a`；独占树/分支 `re0041-g22` / `codex/re-0041-g22`。**挂原认领G19/3，限定接受G21；无原字或核心语义纠正，复核新增功能0。** 实际op2分支先写tail，再copy16，随后读entry数组并zero64、按原序写字段；条件下层调用使用原scratch基址，返回未被本体判为成功。接受带有效存储/对齐/容量前提，不认证所有地址、OS提交或存储复用协议。

复核者未参与G21研究。已完整读取主仓最新 [reverse-design.md](reverse-design.md) 和 [唯一认领表](rolling-management-0041-20261023.md)，不以旧worktree副本授权认领；仅核本行差集。G19/4的 `0xa009dfcc` 只保留调用端锚点，未读body；`0xa010e722`、native service和整个ring后端不在本轮。使用已读 [REA技能](C:/Users/cogic/.agents/skills/reverse-engineer-anything/SKILL.md) 的边界/证据规则，没有运行或导入G21脚本，没有以其JSON替代原件。

## 继承结论

|认领/旧出处|已解释连接与局限|本轮差集|
|---|---|---|
|G19/3；[G21](pogo-poll-submit-g21-0041-20261024.md)|作者补了实际op2、submit_ctx+0x3c非−1分支的副本/条目/条件调用；旧300B extent/directcall元数据已有|G21是待审主张，直接读必要原字核字段、顺序和返回；不导出整300B函数|
|G19/1、G19/2；[G20](pogo-poll-cancel-review-g20-0041-20261024.md)|软件取消、同fd聚合与 `0xa009e320→0xa009e0e6(word(L+0x20),B+0x84,word(R),2,fd,&stack16)` 已独立限定接受，调用端不判成功|实际输入和stack16已初始化前提直接继承，不再验取消/聚合/stop/ready/close；不套用其他对象|
|G11/1；[G12](display-producer-review-g12-0041-20261024.md)|六参ABI及submit_ctx+0x3c==−1的四参fallback已有独立接受，ADD/ready相关纠正保留|只核非fallback入口绑定，不重验fallback或ADD/MOD/producer|
|[G03](invalidation-submit-g03-0041-20261023.md)、[G04](invalidation-submit-review-g04-0041-20261023.md)|`0xa000589c` 的16/20B对齐路径值复制、不持有源地址；`0xa0024906` 的对齐零填充包含64B已验|继承copy16/zero64限定路径。record、ctx、scratch槽和entry须有效且满足所需对齐/容量；不推所有地址的算法行为|
|G21所引J05/G11/G12父级complete、最终SIM/ZIP复用结论|旧extent `ev_5ecc1c04…`、directcall `ev_054cff13…`用于选址；SIM服务替代与ROM合同分层|不重跑旧负搜索/最终ZIP/回放，不将SIM通过或旧地址当新增功能|

原件引用 [CATALOG](../../../roms/CATALOG.md)：AP01 `1.0.2_0041`，主仓 `roms/0041/ap01-1.0.2_0041.bin`，6,769,704 B，既有SHA256 `972db4c136c7ed9e24a83c07c1a7fd62040ca018b08ca285216d26b1fee3c6b9`；地址映射 `file_offset=VA−0x9ffff000`。仅核长度、引用已有摘要，不重算hash，不套0031/unsigned/SIM ELF。

## 本轮复核或纠正

独立 [review.py](../../analysis/pogo-poll-submit-review-g22-0041-20261024/review.py) 只读主仓原件，以Capstone 5.0.7离线解码RV32/RV32C；另外自行按bit位核B/JAL/C.B、word访存及厂商byte-store字段。必要锚点见 [review-result.json](../../analysis/pogo-poll-submit-review-g22-0041-20261024/review-result.json)。没有执行原指令或任何模型/输入，没有新REA Evidence ID或整函数/资源/源码导出。

令C=submit_ctx、S=原scratch基址、V=调用者record、i=旧tail与原mask按位AND的结果。以下均为原字和必要寄存器流支持的分析记号，不认证正式OS结构/源码类型：

|G19/3待审主张|独立原件核验|判定/前提|
|---|---|---|
|实际六参绑定及非fallback入口|`0xa009e104/108/10c/10e`保存fd、V、backend_fd、op；`0xa009e106/10a/110`读C+0x3c并BNE −1→`0xa009e168`|接受实际op2差集。fallback正文未重读|
|tail指针、mask与slot索引|`0xa009e168`取word(C+4)为tailp，`0xa009e16a`读mask到s9，`0xa009e170`再读word(tailp)；`0xa009e17a`按位AND|接受+4为指针而非tail值；mask初始化/容量意义未知，不能默认mask=2^n−1|
|先写tail，再copy16|`0xa009e172` V→a1，`0xa009e174`原S→s8；`0xa009e176`先算old_tail+1，`0xa009e17e/182`构造S+(i<<4)，`0xa009e184`SW增量tail，`0xa009e186/188/18a`才以(dst,V,16)调copy|接受指令存储顺序，不补fence/锁或“copy完成才发布tail”。数值/地址运算沿RV32低word|
|copy后才取entries和构造64B条目|`0xa009e18e`在copy返回后读word(C+0x28)；`0xa009e192/19a`以i<<6形成E；`0xa009e196/19e/1a0/1a2`调用zero(E,0,64)|接受scratch槽stride16与entry stride64为两个存储区域的地址形成合同；实际分配/容量/对齐不由用途自动证明|
|字段宽度与原序|`0xa009e1a6/1aa`写fd>>31到E+0x0c；随后E+0x10=copy_dst、+0x14=0、+4=backend_fd、+0x18=op、+8=fd；`0xa009e1c6`byte写E+0；`0xa009e1ca/1ce`写((i<<2) OR op)到E+0x20；最后 `0xa009e1d2`写fd到E+0x24|接受各word/byte宽度、先后与两个fd保存位置；本输入op2不让通用OR换成加法，不命名正式SQE/opcode|
|原mask配合重读head/tail|`0xa009e1d6/1da`重读C+0/C+4指针，`0xa009e1de/1e0`分别再取值，XOR后 `0xa009e1e4`与原s9 mask相AND；没有在这里重读mask|接受重读原序，不凭形状认证full/empty、原子性或并发发布协议|
|条件下层调用的三个实参|`0xa009e1e8`C.BNEZ结果非零跳尾；零时 `0xa009e1ea/1ec/1ee`恢复 `(backend_fd,C,original_S)`，`0xa009e1f0`真实JAL→`0xa009dfcc`|接受零条件才调用；第三参不是copy_dst、V或E。G19/4下层body未展开|
|返回消费|`0xa009e1f4..210`仅恢复保存寄存器、栈及ret，没有比较/替换a0；非零条件直接到同尾|接受不能统一命名成功/失败。有调用时a0沿下层返回，无调用时可能沿前序服务遗留，本体未提供成功回执|

厂商byte-store `0xa009e1c6` 原字为 `0x01add78b`，独立字段 `(opcode,funct3,top5,rd,rs1,rs2,shift)=(0x0b,5,0,15,27,26,0)`。s11是entries基址，s10是i<<6；按现存只读 `ap01thead2.sinc` 的 `th.srb` 规则，写a5低byte到entries+(i<<6)，即E+0。a5在此前置0x1d。规则地址计算、byte宽度与selectors均重新核过；该本地规则不等同独立厂商规范、精确ISA/SDK来源认证，未执行或修改模型。

无原字或核心语义纠正。G21“值复制而非直接保存调用者record指针”的机器表达成立：V只作为copy源参数，E中写的是计算得到的scratch槽地址。须保持其条件强度：不同实参形成地址**不证明实际地址不别名**；若要得出调用者栈失效后副本仍有效，另须副本确在独立且持续有效的存储中。该独立性和scratch/entry寿命、何时可复用仍未由本行建立。本轮不以这项限定注记扩大到初始化或allocator取证。

## 真正新增

**复核新增功能0、ISA规则0、来源排除0、完整函数/资源/源码导出0。** 本轮交付仅为非作者对G19/3本次实际op2差集的限定技术接受及必要原件索引。G11/1 fallback、G19/1–2输入与取消、G03/G04的对齐copy/zero均为继承，不重计旧成果。

复制16B后条目引用scratch槽，而不是直接将V参数发布为条目字段；对于G19/2已准备的全零stack16，在有效、对齐且有足够存储的正常路径上形成全零16B值副本。该条件合同不证明OS已接受该条目，也不证明所有tail都已被消费、scratch槽或64B条目现在可以复用。

## 精确未闭与实际验证

仍未知：C、S、entries的初始化、有效范围/容量/对齐保证及它们与源记录的实际别名关系；跨线程发布/同步；副本和条目的持有期限与复用时机；正式字段/opcode来源；`0xa009dfcc` 如何消费head/tail和副本、向下提交及返回成功。OS close、callback drain、恰好一次、timer停止与context释放不在本行接受范围，未将局部验收扩大成原ROM完整恢复。

实际运行本路独立脚本：**67项稀疏检查PASS，其中1条厂商byte-store，另核既有规则与CATALOG原件长度**。JSON、报告相对链接及diff检查通过。没有运行/导入G21脚本、目标ROM、SIM、QEMU、构建、历史回放、模型、设备或外部服务，没有漏洞/异常输入/缺陷验证，没有生产/ROM/配置/模型或共享认领表修改。

有种子的后继仅引用已登记 **G19/4**：`0xa009e1f0→0xa009dfcc(backend_fd,C,original_S)`，旧extent `ev_3389f9eb…`、directcall `ev_6e8ac40e…`已由G21留存。本次只核callsite，body未派未读；将来须由管理窗口查重并登记负责人/本体差集后才能展开，不能借G22名字扩大到该服务或native backend。本路精确提交后停止。
