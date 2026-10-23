# A24：0041 PNG session、像素与 cache 持有闭包独立复核

2026-10-23；独立基线 `5e0da7b7a0e8e0f6c9552b67b643efe40428026f`，分支 `codex/re-0041-a24`。**纠正一处构造器 callback 归属后，限定接受 A23 的十核心 session/open/close/cache 持有结论。** `a0081d90` 的 data 对齐回调来自全局槽 `62fc964c`，不是 `62fc9674` handler 表的 `+8`。这不改变直接销毁先 raw callback、后 Pixel 对象 free，也不改变 cache close 只证到 release 的结论。

按[共同规则与 A24 任务书](rolling-management-0041-20261023.md)，读取 [A23](png-session-lifecycle-a23-0041-20261023.md)、[A22](png-info-review-a22-0041-20261023.md)及 `reverse-engineer-anything` 技能。仅写本报告和独占 analysis；不改 A23，不改共享索引、主树、其他 worktree、ROM、生产/构建代码或分析器模型。没有运行固件/仿真/解压/绘制、设备/外网、异常输入或历史回放，没有创建下级 agent 或自领后继。

## 证据与方法

原件只读：`D:/Documents/PlatformIO/Projects/cuktech-ap01-firmware/roms/0041/ap01-1.0.2_0041.bin`。沿用既有 dossier 的身份 SHA-256 `972db4c136c7ed9e24a83c07c1a7fd62040ca018b08ca285216d26b1fee3c6b9`，不新建哈希/复制清单。映射为 `offset = VA - a0000000 + 1000`。

本轮独立编写 [review.py](../../analysis/png-session-review-a24-0041-20261023/review.py)，不复制或调用 A23 验证器。重新读取原件，由 Capstone 5.0.7 解普通 RV32/RVC，独立位提取核 JAL、AUIPC/JALR、B、I/S 的地址、寄存器、宽度及有符号位移。厂商字独立提取 funct、寄存器与 shift，并只读本地 `ap01thead2.sinc` 核语义。模型是本地恢复规则，不冒称厂商手册或硬件运行认证。

[review.json](../../analysis/png-session-review-a24-0041-20261023/review.json)保留 ROM 地址/偏移/原字节、22 窗口、90 项断言及厂商字段；[instructions.txt](../../analysis/png-session-review-a24-0041-20261023/instructions.txt)逐地址可读；[review-index.json](../../analysis/png-session-review-a24-0041-20261023/review-index.json)为实际计数。没有打开/切换共享可写 REA target 或数据库；既有报告仅作问题/入口定位，新证据来自独立原件读取。未用新的 REA Evidence ID 冒称实时分析。

## 逐项裁定

| A23 核心/主张 | 裁定 | 本轮原件依据与边界 |
| --- | --- | --- |
| `a00e5c78` owner 的 76 B 栈 session | 接受片段 | `5c78 7171` 分配0xb0栈，`5c8c 0019` 建s0=sp+0xb0。`5d2e 130544f8` a0=s0-7c，`5d32` 调open；`5d38` BEQ恰1才到`5d74`；`5d7c`同地址作a2交`a018f9e8`，`5d88/8c`同地址作a0调close。失败支日志后回栈，没有close。完整几何/循环/物理绘制未核。 |
| `a019b168` 清session、命中与miss | 接受 | `b176` 长0x4c，`b17c`到`a0080d8e`，其`0d96/98`把长度装a2、a1=0。source写+c、class为SB到+10；cache容量非零才存+40并查找。命中由payload+c/+10写decoded/decoder，entry写+44，回1；没有header或user_data恢复写入。 |
| open真实ABI与失败返回 | 接受 | `b1fc 5c41` load decoder+4；`b1fe a685` a1=session；`b200 8297` C.JALR，a0仍decoder。`b204`保存callback返回于s2；`b206 e312f5f8` BNE a0,1到`b18a`，`b190`从s2回a0。非1返回保留，不能统一写0。 |
| `a00eb7b6` class0借ROM→decode→像素交换/发布 | 接受 | `b91c/91e/922`取descriptor、data+10、size+c；`b8b0`仅清out pixel局部，`b8b4`调decode，`b8b8`先重读pixel再分支。status非0且pixel非空才destroy/置0；status0不补NULL门。`b8ca`重读class，仅class1归还临时压缩buffer。`b980`写decoded后才cache插入；插入失败回0而不回滚/补destroy。 |
| `a00829e4`正常options为0对象直返 | 接受本路径 | `b1f4` SW0到session+4，`b1f8` SB0到+8；`2a02/08` option04=0到`2b80`，option05=0经`2b84`到epilogue，`2bd4`回原s1 pixel。其他options路径未核，不称库不存在转换。 |
| `a0082980` cache payload持有与class1副本 | 接受 | `29a0`调`a019d914`，非空才取payload；`29b4`先写pixel+c；class1才复制source+4；`29c8/cc`写userdata+14和decoder+10。PNG传userdata0；entry由session+44持有；后端entry分配/引用内部仍未知。 |
| `a00828d6`先decoder close后cache release | 接受 | `28e2/28e6`取decoder/close；`28ea/ec` ABI `(decoder,session)`。callback后`28ee..2900`重新取全局容量及session+40/+44，均非零才`2902`调`a019d9f6(cache,entry)`。无session本身free或字段清零。 |
| `a00eab9a` byte+6/capacity分流 | 接受 | `ab9a` LBU session+6；非零直接destroy；为0才取global cache+8，非零直接返回；容量0才`abb4/abb6` destroy(session+2c)。不能把cache路径close写立即free。 |
| `a0081f26` raw归还先于28 B对象 | 接受 | `1f72 83572500` LHU flags+2，AND0x10；不owned只日志返回。owned取handlers+18，`1fba`取handler+4，非空则`1fbe`取pixel+14作a0、`1fc0`间接调用；`1fc2/1fc4`才free_adapter(pixel)。NULL/assert诊断原路径不改写成安全return。 |
| `a0081d90`像素构造 | **纠正callback归属，其他接受** | 申请28 B、经传入handler+0分配raw、+14保存raw及+18保存handler、SH宽高/stride，皆成立。**`1e9c`取的是绝对全局62fc964c，而非handler+8**，详见下一节。该差异影响data生成者身份/后继定位，不改变raw字段与析构顺序。 |
| `a008abb0` payload清理与init连接 | 接受，限安装/内容 | `abc6`仅owned pixel调destroy；随后`abca`重读class byte+8，class1才free source副本+4；不free payload自身。init `e64e/e652`形成a008abb0，`e660`放三word表第三槽，copy后传cache创建，`e684`发布G+11c。后端何时调用cleanup未核。 |
| `a019262e`8428 B完整算法、handler安装、cache驱逐/引用内部 | 未核 | 仅针对输出构造/临时析构的必要片段核；不认证全部PNG/LodePNG、精确源码版本或正常ROM每个源运行成功。 |

## 构造器纠正：两个不同的间接调用来源

A23 “成功写……再可选handler表+8以 `(raw,cf)` 得aligned data写+10”应替换为：

> 成功raw返回仍在a0，构造器从独立全局槽 `62fc964c` 取对齐data callback；槽非空时以a0=raw、a1=cf间接调用，返回值存pixel+10。槽为空时本构造器写pixel+10为0。pixel+14仍保存原raw，pixel+18仍保存传入handler表。

可定位原指令：

```text
a0081e90 b797fc62  LUI  a5,0x62fc9        ; a5=62fc9000
a0081e9c 03a7c764  LW   a4,0x64c(a5)     ; *(62fc9000+64c)=*(62fc964c)
a0081ea0 8147      LI   a5,0
a0081ea2 01c7      BEQZ a4,a0081eaa
a0081ea4 ca85      MV   a1,s2            ; cf
a0081ea6 0297      JALR a4               ; a0仍为raw allocation返回
a0081ea8 aa87      MV   a5,a0
a0081eaa 9cc8      SW   a5,0x10(s1)      ; data
a0081eac 23aa8401  SW   s8,0x14(s1)      ; raw
a0081eb4 23ac5401  SW   s5,0x18(s1)      ; incoming handler table
```

`a019290e`/`a0192ada`构造调用把a0形成`62fc9674`，故本PNG输出对象保存的是该handler表。其`+0`为raw allocator，销毁经该表`+4`为可选raw归还；这两个槽与`62fc964c`是不同地址、不同取址链。未恢复`62fc9674`安装/目标，也未恢复`62fc964c`安装/目标；不由已有库布局猜成两者相等或handler+8一定无用。

owned标志的写法也按原宽度保留：先SB cf到+1，再读word+0、AND `0xff00`、OR `0x00300019`并SW+0，因而+2半字包含0x30，析构测试的0x10确实由此设置。宽高/stride分别SH到+4/+6/+8，有截断；data_size为SW到+c。+10/data与+14/raw不能合并。

## 结构、ABI、状态与所有权

以下为恢复伪代码，不是原源码；RV32指针/word为4 B。

```c
struct Session {                     // 76 B, caller stack
    Decoder *decoder;               // +00
    byte options04_07[4]; byte f08;  // +04..+08
    byte pad09[3];
    const Descriptor *source;       // +0c borrowed ROM descriptor
    byte source_class;              // +10
    byte unknown11[15];
    Header header;                  // +20, 12 B
    Pixel *decoded;                 // +2c
    byte unknown30[16];
    Cache *cache; Entry *entry;      // +40/+44
    void *user_data;                // +48
};
struct Pixel {                       // 28 B independent allocation
    byte byte0,cf; uint16_t flags;   // +00/+01/+02
    uint16_t width,height,stride,pad;// +04/+06/+08/+0a
    uint32_t data_size;             // +0c
    byte *data; void *raw;          // +10/+14, distinct
    HandlerTable *handlers;         // +18
};
struct Payload { byte f00[4]; const void *source; byte cls,pad09[3];
                 Pixel *pixel; Decoder *decoder; void *user_data; };
```

真实调用是 `owner(session,source)`→`open_callback(decoder,session)`，不是反转两参；close同样为`close_callback(decoder,session)`。消费入口接收a2=session，`a018fa14`保存到s2，`fa1a`读session+30；本轮仅核入口ABI，没有恢复其完整消费/异步持有内部。owner在该调用返回后立即调用close是已证调用次序，不能据此推物理绘制完成或所有其他caller都相同。

```c
// cache miss的关键原序；显式无source/decoder路径回0。
zero(session,76);
session->source = source; session->source_class = classify(source);
if (global_cache->capacity != 0) {
    session->cache = global_cache;
    entry = cache_lookup(global_cache,key);
    if (entry) {
        payload = payload_of(entry);
        session->decoded = payload->pixel;
        session->entry = entry;
        session->decoder = payload->decoder;
        return 1;                   // 不补header/user_data恢复
    }
}
decoder = info_dispatch(session,&session->header);
session->decoder=decoder;
if (!decoder) return 0;
store32(session+4,0); store8(session+8,0);
status=decoder->open(decoder,session);
if (status!=1) return status;        // b206 -> b18a，不归一化
// decoded及raw/handlers的检查、日志/assert、可选同步按原指令继续。
return 1;
```

PNG class0从source+c/+10借size/data。`decode(&p,&w,&h,data,size)` status0为成功；该返回0同时作为交换循环初始index=0，非额外清变量。`MUL`取低32位w*h，循环以相等退出，读取`data[i*4+2]`与`data[i*4]`后互写，保留byte1/3。原栈p在循环结束重载；失败有p才析构，再置0。class0不free源压缩字节；共同段重读class，只class1归还临时buffer。

成功p经options0直返，写session+2c；capacity非零且option06=0时，entry成功才写session+44。插入失败已写decoded但回0，此owner不close；这是原分支记录，不作异常实验、缺陷判断或修复。新像素来自`a0081d90(62fc9674,w,h,0x10,w<<2)`真实构造边，不能描述成裸RGBA malloc。完整解压器仍为明确合同。

```c
void close(Session *d) {
    Decoder *n=d->decoder;
    if (!n) return;
    if (n->close) n->close(n,d);
    // callback返回后重新读取，不能提前缓存这些判断。
    if (global_cache->capacity && d->cache && d->entry)
        cache_release(d->cache,d->entry); // a019d9f6，内部未恢复
}
void png_close(Decoder *n,Session *d) {
    if (!d->options04_07[2] && global_cache->capacity) return;
    pixel_destroy(d->decoded);
}
void pixel_destroy(Pixel *p) {        // 正常非NULL/有效handler前提
    if (!(load16(p+2)&0x10)) { original_log(); return; }
    fn=load32(p->handlers+4);
    if (fn) fn(p->raw);
    free_adapter(p);                 // raw callback之后
}
void payload_cleanup(Payload *p) {
    if (load16(p->pixel+2)&0x10) pixel_destroy(p->pixel);
    if (load8(p+8)==1) free_adapter(load32(p+4)); // 重读class/source
}
```

正常状态链为 `栈session清零 → hit借cache pixel，或miss选decoder/分配新Pixel → 通道交换/identity → decoded发布 → 可选entry持有 → 真实消费调用 → close直接析构或cache release → owner回栈`。session从未单独malloc/free；decoder归global registry；ROM descriptor/data仅借入；Pixel和raw是独立分配；cache entry/payload由后端管理。class1 source副本与临时buffer不属于class0 ROM所有权。

## 厂商字、来源及剩余断边

| 原地址/字节 | 独立字段解释 |
| --- | --- |
| `a00eb942 8bc5a684` | unsigned byte读，rd11/base13/index10/shift2：data+2+i*4 |
| `a00eb946 0b46a784` | unsigned byte读，rd12/base14/index10/shift2：data+i*4 |
| `a00eb94a 8b55a704` | byte写，src11/base14/index10/shift2 |
| `a00eb94e 0bd6a604` | byte写，src12/base13/index10/shift2 |
| `a00eb7f2 0b48f744` | word indexed读，rd16/base14/index15/shift2，仅class1诊断分支 |

上述模型规则只算`base+(index<<shift)`，不写base；`b952`普通ADDI才改变index。不应解释为postincrement。

事实：已复核真实owner、严格1门、callback返回保留、像素来源构造片段、交換、字段发布、close分流与两层归还次序。推断：正常基础设施有效且PNG decode成功时，此class0像素按这些门进入会话/cache持有。未知：每个ROM PNG的实际执行成功、消费内部保留/完成、8428 B完整算法、raw handler安装及目标、全局align槽安装及目标、cache内部引用/驱逐/何次release触发cleanup。payload cleanup安装不等于每次release实际调用它，release不等于Pixel/raw真实free。

来源沿用ROM路径候选`lv_image_decoder.c`/`lv_lodepng.c`和名`LODEPNG`，准确LVGL/LodePNG版本、厂商差异/未修改源码认证未完成；本轮未查外网、不新增标准实现排除。未因库名排除构造/适配或通用算法。下一闭包建议为 `62fc9674` raw handler安装→allocator/free目标，连同独立`62fc964c`对齐槽的安装/ABI小范围恢复；不扩全heap/PNG/cache。本轮不自行接任务。

实际静态验证：独立脚本通过22窗口、2412 B、827条指令、90项原编码/地址/字段断言、5厂商word，未解0；重新检查报告内部链接及`git diff --check`。未编译、未执行目标/解压/渲染。完成的是A23十核心限定独立复核，非完整PNG/cache或物理绘制认证。
