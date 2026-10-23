# A44：默认 image-cache 局部来源映射独立复核

2026-10-24；基线 `6385a09`，独立树 `re0041-a44`、分支 `codex/re-0041-a44`。**限定接受 A43 的局部源码映射、调用层级和字段/enum ABI 保留；无需语义纠正。新增 ROM 功能0，确证未改可排除项0。** 候选局部合同相符不能认证 ROM 为未改 LVGL 9.2.1，也不能消除 F07/F08 已知差异。

应用 [reverse-engineer-anything skill](C:/Users/cogic/.agents/skills/reverse-engineer-anything/SKILL.md) 的既有证据优先与事实/推断/未知区分规则。只读 A43 已选9文件的必要源行；没有打开/切换 REA target/database、读取 ROM、运行候选代码或历史脚本，不新增 REA Evidence ID。无 SIM、构建、回放、设备、外网或下级 agent；没有改主树共享、生产代码、ROM、配置、模型或候选。

## 继承结论：已有→行为→局限→本题缺口

|已有出处|已有行为与证据|本题处理/局限|
|---|---|---|
|[A43](image-cache-source-a43-0041-20261024.md)|默认 image-cache、size 型 LRU/RB、entry/header、key、计量、访问次序和 cleanup 的具体候选对应；9本地成员与本地 ZIP 相等|本轮只独立核源码映射和论证强度；包相等结果继承，不重读 ZIP、不扩库搜索|
|[A23](png-session-lifecycle-a23-0041-20261023.md)/[A24](png-session-review-a24-0041-20261023.md)、[A27](image-cache-cleanup-a27-0041-20261023.md)/[A28](image-cache-review-a28-0041-20261024.md)|PNG key/payload、session/pixel 所有权、默认backend、ref/invalid及移出→cleanup→free 原字节合同|可靠 ROM 合同直接继承；不再恢复函数或用源码补诊断/失败门|
|[A30](image-cache-accounting-a30-0041-20261024.md)/[A32](image-cache-accounting-review-a32-0041-20261024.md)、[A34](image-cache-order-a34-0041-20261024.md)/[A36](image-cache-order-review-a36-0041-20261024.md)、[A38](image-cache-key-a38-0041-20261024.md)/[A40](image-cache-key-review-a40-0041-20261024.md)|首word计量、PNG逻辑字节单位、链/树及backlink、头快路径/命中提升/零ref victim、class U8与比较方向|本轮只核 A43 声称的相应源行；不重读原字节、厂商字或 helper，不以候选枚举替代 ROM LBU|
|[F07](display-source-auth-f07-0041-20261023.md)/[F08](display-source-review-f08-0041-20261023.md)、[D13](pixel-source-auth-d13-0041-20261024.md)/[D14](pixel-source-review-d14-0041-20261024.md)|自报9.2.1的本地候选身份局限、display/list差异、draw-buffer及size slot局部对应|候选无自身Git、父apps提交不认证被忽略解包树、本地ZIP无可信上游认证链等限制完整继承；不重做版本/来源身份|

原字节合同是既有静态观察；旧反编译/候选只供定位及比较；SIM/照片/服务替代不能证明 ROM ABI；未检到的准确边仍未知。旧 complete/ZIP 复用边界沿 A43/F08，不重复查询，也不作“以前没有分析”的否定断言。本题实际缺口只有 A43 局部来源论证的独立复核。

## 本轮复核或纠正：逐项接受

`S=Ubuntu-24.04:/home/slepher/nuttx-ap01-sim/apps/graphics/lvgl/lvgl`。以下源行相对 S；地址/偏移为十六进制。源函数名是候选命名推断，不是 ROM 符号。独立读取器 [review_source.py](../../analysis/image-cache-source-review-a44-0041-20261024/review_source.py) 按 A43 已选行段流式读取至最后必要行，与 A43 留存逐行比较；没有导入/运行 A43 脚本或候选。结果 [review-evidence.json](../../analysis/image-cache-source-review-a44-0041-20261024/review-evidence.json) 仅存路径、行段、计数和一致布尔值，不重复留存源码片段。

|复核项目|源码锚点|裁定及强度|
|---|---|---|
|创建及三callback；A23 `a008e642..e694→a019855e`|`src/misc/cache/lv_image_cache.c:54..68`、`lv_cache.c:48..65`、`lv_cache_private.h:113..137,146..158`；`lv_cache_lru_rb.c:111..123`|接受：size型class、payload sizeof、compare/NULL create/free与安装顺序相符。十个class指针的次序支持+0c get、+10 add、+14 remove、+20 victim、+24 reserve。声明/初始化不能认证所有槽的ROM函数体|
|默认key及返回ABI；A38 `a0087bc6→a0087b5c`|`lv_image_cache.c:106..131`、`src/draw/lv_image_decoder.h:34..39`、`lv_cache_private.h:47..50`、`lv_cache_lru_rb.c:228..234`|接受：VARIABLE=0、FILE=1；同FILE用strcmp归一，同VARIABLE比较地址，其他同type相等，异type按值排序；rb接同compare。候选返回int8_t，ROM结果/有符号判断仍独立继承，不认证全部调用ABI|
|payload字段、class宽度|`src/draw/lv_image_decoder_private.h:55..64`、`lv_cache_private.h:174..176`|接受条件相容：普通RV32下slot.size、src、src_type、decoded、decoder、userdata可对应+0/+4/+8/+c/+10/+14。1B或4B enum都可能因后续指针对齐而得到24B；24B不证明enum宽度，ROM U8读取不能反向认证候选编译输入|
|entry与payload身份|`lv_cache_entry.c:22..28,54..71,82..119,148..164`|接受pointer/int32/uint32/bool字段次序、ref0/invalid false初始化、data=entry-node_size和entry=data+node_size；delete只free data。cache.node_size=24是payload长度，不能叫整个entry/header长度或证明完整分配尺寸|
|首word计量与reserve|`lv_cache_lru_rb.c:59..68,216..237,304..313,329..341,441..449,458..462`；`lv_cache_private.h:30..35,174..176`|接受：uint32 getter读slot.size，成功add按key加、remove按data减；预算三项和、TOO_LARGE/NEED_VICTIM/OK为1/2/0。slot.size及reserved_size的size_t只有普通RV32限定下为32位，不能套宿主64位。PNG字节单位仍由A30证明|
|树/链双向关联与访问次序|`lv_cache_lru_rb.c:61..68,150..177,228..234,267..288,329..341,416..425`；`src/misc/lv_rb_private.h:27..39`|接受：链node存tree指针、payload尾存链node指针；get_lru_node公式、头比较(data,key)、rb_find后移头、尾向零ref victim、移树→移链/free链→减计量相符。不会用源码概括替代ROM重读、NULL setter门或厂商indexed-load语义；rb color enum/完整布局与平衡算法未认证|
|release、通用失效、驱逐层级；`a019d9f6/a019cfbe/a019d898`|`lv_cache.c:104..117,299..329,332..347`；class声明`lv_cache_private.h:146..158`及表`lv_cache_lru_rb.c:111..123`|接受：release先减ref，零ref且invalid才free_cb(data,user_data)→delete；通用失效get后零ref走remove/free/delete，有ref标invalid再remove；驱逐先victim、空false、否则remove/free/delete。**a019cfbe映射cache_drop_internal_no_lock，不是class.drop_cb。** class仍有独立drop/drop_all槽，本轮不认证其body。普通release不额外remove/扣量；已知userdata=0只属已有调用点|
|image cleanup `a008abb0`|`lv_image_cache.c:133..145`|接受：忽略userdata，decoded带ALLOCATED才destroy，再FILE source副本free；此callback不free payload。raw→对象释放内部继承A25/A26及D13/D14，不因此认证heap或实际触发时序|
|cache后段及OS配置|`lv_cache_private.h:122..137`、`src/osal/lv_os.h:24..40`、`lv_cache_lru_rb.c:61..68`|接受前四word和三callback的局部对照；随后lock、name，而lock由OS分支选择。没有实际ROM编译输入，不能从候选结构计算cache sizeof、填+1c/+20类型或认证rb必在+24；本轮不推断同步行为|

纠正项为空；没有发现 A43 在本题局部映射中需反转的结论。特别是 A43 已明确把十槽声明、部分已核槽、backend drop未知分开，不能把通用失效 helper 的接受扩大为 backend drop 源码认证。

## 真正新增与四类裁定

新增仅为上述限定源行的独立复核证据；ROM功能新增0、ROM语义纠正0。参数、返回、所有权、状态转换、原序及伪代码沿已有独立复核合同，不生成另一份简化伪代码替代它们。

|四类|本轮裁定|
|---|---|
|确证ROM未改、可排除继续恢复|空，0项；本地包相等或多项局部相符均不证明ROM精确构建来源|
|候选局部合同相符|接受上表默认安装、key、首word计量、entry/链关联、命中/victim、release/通用失效/驱逐及image cleanup的限定对应|
|家族可识别、版本未知|接受image-cache与size型LRU/RB家族、内部header/slot及候选函数名映射；不升级为9.2.1原样来源|
|差异/封装/未认证部分保留|本题未发现新硬差异；F07/F08已知display/list差异继续有效。enum/OS完整ABI、diagnostic/assert、未展开backend drop/drop_all等不认证，差异归因未知|

事实：当前9文件456条已选源行与A43留存完全相等、具体声明和代码存在；A43的9成员本地包相等是继承事实，本轮未重做。推断：这些候选符号/字段与已有ROM合同的局部映射。未核：精确ROM版本/commit、可信上游链、编译输入/enum ABI、完整cache/lock/RB布局、动态重配、未展开backend协议、完整树平衡、allocator/diagnostic实现，以及真实命中/驱逐/ref运行时序。没有新增整LVGL、libc、heap、NuttX或标准库来源排除。

## 验证、断边与结束

按已有明确授权使用 `require_escalated` 完成本地WSL只读读取；未修环境。只运行本轮读取器及交付检查：9文件/456选中行一致，证据JSON解析、报告相对链接、独占差异和 `git diff --check` 检查通过；没有重跑旧ROM或来源核验脚本。本报告是A43的独立技术复核，本轮脚本自身仅作交付自检。

本题局部来源映射验收完成，来源强度保持候选等级。剩余精确断边是ROM实际编译输入/完整ABI及未展开backend槽；不能靠当前候选补齐。若另立后续，只沿真实backend drop/drop_all槽的已定位callee作有界合同核验，先查旧覆盖；无需再恢复key、计量、LRU、cleanup或扩版本搜索。本agent到此结束，由管理者决定去重补位。
