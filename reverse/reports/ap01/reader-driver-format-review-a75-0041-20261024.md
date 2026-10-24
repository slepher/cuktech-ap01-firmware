# A75：count256格式适配层的非作者复核

**限定接受A74的适配差集，语义纠正0、新增业务0。** 同count256入口正常路径构造六word栈S=`{0,a002b536,a002b4d8,a002af2e,buf,255}`，先写buf首byte为0，再经旧32B wrapper向a01a37d2交`(S,0,0,format,va)`；两层正常返回a0不变、没有本体后写。这个结论不认证最终输出、计数含义或截断/NUL协议。

2026-10-24；J08/11，非作者`/root/a56`；独占`re0041-a75` / `codex/re-0041-a75`，固定基线`bd457a6`。作者A74已停止，主仓报告/合同已整合。采用REA留存优先流程，仅独立最小原字段与旧d770来源检查；不运行A74 check.py或历史脚本，不执行目标/指令/模型、host格式输入枚举、固件、SIM/QEMU、构建、回放、IO/设备或外部服务。不切换共享REA、不改生产/主树/共享表，无下级agent、提交推送。

## 继承

|出处|复用及本题边界|
|---|---|
|[A66/A67](reader-driver-open-close-review-a67-0041-20261024.md)|mode2 callback的buf/256/literal`/%s`及suffix首vararg经a008ab4c交a0053252；忽略format返回后继续fd-open。该caller/literal/42B wrapper不重读|
|[C13/C14](text-update-entry-review-c14-0041-20261023.md)、[C23/C24](text-entry-source-review-c24-0041-20261024.md)|较晚两遍调用及候选来源语境已有；不以名字补标准格式器行为，不重开caller或候选库版本|
|[A74](reader-driver-format-gap-a74-0041-20261024.md)及同名contract/evidence|本次只独立核六word、三个target/buf/255、先SB0、参数传递、旧wrapper及两层返回。不导入作者检查源码|
|旧upper-complete d770 dossier|`evidence/rea-0041-20261017/evidence/upper-complete.evidence.json#/records/67`，EID `ev_2fc7174be7213a9616dc6d46d18c0831acd1c06324cba526633b36c29ab2f22e`；直接取normalized_result.assembly十四行，而非upper-coverage边界metadata|
|J08/12 A76及J08/13 A78|engine及三个target本体为另题。本复核不读它们、不把A78作者候选提前算进A74适配验收；count0的discard targets同样不展开|

旧d770 profile为`4825fb58a33a3e7d618557975b153b8318cf7e833d190ad16bcbf8bd441ae621`，language `RISCV:LE:32:ap01thead2`。独立检查来源subject的0041摘要一致；旧assembly不是新ROM重导或整个引擎已验。

主仓原件`roms/0041/ap01-1.0.2_0041.bin`长度6,769,704B独立检查，继承SHA256 `972db4c136c7ed9e24a83c07c1a7fd62040ca018b08ca285216d26b1fee3c6b9`，不重算摘要；file_offset=VA−0x9ffff000。不套0031或SIM。

## 复核与纠正

[review.py](../../analysis/reader-driver-format-review-a75-0041-20261024/review.py)仅读原件`[a0053252,a00532ca)`120B，37个普通位置；Capstone5.0.7 RV32+RVC完整覆盖，独立U/I/S/JAL及压缩branch/jump拆字段。另按唯一EID定位旧wrapper十四行/32B，不新读d770原件或engine。**39项静态检查PASS**，没有UNKNOWN/厂商模型依赖或指令执行。生成`review-evidence.json`保留VA/偏移/原字/宽度及旧assembly来源，忽略留本地原analysis路径。

|锚点|独立接受的事实|
|---|---|
|a0053252/3258|栈帧−0x30，s0=入口sp；S=s0−0x28，六word槽在本层栈存储。不是heap分配|
|325a/3260/3266|a4保存count，a1=原fmt；BEQZ a4→32a8为零比较。给定count256走非零臂；不加signed长度门|
|325c/3262、3268/326c、3274/3278|独立U/I拼成a002af2e、a002b536、a002b4d8，地址不是按名字推断|
|3270/327e/3282/3286/328a/328e|独立S-format均word store、base=s0：相对S偏移依序+4/+8/+c/+0/+10/+14；分别写三target、0、原buf、原count−1。327c为32位count减1，256得到255|
|3292|`23000500`拆SB zero,0(a0)，原a0仍buf；先于本层lower call。不是word清buf，也不是调用后NUL证明|
|3296/329a/329c|a0=S，a2=原a3(va)，a1仍fmt；独立JAL→a002d770。只证这组寄存器word，不用候选C函数名补参数|
|32a0..32a6|恢复ra/s0/sp后RET，不改a0、无S/buf后写。下层可能有副作用，不能由本地无store推最终buf不变|
|32a8..32c8|count0只换S+4=a002b554、S+8=a002b578、仍S+c=a002af2e并清S+0；没有赋S+10/+14或直接写buf。压缩jump解到3296共用call；不读两个discard target、不认证engine是否读未赋槽|
|旧d778/d77a/d77c/d77e|十四行旧assembly明确先a3=a1(fmt)、a4=a2(va)，再a1=0、a2=0；a0保持S。原序不可写成清零后才捕获参数|
|旧d780/d784|AUIPC ra,0x176与JALR +0x52独立常量解算→a01a37d2，因此显式前五word为`(S,0,0,fmt,va)`，不给a5等残值登记形式参数|
|旧d788..d78e|只恢复ra/s0/sp/RET，无a0替换或输出写；engine返回word透过两层。数值含义、signedness、长度与错误码不由透传推定|

**未发现A74语义错误。** 独立接受只针对上述参数/初始化/返回原序，不增加S+4/+8/+c的角色命名。S、caller的va包和buf是不同层栈对象，这只解释来源；有效空间/生命周期与lower正常ABI需成立，不能因为来自不同表达式就证明不别名或下层不持有。

## 真正新增

复核新增业务0、原字语义0、来源/ISA认证0；只为A74提供非作者独立接受与[最小合同](../../analysis/reader-driver-format-review-a75-0041-20261024/contract.json)。本次120B重读及旧十四行再核不重记新功能，不恢复完整formatter。

适配层没有allocation/free；能证把S/format/va交下层、先初始SB0、正常回返不折叠a0。不能证engine/target不会持有指针、不会写其他字段或实际输出。A78本体结论并非本次复核输入，不重复读其字节/规则。

## 精确未闭与后继

仍未闭最终buf字节/NUL、截断/总计数、va消费、返回word含义、深层持有/别名效果及完整库来源。count256适配已验不等于整个格式调用成功；count0另一臂只有局部参数初始化边界，没有discard行为或引擎完整覆盖。

engine实际使用点已有A76另路，stream body已有A78交付，本复核不重复派题。后续若组合实际输出，须取得这些差集的独立接受和所选输入域/存储前提，再检查同S/va/buf的连线；缺它们时如实保留端到端输出断边，不新增helper或整引擎恢复。

实际检查39项PASS、JSON解析、主仓后备链接解析、独占status、证据忽略保留与`git diff --check`通过；无旧脚本/模型/target运行。只写本报告与同名analysis，未提交推送；交付后停止供主窗整合/补位。
