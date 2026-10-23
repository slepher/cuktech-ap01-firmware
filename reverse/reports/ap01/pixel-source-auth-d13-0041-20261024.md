# D13：Pixel/raw 的本地 draw-buffer 候选来源比对

2026-10-24；基线 `b673714627a40a6c9d92c832232d13180391e076`；分支 `codex/re-0041-d13`。**A25/A26 的三表、独立默认对齐、28B Pixel/raw 与析构，和 A30 的首 word 计量，均有本地 LVGL 9.2.1 候选的具体实现可对应。仅认证表列局部合同相符/相容；不认证 ROM 精确版本或未改源码。** 候选显式分配失败返回不能覆盖 ROM 已留存的 diagnostic 后继续路径。新增 ROM 功能恢复 0，确证未改可排除项目 0。

应用 `reverse-engineer-anything` skill 的复用、静态证据与事实/推断/未知规则；没有打开共享 REA target 或数据库，不新增 REA Evidence ID。只写本报告及独占 analysis，不改主树、生产代码、ROM、配置、模型或共享索引。没有 SIM、构建、回放、目标执行、设备、网络或下级 agent。

## 继承结论：已有行为到实际认证缺口

|已有出处|已解释的行为|局限与本轮缺口|
|---|---|---|
|[A25](pixel-memory-contract-a25-0041-20261023.md)、[A26](pixel-memory-review-a26-0041-20261023.md)|`a008e3ac` 默认三表真实写入，`a007fe60/fe4e/ff40` 的 raw 加3/4B对齐/归还，`a0081d90` 的28B对象与独立 `62fc964c`，`a0081f26` 先 raw 后对象|原字节及 ABI 已独立复核；不重取完整函数。缺的是这些合同的具体候选来源对应|
|[A30](image-cache-accounting-a30-0041-20261024.md)，其引用的 A23–A28|`cache+3c=a00ea5be`，`(record)->uint32_t` 返回首 word；PNG key 首 word 来自 Pixel+c；成功插入加、成功移出减，预算按逻辑 data_size 字节|继承 ROM 合同，A30 新增仍按其待独立复核状态；本轮只比对首 word/单位来源，不独立验收 A30，不展开排序或 victim|
|[F07](display-source-auth-f07-0041-20261023.md)、[F08](display-source-review-f08-0041-20261023.md)|明确候选路径、自报9.2.1、本地13成员相等与来源局限；显示/list差异已认证|身份和显示/list结论全继承，不重认证。其13成员没有本题 draw-buffer 主体，不能把显示来源结论直接推广至本题|
|A25/A26/A30 已列旧 complete、pass3、较晚 round3、最终ZIP与复用对照|SIM/旧业务及原字节层次已区分，A25默认槽/A30计量缺口的历史范围已记录|不再重复整套历史检索、源码复制或机械清单；新增仅是下面的局部源码合同比较|

ROM 身份、映射、原指令和断言直接引用 A25/A26/A30 的独占 evidence。主仓 ROM 为 `D:/Documents/PlatformIO/Projects/cuktech-ap01-firmware/roms/0041/ap01-1.0.2_0041.bin`；本轮未再读 ROM、不新建哈希、不冒称原字节复核。

## 本轮复核或纠正：实际局部比较

候选根 `S=/home/slepher/nuttx-ap01-sim/apps/graphics/lvgl/lvgl`，WSL `Ubuntu-24.04`。下列 `S` 只是路径缩写，证据记录完整绝对路径。候选身份沿用 F07/F08：解包树无自身 Git；父 apps commit 不能认证被忽略的解包树/zip；本地包相等不等于官方签名或可信下载链。没有重新读取版本、Git、display/list、配置运行值。

[read_candidate.py](../../analysis/pixel-source-auth-d13-0041-20261024/read_candidate.py) 只读明确的10个必要文件，按成员名与同父 `v9.2.1.zip` 的 `lvgl-9.2.1/<相对路径>` 比较 bytes，保留限定行段于 [candidate-evidence.json](../../analysis/pixel-source-auth-d13-0041-20261024/candidate-evidence.json)。10/10 相等；不是整树或整包认证。WSL 使用任务已授权的 `require_escalated` 静态读取，没有改权限或候选。

|ROM 合同 / 地址|候选精确位置（相对 S）|比较与分类|
|---|---|---|
|`a008e3ac` 三个24B表：`62fc9644/965c/9674`，每表 +0/+4/+8 为 allocate/free/align，+c/+10=0，+14=stride|`src/draw/lv_draw_buf.c:19..21,52..79`；`lv_draw_buf_private.h:27..34`|候选依次初始化 default/font/image 三表，同一 malloc/free/align、NULL/NULL、width_to_stride；六函数指针普通RV32为24B，布局相符。第一表 default、第三表 image 的候选命名受独立对齐与PNG消费者共同支持；中间 font 只由三表顺序支持，本轮未认证其字体消费者或整个 global 布局|
|`a007fe60` raw(size,cf)，仅使用size，加3后 `a008aea0`；`a007fe4e` NULL保留，否则 `(raw+3)&~3`；`a007ff40` 原raw传 `a008ab8a`|`lv_draw_buf.c:597..620`；`src/misc/lv_math.h:33`；`src/lv_conf_internal.h:306..313`|候选 `buf_malloc`/`buf_align` 均显式忽略cf，size加 `LV_DRAW_BUF_ALIGN-1`，round-up；默认宏4给出与ROM相符的加3/4B对齐，free不调指针。宏可被 CONFIG/外部定义覆盖，本轮没有认证实际编译输入；ROM常量4仍由原件独立成立。底层malloc/free来源仅到已恢复adapter，不认证heap实现|
|`a0081d90(handlers,w,h,cf,stride)`；`1e16` 读传入表+0，以 `(size,cf)` 调；表/返回raw空则清对象返回NULL|`lv_draw_buf.c:283..300,631..635`|候选 `lv_draw_buf_create_ex` 与 `draw_buf_malloc` 的参数和正常raw失败清理合同相符。候选 `286..288` 在 `LV_ASSERT_MALLOC` 后另有 `if(draw_buf==NULL)return NULL`；A25 的ROM对象分配失败路径保留 diagnostic/assert，如返回则继续且 `1dfa`保存当时a0。该失败门不能从候选移植到ROM；assert实际终止语义未知，故不宣称正常成功路径行为不同或已经解释两者失败差异|
|`1e90/1e9c` 读独立 `62fc964c`，不是 caller第三表+8=`967c`；槽空写data=0，没有align返回NULL门|`lv_draw_buf.c:108..117,308..311`|候选 create_ex 也调用 `lv_draw_buf_align(buf,cf)`，该wrapper用 **default_handlers**，不是create_ex传入的handlers；align_ex槽空返回NULL，随后无失败门。独立槽是候选本身已有的设计，不因两个槽默认同值便合并；后续动态改写仍未知|
|28B Pixel：header@0，data_size@c，data@10，raw@14，借handlers@18；header cf byte@1、flags half@2、w/h/stride half@4/6/8|`lv_draw_buf.h:78..94`；`lv_image_dsc.h:25,47..56,77..98`；`lv_draw_buf.c:302..312`|候选 little-endian header三个32位bitfield容器，加uint32 size、三个RV32指针得28B，字段次序兼容；magic=19、ALLOCATED=10、MODIFIABLE=20与ROM word `00300019` 保留cf的写法一致。该计算限定普通RV32小端位域布局，不拿宿主64位sizeof认证ROM ABI；候选不能重排原发布指令或抹去宽高/stride的16位截断|
|PNG cf10、stride=`width<<2`，size=`stride*height`（RV32）；Pixel+c是逻辑字节量|`src/misc/lv_color.h:130..151,196..201`；`lv_draw_buf.c:647..662`|候选ARGB8888=10，RGB565A8=14，indexed范围7..a；cf10跳过附加平面/调色板，得到同样size。仅匹配已经恢复的本PNG分支；未新增认证其他cf或完整stride函数。size不含raw对齐余量或28B对象|
|`a0081f26` owned bit10门，handlers从+18读，重读表+4，以raw+14归还，再 `a008ab8a(pixel)`；空free槽仍归还对象|`lv_draw_buf.c:361..376,638..642`；`lv_draw_buf.h:92..93`|候选destroy/free辅助同样检查ALLOCATED、借handlers、归还unaligned_data，再lv_free对象。没有另free data或handler。相符范围保留原顺序和析构时读取，不扩大成所有NULL/assert诊断分支逐字节相同；也不等于cache普通release一定实际析构|
|A30 `a00ea5be` `(record)->uint32_t` 返回首word；init `a00f0e00` 安装，成功插入用key加、移出用payload减、预算门看同值|`src/misc/cache/lv_cache_lru_rb.c:59..68,216..237,304..313,332..342,441..449,458..462`；`lv_cache_private.h:170..176`；`src/draw/lv_image_decoder_private.h:55..64`|候选size backend安装 `size_get_data_size_cb`，返回 `slot->size`；image数据首字段正是size slot，再src/src_type/decoded/decoder/user_data。size_t在普通RV32为4B，callback返回uint32，与ROM首word相容；64位size_t不能反向套ROM。成功加、成功减和unsigned预算表达均有对应；不据此认证全部cache布局、排序、回收或其他backend|

源码函数名均为候选映射，不是从ROM恢复的符号。`default/font/image` 命名强度、编译输入及allocator边界按上表分别限定；不能只因多行相符就把原报告的函数边界改成源码边界。一般优化/内联能改变边界、访存与写入顺序；源码层顺序不是替换原指令顺序的理由。

## 真正新增：来源解释及恢复程度

新增是这十文件局部载体相等证据与八组具体来源比较，新增ROM功能0。现在可以把 A25 的 Pixel/raw 合同与 `lv_draw_buf_create_ex` / `lv_draw_buf_destroy` 家族对应，将 `raw` 的候选名记为 `unaligned_data`，并解释为何 caller用第三表malloc/free却仍用第一表align。A30首word计量可对应size backend/size slot；单位仍由A30的ROM生产消费链成立，不靠源码注释倒推。

生命周期继续保留：默认表安装 → 单独28B零分配 → raw(size+3) → 独立默认对齐 → 同一对象保存data/raw/借表 → PNG/session/cache持有 → 在允许直接destroy时先按当前free槽归还raw，再归还Pixel。cache计量记录data_size，并不计入这两次heap分配的全部实占。没有新伪代码替代原A25/A30伪代码，也没有新增异常输入或行为修正。

相符项仅达到“本地候选合同相符/可识别但版本未知”；失败门与底层封装保留；“确证ROM未改”为空。F07/F08既有显示/list差异完整继承，它们既不阻止本题局部匹配，也不被本题匹配消除。不作整LVGL、标准库或heap排除，不推定差异来自厂商还是另一上游版本。

## 未闭精确边与必要验证

事实：限定源码/头文件内容、十成员本地相等、候选函数/字段/默认宏和失败return存在。推断：上表来源家族、Pixel的候选别名及第一/第三表用途映射。未知：ROM精确版本/commit、完整编译配置/位域ABI、assert/log在失败分支是否返回、底层heap真实策略、动态handler/align重配、非cf10完整size/stride、cache引用何时触发payload析构与真实运行命中。middle表字体用途本轮只支持候选名，不冒称已核字体调用链。

实际验证：静态读取器完成10/10本地成员比较；JSON解析、报告相对链接、独占差异与 `git diff --check` 交付检查通过。不运行候选源码或旧核验脚本；没有重导整函数、重算hash、复制完整源码、扩全库搜索、构建或SIM。源文件整体bytes只在读取时内存比较，交付仅存必要行段。

一个后续闭包：独立技术复核本报告三表角色命名强度、default align的caller/槽区分、RV32 header/size-slot限定，以及malloc失败显式return与ROM diagnostic边界的保留。应继承A25/A26/A30 ROM合同与F07/F08身份，不再做全库来源认证或整函数导出；精确ROM版本仍可能保持未知。本轮不自行领取后继。
