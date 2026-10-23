# D04：UART fd、write 与同步缓冲合同独立复核

2026-10-23；基线 `d07ed94a04f0a0b7c70354aa40b26051da5ab3e8`；分支 `codex/re-0041-d04`。**有一处 helper 可选分支伪代码纠正后，限定接受 D03 的正常 fd→具体 write→同步缓冲所有权闭包。** 纠正仅影响 `a00258a0` 的 optional_mark 非 NULL 分支；实际 `a00258e4` 在调用前明确令 a3=0，正常 write 取得对象的结论不变。D03 原文未改。

应用 `reverse-engineer-anything` skill。直接从主仓库原 ROM 独立取字节，使用隔离的只读静态解码；没有打开或切换共享 REA target，没有使用可写数据库。未执行固件、连接设备/外部服务、历史回放、异常输入/超时/漏洞验证、项目编译；未改 ROM、生产代码、配置或分析器模型。D02 帧、队列、parser 是已验收合同，只针对核 write 返回连接。

## 问题、范围与裁定

问题是 `/dev/ttyS1` 的注册安装怎样支持 fd 槽 `62fc91b0` 到 `a002c206`，对象引用何时增减，frame 是否被异步借用，以及返回值代表什么。结论：注册链与同名 open 支持正常路径关联；条件是成功解析到该注册 inode，且安装表和 private 保持所核配置。正常任务 write 同步读取源 byte 并复制到设备 ring，随后归还局部文件引用；返回接受的源字节数，不认证硬件完成。完整路径解析和运行时替换约束仍未知。

核心按 D03 的 12 函数：`a0025904` acquire、`a00258e4` fd 除/余、`a00258a0` 页式取引用、`a0025874` dispatch、`a0027e94` wrapper、`a0027e54` release、`a01b5a7e` UART 注册、`a01b5a12` inode 安装、`a002c206` write、`a002c140` ring byte 复制、`a002ad82` direct send、`a0019876` lower 适配。另核 ready `a001972c`、txint `a0019810`、context `a0027830`，以及注册 caller、应用 open/config、文件安装和最终 close 的必要切片。没有把大初始化器、allocator、path resolver 或整个 UART 驱动声称为本轮完整恢复。

| D03 命题 | 裁定及原指令依据 |
| --- | --- |
| 注册名、设备、ops/write 关系 | 接受，保留条件。`a00296bc/c0` 传 gp+210 和 a01bc32c；`96c4/c8` 原 AUIPC/JALR 到 a01b5a7e。以既有 gp=62fc34c0 得设备62fc36d0。`a01b5af6..5afe` 传 dev、pathname、a066d7c8；安装成功后 `5a4a/4c` 写 inode+10/+18，`5a54` halfword 发布低四位type=1。表+0xc原word为a002c206。 |
| 应用 fd 来源与槽安装 | 接受。`a005ab14` flags=43，`ab18`同名路径，`ab1c`调用open；`ab20/24`保存返回，`ab2e` signed >0 到 b214；清槽区后 `b232` word 写s5到62fc91b0。请求101→属性参数1002→请求102及各失败记录顺序吻合。不是运行时 inode 同一性观测。 |
| 页式24B对象、6项/页、取得错误码 | 接受。`a00258e6/58f4` signed rem/div6；`58ae`读 pages[page]，`58b4`加slot×24。`5904`先清out；group为空-11，fd门及无有效slot为-9；`591c` page_count是u8。 |
| helper optional_mark 伪代码 | **纠正**。`58ce` a3为空去58e0返回NULL；a3非空才到58d0读refs。`58d2 c.bnez a5,-0x12` 实际到58c0：refs非零时递增并返回slot，即使该分支起始inode为空。D03将这个分支误写为NULL。下节伪代码替代D03的同一helper视图。 |
| 引用临界区与write寿命 | 接受。`58a8..58c4`与`7e72..7e7c`分别清mask8、读/改32位refs、恢复旧mstatus。写调用位于两次局部临界区之间。`7e84`零引用才到final close；不能称全write持引用锁、跨核mutex或最终析构已闭合。 |
| dispatch ABI、归还与errno | 接受并针对核D02。object+0xc→inode+10→ops+0xc，`5890 c.jalr a4`前a0/a1/a2仍为file/src/n。`7ec6`保存write返回至s1，`7ec8/7ecc`归还同一局部file；`7ee6`返回s1。负结果经取errno、写正值、返回-1，release返回不覆盖write。 |
| 正常write源指针和ring复制 | 接受。`c224/226`保存在s6/s3，`c228`由inode+18取dev。`c324`按byte读源，`c33e/c360`只把dev/scalar byte/may_wait传enqueue。`c192`单byte写ring，`c196` halfword 发布head。没有把frame地址安装到对象、ring描述符或请求。 |
| head/tail、等待和锁范围 | 接受。容量`c15c`是signed halfword；head/tail读halfword再sign16，next绕回。满环不可等返回-11；可等分支mask8下重查，通知+2c、txint1、wait(dev+18)、txint0，恢复mstatus，负wait转-4。正常任务dev+40锁覆盖复制和尾通知，不等同fd引用临界区。 |
| 输出转换和源接受数 | 接受。flags+10逐源byte读；bit0启用时CR配mask8转LF，再按mask24判定LF前插CR。成功后才`c348`减left；`c36a`unsigned比较left<n才以`c36e`覆盖为n-left。第一个源byte未完成可保留负结果；已复制的插入CR不单独计源接受数。 |
| direct路径与lower按值发送 | 接受，限初始安装表。caller在恢复mstatus后`c25a`令s2=n，不使用helper返回计数。lower+48原word为0，ready+38=a001972c恒返1；fallback `add2` postincrement读byte到a1，`adda`传dev/byte。初始private首byte=1支持`a0019894`到62fc22ae的scalar分支。另型号分支传本函数栈局部地址及count1，不能扩为所有lower都已认证。 |
| path aliases/动态换表/final close/硬件完成已闭合 | 未核。D03已明确这些断边，本轮继续保留。相邻console和其他tty设备并非同一dev；同名字符串与初值不证明全ROM无别名、重注册、换表或private修改。 |

## 更正后的布局、伪代码和生命周期

分析类型名不是原源码。File stride=0x18：flags:u32@0、refs:i32@4、position@8、inode:ptr32@c、private@10、未解释word@14。Inode type_bits:u16@e、ops:ptr32@10、dev/private:ptr32@18。group来自word[word[62fc6c18]+8]；table=group+5c，page_count:u8@0、pages:ptr32@4，每页6个File。下例保留 helper 实际可选分支，替代 D03 `lookup_ref` 的对应伪代码；没有对这个非主路径作输入实验。

```c
File *lookup_ref(table, page, slot, uint8_t *mark) { // a00258a0
    saved = csr_clear_mstatus(8);
    f = load32(load32(table+4) + 4*page) + 24*slot;
    if (load32(f+0xc) != 0) {
        refs = load32(f+4);
        if (refs == 0) f = NULL;
        else store32(f+4, refs+1);
    } else if (mark == NULL) {
        f = NULL;
    } else {
        refs = load32(f+4);
        if (refs != 0) store32(f+4, refs+1); // 58d2 -> 58c0
        else { store32(f+4, 2); store_u8(mark, 1); }
    }
    csr_write_mstatus(saved);
    return f;
}
// a00258e4强制a3=0，实际acquire不进入上述mark非NULL分支。
```

主路径：open成功安装基础refs=1（`a01b5c08`），acquire在独立临界区取引用；通常1→2，dispatch同步调用write后release→1。这以基础引用仍在、无其他并发变化为前提，不是所有时刻计数断言。refs减为0时先恢复mstatus，再进入`a0027d9a`；其到`a0027ca4`的最后释放内部仍是断边。

设备相关布局：TX head:i16@50、tail:i16@52、capacity:i16@54、ring:ptr32@58、task-write锁对象@40、等待对象@18、lower:ptr32@a0、lower private:ptr32@a4。初始化映射沿用已复核启动复制 `ROM a00027d4→RAM62fc2cc0`，dev62fc36d0对应ROM a00031e4。核到ring=62fc78a8、capacity400、head/tail0，lower=a01bcb18，private=62fc36b4、其首byte1。仅是初值，非设备运行快照。

```c
// 仅正常任务分支；入口context门、失败清理均按上表原指令。
uart_write(file, src, n) {
    dev = load32(load32(file+0xc)+0x18);
    r = lock(dev+0x40); if (r < 0) return r;
    may_wait = ((load32(file) ^ 0x40) >> 6) & 1;
    lower_txint(dev, 0);
    left=n; end=src+n;
    while (left != 0) {
        b=load_u8(end-left); flags=load32(dev+0x10);
        if ((flags&1) && b==13 && (flags&8)) b=10;
        if ((flags&1) && b==10 && (flags&0x24)) {
            r=enqueue(dev,13,may_wait); if (r<0) goto finish;
        }
        r=enqueue(dev,b,may_wait); if (r<0) goto finish;
        left--;
    }
    r=n;
finish:
    if ((uint32_t)left < (uint32_t)n) r=n-left;
    if (load_i16(dev+0x50) != load_i16(dev+0x52)) {
        // 原码此处及txint前分别重读lower，不合并成固定缓存表。
        cb=load32(load32(dev+0xa0)+0x2c); if(cb) cb(dev);
        load32(load32(dev+0xa0)+0x34)(dev,1);
    }
    unlock(dev+0x40);
    return r;
}
```

enqueue接收scalar byte，没有源地址。可写分支先重新读head和ring，将byte写ring[sign16(head)]，再halfword写next到head。这个本地顺序不独立证明跨核内存模型或消费者硬件顺序。通知+2c只传dev，随后txint也只传dev/enable；保存的write结果在callee覆盖a0之后从s2恢复。direct helper的批量槽若动态安装，可以接收到src指针；**未安装该槽是本轮direct按值合同的条件**。正常任务ring复制结论同样只限所核安装和正常调用，不推广到任意设备ops。

D02连接仅为：进度器用fd槽、frame+cursor、剩余byte数调用wrapper，正返回推进cursor；本次r个源byte已在本次任务write中读取、内容已复制进设备ring，caller无需把这部分frame原地址借到DMA完成。r不统计可能插入的输出CR，部分返回仍可留源后缀等待下一write。ring里的设备副本可以在返回后继续存在/传输；file局部引用归还不等于ring发送结束，也不等于帧响应匹配成功。没有allocator/free证据把静态frame和ring说成堆对象。

## 独立证据、来源与实际静态验证

[verify_review.py](../../analysis/uart-write-review-d04-0041-20261023/verify_review.py)只读 `D:/Documents/PlatformIO/Projects/cuktech-ap01-firmware/roms/0041/ap01-1.0.2_0041.bin`，VA→file offset=VA−9ffff000。脚本独立按原半字前缀推进2/4B，普通RV32+C由Capstone解码，厂商字另按原字段匹配本地既有模型；没有运行D03验证脚本或使用其pass输出来形成结论。人工读寄存器流/控制流，脚本另核关键编码。最后才将782条独立读取的raw与D03窗口交集逐条比较，全部相同。

实际运行 `python -B reverse/analysis/uart-write-review-d04-0041-20261023/verify_review.py`通过：**15个合并窗口、782条指令、61项精确操作数、21条原编码边、4项独立S型写宽/寄存器/位移检查、17条厂商字**，以及9个初始化word、ring半字初值、private首byte和路径/CR/LF常量。窗口包含D03正式12核心和必要依赖，没有重复全帧或parser。新[review-evidence.json](../../analysis/uart-write-review-d04-0041-20261023/review-evidence.json)保留地址、偏移、原byte、解码、模型摘录、检查与限制；不伪造REA Evidence ID。

纠正边原byte `a00258d2:fdf7`，独立拆C.BNEZ的rs1=a5及有符号offset=-18，目标58c0；不是仅凭反编译确定。该处`58c0:8507`加1、`58c2:5cc1` word写refs。实际调用的`58f2:8146`把a3置0，因此更正不改变正常acquire的分支。

厂商原字以模型 `evidence/rea-0041-20261017/ghidra/Ghidra/Processors/RISCV/data/languages/ap01thead2.sinc` 为语义依据：`th.mula`行25是rd += rs1*rs2，`th.lrw`行6564是4B indexed load，`th.lrbu`行6410是1B unsigned indexed load，`th.srb`行6442是1B indexed store；`th.ext`行762为sign16，`th.extu`行3372取bit6，`th.lbuia`行6431读旧地址byte再更新base。17个原字均保留opcode/rd/rs1/rs2/funct3/high/shift；代表字节为`58ae:0bc5b744`、`58b4:0b15f620`、`c192:8b59f700`、`c30a:8bba6a18`、`add2:8bc51498`。模型一致性是本地已有语义来源，不是新增厂商ISA文档认证。

初始化器历史来源仅作定位/身份：主仓库 `reverse/analysis/factory-test-0041-20261023/retained-initializer.json`，已实际读其元数据确认地址a005a736，Evidence `ev_dc0e38b0f382799ea2a8e8ad7f21cefc5998b0767ecf38a58cfdebe8add167c3`，profile `bcefdee5092076e55636e077b45523e203f4b870ae7b7ab547945ed1b8162279`。操作表、必要open和安装切片由本轮原字独立核。没有在线查来源；原厂源码、版本/编译配置仍未知。疑似NuttX/通用RTOS的名称不能认证来源，本轮未排除文件层、UART适配、同步函数等厂商实现；同步对象内部保留合同而非声称已恢复其算法。

事实是原字、字段访问宽度/顺序、计数临界区、安装动作、间接实参、源byte复制和返回覆盖。File/Inode/锁/环形TX等名称及同名open到注册inode的正常关联是据此形成的解释/推断。保留未知：完整path和所有aliases；运行中换ops/private/批量槽的全部写者；final close内部归还/通知；同步函数调度保证；lower 62fc22ae和另一型号栈byte callee内部；ring消费者 `a001a70a`、DMA完成、tail推进、等待者唤醒和物理交付。本轮没有负搜索证明这些边不存在，也没有对其进行设备试验。

建议一个后继闭包：以 `a001a70a(dev)` 对head/tail/ring的正常启动片段→实际完成回调→tail推进/等待者通知为入口，回答设备副本何时可复用及谁唤醒write；保持D02与本轮引用/源复制合同，不扩成全UART/DMA驱动。D04纠正后的限定接受可供管理整合，未自行启动后继。
