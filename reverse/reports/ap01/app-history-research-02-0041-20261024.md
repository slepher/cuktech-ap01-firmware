# Q-03：普通详情 page0x13 正常关闭的 payload 资源边界

**部分恢复；P 最终归还仍未闭，作者交付待非作者复核。** 正常 Return 在详情确为最后枚举子对象的前提下，把该 GUI 对象交给公共删除；DELETE 清 P 内控件引用、删除 P 的 timer、归还 R 并清 W 的挂接。既有公共析构合同及本页实际 base class 不能补成 free(P)。本轮沿明确同 P 的构造尾部调用检查后，没有取得新的 P 归还/转移种子，按登记要求提前交付，不扩成全 ROM 负搜。

认领 Q-03，代理 `app_history_research_02`；唯一登记 [管理记录](rolling-management-0041-20261023.md) 2026-10-24 23:54 HKT 节及 Q-03 行；实核 HEAD `5bbc331ab429fb76e956e50b8081c56f8d278b11`。独占本报告及 [analysis](../../analysis/app-history-research-02-0041-20261024/)。父窗授权直接写主树，不建 worktree，不改共享表、作者成果或其他工作。

已读 [reverse-design](reverse-design.md) 3.1/3.2/5.1/7，并应用 [REA skill](C:/Users/cogic/.agents/skills/reverse-engineer-anything/SKILL.md) 的留存优先、有限边和事实/推断/未知分账。未开/切共享 REA，没有执行目标、模型、SIM、构建、刷机或网络；未改 ROM、生产配置、分析器；未派下级、提交、推送、reset/clean。

## 继承结论

- [P19 非作者复核](app-history-review-01-0041-20261024.md) 已接受 W=s2、R=s7、P=s1，P 为独立零化的0x6c B分配；`0xa01b0614/0618/0620` 写 R.id=0x13、R.payload=P、W+0x10=R。不重做 creator/ring、首次消费、maximum=0 或换端口算法。
- [PR12](history-reader-review-pr12-0041-20261024.md) 的同步标量消费和 GUI API 边界保持；图表只接收取出的数值，不能把 I inline ring 与 P 合并。
- [E06](ctk-app-close-review-e06-0041-20261023.md) 已接受 `0xa00dcf52` 条件删除次序：置删除位→发送0x29；发送结果允许继续时才清事件列表、递归child0、处理输入/动画、class析构、摘父数组和free(obj)。事件失败可清位返回，因此不能无条件写成所有删除调用均完成整棵树回收。
- E06 及 [H04](weather-page-close-review-h04-0041-20261023.md) 已覆盖 class walker/base dtor：class+8 回调后重读 base；base 内明确释放的是 GUI 扩展/其数组，未以 obj+0x10 直接取业务 payload。opaque 辅助内部不作全局否定。本轮不重做这些公共析构函数。

原件身份复用 CATALOG/P19：`roms/0041/ap01-1.0.2_0041.bin`，6,769,704 B，SHA256 `972db4c136c7ed9e24a83c07c1a7fd62040ca018b08ca285216d26b1fee3c6b9`；RV32 LE、`offset=VA-0x9ffff000`。本轮只核长度与选定原字节，不另造哈希账。

留存出处：`reverse/rehost/charge-0041-round4.json#/records/2`，Evidence `ev_e30acc99f01e5e79a06965e472ec0c1aee39a56a7c3e8ae8ad7fdef09673d74e`；`charge-complete-0041.json#/creator_continuations/2` 的 Capstone5.0.7 RV32+C 续体；其 record19 Evidence `ev_709b5ff51cf4fb33e1b9ae866819ac7a860e0ffe029c2c56c7e9344ac037af88` 的普通消费沿 PR12。旧载体 profile 缺失、generic/custom/no-return 局限继续保留，不贴现代 profile。普通 caller 的真实载体是 `reverse/rehost/system-complete-0041.json#/cached_evidence/charge_a00f61ae`。本轮 callback 原字载体采用 P19 的 static-evidence.json，直接重读 ROM 核必要字节，没有把作者脚本执行结果当新增独立验收。

## 本轮复核或纠正

| 有限连接 | 原字与判定 |
| --- | --- |
| 实际 W 的 class | `0xa01afda6:ef9002c2` JAL 到 `0xa00d91c6`，`afdaa` 非零路径后 `afdac:2a89` 保存 W。factory 薄接点 `d91d0:aa85` 把 parent 传 a1；`d91d2:374526a0`、`d91d6:130545ef` 构造 class=`0xa0263ef4`；`d91da→0xa00d76ae`。原 class 前16 B `00000000c4540da0d0870da07ab00da0`，base=0、dtor=`0xa00d87d0`。因此这个 W 是普通 base 对象，不得套用主 app/window 的 timer/G 析构身份。class walker/base 行为直接继承 E06/H04。 |
| DELETE 的 target 身份 | `1bac:83294500` 取 **E+4 original target** 到 s3=W；不是 E+0 current_target。`1bb0` 取 R=W+10，R非空后 `1bb8` 取 P=R+4。沿原过滤 `(code&0xffff7fff)==0x29`，userdata 注册值为0；不能把 descriptor userdata 解释成另一个 P owner。 |
| DELETE 的严格原序 | `1bbc:a84c` 先取旧 timer=P+58；随后清 P 的0/4/14/1c/20/24/28/3c/40/44/64等 GUI 字段，`1bea→0xa008ae58(timer)`；`1bee:4a85` 明确 a0=s2=R，继续清其余控件字段，`1c10→0xa008ab8a(R)`，`1c14` 清 W+10。P+58 本身没有被清，P+60 cursor也没有清；清控件引用不等于逐个delete控件。完整callback只有这两处直接调用，没有 free(P) 或交出 P 给新的清理者。 |
| Return 对象身份 | 沿 P19/Q复核的枚举结果：只把匹配 page0x13 的 payload存s6=P，a0保留 Wlast。`7194:3147`、`7196:6384e700` 为 Return=0xc 门；`719e..71aa` 恢复列表/选择状态，`71ae→0xa00ded6c` 前没有把s6移入a0。正常布局下详情为Wlast，才衔接本页DELETE；任意重排仍未知。 |

P19 对顶层失败处的“删除W”必须按其实际 callee 理解：旧 creator `0xa01afdbe→0xa00d7806` 是 class walker，不能升级成 `0xa00ded6c` 的完整公共删除。该区别已有 E06/H04 合同，不另计新增失败行为，也不在本题展开失败清理。

## 真正新增

新增业务页面/算法0；新增静态连接是**本页具体 class 身份与既有析构合同的接入**，以及一个同 P 有限候选被收缩为外观更新，无法填补 P 归还边。

creator 唯一在较晚续体中直接 `c.mv a0,s1` 的接点是 `0xa01b060c:2685`，紧接 `060e:ef4054ab→0xa00f50c2(P,u16(stack+18))`。本题按这个真实种子读取 `0xa00f50c2..0xa00f51f3`，而非找所有 P reader。该helper保存 s1=P，按 a1 零/非零分两套外观参数；调用时 a0均取 P+0/+10/+14/+18/+1c/+20 的 GUI 字段，a1/a2为颜色/样式参数，末支合流至 `515c..516e` 返回。已核指令没有 free接口、timer接口、event注册，亦无把P本身传给后续callee或持久全局/对象的 store；callee停止在GUI API，不下探内部。因此这里没有形成可继续追的payload归还种子。此次候选筛选只覆盖这份 creator continuation 的显式 `a0=s1`，不证明所有别名或更早调用都已穷尽。

可用于重建的分析伪代码（非原源码）：

```c
Return_if_selected_0xc:
    restore_list_selection();
    gui_delete(Wlast);           // detail identity needs normal last-child layout
DELETE_for_page0x13(E):
    W = E.original_target; R = W.userdata;
    if (!R) return;
    P = R.payload; timer = P.timer;
    clear_first_group_of_GUI_references(P);
    delete_timer(timer);
    clear_remaining_GUI_references(P);
    free(R); W.userdata = 0;
// Continuing public deletion owns GUI child recursion/base destruction/free(W).
// No established free(P) edge; do not invent one as ROM behavior.
```

所有权账：W及其GUI孩子交给公共GUI删除；R明确由本callback归还；timer明确由本callback交给已验timer删除；P为另一个独立分配，已知根 W→R→P 在归还R、清W+10后断开。不能据此认定 P 永久保留、泄漏或不存在别名，也不能把 free(W)、free(R)、series内部释放当作 free(P)。重建若选择显式管理自有P，其归还策略属于实现设计，不是此次已恢复的ROM事实。

## 未闭精确边与交付

精确未闭是 `alloc_zero(0x6c)→P→R+4` 到 **以同一个P为实参的归还/明确所有权移交**。已查同容器登记、完整DELETE、正常Return及具体同P helper仍未给出消费种子；继承的base析构不能代填。本题不展开全ROM free、所有P reader/writer、其他page/summary、根退出、公开图表/分配器内部或timer resume。因此完整payload生命周期仍未闭。

后续仅保留一个带条件的真实断边：现有 creator 的 `R+4=P` / DELETE 的 `free(R)`；若以后其他已登记证据给出保存同P或以同P作归还实参的具体地址，再按该连接去重登记。当前没有足够种子建议再开“找所有释放者”任务。

本轮 [check_static.py](../../analysis/app-history-research-02-0041-20261024/check_static.py) 用新Capstone RV32+C实例读取原件，未知解码保留opaque，不导入/执行目标或指令模型；[static-evidence.json](../../analysis/app-history-research-02-0041-20261024/static-evidence.json) 保存6个必要窗口、174条指令、7个独立JAL目标、69处旧carrier字节匹配及class原字。机械检查数量不计业务恢复量，作者自核不代替非作者复核。未重导creator整函数，也未复跑E06公共析构检查。

首个可得UTC开始 `2026-10-24 15:56:21`。父窗预测20–29分钟，中低置信：覆盖对象4–6、可达清理7–10、关闭所有权5–7、原字交付4–6；比较项P19作者20–30分钟估计、Q复核实际206.656秒。此次材料充分定位、class已覆盖、同P候选未扩出新种子，按父窗明确停止条件提前收敛，不能用阶段估计冒充实际耗时。无主动等待/排队/中断；正常工具等待计入墙钟，有效工时未独立测量。token由父窗统一实测 input/cached input/output/reasoning，cached单列；本子窗无独立用量，记不可用而非估算。

结束UTC、实际墙钟和格式/路径检查见同目录 delivery-checks.json；交付后停止，不自行接后继。
