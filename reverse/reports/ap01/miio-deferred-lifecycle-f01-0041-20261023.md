# F01：MiIO 共享延后设置 timer 生命周期

2026-10-23；基线 `2ee39b3`，分支 `codex/re-0041-f01`。**初始化、三个已知提交、到期交接和请求清理已恢复；最终销毁与外部串行化仍为可定位断边，待独立技术复核。** 本文为分析者视图，伪代码不是原源码。只静态读取原厂 0041，没有执行固件、外连、异常重复提交实验、改 ROM、生产模型或共享 REA 状态。

## 问题与结论

共享对象 `62fc9428` 是由外层 loop 注册的常驻 RAM timer，提交者为每次操作另外分配 8 B 请求，将其放入 timer 首 word。timer 初始化函数本身**不清首 word/data**；提交时才明确写入该槽。到期分派器先停止该 timer 的活动状态，随后以 `callback(timer)` 间接调用业务回调；正常一次性任务的 repeat 为0，不走重排分支。业务回调只在入口读一次 timer.data，将请求指针保存在 s4，使用该保存指针释放请求，然后清 timer.data。

“data 重读”应分层表述：入口日志读取 req.kind 和 req.value；日志返回后又读取 **req.kind** 决定分支，既没有重新读取 timer.data，也没有在分支中重新读取 req.value。kind0..6 的业务值沿用全局槽，不能将请求建模为业务快照或队列。

真正 MiIot deinit 片段 `a005c9ea..a005ca99` 可以定位，但其中显式停止的是 `62fc9480` 和 `62fc9228`，另停止并提交关闭 `62fc9894`。本片段没有显式停止或关闭 `62fc9428`，也没有释放共享 data。不能借同一模块的 deinit 日志补造共享 timer 的最终销毁。

## 范围与证据

核心闭包为容器 `a005a736` 的初始化/循环调用/deinit 三个局部片段，`a009d106` 初始化器、`a009d146` start、`a009d286` scheduler、`a009d304` 到期分派、`a009d8bc` 整数属性相关分支、`a00a0e78` 字符串属性相关分支、`a00a0bd8` callback、`a00a5b90` 天气桥，以及 `a01b2b5c` stop 的必要接口前缀。没有恢复通用 heap 算法、所有 MiIO 属性或新增 kind2 提交检索。

- [本轮原指令与检查](../../analysis/miio-deferred-lifecycle-f01-0041-20261023/instruction-evidence.json)：14个独立原字节窗口，共1904 B，31项固定指令/直接调用核对；两个厂商指令明确保留 UNKNOWN。
- [静态核对脚本](../../analysis/miio-deferred-lifecycle-f01-0041-20261023/verify.py)：读取主仓库原件和既存保留证据，仅写本任务目录。
- [容器完整保留证据](../../analysis/factory-test-0041-20261023/retained-initializer.json)：`ev_dc0e38b0f382799ea2a8e8ad7f21cefc5998b0767ecf38a58cfdebe8add167c3`，profile `bcefdee5092076e55636e077b45523e203f4b870ae7b7ab547945ed1b8162279`；只认证本文选定片段，不将整个巨大容器视为已恢复。
- [提交/回调完整保留证据](../../analysis/miio-deferred-settings-0041-20261023/retained-functions.json)：scheduler `ev_15d25912dcae18694fd03cbf2022ff39dcdad7b267c94e4e98a8c4ad98ba4da9`，整数属性 `ev_17a8de6820bfe771a96a269aef06904915c9fd915bf3dd149e40a78307a6e1e2`，callback `ev_37aab69cd986e090eca0c8ab82e3cd2b78d6ce5806a641413fc3aa8453bb1e19`，字符串属性 `ev_28433b668abf554329ef5d090d7b391f93351bb3640eefedcc78541244401297`；profile 每项保留在本轮证据 sources。

主仓库只读 ROM 为 `D:/Documents/PlatformIO/Projects/cuktech-ap01-firmware/roms/0041/ap01-1.0.2_0041.bin`；映射基址 `9ffff000`，身份沿用上述保留来源，不另造哈希清单。既存保留记录的全部 raw ranges 本轮逐字节核对原件成功；这只认证证据绑定，不认证无关分支语义。

## 初始化和最小布局

`a005a77a` 保存外层 a0 至 s1，至 `a005ac0c` 没有重赋 s1。`a005ac04..ac0e` 构造 a1=`62fc9428`、a0=s1，调用 `a009d106(loop,timer)`。调用返回非0时 `a005ac18..ac34` 日志，零和非零路径都接到 `ac38`；不把日志分支改成提前返回。当前原件初始化器完整64 B `a009d106..a009d145` 实际恒返回0，但调用者仍保留非0检查。

初始化器明确写入：

| timer 偏移 | 访问与含义 |
| --- | --- |
| +0 | 本初始化器没有写入；后续 scheduler 写请求指针，callback 读并最终清零 |
| +4 | word loop 指针 |
| +8 | byte 13，类型数值事实；不还原未经来源认证的原枚举名 |
| +0x10/+0x14 | word 注册链节点；节点插入 loop+8/+0xc 所指链表 |
| +0x28 | word清0 |
| +0x2c | word写8；bit2后续用于活动状态，bit3与loop活动计数联动 |
| +0x30 | word清0；start 写 callback |
| +0x40/+0x44 | 两个word清0；start 写到期值 |
| +0x48/+0x4c | 两个word清0；start 写repeat低/高word |

没有由这些偏移推断完整 `sizeof(timer)`。`+0x34..+0x3c` heap 节点等内部字段仅作为既有 timer 合同，不扩展算法。请求布局为8 B：`u8 kind @+0`、未观察赋值padding `+1..3`、`u32 value @+4`。timer 是静态 RAM 对象；请求为动态分配对象，二者不可用同一个 free 表示。

原指令定位：`a009d10e: 2384f500` 为 `sb a5,8(a1)`；`a009d118` 保存loop；`a009d11a` 写标志8；`a009d130: 23a40502` 为 `sw zero,0x28(a1)`。全部写入列表可在64 B完整窗口逐项复查，未出现 `sw ...,0(a1)`。

## 三个已知属性到提交的交接

仅核接口、宽度和顺序，属性分派条件沿用[既有 MiIO 报告](miio-deferred-settings-0041-20261023.md)。

| 属性 | 提交之前 | 提交参数/地址 | 提交之后 |
| --- | --- | --- | --- |
| 整数3/1亮度 | 将完整输入s1低byte写 `62fcafc8` | `(0, input)`，`a009dacc` | 重新读PWM亮度 `62fc94e5`，调用 `a0195144(3,1,current,0)`；不等待callback |
| 整数4/1模式 | 将输入低byte写 `62fcaff2`；计算完整word `input-1`，unsigned范围仅0..3提交 | `(1,input-1)`，`a009de26` | `a01950e4(4,1,input!=0,0)`；提交返回寄存器未作为成功条件 |
| 字符串3/5位置 | 复制参数63至 `62fcaf00`，末byte `+63` 写NUL | `(3,1)`，`a00a0f32` | 对原输入strlen并 `a0195106(3,5,input,len,0)`，随后明确返回0 |

scheduler `a009d286(kind,value)` 的 ABI 为 a0/a1 两个word，kind仅保存低byte。它先 `alloc_a002fcc8(8)`；NULL直接到尾部，不给调用者统一成功状态。非NULL写 kind/value，`a009d2b4: 23249542` 将请求写至 `62fc9428`。随后 a0=timer、a1=`a00a0bd8`、a2/a3=delay低/高word=0、a4/a5=repeat低/高word=0，调用start。RV32参数对应两个64位量，不能误读成六个独立业务参数。

start `a009d146` 检查 `timer.flags & 3` 和callback非NULL，拒绝分支返回 `-22`；若已活动则先调用stop。它保存callback至 `+0x30`、repeat低/高word至 `+0x48/+0x4c`，在heap注册后置活动bit2，并按bit3调整loop计数，成功返回0。本轮只保留字段交接和返回合同；`a009d18c` 原字节 `7715aac0`、`a009d1bc` 原字节 `7716c5c0` 为通用Capstone不识别的厂商算术，未为其补造含义或修改模型。因此到期算术及heap完整算法不在本次认证中。

start返回非0：scheduler记录错误，释放自己保留的请求指针s1；本完整scheduler没有随后的data清零。返回0：scheduler不释放请求，将它留给callback。报告此原行为，不开展重复提交实验，不从它推导异常利用或新增修复。

## 到期消费、重读和释放

到期分派器 `a009d304..a009d381` 的存在让“start如何把timer交给业务callback”获得原指令连接。外层容器在 `a005c81a` 以a0=s1(loop)调用它；全loop调度只核此调用点，不重新恢复整个调度器。

`a009d314` 从loop+0x130取heap节点s1，`a009d320` 得到timer=`node-0x34`保存为s2。达到其到期判断后，`a009d336..d33c` 调 `a01b2b5c(timer)`。然后检查timer+0x30的callback是否存在以及repeat两个word。repeat非0分支另调用stop并 `start(timer,callback,repeat,repeat)`；本共享scheduler写repeat=0，所以正常到期跳过重排分支，直接到最终间接调用：

```c
// 分派器局部视图；不替代时间比较/heap实现。
timer = (Timer *)((char *)node - 0x34);
stop(timer);
if (timer->callback && (timer->repeat_lo | timer->repeat_hi)) {
    stop(timer);
    start(timer, timer->callback, timer->repeat, timer->repeat);
}
callback = timer->callback;  // a009d36a 再读，不能提前缓存跨越控制调用
callback(timer);            // a009d36e a0=s2；a009d370 c.jalr a5
```

这里最终callback读指令 `83a7c4ff` 是从node-4读取，即timer+0x30；a0原指令 `4a85`、间接调用 `8297`。不要把这个重读与业务data槽重读混为一谈。该分派器中最初callback为NULL的分支跳到最终重读位置；本任务正常提交始终给非NULL callback，不扩展其异常合同。

业务callback完整窗口 `a00a0bd8..a00a0e77` 的s4/s5只用于以下关系，跨callee按RV32保存寄存器合同保留：

```c
void deferred_callback(Timer *timer) {
    Request *saved = timer->data;           // a00a0bf0 -> s4，仅这一处读data
    Timer *saved_timer = timer;             // a00a0c08 -> s5
    log(saved->kind, saved->value);         // a00a0bfc byte / a00a0c00 word
    switch (saved->kind) {                  // a00a0c20 再读kind byte
        // 既有kind0..6合同；从全局取业务数据。
        // 各分支最终汇合到a00a0cce；本轮不重复业务分支解码。
    }
    free_a002e14e(saved);                   // a00a0cce / a00a0cd0
    saved_timer->data = NULL;               // a00a0cd4，发生在free之后
}
```

kind0亮度/蜂鸣、kind1模式、kind2/5配置与两位汇合、kind3位置、kind4城市、kind6天气重排均按原报告保留。请求value仅入口日志读取。这里不将data再取一次后free，不把清data移到free前，不将全局业务槽移入请求。

天气桥 `a00a5b90` 先stop `62fc9520`，后 `a01b24c0(1,2000)`，沿用[天气重排合同](weather-scheduling-0041-20261023.md)。**9520不是9428**；这不是业务callback停止自己的timer。共享timer的到期停止发生于上述分派器，业务callback本体只释放请求、清data。

## 控制与销毁边界

stop接口必要前缀 `a01b2b5c..a01b2bb1` 显示：不活动时直返；活动时处理timer的heap归属和 `+0x2c` bit2，若原bit3置位则减少loop+4活动计数。它不等于close/free，不据此前缀承诺请求data的释放；通用heap部分继续为已有未认证来源合同。

同容器实际MiIot deinit顺序由指令确定：

1. `a005c9ea..ca06` 输出deinit开始日志。
2. `a005ca0a..ca16`：a0=`62fc9480`，调用 `a01b2b5c`。
3. `a005ca1a..ca26`：a0=`62fc9228`，调用同stop。
4. `a005ca2a..ca36`：a0=`62fc9894`，调用 `a01b2cb0`，此处只认证控制调用和对象，内部不扩展。
5. `a005ca3a..ca44`：相同对象 `62fc9894`、a1=0，提交 `a009fb96` 关闭。
6. 两个fd槽按 `!= -1` 分别调用close接口并写回-1；最后deinit完成日志，退出容器。

对该完整局部片段，没有出现构造9428、读其data、向它传递stop/close或free其请求。这个负结果只适用于 `a005c9ea..ca99` 的显式调用与地址，未覆盖通过loop链/别名的关闭，也不证明全ROM不存在销毁。loop登记节点已可定位到timer+0x10，最终walker/close链尚未与它连上。

所有权状态为：静态timer注册到外层loop → scheduler持有新8 B请求 → 写data并start → 成功后待callback消费 → 分派器先停活动timer → callback释放保存请求 → 清data。start拒绝分支由scheduler释放请求，data残留行为如上。没有证据支持每任务独立timer、任务队列、请求独占锁、等待完成确认或deinit释放data。

## 事实、推断、未知及验证

事实：字节/word宽度、三个提交顺序、初始化不写data、callback参数及两类重读、free后清data、到期时先stop、deinit对象地址均有原指令。本轮为初始化与交接补了两个此前仅靠命名的函数合同。

推断：`+0x2c` bit2为活动状态、bit3参与引用/计数、常驻对象为事件loop timer，来自多处读写与调用的一致关系；未认证原始typedef、准确库版本和厂商修改。没有新增“未修改开源实现”排除，allocator及timer形状不足以认证来源。

未知：外部线程/调用的串行化保障，是否存在其他间接提交者，kind2/4/5/6的真实生产入口，初始化前data依赖的RAM/BSS建立，loop最终关闭如何处理9428及仍挂data的请求、最终资源归还顺序。正常到期自动停止不解决最终销毁问题；不以有界负结果声称不会销毁。

实际运行 `python reverse/analysis/miio-deferred-lifecycle-f01-0041-20261023/verify.py`：**PASS，31项检查、14窗口、1904 B；仅a009d18c/a009d1bc两个厂商指令UNKNOWN并保留原字节**。保留函数原始范围全部匹配当前只读ROM；脚本首次检查修正过手写opcode期望值及第二个stop调用的目标预期，最终依据原字段解码通过。没有编译项目、执行固件或历史回放。此为作者静态验证，不是独立验收。

后继建议一个闭包：从已证实loop注册节点timer+0x10，聚焦loop关闭/handle walker如何消费注册链及其close回调，检查是否能到达静态9428与请求data清理；不再重复kind2提交扫描或完整timer heap恢复。
