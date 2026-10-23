# A25：0041 Pixel 默认 raw handler、独立 data 对齐与双层归还

2026-10-23；研究基线 `47a43110646f987b23255338ad8ab36a1826d846`；分支 `codex/re-0041-a25`。**默认安装已由实际写指令闭合**：`a008e3ac` 将 `a007fe60` / `a007ff40` 写入 `62fc9674/+4`，分别承担 raw 申请/归还；将 `a007fe4e` 写入独立 `62fc964c`，承担 data 对齐。正常 PNG 的真实构造调用传 `62fc9674`，但构造器对齐仍读 `62fc964c`。默认配置也把同一对齐函数写入 `967c`，不能因此把构造器读取地址改称 handler+8。

遵循共同规则、完整 A25 任务书与 `reverse-engineer-anything` 技能。只写本报告及独占 analysis；未修改共享索引、主树/其他工作树、ROM、生产/构建代码或分析器模型，未打开/切换共享可写 REA。未运行固件、模拟器、解压/绘制、历史回放、设备/网络/异常输入；没有创建下级 agent。结论是静态默认初始化合同，非运行值观测或整 LVGL/PNG 认证。

## 成果复用及本轮增量

根据用户新增复用优先要求，先对主仓旧成果作了只读定点交叉检索，结果/确切路径/行号见 [reuse-crosscheck.json](../../analysis/pixel-memory-contract-a25-0041-20261023/reuse-crosscheck.json)，可由 [reuse.py](../../analysis/pixel-memory-contract-a25-0041-20261023/reuse.py)复现。查询包含八个函数/槽地址以及 `lv_draw_buf`、`draw_buf_handlers`；未提取 ZIP 到工作区、未运行其中脚本。

| 已有出处 | 行为及可复用范围 | 局限与剩余增量 |
| --- | --- | --- |
| [A23](png-session-lifecycle-a23-0041-20261023.md)、[A24](png-session-review-a24-0041-20261023.md) | 原件核过 PNG 真实构造、raw/data 两字段、strict open 门、cache 持有、直接析构顺序；A24 纠正独立 `964c` | 继承 session/cache 合同，不重解。二者明确未解安装者及 callback 实体，本轮正补此缺口 |
| 主仓 `application-function-matrix-0041.json`、`factory-reference-map-0041-20261020.md`、`system-complete-0041.json`、`charge-complete-0041.json` | UI 家族/SIM 完成范围、原件引用与局限账本 | 上述定点词未命中本闭包；只表示这批文本的有界检索未命中，不能说过去从未分析 |
| 主仓 `page-logic-0041.json`、`details-0041-round4.json`、`charge-0041-round4.json` | 页面业务旧成果 | 相同定点检索未命中，不把 SIM 页面结果当 raw allocator 证据 |
| 主仓 `reverse/analysis/0041-20261013/0041-ghidra-pass3.txt:1931,2048` | 已有 `lvgl_ui_main` 调 `a008e3ac` 的旧直接边/伪代码 | 旧反编译不是槽写核验；本轮仅重核 `a005cd36` 的6 B调用窗口 |
| 主仓 `reverse/rehost/ap01-ui-0041-complete-source.zip`，39 成员、35 文本成员 | 只读搜 ZIP 成员，`tools/ap01/rehost-assets.py:123,448` 有 `lv_draw_buf_t` 字体 bitmap callback 参数 | 是 SIM 字体接口，未命中本槽/allocator绑定；不是原 ROM 内存适配恢复，不能据此排除本增量 |

继承结论：A24 两槽区分、Pixel 布局和 session/cache 分流。本轮针对核：PNG 显式调用、构造/析构内间接来源和原宽度。本轮新增：默认写入者/三个表的实际槽地址、三个回调实现、raw 大小加3与对齐关系、Pixel 对象本身的零分配包装。没有重新恢复 cache/8428 B 解压算法、全部页面或通用 heap。

## 原件与证据

只读原件 `D:/Documents/PlatformIO/Projects/cuktech-ap01-firmware/roms/0041/ap01-1.0.2_0041.bin`，映射 `offset=VA-a0000000+1000`；身份沿用已有 dossier 的 SHA-256 `972db4c136c7ed9e24a83c07c1a7fd62040ca018b08ca285216d26b1fee3c6b9`，不新建哈希清单。

[verify.py](../../analysis/pixel-memory-contract-a25-0041-20261023/verify.py)用 Capstone 5.0.7 解原件普通 RV32/RVC，另从原编码提取 U/I/S/JAL/AUIPC/JALR 字段及绝对写地址。[evidence.json](../../analysis/pixel-memory-contract-a25-0041-20261023/evidence.json)保留地址、文件偏移、原字节、96项断言；[instructions.txt](../../analysis/pixel-memory-contract-a25-0041-20261023/instructions.txt)逐指令可读；[validation.json](../../analysis/pixel-memory-contract-a25-0041-20261023/validation.json)记录实际统计。没有产生新的 REA Evidence ID，也不把已有 retained 分析冒称新会话。

核心约11项：init限定片段、raw allocate/align/free 三函数、Pixel construct、cf10 size限定片段、Pixel destroy、对象零分配 wrapper、raw allocation两级短 adapter、free adapter、真实 PNG 构造输出片段；必要依赖仅 zero adapter 和 app init 调用点。非cf10 size/stride选择、完整 init、底层 heap 是明示界限。所选正常路径全为普通指令，没有未解厂商 word；未将未纳入窗口的其他格式厂商指令解释成通用公式。

## 默认配置的真实写入

`a005cd36` 原字节 `ef106367` 调 `a008e3ac`。initializer `e3c4..e3d4` 建 `G=62fc957c`、调用 `a0080d8e(G,0x210)` 清零，再保持 `s1=G`。该清零覆盖全部三表；不能把文件任意偏移当 RAM 槽的静态装载内容。随后：

```text
a008e43c 93890408  ADDI s3,s1,0x80     ; s3=62fc95fc
a008e440 130a0af4  ADDI s4,s4,-0xc0    ; 前LUI a0080 -> a007ff40
a008e444 938b0be6  ADDI s7,s7,-0x1a0   ; 前LUI a0080 -> a007fe60
a008e448 130bebe4  ADDI s6,s6,-0x1b2   ; 前LUI a0080 -> a007fe4e
a008e44c 938a0a03  ADDI s5,s5,0x30     ; 前LUI a0080 -> a0080030
```

`e42c`、`e472`、`e498` 分别在安装对应表前清24 B；后续实际写入如下。表名为分析用途，非确认原厂类型名。

| 表基址 | +0 raw申请 | +4 raw归还 | +8 对齐槽 | +0c/+10 | +14 stride槽 |
| --- | --- | --- | --- | --- | --- |
| `62fc9644` | `e45e`→`a007fe60` | `e454`→`a007ff40` | **`e462`→`a007fe4e` @964c** | 0，`e466/e46a` | `e46e`→`a0080030` |
| `62fc965c` | `e484`→同上 | `e47a`→同上 | `e488`→同上 @9664 | 0，`e48c/e490` | `e494`→同上 |
| **`62fc9674` PNG使用** | `e4a0`→同上 | `e49c`→同上 | `e4b0`→同上 @967c | 0，`e4a4/e4a8` | `e4b4`→同上 |

例如 `e4a0 23ac7907` 为 `SW s7,0x78(s3)`，`62fc95fc+78=62fc9674`；`e49c 23ae4907` 为 `SW s4,0x7c(s3)`，落 `9678`。`e462 23a86905` 为 `SW s6,0x50(s3)`，落 `964c`；第三表 `+8` 则由 `e4b0 23a06411 SW s6,0x100(s1)` 落 `967c`。各次写的时序见完整窗口，不能按表格列顺序理解实际执行顺序。

这是默认初始化非NULL绑定的正面证据。没有声称穷尽后续所有动态写者或保证运行时从未替换。三表 +c/+10 的零值及 stride 槽保留；本 PNG 显式 stride 非零，未调用 stride 槽，不扩其 bit-depth 表恢复。

## 申请、对齐、包装、发布与归还

以下为分析伪代码，不是原源码。RV32 指针/word 为4 B，所有加法/乘法按32位结果；正常有效指针/配置及成功申请前提单列，原诊断路径不擅自增加安全返回。

```c
struct Pixel {                       // independent 28 B allocation
    uint8_t byte0, cf; uint16_t flags;
    uint16_t width, height, stride, pad;
    uint32_t data_size;              // +0c
    void *data;                      // +10, aligned usable pointer
    void *raw;                       // +14, allocator return, must retain
    Handler *handlers;               // +18, borrowed table pointer
};
// Default raw callbacks:
void *raw_alloc(uint32_t size, /* a1=cf */ ...) {  // a007fe60
    return a008aea0(size + 3);        // a007fe68 ADDI; fe6a JAL
}
void *align_data(void *raw, /* a1=cf */ ...) {     // a007fe4e
    if (raw == 0) return raw;
    return (void *)(((uint32_t)raw + 3) & 0xfffffffc);
}
void raw_return(void *raw) {          // a007ff40
    a008ab8a(raw);                   // ff48 JAL; no pointer adjustment
}
```

`fe60`只改a0后调用adapter，`fe4e`只看/改a0，均没有读cf/a1；因此不把caller提供的a1提升成callee必需参数。申请的3 B余量对应最多3 B向上对齐位移，raw原指针始终保留。不能由4 B对齐推断 raw 已对齐、data==raw、DMA/cache一致性或更高对齐。

`a008aea0` 对非零大小调用 `a008ae8c`，后者 `ae94` 调底层 `a002fcc8`；大小零返回 `62fc95e0` sentinel。`a008ab8a` 对 NULL 或同一 sentinel 早退，其他指针 `aba2` 调 `a002e14e`。只恢复这层接口，未给底层 heap 强行认证源码名/精确实现。

Pixel结构的分配是另一条真实边：`1daa`设28，`1db4`调 **`a008e362`**。该wrapper保存长度，调用 `a002fcc8`，成功后 `a0080d8e(pointer,length)` 清零，再返回原分配指针。它不是 raw 的 `a008aea0` 路径。wrapper失败返回NULL，构造器走原log/assert，诊断若返回则继续并在 `1dfa` 保存当时a0；报告不将这段改成无条件提前return。

```c
// a0081d90(handlers,width,height,cf,stride) -> Pixel*/NULL
p = zero_alloc_wrapper(28);          // NULL时原diagnostic/assert，不补return
if (stride == 0) stride = a0081b54(width, cf); // 自动stride接口；非本PNG分支
size = a0081c6a(width,height,cf,stride);
alloc = load32(handlers+0);
if (!alloc) { original_log(); free_adapter(p); return NULL; }
raw = alloc(size, cf);               // a0=size，a1=cf；不臆补a2/a3 ABI
if (!raw) { original_log(); free_adapter(p); return NULL; }
store8(p+1, cf);
store32(p+0, (load32(p+0) & 0xff00) | 0x00300019);
store16(p+4,width); store16(p+6,height); store16(p+8,stride);
fn = load32(0x62fc964c);             // 独立全局；不是本handlers+8
aligned = NULL;
if (fn) aligned = fn(raw,cf);        // raw仍在a0；cf重装到a1
store32(p+0x10,aligned);
store32(p+0x14,raw);
store32(p+0x0c,size);
store32(p+0x18,handlers);
return p;
```

`1e16 83a70a00 LW a5,0(s5)` 取raw allocator，`1e6c ca85;1e6e 8297` 设a1/间接调，`1e70`保存raw。handler+0为空与返回raw为空汇到同一日志/结构free路径，未获得raw故没有额外raw callback。成功后的SH截断宽高/stride，size使用此前完整寄存器算式，不能先把它们转换成uint16再乘。cf先SB，之后word mask/OR保留该byte并令flags含0x30。

`1e90 b797fc62;1e9c 03a7c764` 独立给出 `62fc9000+64c`；槽空时 `1ea0`预置0，`1ea2`跳过间接调用，仍写data=0并保存raw/handler，不增加构造失败判断。align返回值也不补NULL门。成功时先data、再raw、再size、最后handlers发布，顺序如伪代码。默认函数可空指针返回，但本成功raw分支已由原分支筛过raw非空。

真实PNG输出片段 `a0192ac6..a0192af6`：a1来自width、a2来自height，`2ad4` a4=width<<2，`2ad8` a3=0x10，`2ada` a0=62fc9674，`2ade/2ae2` AUIPC/JALR到构造器。cf10且显式stride非零，size函数 `1c76` 跳过自动stride，`1c8a` MUL取低32位 `(width<<2)*height`；cf10不等cf14且不在cf7..0a，故走原公共返回而不额外加平面/调色板大小。完整其他格式只继承接口，不恢复/泛化。非NULL构造返回后 `2aee`直接写调用者out指针，再 `2af0`读取对象+c。完整PNG失败/临时对象/通道交换及session发布沿用A23/A24合同，不由这一片段声称全解压恢复。

```c
// a0081f26，正常非NULL Pixel及有效handler前提
if (!(load16(pixel+2) & 0x10)) { original_log(); return; }
handlers = load32(pixel+0x18);        // NULL走原diagnostic/assert，无新增safe return
release = load32(handlers+4);        // 析构时重读表内容，未复制callback到对象
if (release) release(load32(pixel+0x14));
a008ab8a(pixel);                     // 无论release槽空与否，随后归还28 B对象
```

`1fba dc43;1fbc 99c3;1fbe 4849;1fc0 8297` 原序为读取+4、空槽跳过、取raw、间接调用；`1fc2 2685;1fc4 ef80703c` 才把Pixel本体传free adapter。对齐后的data从未作为这次release实参。默认release进入 `ff40→ab8a→a002e14e(raw)`，再外层 `ab8a→a002e14e(pixel)`，形成独立raw/对象双层归还。handler表是借用全局对象，未free；data指向raw内部，不另free。不owned分支只日志/回栈，不能写成总会释放。

所有权状态为：`默认表清零与绑定 → 单独28 B零分配 → raw(size+3)申请 → 独立964c对齐 → Pixel持raw/data/借handler → out发布 → session/cache持有合同 → 允许直接销毁时先raw再Pixel`。cache release是否触发本析构仍是A24明示断边，本轮未把release写成实际free。

## 事实、推断、未知与验证

事实：三表初始化及非NULL绑定、独立964c读取、默认raw加3/4 B对齐、结构零分配不同wrapper、真实PNG构造/输出、析构两层顺序和空槽门均有原件证据。推断：在该默认初始化完成且相关槽未被改写、正常申请成功的路径，data为raw向上4 B对齐地址，Pixel析构按所借表当前+4归还原raw。静态分析没有观测这条路径实际执行。

精确未闭边：后续是否/何时替换这些表或独立964c未穷尽；cf10之外size/bit-depth/stride完整选择不在本闭包；`a002fcc8/a002e14e`底层heap策略与实际复用未知；cache驱逐/引用释放何时调用payload cleanup未知；完整PNG算法/库版本未认证。未因名称/算法相似排除任何原实现，没有本地LVGL候选源码认证结论。

实际验证：[validation.json](../../analysis/pixel-memory-contract-a25-0041-20261023/validation.json)为15个限定窗口、1108 B、386条指令、96项编码/地址/ABI断言全部通过，未知指令0；复用检索覆盖8个指定旧文件及ZIP的35文本成员。仅运行host端静态字节/文本核验脚本，没有编译项目或执行目标。提交前另检查链接、差异和工作树状态。

建议唯一后继：由新agent独立复核本默认安装→raw申请加3→独立对齐→对象raw/data发布→析构raw/Pixel归还的小闭包，重点核G/s3绝对地址和对象零分配wrapper；不得将同值967c替代实际964c读取，也不扩全heap/cache。本轮不自行领取后继。
