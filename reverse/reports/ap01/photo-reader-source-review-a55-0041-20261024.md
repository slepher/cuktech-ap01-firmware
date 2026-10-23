# A55：reader 前缀/open/close 局部来源的独立复核

2026-10-24；基线 `46fa469`，独立分支 `codex/re-0041-a55`。**限定接受A54的局部候选对应与来源强度，语义纠正0、新增功能0、整库排除0。** H/D/C、GIF前缀、普通open/close及条件缓存归还和清槽相符；实际D、ROM精确版本/配置仍未知。5个明确成员中只有4个整文件与本地ZIP相等；`gifdec.c`整文件不同，只接受三个已选片段文本相同，不升级为GIF全文件同源。

采用 [reverse-engineer-anything skill](C:/Users/cogic/.agents/skills/reverse-engineer-anything/SKILL.md)。本轮独立于A54生产；未运行/导入A54采集器。只读明确WSL候选、现存本地ZIP及旧证据，未读/重导ROM、打开共享REA target/database、运行候选/固件/SIM/模型/构建/回放、连接设备/外网或创建下级agent。未改候选、主树共享文件、生产代码/配置/ROM/模型；仅本路报告/analysis写入。A50/A52内部消费合同直接继承，不再次验收或做read来源扩题。

## 继承结论：已有→行为→局限→实际复核缺口

|已有出处|既有行为与证据等级|本轮处理|
|---|---|---|
|[A54](photo-reader-source-a54-0041-20261024.md)及其candidate-evidence/review-result|5文件限定源行、4整文件与ZIP相等、GIF三个片段相等；局部来源分类已有|本轮从实际候选/ZIP独立重读，核载体一致性、配置边界和映射层级；不重扫差异或版本|
|[A47](photo-reader-mode-a47-0041-20261024.md)、[A49](photo-reader-mode-review-a49-0041-20261024.md)|ROM mode byte、普通open `(D,path,2)`、close `(D,H)`、回调后重读配置/C、条件归还及前三word清零已独立接受|可靠ROM合同直接继承；候选原型不能取代ROM实际寄存器/宽度，未新增ROMbody|
|A37/A39、A41/A42、A33/A35|当时W状态复制到O，外层另free(O)，默认五ROM照片mode0借用|直接继承，不因文件型候选推定实际五照片mode1，不再展开constructor或最终DELETE|
|[A50](photo-reader-consumer-a50-0041-20261024.md)、[A52](photo-reader-consumer-review-a52-0041-20261024.md)|实际read/seek内部接口、C/B持有/填充、count/status与厂商字已接受|内部消费及其未知边完整继承；本题只核前缀/open/close来源，不读lv_fs_read实现|
|A47/A49/A54已复用的旧complete、page-logic、weather complete、round3与最终ZIP/SIM|真实caller种子与替代业务已有|不重复旧body/源码导出，不将SIM或地址清单升级为ROM来源认证；已有完整复用边界沿用|
|F07/F08等本地候选来源结论|候选自报9.2.1、ignored树/本地ZIP身份局限、其他模块真实差异已有|不重复完整库/版本认证；本地成员一致不证明上游获取链、ROM精确构建输入或未改|

实际缺口仅A54来源对应的独立技术接受。四层证据保持分开：已复核ROM合同继承；旧反编译/extent只定位；SIM/照片/安全替代不证明ROM接口；本轮实际读取的候选源行只支持局部对应，不直接证明ROM源码身份。

## 本轮复核或纠正：逐项接受范围

`S`为WSL `Ubuntu-24.04:/home/slepher/nuttx-ap01-sim/apps/graphics/lvgl/lvgl`。文件与行号均相对S；普通RV32布局以4B数据/函数指针及4B uint32对齐为条件推导，未编译或认证ROM全部编译配置。

|A54主张|独立源行/条件核验|判定|
|---|---|---|
|H/D/C与GIF reader前缀|`lv_fs.h:88..92`依次file_d/driver/cache；`gifdec.h:28..33`依次fd/data/uint8 is_file/uint32 f_rw_p|接受条件布局：file 12B，GIF data+c、is_file byte+10、位置+14。ROM byte宽度仍以A47/A49为据；不认证整个gd_GIF尺寸或标准FILE*|
|mode1 wrapper到普通open|`gifdec.c:52..60,773..788`清局部、true进f_gif_open、清位置/data、写flag、以LV_FS_MODE_RD调用lv_fs_open；`lv_fs.h:55` RD=2|接受局部结构相符；is_file=1和driver mode=2是不同参数层。bool adapter成功与ROM初始化返回0门相容，不把源码每个helper强绑成独立ROM实体或给a019d6a4入口发明第三参|
|driver前缀与回调实参|`lv_fs.h:69..75` char letter、uint32 cache_size、ready/open/close；`lv_fs.c:93,106,113,118` ready(D)、保存D、open(D,real_path,mode)、保存H|接受RV32条件槽+4/+8/+c/+10；ROM实际callback(D,H)继续沿A47/A49，不拿候选函数签名认证所有ROM ABI|
|路径后缀和默认盘符条件|`lv_fs.c:509..535`非零默认盘符分支要求A..Z加冒号；`#else` lean分支取path[0]、非空时跳首字符、可选跳冒号|接受ROM source+1/可选+2与lean分支相容。两个宏分支不可混用；不认证ROM实际宏值或某一source类型1实例|
|16B缓存和sentinel归还|`lv_fs_private.h:27..32`三个uint32加buffer；`lv_fs.h:25` UINT32_MAX sentinel；`lv_fs.c:122,168..174`申请C及归还条件|接受条件布局start/end/position/B在+0/+4/+8/+c、size16；普通非零配置条件free(B)/free(C)，sentinel跳B的free。特殊mapped-buffer完整初始化/消费不扩题|
|close入口空门、回调和清槽顺序|`lv_fs.c:154..184` D/close_cb空时在callback前返回；166行为close_cb(D,H)，随后配置/C门、B→C free、177..179清前三字段|接受局部顺序与条件；候选成员表达不覆盖ROM callback后重读，空门也不补成无条件清槽。候选183行return res只属于候选；不补认证ROM完整返回状态|
|外层GIF flag与O独立归还|`gifdec.c:816..821`仅is_file时lv_fs_close(&fd)|接受前缀/flag分层。外层free(O)及owner槽仍由A41/A42证明，候选片段不提供页面最终DELETE时序|
|注册槽与D借用角色|`lv_fs.c:391..417` drv_init清caller结构、register分配链节点保存drv指针、get_drv按letter返回同指针|仅接受候选角色与家族解释；没有ROM注册函数/具体D实例绑定，不认证其所有权全生命周期或具体文件系统|

无语义纠正。上述源行支持A54“局部相符”的强度；H具体类型、实际callback地址和执行成功均不由候选证明。close资源合同仍是：O持H/D/C，具体driver回调接收D/H，通用层按原条件归还B/C并清前缀，外层另free(O)；未把D或H描述为通用层直接free实参。

## 真正新增与来源四类裁定

新增功能、ISA规则、ROM原字节导出、来源版本认证及整库排除均为0；仅增加独立接受及载体核验记录。5个实际文件的A54所留238行与当前文件一致，另55项声明/条件锚点通过。复核没有重新输出238行或复制源码文件。

|来源分类|本轮判定|
|---|---|
|确证ROM未改、可排除恢复|空；精确构建输入未绑定，排除0|
|候选局部合同相符|前缀、mode分层、普通open/close ABI、条件缓存归还/清槽、lean后缀规则，限定接受|
|来源家族可识别但版本/实例未知|lv_fs driver reader与GIF file adapter；不以注册候选绑定ROM具体D|
|差异/未认证保留|三个fs文件及gifdec.h整bytes与本地ZIP相同；gifdec.c整文件不同，只有三个所选连续片段文本在ZIP中原样存在。未扫描差异位置/原因，不能外推GIF全文件或整个包相同；F07/F08其他模块差异继续有效|

后三个GIF片段为52..60、773..788、816..821。本轮仅重复固定成员整体相等布尔比较及这三段已定位文本检查，没有展开ZIP差异、版本历史或read算法。

## 未闭精确边、后继与验证

实际source类型1→D/letter注册项→D+c/+10回调目标仍无ROM实例种子；H真实资源、全部driver寿命、实际mode1照片、ROM精确版本/宏配置/返回ABI、全部失败与特殊sentinel路径、最终DELETE及真实执行继续未知。A50/A52消费合同已继承，不再列为尚未恢复，也不替其另作源码认证。

单一后继闭包：只有取得真实source类型1/注册项原始种子时，再绑定同D的open/close目标；目前可停止来源题，不重复版本搜索、gifdec.c差异扫描或全文件系统路线。

[review.py](../../analysis/photo-reader-source-review-a55-0041-20261024/review.py)未调用A54脚本，实际经授权只读WSL五个明确本地文件和同父v9.2.1.zip，结果 [review-result.json](../../analysis/photo-reader-source-review-a55-0041-20261024/review-result.json)：PASS，238行旧摘录回源、55源条件锚点、4整文件相等及GIF三片段相等。初次验证器对`\\0`的嵌套转义断言已修正，候选未改。未读取ROM、未编译布局、无目标执行或模型运行。JSON解析、报告链接和git diff --check另作交付检查。此独立验收只接受A54明确局部范围，不宣称整个reader/lv_fs/GIF库已完成。
