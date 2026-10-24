# P-R01：P-01模式停机阶段非作者合并复核

**限定接受：可独立使用的局部关闭/重新发现阶段已闭合，完整取消与排空接口未闭。** 本轮未发现要求作者纠正的对象身份、ABI、状态或来源错误。离线清协调阶段与重新发现清期望/活动传输/四槽是不同阶段；迟到入口只有静态条件可达证据，不能写成实机已经发生，也不能把局部无显式取消外推为全局无取消。

认领仍为P-01，非作者复核者`/root/pr01`（P-R01），基线`5bbc331ab429fb76e956e50b8081c56f8d278b11`。独占本报告与同名analysis，主树只读，未撤销其他修改。采用[REA skill](C:/Users/cogic/.agents/skills/reverse-engineer-anything/SKILL.md)，遵守主树[流程](reverse-design.md)及管理P段/P-01行；不运行或导入作者验证器，不开/切共享REA，不运行目标、模型、固件、构建或回放，不接设备/网络，不改原件、生产、配置，不提交推送，不创建代理。预计约30分钟，可提前收敛。

## 继承结论

只读主树作者[报告](mode-stop-p01-0041-20261024.md)及其analysis；必要前提继承[N01](mode-interface-n01-0041-20261024.md)、[NR01](mode-interface-review-nr01-0041-20261024.md)、[dock](dock-presence-polling-0041-20261023.md)、[F01](miio-deferred-lifecycle-f01-0041-20261023.md)与[F02](miio-deferred-review-f02-0041-20261023.md)。正常57/60协调、同步通知/源payload复制、四固定槽消费、MiIO分配/start失败与到期stop/free合同不重复研究；原有最终loop清理、串行化及驱动寿命未知继续保留。

原件沿[CATALOG](../../../roms/CATALOG.md)：0041 `roms/0041/ap01-1.0.2_0041.bin`，6,769,704B，既有SHA256 `972db4c136c7ed9e24a83c07c1a7fd62040ca018b08ca285216d26b1fee3c6b9`，映射`VA-0x9ffff000`。本轮核实际长度及必要原字节，不重算摘要账。

## 本轮逐项接受、纠正与未决

| 阶段/问题 | 复核结论与精确限制 |
| --- | --- |
| 三个入口的清理原序 | 接受。ADC `0xa00a4302/4306`、OTA退出`0xa00a4710/4714`、普通handler事件0x23的`0xa00a884c/8850`均依次到`0xa00a3d22`和`0xa00a3ab6`。前者按继承合同同步UI离线/快照释放，后者释放业务缓存。事件0x23先读`b50c`，等2跳出，否则先写2再清理；cleanup尾清0，不能命名为永久关闭闩锁。ADC确认次数/阶段3排除直接继承dock，不假装本轮重验ADC全部输入。 |
| cleanup对象/所有权 | 接受。`0xa00a3ab6..3b21`以word读`0x62fcb2d0/b2d4/b6c4`，非NULL才调用free，返回后各自置NULL；`b01c`只在首槽非NULL臂清。尾部还清`0x62fcaef0`、byte `b51d`及`b50c`。没有把cache指针当四槽或timer.data。完整局部body无`b01d`、活动state、handler、四occupied或9428.data显式写；外部free/日志/通知副作用和别名不在该负结果内。 |
| 期望清零与初始化 | 接受。`0xa00a557c`为byte清`0x62fcb01d`，同时继承两个16bit控制值清零和`b518=3`。`0xa00a55ba..55ff`先零三动态指针和`b50c/b51c`，`55fc`调用5558；这是有限前缀所支持的初始化形态，不推全函数。既有coverage direct_calls只有55ba、805a两个caller，两个实际callsite均核原ROM；间接caller和metadata遗漏仍未穷尽。三条关闭链并不直接调用5558。 |
| 805a对象与presence门 | 接受。`0xa00a806a`从LV timer参数`a0+0xc`取得s1 context，phase位于context+0x190，presence位于context+0xc5。该对象不是共享MiIO timer `0x62fc9428`。phase3且presence零，`80b2`直接到`826c`日常计数段，日常尾`82bc`跳回阶段推进；该轮不经过retry、重新发现或四槽清理。只能据此限制该次业务分支，不能证明LV timer/poll已注销。 |
| 重新发现与重读 | 接受。presence非零、`b50c==0`才先清`b458[0x32]`、`b48c[0x60]`、`b2f0[0x61]`；活动传输对象在第三段，区间结束于`b350`，不含四槽首址`b354`。再写`b4f8=2`、清`b6c0`当前handler、再次清state。`8120`取`b51c`用于日志；`8146`在日志返回后重读，非零跳`81ae`，只有为零才`8150→5558`、安装普通handler、清四槽occupied并提交D1。不能前移重读或把全部复位当一个原子动作。 |
| 四槽与关闭结果 | 接受限定合同。`816c/8170/8174/8178`分别byte清`b354/b384/b3b4/b3e4`，这是固定槽逻辑丢弃，没有请求级失败/完成返回或动态payload归还。D1 descriptor仍是cmd/len低字节与payload指针布局，源数据同步复制责任按N01继承；调用返回不代表入队成功或底座已重连。 |
| 在途parser/handler | 接受条件可达性。独立核`83f8..8421`的s1=`b458`、s3=`b2f0`；所选响应窗依次核CRC、state2、cmd匹配，复制后`851a`写state3，取当前handler调用，再`853a`重读handler发送0x24。重读后没有第二个NULL测试，不能用入口非NULL代替回调后的全局状态；不据此做异常/缺陷实验。该窗口无presence、`b51d`关闭门。只有UART/loop仍交付、相关内存有效及外部调用正常返回，才可继承cmd57阶段0采纳/cmd60当前期望分支和0x24续接队列的正常合同。未证明实际迟到或离线一定出队。 |
| MiIO kind1 ABI/当前值 | 接受。`0xa00a0bf0`从callback参数`a0+0`仅取一次请求到s4，s5保存timer；日志后`c20`重读请求kind，kind1分到`cf0`。该臂读取当前`0x62fcaff2`，减1后截u8，无符号范围仅0..3才以a0调用`0xa019537a`。没有使用请求value快照，没有presence/`b50c/b51d`/generation门；外部callee正常返回后到共同free(saved request)，再清保存timer.data。共享9428身份和到期前stop继承F01/F02，不把a0误作请求对象。 |
| 失败/取消/最终清理 | 接受“未闭”。原有retry耗尽state清理与0x24通知、scheduler start失败free但不清data均按N01/F01/F02继承；presence零跳过retry不是耗尽。上述完整局部cleanup无显式stop9428/data free，不覆盖owner关闭/loop walker、间接callee或别名。handler/poll/LV timer最终停用、9428最终data归还及全局排空均未闭。 |
| 来源与profile | 接受。8项作者sources逐项匹配对应原留存的Evidence/profile，特别dispatcher `ev_6f9f82e5...`是`bcefdee5092076e55636e077b45523e203f4b870ae7b7ab547945ed1b8162279`，不能套成其他源的`b6368dd...`。初始化70B只有离线字节，无新增REA Evidence/profile。whole-dispatcher旧警告继续有效，仅认证本题窗口。 |

没有要求作者修改的纠正项。上述地址中的`bXXX`均为`0x62fcbXXX`的简写，`aef0/aff2/9428`按完整地址区分；状态与对象别名只是分析命名，不是类型认证或产品语义证明。

## 真正新增与实际独立检查

新增业务恢复为0；这是P-01同题非作者复核。独立[脚本](../../analysis/mode-stop-review-pr01-0041-20261024/review_decode.py)直接从原ROM半字边界推进，以Capstone 5.0.7解码RV32/RVC，独立计算JAL、B、压缩分支/跳转位域；完成独立结果后才比较作者证据，不读取或导入作者验证器。实际为18窗1334B、407条指令、16个关键边断言PASS，作者366行raw/asm逐行相同，8项原来源完整raw_ranges共8774B与ROM一致。后者是来源字节匹配量，不能冒称解码/恢复8774B业务。

[机器证据](../../analysis/mode-stop-review-pr01-0041-20261024/independent-decode.json)与[可读指令](../../analysis/mode-stop-review-pr01-0041-20261024/independent-decode.txt)保留精确窗口、调用/分支目标、来源及metadata范围。UNKNOWN为`0xa00a830a`，以及独立选入日常出口的`0xa00a82b4`（旧留存命名th.mvnez）。未修改模型或补NOP；本轮只核后者周围控制流，不认证其算术、日常计数数值或厂商指令语义。没有重做公共poll/timer内部。

## 未闭精确边与交付

可供重建直接使用的是：三入口有序局部释放；离线清`b51d`与重新发现清`b01d`分离；重新发现按`b51c`重读门清四槽；parser/MiIO按当前全局状态继续处理的条件入口。若新实现加入generation拒收、cancel future、全局排空，应明确为新设计。完整停机接口不能标已闭。

真实后继仍仅为作者已保存的poll注册种子：`0xa005b300..b313`构造`a2=0xa00a8330`、`a1=1`、`a0=s3`并调用`0xa009f9b6`。独立核原字节、call位域与factory-test retained initializer的Evidence `ev_dc0e38b0f382799ea2a8e8ad7f21cefc5998b0767ecf38a58cfdebe8add167c3`/profile `bcefdee...`。尚未把s3绑定到owner/fd；只建议从该来源到同owner stop/close核业务销毁先后，不扩公共walker，也未在本轮继续追踪。9428注册节点/最终data清理仍为旧断边，不另列无新种子的公共内部任务。

首个精确工具UTC `2026-10-24 13:58:46`；结束/墙钟及文件检查见[交付记录](../../analysis/mode-stop-review-pr01-0041-20261024/delivery-checks.json)。初始默认shell曾回到其他目录，随后全部有用仓库操作均显式Set-Location，未在其他目录写入。无主动等待、无外部中断；墙钟含工具时间，不冒充有效工时，token由父窗遥测统计。本报告和独占analysis落盘后停止，等待父窗整合。
