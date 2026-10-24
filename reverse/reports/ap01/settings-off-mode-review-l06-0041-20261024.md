# L06：另一设置 byte 发布与共用服务接入独立复核

2026-10-24；基线 `b0b1df1`；独占树/分支 `re0041-l06` / `codex/re-0041-l06`。**限定接受 L05：常量3→显示flag0、编辑U8→显示flag1的配对，a00ab4a8 的 G+3 差异门、byte 发布、reason4及共用服务接入均成立。语义纠正0、新增功能0。** 不能从 UI 继续显示或共用 writer 调用推出实际持久保存成功。

采用 [reverse-engineer-anything 技能](C:/Users/cogic/.agents/skills/reverse-engineer-anything/SKILL.md)。复核者未参与 L05 生产；未运行或导入 L05 检查器，不以其 JSON 代替原件。仅独立静态读取原 ROM/既有报告，写独占报告和 analysis；未使用共享 REA target/database、执行固件/SIM/模型/构建/历史回放/输入/设备/外部服务，未研究异常输入或缺陷，未改生产代码、ROM、配置、模型、主树共享文件或他人修改，无下级 agent。

## 继承结论

|既有出处|继承范围|本题仅复核|
|---|---|---|
|[L05](settings-off-mode-l05-0041-20261024.md)、[J03](settings-persistence-reuse-gap-j03-0041-20261024.md)|旧 settings-round2b records[10]/system cached handler 中两 call 与48B extent早有留存|两 caller 的真实实参/显示flag、返回覆盖及另一字段/reason，不把旧地址或完整 handler 当新发现|
|[L03](settings-mode-contract-l03-0041-20261024.md)、[L04](settings-mode-review-l04-0041-20261024.md)|s4=62fc402c；共用 a00a5bbe 的同步 callback(node.word4,G,reason)、live G；a00ab274 写服务顺序与返回不检查已接受|服务内部直接引用，不重读其 ROM 窗口、不再核通知/全部 writer；不能凭同类 helper 套用新字段|
|J03及旧 settings-round2d records[3]|type1b constructor 按62fc909b与3的关系设置选择已有|只继承消费者身份，不重核 constructor、整个 ScreenOff/ScreenSave UI 或键分派|
|[最终应用验收](application-rehost-complete-0041-20261017.md)、J03的SIM/ROM分界|旧设置业务和宿主保存通过已有明确范围|passed-in-sim 不证明 ROM 字段/flash/回滚；不运行或重计旧验收|

主仓原件 `D:/Documents/PlatformIO/Projects/cuktech-ap01-firmware/roms/0041/ap01-1.0.2_0041.bin`，映射 `offset=VA−0x9ffff000`。本轮 [review.py](../../analysis/settings-off-mode-review-l06-0041-20261024/review.py) 独立解算标准 RV32 与压缩字段，结果见 [review-result.json](../../analysis/settings-off-mode-review-l06-0041-20261024/review-result.json)。既有 Evidence ID/父级定位沿 L05/J03引用，不生成新 REA ID或重复旧源码/资源/整个函数导出。

## 本轮复核或纠正

|L05主张|独立原字段/目标|判定与边界|
|---|---|---|
|fe9f2 的实参3，后续显示flag0|`fe9f0` C.LI rd=a0/imm3；`fe9f2` JAL ra→a00ab4a8。`fe9f6` LW a5,-58(s0)，`fe9fa` C.LI a1,0，`fe9fc` C.LW a0,8(a5)，`fe9fe` JAL→a018f232|接受。返回后在任何成功判断/保存前已覆盖a0，显示对象来自旧local58；不认证显示效果|
|fea0a 的实参U8，后续显示flag1|`fea06` opcode03/f3=4/rd=a0/rs1=s4/imm3；结合已接受s4基址即62fc402f U8。`fea0a`→同 helper；`fea0e/12/14/16` 同组 LW/C.LI1/C.LW/JAL|接受。编辑byte→flag1，常量3→flag0；不能套用L03的相反配对次序|
|helper取G+3 U8，与完整a0相等则返回|`ab4a8/ac` LUI/ADDI→G=62fc9098；`ab4b0` LBU a4,3(a5)；`ab4b4` BEQ rs1=a4/rs2=a0→ab4d6|接受字段62fc909b。比较前只有基址构造及旧U8读取，没有输入截断；只认证当前3/U8 caller，不展开其他输入|
|差异时byte发布→reason4→共用writer|`ab4c0` S字段opcode23/f3=0/rs1=a5/rs2=a0/imm3；`ab4c4` C.LI a0,4；`ab4c6/ca` JAL→a00a5bbe/a00ab274|接受 SB宽度及原序。通知reason是4，不是L03的3；通知和writer内部合同完全继承L04|
|helper未提供明确成功状态|`ab4ce/d0` C.LWSP恢复ra/s0，`ab4d2` C.ADDI sp,16，`ab4d4` C.JR ra；相等出口`ab4d6` C.JR ra|接受无显式布尔赋值。helper残留a0不可命名保存成功，UI也不消费其返回|

本轮没有语义纠正。伪代码无需重复 L05 全段：实际局部原序为 `G+3` 相等直接返回；不等时 `SB → known_notify(4) → known_writer()`。`known_notify(4)` 依据 L04 将 live G 与 reason4传给已登记callback，不复制状态；共用 writer 在通知后尝试写全局G的既有服务，实际结果和下层资源保证沿既有未知边界。

新差异合同只有值传递及既有全局byte发布，没有新增指针持有/所有权转移。显示对象、订阅节点和文件handle的生命期不因本题被补全，不能把静态调用存在表述为真实回调、屏幕变化或文件落盘已观察。

## 真正新增

**新增功能、算法、ISA规则、来源认证及整库排除均为0。** 本轮只独立接受 L05 新增差异；旧 handler、constructor、共用通知/writer、L04和SIM验收不重计。

实际执行独占 `review.py`：**25条稀疏静态记录、6个独立JAL目标、1个BEQ字段/目标通过**，涵盖两UI返回覆盖、字段/宽度/reason、尾声。检查器只用标准库直接读原件，不执行目标/输入或作者脚本；没有重核通知/writer内部，也没有机械重复旧全函数/资源账。JSON、报告链接及差异另行核验。

## 精确未闭

L05这组两caller→G+3 byte发布→reason4→既有writer接入的局部静态问题可限定验收。完整正式枚举/所有真实写者、订阅者身份与生命周期、下层文件服务完整返回/资源保证、真实持久化与重启效果继续未知；全8B正式结构与下层算法沿L04边界保留，不与其他算法任务重叠。

本轮没有新必要功能种子。此项独立复核已完成，不需再派同一窗口；由管理者选择后继，不凭字段相邻、相同函数长度或全ROM扩扫凑任务。
