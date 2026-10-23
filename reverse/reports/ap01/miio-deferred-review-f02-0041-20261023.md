# F02：MiIO 共享延后设置 timer 生命周期独立复核

2026-10-23；基线 `4a897eecbafb15f94d8e2fe49d1e6772fdd3287d`，分支 `codex/re-0041-f02`。复核者为新 agent，非 F01 作者。**限定接受 F01 的初始化、三个提交、请求交接、分派调用与请求清理合同；未发现需纠正的业务语义。** 两条厂商算术、完整 heap 算法、loop 最终关闭和外部串行化继续未核，不能将这一接受解释为全 timer 或全 MiIO 已恢复。

本文伪代码为分析者表达，不是原源码。仅静态读取原厂 ROM 与既存 REA 保留记录；没有执行固件、历史回放、异常重复提交实验、外连、修改 ROM/生产代码/分析器模型、打开或切换共享 REA 会话。

## 独立方法与证据边界

没有运行 F01 的验证脚本作为独立验收。新写 [review.py](../../analysis/miio-deferred-review-f02-0041-20261023/review.py)，直接读取主仓库原件 `D:/Documents/PlatformIO/Projects/cuktech-ap01-firmware/roms/0041/ap01-1.0.2_0041.bin`，按既存映射 `VA - 0x9ffff000` 重新取字节，使用 Capstone 5.0.7 解码 RV32/RVC，并独立按 JAL、AUIPC/JALR 位域计算直接调用目标。脚本不读取 F01 的 instruction-evidence.json 生成自己的结果，也不使用 F01 的 opcode 检查表。

[independent-evidence.json](../../analysis/miio-deferred-review-f02-0041-20261023/independent-evidence.json) 留存 16 个原字节窗口与逐指令解码、84 项寄存器/字段/调用检查，以及完整初始化器写集、callback 请求读取集、外层 s1 写集和 callback 局部 CFG 验证。窗口含 `a005a736..a005ac37` 完整前缀，以从原件独立核实 loop 参数保存；这不是恢复整个大容器。另补 F01 检查窗口以外的整数分派常量和 `a01b2cae` 非活动 stop 返回点。

既存 REA 来源仅用于函数边界、已恢复业务接口与来源追溯；其 raw_ranges 本轮重新对照当前 ROM 全部匹配，不以其反编译结果代替字节核验：

| 来源 | 保留 Evidence ID / profile |
| --- | --- |
| factory-test retained-initializer | `ev_dc0e38b0f382799ea2a8e8ad7f21cefc5998b0767ecf38a58cfdebe8add167c3` / `bcefdee5092076e55636e077b45523e203f4b870ae7b7ab547945ed1b8162279` |
| MiIO scheduler | `ev_15d25912dcae18694fd03cbf2022ff39dcdad7b267c94e4e98a8c4ad98ba4da9` |
| MiIO integer setter | `ev_17a8de6820bfe771a96a269aef06904915c9fd915bf3dd149e40a78307a6e1e2` |
| MiIO callback | `ev_37aab69cd986e090eca0c8ab82e3cd2b78d6ce5806a641413fc3aa8453bb1e19` |
| MiIO string setter | `ev_28433b668abf554329ef5d090d7b391f93351bb3640eefedcc78541244401297` |

后四项各自 profile digest 与来源相对路径在独立 evidence 的 sources 中完整留存。没有新增 ROM 哈希清单或复制原件。既存私有 REA profile 的语言/命名不是上游库来源证明，本轮未改该 profile。

## 逐项验收

| 合同 / 问题 | 结论 | 独立依据与接受限制 |
| --- | --- | --- |
| `a005a736` 局部初始化：loop 与 `62fc9428` | 接受 | `a005a77a` 保存外层 a0 至 s1；新解码完整前缀只有该处重赋 s1。`a005ac04..ac0e` 传 a0=s1、a1=9428 至 init。非0分支仅记录日志再汇合，未被伪写为提前返回。大容器其余功能未核。 |
| `a009d106`：初始化且不清 data | 接受 | 完整64 B 无调用、无 UNKNOWN；11条以 a1 为基址的写，均非偏移0。类型是 byte13，loop/链表/flags/callback/time/repeat 是 word 写。明确返回0。不能据此认证初始化前 BSS/data 状态。 |
| `a009d146`：start 入参、字段与返回 | 限定接受 | delay 两 word 从 a2/a3 保存至 s4/s5，repeat 从 a4/a5 至 s6/s7，callback从a1至s3；callback与repeat原样存回；检查拒绝路径返回-22，成功路径0；已活动先stop。到期值算术/序号生成两处 UNKNOWN 未核，不接受这些算术已正确还原或有认证库来源。 |
| `a009d286`：8 B 分配、写 data、启动 | 接受 | `alloc(8)`，kind `sb`、value `sw`；非NULL后将保存请求写9428。a2/a3/a4/a5均0，a1构造为a00a0bd8，a0为9428。成功留给callback；失败日志后free保存指针，完整尾部没有清data。NULL直接返回，无统一成功返回合同。 |
| `a009d8bc` 的亮度提交片段 | 接受 | `a009dac8` 先byte写afc8；a0=0、a1=s1完整word，调用scheduler；随后重新读94e5调用属性通知。没有等待callback或检查提交结果。只核该分派接口，未复核整个整数属性函数。 |
| 同函数模式提交片段 | 接受 | `a009d910` 的a5=3沿分派到`a009dd22`再到de14，没有中间调用覆盖；de18先写aff2低byte，de1c完整word减1，de20用unsigned比较，只有结果0..3调用scheduler(1,result)，之后按input!=0通知。 |
| `a00a0e78` 的位置提交片段 | 接受 | `a00a0f10..f4a` 的63长度复制调用、显式末byte NUL、scheduler(3,1)、对原input长度/指针通知和最终返回0顺序成立。copy/strlen内部依既有合同，没有认证其上游实现。 |
| `a009d304`：到期stop、repeat与间接callback | 接受字段/控制交接 | loop+130取node，timer=node-34；无符号高/低word到期比较通过后先stop。repeat两个word按OR测试，为0直达最后callback读取；`d36a`重读timer+30，a0=timer，`d370 c.jalr a5`。该函数不写data。到期字段如何计算仍受start UNKNOWN限制。 |
| `a00a0bd8`：data/kind/value重读与清理 | 接受 | 完整callback中，data仅bf0读入s4；请求访问仅bfc kind、c00 value、c20 kind。s4/s5局部不被业务分支重赋；cce传s4，cd0调用free，cd4才向s5+0写0。局部所有分支在外部callee正常返回前提下汇合清理，无第二次取data或value。 |
| `a00a5b90`：天气桥对象 | 接受 | stop对象为`62fc9520`，随后`a01b24c0(1,2000)`；kind6在d48调用此桥。9520与共享9428不同；不把天气stop写成callback停止自身timer。天气调度内部保留既有合同。 |
| `a01b2b5c`：stop必要接口 | 限定接受 | 前缀读flags bit2，清bit2且按bit3减少loop+4；非活动分支目的`a01b2cae`原字节8280确为ret。活动heap分支超出此前缀，未恢复完整算法。stop不自动等于close或free请求。 |
| `a005c9ea..ca99`：deinit显式对象 | 接受有界负结果 | 直接stop9480、stop9228、控制9894后以a1=0交关闭接口，两个fd条件关闭。没有显式把9428/data交stop/close/free。只接受该局部显式流，不接受“全ROM无销毁”或“loop关闭一定释放data”。 |

纠正项：无。未核项不是自动接受；特别是厂商算术、heap内部和最终关闭仍须作为断边保留。

## 关键字节、ABI 与最小布局

足以区分最容易混淆的交接证据如下；更多字节与相邻指令见独立 evidence：

| 地址 | 原字节 | 原件语义 |
| --- | --- | --- |
| a009d10e | `2384f500` | `sb a5,8(a1)`，类型写是byte |
| a009d130 | `23a40502` | `sw zero,0x28(a1)`，不能误读为清data |
| a009d2a6 | `23002501` | `sb s2,0(a0)`，请求kind仅低byte |
| a009d2aa | `4cc1` | `c.sw a1,4(a0)`，value为word |
| a009d2b4 | `23249542` | `sw s1,0x428(a0)`，a0基址62fc9000，写9428 |
| a00a0bf0 | `032a0500` | `lw s4,0(a0)`，唯一timer.data读取 |
| a00a0bfc / a00a0c20 | `83470a00` | 两次`lbu a5,0(s4)`，是kind重读 |
| a00a0c00 | `03284a00` | `lw a6,4(s4)`，value只给入口日志 |
| a009d36a / d36e / d370 | `83a7c4ff` / `4a85` / `8297` | `lw a5,-4(s1)` / `a0=s2` / `c.jalr a5`，callback重读与首参 |
| a00a0cce / cd0 / cd4 | `5285` / `efd0e8c7` / `23a00a00` | `a0=s4` / direct free_a002e14e / `sw zero,0(s5)` |

请求最小布局：`u8 kind @0; padding @1..3; u32 value @4`，分配长度8。padding未观察赋值，不能编造初始化值。请求存的value与全局业务槽不构成快照：三个setter先更新全局，callback保留已验收kind业务接口并从相应全局槽消费。

timer最小使用布局：`data word @0`，`loop word @4`，`type byte @8`，注册链word @10/@14，word @28，flags word @2c，callback word @30，heap节点从34开始，到期低/高word @40/@44，repeat低/高word @48/@4c。地址均为十六进制偏移，不推断完整sizeof、原始typedef或准确库版本。start还写50/54的序号相关word；其数值来历未认证。

双word宽度来自caller寄存器设置、start保存及成对存储、dispatcher高/低word读取与无符号比较的一致关系。可用`start(timer, callback, delay64, repeat64)`表达二个64位量；这是恢复的机器合同，不能据此认证原源码参数名、原typedef或厂商算术。不能将a2/a3与a4/a5写成四个独立业务参数，亦不能忽略高word。

## 正常一次提交的伪代码与所有权

```c
// 机器合同表达；alloc/free内部、kind分支与heap沿用明确边界。
init(loop, &shared_9428);         // 不写shared.data

submit(kind_word, value_word) {
    Request *p = alloc(8);
    if (p == NULL) return;       // 不承诺返回状态
    p->kind = (u8)kind_word;
    p->value = value_word;
    shared_9428.data = p;
    rc = start(&shared_9428, deferred_callback, 0ULL, 0ULL);
    if (rc != 0) { log_error(rc); free(p); }
    // 上述失败路径原件没有清data；此处不修正原行为。
}

// 仅已到期且正常提交的一次性路径；不代替时间计算或heap。
timer = heap_node - 0x34;
stop(timer);
if (timer->callback && (timer->repeat_lo | timer->repeat_hi)) {
    stop(timer);
    start(timer, timer->callback, timer->repeat, timer->repeat);
}
cb = timer->callback;            // 最后间接调用之前再读
cb(timer);                      // a0为timer，未观察第二业务参数

deferred_callback(Timer *t) {
    Request *saved = t->data;    // 只读一次data
    log(saved->kind, saved->value);
    dispatch_existing_kind(saved->kind);  // 日志之后再读kind
    free(saved);                // 保存的请求指针
    t->data = 0;                // free之后；不是在free前清
}
```

静态timer对象9428由外层loop登记，动态请求另分配。提交者在start成功前保留请求引用，成功后清理责任由callback承担；分派器先停止活动状态，业务callback消费既有kind分支后free请求，再清data。这个责任转移是由路径与调用推断的所有权模型，未认证为原语言所有权类型，也未证明外部串行化。正常一次性路径不需要repeat重排；没有据此证明start时间算术或最终一定执行到callback。

局部callback CFG检查只枚举原指令分支边和共同清理点，不执行固件，不执行kind路径。所有外部调用被作为正常返回合同处理；它不能证明callee终止、并发安全或运行时结果。业务kind0..6内部仅核入口/汇合、kind6桥接、请求访问与清理，不重复已恢复业务算法。

## UNKNOWN、未认证来源与剩余断边

`a009d18c`=`7715aac0` 位于loop+140/+144读出、到期比较/存+40/+44之前；`a009d1bc`=`7716c5c0` 位于loop+138/+13c读取、常量1/0设置与回写之间。两处在本轮通用解码器均为UNKNOWN。观察到输入/输出附近的双word数据流，不等于已证明加法、进位、饱和或序号更新语义；不根据反编译伪码补齐。这阻止认证deadline形成与顺序数值结果，进而不能从delay=0断言真实时刻的调度结果；已知寄存器入参、callback/repeat存储、分派控制顺序和data清理不依赖为这两字节指派算术意义。

timer结构、活动flag和函数形状支持“事件loop timer”解释；没有上游源码/版本认证，不静默排除通用库部分。allocator/free、copy/strlen和已验收天气重排在本轮均是明确边界合同，未重新认证其内部、库版本或线程行为。

剩余断边：初始化前data来自什么RAM建立过程；外部线程/调用的串行化；其他间接提交及kind2/4/5/6实际生产入口；完整heap；注册链在loop最终关闭时如何访问9428、是否提交close callback以及谁释放仍挂data的请求。此次deinit有界负结果不覆盖通过loop或别名的关闭，stop也不证明最终资源归还。

后继只建议一个闭包：由已核实的9428注册链`timer+10/+14`追至loop关闭/handle walker/close callback，明确到达9428与data清理的证据或断边；不回头扩全MiIO、通用heap或重复kind提交扫描。

## 实际静态验证

执行 `python reverse/analysis/miio-deferred-review-f02-0041-20261023/review.py`：**PASS，84项指令/调用检查、16字节窗口；初始化写集、请求读取集、s1与s4/s5局部保存关系、完整callback局部分支到共同清理检查通过；仅上述两处UNKNOWN。** 最初手写初始化目标写数误填10，依据完整解码列出的11条改为11后通过，未改变ROM或模型。既存5份函数记录的raw_ranges全部匹配原件。没有编译项目或运行历史回放。

结论为F01小闭包的限定独立验收；最终销毁、未知算术和来源认证仍开放，不能提升为全模块完成。
