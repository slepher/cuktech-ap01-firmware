# 0041 C16：文本入口区域准备调用独立复核

结论：限定接受 [C15](text-precondition-c15-0041-20261023.md)，无须纠正。`a00dddf4(obj)` 的正常非空路径复制 `obj+0x14` 起四个 word，以 `obj+8` 所指辅助对象的 `+0x2c` word（辅助指针为空则取0）对前两项做减、后两项做加，再无条件调用 `a00ddbf6(obj,&local)`。没有正常条件早退或独立成功码；C13 调用点覆盖返回寄存器。仅三个函数的局部静态合同完成复核，下游接受门控及最终更新未知；来源仍为 LVGL 候选，**无新增开源排除**。

## 范围及证据来源

固定基线 `7373c0f`，分支 `codex/re-0041-c16`，工作树 `D:/CodexHome/visualizations/2026/10/23/01a1689f-d8c8-7821-aacd-286f467e884d/re0041-c16`。已读本树 rolling-management 的共同规则/C16任务书，以及 `C:/Users/cogic/.agents/skills/reverse-engineer-anything/SKILL.md` 和 native guide。检查本树递归 AGENTS.md、逐级父目录至盘根及主仓库根，没有发现适用文件。仅写 C16 独占路径；没有修改 C15、共享索引或其他工作树。

- [独立核验脚本](../../analysis/text-precondition-review-c16-0041-20261023/verify.py)只读主仓库 ROM `D:/Documents/PlatformIO/Projects/cuktech-ap01-firmware/roms/0041/ap01-1.0.2_0041.bin`，沿用 `file_offset=address-0x9ffff000`，输出仅在 C16 目录。
- [本次静态证据](../../analysis/text-precondition-review-c16-0041-20261023/review-evidence.json)的 `windows` 包含新读原编码、Capstone 连续解码和独立位字段解析结果，`contract_checks` 包含52项地址化合同断言，`strings` 保留重新读取的三条字符串。
- [C15证据](../../analysis/text-precondition-c15-0041-20261023/instruction-evidence.json)仅供完整字节/解码交叉比较和继承范围来源；未运行或复制 C15 脚本。本次另写位字段解析器，全部81条逐条解析，不执行指令或建立可运行固件模型。

范围为 `a00dddf4..a00dde99`（166B）、`a01ad6d8..a01ad6eb`（20B）、`a008b43a..a008b455`（28B），以及调用点 `a0091f42..a0091f4d`（12B）。前述三函数继承的 REA 范围 Evidence 分别为 `ev_78a1b6c59ae47ef1857c565c37c495d3aca62b1af47147ab7196295a005414d0`、`ev_bb62d13f093eb196ceb0e2d9212d4b3454f9ec97f84ef7f6df5195d3dfb9bca5`、`ev_ba5e69e512eb6d0f6f74db5d84b44c03157ca7a957e43afb96689e829f2d5f94`；主函数直接边来源为 `ev_c56ec829cd902650b88377bad49644eb79f1fe3008d4f58fe4c8768751cd50aa`。它们为历史静态 provenance，本次没有打开 REA 会话或共享可写数据库，也没有将它们称为新运行观察。

## 逐项验收

| C15命题 | 结果 | 本次原编码依据及边界 |
| --- | --- | --- |
| “precondition”不是已认证的断言职责 | 接受 | `dde00` 的 C.BNEZ a0 跳 `dde42`；后者是正常非空入口。正常路径无验证结果判断。任务名不作函数语义证据。 |
| 正常参数 a0=obj，读取 obj+8 word | 接受 | `dde42` MV s1,a0；`dde44` LW a0,8(a0)；`dde46` JAL `a01ad6d8`；`dde4a` MV s2,a0。obj 与辅助指针不可混称。 |
| getter返回辅助对象+0x2c或0 | 接受 | `d6de` BEQZ a0 跳 `d6e8`；非零路径 `d6e0` LW a0,44(a0)；零路径 LI a0,0 后 `d6ea` J 回公共尾部。完整32位 word，无窄字段扩展指令。 |
| 复制 obj+0x14 起四word到栈 | 接受 | `dddf4` sp-=32，`dddfe` s0=sp+32，故局部 s0-32 等于当前sp；`dde4c/50` 分别给 a1=obj+20、a0=s0-32，`dde54` 调复制函数。 |
| 复制依赖只做四word顺序复制 | 接受 | `b440/446/44a/44e` LW a5,0/4/8/12(a1)，`b444/448/44c/450` SW a5,同偏移(a0)。没有调用/条件跳转/申请释放；另有自身栈保存恢复。a0未写，机器返回仍为dst，C返回类型未认证。 |
| 局部前两项减、后两项加扩展量 | 接受 | `dde58/6a/76/80` 读取 s0-32/-28/-24/-20；`dde62/6e` SUB a5,a5,s2；`dde7a` ADD a5,a5,s2，`dde84` ADD s2,s2,a5；`dde66/72/7c/86` 按word写回。只证RV32模2^32算术，不补造坐标范围。 |
| 最终实参为 obj,&local | 接受 | `dde5c` a1=s0-32；`dde60` a0=s1；随后算术只改a5/s2，不改a0/a1；`dde8a` JAL `a00ddbf6`。 |
| 正常路径没有条件早退 | 接受 | `dde42..dde98` 的全部控制指令为依次三个JAL及最后JR ra；getter内部零分支共同返回，不构成主函数门控。此结论限于所见代码，不保证callee必然正常返回。 |
| 不合成成功码 | 接受 | `dde8e..98` 仅LW ra/s0/s1/s2、sp+=32、JR ra；没有读写a0或按a0分支。机器返回寄存器沿用末次callee，业务类型/含义未知。 |
| C13忽略返回，再读旧文本 | 接受 | `1f42` 保存obj到s1；`1f46` JAL `a00dddf4`；`1f4a` LW a0,44(s1) 覆盖返回，`1f4c` BEQZ针对这次旧文本读取。没有用前置helper返回门控。 |
| 主函数直接调用集及两个依赖的无callee性质 | 接受 | 主函数JAL目标完整为 `a008b51a`、`a0019672`、`a01ad6d8`、`a008b43a`、`a00ddbf6`。两个依赖只有分支/返回，无调用；本范围无厂商未解指令或间接业务调用。 |
| 正常路径自身无文本申请/释放 | 接受，限本体 | 四word在本帧，主函数没有直接allocator调用；不能由此认证callees无其他副作用。 |
| LVGL来源候选及区域外扩语义 | 接受为推断 | ROM重读出 `lv_obj_invalidate`、`lv_obj_pos.c`源码路径及 `obj != NULL`；配合两减两加支持“区域准备/外扩”。字符串不能认证准确版本、无厂商改动或已刷新像素。 |
| 诊断返回属性、下游接受/提交及完整GUI生命周期 | 未核，保留边界 | 只核诊断分支可见JAL目标，不进入或触发诊断；不读取/恢复 `a00ddbf6` 内部。局部地址传入callee不证明callee是否复制/保存它。 |

表内 `ddxx/dexx` 属于 `a00dxxxx`，`d6xx` 属于 `a01axxxx`，`b4xx` 属于 `a008xxxx`，`1fxx` 属于 `a009xxxx`。对应完整地址均保留于JSON。

## 必要结构与局部伪代码

只恢复 `word@obj+8` 为辅助指针，`word@obj+0x14/+0x18/+0x1c/+0x20` 为四项，`word@aux+0x2c` 为扩展量。完整对象类型、原始字段名和有符号坐标类型未知。以下仅表达正常路径指令顺序，非原始源码或可执行参考模型：

```c
// a00dddf4(a0=obj), obj != 0; all arithmetic is RV32 word arithmetic.
amount = a01ad6d8(load32(obj + 8)); // aux ? load32(aux + 0x2c) : 0
a008b43a(&local[0], obj + 0x14);  // four consecutive words
local[0] -= amount;
local[1] -= amount;
local[2] += amount;
local[3] += amount;
a00ddbf6(obj, &local[0]);
// epilogue only; no independently established status result
```

主函数是 `a0091ee4` 内 `a0091f46` 的直接callee；正常路径的两个小依赖合同分别是 `a01ad6d8(aux)->word`、`a008b43a(dst,src)->机器a0仍为dst`，末次调用 `a00ddbf6(obj,&local)` 的返回语义不透明。调用者随后读 `obj+0x2c`，未假设该字段在helper调用前后不变。

## 来源、恢复程度与实际验证

事实来自本次ROM原编码；“区域/两角/外扩”及 LVGL 归属为推断。字符串地址 `a02645f0`、`a056a33c`、`a0263318` 均在 `strings` 中重新核值，未追加LVGL泛搜或外部检索。准确版本和厂商修改、两个小依赖的独立来源、原始C签名未认证，来源未知不自动归入私有，也不据形状排除开源。

运行 `python reverse/analysis/text-precondition-review-c16-0041-20261023/verify.py`，结果 `passed`：4窗口226B、81条连续解码；81条全部另用位字段解析器静态重解；52项地址化合同断言；与C15全部字节和反汇编一致。所有可见直接控制指令均由本次位字段解算，正常路径的控制序列及末次callee后的完整epilogue另作集合/顺序断言。核验没有只凭反编译或字符串建立字段/返回结论。`git diff --check` 通过，差异只在C16独占路径。

未执行固件、模型或历史回放，未连接设备/外部服务，未构造诊断输入、畸形输入或做缺陷验证；未修改ROM、生产代码、安全检查、分析器模型；未建立新哈希或复制清单。只完成本次局部复核，整体非开源功能静态恢复尚未完成。

首次明确路径 `git add` 因只读Git元数据的 `index.lock: Permission denied` 失败；按用户既有本地提交授权通过升级工具成功暂存，没有修改权限或绕过限制。暂存区仅三个C16独占文件，`git diff --cached --check` 通过。

小后继建议：另设小任务仅核 `a00ddbf6` 正常路径前两个返回门的实参与一个直接布尔依赖，区分“已准备局部区域”与“下游是否接受”，继续保留GUI/诊断为边界。
