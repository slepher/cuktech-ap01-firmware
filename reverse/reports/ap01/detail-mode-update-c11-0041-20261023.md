# 0041 C11：详情模式控件更新合同

结论：`a00f388c(ctx,use_current,mode)` 读取 **ctx+4** 的对象，对其 child0/child1/child2 再各取 child1，得到三个目标控件。模式0、1、2分别清除目标0、1、2的标志1，同时对另两个置位标志1；其他模式对三个全部置位。`use_current==0` 使用第三参数的低16位，非零才调用全局模式 getter。详情页 bit2 callback 传 `use_current=0`，第三参数来自当次 snapshot 的 `+8` unsigned byte，故此路径不重读全局模式。

本次局部更新合同恢复完成；完整视觉效果、对象构造/所有权、标志 helper 的嵌套副作用仍部分未知。仅静态分析，伪代码为分析表达而非原始源码。代码来源为厂商/未知；无新增开源排除。

## 范围、先验覆盖和证据

基线 `57abfb4`，独立分支 `codex/re-0041-c11`。先搜索 `reverse/reports/ap01` 的 `a00f388c`：消费者报告明确未展开；C09/C10明确排除此 helper；factory-reference-map仍标“待补”。因此沿原任务执行，没有另选重复项。未发现适用的仓库/输出祖先 AGENTS.md。已读本树滚动管理 C11 和共同约束，以及 reverse-engineer-anything 技能。

本次三个核心函数：`a00f388c` 与两个直接依赖 `a00d8f7c/a00d9044`。既有 `a00dcee4` child选择和 `a00a5c50` getter 合同仅引用 [C09](detail-summary-c09-0041-20261023.md)/[C10](detail-summary-review-c10-0041-20261023.md)，不新增展开。排除页面构造/销毁、其他订阅和完整 LVGL 实现。

- [本次原指令证据](../../analysis/detail-mode-update-c11-0041-20261023/instruction-evidence.json)：5窗口、逐条地址/原字节/通用解码、厂商字段、原厂字符串与inventory入口。
- [静态核验脚本](../../analysis/detail-mode-update-c11-0041-20261023/verify.py)：只读主仓库 `D:/Documents/PlatformIO/Projects/cuktech-ap01-firmware/roms/0041/ap01-1.0.2_0041.bin`，映射 `offset=address-0x9ffff000`，输出只写C11目录。
- [消费者报告](ui-total-consumers-0041-20261023.md)及[既有指令窗口](../../analysis/ui-total-consumers-0041-20261023/instruction-windows.json)：本次逐字节核对完整 `power_detail_total_cb` 窗口，并重解码bit2查页及传参局部；未共享/打开可写 REA 会话或数据库。
- [whole-ROM inventory](../../analysis/whole-rom-coverage-0041-20261023-round1.json)范围：主函数 `a00f388c..a00f3951`，198B，extent Evidence `ev_9355a3bcb04c071409a71a0c601409a92a4914ea236491d6728608d39c353c5e`；add `a00d8f7c..a00d9043`，200B，`ev_d821fc87cad63c5037b53fec315cde2e6522273428ee4457abfee8b1ecfe9308`；remove `a00d9044..a00d910f`，204B，`ev_d51701fdf85658a8a5f23230761a57266ed75df0e3d65335d68ea69df8ac6193`。本次按原ROM边界逐指令核对，不把inventory收录当语义已验收。

## 参数、字段、调用与返回

| 函数/接口 | 已证合同 |
| --- | --- |
| `a00f388c` | a0=ctx，a1=是否重新取全局模式，a2=模式；a2先经厂商指令取低16位存s1。只直接读ctx的+4 word，不直接写ctx。调用者不消费返回；用void表示此使用合同，不认证原始typedef或a0返回值。 |
| `a00dcee4` | a0=对象，a1=child索引，a0返回child；本次六次调用索引依次0、1、2、1、1、1。正常child选择/NULL断言边界沿用C09/C10。 |
| `a00a5c50` | 无有效入参，返回全局snapshot+8 unsigned byte；NULL日志尾部返回0，沿用C09/C10。本helper仅a1非零时调用，并以返回值覆盖s1。 |
| `a00d8f7c` | a0=对象，a1=flag mask。原厂字符串`lv_obj_add_flag`，非空入口保存参数；先调用`a00d7446(obj,mask)`，返回非零则走尾部，不写标志；返回零路径在`8fee..8ff4`执行对象+0x24 word OR mask。 |
| `a00d9044` | a0=对象，a1=flag mask。原厂字符串`lv_obj_remove_flag`；先调用`a00d749e(obj,mask)`，返回零则走尾部；返回非零路径在`90ce..90da`执行对象+0x24 word AND ~mask。 |

两个flag函数返回值未被本helper消费，均不强行认证原始返回类型。对象为空进入日志与`a0019672`边界，不将断言路径补成普通NULL返回。add/remove的内部查询函数不同，未展开其实现，不能把调用等同于每次必然发生写入。两个helper在标志前后还调用层级/布局相关未知接口：add直接边界包含`a00d8f02/a00dddf4/a00d7446/a00d759e/a00d85ea/a00d73c6/a00d8f42`；remove包含`a00d8f02/a00de61e/a00ddbf6/a00dddf4/a00d8f42`等，完整直接callee集合随inventory保留在证据中。这些副作用未进一步展开，不用名称推断完整渲染。

```c
struct DetailModePartial {
    uint32_t unexamined_00; // C09另一路读取+0，本helper不读它
    Object *groups_at_04;
};

// child/add/remove只是已证ROM接口边界；不是可执行重建代码。
void detail_mode_update(DetailModePartial *ctx, uint32_t use_current,
                        uint32_t supplied_mode) {
    uint32_t mode = supplied_mode & 0xffff; // th.extu s1,a2,15,0
    if (use_current != 0) mode = current_mode_a00a5c50();
    Object *base = ctx->groups_at_04;
    Object *g0 = child_a00dcee4(base, 0);
    Object *g1 = child_a00dcee4(base, 1);
    Object *g2 = child_a00dcee4(base, 2);
    Object *t0 = child_a00dcee4(g0, 1);
    Object *t1 = child_a00dcee4(g1, 1);
    Object *t2 = child_a00dcee4(g2, 1);
    if (mode == 0) {
        remove_flag(t0, 1); add_flag(t1, 1); add_flag(t2, 1);
    } else if (mode == 1) {
        add_flag(t0, 1); remove_flag(t1, 1); add_flag(t2, 1);
    } else if (mode == 2) {
        add_flag(t0, 1); add_flag(t1, 1); remove_flag(t2, 1);
    } else {
        add_flag(t0, 1); add_flag(t1, 1); add_flag(t2, 1);
    }
}
```

保留实际调用顺序；ctx/child没有在本helper中增加NULL检查。t0/t1/t2仅是选择路径命名，未证明对象互异或具体视觉身份。flag1可被解释为可见性相关候选，但本次只认证原值及位写入，不从其他SDK枚举认证hidden语义。模式3“自定义”的显示名称沿用消费者模式表；本函数对3没有专属比较，而是进入other分支，因此不能宣称“自定义与未知模式有不同控件路径”。

## 指令/ABI与分支依据

| 地址 | 原始指令事实 |
| --- | --- |
| `a00f389c..38aa` | s2=a0；`389e`原字节`8b34063c`；`38a2: beqz a1`直达`38aa`跳过getter；否则`38a4` JAL `a00a5c50`，`38a8` s1=a0；`38aa`读取`lw s2,4(s2)`。 |
| `a00f38b2/38bc/38c6` | 三个JAL均落`a00dcee4`，a0均为ctx+4对象，a1依次0/1/2，结果存s4/s3/s2。 |
| `a00f38d0/38da/38e4` | 各组a0传相应对象，a1=1，结果覆盖s4/s3/s2。随后这三个保存寄存器跨flag调用保留。 |
| `a00f38ea..391c` | s1为0走`38ec`remove(t0)，`38f4`add(t1)，跳`3914`add(t2)；非零到`38fe`比较1；等1走add(t0)/remove(t1)/add(t2)。 |
| `a00f391e..3950` | 比较2之前已设a0=t0、a1=1；等2走`3928`add(t0)、`3930`add(t1)、`3938`remove(t2)；不等2跳`394c`add(t0)，`3950`回`38f4`，继续add(t1)、add(t2)。 |
| `a00f393c..3951` | 常规epilogue于`394a: c.jr ra`，但其后的`394c..3951`仍是other分支body；不能在第一个ret截断主函数。 |
| `a00f3a5c..3a88` | snapshot+0xc为unsigned halfword mask，AND4；tag=15调用`a00a72ae`，成功及page/ctx非空才在`3a88`跳`3b12`。完整gate/其他mask沿用消费者报告。 |
| `a00f3b12..3b1c` | `lbu a2,8(s1)`；a1=0；a0保留查页取得ctx；`3b18` JAL落`a00f388c`；之后跳后续callback，不消费返回。这与C09 summary路径的全局重读不同。 |

厂商word独立拆出op=11、funct3=3、rd=9(s1)、rs1=12(a2)、thlsb=0、thmsb=15；**thmsb为bits26..31，thlsb为bits20..25**，不能用普通5位rs2/funct7字段误读。对照既有本地 `ap01thead2.reg.sinc:1164..1165` 与 `ap01thead2.sinc:3930` 的`th.extu rd,rs1,15,0`，SLEIGH为左移16后逻辑右移16。模型原文及位置在证据中；通用Capstone保持此word未知。语义依赖既有本地模型，没有新增上游ISA认证或修改分析器。

## 实际验证、恢复程度与未知

执行 `python reverse/analysis/detail-mode-update-c11-0041-20261023/verify.py` 通过：5窗口660B、234条普通指令、1厂商word、32个直接控制流目标、33关键操作数字段、3函数inventory边界，并确认既有callback窗口与ROM逐字节一致。所有覆盖窗口从入口按2/4B步进至明确边界；主函数尾部跳回边已核。脚本开发时纠正了一处验证表中的依赖目标误写（add查询实际为`a00d7446`，remove查询为`a00d749e`），最终报告及证据保留不同目标。验证仅做数据读取/解码，不执行固件、业务模型、实机或外部服务，不做输入/缺陷验证，无生产编译、ROM/模型/安全检查变更，无新哈希/复制清单。

**事实**：原字节、字段宽度、条件分支、调用参数与目标、ctx+4、三个选择路径、对象+0x24的条件OR/AND写入、原厂add/remove名称字符串。**模型依赖/推断**：U16截取语义依赖既有厂商规则；groups/targets等分析字段名和“模式控件”业务归类。**未知**：原始typedef及有效返回；对象身份、互异性、构造和所有权；query函数内部/完整条件语义；flag1准确显示语义和下层布局/重排/事件副作用；全部页面生命周期、其他订阅和运行时调度。LVGL源码路径`a0569130`和函数名仅为来源候选，不足以认证版本或排除厂商修改。

下一小任务建议：独立复核本helper的U16厂商字段、a1选择全局getter的极性、other分支越过ret再跳回路径，以及两个flag依赖各自不同的提前返回条件；不扩完整UI或query实现。
