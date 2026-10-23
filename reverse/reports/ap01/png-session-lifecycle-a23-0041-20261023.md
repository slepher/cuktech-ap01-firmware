# A23：0041 PNG class0 open、会话像素资源与 close 归还

2026-10-23；基线 `a295c3a3fa5863598caa8f57fa19c94475c2789d`，分支 `codex/re-0041-a23`。已连接一条真实调用链：`a00e5c78` 的栈会话 → `a019b168` 通用 open → 已注册 PNG `a00eb7b6` → 像素对象 `session+2c` → `a00828d6` 通用 close → 已注册 PNG `a00eab9a`。正常 class0 从 ROM descriptor 借入压缩数据；新像素对象来自解压输出，不能与 ROM 源混同。close 按会话 byte+6 及全局 cache 容量分流：直接销毁对象，或交 cache release 接口。这里没有将 cache release 等同立即 free。

遵循 [共同规则及 A23 任务书](rolling-management-0041-20261023.md)，应用 `reverse-engineer-anything` skill，读过 A21/A22；A22 对 class0 仍读公共 cache 元数据的精确化沿用。只新增独占报告/analysis，不改 ROM、生产/构建代码、模型、共享索引或别树；未执行固件、仿真、历史回放、异常输入/漏洞测试，未访问设备/外网，未创建下级 agent。作者恢复成果待新 agent 独立复核，不冒称已验收。

## 范围和证据

只读原件 `D:/Documents/PlatformIO/Projects/cuktech-ap01-firmware/roms/0041/ap01-1.0.2_0041.bin`；身份沿用 A22/dossier 的 SHA-256 `972db4c136c7ed9e24a83c07c1a7fd62040ca018b08ca285216d26b1fee3c6b9`，不新增散列/复制清单。映射 `file_offset=VA-a0000000+1000`。

[verify.py](../../analysis/png-session-lifecycle-a23-0041-20261023/verify.py)重新读取原件，以 Capstone 5.0.7 解 RV32/RVC，并独立按位核 JAL、AUIPC/JALR、I/S 宽度/字段、B 条件/目标和厂商 indexed byte 指令。该脚本只解析静态字节与地址，未解释执行固件。[instruction-evidence.json](../../analysis/png-session-lifecycle-a23-0041-20261023/instruction-evidence.json)保留每条原字节/偏移、断言、模型短规则与有限引用来源；[instructions.txt](../../analysis/png-session-lifecycle-a23-0041-20261023/instructions.txt)按地址可读；[review-index.json](../../analysis/png-session-lifecycle-a23-0041-20261023/review-index.json)给实际计数。未打开、切换或写共享 REA session/database；历史 whole-ROM index 仅用于入口定位，新增证据均为重新读原件。

10 核心项如下，片段不作整函数认证：

| 核心 | 本轮边界/ABI |
| --- | --- |
| `a00e5c78` 调用者片段 | `d1a..db8` 内栈会话 open、严格1门、消费、close；几何/完整绘制仍为合同 |
| `a019b168` session open | `(session*,source*)→int`；清76 B、分类、cache hit/miss、info/open分派 |
| `a00eb7b6` PNG open | `(decoder*,session*)→0/1`；class0完整、class1临时文件buffer资源原序只作必要分支记录 |
| `a00829e4` 后处理 | 只恢复新建session +4/+5均0的identity路径；其他配置的转换/复制不展开 |
| `a0082980` cache插入包装 | `(decoder,key,pixel*,user_data)→entry*/NULL`，payload写与class1 source复制 |
| `a00828d6` session close | `(session*)`；间接close，然后条件cache release |
| `a00eab9a` PNG close | `(decoder*,session*)`；+6/capacity门、直接pixel destroy或早退 |
| `a0081f26` pixel destroy | `(pixel*)`；owned flag、handler table+4、raw+14、再free对象 |
| `a0081d90` pixel create | `(handlers,w,h,cf,stride)→28B pixel*/NULL`；分配结构、经handler分配像素、保存结构字段 |
| `a008abb0` cache payload清理 | `(payload*)`；owned pixel析构，再对class1复制source free；不free payload本身 |

必要短依赖：PNG注册常量；`a019262e` 解压器 ABI/输出构造片段（完整8428 B算法未恢复）；cache正常初始化片段；`a008b654` entry payload适配；alloc/free适配。registry/info/header、classify和A20 flag为已验收合同，仅针对调用连接核，不重做全部image class或PNG算法。

## 结构、真实调用 ABI 与 owner

恢复伪代码不是原源码，word/pointer均4 B：

```c
struct Session {                  // 76 B，全清零
    Decoder *decoder;             // +00
    byte option04, option05, option06, option07;
    byte field08; byte pad09[3];
    const Descriptor *source;     // +0c
    byte source_class;            // +10
    byte rest11[15];
    Header header;                // +20，12 B；结果cf位于+21
    Pixel *decoded;               // +2c
    byte rest30[16];
    void *cache;                  // +40
    void *cache_entry;            // +44
    void *user_data;              // +48，PNG此路径未写入
};
struct Pixel {                    // 28 B；与只读ROM descriptor区分
    byte byte0,cf; uint16_t flags; // +00/+01/+02
    uint16_t w,h,stride,reserved;  // +04/+06/+08/+0a
    uint32_t data_size;           // +0c
    byte *data;                   // +10，绘制/通道转换用指针
    void *raw_allocation;         // +14，析构用原始分配指针
    HandlerTable *handlers;      // +18
};
```

真实 owner 片段中 `a00e5d2c` 从绘制参数 `s1+1c` 取 source，`d2e` 把 `a0=s0-7c`，`d32` 直接调用 `a019b168`。这个session占76 B，位于调用者栈，不是PNG callback自行malloc的session。`d36/d38` 只在返回恰1时到 `d74`；失败记录日志并到函数尾部，没有补加close。成功时 `d7c` 把同一session作a2交 `a018f9e8`，返回后 `d88/d8c` 以a0同一地址调close，随后离开此分支。另一路 `d92/d98` 也open同一栈地址，后续重复/铺排消费到 `d8c` 公共close；该几何循环不因此认证。

这是一个已证真实调用者的同步调用次序。callee `a018f9e8` 内部是否保存session/pixel或何时完成物理绘制没有本轮证据，不能据函数返回推物理LCD完成，也不能把所有其它调用者都称相同生命周期。

`a019b168` 首先 `(session,0x4c)` 清零，source为NULL回0；否则写+c，调用 `a00dd454(source)`，SB class到+10。cache对象来自word `62fc9698=G+11c`；其+8容量非零才设session+40并作cache查找 `a019d62e(cache,key)`。key栈记录至少包含class byte+8、source word+4；未写的key字节不自行补清零。cache命中时 `a008b654(entry)` 取得payload，把payload+c写session+2c，payload+10写session.decoder，entry写+44，返回1，跳过info/open和通道交换。cache命中不会复制header到session+20；原指令如此。

cache miss路径调用 `a0082c8c(session,session+20)`，返回decoder存+0；NULL回0。然后SW zero到session+4、SB zero到+8，再LW decoder+4，`a019b1fe a685 / b200 8297` 为 `a1=session; C.JALR a5`，a0仍是decoder。因此真实PNG open ABI为 `(Decoder*,Session*)`。回调返回存s2后 `b206 e312f5f8` 的BNE到 **b18a**，保留原回调值返回，并非把任意失败统一为0；只有若干显式无源/无decoder路径回0。

回调恰1且decoded非空时，通用open核decoded+14与+18非空，失败会进入原log/assert接口，之后仍能到后续指令；未擅自添加提前退出。session+8非零才经 `a0081cd2(pixel,NULL)` 做额外同步操作，正常清零PNG路径该byte仍0，跳过。

## class0 PNG：源借入、像素分配与发布

`a00eb7c8` LBU class，1进文件支；不等1到 `b918`，非0回0。class0到 `b91c..b924`，从source+10取ROM压缩data到s3，source+c取data_size到s1，直接进入共同decode。没有对source或ROM压缩data取所有权，也不临时复制该data。

```c
int png_open(Decoder *n, Session *d) {
    // class1进入另一路文件buffer；这里只展开正常class0。
    if (d->source_class != 0) return other_class_original_path;
    const byte *compressed=d->source->data;
    uint32_t compressed_size=d->source->data_size;
    Pixel *p=NULL;
    uint32_t width, height;
    int status = a019262e(&p,&width,&height,compressed,compressed_size);
    if (status != 0) {
        if (p) { destroy_pixel(p); p=NULL; }
    } else {
        uint32_t i=0;
        byte *base=p->data;         // 原程序此处直接读取p+10
        byte *base2=base+2;
        while (i != (uint32_t)(width*height)) {
            byte b2=base2[i<<2];
            byte b0=base[i<<2];
            base[i<<2]=b2;
            base2[i<<2]=b0;
            ++i;
        }
        p=load_saved_pixel();       // 原栈局部重载
    }
    // 共同段class1还须free compressed临时buffer；class0不free ROM。
    if (!p) { original_log(); return 0; }
    Pixel *q=a00829e4(d,p);
    if (!q) { destroy_pixel(p); return 0; }
    if (q!=p) destroy_pixel(p);
    d->decoded=q;
    if (d->option06 || cache_capacity()==0) return 1;
    entry=a0082980(n,&key,q,NULL);
    if (!entry) return 0;           // decoded已写，原路径不回滚/不补destroy
    d->cache_entry=entry;
    return 1;
}
```

重要原序：`b8b0` 只清out pixel的栈word；`b8b4` call；`b8b8` 先重载pixel，然后判断status。status非零且pixel非空才destroy并置NULL；status为0直接读pixel+10，不替原程序添加NULL门。共同段 `b8ca` **重读** class，仅class1 free临时compressed；然后检查pixel。通道交换循环不是额外分配，也没有改byte1/byte3：`b930 MUL` 为低32位width×height，`b938` 以相等为退出，index由 `b952` 递增；4个厂商indexed byte原编码见下文。

`a00829e4` 正常路径入口读取session+4，0跳 `a0082b80`；在那里session+5为0跳公共返回，返回原pixel指针。session刚清零且open分派又清+4 word，info已验收未写这些options，所以此PNG正常路径后处理是identity。可配置的stride重排/复制/其他cf变换存在于非零option路径，不能把它们从库中删除或称不存在；本轮只将其列为另一个路径的未恢复合同。identity路径上不会发生q!=p的旧对象销毁。

### 通用解压器的明确合同与分配片段

`a019262e(&Pixel*,&width,&height,const byte*,uint32_t)`，status 0由PNG视作成功，非零由外层清理out pixel。完整函数在历史provider边界为 `a019262e..a0194719` 共8428 B；本轮不声称恢复PNG chunk、inflate、滤波、颜色转换全集。

但为认证像素资源来源，重新核了两个真实输出分配点：`a01928f2..2944` 和 `a0192ac6..2af2` 都调用 `a0081d90(62fc9674,width,height,0x10,width<<2)`。后者把返回对象存到调用者out指针，再从对象+c读取data_size；前者也把对象写out并销毁先前临时对象。这些是真实分配/输出边，不能把通用解压简单写作“返回裸RGBA malloc”。另 `a0193bd6..3be6` 有临时pixel的析构/清局部。未核8428 B所有分支，故其全部错误后资源、准确产物尺寸与每个正常ROM PNG最终成功仍为合同前提，不从header认证推运行成功。

`a0081d90` 先申请28 B结构，正常保存handler表为 `62fc9674`。非零传入stride沿用；size由 `a0081c6a(width,height,cf,stride)` 计算合同给出。先取handler表+0，非空时调用它，已确立参数a0为此前size计算返回值、a1=cf；a2/a3未在间接调用前重装，本轮不擅自扩成完整四参分配API。返回raw存s8，NULL时free结构回NULL；成功写cf/width/height/stride、size、+14 raw与+18 handler表，再可选handler表+8以 `(raw,cf)` 得aligned data写+10。header word保留位/常量是 `(old&0xff00)|0x00300019`，故owned flag位0x10属于之后操作的真实门，不仅靠名字断言。

构造分配NULL的log/assert分支随后继续使用返回寄存器，非全部立即return；本轮描述正常分配成功路径，不“修复”原固件。底层handler表具体安装者/分配与free目标未完整连接，是可定位断边 `62fc9674+0/+4/+8`；比“raw已直接传free_adapter”更精确。

## close、cache 与所有权

```c
void session_close(Session *d) {
    Decoder *n=d->decoder;
    if (!n) return;
    if (n->close) n->close(n,d);  // 先callback，再重读global/cache字段
    if (load32(global_cache+8)!=0 && d->cache && d->cache_entry)
        a019d9f6(d->cache,d->cache_entry);
}
void png_close(Decoder *unused,Session *d) {
    if (d->option06==0 && load32(global_cache+8)!=0) return;
    destroy_pixel(d->decoded);
}
void destroy_pixel(Pixel *p) {
    // 省略原NULL/assert诊断，非额外防护。
    if ((p->flags & 0x10)==0) { original_log(); return; }
    HandlerTable *h=p->handlers;  // +18，原程序非空assert
    if (h->free_raw) h->free_raw(p->raw_allocation); // +4函数指针
    free_adapter(p);             // 此时才归还28B对象
}
```

session close `a00828e2` 读取session+0到a0，`28e6` LW decoder+c，`28ea/28ec` 传a1=session后间接call；没有把session当decoder，也没有对session本身free。close返回后 `28ee..2900` 重新读全局cache容量和session+40/+44。PNG close byte+6非零时不读capacity就直接destroy；为0时必须capacity为0才destroy。close不会清session+2c/+0/+44。session栈的销毁由owner返回完成，像素对象的归还由上述门决定。

在直接归还路径，raw归还callback先于pixel结构free。`a0081f26` 原件LHU pixel+2、ANDI0x10；非owned只log后返回，不free。handler table为空走原assert后续，不伪造NULL安全返回。正常free adapter `a008ab8a` 对NULL及sentinel `62fc95e0`早退，其他指针经backend `a002e14e`；通用allocator内部不展开。这证明了回收调用次序，不认证heap实际复用或底层handler实现。

cache路径正常全局初始化把 `a008abb0` 安装为payload清理callback（三个word表的第3槽），调用cache创建，capacity参数 `0xe1000`，结果写G+11c；缓存名指针也写cache+20。该字段单位与策略不从数值猜测。`a0082980` 调cache插入 `a019d914(cache,key)`，成功才 `a008b654(entry)` 取得payload：

```c
struct CachePayload {
    byte unknown00[4];
    void *source;             // +04；class1时复制字符串，否则借原source
    byte source_class;       // +08，backend key生产，wrapper据此决策
    byte pad09[3];
    Pixel *decoded;          // +0c
    Decoder *decoder;        // +10
    void *user_data;         // +14，PNG传NULL
};
```

payload+c先写decoded；class==1才 `(payload+4)` 经 `a008d8d2` 复制并回写；再写user_data+14、decoder+10。session保存entry，后续cache hit复用同一pixel。`a008abb0` 清理时从payload+c读pixel，其flags bit0x10为1才 `a0081f26`；之后重读payload+8，class1才free payload+4的source副本。class0 ROM descriptor/source不free。该callback不free payload/entry自身，entry由cache后端管理。

因此正常新session options均0且全局cache有效/容量非零时，open把像素对象交cache条目持有，PNG close故意跳过对象析构，通用close调用cache release接口。**`a019d9f6`后端是否只减引用、何时驱逐、容量如何计量、callback是否在本次release触发都未恢复**。真实清理callback的安装及其销毁内容已证，具体调度是精确断边；不能写“每次close立即释放PNG像素”，也不能由跳过free推永久泄漏或作缺陷判断。

若cache插入返回NULL，PNG此前已写decoded但返回0，通用open原样返回0，此实际caller不close。本轮仅忠实记录此失败分支，无异常实验、无行为修复、不作缺陷或可利用性判断。此结论也不等于证明正常ROM/分配成功条件下一定触发该支。

状态为 `调用者栈session清零 → cache命中借pixel，或miss选decoder并分配新pixel → class0通道交换/identity后处理 → publish decoded → 可选cache条目持有 → 同步消费调用 → close直接销毁或cache release → owner栈返回`。decoder属于global registry；source/data属于ROM借用；session是调用者栈；Pixel/其raw是独立分配；cache entry/payload由cache后端管理，class1的临时buffer/字符串不是本class0 ROM所有权。

## 厂商编码、来源与实际验证

| 位置/原字节 | 原字段与恢复 |
| --- | --- |
| `a00eb7f2 0b48f744` | diagnostic指针word查表，`th.lrw a6,a4,a5,2`；仅class1文件失败日志支 |
| `a00eb942 8bc5a684` | opcode0xb/f3=4/top5=16/rd11/base13/index10/shift2，unsigned byte读 `base2+(i<<2)` |
| `a00eb946 0b46a784` | 同family，rd12/base14/index10/shift2，读 `base+(i<<2)` |
| `a00eb94a 8b55a704` | opcode0xb/f3=5/top5=0/rd11/base14/index10/shift2，写byte到base+i*4 |
| `a00eb94e 0bd6a604` | rd12/base13/index10/shift2，写byte到base2+i*4 |

这是indexed读写，**不是带基址回写的postincrement**；index只由普通 `ADDI a0,1`变化。JSON保存本地只读 `ap01thead2.sinc` 的 `th.lrbu/th.srb/th.lrw` 规则，EA=base+(index<<shift)，unsigned8 load/store以及word load，无base回写。模型对应不是厂商文档或硬件运行认证；没有改分析模型。

来源候选沿用A21/A22的LVGL `lv_image_decoder.c`、`lv_lodepng.c` ROM路径及注册名 `LODEPNG`。准确LVGL/LodePNG版本、上游逐字比对/厂商修改认证仍未知；无外连取源码，没有任何“标准库已认证可排除”的新增项。通用解压器8428 B保留未恢复/未认证，像素分配适配、cache包装/回调继续恢复，不因名称像库代码而排除。

实际静态验证：`verify.py`通过21窗口、2364 B、794条指令、74项原编码/地址断言、5厂商word，未解指令0。核对了实际indirect open/close和raw-free ABI、严格1门、callback失败保留返回值、word/halfword/byte宽度、转换读写、清理排序和字段重读。检查报告链接及 `git diff --check`；不编译生产项目，不运行固件/解压器/渲染，也不对正常ROM内容作解压试跑。

事实是原调用/字段/门/分配和清理调用顺序；推断是在新建session选中此PNG且底层decode成功、对象/全局基础设施有效时，class0新像素对象会经过所述交换与identity后处理进入session/cache；未知包括每个ROM PNG是否实际成功执行、通用算法全集、handler安装目标、cache内部引用/驱逐时机和物理显示结果。回调注册存在本身不作执行成功证据。

一个后继闭包建议：新agent独立复核本10核心及必要短依赖，重点核缓存持有与直接close分流、对象与raw双层归还、cache miss与hit返回/字段差异、厂商indexed通道交换；之后才选择 `62fc9674` handler安装→raw allocation/free的小闭包，勿扩全heap或完整PNG解压。本轮不自行领取后继。
