# A43：默认 image-cache / LRU backend 局部来源认证

2026-10-24；基线 `d493236`，分支 `codex/re-0041-a43`。**已核默认 key、首 word 计量、双链访问次序及 release/失效/驱逐清理，均有本地 LVGL 9.2.1 候选的具体实现对应；这认证局部合同相符，尚不能认证 ROM 精确版本或未改源码。新增 ROM 功能0，确证未改可排除项0。** 本题正常合同未找到必须纠正的硬差异；宽度、配置和未展开分支仍明确保留，不能以“未找到差异”冒称整 backend 相同。

应用 [reverse-engineer-anything skill](C:/Users/cogic/.agents/skills/reverse-engineer-anything/SKILL.md) 的留存优先及事实/推断/未知规则。未打开或切换共享 REA target/database，不新增虚构 Evidence ID。只读既有 ROM 合同与明确候选源文件；无 ROM 整函数重读、SIM、构建、目标执行、设备、网络、历史回放或下级 agent。不改主树、ROM、生产代码、配置、模型或候选。

## 继承结论：已有出处→实际认证缺口

|已有出处|已有行为与证据层次|实际局限/本轮处理|
|---|---|---|
|[A23](png-session-lifecycle-a23-0041-20261023.md)/[A24](png-session-review-a24-0041-20261023.md)|原字节已闭 G+11c image-cache 创建、callback 表、PNG key/payload、pixel/source 所有权|直接继承，不重做 PNG/session；本题只找候选字段、安装与 cleanup 对应|
|[A27](image-cache-cleanup-a27-0041-20261023.md)/[A28](image-cache-review-a28-0041-20261024.md)|默认 backend `a0263afc`、entry 内部偏移、ref/byte+c门、移出→cleanup→free|原字节合同已有独立复核；不重导后端或把 release 当立即 free|
|[A30](image-cache-accounting-a30-0041-20261024.md)/[A32](image-cache-accounting-review-a32-0041-20261024.md)|+3c计量首word、成功加减/重读、PNG data_size逻辑字节单位|D13已部分对应size slot；本题只将其接到其他 backend 来源合同|
|[A34](image-cache-order-a34-0041-20261024.md)/[A36](image-cache-order-review-a36-0041-20261024.md)|+30偏移4、头/尾、树与链两级关系及backlink、命中提升、尾向零ref victim|已有原字节和厂商字复核，不重新恢复链 helper；补候选 backend 具体对应|
|[A38](image-cache-key-a38-0041-20261024.md)/[A40](image-cache-key-review-a40-0041-20261024.md)|默认比较器安装、source word+4/class U8+8、class0地址/class1内容、两查询参数方向|直接继承，不重新核字符串 helper；候选 enum 声明不能反向决定 ROM 读取宽度|
|[F07](display-source-auth-f07-0041-20261023.md)/[F08](display-source-review-f08-0041-20261023.md)，[D13](pixel-source-auth-d13-0041-20261024.md)/[D14](pixel-source-review-d14-0041-20261024.md)|候选自报9.2.1及身份局限；显示/list差异，draw-buffer/size-slot局部来源|不覆盖本题 backend 全部；身份直接继承，不重做整库/版本认证|

证据四类沿用既有报告：可靠原字节合同直接引用；旧 whole-ROM/source-candidate/反编译元数据只定位、不能作来源证明；旧 SIM/照片/替代服务不证明 ROM ABI；本轮只增加明确源行与局部合同比较。既有 reuse.json/complete/ZIP 边界直接继承，不再作整套有界查询，更不以 token 未命中宣称此前没有分析。

## 本轮复核或纠正：源行与局部映射

下文 `S` 仅缩写 WSL `Ubuntu-24.04:/home/slepher/nuttx-ap01-sim/apps/graphics/lvgl/lvgl`。候选树无自身 Git、apps commit 不能认证被忽略解包树、local zip不代表上游签名/下载链等身份局限全部继承 F07/F08。仅读取9个明确文件；与同父 `v9.2.1.zip` 的 `lvgl-9.2.1/<相对路径>` 成员在内存比 bytes，9/9相等。交付保留必要行段，不复制源码库、对象文件或整文件副本。

|ROM 已闭合同/地址|候选精确位置（相对S）|来源比对及限制|
|---|---|---|
|A23 `a008e642..e694`，创建器 `a019855e`；node_size=0x18、三callback word|`src/misc/cache/lv_image_cache.c:54..68`；`lv_cache.c:48..65`；`lv_cache_private.h:113..137,146..158`|`lv_image_cache_init` 选 `lv_cache_class_lru_rb_size`，node_size=`sizeof(lv_image_cache_data_t)`，compare、NULL create、free三槽；create填class/node_size/max/used/ops再init，顺序与合同相符。class十函数指针次序对应ROM已核+0c get、+10 add、+14 remove、+20 victim、+24 reserve；未据此认证所有表槽函数体|
|A38 `a0087bc6→a0087b5c`，cache+10/tree+4默认同槽|`lv_image_cache.c:106..131`；`lv_image_decoder.h:34..39`；`lv_cache_lru_rb.c:228..234`|源码 `image_cache_compare_cb→image_cache_common_compare`，同type FILE strcmp归一、VARIABLE地址比较、其他同type返回0、异type排序，和ROM class1/0规则逐项相符；enum起点分别0/1。init将ops.compare传入rb初始化，支持同槽身份。候选compare返回类型为`int8_t`（private.h:47..50）；ROM保留a0结果和signed判断，不以源码推断全部调用ABI|
|A23/A30 payload首word、source+4、class+8、decoded+c、decoder+10、userdata+14|`src/draw/lv_image_decoder_private.h:55..64`；`lv_cache_private.h:170..176`|字段次序是size slot、src、src_type、decoded、decoder、user_data。普通RV32 `size_t`/pointer为4B时首两字段和后续位置相容；enum可能1B或4B而仍经对齐使decoded位于+c，故24B总长不能认证enum宽度。ROM LBU是独立事实，候选enum声明不保证此读取|
|A27 entry+0 cache、+4 word ref、+8 node_size、+c byte invalid；entry→payload用运行期偏移|`lv_cache_entry.c:22..28,54..71,82..119,148..164`|候选pointer/int32/uint32/bool次序相容；`get_data = (uint8_t*)entry-entry->node_size`，`get_entry = data+node_size`；初始化ref0/invalid=false，delete先算data再free，支持同块内置header身份。不能把cache+4=24误当完整entry/header长度|
|A30 `a00f0d1c` init，+3c=`a00ea5be`；计量与预算门 `a00ea78c`|`lv_cache_lru_rb.c:59..68,216..237,304..313,329..341,441..449,458..462`；private.h:30..35|size init装 `size_get_data_size_cb`，返回slot首字段；成功add对原key加、remove对payload减；预算size+reserved+need，TOO_LARGE/NEED_VICTIM/OK对应1/2/0。`uint32_t`返回与ROM word计量相容；reserved_size为size_t，只有RV32限定才同32位，不能拿宿主64位算术替换ROM。PNG字节单位与不计heap元数据仍由A30生产消费链证明|
|A34 `a00ebb90`成功插入与+2c尾backlink；+30/+34/+38链|`lv_cache_lru_rb.c:61..68,150..177,228..234`；`src/misc/lv_rb_private.h:27..39`|struct含cache、rb、ll、计量函数；rb分配大小为entry总长再加pointer。新node数据复制key；ll_ins_head；链首word存TreeNode*，payload尾存链节点*；`get_lru_node=data+rb.size-sizeof(void*)`同ROM公式。RB声明root/compare/size及node parent/left/right/color/data支持已知关系；不展开平衡算法、不认证color enum宽度或整结构ABI|
|A34 `a00eb9c0`头快路径/命中提升；`a00ec1e6` victim；`a00ebe98`移出|`lv_cache_lru_rb.c:267..288,329..341,416..425`|头node→tree→data，以compare(data,key)==0直返；fallback rb_find后通过backlink移到head；victim逆向遍历尾到头，只返零ref；remove先rb_remove，再ll_remove/free链节点，随后减用量。与已复核指针链顺序相符，不把源码表达替换ROM的重读/NULL setter门或厂商indexed-load无写回事实|
|A27 `a019d9f6` release；`a019cfbe`失效；`a019d898`驱逐|`lv_cache.c:104..117,299..329,332..347`|release先release_data，再ref==0且invalid才callback(data,user_data)和delete；失效零ref先remove/callback/delete，有ref先标invalid再remove；victim空返false，非空先remove/callback/delete。容量循环按2重复、1拒绝。ROM已核调用点user_data=0，相符不等于所有API必须为NULL；普通release没有backend remove/计量扣减|
|A23/A27 cleanup `a008abb0`|`lv_image_cache.c:133..145`|候选free_cb忽略userdata，decoded有ALLOCATED才destroy，再FILE source副本free；不free payload。与A23借用class0、owned pixel、class1副本责任及A27 callback后backend释放payload一致；draw_buf内部raw→对象释放沿D13/D14、A25/A26继承，不另认证heap|

cache基础头四个word与三callback槽可直接与ROM+0..+18局部对照；后接`lv_mutex_t lock`及name。`src/osal/lv_os.h:24..40`显示lock类型受LV_USE_OS分支决定。因此本轮不把cache+24的rb位置等同于任何未核候选编译配置的sizeof(cache)，不填补+1c/+20真实类型，不认证同步。LL内部布局/算法沿F07/F08已有局部比对，不以重复源码证明增加本题成果。

源码中的 `drop_cb`/`drop_all_cb` 未与ROM逐项对应；尤其不能将backend `drop_cb`误认作A27的通用失效helper `a019cfbe`，后者对应的是`cache_drop_internal_no_lock`。本题映射保持实际调用层级；未展开分支仍保留未知。

## 真正新增与四类裁定

新增仅为上述source定位、9成员局部载体一致性和合同关联；**新增ROM功能0、旧语义纠正0**。伪代码、状态转换、参数/返回、RV32宽度、重读、所有权和清理顺序全部引用已独立复核报告，不再生成一份简化实现盖过原合同。

|来源分类|本轮裁定|
|---|---|
|确证ROM未改、可以排除继续恢复|空；没有精确构建输入或ROM版本/commit认证|
|候选局部合同相符|上表key规则、首word计量、节点关联/命中提升/零ref victim、release/失效/清理原序|
|来源家族可识别但版本未知|默认image cache与size型LRU/RB backend家族，entry内部header、size slot及cleanup候选命名；不能由多项匹配反推9.2.1原样来源|
|差异/封装/未认证部分保留|本题正常范围未证硬差异；enum/class真实ABI、OS lock/完整布局、诊断和未展开backend分支仍未认证。F07/F08实际显示/list差异照旧保留，不能以本题匹配消除；也不推断由厂商还是另一上游版本造成|

事实是候选限定源行、9成员相等与既有原字节合同；来源家族/候选符号映射是推断。没有使用源码修复ROM行为，没有整LVGL、libc、heap或NuttX来源排除。

## 未闭精确边、验证与后续闭包

仍未知ROM精确版本/commit、编译配置/enum宽度、完整lock与后段布局、动态backend/comparator/计量重配、完整树平衡、所有其他class协议、backend drop/drop_all及诊断分支的逐项来源。已知静态合同不能证明真实图片命中/驱逐、实际ref时序或allocator成功。

[read_candidate.py](../../analysis/image-cache-source-a43-0041-20261024/read_candidate.py) 仅经WSL Python读取明确文件/本地zip，结果见 [candidate-evidence.json](../../analysis/image-cache-source-a43-0041-20261024/candidate-evidence.json)：9/9成员相等、22项源行token检查通过，交付仅有行号短片段；不新建机械hash账。默认sandbox WSL读取报E_ACCESSDENIED后，按已授权明确本地根使用require_escalated只读读取成功，未修环境或候选。未重跑旧核验脚本或读取完整ROM；本轮ROM断言证据全部显式继承既有独立复核。JSON解析、报告本地链接与git diff --check另作交付检查；作者自检不冒称独立技术验收。

唯一建议后续闭包：独立复核本题source映射的层级（通用drop helper与backend drop不同）、enum/OS布局保留强度和局部相符不等于9.2.1未改认证即可；无需再次恢复key、计量、链或cleanup，也不扩大版本搜索。本题来源认证缺口已在局部合同等级闭合，可结束交管理者补位。
