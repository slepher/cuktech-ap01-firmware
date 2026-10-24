# F33：同M loop退出绑定的非作者限定复核

**限定接受 F32，语义纠正0、新增业务0。** 旧证据支持同M的16B配置与两层退出回调接线，以及所见线程创建非零路径的同L归还caller；不证明实际quit、queued I排空、下层成功或最终free。本项待复核差集可以关闭，功能断边继续保留。

2026-10-24；F11/12；非作者 `/root/g23`，作者 `/root/a56` 已停止。独占 `review-close-f33`／`codex/re-0041-f33-review`，固定 `bd457a6`。按用户本轮“复核并关闭”只核该差集，不滚动补位，不创建下级agent。采用REA技能留存优先；只读主仓F32报告、源码文本、合同、evidence和必要旧记录／合同，**未运行作者check.py**，未新读ROM、callback、close、调度body或模型，不执行目标/IO/固件/SIM/QEMU/构建/旧脚本或外部服务。

## 1. 继承结论

| 出处 | 复用内容与限定 |
| --- | --- |
| [F15](miio-queue-size-gap-f15-0041-20261024.md)／[F16限定接受](miio-queue-size-review-f16-0041-20261024.md) | 同M正常setup中L=M+0x128，Q槽M+0x140=L+0x18，user=M+0xe8；vtable／16B配置安装、正常线程接口与ctx身份桥已验。本轮不重恢复start、queue size或copy算法。有效分离、对齐16B值复制及正常callee保存／后续字段兼容仍是前提 |
| [F32作者报告](miio-loop-exit-gap-f32-0041-20261024.md)与同名合同／evidence | 只核本次绑定和失败路径caller。作者45项自检不代替非作者检查；源码文本只用于了解证据选择，无运行／导入 |
| 旧 `upper-miio-b.json`／`.md` | 复用worker generic finish、e0ac adapter、0788局部生命周期接口及f984独立角色，不重建generic循环或新helper |
| 旧 `upper-routing.md`／`.json` | 复用a011fd3c的generic注销／队列与sync-list处理合同及caller-owned group不在本体free的边界；不是本轮新发现或实际排空观测 |
| [F04](miio-loop-close-review-f04-0041-20261023.md) | 另一个栈loop的close/pending合同不接入本题，不能因同名loop或+0x18偏移相同合对象 |

原件身份仅继承0041、6,769,704B、SHA256 `972db4c136c7ed9e24a83c07c1a7fd62040ca018b08ca285216d26b1fee3c6b9`，file offset=VA−0x9ffff000。本轮ROM读取0B，不重算摘要、不套0031或SIM。

## 2. 本轮复核或纠正

直接从主仓 `evidence/rea-0041-20261017/evidence/upper-complete.evidence.json` 取必要稀疏assembly字段，核对以下record／EID及共同profile `4825fb58a33a3e7d618557975b153b8318cf7e833d190ad16bcbf8bd441ae621`：

| record | EID | 本题必要字段 |
| --- | --- | --- |
|248|`ev_c3dd842723b83165bc8e1a6b235f2005269080da4969520bd0c0f0e413db133a`|同M配置、16B copy实参、vtable第二槽／user、线程返回门及55ba caller|
|195|`ev_9a7e0a186c4ed2b341b4d42187fcb73bebec13d401cd226033d30027d121387d`|worker入口L→s1及vtable+4读取／两参调用|
|309|`ev_f7edb78f19e658d59333a033352ac0d773b5a624c66ecd33e8c823a7d5278ccd`|e0ac从第二参取+40/+48、间接调用及两个强制0返回|
|77|`ev_339445ec35b31491f695197f3dd123d01e24a74489ccc10fde6b5e3f8e1a86c6`|fd3c入口Q检查／L保存，fdc2检查、fdc6重读、fdd0接口与fdd4清槽|

旧局部合同profile则是 **`04b34bbb41e8ff5d0cbbc2c7471d390693c40fe70f2e21519e2b21d268c9237d`**：worker `ev_d6ca150724daa7644ed5506256c6a95b1a2139c22f4d49cf6923fd6bf288bbea`，adapter `ev_9a6f1939371027a133a36f527343d421d82247d825be42acd324c72a304de0f8`，0788 `ev_fed264e8febd84155f55a3ea96b02d2f198fbc22194ca0bf56d1850b312f38df`，f984 `ev_0e30a891adc06e823abfad79fbef5207569374ee6db7fbe1b4ead46340cce0e2`。本轮独立核各自source SHA一致，保留profile分层，不把两个不同EID当同次生产或新原字证明。无新REA生产EID／ISA认证。

84项独立检查核对旧assembly的opcode／operand字段、必要16B传递点、对象偏移算术及合同引用。源码 [review.py](../../analysis/miio-loop-exit-review-f33-0041-20261024/review.py) 仅解析留存文本／JSON；生成 [review-evidence.json](../../analysis/miio-loop-exit-review-f33-0041-20261024/review-evidence.json) 本地忽略保留。此检查是必要旧字段／引用一致性复核，不宣称重新拆原ROM机器字或重新认证旧模型。

语义纠正0。特别精确化接受域：F32写“所见线程创建非零路径”成立；`557c` 返回0跳55da，非零后还存在 `5590` 的signed `s4<a5` 跳55b8，以及日志后 `55b4` 的signed `s4>=a5` 跳563a。因此不能强化成“任何非零返回必调用55ba”，也不能据本片段排除其它未查caller。F32已保留该有限范围，不计语义修复。

## 3. 真正新增：0；接受的绑定与返回域

| 复核项 | 独立接受的事实 |
| --- | --- |
|配置来源／目标|master53b8/53bc构造a0110788存第二word，53c4/53c8构造a010f984存第三word，53d8存user。53f8 a2=16、53fa a1=&四word局部配置、5402 a0=M+164、5406调用copy界面；继承16B复制条件后，L+3c起点使第二／三／四word成为L+40／+44／+48 |
|vtable接线|53ec/53f0构造a011e0ac，53f4写M+15c；53fe写L到M+160。vtable=M+158=L+30，故第二槽+4=e0ac、user+8=L；L+10安装关系直接继承F15/F16，不能仅凭邻近槽猜身份 |
|worker真实ABI|入口e3ee s1=L；e436重取word(L+10)，e440取word(vtable+4)，非零才e444取a1=word(vtable+8)、e446置a0=L、e448 C.JALR。因此字段兼容条件下是e0ac(L,L)，并非普通direct-call图中已有的直接边 |
|adapter真实ABI与返回|e0ac用**第二参**取word(L+40)，非零时e0b8 a0=L、e0ba a1=word(L+48)，e0bc间接调用；此配置即0788(L,M+e8)。回后e0c2强制a0=0，空callback e0c8也强制0；worker e44a将该0存s2。0是适配折叠，不能表示下层成功 |
|另一槽角色|L+44=f984，旧04b34合同为external RPC receive forwarding。当前退出接线读的是vtable+4再L+40，未把L+44作为退出callback；无需重读f984本体 |
|既有0788合同参数化|parent=L、owner=M+e8，所以owner+8c=M+174、owner+880=M+968，与既验两个ctx相连；其下层注销等仍opaque，不认证ctx／资源已free |
|所见同L caller|线程实参a4=s7=L，557c零跳55da；在所见非零分支可达55b8 a0=s7、55ba→fd3c，55be回4fa2。保留callee-saved／分支门，不说实际运行后必清理 |
|Q重读与清槽原序|fd3c先读L+18，fd52保存L；fdc2还检查当前槽，若控制到fdc6，**再次**取word(L+18)为a0，fdd0→a01b3c64；正常返回后fdd4 SW0到L+18。当前Q身份取决于此刻槽值，不沿用setup快照；清槽不是close内部或物理资源全部归还证明 |

因此接受的仅是已有generic角色接到同M的实例绑定与所见caller边界。L和vtable均为M内嵌字段，不能因generic“group”名字另造分配根；Q为当前L+18所持native队列，与F11其它名为Q的栈descriptor不合并。旧generic合同的drain/free角色不等于queued I或其深层资源在该运行实例已排空，也不等于M/L最终free。

复核没有新增业务、ROM或helper正文。最小接受合同 [contract.json](../../analysis/miio-loop-exit-review-f33-0041-20261024/contract.json) 保留所有条件与未闭项。

## 4. 精确未闭与关闭

仍未闭：实际quit触发、worker finish的运行事实、正常运行后哪个caller在何同步条件调用sameL的fd3c、下层callback全部完成、真实queue资源归还、queued I排空／深层责任、后续writer／并发与M/L最终free。adapter0、finished flag、失败caller和generic名称不能替代这些证据。

有种子的潜在后继仅记录，不启动：`0xa011fdd0→0xa01b3c64(a0=fdc6重读的word(L+18))` 的必要正常接口效果；若问实际quit，则必须另有正常运行后的 `caller→a011fd3c(sameL)` 连接，当前线程创建失败边不能替代。用户只授权本轮三项复核并关闭，因此不读新body、不登记/执行新任务。

84项独立留存检查通过，JSON解析、报告引用、`git diff --check`及生成物忽略检查通过。仅本报告与同名analysis；无主树/共享表/生产ROM配置模型修改，无提交或推送。F32差集可限定验收关闭；所有功能断边保留，交付后停止。
