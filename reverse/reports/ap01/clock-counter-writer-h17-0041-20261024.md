# H17：62fc6c64 实际 writer 的有界定位（0041，2026-10-24）

结论：本轮留存引用与较晚材料没有提供 `62fc6c64` 的可靠 ROM writer 种子。主 REA 材料命中的四份 dossier 实际都是同一读者 `a00992d2` 的不同采集；完整 upper bundle 中相关的四条引用均为 READ、非 WRITE。候选 `clock_timer()` 在本地 `clock_initialize.c` 中，而非同名 `.c` 文件，但未与 ROM 地址绑定。按任务书停止，不用源码候选拼出原件计数更新链。新增完整业务功能0，writer、节奏、计数起点与 epoch 继续未知。

基线 `df35f44`，独立分支 `codex/re-0041-h17`。采用 reverse-engineer-anything 技能，优先既有证据，再做限定引用筛选与候选必要行读取。本轮没有打开/切换共享 REA target，没有读取/扫描全 ROM 字段、遍历 IRQ、执行固件、SIM、模型、历史回放、构建、设备或网络；没有修改主树、共享索引、生产 ROM、配置或模型，没有创建下级 agent。没有重复 offset `62fc5c74` 搜索。

## 继承结论：已有出处 → 行为 → 局限 → 缺口

|既有出处|已解释行为|局限及本轮处理|
|---|---|---|
|[H15](clock-source-offset-h15-0041-20261024.md)、[H16 独立复核](clock-source-review-h16-0041-20261024.md)|`a002645a(out8)` 单次读取 `62fc6c64` 的32位值，DIVU/REMU 1000，余数乘1000000，顺序写out两word并返回0；无底层callee|可靠合同直接继承，不重导读者或重核44B窗口。只读行为不能提供实际writer，单位类比不证明真实更新节奏|
|H15 的 `candidate-excerpts.json`，本地 NuttX 候选 `sched/clock/clock_systime_timespec.c` 与 `include/nuttx/clock.h`|非架构分支使用 `g_system_ticks`，输出秒/纳秒形状与 ROM 局部算术对应|只是候选及条件性输入刻度解释；不认证ROM配置、宏分支、硬件、计数起点或上电epoch|
|H13/H14、旧 complete/最终ZIP的服务替代边界|wrapper与天气消费者正常ABI已覆盖；旧页面/SIM服务与ROM来源区分明确|全部继承，不重新读ZIP/复制服务或重做上层时间换算|
|H15 已有较晚 `round3/evidence` 与旧目录查询|精确地址文本未产生writer|本轮只补指定counter/候选名称的留存引用选择，不扩大为完整程序别名分析|

当前实际缺口只剩：哪个 ROM 函数/调用点将正常更新值保存至 `62fc6c64`，以及它与正常计数驱动的连接。没有函数种子就无法合法补其参数/返回、increment/reset次序、并发边界或所有权合同；不会把一个已知读者再命名为writer来充当闭包。

## 本轮复核或纠正

主仓绝对前缀统一为 `D:/Documents/PlatformIO/Projects/cuktech-ap01-firmware/`。本轮精确查询范围、命中文件、旧record引用类型与候选必要行见[review-result.json](../../analysis/clock-counter-writer-h17-0041-20261024/review-result.json)、[candidate-excerpts.json](../../analysis/clock-counter-writer-h17-0041-20261024/candidate-excerpts.json)。没有复制完整dossier、源码或建立哈希清单。

1. 在主仓 `reverse`、`evidence/rea-0041-20261017/evidence`、`round3/evidence` 的现有文件名清单中，未找到 source-xrefs/global-refs/globalrefs 命名的产物。本结论限文件名及这些根，不能声称原始分析从未包含全局引用；替代复用实际 dossier 的 `outgoing_references`。
2. 主 `evidence` 排除 bundle 的 JSON 文本查询 `62fc6c64|g_system_ticks|clock_timer|clock_systimer` 命中 `final-seeded-roots-135.json`、`root-collection-044.json`、`upper-final-collection-020.json`、`v2-all-roots-240.json`。四者 procedure 都为 `a00992d2`，不是四个writer。旧反编译仅把该值用于前后时间差；不扩展该函数业务恢复。
3. 选择已有完整 `upper-complete.evidence.json` 的317条record逐条筛同样名称/地址，唯一命中为 `records[108]`，Evidence `ev_4d6c9f986061ce8306d891bf4fe062d0411c134c2aeb388cd1253c071e04a722`，procedure=`a00992d2`。其中 `a00993a2/a00993ca/a0099412/a009948a→62fc6c64` 的四条 `outgoing_references` 均明确 `type=READ,read=true,write=false`。`native_value_flow` 中出现 `output.location=62fc6c64` 不能直接等同真实存储指令或writer；本轮以实际引用类型筛除，未将伪代码或值流元数据提升为原字节写入事实。
4. `round3/evidence/*.json` 与 `reverse/rehost/*.json`（排除bundle）的同项查询未命中。由新候选位置追加的 `clock_initialize` 名称查询在主/round3 evidence及rehost的这些JSON中也未命中。没有得到新的 ROM 函数种子；文本表示未命中不覆盖指令拼接地址、未留存函数或未定义的全局符号。

这不是 H15/H16 原字节合同的技术纠正。其 counter 单次读取、unsigned pair 换算与单位限制全部接受；本轮没有产生需要重新导出原函数的理由。

## 真正新增：候选位置纠偏，ROM 新增功能0

只读沿用 H15 已给定的 `Ubuntu-24.04:/home/slepher/nuttx-ap01-sim/nuttx` 候选。未新做版本/整库认证、checkout或远程访问。沙盒 WSL 读取曾返回 `Wsl/E_ACCESSDENIED`，获准提升后完成同一必要行读取；这不是 REA target或固件执行。

|本地候选定位|实际读取事实|不能推广的结论|
|---|---|---|
|`sched/clock/clock_timer.c`、`clock_systimer.c`|该候选树中两文件不存在|不能因此声称 ROM 没有对应更新函数|
|`sched/clock/clock_initialize.c:52–55`|条件定义 `volatile clock_t g_system_ticks = INITIAL_SYSTEM_TIMER_TICKS`|不能绑定 `62fc6c64`，不能据宏名断言 ROM 初始值为0或特定epoch|
|同文件 `:399–408`|非 TICKLESS/ALARM_ARCH/TIMER_ARCH 条件下定义 `clock_timer(void)`；TIME64与非TIME64分别对 `g_system_ticks` atomic加1|这是候选增量行为，不是 ROM increment 的原指令；未获调用/地址连接，因此不继续展开周期或IRQ|
|同文件 `:377–383`|候选另有由 RTC 差值转换 ticks 后 atomic累加的语境|不能借此推断ROM校时、单调性、重置策略或实际counter写者，也不继续扩该候选分支|

真正新增仅是有界引用分类与上述候选函数位置。**新增 ROM writer/increment/reset/timer周期合同0；新增完整业务功能0；新增ISA规则与开源认证排除0。** 因没有真实种子，本轮未生成 ROM 伪代码、结构体或状态机，避免把候选实现当作恢复出的原件行为。

## 未闭精确边、停止边界与实际验证

未闭边是 `a002645a` 所读32位 `62fc6c64` 的真实ROM writer入口与保存指令、正常increment/reset及驱动调用连接。更新节奏、计数起点、epoch、硬件timer身份和候选的ROM绑定全部未知。没有静态运行观测，也没有证明counter全局单调或按真实1ms增加；H15的条件性单位解释没有改变。offset writer仍继承旧未知，本轮不重新搜索。

单一后续闭包：先获得针对 `62fc6c64` 的真实 WRITE xref，或命名/来源账直接把 ROM 函数绑定到 `clock_timer`；届时只核该函数一次正常保存与其直接调度调用。当前无此种子，无需派无地址的全IRQ或全ROM字段扫描复核。

实际验证：[collect.py](../../analysis/clock-counter-writer-h17-0041-20261024/collect.py)完成有界留存查询、所选完整bundle的317条筛选、四条 READ/非WRITE断言，以及三个精确候选路径的只读行采集。复核必要性仅限判断是否存在writer种子，没有重跑 H15/H16 或原程序。`git diff --check` 与报告相对链接检查通过。结果是有界未闭交付，待独立技术复核，不冒称时钟模块完成。
