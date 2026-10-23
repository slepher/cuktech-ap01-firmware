# D01：正常命令提交、构帧、部分写与完成通知

2026-10-23，研究基线 `2ee39b3`，分支 `codex/re-0041-d01`。**正常发送链的局部生命周期已恢复，驱动与全局资源生命周期仍部分恢复，待独立技术复核。** 命令描述符被同步复制到活动区或固定槽，构帧后允许多次部分写；全部字节写出只把传输状态置2。收到 CRC 正确且命令匹配的响应才置3并同步调用 handler，随后重读 handler 槽发送 `0x24`。handler 的具体分支负责归还空闲状态，`0x24` 仅提供一次队列消费机会。

本任务采用 REA skill 的保留证据工作流：复用已有 dossier，直接核原 ROM，不打开共享 REA 会话或数据库。只静态恢复原程序正常业务；没有固件执行、设备/服务连接、历史输入回放、超时研究、长度审计、漏洞调查、OTA 扩展、ROM/生产代码/模型修改。

## 问题、范围与证据

问题是一个调用者提交的 `{command,length,payload}`，如何脱离调用者存储、成为待发字节、经部分 write 推进，再触发正常完成通知和下一槽消费。研究覆盖10个函数身份，其中普通 handler/parser 仅核与此问题相关的窗口；不是认证这两个大函数全部业务。

| 函数/窗口 | 参数、返回、恢复边界 |
| --- | --- |
| `a01951e2..a0195309` | `a0=descriptor*`；无显式业务成功返回。完整恢复活动复制、忙时去重/入槽和启动关系。 |
| `a01915bc..a0191651` | 无业务参数/返回；四槽选择、搬运、调用后清槽沿用 [B20](queued-command-consume-b20-0041-20261023.md)，本轮只核衔接合同，不修改或复核其原文。 |
| `a00ee9ce..a00eea07` | 无业务参数/返回；state1 才构帧、推进 write，再写 attempts/wait。 |
| `a01a4ff8..a01a50fd` | 无参数/业务返回；读活动区、附 CRC、转义到静态帧区。完整指令核对。 |
| `a00ee96c..a00ee9cd` | 无参数/业务返回；静态 frame_len/cursor 驱动一次 write。完整恢复正常推进。 |
| `a0027e94..a0027eed` | `a0=fd,a1=buffer,a2=count`，返回 signed int；新增原字节恢复的包装器。边界由返回和邻接下一入口推定，未附加旧 REA Evidence 身份。 |
| `a0025874..a002589f` | `a0=取得的对象,a1=buffer,a2=count`；返回具体操作的结果。新增原字节恢复的操作表分派器。 |
| `a00a8330` 的 `a00a84ee..8551`、`844e..8453` | 正常匹配响应复制、两次同步通知、发送推进入口。完整解析/CRC沿用 [B18](uart-normal-parser-b18-0041-20261023.md)/B19，不重解。 |
| `a00a8582` 的入口/`0x24`/cmd58窗口 | 普通 handler ABI 与正常完成事件消费；仅局部分支，不能外推整个6044 B函数。 |
| `a0191652..a01916ff` | `a0=cache_dst,a1=n,a2=response_view*`；既有普通缓存 helper，核 state0 写和同步通知对发送链的影响；其轮询合同沿用 dock/B03。 |

[instruction-evidence.json](../../analysis/uart-send-lifecycle-d01-0041-20261023/instruction-evidence.json)保留13个窗口、458条原字节/文件偏移/独立 Capstone 文本与适用的历史 provider 文本；[verify_static.py](../../analysis/uart-send-lifecycle-d01-0041-20261023/verify_static.py)只读主仓库 ROM 和保留记录，只写本任务目录。VA 映射为 `file_offset=VA-0x9ffff000`，ROM 固定原件 `D:/Documents/PlatformIO/Projects/cuktech-ap01-firmware/roms/0041/ap01-1.0.2_0041.bin`，身份沿用 [USB/OTA](usb-interface-ota-0041-20261023.md)。

主要保留记录为主仓库 `reverse/analysis/usb-interface-ota-0041-20261023.json`，其函数级原 dossier、Evidence ID、profile和完整body范围随本轮证据保留。新增检查不重贴这些历史身份：

| 身份 | 原 Evidence ID / 原 dossier（`evidence/rea-0041-20261017/evidence/` 下） |
| --- | --- |
| submit | `ev_6fb98e4786e8bc080925cd55243be39eec18656b73e7123627fed450a4a66af7` / `whole-rom-usb-closure-20261023-005.json` |
| starter | `ev_313ec1bbe3f041925d5f81e95f82eac99ccabf8b54ebeebb31fe2ad1b0536a2f` / `whole-rom-usb-worker-20261023-002.json` |
| frame | `ev_6f837cbc62bd40c5a13276f71d9f1c6343a9399687e53d49e76fbb13bb841b69` / `whole-rom-usb-tx-20261023-000.json` |
| write progress | `ev_2dd7fa785883e602e5643f9c4b2790d32a63979b30fe6664a4ddded5329838a7` / `whole-rom-usb-tx-20261023-001.json` |
| parser dispatch | `ev_6f900403de24d247461a1e302c564c71481c3d43d481acdc83bbb716318e1159` / `whole-rom-private-20261023-067.json` |

上述外层 profile 为 `b6368dd18431e8113aa5026c713d41e648ab0f6ddd9421ff6c4a49e23b3cd2f3`；语言/底层profile归属沿用USB/OTA报告。缓存helper原字节来自 [dock保留窗口](../../analysis/dock-presence-polling-0041-20261023/instruction-windows.json)，其来源/相关复核见 [B03](poll-phase-review-b03-0041-20261023.md)。本轮没有新制哈希或复制清单。

## 存储布局、所有权与状态

所有下列类型和名称都是分析视图，并非原始源码：

```c
struct CommandView { uint8_t cmd, len; uint8_t gap[2]; const void *payload; };
// RV32: cmd@0, len@1, pointer@4；gap没有业务读取证据。
// 活动区：62fcb2f0 state；+1 attempts；+2 wait；+3 cmd；+4 len；+5 payload。
// 四槽：62fcb354/384/3b4/3e4，stride0x30：occupied@0, cmd@1, len@2, payload@3。
// 响应副本：62fcb322 cmd，323 len，324 payload。
// 发送帧：62fcb48c frame[]；62fcb4ea frame_len；62fcb4eb cursor，二者均为byte。
// 62fc91b0 是传给 read/write 的 fd word；62fcb6c0 是当前响应handler word。
```

| 状态转换 | 本闭包可定位写者/意义 |
| --- | --- |
| idle0→prepared1 | submit `a01952e8`，或B20消费者 `a0191620`；活动命令已复制。复制后可能重读state，不能假定复制调用没有副作用。 |
| prepared1→await_response2 | `a00ee9bc`，仅正 write 返回并且新cursor等于重读frame_len；这是本地字节进度完成，未证明底座执行成功。 |
| await_response2→response3 | parser `a00a84f6/8502` 两门通过，复制响应后 `a00a851a`；匹配命令和 CRC 的合同不包含业务结果码。 |
| response3→idle0 | 已知普通缓存helper `a0191668`；其他普通命令也有分支自行清state，例如 `a00a8622`。parser不会统一代劳。此处不是全部写者清单。 |
| idle0再次启动 | 普通handler可能在第一通知内直接提交后继，或第二通知 `0x24` 触发取槽；两者都受当前state及handler业务门控制。 |

调用者保留 descriptor/payload 的存储所有权；submit在函数内复制字节，既不保存descriptor指针，也不保存其payload指针到活动/排队对象。活动payload和队列payload是独立静态字节副本，无堆分配或释放。B20的清occupied是槽的逻辑归还，发生在发送启动器正常返回后，不等“整帧写完/响应到来”，也不清残留payload。响应副本同样是静态缓冲区；通知中的指针是该副本的借用地址，不转移堆所有权。实际可借用时间及跨回调保存规则仍需消费者合同。

帧构造期间CRC两字节写在活动payload尾部，之后从活动cmd开始转义复制至独立frame区。write消费frame，不直接消费调用者payload。完整写用 `a00ee9c0: sh zero,0x5e(s1)` 一次清frame_len/cursor，归还这对发送进度字段供下一帧使用；frame字节未擦除。**构帧函数只将frame_len设2，不清cursor**。本闭包证明正常完整前帧写后的cursor为0，未证明冷启动/断连/其他写者都满足该前置条件。

## 提交到构帧

submit先读取state。空闲时在 `a01952c0..52da` 取descriptor的cmd/len/payload指针并写活动cmd/len；len为1..45才调用复制依赖 `a000589c(active_payload,payload,len)`，由 `a01952c4` 的a2和 `52d4` 的a1核实。复制后 `a0195302` 重读state，仍0才置1；无论此次是否置1，都到 `a01952ec` 调starter。len不进入复制区间时原分支直接写1再启动；这里只保留原分支，不研究异常长度。

忙时扫描四个已占用槽，按cmd、len、`a00501be(descriptor.payload,slot.payload,slot.len)==0`去重；指令 `a0195224/522c/5230` 补足反编译遗漏的第三参数。去重命中或四槽全占用都直接返回，没有业务成功码。选第一空槽后 **先**写occupied=1（`5268`），再写cmd/len和可选payload复制（a2在`5270`）；不能改写为“复制完成后发布”或据此补造锁/原子保证。复制/比较函数体来源未在本轮认证，沿用既有语义合同，适配ABI仍保留。

starter保存当次state，只有值1才依次调用frame builder和write progress；返回后把保存的1写attempts、wait清0（`a00ee9f4/9f8`）。这两次写不依赖callee返回码，也发生在write可能已经置state2之后。starter不等write全完成，不返回发送成功。

构帧精确次序如下：

1. `a01a501a` 写frame_len=2；`502e: sh 0x00a5` 同时写frame[0]=A5、frame[1]=00。CRC从initial0先处理frame[1]这一个byte，再处理活动cmd起的len+2字节。
2. 初次len快照s4决定CRC低字节目的`62fcb2f5+s4`；`5056`重读len决定高字节目的`62fcb2f6+len`；`5068`再次重读len，循环计数为`(len+4)&255`。不能合并这些读取为一次永久快照。
3. 从活动cmd开始逐byte复制cmd、len、payload、CRC低/高字节；遇A5、5A、AA先加AA，原byte不做XOR。frame[1]的00已直接写好，不进入这一转义循环。输出索引每次以8位截断；正常遍历结束追加5A，并写最终frame_len。
4. 原函数仍有输出索引超过0x5e后的提前返回分支（`a01a50de..50e2`）；它不追加尾标记，也不返回显式构帧失败。这里只保留代码形状，未计算输入界限或验证该分支。不能将builder重建成“始终返回完整合法帧”。

CRC算法和正长度返回沿用既有CRC合同，没有重解表或执行原厂CRC。6条THead指令均按ROM原字核opcode/funct3/高位、寄存器与shift字段：`5052/5064/50b0/50ca/50da`是单byte store，`50b6`是无符号byte load。现有SLEIGH `ap01thead2.sinc:6442/6410` 的地址计算为`rs1+(rs2<<shift)`，本处shift=0；证据中保留模型原文，不用不支持厂商指令的Capstone输出替代语义。

## 部分write与底层边界

`a00ee96c`只看frame_len是否非0，不先检查state。存在待发字节时调用：

```c
int r = write_wrapper(load32(0x62fc91b0), frame + cursor,
                      (frame_len - cursor) & 255);
if (r <= 0) return;                       // 不推进，也不宣告完成
uint8_t next = (r + load_u8(&cursor)) & 255; // 调用后重读cursor
uint8_t length_now = load_u8(&frame_len);   // 调用后重读长度
cursor = next;
if (length_now == next) {                 // 原指令是等于，不是 >=
    state = 2;
    store_u16(&frame_len, 0);             // 同时清cursor
}
```

正返回先推进cursor，尚不相等则保留frame_len和cursor供下次推进；非正返回不改这两个字段。只有正write路径走完成比较，即便传入count为0也不能凭“游标等长”绕过返回门。此描述保留原整数宽度/比较，不分析越界或异常返回值。

一次启动会立即调用一次write；正常poll读取/解析后，环形区耗尽在 `a00a844e` 再调用write progress。该poll入口仍由a1非负、a2 bit0决定，未证明每次可写事件、发送延迟或底层调度保证；外层parser stage3分支也到同一推进点，B18已有顺序合同。因而部分write可跨调用累积，但“何时一定再次调用”是调度边界。

新增底层只读解码显示 `a0027e94(fd,buf,count)` 的正常路径：保留buf/count，调用 `a0025904(fd,&local_object)`；取得成功后调用 `a0025874(object,buf,count)`，保存结果，再调用 `a0027e54(object)`，最后原样返回保存的非负结果。句柄取得/归还函数体未恢复，因此这里只依据栈对象交接和调用顺序描述局部资源关系，不认证引用计数、阻塞或锁。原负结果路径转换为errno/-1，外层只以signed r>0判推进；没有扩展失败研究。

`a0025874`在object.flags的bit1置位、三个链接均存在时取 `object+0x0c → link+0x10 → ops+0x0c` 的函数指针，通过 `a0025890: c.jalr a4` 调用。到该间接调用时a0仍为object、a1仍为buf、a2仍为count；返回a0不被包装成“全部完成”。具体驱动write实现、其正返回是否代表队列接收/硬件发出、buf是否被同步消费、是否持有异步引用及实际可写唤醒机制未找到安装点，不宣称POSIX库来源或真实硬件交付。完整写清frame元数据本身不证明驱动已放弃frame指针。

## 匹配响应、两个通知与下一命令

沿用B18/CRC接受合同，parser在CRC匹配后先置解析stage3，再检查传输state2和接收cmd==活动cmd（`a00a84ee..8502`）。两门通过才从解码cmd起复制len+2字节至`62fcb322`，随后置传输state3。未命中这两个门的CRC正确帧不构成本次活动命令完成通知。

第一次通知ABI为 `(unsigned_byte response_cmd,unsigned_byte response_len,payload_or_NULL)`：len=0时a2=0，非0时a2=`62fcb324`；`a00a852e`加载当前handler，非NULL才调用。第一次返回后 `a00a853a` **重新加载** `62fcb6c0`，不再次判NULL，以新指针发 `(0x24,0,NULL)`。两个调用的返回寄存器都不作为业务成功条件。不能缓存第一次函数指针，不能给第二次补NULL检查，也不能在静态恢复中保证handler不被同步替换。parser随后只清解析stage（`8548`）并调starter（`854c`），没有统一清传输state或释放活动对象。

普通handler `a00a8582`在入口将cmd、len、payload保存成栈上的CommandView。`0x24`分支 `a00a8856..886e` 读取OTA阶段`62fcb2ef`：值1调用已有OTA起始边界，其他值才调用B20消费者；本轮不展开OTA路径。因此不能概括成每次0x24都无条件出队。

以已核普通cmd58为具体正常闭包：`a00a8780`先调用 `a0191652(62fcb504,4,&view)`，helper在`a0191668`清传输state0；它可能先置round_done，然后比较/复制缓存、变化时同步向当前handler发派生事件`((view.cmd+0x20)&255,0,NULL)`。caller在helper返回后读缓存条件并进入已有poll selector `a0191746`。该selector可能提交后继命令，所以在随后0x24发生前state可能已经再次忙，B20将保留队列槽。若没有后继占用且普通handler仍安装，0x24可消费一个固定槽，启动后清所选occupied，完成一次正常队列交接。

这条具体正常命令闭合了state3归还至下一命令的责任边界；不把它扩大为所有响应统一清idle。未知/不处理的普通cmd可以直接返回，parser不会替它清state3；没有handler时两通知都不发，也不能由parser自动排空队列。已知安装点只证明普通handler可被安装，不保证本次调用时一定是它。handler替换/生命周期的完整集合仍未知。

## 实际验证、恢复程度与断边

实际执行 `python -B reverse/analysis/uart-send-lifecycle-d01-0041-20261023/verify_static.py` 成功，输出 `static_checks_passed`：13个窗口458条指令，6条厂商指令原字段、38项关键操作数/间接ABI、25项直接控制流目标断言（含3组AUIPC/JALR原字段）通过；已有记录涉及的完整body原字节与主仓库ROM一致。手工核调用参数生存期、byte/halfword写宽、读取在调用前后的顺序和state写者。首次检查脚本有一个窗口起点落在指令中间，以及Capstone `addi`/provider `li`别名差异；依据原指令边界修正检查表示后通过，未改ROM或模型。验证是宿主静态解码，不是固件运行或整模块技术验收。

事实：submit不保留调用者指针；busy路径occupied先写；frame/游标宽度与重读；write完成仅state2且以相等门清两个byte；匹配响应state3后双通知；0x24普通分支和缓存helper的state0写均有原指令。推断：名称prepared/await_response/response、静态字节副本的业务所有权、取得/归还句柄的角色来自这些调用/读写关系。未知：全局并发与完整状态写者、调用者/handler重入、驱动具体合同、冷启动cursor和销毁边界；不能由静态窗口补造线程安全或成功回执。

可复用的新恢复是submit ABI、构帧临时CRC/转义次序、部分write重读与元数据归还、底层操作表ABI及正常完成的责任分配。B20槽、B18解析、CRC、dock轮询均保留既有合同；未认证任何新增标准库/开源排除。PogoPinMng/UartComm/EsUnitProtocol路径只是既有私有模块归属线索，原源码、厂商库版本和编译配置仍未认证。

明确断边：

- **底层write**：`a0025904/a0027e54`对象取得/归还内部与`object+0xc → +0x10 → +0xc`实际安装者未恢复；具体驱动是否同步消费frame仍未知。
- **状态写者**：表只覆盖本闭包；frame constructor不清cursor，冷启动/断连和全部外部state/cursor写者未证明。
- **回调ABI及寿命**：两次调用的三参数已恢复，第二次槽重读且无再次NULL门；实际handler集合、替换约束、派生事件消费者、响应指针可保存多久未认证。
- **资源归还**：原槽在starter返回后清occupied；frame在本地全写后清元数据；活动/响应缓存无释放。这些不等于驱动、handler或整模块最终销毁完成。
- **调度**：正常poll尾可继续部分write；完整事件注册/可写唤醒与真实通信时序未恢复。没有硬件执行证据。

后继建议一个独立闭包：从 `a0025904(fd,&object)`、`a0027e54(object)` 及上述操作表安装者恢复UART写对象的取得→具体write→归还，保持静态正常路径，明确buffer同步消费合同；不要扩成驱动全模块或超时调查。本报告首先应由新的独立agent技术复核。
