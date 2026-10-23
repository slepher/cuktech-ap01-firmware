# D22：背光动画属性映射与局部来源差异独立复核

2026-10-24；基线 `9f76584`；独立树/分支 `re0041-d22` / `codex/re-0041-d22`。**限定接受D21：property3e/selector20000支持indicator默认状态的shadow opacity局部命名；96/88B、early_apply尾位域、即时path调用、repeat超期余时四项对照成立，证据前提分别保留。语义纠正0，新增功能0。** 不能把本地候选当作ROM未改源码，也不证明真实视觉、控件类型或精确版本。

使用reverse-engineer-anything skill，只读主仓ROM、留存及明确的本地WSL候选，不打开、共享或切换REA target/database。不执行固件、模型、SIM、构建、回放、设备或外网，不改共享/主树、生产ROM、配置或分析器模型，不创建下级agent。布局手算与伪代码只是条件分析，不是原源码/编译产物认证。

## 继承结论：已有出处→行为→局限→精确缺口

|已有出处|行为与证据局限|本轮处理|
|---|---|---|
|[D21](backlight-animation-source-d21-0041-20261024.md)及其[candidate-excerpts.json](../../analysis/backlight-animation-source-d21-0041-20261024/candidate-excerpts.json)|属性、selector和候选动画局部源行已定位；四项ROM差异已研究|仅独立核映射、差异及证据强度，回源比对已有7份明确文件，不扩大源码扫描|
|[D19](backlight-animation-d19-0041-20261024.md)、[D20](backlight-animation-review-d20-0041-20261024.md)|96B descriptor、target=word(ctx+10)、exec/path、2000单周期无限repeat；结束编辑正常查询/删除同pair并置0；完成/删除通知槽0|直接继承行为/所有权；仅取7个与来源差异有关的旧窗口对原件，不重做背光/GUI、style、ctx free或页面DELETE|
|D20引用settings-round2b records[10]，Evidence `ev_d2c060238142516e1df7a388e5984d96623578a75366a96c1472e9ed8c8df9fb`；D19旧complete/system链|结束编辑清理接线和动画业务早有，不能算本题新增功能|继承其范围，不重复大记录/整函数/资源导出，不将SIM替代作为ROM ABI证据|
|F07/F08及D21的本地候选身份、ZIP比较|WSL本地目录与同父v9.2.1.zip成员一致不证明ROM编译输入或远程获取链；显示/LL已有差异|保留来源局限，不重复整LVGL认证或用相邻模块推本结构同一性|

主仓原件为 `D:/Documents/PlatformIO/Projects/cuktech-ap01-firmware/roms/0041/ap01-1.0.2_0041.bin`，映射VA−0x9ffff000。以下源行缩写S为 `Ubuntu-24.04:/home/slepher/nuttx-ap01-sim/apps/graphics/lvgl/lvgl`。没有新REA Evidence ID；旧窗口出处仍是D19/D20/D21，并非新发现函数。

## 本轮复核或纠正：逐项接受/未核

|复核项|处置|独立原字段/源行及证据强度|
|---|---|---|
|shadow opacity属性及值ABI|接受局部命名|ROM a00f43c4为ANDI a1,255，c8调用a018fb3c；fb44把值移a2，fb4a令a1=0x3e，fb4e目标a00df94c。S/src/core/lv_obj_style_gen.c:485–491把value放数值union，调通用setter；S/src/misc/lv_style.h:260定义SHADOW_OPA=62。数值与参数形状支持命名，不认证全部属性枚举或该ROM薄wrapper就是候选通用API原体|
|selector20000/default state|接受局部映射|ROM fb46的LUI给a3=0x20000。S/src/core/lv_obj.h:47为DEFAULT=0、:74为INDICATOR=0x020000；S/src/core/lv_obj_style.h:35及:45给uint32与parts/state按OR的定义。故该数值与indicator默认状态相符；没有核ROM整个selector解析或target实际class|
|差异1：ROM96B与候选条件88B|接受，条件明确|ROM df46给清零长度96，bfe6给复制长度96。候选S/src/misc/lv_anim.h:125–143有九指针槽、九32位值；本轮补读:115–121，确认bezier参数是四个int16，合8B；:149有uint32 last_timer_run，:150–153有四个uint8单bit字段。在4B指针/对齐、常见位域存储前提下，36+36+8+4=84至flags，再尾部对齐得88。没有编译sizeof；不能把这项条件计算升级为候选实际编译ABI测量|
|差异2：early_apply尾偏移/bit|接受，布局前提明确|ROM df6a LBU +5c、df72 ORI 0x10、df76 SB +5c；补核c018同偏移LBU，c026 C.ANDI 0x10，c028零时跳c060，确认此mask实际控制即时应用。候选flags在上述普通RV32推算为+54，early_apply是第四个声明bit；仅在常见低bit起布局为mask08。ROM的+5c/mask10是事实；候选+54/mask08依ABI/编译器，未认证ROM尾部未知字段名或差异成因|
|差异3：start即时path调用|接受，无需候选sizeof前提|ROM c044取node+20的path，c046给node，c048调用；c04c写返回current，c04e给value到a1，c052给target到a0，c054调用exec。候选S/src/misc/lv_anim.c:115–119直接给start_value到exec/custom_exec；此处分支没有对应先调用path的步骤。不能因初始数值可能相同就抹去调用顺序差异|
|差异4：repeat超期余时|接受，保留机器比较/减法原序|ROM c1cc/c1ce读取act_time(+34)/duration(+30)；直接repeat支路保持a1/a3。c23e先置a4=0，c240以signed BGE duration,act_time跳过差值，否则c244 SUB a4=act_time−duration；c248读repeat_delay(+40)，c24a再减，c24c写act_time。普通正超期时保留其余时，本例repeat_delay=0。候选lv_anim.c:593–595直接令act_time=−repeat_delay。这里只解释原signed门和RV32减法，不展开全部playback/调度算法或异常数值|
|本例三角数值与清理|继承|D19/D20已经接受byte截取、量化0→约255→0、无限repeat、结束编辑同target/exec删除并置0；此局部属性命名不证明阴影宽度/颜色已有效、页面可见或target/ctx已销毁|
|准确版本/差异归因/可见效果|未核|本地文件与ZIP一致仍不能认证ROM准确来源；可能其他上游版本或本地改动，不能写成已证明厂商修改。实际控件、渲染、所有style映射与ctx释放均无本题证据|

无需改写D21语义。四项差异中，前两项的候选侧需要明确普通RV32/位域前提；后两项是源语句与ROM调用/数据流的差异，独立于sizeof或位域分配。因而即使不认证候选编译布局，也不能将本地9.2.1宣称为ROM未改动画原体。局部对应只支持来源家族与该调用的语义解释，不支持整库排除。

ROM重复重置的必要分析关系为：按signed比较选择 `excess=0` 或RV32的 `act_time-duration`，随后RV32减去repeat_delay并写+34；候选此处直接写负repeat_delay。它不是一次repeat结束自动free目标。D19/D20的动画节点、target、ctx身份与回收责任继续继承，不引入新对象/所有权或改变清理原序。

## 真正新增与实际验证

新增ROM功能、算法、ISA规则、资源和来源版本认证均为 **0**，无语义纠正。新增仅独立接受记录、检查索引、8B early_apply实际门锚点及9行候选bezier定义；不复制全结构/整个函数或整表。

[review.py](../../analysis/backlight-animation-source-review-d22-0041-20261024/review.py) 实际通过 **44项** 静态检查，包含7个既有ROM窗口逐byte一致、独立I/S/B/J/LUI及压缩访存/移动/位门字段、两个实际调用目标和条件布局常数。7个候选文件的D21留存源行逐行回源相等，且7份完整文件在内存中分别与本地ZIP对应成员相等；未解包或复制源码树。仅补源行S/src/misc/lv_anim.h:114–122，四个int16定义位于:117–120；原文件和ZIP未改。

[review-result.json](../../analysis/backlight-animation-source-review-d22-0041-20261024/review-result.json)保存检查索引、源行比较计数和上述稀疏增补，不虚构新Evidence ID。ROM核验用Python标准库，不导入D21脚本/解码器；WSL默认只读访问被sandbox拒绝后，提升执行同一必要本地静态读取及回源检查成功，未运行候选源码或构建。JSON、报告本地链接、提交差异检查通过。

## 未闭精确边与后继建议

已闭本任务：wrapper属性/selector局部对应及四项差异的独立证据强度。未闭的是ROM精确版本/编译输入/尾部实际字段、全部属性编号一致性、query遍历厂商字、实际target class/可见渲染及完整页面/ctx生命周期。本轮未扩style引擎或GUI所有权。

D21提出的独立复核即为本题，现已覆盖，没有必要再派重复属性/四差异研究。若需认证96B尾部或精确来源，必须先有包含实际不同字段/调用序列的真实本地候选种子；当前材料没有该种子，应保留未知，不从相邻字段猜布局或扩扫所有LVGL版本。真实渲染/ctx free也不以候选推定，本轮不自行接后继。
