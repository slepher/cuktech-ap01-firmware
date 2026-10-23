# D06：UART TX ring IRQ 与条件 DMA 消费/通知独立复核

2026-10-23；基线 `1c79f0d1a7725c2921d0caf02ab2cd7683f95554`；分支 `codex/re-0041-d06`。**一处型号分支发布次数纠正、补齐 DMA IRQ trampoline ABI 后，限定接受 D05。** 已知 ttyS1 的初始 type=1，属于原报告两次发布成立的分支，因此纠正不改变其 IRQ 主链及条件 DMA 归还合同。D05 原文未改。

使用 `reverse-engineer-anything` skill；直接只读主仓库原 ROM 独立取字节、分段解码并核机器字段，没有导入 D05 的证据 JSON/断言、打开共享 REA target 或共享可写数据库。D05 用作待复核命题和定位来源；D04 的 fd/source 同步复制、optional_mark 纠正和 D02 帧队列只作为前置合同。没有执行固件、连接设备/外部服务、运行历史回放/项目编译、异常/超时/漏洞实验；没有改 ROM、生产代码、构建配置或分析器模型。

## 业务答案和逐项裁定

设备 `62fc36d0` 的初始化关联是 lower=`a01bcb18`、private=`62fc36b4`，private+0 type=1、+1 IRQ=0x3d、+e=0。该初值使 `a001a70a` 直接返回，但不能证明运行中 +e 永远为零。首次 open 安装 UART IRQ 的真实 callback/arg；公共分发令 a2=dev，TX active 的 **mask 0x4（位号2）** 且 private+e=0 时调用 ring consumer。初始 lower+48=0，走 scalar 分支：先以 SH 发布新 tail，再从旧 tail 读无符号 byte，按值调用 lower；有进度后通知写者。软件槽归还并不证明字节已离开 UART 或被对端收到。

private+e 非零时，另有已定位的 DMA start/两段 state/完成 callback/release 路径；完成 callback 的软件计数不能替代硬件交付证据。释放函数的 pointer 门只控制 tail 更新，三计数清零和非零进度通知均在门外。通知固定先 poll，再处理 dev+18 的等待对象。

| D05 命题 | 裁定、独立原指令依据 |
| --- | --- |
| private 初值 +e=0、DMA available 早退 | 接受，限初值。ROM `a00031c8` 原28B以 `013d...` 开始，+e=0；`a001a720:83c7e900` LBU，`a724:63890716` BEQ 到 `a001a896` epilogue。未执行启动复制/程序。 |
| 首次 open→lower+8→UART IRQ 安装 | 接受。`a002bae0/e6/e8` 重读 lower、取+8、间接调用；`a001a1e8` a2=dev，`a1ea/f2` a1=`a0019ae0`，`a1ee` a0=u8(private+1)。installer 成功返回0才 enable IRQ；open 的 attach 返回非负才继续，失败有原lower+4清理分支。 |
| IRQ 表和公共分发的三参 ABI | 接受。`a00264cc:8bd52747` indexed word 写 callback 到 `62fc662c+8*irq`，`64d4` 写 arg+4；`a0001026` 读 arg到a2，日志调用前后栈保存/恢复a2，`1042/44/46` 以 a0=irq/a1=context/a2=arg 调callback。 |
| TX status/mask/private 门 | 接受。type≤1切片 `a0019b14..42` 读 status@20 与mask@24，active=status&~mask；mask4非零、+e为0才 `9b34→a002d36a`；回来重读寄存器基址，OR4写mask。+e非零也仍走mask写回。type>1的TX短分支 `9c4e..6a` 同样有+e门。其相邻RX未复核。 |
| scalar 先 tail 发布、再读旧槽、按值 send | 接受。`a002d3d4` LHU旧tail，`d3dc` sign16旧值供地址，`d3e6:2399f404` SH新tail，`d3ea:8bc5d580` indexed unsigned byte load到a1，`d3ee` jalr lower+30。send返回值未参与接受数计算。 |
| ready=1、bulk=0及循环/重读/回绕 | 接受，限所核表。+38=`a001972c`，`a0019734` a0=1后返回；+48原word为0。`d37a..9e`两次head/tail读取，ready为0到第二次比较；scalar/bulk之后 signed tail≥signed capacity才SH tail=0。bulk≤0跳wrap再循环，未改为退出。progress截u16。 |
| DMA start 实际安装 a0019d9a(dev) | 接受。`a001a3f2/f6/fa/fc` a0=channel handle、a1=`a0019d9a`、a2=dev，`a400→a00264ec`；`6500` indexed store callback、`6514` store arg。同一handle的group/channel被重读。 |
| DMA 公共 IRQ 安装和调用连接 | 补充中间ABI后接受。真正注册到IRQ表的是 RAM `62fc133c`，arg是8B pair；pair[0]=`a0024b12`、pair[1]=0。trampoline从a2取pair，令a1=pair[1]，以仍为IRQ的a0调用pair[0]，然后返0；`a0024b12`不用其入口参数，读pending并调用槽callback(arg)。不能把 `a0024b12` 写成直接安装到公共IRQ表的值。详见下节。 |
| 两段phase/remain决定结束、停止/clear后归还 | 接受。type≤1在second_len=0或phase非0或首次remain低12位=0时终结，否则clear→phase=1→重读remain，重读0继续终结，非0返回。type>1同一判断结构而使用独立state。不是按callback次数判断。 |
| 所有型号终结均两次 word 发布 dev+88 | **纠正**。type≤1是 `9e18`存first_len、`9e26`存总数；type>1的 `9ee2/9ee6`先读两长度，`9eea:2dbf`直接跳`9e24`，只经过`9e26`一次总数store，绕过`9e18`。不得以两次发布概括全函数。 |
| pointer门控tail、门外清三计数/通知 | 接受。`d5ea` mismatch到`d608`；匹配才重读tail、读signed capacity、ADD/REMU、SH tail；`d608/d60c/d610`按+88/+84/+80顺序word清零，原保存consumed非0才`d61e→a002be92`。不清p1/p2，也不写head。 |
| poll先于semaphore及写者重查 | 接受。`bea4→a002bcec(dev,0,4,4)` 后 `bea8` a0=dev+18、`beac→a002b8de`。waiter helper只在入口读signed16 count，此后递增局部值。`c1d4/c1e0/c1e4/c1f4/c1f6`为available→txint1→wait→txint0→恢复mstatus，返回非负再查tail，负返-4。 |
| 动态gate/ops写者、硬件完成、调度/poll全合同已闭合 | 未核，继续保留D05边界。初值、静态注册动作、软件tail与notify不是运行时固定配置或物理完成证明。 |

## 函数、结构和返回合同

12个正式核心及必要短切片均按D05范围核原指令：`a001a1d8` attach、`a0019ae0` TX相关IRQ切片、`a002d36a` drain、`a001a70a` available、`a001a240` start、`a0019d9a` completion、`a00264ec` callback installer、`a0024b12` DMA IRQ、`a002d5d8` release、`a002be92` notify、`a002bcec` poll wrapper、`a002b8de` waiter helper。没有将完整UART IRQ/RX、多型号硬件表、DMA算法、poll或调度核心称作全量恢复。

必要切片包括首次open、公共IRQ installer/dispatcher、ready/scalar send/txint、DMA configure/state/mask/submit wrapper、enqueue等待，以及本轮补核的RAM trampoline/其启动复制。attach返回installer原结果；UART IRQ及RAM trampoline明确返回0。drain/available/start/completion/release/notify的caller不使用接受字节数返回合同，不能把其中偶然保留的a0当发送数。DMA common IRQ只按已取pending扫描8槽，先写清pending再逐槽间接调用；未观察硬件触发。

分析布局（名字不是原源码）：

```c
Dev {
    /* +18 */ WaitObject tx_wait;
    /* +40 */ WriteLock task_write_lock;
    /* +50/+52/+54 */ int16_t head, tail, capacity;
    /* +58 */ uint8_t *ring;                 // 初值62fc78a8，cap=0x400
    /* +78/+7c */ uint8_t *first, *second;
    /* +80/+84/+88 */ uint32_t n1, n2, consumed;
    /* +a0/+a4 */ Lower *ops; Private *priv;
    /* +ac */ PollSlot slots[4];            // 每槽word指针，core持有合同未解
};
Private { /* +0 */ uint8_t type; /* +1 */ uint8_t irq; /* +e */ uint8_t tx_dma_gate; };
// type≤1: n1[typ]@62fc86d0, n2[typ]@62fc86d8, phase:u8[typ]@62fc86e0
// type>1: n1@62fc85f0, n2@62fc85f4, phase:u8@62fc85f8
// channel:u8[typ]@gp+3dc，消费前sign8；handle*[channel]@62fc603c。
```

head/tail为LHU后显式sign16；capacity是LH。`consumed/n1/n2`是word，phase/channel/private门是byte，release的余数是RV32 unsigned REMU，非signed `%`。初始 ring head/tail=0。D04已证源byte同步复制到ring并先写byte后SH发布head；这里只针对核该两条 `a002c192/196`，不重做文件页表/帧队列。

## 真实安装与 IRQ 的短闭包

```c
attach(dev) { // a001a1d8，参数和返回均按机器码
    p = L32(dev+0xa4);
    r = install_irq(U8(p+1), a0019ae0, dev);
    if (r == 0) enable_irq(U8(p+1));
    return r;
}
uart_irq(irq, context, dev) { // type≤1 TX切片；省略的RX不是伪造空操作
    p = L32(dev+0xa4);
    regs = L32(L32(p+0x10)+4);
    active = L32(regs+0x20) & ~L32(regs+0x24);
    if (active & 4) {
        if (U8(p+0xe)==0) drain(dev);
        regs = L32(L32(p+0x10)+4);          // 调用后重读
        S32(regs+0x24,L32(regs+0x24)|4);
    }
    /* 原函数随后仍有其他分支 */
    return 0;                              // 所核公共epilogue
}
```

DMA installer `a00264ec`先把 callback/arg按 `index=handle.channel+4*handle.group` 写 `62fc5c4c+8*index`，再清handle->regs+10的0x8000位；group非0返回。group0读取 `IRQ=U8(handle+8)+0x10`。若IRQ表当前callback已经是 `62fc133c`，复用原arg pair；否则分配8B pair。随后 `a002657a/7e/82`把 `a0024b12` word写pair+0，`6584:23220600`写pair+4=0；`6588/8c/8e`以 `(IRQ,62fc133c,pair)` 调 `a0026498`，成功才enable相应IRQ。

RAM代码的定位不是猜测：启动 `a0029cf6..a0029d0e`构造dest=`62fc1100`、source=`a0000c14`、end=`62fc2cc0`；`a0029e2c:0b464758`/`9e30:0bd64758` 按原模型是加载/存储word后各指针+4，`9e34`回到`9d0e`比较。因此 RAM `62fc133c` 对应 ROM `a0000e50`，文件offset=`0x1e50`。该静态复制关系连接的是将被安装的代码，不是观察到其已执行。

```c
irq_trampoline(irq,context,pair /* a2 */) { // RAM62fc133c..1353
    fn = L32(pair);                         // 1344:1c42
    a1 = L32(pair+4);                       // 1346:4c42
    fn(irq,a1,pair);                       // 1348:8297；a0仍是irq，a2仍是pair
    return 0;
}
dma_irq(/* 入口参数未使用 */) {            // a0024b12
    pending=L32(0x2000c004);
    S32(0x2000c008,pending);                 // 先清再扫描
    for (i=0;i<8;i++) if (pending & (1u<<i)) {
        fn=L32(0x62fc5c4c+8*i);
        arg=L32(0x62fc5c50+8*i);
        fn(arg);                           // a0=dev，一参ABI
    }
}
```

UART callback接收dev于a2；DMA最终业务callback接收dev于a0。中间trampoline将pair[1]传a1而非a0，common IRQ恰未使用入口实参，故不能省略此处ABI后又把所有callback画成统一签名。pair的最终释放、非group0的其他IRQ路径保留边界，不展开全IRQ框架。

## scalar 消费、回绕和通知

下列L16/L32/U8每次出现都表示原码对应重新读取；SX16表示显式符号扩展，伪代码是本轮解释而非原源码。

```c
drain(d) {                                 // a002d36a
    uint16_t progress=0;
again:
    if (SX16(L16(d+0x50)) != SX16(L16(d+0x52))) {
        if (!L32(L32(d+0xa0)+0x38)(d)) goto finish;
        ops=L32(d+0xa0); ring=L32(d+0x58); bulk=L32(ops+0x48);
        if (!bulk) {
            send=L32(ops+0x30); raw=L16(d+0x52); old=SX16(raw);
            progress++;
            S16(d+0x52,SX16(raw+1));         // SH先于旧槽byte读取
            b=U8(ring+old);
            send(d,b);                     // a0=d,a1=scalar；返回未计数
        } else {
            t=SX16(L16(d+0x52)); h=SX16(L16(d+0x50));
            n=(t<h) ? SX16(L16(d+0x50))-SX16(L16(d+0x52))
                    : I16(d+0x54)-SX16(L16(d+0x52));
            ptr=ring+SX16(L16(d+0x52));
            r=bulk(d,ptr,n); if (r<=0) goto wrap;
            raw=L16(d+0x52); accepted=(uint16_t)r;
            progress+=accepted; S16(d+0x52,SX16(raw+accepted));
        }
        progress=(uint16_t)progress;
wrap:
        if (SX16(L16(d+0x52)) >= I16(d+0x54)) S16(d+0x52,0);
        goto again;
    }
finish:
    if (SX16(L16(d+0x50)) == SX16(L16(d+0x52)))
        L32(L32(d+0xa0)+0x34)(d,0);         // 重读为空才关TX
    if (progress) notify(d);
}
```

当前安装bulk为NULL，ready恒1；这两个条件都来自表/函数静态初值，未穷尽运行时换表。scalar send `a0019876`对type≤1从private+10取regs，并以a1仍为byte调用 `62fc22ae`；另型号传的是本函数栈上scalar副本地址、count1，不能推广为任何lower都按完全相同ABI发送。该BootROM/外设发送深层实现仍未恢复。

## 条件 DMA 状态及 D05 替代段落

`a001a70a`在+e非0才触及channel。非法channel尝试分配、byte发布并重读；仍负转原断言边。合法且active时，先MMIO置0x40000→stop→clear→清0x40000→读取remain低12位。按旧phase选择 `n1-remain` 或 `n1+n2-remain`，byte清phase；非零进度word写dev+88再release。此后重读channel和head/tail，ring非空才构造一/两段设备描述符并调用重读的lower+20。

构造顺序维持D05：不绕回时清p2、清n2、写p1、写n1；绕回时写p1、n1、p2=ring、n2=head。head=0仍可发布p2=ring而n2=0。start `a001a240`复制20B模板到栈、组两个12B项 `{src,dst,count}`，检查channel和n1；清dev+88和pending，持久保存n1/n2、清phase，configure→txint0→安装callback→clear/mask→submit→enable。提交count按n2为0选1否则2，不由p2是否非空决定。

实际submit仍经 `a01a47dc`重排为 `a01b554e(regs,storage,4,stack_desc,number)`；persistent storage type≤1是 `62fc86e4+64*type`、type>1是`62fc85fc`。底层是否同步复制stack_desc、cache/descriptor格式未核；不能把这一层栈数组断边伪装成已经证明深拷贝。原frame已复制到设备ring的D04合同不因该断边变成DMA借用frame原地址。

**D05“正常完成与 tail 归还”中关于发布次数的段落应由以下文字替代：**

> 终结先stop(channel)→clear(channel)→byte清phase。type≤1先在a0019e18 word写dev+88=first_len，再重读second_len、相加并在a0019e26第二次word写dev+88，随后调用a002d5d8。type>1则在a0019ee2/9ee6先读first_len和second_len，a0019eea直接跳a0019e24相加，仅经过a0019e26一次总数word发布，再调用同一release。两分支的phase/remain正常结束判断相同，dev+88中间发布序列不同。初始ttyS1 type=1属于前者。

这是机器序列纠正，既没有修改厂商行为，也没有对中间发布的并发可见性作证明。

```c
complete(d) { // 概要，仅将两类state别名抽为 n1/n2/phase；各U8(type)原处仍重读
    if (L32(n2)!=0 && U8(phase)==0) {
        if ((L32(channel_count_reg)&0xfff)!=0) {
            clear(channel); S8(phase,1);
            if ((L32(channel_count_reg)&0xfff)!=0) return;
        }
    }
    stop(channel); clear(channel); S8(phase,0);
    if (type_branch_le1) {
        total=L32(n1); S32(d+0x88,total);    // 9e18
        second=L32(n2);
    } else {
        total=L32(n1); second=L32(n2);      // 9ee2/9ee6，无中间发布
    }
    total+=second; S32(d+0x88,total);        // 9e24/9e26共同段
    release(d);
}
release(d) {                                // a002d5d8
    old=SX16(L16(d+0x52)); consumed=L32(d+0x88);
    expected=L32(d+0x58)+old; first=L32(d+0x78);
    if (first==expected) {
        t=SX16(L16(d+0x52)); cap=I16(d+0x54);
        next=(uint32_t)(t+consumed) % (uint32_t)cap; // RV32 ADD/REMU
        S16(d+0x52,SX16(next));
    }
    S32(d+0x88,0); S32(d+0x84,0); S32(d+0x80,0);
    if (consumed!=0) notify(d);              // pointer不匹配亦可达
}
```

这些字段不能合并成单一busy bool：硬件enable bit、phase、设备段长度、持久数组长度各有不同用途。release不清持久n1/n2数组、不清p1/p2、不自动重启；它只在pointer匹配时归还tail、总是清设备三计数并按保存进度通知。

## 等待、所有权及可达结果

`notify(d)`原序为poll wrapper `(d,0,4,4)`→waiter helper `(d+18)`。poll wrapper mask8临界区内以a0=`d+(first+0x2b)*4`、a1=`last-first`、a2=event 调 `a002e2a0`，实际为四个slot、event4；必要调度helper前后重读其门，最后恢复旧mstatus。poll core是否保留slot/怎样匹配用户仍未解。

waiter helper入口LHU并sign16到局部count，count>0返回，否则重复 `a00273cc(waitobject)`并令局部count+1直到正值，**没有每轮重读对象count**。post内部排队/唤醒/调度完整保证未恢复；不由helper名推断等待write立即成功。

满环writer在mask8下重查tail，仍满才available→txint1→wait(dev+18)→txint0→恢复旧mstatus；非负wait回循环查tail，负wait返回-4，不可等待分支-11。head是producer发布，tail是consumer归还；通知不预留槽数。task write锁、fd引用临界区和consumer中断控制是不同机制，不推断跨核顺序/公平性。

frame源字节的生命周期以D04为准：write接受部分已同步复制进设备ring，局部file引用归还不意味着设备副本发送完成。scalar消费先发布tail再读取旧槽/传scalar；本轮不改变该顺序或给出硬件完成承诺。条件DMA引用的是设备ring和设备/全局state；callback/release软件归还不证明外设最后一个byte已经发完。ring/dev/frame均没有在本闭包中出现heap free，不创造分配/释放所有权；DMA callback pair分配存在，但其最终释放未核。

## 独立证据、实际验证、来源及断边

[review.py](../../analysis/uart-ring-review-d06-0041-20261023/review.py)从主仓库 `roms/0041/ap01-1.0.2_0041.bin`读取原ROM，XIP地址file offset=VA−9ffff000；RAM trampoline按本轮原指令证实的复制映射读取。[original-instructions.json](../../analysis/uart-ring-review-d06-0041-20261023/original-instructions.json)包含28窗口1349条指令的VA/文件offset/原byte/解码，初值、10个厂商语义原条款、107条标准JAL/branch边、8对相邻AUIPC/JALR、44条原S型store字段。所有记录重新取自原ROM，不是回放D05 JSON。

实际运行 `python -B reverse/analysis/uart-ring-review-d06-0041-20261023/review.py` 通过。线性边界按原halfword低位定2/4B，Capstone 5.0.7解RV32+C；独立抽取B/J/S字段核11条必要JAL目标、7条关键store宽度/寄存器/位移、gate目标、三对关键AUIPC/JALR目标；从C.J位域独立核`9eea→9e24`、`9e30→9e8a`及启动copy回边；核RAM trampoline三条间接ABI指令、ready=1与private/lower初值。随后人工按原分支检查上述裁定及伪代码的发布、重读、清理、返回和持有顺序。脚本不执行伪代码/固件、模拟DMA或测试异常数据。

厂商字使用主仓库只读 `evidence/rea-0041-20261017/ghidra/Ghidra/Processors/RISCV/data/languages/ap01thead2.sinc` 的确切条款：ext为signed位域、extu无符号截位、lrbu无符号indexed byte、lrw indexed word、srb/srw byte/word indexed store、addsl基址加移位索引、lwia/swia按旧地址读写后更新基址。条款连同来源行号在JSON留存；没有修改模型。此为本地既有厂商模型来源，不冒称本轮外部ISA/原厂SDK版本认证。普通库/RTOS相似性未认证版本，故没有以“标准库”为由静默排除适配或回调。

事实：原字节、写宽、符号扩展、分支目标、构造常量、参数寄存器、返回及重读顺序。推断：UART TX/ring/phase/归还/通知等分析命名由MMIO用途及计数指针支持，不是原源码符号。未知：全ROM动态private+e、ops/private/批量槽写者未穷尽；同名设备运行时关联仍受D04 pathname/alias边界限制；IRQ/hardware实际执行、优先级与线缆交付未观测；channel allocator/final close、DMA a01b554e深层描述符/缓存/stack_desc持有、完整poll core/调度内部和DMA pair最终释放未闭合。没有把这些有界未核解释成不存在，也不作缺陷结论。

恢复程度：所核初始type1的IRQ软件消费→tail→通知，以及+e非零的条件DMA注册→正常callback→软件release，均有可定位原指令连接；型号发布次数纠正后限定接受D05。一个建议后继闭包：只追 `a01a47dc→a01b554e` 的正常一/两段描述符输入如何写到持久storage，确认stack_desc借用/复制与提交返回时的所有权；保留cache/hardware触发边界，不扩DMA全框架。本轮不自行领取。
