# P-18 在线摘要接入的独立复核

**可独立使用阶段已闭合但接口未闭；P-18 在线差集限定接受，行为纠正0，新增业务恢复0。** 已接受正常有效端口在旧活动0→新活动非0时的入口门、child0/S身份、当前槽初始化、按原paused bit条件resume/reset、重读timer句柄、共享保存及常规更新分派。不能据此认证全部五槽生产、通知必重启、即时tick或完整应用生命周期。

复核者 `/root/app_summary_review_01` 非作者；基线实际核对 `5bbc331ab429fb76e956e50b8081c56f8d278b11`。依据管理记录2026-10-24 23:44 HKT小节及P-18行，读取统一流程3.1/3.2/5.1/7，应用 [REA技能](C:/Users/cogic/.agents/skills/reverse-engineer-anything/SKILL.md)。按本次派发只写主树本报告与同名analysis，不建worktree、不改共享表及作者文件，不提交推送；其他研究者的成果未撤销。未运行目标/模型/SIM/QEMU/构建/回放/设备/网络，没有改ROM、生产、配置或分析器，未创建下级代理或切换共享REA。

预估6–10分钟：定位1–2、原字门与调用3–5、交付2–3；参考已定位P17约6分钟/P15约4分钟，证据已定位，允许提前收敛。UTC开始 `2026-10-24 15:45:29`，结束见文末。

## 继承结论

- [作者P-18](app-online-lifecycle-p18-0041-20261024.md)仅作为待验命题和定位，未运行或导入其verify脚本，未以作者checks/evidence代替独立判断。曾只读其verify前段了解输入定位，本次复验源码独立编写。
- [P-R07](offline-summary-review-pr07-0041-20261024.md)已接受同child0摘要S、create(ad602,3000,S)→S+f4、初始pause，以及离线清槽/同步tick/条件pause和共享保存。E13正常port解码、u16(port-1)及item+d新活动、P03/P-R02动画门与机会式缓存沿既验范围继承。
- P-R11已验timer+c→S和五槽轮转；P-R13/P-R15已验输出和摘要pane行为；G05/G06的公开timer边界继承。本次不重新认证这些完整主体，不把旧SIM概念当ROM新增。
- 原件沿CATALOG：`roms/0041/ap01-1.0.2_0041.bin`，6,769,704B，SHA256 `972db4c136c7ed9e24a83c07c1a7fd62040ca018b08ca285216d26b1fee3c6b9`；RV32 LE，offset=VA−0x9ffff000。本次独立核长度与必要原字窗，不重复全件hash清单。

## 本轮复核或纠正

直接来源为 `evidence/rea-0041-20261017/evidence/whole-rom-private-20261023.evidence.json#/records[parameters.procedure=...]` 原assembly及原ROM。三记录profile均独立核为 `Ghidra12.1.4 / RISCV:LE:32:ap01thead2`，digest `b6368dd18431e8113aa5026c713d41e648ab0f6ddd9421ff6c4a49e23b3cd2f3`。

| procedure | Evidence ID |
| --- | --- |
| 0xa00adabc | ev_19e11c8fc1582881b289f2b24c2a98bbb305f7c2e57caad784442a60d1fb76e5 |
| 0xa005cc1e | ev_2f6c46cd278b33760dc15702309279178fd3b14a0bef128e4814088addec2866 |
| 0xa00ad602 | ev_9a7754188b853599f5646fcd698e04fa0a888175362857916605f5ae6e3478f0 |

| 差集 | 独立验收 |
| --- | --- |
| 入口及对象 | 接受。adae8/ea保存app/item为s6/s2；adb02/3e空指针门，adb5a非零动画分支经item.word0→app+54后日志返回；adba4/8要求app.byte4c非0。adbf6/f8传(child app,0)，adc20后child+10→wrapper+4→s1=S。 |
| 活动分支 | 接受。adc32从62fc403c+i取old；adc3a相等直接adcd0，adc3e旧非0→ae196，ae19a新非0→adcc4保存；旧0且新非0才通过adc42进入adc46初始化。不把非零换非零当首次接入。 |
| 清理原序/宽度 | 接受。adc46先调用a00a769a；adc4a截u8 i，仅用于62fc4054数组置1；adc56以原s8构S+i，依次SB0到+9d、+101，SH0到S+fa同时清fb，SB0到+fc。并非清所有五槽/位图或f8/f9。 |
| timer参数及门 | 接受。adc6a先LW a0=S+f4即T，adc6e置62fc403a=1；adc76 LW T+14、AND1，adc7a为零跳adca4。原bit0非0才有两次API调用；不因通知一定执行resume。 |
| 正确调用及重读 | 接受作者对旧派发的纠正。adc7c原字`efe04d8f`独立JAL立即数得a008bd70；adc84 `efe0cde4`得a008c2d0，均rd=ra。adc7c前a0仍为T；adc80重读S+f4到a0后才reset。不是a00abd70/a00ac2d0，也不是将S作为API参数。 |
| 公共API正常效果 | 接受，止必要API边界。原ROM bd7a非NULL→bdbc，`83474501/f99b/230af500`为读取T.byte14、AND−2、写回byte14，bdc6通知a0087b06。c2da非NULL→c31c保存T到s1，c31e调用a008b17e，c322 `c8c0`写返回a0到T+4，c324通知同服务。只认证公开resume清bit0/reset记录已有tick；无同步ad602或立即调度保证。 |
| 保存与常规分派 | 接受。adcc4从frame−d4重读new，adccc以SB保存到62fc403c+i；随后adcd0读旧类别及item+21/e。add16对port−1截u8供4054，add24要求该byte=1，add28/2c还要求62fc4038=1，add30/38才按item+c分派。不因首次置4054保证全部分类/输出。 |
| 构造与回调桥 | 接受必要继承前提。da14 s3=S+80；da4a/52给3000、da4c/56给ad602、da50 a2=S；da5a create，da5e存S+f4，da62同返回T pause；da6c/74接wrapper与child。ad61e从T+c取回s1=S，不混入app+58的timer。 |

原adabc反编译删除unreachable块，不能据其死标记否认上述明确assembly路径；本次结论均是满足入口/活动前提时的静态路径，未观察任何实际执行。厂商port解码沿既验前提，不运行指令模型，也不宣称完整函数等价。

本阶段从既有对象图借用S/child/wrapper/T，无分配、free、timer删除或item指针持有；本地不检查child/wrapper/S/T的NULL，不应补造可恢复错误码/回滚。公开API非NULL正常效果核查不等于认证其完整错误/诊断实现。生命周期组合为构造pause→零到非零条件激活/复位→公开timer机会性进入已验callback→离线同步更新并条件pause→后续零到非零再激活；相同活动通知不恢复已暂停T。

## 真正新增

新增业务恢复0；新增非作者限定验收。独立 [audit.py](../../analysis/app-summary-review-01-0041-20261024/audit.py)读取原件/原留存，静态Capstone5.0.7解码标准指令，另用独立位字段公式核RV32 JAL/branch及RVC条件跳转。[audit.json](../../analysis/app-summary-review-01-0041-20261024/audit.json)保存稀疏窗、原字、对应原留存文本、来源和检查，不复制整个函数。公共API必要窗仅有ROM/Capstone来源，无新增REA Evidence ID。

实际16个稀疏窗458B/136条标准指令、75项选定字段/宽度/参数、直接目标及条件边检查PASS；不能把解码条数当完整语义证明。原留存与ROM指令边界核对，具体业务结论结合人工顺序/对象流核查。没有全ROM负搜或新业务callee扩展。

## 未闭精确边

1. `0xa00add16..38`普通/安心分派之后，`addfc SB3`、`ae442 SB4`及1/2/事件mask后续写入到同S+101..105的全部合法值生产和覆盖顺序未验。因此“在线输入→正确五槽摘要内容”的完整接口仍未闭。唯一后继保留作者种子：合并恢复该正常分类阶段，止于P-R11已验五槽输入，不逐writer拆任务、不下探公共LVGL。
2. 实际下一tick时刻、通知调度的即时性、并发/最终销毁、异常指针/创建失败及物理显示仍未知。本轮不追无种子主W退出，不把正常借用关系推成唯一owner证明。
3. 接受P-18在线阶段不等于接口全闭、全部UI生命周期或整个ROM恢复完成；P-R07离线与其他既验合同的局限继续保留。

计量：首次UTC与结束的差值为墙钟，工具读写和进程启动包含其中；无主动等待/排队或任务中断，无有效计算工时实测。首个reverse-design相对路径未命中，只读失败，随后找到实际路径；未写错误目录。Token由父窗本轮遥测快照统一统计：input、cached input单列、output/reasoning按可见实测；本子代理未获取数值，不估计。最终检查/UTC见交付记录。

交付检查结束UTC `2026-10-24 15:48:44`，墙钟3分15秒，比预计6–10分钟提前收敛；差集和原留存充分定位，无等待凑时。75项静态断言、JSON解析、全部报告相对本地引用、3文件尾换行/无尾空格及限定路径git diff --check通过。独占产物为本报告、audit.py、audit.json（JSON受既有Git忽略，仍保留原路径）；未暂存/提交/推送。交付后停止，管理表和后继由父窗处理。
