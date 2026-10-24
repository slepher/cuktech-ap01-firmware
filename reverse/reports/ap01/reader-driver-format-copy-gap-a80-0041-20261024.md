# A80：format stream调用copy的短长度及对齐缺口

2026-10-24；J08/14，`/root/f12`；独占`re0041-a80` / `codex/re-0041-a80`，基线`bd457a6`。本题从旧record76及主窗登记24B增量核实[a002b512调用](reader-driver-format-stream-review-a79-0041-20261024.md)的copy短域：**n1走普通LBU/SB单byte路径，不经过alignment门；正常有效分离的1B源/目的，无需word对齐或额外padding，返回原dst，无直接参数地址持有。n8..255仅定位对齐分支种子，不能借n4/n16/20既验域认证。** 新业务0，作者合同待非作者复核。

权限取自主仓最新[认领表](rolling-management-0041-20261023.md) J08/14与主窗派发。沿[流程](reverse-design.md)、[保留规则](../../analysis/README.md)及REA技能先复用留存；不运行旧脚本、目标、host输入枚举/指令模型、固件、SIM、构建、回放、IO/设备或外部服务，不切换共享REA、不改主树/共享表/生产ROM配置，无下级agent、提交推送。

## 继承结论

|已有来源|可信域与本题差集|
|---|---|
|[A78](reader-driver-format-stream-a78-0041-20261024.md)/[A79](reader-driver-format-stream-review-a79-0041-20261024.md)|stream先以unsigned min选择n，signed n>0才调用a000589c(oldbuf+oldcount,src,n)。给定cap255、有效count≤cap，则实际copy只在1..255。prefix-char分支请求n1；suffix后续dst可为buf+1，表达式不证明地址对齐、分离或容量|
|[F17](miio-queue-copy4-f17-0041-20261024.md)/[F18](miio-queue-copy4-review-f18-0041-20261024.md)|n4正常有效word对齐域已验：短分支、交错byte读写/最后普通LBU/SB、原dst返回、无直接参数持有。本轮不把其域扩成任意非对齐或所有length|
|[G03/G04](invalidation-submit-review-g04-0041-20261023.md)|仅正常分离word对齐n16/20路径；业务a008b43a“copy4”是四word16B，不是n4|
|[B25](cmd56-item-field-contract-b25-0041-20261024.md)/B26|n12 caller的copy接口与字段连接沿用既有角色，报告明确未核1080B算法的全部宽度/次序；不作为新n12 body验收|

原件继承0041、6,769,704B、SHA256 `972db4c136c7ed9e24a83c07c1a7fd62040ca018b08ca285216d26b1fee3c6b9`及VA−0x9ffff000。首阶段不读ROM；经主窗登记后只读取24B并核长度，不重算摘要；没有复制大导出/1080B body。

## 本轮复核或纠正

精确旧来源为主仓 `evidence/rea-0041-20261017/evidence/upper-complete.evidence.json#/records/76`，Evidence `ev_32725e49dc86c4d072d48e396f5c14986a521284bea8c8ff59cd533fc995a848`，profile `4825fb58a33a3e7d618557975b153b8318cf7e833d190ad16bcbf8bd441ae621`。旧Ghidra12.1.4/AP01局部模型assembly是定位与条件语义线索，不替代本轮独立raw/外部ISA证据；caller inventory另有partial局限，不做全caller否定。

[locate.py](../../analysis/reader-driver-format-copy-gap-a80-0041-20261024/locate.py)只读取该record并匹配EID/profile/入口，保留33条必要dispatcher/terminal/alignment入口旧行，不读取pseudocode或导出整函数。**19项旧定位/行一致性检查PASS，ROM0B**；[retained-evidence.json](../../analysis/reader-driver-format-copy-gap-a80-0041-20261024/retained-evidence.json)本地原路径忽略保留。没有运行作者/历史检查器或执行任何输入。

主窗随后已在J08/14/顶部登记，仅准 `[0xa00058ae,0xa00058c6)` 24B dispatcher。独立[verify_n1.py](../../analysis/reader-driver-format-copy-gap-a80-0041-20261024/verify_n1.py)在这24B八位置核 **16项PASS**：Capstone5.0.7 RV32/RVC八指令边界/解码，另拆四个B型opcode/funct3/寄存器/有符号目标、三个C.LI rd/imm与C.MV rd/rs2。`58ae`确为unsigned BLTU a4,a2→58c8，`58b4`为BEQ n,2→5920，`58bc`为BEQ n,3→58fe，`58c2`为BEQ n,1→590e；`58ba`确把原a0移至a5。新字段没有厂商未知字/规则依赖；两端F18原字/语义直接继承而非重读或运行F18脚本。[n1-evidence.json](../../analysis/reader-driver-format-copy-gap-a80-0041-20261024/n1-evidence.json)保留精确VA/偏移/原字和检查，无新REA生产ID/profile。

## 真正新增

新增业务/ISA/来源认证为0，旧合同语义纠正0。新补原字段24B仅使n1有限路线形成合同；n8..255仍只是旧定位，不把旧代码存在记作新功能恢复：

|有限域|旧assembly静态路径/本题缺口|
|---|---|
|n1|589c a5=7，589e保存dst至a6；58a4的7<n假，58aa的n4门假，58ae的4<n假，58b4的n2门假，58ba令a5=原dst，58bc的n3门假，58c0给1，58c2的n1门真→590e LBU a4,0(a1)→5912 SB a4,0(a5)→5916 RET。普通byte路径没有alignment分流，无额外读padding、无callee/栈/直接地址持有且a0原dst不改|
|n2..7|短长度dispatcher接5920/5922、58fe、591c/591e、58ee、5918/591a、58dc不同byte序列；只有既验n4子域可直接引用。其他长度不因共享末尾自动宣布已验|
|n8..255|58a4→592c。592c以a6&3测目的对齐，5924/5928旧byte postinc前缀后回592c；5930重算剩余。5936后以当前src&3分四路：0→599c、1→5950、2→5af2、3→5be2。本题只留必要入口，不展开循环/word拼接/尾部|
|源余数1足迹种子|旧5950先将a1向下按4对齐，5952再作word load postinc4。不能仅由原src起n字节可读就推该向下对齐后的读足迹有效；实际额外前后padding及字节拼接语义须按原访问另验，不作漏洞/异常输入试验|

给定源1B可读、目的1B可写及适当分离/无干扰、正常byte访问/返回约定，n1路线严格按源原地址读1B，再按目的原地址写该值；没有先向下对齐、word读或后续借源继续工作。参数地址未写入持久对象，复制的byte本身即使是指针编码的一部分也不转移任何被指对象所有权。这里不要求word对齐，因为本条路线每次访问就是普通byte，且没有alignment测试；不将F18 n4域暗中扩大。caller b536栈byte可在该同步有限helper返回后结束其copy借用，但S/buf/engine实际持有与输出另按A78/A79/A76前提，不从n1推完整格式库生命周期。

最小[contract.json](../../analysis/reader-driver-format-copy-gap-a80-0041-20261024/contract.json)将n1已核域与其他长度未闭分支分开。上述是静态条件代入与符号路径，不是host替代函数、目标执行、输入枚举或异常试验。

## 未闭精确边

最小24B增量已登记并完成。F18已验 `[589c,58ae)` 与末 `[590e,5918)` 端点，直接继承而非重读；本题没有扩大n4既验域、重验厂商byte postincrement或其他端点。

有种子后继为剩余n2..7短分支，或明确受限n8..255下5924..594c的目的前缀/源余数分流及所选单支访问足迹；必须先主窗查重登记。不能将任意n≤255、dst=buf+1、有效容量或参数表达式不同当作alignment/分离/额外可读padding证明。源/目的/S有效分离、容量和正常服务前提继续保留。engine与实际输出另题，不通过copy接口反推完整format输出。

实际检查为19项旧留存检查+16项新原字段检查，33条旧必要行、24B新字段；JSON解析/相对链接主仓后备/空白/git diff --check、独占及忽略原路径保留通过。只新增本报告与同名analysis，未提交推送，交付停止待非作者复核。
