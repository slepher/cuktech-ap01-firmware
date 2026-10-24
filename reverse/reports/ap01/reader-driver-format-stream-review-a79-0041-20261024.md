# A79：format stream三入口的非作者复核

2026-10-24；J08/13；非作者 `/root/f12`；独占 `re0041-a79` / `codex/re-0041-a79`，基线 `bd457a6`。**限定接受[A78](reader-driver-format-stream-a78-0041-20261024.md)：三个实际入口的参数使用、选中n门、copy调用端、回后重读/计数先写再NUL及返回边界一致；语义纠正0，复核新增业务0。** 任意所选0..255长度的copy本体效果、engine ABI与实际格式字符串输出不因本次接受闭合。

授权来自主仓最新[认领表](rolling-management-0041-20261023.md) J08/13 A79进行行；沿已读[流程](reverse-design.md)、[保留规则](../../analysis/README.md)及REA技能。只读必要原字段和已有局部ISA规则文本；不运行A78 verify.py/旧脚本、模型、固件、SIM、构建、输入试验或IO，不读copy/诊断/engine body、不切换共享REA，无下级agent、提交推送或主树/共享表修改。

## 继承结论

|旧来源|沿用内容与边界|
|---|---|
|A74候选初始化/A76 engine独立题|仅给定count256候选S与三个target地址；不由槽名命名正式putc/puts/flush，不验engine实际寄存器映射/调用次数/顺序或初始NUL|
|A78报告及contract/evidence|作者差集为af2e14B、b4d8 94B、b53630B；本轮独立取同三有限入口，不执行其检查器或直接将作者PASS代替验收|
|[A52](photo-reader-consumer-review-a52-0041-20261024.md)、[F12](miio-request-ownership-review-f12-0041-20261024.md)|th.mvnez、th.srb已有局部规则/字段接受；本轮重新核两原字并读必要短规则文本，不执行或扩大厂商模型|
|B25、G03/G04、F17/F18有限copy合同|a000589c的byte-copy调用角色已有；n4/12/16/20的有限合同不能推广任意n或本次有效容量/分离、深层持有结论|

旧extent仅定位：af2e `ev_53d78845714a38bc97fff365215574646084394777f9308875ed2f91abbfc467`，b4d8 `ev_436110630e392c919f879e7d9e9b5957673ce4b47f3533c1d17f1e74f7c5826c`，b536 `ev_e0e9de2b168e4be73d93997d4ae7c06d952f8e7be8d340fd7022d95868d46cd2`。不把旧函数索引/源码路径候选当body合同或正式版本认证。

原件主仓 `roms/0041/ap01-1.0.2_0041.bin`，本轮核长度6,769,704B；继承SHA256 `972db4c136c7ed9e24a83c07c1a7fd62040ca018b08ca285216d26b1fee3c6b9`，不重算摘要；file_offset=VA−0x9ffff000。本次无新REA生产EID/profile，旧来源各自保留。

## 本轮复核或纠正

[review.py](../../analysis/reader-driver-format-stream-review-a79-0041-20261024/review.py)独立读取三范围合138B，Capstone5.0.7 RV32/RVC核52普通位置；b504/b524保留原4B厂商字，按半word宽度继续b508/b528，不将未知指令NOP化或从中间误解码。关键S/I/R/B/J/压缩零门另独立拆字段。**49项静态检查PASS**，不执行指令或构造字符串输入；[evidence.json](../../analysis/reader-driver-format-stream-review-a79-0041-20261024/evidence.json)保留必要字段、原字和有限范围摘要，本地原路径忽略保留。

|复核接点|独立接受的事实与条件|
|---|---|
|b536→b4d8|b53e为SB a1,-17(s0)，仅low8(a1)；b542令a2=1，b544给a1=&该栈byte，a0未改。b548 JAL独立目标b4d8。回后仅恢复frame/RET，保留nested a0；本体不读输入字符串/strlen，不发布持久栈byte指针，深层copy是否持有仍是前提|
|有效S入口|b4e4 C.BNEZ a0→b4f8；空S诊断b4f4→a0019672只核callsite，不读诊断也不假定回来即有效。正常S从b4f8取count、b4fa取cap、b4fc保存S至s2、b4fe算remaining=low32(cap−count)|
|unsigned min|b500 SLTU a4,a2,s1按unsigned requested<remaining；b504原字8b14e642字段opcode0b/f3=1/f7=33/rd9/rs1=12/rs2=14。按既有th.mvnez局部规则条件非零才令s1=requested，因此n=unsigned_min(requested,remaining)|
|signed正门|b508字段funct3=5/rs1=zero/rs2=s1，目标b528，即signed0>=n跳过。候选0≤count≤cap255域对应n=0不copy、不写count、不补NUL；不是无条件追加终止符|
|copy接口|b50c取旧buf，b50e置a2=n，b510加旧count，b512 JAL→a000589c，a1保持原src；只认证copy(oldbuf+oldcount,src,n)调用端，所选n的实际数据效果须依正常copy合同|
|回后原序|b516 LW a5,0(s2)重读count，再b51a LW a4,16(s2)重读buf；b51e加保存n，b520 SW新count至S。不能缓存旧count/buf代替这两个重读，也不由字段名不同推无别名|
|NUL与返回|b524原字0b50f700字段opcode0b/f3=5/rd0/base14/index15/shift0/top5=0；局部th.srb规则为byte0写重读buf+newcount且不回写base。晚于count SW。b52e将保存n给a0，随后才恢复s1/栈并RET，返回不是requested/newcount/格式总所需长度|
|af2e|完整14B七条普通指令只建立/恢复本地16B帧及s0、a0=0、RET。无S/buffer解引用、callee或输入指针持久保存；不能据槽名补flush/终止效果|

规则仅仅读主仓 `evidence/rea-0041-20261017/ghidra/Ghidra/Processors/RISCV/data/languages/ap01thead2.sinc` 的th.mvnez（行18）与th.srb（行6442）必要构造器。原字段是事实，条件替换和indexed byte-store解释依该既有局部规则；不提升为独立外部ISA权威或硬件实测。没有读取copy/engine新字节。

接受域为S有效非零、cap255且count≤cap、src可读、目的含终止byte容量可写、S/源/目的适当分离与兼容别名副作用、copy正常返回并保存s1/s2。只有相关字段保持兼容才可将newcount解释为原count+n的正常累计并给出buf第256byte容纳尾NUL；本体实际重读语义不能被这些前提覆盖掉。直接本体没有把src/S指针发布到global或S字段，不能外推copy/engine/整个格式库绝不留用它们。

## 真正新增

**复核新增业务/语义纠正/ISA规则/来源认证均0。** 三body获得限定接受，49项检查不是新formatter功能。最小[contract.json](../../analysis/reader-driver-format-stream-review-a79-0041-20261024/contract.json)显式保留copy未验域、n0无NUL更新及engine隔离；不把调用接口观察写成任意长度同步copy本体已证。

## 未闭精确边

任意实际选中n的copy数据效果/更深持有、有效容量与无有害别名、S字段在callee期间兼容仍为前提。真正后继种子为b512→a000589c(oldbuf+oldcount,src,n)，正常0<n≤255；先复用完整dossier并由主窗另登记，不能读整1080B算法。A74初始化与A76 engine实际ABI/循环/返回由原题维护，本轮不代验或补输出。

实际格式字节/路径、截断返回/最终NUL端到端保证、真实IO与精确库版本继续未知。n0和noop均不补NUL，初始buf0不能由本题三入口凭空补证。JSON/引用/空白/git diff --check、独占及忽略原路径检查通过；无提交推送，交付停止。
