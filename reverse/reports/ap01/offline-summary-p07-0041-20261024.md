# P-07：端口离线后的 child0 汇总与业务 timer 接入

**可独立使用阶段已闭合但接口未闭；待非作者复核。** `0xa00adabc` 的旧活动非零→新活动零路径，在 E13 的详细 panel reset→SOC 之后，经 `0xa00ae250` 完成 child0 指示撤销、端口状态清理、同步业务重算/条件暂停与旧状态保存，再回到当前通知的常规更新。此合同可用于实现该应用阶段；业务轮转 callback 的完整状态机、重新启动/通知活性及最终应用退出仍未闭。没有新增函数体恢复；本轮新增的是此前未认证尾段的应用合同，不能把“留存已有”写成此阶段早已验收。

认领 P-07，固定基线 `5bbc331ab429fb76e956e50b8081c56f8d278b11`；独占树 `.worktrees/batch-20261024-p/p07`，只写本报告及同名 analysis。已读主树 reverse-design、管理顶部批次P与P-07行；管理已登记精确差集，作者不改表、不接后继。使用 [REA skill](C:/Users/cogic/.agents/skills/reverse-engineer-anything/SKILL.md)，复用留存和必要原ROM，只做静态检查。未开/切共享REA、未执行目标/设备/网络/模型/SIM/QEMU/回放/构建，未改ROM/生产/配置/分析器，未提交推送或创建代理。

首次可得 UTC 开始 `2026-10-24 14:13:20`；预估约30分钟，问题收敛可提前交付；实际结束/墙钟见文末。token由父窗实测统计，本工具不可得，不估算。

## 继承结论

- [E13](D:/Documents/PlatformIO/Projects/cuktech-ap01-firmware/reverse/reports/ap01/ctk-offline-transition-e13-0041-20261024.md)：同callback `app=s6`、`index=u16(port-1)=s8`、旧非零→新零、selector切回、四槽reset→SOC及借用view寿命。E13明确不认证 `ae250` 后尾段；本轮不重验滑动/converter/详细控件。
- [P-03](D:/Documents/PlatformIO/Projects/cuktech-ap01-firmware/reverse/reports/ap01/deferred-refresh-p03-0041-20261024.md)、[P-R02](D:/Documents/PlatformIO/Projects/cuktech-ap01-firmware/reverse/reports/ap01/power-refresh-review-pr02-0041-20261024.md)：动画入口覆盖app+54、当前item数据与延后mask分离、公共尾清cache不等于显示成功。该缓存/dispatcher不作为新增。
- [G05](D:/Documents/PlatformIO/Projects/cuktech-ap01-firmware/reverse/reports/ap01/display-event-flow-g05-0041-20261023.md)、[G06](D:/Documents/PlatformIO/Projects/cuktech-ap01-firmware/reverse/reports/ap01/display-event-review-g06-0041-20261023.md)：`a008bd16(timer)`置暂停bit0，`a008bd70`清bit0；暂停保留timer。仅继承公开边界，不展开调度器、LVGL或timer内部。
- theme-online研究的入口是另一 `0xa00ac93c`，不能凭相同偏移移植对象合同。这里对象由当前callback的 `child(app,0)` 重新取得。

原件沿CATALOG：主树 `roms/0041/ap01-1.0.2_0041.bin`，6,769,704B，SHA256 `972db4c136c7ed9e24a83c07c1a7fd62040ca018b08ca285216d26b1fee3c6b9`；RV32 little-endian，`file_offset=VA-0x9ffff000`。未另建整件哈希账。

## 本轮复核或纠正

来源为主树 `evidence/rea-0041-20261017/evidence/whole-rom-private-20261023.evidence.json#/records[parameters.procedure=...]`。callback `a00adabc` Evidence `ev_19e11c8fc1582881b289f2b24c2a98bbb305f7c2e57caad784442a60d1fb76e5`；构造器 `a005cc1e` 为 `ev_2f6c46cd278b33760dc15702309279178fd3b14a0bef128e4814088addec2866`；timer callback `a00ad602` 为 `ev_9a7754188b853599f5646fcd698e04fa0a888175362857916605f5ae6e3478f0`。三份实际来源均 Ghidra12.1.4 / `RISCV:LE:32:ap01thead2`，digest `b6368dd18431e8113aa5026c713d41e648ab0f6ddd9421ff6c4a49e23b3cd2f3`。沿用既有unreachable-block等局限，只认证选窗，不认证整个callback。

**反编译的无参数pause需要收紧。** `ae2ea`先把`summary+f4`装入a0，`ae2ee`只读timer+14到a4，`ae2f0/2`只改/测a4，`ae2f4→a008bd16`之前没有重写a0。因此本调用实参是刚重读的timer，不能按伪代码`a008bd16()`说它无对象或全局暂停。类似构造器`da5a`返回timer到a0，`da5e`存句柄、`da62`原a0继续pause；这不是新增公共timer实现或旧E05结论的全局更正。

`ad486`的选中分支来自主树 `reverse/rehost/system-complete-0041.json#/local_disassembly/0xa00ad486`，记录自述 **Local Capstone5.0.7 and cached raw Ghidra evidence**。本轮仅将必要标准指令与ROM及当前Capstone复核，不将此来源标为私有thead2。旧pass3文本的构造伪代码为generic `RISCV:LE:32:default`，只用作定位；正式参数桥由上述thead2留存与原字节窗口支持。

## 真正新增：可实施应用合同

`S=load32(load32(child(app,0)+0x10)+4)`，是借用的child0汇总上下文，不是app、item、详细panel或栈view。`ae1ba`已令`bit_port=index+1`；这里掩码用 **port位**，数组用 **index**，不能两者统一为index。

| 顺序与原地址 | 原件观察及应用含义 |
| --- | --- |
| `ae250..25a` | 重新调用`child(app,0)`并取得S；本地无NULL/失败门，不据此补造成功返回合同 |
| `ae25e..294` | 读u8 S+9c，按RV32 shift的port低5位测试。对应位成立才`a00d8f7c(S.word90,1)`；随后**重读**u8 S+9c、清该位并SB回，写u8 S+9d+index=1。位未成立则跳过整个条件段，保留原+9d槽；不是无条件置1/清整个mask，也不承诺剩余位自动重显 |
| `ae298..2b8` | 无条件SB0到S+101+index和S+fc+index；顺序调用`ad486(S,2,0,(u8)index)`再`ad486(S,1,0,(u8)index)`。前两次数组地址用原u16 index，helper实参截u8 |
| `ae2bc..2dc` | LBU S+102、103、104、105、101依次相加，再AND0xff。按**低8位和是否为0**分支，不能改成无条件逻辑OR/非零端口计数 |
| 低8位和=0，`ae2de..2e6` | 调`ad486(S,0,1,0)`，汇入ae2ea |
| 低8位和非0，`ae3aa..3b2` | 取S.wordf4直接同步调用`ad602(timer)`，随后跳ae2ea；不是resume、排队或等待下个tick。该callback从timer.wordc取其业务上下文；内部轮转策略未在本轮认证 |
| `ae2ea..318` | **两条分支均重新取S.wordf4**，测试timer.word14的bit0。bit0=0才`pause(timer)`并记录timer_paused；bit0!=0跳过。不能归纳为“还有其他状态所以继续运行timer” |
| `ae318..33e→adcba..d0` | 清`u8[62fc4054+(u8)index]`，**SH0到S+fa，连带+fb**；日志后保存本次新状态到`u8[62fc403c+index]`。然后进入adcd0常规item字段/当前事件处理，不从离线尾直接return |

其中s4在`adc08`先为`62fc4000`，`adc36`加`0x2c`；所以`ae328`的`s4+0x28+(u8)index`是`62fc4054+(u8)index`，不是另一个裸`62fc4028`数组。SH清除发生在同步ad602返回之后，因此不能把该callback中可能刚更新的+fa/+fb latch当作尾段最终保留值。

`ad486(S,mode,on,index)`只认证本阶段使用的分支：

| 参数 | 选中下游动作（顺序保留） |
| --- | --- |
| `(2,0,0)` / `(2,0,1)` | 分别对S.wordbc / S.worde4调用`a00d8f7c(widget,1)` |
| `(1,0,0)` | 对word槽+a4、a8、ac、b0、b8、b4依次调用同一flag1动作 |
| `(1,0,1)` | 对word槽+cc、d0、d4、d8、e0、dc依次调用同一flag1动作 |
| `(0,1,0)` | 对word槽+54、58、4c依次调用`a00d9044(widget,1)`（沿既有控件flag语义，撤销该flag） |
| 前两种mode的index既非0也非1 | 相应路径直接返回，不能扩成所有端口都有对应图标；外层状态数组仍照原指令清理 |

这些本地动作与借用widget指针不转移所有权；本阶段无分配、free或timer删除，不保存item/view指针。控件物理显示、线程串行性或callback副作用的原子性没有由静态证明。

### timer对象桥与实现边界

构造器必要窗`a005da14..da78`：`s3=s2+0x80`；以`(a0=a00ad602,a1=0x1000-0x448=3000,a2=s2)`调`a008bc64`，返回句柄写`s3+0x74=s2+0xf4`，接着pause同a0；再把s2写包装对象s7+4，把s7写child s1+10。与本次S取得路径一致。`ad61e`从timer+0xc读取业务上下文，支持同一S的timer userdata桥；没有把app+58的另一个timer混进来。此处3000是原API周期实参，实际墙钟调度/误差沿timer适配而未测量。

以下是接入伪代码，**不是原源码**；mask重读和顺序应保留：

```c
S = child_context(app, 0);
if ((load_u8(S+0x9c) >> ((index+1)&31)) & 1) {
    add_flag(load_ptr(S+0x90), 1);
    store_u8(S+0x9c, load_u8(S+0x9c) & ~(1u << ((index+1)&31)));
    store_u8(S+0x9d+index, 1);
}
store_u8(S+0x101+index, 0); store_u8(S+0xfc+index, 0);
summary_widgets(S, 2, 0, (uint8_t)index);
summary_widgets(S, 1, 0, (uint8_t)index);
if ((uint8_t)(u8(S+0x102)+u8(S+0x103)+u8(S+0x104)+u8(S+0x105)+u8(S+0x101)) == 0)
    summary_widgets(S, 0, 1, 0);
else
    business_summary_tick(load_ptr(S+0xf4)); // 原同步ad602，内部策略未认证
T = load_ptr(S+0xf4);
if (!(load_u32(T+0x14) & 1)) pause(T);
store_u8(0x62fc4054+(uint8_t)index, 0);
store_u16(S+0xfa, 0);
// 日志→保存本次新状态到62fc403c+index→当前通知常规更新
```

**新实现策略另列：** 可使用自己的UI控件及timer适配，实现上述状态清理、即时重算与暂停。若希望其他端口继续周期轮转，应作为新的产品策略显式决定；不能声称原离线尾段会保持timer运行。数据复制/异步投递需应用自有存储，沿继承同步借用合同，不持有原item/view指针。

## 实际检查与合并复核差集

[verify.py](../../analysis/offline-summary-p07-0041-20261024/verify.py)只读主树ROM与两份既有JSON，写本目录[evidence.json](../../analysis/offline-summary-p07-0041-20261024/evidence.json)、[checks.json](../../analysis/offline-summary-p07-0041-20261024/checks.json)。最终PASS：13个必要标准指令窗702B/237条、59项直接目标/operand锚点检查，包含9个指定调用目标；三份实际profile核对通过。helper只复核选中分支，不导出全callback；未运行旧作者脚本或指令模型。第一次脚本把常规汇合窗结束写在4B指令中间，边界断言拦下，改到真实边界后通过；无业务结论修改。检查不等于完整数据流形式证明或独立验收。

供一个新非作者一次复核的差集为：port位与index分离、条件+9d写/掩码重读、两类数组宽度、ad486选中模式顺序、低8位和分支、同步ad602后两路均进入条件pause、构造userdata/句柄桥、半字清fa/fb及常规汇合。E13入口/详细panel与P-03缓存门直接继承，不重新审整套动画、dispatcher或公共timer。

## 未闭精确边与一个真实后继

1. `ae3ae→a00ad602(timer)`的**完整业务轮转状态机**仍未认证：旧thead2保留了1210B body及伪代码，真实userdata为同S；可从`ad61e`的timer+0xc与`ad64c`的S+101五槽进入，核S+f8/+f9/+fa/+fb如何选择C1/C2指示，以及`ad78c→a00abbf6`的应用参数和返回后清理，止于本callback返回。建议作为同汇总接口下一块20–30分钟，先由管理者查重登记；不展开公共控件/timer实现。此为真实有地址种子，不由本作者接题。
2. timer全部resume/restart来源、通知间隔/活性、最终销毁/全体writer/并发与后续常规更新的完整结果仍未知；本题没有新的主W退出种子，不重开无种子搜索。P-01停机/P-02底座生产排除。
3. 本阶段可独立实现的前提是已有S/timer/widget正常有效；原本地没有错误返回检查，不能补造重试、回滚或“已物理显示成功”合同。完整离线UI与应用生命周期没有因本题关闭。

结束 `2026-10-24 14:21:06 UTC`，墙钟约7分46秒，范围收敛提前交付；工具读写/等待计入墙钟，没有单独测量有效工时，不以墙钟冒充有效工时。无主动等待或任务中断。前两次PowerShell登录profile将cwd改到其他目录，仅发生无关只读文件名枚举；随后显式login=false与workdir纠正，未在错误目录写入。最终两JSON解析、9条本地引用与尾换行/尾空格检查通过；独占产物3份analysis+1份报告，未改主树。作者自核不代替非作者验收，交付后停止。
