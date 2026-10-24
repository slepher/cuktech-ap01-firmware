# P-R08：P-08底座OTA正常应用生命周期非作者合并复核

**限定接受：可独立使用阶段已闭合但接口未闭。** 接受P-08的正常进入、同步通知、正常结束、局部退出与重新发现阶段合同，以及设置页订阅/撤销的U/T/W身份桥；未发现需要作者纠正的行为、ABI或来源标注。U最终归还、订阅node回收、完整关闭及通信ready仍未闭，不能据此标记完整OTA接口或实机成功。

认领P-08，复核P-R08，非作者`/root/pr08`；基线`5bbc331ab429fb76e956e50b8081c56f8d278b11`，独占`.worktrees/batch-20261024-p/pr08`，只写本报告及同名analysis。遵循主树[流程](reverse-design.md)和管理顶部P/P-08行；采用[REA skill](C:/Users/cogic/.agents/skills/reverse-engineer-anything/SKILL.md)，复用已有留存，不打开或切换共享REA。主树只读，未改作者稿、撤销他人修改或创建代理。预算约30分钟，按实际问题收敛，未等待凑时长。

## 继承结论与查重

本题为[P-08作者稿](dock-ota-lifecycle-p08-0041-20261024.md)同题合并复核，作者已停止；不另立OTA研究。原状态机/传输及失败边界继承[USB OTA](usb-interface-ota-0041-20261023.md)、[UART retry](uart-retry-receive-0041-20261023.md)，退出与重新发现继承[P-01](mode-stop-p01-0041-20261024.md)/[P-R01](mode-stop-review-pr01-0041-20261024.md)，响应后重读handler及固定槽门继承[B02](poll-phase-writer-b02-0041-20261023.md)/[B21](queued-command-review-b21-0041-20261023.md)。未重做CRC、传输块、异常输入/缺陷、底座MCU或公共库内部。

原件沿[CATALOG](../../../roms/CATALOG.md)：`roms/0041/ap01-1.0.2_0041.bin`，6,769,704B，既有SHA256 `972db4c136c7ed9e24a83c07c1a7fd62040ca018b08ca285216d26b1fee3c6b9`，`file_offset=VA-0x9ffff000`。本轮独立核长度与有界原字节，未另算摘要账。所有命名和伪代码都是分析视图，不是原厂源码。

## 逐项接受、纠正与未决

| 核验问题 | 决定与必要限制 |
| --- | --- |
| enter输入与返回 | 接受。`0xa00a56d4`从全局transport/待更新位图取输入，未发现供应用判定accepted的业务返回。transport非0分到`5808`只通知stage1；位图无bit1/bit0日志返回。不能把调用返回当已进入或完成。位图/头部全部生产者未闭。 |
| 正常提交的优先级和先后 | 接受。bit1优先，selector/header身份分别为`b429/b6bc`。`574c/5750`注册测试callback=`0xa00a4030`、userdata=200；清error后`575e`同步通知stage2。`5768/5772/5782`随后才写control3/threshold10/handler5810；`578a/5790`重读stage==2才继续D0。不能前移handler或省掉重读。 |
| D0描述符与payload | 接受。`5794/579a/579e`写小端halfword0x10d0，即cmd D0、len16；selector1取`0xa026ad80`，另一臂取`0xa026ad90`，payload pointer入descriptor+4，`57b8`提交。复制/排队结果沿B21；本地调用无成功确认。 |
| 通知ABI与同步边界 | 接受。`0xa00a3df4`先将旧stage byte与传入word比较，变化才写stage低byte并以原word及当时progress分发。`0xa00a3a46/48/4a/4c`以`(node.userdata,stage,progress)`直接同步调用；返回后重读link_offset并求next。值参数不等于payload借用；回调可重入及遍历期间摘链/销毁安全未认证。 |
| busy正常续接 | 接受限定合同。ordinary的0x24局部在stage1调用enter，其他stage到槽消费器；仍须当前目标是ordinary且通知实际交付。UART耗尽清transport并通知0x24沿旧合同，不增加“总会重试成功”或“OTA失败退出”。 |
| 正常完成到同出口 | 接受。handler5810的D5 stage7/status0到`0xa00a5b4e→4708`；selector1的D4正常成功且无bit0也到该出口。有bit0时`5a54/5a5a/5a5e`修改权重/清bit1再enter，不能命名为整个OTA结束。D4/D5更早解析/状态生产沿USB OTA继承。 |
| exit直接顺序 | 接受。`4710/4714`依次UiIFace deinit与cache cleanup；`4724`普通handler=`0xa00a8582`、`4730`threshold2；`4734`通知stage0；之后`4740`control0、`474e`subcount1、`4752/4756`按测试callback撤销。局部没有应用callback撤销或error/progress清零。callee副作用不纳入本地负结论。 |
| stage0时能依赖什么 | 接受作者限制。通知期间普通handler与阈值已写，但本函数尾部control0/subcount1/测试摘链尚未执行；不保证这些字段当时仍是旧值，也不保证回调不修改它们。stage0不是退出尾部全部完成，更不是ordinary-ready。 |
| U/T/W来源与身份 | 接受。constructor`0xa00fcd54`的W是`0xa00d91c6`返回值存s1；T为0x14分配结果存s5；U为0x4c分配结果在`fcdb6`存s2。独立核完整constructor原字节/留存，至注册点s2无重新定义，依赖常规callee保存s2的ABI。U字段写不能当s2重定义。 |
| 实际订阅与DELETE绑定 | 接受。`fd164`把s2/U送a1，`fd160/166`构造callback6064，`fd16a→a01b25e8`。`fd18e`写T+4=U、`fd196`写W+0x10=T；`fd192/1a0/1a4/1a6`将W和callback42c6、filter0x29、userdata0交事件注册。三个对象不可混同。 |
| 订阅持有和去重 | 接受。`b53c`是OTA订阅头，与其他head区分；callback@0/userdata@4/link@8/next@12。subscribe按callback单键查重，命中返回而不替换U；新节点word保存U。无U复制、retain或所有权转移证据。尺寸/通用append、摘链无free边界沿既有合同，不再认证链表库。 |
| callback消费与结果 | 接受。`6064`保存a0=U/a1=status/a2=progress；lookup(kind按U+0x38选7/1)的返回和out同时非0才进入处理。status2写U+0x34=1，stage0在参与flag条件下变2；日志后重读flag2才结束处理，读取当前error，结果写`R+1`并调用`fa082`，正常返回后清flag。lookup/UI及日志调用不透明，不外推任意stage0成功或字段永久不变。 |
| DELETE对象及撤销/释放 | 接受。`42c6`筛选`event+8 & 0xffff7fff == 0x29`，event+4取得W，再取W+0x10=T、T+4=U。先清所列U字段；a0保持callback6064至`433a→25ae`；`433e`把s1/T送free adapter，`4340→a008ab8a`；最后`4350`清W+0x10。这里只free T，不能写free U或node。 |
| 应用enter callsite | 接受。`b056a/fed98/fedb8`均在`fa082(...,0x46,0)`正常返回之后调用enter；没有检查enter的业务返回。仅认证选中callsite，不声称恢复所有触发事件和位图生产者。 |
| 退出后重新发现 | 接受。P-R01前提成立时，phase3/presence非0及control0分支先清RX/TX/活动区，再`8110`清handler=NULL；日志后`8146`重读subcount非0跳过ordinary安装/D1。subcount0才`8150→5558`、`8160`恢复ordinary、清四槽occupied并`818c`提交D1。不能因为exit装过ordinary而省略其后清NULL，不换算固定毫秒或保证立即重连。 |
| 响应后的第二次目标 | 接受继承边。B02/B21/P-R01已认证正常响应先调用当前handler，返回后重读handler再发0x24。因此D5内退出可使第二次调用读到ordinary，但stage0只走队列消费分支且仍受transport空闲门。未据此保证出队、在线、快照或ready。 |
| 来源/profile | 接受。13项source逐项匹配旧留存Evidence ID与workflow profile`b6368dd18431e8113aa5026c713d41e648ab0f6ddd9421ff6c4a49e23b3cd2f3`；4个应用bundle原记录同时匹配原件ID及`RISCV:LE:32:ap01thead2`。P-R01另一dispatcher来源`bcefdee...`不移贴。本轮无新REA Evidence/profile；DELETE只按ROM字节和constructor绑定证明。 |
| 完整关闭/ready | 接受未闭。U最终归还及node回收、同步销毁/摘链约束、owner最终poll/timer停用、全局取消/排空、实际通信ready时间和真实设备成功仍未知。不能用有限窗口无某条写入证明全局无清理。 |

纠正项为0。本轮未修改作者稿；新增业务恢复为0。上述`bXXX`均指`0x62fcbXXX`，对象类型及业务命名沿分析视图。

## 真正新增与实际独立检查

[独立源码](../../analysis/dock-ota-review-pr08-0041-20261024/review_static.py)仅使用Python标准库，从原ROM按半字长度位分帧，直接提取所选RISC-V JAL、B、AUIPC/JALR、store、c.mv位域；没有运行或导入作者脚本，也没有执行指令模型。必要旧留存汇编见[选中视图](../../analysis/dock-ota-review-pr08-0041-20261024/retained-selected.txt)，[机器记录](../../analysis/dock-ota-review-pr08-0041-20261024/independent-review.json)保留原字节、来源pointer及具体检查。

实际检查108项PASS：17个JAL、17个store、10个B分支、2个AUIPC/JALR、9个c.mv；17个作者数据窗1,986B逐字节与ROM一致；六个小合同旧raw_ranges共710B与ROM一致；13项旧Evidence/profile配对共26项；4个应用原记录的原件ID。独立选择15窗2,834B/903条**长度分帧**，包含完整constructor的身份桥；这不是903条语义独立反汇编，也不是新增恢复2,834B业务。检查次数只是覆盖，不是功能完成量。

`0xa01b262c/0xa01b25e2`的th.lrw语义继承旧证据；本轮没有假称标准解码器确认其厂商语义。原普通dispatcher全函数警告继续有效，只接受所选局部。DELETE没有旧procedure Evidence身份，仍保留原稿的绑定/局部返回边界。未执行目标、设备、网络、SIM/QEMU、回放、构建或模型，未改ROM、生产配置或分析器，无提交/推送。

## 未闭精确边与交付

可用阶段是“调用enter→有条件D0提交→同步状态/progress消费→正常完成进入局部exit→按presence/phase/subcount重新发现”，以及实际UI正常订阅/DELETE撤销T释放。实现若增加accepted/completed返回、owner token、显式cancel、ordinary-ready事件或U集中释放，必须标为新设计。

唯一后继保留作者seed：`0xa00fcdae..fcdb6`分配的同U，通过`T+4=U/W+0x10=T`追正常页面最终归还；现有`0xa00f4340`只释放T，不能借此跨成allocator/UI库研究。本轮未继续此后继，先查较晚同owner生命周期成果后才能另行登记。

UTC起始`2026-10-24 14:29:36`；结束、墙钟与独占文件/链接检查见[交付检查](../../analysis/dock-ota-review-pr08-0041-20261024/delivery-checks.json)。无主动等待、无外部中断；初始两次相对路径读取受shell默认目录影响未成功，随后有效操作均用绝对路径，未在其他目录写入。墙钟含工具时间，不冒称有效工时；token由父窗实测统计。四类结论已分账，落盘停止，由父窗整合。
