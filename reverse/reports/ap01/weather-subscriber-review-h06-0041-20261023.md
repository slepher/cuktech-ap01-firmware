# H06：H05 weather1 type4 订阅、图标消费及 ctx 归还独立复核

2026-10-23；基线 `04cb395c5c38875ba72cefd84ca55bfadc3e4538`；分支 `codex/re-0041-h06`。本轮为新 agent 对 [H05](weather-subscriber-h05-0041-20261023.md) 的独立静态技术复核，使用 reverse-engineer-anything 技能及共同规则。**六个新恢复入口、三个既有合同边界均限定接受；无语义纠正项。** 接受范围仅为构造必要片段→主要 callback/直接图标 setter→已安装 DELETE 中的注销与 ctx/wrapper 归还。正常上层离页动作→该 page DELETE 的派送仍未连接。

## 原件、方法与范围

原件只读绝对路径：`D:/Documents/PlatformIO/Projects/cuktech-ap01-firmware/roms/0041/ap01-1.0.2_0041.bin`。沿用共同原件身份，不新增哈希清单；映射 `file_offset = VA - 0x9ffff000`。本树及输出目录所有祖先未发现适用 `AGENTS.md`。

已读完整 H06 任务书、H05 报告和其验证器以明确被审主张；**没有运行、导入或复制 H05 验证器**。新写 [review.py](../../analysis/weather-subscriber-review-h06-0041-20261023/review.py) 独立读取原 ROM，Capstone RV32/RV32C 对选定十窗检查连续指令边界；另以位运算核 RV32 load/store/JAL/branch/LUI/ADDI、RVC load/move/immediate/jump/branch，保存 [review-evidence.json](../../analysis/weather-subscriber-review-h06-0041-20261023/review-evidence.json) 的 210 项原编码检查与 [anchors.txt](../../analysis/weather-subscriber-review-h06-0041-20261023/anchors.txt) 的地址、文件偏移、原字节和解码。只留本轮复核锚点，不重存 H05 全量指令清单。

这是本地独立原字节证据，**不是新 REA Evidence ID**。未打开或切换共享 REA target/database；H05 引用的 whole-ROM extent/dossier 只作为包含函数边界的历史定位，不假称本轮重新恢复 `a005cc1e` 全部 body。六个新入口和三个既有边界之外不扩全 UI、全部天气或 PNG 解码。

## 逐项结论

| 对象 | 结论 | 独立证据与限定 |
| --- | --- | --- |
| `a005cc1e` 内构造片段 `cfd8..cff7/e4e6..e523/e8d2..e909` | 接受 | page→20 B wrapper→68 B ctx 的真实实参及失败分支；登记在 type/ctx/page 字段挂接之前；DELETE 安装四参。整体包含函数未恢复 |
| `a00abed2..a00abfe5` | 接受 | `(data,page)`，page=0 单门；完整温度/时间/icon load、控件重读、所有主要 direct call 与 variadic 参数顺序 |
| `a00abb62..a00abbf5` | 接受 | mask `ffff7fff` 与码29门；完整16次SW；ctx作为 free 的 a0 未改；同 callback/page 注销；wrapper free→page+10清零 |
| `a019cbc0..a019cd13` | 接受 | 独立分类分支树、16个源常量和合流跳转；category15重新隐藏；其他默认保留旧source。与 A19 `a0198946` 分开 |
| `a008e362..a008e38b` | 接受 | size保存→下层分配→仅非零零填充→原指针返回。没有把下层分配器认证为标准库 |
| `a0080d8e..a0080da5` | 接受 | `(ptr,size)`变成`(ptr,0,size)`交`a0024906`；只接受明确零填充适配合同，下层实现/来源未认证 |
| `a00b3a68/a00b3abe` | 既有合同定点接受 | 独立核真实callsite和callback/page双word键；五槽首空/首匹配规则沿用H02，未重做完整注册器 |
| `a00b3be6` 中 `a00b3c14..25` | 既有合同定点接受 | LW callback、LW userdata、a0=data、`c.jalr a5`后直接步进；不消费callback返回。完整分发器沿用既验收范围 |
| `a008ab8a` | 既有合同定点接受 | 独立核ctx失败分支wrapper、DELETE ctx及wrapper三个真实free实参；分配器/归还内部沿用既有合同，不扩大覆盖 |

纠正：0。未核：包含函数剩余 UI 构造、描述文本分类树 `a00a6d34` 内部、allocator/文本/image toolkit内部、具体正常导航与外层对象最终归还；它们不纳入本次验收。

## 构造、登记与资源挂接

`a005cfda` 调用 `a00d91c6(s4)`，结果page留在s5；零跳`a005cff8`。非零时`a005cfe2`的原字`5145`是20 B分配实参，分配结果留s8。wrapper非零经`a005cfec`直接跳`a005e4e6`，不是另一个函数入口；零分支调用`a00d7806(page)`并把s5置零。该walker不能自行升格成完整公共删除。

`a005e4e6`原字`13054004`设size=0x44，分配结果ctx留s2。非零跳`a005e524`继续构造。零臂在日志后依次walker(page)、free(wrapper)，`a005e520`跳`a005cff6`置page寄存器零。这里只静态核正常代码含有的失败路径，不执行失败/异常试验。

成功尾部核出的真正顺序是：

```c
register_try(a00abed2, page);       // a005e8dc；不检查结果
SW(wrapper+0, 4);                  // a005e8e2
SW(wrapper+4, ctx);                // a005e8e6
SW(page+0x10, wrapper);            // a005e8ee
install_event(page, a00abb62, 0x29, 0); // a005e8fe/902 -> a01ad654
```

这些是分析伪代码而非原源码。`a005e8d2/d8`独立LUI/ADDI得到callback=`a00abed2`，`a005e8ea/f8`得到DELETE=`a00abb62`，没有拿调用点 `a005e8dc` 当入口。注册不保证占槽，也不补造其成功返回。wrapper20 B中只有+0/+4在此链有语义，剩余12 B未命名。

新读ROM字符串 `a01c42a0=lv_page_ui_weather1_create`、`a037bce8=lv_ui_weather1_update_wx_data_cb`、`a01c3b98=lv_power_ui/lv_ui_theme.c`，支持weather1厂商页面身份；不是凭type数字推断。

## Callback 数据宽度、参数及持有

独立原编码确认`a00abed2`只在a1(page)零时直接返回，无data、wrapper或ctx的额外空门。`a00abef0`从page+10取wrapper，`a00abefa`从wrapper+4取ctx。关键输入如下：

| data偏移 | 指令锚点/宽度 | callback中的用途 |
| --- | --- | --- |
| +0x1c | `a00abef2 0329c501` LW s2 | 完整32位icon传两个消费者 |
| +6 / +8 / +10 / +12 | `abef6/abefc/abf00/abf14` LH | 体感/最高/最低/当前，有符号扩展 |
| +14 / +16 / +18 / +20 | `abf04/08/0c/10` LHU | 日出时/分、日落时/分，无符号扩展 |

全部上述输入读取均早于第一个文本helper；不把它们称并发一致快照。data地址本身不保存，ctx只保存既有控件地址，此callback是同步数值借用，不是天气结构复制。

按真实调用顺序恢复的必要伪代码：

```c
// c=ctx，所有字段值按上表原顺序先载入保存寄存器。
label_fmt(LW(c+0x0c), "%d", now);
align(LW(c+0x0c), LW(c+0), 1, 20, 70);
align(LW(c+0x10), LW(c+0x0c), 3, 12, 0);
align(LW(c+0x14), LW(c+0x0c), 3, 46, 0);
label_fmt(LW(c+0x18), "最高: %d 最低: %d", high, low);
label_fmt(LW(c+0x1c), "体感温度: %d", feels);
a019cbc0(LW(c+0x20), icon);
a00a6d34(LW(c+0x24), icon);  // 仅核本页传参，内部分类未新恢复
label_fmt(LW(c+0x28), "%02d:%02d", rise_h, rise_m);
label_fmt(LW(c+0x2c), "%02d:%02d", set_h, set_m);
log_update();
```

`a0091ee4`为文本格式调用，`a00dbb68`为对齐调用。独立核对了三次重新读取ctx+0xc的对齐参照，不合并成一次读取。`abf5a/5c`保留a3=low/a2=high；日出和日落均a2=hour/a3=minute。当前/high/low/体感使用原signed值，没有A15 arc的回退门。四种格式字符串都从原ROM重新读出，格式的`%d`不把时间load变成signed LH。调用后无返回检查，不推为物理显示成功。

## 图标setter的独立分类核对

`a019cbc0(image,icon_word)`先保存image、把a1完整移入a0调`a00a6998`，category留s1；随后`a00d9044(image,1)`移除隐藏bit0。已验收分类器、flag helper与PNG info只作合同边界，不重做其实现。

本轮独立检查22条RV32分支、17个category比较立即数、16组LUI/ADDI资源地址和通向同一image setter的合流跳转。映射为：

| category | src | category | src |
| --- | --- | --- | --- |
| 1 | a0251fd4 | 2 | a063461c |
| 3 | a0633960 | 4 | a0633f50 |
| 5 | a06318b0 | 6 | a06315bc |
| 7 | a0631f78 | 8 | a0632308 |
| 9 | a0632968 | 10 | a0636644 |
| 11 | a0636130 | 12 | a06334ec |
| 13 | a06330b8 | 14 | a0631c68 |
| 22 | a0634fe4 | 23 | a0635878 |

这些路径合流到`a019cc3e/40`，以`a0=image,a1=src`调`a00ed560`，然后回`a019cc08`归还栈帧。category15经`a019cc8c/8e`选中`a019cc92..96`，调`a00d8f7c(image,1)`重新隐藏而不调image setter。其余category进入`a019cc08`返回：已移除隐藏位，source未写，**保留旧src且没有fallback资源**。这与“未知图标隐藏”不同，不能擅自改原行为。静态ROM src是借用指针，不是本轮分配或复制的PNG数据。

## DELETE 的精确归还与状态

`a00abb62`从event+8读取码。`a00abb64..68`原字`6177 7d17 f98f`构成mask `0xffff7fff`并AND；只在结果等于0x29继续，**不截成16位**。page从event+4读取；wrapper为page+10；仅wrapper=0有返回门。ctx从wrapper+4读入a0，没有独立ctx零门。

下面的原序未重排：

```c
// 分析伪代码，event与字段均为RV32视图。
if ((LW(e+8) & 0xffff7fff) != 0x29) return;
p = LW(e+4); b = LW(p+0x10);
if (!b) return;
c = LW(b+4);
// 十六进制偏移，按原16次SW顺序：
for off in [1c,34,08,10,14,00,0c,30,28,2c,04,24,20,18,38,3c]:
    SW(c+off,0);
a008ab8a(c);                 // a00abbcc
a00b3abe(a00abed2,p);        // a00abbda
a008ab8a(b);                 // a00abbe0
SW(p+0x10,0);               // a00abbe4
```

`a00abb88 03254900`确实把ctx载入a0。其后直到`a00abbcc efe0fdfb`只有16次以a0为基址的零SW，没有改写a0或插入其他调用，所以free(ctx)为直接参数证据，不由“清空”等动作推论。clear集合恰为+0..+0x3c的16word；0x44分配的最后4 B（+0x40）没有预清，但整ctx指针交free。`a00abbd0/d6`常量仍是同一个callback，`abbd4`把page放a1；`abbde 4a85`重新把wrapper放a0再free。

资源/状态关系为：槽借用page，page+10持有wrapper，wrapper+4持有ctx；控件地址由ctx记录。构造成功后存在已挂接状态；DELETE内依次进入“ctx前64B清零→ctx归还→首个同键槽清除→wrapper归还→page+10零”。**free先于注销的原序保留**，不讨论或改造异常重入。注销不承诺清除全部重复键。控件字段清零不是widget删除；显式ctx/wrapper归还也不证明page本体已free。

因此H05与H03详情type19不同：H06只接受本页直接ctx free证据，不把这一生命周期套到H03。外层通用递归/DELETE合同也不能代替本page真实导航连边。

## 实际验证、事实与未闭合边

实际运行命令为 `python reverse/analysis/weather-subscriber-review-h06-0041-20261023/review.py`。结果 **passed：10窗，1058 B，355条连续解码指令，210项原编码检查**。最终重跑结果与生成证据一致；选定窗口无未解码/厂商opcode。原宽度、符号、mask、分支目的、双参数ABI、地址常量与归还顺序均有独立字节核对。未用反编译填未知厂商语义。未执行固件、设备、模拟器、历史回放、构建、外连、异常输入或漏洞验证，未改ROM/生产模型/其他agent文件。

事实：以上原指令、实参、读取宽度和重复读取、默认门、挂接/free和注销键。推断/分析命名：ctx控件职责来自字段到真实helper的用途；weather1名称来自日志；DELETE及工具库名称沿用既验收合同。未知：实际插槽占用、callback是否在某次运行发生、物理绘制、底层分配器内部、完整描述文本分类、page/widget最终归还和具体上层导航。

来源仍分层：厂商UI日志/路径与胶合结构可识别；LVGL候选合同可复用；没有认证本链精确上游版本、未修改实现或整个库来源。**本轮新增确证开源排除0**。

唯一后续闭包建议：沿本type4 page的真实所有者/父对象和正常导航调用，恢复“具体用户动作或父页替换→该对象被删除→向此page送达0x29→`a00abb62`”。目前精确断边在已安装的DELETE handler与其上层正常触发来源之间；本次没有重做全UI负搜索，也不拼接E05条件root删除或其身份未闭合对象。上述局部生命周期已可限定验收，上层断边继续明确保留。
