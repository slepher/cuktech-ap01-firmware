# F14：F11/3 native queue 源/长度与消息发布顺序独立复核

2026-10-24；固定基线 `bd457a6`，分支 `codex/re-0041-f14`；挂原认领 **F11/3**，非作者复核 `/root/g23`，作者F13 `/root/f12`已交付停止。**限定接受F13：实际wait=−1路线转交原源指针与word(Q+0x18)长度，经Q→F→K及非零候选消息M传到`copy(M+0x0c,source,n)`；此调用返回之后才进行M链指针发布和计数增加。语义纠正0，新增业务0。** 不接受由调用事实直接推出任意n/4B已复制、栈可立即失效或实际consumer执行；F13最终报告已保留这些限制。

已读主仓 [F13报告](miio-native-queue-f13-0041-20261024.md)、[F13合同](../../analysis/miio-native-queue-f13-0041-20261024/contract.json)及 [唯一管理记录](rolling-management-0041-20261023.md#链条认领表) 的F14登记；沿本批已读 [reverse-design](reverse-design.md)、[analysis保留规则](../../analysis/README.md)和 [REA技能](C:/Users/cogic/.agents/skills/reverse-engineer-anything/SKILL.md)。没有运行/导入F13或旧检查器，没有将作者逐指令JSON当原件；直接从主仓0041读取必要稀疏字节独立解码/核位域。

未运行目标、指令、模型、固件、SIM/QEMU、构建、回放、设备、外部服务或异常输入；未改生产ROM配置模型、共享REA/管理表，没有下级agent、提交或推送。allocator/wait/notify/copy全算法仍opaque，F15正在研究的同Q.size创建身份桥未碰。本文静态表达不是原源码、目标执行或整ROM验收。

## 继承结论

|来源|可继承合同|本轮边界|
|---|---|---|
|[F11](miio-request-ownership-f11-0041-20261024.md)/[F12](miio-request-ownership-review-f12-0041-20261024.md)|type1 invocation I及payload独立对象；跨线程caller以`(word(loop+0x18),&局部I,−1)`调用`0xa005f464`|直接继承caller/I身份，不重验D/R/P/S所有权或事件循环；本题source是I指针局部槽的地址，不是I对象首地址|
|[F13](miio-native-queue-f13-0041-20261024.md)，F11/3|作者给出adapter/正常callee/copy接口与接链顺序，原Q→F→K和M只是本题对象记号|作为待审主张，与原件比对；不是另开同题研究，不重导完整queue或逐指令大文件|
|G03/G04，经G21/G22继承的copy合同|有效、分离、word对齐16/20B路径值复制，不保留源地址|本题n未知；该域不能推广到4B/任意长度。没有读取`0xa000589c`本体或添加算法认证|
|旧whole-ROM索引metadata及F13列出的原Evidence ID/profile|0xa005f464、0xa0197a8e、0xa01949f0的extent/directcall历史定位|metadata不是本体语义；不重做全索引/SDK认证，不重标旧profile为本轮新REA分析|

原件沿 [CATALOG](../../../roms/CATALOG.md)：AP01 `1.0.2_0041`，主仓`roms/0041/ap01-1.0.2_0041.bin`，6,769,704B，既有SHA256 `972db4c136c7ed9e24a83c07c1a7fd62040ca018b08ca285216d26b1fee3c6b9`，映射`file_offset=VA−0x9ffff000`。本轮只核长度、引用既有摘要，不重算hash，不套0031/SIM。F13三层extent/directcall的旧Evidence与两种profile分别沿原报告，不伪造新REA ID。

## 本轮复核或纠正

本题 [review.py](../../analysis/miio-native-queue-review-f14-0041-20261024/review.py) 仅读原件，用Capstone 5.0.7离线RV32/RVC；B/JAL/C.J、AUIPC/JALR及关键字节/halfword/word访存另外独立取位域。选定锚点与结果保存在 [review-result.json](../../analysis/miio-native-queue-review-f14-0041-20261024/review-result.json)，此生成物按规则留本地原路径并受Git忽略。没有执行原指令、p-code或模型。

记Q=caller传入queue；F=word(Q+0x0c)，K=word(F+0x18)，S=caller保存I指针的局部槽地址，n=word(Q+0x18)，M=opaque服务返回的非零候选消息。与F11中的descriptor Q/response S不是同一对象。

|待审主张|独立原字段/控制检查|判定|
|---|---|---|
|−1路线保持原S、读取同Q长度|`0xa005f474`置−1；`0xa005f47a`BNE非−1才去0xa005f498；本路线`0xa005f47e`仅LW a2,Q+0x18，a1不被解引用/替换；`0xa005f480/484`AUIPC/JALR独立求得目标0xa0197a8e|接受(Q,S,n)调用端；n数值未证，不由S=&I推4|
|Q→F→K对象桥|`0xa0197a8e`LW a5,Q+0x0c；`0xa0197aa2`LW s1,F+0x18；Q首word&2、S/K非空及`0xa0197ab0/ab4`U16(K+0x24)与n的unsigned比较|接受这些加载/门，不把它们认证为具体queue类型、容量/有效M或运行成功|
|原source与长度经候选消息服务后继续传入|`0xa0197ab8/aba`把n/S保存到s4/s3；实际选定非零M臂`0xa0197b12..b18`置(a0,a1,a2,a3)=(K,M,S,n)，`0xa0197b1a`JAL独立求目标0xa01949f0|接受ABI和保存/恢复的正常约定；候选M服务内部仍未知，不根据其名称给分配/所有权结论|
|目的为M+0xc，源为S、长度n|`0xa0194a00/a02`保存M/K；a04把原a2即S置a1；a06 SH n→M+0xa；a0a将n置a2；a0c SB0→M+9；a10以M+0xc作a0；a14/a18独立解到0xa000589c|接受精确接口与byte/halfword宽度；不把长度SH截断当作copy参数也被截断，copy a2沿完整传入n|
|copy调用先于消息M发布|call返回到`0xa0194a1c`才读K+0x1c；a20形成K+0x18 sentinel；a26/a2a独立分支到遍历/替代插入；`0xa0194a30/a34/a3a/a3e`或`0xa0194ac6/aca/ad0/ad4`写M的+0/+4及相邻节点/K链槽|接受两条所读插入路线在copy接口返回之后；链槽发布值是M而非S。copy内部是否已处理所有n字节须另有算法域证据|
|计数宽度/原序|`0xa0194ad8`独立C.J回0xa0194a42；a42 LH K+0x22、a46加1、a4a SH回同槽|接受原signed-halfword读取与halfword写回，不改成word计数或长度字段；不认证并发/原子发布|
|返回折叠|所读共同正常尾`0xa0194b48`明确a0=0；`0xa0197b1e`独立跳0xa0197afe恢复原mstatus，再返回；adapter0xa005f492算术右移a0,31|接受进入并正常返回该尾声的零返回，以及adapter把所有返回按符号折为0/−1。不是原状态码透传，也不等于业务成功|

计数之后的notify/wait门和服务没有纳入全闭包，不把读到的共同尾声推广为所有通知/唤醒路径的完整语义。上层`0xa0197abe`的CSRR C原指令保存mstatus并清mask8，`0xa0197afe`写回所保存值；仅接受所见指令/原序，不宣称因此已认证全部并发同步。

**核心语义纠正0。** F13已把copy调用事实与复制效果分开，最终“尚不能无条件断言同步复制4B I指针/caller栈可立即失效”的限定应保留。更不能凭没有直接把S挂链，就抹去opaque copy内部/存储有效性边界：可核的直接链写入发布M；copy若实际满足继承域，才有该域下的同步值复制推导。

## 真正新增

复核新增业务 **0**，新增callee本体 **0**，copy新算法域 **0**，ISA/来源排除 **0**。交付是非作者对F13当前差集的限定接受、独立原件索引与宽度/顺序复核，不把同一字节再读计作新恢复。

接受的持有边界为：adapter不直接解引用S或把它挂链；下层以S/n调用copy服务，返回之后才发布M并增加K计数。只有S及M目的区有效、足够、分离且n/地址形状落入既有copy域时，才能说源值在发布前已经复制。M来源、对齐/容量、存储独立性与持续寿命未知，本次也没有得到同Q实际n=4的证据。原caller栈能否在返回后失效仍未闭。

## 未闭精确边与实际检查

同Q的word(Q+0x18)创建/初始化身份桥归 **F11/4、F15**，本复核未取该writer或创建器窗口，没有并行重复。实际n确定后是否另需4B等copy域验证仍待管理登记；本轮未读copy全算法。allocator、M获取/复用/释放、wait/notify、锁/调度、完整错误/返回分支、实际consumer/I执行与云端业务成功仍未知。

实际运行本路独立检查器 **79个静态锚点PASS**：含两组AUIPC/JALR、一条JAL、五个B型门、三个C.J及关键存储宽度独立字段；没有运行F13/旧检查器或作者JSON驱动的重放。另查新JSON解析、报告相对链接、Git忽略、独占文件及diff。源码/报告可复验，逐指令结果按规则仅留本地原路径，未提交推送。

有种子后继只继承已登记 **F15**：`Q=word(loop+0x18)`→同Q的size槽`Q+0x18`写入身份桥；由该任务先解决实际长度，不能由本复核重新展开。若其结果要求新copy算法域，应在旧G03/G04限定不足及真实n/地址形状明确后另登记最小输入分支，不能以函数名自动认证。
