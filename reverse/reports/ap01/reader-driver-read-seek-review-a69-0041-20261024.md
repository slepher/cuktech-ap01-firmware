# A69：实际read/seek callback的非作者限定复核

**限定接受A68在J08/8的callback合同，语义纠正0、新增业务0。** read以H−1、原buffer/count word调用0xa003f6a2；只在返回a0按signed32非负时word写out_count，再返回callback0，底层0也走同门。负分支callback自身不写/清out_count，日志后重新getter/读错误word再交映射。

seek先按**unsigned origin>2直接返回数值11**；允许臂显式转交fd=H−1、原position word、原origin word，`0xa00ef64e`的真实JAL目标为 **0xa00281d8**。仅以返回a0的signed值判门，非负折0，负分支同样日志后二次getter/映射。不能据标准原型补position高word、off_t位宽或返回pair。

2026-10-24；非作者 `/root/f12`，任务A69挂原认领 **J08/8**；固定基线 `bd457a6`，独占 `re0041-a69` / `codex/re-0041-a69`。A68作者 `/root/g23` 已交付停止，主仓[唯一管理记录](rolling-management-0041-20261023.md)已登记本轮。沿最新 [reverse-design](reverse-design.md)、[材料规则](../../analysis/README.md)及REA技能，只核实际两入口与所派字段。

只写本报告、[独立源码](../../analysis/reader-driver-read-seek-review-a69-0041-20261024/review.py)、[必要合同](../../analysis/reader-driver-read-seek-review-a69-0041-20261024/contract.json)，[生成证据JSON](../../analysis/reader-driver-read-seek-review-a69-0041-20261024/evidence.json)忽略留本地原路径。不跑A68或历史技术脚本，不读邻近write callback/IO/mapper/getter/logger body，不执行目标/指令/模型、固件、SIM/QEMU、构建、回放、文件/设备IO或外部服务；不切换共享REA，不改生产/ROM/配置/模型/主树/共享表，无下级agent、提交或推送。

## 继承结论

|来源|已有行为/实际局限|本轮处理|
|---|---|---|
|[A64](reader-driver-slot-bind-a64-0041-20261024.md)/[A65限定接受](reader-driver-slot-review-a65-0041-20261024.md)|正常条件下D+0x14→0xa00ef55e、D+0x1c→0xa00ef632实际写端已独立接受|引用最新限定意见，不重验slots/基址、选择或D生命周期；A68派发时待复核属历史|
|[A50](photo-reader-consumer-a50-0041-20261024.md)/A52、A47/A49|generic read五参/seek四参和缓存/got/owner已验|不重做cache；上层预清got不能移作callback失败时清out动作|
|[A66](reader-driver-open-close-a66-0041-20261024.md)/[A67限定接受](reader-driver-open-close-review-a67-0041-20261024.md)|正常open的H=low32(fd+1)、close H−1已有body合同，实际fd身份/资源效果仍有前提|本轮独立核read/seek自己的H−1，不重验open/close或把H当FILE*|
|[A68作者交付](reader-driver-read-seek-a68-0041-20261024.md)|两callback的word参数、out条件、origin门和错误重读|只非作者核同差集；中途速报0xa00221d8已弃用，以ef64e原字为准|
|A70独立数值map任务|0xa00ea524映射正由另一题恢复|本复核只认opaque调用端/返回保存，不读取或提前接受map结果|

原件沿 [CATALOG](../../../roms/CATALOG.md)：主仓 `roms/0041/ap01-1.0.2_0041.bin`，实查6,769,704B，继承SHA256 `972db4c136c7ed9e24a83c07c1a7fd62040ca018b08ca285216d26b1fee3c6b9`，不重算机械摘要；`file_offset=VA−0x9ffff000`，不套0031/unsigned/SIM。

旧index read entry为0xa00ef55e、106B extent `ev_d52a57d277f473200206c4ce0bdfd6e3c0409bba50f9f97ef14732600bafe5ee`。**0xa00ef632没有旧独立function entry，邻近write owner0xa00ef5c8的旧extent止0xa00ef631**；本题依据A65实际callback入口核原字/门/平衡栈与RET，不借write owner参数、底层callee或边界来替seek。0xa00281d8的旧88B extent `ev_e4e78eb4b960e25ba685f036fa7a7a8c2229928f73834c72008e6130df1781fb`只定位，未读其body/补原型。新字段没有新REA ID或旧profile重标。

## 本轮复核或纠正

独立检查器只读 `[0xa00ef55e,0xa00ef5c8)`、`[0xa00ef632,0xa00ef69c)` 共 **212B**，不触碰中间write区间；保留 **116B必要锚点**。**48项PASS**：普通指令使用 **Capstone 5.0.7 / RV32+RVC**，十JAL、三signed/unsigned B-format、word输出C.SW与局部out指针S-format另独立位域解算。无UNKNOWN/厂商模型或目标执行，未运行/导入A68验证器。

|复核点/地址|独立结果与接受边界|
|---|---|
|read H与buf/count：ef562/56a/56c/56e/570|原a1=H保存后低word减1；a1=原a2 buffer、a0=fd、a2=原a3 count。只有word寄存器搬运，未新增count的窄化/符号扩展；不能据此补底层size_t/ssize_t定义|
|out身份：ef572/57a|原a4输出地址SW到s0−0x14，底层返回后LW回a4；不是把count输出当第三个IO参数，也不是从H解引用|
|read目标：**ef576**|JAL原字段独立解为 **0xa003f6a2**。本层不分配/释放buffer，只转交地址；下层读写/异步持有不在本复核|
|read门/输出：ef57e/5c2/5c4/5c6|signed BGE a0,zero→ef5c2，C.SW `(base,src,off)=(a4,a0,0)`，再a0=0跳公共尾声。**零与正数同门**，故底层0时写out_count=0且callback0；未认证底层0必是EOF或其他含义|
|read负路径：ef582/586、5aa/5ae/5b2/5b4|第一次getter/LW供日志；日志后再次getter/LW交0xa00ea524，尾声保留转换a0。本体此负路径无out_count store/预清；不排除opaque IO/log/map或alias副作用|
|seek origin门：ef632/634/636|a5=2、a0=11；BLTU(a5,a3)目标ef69a，即unsigned origin>2直接RET，发生在frame建立/H解码/IO之前。保持数值11，不改成mapper结果或正式enum|
|seek word转交：ef63e/646/648/64a/64c|原a1=H保存并low32减1；a1=原position word、a2=原origin word、a0=fd。a3是原origin寄存器残值，不是本callback另构造的独立高word|
|seek真实目标：**ef64e** 原字 **ef80b3b8**|独立JAL→**0xa00281d8**。不采用旧速报221d8，也不因88B metadata补off_t/参数总数/高wordABI|
|seek结果门：ef652/654/656|先保存底层a0到a5，再callback a0=0；signed BGE a5,zero→ef690。只检查返回a0这一个word，非负位置结果也折0，不原样返回position|
|seek负路径：ef65a/65e、682/686/68a/68c|第一次getter/LW日志，之后第二次getter/LW交同mapper；公共尾声不覆写a0。两次错误槽地址/值未认证稳定，不缓存第一次|

真实边界由给定callback入口和门/返回支撑：read成功臂位于公共RET之后的尾段，再跳回共同epilogue；seek无frame的origin早返回ef69a与正常frame尾声ef698均核原字。未修改分析器函数定义或把旧未定义区域伪报为provider已有完整function。

本轮未发现A68语义错误。保持原程序有意义的分离：**read callback状态0与实际got是两条输出；read失败本体不写got；seek显式word传递与下层精确off_t是两个不同问题。** 不为“合理”补64位position、EOF错误、失败清零或高返回word判断。

局部表达（非原源码，正常有效参数/opaque服务正常返回前提）：

```c
r = opaque_a003f6a2(low32(H-1), buffer_word, count_word);
if (signed32(r) >= 0) {
    word(out_count) = r;       // 包括r==0
    return 0;
}
log_boundary(word(error_slot_getter()));
return opaque_a00ea524(word(error_slot_getter())); // 日志后重新取槽/读

if (unsigned32(origin) > 2) return 11;
r = opaque_a00281d8(low32(H-1), position_word, origin_word);
if (signed32(r) >= 0) return 0;
log_boundary(word(error_slot_getter()));
return opaque_a00ea524(word(error_slot_getter()));
```

上式下层参数仅列callback显式设置的寄存器word，不认证C原型、完整参数数目或返回位宽。H解释为前次open编码还须同次fd来源/未关闭复用等前提；buffer/out/generic缓存彼此所有权不合并。callback直接借用跨下层调用，但无法据此说整个IO栈绝不保存指针或已经写入有效数据。

## 真正新增

**非作者复核新增业务0、语义纠正0、ISA/来源认证0、整库排除0。** A68两个给定入口的有限body合同获得限定接受；不重读底层IO、map、邻近write或已验generic/cache/slot写。

A64/A65绑定及A66/A67 H编码直接引用最新限定意见，A68派发时pending属于历史，不将callback复核等同实际路径实例、默认照片mode1或资源成功。ROM POSIX路径/候选LVGL来源继续只说明family，不认证精确版本/ABI。

## 未闭精确边

仍未知下层read/seek实际IO、count/position完整值域与off_t/ssize_t/返回pair约定、buffer/out的有效容量/分离/持有/寿命、实际fd身份/复用、错误槽稳定性与转换的最终数值协议、真实FS/设备/资源效果。callback只判a0，不代表下层没有其他返回约定。默认五ROM照片mode0不改变。

一个有种子的后继是 **0xa00ef64e→0xa00281d8** 的显式 `(a0=fd,a1=position_word,a2=origin_word)` 到该88B服务真实参数/返回ABI；由管理窗口先查重登记，不借它扩write/dir/FS。当前只保存此边；J08/9 A70的map研究另行维护，本复核不重派或提前接受。

实际检查为48项原字段/目标/门/输出检查、JSON解析、引用在本树或整合主树可定位、空白/独占文件与`git diff --check`。报告/源码/合同未提交，生成JSON忽略留本地原路径，复核者交付后停止。
