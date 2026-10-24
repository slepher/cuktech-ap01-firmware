# Q-30 / S-P45 串行 poll → 命令输出 → result 接合（0041）

状态：静态有限阶段恢复，待非作者复核；不代表完整命令执行闭合。作者 app_serial_downstream_research_01；独占分支 `codex/app-serial-downstream-research-01-20261025`，基线 `5f50102e56012e2e1e0fa8f9d8010d3c8e8214fd`。

## 范围与证据

原件为主仓 `roms/0041/ap01-1.0.2_0041.bin`，6769704 B，SHA256 `972db4c136c7ed9e24a83c07c1a7fd62040ca018b08ca285216d26b1fee3c6b9`，offset=VA−0x9ffff000。本轮只读四个新函数原窗：a00bdb74..a00bdf9b 1064 B、a00ba712..a00ba7bf 174 B、a00ba4b4..a00ba535 130 B、a00ba7c0..a00ba8b1 242 B，共1610 B。另读直接引用的字符串及 a066dbdc..a066dcdf 的13×20 B静态分发表；数据不计新增函数body。

覆盖metadata只提供extent/directcall，未当body：`reverse/analysis/whole-rom-coverage-0041-20261023-round1.json` 四精确address记录；extent证据依次 `ev_4b15b68470a1cba9bdad78ffe7a9e36360ed0508f83a81cc509f13672b71a7d5`、`ev_e20887248515230f6d237c8ef64a07bb1c18e5fc2db8336d95d0339ff6ae4097`、`ev_4208d55de46601c91eec5c79217b0287df09af276554fd6c79c5719f8d4582a8`、`ev_68dd7d29b24c05368379f8628f6129c9a3f4b2df7d192398e835f391cd19155e`。

继承而不重读body：upper-miio-b.md §a00bdf9c / §a00be238，Evidence `ev_1c9229862d23cdb4fcce7bd1ed003c575b74855b850d7da27b7b75b02af053be` / `ev_3f3593bae8df35a073c849005980f32b2b56e3da82559eaf7c9a3274bd48f260`；upper-miio-a.md §a00ba5be / §a00ba690，Evidence `ev_a2fe6528d46d540d57269d307304ea1818014153926601d33c4dacbe49b6f08f` / `ev_96e86ef902fbb22924f74283bc8b4dec2f3996f006a4c10d869866010973fdeb`。JSON doc/token API只继承同卡 §a0060cac / §a0061d20；共享error reply只继承 `app-rpc-action-research-01-0041-20261025.md` 的 error/reply/归还段。此继承不使尚未读的普通/json ACK callback body自动闭合。

原字、逐窗SHA、静态解码和引用数据见同stem analysis 的 `windows.json`、`disassembly.txt`、`referenced-data.json`；可提交 [contract.json](../../analysis/app-serial-downstream-research-01-0041-20261025/contract.json) 及提取脚本固定身份和范围。所有指令均由Capstone RV32+C解码，无未知原字。未执行任何目标/模型。

## 已有根接口

get_down 调 poll(ctx,0)，非0直接结束；仅0才进入既有network变化/自动恢复/OTA锁/缓存MQ fd分支。json_get_down 调 poll(ctx,1)，0时只写 `json_down none`，没有MQ fallback。writer ABI是 `ctx+14(ctx+4,text)`。这些旧根行为不计本轮新增。

result 与 json_ack 共用既有消费端：state=ctx+30，tick=+34，timeout=+38，result_cb=+6c，error_cb=+70。state0报error；elapsed严格大于timeout则可选error(ctx,-9999,"user ack timeout")、报error、清state；否则 result_cb(ctx,args)==0才成功，state2在callback后抑制generic ok，最终清0。此返回门只证明本层ACK被处理。

## poll 的有限阶段合同

1. **缓存输出优先**（a00bdb8e..bdc7a）。先读ctx+1fc。值2时用栈builder借用ctx+28/+2c，按mode选择 `json_down` / `down` 前缀，再从ctx+200指针与ctx+204长度调用有界长度API、raw追加、finalize，writer输出ctx+28，清+1fc，return1。值3同样追加5字节 `error` 后输出/清除/return1。其他非0值只写对应none并return1，不清该值。缓存没有在此转移或free。
2. **等待旧命令**（bdc7c..bdcdc）。state非0时，elapsed与timeout作unsigned比较。超时严格 `elapsed>timeout`，调用可空error槽(ctx,-9999,"user ack timeout")，清state，writer("error")，return1。期限内state非2也写error并return1，保持state。state2、mode1写error；state2、mode0依据+1f9/+1fa、+1f8/+1fa的门写 `down update_fw force` / `down update_fw auto` / `down update_fw`。这里只发送等待文本，不证明OTA执行。
3. **SDK取命令及门**（bdcdc..bdd78）。state0才清ctx+38起0x34 B，记tick，令D=ctx+38，D+24(ctx+5c)=ctx+74、D+20(ctx+58)=ctx+78。调用 `a011f43e(*(ctx+0)+0x968,D)`；非0才改用 `*(ctx+0)+0x174`。任一路0进入日志/ctx+48门：+48==0进入命令处理，+48!=0进入下述+88门。两路均非0也进入+88门，不能把非0解释为有效dequeue。
4. **+88等待门**（bdd34..bdd68、bdf98）。ctx+88==0直接return0，因此根可继续network/MQ或json none；非0建立timeout=6000、新tick、result_cb=a00ba9f6、error_cb=a00ba994、state2，然后复用上述等待文本输出并return1。+88的生产者/含义本轮未读，只记录实际偏移门。
5. **mode1输出**（bdd78、bdf5a..bdf54）。P=ctx+5c，N=ctx+58；直接调 a00ba4b4(ctx,0,0,P,N)，不先解析method/params。helper成功返回0后才state=1，return1。失败则进入state2等待安装路径。这里N只作为raw追加API长度；无本层NUL或容量预检查。
6. **mode0解析/分派**（bdd84..bdf58）。栈JsonDoc初始化为(P,N,其余0)，parse非0转state2等待；成功lookup("method",type3)、lookup("params",type0)。method是输入片段及end-start长度；params同样为片段，若type3则指针退1、长度加2以保留双引号。成功parse后均调用doc cleanup；cleanup在使用这些输入片段之前，但它们指向P，非token vector。
7. **缺字段及表匹配**。method或params缺失将相应长度置0并记录日志；cleanup后method指针、params指针或method长度为0转等待。params长度不作非0门。按13个20 B表项逐一比strlen(method_name)==method_len及memcmp==0，选entry+8 handler；null handler转等待。未匹配用a00ba7c0。handler ABI `(ctx,method_ptr,method_len,params_ptr,params_len)`；返回0才state1/return1，非0转等待。表含action/action_v3、ddf_discovery_v3、get/set_properties及v3、get/set_property_report_config_v3、subscribe/unsubscribe events/properties_v3；只恢复本层路由，不展开各handler。

helper非0的根含义是“本轮poll已有响应/等待处理”，不是设备执行成功。state1写入发生在handler返回后；handler内部writer调用发生在此之前。本层未加重入锁，不能据串行命名推并发安全。

## 两个输出适配器

|适配器|同步构造与门|成功安装与返回|
|---|---|---|
|a00ba4b4，mode1|栈descriptor借ctx+28/+2c，计数0；调用a01a5268(desc,"json_down")，a00b5636(desc,P,N)，a018fd68(desc)。不解析输入|finalize==0才安装+6c=a00bda7c、+70=a00bd910，再writer(ctx+4,ctx+28)，return0；finalize非0 return−1，不写槽/不writer|
|a00ba7c0，mode0默认|前缀"down"，a00b55e2追加method片段；另建栈doc解析params。parse失败直接finalize；parse成功lookup零路径取root，type2且end-start>2时去两侧方括号追加内部，否则追加完整原params；成功parse路径cleanup|finalize==0才安装+6c=a00bd938、+70=a00bd7fa，writer后return0；非0 return−1|

空数组长度2走“不追加内容”分支（直接cleanup），非数组/无root走追加原params；数组长度>2才去括号。builder API内部的分隔符、转义、溢出/截断保证未读，不把调用序列冒充逐字输出保证。a01a5268在这些调用点接收builder与前缀字符串；本轮不据其名字赋予SDK回包/copy语义。

## result 接合与消息持有

有限路径是：SDK API写D → 两mode适配/业务handler → 输出到writer → state1 → 旧result/json_ack消费state/tick/timeout → 间接result/error槽。mode0默认error目标a00bd7fa可继承旧共享error合同：用ctx+74和min(unsigned ctx+78,0x558)构造id/error，成功后以40 B栈descriptor（+0=id ctx+3c、+1c=有界输出长度、+20=ctx+74）调用 `(*(ctx+64))(&descriptor,*(ctx+68))`，结果原样返回。SDK dequeued D的+2c/+30即ctx+64/+68，因此是同D的reply/context槽接合，而不是凭名称猜copy。

mode1 result=a00bda7c/error=a00bd910及mode0默认result=a00bd938的具体ACK转换、调用reply条件/返回值仍是本包四窗外的API断边；等待state2的a00ba9f6/a00ba994同理。未读其body，未宣称这些路径已到真实SDK接收。旧result消费者负责清state；本轮适配器不清reply/context/result/error槽、不释放SDK消息。

|对象|本层已证持有/归还|未证保证|
|---|---|---|
|SDK写入的D=ctx+38|清52 B后传给两个dequeue API；回包槽/输入片段保持在ctx中，输出后未显式release|SDK是否copy/接管原消息、失败时填充、下一poll覆盖、释放/取消协议|
|P=ctx+5c,N=ctx+58|本层只借用；method/params均指向P；doc cleanup后仍同步消费P；无free(P)|SDK与ctx+74共享缓冲是否别名、后续ACK时保活|
|栈builder descriptor|仅在a01a5268/append/finalize调用期间存在；writer传的是ctx+28|这些API是否保留descriptor或引用，不从异步名判断|
|ctx scratch +28/+2c与+74/+78|前者用于串行输出，后者作为dequeue默认缓冲及旧共享error输出；未本地free|二者别名/并发覆盖、完整ctx销毁|
|栈JsonDoc/token vector|parse成功后调用a01b38b6；切片借P而不是token；parse失败沿旧API错误合同|parser/allocator内部失败细节与恶意输入保证|
|旧reply的40 B栈descriptor|共享error只在间接reply调用期间有效|reply深copy或异步接管，真实传输/设备执行|

## 仅get_down的 MQ fallback

a00ba712(out,cap)借caller输出缓冲，栈上0x140 B消息先整体清零（首4 B单独清零，其余0x13c memset）。读全局fd=*(0x62fc4dd8)，−1时return−1（日志受级别门），不打开/关闭；根负责缓存fd。调用a01990c8(fd,&stack_msg,0x140)，仅返回−1视失败；其他返回值，包括0或短读，都调用格式API a002d7fc(out,cap,"down %s",&stack_msg)，然后return0。消息按NUL文本参数传入；满长非NUL数据的安全性不能由预清零证明，read/formatter止API。本层未分配/释放队列消息，无type/id/ACK结构，也不建立state/result槽。根在return0时输出out，失败时输出down none；json_get_down没有此分支。

## 检查与停止边界

已核原件长度/SHA、四extent与总1610 B、逐窗offset/SHA、完整解码步进及0未知指令、所有direct-call/条件跳转、13表项及直接字符串、回调目标算术、报告引用与精确输出范围。脚本只读取ROM、写独占analysis，不执行目标或模型；未运行SIM/QEMU、回放、构建、设备、外网。没有生产、ROM、配置、分析器或共享REA变更。

重叠检查：旧get_down/json_get_down和result/json_ack只继承；业务action/property/subscription handler仅表目标，不重读；新增函数仅四窗。仍未闭：三个普通/json result/error目标的ACK转换、等待state2 callbacks、SDK消息完整生命周期、真实reply复制/接收、clock wrap、全ctx并发/销毁、实际MCU执行。后继只能以这些精确API目标/生产者为种子，需单独授权差集；本包不为了补时进入SDK/MQ/parser/formatter内部。

技术/必要检查 UTC 2026-10-24 18:14:23→18:18:39，共256秒（4分16秒）。提交/停止终点分列在交付消息；墙钟含正常工具时间，不等于有效计算工时。无额外排队/人为等待；token遥测不可得，不造数。预测7–11分钟为派发估计，实际以clock为准，提前闭合立即交。
