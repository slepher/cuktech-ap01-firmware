# D07：UART 条件 DMA 描述符持久存储、借用与归还

2026-10-23；基线 `e8ce444c5e7dcc388a1c197a4efc357aa3b3da51`；分支 `codex/re-0041-d07`。使用 `reverse-engineer-anything` skill，直接从主仓库原 ROM 重新读取指令；未切换共享 REA target 或使用共享可写数据库。本报告为恢复交付，尚待新 agent 独立技术复核。

## 业务结论和范围

条件 private+e 非零时，`a001a240 → a01a47dc → a01b554e` **同步消费栈上的一/两个 12B transfer，写入固定 RAM 池的 16B LLI**。保存的是 ring 源地址、外设目标地址、next 和 control，既不保存 transfer 栈数组地址，也不复制 ring payload。提交返回后栈 transfer 可以失效；ring 字节及 LLI 池仍被这次 DMA 使用。后续 `a0024b7e` 独立置 channel enable，正常 callback 先 stop/clear，再走既有 release 归还 ring tail；本闭包没有 heap 分配或 free LLI/ring。下一次 start 重写同一按 type 选择的池，并非从 callback 收回一个 heap descriptor。

`a01b554e` 完成 LLI 后，先把首项四个 word 依次写 channel MMIO，再调用 `a0025d9e(pool, used*16)` 作 cache clean。这个调用链只 clean descriptor 范围，没有调用针对 ring payload 的 clean，也没有做源/next 地址转换；不由此推断 ring 的 cache 属性、硬件一致性或物理交付。

原 UART 配置模板是 byte width、source increment、destination fixed。已知 ttyS1 ring cap=0x400，每段不超过 1024B，故每个 transfer 产生一个 LLI：不绕回用 1 项，绕回且 n2 非零用 2 项；池容量参数固定为 4 项（64B）。这只是该正常 UART 配置的静态推导，不能推广到其他调用者或动态换表。+e 初值为 0、IRQ 主链、D06 的 type≤1 两次/type>1 一次 dev+88 发布与 RAM trampoline/pair ABI 均保留既有合同，不把条件 DMA 描述成默认 TX。

本轮 10 个核心：start `a001a240`，wrapper `a01a47dc`，LLI builder `a01b554e`，configure `a0025cec`，cache clean `a0025d9e`，enable `a0024b7e`，stop `a0024bb6`，clear `a0024c20`，completion `a0019d9a`，release `a002d5d8`。active `a0024bec` 是相邻短合同。channel 分配器、IRQ 全框架、RX、其他 DMA 用户和全部 SDK 不在恢复范围。

## 参数、存储布局与实际所有者

下列名称为分析名，不是原源码：

```c
struct Transfer { uint32_t src, dst, nbytes; };  // 12B，start 的栈上
struct Lli { uint32_t src, dst, next, control; };// 16B，固定 RAM
// control: count[11:0], SWidth[19:18], SI bit26, DI bit27, I bit31
// Dev: ring+58, first+78, second+0x7c, n1+80, n2+84, consumed+0x88
// channel byte[U8(private+0)] @ gp+3dc；消费前明确 sign8
// handles[channel] @ 62fc603c；handle+4 是 channel_regs
```

| 资源 | 实际持有与生命周期 |
| --- | --- |
| frame/source | D04 已证明接受的字节同步复制到设备 ring；本轮不重新借用 frame 原地址。 |
| ring payload | `dev+58` 持有 ring；`dev+78/+7c`、栈 transfer.src、持久 LLI.src、channel 源寄存器逐层保存同一 ring 地址值。LLI 不拥有/释放 payload。 |
| 栈配置和 transfer | `a001a240` 的 `s0-4c` 是 20B 配置，`s0-38` 与 `s0-2c` 是两个 transfer；configure/builder 在返回前读完，没有把这些栈地址发布到持久字段或 MMIO。 |
| LLI pool | type≤1：`62fc86e4 + (type<<6)`，type>1：`62fc85fc`；start 将地址作为参数，builder 原址填充。不是本函数 malloc；本闭包也没有 free。type1 具体为 `62fc8724`。 |
| channel 选择 | private 的 type 索引 `gp+3dc` 的 byte，sign8 后检查 0..2；`62fc603c[channel]` 提供 handle 与 regs。选择值在提交/enable 前重新读取，不假装一次 snapshot。 |
| DMA 软件状态 | `62fc86d0/86d8 +4*type` 存两长度，`62fc86e0+type` 存 phase byte；type>1 使用 `62fc85f0/85f4/85f8`。这些与 pool、dev 的三计数不是同一 busy 标志。 |
| callback | 已有 `a00264ec(handle,a0019d9a,dev)` 将 callback 与 dev 存全局槽；callback 没有接收 stack transfer 或 pool 指针，靠 dev、type、channel、持久长度/phase 找回状态。 |

`a01a47dc(channel,pool,stack_transfer,count)` 先用厂商 indexed word load 取 `62fc603c[channel]`，然后重排为 `a01b554e(handle->regs,pool,4,stack_transfer,count)`。`a01a480c/0e` 分别将 count 移 a4、transfer 移 a3，`4810` 读 regs 到 a0，`4812` a2=4，`4814` JAL 实际目标为 a01b554e。没有将 stack transfer 指针写入 handle。

## 原字节定位及发布顺序

证据 [instructions.json](../../analysis/uart-dma-descriptor-d07-0041-20261023/instructions.json) 的每条记录含 VA、file offset、原 bytes、指令；VA→文件 offset 使用 `VA-0x9ffff000`。以下 bytes 是内存小端排列。

| 位置与原字节 | 含义 |
| --- | --- |
| `a01b5578: 0b3e2e4d` | 厂商 extu 提取 channel control 的 [19:18] 到 t3，作为 source width。 |
| `a01b558e: 0bc9c7a3` | 厂商 lrhu：从 `a066d580 + 2*width` 无符号 halfword 读 address step；表三项 4064/8128/16256，不是 word 表。 |
| `a01b55e2: 03aa0600`、`55ea: 83aa4600` | word 读 transfer.src/dst；`55be/56a6/56b2` 各 width 分支 word 读 nbytes。 |
| `a01b560c: 23204501`、`5610: 23225501`、`5614: 23240500` | 顺序 word 写 LLI.src、dst、next=0。 |
| `a01b563c: 232ca5fe`、`5640: 23260501` | 后继项填充时写前项 next=当前项地址；随后写当前 control。 |
| `a01b5650: 23acdeff` | 若非首 transfer，写前一 transfer 最后 LLI 的 next，连接两个段。 |
| `a01b5656: 63695602` | 完成本段填充/连接、累加 used 后，才以无符号比较 used>capacity 跳 a01b5688 原 epilogue。没有改成填充前检查。 |
| `a01b5666/566c/5672/567c` | 四次 SW 依次发布 pool[0] 的 src/dst/next/control 到 regs+0/+4/+8/+c。 |
| `a01b5680: 9700e7ff`、`5684: e780e071` | AUIPC/JALR 原字段算出 a0025d9e，参数 a0=pool，a1=used<<4；在上述 MMIO 四写之后。 |
| `a0025dc4: 0b809702` | cache 地址操作，rs1=a5、rd=x0、funct3=0、imm=0x29；下节说明本地编码来源。 |
| `a001a454/458` 后 `a45c: 83c70400` | submit 返回后立即重读 type，没有测试 a0 返回；再重读 channel 并在 a468 调 enable。 |

LLI 构造只保存地址值。`src += step` 由 control bit26 控制，`dst += step` 由 bit27 控制；没有逐 byte payload load/store，也没有修改地址到另一总线别名。末项 count 写低12位、I=1；内部项 count=4064、I=0。每个 transfer 的最后项均设置 I，因此双段中第一个段末也有完成通知位，和已验收 phase/remain 处理相接；不推断硬件一定产生了几次 callback。

## 伪代码与原返回行为

伪代码不是可编译参考实现。所有 L/S 是原宽度访问，保存原重读及发布次序；这里只展开 UART 能到达的 source width=0。一般 width1/2 的 alignment 返回边下文单列。

```c
start(d) {                                     // a001a240
    cfg = copy20(a01bb000);                     // 原 memcpy，调用合同未认证
    tr[0] = {L32(d+0x78), 0, L32(d+0x80)};
    tr[1] = {L32(d+0x7c), 0, L32(d+0x84)};
    // sign8(channel[type]) 不在 0..2 或 tr[0].nbytes==0 则返回。
    // type0: dst=2000a088；type1: cfg+8=3,dst=2000a188。
    // type2: 保留原相对 ops+28/+24 调用取配置和两次 dst；不是任意推常量。
    S32(d+0x88,0); clear(channel_reloaded);
    save_lengths_and_zero_phase(d);             // D06 原 type 分支、宽度与次序
    // type≤1 另先置 UART regs+80 bit0
    configure(handles[channel_reloaded], &cfg);
    txint(d,0);
    install_callback(handles[channel_reloaded], a0019d9a, d);
    clear(channel_reloaded); mask(channel_reloaded);
    count = L32(d+0x84)==0 ? 1 : 2;
    submit(channel_reloaded,pool_for_reloaded_type,tr,count);
    // 原代码不判断 submit 的 a0，也不做失败时 stop/free/计数回滚。
    enable(channel_reloaded);
}

build_uart_lli(regs,pool,capacity,transfer,count) { // a01b554e，width0
    width = EXTU(L32(regs+0xc),19,18);          // UART 配置使 width==0
    step = U16(a066d580+2*width);               // 此路径=4064
    used=0; i=0;
    do {
        len=L32(transfer+8);
        q=len/4064; n=q+1; last=len%4064;       // DIVU/REMU
        if (n!=1 && last<=30) { last+=4064; n=q; }
        first=pool+16*used;
        src=L32(transfer); ctrl=L32(regs+0xc); dst=L32(transfer+4);
        ctrl=(ctrl & 0x7ffff000)|4064;
        final=(last|0x80000000)&0x80000fff;
        p=first; j=0;
        do {
            S32(p,src); S32(p+4,dst); S32(p+8,0);
            if (ctrl & (1u<<26)) src+=step;
            if (ctrl & (1u<<27)) dst+=step;
            if (j==n-1) ctrl=(ctrl & 0x7ffff000)|final;
            if (j!=0) S32(p-8,p);
            S32(p+12,ctrl);
            ++j; p+=16;
        } while (j!=n);
        if (i!=0) S32(first-8,first);
        used+=j;
        if ((uint32_t)used>(uint32_t)capacity) goto original_epilogue;
        ++i; transfer+=12;
    } while (i!=count);
    S32(regs+0,L32(pool)); S32(regs+4,L32(pool+4));
    S32(regs+8,L32(pool+8)); S32(regs+12,L32(pool+12));
    cache_clean(pool,used*16);
original_epilogue:
    // 只恢复被保存寄存器与栈，未把 used 或负 errno 放入 a0。
    return /* 原 a0 residue，UART caller 不使用 */;
}
```

特别保留源码差异：本 ROM `a01b5688..56a4` 只恢复 ra/s0..s11/sp 并返回。成功时 cache helper 令 a0=pool+used*16；width1 的 nbytes&1 非零、width2 的 nbytes&3 非零时，分别从 `a01b56ac/56b8` 到同一 epilogue，a0 保留那个非零余数；capacity 门也直接到同 epilogue，a0 保留当前项填充后的地址。原函数没有显式返回 -1、-ENOMEM 或 used_count。不能为它补上 SDK 中的这些返回语义，不能把 caller 忽略返回说成已处理失败。这里仅静态保留原路径，不生成异常输入、不验证缺陷。width3 不属于原 UART 配置，其 default 保留路径未作为通用 DMA 支持恢复。

## 配置、cache 和正常归还的连接

配置模板 `a01bb000` 原20B为 `01000000 00000000 01000000 01000000 00000000`。configure `a0025cec` 先置 DMA global+30 bit0、清 channel+10 enable；control 保留 mask `0x03824000` 后按 cfg+12/+13 安装 SI/DI，按 cfg+16/+17 安装 source/destination width，再写 control。模板 cfg+12=1/+13=0，+16/+17=0，故源递增、目标固定、宽度0。随后 channel+10 配置请求/方向并 OR0xc000、control清 I 位、依次清 TC/error pending。没有把早先 cfg 指针存到寄存器长期持有。

cache helper `a0025d9e` 原序：a1+=a0&31；a0&=~31；fence；a0+=a1；每轮 a5=a0-a1，signed a1>0 才做 imm0x29 操作，a1-=32 回环；结束 fence。因此首地址向下32B对齐，处理覆盖 pool 的 cache line；原 a0 最终为未对齐 pool+原长度。没有采用 SDK API 文档的返回值。该实现没有本地 SDK `bflb_l1c.c` 现代 wrapper 的 cache-address check 和8行展开；只有单行循环。

具体编码根据本地候选 `drivers/lhal/include/arch/risc-v/t-head/Core/Include/csi_rv32_gcc.h:1368` 附近 `__CUSTOM_DCACHE_CPA` 的 `.insn i 0x0b,0,x0,%0,0x29` 核对：与 ROM `0x0297800b` 的字段完全一致，地址寄存器为 a5。由此将操作命名为该候选的 `DCACHE_CPA`/clean；这是编码与候选函数语义的证据，不是芯片运行时 cache 效果证明。既有 `ap01thead2.sinc` 未提供此条 cache pseudo-op，本轮未修改分析模型。

enable `a0024b7e` 经重读 handle->regs，对 regs+10 OR1；stop `a0024bb6` 清该 bit；active `a0024bec` 只返回该 bit；clear `a0024c20` 按 handle+a channel 字节构造 1<<channel 写 2000c008。没有 pool busy 标志或引用计数。

正常归还针对核原 callback/release：second_len=0、phase非0或remain低12位=0时终结；否则 clear→phase=1→重读 remain，重读非0提前返回。终结先 stop→clear→phase=0；type≤1依次 word 写 dev+88=first_len、dev+88=first_len+second_len，type>1只在共同段写一次总数，随后 a002d5d8。release 只在 first==ring+sign16(tail) 时以 REMU 计算并 SH 发布 tail；无论匹配与否，按 dev+88/+84/+80 顺序清零，保存的 consumed 非0则通知。p1/p2、pool 内容、持久 n1/n2 不被清空；通知顺序保持 D06 的 poll→waiter 合同。这里的“归还”是软件环槽可再用，并非释放 heap/descriptor，也非证明 UART 物理发送完成。

`a00264ec` 的全局 callback/arg 槽、IRQ `62fc133c` trampoline→pair→`a0024b12`→callback(dev) 沿用 D06 已核 ABI，不重复整个 IRQ 安装。pool 本身不会被传给 callback；终结不从 pool 推导 consumed，依赖预先保存的两长度/phase。phase=1 中途返回不归还 ring；最终 release 通知后可进入下一次 available/start 构造。不存在本报告证明的 descriptor free；close 后 channel 归还、callback pair 最终回收仍是断边。

## 本地来源认证界限

只读核实 `D:/Documents/PlatformIO/Projects/bouffalo_sdk`：`VERSION` 为 `PROJECT_SDK_VERSION "2.3.36"`，Git HEAD=`41bf338a57be53919d99f6c6715a96100428c97d`；`git status --short --untracked-files=no` 无输出。初次 sandbox 下 git -C 被拒，随后按已有明确根只读授权用 require_escalated 成功查询，未改 ACL、文件或下载。HEAD/packed-refs 也可直接读取。此信息认证候选树身份，**不认证其为 ROM 原始源码**。

ROM 既有交接中 AP01_BL618/chip/bl616 字符串及 2000c000 DMA 映射与候选 BL616 家族相容，但候选支持多个芯片。DMA callback 槽规模/包装、版本与板级配置不能靠名字和 base 相同判定。SDK 中 BL616 分支声明4槽而其 ISR循环仍为8，ROM自身8槽扫描合同以D06原字节为准，不据此替原程序修正。

| ROM 与候选路径/函数 | 匹配及必须保留的差异 |
| --- | --- |
| a01b554e ↔ `drivers/lhal/src/bflb_dma.c:243` bflb_dma_channel_lli_reload，内联 `:188` bflb_dma_lli_config | 4064分块、尾项小于31合并、16B池/12B输入、SI/DI、两段next连接、先写MMIO再clean高度同形；ROM对调用ABI已改为regs基址而非device，未返回候选used_count/-1/-ENOMEM。只作可识别算法来源候选，不能排除恢复。 |
| a0025cec ↔ 同文件 bflb_dma_init | control/config 的字段拼接与清pending相容；ROM硬编码2000c000，handle+4读取与板级包装仍需保留，未认证整函数无修改。 |
| a0024b7e/a0024bb6/a0024bec/a0024c20 ↔ 同文件 start/stop/isbusy/tcint_clear | 单bit操作同形；ROM上层用channel编号→handle并带断言，不是候选device* API原样实现。 |
| a0025d9e ↔ `core_rv32.h:1293` csi_dcache_clean_range 与 `csi_rv32_gcc.h` CPA编码 | 32B对齐/fence/逐行clean匹配；候选有8行展开、现代l1c wrapper有cache地址门，ROM实际没有这些门，且直接返回寄存器余值。 |
| a001a240、a01a47dc、a0019d9a、a002d5d8 | NuttX/厂商 UART wrapper、持久类型状态、release；不因底层算法相似排除，实际行为以本报告/D06恢复为准。 |

未把完整 SDK、标准 memcpy、IRQ适配或 RTOS 归类为“已认证未修改标准实现”。没有需要从恢复范围静默排除的函数。

## 实际静态验证、事实与断边

运行 `python -B reverse/analysis/uart-dma-descriptor-d07-0041-20261023/collect.py`，从原 ROM 新取8窗口648条指令和8个厂商模型条款；保存八组原指令与 S-type store 字段。Capstone RV32+C 解标准指令，厂商 ext/extu/lrbu/lrw/lrhu/srb/srw 使用既有只读模型确切条款，JSON保留其来源行号/内容。单独按机器字段核 submit/cache 两对 AUIPC/JALR、LLI/MMIO 八次 word store 的寄存器/位移、cache imm与32B原序、模板/三项halfword表，以及四条B与两条CB的原返回/循环目标。人工顺着原发布、重读、清理和返回序复核报告；未执行伪代码、固件、设备、构建、历史回放、网络或异常输入测试。`git diff --check` 完成后随提交记录报告。

事实是字节、布局、具体传参、word/byte写、bit域、同步填充、没有发布栈transfer地址、cache及enable顺序、无调用方返回判断。推断是 UART/LLI/借用/归还等命名及在初始ring容量/配置下每段一项。未知是运行时+e/ops/type/channel的全体写者、硬件是否触发及结束、cache属性与实际可见性；所有静态结论均不等同运行观察。

原问题的栈描述符寿命断边已闭合：它被同步转换为固定持久 LLI，源buffer地址持续借用，callback靠持久软件state归还软件ring。保留精确断边：

- `a001a8ee→a00288de` channel 分配/最终归还、close 路径和全局槽是否被其他设备重用尚未展开；不能宣称全生命周期互斥已证明。
- ring/cacheable范围属性、payload cache策略、总线地址含义与硬件交付未证；只证明此 submit链没有payload clean/地址转换调用。
- type2 的 a066e000 相对ops+28/+24配置/目标查询只保留既有短ABI，其他chip宽度/通道未纳入UART小闭包。
- callback pair最终释放和原IRQ/public通知内部仍沿D06断边；pool为固定地址而非heap不解决整个设备close。

只建议一个后继：新 agent 独立复核本 D07 的 stack→LLI→MMIO→cache→enable→callback/release 完整小闭包，重点核 ROM 与 SDK 返回差异、halfword宽度表、每段末 I 位与双段 phase/remain、源buffer借用及cache范围。未自行启动后继。
