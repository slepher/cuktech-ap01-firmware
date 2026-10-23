# H01：0041 天气详情页订阅、字段消费与删除清理

2026-10-23；分支 `codex/re-0041-h01`，研究基线 `99c02abcf47f491987b1b1efd214c0ae489329b8`。依共同任务书及 reverse-engineer-anything skill，只读原 ROM 和已留存静态 Evidence。范围是一个天气详情页的正常订阅生命周期，约 9 个核心入口/合同；没有恢复整个构造 UI、网络、所有订阅者或屏保页。祖先和目标目录检查未发现 AGENTS.md。

**结论：**`a00b8bc2` 是 `a00b821e` 构造函数内的调用点；真实注册对是 `(a00b5cd4,page)`。这个短 callback 在 userdata 非零时调用 `a00b5b58`，后者复制并重排天气数据为栈上的显示输入，再同步调用 `a00b564e` 更新当前天气和七行预报。构造尾部还将 `a00b3b26` 安装为事件 `0x29` 的回调。该回调取页面 wrapper/context，按原顺序清 context 的 `+0..+0x6c` 共 28 个 word，注销相同 callback/page 对，释放 wrapper，清页面 `+0x10`。**本闭包没有找到释放 0x74 B context 的调用；因此不能声称整个页面堆对象已经回收，也不作缺陷判定。**

## 原件、来源与证据定位

- 原件只读路径：`D:/Documents/PlatformIO/Projects/cuktech-ap01-firmware/roms/0041/ap01-1.0.2_0041.bin`。沿用已认证身份 `972db4c136c7ed9e24a83c07c1a7fd62040ca018b08ca285216d26b1fee3c6b9`；映射 `offset=VA-0x9ffff000`，不另建哈希/复制清单。
- 历史 REA 原始来源：主仓库 `evidence/rea-0041-20261017/evidence/whole-rom-private-20261023-{094,095,096,098,100,101}.json`。本轮筛选留存在 [retained-functions.json](../../analysis/weather-subscriber-lifecycle-h01-0041-20261023/retained-functions.json)，每项保留原 Evidence ID、分析 profile、局限与地址。构造函数只留所有权前缀和注册尾部；完整 UI 部分不作本次恢复。
- 注册 `ev_37f69171866916d2577d307574b9c125d6b82edabd9664fdb0b248cac14eea5b`；注销 `ev_b01c9bd1363658594f90e3d063fff42fc67f5732cd4d251f613d2808b8fe1ee0`；分发 `ev_3243848b71bac1ef23bcc9a90ca52e79460d54d77b8f2eaad237d6e9d96e79a2`；消费 `ev_b35fd250fe92c17c7cc51c60e047baf7f66743489971ddd848c58484029d0fd3`；重排 `ev_710cdcdc3b7c65ca0e83b59cf3a93487360aca60057d05836a5a292ba6cee08e`；构造 `ev_1918e8f911a15a34dfeb3de693941a3f265dd1f809986850f3786b407ef8563e`。
- 原指令直接读取结果：[instruction-evidence.json](../../analysis/weather-subscriber-lifecycle-h01-0041-20261023/instruction-evidence.json)，包含 10 个有界窗口、647 条逐地址原字节及 62 项位域/字节/JAL 检查。`a00b3b26` 和 `a00b5cd4` 在基线全 ROM inventory 中不是独立函数项；本轮据真实分支、栈帧、返回和回调地址确定这些入口，没有把相邻已有函数当成它们。
- 厂商 indexed load/store 及 unsigned extract 使用既有只读 AP01 profile，并从原 word 独立核 opcode、funct3、高位操作型、寄存器与 shift。[vendor-model-excerpts.json](../../analysis/weather-subscriber-lifecycle-h01-0041-20261023/vendor-model-excerpts.json)给出精确原模型路径、行号和所用短规则。没有改模型或打开共享可写数据库。
- 已有布局及五槽/双参合同沿用 [weather-dataflow](weather-dataflow-0041-20261023.md)、[A15](weather-subscriber-a15-0041-20261023.md)、[A16](weather-subscriber-review-a16-0041-20261023.md)；arc setter 沿用 [A17](weather-current-consumer-a17-0041-20261023.md)。这里只核相关传参，未重新恢复它们全部实现。

## 入口、ABI 与正常调用链

| 地址/范围 | 参数及返回使用 | 本次恢复角色 |
| --- | --- | --- |
| `a00b821e..a00b8bfb`，仅选定片段 | 页面构造；返回 page 或 0；原首调 page 创建器的入参不在本题中补造 | 分配 wrapper 0x14 B/context 0x74 B，连接页面、订阅与删除 hook |
| `a00b3a68..a00b3abd` | `a0=cb,a1=page`；调用者不检查返回 | 五槽首空注册，沿用合同 |
| `a00b3be6` 的 `a00b3c14..24` | 间接 `cb(a0=data,a1=userdata)`；返回未消费 | 同步借用数据，五槽分发合同 |
| `a00b5cd4..a00b5ceb` | `a0=data,a1=page`；a1=0直接返回，非零调用 `a00b5b58`；无业务返回值 | 本订阅者真实短 callback |
| `a00b5b58..a00b5cd3` | `data,page`；同步调用 `a00b564e(ctx,page,stack_view)` 后日志/返回 | 数据复制、日期/预报重排 |
| `a00eeae6..a00eeb39` | `a0=year,a1=month,a2=day`，返回 word，调用方 SH 截成16位 | 必要日期短依赖，计算星期索引 |
| `a00b564e..a00b59c3` | `a0=ctx,a1=page,a2=view`；ctx/page 非零走主要分支；未检查 view；结果不向上返回 | 当前天气及七行控件消费 |
| `a00b3b26..a00b3be5` | `a0=event`；读取 event+8 的 mask后码、event+4 的页面 | 页面删除回调、清指针、注销及 wrapper 释放 |
| `a00b3abe..a00b3b25` | `a0=cb,a1=page`，匹配首组两个word后清零 | 与注册键完全相同，沿用槽合同 |

业务名由原日志 `lv_page_ui_wx1_dtl1_create` / `lv_ui_wx1_dtl1_update_wx_data_cb` / `j_ui_wx1_dtl1_update_wx_data` 支持；不是依据地址猜测。

关键原指令：

```text
a00b8bb4  37650ba0  lui a0,0xa00b6
a00b8bb8  a685      c.mv a1,s1                  ; s1=page
a00b8bbe  130545cd  addi a0,a0,-0x32c          ; callback=a00b5cd4
a00b8bc2            jal a00b3a68
a00b8bde            sw a5,0(s4)                ; a5=0x19,type
a00b8be2            sw s2,4(s4)                ; wrapper->ctx
a00b8be6            sw s4,0x10(s1)             ; page->wrapper
a00b8bca/b8bee      lui a1,0xa00b4; addi a1,a1,-0x4da ; delete hook=a00b3b26
a00b8bea            addi a2,zero,0x29
a00b8bf2/b8bf4      c.mv a0,s1; jal a01ad654  ; (page,delete_hook,0x29,0)
a00b5cd4            c.beqz a1,a00b5cea
a00b5cde            jal a00b5b58               ; a0/a1原样传递
a00b5c82            jal a00b564e               ; a0=ctx,a1=page,a2=栈view
```

注册发生在 `wrapper->ctx`、`page->wrapper` 写入**之前**；保持这个原顺序，不能在伪代码中重排成先全挂接再注册。原注册器不提供给此调用者可检查的插槽成功结果，故静态结论是“尝试注册”，不保证实际占用槽位。

## 数据布局、宽度与复制边界

`a00b5b58` 先从 `load32(load32(page+0x10)+4)` 取 ctx，然后调用 `a000589c(dst,data,0x24)`。此 copy-like 函数沿用既有逐字节复制合同，不将其来源直接认证为标准库。它随后**重新读取原 data** 的日期、最大/最小温及 icon，而不是从刚复制的局部数据读取；六个未来日块则先各复制 0x14 B 到临时数组，再从这些副本重排。不合并这些读取，也不声称并发一致快照。

显示输入 view 是 caller 栈上 `s0-0xc4`，下列最大访问到 `+0x92`（16位）；这不是一个持久堆天气对象：

| view 偏移 | 字段/实际来源与宽度 | 主要消费 |
| --- | --- | --- |
| `+0..+0x23` | 从 data 当前块复制36 B；布局沿用 weather-dataflow | 温度/体感/日出日落/UV/AQI/湿度/当前 icon |
| `+0x24..+0x2b` | 当前 `year/month/day/weekday`，各16位；日期原件 LHU；helper返回 SH | 第一行日期已由构造固定表现，循环i=0不读日期/星期文本 |
| `+0x2c+8*j`，j=0..5 | future[j] 的 year/month/day及计算的weekday，各16位 | 循环i=j+1读取 `+0x28+8*i` 为 day，`+0x2a+8*i` 为 weekday |
| `+0x5c` | `load32(data+0x1c)`，当前 icon完整word副本 | i=0预报行图标 |
| `+0x60+4*j` | future副本 `+0xc` 的32位 icon | i=j+1预报行图标 |
| `+0x78` / `+0x86` | 当前data `+0xa` / `+8` 的16位副本，分别最低/最高温 | 预报行用 LH/TH.LRH 按 signed16读 |
| `+0x7a+2*j` / `+0x88+2*j` | future副本 `+8` / `+6` 的16位最低/最高温 | 同上 |

`a00b5c72` 原 word `0x432ad78b` 是 `th.srw a5,s5,s2,1`。此时 `s5=0x60-view`、`s2=view+2*j`，地址严格为 `view+0x60+4*j`；不是反编译文本看起来的“双倍栈指针”错误地址。消费侧 `a00b5930` 以 `ctx+0x54 + i*4` 取第i个行对象；`a00b596e/597e` 的 shift=3 读日期/星期；`a00b5998` shift=2读图标；`a00b59ac/59be` shift=1、有符号halfword读最低/最高温。

星期 helper 的 unsigned32 算式（伪代码，非原源码）：

```c
uint32_t weekday(uint32_t y, uint32_t m, uint32_t d) {
    y -= (m < 3);
    uint32_t m1 = m + (m <= 2 ? 12 : 0);
    return (((31*m1 - 62)/12) + y + d + y/4 + y/400 - y/100) % 7;
}
```

原件用 `DIVU/REMU`，没有自行增加日期校验或解释边界输入。它的输出被用作 `a0255904` 表的索引，业务“星期”属公式、表用法和日志共同支持的推断。

## 可读伪代码与主要消费

下面是 RV32 地址/定宽访问视图；是依据指令重建的可读伪代码，不是原源码，也不意味着所有 toolkit 调用已复原。

```c
struct Wrapper { uint32_t type, ctx; uint8_t unexamined[12]; }; // alloc 0x14
struct Context {
    uint32_t controls[21];  // +0..+0x50
    uint32_t rows[7];      // +0x54..+0x6c
    uint8_t date_pending;  // +0x70，构造设为(date.year==0x7b2)
    uint8_t unexamined[3]; // alloc 0x74
};

// a00b821e，省略与本题无关的控件逐一构造，保留生命周期顺序
page = create_page(original_arguments);
if (!page) return 0;
wrapper = alloc(0x14);
if (!wrapper) { delete_page(page); return 0; }
ctx = alloc(0x74);
if (!ctx) { log(); delete_page(page); free(wrapper); return 0; }
construct_current_controls_and_7_rows(page,ctx);
// 尾部ctx+0x4c先存入一个新建控件
register_weather(a00b5cd4,page); // 不消费返回；此前页面尚未挂wrapper
ctx->date_pending = (construction_date.year == 0x7b2);
wrapper->type = 0x19;
wrapper->ctx = ctx;
store32(page+0x10,wrapper);
add_event_callback(page,a00b3b26,0x29,0);
return page;

// a00b5cd4
void weather_cb(Data *data, Address page) {
    if (page == 0) return;
    normalize_and_update(data,page); // a00b5b58
}

// a00b5b58：n为栈上view，future为6个临时20字节块
ctx = load32(load32(page+0x10)+4);
copy(n,data,36);
m=u16(data+2); d=u16(data+4); y=u16(data+0);
store16(n+0x26,m); store16(n+0x28,d); store16(n+0x24,y);
store16(n+0x2a,weekday(y,m,d));
store16(n+0x86,load16(data+8));
store16(n+0x78,load16(data+10));
store32(n+0x5c,load32(data+28));
for (j=0;j<6;j++) copy(future[j],data+36+20*j,20);
for (j=0;j<6;j++) {
    // 每日原16位year/month/day副本先写入日期组，再计算星期
    y=u16(future[j]); m=u16(future[j]+2); d=u16(future[j]+4);
    store16(n+0x2c+8*j,y); store16(n+0x2e+8*j,m); store16(n+0x30+8*j,d);
    store16(n+0x32+8*j,weekday(y,m,d));
    store16(n+0x88+2*j,u16(future[j]+6));
    store16(n+0x7a+2*j,u16(future[j]+8));
    store32(n+0x60+4*j,load32(future[j]+12));
}
a00b564e(ctx,page,n);
log_update(); // 然后返回，栈view和future副本结束生命
```

`a00b564e` 主要分支按原调用顺序：

1. `ctx+8` 文本用 `LH(view+12)` 当前温度；重新对齐 `ctx+0xc/+0x10`。`ctx+0x14` 文本读 LH 最大/最小温 `+8/+10`，`ctx+0x18` 文本读 LH 体感 `+6`。`ctx+0x1c/+0x20` 文本分别以 LHU 读取日出/日落的两个halfword。
2. **当前主图标只取 LHU(view+0x1c)**，传 `a0190da4(load32(ctx+0x28),icon16)`；Ghidra文本漏了第二参数，`a00b5736..5740` 明确 `a1=icon16`。同值保存栈后重读，再传 `a00a6d34(load32(ctx+0x2c),icon16)` 更新相邻描述，随后 `a0090af8`、`a002dcae` 与对齐调用；这里不把描述helper和计数查询完全解码为已认证的可视效果。
3. AQI 用 LHU `view+0x18` 传 arc setter和数值文本；小于100用字体地址 `a0254a18`、相对y=12，否则 `a05647b4`、y=17。UV用 LHU `view+0x16` 传 `ctx+0x38` arc及 `ctx+0x3c` 文本。
4. 湿度读 **LHU** `view+0x1a`（`a00b57cc`），传 `ctx+0x40` arc。若等于100，文本/后缀字体分别 `a02549d0/a056476c`，数字相对offset(-5,1)，后缀offset(1,0)。否则先 `(value-10)&0xffff` 与89作 unsigned 比较：10..99数字offset(-4,-1)，其余(-5,-1)；共同字体 `a05647b4/a0564790`，后缀offset(1,3)。**原反编译 `short sVar3` 不应覆盖该 LHU 事实**；传给数值文本的实际寄存器是零扩展的word。
5. 七行循环：i=0取 row[0] 子对象1/2/3；`a00a6afa(iconObject,load32(view+0x5c),1)`，并用 signed16最低/最高温更新两个文本。i=1..6取 row[i] 子对象0/1/2/3/4；写日期日号、按weekday取表字符串，再 `a00a6afa(iconObject,load32(view+0x5c+4*i),0)`，写signed16最低/最高温。每次 `load32(ctx+0x54+4*i)` 和子对象查询保持原顺序；不把所有对象缓存成单次读取。

所有 `a0091ee4`、`a00dbb68`、`a019d0ae`、`a008ce16` 调用的返回均未用作后续业务成功判断。图标/arc是本题的终端消费合同；不声称已观察到屏幕刷新。`view` 和 `data` 指针没有在本路径写到 context/订阅槽，仅把定宽数值或控件地址传下去；callee是否另行内部复制字符串/资源并非本题恢复范围。

## 删除事件、所有权与未闭合边

`a00b3b26` 首先 `event_code=load32(event+8)&0xffff7fff`，仅在等于 `0x29` 时进入；低码与页面事件安装一致，名称 DELETE 沿用既有LVGL事件合同。页面来自 `load32(event+4)`，wrapper来自 `load32(page+0x10)`。wrapper为0直接返回；非零才 `ctx=load32(wrapper+4)`，没有另加ctx检查。原件按偏移序列：

```text
18 30 40 38 04 0c 34 10 44 48 1c 20 3c 08 24 00 2c 28 14
4c 50 54 58 5c 60 64 68 6c
```

全部是 `SW zero,offset(ctx)`；精确覆盖 `+0..+0x6c` 28个word，**不清 `ctx+0x70` 的byte及尾部3 B**。然后：

```c
// a00b3bc6..a00b3bd4，顺序不能更换
unregister_weather(a00b5cd4,page); // a00b3abe，只移首个完全匹配槽
free(wrapper);                  // a008ab8a(a0=s2)，不是ctx
store32(page+0x10,0);
```

因此页面 userdata 持有页面地址而非ctx；context经页面wrapper间接访问。分发传入的数据只借用到同步调用结束；重排显示对象只在callback栈上。注册表不拥有page/context；删除hook负责解除这一个登记键与wrapper挂接。原指令先清控件地址再注销，不把其解释成先删除这些控件；控件析构/递归删除属于 toolkit 后续路径，不能由清零动作代替。

明确检索界限：依据注册调用点定位其包含构造函数、构造尾部回调常量、所装删除hook完整 `a00b3b26..a00b3be5`、callback完整 `a00b5cd4..a00b5ceb`、重排和主要消费两个完整函数，核对这几个路径的全部直接调用。删除hook仅调用注销、free(wrapper)；未出现 `free(ctx)`，也未观察到把ctx移交另一个释放者。没有扩扫全 UI 删除系统、所有 wrapper 或其他订阅者，因此“谁最终释放0x74 B ctx”“页面控件何时逐个析构”“删除事件由哪一个上层导航动作触发”仍是可定位断边，不以未搜索范围作不存在结论。

## 实际静态验证与恢复程度

执行 `python reverse/analysis/weather-subscriber-lifecycle-h01-0041-20261023/verify.py`：**pass，10个窗口、647条原指令、62项检查、6份保留dossier**。检查覆盖注册和注销callback常量一致、9条关键JAL目标、当前字段LH/LHU差异、wrapper挂接/脱挂、28条清零SW完整覆盖、T-Head预报数组寻址/位宽/shift以及humidity分支的16位截取。原ROM未改，没有编译项目、执行固件/设备/模拟器、外连服务或历史回放；没有缺陷/异常输入验证。REA只读查询会话显示未打开目标，本轮没有切换全局target或新建可写数据库。

事实：入口常量、字节、字段宽度、复制次数、日期算式、消费参数、清理顺序与free实际参数。推断：业务字段名称来自既有生产布局；星期来自算式和索引用途；DELETE名称来自已用事件合同。未知：实际槽占用/页面显示、通用callee内部资源生命周期、context最终释放者和上层离页触发者。

本题已闭合“该订阅者注册→正常callback→当前与七行预报主要消费→相同键注销/wrapper清理”；完整堆context释放保留上述断边。结果是待独立技术复核的恢复，不自称验收通过。建议后继只追 `a00b3b26` 周围页面 `type=0x19` 的context最终所有权/上层离页事件交付，保持当前订阅数据流合同，不扩回所有天气页面。
