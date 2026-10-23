# D03：UART 写对象取得、具体 write 与缓冲寿命

2026-10-23；基线 `1a8062381982cdd8ee49dd6bfac9740056133019`，分支 `codex/re-0041-d03`。**恢复到正常 UART write 的字节复制闭包，待独立技术复核。** `62fc91b0` 的 fd 来自打开 `/dev/ttyS1`；启动注册把该名字接到设备 `62fc36d0`，inode 操作表 `a066d7c8` 的 write 为 `a002c206`。取得 fd 时增加文件对象的 32 位引用计数，write 后归还该引用。正常任务路径同步逐 byte 把传入 frame 的内容写入设备 TX 环形缓冲，不把 frame 指针存入设备或异步请求。返回的是本次接受的源字节数；不表示硬件发送完成。

应用 `reverse-engineer-anything` skill，直接核原 ROM 并复用已有来源身份；没有打开共享 REA target/可写数据库。只静态分析，没有执行固件、历史回放、外连、超时/异常输入/漏洞验证，没有修改 ROM、生产代码、构建配置或分析器模型。D01/D02 的构帧、队列、parser 只保留已验收合同。

## 范围、函数与来源

核心为下表 12 个函数身份，另核短 lower 回调、context 谓词和必要创建/配置片段。`a005a736` 大初始化器、`a003eb14` open 内部和 `a01b5b74` 分配器只恢复需要的切片，不声称其整函数闭合。新函数边界根据入口调用、返回及邻接指令推定，未伪造 REA 函数 Evidence ID。

| 地址 | ABI、返回和本轮职责 |
| --- | --- |
| `a0025904..595b` | `(fd:int32,out:File**) -> 0/负数`；当前任务 group 中 fd 范围检查、取得对象。 |
| `a00258e4..5903` | `(FileTable*,fd:int32) -> File*`；有符号除/余6，传给下一层。 |
| `a00258a0..58e3` | `(table,page_index,slot_index,optional_mark*) -> File*或NULL`；页指针、24B slot、临界区引用取得。 |
| `a0025874..589f` | `(File*,buffer*,count) -> signed result`；D02 已验收三参数间接 ABI，针对核。 |
| `a0027e94..7eed` | `(fd,buffer*,count) -> signed result或-1并写errno`；D02 已验收 wrapper，针对核归还串接。 |
| `a0027e54..7e93` | `(File*) -> 0或最终close结果`；临界区计数减1，零时转 `a0027d9a`。 |
| `a01b5a7e..5b0d` | `(pathname*,UartDev*) -> 注册返回`；必要 UART 初始化、安装统一 ops 与设备私有指针。 |
| `a01b5a12..5a7d` | `(pathname*,ops*,private*) -> 0/负数`；名字保留器成功后写 inode 的 ops/private/type。 |
| `a002c206..c3a5` | `(File*,src*,n) -> 源字节接受数/负数`；具体 UART write，任务/直接路径及输出转换。 |
| `a002c140..c205` | `(dev*,byte,may_wait) -> 0/负数`；复制 byte 到 TX ring、发布 halfword head；满时可唤醒/等待。 |
| `a002ad82..addd` | `(dev*,src*,n)`；直接发送路径，轮询 lower ready 后按批量或单 byte 操作发送；caller不使用其返回。 |
| `a0019876..98bb` | `(dev*,byte)`；lower 单字节发送适配，按 private 首 byte 选择 RAM 调用或另一表中的1字节调用。 |

另外完整核 `a001972c..9739`（ready 恒返1）、`a0027830..786b`（context 谓词）；`a0019810..9875` 只作 txint 回调合同。零引用下 `a0027d9a..7dbf` 调 `a0027ca4(File*)`，成功后清 inode，后者内部退出/通知/释放不扩解。RTOS mutex/semaphore、errno、名字保留器和 allocator 均未取得可核实版本来源，只作明确外部合同，**没有因疑似 NuttX 而排除其厂商适配**。

[原指令证据](../../analysis/uart-write-object-d03-0041-20261023/instruction-evidence.json)含22窗口782条指令、原字节和文件偏移，及操作表/设备初值。ROM只读来源为主仓库 `roms/0041/ap01-1.0.2_0041.bin`，VA→file offset 为 `VA−9ffff000`。RAM初值沿用已复核启动复制合同 `ROM a00027d4 → RAM 62fc2cc0`，不是本轮观察到的设备运行状态。

初始化器来源沿用 `reverse/analysis/factory-test-0041-20261023/retained-initializer.json`：`a005a736`，Evidence `ev_dc0e38b0f382799ea2a8e8ad7f21cefc5998b0767ecf38a58cfdebe8add167c3`，profile `bcefdee5092076e55636e077b45523e203f4b870ae7b7ab547945ed1b8162279`。原 fd refs 来自 `evidence/rea-0041-20261017/evidence/whole-rom-uart-xrefs-20261023-004.json`：`ev_cbc9c78ecaf5c5902888e222f533a62e08edb1f51f28493d7758523d0b0fd7ec`，只作为定位线索，关键写者本轮核原字节。

## fd、操作表和必要安装片段

启动 `a00296bc..96c8` 传 `(a0=a01bc32c="/dev/ttyS1",a1=gp+0x210)`，AUIPC/JALR 原编码目标是 `a01b5a7e`；沿用启动 `gp=62fc34c0`，设备即 `62fc36d0`。不是由 fd 数值猜设备，也没有把 `/dev/console` 与它合并：相邻注册明确还使用 `gp+0x138` 和 `gp+0x310`。

`a01b5a7e` 清 dev+8；dev+2 非0时另清dev+1、flags+14 |=9、+10=5、+c |=0x100；随后依次初始化 dev+40/+5c/+30 及 dev+18/+24 的同步对象，置 +aa=0、+a9=1。`a01b5af6..5afe` 传 `(pathname,a066d7c8,dev)` 调 `a01b5a12`。后者调用名字保留器 `a01b5908(path,&inode)`，成功才把 ops 写 inode+10、private 写 inode+18，并以 halfword 更新 inode+e 的低四位为1；保留其他位。名字锁获取/释放的内部算法未展开，不能用名字字符串取代这个实际安装证据。

`a066d7c8` 表前四项原 word 是 `{a002ba6c,a002c678,a002c792,a002c206}`；write槽为+0xc。设备 RAM 初值来自 `ROM a00031e4`：dev+a0=`a01bcb18`、dev+a4=`62fc36b4`、TX ring 数据地址 dev+58=`62fc78a8`，容量 halfword dev+54=0x400、head/tail初值0。lower表 `a01bcb18` 中 +30=`a0019876`、+34=`a0019810`、+38=`a001972c`、+2c=`a001a70a`、+48=0。这些初值和注册链支持正常安装目标，未证明全 ROM 没有运行中换表/改指针。

应用初始化 `a005ab10..ab24` 以同一个 `/dev/ttyS1` 和 flags=0x43 调 `a003f4f6`，保存返回于ctx+4及s5，正值才走 `a005b214`：先清 `62fc91b0` 起0x6c B，再于 `a005b232` 将s5写入该fd槽。之后按原顺序执行请求0x101、属性参数0x1002 helper、请求0x102；失败记录后仍继续。这里只为确认 fd身份/配置串接，不把 helper参数0x1002硬译成实际波特率，也不展开整个属性驱动。

open wrapper `a003f4f6` 将pathname/flags交 `a003eb14`；后者已核切片 `a003eb4e..eb6e` 把路径解析产生的 inode、flags/position/private和group文件表交 `a01b5b74`。文件安装切片 `a01b5bfc..5c08` 写 file+10、flags+0、position+8、inode+c、refs+4=1；返回 fd由page*6+slot构成。完整 pathname查找/名字别名解析不在本轮范围，因此“正常注册名→正常open到同inode”是有安装和同名调用支持的关联推断，不是运行时 inode身份观测；没有声称唯一可能设备或消除所有动态替换。

## 文件对象、取得和归还

以下是分析布局，不是原始源码类型名：

```c
struct File {                    // stride 0x18
    uint32_t flags;              // +0，write用bit1；UART用bit6决定可等待
    int32_t refs;                // +4
    uint32_t position;           // +8，本闭包不解释其更新
    Inode *inode;               // +c
    void *private_data;          // +10
    uint32_t unknown14;
};
// current_task = word[62fc6c18]；group=word[current_task+8]
// table=group+0x5c；u8 page_count@0，File **pages@4；每页6个File。
// Inode: u16 type_bits@+e；ops*@+10；UART private dev*@+18。
```

取得路径保留先清out、宽度与失败码：

```c
int acquire(int32_t fd, File **out) {               // a0025904
    *out = NULL;
    group = load32(load32(0x62fc6c18) + 8);
    if (!group) return -11;
    if (fd < 0 || fd >= load_u8(group+0x5c)*6) return -9;
    *out = lookup_ref(group+0x5c, fd/6, fd%6, NULL);
    return *out ? 0 : -9;
}
File *lookup_ref(table, page, slot, uint8_t *mark) { // a00258a0
    saved = csr_clear_mstatus(0x8);
    f = load32(load32(table+4) + 4*page) + 24*slot;
    if (load32(f+0xc) != 0) {
        if (load32(f+4) == 0) f = NULL;
        else store32(f+4, load32(f+4)+1);
    } else if (mark && load32(f+4) == 0) {
        store32(f+4, 2); store_u8(mark, 1);
    } else f = NULL;
    csr_write_mstatus(saved);
    return f;
}
int release(File *f) {                             // a0027e54
    // NULL参数另有assert边，正常调用者传取得的对象。
    saved = csr_clear_mstatus(0x8);
    refs = load32(f+4)-1; store32(f+4, refs);
    csr_write_mstatus(saved);
    return refs != 0 ? 0 : close_final(f);          // a0027d9a
}
```

`a00258ae:0bc5b744` 是 `th.lrw a0,a5,a1,2`；`58b4:0b15f620` 是 `th.mula a0,a2,a5`，且此前a5=0x18。它们落实“pages[page]+slot*24”，不能将它误记为单层 fd数组。optional mark 分支不是实际 acquire调用所走路径（a3在`58f2`置0），保留它只为不把helper语义改写。

计数增加和减少各自仅在清 mstatus mask0x8 到恢复旧mstatus之间。**write调用期间不持有这个临界区，也没有证据证明它是跨核mutex或整个fd寿命锁。** 对仍保留基础引用的打开对象，一次正常write的局部变化为1→2→1；这只是该前提下的视图，未排除其他引用/关闭者。

D02 wrapper合同保持：取得成功后 `dispatch(f,buf,n)`，在归还前保存该结果，归还后仍返回保存值；release结果不覆盖write结果。取得失败不归还未取得的对象。NULL buf先走-22；dispatch的flags bit1不满足为-13，inode/ops/write缺失为-9。负结果转成errno正值和返回-1，非负结果原样上交。没有为这些路径作异常实验。

## 具体 UART write、同步消费与返回语义

`a002c222/228` 从 `File.inode+18` 取得dev；入口只将buf保存在s6、n保存在s3，指针在函数栈/寄存器内使用。正常任务路径的核心伪代码：

```c
uart_write(file, src, n) {
    dev = file->inode->private;
    if (load32(0x62fc6034) != 0 || context_predicate() != 0)
        goto direct_path;
    r = lock(dev+0x40); if (r < 0) return r;
    lower(dev+0xa0)->txint(dev, 0);
    may_wait = ((load32(file+0) ^ 0x40) >> 6) & 1; // 原字抽bit6
    left = n; end = src+n;
    while (left != 0) {
        b = load_u8(end-left);
        flags = load32(dev+0x10);                 // 每次重读
        if ((flags & 1) && b == 13 && (flags & 8)) b = 10;
        if ((flags & 1) && b == 10 && (flags & 0x24)) {
            r = enqueue_byte(dev,13,may_wait);
            if (r < 0) goto finish;
        }
        r = enqueue_byte(dev,b,may_wait);
        if (r < 0) goto finish;
        left--;
    }
    r = n;
finish:
    if (left < n) r = n-left;
    if (sign16(load_u16(dev+0x50)) != sign16(load_u16(dev+0x52))) {
        if (lower->slot_2c) lower->slot_2c(dev);
        lower->txint(dev,1);
    }
    unlock(dev+0x40);
    return r;
}
```

这保留源字节计数、输出转换、必要的call后读取和失败/解锁顺序；`r`不是输出物理byte计数。函数在非负完成与部分接受处可返回n或n-left，发生首个复制失败时保留负结果；包装层再转errno。没有把下层通知调用返回解释成发送成功。

`enqueue_byte` 的顺序是：以 `sign16(load_u16(head))+1` 形成next，与 `load_i16(capacity)` 比较后必要归0；反复重读tail并比较next。可写时重读head和ring pointer，将传入byte写到 `ring[sign16(head)]`，最后 halfword 发布next到head（`a002c192` byte store，`c196` halfword head store）。byte先于head；没有传递src指针。ring已满时，不可等待返回-11；可等待路径进入mask0x8临界区重查，若仍满，必要调用+2c回调、txint(dev,1)、等待dev+18，随后txint(dev,0)并恢复mstatus。等待返回非负则重新读tail，负则返回-4。只恢复原分支，没有做满环/中断/调度实验或保证等待一定结束。

因此正常返回r>0时，这r个源字节已在本次调用内读取，内容已复制到设备自身ring；没有证据要求frame持续借给DMA。仍未接受的源后缀由上层保留并在下次write传入，D02的cursor推进正好消费返回r。`+2c=a001a70a` 可能启动后续设备传输，本轮仅核其ABI输入dev，没有把它展开为DMA全流程或证明物理交付。

另一 `direct_path` 先清mask0x8临界区；dev.flags bit0未开时直接发原字节跨度；开启时先遍历源byte、按bit8把CR变成ROM单byte LF、按0x24在LF前插ROM单byte CR，按原顺序调用 `a002ad82`，最后恢复mstatus并返回n。原码对此路径不使用direct helper返回值，不能重建成按硬件实际返回值累加。

`a002ad82` 原样有ready循环、+48批量callback与+30单byte fallback。该设备lower初始表+48=0、+38=`a001972c`恒返1，所以正常初始安装下走单byte fallback：`a002add2` 在调用前读byte并将src前进1，传 `(dev,byte)` 给 `a0019876`，剩余计数减1；没有把frame指针传给lower发送。lower中private首byte<=1的分支以硬件对象和scalar byte调用 `62fc22ae`（AUIPC/JALR原目标），另一分支以**本函数栈上4B局部值地址**和count1调用相对表目标。后者局部地址的同步消费合同未认证；它不是frame原地址，不据此认证所有型号的lower驱动。初始 `/dev/ttyS1` private `62fc36b4` 首byte为1，支持第一分支，但未完整恢复private构造后的所有写者或把初值当运行时事实。

## 验证、事实/推断/未知及后继

实际执行 [verify_static.py](../../analysis/uart-write-object-d03-0041-20261023/verify_static.py)通过：**22窗口、782指令、31项精确操作数、15条原编码直接边（含3组AUIPC/JALR）、17条厂商字、3个初始化区域**。脚本逐条由原半字前缀推进2/4B边界，标准RV32+C由Capstone解码，厂商字单独拆opcode/寄存器/funct3/high/shift并对照只读既有 `ap01thead2.sinc`；证据保留具体model行和构造。所用 `th.lrw/th.mula/th.lrbu/th.srb/th.ext/th.extu/th.lbuia` 均核原字。特别是 `a002c30a:8bba6a18` 抽bit6，`c192:8b59f700` 单byte store，`add2:8bc51498` post-increment byte load；不让Capstone猜未知指令，不修改模型。模型一致性不等于新增外部ISA文档认证。

另实际用 [scan.py](../../analysis/uart-write-object-d03-0041-20261023/scan.py)对 ROM 原字扫描 direct J、短窗口LUI/use候选和word引用，定位同名字符串注册/应用打开及lower表初值；逐条人工核落点后才纳入报告。扫描覆盖偶地址直接J及最多40B LUI后使用，不包含通用寄存器传播/所有间接别名，**不是穷尽的全ROM交叉引用**。无共享target切换、无固件执行或历史回放。

事实是字节、计数加减、mask0x8临界区、操作表安装、正常write调用参数和ring byte复制/halfword发布。File/Inode/UartDev、acquire/release/lock等名称是根据这些字段/调用关系形成的分析命名。正常tty注册和应用同名open的连接、打开基础引用1→2→1、此ring是TX所有权域，是有具体读写支持的推断；没有来源版本认证，不将通用文件层或UART适配直接归为未经修改的某一NuttX版本。

明确限制：完整path查找和运行中替换/全部aliases未核；零引用后 `a0027ca4` 的最终close/唤醒和inode释放未闭合；两个同步原语的内部算法/线程调度不保证；`a001a70a` 对设备ring的后续消费及DMA完成/唤醒未恢复；`62fc22ae` 及另一相对表callee内部硬件行为未核；仅在已述正常安装路径确认frame同步被读取/复制或按值传送，不宣称所有可能lower表/所有UART型号合同；硬件发出、对端接受、最终销毁仍未知。没有把恢复程度扩大到整个UART驱动。

建议后继一个闭包：以 `a001a70a(dev)` 对dev+50/+52/+58的传输启动→正常完成回调→tail推进/等待者通知为入口，恢复设备ring的消费与可写唤醒；保持本轮fd引用与frame同步复制合同，不扩完整DMA或全UART驱动。D03首先需要新的独立agent技术复核，特别核路径安装关联与ring/source所有权的条件。
