# P-05：cmd50 raw latch 与 cmd55 条件清除

**部分恢复；作者交付待非作者复核。** 已能复刻 `u16[0x62fcb50a]` 的一个置位路径及一个条件清除路径。尚无业务消费者、请求用途或专属通知证据，继续称 **raw latch**；不能命名为告警、成功、待确认或端口故障。完整消费接口未闭合。

认领 P-05，基线 `5bbc331ab429fb76e956e50b8081c56f8d278b11`，独占 `.worktrees/batch-20261024-p/p05`；仅本报告与同名analysis。预估约30分钟，可提前收敛。首次可得开始 `2026-10-24 14:04:59 UTC`；结束与实际墙钟见末节。使用 [REA skill](C:/Users/cogic/.agents/skills/reverse-engineer-anything/SKILL.md)。未运行固件、设备、网络、SIM/QEMU、回放、构建或ISA模型，未改ROM/生产配置/分析器，未提交推送、创建代理或接后继。

## 继承结论

- [P-02](power-producer-p02-0041-20261024.md) 提供真实种子 `0xa00a921c→0xa00a9234`：cmd50逐项处理时，`u16(record+4)&0x6000==0x6000` 才OR置位本半字。P-02为作者交付、待非作者复核，本文不提前称已验，不重做功率、历史、item/total mask或通知walker。
- [poll-phase B02](poll-phase-writer-b02-0041-20261023.md) 与 [dock](dock-presence-polling-0041-20261023.md) 的轮询选择器、phase与连接阶段为既有合同；不能因邻近 `b508/b50c` 就把本半字认成它们的一部分。
- [P-01](mode-stop-p01-0041-20261024.md) 提供关闭、`0xa00a5558` 复位与重新发现边界。停机复位不重做，本文不把关闭等价成本latch清除。P-01状态按其报告保留，不借其待复核结论关闭本接口。

查重先读主树 reverse-design、管理顶部P段与P-05行，再查指定旧dispatcher/initializer及其引用metadata。已有dispatcher全文早已包含清零字样；本轮新增为**置位→cmd55清除条件及通知时序的连接合同**，不把旧body或408B复核字节重复算作新增函数。管理表及当前P-02提及本地址不证明历史从未分析。

## 本轮复核或纠正

原件只读 `D:/Documents/PlatformIO/Projects/cuktech-ap01-firmware/roms/0041/ap01-1.0.2_0041.bin`，6,769,704B；既有SHA256 `972db4c136c7ed9e24a83c07c1a7fd62040ca018b08ca285216d26b1fee3c6b9`，RV32 little-endian，`file_offset=VA−0x9ffff000`。只核长度/有限原字节，不新造整ROM摘要清单。

主要来源为 `reverse/analysis/buzzer-backlight-0041-20261023.json#/functions[address=0xa00a8582]`，Evidence `ev_6f9f82e5daf0540a1c24a0b85daa2e394785391692765e5e3e100eb7b37ed94c`，Ghidra 12.1.4，language **`RISCV:LE:32:ap01thead3`**，profile `bcefdee5092076e55636e077b45523e203f4b870ae7b7ab547945ed1b8162279`。其原来源为 `evidence/rea-0041-20261017/round3/evidence/whole-rom-round3-initial.evidence.json`，原来源摘要 `689b060f96eaba167291ecf78c8998e5aea590555e793cac735d448265d1d385`。不以旧USB整合文件另一profile代替此记录。

[静态证据](../../analysis/telemetry-latch-p05-0041-20261024/static-evidence.json) 保留上述source、5个必要窗口、逐指令原字节/文件偏移/留存与标准Capstone解码、参考metadata及有界负查。整个dispatcher仍有旧反编译警告，本文只认证选定窗口。`0xa00a893a` 厂商extu原字保留，前驱是两个LHU的OR，零/非零判定可由这两个16位输入核对；未加载/执行厂商模型。

原始留存 `/records/2/normalized_result/outgoing_references` 对本地址仅有三条：`8a1e WRITE`、`9228 READ`、`9234 WRITE`。其中READ只是OR写回的读改写前半，并非独立消费。本body recognized reference集合不能当全ROM全局xref全集。

另外按任务边界检查 `0xa005a736` initializer的留存引用metadata：无精确目标 `0x62fcb50a`；已有 `0xa0191746` selector及 `0xa00a5558` reset的留存body无该地址明示访问。这些只是相应body/provider识别范围，不排除间接callee副作用。没有可复用的独立全局xref索引，未新建/修复共享REA或扫描全ROM。REA技能调用仅查询session，返回open=false；未打开、切换或关闭共享目标。

按管理窗口补充定位，对主树 `reverse/analysis/0041-20261013/0041-ghidra-pass3.txt`、`pass4.txt`、`pass5.txt` 各查精确地址token，均0命中。文本无命中不证明真实消费者不存在；不继续全目录负搜。

## 真正新增：置位至条件清除的生命周期合同

### 写入端（继承P-02，必要原字段复核）

`0xa00a9212` LHU取得当前record+4；`9216/9218` 得到与0x6000的AND，`921c` 不等则跳过。

```c
// 分析伪代码，非原厂源码；RV32机器宽度。
if ((load16(record+4) & 0x6000) == 0x6000) {
    uint32_t bit = 1u << (index_word & 31);
    store16(0x62fcb50a, load16(0x62fcb50a) | bit);
}
```

`9224`构造地址，`9228` LHU，`922e` SLL，`9232` OR，`9234` SH。最终只保留低16位，不把它推广为无限端口位图。本分支不根据不满足条件的record清对应位；也没有新增item mask位或直接调用通知函数。后来item/total通知仍由P-02中其它状态/数值/历史变化控制；不能将它当本latch变化通知。

### 清除端：cmd55基础信息初始化门

`0xa00a8602/8606` 将cmd55路由到 `88f6`。以下按机器实际读点，不把全局重读折叠为一个payload快照：

| 读点/条件 | 与latch清除的关系 |
| --- | --- |
| `88f6..8904` 调 `0xa0191652(0x62fcb004,24,&descriptor)` | 缓存helper先执行；返回值未作为本分支成功门。若缓存变化，既有helper同步raw通知cmd+0x20即0x75发生在下面各读点与清latch之前。 |
| `8930/8934/893e` 读缓存 `u16[b014] OR u16[b016]` | 结果为0则去`8940`既有分支，不到本清除路径；非零到`8950`。不能用helper返回值代替。 |
| `8950` 取缓存 `u8[b01a]`，`895a`写阶段b50c=1 | 保存的count byte等0xff则`8966→8a22`，跳过本次清除。阶段1写入先于该判断。 |
| byte!=0xff，`898e`写 `b01c`，`8992`日志，`8996`重读b01c | 重读为0则`899a→8a22`，仍跳过清除。不能把日志前的count非零当重读保证。 |
| 该次重读非零 | 经既有三缓存非空检查/必要分配callsite后，`89e0`再次读b01c至a6；构造两组mask的局部loop完成后到`8a12`。不展开allocator或扩其它flag。 |
| `8a1a/8a1e` | `lui a5,0x62fcb; sh zero,0x50a(a5)`，无旧latch检查，清整个16位。随后`8a22`继续原对象重建路径。 |

正常返回/前置内存有效的静态路径中，第二次count重读即使变0，mask loop本身也可直接结束到清零；**决定是否跳过清零的是8996那次重读**。本题不声称这些重读间有锁或运行时一定变化。

```c
// 仅展开与本latch有关的条件；省略已有日志、类型及数组重建。
cache_update(base_cache, 24, descriptor);  // 可同步raw通知，先于下面的读
if ((load16(b014) | load16(b016)) == 0) goto existing_other_path;
saved_count = load8(b01a);
store8(b50c, 1);
if (saved_count == 0xff) goto existing_rebuild;
store8(b01c, saved_count);
log_base_info();
if (load8(b01c) == 0) goto existing_rebuild;
existing_cache_pointer_checks_and_allocations();
n = load8(b01c);
existing_mask_loop(n); // 8a06/8ab4..8ac8，回到8a12
store16(b50a, 0);
existing_rebuild: /* 8a22，继续原对象重建 */;
```

此清零是基础信息接受/重建路径的动作，不是从latch读出请求、逐bit确认或取出后清除。未证“断连自动清latch”“每次cmd55都清”“cmd50某位回0便清”“置位后必在某时间清除”。`count=0`和`0xff`两条跳过只限本路径，不保证整个callee图绝无其它写者。

### 通知、请求与所有权边界

本半字是固定RAM地址，无动态分配/指针转移/归还接口；这里只恢复访问语义，不外推线程安全。cmd50 OR与cmd55清零均无已证latch专用回调或请求完成结果。cmd55 raw缓存通知若发生，先于清除；故不能把0x75视为“此latch已清”的确认。后面的既有UI对象重建/轮询调用没有与本半字独立读取连接的证据，不能仅凭先后命名为本latch通知；未穷尽其间接副作用。

应用现在可复刻上述raw置位与条件清零，或将它作为未解释内部状态保留。任何告警文案、成功状态、MCU请求含义、清除确认事件均无证据；不建议从该半字生成用户可见语义。

## 未闭精确边、检查与合并复核包

断边：**`u16[0x62fcb50a]` 在cmd50 OR之后，尚未定位独立业务读取者→是否产生请求/可见状态→确认/清位→专属通知**。已知cmd55全清不能填补消费端。全局引用覆盖不可得，指定旧导出/initializer/selector无明确读者，不作无种子扩扫。

一个有真实种子的后续建议：若能取得**隔离且匹配0041/ap01thead3**的既有数据库或留存精确xref结果，只查询 `0x62fcb50a`（必要时覆盖其第二字节）并从实际READ callsite跟到业务输出；预计20–30分钟。若仍只返回本报告三条reference，停止并保留raw latch；不以地址种子为由扫描全部flag、driver或MCU。本轮不自行启动。

新非作者一次合并复核：①P-02 writer必要前提与RV32位移/SH宽度；②cmd55路由与缓存通知先于读点；③b014/b016门、count=ff与8996重读为0两条跳过；④mask loop结束与8a1e清16位；⑤“READ仅为RMW”与全局覆盖/通知未知措辞。helper、allocator、item/total通知和停机复位继承，不逐个拆新题。

实际执行 [verify_static.py](../../analysis/telemetry-latch-p05-0041-20261024/verify_static.py)：**33项检查、5窗408B PASS**，选窗均与旧留存逐字节一致；只做原字节字段、控制目标、source/profile、三条reference与三个指定文本的有限检查，没有输入枚举或目标执行。作者自核不是独立验收。

结束时间及交付检查追加于末尾。工具未提供任务token用量，由父窗遥测，不估算；无主动等待或任务中断。shell默认登录初始化将cwd改到另一目录，首次相对读取失败后立即以login=false及显式workdir修正，未写入错误目录。

交付结束 `2026-10-24 14:11:45 UTC`，至最后静态/链接检查墙钟约406秒（6分46秒），含工具读取与离线核验，未另测有效工时。JSON解析、报告本地/主树继承链接、末尾换行/无尾空格及`git diff --check` PASS。独占树仅新增本报告、verify_static.py及本地忽略的static-evidence.json；最后一项需随报告原路径保存，不能因Git忽略而遗漏。未提交推送。约半小时为工作量上界参考，本题在有界证据耗尽后提前收敛，不为时长扩题。
