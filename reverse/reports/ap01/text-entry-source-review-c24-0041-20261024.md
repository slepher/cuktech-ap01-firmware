# C24：文本格式化入口局部来源独立复核

2026-10-24；基线 `c44f3bf`，独立分支 `codex/re-0041-c24`。**限定接受C23：正常两遍格式化、len+1申请、返回缓冲直接由label持有及清静态标记的局部来源映射成立，无语义纠正。** ROM静态标志仍是byte `obj+0x5c`、mask `0x10`；候选位域声明不能覆盖该事实。新增ROM功能0、精确版本未知、整库排除0。

使用 [reverse-engineer-anything 技能](C:/Users/cogic/.agents/skills/reverse-engineer-anything/SKILL.md)，未参与C23生产。只读指定候选必要行和既有证据；未读/导出ROM、未运行C23脚本或候选，没有打开/切换共享REA target/database。无formatter、allocator、GUI、固件、SIM、构建、历史回放、设备、外网或下级agent执行；未修改主树共享、生产ROM、配置、模型或候选。

## 继承结论：已有→行为→局限→本题缺口

|已有出处|已解释行为与局限|本题处理|
|---|---|---|
|[C13](text-update-entry-c13-0041-20261023.md)、[C14](text-update-entry-review-c14-0041-20261023.md)|`a0091ee4`入口a2..a7连续va区，旧text+2c非空且+5c bit4=0才free；helper两遍调用、首遍返回32位加1申请、返回原buf；入口先存text再清bit4再刷新|可靠原字节合同继承，不重核101条指令/306B。formatter长度/NUL/va推进、完整生命周期、诊断返回等未核事项保留|
|[C23](text-entry-source-c23-0041-20261024.md)及[候选摘录](../../analysis/text-entry-source-c23-0041-20261024/candidate-excerpts.json)|四文件必要源行与正常业务/缓冲所有权映射，va/config/位域限制，4个local ZIP成员相等|只独立核选中源行及论证强度，ZIP相等与来源限制继承，不重复包读取/身份认证|
|C15–C22、G01–G04及C23列明的后继覆盖|前置区域准备、门控/变换/提交与消费已有恢复|不沿C14历史未知重开前置/后继GUI函数，不重新搜索完整printf或无种子文本生命周期|
|F07/F08、C23既有complete/宿主/最终ZIP复用边界|本地自报9.2.1候选无自身Git；apps提交不认证ignored解包树，本地ZIP没有可信上游认证链；SIM/服务不认证ROM|全继承，不扩版本、全库或宿主搜索；局部同形不消除既有库差异|

本题缺口只有C23的局部映射与解释强度是否应接受；候选函数名/字段是分析对应，不是原ROM符号、typedef或完整结构布局认证。

## 本轮复核或纠正：逐项接受

候选根 `S=Ubuntu-24.04:/home/slepher/nuttx-ap01-sim/apps/graphics/lvgl/lvgl`。独立流式读取`src/widgets/label/lv_label.c:178–204`、`lv_label_private.h:31–56`、`src/misc/lv_text.c:409–448`、`src/core/lv_obj_private.h:49–73`；四文件118行与C23逐行相同。[review-evidence.json](../../analysis/text-entry-source-review-c24-0041-20261024/review-evidence.json)只存区间、计数、校验和解释边界，不复制第二份源码。

|映射/限制项目|独立源行依据|裁定与ROM边界|
|---|---|---|
|正常入口先invalidate、末尾refresh|label`:178–204`，尤其183/203|接受与C13/C14及已恢复前置/后继的正常顺序相符；不认证原始void返回类型或所有参数前置|
|旧动态文本释放|label`:192–195`，text非空且static_txt==0才free，再置text=NULL|接受静态/借用标志的业务命名候选及局部归还条件；ROM实际门仍按bit4，不将C条件编译布局倒灌原件|
|新缓冲直接持有|label`:198–203`，va_start→helper返回直接写label.text→va_end→static_txt=0→refresh|接受正常路径不再经过另一复制setter，新申请缓冲由label字段持有；不认证完整析构/所有静态文本生产或后续并发生命周期|
|首遍及len+1申请|text`:409–415,438–445`：va_copy供首遍，uint32 len接返回；普通分支malloc(len+1)后再格式化|接受与`a008bbd8`正常单缓冲实参形状相符。ROM机器加1仍是32位事实；求长度/终止符空间意图有源语境，不等于已核a0053252完整长度或NUL保证|
|返回值身份|text`:439,445,448`，第二遍用text，return text|接受helper返回原申请buf，label直接保存；不把第二遍formatter返回值误作buf，不认证allocator内部|
|va_copy解释|text`:412–415`对ap_copy调用首遍，`:445`对原ap调用第二遍|接受C23的条件解释：若原RV32 va_list为按值传递的指针形式，copy可能体现为局部/寄存器保存，同起点不证明缺少va_copy。未认证原typedef、后端推进/所指内容、全部格式/64位对齐/浮点ABI；候选copy也不能反向证明ROM这些性质|
|单缓冲配置条件|text`:418–437`为Arabic/Persian分支，增加raw_txt、转换计数、第二申请/处理和raw释放；`:438–446`普通分支|接受ROM已核正常形状与普通分支相容，不能认证原宏名/.config或全脚本支持；不执行配置探测|
|label/基类配置布局|label private`:32–54`含obj/text、hint/selection条件字段；obj private`:54–61`含style cache/object ID条件字段|接受布局受配置影响。不能从text@2c反推出完整sizeof、hint/selection开关、枚举大小、全部基类或位域ABI|
|静态标记位域差异强度|label private`:51–52`是long_mode:3，随后uint8 static_txt:1|接受C23限定：普通连续低bit分配时可解释为bit3，但混合enum/uint8位域实际布局未编译验证。本文不声称已测得候选mask=8；ROM+5c mask10来自C13/C14独立证据，始终保留。不能因此认定某版本/厂商改动或完整布局相同|
|NULL/申请失败和诊断|label`:180–190`有断言和NULL fmt刷新；text`:440–443`申请失败return NULL|接受不把候选补成ROM这些分支。复核范围是正常非空/申请成功路径；不扩大整体等价、诊断返回政策或做NULL/失败实验|

C23没有需要纠正的技术结论。特别是“清静态文本标志”可作为行为/所有权对应，并不意味着两个声明的位号和对象布局相同；来源伪代码不能替代ROM保存/重读顺序。

## 真正新增与来源强度

新增ROM功能0、ISA规则0、函数导出0、精确来源认证0、未改可排除项0。11项源合同检查和118行相等性属于独立复核，不重复计为业务恢复；C13/C14字节合同与C15–C22/G01–G04后继完全继承。

事实为候选当前必要行与留存一致、存在va_copy/普通和Arabic条件分支、label与obj配置字段及bitfield声明。推断为两个已核ROM入口与对应LVGL函数家族的正常文本更新/持有形状相符。未知为原ROM精确版本/修改来源、编译配置/位域分配、va_list ABI及formatter/allocator完整合同。C23本地ZIP相等结果仅继承为本地包一致性，不升级上游真实性或ROM出处。

## 未闭精确边与实际验证

仍未知ROM精确构建、static mask与候选声明差异的确切归因、完整对象大小/布局、长度/NUL/va推进和格式能力、所有文本更新/析构与运行期显示完成。正常缓冲归label的接入已得到局部来源对应，不表示完整文本系统或所有生命周期闭合。

[review.py](../../analysis/text-entry-source-review-c24-0041-20261024/review.py)通过：四文件118行独立逐行相等、11项源合同及边界检查。只用WSL已授权require_escalated固定本地读取，不导入/执行候选或生产脚本，不读取ROM/ZIP、不编译探测va或位域、不做完整printf/GUI恢复。JSON、报告链接及`git diff --check`通过。

本题独立复核闭合。唯一后续建议是保留mask10/位域与va/config未知，只有获得原始构建配置或直接ABI来源材料时才收窄对应边界；当前不再派同一源行或无种子的formatter/GUI全库搜索。
