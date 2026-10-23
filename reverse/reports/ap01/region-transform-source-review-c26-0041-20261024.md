# C26：区域变换局部候选来源独立复核

限定接受C25，无语义纠正，新增功能0。候选四点/父链/比例与旋转正常形状支持G01/G02的局部来源映射；五属性按相同用途对应后，候选108–112、ROM110–114确实各差+2。该显式数值差异不能由enum存储宽度解释，不能据此归因特定版本或厂商改动，也不能认证ROM为未改本地9.2.1。整库排除0。

基线 `34ff6baef6f2e2ac434a3be9ea703e78521c6140`，独立树/分支 `re0041-c26` / `codex/re-0041-c26`，未参与C25生产。使用 reverse-engineer-anything 技能，只读已有可靠合同、留存候选与明确本地源行；未新开/切换共享REA target/数据库，未读/重导ROM、执行模型/候选/固件/SIM/构建/回放、连接设备或外网，未创建下级agent。仅写本报告与独占analysis，不改共享/主树/生产ROM配置模型/候选，不撤销他人改动。函数/字段映射为分析表达，不等于原源码认证。

## 继承结论：已有 → 行为 → 局限 → 精确缺口

|已有出处|已有行为与证据局限|本轮处理|
|---|---|---|
|[C25](region-transform-source-c25-0041-20261024.md)及candidate-excerpts.json、verification.json|11个明确候选文件271行已有局部映射、五属性+2差异与C算术/config限定；作者自核待复核|独立重读这些必要行并核来源主张，不运行C25脚本、不再保存一份源码片段|
|[G01](region-transform-flow-g01-0041-20261023.md)、[G02](region-transform-review-g02-0041-20261023.md)|11函数原字节、厂商字、四点/递归/整数变换和五属性用途已恢复并独立接受|原行为全继承，不复核11函数/厂商字/正弦表；ROM五编号由G02已核getter与用途引用|
|[C22](region-gating-review-c22-0041-20261023.md)及G01/G02后继|两处a00dca48(obj,area,1)接入及后续内部闭包已存在；不能由旧未知推新缺口|直接继承，不重开门控、提交或物理刷新|
|[F07](display-source-auth-f07-0041-20261023.md)/[F08](display-source-review-f08-0041-20261023.md)、[A43](image-cache-source-a43-0041-20261024.md)/[A44](image-cache-source-review-a44-0041-20261024.md)|本地候选根、自报9.2.1、ignored源码/zip身份局限与其他局部来源合同已有|身份与限界继承，不重做整包/版本认证，不把cache/display来源映射当本题属性证明|
|G01/G02/C25所留旧complete/最终ZIP/SIM复用边界|旧服务/照片替代不能认证ROM几何ABI；近期定向查询未取得可替代本题的来源表|继承搜索边界，不重解ZIP/回放/泛扫，也不把负结果说成全历史从未分析|

本轮精确缺口仅为C25源行映射与解释强度的独立接受。四类证据保持分开：可靠原字节行为继承；反编译/extent/字符串只定位；SIM替代不认证ROM；新证据只为必要本地源行核对。

## 本轮复核或纠正：逐项裁决

候选绝对根沿C25为 `Ubuntu-24.04:/home/slepher/nuttx-ap01-sim/apps/graphics/lvgl/lvgl`，下表路径相对此根。独立重读11文件的原271行，与C25留存逐行一致，没有复制整文件或重查zip/版本。结果见 [review-result.json](../../analysis/region-transform-source-review-c26-0041-20261024/review-result.json)。

|C25主张|必要候选源行与继承ROM依据|判定/局限|
|---|---|---|
|四word区域、两word点|`src/misc/lv_area.h:31–47` 明确area与point字段为int32；G02已核16B area、8B点步长|接受普通RV32布局相容，不认证完整obj/style布局|
|四点右/下+1、极值写回不减1|`src/core/lv_obj_pos.c:796–810` 构造四点，调用count4，再直接MIN4/MAX4写area；`lv_math.h:159–165` signed坐标用<、>比较|接受。候选宏不证明ROM同一比较树/重读次数；原存储顺序与signed机器行为沿G02|
|flags与当前/父链原序|`lv_obj_pos.h:26–38` 显式0/1/2/3；`lv_obj_pos.c:777–794` inverse时父先当前后，否则当前先父后；G02已核flags1当前→父|接受。flags1无inverse，不将残余a0命名成功返回；候选void不能认证ROM原typedef|
|mode2变换家族|`src/core/lv_obj_draw.h:31–35` NONE/SIMPLE/TRANSFORM依序0/1/2，pos.c:781–782只在TRANSFORM调用当前节点变换；ROMmode2关系沿G02|接受用途映射，不认证spec_attr位域ABI或getter完整来源|
|角度/比例/支点顺序与safe getter|`pos.c:1151–1164` angle→safe sx→safe sy，identity先返回后取pivot；`lv_obj_style.h:290–300` signed正数保持，否则1；`lv_obj_style_gen.h:106–134`把五用途映射到属性符号|接受形状和用途；具体编号按下表保持差异，不把相同整数强配成相同属性|
|scale基准与默认|`lv_style.h:47–48` SCALE_NONE=256，`lv_style.c:357–361`两个scale默认256|接受局部对应G02的100；不将本次升为整个默认属性表或全部继承行为认证|
|百分比支点与inverse公式|`lv_area.h:206–234` shift29、plain mask/sentinel与正负编码；`pos.c:1166–1182`百分比乘尺寸/100、加低边、inverse整数倒数及负angle；`lv_area.c:512–520`尺寸high−low+1|接受正常机器形状家族。静态常量代数确认PCT_POS_MAX=0fffffff，但没有运行变换输入或扩大所有数值域证明|
|点变换缩放/旋转形状|`lv_area.c:449–510` identity、减pivot、无角度>>8、单次角度修正、四sin插值、zoom_first分支；math.h:23的TRIGO_SHIFT15与area.c:441的10|接受局部来源对应；不重新核正弦实现/厂商字或任意输入位级等价|
|坐标与count宽度|area.h明写int32字段；area.c签名angle/scale为int32、count为size_t、i为uint32；`lv_types.h:78–82`只在precise别名切float/int32|接受C25限定。LV_USE_FLOAT不把这里的lv_point_t/area变成float；count与ROMword相容须普通RV32 size_t前提，不以宿主64位替代|
|C算术与原机器规则|候选signed乘加/移位与G02已证RV32低32位/ASR属于不同证明层|接受C25局限：源码signed溢出不定义任意输入模2^32，负数右移/ABI受编译输入影响；保留G02机器合同|

五项差异逐项独立核对如下。候选显式编号来自 `src/misc/lv_style.h:305–309`；ROM值引用G02已核的比例getter6e/6f、角度getter70、支点71/72及对应调用用途，未重新解码ROM。

|用途/候选符号后缀|候选十进制|ROM十进制|差|
|---|---|---|---|
|TRANSFORM_SCALE_X|108|110|+2|
|TRANSFORM_SCALE_Y|109|111|+2|
|TRANSFORM_ROTATION|110|112|+2|
|TRANSFORM_PIVOT_X|111|113|+2|
|TRANSFORM_PIVOT_Y|112|114|+2|

这是在用途映射成立后的具体数值差异：例如候选110是rotation，ROM110是scale_x，不能按同号直接套名。enum packing会影响存储/ABI，不改变这些显式常量的数值；它不能解释本表。差异可能涉及其他上游版本、属性生成输入或修改，当前无依据二选一或指定厂商行号。无需为此扩大版本搜索。

无需要纠正C25的技术结论。同步栈area/point/pivot借用与未持久保存、未分配释放的所有权合同沿G02，不因候选源码形式推断对象最终寿命、串行化或实际屏幕刷新。

## 真正新增

新增功能0、ISA规则0、模型修改0、完整ROM函数导出0、确证未改可排除项0。11文件/271行重读与11项源合同/常量检查仅为独立复核，五项+2为对C25已有差异的接受，不重复计功能。没有新恢复style、正弦、全部GUI或物理刷新。

## 未闭精确边、后继与验证

仍未知：精确ROM版本/commit/宏与编译输入、完整对象/style ABI、五项+2的来源归因、属性setter/aux生产释放、并发规则、整个三角函数家族、下游物理刷新。候选局部相符和原字节合同均不能自动解决这些边界。

单一后继闭包：只有出现可定位原构建或属性生成输入时，再解释五属性+2的来源；当前没有该种子，不泛扫版本，不重做11函数或物理刷新。当前局部来源验收已闭，是否另题由管理者决定，本轮不自行接题。

[review.py](../../analysis/region-transform-source-review-c26-0041-20261024/review.py)通过：只读本地WSL指定11文件/271必要行，与C25留存完全一致；独立检查四点、flags/递归、mode、getter、percent/宽度及五属性+2共11项。脚本不读取ROM、不导入C25验证器、不执行任何几何输入或候选。报告相对链接、JSON和 `git diff --cached --check`通过。结论只接受C25局部来源主张及限界，不升级精确版本/整库认证。
