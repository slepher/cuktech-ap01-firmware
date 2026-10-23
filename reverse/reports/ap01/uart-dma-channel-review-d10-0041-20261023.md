# D10：D09 UART TX 三槽与正常 close 的独立复核

2026-10-24；基线 `a825ac8`；分支 `codex/re-0041-d10`。使用 `reverse-engineer-anything` skill，只读原0041 ROM及留存证据，不打开共享REA target或数据库。没有SIM、构建、回放、设备、外网、固件执行、异常输入或漏洞验证；未修改生产代码、ROM、配置、模型或共享索引。

**限定接受D09的三槽busy及正常close连接，纠正一处读取次数/伪代码精度；新增功能为0。** 软件busy归还不能解释为DMA callback pair、固定LLI池或硬件的整体析构。

## 已有成果→实际复核缺口

|既有出处与证据层|已解释的行为|局限及本轮实际复核|
|---|---|---|
|[D09复用对照](uart-dma-channel-d09-0041-20261023.md)及其[reuse-check](../../analysis/uart-dma-channel-d09-0041-20261023/reuse-check.json)|旧21份材料和最终ZIP39成员的有界检索；SIM最终验收、factory map路径、旧pass3 dma0_ch3及本地服务的范围已区分|直接继承检索，不重新导出/解包/记账。文本无命中不等同从未分析；passed-in-sim不认证原UART ABI。|
|[D03](uart-write-object-d03-0041-20261023.md)、[D04](uart-write-review-d04-0041-20261023.md)；原字节及复核|File/inode/dev注册、初始ops与private、最后File引用归还|不重做注册或write；仅核close间接slot及初始对象仍是本题对象。|
|[D05](uart-ring-drain-d05-0041-20261023.md)、[D06](uart-ring-review-d06-0041-20261023.md)；原字节及复核|channel申请/发布、stop接口、type索引、IRQ callback及ring消费已有|直接引用；只检查D09接入stop/free的实际参数与重新读取顺序。|
|[D07](uart-dma-descriptor-d07-0041-20261023.md)、[D08](uart-dma-review-d08-0041-20261023.md)；原字节及独立复核|handle、固定LLI池、submit、MMIO、cache、completion和ring归还|不重导、不扩IRQ/ring/硬件。busy槽不是这些对象的free。|
|[D09原指令](../../analysis/uart-dma-channel-d09-0041-20261023/instructions.json)|三槽首空选择、busy发布/清除、最后close到lower shutdown以及0x0f写回|本轮仅独立校核上述增量的位域、ABI、分支、对象和原序；读取次数需明确。|

## 继承的旧结论

设备 `62fc36d0`、private `62fc36b4`、lower表 `a01bcb18`，File→inode+18→dev、启动复制及gp身份沿用D03/D04；TX byte表 `gp+3dc=62fc389c`、handle表和stop语义沿用D05–D08。DMA模式受private+e门控，初值为0，不能将条件DMA分支描述为设备启动后必走路径。D09新增allocator/close合同与旧SIM服务是不同证据范围。

## 本轮复核或纠正

[静态复核脚本](../../analysis/uart-dma-channel-review-d10-0041-20261023/review.py)及[结果](../../analysis/uart-dma-channel-review-d10-0041-20261023/review-results.json)直接读取主仓ROM，以D09留存行定位，独立解码普通指令、call/branch立即数与12个厂商指令字段，没有执行D09脚本或重复导出整函数。必要原字节重读均属**旧结论复核**。

|检查项|判定与限定|
|---|---|
|allocator与release的同步对象|接受。allocator wait=`gp-28`，lock/unlock=`gp-38`；release复用后者，非零busy清零后post前者。callee目标分别与D09一致；不认证同步原语内部并发或硬件保证。|
|三槽首空选择/占用|接受。`a0028924/2e/34`分别读`62fc6048[0/1/2]` U8；首零选0/1/2，再于`a0028946` byte写1。`a0028952`按sign8返回index。三槽均非零的assert边不扩展、不推测其是否返回。|
|release清busy与返回消费|接受。`a01b5c6e/74`使用相同busy基址，零值只解锁，非零先byte清0再post再解锁；无handle/pool/callback表写。lock失败保留其负a0，否则末次unlock的a0遗留；caller在free返回后不消费a0，而是重读type并写哨兵。不能补造明确success返回。|
|正常close与ops身份|接受。`a066d7cc=a002c678`，`a01bcb1c=a00198bc`；初始dev+a0/+a4再次核为上述lower/private。close读取File+c→inode+18；count>1仅减1并解锁，机器分支count≤1到shutdown，正常最后关闭以count=1为前提。|
|close顺序与门|接受。先lower+18(dev,0)，按flags bit6选择drain，再保存/清mstatus bit3、lower+c，dev+2为0才lower+4；`a002c700:73900930`为`csrw mstatus,s3`恢复原值。dev+3为0跳回解锁，optional lower+40不在静态普通设备分支中。未认证运行时换表或标志修改。|
|stop sign8 / free U8 / 0x0f|接受。`a0019926`是signed extract低8位，`a0019936`为ANDI ff，`a0019946` LI 0xf而非-1或0xff，随后indexed byte写。stop目标a0024bb6、free目标a01b5c48均独立核。|
|type/channel重读次数及伪代码|**精度纠正**，见下文。D09主体结论成立，但“三次type/channel重读”及展开式stop参数易误读；必须分开type与channel的实际读取，不插入不存在的load。|

在已进入DMA条件段后，`a0019900`读取type到a5，这个同一a5供两次channel门检查以及stop的channel加载使用；`a0019922`之前没有新的type load。此段type读共3次：`9900 → 992e → 9942`；channel读共4次：`9908 → 9916 → 9922 → 9932`，最后`9948`写channel。更早的型号分支`a00198ce`另有一次type读取，不应算入这三次。两个门分别消费各自的channel读取，不能用一次snapshot合并。

以下伪代码仅细化D09已恢复的原序，名称不是原源码；`L8`为无符号byte load，`SX8`为signed低8位转换：

```c
t0 = L8(private);                  // a0019900，沿用至stop参数
if (SX8(L8(tx_channel+t0)) > 2) goto out;
if (SX8(L8(tx_channel+t0)) < 0) goto out;
stop(SX8(L8(tx_channel+t0)));       // a0019922/26/2a
// stop之后才重读type。
t1 = L8(private);                  // a001992e
release_busy(L8(tx_channel+t1) & 0xff); // a0019932/36/3a/3e
// 不判断release_busy的返回值。
t2 = L8(private);                  // a0019942
S8(tx_channel+t2, 0x0f);           // a0019946/48
```

厂商indexed load/store按opcode、rd/rs1/rs2、shift=0和byte宽度核；signed extract按high=7/low=0核，语义继承D08已核只读条款，不修改模型。上述读取是静态指令事实，不假设调用中type/channel恒定；同一正常槽的解释保留D09条件，未开展异常或并发故障研究。

## 本轮真正新增

**新增业务恢复0；独立复核及上述一项伪代码精度纠正。** 原allocator、close、0x0f、ops身份均归D09或更早成果。`a002c700`额外4B只是核D09已陈述的mstatus恢复，不计新功能。没有新源码、资源、PNG、分类表、整函数或机械哈希清单。

实际执行 `python -X utf8 -B reverse/analysis/uart-dma-channel-review-d10-0041-20261023/review.py`，201项检查通过，覆盖46个普通指令锚点、12个厂商字段锚点、8个直接/长调用目标、12个普通/压缩分支门及必要ops/private常量。检查数包含同一锚点的字节、解码、字段，不等同201项新行为。没有运行固件或伪代码。

## 仍未闭合的精确边

- DMA callback表及IRQ pair最终注销/free继续继承D09断边；busy清0不是该释放证明。
- 固定pool跨设备全局排他、重配置、硬件排空/物理UART交付和payload cache属性仍未知；未扩RX或全部IRQ。
- 本复核不认证同步原语内部、type>1型号、运行中ops替换或动态dev清理链；正常路径以既有设备身份与各门条件为限。

本轮没有找到尚未核的真实正常caller/callee入口作为后继新种子；callback/IRQ pair最终析构只继承D09未知，不建议再派一轮相同负搜索。没有必要的独立增量，至此结束，由管理窗口决定换题。
