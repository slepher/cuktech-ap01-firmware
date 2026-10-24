# P02：activity byte 与 idle counter 局部原序的独立接受

2026-10-24；基线 `a09959e`；独占树/分支 `re0041-p02` / `codex/re-0041-p02`。**限定接受 P01：主输入 SB1、callback 两次独立 LBU、两个零门、两个32位 counter 清零及最后清 activity 的字段/顺序成立。语义纠正0、新增功能0。** 中间诊断调用不能省略，两次读取不能合并；不认证跨调用 flag 稳定或真实经过秒数。

**认领 ID：P01/1（关联 P02/J07），唯一管理表补录基线 `02afb05`。** 主窗口已确认原作者 `/root/l03` 提交停止，复核者 `/root/l04` 未参与 J07/P01，P02只挂原认领、不新建研究。原件身份继承主仓 CATALOG 的0041记录；研究树基线仍为 `a09959e`，没有移动到新管理基线。

链条认领新规则到达时，本轮技术核对及文档检查已结束，随即停止新增 ROM 读取/反编译/沿链复核，保存已有成果；已读主仓最新[逆向流程全文](D:/Documents/PlatformIO/Projects/cuktech-ap01-firmware/reverse/reports/ap01/reverse-design.md)与[管理记录顶部规则及P01/1行](D:/Documents/PlatformIO/Projects/cuktech-ap01-firmware/reverse/reports/ap01/rolling-management-0041-20261023.md)。收到补录确认后只加认领/差集、整理检查并提交，没有继续读ROM或沿链复核；未修改共享认领表。本轮此前实际离线解码查看半开窗口 `[0xa00afd52,0xa00afd64)`、`[0xa00af78a,0xa00af78e)`、`[0xa00af79a,0xa00af79e)`、`[0xa00afa78,0xa00afacc)` 共110B，其中独立字段记录为20条/76B，无剩余原件读取需求。

|相交认领/旧合同|继承与真正差集|
|---|---|
|J07、P01/1|同一global activity→两counter精度问题合并在P01/1；P01作者已停止，P02差集仅为非作者独立接受，新增0，不另开同题研究|
|E05/1及E06|共享callback `0xa00af262`，只继承timer注册/borrowed app与DELETE范围；P01/1核的是独立global `0x62fc403a`/两个counter，不重验timer或app生命周期|
|guide父级、最终complete|阈值、唤醒/首事件消费、长按直接继承，不复核算法或运行验收|
|F11/1、G19/1–2|主窗口已确认对象、地址、连接及问题无交集，不扩大认领到这些链；未闭跨调用稳定、所有writer或真实节拍也不新派取证|

采用 [reverse-engineer-anything 技能](C:/Users/cogic/.agents/skills/reverse-engineer-anything/SKILL.md)。复核者未参与 J07/P01；未运行或导入 P01 检查器，也未使用其结果 JSON 代替原 ROM。只写本报告和独占 analysis；未执行ROM、SIM、模型、构建、历史回放、输入、设备或外部服务，没有漏洞/异常输入/缺陷验证，不改生产代码、ROM、配置、模型、共享REA、主树文件或他人修改，无下级 agent。

## 继承结论

|出处|已有覆盖|本题范围|
|---|---|---|
|[J07](input-idle-reuse-gap-j07-0041-20261024.md)、[P01](input-idle-activity-p01-0041-20261024.md)|旧 producer/consumer 的真实定位，s2与borrowed app区分；P01补原字段精度|仅作非作者独立接受，不重盘全部输入writer或重新恢复旧算法|
|旧 main-knob-round2 records[1]，`ev_daf583e6c481f2d7f53eb8443cd04003d53c22365147ac088957c1415a947da7`；system cached main|主输入 activity/唤醒接入及完整 handler 已留存|只核指定SB及直接wrapper目标，不展开唤醒/长按/全主键handler|
|旧 screen-host-append-20261020.json functions[4]，`ev_4cd9ffcadd54fe381d075066b194c8af6fb2cd7098d35012c9c14281446c9463`；guide-complete saver idle窗口|a00af262 callback及ScreenOff/ScreenSave旧阈值、门/算法早有|只核指定普通指令；不把带unreachable/extraout的整伪码当完整可信模型，不重导callback|
|[E05](ctk-app-close-e05-0041-20261023.md)/[E06](ctk-app-close-review-e06-0041-20261023.md)|1000ms T1注册a00af262、borrowed app userdata与局部DELETE已独立接受|timer/app生命周期直接继承，不重验；此片段s2是另一个全局基址|
|[最终complete](application-rehost-complete-0041-20261017.md)、J07的父级/较晚合同对照|唤醒首事件消费、3秒长按、idle阈值及SIM场景已有范围限定通过|不重跑、不重计，passed-in-sim不证明原ROM所有分支/输入驱动或真实计时|

原件只读路径 `D:/Documents/PlatformIO/Projects/cuktech-ap01-firmware/roms/0041/ap01-1.0.2_0041.bin`，映射 `offset=VA−0x9ffff000`。独占 [review.py](../../analysis/input-idle-activity-review-p02-0041-20261024/review.py) 从原件解算 RV32 I/S/B/J 与 C.LI/C.BEQZ 字段；[review-result.json](../../analysis/input-idle-activity-review-p02-0041-20261024/review-result.json) 仅保留必要稀疏记录与字段身份。没有新REA Evidence ID、完整函数/资源/源码导出或哈希账。

## 本轮复核或纠正

|P01主张|独立原字段/目标依据|判定与限制|
|---|---|---|
|主输入存byte1到0x62fc403a|`0xa00afd52` LUI rd=s6/upper0x62fc4000；`0xa00afd56` ADDI s11,s6,0x2c；`0xa00afd5a` C.LI a5,1；`0xa00afd5c` S字段f3=0/rs1=s11/rs2=a5/imm14；`0xa00afd60` JAL ra→0xa00a769a|接受 SB1@0x62fc402c+0x0e。同字段身份已证，不证明所有输入均经过此路径；wrapper内部直接继承|
|callback使用全局s2|`0xa00af78a` LUI rd18/upper0x62fc4000，`0xa00af79a` ADDI rd18/rs1=18/imm0x2c|接受 s2=0x62fc402c，不是timer的borrowed app；不套app成员偏移|
|第一读为U8，零时跳既有ScreenOff路径|`0xa00afa78` opcode03/f3=4/rd=a5/rs1=s2/imm14；`0xa00afa8c` C.BEQZ寄存器a5，位移独立解算→0xa00afb42|接受独立LBU/零门，零臂不执行当前直落clear；该目标不是函数return，旧ScreenOff内部后续连接不在本题重建|
|首次非零直落臂清第一counter，再调用诊断|`0xa00afa7c/0xa00afa80` LUI s1=0x62fcc000及ADDI−0x33c→0x62fcbcc4；`0xa00afaa8` S字段f3=2/rs1=s1/rs2=x0/imm0；`0xa00afaac` JAL ra→0xa008b51a|接受32位SW零及先写后调用原序。两者之间/之前的本地参数准备不改为第二counter写，不展开诊断内部|
|诊断后重新读取同activity，重构第二地址|`0xa00afab0` 与0xa00afa78的完整原I字段相同，再次LBU@0x62fc403a；`0xa00afab4/0xa00afab8` LUI s1=0x62fcc000及ADDI−0x338→0x62fcbcc8|接受独立第二次读取，不用调用前缓存值；两个counter地址相差4但分别构造，不误称同一counter|
|第二次零跳，不清第二counter/flag|`0xa00afabc` B字段opcode63/f3=0/rs1=a5/rs2=x0，独立目标0xa00afbec|接受第二个独立零门。零臂跳旧ScreenSave路径，不执行紧随的0xa00afac0/0xa00afac4；不推广该旧路径的全部效果|
|第二次非零才先清第二word，再清byte|`0xa00afac0` SW x0,0(s1)；`0xa00afac4` SB x0,14(s2)；`0xa00afac8` JAL rd=x0→0xa00af2a8|接受32位0x62fcbcc8→8位0x62fc403a清零顺序。最后是无链接跳共同尾声，不是新callee调用；不能交换或提前清flag|

原序的必要结论是：第一零门控制本直落臂的 `SW bcc4`；随后保留诊断调用；**重读**后由第二零门控制 `SW bcc8 → SB activity=0`。首次读为非零不能证明第二读非零，也不能把两个条件合成一次读取后的无条件双reset。本轮不研究诊断对flag的真实影响、并发/重入或缺陷。

这些是全局标志和计数的按值访存，本片段没有新的分配、free、指针保留或所有权移交。app/timer仍按E05/E06的借用/清理边界处理。原指令的SW/SB宽度不赋予原子性、串行化、counter正式结构名或物理时间单位；两个函数存在同字段访问也不证明它们已在设备上先后执行。

## 真正新增

新增功能、算法、ISA规则、来源认证、资源及整库排除均为 **0**。本轮交付仅是P01旧合同精度的非作者限定接受；无语义纠正。旧body、J07去重与别名纠正、阈值/唤醒/timer合同和SIM通过均不重计。

独占检查器实际通过 **20条稀疏原指令、76B；3个JAL目标（其中1个rd=x0）、1个BEQ、1个C.BEQZ**，另验证四个绝对字段地址、两LBU原字段相同与写/调用/重读次序。JSON、报告链接和差异另行核验。仅作原件静态字段解码，未运行P01脚本、目标、输入、模拟模型或历史验证器。

## 精确未闭

P01指定的 producer→同activity byte→两个counter门/重读/消费顺序可按本局部合同验收。完整callback刷新/其他阈值/对象分支、所有activity生产者、输入设备与真实节拍、跨调用flag稳定或并发保证继续不在此验收范围；不声称这些边已恢复或不存在。

本轮没有新必要功能种子，原20条窗口无需再次派同题。其他未闭领域的选择交主窗口；不因本局部没有新种子推论整个ROM完成，也不自动扩大到全输入、GUI、GPIO或全部writer。
