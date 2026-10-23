# C25：区域变换局部候选来源认证

**G01/G02 已核区域变换与本地 LVGL 9.2.1 候选的四点/递归/缩放旋转正常合同局部相符，但五个属性编号明确不同：候选108–112，ROM110–114。** 四word区域、flags=1当前→父链、右下+1且写回不减1均有候选对应。新增ROM功能0、既有ROM语义纠正0、确证未改可排除项0；差异不归因到具体版本或厂商修改，不作整库排除。

2026-10-24；基线 `29002d0`，独占树 `re0041-c25`、分支 `codex/re-0041-c25`。采用 reverse-engineer-anything 技能，继承G01/G02原字节与厂商指令合同，不读取/导出ROM或运行其脚本。本轮仅只读既有本地候选必要源行；没有共享REA target/database、模型/固件执行、SIM、构建、历史回放、设备、外网或下级agent。只写本报告及同名analysis，不改共享文档/主树/生产代码/ROM/配置/模型/候选，不撤销其他任务改动。函数名、字段名的ROM映射为分析推断，候选不等于原源码。

## 继承结论：已有 → 行为 → 局限 → 实际缺口

| 已有出处 | 已解释行为/证据层次 | 本轮处理 |
| --- | --- | --- |
| [G01](region-transform-flow-g01-0041-20261023.md)、[G02](region-transform-review-g02-0041-20261023.md) | `a00dca48`四点→父链/节点变换→signed包围框；11核心、属性读取和32位截断/ASR/厂商字已有完整小闭包及独立复核 | 全继承，不重新恢复11函数、表、元数据或原字；实际缺口仅候选源行映射与差异/配置边界 |
| [C22](region-gating-review-c22-0041-20261023.md)与G01/G02后续成果 | C22当时只核两处`a00dca48(obj,area,1)`调用；该内部未知后来已由G01/G02解决 | 不再把C22历史未知当当前功能缺口；两caller裁剪、门控直接继承，不扩提交/物理刷新 |
| [A43](image-cache-source-a43-0041-20261024.md)/A44、[A51](image-cache-drop-source-a51-0041-20261024.md)、F07/F08 | 既有本地LVGL候选根、自报9.2.1及来源局限；各自具体cache/display合同 | 仅沿用候选身份，不把cache局部相符推广到区域属性；近期来源报告无本题区域源行映射可直接替代 |
| G01/G02原函数extent/callee与ROM路径字符串 | `lv_obj_style.c/lv_obj_get_style_prop`支持家族线索，厂商语义依据既有私有模型；不是准确源码/版本认证 | 引用可靠合同，不复核厂商字、不扩上游ISA或源码版本；候选符号仅作局部映射 |
| G01/G02已完成的旧complete/最终验收/ZIP复用边界；本轮近期`*source*.md/*complete*.md/*final*.md`区域词项查询 | 旧SIM/照片/服务重建不认证ROM；未取得已覆盖本题源码认证的近期报告 | 不重解ZIP、不执行旧回放，不把有界无相关匹配说成此前从未分析 |

证据四层分开：既有已验收原字合同直接继承；旧清单/反编译/路径仅定位；SIM/照片/安全替代不证明ROM；本轮新证据仅指定候选源行。没有恢复新ROM行为。

## 本轮复核或纠正：匹配、差异、配置条件与未知

候选根沿用 `S=Ubuntu-24.04:/home/slepher/nuttx-ap01-sim/apps/graphics/lvgl/lvgl`。本轮限定读取11个明确文件、271行，原文见 [candidate-excerpts.json](../../analysis/region-transform-source-c25-0041-20261024/candidate-excerpts.json)，不保存整文件、不重查ZIP相等或版本身份。`lv_obj_pos.c`/`lv_area.c`之外仅取所需类型、属性、flags、百分比和缩放常量/短getter，不重做完整style查找、正弦源码或刷新链。

| 项目/类别 | 候选精确源行（相对S） | 与已核ROM合同的对应/限定 |
| --- | --- | --- |
| **匹配：四word区域与四点** | `src/misc/lv_area.h:31–47`；`src/core/lv_obj_pos.c:796–805` | `lv_area_t={int32 x1,y1,x2,y2}`；`lv_point_t={int32 x,y}`，对应area四word/point两word。构造`{x1,y1},{x1,y2+1},{x2+1,y1},{x2+1,y2+1}`后调用点数组(count4)，对应`a00dca48`已核8word栈数组。候选C普通RV32布局相容，不以源码重定义整个ROM对象 |
| **匹配：写回无减1** | `lv_obj_pos.c:807–810`；`src/misc/lv_math.h:159–165` | MIN4/MAX4直接写x1/x2/y1/y2，不作末尾−1或外层identity早退；int32操作数的`<`/`>`与ROMsigned extrema相符。宏形式不要求ROM使用同一比较树/重读顺序，原实际store顺序沿G01/G02 |
| **匹配：flags与父链原序** | `src/core/lv_obj_pos.h:26–38`；`lv_obj_pos.c:777–794` | RECURSIVE=1、INVERSE=2；flags1不逆向，先当前transform再parent递归；inverse时先递归再当前。对应`a00dc9ba`。候选返回void和caller不消费返回相容，不把ROM残余SLT返回值命名为成功码 |
| **匹配：mode的家族解释** | `src/core/lv_obj_draw.h:31–35`；`lv_obj_pos.c:781–782` | NONE/SIMPLE/TRANSFORM依次0/1/2，只有TRANSFORM调用节点变换；与ROMmode2相符。未认证候选`lv_obj_get_layer_type`及完整spec_attr布局，不能从此证明ROM aux位域/对象ABI等于候选编译布局 |
| **匹配：属性用途和安全比例** | `lv_obj_pos.c:1151–1164`；`src/core/lv_obj_style_gen.h:106–134`；`src/core/lv_obj_style.h:290–300` | angle→scale_x→scale_y，safe getter正数原值否则1，节点又保留零变1；无变换先返回，不读pivot，之后读pivot_x/y。对应`a0083796/a019dfd0/a019dff0/a00dc862`的用途/顺序，但属性**编号不同**，见下表 |
| **匹配：scale基准/默认局部** | `src/misc/lv_style.h:47–48`；`src/misc/lv_style.c:357–361` | LV_SCALE_NONE=256，两个scale默认值为256；与G01/G02的0x100相符。本轮没有认证整个默认表或全部style继承，其他ROM默认值继续按G01/G02引用 |
| **匹配：支点百分比与逆向公式** | `lv_obj_pos.c:1166–1182`；`lv_area.h:206–234`；`src/misc/lv_area.c:512–520` | 特殊坐标类型shift29；百分比排除最大plain sentinel，正负编码分界0xfffffff；尺寸为high−low+1，百分比乘后/100，再加obj.coords低边；inverse用`(65536+scale−1)/scale`和负angle，最后传`!inv`作zoom_first。与既有ROM形状局部相符，不以C表达式承诺任意输入位级等价 |
| **匹配：整数点变换形状** | `lv_area.c:449–510`、`:441`；`src/misc/lv_math.h:23` | identity返回、先减pivot；无角度乘scale后>>8；角度仅单次修正、/10插值四次sin；TRIGO_SHIFT15/TRANSFORM_SHIFT10，插值后>>5；scale_first与旋转后scale两分支分别>>18。不重做sin函数/表或11函数闭包，不认证标准数学库来源 |
| **配置条件：宽度** | `lv_area.h:31–47`；`src/misc/lv_types.h:78–82`；点函数参数/局部声明 | area/point和angle/scale明确int32；count为size_t、循环i为uint32，普通RV32下与ROMword入参相容。LV_USE_FLOAT只在所选声明切换`lv_value_precise_t`，这里用的是`lv_point_t`，不能因float配置把四word区域或点运算升级为浮点/64位 |
| **配置条件：C算术与ABI** | 上述int32算式及flags enum声明 | 源码signed溢出不自动定义为RV32模2^32，负数右移受实现影响；未取得原编译输入，不把C源码当任意数值的截断/ASR证明。ROM低32位/ASR仍由G01/G02独立合同决定；enum packing也不能解释下述显式数值编号差异 |
| **未知** | 本题源行不能解决 | 精确ROM版本/commit/宏/完整对象和style ABI、差异归因、属性setter/aux生产释放、并发串行化、整个style/三角函数来源、下游提交/物理刷新均未知 |

五项显式编号差异如下；候选编号取`lv_style.h:305–309`，ROM编号直接继承G01/G02，**本轮没有重读ROM**：

| 对应属性用途/候选符号 | 本地候选 | 已核ROM | ROM−候选 |
| --- | --- | --- | --- |
| `LV_STYLE_TRANSFORM_SCALE_X` | 108 / 0x6c | 110 / 0x6e | +2 |
| `LV_STYLE_TRANSFORM_SCALE_Y` | 109 / 0x6d | 111 / 0x6f | +2 |
| `LV_STYLE_TRANSFORM_ROTATION` | 110 / 0x6e | 112 / 0x70 | +2 |
| `LV_STYLE_TRANSFORM_PIVOT_X` | 111 / 0x6f | 113 / 0x71 | +2 |
| `LV_STYLE_TRANSFORM_PIVOT_Y` | 112 / 0x70 | 114 / 0x72 | +2 |

这是局部合同对应下的明确数值差异，不是ROM几何行为纠正；不把相同数字110在两者中强行解释成同一属性。显式枚举值不随enum存储宽度改变，当前证据不足以将整体+2归因于版本、厂商新增属性或其他生成输入。无需为归因扩版本搜索。

现有ROM与候选均是在同步栈数组上做几何处理；area由caller借用写回，点数组/pivot为局部，持久对象/属性只借用读取。本轮不改变G01/G02所有权结论，不把候选形式变成对象生命周期或全程串行化保证。原始GUI物理坐标/刷新输出也不由四点矩形映射认证。

## 真正新增与来源分类

新增ROM功能0、ROM语义纠正0、厂商规则/模型修改0、ROM函数导出0。新交付仅为区域变换家族的局部候选源行映射与五属性编号差异；旧C22内部未知已被G01/G02解决，不重计为新恢复。

| 来源分类 | 裁定 |
| --- | --- |
| 确证ROM未改、可排除继续恢复 | 0项；局部几何一致且存在明确属性编号差异，不能排除整个LVGL或变换库 |
| 候选局部合同相符 | 四word/四点/+1无−1、flags递归顺序、mode2家族、scale/pivot及整数点变换形状相符；受上述配置与完整ABI限制 |
| 家族可识别、版本未知 | 支持LVGL对象区域变换家族及候选符号映射；本地自报9.2.1不等于ROM版本 |
| 差异/封装/未认证部分保留 | 五属性编号整体+2；C算术域、完整style/对象ABI和构建来源未认证；F07/F08已知其他差异继续继承 |

## 实际验证、未闭精确边与后续闭包

按本轮已有授权以`require_escalated`只读本地WSL源文本，未修环境或访问网络。初步定位限制在已知LVGL区域/style/header文件，命中后收敛到固定源行；最终 [read_candidate.py](../../analysis/region-transform-source-c25-0041-20261024/read_candidate.py) 仅流式读取所列271行，不复制整源码，不导入/执行候选。

本路 [verify.py](../../analysis/region-transform-source-c25-0041-20261024/verify.py) 通过：11文件/271选中行、9项源合同检查，五属性数值与继承ROM比较均为+2。结果 [verification.json](../../analysis/region-transform-source-c25-0041-20261024/verification.json)。校验源文本/行段、flags、四点与写回、递归顺序、mode枚举、safe scale、百分比/类型和整数变换必要形状；不运行算术输入，不作位级编译实验。JSON解析、报告相对链接和 `git diff --check` 通过；待新独立技术复核。

本题来源认证已在“局部合同相符+明确编号差异”范围内闭合。差异的准确来源、原构建输入仍缺证；没有属性setter或准确版本新种子，不扩物理刷新/GUI/整库。单一后续建议：新独立agent只核本报告源行映射、五编号差异和C算术/float配置限定，不重做G01/G02的11核心或ROM厂商字。是否派发由管理者决定，本轮结束。
