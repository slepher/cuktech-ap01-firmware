# G24：G19/4 状态门与完成记录消费的非作者限定复核

2026-10-24；研究基线 `32f9c9e`，沿现有 `re0041-a56` / `codex/re-0041-a56-resume` 工作区。认领 **G19/4**；复核者 `/root/a56`，作者G23 `/root/g23` 已交付停止。主仓唯一[认领表](rolling-management-0041-20261023.md#链条认领表)本轮复核登记明确准许：只核 `0xa009dfcc` 本轮counter重读/诊断门、局部16B副本、完成记录消费、tag/result门及op3调用端；不接新callee或op3本体。

**限定接受G23本轮字段、顺序与条件合同，语义纠正0、新增业务功能0。** 特别接受作者保留的可达性限制：诊断返回及寄存器合同尚未知，从入口到后半完成环的普通可达性仍未闭；不能把线性字节排列或局部原字段验证当作实际提交/完成。研究管理者可将本轮差集记为独立限定接受，原未闭边不得改成全ROM已闭。

已阅读主仓 [reverse-design](reverse-design.md) 和最新登记，采用 [REA skill](C:/Users/cogic/.agents/skills/reverse-engineer-anything/SKILL.md) 的证据/静态边界规则。未打开共享REA、运行作者脚本、目标/指令/模型、固件、SIM/QEMU、构建、回放、设备或外部服务；未做缺陷/异常输入验证；未改生产、ROM、配置、分析器或共享表，无下级agent，无提交/推送。原A56成果保持。

## 继承结论

|出处|继承范围|本轮不外推的边界|
|---|---|---|
|G19/G20的G19/1–2已验差集|W=P+0x34取消、fd聚合、传给上层六参服务的实际输入|不重做stop/close/ready或引用计数释放|
|[G21](pogo-poll-submit-g21-0041-20261024.md)/[G22](pogo-poll-submit-review-g22-0041-20261024.md)的G19/3|实际op2先增tail、copy16/zero64、构造条目；masked-XOR条件成立才调用 `0xa009dfcc(backend_fd,C,S)`，返回未在上层判断|本次入口对象来源从此继承，op2合同不套到op3；容量/对齐/别名及发布成功限制保留|
|G03/G04和G11/G12的既有copy/fallback合同，经G21/G22引用|`0xa000589c` 正常对齐16B值复制为已有服务前提|不重验库body、不补所有地址域或全部ABI，不重做fallback|
|[G23作者报告](pogo-poll-ring-consume-g23-0041-20261024.md)及其同名analysis/evidence.json|新增本体说明、100个作者锚点和既有模型实例；旧extent/directcall metadata不等同本体恢复|作者检查不是独立证明；本轮另写字段验证器，不运行/导入作者代码，不新导整函数或反编译|

旧whole-ROM `/functions/2356` 的范围Evidence `ev_3389f9eb111676b5aa1d29ed405d754612ba2d22d0899a45d361148734f89779` 和directcall Evidence `ev_6e8ac40e4549bbf220c9a7869277a91b8ca2984a1a2baa6431d765f3bab83edd` 只继承作定位；本轮没有产生REA调用、profile或新Evidence ID。本体字段复核证据为本报告配套原字段JSON，不把旧EID重标成新分析。

## 本轮复核或纠正

独立以原件稀疏seek取得关键指令，直接拆RV32/RVC位域，不依赖Capstone显示文本。分支/直接跳转自行重组立即数；普通及压缩访存解出寄存器、位宽和偏移；完整的20B返回段逐条核是否写a0。检查器与结果见 [review.py](../../analysis/pogo-poll-ring-consume-review-g24-0041-20261024/review.py)、[review-evidence.json](../../analysis/pogo-poll-ring-consume-review-g24-0041-20261024/review-evidence.json)。

|复核差集/原字锚点|独立核对结果与裁定|
|---|---|
|`0xa009dfe0` 读C+0x3c、`0xa009dfe4` BNE→`0xa009dffa`；`0xa009dff6` JAL→`0xa0019672`|非−1才无诊断直达首次counter读取。相等臂会调用未展开服务；不能假设返回后a0/a1/a2还是入口值。接受作者这一限制|
|`0xa009dffa..0xa009e008` 的C+0/C+4指针与word读、SUB及BEQ→`0xa009e042`|首次比较完整word，delta为tail−head的RV32结果。相等臂设line0x4f5并跳共同诊断 `0xa009dfee`，不是空环普通返回；不把G21上层mask条件代入|
|`0xa009e016`、`0xa009e01e` JAL→`0xa00267c0`，中间SW s6=0x26到返回地址，后次返回地址LW再与4比较|读写及重试门与作者一致；不认证两次返回同地址、不认证callee无副作用，也不凭形状宣布其精确errno类型或系统行为|
|`0xa009e030` JAL→`0xa0134716` 后，`0xa009e036` delta==−1门；line0x500诊断|仅在delta==−1臂才无后续诊断到第二次counter读取。没有对两服务和日志的副作用/寄存器作新假设，也未试图解释为何满足该条件|
|`0xa009e04a/04c/04e/050` 再取C+0/C+4指针和word；`0xa009e052` BEQ→`0xa009e05e`|接受必须保留重读顺序；第二次不等则line0x502诊断。不能用第一次counter的值替代，也不能由“第一次delta−1”静态推得重读相等|
|`0xa009e05e/060/062/066`：a2=16、a1=s2=S、a0=s0−0x30、JAL→copy服务|s0=sp+0x30由帧锚点核实；目的为本函数局部16B。复制在完成环循环前一次，源是原S基址；不是按每项index从S复制。对齐/对象寿命前提沿旧合同，不由局部指针来源认证|
|`0xa009e070..078`：C+0x14/+0x18两指针和word；BNE→`0xa009e090`|这是另一组counter，不能与入口C+0/C+4合一。相等进入已核返回段，不等才消费记录|
|`0xa009e090` ADDI old+1、`0xa009e094` C.SW、`0xa009e096/098` 后读mask/base|consumer先增加并写回，然后才取C+0x1c mask和C+0x24 records，按old低word与mask及stride16形成Q。接受原序，不能改成先读取record后增consumer|
|`0xa009e0a0` Q+8 word；`0xa009e0a2`结果0跳头；非零才Q+0/+4 word|接受result0直接继续。无局部清Q或归还S/环存储动作；计数增长本身不能证明底层已完成或存储可复用|
|`0xa009e0a8` low&3；`0xa009e0ac` 原字`f70726de`；`0xa009e0b0` AND0xff|厂商字拆 `(opcode,rd,f3,rs1,shift,top7)=(0x77,15,0,12,2,0x6f)`，匹配既有 `wexti` pair规则；逻辑右移a2/a3组成的64bit，再取低32bit、低8bit。数学上index=`(low>>2)&0xff`，仍保留原pair操作和模型来源限制|
|`0xa009e0b4` tag2→循环头；`0xa009e0b8` tag1→result门；`0xa009e0c4` result==s6(−17)→`0xa009e0d0`|只有tag1/result−17臂无诊断地进入op3调用端。其他tag或其他非零result分别经line0x51c/0x51f诊断；不越诊断补普通流程|
|`0xa009e0d0..e0e2` ABI、C.JAL→`0xa009e0e6`，`0xa009e0e4` C.J→环头|独立核得 `(a0,a1,a2,a3,a4,a5)=(s3,s1,s2,3,Q+4的word,local16+(index<<4))`，即 `(backend_fd,C,S,3,high,...)`。只接受callsite，明确不是已验op2。返回不被比较，立即重读完成counter|
|`0xa009e07c..0xa009e08e` 全部epilogue|8个LWSP只恢复ra/s0/s1/s2/s3/s4/s5/s6，再恢复sp、JR ra；没有a0写入。无op3时沿copy返回值，有op3时沿最近op3返回值，不能认证统一0或成功码|

**语义纠正0。** 作者将可写错误槽/日志作为候选解释、将稳定无副作用前提下的“占位形状”作为推断并明确不作缺陷结论，这一证据分层可保留；复核只接受原调用端和读写/分支事实，不把该解释升级为服务内部语义或实现意图。

`wexti`语义依只读 `evidence/rea-0041-20261017/ghidra/Ghidra/Processors/RISCV/data/languages/ap01thead2.sinc` 的现有局部规则，完整必要规则保存在本题JSON。检查字段及规则文本不等同新增厂商规范认证；未修改模型、未将未知编码替换为NOP、未执行p-code/模拟指令。诊断callee是否返回、返回后caller-saved寄存器为何值均未知，故不可绕过边界把后半段写成入口保证行为。

## 真正新增

新增业务恢复 **0**，新增callee本体 **0**，新增来源认证/整库排除 **0**。本轮新增的是非作者独立核对证据及对G19/4的限定接受，不把重读相同原字节计为新功能。复制、循环、状态门和六参ABI均保持作者原合同；无需为解释可达性改动ROM、模型或错误路径。

## 未闭精确边与实际检查

仍未知：入口条件调用到完成环的正常可达性；`0xa0019672`诊断返回与寄存器合同；`0xa00267c0`和`0xa0134716`副作用；counter初始化/发布/一致性、环容量与mask、local16索引有效范围、S/entry的别名/对齐/寿命；op3对局部副本的消费/持有、实际native/OS提交及成功、最终存储释放。复核没有为这些边补认定，也没有做输入实验或缺陷验证。

沿作者唯一有种子后继保留：`0xa009e0e2→0xa009e0e6(backend_fd,C,S,3,high,local16+(index<<4))` 的 **op3消费/持有合同**。必须先由管理窗口按G19/4关联新问题查重登记后再展开，不能套G21的op2或借此接全backend/native；本轮仅记录callsite，不取callee body。

实际运行本题独立字段检查器 **90项PASS，89条必要稀疏指令、234B**；包含关键分支和压缩跳转独立目标、字节/word宽度、消费顺序、帧/epilogue和唯一厂商实例。原件身份沿[CATALOG](../../../roms/CATALOG.md)：0041 `ap01-1.0.2_0041.bin`，6,769,704B，既有SHA256 `972db4c136c7ed9e24a83c07c1a7fd62040ca018b08ca285216d26b1fee3c6b9`，VA映射 `VA−0x9ffff000`；仅核长度、引用旧摘要，不重算哈希。不导出整282B函数/伪代码，不运行作者/旧验证器。

JSON解析、报告引用与 `git diff --check` 已检查；作者报告链接在本树尚未整合的G23报告以对应作者工作树同名文件校验，主窗口整合时应再核相对链接。本树只有A56与G24独占未提交产物，原A56文件未修改。交付后停止取证，G19/4仅可标本轮差集独立限定接受，未闭边继续保留。
