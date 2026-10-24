# P-08：底座 OTA 正常进入、应用回调与退出后通信恢复

**可独立使用阶段已闭合但接口未闭，待非作者复核。** 本轮形成可用于重建的“提交进入→同步状态通知→正常结束→局部退出→重新发现”合同；不能据此宣称应用 userdata 最终归还、全局停机或实际底座 OTA 已验。继承状态机和已验局部退出不算新增业务。

认领 P-08，作者 `/root/p08`，独占工作树 `.worktrees/batch-20261024-p/p08`，基线 `5bbc331ab429fb76e956e50b8081c56f8d278b11`；仅本报告及同名 analysis。主树只读，未撤销他人修改。采用 [REA skill](C:/Users/cogic/.agents/skills/reverse-engineer-anything/SKILL.md)，按主树 [流程](reverse-design.md)及管理顶部 P/P-08 行。预算约30分钟，可提前收敛；实际起止与检查见文末。没有打开/切换共享 REA、修改模型、运行目标/固件/模型/设备/网络/SIM/QEMU/回放/构建，没有修改生产、ROM或配置，没有提交推送或创建代理。

## 继承结论与查重

只读 [USB OTA](usb-interface-ota-0041-20261023.md)、[UART重试](uart-retry-receive-0041-20261023.md)、[P-01](mode-stop-p01-0041-20261024.md)、[P-R01](mode-stop-review-pr01-0041-20261024.md)、[B02](poll-phase-writer-b02-0041-20261023.md)、[B21](queued-command-review-b21-0041-20261023.md)、[UiIFace生命周期](uiiface-lifecycle-0041-20261023.md)的必要接口；同一摘链 helper 的无 free 边界另继承 [E06](ctk-app-close-review-e06-0041-20261023.md)。未通读管理历史。

已有出处已解释 D0/D2/D4/D3/D1/D5 阶段、失败码、payload、传输和 CRC，P-01/P-R01 已验退出的局部复位及重新发现。差集是：把正常调用、状态订阅持有和恢复通信拼成一个应用可用合同，并补实际设置页注册/通知/撤销对象桥。报告范围内精确检索 `a01b25e8/a01b25ae/a00a56d4/a00a4708/b53c`，命中上述报告和 E06 的其他 callback 对照，未发现完整 OTA 应用 userdata 合同；这是本次目录/锚点搜索结论，不证明全 ROM 没有其他路径。

原件沿 [CATALOG](../../../roms/CATALOG.md)：`roms/0041/ap01-1.0.2_0041.bin`，6,769,704B，既有 SHA256 `972db4c136c7ed9e24a83c07c1a7fd62040ca018b08ca285216d26b1fee3c6b9`，`file_offset=VA-0x9ffff000`。本轮核长度与必要原字节，不重算原件摘要。

## 本轮复核或纠正：进入和退出的精确时序

以下为原指令的分析视图，非原源码。`bXXX` 均指 `0x62fcbXXX`；stage=`b2ef`、progress=`b2ee`、error=`b420`、transport=`b2f0`，对象身份互不混同。

| 接口/阶段 | 参数、结果和必须保留的顺序 |
| --- | --- |
| `0xa00a56d4()` | 无业务输入参数和已认证成功返回值。transport非0时只 `change_stage(1)` 后返回，不在此安装handler或发送D0；该返回不代表已进入。transport为0且位图`b428`没有bit1/bit0时只日志返回。位图和对应RAM头部是既有全局输入，本轮未认证它们全部生产者。 |
| 有待更新数据的进入 | bit1优先，设置selector=`b429`及header pointer=`b6bc`；注册测试callback=`0xa00a4030`,userdata=200；清error；调用`change_stage(2)`同步通知；**通知返回后**才写control=`b50c=3`、threshold=`b4f8=10`、handler=`b6c0=0xa00a5810`。再重读stage，仍2才构造D0/len16，payload取`0xa026ad80/0xa026ad90`并提交。不能提前安装handler，也不能省掉通知后的重读。 |
| 通知可改变stage | `change_stage`先比较旧byte与传入word，变化时日志、读取当前progress、写stage低byte，再同步分发原始参数。enter的D0门可以被同步通知改变的stage关闭；即使D0未发，随后control/threshold/handler三写已经发生。此为保留原顺序的静态合同，不宣称并发或回调可重入安全。 |
| busy后正常续接 | 普通handler的`0x24`分支在stage==1时调用enter，否则消费固定槽；因此仅在当前handler仍是普通分派、相关通知实际交付且transport满足时有这条重试进入路径。不能把所有busy调用都保证为最终成功进入。传输耗尽只清transport/发0x24，继承UART合同，不等于OTA失败退出。 |
| 正常结束调用点 | 继承状态机：D5阶段7、状态byte0走`0xa00a5b4e→0xa00a4708`；selector1的D4阶段6成功且无bit0待更新也到同出口。另一部分仍待更新时先清bit1/改权重再进入，不当作整流程结束。本轮不重做块传输、CRC或子MCU。 |
| `0xa00a4708()`局部退出 | 依序UiIFace deinit→底座业务cache cleanup→安装普通handler`0xa00a8582`→threshold=2→`change_stage(0)`同步通知→control=0→subcount=`b51c=1`→按callback键撤销测试callback。error、progress和应用订阅没有在该局部body中清除/撤销；外部callee副作用不在这项局部负结论内。 |

这里纠正的是跨报告容易产生的扩大解释，既有报告的局部指令合同无行为纠正：**退出确实立即写普通handler；这次写入不保证其后一直可用，更不代表普通连接和快照已经重建。** stage0通知发生时普通handler/阈值2已经写入，但control尚未由本函数最后写0、测试callback尚未摘链。收到stage0的应用不能从该通知推定全部退出尾部已完成。

## 真正新增：实际设置页订阅、回调消费和撤销对象桥

来源为同原件旧 REA bundle 的必要窗口，非新反编译。设置页constructor `0xa00fcd54`：

```text
W = 0xa00d91c6(...) 返回对象（更深类型/所有权不展开）
T = zeroed_alloc(0x14)       // 0xa00fcd7c..82，保存在s5
U = zeroed_alloc(0x4c)       // 0xa00fcdae..db6，保存在s2
0xa00fd132/136: U+0x34=0, U+0x38=0
0xa00fd160..16a: subscribe(callback=0xa00f6064, userdata=U)
0xa00fd18a/18e/196: T+0=0x1f, T+4=U, W+0x10=T
0xa00fd192..1a6: event_register(W, callback=0xa00f42c6, filter=0x29, userdata=0)
```

s2从`0xa00fcdb6`分配结果赋值后至注册点没有再次作为目的寄存器定义；调用链保留s2的ABI前提和原指令用途共同绑定U。不是把W、T和U都叫页面state。zeroed allocation语义继承UiIFace的`0xa008e362`合同，不展开allocator。constructor中初始化后的其他helper可能改变U字段，故不把`U+0x38=0`外推成永久属性。

OTA状态订阅头为`0x62fcb53c`，boot的`0xa00a562c..563f`设 `{link_offset=8,first=0,last=0}`，与控制订阅头`b554`、item订阅头`b530`不同。节点分析视图为`{word callback@0,word userdata@4,link@8,next@12}`，16B节点尺寸沿同append adapter合同；这里只需要业务保存字段，不重新恢复通用链表。

- `0xa01b25e8(callback,userdata)`按callback单键去重。相等直接返回，不更新userdata；未命中以`b53c`调用append，随后word写callback/userdata。正常路径保留U指针，没有复制0x4c对象、retain引用或转移U所有权的证据。无已认证业务成功返回/注册失败恢复。
- `0xa00a3a0e(stage,progress)`沿head遍历，非NULL callback以`(node.userdata,stage,progress)`同步调用；返回后重读head link_offset并从当前node求next。进度/状态是值参数，不借用payload；U持续借用至撤销，回调期间摘链/销毁的完整约束未知。
- OTA退出只撤销测试callback=`0xa00a4030`，**不会自动撤销**设置页`0xa00f6064`。相同callback键再次注册也不替换旧U；不据此实验异常生命周期或推导缺陷。

`0xa00f6064(U,status,progress)`的本轮静态合同：先按`U+0x38`选择kind7或1，以`0xa008184e()`返回值和`&out`调用`0xa00a7334`；返回值和out都非0才继续，否则日志返回。取得`R=word[out+0x10]`。status==2时word写`U+0x34=1`；status==2或旧flag==1才调用`0xa008e05e(word[U+0x24],progress,0)`，随后status==0才置flag2。日志后重读flag，只有flag2才做结束处理：按当前`U+0x38`条件调用`0xa00f5fea(U)`，再读取error byte，0时写`R+1=0x47`并调用`0xa00fa082(U,0x47,0)`，非0时依当前`U+0x38`选0x48/0x49及第三参1；返回后word清`U+0x34`。

因此应用自身也以“曾参与stage2后的stage0 + 当前error”解释结果，不把任意stage0当成功。这个callback在stage0期间的lookup/UI调用保持不透明，仅认证参数和normal返回先后；没有沿UI库、全设置状态机或异常输入扩展。

实际enter调用点继承旧incoming并核原字节：`0xa00b056a`（owner`0xa00afc88`）、`0xa00fed98/0xa00fedb8`（owner`0xa00fd1ac`）均在一次`0xa00fa082(...,0x46,0)`正常返回后调用无参enter，不检查业务返回值。这里只认证这几个正常callsite，不恢复全部触发事件/设置状态，也不保证它们当时的位图/transport条件。

### DELETE先撤销，但U最终归还未闭

constructor绑定的`0xa00f42c6`原字节窗口以`(word[event+8]&0xffff7fff)==0x29`筛选，`word[event+4]`取W，再以`word[W+0x10]`取T；T为0则直接返回。非0从`T+4`取U，清U的一组word字段（本轮所见+0/+4/+8/+0xc/+0x10/+0x14/+0x18/+0x1c/+0x20/+0x24/+0x28/+0x2c/+0x30/+0x3c/+0x40/+0x44/+0x48），其中不含callback消费的+0x34/+0x38。

`0xa00f42ee/42f2`合成callback=`0xa00f6064`，保持到`0xa00f433a→0xa01b25ae`；随后`0xa00f433e/4340`把T交free adapter，`0xa00f4350`清W+0x10。这证明正常该DELETE局部“清U字段→按同callback键撤销→free T→清W+0x10”。不是free U，也没有证据表明摘链helper会free U或node。摘链无free的底层边界继承E06，不重做公共helper。

`0xa00f42c6`没有被原remove dossier的caller metadata识别为procedure；本轮从constructor的函数指针绑定和该原ROM窗口确认局部callback身份。**不为这段新字节伪造REA Evidence/profile，也不宣称整个owner teardown已恢复。**

## 返回普通通信的可用阶段合同

沿P-01/P-R01继承，下表把正常退出后与普通链的衔接放在同一处；不是重新认证轮询内部。

| 时点 | 可依赖的行为/限制 |
| --- | --- |
| exit正常返回 | 局部直接写handler=ordinary、阈值2、stage0、control0、subcount1；UiIFace离线通知/快照释放已发生，普通新快照尚未由该函数创建。没有取消/排空全部传输的证明。 |
| 下一个有效业务轮次 | LV timer参数+0xc取context；仅context phase3且presence byte+0xc5非0进入。control0时先清RX0x32、TX0x60、活动区0x61；阈值2、handler=NULL、transport0。不会因为上一次exit装过handler就跳过这些写。 |
| 子计数非0 | 日志后重读subcount；非0跳过ordinary安装和D1，随后递增，超过10归零。exit的subcount1意味着按该局部不变值进入时第一轮不发D1；同步回调、外部状态变化及presence门会影响实际轮次，不换算毫秒或保证固定等待时长。 |
| 子计数为0 | 调`0xa00a5558`初始化、安装ordinary handler、按byte清四槽occupied、提交D1/len0/NULL；这仅代表重新发现请求提交，不代表底座回复或已在线。 |
| 后续实际响应 | UART正常接受路径先调用当前handler(cmd,len,payload或NULL)，返回后**重新读取**handler再发0x24。若退出发生在D5响应中，第二次事件会读到退出安装的ordinary；stage0会走队列消费分支，仍受transport空闲门限制。不能凭固定0x24判定成功或出队。普通基础信息0x55再重建UiIFace/在线通知的既有合同沿UiIFace继承，不把所有普通dispatcher认证完成。 |

可供新实现采用的是上述入口、值通知、持有/撤销和阶段门。若新实现提供`accepted/completed`返回、生命周期token、显式取消、等待ordinary-ready或U集中释放，均须标为**新设计**；本报告没有声称原厂存在这些API。应用层可在新设计中把OTA结果和普通通信ready分成两个事件，避免把stage0重命名为ready。

## 实际检查、来源及未闭精确边

[采集源码](../../analysis/dock-ota-lifecycle-p08-0041-20261024/collect_static.py)、[机器证据](../../analysis/dock-ota-lifecycle-p08-0041-20261024/static-evidence.json)、[可读指令](../../analysis/dock-ota-lifecycle-p08-0041-20261024/static-evidence.txt)。实际离线选择17窗1,986B/631条指令；六个小合同完整raw_ranges共710B与ROM相同；13个独立JAL目标、9个store编码寄存器/位宽/偏移、6个小合同raw及1个head初始化，共29项PASS。数字只是检查覆盖，不是新增恢复量。原件读取/Capstone解码没有运行固件或指令模型。

Capstone 5.0.7未知仅`0xa01b262c/0xa01b25e2`，旧REA标为`th.lrw`，链遍历语义沿留存，不把未知改NOP或冒称独立认证厂商语义。新page DELETE窗保留完整raw和普通解码，函数边界只按绑定入口/局部return解释。原普通dispatcher全函数警告继续有效，本轮仅认证选中窗口。

来源逐函数记在机器证据`/sources`，带旧路径/JSON pointer/Evidence ID/profile。OTA和timer、四个新读取的旧应用dossier均为外层workflow profile `b6368dd18431e8113aa5026c713d41e648ab0f6ddd9421ff6c4a49e23b3cd2f3`，语言`RISCV:LE:32:ap01thead2`，底层profile `f71eaf7d63ce1b1fa1671fe1932e6a44e275d3716b51411a6bb6af26d7663a44`沿原报告；不把它们重贴为P-R01另一来源`bcefdee...`。本轮没有新REA会话/Evidence。关键新桥：constructor `ev_0a7220c5ae4a956f8fae6c2b037e1d93b23ae3c41c081dc4696f6a83a2527e97`、callback `ev_91bf3cada1ebc3edebc5feca456fd1605ad5c6e3005a3c40c0e4a94836988b8a`；原bundle精确record pointer见JSON，未复制全bundle或全caller。

尚未闭合：U最终free/归还方与订阅node回收；回调期间修改链或销毁U的同步约束；全部应用enter触发/位图生产者；poll/owner最终注销和全局排空；普通通信实际ready时间与真实设备OTA成功。后四项分别保持原范围未知，不沿CRC、公共queue/driver、子MCU或OTA异常退出扩展。

唯一后继seed：从`0xa00f42c6`绑定的DELETE及`W+0x10=T,T+4=U`同对象，追`0xa00f4340`只free T之后**U=0x4c分配结果的正常页面最终归还**，核是否经同owner class teardown/close清理；现有`0xa00fcdae..db6`为allocation来源，`0xa00fd18e/196`为身份桥。先查较晚页面生命周期成果，未覆盖才取必要业务窗口，保持UI/allocator内部不透明，估20–30分钟。不自行接后继。

起始UTC `2026-10-24 14:18:15`，结束、墙钟及最终引用/独占范围检查见[交付检查](../../analysis/dock-ota-lifecycle-p08-0041-20261024/delivery-checks.json)。无主动等待、无外部中断；最初两次shell受默认目录影响，随后所有有效仓库读写均显式Set-Location/绝对路径，未在其他目录写入。墙钟含工具时间，不冒充有效工时；token由父窗遥测统计。落盘后停止，供新的非作者合并复核。
