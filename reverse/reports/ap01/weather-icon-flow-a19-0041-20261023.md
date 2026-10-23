# A19：天气图标 code 到 ROM 资源和控件更新

2026-10-23；研究基线 `2ee39b3`，分支 `codex/re-0041-a19`。本轮恢复一个条件闭包：`now.ico` 的两个整数结果 → 天气对象 `+28/+32` → 本订阅者只取 `+28` → `a00a6998` 分组及全局 byte 选择 → `a0198946` 选择图像描述符或设置隐藏位 → `a00ed560` 在 decoder-info 成功后保留 ROM 描述符、写宽高和格式，并提交尺寸/区域更新调用。图标 code 不是资源地址，也不是直接数组下标。decoder 注册及具体 info callback 身份尚有明确断边，因此没有声称 PNG 必定已解码或图像已显示到物理屏幕。

遵循 [共同规则和 A19 任务书](rolling-management-0041-20261023.md)，采用 `reverse-engineer-anything` skill；不创建下级 agent。只写本报告和独占 analysis 目录，不改 ROM、生产代码、模型、共享索引或其他 worktree。静态读取原件和已保存证据；没有开启或切换共享 REA、执行固件、仿真、历史回放、设备/服务连接或缺陷验证。祖先、worktree 根及目标目录未发现适用 AGENTS.md。

## 范围、证据及恢复粒度

11 个核心函数：构造胶合 `a00a5d5c`、code 分组 `a00a6998`、图标更新 `a0198946`、flag remove/add `a00d9044/a00d8f7c`、source classifier `a00dd454`、info wrapper `a0082e32`、info dispatcher `a0082c8c`、image setter `a00ed560`、尺寸门 `a01b1ee6`、缩放模式更新 `a00ed438`。必要直接依赖 `a00d7446/a00d749e` 仅恢复非空 flag 谓词。保存完整函数原字节，语义恢复限定本天气调用可达的正常分支；不把诊断、文件/符号源、缓存通用算法和所有 GUI helper 自动算作已恢复。

- 原件只读：`D:/Documents/PlatformIO/Projects/cuktech-ap01-firmware/roms/0041/ap01-1.0.2_0041.bin`；身份沿用既有报告的 SHA-256 `972db4c136c7ed9e24a83c07c1a7fd62040ca018b08ca285216d26b1fee3c6b9`。地址映射 `file_offset = VA - 0xa0000000 + 0x1000`，没有新建哈希或复制清单。
- [instruction-evidence.json](../../analysis/weather-icon-flow-a19-0041-20261023/instruction-evidence.json)：原字节、偏移、解码、92 项独立编码核验、16 个资源描述符和 PNG 格式校验、ROM 名称、模型原文及历史 extent/call Evidence IDs。[instructions.txt](../../analysis/weather-icon-flow-a19-0041-20261023/instructions.txt) 供按地址快速审阅。
- [verify.py](../../analysis/weather-icon-flow-a19-0041-20261023/verify.py) 从只读原件重新提取并断言，不执行目标代码；[review-index.json](../../analysis/weather-icon-flow-a19-0041-20261023/review-index.json) 为实际运行摘要。
- 历史函数范围来自 [whole-ROM inventory](../../analysis/whole-rom-coverage-0041-20261023-round1.json)，其中图标函数 extent `ev_48a593bbbf7a8befb44776b4929c56a3870ee936fba074bc519664c0fed95817`、callee 列表 `ev_bd717ed8cf4b6d3a06f9434b4228d1d29d3efd4e59a5a06f11b9170613290e13`；这只是历史静态 provenance，不是本轮新 REA 观测。本轮每条指令均重新读 ROM，不凭历史反编译认证参数。
- [weather-dataflow](weather-dataflow-0041-20261023.md)、[A15](weather-subscriber-a15-0041-20261023.md)、[A16](weather-subscriber-review-a16-0041-20261023.md)、[A17](weather-current-consumer-a17-0041-20261023.md)、[A18](weather-current-review-a18-0041-20261023.md) 提供生产布局、同步发布、注册/context 及 arc 合同。此处只补图标必要原字节，不重做 getter/arc。

以下函数、变量和结构名称是分析视图，不是原始源码或准确 C 声明；直接调用的 a0 留值不自动当稳定返回值。

## 图标生产与控件生产如何汇合

`a00aa58a/58e` 形成字段名地址 `a0269c4c`，ROM 原文为 `ico`；随后取节点并经过既有字符串判定/取值接口。`a00aa5d0` 和 `a00aa5da` **分别**以相同 s3 字符串指针调用 `a0053f46`，返回 a0 分别以 SW 写 `s0-0xc0` 与 `s0-0xbc`。结合既有栈 weather 基址 `s0-0xdc`，它们是 `weather+28/+32`。代码有两次转换，不能合并为“一次计算后复制”；字符串转整数内部沿用 weather-dataflow 的合同，未重新认证库版本/所有输入语义。字段缺失时保留已清零对象的既有合同。

既有发布链先缓存 156 B，再同步把原 data 指针交给 `callback(data,user_arg)`。本次 callback 在 `a00ab6c0/6ca` 取 `wrapper=load32(obj+0x10)`、`ctx=load32(wrapper+4)`，在 `a00ab6d0` 用 LW 把 `weather+28` 保存至 s3。`a00ab710` 的 `8850` 是 `C.LW a0,32(s1)`；`a00ab712` 为 `C.MV a1,s3`，`a00ab714` 的 JAL 到 `a0198946`。第一参数是 **字段内指针**，不是 `ctx+0x20` 地址；第二参数保留完整 32 bit。`+32` 的第二图标槽在此 callback 不读取。

此 widget 也有明确生产边：构造器片段 `a00a7f7e..7f9d` 从 `ctx+0x18` 取得父/参考对象，a0/a1 均设该指针；a2 为 `a0251da8`，a3=19、a4=40，`a00a7f96 -> a00a5d5c`，返回指针在 `a00a7f9a` 以 SW 保存 `ctx+0x20`。`a00a5d5c` 正常直线顺序为：

```c
// a0=parent, a1=reference, a2=initial_src, a3=x_arg, a4=y_arg
widget = a00ed0a8(parent);                  // 图像对象创建边界，内部未展开
saved_widget = widget;                    // 栈 word 保存；没有返回非空检查
a00ed560(widget, initial_src);
a00dbb68(saved_widget, reference, 1, x_arg, y_arg); // 布局边界
return saved_widget;
```

这里初始资源正是后文 category 1 的描述符。对象创建/布局不计作完整内部恢复；没有用“创建一定成功”替代指令中缺失的检查。callback 借用输入 weather，图标后续仅传整数，不保留 weather 指针。

## a00a6998：从原 code 到显示类别

入口 a0 是 32 bit 位模式；范围门均为 unsigned 比较，先计算 RV32 模减差值。全局选择值 `q=load_u8(0x62fc405f)` 只在相应路径读取，不能写成每次函数入口无条件读取；每次调用在被选中的路径上只读一次。没有写全局字段或天气对象，也没有 callee。

| 原 code（十进制） | 返回类别 | 指令锚点 |
| --- | --- | --- |
| 100 | `1+(q!=0)` | `a00a69b8 -> a00a6a06..14` |
| 101..103 | `3+(q!=0)` | `a00a69bc..d4` |
| 104 | 6 | `a00a69aa..b0 -> 69d6` |
| 150 | q==1 时 2，否则 1 | `a00a69de..e2 -> a00a6a16..26` |
| 151..153 | q==1 时 4，否则 3 | `a00a69e6..a04` |
| 300..301 | `8+(q!=0)` | `a00a6a50..54 -> 6a76..84` |
| 302..304 | 11 | `a00a6a58..60` |
| 305..318，399 | 7 | `a00a6a34..3c`，`a00a6a68..74` |
| 350..351 | q==1 时 9，否则 8 | `a00a6a48..4c -> 6a86..98` |
| 400..403、405、407..410、457、499 | 12 | `a00a6aa2..ce` |
| 404、406、456 | 13 | `a00a6aae..b2`，`a00a6ad8..ea`；406 经 `ANDI -3` 成404 |
| 500..515 | 14 | `a00a6aec..f8`；unsigned差值<=15 |
| 其他 32 bit code | 15 | 默认返回；不能假定其等价某个气象枚举 |

其中 `q!=0` 与 `q==1` 是两种真实不同的测试，不应统一成 boolean 日夜选择。`q` 与昼夜/主题模式有关是业务候选，本轮没有恢复其写者，因此只以 q 命名。未把天气服务的公开 code 表或常见晴雨名称强加到资源类别。

分组恢复的可读表示如下；表中的条件均以 unsigned RV32 区间为准，不用宿主有符号比较替代原门：

```c
category = map_code(icon_code);  // 以上表覆盖 a00a6998
// 实际返回汇合 a00a69d6: restore s0; a0=a5; restore sp; jr ra
```

## a0198946：资源选择与隐藏状态

`a0198952` 保存 widget，`a0198954/56` 把 code 放入 a0 调上述 mapper，返回类别保存在 s1。随后 **先** `a00d9044(widget,1)`，再按 s1 分支，全部资源臂汇合到 `a0198a1e/20` 调 `a00ed560(widget,descriptor)`。category 15 去 `a0198a94..98 -> a00d8f7c(widget,1)`，不更换图像源；它不是释放旧源或置源为 NULL。

| 类别 | ROM 描述符地址 | PNG 数据地址 | 长度 / 像素宽高 |
| --- | --- | --- | --- |
| 1 | `a0251da8` | `a0251dc4` | 527 B，19×19 |
| 2 | `a062ff20` | `a062ff3c` | 593 B，20×20 |
| 3 | `a062fb30` | `a062fb4c` | 469 B，20×16 |
| 4 | `a062fd24` | `a062fd40` | 478 B，20×20 |
| 5 | `a062f000` | `a062f01c` | 336 B，21×20 |
| 6 | `a062eee8` | `a062ef04` | 250 B，20×20 |
| 7、17 | `a062f2bc` | `a062f2d8` | 315 B，20×20 |
| 8 | `a062f414` | `a062f430` | 486 B，20×20 |
| 9 | `a062f618` | `a062f634` | 512 B，20×20 |
| 10 | `a0630838` | `a0630854` | 491 B，20×20 |
| 11 | `a0630658` | `a0630674` | 451 B，20×20 |
| 12 | `a062f9a4` | `a062f9c0` | 367 B，20×20 |
| 13 | `a062f834` | `a062f850` | 339 B，20×20 |
| 14 | `a062f16c` | `a062f188` | 305 B，20×20 |
| 22 | `a0630190` | `a06301ac` | 579 B，20×20 |
| 23 | `a06303f0` | `a063040c` | 585 B，20×20 |

资源地址由每一臂的 LUI+ADDI 原编码独立重构。16 个描述符均为 28 B 存储视图 `{word 0x119, word 0, word 0, word payload_size, word payload_ptr, word 0, word 0}`，数据紧接描述符 `+28`。格式证据是 PNG signature、IHDR 宽高、完整块边界、每块 CRC 和 IEND；没有执行解码器或复制像素资产。这里前三 word 中尺寸为零，不能直接把描述符 `+4/+8` 当 PNG 宽高；真实宽高需 info 解码路径取得。原始资源符号名及晴雨图像身份未知。

类别5/10/17/22/23 是 setter 中存在的臂，但本 mapper 返回集合为 `{1,2,3,4,6,7,8,9,11,12,13,14,15}`，因此不能把这些额外臂声称为本天气数据链可达。其他类别直接恢复返回，已有 remove-flag 操作仍已发生；此事实来自 selector 的完整控制流，不是执行测试。

```c
icon_update(widget, code) {
    c = a00a6998(code);
    remove_flag(widget, 1);
    if (c == 15) { add_flag(widget,1); return; }
    if (c has descriptor above) image_set_src(widget, descriptor[c]);
    // 此函数不汇总稳定返回结果；caller 下一条覆盖 a0。
}
```

`a00ab718` 开始构造日志参数并覆盖 a0；callback 不保存或判断 icon setter 结果。selector 自己也不检查 remove-flag/set-src/add-flag 返回；不能写成返回成功布尔值。

## flag 状态与更新副作用

ROM 字符串分别为 `lv_obj_remove_flag`（`a0569ac8`）和 `lv_obj_add_flag`（`a0569848`）。`a00d7446` 正常非空谓词返回 `((load32(obj+0x24)&mask)==mask)`，`a00d749e` 返回 `((load32(obj+0x24)&mask)!=0)`。图标链 mask 恒1，两者均成为 bit0 测试，但保留不同函数合同。

remove 的 `a00d9098` 先调用 any predicate；没有该位就直接返回。正常有位时，先调 `a00d8f02(obj)` 保存结果，mask1不走 mask0x10 的区域局部处理，再在 `a00d90ce..da` 重读 flags、写 `flags & ~mask`。随后顺序调用 `a00dddf4(obj)`、`a00d8f42(load32(obj+4))`、`a00d8f42(obj)`；最后重调 `a00d8f02(obj)`，若结果不同再调 `a00d8f42(parent)`。这些是尺寸/区域请求边界，不能由名字推出实际硬件刷新。

add 的 `a00d8fd2` 先调用 all predicate；原位已存在则返回。否则保存 `a00d8f02(obj)` 结果，mask1先调 `a00dddf4(obj)`，在 `a00d8fee..ff4` 重读 flags 并写 `flags | mask`；随后若 `a00d7446(obj,2)` 非零，按 `a00d759e(obj)` 取到对象是否非空，再调 `a00d85ea`、`a00d73c6` 并可能调 `a00dddf4`。最终重调 `a00d8f02` 比较，变化时对 parent 和 obj 各调 `a00d8f42`。未展开这些 GUI helper 的全图语义。

因此 code 类别15下若 widget 原来可见，会先把隐藏 bit 清除（若原已隐藏），再把它置回；原顺序不能简化成只写一次最终 flag。非15类别也先清隐藏位，然后才尝试 image-info；即使 info 未成功，也不能承诺 flag 没变化。bit0 的“隐藏”名来自 add/remove、invalidations 的行为及 LVGL 来源候选，原枚举版本尚未认证；最强的指令事实是上述 bit 操作及调用顺序。

## a00ed560 的本链正常 class0 路径

最小控件存储视图如下；它不代表完整结构体：

| 偏移 | 宽度 | 本轮行为 |
| --- | --- | --- |
| `+0x24` | word | 对象 flags；由 add/remove 更新 bit0 |
| `+0x2c` | word | 当前 source 指针；class0直接保留 ROM 描述符地址 |
| `+0x3c/+0x40` | word | 从 info header 的 unsigned16 width/height 扩展写入 |
| `+0x44/+0x48/+0x4c` | word | 后续变换门：分别与0、256、256比较；角色候选角度/双轴缩放 |
| `+0x58` | byte/halfword | source type bits0..1、格式 bits2..6；保留 bit7及更高原字段 |

`a00dd454(src)`：NULL返回3；首 byte 在 `0x20..0x7f` 返回1，否则返回 `(first_byte>>7)*2`。16 个描述符首 byte `0x19`，所以本链分类均是0，而不是文件名/符号。`a00ed5b6` 在分类前先请求 `a00dddf4(widget)`。info 失败时有日志及恢复返回，未到新源/宽高写入；class3/null清理和class1/2复制路径不属于本链，仅保存全原字节。

正常 class0 关键指令顺序：

```c
// 此处前置顺序：invalidate(widget); type=classify(src); ok=get_info(src,&header)
if (ok != 1) { log_info_failure(); return; }
if ((header.flags & 0x10) &&
    (load32(src+0x14)==0 || load32(src+0x18)==0)) {
    log_missing_aux_data(); return;
}
old_type = load_u16(widget+0x58) & 3;
if ((uint16_t)(old_type-1) <= 1) a008ab8a(load32(widget+0x2c));
store32(widget+0x2c, src);                  // a00ed6ce，直接保存描述符
store32(widget+0x3c, load_u16(header+4));    // a00ed6d2/de
store32(widget+0x40, load_u16(header+6));    // a00ed6e0/ea
b = load_u8(widget+0x58);                   // 在这些写后重读
store_u8(widget+0x58, (b&0x80) | ((header.byte1<<2)&0x7c) | (type&3));
a01b1ee6(widget);
a00ed438(widget);
if (load32(widget+0x44)!=0 || load32(widget+0x48)!=256 ||
    load32(widget+0x4c)!=256) a00d89c6(widget);
a00dddf4(widget);
```

旧源类型的真实读取位于 info/aux guard 之后，没有在 info 前提前读取。描述符 `+0x14/+0x18` 本轮皆0，但 header.flags 是实际 decoder-info 输出，不能据描述符零值断言此门必过或必失败。

`a00ed6b6..c4` 旧源类型判定含厂商 `a00ed6c0` 原 word `0x3c07b78b`：opcode=0x0b、funct3=3、rd=rs1=15、msb=15、lsb=0，对原差值取低16 bit (`th.extu a5,a5,15,0`) 后再 unsigned 比较。完整 setter 的同 word 还在 `a00ed5f8/a00ed748`。不是 signed 比较，也不是把 `old_type==0` 当 free 条件。模型来自既有只读 `ap01thead2.sinc:3930–3934`；本轮保留模型原文/原编码，没有改模型或认证芯片运行时。`a008ab8a` 的释放角色沿用既有 allocator 合同；本轮仅证明条件与参数，不重做 heap 库。

所有权：class0新源不分配、不复制、不 free；控件持有指向 ROM 描述符的非拥有引用。若旧源类型为1或2，本路径先释放旧 `+0x2c` 后覆盖；若旧类型为0则不释放旧 ROM 源。没有 code-cache 去重门，正常同一个描述符也重新 info/提交更新。生命周期结束时谁释放 widget/context 仍未连接，不能以 ROM 源无需 free 推导 UI 对象无需销毁。

## decoder-info 的 ABI、成功和断边

`a0082e32(src,out_header)`：以 `a0080d8e(local,0x4c)` 初始化局部，写 `local+0xc=src`，再次 classifier 后把 type 写 `local+0x10`，再 `a0082c8c(&local,out_header)`，最后用 `SNEZ` 将返回指针/值规范为0/1。初始化 helper 的“清零”职责是调用形状及通用用途候选，内部未在本轮认证。

dispatcher `a0082c8c` 对本链 class0：先 `a0080d8e(out_header,12)`，取 `src=load32(local+0xc)`、type byte；`a0082cbe` 检查 `load32(src+0x10)` 非零后进入 registry。16个描述符的该字段为PNG数据指针，均非零。registry 基对象是 `62fc957c`，decoder-list head 在 `+0x114`；缓存对象在 `+0x120`。class0跳过文件类型1的文件/缓存预备动作，走 `a0082d76` 起的链表。

对每个 decoder 节点 `d`，`load32(d+0)` 和 `load32(d+4)` 均须非零；准备 `local+0x14` 的辅助位置后，重新从 `d+0` 取函数，`a0082d94..9c` 明确以 `a0=d,a1=&local,a2=out_header` 经 `C.JALR a5` 调用，成功结果**必须等于1**。失败在 `a0082e22..28` 用 registry `+0x110` 提供步长，取 `load32(d+step+4)` 迭代。未找到则返回0；成功返回 decoder 节点指针，再被 wrapper 转为1。

成功后如 `out_header+8` 的 unsigned16 stride 为0，dispatcher按格式计算并 SH 回 `+8`：格式20用 width×2，其他格式经 `a00897c2(format)` 取得因子后 `(width*factor+7)>>3`。本轮没有认证该 helper 的颜色深度表。class0成功返回后无文件资源关闭/拷贝分支。`out_header` 是12 B临时输出，setter只持久化宽高和格式，不保存 header 栈地址。

**断边精确位置**：registry 的初始化/PNG decoder注册及实际节点 `+0` 指向哪个 info callback 未恢复。不能因为 payload 是PNG就编造具体 decoder地址、声称 header.flags==0、宽高一定等于IHDR或 info必成功。原件 PNG 的 IHDR尺寸是资源事实；控件字段实际写入值由 callback 输出决定。闭包已到 source保留及控件更新入口，以 info成功为条件，不扩通用 PNG解码算法。

## 更新依赖与返回边界

`a01b1ee6` 依次以 `(widget,0)` 调 `a00901cc`、`a00901e2`；任一个返回 `0x3fffffff` 则调用 `a00d8f42(widget)`。没有直接写图像源或尺寸。两个 getter 只保留参数和 sentinel门，不重复恢复内部。

`a00ed438` 读 `load_u16(widget+0x58)&0xf00`；非以下模式直接返回。四种模式均先 `a00ed198(widget,0)` 再 `a019dd98(widget)`。模式 `0xb00/0xd00/0xe00` 还要求源宽高 `+0x3c/+0x40` 均非零；经 `a00d929a(widget)` 后取 `W=a00d93a2(widget)`、`H=a00d93fa(widget)`，signed DIV 形成 `sx=(W<<8)/source_w, sy=(H<<8)/source_h`。`0xb00` 以 `(widget,sx,sy)` 调 `a00ed314`；`0xd00` 两轴选 signed min；`0xe00` 两轴选 signed max；`0xc00` 直接 `(widget,256,256)` 调该函数。a00ed314内部不展开，不声称这里已经 rasterize。min/max 条件移动 `a00ed4f2` 原 word `0x42f9160b` 经本地模型明确是 `th.mvnez a2,s2,a5`，rd=12/rs1=18/rs2=15；`a00ed540` 的共享跳转保留，模式e的比较方向不同。没有擅自合并调用顺序或补除零以外的安全修正。

setter最后的 `a00d89c6` 与 `a00dddf4` 是变换相关请求及区域失效边界，后者沿用既有 invalidation 系列的门合同，不等同物理刷新。图像 setter、flag setter及selector都没有统一设置数值成功返回；本callback也不消费。各callee内部可留下a0，恢复伪代码采用操作形式仅为可读，不认证原始void声明。

## 事实、推断、未知及静态验证

事实：两个独立整数转换/word写；借用输入的word图标传递；具体ctx控件生产/保存；unsigned code分组及两种q判定；资源地址/PNG格式；flag重读/更新顺序；class0描述符指针保留；旧类型决定释放；info间接ABI与成功==1；header字段写宽度；更新调用与返回未消费。推断：q可能为昼夜/模式；bit0为隐藏；源字段/缩放模式的业务名称。未知：q写者、准确气象/资源符号名、完整constructor/失败处理、decoder注册及精确info callback、最终渲染/屏幕效果、UI与ctx销毁、并发存活保证、库版本/厂商修改。

来源状态：ROM直接引用 `lv_image_set_src`（`a056d750`）和 `/home/jiangmingmin/ap01/AP01_BL618/apps/graphics/lvgl/lvgl/src/widgets/image/lv_image.c`（`a056af14`），以及add/remove flag名称，支持LVGL image/object来源候选；没有认证精确版本或未修改实现，新增已认证开源排除为0。`a00a5d5c/a00a6998/a0198946` 的厂商胶合角色来自其业务连接，原函数符号未知。完整原字节留存不等于完整库功能恢复。

实际执行本轮 verify.py 通过：11核心+2必要谓词、17窗口、3066B、1011条指令、92项独立编码检查、4个厂商word按原模型解释、16个描述符地址及PNG全块CRC/IEND验证、剩余未知指令0。脚本首次有目录层级路径错误、增补branch检查时一处地址抄成半字中间，均在原字节断言中失败并改正后重新通过；没有触发目标代码。另检查报告相对链接、独占文件范围及 `git diff --check`。这不是目标运行观察、正常输入回放或功能测试；没有制作哈希/复制清单。

一个后继闭包：从 `62fc957c+0x114` decoder注册生产者到PNG info callback的成功返回/header写入，维持静态，仅闭合本16个ROM描述符需要的info，不扩全部PNG算法/最终绘制。管理者另询H01天气订阅候选：本轮已遇到的a00b3a68历史incoming refs还有 `a005e1fc/a005e8dc/a00b8bc2`；可取 `a00b8bc2` 为注册入口。现有遇到的材料未给其具体caller入口、callback或清理入口，明确未知，不额外扩扫描冒充已找到。
