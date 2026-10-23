# 0041 F09：event array 容量 helper 的增量合同

本题主体已被 G03–G06 覆盖，不能根据 F06 较早的未展开清单重新登记重入/删除恢复。F09 收缩到 `a00ecc68` 的容量调整 ABI 与既有注册调用者连接：正常可归还 array 以 `new_capacity * element_size` 调 `a008c332`，先发布返回 data，再发布 capacity，仅在旧 count 大于新 capacity 时截断 count；返回原先读取的非零标记。注册器只检查非零，然后继续旧追加路径。**新增页面/事件业务恢复为0**；新增的是已有原指令的局部语义合同，仍待独立复核。

基线 `fca1d5e`，独立分支 `codex/re-0041-f09`。只写本报告及独占 analysis，遵循 REA shipped-artifact 技能的证据分层，以只读 ROM/保留证据静态核验，未开共享可写 REA 数据库。没有执行固件、SIM、构建、历史回放或归档脚本，没有修改生产、ROM、配置、分析器模型或共享索引。

## 已有成果→实际缺口

|既有出处及证据类别|已经解释的行为|证据局限、本轮处理|
|---|---|---|
|[F05](miio-exit-callback-f05-0041-20261023.md)、[F06](display-exit-review-f06-0041-20261023.md)，原指令/独立复核|descriptor12B、注册追加、filter、callback ABI、双阶段 sender|F06 第11/24/117行尚列 array 维护未核，但时间较早；不能当当前未知清单|
|[G03](invalidation-submit-g03-0041-20261023.md)、[G04](invalidation-submit-review-g04-0041-20261023.md)，原指令/独立复核|`ac38/acc6` 压紧与快照清理；slot helper `cd68` 是 `a00ecd14` 续接，不是新函数|已覆盖，直接继承；本轮不重复导出|
|[G05](display-event-flow-g05-0041-20261023.md)、[G06](display-event-review-g06-0041-20261023.md)，原指令/独立复核|busy bit0、dirty bit1、禁用 filter bit16、延迟释放、压紧；容量满时传 count+4，返回非零才追加|这些也已覆盖；仅容量 helper 内部的 owned 门、宽度、发布顺序和返回未作语义展开|
|主仓 `reverse/analysis/0041-20261013/refined/0041-candidate-disassembly.txt` 的 `a00ecc68` 候选窗口及续接；同目录原版也有|已保留 helper 原字节/普通指令，不是本轮首次发现此地址或代码|窗口标题本身不证明函数边界，候选被重复上下文切开；本轮局部核正常入口/成功尾及实际 caller，不重新导出完整函数|
|[F07](display-source-auth-f07-0041-20261023.md)、[F08](display-source-review-f08-0041-20261023.md)，来源比较|候选 LVGL9.2.1 与 ROM 的匹配和差异，20B只是 array 前缀，list+14另有状态|全部继承；不套候选16B array，不认证 ROM 版本或整库排除|
|旧最终 SIM 报告、矩阵、factory map、4项 complete、page-logic/round4/knob/settings、pass3及最终 ZIP 成员|SIM 成果仍解释重建行为，父级 passed-in-sim 有效于该范围|本题5个精确地址在20份已检优先文件及所读 ZIP 文本成员无命中；仅有界地址检索，不证明历史从未分析。近期 G03–G06 命中优先于旧未知项|

检索明细见 [evidence.json](../../analysis/event-array-maintenance-f09-0041-20261023/evidence.json)。旧路径未因失效被视为缺失；最终 ZIP 只读文本成员，未解包、复制或执行。SIM 来源与 ROM ABI 不混同。

## 继承的旧结论

`a01b93b4` 保存 callback/filter/userdata、追加 descriptor 指针与 count 更新均继承。注册容量满的 `a01b9510..951a` 及其返回消费已在 G05/G06 留存，不计新增。`a008acfa` 快照原 array 前缀20B，list+14 busy/dirty及 `a008ac38/a008acc6` 删除/重入维护合同继承 G03–G06，不重复研究。array 前缀的可见字段为 data word+0、count word+4、capacity word+8、element_size word+c、owned byte+10；完整 list sizeof 未认证。

## 本轮复核或纠正

纠正范围判断：F06 的“未核 event array 维护”不能覆盖 G03–G06 后续完成内容；F09 不再将其称新增恢复。原字节重读统一标 **旧结论复核**。

独占 [verify.py](../../analysis/event-array-maintenance-f09-0041-20261023/verify.py) 只读主 ROM，以 `offset=VA-0x9ffff000`，独立按低2位核2/4B宽度、Capstone普通RV32/RVC、原 JAL 位域计算目标。4个必要窗口共28条普通指令、20项断言通过：`ecc76..ecc7e`、`ecca0..eccc2`、`ecd02..ecd14` 与旧 caller `9510..951c`。不重复导出注册/分发函数，未执行旧验证脚本。该窗口无 custom0/unaff/extraout，`eccb8` 为标准 `mul`；既有 `th.mula` 注册追加与 slot 运算合同不再重新取证。

具体锚点：`ecc76 83490501` 是 **LBU**，不是 word/bool规范化；`eccb8 b305b902` 是 RV32 MUL；`eccbc eff069e7` 独立还原到 `a008c332`；`ecd0a e37bf9f8` 是 **BGEU**，比较新 capacity 与旧 count；`9514 ef3043f5` 到 `a00ecc68`。`9518 61f9` 对返回仅测非零，非零回 `94e8`，零经 `951a` 到 `9504` 尾出。这里不能命名注册函数统一的 descriptor 返回 ABI。

## 本轮真正新增

新增是 `a00ecc68(array*, uint32 new_capacity)` 的下列局部合同解释，代码/地址已在早期留存，不算重新发现或新业务功能：

1. 入口 LBU `array+10` 保存到 s3。若为0，走已有日志调用 `a008b51a`，随后返回原 s3=0；该支不进行容量发布。若非0，保存 array 到 s1、new_capacity 到 s2，读取 word element_size+0xc 与 word data+0。
2. 以 RV32 低32位乘积作为 `a1`、旧 data 为 `a0` 调 `a008c332`。这里只采用既有 realloc 家族调用边界，不认证分配器/heap/来源；没有研究异常输入。返回非零跳至 `a00ecd02` 正常成功尾。
3. 正常尾先读取旧 word count 到 a5，然后依次 SW 返回 data@0、SW new_capacity@8。若 `new_capacity >= old_count`（unsigned）直接回尾；否则再 SW new_capacity@4，保留 `count <= capacity`。返回 `s3` 的原 LBU 数值，**不是** data、capacity或固定规范化1。调用者只测非零，因此正常 owned=1 路径返回1，但不外推所有可见非零标记必为1。
4. 本注册路径在已知 `count==capacity` 时传 `count+4`，故正常增长后不截断 count，再由既有追加逻辑写 descriptor 指针并 count++。`a008ac38` 压紧后的 shrink 也调用同一 helper（继承 G03/G04/G06），本轮不另取它的字节或记一份新删除恢复。

仅为正常路径的说明性伪代码，不是原源码：

```c
u8 owned = load_u8(array + 0x10);
if (!owned) { existing_log_call(); return owned; }
u32 bytes = new_capacity * load_u32(array + 0x0c); // low32
void *p = opaque_realloc(load_ptr(array), bytes);
if (p != NULL) {
    u32 old_count = load_u32(array + 4);
    store_ptr(array, p);
    store_u32(array + 8, new_capacity);
    if (new_capacity < old_count) store_u32(array + 4, new_capacity);
    return owned;
}
// Existing diagnostic/assertion branch: not converted to return NULL/false.
```

没有给原程序补 descriptor 回滚/free。没有通过这个 helper 证明 callback 可安全修改列表的全部情形，也不把本地候选替代ROM差异。

## 仍未闭合的精确边

`a00eccc0` 返回0进入日志/断言块；该块覆写 s1，`a00eccfe` 调既有断言处理入口 `a0019672` 后在线性字节上接成功尾。没有核断言处理是否返回，**不能**把它接成正常成功发布或伪造安全失败返回。这是具体的 no-return 不可信边，保留 opaque，不扩断言系统。

`a008c332` 的 heap/realloc、容量零特殊值、底层回收最终语义在本题仍只保留调用合同。完整 list sizeof、所有动态订阅者及 callback 重入组合、ROM精确LVGL版本不因本题闭合。没有证据证明本路径以外所有 list 均为相同 owned 值。

本题完成为“主体已覆盖，最小容量 helper 正常合同补齐，失败断言与底层分配器保留精确边”，不是完整事件库或原 ROM 完成。后继只需独立复核本轮正常 helper ABI/发布顺序；没有必要为本题继续扩扫。
