# A78：count256候选stream的三个实际callback合同

**在有效S域，0xa002b4d8把本次请求按剩余容量夹取；正数时先交copy接口，再重读S.count/S.buf，写更新后的word计数及buf末尾的NUL byte，返回本次选中的n。0xa002b536只把a1低byte放本栈并以n=1调用它；0xa002af2e不读写S或buffer，只返回0。** 名称不决定签名；这些是本体实际使用的寄存器/字段，不认证engine调用端的完整ABI。

2026-10-24；J08/13，任务A78，`/root/a56`；独占`re0041-a78` / `codex/re-0041-a78`，基线`bd457a6`。沿REA技能与主仓流程先旧留存/合同，再只取三精确入口138B，不展开engine/适配层、copy、诊断或IO。无目标/固件/指令/模型执行，无host字符串输入枚举、旧脚本运行、SIM/QEMU、构建、回放、设备/外部服务；不切换共享REA、不改生产/主树/共享表，无下级agent、提交推送。

## 继承与旧证据范围

|已有出处|行为/局限与本题处理|
|---|---|
|J08/11 A74派发种子|count256候选S初始化：word0=0、+4=a002b536、+8=a002b4d8、+c=a002af2e、+10=buf、+14=255，先SB0到buf再调用engine。**A74尚待非作者复核**；本题未重验该初始化，不能提前认证实际输出。主仓本题首次查找时尚无A74报告文件，明确使用管理者给定候选|
|J08/12 A76另路|engine实际ABI/调用次数与顺序由另题核验，本题不读该body，不把S+4/+8/+c先命名putc/puts/flush或给未使用寄存器补参数|
|主仓reports/analysis合同、rehost JSON|以三个精确地址大小写无关查找rehost，并在报告/机器合同查找；仅管理登记命中，无已存body合同。此有限输入无命中不是历史全局不存在或整库未知|
|whole-ROM round1函数532/545/546|仅extent/直接边：af2e14B、b4d8 94B、b536 30B；dossier/历史合同为空。b4d8有Nuttx路径候选，仅作定位，不能认证未改源码或正式签名|
|[B25](cmd56-item-field-contract-b25-0041-20261024.md)、[G03](invalidation-submit-g03-0041-20261023.md)/[G04](invalidation-submit-review-g04-0041-20261023.md)、[F17](miio-queue-copy4-f17-0041-20261024.md)/[F18](miio-queue-copy4-review-f18-0041-20261024.md)|a000589c byte-copy调用角色已有；不同成果仅明确n12/16/20及有效对齐n4等有限合同。**不能将这些推广成本题任意所选0..255长度的body证明**；本题保持正常copy界面前提，不读1080B算法|
|[A50/A52](photo-reader-consumer-review-a52-0041-20261024.md)、[F11/F12](miio-request-ownership-review-f12-0041-20261024.md)|既有th.mvnez及th.srb字段/局部规则可复用；F12甚至有同字0b50f700。本题只匹配原字段及必要短规则，不改/执行模型或新增厂商ISA认证|

旧extent Evidence分别为：af2e `ev_53d78845714a38bc97fff365215574646084394777f9308875ed2f91abbfc467`；b4d8 `ev_436110630e392c919f879e7d9e9b5957673ce4b47f3533c1d17f1e74f7c5826c`；b536 `ev_e0e9de2b168e4be73d93997d4ae7c06d952f8e7be8d340fd7022d95868d46cd2`。它们只定位范围，不代替内部语义。无新REA生产ID/profile。

原件为主仓`roms/0041/ap01-1.0.2_0041.bin`，实际长度6,769,704B；继承SHA256 `972db4c136c7ed9e24a83c07c1a7fd62040ca018b08ca285216d26b1fee3c6b9`，不重算摘要。映射offset=VA−0x9ffff000，不混其他版本/SIM。

## 本轮复核与纠正

旧合同语义纠正0。Capstone5.0.7/RV32+RVC在b504/b524不能解码，检查器依原半word宽度将两处保留为4B厂商字，分别独立拆字段；随后在明确边界b508/b528继续，**没有将未知字当NOP或误从中间半word开始**。54位置中52普通位置、2厂商字，共138B。独立JAL/B-format和局部规则文本检查共44项PASS；没有执行指令或枚举输入。

[verify.py](../../analysis/reader-driver-format-stream-a78-0041-20261024/verify.py)保存本次来源/原字/偏移/宽度及检查。生成`evidence.json`本地忽略保留。新callee连接已先报管理窗：b512→a000589c、空S诊断b4f4→a0019672，只作为调用边，不展开正文。b536→b4d8属于已登记三入口内部，不新扩题。

## 真正新增：本体使用参数与可见写序

以下S/count/buf/cap/n均为字段分析名，word运算按RV32低32位；要求S非零有效、source可读、目的含终止byte可写、copy所需容量/适当不重叠及相关正常callee保存条件成立。候选有效域取0≤count≤cap=255；不恢复下溢/巨大数/异常输入行为。

|入口/地址|实际参数、数据域与返回|
|---|---|
|a002b536..b544|使用a0和a1：SB a1到s0−0x11，只保留**低8位**；置a2=1、a1=&本栈byte，a0保持原S。没有读取a1所指字符串，也没有strlen。此本体未提供完整形式参数数目的证据|
|a002b548..b552|调用a002b4d8，正常返回后只恢复frame/RET，保留helper的a0；不擅命void。栈byte只跨本次nested调用存活，callback自身没有持久发布该栈指针；copy更下层是否持有仍是界面前提|
|a002b4e4..b4f8|a0非零跳b4f8。零路径向诊断a0019672传路径地址/行44等，本题不读诊断/串、不假定其返回后有效。正常S域从b4f8继续|
|b4f8/b4fa/b4fc/b4fe|从入口S取word count=S+0、cap=S+0x14，保存S到s2，s1=low32(cap−count)。a1=src、a2=requested到此仍原值|
|b500/b504|SLTU判unsigned requested<remaining；原字**8b14e642**拆opcode0b/f3=1/f7=33、rd=s1、rs1=a2、rs2=a4，按既有th.mvnez条件替换。故n=unsigned_min(requested,remaining)，不是strlen或传入requested必全接收|
|b508|signed BGE zero,s1→b528，即n≤0直接去epilogue。不copy、不更新本体count，也不补写终止byte。候选正常容量域该门对应n=0|
|b50c/b50e/b510/b512|取当前S+0x10的buf，a0=buf+先前count，a1仍src，a2=n，调用既有a000589c界面。选中数据域是源[src,src+n)至目的[buf+old_count,buf+old_count+n)，实际copy效果依该n的正常界面合同，不由call本身代证|
|b516/b51a/b51e/b520|**copy回来先重读S+0的count，再重读S+0x10的buf**；new_count=low32(reread_count+n)，先SW new_count到S+0。不能沿用copy前count/buf快照，也不能由不同字段名证明不别名/无副作用|
|b524|原字**0b50f700**拆opcode0b/f3=5/rd=zero/base=a4/index=a5/shift0/top5=0；既有th.srb为无base回写的1B indexed store。因此在**重读buf+new_count**写NUL，严格晚于计数SW；不是word清零或写buf+cap固定位置|
|b528..b534|恢复ra/s0/s2，先a0=s1，再恢复s1/栈/返回。返回为选中的n word，不是requested、new_count、buf或完整格式化所需长度|
|a002af2e..af3a|只保存/恢复自身s0栈槽，a0=0、RET。没有输入寄存器解引用、S/buffer读写、callee或持久指针保存；不能凭S+c槽名说它刷新IO/追加NUL|

厂商语义只依主仓`evidence/rea-0041-20261017/ghidra/Ghidra/Processors/RISCV/data/languages/ap01thead2.sinc`中`:th.mvnez`行18、`:th.srb`行6442的短规则。与既有F12/A52的局部接受相符；未提升成外部硬件规格、完整ISA或库来源认证。

必要表达（分析伪码，非原源码/执行模型）：

```c
// b4d8: 使用输入a0=S,a1=src,a2=requested_word
old_count = word(S);
n = unsigned_min(requested_word, low32(word(S+0x14)-old_count));
if (signed32(n) > 0) {
    copy_interface(word(S+0x10)+old_count, src, n);
    after_count = word(S);              // 原序重读
    after_buf = word(S+0x10);
    new_count = low32(after_count+n);
    word(S) = new_count;
    byte(after_buf+new_count) = 0;
}
return n;
```

如果采用A74给定候选初始化、S/count/buf在服务中保持兼容、cap255且count从0正常累加，计数是本次实际接受存放字节数的累计，正写入后NUL在buf+count，buf需含第256个byte作为尾部空间。**这只是这些callback的条件效果**；n=0时不重写NUL，af2e也不补NUL。初始NUL依赖待验A74，而不是本题三body自动保证。不能仅由cap255承诺engine会调用这些入口、总所需输出长度、截断返回或path最终内容。

直接持有：b4d8以src调用copy，没有把src或S指针写入S字段/global；只更新计数、buffer数据与末尾byte。b536仅把一个byte放自己的栈供同步下层使用；af2e不接触输入。此“本体没有持久指针发布”不扩成copy/engine/整个格式库绝无更深借用；S/buf/source仍需在相应界面期间有效。无分配/归还或IO调用。

新增是三实际入口的参数使用、夹取/计数/NUL写序及返回边界；新业务/来源认证/ISA规则/整库排除均0，不认证完整路径输出。最小合同见[contract.json](../../analysis/reader-driver-format-stream-a78-0041-20261024/contract.json)。

## 精确未闭与后继

A74初始化尚待独立接受，engine真实S参数映射/选择哪槽、调用顺序/次数与处理返回由A76另路；不重复engine或count0 discard targets。a000589c任意所选n的具体读写/直接持有合同、S/count/buf在copy期间的有效容量/不别名/稳定性仍为前提；不由有限n4/12/16/20推广。本次没有新copy/helper正文授权，不自行展开。

实际format数据、返回/截断/NUL端到端协议、source/path字节、底层IO与精确库版本均未知。若之后需要加强数据效果，真正局部种子为**b512→a000589c(buf+count,src,n)，且正常0<n≤255的实际选中n域**，先查已有完整dossier与管理去重再只补必要copy合同；这不等于请求读取完整1080B算法。本轮停于界面，亦不重派已有A76/A74问题。

实际检查44项PASS、54位置/138B、JSON解析、报告引用主仓后备解析、独占status/忽略保留与`git diff --check`通过；无输入枚举/目标执行。只新增本报告与同名analysis源码/合同，本地生成证据原路径保留，未提交推送。交付后停止供主窗复核/补位。
