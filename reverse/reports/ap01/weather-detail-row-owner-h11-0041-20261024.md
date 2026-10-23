# H11：type19 详情 C+0x54 行游标与 context 所有权断边

2026-10-24；分支 `codex/re-0041-h11`，基线 `f22430e`。使用 reverse-engineer-anything 技能。只读 0041 原 ROM；独立本地原指令解码，不打开或切换共享 REA target，不创建下级 agent。此研究待新 agent 技术复核。

**结论：H04 唯一后继种子 `a00b8818` 的 C+0x54 是构造函数内部的七行地址槽游标。本条有界链没有找到第二个 context 所有权根，也没有提供新的 free(C) 接入。旧 round4 已留相同行循环，新增业务功能为0；本轮到此停止，不扩大别名/free 搜索。**

## 既有出处、行为与实际缺口

| 既有出处 | 已解释行为 | 局限 / 本轮处理 |
| --- | --- | --- |
| [H01](weather-subscriber-lifecycle-h01-0041-20261023.md)、[H03](weather-page-close-h03-0041-20261023.md)、[H04](weather-page-close-review-h04-0041-20261023.md) | type19 的116 B C，20 B wrapper B，P+0x10→B+4→C；构造、订阅、DELETE 清28word、free(B)、清P+0x10；正常离页与对象树递归 | 全部继承，不重做全 context/free 负搜索。H04明确未追派生游标C+54，不能把已验根寄存器索引当全局别名穷尽。 |
| 主仓 `reverse/rehost/details-0041-round4.json` `/evidence/7` (`a00b821e`) | `puVar7=puVar3+0x15`，七轮写入/重读行对象，游标每轮加一word；之后创建底部块和bar | 业务循环已有；custom0和反编译变量复用不能单独证明派生地址是否传出。本轮只补游标生存范围的原字与对象身份。 |
| 同文件 `/evidence/9` (`a00b564e`)；主仓 `reverse/rehost/weather-calendar-complete-0041.json` `/evidence/14` 原汇编 | C+54取得首行对象，再按子对象索引更新天气；完整七行消费者已有 | 本轮只核首行取值→child getter实参，不恢复天气格式/分类/其他六行。 |
| 较晚 `evidence/rea-0041-20261017/round3/evidence` 的既存 JSON 文件 | 对 `a00b821e/a00b564e` 做精确地址复用检索；命中 `sub64-no-return-20261023.json`，未选得这两个入口的 before/after 函数记录 | 有界检索不能证明整个历史不存在其他材料；不将调用名/地址字符串命中当该函数的完整覆盖证明。完整行为直接引用上列complete/round4。 |

实际问题仅为：C+54游标是否被另一个持久拥有者保存或间接传出，以及这条链能否补上116 B context正常归还者。没有接管其他UI对象的生命周期。

## 继承结论

H04的布局和删除合同直接使用：C有 `controls32[21]@0`、`rows32[7]@0x54`、`state8@0x70`；B.type32=0x19、B.ctx32@4=C。父状态S8、B20、C116互不相同。正常子DELETE先按原序清C前112 B，再同键注销、free(B)、清P+0x10；对象树子控件随后靠P的children数组递归删除。清C中的行对象地址不会清对象树。

H04的父/子DELETE、class walker、base析构、事件安装及返回门均不重新导出。type4的68 B context和type2的136 B context完全不用于本条释放推断。

## 本轮复核或纠正

原件为主仓只读 `roms/0041/ap01-1.0.2_0041.bin`，沿用既存身份 `972db4c136c7ed9e24a83c07c1a7fd62040ca018b08ca285216d26b1fee3c6b9`；映射 `file_offset=VA-0x9ffff000`。本轮没有重建散列清单。证据见 [instruction-evidence.json](../../analysis/weather-detail-row-owner-h11-0041-20261024/instruction-evidence.json) 和 [instruction-windows.txt](../../analysis/weather-detail-row-owner-h11-0041-20261024/instruction-windows.txt)。不伪造新REA Evidence ID；这是原件局部解码和历史材料复用。

1. `a00b8818: 93094905` 是 `addi s3,s2,0x54`，C在s2；`s8=0`作为行号。`883a` 非零行跳到 `8a54`，首行走 `8858→a00a643a` 并在 `8860:232aa904` 将返回的行对象指针写入C+54。传给创建helper的a0/a1均是P=s1，传出的是P及尺寸/位置，未传游标s3。
2. 非零行 `8a54..8a7e`计算 `i*43+240`，同样以P调用 `a00a643a`；`8a82:23a0a900` 是 `sw a0,0(s3)`。`8abc/8af6/8b10/8b44/8b72` 都从 `0(s3)`重读行对象，装配子控件时传给helper的是这些槽内的行对象值。没有将槽地址本身传为参数。
3. `8936`将行号加1，`893a:9109`将s3加4，`893c`与7比较回 `883a`；非零行块 `8b80:65b3`回 `8928`共用行背景配置，再经过同一循环尾。索引0..6对应C+54..6c；最后加到C+70后立即退出，未把C+70当第八个行指针解引用。
4. 七轮退出 `8940` 创建底部块，`8990→a00d76ae`创建bar，`8994:aa89`用返回值覆盖s3。其后诸如 `8b82` 的 `lbu ...,0x70(s3)`属于bar对象，而非C的state8；不能因为寄存器仍叫s3就恢复为同一个所有者。

对游标有效的两个范围 `8818..8995`、`8a54..8b81`逐条解码并索引全部s3引用，普通引用恰为上述派生、+4、覆盖、一次SW和五次LW。唯一厂商word在 `8a76`，字段rd=15、rs1=15、rs2=0，不引用x19=s3；本结论不需要对该厂商位域算术作新解释。范围内没有把s3复制到另一个寄存器、存为持久值或传入a0..a7的指令。因此这条链的原指针没有可跟进的callee逃逸种子。

旧刷新消费者的最小接点另核：`a00b56b2:aa84` 保存a0=C到s1；`5850:83aa4405` 是 `lw s5,0x54(s1)`，所得是R0。`5854/5856/5858`以 `(R0,1)`调用 `a00dcee4`，`5860..5864`及`586c..5870`分别用 `(R0,2)`、`(R0,3)`取子控件。返回控件暂存在栈或寄存器，再交给旧天气更新helper。此处没有把C+54作为child对象，也没有安装拥有C的callback；不展开这些已恢复的绘制helper。

没有对H04核心合同作语义纠正。唯一澄清是行游标和后续bar复用s3，地址相同的寄存器名不代表对象相同。

```c
// 分析伪代码，非原源码；其余控件装配、参数重读和样式沿旧证据。
uint32_t *slot = (uint32_t *)(C + 0x54);  // a00b8818
for (unsigned i = 0; ; ) {
    if (i == 0) {
        R0 = a00a643a(P, P, 300, 43, /*原参数*/, 240);
        STORE32(C + 0x54, R0);
        assemble_first_row_using_reloaded_R0();
    } else {
        Ri = a00a643a(P, P, 300, 43, /*原参数*/, narrow_position(i*43+240));
        STORE32(slot, Ri);
        assemble_other_row_using_reloaded_LOAD32(slot);
    }
    configure_row_background_in_original_order();
    ++i;
    ++slot;
    if (i == 7) break;
}
create_bottom_block(P);
s3 = a00d76ae(bar_class, P);  // a00b8994覆盖游标寄存器

// 已恢复消费者的单条局部接点：
R0 = LOAD32(C + 0x54);
child1 = a00dcee4(R0, 1);     // a00b5858
child2 = a00dcee4(R0, 2);
child3 = a00dcee4(R0, 3);
// 下接旧天气更新合同，不返回或持久保存slot。
```

`narrow_position`仅表示旧厂商位置窄化边存在，不在本轮重新认证其完整语义。七行的300×43和y=240+43*i业务布局早由round4报告解释，不计新增。

## 真正新增

新增业务功能 **0**。新增证据是上述派生指针有效范围的完整s3使用索引、各行对象值与槽地址的区分、七轮退出后bar覆盖，以及一个旧row0消费者的原字实参接点。这收口了H04唯一种子：它没有产生第二context根或新的正常清理入口。已有行行为/天气格式和对象树正常删除不能改称本轮首次恢复。

## 未闭精确边与停止位置

已知持久根仍是 `P+0x10→B+4→C`。游标只在当前函数内持有槽地址；槽中持有的是对象R0..R6，row getter接收的也是R0。对象树继续拥有这些行对象，因此继承的正常对象递归清理可以删除行子树；这条所有权链不反向拥有C，也不能把free(行对象)等同free(C)。

**未闭边保持原状：成功 `alloc(0x74)` 的C，经B+4挂接后，到底由谁最终归还，仍无已定位调用或间接安装。** 本轮没有获得第二根，按任务书停止于游标被覆盖及旧row0取子对象接点。不作“C必然常驻”或缺陷判断；没有对全ROM别名、全部free、所有callee内部或全部UI类型做穷尽否定。

事实为原字、宽度、寄存器/槽身份、调用目标和有界引用集合；“函数局部行游标”是这些指令支持的推断；context最终归还者、opaque helper潜在的其他对象别名和实际运行时清理状态仍未知。通用GUI helper来源/版本认证沿既有边界，没有将其凭名称排除为标准库。

唯一后续闭包建议为新agent独立复核本轮“槽地址未传出/对象值传出”的有界判定及bar寄存器覆盖。没有新地址种子可据此启动更宽的context归还研究；是否另立题由管理者决定。

## 实际静态验证

运行 [verify.py](../../analysis/weather-detail-row-owner-h11-0041-20261024/verify.py)：**PASS，254条局部原指令，27项检查**。包含游标所有引用、非零行分支/共用循环尾、+4/七轮退出、bar覆盖、两处槽写入、六个JAL目标、row0 getter对象身份及旧round4关键结构存在检查。`git diff --check`及报告相对链接存在检查通过。

无固件执行、SIM/构建/历史回放/设备/网络；没有修改生产代码、ROM、配置、分析器模型、主树共享材料。只新增本报告和独占analysis证据。恢复程度为指定种子有界收口，保留116 B context最终归还断边。
