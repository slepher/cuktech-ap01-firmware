# H12：type19 派生行指针有界链独立复核

2026-10-24；分支 `codex/re-0041-h12`，基线 `0df1b44`。依共同/复用/六路规则和H12任务书，使用 reverse-engineer-anything 技能；未创建下级agent。

**裁定：限定接受 H11。构造内 s3 持有 C+0x54 行槽游标；传给控件helper的是槽内行对象值，正常七轮后 s3 被新bar对象覆盖。旧刷新器传给 child getter 的父对象是 R0=LW(C+0x54)。所核构造派生链没有第二个 context 持久根或新的 free(C) 接入。新增业务功能0；116 B context最终归还者继续未知。**

## 先有覆盖与实际复核缺口

| 已有出处 | 已有行为 | 本轮实际缺口 |
| --- | --- | --- |
| [H01](weather-subscriber-lifecycle-h01-0041-20261023.md)、[H03](weather-page-close-h03-0041-20261023.md)、[H04](weather-page-close-review-h04-0041-20261023.md) | C116、B20、P与 `P+0x10→B+4→C`；正常离页、DELETE清28word、注销、free(B)、对象树递归 | 合同直接继承；不重导构造或清理，不跨用type2/type4 |
| 主仓只读 `reverse/rehost/details-0041-round4.json /evidence/7` 与 `/evidence/9`；H11出处表 | 七行构造、底部块/bar、七行刷新已有 | 反编译不能独立认证槽地址与槽值的区别；本轮核必要原字/ABI |
| [H11](weather-detail-row-owner-h11-0041-20261024.md)及其 `instruction-evidence.json` | s3九处普通引用、唯一厂商word字段、七轮及bar覆盖、row0三次getter | 独立重读所列原窗口，并检查消费者C寄存器到R0的连续性；不运行H11 verifier或复制其导出 |

旧round4和complete继续是业务来源；本轮不重复较晚round3或全ROM负搜索。H11历史检索未命中完整记录的陈述只视为其原有有界检索结果，不升级为历史材料缺失证明。

## 继承结论

布局沿H04：`C.controls32[21]@0`、`C.rows32[7]@0x54`、`C.state8@0x70`、尾3 B未知；`B.type32@0=0x19`、`B.ctx32@4=C`，P+0x10指向B。DELETE按旧原序清 C+0..6c 的28word，随后注销、free(B)、清P+0x10；这不是free(C)。行对象由GUI对象树继续拥有；清C中的地址不清children数组。父S8、B20、C116、行对象不能互换。type2 136 B及type4 68 B释放合同均未套用。

## 本轮复核或纠正

只读原件 `D:/Documents/PlatformIO/Projects/cuktech-ap01-firmware/roms/0041/ap01-1.0.2_0041.bin`，沿用身份 `972db4c136c7ed9e24a83c07c1a7fd62040ca018b08ca285216d26b1fee3c6b9`；`file_offset=VA-0x9ffff000`。新写 [review.py](../../analysis/weather-row-owner-review-h12-0041-20261024/review.py)，以独立本地Capstone 5.0.7及原word I/S/B/J位域解码；不切换共享REA target，不打开数据库，不伪造REA Evidence ID。可定位原字和裁定保存在 [review-evidence.json](../../analysis/weather-row-owner-review-h12-0041-20261024/review-evidence.json)。整段只在内存索引，留存96条稀疏指令，不重导完整构造或消费者。

| H11命题 | 裁定 | 独立依据与限制 |
| --- | --- | --- |
| s3由C+54派生，七个槽保存行对象 | 接受 | `8818:93094905`，I型 rd=19/rs1=18/imm=84；`8860:232aa904` 为 `SW a0,84(s2)`；`8a82:23a0a900` 为 `SW a0,0(s3)`，均32位对象值写入 |
| 槽内对象值用于控件调用，槽地址未作为本链参数传出 | 限定接受 | 两个游标有效代码区间 `8818..8996`、`8a54..8b82`（尾为exclusive）的普通s3引用恰九处：派生、+4、覆盖、一次SW、五次LW；无搬入a0..a7或保存s3的指令。`8abc/8af6/8b10/8b44/8b72`均LW槽值；如 `8ad4/8ae2`、`8b0a/8b0c`、`8b68/8b6a`交付值而非地址。创建调用 `8858/8a7e→a00a643a` 前 a0=a1=P=s1 |
| 七轮共用尾，不读第八行槽 | 接受 | `8820` s8=0；`883a` 非零跳8a54；`8b80:65b3`回8928；`8936` s8+1、`8938`常数7、`893a` s3+4、`893c` BNE回883a。最后一次使s3=C+70后退出，槽访问限定C+54..6c |
| 游标随后被bar返回对象覆盖 | 接受 | `8990:efe0f151` JAL目标a00d76ae；`8994:aa89` 为 `MV s3,a0`；后续 `8b82` LBU a5,0x70(s3) 属新对象。H11将该处与C.state分开正确；bar身份沿旧round4对象合同 |
| 厂商字不使游标判定失真 | 限定接受 | 两个游标区间只有 `8a76:8ba7073c`，原字段rd=15/rs1=15/rs2位域=0，无x19；本轮不认证位置窄化算术，不借厂商word恢复其他业务 |
| a00b564e中R0成为getter父对象 | 接受 | `56b2:aa84`保存入参C到s1；连续扫描 `56b2..5874` 未见其他s1目的写入或未处理厂商字。`5850:83aa4405` 为 `LW s5,84(s1)`；`5854/5856/5858`为 `(R0,1)→a00dcee4`，`5860..5864`、`586c..5870`分别为 `(R0,2/3)`。返回子对象存栈，第三个暂留寄存器，沿旧天气更新合同消费 |
| 本链无第二根等于全ROM无别名/free | 未核，不接受外推 | H11已正确保留范围。本轮仅判定构造游标引用和row0 ABI，未查所有callee/其他对象/全ROM自由变量 |

没有核心语义纠正。补充一处范围澄清：消费者本身在 `5826:93874405` 另算 `a5=C+54`，`5834:232ef4fa` 保存到当前栈帧 `s0-0x44`，供H01早已恢复的七行消费循环使用。这是旧函数的局部游标保存，不能把“构造中局部s3链”读成“整个ROM只存在这一个C+54派生值”。本题未展开该旧循环后段，也未据此宣称所有callee无别名；这条澄清不产生持久所有者或新业务。

调用ABI延续H01：`a00b564e(a0=C,a1=P,a2=stack_view)`，上层不消费业务返回；getter `a00dcee4(a0=row,a1=index)`返回子对象。游标+4及LW/SW是RV32指针宽度事实；七轮限定是原分支与计数支持的推断。沿常规callee保存寄存器合同解释局部s1/s3，未重导全部helper或将其来源认证为某版标准库。

```c
// 分析伪代码，非原源码；控件装配次序/重读沿既有完整材料。
slot = (uint32_t *)(C + 0x54); i = 0;
do {
    row = create_row(P, P, /*旧尺寸/位置合同*/);
    STORE32(i == 0 ? C+0x54 : slot, row);
    assemble_and_style_with_original_reloads();
    ++i; ++slot;
} while (i != 7);
create_bottom_block(P);
s3 = a00d76ae(bar_class, P);  // 覆盖槽地址
// 旧刷新器局部接点：
R0 = LOAD32(C+0x54);
child1 = a00dcee4(R0,1);
child2 = a00dcee4(R0,2);
child3 = a00dcee4(R0,3);
```

## 真正新增

新增业务功能 **0**，无新增生命周期入口。独立证据补强了H11的槽地址/对象值区别、循环边及覆盖时点；增加消费者s1连续性检查和旧栈游标的范围澄清。没有把原字重读记成首次恢复功能。

## 未闭精确边与停止位置

成功alloc(0x74)的C经B+4挂接后，到底由哪个明确调用或间接安装最终归还，仍未知。已知根 `P+0x10→B+4→C` 不变；构造派生链终止于8994覆盖，row0局部接点终止于三个旧getter调用。free(行对象)、free(B)、type2/type4析构均不能补上free(C)。opaque helper内部、其他未检路径和实际堆状态不在接受范围；无常驻、泄漏或全局无别名结论。

后续闭包仅在另有可定位、独立的C持久保存/最终归还种子时由管理者另立题；本轮未产生新种子，不重复递归复核或全ROMfree扫描。

实际验证：新脚本 **PASS，373条内存解码、40项检查、96条稀疏留存**；报告相对链接及 `git diff --check`通过。仅写本报告和独占analysis；无SIM、构建、回放、固件执行、设备、外网；未修改生产ROM、配置、分析器模型或主树共享材料。
