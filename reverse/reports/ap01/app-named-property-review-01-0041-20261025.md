# Q21 非作者复核：命名属性更新与即时 report

**可独立使用阶段已闭合但接口未闭。** 接受作者 `5be2e80b03c56e1af6ece0eadddb7bef9be0e57f` 与必要补修 `58cd281071fe4e4ec758a2de476ce29ddb66b5c4` 的限定阶段。纠正一处链插入拓扑表述，真正新增业务为0；不认证完整 publication 回收、并发或云送达。

认领 Q21，非作者 `app_named_property_review_01`。独占分支 `codex/app-named-property-review-01-20261025`，启动基线 `a4979f031d0799f97913c9496213394ab02abb58`。仅写本报告与同 stem analysis，不修改管理认领表、ROM、生产配置或分析器，不回退其他协作者。

## 继承结论与材料

原件主仓 `roms/0041/ap01-1.0.2_0041.bin`，6,769,704 B，SHA256 `972db4c136c7ed9e24a83c07c1a7fd62040ca018b08ca285216d26b1fee3c6b9`；`offset=VA−0x9ffff000`。本轮独立核对长度及摘要；地址不是烧录地址。

作者报告见 [研究报告](app-named-property-research-01-0041-20261025.md)，原检查源仅阅读、未执行。开始时作者尚未合并，输入取自已停作者树 `D:/CodexHome/visualizations/2026/10/24/01a16ec4-7aa8-7b43-a0e8-609e1021781b/ap01-s/named-property01/` 中的同名报告及 analysis；相对引用指向父窗转存后的主树路径：

- [原字窗口](../../analysis/app-named-property-research-01-0041-20261025/windows.json)：仅 `[0xa0116900,0xa0116a3a)`、`[0xa0116a3a,0xa0116ad0)`、`[0xa011c3b0,0xa011c514)`，820 B/281条。
- [root256单条原记录](../../analysis/app-named-property-research-01-0041-20261025/root-record-256.json) 与 [profile](../../analysis/app-named-property-research-01-0041-20261025/root-profile.json)：真实 EID `ev_cae45a84ae40a1571e17792b4854ee16d8f5d44a3f6fe046f24ad031b85410da`，profile digest `4825fb58a33a3e7d618557975b153b8318cf7e833d190ad16bcbf8bd441ae621`。根卡 EID `ev_32e5d4799b24d8b2676f0461c9349f5a6ec6980ea777ad502e1b14f4c1c04785` 不替代真实 root EID。

profile 为 Ghidra 12.1.4、`RISCV:LE:32:ap01thead2`、gcc、32位、base `0x9ffff000`，私有模型 commitment `b4a05993cfa5772e27fcf934422f6bf3ef0c1c5bab9034e93505eca934875039`。其工具局限保留，未把留存反编译认作运行证据。继承根的逐对处理、首非零停止与已成功项不回滚，不重读 tokenizer。

已读主仓 reverse-design §3.1/3.2/5.1/7、rolling 顶部与 Q21 补位行。排除 event `0xa0116ad0`、flush 及其他 owner；callback `0xa0116db0` 仅核指针常量，不读其 body。公共字符串、builder、allocator、链移除与下游 submit 均止于 API。

## 本轮复核与纠正

以下是原字与人工数据流复核，不是执行模型或宿主行为测试。

| 验收项 | 独立核对与结论 |
|---|---|
| root 实参/接受门 | `0xa00ba3da/de/e2` 分别绑定 value/name/`word(command_ctx)` 后调用 wrapper。wrapper name/value 非空、bounded length 参数33/901及上限32/900，随后 validator `0xa0060296`/`0xa0062568` 必须为0；不推断所有文本/JSON均可接受。长度拒绝−10，validator非零原样返回。 |
| 顺序/status | `0xa0116a9a` 先 report，不消费返回；`0xa0116aa4` 用 `word(C+0xd8),−1` 锁，`0xa0116ab0` 以 `H=C+0xd0` 更新，`0xa0116ab4` 保存结果，重读句柄解锁，最终仅返回更新结果。锁/解锁返回均不替代 status；根 ok 不代表发送成功。 |
| 节点身份/名称 | 64 B分配，`+0/+4`链字段，name从`+8`复制32 B且`+0x28`显式NUL；value指针`+0x2c`、容量`+0x30`。同名比较命中复用，不重写name；`+0x38/+0x3c`未知，不命名refcount。 |
| 替换/失败 | unsigned容量比较足够则reuse；不足先alloc，成功才free旧指针并装新指针/容量，再复制不含NUL的内容和终止字节。新alloc失败existing保旧；new entry先撤链，再free非空value，再free entry。lower本层输入门−1、alloc失败−5、成功0；成功标志为`1+(word(entry+0x38)!=0)`。 |
| 厂商字 | 原字`0x00a7d00b`在`0xa0116a0c`：opcode11/rd0/f3=5/rs1=15/rs2=10/shift0/top5=0；主仓旧`ap01thead2.sinc:6442`的`th.srb`写单byte，故目标是value buffer+strlen(value)，写零。未当NOP、未运行模型。 |
| report寿命 | `0xa011c3b0`申请P=0x558 B；finalize `0xa00602e6` 为0才调用 `0xa011c0da(C,S,K)`。S=fp−0xac，K=fp−0x78；K清88 B后tag5/name32，S显写id、length、P、callback及所见零字段。调用返回不检查，立即free P并撤栈；不把S未见字段假定零。builder quoting/raw语义未知。 |

发现并修正：作者最初称“插入H对应链尾”。实际 `0xa011699e..69a6` 写序是 `old=word(H); word(old+4)=entry; word(entry)=old; word(entry+4)=H; word(H)=entry`。`0xa011695c` 从 `word(H)` 沿`+0`遍历，因此新节点是首个遍历节点。不能在未约定next/prev方向时称链尾。作者补修 `58cd281` 仅改该报告一行，本轮读取精确diff并与已核四条写指令及旧加载核对，**补修接受**，没有新增body/导出或重验其他范围。

## 真正新增

新增业务0、新body0。独立 [review_static.py](../../analysis/app-named-property-review-01-0041-20261025/review_static.py) 不导入作者脚本，逐字节比较窗口/每条记录、独立按位拼接6个JAL的有符号立即数且检查rd=ra，检查厂商字字段、两个字符串及root/profile标识；[检查结果](../../analysis/app-named-property-review-01-0041-20261025/checks.json) PASS。人工检查资源原序与上述语义；字节相同和JAL通过本身不证明完整业务。

## 未闭精确边

条目持有name/value副本不等于下游持有P或descriptor。精确断边仍是 `0xa011c4cc→0xa011c0da(C,S,K)` 的复制/持有/publication归还，以及 `entry+0x38/+0x3c` 后续持有者/最终销毁。validator全语法、builder quoting/raw语义、并发一致性、锁失败效果、设备应用与云送达未知。后继如确有兼容必要，只能先登记这条submit边的所有权问题；不以认证公共库或完整回收为本阶段接受条件。标准容器/字符串/锁/JSON可作替代实现起点，仍需另有接受集合合同。

## 检查、时间、提交与停止

本轮静态检查：原件身份；820 B/281条记录连续覆盖；6JAL；1厂商字；2字符串；root必要实参/profile；资源原序；补修单行diff。未执行作者脚本/固件/模型/SIM/QEMU/回放/构建/设备/外网，未切共享REA、未派下级。源码/报告按精确路径本地commit，不推送；commit SHA与提交/停止UTC在最终交付另列。

预估3–5分钟，据作者342秒及近期短复核实测，仅为预测。第一工具起点 `2026-10-24 17:36:37 UTC`；暂停前最后观测 `17:38:08 UTC`，收到作者补修后首工具恢复 `17:39:04 UTC`，两观测间56秒包含调度/补修等待，无法拆成精确纯等待，不计为净技术用时。作者补修独立区间 `17:38:34–17:38:49 UTC` 为父窗提供，不算本代理工作。技术冻结 `2026-10-24 17:40:07 UTC`，自起点3分30秒（包含上述间隔）；提交、停止完整UTC由交付记录。没有有效计算时间或工具等待汇总，token/cached/output/reasoning统计不可得，不造数，不把墙钟称计算工时。

tracked仅报告和review_static.py；ignored仅本stem的checks.json，交父窗同相对路径转存并核对。作者ignored由父窗另行转存，本任务不复制或删除其树。工作树清理由父窗在合并/转存后处理。
