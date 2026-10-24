# Q21：cmd.props 命名属性更新与即时 report 交接（研究，待独立复核）

本阶段恢复 `cmd.props` 借用 name/value 到命名属性条目持有以及即时 report 调用端的合同。关键顺序是 **先 report，后加锁更新条目**；report 的失败/返回不控制条目更新，也不进入命令最终 status。完整 publication 回收、并发和云送达仍未闭合。

## 范围、身份与证据

- 认领 Q21；作者 `app_named_property_research_01`；分支 `codex/app-named-property-research-01-20261025`；启动基线 `8782ea6916e6879af8c044af60d2e5aa6988fb74`。
- 原件 `roms/0041/ap01-1.0.2_0041.bin`，6,769,704 B，SHA256 `972db4c136c7ed9e24a83c07c1a7fd62040ca018b08ca285216d26b1fee3c6b9`；本轮重新核字节数与全文件 SHA256。VA 映射 `file_offset=VA−0x9ffff000`，不把分析 VA 当实机烧录地址。
- 继承父仓 `evidence/rea-0041-20261017/evidence/upper-miio-a.md` §`0xa00ba35a` 根卡，EID `ev_32e5d4799b24d8b2676f0461c9349f5a6ec6980ea777ad502e1b14f4c1c04785`。根卡的偶数至少两参、逐对调用、首非零停止、既成功项不回滚均不重做 tokenizer。
- 核对父仓 `evidence/rea-0041-20261017/evidence/upper-complete.evidence.json#/records/256/normalized_result`，真实 root EID `ev_cae45a84ae40a1571e17792b4854ee16d8f5d44a3f6fe046f24ad031b85410da`。其 profile digest 原值 `4825fb58a33a3e7d618557975b153b8318cf7e833d190ad16bcbf8bd441ae621`，`language_id=RISCV:LE:32:ap01thead2`、`private_model_commitment=b4a05993cfa5772e27fcf934422f6bf3ef0c1c5bab9034e93505eca934875039`、Ghidra 12.1.4、base `0x9ffff000`、32位、gcc。根卡 EID 与真实 root EID 分列，不互换；原件摘要与 subject digest 相符。profile 原值、局限及根汇编保存在本地 `root-profile.json`，完整单条原记录为 `root-record-256.json`。
- 新读 body 仅 `[a0116900,a0116a3a)` 314 B、`[a0116a3a,a0116ad0)` 150 B、`[a011c3b0,a011c514)` 356 B，共820 B；另核两个已引用只读字符串 `a0565828="props"`、`a056c058="method"`。新静态证据不是 REA 新 EID，定位为同 stem analysis 的 `windows.json` 与可复验脚本。
- 派前查重在领域报告/根卡中未定位上述三个 body 的既有恢复；使用主仓最新 reverse-design §3.1/3.2/5.1/7、rolling 顶部和 Q21 行。明确排除 `a0116ad0` 的138 B事件 owner、Q19 flush/event 四 body、`a01af798`。没有读取它们，也不依赖其未验语义。

## 输入和可观察 status

`a00ba3da..e2` 的实参是 `C=word(command_ctx+0)`、当前借用 name 指针、value 指针；并非按形状认同 Q18 的 MIOT 72 B/ctx+228 或 Q15 typed 32 B数组。`a0116a3a(C,name,value)` 的实际寄存器合同如下。

| 顺序/地址 | 接受门和动作 | 本层结果 |
|---|---|---|
| `6a4a..64` | name 非空；调用 `a002de24(name,33)`，结果不得大于32 | 否则返回−10 |
| `6a68..70` | `a0060296(name)` | 非零原样返回，未 report/未更新 |
| `6a72..86` | value 非空；调用 `a002de24(value,901)`，结果不得大于900 | 否则返回−10 |
| `6a8a..92` | `a0062568(value)` | 非零原样返回，未 report/未更新 |
| `6a94..9a` | `a011c3b0(C,name,value)` | 返回不检查 |
| `6a9e..aa4` | `a005f3d8(word(C+0xd8),−1)` | 锁 API 返回不检查 |
| `6aa8..ab4` | `a0116900(C+0xd0,name,value)` | 保存此 status |
| `6ab6..aba` | 重读 `word(C+0xd8)`，调用 `a01b3c8c` | 解锁 API 返回不替代保存 status |
| `6abe..ace` | 返回保存 status | 根命令据此选择 ok/error |

`a002de24` 在此是 bounded-length 调用形状；与已用字符串 API 一致，但本轮不读取其库内部。name/value 都以指向 NUL 终止文本的指针传入；本层没有将 value 转为 bool/整数/浮点/typed 数组，也没有显式类型标记参数。**接受集合还必须满足两个校验 API 返回0**，不能据长度门认定空串、任意文本、任意 JSON 类型都合法。`a0060296` 的名称语法、`a0062568` 的值类型/语法仍止于 API，未展开其内部。校验门的非零具体枚举未恢复。C 有效性由 caller 提供，本包装层未见 C 判空。

## 条目对象、替换和借用终点

`a0116900` 接收的 head 是 **H=C+0xd0**。`695c..69bc` 从 `word(H)` 沿节点 `+0` 链遍历，回到 H 表示无匹配；`a002db16(name,entry+8)==0` 表示匹配。字符串比较的 API 边止于调用端。H、节点和 C 有实际实参/字段联系，不是按节点外形认定 owner。没有发现与事件 `C+0xdc` 为同 head 的证据，不合并生命周期。

| entry 字段 | 本窗口的实际访问 |
|---|---|
| `+0/+4` | 双向链字段；新节点先自指，再插在 H 与原 `word(H)` 之间，成为沿 `+0` 遍历的首节点：`old=word(H); word(old+4)=entry; word(entry)=old; word(entry+4)=H; word(H)=entry`（`699e..69a6`） |
| `+8..+0x27` | 从 name 调用 `a01b406c(dst,name,32)` 建立至多32字节的内联副本 |
| `+0x28` u8 | 新节点显式写0，提供名称副本的终止字节 |
| `+0x2c` u32 | 值缓冲指针，后续复制目标 |
| `+0x30` u32 | 已分配容量，以 `strlen(value)+1` 比较/赋值，不是当前值长度 |
| `+0x34` u8 | 成功更新置 `1 + (word(entry+0x38)!=0)`；初始化以16位写零 `+0x34` |
| `+0x38/+0x3c` u32 | 新建置0；仅 `+0x38` 在本窗口用于上述标志计算 |

无匹配时 `6964..69aa` 申请64 B节点；失败返回−5。节点复制 name、初始化字段并入链后，才处理 value 容量。已有同名节点直接复用，**不新增重复节点、不重写原名称副本**。不能把 `+0x38/+0x3c` 未知字段命名成引用计数或发布对象。

`69c2..69f0` 取得 value 长度并加1。容量足够直接使用旧缓冲；不足时先申请新容量，申请成功后才在 `69d8..e0` 将旧 `entry+0x2c` 非空指针交给 `a002e14e`（free 能力边），随后安装新指针和容量。旧值归还发生在新值内容复制之前。`69f2..6a0c` 按不含NUL的长度复制 value 到条目缓冲，再显式写终止零。

`a0116a0c=0x00a7d00b` 是唯一 Capstone 未识别厂商字；拆字段为 opcode11/f3=5/top5=0/rd=zero/rs1=a5/rs2=a0/shift0。只读既有 `evidence/rea-0041-20261017/ghidra/Ghidra/Processors/RISCV/data/languages/ap01thead2.sinc:6442` 的 `th.srb` 构造器：写单 byte `a5+a0`，因此是 `value_buffer[strlen(value)]=0`。未当 NOP、未改模型，也不认证整个厂商 ISA。

value 新申请失败时：已有节点（s4=0）保留旧指针、旧容量和旧值，返回−5；新节点（s4=1）先以 `a006929a(entry)` 交给链移除能力边，再归还非空 value 指针，最后归还节点，返回−5。正常成功返回0，空 H/name/value 的 lower-helper 本地输入门返回−1。这是本层分配失败正常返回的恢复，不扩异常安全分析。链移除/allocator/free 内部均未读。

name 的 caller 借用到验证/report/比较或内联复制边；value 的借用到验证/report/strlen和内容复制边。成功条目持有内联名称及独立值缓冲，未保存 caller 的 name/value 指针。完整条目销毁、后续消费者及 `+0x38/+0x3c` 全部持有者未知。本层无持久化调用证据，不能推论不存在下游持久化。

## 即时 report 的局部寿命和断边

`a011c3b0` 保存 C/name/value，先调 `a0110984(C)` 并保存返回32位标量 id；不读取该 callee body，不认证其全局唯一性。随后申请 `0x558` B临时缓冲；失败直接返回，包装层仍继续更新。

在调用端可见 builder 绑定该缓冲、使用 id、写 `method` 与 `props`、以 `(builder,name,value,strlen(value))` 调 `a01b6866`，再调用封闭/最终化能力 API。helper 对 value 的 quoting/raw/数值语义仍未知，不把这些调用名代成源码类型。`a00602e6(builder,0,&length)` 非零只走诊断并归还临时缓冲，不调用下游交接；为0才构造两个栈对象。

设 `S=fp−0xac`、`T=fp−0x78`：可见 `S+4=id`、`S+0x10` u8=0、`S+0x20=length`、`S+0x24=buffer`、`S+0x2c=a0116db0`、`S+0x30=0`。T 先清零88 B，随后 `T+0` u8=5、`T+4` 以长度32复制 name。只按实写字段描述，未初始化字节不推为0，也不凭 tag5认定某公开类型。

`a011c4c2..cc` 调 `a011c0da(C,S,T)`，**不检查返回**；`c4d0..d2` 随即归还临时 buffer，之后栈帧撤销。C/name/value 都是借用，S/T 只在同步调用期间有效，buffer 的本层寿命止于该调用返回后的 free。没有将 buffer 的独立所有权交给下游的证据。需要跨调用保留者必须有自己的复制/持有合同，而本阶段不认证其存在。callback `a0116db0` 只作为传入的地址，未读 body、不等同此前排除的 `a0116ad0`。

report 没有本层明确设置的 status 返回合同；不得用其残留 a0解释成功。先 report 再 update 的事实意味着：report 可已交接但本地后续分配失败；report 也可本层失败而本地更新成功。根 `ok` 不是实际设备应用成功、队列持有成功或云送达。锁范围只含条目更新；report 位于锁外，锁/解锁句柄均重读且返回不检查，并发下句柄稳定性、report 与条目消费者的一致性未知。

## 验收边界和重建约束

| 阶段问题 | 本阶段回答 | 保留断边 |
|---|---|---|
| 借用到 entry/report 边界 | 已恢复指针使用、内联名称/值副本及临时 report 栈/heap寿命 | 下游异步复制/持有未知 |
| 同名替换/旧值归还/status | 已恢复比较、容量复用、先申请后归还、失败保旧或撤新节点和0/−1/−5 | allocator/链移除内部、完整节点回收未知 |
| 对象身份 | 实际 C→C+d0→64 B节点链；report 实际同 C/name/value | 不混用事件C+dc、MIOT/typed对象；跨 owner 全图未知 |
| 接受类型与即时 report | 文本/长度/API门及先report后update已恢复 | 校验器语法/值类型，JSON helper语义未知 |
| 锁与正常返回 | update持锁区及重读解锁、仅update status返回已恢复 | 并发、锁调用失败效果未知 |

重建可采用标准字符串/容器/锁和 JSON API 实现这些业务边界；公共 formatter、copy、allocator、builder、队列无需为此继续逆向。若要复现原 API 接受集合，必须另有已登记的校验器合同；本报告不自行放宽到任意值。只恢复此独立阶段，未宣称完整命名属性接口闭合。

## 检查、产物与时间

实际运行 [verify_static.py](../../analysis/app-named-property-research-01-0041-20261025/verify_static.py) 通过：原件身份、820 B逐半字前缀推进、281条指令、6条独立 JAL编码/目标、1个厂商字字段及2个字符串。根 profile/EID/subject摘要从真实单条原记录核对。`git diff --check` 通过；无固件执行、模型修改、SIM/QEMU/回放、构建、设备或外网操作，未切共享 REA，未派下级。作者静态核查不代替非作者复核。

tracked 仅此报告及同 stem `verify_static.py`；ignored 中间产物 `windows.json`、`root-record-256.json`、`root-profile.json`，交父窗转存同相对路径后逐文件核对。报告在任务分支按精确路径本地提交，不推送，commit由交付消息给出。

完整 UTC 开始 `2026-10-24 17:27:43 UTC`（第一工具 clock）；证据/报告冻结 `2026-10-24 17:32:59 UTC`，此段实际墙钟5分16秒。最终提交后结束时间及含交付的总墙钟由最后交付消息记录。无排队/中断，工具调用通常秒级；未另测净工具等待总量，不能用墙钟替代有效计算时长。环境未提供 input/cached/output/reasoning token 统计，不造数。原包6–11分钟中低置信估时仅为派发预测，不是实测工时，阶段提前闭合立即交付。
