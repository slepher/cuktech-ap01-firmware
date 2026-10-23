# A17：天气当前值首消费合同

2026-10-23，基线 `ae3956f`，分支 `codex/re-0041-a17`。闭合 `a00ab6ea -> a008ce16(arc,current)` 的正常非空对象参数、字段、分支与返回使用合同。setter 的 ROM 名称为 `lv_arc_set_value`：先比较请求值与旧值；不相等时把 signed 32 bit 请求值先上限钳位、再下限钳位；钳位结果仍与旧值不同时写 arc 的 32 bit value 并调用 `a008ccd2`。调用者不消费返回值。只恢复 setter 与 callback 的必要调用切片两个核心范围；没有恢复直接依赖内部。

遵循 rolling-management 的共同规则/A17 任务书，使用 reverse-engineer-anything skill。先检索本树 `reverse/reports/ap01` 全部报告与 `reverse/analysis` 的 `a008ce16/a00ab6ea/a008ce90`：A15/A16 只列当前值调用边界，未给此 setter 内部合同；whole-ROM inventory 给范围和边，不是本合同的既有恢复。未重复已验收 range consumer，不展开图标、文本、生命周期、完整 UI 或弧形控件渲染。适用祖先和目标目录未发现 AGENTS.md。

## 证据与方法

- [A15](weather-subscriber-a15-0041-20261023.md)、[A16](weather-subscriber-review-a16-0041-20261023.md)提供入口：天气 current 在 `a00ab6cc` 从 `weather+12` 用 LH 读入 s2；context 的 `+0x18` 保存 arc 指针。数据生产布局与 range 合同沿用这些报告，不重做。
- 原件只读：`D:/Documents/PlatformIO/Projects/cuktech-ap01-firmware/roms/0041/ap01-1.0.2_0041.bin`。身份沿用既有 dossier/A15/A16 的 `972db4c136c7ed9e24a83c07c1a7fd62040ca018b08ca285216d26b1fee3c6b9`，不重新散列。映射 `file_offset = VA - 0xa0000000 + 0x1000`。
- [whole-ROM inventory](../../analysis/whole-rom-coverage-0041-20261023-round1.json) 的 setter extent Evidence `ev_2a35af477f1157d56ae4d28bd728eeb065de348fca213d18da3904bcedd577dc`：`a008ce16..a008ce8f`，122 B；direct calls Evidence `ev_ccfc42e3fa19fbf2f5dbef80aee727b19e408377732d8c0bc37567913c97cfe1` 给 `a0019672/a008b51a/a008ccd2`。这是历史静态 provenance，不是新运行证据。
- 本轮 [verify.py](../../analysis/weather-current-consumer-a17-0041-20261023/verify.py)直接从原件读取完整 setter 与两个 callback 切片，以 Capstone 5.0.7 解普通 RV32/RV32C，同时独立提取 signed load、word load/store、SLT、JAL、BEQ、C.BNEZ 与厂商指令的原编码位域。结果和每条地址/原字节/文件偏移保存在 [instruction-evidence.json](../../analysis/weather-current-consumer-a17-0041-20261023/instruction-evidence.json)；[review-index.json](../../analysis/weather-current-consumer-a17-0041-20261023/review-index.json)为实际运行摘要。
- 两个普通解码器未知 word 用本机既有只读 `evidence/rea-0041-20261017/ghidra/Ghidra/Processors/RISCV/data/languages/ap01thead2.sinc` 第 18–23 行解释，模型原文一并保留。没有打开 REA 会话/数据库、修改模型、执行固件/模拟器、回放输入、连接设备/服务或进行缺陷验证。

## 参数与字段

| 位置 | 原指令事实 | 局部合同 |
| --- | --- | --- |
| `a00ab6cc` | `LH s2,12(a0)`；opcode 3/funct3 1 | 当前值从 signed 16 bit 扩展为 RV32 32 bit；不是 unsigned halfword |
| `a00ab6e6/e8/ea` | `C.LW a0,24(s1)`；`C.MV a1,s2`；JAL `a008ce16` | `(load32(ctx+0x18),current)`，第二参数没有再截断；天气对象地址不传入 setter |
| `a008ce20` | `C.BNEZ a0,a008ce62` | 正常非空对象直接到字段逻辑；空对象转诊断臂，本报告不假定诊断返回 |
| `a008ce62` | `C.LW a2,0x40(a0)` | old，32 bit word |
| `a008ce68/72` | `C.LW a3,0x48(a0)`；`C.LW a4,0x44(a0)` | high/low，32 bit word；业务名复用 range 已解合同 |
| `a008ce80` | `C.SW a4,0x40(a0)` | 唯一直接 arc 字段写入；不写天气对象或上下限 |
| `a008ce82` | JAL `a008ccd2`，a0仍为 arc | 值改变时通知 update helper；不声称绘制、显示刷新或事件发布已完成 |

这是 RV32 存储视图，字段及变量名为分析名，不是原始 C 结构体：`arc+0x40:value32`、`arc+0x44:low32`、`arc+0x48:high32`。signed 性来自后续 SLT；LW 本身只读 32 bit 位模式。setter 接口可容纳 signed 32 bit，请求值在这个天气调用点的来源限于 sign-extended signed 16 bit。

## 原指令分支与厂商字核验

| 地址 | 原编码/操作 | 直接语义 |
| --- | --- | --- |
| `a008ce64` | `6301b602`，BEQ a2,a1 → `ce86` | 请求值等于 old，直接恢复返回，连上下限也不读取 |
| `a008ce6a` | `33a7d500`，SLT a4,a1,a3 | signed `requested < high`，结果为 0/1 |
| `a008ce6e` | `8b96e542`，word `0x42e5968b` | opcode=0x0b、funct3=1、bits31:25=33、rd=13、rs1=11、rs2=14；`th.mvnez a3,a1,a4`，条件非零才令 a3=requested，否则保留 high |
| `a008ce74` | `b325d700`，SLT a1,a4,a3 | signed `low < capped`，覆盖 a1；原请求值此后不再需要 |
| `a008ce78` | `0b97b642`，word `0x42b6970b` | 同 opcode/funct，rd=14、rs1=13、rs2=11；`th.mvnez a4,a3,a1`，条件非零才令 a4=capped，否则保留 low |
| `a008ce7c` | `6305e600`，BEQ a2,a4 → `ce86` | 钳位后仍等于 old，直接返回，不触发 helper |
| `a008ce80/82` | SW 后 JAL `a008ccd2` | 仅最终值不同才写入并调用 |
| `a008ce86..8e` | 恢复 ra/s0/s1/sp，`C.JR ra` | 没有设置统一数值结果 |

模型明确 `if (rs2 == 0) goto done; rd = rs1;`，与两条 ROM word 的操作数一致。结合两条普通 signed SLT 可得精确顺序 `max(low,min(requested,high))`；在 A15/A16 的正常 `low<high` 范围下就是区间钳位。不是两端值截成 16 bit，也不是覆盖天气 current。两个 equality 门分别比较原请求值与钳位结果，不能折叠成“每次调用均更新”。此结论由静态控制流推导，未构造输入、执行目标函数或测试边界。

## 可读伪代码与返回

```c
// 分析视图；仅非空 arc 正常路径。不是精确源码声明。
arc_set_value_normal(arc, int32_t requested) { // a008ce16
    int32_t old = load32(arc + 0x40);
    if (old == requested) return;             // a008ce64
    int32_t capped = load32(arc + 0x48);       // high
    if (requested < capped) capped = requested;
    int32_t selected = load32(arc + 0x44);     // low
    if (selected < capped) selected = capped;
    if (old == selected) return;              // a008ce7c
    store32(arc + 0x40, selected);
    a008ccd2(arc);                            // 内部未恢复
}
// callback 的相关切片：
current = sign_extend16(load16(weather + 12));
arc_set_value_normal(load32(ctx + 0x18), current);
// a00ab6ee 立即 LW a0,0x1c(s1)，覆盖刚才的 a0。
```

返回合同：正常不更新的两个返回臂中 a0 保持 arc 指针，更新臂 a0 是 opaque helper 留下的值；setter 没有统一结果赋值。本 callback 在 `a00ab6ee` 立即覆盖 a0，不作结果分支/存储，因此应以无消费返回值的操作建模，不能承诺 0、布尔“改变”或稳定指针返回。原始 C 的 `void` 声明没有源码认证。setter 除局部栈保存外仅直接写 value；没有保存天气指针或取得其所有权的指令。helper 是否间接保存内部对象或发布事件仍未知。

## 来源、恢复程度、验证与后继

ROM 在 `a008ce3a/5a` 形成路径地址 `a0263324`，路径为 `/home/jiangmingmin/ap01/AP01_BL618/apps/graphics/lvgl/lvgl/src/widgets/arc/lv_arc.c`；`a008ce4c` 形成 `a0263884`，字符串 `lv_arc_set_value`；`a008ce44` 形成 `a0263318`，字符串 `obj != NULL`。这些支持 LVGL arc 来源候选与诊断名称，不能认证精确版本、原源码或厂商未修改。未新增开源排除，也不因版本未知自动认定 setter 为厂商私有。天气 callback 的厂商胶合来源沿用 A15/A16。

事实：signed 16→32 参数链、两次 signed 比较/条件移动、三个字段宽度、两道早退、唯一字段写入、直接 helper 边、返回覆盖。推断：正常区间钳位，以及 `a008ccd2` 是更新操作的角色名。未知：helper 内部角度/模式映射及其返回、副作用完成时刻、原 C 声明/源码版本、完整 UI、天气与控件生命周期。

恢复程度：本 setter 正常参数/字段/返回消费局部合同已恢复；空对象诊断臂只保留完整原字节和调用边界，不恢复诊断器语义。未使用直接依赖预算；`a008ccd2` 内部不计为已恢复。整模块和全 ROM 仍未完成。

实际验证：运行本轮 verify.py，3 窗口/136 B/44 条指令、20 项独立原编码检查、2 条厂商 word、3 条 ROM 字符串全部通过；普通解码未知恰为已核两条厂商指令，无剩余未知 word。检查本报告相对链接和 `git diff --check`。这些是原件静态验证，不是运行观察或功能测试。只新增独占报告和任务证据目录，不改主树、生产代码、ROM、安全检查、共享状态或模型。

一个小后继建议：A18 独立复核本合同，优先核两条条件移动的条件极性、两道 equality 门及调用后返回覆盖；不扩下游渲染或生命周期。
