# C23：文本格式化入口局部来源认证

`a0091ee4` / `a008bbd8` 的正常非空对象、非空格式串、申请成功合同，与明确本地LVGL 9.2.1候选 `lv_label_set_text_fmt` / `lv_text_set_text_vfmt` 的对应源行相符：先失效原区域，释放旧动态文本，取得新申请缓冲并由label持有，清静态文本标志，随后刷新；下层先求长度、申请len+1、第二遍格式化、返回缓冲。函数名/路径另有C13/C14 ROM自报字符串支持，来源家族可识别。具体布局、配置、精确版本与完整formatter/allocator仍未认证，新增ROM功能0、整库排除0。

基线 `0a1cf0a62f3fba83f863d10d1361dc3f4b9f7fd5`，独立树 `re0041-c23`、分支 `codex/re-0041-c23`。使用 reverse-engineer-anything 技能，只读主仓ROM、留存证据与指定本地候选，未开共享REA target/数据库，未执行ROM、模型、SIM、构建、回放、设备或外网，没有下级agent。仅写本报告及独占analysis，不改共享/主树/生产ROM配置模型/候选，不撤销其他agent改动。下文字段/伪代码是恢复表达，不是原源码或ABI认证。

## 继承结论：已有 → 行为 → 局限 → 实际缺口

|已有出处|行为与证据局限|本轮处理|
|---|---|---|
|[C13](text-update-entry-c13-0041-20261023.md)、[C14](text-update-entry-review-c14-0041-20261023.md)|两个入口166B/140B、a2..a7连续va保存区、text+2c、flags+5c bit4、两遍调用与申请/释放原序已独立接受；当时两目录未找到本地源码|行为直接继承，不运行旧验证器、不重导函数。本轮实际缺口是现有明确候选的源行与所有权/布局比较|
|C13/C14原名字符串与历史extent|`lv_label_set_text_fmt`@a02647f4、label源码路径@a02641a0；`lv_text_set_text_vfmt`@a0263794、text源码路径@a0263224；extent Evidence `ev_9bebf4d87defa0d1c2a1cf83c013b26dbd39471d91a976b647a8536709e3b442`、`ev_88c00ee419366a48bd34b527f212e68bfde147e2cf7fd33216cbbee0edeb3306`|支持命名/边界，不能单靠字符串认证未改源码；本轮继承，不复制字符串账|
|[C15](text-precondition-c15-0041-20261023.md)/[C16](text-precondition-review-c16-0041-20261023.md)、C17–C22、[G01](region-transform-flow-g01-0041-20261023.md)/[G04](invalidation-submit-review-g04-0041-20261023.md)|a00dddf4已解释区域准备，a00ddbf6及后续门控/变换/提交/消费已有后继恢复，不能沿C14历史“未知”重开|全部继承，不重复区域或GUI恢复；这些后继未解决本题两个格式化入口的源码对应|
|[F07](display-source-auth-f07-0041-20261023.md)/[F08](display-source-review-f08-0041-20261023.md)|明确本地LVGL候选根与zip、版本身份局限，显示/event差异已知|身份直接继承；其局部来源表不覆盖本题label/text入口，不把显示匹配或差异推广所有函数|
|[宿主报告](multi-screen-app-host-0041.md)、旧charge/guide/system/weather complete|已有文本格式调用命名与服务/业务覆盖；本轮限定complete地址/符号检索命中这四份旧材料|调用或服务覆盖不能认证两个ROM函数内部与候选等价，不重做宿主/最终ZIP或服务实现|

有界后继报告检查列在 [static-result.json](../../analysis/text-entry-source-c23-0041-20261024/static-result.json)。未命中精确source token只约束所列文本，不宣称全历史无来源研究。本轮采用已知合同，不以旧源码目录负搜索推断当前候选不存在。

## 本轮复核或纠正：必要源行、布局与所有权

`S`缩写 WSL `Ubuntu-24.04:/home/slepher/nuttx-ap01-sim/apps/graphics/lvgl/lvgl`。继承F07/F08：解包树无独立Git，apps commit不能认证ignored源码；自报9.2.1与现存zip相等不证明下载链、签名或ROM版本。只读四个明确文件必要行，与同父 `v9.2.1.zip` 对应 `lvgl-9.2.1/<path>` 成员在内存比对，4/4相等；不解包/复制整源码，不新做hash清单。必要行及绝对路径见 [candidate-excerpts.json](../../analysis/text-entry-source-c23-0041-20261024/candidate-excerpts.json)。

|ROM已核局部合同|候选相对S精确源行|对应与限制|
|---|---|---|
|a0091ee4的obj/fmt/变参入口，前置a00dddf4，末尾a009166e|`src/widgets/label/lv_label.c:178–204`|候选为void `(lv_obj_t*,const char*,...)`，先invalidate，末尾refr_text；ROM命名字符串、正常调用原序与之相符。原RV32寄存器保存和va栈构造仍由C13/C14证明，不由主机C类型反推ABI|
|旧text非0且flags bit4为0才free，随后清旧槽|`lv_label.c:192–195`|候选条件 `label->text != NULL && label->static_txt == 0`、先free再置NULL，局部所有权行为相符。支持bit4业务命名为静态文本标志，但不能直接认证候选位域mask等于ROM|
|直接保存下层申请结果到obj+2c，清flag再刷新|`lv_label.c:197–203`|候选va_start→text_vfmt→va_end→static_txt=0→refr_text；新缓冲直接成为label文本，不再交另一复制setter。正常路径所有权从helper返回交给label字段；helper不额外释放新缓冲。完整析构/静态文本生产与所有后继所有权仍不在本轮|
|a008bbd8首遍a0053252(0,0,fmt,va)，a0+1申请，再第二遍(buf,size,fmt,va)，最终返回buf|`src/misc/lv_text.c:409–415,438–448`|候选先va_copy，`uint32_t len=lv_vsnprintf(NULL,0,fmt,ap_copy)`，结束copy，再在非Arabic分支malloc(len+1)、格式化并return text。与正常单buffer形状相符，支持求长度/终止符空间的源码语境；不认证a0053252完整vsnprintf语义或实际NUL写入|
|普通单缓冲路径与配置分支|`lv_text.c:417–446`|候选Arabic/Persian开关开启时另有raw_txt、二次申请/处理/释放，ROM本入口没有这套调用链。只能说ROM正常形状对应候选非Arabic分支，不能据此认证ROM原宏名/配置或整文本脚本支持|
|label字段顺序|`src/widgets/label/lv_label_private.h:31–56`|候选obj基类后是text，再dot/dot_end、可选hint/selection、size_cache/offset、位域。ROMtext@2c、flags byte@5c是独立事实；候选有配置字段，不用text位置推导完整label sizeof或hint/selection已启用|
|基类布局条件|`src/core/lv_obj_private.h:49–73`|style cache、object ID等条件字段可改变obj大小，继而移动label.text。没有读取/构建ROM配置，不能把本地源码声明当精确ROM结构|

### 不能被来源形状掩盖的边界

静态文本标志：ROM `a0091f4e/1f52` 读 `obj+5c` 后AND10，`1f74/1f76` AND~10并以byte写回；候选 `lv_label_private.h:51–52` 声明 `long_mode:3` 后接 `static_txt:1`。普通连续低bit分配时后者会是bit3，而ROM使用bit4。本轮不执行编译器布局探测；混合enum/uint8位域实际分配受ABI影响，所以裁定是**候选声明不能直接证明ROM位域布局相同**，不虚称已测得候选二进制mask。ROM原mask10始终保留，也不将此差别归因于厂商或特定上游版本。

va_list：候选显式va_copy供首遍使用，原ap供第二遍；ROM传同一保存起点到两遍。对于按值传递的RV32指针式va_list，源码copy可能只体现为寄存器/局部保存，不能单凭“同地址”宣布缺少va_copy或算法差异。反过来也不能仅凭源码证明a0053252不推进/修改任何所指内容、覆盖所有格式或64位/浮点传参。当前只接受正常入口实参数据流与候选意图对应。

候选 `lv_label.c:180–190` 另有fmt断言及NULL格式串刷新分支；`lv_text.c:440–443` 有申请失败返回NULL。C13/C14已限定ROM正常非空/申请非零合同、诊断返回属性未知。本轮不以候选补写ROM这些分支、不做NULL/失败实验，也不据它们推断缺陷。函数整体等价、原始void typedef及全部返回政策均未认证。

必要正常伪代码（不是原源码）：`invalidate(obj); if (old_text && !static_flag) { free(old_text); text=NULL; } text=text_vfmt(fmt,va); static_flag=0; refresh(obj);`；下层 `len=format(NULL,0,fmt,va_copy_context); buf=allocate(len+1); format(buf,len+1,fmt,va); return buf;`。ROMflags仍按bit4、text仍按+2c、清flag与字段写回原序以C13/C14为准；该来源伪代码不替代机器ABI。

## 真正新增与恢复程度

新增仅为四文件必要源行、局部函数/所有权对应和布局/配置/va解释边界；新增ROM功能0、ISA规则0、完整函数导出0、确证未改可排除项0。C13/C14正常机器合同无需纠正，C15–C22/G01–G04后续保持继承，没有新恢复printf、字体、分配器、刷新或完整GUI。

事实：原件与C14的101条留存指令bytes一致；明确候选源行与4个local zip成员相等；候选有上述条件字段/配置分支。推断：两个ROM入口属于对应LVGL函数家族，正常业务及新缓冲归label的局部所有权与候选相符。未知：精确ROM版本/修改来源/配置、完整label/基类布局及位域ABI、formatter长度/NUL/va推进全合同、allocator内部、所有文本更新/析构与并发寿命、实际显示完成。

## 未闭精确边、一个后继与验证

本题来源主问在局部正常合同内得到答案，未把相符升级为完整未改源码。布局mask10与候选声明的确切差异归因仍未知；配置与失败分支不认证。a00dddf4后继已被后续报告恢复，不作为新题重开；本轮不另找无种子的GUI/字体/文本所有权全生命周期。

单一后继建议：新独立agent只核本题正常源行映射、位域/config/va_copy解释强度，保持C13/C14机器合同与G01/G04继承，不扩formatter/allocator/GUI。当前不自行接题。

[verify.py](../../analysis/text-entry-source-c23-0041-20261024/verify.py)静态核验通过：只将C14的101条原字节与主仓 `roms/0041/ap01-1.0.2_0041.bin`（base9ffff000）比较，不重复函数导出；4个候选文件与既有zip成员相等；限定后继报告source覆盖检查及源行关键合同检查通过。只读WSL访问使用已授权require_escalated，没有执行候选、ROM或模型。报告相对链接、`git diff --cached --check`通过。本轮为研究者自核，技术接受待独立复核。
