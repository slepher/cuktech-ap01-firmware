# 0041 E08：E07 调用边界与增量口径独立复核

限定接受 E07 的有界引用结论：`a00a1aa8 → a00a53c0` 是带 ra 链接的原 ROM JAL，且调用位置不在所记录的 `a00a12d0..a00a144f` body 内。**不能据此认证真实函数入口、owner 或完整 CFG；也没有恢复 item+0x34/+0x38 的实际页面读者。新增功能为 0。**

基线 `fca1d5e`；独占本报告及同名 analysis 目录。采用 reverse-engineer-anything 技能的留存证据复用、原字节局部核验和事实/推断/未知分离方法。只读原 ROM、旧证据与近期成果；未启动 SIM、构建、历史回放、设备、外部服务或共享 REA 可写 target，未改生产代码、ROM、配置或分析器模型。

## 继承的旧结论：已有成果 → 实际缺口

| 已有出处 | 已解释行为 | 证据局限／本轮只补什么 |
| --- | --- | --- |
| 主仓库 `reverse/rehost/charge-complete-0041.json` records[8]/[9]/[19]，分别 `a00f4610/a00f44e8/a00f5288` | C1/C2 普通值、SOC/时间及 detail 普通项消费者的原指令早已留存 | 直接继承，不重新恢复消费者；SIM 本地服务不认证原 ROM item 扩展字段别名 |
| E01–E06 及 E07 的旧成果交叉对照 | 五组生产/所有权、前三组消费、通知与类型变化清理，已有明确范围 | 不重核整条业务，不把通知访问机会等同读取 +34/+38 |
| [E07 报告](ctk-extra-consumers-e07-0041-20261023.md)及 focused-call-index.json | 14 getter／3 注册器精确编码候选、一个 retained body 不匹配 | 只独立核候选原字节、目标、link 寄存器及记录 body；不重新扫描、不导出函数 |
| E07 retained-search-boundary.json 与 instruction-evidence.json | 所选 dossier 的 literal 偏移候选、局部字段／对象身份校核 | literal 命中不构成 alias 证明；未找到读者不构成不存在证明 |

上述 complete 三条 Evidence ID 为 `ev_a5e9ee75bd0538cbf7e162f205773a29ef0b74cb51f1da0c3108f9bdce600adb`、`ev_28940c3eaa4e13f7d351652eac928f4ea62a4f1961422b2f1ad27137a95d8931`、`ev_709b5ff51cf4fb33e1b9ae866819ac7a860e0ffe029c2c56c7e9344ac037af88`。复核确认原件仍在当前 reverse/rehost，旧 local_path 不代表材料缺失；未另复制原函数。旧 round4 未恢复提示与后续 complete/SIM 解释沿 E07 对照继承，不恢复成当前全局未知项。

## 本轮复核或纠正

[独立验证脚本](../../analysis/ctk-extra-review-e08-0041-20261023/verify.py)只读取 E07 固定候选列表，对每处从原 ROM 读取已有指令长度，独立按 RV32 位域计算 JAL 或相邻 AUIPC/JALR 目标，并检查链接寄存器 ra。JALR 计算包含最低位清零；不依赖旧反编译命名或 custom0 模型。17 处原字节、目标、ra 均通过，其中 getter14／注册器3是**继承列表计数**，不是本轮重新发现数量。

关键局部事实：ROM 映射 `VA - 0x9ffff000`；`a00a1aa8` 文件偏移 `0xa2aa8`，原字节 `ef309011`，指令字 `0x119030ef`，独立解出 `jal ra,+0x3918`，目标 `a00a53c0`。这是“旧结论复核”，没有新增业务恢复。

原 retained `procedure_info` 来源为主仓库 `evidence/rea-0041-20261017/evidence/whole-rom-graph-20261023-4778.json`，Evidence `ev_2ecf5b8ded9c350a2da4c8206066d7cc73f0e3f9f2e80eb4fc229f111a5aeceb`。其 body 单一区间 `a00a12d0..a00a144f`，原记录与 E07 摘录相符，因此 `a00a1aa8` 不属于**这个记录的 body**。

对结论强度的限定如下，未发现需要改动 E07 原字节事实的错误：

- `owner=null` 是拒绝按最近入口误归属的防护值；不能解释为真实程序无 owner，也不能据此宣布真实函数边界已恢复。其他候选落在 preceding-entry 的记录 body 亦只是该记录的归属关系。
- E07 脚本以半字对齐匹配两个指定目标的 JAL／相邻 AUIPC-JALR。这支持“该限定编码及范围中的候选”，不认证每个候选的完整正常 CFG，也不涵盖间接调用、非相邻取址、其他编码或别名。E08 不重扫该区域，故不独立宣称候选集合的完备性。
- 选定 dossier 的 `lw/sw +34/+38` literal 提取不是指针追踪；没有命中不能排除通过副本、数组或其他入口读取。已知 panel+34 不能拼为 item+34。

## 本轮真正新增

仅有独立复核意见、固定候选校核结果和上述表述范围限定。新页面消费者、新数值转换、新借用寿命、新完整函数边界、新协议字段解释均为 0。没有重导函数、复制全源码、重建分类表或新增机械哈希清单。

## 仍未闭合的精确边

`a00a1aa8` 所在真实正常函数入口／CFG，以及 E07 已保留的 `s0-0xe4` item 保存槽后续别名到达关系仍未认证；+34/+38 实际页面读者、转换、主要下游 ABI 与借用结束时刻仍未定位。本轮没有进一步追踪该槽，不将它预判为消费者，也不重开 E05/E06 的 app DELETE/注销问题。

若管理者决定继续，只需另派 `a00a1aa8` 正常调用上下文与该保存槽的局部 alias 问题；若只通向普通字段即可关闭该候选。不得由本轮复核自动扩大成 CTK 泛扫或全 ROM 不存在证明。

验证命令 `python -X utf8 -B reverse/analysis/ctk-extra-review-e08-0041-20261023/verify.py`：PASS，17 固定候选及其 retained body、3 条旧 complete 记录通过；[结果](../../analysis/ctk-extra-review-e08-0041-20261023/review-result.json)仅记录必要定位与检查结论。脚本不运行 E07 扫描、不写旧成果、不执行 ROM；静态复核不能声称观察到运行行为。
