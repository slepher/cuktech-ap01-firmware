# F04：F03 条件关闭链与退出断边独立复核

2026-10-23；基线 `48af5ae2203304f254cf5f3f42eb6113ed3942d8`，分支 `codex/re-0041-f04`。新 agent 独立复核，**限定接受 F03，未发现业务语义纠正**。type13 的条件 close→stop→pending→完成摘链→关闭 callback 成立；它不能证明共享 timer `62fc9428` 在真实退出中被关闭或仍挂请求被归还。实际 close、退出后的 pending 消费机会、`obj+0x2b8` callback 安装者三条断边继续开放。

仅静态读取原厂0041及既存保留证据，未执行固件、历史回放、异常输入、外连或修改ROM/生产代码/分析器模型。没有打开或切换共享REA。伪代码是分析表达，不是原源码。范围为注册、type13关闭/入队/完成/摘链、容器必要片段、caller与返回后对象清理片段，约九个核心身份；stop完整heap与obj callback身份不在本轮。

## 独立证据与实际验证

新写 [review.py](../../analysis/miio-loop-close-review-f04-0041-20261023/review.py)，直接从 `D:/Documents/PlatformIO/Projects/cuktech-ap01-firmware/roms/0041/ap01-1.0.2_0041.bin` 按 `VA-0x9ffff000` 取字节；没有运行F03脚本，没有从其instruction-evidence生成结果。Capstone 5.0.7重新解码，JAL、branch和AUIPC/JALR直接目标另按立即数位域求值。

[independent-evidence.json](../../analysis/miio-loop-close-review-f04-0041-20261023/independent-evidence.json) 保存21窗口2020 B原字节/指令、83项核对及初始化完整写集。本轮补全caller `a005cc1e..cf05`，包括0x400栈帧建立与返回；完整读取 `a0081554..1645`，不只复用间接call三条指令。选定窗口全部可按普通RV32/RVC解码，没有新增UNKNOWN厂商字；F02 start中两条厂商算术仍未核，不提升为时间算法已认证。

REA保留来源：[retained-initializer.json](../../analysis/factory-test-0041-20261023/retained-initializer.json)，Evidence `ev_dc0e38b0f382799ea2a8e8ad7f21cefc5998b0767ecf38a58cfdebe8add167c3`，profile `bcefdee5092076e55636e077b45523e203f4b870ae7b7ab547945ed1b8162279`。全部raw_ranges与原ROM逐字节匹配。该来源给出caller线索；具体ABI和调用目标用新原字节核，不把caller列表当间接调用全集。F01/F02的业务请求及stop合同仅接口复核。

实际执行 `python reverse/analysis/miio-loop-close-review-f04-0041-20261023/review.py`：**PASS 83 checks，21 windows，2020 bytes；保留容器raw_ranges匹配；type13 & mask结果为0x2000。** 无目标代码执行或项目编译。提交前另运行git diff --check及独占路径状态核对。

## 逐项裁定

| F03合同 | 裁定 | 原指令依据与边界 |
| --- | --- | --- |
| `a009d106(loop,timer)`登记 | 接受 | `d10e` byte写type13，`d118` word写loop；`d11c..d128`将timer+10/+14插入loop+8哨兵双链尾。完整11项timer写入没有+0或+c；不能据此假定data或close_cb初值。返回a0=0。 |
| `a009fb96(h,cb)`关闭入口 | 接受 | flags低2位为0正常分支：`fbc2/c6` word写bit0，`fbc8`读取byte type，`fbcc` word写cb到+c，`fbd0`保存h。非正常前置的assert路径不展开。 |
| type13 stop→入队 | 接受 | `fc50` branch目标fd94；`fd94/98`成对调用a01b2b5c，a0沿该分派路径仍是h；`fd9c`回fcde，重取a0=s2再调用a009c228。stop沿F02必要接口，不代替free。 |
| pending单链字段/次序 | 接受 | `c256`从h+4取loop，`c258`读取loop+d4，`c25c`先写h+28，`c25e`再写loop+d4。正常前置bit0=1、bit1=0。与+10/+14注册双链不同。 |
| type13完成选择 | 接受 | a009f524先正常前置检查，再word写bit1；`f582`计算1<<type，`f586/88`构成0x275e，`f58e`跳f8b6。13命中mask，无需进入其他type清理。 |
| 完成尾部顺序 | 接受 | 清bit3后依据旧flags bit0在f8c8跳过计数减少；`f8d6/da`先以h+10调用摘链，再`f8de`读h+c。NULL回正常epilogue；非NULL以a0=h间接调用，返回值不消费。 |
| a0098b4a(node)摘链 | 接受 | 先读prev@4和next@0，word写prev->next；`8b56`重读node+4，再word写next->prev。不清node，不自环，也不读data。 |
| walker与pending消费者 | 接受有界结果 | a005a9d4的type byte来自node-8，比较16；a9dc传node-10，a9e0调用a009e840；不能用它证明type13被关闭。c166/c16a先取出并清pending头，c802在finish前保存h+28，c806调用a009f524。注册本身不会触发pending。 |
| 栈loop与退出后参数 | 接受 | cc1e分配0x400栈帧，cc2a建s0；cc60传s0-240且a2=200清零；cec2传同一地址给a005a736，a1=s0-314。ceca重新读取word(s0-314)作a0081554的a0，绝非直接传栈loop地址。未排除callee通过别名/全局访问loop。 |
| 返回后间接callback | 接受片段/身份未核 | a00815e8取obj+2b8，非NULL时a0=obj、a1=word(obj+2b0)，15f4间接call；返回后15f6**重新读取**obj+2b0，再经a008ab8a归还该值，继而归还obj。callback身份及内部不在本轮。 |
| data自动归还 | 接受其否定范围 | 所核type13 dispatcher、pending和摘链路径没有把data传给callback或直接free(data)。stop内部沿F02边界；不能提升为所有callee绝无data访问，也不能说最终close一定归还请求。 |

纠正项为0；未核不是自动接受：实际close(9428,cb)、该cb身份、退出后consumer、obj+2b8安装、完整heap、厂商时间算术和原库版本均未核。

## ABI、布局与正常状态

偏移均十六进制；只表达已用字段，不认证typedef或完整sizeof：

| 对象 | 最小字段 |
| --- | --- |
| handle/timer | data word@0，loop word@4，type byte@8，close_cb word@c，注册node.next/prev word@10/14，pending_next word@28，flags word@2c，expiry_cb word@30 |
| loop | 注册哨兵next/prev word@8/c，pending_head word@d4；不能据这些字段推完整loop类型 |
| request | 分配8 B：kind byte@0，未观察赋值padding@1..3，value word@4 |
| 返回后清理对象 | payload word@2b0，callback word@2b8；它与loop参数不是同一直接实参 |

```c
// 条件入口；不代表已找到对9428的实际调用。
close_timer13(h, cb) {
    // 原flags低两位必须为0。
    h->flags |= 1;
    h->close_cb = cb;                 // word +c
    stop_a01b2b5c(h);                // F02合同；不是free(data)
    h->pending_next = h->loop->pending_head;
    h->loop->pending_head = h;
}
finish_timer13(h) {
    // 原bit0=1、bit1=0。
    h->flags |= 2;
    if (h->flags & 8) h->flags &= ~8u;
    // 本路径bit0为1，跳过尾部计数减少。
    node = (char *)h + 0x10;
    prev = node->prev;
    next = node->next;
    prev->next = next;
    prev = node->prev;                // 必须保留原重读
    next->prev = prev;
    cb = h->close_cb;                 // 摘链之后读取+c
    if (cb) cb(h);                   // a0不是h->data
}
// a0081554的必要尾部，其他资源callee保留边界。
cb = obj->callback_2b8;
if (cb) cb(obj, obj->payload_2b0);
release_a008ab8a(obj->payload_2b0);     // callback返回后重读
release_a008ab8a(obj);
```

关键原字节：`fc50 6302f714`到fd94；`fd94 97301100`/`fd98 e78080dc`到stop；`f8d6 13850401`/`f8da ef900fa7`以h+10摘链；`f8de dc44`/`f8e4 2685`/`f8e6 8297`从+c取cb并传h；`8b56 5841`重读prev；`ceca 0325c4ce`读取word(s0-314)为参数；`15f4 8297`为obj callback间接边。到期callback则是`d36a 83a7c4ff`从timer+30读取，`d36e 4a85`传timer，`d370 8297`调用。两套callback不能合并。

静态9428、caller栈loop、动态8 B请求三种所有权分开。正常请求已到期完成时，F02已证明free保存请求后才清timer.data；之后条件close没有data要归还。正常请求仍挂data时，只有到期callback归还已证实；条件close没有自动选择+30，因此不能替未知+c callback补写请求清理。未据此下泄漏、缺陷或实际运行时结论。

## 搜索边界、事实和后继

独立重做保留容器汇编中以s1为直接基址、偏移8/c的检索，结果为a802/a806、a8dc/a8e6、a972、cb38/cb46，保存于evidence。该结果只是一组直接引用；非完整别名分析，且s1在c83a后已改作字符串基址。选定a9d4 walker仅匹配type16。deinit c9ea..cad0显式对象仍为9480、9228、9894及两个fd；未见9428实参，但不排除callee/别名/其他阶段。

caller的cece清理返回后，零flag路径经日志cf02/cf04回ccfc；非零经ee9a及eea6/eeb6回ccfc，cd30归还0x400栈帧、cd34返回。这些局部后继无close或pending消费者直呼；日志/其他callee内部和obj callback不能纳入这一负结论。不能由“此前有consumer”推导“退出后必再消费”。

原指令支持字段、ABI、顺序和直接目标这些事实；close_cb/pending等名称及所有权是基于保存/消费关系的分析推断。未认证libuv具体版本或源码，未新增标准实现排除；厂商适配不被略去。REA技能只用于方法和证据区分，既存反编译不替代原字节。此次完成标准是F03小闭包限定复核及精确断边，不是全退出链恢复。

唯一后继建议仍为：从caller返回后a0081554的对象来源追obj+2b8安装者和15f4真实callback，再判断是否接触本loop注册链/9428。不得预命名为walker，不重复全ROMtimer/heap扫描。本轮不接管该后继。
