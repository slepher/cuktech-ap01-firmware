# T01：repeat_count=0 后的 timer 归还接入复用

2026-10-24；基线 `09e11d0`，独占分支 `codex/re-0041-t01`。**主体已由G05/G06覆盖：callback返回后，scheduler先检查全局删除标志；未删除时重读repeat，等0才按auto-delete位选择删除或暂停。** I01/I02的boot callback使用同一已核构造器/字段，可接到此旧合同，无需再导出scheduler或delete helper。新增ROM功能0、原字节窗口0、开源排除0。

采用 [reverse-engineer-anything 技能](C:/Users/cogic/.agents/skills/reverse-engineer-anything/SKILL.md)，只读既有证据和本地候选最少命名行；没有读ROM、运行历史验证器、开共享REA target/database或新增反编译。无固件、SIM、构建、回放、设备、外网、下级agent及异常/并发/缺陷测试；只写独占报告/analysis，不改共享/主树/生产ROM、配置或模型。

## 继承结论：已有→行为→局限→实际缺口

|既有出处|已解释行为及证据层次|本题处理|
|---|---|---|
|[I01](boot-ready-increment-i01-0041-20261024.md)、[I02](boot-ready-review-i02-0041-20261024.md)|boot经`a008bc64(a00a7472,1000,P)`构造timer；P独立1B userdata。callback完成链先`a008c280(timer,0)`，后`a008ab8a(P)`，不直接free timer|原字节/独立复核合同全继承，不重做boot/private callback或完成条件；旧“最终timer归还未知”须对照既有scheduler覆盖|
|[G05](display-event-flow-g05-0041-20261023.md)、[G06](display-event-review-g06-0041-20261023.md)|同`a008bc64`初始化repeat=-1、flags byte+14清bit0/置bit1；timer进入`62fc95f0`链。`a00804e2`正常迭代包括callback后repeat/auto-delete门，G06已独立接受|这不是仅display专用的字段解释。直接引用已核同构造/全局链/泛型timer形参，不重新查全ROM caller或导出函数|
|G06对G05的纠正3与callback后接受项|now→callback快照→last_tick发布→按旧repeat决定是否回调；返回后先查删除byte再重读当前timer|必须保留原序。不能把callback后timer恒有效、同次必立即free或任意对象不被改写作为通用保证|
|G05/G06 `a008ae58`短资源边|同timer先摘链，写删除标志`62fc95fe=1`，再free timer；删除helper没有替boot释放userdata|全继承，不重做链/allocator/标志/free；timer与P是两个分配根|
|I01引用的system/guide complete、buzzer round2既有setter合同|boot原timer/回调汇编已有，`a008c280`原日志/字段支持repeat_count setter；SIM固定2000ms仅替代|完整旧流程不重复读取/导出；不把SIM替代当真实调度或归还观测|

本题初始缺口经复用对照已收窄为**I01对象与既有G05/G06正常归还门的接入说明**，没有新的未分析scheduler入口或必要字节缺口。

## 本轮复核或纠正：既有门与对象的连接

以下地址/指令均来自G05留存，接受强度以G06为准；本轮只核旧JSON中的7锚点/2直接边及相关报告一致，不把它说成新原字节验证。[reuse-evidence.json](../../analysis/timer-repeat-release-t01-0041-20261024/reuse-evidence.json)保留复用索引及25行最少候选命名材料。

|既有接入地址|继承正常合同及I01连接|
|---|---|
|`a00805a0..05c6`|原repeat为正先减1；now返回→取callback快照→写last_tick。旧repeat非0且callback非空时`05c4`以a0=s2=当前timer调用`05c6`保存callback。I01的callback在这一generic timer ABI上接收timer，不是以P作为callback形参|
|`a00805c8/05cc`|先读全局删除byte`G+82=62fc95fe`；非零跳至后续迭代控制，跳过本块对当前timer的repeat/flags读取。不能无条件在callback返回后解引用timer或删除第二次|
|`a00805ce/05d2`|删除标志为0才重读word[timer+10]；非零则绕过本次删除/暂停分支。这里使用callback返回后的新值，故I01在callback内把repeat置0可进入此门；不是继续只用调用前的旧repeat|
|`a00805d4..05dc`|repeat=0后LBU flags@timer+14，a0=s2，AND2；bit1非0走删除，bit1为0走暂停。auto-delete门**存在**，不能省略成repeat0无条件free|
|`a00805de`|JAL至`a008ae58`，实参仍为同timer基址；其摘链→删除标志→free合同直接继承G05/G06。没有把P作为该call实参|
|`a00805f4/05f8`|bit1为0时调用`a008bd16(timer)`暂停，再汇入同后续迭代控制；不free timer。后续扫描/重启和统计不属于本题，无需展开完整调度器|

因此I01正常完成链可作如下**继承合同的分析表达**，非新恢复原源码，也不表示观察到实际调度：

```c
// I01/I02已有callback：repeat(timer)=0; free(P); return;
// 回到同a00804e2，且其原到期/非暂停等入口条件已满足：
if (global_timer_deleted == 0) {
    if (load32(timer + 0x10) == 0) {
        if (load_u8(timer + 0x14) & 2)
            a008ae58(timer);   // 继承：摘链→标志→free(timer)
        else
            a008bd16(timer);   // 继承：暂停；保留timer分配
    }
}
// 后续按原调度器迭代门处理，本题不展开。
```

`a008bc64`初始化bit1=1已由G05/G06核实；I01所用setter只写repeat，不等于立即free或清auto-delete。若执行至该正常返回门时仍保留已核构造默认bit1，且删除标志为0，则走删除分支；若该位当前为0则暂停。没有运行时证据证明任何实际实例在此刻必保持默认位，也不穷举所有改位者或私有callback副作用。P已在callback内归还，timer节点随后由scheduler归还，责任不能合并或重复释放。

## 真正新增与候选命名强度

新增功能0、语义纠正0、ROM窗口0、完整函数导出0。新增只有把I01/I02保留的“最终timer归还未知”对接到早已核实的G05/G06合同；不是重新发现timer删除机制。管理者确认主体旧覆盖后按书收缩，不为闭包额外取scheduler/delete窗口。

候选根继承既有本地LVGL9.2.1参考背景，仅固定读取`src/misc/lv_timer.c:175–180,228–231,339–350`及`lv_timer_private.h:35–37`共25行：构造repeat=-1/auto_delete=true，setter写repeat，条件`!timer_deleted && repeat==0`后auto_delete选择delete/pause；header以repeat_count/paused/auto_delete命名字段。这只支持命名及分支意图相容；没有扩展包/版本来源认证，候选uint32位域声明不认证ROM的byte访问宽度、完整结构或配置。原ROM门及偏移仍全来自G05/G06，不用候选替代。

## 未闭精确边与实际验证

仍未知实际scheduler调用时刻、当前timer是否到期/暂停、运行期删除标志与auto-delete位状态、所有改位者、外部callback副作用及真实heap复用。boot/P正常责任与旧资源合同已说明，但不证明固定2秒、硬件ready、系统并发或整个timer调度器完成。不存在需要继续全ROM timer/IRQ扫描才能交付本题的必要缺口。

[reuse.py](../../analysis/timer-repeat-release-t01-0041-20261024/reuse.py)通过：旧G05 JSON的7锚点/2目标、G06已接受条款与I02责任边界一致；WSL已授权require_escalated只读25行候选命名材料。没有执行G05/G06/I01/I02验证器或候选，未读ROM、未重新核原字节。JSON、报告链接及`git diff --check`通过。

本题按已有覆盖结束，后继不再派相同repeat0→scheduler→delete研究；若今后有具体实例改auto-delete或正常激活/注销的真实种子，另以该实例的字段写入/调用接入为界。本轮不自行接题，也不扩全部timer/IRQ。
