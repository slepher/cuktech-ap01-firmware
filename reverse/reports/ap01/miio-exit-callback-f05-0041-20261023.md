# F05：退出后显示对象来源、DELETE 回调与 +2b8 断边

2026-10-23；分支 `codex/re-0041-f05`，基线 `3aba13a76a74185622521b110f7a10c50338455e`。本轮为功能恢复，未经过新 agent 独立技术复核。

**结论：`s0-314` 最初接收的是 `/dev/fb0` 对应的 LVGL 显示对象，`a0081554` 是显示对象删除路径。它不是已证实的 MiIO loop walker。** 构造时清零 `0x324` B，故 `obj+2b8` 初值为 NULL；本轮未定位其非 NULL 安装者，不能证明经过整个容器运行后该槽仍为 NULL，也不能给 `a00815f4` 指定非 NULL 真实目标。已经另外定位到正常安装并在删除时匹配的 **DELETE 事件 callback `a00800b4`**，其 userdata 是显示对象，清理显示后端 context/fd/资源。两套 callback 槽和参数不能混同。

在以下有证据闭包中未建立到 caller 栈 loop `s0-240`、共享 timer `62fc9428` 或 timer.data 的连接。该结论只表示未建立连接，不排除未展开 callee、事件重入、对象别名或其他时段的间接作用。F03/F04 的“实际 timer close 与退出后 pending 消费机会”断边没有因此关闭。

## 范围与证据

只静态读取原厂0041、已有保留证据和既有本地厂商指令模型，没有执行固件、连接设备/服务、运行历史回放、异常输入或修改ROM/生产代码/模型。没有打开、切换共享 REA session。已使用 REA 技能的原字节核验、证据区分和有界负搜索方法。

[verify.py](../../analysis/miio-exit-callback-f05-0041-20261023/verify.py) 直接读取 `D:/Documents/PlatformIO/Projects/cuktech-ap01-firmware/roms/0041/ap01-1.0.2_0041.bin`，按 `file_offset=VA-0x9ffff000` 取原字节。结果 [instruction-evidence.json](../../analysis/miio-exit-callback-f05-0041-20261023/instruction-evidence.json) 保存23个选择窗口、2130 B原字节/解码、101条指令/独立位域目标核对、来源字符串、两条厂商字与本地模型摘录、构造容器未知厂商字位置以及有界 SW 编码搜索结果。不是从F03/F04的派生汇编生成本轮指令。

入口保留来源为 `factory-test-0041-20261023/retained-initializer.json`，Evidence `ev_dc0e38b0f382799ea2a8e8ad7f21cefc5998b0767ecf38a58cfdebe8add167c3`，profile `bcefdee5092076e55636e077b45523e203f4b870ae7b7ab547945ed1b8162279`；其全部 raw_ranges 与原ROM逐字节匹配。它只作容器参数来源线索，未把反编译器的 `char *param_2` 当真实对象类型。

核心身份如下；大初始化函数只展开本问题需要的创建、发布、注册和后端连接片段，不宣称恢复其余显示/输入初始化。

| 身份 | 本轮恢复的合同 |
| --- | --- |
| `a005cc1e` caller | 配置、out槽、loop调用和返回后删除实参 |
| `a0084b96` 初始化容器片段 | 接收config/out，创建显示、payload及后端，注册DELETE，发布out |
| `a008aec0` | 从全局显示list取得新对象并链接，返回对象指针 |
| `a0081554` | 发DELETE、清显示资源、可选+2b8调用、归还payload/obj |
| `a007ffa0` | 把对象转为obj+2e8事件list后调用注册实现 |
| `a01b93b4` | 分配12 B事件descriptor、保存callback/filter/userdata并追加指针 |
| `a00814f4` | 建立栈event，先phase1，返回1才送phase0 |
| `a008acfa` | 按filter/phase选择descriptor，安装event.userdata并间接调用 |
| `a00800b4` | 正常DELETE callback，显示后端资源清理 |
| `a007fe32` | 取obj+2e0；NULL对象才取默认显示再访问 |

短依赖 `a0080d8e` 是清零wrapper；`a00819d0→a0081978` 是58 B payload清零/default；`a008ab8a` 是已有归还wrapper；显示其他资源callee、event数组增长/维护、底层fd最终归还保留精确接口，不扩全LVGL/文件系统。

## 对象来源与 +2b8 安装的实际范围

caller `a005cc9c..ccc6` 先清12 B配置，再写两条ROM路径到配置+0/+4：

- `a01c3af4` 为 `/dev/fb0`，写到 `s0-308`；
- `a01c3b00` 为 `/dev/input0`，写到 `s0-304`；
- `a005ccba` 以a1=`s0-314`、`ccbe`以a0=`s0-308`，`ccc6`直接调用 `a0084b96`。

`a0084bb4`保存config，`4bba`保存out到s7；`4d9a..4da6`以 `62fc9580` 为list参数调用 `a008aec0` 并把返回值存s1。`4de8/4dec`以a1=`0x324`调用清零wrapper，a0仍是新对象。wrapper `a0080d96/98/9a`将长度转a2、a1置0后调用 `a0024906`。因此字节区 `[obj,obj+324)` 包含 `+2b4/+2b8`，两槽初值均为0。

`4e26/4e2a`取得58 B payload，`4e2e` word写 `obj+2b0`；`4e6e`以返回payload调用 `a00819d0`，它清零58 B并经 `a0081978` 设置payload+38=`0xff`、+3c byte=0。之后 `4e72..4e7e` 条件读取 `obj+2b4`，若非NULL以 `(obj,payload)` 调用。这个构造 callback 槽与删除槽+2b8也不能合并。

`a00873ea` word写 `s1→[s7]`，即最初的 `s0-314`。后续还有输入设备初始化，不能只凭发布out将其之前的所有初始化路径认证为唯一来源。正常已发布显示分支足以建立本轮对象身份；未扩大为全初始化成功条件恢复。

caller在 `a005cec6` 以a0=`s0-240`、a1=`s0-314`调用 `a005a736`；`ceca` **重新读** word(`s0-314`)后调用 `a0081554`。F04已确认两直接参数身份不同。本轮不能把“初始out是显示”提升为对容器整个运行期间别名修改的完备排除。

为定位+2b8直接安装，扫描原ROM全部半字对齐位置的普通RV32 `SW` opcode/funct3/S立即数字段，匹配offset=`0x2b8`仅有：

| PC | 原字 | 解码 | 范围含义 |
| --- | --- | --- | --- |
| `a00efd3e` | `23acab2a` | `sw a0,0x2b8(s7)` | 另一上下文分配结果写入，不建立本显示writer |
| `a00eff32` | `23ac0b2a` | `sw zero,0x2b8(s7)` | 对应另一上下文清槽 |
| `a014e264` | `232c812a` | `sw s0,0x2b8(sp)` | 栈保存 |

该检索不是完整指针分析或指令/数据分类；不能覆盖先加基址再低偏移store、indexed厂商store、memcpy等批量写或任意callee别名写。构造大容器线性扫描的21条Capstone未知厂商字位置一并保留，没有用普通指令负搜索代替它们的语义。**+2b8唯一有依据的初始候选为NULL；非NULL候选地址集仍未建立。** 不把没有直接安装证据写成回调不存在或实际一定跳过15f4。

## 真正安装的 DELETE callback 与资源归还

`a0086cc6`将后端指针word写 `obj+2e0`。`6cb0/6cce`组合a1=`a00800b4`，`6cca`置a2=`0x29`，`6cb4`置a3=obj，`6cd2`置a0=obj，`6cd4`调用 `a007ffa0`。后者在 `a007ffec`将a0增加`0x2e8`，`fff0/fff4`直接目标为 `a01b93b4`，**不是**以offset2b8安装函数指针。

`a01b93b4`分配12 B descriptor；`9432` word写callback@0，`9438`写filter@8，`943a`写userdata@4；正常分支将descriptor指针追加到list数组，`9500/9502`增加word count@4。`94f2`原字`0b15f620`按既有本地模型为 `th.mula a0,a2,a5`，即在数组首指针加 `element_size*count` 后复制descriptor指针。数组首次分配、容量增长/重入维护只保留该helper合同，未认证上游来源版本。

`a0081554`保存obj到s1，先以a1=29、a2=0调用 `a00814f4`。该函数创建28 B栈event：obj同时写event+0/+4，code写+8，参数写+10；它没有把参数0当userdata。先以a2=1调用 `a008acfa(obj+2e8,event,1)`，只有返回1才以a2=0再送同一event。

dispatcher正常取descriptor，从+8读取filter：bit16的条目跳过；提取bit15比较phase；低15位为0表示通配，否则与event+8的code比较。`a008ad78`原字 `8bb6f73c`，位域核为rd=a3、rs1=a5、lsb=15、msb=15，既有本地 `th.extu` 模型得到 `(filter>>15)&1`。因此filter=29正常匹配phase0，不能把phase1先行误写成callback调用两次。flags/删除/停止正常分支保留原返回判断，没有分析重入或异常输入。

`ad8e`先从descriptor+4取userdata，`ad92`写event+c，再`ad96`**重读**descriptor+0的callback；`ad90/98`以a0=栈event间接调用。该条目恢复出的目标就是 `a00800b4`，a0不是显示对象。callback不消费返回值。

`a00800b4`的已核顺序：

1. `00c0`读event+c得到注册userdata=obj；通过 `a007fe32(obj)`读obj+2e0取得backend。NULL backend跳到日志/返回。
2. 正常非NULL obj先word清obj+2e0，再清obj+2c。obj为NULL时先读默认显示62fc9590，得到非NULL才清这两个字段。
3. word读backend+0作为有符号fd，非负才调用 `a0026888(fd)`，返回后无论返回值如何均word写-1到backend+0。此callee按fd归还wrapper合同；未恢复其底层file最终close，不把“调用归还”提升为已观测硬件释放成功。
4. word读backend+34，非NULL调用 `a002e14e` 归还，然后word清backend+34。
5. `00fc`清槽之后以backend调用 `a008ab8a`，随后日志并返回。它未直接读取timer.data或把callback参数改成MiIO loop。

后端fd的局部生产连接为 `a0086d26..6d40`：先通过同一个getter读backend，已有非负fd先交同一归还wrapper；以pathname、flags=3调用 `a003f4f6`（既有D03 open合同），word写返回到backend+0。backend+34的生产/完整帧缓冲初始化不在本轮，故只称资源指针，不硬译成mmap或证明物理显存来源。也不把初始化容器里另一个0x368 B对象错当此backend。

## 删除尾部、布局与所有权

DELETE事件返回后，`a0081554`才继续清事件list（`a008b7f0(obj+2e8)`），处理全局输入对象关联，清理+2c0/+2c4/+2cc、+2bc数组中的对象及+26c列表，调用 `a0089d02(62fc9580,obj)`从显示list移除，条件删除obj+308调度对象。上述一般对象/列表/timer内部不扩展，特别是不能把obj+308等同 `62fc9428`。

然后才到 `15e8`读取obj+2b8；非NULL则a0=obj、a1=word(obj+2b0)，`15f4`间接call。返回值没有消费，`15f6`**重新读**obj+2b0，经 `a008ab8a`归还；再归还obj。最后按入口保存的两个全局显示对象引用更新62fc957c+14/+10，保持原先free后全局更新顺序，不擅自重排。

| 对象 | 最小已用布局（hex偏移） | 所有权 |
| --- | --- | --- |
| caller | out word@s0-314；loop区域@s0-240 | 两个不同的直接参数；out在返回时重读 |
| 显示obj | payload word@2b0；init_cb word@2b4；optional delete_cb word@2b8；backend word@2e0；event list@2e8；调度对象word@308 | 显示list持有；删除路径最终归还payload和obj |
| event descriptor，12 B | cb word@0；userdata word@4；filter word@8 | event list保存descriptor指针 |
| 栈event，28 B | obj word@0/+4；code word@8；userdata word@c；param word@10；flags byte@18 | sender栈上同步借用；dispatcher每次callback前安装userdata |
| backend | fd signed word@0；资源指针word@34 | obj+2e0持有；DELETE callback清关联后归还资源及backend |
| payload，58 B | default word@38=ff、byte@3c=0；其余字段本轮不定名 | 删除尾部在可选callback返回后重读归还 |

```c
// 分析伪代码，不是原源码；未知效果不能用省略号证明不存在。
entry() {
    config = { rom_string("/dev/fb0"), rom_string("/dev/input0"), 0 };
    init_display_input(&config, &out);       // a0084b96
    // 初始化其他业务……
    run_container(&stack_loop, &out);       // a005a736
    delete_display(out);                   // 这里重新读取out
}
create_display_fragments() {
    obj = list_allocate(&display_list);
    zero(obj, 0x324);                      // +2b4/+2b8 初始NULL
    obj->payload = allocate(0x58);
    initialize_payload(obj->payload);
    if (obj->init_cb) obj->init_cb(obj, obj->payload);
    // 后端/显示设置……
    obj->backend = backend;
    add_event(obj + 0x2e8, a00800b4, 0x29, obj);
    *out = obj;
}
delete_backend_event(event) {
    obj = event->userdata;                // word+c，不是event+4
    backend = get_backend(obj);           // NULL obj才取默认显示
    if (backend) {
        if (!obj) obj = default_display;
        if (obj) { obj->backend = NULL; obj->field_2c = NULL; }
        fd = backend->fd;
        if (fd >= 0) { release_fd(fd); backend->fd = -1; }
        if (backend->resource_34) {
            free_a002e14e(backend->resource_34);
            backend->resource_34 = NULL;
        }
        release_a008ab8a(backend);
    }
    log();
}
delete_display(obj) {
    send_event(obj, 0x29, NULL);           // phase1返回1后才phase0
    clear_event_list(obj + 0x2e8);
    // 已定位的显示子对象/list/调度资源清理，内部效果保留边界。
    cb = obj->optional_delete_cb;
    if (cb) cb(obj, obj->payload);        // +2b8；非NULL真实目标尚未建立
    release_a008ab8a(obj->payload);        // 原程序重读
    release_a008ab8a(obj);
    update_saved_global_display_refs();
}
```

## 验证、事实/推断/未知与精确结束边

实际执行本轮脚本得到：**PASS 101 instruction/edge checks；23 windows；2130 bytes；3 SW encoding matches；21 constructor custom words retained。** Capstone 5.0.7处理普通RV32/RVC；JAL及AUIPC/JALR目标另外按位域算；厂商两字独立核原字及寄存器/位域，语义使用只读既有本地模型，不冒称已认证厂商ISA手册。完整大构造函数的未知厂商字未被当成无副作用。未编译项目、执行目标或回放模型。提交前还核独占路径及 `git diff --check`。

事实包括配置字符串地址、对象/字段写入、清零范围、out发布/返回重读、descriptor安装、间接ABI、资源调用及重读/归还顺序。显示删除、DELETE、backend/fd等业务命名是由代码连接和ROM源码路径共同支持的恢复推断。ROM包含 `.../src/drivers/nuttx/lv_nuttx_entry.c` 与 `.../src/display/lv_display.c` 字符串，足以帮助定位子系统，**不足以认证LVGL具体版本或未修改源码**；没有据“普通开源库”排除此厂商初始化适配或callback。

尚未建立：非NULL obj+2b8安装者/目标；进入15f4时槽的实际值；容器整个期间out和obj字段所有别名写；底层fd实际最终close及硬件交付；其余显示资源callee完整效果；DELETE事件重入/其他订阅者的间接效果。因此本轮实际完成的是“显示对象来源→真实已装DELETE callback→后端归还→显示尾部释放”的有界正常闭包，以及 **+2b8从来源未知收窄到初始NULL、非NULL安装仍未定位** 的准确断边。没有把另一套事件callback伪装成15f4的目标，也没有据显示命名宣布MiIO退出清理已经完成。

本轮到此结束，不接管全显示栈或全退出。一个后继闭包建议：新agent先独立复核本轮out身份、DELETE descriptor匹配/栈event ABI、后端归还次序及+2b8负搜索边界；若继续追15f4，只应围绕本显示对象的别名写/批量写及容器运行期间保存引用展开，不能再次预命名walker或扫描全部timer。对9428实际close及pending消费的后继选择仍应从F04独立断边出发。
