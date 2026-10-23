# T02：repeat0后timer归还接入独立复核

**限定接受T01的复用衔接与运行时限定，语义纠正0、新增功能0。** I01/I02的boot timer使用同一已核构造器；callback设置repeat0并释放P后，可接入G05/G06既有post-callback门。删除标志、重读repeat、当前auto-delete位的条件不能省略，构造默认bit1不能提升为所有时刻的保证。P和timer是两个分配根，由不同责任方归还。

2026-10-24；基线 `75f977a`，独占树/分支 `re0041-t02` / `codex/re-0041-t02`。复核者未参与T01生产，采用reverse-engineer-anything技能。本轮只读既有报告/证据JSON，不读ROM、不反汇编或重导窗口/函数、不读取候选库/WSL、不运行旧验证器/模型/固件/SIM/构建/回放/设备/外网，不打开共享REA target/database，不创建下级agent。仅写本报告及同名analysis，不改共享/主树/生产ROM配置模型或他人成果，不再写旧树。伪代码是继承合同的分析表达，非原源码或运行观察。

## 继承结论：已有 → 行为 → 局限 → 本题缺口

| 已有出处 | 已解释行为/证据强度 | 本轮处理 |
| --- | --- | --- |
| [T01](timer-repeat-release-t01-0041-20261024.md)及`reuse-evidence.json` | 已将boot对象连接到原scheduler后处理；7旧锚点/2直接边；无新ROM功能/窗口 | 只独立核复用来源、对象身份衔接和限定强度，不重新技术验收整个scheduler |
| [I01](boot-ready-increment-i01-0041-20261024.md)/[I02](boot-ready-review-i02-0041-20261024.md) | `a005ce98`以callback=`a00a7472`、period1000、P调用`a008bc64`；callback从timer+c取P；完成链`a008c280(timer,0)`→`a008ab8a(P)` | 独立引用I02已验调用/字段结果；P为1B userdata，不是timer/root/config缓存。私有boot条件、完成helper和窗口删除直接继承，不重复恢复 |
| [G05](display-event-flow-g05-0041-20261023.md)/[G06](display-event-review-g06-0041-20261023.md) | `a008bc64`的callback/data/repeat/flags及同`62fc95f0`链；scheduler泛型timer形参，paused/elapsed/old-repeat/callback门与返回后清理已有独立验收 | 同构造器/全局链/泛型timer接入有既有依据，不是仅凭字段相同就猜boot套display。G06三项原序纠正优先，未展开统计/IRQ/所有timer |
| G06 callback后接受项及`a008ae58`资源边 | 先读删除byte；未删除才重读repeat/flags；repeat0按bit1删除/暂停；删除helper先摘链→置删除标志→free(timer) | 全继承；helper没有替boot承担free(P)责任，不能把repeat setter或callback本身说成直接free(timer) |
| T01原25行本地LVGL候选材料；I01旧complete/最终ZIP复用 | 候选构造/setter/auto-delete意图仅支持命名；SIM固定2000阈值是宿主替代 | 不重读候选，不把uint32位域或源码命名变成ROMbyte宽度/完整ABI/版本认证；不重跑SIM或ZIP资料 |

证据分层保留：I02/G06已验收原字合同直接引用；旧JSON只在接入锚点上交叉一致核对；SIM/照片/候选是替代或参考；实际调度/字段状态无观察继续未知。本题没有新的缺失scheduler入口，只有T01来源接线的独立接受需求。

## 本轮复核或纠正：逐项接受

[review_reuse.py](../../analysis/timer-repeat-release-review-t02-0041-20261024/review_reuse.py)直接读G05 `evidence.json`、G06独立 `evidence.json`、I02独立 `review-result.json`和T01复用结果；不导入任何旧脚本。结果 [review-result.json](../../analysis/timer-repeat-release-review-t02-0041-20261024/review-result.json)只保留接入索引/一致性与限制，不再导出scheduler/delete/boot本体，不虚构新REA Evidence ID。

| T01项目 | 本轮判定与可定位依据 |
| --- | --- |
| **boot对象能接到既有generic timer合同** | **接受**。I02已验`JAL a005ce98→a008bc64`，`a00a7488`为LW P,[timer+c]；G05/G06已核同constructor设置callback/data并入公共timer链。原scheduler以a0=s2当前timer调用callback，因此boot收到timer而不是直接收到P。仅这条正常对象接入，不保证实际到期或被调用 |
| **保留G06 callback前纠正顺序** | **接受继承**。`05a0`保存旧signed repeat，正数先减写；`05b0` now返回→`05b4`callback快照→`05b8`发布last_tick；`05be/05c0`检查保存callback与旧repeat，`05c4/05c6`传同timer间调。T01没有把旧repeat与callback后新repeat混同，也未重读callback执行 |
| **callback后删除标志门先于当前timer重读** | **接受**。T01/G05/G06三方的`05c8: LBU G+82`锚点一致；G06独立目标`05cc→05e2`。非零绕过本块repeat/flags读取；不能无条件在callback返回后解引用当前timer或再删除一次。这里继承正常scheduler合同，不主张callback后timer恒存活 |
| **repeat重读与auto-delete当前位选择** | **接受**。三方`05ce: LW timer+10`、`05d4: LBU timer+14`、`05d8: a0=s2`、`05da: ANDI2`一致；G06已验`05d2`非零→05e2，`05dc`零→05f4。只有新repeat==0才继续；bit1非零`05de→a008ae58(timer)`，为0`05f4→a008bd16(timer)`暂停，非无条件释放 |
| **默认bit与运行时界限** | **接受**。G06已核constructor清flags bit0、置bit1、repeat=-1；I02已核setter只以(timer,0)接入。T01明确写“没有运行时证据证明任何实际实例在此刻必保持默认位”。未穷举所有改位者或callback副作用；不将默认值、静态门或候选auto_delete=true提升为本实例一定立即归还 |
| **P与timer分根释放责任** | **接受**。I02已验`7546→a008c280`在`754c→a008ab8a`之前，实际free实参为P；timer删除实参来自scheduler当前s2。G06既有`a008ae58`摘链/标志/free不处理userdata。P在boot callback内归还，timer仅在随后满足上述门的scheduler路径归还，或按另一分支暂停；不能合并为同一次free或假定userdata随timer自动释放 |

上述6项限定接受，技术语义纠正0。本轮对照7个T01/G05/G06相同锚点、5个G06已接受控制边、4项I02已接受身份/调用结果；它们是旧证据复用一致性检查，不是再次从ROM独立证明旧整个调度器。

```c
// 继承I01/I02正常完成callback：set_repeat(timer, 0); free(P); return;
// 继承G06已经通过其入口/到期/callback门后的局部控制：
if (global_deleted_byte == 0) {
    if (load32(timer + 0x10) == 0) {       // callback之后重读
        if (load_u8(timer + 0x14) & 2)    // 当前位，不是缓存的构造默认值
            inherited_delete_timer(timer);
        else
            inherited_pause_timer(timer);
    }
}
```

这段表达不承诺每次完成callback都立即释放timer，不认证正常执行的墙钟时刻、是否到期/暂停或其他callback造成的全局状态。没有从host固定2000阈值推出原ROM时间保证。

## 真正新增与实际验证

新增ROM功能0、ROM读取/原字窗口0、完整函数导出0、候选源码读取0、ISA/模型变更0、精确来源排除0。交付只是T01复用衔接的独立接受；I02/G06已有技术验收不重计，T01候选25行保持纯命名/意图参考等级。

执行 `python -X utf8 -B reverse/analysis/timer-repeat-release-review-t02-0041-20261024/review_reuse.py`：PASS，7三方锚点、5既验控制边、4已验身份结果及报告运行时限定检查；JSON解析、报告相对链接和`git diff --check`通过。没有运行G05/G06/I01/I02/T01验证器，没有重新字节取证或将旧工具结果冒充新REA执行。

## 精确未闭边与后续边界

实际scheduler调用/到期时刻、当前deleted与auto-delete位、所有改位者、外部callback副作用、真实heap复用、精确源码/版本仍未知。P正常责任和条件timer归还接入已有可定位答案；这些未知不能倒退成同repeat0门未恢复，也不能由构造默认位补齐。

本题已有覆盖并已获得限定接受，**不再派相同repeat0→scheduler→delete研究**。只有未来出现某个具体实例的auto-delete改位、正常激活/注销真实调用种子，才建议以该实例的字段写入/接入为界核对；本轮没有新种子，不扩大timer/IRQ/候选库扫描，由管理者决定换题。
