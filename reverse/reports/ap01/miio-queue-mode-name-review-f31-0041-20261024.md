# F31：name斜杠cursor回环的非作者复核

2026-10-24；F11/11；非作者`/root/f12`，独占`re0041-f31` / `codex/re-0041-f31`，基线`bd457a6`。**限定接受[F30](miio-queue-mode-name-branch-f30-0041-20261024.md)：e43c的C.ADDI a3,1及e43e的C.J→e38e形成4B正常回边，旧LBU/BEQ可重复跳过当前斜杠byte，非斜杠落e396。该有限局部环不改s3/s6，无新callee/返回。** 语义纠正0、新增业务0；不接受将其扩大为所有name创建成功或完整返回时mode保持。

权限为主仓最新[认领表](rolling-management-0041-20261023.md) F11/11 F31进行行。沿已读[流程](reverse-design.md)、[保留规则](../../analysis/README.md)及REA技能复用旧证据。只读4B原件及六条必要旧端点，不运行F30 check.py/F27/F28或旧技术脚本，不执行目标/指令模型/输入、固件、SIM、构建、open/IO或外部服务，不切换共享REA；无下级agent、提交推送或主树/共享表修改。

## 继承结论

- [F27](miio-queue-mode-init-gap-f27-0041-20261024.md)/[F28](miio-queue-mode-init-review-f28-0041-20261024.md)已限定接受同Q参数→s3、请求7→s6、所选lookup非负/type5/clear正常块在e3fc完整SW7的写点合同，opaque调用正常保存约定与Q有效性仍为条件。Q+18 size4不是Q首word mode。
- F28原路径`reverse/analysis/miio-queue-mode-init-review-f28-0041-20261024/review-evidence.json`六条锚点：e344/e348、e38a/e38e/e392、e3fc。本轮读取这些留存raw并独立拆字段，不重读前缀ROM或运行旧脚本。
- lower530B extent EID `ev_1ae31bd9673fe052005725f2f591e68ab775f2c90180395a1d2879b61bedc772`仅定位；旧F15/F16对象桥profile `4825fb58a33a3e7d618557975b153b8318cf7e833d190ad16bcbf8bd441ae621`按原来源继承，不为新4B虚构REA ID/profile。

原件主仓`roms/0041/ap01-1.0.2_0041.bin`，实核长度6,769,704B，继承SHA256 `972db4c136c7ed9e24a83c07c1a7fd62040ca018b08ca285216d26b1fee3c6b9`，不重算；offset=VA−0x9ffff000，不套其他ROM/SIM。

## 本轮复核或纠正

[review.py](../../analysis/miio-queue-mode-name-review-f31-0041-20261024/review.py)只以标准库读取新4B并核旧六行，**10项静态字段检查PASS**，没有Capstone/厂商模型/目标执行。新字节为e43c `8506`、e43e `81bf`；分别独立核C.ADDI的quadrant/funct3/rd/signed立即数和C.J位移拼装。原字与实际VA/偏移、旧行及检查见本地忽略[evidence.json](../../analysis/miio-queue-mode-name-review-f31-0041-20261024/evidence.json)。

|独立复核项|接受内容与限制|
|---|---|
|新e43c|quadrant1/funct3=0/rd13/imm1，即a3=low32(a3+1)，没有定义s3或s6，也没有访存|
|新e43e|quadrant1/funct3=5，signed位移−0xb0，target=a010e38e；不落入e440、不是RET或call|
|旧e38a/e38e|留存I-format分别为a5=47与LBU a4,0(a3)，真实byte读取游标，不是word读或只看首次byte|
|旧e392|B-format opcode0x63/funct3=0/rs1=a4/rs2=a5，真实目标e43c，4B fallthrough=e396。回环内a5常量不变，a3每次递增后重读a4；没有隐藏s3/s6定义|
|旧e344/e348/e3fc|C.MV分别保存s3=a0、s6=a2；旧S-format为SW s6,0(s3)。若回环退出并满足已验后续正常条件，到此写点仍写7，不能由本地未改寄存器推callee保存/lookup/type条件自动成立|

新两条均16位，无厂商未知字；旧普通字段按其原raw复核。局部环本身没有返回，只能有条件接回旧正常公共块及其返回边界；有效游标读取和最终非匹配byte是退出前提，不做字符串输入/终止性试验。

F30如实披露首探80B、后76B未纳入语义。本轮仅独立读4B，不重查或跟进那76B里的callee；这些额外读取不属于本次接受覆盖。没有语义纠正，也不反写F27/F28的历史未知。

## 真正新增

**复核新增业务/语义纠正/ISA规则/来源认证均0。** 仅对F30新4B及必要旧端点提供限定非作者接受；不把10项检查或重复读取记为新queue功能。[contract.json](../../analysis/miio-queue-mode-name-review-f31-0041-20261024/contract.json)保留同Q/请求前提、退出/写点条件和读取边界。

## 未闭精确边

e440及后续创建/permission/失败臂、所有成功返回的mode保持、cleanup别名副作用、后续writer/替换与F23实际运行mode继续未知。局部不改s3/s6只保证到旧写点的条件连续性，不给所有name统一赋结果7，也不证明Q容量/生命周期。

唯一有种子后继仍为旧lookup负门e3d6→e440同Q/请求7下的创建正常汇合/返回，须主窗另查重登记；不沿首探多读76B或全FS/allocator/driver展开。实际JSON解析、链接主仓后备、空白/git diff --check、独占及忽略路径检查通过，无提交推送，交付停止。
