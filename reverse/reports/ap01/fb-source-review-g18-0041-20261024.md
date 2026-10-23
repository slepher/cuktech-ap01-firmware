# G18：framebuffer 来源候选独立复核（0041，2026-10-24）

**限定接受 G17 的 open/close/poll/notify 本地候选映射、`&fds` 与 F 内槽载体差异及 RV32/双槽/无FB_SYNC的条件解释。** 没有需要改写的ROM语义结论；仅收紧槽数措辞：poll之前有8个槽，poll是第9项，偏移`0x20`。新增业务功能0、整库排除0，精确ROM版本/配置仍未认证。

基线 `ed4735b`，独立树 `re0041-g18`、分支 `codex/re-0041-g18`。未参与G17生产。本轮采用 reverse-engineer-anything 技能：复用G13–G16已验原字节行为，只读本地候选必要行独立比较，没有重导/重新读取ROM，没有打开或切换共享REA target。未运行固件、SIM、模型、构建、历史回放、设备或外网；未改共享文档、主树、生产ROM、配置、模型或候选源码；没有下级agent。

## 继承结论：已有出处 → 行为 → 局限 → 复核缺口

|已有出处|可直接继承的行为|局限与本轮处理|
|---|---|---|
|[G13](display-device-poll-g13-0041-20261024.md)、[G14](display-device-poll-review-g14-0041-20261024.md)|fb0注册、ops+20=`a0132116`；F双槽借用P，P+14回指槽；通知`a003e2a0`的word位运算/重读/callback ABI|不重复ROM恢复。来源比较只引用该合同和已留存关键行，未把候选字段补成原件布局|
|[G15](fb-file-lifecycle-g15-0041-20261024.md)、[G16](fb-file-review-g16-0041-20261024.md)|同ops open/close、F的16B零化/初始化/发布、lower有条件调用→摘链→恢复临界区→归还|直接接受原序与错误门。close本体没有poll teardown，不能因此认定外层或lower没有清理|
|[G17](fb-source-auth-g17-0041-20261024.md)及其`source-evidence.json`|8个本地文件已有必要摘录和来源映射；`&fds`与slot差异已明确保留|本轮重新只读指定源码、核身份/未修改状态、独立分析四个入口及配置条件；不运行G17采集器、不重复其ROM锚点|
|A13/A14、G17复用的旧complete/最终ZIP/较晚round3边界|本地参考候选和宿主替代的证据层次已区分|继承有界结果，不重新解包/复制源码，不把SIM成功或外观用来认证ROM ABI|

本轮缺口仅为 G17 的来源映射和限制是否可接受，不是显示/F生命周期功能缺失。旧材料的完整路径和Evidence通过上述报告定位；本轮没有虚构新的REA ID。

## 本轮复核或纠正

本地候选根为 `Ubuntu-24.04:/home/slepher/nuttx-ap01-sim/nuttx`。独立只读HEAD=`6fc5b3e9dc51dcda46d99519f72b7f2ec6db2e64`、exact tag=`nuttx-12.10.0`；8个实际读取文件的`status --short`和`diff HEAD --exit-code`均为空/成功。身份只认证本地候选，没有远端签名或ROM出处推论。已授权require_escalated用于WSL只读，不更改权限或源码。

|复核项|判定|独立依据与边界|
|---|---|---|
|ops槽序和ABI|接受，措辞收紧|`include/nuttx/fs/fs.h:223–242`依序为open/close/read/write/seek/ioctl/mmap/truncate/poll；`fb.c:182–193`实例一致。按4B函数指针，索引0/1/8对应+0/+4/+20。G17“9个前置槽”应理解为前9项共9槽；严格说是8个前置槽再到poll，不改变其+20结论|
|F字段与lower ABI|条件接受|`fb.c:80–95`为flink、int overlay、fds数组及条件sem；`fb.h:720–728`两个信息回调后是open/close(vtable)。在RV32普通对齐、NPOLLWAITERS=2、无SYNC条件下，F为+0/+4/+8/+c共16B，lower+8/+c对应；不认证完整D/plane或其他配置字段|
|open发布与负值清理|接受|`fb.c:432–467`零化申请；空链才尝试lower open，signed负值到err；overlay=-1，next/head/file私有发布，恢复临界区后返回0；错误先恢复再free再返回。与G15/G16正常合同对应，不证明allocator底层相同或运行成功|
|close条件与归还原序|接受|`fb.c:493–503`门是当前head.next为空，不是所关F的next；可选lower close返回负则先恢复后返回；`:510–532`按prev摘链，先恢复、可选sem destroy、再free。无本体poll teardown；完整前置调用时序仍未核|
|poll登记/撤销|接受|`fb.c:1415–1447`先找空槽；满槽-EBUSY；`*pollfds=fds`与`fds->priv=pollfds`；撤销按`*slot=NULL→fds->priv=NULL`。借用关系与G13/G14相容，不释放F/P，不补充未恢复的caller|
|环缓冲空间门|接受|`circbuf.h:54–58`对应base/size/head/tail；`lib_circbuf.c:198/214/229/274`为size、head-tail、size-used、!space。候选`!is_full`与ROM的space非零门对应；不能缩成space正值或硬件ready。只认证局部关系，不排除整个circbuf库|
|pollfd与notify|条件接受|`sys/poll.h:103/123–131`用uint32事件，int fd、events/revents/arg/cb/priv；32位普通ABI解释P的+4/+8/+c/+10/+14。`fs_poll.c:283–302`循count/eventset、并入(requested\|ERR\|HUP)、错误位清OUT、非零revents或ALWAYS且cb存在则cb(P)，与G13合同相容；ALWAYS不能被误写为ready|
|立即通知实参数组载体|接受差异|候选`fb.c:1438`明确`poll_notify(&fds,1,POLLOUT)`，载体是形参fds的局部存储；ROM继承G13的`a0132176`生成F内slot，`217a`写回指，`2192:2685`传s1=slot。单项首元素可同为P，地址载体仍不同；不认证源码逐字相同或所有别名行为等价，差异原因未知|
|NPOLLWAITERS/FB_SYNC|限定接受|`Kconfig:54–57`默认2及`:24–26`默认SYNC=n只支持兼容解释，不证明ROM实际.config。`:92–94/450–452/529–531`说明SYNC会增加wait及初始化/销毁，与本题ROM16B/无这些操作相容的是无SYNC分支；不从默认值宣布配置已恢复|

ROM来源边界和原字节已由G13/G14/G16独立接受，本轮仅复用其证据行，不能冒称新增原字节验证。P仍是node+14设备视图，未把node本体与P混用，也未把宿主64位指针布局套入ROM。

## 真正新增

新增ROM业务功能0、ISA规则0、整库排除0。没有新增来源版本认证；这是对G17局部候选关系的独立接受。措辞调整只涉及前置槽计数，无表值/ABI语义变更。

为补齐环缓冲映射的最小证据，独立读取G17摘录起点之前的 `lib_circbuf.c:190–198` 9行，确认 `circbuf_size()` 的实际 `return circ->size;`，而不是仅凭名称猜测。仅这9行作为源码增补留存；旧256行对照结果引用原摘录，不重新复制完整文件。

## 未闭精确边与实际验证

仍未核：ROM精确NuttX版本/提交、完整配置与优化、`&fds`/F内slot差异来自版本/改动/编译变换中的哪一种、lower实际目标及副作用、正常caller确保P teardown早于F归还的连接、异步硬件通知与实际fd/F/P运行同一性。本次候选匹配不补这些未知，不承诺ready或实际open成功。

后续闭包优先是沿已有正常caller种子核P teardown到F最终归还的顺序；无需再做相同候选比较或无目标版本扫描。没有真实caller连接时继续保留未知，不将候选close本体当作全系统时序证明。

[review.py](../../analysis/fb-source-review-g18-0041-20261024/review.py)实际通过：8个本地文件身份/未修改状态、256条旧必要源行fresh对照、14项结构/顺序/条件检查，以及9行`circbuf_size`最小补证。布局结果是条件性偏移计算，未编译或运行布局探针。结果/源码增补见[review-result.json](../../analysis/fb-source-review-g18-0041-20261024/review-result.json)。报告链接及`git diff --check`通过；仅写本报告与独占analysis，无ROM重导或原程序执行。独立技术复核在上述范围接受G17，不代表整库或完整设备生命周期完成。
