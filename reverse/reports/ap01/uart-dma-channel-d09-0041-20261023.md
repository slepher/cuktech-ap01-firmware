# D09：UART TX channel 分配到正常 close 的增量恢复

2026-10-23；基线 `fca1d5e`；分支 `codex/re-0041-d09`。使用 `reverse-engineer-anything` skill，直接只读原0041 ROM和留存材料，不打开共享REA target/数据库。只写本任务独占目录；没有SIM、构建、历史回放、设备、外网、异常输入或漏洞验证，没有修改ROM、生产代码、配置或分析器模型。以下命名与伪代码是分析解释，不是原源码。

**本轮补上正常 UART close 到 TX channel busy 槽归还的连接；没有补出 DMA callback/IRQ pair 的最终析构。** 原 allocator只取得三个逻辑槽中的一个，不分配LLI或handle。最后一个UART open关闭时，lower shutdown先stop TX channel，再归还busy槽，再把本UART的channel byte写成`0x0f`。此顺序及对象身份是新增；既有descriptor、IRQ、ring release合同继承，不重复计数。结论待独立技术复核。

## 已有成果→实际缺口

[有界复用检索](../../analysis/uart-dma-channel-d09-0041-20261023/reuse-check.json)及[脚本](../../analysis/uart-dma-channel-d09-0041-20261023/reuse_check.py)记录文件/成员和命中行，只保存检索结果，没有复制旧源码或旧反编译。先检查21份旧材料及最终ZIP的39成员，再按新发现close/release地址复检。地址未命中仅表示这组文本未命中，不能说明此前没有分析。

|既有出处/证据层|已经解释的行为|局限、本轮实际补什么|
|---|---|---|
|`application-rehost-complete-0041-20261017.md`、`application-function-matrix-0041.json`；SIM验收|GUI/service contracts在SIM通过，父级最终验收优先于旧pending/remaining|不是原UART/DMA ABI或驱动完成证明，不重做SIM。|
|`factory-reference-map-0041-20261020.md` 第27/68行；路径线索|`PogoPinMng/UartComm.c`依赖与服务线索|覆盖未认证；不能代替channel原指令。|
|`charge-complete-0041.json`、`system-complete-0041.json`，以及weather/guide complete、page-logic/evidence、round4、knob/settings旧记录|应用页面、设备数值及本地替代服务等既有恢复|检索channel/handle/callback表地址及DMA别名未定位本题allocator/close合同；服务替代不能证明原ROM生命周期。旧remaining不直接沿用。|
|`0041-ghidra-pass3.txt:1148`；旧反编译|另一用户`dma0_ch3` lookup与callback安装|不是本UART的TX callback，不把其当新增或本对象析构。|
|`ap01-ui-0041-complete-source.zip`；39成员只读|SIM本地服务和应用重建；两个工具成员含UartComm字符串|不是原channel allocator；不执行脚本、不解包、不复制。|
|[D03](uart-write-object-d03-0041-20261023.md)、[D04](uart-write-review-d04-0041-20261023.md)；原字节及独立复核|正常`/dev/ttyS1`注册、fd/inode/dev身份、inode ops、File最后引用到`a0027ca4`；D03已记录`a066d7c8.close=a002c678`|继承对象身份、引用归还及ops安装；只补close间接调用到lower shutdown及channel释放。不重新恢复path/aliases或write。|
|[D05](uart-ring-drain-d05-0041-20261023.md)、[D06](uart-ring-review-d06-0041-20261023.md)|`a001a8ee→a00288de`调用和channel byte发布早已有；TX start、callback、stop、ring tail、IRQ pair ABI/安装已解释|本轮不是首次发现分配调用；只展开三槽选择及正常close连接。IRQ pair最终free仍独立未知。|
|[D07](uart-dma-descriptor-d07-0041-20261023.md)、[D08](uart-dma-review-d08-0041-20261023.md)|固定LLI池、transfer借用、MMIO/cache/enable、completion/release原序已恢复并复核|全部直接引用，不重导。D08明确留下channel分配/close与跨对象复用边；本轮只补软件busy槽复用，硬件与全局排他仍不外推。|

## 继承的旧结论

D03/D04给出正常注册设备`62fc36d0`，private=`62fc36b4`，lower表=`a01bcb18`；启动复制身份为ROM `a00027d4→RAM 62fc2cc0`。File→inode+18→dev以及inode ops安装直接继承。D05–D08给出TX channel byte表`gp+3dc`（继承gp=`62fc34c0`，故`62fc389c`）、type索引、消费前SX8与0..2门、handle表`62fc603c[channel]`和固定pool身份。

D06已有callback表`62fc5c4c+8*(handle.channel+4*handle.group)`及IRQ pair安装/复用；下一次start会再次安装callback/arg。D07/D08已证明固定LLI pool不是堆对象，completion归还的是ring tail，不是heap descriptor。它们不因本轮busy清零而变成析构证据。

## 本轮复核或纠正

仅重新读取两个必要旧ops word：`a066d7cc=a002c678`、`a01bcb1c=a00198bc`，标记为**旧结论复核**，不是新增发现close名称。D03初始dev四个byte在ROM `a00031e4`为`00000000`，故初始console门dev+2为0、动态清理门dev+3为0；不把初值当运行状态观测。未发现需要纠正既有D03–D08合同的技术结论。

厂商`th.lrbu/th.srb/th.ext`仅按现存只读模型相应三条条款核本窗口的indexed byte、byte写及sign8，不信不受支持的custom0伪变量，不改模型。脚本直接取原字节并验证实际JAL/AUIPC-JALR及B/C.B目标。一次验证中人工目标把`c74a`误写为`c6ae`，由位域解码纠正为`c6b0`；最终结果均通过，原成果未改。

## 本轮真正新增

[指令证据](../../analysis/uart-dma-channel-d09-0041-20261023/instructions.json)仅7个必要窗口576B/196条指令；[静态验证脚本](../../analysis/uart-dma-channel-d09-0041-20261023/verify_static.py)有38项控制流/字段检查及3条厂商条款。VA→file offset=`VA−9ffff000`，原ROM从主仓库只读，未生成哈希账或整函数重复导出。

### 三槽分配与归还

`a00288de..a002897b`的正常allocator流程：先等待`gp-28`，helper `a00288b8`对底层`-4`作原循环；等待成功再锁`gp-38`。wait/lock/post/unlock是同步用途分析名，原callee分别为a002786c（经retry wrapper）、a0027968、a00273cc、a00274b2；post边界继承D05/D06。两同步原语内部调度及并发保证不在本题，不擅自把局部调用解释成跨核互斥证明。

`a0028920..893c`按顺序读`62fc6048[0]`、`[1]`、`[2]`的U8。首个0对应index=0/1/2；`a0028944/46`用byte写1，随后`a002894a/4e`解锁，`a0028952`将index sign8到a0返回。无heap分配，也不修改`handles[channel]`。等待/锁失败的原分支归一为-1；三槽均非0的assert边仅定位，不对异常输入运行或展开其处理。

`a01b5c48..5c9b(channel)`使用同一个`gp-38`锁，锁成功后读`62fc6048[channel]`的U8；非0才依次byte清0（`a01b5c74:0b50f900`）→post `gp-28`（`a01b5c78..80`）→解锁（`a01b5c84..8c`）。若本来0，只解锁，不重复post；锁失败直接返回。返回a0是所走callee遗留，UART caller没有检查，不能补造明确success返回合同。这里不写handle表、callback表，不free pool/IRQ pair。

### 正常close接到同一个TX槽

File refs归零到`a0027d9a→a0027ca4`沿用D03/D04。新增只核`a0027d16..24`从保存的inode+10取ops，再取ops+4并调用，故原表目标为`a002c678(File*)`。

`a002c68e/92`从File+0xc的inode+0x18取得同一个dev。锁dev+30后读open count byte：大于1仅减1、解锁，不shutdown；最后一个open分支清dev+0，依次调用lower+18(dev,0)，按File flags bit6决定是否进入既有drain helper，然后清mstatus bit3，调用lower+c(dev)，并在dev+2为0时调用lower+4(dev)。**lower+4的实际初始slot就是`a00198bc`**。随后恢复原mstatus并走既有通知/解锁。dev+3为0的正常静态设备跳回`a002c6b0`解锁，不进入动态清理及optional lower+40；完整等待者/同步对象销毁不是本题。

在`a00198bc`的type≤1分支，先按原序处理UART MMIO mask，随后`a00198fa`读private+e，0则跳过TX DMA释放；非0才读`gp+3dc[type]`并两次SX8，检查0..2。合法时：

```c
// 以下每次L8都保留原重读；分析伪代码，不是原源码。
stop(SX8(L8(tx_channel + L8(private))));    // a0019922..2a → a0024bb6，D07/D08旧合同
release_busy(U8(L8(tx_channel + L8(private)))); // a001992e..3e → a01b5c48；不检返回
S8(tx_channel + L8(private), 0x0f);        // a0019942..48；不是0xff
```

不能把channel一次snapshot替代三次type/channel重读。`stop`的实参sign8，而释放实参以`ANDI ff`保留U8；后者用到的channel在前门内且正常无改写时为0..2。原caller即使release返回也不判断a0，继续发布0x0f。后续TX available继承D05的0..2门，所以0x0f会重新进入已知allocator；不需要把0x0f说成负数哨兵。

|状态/对象|本轮回答|不能混同|
|---|---|---|
|`62fc6048[0..2]` U8 busy|allocator首空置1；release非0清0并post|不是DMA enable、phase或callback有效位|
|`gp+3dc[type]` U8 channel|allocator结果发布；shutdown最终写0x0f|不是callback表index本身，也不是pool指针|
|`handles[channel]`与regs|旧start/stop按index使用；本allocator/release不重建handle|不能称新分配handle或整个DMA设备销毁|
|固定LLI池及callback/IRQ pair|继承原持有与安装；本次直接release不释放这些对象|busy槽可归还不代表所有关联资源已清空|

新增恢复限定为allocator/release的三槽软件合同及File close→lower TX shutdown→busy归还→channel哨兵连接，不另计重读旧stop、ops word或SIM服务为新增业务。

## 仍未闭合的精确边

- DMA callback表项`62fc5c4c+8*index`与IRQ pair的最终注销/free仍未定位；本题直接TX shutdown/release链没有这些写/调用。不能由局部未见外推全ROM没有释放，也不能把UART lower+c的设备IRQ解绑视为DMA IRQ pair释放。
- 软件busy槽允许后续allocator重选同一index；fixed pool的跨设备全局互斥、重配置、IRQ排空/硬件静止和payload cache属性没有运行证据或全局写者证明。静态close顺序不证明硬件交付或全并发安全。
- type>1另一UART型号、RX channel、dev动态标志改变/ops换表、所有名字aliases、同步原语内部不扩扫。private+e为0的初始IRQ主路径继承D06，不因条件DMA合同被替换。

建议仅一个后继：独立复核本轮7窗口的allocator/free同步对象身份、最后open门及三次channel重读/0x0f原序；callback pair最终释放继续作为独立精确断边，不为本题凑闭包扩全IRQ。
