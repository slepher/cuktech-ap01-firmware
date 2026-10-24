# A71：reader数值result mapper非作者复核

2026-10-24；J08/9；非作者 `/root/f12`；独占树 `re0041-a71`、分支 `codex/re-0041-a71`，基线 `bd457a6`。**限定接受[A70](reader-driver-result-map-a70-0041-20261024.md)的140B纯数值合同：十二个特例映到0..11，其他32位word返回12，三排序门均为signed BLT。语义纠正0，复核新增业务0。** 仅静态原字段与手工符号叶路径，不运行作者脚本、目标、host输入枚举、指令模型或异常试验。

授权取自主仓最新[认领表](rolling-management-0041-20261023.md) J08/9 A71进行行，非本树旧表。继承已读[逆向流程](reverse-design.md)、[保留规则](../../analysis/README.md)及[REA技能](C:/Users/cogic/.agents/skills/reverse-engineer-anything/SKILL.md)。不切换共享REA，不读getter/IO/其他driver body，无下级agent、提交推送或主树/共享表修改。

## 继承结论

- A66/A67和A68/A69已恢复close/read/seek失败调用端：日志后第二次getter/LW取得的word传入mapper，返回a0交callback尾声。本轮不重验这些caller；不把输入绑定为第一次getter值或原IO负返回。
- 旧whole-ROM functions3328仅提供范围 `[0xa00ea524,0xa00ea5b0)` / 140B、空callee与无dossier。extent EID `ev_c45212c04d6f0d4df9dca25e571b40d05e3508d5ddc8867f30925bac3eda87c2`，directcall EID `ev_5007020263124b8311e3c1adbf8333401dcf5802fde5a39c2afccb94b3e5c2e7`；定位不等于映射合同。
- 原件主仓 `roms/0041/ap01-1.0.2_0041.bin`，实际长度6,769,704B；继承SHA256 `972db4c136c7ed9e24a83c07c1a7fd62040ca018b08ca285216d26b1fee3c6b9`，不重算；`file_offset=VA−0x9ffff000`。未使用其他版本、SIM或运行证据。

重叠只限A70新增纯mapper本体的非作者复核；没有新上层driver功能。旧端点/调用角色直接继承，不把已有检查计作本轮原字段。

## 本轮复核或纠正

本轮直接读取上述140B，独立拆B型opcode/funct3/rs1/rs2/有符号立即数、C.LI的rd/imm、三个ADDI常量、四个C.J和C.BNEZ目标；与完整有限范围离线反汇编的边界/效果清单交叉核对。未导入或执行A70 `verify.py`，未对任何输入调用替代mapper。

`a52c 6300f508`比较输入与16，相等跳a5ac置7；`a530 63c1a704`的funct3=4、rs1=a5、rs2=a0，signed `16<input`跳a572。低侧`a538`等值12置10，`a53c 6341a702` signed `12<input`跳a55e。高侧`a578`等值38置9，`a57c 634ca700` signed `38<input`跳a594。排序门不是BLTU。各BEQ/BNE成功/默认方向依原目标保留。

下表是静态叶路径约束及定义点，不是运行输入记录。x表示入口a0的signed解释；等值比较保留完整32位word。前三门把signed全域分成互斥臂，每臂用有限等值/零门耗尽，故其余word无遗漏地返回12。

|符号臂|相等叶及返回值|不匹配叶|
|---|---|---|
|x=16|16→7，a5ac|无|
|x<16且x=12|12→10，a536/a538|无|
|12<x<16|13→6（a560/a562）；14→2（a56a fallthrough/a56e）|a568置12，经a56a→a556|
|x<12|2→3（a542/a544）；5→1（a54a/a54c）；0→0（a552 fallthrough/a554）|a550置12，经a552非零→a556|
|16<x且x=38|38→9，a576/a578|无|
|16<x<38|22→11（a582/a584）；28→4（a58c fallthrough/a590）|a58a置12，经a58c→a556|
|38<x|110→8（a598/a59a）；114→5（a5a4 fallthrough/a5a8）|a5a2置12，经a5a4→a556|

零门`a552 11e1`独立拆为C.BNEZ a0→a556；零才落到`a554 8147`置a5=0。所有非直接默认叶或相等叶最后汇入a556。那里`3244`恢复s0，`a558 3e85`把a5移入32位a0，`a55a 4101`恢复16B栈，`a55c 8280`返回。四个C.J目标均为a556；没有另一个返回输出或隐含高word。

完整解码效果清单仅`a526 22c6`将s0写到sp+c、`a556`恢复该word；栈建立/局部s0计算不读外部对象。没有JAL/JALR/call，唯一RET在a55c。接受前提是有效局部栈与正常RV32返回；不把局部栈保存说成完全无内存访问。A70的分支、表、默认值、返回宽度与效果描述全部与独立字段一致，无需纠正。

## 真正新增

**复核新增0，业务新增0。** 独立证据和限定验收不是新的mapper功能。十二对数值与默认12见[机器合同](../../analysis/reader-driver-result-map-review-a71-0041-20261024/contract.json)。没有给数字套标准errno/LVGL enum名、正式source类型或版本。

实际独立[review.py](../../analysis/reader-driver-result-map-review-a71-0041-20261024/review.py)通过 **53项编码/常量/目标检查 +3项静态效果检查**，140B。Python只读取原件/提取编码并核静态定义，Capstone 5.0.7 RV32/RVC仅做离线边界与内存/调用清单；不求值输入路径、不运行目标模型。手工符号路径表的全域分割不算host输入枚举。无厂商未知指令。本轮不产生REA生产EID/profile；旧metadata EID按其原来源继承，不冒充新证据。必要字段[evidence.json](../../analysis/reader-driver-result-map-review-a71-0041-20261024/evidence.json)本地原路径忽略保留，未复制整函数导出或大型通用账本。

## 未闭精确边

mapper本体的数值分支无待展开callee。真正未闭的是A66/A68第二次getter实际读值及与首次值的稳定性、真实IO结果、数字的正式枚举命名/版本；本题不读getter或IO以猜这些条件。若第二次word为0，此mapper返回0，所以不能只因先前IO负返回就硬称callback必固定非零；这不是缺陷实验或运行状态证明。

有种子后继为管理窗口将A71限定合同接入A72现有reader生命周期合成，保持第二getter输入边界；若将来研究真实错误状态，需另登记getter/IO精确问题，不从表逆推实际输入。本轮已停止，不自行展开。报告/源码/合同与证据JSON、相对引用、diff空白及独占路径已检查；无提交推送。
