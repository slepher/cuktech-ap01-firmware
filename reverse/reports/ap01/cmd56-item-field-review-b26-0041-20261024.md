# B26：cmd56 同 item 字段写入合同独立技术复核

2026-10-24；基线 `dbd788a`；独占树/分支 `re0041-b26` / `codex/re-0041-b26`。**限定接受 B25：cmd56 正常有效 item 路径的复制目的，与 cmd51 半字读者属于同一个全局总对象/数组/索引布局的 `item+0x18`；len 精确13、整12B比较非零后才复制，随后重读对象、OR `0x800`、日志、同步通知。无行为语义纠正，新增功能0。** 物理单位、跨命令的实际先后和同一实例稳定性继续未知。

采用 [reverse-engineer-anything 技能](C:/Users/cogic/.agents/skills/reverse-engineer-anything/SKILL.md)，本复核者未参与 B25 生产。只读主仓原 ROM、既有合同和局部规则，独立解算字段/控制目标；未运行或导入 B25 的 verify.py，未将其 JSON 当作原件，未打开/切换共享 REA target/database。未运行目标、模型、SIM、构建、历史回放、设备或外部服务，未做漏洞/异常输入/缺陷验证，未改生产代码、ROM、配置或分析器模型，不创建下级 agent。只写本报告和独占 analysis，不撤销其他工作。伪代码/分析名不等于原源码。

## 继承结论：已有→行为→局限→本题缺口

|已有出处|已解释的行为及限制|本题处理|
|---|---|---|
|[B24](cmd51-item-field-producer-b24-0041-20261024.md)、[B25](cmd56-item-field-contract-b25-0041-20261024.md)|B24 只留候选；B25 给出正常 cmd56 写入及同址公式，作者验证未独立验收|只复核这次接入解释；旧 copy 存在不算新发现|
|[B22](cmd51-device-type-b22-0041-20261024.md)、[B23](cmd51-device-type-review-b23-0041-20261024.md)|cmd51 同数组布局及三个 LHU `item+0x18` 读者已独立接受；分类/阈值/发布有明确范围|分类直接继承；只核足以连接对象的原字，不重验分类树|
|[E01](uiiface-item-ownership-e01-0041-20261023.md)、[E02](uiiface-ownership-review-e02-0041-20261023.md)|`62fcb2cc` 总对象、首 word 数组、`+6` U8 count、`0x1a8` item；比较0相等、copy及通知接口；嵌套所有权已接受|直接引用接口和生命周期，不重导比较/copy/通知或整个 dispatcher。通知仍借用 item，payload 指针没有因本段复制而转移|
|B25 所引旧 dispatcher `ev_6f9f82e5daf0540a1c24a0b85daa2e394785391692765e5e3e100eb7b37ed94c`、旧 UART 正常观察、J01及 application complete|完整旧素材早已存在；SIM/回放各有受控范围，不认证此处机器 ABI/单位/运行时序|继承来源和有界查询，不重复原函数导出、旧复用检索或任何历史运行。passed-in-sim 不等于原ROM完整恢复|

实际缺口仅为 B25 新增局部解释能否得到独立接受，不是五指针生命周期、整充电协议或分类尚未分析。旧地址/完整留存与本轮独立语义接受不重复计数。

## 本轮复核或纠正：逐项接受与精度说明

原件为 `D:/Documents/PlatformIO/Projects/cuktech-ap01-firmware/roms/0041/ap01-1.0.2_0041.bin`，映射 `file_offset=VA-0x9ffff000`。独占 [review.py](../../analysis/cmd56-item-field-review-b26-0041-20261024/review.py) 直接读原件，标准32位的 load/ADDI、B/JAL、乘加/位段分别独立解算；必要压缩指令核原16位字并人工对照静态解码。结果见 [review-result.json](../../analysis/cmd56-item-field-review-b26-0041-20261024/review-result.json)。没有新 REA Evidence ID或完整函数/资源导出。

|B25主张|独立依据|判定与限制|
|---|---|---|
|cmd56分流、payload借用|`85ba:b284` 保存 a2 到 s1；`860a` 置 `0x56`；`860e` BNE相反分流；`8612` JAL rd=0→`98d0`|接受；dispatcher参数身份沿E01，未认证整体返回|
|len13与正常有效item门|`98d4` SB先清 `62fcb2f0`；`98d8` 置13；`98da` BNE a1,a5→`9ab6`。`98e2` 取总对象，`98e6` LBU payload[0]；`98ec` 零门，`98f0` LBU count，`98f4` **BGEU** index,count|接受所选 total非零且index<count 的路径。不据此验收其他分支或外层长度处理|
|目的与cmd51字段相同|`98f8` 读 total首word，`98fc` 置 `0x1a8`；`9900:0b99f920` 字段 op0b/f3=1/f7=16/rd18/rs119/rs215；`9904:6109` 加 `0x18`。cmd51 `93c2` 建同全局基址，`93ca` 缓存到栈槽，`93e8`重取该基址，`93ec`再读 `+0x2cc`；`93f0/93f8/93fc/9400/9404`为相同count/步长/数组/索引形成item|接受同对象族/同字段公式：`dst=load32(load32(62fcb2cc))+index*0x1a8+0x18`。只有同一total/array实例、同index时才是同一实际地址；不证明两次响应间身份保持|
|整12B变更门及copy ABI|`9908/990a/990c`给 `(payload+1,dst,12)`，`990e` JAL→已接受比较器 `a00501be`；`9912` BEQ a0,0→`9ab6`。`9916/9918/991a`给 `(dst,payload+1,12)`，`991c` JAL→既有 `a000589c`|接受。比较任一字节不同即可复制，不要求首半字变化。复制区间明确为十六进制 **`[item+0x18,item+0x24)`**，共12B；不是十进制24终点，不是SH或原子写合同|
|copy后重读与置mask|`9920`重新读global，`9924/9928`重算index步长，`992c/9930/9934/9938`再核非零/count/数组；`993a/993c`构成 `0x800`。`9940/994c` indexed word字字段op0b/f3=4或5/rd12/rs113/rs214/upper5=8/shift0；`994a:4d8e`为OR|接受原序与word OR，不把copy后当前item简化成一直使用先前缓存dst，不声明稳定性/串行化。不是cmd52直接赋mask的合同|
|日志DCap与后续通知|`9954`为 **LHU a6,0x18(a5)**，`9950`为LHU a7,+0x1a，`9958/9968`取+0x1c到栈；`996e`给a5=index。原串 `a0269760` 为 `UiIFaceMngBmsChange = %d, DCap=%d,FCap=%d,RCap=%d`，a4指向它；`997c`日志后，`9980`给a0=index、`9982`→`a00a389c`|接受日志实参对应及通知顺序。DCap仅是日志提供的分析名；本段没有单位/缩放证据，容量类解释属有限推断，不认证mAh/Wh/比例/实际电池语义|
|所有权及返回消费|同步比较/复制用payload+1；item内联区间由原数组持有。copy后代码取新全局而非使用copy返回；日志后重设a0=index给通知|接受本段无新分配/free、无payload指针持有。通知内部ABI与mask清零沿E02，不重新恢复；下层copy的store粒度/原子性/精确来源未核|

三个厂商字的字段是本轮从原字独立提取，语义仍仅与主仓只读 `ap01thead2.sinc` 的 `th.mula`（25..28）、`th.lrw`（6564..6572）、`th.srw`（6596..6603）特定局部规则对应。`mula`为rd加rs1乘rs2，indexed word读写为base+index左移shift；本例shift0。此私有模型不是独立厂商规范，不新增ISA规则或上游来源认证。

本复核没有发现B25语义冲突。上表把偏移全部显式写为 `0x`，并收紧“同一item”为有条件的同实例地址关系；这些是精度说明，与B25原有稳定性限制一致，不是新功能或行为纠正。首半字后续按ROM既有小端LHU读作 `payload[1] | payload[2]<<8`，这是字节复制结果的解释，不宣称copy内部先写半字、一次半字store或其他10B不参与比较。

## 真正新增与实际验证

**新增ROM功能0、语义纠正0、来源排除0、ISA规则0。** 新交付只有本局部合同的独立限定接受及定位证据，不重计B25解释、旧dispatcher、B22/B23分类、E01/E02所有权或旧SIM验收。

实际运行独占review.py：**64项原件字段/目标/压缩原字检查PASS，另核2处原字串**；包括7个B分支及5个JAL目标、对象地址形成、byte/halfword/word宽度、3个厂商字和日志实参。本脚本独立编写，不导入B25或其证据JSON；仅做静态解码/字段断言，不执行指令或枚举输入。开发时将脚本中未验证的 `93e8`“重建基址”假设纠正为原字所示的栈槽load，并补核 `93ca`保存；B25正文原本只说重读总对象，未受此脚本假设影响。

JSON解析、报告相对链接与 `git diff --check` 通过。没有运行目标、回放、旧SIM测试或共享分析会话。

## 精确未闭

继续未知：payload的真实生产者、物理单位与编码来源；cmd56相对后续cmd51的真实调度顺序和对象稳定性；其他writer/完整命令集/外层协议；底层copy的具体store宽度/原子性、精确库来源与厂商规范。内部copy→重读→OR→日志→通知静态顺序已接受，不能外推实际执行、立即重分类或设备结果。

本题复核闭合，无新的正常功能扩展种子。后续若研究单位或跨命令时序，须先取得真实payload生产者或调度绑定；不为填席扩扫ROM/driver/帧。由管理者决定换题，本路提交后结束。
