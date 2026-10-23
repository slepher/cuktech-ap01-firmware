# A21：0041 PNG decoder 注册、info 返回与注册对象生命周期

2026-10-23；基线 `ab67c6f6f873d4f38f335db9ddfa3d77f743dc5b`，分支 `codex/re-0041-a21`。本轮已从真实注册写指令连通 **global initializer → registry 头插 → `a00eb6fe` PNG info callback → dispatcher 返回 decoder 指针 → wrapper 返回 1 → image setter 已验收接口**。另连通 global deinit 的 registry clear、逐节点 unlink/free；无需把未知注销边伪造成常驻。初始正常注册顺序中 PNG 位于 BIN 前面，名字为 `LODEPNG`。

结果是静态条件结论：正常初始化完成、分配成功、registry 未被后续新注册覆盖/改变且 ROM 原件不变时，A20 的12个正常天气描述符由此 PNG info callback 识别，向 setter 返回 `cf=0x10`、宽高及 `stride=4*width`。本轮没有执行 decoder，也没有恢复像素解压、open/close 算法或最终绘制。**输出 header 并非照抄 ROM 描述符的 header**：ROM 源开头是 `19 01 00 00`，info 结果开头是 `00 10 00 00`。

遵循 [共同规则及 A21 任务书](rolling-management-0041-20261023.md)和 `reverse-engineer-anything` skill，读取 [A19](weather-icon-flow-a19-0041-20261023.md)、[A20](weather-icon-review-a20-0041-20261023.md)。A20 对 `a00d8ffe → a00d7546(obj,2)`、unsigned16 `obj+0x28` 状态谓词的纠正仍是既有合同；本轮不重解 flag/image 后处理。只写本报告和独占 analysis；未改共享索引、ROM、生产/构建代码、分析器模型、其他 worktree，也未创建下级 agent。

## 证据、范围与函数

原件只读 `D:/Documents/PlatformIO/Projects/cuktech-ap01-firmware/roms/0041/ap01-1.0.2_0041.bin`；身份沿用既有 dossier/A20 的 SHA-256 `972db4c136c7ed9e24a83c07c1a7fd62040ca018b08ca285216d26b1fee3c6b9`，不新增散列清单。映射 `file_offset = VA - 0xa0000000 + 0x1000`。

- [verify.py](../../analysis/png-info-lifecycle-a21-0041-20261023/verify.py)读取原件，Capstone 5.0.7 解普通 RV32/RVC；独立取原编码字段核对 JAL、I/S/B、RVC memory/CR 和厂商 indexed load/store。脚本只是字节/编码/静态表达式核验，不调用或模拟固件函数。
- [instruction-evidence.json](../../analysis/png-info-lifecycle-a21-0041-20261023/instruction-evidence.json)保存全部窗口原字节、偏移、字段、65项断言、12个源及条件输出、有限 direct-call inventory 引用和 ISA 模型片段；[instructions.txt](../../analysis/png-info-lifecycle-a21-0041-20261023/instructions.txt)可逐地址审阅。
- 已有 whole-ROM index 只提供定位和历史 Evidence，不作为本轮新 REA 会话结果。本轮不打开、切换或写共享 REA database。它的6487个 provider procedure/direct-call inventory 对 create 的调用者给出 `a008e3ac`，对 initializer/deinitializer 都给出 `a005cc1e`；这不排除间接引用或未定义函数。

| 10项核心 | 本轮恢复范围/ABI |
| --- | --- |
| `a008e3ac` global initializer | 只恢复 global 清零、registry size、BIN/PNG 注册顺序及具体 callback 写入片段；不是整函数全部 GUI 初始化验收 |
| `a0082914` decoder create | 无参；registry 分配并头插、清28 B payload，返回 node |
| `a008aec0` list insert-head | `(list*) → node/NULL`；分配 size+8，双链接写入，发布 head/tail |
| `a0082e32` info wrapper | `(source,header_out) → bool`；栈 local 76 B、dispatcher 非零归一化 |
| `a0082c8c` info dispatcher | `(local*,header_out) → decoder*/NULL`；重点 class0 registry 路径 |
| `a00eb6fe` PNG info | `(decoder*,local*,header_out) → 1/0`；class0 完整，class1 仅接口界限 |
| `a008ae42` list clear wrapper | `(list*)`；传 NULL 清理 callback 到 walker |
| `a008adf4` clear walker | `(list*,optional_callback)`；保存 next、unlink/free 或 callback |
| `a0089d02` list unlink | `(list*,node)`；修 head/tail 或双向邻接，不负责 free |
| `a008be06` global deinit | 只恢复 cache 销毁先于 registry clear、registry clear、末尾 global initialized byte 清零片段 |

必要依赖：`a00501be` comparator、`a00897c2` format bit-depth、`a0089cda/a0089cee` prev/next 写、`a008aea0/a008ae8c` allocation adapters、`a008ab8a` free adapter、`a005cc1e` 的初始化/清理调用片段。`a0089bde`、clear-memory、底层 allocator、diagnostic assert 保留明确接口，不因名字像标准库而认证排除。open `a00eb7b6` 与 close `a00eab9a` 只定位注册身份，不展开像素处理。

## 注册对象布局、顺序和所有权

`G=0x62fc957c`。registry `L=G+0x110=0x62fc968c`：

```c
struct Registry {                 // observed RV32 layout
    uint32_t payload_size;        // +0, 28
    Decoder *head;                // +4 = G+0x114
    Decoder *tail;                // +8 = G+0x118
};
struct Decoder {                  // 28 B zeroed payload
    InfoFn info;                  // +0
    OpenFn open;                  // +4; dispatcher requires non-NULL even for info
    uint32_t field08;             // +8, zero after PNG registration
    CloseFn close;                // +0xc
    uint32_t field10;             // +0x10, zero
    const char *name;             // +0x14, ROM "LODEPNG"
    uint32_t field18;             // +0x18, zero
    Decoder *prev;                // +0x1c, allocator trailing link
    Decoder *next;                // +0x20, allocator trailing link
};                               // allocation 28+8 = 36 B
```

初始化 `a008e3d0` 调 clear-memory `(G,0x210)`，所以初始 head/tail 为0。`a008e4c0` 建 `s4=G+0x100`；`e61e` 将 `a5=0x1c`，`e620 2328fa00` 是 `SW a5,0x10(s4)`，故写的是 **G+0x110**，不是其它 list 的大小。

`a008291e/22` 常量为 L；`2926 ef80a059` JAL 到 `a008aec0`。后者先取 list+0、加8再调 `a008aea0`；分配成功先 `set_prev(new,NULL)`、`set_next(new,oldhead)`，oldhead 非空再 `set_prev(oldhead,new)`，随后 `SW new,list+4`；原 tail 为空才 `SW new,list+8`。创建者 `296c` 设置 `a1=0x1c`、保存 node，`2970` 调 clear-memory `(node,28)`，重载返回 node。**链接在 payload 之后，不被28 B清零覆盖**。内存发布和 payload 清零的原顺序保留；不额外推断线程同步保证。

`a008e6ea` 第一次 create，成功后注册 BIN info/open/area/close/name。`a008e82c` 第二次 create，具体原指令如下：

| 原指令位置 | 写入 |
| --- | --- |
| `e830 b7b70ea0; e834 9387e76f; e838 1cc1` | `LUI a5,a00eb000; ADDI +0x6fe; SW node+0` = `a00eb6fe` |
| `e83a b7b70ea0; e83e 9387677b; e842 5cc1` | `node+4 = a00eb7b6` |
| `e844 b7b70ea0; e848 9387a7b9; e84c 5cc5` | `node+0xc = a00eb000 - 0x466 = a00eab9a`；必须按 signed12，不能误成 `a00eb39a` |
| `e84e b73726a0; e852 9387074f; e856 5cc9` | `node+0x14 = a02634f0`，原件字符串 `LODEPNG\0` |

因此正常 initializer 尾部 list 顺序是 **PNG → BIN → NULL**。源码名和名字字符串只是佐证；具体 callback 身份由 create 及 store 的指令路径建立，绝非靠 signature 搜索替代注册路径。

create 里分配 NULL 会进入现存 log/assert 分支，之后代码继续到 payload clear；本轮不执行/探索失败后续。正常结果与所有权结论明确以分配成功为前提，未擅自增加新 fail return 或修复行为。

## class0 选择、间接 ABI 和输出

wrapper 在栈分配0x60 frame，清 `local[0x4c]`；写 `local+0xc=source`、`local+0x10=classify(source)`，调用 `(local,header_out)` dispatcher，最后 SNEZ。因此 dispatcher 返回的是 node 指针，wrapper 才返回 bool 1。

已验收描述符首 byte0x19 → class0。dispatcher 首先清 header_out 的12 B；class0 要求 `load32(source+0x10)!=0`（payload pointer）。class1 cache/文件路径跳转存在，但本 class0 路径绕过它们，直达 `a0082d76` 载入 `G+0x114`。

```c
// 表达式是恢复伪代码，不是原源码；只展开正常 class0。
Decoder *info_class0(Local *d, Header *out) {
    zero(out, 12);
    if (d->source->data == NULL) return NULL;
    for (Decoder *n = G.registry.head; n; n = load32((byte*)n + G.registry.payload_size + 4)) {
        if (!n->info || !n->open) continue;
        a0089bde((byte*)d + 0x14, 0, 0);  // result ignored; d local was zeroed
        int r = n->info(n, d, out);        // reload +0 immediately before call
        if (r != 1) continue;
        if (out->stride16 == 0) {
            uint32_t w = out->width16;
            if (out->cf8 == 0x14) out->stride16 = (uint16_t)(w << 1);
            else out->stride16 = (uint16_t)((w * bitdepth(out->cf8) + 7) >> 3);
        }
        return n;
    }
    return NULL;
}
```

`a0082d82/86` 分别读 node+0/+4 作门；`d94` 重读+0，`d96` `a2=header_out`、`d98` `a1=local`、`d9a` `a0=node`，`d9c 8297` 为 C.JALR a5。`d9e 63129509` 是 `BNE a0,s9,a0082e22`，`s9=1`：不能把 callback 任意非零算成功。`e22` 读 payload_size、加到 node，再 `e28` 读+4取 next。无匹配回0；找到则 node 保存在s1，经公共尾部返回。

callback `a00eb6fe` 的 class0 路径：读 unsigned byte `local+0x10`；大于1回0，等于1进入文件读24 B路径，等于0到 `a00eb792`。后者 `source=LW local+0xc`；`LW source+0xc` data_size 必须 **unsigned >7**；`LW source+0x10` 取得 data。`a00eb79e/7a4` 重构 `a059bf2c`、`a2=8`，`7aa` 调 comparator(data,signature,8)，非零回0。signature 为 `89 50 4e 47 0d 0a 1a 0a`。

比较通过才令 `a0=data+0x10`，`a00eb7b4` 跳到 `a00eb752` 共同输出片段（class1由 `a00eb74e` 将 a0设为栈24 B缓冲的+16）。它没有在此 class0 路径跑 PNG CRC、chunk walker 或解压：

```c
int png_info(Decoder *unused, Local *d, Header *out) {
    // only class0 shown; class1 has its own read-count==24/signature gate
    ImageDescriptor *s = d->source;
    if (s->data_size <= 7u) return 0;
    if (compare(s->data, rom_signature, 8) != 0) return 0;
    const byte *p = s->data + 16;
    out->cf8 = 0x10;
    uint32_t v = load_le32(p);
    out->width16 = (uint16_t)(((v >> 8) & 0xffffff00u) + (v >> 24));
    v = load_le32(p + 4);
    out->height16 = (uint16_t)(((v >> 8) & 0xffffff00u) + (v >> 24));
    return 1;
}
```

这里是 **LW、SRLI8、ANDI -256、SRLI24、ADD、SH**，不可改写成无截断的 full32 BE load。正常现有尺寸都小于65536，公式等价于提取 PNG 大端尺寸的低16位。本轮只对这些原 ROM 源作静态结果计算，不进行异常长度或尺寸测试。

`Header` 输出布局：byte0=0、byte1=cf0x10、+2 unsigned16 flags=0、+4 unsigned16 width、+6 unsigned16 height、+8 unsigned16 stride、+10 unsigned16=0。callback 只写 byte1/+4/+6，其余来自 dispatcher 清零；随后 stride 为0触发补值。`a00897c2` 对 `(cf-6)&0xff` 查 `a0263724` byte table；cf0x10用 index10，原 byte `a026372e=0x20`，故 stride16=`4*width`。**cf 的数值及32 bit depth 已证；精确 LVGL enum/source version 没有认证，不拿 ARGB 名称替代此数值合同。**

| category | ROM descriptor | width × height | stride | 12 B output header |
| --- | --- | --- | --- | --- |
| 1 | `a0251da8` | 19 × 19 | 76 | `00100000130013004c000000` |
| 3 | `a062fb30` | 20 × 16 | 80 | `001000001400100050000000` |
| 2/4/6/7/8/9/11/12/13/14 | 各地址/源字节逐项保存在 evidence.resources | 20 × 20 | 80 | `001000001400140050000000` |

每个值均基于实际注册 callback 的 loads/shift/store 表达式与原 ROM 源，不由 PNG 标识或 CRC 单独推定“decoder运行成功”。A20 已验收 `a00ed560` 在 wrapper 成功及 aux guard 通过后才替换 source，class0 借用 ROM descriptor、写 obj+0x3c/+0x40 的word尺寸和格式byte、再请求更新；本轮只提供其缺失的真实 info 生产者。info 没有分配/持有像素缓冲，没有获取新的 ROM 源所有权。

## 注册对象清理与生命周期边界

global deinit `a008be06` 的 `beb2..beca` 先取 `G+0x11c/+0x120` 两个 cache 对象，分别经 AUIPC/JALR 到同一个外部 cache-destroy 合同 `a019d010`；本轮不展开 cache 内部。随后 `beca 3795fc62; bece 1305c568` 构造同一 L，`bed2 efe01ff7` 调 `a008ae42(L)`，该 wrapper 令 `a1=0` 再调 `a008adf4`。

```c
void clear_list(Registry *l, void (*callback)(Decoder*)) {
    Decoder *n = l->head;
    while (n) {
        Decoder *next = load32((byte*)n + l->payload_size + 4);
        if (callback == NULL) {
            unlink(l, n);
            a008ab8a(n);  // null/sentinel-aware free adapter → backend boundary
        } else {
            callback(n); // alternate interface exists, not used by this registry clear
        }
        n = next;
    }
}
```

`a008ae22` 在任何 unlink/free 之前保存 next；`ae2e→a0089d02`，`ae34→a008ab8a`，`ae38` 才换节点。unlink 的 head 分支将 head=next，next为空清tail，否则清 next.prev；tail 分支将 tail=prev，prev为空清head，否则清 prev.next；中间节点先 prev.next=next，再 next.prev=prev。两组末尾链接不在 callback payload 内。

在初始 PNG→BIN 状态下，clear先保存BIN，unlink/free PNG，再unlink/free BIN，最终head/tail=0。此 clear **不会调用 decoder+0xc 的 close callback**；`close=a00eab9a` 是另一类 open 会话的回调字段，不是注册对象 destructor。全局销毁末尾 `a008bf44` `SB zero,0(s1)` 清 G initialized byte。注册内存由 registry 承担，到 global deinit 回收；ROM name/signature/descriptor都是借用常量，不逐项释放。

父函数的有限挂接证据：`a005cc68..cc78` 测 G+0 initialized byte，为0跳 `a005cd36`，该点直接 JAL initializer，随后跳回父流程；已有 whole-ROM xref Evidence `ev_ca01df8c53039f6555a9f8ff2e36f2c428a476860fa6919bcdf0cd4866e7e0aa`。同父函数 `a005eea0` 测 G+1 byte，为0到 `eeaa` 保存返回值，`eeae` JAL global deinit，重载返回值再跳父公共尾部。这证明有实际父清理调用，不证明所有导航都会触发 global deinit，也不认证完整父函数的事件/退出条件。注册对象正常驻留于 GUI 全局会话，不是每次 weather icon 更新创建/销毁一次。

状态可概括为 `G未初始化 → 正常init成功并注册BIN/PNG → registry借用供info → global deinit销毁cache → 清registry并free节点 → G initialized=0`。每次 info 的 local/header 是同步栈借用，返回后该 local 不再由 callback 持有；decoder 与 ROM 数据在此路径不转移给 image 对象。是否有其它后续注册、并发清理协调或 active open descriptor 的最终关闭，不由本闭包推定。

## 厂商编码、来源、验证及未闭合边

5个 Capstone 不支持的 word 都逐字段核原件，而非只读反编译：

| 地址 / bytes | 字段与恢复 |
| --- | --- |
| `a0089ce4 0bd6f540` | opcode0xb、funct3=5、top5=8、rd12/rs1=11/rs2=15、shift0：`th.srw a2,a1,a5,0`，写 prev 到 node+size |
| `a0089d3a 8bc5e540` | funct3=4、top5=8、rd11/rs1=11/rs2=14、shift0：`th.lrw a1,a1,a4,0`，取 prev |
| `a00897de 0bc5a780` | funct3=4、top5=16、rd10/rs1=15/rs2=10、shift0：`th.lrbu` table byte |
| `a00501ee 8b47e580` / `a00501f4 8bc6e580` | 同 unsigned indexed byte 形式，分别取 comparator 两侧 byte；word对齐快比较不等后从原地址逐byte比较 |

本地只读 `.../evidence/rea-0041-20261017/ghidra/Ghidra/Processors/RISCV/data/languages/ap01thead2.sinc` 中相应3个规则原文保存在 evidence.model；它们分别实现地址 `rs1+(rs2<<shift)` 的32 bit写/32 bit读/unsigned8读，均不回写base。本轮没有改模型；本地模型吻合不冒称独立硬件/厂商ISA认证。

来源候选：原件 `a025ebf4` 含 `/home/jiangmingmin/ap01/AP01_BL618/apps/graphics/lvgl/lvgl/src/draw/lv_image_decoder.c`，`a056b1a4` 含 `.../src/libs/lodepng/lv_lodepng.c`，注册字符串 `a02634f0="LODEPNG"`。source-path inventory 的 PNG xref 来源 `ev_e1af5430bc7685b72bdfb5647fa0aa8d01ff1b8e83ad9d68375a6e858012f616` 归属 open callback `a00eb7b6`，与注册事实相容。准确 LVGL/LodePNG 版本、上游未修改认证均未知；本轮无外连下载，无新增已认证开源排除。通用list、comparator和厂商注册glue继续按实际指令恢复。

实际运行 `verify.py` 通过：[review-index.json](../../analysis/png-info-lifecycle-a21-0041-20261023/review-index.json)记录10核心（initializer/deinitializer为明确片段）及8必要依赖、25窗口、1698 B、606条指令、65项编码断言、5个厂商word、12个正常ROM源条件输出、未解指令0。开发核对中修正两处证据窗口边界及一处临时 close 常量误算，均由原件编码断言发现并在最终证据内纠正，未改原件/模型。报告链接和 `git diff --check` 另核；不编译项目、不执行固件/仿真、不作设备/网络/历史回放/异常输入/缺陷实验。

事实：PNG注册身份、头插优先顺序、同步info ABI、严格1成功门、header写宽/补stride、registry clear unlink/free顺序已有原字节支持。推断：在已述正常前提下，12个现有ROM源的info将返回该PNG node，wrapper为1，header值如表；这是静态推导，不是运行观测。未知：所有后续registry修改者、完整上层global deinit触发语义、open descriptor像素资源与并发关闭协调、准确库版本、物理绘制。

本业务问题在正常初始化和已知global清理接口范围内闭合；未知未被隐藏为“所有PNG库已恢复”。一个后继闭包建议：从 `a00eb7b6` 的正常 class0 open 分支追 source→持有的decoder-session数据/像素对象→已注册 `a00eab9a` close 的归还，约5–12核心，以底层通用解压算法为明确边界；先证真实open/close ABI和所有权，不扩完整PNG压缩算法或最终绘制。本轮不自行领取后继，交独立agent复核。
