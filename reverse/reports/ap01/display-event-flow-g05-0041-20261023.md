# 0041 G05：display 事件真实安装与刷新调度连接

本轮把一条真实的内建 display 路径连接起来：构造器把 `a0080002 / filter=0x38 / userdata=0` 安装到同一 display 的 `+0x2e8` 事件表。该 callback 从 event 的 current-target 字段取 display，再恢复 `display+0x308` 的 timer。这个 timer 最初创建为 `a00e0ac8`，随后同一构造流程把 callback 换为 `a0080da6`。正常 scheduler 经过周期门调用它；它只有在非阻塞 poll 返回非负且 `revents & 4` 时才交给 `a00e0ac8(timer)`。因此 38 的连接是恢复 timer 并通知 scheduler，仍有周期和就绪条件，不是直接调用绘制消费者。

`a0080002` 不读取、修改或保存 event.param，也不写 event.flags。对本条 filter=38 的 descriptor，35 不匹配，所以这里不存在对 clipped 栈矩形的调整或保存。**全系统是否还有动态 35/ALL handler 未闭合**：不能把本条 callback 的不持有合同推广成所有 descriptor 的不持有合同，也不能宣称 35 在原程序全局必然通过。

## 范围、证据及恢复程度

固定研究基线 `7c3a3cf7ca02515f928141e7e9630051cdf08501`，分支 `codex/re-0041-g05`。读共同规则/G05任务书、G03/G04、F05、已有 display-chain 及 REA 技能；未见本树 AGENTS.md。只写本报告及独占 analysis；未开下级 agent、未修改生产代码/ROM/模型、未切共享 REA target。REA 技能用于约束 shipped-artifact 证据与事实/推断分层；本轮采用可隔离的原 ROM 静态读取，不开可写数据库。

新 [verify.py](../../analysis/display-event-flow-g05-0041-20261023/verify.py) 与 [read_rom.py](../../analysis/display-event-flow-g05-0041-20261023/read_rom.py) 只读主仓库 ROM `D:/Documents/PlatformIO/Projects/cuktech-ap01-firmware/roms/0041/ap01-1.0.2_0041.bin`，地址映射 `file_offset=VA-0x9ffff000`；Capstone 普通 RISC-V32/RVC 解码，按原半字判断2/4B宽度，JAL/RVC jump/AUIPC+JALR 目标独立拆立即数。厂商指令保存原字/字段并读既有 `ap01thead2.sinc` 文本，未执行模型。完整窗口见 [instructions.txt](../../analysis/display-event-flow-g05-0041-20261023/instructions.txt)，检查与直接引用扫描见 [evidence.json](../../analysis/display-event-flow-g05-0041-20261023/evidence.json)。

约12个核心（将同一构造函数的局部窗口计为一项），及必要资源短依赖：

| 核心地址 | 本轮正常路径合同 |
| --- | --- |
| `a0084b96` 构造片段 `4de8..4eea / 6b98..6bc6 / 72e8..72ee / 73b6..73c6` | 同一 s1 display：zero324、建 timer、安装38、替换 timer callback；不宣称整段巨大构造器全部恢复 |
| `a007ffa0..a0080002` | `(display,callback,filter,userdata)` 转 `display+2e8` 后注册 |
| `a01b93b4..a01b951c` | 分配12B descriptor，三word字段，向事件 vector 追加 descriptor 指针 |
| `a00814f4..a0081554` | 栈 event，phase1恰返回1才phase0；G04合同针对核 |
| `a008acfa..a008adf4` | 精确 filter/phase、userdata 写入及 `callback(event*)`；保留G04全部标志返回纠正 |
| `a0080002..a0080030` | 38真实 handler，取 current-target+308，非零才 resume |
| `a008bc64..a008bd16` | timer构造，周期/callback/userdata/repeat及状态 |
| `a008bd70..a008bdd4` | 恢复 timer：仅清 paused bit0，再调通知器 |
| `a0087b06..a0087b30` | next-delay清0，若全局callback存在，以全局data为a0间接通知 |
| `a00804e2..a00806d0` | 本timer直接调度消费：paused、elapsed、repeat、发布时间与间接ABI；其余统计/后续工作有留证不作全调度恢复 |
| `a0080da6..a0080dfe` | timer数据→display/backend fd→poll→条件调用消费者 |
| `a0081554` 资源边 / `a008b7f0 / a008ac38 / a008acc6 / a008ae58` | DELETE后事件descriptor注销、条件立即或延迟释放，之后同display timer摘链/free |

`a00e0ac8` 只新核入口到 `0b70` 的 timer.data/default、pause和display发布，失效区域合并/绘制交付/清空承接 G04，不重复数学。`a008335e` 及 `a00806f8` 仅作另一个调度候选的定位，不算本轮恢复的第二完整业务。

## 原指令支持的真实安装与身份

构造成功后 `a0084da6` 保存 obj 到 s1，`4de8` 长度0x324，`4dec` 清零。`4e94` 明确 `s3=s1+0x300`。`4eca/4ed6` 组合 callback=`a00e0ac8`，`4ed2` a2=s1，`4ed4` a1=16，`4ee2` 调 `a008bc64`，`4ee6` word写返回值至 `8(s3)`，即 **同obj+308**。

`a0086ba2/6bb0` 得 a1=`a0080002`，`6baa` a3=0，`6bac` a2=0x38，`6bb4` a0=s1，`6bba` 调 `a007ffa0`。wrapper 的 `a007ffec` 只把 a0 加0x2e8，`fff0/fff4` 目标 `a01b93b4`。这个注册和timer创建使用同一构造器保留的s1，不能把“同布局”替代为身份推测。

`a00872e8` 读同s1+308到a4，非零分支 `a00873b6/73ba` 组合 a5=`a0080da6`，`73be=1cc7` 写 `8(a4)`。所以不能只引用初始 timer 创建就说 scheduler 最终直接调用 `a00e0ac8`。原构造函数仍有其他分支/callee；这里只连接实际成功路径，不证明每次调用均走至此。

注册器 `a01b93c2` 请求12B，`93d0/93d4` 调allocator；非零路径 `9432` 写callback@0，`9438`写filter@8，`943a`写userdata@4。空vector分配4B槽并设置element-size=4；正常追加 `94e8..9502` 将 descriptor 指针写到数组尾，再增加word count。原字 `a01b94f2=0x20f6150b` 是 `th.mula a0,a2,a5`，即 `a0 += a2*a5` 低32位，连接 element_size*count。没有把 descriptor 内存嵌入 display，也没有为 param 分配长期对象。

容量满时 `a01b9510` 传 count+4 给 `a00ecc68`，返回非零才回追加；为0则直接尾出。这个局部没有 descriptor 回滚free，不替原程序补造回滚。分配为0会走日志/断言入口再接后段，断言是否返回未展开，不能改写为安全的 `return NULL`。调用者没有使用注册器返回值，因此本轮不定义该helper统一返回descriptor的API。

## 事件35/38的实际消费与返回

事件布局由 `a00814f4` 原写入核定：28B本帧event清零；+0/+4=display，+8=code，+0x10=param；分派前+0xc不是param，而是稍后由 descriptor.userdata 覆写的槽。`a008ad8e..ad98` 读 descriptor+4，SW至event+c，以a0=event*间接调用descriptor+0；callback的a0返回值不作为事件结果。

沿用 G04：filter先排除bit16，再要求bit15等phase；比较值是 `filter & 0xffff7fff`。phase1没有匹配本filter38；phase0才匹配38。bit1停止必须归一1；bit0分别有入口0、callback后仅bit0为0、循环头为1的不同路径。不能把 bit0 全部概括成统一拒绝。wrapper首phase恰1才继续第二phase，最后返回实际分派结果；提交35仍必须恰1。

真实handler `a0080002` 首取event+8，以0xffff7fff清bit15后与38比较；不符直返。`0012`读event+4（current-target），`0014`取display+308；为0直返，否则 `0022` 调 `a008bd70(timer)`。**整个28B handler窗口没有读event+10、写event任一字段或保存event指针**。userdata虽注册为0，此handler也不读event+c；display来源是current-target。

因此在本内建handler中，`event38(display,0)` 的0不是消息载荷、不是userdata，也不是timer指针；timer从display取得。本handler不改变flags，它本身不能取消35或使callback后bit0/bit1门发生变化。但 `a0087b06` 的未知全局间接callee仍是外部边，不推全系统无重入/无外部状态变化。

G03/G04 `a00ddd90` a2=本帧clipped，`ddd94` a1=35；本descriptor38不匹配它。同display构造已知的DELETE descriptor filter29也不匹配。新有界扫描 `[a0000000,a01c0000)` 编码直接调用/跳转得到7处注册相关边：wrapper→通用注册，四处wrapper caller（`a00834f4/3522/6bba/6cd4`），以及直接通用注册caller `a00875fe/a01ad6ca`。已识别本构造内38/29；另一函数注册42/38，另外两处非本display构造注册不接管。扫描不是穷尽别名、间接调用或所有后续动态安装，且不把普通线性解码当完整CFG。**本轮未发现本构造明确装35/ALL；是否存在其他35 handler、是否可改clipped或保留栈地址，仍未证。** 仅凭分派器允许传可写指针不能证明实际有人修改/保存。

## 从resume到条件消费者

`a008bc64` 正常构造 timer：word+0=period，+4=当前tick，+8=callback，+0xc=userdata，+0x10=-1；byte+0x14先清bit0，再置bit1。list header=`62fc95f0`。helper分配/链表内部保留合同，未认证上游版本。

`a008bd70` 正常非零路径 `bdbc/bdc0/bdc2` 读byte+14、AND -2、写回，**不重置word+4，也不重写period、repeat、callback、data**；再 `bdc6` 调 `a0087b06`。通知器 `7b12` word写0到全局base62fc957c+84（62fc9600），`7b0e` 读+9c（62fc9618）的callback；非零时从+a0（62fc961c）取a0间调。全局callback实际安装与其最终唤醒对象未展开，所以“通知”是已证call边，“唤醒某OS线程/立即运行scheduler”不是本轮结论。

scheduler `a00804e2` 有全局busy/enabled门；从同全局base+78（62fc95f4，即timer list head）逐timer取下一节点。`0586..058c` 检查timer+14 bit0，置位则跳过。`058e/0594` 从timer+4计算elapsed；`0598/059c` unsigned比较 elapsed>=period 才进入。`05a0` 读取signed repeat，正值先减1；`05b0/05b8` 把新tick写timer+4；`05b4`取callback，callback非零且原repeat非零时 `05c4/05c6` 以a0=timer*间调。初始repeat=-1，不进入正数递减门，且满足非零callback门。

callback后重新读取全局链变化标志及repeat；repeat=0走auto-delete bit1条件删除，否则pause，必要时重新从head扫描。这里保留原顺序和重读，不把timer地址跨任意callback恒定有效作为通用保证。统计/剩余延迟/后续work调用有原字节但未作全系统调度语义恢复。周期参数是原数值16；本轮没有重新认证tick时间单位，不据此新增毫秒精度结论。

本构造最后callback是 `a0080da6`。它保存timer到s1，`0db4`取timer+c作为display，调getter `a007fe32`取backend。清24B本帧poll项后：首word=backend首word fd，第二word=4；`0ddc` 以(a0=&poll_item,a1=1,a2=0)调 `a003f546`。`0de0`返回负则退出，非负取第三word revents，AND4为0退出，否则 `0dec/0dee` 以原timer指针调用 `a00e0ac8`。poll项只借当前栈；本轮未追poll实现/硬件位4生产者。

消费者入口 `a00e0aee` 区分timer非零：读timer+c，写全局62fc958c当前display，再调用 `a008bd16(timer)` 置paused bit0；timer为0则取默认display62fc9590，跳过pause调用。于是本timer在就绪时进入消费者后会暂停；若poll未就绪，适配器没有调用消费者，也没有在其自身暂停timer。后续失效38又可恢复它。G04记录合并/消费/清零成立的前提保留，不由这些静态边证明物理刷新发生。

## 整理伪代码与生命周期

以下是机器合同整理，不是原源码；省略的vector分配/失败与scheduler外层门以前述原序为准。

```c
struct Event { void *original, *current; u32 code; void *userdata;
               void *param; u32 opaque; u8 flags; /* 28B frame */ };
struct Descriptor { void (*cb)(Event *); void *userdata; u32 filter; }; // 12B
struct Timer { u32 period, last_tick; void (*cb)(Timer *); void *data;
               s32 repeat; u8 flags; }; // 本轮只定义已读字段
// one successful path inside a0084b96
zero(display, 0x324);
t = timer_create(a00e0ac8, 16, display);
display->at308 = t;
event_add(display->at2e8, a0080002, 0x38, NULL);
// later, after re-reading same display+308 and nonzero check:
display->at308->cb = a0080da6;

void a0080002(Event *e) {
    if ((e->code & 0xffff7fff) != 0x38) return;
    Timer *t = word(e->current + 0x308);
    if (t) resume(t); // e->param is untouched
}
void resume(Timer *t) {
    t->flags &= ~1;     // byte write; last_tick untouched
    global.next_delay = 0;
    if (global.notify) global.notify(global.notify_data);
}
// selected normal scheduler iteration; next pointer cached before callback
if (!(t->flags & 1) && elapsed(t->last_tick) >= t->period) {
    s32 before = t->repeat;
    if (before > 0) t->repeat = before - 1;
    t->last_tick = now();
    if (t->cb && before != 0) t->cb(t);
    // re-read mutation flags/repeat, then delete/pause/restart as original
}
void a0080da6(Timer *t) {
    Backend *b = get_backend(t->data);
    PollItem p = {0}; p.fd = b->fd; p.events = 4;
    if (poll(&p, 1, 0) >= 0 && (p.revents & 4)) a00e0ac8(t);
}
// a00e0ac8 entry: nonzero timer => current_display=t->data; pause(t)
// zero timer => current_display=default_display; no pause(t)
```

所有权：display内嵌事件表拥有descriptor指针数组，descriptor持有ROM callback和userdata值（本38为0）；event及clipped仍属于提交调用帧。timer作为单独list节点由display+308持有引用，timer+c借display；两者不是同一分配。resume不复制param、不创建区域记录，也不额外分配timer。

正常显示删除 `a0081554` 先发29(param0)，返回后 `1582/1586` 调 `a008b7f0(display+2e8)`。该函数逐descriptor把filter OR0x10000（禁止后续匹配），将list+14 byte置bit1，再调 `a008acc6`。若list尚busy bit0置位，清理留待外层分派；不busy且dirty则 `a008ac38` 遍历、对禁用descriptor调free `a008ab8a`，保留项前移/缩容；无保留项且数组owned时free数组，清指针/count/capacity。故注销可先失效而延后归还，不能把调用b7f0等同任意时点已立即free。

同一次display删除后续 `15de`重读display+308；非零 `15e4`调 `a008ae58`，后者先从62fc95f0链表摘timer、写全局删除标志62fc95fe=1，再free timer。display后端/其他对象清理原序承接F05，不扩展全部析构。只说明该正常删除函数内存在资源边；运行中何时进入删除、外部notify生命周期/并发串行化没有新增证明。

## 事实、推断、未知及后继

事实：上列原字、写宽、同s1身份、descriptor实际三参数、filter38、param未读取、timer+308及callback替换、resume仅清bit0、周期/repeat门、poll条件、消费者pause与注销资源边。功能命名display/事件/paused来自结构与调用对应；准确LVGL版本、源码身份、厂商修改边界均未认证，不新增开源/标准库排除。allocator/free/vector/list/poll/tick保留明确调用合同与未恢复内部，不能因形似库函数静默移出范围。

推断：38在选定构造成功路径用于恢复刷新timer，且消费者在就绪时pause使其形成按失效恢复的循环。这个推断有真实写入/调用条件支持；不包含时序执行观察、精确周期单位或物理交付。

精确断边：

- 35的其他动态descriptor安装、ALL callback和param长期保存未知；有界直接边扫描不是全局否定。
- 全局notify@62fc9618/data@62fc961c的真实安装及下游唤醒未知；本轮已恢复resume→通知call及scheduler→timer callback，未凭名称补OS事件。
- `a008335e` 另一路正常分支在 `3494` 删除旧display+308、`3498`写0，随后 `3522`注册 `a00806f8/filter38/userdata=state+58`；handler以event+c取userdata，byte+4为0才置1、以userdata+8/a1=2/callback=a00806d0调用 `a009f9b6`。`a00806d0`静态有a0=0→a00e0ac8并清state+5c，但选择此替代路径的完整caller/状态所有权及a009f9b6调度消费尚未恢复，不能拼成本内建timer链的必经路径。
- poll返回位4生产者、最终绘制/flush、硬件完成、mode1副本归还继续留给既有后继，不因本轮调度闭合而宣称显示完成。

实际验证：新verify静态提取 **25窗口、1076指令、95检查、7条注册相关直接边，通过**。人工核窗口中的构造身份、真实descriptor写入、精确过滤/flags、callback无param访问、timer构造/resume/调度/适配器/消费者入口及注销顺序；核两个关键厂商字原编码及本地模型原文。没有执行历史验证器、固件、设备/外连、异常param、漏洞验证、历史回放、编译或生产测试。本报告为恢复交付，未冒称独立技术验收。

一个后续闭包建议：先由新agent独立复核本轮同display注册→timer替换→resume/周期/poll→消费者及注销；后续研究只选 **a008335e替代38注册→a00806f8去重→a009f9b6真实调度消费→a00806d0** 的完整状态归还闭包，不同时接管全部GUI事件或最终绘制。
