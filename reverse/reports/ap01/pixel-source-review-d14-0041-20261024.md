# D14：D13 Pixel/raw 局部候选匹配的独立复核

2026-10-24；基线 `f2c1458f2fe731a01e849d669f1884918c0d2ef9`；独立树 `re0041-d14`、分支 `codex/re-0041-d14`。**限定接受 D13 的局部来源对应、三表命名强度、独立 default align、28B 字段与 raw→对象归还、首 word 计量及失败门保留。文字收紧一处：raw 分配 helper 检查的是 malloc callback 槽，不是 handlers 指针本身。新增 ROM 功能 0，未改源码/整库排除 0。**

使用 `reverse-engineer-anything` skill 的既有证据复用、事实/推断/未知区分规则。没有打开或切换共享 REA target/database，无新增 REA Evidence ID。仅写本报告及独占 `reverse/analysis/pixel-source-review-d14-0041-20261024/`；未改主树共享、ROM、生产代码、配置、模型或候选。未运行 SIM、构建、回放、目标代码、设备、网络，也未创建下级 agent。

## 继承结论：已有出处、行为及实际缺口

|已有出处|已经解释的行为|证据局限与本次处理|
|---|---|---|
|[D13](pixel-source-auth-d13-0041-20261024.md)及其 `candidate-evidence.json`|十个成员与同父本地 ZIP 相等；具体 draw-buffer/size-slot 对应及差异边界|本轮独立读同十成员的已选源行，人工核其论证；不重做 ZIP 比对或整库来源认证|
|[F07](display-source-auth-f07-0041-20261023.md)、[F08](display-source-review-f08-0041-20261023.md)|本地自报9.2.1候选身份和来源局限；显示/list 的已知差异|直接继承，无自身 Git、父 apps commit 不认证解包树等限制继续有效；不重取版本、display/list 或整树|
|[A25](pixel-memory-contract-a25-0041-20261023.md)、[A26](pixel-memory-review-a26-0041-20261023.md)|ROM 三表写入、raw/align/free ABI、28B Pixel、独立 `62fc964c`、析构原序|已具原字节及独立复核；本轮引用这些合同，不重读 ROM 或整函数，不以候选替换原指令顺序|
|[A30](image-cache-accounting-a30-0041-20261024.md)|`a00ea5be(record)` 取首 word，初始化写 `cache+0x3c`，成功加减与 PNG Pixel+0x0c 的单位连接|仅复核 D13 的候选对应，不重新验收 A30 的 ROM 原编码、排序或预算实现|

实际缺口只是 D13 局部来源论证的独立验收。上述历史业务与 ROM 恢复不是本轮新增。旧 complete、较晚 round3、ZIP 和 SIM 的范围沿用原报告复用结论，未再次扫描。

## 本轮复核或纠正：逐项结论

候选根 `S=/home/slepher/nuttx-ap01-sim/apps/graphics/lvgl/lvgl`，WSL `Ubuntu-24.04`。源行位置以下均相对 S；字段偏移、地址及 `cf=0x10` 明确按十六进制。独立读取器 [review_source.py](../../analysis/pixel-source-review-d14-0041-20261024/review_source.py) 仅逐行读 D13 十成员至最后必要行，不读本地 ZIP、不执行候选，保留源路径、行号及一致结果至 [review-evidence.json](../../analysis/pixel-source-review-d14-0041-20261024/review-evidence.json)。与 D13 留存逐行相同；这是源行复核，不是新的完整成员/包认证。

|项目 / ROM 接入|独立源码核对|接受、纠正与限度|
|---|---|---|
|三表 `62fc9644/965c/9674`，`a008e3ac` 初始化|`src/draw/lv_draw_buf.c:19–21,52–79`；`lv_draw_buf_private.h:27–34`：default/font/image_cache 顺序；六槽为 malloc/free/align/invalidate/flush/stride|接受局部对应。普通 RV32 六指针共24B、各表同默认 callback 与两个 NULL 槽相符。default 的独立对齐及 image 的 PNG 接入有 ROM 合同交叉支持；middle=font 仍仅为候选顺序命名推断，未验字体消费者或整个 global 布局；三表地址不同，默认值相同不合并槽身份|
|raw `a007fe60`、align `a007fe4e`、free `a007ff40`|`lv_draw_buf.c:597–620`、`src/misc/lv_math.h:33`、`src/lv_conf_internal.h:306–312`：忽略 cf，malloc 加 ALIGN-1，非空向上对齐，free 原地址|接受。默认 ALIGN=4 给加3/4B关系；CONFIG/外部宏可覆盖，未认证 ROM 编译输入。源码 round-up 算术仅支持对齐来源解释，不替换 A26 原 ROM 的 RV32 加法/掩码和溢出边界；heap 实现未知|
|`a0081d90(handlers,w,h,cf,stride)` raw 分配及失败清理|`lv_draw_buf.c:283–300,631–635`：`draw_buf_malloc` 直接取 `handlers->buf_malloc_cb`，槽非空调 `(size,cf)`，否则返回 NULL；raw 返回 NULL 则 free 对象并返回 NULL|接受正常合同；**文字收紧** D13“表/返回raw空”：应读作“malloc 槽为空或 callback 返回 raw 为空”。这里没有 `if(handlers==NULL)` 门，不能推出整个借用表指针可为 NULL。此为限定文字，不新增 ROM 语义判断|
|对象分配失败门|`lv_draw_buf.c:286–288`：先 `lv_malloc_zeroed`，再 `LV_ASSERT_MALLOC`，再显式 NULL return|接受 D13 的差异保留。A25 已留 ROM diagnostic/assert 后若返回则继续、`1dfa` 保存当时 a0；不能把候选显式 return 添进 ROM。assert/log 实际是否返回及 ROM 诊断调用后的 a0 语义仍未知；未重新核诊断实现|
|独立 default align：`a0081e90/1e9c` 读 `62fc964c`，不是 caller 表的 `967c`|`lv_draw_buf.c:108–117,308–311`：create_ex 传原 raw 到 `lv_draw_buf_align`；wrapper 明确传 `&default_handlers`；align_ex 槽空返回 NULL；create_ex 继续保存|接受；即使 create_ex 的 malloc/free 来自 caller handlers，align 仍选 default。无 align 返回 NULL 后的失败回滚门，不能据源码为 ROM 补门；动态修改后槽是否仍同值未知|
|28B Pixel 字段与 header|`lv_draw_buf.h:88–94`；`lv_image_dsc.h:25,50,56,77–98`；`lv_draw_buf.c:302–311`：三组32位 bitfield 容器、uint32 size 和三个指针；magic=0x19，flags=0x10\|0x20|接受**普通 RV32 小端布局的条件相容**：header 0x00..0x0b；size +0x0c，data +0x10，raw/unaligned_data +0x14，借 handlers +0x18；cf byte +1，flags half +2，w/h/stride half +4/+6/+8。共12+4+12=28B。未编译或测宿主 sizeof，未认证候选 bitfield ABI/配置；原 ROM 的写入顺序与16位截断仍按 A25/A26|
|PNG size 分支|`src/misc/lv_color.h:130–151,196–201`、`lv_draw_buf.c:647–662`：ARGB8888=0x10，不等于 RGB565A8=0x14，亦不在 indexed 0x07..0x0a；size=stride*h|接受本 PNG 路径相容；A25 的显式 stride=`width<<2` 及 RV32 size 直接继承。单位是逻辑 data bytes，不含加3余量或28B对象；不延伸其他颜色格式、完整 stride 或资源解码|
|`a0081f26` raw→对象归还|`lv_draw_buf.c:361–376,638–642`：ALLOCATED 门，取借用 handlers，将 unaligned_data 交 helper；helper 当前 free 槽非空才调，再 `lv_free(draw_buf)`|接受正常有效对象下的顺序与所有权对应；未释放 data/handlers。free 槽为空仍归还对象。源中 handlers NULL assert 不是 helper 的可空表保护；ROM 的重读、宽度与清理顺序以 A26 为准，未认证所有断言/NULL 分支相同；普通 cache release 不因此等于析构|
|首 word 计量 `a00ea5be` 与默认安装|`src/misc/cache/lv_cache_lru_rb.c:59–68,216–237,304–313,332–342,441–449,458–462`；`lv_cache_private.h:174–176`；`lv_image_decoder_private.h:55–64`|接受来源对应：uint32 callback 读 `slot->size`，image record 首成员是 slot；成功插入用 key 加、移出用 data 减，预算有同值。size_t 在普通 RV32 为4B，不能套64位宿主；单位仍由 A30 ROM 生产/消费链确立。未核整个 cache/global 的大小/偏移、排序、victim 或所有 backend|

表中源码函数名/字段名都是候选来源映射，不是 ROM 符号认证。D13 的版本未知、不可整库排除和不能用候选失败门补 ROM 诊断边界的结论均接受；没有发现需反转的局部来源结论。

正常生命周期沿用 A25/A26：默认三表安装→分配28B对象→caller malloc(size,cf) 得 raw→独立 default align 得 data→对象持有 data/raw 并借表→允许 destroy 时按当时 free 槽归还 raw→归还对象。候选解释了 default align 与 caller malloc/free 的分离；不新增页面/cache何时触发 destroy 的时序证明。计量 record 与 Pixel 是不同对象，record 首 word 映射 Pixel+0x0c 的 size，而非将 Pixel 自身首 word/header 作为计量。

## 真正新增

新增为 D13 十成员限定源行的独立读取与上述技术验收；新增 ROM 功能 **0**，ROM 语义纠正 **0**。一处可空表措辞收紧，防止把 callback 槽 NULL 误解为整个 handlers NULL；不改变 D13 正常路径结论。没有新增伪代码、库排除、ROM byte 导出、哈希或完整源码复制。D13 现达到本任务规定的局部独立验收；“确证 ROM 未改”仍为空。

## 未闭精确边与验证

事实：当前限定源行与 D13 留存一致；显式 NULL return、default wrapper、字段声明、raw free 调用和 size-slot getter 均存在。推断：这些源码家族可对应已恢复 ROM 合同，font 名只由顺序支持。未核：精确 ROM 版本/commit、可信上游下载链、编译宏/bitfield ABI、allocator/assert/log 实现、动态表/align重配、字体消费者、非0x10完整size/stride、实际cache运行与析构触发。F07/F08 的 display/list 差异完整继承，本轮相符不消除其差异，也不证明修改来自何方。

实际验证：授权 `require_escalated` 只读 WSL 完成10成员限定行段读取与逐行一致断言；证据 JSON 可解析；报告相对链接、独占差异及 `git diff --check` 通过。未运行 D13/A25/A26/A30 的历史核验脚本，不重读 ROM；只运行本轮读取器和交付检查。

本题已闭，不因待确认的来源版本扩扫整库。一个有界后续闭包可另按已存在的字体消费者种子核 middle 表角色；本轮没有此消费者证据，故不作事实升级。由管理者先去重再决定是否启动，本 agent 不自行领取后继。
