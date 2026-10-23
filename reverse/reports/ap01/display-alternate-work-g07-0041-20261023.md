# G07：替代38路径的 poll 身份、去重与归还

2026-10-23；研究基线 `fca1d5e`，分支 `codex/re-0041-g07`。状态：**局部增量恢复，待独立技术复核；后端就绪分发及退出后drain时序仍未闭合**。本文偏移视图与伪代码是分析者整理，不是原始源码。

替代38不是已经证明的通用“work队列”：实际对象是 `type8` poll handle，借同一framebuffer fd登记backend事件。已知event去重byte在正常回调末尾清零；新增证据说明回调先停止同一个poll，再消费默认display。正常退出登记和close walker合同大部分早已有证据，本轮只补本owner的身份和最终计数callback。没有静态证据可以保证某次登记后必然发生ready事件、退出后必然再次drain或每个关闭callback恰好执行一次。

## 继承的旧结论：已有成果→实际缺口

| 既有出处 / 证据类型 | 已解释的行为 | 局限 / 本轮实际补什么 |
| --- | --- | --- |
| [G05](display-event-flow-g05-0041-20261023.md)，`evidence.json` 的 `alternative_install` / `alternative_callback`，原字节行为 | `a0083494`删除display+308旧timer并清槽；以user=`state+58`登记filter38；`a00806f8`先检查byte user+4、置1，再以user+8提交 `a009f9b6(...,2,a00806d0)`；回调调用 `a00e0ac8(NULL)`，末尾清state+5c | 这些不是本轮新发现。只补同对象poll初始化、start/stop/adapter ABI，以及owner清理连接。原窗口只比对旧raw，没有再导出 |
| [G06](display-event-review-g06-0041-20261023.md)，独立复核 | 主timer路径及三处精度纠正；替代链明确留断边 | 直接继承；本轮不重复timer、poll adapter a0080da6或event主dispatcher |
| [既有initializer](../../analysis/factory-test-0041-20261023/retained-initializer.json)，`ev_dc0e38b0f382799ea2a8e8ad7f21cefc5998b0767ecf38a58cfdebe8add167c3`，旧反编译、汇编及原raw ranges | `a005b100/b104/b108`已有0x188B uv context分配与s4身份；`be48/be4c`已保存全局notify=`a00804ba`、data=state；`be50`已有 `a008335e` caller；`c874..c8c0`已有两poll及timer关闭登记、notify清槽 | 不能把G05尚未展开误写成此前未分析。对这三个旧窗口只比对原bytes；本轮细化 `a008335e` 内参数/子对象和关闭callback，不重新导出整个initializer，也不将notify安装计新增 |
| [C03](pogo-close-callback-c03-0041-20261023.md) / [C04](pogo-close-review-c04-0041-20261023.md)，近期原字节及独立复核 | 已有 `a009e4f6(loop,poll,fd)`→`a009f9b6(poll,events,cb)`调用合同，poll首word回指owner、owner计数用法 | Pogo ctx+198不是本uv ctx+180；不跨对象套用。新补display场景的子对象身份及本callee必要窗口 |
| [C05](pogo-close-dispatch-c05-0041-20261023.md) / [C06](pogo-close-dispatch-review-c06-0041-20261023.md)，[F03](miio-loop-close-f03-0041-20261023.md) / [F04](miio-loop-close-review-f04-0041-20261023.md) | `a009fb96`保存close callback；type8先 `a009f972` 再入pending；`a009f524`共用尾部以原handle调用close callback；type13和共用完成尾部也已有 | 直接引用登记/消费/共用尾部，不重恢复整个libuv关闭器；这里只补stop内局部状态和 `a007ff54`本owner释放 |
| 优先三个报告/矩阵、四领域complete、page-logic、round2/round4、pass3，见[有界检索](../../analysis/display-alternate-work-g07-0041-20261023/reuse-crosscheck.json) | complete和最终passed-in-sim解释重建UI与服务替代；旧settings timer和ZIP SIM sleep/redraw不是本ROM poll ABI | 20个文本文件、ZIP 39个可UTF8读取成员按8地址及字段/队列词的有界检索无命中；仅说明该集合的文本检索结果，不证明从未分析。上面的近期initializer恰有重要重叠 |

ZIP只读成员，未运行脚本、全量解包或复制。旧路径失效不是缺证依据；本轮采用当前 retained initializer 与归档成员。passed-in-sim不用于认证原ROM来源、ABI或驱动完成。

## 本轮复核或纠正

旧G05两个窗口和initializer三个局部窗口均与原ROM逐byte一致，记录在[证据JSON](../../analysis/display-alternate-work-g07-0041-20261023/evidence.json) 的 `old_conclusion_rechecks`，属于**旧结论复核**，不计新增业务。G05没有断言该链是内建timer必经路径，本轮保持此限制。

“work”在管理任务书中是待查工作代称；此次实证应收窄为**poll一次激活、停止与pending byte归还**。未使用通用workqueue排队假设，也未证明该分支在实际设备上执行。ROM字符串 `a01c3874` 是 `.../lvgl/src/drivers/nuttx/lv_nuttx_libuv.c`，`a026633c` 是 `libuv/src/unix/poll.c`，只能支持模块命名；源码身份/确切版本继续未知，新增开源排除0。

## 本轮真正新增

### 同一owner、fd及内嵌poll身份

`a008335e` 入口 `3376/337a` 分别读参数0的+0 loop、+4 display；第二参数保存为state（`342e`）。`342c/3430/3434/3436` 调 `a007fe32(display)`后取返回对象首word，并存state+58，正常后续条件是该有符号word>0且display+308非零。这不是独立新分配的fd holder。旧窗口 `349c..34a8` 以loop、state+60、word(state+58)调用 `a009e4f6`，此前 `34a4` 将state写到poll首word；`34ac..34c2` 增state+180，再用同poll启动a00806d0。第二poll为state+bc，初始化也以同一fd；仅为本题owner退出身份定位，不展开其filter42业务。

```c
// 仅本题必要的偏移视图；不是完整struct/大小认证。
// state本身另有timer，来自旧initializer的0x188B分配。
state+0x58 : s32 observed_fd;
state+0x5c : u8 pending;
state+0x60 : Poll p;        // p+0 = state
state+0xbc : Poll other;    // other+0 = state，另一条42业务不展开
state+0x180: u32 close_count;
// filter38 user = state+58，故 user+8 == &p。
```

`a009e5f6..e634` 说明poll init正常成功段将type byte与flags word置8、loop写poll+4，初始化 `poll+34` watcher；callback常量由 `e614/e628` 构成 `a009f8ea`。`a009cd86/cd88` 将callback写watcher+0，将传入fd写watcher+24（即poll+58）。这里无证据把整个poll视作state+58；它们相差8B，首word也不同。

### start→adapter→stop→clear的ABI及原序

`a009f9b6` 正常入口低2 flags位为0时，保留poll到s1和callback到s2；先 `a009f972(poll)`，然后按**保存的a1**构建backend mask：输入bit0保留为1，输入bit3则加2；否则输入bit1则加4。此次a1=2走后者，即mask4。以 `(poll->loop,poll+34,mask)`调用 `a009ec98`，设置active bit2，必要时增加loop+4，最后 `fa1c` 写callback到poll+30，`fa28` 返回0。callback保存位于backend登记调用之后；不能改写成先发布callback或直接执行callback。a00806f8并不检查这个返回值，其pending已在调用前置1。

`a009f8ea` 的真实入口是 `(loop,watcher,backend_events)`：`f8fe` 以watcher-34还原poll；从watcher-4，即poll+30，读callback。正常事件分支按backend bit1→公开bit3、bit2→公开bit1、bit4→公开bit2映射，另保留bit0，再以 `(poll,0,mapped_events)`间接调用（`f964..f96e`）。另一个已有编码分支 `(events & 0xa)==8` 先解除watcher mask0x17、清active/计数，再调用 `(poll,-9,0)`；这里只陈述正常程序内存在的状态分支，未构造或执行输入。

`a00806d0` 不消费status/events。G05原窗口中 `06da` 从poll+0取state；`06dc/06e0` 精确PC相对调用 `a01b2cb0(poll)`。新增stop wrapper窗口证实其正常分支转 `a009f972`；后者对poll+34调用 `a009f442(...,0x17)`，清flags bit2，必要时减loop+4，再以loop、word(poll+58)调用 `a009e212`。内部backend取消及OS唤醒不在此扩展。

因此本题正常返回链的原序是：

```c
on_event38(event) {                 // 继承G05，不计新增
    Prefix *u = event->userdata;    // u == state+58
    if (u->pending) return;
    u->pending = 1;                 // byte store；先于poll_start
    poll_start(&u->poll, 2, refresh_ready); // 返回值未消费
}
refresh_ready(Poll *p, int status, unsigned events) {
    State *s = p->userdata;         // p == s+60，首word保存s
    stop_a01b2cb0(p);               // 新增stop合同
    a00e0ac8(NULL);                 // 继承G05/G04：使用默认display
    s->pending = 0;                // byte store，消费调用返回之后
}
```

不能将状态byte清零提前到stop之前或刷新之前，也不能将NULL刷新改为本注册display。注册display来自a008335e的第一个参数+4；NULL消费选择默认display是另一个身份合同，二者运行时相等未在本题证明。重复38在pending非零时直接返回，未再触发start；这说明软件去重条件，不证明成功登记/必然ready/跨线程互斥。

### 正常退出登记和最终owner释放

旧initializer的 `c874/c878` 仅在signed word(state+58)>0时，依次提交 `a009fb96(state+60,a007ff54)`、`a009fb96(state+bc,a007ff54)`。然后清全局notify和data，提交 `a009fb96(state,a007ff54)` 关闭timer；本段的登记顺序是旧证据，非本轮新增。type8及共用close完成回调的传递直接继承C05/C06/F03/F04，不能把登记本身写成已经完成释放。

新增 `a007ff54..ff9e`：a0为原关闭handle；`ff5e` 从handle首word取state；`ff60/ff64/ff66` 以32位读、减1、写state+180；`ff6a` 为signed bgtz，减后>0返回，否则记录Done日志，`ff90/ff92` 将state交 `a008ab8a`。释放封装合同继承C03，不重导底层heap。

这与本题poll首word回指及+180初始化增加相互支持，形成“登记子handle→共用完成尾部给原handle→本callback取owner→计数归还”的**静态连接**。未证明关闭callback时序、全局计数不变量或callback恰好一次；不把Pogo+198的计数/释放合同直接套到本state。

## 仍未闭合的精确边及验证

- `a009ec98(loop,poll+34,4)`已定位登记；`a009f8ea(loop,watcher,events)`已定位消费adapter及poll+30间接调用。但从实际OS/driver ready到此watcher+0间接调用的后端循环仍未逐指令闭合，不能称实际调度已观察或必达。本轮不扩全部poll后端。
- 正常退出已有登记和共用walker合同，但登记之后该loop是否继续drain、state+180全部写者/全局不变量、所有callback完成后才离开owner作用域的时序仍未知。旧SIM回归不能填这些边。
- `a00e0ac8(NULL)`实际默认display与本注册display是否始终一致未知。other poll的filter42动作、驱动fd ready位生产者及物理flush不在本题；未以命名猜补。
- initializer旧反编译中的custom0/unaff及完整大函数边界没有用作新增ABI依据。本轮只按其原raw比对必要调用/退出窗口；新增9窗口均普通RV32/RVC，未依赖未解码厂商字。assert分支的返回/no-return不作推定，只论正常前置路径。

实际运行[本轮静态验证脚本](../../analysis/display-alternate-work-g07-0041-20261023/verify.py)：9个新增依赖/身份窗口、590B、215条指令、44项精确asm/调用目标检查通过；5个旧窗口原bytes局部比对通过。原ROM映射 `VA-0x9ffff000`；新证据仅保留这9窗口的raw/指令，无重复plaintext导出、全函数导出或新哈希清单。复用读取20个旧文件及ZIP的39个UTF8成员，未执行旧脚本、SIM、构建、历史回放、固件、设备或外连，未改生产代码/ROM/config/分析器模型。

本题新增是poll身份/adapter ABI/stop清理以及本owner callback计数释放的局部合同，不是新增一个页面业务或完整显示闭包。一个后续精确任务可独立复核这些新增合同；若再研究调度，只补 `a009ec98` 对应watcher的真实ready消费调用点，继续继承本报告与既有close walker，避免重扫全部GUI/库。
