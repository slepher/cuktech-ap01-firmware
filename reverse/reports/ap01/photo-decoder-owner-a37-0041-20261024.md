# A37：照片 reader 副本与返回对象持有

2026-10-24；基线 `f17c7d7`，分支 `codex/re-0041-a37`。本题的正常成功小闭包已得到静态答案：**`a010a65a(W)` 分配对象 O，把 W 的 0x664 字节按值复制到 O；原 ROM 输入指针由 W+0x0c 保留为 O+0x0c。返回 O 经 `a0107dea` 原样返回，写入 `a00ed7f4` owner+0x5c。** 所以栈工作区本身不必跨返回存活；源数据仍由原 ROM 地址提供，没有由此变成整个输入 payload 的独立副本。采用 reverse-engineer-anything 技能；未打开共享可写 REA target。

## 继承结论：已有出处→行为→局限→实际缺口

|已有出处|已解释行为|局限及本轮处理|
|---|---|---|
|[A33](photo-source-abi-a33-0041-20261024.md)、[A35](photo-source-review-a35-0041-20261024.md)|新 source 的可信实参、descriptor+0x10→W+0x0c；W 是清零的 0x664 字节栈区，mode+0x10=0、cursor+0x14=0；setter 的返回非零门|已验收交接直接继承；这里只补 W 的 callee 内复制和 O 返回保存槽|
|`photo-evidence-round3.json#/rea_records/3`，`ev_e3db1fb1f6b8b75d3ba7fbf202ad701f4cd3b8eb42987c05789f1e2626527941`；system complete；main-knob round2|照片五项轮转、caller 与 setter 业务早已有|完整旧照片 body 不是 constructor 所有权认证；不重导、不重做资源|
|主仓 `weather-calendar-complete-0041.json#/evidence/30`，address=`A010A302`，tool=`local GNU objdump, bounded offline ROM window`|旧原指令已留存 reader `a010a5d6`、seek `a010a618` 及 constructor 开头|该 stdout 自带 `Warning: truncated output`，结束在 `a010a69e`；不能当成完整 constructor。复用 reader 原序，仅补必要后段原字节|
|主仓 `page-logic-0041.json#/records/15`，`ev_794a176f91454b7304c06fbfaff53024aa96bf8a3a51698dbb831f8b9359f9ef`|`a0024906` dossier 的 caller/引用清单已有 `a0107dea/a010a65a`|是清零 helper 的 caller 地址信息，不是本题两个函数的完整内部持有合同|
|whole-ROM round1 的 constructor extent `ev_862da6aa4f4b14417538d09fd8597604a77ca3ad056b66262f78060baff3118c`；direct calls `ev_f393168d378cf4adc2a24e457a58025661168ad43e389911148936d1ca730149`|函数范围 `a010a65a..a010a8bb`、依赖地址已有|清单不提供输入槽到返回对象的值流；不算本轮首次发现函数|
|最终 ZIP `tools/ap01/ap01-ui-pages.h`、`tools/ap01/verify_gif.py`；旧 SIM/最终验收|照片页替代实现及资源检查已有|只核 ZIP 成员名，继承 A33 对 pages.h 的读取；不执行脚本、不提取或解码资源、不据文件名认证格式/库版本|
|[A29](image-cache-invalidation-a29-0041-20261024.md)、[A31](image-cache-invalidation-review-a31-0041-20261024.md)；A25/A30/A32、G03/G04|旧源失效合同、allocator wrapper `a008aea0`、copy 接口 `a000589c(dst,src,n)` 已有|全部继承；只核本次实参，必要扩到 0x664 拷贝的指针槽，不套用 PNG/free 或 cache 所有权|

本轮按三个地址有界检查主仓 `reverse/rehost/*.json`（包括较晚 round3）：命中仅 page-logic、weather-calendar-complete。未命中不是从前没有分析的证明；[evidence.json](../../analysis/photo-decoder-owner-a37-0041-20261024/evidence.json) 留存查询边界、命中文件和必要原指令。原 ROM 身份及 `offset=VA-0x9ffff000` 沿用 A33/A35，不另建哈希清单。

## 本轮复核或纠正

没有纠正 A33/A35；将其明确保留的 constructor 未知收窄为下面的已证实合同。旧 reader 是原字节行为，但旧 stdout 被截断；page-logic 只含 caller 地址；SIM/照片源码是替代实现；三类不能合并称完整 ROM 恢复。

- `a010a678` 将参数 W 保存为 s2。mode 为零的 reader 臂在 `a010a5fa..614` 取 word[reader+0x14]、word[reader+0x0c]，以 `data+cursor` 为源、调用者 a1 为目的、a2 为长度，调用既有 copy 接口，再重读 cursor，加保存的长度写回。输入指针没有被递增或覆写；递增的是 32 位 cursor。
- `a010a7be/7c2` 为 AUIPC/JALR，独立目标计算得 `a000589c`，不能只凭旧调用名判断。`a010a7b8` 是 a2=0x664、`7bc` 是 a1=s2，而 a0 为刚分配的 O。
- 厂商字 `a010a7aa: 0b95fa20` 的字段为 opcode=0x0b/f3=1/f7=16/rd=a0/rs1=s5/rs2=a5。只读现存 `ap01thead2.sinc` 的 `th.mula` 规则为 `rd += rs1*rs2`。`a010a814: 0b155505` 对应 `th.addsl a0,a0,s5,2`，得 O+0x664+4N。原字位域与规则都校核，没有修改模型；局部规则不能认证整模型或来源版本。

## 真正新增：一个正常构造→返回持有闭包

`a010a65a` 入口 a0=W，返回 a0=O 或失败路径的零。仅恢复通过既有正常 header/尺寸检查且分配非零的路径；诊断/所有失败臂不在本题。构造器先经 reader 消费两段3字节、两次2字节及三次1字节，作为尺寸和状态；本轮不以这些字节形状预设输入格式或算法库版本。两次2字节 reader 是 `a0107d64`，其 LBU/移位/相加构成小端 u16。

|阶段/原地址|机器合同和持有|
|---|---|
|`a010a79e..7b4`|N=s7*s6（RV32 MUL）；a0先为0x4664，再由 `th.mula` 加5N；`a008aea0(0x4664+5N)`，返回保存s1=O。零分支到既有失败臂，不声称后续必成功。allocator 内部沿用 A25 的不透明底层 heap 边界|
|`a010a7b8..7c2`|copy(O,W,0x664)：保存整个 reader 状态副本，含 O+0x0c 原 ROM data、O+0x10 mode、O+0x14 当时 cursor。没有保存 W 的栈地址；payload 并不因这次结构复制而整体复制|
|`a010a7de..804`|O+0x1c/0x1e 以 SH 保存两维；O+0x20 以 SH 保存状态派生值；O+0x33c 写表计数，reader 以 O 为对象读到 O+0x340；O+0x34=O+0x33c。这里确有有界表字节复制，不能说 constructor 完全不复制输入字节|
|`a010a80a..818`|O+0x658=O+0x664，O+0x65c=O+0x664+4N；随后 `a010a840` 将 O+0x660 设为前者第二区域起点再加N，即 O+0x664+5N。它们指向同一分配内存；不是独立申请的几个所有权根|
|`a010a85e..86c`|调用 `a010a618(O,0,1)`，mode0 的 seek 规则返回当前 cursor；结果保存 O+0x18；O+0x24=0xffffffff。中间正常初始化/输出填充不写 O+0x0c；本题不恢复像素/压缩循环算法|
|`a010a880..886`、`a0107e22..32`|constructor 先 a0=O 再恢复保存寄存器返回。wrapper 只恢复 ra/s0/s1/sp，未覆写 a0，所以 O 原样返回给 setter|
|`a00ed840/842`（A35）→`a00ed884..88c`|s2=返回 O，非零才到成功路径；store32(owner+0x5c,O)。再读 O+0x658，存 owner+0x74，让 owner 持有 O 内部输出区的派生指针；这不构成第二个独立分配|

必要分析伪代码如下，非原源码，也不代替检查/填充原序：

```c
// 入口 W+c=data、W+10=0、W+14=0 来自 A33/A35。
read_initial_fields_and_keep_cursor(W); // 先消费正常头；细节保留在既有/局部原指令
uint32_t N = dim0 * dim1;
O = a008aea0(0x4664 + 5*N);
if (!O) goto existing_failure;
a000589c(O, W, 0x664);                // O+c=data，O+14=当时cursor
initialize_fields(O);                // SH尺寸、内嵌表、输出区；不覆写O+c
O->region658 = (byte *)O + 0x664;
O->region65c = O->region658 + 4*N;
O->end660 = O->region65c + N;
O->position18 = a010a618(O, 0, 1);
O->state24 = 0xffffffff;
return O;                            // a0107dea不改返回a0
// setter非零成功臂：
store32(owner + 0x5c, O);
store32(owner + 0x74, load32(O + 0x658));
```

生命周期结论：ROM source/data → 栈 reader W 借用 data → 分配 O 并复制 reader 状态 → O 持续借用相同 ROM data，拥有自身状态/内嵌表/派生输出区 → owner+0x5c 持有 O、owner+0x74 指入 O。W 生命周期可结束而不使 O+c 变成栈悬空地址。这里“拥有”描述分配与持有关系，不宣称已经闭合最终释放或引用计数。

分配式中的额外 0x4000 字节用途没有在本闭包展开；不可将总分配量误写成只有 0x664+5N，也不由该常数推出算法实现或版本。

## 未闭精确边与必要静态验证

- 本题输入持久化到返回对象及 owner 保存槽闭合。reader 没有从 descriptor+0x0c 的长度建立整体输入上界：已继承 caller 只传 data；不发明总长度或格式类型。正式结构名、准确库版本/编译输入仍未知。
- O 的正常替换/页面退出销毁、owner+0x74 派生指针的撤销顺序不由本题证明；A29/A31 仅为旧 source 的 cache 失效，不能替代 O 的析构。唯一后续闭包可选 owner+0x5c 旧 O 到实际析构及+0x74撤销的正常替换连接，先复用旧 setter/完整阶段，避免重做算法。
- 没有观察实际输入命中、分配/解码/显示成功、运行时访问和页面时序；不恢复所有失败臂、完整压缩/动画算法或动态文件模式。

[verify.py](../../analysis/photo-decoder-owner-a37-0041-20261024/verify.py) 只读主仓 ROM/历史证据与模型，检查9个必要短窗、42项调用/ABI断言及2个厂商原字位域/规则；包括正常对齐 copy 的 bulk `+0x0c` load/store 和尾部循环锚点。copy整体接口继承 A30/A32/G03/G04，没有重新导出整个 helper。JSON 解析、报告链接与 `git diff --check` 验证通过。无目标执行、SIM、构建、回放、设备、外网、资源解码或分析器修改；仅写本题独占 report/analysis。本报告为研究交付，待独立技术复核。
