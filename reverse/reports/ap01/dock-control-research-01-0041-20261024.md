# Q-02：cmd55 描述表输入、count 与替换生命周期

**可独立使用阶段已闭合但接口未闭；作者交付，待非作者复核。** 描述表基址已经接到本次普通响应的原始 payload：`payload[0x17+i] → I+0x24`。count 另外从固定24B基础信息缓存取得，`0xff` 保留旧 count。固件在这条路径没有生成、排序或校验成固定 selector 顺序；选中留存没有实际远端条目值，因此仍不能证明 `selector=i+1`。此处停止于协议/运行输入边界，不追 MCU。

研究者 `/root/dock_control_research_01`；唯一认领为管理记录23:54节/Q-02行；实查 HEAD `5bbc331ab429fb76e956e50b8081c56f8d278b11`。仅写本报告及同名 analysis，主树独占输出，不建 worktree，不改共享表或他人成果。已读 reverse-design 3.1/3.2/5.1/7，采用 [REA 技能](C:/Users/cogic/.agents/skills/reverse-engineer-anything/SKILL.md) 的留存优先静态流程；没有打开或切换共享 REA、执行目标/模型/SIM/回放/构建、访问设备/网络、修改 ROM/生产配置/分析器、提交推送或派下级。

开始UTC `2026-10-24 15:56:01`；原预测20–29分钟，中低置信：覆盖定位4–6、上游7–10、条目/生命周期5–7、原字/交付4–6分钟。依据P16后继原估20–30、P17单分支约6、Q复核约3–5分钟校准；实际因表直接落到远端输入且无条目值提前收敛，不追库凑时。结束采时和墙钟见文末；token由父窗统一实测，cached input单列，本子任务不估算不可得计数。

## 继承结论

| 已有出处 | 已解释行为 | 本轮差集/保留限制 |
| --- | --- | --- |
| [P16](port-selector-p16-0041-20261024.md)、[Q合并复核](dock-control-review-01-0041-20261024.md) | 四个详情入口使请求index、getter索引和S+7同源；selector从descriptor映射，过滤不比I+0x13 | 只补P16明确留下的同描述表上游、count、正常替换输入；不重验位提取/getter/setter |
| [P17](port-response-p17-0041-20261024.md)及Q复核 | 普通63/65回复清state并同步保存共享1B；不是业务成功 | 完全继承，不查b50d、不补控制确认 |
| [生命周期](uiiface-lifecycle-0041-20261023.md)、[E01](uiiface-item-ownership-e01-0041-20261023.md)、[E02](uiiface-ownership-review-e02-0041-20261023.md) | 380B总对象、424B数组项、同步借用、离线通知先于释放；全局deinit未接逐item嵌套清理 | 只连接本次来源及替换；不重做订阅、嵌套资源或消费者 |
| [B04](poll-phase-one-b04-0041-20261023.md)、[B03](poll-phase-review-b03-0041-20261023.md)、[PR05](telemetry-latch-review-pr05-0041-20261024.md) | cmd55缓存非零门、count ff跳转、缓存重读、phase后奏已解释 | 按必要前提继承，不计新业务；本轮核到描述符基址及来源分离 |
| [B08](basic-info-callback-b08-0041-20261023.md)、[B10](basic-info-dispatch-caller-b10-0041-20261023.md)及其复核 | 基础信息注册/ABI、单项通知与lookup | 没有提供本题实际cmd55条目顺序；不沿全部通知扩展 |
| [B19](uart-normal-parser-review-b19-0041-20261023.md)、[B21](queued-command-review-b21-0041-20261023.md)、[NR01](mode-interface-review-nr01-0041-20261024.md) | 普通匹配响应、当前handler重读、同步缓存比较/复制和派生事件 | 上游帧/普通handler前提及helper语义继承，不重审parser/copy；不把CRC/cmd匹配当条目顺序验证 |

原件为 `roms/0041/ap01-1.0.2_0041.bin`，长度实查6,769,704B，SHA256沿原件身份 `972db4c136c7ed9e24a83c07c1a7fd62040ca018b08ca285216d26b1fee3c6b9`；RV32 little-endian，`offset=VA−0x9ffff000`。没有重算整件hash。

## 本轮复核或纠正

无既有行为纠正。旧生命周期明确把desc的完整生产合同留待核，P16/Q也没有认证实际条目值，本轮没有推翻这些未知。

直接来源为 [retained-initializer.json](../../analysis/uiiface-lifecycle-0041-20261023/retained-initializer.json) 的function，Evidence `ev_6f9f82e5daf0540a1c24a0b85daa2e394785391692765e5e3e100eb7b37ed94c`，`RISCV:LE:32:ap01thead3`，profile `bcefdee5092076e55636e077b45523e203f4b870ae7b7ab547945ed1b8162279`，原source为 `evidence/rea-0041-20261017/round3/evidence/whole-rom-round3-initial.evidence.json`。本轮原字只针对其选中窗；不认证有bad-instruction/不可达警告的完整6044B dispatcher。

缓存helper旧记录另在 `reverse/analysis/uart-response-0041-20261023.json#/functions/1/normalized_result`，Evidence `ev_3a861f94ddb2b4481b6d96b4f46d593f35e2729ecb9022aa64949e92b607615c`，profile `b6368dd18431e8113aa5026c713d41e648ab0f6ddd9421ff6c4a49e23b3cd2f3`。仅查其输入合同以明确固定n不消费view.length，不能把initializer的profile贴给它。callback旧profile继续未知。

## 真正新增

### 同一个响应，两条输入来源

以下为静态指令事实及分析命名，不是原源码或实际通信观察。

| 地址 | 已恢复连接 |
| --- | --- |
| `0xa00a85a0/a4/a8` | 保存 `{u8 cmd,u8 len,pad,word payload}` 到frame−0x50；a2原payload存frame−0x4c |
| `0xa00a8602/8606` | 完整command等于0x55进入88f6；本条路径未用保存的length作表长/count验证 |
| `0xa00a88f6..8904` | `cache_helper(0x62fcb004,24,&view)`；固定前缀同步比较/变化时复制，然后才可能派生0x75通知。不是复制24+count字节，也不是解析条目 |
| `0xa00a8930..893e` | helper返回后，缓存u16@b014与b016 OR非零才继续；为零走既有状态处理/离开，不重建本题快照 |
| `0xa00a8950/8966/898e` | count候选为缓存`b004+0x16=b01a`。非ff才写b01c；ff直接跳8a22，使用既有b01c。没有本地4/5项上限门 |
| `0xa00a8996/89e0/8a22` | 日志/必要调用后分别重读b01c。最终8a22的u8读存s3，成为本次重建N；不能把前面读点折叠成一个永不变化的payload字段 |
| `0xa00a8a5c/8a62` | 从frame−0x4c重载**原始payload**到s2，再加0x17。这是P16的desc实际基址，不是b004缓存、2d0/2d4/6c4数组或ROM常量表 |
| `0xa00a8a64/8a6c/8aca..8b26` | u8循环索引与N比较；数组项按完整i×424寻址，三次独立读取payload[23+i]，分组写descriptor；另写u8(I+0x13)=i。没有按descriptor排序/搜索或按i构造descriptor |

`62fcb2d0/2d4/6c4` 是本前奏按N×8必要分配的其它原始记录缓冲区；本题descriptor读取不经过它们，不把相邻分配误认成表生产。

固定24B缓存只覆盖payload[0..23]，包含count byte22和**第一条descriptor byte23**。i≥1的条目直接来自原payload后续字节，不在这次固定前缀缓存内。即使前24B相同使helper不复制、不发0x75，caller仍按缓存门及count进入重建，并读取当前payload条目；因此0x75不能用作“整个descriptor表变化”的事件。这里不证明远端实际发送过相同前缀/不同后缀。

### 正常输入与替换生命周期合同

可供重建使用的顺序视图如下；显式保留原调用/读取次序，不增加原程序没有的事务或成功门：

```c
// 分析伪代码；ordinary handler确为a00a8582，command==0x55。
cache_fixed_prefix(b004, 24, &view); // 同步copy/可能0x75回调，返回后再读缓存
if ((U16(b014) | U16(b016)) == 0) {
    leave_via_existing_state_calls();
    return;
}
candidate = U8(b01a);
U8(b50c) = 1;
if (candidate != 0xff) {
    U8(b01c) = candidate;          // 保存8950取得的a7，不新增第二次读取
    existing_log_and_raw_buffer_setup(); // 内有多次count重读，count0跳过
}
N = U8(b01c);                     // 8a22的最终快照
ui_deinit();                      // 旧对象离线通知→释放→清全局
T = zero_alloc(380);
global_total = T;
if (T != NULL) {
    T->array = zero_alloc_or_static(N * 424);
    p = original_payload + 23;
    for (i = 0; (uint8_t)i < N; ++i) {
        // 原代码三次重读p[i]，分组写bit6/低4位/bit5..4。
        // 对稳定正常输入合成I.descriptor = p[i] & 0x7f；bit7不复制。
        set_descriptor_groups(T->array + i*424, p, i);
        U8(T->array + i*424 + 0x13) = i;
        log_descriptor();
    }
    U8(T+6) = N;                  // 填完后才发布count
    existing_header_select();
    existing_ota_flag_query();
    online_dispatch(1);
}
// 后续原注册循环及phase/done/sent/轮询合同继承B04等，不当控制完成。
```

上面`set_descriptor_groups`等只是压缩显示原内联片段，没有新增原函数。`a00a5b5c`的日志/返回0职责已有[theme-online](theme-online-0041-20261023.md)合同；不再展开它或公共分配/copy库。

完整输入/寿命边界：

- 正常固定前缀操作需payload至少24B可读；正N的descriptor读取还需从payload+23起至少N字节可读，即总extent至少`max(24,23+N)`。这是重建程序应满足的源有效前提，不是本路径已恢复的length检查，也不借此开展异常输入或长度缺陷判断。无本轮实测payload，无法宣称真实len满足或不满足。
- payload由既有parser响应副本借用传入，不转移所有权；frame保存的是该指针。descriptor值分组写入项，未把p存入总对象/项供稍后借用。本次初始化返回后，下游使用已复制descriptor。源在helper通知、deinit通知和本轮日志/初始化期间的稳定性/可读寿命需由外层正常合同保证；原代码多次读取，不是原子表快照。
- count ff不表示不重建，而是沿用旧N并读取本次payload条目；N=0仍走deinit及总对象申请，数组遵循既有零尺寸sentinel合同，循环不执行。不能把ff自动当255条新表，或把0自动当“保留旧快照”。
- 先释放旧快照，再申请/发布新总对象；总对象申请失败时旧对象已撤销且全局被写0，不产生本块在线1通知。数组分配返回值在本片段直接写入，后续正常填充以有效数组为前提；未恢复整组回滚/业务错误返回。总对象先发布、count填完后才写；没有新证明原子替换、代际字段或取消/迟到隔离。
- 离线通知发生于旧数组尚存时；同步回调后重读全局释放的语义及“全局deinit没有逐项嵌套cleanup”的断边沿E02/lifecycle保留。不能为本题补接一条未发生的释放链。新旧item指针不可跨替换持有，订阅不因本次重建自动被认证为全部摘除。

### 对selector恒等的准确结论

P16已验映射是type0且nibble≤2→nibble+1；type1→4；type2→5；其它→0。由此，稳定输入若要使数组第i项满足selector=i+1，必须额外满足：

| 数组i | 必需descriptor条件（只看低6位） |
| --- | --- |
| 0 | type0、nibble0 |
| 1 | type0、nibble1 |
| 2 | type0、nibble2 |
| 3 | type1、任意nibble |
| 4 | type2、任意nibble |

bit6不影响该selector。i≥5没有selector=i+1的可能，因为此映射最大5；本地count输入范围并没有与此匹配的≤5门。对P16的四个正常入口，仍需实际前四条证明表中条件；**本次没有该实际值**。表可按协议约定恰好满足这些条件，但ROM这条消费者链不足以认证该远端约定或真实物理端口顺序。

重建应继续保持`{array_index, descriptor-derived selector}`两个身份，按P16复制标量/必要双身份匹配；不能把本次定位到payload误写成已证明selector恒等或请求成功。

## 未闭精确边与交付

未闭边已经由“desc基址未知”收窄为：**真实cmd55响应payload[23..23+N)的条目值/顺序与count语义 → 上表恒等条件是否在真实底座成立**。现有选中静态资料没有运行响应值，`b004/b01a/b01c`是RAM缓存地址而非ROM初始化常量。没有可据此继续追的同输入静态排序器；不无种子负搜全ROM、不转追MCU或b50d。

真实后继材料种子是保留来源身份、len及N的同一次cmd55响应字节（payload+0x16和+0x17起N字节），或明确底座协议的有来源条目合同。未来若已有这种留存，直接逐项对上表，无需重做getter/位提取/完整dispatcher。本轮没有执行或授权采设备/网络数据；没有该材料时保留协议输入边界。控制结果、遥测年龄/因果及跨替换迟到关联仍属P16/P17既有未知，不计本题已闭。

本轮自检源码 [collect_static.py](../../analysis/dock-control-research-01-0041-20261024/collect_static.py) 仅读ROM/既有留存，写 [static-evidence.json](../../analysis/dock-control-research-01-0041-20261024/static-evidence.json)。实际PASS：4窗580B，179条原指令连续边界与留存raw_ranges逐字一致；普通RV32+C由Capstone解码，厂商字保留为custom，另核三条索引load寄存器字段；19个基址/count/发布/跳转检查点相符。厂商读取语义继承P16/Q接受合同，不冒充新增ISA独立认证；无目标、模型或历史验证器执行。数量不代表业务覆盖率或独立验收。

交付待非作者检查：①入口保存指针至8a5c/62真实数据流；②固定24B缓存与原payload后续条目的分离；③ff/count重读、正常长度/稳定性前提；④先deinit后新发布与count落点；⑤条件恒等表与实际值未知的区别。没有改作者/共享文件，没有提交推送。

没有新的同底座输入接口、确切VA/对象的静态后继；上述实际响应字节仅是所缺外部证据，不能据此继续静态追MCU。未开展b50d/b50a reader搜索。

交付三文件：本报告、collect_static.py及ignored的static-evidence.json，均保留原路径。JSON解析、三文件尾换行/尾空白、19个本地引用及限定路径git diff --check通过；限定路径状态为两份untracked报告/源码、一份ignored证据。初始曾用错误根目录文件名读取reverse-design、以及将留存assembly当dict/未剥normalized_result读取而失败，随后按真实路径/结构纠正；均为只读定位失败，没有污染结论或他人文件。

UTC结束采时 `2026-10-24 16:01:38`，开始至结束实际墙钟337秒（5分37秒）。提前交付原因是留存足以确认原payload直接来源，而实际条目值落在未留存的协议输入边界；没有凑估时。无主动等待、排队或任务中断；工具往返与静态读取包含于墙钟，工具等待总量及有效工时未独立测量。input/cached input/output/reasoning计数本子任务不可得，交由父窗本轮实际快照单列，不估算。作者自检不等于独立验收，交付后停止，不自行接题。
