# 0041 G06：display event38 调度闭包独立复核

结论：**三项精度纠正后，限定接受 G05 的同 display 内建 event38 → timer 恢复/通知 → 周期和 poll 门 → 区域消费者及注销资源边。** 真实 callback `a0080002` 从 event.current-target 取得 display，读取 `display+0x308`；它不读取、修改或保存 event.param，也不写 event.flags。恢复 timer 并非立即消费区域：scheduler 仍须通过 paused、unsigned elapsed/period 和旧 repeat 门，最终 `a0080da6(timer*)` 只有 poll 返回非负且 `revents&4` 才调用 `a00e0ac8(timer*)`。

三项纠正是 handler 字节数、notifier 的 callback 快照/清状态原序、scheduler 的 now → callback 快照 → last_tick 发布原序。它们须替代 G05 的相应尺寸说明或整理伪代码，具体见下表；不改 G05 原文件，不改变已证实的业务门，也不把未知 notifier 安装、poll 位生产者或物理绘制说成已恢复。

## 范围、来源与独立方法

分支 `codex/re-0041-g06`，固定启动基线 `a6a4e7c3d51bb6813f6d3615aaa9110433dc5ae0`，独占本报告与 `reverse/analysis/display-event-review-g06-0041-20261023/`。已读用户原始粘贴请求、共同规则和完整 G06 任务书、[G05](display-event-flow-g05-0041-20261023.md)、[G04](invalidation-submit-review-g04-0041-20261023.md)、所需 [F06](display-exit-review-f06-0041-20261023.md) 资源合同、REA 技能及 native guide；本树 `rg --files -g AGENTS.md` 未返回文件。

本轮新写 [review.py](../../analysis/display-event-review-g06-0041-20261023/review.py)，不导入或执行 G05/G04 的提取器、验证器或历史回放。只读原 ROM `D:/Documents/PlatformIO/Projects/cuktech-ap01-firmware/roms/0041/ap01-1.0.2_0041.bin`，映射 `file_offset=VA-0x9ffff000`。普通指令用 Capstone 5.0.7 RISCV32/RVC，2/4B 长度由原半字判定；B/JAL/RVC branch/jump 和相邻同基寄存器 AUIPC+JALR 目标自行拆立即数。厂商字重新拆 opcode/rd/rs1/rs2/funct 字段，只读本地 `ap01thead2.sinc` 文本核语义，未执行/修改模型。没有打开或切换共享 REA active target/数据库。

独立 [instructions.txt](../../analysis/display-event-review-g06-0041-20261023/instructions.txt) 保存 22 个有界窗口、950 条指令；[evidence.json](../../analysis/display-event-review-g06-0041-20261023/evidence.json) 另存 101 项关键编码/操作数/直接目标检查、4 条厂商字字段及模型原文。另有 `constructor_s1_audit`：对 `a0084da6..a00873c0` 的 2884 条线性指令只留 s1 定义候选及邻近原字，支持选定成功路径的身份核对；它不是整个构造 CFG 或全部 callee 保寄存器的独立证明。没有重新保存整段构造器/区域数学/全 ROM 扫描。

本轮核心与边界：

| 核心地址/组 | 独立核查范围与调用合同 |
| --- | --- |
| `a0084b96` 必要构造片段 | 同 s1 创建 timer、注册38、重读并替换 callback；整个巨大容器和所有错误路径未作整体恢复 |
| `a007ffa0`、`a01b93b4` | `(display,cb,filter,userdata)` → display 内嵌事件表；12B descriptor 的三 word 与指针追加 |
| `a00814f4` | 28B 栈 event、param 与 userdata 分槽、phase1 恰1后 phase0 |
| `a008acfa` | filter/phase、callback(event*)、G04 已纠正的 flags/返回路径针对核 |
| `a0080002` | 实际 filter38 callback，current-target → display+308 → resume |
| `a008bc64` | timer callback/period/userdata/repeat/flags 字段，list 分配与 tick/通知调用合同 |
| `a008bd16`、`a008bd70` | pause 置 byte bit0；resume 清 byte bit0并通知，未重置 last_tick |
| `a0087b06` | callback 快照、next-delay=0、条件读取 data/间调；真实安装仍断边 |
| `a00804e2` | 本 timer 的 paused/elapsed/repeat、callback 快照和发布/间接 ABI；统计及后续 work 算法不验收 |
| `a0080da6`、`a007fe32` | timer.data → display.backend → fd；24B 本帧 poll 项及返回/revents 门 |
| `a00e0ac8` 入口 | timer 非零取 data/pause；timer 零取默认 display；G04 区域消费仅承接已验收合同 |
| `a0081554`、`a008b7f0/ac38/acc6`、`a008ae58` | 先 DELETE 再 descriptor 失效/条件清理，后重读同 timer、摘链/删除标志/free 的短资源边 |

allocator/free、vector slot/shrink、list 内部、tick 和 poll 本体维持明确调用合同，未认证来源也未作为已确认标准实现排除。`a0089d02` 的摘链合同和 `a008aec0` 的分配/list 持有承接 F06；本轮新增独立验证其 timer 调用实参及先后。`a00e0ac8` 后续合并/绘制借用/复位承接 G04；不是再次整体验收全部刷新器。

## 逐项裁决与三项应替代合同

| G05 项目 | G06 裁决与独立原指令 |
| --- | --- |
| 同 display 创建、安装、替换 | **接受选定成功路径**。`4da6` 保存返回对象到 s1；`4e94` s3=s1+300；`4ed2/4ed4/4ed6` 形成 `(a00e0ac8,16,s1)`，`4ee2` timer_create，`4ee6` SW 至 s1+308。`6baa/6bac/6bb0/6bb4/6bba` 为 userdata0/filter38/cb=a0080002/display=s1 的真实调用。`72e8/72ec` 重读同 s1+308、非零到 `73b6..73be` 写 callback=a0080da6。身份不是仅因字段布局相同推断。 |
| descriptor 与 ABI | **接受**。wrapper `ffec` 只把 display 加2e8；`fff0/fff4` 调通用注册。`93c2` 请求12B；`9432/9438/943a` 分别写 cb@0/filter@8/userdata@4。`94f2` 乘加地址后复制 descriptor 指针、`9502` 增 word count。调用者不使用返回值，不新增统一 descriptor-return API。 |
| callback 不触 param/flags | **接受直接 handler 合同**。`0002` LW event+8，mask 清bit15，比38；`0012` LW event+4，`0014` LW display+308；其余只有条件跳转、栈保存/恢复和 resume 调用。没有 event+10/+c/+18 的访问或保存 event 指针。下游未知 notifier 的副作用不由此被否定。 |
| “整个28B handler窗口” | **纠正1：应改为 0x2e=46B。** `a0080002` 到 `a0080030` 末端不含，28B 指的是 sender 的 event 栈对象。代码包含两条返回路径至 `002e`；不能用28B截取把后半 resume/返回遗漏。此纠正不改变 param/flags 不直接访问结论。 |
| filter、phase、event 返回 | **接受 G04 正式纠正**。mask 是 `0xffff7fff`，非低15位；bit16先过滤，bit15等phase。`ad98` a0=event*间调，其返回寄存器不作为分派结果。bit0 入口0、callback后仅bit0为0、循环头bit0为1；bit1停止归一1，wrapper首phase恰1才继续第二phase。 |
| 内建38/29与35 | **接受限定**。本38不匹配35，F06已核的同display29也不匹配35。本轮不重跑G05的7边直接注册扫描，不据它否定动态35/ALL、间接注册或其他handler持有param。 |
| timer 初始化和 resume | **接受**。`bcce` repeat=-1，`bcd4` period word，`bcd6` callback word，`bcea` last_tick，`bcec` data；flags逐次byte读改写，清bit0、置bit1。`bdbc..bdc2` 仅清bit0，`bdc6` 通知，不写 period/last_tick/callback/data/repeat。数值16未认证为毫秒。 |
| notifier 整理伪代码 | **纠正2：先取 callback 快照，再清 next-delay，再按快照条件取 data/调用。** `7b0e` LW a4=[base+9c]；`7b12` SW [base+84]=0；`7b16` 测保存a4；非零 `7b20` LW a0=[base+a0]、`7b24` JALR a4。不能写成先清状态再读取 callback，或测试一次后重读 callback 执行。仍接受“清 next-delay 并条件通知”的业务解释；安装者/callee副作用不变为已知。 |
| scheduler 整理伪代码 | **纠正3：now()返回 → 取 callback 快照 → 写 last_tick → 消费保存 callback 和旧 repeat。** `05a0` signed old_repeat；正数先减写；`05b0` 调now，`05b4` LW a5=timer+8，`05b8` SW last_tick；`05be/05c0` 分别测试保存a5和s9旧repeat；`05c4/05c6` 以timer*间调保存a5。不能写成先发布last_tick再读取或重复读取t->cb。elapsed/period unsigned门、repeat=-1持续及真实callback仍接受。 |
| callback 后重读与清理 | **接受限定**。`05c8` 先读全局删除byte，非零跳过再读当前timer；否则 `05ce` 重读repeat，等0才查byte flags bit1，auto-delete或pause。重启/下个节点照原分支，不作callback后timer永远有效的通用保证。 |
| poll 门与消费者 pause | **接受**。`0ddc` 调poll(&local,1,0)，`0de0` signed负数退出，非负 `0de4/0de8` LW revents并AND4，不满足退出；`0dec/0dee` 原timer交消费者。`0af0/0af2/0af4` 从timer+c发布当前display后pause；timer0分支 `0b3c` 取默认display并回公共门，跳过pause。 |
| descriptor/timer 归还 | **接受局部资源边**。`157e` 先发29，`1586` 调同display+2e8清理；`b87a/b884` dirty与禁用bit16；`acce/acd2` busy/dirty门；`acae` free禁用descriptor，无保留且owned才free数组；`15de/15e4` 重读同display+308并删timer；`ae6e` 摘链，`ae7a` 写删除标志byte1，`ae7e` free。未证明正常业务何时触发整个display删除。 |

表中 `4d/4e/6b/72/73`、`ff/00/05/0d/14/15/ac/ad/ae/b7/b8/bc/bd/7b` 指令前缀均按完整 listing 的 `a008` 或 wrapper `a007` 定位；descriptor `93..95` 为 `a01b`，消费者 `0a/0b` 为 `a00e`。

三项纠正均只在本独占报告给出正式替代，不修改 G05。第1项修正文档/证据边界，第2/3项保留原机读取快照和写序；均不声称已观察到由顺序差异导致的正常运行变化，也不引入异常输入或缺陷验证。

## 可读结构、伪代码与状态

下文是机器合同整理，不是原源码。字段偏移为十六进制，指针/word 为32位；flags为byte。未列字段不推定不存在。诊断/断言是否返回未展开，不能将分配失败改写成自创安全返回。descriptor 扩容失败原路直接尾出，没有在本局部补造 descriptor 回滚free。

```c
struct Event { void *original, *current; u32 code; void *userdata;
               void *param; u32 opaque; u8 flags; /* 28B frame */ };
struct Descriptor { void (*callback)(Event *); void *userdata; u32 filter; };
struct Timer { u32 period, last_tick; void (*callback)(Timer *); void *data;
               s32 repeat; u8 flags; };
// Display known fields: +2e0 backend, +2e8 event vector, +308 Timer*.

// Selected successful constructor path, preserving s1 display identity:
t = a008bc64(a00e0ac8, 16, display);
word(display + 0x308) = t;
a007ffa0(display, a0080002, 0x38, 0);
// Later reread and nonzero check:
t_again = word(display + 0x308);
if (t_again) word(t_again + 8) = a0080da6;

void a0080002(Event *e) {
    if ((e->code & 0xffff7fff) != 0x38) return;
    Timer *t = word(e->current + 0x308);
    if (t) a008bd70(t);   // no direct param/userdata/flags access
}
void a008bd70(Timer *t) { // selected nonzero branch
    byte(t + 0x14) = byte(t + 0x14) & 0xfe;
    a0087b06();
}
void a0087b06(void) {
    NotifyFn saved = word(0x62fc9618); // read callback BEFORE next-delay write
    word(0x62fc9600) = 0;
    if (saved) {
        void *data_now = word(0x62fc961c);
        saved(data_now);              // same saved function pointer, one argument
    }
}
// Selected iteration inside a00804e2, after busy/enabled gates and next-node capture:
if (!(byte(t+0x14) & 1)) {
    u32 elapsed = a008b236(word(t+4));
    if (elapsed >= word(t)) {         // unsigned comparison
        s32 old_repeat = word(t+0x10);
        if (old_repeat > 0) word(t+0x10) = old_repeat - 1;
        u32 now = a008b17e();
        TimerFn saved = word(t+8);    // callback read BEFORE last_tick write
        word(t+4) = now;
        if (saved && old_repeat != 0) saved(t);
    }
    // Original path checks global deleted byte first; only if zero reads t->repeat.
    // repeat==0 then auto-delete bit1 ? delete(t) : pause(t); otherwise follow mutation gates.
}
void a0080da6(Timer *t) {
    Display *d = word(t+0xc);
    Backend *b = a007fe32(d);          // nonzero d: word(d+0x2e0); null d: default fallback
    u8 local[24]; zero(local, 24);
    word(local+0) = word(b); word(local+4) = 4;
    s32 status = a003f546(local, 1, 0);
    if (status < 0) return;
    if (!(word(local+8) & 4)) return;
    a00e0ac8(t);
}
// a00e0ac8 entry:
if (timer) { current_display = word(timer+0xc); a008bd16(timer); }
else current_display = word(0x62fc9590);
// Then common display checks / G04 region-consumer contract; no physical-completion claim.
```

初始化 repeat=-1、不paused；resume只清暂停位，不把 elapsed 归零。就绪时消费者先pause；未就绪或poll负返回则本adapter不pause、不消费。该结构支持“失效38恢复 → 到期尝试poll → 就绪消费并暂停 → 后续失效可恢复”的解释，但不证明每次事件当场执行scheduler，也不证明16的实际时间单位。

事件 flags 返回合同承接 G04，必须区分检查位置。handler本身的返回寄存器未作为dispatcher返回；不能将resume返回值解释为35/38取消状态。本内建38只在phase0匹配，phase1没有因该descriptor而调用它。

## 所有权、资源原序与原字节

display事件表拥有descriptor指针数组；descriptor单独分配12B，持有ROM callback值和userdata值，本38的userdata=0。event属于sender本帧，param只在event+10存一次；callback直接不持有它。G04的35借用clipped栈矩形、按值复制到display内嵌记录的合同继续成立，但没有把未知动态35/ALL handler排除。

timer为独立list分配对象，display+308保存指针，timer+c借display；timer_create初始callback=a00e0ac8，最终成功构造路径替换为poll adapter。创建时自身也调用通知器（`bd02`），位于返回timer并由构造器保存+308之前；未知通知callee不能推定为立即调scheduler。resume不分配资源、不复制区域或param。

display删除中先同步发29，再禁用所有descriptor：filter OR0x10000、事件表dirty bit1。busy bit0存在时 `a008acc6` 返回，禁用已生效而free可推迟；外层dispatcher清busy或处理快照后才可调用cleanup。cleanup遍历禁用descriptor调用free，保留项前移；无保留项且数组owned时free数组并清指针/count/capacity。此合同不等于每次调用清理入口已立即归还全部内存。

随后显示删除重读+308，非零才调 `a008ae58`：将同timer交list移除器、写全局删除标志、再free timer。后端/其他对象和payload/display尾部清理承接F06，不将timer摘链与display本体free混为同一步；运行期删除触发者和外部通知对象的最终生命周期未闭合。

四个必要厂商字独立核原编码和本地模型文本：

| 指令地址 | 原字（u32）/字段 | 本闭包用途与限制 |
| --- | --- | --- |
| `a0086ba6` | `0x4164978b`，rd15/rs1=9/rs2=22，MVEQZ | s6非零保留已移入a5的值，否则取s1；影响构造全局引用恢复，不写s1、不改变注册实参a0..a3。 |
| `a01b94f2` | `0x20f6150b`，rd10/rs1=12/rs2=15，MULA | a0 += element_size*count低32位，指向descriptor指针槽。 |
| `a008ad78` | `0x3cf7b68b`，rd13/rs1=15，EXTU 15:15 | 精确取filter bit15与phase比较；不等于截低15位。 |
| `a008061c` | `0x42e7990b`，rd18/rs1=15/rs2=14，MVNEZ | 后续剩余延迟选小值的单条指令；未因此验收全部剩余延迟/统计/work算法。 |

构造 s1 定义审计看见若干诊断路径把s1装成字符串基址，以及 `6d74` 删除display后 `6d78` 置s1=0、`6d7a` 直接跳 `73ea` 发布出口。这些不是选定成功路径中的display替换。仅就正常成功路径保持身份；本轮不恢复所有诊断终止callee、整个构造器的可达性或任意间接callee对ABI的遵守证明。

## 接受边界、实际验证与后继

指令事实：安装的三个注册实参及同s1身份、timer字段宽度、callback替换、filter与真实handler访问集合、notify和scheduler的快照顺序、unsigned周期门/旧signed repeat门、poll signed返回与bit4门、消费者入口pause、descriptor失效/延迟free和timer移除/free调用序。结构/业务名称依据字段及上下游合同，是有依据恢复；没有称为原源码。

行为推断：在选定正常构造链，event38用于恢复区域刷新timer；poll就绪才交现有区域消费者，并在入口暂停timer。这是静态连接结论，不是执行观察。原ROM路径和局部算法形似LVGL并不足认证准确版本或未改实现；本轮未访问候选源码、未外连，也未新增开源/标准库排除。厂商callback/适配层仍属于已恢复私有合同。

精确未核/断边：

- `62fc9618` notifier callback与`62fc961c` data真实安装、保存对象寿命及下游唤醒对象未知。已核resume→call边，未闭合OS线程/调度器触发来源。
- `a003f546` poll内部及backend fd的revents bit4实际生产者未知；区域消费者后续绘制、flush、DMA/物理完成未接管。周期16仅为机器数值。
- 动态35/ALL descriptor、param外部长期保存与重入未知。G05有界直接边扫描仍仅作原有定位证据，本轮没有以重复扫描构造全局否定。
- G04区域数学/清零、mode1链副本最终归还沿用原边界。descriptor延迟归还不证明全局并发序列化或外部notify对象能安全跨所有显示删除存活。
- `a008335e` → 替代注册 `a00806f8/filter38/userdata=&state+58` → `a009f9b6` → `a00806d0` 仅保留G05可定位候选：旧timer删除/清槽、去重byte、调度消费和状态归还须另闭包。本轮未独立重做该链，不把它拼为内建timer的必经阶段。

实际执行新 `review.py`：**passed，22窗口/950指令/101检查**；另有有界构造s1定义候选审计及4条厂商字字段/只读模型语义核对。人工读取新listing中的构造实参、注册/分派、handler、timer初始化/pause/resume、notify、scheduler选定迭代、poll/getter、消费者入口和资源清理；按原寄存器流形成三项精度纠正。脚本最初两次取窗末端落在32位指令中，被边界断言拒绝，随后按完整指令边界调整；这些是静态工具取窗修正，没有执行ROM。未执行旧验证器、固件、实机/外部服务、历史回放、异常param、漏洞验证、编译或生产测试。

本轮达到独立复核范围闭包，**在三项精度纠正和所列断边下接受G05**。一个适合后续的完整小闭包是 `a008335e` 替代38安装 → `a00806f8` 去重 → `a009f9b6` 真调度消费 → `a00806d0` 状态清回及owner退出归还；只作为建议，不自行承接，不扩全部GUI timer或最终绘制。
