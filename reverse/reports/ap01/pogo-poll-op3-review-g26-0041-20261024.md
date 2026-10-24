# G26：G19/5 实际op3实例化的非作者限定复核

2026-10-24；认领 **G19/5**，复核者 `/root/a56`，作者G25 `/root/g23` 已交付停止；固定基线 `bd457a6`，独占 `re0041-g26` / `codex/re-0041-g26`。主仓[唯一认领表](rolling-management-0041-20261023.md#链条认领表)已登记G26，只核实际op3输入的字段、I/j区别、record/复制/直接持有限定与继承的条件返回边界。遵循主仓最新[流程](reverse-design.md)、[证据保留规则](../../analysis/README.md)和REA技能的留存优先约束。

**限定接受G25，语义纠正0、新增业务/独立op3 body均0。** 实际op=3沿s6写E+0x18，并与本次提交j形成E+0x20=`(j<<2)|3`；旧完成index I决定源record=`local16+(I<<4)`，j决定本次目的槽。两者来自不同读取与计算，不能相互代入，也不意味着运行数值保证不相等。high仅作为本次fd word和符号扩展保存，不能升级为最初P.fd或有效OS句柄身份。

本题未执行G25或旧技术脚本、目标/指令/固件/模型、SIM/QEMU、构建、回放、设备或外部服务；无异常输入/缺陷验证、共享REA切换、生产ROM配置模型或共享表修改，无下级agent、提交或推送。作者报告和大导出从主仓原路径只读，不复制整body；新指令JSON只留本地原analysis路径并受Git忽略。

## 继承结论

|已有出处|已验行为与本次边界|
|---|---|
|[G21](pogo-poll-submit-g21-0041-20261024.md)/[G22](pogo-poll-submit-review-g22-0041-20261024.md)，G19/3|六参共用非fallback体、tail先增、copy16/zero64/entry、counter重读/条件下一跳和不替换a0尾声已验。G26不重导共用体，不重新认证库服务或其他op|
|[G23](pogo-poll-ring-consume-g23-0041-20261024.md)/[G24](pogo-poll-ring-consume-review-g24-0041-20261024.md)，G19/4|实际caller `(backend_fd,C,S,3,high,local16+(I<<4))` 来自后段tag1/result−17无诊断臂；local16只复制S开头16B一次。入口到该后段正常可达性和local16索引范围未闭，不因op3字段核对而闭合|
|G03/G04、G11/G12和G19/G20，经上述报告引用|正常有效对齐16B复制、zero64及fallback界面已验；本次不展开库、native、诊断、fallback或其他四参/六参op实例|
|[G25作者报告](pogo-poll-op3-g25-0041-20261024.md)|只将实际op3输入实例化到已验共用body，没有新专用body。14个作者锚点不是独立验收，本次另写直接字段检查器，不运行/导入作者检查代码|

原件身份沿[CATALOG](../../../roms/CATALOG.md)及旧G22/G24留存：0041 `ap01-1.0.2_0041.bin`，6,769,704B，既有SHA256 `972db4c136c7ed9e24a83c07c1a7fd62040ca018b08ca285216d26b1fee3c6b9`，映射`file_offset=VA−0x9ffff000`。本次核长度并继承摘要，不重算哈希、不套0031或SIM。旧extent/directcall的EID沿G25原引用，仅作定位；本次没有新REA会话/profile/Evidence ID。

## 本轮复核或纠正

新原件只seek14个操作数相关锚点，共46B；不用Capstone或作者指令预期文本，独立拆RV32/RVC寄存器/立即数/访存宽度及分支目标。其余共用copy/zero、byte store、counter/尾声只读G22的选定记录；实际caller及I来源只读G24已核原字段记录。

|本次必要锚点|独立结果与裁定|
|---|---|
|`0xa009e104/108/10c/10e` 压缩MV|分别保存 `s4=a4(high)`、`s2=a5(record)`、`s5=a0(backend_fd)`、`s6=a3(op)`。继承G24 caller的a3=3，故本次s6=3，不把其他调用者的op带入|
|`0xa009e110` 普通BNE|独立解得rs1=a4、rs2=a5、非等目标0xa009e168；沿既验C+0x3c/−1门接共用体，不是按op选新body。fallback不在本题|
|`0xa009e1ba` word store|source=s6，base=s2(E)，offset0x18，故实际word(E+0x18)=3。E的来源及s2重绑定为共用body既验前提，不把入口record寄存器的旧角色永久套到此store|
|`0xa009e1c4/1ca/1ce`|s1(j)左移2，与s6按word OR，再SW到E+0x20；故`(j<<2)|3`。保留OR与word宽度，不擅改成正式ABI名称或加法|
|`0xa009e1a6/1aa`|SRAI以s4算术右移31，再word存E+0x0c；是high的符号扩展高word。未把high解释为有符号负数范围的实际输入观察|
|`0xa009e1be/1d2`|原high word分别SW到E+8、E+0x24；`0xa009e1b6`把backend_fd数值SW到E+4。接受数值保存，不认证句柄对象/系统有效性|
|G24已存 `0xa009e0a4..0xa009e0b0`、`0xa009e0d0..0xa009e0e2`|I来自旧完成记录low的pair右移及低8bit；调用record=`local16+(I<<4)`，high来自旧记录+4。I定义不同于共用体从submission tail/mask计算的j，不能套op2零record或最初P.fd|
|G22已存 `0xa009e172/174/18a`、`1a2/1ae/1b2`|源record用于copy16，目的D=S+(j<<4)，之后条目地址字段保存D及0高word。正常有效对齐且足够存储的条件下不直接持有record参数指针；不能从源/目的表达式不同推出非别名、目的独立性或跨调用寿命|
|G22已存 `0xa009e1e8/1f0` 与原尾声合同|填完条目后重读counter，非零masked-XOR去尾声，相等才以原 `(backend_fd,C,S)` 调0xa009dfcc。S没有改成D或record。没有比较/替换a0或统一成功码；不递归展开下一跳|

没有发现G25语义错误。I与j“不同”的精度限定为**定义与来源不同**，并非断言运行数值必须不等，这与作者不互相代入的本意一致，不计语义纠正。真实copy仍以前提为限：源区域是否有效、I范围、D是否独立持续有效、S/record/E是否别名及何时可复用都未认证；不把“没有直接存record指针”改写成“caller栈可立即失效”。

局部数据合同（非原源码，完整原序沿G21/G22）：

```c
// G24本次实际调用发生且进入非fallback共用体时：
record = local16 + (I << 4);       // I：旧完成记录
j = old_submission_tail & mask;  // j：本次提交槽；不是I的别名
copy16(S + (j << 4), record);     // 有效/对齐/足够存储的既验前提
word(E + 0x18) = 3;
word(E + 0x20) = (j << 2) | 3;
word(E + 8) = high;
word(E + 0x0c) = arithmetic_shift_right(high, 31);
// 其余字段、tail先增及copy/zero原序、条件下一跳、返回沿共用合同。
```

本简写只是输入实例化，不能作为省略tail/zero/重读的替代实现或编译源码。

## 真正新增

新增业务0、独立op3 body0、新callee/ISA/来源认证或整库排除0。新增为非作者操作数字段证据与限定接受；重核共用store不计新恢复功能。没有沿条件递归、新完成项、native服务或其他op扩范围。

## 未闭精确边与实际检查

保留G23/G24入口到完成段正常可达性、诊断返回与寄存器、I范围、copy区域有效/对齐/容量、别名与跨条件递归寿命、counter发布/一致性、实际native/OS交付成功及最终归还。G19/5本轮可记独立限定接受，这些边不能据此记闭；四参op3和本六参op3仍不得同一化。

唯一后继种子沿G25：`0xa009e1f0→0xa009dfcc(backend_fd,C,S)` 时本次E+0x18/E+0x20已写3及`(j<<2)|3`的C/S状态，对应的可达性与副本持续寿命仍需新的具体证据；管理窗口必须先查旧覆盖并登记问题，不能再开同一共用body、递归/全backend扫描。本复核只保留该边界，没有新取证。

[review.py](../../analysis/pogo-poll-op3-review-g26-0041-20261024/review.py) 实际 **21项检查PASS**：14个新稀疏字段锚点/46B，加必要G22/G24原件身份及继承记录定位。结果 [review-evidence.json](../../analysis/pogo-poll-op3-review-g26-0041-20261024/review-evidence.json) 留本地忽略路径，保留新原字/偏移、字段与选定旧记录引用；不复制大导出、不重跑旧技术脚本。JSON、相对链接、Git忽略及diff检查通过。交付后停止本题，主窗口整合并决定后继；无提交/推送。
