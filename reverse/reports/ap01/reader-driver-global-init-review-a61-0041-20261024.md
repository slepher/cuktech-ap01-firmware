# A61：J08/4 reader两槽初始化writer的独立限定复核

2026-10-24；认领 **J08/4**，非作者 `/root/a56`，作者A60 `/root/g23` 已交付停止；固定基线 `bd457a6`，独占 `re0041-a61` / `codex/re-0041-a61`。主仓[唯一认领表](rolling-management-0041-20261023.md#链条认领表)已登记A61。遵循最新[流程](reverse-design.md)、[保留规则](../../analysis/README.md)及REA技能的静态/留存边界。

**限定接受A60，语义纠正0、新增功能0。** 已验s1=G=0x62fc957c、所选a0非零分支及opaque helper正常遵守s1保存约定时，独立原字段确认：0xa008e51e写word4到0x62fc9740；0xa008e522写word0到0x62fc9744；随后0xa008e526写word0到0x62fc9748仅作同序锚点。该结论补初始化状态，不证明registry已有节点、实际driver/slot绑定、后续writer或对象寿命。

不运行作者/历史脚本、目标/指令/固件/模型、SIM/QEMU、构建、回放、异常输入、设备或外部服务；不切换共享REA，不改生产ROM配置模型或共享表，无下级agent、提交推送。不读取0xa0087b06 body、剩余334B窗口或新节点注册；新JSON留原相对analysis路径并受Git忽略。

## 继承结论

|出处|继承范围与本题不重验的部分|
|---|---|
|[A56](reader-driver-selection-a56-0041-20261024.md)/[A57](reader-driver-selection-review-a57-0041-20261024.md)|reader从word(G+0x1c8)取head，以word(G+0x1c4)+4形成动态next偏移；只用确切两槽种子，不重读选择144B或接口/缓存|
|A58/A59，J08/3|旧metadata不足与同偏移栈对象消歧仍是当时有限结论，不重复全载体负搜索或由旧未知推不存在writer|
|[A21](png-info-lifecycle-a21-0041-20261023.md)/[A22](png-info-review-a22-0041-20261023.md)、[A25](pixel-memory-contract-a25-0041-20261023.md)/[A26](pixel-memory-review-a26-0041-20261023.md)|正常caller/initializer、G基址及s1=G、清零0x210等为既验前提，直接引用，不运行旧检查器或重验原字/PNG/像素主体|
|[A60作者报告](reader-driver-global-init-a60-0041-20261024.md)|最小新增为e4c4正常分支和e51c/e51e/e522/e526确切初始化字段；作者73项检查不是独立接受，本次另写最小位域检查器|

原件沿[CATALOG](../../../roms/CATALOG.md)：0041 `ap01-1.0.2_0041.bin`，6,769,704B，既有SHA256 `972db4c136c7ed9e24a83c07c1a7fd62040ca018b08ca285216d26b1fee3c6b9`，`file_offset=VA−0x9ffff000`。只校长度、引用摘要，不重算哈希。A21/A25旧EID/profile及A60旧owner出处原样保留，本次没有新REA生产记录、profile或EID。

## 本轮复核或纠正

自行拆RV32/RVC位域，不用Capstone/作者预期文本，仅读e4c4与e506..e52a必要直线段，共12条/38B。其间不涉及s1的新显式定义；跨e516调用则以普通callee保存s1、该调用正常返回为**条件**，未认证helper内部或副作用。

|锚点|独立结果与接受边界|
|---|---|
|`0xa008e4c4` 原字29e1|压缩非零门寄存器a0、目标0xa008e506。仅a0非零这条边保留继承s1=G；不补零分支或把两分支拼成同一正常执行|
|`0xa008e506..e512`|CLI a5及SW/SB只操作其他寄存器/内存，不写s1；这些非目标字段只用于基址连续性核对，不恢复其业务语义|
|`0xa008e516`|JAL写ra，独立目标0xa0087b06。helper不读，s1连续性依正常callee-saved约定；此事实不证明helper已成功初始化任何资源|
|`0xa008e51a`|C.LW目的a0、base=s1、offset0x58；不写s1。只核寄存器关系，不为该字段命名|
|`0xa008e51c` 原字9147|C.LI目的a5，signed immediate=4。不是byte截断或继承另一次寄存器值|
|`0xa008e51e` 原字23a2f41c|S-format为 `(opcode,f3,base,src,off)=(0x23,2,s1,a5,0x1c4)`；32位SW，G+0x1c4=0x62fc9740，写4|
|`0xa008e522` 原字23a4041c|同格式base=s1、src=zero、off0x1c8；32位SW，目标0x62fc9744，写0；严格在前条之后|
|`0xa008e526` 原字23a6041c|同格式src=zero、off0x1cc；随后word0写0x62fc9748。只保留地址/宽度/顺序锚点，不推三word结构或尾槽正式类型|

没有发现A60语义错误。head初始化0与stride初始化4不表示已有注册项；A56的next_off只有在该初始化值未被改变时才代入4+4=8，也不能凭这个数值认定实际节点大小/容量或具体D。

局部合同（非原源码）：

```c
// 继承s1=G；仅e4c4非零分支，opaque helper正常保存s1。
word(G + 0x1c4) = 4;
word(G + 0x1c8) = 0;
word(G + 0x1cc) = 0;  // 仅第三次原序锚点
```

## 真正新增

新增业务/语义纠正/ISA/来源认证/整库排除均0。新增为非作者16项位域与地址/顺序证据，限定接受两槽writer；G清零、基址、caller发现与完整initializer均不计本轮恢复。没有读取新helper、剩余缺窗、节点创建/注册/slot本体。

## 未闭精确边与检查

仍未知后续N.word0=D节点创建/登记和head发布、实际D/slot目标/盘符映射、注销/生命周期、运行期writer/稳定性及并发；未观察到真实初始化或五ROM照片走mode1。a0非零门及跨helper正常s1保存约定必须保留，不由SW字段认证入口条件或服务执行。

有种子后继仅以已验 **0x62fc9744 head初始化写点e522与A56的head读取端** 为两端，取得真实后续节点发布/write-xref种子后由管理窗口另登记；不得把本复核扩成剩余334B、全initializer/registry重建。当前没有新增注册callee，本复核不自行展开。

[review.py](../../analysis/reader-driver-global-init-review-a61-0041-20261024/review.py) 实际 **16项PASS，12条指令/38B**；含独立C.BNEZ/C.LI/JAL/S-format、完整必要直线段寄存器宽度及G地址算术。结果 [review-evidence.json](../../analysis/reader-driver-global-init-review-a61-0041-20261024/review-evidence.json) 保留原字/VA/文件偏移与继承前提；没有运行作者collect.py或A21/A25检查器。

JSON、相对链接、Git忽略和diff检查通过。交付后停止本项，由管理窗口整合/补位；无提交推送。
