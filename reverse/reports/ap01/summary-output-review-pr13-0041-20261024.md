# P-R13：P-13 摘要选择到固定输出接线独立复核

**可独立使用阶段已闭合但接口未闭；P-13 限定接受。** P-11 实际 mode 1..4 的固定资源、颜色、flag 与布局接线接受；一般 mode 门的范围表述纠正1项，作者已修正且必要差集复核通过。`0xa00abbf6` 不提供设备测量读取或数值格式化接口，不能据此宣称完整设备摘要接口闭合。

认领 P-13 的非作者复核 P-R13，复核者 `/root/pr13` 未参与作者实现。基线实际 `5bbc331ab429fb76e956e50b8081c56f8d278b11`；仅写独占树 `.worktrees/batch-20261024-p/pr13` 中本报告与同名 analysis。主树、作者文件和管理表只读。按 [REA skill](C:/Users/cogic/.agents/skills/reverse-engineer-anything/SKILL.md) 先读留存再核原字段；没有切共享 REA、运行或导入作者脚本、执行目标/设备/网络/SIM/QEMU/回放/指令模型/构建，没有改 ROM/生产/配置/模型、提交推送或创建代理。预估约30分钟，收敛可提前交付；计时见末，token由父窗统计。

## 继承结论

- [P-R11](D:/Documents/PlatformIO/Projects/cuktech-ap01-firmware/reverse/reports/ap01/summary-rotation-review-pr11-0041-20261024.md) 已限定接受 P-11 的选择状态与 `ad78c/ad9bc/ada4c→abbf6(S,mode,bank,selected)` 实参；作者开始时尚待验的状态现已更新。单 C1 状态4传 mode2、单 C2 状态4传 mode4的不对称保留，不改 caller。
- [P-07](D:/Documents/PlatformIO/Projects/cuktech-ap01-firmware/reverse/reports/ap01/offline-summary-p07-0041-20261024.md)与[P-R07](D:/Documents/PlatformIO/Projects/cuktech-ap01-firmware/reverse/reports/ap01/offline-summary-review-pr07-0041-20261024.md) 的同 S/timer、离线暂停/尾清及旧3秒概念直接继承。S不等同LVGL对象本体。
- 公开 `d8f7c/d9044/d92ec/dbb68/dfb70` 角色及 `ed560` 静态descriptor借用边界沿作者所引已验报告继承；本次不重验公共库、decoder、资源成功显示或私有颜色packing。
- [CATALOG](D:/Documents/PlatformIO/Projects/cuktech-ap01-firmware/roms/CATALOG.md) 原件 `roms/0041/ap01-1.0.2_0041.bin`，6,769,704B，SHA256 `972db4c136c7ed9e24a83c07c1a7fd62040ca018b08ca285216d26b1fee3c6b9`；RV32 little-endian，`offset=VA-0x9ffff000`。独立读得长度一致；不重建整件哈希账。

## 本轮复核或纠正

作者报告与 JSON 只作为待验主张和定位，不是自证。独立 [audit.py](../../analysis/summary-output-review-pr13-0041-20261024/audit.py) 用 Python 标准库读原ROM，按低位确定2/4B长度并拆标准指令字段；`abbf6..abd9b` 422B及既已限定的 `a5e8e..a5ed5` 72B共494B/162条记录。不是重新反编译、ISA执行或形式数据流证明；两条厂商word保持opaque。

独立核原coverage中 abbf6 的422B extent、7个direct callees和Evidence ID；原始 `evidence/rea-0041-20261017/evidence/whole-rom-paths-20261023.evidence.json` 中 inventory Evidence `ev_50cdbf92a7c9800e4d4bc140d70fa8cd1509eca7a199cfd6050d483cf7d695b2` 实际 provider **Ghidra12.1.4**、language **`RISCV:LE:32:ap01thead2`**、profile **`b6368dd18431e8113aa5026c713d41e648ab0f6ddd9421ff6c4a49e23b3cd2f3`**。extent ID `ev_8f2d0976e7d729c7f4fcea563211718dbbb78d480bf85a50e6a16c9a068b486a` 和calls ID `ev_271f5201d6031af8614467203bfef7073226663929ba0b70d6b86d289b4ca278` 来自coverage留存，不冒称新provider输出。

| 项目 | 结果和原字段依据 |
| --- | --- |
| 一般 mode gate | **纠正1项**。`abc00=13f7d50f` 解为ANDI a4,a1,253，`abc04` a5=1，`abc08` BNE到abd34；图像门为 `(mode & 0xfd)==1`。前者不成立后，`abd34=f915` a1-=2，`abd36=93f5d50f` ANDI a1,a1,253，`abd3a` 非零返回；flag门为 `(((mode-2) mod 2^32)&0xfd)==0`。两门分别只约束mode低8位为{1,3}/{2,4}，作者原“完整32bit、恰为1/3或2/4”过强。本结论只针对这两predicate，不声称所有mode使用预先截u8。 |
| 正常P-11模式 | **接受**。已验caller实际1..4动作表不变，mode1/3同组、2/4同组；bank仍精确全寄存器比较1，selected仍全寄存器比较0，不能把它们也截byte或强制bool。 |
| descriptor与选槽 | **接受**。abc10/18常量a0242574，abc5c/64常量a0242808；bank!=1用前者，bank1用后者。s1=S+80，再反复C.LW +30/+58取image即S+b0/d8，+38/+60取背景即S+b8/e0。两份24B header均与ROM一致，只证静态descriptor地址与原字，不证外观/解码。 |
| 三色与位置 | **接受**。独立LUI/ADDI得到06ff8b、ff7a00、89d8f3；bank!=1两selected同绿色/92,168，bank1的selected0橙、非0蓝/98,170。align均1。每步LW重取控件并按ed560→a5e8e→d92ec→dfb70调用，无成功判断，不跨call缓存指针。 |
| 背景颜色宽度 | **接受低24bit，完整32bit未知**。abc48/4e、abc94/9a、abce0/e8、abd20/26各SH+SB，后续LW32；对应局部栈槽第4 byte本层没有初始化。保存寄存器栈槽不覆盖这些byte。dfb70 selector构造为20000。不能把高byte补0或解释为确定alpha。 |
| 胶水停止边界 | **接受限定结论**。a5ea2→a019cd76(widget,ff)，a5ea8→a008986e(saved color)，stack byte stores/LW后a5ec6→a019cd92(widget,packed word)。a5eb0原字8b37853c、a5eb4原字0b35055d与留存一致，不补猜转换/packing；止于公开style边界，无测量source输入。 |
| mode2/4四组 | **接受**。bank!=1 remove_flag1，bank1 add_flag1；selected0对象c4/对齐c0参照bc，非0对象ec/对齐e8参照e4。abd4c/60/7c/94给y7；bank!=1的align1,x22，bank1的align2,x0。先flag call再LW参照和被对齐对象，abd6e→dbb68；不换图、不设色或文本。 |
| 对象、数据和错误合同 | **接受限定结论**。本body仅读10个S控件word，所有直接store均为栈槽；没有测量字段、formatter、新对象、分配/free/timer操作。同步借用有效S/widget，未转移所有权。本层无显式错误/超时/取消/关闭或下层成功判定，返回后P11推进状态不保证显示成功。线程安全、对象writer及全生命周期仍未知。 |

本轮不是设备异常输入验证；mode范围纠正来自原立即数字段的代数解释。没有运行目标或枚举异常设备输入。

## 真正新增与实际检查

新增业务恢复0；新增为P-13阶段的非作者验收和一项gate范围纠正。独立检查 **387项PASS**，包括原字节、RV32/RVC跳转目标、寄存器/宽度/立即数、各组常量/槽位/位置、局部颜色写宽及原profile身份，详见 [audit.json](../../analysis/summary-output-review-pr13-0041-20261024/audit.json)。人工沿短body原字段核控制/调用顺序，不把数值断言数量当作完整语义证明。

作者保存的9稀疏窗350B/110条observations全部逐字节一致；其selected_instructions实际含27条direct_target（20个去重地址），本复核独立解码并核全27条均一致。作者checks记21个目标为作者自核口径，本复核不借用该数字冒称自己的覆盖；2个descriptor header、2个opaque word均一致。作者报告9条相对引用均可定位。本轮无共享REA新分析，零执行/构建/屏幕观察。

## 未闭精确边

1. a5e8e内部厂商packing及a008986e/public color实现未认证；公开API允许功能等价替代，本轮不深挖色彩库。
2. 资源实际外观/decoder及物理屏幕未观察；背景高byte未定，不补造固定32bit色。
3. S控件构造/writer、测量数据更新/数值formatter来源未定位；当前body无消费者，不能发明设备数字数据接口。
4. P11 timer后续活性、H开启的额外副作用、完整退出/并发/销毁未闭。真实后继种子仍是已定位 `ad998/ad9a2→ad486(S,slot,1,selected)`，是否连接数据呈现仍未知；本复核未读该开启支路新后继，不自行接题。

作者修正复核：父窗保存的主树报告/evidence/checks已读。精确图像谓词、前者不成立时flag谓词、RV32回绕、局部mask而非全函数u8 ABI、bank/selected原全寄存器比较以及P11实际1..4域保持原表，均与独立原字段一致。**该必要差集接受，纠正1项已关闭**。作者未重跑完整验证器的口径已明确，不把增加的源码断言记作已运行；本复核自己的387项不依赖作者运行记录。P11已验状态由本报告继承段更新，作者旧“仍待验”文字视作其起始时快照，不重新开启已验阶段。

首次可得UTC `2026-10-24 14:45:51`；结束 `2026-10-24 14:51:30 UTC`，墙钟约5分39秒。问题短且有明确停止边界，提前收敛；工具/进程等待计入墙钟，无主动等待或任务中断，不当作有效工时。最初login PowerShell覆盖cwd导致只读未命中，随后login=false和明确workdir纠正，错误目录未写入。无token实测值，不估算；由父窗统计。本轮仅报告/audit.py/audit.json三文件，JSON、引用及空白检查PASS；未提交推送，交付后停止。
