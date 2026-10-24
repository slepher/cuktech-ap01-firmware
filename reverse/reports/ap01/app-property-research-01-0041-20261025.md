# Q-15：typed 属性收集与延后消费阶段（0041）

状态：作者静态恢复，待非作者复核。给定有效 count 的收集→延后消费→发送 API 阶段可独立使用；count 初始化/复位、并发、共享 buffer 生命周期及云端送达未闭，不能标全事务闭合。

## 范围、查重及原件

基线 `7f7c37a6a0fd7f8de91cc57e34b79639c2cea496`，分支 `codex/app-property-research-01-20261025`。独占报告及同 stem analysis，不改主树管理表。遵从主树 reverse-design 3.1/3.2/5.1/7 和 Q-15 当前合同。

原件为主树 `roms/0041/ap01-1.0.2_0041.bin`，6,769,704 B，沿既有 SHA256 `972db4c136c7ed9e24a83c07c1a7fd62040ca018b08ca285216d26b1fee3c6b9`；file_offset=VA−`0x9ffff000`。本轮检查文件长度，不重算全 ROM 摘要。只读取指定旧留存及必要原字，没有运行固件、模拟器、构建、设备或网络，也没有切换共享 REA。

有限查重：主树 reports 中精确入口/共享 count，以及旧 `upper-miio-a.md`、`upper-miio-b.md`、`upper-routing.md` 的本入口词项无本体合同命中；这是本次载体/词项范围，不是全历史负证明。旧 deferred/F01/Q11 caller 参数按派发前提继承，未重新恢复其链。旧库 formatter/copy/queue 内部有公开替代，本次止 API，不认证库来源或版本。

## Evidence 与复验

以下均为主树 `evidence/rea-0041-20261017/evidence/` 中既有 JSON 的 `/structuredContent/normalized_result`；不是本轮新 REA 导出：

|记录|真 body|Evidence ID|
|---|---|---|
|whole-rom-private-20261023-144.json|a0195034..a01950e3，176 B|ev_89e3ae9d1a09935389925ac12a464c788cae672e9b1631dccf95d099355d501f|
|whole-rom-private-20261023-159.json|a01b5d70..a01b606b，764 B|ev_d130f16f50acaa43d7f20c98370e94baef9d75355aea1e27d2af68d7ebee7db2|
|whole-rom-private-20261023-021.json|a00a116e..a00a12cf，354 B|ev_e56e7bf85b43acfb10c1c6065be0dd6f8d6ff82cbb1c1c92f3665a396e97610e|
|whole-rom-private-20261023-024.json|a00a2578 GET/SET 两处 consumer(0)，只抽上下文|ev_c1e4264fde90a17127f8044f76f1c829bac816668b38d62f57229fdc852b638c|

profile 沿 Ghidra12.1.4、`RISCV:LE:32:ap01thead2`、历史 private profile；完整 profile 原样保存在 bounded-evidence。反编译只作辅助，字段/宽度/分支以留存 assembly 和本轮指定原字为准。四 wrapper 原有 extent/direct-call 证据只有入口边，新增只取其130 B原字，用本地 Capstone 解普通 RV32/RVC 指令，检查解码完整、每个唯一 jal 目标 a0195034。这不验证整个私有指令模型。

复验脚本 [verify.py](../../analysis/app-property-research-01-0041-20261025/verify.py) 从绝对主树路径读取源，输出同目录 ignored `bounded-evidence.json.tmp`：三份完整必要 assembly/pseudocode、1,294 B继承 body 原字、130 B新增 wrapper、16个必要NUL字符串窗、024局部上下文。原字含 offset、hex、逐窗SHA；未泛搜 ROM。分析结果不含目标执行。

## 收集 ABI 与槽布局

`a0195034(id0,id1,type,value_ptr,extent,include_value)` 的六个 RV32 参数依次为 a0..a5。`count=u32@62fcb044` 通过 signed `bge 19,count` 进入写入；本合同要求 `0<=count<=20`。count≥20时只日志返回，不写槽、不递增；负值并没有下界防护，不能据此证明任意输入安全。函数没有可用成功返回合同。

槽 `S=62fcb048+count*0x20`，**stride0x20=32 B**，collector 的 `slli5` 与 consumer 的 `+0x20` 一致。派发中裸写 stride20 应按十六进制理解，非十进制20；这属于转述澄清。

|S偏移|写入/消费|
|---|---|
|+0/+4|id0/id1，各word；序列化 `%u %u`|
|+8|collector写零halfword；mode0消费用 `lh`，故是有符号16位状态码|
|+0xa|type低byte；collector分支比较使用原完整type参数|
|+0x10|type3读取/复制2 B，type4复制4 B，type1/2复制1 B；其它类型保存value_ptr word|
|+0x14|本collector不写；type5/9消费会读取，与本轮四wrapper无闭合构造链|
|+0x18|extent word；type0消费仅检查非零，不按此长度截断字符串|
|+0x1c|include_value低byte；消费只测零/非零|

所有字段写入后 `a01950ca..cc` 将count加1并存回；没有清理padding。类型比较为完整寄存器、存储为byte，故超出已知有限type的输入不能只按低byte等价替换。

|wrapper范围/长度|输入→collector|
|---|---|
|a01950e4..5105 /34 B|`(id0,id1,value,flag)`：低byte栈临时，type1、extent1、a5=flag；立即复制1 B|
|a0195106..5121 /28 B|`(id0,id1,ptr,len,flag)`：type0、value_ptr=ptr、extent=len、a5=flag；保存指针|
|a0195122..5143 /34 B|`(id0,id1,value,flag)`：word栈临时，type4、extent4、a5=flag；立即复制4 B|
|a0195144..5165 /34 B|`(id0,id1,value,flag)`：低byte栈临时，type2、extent1、a5=flag；立即复制1 B|

数值wrapper栈临时不会被保存为悬空指针，collector在wrapper返回前复制到S+0x10。string wrapper没有深拷贝或归还：有效指针及NUL串须持续至延后消费者格式化结束，len不是拷贝长度。flag=0仅生成id/status前缀，flag=1包含value；任意其它非零byte在本consumer同样包含。flag并非wrapper固定常量。

## 延后消费合同

`a01b5d70(mode)` 初次signed count<=0即返回；mode0把共享 `B=62fda0a8` 初始化为 `result`，非零初始化为 `properties_changed`。因此mode1只是常见非零形式，本体不限定只收0/1。024的GET/SET两条路径确实调用consumer(0)；GET前 a00a12d0(0)仅记锚点，截断证据不用于推断复位owner。

循环每次 `a01b5dd8` **重读count**，当 i>=count 或 i==20停止；不是一次snapshot。故只能承诺最多20次消费，不能承诺与生产并发下固定批次。每槽先追加 ` %u %u %d`（mode0，状态signed16）或 ` %u %u`（非零）。include_value=0跳过value，仍推进槽。

include_value非零时：type0在ptr和extent均非零时用 ` "%s"`，否则 ` ""`；type1从byte判真假并用 `%s` 输出布尔文本；type2/3/4按unsigned byte/halfword/word输出 `%u`；type6/7/8按signed byte/halfword/word输出 `%d`；type5/9读取两个word并传 `%llu`/`%lld`；其它type输出 ` invalid`。此消费覆盖不代表collector为type5..9正确构造了数值，其默认分支只写指针word，禁止外推64位typed wrapper。

输出门准确保留：每槽前 `R=0x201-strlen(B)`，signed R<=0日志早退；前缀在64 B栈缓冲format后测strlen，若prefix_len>=R日志早退。value也在同栈缓冲format，但若value_len>=`0x201-strlen(B)`，**仅不追加value而继续下一槽**，不会返回错误。未检查formatter返回，不能假设长字符串完整输出或据len保持串边界。最终 `strlen(B)<=0x200` 才日志并调用send(B)，超出只日志返回。这里0x201为513、0x200为512，均是代码中的数值门，不证明共享buffer实际分配容量。

send在 `a01b6054` 的返回被忽略；consumer没有额外append终结符/关闭JSON，也没有重置count或归还string的本体写端。格式是命令文本，由本轮原字字符串确认，不把它当JSON消息。

## 正常发送 API 与返回

`a00a116e(message)` 首先strlen，零长度返回-1；没有NULL门。队列handle `word@62fc400c==-1` 返回-1。正常路径在本函数栈 `s0-0x124` 用 `format(dst,0x101,"%s%c",message,13)`，即附CR；formatter返回按unsigned必须<=0x100（256），否则日志返回-1。按常规snprintf合同，原message长度255可连CR通过，256会被门拒绝；这是公开API替代推论，原厂formatter内部未恢复/认证。

通过门后 `a00a1252..5c` 调 `a0199064(reloaded_queue_handle, stack_buffer, formatted_length)`。返回-1记录errno并返回-1；其余值被视为提交成功，随后对message与`get_down`前8 B比较来决定是否日志，最终返回0。没有要求队列API返回等于请求长度。此处止队列API，不证明消息进入无线链路或云端接收。

message只在同步调用内用于format/比较/日志，没有把原共享B指针交给队列，也没有free；队列API得到的是函数内栈缓冲和长度，其复制/后续持有由队列API外部合同承担，本轮不展开。caller自己仍持有B，send不清count、不free槽字符串、不转移字符串所有权；正常/失败出口均恢复栈寄存器。未见本体allocator，因此不存在本轮可证的堆归还步骤。

## 验收边界与交付

已恢复：四wrapper实际type/宽度与直接目标、有限类型/flag、20槽门与递增、数值复制/string借用、consumer重读count/最多20、signed16状态、mode0/非零、长度早退和value省略差异、send参数及0/-1返回门。以上为静态观察；真实执行结果未知。

未闭：count初始化/复位写端及owner、其它状态码写端、并发/批次隔离、B容量与跨调用生命周期、string在延后消费前的有效性、队列内部复制/完成/失败/取消、端到端发送。144/159/021实际写端只有collector增count，后两者没有清count；这不证明全ROM没有复位，不做全局负搜，也不依据022截断/旧extent猜a00a12d0语义。

作者检查：脚本完整跑通、四wrapper解码覆盖130 B且唯一jal均指向collector；三个body identity/长度与留存一致；原字与必要字符串已留存；提交前检查diff/忽略规则。没有独立技术验收。下一步非作者只需围绕本阶段字段、借用、长度门、send边界复核；完整事务须另有count复位及生命周期真body种子后再定义，不展开跨owner。

计时：UTC开始2026-10-24 17:08:06（首工具时钟），报告检查完成17:11:16，190秒；commit交付结束另见父窗记录。预测6–11分钟，中低置信；wrapper1–2、收集消费3–5、send1–2、交付1–2，沿派发约1 KB齐材240秒校准。材料已定位、普通wrapper可直接静态解码，实际短于预测，不补时；此数据供后续校准。未提供token/有效工时统计，不造数。无主动等待/中断，工具耗时包含在墙钟内。
