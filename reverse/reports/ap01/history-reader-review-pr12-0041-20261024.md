# P-R12：普通详情 history ring→图表接缝非作者复核

**可独立使用阶段已闭合但完整 history 接口未闭；限定接受，顺序文字纠正1处已由作者修正并复核关闭。** 本席未参与 P-12 作者工作。认领沿管理 P-12，基线 `5bbc331`；只写本报告及同名 analysis，主仓只读，未改作者文件、管理表、ROM、配置或模型，不提交推送，不创建代理。使用 [REA skill](C:/Users/cogic/.agents/skills/reverse-engineer-anything/SKILL.md) 的留存优先和事实/推断/未知分账；未打开、切换或修复共享 REA，未执行目标、设备、网络、SIM、QEMU、回放、构建或指令模型。

起始 `2026-10-24 14:50:37 UTC`（首次可得时间）；预计约30分钟，证据收敛可提前交。实际结束/墙钟见交付记录，token由父窗统计，未估算有效工时。

## 继承结论

已读主树 [reverse-design](reverse-design.md)、管理顶部 P 规则及 P-12 行、[P-12 原报告](history-reader-p12-0041-20261024.md) 与全部三个同名 analysis 文件。先读 [charge-complete](../../rehost/charge-complete-0041.json) 顶层 scope/service_contract/verification/limitations 与 record19 必要原 callback，再核 E07 交叉对照、window-history 布局/原序与 P-R10 writer 调用前提。未通读管理历史；一次顶部命令取110行，含少量无关旧记录，未据此扩题。

普通详情图表行为、`0x400` 门、maximum/cursor、三段循环及 `0xa00a64e4` 调用在10-16 record19已存在，新增业务功能为0。旧服务独立180点 milliwatt/head/count 是 SIM 替代设计，不能据其补原ROM单位、采样时间、生命周期。P02/P-R02/P10/P-R10 和 window-history 的生产/通知/借用前提直接继承；没有重做采样或公开图表内部。

原件沿 [CATALOG](../../../roms/CATALOG.md)：0041，6,769,704 B，SHA256 `972db4c136c7ed9e24a83c07c1a7fd62040ca018b08ca285216d26b1fee3c6b9`，LE RV32，`offset=VA-0x9ffff000`；未另算ROM摘要清单。record19 Evidence `ev_709b5ff51cf4fb33e1b9ae866819ac7a860e0ffe029c2c56c7e9344ac037af88` 未保留 profile，沿其 generic/custom/ABI局限，不能贴较晚 thead2 digest。胶水独立 body 出处为 `whole-rom-graph-20261023-4942.json` / `ev_d9fe3aaa705b0bb7ce83bfd8b91ed54a15338d12c0cedb2e144f929e2370b7ff`，inclusive `0xa00a64e4..0xa00a6547`，100 B；Ghidra12.1.4、`RISCV:LE:32:ap01thead2`，digest `b6368dd18431e8113aa5026c713d41e648ab0f6ddd9421ff6c4a49e23b3cd2f3`。私有指令意义只对已绑定现有模型作有界核验，不宣称上游ISA认证。

## 本轮逐项接受、纠正及未决

| 项目 | 判定与证据 |
| --- | --- |
| I 与 P 身份 | 接受。`52b6:ae84` 是 `s1=a1=I`；`53ba..53de` 对 page id 0x13 输出 `local_7c=P` 并检查返回及两输出非空；`56ba..56e0` 当前页面端口门沿旧callback。I的编码提取未重验，保留继承前提。P绝不因同偏移与I合并。 |
| writer→I reader | 接受布局接缝。已验 `92a0→398c(I+3c)` 与 reader 的s1同为item对象类型；`575c/5a10:8b97f402` 的 rd=15/rs1=9/rs2=15/shift=1；随后的LHU读 `I+3c+2*slot`。`5a34`令s9=I+3c，`5a44:0bc55ca3` 的lrhu读同基址+2*s5，零扩展。这里只是条件静态对象连接，不声称实机同一次通知实例已观察。 |
| 门、maximum/cursor与增量序列 | 接受。`5704` ANDI 0x400；`570a` LHU I+1a4，`571a` LBU I+1a6；`5740` LBU P+60。`5744/5748` unsigned比较分别选前进/相等/回绕；`577a`、`5a2e`和`5a40`支持旧cursor含、新cursor不含，回绕尾再头。`5782`写回P+60；相等不emit，整圈混叠及不通知/门不满足照旧保留。正常序列前提是item cursor和已有页面cursor均在0..179；本路径未补页面初始化或纠正非法cursor。 |
| maximum=0 | 接受。`5a58..5a7a`只作原API/可见性及P+4c清零，不写P+60，不提交180个零；不为合理性改写原行为。 |
| 标量图表边界 | 接受。三call的a0来自u16值、a1是P+3c，返回写P+4c；胶水未接收I/ring指针。`650c:0bc5a65a` LWIA rd=a0/rs1=a3/imm=10/shift=1：先从C=P+3c取chart，再a3=C+20=P+50；`6512/651a`把该输出指针存栈/恢复跨append call。 |
| cached_max与point输出 | 接受。`64ee/64f4/64f8`沿C+10 unsigned最大值；`6540`返回C+10，对应P+4c。chart/series/marker来自C+0/+4/+8；末点index179，输出落C+14/+18=P+50/+54；对齐参数x−8、y−7。P+4c不是另一个历史副本。 |
| writer写序文字 | **纠正1处**。作者称“writer在推进cursor前写old_slot”与原序不符。`39b2:2385e716`先SB next到history+16a；`39b6:8bd5d722`再以已绑定SRH写old_slot；`39c2:23850716`按需cursor回绕0。reader完成后序列结论仍成立，但不能推样本先于cursor发布、并发原子性或无竞争。已报父窗转作者；主树作者报告第71行已改为完成后cursor关系并逐项保留原store顺序，末节记录14:53:10–14:53:39 UTC同题修正。非作者于14:54:46 UTC只读核该必要文字差集，接受修正；analysis无需变化，未重跑ROM/脚本。 |
| 完整接口状态 | 未决，维持作者断边：T+e实际reader、首次装载/换item的P+60与series复位、库内部复制/滚动/分配失败、series最终释放、页面最终销毁、物理单位/时轴、跨响应代际及全订阅关闭。 |

## 真正新增与独立核验

新增业务0；本席只提供非作者接受和上述顺序表述纠正。作者新增贡献限于I inline ring真实地址式与P图表标量接缝，不重新计普通详情功能。

独立 [verify_independent.py](../../analysis/history-reader-review-pr12-0041-20261024/verify_independent.py) 只使用Python标准库，未导入或运行作者验证器、E05 decoder、Capstone或指令模型。将作者JSON作为需要核对的载体，独立按原ROM指令长度逐条核7窗458 B/146边界与留存callback位置；不是把作者assembly当解码真值。另对原位域独立提取RV32 I/S/B/J、相关压缩MV/LW、私有opcode字段；56项断言通过，另留4段现有模型出处文本，合计60记录见 [独立结果](../../analysis/history-reader-review-pr12-0041-20261024/independent-checks.json)。纠正只增加3个已定位writer指令共12 B，未重导helper或重跑采样算法。检查数不当业务数量。

静态事实支持API调用形状：`0xa019c5d0(chart,0,value)`、`0xa00925e0(chart,series,value)`、`0xa0093a7c(chart,series,179,P+50)`、`0xa00dbb68(marker,chart,1,x−8,y−7)`。把它们映射LVGL设置范围/追加值/取坐标/对齐是合理重建推断；本席不认证精确公开符号、版本或update mode。`0xa0090470`保留opaque调用，不继续公开库内部。

寿命接受限于本同步路径：从borrowed I加载标量后，仅value和P的C进入glue，页面保存cursor/cached_max和图表对象，未把I/ring地址传给图表。无需为这一点提交额外retain I；不能外推callback后I仍有效、公共图表不分配或完整释放安全。

## 未闭精确边与交付

可用阶段为：在已通过app/page/selected-port门、已有有效页面cursor且生产完成的前提下，将同一布局I的增量ring点按原序提交给图表标量API。完整history接口仍未闭。

唯一后继沿作者种子：从该页面P+60及P+3c/+40的creator/换端口来路，先查complete留存，再按必要窗口核首次装载、换item时cursor及series复位，回答是否补历史；需父窗查重登记后另派，本席不开展。T reader独立待排，不做全局负搜。

源文件保持只读；独占输出仅本报告、verify_independent.py、independent-checks.json及delivery-checks.json。结束时间、格式/引用/差异检查和作者修正确认将记末节。

最终限定接受：作者顺序纠正1项已确认关闭；增量环序、标量API和寿命边界无追加行为纠正，新增业务0。结束 `2026-10-24 14:55:12 UTC`，墙钟约276秒；没有主动等待或任务中断，工具等待包含在墙钟，有效工时未单独测量。首次shell登录目录覆盖导致一次输入定位失败，随后显式Set-Location继续，未改来源。token由父窗统计。完成后停止。
