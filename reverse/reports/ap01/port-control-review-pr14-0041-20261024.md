# P-R14：P-14 请求提交与遥测呈现的合并非作者复核

**可独立使用阶段已闭合但接口未闭；P-14 本轮差集限定接受，无行为纠正、无作者返工。** 实际 UI 请求字节、提交门与同页遥测呈现可用于重建；未认证请求接纳或设备执行成功。两阶段接线成立不等于端到端控制确认成立。

认领 P-14，复核者 `/root/pr14`，未参与作者成果。基线 `5bbc331ab429fb76e956e50b8081c56f8d278b11`；独占树 `D:/Documents/PlatformIO/Projects/cuktech-ap01-firmware/.worktrees/batch-20261024-p/pr14`。只写本报告和 `reverse/analysis/port-control-review-pr14-0041-20261024/`；主树只读。计划约30分钟，可提前交；开始 `2026-10-24 14:53:34 UTC`，结束与实际墙钟见末尾。token 本工具不可得，交父窗实测统计。

采用 [REA skill](C:/Users/cogic/.agents/skills/reverse-engineer-anything/SKILL.md)，只读留存与原 ROM，独立 stdlib 原字段核验。不打开/切换共享 REA、不运行分析器或指令模型、目标、设备、网络、SIM、QEMU、回放或构建；不改生产、ROM、配置或模型，不创建代理，不提交推送。

## 继承结论

只读主树 `reverse-design.md`、管理记录顶部及 P-14 行。作者已停止，管理行已登记本非作者复核。查重范围为真实 `0xa00f61ae` 的 switch/safe UI 动作→setter→命令提交，以及 `0xa00f5288` 的同页反馈消费；不触及 P-12 历史 reader、P-13 摘要、N01 mode/cmd60 或 P-02 反馈生产的新恢复。

作者成果为主树 [P-14 报告](D:/Documents/PlatformIO/Projects/cuktech-ap01-firmware/reverse/reports/ap01/port-control-p14-0041-20261024.md)及同名 analysis 的四产物。本轮把作者 JSON 当定位/对照数据读取，未导入或运行作者验证器。

- [N01/NR01](D:/Documents/PlatformIO/Projects/cuktech-ap01-firmware/reverse/reports/ap01/mode-interface-review-nr01-0041-20261024.md)的 submit ABI：`cmd@0,len@1,payload*@4`；同步复制至活动区或四固定槽，去重/满槽可直接返回，没有请求级成功结果；源 descriptor/payload 不转移所有权。本轮只核本请求确实遵循该形状，不重新研究提交器。
- [E07](D:/Documents/PlatformIO/Projects/cuktech-ap01-firmware/reverse/reports/ap01/ctk-extra-consumers-e07-0041-20261023.md)的 safe setter `0xa01917d0`：raw 指针、word index 小于 u8 count、item 非空、item+0x24 bit6 门；提交 cmd63/len2/两个低 byte。本轮未升级 E08 原有限复核范围，也未重做 setter 本体。
- [P-R02](D:/Documents/PlatformIO/Projects/cuktech-ap01-firmware/reverse/reports/ap01/power-refresh-review-pr02-0041-20261024.md)的反馈生产：status bit10→I+0xc、mask0x10；R+7既有换算→I+0xa、mask8。I 与 mask 仅同步借用，应用应在 callback 内复制标量。
- `reverse/rehost/charge-complete-0041.json` 的完整 UI/SIM覆盖及 records18/19旧显示代码直接继承。SIM 服务 true 才更改持久勾选的合同不能覆盖原 ROM 实际动作顺序。

## 本轮复核或纠正

原件 `roms/0041/ap01-1.0.2_0041.bin`，长度实查 6,769,704B；SHA256沿 metadata、旧complete与handler subject一致的 `972db4c136c7ed9e24a83c07c1a7fd62040ca018b08ca285216d26b1fee3c6b9`，未重算整件hash。RV32 little-endian；`offset=VA−0x9ffff000`。

handler来自 `evidence/rea-0041-20261017/evidence/whole-rom-private-20261023.evidence.json`，Evidence `ev_6044e70f4a6f785a665e891cedb82fc897de52716642b9e9bbe0538f9b9d4c40`，Ghidra12.1.4，`RISCV:LE:32:ap01thead2`，profile `b6368dd18431e8113aa5026c713d41e648ab0f6ddd9421ff6c4a49e23b3cd2f3`。直接读取完整bundle目标record，不把旧transport resource_constraint预览当完整记录。旧callback record19 Evidence `ev_709b5ff51cf4fb33e1b9ae866819ac7a860e0ffe029c2c56c7e9344ac037af88` 未提供 analysis_profile；不得套用handler的thead2或P-02的thead3。

| 验收项 | 结果与证据 |
| --- | --- |
| 输入对象与switch选择 | 接受。handler `0xa00f61ea` 取event+0作为W，`61fc`取word(W+0x10)作为S。`7cc6/7d00` LBU S+7，减1后AND255；不是凭页面名猜内部物理端口。 |
| 两个switch实际value | 接受。`7cca`、`7d04`为整寄存器a1常量0/1，至`7cd2/7d0c`调用间无OR/shift/取反。只认证两个UI动作的值；通用第二byte仍不命名为bool或设备mask。 |
| cmd65完整62B | 接受。`0xa0191834..1872`的LUI/LBU读取`0x62fcb01c`，BGEU以完整word index比较u8 count，越界直接ret；`1848`形成0x0265，SH得到LE字节65,02；SB index/value到s0−28/−27，descriptor在s0−24，payload指针写s0−20；`1864`直调`0xa01951e2`。仅栈字段写，无本地I/T遥测写，没有定义业务成功返回。 |
| 实际switch视觉顺序 | 接受。setter后立即装入`40ee`参数并调用，不测试返回；0动作给呈现helper传1，1动作传0。选择0x13仅切页面/移除子页，不构成已发请求取消。 |
| safe正常选择域及顺序 | 接受。`7db0/7fe2`读S+4；无符号`(S+4−0x18)<=4`时计算0..4请求index。先操作控件flag，`7dd6/8000`调cmd63 setter，然后SH0x101/0x100到safe state+8；UI变化不依赖E07门是否提交。范围外旧寄存器语义保留，未补默认值或研究异常输入。 |
| safe反馈 | 接受。mask0x10查页面0x16，非空且`S+7==selector`；`5b40`明确LBU I+0xc，与1比较切控件。请求读S+4而此处过滤读S+7，不能合并两个身份域。 |
| switch反馈 | 接受。mask8查页面0x15，非空且同selector过滤；`5b78`明确LHU I+0xa作a3，a2=1，经`5b7e`交40ee。不能改成enable bit或cmd65 ACK。 |
| helper零/非零与所有权 | 接受。旧record18中a3经s0−0x34保存/恢复，非初始化分支`4214`按a3非零走另一控件flag组。与动作共用呈现helper不代表命令byte等于I+0xa。栈请求只同步借用；I/mask不能跨callback长期保存。 |
| 失败/完成/取消边界 | 接受作者未闭结论。submit可能未接纳，UI不看返回；本题没有请求ID、cmd63/65结果与遥测比较、回执年龄、业务超时/失败回滚、取消句柄或迟到响应隔离。不能借mode/UART旧合同补足这些保证。 |

来源限定补充：旧callback `0xa00f5350`仍为`custom0.rs1.rs2`，类型提取结果在伪代码中为`extraout_a4`；本轮不运行/修复模型，未独立认证该厂商提取编码的精确bit范围。其后类型结果1→selector4、2→5、0且低nibble<3→nibble+1的标准分支以及S+7比较可定位，足以支持“callback派生UI selector而非远端内部端口”的有限结论。作者已保留旧profile缺失，本补充不要求行为修正。

## 真正新增

新增业务恢复为0；本轮是独立验收。独立 [review_static.py](../../analysis/port-control-review-pr14-0041-20261024/review_static.py)仅使用stdlib，从原ROM解析I/S/B/J字段与选定压缩LI/ANDI编码，重新读取7窗666B，核指令长度边界及6条JAL实际目标，并比对原留存地址边界。关键字段和对象入口/selector/helper的必要稀疏原字另行核对；未把地址对齐检查等同完整语义验证。

[review-evidence.json](../../analysis/port-control-review-pr14-0041-20261024/review-evidence.json)保存原字、检查标签、来源限制与必要稀疏留存。最终277项静态断言PASS；该数字只说明检查执行范围，不代表功能完成率或新增恢复量。未使用Capstone或运行作者脚本。

可用重建阶段是：保留UI selector与真实byte参数→按已证门构造cmd63/65请求→同步提交尝试；另将callback内复制的最近观测值交同页呈现。应用可分别存意图和观测，增加待确认/过期策略，但须标为新设计，不能伪装ROM原有设备确认。

## 未闭精确边

1. cmd65第二byte的设备语义、index到外层连接/底座内部物理端口映射未知，两个0/1动作不能补出通用mask合同。
2. safe的S+4请求域与S+7反馈域身份桥未闭；源种子仍是`0xa00f7db0/7fe2`和`0xa00f5b0e/5b70`。若以后登记后继，定向查已有handler/creator两byte赋值与选择身份即可；本复核未开展writer后继。
3. 命令接纳、运输结果、底座执行与遥测的因果关系、响应年龄及业务失败/取消/关闭后保证未知。遥测变化和即时勾选均不是事务确认。
4. callback厂商类型提取的旧profile未供应，本轮只保留旧留存解释与标准下游分支，不认证厂商ISA或完整callback CFG。

独占产物共3个：本报告、review_static.py、review-evidence.json；JSON按仓库规则ignored但保留原路径。未修改作者文件或共享索引。结束 `2026-10-24 14:59:16 UTC`，实际墙钟342秒；无主动等待/任务中断，读取和静态检查工具耗时计入墙钟，未单独测有效工时。初次shell目录被登录环境改变，后续显式workdir并禁用login；一次旧JSON读取默认编码失败后改UTF-8成功，未据失败读取下结论。提前收敛交付，不以计划时间强制等待。

实际交付检查：最终静态脚本277项PASS；3文件尾换行/尾空白、JSON解析、7个本地链接、`git diff --check`通过。worktree tracked/staged无改，untracked仅报告与复核源码，ignored仅本题review-evidence.json。未提交推送；未宣称完整端口控制接口或设备成功已闭合。
