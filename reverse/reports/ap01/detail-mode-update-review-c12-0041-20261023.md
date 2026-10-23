# 0041 C12：详情模式更新独立复核

结论：**限定接受 C11，无需纠正其核心合同**。`a00f388c(ctx,use_current,mode)` 的第三参数先取低16位；a1为零跳过全局getter。ctx+4经六次child调用形成三个目标，模式0/1/2分别remove目标0/1/2的flag1，其他目标add；other对三个全add。other尾部位于首个ret之后，仍属于有直接跳入和跳回的有效函数体。两个flag依赖的查询入口及早退极性不同，C11已准确区分。

仅静态核验；局部合同恢复充分，不等于完整UI或生命周期恢复。伪代码和字段名为分析表达，非原始源码。来源厂商/未知，LVGL字符串只提供候选来源，未认证版本或排除厂商修改；无新增开源排除。

## 范围与依据

固定基线 `cb16c11`，专属树/分支 `re0041-c12` / `codex/re-0041-c12`。遵守本树滚动管理C12及共同约束，已读 reverse-engineer-anything 技能。逐级检查本工作树到盘根的AGENTS.md，未发现适用文件；主仓库的根也未发现AGENTS.md。不修改主树、共享索引或其他工作树，不打开共享可写REA数据库。

本次三个核心函数仅为 `a00f388c`、`a00d8f7c`、`a00d9044`。沿用C09/C10的child/getter合同，不再次展开；callback只核已有两个留存局部的字节/传参。未扩完整UI、query内部或生命周期。

- [C11原报告](detail-mode-update-c11-0041-20261023.md)及[其证据](../../analysis/detail-mode-update-c11-0041-20261023/instruction-evidence.json)：作为逐项复核对象，不将其断言直接视为已证。
- [C12静态核验脚本](../../analysis/detail-mode-update-review-c12-0041-20261023/verify.py)与[实际生成证据](../../analysis/detail-mode-update-review-c12-0041-20261023/review-evidence.json)：从主仓库ROM绝对路径只读重解码，按 `offset=address-0x9ffff000` 定位；输出只写C12目录。
- 主函数范围 `a00f388c..a00f3951`，add范围 `a00d8f7c..a00d9043`，remove范围 `a00d9044..a00d910f`，与C11既存inventory范围一致。本次不新做全ROM扫描或复制清单。

## 逐项验收

| 项目 | 决定及原始指令依据 |
| --- | --- |
| 第三参数U16 | 接受，附模型依赖。`389e`字节`8b34063c`独立拆出op=11、rd=9(s1)、funct3=3、rs1=12(a2)、bits20..25=0、bits26..31=15。既有本地 `ap01thead2.reg.sinc:1164..1165` 和 `ap01thead2.sinc:3930..3934` 原文已实际读取核对；左移16再逻辑右移16给低16位。未新增ISA上游认证，不能提升为无模型依赖事实。 |
| a1门控极性 | 接受。`38a2`字节`81c5`为c.beqz a1，原编码解算目的`38aa`；零跳过`38a4 -> a00a5c50`及`38a8 s1=a0`。非零才覆盖模式。不能把参数名use_current误读成零时取当前值。 |
| ctx字段/六次选择 | 接受。`38aa lw s2,4(s2)`；六个JAL至`a00dcee4`，base的索引0/1/2结果保存s4/s3/s2，再各取索引1。ctx+0不在此函数被直接读取；六次选择及寄存器保存均与ROM重解码一致。 |
| 模式分支和调用序 | 接受。`38ea`非零到`38fe`；`3900`不等1到`391e`；`3924`不等2到`394c`。0按remove(t0),add(t1),add(t2)；1按add(t0),remove(t1),add(t2)；2按add(t0),add(t1),remove(t2)。每次mask=1，顺序不互换。 |
| 首ret之后的other尾部 | 接受。`394a 8280`返回；但`3924`直接跳`394c`，`394c`JAL add(t0)，`3950 55b7`原编码跳回`38f4`，继续add(t1)再由`38fc`到`3914`add(t2)，`391c`才到共同epilogue。若在首ret截断会遗漏other。 |
| add查询与早退 | 接受。非空入口`8fce s1=a0`、`8fd0 s3=a1`；`8fd2`JAL目标`a00d7446`；`8fd6`c.bnez a0到`9034`，非零绕过本函数直接flag写入。零路径先`8fda`调用`a00d8f02`，mask bit0为1时`8fea`调用`a00dddf4`，随后`8fee`读obj+0x24、`8ff0`OR mask、`8ff4`word写回，之后仍有callee。 |
| remove查询与写序 | 接受。非空入口`9094 s1=a0`、`9096 s2=a1`；`9098`JAL目标`a00d749e`，不同于add；`909c`c.beqz a0到`9102`，零绕过直接flag写入。非零路径`90a0`先调用`a00d8f02`；mask bit4条件块在写前，本helper传1因此该条件位为零；`90ce`读obj+0x24，`90d0`NOT mask，`90d8`AND，`90da`word写回；mask bit0后续块及其他callee在写后。 |
| callback传参 | 接受该已有局部。`a00f3b12 lbu a2,8(s1)`、`3b16 a1=0`、`3b18`JAL本helper，确实使用snapshot byte。gate lookup局部逐字节一致，但未重新认证整个callback或所有mask控制流。 |
| 返回/来源/未知边界 | 接受C11限定。调用者不消费本helper返回；flag helper返回也未被其消费，不能认证原始void typedef。原厂字符串和未认证版本不足以证明上游开源身份。NULL日志/断言分支未等同普通NULL返回。 |

表中省略地址高位时沿用所在函数地址，例如38a2=`a00f38a2`，8fd2=`a00d8fd2`。所有原字节、完整地址和重新解码在C12证据的 `windows`；30条关键控制流另在 `raw_control_targets`，目的地址由原始RISC-V immediate位拼接和符号扩展独立解算，并非复用Capstone打印偏移或C11验证表。

## 合同与恢复程度

`a00f388c`：a0=ctx，a1=是否取全局getter，a2=提供的模式；先截a2低16位，a1非零才以getter结果覆盖。直接依赖仅认证接口：`a00d8f7c(a0=obj,a1=mask)`条件OR到obj+0x24；`a00d9044(a0=obj,a1=mask)`条件AND反mask到同一word。两者本次都传mask1，是否实际写入由各自query返回控制。上述参数/寄存器与调用目标为原指令事实；getter/child更完整行为沿用[C09](detail-summary-c09-0041-20261023.md)/[C10](detail-summary-review-c10-0041-20261023.md)。

必要控制结构：`mode=u16(a2); if(a1!=0) mode=getter(); base=word(ctx+4); t[i]=child(child(base,i),1);` 然后按验收表的三个有序flag调用处理0/1/2/other。此表达不执行、不重建业务模型。未证明三个对象互异，也不从flag1数值直接认证隐藏/可见显示效果。

事实是字节、操作数宽度、分支极性、直接callee及调用/写入顺序；U16具体语义依赖既有本地模型，groups/targets/模式控件等名称为分析解释。未核/未知：两个query内部与其返回业务含义、下层布局/事件/层级副作用、有效返回值、对象身份与所有权、flag1准确视觉语义、全页面构造销毁及运行时可达性。本次不扩大否定结论到完整调用链，尤其“跳过直接写”不代表callee无其他副作用。

## 实际验证

执行 `python reverse/analysis/detail-mode-update-review-c12-0041-20261023/verify.py` 成功：5窗口660B、234条普通指令、1厂商word；每条原字节与C11证据一致，普通反汇编逐条一致；30个直接控制流目的地址原编码解算，28个关键操作数字段核对；既有SLEIGH字段/语义两处原文一致。完整三个函数窗口按2/4B边界推进；没有通过伪代码替代厂商字段或尾部原指令检查。

这是静态数据读取与解码；未执行固件/业务模型、未连接设备/服务、未做缺陷或异常输入验证，未改生产代码/ROM/安全检查/分析器模型。未进行额外哈希或复制清单。脚本与报告仅位于C12独占路径。

后继建议：限定恢复 `a0091ee4` 文本更新入口及一个直接依赖的格式化/存储合同，沿C09/C10的未展开边界，不扩整个GUI；当前任务不开展该逆向。
