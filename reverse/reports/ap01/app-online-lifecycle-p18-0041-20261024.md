# P-18：摘要在线接入、初始化与业务 timer 活性合同

**可独立使用阶段已闭合但接口未闭；待非作者合并复核。** 同一 `0xa00adabc(app,item)` 中，正常有效端口的旧活动0→新活动非0路径，从入口门、child0摘要身份、接入清槽，到按原暂停bit恢复并重置业务timer、保存新状态、汇入常规更新，已形成可实施合同。与已验P-07离线pause组合，可实现已构造对象的接入/离线timer阶段；**不等于完整应用生命周期或“在线输入到正确摘要内容”全部闭合**，常规设备分类到五槽值的生产、最终销毁/并发/调度时效仍未闭。

认领P-18，作者 `/root/app_summary_research_01`；独占树 `.worktrees/batch-20261024-p/app-summary-research-01`，实核基线 `5bbc331ab429fb76e956e50b8081c56f8d278b11`。仅读主树最新reverse-design、管理顶部P及P-18行，只写本报告与同名analysis，不撤销他人修改。采用 [REA skill](C:/Users/cogic/.agents/skills/reverse-engineer-anything/SKILL.md)，复用留存和必要ROM离线静态；没有开/切共享REA、运行目标/设备/网络/SIM/QEMU/回放/指令模型/构建，没有改ROM/生产/配置/分析器，未提交推送、创建代理或接后继。预估约30分钟，收敛可提前交付；UTC起点 `2026-10-24 15:07:07`，实际结束见末，token由父窗实测统计。

## 继承结论

- 先查主树 `reverse/rehost/system-complete-0041.json#/native_semantics/Power_bottom`：已有3秒摘要轮转/互斥可见概念，且明确四端口SIM推广不等于原始五槽编码恢复；`#/cached_evidence`/旧callback留存不作为本次新函数恢复。该概念及全部旧函数体新增恢复均为0。本轮差集为此前P15未认证的在线门、原参数身份、清槽与resume/reset顺序，不将已有body或旧SIM行为计作新业务。
- [P-07](D:/Documents/PlatformIO/Projects/cuktech-ap01-firmware/reverse/reports/ap01/offline-summary-p07-0041-20261024.md) / [P-R07](D:/Documents/PlatformIO/Projects/cuktech-ap01-firmware/reverse/reports/ap01/offline-summary-review-pr07-0041-20261024.md)：同child0摘要S、`create(ad602,3000,S)`→S+f4、初始pause、离线清槽/同步tick/两路条件pause/SH0清FA-FB已验，直接继承。
- [E13](D:/Documents/PlatformIO/Projects/cuktech-ap01-firmware/reverse/reports/ap01/ctk-offline-transition-e13-0041-20261024.md)及其E04前提：同callback的正常端口解码及 `index=u16(port-1)`、新活动来自item+d的u8、旧活动数组62fc403c、旧非0新0门、详细panel reset→SOC已解释。P-03/P-R02的动画门/缓存策略沿原接受范围继承，不把机会式后续通知改成保证重放。
- [P-R11](D:/Documents/PlatformIO/Projects/cuktech-ap01-firmware/reverse/reports/ap01/summary-rotation-review-pr11-0041-20261024.md)：timer+c取S、五槽低8位和/选择/F8-FA-FB、真实H/U实参已验。[P-R13](D:/Documents/PlatformIO/Projects/cuktech-ap01-firmware/reverse/reports/ap01/summary-output-review-pr13-0041-20261024.md)固定输出及局部mask、[P-R15](D:/Documents/PlatformIO/Projects/cuktech-ap01-firmware/reverse/reports/ap01/summary-pane-review-pr15-0041-20261024.md)开关/布局已接受；不重算为本轮新增。
- [G05](D:/Documents/PlatformIO/Projects/cuktech-ap01-firmware/reverse/reports/ap01/display-event-flow-g05-0041-20261023.md) / G06已有timer构造、暂停bit0及resume清bit0后通知的公共边界；不认证原LVGL版本、不下探调度器或通知器内部。另一theme-online入口 `0xa00ac93c` 与本题对象分开。

原件身份沿CATALOG：0041 `roms/0041/ap01-1.0.2_0041.bin`，6,769,704B，SHA256 `972db4c136c7ed9e24a83c07c1a7fd62040ca018b08ca285216d26b1fee3c6b9`，RV32 little-endian，`file_offset=VA-0x9ffff000`。仅核长度及选窗，不另造全件哈希账。

## 本轮复核或纠正

**派发简写地址纠正：不存在本题所称两次私有helper调用。** 原字节 `adc7c: efe04d8f` 的JAL目标为 **`0xa008bd70`**；`adc84: efe0cde4` 的JAL目标为 **`0xa008c2d0`**。不是 `0xa00abd70` / `0xa00ac2d0`。P15原报告写的是正确的a008目标，错误来自后续派发地址转写。本轮据真实指令收缩为两个公开timer API的业务接线，不分析两个无关a00a函数。下面两个调用收到的是timer T，**均不是摘要S实参**。

正式callback留存为主树 `evidence/rea-0041-20261017/evidence/whole-rom-private-20261023.evidence.json#/records[parameters.procedure="0xa00adabc"]`，Evidence `ev_19e11c8fc1582881b289f2b24c2a98bbb305f7c2e57caad784442a60d1fb76e5`；ctor `0xa005cc1e` 为 `ev_2f6c46cd278b33760dc15702309279178fd3b14a0bef128e4814088addec2866`，业务callback `0xa00ad602` 为 `ev_9a7754188b853599f5646fcd698e04fa0a888175362857916605f5ae6e3478f0`。实际provider Ghidra12.1.4、语言 `RISCV:LE:32:ap01thead2`、profile digest `b6368dd18431e8113aa5026c713d41e648ab0f6ddd9421ff6c4a49e23b3cd2f3`。报告只恢复所列标准指令窗；vendor extu/port解码沿E04/E13接受前提，不运行模型。

adabc旧伪代码会删除包括adc04在内的unreachable块，value-flow有is_dead项；不能据此说在线块永不可达，也不能把死标记忽略后宣称运行已发生。本轮依据原assembly的显式条件边建立**满足前提时的静态路径**，不证明某次运行满足门。反编译无参数`a008bd70()`也不作ABI依据：`adc6a`已把T装入a0，76/78/7a只操作a5，7c前a0未改。reset在80重读S+f4到a0后调用；两个API之间不缓存原T句柄。

公共reset只查所需正常非NULL效果：`a008c31c`保存入参T到s1，`c31e→a008b17e`取已有tick API值，`c322 C.SW a0,4(s1)`写T+4，`c324→a0087b06`通知。即重置上次运行tick，不改成立即同步调用ad602。此12B必要API效果窗来自本轮ROM/Capstone5.0.7，无新REA Evidence ID；coverage记载其完整extent为c2d0..c331、98B，源路径候选lvgl、无dossier/historical contract。本轮不展开NULL诊断或公开timer内部；该extent不当作完整API认证。

## 真正新增：在线接入阶段的可实施合同

### 输入门与对象桥

`0xa00adae8/0xa00adaea`将a0/app保存为s6、a1/item保存为s2。app或item为空分别走日志/返回；动画计数非0时，将item.word0写app+54，记录后返回，不进入在线初始化；app.byte4c为0也日志返回。这些门为继承的机会式更新限制，不提供排队/最终重放保证。正常port域沿既验解码，不将无效port的index=ffff当成受支持的正常输入。

`adc20 child(app,0)`返回child；`adc24 LW child+10→wrapper`、`adc2a LW wrapper+4→s1=S`。这里S是现有child0摘要上下文，非app/item/详细panel。构造桥沿P07并复核必要窗：`s3=s2+80`，`da50 a2=s2`、a0=ad602、a1=3000→da5a创建T；da5e写s3+74即S+f4，da62暂停同返回a0；da6c写S到wrapper+4，da74写wrapper到child+10。ad61e `C.LW s1,c(a0)`将T.userdata取回S。以上桥连接同一个业务对象；没有靠相同偏移猜测两个ctx相同。

### 变化判定、初始化、timer动作与汇合

令 `i=u16(port-1)`、`new=u8(item+d)`、`old=u8[62fc403c+i]`。s4在adc08为62fc4000，在adc36加2c，所以下表相对全局地址均按62fc402c解释。

| 门/原地址 | 正常业务动作，保留原序与位宽 |
| --- | --- |
| adc3a，new==old | 直接adcd0常规更新；不清槽、不resume、不reset、不重新保存相同状态 |
| adc3e / ae196..19a，old!=0且new!=0 | 跳adcc4只保存新活动byte，然后adcd0；不能把非零→另一非零当首次接入 |
| adc42，old==0且new!=0 | 进入adc46首次接入块；当前正常状态域内这是唯一执行以下初始化的门 |
| adc46 | 调既有 `a00a769a()`，本题不展开其内部通知业务；本地不以返回值判成败 |
| adc4a..66 | 先 `u8[62fc4054+(u8)i]=1`，再依次SB0到S+9d+i、S+101+i，**SH0到S+fa同时清fb**，SB0到S+fc+i。摘要数组用u16 i，全局4054数组用u8 i，不能统一宽度 |
| adc6a..7a | 先LW T=S+f4，再 `u8[62fc403a]=1`；LW T+14，AND1，bit0==0跳adca4，跳过resume及reset |
| adc7c..84，原bit0!=0 | `resume(T)`；其返回后**重读**S+f4作为T2，再`reset(T2)`。没有成功判断、回滚或timer重新分配；不得从正常同句柄推成允许省掉重读 |
| adca4..cc0 | 两条timer路径都记录接入日志；本块没有直接同步调用ad602 |
| adcc4..ccc | 从frame-d4重读new，SB到62fc403c+i，然后adcd0；不能在resume之前提前存old数组 |
| old!=0且new==0 | 走已验P07/E13离线阶段；同步重算后仍条件pause、清FA/FB、保存新活动，再汇入同adcd0 |

此块不写S+f8/+f9，也不整体清S+9c位图或初始化全部五槽；只清当前i的三个槽及FA/FB。不能把“新接入”写成重置整个轮转游标。timer状态在API内部按其公开边界改变；本地只用bit0门，不把其他状态位解释成业务状态。

以下为说明性伪代码，**不是原源码**，仅展开本次在线分支，离线/动画段沿既验合同：

```c
S = load32(load32(child(app,0)+0x10)+4);
old = load_u8(0x62fc403c + i);
if (new != old) {
    if (old == 0 && new != 0) {
        notify_a00a769a();
        store_u8(0x62fc4054 + (uint8_t)i, 1);
        store_u8(S+0x9d+i, 0);
        store_u8(S+0x101+i, 0);
        store_u16(S+0xfa, 0); // also FB
        store_u8(S+0xfc+i, 0);
        T = load32(S+0xf4);
        store_u8(0x62fc403a, 1);
        if (load_u32(T+0x14) & 1) {
            resume(T);
            reset(load32(S+0xf4));
        }
        // original logs
    } else if (new == 0) {
        offline_P07_before_common_save(); // accepted actions; shared save remains below
    }
    store_u8(0x62fc403c+i, new);
}
regular_notification_update(); // starts at adcd0, not an unconditional successful render
```

### 常规更新接缝、暂停与所有权

不是初始化后return：adcd0重新读旧设备类别 `u8[62fc4041+i]`，adcd8读item+21、adcdc读item+e；add16将原port-1截u8作4054数组索引，add24要求该全局byte恰为1，add28/2c又要求boot/init全局62fc4038恰为1，满足后add30以item+c是否为0选择普通/安心分支，否则转ade8a后续事件mask更新。故首次接入置4054并不足以保证当次分类已执行，更不足以保证S+101非0或有可显示摘要。旧活动相同仍可进入同一常规消费路径，**本段不会为仍暂停的timer自动resume**。

与P07组合的真实生命周期是：构造T并pause → 正常零到非零接入时条件resume/reset → 公开timer有机会以T+c=S进入已验P11选择及P13/P15输出 → 旧非零到零时P07同步重算后条件pause → 下一次零到非零再按上述门激活。P07即使尚有其他摘要槽非0也最终条件pause，因此“其他端口仍在线”不保证timer持续运行；同活动通知不能补回该活性。这是原静态合同的限制，不建议悄悄改变。3000是创建周期实参，复位后实际下一tick时间、通知器是否立即驱动调度器、线程串行性或物理屏幕结果没有实测。

S、child/wrapper、已有控件、T均从已构造图借用，item仅本次通知读取。在线接入块无分配/free、timer删除、userdata替换或新指针持有；没有保存item指针。NULL/失败门只有上述app/item入口；child/wrapper/S/T本地没有检查，不能补造成可恢复错误/成功返回码。本块无超时、取消、撤销或完整退出；pause保留T。新实现如需要复制异步item、在存量在线通知时修复timer或保证重新调度，应标产品策略，不得归为原ROM已证行为。公开timer/LVGL可用自有适配，不需继续逆向其内部。

## 未闭精确边、实际检查及合并复核

尚未闭合的是**adcd0之后的设备分类/状态槽生产 → S+101..105的有效值**，并非已经接受的P11选择或P13/P15输出。该callback里真正writer `addfc SB3→S+101+(port-1)`、`ae442 SB4`及安心分支另有1/2写入，后续事件mask还可再次改槽；仅找到store不能宣称完整合法值来源已验。本报告只核到add38的常规分派门，未把上述writer的全部条件、资源借用/持有及后续覆盖认证。全体writer、最终销毁/并发、实际timer调度继续未知；不追无种子主W退出、不扩全UI。

**唯一后继建议：** 从 `add16..38` 的普通/安心分派及 `addfc/ae442` 两端实际writer入手，恢复item+c/d/e/21与必要item+30资源到同S+101槽值、后续mask改写的正常分类阶段，止于传给已验P11的五槽输入合同，预计25–35分钟；先查旧charge-complete/较晚ctk报告的同对象覆盖。不要逐个writer拆任务，不重做popup/UI库内部或已验固定输出。本作者不接后继。

[verify.py](../../analysis/app-online-lifecycle-p18-0041-20261024/verify.py)只读原ROM、旧private bundle和coverage，写[evidence.json](../../analysis/app-online-lifecycle-p18-0041-20261024/evidence.json)、[checks.json](../../analysis/app-online-lifecycle-p18-0041-20261024/checks.json)。实际PASS：11个稀疏留存窗434B/122条边界与ROM连续映射；原寄存器/读写宽度/offset锚、JAL绝对目标、8条条件边核对；另12B公共reset正常效果。三条record的实际profile核对通过。未复制整adabc/ctor或重写全解码框架。Capstone5.0.7只作标准静态解码，保留旧assembly并人工核路径，不是指令执行、全函数等价或数据流形式证明。

第一次自检把已验ad61e userdata目标寄存器误录s10，实际ROM/留存均为s1，断言拦下后更正，最终通过；不影响对象桥结论。初始两次登录shell覆盖cwd导致只读未命中，后续显式Set-Location及绝对路径纠正，错误目录未写入；较宽profile预览截断后未作为完整证据。没有运行其他作者脚本。

交由一个新非作者一次合并复核P18差集：正确a008目标、在线零→非零门/非零→非零保存、同S与T身份、初始化顺序/宽度、原paused-bit门、resume后句柄重读/reset、公共保存与常规分派门，以及P07/P11/P13/P15接缝与本报告完整接口未闭限定。作者自核不代表独立接受。

交付检查UTC `2026-10-24 15:15:59`；从首个UTC起墙钟8分52秒，范围收敛提前交付。工具等待计入墙钟，无主动等待或任务中断，没有有效工时单独测量，不以墙钟冒充有效工时；token由父窗统计。本轮48项选定原字段/直接目标/条件边检查PASS，2JSON解析、11条本地引用、4文件尾换行/无尾空格及git diff --check通过；git status仅本报告与同名analysis独占路径。必要body重读、继承ctor及公共API效果认证均不计新增业务函数。作者交付后停止。
