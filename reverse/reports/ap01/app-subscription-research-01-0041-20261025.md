# Q-20：正常 miIO.unsub 删边与归还阶段（0041）

状态：作者静态恢复，待非作者复核。有效 descriptor、既有 reciprocal 图前提下，精确移除、typed aggregate、空对象归还及共享过期清理阶段已恢复；厂商指令语义限定推断，并发、投递和总 manager 销毁仍未知。伪代码不是原源码，静态分析不是执行观察。

## 继承结论与范围

分支 `codex/app-subscription-research-01-20261025`，基线 `841a7a194a9ecdd02935d429c2cdc57e68ae5ab8`。独占本报告及同 stem analysis，遵循主树 reverse-design 3.1/3.2/5.1/7 和 Q-20。原件主树 `roms/0041/ap01-1.0.2_0041.bin`，6,769,704 B，沿 CATALOG SHA256 `972db4c136c7ed9e24a83c07c1a7fd62040ca018b08ca285216d26b1fee3c6b9`；offset=VA−`0x9ffff000`。本轮核长度，不重算全ROM摘要。

继承 `upper-miio-b.md` 的 `0xa0115f7e` / `0xa011d202` 根卡：88 B descriptor 已分类，peer DID匹配和有效有限type是前提。root在mutex `0x62fcaba8` 内先要求peer和匹配topic非零，否则status=-9。`.` 依次处理1/3/4/5/7/2/6/8/9，`prop.` 为1/3/5/7，`event.` 为2/4/6/8，aggregate第三参实际为0；其余调用精确移除。精确成功后仅在重新lookup peer非零时刷新sender8、update_ts和lastseen；aggregate不作这段刷新。

有限查重：主树reports精确搜索 `a011d10e/a01abe54/a0113c8a/a01188a6` 仅命中Q-20登记，未见较晚本体合同；旧callee metadata和根body委托不能代替删边语义。这是给定载体/词项范围，不是全历史负证明。不重做sub创建/allocation-failure，不混同Q19 eventproducer、N03 UiIFace、Q07 P对象。

## 本轮复核或纠正

`0xa0113c8a` 入口 `0xa0113ca8` **先调用 `0xa011bffe` 清理过期peer**，随后日志输出统计及peer/topic内容。本层后续遍历没有图写入；不能把整个函数只称dump并否定此前置副作用，也不能把其后半日志误写成删边。

`0xa01188a6(type,delta)` 仅对九类topic计数作加法，没有本层callback注册/注销调用；所谓type注销应写成最后topic释放前计数减1。外部type注册生命周期未知。

## 真正新增：布局与精确移除

令 G=`0x62fcab6c`。G+0..+0x20为type1..9的9个word计数；G+0x24是peer数；G+0x28=`0x62fcab94`是peer链哨兵；G+0x30是topic数；G+0x34=`0x62fcaba0`是topic链哨兵。

|对象|必要字段与所有权|
|---|---|
|peer P|+0/+4全局链；+8 DID8；+0x10 lastseen；+0x14 update_ts；+0x18 sender8；+0x20 topic-edge数；+0x24 edge哨兵|
|topic T|+0/+4全局链；+8 type byte/descriptor起点；+0x60 peer-edge数；+0x64 edge哨兵|
|edge E|+0/+4链；+8对侧对象指针。P侧指T，T侧指P，两侧分别拥有一个edge节点|

`0xa011bfc4(H,target)` 从word(H)遍历至H，比较word(E+8)==target，只删首个匹配。先 `0xa006929a(E)` unlink，再 `0xa002e14e(E)` free，返回1；无匹配返回0，不改上层计数。通用unlink/allocator止API，不展开库内部。

`0xa011d10e(P,descriptor)` 在P=0或 `0xa0118b08(P,descriptor)` 未匹配时返回-9。matcher从P侧edge取T，调用 `0xa0118a40(descriptor,T+8)`，返回0表示匹配；完整语法止API。正常精确移除原序如下：

```c
T = find_topic(P, descriptor); // 无匹配 -9
if (erase_first(P+0x24,T)) P->edge_count--;
if (erase_first(T+0x64,P)) T->edge_count--;
if (P->edge_count == 0) {
    unlink(P); free(P); G.peer_count--;
}
if (T->edge_count == 0) {
    type_count_add(T->type,-1);
    unlink(T); free(T); G.topic_count--;
}
return 0;
```

两侧分别只在erase非零时减1；空P先释放、空T后释放，type计数先于T unlink/free。函数不要求“至少实际删除一条edge”才返回0：匹配T已找到就最终0。因此该返回不是全图一致性认证；正常合同要求有效reciprocal图，未实验异常图。

关键原字：`0xa011d192:11c5` / `0xa011d1a8:01c5` 是两侧erase结果门；`0xa011d1b4:91ef` / `0xa011d1d4:63150902` 是零计数门；`0xa011d1de:efb08fec` 调type_count_add；`0xa011bfe2:efd084ab` unlink先于 `0xa011bfe8:ef206196` free。

## 真正新增：typed aggregate

`0xa01abe54(peerID,target,flag,type)` lookup P，无P直接返回，无独立成功状态。先缓存当前edge的next，再取E+8为T，要求非空且T.type==type。

- type5/6仅flag非零才精确移除；root的flag=0，故这两类在aggregate中被跳过，即使`.`列表包含5/6。调用某type不代表实际删除。
- 其它type比较target与topic中最多0x47 B字段；type3/4用T+0x18，其余用T+0x14。比较API `0xa005340c` 返回0才调用 `0xa011d10e(P,T+8)`。
- 精确调用返回被忽略，P/T可能被释放。原遍历仍按缓存next及后续load推进；本合同保留原序，不擅自修复或据此承诺任意生命周期/并发安全。

Capstone将 `0xa01abe7e:8bc7994c`、`0xa0118b1a:8bc7944c`、`0xa011c05e:8b479a4c`、`0xa0113e8c:8b47994c` 标UNKNOWN。旧root `0xa011632e:0bc7994c` 留存模型解作 `th.lwib a4,s3,9,2`；本轮利用同编码族、源寄存器及后续哨兵比较，推断为base预增0x24后取首edge，**不是独立ISA认证**。P+0x24/T+0x64同时有普通指令调用参数支持。未知原字不改NOP、不修改分析模型。

## 真正新增：共享过期清理、锁与计数

所有进入root锁域的退出都调用 `0xa0113c8a()` 后unlock。因此缺匹配/语义失败也可能清理其它过期peer，status不能证明全图无变更。

`0xa011bffe()` 遍历全局peer链，每peer先缓存next，再调用 `0xa005fa1a()`；RV32 unsigned `(now-word(P+0x10)) > 0x78` 才清理，等于0x78保留。时间API单位与回绕策略未认证，循环不是一次snapshot。

过期P的每个edge：取T，先从T+0x64删反向P节点（不检查erase返回），T.count直接减1；**signed新值<=0**时type_count_add(type,-1)、unlink T、free T、全局topic数减1。随后从P侧删T，P.count直接减1（同样不检查erase返回）。处理完毕unlink P、free P、全局peer数减1。与精确移除的返回门及“==0”条件不同，不能规范化成同一个语义helper。

`0xa01188a6(type,delta)` 将type1..9映射到G+4*(type−1)，word加delta后写回，无饱和或外部通知。本合同仅有效有限type。sharedcleanup/dump由root持mutex时调用；本体不自行lock/unlock。其它caller的锁协议、fanout并发和总销毁未知。

## 响应、Evidence与静态验证

删边/sharedcleanup早于响应分配。继承根卡：parser dispose后申请100 B响应，失败outer=-5；分配成功时result.code承载语义status，finalizer=0才reply，free响应后outer=0。aggregate路径root设status0，不汇总实际edge数；精确无匹配status=-9。**outer0不是实际删成功或reply送达证明。**

旧根卡EID：sub=`ev_c9c083522ddaa5a7c350aad4fd271a4e9fd7998e751e2f4db869cbe71d44272a`；unsub=`ev_d4942aedf1d2ed7b7ee29db9fb686a68f9f7155c6d5706b91f8c5b96da16a7c8`。`upper-miio-b.json` 所列根卡profile digest=`04b34bbb41e8ff5d0cbbc2c7471d390693c40fe70f2e21519e2b21d268c9237d`，来源bundle=`final-0041.evidence.json`。与下列complete记录分账，不混用profile。

主树 `evidence/rea-0041-20261017/evidence/upper-complete.evidence.json`：`/records/245/normalized_result` 为sub，EID=`ev_c22e8476e961b1745b154b77d021ebafc0cedf6d943f1eb10ef9c9b712f6e21b`；`/records/48/normalized_result` 为unsub，EID=`ev_221426fb577a1866be99a4825a47510530b45aec1e8d468aed90c0e391e9f036`。二者profile digest均 `4825fb58a33a3e7d618557975b153b8318cf7e833d190ad16bcbf8bd441ae621`，Ghidra12.1.4 / `RISCV:LE:32:ap01thead2`；完整profile随本地证据保留。

[verify.py](../../analysis/app-subscription-research-01-0041-20261025/verify.py) 仅读原件及旧complete，保留7个授权窗口合计1,780 B：d10e244、abe54170、3c8a738、8b0876、bffe220、bfc458、88a6274。各窗含offset/hex/局部SHA及Capstone5.0.7解码；UNKNOWN原字保留。本轮无新REA EID，未启动或切换共享REA，未运行固件/模型/SIM/QEMU/构建/设备/网络。

## 未闭精确边与交付

正常图变更/归还阶段可独立使用，厂商指令仍是限定推断。下一有种子非作者复核应核上述4处 `th.lwib` 编码，以及aggregate flag0/type5/6跳过、精确零计数与stale signed<=0差异。`0xa0113e54/58` 诊断DID拼接未知字只影响日志，非删边依赖。完整matcher语法、投递、其它caller并发、manager总销毁和外部type注册不在本阶段闭合。

实际检查：原件长度、7窗范围/总字节、关键直接调用目标、根flag0及lock→mutation→sharedcleanup/dump→unlock→response顺序、JSON解析与Git diff。没有目标执行测试，作者不冒充独立验收。开始UTC未及时记录，故实际总耗时不可可靠计算；结束UTC见交付消息，token用量不可得。9–14分钟是派发估计，不能冒充实测。
